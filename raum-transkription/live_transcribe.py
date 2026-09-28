#!/usr/bin/env python3
"""Live-Transkription für Raumaufnahmen (Meeting Owl o. ä.) mit faster-whisper.

Gegen den Degenerations-Loop wirken drei Dinge gleichzeitig:

1. Segmentierung an Sprechpausen statt festem Zeitfenster. Whisper bekommt nur
   Abschnitte, die tatsächlich Sprache enthalten - keine Stille, in der die
   Owl-AGC den Raumnoise hochzieht.
2. `condition_on_previous_text=False`. Der wirksamste Einzelschalter: ohne
   Kontextübergabe kann sich ein Loop nicht über Segmentgrenzen fortpflanzen.
3. Loop-Guard nach der Erkennung (loop_guard.py). Was trotzdem kollabiert, wird
   als "[unverständlich]" ausgegeben und im Debug-Log festgehalten - sichtbarer
   Fehler statt plausibel falschem Protokoll.

Setup:
    pip install faster-whisper sounddevice numpy

Aufruf:
    python live_transcribe.py --list-devices
    python live_transcribe.py --device 3 --model large-v3 --out sitzung.txt

Parameter sind gegen faster-whisper (transcribe(), VadOptions) geprüft.
"""

from __future__ import annotations

import argparse
import datetime as dt
import queue
import sys
import threading
from collections import deque

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

from loop_guard import analyse, collapse

SAMPLE_RATE = 16_000
FRAME_MS = 30
FRAME = SAMPLE_RATE * FRAME_MS // 1000     # 480 Samples
PREROLL_FRAMES = 10                        # 300 ms vor Sprechbeginn mitnehmen


def transcribe_options(language: str, aggressive: bool) -> dict:
    """Anti-Loop-Einstellungen für faster-whisper."""
    return dict(
        language=language,                 # nie Autodetect: auf Gemurmel unzuverlässig
        beam_size=5,
        condition_on_previous_text=False,  # kein Loop über Segmentgrenzen
        temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],   # Fallback-Kette
        compression_ratio_threshold=2.4,   # verwirft repetitive Dekodierungen
        log_prob_threshold=-1.0,
        no_speech_threshold=0.6,
        repetition_penalty=1.1,
        # 0 = aus. 3 blockt jedes wiederholte Trigramm - wirksam, verstümmelt
        # aber echte Wiederholungen. Nur zuschalten, wenn Loops bleiben.
        no_repeat_ngram_size=3 if aggressive else 0,
        hallucination_silence_threshold=2.0,
        vad_filter=True,                   # zweite Stufe: Silero im Modell
        vad_parameters={"min_silence_duration_ms": 500, "speech_pad_ms": 200},
        word_timestamps=False,
    )


class Segmenter:
    """Energie-VAD mit adaptivem Grundrauschpegel und Hysterese.

    Adaptiv, weil Konferenzmikrofone (Owl) eine eigene AGC fahren: ein fester
    Schwellwert ist nach zwei Minuten falsch.
    """

    def __init__(self, silence_ms: int, max_segment_s: float, factor: float):
        self.silence_frames = max(1, silence_ms // FRAME_MS)
        self.max_frames = int(max_segment_s * 1000 // FRAME_MS)
        self.factor = factor
        self.noise = deque(maxlen=100)     # ~3 s Historie
        self.preroll: deque[np.ndarray] = deque(maxlen=PREROLL_FRAMES)
        self.buffer: list[np.ndarray] = []
        self.silent_run = 0
        self.in_speech = False
        self.speech_run = 0

    def _is_speech(self, rms: float) -> bool:
        self.noise.append(rms)
        floor = float(np.percentile(self.noise, 20)) if len(self.noise) > 20 else rms
        return rms > max(floor * self.factor, 1e-4)

    def feed(self, frame: np.ndarray) -> np.ndarray | None:
        """Nimmt einen Frame, gibt ein fertiges Segment zurück oder None."""
        rms = float(np.sqrt(np.mean(np.square(frame))))
        speech = self._is_speech(rms)

        if not self.in_speech:
            self.preroll.append(frame)
            self.speech_run = self.speech_run + 1 if speech else 0
            if self.speech_run >= 3:       # 90 ms Sprache = Beginn
                self.in_speech = True
                self.buffer = list(self.preroll)
                self.silent_run = 0
            return None

        self.buffer.append(frame)
        self.silent_run = 0 if speech else self.silent_run + 1

        ends = self.silent_run >= self.silence_frames
        too_long = len(self.buffer) >= self.max_frames
        if ends or too_long:
            segment = np.concatenate(self.buffer)
            self.in_speech = False
            self.speech_run = 0
            self.buffer = []
            self.preroll.clear()
            return segment
        return None

    def flush(self) -> np.ndarray | None:
        if self.buffer:
            segment = np.concatenate(self.buffer)
            self.buffer = []
            return segment
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list-devices", action="store_true", help="Eingabegeräte zeigen")
    ap.add_argument("--device", type=int, default=None, help="Index des Eingabegeräts")
    ap.add_argument("--model", default=None,
                    help="Whisper-Modell (default: large-v3 mit GPU, small ohne)")
    ap.add_argument("--compute-type", default="auto",
                    help="auto (default), float16 (GPU), int8 (CPU)")
    ap.add_argument("--compute-device", default="auto",
                    choices=["auto", "cuda", "cpu"], help="Rechengerät (default auto)")
    ap.add_argument("--language", default="de")
    ap.add_argument("--out", default=None, help="Transkript-Datei (append)")
    ap.add_argument("--debug-log", default=None, help="verworfene Segmente mitschreiben")
    ap.add_argument("--silence-ms", type=int, default=700,
                    help="Pause, die ein Segment beendet (default 700)")
    ap.add_argument("--max-segment-s", type=float, default=20.0,
                    help="Zwangsschnitt, falls niemand Luft holt (default 20)")
    ap.add_argument("--vad-factor", type=float, default=3.0,
                    help="Sprache = Grundrauschen x Faktor (default 3.0)")
    ap.add_argument("--aggressive", action="store_true",
                    help="no_repeat_ngram_size=3 zuschalten")
    args = ap.parse_args(argv)

    if args.list_devices:
        print(sd.query_devices())
        return 0

    info = sd.query_devices(args.device, "input") if args.device is not None else None
    if info is not None:
        print(f"Eingang: {info['name']} ({info['max_input_channels']} Kanal/Kanäle)",
              file=sys.stderr)
        if info["max_input_channels"] < 2:
            print("Hinweis: Monokanal - Sprecherzuordnung ist nachträglich nicht "
                  "möglich. Für 'wer sagt was' braucht es Mikrofone pro Sprecher.",
                  file=sys.stderr)

    # Ohne GPU ist large-v3 nicht echtzeitfähig: kleineres Modell wählen,
    # sonst läuft die Transkription der Aufnahme hinterher und reißt Lücken.
    has_cuda = args.compute_device == "cuda"
    if args.compute_device == "auto":
        try:
            import ctranslate2
            has_cuda = ctranslate2.get_cuda_device_count() > 0
        except Exception:
            has_cuda = False
    model_name = args.model or ("large-v3" if has_cuda else "small")
    if not has_cuda:
        print(f"Keine CUDA-GPU erkannt -> Modell {model_name} auf CPU. Bei "
              f"Aussetzern kleineres Modell (--model base) verwenden.", file=sys.stderr)

    print(f"Lade Modell {model_name} ...", file=sys.stderr)
    model = WhisperModel(model_name, device=args.compute_device,
                         compute_type=args.compute_type)
    options = transcribe_options(args.language, args.aggressive)

    frames: queue.Queue[np.ndarray] = queue.Queue()
    stop = threading.Event()

    def callback(indata, _frames, _time, status):
        if status:
            print(f"[audio] {status}", file=sys.stderr)
        frames.put(indata[:, 0].copy())

    segmenter = Segmenter(args.silence_ms, args.max_segment_s, args.vad_factor)
    out_fh = open(args.out, "a", encoding="utf-8") if args.out else None
    dbg_fh = open(args.debug_log, "a", encoding="utf-8") if args.debug_log else None
    started = dt.datetime.now()
    kept = dropped = 0

    def emit(text: str, *, suspect: bool, raw: str = "") -> None:
        stamp = str(dt.timedelta(seconds=int((dt.datetime.now() - started).total_seconds())))
        line = f"[{stamp}] {text}"
        print(line, flush=True)
        if out_fh:
            out_fh.write(line + "\n")
            out_fh.flush()
        if suspect and dbg_fh:
            dbg_fh.write(f"[{stamp}] VERWORFEN: {raw}\n")
            dbg_fh.flush()

    def handle(segment: np.ndarray) -> None:
        nonlocal kept, dropped
        if len(segment) < SAMPLE_RATE // 2:        # < 0,5 s: nicht auswertbar
            return
        parts, _ = model.transcribe(segment, **options)
        text = " ".join(p.text.strip() for p in parts).strip()
        if not text:
            return

        verdict = analyse(text)
        if verdict.degenerate:
            gefaltet = collapse(text)
            if not analyse(gefaltet).degenerate and len(gefaltet) > 3:
                kept += 1
                emit(gefaltet, suspect=False)      # war nur vervielfacht
            else:
                dropped += 1
                emit(f"[unverständlich, {len(segment)/SAMPLE_RATE:.1f}s - "
                     f"{verdict.reason}]", suspect=True, raw=text)
            return
        kept += 1
        emit(text, suspect=False)

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                            blocksize=FRAME, device=args.device, callback=callback):
            print("Aufnahme läuft. Abbruch mit Ctrl+C.", file=sys.stderr)
            while not stop.is_set():
                frame = frames.get()
                segment = segmenter.feed(frame)
                if segment is not None:
                    handle(segment)
    except KeyboardInterrupt:
        rest = segmenter.flush()
        if rest is not None:
            handle(rest)
    finally:
        print(f"\nSegmente: {kept} übernommen, {dropped} verworfen.", file=sys.stderr)
        for fh in (out_fh, dbg_fh):
            if fh:
                fh.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
