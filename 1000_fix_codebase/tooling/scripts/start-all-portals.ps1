# =============================================================================
# start-all-portals.ps1 - Launch all 8 Next.js Portals + Static Frontend
# =============================================================================
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$logDir = Join-Path $root 'results\portals'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

$portals = @(
    @{ Name = 'customer';      Port = 3000 },
    @{ Name = 'corporate';     Port = 3001 },
    @{ Name = 'analytics';     Port = 3002 },
    @{ Name = 'seller';        Port = 3003 },
    @{ Name = 'brand';         Port = 3004 },
    @{ Name = 'agent-console'; Port = 3005 },
    @{ Name = 'partner';       Port = 3006 },
    @{ Name = 'vendor';        Port = 3007 }
)

Write-Host "--- Checking & Launching Next.js Web Portals ---" -ForegroundColor Cyan

foreach ($p in $portals) {
    $port = $p.Port
    $name = $p.Name
    $appDir = Join-Path $root "apps\web\$name"
    $logFile = Join-Path $logDir "$name.log"
    
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        Write-Host "[ALREADY UP] Portal $name is already listening on port $port" -ForegroundColor Green
    } else {
        Write-Host "[STARTING] Launching Portal $name on port $port..." -ForegroundColor Yellow
        $startInfo = New-Object System.Diagnostics.ProcessStartInfo
        $startInfo.FileName = "cmd.exe"
        $startInfo.Arguments = "/c npm.cmd run dev > `"$logFile`" 2>&1"
        $startInfo.WorkingDirectory = $appDir
        $startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
        $startInfo.CreateNoWindow = $true
        $startInfo.UseShellExecute = $true
        [System.Diagnostics.Process]::Start($startInfo) | Out-Null
    }
}

# Also launch Front_end static prototype on port 8085
$frontEndDir = "c:\software_project\software_project_14\1000 fix\1000fix_new_erp_system\Front_end"
$feConn = Get-NetTCPConnection -LocalPort 8085 -State Listen -ErrorAction SilentlyContinue
if ($feConn) {
    Write-Host "[ALREADY UP] Front_end prototype is already listening on port 8085" -ForegroundColor Green
} else {
    Write-Host "[STARTING] Launching Front_end prototype on port 8085..." -ForegroundColor Yellow
    $feLog = Join-Path $logDir "front_end_static.log"
    $py = Join-Path $root ".venv\Scripts\python.exe"
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = "cmd.exe"
    $startInfo.Arguments = "/c `"$py`" -m http.server 8085 --bind 127.0.0.1 > `"$feLog`" 2>&1"
    $startInfo.WorkingDirectory = $frontEndDir
    $startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    $startInfo.CreateNoWindow = $true
    $startInfo.UseShellExecute = $true
    [System.Diagnostics.Process]::Start($startInfo) | Out-Null
}

Write-Host "All portal launch commands dispatched. Waiting for health..." -ForegroundColor Cyan
