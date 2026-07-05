# Aufgabenliste: Meetily-GLM-Bridge — Initialer Aufbau

## Aktueller Stand
* **Zuletzt bearbeitet:** 2026-07-05 durch Claude (Cowork/Dispatch) — Produktivbetrieb abgeschlossen
* **Status: PRODUKTIV** — Dienst läuft, Autostart registriert, Meetily-Integration verifiziert.

### Abgeschlossene Schritte (chronologisch)

* **Code-Transfer & Regressionscheck:** Projekt von `steffensoldan/claude`
  (Branch `claude/open-router-aos-integration-827scj`) nach
  `<AOS_ROOT>/projects/Projekte-Claude/meetily-glm-bridge/` übertragen,
  eigenständiges Git-Repo initialisiert. 1 Windows-Bug gefixt
  (`Path.write_text` CRLF → `newline="\n"` in `app/jobs.py`). 51 Tests grün.

* **Produktivkonfiguration:** `.env` mit `ANTHROPIC_API_KEY`, `ADMIN_USERNAME=admin`,
  `ADMIN_PASSWORD=meetily2026` befüllt. 2 Bugs gefixt: (1) `.env` wurde nie geladen
  (`python-dotenv` fehlte), (2) relative Pfade landeten in `backend/data/` statt
  `data/` → via `_resolve_path()` gegen `_PROJECT_ROOT` aufgelöst.
  DB initialisiert, Admin-User `admin` angelegt.

* **Smoke-Test:** Synthetisches Transkript → echter Anthropic-Key → Job `done` →
  deutsche Übersetzung geliefert. Cross-User-Isolation im Browser verifiziert
  (Test-User `bob` angelegt, Isolation bestätigt, `bob` bleibt für manuelle Tests).

* **Meetily v0.4.0 installiert** (NSIS-Installer `/S /CURRENTUSER`, kein Admin nötig,
  unter `%LOCALAPPDATA%\meetily\`). SHA256 gegen GitHub-API verifiziert.

* **Reales SQLite-Schema verifiziert** — ursprüngliche Annahme war falsch:
  Transkript liegt NICHT als Blob in `meetings`, sondern in separater `transcripts`-Tabelle
  (ein Row pro Audiosegment, Speaker `mic`/`system`, `audio_start_time`).
  `SqliteMeetilySource` umgeschrieben, Tests angepasst, `docs/meetily-integration-spike.md`
  aktualisiert. `.env` auf `MEETILY_SOURCE_MODE=sqlite` mit echtem Pfad
  (`%APPDATA%\com.meetily.ai\meeting_minutes.sqlite`) umgestellt. 51 Tests grün.

* **HOST auf 0.0.0.0 umgestellt** → Dienst netzwerkweit erreichbar unter
  `http://192.168.70.143:8000`.

* **Autostart registriert (2026-07-05):** Windows Scheduled Task `MeetilyGLMBridge`
  erfolgreich via `fix-autostart.ps1` (elevated, UAC-Ja durch Nutzer) registriert.
  Task startet Dienst automatisch bei Systemstart als User `sts` (S4U, LogonType).
  Skripte: `fix-autostart.bat` + `fix-autostart.ps1` im Projektroot für künftige
  Neuregistrierung (z.B. nach venv-Rebuild).

### Architektur-Einschränkung (bekannt, bewusst)

Der Dienst liest die **lokale** Meetily-SQLite-Datenbank auf dem VM-Server selbst
(`%APPDATA%\com.meetily.ai\meeting_minutes.sqlite`). Remote-Nutzer mit Meetily
auf eigenen Laptops können deren Transkripte nicht über diesen Dienst abrufen.

**Aktuelle Nutzer-Workflow:** RDP auf `sts-w-0001.zew.local` → Meetily starten →
Meeting aufnehmen → Browser → `http://192.168.70.143:8000` → Login → übersetzen/zusammenfassen.

**Diskutierte Erweiterungsoptionen (noch nicht beauftragt):**
- Datei-Upload-Modus (einfach, 1–2 Tage): Nutzer lädt Transkript-Datei hoch,
  Dienst verarbeitet ohne lokale SQLite-Abhängigkeit
- Browser-Audio-Streaming (komplex): Browser → WebSocket → VM-seitiger
  Whisper-Dienst → Claude API → Echtzeit-Anzeige (erfordert `faster-whisper`
  als separaten Service; Claude API unterstützt kein Echtzeit-Audio-Streaming)

### Offene Punkte

* **Echtes Testmeeting fehlt:** Kein reales Testmeeting aufgezeichnet — Schema
  ist durch Migrationsdateien + leere Live-DB sehr sicher belegt, aber noch nicht
  durch echte Beispieldaten bestätigt. Vor erstem Produktiv-Job: ein Testmeeting
  in Meetily aufnehmen und `get_transcript()` dagegen prüfen.
* **Scaleway-Migration:** Noch kein Scaleway-Key vorhanden — separater Auftrag.
  Sobald Key liegt: `GET https://api.scaleway.ai/v1/models` → GLM-Modell-ID in
  `.env` eintragen → `PROVIDER=scaleway` → Smoke-Test.
* **Test-User `bob`** (Passwort `bob-testpass-2026`) bleibt in DB für manuelle
  Tests; bei Bedarf via `python -m app.db` entfernen (CLI noch nicht implementiert
  → direkte SQLite-Abfrage nötig).

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
- [x] Autostart via Windows Task Scheduler — registriert via `fix-autostart.bat` (UAC elevated)
- [x] Live-Smoke-Test mit echtem Anthropic-Key
- [x] Cross-User-Download-Isolation im Browser verifiziert
- [x] Meetily v0.4.0 installiert (per-user, NSIS-Installer, kein Admin nötig)
- [x] Reales SQLite-Schema verifiziert — Annahme war falsch, Code + Doku korrigiert
- [x] `.env` auf `sqlite`-Modus mit echtem Pfad umgestellt
- [x] HOST auf 0.0.0.0 → netzwerkweit erreichbar unter http://192.168.70.143:8000
- [ ] Echtes Testmeeting in Meetily aufnehmen und `get_transcript()` dagegen prüfen
- [ ] Scaleway-Migration (separater Auftrag, Key noch nicht vorhanden)
