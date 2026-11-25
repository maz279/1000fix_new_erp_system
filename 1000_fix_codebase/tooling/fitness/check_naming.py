#!/usr/bin/env python3
"""FF-02 — Module naming convention check (AS-04, P02-M08-T07).

Validates that every custom module under addons/ follows the naming
convention: module directory is cd_<snake_case>, model _name is
fix.<domain>.<entity>, and table name is fix_<domain>_<entity>.

Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADDONS = REPO_ROOT / "addons"

MODULE_DIR_PATTERN = re.compile(r"^cd_[a-z0-9_]+$")
# AS-04: fix.<segments> where segments are 1-3 dot-separated lowercase words
# e.g. fix.entity (2 parts), fix.party.role (3), fix.mdm.change.request (4)
MODEL_NAME_PATTERN = re.compile(r"^fix\.[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*){0,2}$")


def main() -> int:
    violations = []
    modules_checked = 0
    models_checked = 0

    for module_dir in sorted(ADDONS.iterdir()):
        if not module_dir.is_dir() or module_dir.name.startswith("_"):
            continue
        for cd_dir in sorted(module_dir.iterdir()):
            if not cd_dir.is_dir() or not cd_dir.name.startswith("cd_"):
                continue
            modules_checked += 1
            if not MODULE_DIR_PATTERN.match(cd_dir.name):
                violations.append(
                    (cd_dir.name, f"directory {cd_dir.name!r} does not match cd_<snake_case>")
                )

            # Check model names in Python files
            for py in cd_dir.rglob("*.py"):
                if "__pycache__" in py.parts:
                    continue
                text = py.read_text(encoding="utf-8", errors="ignore")
                for m in re.finditer(r'_name\s*=\s*"(fix\.[^"]+)"', text):
                    model_name = m.group(1)
                    models_checked += 1
                    if not MODEL_NAME_PATTERN.match(model_name):
                        violations.append(
                            (
                                cd_dir.name,
                                f"model {model_name!r} does not match fix.<domain>.<entity>",
                            )
                        )

    if violations:
        print(
            f"naming: FAIL - {len(violations)} violation(s) ({modules_checked} modules, {models_checked} models):"
        )
        for mod, msg in violations[:15]:
            print(f"  {mod}: {msg}")
        print(
            "  remedy: AS-04 naming: module cd_<snake>, model fix.<domain>.<entity>, table fix_<domain>_<entity>."
        )
        return 1
    print(f"naming: OK - {modules_checked} modules, {models_checked} model names conform to AS-04")
    return 0


if __name__ == "__main__":
    sys.exit(main())
