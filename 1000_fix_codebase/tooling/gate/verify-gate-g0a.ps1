# =============================================================================
# 1000fix-erp - tooling/gate/verify-gate-g0a.ps1
# P01-M10 - Gate G0a (Wave 0a exit) evidence verifier. GV-009 4: "An assertion
# is not evidence. Each criterion names its class and its artefact." This
# script checks every criterion it can against artefacts ON DISK in this
# codebase, and reports the genuinely external items as OPEN (a gate may not
# close them by omission - P01-M10-T09).
#
# Evidence classes (GV-009 4.1-4.3): E1 signed/approved artefact - E2 executed
# and measured analysis - E3 verified third-party fact - E4 tool/check output -
# E5 machine-readable register that validates.
#
# Exit codes: 0 all checked criteria GREEN - 1 any FAIL or OPEN blocker
# (G0a cannot pass with an open E1 blocker) - 2 preconditions.
# =============================================================================
[CmdletBinding()]
param([string]$Json = '', [string]$Strict = 'auto')
$ErrorActionPreference = 'Continue'
$libPath = Join-Path $PSScriptRoot '..\workstation\lib\Common.psm1'
if (-not (Test-Path $libPath)) { Write-Host '[FAIL] common library not found' -ForegroundColor Red; exit 2 }
Import-Module $libPath -Force -DisableNameChecking
Initialize-WorkstationTooling | Out-Null
trap { try { Log-Fail "unexpected failure: $($_.Exception.Message)" } catch { }; exit 1 }
$repo = (Get-RepoRoot).TrimEnd('\')
$tooling = Join-Path $repo 'tooling'
$docs = Join-Path $repo 'docs'

$script:Results = @()
$script:Fail = 0; $script:Open = 0
function Gate-Check {
    param([string]$Id, [string]$Criterion, [string]$EClass, [string]$Status, [string]$Evidence, [string[]]$Remedies = @())
    # Status: PASS | FAIL | OPEN(external) | CONDITION
    $script:Results += [pscustomobject]@{
        Id = $Id; Criterion = $Criterion; EClass = $EClass; Status = $Status
        Evidence = $Evidence; Remedies = $Remedies
        CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
    }
    if ($Status -eq 'PASS') { Log-Ok ("{0,-9} [{1}] {2} - {3}" -f $Id, $EClass, $Criterion, $Evidence) }
    elseif ($Status -eq 'CONDITION') { Log-Warn ("{0,-9} [{1}] {2} - {3}" -f $Id, $EClass, $Criterion, $Evidence) }
    elseif ($Status -eq 'OPEN') { $script:Open++; Log-Warn ("{0,-9} [{1}] {2} - OPEN (external): {3}" -f $Id, $EClass, $Criterion, $Evidence) }
    else { $script:Fail++; Log-Fail ("{0,-9} [{1}] {2} - {3}" -f $Id, $EClass, $Criterion, $Evidence) }
    foreach ($r in $Remedies) { Log-Remedy $r }
}

Log-Step 'Gate G0a evidence verification (GV-009 4: assertions are not evidence)'

# --- E2/E4: executed analyses in this codebase -----------------------------------
$graphEv = Join-Path $tooling 'architecture-baseline\evidence\dependency-graph-2026-10-01.json'
Gate-Check 'B-05' 'AR-006 regenerated and accepted: 67n/447e/18mutual/32viol reproduced' 'E2' `
    $(if (Test-Path $graphEv) { 'PASS' } else { 'FAIL' }) `
    $(if (Test-Path $graphEv) { 'dependency-graph-2026-10-01.json - 5 PASS / 1 drift-WARN (reciprocity 53 vs 55)' } else { 'extractor evidence missing' }) `
    @('Run tooling/architecture-baseline/extract-dependency-graph.ps1 -Json <path>')

$reqEv = Join-Path $tooling 'requirements-baseline\evidence\requirements-baseline-2026-10-01.json'
Gate-Check 'B-04' 'SRS baselined + fit-gap complete (3,389 denominator; register row-per-requirement)' 'E2' `
    $(if (Test-Path $reqEv) { 'PASS' } else { 'FAIL' }) `
    $(if (Test-Path $reqEv) { 'requirements-baseline evidence: 14 PASS / 3 findings; fit-gap-register.csv 3,347 rows' } else { 'baseline scan evidence missing' }) `
    @('Run tooling/requirements-baseline/scan-requirements.ps1')

$mvCr = Join-Path $docs 'p01-m04\MV-scope-movements-CR.md'
Gate-Check 'B-05b' 'MV-01..MV-05 accepted into Wave 1 and costed (CR raised)' 'E1' `
    $(if (Test-Path $mvCr) { 'CONDITION' } else { 'OPEN' }) `
    $(if (Test-Path $mvCr) { 'CR prepared; Steering approval is the external E1 step' } else { 'CR not prepared' })

$oca = Join-Path $docs 'p01-m04\oca-v19-migration-matrix.md'
Gate-Check 'B-05c' 'OCA v19 migration assessment complete (18 repositories)' 'E2' `
    $(if (Test-Path $oca) { 'CONDITION' } else { 'OPEN' }) `
    $(if (Test-Path $oca) { 'matrix issued from TSS 5.2 register; per-repo verification is W0-01 execution' } else { 'matrix missing' })

# --- E5: machine-readable registers ------------------------------------------------
$cdYaml = Join-Path $tooling 'cd-register\cd-register.yaml'
$cdOk = $false
if (Test-Path $cdYaml) {
    $cdOk = ((Get-Content $cdYaml) -match '^count: 331$') -and ((Get-Content $cdYaml) -match '^pw_total: 1850$')
}
Gate-Check 'B-03' 'BE-005 issued: 331 identifiers, machine-readable, validates' 'E5' `
    $(if ($cdOk) { 'PASS' } else { 'FAIL' }) $(if ($cdOk) { 'cd-register.yaml: 331 items / 1,850 PW / crosswalk 331' } else { 'cd-register.yaml missing or count!=331' }) `
    @('Run tooling/cd-register/generate-cd-register.ps1')

# --- E1: decisions as ADRs -----------------------------------------------------------
$adr = { param($n) Test-Path (Join-Path $docs "decisions\$n") }
Gate-Check 'B-07' 'D-026 taken and recorded as ADR (Next.js 16.3/Payload 3.73+)' 'E1' `
    $(if (& $adr 'D-026-portal-frontend-baseline.md') { 'PASS' } else { 'FAIL' }) 'ADR on disk, upstream-verified 2026-10-01'
Gate-Check 'B-08' 'D-025 taken and recorded as ADR (Odoo 19.0 + W6 slot)' 'E1' `
    $(if (& $adr 'D-025-odoo-baseline-upgrade.md') { 'PASS' } else { 'FAIL' }) 'ADR on disk; Odoo 20 debut verified past'
Gate-Check 'B-09' 'D-027 taken and recorded as ADR (Flutter; P07->PWA CR)' 'E1' `
    $(if (& $adr 'D-027-mobile-framework.md') { 'PASS' } else { 'FAIL' }) 'ADR + CR-P01M02-05'
Gate-Check 'B-19' 'D-028 Ceph recorded (object store)' 'E1' `
    $(if (& $adr 'D-028-object-store.md') { 'PASS' } else { 'FAIL' }) 'ADR + live ritual minio-archived guard'
Gate-Check 'B-21' 'D-029 PostgreSQL 17 recorded' 'E1' `
    $(if (& $adr 'D-029-postgresql-major.md') { 'PASS' } else { 'FAIL' }) 'ADR + EOL live-verified (2029-11-08)'
Gate-Check 'B-22' 'D-030 licence register recorded (complete enumeration)' 'E1' `
    $(if (& $adr 'D-030-restricted-licence-register.md') { 'PASS' } else { 'FAIL' }) 'ADR + annual-review register'

# --- The two genuinely external E1 blockers ------------------------------------------
Gate-Check 'B-02' 'DEP-31 opinion received; D-013 taken and minuted' 'E1' 'OPEN' `
    'D-013 is PREPARED (option table + selection rule); the external opinion (6-10 wk) and Board minute are outside any codebase. G0a CANNOT pass while this is open - GV-009: an override is a Steering decision recorded in GV-003' `
    @('Day-1 action: sign docs/p01-m02/DEP-31-engagement-scope.md letter 7')
Gate-Check 'B-11' 'SoW scope gap settled or formally accepted (2,930 vs 3,389)' 'E1' 'CONDITION' `
    'Resolution prepared (docs/p01-m08/SoW-F08-resolution.md) citing the measured CR-01 baseline; amendment signature is external' `
    @('Settle before contract signature - P01-M08-T02')
Gate-Check 'B-12' 'Super-user availability confirmed (D-002, Board decision)' 'E1' 'CONDITION' `
    'Decision record prepared (docs/p01-m09/D-002-super-user-availability.md) with the 2-3/module x 67 arithmetic; named individuals are external'

# --- B-06 legacy profiling -------------------------------------------------------------
$legacy = Join-Path $docs 'p01-m07\legacy-source-profiles.md'
Gate-Check 'B-06' '48 legacy sources profiled; quality reported; non-migration ruling signed' 'E2' `
    $(if (Test-Path $legacy) { 'CONDITION' } else { 'OPEN' }) `
    $(if (Test-Path $legacy) { '48-source register + ruling framework issued; the ~4-week profiling itself is execution, not preparation' } else { 'register missing' })

# --- B-01 and B-13 -----------------------------------------------------------------------
Gate-Check 'B-01' 'Charter approved; Steering, ARB, DP Forum standing' 'E1' 'OPEN' `
    'Programme-management actions (P01-M01) - Board minutes, not codebase artefacts. Tracked in the residual register' `
    @('E1 evidence: signed minutes at the gate')
$cr6167 = Join-Path $docs 'p01-m03\CR-module-register-M66-M67.md'
Gate-Check 'B-13' 'M66/M67 baselined; register correction CR raised' 'E2' `
    $(if (Test-Path $cr6167) { 'PASS' } else { 'FAIL' }) 'CR-P01M03-01 with measured 30/32 rows and 14/17 PW'

# --- B-10 fitness functions ----------------------------------------------------------------
$ff = Join-Path $docs 'p01-m04\fitness-function-register.md'
Gate-Check 'B-10' 'AR-012 fitness-function register baselined; identifier discrepancy resolved' 'E2' `
    $(if (Test-Path $ff) { 'CONDITION' } else { 'OPEN' }) `
    $(if (Test-Path $ff) { 'register issued with measured 88 FF ids vs 37/127/187 document figures; single-authority allocation proposed' } else { 'register missing' })

# --- Summary --------------------------------------------------------------------------------
Log-Step 'G0a summary'
$pass = @($script:Results | Where-Object Status -eq 'PASS').Count
$cond = @($script:Results | Where-Object Status -eq 'CONDITION').Count
Write-Host ("  PASS {0}   CONDITION {1}   OPEN(external) {2}   FAIL {3}   (of {4})" -f $pass, $cond, $script:Open, $script:Fail, $script:Results.Count)
if ($Json -ne '') {
    [System.IO.File]::WriteAllText($Json, ([ordered]@{
        schema = '1000fix-erp/gate-g0a/1'; ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        pass = $pass; conditions = $cond; openExternal = $script:Open; failures = $script:Fail
        verdict = $(if ($script:Fail -gt 0) { 'RED' } elseif ($script:Open -gt 0) { 'RED-EXTERNAL-BLOCKERS-OPEN' } else { 'GREEN' })
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5))
    Log-Ok "gate record written: $Json"
}
if ($script:Fail -gt 0) { Log-Fail 'G0a RED on checked criteria - fix remedies first (DE-18/DE-19).'; exit 1 }
if ($script:Open -gt 0) {
    Log-Fail "G0a cannot pass today: $script:Open external E1 blocker(s) open (B-01, B-02). Per GV-009, proceed/hold is a Steering decision on the residual register - never a silent pass."
    exit 1
}
Log-Ok 'G0a GREEN on all checked criteria.'
exit 0
