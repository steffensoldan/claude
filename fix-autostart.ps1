# fix-autostart.ps1 — Bereinigt verwaisten Registry-Eintrag und registriert Scheduled Task neu
# Alle Pfade hardcoded, damit $PSScriptRoot-Probleme bei elevated Ausfuehrung nicht auftreten.

$ErrorActionPreference = "Stop"

$TaskName   = "MeetilyGLMBridge"
$BaseDir    = "C:\Users\sts\AOS\projects\Projekte-Claude\meetily-glm-bridge"
$BackendDir = "$BaseDir\backend"
$Python     = "$BackendDir\.venv\Scripts\python.exe"
$RegistryPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\$TaskName"

# ---- Sanity checks ---------------------------------------------------------------
if (-not (Test-Path $Python)) {
    Write-Error "Python-venv nicht gefunden: $Python"
    Write-Host "Druecke eine Taste zum Schliessen."
    [Console]::ReadKey() | Out-Null
    exit 1
}

# ---- Registry-Eintrag loeschen (falls vorhanden) --------------------------------
if (Test-Path $RegistryPath) {
    Write-Host "Verwaisten Registry-Eintrag loeschen..."
    Remove-Item -Path $RegistryPath -Recurse -Force
    Write-Host "Erledigt."
} else {
    Write-Host "Registry-Eintrag nicht vorhanden (kein Aufraeum-Bedarf)."
}

# ---- Vorhandenen Task entfernen (falls vorhanden) --------------------------------
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Bestehenden Task '$TaskName' entfernen..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# ---- Task direkt registrieren (ohne setup-vm.ps1, ohne $PSScriptRoot) -----------
$Action = New-ScheduledTaskAction `
    -Execute $Python `
    -Argument "-m uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000" `
    -WorkingDirectory $BackendDir

$Trigger  = New-ScheduledTaskTrigger -AtStartup

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType S4U `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Force | Out-Null

Write-Host ""
Write-Host "Task '$TaskName' registriert."
Write-Host "  Python: $Python"
Write-Host "  Startet automatisch beim naechsten Systemstart als $env:USERNAME."
Write-Host "  Erreichbar unter http://192.168.70.143:8000"
Write-Host ""
Write-Host "Druecke eine Taste zum Schliessen."
[Console]::ReadKey() | Out-Null
