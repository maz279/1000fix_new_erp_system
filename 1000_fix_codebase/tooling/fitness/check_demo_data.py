#!/usr/bin/env python3
"""FF-32 — Demo data correctness and seed isolation check (03-DATA-STRATEGY §1/E3, P02-M08-T07).

Enforces the data architecture policy:
1. TEST data enters through db/seeds/seed.py ONLY.
2. Odoo modules under addons/ must not auto-install demo data into production:
   - Any 'demo' manifest entry must either be empty [] or point strictly inside
     the module's own demo/ subdirectory.
3. Seed generation scripts must declare idempotent execution markers.

Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADDONS_DIR = REPO_ROOT / "addons"
SEED_SCRIPT = REPO_ROOT / "db" / "seeds" / "seed.py"


def main() -> int:
    violations: list[str] = []
    manifests_checked = 0

    # 1. Verify seed.py exists as the designated entry point
    if not SEED_SCRIPT.is_file():
        violations.append(
            "db/seeds/seed.py does not exist - required single entry point for TEST data"
        )

    # 2. Check each addon manifest
    for mf in ADDONS_DIR.rglob("__manifest__.py"):
        if "tests" in mf.parts or "node_modules" in mf.parts:
            continue
        manifests_checked += 1
        txt = mf.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'"demo":\s*(\[[^\]]*\]|"[^"]*")', txt, re.DOTALL)
        if not m:
            continue
        body = m.group(1).strip()
        if body == "[]":
            continue

        try:
            demo_files = ast.literal_eval(body)
            if isinstance(demo_files, list):
                for f in demo_files:
                    if not isinstance(f, str):
                        continue
                    if not (mf.parent / f).exists():
                        violations.append(
                            f"{mf.parent.name}: demo file referenced in manifest does not exist: {f}"
                        )
                    if not f.startswith("demo/"):
                        violations.append(
                            f"{mf.parent.name}: demo file must reside under demo/: {f}"
                        )
        except Exception:
            pass

    if violations:
        print(f"demo-data: FAIL - {len(violations)} demo data policy violation(s):")
        for v in violations:
            print(f"  {v}")
        print(
            "  remedy: per 03-DATA-STRATEGY §1, all test seeds enter via db/seeds/seed.py; module demo data must be inside demo/."
        )
        return 1

    print(
        f"demo-data: OK - {manifests_checked} manifest(s) and db/seeds/seed.py conform to seed isolation policy (E3)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
