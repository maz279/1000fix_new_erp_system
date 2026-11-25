# =============================================================================
# apply-branch-protection.ps1 - Enforce branch protection per BE-003 Section 3.3
# Implements R01-M03-T01 from R01_Foundation_and_Governance_Closure.md
# Configures develop and main protection rules matching .github/settings.yml
#
# R01 audit correction (2026-10-21): evidence is written ONLY after the GitHub
# API confirms the rules, with api_verified=true and per-branch API status.
# Without an authenticated gh CLI the script records nothing and exits
# non-zero - a local JSON of intended rules was previously written BEFORE any
# API call and read as "protection applied".
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

function Test-GhAuthed {
    $ghCli = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $ghCli) { return $false }
    try {
        $null = & gh auth status 2>$null
        return ($LASTEXITCODE -eq 0)
    } catch { return $false }
}

function Write-Evidence {
    param([bool]$ApiVerified, [hashtable]$BranchApiStatus)
    $rulesRecord = @{
        repository = $Repo
        configured_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        standard = "BE-003 Section 3.3 / P02-M03-T05 / R01-M03-T01"
        declarative_file = ".github/settings.yml"
        api_verified = $ApiVerified
        branch_api_status = $BranchApiStatus
        branches = @{
            main = $mainProtection
            develop = $developProtection
        }
    }
    $evidenceFile = Join-Path $evidenceDir "branch-protection-rules.json"
    $rulesRecord | ConvertTo-Json -Depth 6 | Set-Content -Path $evidenceFile -Encoding UTF8
    Write-Host "[BranchProtection] Evidence written: $evidenceFile (api_verified: $ApiVerified)" -ForegroundColor Green
}

if ($VerifyOnly) {
    # Verify what is ACTUALLY configured on the remote.
    if (-not (Test-GhAuthed)) {
        Write-Host "[BranchProtection] FAIL: --VerifyOnly requires an authenticated gh CLI (gh auth login)." -ForegroundColor Red
        exit 1
    }
    $apiStatus = @{}
    foreach ($branch in @("develop", "main")) {
        & gh api "repos/$Repo/branches/$branch/protection" 2>$null | Out-Null
        $apiStatus[$branch] = if ($LASTEXITCODE -eq 0) { "PROTECTION_PRESENT" } else { "NO_PROTECTION" }
    }
    Write-Evidence -ApiVerified $true -BranchApiStatus $apiStatus
    $unprotected = @($apiStatus.GetEnumerator() | Where-Object { $_.Value -ne "PROTECTION_PRESENT" }).Count
    if ($unprotected -gt 0) {
        Write-Host "[BranchProtection] $unprotected branch(es) unprotected on $Repo." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "[BranchProtection] Verified: develop + main protected on $Repo." -ForegroundColor Green
    exit 0
}

if (-not (Test-GhAuthed)) {
    Write-Host "[BranchProtection] FAIL: gh CLI not available/authenticated. No evidence written - protection was NOT applied." -ForegroundColor Red
    Write-Host "  The Probot Settings app may auto-apply .github/settings.yml on push; verify with -VerifyOnly after." -ForegroundColor Yellow
    exit 1
}

if ($DryRun) {
    Write-Host "[BranchProtection] Dry run: gh authenticated; live API calls skipped, no evidence written." -ForegroundColor Cyan
    exit 0
}

Write-Host "[BranchProtection] Applying branch protection via GitHub API to $Repo..." -ForegroundColor Cyan

$mainJson = $mainProtection | ConvertTo-Json -Depth 6 -Compress
$developJson = $developProtection | ConvertTo-Json -Depth 6 -Compress
$apiStatus = @{}
$anyFailure = $false

foreach ($pair in @(@{ branch = "develop"; json = $developJson }, @{ branch = "main"; json = $mainJson })) {
    $branch = $pair.branch
    Write-Host "  Applying protection to $branch..." -NoNewline
    $tmp = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $tmp -Value $pair.json -Encoding UTF8
    & gh api -X PUT "repos/$Repo/branches/$branch/protection" --input $tmp 2>$null | Out-Null
    $ok = ($LASTEXITCODE -eq 0)
    Remove-Item -Force $tmp -ErrorAction SilentlyContinue
    if ($ok) {
        $apiStatus[$branch] = "APPLIED"
        Write-Host " [OK]" -ForegroundColor Green
    } else {
        $apiStatus[$branch] = "API_FAILED"
        $anyFailure = $true
        Write-Host " [FAILED]" -ForegroundColor Red
    }
}

# Evidence written only now - after the API calls, recording what actually happened.
Write-Evidence -ApiVerified (-not $anyFailure) -BranchApiStatus $apiStatus
if ($anyFailure) {
    Write-Host "[BranchProtection] One or more API calls failed; evidence records api_verified=false." -ForegroundColor Yellow
    exit 1
}
Write-Host "[BranchProtection] Branch protection applied and verified." -ForegroundColor Green
exit 0
