# =============================================================================
# 1000fix-erp - tooling/workstation/lib/Common.psm1
# Shared helpers for the P02-M01 Windows-native workstation baseline.
#
# Imported (never executed directly) by:
#   setup-workstation.ps1 - verify-workstation.ps1 - machine-inventory.ps1
#   install-wkhtmltopdf.ps1
#
# Runtime target: Windows PowerShell 5.1 (inbox on Windows 10 22H2+/11) and
# PowerShell 7+. No 7-only syntax is used.
#
# Governing rules honoured here:
#   DE-18 - every failure prints the REMEDY, not only the symptom
#   IR-07 / BE-007 LX-03 - no version is ever "latest"; pins come from
#          tooling/versions.lock and nowhere else
#   D-WS-001 - the workstation baseline is native Windows; this module
#          carries no Linux code paths
#   No credentials of any kind are read, stored or emitted by this module.
# =============================================================================

# ---------------------------------------------------------------------------
# Script scope state
# ---------------------------------------------------------------------------
$script:RepoRoot = $null
$script:VersionLockPath = $null
$script:PackagesWingetPath = $null

# ---------------------------------------------------------------------------
# Repo-root + paths
# ---------------------------------------------------------------------------
function Initialize-WorkstationTooling {
    <#
    .SYNOPSIS
        Resolves the repository root and canonical file paths.
        Env override: FIX_REPO_ROOT wins (used by CI and tests).
    #>
    if ($env:FIX_REPO_ROOT) {
        $script:RepoRoot = $env:FIX_REPO_ROOT
    }
    else {
        # $PSScriptRoot here is <repo>\tooling\workstation\lib - go up THREE.
        $script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
    }
    $script:VersionLockPath   = Join-Path $script:RepoRoot 'tooling\versions.lock'
    $script:PackagesWingetPath = Join-Path $script:RepoRoot 'tooling\workstation\packages.winget'
    return $script:RepoRoot
}

function Get-RepoRoot   { if (-not $script:RepoRoot) { Initialize-WorkstationTooling | Out-Null }; return $script:RepoRoot }
function Get-VersionLockPath   { if (-not $script:VersionLockPath) { Initialize-WorkstationTooling | Out-Null }; return $script:VersionLockPath }
function Get-PackagesWingetPath { if (-not $script:PackagesWingetPath) { Initialize-WorkstationTooling | Out-Null }; return $script:PackagesWingetPath }

# ---------------------------------------------------------------------------
# Logging - colour when a console is attached, plain otherwise (DE-18 style)
# ---------------------------------------------------------------------------
function Log-Step { param([string]$Message) Write-Host ''; Write-Host ('==> ' + $Message) -ForegroundColor White }
function Log-Info { param([string]$Message) Write-Host ('[info] ' + $Message) -ForegroundColor Gray }
function Log-Ok   { param([string]$Message) Write-Host ('[ ok ] ' + $Message) -ForegroundColor Green }
function Log-Warn { param([string]$Message) Write-Host ('[warn] ' + $Message) -ForegroundColor Yellow }
function Log-Fail { param([string]$Message) Write-Host ('[FAIL] ' + $Message) -ForegroundColor Red }
function Log-Remedy { param([string]$Message) Write-Host ('      remedy: ' + $Message) -ForegroundColor Yellow }

# ---------------------------------------------------------------------------
# Pin loading - the ONLY place versions may enter the workstation scripts.
# Fails closed when the lock file is missing or a required pin is absent.
# ---------------------------------------------------------------------------
function Load-VersionLock {
    <#
    .SYNOPSIS
        Parses tooling/versions.lock (KEY=VALUE lines) into a hashtable.
        Fails closed (throws) per IR-07 when the lock or a pin is missing.
    #>
    $lockPath = Get-VersionLockPath
    if (-not (Test-Path $lockPath)) {
        Log-Fail "tooling/versions.lock not found at: $lockPath"
        Log-Remedy 'Restore the file from version control - no install may proceed without pins (BE-007 LX-03).'
        throw 'versions.lock missing'
    }

    $lock = @{}
    foreach ($line in Get-Content -LiteralPath $lockPath) {
        $trimmed = $line.Trim()
        if ($trimmed -eq '' -or $trimmed.StartsWith('#')) { continue }
        $idx = $trimmed.IndexOf('=')
        if ($idx -lt 1) { continue }
        $key = $trimmed.Substring(0, $idx).Trim()
        $val = $trimmed.Substring($idx + 1).Trim()
        # Defensive: strip a trailing inline comment ("VALUE  # note").
        $hashIdx = $val.IndexOf(' #')
        if ($hashIdx -ge 0) { $val = $val.Substring(0, $hashIdx).Trim() }
        $val = $val.Trim('"')
        if ($key) { $lock[$key] = $val }
    }

    $required = @(
        'WORKSTATION_WINDOWS_MIN_BUILD',
        'WORKSTATION_WINGET_GIT_VERSION',
        'WORKSTATION_WINGET_DOCKER_VERSION',
        'WORKSTATION_WINGET_PYTHON_VERSION',
        'WORKSTATION_WINGET_CHROME_VERSION',
        'WORKSTATION_WINGET_FIREFOX_VERSION',
        'WORKSTATION_DOCKER_ENGINE_MIN_VERSION',
        'WORKSTATION_DOCKER_COMPOSE_MIN_MAJOR',
        'WORKSTATION_GIT_MIN_VERSION',
        'WORKSTATION_WKHTMLTOPDF_HOST_VERSION',
        'WORKSTATION_WKHTMLTOPDF_HOST_URL',
        'WORKSTATION_WKHTMLTOPDF_HOST_SHA256',
        'WORKSTATION_WKHTMLTOPDF_PATCHED_MARKER',
        'WORKSTATION_WKHTMLTOPDF_CONTAINER_VERSION',
        'WORKSTATION_FONT_NOTO_BENGALI_URL',
        'WORKSTATION_FONT_NOTO_BENGALI_SHA256',
        'WORKSTATION_FONT_NOTO_BENGALI_FAMILY',
        'WORKSTATION_FONT_WINDOWS_BENGALI_FAMILY',
        'WORKSTATION_RESERVED_PORTS'
    )
    foreach ($pin in $required) {
        if (-not $lock.ContainsKey($pin) -or [string]::IsNullOrWhiteSpace($lock[$pin])) {
            Log-Fail "Pin '$pin' is missing or empty in $lockPath"
            Log-Remedy 'Re-add the pin - a workstation must never install an unpinned version (IR-07).'
            throw "pin missing: $pin"
        }
    }
    return $lock
}

# ---------------------------------------------------------------------------
# Version comparison
# ---------------------------------------------------------------------------
function Get-FirstVersionToken {
    <#.SYNOPSIS Extracts the first version-shaped substring:
               "24.0.9, build abc" -> "24.0.9"; "Docker version 29.8.1" -> "29.8.1"; "v2.43" -> "2.43".#>
    param([string]$Raw)
    if ([string]::IsNullOrWhiteSpace($Raw)) { return $null }
    $t = [regex]::Match($Raw, '\d+(\.\d+)+|\d+').Value
    if ([string]::IsNullOrEmpty($t)) { return $null }
    return $t
}

function Test-VersionGe {
    <#.SYNOPSIS Returns $true when version A >= floor B (both may carry prefixes/suffixes).#>
    param([string]$Left, [string]$Right)
    $a = Get-FirstVersionToken $Left
    $b = Get-FirstVersionToken $Right
    if (-not $a -or -not $b) { return $false }
    # [version] rejects single-component strings ("24") - normalise to "24.0".
    if ($a -notmatch '\.') { $a = $a + '.0' }
    if ($b -notmatch '\.') { $b = $b + '.0' }
    try { return ([version]$a) -ge ([version]$b) } catch { return ($a -eq $b) }
}

# ---------------------------------------------------------------------------
# Platform info (T02 preconditions, elevation state)
# ---------------------------------------------------------------------------
function Get-PlatformInfo {
    <#
    .SYNOPSIS
        Returns OS build, elevation and architecture facts used by the checks.
        Never throws - a broken machine must still produce a report.
    #>
    $info = [ordered]@{
        OsName        = [System.Environment]::OSVersion.VersionString
        OsBuild       = [System.Environment]::OSVersion.Version.Build
        Is64Bit       = [System.Environment]::Is64BitOperatingSystem
        PSVersion     = $PSVersionTable.PSVersion.ToString()
        IsElevated    = $false
        IsServer      = $false
        ProductName   = 'Windows (registry probe failed)'
    }
    try {
        $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
        $info['IsElevated'] = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    } catch { $info['IsElevated'] = $false }

    try {
        $cv = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion' -ErrorAction Stop
        $info['DisplayVersion'] = $cv.DisplayVersion
        $info['CurrentBuild'] = $cv.CurrentBuild
        $info['ProductNameRaw'] = $cv.ProductName
        $info['ProductName'] = $cv.ProductName
        if ($cv.InstallationType -match 'Server') { $info['IsServer'] = $true }
        if ($cv.CurrentBuild) { $info['OsBuild'] = [int]$cv.CurrentBuild }
        # The registry ProductName is STALE on Windows 11 - it still reads
        # "Windows 10 Pro" on every Win11 build (a known Microsoft quirk).
        # Reports must carry the marketing name, so derive it from the build:
        # client builds >= 22000 are Windows 11. Raw value kept above for audits.
        if (-not $info['IsServer'] -and $info['OsBuild'] -ge 22000) {
            $info['ProductName'] = 'Windows 11'
        }
    } catch { }

    return [pscustomobject]$info
}

# ---------------------------------------------------------------------------
# Dry-run aware command executor
# ---------------------------------------------------------------------------
$script:DryRun = $false
function Set-DryRun { param([bool]$Enabled) $script:DryRun = $Enabled }
function Get-DryRun { return $script:DryRun }
function Invoke-RunStep {
    <#
    .SYNOPSIS
        Prints a description then executes the command (or echoes it in
        dry-run). Keeps -DryRun honest across every mutating step.
    #>
    param([string]$Description, [scriptblock]$Action)
    if ($script:DryRun) {
        Write-Host ('[dry ] ' + $Description) -ForegroundColor DarkGray
        Write-Host ('       (skipped: ' + $Action.ToString() + ')') -ForegroundColor DarkGray
        return
    }
    Log-Info $Description
    & $Action
}

# ---------------------------------------------------------------------------
# Winget package list (packages.winget)
# ---------------------------------------------------------------------------
function Get-WingetPackageList {
    <#
    .SYNOPSIS
        Parses packages.winget: lines of "winget-id|version|note".
        Comments (#) and blank lines are ignored.
    #>
    $path = Get-PackagesWingetPath
    if (-not (Test-Path $path)) {
        Log-Fail "Winget package list not found: $path"
        Log-Remedy 'Restore tooling/workstation/packages.winget from version control.'
        throw 'packages.winget missing'
    }
    $items = @()
    foreach ($line in Get-Content -LiteralPath $path) {
        $t = $line.Trim()
        if ($t -eq '' -or $t.StartsWith('#')) { continue }
        $parts = $t -split '\|'
        $items += [pscustomobject]@{
            Id      = $parts[0].Trim()
            Version = $parts[1].Trim()
            Note    = if ($parts.Count -ge 3) { $parts[2].Trim() } else { '' }
        }
    }
    return $items
}

# ---------------------------------------------------------------------------
# Fonts (T05)
# ---------------------------------------------------------------------------
function Get-InstalledFontFamilies {
    <#
    .SYNOPSIS
        Enumerates installed font entries from HKLM + HKCU font registry,
        keyed by the registered value name minus the (TrueType)/(OpenType)
        suffix. NOTE: Windows does not guarantee one entry per family -
        entries may be hyphenated PostScript-style basenames
        ("NotoSansBengali-Regular") or compound .ttc names
        ("Nirmala UI & Nirmala UI Bold & ..."). Use Test-FontFamilyInstalled
        for presence checks - do NOT ContainsKey() this table directly.
    #>
    $families = @{}
    foreach ($regHive in @('HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts',
                           'HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts')) {
        try {
            if (-not (Test-Path $regHive)) { continue }
            foreach ($p in Get-ItemProperty -Path $regHive -ErrorAction SilentlyContinue) {
                foreach ($prop in $p.PSObject.Properties) {
                    if ($prop.Name -in @('PSPath','PSParentPath','PSChildName','PSDrive','PSProvider')) { continue }
                    $family = $prop.Name -replace ' \(TrueType\)$','' -replace ' \(OpenType\)$',''
                    $families[$family] = [string]$prop.Value
                }
            }
        } catch { }
    }
    return $families
}

function Test-FontFamilyInstalled {
    <#
    .SYNOPSIS
        Robust font-family presence test across Windows' registration shapes:
          exact            "Noto Sans Bengali"
          PostScript-style "NotoSansBengali-Regular" (prefix match)
          style-suffixed   "Noto Sans Bengali Black"  (prefix match)
          compound .ttc    "Nirmala UI & Nirmala UI Bold & ..." (& split)
    #>
    param([Parameter(Mandatory=$true)][string]$Family, [hashtable]$InstalledFamilies)

    $norm = Test-NormalizeFontName $Family
    if (-not $norm) { return $false }
    foreach ($name in $InstalledFamilies.Keys) {
        foreach ($segment in ($name -split ' & ')) {
            $candidate = Test-NormalizeFontName $segment
            if (-not $candidate) { continue }
            if ($candidate -eq $norm -or $candidate.StartsWith($norm)) { return $true }
        }
    }
    return $false
}

function Test-NormalizeFontName {
    param([string]$Name)
    if ([string]::IsNullOrWhiteSpace($Name)) { return $null }
    return ($Name.ToLower() -replace '[\s_\-]','')
}

function Install-UserFontsFromDirectory {
    <#
    .SYNOPSIS
        Installs .ttf files under a directory for the current user (no admin):
        copies to %LOCALAPPDATA%\Microsoft\Windows\Fonts and registers under
        HKCU. IDEMPOTENT: a file already present and registered is skipped
        (a locked file means the font service has it loaded = installed).
        When the upstream zip layout is present (hinted/ + unhinted/), only
        the HINTED subtree is installed - registering both would duplicate
        every face. Returns @{ Installed = n; Skipped = m }.
    #>
    param([string]$SourceDir)

    # Prefer the hinted subtree when the notofonts zip layout is detected.
    $hinted = Join-Path $SourceDir 'hinted'
    if (Test-Path $hinted) { $SourceDir = $hinted }

    $userFontDir = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
    $hkcuFonts   = 'HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
    if (-not (Test-Path $userFontDir)) { New-Item -ItemType Directory -Path $userFontDir -Force | Out-Null }
    if (-not (Test-Path $hkcuFonts))   { New-Item -Path $hkcuFonts -Force | Out-Null }

    $existing = Get-InstalledFontFamilies
    $installed = 0; $skipped = 0
    foreach ($ttf in Get-ChildItem -LiteralPath $SourceDir -Filter '*.ttf' -Recurse -File) {
        $dest = Join-Path $userFontDir $ttf.Name
        $family = [System.IO.Path]::GetFileNameWithoutExtension($ttf.Name)
        $valueName = "$family (TrueType)"
        $registered = $existing.ContainsKey($family)
        $present = Test-Path -LiteralPath $dest
        if ($registered -and $present) { $skipped++; continue }
        try {
            if (-not $present) {
                Copy-Item -LiteralPath $ttf.FullName -Destination $dest -Force -ErrorAction Stop
            }
        } catch [System.IO.IOException] {
            # In use by the font service = already installed; register+skip.
            $skipped++
            New-ItemProperty -Path $hkcuFonts -Name $valueName -Value $dest -PropertyType String -Force | Out-Null
            continue
        }
        New-ItemProperty -Path $hkcuFonts -Name $valueName -Value $dest -PropertyType String -Force | Out-Null
        $installed++
    }
    return @{ Installed = $installed; Skipped = $skipped }
}

# ---------------------------------------------------------------------------
# Installed-version probe (T04): winget's console output truncates at the
# terminal width, so every package id gets a deterministic BINARY fallback.
# ---------------------------------------------------------------------------
function Get-InstalledAppVersion {
    <#
    .SYNOPSIS
        Best-effort installed-version probe for the pinned package ids.
        Returns a version string, or $null when the package is absent.
    #>
    param([Parameter(Mandatory=$true)][string]$WingetId)

    switch ($WingetId) {
        'Git.Git' {
            $c = Get-Command git -ErrorAction SilentlyContinue
            if ($c) {
                $v = & $c.Source --version 2>$null | Select-Object -First 1
                # "git version 2.55.0.windows.5" == winget "2.55.0.5":
                # fold the ".windows.N" tag into the 4th version component.
                $v = "$v" -replace '^git version\s*','' -replace '\.windows\.','.'
                $t = Get-FirstVersionToken $v
                if ($t) { return $t }
            }
        }
        'Docker.DockerDesktop' {
            # Returns the ENGINE version (docker --version), not the Desktop
            # version - callers must NOT compare this against the Desktop pin;
            # the engine/compose floors are enforced by check T06.
            $c = Get-Command docker -ErrorAction SilentlyContinue
            if ($c) { $v = & $c.Source --version 2>$null | Select-Object -First 1
                      $t = Get-FirstVersionToken "$v"
                      if ($t) { return $t } }
        }
        'Python.Python.3.12' {
            # Prefer the py launcher pinned to the 3.12 line.
            $py = Get-Command py -ErrorAction SilentlyContinue
            if ($py) {
                $v = & $py.Source -3.12 --version 2>$null | Select-Object -First 1
                if ("$v" -match '(3\.12[\d\.]*)') { return ($Matches[1].Trim('.')) }
            }
        }
        'Google.Chrome' {
            foreach ($exe in @('chrome.exe','chromium.exe')) {
                foreach ($root in @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths',
                                    'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths')) {
                    $k = Join-Path $root $exe
                    if (Test-Path $k) {
                        $p = (Get-ItemProperty $k).'(default)'
                        if ($p -and (Test-Path $p)) {
                            $v = (Get-Item $p).VersionInfo.ProductVersion
                            # While Chrome is RUNNING, chrome.exe still reports the
                            # old build even though the new version dir is laid
                            # down. Take the max(exe, highest version dir).
                            $appDir = Split-Path -Parent $p
                            $dirMax = Get-ChildItem -LiteralPath $appDir -Directory -ErrorAction SilentlyContinue |
                                      Where-Object Name -match '^\d+(\.\d+){3}$' |
                                      ForEach-Object { $_.Name } |
                                      Sort-Object { [version]$_ } -ErrorAction SilentlyContinue |
                                      Select-Object -Last 1
                            foreach ($cand in @($v, $dirMax)) {
                                if ($cand -and (Test-VersionGe "$cand" "$v")) { $v = "$cand" }
                            }
                            return "$v"
                        }
                    }
                }
            }
        }
        'Mozilla.Firefox' {
            $k = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe'
            if (-not (Test-Path $k)) { $k = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe' }
            if (Test-Path $k) {
                $p = (Get-ItemProperty $k).'(default)'
                if ($p -and (Test-Path $p)) { return (Get-Item $p).VersionInfo.ProductVersion }
            }
        }
    }
    return $null
}

# ---------------------------------------------------------------------------
# Port hygiene (T10)
# ---------------------------------------------------------------------------
function Get-ReservedPortListeners {
    <#
    .SYNOPSIS
        Returns listeners on the reserved ports (5432/6379/9000 by pin).
        Each row: Port, LocalAddress, OwningProcess, ProcessName, IsDocker.
    #>
    param([int[]]$Ports)
    $rows = @()
    foreach ($port in $Ports) {
        $conns = $null
        try { $conns = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue } catch { }
        foreach ($c in $conns) {
            $pname = ''; $isDocker = $false
            try {
                $proc = Get-Process -Id $c.OwningProcess -ErrorAction Stop
                $pname = $proc.ProcessName
                if ($pname -match 'docker|com\.docker|vpnkit|wslrelay') { $isDocker = $true }
            } catch { $pname = "pid $($c.OwningProcess)" }
            $rows += [pscustomobject]@{
                Port         = $port
                LocalAddress = $c.LocalAddress
                OwningProcess= $c.OwningProcess
                ProcessName  = $pname
                IsDocker     = $isDocker
            }
        }
    }
    return $rows
}

# ---------------------------------------------------------------------------
# Hardware summary (T01) - shared by inventory + verify
# ---------------------------------------------------------------------------
function Get-HardwareSummary {
    <#.SYNOPSIS CPU / RAM / system-disk / display facts. Never throws.#>
    $s = [ordered]@{
        CpuName = ''; CpuSockets = 0; CpuCores = 0; CpuThreads = 0
        RamTotalGB = 0
        SystemDiskSizeGB = 0; SystemDiskFreeGB = 0; SystemDiskBus = ''; SystemDiskMedia = ''
        Displays = @()
    }
    try {
        $cpus = Get-CimInstance Win32_Processor -ErrorAction Stop
        foreach ($c in $cpus) {
            $s.CpuSockets++
            $s.CpuName = $c.Name.Trim()
            $s.CpuCores  += [int]$c.NumberOfCores
            $s.CpuThreads += [int]$c.NumberOfLogicalProcessors
        }
    } catch { }
    try {
        $mem = Get-CimInstance Win32_PhysicalMemory -ErrorAction Stop
        $sum = ($mem | Measure-Object -Property Capacity -Sum).Sum
        $s.RamTotalGB = [math]::Round($sum / 1GB, 1)
    } catch { }

    try {
        $os = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
        $sysDrive = ($os.SystemDrive).TrimEnd('\')     # e.g. C:
        $vol = Get-CimInstance Win32_Volume -Filter "DriveLetter='$sysDrive'" -ErrorAction Stop |
               Select-Object -First 1
        if ($vol) {
            $s.SystemDiskSizeGB = [math]::Round($vol.Capacity / 1GB, 0)
            $s.SystemDiskFreeGB = [math]::Round($vol.FreeSpace / 1GB, 0)
        }
        # Physical disk backing the system volume (BusType/MediaType)
        $part = Get-Partition -DriveLetter $sysDrive.TrimEnd(':') -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($part) {
            $disk = Get-PhysicalDisk -ErrorAction SilentlyContinue | Where-Object { $_.DeviceId -eq [string]$part.DiskNumber } | Select-Object -First 1
            if ($disk) {
                $s.SystemDiskBus   = [string]$disk.BusType
                $s.SystemDiskMedia = [string]$disk.MediaType
            }
        }
    } catch { }

    try {
        $gpus = Get-CimInstance Win32_VideoController -ErrorAction Stop |
                Where-Object { $_.CurrentHorizontalResolution -gt 0 }
        foreach ($g in $gpus) {
            $s.Displays += [pscustomobject]@{
                Name     = $g.Name
                Width    = [int]$g.CurrentHorizontalResolution
                Height   = [int]$g.CurrentVerticalResolution
            }
        }
    } catch { }

    return [pscustomobject]$s
}

# ---------------------------------------------------------------------------
# Hardware classification (T01) - the SINGLE implementation of the two
# baselines, consumed by both machine-inventory.ps1 and verify-workstation.ps1
# (audit F-C1: the two scripts had diverged - one required 2560x1440, the
# other only width>=2560. Roadmap T01 says "2560x1440 or dual display").
# ---------------------------------------------------------------------------
function Get-HardwareClassification {
    <#
    .SYNOPSIS
        Classifies a Get-HardwareSummary result against the roadmap T01
        baselines. RECOMMENDED = 8c/16t, 32 GB, 512 GB NVMe, 2560x1440 or
        dual display. MINIMUM = 4c, 16 GB, 256 GB SSD (core profile only).
        Returns @{ Recommended; Minimum; Classification }.
    #>
    param([Parameter(Mandatory=$true)]$Hardware)

    $displays = @($Hardware.Displays)
    $displayRecommended = ($displays.Count -ge 2) -or
        (@($displays | Where-Object { $_.Width -ge 2560 -and $_.Height -ge 1440 }).Count -ge 1)

    $recommended = ($Hardware.CpuCores -ge 8) -and ($Hardware.CpuThreads -ge 16) -and
                   ($Hardware.RamTotalGB -ge 32) -and
                   ($Hardware.SystemDiskSizeGB -ge 512) -and
                   ($Hardware.SystemDiskBus -eq 'NVMe') -and
                   $displayRecommended
    $minimum = ($Hardware.CpuCores -ge 4) -and ($Hardware.RamTotalGB -ge 16) -and
               ($Hardware.SystemDiskSizeGB -ge 256) -and
               ($Hardware.SystemDiskMedia -match 'SSD|Unspecified')

    $class = if ($recommended) { 'RECOMMENDED (full profile capable)' }
             elseif ($minimum) { "MINIMUM (core profile only - BE-001 SS3.1: the 'full' profile + Odoo + IDE exceeds 16 GB)" }
             else { 'BELOW MINIMUM - not a supported build machine' }

    return [pscustomobject]@{ Recommended = $recommended; Minimum = $minimum; Classification = $class }
}

# ---------------------------------------------------------------------------
# docker-users group membership (T06, Windows analogue of "add the user to
# the docker group"). Returns $true / $false, or $null when indeterminate
# (group absent - e.g. some Docker Desktop backends - or probe unavailable).
# ---------------------------------------------------------------------------
function Test-UserInDockerUsersGroup {
    try {
        $me = [Security.Principal.WindowsIdentity]::GetCurrent().Name
        $members = Get-LocalGroupMember -Group 'docker-users' -ErrorAction Stop
        foreach ($m in $members) {
            if ($m.Name -ieq $me) { return $true }
        }
        return $false
    } catch { return $null }
}

Export-ModuleMember -Function @(
    'Initialize-WorkstationTooling','Get-RepoRoot','Get-VersionLockPath','Get-PackagesWingetPath',
    'Log-Step','Log-Info','Log-Ok','Log-Warn','Log-Fail','Log-Remedy',
    'Load-VersionLock','Get-FirstVersionToken','Test-VersionGe',
    'Get-PlatformInfo','Set-DryRun','Get-DryRun','Invoke-RunStep',
    'Get-WingetPackageList','Get-InstalledFontFamilies','Test-FontFamilyInstalled','Test-NormalizeFontName','Install-UserFontsFromDirectory',
    'Get-InstalledAppVersion','Get-ReservedPortListeners','Get-HardwareSummary',
    'Get-HardwareClassification','Test-UserInDockerUsersGroup'
)
