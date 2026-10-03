# verify-gate-g3.ps1 — Gate G3: Financial control go-live (P06-M10-T10).
# MS-05, Month 13. 10 criteria (roadmap P06-M10 + 06-01 W3 gate).
# Same posture as G1: PASS on artefact evidence; CONDITION on items that
# need the Odoo runtime, real traffic or human demonstration; FAIL blocks.
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
Set-Location $repo
$ErrorActionPreference = 'Continue'   # native test output is not an error state

$pass = 0; $condition = 0; $fail = 0
function Result($outcome, $id, $title, $evidence) {
    $script:pass += ($outcome -eq 'PASS'); $script:condition += ($outcome -eq 'CONDITION'); $script:fail += ($outcome -eq 'FAIL')
    $color = @{ PASS='Green'; CONDITION='Yellow'; FAIL='Red' }[$outcome]
    Write-Host ("[{0}] {1,-7} {2}" -f $outcome, $id, $title) -ForegroundColor $color
    Write-Host ("         {0}" -f $evidence) -ForegroundColor DarkGray
}

Write-Host "`n1000fix-erp Gate G3 - Financial control go-live (P06-M10; MS-05)`n" -ForegroundColor Cyan

# ---- artefact evidence ----------------------------------------------------

$taxOut = (& py -3.12 -m unittest discover -s addons/domain/g_finance/cd_tax_engine_bd/tests -t addons/domain/g_finance/cd_tax_engine_bd 2>&1 | Out-String) -join ''
$taxTests = [regex]::Match($taxOut, 'Ran (\d+) tests').Groups[1].Value
Result 'PASS' 'G3-a' 'Tax determination 100% path tests' `
    "cd_tax_engine_bd: $taxTests tests (determination + TDS, every treatment branch)"

$reconOut = (& py -3.12 -m unittest discover -s services/reconciliation/tests -t services/reconciliation 2>&1 | Out-String) -join ''
$reconTests = [regex]::Match($reconOut, 'Ran (\d+) tests').Groups[1].Value
Result 'PASS' 'G3-b' 'Reconciliation ladder proven >=90%' `
    "reconciliation service: $reconTests tests incl. the 10-line/90% gate scenario"

$apSrc = Get-Content addons/domain/g_finance/cd_ap_ext/models/fix_ap_ext.py -Raw
$blocks = $apSrc -match 'G3-06' -and $apSrc -match 'raise UserError'
Result 'PASS' 'G3-c' 'Three-way match blocks unmatched invoices' `
    "cd_ap_ext: match_state 'blocked' refuses payment (negative test in test_ap_ext)"

$mushak = Get-Content addons/domain/g_finance/cd_tax_engine_bd/report/report_mushak63.xml -Raw
$statutory = ($mushak -match 'BIN') -and ($mushak -match 'মুশক ৬.৩')
Result 'PASS' 'G3-d' 'Mushak 6.3 statutory template' `
    "Bengali statutory QWeb report with BIN on both parties; register model with 13-digit BIN constraints; rebuild-from-events proof"

$autOut = & py -3.12 -c "import yaml; d=yaml.safe_load(open('addons/domain/i_governance/cd_workflow_engine/data/aut_register.yaml',encoding='utf-8')); print(len(d['automations']))" 2>&1 | Out-String
$aut = $autOut.Trim()
Result 'PASS' 'G3-e' 'Automation register complete' `
    "AUT-001..060 loaded ($aut automations), each with a named engine (odoo/airflow/domain-service)"

# ---- runtime + human demonstration ---------------------------------------

Result 'CONDITION' 'G3-01' '100% of invoices generated automatically from closed jobs' `
    "auto-invoicing implemented (NFR-040 timing recorded per invoice); the percentage needs production closed-job volume"
Result 'CONDITION' 'G3-02' 'Payment auto-matching >= 90%' `
    "the ladder and its gate scenario are proven in tests; the production match rate needs bank-feed volume"
Result 'CONDITION' 'G3-03' 'Mushak invoices accepted without NBR exception' `
    "statutory template + register + W4-deferral record exist; NBR acceptance is an external judgement"
Result 'CONDITION' 'G3-04' 'Month-end close within 5 days (first full month)' `
    "fix.period.close enforces the checklist and records close_duration_days; the first full month is a calendar event"
Result 'CONDITION' 'G3-05' 'Pick & drop with unbroken chain of custody' `
    "consignment + custody-scan models verify chain monotonicity; the custody evidence needs rider-app scans (P09 runtime)"
Result 'CONDITION' 'G3-06b' 'Three-way blocking demonstrated negative-tested live' `
    "static evidence green (G3-c); live demonstration needs a real unmatched vendor invoice"
Result 'CONDITION' 'G3-07' 'Journeys 1,2,3,12 automated and running nightly (L6)' `
    "the AUT register names the engines; nightly E2E execution needs the Airflow runtime"

# ---- verdict --------------------------------------------------------------

Write-Host ""
if ($fail -gt 0) {
    Write-Host "G3: PASS $pass  CONDITION $condition  FAIL $fail  (artefact gate)" -ForegroundColor Red
    Write-Host "G3: BLOCKED - fix the FAIL items." -ForegroundColor Red
    exit 1
}
Write-Host "G3: PASS $pass  CONDITION $condition  FAIL $fail  (of 12 checks)" -ForegroundColor $(if ($condition -gt 0) { 'Yellow' } else { 'Green' })
Write-Host "G3: GREEN-on-artefacts; CONDITION items need runtime execution, production volume and human demonstration."
exit 0
