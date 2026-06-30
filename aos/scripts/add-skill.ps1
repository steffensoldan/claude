param(
    [Parameter(Mandatory=$true)]
    [string]$CommandName
)

$ErrorActionPreference = 'Stop'

$aosPath = Split-Path $PSScriptRoot -Parent
$claudePath = "$HOME\.claude"
$geminiPath = "$HOME\.gemini"

# Pfade normalisieren
$sourceFile = "$aosPath\commands\$CommandName.md"

function Write-Utf8NoBom {
    param([string]$Path, [string]$Content)
    [System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))
}

function Create-Link {
    param([string]$LinkPath, [string]$TargetPath)
    if (Test-Path $LinkPath) {
        Remove-Item -Force $LinkPath
    }
    try {
        New-Item -ItemType SymbolicLink -Path $LinkPath -Value $TargetPath -Force | Out-Null
        Write-Host "Link verknuepft (Symlink): $(Split-Path $LinkPath -Leaf)" -ForegroundColor Green
    }
    catch {
        try {
            New-Item -ItemType HardLink -Path $LinkPath -Value $TargetPath -Force | Out-Null
            Write-Warning "WARNUNG: Symlink-Erstellung fehlgeschlagen (Berechtigung?). Nutze Hardlink-Fallback fuer $(Split-Path $LinkPath -Leaf). Drift-Gefahr bei Updates!"
        }
        catch {
            Write-Error "FEHLER: Link-Erstellung fehlgeschlagen fuer $LinkPath: $_"
            throw $_
        }
    }
}

if (-not (Test-Path $sourceFile)) {
    # Erstelle ein leeres Template, falls die Datei noch nicht existiert
    $template = @"
---
name: $CommandName
description: Beschreibung des neuen Befehls.
---

Hier die Logik und Instruktionen für den Befehl.
"@
    Write-Utf8NoBom $sourceFile $template
    Write-Host "Template fuer '$CommandName.md' erstellt in $aosPath\commands\" -ForegroundColor Yellow
}

# 1. Claude Link erstellen
$claudeLink = "$claudePath\commands\$CommandName.md"
Create-Link -LinkPath $claudeLink -TargetPath $sourceFile

# 2. Antigravity Link erstellen
$geminiSkillDir = "$geminiPath\config\plugins\agos-core\skills\$CommandName"
if (-not (Test-Path $geminiSkillDir)) {
    New-Item -ItemType Directory -Path $geminiSkillDir -Force | Out-Null
}
$geminiLink = "$geminiSkillDir\SKILL.md"
Create-Link -LinkPath $geminiLink -TargetPath $sourceFile

Write-Host "Neuer Skill '$CommandName' erfolgreich im AOS registriert!" -ForegroundColor Cyan
