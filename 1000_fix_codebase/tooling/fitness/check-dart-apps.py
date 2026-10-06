#!/usr/bin/env python3
"""check-dart-apps — PP4-M02/M03/M04/M05 structural validation.

Validates all 4 Flutter apps' structure without a Dart SDK:
- Consumes fix_ui tokens via fixColor() (CFM-01: zero hand hex)
- Consumes the fix_offline engine (FL-03: one engine, never re-implemented)
- Has the app-specific screens per the plan's task table
- Bengali-first in the customer app (DE-17)

Exit: 0 pass / 1 violations.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MOBILE = REPO / "apps" / "mobile"

APPS = {
    "technician": {
        "title": "P02 Technician",
        "screens": ["DayViewScreen", "JobExecutionScreen", "EvidenceCaptureScreen"],
        "bn": False,  # EN-first for field staff
    },
    "rider": {
        "title": "P09 Rider",
        "screens": ["ManifestScreen", "CustodyScanScreen", "DeliveryConfirmScreen"],
        "bn": False,
    },
    "auditor": {
        "title": "P11 Auditor",
        "screens": ["AuditListScreen", "ChecklistScreen"],
        "bn": False,
    },
    "customer": {
        "title": "APP-04 Customer",
        "screens": ["HomeScreen", "BookingScreen"],
        "bn": True,  # Bengali-first (DE-17)
    },
}


def main() -> int:
    v: list[str] = []

    for dirname, spec in APPS.items():
        base = MOBILE / dirname
        main_dart = base / "lib" / "main.dart"
        pubspec = base / "pubspec.yaml"

        if not main_dart.exists():
            v.append(f"{dirname}: lib/main.dart missing")
            continue

        code = main_dart.read_text(encoding="utf-8")

        # CFM-01: zero hand-authored hex outside fix_color.dart
        hexes = re.findall(r"Color\(0x[0-9A-Fa-f]+\)", code)
        if hexes:
            v.append(f"{dirname}: hand-authored hex Color(): {hexes[:3]}")

        # fix_ui consumption via fixColor()
        if "fixColor(" not in code:
            v.append(f"{dirname}: fixColor() not used (CFM-01)")

        # Token consumption
        if "t_color_primary_base" not in code:
            v.append(f"{dirname}: primary token not consumed")

        # fix_offline engine consumed (FL-03)
        pubspec_text = pubspec.read_text(encoding="utf-8") if pubspec.exists() else ""
        if "fix_offline" not in pubspec_text:
            v.append(f"{dirname}: fix_offline dependency missing (FL-03)")

        # App-specific screens
        for screen in spec["screens"]:
            if screen not in code:
                v.append(f"{dirname}: screen {screen} missing")

        # Bengali-first (DE-17) for the customer app
        if spec["bn"]:
            # Check for Bengali text (Unicode block 0980-09FF)
            bn_chars = re.findall(r"[\u0980-\u09FF]", code)
            if len(bn_chars) < 10:
                v.append(f"{dirname}: Bengali-first UI required (DE-17) — "
                         f"only {len(bn_chars)} Bengali chars found")

        # The app title
        if spec["title"].split(" ")[0] not in code and spec["title"] not in code:
            v.append(f"{dirname}: title '{spec['title']}' not found")

    if v:
        print(f"dart-apps: FAIL - {len(v)} violation(s):")
        for line in v:
            print(f"  {line}")
        return 1

    total_screens = sum(len(s["screens"]) for s in APPS.values())
    print(f"dart-apps: OK — 4 apps, {total_screens} screens, all consuming "
          "fix_ui tokens + fix_offline engine (FL-03), CFM-01 clean, "
          f"customer app Bengali-first (DE-17)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
