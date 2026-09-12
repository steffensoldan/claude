# Python SDK (`fish-audio-sdk` 1.3.0, package `fishaudio`)

```bash
pip install fish-audio-sdk            # core
pip install "fish-audio-sdk[utils]"   # + play()/stream() helpers
```

## Clients

```python
from fishaudio import FishAudio, AsyncFishAudio

client = FishAudio(api_key=None, base_url="https://api.fish.audio")  # api_key falls back to $FISH_API_KEY
```

Missing key → `ValueError` at construction. Both clients are context managers
(`with FishAudio() as client:` / `async with AsyncFishAudio() as client:`) and expose
`close()`. Namespaces: `client.tts`, `client.asr`, `client.voices`, `client.account`.
Async mirrors the sync API with `await` (and `async for` on streams).

`base_url` is the hook for proxies/self-hosted gateways.

## TTS

```python
client.tts.convert(*, text, reference_id=None, references=None, format=None,
                   latency=None, speed=None, config=TTSConfig(), model="s2-pro",
                   request_options=None) -> bytes

client.tts.stream(...)            # same signature -> AudioStream (iterable of bytes, .collect() -> bytes)

client.tts.stream_websocket(text_iterable, *, reference_id=None, references=None,
                            format=None, latency=None, speed=None, config=TTSConfig(),
                            model="s2-pro", ws_options=None)
```

Direct kwargs always override the matching `config` field. `speed=` rebuilds `prosody`
preserving `volume`. `stream_websocket` accepts an iterable/generator of `str`, `TextEvent`
or `FlushEvent` (async iterables for `AsyncFishAudio`); it sends `start`, then the events,
then `stop`, and yields audio chunks.

### `TTSConfig` (reusable; all optional)

| Field | Default | Range / values |
|---|---|---|
| `format` | `"mp3"` | `wav`, `pcm`, `mp3`, `opus` |
| `sample_rate` | `None` | Hz |
| `mp3_bitrate` | `128` | 64, 128, 192 |
| `opus_bitrate` | `32` | -1000, 24, 32, 48, 64 |
| `normalize` | `True` | |
| `chunk_length` | `200` | 100–300 |
| `latency` | `"balanced"` | `normal`, `balanced` |
| `reference_id` | `None` | voice-model id |
| `references` | `[]` | `list[ReferenceAudio]` |
| `prosody` | `None` | `Prosody(speed=0.5–2.0, volume=-20…20)` |
| `top_p` | `0.7` | 0.0–1.0 |
| `temperature` | `0.7` | 0.0–1.0 |
| `max_new_tokens` | `1024` | |
| `repetition_penalty` | `1.2` | |
| `min_chunk_length` | `50` | |
| `condition_on_previous_chunks` | `True` | |
| `early_stop_threshold` | `1.0` | |

`ReferenceAudio(audio: bytes, text: str)` — `text` must match the sample verbatim.

Models: `Literal["speech-1.5", "speech-1.6", "s1", "s2-pro"]`; `speech-1.5`/`speech-1.6`
trigger a `DeprecationWarning`.

## ASR

```python
client.asr.transcribe(*, audio: bytes, language=None, include_timestamps=True,
                      request_options=None) -> ASRResponse
```

`ASRResponse(text: str, duration: float /* ms */, segments: list[ASRSegment])`,
`ASRSegment(text: str, start: float /* s */, end: float)`.
`include_timestamps=False` maps to the wire flag `ignore_timestamps=True`.

## Voices

```python
client.voices.list(*, page_size=10, page_number=1, title=None, tags=None, self_only=False,
                   author_id=None, language=None, title_language=None,
                   sort_by="task_count") -> PaginatedResponse[Voice]   # .total, .items
client.voices.get(voice_id) -> Voice
client.voices.create(*, title, voices: list[bytes], description=None, texts=None, tags=None,
                     visibility=None, train_mode="fast", cover_image=None,
                     enhance_audio_quality=None) -> Voice
client.voices.update(voice_id, *, title=None, description=None, cover_image=None,
                     visibility=None, tags=None) -> None
client.voices.delete(voice_id) -> None
```

`Voice.id` maps the API's `_id`; `Voice.state` ∈ `created|training|trained|failed`;
`visibility` ∈ `public|unlist|private`.

## Account

```python
client.account.get_credits() -> Credits    # .credit is decimal.Decimal
client.account.get_package() -> Package    # .total, .balance, .finished_at
```

## Options

```python
from fishaudio.core import RequestOptions, WebSocketOptions

RequestOptions(timeout=None, max_retries=None, additional_headers=None,
               additional_query_params=None)
WebSocketOptions(keepalive_ping_timeout_seconds=None, keepalive_ping_interval_seconds=None,
                 max_message_size_bytes=None, queue_size=None)
```

Client default timeout: 240 s. For long realtime sessions raise
`keepalive_ping_timeout_seconds` (README example: 60.0).

## Utils

```python
from fishaudio.utils import play, save, stream
save(audio_or_chunks, "out.mp3")   # bytes or iterable of bytes
play(audio)                        # needs a system player (ffplay/afplay/…)
stream(chunk_iterator) -> bytes    # play while collecting
```

## Exceptions

```python
from fishaudio.exceptions import (FishAudioError, APIError, AuthenticationError,
                                  PermissionError, NotFoundError, RateLimitError,
                                  ServerError, WebSocketError, ValidationError,
                                  DependencyError)
```

`APIError(status, message, body)` is the parent of the HTTP-status classes;
`FishAudioError` is the root — catch it as the fallback.

## Legacy package

The same distribution still ships `fish_audio_sdk` (`Session`, `WebSocketSession`,
`TTSRequest`, `ReferenceAudio`, default backend `speech-1.5`). Frozen — no updates.
Migrate to `fishaudio`; the wire protocol is identical.
