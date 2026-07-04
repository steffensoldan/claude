# CLAUDE.md (Meetily-GLM-Bridge)

Dieses Projekt folgt den AOS-Konventionen (lokale AOS-Kopie: `../aos/`),
insbesondere `aos/memory/global-rules.md` (Slim Code, Spec-First, Surgical
Changes, Portabilität/keine Hardcodierung, Fehlerfreie Lauffähigkeit vor
Übergabe) — mit einer dokumentierten Abweichung: Build-Ort ist ein
Top-Level-Ordner statt `aos/projects/Projekte-Claude/`, siehe `PROJECT.md`.

## Testbefehle

```bash
cd backend && pytest -q && ruff check .
```

## Zuständigkeitsbereich

Nur Dateien innerhalb von `meetily-glm-bridge/` — keine Änderungen an `aos/`
oder anderen Top-Level-Projekten in diesem Repo.
