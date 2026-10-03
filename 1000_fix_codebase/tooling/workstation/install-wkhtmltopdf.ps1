# =============================================================================
# 1000fix-erp - tooling/workstation/install-wkhtmltopdf.ps1
# P02-M01-T08 (Windows adaptation) - install the PATCHED wkhtmltopdf build
# on the host, not an arbitrary/unpatched one.
#
# D-WS-001 split-build ruling:
#   * The PRIMARY renderer for Odoo QWeb reports is the patched-Qt
#     0.12.6.1-3 Linux build baked into the Odoo container image (Odoo runs
#     containerised on Windows).
#   * The HOST build is the last Windows binary upstream ever shipped:
#     wkhtmltox 0.12.5-1 (msvc2015, win64) - a PATCHED build used for local
#     QWeb->PDF checks outside the container. There is no Windows 0.12.6.x
#     and no winget package; the URL + SHA256 are pinned in versions.lock.
#
# Behaviour:
#   * version + SHA256 come ONLY from tooling/versions.lock (IR-07)
#   * the downloaded artefact is hash-verified BEFORE install - a mismatch
#     aborts without touching the system (fail closed)
#   * idempotent: an already-installed matching patched build is a no-op
#   * silent NSIS install (/S); adds the install dir to the machine PATH
#
# Usage (elevated recommended for Program Files + machine PATH):
#   powershell -ExecutionPolicy Bypass -File install-wkhtmltopdf.ps1 [-DryRun] [-Force]
#
# Exit codes: 0 ok - 1 verification/install failure - 2 preconditions
# =============================================================================
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$UserScope   # install to %LOCALAPPDATA%\Programs\wkhtmltopdf with a
                         # USER Path entry - no elevation needed. Default remains
                         # machine scope (Program Files + machine Path).
)

$ErrorActionPreference = 'Stop'
# DE-18 failure discipline: unexpected terminating errors still print
# FAIL + remedy (not a bare stack trace) and exit non-zero. The fallback
# Write-Host keeps the trap usable even when the failure IS the module load.
trap {
    $msg = "unexpected failure: $($_.Exception.Message)"
    try {
        Log-Fail $msg
        Log-Remedy 'Fix the reported cause and re-run - the installer is idempotent.'
    } catch {
        Write-Host ('[FAIL] ' + $msg) -ForegroundColor Red
        Write-Host ('      remedy: fix the reported cause and re-run - the installer is idempotent.') -ForegroundColor Yellow
    }
    exit 1
}
$libPath = Join-Path $PSScriptRoot 'lib\Common.psm1'
Import-Module $libPath -Force -DisableNameChecking
Initialize-WorkstationTooling | Out-Null
if ($DryRun) { Set-DryRun -Enabled $true }

$lock = Load-VersionLock

# --- preconditions -----------------------------------------------------------
$platform = Get-PlatformInfo
if (-not $platform.Is64Bit) {
    Log-Fail 'The pinned wkhtmltox Windows build is x64-only; this OS is not 64-bit.'
    exit 2
}
if (-not $platform.IsElevated -and -not $UserScope -and -not $DryRun) {
    # Hard precondition, not a warning: an unattended machine-scope NSIS install
    # from a non-elevated shell cannot succeed - fail fast with the remedy.
    Log-Fail 'Not elevated and no -UserScope: the machine-scope install (Program Files + machine PATH) cannot proceed.'
    Log-Remedy 'Re-run from an elevated PowerShell window, or pass -UserScope to install per-user without admin.'
    exit 2
}

# PS 5.1 needs TLS 1.2 opted-in for GitHub downloads.
try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch { }

$targetVersion = $lock.WORKSTATION_WKHTMLTOPDF_HOST_VERSION
$downloadUrl   = $lock.WORKSTATION_WKHTMLTOPDF_HOST_URL
$expectedSha   = $lock.WORKSTATION_WKHTMLTOPDF_HOST_SHA256
$marker        = $lock.WORKSTATION_WKHTMLTOPDF_PATCHED_MARKER

# --- fast path: already patched at the pinned version ------------------------
$existing = Get-Command wkhtmltopdf -ErrorAction SilentlyContinue
if (-not $existing) {
    foreach ($fallback in @((Join-Path $env:LOCALAPPDATA 'Programs\wkhtmltopdf\bin\wkhtmltopdf.exe'),
                            'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                            'C:\Program Files\wkhtmltopdf\wkhtmltopdf.exe')) {
        if (Test-Path $fallback) { $existing = Get-Item $fallback; break }
    }
}
if ($existing -and -not $Force) {
    # $existing is CommandInfo (.Source) or FileInfo (.FullName).
    $existingExe = if ($existing.PSObject.Properties['Source']) { $existing.Source } else { $existing.FullName }
    $verOut = & $existingExe --version 2>$null | Select-Object -First 1
    if ("$verOut" -match [regex]::Escape($marker)) {
        Log-Ok "wkhtmltopdf already patched: $verOut"
        # Binary prints the base version ("0.12.5"); the pin carries the
        # packaging tag ("0.12.5-1"). Accept a base-version match.
        $base = $targetVersion -replace '-\d+$',''
        if ("$verOut" -match [regex]::Escape($base) -or "$verOut" -match [regex]::Escape($targetVersion)) {
            Log-Ok "Nothing to do (already at pinned host version $targetVersion)."
            exit 0
        }
        Log-Warn "Patched but not at pinned version $targetVersion - continuing install."
    } elseif ("$verOut" -ne '') {
        Log-Warn "Existing build is NOT patched: $verOut"
        Log-Remedy 'This script replaces it with the pinned patched build; continuing.'
    }
}

Log-Step "P02-M01-T08 - installing patched wkhtmltopdf $targetVersion (host build, win64)"

# --- download + hash verify --------------------------------------------------
$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("wkhtmltox." + [guid]::NewGuid().ToString('N').Substring(0,8))
$exePath = Join-Path $tempDir 'wkhtmltox-installer.exe'

Invoke-RunStep "Downloading $downloadUrl" {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    Invoke-WebRequest -Uri $downloadUrl -OutFile $exePath -UseBasicParsing
}

if (-not (Get-DryRun)) {
    if (-not (Test-Path $exePath) -or (Get-Item $exePath).Length -lt 1MB) {
        Log-Fail 'Download failed or produced a suspiciously small file.'
        Log-Remedy 'Check network reachability to github.com, then re-run.'
        exit 1
    }
    $actualSha = (Get-FileHash -Path $exePath -Algorithm SHA256).Hash.ToLower()
    if ($actualSha -ne $expectedSha.ToLower()) {
        Log-Fail "SHA256 mismatch for the wkhtmltox $targetVersion installer"
        Log-Fail "  expected: $expectedSha"
        Log-Fail "  actual:   $actualSha"
        Log-Remedy 'Do NOT install. Delete the file, re-download; if the mismatch persists, update the pin in tooling/versions.lock via a reviewed change.'
        exit 1
    }
    Log-Ok "SHA256 verified: $actualSha"
} else {
    Log-Info "[dry ] would verify SHA256 == $expectedSha"
}

# --- silent install + PATH ---------------------------------------------------
# NSIS rules: /D=<dir> must be the LAST argument, unquoted, no trailing slash.
if ($UserScope) {
    $installDir = Join-Path $env:LOCALAPPDATA 'Programs\wkhtmltopdf'
    $nsisArgs = "/S /D=$installDir"
} else {
    $installDir = 'C:\Program Files\wkhtmltopdf'
    $nsisArgs = "/S /D=$installDir"
}
Invoke-RunStep "Running NSIS silent install ($nsisArgs) - this can take a minute" {
    $proc = Start-Process -FilePath $exePath -ArgumentList $nsisArgs -Wait -PassThru
    if ($proc.ExitCode -ne 0) { throw "installer exited $($proc.ExitCode)" }
}

$scopeLabel = 'machine'
if ($UserScope) { $scopeLabel = 'user' }
# The NSIS layout is <dir>\bin\wkhtmltopdf.exe - PATH points at bin.
$binDir = Join-Path $installDir 'bin'
Invoke-RunStep "Ensuring '$binDir' is on the $scopeLabel PATH" {
    if ($UserScope) {
        $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
        # Drop a stale root-entry from a pre-bin-layout run, then add bin.
        $parts = @($userPath -split ';' | Where-Object { $_ -ne '' -and $_ -ne $installDir })
        if ($parts -notcontains $binDir) { $parts += $binDir }
        [Environment]::SetEnvironmentVariable('Path', ($parts -join ';'), 'User')
    } else {
        $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
        if ($machinePath -notlike "*$binDir*") {
            [Environment]::SetEnvironmentVariable('Path', ($machinePath.TrimEnd(';') + ';' + $binDir), 'Machine')
        }
    }
    if (-not ($env:Path -like "*$binDir*")) { $env:Path += ';' + $binDir }
}

# --- post-verify --------------------------------------------------------------
if (-not (Get-DryRun)) {
    $bin = Join-Path $installDir 'bin\wkhtmltopdf.exe'
    if (-not (Test-Path $bin)) {
        Log-Fail "Expected binary not found after install: $bin"
        Log-Remedy 'Run the installer manually without /S to see its error UI, then re-run this script.'
        exit 1
    }
    $verOut = & $bin --version 2>$null | Select-Object -First 1
    if ("$verOut" -match [regex]::Escape($marker)) {
        Log-Ok "Installed: $verOut"
        Log-Ok 'P02-M01-T08 host half complete - patched build active.'
        Log-Info 'Container half (0.12.6.1-3, patched Qt) is baked into the Odoo image - see versions.lock.'
    } else {
        Log-Fail "Installed binary does not report the patched marker '$marker' (got: $verOut)."
        Log-Remedy 'Check PATH resolution for a stale unpatched wkhtmltopdf shadowing the install.'
        exit 1
    }
}
exit 0
