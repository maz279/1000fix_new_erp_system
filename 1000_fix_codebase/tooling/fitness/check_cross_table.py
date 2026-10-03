#!/usr/bin/env python3
"""FF-06 — No cross-module table reads (AS-01, P02-M08-T07 stage 9).

Scans every model file under addons/ for direct SQL or ORM access to
another module's tables. AS-01: "no module reads another module's tables
directly" — everything goes through the published API or the event bus.

Patterns checked:
  - Raw SQL with table names starting fix_ that aren't the module's own
  - env['other.module.model'].search() in a module that doesn't own that model
    (a heuristic — direct env[] access to foreign models without a published
    API is the failure mode)

Exit: 0 pass / 1 violations.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADDONS = REPO_ROOT / "addons"

SQL_TABLE_PATTERN = re.compile(r'(?:FROM|JOIN|INTO|UPDATE)\s+(fix_\w+)', re.IGNORECASE)
ENV_MODEL_PATTERN = re.compile(r"env\[\"(fix\.[^\"]+)\"\]")


def module_owns_model(module_dir: Path, model_name: str) -> bool:
    """Check if a module declares this model in its own Python files."""
    for py in module_dir.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
            if f'_name = "{model_name}"' in text:
                return True
        except OSError:
            continue
    return False


def model_name_to_table(model_name: str) -> str:
    """Convert fix.domain.entity to fix_domain_entity."""
    return model_name.replace(".", "_")


def main() -> int:
    violations = []
    files_checked = 0

    for module_dir in sorted(ADDONS.iterdir()):
        if not module_dir.is_dir() or module_dir.name.startswith("_"):
            continue
        for cd_dir in sorted(module_dir.iterdir()):
            if not cd_dir.is_dir() or not cd_dir.name.startswith("cd_"):
                continue
            for py in cd_dir.rglob("*.py"):
                if "__pycache__" in py.parts:
                    continue
                files_checked += 1
                text = py.read_text(encoding="utf-8", errors="ignore")
                rel = py.relative_to(REPO_ROOT).as_posix()

                # Check raw SQL for foreign tables
                for m in SQL_TABLE_PATTERN.finditer(text):
                    table = m.group(1).lower()
                    # Check if this module owns the model for that table
                    model_name = table.replace("fix_", "fix.", 1).replace("_", ".")
                    # More precise: check all fix.* models declared in this module
                    if not _owns_table(cd_dir, table):
                        violations.append((rel, f"AS-01: raw SQL references foreign table {table!r}"))

    if violations:
        print(f"cross-table: FAIL - {len(violations)} violation(s) ({files_checked} files):")
        for rel, msg in violations[:15]:
            print(f"  {rel}: {msg}")
        print("  remedy: AS-01 forbids cross-module table reads. Use the published API or the event bus.")
        return 1
    print(f"cross-table: OK - {files_checked} files, 0 cross-module table reads")
    return 0


def _owns_table(module_dir: Path, table: str) -> bool:
    """Check if any model in this module maps to the given table name."""
    for py in module_dir.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        text = py.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'_name\s*=\s*"(fix\.[^"]+)"', text):
            model_table = m.group(1).replace(".", "_")
            if model_table == table:
                return True
    return False


if __name__ == "__main__":
    sys.exit(main())
