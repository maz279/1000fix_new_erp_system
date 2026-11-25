#!/usr/bin/env python3
"""FF-09 — Residency single-client check (P03-M09-T07, blocking from first build).

Scans every Python file under addons/ and services/ for imports or references
to the residency service that do NOT go through libs/py/fix_residency.
Any direct Z4 access path fails this check.

Exit: 0 pass / 1 violations (blocking — a residency leak is a notifiable event).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = [REPO_ROOT / "addons", REPO_ROOT / "services"]

BYPASS_PATTERNS = [
    (re.compile(r"127\.0\.0\.1:8100|residency[-_]stub"), "direct residency-service URL reference"),
    (re.compile(r"psycopg[^\n]*8100|5433"), "direct database connection on the residency port"),
    (
        re.compile(r"from\s+(?!libs\.py\.fix_residency)\S*fix_residency\s+import"),
        "fix_residency imported from a non-canonical path",
    ),
]

EXEMPT = {
    "services/local-residency-stub/app.py",
    # Tests of the CANONICAL client against the live local stub: the loopback
    # literal here is the probe target, not a classified-field access path
    # (R01 re-audit 2026-10-22 - every src-level hit routes through
    # libs/py/fix_residency).
    "services/dsr-orchestrator/tests/test_dsr_residency_client.py",
}


def main() -> int:
    violations: list[tuple[str, int, str]] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for py in root.rglob("*.py"):
            rel = py.relative_to(REPO_ROOT).as_posix()
            if rel in EXEMPT:
                continue
            try:
                text = py.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                for pattern, description in BYPASS_PATTERNS:
                    if pattern.search(line):
                        violations.append((rel, lineno, f"{description}: {line.strip()[:120]}"))

    if violations:
        print(f"FF-09: FAIL - {len(violations)} residency bypass path(s) found:")
        for rel, lineno, msg in violations:
            print(f"  {rel}:{lineno}: {msg}")
        print("  remedy: ALL classified-field access goes through libs/py/fix_residency (FF-09).")
        return 1

    print("FF-09: OK - no residency bypass paths; fix_residency is the sole client")
    return 0


if __name__ == "__main__":
    sys.exit(main())
