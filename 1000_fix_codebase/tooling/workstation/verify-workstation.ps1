# =============================================================================
# 1000fix-erp - tooling/workstation/verify-workstation.ps1
# P02-M01 (Windows adaptation, decision D-WS-001) - executable verification of
# the workstation baseline, all ten tasks of the milestone.
#
# Every check prints PASS / WARN / FAIL and, on failure, the REMEDY (DE-18:
# "exits non-zero on any failure and prints the remedy, not only the
# symptom"). Exit code is non-zero when any check FAILs (DE-19: a developer
# does not begin work until the baseline is green).
#
#   check  task    pass condition (Windows adaptation of the roadmap 'Verify')
#   ------|-------|--------------------------------------------------------------
#    T01   T01     hardware >= MINIMUM baseline (4c/16GB/256GB SSD);
#                   RECOMMENDED (8c/16t/32GB/NVMe/1440p|dual) reported
#    T02   T02     Windows 10 22H2+ / Windows 11 client (native Windows is
#                   supported UNDER D-WS-001, which supersedes BE-001-D-06).
#                   Windows 10-range builds additionally WARN: 22H2 passed
#                   end of support in Oct 2025 - plan migration to Windows 11
#    T03   T03     BitLocker protection ON for the OS volume (LUKS analogue)
#    T04   T04     every package in packages.winget installed at >= its pin
#    T05   T05     Bengali fonts render-capable: Noto Sans Bengali +
#                   Nirmala UI registered (TR-07; conjunct reference-image
#                   comparison itself is make-doctor check 10, P02-M10-T04)
#    T06   T06     docker >= 24 floor AND 'docker compose version' v2.x AND
#                   the engine is REACHABLE ('docker info' exits 0 - catches
#                   "installed but Docker Desktop never launched"); user in
#                   the docker-users group (Windows analogue of the docker
#                   group; WARN when definitively absent)
#    T07   T07     git >= 2.40
#    T08   T08     'wkhtmltopdf --version' reports 'with patched qt'
#                   (host 0.12.5-1; container 0.12.6.1-3 ships in the image)
#    T09   T09     Chrome/Chromium AND Firefox both present
#    T10   T10     no listener on 5432/6379/9000 (DE-01 port hygiene)
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File verify-workstation.ps1
#              [-Json out.json] [-Strict] [-Deep] [-SelfTest]
#
# Exit codes: 0 all green (warnings allowed unless -Strict) - 1 failures -
#             2 preconditions/self-test failure
# =============================================================================
[CmdletBinding()]
param(
    [string]$Json = '',
    [switch]$Strict,     # warnings also fail the run
    [switch]$Deep,       # adds slow checks (Bengali PDF render probe)
    [switch]$SelfTest    # validates the tool's own logic; no system access
)

$ErrorActionPreference = 'Continue'
Import-Module (Join-Path $PSScriptRoot 'lib\Common.psm1') -Force -DisableNameChecking
Initialize-WorkstationTooling | Out-Null

# ---------------------------------------------------------------------------
# Check harness
# ---------------------------------------------------------------------------
$script:Results = @()
$script:FailCount = 0
$script:WarnCount = 0

function Complete-Check {
    param([string]$Id, [string]$Name, [ValidateSet('PASS','WARN','FAIL','SKIP')][string]$Status,
          [string]$Detail, [string[]]$Remedies = @())
    $script:Results += [pscustomobject]@{
        Check = $Id; Name = $Name; Status = $Status; Detail = $Detail; Remedies = $Remedies
    }
    switch ($Status) {
        'PASS' { Log-Ok   ("{0} {1} - {2}" -f $Id, $Name, $Detail) }
        'WARN' { $script:WarnCount++
                 Log-Warn ("{0} {1} - {2}" -f $Id, $Name, $Detail) }
        'FAIL' { $script:FailCount++
                 Log-Fail ("{0} {1} - {2}" -f $Id, $Name, $Detail) }
        'SKIP' { Log-Info ("{0} {1} - skipped: {2}" -f $Id, $Name, $Detail) }
    }
    foreach ($r in $Remedies) { Log-Remedy $r }
}

function Invoke-ToolVersion {
    param([string]$Name, [string[]]$Argument = @('--version'))
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) { return $null }
    try {
        $out = & $cmd.Source @Argument 2>$null | Select-Object -First 1
        return "$out".Trim()
    } catch { return $null }
}

# ---------------------------------------------------------------------------
# -SelfTest: validate the tool's own logic without touching the system
# ---------------------------------------------------------------------------
if ($SelfTest) {
    Log-Step 'self-test - validating tool logic (no system access)'
    $fail = 0

    $cases = @(
        @{ L = '2.55.0.5'; R = '2.40';  Want = $true  },
        @{ L = '2.43.1';   R = '2.40';  Want = $true  },
        @{ L = '2.34.1';   R = '2.40';  Want = $false },
        @{ L = '24.0.9, build 123'; R = '24'; Want = $true },
        @{ L = 'v2.43';    R = '2.40';  Want = $true  },
        @{ L = 'Docker version 29.8.1, build abc'; R = '24'; Want = $true }
    )
    foreach ($c in $cases) {
        $got = Test-VersionGe $c.L $c.R
        if ($got -ne $c.Want) { Log-Fail ("Test-VersionGe('{0}','{1}') = {2}, want {3}" -f $c.L, $c.R, $got, $c.Want); $fail++ }
    }

    $lockPath = Get-VersionLockPath
    if (-not (Test-Path $lockPath)) { Log-Fail 'versions.lock not found'; $fail++ } else {
        $n = (Get-Content $lockPath | Where-Object { $_ -match '^[A-Z0-9_]+=' }).Count
        if ($n -lt 25) { Log-Fail "versions.lock looks truncated ($n pins)"; $fail++ } else { Log-Ok "versions.lock parses with $n pins" }
        # DE-06: ":latest" must appear in no PIN (comment prose is allowed).
        if (Get-Content $lockPath | Where-Object { $_ -match '^[A-Z0-9_]+=' } | Select-String -SimpleMatch ':latest') {
            Log-Fail '":latest" found in a pin of versions.lock (DE-06 violation)'; $fail++
        }
    }

    $pkgs = Get-WingetPackageList
    if ($pkgs.Count -lt 5) { Log-Fail "packages.winget parse yielded $($pkgs.Count) packages (want >= 5)"; $fail++ }
    else { Log-Ok ("packages.winget parses with {0} packages" -f $pkgs.Count) }

    # The verifier checks ITSELF too - the file most likely to be edited must
    # not be the one file the purity check skips.
    foreach ($p in @('setup-workstation.ps1','verify-workstation.ps1','install-wkhtmltopdf.ps1','machine-inventory.ps1','lib\Common.psm1')) {
        $full = Join-Path $PSScriptRoot $p
        if (Test-Path $full) { Log-Ok "sibling script present: $p" }
        else { Log-Fail "sibling script missing: $p"; $fail++ }
        # ASCII purity: PS 5.1 parses BOM-less files as ANSI; any non-ASCII
        # byte in a .ps1/.psm1 is a latent parse-corruption bug.
        $bad = (Get-Content $full -ErrorAction SilentlyContinue | Where-Object { $_ -match '[^\x00-\x7F]' })
        if ($bad) { Log-Fail "$p contains non-ASCII characters (PS 5.1 ANSI-parse hazard)"; $fail++ }
    }

    if ($fail -eq 0) { Log-Ok 'SELF-TEST GREEN'; exit 0 } else { Log-Fail "SELF-TEST RED ($fail)"; exit 2 }
}

# ---------------------------------------------------------------------------
# Real verification begins
# ---------------------------------------------------------------------------
$lock = Load-VersionLock
$platform = Get-PlatformInfo
Write-Host ''
Write-Host '1000fix-erp - P02-M01 workstation verification (native Windows, D-WS-001)' -ForegroundColor Cyan
if (-not $platform.IsElevated) {
    Log-Warn 'Not elevated: T03 (BitLocker) will be indeterminate. Re-run elevated for a definitive pass.'
}

# --- T01 hardware --------------------------------------------------------------
Log-Step 'T01 - hardware baseline'
$h = Get-HardwareSummary
$t01 = Get-HardwareClassification -Hardware $h
$hwDetail = ("{0}c/{1}t, {2} GB RAM, {3} GB {4} disk ({5}), {6} display(s)" -f `
    $h.CpuCores, $h.CpuThreads, $h.RamTotalGB, $h.SystemDiskSizeGB, $h.SystemDiskBus, $h.SystemDiskMedia, @($h.Displays).Count)
if ($t01.Recommended) {
    Complete-Check 'T01' 'Hardware baseline' 'PASS' ("meets RECOMMENDED - $hwDetail")
} elseif ($t01.Minimum) {
    Complete-Check 'T01' 'Hardware baseline' 'WARN' ("meets MINIMUM only (core profile; 'full' profile + Odoo + IDE exceeds 16 GB) - $hwDetail") @(
        'T01 is an inventory + classification check: below-minimum is the failing case; minimum-only is a supported-but-core-profile configuration (BE-001 SS3.1).'
    )
} else {
    Complete-Check 'T01' 'Hardware baseline' 'FAIL' ("below MINIMUM - $hwDetail") @(
        'Use a machine with at least 4 cores / 16 GB RAM / 256 GB SSD (the core-profile minimum).'
    )
}

# --- T02 operating system ------------------------------------------------------
Log-Step 'T02 - operating system (native Windows per D-WS-001)'
$minBuild = [int]$lock.WORKSTATION_WINDOWS_MIN_BUILD
if ($platform.IsServer) {
    Complete-Check 'T02' 'Operating system' 'FAIL' "Windows Server (build $($platform.OsBuild)) is not a supported developer workstation." @(
        'Use a Windows 10 22H2+ / Windows 11 client machine (D-WS-001).'
    )
} elseif ($platform.OsBuild -lt $minBuild) {
    Complete-Check 'T02' 'Operating system' 'FAIL' "build $($platform.OsBuild) is below the floor ($minBuild)." @(
        'Upgrade to Windows 10 22H2 or newer; Docker Desktop 4.x requires it.'
    )
} elseif ($platform.OsBuild -lt 22000) {
    # Client builds below 22000 are Windows 10. The floor itself is met, but
    # Windows 10 22H2 passed end of support in October 2025 - on a baseline
    # whose encryption controls cite DE-12/SC-009, running past-EOS client
    # OSes is a standing security exposure worth a WARN, not silence.
    Complete-Check 'T02' 'Operating system' 'WARN' ("{0} build {1} ({2}) meets the floor, but Windows 10 is past end of support (Oct 2025) without ESU." -f `
        $platform.ProductName, $platform.OsBuild, $platform.DisplayVersion) @(
        'Plan migration to Windows 11 (ESU, where purchased, only defers the exposure). Native Windows is the sanctioned baseline under D-WS-001.'
    )
} else {
    Complete-Check 'T02' 'Operating system' 'PASS' ("{0} build {1} ({2}) - native Windows is the sanctioned baseline under D-WS-001" -f `
        $platform.ProductName, $platform.OsBuild, $platform.DisplayVersion)
}

# --- T03 full-disk encryption (BitLocker) ---------------------------------------
Log-Step 'T03 - full-disk encryption (BitLocker; LUKS analogue)'
$encryption = 'unknown'
$protLine = ''
try {
    $bde = manage-bde -status "$env:SystemDrive" 2>$null
    $protLine = ($bde | Where-Object { $_ -match 'Protection Status' }) -join ''
} catch { }
if ($protLine -match 'Protection On')      { $encryption = 'on' }
elseif ($protLine -match 'Protection Off') { $encryption = 'off' }
if ($encryption -eq 'on') {
    Complete-Check 'T03' 'Full-disk encryption' 'PASS' 'BitLocker protection is ON for the OS volume (DE-12 / SC-009 satisfied).'
} elseif ($encryption -eq 'off') {
    Complete-Check 'T03' 'Full-disk encryption' 'FAIL' 'BitLocker protection is OFF for the OS volume.' @(
        'Run (elevated):  manage-bde -on C:   then reboot. DE-12/SC-009 make an unencrypted workstation non-negotiable.'
    )
} else {
    Complete-Check 'T03' 'Full-disk encryption' 'WARN' 'status indeterminate from this shell (manage-bde needs elevation).' @(
        'Re-run this script from an elevated PowerShell window to get a definitive T03 verdict.'
    )
}

# --- T04 pinned package set ------------------------------------------------------
Log-Step 'T04 - system package set at pinned versions'
$pinById = @{
    $lock.WORKSTATION_WINGET_GIT_ID     = $lock.WORKSTATION_WINGET_GIT_VERSION
    $lock.WORKSTATION_WINGET_DOCKER_ID  = $lock.WORKSTATION_WINGET_DOCKER_VERSION
    $lock.WORKSTATION_WINGET_PYTHON_ID  = $lock.WORKSTATION_WINGET_PYTHON_VERSION
    $lock.WORKSTATION_WINGET_CHROME_ID  = $lock.WORKSTATION_WINGET_CHROME_VERSION
    $lock.WORKSTATION_WINGET_FIREFOX_ID = $lock.WORKSTATION_WINGET_FIREFOX_VERSION
}
$t04Missing = @()
$t04Stale = @()
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Complete-Check 'T04' 'Package set' 'FAIL' "'winget' is not on PATH." @(
        'Install "App Installer" from the Microsoft Store, then re-run setup-workstation.ps1.'
    )
} else {
    foreach ($pkg in Get-WingetPackageList) {
        $pinned = $pinById[$pkg.Id]
        if (-not $pinned) { continue }   # notes-only rows
        $installed = $null
        # Probe 1: winget list (column output - truncates on narrow consoles).
        $line = winget list --id $pkg.Id --exact --accept-source-agreements 2>$null |
                Select-String -SimpleMatch $pkg.Id | Select-Object -Last 1
        if ($line) {
            $cols = ("$line" -split '\s{2,}' | Where-Object { $_ -ne '' })
            $idIdx = [array]::IndexOf($cols, $pkg.Id)
            if ($idIdx -ge 0 -and ($idIdx + 1) -lt $cols.Count) { $installed = $cols[$idIdx + 1] }
        }
        # Probe 2: deterministic binary probe (engine/cli/exe VersionInfo).
        if (-not $installed) { $installed = Get-InstalledAppVersion -WingetId $pkg.Id }
        if (-not $installed) {
            $t04Missing += "$($pkg.Id)@$pinned"
        } elseif ($pkg.Id -eq $lock.WORKSTATION_WINGET_DOCKER_ID) {
            # The binary probe yields the ENGINE version, not the Desktop
            # version - presence is what T04 asserts here; the engine >= 24 +
            # Compose v2+ floors are enforced by check T06.
            Log-Info "Docker present (engine $installed; Desktop pin $($pinned) - floors enforced at T06)."
        } elseif (-not (Test-VersionGe $installed $pinned)) {
            $t04Stale += "$($pkg.Id) (have $installed, pin $pinned)"
        }
    }
    if ($t04Missing.Count -eq 0 -and $t04Stale.Count -eq 0) {
        Complete-Check 'T04' 'Package set' 'PASS' 'every pinned package installed at (or above) its pin.'
    } else {
        $bits = @()
        if ($t04Missing.Count) { $bits += ('missing: ' + ($t04Missing -join ', ')) }
        if ($t04Stale.Count)   { $bits += ('below pin: ' + ($t04Stale -join ', ')) }
        Complete-Check 'T04' 'Package set' 'FAIL' ($bits -join '; ') @(
            'Run:  powershell -ExecutionPolicy Bypass -File tooling\workstation\setup-workstation.ps1  (elevated).'
        )
    }
}

# --- T05 Bengali fonts -------------------------------------------------------------
Log-Step 'T05 - Bengali font set (TR-07)'
$fonts = Get-InstalledFontFamilies
$notoOk    = Test-FontFamilyInstalled -Family $lock.WORKSTATION_FONT_NOTO_BENGALI_FAMILY -InstalledFamilies $fonts
$nirmalaOk = Test-FontFamilyInstalled -Family $lock.WORKSTATION_FONT_WINDOWS_BENGALI_FAMILY -InstalledFamilies $fonts
if ($notoOk -and $nirmalaOk) {
    Complete-Check 'T05' 'Bengali fonts' 'PASS' ("{0} + {1} registered (two conjunct-capable families)." -f `
        $lock.WORKSTATION_FONT_NOTO_BENGALI_FAMILY, $lock.WORKSTATION_FONT_WINDOWS_BENGALI_FAMILY)
} else {
    $missing = @()
    if (-not $notoOk)    { $missing += $lock.WORKSTATION_FONT_NOTO_BENGALI_FAMILY }
    if (-not $nirmalaOk) { $missing += $lock.WORKSTATION_FONT_WINDOWS_BENGALI_FAMILY }
    Complete-Check 'T05' 'Bengali fonts' 'FAIL' ('missing: ' + ($missing -join ', ') + ' - a machine that cannot render Bengali will not see a shaping defect that reaches a Mushak 6.3 invoice (TR-07).') @(
        'Run:  powershell -ExecutionPolicy Bypass -File tooling\workstation\setup-workstation.ps1 -SkipWinget -SkipWkhtmltopdf  (installs the pinned Noto Sans Bengali family per-user).'
    )
}
if ($Deep) {
    Log-Info 'Deep probe: rendering a Bengali HTML->PDF sample (if wkhtmltopdf is present)...'
    $wkDeep = Invoke-ToolVersion 'wkhtmltopdf'
    if ($wkDeep) {
        $sampleHtml = Join-Path $env:TEMP 'fix-bengali-probe.html'
        $samplePdf  = $sampleHtml -replace '\.html$','.pdf'
        # Bengali sample built from code points so THIS FILE stays pure ASCII:
        # Windows PowerShell 5.1 reads BOM-less files as ANSI, and a literal
        # Bengali string would corrupt the parser. Text is the word "Bangla"
        # followed by the label "juktakshar" (conjunct letters) and five
        # conjuncts: k+ssa, t+ra, j+nya, n+da, r+ka.
        $bnText = -join (@(
            0x09AC,0x09BE,0x0982,0x09B2,0x09BE,0x0020,
            0x09AF,0x09C1,0x0995,0x09CD,0x09A4,0x09BE,
            0x0995,0x09CD,0x09B7,0x09B0,0x003A,0x0020,
            0x0995,0x09CD,0x09B7,0x0020,
            0x09A4,0x09CD,0x09B0,0x0020,
            0x099C,0x09CD,0x099E,0x0020,
            0x09A8,0x09CD,0x09A6,0x0020,
            0x09B0,0x09CD,0x0995
        ) | ForEach-Object { [char]$_ })
        $html = '<html><head><meta charset="utf-8"></head><body><p>' + $bnText + '</p></body></html>'
        Set-Content -Path $sampleHtml -Value $html -Encoding UTF8
        $probeKept = $false
        try {
            $wkCmd = Get-Command wkhtmltopdf
            & $wkCmd.Source --quiet --encoding utf-8 $sampleHtml $samplePdf 2>$null
            if ((Test-Path $samplePdf) -and ((Get-Item $samplePdf).Length -gt 5KB)) {
                $probeKept = $true   # kept on disk for visual inspection
                Log-Ok "deep probe: Bengali PDF rendered ($((Get-Item $samplePdf).Length) bytes) - inspect $samplePdf visually (reference-image comparison arrives with make-doctor check 10)."
            } else {
                Log-Warn 'deep probe: PDF missing or suspiciously small - check fonts + wkhtmltopdf.'
            }
        } catch { Log-Warn "deep probe failed: $($_.Exception.Message)" }
        if (-not $probeKept) {
            # Leave no probe artefacts behind in %TEMP% on a failed render.
            Remove-Item $sampleHtml, $samplePdf -Force -ErrorAction SilentlyContinue
        } else {
            Remove-Item $sampleHtml -Force -ErrorAction SilentlyContinue
        }
    } else {
        Log-Warn 'deep probe skipped: wkhtmltopdf not present.'
    }
}

# --- T06 Docker Engine + Compose v2 ------------------------------------------------
Log-Step 'T06 - Docker Engine (>= 24) + Compose v2 + engine reachable'
$dockerVer = Invoke-ToolVersion 'docker'
$composeVer = Invoke-ToolVersion 'docker' @('compose','version')
if (-not $dockerVer) {
    Complete-Check 'T06' 'Docker Engine' 'FAIL' "'docker' not found on PATH." @(
        'Install pinned Docker Desktop:  winget install --id Docker.DockerDesktop --version ' + $lock.WORKSTATION_WINGET_DOCKER_VERSION + ' --exact --silent'
        'Then launch Docker Desktop once, accept the licence, and open a NEW shell.'
    )
} else {
    $engineOk = Test-VersionGe (Get-FirstVersionToken ($dockerVer -replace '^Docker version\s*','')) $lock.WORKSTATION_DOCKER_ENGINE_MIN_VERSION
    # Compose floor is "v2 or later" (v1 was the legacy Python compose).
    $composeMajor = 0
    if ($composeVer -match 'v(\d+)\.') { $composeMajor = [int]$Matches[1] }
    elseif ($composeVer -match 'version\s+(\d+)\.') { $composeMajor = [int]$Matches[1] }
    $composeOk = $composeMajor -ge [int]$lock.WORKSTATION_DOCKER_COMPOSE_MIN_MAJOR
    if (-not ($engineOk -and $composeOk)) {
        Complete-Check 'T06' 'Docker Engine' 'FAIL' ("$dockerVer; compose: $composeVer") @(
            "Engine must be >= $($lock.WORKSTATION_DOCKER_ENGINE_MIN_VERSION) and Compose must be v$($lock.WORKSTATION_DOCKER_COMPOSE_MIN_MAJOR)+ - reinstall at the pinned version via setup-workstation.ps1."
        )
    } else {
        # Floors met. The roadmap's literal verify text is satisfied, but a
        # machine whose engine has never been STARTED (Docker Desktop not
        # launched / licence not accepted) still cannot run containers - probe it.
        $t06Status = 'PASS'
        $t06Notes = @()
        $t06Remedies = @()
        $engineReachable = $false
        try {
            & docker info --format '{{.ServerVersion}}' 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { $engineReachable = $true }
        } catch { }
        if (-not $engineReachable) {
            $t06Status = 'WARN'
            $t06Notes += 'engine NOT reachable (Docker Desktop not running or licence not accepted)'
            $t06Remedies += 'Launch Docker Desktop, accept the licence, wait for "Engine running", then re-run verify.'
        } else {
            $t06Notes += 'engine reachable'
        }
        # Roadmap T06 "add the user to the docker group" -> Windows analogue:
        # membership of the local 'docker-users' group. $null = indeterminate
        # (group absent on this backend) - engine reachability above already
        # proves functional access, so indeterminate is informational only.
        $inGroup = Test-UserInDockerUsersGroup
        if ($inGroup -eq $false) {
            if ($t06Status -ne 'FAIL') { $t06Status = 'WARN' }
            $t06Notes += 'current user NOT in the docker-users group'
            $t06Remedies += 'Run (elevated):  net localgroup docker-users "%USERNAME%" /add  - then sign out and back in.'
        } elseif ($inGroup -eq $null) {
            Log-Info "docker-users group not present on this machine (backend-dependent) - engine reachability is the functional proof."
        } else {
            $t06Notes += 'user in docker-users group'
        }
        Complete-Check 'T06' 'Docker Engine' $t06Status ("$dockerVer; $composeVer; " + ($t06Notes -join '; ')) $t06Remedies
    }
}

# --- T07 git >= 2.40 ------------------------------------------------------------------
Log-Step 'T07 - git >= 2.40'
$gitVer = Invoke-ToolVersion 'git'
if (-not $gitVer) {
    Complete-Check 'T07' 'git' 'FAIL' "'git' not found on PATH." @(
        'Run setup-workstation.ps1 (installs Git.Git at the pinned version), then open a NEW shell.'
    )
} elseif (Test-VersionGe ($gitVer -replace '^git version\s*','') $lock.WORKSTATION_GIT_MIN_VERSION) {
    Complete-Check 'T07' 'git' 'PASS' $gitVer
} else {
    Complete-Check 'T07' 'git' 'FAIL' "$gitVer (< $($lock.WORKSTATION_GIT_MIN_VERSION) - BE-004 needs subtrees + partial-clone support)" @(
        'Run setup-workstation.ps1 to raise Git to the pinned version.'
    )
}

# --- T08 patched wkhtmltopdf ------------------------------------------------------------
Log-Step 'T08 - patched-Qt wkhtmltopdf'
$marker = $lock.WORKSTATION_WKHTMLTOPDF_PATCHED_MARKER
# Resolution order: live PATH, then the canonical install locations (a shell
# spawned before the User PATH update cannot see it - the registry is truth).
$wkExe = $null; $wkSource = ''
$cmd = Get-Command wkhtmltopdf -ErrorAction SilentlyContinue
if ($cmd) { $wkExe = $cmd.Source; $wkSource = 'PATH' }
if (-not $wkExe) {
    foreach ($canon in @((Join-Path $env:LOCALAPPDATA 'Programs\wkhtmltopdf\bin\wkhtmltopdf.exe'),
                         'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')) {
        if (Test-Path $canon) { $wkExe = $canon; $wkSource = 'canonical'; break }
    }
}
$wkPathRegistered = $false
try {
    $userPathReg = [Environment]::GetEnvironmentVariable('Path', 'User')
    $machPathReg = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    if (("$userPathReg$machPathReg") -like '*wkhtmltopdf\bin*') { $wkPathRegistered = $true }
} catch { }
if (-not $wkExe) {
    Complete-Check 'T08' 'wkhtmltopdf' 'FAIL' "'wkhtmltopdf' not found on PATH or at the canonical install locations." @(
        'Run:  powershell -ExecutionPolicy Bypass -File tooling\workstation\install-wkhtmltopdf.ps1 -UserScope   (or without -UserScope from an elevated shell).',
        'The distribution/unpatched build renders Odoo reports blank or unstyled (BE-001 SS9.2); never winget-install a generic build.'
    )
} else {
    $wkVer = & $wkExe --version 2>$null | Select-Object -First 1
    if ("$wkVer" -match [regex]::Escape($marker)) {
        if ($wkSource -eq 'PATH' -or $wkPathRegistered) {
            Complete-Check 'T08' 'wkhtmltopdf' 'PASS' ("$wkVer (resolved via $wkSource; PATH registry wired)")
        } else {
            Complete-Check 'T08' 'wkhtmltopdf' 'FAIL' "$wkVer found at $wkExe but no PATH (User or Machine registry) points at it." @(
                'Re-run install-wkhtmltopdf.ps1 to repair the PATH entry.'
            )
        }
    } else {
        Complete-Check 'T08' 'wkhtmltopdf' 'FAIL' "$("$wkVer" -replace '^\s*','') at $wkExe - unpatched build." @(
            'Run:  powershell -ExecutionPolicy Bypass -File tooling\workstation\install-wkhtmltopdf.ps1  - it replaces the unpatched binary with the pinned patched build.'
        )
    }
}

# --- T09 two browsers -----------------------------------------------------------------------
Log-Step 'T09 - Chrome (primary) + Firefox (second engine)'
function Test-AppPath {
    param([string]$Exe)  # e.g. 'chrome.exe'
    foreach ($root in @("HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
                        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths")) {
        $k = Join-Path $root $Exe
        if (Test-Path $k) {
            $v = (Get-ItemProperty $k).'(default)'
            if ($v -and (Test-Path $v)) { return $v }
        }
    }
    return $null
}
$chrome = Test-AppPath 'chrome.exe'
if (-not $chrome) { $chrome = Test-AppPath 'chromium.exe' }
$firefox = Test-AppPath 'firefox.exe'
if ($chrome -and $firefox) {
    Complete-Check 'T09' 'Browsers' 'PASS' ("chrome: $chrome ; firefox: $firefox")
} else {
    $missing = @()
    if (-not $chrome)  { $missing += 'Chrome/Chromium' }
    if (-not $firefox) { $missing += 'Firefox' }
    Complete-Check 'T09' 'Browsers' 'FAIL' ('missing: ' + ($missing -join ', ') + ' - portal work is verified in two engines; Bengali conjunct shaping differs between them (UX-005/QA-008).') @(
        'Run setup-workstation.ps1 (installs both browsers at pinned versions).'
    )
}

# --- T10 reserved ports -------------------------------------------------------------------------
Log-Step 'T10 - reserved ports clean (5432/6379/9000)'
$ports = $lock.WORKSTATION_RESERVED_PORTS.Split(',') | ForEach-Object { [int]$_.Trim() }
$listeners = Get-ReservedPortListeners -Ports $ports
if ($listeners.Count -eq 0) {
    Complete-Check 'T10' 'Reserved ports' 'PASS' 'no listener on any reserved port (DE-01 host hygiene).'
} else {
    $dockerOnly = @($listeners | Where-Object { $_.IsDocker }).Count -eq $listeners.Count
    $detail = ($listeners | ForEach-Object { ":$($_.Port)=$($_.ProcessName)" }) -join ' '
    if ($dockerOnly) {
        # Container-origin listeners (docker backend / wslrelay) are managed by
        # Docker, not host-installed services - DE-01's violation class is the
        # HOST service. A publishing container (any project's stack) is a
        # port-collision RISK for the 1000fix-erp local stack -> WARN.
        Complete-Check 'T10' 'Reserved ports' 'WARN' "Docker-managed listeners hold $detail" @(
            'Identify the publishing container:  docker ps --filter publish=5432  - then stop that stack, or remap it. When the 1000fix-erp stack binds 127.0.0.1:5432 the collision will refuse the bind.'
        )
    } else {
        Complete-Check 'T10' 'Reserved ports' 'FAIL' "host services are holding $detail" @(
            'Stop or uninstall the host PostgreSQL / Redis / object-store service - those run as containers only (DE-01).'
        )
    }
}

# ---------------------------------------------------------------------------
# Summary + exit
# ---------------------------------------------------------------------------
Write-Host ''
Log-Step 'summary'
$pass = @($script:Results | Where-Object Status -eq 'PASS').Count
Write-Host ("  PASS {0}   WARN {1}   FAIL {2}" -f $pass, $script:WarnCount, $script:FailCount)
if ($Json -ne '') {
    $jsonDir = Split-Path -Parent $Json
    if ($jsonDir -and -not (Test-Path $jsonDir)) { New-Item -ItemType Directory -Force -Path $jsonDir | Out-Null }
    [System.IO.File]::WriteAllText($Json, ($script:Results | ConvertTo-Json -Depth 5))
    Log-Ok "results JSON written: $Json"
}

if ($script:FailCount -gt 0) {
    Log-Fail 'workstation baseline is RED - fix the remedies above before starting work (DE-19).'
    exit 1
}
if ($script:WarnCount -gt 0 -and $Strict) {
    Log-Fail 'strict mode: warnings treated as failures.'
    exit 1
}
if ($script:WarnCount -gt 0) {
    Log-Warn 'baseline GREEN with warnings (re-run elevated / with -Strict before recording T03).'
} else {
    Log-Ok 'workstation baseline GREEN - P02-M01 verified.'
}
exit 0
