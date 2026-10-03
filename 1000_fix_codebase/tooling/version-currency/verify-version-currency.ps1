# =============================================================================
# 1000fix-erp - tooling/version-currency/verify-version-currency.ps1
# P01-M02-T10 - the version-currency re-verification ritual, executable.
#
# "Re-verify every stack component against upstream, never against the last
# document that verified it" (alignment audit R-04). The standing list is
# tooling/version-currency/components.json (all L4 systems incl. the
# D-028/D-030 replacements, L1-L3 classes, app-platform runtimes, L6 set).
#
# Checks, per component (components.json "check" object):
#   endoflife  -> GET https://endoflife.date/api/{product}.json ; the named
#                 cycle's eol date. FAIL if past; WARN if within -WarnDays.
#   github     -> GET https://api.github.com/repos/{repo} (archived flag:
#                 FAIL - the MinIO failure mode) + releases/latest (recorded
#                 as information; a pin BELOW latest is deliberate, DE-06).
#   manual     -> facts carried from a dated human verification; WARN when the
#                 lastVerified date is older than -ManualStaleDays.
#   watchList  -> repositories that must STAY archived (regression checks).
#
# DE-18: every failure prints the remedy. DE-19: exit non-zero on any FAIL.
# Exit codes: 0 green (warnings allowed) - 1 failures - 2 preconditions.
# Usage:
#   powershell -ExecutionPolicy Bypass -File verify-version-currency.ps1
#              [-Json out.json] [-Offline] [-Strict] [-WarnDays 365]
#              [-ManualStaleDays 90]
# =============================================================================
[CmdletBinding()]
param(
    [string]$Json = '',
    [switch]$Offline,
    [switch]$Strict,
    [int]$WarnDays = 365,
    [int]$ManualStaleDays = 90
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
    try { Log-Remedy 'Fix the reported cause and re-run.' } catch { }
    exit 1
}

# TLS 1.2 for Windows PowerShell 5.1 (github/endoflife need it)
try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch { }

$manifestPath = Join-Path $PSScriptRoot 'components.json'
if (-not (Test-Path $manifestPath)) {
    Log-Fail "components.json not found at $manifestPath"
    Log-Remedy 'Restore the standing list - without it the ritual verifies nothing (P01-M02-T10).'
    exit 2
}
try { $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json }
catch {
    Log-Fail "components.json failed to parse: $($_.Exception.Message)"
    Log-Remedy 'Fix the JSON - the manifest is the single input of the ritual.'
    exit 2
}
if (-not $manifest.components -or $manifest.components.Count -lt 20) {
    Log-Fail ("manifest carries only {0} components - the standing list is all L4 + L1-L3 + L6 (expect ~40)" -f @($manifest.components).Count)
    exit 2
}

$script:Results = @()
$script:FailCount = 0
$script:WarnCount = 0
function Add-Result {
    param([string]$Id, [string]$Name, [string]$Status, [string]$Detail, [string[]]$Remedies = @())
    $script:Results += [pscustomobject]@{
        Id = $Id; Name = $Name; Status = $Status; Detail = $Detail
        Remedies = $Remedies; CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
    }
    switch ($Status) {
        'OK'          { Log-Ok   ("{0,-12} {1,-34} {2}" -f $Id, $Name, $Detail) }
        'WARN'        { $script:WarnCount++; Log-Warn ("{0,-12} {1,-34} {2}" -f $Id, $Name, $Detail) }
        'FAIL'        { $script:FailCount++; Log-Fail ("{0,-12} {1,-34} {2}" -f $Id, $Name, $Detail) }
        default       { Log-Info ("{0,-12} {1,-34} {2}" -f $Id, $Name, $Detail) }
    }
    foreach ($r in $Remedies) { Log-Remedy $r }
}

# --- one HTTP GET helper, tolerant of offline sandboxes ----------------------
function Invoke-GetJson {
    param([string]$Uri, [int]$TimeoutSec = 20)
    try {
        $resp = Invoke-RestMethod -Uri $Uri -TimeoutSec $TimeoutSec -Headers @{ 'User-Agent' = '1000fix-erp-version-currency/1' } -ErrorAction Stop
        return @{ Ok = $true; Data = $resp }
    } catch {
        return @{ Ok = $false; Error = $_.Exception.Message }
    }
}

Log-Step "P01-M02-T10 - version-currency verification ($(if ($Offline) {'OFFLINE - manifest + manual facts only'} else {'against upstream'}))"
$today = (Get-Date).Date

# --- watch list first: repos that must STAY archived -------------------------
if ($Offline) {
    Log-Info 'offline run: the archived-repo watch guard was NOT checked (it needs the network).'
}
if (-not $Offline) {
    foreach ($w in @($manifest.watchList)) {
        $r = Invoke-GetJson -Uri ("https://api.github.com/repos/{0}" -f $w.repo)
        if ($r.Ok) {
            if ($r.Data.archived) { Add-Result ('watch-' + $w.repo) $w.repo 'OK' 'still archived upstream (as the register expects)' }
            else {
                Add-Result ('watch-' + $w.repo) $w.repo 'FAIL' ('repo is ACTIVE again upstream - the D-028/D-030 replacement rationale must be re-examined') @(
                    ('Re-open {0} against the current register row before any image pin changes.' -f $w.reason)
                )
            }
        } else {
            Add-Result ('watch-' + $w.repo) $w.repo 'WARN' ("probe unreachable ($($r.Error))") @('Re-run online - the watch check is the ritual''s regression guard.')
        }
    }
}

# --- components ---------------------------------------------------------------
foreach ($c in @($manifest.components)) {
    $check = $c.check
    if ($check.type -eq 'manual') {
        $age = $null
        try { $age = ($today - [datetime]$check.lastVerified).Days } catch { }
        if ($age -eq $null) {
            Add-Result $c.id $c.name 'WARN' 'manual fact has no parseable lastVerified date' @('Re-verify and re-date the manual fact (RG-08: figures carry the timestamp that made them true).')
        } elseif ($age -gt $ManualStaleDays) {
            Add-Result $c.id $c.name 'WARN' ("manual verification is $($age) days old (>$ManualStaleDays)") @('Re-verify against upstream and update components.json lastVerified.')
        } else {
            Add-Result $c.id $c.name 'OK' ("manual fact verified $($age) day(s) ago: $($c.notes)")
        }
        continue
    }
    if ($Offline) {
        Add-Result $c.id $c.name 'WARN' 'offline run - upstream not checked' @('Re-run online before recording a gate result (DE-19).')
        continue
    }

    if ($check.type -eq 'endoflife') {
        $r = Invoke-GetJson -Uri ("https://endoflife.date/api/{0}.json" -f $check.product)
        if (-not $r.Ok) {
            Add-Result $c.id $c.name 'WARN' ("endoflife.date unreachable for '$($check.product)' ($($r.Error))") @('Re-run online; if the product is not tracked, move the fact to manualFacts with a dated source.')
            continue
        }
        $cycle = @($r.Data) | Where-Object { $_.cycle -eq $check.cycle } | Select-Object -First 1
        if (-not $cycle) {
            Add-Result $c.id $c.name 'WARN' ("cycle '$($check.cycle)' not found for product '$($check.product)' (cycles: " + ((@($r.Data) | Select-Object -First 5 | ForEach-Object { $_.cycle }) -join ', ') + ')') @('Update the manifest cycle or move the component to manualFacts.')
            continue
        }
        # endoflife.date encodes "no EOL announced yet" as the boolean false
        # (e.g. the current nextjs cycle), not a date - handle both shapes.
        $eol = $null
        $eolLiteral = "{0}" -f $cycle.eol
        if ($eolLiteral -match '^(False|True)$') {
            if ($eolLiteral -eq 'False') {
                Add-Result $c.id $c.name 'OK' ("cycle $($check.cycle): no EOL announced upstream yet (endoflife.date reports eol=false)")
            } else {
                Add-Result $c.id $c.name 'WARN' ("cycle $($check.cycle) reports eol=true with no date - upstream data anomaly") @('Check endoflife.date/{0} manually and correct the manifest.' -f $check.product)
            }
            continue
        }
        try { $eol = [datetime]$cycle.eol } catch { }
        if ($eol -eq $null) {
            Add-Result $c.id $c.name 'WARN' ("EOL date unparseable for cycle '$($check.cycle)': '$($cycle.eol)'") @('Correct the manifest or move to manualFacts.')
        } elseif ($eol.Date -lt $today) {
            Add-Result $c.id $c.name 'FAIL' ("baseline cycle $($check.cycle) EOL since $($cycle.eol)") @('Re-baseline the component via an ADR + D-nnn (GV-003); update versions.lock and components.json together.')
        } elseif ($eol.Date -le $today.AddDays($WarnDays)) {
            Add-Result $c.id $c.name 'WARN' ("baseline cycle $($check.cycle) EOL $($cycle.eol) - within $WarnDays days") @('Schedule the re-baseline at the next gate; name the decision that owns it (see the decision column).')
        } else {
            Add-Result $c.id $c.name 'OK' ("cycle $($check.cycle) EOL $($cycle.eol) - $($eol.Subtract($today).Days) days of margin")
        }
        continue
    }

    if ($check.type -eq 'github') {
        $r = Invoke-GetJson -Uri ("https://api.github.com/repos/{0}" -f $check.repo)
        if (-not $r.Ok) {
            Add-Result $c.id $c.name 'WARN' ("github unreachable for $($check.repo) ($($r.Error))") @('Re-run online (GitHub rate limits reset hourly).')
            continue
        }
        if ($r.Data.archived) {
            Add-Result $c.id $c.name 'FAIL' ("upstream repo $($check.repo) is ARCHIVED") @('The MinIO failure mode (IRB-01): select a replacement via an ADR (D-028 pattern), then update versions.lock, components.json and the D-030 register together.')
            continue
        }
        # Quota discipline: the releases/latest call doubles the GitHub API
        # budget (unauthenticated = 60 req/h) and is informational only - it
        # runs solely for components whose manifest sets "latest": true.
        $latestNote = ''
        if ($check.latest -eq $true) {
            $rel = Invoke-GetJson -Uri ("https://api.github.com/repos/{0}/releases/latest" -f $check.repo)
            if ($rel.Ok -and $rel.Data.tag_name) { $latestNote = " ; latest upstream release: $($rel.Data.tag_name) (pinning below latest is deliberate, DE-06)" }
        }
        Add-Result $c.id $c.name 'OK' ("repo active$latestNote")
        continue
    }

    Add-Result $c.id $c.name 'WARN' ("unknown check type '$($check.type)'") @('Fix components.json - supported: endoflife | github | manual.')
}

# --- summary -------------------------------------------------------------------
Log-Step 'summary'
$ok = @($script:Results | Where-Object Status -eq 'OK').Count
Write-Host ("  OK {0}   WARN {1}   FAIL {2}   (of {3})" -f $ok, $script:WarnCount, $script:FailCount, $script:Results.Count)
if ($Json -ne '') {
    $out = [ordered]@{
        schema    = '1000fix-erp/version-currency-record/1'
        ranAtUtc  = (Get-Date).ToUniversalTime().ToString('o')
        mode      = $(if ($Offline) { 'offline' } else { 'online' })
        warnDays  = $WarnDays
        ok = $ok; warnings = $script:WarnCount; failures = $script:FailCount
        results   = $script:Results
    }
    [System.IO.File]::WriteAllText($Json, ($out | ConvertTo-Json -Depth 6))
    Log-Ok "verification record written: $Json"
}
if ($script:FailCount -gt 0) {
    Log-Fail 'version currency RED - fix the remedies before the gate accepts this record (DE-18/DE-19).'
    exit 1
}
if ($script:WarnCount -gt 0 -and $Strict) { Log-Fail 'strict mode: warnings treated as failures.'; exit 1 }
if ($script:WarnCount -gt 0) { Log-Warn 'version currency GREEN with warnings - re-run online / update manual facts before recording a gate result.' }
else { Log-Ok 'version currency GREEN.' }
exit 0
