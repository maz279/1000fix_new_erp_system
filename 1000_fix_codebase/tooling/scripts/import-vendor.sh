#!/usr/bin/env bash
# =============================================================================
# import-vendor.ps1 runs this on Git Bash / Linux CI. Kept as .sh so the same
# vendoring runs everywhere; the PowerShell entry point orchestrates on Windows.
# P02-M04-T01/T02 - Odoo submodule + OCA subtrees, pinned from versions.lock.
#
# Layout (single-repo): the git repository root is the WORKSPACE
# (1000fix_new_erp_system/, connected to GitHub); the ERP tree lives in the
# 1000_fix_codebase/ subdirectory. The lock file and the vendor/ tree are
# resolved relative to THIS SCRIPT (codebase), while every git operation runs
# at the repository toplevel with codebase-relative pathspecs.
# =============================================================================
set -euo pipefail

script_dir=$(cd "$(dirname "$0")" && pwd)
code_root=$(cd "$script_dir/../.." && pwd)
git_root=$(git -C "$code_root" rev-parse --show-toplevel)
cd "$git_root"
# Path of the codebase relative to the repository root (e.g. 1000_fix_codebase).
# rev-parse --show-prefix is used because Git for Windows prints --show-toplevel
# in D:/ style while $(pwd) is /d/ style; stripping one from the other silently
# fails and yields an absolute path that mangles .git/modules.
rel=$(git -C "$code_root" rev-parse --show-prefix)
rel=${rel%/}

get_lock() { grep -m1 "^$1=" "$code_root/tooling/versions.lock" | cut -d= -f2; }

ODOO_URL=$(get_lock VENDOR_ODOO_URL)
ODOO_BRANCH=$(get_lock VENDOR_ODOO_BRANCH)

# --- T01: Odoo as a submodule, pinned commit on branch 19.0 -------------------
# Windows prerequisite: core.longpaths=true (Odoo paths exceed MAX_PATH;
# checkout fails with "Filename too long" without it).
# NOTE: git writes .gitmodules at the REPOSITORY ROOT, never beside the tree.
gm="$git_root/.gitmodules"
if [ ! -f "$gm" ] || ! grep -q 'vendor/odoo' "$gm"; then
  git submodule add -b "$ODOO_BRANCH" "$ODOO_URL" "$rel/vendor/odoo"
fi
git -C "$rel/vendor/odoo" fetch origin "$ODOO_BRANCH"
PIN=$(get_lock VENDOR_ODOO_COMMIT)
if [ "$PIN" = "PENDING-CLONE" ]; then
  PIN=$(git -C "$rel/vendor/odoo" rev-parse "origin/$ODOO_BRANCH")
  echo "import-vendor: resolved Odoo pin -> $PIN (recorded back to versions.lock)"
  sed -i "s|^VENDOR_ODOO_COMMIT=.*|VENDOR_ODOO_COMMIT=$PIN|" "$code_root/tooling/versions.lock"
fi
git -C "$rel/vendor/odoo" checkout --quiet "$PIN"

# P07 audit finding: `git subtree add` refuses a dirty tree. On a FRESH run the
# Odoo phase has just staged the submodule gitlink + .gitmodules and rewritten
# the pin in versions.lock, so the OCA phase below always aborted with
# "working tree has modifications. Cannot add." Commit the Odoo registration
# before the subtree loop (idempotent - nothing to commit on re-runs).
if [ -n "$(git status --porcelain)" ]; then
  git add "$gm" "$rel/vendor/odoo" "$code_root/tooling/versions.lock"
  git commit -m "chore(repo): vendor - Odoo submodule pinned ${PIN:0:10} (import-vendor T01)"
fi

# --- T02-T05: OCA subtrees, whole, own structure retained ----------------------
OCA_ORG=$(get_lock VENDOR_OCA_ORG)
# NOTE: there is NO OCA/l10n-bangladesh repository (P07 finding: the import
# died on the phantom entry). Bangladesh localisation ships inside Odoo core
# (vendor/odoo/addons/l10n_bd, covered by the submodule pin); the statutory
# layer on top is first-party cd_tax_engine_bd.
REPOS="field-service helpdesk management-system operating-unit hr payroll dms \
server-tools web account-financial-tools account-financial-reporting \
reporting-engine mis-builder stock-logistics-workflow stock-logistics-barcode \
stock-logistics-warehouse purchase-workflow partner-contact contract"

# P07 audit finding #2: recording pins INSIDE the loop (sed) left versions.lock
# dirty, and the NEXT `git subtree add` aborted on the dirty tree after the very
# first repo. Pins are collected and written once, after the loop - including
# for repos that are already present but still PENDING-CLONE (a previous run
# that died mid-loop would otherwise never record them).
pin_updates=""
for repo in $REPOS; do
  key="VENDOR_OCA_$(echo "$repo" | tr '[:lower:]-' '[:upper:]_')"
  dir="$rel/vendor/oca/$repo"
  if [ -d "$dir" ] && [ -n "$(ls -A "$dir" 2>/dev/null)" ]; then
    echo "import-vendor: $repo already present - skipping"
  else
    echo "import-vendor: subtree add $repo (19.0)"
    git subtree add --prefix "$dir" "$OCA_ORG/$repo" 19.0 --squash
  fi
  cur=$(get_lock "$key")
  if [ "$cur" = "PENDING-CLONE" ]; then
    pin=$(git log -1 --format=%H "--" "$dir" 2>/dev/null || true)
    if [ -n "$pin" ]; then
      pin_updates+="s|^$key=.*|$key=$pin|\n"
    fi
  fi
done
if [ -n "$pin_updates" ]; then
  sed -i "$(printf '%b' "$pin_updates")" "$code_root/tooling/versions.lock"
  echo "import-vendor: OCA pins recorded in versions.lock"
  git add "$code_root/tooling/versions.lock"
  git commit -m "chore(repo): vendor - OCA subtree pins recorded (import-vendor T02-T05)" || true
fi

echo "import-vendor: done. Verify with: tooling/scripts/check-vendor-clean.sh"
