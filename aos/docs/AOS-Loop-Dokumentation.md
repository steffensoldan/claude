# AOS Loop-Engineering — Dokumentation

**Datum:** 2026-06-28
**Repo:** `steffensoldan/AOS`
**Branch:** `loop/aos-optimierung` (Baseline `f9b93a2` → `765e8af`)
**Verfahren:** 6 Runden echter Datei-Loop (lesen → bewerten → editieren → neu einlesen → committen)

---

## 1. Ziel

Iterative Optimierung des AOS auf **realen Dateien**, bewertet aus der Perspektive einer
Coding-KI ohne Vorwissen, bis eine ehrliche 10/10 erreicht ist oder die Rundenobergrenze
greift. Maßgabe: keine Selbstbewertungs-Inflation, Unsicherheit explizit markieren,
keine destruktiven Git-Operationen, kein Push/Merge (Übergabe an den User per PR-Vorschlag).

### Bewertungskriterien (7 gleichwertig, kein Gate)

1. **Identitäts-Klarheit** — in ≤30 s klar: was, für wen, welches Problem.
2. **Anwendbarkeit & Autonomie** — Agent kann nächsten Schritt allein aus den Docs ausführen.
3. **Bindungskraft & Präzedenz** — explizite Geltungs-, Präzedenz- und Done-Regeln.
4. **Konsistenz & Korrektheit (SSOT)** — keine Widersprüche, Redundanzen, toten Verweise,
   defekten Templates, hartkodierten User-Pfade; eine Wahrheitsquelle je Regel.
5. **Übergabefähigkeit** — fremder Agent/Mensch setzt laufenden Stand ohne Vorwissen fort.
6. **Sicherheit & Compliance** — destruktive Aktionen blockiert; Secrets/DSGVO encodiert/erzwungen.
7. **Wartbarkeit & Dokumentation** — Drift-Resistenz, vollständige/aktuelle Doku, Map-Invariante.

Gesamtnote **minimum-orientiert**: solange ein Kriterium < 10, ist die Gesamtnote < 10.

---

## 2. Eingesetzter Prompt (final)

```text
ROLLE
Claude-Code-Agent, automatisiertes Loop-Engineering zur AOS-Optimierung auf REALEN Dateien.

ZIEL
Echte Runden — bewerten → reale Dateien ändern → frisch neu einlesen → neu bewerten →
committen — bis ehrliche 10/10 (Früh-Abbruch) oder MAX_ROUNDS = 6.

SETUP
1. Branch loop/aos-optimierung; main nie direkt ändern.
2. Gesamtes Repo vollständig von Platte lesen; Stand aus Dateien, nicht aus Gedächtnis.

RUBRIC: 7 gleichwertige Kriterien (s. o.), je Stufe 0/2/4/6/8/10 + Begründung. Kein Gate.
Gesamtnote minimum-orientiert.

PRO RUNDE (n = 1..6):
A EINLESEN (frisch von Platte)  B BEWERTEN (frischer Blick)  C LÜCKEN (präzise, mit Grund)
D FIXEN (reale Änderungen, volle Ausimplementierung inkl. PowerShell; Surgical Changes;
  Spec-Statement bei >1 Datei/>20 Zeilen; keine hartkodierten Pfade)
E VERIFIZIEREN (Self-Tests soweit lauffähig; install.ps1 -Verify ist Windows → statisch
  geprüft + ehrlich gemeldet; geänderte Dateien erneut von Platte gegen Lückenliste)
F COMMIT (git add -A && commit; kein push/--force/reset --hard/clean -f)

ANTI-INFLATION
- Note steigt nur, wenn reale Dateiänderung eine benannte Lücke schließt (im Commit nachweisbar).
- Eine 10 nur mit ergebnisloser adversarialer Gegenprüfung (dokumentiert).
- Nichts erfinden; Unsicherheit markieren (gesichert/plausibel/offen).

ABBRUCH
Früh-Abbruch bei 10/10 + leere Lückenliste + ergebnislose Gegenprüfung; sonst nach Runde 6
ehrlich: beste Note, Restlücken, warum keine 10.

OUTPUT (MD, Deutsch): verlauf, bewertung_final, restluecken, pr_vorschlag; geänderte Dateien
als Download. PR nicht selbst öffnen (kein Remote-Zugriff).
STIL: nüchtern, direkt, Bulletpoints, keine Floskeln.
```

---

## 3. Ausgangsbewertung (Baseline)

**4/10** (getrieben von Kriterium 4). Identifizierte Befunde (statisch verifiziert):

- 4 konkurrierende Namen (UAOS / Universal Agentic / Agent Operating System / Agentic …).
- Keine Ein-Satz-Definition, kein mentales Modell, kein Boot-/Quickstart-Vertrag.
- 27 hartkodierte User-Pfade (`C:\Users\sts\…`) in 7 Dateien — Selbstwiderspruch zur
  eigenen Portabilitätsregel.
- Debatten-Modus-Regeln doppelt (`dialog/README.md` + `commands/dialog-reply.md`).
- `task.md` mit defekten Checkboxen (`- [ ] [ ]`, Codeblock-Marker).
- Toter Verweis im Hook auf nicht existenten README-Abschnitt (`settings.json`).
- Setup doppelt/widersprüchlich (Installer vs. manuelle Symlinks; Hardlink vs. Symlink).
- Unvollständige Verzeichnis-Map; leerer MEMORY-Platzhalter; uneinheitliches Datumsformat.

---

## 4. Ablauf je Runde

| Runde | Commit | Geschlossene Lücken | Verifikation |
|---|---|---|---|
| 1 | `9603817` | Naming (15→0), `task.md`-Checkboxen, Datumsformat, MEMORY-Schema | grep 0 Reste |
| 2 | `cf7d219` | README-Rebuild (Definition/Modell/Boot/Quickstart/Glossar/Map), Präzedenzblock, Debatten-SSOT (`memory/debate-mode.md`) + Dedup, Hook-Abschnitt | Dedup-Katalog 1/0/0 |
| 3 | `217083c` | Pfad-Variabilisierung `<AOS_ROOT>`/`$env:AOS_ROOT`, `install.ps1 -Verify`, Hardlink-Konsistenz, `templates/DEVELOPMENT.md`-Anker | 0 reale Pfade |
| 4 | `ae71b6b` | UAOS-Reste in Skripten, Map↔Dateien & Verweise verifiziert | alle Verweise OK |
| 5 | `85eb6ae` | PowerShell-Guardrail, Quickstart-Disambiguierung, Resume-Pointer, Regressionstest | **Guardrail 12/12 runtime-getestet** |
| 6 | `765e8af` | Hook **fail-closed** bei fehlendem `jq` (statt fail-open) + Self-Test-Check | Pattern-Logik grün |

**Methodischer Kernpunkt:** Jede Runde las den Stand frisch von Platte und committete reale
Änderungen — keine „gedachten" Fixes. Die Note durfte nur steigen, wenn ein Commit eine
benannte Lücke nachweislich schloss.

---

## 5. Endergebnis

### Bewertung: **9/10**

| K | Note | Begründung |
|---|---|---|
| 1 Identität | 10 | Ein-Satz-Definition + mentales Modell + Glossar + ein kanonischer Name |
| 2 Anwendbarkeit | 10 | Boot-Vertrag + Agent-/Operator-Quickstart, AOS-Root/Projekt-Root disambiguiert |
| 3 Bindungskraft | 10 | Geltung & Präzedenz + Definition of Done (per `@import`) |
| 4 Konsistenz | **9** | 0 reale Pfade, SSOT, 0 tote Verweise/Template-Defekte — `install.ps1` jedoch im Linux-Container nicht ausführbar (Runtime statisch plausibel, nicht ausgeführt) |
| 5 Übergabe | 10 | Statusblock + Resume-Pointer + realer `DEVELOPMENT.md`-Anker + `PROJECT.md` |
| 6 Sicherheit | 10 | Bash+PowerShell-Guardrail (12/12), fail-closed, auto-`settings.json`, Secret-Gate |
| 7 Wartbarkeit | 10 | MEMORY-Index, Map-Invariante + `-Verify`, Glossar, SSOT-Dedup, Regressionstest |

### Restlücken

- **Blockierend (K4, rein umgebungsbedingt):** `install.ps1` / `install.ps1 -Verify` sind
  PowerShell/Windows und im Linux-Container nicht lauffähig. → **Ein Lauf von
  `install.ps1 -Verify` auf dem Windows-Host schließt den Punkt → erwartete 10/10.**
- **Inhärente Grenze (kein Defekt):** Der Guardrail ist eine Denylist — fängt gängige
  destruktive Muster (getestet), prinzipbedingt aber keine obfuskierten Befehle.

### Geänderte Dateien (17; +509 / −249)

Neu: `memory/debate-mode.md`, `templates/DEVELOPMENT.md`, `hooks/test-block-dangerous.sh`.
Wesentlich überarbeitet: `README.md`, `install.ps1`, `hooks/block-dangerous.sh`,
`templates/task.md`, `SETUP.md`, `memory/global-rules.md`, `memory/MEMORY.md`,
`commands/*`, `dialog/README.md`.

### Artefakte

- `AOS-loop-optimierung.patch` — alle 6 Commits (anwenden via `git am < …patch`).
- `AOS-ueberarbeitet.zip` — vollständiges überarbeitetes Repo.

---

## 6. Verifizierte Tests

| Test | Methode | Ergebnis |
|---|---|---|
| Guardrail destruktiv → blockiert | 7 Fälle (Bash + PowerShell) gegen Pattern-Logik | 7/7 BLOCK |
| Guardrail harmlos → erlaubt | 5 Fälle (ls, git status/push, npm, Einzel-Remove) | 5/5 ALLOW |
| Hartkodierte reale Pfade | grep `C:\Users\sts` | 0 |
| Namens-Konsistenz | grep `UAOS` / `Agent Operating System` | 0 |
| Debatten-SSOT | Hard-Blocker-Katalog je Datei | nur `debate-mode.md` = 1 |
| Datumsformat | grep `JJJJ-MM-TT` | 0 |
| Template-Defekt | grep `- [ ] [ ]` in `task.md` | 0 |

---

## 7. Merge-Empfehlung

1. `powershell .\install.ps1 -Verify` auf dem Windows-Host ausführen (schließt K4).
2. Bei „ALLE PASS": `loop/aos-optimierung` → `main` (Squash oder 6-Commit-Historie erhalten).
3. PR wurde nicht automatisch geöffnet (kein Remote-Zugriff/Credentials — bewusste Grenze).
