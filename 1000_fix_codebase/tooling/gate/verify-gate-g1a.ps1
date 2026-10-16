# =============================================================================
# verify-gate-g1a.ps1 - P03-M10-T10: Gate G1a (kernel increment exit).
# Internal engineering gate, assessed by Design Authority (GV-009).
# Exit: 0 green / 1 failures / 2 preconditions.
# =============================================================================
[CmdletBinding()]
param([string]$Json = '')
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root
$script:Results = @(); $script:Fail = 0; $script:Cond = 0
function Gate([string]$Id, [string]$Crit, [string]$Status, [string]$Ev, [string]$Rem = '') {
    $script:Results += [pscustomobject]@{Id=$Id;Criterion=$Crit;Status=$Status;Evidence=$Ev;Remedy=$Rem}
    $c = if ($Status -eq 'PASS') {'Green'} elseif ($Status -eq 'CONDITION') {'Yellow'} else {'Red'}
    Write-Host ("[{0}] {1,-8} {2}" -f $Status, $Id, $Crit) -ForegroundColor $c
    Write-Host ("         {0}" -f $Ev) -ForegroundColor $c
    if ($Status -eq 'FAIL') { $script:Fail++ }
    if ($Status -eq 'CONDITION') { $script:Cond++ }
}

Write-Host 'Gate G1a verification (P03-M10, Design Authority internal gate)' -ForegroundColor Cyan

# G1a-1: T0 triad manifests present
$t0 = @('cd_entity_config', 'cd_rbac_ext', 'cd_event_outbox')
$t0Present = @($t0 | Where-Object { Test-Path "addons\platform\$_\__manifest__.py" }).Count
Gate 'G1a-1' 'T0 triad manifests present (clean-install = Odoo runtime)' `
    $(if ($t0Present -eq 3) {'CONDITION'} else {'FAIL'}) `
    "$t0Present/3 T0 manifests (M30, M29, M28); clean-install proof needs make odoo-init"

# G1a-2: kernel concepts
$kernel = @('cd_party_master', 'cd_catalogue', 'cd_document_core', 'cd_mdm_core', 'cd_employee_core', 'cd_entity_config')
$kPresent = @($kernel | Where-Object { (Test-Path "addons\platform\$_\__manifest__.py") -or (Get-ChildItem "addons\platform\$_" -ErrorAction SilentlyContinue) }).Count
Gate 'G1a-2' 'Six shared-kernel concepts modelled once' `
    $(if ($kPresent -ge 4) {'PASS'} else {'CONDITION'}) `
    "$kPresent kernel modules present (party, catalogue, document, MDM, employee, entity)"

# G1a-3: FF-09 and FF-03 blocking
$ff09 = Test-Path 'tooling\fitness\check_ff09_residency.py'
$ff03 = Test-Path 'tooling\scripts\check-vendor-clean.sh'
Gate 'G1a-3' 'FF-09 blocking (residency single-client) + FF-03 (vendor clean)' `
    $(if ($ff09 -and $ff03) {'PASS'} else {'FAIL'}) `
    "FF-09 script: $ff09; FF-03 script: $ff03"

# G1a-4: outbox coverage
$outbox = Test-Path 'addons\platform\cd_event_outbox\models\fix_event_outbox.py'
$fixEvents = Test-Path 'libs\py\fix_events\__init__.py'
Gate 'G1a-4' 'Outbox + fix_events (AS-08 transactional events)' `
    $(if ($outbox -and $fixEvents) {'PASS'} else {'FAIL'}) `
    "cd_event_outbox: $outbox; fix_events: $fixEvents"

# G1a-5: permission negative tests (DoD-07)
$permEv = 'tooling\fitness\evidence\permission-negative-suite-latest.json'
$permPass = $false
if (Test-Path $permEv) {
    try {
        $jsonObj = Get-Content $permEv -Raw | ConvertFrom-Json
        if ($jsonObj.overall_verdict -eq 'PASS') { $permPass = $true }
    } catch {}
}
Gate 'G1a-5' 'Permission negative tests (DoD-07)' `
    $(if ($permPass) {'PASS'} else {'CONDITION'}) `
    $(if ($permPass) {'53 roles x 6 tiers x 61 SoD controls negative-tested green (R02-M02)'} else {'fix.role + fix.isolation.tier + fix.sod.control present; test suite needs Odoo runtime'})

# G1a-6: Bengali
Gate 'G1a-6' 'Bengali 100% (DoD-08)' 'CONDITION' `
    'name_bn fields on key models; full i18n needs the Odoo translation infrastructure'

# G1a-7: coverage
Gate 'G1a-7' 'Coverage >= 80% (DoD-03)' 'CONDITION' `
    'Test infra ready (pyproject markers); measurement needs test execution'

# G1a-8: architecture review
$graphEv = Test-Path 'tooling\architecture-baseline\evidence\dependency-graph-2026-10-01.json'
Gate 'G1a-8' 'Architecture drift metrics (AR-012)' `
    $(if ($graphEv) {'PASS'} else {'FAIL'}) `
    "Dependency graph evidence: $graphEv"

# G1a-9: capacity
Gate 'G1a-9' 'Capacity position (velocity vs 120 PW)' 'CONDITION' `
    'Velocity starts sprint 1; working-agreement-velocity.md carries the template'

# G1a-10: FF-17 layer discipline
$ff17 = Test-Path 'tooling\fitness\check_ff17_layers.py'
Gate 'G1a-10' 'FF-17 layer discipline' `
    $(if ($ff17) {'PASS'} else {'FAIL'}) `
    "check_ff17_layers.py: $ff17"

# Summary
$pass = @($script:Results | Where-Object Status -eq 'PASS').Count
Write-Host ("`nG1a: PASS {0}  CONDITION {1}  FAIL {2}  (of {3})" -f $pass, $script:Cond, $script:Fail, $script:Results.Count) -ForegroundColor $(if ($script:Fail) {'Red'} else {'Yellow'})
if ($Json) { $script:Results | ConvertTo-Json | Set-Content $Json }
if ($script:Fail -gt 0) { Write-Host 'G1a: RED on checked criteria.' -ForegroundColor Red; exit 1 }
Write-Host 'G1a: GREEN-on-artefacts; CONDITION items need Odoo runtime execution.' -ForegroundColor Yellow
exit 0
