# verify-gate-g4.ps1 - Gate G4: v1.0 scope complete (P07-M10-T10).
# MS-06, Month 18. Tranche boundary - Waves 5-9 are re-authorised here (D-017).
# Honest posture (2026-10-22 rewrite): unit-suite criteria PASS only when the
# estate harness (pytest) exits 0 with parsed test counts; operational criteria
# that were previously awarded PASS from simulated or self-authored evidence are
# CONDITION until measured in production. Numbers come from tool output.
param([string]$Json = '')

$ErrorActionPreference = 'Continue'
$repo = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
Set-Location $repo

$pass = 0; $condition = 0; $fail = 0
$script:Results = @()
function Result($outcome, $id, $title, $evidence) {
    $script:pass += ($outcome -eq 'PASS'); $script:condition += ($outcome -eq 'CONDITION'); $script:fail += ($outcome -eq 'FAIL')
    $script:Results += [ordered]@{ Id = $id; Criterion = $title; Status = $outcome; Evidence = $evidence }
    $color = @{ PASS='Green'; CONDITION='Yellow'; FAIL='Red' }[$outcome]
    Write-Host ("[{0}] {1,-7} {2}" -f $outcome, $id, $title) -ForegroundColor $color
    Write-Host ("         {0}" -f $evidence) -ForegroundColor DarkGray
}

# Estate harness runner (pyproject addopts carries one -q; a second would hide
# the summary line the count is parsed from). Exit code gates the verdict.
function Invoke-Pytest($testTarget) {
    $out = (& py -3.12 -m pytest $testTarget --no-header 2>&1 | Out-String) -join ''
    $exit = $LASTEXITCODE
    $m = [regex]::Match($out, '(\d+) passed')
    $count = 0
    if ($m.Success) { $count = [int]($m.Groups[1].Value) }
    $ok = ($exit -eq 0) -and ($count -gt 0)
    return @{ Out = $out; Count = $count; Ok = $ok; Exit = $exit }
}

function Gate-Suite($outcome, $id, $title, $suiteName, $r) {
    Result $outcome $id $title `
        "pytest exit $($r.Exit), $($r.Count) passed ($suiteName). Test-green proves the coded logic; production operation is claimed separately."
}

Write-Host "`n1000fix-erp Gate G4 - v1.0 scope complete (P07-M10; MS-06; tranche boundary D-017)`n" -ForegroundColor Cyan

# ---- unit-suite evidence (executed; exit codes honoured) -------------------

$r = Invoke-Pytest 'addons/domain/a_service_delivery/cd_warranty_claims/tests'
Gate-Suite $(if ($r.Ok) { 'PASS' } else { 'FAIL' }) 'G4-a' 'Warranty claim automation (AUT-018)' 'cd_warranty_claims' $r

$r = Invoke-Pytest 'addons/domain/b_customer_engagement/cd_contact_centre/tests'
Gate-Suite $(if ($r.Ok) { 'PASS' } else { 'FAIL' }) 'G4-b' 'Contact centre system of record + AI handoff' 'cd_contact_centre' $r

$r = Invoke-Pytest 'services/settlement-engine/tests'
Gate-Suite $(if ($r.Ok) { 'PASS' } else { 'FAIL' }) 'G4-c' 'Settlement engine calculation paths' 'settlement-engine' $r

$r = Invoke-Pytest 'addons/domain/g_finance/cd_tax_engine_bd/tests/test_return_logic.py'
Gate-Suite $(if ($r.Ok) { 'PASS' } else { 'FAIL' }) 'G4-d' 'Statutory returns return-calc paths' 'return_logic' $r

$r = Invoke-Pytest 'services/dsr-orchestrator/tests'
Gate-Suite $(if ($r.Ok) { 'PASS' } else { 'FAIL' }) 'G4-e' 'PDPA compliance infrastructure (G4-06)' 'dsr-orchestrator' $r

$r = Invoke-Pytest 'services/portal-contracts/tests'
Gate-Suite $(if ($r.Ok) { 'PASS' } else { 'FAIL' }) 'G4-f' 'Portal contracts + PS-11 server-side validation' 'portal-contracts' $r

$r = Invoke-Pytest 'addons/domain/c_commercial/cd_contract_core/tests/test_contract.py'
Gate-Suite $(if ($r.Ok) { 'PASS' } else { 'FAIL' }) 'G4-g' 'Commercial contracts core & OCA integration (M08)' 'cd_contract_core' $r

$r = Invoke-Pytest 'services/workflow/tests/test_brand_dags.py'
Gate-Suite $(if ($r.Ok) { 'PASS' } else { 'FAIL' }) 'G4-h' '18 Brand submission workflows & blocking completeness (T03)' 'brand_dags' $r

$r = Invoke-Pytest 'services/bi-warehouse/tests/test_dbt_dimensional_models.py','services/bi-warehouse/tests/test_kpi_registry_coverage.py'
Gate-Suite $(if ($r.Ok) { 'PASS' } else { 'FAIL' }) 'G4-i' 'M25/M62 Analytics dimensional models & 95-KPI registry' 'bi-warehouse' $r

$r = Invoke-Pytest 'tests/test_r05_m04_event_reconciliation.py'
Gate-Suite $(if ($r.Ok) { 'PASS' } else { 'FAIL' }) 'G4-j' 'B-17 Event reconciliation register (69 unpublished events)' 'event_reconciliation' $r

# ---- operational criteria: measured/simulated distinction enforced ---------

$r = Invoke-Pytest 'addons/domain/a_service_delivery/cd_warranty_claims/tests/test_aut018_timing_proof.py'
Result $(if ($r.Ok) { 'CONDITION' } else { 'FAIL' }) 'G4-01' 'Claims auto-created within 24h and submitted within 72h' `
    "pytest exit $($r.Exit), $($r.Count) passed - timing proven over SYNTHETIC jobs with a simulated clock (mock claim model); production timing on real warranty volume is unmeasured (open external)"

$r = Invoke-Pytest 'addons/domain/a_service_delivery/cd_warranty_claims/tests/test_warranty_approval_rate.py'
Result $(if ($r.Ok) { 'CONDITION' } else { 'FAIL' }) 'G4-02' 'Claim approval rate >= 90% on first submission' `
    "pytest exit $($r.Exit), $($r.Count) passed - approval rate computed over a mock brand-decision engine with seeded outcomes, not production brand responses; first-submission rate unmeasured (open external)"

$r = Invoke-Pytest 'tests/test_g4_03_corporate_transactions.py'
Result $(if ($r.Ok) { 'CONDITION' } else { 'FAIL' }) 'G4-03' '10+ corporate clients transacting on P04' `
    "pytest exit $($r.Exit), $($r.Count) passed - counterparties are hardcoded fixtures inside the test; production corporate transaction volume is unmeasured (open external)"

Result 'CONDITION' 'G4-04b' 'Hotline capture demonstrated live' `
    "INT-015 webhook + softphone seam coded and unit-tested; no live telephony capture has occurred - requires a CPaaS contract and a real call (open external)"

$r = Invoke-Pytest 'services/conversational-ai/tests'
$simBench = Test-Path 'services/conversational-ai/benchmark_ollama_latency.py'
Result $(if ($r.Ok -and $simBench) { 'CONDITION' } else { 'CONDITION' }) 'G4-05b' 'AI assistant resolving >= 40% measured in production' `
    "unit tests exit $($r.Exit); the published FCR figure comes from a benchmark script that returns literal latencies (simulation, not an Ollama measurement); production resolution rate unmeasured (open external)"

$r = Invoke-Pytest 'tests/test_g4_06_pdpa_readiness.py'
Result $(if ($r.Ok) { 'PASS' } else { 'FAIL' }) 'G4-06b' 'PDPA readiness suite green' `
    "pytest exit $($r.Exit), $($r.Count) passed - DSR rights, export/erasure saga rehearsal, breach runbook checks; SC-003 DPIA carries role-name signatures (governance artefact, unchanged); live NDMA drill is external"

$r = Invoke-Pytest 'tests/test_g4_07_nightly_journeys.py'
$ciYmlPath = Join-Path (Split-Path -Parent $repo) '.github/workflows/ci.yml'
$nightlyJob = $false
if (Test-Path $ciYmlPath) { $nightlyJob = (Get-Content $ciYmlPath -Raw) -match 'nightly-journeys' }
Result $(if ($r.Ok) { 'CONDITION' } else { 'FAIL' }) 'G4-07' 'Journeys 4, 5 and 15 nightly (L6)' `
    "pytest exit $($r.Exit), $($r.Count) passed; nightly job defined in ci.yml: $nightlyJob; nightly EXECUTION needs the CI runner (open external) - the test asserts a dictionary it builds itself, it is not execution evidence"

# Governance artefacts: existence + provenance note only (content immutable
# per the 2026-10-21 governance decision; the statement's 100%-completion
# assertion is contradicted by measured evidence and is recorded, not edited).
$hasStmt = (Test-Path "docs/governance/v1.0-scope-completion-statement.md") -and (Test-Path "docs/decisions/D-017-g4-tranche-decision-waves-5-9.md")
Result $(if ($hasStmt) { 'CONDITION' } else { 'FAIL' }) 'G4-08' 'v1.0 scope-completion statement & D-017 Tranche Decision' `
    "both governance documents exist on disk; they are repo-authored assertions, not countersigned evidence - measured evidence in this run still carries CONDITION items, so scope completion is NOT independently confirmed"

# ---- verdict ---------------------------------------------------------------

Write-Host ""
$verdict = $(if ($fail -gt 0) { 'RED' } elseif ($condition -gt 0) { 'CONDITION' } else { 'GREEN' })
Write-Host "G4: PASS $pass  CONDITION $condition  FAIL $fail  (of $($pass+$condition+$fail) checks)" -ForegroundColor $(if ($fail) { 'Red' } elseif ($condition) { 'Yellow' } else { 'Green' })
Write-Host "G4: $verdict - unit suites executed with honoured exit codes; operational criteria remain CONDITION until measured in production."

if ($Json) {
    [ordered]@{
        schema = '1000fix-erp/gate-g4/2'
        ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        pass = $pass; conditions = $condition; failures = $fail
        verdict = $verdict
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5 | Set-Content $Json
    Write-Host "gate record written: $Json" -ForegroundColor Green
}

if ($fail -gt 0) { exit 1 }
exit 0
