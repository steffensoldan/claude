# Testbericht Chorspur

Stand: 2026-10-17. Geprüft wurde `chorspur.html` mit `test/test.mjs` (Playwright 1.56.1, Chromium 1194 headless, Linux).
Aufruf: `python3 -m http.server 8765` im Ordner `chorspur`, dann `node test/test.mjs http://localhost:8765/chorspur.html <Ausgabeordner>`.

## Umsetzung (Abweichung von der Vorlage)
- Aufnahme nicht mehr per `MediaRecorder`, sondern als Rohdaten über ein AudioWorklet (Fallback ScriptProcessor). Jeder Block trägt die Frame-Nummer der Audio-Uhr. Der Schnitt auf Taktbeginn T0 liegt damit samplegenau; es bleibt nur die Gerätelatenz, die „Latenz (ms)“ ausgleicht.
- Export: `OfflineAudioContext` → WAV 16 Bit Stereo → `<a download>`. Muted Spuren und Rhythmus sind nicht im Export (wie zuvor). Ist der Mix übersteuert (>0 dBFS), wird er automatisch leiser gestellt und das gemeldet.
- Latenz-Messung: 5 Klicks über Lautsprecher, Mikrofonaufnahme, Kreuzkorrelation (Median, Streuung wird angezeigt). Wert wird in `localStorage` gemerkt.
- Wake Lock bei Aufnahme/Wiedergabe/Messung, Fehler werden ignoriert. Hinweis „Kopfhörer verwenden“ während der Aufnahme. Pegel mit Übersteuerungswarnung ab Spitze ≥ 0,98 (≈ −0,2 dBFS), Spitzenpegel nach jeder Aufnahme.
- Fehlermeldungen (Deutsch) für: verweigert, kein Mikro, Mikro belegt, unsicherer Kontext, Worklet-Fehler. Datei-Import bleibt als Rückfall.
- Tempo/Tonhöhe weiterhin über `playbackRate` gekoppelt, im Hilfetext benannt.

## Messwerte

### 1. Aufnahmepfad (Chromium-Fake-Mikrofon, `--use-fake-device-for-media-stream --use-fake-ui-for-media-stream`)
| Größe | Wert |
|---|---|
| Aufnahmedauer (dekodiert) | 3,237 s (> 1 s) |
| Erwartet (Stoppzeit − T0, Einzählen ausgeschlossen) | 3,213 s |
| Kanäle / Samplerate | 1 / 44100 Hz |
| Spitze / RMS | 1,0 / 0,147 (nicht stumm) |
| Seitenfehler | keine |

Mit Einzählphase wären es ca. 6 s; die Aufnahme beginnt also erst bei T0. Die +23 ms Differenz ist die Reaktionszeit zwischen Messung der Stoppzeit und Klick.

### 2. Timing – **simulierte Schleife, kein echtes Gerät**
Aufbau: Das „Mikrofon“ ist der eigene Ausgang der Seite, 80 ms verzögert und als MediaStream zurückgespeist. Rhythmus „Klick“, 90 BPM, 7 Klicks je Aufnahme, Abweichung per Kreuzkorrelation gegen die Taktposition.
| Fall | Abweichung |
|---|---|
| Latenz 0 ms | +101,6 ms (alle 7 Klicks) |
| Kalibrierung misst | 102 ms, Streuung 0,0 ms, 5/5 Klicks |
| Spur 1 mit 102 ms | −0,05 bis −0,39 ms |
| Spur 2 (Overdub über Spur 1) mit 102 ms | 0 bis −0,50 ms |

Ergebnis: Messkette, Schnitt und Korrektur arbeiten rechnerisch auf unter 1 ms (Kriterium < 20 ms erfüllt **für die Simulation**). Die 102 statt 80 ms entstehen in der MediaStream-Kette des Browsers. Aussagekraft für ein echtes Handy: **keine**. Dort kommen Eingangs-/Ausgangslatenz des Geräts, Bluetooth und das menschliche Vorhalten hinzu; das ist offen (Punkt 4/5).

### 3. Export
`ffprobe` auf `Chorspur-Mix.wav` (Mix aus zwei Spuren):
- Codec `pcm_s16le`, 2 Kanäle, 44100 Hz, 16 Bit, Container wav
- Dauer 5,640522 s; erwartet (längste Spur + 0,3 s) 5,640521 s
- Dateigröße 995 032 Byte
Nur mit `ffprobe` geprüft, nicht in Audacity.

### 4. Handy
**Nicht geprüft.** Weder Chrome Android noch Safari iOS wurden getestet. Alle Werte oben stammen vom Desktop-Chromium (headless). Muss Steffen mit Kopfhörern machen: Spur 1 aufnehmen, Spur 2 darüber, Export anhören; Ergebnis hier eintragen:
- Gerät / Browser: _offen_
- Ergebnis (geht / geht nicht): _offen_

### 5. Hörprobe (blind, zwei Spuren auf Gleichlauf)
**Nicht durchgeführt.**

## Erweiterung 2026-10-17: visueller Taktgeber und Notenanzeige
- **Taktgeber:** vier große Felder (Schlag 1 umrandet), Einzählen rot. Neue Option „Einzählen: Klick / Nur sichtbar“; mit Rhythmus „Aus“ läuft die Aufnahme komplett ohne Ton. Auswahl wird im Browser gemerkt.
- Anzeige, Playhead und Noten folgen der *hörbaren* Zeit (`getOutputTimestamp`, Fallback `outputLatency`), damit Bild und Kopfhörer zusammenpassen und die Latenzkorrektur gültig bleibt.
- **Noten:** MusicXML (.musicxml/.xml/.mxl) über OpenSheetMusicDisplay 1.9.9 (jsDelivr, feste Version, erst beim Laden einer Notendatei nachgeladen). Cursor läuft im eingestellten Tempo (Viertel = Schlag), Stimmen per Häkchen ein-/ausblendbar, „Noten-Start (Schläge)“ für Auftakt/Versatz.
- **Gemessen** (`test/score-test.mjs`, headless Chromium, Testsatz 2 Stimmen × 2 Takte): 8 Cursorschritte erkannt; Ausblenden einer Stimme wirkt; bei 90 BPM stimmt der Cursorindex in 11 von 12 Stichproben mit dem Schlag aus der Audio-Uhr überein, die Abweichung (0,70 s ≈ Schlag 1,05) liegt in der Ausgabelatenz, um die die Anzeige bewusst verzögert ist. Keine Seitenfehler. Regressionstest (`test/test.mjs`) erneut bestanden: Werte wie oben.
- **Grenzen:** Taktart der Noten wird nicht übernommen (Raster immer 4/4; bei 3/4 o. ä. laufen Noten korrekt im Viertel-Tempo, nur die Taktstriche der Zeitleiste passen nicht). Tempoangaben und Tempowechsel in der Partitur werden ignoriert; es gilt der Tempo-Regler. Wiederholungen folgt der Cursor so, wie OSMD sie auflöst (nicht geprüft). Am iPhone nicht geprüft; ob .musicxml-Dateien in der iOS-Dateiauswahl wählbar sind, ist offen.

## Offene Punkte / Risiken (nicht gemessen)
- iOS Safari: Samplerate-Wechsel und Ausgabepegel nach Mikrofon-Freigabe sind bekannte Fallstricke; Verhalten unbekannt. AudioContext wird im Klick gestartet, danach nach der Freigabe erneut `resume()`.
- Bluetooth-Kopfhörer: Latenz hoch und schwankend; Kalibrierung über Lautsprecher bildet diesen Pfad nicht ab. Dann Wert per Gehör nachstellen.
- Der Kalibriertest braucht Lautsprecher plus Mikrofon ohne Kopfhörer; der Wert gilt dann für den Lautsprecherweg.
- Latenz gilt nur für neue Aufnahmen. Bestehende Takes lassen sich über „Start“ in der Feinabstimmung nachschieben.
- Schriften kommen weiter von Google Fonts (Fallback vorhanden). Audiodaten werden nicht übertragen. Für ZEW-Kontext ggf. Schriften lokal einbetten.
- Letzte <1024 Samples (ca. 23 ms) am Ende einer Aufnahme gehen verloren (Worklet-Blockgröße).
- Bereitstellung (HTTPS) noch nicht umgesetzt, siehe unten.

## Am Handy öffnen (5 Zeilen)
1. Seite per HTTPS bereitstellen (Vorschlag: GitHub Pages; öffentliches Repo erst nach Freigabe durch Steffen, ZEW-Kontext).
2. Link am Handy in Chrome (Android) oder Safari (iOS) öffnen.
3. Kopfhörer anstecken, bei „Aufnahme“ das Mikrofon erlauben.
4. Optional: „Latenz messen“ (ohne Kopfhörer), dann Stimme 1 aufnehmen, Stimme 2 darüber.
5. „Mix speichern“ lädt `Chorspur-Mix.wav` herunter.
Am Desktop zum Testen: `python3 -m http.server 8765` im Ordner, dann `http://localhost:8765/chorspur.html`.
