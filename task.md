# Aufgabenliste: Wisskomm-Viz (Infrastruktur & Web-Dienst)

## Aktueller Stand
* **Zuletzt bearbeitet:** 2026-07-03 durch Claude Code
* **Letzter Meilenstein:** Sicherheits- und Betriebs-Härtung + Ersteinrichtung der Versionskontrolle. Zugangsdaten aus `deploy.py` entfernt (jetzt Env-Vars), Uvicorn auf `127.0.0.1` gebunden, VM-`.env` auf `600`, Crontab-Autostart angeglichen, Repo initialisiert und als Branch `claude/wisskomm-viz` nach `steffensoldan/claude` gepusht.
* **Nächster Schritt:** (1) SSH-Key-Auth statt Passwort in `deploy.py` (separat vereinbart). (2) Auswertung der ersten echten PDF-Aufbereitung durch Forschende.
* **Offene Fragen / Blockaden:** Autostart via systemd nicht möglich (kein root); Boot-Autostart läuft über `@reboot`-Crontab, real per Reboot noch unbestätigt (nur Prozess-Simulation verifiziert).

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
- [ ] SSH-Key-Auth statt Passwort in `deploy.py` (separat vereinbart)
