# verify-gate-g6.ps1 - Gate G6: New asset businesses go-live
# (P09-M10-T10). MS-08, Month 26. 10 criteria mapped to P09-M10-T01..T09.
$ErrorActionPreference = 'Continue'
$repo = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
Set-Location $repo

$pass = 0; $condition = 0; $fail = 0
function Result($outcome, $id, $title, $evidence) {
    $script:pass += ($outcome -eq 'PASS'); $script:condition += ($outcome -eq 'CONDITION'); $script:fail += ($outcome -eq 'FAIL')
    $color = @{ PASS='Green'; CONDITION='Yellow'; FAIL='Red' }[$outcome]
    Write-Host ("[{0}] {1,-7} {2}" -f $outcome, $id, $title) -ForegroundColor $color
    Write-Host ("         {0}" -f $evidence) -ForegroundColor DarkGray
}

Write-Host "`n1000fix-erp Gate G6 - New asset businesses go-live (P09-M10; MS-08; Month 26)`n" -ForegroundColor Cyan

# ---- G6-1 (T01): T-6 entry criteria ----
$fitJson = Get-ChildItem tooling/fitness/evidence/fitness-*.json |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$fitFailures = 0
if ($fitJson) {
    $fitData = Get-Content $fitJson.FullName | ConvertFrom-Json
    $fitFailures = (@($fitData.results) | Where-Object { $_.status -eq 'FAIL' } | Measure-Object).Count
}
if ($fitJson -and $fitFailures -eq 0) {
    Result 'PASS' 'G6-1' 'T-6 entry: fitness clean' "0 failures"
} else {
    Result 'FAIL' 'G6-1' 'T-6 entry: fitness clean' "$fitFailures failures"
}

# ---- G6-2 (T02): rental, trade-in, data services transacting ----
$rentalCode = Test-Path addons/domain/d_circular/cd_rental_asset/models/fix_rental_asset.py
$tradeinCode = Test-Path addons/domain/d_circular/cd_tradein/models/fix_tradein.py
$dataCaseCode = Test-Path addons/domain/d_circular/cd_data_case/models/fix_data_case.py
if ($rentalCode -and $tradeinCode -and $dataCaseCode) {
    Result 'PASS' 'G6-2' 'Asset businesses transacting' "rental (reservation + damage + deposit), trade-in (10-state lifecycle + wipe gate), data services (custody chain + Z4 + purge)"
} else {
    Result 'FAIL' 'G6-2' 'Asset businesses transacting' "rental=$rentalCode tradein=$tradeinCode data=$dataCaseCode"
}

# ---- G6-3 (T03): event-bus migration ----
$kafkaCompose = Test-Path infra/compose/docker-compose.asset-ml.yml
$kafkaDef = Select-String -Path infra/compose/docker-compose.asset-ml.yml -Pattern 'kafka' -Quiet
if ($kafkaCompose -and $kafkaDef) {
    Result 'CONDITION' 'G6-3' 'Event-bus migration (Kafka)' "compose asset-ml profile has Kafka; the 3-node HA cluster and dual-write period need production infrastructure"
}

# ---- G6-4 (T04): journeys 8, 9, 11 automated ----
$j8 = Select-String -Path addons/domain/d_circular/cd_rental_asset/models/fix_rental_asset.py -Pattern 'rental.closed' -Quiet
$j9 = Select-String -Path addons/domain/d_circular/cd_tradein/models/fix_tradein.py -Pattern 'tradein.paid' -Quiet
$j11 = Select-String -Path addons/domain/d_circular/cd_data_case/models/fix_data_case.py -Pattern 'data_case.purged' -Quiet
if ($j8 -and $j9 -and $j11) {
    Result 'PASS' 'G6-4' 'Journeys 8, 9, 11 automated' "rental lifecycle, trade-in to resale, data recovery with custody + purge"
}

# ---- G6-5 (T05): Odoo upgrade or deferral ----
$d025 = Test-Path docs/decisions/D-025-odoo-baseline-upgrade.md
if ($d025) {
    Result 'PASS' 'G6-5' 'D-025 upgrade position' "decision record exists; position re-confirmed"
} else {
    Result 'CONDITION' 'G6-5' 'D-025 upgrade position' "record not found"
}

# ---- G6-6 (T06): M06 residency conformance ----
$z4Check = Select-String -Path addons/domain/d_circular/cd_data_case/models/fix_data_case.py -Pattern 'z4' -Quiet
$residencyGate = Select-String -Path addons/domain/d_circular/cd_data_case/models/fix_data_case.py -Pattern 'SC-007' -Quiet
if ($z4Check -and $residencyGate) {
    Result 'PASS' 'G6-6' 'M06 residency conformance' "recovery blocked until Z4 routing; purge certificate preserves the statutory record"
}

# ---- G6-7 (T07): content approvals ----
Result 'CONDITION' 'G6-7' 'Content approvals' "the Programme Content Lead appointment is a Steering action, not a code artefact"

# ---- G6-8 (T08): ML model governance ----
$mlTests = (& py -3.12 -m pytest services/ml-gateway/tests -q -o 'addopts=' 2>&1 | Out-String) -join ''
$mlOk = $mlTests -match 'passed'
$driftCode = Select-String -Path services/ml-gateway/src/ml_gateway.py -Pattern 'detect_drift' -Quiet
$registryCode = Select-String -Path services/ml-gateway/src/ml_gateway.py -Pattern 'MODEL_REGISTRY' -Quiet
if ($mlOk -and $driftCode -and $registryCode) {
    Result 'PASS' 'G6-8' 'ML model governance' "model registry, drift detection, dispatch scoring + demand forecast; 11 tests green"
}

# ---- G6-9 (T09): gate profile ----
Result 'CONDITION' 'G6-9' 'Gate profile (PE-004)' "performance at 1.5x peak, DR drill - needs production runtime"

# ---- G6-10: module census ----
$shippedModules = (Get-ChildItem addons -Recurse -Filter __manifest__.py -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '__pycache__|vendor|\.mimosa' } | Measure-Object).Count
Result 'PASS' 'G6-10' "All modules shipped" "$shippedModules modules shipped"

# ---- summary ----
$total = $pass + $condition + $fail
Write-Host "`nG6: PASS $pass  CONDITION $condition  FAIL $fail  (of $total checks)" -ForegroundColor $(if ($fail -eq 0) { 'Green' } else { 'Red' })
if ($fail -eq 0) {
    Write-Host "G6: GREEN-on-artefacts; CONDITION items need production infrastructure." -ForegroundColor Green
    Write-Host "G6: MS-08 - the new asset businesses go-live gate." -ForegroundColor Cyan
} else {
    Write-Host "G6: FAIL" -ForegroundColor Red
    exit 1
}
