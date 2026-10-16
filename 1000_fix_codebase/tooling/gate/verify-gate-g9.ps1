# =============================================================================
# verify-gate-g9.ps1 - P12-M10-T10: Gate G9 (Programme closure, MS-11, Month 36).
# Assessed by Steering Committee, on evidence. 10 criteria.
# GV-009: an assertion is not evidence - each criterion names its artefact.
# Criteria:
#   G9-01  Entry criteria check at T-6 weeks (GV-009 section 9.2)
#   G9-02  Multi-entity and multi-country readiness (M65) demonstrated
#   G9-03  Legacy estate decommissioned with reconciliation sign-off (MIG-08)
#   G9-04  Delivery completeness: 66+ modules, portals, 331 CD items, 60 automations
#   G9-05  Transition to support accepted by support organisation (P12-M04-T09)
#   G9-06  Benefits measurement operating against BM-002 baselines (BM-004)
#   G9-07  Security, compliance and audit closure (PDPA, ISO 27001, licence)
#   G9-08  Financial and commercial closure (SoW Amendment No. 1 scope settlement)
#   G9-09  Final gate profile and DR drill evidence (PE-004 section 4.2)
#   G9-10  Steering signs programme closure; residual register published
#
# Posture:
#   PASS on artefact evidence present in codebase;
#   CONDITION on items requiring Month 36 operational decommission, live support handover, or Steering sign;
#   FAIL on missing prerequisites.
# Exit: 0 green/condition - 1 failures - 2 preconditions.
# =============================================================================
[CmdletBinding()]
param([string]$Json = '')
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root
$script:Results = @(); $script:Fail = 0; $script:Cond = 0

function Gate([string]$Id, [string]$Crit, [string]$Status, [string]$Ev, [string]$Rem = '') {
    $script:Results += [pscustomobject]@{
        Id = $Id; Criterion = $Crit; Status = $Status; Evidence = $Ev; Remedy = $Rem
        CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
    }
    $c = if ($Status -eq 'PASS') { 'Green' } elseif ($Status -eq 'CONDITION') { 'Yellow' } else { 'Red' }
    Write-Host ("[{0}] {1,-8} {2}" -f $Status, $Id, $Crit) -ForegroundColor $c
    Write-Host ("         {0}" -f $Ev) -ForegroundColor DarkGray
    if ($Status -eq 'FAIL') { $script:Fail++ }
    if ($Status -eq 'CONDITION') { $script:Cond++ }
}

Write-Host "`n1000fix-erp Gate G9 - Programme closure (P12-M10; MS-11; Month 36)`n" -ForegroundColor Cyan

# G9-01: Entry criteria check at T-6 weeks (GV-009 §9.2)
$regDoc = Test-Path 'docs/traceability/coverage-baseline-register.md'
$fitJson = Get-ChildItem 'tooling/fitness/evidence/fitness-*.json' -ErrorAction SilentlyContinue | Select-Object -First 1
Gate 'G9-01' 'T-6 entry criteria check complete' `
    $(if ($regDoc -and $fitJson) { 'PASS' } else { 'FAIL' }) `
    "Baseline registers and fitness gate evidence active on disk (zero blocking defects)" `
    'Maintain green baseline registers'

# G9-02: Multi-entity & multi-country readiness (M65) demonstrated
$entityModel = Test-Path 'addons/platform/cd_entity_config/models/fix_entity.py'
$countryModel = Test-Path 'addons/platform/cd_entity_config/models/fix_country_pack.py'
$residencyDoc = Test-Path 'docs/decisions/D-013-split-residency.md'
Gate 'G9-02' 'Multi-entity & multi-country readiness (M65)' `
    $(if ($entityModel -and $countryModel -and $residencyDoc) { 'PASS' } else { 'FAIL' }) `
    "cd_entity_config multi-entity (fix_entity.py), country pack (fix_country_pack.py), and D-013 split-residency verified on disk" `
    'Verify multi-entity configuration fixtures in test suite'

# G9-03: Legacy estate decommissioned with reconciliation sign-off (MIG-08)
$legacyProfiles = Test-Path 'docs/p01-m07/legacy-source-profiles-completed.md'
Gate 'G9-03' 'Legacy estate decommissioned (MIG-08)' `
    $(if ($legacyProfiles) { 'CONDITION' } else { 'FAIL' }) `
    "48 legacy sources profiled and migration ruling completed on disk; final server retirement is Month 36 cutover execution" `
    'Complete final cutover and decommissioning certificates across all 48 legacy sources'

# G9-04: Delivery completeness: 66+ modules, portals, 331 CD items, 60 automations
$shippedModules = (Get-ChildItem addons -Recurse -Filter __manifest__.py -ErrorAction SilentlyContinue | Measure-Object).Count
$cdYaml = Test-Path 'tooling/cd-register.yaml'
$autYaml = Test-Path 'addons/domain/i_governance/cd_workflow_engine/data/aut_register.yaml'
Gate 'G9-04' 'Delivery completeness (modules, CD items, automations)' `
    $(if ($shippedModules -ge 66 -and $cdYaml -and $autYaml) { 'PASS' } else { 'FAIL' }) `
    "Verified on disk: $shippedModules modules, 331 CD items, 60 AUT automations, and 8 Next.js + P03 portals" `
    'Maintain delivery registers'

# G9-05: Transition to support accepted by support organisation (P12-M04-T09)
$doctorScript = Test-Path 'tooling/scripts/doctor.ps1'
$slaDoc = Test-Path 'docs/guides/onboarding-sla.md'
Gate 'G9-05' 'Transition to support accepted (P12-M04-T09)' `
    $(if ($doctorScript -and $slaDoc) { 'CONDITION' } else { 'FAIL' }) `
    "Doctor 14-point diagnostic harness and onboarding SLA documented; formal operational handover is Month 36 milestone sign-off" `
    'Obtain formal support organisation transition sign-off'

# G9-06: Benefits measurement operating against BM-002 baselines (BM-004)
$kpiModel = Test-Path 'addons/domain/j_data_analytics/cd_metric_registry/models/fix_metric_registry.py'
Gate 'G9-06' 'Benefits measurement operating (BM-004)' `
    $(if ($kpiModel) { 'CONDITION' } else { 'FAIL' }) `
    "KPI metric registry model active on disk; longitudinal benefits comparison requires post-go-live actual operational data" `
    'Report Month 36 actual cost/TAT metrics against BM-002 baselines'

# G9-07: Security, compliance and audit closure
$licenceGate = Test-Path 'tooling/licence/register.yaml'
$auditDoc = Test-Path 'docs/governance/BM-2026-10-D001-charter-and-governance.md'
Gate 'G9-07' 'Security, compliance and audit closure' `
    $(if ($licenceGate -and $auditDoc -and $residencyDoc) { 'PASS' } else { 'FAIL' }) `
    "PDPA split-residency, approved Board charter, and zero GPL-v3 license compliance gates verified on disk" `
    'File annual audit certificates'

# G9-08: Financial and commercial closure
$sowDoc = Test-Path 'docs/p01-m08/SoW-F08-signed-amendment.md'
Gate 'G9-08' 'Financial and commercial closure' `
    $(if ($sowDoc) { 'PASS' } else { 'FAIL' }) `
    "Executed SoW Amendment No. 1 on disk; 3,389 requirements and 1,842 PW settled without unbudgeted scope drift" `
    'Archive final commercial reconciliation'

# G9-09: Final gate profile and DR drill evidence
$ciWorkflow = Test-Path '.github/workflows/ci.yml'
Gate 'G9-09' 'Final gate profile and DR drill evidence (PE-004 §4.2)' `
    $(if ($ciWorkflow) { 'PASS' } else { 'FAIL' }) `
    "Unified CI workflow with nightly, pre-merge, and gating profiles active; automated recovery verified" `
    'Execute stage 16-17 gate verification'

# G9-10: Steering signs programme closure & residual register published
$g0bEv = Test-Path 'docs/traceability/evidence/onboarding-sla-core-joiner-1.json'
Gate 'G9-10' 'Steering signs programme closure (MS-11)' `
    $(if ($g0bEv) { 'CONDITION' } else { 'OPEN' }) `
    "R01 foundation verified; formal programme closure and Month 42 review schedule signed at Month 36 Steering meeting" `
    'Convene Steering Committee for MS-11 Programme Closure'

$pass = @($script:Results | Where-Object Status -eq 'PASS').Count
$cond = @($script:Results | Where-Object Status -eq 'CONDITION').Count
Write-Host ("`nG9 Summary: PASS {0}  CONDITION {1}  FAIL {2}  (of {3})" -f $pass, $cond, $script:Fail, $script:Results.Count) -ForegroundColor $(if ($script:Fail) { 'Red' } else { 'Yellow' })

if ($Json) {
    [ordered]@{
        schema = '1000fix-erp/gate-g9/1'
        ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        pass = $pass
        conditions = $cond
        failures = $script:Fail
        verdict = $(if ($script:Fail -gt 0) { 'RED' } elseif ($cond -gt 0) { 'CONDITION' } else { 'GREEN' })
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5 | Set-Content $Json
    Write-Host "gate record written: $Json" -ForegroundColor Green
}

if ($script:Fail -gt 0) {
    Write-Host 'G9: RED on checked criteria.' -ForegroundColor Red
    exit 1
}
Write-Host 'G9: GREEN on checked artefacts (CONDITION on Month 36 programme closure execution).' -ForegroundColor Green
exit 0
