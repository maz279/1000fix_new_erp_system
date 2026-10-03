# =============================================================================
# 1000fix-erp - tooling/workstation/setup-workstation.ps1
# P02-M01 (Windows adaptation, decision D-WS-001) - automated workstation
# baseline: OS floor check, pinned package install (winget), patched
# wkhtmltopdf, Bengali fonts, Docker Desktop.
#
# Task coverage:
#   T02  Windows 10 22H2+ / 11 floor check (replaces Ubuntu 22.04/24.04)
#   T04  system package set via winget, versions pinned in versions.lock
#   T05  Bengali font set (Noto Sans Bengali pinned + Nirmala UI built-in)
#   T06  Docker Desktop (Engine >= 24 + Compose v2 bundled)
#   T07  Git for Windows (>= 2.40 floor, pinned)
#   T08  patched wkhtmltopdf host build (delegates to install-wkhtmltopdf.ps1)
#   T09  Chrome (primary) + Firefox (second engine), pinned
#   T03  BitLocker is a PROVISIONING control, not an install step: the script
#        verifies-and-instructs (enabling BitLocker on the OS volume is a
#        one-time admin/TPM action with reboot implications - never silent).
#        T10 (reserved ports clean) is checked at the end and by verify.
#
# Idempotent: every step checks current state before acting.
# Usage (elevated PowerShell recommended):
#   powershell -ExecutionPolicy Bypass -File setup-workstation.ps1 `
#              [-DryRun] [-SkipWinget] [-SkipFonts] [-SkipWkhtmltopdf] [-AllowUserContext]
#
# Exit codes: 0 ok - 1 failure - 2 preconditions
# =============================================================================
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$SkipWinget,
    [switch]$SkipFonts,
    [switch]$SkipWkhtmltopdf,
    [switch]$AllowUserContext
)

$ErrorActionPreference = 'Stop'
# DE-18 failure discipline: an unexpected terminating error must still print
# FAIL + remedy (not a bare stack trace) and exit non-zero (DE-19). The
# fallback Write-Host keeps the trap usable even when the failure IS the
# module load (Log-* would not exist yet).
trap {
    $msg = "unexpected failure: $($_.Exception.Message)"
    try {
        Log-Fail $msg
        Log-Remedy 'Fix the reported cause and re-run - every step is idempotent.'
    } catch {
        Write-Host ('[FAIL] ' + $msg) -ForegroundColor Red
        Write-Host ('      remedy: fix the reported cause and re-run - every step is idempotent.') -ForegroundColor Yellow
    }
    exit 1
}
Import-Module (Join-Path $PSScriptRoot 'lib\Common.psm1') -Force -DisableNameChecking
Initialize-WorkstationTooling | Out-Null
if ($DryRun) { Set-DryRun -Enabled $true }

$lock = Load-VersionLock
Write-Host ''
Write-Host '1000fix-erp - P02-M01 workstation baseline (native Windows, D-WS-001)' -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# T02 - OS floor (never silently proceed below the supported build)
# ---------------------------------------------------------------------------
Log-Step 'P02-M01-T02 - operating system floor check'
$platform = Get-PlatformInfo
$minBuild = [int]$lock.WORKSTATION_WINDOWS_MIN_BUILD
Log-Info "Running: $($platform.ProductName) build $($platform.OsBuild) ($($platform.DisplayVersion)) - floor is build $minBuild"
if ($platform.IsServer) {
    Log-Warn 'Windows Server detected: Docker Desktop and winget behaviour on Server is unsupported by this baseline.'
    Log-Remedy 'Use a Windows 10 22H2+ / Windows 11 client workstation (D-WS-001).'
    exit 2
}
if ($platform.OsBuild -lt $minBuild) {
    Log-Fail "OS build $($platform.OsBuild) is below the supported floor ($minBuild = Windows 10 22H2)."
    Log-Remedy 'Upgrade Windows before continuing - Docker Desktop 4.x requires Windows 10 64-bit 22H2 or newer.'
    exit 2
}
if (-not $platform.Is64Bit) {
    Log-Fail 'A 64-bit OS is required (the pinned wkhtmltox build is x64).'
    exit 2
}
Log-Ok 'OS floor satisfied (T02).'

# ---------------------------------------------------------------------------
# Elevation (machine-wide winget installs + Program Files need it)
# ---------------------------------------------------------------------------
if (-not $platform.IsElevated -and -not $AllowUserContext -and -not $DryRun) {
    Log-Fail 'This script is not elevated: Git / Docker Desktop / Python / wkhtmltopdf install machine-wide.'
    Log-Remedy "Re-run from an elevated PowerShell window, or pass -AllowUserContext to attempt user-scope installs (winget may still refuse)."
    exit 2
}

# ---------------------------------------------------------------------------
# T03 - full-disk encryption: verify-and-instruct (BitLocker, DE-12/SC-009)
# ---------------------------------------------------------------------------
Log-Step 'P02-M01-T03 - full-disk encryption (BitLocker) status'
$bitlockerStatus = 'unknown'
if ($platform.IsElevated -or $DryRun) {
    Invoke-RunStep 'Querying BitLocker status of the OS volume (manage-bde)' {
        $out = manage-bde -status C: 2>$null
        $script:_BdeOut = $out
    }
    if (-not (Get-DryRun)) {
        $prot = ($script:_BdeOut | Where-Object { $_ -match 'Protection Status' }) -join ''
        if ($prot -match 'Protection On')   { $bitlockerStatus = 'on' }
        elseif ($prot -match 'Protection Off') { $bitlockerStatus = 'off' }
    }
} else {
    Log-Warn 'Cannot query BitLocker from a non-elevated shell.'
}
switch ($bitlockerStatus) {
    'on'      { Log-Ok 'BitLocker protection is ON on the OS volume (T03 satisfied - DE-12).' }
    'off'     {
        Log-Fail 'BitLocker protection is OFF on the OS volume.'
        Log-Remedy 'Run:  manage-bde -on C:  (or Settings > Privacy & security > Device encryption), then reboot. DE-12/SC-009 make an unencrypted workstation non-negotiable.'
    }
    default   {
        Log-Warn 'BitLocker status could not be determined from this shell.'
        Log-Remedy 'Run verify-workstation.ps1 from an elevated shell to confirm (check T03).'
    }
}

# ---------------------------------------------------------------------------
# T04/T06/T07/T09 - pinned winget package set
# ---------------------------------------------------------------------------
if (-not $SkipWinget) {
    Log-Step 'P02-M01-T04/T06/T07/T09 - pinned package set via winget'

    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Log-Fail "'winget' is not available on PATH."
        Log-Remedy 'Install "App Installer" from the Microsoft Store (or update Windows), then re-run.'
        exit 2
    }

    $expected = @{
        $lock.WORKSTATION_WINGET_GIT_ID     = $lock.WORKSTATION_WINGET_GIT_VERSION
        $lock.WORKSTATION_WINGET_DOCKER_ID  = $lock.WORKSTATION_WINGET_DOCKER_VERSION
        $lock.WORKSTATION_WINGET_PYTHON_ID  = $lock.WORKSTATION_WINGET_PYTHON_VERSION
        $lock.WORKSTATION_WINGET_CHROME_ID  = $lock.WORKSTATION_WINGET_CHROME_VERSION
        $lock.WORKSTATION_WINGET_FIREFOX_ID = $lock.WORKSTATION_WINGET_FIREFOX_VERSION
    }

    foreach ($pkg in Get-WingetPackageList) {
        $pinned = $expected[$pkg.Id]
        if (-not $pinned) {
            Log-Warn "$($pkg.Id) is listed in packages.winget but has no pin in versions.lock - skipping (IR-07)."
            continue
        }
        # Idempotency probe: take the last line naming the package, split the
        # winget columns (2+ spaces), read the column AFTER the Id column.
        # Read-only, so it runs in -DryRun too - the dry-run plan must reflect
        # what would ACTUALLY change, not list already-installed packages.
        $installed = $null
        $line = winget list --id $pkg.Id --exact --accept-source-agreements 2>$null |
                Select-String -SimpleMatch $pkg.Id | Select-Object -Last 1
        if ($line) {
            $cols = ("$line" -split '\s{2,}' | Where-Object { $_ -ne '' })
            $idIdx = [array]::IndexOf($cols, $pkg.Id)
            if ($idIdx -ge 0 -and ($idIdx + 1) -lt $cols.Count) {
                $installed = $cols[$idIdx + 1]
            }
        }
        if (-not $installed) { $installed = Get-InstalledAppVersion -WingetId $pkg.Id }
        if ($installed -and ($pkg.Id -eq $lock.WORKSTATION_WINGET_DOCKER_ID)) {
            # Binary probe yields the ENGINE version, not the Desktop version;
            # presence is the idempotency fact, floors are enforced by T06.
            Log-Info "Docker present (engine $installed; floors enforced at verify T06) - no-op."
            continue
        }
        if ($installed -and (Test-VersionGe $installed $pinned)) {
            Log-Ok "$($pkg.Id) already installed at $installed (pin $pinned)"
            continue
        }
        Invoke-RunStep "Installing $($pkg.Id) at pinned version $pinned" {
            winget install --id $pkg.Id --version $pinned --exact --silent `
                --accept-package-agreements --accept-source-agreements
            # 0x8A15002B (-1978335189) = "another/this version already installed"
            if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne -1978335189) {
                throw "winget install failed for $($pkg.Id) (exit $LASTEXITCODE)"
            }
        }
    }

    # Docker post-install: engine + compose probe with honest remedy
    if (-not (Get-DryRun)) {
        Log-Info 'Docker post-install probe (first launch + licence acceptance are interactive by design):'
        if (Get-Command docker -ErrorAction SilentlyContinue) {
            $dv = docker --version 2>$null
            $cv = docker compose version 2>$null
            if ("$dv" -ne '') { Log-Ok "docker: $dv" } else {
                Log-Warn 'docker CLI present but engine not reachable.'
                Log-Remedy 'Launch Docker Desktop once, accept the licence, wait for "Engine running", then re-run verify-workstation.ps1.'
            }
            if ("$cv" -match 'v2\.') { Log-Ok "compose: $cv" }
        } else {
            Log-Warn 'docker CLI not on PATH yet (a new shell is usually needed after install).'
            Log-Remedy 'Open a NEW PowerShell window, launch Docker Desktop once, accept the licence, then run verify-workstation.ps1.'
        }
    }
}

# ---------------------------------------------------------------------------
# T08 - patched wkhtmltopdf (host build; container half ships in the image)
# ---------------------------------------------------------------------------
if (-not $SkipWkhtmltopdf) {
    Log-Step 'P02-M01-T08 - patched-Qt wkhtmltopdf (host build)'
    $installer = Join-Path $PSScriptRoot 'install-wkhtmltopdf.ps1'
    # A non-elevated setup run (only possible with -AllowUserContext) must not
    # attempt a machine-scope NSIS install it cannot complete - pass -UserScope.
    $installerArgs = @('-NoProfile','-ExecutionPolicy','Bypass','-File', $installer)
    if (-not $platform.IsElevated) { $installerArgs += '-UserScope' }
    Invoke-RunStep "Running $installer $(if (-not $platform.IsElevated) {'-UserScope'})" {
        & powershell @installerArgs
        if ($LASTEXITCODE -ne 0) { throw "install-wkhtmltopdf.ps1 exited $LASTEXITCODE" }
    }
}

# ---------------------------------------------------------------------------
# T05 - Bengali fonts (TR-07): Noto Sans Bengali pinned + Nirmala UI built-in
# ---------------------------------------------------------------------------
if (-not $SkipFonts) {
    Log-Step 'P02-M01-T05 - Bengali font set (TR-07)'

    $fontFamilies = Get-InstalledFontFamilies
    if (Test-FontFamilyInstalled -Family $lock.WORKSTATION_FONT_NOTO_BENGALI_FAMILY -InstalledFamilies $fontFamilies) {
        Log-Ok "$($lock.WORKSTATION_FONT_NOTO_BENGALI_FAMILY) already installed."
    } else {
        $zipUrl = $lock.WORKSTATION_FONT_NOTO_BENGALI_URL
        $zipSha = $lock.WORKSTATION_FONT_NOTO_BENGALI_SHA256
        $tempZip = Join-Path ([System.IO.Path]::GetTempPath()) 'NotoSansBengali.zip'
        $tempExtract = Join-Path ([System.IO.Path]::GetTempPath()) ('NotoSansBengali.' + [guid]::NewGuid().ToString('N').Substring(0,8))

        Invoke-RunStep "Downloading $zipUrl" {
            try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch { }
            Invoke-WebRequest -Uri $zipUrl -OutFile $tempZip -UseBasicParsing
        }
        if (-not (Get-DryRun)) {
            $actualSha = (Get-FileHash -Path $tempZip -Algorithm SHA256).Hash.ToLower()
            if ($actualSha -ne $zipSha.ToLower()) {
                Log-Fail "SHA256 mismatch for the Noto Sans Bengali archive (expected $zipSha, got $actualSha)."
                Log-Remedy 'Do NOT install. Re-download; if the mismatch persists, update the pin in tooling/versions.lock via a reviewed change.'
                exit 1
            }
            Log-Ok "SHA256 verified: $actualSha"
        }
        Invoke-RunStep 'Expanding archive' {
            Expand-Archive -Path $tempZip -DestinationPath $tempExtract -Force
        }
        if (-not (Get-DryRun)) {
            $result = Install-UserFontsFromDirectory -SourceDir $tempExtract
            Log-Ok ("Noto Sans Bengali: {0} installed, {1} already present (per-user, no reboot needed)." -f $result.Installed, $result.Skipped)
            Remove-Item $tempZip, $tempExtract -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    if (Test-FontFamilyInstalled -Family $lock.WORKSTATION_FONT_WINDOWS_BENGALI_FAMILY -InstalledFamilies $fontFamilies) {
        Log-Ok "$($lock.WORKSTATION_FONT_WINDOWS_BENGALI_FAMILY) (Windows built-in, second Bengali family) present."
    } else {
        Log-Warn "$($lock.WORKSTATION_FONT_WINDOWS_BENGALI_FAMILY) not found in the font registry."
        Log-Remedy 'Nirmala UI ships with Windows 10/11 as part of the base image. If absent, the OS image is damaged: run  sfc /scannow  (elevated), then verify in Settings > Personalization > Fonts.'
    }
}

# ---------------------------------------------------------------------------
# T10 - reserved ports (report-only here; verify fails the build)
# ---------------------------------------------------------------------------
Log-Step 'P02-M01-T10 - reserved-port hygiene (5432/6379/9000)'
$ports = $lock.WORKSTATION_RESERVED_PORTS.Split(',') | ForEach-Object { [int]$_.Trim() }
$listeners = Get-ReservedPortListeners -Ports $ports
if ($listeners.Count -eq 0) {
    Log-Ok 'No listener on any reserved port - host hygiene clean (DE-01).'
} else {
    foreach ($l in $listeners) {
        if ($l.IsDocker) {
            Log-Warn "port $($l.Port) held by $($l.ProcessName) (Docker backend - stop the stack before baseline verification)."
        } else {
            Log-Fail "port $($l.Port) held by $($l.ProcessName) (pid $($l.OwningProcess))."
            Log-Remedy 'Stop/uninstall the host service - only containers may own 5432/6379/9000 (DE-01).'
        }
    }
}

Write-Host ''
Log-Ok 'setup-workstation.ps1 finished. Next: run verify-workstation.ps1 (elevated) - every check must be green (DE-19).'
exit 0
