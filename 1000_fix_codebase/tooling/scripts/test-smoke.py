#!/usr/bin/env python3
"""test-smoke - P02-M10-T06: one path end to end, under three minutes.

Create a customer -> create a service order -> transition its state machine
-> ASSERT the outbox emitted the declared events -> ASSERT record rules deny
a user without the role.

Activates with the Phase-3 kernel models (M01/M33). Until then it exits 4
(NOT-AVAILABLE) so pipelines treat it as "not yet applicable" rather than
green-by-silence - the roadmap's own principle for missing checks.
"""
from __future__ import annotations

import sys

REQUIRED_MODULES = ["cd_party_master", "cd_service_order"]


def available() -> bool:
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    return all((root / "addons" / "platform" / m).is_dir() or
               any((root / "addons" / "domain" / c / m).is_dir()
                   for c in (p.name for p in (root / "addons" / "domain").glob("*") if p.is_dir()))
               for m in REQUIRED_MODULES)


def main() -> int:
    if not available():
        print("test-smoke: NOT-AVAILABLE - kernel modules not yet present (Phase 3, W1).")
        print("  Exit 4 = not-yet-applicable; never a silent green.")
        return 4
    import unittest  # noqa: F401  - real suite lands with the kernel
    raise SystemExit("test-smoke: kernel present - wire the smoke suite here (P02-M10-T06)")


if __name__ == "__main__":
    sys.exit(main())
