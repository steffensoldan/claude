---
name: fish-audio
description: Use the Fish Audio API for text-to-speech, speech-to-text, voice cloning and realtime audio streaming. Trigger on mentions of Fish Audio, fish.audio, api.fish.audio, fish-audio-sdk, the fishaudio Python/TypeScript clients, models s2-pro / s1 / speech-1.6, FISH_API_KEY, or on tasks like "synthesize speech", "clone a voice", "transcribe this audio", "stream TTS over websocket" where Fish Audio is the chosen provider.
---

# Fish Audio API

Speech platform: TTS (incl. instant voice cloning and realtime streaming), ASR, voice-model
management, account/credit queries. One API key, one base URL.

## Core facts

| Item | Value |
|---|---|
| Base URL | `https://api.fish.audio` |
| Auth | `Authorization: Bearer $FISH_API_KEY` (env var `FISH_API_KEY`; keys at fish.audio/app/api-keys) |
| TTS | `POST /v1/tts` — body **msgpack**, model chosen via `model:` header, response = audio byte stream |
| TTS realtime | `WSS /v1/tts/live` — msgpack event frames both directions |
| ASR | `POST /v1/asr` — body **msgpack**, response JSON |
| Voices | `GET /model`, `GET /model/{id}`, `POST /model` (multipart), `PATCH /model/{id}`, `DELETE /model/{id}` |
| Account | `GET /wallet/self/api-credit`, `GET /wallet/self/package` (no `/v1` prefix) |
| Python SDK | `pip install fish-audio-sdk` → import `fishaudio` (`FishAudio`, `AsyncFishAudio`) |
| TS SDK | `npm install fish-audio` → `FishAudioClient` |

Prefer the official SDK over hand-rolled HTTP: the TTS and ASR bodies are msgpack, not JSON,
and the SDK owns that plus streaming, websocket framing and error mapping.

## Quickstart (Python)

```python
from fishaudio import FishAudio
from fishaudio.utils import play, save

client = FishAudio()                              # reads FISH_API_KEY

audio = client.tts.convert(text="Hallo Welt")     # bytes, model defaults to "s2-pro"
save(audio, "out.mp3")

with open("in.wav", "rb") as f:                   # transcription
    r = client.asr.transcribe(audio=f.read(), language="de")
print(r.text, r.duration)                         # duration in ms
```

## Choosing the right call

| Need | Use |
|---|---|
| Whole file, text known upfront | `client.tts.convert(text=...)` → `bytes` |
| Same, but pipe chunks while they arrive (HTTP) | `client.tts.stream(text=...)` → `AudioStream` (iterate, or `.collect()`) |
| Text produced incrementally (LLM output, live agent) | `client.tts.stream_websocket(text_iterable)` |
| Reuse one voice/format/latency setup | build a `TTSConfig` once, pass `config=` |
| One-off voice imitation | `references=[ReferenceAudio(audio=..., text=...)]` |
| Voice reused across requests | `client.voices.create(...)` once, then `reference_id=voice.id` |

## Models

- `s2-pro` — SDK default; use unless told otherwise.
- `s1` — alternative current model.
- `speech-1.5`, `speech-1.6` — deprecated; the SDK emits a `DeprecationWarning`.

Selected by the `model:` HTTP header (`model=` kwarg in the SDK), not by a body field.

## Parameters that matter

- `format`: `mp3` (default) | `wav` | `pcm` | `opus`; `mp3_bitrate` 64/128/192, `opus_bitrate` -1000/24/32/48/64, `sample_rate` optional.
- `latency`: `balanced` (default, faster) | `normal` (higher quality).
- `prosody`: `speed` 0.5–2.0, `volume` -20…+20 dB. The `speed=` shortcut on `convert`/`stream` overrides `config.prosody.speed` and keeps `volume`.
- `chunk_length` 100–300 (default 200): lower = faster first byte, higher = better continuity.
- `temperature` / `top_p` both default 0.7; lower for consistency, higher for variation.
- `normalize` (default `True`): text cleanup/normalization — keep on for numbers, dates, abbreviations.

## Pitfalls

- `/v1/tts` and `/v1/asr` reject JSON — pack the body with msgpack (`ormsgpack`) and set `Content-Type: application/msgpack`.
- Reference audio `text` must transcribe the sample **exactly**, punctuation included; wrong text degrades prosody.
- `POST /model` is `multipart/form-data`: repeated `voices` file parts plus form fields (`title`, `type=tts`, `train_mode=fast`, `texts`, `tags`, `visibility`, …), not msgpack, not JSON.
- `PATCH /model/{id}` and `DELETE /model/{id}` return no body — don't parse the response.
- Wallet endpoints are unversioned and return `_id` (aliased to `id` in the SDK).
- Realtime: send `start` → n × `text` (optional `flush`) → `stop`; a server `finish` event with `reason: "error"` is a failure, `reason: "stop"` is a clean end. In the TS SDK set `text: ""` in the initial request and stream via the text generator.
- Distinguish `AuthenticationError` (401, bad key) from `PermissionError` (403, key lacks access) and `RateLimitError` (429, back off and retry); `ValidationError` is client-side.
- Audio playback helpers need the extra: `pip install "fish-audio-sdk[utils]"` (and a system player; a missing one raises `DependencyError`).
- Legacy `fish_audio_sdk` package (`Session`, `WebSocketSession`) still ships in the same distribution but gets no updates — new code uses `fishaudio`.

## Key handling

- The key lives in the environment: `FISH_API_KEY`. Both SDKs read it automatically; never
  hardcode it in source, notebooks, prompts or commit messages.
- If a JSON config is required, keep the key out of the tracked one: `config.example.json`
  holds the shape and points at the env var; the real values go into `fish-audio.local.json`
  (matched by the repo's `*.local.json` ignore rule) or into `.env`.

  ```python
  import json, os
  cfg = json.load(open("fish-audio.local.json"))["fish_audio"]
  client = FishAudio(api_key=os.environ[cfg["api_key_env"]], base_url=cfg["base_url"])
  ```
- Never echo the key into logs or error output; `APIError.body` can contain request context —
  scrub before pasting it anywhere.
- A key that has been pasted into a chat, ticket, screenshot or shared file counts as
  compromised: rotate it at fish.audio/app/api-keys and update the environment.

## References

- `references/http-api.md` — raw endpoint contracts, request/response fields, websocket protocol, error mapping.
- `references/python-sdk.md` — full method signatures, `TTSConfig` field table, options, exceptions.
- `references/typescript-sdk.md` — `FishAudioClient` usage.
- `scripts/tts_example.py` — runnable TTS/ASR/clone example.
- `config.example.json` — config shape; copy to `fish-audio.local.json` for real values.

## Provenance and limits

Compiled from the official SDKs: `fish-audio-sdk` 1.3.0 (PyPI, package `fishaudio`) and
`fish-audio` 0.1.0 (npm, `fishaudio/fish-audio-typescript`), read as source of truth.
`docs.fish.audio` was **not** reachable from the build environment (blocked by network egress
policy), so nothing here is taken from the prose documentation.

Not covered — verify against docs.fish.audio before relying on it: pricing and credit
consumption per request, rate limits, supported language codes, audio input format/length
limits, voice-training latency and quotas, availability of `s1` vs `s2-pro` per plan,
the agent/realtime-conversation product (`@fishaudio/agent-client`).
