$ErrorActionPreference = 'Stop'

$root   = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $root 'out'
$target = 'C:\Daten\Projects\weberding\quiz'

if (-not (Test-Path -LiteralPath $source)) {
    Write-Error "out/ nicht gefunden. Bitte zuerst 'python -B scripts\quiz_tool.py publish' ausführen."
    exit 1
}

if (-not (Test-Path -LiteralPath $target)) {
    New-Item -ItemType Directory -Force $target | Out-Null
}

robocopy $source $target /E /NFL /NDL /NJH /NJS /NP
$code = $LASTEXITCODE
if ($code -le 7) {
    Write-Host "Quiz wurde nach $target synchronisiert."
    exit 0
}

Write-Error "Robocopy ist mit Code $code fehlgeschlagen."
exit $code
