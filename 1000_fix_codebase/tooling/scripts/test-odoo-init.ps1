$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root

$env:PYTHONPATH = "$root;$(Join-Path $root 'vendor\odoo');$env:PYTHONPATH"
$env:TZ = 'UTC'
$py = Join-Path $root '.venv\Scripts\python.exe'
$conf = Join-Path $root 'infra\odoo-conf\local.resolved.conf'
$odooBin = Join-Path $root 'vendor\odoo\odoo-bin'

& $py $odooBin -c $conf -d fix_dev --stop-after-init
Write-Host "Exit Code: $LASTEXITCODE"
