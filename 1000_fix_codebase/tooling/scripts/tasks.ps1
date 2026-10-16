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
        Write-Host "targets: bootstrap up down reset odoo-conf db-create odoo-init odoo-install-wave1 run seed test-smoke test-odoo coverage doctor upgrade vendor verify-repo"
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
        Run-Py 'vendor/odoo/odoo-bin' @('-c', 'infra/odoo-conf/local.resolved.conf', '-d', 'fix_dev', '-i', 'base,cd_design_tokens,cd_entity_config,cd_event_outbox,cd_rbac_ext,cd_document_core,cd_gl_ext,cd_grc,cd_knowledge,cd_mdm_core,cd_rate_card,cd_catalogue,cd_party_master,cd_workflow_engine,cd_esignature,cd_fixed_asset_ext,cd_tax_engine_bd,cd_dynamic_pricing,cd_demand_plan,cd_campaign,cd_contact_centre,cd_employee_core,cd_storefront,cd_fpa,cd_settlement_ext,cd_device_registry,cd_equipment_register,cd_hr_core,cd_requisition,cd_data_case,cd_service_order,cd_facility,cd_hse,cd_ppm,cd_talent,cd_ap_ext,cd_import_order,cd_wms_structure,cd_ewaste,cd_attendance,cd_billing_engine,cd_competency,cd_consignment,cd_contract_core,cd_crm_ext,cd_customer_portal,cd_cx_feedback,cd_front_desk,cd_p03_portal,cd_performance,cd_quotation,cd_tradein,cd_vehicle_ext,cd_warranty_claims,cd_stream_registry,cd_vendor_portal,cd_payroll_bd,cd_msp_contract,cd_partner,cd_rental_asset,cd_subscription,cd_qms_process,cd_cash_position,cd_marketplace,cd_metric_registry,cd_itsm,cd_corporate_portal', '--stop-after-init')
    }
    'run'          { Run-Py 'vendor/odoo/odoo-bin' @('-c', 'infra/odoo-conf/local.resolved.conf', '-d', 'fix_dev', '--dev=all') }
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
    'coverage'     {
        Run-Py 'tooling/scripts/measure-coverage.py'
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
