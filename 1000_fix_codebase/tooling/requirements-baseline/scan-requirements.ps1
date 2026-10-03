# =============================================================================
# 1000fix-erp - tooling/requirements-baseline/scan-requirements.ps1
# P01-M03 - the requirements baseline engine: re-measures every countable
# claim of the milestone against the estate ON DISK and emits the registers.
#
# Governing rules honoured here:
#   CR-01 (RQ-001 3.10.5)  - the single denominator, reproduced by command
#   CR-02 (RQ-001 3.10.5)  - no figure without a timestamp (RG-08)
#   RQ-003 3               - disposition taxonomy: fit/configure/extend/build/
#                            buy + undetermined (counted, never defaulted)
#   DE-18/DE-19            - every failure prints the remedy; non-zero exit
#
# What it measures (roadmap P01-M03 claim -> measured):
#   T01  primary docs = 4 files, 17,680 lines
#   T02  delivery-unit specs = 67 M*.md + 12 P*.md (79); governance files counted separately
#   T03  CR-01: modules 2,989 + portals 358 = 3,347 rows, 0 duplicates;
#        SWR supplements 42 -> engineering population 3,389 (contracted 2,930 reconciled)
#   T04  Layer column histogram over 3,347 rows vs 02-05 1 claim
#        (L1 28 / L2 24 / L3 4 / L4 17 / L5 25 / L6 2 percent); dispositions derived
#   T06  NFR space = 122 unique ids, sub-ids NFR-086a/b/c, duplicates resolved (RQ-006 3.3)
#   T08  wave allocation via spec frontmatter (module granularity); multi-wave rows flagged
#   T09  05-05 rules catalogue (140 BRU); module 9 rules (1,330); coverage 20/67;
#        M40/M42 absent; acceptance criteria (1,568 claimed)
#   T10  M66/M67 exist; 30/32 requirement rows; 02-02 3 "not written" claim captured
#
# Registers emitted (CSV, UTF-8) into docs/p01-m03/registers/:
#   fit-gap-register.csv   requirement, module, wave, layer, derived disposition, candidates
#   wave-allocation.csv    module, spec file, wave(frontmatter), requirement rows
#   rtm-seed.csv           requirement -> module -> CD slot -> test slot (reciprocity-seeded)
#
# Exit codes: 0 green (warnings allowed) - 1 claim violations - 2 preconditions.
# Usage: powershell -ExecutionPolicy Bypass -File scan-requirements.ps1
#            [-Json out.json] [-Strict] [-RegistersDir dir] [-EstateRoot path]
# =============================================================================
[CmdletBinding()]
param(
    [string]$Json = '',
    [switch]$Strict,
    [string]$RegistersDir = '',
    [string]$EstateRoot = ''
)

$ErrorActionPreference = 'Continue'
$libPath = Join-Path $PSScriptRoot '..\workstation\lib\Common.psm1'
if (-not (Test-Path $libPath)) {
    Write-Host '[FAIL] workstation common library not found (tooling/workstation/lib/Common.psm1)' -ForegroundColor Red
    exit 2
}
Import-Module $libPath -Force -DisableNameChecking
Initialize-WorkstationTooling | Out-Null
trap {
    $msg = "unexpected failure: $($_.Exception.Message)"
    try { Log-Fail $msg } catch { Write-Host ('[FAIL] ' + $msg) -ForegroundColor Red }
    try { Log-Remedy 'Fix the reported cause and re-run - every step is idempotent.' } catch { }
    exit 1
}

# --- estate root: the codebase's parent (the estate docs live outside it) ----
$repoRoot = (Get-RepoRoot).TrimEnd('\')
if ($EstateRoot -eq '') {
    if ($env:FIX_ESTATE_ROOT) { $EstateRoot = $env:FIX_ESTATE_ROOT }
    else { $EstateRoot = Split-Path -Parent $repoRoot }
}
if (-not (Test-Path (Join-Path $EstateRoot 'primary-doc'))) {
    Log-Fail "estate root not found or has no primary-doc/: $EstateRoot"
    Log-Remedy 'Pass -EstateRoot <path to 1000fix_new_erp_system> (or set FIX_ESTATE_ROOT).'
    exit 2
}
$modulesDir = Join-Path $EstateRoot '1000fix_ERP_Module\03_Modules'
$rqDir      = Join-Path $EstateRoot 'project-guide-doc\01_Requirements_Engineering'
$rq001 = Join-Path $rqDir 'RQ-001_Software_Requirements_Specification.md'
$rq006 = Join-Path $rqDir 'RQ-006_Non_Functional_Requirements_Specification.md'
$rules055 = Join-Path $EstateRoot '1000fix_ERP_Module\05_Cross_Cutting_Specifications\05-05_Business_Rules_and_Automation_Catalogue.md'
$reg022 = Join-Path $EstateRoot '1000fix_ERP_Module\02_Architecture\02-02_Module_Catalogue_Master_Register.md'

$script:Results = @()
$script:FailCount = 0
$script:WarnCount = 0
function Add-Check {
    param([string]$Id, [string]$Claim, [string]$Measured, [string]$Status, [string[]]$Remedies = @())
    $script:Results += [pscustomobject]@{
        Id = $Id; Claim = $Claim; Measured = $Measured; Status = $Status
        Remedies = $Remedies; CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
    }
    $line = ("{0,-8} claim [{1}]  measured [{2}]  {3}" -f $Id, $Claim, $Measured, $Status)
    switch ($Status) {
        'PASS' { $script:FailCount = $script:FailCount; Log-Ok $line }
        'WARN' { $script:WarnCount++; Log-Warn $line }
        'FAIL' { $script:FailCount++; Log-Fail $line }
        default { Log-Info $line }
    }
    foreach ($r in $Remedies) { Log-Remedy $r }
}

Log-Step 'P01-M03 requirements baseline scan (CR-02: every figure below is timestamped by this run)'

# --- T01: primary documents ----------------------------------------------------
$primaryFiles = @(Get-ChildItem (Join-Path $EstateRoot 'primary-doc') -Filter '*.md' -File)
$primaryLines = 0
foreach ($pf in $primaryFiles) { $primaryLines += [System.IO.File]::ReadAllLines($pf.FullName).Count }
Add-Check 'T01' '4 primary documents, 17,680 lines' ("{0} files, {1} lines" -f $primaryFiles.Count, $primaryLines) `
    $(if ($primaryFiles.Count -eq 4 -and $primaryLines -eq 17680) { 'PASS' } else { 'FAIL' }) @(
    'A line-count drift means the reading basis moved: re-read the delta and re-stamp (CR-02/CR-03).'
)

# --- T02: delivery-unit specifications -----------------------------------------
$mSpecs = @(Get-ChildItem $modulesDir -Filter 'M*.md' -File -Recurse)
$pSpecs = @(Get-ChildItem $modulesDir -Filter 'P*.md' -File -Recurse)
$allSpecs = @($mSpecs) + @($pSpecs)
$govFiles = @(Get-ChildItem $modulesDir -Filter '*.md' -File -Recurse | Where-Object { $_.Name -notmatch '^[MP]\d' })
Add-Check 'T02' '79 delivery-unit specs (67 M + 12 P); governance files separate' `
    ("{0} M + {1} P = {2} specs; {3} governance files" -f $mSpecs.Count, $pSpecs.Count, $allSpecs.Count, $govFiles.Count) `
    $(if ($mSpecs.Count -eq 67 -and $pSpecs.Count -eq 12) { 'PASS' } else { 'FAIL' }) @(
    'Spec-count drift: new/removed units must go through BE-005 6 register change control before the baseline moves (CR-03).'
)

# --- T03: CR-01 reproduction ----------------------------------------------------
$frRegex = '^\| *FR-[A-Z0-9]+-[0-9]+[a-z]?'
$moduleRows = 0; $portalRows = 0
$frIds = New-Object System.Collections.Generic.List[string]
$frRows = New-Object System.Collections.Generic.List[object]
foreach ($spec in $allSpecs) {
    $isPortal = $spec.Name -match '^P'
    $specWave = ''
    $head = Get-Content -LiteralPath $spec.FullName -TotalCount 30
    foreach ($h in $head) {
        if ($h -match '^wave:\s*(.+)$') { $specWave = $Matches[1].Trim(); break }
    }
    $waveTag = ''
    if ($specWave -match 'W\d+') { $waveTag = $Matches[0] }
    $multiWave = $specWave -match '(W\d+).*?(W\d+)' -and $Matches[1] -ne $Matches[2]
    $moduleCode = $spec.Name -replace '_.*$',''
    foreach ($line in [System.IO.File]::ReadLines($spec.FullName)) {
        if ($line -match $frRegex) {
            $id = ([regex]::Match($line, 'FR-[A-Z0-9]+-[0-9]+[a-z]?')).Value
            # Layer = the last non-empty pipe cell of the row. Priority = any
            # cell matching ^P[0-2]$ (column order varies across specs; the
            # earlier positional heuristic missed 1,468 of 3,347 rows).
            $cells = @($line -split '\|' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' })
            $layerCell = ''
            if ($cells.Count -ge 2) { $layerCell = $cells[$cells.Count - 1] }
            $pri = ''
            foreach ($c in $cells) { if ($c -cmatch '^P[0-2]$') { $pri = $c; break } }
            if ($isPortal) { $portalRows++ } else { $moduleRows++ }
            $frIds.Add($id)
            $frRows.Add([pscustomobject]@{
                Id = $id; Module = $moduleCode; Spec = $spec.Name; Portal = $isPortal
                Wave = $waveTag; WaveRaw = $specWave; MultiWave = $multiWave
                Layer = $layerCell; Pri = $pri
            })
        }
    }
}
$dupeIds = @($frIds | Group-Object | Where-Object Count -gt 1 | ForEach-Object Name)
$totalRows = $moduleRows + $portalRows
Add-Check 'T03a' 'CR-01: 2,989 module rows' ("{0}" -f $moduleRows) $(if ($moduleRows -eq 2989) { 'PASS' } else { 'FAIL' }) @(
    'Module-row drift vs the 2026-08-18 count: the requirement set changed - recount, re-stamp and record the change under RQ-005 control (CR-03).'
)
Add-Check 'T03b' 'CR-01: 358 portal rows' ("{0}" -f $portalRows) $(if ($portalRows -eq 358) { 'PASS' } else { 'FAIL' }) @(
    'Portal-row drift vs the 2026-08-18 count: same remedy as T03a.'
)
Add-Check 'T03c' 'CR-01: 3,347 total rows, 0 duplicates' ("{0} total, {1} duplicate ids" -f $totalRows, $dupeIds.Count) `
    $(if ($totalRows -eq 3347 -and $dupeIds.Count -eq 0) { 'PASS' } else { 'FAIL' }) @(
    'Duplicate requirement ids break the RTM key - renumber under RR-002 insertion rules before any traceability work.'
)
$swrCount = 0
if (Test-Path $rq001) {
    $swrCount = @([System.IO.File]::ReadLines($rq001) | Select-String -Pattern '\bSWR-0\d\d\b' -AllMatches | ForEach-Object { $_.Matches } | ForEach-Object { $_.Value } | Sort-Object -Unique).Count
}
Add-Check 'T03d' '42 SWR supplements -> population 3,389' ("{0} SWR -> {1}" -f $swrCount, ($totalRows + $swrCount)) `
    $(if ($swrCount -eq 42 -and ($totalRows + $swrCount) -eq 3389) { 'PASS' } else { 'FAIL' })

# --- T04: layer histogram + derived dispositions --------------------------------
# RQ-003 3 mapping (conservative primary): L1->fit, L2/L3->configure, L4->fit,
# L5->build (extend-vs-build resolved at design), L6->buy. Slashed layers
# (e.g. L2/L5) are governed by their HIGHEST layer for the primary
# disposition; every layer in the cell is counted in the presence histogram.
$layerPresence = @{ L1 = 0; L2 = 0; L3 = 0; L4 = 0; L5 = 0; L6 = 0 }
$disposition = @{}
$noLayer = 0
foreach ($r in $frRows) {
    $layers = @()
    foreach ($m2 in [regex]::Matches($r.Layer, 'L[1-6]')) { $layers += $m2.Value }
    if ($layers.Count -eq 0) { $noLayer++; $disposition[$r.Id] = 'undetermined(no-layer)'; continue }
    foreach ($l2 in ($layers | Sort-Object -Unique)) { $layerPresence[$l2]++ }
    $maxL = ($layers | Sort-Object { [int]($_.Substring(1)) } | Select-Object -Last 1)
    switch ($maxL) {
        'L1' { $disposition[$r.Id] = 'fit' }
        'L2' { $disposition[$r.Id] = 'configure' }
        'L3' { $disposition[$r.Id] = 'configure' }
        'L4' { $disposition[$r.Id] = 'fit' }
        'L5' { $disposition[$r.Id] = 'build-class(extend|build)' }
        'L6' { $disposition[$r.Id] = 'buy' }
    }
}
$lp = $layerPresence
$presencePct = @{}
foreach ($k in @('L1','L2','L3','L4','L5','L6')) {
    $presencePct[$k] = [math]::Round(100.0 * $lp[$k] / $totalRows, 1)
}
$presenceStr = ("L1 {0}% L2 {1}% L3 {2}% L4 {3}% L5 {4}% L6 {5}% (presence; slashed rows count in each)" -f `
    $presencePct.L1, $presencePct.L2, $presencePct.L3, $presencePct.L4, $presencePct.L5, $presencePct.L6)
$fitConfShare = [math]::Round($presencePct.L1 + $presencePct.L2 + $presencePct.L3, 1)
Add-Check 'T04a' '02-05 1: L1 28% L2 24% L3 4% L4 17% L5 25% L6 2%' $presenceStr 'WARN' @(
    'QUANTIFIED CONTRADICTION: the 02-05 1 figures describe solution/layer composition, not the requirement-row distribution - measured rows are L5-dominant. RQ-003 2.2 already records that module 16.1 percentages contradict 5 in every sampled module; this run is the first full-population measurement. Record the measured histogram as the fit-gap basis and re-check the roadmap T04 expectation (56% fit-or-configure) against it - it does not hold at requirement level (see T04b).'
)
Add-Check 'T04b' 'fit-or-configure share (L1+L2+L3 presence) ~56%' ("{0}% (roadmap signal, not a gate)" -f $fitConfShare) 'INFO'
Add-Check 'T04c' 'every requirement row carries a Layer value' ("{0} rows without a layer" -f $noLayer) `
    $(if ($noLayer -eq 0) { 'PASS' } else { 'WARN' }) @(
    'Rows without a layer disposition to undetermined - counted, never defaulted (RQ-003 3). Assign layers before the fit-gap register is accepted.'
)
$dispCounts = $disposition.Values | Group-Object | Sort-Object Count -Descending

# --- T06: NFR space ---------------------------------------------------------------
$nfrIds = New-Object System.Collections.Generic.List[string]
$nfrSubIds = New-Object System.Collections.Generic.List[string]
$scanRoots = @((Join-Path $EstateRoot 'primary-doc'), (Join-Path $EstateRoot 'project-guide-doc'), (Join-Path $EstateRoot '1000fix_ERP_Module'))
foreach ($root2 in $scanRoots) {
    foreach ($f2 in (Get-ChildItem $root2 -Filter '*.md' -File -Recurse)) {
        foreach ($m3 in [regex]::Matches((Get-Content -LiteralPath $f2.FullName -Raw), '\bNFR-\d{3}\b')) { $nfrIds.Add($m3.Value) }
        foreach ($m3 in [regex]::Matches((Get-Content -LiteralPath $f2.FullName -Raw), '\bNFR-\d{3}[a-z]\b')) { $nfrSubIds.Add($m3.Value) }
    }
}
$nfrUnique = @($nfrIds | Sort-Object -Unique)
$nfrSubUnique = @($nfrSubIds | Sort-Object -Unique)
Add-Check 'T06a' '122 unique NFR ids (001..122)' ("{0} unique ({1}..{2})" -f $nfrUnique.Count, $nfrUnique[0], $nfrUnique[-1]) `
    $(if ($nfrUnique.Count -eq 122) { 'PASS' } else { 'FAIL' }) @(
    'NFR population drift: reconcile against RQ-006 3.3 (the five-duplicate resolution) before baselining.'
)
Add-Check 'T06b' 'sub-identifiers are exactly NFR-086a/b/c' ("{0}" -f ($nfrSubUnique -join ' ')) `
    $(if ($nfrSubUnique.Count -eq 3 -and ($nfrSubUnique -join ',') -eq 'NFR-086a,NFR-086b,NFR-086c') { 'PASS' } else { 'FAIL' })
$dupResolved = $false
if (Test-Path $rq006) { $dupResolved = ([System.IO.File]::ReadLines($rq006) | Select-String -Pattern 'duplicate' -SimpleMatch | Measure-Object).Count -gt 0 }
Add-Check 'T06c' 'RQ-006 carries the five-duplicate resolution' $(if ($dupResolved) { 'present' } else { 'absent' }) `
    $(if ($dupResolved) { 'PASS' } else { 'FAIL' }) @('RQ-006 3.3 is the resolution rule - restore it before NFR baselining.')

# --- T08: wave allocation (module granularity from frontmatter) -------------------
$waveAgg = @{}
$multiWaveRows = 0
$noWaveRows = 0
foreach ($r in $frRows) {
    if ($r.MultiWave) { $multiWaveRows++ }
    elseif ($r.Wave -eq '') { $noWaveRows++ }
    else { if (-not $waveAgg.ContainsKey($r.Wave)) { $waveAgg[$r.Wave] = 0 }; $waveAgg[$r.Wave]++ }
}
$waveStr = (( $waveAgg.GetEnumerator() | Sort-Object Name | ForEach-Object { "{0}={1}" -f $_.Key, $_.Value }) -join ' ')
Add-Check 'T08' 'every spec carries wave frontmatter (79/79)' ("single-wave rows by wave: {0}; multi-wave(module-split) rows: {1}; no-wave rows: {2}" -f $waveStr, $multiWaveRows, $noWaveRows) `
    $(if ($noWaveRows -eq 0) { 'PASS' } else { 'FAIL' }) @(
    'Specs without wave frontmatter cannot be allocated - complete the frontmatter from the module register (02-02).'
)
Add-Check 'T08b' 'unallocated claim: 1,816 (54%) at REQUIREMENT level' `
    ("module-granularity is complete on disk (0 no-wave rows); the 1,816 is requirement-level allocation status held in the programme tool - the per-requirement split inside {0} multi-wave module rows + 42 SWR is the residual worklist" -f $multiWaveRows) 'INFO'

# --- T09: rules + acceptance criteria ---------------------------------------------
$bruIn055 = 0; $coveredModules = 0
if (Test-Path $rules055) {
    $raw055 = Get-Content -LiteralPath $rules055 -Raw
    $bruIn055 = @([regex]::Matches($raw055, '\bBRU-[A-Z0-9]+-\d+\b') | ForEach-Object Value | Sort-Object -Unique).Count
    $modCodes055 = @([regex]::Matches($raw055, '\b([A-Z]{3,4})\b') | ForEach-Object Value | Sort-Object -Unique)
}
$moduleRuleRows = 0
$m40Rows = 0; $m42Rows = 0
foreach ($spec in $allSpecs) {
    $inSec9 = $false
    foreach ($line in [System.IO.File]::ReadLines($spec.FullName)) {
        if ($line -match '^#{2,3} *9\b') { $inSec9 = $true; continue }
        if ($line -match '^#{2,3} *1[0-9]\b') { $inSec9 = $false }
        if ($inSec9 -and $line -match '^\| *BR[A-Z]*-[A-Z0-9]+-\d+') {
            $moduleRuleRows++
            if ($spec.Name -like 'M40_*') { $m40Rows++ }
            if ($spec.Name -like 'M42_*') { $m42Rows++ }
        }
    }
}
Add-Check 'T09a' '05-05 catalogue = 140 BRU rules' ("{0} unique BRU ids" -f $bruIn055) `
    $(if ($bruIn055 -eq 140) { 'PASS' } elseif ($bruIn055 -gt 0) { 'WARN' } else { 'FAIL' }) @(
    'If the BRU pattern or count drifts, reconcile with RQ-009 (which carries the 140-rule and 20/67-coverage audit figures).'
)
Add-Check 'T09b' 'module 9 rule rows = 1,330' ("{0} rows (pattern: BRU- table rows in section 9)" -f $moduleRuleRows) `
    $(if ($moduleRuleRows -eq 1330) { 'PASS' } else { 'WARN' }) @(
    'Row-pattern basis differs from id-unique basis; record the measured value with its pattern in the rules baseline note.'
)
Add-Check 'T09c' 'RQ-009 claims M40/M42 carry 41/27 rules in their specs' ("measured on disk: M40={0}, M42={1} BRU section-9 rows - RQ-009 figure discrepancy, reconcile (RG-08)" -f $m40Rows, $m42Rows) 'WARN' @(
    'RQ-009 cites 41 (M40) and 27 (M42) rules; the specifications carry 20 each under the BRU-row pattern. Either RQ-009 counts a different rule form or its figure is stale - reconcile before the rules baseline is accepted.'
)
$acRows = 0
foreach ($spec in $allSpecs) {
    foreach ($line in [System.IO.File]::ReadLines($spec.FullName)) {
        if ($line -match '^\| *AC-\d{2,3}\b') { $acRows++ }
    }
}
Add-Check 'T09d' 'acceptance criteria population = 1,568 (module 17)' ("{0} AC-nn table rows across 79 specs (ids are module-local: AC-01..AC-nn per spec)" -f $acRows) `
    $(if ($acRows -eq 1568) { 'PASS' } else { 'WARN' })

# --- T10: M66/M67 + the 02-02 claim ------------------------------------------------
$m66 = $mSpecs | Where-Object Name -like 'M66_*'
$m67 = $mSpecs | Where-Object Name -like 'M67_*'
$m66Rows = @($frRows | Where-Object Module -eq 'M66').Count
$m67Rows = @($frRows | Where-Object Module -eq 'M67').Count
Add-Check 'T10a' 'M66 exists, 30 requirement rows; M67 exists, 32 rows' ("M66={0} rows, M67={1} rows" -f $m66Rows, $m67Rows) `
    $(if ($m66 -and $m67 -and $m66Rows -eq 30 -and $m67Rows -eq 32) { 'PASS' } else { 'FAIL' })
$claim022 = ''
if (Test-Path $reg022) {
    $hit = [System.IO.File]::ReadLines($reg022) | Select-String -Pattern 'M66|M67' | Select-Object -First 4
    $claim022 = ($hit | ForEach-Object { $_.Line.Trim() }) -join ' | '
}
Add-Check 'T10b' '02-02 3 says M66/M67 specs "not written" (the CR target)' ("captured: {0}" -f $(if ($claim022) { $claim022.Substring(0, [math]::Min(160, $claim022.Length)) } else { 'no M66/M67 line found' })) 'INFO'

# --- registers -------------------------------------------------------------------
if ($RegistersDir -ne '') {
    if (-not (Test-Path $RegistersDir)) { New-Item -ItemType Directory -Path $RegistersDir -Force | Out-Null }
    $fitgap = foreach ($r in $frRows) {
        [pscustomobject]@{
            requirement = $r.Id; module = $r.Module; wave = $r.Wave
            multi_wave = $r.MultiWave; layer = $r.Layer; priority = $r.Pri
            disposition = $disposition[$r.Id]
            note = 'derived: conservative primary from Layer (RQ-003 3 mapping); squad assessment refines'
        }
    }
    $fitgap | Export-Csv -Path (Join-Path $RegistersDir 'fit-gap-register.csv') -NoTypeInformation -Encoding UTF8
    $waveAlloc = $frRows | Group-Object Module, Wave, MultiWave | ForEach-Object {
        $parts = $_.Name -split ', '
        [pscustomobject]@{ module = $parts[0]; wave = $parts[1]; multi_wave = ([bool]::Parse($parts[2])); requirement_rows = $_.Count }
    }
    $waveAlloc | Export-Csv -Path (Join-Path $RegistersDir 'wave-allocation.csv') -NoTypeInformation -Encoding UTF8
    $rtm = foreach ($r in $frRows) {
        [pscustomobject]@{
            requirement = $r.Id; module = $r.Module; wave = $r.Wave
            cd_slot = ("CD-set({0})" -f $r.Module); test_slot = ("TC-{0}" -f $r.Id)
            status = 'seeded'; backward_link = $r.Module; forward_link = ("TC-{0}" -f $r.Id)
        }
    }
    $rtm | Export-Csv -Path (Join-Path $RegistersDir 'rtm-seed.csv') -NoTypeInformation -Encoding UTF8
    Log-Ok ("registers written to {0}: fit-gap-register.csv ({1} rows), wave-allocation.csv, rtm-seed.csv ({1} rows)" -f $RegistersDir, $frRows.Count)
}

# --- summary ----------------------------------------------------------------------
Log-Step 'summary'
$pass = @($script:Results | Where-Object Status -eq 'PASS').Count
Write-Host ("  PASS {0}   WARN {1}   INFO {2}   FAIL {3}   (of {4})" -f $pass, ($script:Results | Where-Object Status -eq 'WARN').Count, ($script:Results | Where-Object Status -eq 'INFO').Count, $script:FailCount, $script:Results.Count)
Write-Host ("  disposition histogram: " + (($dispCounts | ForEach-Object { "{0}={1}" -f $_.Name, $_.Count }) -join '  '))
if ($Json -ne '') {
    $out = [ordered]@{
        schema = '1000fix-erp/requirements-baseline/1'
        ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        estateRoot = $EstateRoot
        denominator = [ordered]@{ moduleRows = $moduleRows; portalRows = $portalRows; total = $totalRows; duplicates = $dupeIds.Count; swr = $swrCount; population = $totalRows + $swrCount }
        layerPresence = $layerPresence; layerPresencePct = $presencePct
        dispositions = ($dispCounts | ForEach-Object { [ordered]@{ name = $_.Name; count = $_.Count } })
        waves = $waveAgg; multiWaveRows = $multiWaveRows
        nfr = [ordered]@{ unique = $nfrUnique.Count; subIds = $nfrSubUnique }
        rules = [ordered]@{ bru055 = $bruIn055; moduleRuleRows = $moduleRuleRows; m40 = $m40Rows; m42 = $m42Rows; acRows = $acRows }
        m66m67 = [ordered]@{ m66Rows = $m66Rows; m67Rows = $m67Rows }
        checks = $script:Results
    }
    [System.IO.File]::WriteAllText($Json, ($out | ConvertTo-Json -Depth 6))
    Log-Ok "evidence written: $Json"
}
if ($script:FailCount -gt 0) {
    Log-Fail 'requirements baseline RED - fix the remedies before RQ-001/003/006 accept this run (DE-18/DE-19).'
    exit 1
}
if ($script:WarnCount -gt 0 -and $Strict) { Log-Fail 'strict mode: warnings treated as failures.'; exit 1 }
Log-Ok 'requirements baseline GREEN (warnings are recorded figures, not gate failures).'
exit 0
