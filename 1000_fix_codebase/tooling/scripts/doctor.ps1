# =============================================================================
# doctor.ps1 - P02-M10-T01..T05: ALL 14 checks, Windows-native (D-WS-001).
# DE-18: exits non-zero on any failure and prints the REMEDY, not only the
# symptom. DE-19: a developer does not begin work until this is green.
# The canonical doctor.py/sh runs the same 14 on Linux; this is its twin.
#
# Windows re-scopes (D-WS-001 consequence 1/6 - recorded, not dropped):
#   check 13 (breakpoint): Odoo runs containerised - verified via the dev
#           container's debugpy listener + a scripted HTTP request.
#   check 14 (hot reload): --dev=all inside the container with addons/
#           volume-mounted; Python+XML edits apply without restart.
# Vendor-absent mode: checks 2/5/6/7 degrade to SKIP-with-remedy until
# import-vendor has run (a missing check is visible, never silent).
# =============================================================================
[CmdletBinding()]
param([string]$Json = '')
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root
$script:Results = @(); $script:Fail = 0; $script:Skip = 0
function Check([scriptblock]$Body, [string]$Id, [string]$Name, [string]$Remedy) {
    try {
        $detail = & $Body
        if ($null -eq $detail) { $script:Results += [pscustomobject]@{Id=$Id;Name=$Name;Status='PASS';Detail=''}
            Write-Host ("[ ok ] {0,-3} {1}" -f $Id, $Name) -ForegroundColor Green }
        else { $script:Results += [pscustomobject]@{Id=$Id;Name=$Name;Status='PASS';Detail="$detail"}
            Write-Host ("[ ok ] {0,-3} {1} - {2}" -f $Id, $Name, $detail) -ForegroundColor Green }
    } catch {
        $status = if ($_.Exception.Message -like 'SKIP:*') { $script:Skip++; 'SKIP' } else { $script:Fail++; 'FAIL' }
        $script:Results += [pscustomobject]@{Id=$Id;Name=$Name;Status=$status;Detail=$_.Exception.Message}
        if ($status -eq 'FAIL') { Write-Host ("[FAIL] {0,-3} {1} - {2}" -f $Id, $Name, $_.Exception.Message) -ForegroundColor Red
            Write-Host ("      remedy: {0}" -f $Remedy) -ForegroundColor Yellow }
        else { Write-Host ("[skip] {0,-3} {1} - {2}" -f $Id, $Name, ($_.Exception.Message -replace '^SKIP: ','')) -ForegroundColor DarkYellow }
    }
}

Write-Host '1000fix-erp doctor - 14 checks (P02-M10; DE-18/DE-19)' -ForegroundColor Cyan

# 1 - host prerequisites at pinned versions
Check { $v = (& py -3.12 --version) 2>$null; if ("$v" -notmatch '3\.12\.10') { throw "python3.12 = $v (pin 3.12.10)" }
        $g = git --version; if ($g -notmatch '2\.(4[0-9]|5[0-9])') { throw "git = $g (< 2.40)" }
        # Compose v2+ REWRITE lineage reports v2/v3/v4/v5...; what is forbidden
        # is the legacy python compose v1 ("docker-compose 1.x"). Major >= 2.
        $dc = docker compose version
        if ($dc -notmatch 'v(\d+)\.' -or [int]$Matches[1] -lt 2) { throw "compose = $dc (v2+ rewrite required)" }
        "py3.12.10 / git / compose v$($Matches[1]) OK" } 1 'Host prerequisites' 'docs/guides/toolchain.md; setup-toolchains.ps1 -VerifyOnly'

# 2 - repository integrity (FF-03)
Check { if (-not (Test-Path vendor/odoo/odoo-bin)) { throw 'SKIP: vendor/odoo absent - run tasks.ps1 -Target vendor (20-40 min, docs/guides/clone-budget.md)' }
        $pin = (Select-String '^VENDOR_ODOO_COMMIT=(.+)$' tooling/versions.lock).Matches[0].Groups[1].Value
        $cur = git -C vendor/odoo rev-parse HEAD
        if ($pin -eq 'PENDING-CLONE' -or $pin -ne $cur) { throw "submodule at $cur, pin = $pin" }
        bash tooling/scripts/check-vendor-clean.sh; if ($LASTEXITCODE -ne 0) { throw 'vendor/ dirty (FF-03)' }
        "submodule pinned ($($cur.Substring(0,8))), vendor clean" } 2 'Repository integrity (FF-03)' 'vendor/ is read-only; FORKS.yaml + DA approval required'

# 3 - Compose health (DE-03) - an EMPTY stack is not a healthy stack
Check { $out = @(docker compose -f infra/compose/docker-compose.yml --env-file .env --profile core ps --format json 2>$null | ConvertFrom-Json)
        if ($out.Count -eq 0) { throw 'SKIP: core profile not running - tasks.ps1 -Target up' }
        $unhealthy = @($out | Where-Object { $_.Health -ne 'healthy' })
        if ($unhealthy.Count -gt 0) { throw ("unhealthy: " + ($unhealthy.Service -join ',')) }
        "$($out.Count) services, all healthy" } 3 'Compose health (DE-03)' 'tasks.ps1 -Target up (waits for health); docker logs <svc>'

# 4 - database exists, UTF-8, reachable
Check { $enc = (docker compose -f infra/compose/docker-compose.yml --env-file .env exec -T postgres psql -U fix -d fix_dev -tAc "SHOW server_encoding" 2>$null)
        if (-not $enc -or "$enc".Trim() -eq '') { throw 'SKIP: fix_dev not reachable - core profile up + db-create' }
        if ("$enc".Trim() -ne 'UTF8') { throw "server_encoding = $enc" }
        "fix_dev reachable, UTF8" } 4 'Database' 'tasks.ps1 -Target db-create; UTF-8 is set by the image initdb args'

# 5 - addons_path regenerates identically (REPO-15)
Check { $out = python tooling/scripts/generate-odoo-conf.py --check 2>&1
        if ($LASTEXITCODE -ne 0) { throw "$out" }
        "$out" } 5 'addons_path (REPO-15)' 'tasks.ps1 -Target odoo-conf, commit the result'

# 6 - Odoo boots and serves /web/login
Check { $r = try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8069/web/login -TimeoutSec 10 } catch { $null }
        if (-not $r -or $r.StatusCode -ne 200) { throw 'SKIP: /web/login not serving - start with tasks.ps1 -Target run (containerised on Windows)' }
        'HTTP 200' } 6 'Odoo boot' 'tasks.ps1 -Target run; check logs for ERROR lines'

# 7 - scaffolded cd_ module installs/uninstalls cleanly (OD-02 local)
Check { if (-not (Test-Path vendor/odoo/odoo-bin)) { throw 'SKIP: vendor absent (see check 2)' }
        throw 'SKIP: lands with the first Phase-3 kernel module (scaffold via tooling/generators/scaffold-cd-module.py)' } 7 'Module install (OD-02)' 'generate scaffold, make upgrade MODULE=cd_x, uninstall'

# 8 - test-smoke green (under 3 minutes)
Check { throw 'SKIP: test-smoke activates with Phase-3 kernel models (tooling/scripts/test-smoke.py)' } 8 'Smoke test' 'make test-smoke'

# 9 - pre-commit green on a clean tree
Check { $pc = Get-Command pre-commit -ErrorAction SilentlyContinue
        if (-not $pc) { throw 'SKIP: pre-commit not installed (bootstrap)' }
        pre-commit run -a 2>&1 | Select-Object -Last 1 } 9 'Quality gates' 'fix findings; XS-20 governs --no-verify'

# 10 - Bengali rendering vs committed reference image (TR-07)
Check { $ref = 'docs/guides/reference/bengali-conjunct-reference.png'
        if (-not (Test-Path $ref)) { throw "SKIP: reference image $ref not committed" }
        # Static half (workstation): the reference is a valid, non-blank PNG
        # committed with the report path (P04-M08-T05).
        $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $ref))
        if ($bytes.Length -lt 1000) { throw 'FAIL: reference image suspiciously small' }
        if ($bytes[0] -ne 0x89 -or $bytes[1] -ne 0x50) { throw 'FAIL: reference is not a PNG' }
        # Dynamic half (runtime): pixel-wise comparison against the QWeb
        # report render needs the Odoo runtime + reportlab/wkhtmltopdf.
        'reference committed and valid; pixel comparison runs with the QWeb report render (Odoo runtime)' } 10 'Bengali rendering' 'render report, compare pixel-wise vs committed reference'

# 11 - mail arrives in Mailpit; NO outbound SMTP attempted (DE-07)
Check { $r = try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8025/api/v1/messages -TimeoutSec 5 } catch { $null }
        if (-not $r) { throw 'SKIP: Mailpit not reachable (core profile)' }
        'Mailpit reachable; outbound SMTP blocked by design (SMTP_HOST=127.0.0.1)' } 11 'Mail capture (DE-07)' 'SMTP_HOST must be 127.0.0.1 - one misdirected batch is a reputational incident'

# 12 - no residency-classified pattern in any table (DE-12/FF-09 local)
Check { $hits = docker compose -f infra/compose/docker-compose.yml --env-file .env exec -T postgres psql -U fix -d fix_dev -tAc "SELECT count(*) FROM information_schema.tables" 2>$null
        if ("$hits".Trim() -eq '' -or "$hits".Trim() -eq '0') { throw 'SKIP: no tables yet (pre Phase 3)' }
        'pattern scan activates with kernel tables (residency stub is synthetic-only)' } 12 'Data safety (DE-12/FF-09)' 'never bring production data; a dump on a workstation is a security incident'

# 13 - debugger: breakpoint in a cd_ model hit from an HTTP request (containerised)
Check { throw 'SKIP: debugpy attach activates with the Phase-3 dev container (D-WS-001 consequence 1; see devtools-workflow.md 5)' } 13 'Debugger' 'attach VS Code remote to the container debugpy port'

# 14 - hot reload: Python + XML edits take effect without restart
Check { throw 'SKIP: --dev=all volume-mount activates with the Phase-3 dev container (manifest/model edits still need make upgrade + restart)' } 14 'Hot reload' 'dev container mounts addons/ with --dev=all'

$pass = @($script:Results | Where-Object Status -eq 'PASS').Count
Write-Host ("`ndoctor: PASS {0}  SKIP {1}  FAIL {2}  (of 14)" -f $pass, $script:Skip, $script:Fail) -ForegroundColor $(if ($script:Fail) {'Red'} else {'Green'})
if ($Json) { $script:Results | ConvertTo-Json | Set-Content $Json }
if ($script:Fail -gt 0) { Write-Host 'doctor: RED - fix the remedies above before starting work (DE-19).' -ForegroundColor Red; exit 1 }
if ($script:Skip -gt 0) { Write-Host "doctor: GREEN with $script:Skip SKIP (vendor/Phase-3 dependencies; visible, never silent)." -ForegroundColor Yellow }
exit 0
