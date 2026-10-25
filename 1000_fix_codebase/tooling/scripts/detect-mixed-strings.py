#!/usr/bin/env python3
"""detect-mixed-strings — list every literal that mixes Bangla script with
Latin letters (the DE-17 separation violation) across the 8 portals.

Allowed-in-Bangla Latin tokens (acronyms/product names, user policy
2026-10-25) don't make a string clean per se — the CHECKER enforces the
policy; this detector just inventories candidates for the cleanup pass.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
WEB = ROOT / "apps" / "web"
MIXED = re.compile(r"[\u0980-\u09FF]")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")


def scan_file(path: pathlib.Path) -> list[dict]:
    hits = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return hits
    for lineno, line in enumerate(text.splitlines(), 1):
        if MIXED.search(line) and LATIN_WORD.search(line):
            hits.append(
                {"file": str(path.relative_to(ROOT)), "line": lineno, "text": line.strip()[:150]}
            )
    return hits


def main() -> None:
    out = []
    for app in sorted(WEB.iterdir()):
        if not app.is_dir() or app.name == "node_modules":
            continue
        for f in app.rglob("*"):
            if "node_modules" in f.parts or ".next" in f.parts:
                continue
            if f.suffix not in {".tsx", ".ts", ".json"}:
                continue
            out.extend(scan_file(f))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"# mixed lines: {len(out)}", file=sys.stderr)


if __name__ == "__main__":
    main()
