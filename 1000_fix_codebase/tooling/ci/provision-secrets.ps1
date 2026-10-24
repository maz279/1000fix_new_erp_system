# =============================================================================
# provision-secrets.ps1 - Provision CI secrets and variables for GitHub Actions
# Implements R01-M03-T02 from R01_Foundation_and_Governance_Closure.md
#
# R01 audit correction (2026-10-21):
#   - NO literal fallback values. A secret not present in the environment is
#     reported MISSING and never provisioned ("never literals" means exactly
#     that - a hardcoded placeholder password is a literal).
#   - Evidence is written ONLY after successful `gh secret set` / `gh variable
#     set` calls, and records names + status only - never values.
#   - Unauthenticated runs exit non-zero instead of leaving "PROVISIONED"
#     evidence that never touched GitHub.
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

# The canonical set of secrets and variables declared in .github/workflows/ci.yml
$requiredSecrets = @(
    "PACT_BROKER_URL",
    "FIX_A11Y_PASSWORD",
    "POSTGRES_PASSWORD",
    "REDIS_PASSWORD"
)

$requiredVars = @(
    "FIX_A11Y_USER",
    "FIX_A11Y_BASE_URL",
    "CI_ENVIRONMENT"
)

# Resolve secret values from the environment ONLY. Missing = MISSING, never a placeholder.
$secretStatus = @{}
foreach ($s in $requiredSecrets) {
    $val = [Environment]::GetEnvironmentVariable($s)
    $secretStatus[$s] = if ([string]::IsNullOrEmpty($val)) { "MISSING (set env var $s)" } else { "RESOLVED" }
}

# Variables are non-secret configuration; documented defaults are acceptable,
# but they are recorded as values openly (they are not secrets).
$varValues = @{}
foreach ($v in $requiredVars) {
    $val = [Environment]::GetEnvironmentVariable($v)
    if ([string]::IsNullOrEmpty($val)) {
        if ($v -eq "FIX_A11Y_USER") { $val = "admin" }
        elseif ($v -eq "FIX_A11Y_BASE_URL") { $val = "http://127.0.0.1:8069" }
        elseif ($v -eq "CI_ENVIRONMENT") { $val = "ci-runner" }
    }
    $varValues[$v] = $val
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
    param([string]$Status, [hashtable]$SecretResults, [hashtable]$VarResults)
    $provisionRecord = @{
        repository = $Repo
        provisioned_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        standard = "DE-10 / P02-M09-T02 / R01-M03-T02"
        status = $Status
        note = "names and statuses only - secret values are never recorded in evidence"
        secrets = ($SecretResults.GetEnumerator() | Sort-Object Name | ForEach-Object {
            @{ name = $_.Key; status = $_.Value; type = "secret" }
        })
        vars = ($VarResults.GetEnumerator() | Sort-Object Name | ForEach-Object {
            @{ name = $_.Key; value = $_.Value; type = "variable" }
        })
    }
    $evidenceFile = Join-Path $evidenceDir "ci-secrets-provisioned.json"
    $provisionRecord | ConvertTo-Json -Depth 5 | Set-Content -Path $evidenceFile -Encoding UTF8
    Write-Host "[ProvisionSecrets] Evidence written: $evidenceFile (status: $Status)" -ForegroundColor Green
}

if ($VerifyOnly) {
    # Verify what is ACTUALLY set on the remote - names only, via gh secret list.
    if (-not (Test-GhAuthed)) {
        Write-Host "[ProvisionSecrets] FAIL: --VerifyOnly requires an authenticated gh CLI (gh auth login)." -ForegroundColor Red
        exit 1
    }
    $remoteSecrets = (& gh secret list -R $Repo --json name 2>$null | ConvertFrom-Json) | ForEach-Object { $_.name }
    $remoteVars = (& gh variable list -R $Repo --json name 2>$null | ConvertFrom-Json) | ForEach-Object { $_.name }
    $verifyResults = @{}
    foreach ($s in $requiredSecrets) {
        $verifyResults[$s] = if ($remoteSecrets -contains $s) { "VERIFIED_ON_REMOTE" } else { "ABSENT_ON_REMOTE" }
    }
    $varResults = @{}
    foreach ($v in $requiredVars) {
        $varResults[$v] = $varValues[$v]
        $verifyResults["VAR:$v"] = if ($remoteVars -contains $v) { "VERIFIED_ON_REMOTE" } else { "ABSENT_ON_REMOTE" }
    }
    Write-Evidence -Status "VERIFIED" -SecretResults $verifyResults -VarResults $varResults
    $absent = @($verifyResults.Values | Where-Object { $_ -eq "ABSENT_ON_REMOTE" }).Count
    if ($absent -gt 0) {
        Write-Host "[ProvisionSecrets] $absent required item(s) absent on remote." -ForegroundColor Yellow
        exit 1
    }
    exit 0
}

# Provisioning requires gh + auth + every secret resolved in the environment.
$missing = @($requiredSecrets | Where-Object { $secretStatus[$_] -like "MISSING*" })
if ($missing.Count -gt 0) {
    Write-Host "[ProvisionSecrets] FAIL: secrets not present in environment: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "  Provide them via environment variables; literals are never acceptable (DE-10)." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-GhAuthed)) {
    Write-Host "[ProvisionSecrets] FAIL: gh CLI not available/authenticated. No evidence written - nothing was provisioned." -ForegroundColor Red
    Write-Host "  Authenticate with 'gh auth login' and re-run." -ForegroundColor Yellow
    exit 1
}

if ($DryRun) {
    Write-Host "[ProvisionSecrets] Dry run: all inputs resolved and gh authenticated; remote calls skipped." -ForegroundColor Cyan
    exit 0
}

Write-Host "[ProvisionSecrets] Setting secrets and variables on $Repo via gh CLI..." -ForegroundColor Cyan

$anyFailure = $false
$provisionResults = @{}
foreach ($name in $requiredSecrets) {
    Write-Host "  Setting secret $name..." -NoNewline
    $envVal = [Environment]::GetEnvironmentVariable($name)
    $envVal | & gh secret set $name -R $Repo
    if ($LASTEXITCODE -eq 0) {
        $provisionResults[$name] = "PROVISIONED"
        Write-Host " [OK]" -ForegroundColor Green
    } else {
        $provisionResults[$name] = "FAILED"
        $anyFailure = $true
        Write-Host " [FAILED]" -ForegroundColor Red
    }
}

$varResults = @{}
foreach ($name in $requiredVars) {
    Write-Host "  Setting variable $name..." -NoNewline
    & gh variable set $name -b "$($varValues[$name])" -R $Repo
    if ($LASTEXITCODE -eq 0) {
        $varResults[$name] = $varValues[$name]
        Write-Host " [OK]" -ForegroundColor Green
    } else {
        $varResults[$name] = "FAILED"
        $anyFailure = $true
        Write-Host " [FAILED]" -ForegroundColor Red
    }
}

# Evidence written only now - after the calls actually happened.
Write-Evidence -Status $(if ($anyFailure) { "PARTIAL_FAILURE" } else { "PROVISIONED" }) -SecretResults $provisionResults -VarResults $varResults

if ($anyFailure) { exit 1 }
Write-Host "[ProvisionSecrets] Secrets provisioning complete." -ForegroundColor Green
exit 0
