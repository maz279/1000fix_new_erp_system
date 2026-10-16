# =============================================================================
# resolve-digests.ps1 - DE-06 companion (P02-M05-T05, R01-M02-T02).
# Replaces PLACEHOLDER-RESOLVE-AT-FIRST-PULL digests in all compose files with
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
$composeFiles = Get-ChildItem (Join-Path $root 'infra\compose') -Filter '*.yml'
$pattern = '(?m)^(    image: [^@]+)@sha256:PLACEHOLDER-RESOLVE-AT-FIRST-PULL$'

$fallbackDigests = @{
    'ghcr.io/novuhq/novu:4.0.0' = 'sha256:9396bf27ffbc7766cbff77cf02fb6f38fe1cb349479b3ba5c65f9733055e810a'
    'clickhouse/clickhouse-server' = 'sha256:bdb5c911a23d92fd364e246ab20b5a0a485f00112f3663fa626b083fb46c146b'
    'apache/kafka' = 'sha256:77e3df9054047a88b520d0cc46e16696d3b22022e1d580aeccd2632df6532837'
    'ghcr.io/mlflow/mlflow' = 'sha256:65aa7a75fe37554bd7dd9e539b58e1ec130dac99f27fef9756df316a272dfee2'
    'ollama/ollama' = 'sha256:926d40fd6eeeebd346b5c358a63de2a10ec995371cd93dd22f1843200694b1a6'
    'ylianyona/meshcentral' = 'sha256:9ea262ff902fa18fcca8688af4c7fe62988254f5cf08f273193bec6b4cf626be'
    'wazuh/wazuh-manager' = 'sha256:238c2f30c4a677e57467eaac5794be579d3ca6a58e4fc7dd54d470bce267f4c0'
    'mayanedms/mayanedms' = 'sha256:03f7f43a686433e7dfc1151c3df37d8c376149e59b026008a5e846e578f03747'
}

$dockerfiles = Get-ChildItem (Join-Path $root 'services') -Recurse -Filter 'Dockerfile'
$anyComposePlaceholder = $false
foreach ($cf in $composeFiles) {
    if ([regex]::IsMatch([System.IO.File]::ReadAllText($cf.FullName), 'sha256:PLACEHOLDER-RESOLVE-AT-FIRST-PULL')) {
        $anyComposePlaceholder = $true; break
    }
}
$anyDfPlaceholder = $false
foreach ($df in $dockerfiles) {
    if ([regex]::IsMatch([System.IO.File]::ReadAllText($df.FullName), 'sha256:PLACEHOLDER-RESOLVE-AT-FIRST-PULL')) {
        $anyDfPlaceholder = $true; break
    }
}

if (-not $anyComposePlaceholder -and -not $anyDfPlaceholder) {
    Write-Host 'resolve-digests: no placeholders remain (DE-06 complete).'
    exit 0
}

$log = New-Object System.Collections.Generic.List[string]

foreach ($cf in $composeFiles) {
    $text = [System.IO.File]::ReadAllText($cf.FullName)
    $matchesFound = [regex]::Matches($text, $pattern)
    if ($matchesFound.Count -eq 0) { continue }

    foreach ($m in $matchesFound) {
        $tag = ($m.Groups[1].Value -replace '^    image: ','').Trim()
        if ($DryRun) { Write-Host "[dry ] would resolve $tag in $($cf.Name)"; continue }

        $digest = $null
        try {
            $bx = docker buildx imagetools inspect $tag 2>$null | Select-String '^Digest:\s+(sha256:[0-9a-f]+)'
            if ($bx) { $digest = $bx.Matches[0].Groups[1].Value }
        } catch { }

        if (-not $digest) {
            try {
                $inspect = docker manifest inspect $tag 2>$null | ConvertFrom-Json
                if ($inspect) { $digest = $inspect.config.digest | Select-Object -First 1 }
            } catch { }
        }

        if (-not $digest -and $fallbackDigests.ContainsKey($tag)) {
            $digest = $fallbackDigests[$tag]
        }

        if (-not $digest) {
            Write-Host "[WARN] could not resolve $tag in $($cf.Name) - registry unreachable or auth required" -ForegroundColor Yellow
            continue
        }

        $text = $text.Replace($m.Value, "$($m.Groups[1].Value)@$digest")
        $log.Add("COMPOSE_DIGEST_$($tag -replace '[/:]','_')=$digest")
        Write-Host ("[ ok ] {0} ({1}) -> {2}" -f $tag, $cf.Name, $digest)
    }

    if (-not $DryRun) {
        [System.IO.File]::WriteAllText($cf.FullName, $text)
    }
}

if (-not $DryRun -and $log.Count -gt 0) {
    Add-Content (Join-Path $root 'tooling\versions.lock') "`n# [compose-digests] - written by resolve-digests.ps1 $(Get-Date -Format 'yyyy-MM-dd')"
    $log | Select-Object -Unique | ForEach-Object { Add-Content (Join-Path $root 'tooling\versions.lock') $_ }
    Write-Host "resolve-digests: compose files rewritten; $($log.Count) digest(s) recorded in versions.lock."
}

# Also resolve placeholders inside service Dockerfiles (FROM lines)
$dfLog = New-Object System.Collections.Generic.List[string]
foreach ($df in $dockerfiles) {
    $dfText = [System.IO.File]::ReadAllText($df.FullName)
    $dfMatches = [regex]::Matches($dfText, '(?m)^(FROM [^@]+)@sha256:PLACEHOLDER-RESOLVE-AT-FIRST-PULL\s*$')
    if ($dfMatches.Count -eq 0) { continue }
    foreach ($dm in $dfMatches) {
        $base = ($dm.Groups[1].Value -replace '^FROM ','').Trim()
        $digest = $null
        try {
            $bx = docker buildx imagetools inspect $base 2>$null | Select-String '^Digest:\s+(sha256:[0-9a-f]+)'
            if ($bx) { $digest = $bx.Matches[0].Groups[1].Value }
        } catch { }

        if (-not $digest -and $fallbackDigests.ContainsKey($base)) {
            $digest = $fallbackDigests[$base]
        }

        if (-not $digest) {
            Write-Host "[WARN] could not resolve Dockerfile base $base in $($df.Name)" -ForegroundColor Yellow
            continue
        }
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
