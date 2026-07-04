# setup-vm.ps1 — Meetily-GLM-Bridge: VM-Deployment
# Registriert den FastAPI-Dienst als Windows Scheduled Task, der beim Systemstart
# (unabhängig von einer interaktiven Anmeldung) automatisch läuft.
#
# Voraussetzungen:
#   - venv unter backend\.venv bereits erstellt (siehe PROJECT.md Setup)
#   - .env im Projekt-Root mit ANTHROPIC_API_KEY/ADMIN_USERNAME/ADMIN_PASSWORD befuellt
#   - DB bereits initialisiert (`python -m app.db init`)

$ErrorActionPreference = "Stop"

# -- Konfiguration ------------------------------------------------------------
$BaseDir   = $PSScriptRoot
$BackendDir = Join-Path $BaseDir "backend"
$Python    = Join-Path $BackendDir ".venv\Scripts\python.exe"
$TaskName  = "MeetilyGLMBridge"
$RunAsUser = $env:USERNAME

# -- Pruefungen -----------------------------------------------------------------
if (-not (Test-Path $Python)) {
    Write-Error "venv nicht gefunden: $Python — zuerst 'python -m venv .venv' + 'pip install -e .[dev]' in backend\ ausfuehren."
    exit 1
}
if (-not (Test-Path (Join-Path $BaseDir ".env"))) {
    Write-Error ".env nicht gefunden unter $BaseDir — zuerst .env.example kopieren und befuellen."
    exit 1
}
if (-not (Test-Path (Join-Path $BaseDir "data\app.db"))) {
    Write-Warning "data\app.db nicht gefunden — 'python -m app.db init' vor erstem Start ausfuehren."
}

# -- Task-Aktion ----------------------------------------------------------------
$ActionArgs = @{
    Execute          = $Python
    Argument         = "-m uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000"
    WorkingDirectory = $BackendDir
}
$Action = New-ScheduledTaskAction @ActionArgs

# -- Trigger: bei Systemstart -----------------------------------------------------
$Trigger = New-ScheduledTaskTrigger -AtStartup

# -- Einstellungen: laeuft dauerhaft, startet bei Absturz neu ---------------------
$SettingsArgs = @{
    ExecutionTimeLimit         = [TimeSpan]::Zero
    RestartCount               = 3
    RestartInterval            = New-TimeSpan -Minutes 1
    StartWhenAvailable         = $true
    AllowStartIfOnBatteries    = $true
    DontStopIfGoingOnBatteries = $true
}
$Settings = New-ScheduledTaskSettingsSet @SettingsArgs

# -- Principal: laeuft als aktueller Nutzer, auch ohne aktive Anmeldung (S4U) -----
$PrincipalArgs = @{
    UserId   = $RunAsUser
    LogonType = "S4U"
    RunLevel  = "Limited"
}
$Principal = New-ScheduledTaskPrincipal @PrincipalArgs

# -- Registrieren (idempotent) ----------------------------------------------------
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Task '$TaskName' existiert bereits — wird aktualisiert."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$RegisterArgs = @{
    TaskName  = $TaskName
    Action    = $Action
    Trigger   = $Trigger
    Settings  = $Settings
    Principal = $Principal
    Force     = $true
}
Register-ScheduledTask @RegisterArgs | Out-Null

Write-Host "Task '$TaskName' registriert."
Write-Host "  Startet automatisch beim naechsten Systemstart als $RunAsUser."
Write-Host "  Bindet an 0.0.0.0:8000 (netzwerkweit erreichbar)."
Write-Host ""
Write-Host "Manueller Start/Stop/Test:"
Write-Host "  schtasks /run /tn $TaskName"
Write-Host "  schtasks /end /tn $TaskName"
Write-Host "  schtasks /query /tn $TaskName /v /fo list"
