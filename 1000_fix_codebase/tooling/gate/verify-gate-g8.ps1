# verify-gate-g8.ps1 - Gate G8: Full intelligence go-live (P11-M10-T10).
# Honest posture (2026-10-22 rewrite): PASS only from an executed check whose
# exit code was honoured; existence/grep findings read as CONDITION
# ("artefact present, not measured"); FAIL blocks. Numbers come from tool
# output or from evidence JSON a script generated - hand-written JSON with no
# generator script (e.g. r09-m04-fitness-promotion-record.json,
# gate-g8-signed-report.json) is never read as evidence.
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
# @{ Out=..; Count=N; Failed=N; Ok=bool; Exit=N }. pyproject addopts already
# carries one -q; adding another (or clearing addopts) would drop
# --import-mode=importlib and suppress the summary line the counts are parsed
# from. Counts come from pytest's own summary; the exit code gates Ok.
function Invoke-Unittest([string[]]$pytestArgs) {
    $out = (& py -3.12 -m pytest @pytestArgs --no-header 2>&1 | Out-String) -join ''
    $exit = $LASTEXITCODE
    $count = 0
    $m = [regex]::Match($out, '(\d+) passed')
    if ($m.Success) { $count = [int]($m.Groups[1].Value) }
    $failed = 0
    $mf = [regex]::Match($out, '(\d+) failed')
    if ($mf.Success) { $failed = [int]($mf.Groups[1].Value) }
    $ok = ($exit -eq 0) -and ($count -gt 0)
    return @{ Out = $out; Count = $count; Failed = $failed; Ok = $ok; Exit = $exit }
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
function Get-OutcomeFromVerdicts([string[]]$verdicts, [string]$missingOutcome) {
    # PASS only when every verdict is PASS; FAIL when any evidence reports
    # FAIL; $missingOutcome when evidence is absent; CONDITION otherwise
    # (INCOMPLETE / UNMEASURED / UNKNOWN - the run could not observe it).
    $verdicts = @($verdicts)
    if ($verdicts.Count -eq 0) { return 'CONDITION' }
    if ($verdicts -contains 'FAIL') { return 'FAIL' }
    if ($verdicts -contains 'MISSING') { return $missingOutcome }
    if (@($verdicts | Where-Object { $_ -ne 'PASS' }).Count -eq 0) { return 'PASS' }
    return 'CONDITION'
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

Write-Host "`n1000fix-erp Gate G8 - Full intelligence go-live (P11-M10; MS-10; Month 34)`n" -ForegroundColor Cyan

# ---- G8-1: fitness clean ----
# fitness-*.json is generated by tooling/fitness/run.py; its FAIL tally is a
# machine measurement and reads at face value.
$fitJson = Get-ChildItem tooling/fitness/evidence/fitness-*.json |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$fitFailures = 0
if ($fitJson) {
    $fitData = Get-Content $fitJson.FullName | ConvertFrom-Json
    $fitFailures = (@($fitData.results) | Where-Object { $_.status -eq 'FAIL' } | Measure-Object).Count
    Result $(if ($fitFailures -eq 0) { 'PASS' } else { 'FAIL' }) 'G8-1' 'T-6 entry: fitness clean' "$fitFailures failures ($($fitJson.Name))"
} else {
    Result 'FAIL' 'G8-1' 'T-6 entry: fitness clean' "no fitness evidence found - run tooling/fitness/run.py"
}

# ---- G8-2: all modules and portals delivered ----
$census = Get-ModuleCensus
Result $(if ($census.Ok) { 'PASS' } else { 'FAIL' }) 'G8-2' 'All modules delivered' $census.Text

# ---- G8-3: warehouse migration (ClickHouse) ----
# Compose profile, model file and the NFR-086c string are artefact presence,
# not measurement. The executed part is the metric-registry suite; the
# migration itself (data moved, queries served from ClickHouse) is unmeasured.
$chCompose = Test-Path infra/compose/docker-compose.intelligence.yml
$nfr086c = Select-String -Path addons/domain/j_data_analytics/cd_metric_registry/models/fix_metric_registry.py -Pattern 'NFR-086c' -Quiet
$metric = Invoke-Unittest @('addons/domain/j_data_analytics/cd_metric_registry/tests')
Result $(if ($metric.Ok) { 'CONDITION' } else { 'FAIL' }) 'G8-3' 'Warehouse + data governance' `
    "metric-registry suite exit $($metric.Exit), $($metric.Count) tests (governance/residency logic) executed; compose profile present=$chCompose and NFR-086c residency string in the model=$nfr086c are artefact presence, not measurement; the warehouse migration itself is unmeasured - the ClickHouse container is not running in this environment (open external)"

# ---- G8-4: journey 10 (e-waste) + IoT ----
# Module logic is executed; the wipe-certificate grep is artefact presence;
# journey execution and live telemetry ingestion are unmeasured.
$wipeGate = Select-String -Path addons/domain/d_circular/cd_ewaste/models/fix_ewaste.py -Pattern 'wipe.certificate' -Quiet
$circular = Invoke-Unittest @('addons/domain/d_circular/cd_ewaste/tests', 'addons/domain/j_data_analytics/cd_stream_registry/tests')
Result $(if ($circular.Ok) { 'CONDITION' } else { 'FAIL' }) 'G8-4' 'Journey 10 + IoT telemetry' `
    "e-waste + stream-registry suites exit $($circular.Exit), $($circular.Count) tests executed; wipe-certificate destruction gate in source=$wipeGate (grep - artefact present, not measured); journey-10 EXECUTION (L6) and live IoT telemetry ingestion are unmeasured (open external)"

# ---- G8-5: KPIs instrumented (STT) ----
# The suite executes, but it exercises an echo: services/stt transcribe()
# returns the caller-supplied text - there is no acoustic model behind it, so
# the WER asserted in tests is fixture-typed formula checking, not a
# transcription measurement. The PDPA legal-basis refusal IS executed.
$stt = Invoke-Unittest @('services/stt/tests')
Result $(if ($stt.Ok) { 'CONDITION' } else { 'FAIL' }) 'G8-5' 'ML completion (STT + models)' `
    "services/stt suite exit $($stt.Exit), $($stt.Count) tests green - echo-level STT: transcribe() returns the caller-supplied text, no model behind it, so the measured WER in tests is fixture-typed, not a transcription measurement; the PDPA legal-basis refusal path is executed and asserted; a real Bengali WER measurement needs the acoustic model (open external)"

# ---- G8-6: fitness functions promoted to Blocking (R09-M04) ----
# The hand-authored r09-m04-fitness-promotion-record.json has no generator
# script and is NOT read as evidence. What is verifiable and executed here:
# (a) the registry declares FF-13/14/16/27 blocking (parsed, exit honoured);
# (b) each promoted check's own script runs green right now (exit honoured).
$regCode = @'
import re
t = open('tooling/fitness/registry.yaml', encoding='utf-8').read()
want = ['FF-13', 'FF-14', 'FF-16', 'FF-27']
blocks = {}
for b in t.split('\n  - id: '):
    bid = b.split('\n', 1)[0].strip()
    blocks[bid] = b
missing = [w for w in want if w not in blocks]
not_blocking = [w for w in want if w in blocks and not re.search(r'(?m)^\s+blocking:\s*true\s*$', blocks[w])]
print(len(want) - len(missing) - len(not_blocking)); print('; '.join(missing + not_blocking))
'@
$regOut = (& py -3.12 -c $regCode 2>&1 | Out-String).Trim()
$regExit = $LASTEXITCODE
$regLines = @(($regOut -split "`r?`n") | Where-Object { $_.Trim() })
$regBlocking = 0
if ($regLines.Count -ge 1) { $regBlocking = [int]$regLines[0] }
$regBad = $(if ($regLines.Count -gt 1) { $regLines[1] } else { '' })

$ff13 = (& py -3.12 tooling/fitness/check_api_budget.py 2>&1 | Out-String).Trim(); $ff13Exit = $LASTEXITCODE
$ff14 = (& powershell -NoProfile -ExecutionPolicy Bypass -File tooling/architecture-baseline/extract-dependency-graph.ps1 2>&1 | Out-String).Trim(); $ff14Exit = $LASTEXITCODE
$ff16 = (& py -3.12 tooling/scripts/check-cd-id.py 2>&1 | Out-String).Trim(); $ff16Exit = $LASTEXITCODE
$ff27 = (& py -3.12 tooling/fitness/check_portal_contract.py 2>&1 | Out-String).Trim(); $ff27Exit = $LASTEXITCODE
$ffExits = @($ff13Exit, $ff14Exit, $ff16Exit, $ff27Exit)
$ffNotGreen = @($ffExits | Where-Object { $_ -ne 0 }).Count
$ciYmlPath = Join-Path (Split-Path -Parent $repo) '.github/workflows/ci.yml'   # git root is the parent of the codebase
$ciFitness = $false
if (Test-Path $ciYmlPath) { $ciFitness = (Get-Content $ciYmlPath -Raw) -match 'fitness/run\.py' }
Result $(if (($regExit -eq 0) -and ($regBlocking -eq 4) -and (-not $regBad) -and ($ffNotGreen -eq 0)) { 'CONDITION' } else { 'FAIL' }) 'G8-6' 'Warning fitness functions blocking' `
    ("registry parse exit ${regExit}: $regBlocking of 4 promoted FFs declared blocking (problems: $(if ($regBad) { $regBad } else { 'none' })); executed now: FF-13 exit $ff13Exit (measured 0 OpenAPI contracts/clients - vacuous pass), FF-14 exit $ff14Exit, FF-16 exit $ff16Exit, FF-27 exit $ff27Exit; " +
     "CI runs the blocking set (model-registry job greps true in ci.yml: $ciFitness) - configuration, not an executed CI run here; the r09-m04 promotion record is hand-authored with no generator and is not read as evidence")

# ---- G8-7: regression core automated ----
$regression = Invoke-Unittest @('addons', '-p', 'no:cacheprovider')
$regFailedIds = @([regex]::Matches($regression.Out, '(?m)^FAILED\s+(\S+)') | ForEach-Object { $_.Groups[1].Value })
$regFailNote = ''
if ($regFailedIds.Count -gt 0) {
    $regFailNote = ' - failing: ' + (($regFailedIds | Select-Object -First 5) -join ', ')
    if ($regFailedIds.Count -gt 5) { $regFailNote += (' (+{0} more)' -f ($regFailedIds.Count - 5)) }
}
Result $(if ($regression.Ok) { 'PASS' } else { 'FAIL' }) 'G8-7' 'Automated regression' `
    "addons suite exit $($regression.Exit), $($regression.Count) passed, $($regression.Failed) failed$regFailNote - exit code honoured, today's failures are today's truth"

# ---- G8-8: security & full-estate DR (SC-009 / DoD-15 / PE-007) ----
# Pen-test, remediation and DR verdicts, finding counts, RPO, RTO and data loss
# are all read from the evidence; PASS only when every one is clean.
$pentestPath = "docs/traceability/evidence/r09-m05-l9-pentest-evidence.json"
$remedPath = "docs/traceability/evidence/r09-m05-security-remediation-evidence.json"
$drPath = "docs/traceability/evidence/g8-pe007-full-estate-dr-drill-evidence.json"

$ptData = Read-EvidenceJson $pentestPath
$rmData = Read-EvidenceJson $remedPath
$ptVerdict = $(if ($null -eq $ptData) { 'MISSING' } else { Get-EvidenceVerdict $ptData.summary })
$rmVerdict = $(if ($null -eq $rmData) { 'MISSING' } else { Get-EvidenceVerdict $rmData.summary })
$ptCritical = $ptData.summary.critical_findings
$ptHigh = $ptData.summary.high_findings
$rmAll = $rmData.summary.all_critical_high_remediated
$dr = Get-DrDrill $drPath

# A PASS verdict whose own numbers are missing or not clean is not a PASS.
$ptEffective = $ptVerdict
if ($ptVerdict -eq 'PASS') {
    if ($null -eq $ptCritical -or $null -eq $ptHigh) { $ptEffective = 'INCOMPLETE' } elseif ($ptCritical -gt 0 -or $ptHigh -gt 0) { $ptEffective = 'FAIL' }
}
$rmEffective = $rmVerdict
if ($rmVerdict -eq 'PASS' -and $rmAll -ne $true) { $rmEffective = $(if ($null -eq $rmAll) { 'INCOMPLETE' } else { 'FAIL' }) }
$drEffective = $dr.Verdict
if ($dr.Verdict -eq 'PASS') {
    if ($null -eq $dr.DataLoss) { $drEffective = 'INCOMPLETE' } elseif ($dr.DataLoss -ne 0) { $drEffective = 'FAIL' }
}

Result (Get-OutcomeFromVerdicts @($ptEffective, $rmEffective, $drEffective) 'CONDITION') 'G8-8' 'Zero high/critical security & full-estate DR' `
    ("L9 estate pen-test verdict=$ptVerdict at $(Format-Measured $ptData.timestamp) (critical=$(Format-Measured $ptCritical), high=$(Format-Measured $ptHigh), unmeasured vectors=$(Format-Measured $ptData.summary.unmeasured_tests)); " +
     "DoD-15 remediation verdict=$rmVerdict at $(Format-Measured $rmData.evaluated_at) (all critical/high remediated=$(Format-Measured $rmAll); the record cites pentest run $(Format-Measured $rmData.inputs.pentest_run_at)); $($dr.Text)")

# ---- verdict ---------------------------------------------------------------

Write-Host ""
$verdict = $(if ($fail -gt 0) { 'RED' } elseif ($condition -gt 0) { 'CONDITION' } else { 'GREEN' })
Write-Host "G8: PASS $pass  CONDITION $condition  FAIL $fail  (of $($pass+$condition+$fail) checks)" -ForegroundColor $(if ($fail) { 'Red' } elseif ($condition) { 'Yellow' } else { 'Green' })
Write-Host "G8: $verdict - executed checks honoured; CONDITION items need the warehouse runtime, the acoustic model and production demonstration."

if ($Json) {
    [ordered]@{
        schema = '1000fix-erp/gate-g8/2'
        ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        pass = $pass; conditions = $condition; failures = $fail
        verdict = $verdict
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5 | Set-Content $Json
    Write-Host "gate record written: $Json" -ForegroundColor Green
}

if ($fail -gt 0) { exit 1 }
exit 0
