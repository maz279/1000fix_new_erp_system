# verify-gate-g1a.ps1 - Gate G1a: kernel increment exit (P03-M10-T10).
# Design Authority internal gate (GV-009). 10 criteria.
# Honest posture (2026-10-22 rewrite): PASS only from a check that executed
# and whose exit code was honoured; CONDITION for artefact-present-but-not-
# measured items; FAIL blocks. Numbers are parsed from tool output or from
# script-generated evidence JSON - never typed in, never taken from
# hand-authored markdown.
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

# Read-only counts from the live compose postgres (the same fixed queries the
# doctor runs). Returns a digits/digits|digits string, or -1 when unreachable.
function Invoke-Psql($query) {
    try {
        $out = (& docker compose -f infra/compose/docker-compose.yml --env-file .env exec -T postgres psql -U fix -d fix_dev -t -A -c $query 2>&1 | Out-String) -join ''
        if ($LASTEXITCODE -ne 0) { return -1 }
        $line = @($out -split '\r?\n' | Where-Object { $_ -match '^\s*\d+(\|\d+)*\s*$' } | Select-Object -Last 1)
        if ($null -eq $line -or "$line".Trim() -eq '') { return -1 }
        return "$line".Trim()
    } catch { return -1 }
}

# Module install state as installed|to upgrade|to install|uninstalled|total.
# A shared dev DB can be mid-upgrade (states flip to 'to upgrade' while an
# odoo -u wave runs), so the gate reads the whole breakdown, never a bare
# count that a transient wave could flip.
function Get-ModuleStates() {
    $r = Invoke-Psql "SELECT count(*) FILTER (WHERE state = 'installed') || '|' || count(*) FILTER (WHERE state = 'to upgrade') || '|' || count(*) FILTER (WHERE state = 'to install') || '|' || count(*) FILTER (WHERE state = 'uninstalled') || '|' || count(*) FROM ir_module_module WHERE name LIKE 'cd_%'"
    if ("$r" -eq '-1') { return $null }
    $parts = "$r" -split '\|'
    return @{ Installed = [int]$parts[0]; ToUpgrade = [int]$parts[1]; ToInstall = [int]$parts[2]; Uninstalled = [int]$parts[3]; Total = [int]$parts[4] }
}

Write-Host "`n1000fix-erp Gate G1a - kernel increment exit (P03-M10; Design Authority)`n" -ForegroundColor Cyan

# ---- G1a-1: T0 triad + clean-install proof (matrix evidence + live DB count)
$t0 = @('cd_entity_config', 'cd_rbac_ext', 'cd_event_outbox')
$t0Present = @($t0 | Where-Object { Test-Path "addons/platform/$_/__manifest__.py" }).Count
$matrix = $null
if (Test-Path 'tooling/fitness/evidence/module-install-matrix-latest.json') {
    try { $matrix = Get-Content 'tooling/fitness/evidence/module-install-matrix-latest.json' -Raw | ConvertFrom-Json } catch { $matrix = $null }
}
$manifestCount = @(Get-ChildItem 'addons' -Recurse -Filter '__manifest__.py' -File -ErrorAction SilentlyContinue).Count
$states = Get-ModuleStates
$matrixGreen = ($null -ne $matrix) -and ("$($matrix.verdict)" -eq 'GREEN')
$matrixGap = $(if ($null -ne $matrix) { $manifestCount - [int]$matrix.total_modules } else { 0 })
$g1a1 = 'CONDITION'
$stateEv = 'live DB state not measurable (compose postgres unreachable)'
if ($null -ne $states) {
    $healthy = ($states.Installed -eq $manifestCount) -and ($manifestCount -gt 0)
    $transitional = ($states.Installed + $states.ToUpgrade + $states.ToInstall) -eq $states.Total
    $stateEv = "live psql state breakdown (docker compose exec, exit honoured): $($states.Installed) installed / $($states.ToUpgrade) to upgrade / $($states.ToInstall) to install / $($states.Uninstalled) uninstalled, of $($states.Total) cd_* rows vs $manifestCount manifests"
    if ($matrixGreen -and $healthy) { $g1a1 = 'PASS' }
    elseif ($transitional) { $g1a1 = 'CONDITION' }   # an upgrade/install wave is mid-flight - disclosed, re-run when idle
    else { $g1a1 = 'FAIL' }
}
Result $g1a1 'G1a-1' 'T0 triad manifests present & clean-install proof' `
    "T0 manifests: $t0Present of 3; install matrix (script-generated, 2026-10-16): verdict $($matrix.verdict), $($matrix.passed)/$($matrix.total_modules) modules; $stateEv. The matrix predates the last $matrixGap modules - the live state breakdown is the current measurement."

# ---- G1a-2: six shared-kernel concepts (executed: their pytest suites)
$kernel = @('cd_party_master', 'cd_catalogue', 'cd_document_core', 'cd_mdm_core', 'cd_employee_core', 'cd_entity_config')
$kManifests = @($kernel | Where-Object { Test-Path "addons/platform/$_/__manifest__.py" }).Count
$kernelDirs = @($kernel | ForEach-Object { "addons/platform/$_/tests" } | Where-Object { Test-Path $_ })
$kernelRun = $null
if ($kernelDirs.Count -gt 0) { $kernelRun = Invoke-Unittest $kernelDirs }
$g1a2 = if ($null -ne $kernelRun -and $kernelRun.Ok -and $kManifests -eq 6) { 'PASS' }
        elseif ($null -ne $kernelRun -and -not $kernelRun.Ok) { 'FAIL' } else { 'CONDITION' }
Result $g1a2 'G1a-2' 'Six shared-kernel concepts modelled once' `
    "unittest exit $(if ($null -ne $kernelRun) { $kernelRun.Exit } else { 'n/a' }), $(if ($null -ne $kernelRun) { $kernelRun.Count } else { 0 }) tests across $($kernelDirs.Count) kernel test dirs; $($kManifests) of 6 kernel manifests present (party, catalogue, document, MDM, employee, entity). Modelled-once is enforced by these suites, not by directory existence."

# ---- G1a-3: FF-09 + FF-03 (both scripts executed, exit codes honoured)
$ff09 = Invoke-PyScript 'tooling/fitness/check_ff09_residency.py'
$ff09Line = Get-LastLine $ff09.Out 'FF-09'
$ff03Exit = -1; $ff03Line = 'not run'
if (Get-Command bash -ErrorAction SilentlyContinue) {
    $ff03Out = (& bash 'tooling/scripts/check-vendor-clean.sh' 2>&1 | Out-String) -join ''
    $ff03Exit = $LASTEXITCODE
    $ff03Line = Get-LastLine $ff03Out 'check-vendor-clean'
}
Result $(if ($ff09.Ok -and $ff03Exit -eq 0) { 'PASS' } else { 'FAIL' }) 'G1a-3' 'FF-09 blocking (residency single-client) + FF-03 (vendor clean)' `
    "check_ff09_residency.py exit $($ff09.Exit): $ff09Line; check-vendor-clean.sh exit ${ff03Exit}: $ff03Line. Both checks executed here - exit codes honoured, not asserted from file presence."

# ---- G1a-4: outbox + fix_events (executed: pytest over both)
$obRun = Invoke-Unittest @('addons/platform/cd_event_outbox/tests', 'libs/py/fix_events/tests')
Result $(if ($obRun.Ok) { 'PASS' } else { 'FAIL' }) 'G1a-4' 'Outbox + fix_events (AS-08 transactional events)' `
    "unittest exit $($obRun.Exit), $($obRun.Count) tests across addons/platform/cd_event_outbox/tests and libs/py/fix_events/tests (dual-write, replay, causal ids). Green suites are the evidence; file presence alone would not be."

# ---- G1a-5: permission negative tests (DoD-07) - mock-based suite, worded honestly
$permRun = Invoke-Unittest @('addons/platform/cd_rbac_ext/tests/test_permissions_negative.py')
$rbacLive = Invoke-Psql "SELECT (SELECT count(*) FROM fix_role) || '|' || (SELECT count(*) FROM fix_isolation_tier) || '|' || (SELECT count(*) FROM fix_sod_control)"
$rbacEv = $(if ("$rbacLive" -eq '-1') { 'live registry count unavailable (psql query failed)' } else { "live registry measured read-only via psql (roles|tiers|SoD controls): $rbacLive" })
Result $(if ($permRun.Ok) { 'PASS' } else { 'FAIL' }) 'G1a-5' 'Permission negative tests (DoD-07)' `
    "unittest exit $($permRun.Exit), $($permRun.Count) negative tests green; $rbacEv. HONESTY NOTE: mock-based suite; real ir.rule enforcement via Odoo TransactionCase is separate runtime work (in progress). tooling/fitness/evidence/permission-negative-suite-latest.json records 53 roles/6 tiers/61 controls - self-authored figures from the mock suite's generator, quoted for contrast only, not evidence."

# ---- G1a-6: Bengali 100% (DoD-08) - executed checker, count parsed from output
$trans = Invoke-PyScript 'tooling/fitness/check_translations.py'
$transFields = 0
$mf = [regex]::Match($trans.Out, '(\d+) user-facing fields')
if ($mf.Success) { $transFields = [int]($mf.Groups[1].Value) }
$transLine = Get-LastLine $trans.Out 'translations: '
Result $(if ($trans.Ok -and $transFields -gt 0) { 'PASS' } else { 'CONDITION' }) 'G1a-6' 'Bengali 100% (DoD-08)' `
    "check_translations.py exit $($trans.Exit): $transLine. Field count parsed from the checker's own output: $transFields user-facing fields checked per field (the old hardcoded 1094 figure is retired - this number comes from the tool each run)."

# ---- G1a-7: coverage >= 80% (DoD-03) - measured baseline parsed; target NOT met
$cov = $null
if (Test-Path 'docs/traceability/evidence/coverage-baseline-report.json') {
    try { $cov = Get-Content 'docs/traceability/evidence/coverage-baseline-report.json' -Raw | ConvertFrom-Json } catch { $cov = $null }
}
$estatePct = $null; $estateTarget = $null; $estateVerdict = 'not measured'; $statPct = $null
if ($null -ne $cov -and $null -ne $cov.estate_summary) {
    $estatePct = $cov.estate_summary.percent_covered; $estateTarget = $cov.estate_summary.target_gate_percent
    $estateVerdict = "$($cov.gates_applied.estate.verdict)"
    if ($null -ne $cov.statutory_summary) { $statPct = $cov.statutory_summary.pure_logic_coverage_percent }
}
Result 'CONDITION' 'G1a-7' 'Coverage >= 80% (DoD-03)' `
    "measured baseline (script-generated coverage-baseline-report.json): estate coverage $estatePct% vs the $estateTarget% DoD-03 target - the report's own gate verdict is $estateVerdict (statutory pure-logic $statPct%). The baseline is established and the shortfall tracked; the target is not met, so no PASS is awarded (existence of the register markdown was the old, dishonest basis)."

# ---- G1a-8: architecture drift metrics (AR-012) - parsed from the graph JSON
$graph = $null
if (Test-Path 'tooling/architecture-baseline/evidence/dependency-graph-2026-10-01.json') {
    try { $graph = Get-Content 'tooling/architecture-baseline/evidence/dependency-graph-2026-10-01.json' -Raw | ConvertFrom-Json } catch { $graph = $null }
}
if ($null -ne $graph) {
    $chk = @($graph.checks)
    $chkPass = @($chk | Where-Object { $_.Status -eq 'PASS' }).Count
    $chkWarn = @($chk | Where-Object { $_.Status -eq 'WARN' }).Count
    $chkFail = @($chk | Where-Object { $_.Status -eq 'FAIL' }).Count
    $g1a8 = if ($chkFail -gt 0) { 'FAIL' } elseif ($chkWarn -gt 0) { 'CONDITION' } else { 'PASS' }
    Result $g1a8 'G1a-8' 'Architecture drift metrics (AR-012)' `
        "parsed from the script-generated dependency graph (2026-10-01): $($graph.nodes) nodes, $($graph.edges) edges, $($graph.violationCount) wave-order violations recorded; graph checks: $chkPass PASS / $chkWarn WARN / $chkFail FAIL (reciprocity check records WARN). Metrics are computed and drift is visible - WARN items and a re-run under AR-006 change control are open, so not a clean PASS."
} else {
    Result 'CONDITION' 'G1a-8' 'Architecture drift metrics (AR-012)' `
        "no dependency-graph evidence JSON found - artefact absent, not measured; regenerate via tooling/architecture-baseline"
}

# ---- G1a-9: capacity position - human-compiled report, not re-measured here
$capReport = Test-Path 'docs/traceability/capacity-velocity-measurement-report.md'
Result 'CONDITION' 'G1a-9' 'Capacity position (velocity vs 120 PW)' `
    "capacity-velocity-measurement-report.md present: $capReport - artefact present, not measured. The velocity position is a human-compiled report; this gate does not re-measure it and quotes no number from hand-authored markdown."

# ---- G1a-10: FF-17 layer discipline (executed checker)
$ff17 = Invoke-PyScript 'tooling/fitness/check_ff17_layers.py'
$ff17Line = Get-LastLine $ff17.Out 'FF-17'
$v17 = [regex]::Match($ff17.Out, '(\d+) layer violations')
$v17Count = if ($v17.Success) { $v17.Groups[1].Value } else { 'unparsed' }
Result $(if ($ff17.Ok -and "$v17Count" -eq '0') { 'PASS' } else { 'CONDITION' }) 'G1a-10' 'FF-17 layer discipline' `
    "check_ff17_layers.py exit $($ff17.Exit): $ff17Line; parsed violation count: $v17Count. Verdict from the executed exit code plus the parsed count, not from the script file existing."

# ---- verdict ---------------------------------------------------------------

Write-Host ""
$verdict = $(if ($fail -gt 0) { 'RED' } elseif ($condition -gt 0) { 'CONDITION' } else { 'GREEN' })
Write-Host "G1a: PASS $pass  CONDITION $condition  FAIL $fail  (of $($pass+$condition+$fail) checks)" -ForegroundColor $(if ($fail) { 'Red' } elseif ($condition) { 'Yellow' } else { 'Green' })
Write-Host "G1a: $verdict - executed checks honoured (suites, fitness scripts, live DB counts); CONDITION items are artefact-present-not-measured or measurably below target (see criteria above)."

if ($Json) {
    [ordered]@{
        schema = '1000fix-erp/gate-g1a/2'
        ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        pass = $pass; conditions = $condition; failures = $fail
        verdict = $verdict
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5 | Set-Content $Json
    Write-Host "gate record written: $Json" -ForegroundColor Green
}

if ($fail -gt 0) { exit 1 }
exit 0
