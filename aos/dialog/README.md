# AOS Agent-Dialog

Asynchroner Kommunikationskanal zwischen Claude Code (CC) und Antigravity (AG).
Ermöglicht strukturierte Diskussionen zwischen den Agents — mit oder ohne User.

---

## Protokoll

Jedes Thema bekommt einen Unterordner:

```
dialog/<thema>/
├── status.md        ← Steuerungsdatei
├── from-claude.md   ← CC schreibt hier
└── from-ag.md       ← AG schreibt hier
```

### status.md Format

```
status: waiting-for-claude | waiting-for-ag | done
max_rounds: 10
current_round: 1
started: YYYY-MM-DD
topic: Kurzbeschreibung des Themas
```

### Nachrichtenformat (in from-*.md)

```markdown
**[YYYY-MM-DD, Claude Code — Runde N]**

Nachrichtentext...

— Claude Code
```

Nachrichten werden **angehängt** (append), nie überschrieben.

---

## Sicherheits- & Synchronisationsregeln (Asynchroner Betrieb)

Um Race Conditions, Zeichensatz-Konflikte und gegenseitiges Überschreiben zu verhindern, gelten folgende Regeln im asynchronen Betrieb:

1. **Atomare Schreibreihenfolge**:
   * Ein Agent schreibt **zuerst** seinen Beitrag in die entsprechende `from-*.md` Datei und schließt diese.
   * **Erst als allerletzter Schritt** wird die `status.md` Datei aktualisiert und damit das Schreibrecht (Mutex) an den anderen Agenten übergeben.
   * Lesende Agenten reagieren ausschließlich auf den Status-Wechsel in `status.md`. Ein Umschalten des Status vor dem Beenden des Schreibvorgangs ist strikt untersagt.

2. **Status als exklusiver Mutex**:
   * Nur der Agent, der laut `status.md` an der Reihe ist (`waiting-for-claude` bzw. `waiting-for-ag`), hat das Schreibrecht im jeweiligen Dialog-Ordner.
   * Ein Agent darf unter keinen Umständen in einen Thread schreiben, der ihn aktuell nicht adressiert.
   * Ausnahme: Das Erstellen des Dialog-Ordners und der erste Eintrag in `from-*.md` durch den Initiator beim Start.

3. **`status: done` ist terminal (endgültig)**:
   * Sobald ein Dialog den Status `done` erreicht hat, gilt der Thread als permanent geschlossen.
   * Es dürfen keine weiteren Beiträge angehängt und der Status nicht wieder geändert werden.
   * Für neuen Klärungsbedarf muss zwingend ein neuer Thread (neues Thema und neuer Ordner) angelegt werden.

4. **UTF-8 ohne BOM erzwingen**:
   * Alle Dateien (`status.md`, `from-*.md`) müssen zwingend als **UTF-8 ohne BOM (Byte Order Mark)** gespeichert werden, um Parser-Fehler bei CLI-Tools zu vermeiden.
   * Da Windows PowerShell (insb. Version 5.1) standardmäßig UTF-16 oder UTF-8 mit BOM schreibt, ist die Datei-API von .NET zu verwenden:
     ```powershell
     [System.IO.File]::WriteAllText($Path, $Content)
     ```

5. **Eindeutige Runden-Regelung**:
   * Der Rundenzähler `current_round` wird ausschließlich vom **Antwortenden (zweiten Sprecher der Runde)** beim Zurückgeben des Status an den Initiator erhöht.
   * Der Initiator (erste Sprecher der Runde) behält den aktuellen Wert von `current_round` bei, wenn er seinen Beitrag schreibt und den Status übergibt.

---

## Inhaltliche Qualitätsrichtlinien (Debatten-Modus)

Verbindlich für beide Agenten im Dialog. **Single Source of Truth:**
[`memory/debate-mode.md`](../memory/debate-mode.md) — kritische Distanz,
Alternativenprüfung, fünfdimensionale Kriterien-Matrix, Compliance-Gate,
Runden-Dynamik und Stil. Dieser Abschnitt dupliziert die Regeln nicht.
## Claude aufrufen (verbindlich, AG-seitig)

> [!IMPORTANT]
> Claude ist **kein laufender Dienst**, den AG kontaktiert oder „findet". AG **startet Claude
> selbst** als Headless-Prozess. „Claude erreichen" = das `claude`-Executable starten.

Die `claude`-CLI liegt auf diesem System **nicht im PATH**. AG darf den Pfad **nicht hardcoden**
(npx-Cache enthält einen Hash, die Desktop-Installation eine Versionsnummer — beide ändern sich
bei Updates). Stattdessen den Pfad **dynamisch auflösen**:

```powershell
# 1. claude-Pfad robust auflösen (PATH zuerst, dann bekannte Installationsorte, neueste Version)
$claude = (Get-Command claude -ErrorAction SilentlyContinue).Source
if (-not $claude) {
  $claude = Get-ChildItem `
      "$env:LOCALAPPDATA\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude-code\*\claude.exe", `
      "$env:LOCALAPPDATA\npm-cache\_npx\*\node_modules\@anthropic-ai\claude-code\bin\claude.exe" `
      -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending |
      Select-Object -First 1 -ExpandProperty FullName
}

# 2. Claude headless aufrufen — antwortet auf den Dialog und beendet sich selbst
# --tools Read,Edit,Glob,Grep entzieht Claude die Berechtigung fuer Bash/Terminalbefehle (Sandboxing)
& $claude -p "Führe das Skill dialog-reply aus. Thema: <thema>. Du bist Claude Code." `
          --permission-mode bypassPermissions `
          --tools Read,Edit,Glob,Grep
```

**Vorbedingungen vor dem Aufruf (AG stellt sie her):**
1. Ordner `<AOS_ROOT>\dialog\<thema>\` existiert.
2. AGs Beitrag ist an `from-ag.md` angehängt.
3. `status.md` steht auf `status: waiting-for-claude`.

Claude liest dann den Verlauf, schreibt seine Antwort an `from-claude.md`, setzt
`status: waiting-for-ag` und beendet sich. AG übernimmt die nächste Runde.

*(Falls `claude` später dauerhaft in den User-PATH eingetragen wird, genügt Schritt 2 mit
`claude -p ...` direkt — Schritt 1 wird dann übersprungen, ist aber als Fallback unschädlich.)*

---

## Interaktive Chat-Orchestrierung (Hands-off)

Die Steuerung des Dialogs wird direkt von Antigravity aus der aktiven Chat-Session heraus durchgeführt. Es ist kein separates Terminal-Fenster und kein Runner-Skript nötig:

### Ablaufsteuerung

1. **Start:** Der Benutzer gibt Antigravity das Startkommando (z.B. *"Starte einen Dialog mit Claude zum Thema 'X' über 'Y' für 3 Runden."*).
2. **Antigravity startet:** Schreibt den ersten Beitrag in `from-ag.md` und setzt `status: waiting-for-claude`.
3. **Claude Code antwortet:** Antigravity startet Claude im Headless-Modus im Hintergrund —
   Aufruf exakt wie im Abschnitt [Claude aufrufen (verbindlich, AG-seitig)](#claude-aufrufen-verbindlich-ag-seitig)
   (Pfad dynamisch auflösen, **nicht** hardcoden).
   Claude führt das Skill `dialog-reply` aus, schreibt seine Antwort in `from-claude.md` und setzt `status: waiting-for-ag`.
4. **Antigravity antwortet:** Antigravity liest Claudes Antwort ein, formuliert den eigenen Beitrag, hängt ihn an `from-ag.md` an, setzt den Status wieder auf `waiting-for-claude` und startet sofort die nächste Runde.
5. **Ergebnis:** Sobald `max_rounds` erreicht ist, wird `status: done` gesetzt und Antigravity gibt den gesamten Verlauf gesammelt im Chat aus.

> [!NOTE]
> Das alte PowerShell-Skript `dialog-runner.ps1` wurde in das Verzeichnis `scripts/archive/` verschoben.

---

## Von Claude initiierte Dialoge (`__cc_trigger__`)

Claude Code kann eigenständig ein Thema vorschlagen:
1. Erstellt das Verzeichnis `dialog/<thema>/`.
2. Schreibt den Status `status: waiting-for-ag`.
3. Legt eine leere Datei namens `__cc_trigger__` an.

Sobald der Benutzer Antigravity bittet, nach offenen Dialogen zu suchen, liest Antigravity das Thema ein, löscht die Trigger-Datei, schreibt seine Antwort in `from-ag.md` und startet die automatische Hintergrundschleife.

---

## Bisherige Dialoge

| Thema | Runden | Status | Ergebnis |
|---|---|---|---|
| `stufe-2-konzept` | 1 | offen | CC stellt Fragen zu AG-Loop-Mechanismus |
| `uaos-overhead-check` | 3 | done | Lightweight-Modus beschlossen, git-init angepasst |
| `aos-optimierung` | 3 | done | 5 Nachbesserungen vereinbart (Symlink-Default, Fail-Fast-Prüfung, Allowlist-ZIP-Export) |
