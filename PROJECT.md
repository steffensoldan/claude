# PROJECT.md: Meetily-GLM-Bridge

## Ziel

Übersetzungs- und Zusammenfassungs-Brücke für [Meetily](https://github.com/Zackriya-Solutions/meetily)
(lokale Meeting-Transkription, MIT-Lizenz, läuft auf derselben Windows-VM).
Meetily transkribiert lokal (Whisper.cpp/Parakeet), kann aber nicht
Englisch→Deutsch übersetzen (Whispers `translate`-Task geht nur Richtung
Englisch). Dieses Projekt liest Meetily-Transkripte, übersetzt/fasst sie per
LLM zusammen und stellt Ergebnis über ein separates, mehrbenutzerfähiges
Web-Interface mit Login bereit (nicht Meetilys eigenes Admin-Panel).

## Tech-Stack

- Python 3.11+, FastAPI, Jinja2-Templates, Vanilla-JS (kein Frontend-Framework)
- SQLite (Stdlib `sqlite3`, keine ORM) für Nutzer/Sessions/Jobs — getrennt von
  Meetilys eigener Datenbank
- LLM-Provider austauschbar über Env-Var `PROVIDER`:
  - `anthropic`: `anthropic`-SDK, Modell `claude-sonnet-5`
  - `scaleway`: `openai`-SDK gegen `https://api.scaleway.ai/v1` (GLM 5.2,
    EU-Hosting/Iliad-eigentümergeführt)
- Tests: `pytest`, Linting: `ruff`

## Bewusste Risikoentscheidung (dokumentiert, nicht stillschweigend)

Reale Meeting-Inhalte dürfen bereits während der Anthropic-Provider-Phase
verarbeitet werden — explizite Nutzerentscheidung, abweichend von der
ursprünglichen Empfehlung (real erst nach Scaleway/GLM-Migration). Damit
verlassen Meeting-Inhalte in dieser Phase die VM Richtung US-Anbieter.
Baseline-Hygiene bleibt trotzdem verbindlich: keine Inhalts-Logs, Secrets nur
in `.env`. Das Mobile-Dispatcher-Compliance-Gate aus `MOBILE.md` des lokalen
AOS (keine Transkriptinhalte im mobilen Steuer-Chat tippen) bleibt davon
unberührt in Kraft.

## Build-Ort-Abweichung von AOS-Standardkonvention

AOS sieht Projekte unter `<AOS_ROOT>/projects/Projekte-Claude/` vor — dieser
Ordner ist in AOS' eigener `.gitignore` bewusst ausgeschlossen (jedes Projekt
dort ist eine eigenständige Git-Historie). Da diese Session in einem
Cloud-Sandbox ohne Zugriff auf die reale AOS-Installation läuft, liegt dieses
Projekt stattdessen als eigenständiger Top-Level-Ordner im Repo
(`steffensoldan/claude`), analog zu den bestehenden Ordnern
`github-trend-monitor/`, `safaitic-research/`. Bei Übertragung auf die
reale VM kann es unverändert nach `<AOS_ROOT>/projects/Projekte-Claude/` verschoben
und dort als eigenes Git-Repo initialisiert werden.

## Meetily-Integration — SIMULIERTE ANNAHME, vor Ort zu verifizieren

Kein Zugriff auf eine echte Meetily-Installation in dieser Sandbox möglich
(Tauri-Desktop-App, Audio-Hardware nötig). Die Integration basiert auf einer
dokumentierten, plausiblen Schema-Annahme (siehe
`docs/meetily-integration-spike.md`) und wird gegen synthetische
Fixture-Daten getestet. **Vor Produktivbetrieb zwingend lokal auf der VM zu
verifizieren:** tatsächlicher SQLite-Pfad/Schema bzw. Export-Format von
Meetily, danach `MEETILY_SOURCE_*`-Env-Vars entsprechend anpassen.

## Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp ../.env.example ../.env   # Werte eintragen
python -m app.db init        # Tabellen anlegen + ersten Admin-User erstellen
uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
```

## Testbefehle

```bash
cd backend
pytest -q
ruff check .
```

## Verzeichnisstruktur

```
meetily-glm-bridge/
├── PROJECT.md, implementation_plan.md, task.md, walkthrough.md, CLAUDE.md
├── .env.example
├── backend/
│   ├── pyproject.toml
│   ├── app/           # FastAPI-App, Provider-Abstraktion, Meetily-Source
│   ├── templates/      # Jinja2
│   ├── static/
│   └── tests/{unit,integration,e2e,fixtures}/
├── docs/meetily-integration-spike.md
└── data/               # gitignored: users.db, jobs.db, downloads/
```
