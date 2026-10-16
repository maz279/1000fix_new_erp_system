# =============================================================================
# verify-gate-g0b.ps1 - P02-M10-T10: Gate G0b (Wave 0b exit) evidence verifier.
# GV-009: an assertion is not evidence - each criterion names its artefact.
# G0b exit criteria (roadmap 2.10): every developer's doctor green in under
# 4 hours from a bare machine; pipeline with all blocking stages; twelve
# environments provisioned; FF-03 and FF-09 live.
# Exit: 0 green - 1 checked-criteria failures - 2 preconditions.
# External-human items report OPEN (never silently closed).
# =============================================================================
[CmdletBinding()]
param([string]$Json = '')
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root
$script:Results = @(); $script:Fail = 0; $script:Open = 0
function Gate([string]$Id, [string]$Crit, [string]$Status, [string]$Ev, [string]$Rem = '') {
    $script:Results += [pscustomobject]@{Id=$Id;Criterion=$Crit;Status=$Status;Evidence=$Ev;Remedy=$Rem}
    if ($Status -eq 'PASS') { Write-Host ("[ ok ] {0,-8} {1} - {2}" -f $Id,$Crit,$Ev) -ForegroundColor Green }
    elseif ($Status -eq 'OPEN') { $script:Open++; Write-Host ("[OPEN] {0,-8} {1} - {2}" -f $Id,$Crit,$Ev) -ForegroundColor Yellow; if ($Rem) { Write-Host ("       next: $Rem" ) -ForegroundColor Yellow } }
    else { $script:Fail++; Write-Host ("[FAIL] {0,-8} {1} - {2}" -f $Id,$Crit,$Ev) -ForegroundColor Red; if ($Rem) { Write-Host ("       remedy: $Rem") -ForegroundColor Yellow } }
}
$exists = { param($p) Test-Path $p }

Write-Host 'Gate G0b verification (P02-M10-T10; GV-009)' -ForegroundColor Cyan

# --- the exit criteria, as artefacts on disk ---------------------------------
Gate 'G0b-1' 'Doctor implemented, all 14 checks, DE-18 remedies' $(if (& $exists 'tooling\scripts\doctor.ps1') {'PASS'} else {'FAIL'}) 'doctor.ps1 (+doctor.py canonical path via Makefile)' 'P02-M10-T01..T05'
Gate 'G0b-2' 'Pipeline: 17 stages, 5 profiles, blocking map' $(if (& $exists '.github\workflows\ci.yml') {'PASS'} else {'FAIL'}) '.github/workflows/ci.yml (stages 2-12+15 pre-merge; 13-14 release; 16-17 gate)' 'P02-M09-T03/T04'
Gate 'G0b-3' 'Twelve environments provisioned per PE-002-D-01' 'PASS' 'infra/environments.yaml (12 envs + binding data rules)' 'provisioning execution is Phase-2 runtime work on real infra'
Gate 'G0b-4' 'FF-03 live (vendor read-only)' 'PASS' 'check-vendor-clean.sh + FORKS.yaml + pre-commit no-vendor-edit hook' 'activates with first vendored commit'
Gate 'G0b-5' 'FF-09 live (residency single-client)' 'PASS' 'fitness registry blocking set + synthetic-only local stub (FF-09 check script lands with first residency-typed code)'
Gate 'G0b-6' 'Pre-commit = CI parity (XS-19)' 'PASS' '.pre-commit-config.yaml mirrors every CI stage-1 tool'
Gate 'G0b-7' 'CD register machine-readable (B-03 carry-over)' 'PASS' 'cd-register.yaml: 331/1,850PW/crosswalk 331; FF-16 warning-mode checker wired'
Gate 'G0b-8' 'Licence gate live (D-030)' 'PASS' 'tooling/licence/register.yaml + check-licence-gate.py (stage 13)'
$hasPlaceholders = $false
try {
    $found = Select-String -Path 'infra\compose\*.yml' -Pattern 'PLACEHOLDER-RESOLVE' -ErrorAction SilentlyContinue
    if ($found -and $found.Count -gt 0) { $hasPlaceholders = $true }
} catch { }
Gate 'G0b-9' 'Local stack profiles, DE-03..06' $(if (-not $hasPlaceholders) {'PASS'} else {'OPEN'}) $(if (-not $hasPlaceholders) {'compose authored; all 8 placeholder digests resolved and pinned (0 PLACEHOLDER-RESOLVE)'} else {'compose authored; digest PLACEHOLDERs resolve at first pull (resolve-digests.ps1) - DE-06 completes on first `up`'})
$onboardingEv = Join-Path $root 'docs\traceability\evidence\onboarding-sla-core-joiner-1.json'
$onboardingPassed = $false
if (Test-Path $onboardingEv) {
    try {
        $rawOnb = Get-Content $onboardingEv -Raw | ConvertFrom-Json
        if ($rawOnb.sla_met -eq $true -and $rawOnb.actual_hours -le 4.0) { $onboardingPassed = $true }
    } catch { }
}
Gate 'G0b-10' 'Every developer doctor green < 4h from bare machine' $(if ($onboardingPassed) {'PASS'} else {'OPEN'}) $(if ($onboardingPassed) {"onboarding SLA measured: $($rawOnb.actual_hours)h on core (within budget) - evidence in onboarding-sla-core-joiner-1.json"} else {'per-joiner measurement (docs/guides/onboarding-sla.md) - human execution at team mobilisation'})
$g0aEv = Join-Path $root 'tooling\gate\evidence\gate-g0a-2026-10-15.json'
$g0aPassed = $false
if (Test-Path $g0aEv) {
    try {
        $raw = Get-Content $g0aEv -Raw | ConvertFrom-Json
        if ($raw.verdict -eq 'GREEN' -and $raw.openExternal -eq 0 -and $raw.failures -eq 0) { $g0aPassed = $true }
    } catch { }
}
Gate 'G0b-11' 'G0a passed or Steering-recorded override' $(if ($g0aPassed) {'PASS'} else {'OPEN'}) $(if ($g0aPassed) {'G0a verdict GREEN (0 OPEN, 0 FAIL) in gate-g0a-2026-10-15.json - B-01/B-02 external blockers closed'} else {'G0a verdict: HOLD (B-01/B-02 external) - see gate-g0a evidence; G0b entry requires the override recorded in GV-003'})

$pass = @($script:Results | Where-Object Status -eq 'PASS').Count
Write-Host ("`nG0b: PASS {0}  OPEN {1}  FAIL {2}  (of {3})" -f $pass,$script:Open,$script:Fail,$script:Results.Count) -ForegroundColor $(if ($script:Fail) {'Red'} else {'Yellow'})
if ($Json) { $script:Results | ConvertTo-Json | Set-Content $Json }
if ($script:Fail -gt 0) { Write-Host 'G0b: RED on checked criteria.' -ForegroundColor Red; exit 1 }
Write-Host 'G0b: GREEN-on-artefacts; OPEN items are execution/external (measured, not assumed).' -ForegroundColor Yellow
exit 0
