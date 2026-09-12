# Fish Audio HTTP/WS API reference

Base URL `https://api.fish.audio`. Every request: `Authorization: Bearer $FISH_API_KEY`.
Derived from the official SDK sources (`fish-audio-sdk` 1.3.0, `fish-audio` 0.1.0).

## POST /v1/tts — text to speech

Headers: `Content-Type: application/msgpack`, `model: s2-pro | s1 | speech-1.6 | speech-1.5`.
Response: raw audio byte stream (chunked), content type per `format`.

Body (msgpack map, omit null fields):

| Field | Type | Default | Notes |
|---|---|---|---|
| `text` | str | — | required |
| `reference_id` | str | null | voice-model id (32-hex, e.g. `802e3bc2b27e49c2995d23ef70e6ac89`) |
| `references` | list | `[]` | instant cloning: `{audio: bytes, text: str}` per item |
| `format` | str | `mp3` | `wav`, `pcm`, `mp3`, `opus` |
| `sample_rate` | int | null | format default when null |
| `mp3_bitrate` | int | 128 | 64, 128, 192 |
| `opus_bitrate` | int | 32 | -1000, 24, 32, 48, 64 |
| `latency` | str | `balanced` | `normal` = higher quality |
| `chunk_length` | int | 200 | 100–300 |
| `normalize` | bool | true | text normalization |
| `prosody` | map | null | `{speed: 0.5–2.0, volume: -20…20}` |
| `top_p` | float | 0.7 | 0.0–1.0 |
| `temperature` | float | 0.7 | 0.0–1.0 |
| `max_new_tokens` | int | 1024 | |
| `repetition_penalty` | float | 1.2 | |
| `min_chunk_length` | int | 50 | |
| `condition_on_previous_chunks` | bool | true | continuity across chunks |
| `early_stop_threshold` | float | 1.0 | |

`reference_id` and `references` are alternative ways to pick the voice; a stored model id is
cheaper per request than re-uploading reference audio.

## WSS /v1/tts/live — realtime TTS

Same auth header; same `model:` header. All frames are msgpack **binary** frames.

Client → server events:

| `event` | Payload | Purpose |
|---|---|---|
| `start` | `{event: "start", request: <TTS body>}` | opens the session; `request` is the /v1/tts body (text may be empty) |
| `text` | `{event: "text", text: "..."}` | append a text chunk |
| `flush` | `{event: "flush"}` | force synthesis of buffered text |
| `stop` | `{event: "stop"}` | end the session |

Server → client events: `{event: "audio", audio: bytes}` for each chunk;
`{event: "finish", reason: "stop"}` on clean completion; `{event: "finish", reason: "error"}`
on failure (treat as an exception). Unknown events should be ignored, not fatal.

## POST /v1/asr — speech to text

Headers: `Content-Type: application/msgpack`. Body: `{audio: bytes, ignore_timestamps: bool,
language?: str}`. Note the inverted flag: `ignore_timestamps: false` returns segments.

Response JSON:

```json
{"text": "full transcript",
 "duration": 12345.0,
 "segments": [{"text": "...", "start": 0.0, "end": 1.42}]}
```

`duration` is milliseconds; `start`/`end` are seconds. `segments` is empty when timestamps
are suppressed. `language` is auto-detected when omitted.

## Voice models

### GET /model — list/search
Query params: `page_size` (10), `page_number` (1), `title`, `tag` (repeatable), `self` (bool,
own models only), `author_id`, `language`, `title_language`, `sort_by` (`task_count` |
`created_at`). Response: `{total: int, items: [Voice]}`.

### GET /model/{id} — single model
Response: `Voice` object:
`_id`, `type` (`tts` | `svc`), `title`, `description`, `cover_image`, `train_mode` (`fast`),
`state` (`created` | `training` | `trained` | `failed`), `tags[]`,
`samples[] {title, text, task_id, audio}`, `created_at`, `updated_at`, `languages[]`,
`visibility` (`public` | `unlist` | `private`), `lock_visibility`, `like_count`, `mark_count`,
`shared_count`, `task_count`, `liked`, `marked`, `author {_id, nickname, avatar}`.

### POST /model — create (voice cloning)
`multipart/form-data`. Files: one `voices` part per audio sample, optional `cover_image`.
Form fields: `title` (required), `type=tts`, `train_mode=fast`, `description`, `texts` (per
sample transcripts), `tags`, `visibility`, `enhance_audio_quality`. Response: `Voice`.
Poll `state` until `trained` before relying on the model.

### PATCH /model/{id} — update metadata
`multipart/form-data` with any of `title`, `description`, `visibility`, `tags`, `cover_image`.
No response body.

### DELETE /model/{id}
No response body.

## Account

- `GET /wallet/self/api-credit` → `{_id, user_id, credit, created_at, updated_at, has_phone_sha256?, has_free_credit?}` (`credit` is decimal — parse as decimal, not float, for accounting).
- `GET /wallet/self/package` → `{_id, user_id, type, total, balance, created_at, updated_at, finished_at?}`.

## Errors

| Status | SDK exception | Handling |
|---|---|---|
| 401 | `AuthenticationError` | key missing/invalid — do not retry |
| 403 | `PermissionError` | key lacks access to the resource |
| 404 | `NotFoundError` | wrong model/voice id |
| 429 | `RateLimitError` | back off, retry |
| ≥500 | `ServerError` | retry with backoff |
| other non-2xx | `APIError` | inspect `.message` / `.body` |

Error bodies carry `message` or `detail`. Websocket failures raise `WebSocketError`;
client-side argument problems raise `ValidationError`; missing optional system dependencies
(audio players) raise `DependencyError`.

## Raw call without the SDK (Python, msgpack)

```python
import ormsgpack, httpx

body = {"text": "Hallo Welt", "format": "mp3", "latency": "balanced"}
r = httpx.post(
    "https://api.fish.audio/v1/tts",
    headers={"Authorization": f"Bearer {KEY}",
             "Content-Type": "application/msgpack",
             "model": "s2-pro"},
    content=ormsgpack.packb(body), timeout=240.0)
r.raise_for_status()
open("out.mp3", "wb").write(r.content)
```

Default SDK timeout is 240 s — long generations need a comparably generous client timeout.
