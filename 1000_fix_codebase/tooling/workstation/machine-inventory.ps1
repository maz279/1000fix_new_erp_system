# =============================================================================
# 1000fix-erp - tooling/workstation/machine-inventory.ps1
# P02-M01-T01 - Produce the machine inventory record.
#
# "Produces" column of the roadmap task: 'Machine inventory'. Emits a
# human-readable report and, with -OutFile, a JSON record suitable for the
# hardware register. Classifies the machine against BOTH baselines (the
# single shared implementation lives in lib/Common.psm1 -
# Get-HardwareClassification):
#   RECOMMENDED  8c/16t, 32 GB, 512 GB NVMe, >=2560x1440 or dual display
#   MINIMUM      4c, 16 GB, 256 GB SSD  (supported on the 'core' Compose
#                profile only - BE-001 SS3.1, retained on Windows)
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File machine-inventory.ps1 [-OutFile path.json]
#
# Exit codes: 0 inventory produced (a BELOW-MINIMUM classification is a
#             finding IN the record, not a failure of the tool) - 1 unexpected
#             failure (trap prints FAIL + remedy per DE-18).
# =============================================================================
[CmdletBinding()]
param(
    [string]$OutFile = ''
)

$ErrorActionPreference = 'Continue'      # a broken machine must still report
# DE-18: a terminating error (e.g. versions.lock missing) still prints the
# remedy path Load-VersionLock provides, then exits non-zero - never a bare
# stack trace. Write-Host fallback covers a failed module load.
trap {
    $msg = "unexpected failure: $($_.Exception.Message)"
    try { Log-Fail $msg } catch { Write-Host ('[FAIL] ' + $msg) -ForegroundColor Red }
    try { Log-Remedy 'Fix the reported cause and re-run.' } catch { }
    exit 1
}
Import-Module (Join-Path $PSScriptRoot 'lib\Common.psm1') -Force -DisableNameChecking
Initialize-WorkstationTooling | Out-Null
$lock = Load-VersionLock

# --- gather -------------------------------------------------------------------
$platform  = Get-PlatformInfo
$hardware  = Get-HardwareSummary
$fonts     = Get-InstalledFontFamilies
$ports     = $lock.WORKSTATION_RESERVED_PORTS.Split(',') | ForEach-Object { [int]$_.Trim() }
$listeners = Get-ReservedPortListeners -Ports $ports

function Get-ToolVersion {
    param([string]$Name, [string[]]$Argument = @('--version'))
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) { return $null }
    try {
        $out = & $cmd.Source @Argument 2>$null | Select-Object -First 1
        return "$out".Trim()
    } catch { return $null }
}

$tools = [ordered]@{
    git        = Get-ToolVersion 'git'
    docker     = Get-ToolVersion 'docker'
    compose    = Get-ToolVersion 'docker' @('compose','version')
    python312  = $null
    pythonOnPath = Get-ToolVersion 'python'
    wkhtmltopdf= Get-ToolVersion 'wkhtmltopdf'
}
# The pinned line is Python 3.12.x (versions.lock). Bare 'python' on PATH can
# resolve to ANY other minor (the pre-fix inventory recorded 3.14.7 there),
# so probe the py launcher pinned to 3.12 first and record both separately.
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
    $v = & $py.Source -3.12 --version 2>$null | Select-Object -First 1
    if ("$v" -match '3\.12') { $tools.python312 = "$v".Trim() }
}
# wkhtmltopdf: a shell spawned before the User PATH update cannot resolve it -
# fall back to the canonical install locations (PATH registry is the truth).
if (-not $tools.wkhtmltopdf) {
    foreach ($canon in @((Join-Path $env:LOCALAPPDATA 'Programs\wkhtmltopdf\bin\wkhtmltopdf.exe'),
                         'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')) {
        if (Test-Path $canon) {
            $tools.wkhtmltopdf = (& $canon --version 2>$null | Select-Object -First 1)
            break
        }
    }
}

# BitLocker (best effort; elevated gives a definitive answer)
$encryption = 'unknown'
try {
    $bde = manage-bde -status "$env:SystemDrive" 2>$null
    $prot = ($bde | Where-Object { $_ -match 'Protection Status' }) -join ''
    if ($prot -match 'Protection On') { $encryption = 'on' }
    elseif ($prot -match 'Protection Off') { $encryption = 'off' }
} catch { }

# --- classification (single shared implementation: Get-HardwareClassification) ----
$t01 = Get-HardwareClassification -Hardware $hardware
$recommended = $t01.Recommended
$minimum     = $t01.Minimum
$class       = $t01.Classification

# --- human report ---------------------------------------------------------------
Log-Step 'P02-M01-T01 - machine inventory'
Write-Host ("  host          : {0}" -f $env:COMPUTERNAME)
Write-Host ("  generated     : {0} {1}" -f (Get-Date -Format 'yyyy-MM-dd'), (Get-Date -Format 'HH:mm:ss'))
Write-Host ("  os            : {0} build {1} ({2})" -f $platform.ProductName, $platform.OsBuild, $platform.DisplayVersion)
Write-Host ("  cpu           : {0} - {1} cores / {2} threads ({3} sockets)" -f $hardware.CpuName, $hardware.CpuCores, $hardware.CpuThreads, $hardware.CpuSockets)
Write-Host ("  ram           : {0} GB" -f $hardware.RamTotalGB)
Write-Host ("  system disk   : {0} GB total, {1} GB free - bus {2}, media {3}" -f $hardware.SystemDiskSizeGB, $hardware.SystemDiskFreeGB, $hardware.SystemDiskBus, $hardware.SystemDiskMedia)
foreach ($d in $hardware.Displays) {
    Write-Host ("  display       : {0}x{1} ({2})" -f $d.Width, $d.Height, $d.Name)
}
Write-Host ("  encryption    : BitLocker {0}" -f $encryption)
foreach ($k in $tools.Keys) {
    Write-Host ("  tool {0,-12}: {1}" -f $k, ($(if ($tools[$k]) { $tools[$k] } else { '(not found)' })))
}
$noto = Test-FontFamilyInstalled -Family $lock.WORKSTATION_FONT_NOTO_BENGALI_FAMILY -InstalledFamilies $fonts
$nirmala = Test-FontFamilyInstalled -Family $lock.WORKSTATION_FONT_WINDOWS_BENGALI_FAMILY -InstalledFamilies $fonts
Write-Host ("  bengali fonts : Noto Sans Bengali={0}  Nirmala UI={1}" -f $noto, $nirmala)
Write-Host ("  reserved ports: {0} listener(s) on {1}" -f $listeners.Count, $lock.WORKSTATION_RESERVED_PORTS)
Write-Host ''
if ($recommended) { Log-Ok "classification: $class" }
elseif ($minimum) { Log-Warn "classification: $class" }
else { Log-Fail "classification: $class" }

# --- JSON record -----------------------------------------------------------------
$record = [ordered]@{
    schema            = '1000fix-erp/machine-inventory/2'   # v2: python -> python312 (+ pythonOnPath added)
    task              = 'P02-M01-T01'
    host              = $env:COMPUTERNAME
    generatedUtc      = (Get-Date).ToUniversalTime().ToString('o')
    os                = [ordered]@{
        product = $platform.ProductName; displayVersion = $platform.DisplayVersion
        build = $platform.OsBuild; isServer = $platform.IsServer
    }
    hardware          = [ordered]@{
        cpuName = $hardware.CpuName; cpuCores = $hardware.CpuCores; cpuThreads = $hardware.CpuThreads
        ramTotalGB = $hardware.RamTotalGB
        systemDiskSizeGB = $hardware.SystemDiskSizeGB; systemDiskFreeGB = $hardware.SystemDiskFreeGB
        systemDiskBus = $hardware.SystemDiskBus; systemDiskMedia = $hardware.SystemDiskMedia
        displays = $hardware.Displays
    }
    classification    = $class
    encryption        = $encryption
    tools             = $tools
    bengaliFonts      = [ordered]@{
        notoSansBengali = $noto; nirmalaUI = $nirmala
    }
    reservedPortListeners = $listeners
}

if ($OutFile -ne '') {
    $json = $record | ConvertTo-Json -Depth 6
    [System.IO.File]::WriteAllText($OutFile, $json)
    Log-Ok "inventory JSON written: $OutFile"
}

exit 0
