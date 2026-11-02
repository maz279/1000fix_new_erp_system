# Resilient background supervisor for Odoo 19
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root

while ($true) {
    Write-Host "[Odoo Supervisor] Starting Odoo Server..." -ForegroundColor Cyan
    $env:PYTHONPATH = "$root;$(Join-Path $root 'vendor\odoo');$env:PYTHONPATH"
    $env:TZ = 'UTC'
    $py = Join-Path $root '.venv\Scripts\python.exe'
    $conf = Join-Path $root 'infra\odoo-conf\local.resolved.conf'
    $odooBin = Join-Path $root 'vendor\odoo\odoo-bin'
    
    & $py $odooBin -c $conf -d fix_dev --dev=all
    Write-Host "[Odoo Supervisor] Odoo exited with code $LASTEXITCODE. Restarting in 2 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}
