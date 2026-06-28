# install.ps1 - AOS Installer/Updater + Self-Test fuer VM / Zweitsysteme
# Aufruf:
#   powershell .\install.ps1            -> idempotente Installation
#   powershell .\install.ps1 -Verify    -> Self-Test ohne Aenderungen
param(
    [switch]$Verify
)
$ErrorActionPreference = 'Stop'

$AOS_ROOT     = $PSScriptRoot
$claudeCmdDir = "$HOME\.claude\commands"
$claudeHookDir= "$HOME\.claude\hooks"
$settingsPath = "$HOME\.claude\settings.json"

# ---------------------------------------------------------------------------
# SELF-TEST (-Verify): prueft Installation, aendert nichts. Exit 0 = alle PASS.
# ---------------------------------------------------------------------------
if ($Verify) {
    Write-Host "=== AOS Self-Test (-Verify) ===" -ForegroundColor Cyan
    $fail = 0
    function Check($name, $cond) {
        if ($cond) { Write-Host "  PASS  $name" -ForegroundColor Green }
        else       { Write-Host "  FAIL  $name" -ForegroundColor Red; $script:fail++ }
    }

    # 1. AOS_ROOT-Umgebungsvariable gesetzt
    Check "Umgebungsvariable AOS_ROOT gesetzt" ([Environment]::GetEnvironmentVariable("AOS_ROOT","User"))

    # 2. Alle Commands verknuepft und aufloesbar
    $cmds = Get-ChildItem -Path "$AOS_ROOT\commands" -Filter "*.md"
    foreach ($c in $cmds) {
        Check "Command verknuepft: $($c.Name)" (Test-Path "$claudeCmdDir\$($c.Name)")
    }

    # 3. Safety-Hook verknuepft
    Check "Safety-Hook verknuepft" (Test-Path "$claudeHookDir\block-dangerous.sh")

    # 4. Hook in settings.json (PreToolUse) registriert
    $hookWired = $false
    if (Test-Path $settingsPath) {
        $hookWired = (Get-Content $settingsPath -Raw) -match "block-dangerous\.sh"
    }
    Check "PreToolUse-Hook in settings.json registriert" $hookWired

    # 4b. jq vorhanden (Guardrail-Abhaengigkeit; fehlt es, blockiert der Hook fail-closed)
    Check "jq verfuegbar (Guardrail-Abhaengigkeit)" (Get-Command jq -ErrorAction SilentlyContinue)

    # 5. Keine relativen Pfad-Hops (@../) in verschachtelten CLAUDE.md
    $hops = Get-ChildItem -Path $AOS_ROOT -Recurse -Filter "CLAUDE.md" -ErrorAction SilentlyContinue |
        Where-Object { $_.DirectoryName -ne $AOS_ROOT } |
        Where-Object { (Get-Content $_.FullName -Raw) -match "@\.\./" }
    Check "Keine '@../'-Pfad-Hops in Sub-CLAUDE.md" (-not $hops)

    # 6. Map<->Dateien-Konsistenz: keine hartkodierten Benutzerpfade in Doku
    # Trifft reale Benutzernamen, ignoriert markierte Platzhalter (<user>) und '..'
    $hardcoded = Get-ChildItem -Path $AOS_ROOT -Recurse -Include "*.md","*.ps1","*.sh" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne "install.ps1" } |
        Where-Object { (Get-Content $_.FullName -Raw) -match "C:\\Users\\(?!<|\.\.)[^\\]+\\AOS" }
    Check "Keine hartkodierten realen Benutzerpfade (C:\Users\<name>\AOS)" (-not $hardcoded)

    Write-Host ""
    if ($fail -eq 0) { Write-Host "Self-Test: ALLE PASS" -ForegroundColor Green; exit 0 }
    else { Write-Host "Self-Test: $fail FEHLER" -ForegroundColor Red; exit 1 }
}

# ---------------------------------------------------------------------------
# INSTALLATION
# ---------------------------------------------------------------------------
Write-Host "=== AOS Installation gestartet ===" -ForegroundColor Cyan

# 1. Sicherheits-/Integritaetspruefung (gegen eingepackte Secrets)
$badFiles = Get-ChildItem -Path $AOS_ROOT -Recurse -Include "*.env","*.env.*","secrets.json","credentials.json","*.key","*.pem" -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notmatch "\.(example|template|sample)$" }
if ($badFiles) {
    Write-Error "ABORT: Integritaetsverletzung - Secrets im Installationspaket entdeckt:"
    $badFiles | ForEach-Object { Write-Error "  $($_.FullName)" }
    Write-Error "Bitte bereinigen Sie die Quelle und erstellen Sie den Export neu."
    exit 1
}
Write-Host "Integritaetspruefung: OK" -ForegroundColor Green

# 1.5 Validierung verschachtelter CLAUDE.md auf relative Pfad-Hops
$nestedClaudes = Get-ChildItem -Path $AOS_ROOT -Recurse -Filter "CLAUDE.md" -ErrorAction SilentlyContinue |
    Where-Object { $_.DirectoryName -ne $AOS_ROOT -and $_.DirectoryName -ne "$HOME\.claude" }
foreach ($file in $nestedClaudes) {
    if ((Get-Content $file.FullName -Raw) -match "@\.\./") {
        Write-Warning "WARNUNG: Relative Pfad-Hop-Direktive in $($file.FullName) — bitte vermeiden."
    }
}

# 2. AOS_ROOT als Umgebungsvariable persistieren (User-Scope)
[Environment]::SetEnvironmentVariable("AOS_ROOT", $AOS_ROOT, "User")
$env:AOS_ROOT = $AOS_ROOT
Write-Host "Umgebungsvariable AOS_ROOT gesetzt: $AOS_ROOT" -ForegroundColor Green

# 3. Verzeichnisse anlegen
$paths = @($claudeCmdDir, $claudeHookDir, "$HOME\.gemini\config\plugins\agos-core\skills",
           "$AOS_ROOT\projects\Projekte-Claude", "$AOS_ROOT\projects\Projekte-Antigravity")
foreach ($path in $paths) {
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "Ordner erstellt: $path" -ForegroundColor Green
    }
}

# 4. Claude Commands verknuepfen (Hardlink, idempotent — kein Entwicklermodus noetig)
$commands = Get-ChildItem -Path "$AOS_ROOT\commands" -Filter "*.md"
foreach ($cmd in $commands) {
    $targetLink = "$claudeCmdDir\$($cmd.Name)"
    if (-not (Test-Path $targetLink)) {
        New-Item -ItemType HardLink -Path $targetLink -Value $cmd.FullName -Force | Out-Null
        Write-Host "Command verknuepft (Hardlink): $($cmd.Name)" -ForegroundColor Green
    } else {
        Write-Host "Command bereits verknuepft: $($cmd.Name)" -ForegroundColor Gray
    }
}

# 5. Safety-Hook verknuepfen (Hardlink, idempotent)
$hookSource = "$AOS_ROOT\hooks\block-dangerous.sh"
$hookTarget = "$claudeHookDir\block-dangerous.sh"
if ((Test-Path $hookSource) -and -not (Test-Path $hookTarget)) {
    New-Item -ItemType HardLink -Path $hookTarget -Value $hookSource -Force | Out-Null
    Write-Host "Safety-Hook verknuepft (Hardlink): $hookTarget" -ForegroundColor Green
} else {
    Write-Host "Safety-Hook bereits verknuepft." -ForegroundColor Gray
}

# 6. PreToolUse-Hook in settings.json verdrahten (idempotent, JSON-sicher)
$settings = if (Test-Path $settingsPath) {
    Get-Content $settingsPath -Raw | ConvertFrom-Json
} else { [PSCustomObject]@{} }
$hookCmd = "bash $AOS_ROOT/hooks/block-dangerous.sh"
$raw = if (Test-Path $settingsPath) { Get-Content $settingsPath -Raw } else { "" }
if ($raw -notmatch "block-dangerous\.sh") {
    $hookEntry = [PSCustomObject]@{
        matcher = "Bash"
        hooks   = @(@{ type = "command"; command = $hookCmd })
    }
    if (-not $settings.PSObject.Properties['hooks']) {
        $settings | Add-Member -NotePropertyName hooks -NotePropertyValue ([PSCustomObject]@{})
    }
    if (-not $settings.hooks.PSObject.Properties['PreToolUse']) {
        $settings.hooks | Add-Member -NotePropertyName PreToolUse -NotePropertyValue @()
    }
    $settings.hooks.PreToolUse += $hookEntry
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($settingsPath, ($settings | ConvertTo-Json -Depth 10), $utf8NoBom)
    Write-Host "PreToolUse-Hook in settings.json registriert." -ForegroundColor Green
} else {
    Write-Host "PreToolUse-Hook bereits in settings.json registriert." -ForegroundColor Gray
}

# 7. Gemini Skills registrieren (idempotent ueber add-skill.ps1)
if (Test-Path "$AOS_ROOT\scripts\add-skill.ps1") {
    Write-Host "Registriere Skills in Antigravity (Gemini)..." -ForegroundColor Cyan
    foreach ($cmd in $commands) {
        $geminiSkillFile = "$HOME\.gemini\config\plugins\agos-core\skills\$($cmd.BaseName)\SKILL.md"
        if (-not (Test-Path $geminiSkillFile)) {
            & "$AOS_ROOT\scripts\add-skill.ps1" -CommandName $cmd.BaseName | Out-Null
            Write-Host "Skill registriert: $($cmd.BaseName)" -ForegroundColor Green
        } else {
            Write-Host "Gemini Skill bereits registriert: $($cmd.BaseName)" -ForegroundColor Gray
        }
    }
}

# 8. global-rules.md in globale CLAUDE.md eintragen (idempotent, bereinigt, UTF-8 ohne BOM)
$claudeMdPath  = "$HOME\.claude\CLAUDE.md"
$globalRulesRef= "@$AOS_ROOT\memory\global-rules.md"
if (Test-Path $claudeMdPath) {
    $cleaned = (Get-Content $claudeMdPath) | Where-Object { $_ -notmatch '@.*\\memory\\global-rules\.md' }
    [System.IO.File]::WriteAllLines($claudeMdPath, $cleaned, [System.Text.UTF8Encoding]::new($false))
}
$existing = if (Test-Path $claudeMdPath) { Get-Content $claudeMdPath -Raw } else { "" }
if ($existing -notmatch [regex]::Escape($globalRulesRef)) {
    [System.IO.File]::AppendAllText($claudeMdPath, "`r`n$globalRulesRef`r`n", [System.Text.UTF8Encoding]::new($false))
    Write-Host "global-rules.md in CLAUDE.md verknuepft." -ForegroundColor Green
}

Write-Host "=== AOS Installation abgeschlossen ===" -ForegroundColor Cyan
Write-Host "Verifikation: powershell $AOS_ROOT\install.ps1 -Verify" -ForegroundColor Yellow
Write-Host ""
Write-Host "NAECHSTE SCHRITTE (MOBILE DISPATCHER, optional):" -ForegroundColor Yellow
Write-Host "1. 'claude login' in der VM-PowerShell ausfuehren." -ForegroundColor White
Write-Host "2. 'claude' starten und Handy per Koppelungscode verbinden (siehe MOBILE.md)." -ForegroundColor White
