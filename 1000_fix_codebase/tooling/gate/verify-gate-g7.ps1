# verify-gate-g7.ps1 - Gate G7: Marketplace go-live (P10-M10-T10).
# MS-09, Month 30. 10 criteria mapped to P10-M10-T01..T09.
# Honest posture (2026-10-22 rewrite): PASS only from an executed check whose
# exit code was honoured; existence/grep findings read as CONDITION
# ("artefact present, not measured"); FAIL blocks. Numbers come from tool
# output or from evidence JSON a script generated - hand-written JSON with no
# generator script is never read as evidence.
param([string]$Json = '')

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
Set-Location $repo
$ErrorActionPreference = 'Continue'   # native test output is not an error state

$pass = 0; $condition = 0; $fail = 0
$script:Results = @()
function Result($outcome, $id, $title, $evidence) {
    $script:pass += ($outcome -eq 'PASS'); $script:condition += ($outcome -eq 'CONDITION'); $script:fail += ($outcome -eq 'FAIL')
    $script:Results += [ordered]@{ Id = $id; Criterion = $title; Status = $outcome; Evidence = $evidence }
    $color = @{ PASS='Green'; CONDITION='Yellow'; FAIL='Red' }[$outcome]
    Write-Host ("[{0}] {1,-7} {2}" -f $outcome, $id, $title) -ForegroundColor $color
    Write-Host ("         {0}" -f $evidence) -ForegroundColor DarkGray
}

# Runs the estate's harness (pytest, per pyproject) over a target and returns
# @{ Out=..; Count=N; Ok=bool; Exit=N }. pyproject addopts already carries one
# -q; adding another would suppress the summary line the count is parsed from.
# Counts come from pytest's own summary; the exit code gates Ok.
function Invoke-Unittest([string]$testDir) {
    $out = (& py -3.12 -m pytest $testDir --no-header 2>&1 | Out-String) -join ''
    $exit = $LASTEXITCODE
    $m = [regex]::Match($out, '(\d+) passed')
    $count = 0
    if ($m.Success) { $count = [int]($m.Groups[1].Value) }
    $ok = ($exit -eq 0) -and ($count -gt 0)
    return @{ Out = $out; Count = $count; Ok = $ok; Exit = $exit }
}

# ---- evidence readers (GV-009) ---------------------------------------------
# A criterion that cites evidence reads its verdict and its numbers from
# evidence JSON a tool measured; it never asserts them. An absent or
# unparsable file reads as MISSING, a value the tool did not measure as
# UNMEASURED.
function Read-EvidenceJson([string]$path) {
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    try { return (Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json) } catch { return $null }
}
function Get-EvidenceVerdict($ev) {
    if ($null -eq $ev) { return 'MISSING' }
    foreach ($holder in @($ev, $ev.summary, $ev.results)) {
        if ($null -eq $holder) { continue }
        foreach ($key in @('verdict', 'overall_verdict', 'overall_status', 'status')) {
            $value = $holder.$key
            if ($value -is [string] -and $value.Length -gt 0) { return $value.ToUpperInvariant() }
        }
    }
    return 'UNKNOWN'
}
function Get-OutcomeFromVerdicts([string[]]$verdicts, [string]$missingOutcome) {
    # PASS only when every verdict is PASS; FAIL when any evidence reports
    # FAIL; $missingOutcome when evidence is absent; CONDITION otherwise
    # (INCOMPLETE / UNPROVEN / UNMEASURED / UNKNOWN - the run could not observe it).
    $verdicts = @($verdicts)
    if ($verdicts.Count -eq 0) { return 'CONDITION' }
    if ($verdicts -contains 'FAIL') { return 'FAIL' }
    if ($verdicts -contains 'MISSING') { return $missingOutcome }
    if (@($verdicts | Where-Object { $_ -ne 'PASS' }).Count -eq 0) { return 'PASS' }
    return 'CONDITION'
}
function Format-Measured($value, [string]$unit = '') {
    if ($null -eq $value) { return 'UNMEASURED' }
    return ('{0}{1}' -f $value, $unit)
}
function Get-DrMetric($ev, [string[]]$keys) {
    # First non-null value of $keys in the drill's metrics block ($null = not measured).
    if ($null -eq $ev) { return $null }
    foreach ($block in @($ev.measured_metrics, $ev.sla_metrics, $ev.metrics)) {
        if ($null -eq $block) { continue }
        foreach ($key in $keys) {
            if ($null -ne $block.$key) { return $block.$key }
        }
    }
    return $null
}
function Get-DrDrill([string]$path) {
    # PE-007 DR drill outcome: verdict, RPO and RTO all come from the drill
    # evidence. A PASS verdict without a measured RPO and RTO reads as
    # INCOMPLETE - a drill that measured neither cannot have passed.
    $ev = Read-EvidenceJson $path
    $verdict = Get-EvidenceVerdict $ev
    $rpo = Get-DrMetric $ev @('rpo_measured_seconds', 'rpo_achieved_seconds')
    $rto = Get-DrMetric $ev @('rto_measured_seconds', 'rto_achieved_seconds')
    $dataLoss = Get-DrMetric $ev @('data_loss_records')
    $effective = $verdict
    if ($verdict -eq 'PASS' -and ($null -eq $rpo -or $null -eq $rto)) { $effective = 'INCOMPLETE' }
    $tally = 'check tally not recorded'
    $s = $ev.summary
    if ($null -eq $s) { $s = $ev.drill_summary }
    if ($null -ne $s -and $null -ne $s.checks_total) {
        $tally = '{0} PASS / {1} FAIL / {2} UNMEASURED of {3} checks' -f $s.checks_passed, $s.checks_failed, $s.checks_unmeasured, $s.checks_total
    }
    return [PSCustomObject]@{
        Verdict  = $effective
        DataLoss = $dataLoss
        Text     = "PE-007 DR drill verdict=$verdict, RPO=$(Format-Measured $rpo 's'), RTO=$(Format-Measured $rto 's'), data loss records=$(Format-Measured $dataLoss), $tally [$path]"
    }
}
function Get-ModuleCensus {
    # Manifests counted here + FF-23 (every cd_* module has a manifest and tests).
    # Excluded directories match as whole path segments, so cd_vendor_portal counts.
    $manifests = (Get-ChildItem addons -Recurse -Filter __manifest__.py -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '[\\/](__pycache__|vendor|\.mimosa)[\\/]' } | Measure-Object).Count
    $out = (& py -3.12 tooling/fitness/check_tests_present.py 2>&1 | Out-String).Trim()
    $ok = ($LASTEXITCODE -eq 0) -and ($manifests -gt 0)
    $first = @($out -split "`r?`n")[0]
    return [PSCustomObject]@{ Ok = $ok; Text = "$manifests manifests; FF-23: $first" }
}

$evDir = 'docs/traceability/evidence'
$fitEvDir = 'tooling/fitness/evidence'

Write-Host "`n1000fix-erp Gate G7 - Marketplace go-live (P10-M10; MS-09; Month 30)`n" -ForegroundColor Cyan

# ---- G7-1: T-6 entry: fitness clean ----
# fitness-*.json is generated by tooling/fitness/run.py; its FAIL tally is a
# machine measurement and reads at face value.
$fitJson = Get-ChildItem tooling/fitness/evidence/fitness-*.json |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$fitFailures = 0
if ($fitJson) {
    $fitData = Get-Content $fitJson.FullName | ConvertFrom-Json
    $fitFailures = (@($fitData.results) | Where-Object { $_.status -eq 'FAIL' } | Measure-Object).Count
    Result $(if ($fitFailures -eq 0) { 'PASS' } else { 'FAIL' }) 'G7-1' 'T-6 entry: fitness clean' "$fitFailures failures ($($fitJson.Name))"
} else {
    Result 'FAIL' 'G7-1' 'T-6 entry: fitness clean' "no fitness evidence found - run tooling/fitness/run.py"
}

# ---- executed unittest evidence (G7-2/3/4/8 share the two suites) ----------
$mkt = Invoke-Unittest 'addons/domain/d_circular/cd_marketplace/tests'
$settle = Invoke-Unittest 'addons/domain/g_finance/cd_settlement_ext/tests'

# ---- G7-2: sellers onboarded and transacting ----
# Mechanics are executed (marketplace suite); onboarding scale is machine-
# evidenced but in the sandbox DB; "transacting" (real GMV) is unmeasured.
$pilot = Read-EvidenceJson "$fitEvDir/pilot-onboarded-cohort.json"
$pilotLive = $pilot.total_sellers_live
Result $(if ($mkt.Ok) { 'CONDITION' } else { 'FAIL' }) 'G7-2' 'Sellers onboarded and transacting' `
    "marketplace suite exit $($mkt.Exit), $($mkt.Count) tests (seller party-role, KYC gate, commission.earned event, tenant isolation negatives); pilot onboarding tool measured $(Format-Measured $pilotLive) sellers live - in the PE-002 sandbox DB (fix_dev), not production; transacting (real transaction volume) is unmeasured (open external)"

# ---- G7-3: payout accuracy 100% (M53 behind it) ----
# The settlement engine is executed end to end (TDS math, SoD gate, rail,
# reconciliation); "100% payout accuracy" is a production-volume property.
Result $(if ($settle.Ok) { 'CONDITION' } else { 'FAIL' }) 'G7-3' 'Payout accuracy (M53 settlement)' `
    "settlement suite exit $($settle.Exit), $($settle.Count) tests incl. the commission->TDS->net->payout e2e with SoD approval gate and rail read-back; payout accuracy over production payout volume is unmeasured (open external) - test green is not a 100% accuracy measurement"

# ---- G7-4: journey 7 automated ----
$j7Spec = Test-Path 'tooling/e2e/journeys/j08-marketplace-seller.spec.ts'
Result $(if ($mkt.Ok) { 'CONDITION' } else { 'FAIL' }) 'G7-4' 'Journey 7 automated' `
    "marketplace suite exit $($mkt.Exit) incl. journey-7 state machine (order->quote->selection->job->review->commission->paid asserted in test_journey_seven_states); L6 spec j08-marketplace-seller.spec.ts present=$j7Spec; L6 EXECUTION requires the CI runner (open external) - a state-machine unit test is not a journey run"

# ---- G7-5: all portals delivered ----
# Executed: each named portal manifest must exist and literal_eval to a named
# dict (a broken/missing manifest is a defect -> FAIL). Delivery at scale is
# operational and stays CONDITION.
$portalCode = @'
import ast, pathlib
dirs = ['cd_corporate_portal', 'cd_vendor_portal', 'cd_msp_contract', 'cd_marketplace']
bad = []; ok = 0
for d in dirs:
    hits = [p for p in pathlib.Path('addons').rglob('__manifest__.py') if p.parent.name == d]
    if not hits:
        bad.append(d + ': no manifest'); continue
    try:
        obj = ast.literal_eval(hits[0].read_text(encoding='utf-8'))
    except Exception:
        bad.append(d + ': manifest unparsable'); continue
    if isinstance(obj, dict) and obj.get('name'):
        ok += 1
    else:
        bad.append(d + ': manifest not a named dict')
print(ok); print('; '.join(bad))
'@
$portalOut = (& py -3.12 -c $portalCode 2>&1 | Out-String).Trim()
$portalExit = $LASTEXITCODE
$portalLines = @(($portalOut -split "`r?`n") | Where-Object { $_.Trim() })
$portalOkParsed = 0
if ($portalLines.Count -ge 1) { $portalOkParsed = [int]$portalLines[0] }
$portalBad = $(if ($portalLines.Count -gt 1) { $portalLines[1] } else { '' })
Result $(if (($portalExit -eq 0) -and ($portalOkParsed -eq 4) -and (-not $portalBad)) { 'CONDITION' } else { 'FAIL' }) 'G7-5' 'Portals delivered' `
    "manifest parse exit ${portalExit}: $portalOkParsed of 4 portal manifests parse to a named dict (problems: $(if ($portalBad) { $portalBad } else { 'none' })); operational delivery across the 12-portal estate is unmeasured (production runtime, open external)"

# ---- G7-6: cross-tenant isolation (R08-M04) ----
# Known tool limitations (2026-10-22 review), reported WITH their outputs:
# - loadtest-tenant-isolation.py's cross-tenant probe embeds the isolation
#   filter in its own SQL predicate (seller_id = B AND partner_id = A -
#   structurally empty) over a direct DB connection, so its 0-leak PASS is
#   true by construction and bypasses Odoo record rules entirely;
# - pentest-external-surfaces.py fails open (transport errors and rejected
#   unauthenticated probes count as clean).
# Their PASS verdicts are therefore downgraded to UNPROVEN here; a FAIL from
# either still reads as FAIL. The permission negative suite executed its test
# file against the live DB and reads at face value.
$tJson = Read-EvidenceJson "$fitEvDir/tenant-isolation-scale-evidence.json"
$pJson = Read-EvidenceJson "$fitEvDir/external-surfaces-pentest-report.json"
$cJson = Read-EvidenceJson "$fitEvDir/pilot-onboarded-cohort.json"
$nJson = Read-EvidenceJson "$fitEvDir/permission-negative-suite-latest.json"
$tVerdict = Get-EvidenceVerdict $tJson
$pVerdict = Get-EvidenceVerdict $pJson
$cVerdict = Get-EvidenceVerdict $cJson
$nVerdict = Get-EvidenceVerdict $nJson
$nSuite = $nJson.results.test_suite
$tEffective = $(if ($tVerdict -eq 'PASS') { 'UNPROVEN' } else { $tVerdict })
$pEffective = $(if ($pVerdict -eq 'PASS') { 'UNPROVEN' } else { $pVerdict })
Result (Get-OutcomeFromVerdicts @($tEffective, $pEffective, $cVerdict, $nVerdict) 'CONDITION') 'G7-6' 'Cross-tenant isolation' `
    ("scale loadtest verdict=$tVerdict (synthetic sellers=$(Format-Measured $tJson.results.synthetic_sellers_count), " +
     "cross-tenant leaks=$(Format-Measured $tJson.results.cross_tenant_leakage_count), p95=$(Format-Measured $tJson.results.latency_metrics_ms.p95 'ms')) - its leak probe is empty by construction and bypasses Odoo record rules, so the PASS is UNPROVEN; " +
     "external-surface pen-test verdict=$pVerdict (0 findings recorded) - the tool fails open on transport errors, so the PASS is UNPROVEN; " +
     "pilot cohort verdict=$cVerdict (sellers live=$(Format-Measured $cJson.total_sellers_live), sandbox DB); " +
     "permission negative suite verdict=$nVerdict (executed test file: exit=$(Format-Measured $nSuite.exit_code), $(Format-Measured $nSuite.tests_run) run / $(Format-Measured $nSuite.tests_failed) failed); " +
     "a real isolation measurement through the Odoo runtime is in progress separately")

# ---- G7-7: branches live (R08-M05) ----
# PASS needs the rollout evidence verdict PASS with >= 51 centres measured live.
$rbRunbook = Test-Path docs/runbooks/RB-51-branch-rollout-runbook.md
$brJson = Read-EvidenceJson "$fitEvDir/branch-rollout-evidence.json"
$brVerdict = Get-EvidenceVerdict $brJson
$brLive = $brJson.total_service_centres_live
$brEffective = $brVerdict
if ($brVerdict -eq 'PASS') {
    if ($null -eq $brLive) { $brEffective = 'INCOMPLETE' } elseif ($brLive -lt 51) { $brEffective = 'FAIL' }
}
$g7_7 = @($brEffective)
if (-not $rbRunbook) { $g7_7 += 'MISSING' }
Result (Get-OutcomeFromVerdicts $g7_7 'CONDITION') 'G7-7' 'All 51+ branches live' `
    "branch rollout verdict=$brVerdict; service centres live=$(Format-Measured $brLive) of $(Format-Measured $brJson.total_service_centres_registered) registered (criterion: >= 51); RB-51 runbook present=$rbRunbook"

# ---- G7-8: commission GL reconciliation ----
Result $(if ($settle.Ok) { 'PASS' } else { 'FAIL' }) 'G7-8' 'Commission GL reconciliation' `
    "settlement suite exit $($settle.Exit), $($settle.Count) tests incl. action_post_to_gl ORM tests (FF-91 single-source + contra-posting reversibility) and reconcile_payout_run count/amount balance assertions with zero aged breaks; period-end tie-out against the live Odoo ledger is operational follow-up, not measured here"

# ---- G7-9: gate profile (PE-004 & PE-007) ----
# PE-004/PE-007 verdicts, RPO and RTO are read from tool-generated evidence.
# Steering sign-off is a human execution that has not happened: the
# hand-authored gate-g7-signed-report.json has NO generator script and is
# deliberately not read as evidence. Sign-off pending caps the criterion at
# CONDITION even if both profiles measured PASS.
$perfPath = "$evDir/g7-pe004-performance-evidence.json"
$perfVerdict = Get-EvidenceVerdict (Read-EvidenceJson $perfPath)
$dr = Get-DrDrill "$evDir/g7-pe007-dr-drill-evidence.json"
$g7_9outcome = Get-OutcomeFromVerdicts @($perfVerdict, $dr.Verdict) 'CONDITION'
if ($g7_9outcome -eq 'PASS') { $g7_9outcome = 'CONDITION' }
Result $g7_9outcome 'G7-9' 'Gate profile (PE-004 & PE-007)' `
    "PE-004 1.5x-peak profile verdict=$perfVerdict [$perfPath]; $($dr.Text); Steering sign-off pending (human execution, open) - the signed report on file is hand-authored with no generator and is not machine evidence"

# ---- G7-10: module census ----
$census = Get-ModuleCensus
Result $(if ($census.Ok) { 'PASS' } else { 'FAIL' }) 'G7-10' "All modules shipped" $census.Text

# ---- verdict ---------------------------------------------------------------

Write-Host ""
$verdict = $(if ($fail -gt 0) { 'RED' } elseif ($condition -gt 0) { 'CONDITION' } else { 'GREEN' })
Write-Host "G7: PASS $pass  CONDITION $condition  FAIL $fail  (of $($pass+$condition+$fail) checks)" -ForegroundColor $(if ($fail) { 'Red' } elseif ($condition) { 'Yellow' } else { 'Green' })
Write-Host "G7: $verdict - executed checks honoured; CONDITION items need production volume, the Odoo-runtime isolation test and human Steering sign-off."

if ($Json) {
    [ordered]@{
        schema = '1000fix-erp/gate-g7/2'
        ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        pass = $pass; conditions = $condition; failures = $fail
        verdict = $verdict
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5 | Set-Content $Json
    Write-Host "gate record written: $Json" -ForegroundColor Green
}

if ($fail -gt 0) { exit 1 }
exit 0
