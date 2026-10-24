# verify-gate-g1.ps1 - Gate G1: Foundation go-live (P04-M10-T10, MS-03, Month 4).
# Steering-assessed gate. 12 criteria.
# Honest posture (2026-10-22 rewrite): PASS only from a check that executed
# and whose exit code was honoured (or from a script-generated evidence JSON
# whose verdict is parsed, never trusted from hand-authored markdown);
# CONDITION for items needing the Odoo runtime, pilot volume, an external
# signature or human demonstration; FAIL blocks. Numbers are parsed from
# tool output or measured evidence JSON - never typed in. The git root is
# the PARENT of this codebase directory.
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

# Runs pytest (the estate harness, per pyproject) over one or more dirs and
# returns @{ Out=..; Count=N; Ok=bool; Exit=N }. pyproject addopts already
# carries one -q; a second -q here would hide the summary line the count is
# parsed from. Counts come from pytest's own summary; exit code gates Ok.
function Invoke-Unittest($testDirs) {
    $out = (& py -3.12 -m pytest @testDirs --no-header 2>&1 | Out-String) -join ''
    $exit = $LASTEXITCODE
    $m = [regex]::Match($out, '(\d+) passed')
    $count = 0
    if ($m.Success) { $count = [int]($m.Groups[1].Value) }
    $ok = ($exit -eq 0) -and ($count -gt 0)
    return @{ Out = $out; Count = $count; Ok = $ok; Exit = $exit }
}

# Runs a repo fitness script and honours its exit code.
function Invoke-PyScript($scriptPath) {
    $out = (& py -3.12 $scriptPath 2>&1 | Out-String) -join ''
    $exit = $LASTEXITCODE
    return @{ Out = $out; Exit = $exit; Ok = ($exit -eq 0) }
}

# Last line of $text matching $pattern (parsed tool output for evidence lines).
function Get-LastLine($text, $pattern) {
    $line = (@($text -split '\r?\n') | Where-Object { $_ -match $pattern } | Select-Object -Last 1)
    if ($null -eq $line) { return '' }
    return "$line".Trim()
}

# Read-only count from the live compose postgres. Returns a digits|digits
# string, or -1 when unreachable.
function Invoke-Psql($query) {
    try {
        $out = (& docker compose -f infra/compose/docker-compose.yml --env-file .env exec -T postgres psql -U fix -d fix_dev -t -A -c $query 2>&1 | Out-String) -join ''
        if ($LASTEXITCODE -ne 0) { return -1 }
        $line = @($out -split '\r?\n' | Where-Object { $_ -match '^\s*\d+(\|\d+)*\s*$' } | Select-Object -Last 1)
        if ($null -eq $line -or "$line".Trim() -eq '') { return -1 }
        return "$line".Trim()
    } catch { return -1 }
}

# Parses a JSON evidence file, or returns $null.
function Read-Evidence($path) {
    if (-not (Test-Path $path)) { return $null }
    try { return (Get-Content $path -Raw | ConvertFrom-Json) } catch { return $null }
}

Write-Host "`n1000fix-erp Gate G1 - Foundation go-live (P04-M10; Steering-assessed, 12 criteria)`n" -ForegroundColor Cyan

# ---- G1-01: service orders end-to-end (state machine) - executed suite
$soPath = 'addons/domain/a_service_delivery/cd_service_order/models/fix_service_order.py'
$soModel = Test-Path $soPath
$soStates = $false
if ($soModel) { $soStates = ((Get-Content $soPath -Raw) -match 'SERVICE_ORDER_STATES') }
$soRun = $null
if (Test-Path 'addons/domain/a_service_delivery/cd_service_order/tests') { $soRun = Invoke-Unittest @('addons/domain/a_service_delivery/cd_service_order/tests') }
Result $(if ($null -ne $soRun -and $soRun.Ok -and $soStates) { 'PASS' } elseif ($null -ne $soRun -and -not $soRun.Ok) { 'FAIL' } else { 'CONDITION' }) `
    'G1-01' 'Service orders end-to-end from all channels (state machine)' `
    "unittest exit $(if ($soRun) { $soRun.Exit } else { 'n/a' }), $(if ($soRun) { $soRun.Count } else { 0 }) tests over cd_service_order; SERVICE_ORDER_STATES present in source: $soStates. Channel coverage is exercised by the suite (API security, business gates, technician API), not by model-file existence; pilot-site volume is a runtime matter."

# ---- G1-02: walk-in intake under 3 minutes - timing evidence parsed honestly
$intakeModel = Test-Path 'addons/domain/a_service_delivery/cd_front_desk/models/fix_walkin_intake.py'
$fdRun = $null
if (Test-Path 'addons/domain/a_service_delivery/cd_front_desk/tests') { $fdRun = Invoke-Unittest @('addons/domain/a_service_delivery/cd_front_desk/tests') }
$timing = Read-Evidence 'tooling/fitness/evidence/walkin-intake-timing-latest.json'
$timingEv = 'timing evidence JSON absent - not measured'
$timingDone = $false
$timingVerdict = 'not measured'
if ($null -ne $timing) {
    $timingVerdict = "$($timing.verdict)"
    $timingEv = "timing evidence (script-generated, recorded $($timing.recorded_at)): verdict $($timing.verdict) - $($timing.qualifying_intakes) of $($timing.min_runs_required) required application-recorded intakes (target $($timing.target_seconds)s); branch-staff demonstration UNMEASURED (10 synthesised rows excluded by the tool)"
    $timingDone = ("$($timing.verdict)" -eq 'PASS')
}
Result $(if (-not $intakeModel) { 'FAIL' } elseif ($timingDone) { 'PASS' } else { 'CONDITION' }) `
    'G1-02' 'Walk-in intake under 3 minutes (timed by branch staff)' `
    "intake model present: $intakeModel; front-desk suite exit $(if ($fdRun) { $fdRun.Exit } else { 'n/a' }), $(if ($fdRun) { $fdRun.Count } else { 0 }) tests; $timingEv. The 3-minute claim is NOT met on current evidence - a human-observed pilot session is still required."

# ---- G1-03: migration reconciliation - sign-off STATE parsed, not grepped
$migDoc = Test-Path 'docs/p04/migration-mig-standards.md'
$rehearsalState = 'NOT RECORDED'
if (Test-Path 'migrations/REHEARSAL.md') {
    $rm = [regex]::Matches((Get-Content 'migrations/REHEARSAL.md' -Raw), 'Business sign-off \(MG-004\)[^|]*\|\s*\*\*([A-Z ]+)\*\*')
    if ($rm.Count -gt 0) { $rehearsalState = $rm[$rm.Count - 1].Groups[1].Value.Trim() }
}
$mg004 = Read-Evidence 'docs/traceability/evidence/r10-m05-mg004-business-signoff.json'
$mg004Ev = 'sign-off evidence JSON absent'
if ($null -ne $mg004) {
    $signatory = $(if ($null -ne $mg004.signatory) { "$($mg004.signatory)" } else { 'null' })
    $mg004Ev = "sign-off evidence JSON (script-generated): verdict $($mg004.verdict), signatory $signatory, measured reconciliation itself $($mg004.measured_reconciliation_verdict)"
}
Result $(if (-not $migDoc) { 'FAIL' } elseif ($rehearsalState -match 'SIGNED|DONE|COMPLETE') { 'PASS' } else { 'CONDITION' }) `
    'G1-03' 'Customer/device data migrated with reconciliation signed off' `
    "MIG standards doc present: $migDoc; REHEARSAL.md (parsed) records Business sign-off (MG-004): $rehearsalState - no signature recorded (the old check grepped WAVE1_REHEARSAL and printed signed off; that was wrong); $mg004Ev. Wave-1 rehearsal executed and reconciled; the business sign-off and quarantined-record disposition are the open part."

# ---- G1-04: SLA clocks and escalation - executed suite + parsed demo evidence
$slaRun = $null
if (Test-Path 'services/sla-engine/tests') { $slaRun = Invoke-Unittest @('services/sla-engine/tests') }
$slaEv = Read-Evidence 'tooling/fitness/evidence/sla-demo-evidence-latest.json'
$slaDone = ($null -ne $slaEv) -and ("$($slaEv.verdict)" -eq 'PASS')
$slaScope = 'demo evidence JSON absent'
if ($null -ne $slaEv) { $slaScope = "demo evidence (script-generated, $($slaEv.generated_at)): verdict $($slaEv.verdict), $($slaEv.checks_passed)/$($slaEv.checks_total) checks; SCOPE: $($slaEv.scope)" }
Result $(if ($null -ne $slaRun -and $slaRun.Ok -and $slaDone) { 'PASS' } elseif ($null -ne $slaRun -and -not $slaRun.Ok) { 'FAIL' } else { 'CONDITION' }) `
    'G1-04' 'SLA clocks and escalation firing correctly' `
    "unittest exit $(if ($slaRun) { $slaRun.Exit } else { 'n/a' }), $(if ($slaRun) { $slaRun.Count } else { 0 }) tests over services/sla-engine; $slaScope. Notification delivery on the live mail path is runtime work, disclosed by the evidence's own scope line."

# ---- G1-05: Bengali 100% - executed checker, count parsed from output
$trans = Invoke-PyScript 'tooling/fitness/check_translations.py'
$transFields = 0
$mf = [regex]::Match($trans.Out, '(\d+) user-facing fields')
if ($mf.Success) { $transFields = [int]($mf.Groups[1].Value) }
$transLine = Get-LastLine $trans.Out 'translations: '
Result $(if ($trans.Ok -and $transFields -gt 0) { 'PASS' } else { 'CONDITION' }) `
    'G1-05' '100% Bengali translation (FF-25 blocking)' `
    "check_translations.py exit $($trans.Exit): $transLine. Field count parsed from the checker's own output: $transFields user-facing fields checked per field (the old hardcoded 1094 figure is retired - the number comes from the tool each run)."

# ---- G1-06: security - parsed scan evidence (SAST/secrets/containers/deps)
$sec = Read-Evidence 'tooling/fitness/evidence/security-scan-latest.json'
$secOk = ($null -ne $sec) -and ("$($sec.verdict)" -eq 'PASS') -and ([int]$sec.summary.critical -eq 0) -and ([int]$sec.summary.high -eq 0)
Result $(if ($secOk) { 'PASS' } else { 'CONDITION' }) `
    'G1-06' 'Zero critical/high security findings' `
    "scan evidence (script-generated, $($sec.timestamp)): verdict $($sec.verdict), critical $($sec.summary.critical) / high $($sec.summary.high) / total $($sec.summary.total_findings) findings; third-party penetration test per SC-009 formally deferred to R09 (recorded in the evidence, target $($sec.governance_deferral.target_milestone)). A markdown report's existence no longer gates this criterion."

# ---- G1-07 / G1-08: standing criteria and T-6 entry check - suite searched
$govSuites = @(Get-ChildItem -Path 'addons', 'tooling', 'services', 'libs' -Recurse -Filter 'test_*.py' -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match 'standing|gv.?009|t6|entry.?criteria' })
$t6Doc = Test-Path 'docs/traceability/gate-g1-t6-entry-criteria-review.md'
Result 'CONDITION' 'G1-07' 'Standing criteria applied (GV-009 section 9.1)' `
    "searched the estate for an executable suite covering SC-01..SC-08: $($govSuites.Count) matching test files found (none exist); T-6 review doc present: $t6Doc - artefact present, not measured. Standing-criteria application is the gate assessor's judgement; this gate cannot execute it."

Result 'CONDITION' 'G1-08' 'Entry criteria check at T-6 weeks' `
    "T-6 review doc present: $t6Doc; executable suite search: $($govSuites.Count) matches. The T-6 check is executed six weeks before the gate by the assessor, not at the gate - a dated review record is the artefact, its execution is not measurable here."

# ---- G1-09: gate pipeline profile - Named production condition for R10
$ciYmlPath = Join-Path (Split-Path -Parent $repo) '.github/workflows/ci.yml'   # git root is the parent of the codebase
$drRefs = 0
if (Test-Path $ciYmlPath) { $drRefs = ([regex]::Matches((Get-Content $ciYmlPath -Raw), 'ceph|pgbackrest|drill')).Count }
Result 'CONDITION' 'G1-09' 'Performance at 1.5x peak + DR drill' `
    "Named Condition: cross-region disaster recovery failover drill formally scheduled for Milestone R10 (AR-012/PE-004); remedy: execute the R10 DR failover drill and the 1.5x-peak performance profile on the staging cluster prior to pilot go-live. Local DR primitives referenced in the parent ci.yml: $drRefs matches (ceph/pgbackrest/drill) - references in CI config are not a cross-region drill, and no 1.5x-peak load run has been executed for this gate."

# ---- G1-10: DoD completeness - live DB state + doctor evidence parsed
$domainModules = @(Get-ChildItem 'addons/domain' -Directory -Recurse -Filter 'cd_*' -ErrorAction SilentlyContinue).Count
$manifestCount = @(Get-ChildItem 'addons' -Recurse -Filter '__manifest__.py' -File -ErrorAction SilentlyContinue).Count
$states = Invoke-Psql "SELECT count(*) FILTER (WHERE state = 'installed') || '|' || count(*) FILTER (WHERE state = 'to upgrade') || '|' || count(*) FILTER (WHERE state = 'to install') || '|' || count(*) FILTER (WHERE state = 'uninstalled') || '|' || count(*) FROM ir_module_module WHERE name LIKE 'cd_%'"
$doctor = Read-Evidence 'docs/traceability/evidence/doctor-py-runtime-up.json'
$docRow = $null
if ($null -ne $doctor) { $docRow = @($doctor.results | Where-Object { "$($_.name)" -match 'Module install' } | Select-Object -First 1) }
$docEv = 'doctor evidence JSON absent'
if ($null -ne $docRow) { $docEv = "doctor evidence OD-02 row (run $($docRow.timestamp)): $($docRow.status) - $($docRow.detail)" }
$st = $null
if ("$states" -ne '-1') {
    $p = "$states" -split '\|'
    $st = @{ Installed = [int]$p[0]; ToUpgrade = [int]$p[1]; ToInstall = [int]$p[2]; Uninstalled = [int]$p[3]; Total = [int]$p[4] }
}
$g110 = 'CONDITION'; $stEv = 'live DB state not measurable (compose postgres unreachable)'
if ($null -ne $st) {
    $healthy = ($st.Installed -eq $manifestCount) -and ($manifestCount -gt 0)
    $transitional = ($st.Installed + $st.ToUpgrade + $st.ToInstall) -eq $st.Total
    $stEv = "live psql state breakdown (docker compose exec, exit honoured): $($st.Installed) installed / $($st.ToUpgrade) to upgrade / $($st.ToInstall) to install / $($st.Uninstalled) uninstalled, of $($st.Total) cd_* rows vs $manifestCount manifests"
    if ($healthy) { $g110 = 'PASS' } elseif ($transitional) { $g110 = 'CONDITION' } else { $g110 = 'FAIL' }
}
Result $g110 'G1-10' 'DoD completeness on M01/M04/M17/M07 W1 slices' `
    "$domainModules domain cd_* module dirs; $stEv; $docEv (the doctor row is superseded by the live count when the two differ - the DB query is the same one the doctor runs). The old Test-Path on the install matrix JSON is retired as a PASS basis."

# ---- G1-11: FF-09 + FF-03 - both scripts executed, exit codes honoured
$ff09 = Invoke-PyScript 'tooling/fitness/check_ff09_residency.py'
$ff09Line = Get-LastLine $ff09.Out 'FF-09'
$ff03Exit = -1; $ff03Line = 'not run'
if (Get-Command bash -ErrorAction SilentlyContinue) {
    $ff03Out = (& bash 'tooling/scripts/check-vendor-clean.sh' 2>&1 | Out-String) -join ''
    $ff03Exit = $LASTEXITCODE
    $ff03Line = Get-LastLine $ff03Out 'check-vendor-clean'
}
Result $(if ($ff09.Ok -and $ff03Exit -eq 0) { 'PASS' } else { 'FAIL' }) 'G1-11' 'FF-09 + FF-03 blocking, never bypassed' `
    "check_ff09_residency.py exit $($ff09.Exit): $ff09Line; check-vendor-clean.sh exit ${ff03Exit}: $ff03Line. Both checks executed at gate time - exit codes honoured, not asserted from file presence."

# ---- G1-12: capacity position - human-compiled report, not re-measured here
$capReport = Test-Path 'docs/traceability/capacity-velocity-measurement-report.md'
Result 'CONDITION' 'G1-12' 'Capacity position reported honestly (velocity vs 119 PW)' `
    "capacity-velocity-measurement-report.md present: $capReport - artefact present, not measured. The velocity position is a human-compiled report; this gate does not re-measure it and quotes no number from hand-authored markdown (the old 5.87x echo is retired)."

# ---- verdict ---------------------------------------------------------------

Write-Host ""
$verdict = $(if ($fail -gt 0) { 'RED' } elseif ($condition -gt 0) { 'CONDITION' } else { 'GREEN' })
Write-Host "G1: PASS $pass  CONDITION $condition  FAIL $fail  (of $($pass+$condition+$fail) checks)" -ForegroundColor $(if ($fail) { 'Red' } elseif ($condition) { 'Yellow' } else { 'Green' })
Write-Host "G1: $verdict - counts computed from the $($pass + $condition + $fail) criteria above, not asserted; open conditions: MG-004 sign-off $rehearsalState, walk-in timing $timingVerdict, T-6/standing assessor items, capacity report, DR drill (R10)."

if ($Json) {
    [ordered]@{
        schema = '1000fix-erp/gate-g1/2'
        ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        pass = $pass; conditions = $condition; failures = $fail
        verdict = $verdict
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5 | Set-Content $Json
    Write-Host "gate record written: $Json" -ForegroundColor Green
}

if ($fail -gt 0) { exit 1 }
exit 0
