# 8090 estate watchdog - fix_dev developer estate, created 2026-11-10.
# Same contract as watchdog_8069.ps1: poll the port, (re)start Odoo when it
# drops, never run two. Companion to the 2026-11-10 estate change: 8069 now
# serves fix_real (the real-data estate); fix_dev lives here on 8090.
$root = "c:\software_project\software_project_14\1000 fix\1000fix_new_erp_system\1000_fix_codebase"
$py = "C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe"

Write-Host "Odoo 8090 (fix_dev) supervisor starting..."
$env:PYTHONPATH = "$root;$root\vendor\odoo"

while ($true) {
    $alive = $false
    try {
        $conns = Get-NetTCPConnection -LocalPort 8090 -ErrorAction SilentlyContinue
        if ($conns) { $alive = $true }
    } catch {
        $alive = $false
    }
    if (-not $alive) {
        Write-Host "Odoo port 8090 not active, starting Odoo (fix_dev)..."
        try {
            $proc = Start-Process -FilePath $py -ArgumentList "vendor/odoo/odoo-bin", "-c", "infra/odoo-conf/local.resolved.conf", "-d", "fix_dev", "--http-port=8090", "--logfile=`"$root\infra\odoo-data\fixdev_8090.log`"" -WorkingDirectory $root -NoNewWindow -PassThru
            Write-Host "Spawned Odoo 8090 (fix_dev) process PID $($proc.Id)"
        } catch {
            Write-Host "Spawn failed: $($_.Exception.Message)"
        }
    }
    Start-Sleep -Seconds 15
}
