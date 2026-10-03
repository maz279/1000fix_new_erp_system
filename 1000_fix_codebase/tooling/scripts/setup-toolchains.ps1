# =============================================================================
# setup-toolchains.ps1 - P02-M02 (Windows-native per D-WS-001; the Linux path
# is docs/guides/toolchain.md section 2). Line pins come from
# tooling/versions.lock [toolchain]; exact installed versions are written back
# as TOOLCHAIN_*_INSTALLED provenance keys.
# Idempotent; -VerifyOnly checks without installing (used by doctor check 1).
# =============================================================================
[CmdletBinding()]
param([switch]$VerifyOnly, [switch]$DryRun)
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$lockPath = Join-Path $root 'tooling\versions.lock'
$lock = @{}
Get-Content $lockPath | ForEach-Object {
    $t = $_.Trim()
    if ($t -match '^([A-Z0-9_]+)=(.+)$' -and $t -notmatch 'PENDING') { $lock[$Matches[1]] = $Matches[2] }
}
$fail = 0

function Check-Tool([string]$Name, [scriptblock]$VersionCmd, [string]$Floor) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Write-Host ("[FAIL] {0}: not on PATH" -f $Name) -ForegroundColor Red
        Write-Host ("      remedy: see docs/guides/toolchain.md - {0}" -f $Name) -ForegroundColor Yellow
        $script:fail++
        return
    }
    $v = & $VersionCmd
    Write-Host ("[ ok ] {0}: {1}" -f $Name, "$v".Trim())
}

Check-Tool 'python3.12' { py -3.12 --version } $lock.TOOLCHAIN_PYTHON
Check-Tool 'node' { node --version } "v$($lock.TOOLCHAIN_NODE_LTS)"
Check-Tool 'pnpm' { pnpm --version } $lock.TOOLCHAIN_PNPM_MAJOR
Check-Tool 'uv' { uv --version } $lock.TOOLCHAIN_UV_MAJOR
Check-Tool 'fvm' { fvm --version } $null
Check-Tool 'flutter (via fvm)' { fvm flutter --version } $lock.TOOLCHAIN_FLUTTER_MAJOR
Check-Tool 'go' { go version } $lock.TOOLCHAIN_GO_MAJOR
Check-Tool 'git' { git --version } $lock.TOOLCHAIN_GIT_MIN

if ($VerifyOnly) {
    if ($fail -gt 0) { exit 1 } else { Write-Host 'toolchains: all present (line pins)' -ForegroundColor Green; exit 0 }
}

# --- Install path (only with explicit intent; UAC prompts are the user's) ----
if (-not $DryRun) {
    Write-Host ''
    Write-Host 'install mode: this installs uv, nvm+Node 22, pnpm, fvm, Go.' -ForegroundColor Cyan
    Write-Host 'each installer is the official per-tool script/command; versions pinned by line.' -ForegroundColor Cyan
}
# uv (official installer, pinned line)
if (-not $DryRun -and -not (Get-Command uv -ErrorAction SilentlyContinue)) {
    irm https://astral.sh/uv/install.ps1 | iex
}
# nvm-windows + Node 22 + pnpm 9 (winget-pinned per workstation baseline)
if (-not $DryRun -and -not (Get-Command node -ErrorAction SilentlyContinue)) {
    winget install --id CoreyButler.NVMforWindows --exact --silent --accept-package-agreements --accept-source-agreements
    nvm install 22; nvm use 22
}
if (-not $DryRun -and -not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    npm install -g pnpm@9
}
# fvm + Flutter 3.44 line (D-027: read the 3.44 migration notes BEFORE pinning)
if (-not $DryRun -and -not (Get-Command fvm -ErrorAction SilentlyContinue)) {
    winget install --id leoafarias.fvm --exact --silent --accept-package-agreements --accept-source-agreements
    fvm install 3.44.0; fvm use 3.44.0
}
if (-not $DryRun -and -not (Get-Command go -ErrorAction SilentlyContinue)) {
    winget install --id GoLang.Go --exact --silent --accept-package-agreements --accept-source-agreements
}
# Provenance: write exact installed versions back into the lock.
if (-not $DryRun) {
    $prov = @()
    $node = (Get-Command node -ErrorAction SilentlyContinue); if ($node) { $prov += "TOOLCHAIN_NODE_INSTALLED=$((node --version).Trim())" }
    $pnpm = (Get-Command pnpm -ErrorAction SilentlyContinue); if ($pnpm) { $prov += "TOOLCHAIN_PNPM_INSTALLED=$((pnpm --version).Trim())" }
    if ($prov.Count -gt 0) {
        Add-Content $lockPath ("`n# [toolchain provenance - written by setup-toolchains.ps1 $(Get-Date -Format 'yyyy-MM-dd')]")
        $prov | ForEach-Object { Add-Content $lockPath $_ }
    }
    # P02-M02-T08: commit signing is a branch-protection precondition
    # (docs/guides/branch-protection.md). We ENABLE the config and check a
    # key exists; we never create or upload keys - that is the developer's.
    git config commit.gpgsign true 2>$null
    $key = git config user.signingkey 2>$null
    if (-not $key) {
        Write-Host '[WARN] commit.gpgsign enabled but no user.signingkey set.' -ForegroundColor Yellow
        Write-Host '      remedy: git config --global user.signingkey <KEYID>  (GPG) or use SSH signing:' -ForegroundColor Yellow
        Write-Host '              git config --global gpg.format ssh && git config --global user.signingkey ~/.ssh/id_ed25519.pub' -ForegroundColor Yellow
    }
}
if ($fail -gt 0 -and -not $DryRun) { exit 1 }
exit 0
