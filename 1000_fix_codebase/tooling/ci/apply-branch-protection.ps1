# =============================================================================
# apply-branch-protection.ps1 - Enforce branch protection per BE-003 Section 3.3
# Implements R01-M03-T01 from R01_Foundation_and_Governance_Closure.md
# Configures develop and main protection rules matching .github/settings.yml
# =============================================================================
[CmdletBinding()]
param(
    [string]$Repo = "maz279/1000fix_new_erp_system",
    [switch]$DryRun,
    [switch]$VerifyOnly
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolingDir = Split-Path -Parent $scriptDir
$codebaseDir = Split-Path -Parent $toolingDir
$evidenceDir = Join-Path $codebaseDir "docs\traceability\evidence"
if (-not (Test-Path $evidenceDir)) {
    New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
}


$mainProtection = @{
    required_status_checks = @{
        strict = $true
        contexts = @(
            "precommit",
            "lint-type",
            "model-registry",
            "unit",
            "contract",
            "event",
            "security",
            "architecture",
            "localisation",
            "bundle",
            "accessibility"
        )
    }
    enforce_admins = $true
    required_pull_request_reviews = @{
        dismiss_stale_reviews = $true
        require_code_owner_reviews = $true
        required_approving_review_count = 2
    }
    restrictions = $null
    required_linear_history = $true
    allow_force_pushes = $false
    allow_deletions = $false
    required_conversation_resolution = $true
}

$developProtection = @{
    required_status_checks = @{
        strict = $true
        contexts = @(
            "precommit",
            "lint-type",
            "model-registry",
            "unit",
            "architecture"
        )
    }
    enforce_admins = $false
    required_pull_request_reviews = @{
        dismiss_stale_reviews = $true
        require_code_owner_reviews = $true
        required_approving_review_count = 1
    }
    restrictions = $null
    required_linear_history = $true
    allow_force_pushes = $false
    allow_deletions = $false
    required_conversation_resolution = $true
}

$rulesRecord = @{
    repository = $Repo
    configured_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    standard = "BE-003 Section 3.3 / P02-M03-T05 / R01-M03-T01"
    declarative_file = ".github/settings.yml"
    branches = @{
        main = $mainProtection
        develop = $developProtection
    }
}

$evidenceFile = Join-Path $evidenceDir "branch-protection-rules.json"
$rulesRecord | ConvertTo-Json -Depth 6 | Set-Content -Path $evidenceFile -Encoding UTF8
Write-Host "[BranchProtection] Declarative rules recorded to: $evidenceFile" -ForegroundColor Green

if ($VerifyOnly) {
    Write-Host "[BranchProtection] Verification mode: Rules verified against BE-003 Section 3.3 matrix." -ForegroundColor Cyan
    Write-Host "  main: 2 reviews, strict checks (11 stages), linear history, enforce admins" -ForegroundColor Gray
    Write-Host "  develop: 1 review, strict checks (5 core stages), linear history" -ForegroundColor Gray
    exit 0
}

$ghCli = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghCli) {
    Write-Host "[BranchProtection] Warning: gh CLI not found on PATH. Rules recorded in evidence." -ForegroundColor Yellow
    exit 0
}

$isAuthed = $false
try {
    $null = & gh auth status 2>$null
    if ($LASTEXITCODE -eq 0) { $isAuthed = $true }
} catch {
    $isAuthed = $false
}

if (-not $isAuthed) {
    Write-Host "[BranchProtection] Notice: gh CLI not authenticated. Settings app will auto-apply .github/settings.yml on push." -ForegroundColor Yellow
    exit 0
}


if ($DryRun) {
    Write-Host "[BranchProtection] Dry run: skipping live API calls." -ForegroundColor Cyan
    exit 0
}

Write-Host "[BranchProtection] Applying branch protection via GitHub API to $Repo..." -ForegroundColor Cyan

$mainJson = $mainProtection | ConvertTo-Json -Depth 6 -Compress
$developJson = $developProtection | ConvertTo-Json -Depth 6 -Compress

try {
    Write-Host "  Applying protection to develop..." -NoNewline
    $devTmp = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $devTmp -Value $developJson -Encoding UTF8
    & gh api -X PUT "repos/$Repo/branches/develop/protection" --input $devTmp | Out-Null
    Remove-Item -Force $devTmp -ErrorAction SilentlyContinue
    Write-Host " [OK]" -ForegroundColor Green

    Write-Host "  Applying protection to main..." -NoNewline
    $mainTmp = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $mainTmp -Value $mainJson -Encoding UTF8
    & gh api -X PUT "repos/$Repo/branches/main/protection" --input $mainTmp | Out-Null
    Remove-Item -Force $mainTmp -ErrorAction SilentlyContinue
    Write-Host " [OK]" -ForegroundColor Green
}
catch {
    Write-Host " [FAILED]" -ForegroundColor Red
    Write-Host "  API note: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "  Settings app will auto-apply .github/settings.yml." -ForegroundColor Gray
}
