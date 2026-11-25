# verify-gate-g5.ps1 - Gate G5: Workforce, quality and MSP go-live
# (P08-M10-T10). MS-07, Month 22. 10 criteria mapped to P08-M10-T02..T09.
# Honest posture (2026-10-22 rewrite, G3 pattern): PASS only from a check
# that executed and whose exit code was honoured; CONDITION for items whose
# evidence is an artefact (existence/grep) or another tool's INCOMPLETE
# measurement; FAIL blocks. Numbers are parsed from tool output or measured
# evidence JSON, never typed in. G5-5/6/7 previously grepped method names
# and were awarded PASS; they now execute the journey and module pytest
# suites instead. G5-8 previously awarded PASS for file existence; a
# repo-authored decision record is now CONDITION.
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

# Runs the estate's actual harness (pytest, per pyproject) over one or more
# targets and returns @{ Out=..; Count=N; Ok=bool; Exit=N }. pyproject
# addopts already carries one -q; a second -q here would suppress the summary
# line the count is parsed from. Counts come from pytest's own summary; the
# exit code gates Ok.
function Invoke-Unittest([string[]]$testTargets) {
    $out = (& py -3.12 -m pytest @testTargets --no-header 2>&1 | Out-String) -join ''
    $exit = $LASTEXITCODE
    $m = [regex]::Match($out, '(\d+) passed')
    $count = 0
    if ($m.Success) { $count = [int]($m.Groups[1].Value) }
    $ok = ($exit -eq 0) -and ($count -gt 0)
    return @{ Out = $out; Count = $count; Ok = $ok; Exit = $exit }
}

# T-6 entry criteria: execute the estate's own fitness runner; its exit code
# gates the verdict and the blocking-failure count is parsed from its summary
# line. The runner also writes its own evidence JSON under
# tooling/fitness/evidence/ (script-generated; not read back here).
function Invoke-Fitness {
    $out = (& py -3.12 tooling/fitness/run.py 2>&1 | Out-String) -join ''
    $exit = $LASTEXITCODE
    $m = [regex]::Match($out, 'fitness: (\d+) failure')
    $failures = -1
    if ($m.Success) { $failures = [int]($m.Groups[1].Value) }
    $ok = ($exit -eq 0) -and ($failures -eq 0)
    return @{ Ok = $ok; Exit = $exit; Failures = $failures }
}

# ---- evidence readers (GV-009) ---------------------------------------------
# A criterion that cites evidence reads its verdict and its numbers from the
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
    # (INCOMPLETE / UNMEASURED / UNKNOWN - the run could not observe it).
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
    # Manifests counted here + FF-23 (every cd_* module has a manifest and
    # tests). Excluded directories match as whole path segments.
    $manifests = (Get-ChildItem addons -Recurse -Filter __manifest__.py -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '[\\/](__pycache__|vendor|\.mimosa)[\\/]' } | Measure-Object).Count
    $out = (& py -3.12 tooling/fitness/check_tests_present.py 2>&1 | Out-String).Trim()
    $ok = ($LASTEXITCODE -eq 0) -and ($manifests -gt 0)
    $first = @($out -split "`r?`n")[0]
    return [PSCustomObject]@{ Ok = $ok; Text = "$manifests manifests; FF-23: $first" }
}

Write-Host "`n1000fix-erp Gate G5 - Workforce, quality and MSP go-live (P08-M10; MS-07; Month 22)`n" -ForegroundColor Cyan

# ---- G5-1 (T01): T-6 entry criteria check --------------------------------
$fit = Invoke-Fitness
Result $(if ($fit.Ok) { 'PASS' } else { 'FAIL' }) 'G5-1' 'T-6 entry: fitness clean' `
    "fitness runner executed in this gate run: exit $($fit.Exit), $($fit.Failures) blocking failure(s) parsed from its summary line"

# ---- G5-2 (T02): payroll end to end with BEFTN + Bengali payslips --------
$payroll = Invoke-Unittest @('services/payroll-engine/tests')
$payslipBn = Test-Path addons/domain/h_people/cd_payroll_bd/views/fix_payroll_views.xml
$beftnBatch = Select-String -Path addons/domain/h_people/cd_payroll_bd/models/fix_payroll.py -Pattern 'beftn_settlement_date' -Quiet
Result $(if ($payroll.Ok -and $payslipBn -and $beftnBatch) { 'PASS' } else { 'FAIL' }) 'G5-2' 'Payroll end-to-end (Journey 13)' `
    "payroll-engine tests exit $($payroll.Exit), $($payroll.Count) passed; payslip views present=$payslipBn; BEFTN settlement date in fix_payroll.py=$beftnBatch; a production BEFTN submission to the bank is a runtime act this gate does not claim"

# ---- G5-3 (T03): every stub closed, none outlived its expiry -------------
$stubSites = Get-ChildItem -Path addons -Recurse -Filter *.py -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch 'vendor|__pycache__|tests' } |
    Select-String -Pattern '\bSTUB-(M02|M31|M34|M42)-[A-Z0-9-]+\b' |
    Where-Object { $_.Line -notmatch 'CLOSED|closed|closing|#.*stub|"""|\*|assert' }
$stubCount = ($stubSites | Measure-Object).Count
$qms = Invoke-Unittest @('addons/domain/i_governance/cd_qms_process/tests')
Result $(if ($qms.Ok -and $stubCount -le 3) { 'PASS' } else { 'FAIL' }) 'G5-3' 'Stub closure (GV-005)' `
    "cd_qms_process tests exit $($qms.Exit), $($qms.Count) passed; $stubCount residual STUB-M02/M31/M34/M42 markers outside comments (criterion: <= 3; counted by scanning addons/ sources)"

# ---- G5-4 (T04): certification eligibility blocks at dispatch ------------
$eligibilityCode = Select-String -Path addons/domain/h_people/cd_competency/models/fix_competency.py -Pattern 'dispatch_eligibility' -Quiet
$blockingPath = Select-String -Path addons/domain/h_people/cd_competency/models/fix_competency.py -Pattern 'assignment blocked' -Quiet
$elig = Invoke-Unittest @('addons/domain/h_people/cd_competency/tests')
Result $(if ($elig.Ok -and $eligibilityCode -and $blockingPath) { 'PASS' } else { 'FAIL' }) 'G5-4' 'Certification enforced at dispatch (FR-LMS-039)' `
    "cd_competency tests exit $($elig.Exit), $($elig.Count) passed; dispatch_eligibility() present=$eligibilityCode; 'assignment blocked' error present=$blockingPath"

# ---- G5-5 (T05): journeys 6, 13 and 14 automated -------------------------
# Previously three method-name greps awarded PASS; the criterion is now
# measured by executing the journey lifecycle suites in tests/.
$journeys = Invoke-Unittest @('tests/test_journey_06_msp.py', 'tests/test_journey_13_payroll.py', 'tests/test_journey_14_qms.py')
Result $(if ($journeys.Ok) { 'PASS' } else { 'FAIL' }) 'G5-5' 'Journeys 6, 13, 14 automated' `
    "journey suites executed (grep-only previously): exit $($journeys.Exit), $($journeys.Count) passed - J6 alert>ticket>remote session>SLA report, J13 lock>calc>approve>BEFTN>payslip>post, J14 complaint>NCR>CAPA>verify>close; nightly orchestration EXECUTION is CI-side and not measured here"

# ---- G5-6 (T06): ISO 9001:2015 audit readiness --------------------------
# Previously a grep for 'systems_traced'; the same executed cd_qms_process
# suite (G5-3) carries the CON-11, CAPA-gate and P11 tests.
Result $(if ($qms.Ok) { 'PASS' } else { 'FAIL' }) 'G5-6' 'ISO 9001:2015 audit readiness (CON-11)' `
    "cd_qms_process suite executed (grep-only previously): exit $($qms.Exit), $($qms.Count) passed - covers the CON-11 systems-traced question, critical NCR closing only through verified CAPA and P11 offline capture; the external ISO surveillance audit (Phase 11) is an external judgement this gate does not claim"

# ---- G5-7 (T07): MSP SLA reporting against contract terms ---------------
# Previously two greps ('sla_attainment', 'fix.contract'); now measured by
# executing the module suite that tests report generation and attainment.
$msp = Invoke-Unittest @('addons/domain/a_service_delivery/cd_msp_contract/tests')
Result $(if ($msp.Ok) { 'PASS' } else { 'FAIL' }) 'G5-7' 'MSP SLA reporting against contract terms' `
    "cd_msp_contract suite executed (grep-only previously): exit $($msp.Exit), $($msp.Count) passed - monthly report window, quiet-month full SLA attainment and bilingual regeneration are tested on M08's contract engine; production SLA attainment needs live MSP volume"

# ---- G5-8 (T08): D-025 upgrade slot position ---------------------------
# Existence of a repo-authored decision record is artefact evidence: a
# recorded decision, not a measured property. Previously existence PASS.
$d025File = Get-ChildItem docs/decisions/D-025* -ErrorAction SilentlyContinue | Select-Object -First 1
Result 'CONDITION' 'G5-8' 'D-025 upgrade slot position' `
    $(if ($d025File) {
        "repo-authored decision record present (docs/decisions/$($d025File.Name)); artefact present, not measured - the upgrade slot position is a recorded decision, and its execution is measured at G6-5"
    } else {
        "decision record not yet in docs/decisions/ (Steering records it); Phase 9 P09-M02 executes it"
    })

# ---- G5-9 (T09): gate profile - performance + DR + policy --------------
# Verdicts, RPO and RTO are read from the PE-004 / PE-007 evidence; PASS only
# when both evidence verdicts are PASS (missing evidence = CONDITION).
$perfPath = 'docs/traceability/evidence/g5-pe004-performance-evidence.json'
$perfVerdict = Get-EvidenceVerdict (Read-EvidenceJson $perfPath)
$dr = Get-DrDrill 'docs/traceability/evidence/g5-pe007-dr-drill-evidence.json'
Result (Get-OutcomeFromVerdicts @($perfVerdict, $dr.Verdict) 'CONDITION') 'G5-9' 'Gate profile (PE-004 & PE-007)' `
    "PE-004 1.5x-peak performance verdict=$perfVerdict [$perfPath]; $($dr.Text)"

# ---- G5-10: module census ------------------------------------------------
# FF-23 proves every module ships a manifest and tests; installation on
# fix_dev is not probed by this gate, so the criterion cannot PASS on it.
$census = Get-ModuleCensus
Result $(if ($census.Ok) { 'CONDITION' } else { 'FAIL' }) 'G5-10' 'All modules shipped + installed' `
    "$($census.Text); installation on fix_dev: UNMEASURED (not probed by this gate)"

# ---- verdict ---------------------------------------------------------------

$total = $pass + $condition + $fail
$verdict = $(if ($fail -gt 0) { 'RED' } elseif ($condition -gt 0) { 'CONDITION' } else { 'GREEN' })
$reportVerdict = $(if ($fail -gt 0) { 'FAIL' } elseif ($condition -gt 0) { 'CONDITION' } else { 'PASS' })
Write-Host ""
Write-Host "G5: PASS $pass  CONDITION $condition  FAIL $fail  (of $total checks)" -ForegroundColor $(if ($fail) { 'Red' } elseif ($condition) { 'Yellow' } else { 'Green' })
Write-Host "G5: $verdict - executed checks honour exit codes; CONDITION items need runtime execution, production volume, external judgement or human demonstration."

# Publish the G5 report on every run - a FAIL run must not leave an older
# PASS report in place.
$reportCriteria = @($script:Results | ForEach-Object {
    [ordered]@{ id = $_.Id; title = $_.Criterion; status = $_.Status; evidence = $_.Evidence }
})
$report = [ordered]@{
    schema = '1000fix-erp/gate-g5/1'
    gate = 'G5'
    milestone = 'MS-07'
    ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
    summary = [ordered]@{
        pass = $pass
        condition = $condition
        fail = $fail
        total = $total
        verdict = $reportVerdict
    }
    criteria = $reportCriteria
}
$reportPath = 'docs/traceability/evidence/gate-g5-signed-report.json'
$report | ConvertTo-Json -Depth 5 | Set-Content -Path $reportPath -Encoding utf8
Write-Host "G5 report published: $reportPath" -ForegroundColor DarkGray

if ($Json) {
    [ordered]@{
        schema = '1000fix-erp/gate-g5/2'
        ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        pass = $pass; conditions = $condition; failures = $fail
        verdict = $verdict
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5 | Set-Content $Json
    Write-Host "gate record written: $Json" -ForegroundColor Green
}

if ($fail -gt 0) { exit 1 }
exit 0
