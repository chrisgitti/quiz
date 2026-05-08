$ErrorActionPreference = 'Stop'

$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = 'C:\Daten\Projects\weberding\quiz'

if (-not (Test-Path -LiteralPath $target)) {
    New-Item -ItemType Directory -Force $target | Out-Null
}

robocopy $source $target /E /XD .git __pycache__ /XF *.pyc /NFL /NDL /NJH /NJS /NP
$code = $LASTEXITCODE
if ($code -le 7) {
    Write-Host "Quiz wurde nach $target synchronisiert."
    exit 0
}

Write-Error "Robocopy ist mit Code $code fehlgeschlagen."
exit $code

