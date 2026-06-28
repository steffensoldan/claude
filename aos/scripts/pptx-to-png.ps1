<#
.SYNOPSIS
    Rendert eine PPTX-Datei folienweise nach PNG — Windows-nativ via PowerPoint-COM.
    Ersatz fuer den LibreOffice/pdftoppm-Pfad des offiziellen pptx-Skills auf
    Systemen ohne LibreOffice.

.PARAMETER Pptx
    Pfad zur .pptx-Datei.

.PARAMETER OutDir
    Zielordner fuer die PNGs (wird geleert/neu angelegt). Default: <pptx-Ordner>\render

.PARAMETER Width
    Breite der PNGs in Pixel (16:9 -> Hoehe wird passend gesetzt). Default 1600.

.EXAMPLE
    powershell -File AOS\scripts\pptx-to-png.ps1 -Pptx deck.pptx
    # erzeugt deck-Ordner\render\Folie1.PNG ...
#>
param(
    [Parameter(Mandatory = $true)][string]$Pptx,
    [string]$OutDir,
    [int]$Width = 1600
)

if (-not (Test-Path $Pptx)) { Write-Error "Datei nicht gefunden: $Pptx"; exit 1 }
$Pptx = (Resolve-Path $Pptx).Path
if (-not $OutDir) { $OutDir = Join-Path (Split-Path $Pptx -Parent) "render" }

if (Test-Path $OutDir) { Remove-Item $OutDir -Recurse -Force }
New-Item -ItemType Directory -Path $OutDir | Out-Null

$Height = [int][math]::Round($Width * 9 / 16)

try {
    $pp = New-Object -ComObject PowerPoint.Application
} catch {
    Write-Error "PowerPoint nicht verfuegbar. Alternativ LibreOffice nutzen (soffice + pdftoppm)."
    exit 2
}

try {
    $pres = $pp.Presentations.Open($Pptx, $true, $false, $false)   # ReadOnly, untitled, no window
    $pres.Export($OutDir, "PNG", $Width, $Height)
    $pres.Close()
} finally {
    $pp.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp) | Out-Null
}

Get-ChildItem $OutDir -Filter *.PNG | Sort-Object Name | ForEach-Object { $_.FullName }
