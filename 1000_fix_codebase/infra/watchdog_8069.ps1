# 8069 estate watchdog — updated 2026-11-10. Same contract as the
# original supervisor: poll the port, (re)start Odoo when it drops, never
# run two. Crash-proof: every probe wrapped so an empty result can never
# kill the loop.
#
# 2026-11-10: the estate port now serves fix_real (the real-data estate —
# CIH take-on, bank master, users, chart). fix_dev remains served on 8090
# (its own watchdog) and fix_real is also mirrored on 8089. User directive:
# all implemented work must be visible at http://127.0.0.1:8069.
$root = "c:\software_project\software_project_14\1000 fix\1000fix_new_erp_system\1000_fix_codebase"
$py = "C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe"

Write-Host "Odoo 8069 (fix_real) supervisor starting..."
$env:PYTHONPATH = "$root;$root\vendor\odoo"

while ($true) {
    $alive = $false
    try {
        $conns = Get-NetTCPConnection -LocalPort 8069 -ErrorAction SilentlyContinue
        if ($conns) { $alive = $true }
    } catch {
        $alive = $false
    }
    if (-not $alive) {
        Write-Host "Odoo port 8069 not active, starting Odoo (fix_real)..."
        try {
            $proc = Start-Process -FilePath $py -ArgumentList "vendor/odoo/odoo-bin", "-c", "infra/odoo-conf/local.resolved.conf", "-d", "fix_real", "--http-port=8069", "--logfile=C:\cih_8069.log" -WorkingDirectory $root -NoNewWindow -PassThru
            Write-Host "Spawned Odoo 8069 (fix_real) process PID $($proc.Id)"
        } catch {
            Write-Host "Spawn failed: $($_.Exception.Message)"
        }
    }
    Start-Sleep -Seconds 15
}
