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

## Gehostetes Whisper, OpenAI-kompatibel (Scaleway Generative APIs)

Fertiger Client: `openai_compatible.py`. Schneidet, fragt stückweise an,
eskaliert die Temperatur bei Kollaps und fügt zusammen.

```powershell
$env:SCW_SECRET_KEY = "<dein-key>"
python openai_compatible.py sitzung.wav `
    --base-url https://api.scaleway.ai/v1 `
    --model whisper-large-v3 `
    --out sitzung.txt --debug-log verworfen.log
```

Die drei Hebel, die eine gehostete API noch lässt:

| Hebel | Umsetzung |
|---|---|
| stückweise, kontextfreie Anfragen | 20-s-Stücke aus `chunker.py`, jede Anfrage einzeln |
| Temperatur-Fallback | bei Kollaps dasselbe Stück erneut mit 0.2, 0.4, 0.6 - das macht Whisper intern, über die API muss der Client es tun |
| Segment-Metriken | `response_format=verbose_json`: Segmente mit `compression_ratio > 2.4`, `avg_logprob < -1.0` oder `no_speech_prob > 0.6` fallen raus - genau Whispers eigene Schwellwerte |

Reihenfolge ist wesentlich: **erst neu anfragen, dann retten.** Umgekehrt
schließt die Faltung den Fallback kurz - `entscheidendendend` wird zu
`entscheidend` geglättet und sieht sauber aus, obwohl die restlichen 18
Sekunden des Stücks nie transkribiert wurden.

**`prompt` ist kein Ort für den Text des Vorgängerstücks.** Das Feld
konditioniert den Decoder und schleppt genau den Loop weiter, den die
Stückelung unterbricht. Nur für feste Fachbegriffe verwenden
(`--prompt "Promotionsordnung, Gleichstellungsbeauftragte, Drittmittel"`).

*Modellname und Endpunktpfad des Dienstes hier nicht verifiziert - die
Scaleway-Doku ist aus der Entwicklungsumgebung gesperrt. `--base-url` und
`--model` entsprechend der eigenen Konsole setzen.*

## Wenn kein fertiger Client passt: das Verfahren

Läuft Whisper als Dienst, sind `condition_on_previous_text`, VAD und
`repetition_penalty` nicht erreichbar. Dann muss die Segmentierung **vor** der
Anfrage passieren — und pausenbasiert schneiden hilft nicht, wenn niemand eine
Pause macht. `chunker.py` schneidet deshalb an der *relativ leisesten* Stelle
im Zielbereich: die gibt es immer.

```bash
# 1. Aufnahme in Stücke schneiden (Ziel 20 s, Suchfenster ±5 s, 0,5 s Überlapp)
python chunker.py sitzung.wav --out-dir chunks --target 20
python chunker.py sitzung.wav --plan-only      # nur den Schnittplan ansehen

# 2. jedes Stück als EIGENE Anfrage an den Dienst schicken
#    - kein Kontext, kein Prompt aus dem Vorgängerstück
#    - Sprache explizit setzen (de), nie Autodetect
# 3. Antworten prüfen und zusammenfügen
python loop_guard.py rohtext.txt > sitzung_bereinigt.txt
```

Warum das den Loop bricht:

| Maßnahme | Wirkung |
|---|---|
| Stücke von ~20 s | der Decoder kann sich nicht über Minuten verlaufen |
| Schnitt an der leisesten Stelle | es entsteht eine Kante, auch ohne Sprechpause |
| jede Anfrage einzeln, ohne Kontext | ein Loop kann nicht über Stückgrenzen wandern |
| 0,5 s Überlapp + `stitch()` | keine abgeschnittenen Wortanfänge, Doppelung am Nahtpunkt wird entfernt |
| `loop_guard` auf jede Antwort | was trotzdem kollabiert, wird gefaltet oder markiert |

`stitch(texts)` aus `chunker.py` fügt die Stücktexte zusammen und entfernt die
Wiederholung am Überlapp (Vergleich der letzten und ersten bis zu 12 Wörter).

## Dateien

| Datei | Zweck |
|---|---|
| `openai_compatible.py` | Client für gehostetes Whisper (Scaleway Generative APIs): Chunking, Temperatur-Fallback, Metrik-Filter, Zusammenfügen |
| `chunker.py` | Schneidet Aufnahmen an der leisesten Stelle, auch ohne Sprechpause; `stitch()` fügt die Texte zusammen |
| `loop_guard.py` | Erkennt degenerierte Segmente (n-Gram-Abdeckung, Type-Token-Ratio, **wortinterne** Wiederholung) und faltet sie; CLI als Nachfilter |
| `live_transcribe.py` | Live-Transkription mit lokalem faster-whisper: Segmentierung, Anti-Loop-Parameter, Loop-Guard |
| `test_pipeline.py` | Smoke-Test ohne Mikrofon, Modell oder GPU: Segmentierung, Zwangsschnitt, Entscheidungslogik, Chunker |

Erkannte Fehlerbilder (alle aus echten Ausgaben, alle im Selbsttest abgedeckt):

| Muster | Erkennung |
|---|---|
| `...und dann kam es dann...` ×25 | n-Gram-Abdeckung |
| `die Doktoranden, die Doktoranden, …` mit echtem Vorspann | Abdeckung + Faltung rettet `Also ich glaube die Doktoranden` |
| `50/50/50/50/…` | n-Gram-Abdeckung |
| `entscheidendendendend…` | **wortinterne** Periode (auf Wortebene unsichtbar), Reparatur zu `entscheidend` |
| `und das ist ja ganz entscheid, …` ×9 | Abdeckung 90 % |
| `Ähm. Ähm. Ähm. …` | Abdeckung, wird als unverständlich markiert |

```powershell
pip install faster-whisper sounddevice numpy

# 1. Eingabegeraet finden (Index der Owl notieren)
python live_transcribe.py --list-devices

# 2. Starten. Index einsetzen, keine spitzen Klammern -
#    "<" ist in PowerShell ein reservierter Operator.
python live_transcribe.py --device 3 --out sitzung.txt --debug-log verworfen.log

python loop_guard.py        # Selbsttest der Erkennung
```

Modell und Rechengeraet werden automatisch gewaehlt: mit CUDA-GPU `large-v3`,
ohne GPU `small` auf der CPU (`--model`, `--compute-device`, `--compute-type`
ueberschreiben das). Ohne GPU ist `large-v3` nicht echtzeitfaehig - die
Transkription laeuft der Aufnahme hinterher und reisst Luecken.

Verworfene Segmente erscheinen im Transkript als
`[unverständlich, 4.2s - Muster 'und dann kam es dann' deckt 94% des Segments]`
und im Debug-Log im Rohtext. Fehler sichtbar statt plausibel falsch.

### Nachfilter für eine bestehende Pipeline

Läuft die Live-Transkription über ein anderes Frontend, ist der Loop-Guard auch
allein verwendbar — Zeitstempel am Zeilenanfang bleiben erhalten:

```bash
python loop_guard.py sitzung.txt > sitzung_bereinigt.txt
<irgendein-live-tool> | python loop_guard.py --stdin
```

```
[00:01:09] Also, ich glaube, die Doktoranden, die Doktoranden, die Doktoranden, ...
   ->      Also ich glaube die Doktoranden
```

Zeilen mit echtem Vorspann werden auf den Inhalt gefaltet, vollständig
halluzinierte Zeilen als `[unverständlich: …]` markiert. Die Faltung greift nur
bei Zeilen, die zuvor als degeneriert erkannt wurden — Sätze mit legitimer
Doppelung („sehr sehr wichtig") passieren den Filter unverändert.

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
