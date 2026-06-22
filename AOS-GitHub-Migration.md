# AOS GitHub Migration — Konzeptdokument

**Stand:** 2026-06-22  
**Status:** Entwurf — offene Punkte vorhanden

---

## Ziel

Das AOS (Agent Operating System) soll in ein privates GitHub-Repository migriert werden, sodass es von beliebigen Rechnern per Clone oder ZIP-Installation nutzbar ist — primär mit Claude Code (Subscription-Login, kein API-Key nötig).

---

## Repo-Struktur

### Ins Repo (wird geklont)

| Ordner | Inhalt | Bemerkung |
|---|---|---|
| `memory/` | `global-rules.md`, `MEMORY.md` | Keine Secrets, sicher |
| `templates/` | PROJECT.md, task.md, etc. | Reine Vorlagen |
| `commands/` | Slash-Commands | Sekundär, aber schadet nicht |
| `hooks/` | `block-dangerous.sh` | Harmlos, nützlich |
| `scripts/` | `add-skill.ps1`, `pptx-to-png.ps1` | Siehe offene Punkte |
| `dialog/README.md` | Anleitung zur Dialog-Führung | Nur die Anleitung, nicht die Inhalte |

### Nicht ins Repo (.gitignore)

| Ordner | Grund |
|---|---|
| `dialog/<thema>/` | Laufende Konversationen, potenziell ZEW-intern |
| `projects/` | Projekte haben eigene Repos |

---

## .gitignore

```
dialog/*/
projects/
*.env
*.key
*.secret
```

---

## Setup auf einem fremden Rechner

### Manuell (vor dem Skript)
1. Git installieren
2. PAT 1 bei GitHub erstellen (Zugriff nur auf AOS-Repo)

### Per Skript (automatisch)
3. AOS-Repo klonen
4. `dialog/`-Unterordner lokal neu anlegen
5. PAT 2 lokal speichern (Umgebungsvariable / `.env`) für späteren Projekt-Clone per Prompt
6. `claude login` aufrufen

### Manuell (nach der Session)
7. PAT 1 bei GitHub widerrufen

### Projekte
Werden **nicht** beim Setup geklont. Stattdessen per Prompt gezielt:
> *"Klone Projekt xyz von GitHub"*

Dafür ist PAT 2 mit Zugriff auf Projekt-Repos nötig.

---

## Alternativer Verteilungsweg: ZIP

Für einmaligen Einsatz auf fremdem Rechner ausreichend:
```powershell
Compress-Archive -Path "C:\Users\sts\AOS" -DestinationPath "C:\Users\sts\AOS.zip"
```
Dann ZIP entpacken, `claude login` — fertig. Kein GitHub-Zugriff nötig.

Nachteil: Keine Versionskontrolle, kein automatisches Update.

---

## Offene Punkte

### 1. Skills
Noch ungeklärt. Laut Konversation sind Skills bei Claude Code und Antigravity unterschiedlich angelegt und vermutlich über Symlinks verknüpft. Fragen:
- Wo liegen die Skill-Definitionen im AOS?
- Gehören sie getrennt pro Agent ins Repo?
- Was muss das Setup-Skript nach dem Klonen tun um Skills zu registrieren?

**Aktion:** Spec-Datei des AOS prüfen und Abschnitt zu Skills hier ergänzen.

### 2. Scripts — Plattformkompatibilität
`scripts/` enthält PowerShell-Skripte (Windows-spezifisch). Verhalten auf Mac/Linux ungeklärt.

**Aktion:** Entscheiden ob plattformübergreifende Varianten nötig sind oder ob Windows-only akzeptabel ist.

### 3. Fehlende Dateien (bekannte Soll-Ist-Abweichung)
Laut README referenziert, aber nicht vorhanden:
- `memory/git-conventions.md`
- `memory/coding-standards.md`
- `scripts/generate_slides.py`
- `scripts/sync_project.py`
- `scripts/dialog-watch.ps1`

**Aktion:** Entweder anlegen oder README bereinigen — vor der GitHub-Migration erledigen.

### 4. Hooks-Registrierung
`block-dangerous.sh` muss nach dem Klonen bei Claude Code als PreToolUse-Hook registriert werden. Noch nicht im Skript-Konzept berücksichtigt.

**Aktion:** In Setup-Skript aufnehmen.
