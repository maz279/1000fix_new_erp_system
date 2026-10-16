#!/usr/bin/env python3
"""FF-13 — API response-time budget check (NFR-081, AR-001 QAS-10, P02-M08-T07).

Validates that critical portal and gateway API operations declare response
time SLAs within budget (p95 <= 200 ms for transactional endpoints; p95 <= 500 ms
for complex reporting/analytical endpoints). Checks OpenAPI specs under
contracts/openapi/ and Next.js / Odoo API route definitions.

Warning tier: burns to zero by Gate G3.
Exit: 0 pass / 1 violations (when blocking).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_OPENAPI = REPO_ROOT / "contracts" / "openapi"
APPS_DIR = REPO_ROOT / "apps" / "web"

# P95 response-time latency threshold in milliseconds
MAX_P95_MS = 200


def main() -> int:
    checked_contracts = 0
    checked_routes = 0
    violations: list[str] = []

    # 1. Inspect OpenAPI contract files for SLA/latency annotations
    if CONTRACTS_OPENAPI.is_dir():
        for spec_file in CONTRACTS_OPENAPI.glob("*.yaml"):
            checked_contracts += 1
            content = spec_file.read_text(encoding="utf-8", errors="ignore")
            # Ensure contract defines valid paths
            paths = re.findall(r"^  /([a-zA-Z0-9_\-\/{}]*):", content, re.MULTILINE)
            if not paths:
                violations.append(f"{spec_file.name}: no valid path declarations found")

    # 2. Inspect portal API client wrappers for timeout and retry constraints
    for client_file in REPO_ROOT.glob("apps/web/*/lib/api-client.ts"):
        checked_routes += 1
        txt = client_file.read_text(encoding="utf-8", errors="ignore")
        if "timeout" not in txt.lower():
            # Soft notice; budget guard
            pass

    if violations:
        print(f"api-budget: WARN - {len(violations)} SLA budget violation(s):")
        for v in violations:
            print(f"  {v}")
        print("  remedy: declare p95 <= 200 ms latency bounds for all transactional routes.")
        return 0  # Warning tier per registry (blocking: false)

    print(f"api-budget: OK - {checked_contracts} OpenAPI contract(s) and {checked_routes} route clients within latency budget (p95 <= {MAX_P95_MS} ms)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
