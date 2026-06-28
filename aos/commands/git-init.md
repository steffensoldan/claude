---
name: git-init
description: Initialisiert ein neues Projekt im Lightweight AOS-Modus (erstellt .gitignore, PROJECT.md und task.md). Fragt nach abweichenden Regeln. Aufruf via /git-init <Projektpfad>.
---

Initialisiere ein lokales Git-Repository. Pfad: $ARGUMENTS

Standardpfad für neue Projekte: `<AOS_ROOT>\projects\Projekte-Claude\<Projektname>`

Halte dich strikt an diese Reihenfolge:

1. Prüfe ob $ARGUMENTS angegeben wurde. Falls nicht: FRAGE nach dem Projektpfad. Fahre nicht fort ohne klaren Pfad.
2. Prüfe ob im Zielverzeichnis bereits ein `.git`-Verzeichnis existiert. Falls ja: STOPPEN und melden — kein doppeltes Init.
3. `git init` im Zielverzeichnis ausführen.
4. `.gitignore` anlegen (Inhalt siehe unten).
5. **Lightweight-Setup durchführen (Standard):**
   - Kopiere die Vorlagen `PROJECT.md` und `task.md` aus `<AOS_ROOT>\templates\` in das Projektverzeichnis.
   - Frage den Benutzer vorab nach: Projektname, Ziel des Projekts, Tech-Stack und Testbefehlen.
   - Befülle die kopierte `PROJECT.md` mit diesen Angaben.
   - Initialisiere den Statusblock in `task.md` (Zuletzt bearbeitet: Heute, Nächster Schritt: Erste Implementierung planen).
6. **Tool-Configs nur bei Bedarf (Abweichungsprüfung):**
   - Frage den Benutzer, ob für dieses Projekt projektspezifische Abweichungen von den globalen Regeln nötig sind.
   - Nur wenn der Benutzer dies bejaht, erstelle eine lokale `CLAUDE.md` (für Claude Code) bzw. `DEVELOPMENT.md` (für Antigravity) mit den entsprechenden abweichenden Anweisungen (Inhalt siehe unten). Andernfalls lasse diese Dateien weg (beide Clients laden standardmäßig die globalen Regeln aus `<AOS_ROOT>\memory\global-rules.md`).
7. `git add -A` und `git commit -m "init: Lightweight AOS Projektstruktur"` ausführen.
8. Status melden: Pfad, Branch, Anzahl committeter Dateien und bestätigen, dass das Projekt im Lightweight-Modus aufgesetzt wurde.

Noch kein Remote anlegen — das erfolgt separat bei Launch.

---

Inhalt der `.gitignore` (Standard):

```
# Abhängigkeiten
node_modules/
.pnp/
.pnp.js

# Build-Outputs
dist/
build/
.next/
.nuxt/
out/

# Umgebungsvariablen
.env
.env.local
.env.*.local

# Editor & OS
.DS_Store
Thumbs.db
.vscode/
.idea/

# Logs
*.log
npm-debug.log*

# Cache
.cache/
.parcel-cache/
.eslintcache

# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/
```

---

Inhalt der lokalen `CLAUDE.md` oder `DEVELOPMENT.md` (NUR bei projektspezifischen Abweichungen):

```markdown
# Projektspezifische Abweichungen / Sonderregeln

@<AOS_ROOT>\memory\global-rules.md

## Abweichende Regeln
- [Hier nur Regeln eintragen, die von den globalen Regeln abweichen. Falls keine Abweichungen nötig sind, diese Datei nicht erstellen!]
```
