#!/usr/bin/env python3
"""Recover the damaged attribute wraps using the PRE-TRANSFORM inventory
(p03_strings_tmp.json), which recorded every string's original attribute
kind (placeholder / aria-label / title) from the untouched file.

Damage forms (from the bad repair pass):
    t't("K")'        was  t-esc='...'            (unambiguous)
    t-att't("K")'    was  t-att-{placeholder|aria-label|title}='...'

Recovery rule per key K:
  * kinds = inventory kinds for K among placeholder/aria-label/title
  * if len(kinds) == 1 → that attribute
  * if len(kinds) > 1  → position within its tag (source attr order was
    placeholder, aria-label, title — the transform preserved positions)
  * if K unknown (no attr record) → element heuristic:
    input/textarea → placeholder; button/select/svg/*[role] → aria-label;
    span/div → title
"""

from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "addons" / "platform" / "cd_p03_portal" / "static" / "src"
XML = SRC / "p03_workspace.xml"
INV = ROOT / "p03_strings_tmp.json"

inventory = json.loads(INV.read_text(encoding="utf-8"))
kinds_by_key: dict[str, set[str]] = {}
for row in inventory:
    ks = set()
    for where in row["where"]:
        if ":placeholder" in where:
            ks.add("placeholder")
        elif ":aria-label" in where:
            ks.add("aria-label")
        elif ":title" in where:
            ks.add("title")
    if ks:
        kinds_by_key.setdefault(row["text"], set()).update(ks)

ATTR_ORDER = ["placeholder", "aria-label", "title"]


def attr_for(key: str, tag_head: str, nth_in_tag: int, total_in_tag: int) -> str:
    ks = sorted(kinds_by_key.get(key, set()), key=ATTR_ORDER.index)
    if len(ks) == 1:
        return ks[0]
    if len(ks) > 1:
        if total_in_tag == len(ks):
            return ks[min(nth_in_tag, len(ks) - 1)]
        return ks[0]
    # heuristic on the element
    head = tag_head.lower()
    if "<input" in head or "<textarea" in head:
        return "placeholder"
    if "<button" in head or "<select" in head or "<svg" in head or "role=" in head:
        return "aria-label"
    return "title"


def emit_t_attr(attr: str, key: str) -> str:
    js = '"' + key.replace("\\", "\\\\").replace('"', '\\"') + '"'
    xml = js.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;")
    return f"t-att-{attr}='t({xml})'"


def emit_t_esc(key: str) -> str:
    js = '"' + key.replace("\\", "\\\\").replace('"', '\\"') + '"'
    xml = js.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;")
    return f"t-esc='t({xml})'"


def main() -> None:
    text = XML.read_text(encoding="utf-8")

    # 1) restore the unambiguous t-esc wraps: t't("K")' → t-esc='t("K")'
    esc_bad = re.compile(r"\bt't\((\"(?:[^\"\\]|\\.)*\")\)'")
    n_esc = 0

    def esc_repl(m):
        nonlocal n_esc
        n_esc += 1
        key = json.loads(m.group(1))
        return emit_t_esc(key)

    text = esc_bad.sub(esc_repl, text)

    # 2) recover t-att wraps tag by tag (context needed for heuristics)
    att_bad = re.compile(r"t-att't\((\"(?:[^\"\\]|\\.)*\")\)'")
    n_att = 0
    # split into tags cheaply: find each damaged occurrence, then scan back
    # to the nearest '<' that opened its element
    matches = list(att_bad.finditer(text))
    repaired_spans = []
    for m in matches:
        key = json.loads(m.group(1))
        # scan back to the element open for this attribute
        back = text.rfind("<", 0, m.start())
        # walk back over continuation lines (attr on its own line): keep
        # going while the previous '<' is a t- tag, not the element open
        while back != -1 and text[back : back + 2] in ("<t", "</"):
            back = text.rfind("<", 0, back)
        tag_head = text[back : m.start()] if back != -1 else ""
        # how many damaged att wraps share this element open?
        nth = 0
        total = 0
        for other in matches:
            oback = text.rfind("<", 0, other.start())
            while oback != -1 and text[oback : oback + 2] in ("<t", "</"):
                oback = text.rfind("<", 0, oback)
            if oback == back:
                total += 1
                if other.start() < m.start():
                    nth += 1
        attr = attr_for(key, tag_head, nth, total)
        repaired_spans.append((m.start(), m.end(), emit_t_attr(attr, key)))
        n_att += 1

    for s, e, rep in reversed(repaired_spans):
        text = text[:s] + rep + text[e:]

    XML.write_text(text, encoding="utf-8", newline="\n")
    print(f"restored t-esc: {n_esc} | recovered t-att: {n_att}")


if __name__ == "__main__":
    main()
