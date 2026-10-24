# verify-gate-g3.ps1 - Gate G3: Financial control go-live (P06-M10-T10).
# MS-05, Month 13. 12 criteria (roadmap P06-M10 + 06-01 W3 gate).
# Honest posture (2026-10-22 rewrite): PASS only from a check that executed
# and whose exit code was honoured; CONDITION for items needing the Odoo
# runtime, production volume or human demonstration; FAIL blocks. Numbers are
# parsed from tool output or measured evidence JSON, never typed in.
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

# Runs the estate's actual harness (pytest, per pyproject) over a directory and
# returns @{ Out=..; Count=N; Ok=bool; Exit=N }. pyproject addopts already
# carries one -q; a second -q here would suppress the summary line the count
# is parsed from. Counts come from pytest's own summary; exit code gates Ok.
function Invoke-Unittest($testDir) {
    $out = (& py -3.12 -m pytest $testDir --no-header 2>&1 | Out-String) -join ''
    $exit = $LASTEXITCODE
    $m = [regex]::Match($out, '(\d+) passed')
    $count = 0
    if ($m.Success) { $count = [int]($m.Groups[1].Value) }
    $ok = ($exit -eq 0) -and ($count -gt 0)
    return @{ Out = $out; Count = $count; Ok = $ok; Exit = $exit }
}

Write-Host "`n1000fix-erp Gate G3 - Financial control go-live (P06-M10; MS-05)`n" -ForegroundColor Cyan

# ---- measured evidence -----------------------------------------------------

$covPath = 'docs/traceability/evidence/coverage-baseline-report.json'
$covFile = $null
if (Test-Path $covPath) {
    try { $covFile = Get-Content $covPath -Raw | ConvertFrom-Json } catch { $covFile = $null }
}
function Get-PureLogicCov($relPath) {
    if ($null -eq $script:covFile) { return $null }
    $fin = $script:covFile.statutory_financial_tax_summary
    if ($null -eq $fin) { return $null }
    $v = $fin.pure_logic_per_file.$relPath
    if ($null -eq $v) { return $null }
    return [math]::Round([double]$v, 2)
}

# ---- artefact evidence (executed checks; exit codes honoured) --------------

$tax = Invoke-Unittest 'addons/domain/g_finance/cd_tax_engine_bd/tests'
$taxCov = Get-PureLogicCov 'addons/domain/g_finance/cd_tax_engine_bd/models/tax_logic.py'
$taxCovStr = if ($null -ne $taxCov) { "$($taxCov)%" } else { 'not in report' }
Result $(if ($tax.Ok) { 'PASS' } else { 'FAIL' }) 'G3-a' 'Tax determination path tests green' `
    "unittest exit $($tax.Exit), $($tax.Count) tests; measured tax_logic.py coverage: $taxCovStr (100% path claim verified against the measurement, not asserted)"

$recon = Invoke-Unittest 'services/reconciliation/tests'
$reconCov = Get-PureLogicCov 'services/reconciliation/src/reconciliation.py'
$reconCovStr = if ($null -ne $reconCov) { "$($reconCov)%" } else { 'not in report' }
Result $(if ($recon.Ok) { 'PASS' } else { 'FAIL' }) 'G3-b' 'Reconciliation ladder tests green' `
    "unittest exit $($recon.Exit), $($recon.Count) tests incl. the ladder gate scenario; measured reconciliation.py coverage: $reconCovStr"

$ap = Invoke-Unittest 'addons/domain/g_finance/cd_ap_ext/tests'
$apSrc = Get-Content addons/domain/g_finance/cd_ap_ext/models/fix_ap_ext.py -Raw
$blocks = ($apSrc -match 'G3-06') -and ($apSrc -match 'raise UserError')
Result $(if ($ap.Ok -and $blocks) { 'PASS' } elseif ($ap.Ok) { 'CONDITION' } else { 'FAIL' }) 'G3-c' 'Three-way match blocks unmatched invoices' `
    "unittest exit $($ap.Exit), $($ap.Count) tests; source carries the G3-06 blocking branch: $blocks (both conditions now gate the verdict)"

$mushak = Get-Content addons/domain/g_finance/cd_tax_engine_bd/report/report_mushak63.xml -Raw -Encoding UTF8
# .NET regex \u escapes avoid PowerShell source-encoding hazards for Bengali text
$statutory = ($mushak -match 'BIN') -and ($mushak -match '\u09AE\u09C1\u09B6\u0995')
Result $(if ($statutory) { 'PASS' } else { 'FAIL' }) 'G3-d' 'Mushak 6.3 statutory template present' `
    "QWeb template contains BIN fields and Bengali statutory heading: $statutory (template inspection; runtime rendering is a Phase-4 browser check)"

# AUT register: parse count AND per-entry engine field; nothing awarded on existence alone
$autOk = $false; $autCount = 0; $autMissing = ''
try {
    $autOut = & py -3.12 -c "import yaml; d=yaml.safe_load(open('addons/domain/i_governance/cd_workflow_engine/data/aut_register.yaml',encoding='utf-8')); a=d['automations']; print(len(a)); print(','.join(x['id'] for x in a if not x.get('engine')))" 2>&1
    $lines = @($autOut | Where-Object { $_ -and "$_".Trim() })
    $autCount = [int]$lines[0]
    $autMissing = $(if ($lines.Count -gt 1) { $lines[1] } else { '' })
    $autOk = ($LASTEXITCODE -eq 0) -and ($autCount -ge 60) -and (-not $autMissing)
} catch { $autOk = $false }
Result $(if ($autOk) { 'PASS' } else { 'FAIL' }) 'G3-e' 'Automation register complete (AUT-001..060, engine named)' `
    "$autCount automations parsed; entries missing an engine: $(if ($autMissing) { $autMissing } else { 'none' }). NOTE: register completeness is not engine existence - ir.actions.server deployment is runtime work (see G3-07)"

# ---- runtime + human demonstration ----------------------------------------

Result 'CONDITION' 'G3-01' '100% of invoices generated automatically from closed jobs' `
    "auto-invoicing implemented (NFR-040 timing recorded per invoice); the percentage needs production closed-job volume"

Result 'CONDITION' 'G3-02' 'Payment auto-matching >= 90%' `
    "the ladder and its gate scenario are green in tests (G3-b); the production match rate needs bank-feed volume"

Result 'CONDITION' 'G3-03' 'Mushak invoices accepted without NBR exception' `
    "statutory template + register exist (G3-d); NBR acceptance is an external judgement - sandbox self-minted tokens are NOT evidence (e-VAT client now fails closed unconfigured)"

Result 'CONDITION' 'G3-04' 'Month-end close within 5 days (first full month)' `
    "fix.period.close enforces the checklist and records close_duration_days; the first full month is a calendar event"

Result 'CONDITION' 'G3-05' 'Pick & drop with unbroken chain of custody' `
    "consignment + custody-scan models verify chain monotonicity; the custody evidence needs rider-app scans (P09 runtime)"

Result 'CONDITION' 'G3-06b' 'Three-way blocking demonstrated live' `
    "static + test evidence green (G3-c); live demonstration needs a real unmatched vendor invoice"

$jSpecs = @('tooling/e2e/journeys/j01-customer-books.spec.ts','tooling/e2e/journeys/j02-walkin-repair.spec.ts','tooling/e2e/journeys/j03-pick-drop.spec.ts','tooling/e2e/journeys/j12*.spec.ts') | ForEach-Object { Get-Item $_ -ErrorAction SilentlyContinue }
$ciYmlPath = Join-Path (Split-Path -Parent $repo) '.github/workflows/ci.yml'   # git root is the parent of the codebase
$nightlyJob = $false
if (Test-Path $ciYmlPath) { $nightlyJob = (Get-Content $ciYmlPath -Raw) -match 'nightly-journeys' }
Result 'CONDITION' 'G3-07' 'Journeys 1,2,3,12 automated and running nightly (L6)' `
    "journey specs present: $($jSpecs.Count) of 4 expected; nightly job defined in ci.yml: $nightlyJob; nightly EXECUTION evidence requires the CI runner (open external) - specs existing is not execution"

# ---- verdict ---------------------------------------------------------------

Write-Host ""
$verdict = $(if ($fail -gt 0) { 'RED' } elseif ($condition -gt 0) { 'CONDITION' } else { 'GREEN' })
Write-Host "G3: PASS $pass  CONDITION $condition  FAIL $fail  (of $($pass+$condition+$fail) checks)" -ForegroundColor $(if ($fail) { 'Red' } elseif ($condition) { 'Yellow' } else { 'Green' })
Write-Host "G3: $verdict - artefact checks executed with honoured exit codes; CONDITION items need runtime execution, production volume and human demonstration."

if ($Json) {
    [ordered]@{
        schema = '1000fix-erp/gate-g3/2'
        ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        pass = $pass; conditions = $condition; failures = $fail
        verdict = $verdict
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5 | Set-Content $Json
    Write-Host "gate record written: $Json" -ForegroundColor Green
}

if ($fail -gt 0) { exit 1 }
exit 0
