#!/usr/bin/env bash
# =============================================================================
# import-vendor.ps1 runs this on Git Bash / Linux CI. Kept as .sh so the same
# vendoring runs everywhere; the PowerShell entry point orchestrates on Windows.
# P02-M04-T01/T02 - Odoo submodule + OCA subtrees, pinned from versions.lock.
# =============================================================================
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

get_lock() { grep -m1 "^$1=" tooling/versions.lock | cut -d= -f2; }

ODOO_URL=$(get_lock VENDOR_ODOO_URL)
ODOO_BRANCH=$(get_lock VENDOR_ODOO_BRANCH)

# --- T01: Odoo as a submodule, pinned commit on branch 19.0 -------------------
if [ ! -f .gitmodules ] || ! grep -q 'vendor/odoo' .gitmodules; then
  git submodule add -b "$ODOO_BRANCH" "$ODOO_URL" vendor/odoo
fi
git -C vendor/odoo fetch origin "$ODOO_BRANCH"
PIN=$(get_lock VENDOR_ODOO_COMMIT)
if [ "$PIN" = "PENDING-CLONE" ]; then
  PIN=$(git -C vendor/odoo rev-parse "origin/$ODOO_BRANCH")
  echo "import-vendor: resolved Odoo pin -> $PIN (recorded back to versions.lock)"
  sed -i "s|^VENDOR_ODOO_COMMIT=.*|VENDOR_ODOO_COMMIT=$PIN|" tooling/versions.lock
fi
git -C vendor/odoo checkout --quiet "$PIN"

# P07 audit finding: `git subtree add` refuses a dirty tree. On a FRESH run the
# Odoo phase has just staged the submodule gitlink + .gitmodules and rewritten
# the pin in versions.lock, so the OCA phase below always aborted with
# "working tree has modifications. Cannot add." Commit the Odoo registration
# before the subtree loop (idempotent - nothing to commit on re-runs).
if [ -n "$(git status --porcelain)" ]; then
  git add .gitmodules vendor/odoo tooling/versions.lock
  git commit -m "chore(repo): vendor - Odoo submodule pinned ${PIN:0:10} (import-vendor T01)"
fi

# --- T02-T05: OCA subtrees, whole, own structure retained ----------------------
OCA_ORG=$(get_lock VENDOR_OCA_ORG)
REPOS="field-service helpdesk management-system operating-unit hr payroll dms \
server-tools web account-financial-tools account-financial-reporting \
reporting-engine mis-builder stock-logistics-workflow stock-logistics-barcode \
stock-logistics-warehouse purchase-workflow partner-contact contract \
l10n-bangladesh"

for repo in $REPOS; do
  key="VENDOR_OCA_$(echo "$repo" | tr '[:lower:]-' '[:upper:]_')"
  dir="vendor/oca/$repo"
  if [ -d "$dir" ] && [ -n "$(ls -A "$dir" 2>/dev/null)" ]; then
    echo "import-vendor: $repo already present - skipping"
    continue
  fi
  echo "import-vendor: subtree add $repo (19.0)"
  git subtree add --prefix "$dir" "$OCA_ORG/$repo" 19.0 --squash
  pin=$(git log -1 --format=%H "--" "$dir" 2>/dev/null || true)
  cur=$(get_lock "$key")
  if [ "$cur" = "PENDING-CLONE" ]; then
    sed -i "s|^$key=.*|$key=$pin|" tooling/versions.lock || true
  fi
done

echo "import-vendor: done. Verify with: tooling/scripts/check-vendor-clean.sh"
