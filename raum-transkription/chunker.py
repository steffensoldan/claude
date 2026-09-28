#!/usr/bin/env python3
"""Zerlegt eine Aufnahme in Stücke, auch wenn niemand eine Pause macht.

Das Kernproblem bei Diskussionen mit mehreren Sprechenden: pausenbasierte
Segmentierung findet keine Kante, das Zeitfenster läuft voll, und der Decoder
kollabiert in eine Wiederholung. Die Abhilfe ist nicht "länger warten",
sondern **erzwungenes Schneiden an der leisesten Stelle** im Zielbereich -
es gibt immer eine relativ leiseste Stelle, auch ohne echte Pause.

Verfahren:

1. Zielabstand (Default 20 s) plus Suchfenster (Default ±5 s).
2. Im Suchfenster das leiseste 100-ms-Fenster suchen, dort schneiden.
3. Ein kleiner Überlapp (Default 0,5 s) verhindert abgeschnittene Wortanfänge.
4. Jedes Stück wird als **eigene, kontextfreie Anfrage** transkribiert - damit
   kann sich ein Loop nicht über Stückgrenzen fortsetzen.
5. Die Texte werden über den Überlapp wieder zusammengefügt (stitch()), die
   Doppelung am Nahtpunkt wird entfernt.

Engine-unabhängig: funktioniert mit einer gehosteten API (Scaleway, OpenAI-
kompatibel) genauso wie mit lokalem faster-whisper. Nur Standardbibliothek
plus numpy.

    python chunker.py sitzung.wav --out-dir chunks --target 20
    python chunker.py sitzung.wav --plan-only
"""

from __future__ import annotations

import argparse
import wave
from pathlib import Path

import numpy as np

WINDOW_MS = 100          # Auflösung der Leisestelle-Suche


def read_wav(path: str | Path) -> tuple[np.ndarray, int]:
    """Liest eine PCM-WAV-Datei als Mono-float32 (-1..1) samt Samplerate."""
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        channels = wf.getnchannels()
        width = wf.getsampwidth()
        raw = wf.readframes(wf.getnframes())

    dtypes = {1: np.uint8, 2: np.int16, 4: np.int32}
    if width not in dtypes:
        raise ValueError(f"{width*8}-bit WAV wird nicht unterstützt - "
                         f"vorher mit ffmpeg nach 16 bit PCM wandeln")
    data = np.frombuffer(raw, dtype=dtypes[width]).astype(np.float32)
    if width == 1:
        data = (data - 128.0) / 128.0
    else:
        data /= float(2 ** (8 * width - 1))
    if channels > 1:
        data = data.reshape(-1, channels).mean(axis=1)
    return data, sr


def write_wav(path: str | Path, audio: np.ndarray, sr: int) -> None:
    clipped = np.clip(audio, -1.0, 1.0)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((clipped * 32767.0).astype(np.int16).tobytes())


def _window_rms(audio: np.ndarray, sr: int) -> tuple[np.ndarray, int]:
    """RMS pro 100-ms-Fenster (für die Suche nach der leisesten Stelle)."""
    win = max(1, sr * WINDOW_MS // 1000)
    usable = len(audio) - len(audio) % win
    if usable == 0:
        return np.array([0.0]), win
    blocks = audio[:usable].reshape(-1, win)
    return np.sqrt(np.mean(np.square(blocks), axis=1)), win


def find_cut(audio: np.ndarray, sr: int, start: int,
             target_s: float, search_s: float) -> int:
    """Schnittpunkt (Sample-Index) nahe start+target_s an der leisesten Stelle."""
    target = start + int(target_s * sr)
    if target >= len(audio):
        return len(audio)
    lo = max(start + sr, target - int(search_s * sr))     # min. 1 s Stück
    hi = min(len(audio), target + int(search_s * sr))
    if hi - lo < sr // 2:
        return min(target, len(audio))

    rms, win = _window_rms(audio[lo:hi], sr)
    quietest = int(np.argmin(rms))
    return lo + quietest * win + win // 2


def split(audio: np.ndarray, sr: int, *, target_s: float = 20.0,
          search_s: float = 5.0, overlap_s: float = 0.5,
          min_s: float = 1.0) -> list[tuple[int, int]]:
    """Liste von (start, ende) in Samples, mit Überlapp."""
    spans: list[tuple[int, int]] = []
    overlap = int(overlap_s * sr)
    pos = 0
    while pos < len(audio):
        cut = find_cut(audio, sr, pos, target_s, search_s)
        if len(audio) - cut < min_s * sr:      # Reststück anhängen
            cut = len(audio)
        spans.append((max(0, pos - overlap if spans else 0), cut))
        if cut >= len(audio):
            break
        pos = cut
    return spans


def stitch(texts: list[str], max_overlap_words: int = 12) -> str:
    """Fügt Stücktexte zusammen und entfernt die Doppelung am Überlapp."""
    result: list[str] = []
    for text in texts:
        words = text.split()
        if not result or not words:
            result += words
            continue
        best = 0
        limit = min(max_overlap_words, len(result), len(words))
        for n in range(limit, 0, -1):
            tail = [w.lower().strip(".,;:!?") for w in result[-n:]]
            head = [w.lower().strip(".,;:!?") for w in words[:n]]
            if tail == head:
                best = n
                break
        result += words[best:]
    return " ".join(result)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("datei", help="PCM-WAV-Datei (16 bit empfohlen)")
    ap.add_argument("--out-dir", default="chunks", help="Zielverzeichnis für die Stücke")
    ap.add_argument("--target", type=float, default=20.0, help="Ziellänge in s (default 20)")
    ap.add_argument("--search", type=float, default=5.0, help="Suchfenster ±s (default 5)")
    ap.add_argument("--overlap", type=float, default=0.5, help="Überlapp in s (default 0.5)")
    ap.add_argument("--plan-only", action="store_true", help="nur Schnittplan zeigen")
    args = ap.parse_args(argv)

    audio, sr = read_wav(args.datei)
    spans = split(audio, sr, target_s=args.target, search_s=args.search,
                  overlap_s=args.overlap)
    rms_all = float(np.sqrt(np.mean(np.square(audio)))) or 1e-9

    print(f"{args.datei}: {len(audio)/sr:.1f}s, {sr} Hz -> {len(spans)} Stücke")
    out = Path(args.out_dir)
    if not args.plan_only:
        out.mkdir(parents=True, exist_ok=True)

    for i, (a, b) in enumerate(spans, 1):
        cut_rms, win = _window_rms(audio[max(0, b - sr // 10): b + sr // 10], sr)
        leise = float(np.min(cut_rms)) / rms_all
        name = f"chunk_{i:04d}.wav"
        print(f"  {name}  {a/sr:7.2f} - {b/sr:7.2f}s  ({(b-a)/sr:5.2f}s, "
              f"Schnittpegel {leise:.2f}x Mittel)")
        if not args.plan_only:
            write_wav(out / name, audio[a:b], sr)

    if not args.plan_only:
        print(f"\nGeschrieben nach {out}/. Jedes Stück als EIGENE Anfrage "
              f"transkribieren (kein Kontext, kein Prompt aus dem Vorgänger),\n"
              f"dann die Texte mit loop_guard prüfen und mit stitch() zusammenfügen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
