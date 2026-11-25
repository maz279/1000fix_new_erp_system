#!/usr/bin/env python3
"""FF-23 — Test presence check (P02-M08-T07, stage 4 companion).

Verifies that every module under addons/ has a tests/ directory with at
least one test file. A module without tests is a module nobody can change
safely — and DoD-03 requires >= 80% coverage (100% financial/tax).

Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADDONS = REPO_ROOT / "addons"


def main() -> int:
    violations = []
    modules_checked = 0

    # Find all cd_* modules at any nesting level under addons/
    # (platform modules are at addons/platform/cd_*, domain at addons/domain/<category>/cd_*)
    for cd_dir in sorted(ADDONS.rglob("cd_*")):
        if not cd_dir.is_dir():
            continue  # files named cd_* (data XML etc.) are not modules
        if "__pycache__" in cd_dir.parts:
            continue
        modules_checked += 1
        if not (cd_dir / "__manifest__.py").is_file():
            violations.append(
                (
                    str(cd_dir.relative_to(REPO_ROOT)),
                    "matches cd_* but has no __manifest__.py (stray scaffold?)",
                )
            )
            continue
        tests_dir = cd_dir / "tests"
        if not tests_dir.is_dir():
            violations.append((cd_dir.name, "no tests/ directory"))
            continue
        test_files = list(tests_dir.glob("test_*.py"))
        if not test_files:
            violations.append((cd_dir.name, "tests/ exists but contains no test_*.py files"))

    if violations:
        print(
            f"tests-present: FAIL - {len(violations)} module(s) without tests ({modules_checked} checked):"
        )
        for mod, msg in violations:
            print(f"  {mod}: {msg}")
        print(
            "  remedy: every module ships a tests/ directory with test_*.py (DoD-03 requires >= 80% coverage)."
        )
        return 1
    print(f"tests-present: OK - {modules_checked} modules, all have tests/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
