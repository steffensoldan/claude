# setup-vm.ps1 — GitHub Trend Monitor: VM-Deployment
# Registriert den Collector als täglichen Windows Scheduled Task.
# Ausführen als AI-Admin auf dem Server.

$ErrorActionPreference = "Stop"

$BaseDir   = "C:\AI-Tools\claude\github-trend-monitor"
$Script    = "$BaseDir\trend_monitor.py"
$Python    = "C:\AI-Tools\AutoGen\venv\Scripts\python.exe"
$TaskName  = "GHTrend-Collector"
$RunAt     = "06:00"
$RunAsUser = "AI-Admin"

if (-not (Test-Path $Script)) {
    Write-Error "trend_monitor.py nicht gefunden: $Script"
    exit 1
}
if (-not (Test-Path $Python)) {
    Write-Error "Python nicht gefunden: $Python"
    exit 1
}
if (-not (Test-Path "$BaseDir\.env")) {
    Write-Warning ".env nicht gefunden — GITHUB_TOKEN vor erstem Lauf hinterlegen."
}

$Action = New-ScheduledTaskAction `
    -Execute $Python `
    -Argument "`"$Script`" --base-dir `"$BaseDir`"" `
    -WorkingDirectory $BaseDir

$Trigger = New-ScheduledTaskTrigger -Daily -At $RunAt

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Task '$TaskName' existiert bereits — wird aktualisiert."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -RunLevel Highest `
    -User $RunAsUser `
    -Force | Out-Null

Write-Host "✅ Task '$TaskName' registriert — täglich $RunAt als $RunAsUser."
Write-Host "Manueller Test: schtasks /run /tn $TaskName"
