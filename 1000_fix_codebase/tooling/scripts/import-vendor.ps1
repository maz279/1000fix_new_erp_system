# =============================================================================
# import-vendor.ps1 - P02-M04 orchestration (Windows entry point).
# Runs tooling/scripts/import-vendor.sh under Git Bash (ships with Git for
# Windows, pinned by P02-M01). Idempotent: present subtrees are skipped.
# The 20-40 minute clone budget (BE-004 section 11) is EXPECTED - see
# docs/guides/clone-budget.md for the partial-clone accelerator.
# =============================================================================
[CmdletBinding()]
param([switch]$DryRun)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$sh = Join-Path $root 'tooling\scripts\import-vendor.sh'
if (-not (Test-Path $sh)) { Write-Error "import-vendor.sh not found: $sh" }
$bash = Get-Command bash -ErrorAction SilentlyContinue
if (-not $bash) {
    Write-Host '[FAIL] bash not on PATH - Git for Windows provides it (P02-M01-T07).' -ForegroundColor Red
    Write-Host '      remedy: install Git for Windows at the pinned version, re-run.' -ForegroundColor Yellow
    exit 2
}
if ($DryRun) { Write-Host "[dry ] would run: bash $sh"; exit 0 }
Write-Host 'import-vendor: starting (Odoo submodule + 20 OCA subtrees; expect 20-40 min)...' -ForegroundColor Cyan
& $bash.Source $sh
exit $LASTEXITCODE
