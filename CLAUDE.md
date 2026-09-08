# CLAUDE.md

Leitfaden für Claude Code (claude.ai/code) in diesem Repository.

## Was das hier ist

Eine **Sammlung eigenständiger Projekte**, kein einzelnes Programm. Es gibt keinen Repo-weiten Build, keine Tests auf oberster Ebene und keine gemeinsamen Abhängigkeiten. Jedes Projekt liegt in einem eigenen Verzeichnis und ist für sich zu behandeln.

Zwei Sorten Projekt:

- **Werkzeuge** (Python, PowerShell) — `github-trend-monitor`, `aos`
- **Buchprojekte** (Dokumentation, Manuskripte, Build-Skripte) — `safaitic-research`, `diabelli-variationen`

**Arbeitssprache ist Deutsch.** READMEs, Projektdokumentation und Commit-Messages sind auf Deutsch zu verfassen.

## Projekte

| Verzeichnis | Art | Inhalt | Einstieg |
|---|---|---|---|
| `aos/` | Werkzeug | „Agentic Operating System": gemeinsames Regel-, Command- und Hook-Verzeichnis für Claude Code und Antigravity auf einem Windows-System. Hat **eigene** `CLAUDE.md`. | `aos/README.md`, `aos/CLAUDE.md` |
| `github-trend-monitor/` | Werkzeug | Täglicher GitHub-Repo-Monitor nach Thema, Ausgabe per Telegram-Bot. Produktiv. | `github-trend-monitor/PROJECT.md` |
| `safaitic-research/` | Buchprojekt | „Wer dies liest, lebe lang" — Lyrikband aus safaitischen Felsinschriften auf Basis des OCIANA-Korpus. Aktuelle Fassung v6. | `safaitic-research/README.md` |
| `diabelli-variationen/` | Buchprojekt | „Dreiunddreißig Eingriffe" — Gedichtband nach dem Verlauf von Beethovens op. 120. Bauplan Fassung 2, kein Stück geschrieben. | `diabelli-variationen/README.md` |

## Bindende Regeln

`aos/memory/global-rules.md` erklärt sich für **jeden Agenten in jeder Session** für verbindlich, mit dieser Präzedenz:

1. Explizite Anweisung des Nutzers in der laufenden Session
2. Projekt-`CLAUDE.md` / `DEVELOPMENT.md` — nur die dort gelisteten Abweichungen
3. `aos/memory/global-rules.md`

Vor Arbeiten in `aos/` diese Datei lesen. Bei Arbeiten in den übrigen Projekten gilt sie dem eigenen Anspruch nach ebenfalls; sie enthält unter anderem eine Definition of Done (Qualitätssicherung, Übergabefähigkeit).

## Konvention für Buchprojekte

`safaitic-research/` und `diabelli-variationen/` folgen demselben Muster. Neue Buchprojekte ebenso anlegen:

- **`README.md`** mit Kurzbeschreibung, Zielen, einer Tabelle „Wo ist was" (welcher Ordner ist aktuell, welcher abgelöst) und einer **Zeitachse** der Konzeptstufen.
- **Ein aktiver Arbeitsordner** (`register/`, `bauplan/`) — nur hier wird gearbeitet.
- **`archiv/`** für abgelöste Entwicklungsstufen. Nicht löschen: Vorstufen bleiben aus Nachvollziehbarkeit erhalten, mit einer `README.md`, die begründet, warum die Stufe verworfen wurde und was in die Nachfolgefassung überging.
- **Belegstatus ausweisen.** Wo Zuordnungen oder Deutungen gesetzt und nicht belegt sind, ist das je Eintrag zu markieren (siehe `diabelli-variationen/bauplan/STUECKE.md`, Spalte „Stand"). Nichts als gesichert ausgeben, was Interpretation ist.

## Kommandos

Es gibt keine Repo-weiten Kommandos. Alle Skripte laufen mit **Python 3.11+ aus der Standardbibliothek** — keine `requirements.txt`, kein `pip install` nötig.

```bash
# GitHub Trend Monitor (aus github-trend-monitor/)
python trend_monitor.py            # Lauf anstoßen; braucht GITHUB_TOKEN in .env

# Safaitic: Manuskript neu bauen (aus safaitic-research/, nicht aus scripts/)
python register/scripts/build_register.py
```

**Falle bei `build_register.py`:** Das Skript liest `register/wer_dies_liest_register_v6.docx` als Vorlage und schreibt in **dieselbe Datei** zurück. Es ersetzt nur `word/document.xml` im Zip-Container und erhält damit das Docx-Skelett (Styles, Kopfzeilen). Vor dem Lauf eine Kopie sichern, sonst ist die Vorlage weg. `python-docx` wird nicht verwendet.

## Umgebung

- Das Repo wird **auf Windows** betrieben (`C:\AI-Tools\claude\…`, operativer Server `sts-w-0001.zew.local`). Die Pfadangaben in `README.md` und `PROJECT.md` beziehen sich darauf.
- **`.ps1`-Skripte sind in einer Linux-Websession nicht ausführbar** (`install.ps1`, `export-aos.ps1`, `setup-vm.ps1`, `ops/deploy.ps1`). Sie können gelesen und bearbeitet, aber nicht getestet werden. Änderungen daran entsprechend kennzeichnen.
- `.gitignore` schließt Laufzeitdaten aus: `state/`, `reports/`, `*.log`, `.env`, `*.env`. Keine Tokens oder Zugangsdaten committen.

## Pflege dieser Datei

Wird ein Projekt angelegt, umbenannt oder abgeschlossen, sind **beide** Übersichten nachzuziehen: die Projekttabelle hier und die in `README.md`.
