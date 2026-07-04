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
* **Nächster Schritt:** Schritt 3 — lokale Meetily-Schema-Verifikation
  (`docs/meetily-integration-spike.md`), danach Produktivkonfiguration und
  Live-Smoke-Test mit echtem Anthropic-Key
* **Offene Fragen / Blockaden:** Warte auf Secrets vom Nutzer (ANTHROPIC_API_KEY,
  Admin-Zugangsdaten) für Schritt 4

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
