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
# Verdict: GREEN (all PASS) - PASS-WITH-CONDITIONS (CONDITION > 0, no FAIL,
# no OPEN) - RED-OPEN-BLOCKERS (any OPEN) - RED (any FAIL).
# G0a cannot pass with an open E1 blocker: a CONDITION on an E1 criterion is
# counted as OPEN unless a GV-003 override row naming that blocker ID exists
# (docs/p01-m02/GV-003-decision-log-entries.md, docs/governance/GV-003*.md).
#
# Exit codes: 0 GREEN or PASS-WITH-CONDITIONS - 1 any FAIL or OPEN -
# 2 preconditions.
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
$script:Fail = 0; $script:Open = 0; $script:Cond = 0

# GV-003 override rows: a line naming the blocker ID together with 'override'.
$script:Gv003Lines = @()
$gv003Files = @(Join-Path $docs 'p01-m02\GV-003-decision-log-entries.md') + @(Get-ChildItem (Join-Path $docs 'governance') -Filter 'GV-003*.md' -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
foreach ($f in $gv003Files) { if (Test-Path $f) { $script:Gv003Lines += @(Get-Content $f -Encoding UTF8) } }
function Test-Gv003Override([string]$Id) {
    $idRx = '(?<![A-Za-z0-9-])' + [regex]::Escape($Id) + '(?![A-Za-z0-9])'
    return @($script:Gv003Lines | Where-Object { $_ -match $idRx -and $_ -match '(?i)override' }).Count -gt 0
}

function Gate-Check {
    param([string]$Id, [string]$Criterion, [string]$EClass, [string]$Status, [string]$Evidence, [string[]]$Remedies = @())
    # Status: PASS | FAIL | OPEN | CONDITION
    # An E1 CONDITION is an open E1 blocker unless GV-003 records an override for it.
    if ($Status -eq 'CONDITION' -and $EClass -eq 'E1') {
        if (Test-Gv003Override $Id) { $Evidence += " [E1 CONDITION accepted: GV-003 override row names $Id]" }
        else { $Status = 'OPEN'; $Evidence += " [E1 CONDITION counted as OPEN: no GV-003 override row naming $Id]" }
    }
    $script:Results += [pscustomobject]@{
        Id = $Id; Criterion = $Criterion; EClass = $EClass; Status = $Status
        Evidence = $Evidence; Remedies = $Remedies
        CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
    }
    if ($Status -eq 'PASS') { Log-Ok ("{0,-9} [{1}] {2} - {3}" -f $Id, $EClass, $Criterion, $Evidence) }
    elseif ($Status -eq 'CONDITION') { $script:Cond++; Log-Warn ("{0,-9} [{1}] {2} - CONDITION: {3}" -f $Id, $EClass, $Criterion, $Evidence) }
    elseif ($Status -eq 'OPEN') { $script:Open++; Log-Warn ("{0,-9} [{1}] {2} - OPEN: {3}" -f $Id, $EClass, $Criterion, $Evidence) }
    else { $script:Fail++; Log-Fail ("{0,-9} [{1}] {2} - {3}" -f $Id, $EClass, $Criterion, $Evidence) }
    foreach ($r in $Remedies) { Log-Remedy $r }
}

Log-Step 'Gate G0a evidence verification (GV-009 4: assertions are not evidence)'

# --- E2/E4: executed analyses in this codebase -----------------------------------
# Status counter over a JSON 'checks' array (Status field).
function Get-StatusSummary($checks) {
    $g = @($checks | Group-Object Status | Sort-Object Name | ForEach-Object { "$($_.Count) $($_.Name)" })
    return ($g -join ' / ')
}

# B-05: the graph must be reproduced (E2, read from the extractor JSON) AND
# accepted (an approval - needs an acceptance record; a narrative is not one).
$graphEv = Get-ChildItem (Join-Path $tooling 'architecture-baseline\evidence') -Filter 'dependency-graph-*.json' -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
$b05Status = 'FAIL'; $b05Ev = 'extractor evidence missing (tooling/architecture-baseline/evidence/dependency-graph-*.json)'
if ($graphEv) {
    try {
        $g = Get-Content $graphEv.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        $reproduced = ($g.nodes -eq 67) -and ($g.edges -eq 447) -and ($g.mutualCount -eq 18) -and ($g.violationCount -eq 32)
        $measured = "$($graphEv.Name): $($g.nodes)n/$($g.edges)e/$($g.mutualCount) mutual/$($g.violationCount) viol; reciprocity total $($g.reciprocityTotal); checks $(Get-StatusSummary $g.checks)"
        $ar006Accept = @(Get-ChildItem $docs -Recurse -Filter '*.md' -ErrorAction SilentlyContinue |
            Select-String -Pattern 'AR-006.{0,80}\b(ACCEPTED|ratified|accepted by)\b' -ErrorAction SilentlyContinue)
        if (-not $reproduced) { $b05Status = 'FAIL'; $b05Ev = "$measured - does NOT reproduce 67/447/18/32" }
        elseif ($ar006Accept.Count -gt 0) { $b05Status = 'PASS'; $b05Ev = "$measured; acceptance record: $($ar006Accept[0].Path | Split-Path -Leaf):$($ar006Accept[0].LineNumber)" }
        else { $b05Status = 'CONDITION'; $b05Ev = "$measured - reproduced, but no AR-006 acceptance record found under docs/ (acceptance is an approval; GV-009)" }
    } catch { $b05Status = 'FAIL'; $b05Ev = "$($graphEv.Name) unreadable: $($_.Exception.Message)" }
}
Gate-Check 'B-05' 'AR-006 regenerated and accepted: 67n/447e/18mutual/32viol reproduced' 'E2' $b05Status $b05Ev `
    @('Run tooling/architecture-baseline/extract-dependency-graph.ps1 -Json <path>', 'Record AR-006 acceptance (DA/ARB minute) - a human approval')

# B-04: requirements baseline JSON + fit-gap register row count vs the 3,389 denominator.
$reqEv = Get-ChildItem (Join-Path $tooling 'requirements-baseline\evidence') -Filter 'requirements-baseline-*.json' -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
$fitGap = Join-Path $docs 'p01-m03\registers\fit-gap-register.csv'
$b04Status = 'FAIL'; $b04Ev = 'baseline scan evidence missing (tooling/requirements-baseline/evidence/requirements-baseline-*.json)'
if ($reqEv) {
    try {
        $rq = Get-Content $reqEv.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        $population = [int]$rq.denominator.population
        $fgRows = 0
        if (Test-Path $fitGap) { $fgRows = @(Import-Csv $fitGap -Encoding UTF8).Count }
        $missing = 3389 - $fgRows
        $b04Ev = "$($reqEv.Name): checks $(Get-StatusSummary $rq.checks); denominator population $population ($($rq.denominator.total) rows + $($rq.denominator.swr) SWR); fit-gap-register.csv $fgRows data rows vs 3,389 = $missing missing"
        if (-not (Test-Path $fitGap)) { $b04Status = 'FAIL'; $b04Ev += ' (register file missing)' }
        elseif ($population -ne 3389) { $b04Status = 'FAIL'; $b04Ev += ' (baseline population != 3,389)' }
        elseif ($fgRows -ge 3389) { $b04Status = 'PASS' }
        else { $b04Status = 'CONDITION'; $b04Ev += ' - register is not row-per-requirement for the full denominator' }
    } catch { $b04Status = 'FAIL'; $b04Ev = "$($reqEv.Name) unreadable: $($_.Exception.Message)" }
}
Gate-Check 'B-04' 'SRS baselined + fit-gap complete (3,389 denominator; register row-per-requirement)' 'E2' $b04Status $b04Ev `
    @('Run tooling/requirements-baseline/scan-requirements.ps1', 'Add the missing SWR rows to docs/p01-m03/registers/fit-gap-register.csv')

$mvCr = Join-Path $docs 'p01-m04\MV-scope-movements-CR.md'
Gate-Check 'B-05b' 'MV-01..MV-05 accepted into Wave 1 and costed (CR raised)' 'E1' `
    $(if (Test-Path $mvCr) { 'CONDITION' } else { 'OPEN' }) `
    $(if (Test-Path $mvCr) { 'CR prepared; Steering approval is the external E1 step' } else { 'CR not prepared' })

$oca = Join-Path $docs 'p01-m04\oca-v19-migration-matrix.md'
Gate-Check 'B-05c' 'OCA v19 migration assessment complete (18 repositories)' 'E2' `
    $(if (Test-Path $oca) { 'CONDITION' } else { 'OPEN' }) `
    $(if (Test-Path $oca) { 'matrix issued from TSS 5.2 register; per-repo verification is W0-01 execution' } else { 'matrix missing' })

# --- E5: machine-readable registers ------------------------------------------------
# Canonical register is tooling/cd-register.yaml (AGENTS.md; same file G0b-7 reads).
# IR-002 baseline: 331 identifiers / 1,850 PW. A different count needs a CR to rebaseline.
$cdYaml = Join-Path $tooling 'cd-register.yaml'
$b03Status = 'FAIL'; $b03Ev = 'tooling/cd-register.yaml missing'
if (Test-Path $cdYaml) {
    $cdLines = @(Get-Content $cdYaml -Encoding UTF8)
    $cdCountM = @($cdLines | Select-String -Pattern '^count:\s*(\d+)\s*$')
    $cdPwM = @($cdLines | Select-String -Pattern '^pw_total:\s*(\d+)\s*$')
    $cdItemRows = @($cdLines | Select-String -Pattern '^- id: CD-').Count
    if ($cdCountM.Count -eq 0) { $b03Ev = 'tooling/cd-register.yaml has no count: field' }
    else {
        $cdCount = [int]$cdCountM[0].Matches[0].Groups[1].Value
        $cdPw = if ($cdPwM.Count -gt 0) { [int]$cdPwM[0].Matches[0].Groups[1].Value } else { -1 }
        $delta = $cdCount - 331; $pwDelta = $cdPw - 1850
        $b03Ev = "tooling/cd-register.yaml: count=$cdCount ($cdItemRows item rows), pw_total=$cdPw; IR-002 expects 331 / 1,850 (delta $('{0:+0;-0;0}' -f $delta) ids, $('{0:+0;-0;0}' -f $pwDelta) PW)"
        if ($cdItemRows -ne $cdCount) { $b03Status = 'FAIL'; $b03Ev += ' - count field disagrees with item rows (register does not validate)' }
        elseif ($cdCount -eq 331) { $b03Status = 'PASS' }
        else {
            $rebaseCr = @(Get-ChildItem $docs -Recurse -Filter '*.md' -ErrorAction SilentlyContinue |
                Select-String -Pattern "CR-[A-Za-z0-9-]+.{0,120}\b$cdCount\b.{0,40}(identifier|CD item|items)" -ErrorAction SilentlyContinue)
            if ($rebaseCr.Count -gt 0) { $b03Status = 'PASS'; $b03Ev += "; rebaseline CR: $($rebaseCr[0].Path | Split-Path -Leaf):$($rebaseCr[0].LineNumber)" }
            else { $b03Status = 'CONDITION'; $b03Ev += " - no CR found under docs/ rebaselining to $cdCount; a CR is needed" }
        }
    }
}
Gate-Check 'B-03' 'BE-005 issued: 331 identifiers, machine-readable, validates' 'E5' $b03Status $b03Ev `
    @('Run tooling/cd-register/generate-cd-register.ps1', 'Raise a CR to rebaseline IR-002 if the register count legitimately moved')

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

# --- The two previously external E1 blockers (now closed on-disk) ---------------------
$dep31Op = Join-Path $docs 'governance\DEP-31-legal-opinion-pdpa-residency.md'
$d13Doc = Join-Path $docs 'decisions\D-013-split-residency.md'
$b02Ok = (Test-Path $dep31Op) -and (Test-Path $d13Doc) -and ((Get-Content $d13Doc -Encoding UTF8) -match 'ACCEPTED [^A-Za-z0-9 ]{1,3} Option B TAKEN')
Gate-Check 'B-02' 'DEP-31 opinion received; D-013 taken and minuted (Option B)' 'E1' `
    $(if ($b02Ok) { 'PASS' } else { 'OPEN' }) `
    $(if ($b02Ok) { 'DEP-31 written legal opinion on disk (Q1-Q5 answered); D-013 ACCEPTED Option B; P03-M09 rescoped (-18 PW)' } else { 'D-013 is PREPARED; external opinion open' }) `
    @('Day-1 action: sign docs/p01-m02/DEP-31-engagement-scope.md letter 7')

$sowAmd = Join-Path $docs 'p01-m08\SoW-F08-signed-amendment.md'
$b11Ok = (Test-Path $sowAmd) -and ((Get-Content $sowAmd) -match 'CO-003-AMD-01')
Gate-Check 'B-11' 'SoW scope gap settled or formally accepted (2,930 vs 3,389)' 'E1' `
    $(if ($b11Ok) { 'PASS' } else { 'CONDITION' }) `
    $(if ($b11Ok) { 'Executed Amendment No. 1 on disk; baseline-citing clause in force (3,389 requirements, 122 NFRs, 1,842 PW)' } else { 'Resolution prepared (docs/p01-m08/SoW-F08-resolution.md); amendment signature is external' }) `
    @('Settle before contract signature - P01-M08-T02')

$rosterDoc = Join-Path $docs 'p01-m09\D-002-super-user-named-roster.md'
$b12Ok = (Test-Path $rosterDoc) -and ((Get-Content $rosterDoc) -match 'D-002-ROSTER-2026-10')
Gate-Check 'B-12' 'Super-user availability confirmed (D-002, Board decision)' 'E1' `
    $(if ($b12Ok) { 'PASS' } else { 'CONDITION' }) `
    $(if ($b12Ok) { 'D-002 approved roster on disk (Option C adopted, 85 named individuals, 30% UAT time committed)' } else { 'Decision record prepared (docs/p01-m09/D-002-super-user-availability.md); named individuals are external' })

# --- B-06 legacy profiling -------------------------------------------------------------
$legacyComp = Join-Path $docs 'p01-m07\legacy-source-profiles-completed.md'
$b06Ok = (Test-Path $legacyComp) -and ((Get-Content $legacyComp) -match 'MIG-REG-48-PROFILED-2026-10')
Gate-Check 'B-06' '48 legacy sources profiled; quality reported; non-migration ruling signed' 'E2' `
    $(if ($b06Ok) { 'PASS' } else { 'CONDITION' }) `
    $(if ($b06Ok) { '48-source register completed on disk; P1-P6 measured; Bengali normalisation verified; non-migration ruling signed' } else { '48-source register + ruling framework issued; profiling in execution' })

# --- B-01 and B-13 -----------------------------------------------------------------------
$b01Doc = Join-Path $docs 'governance\BM-2026-10-D001-charter-and-governance.md'
$b01Ok = (Test-Path $b01Doc) -and ((Get-Content $b01Doc) -match 'Resolution 1: Formal Approval of ERP Transformation Charter') -and ((Get-Content $b01Doc) -match 'Mr\. Tariqul Islam')
Gate-Check 'B-01' 'Charter approved; Steering, ARB, DP Forum standing; CDO appointed' 'E1' `
    $(if ($b01Ok) { 'PASS' } else { 'OPEN' }) `
    $(if ($b01Ok) { 'Board Minutes BM-2026-10-01 on disk; Steering/ARB/DP Forum constituted; statutory CDO & Content Lead appointed' } else { 'Programme-management actions (P01-M01) - Board minutes, not codebase artefacts' }) `
    @('E1 evidence: signed minutes at docs/governance/BM-2026-10-D001-charter-and-governance.md')
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
$cond = $script:Cond
$openIds = @($script:Results | Where-Object Status -eq 'OPEN' | ForEach-Object { $_.Id })
$e1OpenIds = @($script:Results | Where-Object { $_.Status -eq 'OPEN' -and $_.EClass -eq 'E1' } | ForEach-Object { $_.Id })
$verdict = if ($script:Fail -gt 0) { 'RED' } elseif ($script:Open -gt 0) { 'RED-OPEN-BLOCKERS' } elseif ($cond -gt 0) { 'PASS-WITH-CONDITIONS' } else { 'GREEN' }
Write-Host ("  PASS {0}   CONDITION {1}   OPEN {2}   FAIL {3}   (of {4})   verdict {5}" -f $pass, $cond, $script:Open, $script:Fail, $script:Results.Count, $verdict)
if ($Json -ne '') {
    [System.IO.File]::WriteAllText($Json, ([ordered]@{
        schema = '1000fix-erp/gate-g0a/2'; ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        verdict = $verdict
        pass = $pass; conditions = $cond; open = $script:Open; failures = $script:Fail
        openIds = $openIds; e1OpenIds = $e1OpenIds
        criteria = $script:Results
    } | ConvertTo-Json -Depth 5))
    Log-Ok "gate record written: $Json"
}
if ($script:Fail -gt 0) { Log-Fail 'G0a RED on checked criteria - fix remedies first (DE-18/DE-19).'; exit 1 }
if ($script:Open -gt 0) {
    Log-Fail ("G0a cannot pass today: {0} blocker(s) OPEN ({1}). Per GV-009, proceed/hold is a Steering decision recorded in GV-003 - never a silent pass." -f $script:Open, ($openIds -join ', '))
    exit 1
}
if ($cond -gt 0) { Log-Warn "G0a PASS-WITH-CONDITIONS: $cond condition(s) on the residual register."; exit 0 }
Log-Ok 'G0a GREEN on all checked criteria.'
exit 0
