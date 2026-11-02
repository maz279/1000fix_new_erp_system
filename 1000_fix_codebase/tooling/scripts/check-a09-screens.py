#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(
    "c:/software_project/software_project_14/1000 fix/1000fix_new_erp_system/1000_fix_codebase"
)
STATIC_A09 = ROOT / "addons" / "platform" / "cd_p03_portal" / "static" / "src" / "a09"

A09_MODS = ["M21", "M55", "M56", "M57", "M22", "M58", "M59"]

for mid in A09_MODS:
    js_file = STATIC_A09 / f"{mid.lower()}.js"
    if not js_file.exists():
        continue
    content = js_file.read_text(encoding="utf-8")

    # Extract SCREENS keys and kinds
    screens = re.findall(r"'([A-Za-z0-9_\-]+)':\s*\{\s*kind:\s*'([a-z_]+)'", content)
    print(f"\n[{mid}] Total screens declared: {len(screens)}")
    by_kind = {}
    for sc_id, kind in screens:
        by_kind.setdefault(kind, []).append(sc_id)
    for kind, sc_list in by_kind.items():
        print(
            f"  kind '{kind}' ({len(sc_list)}): {', '.join(sc_list[:5])}{'...' if len(sc_list) > 5 else ''}"
        )

    # Check FORM_CHIPS
    chips_match = re.search(r"export const FORM_CHIPS = \{([\s\S]*?)\n\};", content)
    if chips_match:
        chips = re.findall(r"'([^']+)':\s*'([^']+)'", chips_match.group(1))
        print(f"  FORM_CHIPS: {len(chips)} chip mappings")
    else:
        print("  FORM_CHIPS: NONE!")

    # Check CREATE
    create_match = re.search(r"export const CREATE = \{([\s\S]*?)\n\};", content)
    if create_match:
        print(f"  CREATE: {create_match.group(1).strip()[:80]}")
    else:
        print("  CREATE: NONE!")
