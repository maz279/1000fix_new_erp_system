# runner entry (Windows) - D-WS-001: same runner, PowerShell wrapper.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue; & $py.Source -3.12 (Join-Path $root 'tooling\fitness\run.py') }
else { & $py.Source (Join-Path $root 'tooling\fitness\run.py') }
exit $LASTEXITCODE
