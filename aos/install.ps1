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
# HILFSFUNKTIONEN
# ---------------------------------------------------------------------------
function Write-Utf8NoBom {
    param([string]$Path, [string]$Content)
    [System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))
}

function Write-Utf8NoBomLines {
    param([string]$Path, [string[]]$Content)
    [System.IO.File]::WriteAllLines($Path, $Content, [System.Text.UTF8Encoding]::new($false))
}

function Append-Utf8NoBom {
    param([string]$Path, [string]$Content)
    [System.IO.File]::AppendAllText($Path, $Content, [System.Text.UTF8Encoding]::new($false))
}

function Test-FileContentMatch([string]$path1, [string]$path2) {
    if (-not (Test-Path $path1) -or -not (Test-Path $path2)) { return $false }
    try {
        $bytes1 = [System.IO.File]::ReadAllBytes($path1)
        $bytes2 = [System.IO.File]::ReadAllBytes($path2)
        if ($bytes1.Length -ne $bytes2.Length) { return $false }
        for ($i = 0; $i -lt $bytes1.Length; $i++) {
            if ($bytes1[$i] -ne $bytes2[$i]) { return $false }
        }
        return $true
    } catch {
        return $false
    }
}

function Create-Link {
    param([string]$LinkPath, [string]$TargetPath)
    if (Test-Path $LinkPath) {
        # Pruefe ob Inhalt uebereinstimmt
        if (Test-FileContentMatch $LinkPath $TargetPath) {
            Write-Host "Link bereits verknuepft und konsistent: $(Split-Path $LinkPath -Leaf)" -ForegroundColor Gray
            return
        }
        # Bei Inkonstistenz (Drift) Loeschen und neu verknuepfen
        Remove-Item -Force $LinkPath
    }
    
    try {
        # Symbolischer Link als Standard (Developer Mode oder Admin-Rechte erforderlich)
        New-Item -ItemType SymbolicLink -Path $LinkPath -Value $TargetPath -Force | Out-Null
        Write-Host "Link verknuepft (Symlink): $(Split-Path $LinkPath -Leaf)" -ForegroundColor Green
    }
    catch {
        # Fallback auf HardLink bei fehlenden Rechten
        try {
            New-Item -ItemType HardLink -Path $LinkPath -Value $TargetPath -Force | Out-Null
            Write-Warning "WARNUNG: Symlink-Erstellung fehlgeschlagen (Berechtigung?). Nutze Hardlink-Fallback fuer $(Split-Path $LinkPath -Leaf). Drift-Gefahr bei Updates!"
        }
        catch {
            Write-Error "FEHLER: Link-Erstellung fehlgeschlagen fuer $($LinkPath). Fehler: $_"
            throw $_
        }
    }
}

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

    # 2. Alle Commands verknuepft und konsistent
    $cmds = Get-ChildItem -Path "$AOS_ROOT\commands" -Filter "*.md"
    foreach ($c in $cmds) {
        $linkPath = "$claudeCmdDir\$($c.Name)"
        $exists = Test-Path $linkPath
        $match = $false
        if ($exists) {
            $match = Test-FileContentMatch $c.FullName $linkPath
        }
        Check "Command verknuepft und konsistent: $($c.Name)" ($exists -and $match)
    }

    # 3. Safety-Hook verknuepft und konsistent
    $hookTarget = "$claudeHookDir\block-dangerous.sh"
    $exists = Test-Path $hookTarget
    $match = $false
    if ($exists) {
        $match = Test-FileContentMatch "$AOS_ROOT\hooks\block-dangerous.sh" $hookTarget
    }
    Check "Safety-Hook verknuepft und konsistent" ($exists -and $match)

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
        Where-Object { $_.FullName -notmatch '\\(projects|dialog|scratch)\\' -and $_.Name -ne "install.ps1" } |
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
    Where-Object { $_.FullName -notmatch '\\projects\\' -and $_.Name -notmatch "\.(example|template|sample)$" }
if ($badFiles) {
    Write-Error "ABORT: Integritaetsverletzung - Secrets im Installationspaket entdeckt:"
    $badFiles | ForEach-Object { Write-Error "  $($_.FullName)" }
    Write-Error "Bitte bereinigen Sie die Quelle und erstellen Sie den Export neu."
    exit 1
}
Write-Host "Integritaetspruefung: OK" -ForegroundColor Green

# 1.5 Validierung verschachtelter CLAUDE.md auf relative Pfad-Hop-Verstöße
$nestedClaudes = Get-ChildItem -Path $AOS_ROOT -Recurse -Filter "CLAUDE.md" -ErrorAction SilentlyContinue |
    Where-Object { $_.DirectoryName -ne $AOS_ROOT -and $_.DirectoryName -ne "$HOME\.claude" }
foreach ($file in $nestedClaudes) {
    if ((Get-Content $file.FullName -Raw) -match "@\.\./") {
        Write-Warning "WARNUNG: Relative Pfad-Hop-Direktive in $($file.FullName) - bitte vermeiden."
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

# 4. Claude Commands verknuepfen (Symlink mit Hardlink-Fallback)
$commands = Get-ChildItem -Path "$AOS_ROOT\commands" -Filter "*.md"
foreach ($cmd in $commands) {
    $targetLink = "$claudeCmdDir\$($cmd.Name)"
    Create-Link -LinkPath $targetLink -TargetPath $cmd.FullName
}

# 5. Safety-Hook verknuepfen (Symlink mit Hardlink-Fallback)
$hookSource = "$AOS_ROOT\hooks\block-dangerous.sh"
$hookTarget = "$claudeHookDir\block-dangerous.sh"
if (Test-Path $hookSource) {
    Create-Link -LinkPath $hookTarget -TargetPath $hookSource
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
    Write-Utf8NoBom $settingsPath ($settings | ConvertTo-Json -Depth 10)
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
    Write-Utf8NoBomLines $claudeMdPath $cleaned
}
$existing = if (Test-Path $claudeMdPath) { Get-Content $claudeMdPath -Raw } else { "" }
if ($existing -notmatch [regex]::Escape($globalRulesRef)) {
    Append-Utf8NoBom $claudeMdPath "`r`n$globalRulesRef`r`n"
    Write-Host "global-rules.md in CLAUDE.md verknuepft." -ForegroundColor Green
}

# 9. Abschliessende Konsistenzprüfung (Fail-Fast)
Write-Host "Führe abschliessende Verifikation durch..." -ForegroundColor Cyan
$installFailed = $false
foreach ($cmd in $commands) {
    $targetLink = "$claudeCmdDir\$($cmd.Name)"
    if (-not (Test-FileContentMatch $cmd.FullName $targetLink)) {
        Write-Error "FEHLER: Konsistenzprüfung fehlgeschlagen für $($cmd.Name). Link weicht von Quelle ab!"
        $installFailed = $true
    }
}
if (-not (Test-FileContentMatch $hookSource $hookTarget)) {
    Write-Error "FEHLER: Konsistenzprüfung fehlgeschlagen für Safety-Hook. Link weicht von Quelle ab!"
    $installFailed = $true
}
if ($installFailed) {
    Write-Error "AOS-Installation ist inkonsistent! Bitte überprüfen Sie Berechtigungen und führen Sie install.ps1 erneut aus."
    exit 1
}
Write-Host "Konsistenzprüfung: OK" -ForegroundColor Green

Write-Host "=== AOS Installation abgeschlossen ===" -ForegroundColor Cyan
Write-Host "Verifikation: powershell $AOS_ROOT\install.ps1 -Verify" -ForegroundColor Yellow
Write-Host ""
Write-Host "NAECHSTE SCHRITTE (MOBILE DISPATCHER, optional):" -ForegroundColor Yellow
Write-Host "1. 'claude login' in der VM-PowerShell ausfuehren." -ForegroundColor White
Write-Host "2. 'claude' starten und Handy per Koppelungscode verbinden (siehe MOBILE.md)." -ForegroundColor White
