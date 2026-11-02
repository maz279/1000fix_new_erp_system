import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
log_dir = os.path.join(root, "results", "portals")
os.makedirs(log_dir, exist_ok=True)

portals = [
    ("corporate", 3001),
    ("analytics", 3002),
    ("seller", 3003),
    ("brand", 3004),
    ("agent-console", 3005),
    ("partner", 3006),
    ("vendor", 3007),
]

# Detached process flag for Windows
DETACHED_PROCESS = 0x00000008

for name, port in portals:
    app_dir = os.path.join(root, "apps", "web", name)
    log_file = os.path.join(log_dir, f"{name}.log")
    if os.path.exists(app_dir):
        print(f"Launching {name} on port {port}...")
        with open(log_file, "w", encoding="utf-8") as out:
            p = subprocess.Popen(
                ["cmd.exe", "/c", "npm.cmd", "run", "dev"],
                cwd=app_dir,
                stdout=out,
                stderr=out,
                creationflags=DETACHED_PROCESS,
                close_fds=True,
            )
        print(f"  Started {name} (PID: {p.pid})")

# Launch Front_end static prototype on 8085
fe_dir = "c:\\software_project\\software_project_14\\1000 fix\\1000fix_new_erp_system\\Front_end"
fe_log = os.path.join(log_dir, "front_end_static.log")
py_exe = os.path.join(root, ".venv", "Scripts", "python.exe")
if os.path.exists(fe_dir):
    print("Launching Front_end static prototype on port 8085...")
    with open(fe_log, "w", encoding="utf-8") as out:
        p = subprocess.Popen(
            [py_exe, "-m", "http.server", "8085", "--bind", "127.0.0.1"],
            cwd=fe_dir,
            stdout=out,
            stderr=out,
            creationflags=DETACHED_PROCESS,
            close_fds=True,
        )
    print(f"  Started Front_end prototype (PID: {p.pid})")

print("All daemon portals launched successfully!")
