# =============================================================================
# resolve-digests.ps1 - DE-06 companion (P02-M05-T05).
# Replaces PLACEHOLDER-RESOLVE-AT-FIRST-PULL digests in the compose file with
# the real sha256 digests of the pinned tags, and records them in
# versions.lock [compose-digests]. After this runs, `docker compose config`
# is byte-reproducible - DE-06 completes (doctor/gate G0b-9 closes).
# Idempotent; requires the docker daemon (it inspects the registry, it does
# not run anything).
# =============================================================================
[CmdletBinding()]
param([switch]$DryRun)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$compose = Join-Path $root 'infra\compose\docker-compose.yml'
$text = [System.IO.File]::ReadAllText($compose)
$pattern = '(?m)^(    image: [^@]+)@sha256:PLACEHOLDER-RESOLVE-AT-FIRST-PULL$'
$matchesFound = [regex]::Matches($text, $pattern)
# P07 verification finding: the Dockerfiles carry the same DE-06 placeholders
# (FROM ...@sha256:PLACEHOLDER...) - the resolver only rewrote compose, so
# `compose up --build` failed on the residency stub. Dockerfiles resolve too.
$dockerfiles = Get-ChildItem (Join-Path $root 'services') -Recurse -Filter 'Dockerfile'
# The early exit must test whether any FILE still carries a placeholder,
# not merely whether Dockerfiles exist (audit finding: `$dockerfiles.Count
# -eq 0` is never true once the repo has Dockerfiles, so the DE-06-complete
# message never printed).
$anyDfPlaceholder = $false
foreach ($df in $dockerfiles) {
    if ([regex]::IsMatch([System.IO.File]::ReadAllText($df.FullName), 'sha256:PLACEHOLDER-RESOLVE-AT-FIRST-PULL')) { $anyDfPlaceholder = $true; break }
}
if ($matchesFound.Count -eq 0 -and -not $anyDfPlaceholder) { Write-Host 'resolve-digests: no placeholders remain (DE-06 complete).'; exit 0 }

$log = New-Object System.Collections.Generic.List[string]
foreach ($m in $matchesFound) {
    $tag = ($m.Groups[1].Value -replace '^    image: ','').Trim()
    if ($DryRun) { Write-Host "[dry ] would resolve $tag"; continue }
    # Resolution order (P07 verification finding: the old single path read
    # $inspect.config.digest, which is NULL for multi-arch manifest LISTS -
    # the shape nearly every pinned tag has - so every resolution "failed"):
    #   1. docker buildx imagetools inspect -> the INDEX digest (works for
    #      manifest lists AND single manifests; pull-by-index-digest picks
    #      the right platform at pull time)
    #   2. docker manifest inspect -> config.digest (single-arch fallback)
    $digest = $null
    # A registry 403/timeout (e.g. ghcr.io anonymous rate-limit) must SKIP
    # the image, never abort the run before the file rewrite - the digest
    # resolution is per-image best-effort with a WARN.
    try { $bx = docker buildx imagetools inspect $tag 2>$null | Select-String '^Digest:\s+(sha256:[0-9a-f]+)' } catch { $bx = $null }
    if ($bx) { $digest = $bx.Matches[0].Groups[1].Value }
    if (-not $digest) {
        try { $inspect = docker manifest inspect $tag 2>$null | ConvertFrom-Json } catch { $inspect = $null }
        if ($inspect) { $digest = $inspect.config.digest | Select-Object -First 1 }
    }
    if (-not $digest) { Write-Host "[WARN] could not resolve $tag - registry unreachable or auth required (ghcr.io needs a login for some packages)" -ForegroundColor Yellow; continue }
    $text = $text.Replace($m.Value, "$($m.Groups[1].Value)@$digest")
    $log.Add("COMPOSE_DIGEST_$($tag -replace '[/:]','_')=$digest")
    Write-Host ("[ ok ] {0} -> {1}" -f $tag, $digest)
}
if (-not $DryRun -and $log.Count -gt 0) {
    Add-Content (Join-Path $root 'tooling\versions.lock') "`n# [compose-digests] - written by resolve-digests.ps1 $(Get-Date -Format 'yyyy-MM-dd')"
    $log | ForEach-Object { Add-Content (Join-Path $root 'tooling\versions.lock') $_ }
    [System.IO.File]::WriteAllText($compose, $text)
    Write-Host "resolve-digests: compose file rewritten; $($log.Count) digests recorded in versions.lock."
}

# Resolve the same placeholders inside service Dockerfiles (FROM lines).
# Audit finding: the old loop appended the WHOLE $log per Dockerfile — every
# run tripled the DOCKERFILE_DIGEST rows. Now each Dockerfile contributes
# only its own entries, collected into $dfLog and written ONCE.
$dfLog = New-Object System.Collections.Generic.List[string]
foreach ($df in $dockerfiles) {
    $dfText = [System.IO.File]::ReadAllText($df.FullName)
    $dfMatches = [regex]::Matches($dfText, '(?m)^(FROM [^@]+)@sha256:PLACEHOLDER-RESOLVE-AT-FIRST-PULL\s*$')
    if ($dfMatches.Count -eq 0) { continue }
    foreach ($dm in $dfMatches) {
        $base = ($dm.Groups[1].Value -replace '^FROM ','').Trim()
        $digest = $null
        try { $bx = docker buildx imagetools inspect $base 2>$null | Select-String '^Digest:\s+(sha256:[0-9a-f]+)' } catch { $bx = $null }
        if ($bx) { $digest = $bx.Matches[0].Groups[1].Value }
        if (-not $digest) { Write-Host "[WARN] could not resolve Dockerfile base $base in $($df.Name)" -ForegroundColor Yellow; continue }
        $dfText = $dfText.Replace($dm.Value, "$($dm.Groups[1].Value)@$digest")
        $dfLog.Add("DOCKERFILE_DIGEST_$($base -replace '[/:]','_')=$digest")
        Write-Host ("[ ok ] {0} ({1}) -> {2}" -f $base, $df.Name, $digest)
    }
    if (-not $DryRun) { [System.IO.File]::WriteAllText($df.FullName, $dfText) }
}
if (-not $DryRun -and $dfLog.Count -gt 0) {
    $dfLog | Select-Object -Unique | ForEach-Object { Add-Content (Join-Path $root 'tooling\versions.lock') $_ }
    Write-Host "resolve-digests: $($dfLog.Count) Dockerfile digest(s) recorded in versions.lock."
}
exit 0
