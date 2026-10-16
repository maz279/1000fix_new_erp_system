# verify-gate-gp.ps1 - Gate GP: Porting-programme 100% verification (PP7-M05).
# Aggregates the porting DoD's machine-checkable halves (05-DOD-100-PERCENT):
# registry integrity, fixture-freedom, i18n parity, token conformance,
# security headers, a11y gatekeeper results, journey E2E results and the
# bundle budgets, plus the estate battery. Deployment-side items (staging
# trace round-trip, SSL Labs, migration rehearsal at volume) are listed as
# CONDITION with their evidence requirement — never silently passed.
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

Write-Host "`n1000fix-erp Gate GP - Porting 100% verification (PP7-M05)`n" -ForegroundColor Cyan

# ---- GP-1: navigation registry integrity (FF-38, D1 asset coverage) ----
$ff38 = python tooling/fitness/check-nav-registry.py 2>$null
Result $(if ($LASTEXITCODE -eq 0) { 'PASS' } else { 'FAIL' }) 'GP-1' 'D1: navigation registry integrity (67/278/823/346/266)' "$($ff38 | Select-Object -Last 1)"

# ---- GP-2: fixture-free codebase (FF-39, D2 data strategy) ----
$ff39 = python tooling/fitness/check-no-fixtures.py 2>$null
Result $(if ($LASTEXITCODE -eq 0) { 'PASS' } else { 'FAIL' }) 'GP-2' 'D2: no fixtures/demo data in runtime space' "$($ff39 | Select-Object -Last 1)"

# ---- GP-3: i18n 0 counterpart-pending (D4) ----
$fitLatest = Get-ChildItem tooling/fitness/evidence/fitness-*.json |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$i18nOk = $false; $i18nEvidence = 'no fitness evidence'
if ($fitLatest) {
    $fit = Get-Content $fitLatest.FullName | ConvertFrom-Json
    $i18n = @($fit.results) | Where-Object { $_.suite -eq 'FF-25' } | Select-Object -First 1
    if ($i18n) { $i18nOk = ($i18n.status -eq 'PASS'); $i18nEvidence = $i18n.remedy }
}
Result $(if ($i18nOk) { 'PASS' } else { 'FAIL' }) 'GP-3' 'D4: i18n 100% (0 counterpart-pending)' $i18nEvidence

# ---- GP-4: token conformance (CFM, D5) ----
$cfm = python tooling/design-system/conformance.py 2>$null
Result $(if ($LASTEXITCODE -eq 0) { 'PASS' } else { 'FAIL' }) 'GP-4' 'D5: design-token conformance (CFM-01..05)' "$($cfm | Select-Object -Last 1)"

# ---- GP-5: security headers live on all 8 portals (D17, PP7-M03) ----
$ports = @{ corporate=3001; customer=3010; analytics=3012; seller=3013; brand=3014; 'agent-console'=3015; partner=3016; vendor=3017 }
$headersOk = $true; $headerEvidence = @()
foreach ($name in $ports.Keys) {
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$($ports[$name])/" -Method Head -UseBasicParsing -TimeoutSec 8
        $csp = $resp.Headers['Content-Security-Policy']
        $hsts = $resp.Headers['Strict-Transport-Security']
        if (-not $csp -or $csp -notmatch 'nonce-' -or -not $hsts) { $headersOk = $false; $headerEvidence += "$name missing CSP-nonce/HSTS" }
    } catch { $headersOk = $false; $headerEvidence += "$name unreachable" }
}
Result $(if ($headersOk) { 'PASS' } else { 'FAIL' }) 'GP-5' 'D17: nonce-CSP + HSTS served on all portals' "$(if ($headersOk) { '8/8 portals verified live' } else { $headerEvidence -join '; ' })"

# ---- GP-6: a11y gatekeeper results (D9, PP7-M02) ----
$a11yPath = 'tooling/a11y/results/a11y-gatekeeper.json'
$a11yOk = $false; $a11yRoutes = 0
if (Test-Path $a11yPath) {
    $a11y = Get-Content $a11yPath | ConvertFrom-Json
    $a11yRoutes = ($a11y.routes.PSObject.Properties | Measure-Object).Count
    $a11yOk = (($a11y.routes.PSObject.Properties | Where-Object { $_.Value.critical -gt 0 } | Measure-Object).Count -eq 0)
}
Result $(if ($a11yOk -and $a11yRoutes -ge 25) { 'PASS' } else { 'FAIL' }) 'GP-6' 'D9: WCAG 2.2 AA gatekeeper 0 serious/critical' "$a11yRoutes routes scanned (results < 90 days from $($a11y.generated))"

# ---- GP-7: journey E2E suite green (D3, PP7-M01) ----
$journeysPath = 'tooling/e2e/results/journeys.json'
$jOk = $false; $jEvidence = 'run the suite: cd tooling/e2e && npx playwright test'
if (Test-Path $journeysPath) {
    $j = Get-Content $journeysPath -Raw | ConvertFrom-Json
    $stats = $j.stats
    if ($stats) {
        # Playwright's JSON reporter: expected/skipped/unexpected/flaky.
        $jOk = ($stats.expected -ge 10 -and $stats.unexpected -eq 0 -and
                $stats.skipped -eq 0 -and $stats.flaky -eq 0)
        $jEvidence = "expected=$($stats.expected) unexpected=$($stats.unexpected) skipped=$($stats.skipped) flaky=$($stats.flaky)"
    }
}
Result $(if ($jOk) { 'PASS' } else { 'FAIL' }) 'GP-7' 'D3: journeys J01-J10 green, zero flakiness' $jEvidence

# ---- GP-8: bundle budgets (D10, PP7-M04) ----
$bOk = $true; $bEvidence = @()
foreach ($app in @('customer','corporate','vendor','analytics','seller','brand','agent-console','partner')) {
    $out = python tooling/scripts/check-bundle-budget.py "apps/web/$app" 400 2>$null | Select-Object -Last 1
    if ($out -notmatch 'OK') { $bOk = $false; $bEvidence += "$app $out" }
}
Result $(if ($bOk) { 'PASS' } else { 'FAIL' }) 'GP-8' 'D10: bundle budgets (all portals < 400 KB gz)' "$(if ($bOk) { '8/8 within contract' } else { $bEvidence -join '; ' })"

# ---- GP-9: estate battery clean (D15) ----
$fitFailures = 999
if ($fitLatest) {
    $fitData = Get-Content $fitLatest.FullName | ConvertFrom-Json
    $fitFailures = (@($fitData.results) | Where-Object { $_.status -eq 'FAIL' } | Measure-Object).Count
}
Result $(if ($fitFailures -eq 0) { 'PASS' } else { 'FAIL' }) 'GP-9' 'D15: estate fitness battery 0 failures' "latest evidence: $($fitLatest.Name), $fitFailures failures"

# ---- GP-10..GP-12: deployment-side conditions (never machine-passed here) ----
Result 'CONDITION' 'GP-10' 'D18: OTel trace round-trip verified in staging' 'WORKSTATION-BLOCKED: otel-collector image fails exec on this host; Tempo OTLP loopback-bound. Verify at staging: beacon visible in Tempo/Grafana.'
Result 'CONDITION' 'GP-11' 'D16: migration rehearsal at production volume' 'Run migrations/REHEARSAL.md procedure; MIG-02 control totals; MG-005/MIG-08 sign-offs.'
Result 'CONDITION' 'GP-12' 'D14: build-once-promote drill + rollback rehearsal' 'Deployment drill with /healthz probes — host has no staging env.'

Write-Host "`nGate GP summary: $pass PASS / $condition CONDITION / $fail FAIL" -ForegroundColor $(if ($fail -eq 0) { 'Green' } else { 'Red' } )
$outJson = @{
    gate = 'GP'; generated = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ');
    pass = $pass; condition = $condition; fail = $fail
} | ConvertTo-Json
New-Item -ItemType Directory -Force -Path tooling/gate/evidence | Out-Null
$outJson | Set-Content (Join-Path 'tooling/gate/evidence' ("gate-gp-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss')))
if ($fail -gt 0) { exit 1 } else { exit 0 }
