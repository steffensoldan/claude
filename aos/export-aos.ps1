# export-aos.ps1 - Erstellt das saubere ZIP-Archiv fuer die VM-Installation
$ErrorActionPreference = 'Stop'

$SourcePath = $PSScriptRoot
$ExportPath = Join-Path (Split-Path $PSScriptRoot -Parent) "AOS-export.zip"


Write-Host "=== Erstelle AOS Export-Paket ===" -ForegroundColor Cyan

# 1. Sicherheits- und Integritätsprüfung vor ZIP-Export
$secretPatterns = @("*.env", "*.env.*", "secrets.json", "credentials.json", "*.key", "*.pem")
$safeExceptions = @("\.example$", "\.template$", "\.sample$")

function Test-IsException([string]$path) {
    foreach ($p in $safeExceptions) { if ($path -match $p) { return $true } }
    return $false
}

# Tracked Secrets Check
$trackedSecrets = foreach ($pat in $secretPatterns) {
    git -C $SourcePath ls-files $pat 2>$null | Where-Object { -not (Test-IsException $_) }
}
# Untracked Secrets Check
$untrackedSecrets = git -C $SourcePath ls-files --others --exclude-standard 2>$null | Where-Object {
    ($_ -match "\.env(\.|$)|secrets\.json|credentials\.json|\.key$|\.pem$") -and
    -not (Test-IsException $_)
}

if ($trackedSecrets -or $untrackedSecrets) {
    Write-Error "ABORT: Kritische Secrets-Dateien im Repositories-Pfad gefunden!"
    $trackedSecrets   | ForEach-Object { Write-Error "  [TRACKED IN GIT] $_" }
    $untrackedSecrets | ForEach-Object { Write-Error "  [UNTRACKED]      $_" }
    exit 1
}

# .gitignore Validierungs-Check
$gitignorePath = Join-Path $SourcePath ".gitignore"
if (-not (Test-Path $gitignorePath)) {
    Write-Error "ABORT: Keine .gitignore im Stammverzeichnis vorhanden."
    exit 1
}
$gitignoreContent = Get-Content $gitignorePath -Raw
$requiredPatterns = @(".env", "*.key", "*.pem", "secrets.json")
$missing = $requiredPatterns | Where-Object { $gitignoreContent -notmatch [regex]::Escape($_) }
if ($missing) {
    Write-Warning "Sicherheits-Lücke in .gitignore! Folgende Einträge fehlen: $($missing -join ', ')"
}
Write-Host "Secrets-Scan & gitignore-Prüfung: OK" -ForegroundColor Green

# 1.5 Validierung verschachtelter CLAUDE.md auf relative Pfad-Hop-Verstöße (Option C+A)
Write-Host "Prüfe verschachtelte CLAUDE.md auf Pfad-Hops..." -ForegroundColor Cyan
$nestedClaudes = Get-ChildItem -Path $SourcePath -Recurse -Filter "CLAUDE.md" -ErrorAction SilentlyContinue |
    Where-Object { $_.DirectoryName -ne $SourcePath -and $_.DirectoryName -ne "$HOME\.claude" }

foreach ($file in $nestedClaudes) {
    $content = Get-Content $file.FullName -Raw
    if ($content -match "@\.\./") {
        Write-Warning "WARNUNG: Relative Pfad-Hop-Direktive in verschachtelter CLAUDE.md gefunden:"
        Write-Warning "  $($file.FullName)"
        Write-Warning "  Bitte vermeiden Sie relative Imports mit '../' in Sub-Projekten (Option C+A)."
        Write-Warning "  Nutzen Sie stattdessen die Vererbung oder erstellen Sie separate Rules ohne relative Hops."
    }
}


# Temporaeres Verzeichnis fuer sauberen ZIP-Build
$TempPath = Join-Path $env:TEMP "AOS_Export_Temp"
if (Test-Path $TempPath) { 
    Remove-Item -Recurse -Force $TempPath 
}
New-Item -ItemType Directory -Path $TempPath | Out-Null

# Kopiere nur relevante Ordner
$FoldersToCopy = @("memory", "templates", "commands", "hooks", "scripts", "dialog", "ops")
foreach ($folder in $FoldersToCopy) {
    if (Test-Path "$SourcePath\$folder") {
        Copy-Item -Path "$SourcePath\$folder" -Destination "$TempPath\$folder" -Recurse -Force
        Write-Host "Kopiert Ordner: $folder" -ForegroundColor Gray
    }
}

# Root-Dateien kopieren
$FilesToCopy = @("README.md", "SETUP.md", ".gitignore", "install.ps1", "MOBILE.md", "CLAUDE.md")
foreach ($file in $FilesToCopy) {
    if (Test-Path "$SourcePath\$file") {
        Copy-Item -Path "$SourcePath\$file" -Destination "$TempPath\$file" -Force
        Write-Host "Kopiert Datei: $file" -ForegroundColor Gray
    }
}


# Globale CLAUDE.md auslesen und einpacken
$claudeGlobal = "$env:USERPROFILE\.claude\CLAUDE.md"
if (Test-Path $claudeGlobal) {
    $claudeDestDir = Join-Path $TempPath ".claude"
    New-Item -ItemType Directory -Path $claudeDestDir -Force | Out-Null
    Copy-Item -Path $claudeGlobal -Destination (Join-Path $claudeDestDir "CLAUDE.md") -Force
    Write-Host "Kopiert globale CLAUDE.md" -ForegroundColor Gray
}

# Dialog-Unterordner (bis auf README.md) loeschen, um Privatsphaere zu wahren
if (Test-Path "$TempPath\dialog") {
    Get-ChildItem -Path "$TempPath\dialog" -Directory | Remove-Item -Recurse -Force
    Write-Host "Laufende Dialog-Threads entfernt." -ForegroundColor Gray
}

# Archivieren
if (Test-Path $ExportPath) { 
    Remove-Item -Force $ExportPath 
}
Compress-Archive -Path "$TempPath\*" -DestinationPath $ExportPath -Force

# Aufraeumen
Remove-Item -Recurse -Force $TempPath

Write-Host "AOS erfolgreich als ZIP exportiert nach: $ExportPath" -ForegroundColor Green
Write-Host "=== Export abgeschlossen ===" -ForegroundColor Cyan
