#!/usr/bin/env python3
"""check-bundle-budget — the contracted P01 < 400 KB critical-path budget.

Measures the gzipped first-load weight of a built Next app: every JS chunk
under .next/static plus the prerendered route HTML (the bytes a cold 3G
visitor pulls before interactivity). Usage:

    python tooling/scripts/check-bundle-budget.py apps/web/customer 400

Exit 0 within budget (prints the measured KB); exit 1 over budget or when
no build output exists (run `npm run build` first).
"""
from __future__ import annotations

import gzip
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def gzip_size(data: bytes) -> int:
    return len(gzip.compress(data, mtime=0))


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check-bundle-budget.py <app-dir> [budget_kb]")
        return 1
    app = REPO / sys.argv[1]
    budget_kb = float(sys.argv[2]) if len(sys.argv) > 2 else 400.0
    chunks = app / ".next" / "static"
    html_dir = app / ".next" / "server" / "app"
    if not chunks.is_dir():
        print(f"bundle-budget: FAIL — no build output at {app}/.next (run npm run build)")
        return 1
    total = 0
    files = 0
    for f in chunks.rglob("*"):
        if f.is_file() and f.suffix in {".js", ".css"}:
            total += gzip_size(f.read_bytes())
            files += 1
    html_bytes = 0
    if html_dir.is_dir():
        for f in sorted(html_dir.rglob("*.html")):
            html_bytes += gzip_size(f.read_bytes())
            files += 1
            break  # the critical path is ONE route — measure the first only
    total += html_bytes
    kb = total / 1024
    verdict = "OK" if kb <= budget_kb else "OVER BUDGET"
    print(f"bundle-budget: {verdict} — {kb:.0f} KB gz across {files} files "
          f"(budget {budget_kb:.0f} KB; JS+CSS chunks{' + route HTML' if html_bytes else ''})")
    return 0 if kb <= budget_kb else 1


if __name__ == "__main__":
    sys.exit(main())
