# AOS — Agentic Operating System

**AOS ist die Single Source of Truth für zwei Coding-Agenten — Claude Code und
Antigravity (Googles agentische IDE) — die sich auf einem Windows-System ein Projekt
teilen.** Es koordiniert sie über ein gemeinsames Dateisystem: kein Server, kein Dienst —
das Repo *ist* der Kommunikationskanal. Regeln, Templates, Commands, Hooks und der
Agent-Dialog liegen als Dateien vor; jeder Agent liest und schreibt sie nach festem Protokoll.

> Pfad-Konvention: `<AOS_ROOT>` ist das Wurzelverzeichnis dieses Repos. Die PowerShell-Skripte
> setzen `$env:AOS_ROOT` automatisch. In Beispielen steht `<AOS_ROOT>` als Platzhalter —
> keine hartkodierten Benutzerpfade. Ein konkretes Beispiel: `<AOS_ROOT>` = `C:\Users\<user>\AOS`.

---

## Mentales Modell (30 Sekunden)

- **Akteure:** Claude Code (CLI, textbasiert, **kein sessionübergreifendes Gedächtnis**) und
  Antigravity (agentische IDE). Beide laden dieselben globalen Regeln.
- **Bus:** das gemeinsame Dateisystem. Übergabe = Datei schreiben + Status setzen.
- **Gedächtnis (3 Schichten, Präzedenz absteigend):** laufende User-Anweisung →
  Projekt-`CLAUDE.md` (nur Abweichungen) → `memory/global-rules.md` (global, bindend).
  Laufender Stand: Statusblock in `task.md`.
- **Spec-First:** kein Code ohne `PROJECT.md` + `implementation_plan.md`.

---

## Agent-Quickstart (wenn du eine KI bist und hier aufwachst)

1. Lies `memory/global-rules.md` — diese Regeln sind in **jeder** Session bindend.
2. **Verorte dich:** Bist du im AOS-Masterverzeichnis (`<AOS_ROOT>`), gilt `CLAUDE.md` +
   `memory/`. Bist du in einem Projekt unter `projects/…`, lies dort `PROJECT.md` (was ist
   das Projekt) und den Statusblock in `task.md` (**wo stehe ich, was ist der nächste Schritt**).
3. Arbeite ausschließlich an Dateien im aktuellen Task-Scope (Surgical Changes).
4. Vor Übergabe: Tests grün, Git sauber, Statusblock in `task.md` aktualisiert.

> **Wiederaufsetzen (Resume):** Der Statusblock in `task.md` ist der einzige verbindliche
> Wiederaufsetzpunkt. Nie aus dem Gedächtnis fortfahren — immer zuerst den Statusblock lesen.

## Operator-Quickstart (Mensch, neues System)

1. `powershell <AOS_ROOT>\install.ps1` — einziger autoritativer Setup-Pfad (idempotent).
2. `powershell <AOS_ROOT>\install.ps1 -Verify` — Self-Test (Links, Hook, Commands).
3. Manuelle Alternative (nur falls Installer nicht nutzbar): siehe [SETUP.md](SETUP.md).

---

## 1. Verzeichnisstruktur (vollständig)

```text
<AOS_ROOT>\                          ← AOS-Masterverzeichnis (SSOT)
│
├── README.md                        ← Diese Einstiegs- und Orientierungsdatei
├── CLAUDE.md                        ← Workspace-Regeln für Claude Code (lädt global-rules)
├── SETUP.md                         ← Fallback: manuelle Verknüpfung (sonst install.ps1)
├── MOBILE.md                        ← Mobile-Dispatcher (Handy ↔ VM) inkl. Compliance-Gate
├── install.ps1                      ← Installer/Updater + Self-Test (-Verify)
├── export-aos.ps1                   ← Secret-freies ZIP-Paket für VM/Migration
│
├── memory\                          ← Geteiltes Langzeitgedächtnis & Standards
│   ├── MEMORY.md                    ← Index aller Memory-Dateien
│   ├── global-rules.md             ← Globale, bindende Arbeitsanweisungen
│   └── debate-mode.md              ← SSOT: Bewertungsmatrix & Compliance-Gate (Dialog)
│
├── templates\                       ← Geteilte Dateischablonen
│   ├── PROJECT.md                   ← Projekt-Metadaten & Tech-Stack (Zero-Context-Start)
│   ├── implementation_plan.md       ← Technische Spezifikation (Spec-First)
│   ├── task.md                      ← Aufgabenliste mit Statusblock
│   ├── walkthrough.md               ← Änderungs- & Testdokumentation
│   └── GOVERNANCE.md                ← Lifecycle, IP, Risiko, TCO, Barrierefreiheit
│
├── commands\                        ← Slash-Commands für Claude Code (Master)
│   ├── sync.md                      ← Sicherer Git-Sync-Zyklus
│   ├── git-init.md                  ← Lightweight-Projektinitialisierung
│   ├── entscheidungsvorlage.md      ← Entscheidungstaugliche Vorlage
│   ├── zew-praesentation.md         ← ZEW-PPTX im Corporate Design
│   └── dialog-reply.md              ← Antwort im Agent-Dialog
│
├── dialog\                          ← Agent-zu-Agent-Kommunikationskanal
│   ├── README.md                    ← Protokoll & Nutzungsanleitung
│   └── <thema>\                     ← Pro Thema: status.md, from-claude.md, from-ag.md
│
├── hooks\                           ← Sicherheits-Hooks für Claude Code
│   ├── block-dangerous.sh           ← PreToolUse-Guardrail gegen destruktive Befehle (Bash + PowerShell)
│   └── test-block-dangerous.sh      ← Regressionstest der Guardrail-Muster
│
├── scripts\                         ← Geteilte Automatisierung (PowerShell)
│   ├── add-skill.ps1                ← Neuen Command/Skill für beide Clients registrieren
│   └── pptx-to-png.ps1              ← PPTX → PNG (visuelle QA, PowerPoint-COM)
│
├── ops\                             ← Deployment & Betrieb
│   └── deploy.ps1                   ← Projekt-Deploy nach deploy-manifest.json
│
├── projects\                        ← Aktive Projekt-Workspaces (von install.ps1 angelegt)
│   ├── Projekte-Claude\             ← primär Claude Code
│   └── Projekte-Antigravity\        ← primär Antigravity
│
└── live\                            ← Deploy-Ziele/Manifeste (von ops/deploy.ps1 genutzt)
```

> **Konsistenz-Invariante:** Jede versionierte Datei steht in dieser Map, und jeder
> Map-Eintrag existiert real. `install.ps1 -Verify` prüft das.

---

## 2. Glossar

- **Antigravity:** Googles agentische IDE/Harness; zweiter Coding-Agent neben Claude Code.
- **Claude Code:** Anthropics CLI-Agent; textbasiert, ohne sessionübergreifendes Gedächtnis.
- **SSOT (Single Source of Truth):** genau eine maßgebliche Quelle je Regel/Information.
- **Spec-First:** Spezifikation (`PROJECT.md`, `implementation_plan.md`) vor Implementierung.
- **Statusblock:** Kopf von `task.md` (zuletzt/nächster Schritt/Blockaden) — Wiederaufsetzpunkt.
- **Headless-Modus:** Claude wird als Hintergrundprozess gestartet, antwortet, beendet sich.
- **Mutex (im Dialog):** `status.md` vergibt das exklusive Schreibrecht im Thema-Ordner.
- **`__cc_trigger__`:** leere Markerdatei, mit der Claude Code einen Dialog initiiert.
- **Bus-Faktor:** Anzahl Personen, deren Ausfall das Projekt stoppt (Übergabe-Risiko).
- **Surgical Changes:** nur task-relevante Dateien ändern, keine kosmetischen Eingriffe.

---

## 3. Setup & Sicherheits-Hook aktivieren

Standard: `powershell <AOS_ROOT>\install.ps1` legt Links idempotent an, registriert den
Guardrail-Hook und führt eine Secret-Integritätsprüfung durch. Verifikation mit
`install.ps1 -Verify`. Manuelle Alternative: [SETUP.md](SETUP.md).

Den PreToolUse-Guardrail (`hooks/block-dangerous.sh`) in `~/.claude/settings.json` verdrahten
(von `install.ps1` automatisch gesetzt; hier zur Nachvollziehbarkeit):

```jsonc
// ~/.claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [
          { "type": "command",
            "command": "bash <AOS_ROOT>/hooks/block-dangerous.sh" }
        ] }
    ]
  }
}
```

---

## 4. Integration in Antigravity

Antigravity lädt die globalen Regeln über eine `DEVELOPMENT.md` im Projekt-Root, die auf
`<AOS_ROOT>/memory/global-rules.md` verweist (Vorlage: `templates/DEVELOPMENT.md`).
Wrapper-Skills unter `~/.gemini/config/plugins/agos-core/skills/` verbinden die globalen
Konventionen mit den lokalen Skripten in `<AOS_ROOT>/scripts/`.

---

## 5. Spezifikationsgetriebenes Arbeiten (Spec-Driven)

Standard-Dateiset im Projekt-Root beim Tool-Wechsel:

1. **`PROJECT.md`** — Projekt tool-neutral (Ziel, Stack, Pfade, Testbefehle).
2. **`implementation_plan.md`** — technische Spezifikation und Architekturfragen.
3. **`task.md`** — Aufgabenliste (GFM-Checkboxen) mit verpflichtendem Statusblock.
4. **`walkthrough.md`** — Zusammenfassung von Codeänderungen und Testergebnissen.

### Verpflichtender Statusblock (`task.md`)

Vor jeder Übergabe pflegen, da **Claude Code kein sessionübergreifendes Gedächtnis besitzt**:

```markdown
## Aktueller Stand
Zuletzt bearbeitet: YYYY-MM-DD durch [Claude Code | Antigravity]
Letzter abgeschlossener Schritt: [Beschreibung]
Nächster Schritt: [Beschreibung]
Offene Fragen / Blockaden: [Beschreibung oder "Keine"]
```

---

## 6. Arbeitsaufteilung (Single-Client-Strategie)

- Jedes Projekt wird primär von **einem** Client bearbeitet (Merge-Konflikte/Ressourcensperren vermeiden):
  - `<AOS_ROOT>\projects\Projekte-Claude\` (primär Claude Code)
  - `<AOS_ROOT>\projects\Projekte-Antigravity\` (primär Antigravity)
- Übergabe an das andere Tool nur an expliziten **Meilensteinen**.
- **Übergabe-Regel:** vorher alles committet (sauberer Git-Status), gepusht, Statusblock aktualisiert.

---

## 7. Neue Skills (`add-skill.ps1`)

```powershell
powershell <AOS_ROOT>\scripts\add-skill.ps1 -CommandName "name-des-neuen-skills"
```

1. Erstellt (falls nötig) `<AOS_ROOT>\commands\name-des-neuen-skills.md`.
2. Verknüpft die Datei für Claude Code (`~/.claude/commands/`).
3. Legt Struktur + Verknüpfung für Antigravity (`agos-core/skills/.../SKILL.md`) an.

Verknüpfungsart standardmäßig **Symbolic Links** (mit automatischem Fallback auf **Hardlinks**, falls Berechtigungen fehlen) — konsistent mit `install.ps1`.

---

## 8. Agent-zu-Agent-Kommunikation (`dialog\`)

Claude Code und Antigravity kommunizieren asynchron über `dialog\`. Start per Textbefehl in
Antigravitys Chat; der Dialog läuft im Hintergrund; nach Abschluss wird der Verlauf
ausgegeben. Protokoll, Status-Mutex und der Debatten-Modus: [dialog/README.md](dialog/README.md).
Inhaltliche Qualitätsregeln (SSOT): [memory/debate-mode.md](memory/debate-mode.md).

---

## 9. Versionskontrolle & Wartung (Git)

Das gesamte AOS-Masterverzeichnis wird per Git versioniert — Schutz vor Fehlkonfiguration
durch Agenten und lückenlose Historie aller Regel-, Befehls- und Skriptänderungen.

**Wartung des AOS selbst:**
- Änderungen an Regeln/Commands/Skripten laufen über einen Branch (`git switch -c …`),
  nie direkt auf `main`.
- Nach jeder strukturellen Änderung: `install.ps1 -Verify` ausführen (Map-Invariante,
  Links, Hook, keine hartkodierten Pfade).
- Neue Memory-Regeln nur über `/remember` in `memory/global-rules.md`; neuer Index-Eintrag
  in `memory/MEMORY.md`. Eine Regel = eine Quelle (SSOT), keine Duplikate.
