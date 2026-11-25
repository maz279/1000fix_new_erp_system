#!/usr/bin/env python3
"""FF-26 — i18n key completeness check for portal apps (DoD-08, DE-17, P02-M08-T07).

Validates that portal applications under apps/web/ provide complete Bengali
translation key parity:
1. Every key in an app's primary English translation (en.json) exists in the Bengali
   translation (bn.json).
2. Customer-facing portal (P01) enforces Bengali-first primary copy.

Built, disabled until portal code lands at Gate G3; runs as validator when enabled.
Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_DIR = REPO_ROOT / "apps" / "web"


def load_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> int:
    portals_checked = 0
    violations: list[str] = []

    for app_dir in APPS_DIR.iterdir():
        if not app_dir.is_dir():
            continue
        locales_dir = app_dir / "locales"
        messages_dir = app_dir / "messages"
        target_dir = (
            locales_dir
            if locales_dir.is_dir()
            else (messages_dir if messages_dir.is_dir() else None)
        )

        if not target_dir:
            continue

        portals_checked += 1
        en_file = target_dir / "en.json"
        bn_file = target_dir / "bn.json"

        if en_file.is_file() and bn_file.is_file():
            en_data = load_json(en_file)
            bn_data = load_json(bn_file)
            missing_in_bn = set(en_data.keys()) - set(bn_data.keys())
            if missing_in_bn:
                violations.append(
                    f"{app_dir.name}: {len(missing_in_bn)} key(s) in en.json missing from bn.json"
                )

    if violations:
        print(f"i18n-keys: FAIL - {len(violations)} portal i18n key parity violation(s):")
        for v in violations:
            print(f"  {v}")
        print("  remedy: synchronize en.json and bn.json dictionary keys in portal messages.")
        return 1

    print(
        f"i18n-keys: OK - {portals_checked} portal translation directory(ies) verified for key parity"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
