# =============================================================================
# tasks.ps1 - the Windows-native twin of the Makefile (D-WS-001 consequence 2:
# "PowerShell, not Bash/Make, is the workstation tooling runtime; the task list
# is unchanged, its harness changes"). Same targets, same operations.
#   powershell -File tooling\scripts\tasks.ps1 -Target up [-Profile full]
# =============================================================================
[CmdletBinding()]
param(
    [Parameter(Position = 0)][string]$Target = 'help',
    [string]$Profile = 'core',
    [string]$Module = ''
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root
# DE-10: .env lives at the repo root and is GIT-IGNORED; compose resolves it
# explicitly so `tasks.ps1 -Target up` works from any cwd (P07 verification finding).
$compose = @('compose', '-f', 'infra/compose/docker-compose.yml', '--env-file', '.env')

function Compose([string[]]$Args) { & docker @compose @Args }
function Run-Py([string]$Script, [string[]]$PyArgs = @()) {
    # Odoo runs need the codebase root importable (the shared libs/ packages)
    # and, for tests, the vendored odoo package itself. Without this the odoo
    # targets died on "No module named 'libs/py'" (P07 verification finding).
    $env:PYTHONPATH = "$root;$(Join-Path $root 'vendor\odoo')$([System.IO.Path]::PathSeparator)$env:PYTHONPATH"
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue; & $py.Source -3.12 (Join-Path $root $Script) @PyArgs }
    else { & $py.Source (Join-Path $root $Script) @PyArgs }
}

switch ($Target) {
    'help' {
        Write-Host "targets: bootstrap up down reset odoo-conf db-create odoo-init odoo-install-wave1 run seed test-smoke test-odoo doctor upgrade vendor verify-repo"
        Write-Host "options: -Profile core|auth|integration|field|observability|full   -Module cd_x (for upgrade)"
    }
    'bootstrap' {
        & powershell -ExecutionPolicy Bypass -File (Join-Path $root 'tooling\scripts\setup-toolchains.ps1')
        if (Get-Command uv -ErrorAction SilentlyContinue) { uv sync }
        if (Get-Command pnpm -ErrorAction SilentlyContinue) { pnpm install }
        if (Get-Command pre-commit -ErrorAction SilentlyContinue) { pre-commit install }
        git config core.hooksPath 1000_fix_codebase/.githooks  # single-repo layout (P07)
        & $PSCommandPath -Target odoo-conf
    }
    'up'      {
        # Profiles STACK on core (auth/integration depend on core's postgres)
        $p = @('--profile', 'core'); if ($Profile -ne 'core') { $p += @('--profile', $Profile) }
        Compose ($p + @('up', '-d', '--wait'))
    }
    'down'    {
        $p = @('--profile', 'core'); if ($Profile -ne 'core') { $p += @('--profile', $Profile) }
        Compose ($p + @('down'))
    }
    'reset'   {
        $p = @('--profile', 'core'); if ($Profile -ne 'core') { $p += @('--profile', $Profile) }
        Compose ($p + @('down', '-v'))
        & $PSCommandPath -Target up -Profile $Profile
        & $PSCommandPath -Target db-create
        & $PSCommandPath -Target odoo-init
        & $PSCommandPath -Target seed
    }
    'odoo-conf'    { Run-Py 'tooling/scripts/generate-odoo-conf.py' }
    'db-create'    {
        $exists = Compose (@('exec', '-T', 'postgres', 'psql', '-U', 'fix', '-d', 'postgres', '-tAc', "SELECT 1 FROM pg_database WHERE datname='fix_dev'"))
        if ("$exists".Trim() -ne '1') { Compose (@('exec', '-T', 'postgres', 'createdb', '-U', 'fix', 'fix_dev')) }
    }
    'odoo-init'    { Run-Py 'vendor/odoo/odoo-bin' @('-c', 'infra/odoo-conf/local.resolved.conf', '-d', 'fix_dev', '-i', 'base', '--stop-after-init') }
    'odoo-install-wave1' {
        Run-Py 'vendor/odoo/odoo-bin' @('-c', 'infra/odoo-conf/local.resolved.conf', '-d', 'fix_dev', '-i', 'base,cd_party_master', '--stop-after-init')
    }
    'run'          { Run-Py 'vendor/odoo/odoo-bin' @('-c', 'infra/odoo-conf/local.resolved.conf', '-d', 'fix_dev') }
    'seed'         { Run-Py 'db/seeds/seed.py' @('--seed', '1000fix') }
    'test-smoke'   { Run-Py 'tooling/scripts/test-smoke.py' }
    'doctor'       {
        $ps1 = Join-Path $root 'tooling\scripts\doctor.ps1'
        if (Test-Path $ps1) { & powershell -ExecutionPolicy Bypass -File $ps1; exit $LASTEXITCODE }
        Write-Host 'doctor.ps1 not found - has P02-M10 landed?' -ForegroundColor Red; exit 1
    }
    'upgrade'      {
        if (-not $Module) { Write-Host 'upgrade requires -Module cd_x' -ForegroundColor Red; exit 2 }
        Run-Py 'vendor/odoo/odoo-bin' @('-c', 'infra/odoo-conf/local.resolved.conf', '-d', 'fix_dev', '-u', $Module, '--stop-after-init')
    }
    'test-odoo'    {
        # The full module test estate (34 suites) under the runtime harness:
        # addons/conftest.py bootstraps Odoo's module machinery (no database
        # needed) so the suites can import odoo.addons.cd_* model classes.
        $env:PYTHONPATH = "$root;$(Join-Path $root 'vendor\odoo')$([System.IO.Path]::PathSeparator)$env:PYTHONPATH"
        $py = Get-Command python -ErrorAction SilentlyContinue
        $pyExe = if ($py) { $py.Source } else { 'py' }
        $pyArgs = @()
        if (-not $py) { $pyArgs = @('-3.12') }
        & $pyExe @pyArgs -m pytest addons --quiet -p no:cacheprovider -o 'addopts='
        exit $LASTEXITCODE
    }
    'vendor'       { & powershell -ExecutionPolicy Bypass -File (Join-Path $root 'tooling\scripts\import-vendor.ps1'); exit $LASTEXITCODE }
    'verify-repo'  {
        $fit = Join-Path $root 'tooling\fitness\run.ps1'
        if (Test-Path $fit) { & powershell -ExecutionPolicy Bypass -File $fit; exit $LASTEXITCODE }
        Write-Host 'fitness runner not found' -ForegroundColor Red; exit 1
    }
    default { Write-Host "unknown target: $Target (see -Target help)" -ForegroundColor Red; exit 2 }
}
