#!/usr/bin/env python3
"""sync-p03-meta — regenerate P03_MODULES in cd_p03_portal from the frozen
navigation registry (supersedes sync-p03-meta-titles.py).

Why: the hand-authored P03_MODULES content (kpis / groups / screens /
reports / forms / freg) drifted from contracts/nav/registry.json for all 67
modules — e.g. the M42 Supplier Relationship workspace showed two warehouse
sub-modules and an "Inbound GRN Receiving Form" instead of its nine
supplier sub-modules and four supplier forms. The titles-only sync fixed
headings but left the body wrong. The registry is the single authority
(PP0-M03), so the whole module block is now generated from it.

What is NOT generated here: which backend model captures a form, and which
forms belong to which sub-module. That lives in p03_capture_map.js (hand
maintained, module by module, as backends land) so this mirror stays a
pure, idempotent copy of the registry.

KPI values are deliberately absent: the registry holds labels only and the
workspace wires values per module phase (FF-44: no fabricated numbers).

Run from the repo root:
    python tooling/scripts/sync-p03-meta.py            # rewrite
    python tooling/scripts/sync-p03-meta.py --check    # exit 1 on drift
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "contracts" / "nav" / "registry.json"
META = (REPO / "addons" / "platform" / "cd_p03_portal" /
        "static" / "src" / "p03_modules_meta.js")

START = "export const P03_MODULES = {\n"
END_RE = re.compile(r"^};\n", re.M)


def q(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def module_block(m: dict) -> str:
    mid = m["id"]
    lines = [f"  {mid}: {{",
             f"    area: {q(m['area'])}, code: {q(mid)}, en: {q(m['en'])},"
             f" title: {q(mid + ' · ' + m['en'])},",
             f"    bn: {q(m.get('bn', ''))}, icon: {q(m.get('icon', ''))},",
             f"    desc: {q(m.get('desc', ''))},",
             "    kpis: [" + ", ".join(f"{{ l: {q(k)} }}" for k in m.get("kpis", [])) + "],",
             "    groups: ["]
    for g in m.get("groups", []):
        lines.append(f"      {{ en: {q(g['en'])}, screens: [")
        for s in g["screens"]:
            lines.append(f"        {{ id: {q(s['id'])}, en: {q(s['en'])},"
                         f" bn: {q(s.get('bn', ''))}, t: {q(s['t'])} }},")
        lines.append("      ] },")
    lines.append("    ],")
    lines.append("    reports: [" + ", ".join(q(r) for r in m.get("reports", [])) + "],")
    lines.append("    forms: [" + ", ".join(q(f) for f in m.get("forms", [])) + "],")
    lines.append("    cross: [" + ", ".join(q(c) for c in m.get("cross", [])) + "],")
    freg = m.get("freg", {"src": 0, "sub": []})
    subs = ", ".join(f"[{q(s[0])}, {q(s[1])}, {int(s[2])}]" for s in freg["sub"])
    lines.append(f"    freg: {{ src: {int(freg['src'])}, sub: [{subs}] }}")
    lines.append("  },")
    return "\n".join(lines)


def build(reg: dict, area_order: list[tuple[str, str, list[str]]]) -> str:
    mods = {m["id"]: m for m in reg["modules"]}
    out = [START.rstrip("\n")]
    placed: list[str] = []
    for area_id, area_en, mids in area_order:
        out.append(f"  /* ============ {area_id} · {area_en.upper()} "
                   + "=" * max(4, 50 - len(area_en)) + " */")
        for mid in mids:
            out.append(module_block(mods[mid]))
            placed.append(mid)
        out.append("")
    if sorted(placed) != sorted(mods):
        missing = sorted(set(mods) - set(placed))
        raise SystemExit(f"P03_AREAS does not place every registry module: {missing}")
    out[-1] = "};"
    return "\n".join(out) + "\n"


def area_order(src: str, reg: dict) -> list[tuple[str, str, list[str]]]:
    """Order from the meta's own P03_AREAS (the mega-menu order); each
    module's area must agree with the registry."""
    mods = {m["id"]: m for m in reg["modules"]}
    order = []
    for m in re.finditer(r"\{ id: '(A\d\d)',[^}]*?en: '([^']*)'.*?mods: \[([^\]]*)\] \}", src):
        area_id, area_en, mids = m.group(1), m.group(2), re.findall(r"'(M\d\d)'", m.group(3))
        for mid in mids:
            if mods[mid]["area"] != area_id:
                raise SystemExit(f"{mid}: P03_AREAS says {area_id}, registry says "
                                 f"{mods[mid]['area']}")
        order.append((area_id, area_en, mids))
    return order


def main() -> int:
    check = "--check" in sys.argv
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    src = META.read_text(encoding="utf-8")
    start = src.index(START)
    end_match = END_RE.search(src, start)
    if not end_match:
        raise SystemExit("could not find the end of P03_MODULES")
    current = src[start:end_match.end()]
    wanted = build(reg, area_order(src, reg))
    if current == wanted:
        print(f"sync-p03-meta: OK - {len(reg['modules'])} modules match the registry")
        return 0
    if check:
        print("sync-p03-meta: DRIFT - P03_MODULES differs from contracts/nav/registry.json; "
              "run python tooling/scripts/sync-p03-meta.py")
        return 1
    META.write_text(src[:start] + wanted + src[end_match.end():], encoding="utf-8", newline="\n")
    print(f"sync-p03-meta: rewrote P03_MODULES from the registry ({len(reg['modules'])} modules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
