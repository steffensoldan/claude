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

## Erweiterung 2: Ganzbild-Taktsignal, Beispielsatz
- **Taktsignal über den ganzen Bildschirm:** Rahmen um den Bildschirm blinkt auf jedem Schlag (Schlag 1 breiter, Einzählen rot), dazu eine feste Leiste unten mit den vier Schlagfeldern, Takt/Schlag und „Stopp“; bleibt beim Scrollen zu den Noten sichtbar. Gemessen: Rahmen-Status „on“ und Leiste sichtbar während der Wiedergabe (Screenshot, Chromium 390 px breit).
- **Beispielsatz** `noten/alle-meine-entchen.musicxml`: Volkslied, F-Dur, 4/4, 10 Takte, Sopran mit Text, Alt/Tenor/Bass als einfacher eigener Satz (I–IV–V7, ganze Noten). Gemessen: 4 Stimmen erkannt und alle sichtbar, 27 Cursorschritte, Cursor folgt dem Schlag. Notenhöhenumfang S F4–D5, A C4–F4, T A3–C4, B F2–F3. Satz nicht von einer Chorleitung geprüft.
- Regressionstest erneut bestanden (Aufnahme 3,24 s; Kalibrierung 102 ms; Abweichung ≤ 0,5 ms; WAV-Dauer = Erwartung).

## Umbau 3 (Wunsch Steffen): 8 Spuren, Noten pro Spur, ohne Beat/Pan/Latenz
- 8 Aufnahmespuren (eigene Farben 5–8). Rhythmus nur noch „Aus/Klick“, Pan entfernt (Mix mittig), **Latenz-Einstellung und -Messung entfernt**.
- Noten pro Spur: Nach dem Laden einer MusicXML-Datei bekommt Spur k automatisch Notenstimme k (bis zur Zahl der Notenstimmen), Spuren darüber hinaus „keine Noten“ (Percussion/Impro). Zuordnung je Spur per Auswahlfeld änderbar. Beim Start einer Aufnahme scrollt die Seite zur Spur.
- **Gemessen** (`test/score-test.mjs`, Entchen-Satz, 390 px): 8 Spuren; keine Pan-Regler, keine Latenz-Bedienung; Stimmen Sopran/Alt/Tenor/Bass auf Spur 1–4, jede Ansicht zeigt genau ihre Stimme; Spur 5 umstellbar; Cursor pro Ansicht synchron zum Schlag (Sopran in Vierteln, Unterstimmen in Ganzen). Fehler gefunden und behoben: Cursor der Unterstimmen sprang zu weit, weil OSMD Stellen ohne neue Note in der sichtbaren Stimme überspringt; jetzt eigene Zeitliste je Ansicht.
- **Regression** (`test/test.mjs`, simulierte Schleife 80 ms): Aufnahme 3,24 s ohne Einzählen; Spur 1 und 2 liegen je **+102 ms hinter dem Raster** (keine Korrektur mehr), zueinander −0,3 ms; WAV 16 Bit Stereo, Dauer = Erwartung (5,742517 s).
- **Folge der entfernten Latenzkorrektur (nicht real gemessen):** Jede Aufnahme liegt um die Geräte-Rundlaufzeit zu spät. Folgen alle Sänger dem *Bildsignal*, sind alle Spuren gleich verschoben und laufen zueinander synchron. Folgt jemand den *vorher aufgenommenen Spuren*, addiert sich die Verzögerung pro Schicht. Abhilfe: „Feinabstimmung → Start“ ins Minus.

## Erweiterung 4: Projekt speichern / öffnen
- „Projekt speichern“ lädt eine ZIP-Datei herunter: `projekt.json` (Tempo, Rhythmus, Einzählen, Noten-Start, je Spur Lautstärke/Stumm/Start/Tempo/Tonhöhe/Notenzuordnung), `spur1.wav` … (nur belegte Spuren, mono 16 Bit) und die Notendatei. „Projekt öffnen“ stellt alles wieder her; danach kann normal weiter aufgenommen werden. Die Spuren sind auch einzeln in anderen Programmen nutzbar.
- **Gemessen** (`test/proj-test.mjs`): 2 Spuren + 8-stimmige Noten + geänderte Einstellungen gespeichert; `unzip -l` zeigt 4 Dateien; `spur1.wav` laut ffprobe pcm_s16le, mono, 44100 Hz, 3,04 s. Nach Neuladen der Seite und Öffnen: alle 8 Spuren mit gleicher Länge, Lautstärke, Stumm, Start und Notenzuordnung wie vorher (inkl. abgewählter Spur 6), Tempo 100 wiederhergestellt; Audio weicht nur durch 16-Bit-Rundung ab (0,05 % der Summe). Danach Spur 3 aufgenommen (3,04 s) und Mix exportiert (Stereo, 3,34 s = Erwartung). Keine Seitenfehler. Regression (`test/test.mjs`) bestanden.
- **Nicht geprüft:** iPhone (Download und Auswahl der .zip in „Dateien“). Wird die ZIP in „Dateien“ entpackt, bitte die ursprüngliche .zip wählen, nicht den Ordner. Neu gepackte ZIPs (Deflate) werden gelesen, wenn der Browser `DecompressionStream` kann (nicht geprüft).

## Erweiterung 5: Einsätze auf den Schlag ausrichten
- Pro Spur („Feinabstimmung → Einsatz auf den Schlag ausrichten“) oder für alle Spuren („Alle Einsätze auf den Schlag ausrichten“). Erkennung des ersten Einsatzes über den Pegelverlauf (10-ms-Fenster, Schwelle 15 % des Maximums, zurück bis 40 % der Schwelle); Verschiebung über „Start“ auf den nächsten Schlag, mit Vorhalt für Verspätung (bis ¾ Schlag nach einem Schlag zählt zu diesem Schlag).
- **Gemessen** (`test/test.mjs`): zwei Spuren in der simulierten Schleife, je +101,6 ms zu spät → nach „Alle ausrichten“ −0,05 ms auf allen 7 Schlägen. Stimmähnlicher Ton mit 60 ms weichem Anstieg, Einsatz bei 0,95 s → auf Schlag 2 (0,667 s) gelegt, Restfehler −3,4 ms.
- **Grenzen (nicht real gemessen):** Ausgerichtet wird nur der *erste* Einsatz; Tempoabweichungen innerhalb der Spur bleiben. Atemgeräusch, Räuspern oder Übersprechen vor dem Einsatz können als Einsatz erkannt werden. Bei sehr weichen Einsätzen (summen, „m“) kann der erkannte Punkt einige zehn Millisekunden später liegen. Ein Auftakt auf „und“ landet auf dem nächsten ganzen Schlag; dann per „Start“ nachstellen.

## Erweiterung 6: Anfangston beim Einzählen
- Auswahl „Anfangston“ (aus, C … H, eine Oktave C4–H4, deutsche Tonnamen, B = B♭, H = B♮), Knopf „♪ Anhören“. Der Ton (Orgelklang: Grundton + Oktave + Duodezime) klingt während des Einzählens und endet 0,45 Schlag vor Schlag 1. Gespeichert im Browser und in der Projektdatei.
- **Gemessen** (`test/ref-test.mjs`): 13 Optionen; mit „A“ liegt die stärkste Frequenz am Ausgang während des Einzählens bei 431 Hz (Analyser-Auflösung 86 Hz, also passend zu 440 Hz); in der Aufnahme (simulierte Schleife, Rhythmus aus) Spitzenpegel 0, der Ton gelangt also nicht in die Spur. Regression (`test/test.mjs`) bestanden.
- **Nicht geprüft:** Lautstärke und Klang am iPhone-Kopfhörer.

## Umbau 7 (nach Rückfragen): ohne Rhythmus/Klick, Rahmen nur beim Einzählen, Loop pro Spur
- Entfernt: Rhythmus-Auswahl und alle Klicks. Eine Zeile „Einzählen: 4 Schläge / aus“ + „Ton –/C…H“ + „♪“. Einzählen ist rein sichtbar; „aus“ startet die Aufnahme sofort (0,25 s Vorlauf), dann ohne Anfangston.
- Bildschirmrahmen blinkt nur noch beim Einzählen; untere Leiste bleibt bei Wiedergabe und Aufnahme.
- Loop pro Spur: „aus / 1 / 2 / 4 / 8 Takte“. Wiederholt Takt 1 bis x der Spur (inkl. „Start“-Verschiebung) endlos bis Stopp; Rest der Aufnahme wird ignoriert. Zeitleiste zeigt die Wiederholungen blasser. Mix speichern fragt bei Loops nach der Länge in Takten (Vorgabe: längste Nicht-Loop-Spur, sonst 4 × längster Loop). Loop wird im Projekt gespeichert.
- **Gemessen** (`test/loop-test.mjs`): 1-Takt-Datei mit Klick am Taktanfang und Störimpuls nach dem Takt, Loop 1 → Wiedergabe läuft nach 5 s weiter; Rahmen während Wiedergabe immer aus, beim Einzählen „on cnt“, danach aus; Export 3 Takte = 8,000 s (90 BPM), Klicks bei 0 / 2,667 / 5,333 s, Störimpuls nicht im Mix. `proj-test`: Loop 2 wird gespeichert und wiederhergestellt, Export-Vorgabe 2 Takte → 4,8 s bei 100 BPM. Regression `test.mjs` (Klicks jetzt vom Test eingespeist), `score-test`, `ref-test` bestanden.
- **Gefundener und behobener Fehler:** Die Notenzuordnung füllte nach Einbau des Loop-Felds das falsche Auswahlfeld; behoben, durch `score-test`/`proj-test` aufgedeckt.
- **Grenzen:** Tempo/Tonhöhe einer Loop-Spur während der Wiedergabe zu ändern, wirkt erst beim nächsten Start sauber. Loop-Länge in Takten richtet sich nach dem eingestellten Tempo; wurde die Spur in einem anderen Tempo aufgenommen, passt der Ausschnitt nicht.

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
