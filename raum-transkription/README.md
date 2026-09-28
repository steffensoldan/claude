# Raum-Transkription (Live, Whisper, Meeting Owl)

Gegenmaßnahmen gegen den Whisper-Degenerations-Loop bei Raumaufnahmen mit
mehreren, gleichzeitig sprechenden Personen.

## Symptom

```
[00:01:50] ...und dann kam es dann... ...und dann kam es dann... ...und dann kam es dann...
```

Kein Inhalt, sondern ein Dekodierungs-Kollaps: der autoregressive Decoder
bekommt informationsarmes Audio und füllt das Zeitfenster mit einem Fragment.
Auslöser, in dieser Reihenfolge wirksam:

| # | Auslöser | Mechanismus |
|---|---|---|
| 1 | mehrere Sprecher gleichzeitig auf einem Mischkanal | kein dominanter Signalpfad, nichts Dekodierbares |
| 2 | Distanz und Hall (360°-Mikro auf dem Tisch) | SNR unter Schwelle |
| 3 | AGC des Konferenzmikros | zieht in Pausen den Raumnoise hoch → Whisper transkribiert Rauschen |
| 4 | festes Zeitfenster statt Segmentierung an Sprechpausen | Modell muss auch über Stille dekodieren |
| 5 | Kontextübergabe zwischen Fenstern | ein begonnener Loop pflanzt sich fort |
| 6 | `language` nicht gesetzt | Autodetect auf Gemurmel verstärkt Halluzination |

## Was die Owl kann und was nicht

Die Meeting Owl liefert **einen gemischten Monokanal** über USB. Beamforming und
Sprecherwechsel passieren geräteintern; nach außen kommt eine Spur. Konsequenz:

- **Nicht lösbar in Software:** Sprechertrennung bei Überlappung, Sprecherlabels
  („wer sagt was"). Beides braucht getrennte Kanäle — Lavalier/Headset pro
  Person, oder ein Array, das Rohkanäle herausgibt.
- **Lösbar:** Halluzinationen aus Stille und Rauschen, Loops über
  Segmentgrenzen, Übernahme von Müll ins Protokoll. Dafür dieses Verzeichnis.

*Herstellerangaben zur Reichweite je Owl-Modell nicht geprüft — für die
Diagnose unerheblich, für die Raumaufstellung relevant.*

## Dateien

| Datei | Zweck |
|---|---|
| `live_transcribe.py` | Live-Transkription: Pausensegmentierung, Anti-Loop-Parameter, Loop-Guard |
| `loop_guard.py` | Erkennung degenerierter Segmente (n-Gram-Abdeckung, Type-Token-Ratio) + Faltung |

```bash
pip install faster-whisper sounddevice numpy

python live_transcribe.py --list-devices
python live_transcribe.py --device <owl-index> --model large-v3 \
    --out sitzung.txt --debug-log verworfen.log
python loop_guard.py        # Selbsttest der Erkennung
```

Verworfene Segmente erscheinen im Transkript als
`[unverständlich, 4.2s - Muster 'und dann kam es dann' deckt 94% des Segments]`
und im Debug-Log im Rohtext. Fehler sichtbar statt plausibel falsch.

## Die wirksamen Parameter (faster-whisper)

Geprüft gegen `faster_whisper.transcribe.WhisperModel.transcribe()` und
`faster_whisper.vad.VadOptions`.

| Parameter | Default | Hier | Wirkung |
|---|---|---|---|
| `condition_on_previous_text` | `True` | **`False`** | stärkster Einzelschalter: Loop kann nicht über Segmente wandern |
| `language` | `None` | `"de"` | kein Autodetect auf Gemurmel |
| `temperature` | `[0.0 … 1.0]` | unverändert | Fallback-Kette; bei Kollaps wird neu dekodiert |
| `compression_ratio_threshold` | `2.4` | unverändert | verwirft repetitive Dekodierungen |
| `log_prob_threshold` | `-1.0` | unverändert | verwirft unsichere Segmente |
| `no_speech_threshold` | `0.6` | unverändert | erkennt Nichtsprache |
| `hallucination_silence_threshold` | `None` | `2.0` | überspringt Stille-Passagen |
| `repetition_penalty` | `1` | `1.1` | dämpft Wiederholung ohne echte Rede zu verstümmeln |
| `no_repeat_ngram_size` | `0` | `0` (`3` via `--aggressive`) | hart wirksam, blockt aber auch legitime Wiederholungen |
| `vad_filter` | `False` | `True` | Silero-VAD im Modell, zweite Stufe nach der eigenen Segmentierung |
| `vad_parameters` | — | `min_silence_duration_ms=500`, `speech_pad_ms=200` | Schnitt an Pausen, Anlaut nicht abschneiden |

`whisper.cpp`-Äquivalente, falls die Live-Kette darauf läuft: `-kc/--keep-context`
**nicht** setzen (dort standardmäßig aus — entspricht
`condition_on_previous_text=False`), `-l de`, `-vth` (VAD-Schwelle, Default 0.6),
`-fth` (Hochpass, Default 100 Hz), `--step`/`--length`/`--keep` für das
Schiebefenster; `-nf` schaltet den Temperatur-Fallback ab — also **nicht** setzen.

## Betrieb im Raum (wirkt stärker als jeder Parameter)

1. Moderationsdisziplin: einer spricht. Überlappung ist die Ursache Nr. 1 und
   entsteht vor dem Mikrofon.
2. Owl zentral, Abstand zu Sprechenden möglichst ≤ 1 m; bei Tischrunden > 2 m
   zusätzliche Mikrofone.
3. Harte Flächen dämpfen (Vorhang, besetzte Stühle, Whiteboard nicht als
   Reflektor hinter der Runde).
4. Für protokollpflichtige Sitzungen: Headset/Lavalier für die Hauptsprechenden,
   Owl nur für Bild und Raumatmosphäre.
5. Fachvokabular über `initial_prompt` vorgeben (Gremien-, Programm-, Projektnamen)
   — reduziert falsche Wortwahl, nicht die Loops.

## Sprecherzuordnung (wenn nötig)

Whisper liefert keine Sprecherlabels. Ketten mit Diarisierung: WhisperX oder
pyannote.audio lokal; als Dienst Deepgram oder AssemblyAI mit
Diarisierungs-Flag. *Feature- und Preisstände nicht geprüft.* Auf einem
gemischten Monokanal bleibt die Diarisierung auch dort unzuverlässig, sobald
Sprecher überlappen — die Trennung muss bei der Aufnahme passieren.
