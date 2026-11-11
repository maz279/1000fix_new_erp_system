# verify-gate-g6.ps1 - Gate G6: New asset businesses go-live
# (P09-M10-T10). MS-08, Month 26. 10 criteria mapped to P09-M10-T01..T09.
# Honest posture (2026-10-22 rewrite, G3 pattern): PASS only from a check
# that executed and whose exit code was honoured; CONDITION for items whose
# evidence is an artefact (existence/grep) or another tool's INCOMPLETE
# measurement; FAIL blocks. Numbers are parsed from tool output or measured
# evidence JSON, never typed in. Honest evidence-verdict reads are kept for
# the broker drills (G6-3) and the upgrade-slot evidence (G6-5); the
# existence/grep criteria (G6-2, G6-4, G6-6, G6-7) are CONDITION/FAIL on real
# measurements, and G6-9 no longer requires a hand-written signed report.
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

# Executes the event schema registry verifier (tooling/events/
# verify_event_registry.py) and returns its honoured exit code plus the
# counts parsed from the evidence JSON the tool itself wrote (script-
# generated; never typed here). Exit 0 PASS / 1 FAIL / 2 INCOMPLETE.
function Invoke-EventRegistryAudit {
    $out = (& py -3.12 tooling/events/verify_event_registry.py 2>&1 | Out-String) -join ''
    $exit = $LASTEXITCODE
    $reg = Read-EvidenceJson 'docs/traceability/evidence/event-schema-registry-audit.json'
    $registered = $null; $published = $null; $unregistered = $null; $regVerdict = 'UNKNOWN'
    if ($null -ne $reg -and $null -ne $reg.results) {
        $r = $reg.results
        $registered = $r.registered_events
        $published = $r.published_event_types_direct_calls
        $unregistered = $r.published_but_unregistered
        if ($r.verdict -is [string] -and $r.verdict) { $regVerdict = $r.verdict.ToUpperInvariant() }
    }
    return [PSCustomObject]@{ Exit = $exit; Verdict = $regVerdict; Registered = $registered; Published = $published; Unregistered = $unregistered }
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

$evDir = 'docs/traceability/evidence'

Write-Host "`n1000fix-erp Gate G6 - New asset businesses go-live (P09-M10; MS-08; Month 26)`n" -ForegroundColor Cyan

# ---- G6-1 (T01): T-6 entry criteria ----
$fit = Invoke-Fitness
Result $(if ($fit.Ok) { 'PASS' } else { 'FAIL' }) 'G6-1' 'T-6 entry: fitness clean' `
    "fitness runner executed in this gate run: exit $($fit.Exit), $($fit.Failures) blocking failure(s) parsed from its summary line"

# ---- G6-2 (T02): rental, trade-in, data services transacting ----
# Existence of the three models is artefact evidence; the criterion says
# 'transacting', which is runtime transaction volume - not measured here.
# Previously existence was awarded PASS with 'transacting' prose.
$rentalCode = Test-Path addons/domain/d_circular/cd_rental_asset/models/fix_rental_asset.py
$tradeinCode = Test-Path addons/domain/d_circular/cd_tradein/models/fix_tradein.py
$dataCaseCode = Test-Path addons/domain/d_circular/cd_data_case/models/fix_data_case.py
Result $(if ($rentalCode -and $tradeinCode -and $dataCaseCode) { 'CONDITION' } else { 'FAIL' }) 'G6-2' 'Asset businesses transacting' `
    $(if ($rentalCode -and $tradeinCode -and $dataCaseCode) {
        "artefact present, not measured: rental (reservation + damage + deposit), trade-in (10-state lifecycle + wipe gate) and data services (custody chain + Z4 + purge) models exist; no runtime transactions measured - bookings, deposits and purge volume need the production estate (existence was previously awarded PASS with 'transacting' prose)"
    } else {
        "rental=$rentalCode tradein=$tradeinCode data=$dataCaseCode - a business line's model file is missing"
    })

# ---- G6-3 (T03): event-bus migration ----
# Each drill's verdict is read from its evidence; PASS only when all are PASS.
$kafkaCompose = Test-Path infra/compose/docker-compose.asset-ml.yml
$busVerdicts = [ordered]@{
    'cluster-survival'      = Get-EvidenceVerdict (Read-EvidenceJson "$evDir/kafka-cluster-survival-evidence.json")
    'dual-write-parity'     = Get-EvidenceVerdict (Read-EvidenceJson "$evDir/dual-write-parity-evidence.json")
    'cutover'               = Get-EvidenceVerdict (Read-EvidenceJson "$evDir/event-bus-cutover-log.json")
    'dlq-replay'            = Get-EvidenceVerdict (Read-EvidenceJson "$evDir/kafka-dlq-replay-evidence.json")
    'schema-registry-audit' = Get-EvidenceVerdict (Read-EvidenceJson "$evDir/event-schema-registry-audit.json")
}
$d037 = Test-Path docs/decisions/D-037-kafka-event-bus-migration.md
$busText = (@($busVerdicts.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ' ') + " D-037=$d037"
if ($kafkaCompose) {
    $g6_3 = @($busVerdicts.Values)
    if (-not $d037) { $g6_3 += 'MISSING' }
    Result (Get-OutcomeFromVerdicts $g6_3 'CONDITION') 'G6-3' 'Event-bus migration (Kafka)' "evidence verdicts: $busText"
} else {
    Result 'FAIL' 'G6-3' 'Event-bus migration (Kafka)' "Kafka cluster infrastructure missing; evidence verdicts: $busText"
}

# ---- G6-4 (T04): journeys 8, 9, 11 automated ----
# Previously three event-name greps; now the journey suites are executed and
# the event registry audit runs live (its exit code honoured: 0 PASS /
# 1 FAIL / 2 INCOMPLETE), counts parsed from the audit evidence the tool
# wrote.
$reg = Invoke-EventRegistryAudit
$journeys = Invoke-Unittest @('tests/test_journey_08_rental.py', 'tests/test_journey_09_tradein.py', 'addons/domain/d_circular/cd_data_case/tests/test_journey_11_data_services.py')
$g6_4 = 'FAIL'
if ($reg.Exit -eq 0) { $g6_4 = 'PASS' } elseif ($reg.Exit -eq 2) { $g6_4 = 'CONDITION' }
if (-not $journeys.Ok) { $g6_4 = 'FAIL' }
Result $g6_4 'G6-4' 'Journeys 8, 9, 11 automated' `
    "journey suites executed (grep-only previously): exit $($journeys.Exit), $($journeys.Count) passed (rental money path, trade-in lifecycle, data-services custody + purge); event-registry audit executed live: exit $($reg.Exit), verdict=$($reg.Verdict), registered=$(Format-Measured $reg.Registered), published-direct=$(Format-Measured $reg.Published), published-but-unregistered=$(Format-Measured $reg.Unregistered) [docs/traceability/evidence/event-schema-registry-audit.json]; broker-side topic provisioning UNMEASURED (brokers down) - end-to-end automation over the bus is not yet demonstrable"

# ---- G6-5 (T05): Odoo upgrade slot execution & deferral ----
$d025 = Test-Path docs/decisions/D-025-odoo-baseline-upgrade.md
$d038 = Test-Path docs/decisions/D-038-odoo20-upgrade-slot-execution.md
$ocaVerdict = Get-EvidenceVerdict (Read-EvidenceJson "$evDir/fork-audit-and-oca-v20-matrix.json")
$bnVerdict = Get-EvidenceVerdict (Read-EvidenceJson "$evDir/bengali-rendering-verification.json")
if ($d025) {
    $g6_5 = @($ocaVerdict, $bnVerdict)
    if (-not $d038) { $g6_5 += 'MISSING' }
    Result (Get-OutcomeFromVerdicts $g6_5 'CONDITION') 'G6-5' 'D-025 upgrade slot executed' `
        "D-025=$d025 D-038=$d038; fork audit + OCA v20 matrix verdict=$ocaVerdict; Bengali conjunct rendering (TR-07) verdict=$bnVerdict"
} else {
    Result 'FAIL' 'G6-5' 'D-025 upgrade slot executed' "D-025 record not found"
}

# ---- G6-6 (T06): M06 residency conformance ----
# Previously a grep for 'z4'/'SC-007' awarding PASS; the Z4 gate is exercised
# by the executed journey 11 suite, but runtime Z4 routing and per-read audit
# volume are unmeasured - CONDITION, not PASS.
Result $(if ($journeys.Ok) { 'CONDITION' } else { 'FAIL' }) 'G6-6' 'M06 residency conformance' `
    "journey 11 suite executed (grep-only previously): part of $($journeys.Count) passed (exit $($journeys.Exit)) - exercises the Z4 residency gate (SC-007: recovery blocked unless routed to Z4), step-up authentication and the NIST SP 800-88 purge certificate with statutory retention; runtime Z4 routing and per-read access-audit volume are UNMEASURED"

# ---- G6-7 (T07): content approvals ----
# The register under docs/traceability/evidence/content-approval-register.json
# is repo-authored (hand-written): no tool measured any approval, so its
# pending_count is asserted, not measured. Approvals are human acts recorded
# in governance documents.
$appointmentDoc = Test-Path docs/governance/programme-content-lead-appointment.md
$signoffDoc = Test-Path docs/governance/content-approval-g6-signoff.md
$contentReg = Read-EvidenceJson "$evDir/content-approval-register.json"
$declared = $null; $pending = $null
if ($null -ne $contentReg -and $null -ne $contentReg.summary) {
    $declared = $contentReg.summary.total_class_a_b_templates
    $pending = $contentReg.summary.pending_count
}
Result $(if ($appointmentDoc -and $signoffDoc) { 'CONDITION' } else { 'FAIL' }) 'G6-7' 'Content approvals' `
    $(if ($appointmentDoc -and $signoffDoc) {
        "appointment and G6 sign-off documents present; register reads $(Format-Measured $declared) declared Class A/B templates, pending=$(Format-Measured $pending) - the register is repo-authored and no tool measured the approvals (the gate previously trusted its pending_count for PASS); Steering confirmation is a human act"
    } else {
        "appointment doc=$appointmentDoc; G6 signoff doc=$signoffDoc - a governance record is missing"
    })

# ---- G6-8 (T08): ML model governance ----
$ml = Invoke-Unittest @('services/ml-gateway/tests')
$driftCode = Select-String -Path services/ml-gateway/src/ml_gateway.py -Pattern 'detect_drift' -Quiet
$registryCode = Select-String -Path services/ml-gateway/src/ml_gateway.py -Pattern 'MODEL_REGISTRY' -Quiet
Result $(if ($ml.Ok -and $driftCode -and $registryCode) { 'PASS' } else { 'FAIL' }) 'G6-8' 'ML model governance' `
    "ml-gateway tests exit $($ml.Exit), $($ml.Count) passed; model registry present=$registryCode; drift detection present=$driftCode"

# ---- G6-9 (T09): gate profile ----
# PE-004 and PE-007 verdicts, RPO and RTO are read from the evidence; the
# Steering gate sign-off is a human execution that has not happened. The
# hand-written gate-g6-signed-report.json claiming PASS is not evidence and
# is no longer required for any outcome (its existence previously gated
# this criterion).
$perfPath = "$evDir/g6-pe004-performance-evidence.json"
$perfVerdict = Get-EvidenceVerdict (Read-EvidenceJson $perfPath)
$dr = Get-DrDrill "$evDir/g6-pe007-dr-drill-evidence.json"
Result (Get-OutcomeFromVerdicts @($perfVerdict, $dr.Verdict) 'CONDITION') 'G6-9' 'Gate profile (PE-004 & PE-007)' `
    "PE-004 1.5x-peak profile verdict=$perfVerdict [$perfPath]; $($dr.Text); Steering gate sign-off: PENDING - human execution, and the hand-written gate-g6-signed-report.json is not evidence"

# ---- G6-10: module census ----
$census = Get-ModuleCensus
Result $(if ($census.Ok) { 'PASS' } else { 'FAIL' }) 'G6-10' 'All modules shipped' `
    "$($census.Text) (manifest count + FF-23 executed with exit code honoured); installation on fix_dev is not part of this criterion"

# ---- verdict ---------------------------------------------------------------

$total = $pass + $condition + $fail
$verdict = $(if ($fail -gt 0) { 'RED' } elseif ($condition -gt 0) { 'CONDITION' } else { 'GREEN' })
Write-Host ""
Write-Host "G6: PASS $pass  CONDITION $condition  FAIL $fail  (of $total checks)" -ForegroundColor $(if ($fail) { 'Red' } elseif ($condition) { 'Yellow' } else { 'Green' })
Write-Host "G6: $verdict - executed checks honour exit codes; CONDITION items need production infrastructure, runtime volume or human execution; FAIL items block."
if ($Json) {
    [ordered]@{
        schema = '1000fix-erp/gate-g6/2'
        ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        pass = $pass; conditions = $condition; failures = $fail
        verdict = $verdict
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5 | Set-Content $Json
    Write-Host "gate record written: $Json" -ForegroundColor Green
}

if ($fail -gt 0) { exit 1 }
exit 0
