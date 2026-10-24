#!/usr/bin/env python3
"""verify_gate_g4.py - DEPRECATED, retained for history (R01 re-audit 2026-10-22).

This Python gate verifier fell back to HARDCODED counts when regex parsing
failed and awarded literal PASS for every criterion, whatever the suites did.
It is superseded by the honest rewrite of tooling/gate/verify-gate-g4.ps1
(exit codes honoured, counts parsed, operational criteria honestly
CONDITION), whose evidence JSON is tooling/gate/evidence/gate-g4-latest.json.

Do not call this module. It takes no action and proves nothing.
"""

from __future__ import annotations

import sys

MESSAGE = (
    "verify_gate_g4.py is deprecated (literal PASS verifier; see the R01 "
    "re-audit 2026-10-22). Use: powershell -File tooling/gate/verify-gate-g4.ps1 "
    "-Json tooling/gate/evidence/gate-g4-latest.json"
)


def main() -> int:
    print(MESSAGE, file=sys.stderr)
    return 2  # permanent failure: forces any stale caller to notice


if __name__ == "__main__":
    sys.exit(main())
