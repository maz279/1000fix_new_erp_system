#!/usr/bin/env python3
"""check-nav-registry — PP0-M03-T01 (the prototype's _audit_meta.js logic as CI).

Validates contracts/nav/registry.json — the production navigation universe:

  1. headline counts      12 areas · 12 portals · 67 modules · 278 groups ·
                          823 screens · 346 reports · 266 forms · 600 sub
                          triples · 5,100 functions · 10 journeys · 4 personas
  2. function ledger      freg.src == sum(sub counts) for EVERY module
  3. screen integrity     no duplicate screen ids
  4. area integrity       no orphan area->module references; no module
                          without an area
  5. i18n parity          the prototype FX_I18N catalogues carry identical
                          key sets in EN and বাংলা (74/74)
  6. freshness            regeneration is byte-identical (registry not stale
                          against the frozen prototype)

Exit: 0 OK / 1 violations.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "contracts" / "nav" / "registry.json"
GENERATOR = REPO / "tooling" / "generators" / "generate-nav-registry.py"
FRONT_I18N = REPO.parent / "Front_end" / "js" / "i18n.js"

EXPECT = {
    "areas": 12,
    "portals": 12,
    "modules": 67,
    "groups": 278,
    # 2026-11-09 partner-ledger rollout: +4 M19 screens, +2 reports, +1 form
    # (+4 function tokens); M19 freg 'Journals' row 11 -> 15.
    "screens": 827,
    "reports": 348,
    "forms": 267,
    "sub_triples": 600,
    "functions": 5104,
    "journeys": 10,
    "personas": 4,
}


def main() -> int:
    if not REGISTRY.exists():
        print(
            "nav-registry: FAIL — contracts/nav/registry.json missing "
            "(run tooling/generators/generate-nav-registry.py)"
        )
        return 1
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    v: list[str] = []

    # 1 — headline counts (recomputed from the tree, not trusted from the block)
    modules = reg["modules"]
    counts = {
        "areas": len(reg["areas"]),
        "portals": len(reg["portals"]),
        "modules": len(modules),
        "groups": sum(len(m["groups"]) for m in modules),
        "screens": sum(len(g["screens"]) for m in modules for g in m["groups"]),
        "reports": sum(len(m["reports"]) for m in modules),
        "forms": sum(len(m["forms"]) for m in modules),
        "sub_triples": sum(len(m["freg"]["sub"]) for m in modules),
        "functions": sum(t[2] for m in modules for t in m["freg"]["sub"]),
        "journeys": len(reg["journeys"]),
        "personas": len(reg["personas"]),
    }
    for key, got in counts.items():
        if got != EXPECT[key]:
            v.append(f"count {key}: {got} != {EXPECT[key]}")
    if reg.get("counts") != counts:
        v.append("counts block stale vs recomputed tree")

    # 2 — function ledger integrity per module
    for m in modules:
        sub_sum = sum(t[2] for t in m["freg"]["sub"])
        if m["freg"]["src"] != sub_sum:
            v.append(f"freg ledger mismatch {m['id']}: src={m['freg']['src']} != sub-sum={sub_sum}")

    # 3 — screen id uniqueness
    ids = [s["id"] for m in modules for g in m["groups"] for s in g["screens"]]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        v.append(f"duplicate screen ids: {sorted(dupes)}")

    # 4 — area/module integrity, both directions
    mod_ids = {m["id"] for m in modules}
    for area in reg["areas"]:
        for mid in area["modules"]:
            if mid not in mod_ids:
                v.append(f"orphan area ref {area['id']} -> {mid}")
    area_of = {mid: a["id"] for a in reg["areas"] for mid in a["modules"]}
    for m in modules:
        if m["id"] not in area_of:
            v.append(f"module {m['id']} belongs to no area")
        elif area_of[m["id"]] != m["area"]:
            v.append(f"module {m['id']} area {m['area']} != area list {area_of[m['id']]}")

    # 5 — prototype i18n catalogue parity (EN <-> BN identical key sets)
    src = FRONT_I18N.read_text(encoding="utf-8")
    en_block = re.split(r"en:\s*\{", src, maxsplit=1)[1]
    en_block = re.split(r"\},?\s*\n\s*bn:\s*\{", en_block)[0]
    bn_block = re.split(r"bn:\s*\{", src, maxsplit=1)[1].split("\n};")[0]
    key_re = re.compile(r"\b([a-z0-9_]+):'")
    en_keys = set(key_re.findall(en_block))
    bn_keys = set(key_re.findall(bn_block))
    if en_keys != bn_keys:
        v.append(
            f"i18n parity broken: en-only={sorted(en_keys - bn_keys)} "
            f"bn-only={sorted(bn_keys - en_keys)}"
        )
    elif len(en_keys) != 74:
        v.append(f"i18n catalogue expected 74 keys per locale, got {len(en_keys)}")

    # 6 — freshness: regenerating must be byte-identical
    before = REGISTRY.read_bytes()
    result = subprocess.run(
        [sys.executable, str(GENERATOR)], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        v.append("generator failed against the frozen prototype")
    elif REGISTRY.read_bytes() != before:
        v.append(
            "registry was stale — regenerated now; commit the fresh file "
            "with the payload change that caused it"
        )

    if v:
        for line in v:
            print("nav-registry: FAIL —", line)
        return 1
    print(
        f"nav-registry: OK — {counts['modules']} modules, {counts['groups']} "
        f"groups, {counts['screens']} screens, {counts['reports']} reports, "
        f"{counts['forms']} forms, {counts['functions']} functions, "
        f"{counts['journeys']} journeys; ledger, ids, areas, i18n parity, "
        f"freshness all verified"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
