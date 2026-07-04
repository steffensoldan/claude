# Aufgabenliste: Meetily-GLM-Bridge — Initialer Aufbau

## Aktueller Stand
* **Zuletzt bearbeitet:** 2026-07-04 durch Claude Code (VM-Produktivsetup)
* **Letzter abgeschlossener Schritt:** Projekt von `steffensoldan/claude`
  (Branch `claude/open-router-aos-integration-827scj`) nach
  `<AOS_ROOT>/projects/Projekte-Claude/meetily-glm-bridge/` übertragen,
  eigenständiges Git-Repo initialisiert. Regressionscheck auf der VM
  durchgeführt: 1 plattformspezifischer Bug gefunden und gefixt
  (`Path.write_text` übersetzte auf Windows `\n`→`\r\n`, dadurch schlug
  `test_full_pipeline_transcript_to_download` fehl; Fix: `newline="\n"` in
  `app/jobs.py::run_job`). Danach alle 51 Tests grün, `ruff check .` clean.
* **Schritt 3 (Meetily-Verifikation):** Meetily ist auf dieser VM NICHT
  installiert (AppData/AppX/Uninstall-Registry/Win32_Product geprüft, kein
  Treffer). `MEETILY_SOURCE_MODE=export_folder` verwendet (bereits
  `.env.example`-Default, entkoppelt vom internen DB-Schema). Ordner
  `data/meetily_exports/` angelegt, aktuell leer. SQLite-Schema-Annahme
  bleibt unverifiziert, bis Meetily installiert wird — siehe
  `docs/meetily-integration-spike.md`.
* **Schritt 4 (Produktivkonfiguration):** `.env` mit vom Nutzer bereitgestelltem
  `ANTHROPIC_API_KEY` sowie `ADMIN_USERNAME=admin`/`ADMIN_PASSWORD=meetily2026`
  befüllt (Nutzerentscheidung). Dabei zwei echte Bugs gefunden und gefixt:
  (1) `.env` wurde nie geladen — kein `dotenv`-Aufruf existierte; jetzt
  `python-dotenv` + `load_dotenv()` in `app/config.py`. (2) Relative Pfade aus
  `.env` (`DATABASE_PATH` etc.) wurden gegen das Arbeitsverzeichnis statt den
  Projekt-Root aufgelöst — landete in `backend/data/` statt `data/`, da die
  dokumentierte Startroutine `cd backend && uvicorn ...` lautet; jetzt via
  `_resolve_path()` gegen `_PROJECT_ROOT` aufgelöst. DB initialisiert
  (`python -m app.db init`), Admin-User `admin` angelegt. Dienst manuell
  gestartet und per curl verifiziert (Login + Dashboard funktionieren).
  **Autostart-Blocker:** `setup-vm.ps1` (Windows Scheduled Task) liegt bereit,
  aber `Register-ScheduledTask` schlägt mit „Zugriff verweigert" fehl — die
  Sitzung läuft als `ZEW\sts` ohne Administratorrechte (nicht elevated). Der
  Dienst läuft aktuell nur manuell im Vordergrund (PID variiert je Neustart);
  Autostart nach VM-Neustart ist NICHT eingerichtet, bis jemand mit
  Admin-Rechten `setup-vm.ps1` ausführt.
* **Nächster Schritt:** Schritt 5 — Smoke-Test mit laufendem manuellem Dienst
* **Offene Fragen / Blockaden:** Admin-Rechte auf der VM nötig, um
  `setup-vm.ps1` erfolgreich auszuführen (Autostart-Registrierung)

---

## 1. Planungsphase
- [x] `PROJECT.md` ausgefüllt und verifiziert
- [x] `implementation_plan.md` erstellt und vom Entwickler freigegeben (Plan-Mode-Approval)

## 2. Umsetzung
- [x] Provider-Abstraktion (base/anthropic/scaleway/factory)
- [x] Meetily-Source-Abstraktion + Spike-Doku (simuliert, siehe PROJECT.md)
- [x] Auth/Jobs/DB-Layer
- [x] FastAPI-App + Templates
- [x] Testsuite (unit/integration/e2e), 51 Tests

## 3. Verifizierung & Dokumentation
- [x] Lokale Tests ausgeführt und bestanden (`pytest -q`: 51 passed; `ruff check .`: clean)
- [x] `walkthrough.md` erstellt
- [x] Git Commit durchgeführt
- [x] Statusblock für Übergabe aktualisiert
