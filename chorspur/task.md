# Aufgabenliste: Chorspur

## Aktueller Stand
* **Zuletzt bearbeitet:** 2026-10-18 durch Claude Code
* **Letzter Meilenstein:** Rhythmus/Klick entfernt, Einzählen + Anfangston in einer Zeile, Rahmen blinkt nur beim Einzählen, Loop pro Spur (Commit `0ec3c83`)
* **Nächster Schritt:** Realtest am iPhone mit Kopfhörern (Spur 1, Spur 2 darüber, Loop, Projekt speichern/öffnen, Export) und Ergebnis in `TESTBERICHT.md` eintragen
* **Offene Fragen / Blockaden:**
  * Lizenz des Projekts nicht festgelegt
  * Bereitstellung: GitHub Pages nicht aktiviert; genutzt wird raw.githack.com (Drittanbieter)
  * Arbeitsbranch `claude/chorspur-aufnahme` ist nicht nach `main` gemergt; kein Pull Request

---

## 1. Planungsphase
- [x] Ausgangs-Auftrag (TASK.md, Steffen) mit Zielen, Nicht-Zielen und Abnahmekriterien vorhanden (im Chat übergeben, nicht im Repo)
- [x] `PROJECT.md` ausgefüllt
- [ ] `implementation_plan.md`: nicht angelegt; Anforderungen wurden iterativ im Dialog freigegeben (Rückfragerunden zu Loop, Einzählen, Rahmen, Export)

## 2. Umsetzung
- [x] Aufnahme lauffähig
  - [x] `getUserMedia` ohne Echo-/Rausch-/Pegelautomatik, deutsche Fehlermeldungen, Datei-Import als Rückfall
  - [x] AudioWorklet-Aufnahme mit Zeitstempel der Audio-Uhr, Schnitt samplegenau auf Takt 1
- [x] Export als WAV 16 Bit Stereo über `OfflineAudioContext`, Download per `<a download>`
- [x] Zuverlässigkeit am Handy: Wake Lock, Hinweis „Kopfhörer verwenden“, Pegel und Übersteuerungswarnung
- [x] Latenzkorrektur gebaut, später auf Wunsch entfernt (Ersatz: Einsätze auf den Schlag ausrichten, „Start“ per Hand)
- [x] Visueller Taktgeber: Schlagfelder, Leiste unten, Rahmen nur beim Einzählen
- [x] Noten (MusicXML) je Spur mit mitlaufendem Cursor; Zuordnung Spur → Notenstimme
- [x] 8 Spuren; Pan, Beat, Rhythmus und Klick entfernt
- [x] Projekt speichern/öffnen (ZIP: `projekt.json`, `spurN.wav`, Noten)
- [x] Einsätze einzeln oder gemeinsam auf den Schlag ausrichten
- [x] Anfangston beim Einzählen (C–H, eine Oktave)
- [x] Loop pro Spur (1/2/4/8 Takte, endlos bis Stopp; Export fragt Taktzahl)
- [x] Beispielnoten: Alle meine Entchen (4 und 8 Stimmen), Na-na-Vamp

## 3. Verifizierung & Dokumentation
- [x] Lokale Tests ausgeführt und bestanden (Desktop-Chromium headless; Werte in `TESTBERICHT.md`)
- [ ] Realtest Handy (Abnahmekriterium 4): **offen**, nur Desktop geprüft
- [ ] Blinde Hörprobe zweier Spuren (Abnahmekriterium 5): **offen**
- [ ] WAV in Audacity geprüft: offen (nur `ffprobe`)
- [x] Build-Prozess: entfällt
- [x] `walkthrough.md` erstellt
- [x] `GOVERNANCE.md` erstellt
- [x] Git Commit & Push durchgeführt (Branch `claude/chorspur-aufnahme`)
- [x] Statusblock für Übergabe aktualisiert

## 4. Offene Punkte (Backlog, nicht beauftragt)
- [ ] Anfangston pro Spur, vorbelegt aus dem ersten Ton der zugeordneten Notenstimme (angeboten)
- [ ] Taktart der Partitur übernehmen (Raster ist fest 4/4)
- [ ] Schriften lokal einbetten statt Google Fonts (Datenschutz, Offline-Betrieb)
- [ ] Notenanzeige offline verfügbar machen (OSMD lokal statt CDN)
