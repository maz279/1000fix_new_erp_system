#!/usr/bin/env bash
# =============================================================================
# check-vendor-clean - FF-03 (AS-05): vendor/ is read-only to product
# developers. Any working-tree or staged modification under vendor/ must be
# authorised by a FORKS.yaml entry naming the path.
# Exit 0 clean/authorised - 1 unauthorised modification. DE-18: remedy printed.
# Runs: pre-commit (no-vendor-edit hook) + CI stage 9 (architecture).
# =============================================================================
set -euo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || { echo 'check-vendor-clean: not a git repository'; exit 1; })"

if [ ! -d vendor ]; then
  echo "check-vendor-clean: SKIP - vendor/ absent (run tooling/scripts/import-vendor.sh first)"
  exit 0
fi

changed=$(git status --porcelain -- vendor/ || true)
if [ -z "$changed" ]; then
  echo "check-vendor-clean: OK - vendor/ clean (FF-03)"
  exit 0
fi

# There are modifications. Each must be authorised by FORKS.yaml.
python - "$changed" <<'PY' || exit 1
import sys, re, pathlib
changed = sys.argv[1]
try:
    import yaml  # PyYAML ships with Odoo's constraints
    forks = (yaml.safe_load(pathlib.Path("FORKS.yaml").read_text()) or {}).get("forks") or []
except Exception:
    forks = []
authorised = []
for f in forks:
    repo = f.get("repo", "")
    p = f.get("path", "")
    if repo == "odoo":
        authorised.append(f"vendor/odoo/{p}".rstrip("/"))
    else:
        authorised.append(f"vendor/oca/{repo}/{p}".rstrip("/"))
unauth = []
for line in changed.splitlines():
    path = line[3:].strip().strip('"')
    if not any(path.startswith(a) for a in authorised):
        unauth.append(path)
if unauth:
    print("check-vendor-clean: FAIL - modifications under vendor/ with no FORKS.yaml entry:")
    for p in unauth:
        print(f"  {p}")
    print("  remedy: vendor/ is read-only (AS-05). Move the change into addons/, or add a")
    print("          FORKS.yaml entry WITH Design Authority approval (AR-007 5.4) and an exit plan.")
    sys.exit(1)
print(f"check-vendor-clean: OK - {len(unauth)==0} modifications, all FORKS.yaml-authorised")
PY
