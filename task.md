# Aufgabenliste: Wisskomm-Viz (Infrastruktur & Web-Dienst)

## Aktueller Stand
* **Zuletzt bearbeitet:** 2026-07-06 durch Antigravity
* **Letzter Meilenstein:** ZEW CD-Vorgaben (News-Grün, Anthrazit, Hellblau, Grau) und Hausschriften (Linux Libertine, Calibri) aus zewEcon vollständig integriert; SSH-Key-Auth und Dateitransfer in deploy.py implementiert und im Git-Branch gepusht.
* **Nächster Schritt:** API-Guthaben der VM aufladen (Anthropic Developer Console); deploy.py auf VM ausführen und Live-CD-Darstellung verifizieren.
* **Offene Fragen / Blockaden:** Keine (CD-Farben und Schriften vollständig normalisiert).

---

## 1. Planungsphase
- [x] `PROJECT.md` ausgefüllt und verifiziert
- [x] Lösungsüberblick in `implementation_plan.md` aktualisiert

## 2. Umsetzung
- [x] **Web-Service & API-Anbindung:**
  - [x] `app.py` und `deploy.py` mit `load_dotenv` zur Keys-Verarbeitung versehen
  - [x] API-Modell in `prompt.py` auf `claude-opus-4-8` aktualisiert
  - [x] Veraltete API-Parameter (`temperature`) entfernt
  - [x] Token-Limit (`max_tokens`) auf 8000 erhöht (behebt unvollständige JSONs)
- [x] **Infrastruktur & Proxy-Anpassungen:**
  - [x] Gunicorn-Timeout auf der VM auf 120 Sekunden erhöht
  - [x] `@xframe_options_exempt` in Django (`stellar-galaxy`) für IFrame-Anzeige aktiviert

## 3. Verifizierung & Dokumentation
- [x] End-to-End-Upload lokal via `test_upload.py` erfolgreich getestet (Status 200)
- [x] `PROJECT.md` erstellt und dokumentiert
- [x] `walkthrough.md` für den Meilenstein angelegt
- [x] Statusblock für Übergabe aktualisiert

## 4. Sicherheits- & Betriebs-Härtung (2026-07-03, Claude Code)
- [x] Hartkodierte Zugangsdaten/Pfade aus `deploy.py` entfernt → Env-Vars + `.env.example`
- [x] Uvicorn an `127.0.0.1` statt `0.0.0.0` gebunden (Code + VM + Crontab + `.service`)
- [x] `requirements.txt`: `anthropic` gepinnt, fehlendes `python-dotenv` ergänzt
- [x] `SPEC-Wisskomm-Viz.md` → `implementation_plan.md` (AOS-Konvention)
- [x] `.gitignore` angelegt; Repo initialisiert, Push als Branch `claude/wisskomm-viz`
- [x] VM: `.env` auf `600`, Testartefakte aus `output/` entfernt, Autostart-Kommando per Neustart-Simulation verifiziert (HTTP 200)
- [x] SSH-Key-Auth statt Passwort in `deploy.py` (realisiert am 06.07.2026)

## 5. Quarto-Pilot (Stufe 3, 2026-07-03, Claude Code)
- [x] Struktur gem. `implementation_plan.md` Teil J: `_quarto.yml`, `_brand.yml`, `theme/zew.scss`
- [x] Zentrale ZEW-CD (`_brand.yml`) mit aus RGB normalisierten Farben; System-Schrift als Platzhalter
- [x] PPTX-CD-Vorlage `templates/reference-zew.pptx` (Theme-Farben + Schriften)
- [x] Referenz-DP `publications/zew-dp-26-021/` (`index.qmd` + Daten-CSV + Datenvertrag-README)
- [x] Quarto + venv (matplotlib/jupyter) user-lokal auf VM installiert (`~/opt`, `~/wisskomm-quarto-pilot`)
- [x] Render aller 4 Formate erfolgreich; DSGVO-Check (keine externen Requests) bestanden
- [x] PPTX-Realitätscheck: Text nativ/editierbar, Charts als Standbilder (empirisch bestätigt)
- [x] Serving unter eigener URL: `app.py` mountet `/wisskomm/pub`, `publish_quarto.py` rendert+veröffentlicht; End-to-End über Proxy verifiziert (HTTP 200)
- [x] Dashboard-Verlinkung: Sektion „Quarto-Hausdienst" mit Web/PDF/Folien/PPTX-Links; deployed und über Proxy verifiziert
- [x] „signal vs. diluted" ohne Marken-Rot final festgelegt; ZEW-Hausschrift und CD aus zewEcon integriert (06.07.2026)
