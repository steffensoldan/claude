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

if (-not (Test-Path $sourceFile)) {
    # Erstelle ein leeres Template, falls die Datei noch nicht existiert
    New-Item -ItemType File -Path $sourceFile -Value @"
---
name: $CommandName
description: Beschreibung des neuen Befehls.
---

Hier die Logik und Instruktionen für den Befehl.
"@ | Out-Null
    Write-Host "Template fuer '$CommandName.md' erstellt in $aosPath\commands\" -ForegroundColor Yellow
}

# 1. Claude Link erstellen
$claudeLink = "$claudePath\commands\$CommandName.md"
New-Item -ItemType HardLink -Path $claudeLink -Value $sourceFile -Force | Out-Null
Write-Host "Link fuer Claude Code erstellt: $claudeLink" -ForegroundColor Green

# 2. Antigravity Link erstellen
$geminiSkillDir = "$geminiPath\config\plugins\agos-core\skills\$CommandName"
New-Item -ItemType Directory -Path $geminiSkillDir -Force | Out-Null
$geminiLink = "$geminiSkillDir\SKILL.md"
New-Item -ItemType HardLink -Path $geminiLink -Value $sourceFile -Force | Out-Null
Write-Host "Link fuer Antigravity erstellt: $geminiLink" -ForegroundColor Green

Write-Host "Neuer Skill '$CommandName' erfolgreich im AOS registriert!" -ForegroundColor Cyan
