#!/usr/bin/env python3
"""Smoke-Test der Live-Pipeline ohne Mikrofon, GPU oder Modell.

Prüft die zwei Teile, die beim Start schiefgehen können, bevor sie auf der
Sitzung schiefgehen:

1. Segmenter: findet er aus synthetischem Audio (Stille - Sprache - Stille)
   genau ein Segment, und schneidet er an der Pause?
2. classify_segment: landet aus Whisper-Ausgaben das Richtige im Protokoll -
   gefaltet, markiert oder unverändert?

faster-whisper und sounddevice werden als Attrappe eingehängt; der Test
installiert und lädt nichts.

    python test_pipeline.py
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import numpy as np

# --- Attrappen, damit der Import von live_transcribe ohne Audio-Stack klappt --
_sd = types.ModuleType("sounddevice")
_sd.InputStream = object
_sd.query_devices = lambda *a, **k: {}
sys.modules.setdefault("sounddevice", _sd)

_fw = types.ModuleType("faster_whisper")
_fw.WhisperModel = object
sys.modules.setdefault("faster_whisper", _fw)

from live_transcribe import (  # noqa: E402  (nach den Attrappen)
    FRAME,
    SAMPLE_RATE,
    Segmenter,
    classify_segment,
    transcribe_options,
)

RNG = np.random.default_rng(42)


def frames_from(signal: np.ndarray) -> list[np.ndarray]:
    usable = len(signal) - len(signal) % FRAME
    return [signal[i : i + FRAME] for i in range(0, usable, FRAME)]


def synthetic(seconds: float, amplitude: float) -> np.ndarray:
    """Rauschen in definierter Lautstärke - Raumgrundgeräusch bzw. Sprache."""
    return (RNG.standard_normal(int(SAMPLE_RATE * seconds)) * amplitude).astype(np.float32)


def test_segmenter() -> list[str]:
    """1 s Ruhe, 2 s 'Sprache', 1,5 s Ruhe -> ein Segment von ~2 s."""
    errors = []
    signal = np.concatenate([
        synthetic(1.0, 0.002),     # Grundrauschen (Owl-AGC-Pegel)
        synthetic(2.0, 0.08),      # Sprache, 40x über dem Rauschen
        synthetic(1.5, 0.002),
    ])
    seg = Segmenter(silence_ms=700, max_segment_s=20.0, factor=3.0)
    segments = [s for frame in frames_from(signal) if (s := seg.feed(frame)) is not None]

    if len(segments) != 1:
        errors.append(f"Segmenter: {len(segments)} Segmente statt 1")
    else:
        dauer = len(segments[0]) / SAMPLE_RATE
        # 2 s Sprache + 300 ms Pre-Roll + 700 ms Pause bis zum Schnitt
        if not 2.0 <= dauer <= 3.3:
            errors.append(f"Segmenter: Segment {dauer:.2f}s, erwartet 2.0-3.3s")
        print(f"ok  Segmenter: 1 Segment, {dauer:.2f}s")

    # Zwangsschnitt, wenn niemand Luft holt
    seg2 = Segmenter(silence_ms=700, max_segment_s=2.0, factor=3.0)
    dauer_signal = np.concatenate([synthetic(0.5, 0.002), synthetic(6.0, 0.08)])
    forced = [s for frame in frames_from(dauer_signal) if (s := seg2.feed(frame)) is not None]
    if len(forced) < 2:
        errors.append(f"Zwangsschnitt: {len(forced)} Segmente, erwartet >= 2")
    else:
        print(f"ok  Zwangsschnitt bei max_segment_s=2: {len(forced)} Segmente")

    # Reine Stille darf nichts erzeugen
    seg3 = Segmenter(silence_ms=700, max_segment_s=20.0, factor=3.0)
    leer = [s for frame in frames_from(synthetic(4.0, 0.002)) if (s := seg3.feed(frame)) is not None]
    if leer:
        errors.append(f"Stille: {len(leer)} Segmente, erwartet 0")
    else:
        print("ok  Stille erzeugt kein Segment")
    return errors


def test_classify() -> list[str]:
    """Die drei realen Fälle aus dem Betrieb."""
    errors = []
    cases = [
        # (Whisper-Ausgabe, erwartete Ausgabe im Protokoll, verdächtig?)
        ("Also, ich glaube, die Doktoranden, " + "die Doktoranden, " * 43 + "die",
         "Also ich glaube die Doktoranden", False),
        ("...und dann kam es dann... " * 25, None, False),      # gefaltet, Inhalt egal
        ("Die Begutachtung dauert länger, deshalb verschieben wir den Termin.",
         "Die Begutachtung dauert länger, deshalb verschieben wir den Termin.", False),
        ("Ähm. Ähm. Ähm. Ähm. Ähm. Ähm. Ähm. Ähm. Ähm. Ähm. Ähm. Ähm.", None, None),
    ]
    for text, expected, expect_suspect in cases:
        line, suspect, raw = classify_segment(text, 4.2)
        if expected is not None and line != expected:
            errors.append(f"classify: {line!r} statt {expected!r}")
        if expect_suspect is not None and suspect != expect_suspect:
            errors.append(f"classify: suspect={suspect}, erwartet {expect_suspect}")
        if suspect and not raw:
            errors.append("classify: verdächtig, aber kein Rohtext fürs Debug-Log")
        print(f"ok  classify -> {'[verworfen] ' if suspect else ''}{line[:60]}")
    return errors


def test_options() -> list[str]:
    """Die Parameter, die den Loop verhindern, müssen gesetzt bleiben."""
    errors = []
    opt = transcribe_options("de", aggressive=False)
    erwartet = {
        "language": "de",
        "condition_on_previous_text": False,
        "no_speech_threshold": 0.6,
        "vad_filter": True,
        "no_repeat_ngram_size": 0,
    }
    for key, value in erwartet.items():
        if opt.get(key) != value:
            errors.append(f"Option {key}={opt.get(key)!r}, erwartet {value!r}")
    if transcribe_options("de", aggressive=True)["no_repeat_ngram_size"] != 3:
        errors.append("--aggressive setzt no_repeat_ngram_size nicht auf 3")
    if not errors:
        print("ok  Anti-Loop-Optionen vollständig")
    return errors


def test_chunker() -> list[str]:
    """Dauergerede ohne Pause: es muss trotzdem geschnitten werden."""
    from chunker import read_wav, split, stitch, write_wav

    errors = []
    tmp = Path(__file__).with_name("_test_dauer.wav")
    audio = synthetic(70.0, 0.08)                 # durchgehend laut
    for t in (18, 37, 55):                        # nur relativ leisere Stellen
        audio[int(t * SAMPLE_RATE): int((t + 0.6) * SAMPLE_RATE)] *= 0.05
    write_wav(tmp, audio, SAMPLE_RATE)
    try:
        a, sr = read_wav(tmp)
        spans = split(a, sr, target_s=20.0, search_s=5.0, overlap_s=0.5)
    finally:
        tmp.unlink(missing_ok=True)

    if len(spans) < 3:
        errors.append(f"Chunker: {len(spans)} Stücke bei 70s, erwartet >= 3")
    if any((b - a_) / sr > 26.0 for a_, b in spans):
        errors.append("Chunker: Stück länger als 26s")
    if any(spans[i][1] < spans[i + 1][0] for i in range(len(spans) - 1)):
        errors.append("Chunker: Lücke zwischen zwei Stücken")
    # Die Schnitte müssen auf den leisen Stellen liegen, nicht im Redefluss.
    ref = float(np.sqrt(np.mean(np.square(a))))
    for _, b in spans[:-1]:
        umgebung = a[b - sr // 10: b + sr // 10]
        if float(np.sqrt(np.mean(np.square(umgebung)))) > 0.6 * ref:
            errors.append(f"Chunker: Schnitt bei {b/sr:.1f}s liegt nicht auf einer leisen Stelle")
    if stitch(["das ist ja ganz entscheidend für die",
               "für die Zukunft der Promotion"]) != \
            "das ist ja ganz entscheidend für die Zukunft der Promotion":
        errors.append("stitch: Überlapp wurde nicht entfernt")
    if not errors:
        print(f"ok  Chunker: {len(spans)} Stücke, Schnitte auf den leisen Stellen, stitch sauber")
    return errors


def main() -> int:
    errors = test_segmenter() + test_classify() + test_options() + test_chunker()
    print()
    if errors:
        for e in errors:
            print("FEHL", e)
        return 1
    print("Alle Prüfungen bestanden. Die Pipeline startet; für den echten Lauf "
          "fehlen nur Mikrofon und Modell.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
