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
* **Schritt 5 (Smoke-Test):** Synthetisches Testtranskript (kein reales
  Meeting) in `data/meetily_exports/` gelegt, echten Übersetzungs-Job über
  die Web-UI/API gegen den echten Anthropic-Key gefahren — Job-Status
  `done`, Download lieferte plausible deutsche Übersetzung. Zweiten
  Test-Nutzer `bob` angelegt (Passwort `bob-testpass-2026`) und
  Cross-User-Isolation im echten Chrome-Browser verifiziert: `bob` sieht
  `admin`s Job nicht in "Meine Jobs" und erhält beim direkten Aufruf von
  `admin`s Download-URL `404 Job not found`. Test-Transkript nach Abschluss
  wieder gelöscht; Test-User `bob` bewusst belassen für künftige manuelle
  Tests.
* **Nachtrag Meetily-Installation (2026-07-04, Nutzeranfrage):** Erneute,
  breitere Suche (LocalAppData/AppData `meetily*`/`Zackriya*`, ProgramFiles,
  Startmenü, Desktop, `Get-Package`, `Get-Process`, Registry App-Paths)
  bestätigte erneut: kein Treffer — die ursprüngliche Einstufung "nicht
  installiert" war korrekt, keine übersehene Installation. Port 8000 war zu
  diesem Zeitpunkt bereits belegt, aber nachweislich durch den eigenen,
  seit Schritt 5 durchlaufenden Dienst (PID-Commandline-Check) — keine
  Kollision mit Fremdprozessen.

  Danach explizit beauftragt: Meetily v0.4.0 von
  `github.com/Zackriya-Solutions/meetily/releases` installiert.
  MSI-Installer (Pro-Maschine) scheiterte mit Error 1925 (Admin-Rechte
  nötig, wie erwartet). NSIS-`.exe`-Installer mit `/S /CURRENTUSER`
  **funktionierte ohne Admin-Rechte** (Install nach
  `%LOCALAPPDATA%\meetily\`). Beide Downloads per SHA256 gegen GitHub-API
  verifiziert. App einmal gestartet (Hintergrundprozess, kein
  Computer-Use-Zugriff möglich — nicht genehmigbar in diesem
  nicht-interaktiven Lauf), dabei echten Datenpfad
  (`%APPDATA%\com.meetily.ai\meeting_minutes.sqlite`) gefunden und App
  sauber beendet.

  **Schema-Verifikation ergab: ursprüngliche Annahme war falsch.**
  `meetings` hat kein Transkript-Feld; der Text liegt in `transcripts`
  (ein Row pro Audiosegment, Speaker 'mic'/'system', `audio_start_time`),
  bestätigt sowohl durch die leere Live-DB-Kopie als auch die offiziellen
  Migrationsdateien im Meetily-Repo. `SqliteMeetilySource` in
  `meetily_source.py` entsprechend umgeschrieben (Segmente aggregieren,
  chronologisch sortieren), Unit-Tests angepasst, `docs/meetily-integration-spike.md`
  mit dem verifizierten Schema aktualisiert. `.env`/`.env.example` auf
  `MEETILY_SOURCE_MODE=sqlite` mit echtem Pfad umgestellt. Danach erneut
  51 Tests grün, `ruff check .` clean; Dienst neu gestartet und Dashboard
  gegen die echte (noch leere) Meetily-DB fehlerfrei geprüft.

  **Weiterhin offen:** kein reales Testmeeting aufgezeichnet (kein
  Mikrofon-Setup in diesem Auftrag) — Segment-Struktur ist durch Schema +
  Migrationshistorie sehr sicher belegt, aber nicht durch echte
  Beispieldaten. Vor dem ersten echten Produktiv-Job: ein Testmeeting in
  Meetily aufnehmen und `get_transcript()` gegen die entstehenden Zeilen
  prüfen.
* **Produktivsetup insgesamt: funktional abgeschlossen, jetzt mit echter
  Meetily-Integration.** Einziger offener Punkt: Autostart-Registrierung
  (`setup-vm.ps1`) erfordert Admin-Rechte, die diese Sitzung nicht hat —
  siehe unten.
* **Nächster Schritt:** Jemand mit Admin-Rechten auf der VM führt
  `setup-vm.ps1` aus (oder alternative Autostart-Lösung), damit der Dienst
  einen VM-Neustart übersteht. Danach: ein reales Testmeeting in Meetily
  aufnehmen und gegen `SqliteMeetilySource` verifizieren; Test-User `bob`
  optional wieder entfernen; Scaleway-Migration folgt in separatem Auftrag.
* **Offene Fragen / Blockaden:** Admin-Rechte auf der VM nötig, um
  `setup-vm.ps1` erfolgreich auszuführen (Autostart-Registrierung). Bis
  dahin muss der Dienst nach jedem VM-Neustart manuell gestartet werden:
  `cd backend && .venv\Scripts\python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000`

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

## 4. VM-Produktivsetup (dieser Auftrag)
- [x] Code auf VM übertragen, eigenständiges Git-Repo
- [x] Regressionscheck auf VM (1 Bugfix: Windows-Zeilenumbrüche)
- [x] Meetily-Installation geprüft (zunächst nicht vorhanden) → `export_folder`-Modus
- [x] `.env` produktiv befüllt (2 Bugfixes: dotenv-Loading, Pfadauflösung)
- [x] DB initialisiert, Admin-User angelegt
- [x] Dienst manuell gestartet und erreichbar
- [ ] Autostart via Windows Task Scheduler — **blockiert, Admin-Rechte nötig**
- [x] Live-Smoke-Test mit echtem Anthropic-Key
- [x] Cross-User-Download-Isolation im Browser verifiziert
- [x] Meetily v0.4.0 installiert (per-user, NSIS-Installer, kein Admin nötig)
- [x] Reales SQLite-Schema verifiziert — Annahme war falsch, Code + Doku korrigiert
- [x] `.env` auf `sqlite`-Modus mit echtem Pfad umgestellt
- [ ] Echtes Testmeeting in Meetily aufnehmen und `get_transcript()` dagegen prüfen
