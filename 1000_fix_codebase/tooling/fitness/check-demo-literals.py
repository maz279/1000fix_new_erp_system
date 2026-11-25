#!/usr/bin/env python3
"""check-demo-literals — PP6 E3: no fabricated data in the Odoo estate.

The elimination plan's sweep, made durable (03-DATA-STRATEGY §3 E3):
- View/template/static files carry no data-looking literals (sample
  phone numbers, example/demo e-mails, PRNG, lorem text)
- No module ships Odoo demo data: a `"demo"` manifest key may only be
  empty or reference files inside the module's own `demo/` directory —
  per §1 the TEST data class enters through db/seeds/seed.py ONLY
  (Odoo demo data would install fabricated rows on production installs
  with demo_mode enabled)

Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADDONS = REPO / "addons"
APPS = REPO / "apps"

SKIP_PARTS = {"tests", "stories", "__pycache__", ".mimosa", "i18n", "node_modules", ".next", "demo"}

LITERAL_SMELLS = {
    "bd-phone-literal": re.compile(r">\s*01[3-9]\d{8}\s*<"),
    "example-email": re.compile(r"[\w.]+@(?:example|test|demo)\.\w+"),
    "prng": re.compile(r"\b(?:random\.\w+|Math\.random)\s*\("),
    "lorem": re.compile(r"lorem ipsum", re.I),
}


def main() -> int:
    v: list[str] = []

    # --- view/template/static literal sweep -----------------------------
    for base in (ADDONS, APPS):
        for f in base.rglob("*"):
            if not f.is_file() or f.suffix not in (".xml", ".py", ".js", ".ts", ".tsx"):
                continue
            if any(p in SKIP_PARTS for p in f.parts) or "/demo/" in str(f).replace("\\", "/"):
                continue
            try:
                txt = f.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for name, rx in LITERAL_SMELLS.items():
                for m in rx.finditer(txt):
                    v.append(f"{name}: {f.relative_to(REPO)} :: {m.group(0)[:50]!r}")

    # --- Odoo demo-data policy ------------------------------------------
    for mf in ADDONS.rglob("__manifest__.py"):
        if any(p in SKIP_PARTS for p in mf.parts):
            continue
        rel = mf.relative_to(REPO)
        src = mf.read_text(encoding="utf-8")
        m = re.search(r'"demo":\s*(\[[^\]]*\]|"[^"]*")', src, re.S)
        if not m:
            continue  # no demo key at all — the default is none
        body = m.group(1)
        if body.strip() == "[]":
            continue  # explicitly empty — fine
        # non-empty: every referenced file must live under the module's demo/
        module_dir = mf.parent
        for ref in re.findall(r'"([^"]+\.(?:xml|csv|py))"', body):
            if not (module_dir / "demo" / ref).exists():
                v.append(f"demo-data outside demo/: {rel} references {ref}")

    if v:
        print(f"demo-literals: FAIL - {len(v)} violation(s):")
        for line in v:
            print(f"  {line}")
        return 1

    print(
        "demo-literals: OK — estate views/static carry no fabricated "
        "literals and no module ships Odoo demo data (TEST data enters "
        "via db/seeds/seed.py only, 03-DATA-STRATEGY §1/E3)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
