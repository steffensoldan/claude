# GitHub Trend Monitor

**Status:** Produktiv  
**Erstellt:** 2026-06-27  
**Implementiert durch:** Claude (Cowork)

---

## Zweck

Täglicher Monitor für GitHub-Repositories nach Thema. Erkennt neue, populäre und stark wachsende Repos — zugänglich per Telegram-Bot.

## Architektur

```
C:\AI-Tools\claude\github-trend-monitor\
├── core.py              # Geteilte Logik (GitHub API, Snapshots, Delta, Report)
├── trend_monitor.py     # CLI-Entry-Point (täglich via Task Scheduler)
├── config.json          # Thema, Abfrage, Kategorie-Limits
├── .env                 # GITHUB_TOKEN (gitignored)
├── setup-vm.ps1         # Scheduled Task Registrierung (als AI-Admin ausführen)
├── state/snapshots/     # Tägliche JSON-Snapshots (gitignored)
└── reports/             # Markdown-Reports inkl. LATEST.md (gitignored)
```

**Integration:** Telegram-Commands in `C:\AI-Tools\VM-Server\proxy.py`

## Telegram-Befehle

| Befehl | Funktion |
|---|---|
| `/trend` | Letzter vollständiger Report |
| `/trend-week` `/trend-month` `/trend-24h` `/trend-30d` | Einzelkategorien |
| `/trend-now` | Frischen Lauf anstoßen |
| `/trend-topic <query>` | Thema live ändern |
| `/trend-help` | Hilfe |

## Abhängigkeiten

- Python 3.11+ (stdlib only — kein pip install)
- `C:\AI-Tools\AutoGen\venv\Scripts\python.exe`
- GitHub Classic PAT (kein Scope)

## Verwandte Dateien

- `C:\AI-Tools\VM-Server\proxy.py` — Telegram-Bot mit integrierten Trend-Commands
- `C:\Users\sts\AOS\projects\github-trend-monitor\` — AOS-Spiegelung (Strukturinfo)
