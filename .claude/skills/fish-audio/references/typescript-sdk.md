# TypeScript SDK (`fish-audio` 0.1.0, fishaudio/fish-audio-typescript)

```bash
npm install fish-audio
```

```typescript
import { FishAudioClient } from "fish-audio";

const fishAudio = new FishAudioClient();                       // reads FISH_API_KEY
// or: new FishAudioClient({ apiKey: "...", baseUrl: "https://your-proxy-domain" })
```

Namespaces differ from the Python SDK: `textToSpeech`, `speechToText`, `voices`, `user`.

## TTS

```typescript
import { FishAudioClient, play } from "fish-audio";
import type { TTSRequest, ReferenceAudio } from "fish-audio";

const audio = await fishAudio.textToSpeech.convert({ text: "Hello, world!" }); // backend "s2-pro"
await play(audio);

// stored voice
const req: TTSRequest = { text: "Hello", reference_id: "your_model_id" };

// instant cloning
const referenceAudio: ReferenceAudio = { audio: new File([buf], "ref.wav"), text: "reference transcript" };
const req2: TTSRequest = { text: "Hello", references: [referenceAudio] };
```

## Realtime TTS (websocket)

```typescript
import { FishAudioClient, RealtimeEvents } from "fish-audio";

async function* makeTextStream() { yield "Hello "; yield "from Fish Audio!"; }

const connection = await client.textToSpeech.convertRealtime(
  { text: "", reference_id: "your_model_id" },   // text MUST be "" in realtime mode
  makeTextStream()
);

connection.on(RealtimeEvents.OPEN, () => {});
connection.on(RealtimeEvents.AUDIO_CHUNK, (audio) => { /* Uint8Array/Buffer */ });
connection.on(RealtimeEvents.ERROR, (err) => {});
connection.on(RealtimeEvents.CLOSE, () => { /* flush collected chunks to disk */ });
```

## ASR

```typescript
const result = await fishAudio.speechToText.convert({ audio: createReadStream(path) });
result.text; result.duration; result.segments;
```

## Voices and user

```typescript
await fishAudio.voices.ivc.create({ title, voices: [audioStream], cover_image: imgStream });
await fishAudio.voices.search();
await fishAudio.voices.get("your_model_id");
await fishAudio.voices.update("your_model_id", { title: "new_title" });
await fishAudio.voices.delete("your_model_id");
await fishAudio.user.get_api_credit();
```

Created voices are returned with `_id` (not `id`) — use `_id` as `reference_id`.

Caveat: the TS SDK is at 0.1.0 and its surface is less settled than the Python SDK's
(the README also lists `fishAudio.voices.get_package()` for the package endpoint, which
looks like a doc slip for a user-level call — verify at runtime before depending on it).
