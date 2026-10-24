#!/usr/bin/env python3
"""generate-prototype-copy-pack — PP0-M02-T01.

Merges the prototype's bilingual catalogues into the W1 copy library as one
generated pack (UI-900), so `extract-ui-copy.py` regenerates the runtime
registry with them:

  js/i18n.js FX_I18N  74 keys per locale  -> proto.shell.*
  index.html LAND_I18N 34 durable keys    -> proto.land.*   (40 keys total;
                               5 prototype-meta keys excluded: live/ft/st1/
                               st2/st3; 1 locale-neutral punctuation key
                               excluded: h1c (" —" — identical in EN and BN,
                               owned by the landing component, not copy)
  nav_data*.js areas   12                 -> nav.area.*
  nav_data*.js modules 67                 -> nav.module.*
  demo_data.js PORTALS 12 (EN) + authored BN -> nav.portal.*

The generator READS the prototype payloads (read-only reference, PP0-M05) and
WRITES only the pack. Re-running is idempotent (byte-identical output).

Exit: 0 written / 1 parse failure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FRONT = REPO.parent / "Front_end"
OUT = (
    REPO.parent
    / "project_content"
    / "03_UI_Copy_and_Microcopy"
    / "03A_Cross_Cutting"
    / "UI-900_Prototype_Shell_and_Landing_Copy_Pack.md"
)

BENGALI = re.compile(r"[\u0980-\u09FF]")

# Landing keys that describe the product (durable). The five excluded keys
# (live, ft, st1..st3) describe the PROTOTYPE (version line, demo login,
# verification badges) and must not reach production copy (data strategy §3).
LAND_KEYS = [
    "h1a",
    "h1b",
    "h1d",
    "lede",
    "f1",
    "f2",
    "f3",
    "f4",
    "f5",
    "s1",
    "s2",
    "s3",
    "s4",
    "s5",
    "s6",
    "jh",
    "js",
    "ph",
    "ps",
    "p1t",
    "p1d",
    "p2t",
    "p2d",
    "p3t",
    "p3d",
    "p4t",
    "p4d",
    "mh",
    "ms",
    "pth",
    "pts",
    "dh",
    "ds",
    "jn1",
]
# 34 product keys. Excluded: live/ft/st1/st2/st3 (prototype-meta) and h1c
# (locale-neutral punctuation " —", owned by the component).
LAND_DURABLE = LAND_KEYS

# Bengali portal names authored for the production landing (the prototype's
# portal cards are EN-only; the pack is the reviewed BN home for them).
PORTAL_BN = {
    "P01": "গ্রাহক সেলফ-সার্ভিস পোর্টাল",
    "P02": "টেকনিশিয়ান মোবাইল অ্যাপ",
    "P03": "অ্যাডমিন অপারেশন্স পোর্টাল",
    "P04": "কর্পোরেট B2B পোর্টাল",
    "P05": "ভেন্ডর ও সাপ্লায়ার পোর্টাল",
    "P06": "অ্যানালিটিক্স ও এক্সিকিউটিভ ড্যাশবোর্ড",
    "P07": "মার্কেটপ্লেস সেলার পোর্টাল",
    "P08": "ব্র্যান্ড পার্টনার পোর্টাল",
    "P09": "লজিস্টিক্স ও রাইডার অ্যাপ",
    "P10": "কন্টাক্ট সেন্টার এজেন্ট কনসোল",
    "P11": "ফিল্ড অডিটর ও কোয়ালিটি অ্যাপ",
    "P12": "পার্টনার ও রেফারেল পোর্টাল",
}


def parse_kv_block(text: str) -> dict[str, str]:
    # Keys sit several per line in the prototype payloads — no line anchor.
    out: dict[str, str] = {}
    for m in re.finditer(r"\b([a-z0-9_]+):'((?:[^'\\]|\\.)*)'", text):
        out[m.group(1)] = m.group(2).replace("\\'", "'")
    return out


def load_i18n() -> tuple[dict[str, str], dict[str, str]]:
    src = (FRONT / "js" / "i18n.js").read_text(encoding="utf-8")
    en_block = re.split(r"en:\s*\{", src, maxsplit=1)[1]
    en_block = re.split(r"\},?\s*\n\s*bn:\s*\{", en_block)[0]
    bn_block = re.split(r"bn:\s*\{", src, maxsplit=1)[1].split("\n};")[0]
    return parse_kv_block(en_block), parse_kv_block(bn_block)


def load_landing() -> tuple[dict[str, str], dict[str, str]]:
    html = (FRONT / "index.html").read_text(encoding="utf-8")
    bn_block = re.search(r"var LAND_I18N = \{\s*bn:\s*\{(.*?)\n\s*\},", html, re.S)
    if not bn_block:
        raise SystemExit("generate-prototype-copy-pack: LAND_I18N.bn not found")
    bn = parse_kv_block(bn_block.group(1))
    en: dict[str, str] = {}
    for key in LAND_DURABLE:
        if key == "jn1":
            # jn1 is composed in JS (steps count + label), not a data-i18n
            # element; its English lives in the en:{} block.
            m = re.search(r"en:\s*\{\s*jn1:'([^']*)'", html)
            if not m:
                raise SystemExit("generate-prototype-copy-pack: en.jn1 not found")
            en[key] = m.group(1).strip()
            continue
        m = re.search(r'data-i18n="%s"[^>]*>([^<]*)' % key, html)
        if not m:
            raise SystemExit(f"generate-prototype-copy-pack: landing en missing for {key}")
        en[key] = m.group(1).strip()
    # s5's visible text is split across a sibling <b>ISO 9001</b> + the span
    # (":2015 certified operations") — compose the full English for the pack.
    en["s5"] = "ISO 9001:2015 certified operations"
    for key, val in en.items():
        if val.startswith((": ", "; ", ", ", ". ")) or not val:
            raise SystemExit(
                f"generate-prototype-copy-pack: landing en for " f"{key} looks truncated: {val!r}"
            )
    return en, bn


def load_areas_modules() -> tuple[list[dict], list[dict]]:
    all3 = ""
    for name in ("nav_data.js", "nav_data2.js", "nav_data3.js"):
        all3 += (FRONT / "js" / name).read_text(encoding="utf-8")
    areas = []
    for m in re.finditer(r"\{ id:'(A\d+)', key:'[a-z]+',\s*en:'([^']*)',\s*bn:'([^']*)'", all3):
        areas.append({"id": m.group(1), "en": m.group(2), "bn": m.group(3)})
    modules = []
    for m in re.finditer(r"\b(M\d{2}): \{ area:'(A\d+)', en:'([^']*)', bn:'([^']*)'", all3):
        modules.append({"id": m.group(1), "en": m.group(3), "bn": m.group(4)})
    for m in re.finditer(
        r"FX_MODULES\.(M\d{2}) = \{ area:'(A\d+)', en:'([^']*)', bn:'([^']*)'", all3
    ):
        modules.append({"id": m.group(1), "en": m.group(3), "bn": m.group(4)})
    return areas, modules


def load_portals() -> list[tuple[str, str]]:
    demo = (FRONT / "js" / "demo_data.js").read_text(encoding="utf-8")
    m = re.search(r"D\.PORTALS\s*=\s*\[(.*?)\n\s*\];", demo, re.S)
    if not m:
        raise SystemExit("generate-prototype-copy-pack: FX_DEMO.PORTALS not found")
    out = []
    # Rows are [id, name, users, volume, tech, [caps]] — anchor on the row id.
    for row in re.finditer(r"\[\s*'(P\d\d)'\s*,\s*'([^']*)'", m.group(1)):
        out.append((row.group(1), row.group(2)))
    return out


def esc(text: str) -> str:
    return text.replace("|", "\\|")


def main() -> int:
    en_i18n, bn_i18n = load_i18n()
    if len(en_i18n) != 74 or len(bn_i18n) != 74 or set(en_i18n) != set(bn_i18n):
        print(
            f"generate-prototype-copy-pack: FX_I18N shape unexpected "
            f"(en={len(en_i18n)} bn={len(bn_i18n)})"
        )
        return 1
    en_land, bn_land = load_landing()
    if len(bn_land) != 40:
        print(f"generate-prototype-copy-pack: LAND_I18N expected 40 keys, got {len(bn_land)}")
        return 1
    areas, modules = load_areas_modules()
    if len(areas) != 12 or len(modules) != 67:
        print(f"generate-prototype-copy-pack: areas={len(areas)} modules={len(modules)}")
        return 1
    portals = load_portals()
    if len(portals) != 12:
        print(f"generate-prototype-copy-pack: portals={len(portals)}")
        return 1

    rows: list[tuple[str, str, str, str]] = []  # (label, key, en, bn)
    for key in sorted(en_i18n):
        rows.append((f"Shell · {key}", f"proto.shell.{key}", en_i18n[key], bn_i18n[key]))
    for key in LAND_DURABLE:
        if key not in bn_land:
            print(f"generate-prototype-copy-pack: landing key {key} missing bn")
            return 1
        rows.append((f"Landing · {key}", f"proto.land.{key}", en_land[key], bn_land[key]))
    for a in areas:
        rows.append((f"Area {a['id']}", f"nav.area.{a['id'].lower()}", a["en"], a["bn"]))
    for mod in sorted(modules, key=lambda x: x["id"]):
        rows.append(
            (f"Module {mod['id']}", f"nav.module.{mod['id'].lower()}", mod["en"], mod["bn"])
        )
    for pid, name_en in portals:
        rows.append((f"Portal {pid}", f"nav.portal.{pid.lower()}", name_en, PORTAL_BN[pid]))

    for _, _, _, bn in rows:
        if not BENGALI.search(bn):
            print("generate-prototype-copy-pack: a row carries no Bengali script")
            return 1

    lines = [
        "# UI-900 — Prototype Shell & Landing Copy Pack (generated)",
        "",
        "id: UI-900",
        "wave: W1",
        "",
        "Generated by `tooling/scripts/generate-prototype-copy-pack.py` from the",
        "read-only prototype payloads (PP0-M02-T01). Do not edit by hand — the",
        "prototype is the source; re-run the generator after any (tracked) prototype",
        "change. LAND_I18N keys `live`, `ft`, `st1`, `st2`, `st3` are prototype-meta",
        "strings (version line, demo login, verification badges) and are deliberately",
        "NOT ported (data strategy §3: no demo/meta copy in production).",
        "",
        "| Label | Key | English | বাংলা |",
        "|---|---|---|---|",
    ]
    lines += [f"| {esc(label)} | `{key}` | {esc(en)} | {esc(bn)} |" for label, key, en, bn in rows]
    lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"generate-prototype-copy-pack: {len(rows)} inline keys -> {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
