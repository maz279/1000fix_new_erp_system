#!/usr/bin/env python3
"""check-expansion-static — the workstation half of P04-M06-T08 / P04-M08-T09.

Bengali runs typically 15-30% longer than English (UX-007 §expansion). Two
things are checkable WITHOUT a browser, and both are enforced here:

  1. Budget: every inline-bilingual UI-copy key fits its declared character
     budget in BOTH locales (VB-002). The extractor checks this at generation
     time; this check guards against hand edits to the generated registry.
  2. No silent clipping: Odoo views and design-system components must not use
     truncation (text-truncate / ellipsis / o_text_overflow) on translatable
     labels — an ellipsised Bengali status is a wrong status (MD-027).

The dynamic half (render both locales in a real browser, assert no overflow)
lives in tooling/a11y/tests/expansion.spec.ts and runs where a renderer
exists (CI stage 12, or locally with the compose stack up).

Exit: 0 pass / 1 violations.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "libs/ts/i18n/src/ui-copy.generated.json"
SCAN_ROOTS = [REPO / "addons", REPO / "libs/ts/ui/src/components"]

TRUNCATION = re.compile(
    r"text-truncate|o_text_overflow|text-overflow:\s*ellipsis|white-space:\s*nowrap"
)
# Attrs that legitimately nowrap (non-translatable chrome): icons, numerics.
ALLOWED_NOWRAP_CONTEXT = re.compile(r"widget=\"(?:badge|boolean|progressbar)\"")


def check_budgets() -> list[str]:
    violations: list[str] = []
    doc = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for pack_id, pack in doc["packs"].items():
        for entry in pack["copy"]:
            if entry["bn_status"] != "inline":
                continue
            budget = entry.get("max")
            if budget is None:
                continue
            for side in ("en", "bn"):
                length = len(entry[side] or "")
                if length > budget:
                    violations.append(
                        f"{pack_id}/{entry['key']}: {side} {length} > budget {budget}"
                    )
    return violations


def check_no_clipping() -> list[str]:
    violations: list[str] = []
    for root in SCAN_ROOTS:
        if not root.is_dir():
            continue
        for path in list(root.rglob("*.xml")) + list(root.rglob("*.scss")):
            if "__pycache__" in path.parts or "vendor" in path.parts or "i18n" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for line_no, line in enumerate(text.splitlines(), 1):
                hit = TRUNCATION.search(line)
                if not hit:
                    continue
                if ALLOWED_NOWRAP_CONTEXT.search(line):
                    continue
                rel = path.relative_to(REPO)
                violations.append(
                    f"{rel}:{line_no}: truncation on a translatable surface ({hit.group()})"
                    .replace("\\", "/")
                )
    return violations


def main() -> int:
    if not REGISTRY.is_file():
        print("expansion-static: FAIL - generated UI-copy registry missing "
              "(run tooling/scripts/extract-ui-copy.py)")
        return 1
    budget_failures = check_budgets()
    clipping = check_no_clipping()
    doc = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if budget_failures or clipping:
        print(f"expansion-static: FAIL - {len(budget_failures)} budget / {len(clipping)} clipping issue(s):")
        for v in budget_failures + clipping:
            print(f"  {v}")
        return 1
    print(f"expansion-static: OK - budgets hold across {doc['total_keys']} keys; "
          f"no truncation on translatable surfaces "
          f"({doc['counterpart_pending']} keys await BN counterparts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
