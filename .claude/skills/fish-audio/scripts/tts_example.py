#!/usr/bin/env python3
"""Fish Audio: TTS, streaming TTS, ASR and voice cloning in one runnable file.

Setup:
    pip install "fish-audio-sdk[utils]"
    export FISH_API_KEY=...

Usage:
    python tts_example.py tts        "Text to speak" [reference_id]
    python tts_example.py ws         "Text to speak" [reference_id]
    python tts_example.py asr        input.wav [language]
    python tts_example.py clone      "Voice title" sample.wav "exact transcript of sample.wav"
    python tts_example.py voices     [search title]
    python tts_example.py credits
"""

from __future__ import annotations

import sys

from fishaudio import FishAudio
from fishaudio.exceptions import FishAudioError, RateLimitError
from fishaudio.types import Prosody, ReferenceAudio, TTSConfig
from fishaudio.utils import save

MODEL = "s2-pro"


def cmd_tts(text: str, reference_id: str | None = None) -> None:
    """One-shot synthesis to out.mp3."""
    client = FishAudio()
    config = TTSConfig(format="mp3", latency="balanced", prosody=Prosody(speed=1.0))
    audio = client.tts.convert(
        text=text, reference_id=reference_id, config=config, model=MODEL
    )
    save(audio, "out.mp3")
    print(f"out.mp3 ({len(audio)} bytes)")


def cmd_ws(text: str, reference_id: str | None = None) -> None:
    """Realtime synthesis: text arrives in chunks, audio is consumed as it is produced."""

    def text_chunks():
        for word in text.split():
            yield word + " "

    client = FishAudio()
    chunks: list[bytes] = []
    for chunk in client.tts.stream_websocket(
        text_chunks(), reference_id=reference_id, latency="balanced", model=MODEL
    ):
        chunks.append(chunk)
    save(b"".join(chunks), "out_ws.mp3")
    print(f"out_ws.mp3 ({sum(len(c) for c in chunks)} bytes, {len(chunks)} chunks)")


def cmd_asr(path: str, language: str | None = None) -> None:
    client = FishAudio()
    with open(path, "rb") as f:
        result = client.asr.transcribe(audio=f.read(), language=language)
    print(f"{result.text}\n--- {result.duration / 1000:.2f}s")
    for seg in result.segments:
        print(f"[{seg.start:6.2f} - {seg.end:6.2f}] {seg.text}")


def cmd_clone(title: str, sample_path: str, transcript: str) -> None:
    """Two paths: a persistent voice model, and one-off cloning via references."""
    client = FishAudio()
    with open(sample_path, "rb") as f:
        sample = f.read()

    voice = client.voices.create(
        title=title, voices=[sample], texts=[transcript], visibility="private"
    )
    print(f"voice id={voice.id} state={voice.state}")  # poll until state == "trained"

    # Same effect without storing a model:
    audio = client.tts.convert(
        text="Dies ist die geklonte Stimme.",
        references=[ReferenceAudio(audio=sample, text=transcript)],
        model=MODEL,
    )
    save(audio, "out_clone.mp3")
    print(f"out_clone.mp3 ({len(audio)} bytes)")


def cmd_voices(title: str | None = None) -> None:
    client = FishAudio()
    page = client.voices.list(page_size=10, title=title, sort_by="task_count")
    print(f"total={page.total}")
    for voice in page.items:
        print(f"{voice.id}  {voice.state:8}  {voice.title}")


def cmd_credits() -> None:
    client = FishAudio()
    print(f"credit={client.account.get_credits().credit}")
    package = client.account.get_package()
    print(f"package={package.type} balance={package.balance}/{package.total}")


COMMANDS = {
    "tts": cmd_tts,
    "ws": cmd_ws,
    "asr": cmd_asr,
    "clone": cmd_clone,
    "voices": cmd_voices,
    "credits": cmd_credits,
}


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 2
    try:
        COMMANDS[argv[0]](*argv[1:])
    except RateLimitError:
        print("rate limited — back off and retry", file=sys.stderr)
        return 1
    except FishAudioError as exc:
        print(f"Fish Audio error: {exc}", file=sys.stderr)
        return 1
    except TypeError:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
