# AOS Setup (Fallback): Manuelle Verknüpfung

> **Standardweg ist `install.ps1`** (idempotent, setzt Symlinks/Hardlinks, verdrahtet den Hook,
> registriert Skills, setzt `$env:AOS_ROOT`). Diese Anleitung ist nur der **Fallback**,
> falls der Installer nicht nutzbar ist. Verifikation in beiden Fällen:
> `powershell <AOS_ROOT>\install.ps1 -Verify`.

---

## Voraussetzungen

`<AOS_ROOT>` ist das Wurzelverzeichnis dieses Repos. Hardlinks benötigen **keinen**
Entwicklermodus und keine Administratorrechte (Quelle und Ziel auf demselben Laufwerk).

---

## Einrichtung der Links (Hardlinks, konsistent mit install.ps1)

In einer **PowerShell-Konsole** ausführen:

```powershell
# 0. AOS_ROOT setzen (an euren Pfad anpassen)
$env:AOS_ROOT = "C:\Users\<user>\AOS"

# 1. Commands verknüpfen (alle .md im commands-Ordner)
Get-ChildItem "$env:AOS_ROOT\commands" -Filter *.md | ForEach-Object {
    New-Item -ItemType HardLink -Path "$HOME\.claude\commands\$($_.Name)" -Value $_.FullName -Force | Out-Null
}

# 2. Safety-Hook verknüpfen
New-Item -ItemType HardLink -Path "$HOME\.claude\hooks\block-dangerous.sh" `
         -Value "$env:AOS_ROOT\hooks\block-dangerous.sh" -Force | Out-Null
```

*Hinweis: Neue Skills über `add-skill.ps1` werden standardmäßig per Symlink verknüpft.*
*Den PreToolUse-Hook in `~/.claude/settings.json` siehe README Abschnitt 3.*
