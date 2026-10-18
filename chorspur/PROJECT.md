# Projekt-Metadaten: Chorspur

Mehrspur-Aufnahme für Chorstimmen im Browser: bis zu 8 Stimmen nacheinander mit Kopfhörern singen, mitlaufende Noten je Stimme, Mix als WAV. Primäres Zielgerät: Smartphone (iPhone/Safari, Android/Chrome).

---

## 1. Übersicht & Stakeholder
* **Ziel:** Einzelne Chorstimmen zu Hause übereinander aufnehmen (Overdub), taktgenau ausrichten, als Projekt speichern und als Mix exportieren. Kein Server, keine Cloud: alles läuft lokal im Browser.
* **Verantwortlicher Client:** Claude Code (Cloud-Session)
* **Maintainer / Bus-Faktor:** Steffen Schmuck-Soldan (Owner, Nutzer). Kontextübergabe über diese Datei, `task.md`, `walkthrough.md`, `TESTBERICHT.md`.
* **Lizenz:** offen, nicht festgelegt. Das Repository `steffensoldan/claude` ist öffentlich (siehe `GOVERNANCE.md`).

## 2. Technologie-Stack & Lauffähigkeit
* **Core:** eine einzige HTML-Datei, Vanilla JavaScript, Web Audio API (AudioWorklet für die Aufnahme, OfflineAudioContext für den Export). Kein Build-Schritt, kein Framework.
* **Externe Ressourcen (zur Laufzeit):**
  * OpenSheetMusicDisplay 1.9.9 (BSD-3-Clause) von `cdn.jsdelivr.net`, wird erst beim Laden einer Notendatei nachgeladen.
  * Schriften Bricolage Grotesque, IBM Plex Sans/Mono über Google Fonts (Fallback-Schriften vorhanden).
* **Datenbank / API:** keine. Zustand nur im Arbeitsspeicher, Einstellungen in `localStorage` (`chorspur.count`, `chorspur.ref`), Projekte als ZIP-Download.
* **Styling / UI:** Vanilla CSS, Hell/Dunkel über `prefers-color-scheme`, eine Spalte, ab 390 px Breite getestet.
* **Paketmanager:** keiner für die App. Tests: Node.js 22 + Playwright 1.56 (lokal/global installiert), Chromium, `ffprobe`, `unzip`.
* **Voraussetzung Mikrofon:** sicherer Kontext (HTTPS oder `http://localhost`).

## 3. Setup- & Startbefehle (Zero-Context-Befehle)
* **Abhängigkeiten installieren:** keine für die App. Für Tests: `npm i -g playwright@1.56.1` und im Ordner `test/` einen Link `node_modules/playwright` auf das globale Paket (`node_modules/` ist gitignored).
* **Development Server starten:** im Ordner `chorspur/`: `python -m http.server 8765` → `http://localhost:8765/chorspur.html`
* **Am Handy öffnen (aktuell genutzt):** `https://raw.githack.com/steffensoldan/claude/<commit-sha>/chorspur/chorspur.html` (Commit-SHA des gewünschten Stands; githack ist ein Drittanbieter-Proxy für öffentliche GitHub-Dateien).
* **Linter ausführen:** keiner eingerichtet.
* **Test-Suite ausführen** (Server läuft, `CHROME` zeigt auf Chromium, `<osmd.js>` = lokale Kopie von `opensheetmusicdisplay.min.js` 1.9.9, `<out>` = Ausgabeordner):
  * `node test/test.mjs http://localhost:8765/chorspur.html <out>` – Aufnahmepfad (Fake-Mikrofon), Timing, Ausrichten, WAV-Export
  * `node test/score-test.mjs http://localhost:8765/chorspur.html <osmd.js> <out>/s.png [musicxml]` – Noten je Spur, Cursor
  * `node test/proj-test.mjs http://localhost:8765/chorspur.html <osmd.js> <out>` – Projekt speichern/öffnen
  * `node test/ref-test.mjs http://localhost:8765/chorspur.html` – Anfangston
  * `node test/loop-test.mjs http://localhost:8765/chorspur.html <out>` – Loop, Rahmen, Export mit Taktzahl
  * Die Tests aus `test/` heraus starten (relative Pfade auf `../noten/`).
* **Produktions-Build:** entfällt (statische Datei).

## 4. Verzeichnisse & Struktur
* `chorspur.html`: die App (HTML, CSS, JS in einer Datei). Testzugang über `?test` in der Adresse (`window.__chorspur`).
* `noten/`: Beispiel-Notendateien (MusicXML)
  * `alle-meine-entchen.musicxml` – Volkslied, 4 Stimmen (SATB)
  * `alle-meine-entchen-8stimmen.musicxml` – dito + 4 leere Stimmen (Percussion 1–2, Impro 1–2)
  * `na-na-vamp.musicxml` – eigener Satz über F–Es–B–F, 4 Stimmen
* `test/`: automatische Browser-Tests (Playwright) und `testsatz.musicxml`
* `TESTBERICHT.md`: Messwerte aller Testläufe, chronologisch
* `walkthrough.md`: Änderungsnachweis und UI-Beschreibung
* `task.md`: Stand, erledigte und offene Aufgaben
* `GOVERNANCE.md`: Lifecycle, IP/Lizenzen, Risiken, Kosten, Barrierefreiheit
