**[2026-06-30 10:30, Claude Code — Runde 1]**

Danke für die strukturierte Analyse. Zwei inhaltliche Korrekturen, bevor ich die Fragen beantworte.

---

### Kritik an der Antigravity-Analyse (Harmonie-Filter)

Antigravity deklariert "keine Einwände gegen eine Übernahme" — in Runde 1 ist das ein Regelverstoß gegen die Debatten-Anforderungen dieses Formats. Ich führe daher die fehlende Risikoanalyse nach.

**Schwachstelle 1 — Hardlinks unter Windows (direkte Antwort auf Frage 1):**

Hardlinks auf NTFS sind inode-gebunden. Wenn Claude Code bei einem Update eine Konfigurationsdatei *ersetzt* statt in-place überschreibt (auf Windows der Normalfall für atomare Datei-Writes), entsteht ein neuer inode. Der Hardlink zeigt dann weiterhin auf den alten Dateistand — ohne Fehlermeldung, ohne sichtbaren Unterschied. Ergebnis: AOS-Konfiguration ist lautlos veraltet.

Der `-Verify`-Modus prüft derzeit nur die Existenz von Symlinks/Hardlinks, nicht ihre Inhaltskonsistenz gegenüber der Quelle. Das schließt den Drift nicht aus.

**Alternative zu Hardlinks:** Symlinks (`New-Item -ItemType SymbolicLink`) sind das sicherere Instrument: Sie dereferenzieren beim Lesen transparent zur aktuellen Zieldatei, auch nach einem Update-Replace. Nachteil: erfordert Developer Mode oder erhöhte Rechte auf Windows. Bewerteter Trade-off: Symlinks sind hier der bessere Default; Hardlinks nur als Fallback, wenn Symlinks fehlschlagen — mit explizitem Log-Eintrag.

**Schwachstelle 2 — SSOT `memory/debate-mode.md` ohne Fallback:**

Wenn die Datei fehlt oder beschädigt ist, entfällt die Kriterienmatrix lautlos. Ein einfacher Existenz-Check mit Abbruch bei Fehler fehlt im Befehlsparser. Das ist wartbar, aber fragil.

---

### Antwort auf Frage 2 — Restrisiken nach 6 Runden Loop-Engineering

Drei offene Punkte:

1. **PowerShell 5.1 vs. 7+ Kompatibilität in `install.ps1`**: Die letzten Commits (u.a. `46792b2`) haben PS-5.1-Probleme behoben, aber ein systematischer Kompatibilitätstest auf einer reinen PS-5.1-Umgebung fehlt noch. Gefährdete Konstrukte: `$PSEdition`-Guards, `New-Item`-Optionssets, `Write-Host`-Farbcodes.

2. **Zeichensatz-Risiko**: UTF-8 ohne BOM ist korrekt spezifiziert, aber nicht erzwungen. `install.ps1` nutzt noch einige `Out-File`-Aufrufe ohne expliziten `-Encoding UTF8`-Parameter. Auf älteren Windows-Locales mit CP1252-Default kann das zu Encoding-Drift in `.md`-Dateien führen.

3. **Fehlende Regressionsprüfung für `export-aos.ps1`**: Das Skript exportiert ohne Secret-Inhalte, aber es gibt keinen Test, der verifiziert, dass `.env`-Dateien oder Token-haltiger Content im ZIP nicht landen.

---

### Kriterienmatrix

| Dimension | Bewertung | Anmerkung |
|---|---|---|
| **Sicherheit** | GUT | Fail-closed Hook korrekt; keine Netzwerkabhängigkeiten |
| **Robustheit** | MITTEL | Hardlink-Drift-Risiko; fehlende Encoding-Erzwingung |
| **Wartbarkeit** | GUT | SSOT debate-mode.md sinnvoll; Fallback fehlt |
| **Usability** | GUT | `-Verify`-Modus wertvoll für Onboarding |
| **Compliance (Gate)** | BESTANDEN | Keine Cloud-Schnittstellen, keine Lizenzkonflikte, kein Online-Zwang |

---

### Empfehlung vor Merge

Drei Nachbesserungen mit geringem Aufwand:

1. Hardlinks in `install.ps1` durch Symlinks ersetzen (primär); Hardlink als expliziter Fallback mit Log.
2. `Out-File`-Aufrufe in `install.ps1` auf `-Encoding UTF8NoBOM` vereinheitlichen.
3. `export-aos.ps1`: Negativtest ergänzen — prüft, dass `*.env`, `*token*`, `*secret*` nicht im ZIP landen.

Konsens in Runde 1 wäre verfrüht. Ich empfehle Runde 2 für Antigravitys Gegenposition zu den Hardlink-Alternativen.

— Claude Code

**[2026-06-30 11:00, Claude Code — Runde 2]**

### Gegenprüfung der Antigravity-Vorschläge (Runde 2)

**Vorschlag 1 — Hardlink-Drift: Hash-Vergleich in `-Verify`**

Architektonisch korrekt. Zwei Präzisierungen:

- `Get-FileHash` in PS 5.1 hält kurzzeitig ein Lese-Handle auf die Zieldatei. Bei Dateien, die gleichzeitig von Claude Code im Hintergrund gelesen werden (z.B. `settings.json` zur Laufzeit), entsteht ein Locking-Risiko. Alternative: Byte-Vergleich über `[System.IO.File]::ReadAllBytes()` — kein dauerhaftes Handle, kein Blockierungs-Fenster.
- **Strukturelles Gegenargument zum Ansatz:** Drift-Erkennung im `-Verify`-Modus ist reaktiv. Ein Fail-Fast-Mechanismus *während* des Installs (Konsistenzprüfung als letzter Schritt von `install.ps1`) schließt das Drift-Fenster zwischen Install und Verify-Aufruf. Empfehlung: Beide Ebenen, nicht nur Verify.

**Vorschlag 2 — `$PSEdition`-Guard und `.NET`-Encoding**

Antigravity fragt, ob `$PSEdition` auf PS 5.1 zuverlässig ausgewertet wird. Antwort: In PS 5.1 RTM ist `$PSEdition` als `'Desktop'` definiert — aber in frühen 5.0-Builds und inoffiziellen Repacks ist die Variable leer oder `$null`. Zuverlässigere Alternative:

```powershell
if ($PSVersionTable.PSVersion.Major -ge 7) { ... }
```

`.NET`-Schreibmethode (`[System.IO.File]::WriteAllText` mit `[System.Text.UTF8Encoding]::new($false)`) ist korrekt. Schwachstelle: Wenn der Aufruf an fünf Stellen in `install.ps1` vorkommt, wächst die Fehleranfälligkeit bei Wartung. Empfehlung: Einen zentralen Helper definieren:

```powershell
function Write-Utf8NoBom {
    param([string]$Path, [string]$Content)
    [System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))
}
```

Einmalig in `install.ps1` definiert, überall verwendet — kein Copy-Paste-Risiko.

**Vorschlag 3 — ZIP-Integritätsprüfung: Denylist zu eng**

Antigravitys Muster `*.env`, `*token*`, `*secret*` sind ein Denylist-Ansatz mit vorhersehbaren Lücken: `.env.local`, `credentials.json`, `*.pem`, `*.key`, `*.pfx` würden ungeprüft exportiert. Ein neues Secret-Format macht den Check blind.

**Gegenentwurf — Allowlist statt Denylist:**

```powershell
$allowedExtensions = @('.md', '.ps1', '.sh', '.json', '.txt', '.yaml', '.example')
# Alles außerhalb dieser Liste wird vor dem Packen explizit geblockt
```

Overhead: minimal. Schutz: vollständig gegen unbekannte Secret-Formate. Neue Dateitypen müssen aktiv freigegeben werden — das ist die sicherere Default-Haltung.

### Kriterienmatrix (Antigravity Runde 2)

| Dimension | Bewertung | Anmerkung |
|---|---|---|
| **Sicherheit** | GUT | Hash-Verify und ZIP-Check schliessen zwei echte Angriffsflächen |
| **Robustheit** | MITTEL | Get-FileHash Locking-Risiko; Denylist-Ansatz strukturell fragil |
| **Wartbarkeit** | GUT | `.NET`-Wrapper sinnvoll — muss aber als Helper zentralisiert werden |
| **Usability** | GUT | Kein Mehraufwand für den Endnutzer; Fehlermeldungen werden klarer |
| **Compliance (Gate)** | BESTANDEN | Kein Online-Zwang, keine proprietären Lizenzen, kein Datenabfluss |

### Stand vor Runde 3

Drei Punkte brauchen in der Abschlussrunde eine Entscheidung:

1. **`$PSVersionTable.PSVersion.Major` vs. `$PSEdition`** — Einigung auf einen Standard, der in die Codebasis eingetragen wird.
2. **Allowlist vs. Denylist in `export-aos.ps1`** — Gegenentwurf liegt vor; Antigravity hat Gegenposition noch nicht eingenommen.
3. **`Write-Utf8NoBom`-Helper: Scope** — Inline in `install.ps1` oder als separates Utility-Modul? Entscheidung bestimmt, ob andere Skripte (`export-aos.ps1`) davon profitieren.

Kein Konsens in Runde 2 — regelkonform. Alle drei Punkte sind lösbar, ohne den Scope der Branch-Optimierungen zu sprengen.

— Claude Code