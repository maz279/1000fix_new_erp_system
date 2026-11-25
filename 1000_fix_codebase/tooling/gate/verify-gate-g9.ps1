# =============================================================================
# verify-gate-g9.ps1 - P12-M10-T10: Gate G9 (Programme closure, MS-11, Month 36).
# Assessed by Steering Committee, on evidence. 10 criteria.
# GV-009: an assertion is not evidence - each criterion names its artefact.
# Criteria:
#   G9-01  Entry criteria check at T-6 weeks (GV-009 section 9.2)
#   G9-02  Multi-entity and multi-country readiness (M65) demonstrated
#   G9-03  Legacy estate decommissioned with reconciliation sign-off (MIG-08)
#   G9-04  Delivery completeness (IR-002 P12-M10-T04: 67 modules, 12 portals,
#          47 integrations, 122 NFRs, 452 content files; 331 CD items, 60 automations)
#   G9-05  Transition to support accepted by support organisation (P12-M04-T09)
#   G9-06  Benefits measurement operating against BM-002 baselines (BM-004)
#   G9-07  Security, compliance and audit closure (PDPA, ISO 27001, licence)
#   G9-08  Financial and commercial closure (SoW Amendment No. 1 scope settlement)
#   G9-09  Final gate profile and DR drill evidence (PE-004 section 4.2)
#   G9-10  Steering signs programme closure; residual register published
#
# Posture (GV-009 - an assertion is not evidence):
#   PASS only on a machine-produced measurement or a genuine countersigned record;
#   CONDITION when only code, registers or repo-authored narrative/JSON exist
#     (closure outcomes are Month 36 operational events - this is a dev repo);
#   OPEN when a Steering/human sign-off is outstanding;
#   FAIL on missing prerequisites.
# Verdict: GREEN - PASS-WITH-CONDITIONS - RED-OPEN (any OPEN) - RED (any FAIL).
# Exit: 0 GREEN or PASS-WITH-CONDITIONS - 1 any FAIL or OPEN - 2 preconditions.
# =============================================================================
[CmdletBinding()]
param([string]$Json = '', [switch]$Strict)
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root
$script:Results = @(); $script:Fail = 0; $script:Cond = 0; $script:Open = 0
$evDir = 'docs/traceability/evidence'

function Gate([string]$Id, [string]$Crit, [string]$Status, [string]$Ev, [string]$Rem = '') {
    $script:Results += [pscustomobject]@{
        Id = $Id; Criterion = $Crit; Status = $Status; Evidence = $Ev; Remedy = $Rem
        CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
    }
    $c = if ($Status -eq 'PASS') { 'Green' } elseif ($Status -eq 'CONDITION') { 'Yellow' } else { 'Red' }
    Write-Host ("[{0}] {1,-8} {2}" -f $Status, $Id, $Crit) -ForegroundColor $c
    Write-Host ("         {0}" -f $Ev) -ForegroundColor DarkGray
    if ($Status -eq 'FAIL') { $script:Fail++ }
    elseif ($Status -eq 'CONDITION') { $script:Cond++ }
    elseif ($Status -eq 'OPEN') { $script:Open++ }
}
function Read-JsonSafe([string]$Path) {
    try { return (Get-Content $Path -Raw -Encoding UTF8 | ConvertFrom-Json) } catch { return $null }
}

Write-Host "`n1000fix-erp Gate G9 - Programme closure (P12-M10; MS-11; Month 36)`n" -ForegroundColor Cyan

# G9-01: Entry criteria check at T-6 weeks - read the NEWEST fitness evidence and count FAILs.
$regDoc = Test-Path 'docs/traceability/coverage-baseline-register.md'
$fitJson = Get-ChildItem 'tooling/fitness/evidence' -Filter 'fitness-*.json' -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
$blockingIds = @()
if (Test-Path 'tooling/fitness/registry.yaml') {
    $cur = $null
    foreach ($l in (Get-Content 'tooling/fitness/registry.yaml' -Encoding UTF8)) {
        if ($l -match '^\s*-\s+id:\s*(FF-\S+)') { $cur = $Matches[1] }
        elseif ($cur -and $l -match '^\s+blocking:\s*true\s*$') { $blockingIds += $cur }
    }
}
$t6G9 = @(Get-ChildItem 'docs' -Recurse -Filter '*g9*t6*entry*.md' -ErrorAction SilentlyContinue)
$g901Ev = "coverage-baseline register: $regDoc; "
$g901Status = 'CONDITION'
if (-not $fitJson) { $g901Status = 'FAIL'; $g901Ev += 'no fitness evidence JSON (tooling/fitness/evidence/fitness-*.json)' }
else {
    $fj = Read-JsonSafe $fitJson.FullName
    $res = @($fj.results)
    $fails = @($res | Where-Object { $_.status -eq 'FAIL' })
    $blkFails = @($fails | Where-Object { $blockingIds -contains $_.suite } | ForEach-Object { $_.suite })
    $g901Ev += "newest $($fitJson.Name): $($res.Count) results, $(@($res | Where-Object status -eq 'PASS').Count) PASS / $($fails.Count) FAIL / $(@($res | Where-Object status -eq 'SKIP').Count) SKIP; blocking FAILs: $(if ($blkFails.Count) { $blkFails -join ',' } else { 'none' }); "
}
$g901Ev += $(if ($t6G9.Count) { "G9 T-6 record: $($t6G9[0].Name)" } else { 'no G9 T-6 entry-criteria record (Month 36 review not yet held)' })
Gate 'G9-01' 'T-6 entry criteria check complete' $g901Status $g901Ev 'Hold the G9 T-6 entry review with a clean blocking fitness run and record it'

# G9-02: Multi-entity & multi-country readiness (M65) demonstrated
# R10's multi-entity module is cd_multi_entity (consolidation, FX, eliminations);
# cd_entity_config carries the BD country pack. Check both, name both.
$entityModel = Test-Path 'addons/platform/cd_multi_entity/models/fix_consolidation.py'
$countryModel = Test-Path 'addons/platform/cd_entity_config/models/fix_country_pack.py'
$residencyDoc = Test-Path 'docs/decisions/D-013-split-residency.md'
Gate 'G9-02' 'Multi-entity & multi-country readiness (M65)' `
    $(if ($entityModel -and $countryModel -and $residencyDoc) { 'CONDITION' } else { 'FAIL' }) `
    "cd_multi_entity/fix_consolidation.py: $entityModel; cd_entity_config/fix_country_pack.py: $countryModel; D-013: $residencyDoc - models on disk are not a demonstration; no multi-entity / second-country run evidence read" `
    'Demonstrate a second legal entity and country pack end-to-end and archive the run evidence'

# G9-03: Legacy estate decommissioned with reconciliation sign-off (MIG-08)
$legacyProfiles = Test-Path 'docs/p01-m07/legacy-source-profiles-completed.md'
$decomPath = "$evDir/r11-m02-decommission-register.json"
$decomNote = 'no decommission register JSON'
if (Test-Path $decomPath) {
    $dj = Read-JsonSafe $decomPath
    if ($dj) {
        $ds = $dj.disposition_summary
        $decomNote = "r11-m02-decommission-register.json claims: $($ds.retirable_sources_decommissioned_d7) D7-decommissioned, $($ds.deliberately_retained_sources_k) retained, $($ds.purge_disposition_sources_p) purge, $($ds.non_system_sources_transitioned_n) transitioned, $($ds.total_estate_accounted_for)/48 accounted; overall_status $($dj.overall_status); dated $($dj.execution_timestamp) - repo-authored JSON (no system-produced decommission certificates), and Month 36 decommission cannot have occurred in this dev repo"
    } else { $decomNote = 'r11-m02-decommission-register.json unreadable' }
}
Gate 'G9-03' 'Legacy estate decommissioned (MIG-08)' `
    $(if ($legacyProfiles) { 'CONDITION' } else { 'FAIL' }) `
    "legacy profiles: $legacyProfiles; $decomNote" `
    'Complete final cutover and decommissioning certificates across all 48 legacy sources'

# G9-04: Delivery completeness - measured counts vs IR-002 P12-M10-T04
$shippedModules = @(Get-ChildItem addons -Recurse -Filter __manifest__.py -ErrorAction SilentlyContinue).Count
$cdPath = 'tooling/cd-register.yaml'
$mUnits = 0; $pUnits = 0; $cdCount = 0
if (Test-Path $cdPath) {
    $cdLines = @(Get-Content $cdPath -Encoding UTF8)
    $mUnits = @($cdLines | Select-String -Pattern '^\s+unit:\s*(M\d+)' | ForEach-Object { $_.Matches[0].Groups[1].Value } | Sort-Object -Unique).Count
    $pUnits = @($cdLines | Select-String -Pattern '^\s+unit:\s*(P\d+)' | ForEach-Object { $_.Matches[0].Groups[1].Value } | Sort-Object -Unique).Count
    $cdCount = @($cdLines | Select-String -Pattern '^- id: CD-').Count
}
$autPath = 'addons/domain/i_governance/cd_workflow_engine/data/aut_register.yaml'
$autCount = if (Test-Path $autPath) { @(Select-String -Path $autPath -Pattern 'id:\s*AUT-').Count } else { 0 }
$webPortals = @(Get-ChildItem 'apps/web' -Directory -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path $_.FullName 'package.json') }).Count
$g904Status = if (-not (Test-Path $cdPath) -or -not (Test-Path $autPath)) { 'FAIL' } else { 'CONDITION' }
Gate 'G9-04' 'Delivery completeness (modules, portals, CD items, automations)' $g904Status `
    "measured: $shippedModules addon manifests; cd-register units $mUnits M (67 required) / $pUnits P (12 required); $cdCount CD items (IR-002 331); $autCount AUT entries (60 required); apps/web portal apps $webPortals (12 portals required); 47 integrations, 122 NFRs and 452 content files NOT measured by this verifier; register rows are not delivery acceptance" `
    'Produce a measured delivery-completeness report (modules/portals/integrations/NFRs/content) and accept it'

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

# G9-07: Security, compliance and audit closure - run the licence gate, report what it covers.
$licenceGate = Test-Path 'tooling/licence/register.yaml'
$auditDoc = Test-Path 'docs/governance/BM-2026-10-D001-charter-and-governance.md'
$licNote = 'licence gate not run'
if (Test-Path 'tooling/scripts/check-licence-gate.py') {
    $lo = (& python tooling/scripts/check-licence-gate.py 2>&1 | Out-String).Trim()
    $le = $LASTEXITCODE
    $licNote = "check-licence-gate.py exit $le ($(($lo -split "`r?`n" | Select-Object -Last 1)))"
    if ($lo -match 'no SBOM') { $licNote += ' - no SBOM: declared register entries only' }
}
$gpl3 = if ($licenceGate) { @(Select-String -Path 'tooling/licence/register.yaml' -Pattern '(?<!A)GPL-3' -ErrorAction SilentlyContinue).Count } else { 0 }
Gate 'G9-07' 'Security, compliance and audit closure' `
    $(if ($licenceGate -and $auditDoc -and $residencyDoc) { 'CONDITION' } else { 'FAIL' }) `
    "$licNote; register lines naming GPL-3 (non-AGPL): $gpl3; the gate's restricted markers do not include plain GPL-3, so 'zero GPL-v3' is NOT measured; no countersigned PDPA / ISO 27001 audit certificate read (r11-m03-* JSONs are repo-authored)" `
    'Run the licence gate over a full SBOM (incl. GPL-3 classification) and file the audit certificates'

# G9-08: Financial and commercial closure
$sowDoc = Test-Path 'docs/p01-m08/SoW-F08-signed-amendment.md'
$ccPath = "$evDir/r11-m04-commercial-closure-statement.json"
$ccNote = if (Test-Path $ccPath) { $cc = Read-JsonSafe $ccPath; "r11-m04-commercial-closure-statement.json states '$($cc.commercial_verdict)' (repo-authored JSON, not a countersigned closure)" } else { 'no commercial closure statement' }
Gate 'G9-08' 'Financial and commercial closure' `
    $(if ($sowDoc) { 'CONDITION' } else { 'FAIL' }) `
    "SoW Amendment No. 1 on disk: $sowDoc (a scope amendment is not a closure); $ccNote; no final commercial reconciliation read" `
    'Archive the countersigned final commercial reconciliation'

# G9-09: Final gate profile and DR drill evidence
$ciWorkflow = Test-Path '..\.github\workflows\ci.yml'
$drAll = @(Get-ChildItem $evDir -Filter '*dr-drill*.json' -ErrorAction SilentlyContinue)
$drG9 = @($drAll | Where-Object { $_.Name -match '^g9-' })
$drNote = if ($drG9.Count -gt 0) {
    $d = Read-JsonSafe $drG9[0].FullName; "$($drG9[0].Name): status $($d.status) (repo-authored JSON)"
} else { "no G9-scoped DR drill evidence; $($drAll.Count) drill JSON(s) for other gates ($(($drAll | ForEach-Object { $_.Name }) -join ', ')), all repo-authored" }
Gate 'G9-09' 'Final gate profile and DR drill evidence (PE-004 section 4.2)' `
    $(if ($ciWorkflow) { 'CONDITION' } else { 'FAIL' }) `
    "../.github/workflows/ci.yml present: $ciWorkflow (workflow existence is not a gate run; 'automated recovery' not verified); $drNote" `
    'Execute the stage 16-17 final gate profile and DR drill on target infrastructure'

# G9-10: Steering signs programme closure (no proxy: a signed report or OPEN)
$g9Signed = Test-Path "$evDir/gate-g9-signed-report.json"
Gate 'G9-10' 'Steering signs programme closure (MS-11)' `
    $(if ($g9Signed) { 'CONDITION' } else { 'OPEN' }) `
    $(if ($g9Signed) { 'gate-g9-signed-report.json on disk - a repo-authored JSON is not a countersigned Steering minute' } else { "no programme-closure sign-off ($evDir/gate-g9-signed-report.json); Month 36 Steering decision outstanding" }) `
    'Convene Steering Committee for MS-11 Programme Closure'

$pass = @($script:Results | Where-Object Status -eq 'PASS').Count
$verdict = if ($script:Fail -gt 0) { 'RED' } elseif ($script:Open -gt 0) { 'RED-OPEN' } elseif ($script:Cond -gt 0) { 'PASS-WITH-CONDITIONS' } else { 'GREEN' }
Write-Host ("`nG9 Summary: PASS {0}  CONDITION {1}  OPEN {2}  FAIL {3}  (of {4})  verdict {5}" -f $pass, $script:Cond, $script:Open, $script:Fail, $script:Results.Count, $verdict) -ForegroundColor $(if ($script:Fail -or $script:Open) { 'Red' } else { 'Yellow' })

if ($Json) {
    [System.IO.File]::WriteAllText($Json, ([ordered]@{
        schema = '1000fix-erp/gate-g9/2'
        ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        verdict = $verdict
        pass = $pass
        conditions = $script:Cond
        open = $script:Open
        failures = $script:Fail
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5))
    Write-Host "gate record written: $Json" -ForegroundColor Green
}

if ($script:Fail -gt 0) { Write-Host 'G9: RED on checked criteria.' -ForegroundColor Red; exit 1 }
if ($script:Open -gt 0) { Write-Host "G9: RED-OPEN - $($script:Open) Steering/human item(s) open." -ForegroundColor Red; exit 1 }
if ($script:Cond -gt 0) {
    Write-Host "G9: PASS-WITH-CONDITIONS ($($script:Cond) condition(s))." -ForegroundColor Yellow
    # -Strict: CI mode - conditions are not green; only GREEN exits 0.
    if ($Strict) { Write-Host 'G9: STRICT mode - conditions fail the CI gate.' -ForegroundColor Red; exit 1 }
    exit 0
}
Write-Host 'G9: GREEN.' -ForegroundColor Green
exit 0
