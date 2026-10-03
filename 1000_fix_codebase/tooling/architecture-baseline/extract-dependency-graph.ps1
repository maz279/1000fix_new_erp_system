# =============================================================================
# 1000fix-erp - tooling/architecture-baseline/extract-dependency-graph.ps1
# P01-M04-T02 - regenerate the module dependency graph from the 67 module
# specifications' own declarations (AR-006 2.1 extraction method), never by
# copying AR-006's figures. MR-01: the graph is regenerated, never edited.
#
# Reproduces (claim -> measured):
#   nodes 67 (modules with module_id frontmatter)   edges 447 (DEP A->B)
#   18 mutual pairs                                 32 wave-order violations
#   in-degree top: M29:53  M33:41  M28:37
#   reciprocity failures 55, by module M33:22 M21:11 M24:8 M19:4 M27:3
#
# Analysis rules carried over from AR-006 3 (limitations):
#   * only the section-1 Module Identity rows are read (graph = lower bound)
#   * blanket phrase "All 66 other modules..." (M28/M29/M30/M65) is NOT
#     expanded into edges and those modules are excluded from reciprocity
#   * split-wave modules taken at their FIRST wave (conservative)
#
# Outputs: graph.txt (DEP edge list + REV declarations), evidence JSON,
#          reciprocity-worklist.csv, wave-violations.csv. DE-18/DE-19: remedy
#          printed, exit non-zero on FAIL.
# Exit codes: 0 green - 1 claim violations - 2 preconditions.
# Usage: powershell -ExecutionPolicy Bypass -File extract-dependency-graph.ps1
#            [-Json out.json] [-OutDir dir] [-EstateRoot path] [-Strict]
# =============================================================================
[CmdletBinding()]
param(
    [string]$Json = '',
    [string]$OutDir = '',
    [string]$EstateRoot = '',
    [switch]$Strict
)

$ErrorActionPreference = 'Continue'
$libPath = Join-Path $PSScriptRoot '..\workstation\lib\Common.psm1'
if (-not (Test-Path $libPath)) {
    Write-Host '[FAIL] workstation common library not found' -ForegroundColor Red
    exit 2
}
Import-Module $libPath -Force -DisableNameChecking
Initialize-WorkstationTooling | Out-Null
trap {
    $msg = "unexpected failure: $($_.Exception.Message)"
    try { Log-Fail $msg } catch { Write-Host ('[FAIL] ' + $msg) -ForegroundColor Red }
    try { Log-Remedy 'Fix the reported cause and re-run.' } catch { }
    exit 1
}
$repoRoot = (Get-RepoRoot).TrimEnd('\')
if ($EstateRoot -eq '') {
    if ($env:FIX_ESTATE_ROOT) { $EstateRoot = $env:FIX_ESTATE_ROOT }
    else { $EstateRoot = Split-Path -Parent $repoRoot }
}
$modulesDir = Join-Path $EstateRoot '1000fix_ERP_Module\03_Modules'
if (-not (Test-Path $modulesDir)) {
    Log-Fail "modules directory not found: $modulesDir"
    Log-Remedy 'Pass -EstateRoot <path to 1000fix_new_erp_system>.'
    exit 2
}

$script:Results = @()
$script:FailCount = 0
$script:WarnCount = 0
function Add-Check {
    param([string]$Id, [string]$Claim, [string]$Measured, [string]$Status, [string[]]$Remedies = @())
    $script:Results += [pscustomobject]@{
        Id = $Id; Claim = $Claim; Measured = $Measured; Status = $Status
        Remedies = $Remedies; CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
    }
    $line = ("{0,-7} claim [{1}]  measured [{2}]  {3}" -f $Id, $Claim, $Measured, $Status)
    switch ($Status) {
        'PASS' { Log-Ok $line }
        'WARN' { $script:WarnCount++; Log-Warn $line }
        'FAIL' { $script:FailCount++; Log-Fail $line }
        default { Log-Info $line }
    }
    foreach ($r in $Remedies) { Log-Remedy $r }
}

Log-Step 'P01-M04-T02 - dependency graph regeneration (AR-006 2.1 method, MR-01)'

# --- extract declarations (frontmatter + section-1 identity rows) ---------------
$mSpecs = @(Get-ChildItem $modulesDir -Filter 'M*.md' -File -Recurse)
$nodes = @{}          # id -> wave (first)
$dependsOn = @{}      # id -> @(ids)   from '| **Depends on** |'
$dependedBy = @{}     # id -> @(ids)   from '| **Depended on by** |'
$blanket = @()        # modules using the permitted blanket phrase
foreach ($spec in $mSpecs) {
    $id = ''; $wave = ''
    $head = Get-Content -LiteralPath $spec.FullName -TotalCount 40
    foreach ($h in $head) {
        if ($h -match '^module_id:\s*(\S+)') { $id = $Matches[1] }
        if ($h -match '^wave:\s*(.+)$') {
            $w = [regex]::Match($Matches[1], 'W\d+').Value
            if ($w) { $wave = $w }
        }
    }
    if (-not $id) { continue }
    $nodes[$id] = $wave
    $dependsOn[$id] = @()
    $dependedBy[$id] = @()
    foreach ($line in [System.IO.File]::ReadLines($spec.FullName)) {
        if ($line -match '^\| *\*{0,2}Depends on\*{0,2}\|?\s*\|') { }
        if ($line -match '^\| *\*\*Depends on\*\*') {
            if ($line -match 'All \d+ other modules') { $blanket += $id; continue }
            $dependsOn[$id] = @([regex]::Matches($line, '\bM\d{2}\b') | ForEach-Object { $_.Value } | Sort-Object -Unique)
        }
        if ($line -match '^\| *\*\*Depended on by\*\*') {
            # AR-006 3: the permitted blanket phrase (either row) marks the
            # module as excluded from reciprocity analysis as a TARGET - its
            # dependers are declared en masse, not enumerated.
            if ($line -match 'All \d+ other modules') { if ($blanket -notcontains $id) { $blanket += $id }; continue }
            $dependedBy[$id] = @([regex]::Matches($line, '\bM\d{2}\b') | ForEach-Object { $_.Value } | Sort-Object -Unique)
        }
    }
}
Add-Check 'N' 'nodes = 67 modules with module_id' ("{0} nodes; blanket-phrase modules: {1}" -f $nodes.Count, ($blanket -join ',')) `
    $(if ($nodes.Count -eq 67) { 'PASS' } else { 'FAIL' }) @(
    'Node-count drift: a module without module_id frontmatter is invisible to the graph - fix the spec header (MR-01).'
)

# --- edges: DEP A->B means A declares dependence on B ---------------------------
$edges = New-Object System.Collections.Generic.List[object]
foreach ($a in $dependsOn.Keys) {
    foreach ($b in $dependsOn[$a]) {
        if ($nodes.ContainsKey($b)) { $edges.Add([pscustomobject]@{ From = $a; To = $b }) }
    }
}
Add-Check 'E' 'edges = 447 declared DEP edges' ("{0} edges" -f $edges.Count) `
    $(if ($edges.Count -eq 447) { 'PASS' } else { 'WARN' }) @(
    'Edge-count drift vs AR-006: specifications changed since the AR-006 run - re-run the analysis, update AR-006 figures under change control, and re-check the 32-violation register against the new count.'
)

# --- in-degree (how many depend on X) -------------------------------------------
$inDeg = @{}
foreach ($e in $edges) { if (-not $inDeg.ContainsKey($e.To)) { $inDeg[$e.To] = 0 }; $inDeg[$e.To]++ }
$top = $inDeg.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 5
$topStr = ($top | ForEach-Object { "{0}:{1}" -f $_.Key, $_.Value }) -join ' '
Add-Check 'INDEG' 'top in-degree M29:53 M33:41 M28:37' ("top5: {0}" -f $topStr) `
    $(if ($inDeg['M29'] -eq 53 -and $inDeg['M33'] -eq 41 -and $inDeg['M28'] -eq 37) { 'PASS' } else { 'WARN' }) @(
    'In-degree drift changes the kernel argument - re-cost the affected module and re-check MV movements.'
)

# --- mutual pairs ----------------------------------------------------------------
$edgeSet = @{}
foreach ($e in $edges) { $edgeSet[("$($e.From)->$($e.To)")] = $true }
$mutual = New-Object System.Collections.Generic.List[string]
foreach ($e in $edges) {
    if ($edgeSet.ContainsKey("$($e.To)->$($e.From)") -and ($e.From -lt $e.To)) {
        $mutual.Add("$($e.From)<->$($e.To)")
    }
}
Add-Check 'MUT' 'mutual pairs = 18' ("{0} mutual: {1}" -f $mutual.Count, ($mutual -join ' ')) `
    $(if ($mutual.Count -eq 18) { 'PASS' } else { 'WARN' })

# --- wave-order violations: A->B with wave(B) > wave(A) ---------------------------
$viol = New-Object System.Collections.Generic.List[object]
foreach ($e in $edges) {
    $wa = $nodes[$e.From]; $wb = $nodes[$e.To]
    if ($wa -and $wb -and ([int]$wb.TrimStart('W')) -gt ([int]$wa.TrimStart('W'))) {
        $viol.Add([pscustomobject]@{ From = $e.From; WaveFrom = $wa; To = $e.To; WaveTo = $wb })
    }
}
Add-Check 'VIOL' 'wave-order violations = 32' ("{0} violations (prerequisite in a later wave)" -f $viol.Count) `
    $(if ($viol.Count -eq 32) { 'PASS' } else { 'WARN' }) @(
    'Violation-count drift: the disposition register (STUB/MOVE/NOT-A-PREREQ/ACCEPT) must be re-derived - see wave-violations.csv and P01-M04-T05.'
)

# --- reciprocity (RG-04): A declares dep on B but B does not list A ---------------
$recipFail = @{}
foreach ($a in $dependsOn.Keys) {
    if ($blanket -contains $a) { continue }
    foreach ($b in $dependsOn[$a]) {
        if (-not $nodes.ContainsKey($b)) { continue }
        if ($blanket -contains $b) { continue }
        if ($dependedBy[$b] -notcontains $a) {
            if (-not $recipFail.ContainsKey($b)) { $recipFail[$b] = 0 }
            $recipFail[$b]++
        }
    }
}
$recipTotal = ($recipFail.Values | Measure-Object -Sum).Sum
if ($null -eq $recipTotal) { $recipTotal = 0 }
$recipStr = (( $recipFail.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 6 | ForEach-Object { "{0}:{1}" -f $_.Key, $_.Value }) -join ' ')
Add-Check 'RECIP' 'reciprocity failures = 55; by module M33:22 M21:11 M24:8 M19:4 M27:3' `
    ("total {0}; top: {1}" -f $recipTotal, $recipStr) `
    $(if ($recipTotal -eq 55) { 'PASS' } else { 'WARN' }) @(
    'R-03: reciprocity must become a CI check (P01-M04-T06) or 67 files edited by many authors drift again within a wave.'
)

# --- outputs -----------------------------------------------------------------------
$outGraph = New-Object System.Collections.Generic.List[string]
$outGraph.Add('# regenerated dependency graph - P01-M04-T02 - ' + (Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'))
$outGraph.Add('# MR-01: the graph is regenerated, never edited.')
foreach ($n in ($nodes.Keys | Sort-Object)) { $outGraph.Add("NODE $n $($nodes[$n])") }
foreach ($e in ($edges | Sort-Object From, To)) { $outGraph.Add("DEP $($e.From) $($e.To)") }
foreach ($m in $mutual) { $outGraph.Add("MUTUAL $m") }
if ($OutDir -ne '') {
    if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
    [System.IO.File]::WriteAllLines((Join-Path $OutDir 'graph.txt'), $outGraph)
    $recipFail.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object {
        [pscustomobject]@{ module = $_.Key; missing_reverse_declarations = $_.Value }
    } | Export-Csv (Join-Path $OutDir 'reciprocity-worklist.csv') -NoTypeInformation -Encoding UTF8
    $viol | ForEach-Object {
        # Mechanical disposition classes (P01-M04-T05): MV-matched rows are
        # MOVE (the accepted scope movements resolve them); rows inside a
        # designed interface break are BREAK-DESIGNED (the AR-003 record is
        # the fix); the remainder are ASSIGN-SA at G0a with expiry - every
        # row carries owner + expiry so GV-005 registration is mechanical.
        $mvTargets = @{ M21 = 'MV-01'; M24 = 'MV-02'; M51 = 'MV-03'; M64 = 'MV-04'; M17 = 'MV-05' }
        $breakPairs = @{ 'M20' = @('M50','M51'); 'M51' = @('M52','M65'); 'M50' = @('M52'); 'M16' = @('M42','M52'); 'M12' = @('M53'); 'M41' = @('M44'); 'M49' = @('M54'); 'M21' = @('M29') }
        $disp = 'ASSIGN-SA'; $why = 'no mechanical class - SA dispositions per AR-006 5'
        if ($mvTargets.ContainsKey($_.To)) { $disp = "MOVE ($($mvTargets[$_.To]))"; $why = 'prerequisite moved to an earlier wave by CR-P01M04-01' }
        elseif ($breakPairs.ContainsKey($_.From) -and $breakPairs[$_.From] -contains $_.To) { $disp = 'BREAK-DESIGNED'; $why = 'pair has an AR-003 interface-break record (architecture-baseline.md)' }
        [pscustomobject]@{
            from = $_.From; from_wave = $_.WaveFrom; prerequisite = $_.To; prereq_wave = $_.WaveTo
            gap = "W$([int]$_.WaveTo.TrimStart('W') - [int]$_.WaveFrom.TrimStart('W'))"
            disposition = $disp; basis = $why; owner = 'SA'; expiry = 'G0a'
        }
    } | Export-Csv (Join-Path $OutDir 'wave-violations.csv') -NoTypeInformation -Encoding UTF8
    Log-Ok "outputs written to $OutDir : graph.txt ($($edges.Count) DEP edges), reciprocity-worklist.csv, wave-violations.csv ($($viol.Count) rows)"
}

Log-Step 'summary'
$pass = @($script:Results | Where-Object Status -eq 'PASS').Count
Write-Host ("  PASS {0}   WARN {1}   INFO {2}   FAIL {3}   (of {4})" -f $pass, ($script:Results | Where-Object Status -eq 'WARN').Count, ($script:Results | Where-Object Status -eq 'INFO').Count, $script:FailCount, $script:Results.Count)
if ($Json -ne '') {
    $out = [ordered]@{
        schema = '1000fix-erp/dependency-graph/1'
        ranAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        nodes = $nodes.Count; edges = $edges.Count
        mutualPairs = $mutual; mutualCount = $mutual.Count
        violations = $viol; violationCount = $viol.Count
        inDegreeTop = ($inDeg.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 10 | ForEach-Object { [ordered]@{ module = $_.Key; indegree = $_.Value } })
        reciprocityFailures = $recipFail; reciprocityTotal = $recipTotal
        blanketModules = $blanket
        checks = $script:Results
    }
    [System.IO.File]::WriteAllText($Json, ($out | ConvertTo-Json -Depth 6))
    Log-Ok "evidence written: $Json"
}
if ($script:FailCount -gt 0) { Log-Fail 'dependency graph RED - fix remedies before AR-006 acceptance (DE-18/DE-19).'; exit 1 }
if ($script:WarnCount -gt 0 -and $Strict) { Log-Fail 'strict mode.'; exit 1 }
Log-Ok 'dependency graph regenerated GREEN (warnings are recorded drift, not extraction failures).'
exit 0
