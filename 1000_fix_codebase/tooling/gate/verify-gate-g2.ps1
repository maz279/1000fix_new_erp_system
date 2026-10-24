# =============================================================================
# verify-gate-g2.ps1 - P05-M10-T10: Gate G2 (Field operations go-live, MS-04, Month 8).
# Assessed by Steering Committee, on evidence. 10 criteria.
# GV-009: an assertion is not evidence - each criterion names its artefact.
# Criteria:
#   G2-01  Technician app in daily use by all Dhaka technicians
#   G2-02  24-hour offline operation demonstrated with zero data loss (AR-010, TS-015)
#   G2-03  Route optimisation reducing measured travel time by >= 15%
#   G2-04  Inventory accuracy >= 95% at migrated locations
#   G2-05  Online booking rate >= 60% at pilot sites
#   G2-06  Paper service forms withdrawn in Dhaka
#   G2-07  Entry criteria check at T-6 weeks (GV-009 section 9.2)
#   G2-08  Verify L6 end-to-end suite is fully automated by W3 and journeys 1-3 run nightly
#   G2-09  Gate pipeline profile: performance at 1.5x peak + DR drill evidence (NFR-056)
#   G2-10  Gate G2: Steering signs, report published, residual register issued
#
# Posture (GV-009 - an assertion is not evidence):
#   PASS only on a machine-produced measurement or a genuine countersigned record;
#   CONDITION when only code, specs or repo-authored narrative reports exist
#     (field outcomes need production telemetry: this is a dev repo, not deployed);
#   OPEN when a human/Steering step is outstanding;
#   FAIL on missing prerequisites or internally inconsistent evidence.
# Field-outcome telemetry, when it exists, is read from
#   docs/traceability/evidence/g2-0N-telemetry*.json  {source, measured, threshold}
#   (source must not be local-harness / repo-authored / synthetic).
# Verdict: GREEN - PASS-WITH-CONDITIONS - RED-OPEN (any OPEN) - RED (any FAIL).
# Exit: 0 GREEN or PASS-WITH-CONDITIONS - 1 any FAIL or OPEN - 2 preconditions.
# =============================================================================
[CmdletBinding()]
param([string]$Json = '')
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

# Field-outcome telemetry reader. Returns @{ Status; Note }.
#   PASS requires BOTH a machine origin and a production source: the JSON must
#   name a generator script that exists in the repo (provenance by file origin,
#   not by a self-declared string) AND a source that is not repo-authored.
#   A hand-written JSON claiming source=production can no longer award PASS.
function Read-Telemetry([string]$Id) {
    $f = Get-ChildItem $evDir -Filter "$($Id.ToLower())-telemetry*.json" -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
    if (-not $f) { return @{ Status = 'CONDITION'; Note = "no machine telemetry evidence ($evDir/$($Id.ToLower())-telemetry*.json)" } }
    try {
        $t = Get-Content $f.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        $src = "$($t.source)"
        $gen = "$($t.generator)"
        $genExists = $false
        if ($gen) { $genExists = Test-Path $gen }
        if (-not $genExists) {
            return @{ Status = 'CONDITION'; Note = "$($f.Name): no generator script named/found (generator='$gen') - provenance unproven, cannot award PASS regardless of source string" }
        }
        if (-not $src -or $src -match '(?i)local-harness|repo-authored|synthetic|manual') {
            return @{ Status = 'CONDITION'; Note = "$($f.Name): generator $gen ran, but source '$src' is not production telemetry" }
        }
        if ($null -eq $t.measured -or $null -eq $t.threshold) { return @{ Status = 'CONDITION'; Note = "$($f.Name): no measured/threshold fields" } }
        $ok = [double]$t.measured -ge [double]$t.threshold
        return @{ Status = $(if ($ok) { 'PASS' } else { 'FAIL' }); Note = "$($f.Name): generator $gen, source $src, measured $($t.measured) vs threshold $($t.threshold)" }
    } catch { return @{ Status = 'FAIL'; Note = "$($f.Name) unreadable: $($_.Exception.Message)" } }
}

Write-Host "`n1000fix-erp Gate G2 - Field operations go-live (P05-M10; MS-04; Month 8)`n" -ForegroundColor Cyan

# G2-01: Technician app daily use
$soModel = Test-Path 'addons/domain/a_service_delivery/cd_service_order/models/fix_service_order.py'
$techModel = Test-Path 'addons/domain/a_service_delivery/cd_service_order/models/fix_technician.py'
$techRollout = Test-Path 'docs/traceability/g2-01-technician-app-rollout-report.md'
$t01 = Read-Telemetry 'G2-01'
Gate 'G2-01' 'Technician app in daily use by all Dhaka technicians' `
    $(if (-not ($soModel -or $techModel)) { 'FAIL' } else { $t01.Status }) `
    "app models on disk: $($soModel -or $techModel); rollout report present: $techRollout (repo-authored narrative claiming 42 technicians / 100% DAU for an app this repo has never deployed - not evidence); $($t01.Note)" `
    'Deploy the technician app and export daily-active-usage telemetry as machine evidence'

# G2-02: 24-hour offline operation with zero data loss
$offlineDoc = Test-Path 'docs/guides/offline-sync-protocol.md'
$offlineReport = Test-Path 'docs/traceability/g2-02-offline-zero-loss-report.md'
$offlineSuite = Test-Path 'tooling/tests/test_l12_offline_suite.py'
$t02 = Read-Telemetry 'G2-02'
Gate 'G2-02' '24-hour offline operation with zero data loss (AR-010, TS-015)' `
    $(if (-not ($offlineDoc -or $offlineSuite)) { 'FAIL' } else { $t02.Status }) `
    "protocol doc: $offlineDoc; L12 offline suite: $offlineSuite; report present: $offlineReport (repo-authored narrative); a suite on disk is not a 24-hour field demonstration; $($t02.Note)" `
    'Run and record a 24-hour offline field demonstration (device logs + server reconciliation)'

# G2-03: Route optimisation reducing measured travel time >= 15%
$routeModel = Test-Path 'addons/domain/a_service_delivery/cd_field_service/models/fix_field_route.py'
$routeReport = Test-Path 'docs/traceability/g2-03-route-optimization-report.md'
$routeOptimizer = (Test-Path 'services/dispatch-scoring/dispatch_scoring/route_optimizer.py') -or (Test-Path 'services/dispatch-scoring/src/route_optimizer.py')
$t03 = Read-Telemetry 'G2-03'
Gate 'G2-03' 'Route optimisation reducing travel time >= 15%' `
    $(if (-not ($routeModel -or $soModel)) { 'FAIL' } else { $t03.Status }) `
    "route model: $routeModel; optimizer: $routeOptimizer; report present: $routeReport (a single synthetic 5-stop benchmark claiming 18.86% - not fleet-measured travel time); $($t03.Note)" `
    'Measure fleet GPS travel time before/after optimisation over a representative period'

# G2-04: Inventory accuracy >= 95% - plus an arithmetic consistency check of the sign-off.
$invModel = Test-Path 'addons/domain/e_supply_chain/cd_inventory/models/fix_spare_part.py'
$invSignoffPath = 'docs/traceability/inventory-reconciliation-signoff.md'
$invNote = 'sign-off file absent'; $invConsistent = $true
if (Test-Path $invSignoffPath) {
    $sumC = 0; $sumR = 0; $sumV = 0; $rows = 0; $tot = $null
    foreach ($line in (Get-Content $invSignoffPath -Encoding UTF8)) {
        if ($line -notmatch '^\|') { continue }
        $cells = @($line.Trim().Trim('|').Split('|') | ForEach-Object { $_.Trim() })
        if ($cells.Count -ne 7) { continue }
        $nums = @($cells[3], $cells[4], $cells[5] | ForEach-Object { ($_ -replace '[\*,\s]', '') })
        if (@($nums | Where-Object { $_ -notmatch '^\d+$' }).Count -gt 0) { continue }
        if ($cells[0] -match 'Totals') { $tot = @([int]$nums[0], [int]$nums[1], [int]$nums[2]) }
        else { $sumC += [int]$nums[0]; $sumR += [int]$nums[1]; $sumV += [int]$nums[2]; $rows++ }
    }
    if ($rows -eq 0 -or $null -eq $tot) { $invConsistent = $false; $invNote = 'location breakdown table or totals row not parseable' }
    else {
        $invNote = "location rows ($rows) sum to $sumC counted / $sumR reconciled / variance $sumV; totals row states $($tot[0]) / $($tot[1]) / $($tot[2])"
        if ($sumC -ne $tot[0] -or $sumR -ne $tot[1] -or $sumV -ne $tot[2] -or ($tot[0] - $tot[1]) -ne $tot[2]) {
            $invConsistent = $false; $invNote += " - evidence internally inconsistent (totals row variance vs counted-reconciled = $($tot[0] - $tot[1]))"
        }
    }
    $buf = Select-String -Path $invSignoffPath -Pattern '\*\*([\d.]+)%\*\*\s*\|\s*\+([\d.]+)% buffer' | Select-Object -First 1
    if ($buf) {
        $acc = [double]$buf.Matches[0].Groups[1].Value; $claimed = [double]$buf.Matches[0].Groups[2].Value
        $real = [math]::Round($acc - 95.0, 2)
        if ([math]::Abs($real - $claimed) -gt 0.01) { $invConsistent = $false; $invNote += "; stated buffer +$claimed% but $acc% - 95% = +$real%" }
    }
}
$t04 = Read-Telemetry 'G2-04'
$g204Status = if (-not $invModel) { 'FAIL' } elseif ((Test-Path $invSignoffPath) -and -not $invConsistent) { 'FAIL' } else { $t04.Status }
Gate 'G2-04' 'Inventory accuracy >= 95% at migrated locations' $g204Status `
    "inventory model: $invModel; sign-off (repo-authored, not countersigned): $invNote; $($t04.Note)" `
    'Re-issue the reconciliation from an executed cycle count (machine export) with consistent totals; countersign'

# G2-05: Online booking rate >= 60% at pilot sites
$custPortal = Test-Path 'apps/web/customer/app/booking/page.tsx'
$custAddon = Test-Path 'addons/domain/b_customer_engagement/cd_customer_portal'
$custBookingSpec = Test-Path 'tooling/e2e/journeys/j01-customer-books.spec.ts'
$onlineBookingReport = Test-Path 'docs/traceability/g2-05-online-booking-report.md'
$t05 = Read-Telemetry 'G2-05'
Gate 'G2-05' 'Online booking rate >= 60% at pilot sites' `
    $(if (-not (($custPortal -or $custAddon) -and $custBookingSpec)) { 'FAIL' } else { $t05.Status }) `
    "booking portal: $($custPortal -or $custAddon); journey spec: $custBookingSpec; report present: $onlineBookingReport (repo-authored narrative claiming 68.40%; no pilot-site intake data); $($t05.Note)" `
    'Measure web/app intake proportion over the first 30 days of the branch pilot (machine export)'

# G2-06: Paper service forms withdrawn in Dhaka
$esignModel = Test-Path 'addons/platform/cd_esignature/models/fix_esignature.py'
$paperWithdrawal = Test-Path 'docs/traceability/g2-06-paper-forms-withdrawal-order.md'
$t06 = Read-Telemetry 'G2-06'
Gate 'G2-06' 'Paper service forms withdrawn in Dhaka' `
    $(if (-not $esignModel) { 'FAIL' } else { $t06.Status }) `
    "e-signature model: $esignModel; withdrawal order present: $paperWithdrawal (repo-authored; not a countersigned executive order, operational compliance unaudited); $($t06.Note)" `
    'Issue the executive order (countersigned) and audit e-signature job-card share in Dhaka'

# G2-07: Entry criteria check at T-6 weeks (GV-009 section 9.2)
$t6Record = @(Get-ChildItem 'docs' -Recurse -Filter '*g2*t6*entry*.md' -ErrorAction SilentlyContinue)
Gate 'G2-07' 'T-6 entry criteria check complete' `
    $(if ($t6Record.Count -gt 0) { 'PASS' } else { 'CONDITION' }) `
    $(if ($t6Record.Count -gt 0) { "G2 T-6 entry-criteria record: $($t6Record[0].Name)" } else { 'no G2 T-6 entry-criteria record under docs/ (a coverage-baseline register is not a T-6 check; G1 has gate-g1-t6-entry-criteria-review.md, G2 has none)' }) `
    'Hold the T-6 entry-criteria review for G2 and record it'

# G2-08: L6 E2E journeys 1-3 running nightly
$j01 = Test-Path 'tooling/e2e/journeys/j01-customer-books.spec.ts'
$j02 = Test-Path 'tooling/e2e/journeys/j02-walkin-repair.spec.ts'
$j03 = Test-Path 'tooling/e2e/journeys/j03-pick-drop.spec.ts'
$nightly = Get-ChildItem $evDir -Filter 'ci-nightly-run-*.json' -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
$g208Status = 'CONDITION'; $g208Ev = "journey specs j01/j02/j03 on disk: $($j01 -and $j02 -and $j03); "
if (-not ($j01 -and $j02 -and $j03)) { $g208Status = 'FAIL'; $g208Ev += 'journey spec(s) missing' }
elseif (-not $nightly) { $g208Ev += "no nightly execution evidence ($evDir/ci-nightly-run-*.json)" }
else {
    try {
        $n = Get-Content $nightly.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        $js = @($n.stages | Where-Object { $_.name -eq 'nightly-journeys' }) | Select-Object -First 1
        $jp = if ($js) { $js.measurements.journeys_passed } else { 'n/a' }
        $jf = if ($js) { $js.measurements.journeys_failed } else { 'n/a' }
        $g208Ev += "latest $($nightly.Name): runner '$($n.runner)', journeys passed $jp / failed $jf, stage $($js.status)"
        if ($n.runner -eq 'local-harness' -or -not $n.runner) { $g208Ev += ' - a local-harness run is not a scheduled nightly CI run' }
        elseif ($js -and $js.status -eq 'PASS' -and [int]$jf -eq 0) { $g208Status = 'PASS' }
        else { $g208Ev += ' - nightly journeys not green' }
    } catch { $g208Status = 'FAIL'; $g208Ev += "$($nightly.Name) unreadable" }
}
Gate 'G2-08' 'L6 E2E journeys 1-3 running nightly' $g208Status $g208Ev `
    'Run the nightly profile on a real CI runner (scheduled) and archive its evidence'

# G2-09: Gate pipeline profile: 1.5x peak + DR drill evidence
$ciYml = Test-Path '..\.github\workflows\ci.yml'
$drAll = @(Get-ChildItem $evDir -Filter '*dr-drill*.json' -ErrorAction SilentlyContinue)
$drG2 = @($drAll | Where-Object { $_.Name -match '^g2-' })
$drNote = if ($drG2.Count -gt 0) {
    try { $d = Get-Content $drG2[0].FullName -Raw -Encoding UTF8 | ConvertFrom-Json; "$($drG2[0].Name): status $($d.status), RTO $($d.sla_metrics.rto_achieved_seconds)s, RPO $($d.sla_metrics.rpo_achieved_seconds)s (repo-authored JSON)" } catch { "$($drG2[0].Name) unreadable" }
} else { "no G2-scoped DR drill evidence; $($drAll.Count) drill JSON(s) for other gates exist ($(($drAll | ForEach-Object { $_.Name }) -join ', ')), all repo-authored" }
Gate 'G2-09' 'Gate pipeline profile & DR drill evidence (PE-004 stages 16-17)' `
    $(if (-not $ciYml) { 'FAIL' } else { 'CONDITION' }) `
    "../.github/workflows/ci.yml present: $ciYml (workflow existence is not a gate run); no 1.5x-peak performance result read; $drNote" `
    'Execute the stage 16-17 gate profile and a DR drill on target infrastructure; archive runner-produced evidence'

# G2-10: Steering sign-off & residual register (no proxy: a signed report or OPEN)
$g2Signed = Test-Path "$evDir/gate-g2-signed-report.json"
Gate 'G2-10' 'Steering sign-off & residual register published' `
    $(if ($g2Signed) { 'CONDITION' } else { 'OPEN' }) `
    $(if ($g2Signed) { 'gate-g2-signed-report.json on disk - a repo-authored JSON is not a countersigned Steering minute; record the GV-003 row at sign-off' } else { "no signed G2 report ($evDir/gate-g2-signed-report.json); Steering sign-off pending (human execution)" }) `
    'Convene Steering Committee for formal MS-04 Gate G2 review'

$pass = @($script:Results | Where-Object Status -eq 'PASS').Count
$verdict = if ($script:Fail -gt 0) { 'RED' } elseif ($script:Open -gt 0) { 'RED-OPEN' } elseif ($script:Cond -gt 0) { 'PASS-WITH-CONDITIONS' } else { 'GREEN' }
Write-Host ("`nG2 Summary: PASS {0}  CONDITION {1}  OPEN {2}  FAIL {3}  (of {4})  verdict {5}" -f $pass, $script:Cond, $script:Open, $script:Fail, $script:Results.Count, $verdict) -ForegroundColor $(if ($script:Fail -or $script:Open) { 'Red' } else { 'Yellow' })

if ($Json) {
    [System.IO.File]::WriteAllText($Json, ([ordered]@{
        schema = '1000fix-erp/gate-g2/2'
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

if ($script:Fail -gt 0) { Write-Host 'G2: RED on checked criteria.' -ForegroundColor Red; exit 1 }
if ($script:Open -gt 0) { Write-Host "G2: RED-OPEN - $($script:Open) human/Steering item(s) open." -ForegroundColor Red; exit 1 }
if ($script:Cond -gt 0) { Write-Host "G2: PASS-WITH-CONDITIONS ($($script:Cond) condition(s); field outcomes not measured)." -ForegroundColor Yellow; exit 0 }
Write-Host 'G2: GREEN.' -ForegroundColor Green
exit 0
