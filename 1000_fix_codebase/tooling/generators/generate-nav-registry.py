#!/usr/bin/env python3
"""generate-nav-registry — PP0-M03-T01.

Parses the read-only prototype payloads (Front_end/, frozen at PP0-M05) and
emits contracts/nav/registry.json — the production navigation universe that
P03 menus, portal routes, Tell-ME search, the Report Center and the coverage
ledger all consume.

Payload syntax (verified by the zero-trust audits, iterations 4–5):
  nav_data.js    FX_AREAS (12), FX_PORTALS (12), FX_MODULES literal keys (14)
  nav_data2/3.js window.FX_MODULES.Mxx = {...} assignments (53)  -> 67 modules
  per module     groups:[{en, screens:[{id,en,bn,t}]}]  -> 278 groups,
                 823 unique screen ids (t: w g f r c d x s)
                 reports:['…'] (346 strings), forms:['…'] (266 strings),
                 cross:['…'], freg:{src, sub:[[id,name,count]]} -> 600 triples,
                 5,100 functions; kpis:[{l,v,d,spark…}] — LABELS ONLY (the
                 fabricated values/sparklines are dropped at the gate)
  demo_data.js   structural arrays: PORTALS (12 rows), JOURNEYS (10 with
                 step->screen links), PERSONAS (4) — structure kept, fixtures
                 dropped

Every headline count is asserted; a drifting payload fails the run rather
than silently producing a short registry. Deterministic and idempotent.

Exit: 0 written / 1 payload shape unexpected.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FRONT = REPO.parent / "Front_end"
OUT = REPO / "contracts" / "nav" / "registry.json"

EXPECT = {
    "areas": 12,
    "portals": 12,
    "modules": 67,
    "groups": 280,
    # 2026-11-09 partner-ledger rollout (R-2/R-11): +4 M19 screens, +2
    # reports, +1 form — prototype payloads extended alongside the workspace.
    # (Each added screen object also advances the function-token count.)
    # 2026-11-23 A10 deep audit (D-A10-7): the shipped fragments overlay the
    # prototype (M23/M24/M60/M61 capture-pass screens). +2 groups, +50 screens,
    # +55 forms, +2 reports versus the frozen prototype.
    "screens": 877,
    "reports": 350,
    "forms": 322,
    "sub_triples": 600,
    "functions": 5104,
    "journeys": 10,
    "personas": 4,
}


def read(name: str) -> str:
    return (FRONT / "js" / name).read_text(encoding="utf-8")


def parse_areas(nav1: str) -> list[dict]:
    areas = []
    for m in re.finditer(
        r"\{ id:'(A\d+)', key:'([a-z]+)',\s*en:'([^']*)',\s*bn:'([^']*)'," r"\s*mods:\[([^\]]*)\]",
        nav1,
    ):
        areas.append(
            {
                "id": m.group(1),
                "key": m.group(2),
                "en": m.group(3),
                "bn": m.group(4),
                "modules": re.findall(r"'(M\d\d)'", m.group(5)),
            }
        )
    return areas


def split_modules(all3: str) -> dict[str, str]:
    """Return {module_id: module_body} for both declaration styles."""
    bodies: dict[str, str] = {}
    # Style 1 — object literal `M01: { ... },` (nav_data.js, column-0 keys):
    # the body ends at the next module key OR the FX_MODULES closing `};`,
    # whichever comes first — never past it into the assignment-style files.
    for m in re.finditer(r"\n(M\d{2}): \{", all3):
        start = m.end() - 1
        window = all3[m.end() :]
        nxt = re.search(r"\n(M\d{2}): \{", window)
        close = re.search(r"\n\};", window)
        if close and (not nxt or close.start() < nxt.start()):
            end = m.end() + close.start()
        else:
            end = m.end() + (nxt.start() if nxt else len(window))
        bodies[m.group(1)] = all3[start + 1 : end]
    # Style 2 — `window.FX_MODULES.Mxx = { ... };` assignments (nav_data2/3).
    for m in re.finditer(r"FX_MODULES\.(M\d{2}) = \{", all3):
        start = m.end() - 1
        nxt = re.search(r"FX_MODULES\.M\d{2} = \{", all3[m.end() :])
        end = m.end() + (nxt.start() if nxt else len(all3) - m.end())
        body = all3[start + 1 : end]
        body = body.rsplit("};", 1)[0]
        bodies[m.group(1)] = body
    return bodies


def parse_module(mid: str, body: str) -> dict:
    head = re.search(
        r"area:'(A\d+)', en:'((?:[^'\\]|\\.)*)', bn:'((?:[^'\\]|\\.)*)'"
        r"(?:, icon:'([^']*)')?(?:, rail:'([a-z]*)')?",
        body,
    )
    mod = {
        "id": mid,
        "area": head.group(1),
        "en": head.group(2).replace("\\'", "'"),
        "bn": head.group(3).replace("\\'", "'"),
        "icon": head.group(4) or "",
        "rail": head.group(5) or "",
    }
    d = re.search(r"desc:'((?:[^'\\]|\\.)*)'", body)
    mod["desc"] = d.group(1).replace("\\'", "'") if d else ""
    # groups -> screens
    groups = []
    for gm in re.finditer(r"\{en:'((?:[^'\\]|\\.)*)',\s*screens:\[(.*?)\]\}", body, re.S):
        screens = []
        for sm in re.finditer(
            r"\{id:'([^']+)',\s*en:'((?:[^'\\]|\\.)*)',\s*bn:'((?:[^'\\]|\\.)*)',"
            r"\s*t:'([a-z])'\}",
            gm.group(2),
        ):
            screens.append(
                {
                    "id": sm.group(1),
                    "en": sm.group(2).replace("\\'", "'"),
                    "bn": sm.group(3).replace("\\'", "'"),
                    "t": sm.group(4),
                }
            )
        groups.append({"en": gm.group(1).replace("\\'", "'"), "screens": screens})
    mod["groups"] = groups
    # reports / forms / cross — plain-string arrays
    for field in ("reports", "forms", "cross"):
        am = re.search(field + r":\s*\[(.*?)\]", body, re.S)
        mod[field] = re.findall(r"'((?:[^'\\]|\\.)*)'", am.group(1)) if am else []
        mod[field] = [v.replace("\\'", "'") for v in mod[field]]
    # freg — src + sub triples
    freg = {"src": 0, "sub": []}
    fm = re.search(r"freg:\s*\{\s*src:(\d+),\s*sub:\s*\[(.*?)\]\s*\}", body, re.S)
    if fm:
        freg["src"] = int(fm.group(1))
        for tm in re.finditer(r"\['([^']*)','((?:[^'\\]|\\.)*)',(\d+)\]", fm.group(2)):
            freg["sub"].append([tm.group(1), tm.group(2).replace("\\'", "'"), int(tm.group(3))])
    mod["freg"] = freg
    # kpis — LABELS ONLY; fabricated values/deltas/sparks are dropped here
    kpis = []
    for km in re.finditer(r"\{l:'((?:[^'\\]|\\.)*)'", body):
        kpis.append(km.group(1).replace("\\'", "'"))
    mod["kpis"] = kpis
    return mod


def parse_structural(demo: str) -> dict:
    out: dict = {}
    pm = re.search(r"D\.PORTALS\s*=\s*\[(.*?)\n\];", demo, re.S)
    portals = []
    for row in re.finditer(
        r"\[\s*'(P\d\d)'\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*,"
        r"\s*'([^']*)'\s*,\s*\[(.*?)\]\s*\]",
        pm.group(1),
        re.S,
    ):
        caps = re.findall(r"'((?:[^'\\]|\\.)*)'", row.group(6))
        portals.append(
            {
                "id": row.group(1),
                "name": row.group(2),
                "users": row.group(3),
                "volume": row.group(4),
                "tech": row.group(5),
                "capabilities": [c.replace("\\'", "'") for c in caps],
            }
        )
    out["portals"] = portals
    jm = re.search(r"D\.JOURNEYS\s*=\s*\[(.*?)\n\];", demo, re.S)
    # Steps are triples [actor, description, '#/route'] — actor + route kept
    # (the route is the step->screen link); the description is copy, kept too.
    journeys = []
    for row in re.finditer(
        r"\{[^{}]*?id:'([^']+)'[^{}]*?en:'([^']*)'"
        r"(?:[^{}]*?bn:'([^']*)')?[^{}]*?steps:\[(.*?)\]\]\s*\}",
        jm.group(1),
        re.S,
    ):
        steps = []
        for sm in re.finditer(r"\['([^']*)','((?:[^'\\]|\\.)*)','([^']*)'\]", row.group(4)):
            steps.append(
                {
                    "actor": sm.group(1),
                    "desc": sm.group(2).replace("\\'", "'"),
                    "route": sm.group(3),
                }
            )
        journeys.append(
            {"id": row.group(1), "en": row.group(2), "bn": row.group(3) or "", "steps": steps}
        )
    out["journeys"] = journeys
    per = re.search(r"D\.PERSONAS\s*=\s*\[(.*?)\n\];", demo, re.S)
    personas = []
    for row in re.finditer(r"\{[^{}]*?id:'([^']+)'", per.group(1)):
        personas.append({"id": row.group(1)})
    out["personas"] = personas
    return out


FRAGMENTS = REPO / "contracts" / "nav" / "fragments.json"
FRAGMENT_SOURCES = [
    REPO / "addons" / "platform" / "cd_p03_portal" / "static" / "src" / "a10" / f"{code}.js"
    for code in ("m23", "m24", "m60", "m61")
]


def apply_fragment_overlay(modules: list[dict]) -> list[dict]:
    """Overlay the SHIPPED fragments onto the prototype parse (A10 deep audit
    2026-11-23, D-A10-7). The prototype is frozen; the capture-pass screens
    live only in the fragments, and the registry must describe what ships.
    The sidecar is generated by export-fragment-nav.mjs; a stale sidecar
    (fragment newer than the export) fails the run rather than shipping a
    registry that hides shipped screens."""
    if not FRAGMENTS.exists():
        print(
            "generate-nav-registry: contracts/nav/fragments.json missing "
            "(run tooling/generators/export-fragment-nav.mjs)"
        )
        return modules
    exported_at = FRAGMENTS.stat().st_mtime
    for src in FRAGMENT_SOURCES:
        if src.exists() and src.stat().st_mtime > exported_at:
            print(
                f"generate-nav-registry: {src.name} is newer than fragments.json "
                "(re-run export-fragment-nav.mjs)"
            )
            raise SystemExit(1)
    sidecar = json.loads(FRAGMENTS.read_text(encoding="utf-8"))
    overlay = sidecar.get("modules", {})
    out = []
    for module in modules:
        patch = overlay.get(module["id"])
        if patch:
            module = {**module, **patch}
        out.append(module)
    return out


def main() -> int:
    nav1, nav2, nav3 = read("nav_data.js"), read("nav_data2.js"), read("nav_data3.js")
    all3 = nav1 + nav2 + nav3
    demo = read("demo_data.js")

    areas = parse_areas(nav1)
    bodies = split_modules(all3)
    modules = [parse_module(mid, body) for mid, body in sorted(bodies.items())]
    modules = apply_fragment_overlay(modules)
    structural = parse_structural(demo)

    counts = {
        "areas": len(areas),
        "portals": len(structural["portals"]),
        "modules": len(modules),
        "groups": sum(len(m["groups"]) for m in modules),
        "screens": sum(len(g["screens"]) for m in modules for g in m["groups"]),
        "reports": sum(len(m["reports"]) for m in modules),
        "forms": sum(len(m["forms"]) for m in modules),
        "sub_triples": sum(len(m["freg"]["sub"]) for m in modules),
        "functions": sum(t[2] for m in modules for t in m["freg"]["sub"]),
        "journeys": len(structural["journeys"]),
        "personas": len(structural["personas"]),
    }
    bad = {k: (v, EXPECT[k]) for k, v in counts.items() if v != EXPECT[k]}
    if bad:
        for k, (got, want) in bad.items():
            print(f"generate-nav-registry: {k} = {got}, expected {want}")
        return 1
    ids = [s["id"] for m in modules for g in m["groups"] for s in g["screens"]]
    if len(ids) != len(set(ids)):
        dupes = {i for i in ids if ids.count(i) > 1}
        print(f"generate-nav-registry: duplicate screen ids {sorted(dupes)}")
        return 1

    registry = {
        "$schema": "generated by tooling/generators/generate-nav-registry.py "
        "(PP0-M03-T01). Source: the frozen Front_end prototype. "
        "Do not edit by hand.",
        "$note": "Faithful freeze: portal 'tech' strings are prototype-era "
        "(e.g. 'Next.js 15 + RN', 'Metabase + Grafana') and are "
        "SUPERSEDED for production by D-026 (Next.js 16.3, no RN), "
        "D-027 (Flutter) and the L4 baseline (Superset+Grafana) — "
        "see docs/navigation/registry-to-production-mapping.md. "
        "Journey names are EN-only in the frozen payload; production "
        "Bengali journey names land with the PP5 marketing shell.",
        "areas": areas,
        "modules": modules,
        "portals": structural["portals"],
        "journeys": structural["journeys"],
        "personas": structural["personas"],
        "counts": counts,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(registry, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        f"generate-nav-registry: {len(modules)} modules, {counts['screens']} "
        f"screens, {counts['reports']} reports, {counts['forms']} forms, "
        f"{counts['functions']} functions -> {OUT.relative_to(REPO)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
