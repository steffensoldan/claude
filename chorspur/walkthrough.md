# Dokumentation & Walkthrough: Chorspur

Zusammenfassung der Änderungen von der claude.ai-Artifact-Fassung (4 Spuren, ohne funktionierende Aufnahme) bis zum Stand `0ec3c83` (8 Spuren, Noten, Loop). Messwerte im Detail: `TESTBERICHT.md`.

---

## 1. Durchgeführte Änderungen

### Commits (Branch `claude/chorspur-aufnahme`, chronologisch)
| Commit | Inhalt |
|---|---|
| `f06d298` | Aufnahme per AudioWorklet, WAV-Export, Latenzkorrektur, Tests |
| `2c6f18b` | `.nojekyll` (Vorbereitung GitHub Pages, nicht aktiviert) |
| `22f84f6` | Visueller Taktgeber, stilles Einzählen, Notenanzeige (MusicXML) mit Cursor |
| `c27e81f` | Taktsignal als Bildschirmrahmen und feste Leiste; Beispielsatz „Alle meine Entchen“ |
| `6ade1db` | 8 Spuren, Noten je Spur; Beat, Pan, Latenz entfernt |
| `beee72f` | Entchen-Satz mit 8 Notenstimmen |
| `8a69379` | Projekt speichern/öffnen (ZIP) |
| `83966b1` | Beispielsatz Na-na-Vamp |
| `640e291` | Einsätze auf den Schlag ausrichten |
| `b11ab5a` | Anfangston beim Einzählen |
| `0ec3c83` | Rhythmus/Klick entfernt, Einzählen + Ton in einer Zeile, Rahmen nur beim Einzählen, Loop pro Spur |

### Dateien
* **[NEW]** `chorspur/chorspur.html`: aus der eingefügten Artifact-Fassung übernommen und umgebaut:
  * **Aufnahme:** `getUserMedia` (ohne Echo-/Rausch-/Pegelautomatik) → AudioWorklet liefert PCM-Blöcke mit `currentFrame`. Der Take beginnt samplegenau bei Takt 1 (Frame `T0·sampleRate`); das Einzählen ist nicht enthalten. Fallback: ScriptProcessor. Fehlermeldungen auf Deutsch (verweigert, kein Mikrofon, belegt, unsicherer Kontext).
  * **Export:** `OfflineAudioContext` → WAV 16 Bit Stereo → `<a download>`. Übersteuerung über 0 dBFS wird automatisch abgesenkt und gemeldet. Bei Loops fragt der Export die Länge in Takten ab.
  * **Projektdatei:** ZIP ohne Kompression (eigener Schreiber/Leser, CRC32): `projekt.json`, `spurN.wav` (mono, 16 Bit), Notendatei. Der Leser akzeptiert auch Deflate, sofern der Browser `DecompressionStream` kann.
  * **Noten:** OpenSheetMusicDisplay 1.9.9, erst bei Bedarf von jsDelivr geladen. Eine Instanz pro Spur zeigt nur die zugeordnete Notenstimme. Der Cursor folgt der hörbaren Zeit (`getOutputTimestamp`); jede Ansicht hat eine eigene Zeitliste, weil OSMD Stellen ohne neue Note in der sichtbaren Stimme überspringt.
  * **Taktanzeige:** vier Schlagfelder, feste Leiste unten (mit Stopp), Bildschirmrahmen nur beim Einzählen. Kein hörbarer Takt mehr.
  * **Einzählen:** 4 Schläge (nur sichtbar) oder aus; der Anfangston (C4–H4, Orgelklang) klingt über das Einzählen und endet 0,45 Schlag vor Takt 1.
  * **Ausrichten:** Erkennung des ersten Einsatzes (10-ms-RMS, Schwelle 15 % des Maximums), Verschiebung über „Start“ auf den nächsten Schlag (mit Vorhalt für Verspätung).
  * **Loop:** Takt 1 bis x der Spur als eigener Puffer mit `loop=true`; endlos bis Stopp, auch beim Aufnehmen anderer Spuren.
  * **Entfernt im Verlauf (auf Wunsch):** Beat-Rhythmus, Klick, Pan, Latenz-Regler und -Messung, `window.claude`-Export.
  * **Beibehalten:** deutsche Oberfläche, Hell/Dunkel-Design, Kopplung von Tempo und Tonhöhe über `playbackRate` (im Hilfetext benannt), Datei-Import pro Spur.
* **[NEW]** `chorspur/noten/*.musicxml`: drei Beispielsätze (siehe `PROJECT.md`).
* **[NEW]** `chorspur/test/*.mjs`, `test/testsatz.musicxml`, `test/.gitignore`: Playwright-Tests.
* **[NEW]** `chorspur/TESTBERICHT.md`, `PROJECT.md`, `task.md`, `walkthrough.md`, `GOVERNANCE.md`.
* **[NEW]** `.nojekyll` im Repo-Root.
* **[MODIFY]** `README.md` (Repo-Root): Zeile für das Projekt `chorspur` ergänzt.

---

## 2. Testergebnisse & Verifizierung

### Automatisierte Tests (Desktop-Chromium 1194 headless, Linux)
* **Aufnahmepfad** (`test.mjs`, Fake-Mikrofon): 3,24 s dekodiert, mono, nicht stumm. Erwartet waren 3,21 s; die Differenz ist die Reaktionszeit des Stopp-Klicks. Die Einzählphase ist nicht enthalten. **Bestanden.**
* **Timing** (`test.mjs`, simulierte Schleife: eigener Ausgang 80 ms verzögert als Mikrofon):
  * Ohne Korrektur liegt die Aufnahme +100 bis +102 ms hinter dem Takt.
  * Nach „Alle Einsätze ausrichten“: −0,05 ms auf 7 Schlägen.
  * Weicher Einsatz (60 ms Anstieg): Restfehler −3,4 ms. **Bestanden** (Kriterium < 20 ms), **nur Simulation**.
* **Export:** `ffprobe` meldet pcm_s16le, 2 Kanäle, 44,1 kHz; die Dauer entspricht der Erwartung auf 1 µs. **Bestanden.**
* **Noten** (`score-test.mjs`): 4 und 8 Notenstimmen erkannt, jede Ansicht zeigt genau eine Stimme, der Cursor folgt dem Schlag. **Bestanden.**
* **Projekt** (`proj-test.mjs`):
  * Speichern → Neuladen → Öffnen: Länge, Loop, Lautstärke, Stumm, Start, Zuordnung und Tempo sind identisch; das Audio weicht nur durch die 16-Bit-Rundung ab (0,05 %).
  * Danach weiter aufgenommen und exportiert. **Bestanden.**
* **Anfangston** (`ref-test.mjs`): Bei „A“ liegt der Spitzenwert bei 431 Hz (Auflösung 86 Hz), in der Aufnahme ist kein Ton enthalten. **Bestanden.**
* **Loop** (`loop-test.mjs`):
  * Die Wiedergabe läuft über das Spurende hinaus weiter, der Rahmen blinkt nur beim Einzählen.
  * Export mit 3 Takten = 8,000 s, Klicks bei 0 / 2,667 / 5,333 s, der Rest der Aufnahme ist nicht enthalten. **Bestanden.**
* **Linter:** keiner eingerichtet.

### Manuelle Verifizierung
* **Screenshots** bei 390 px Breite (Chromium): Bedienzeile „Einzählen / Ton / ♪“ einzeilig, Notenansicht je Spur, Leiste unten, Rahmen.
* **iPhone:** Dass die Seite über raw.githack.com lädt, hat Steffen bestätigt („Geht“). Ein vollständiger Ablauf mit Kopfhörern (Aufnahme, Overdub, Export) ist **nicht dokumentiert** → `task.md`.
* **Nicht geprüft:** Audacity, Hörprobe, Android, Bluetooth-Kopfhörer.

### Gefundene und behobene Fehler
* Der Cursor der Unterstimmen sprang zu weit, weil OSMD Stellen ohne neue Note in der sichtbaren Stimme überspringt → eigene Zeitliste je Ansicht.
* Die Notenzuordnung wurde in das Loop-Auswahlfeld geschrieben, weil sie das erste `select` der Spurkarte nahm → Selektor `select[data-i]`.

---

## 3. Visuelle Änderungen & Layout

> [!NOTE]
> Textliche Beschreibung des UI-Stands `0ec3c83`.

* **Layout-Typ:** eine Spalte, maximal 560 px breit, Seitenrand 16 px (Safe-Area berücksichtigt). Unten eine feste Leiste, wenn Wiedergabe oder Aufnahme läuft. Kein horizontales Scrollen bei 390 px.
* **Farbpalette:**
  * Hell: Hintergrund #EDF0F3, Flächen #FFFFFF, Akzent #0F766E (Petrol), Aufnahme #C62828.
  * Dunkel: Hintergrund #0E151B, Flächen #16212A, Akzent #2DD4BF, Aufnahme #F87171.
  * 8 Spurfarben, hell: Blau, Grün, Magenta, Ocker, Violett, Cyan, Oliv, Schiefer.
* **Komponenten-Beschreibung:**
  * *Kopf:* Titel „Chorspur“, rechts „8 Stimmen, Noten, Mix“. Darunter ein Hinweisfeld mit rotem Rand (nur bei Meldungen).
  * *Karte Wiedergabe:*
    * „▶ Abspielen“ (Akzentfarbe, breit) und „Mix speichern“
    * „Projekt speichern“ und „Projekt öffnen“
    * „Alle Einsätze auf den Schlag ausrichten“
    * Tempo-Regler 50–160 BPM
    * eine Zeile „Einzählen [4 Schläge | aus] [Ton –/C…H] [♪]“
    * während der Aufnahme der Hinweis „Kopfhörer verwenden.“ (rot bei Übersteuerung)
    * vier große Schlagfelder (Schlag 1 umrandet, Einzählen rot), darunter die Positionsanzeige und der Pegelbalken
  * *Karte Zeitleiste:* Canvas mit 8 Bahnen à 36 px, Taktraster mit Taktnummern, Wellenformen in Spurfarbe, Loop-Wiederholungen blasser, Abspielkopf in Akzentfarbe.
  * *Karte Noten:* „MusicXML laden“, Regler „Noten-Start (Schläge)“, Hinweistext.
  * *Spurkarten 1–8* (linker Farbrand):
    * Titel „Stimme n · Notenstimme“, rechts Länge oder „Loop x T.“
    * Knöpfe „● Aufnahme“, „Datei“, „Stumm“, „Leeren“
    * Auswahl „Loop“
    * Auswahl „Noten“ (nur nach dem Laden von Noten)
    * Notenzeile auf weißem Grund mit grünem Cursor
    * Lautstärke
    * aufklappbar „Feinabstimmung“: Start, „Einsatz auf den Schlag ausrichten“, Tempo, Tonhöhe
  * *Bildschirmrahmen:* 14–22 px, nur beim Einzählen, rot, blinkt auf jedem Schlag.
  * *Leiste unten:* vier kleinere Schlagfelder, „Takt n / Schlag m“, „■ Stopp“.
* **Verweis auf Assets:** keine Screenshots im Repo (nur in der Cloud-Session erzeugt).
