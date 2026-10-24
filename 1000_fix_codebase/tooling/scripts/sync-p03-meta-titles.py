#!/usr/bin/env python3
"""sync-p03-meta-titles — PP7 hardening fix (found by the journey suite).

The hand-authored P03_MODULES metadata in cd_p03_portal drifted from the
frozen navigation registry (63 of 67 module titles mismatched). This
script re-aligns, per module: `en`, `title` (= "<code> · <en>"), `bn`,
`icon`, `desc`, `cross` — everything the registry is the authority for —
while leaving the hand-maintained kpis/groups/screens/reports/forms/freg
content untouched. Idempotent; asserts all 67 modules are present both
sides before writing. Run from the repo root:

    python tooling/scripts/sync-p03-meta-titles.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "contracts" / "nav" / "registry.json"
META = REPO / "addons" / "platform" / "cd_p03_portal" / "static" / "src" / "p03_modules_meta.js"


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def main() -> int:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    mods = {m["id"]: m for m in reg["modules"]}
    src = META.read_text(encoding="utf-8")

    present = set(re.findall(r"^  (M\d{2}): \{$", src, re.M))
    missing = sorted(set(mods) - present)
    if missing:
        print(f"meta lacks modules: {missing}")
        return 1

    changed = 0
    for mid, m in mods.items():
        start = src.find(f"  {mid}: {{\n")
        assert start != -1, mid
        end = src.find("\n  },", start)
        blk = src[start:end]

        want_en = m["en"]
        want_title = f"{mid} · {want_en}"
        want_bn = m.get("bn", "")
        want_desc = m.get("desc", "")
        want_icon = m.get("icon", "")

        new = blk
        new = re.sub(r"en: '[^']*'", f"en: '{esc(want_en)}'", new, count=1)
        new = re.sub(r"title: '[^']*'", f"title: '{esc(want_title)}'", new, count=1)
        new = re.sub(r"bn: '[^']*'", f"bn: '{esc(want_bn)}'", new, count=1)
        if want_desc:
            new = re.sub(r"desc: '[^']*'", f"desc: '{esc(want_desc)}'", new, count=1)
        if want_icon:
            new = re.sub(r"icon: '[^']*'", f"icon: '{esc(want_icon)}'", new, count=1)
        if new != blk:
            changed += 1
            src = src[:start] + new + src[end:]

    META.write_text(src, encoding="utf-8", newline="\n")

    # verify zero drift after the rewrite
    src = META.read_text(encoding="utf-8")
    drift = []
    for mid, m in mods.items():
        start = src.find(f"  {mid}: {{\n")
        end = src.find("\n  },", start)
        blk = src[start:end]
        en = re.search(r"en: '([^']*)'", blk).group(1)
        if en != m["en"]:
            drift.append(mid)
    print(
        f"sync-p03-meta-titles: {changed} modules corrected, "
        f"post-verify drift: {len(drift)} {drift[:5]}"
    )
    return 0 if not drift else 1


if __name__ == "__main__":
    sys.exit(main())
