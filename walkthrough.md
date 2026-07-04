# Walkthrough: Meetily-GLM-Bridge — Initialer Aufbau

## Zusammenfassung

Vollständige Erstimplementierung einer Übersetzungs-/Zusammenfassungs-Brücke
für Meetily-Transkripte mit austauschbarem LLM-Provider (Anthropic jetzt,
Scaleway/GLM 5.2 später) und separatem, mehrbenutzerfähigem Web-Interface.
Umgesetzt in einem durchgehenden autonomen Lauf gemäß Konzept
(`/root/.claude/plans/ich-brauche-ein-konzept-agile-sonnet.md`).

## Ergebnis der automatisierten Definition-of-Done

- `pytest -q`: **51 Tests, alle grün** (unit: Provider/Auth/Meetily-Source/Jobs/Config,
  integration: FastAPI-App inkl. Multi-User-Isolation, e2e: voller Pipeline-Durchlauf)
- `ruff check .`: **clean**
- Keine `skip`/`xfail`-Marker eingeführt
- `.env.example` deckt exakt die von `config.py` gelesenen Variablen ab (per Test verifiziert)
- Multi-User-Isolationstest vorhanden und grün (`tests/integration/test_multiuser_isolation.py`)

Ein Zwischenfehler während der Schleife (Jinja2/Starlette-Versionsinkompatibilität:
`TemplateResponse(name, {"request": ..., ...})`-Aufrufform verursachte
`TypeError: unhashable type: 'dict'` im installierten Starlette 1.3.1) wurde
identifiziert und behoben durch Umstieg auf die aktuelle, nicht-deprecated
Aufrufform `TemplateResponse(request=request, name=..., context=...)` — betrifft
`app/main.py`, drei Stellen.

## Bewusste Abweichungen von der ursprünglichen Konzept-Vorlage

1. **Build-Ort:** Top-Level-Ordner `meetily-glm-bridge/` statt
   `aos/projects/Projekte-Claude/...` — letzteres ist in AOS' eigener
   `.gitignore` ausgeschlossen (Projekte sind dort als separate Git-Repos
   gedacht) und diese Sandbox hat ohnehin keinen Zugriff auf die reale
   AOS-Installation auf der VM. Vom Nutzer bestätigt.
2. **Meetily-Integration simuliert:** Kein Zugriff auf eine echte
   Meetily-Installation möglich. Schema/Exportformat sind eine dokumentierte,
   plausible Annahme (`docs/meetily-integration-spike.md`), gegen synthetische
   Fixtures getestet. **Zwingender manueller Schritt vor Produktivbetrieb.**
3. **Reale Inhalte bereits in Anthropic-Phase erlaubt:** Vom Nutzer explizit
   als akzeptiertes Risiko bestätigt, abweichend von der ursprünglichen
   Empfehlung (real erst nach Scaleway-Migration). In `PROJECT.md` dokumentiert.
4. **Ein durchgehender Lauf statt Phasen-Gates:** Auf Nutzerwunsch keine
   Zwischen-Freigaben zwischen Spike/Provider/Integration/Web/Härtung —
   die gesamte Umsetzung lief als ein Zug bis zum grünen Definition-of-Done.
5. **Admin-Env-Vars zentralisiert:** `ADMIN_USERNAME`/`ADMIN_PASSWORD` wurden
   aus `db.py` nach `config.py`/`Settings` verschoben (statt separater
   `os.environ`-Zugriffe), damit der Konsistenztest ".env.example deckt exakt
   die gelesenen Variablen ab" literal und ohne Sonderfall-Ausnahme gilt.

## Manuelle Checklistenpunkte (außerhalb der automatisierten Schleife)

- [ ] Live-Smoke-Test mit echtem `ANTHROPIC_API_KEY` gegen ein reales Transkript
- [ ] Nach Erhalt eines Scaleway-Keys: `GET https://api.scaleway.ai/v1/models`
      aufrufen, echten GLM-5.2-Modell-ID-String in `.env` eintragen, Smoke-Test
      gegen `ScalewayProvider` wiederholen
- [ ] **Vor Ort auf der VM:** echte Meetily-Installation, SQLite-Pfad/Schema
      oder Export-Format verifizieren (Schritte in
      `docs/meetily-integration-spike.md`), `MEETILY_SOURCE_*` in `.env` anpassen
- [ ] Cross-User-Download-Versuch manuell im Browser mit zwei echten
      Benutzerkonten bestätigen (automatisierter Test deckt die Logik ab,
      nicht die tatsächliche Browser-Cookie-Behandlung)
- [ ] Bei Bedarf: `python -m app.db init` mit `ADMIN_USERNAME`/`ADMIN_PASSWORD`
      in `.env` ausführen, um den ersten echten Nutzer anzulegen

## Geänderte/neue Dateien

```
meetily-glm-bridge/
├── PROJECT.md, implementation_plan.md, task.md, walkthrough.md, CLAUDE.md
├── .env.example, .gitignore
├── docs/meetily-integration-spike.md
├── data/.gitkeep
└── backend/
    ├── pyproject.toml
    ├── app/
    │   ├── __init__.py, config.py, db.py, auth.py, jobs.py, meetily_source.py, main.py
    │   └── providers/{__init__,base,_prompts,anthropic_provider,scaleway_provider,factory}.py
    ├── templates/{login,dashboard}.html
    ├── static/app.js
    └── tests/
        ├── conftest.py
        ├── unit/{test_providers,test_auth,test_meetily_source,test_jobs,test_config}.py
        ├── integration/{test_app,test_multiuser_isolation}.py
        └── e2e/test_pipeline.py
```
