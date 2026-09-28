#!/usr/bin/env python3
"""Transkription über eine OpenAI-kompatible API (Scaleway Generative APIs).

Bei einem gehosteten Dienst sind `condition_on_previous_text`, VAD und
`repetition_penalty` nicht erreichbar. Was bleibt, sind drei Hebel - und sie
genügen, wenn man sie zusammen verwendet:

1. **Stückweise Anfragen** (chunker.py): 20-s-Stücke, geschnitten an der
   leisesten Stelle, jedes als eigene Anfrage. Ohne Kontextübergabe kann sich
   ein Loop nicht über Stückgrenzen fortsetzen.
2. **Temperatur-Fallback im Client**: Whisper macht das intern - bei einer
   kollabierten Dekodierung wird mit höherer Temperatur neu dekodiert. Über
   die API muss der Client das selbst tun: erkennt loop_guard einen Kollaps,
   wird dasselbe Stück mit 0.2, dann 0.4, dann 0.6 erneut angefragt.
3. **Segment-Metriken auswerten**, falls der Dienst `verbose_json` mit
   `compression_ratio`, `avg_logprob` und `no_speech_prob` liefert. Das sind
   genau die Größen, mit denen Whisper intern verwirft - Schwellwerte 2.4,
   -1.0 und 0.6.

Fallstrick: `prompt` ist **kein** Ort für den Text des Vorgängerstücks. Das
Feld konditioniert den Decoder und schleppt damit genau den Loop weiter, den
die Stückelung gerade unterbricht. Nur für feste Fachbegriffe verwenden.

Nur Standardbibliothek plus numpy - kein openai-SDK nötig.

    set SCW_SECRET_KEY=...        (PowerShell: $env:SCW_SECRET_KEY="...")
    python openai_compatible.py sitzung.wav --out sitzung.txt
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Callable

import numpy as np

from chunker import read_wav, split, stitch, write_wav
from loop_guard import analyse, collapse, tokenize

# Schwellwerte aus Whispers eigener Verwurfslogik
COMPRESSION_RATIO_LIMIT = 2.4
AVG_LOGPROB_LIMIT = -1.0
NO_SPEECH_LIMIT = 0.6

TEMPERATURE_LADDER = (0.0, 0.2, 0.4, 0.6)

Sender = Callable[[bytes, float], dict]


def build_multipart(fields: dict[str, str], wav: bytes,
                    filename: str = "chunk.wav") -> tuple[str, bytes]:
    """Baut einen multipart/form-data-Body (ohne Fremdbibliothek)."""
    boundary = f"----raumtranskription{uuid.uuid4().hex}"
    parts: list[bytes] = []
    for key, value in fields.items():
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n"
            f"{value}\r\n".encode()
        )
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
        f"filename=\"{filename}\"\r\nContent-Type: audio/wav\r\n\r\n".encode()
    )
    parts.append(wav)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    return f"multipart/form-data; boundary={boundary}", b"".join(parts)


def make_sender(base_url: str, api_key: str, model: str, language: str,
                prompt: str | None, timeout: float = 300.0,
                retries: int = 4) -> Sender:
    """Liefert eine Funktion (wav_bytes, temperature) -> Antwort-JSON."""
    url = base_url.rstrip("/") + "/audio/transcriptions"

    def send(wav: bytes, temperature: float) -> dict:
        fields = {
            "model": model,
            "language": language,            # nie Autodetect auf Gemurmel
            "response_format": "verbose_json",
            "temperature": f"{temperature}",
        }
        if prompt:
            fields["prompt"] = prompt        # nur Fachbegriffe, nie Vorgängertext
        content_type, body = build_multipart(fields, wav)

        last: Exception | None = None
        for versuch in range(retries):
            req = urllib.request.Request(url, data=body, method="POST")
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("Content-Type", content_type)
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code in (408, 429, 500, 502, 503, 504) and versuch < retries - 1:
                    wartezeit = 2 ** versuch
                    print(f"    HTTP {exc.code}, neuer Versuch in {wartezeit}s",
                          file=sys.stderr)
                    time.sleep(wartezeit)
                    last = exc
                    continue
                raise                        # 401/403/413 sind nicht wiederholbar
            except (urllib.error.URLError, TimeoutError) as exc:
                if versuch < retries - 1:
                    time.sleep(2 ** versuch)
                    last = exc
                    continue
                raise
        raise RuntimeError(f"Anfrage endgültig fehlgeschlagen: {last}")

    return send


def usable_text(payload: dict) -> tuple[str, list[str]]:
    """Text aus der Antwort, um unbrauchbare Segmente bereinigt.

    Rückgabe: (Text, Liste der Verwurfsgründe). Liefert der Dienst keine
    Segment-Metriken, wird `text` unverändert übernommen - dann greift nur
    loop_guard.
    """
    segments = payload.get("segments") or []
    if not segments:
        return (payload.get("text") or "").strip(), []

    behalten: list[str] = []
    gruende: list[str] = []
    for seg in segments:
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        cr = seg.get("compression_ratio")
        lp = seg.get("avg_logprob")
        ns = seg.get("no_speech_prob")
        if cr is not None and cr > COMPRESSION_RATIO_LIMIT:
            gruende.append(f"compression_ratio {cr:.2f} > {COMPRESSION_RATIO_LIMIT}")
            continue
        if lp is not None and lp < AVG_LOGPROB_LIMIT:
            gruende.append(f"avg_logprob {lp:.2f} < {AVG_LOGPROB_LIMIT}")
            continue
        if ns is not None and ns > NO_SPEECH_LIMIT:
            gruende.append(f"no_speech_prob {ns:.2f} > {NO_SPEECH_LIMIT}")
            continue
        behalten.append(text)
    return " ".join(behalten).strip(), gruende


def transcribe_chunk(sender: Sender, wav: bytes, seconds: float,
                     ladder: tuple[float, ...] = TEMPERATURE_LADDER
                     ) -> tuple[str, bool, str, float]:
    """Ein Stück transkribieren, mit Temperatur-Fallback bei Kollaps.

    Reihenfolge ist wesentlich: bei einem Kollaps wird **zuerst** mit höherer
    Temperatur neu angefragt, und erst wenn alle Stufen kollabieren, wird die
    Faltung als Rettung verwendet. Umgekehrt würde die Faltung den Fallback
    kurzschließen - "entscheidendendend" wird zu "entscheidend" geglättet und
    sieht sauber aus, obwohl der Rest des Stücks nie transkribiert wurde.

    Rückgabe: (Text fürs Protokoll, verdächtig, Rohtext, benutzte Temperatur).
    """
    kandidaten: list[tuple[str, str, float]] = []      # (Rohtext, Grund, T)
    letzter_grund = "keine Antwort"
    for temperature in ladder:
        payload = sender(wav, temperature)
        text, gruende = usable_text(payload)
        if not text:
            letzter_grund = "; ".join(gruende) or "leere Antwort"
            continue
        verdict = analyse(text)
        if not verdict.degenerate:
            return text, False, "", temperature
        kandidaten.append((text, verdict.reason, temperature))

    # Alle Stufen kollabiert: den inhaltsreichsten Versuch retten.
    gerettet: list[tuple[int, str, str, float]] = []
    for roh, grund, temperature in kandidaten:
        gefaltet = collapse(roh)
        if not analyse(gefaltet).degenerate and len(tokenize(gefaltet)) >= 2:
            gerettet.append((len(tokenize(gefaltet)), gefaltet, roh, temperature))
    if gerettet:
        _, gefaltet, roh, temperature = max(gerettet, key=lambda x: x[0])
        return gefaltet, False, roh, temperature

    if kandidaten:
        roh, letzter_grund, temperature = kandidaten[-1]
    else:
        roh, temperature = "", ladder[-1]
    return (f"[unverständlich, {seconds:.1f}s - {letzter_grund}]",
            True, roh, temperature)


def run(path: Path, sender: Sender, *, target_s: float, search_s: float,
        overlap_s: float, out: Path | None, debug: Path | None) -> int:
    audio, sr = read_wav(path)
    spans = split(audio, sr, target_s=target_s, search_s=search_s, overlap_s=overlap_s)
    print(f"{path}: {len(audio)/sr:.1f}s -> {len(spans)} Stücke", file=sys.stderr)

    tmp = path.with_name(f".{path.stem}_chunk.wav")
    texte: list[str] = []
    verworfen = 0
    dbg = open(debug, "w", encoding="utf-8") if debug else None
    try:
        for i, (a, b) in enumerate(spans, 1):
            write_wav(tmp, audio[a:b], sr)
            wav = tmp.read_bytes()
            text, suspect, raw, temp = transcribe_chunk(sender, wav, (b - a) / sr)
            marke = "!" if suspect else " "
            print(f"  {marke} {i:3}/{len(spans)}  {a/sr:7.1f}s  T={temp:.1f}  "
                  f"{text[:70]}", file=sys.stderr)
            texte.append(text)
            if suspect:
                verworfen += 1
            if dbg and raw:
                dbg.write(f"[{a/sr:.1f}s-{b/sr:.1f}s] T={temp} ROH: {raw}\n")
    finally:
        tmp.unlink(missing_ok=True)
        if dbg:
            dbg.close()

    ergebnis = stitch(texte)
    if out:
        out.write_text(ergebnis + "\n", encoding="utf-8")
        print(f"\n{out} geschrieben.", file=sys.stderr)
    else:
        print(ergebnis)
    print(f"{len(spans) - verworfen}/{len(spans)} Stücke verwertbar, "
          f"{verworfen} als unverständlich markiert.", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("datei", help="PCM-WAV-Aufnahme")
    ap.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", ""),
                    help="z. B. https://api.scaleway.ai/v1 (oder Env OPENAI_BASE_URL)")
    ap.add_argument("--model", default="whisper-large-v3",
                    help="Modellname des Dienstes (default whisper-large-v3)")
    ap.add_argument("--key-env", default="SCW_SECRET_KEY",
                    help="Name der Umgebungsvariablen mit dem API-Key")
    ap.add_argument("--language", default="de")
    ap.add_argument("--prompt", default=None,
                    help="feste Fachbegriffe - NIE den Text des Vorgängerstücks")
    ap.add_argument("--target", type=float, default=20.0)
    ap.add_argument("--search", type=float, default=5.0)
    ap.add_argument("--overlap", type=float, default=0.5)
    ap.add_argument("--out", default=None)
    ap.add_argument("--debug-log", default=None)
    args = ap.parse_args(argv)

    if not args.base_url:
        ap.error("--base-url fehlt (oder Umgebungsvariable OPENAI_BASE_URL setzen)")
    api_key = os.getenv(args.key_env)
    if not api_key:
        ap.error(f"Kein API-Key: Umgebungsvariable {args.key_env} ist nicht gesetzt")

    sender = make_sender(args.base_url, api_key, args.model, args.language, args.prompt)
    return run(Path(args.datei), sender, target_s=args.target, search_s=args.search,
               overlap_s=args.overlap,
               out=Path(args.out) if args.out else None,
               debug=Path(args.debug_log) if args.debug_log else None)


if __name__ == "__main__":
    raise SystemExit(main())
