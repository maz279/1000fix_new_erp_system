#!/usr/bin/env python3
"""verify_gate_g3.py - DEPRECATED, retained for history (R01 re-audit 2026-10-22).

This Python gate verifier IGNORED test exit codes and invented counts when
parsing failed; it awarded PASS regardless of what the suites did. It is
superseded by the honest rewrite of tooling/gate/verify-gate-g3.ps1, whose
exit codes are honoured and whose evidence JSON is written to
tooling/gate/evidence/gate-g3-latest.json.

Do not call this module. It takes no action and proves nothing.
"""

from __future__ import annotations

import sys

MESSAGE = (
    "verify_gate_g3.py is deprecated (ignored exit codes; see the R01 re-audit "
    "2026-10-22). Use: powershell -File tooling/gate/verify-gate-g3.ps1 -Json "
    "tooling/gate/evidence/gate-g3-latest.json"
)


def main() -> int:
    print(MESSAGE, file=sys.stderr)
    return 2  # permanent failure: forces any stale caller to notice


if __name__ == "__main__":
    sys.exit(main())
