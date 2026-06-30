# Dokumentation & Walkthrough: GitHub Trend Monitor

Zusammenfassung der Implementierung, Deployment-Entscheidungen und Verifikation.
Implementiert: 2026-06-27 durch Claude (Cowork).

---

## 1. Durchgeführte Änderungen

* **[NEW]** `core.py`: Geteilte Logik — GitHub Search API (paginiert, stdlib-only), Snapshot-Management (tägliche JSON-Dateien), Delta-Berechnung (24h/30d), Markdown-Report-Rendering, Section-Extraktion für Telegram-Einzelabfragen
* **[NEW]** `trend_monitor.py`: CLI-Entry-Point — lädt .env + config.json, ruft `core.run()` auf, wird täglich via Task Scheduler ausgeführt
* **[NEW]** `config.json`: Startkonfiguration — Thema: "Artificial Intelligence", min. 100 Sterne, 4 Kategorien, 35 Tage Retention
* **[NEW]** `setup-vm.ps1`: Registriert Windows Scheduled Task `GHTrend-Collector` (täglich 06:00, Python-venv von AutoGen)
* **[MODIFY]** `C:\AI-Tools\VM-Server\proxy.py`: 7 neue Telegram-Befehle (`/trend*`) integriert; `/start`-Nachricht erweitert

### Architektur-Entscheidung: kein separater bot.py

Ursprüngliches Konzept sah einen eigenen `bot.py`-Prozess vor. Verworfen, weil zwei Prozesse nicht dieselbe Bot-Token pollen können (Telegram-API). Lösung: Trend-Befehle direkt in den bestehenden `proxy.py`-Bot integriert — ein Polling-Loop, alles in einem Prozess.

---

## 2. Telegram-Befehle

| Befehl | Funktion |
|---|---|
| `/trend` | Letzter vollständiger Report (LATEST.md) |
| `/trend-week` | Nur Kategorie: Neue Repos (7 Tage) |
| `/trend-month` | Nur Kategorie: Neue Repos (30 Tage) |
| `/trend-24h` | Nur Kategorie: Stärkstes Wachstum (24h) |
| `/trend-30d` | Nur Kategorie: Stärkstes Wachstum (30 Tage) |
| `/trend-now` | Frischen Collector-Lauf anstoßen (async, ~1–2 min) |
| `/trend-topic <query>` | Thema/Query in config.json live aktualisieren |
| `/trend-help` | Hilfenachricht |

---

## 3. Testergebnisse & Verifikation

### Slim-Check
- Keine externen Dependencies — stdlib-only (`urllib.request`, `json`, `datetime`, `pathlib`, `argparse`, `os`)
- `import core` und `import trend_monitor` fehlerfrei (keine ImportError)

### Live-Verifikation
- Erster Lauf via `/trend-now` im Telegram: **erfolgreich** (2026-06-27)
- GITHUB_TOKEN in `.env` gesetzt — authentifizierter API-Zugriff (30 Search-Req/min)
- Kategorien 1 & 2 (neue Repos 7d/30d): vollständig
- Kategorien 3 & 4 (24h/30d-Delta): Warmlauf-Modus (korrekt — kein Baseline am ersten Tag)
- Report in `reports/LATEST.md` erzeugt ✅
- Snapshot in `state/snapshots/2026-06-27.json` erzeugt ✅

### Warmlaufphase
- 24h-Delta: ab dem **2. täglichen Lauf** vollständig
- 30d-Delta: nach **~30 Läufen** vollständig; Report kennzeichnet unvollständige Baselines explizit

---

## 4. Wichtige Implementierungsdetails

### GitHub Rate Limits
- Unauthentifiziert: 10 Search-Requests/Stunde — für paginierten Abruf (bis 10 Seiten) nicht ausreichend
- Authentifiziert (Classic PAT, kein Scope): 30 Search-Requests/Minute — ausreichend
- PAT: Classic, kein Scope, 1 Jahr Laufzeit

### Telegram-Nachrichtenlimit
- Telegram begrenzt Nachrichten auf 4096 Zeichen
- `_trend_truncate()` kürzt bei Bedarf mit Hinweis auf `/trend` für Vollversion

### Pfad-Konfiguration
- `TREND_BASE_DIR` in `proxy.py` zeigt auf `C:\AI-Tools\claude\github-trend-monitor`
- Überschreibbar via Umgebungsvariable `TREND_BASE_DIR`
- Laufzeit-Daten (state/, reports/) liegen im selben Verzeichnis, sind gitignored

### Scheduled Task
- Task `GHTrend-Collector`: täglich 06:00, Python-venv `C:\AI-Tools\AutoGen\venv\Scripts\python.exe`
- `setup-vm.ps1` muss als AI-Admin ausgeführt werden (Task-Registrierung mit elevated privileges)

---

## 5. Offene Punkte / Optional

- [ ] `setup-vm.ps1` als AI-Admin ausführen (Task Scheduler für täglichen Automatiklauf)
- [ ] `/trend-toexcel` — Report als XLSX exportieren (optional)
- [ ] Erweiterung: `/trend-topic` mit Bestätigung des aktuellen Themas vor Änderung
