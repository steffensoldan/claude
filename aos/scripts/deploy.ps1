#Requires -Version 7
param(
    [Parameter(Mandatory)][string]$Project,
    [string]$LiveRoot    = (Join-Path (Split-Path $PSScriptRoot -Parent) "live"),
    [string]$ProjectRoot = (Join-Path (Split-Path $PSScriptRoot -Parent) "projects")

)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectPath = Join-Path $ProjectRoot $Project
$manifestPath = Join-Path $LiveRoot $Project "deploy-manifest.json"

if (-not (Test-Path $projectPath)) {
    Write-Error "ABORT: Projektpfad $projectPath nicht gefunden."
    exit 1
}

# Standard-Konvention (z. B. für Wisskomm-Viz)
$syncRules = @(
    @{ source = "dist"; target = "dist"; mode = "mirror" }
)
$container = "aos-$Project"

# Manifest laden falls vorhanden (z. B. für Stirling-PDF mit config/input Volumes)
if (Test-Path $manifestPath) {
    Write-Host "Manifest geladen: $manifestPath"
    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.sync_rules) { $syncRules = $manifest.sync_rules }
    if ($manifest.container) { $container = $manifest.container }
}

# Robocopy-Synchronisation
foreach ($rule in $syncRules) {
    $src = Join-Path $projectPath $rule.source
    $tgt = Join-Path $LiveRoot $Project $rule.target
    
    if (-not (Test-Path $src)) {
        Write-Warning "Quelle $src nicht gefunden. Übersprungen."
        continue
    }
    
    if (-not (Test-Path $tgt)) {
        New-Item -ItemType Directory -Path $tgt -Force | Out-Null
    }
    
    Write-Host "Sync ($($rule.mode)): $src -> $tgt"
    
    if ($rule.mode -eq "mirror") {
        # Spiegelung für Code
        robocopy $src $tgt /MIR /NP /NJS /NJH /LOG+:"$LiveRoot\deploy.log"
    } else {
        # Update-only für Konfigurations- oder Datenverzeichnisse (kein Löschen im Ziel)
        robocopy $src $tgt /E /XC /XN /NP /NJS /NJH /LOG+:"$LiveRoot\deploy.log"
    }
    
    if ($LASTEXITCODE -ge 8) {
        Write-Error "robocopy Fehler (Exit $LASTEXITCODE) bei $src."
        exit 1
    }
}

# Docker-Container Neustart (idempotent)
$running = docker ps --filter "name=^${container}$" --format "{{.Names}}" 2>$null
if ($running -eq $container) {
    Write-Host "Neustart: $container"
    docker restart $container
} else {
    Write-Host "Container $container nicht aktiv - kein Neustart erforderlich."
}


Write-Host "Deploy abgeschlossen: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
