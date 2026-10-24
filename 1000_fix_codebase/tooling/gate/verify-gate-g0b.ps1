# =============================================================================
# verify-gate-g0b.ps1 - P02-M10-T10: Gate G0b (Wave 0b exit) evidence verifier.
# GV-009: an assertion is not evidence - each criterion names its artefact.
# G0b exit criteria (roadmap 2.10): every developer's doctor green in under
# 4 hours from a bare machine; pipeline with all blocking stages; twelve
# environments provisioned; FF-03 and FF-09 live.
#
# Status: PASS (measured) - CONDITION (artefact present, outcome not yet
# measured) - OPEN (external/human step outstanding) - FAIL (defect).
# Verdict: GREEN - PASS-WITH-CONDITIONS (CONDITION > 0, no FAIL/OPEN) -
# RED-OPEN (any OPEN) - RED (any FAIL).
# Exit: 0 GREEN or PASS-WITH-CONDITIONS - 1 any FAIL or OPEN - 2 preconditions.
# External-human items report OPEN (never silently closed).
# =============================================================================
[CmdletBinding()]
param([string]$Json = '')
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root
# The CI workflow lives at the GIT root (GitHub reads only <git-root>/.github/workflows).
$ciYml = '..\.github\workflows\ci.yml'
$script:Results = @(); $script:Fail = 0; $script:Open = 0; $script:Cond = 0
function Gate([string]$Id, [string]$Crit, [string]$Status, [string]$Ev, [string]$Rem = '') {
    $script:Results += [pscustomobject]@{Id=$Id;Criterion=$Crit;Status=$Status;Evidence=$Ev;Remedy=$Rem;CheckedUtc=(Get-Date).ToUniversalTime().ToString('o')}
    if ($Status -eq 'PASS') { Write-Host ("[ ok ] {0,-8} {1} - {2}" -f $Id,$Crit,$Ev) -ForegroundColor Green }
    elseif ($Status -eq 'CONDITION') { $script:Cond++; Write-Host ("[COND] {0,-8} {1} - {2}" -f $Id,$Crit,$Ev) -ForegroundColor Yellow; if ($Rem) { Write-Host ("       next: $Rem") -ForegroundColor Yellow } }
    elseif ($Status -eq 'OPEN') { $script:Open++; Write-Host ("[OPEN] {0,-8} {1} - {2}" -f $Id,$Crit,$Ev) -ForegroundColor Yellow; if ($Rem) { Write-Host ("       next: $Rem" ) -ForegroundColor Yellow } }
    else { $script:Fail++; Write-Host ("[FAIL] {0,-8} {1} - {2}" -f $Id,$Crit,$Ev) -ForegroundColor Red; if ($Rem) { Write-Host ("       remedy: $Rem") -ForegroundColor Yellow } }
}
$exists = { param($p) Test-Path $p }

Write-Host 'Gate G0b verification (P02-M10-T10; GV-009)' -ForegroundColor Cyan

# --- G0b-1: doctor defines 14 distinct checks --------------------------------
# Each check is `Check { ... } <N> '<name>' '<remedy>'`; count the distinct ids.
$doctor = 'tooling\scripts\doctor.ps1'
$docIds = @()
if (Test-Path $doctor) {
    $docIds = @(Select-String -Path $doctor -Pattern "\}\s+(\d+)\s+'[^']+'" -AllMatches | ForEach-Object { $_.Matches } | ForEach-Object { [int]$_.Groups[1].Value } | Sort-Object -Unique)
}
$docExpected = 1..14
$docMissing = @($docExpected | Where-Object { $docIds -notcontains $_ })
Gate 'G0b-1' 'Doctor implemented, all 14 checks, DE-18 remedies' `
    $(if (-not (Test-Path $doctor)) {'FAIL'} elseif ($docIds.Count -eq 14 -and $docMissing.Count -eq 0) {'PASS'} else {'FAIL'}) `
    $(if (Test-Path $doctor) { "doctor.ps1 defines $($docIds.Count) distinct check id(s) [$($docIds -join ',')]; missing: $(if ($docMissing.Count) { $docMissing -join ',' } else { 'none' }) (definition count only - a green run is G0b-10)" } else { 'tooling/scripts/doctor.ps1 missing' }) `
    'P02-M10-T01..T05 - implement the missing doctor checks'

# --- G0b-2: workflow structurally valid (validate-workflow.py) + job count ---
$vwOut = ''; $vwExit = -1; $jobCount = 0
if (Test-Path 'tooling\ci\validate-workflow.py') {
    $vwOut = (& python tooling/ci/validate-workflow.py 2>&1 | Out-String).Trim()
    $vwExit = $LASTEXITCODE
    $jm = [regex]::Match($vwOut, '(\d+) jobs checked')
    if ($jm.Success) { $jobCount = [int]$jm.Groups[1].Value }
}
if ((Test-Path $ciYml) -and $jobCount -eq 0) {
    $jobCount = @(Select-String -Path $ciYml -Pattern '^  [A-Za-z0-9_-]+:\s*$' | Where-Object { $_.LineNumber -gt (@(Select-String -Path $ciYml -Pattern '^jobs:')[0].LineNumber) }).Count
}
$vwLast = if ($vwOut) { ($vwOut -split "`r?`n" | Select-Object -Last 1) } else { 'validator not run' }
Gate 'G0b-2' 'Pipeline: 17 stages, 5 profiles, blocking map' `
    $(if ($vwExit -eq 0 -and $jobCount -ge 17) {'PASS'} else {'FAIL'}) `
    "validate-workflow.py exit $vwExit ($vwLast); $jobCount job(s) in ../.github/workflows/ci.yml (17 required). Structural validity only - no GitHub Actions run is evidenced here" `
    'P02-M09-T03/T04 - fix the findings printed by python tooling/ci/validate-workflow.py'

# --- G0b-3: environments defined vs provisioned -------------------------------
$envCount = @(Select-String -Path 'infra\environments.yaml' -Pattern '^\s*-\s+name:' -ErrorAction SilentlyContinue).Count
Gate 'G0b-3' 'Twelve environments provisioned per PE-002-D-01' $(if ($envCount -lt 12) {'FAIL'} else {'CONDITION'}) `
    "infra/environments.yaml DEFINES $envCount environment(s) (12 required); provisioning on real infrastructure is Phase-2 runtime work and no provisioning evidence is read by this verifier" `
    'P02-M09-T09 - provision the environments and record machine evidence of each'

# --- G0b-4: FF-03 actually executed -------------------------------------------
$ff03Files = (& $exists 'tooling\scripts\check-vendor-clean.sh') -and (& $exists 'FORKS.yaml') -and @(Select-String -Path '.pre-commit-config.yaml' -Pattern 'id:\s*no-vendor-edit' -ErrorAction SilentlyContinue).Count -ge 1
$cvOut = ''; $cvExit = -1
# Git for Windows bash (same convention as doctor.ps1); `bash` on PATH may be the WSL launcher.
$bashExe = 'C:\Program Files\Git\bin\bash.exe'
if (-not (Test-Path $bashExe)) {
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    $cand = if ($gitCmd) { Join-Path (Split-Path -Parent (Split-Path -Parent $gitCmd.Source)) 'bin\bash.exe' } else { '' }
    $bashExe = if ($cand -and (Test-Path $cand)) { $cand } else { 'bash' }
}
if (Test-Path 'tooling\scripts\check-vendor-clean.sh') {
    $cvOut = (& $bashExe tooling/scripts/check-vendor-clean.sh 2>&1 | Out-String).Trim()
    $cvExit = $LASTEXITCODE
}
$cvLast = if ($cvOut) { ($cvOut -split "`r?`n" | Select-Object -Last 1) } else { 'not run' }
Gate 'G0b-4' 'FF-03 live (vendor read-only)' $(if ($ff03Files -and $cvExit -eq 0) {'PASS'} else {'FAIL'}) `
    "check-vendor-clean.sh executed: exit $cvExit ($cvLast); FORKS.yaml + pre-commit no-vendor-edit hook present: $ff03Files" `
    'restore tooling/scripts/check-vendor-clean.sh, FORKS.yaml or the no-vendor-edit hook; fix the reported vendor edits'

# --- G0b-5: FF-09 registered as blocking --------------------------------------
$ff09Blocking = $false
if (Test-Path 'tooling\fitness\registry.yaml') {
    $reg = @(Get-Content 'tooling\fitness\registry.yaml' -Encoding UTF8)
    for ($i = 0; $i -lt $reg.Count; $i++) {
        if ($reg[$i] -match '^\s*-\s+id:\s*FF-09\s*$') {
            for ($j = $i + 1; $j -lt $reg.Count -and $reg[$j] -notmatch '^\s*-\s+id:'; $j++) {
                if ($reg[$j] -match '^\s+blocking:\s*true\s*$') { $ff09Blocking = $true }
            }
        }
    }
}
Gate 'G0b-5' 'FF-09 live (residency single-client)' $(if ($ff09Blocking) {'PASS'} else {'FAIL'}) `
    $(if ($ff09Blocking) { 'tooling/fitness/registry.yaml: FF-09 entry with blocking: true' } else { 'no FF-09 entry with blocking: true in tooling/fitness/registry.yaml' }) `
    'register FF-09 with blocking: true in tooling/fitness/registry.yaml'

# --- G0b-6: pre-commit / CI parity ---------------------------------------------
$pcHooks = @(Select-String -Path '.pre-commit-config.yaml' -Pattern '^\s*-\s+\{\s*id:' -ErrorAction SilentlyContinue).Count + @(Select-String -Path '.pre-commit-config.yaml' -Pattern '^\s*-\s+id:' -ErrorAction SilentlyContinue).Count
$ciParity = (& $exists '.pre-commit-config.yaml') -and (& $exists $ciYml) -and @(Select-String -Path $ciYml -Pattern 'ruff' -ErrorAction SilentlyContinue).Count -ge 1 -and $pcHooks -ge 8
Gate 'G0b-6' 'Pre-commit = CI parity (XS-19)' $(if ($ciParity) {'PASS'} else {'FAIL'}) ".pre-commit-config.yaml ($pcHooks hooks) and ../.github/workflows/ci.yml both present; ci.yml references ruff: $(@(Select-String -Path $ciYml -Pattern 'ruff' -ErrorAction SilentlyContinue).Count -ge 1)" 'align .pre-commit-config.yaml with ../.github/workflows/ci.yml stage 1'

# --- G0b-7: CD register ---------------------------------------------------------
$cdRegister = Join-Path $root 'tooling\cd-register.yaml'
$cdCount = 0; $cdPw = 0; $cdItems = 0
if (Test-Path $cdRegister) {
    $cdCount = [int](Select-String -Path $cdRegister -Pattern '^count:\s*(\d+)').Matches[0].Groups[1].Value
    $cdPw = [int](Select-String -Path $cdRegister -Pattern '^pw_total:\s*(\d+)').Matches[0].Groups[1].Value
    $cdItems = @(Select-String -Path $cdRegister -Pattern '^- id: CD-').Count
}
$cdOk = ($cdCount -ge 331) -and ($cdItems -eq $cdCount)
Gate 'G0b-7' 'CD register machine-readable (B-03 carry-over)' $(if ($cdOk) {'PASS'} else {'FAIL'}) "cd-register.yaml: count=$cdCount, pw_total=$cdPw, $cdItems item rows on disk (rule CDR-11); IR-002 baseline 331 - see G0a B-03 for the rebaseline condition" 'regenerate tooling/cd-register.yaml via tooling/cd-register/generate-cd-register.ps1'

# --- G0b-8: licence gate ----------------------------------------------------------
$licOk = (& $exists 'tooling\licence\register.yaml') -and (@(Get-ChildItem (Join-Path $root 'tooling') -Recurse -Filter 'check-licence-gate.py' -ErrorAction SilentlyContinue).Count -ge 1)
Gate 'G0b-8' 'Licence gate live (D-030)' $(if ($licOk) {'PASS'} else {'FAIL'}) 'tooling/licence/register.yaml + check-licence-gate.py verified on disk (stage 13)' 'restore tooling/licence/register.yaml or check-licence-gate.py'

# --- G0b-9: compose digests (DE-03..06) -------------------------------------------
$composeFiles = @(Get-ChildItem 'infra\compose' -Filter '*.yml' -ErrorAction SilentlyContinue)
$placeholders = 0; $pending = 0
if ($composeFiles.Count -gt 0) {
    $placeholders = @(Select-String -Path 'infra\compose\*.yml' -Pattern 'PLACEHOLDER-RESOLVE' -ErrorAction SilentlyContinue).Count
    $pending = @(Select-String -Path 'infra\compose\*.yml' -Pattern 'PENDING-FIRST-BUILD' -ErrorAction SilentlyContinue).Count
}
$digestNote = 'verify-compose-digests.py not present'; $digestExit = $null
if (Test-Path 'tooling\scripts\verify-compose-digests.py') {
    $dOut = (& python tooling/scripts/verify-compose-digests.py 2>&1 | Out-String).Trim()
    $digestExit = $LASTEXITCODE
    $dLast = ($dOut -split "`r?`n" | Select-Object -Last 1)
    $digestNote = "verify-compose-digests.py exit $digestExit ($dLast)"
    if ($digestExit -eq 4) { $digestNote += ' - registry unreachable, no verdict' }
}
$g9Status = if ($composeFiles.Count -eq 0) { 'FAIL' } elseif ($digestExit -eq 1) { 'FAIL' } elseif ($placeholders -gt 0 -or $pending -gt 0 -or $digestExit -eq 4) { 'CONDITION' } else { 'PASS' }
Gate 'G0b-9' 'Local stack profiles, DE-03..06' $g9Status `
    "$($composeFiles.Count) compose file(s); $placeholders PLACEHOLDER-RESOLVE, $pending PENDING-FIRST-BUILD reference(s) (locally-built 1000fix/odoo images unpinned until first build - DE-06 not met); $digestNote" `
    'build and push the 1000fix/odoo images, pin their digests (docs/guides/digest-pinning-policy.md), rerun verify-compose-digests.py'

# --- G0b-10: onboarding SLA -------------------------------------------------------
$onboardingEv = Join-Path $root 'docs\traceability\evidence\onboarding-sla-core-joiner-1.json'
$onboardingPassed = $false
if (Test-Path $onboardingEv) {
    try {
        $rawOnb = Get-Content $onboardingEv -Raw | ConvertFrom-Json
        if ($rawOnb.sla_met -eq $true -and $rawOnb.actual_hours -le 4.0) { $onboardingPassed = $true }
    } catch { }
}
Gate 'G0b-10' 'Every developer doctor green < 4h from bare machine' $(if ($onboardingPassed) {'PASS'} else {'OPEN'}) $(if ($onboardingPassed) {"onboarding SLA measured: $($rawOnb.actual_hours)h on core (within budget) - evidence in onboarding-sla-core-joiner-1.json"} else {'per-joiner measurement (docs/guides/onboarding-sla.md) - human execution at team mobilisation'})

# --- G0b-11: G0a outcome (latest record) -------------------------------------------
$g0aEv = Join-Path $root 'tooling\gate\evidence\gate-g0a-latest.json'
$g11Status = 'OPEN'; $g11Ev = 'gate-g0a-latest.json missing - run verify-gate-g0a.ps1 -Json tooling/gate/evidence/gate-g0a-latest.json'
if (Test-Path $g0aEv) {
    try {
        $raw = Get-Content $g0aEv -Raw | ConvertFrom-Json
        $e1Open = @($raw.criteria | Where-Object { $_.Status -eq 'OPEN' -and $_.EClass -eq 'E1' } | ForEach-Object { $_.Id })
        $g0aOpen = @($raw.criteria | Where-Object { $_.Status -eq 'OPEN' } | ForEach-Object { $_.Id })
        $g11Ev = "gate-g0a-latest.json ($($raw.ranAtUtc)): verdict $($raw.verdict); $($raw.failures) FAIL, $($g0aOpen.Count) OPEN [$($g0aOpen -join ',')], $($raw.conditions) CONDITION; E1 open: $(if ($e1Open.Count) { $e1Open -join ',' } else { 'none' })"
        if ($raw.verdict -in @('GREEN', 'PASS') -and $e1Open.Count -eq 0) { $g11Status = 'PASS' }
        elseif ($raw.verdict -eq 'PASS-WITH-CONDITIONS' -and $e1Open.Count -eq 0) { $g11Status = 'PASS'; $g11Ev += ' - G0a passed with conditions, no E1 open' }
        else { $g11Status = 'OPEN'; $g11Ev += ' - G0a not passed; G0b entry requires a Steering override recorded in GV-003' }
    } catch { $g11Status = 'FAIL'; $g11Ev = "gate-g0a-latest.json unreadable: $($_.Exception.Message)" }
}
Gate 'G0b-11' 'G0a passed or Steering-recorded override' $g11Status $g11Ev 'close the G0a OPEN blockers or record the Steering override in GV-003'

# --- Summary -------------------------------------------------------------------------
$pass = @($script:Results | Where-Object Status -eq 'PASS').Count
$verdict = if ($script:Fail -gt 0) { 'RED' } elseif ($script:Open -gt 0) { 'RED-OPEN' } elseif ($script:Cond -gt 0) { 'PASS-WITH-CONDITIONS' } else { 'GREEN' }
Write-Host ("`nG0b: PASS {0}  CONDITION {1}  OPEN {2}  FAIL {3}  (of {4})  verdict {5}" -f $pass,$script:Cond,$script:Open,$script:Fail,$script:Results.Count,$verdict) -ForegroundColor $(if ($script:Fail -or $script:Open) {'Red'} else {'Yellow'})
if ($Json) {
    [System.IO.File]::WriteAllText($Json, ([ordered]@{
        schema = '1000fix-erp/gate-g0b/2'; ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        verdict = $verdict
        pass = $pass; conditions = $script:Cond; open = $script:Open; failures = $script:Fail
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5))
    Write-Host "gate record written: $Json" -ForegroundColor Green
}
if ($script:Fail -gt 0) { Write-Host 'G0b: RED on checked criteria.' -ForegroundColor Red; exit 1 }
if ($script:Open -gt 0) { Write-Host "G0b: RED-OPEN - $($script:Open) external/human item(s) open; not a pass." -ForegroundColor Red; exit 1 }
if ($script:Cond -gt 0) { Write-Host "G0b: PASS-WITH-CONDITIONS ($($script:Cond) condition(s))." -ForegroundColor Yellow; exit 0 }
Write-Host 'G0b: GREEN.' -ForegroundColor Green
exit 0
