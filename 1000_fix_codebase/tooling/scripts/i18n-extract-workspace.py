#!/usr/bin/env python3
"""i18n-extract-workspace — inventory every user-visible literal in the P03
workspace (p03_workspace.xml text nodes + label attributes, p03_workspace.js
toasts/titles/labels) so the bn dictionary in p03_i18n.js can be authored
completely. Read-only: prints a JSON list of unique strings with usage
counts and where they occur (file:kind)."""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "addons" / "platform" / "cd_p03_portal" / "static" / "src"

# text worth translating: has a letter, is not an expression/whitespace
TEXT_RE = re.compile(r">([^<>{}]*[A-Za-z\u0980-\u09FF][^<>{}]*)<")
ATTR_RE = re.compile(r'\b(placeholder|aria-label|title)="([^"{}<>]*[A-Za-z][^"{}<>]*)"')
LABEL_ATTRS = ("placeholder", "aria-label", "title")
TOAST_RE = re.compile(r'showToast\(\s*"([^"{}]+)"\s*[,)]')
SIMPLE_STR_RE = re.compile(r'"([A-Za-z][A-Za-z0-9 ,\.\-\u2014\u2019\?:%!/\(\)\u0980-\u09FF]{3,})"')


def looks_translatable(text: str) -> bool:
    t = text.strip()
    if not t:
        return False
    if not re.search(r"[A-Za-z]", t):  # Bangla-only handled separately; skip
        return False
    # skip pure symbols/numbers/emoji
    return bool(re.search(r"[A-Za-z]{2}", t))


def main() -> None:
    inventory: dict[str, dict] = {}

    def add(text: str, where: str) -> None:
        key = " ".join(text.split())  # normalise inner whitespace
        if not looks_translatable(key):
            return
        entry = inventory.setdefault(key, {"count": 0, "where": set()})
        entry["count"] += 1
        entry["where"].add(where)

    xml = (SRC / "p03_workspace.xml").read_text(encoding="utf-8")
    for m in TEXT_RE.finditer(xml):
        add(m.group(1), "p03_workspace.xml:text")
    for m in ATTR_RE.finditer(xml):
        add(m.group(2), f"p03_workspace.xml:{m.group(1)}")

    js = (SRC / "p03_workspace.js").read_text(encoding="utf-8")
    for m in TOAST_RE.finditer(js):
        add(m.group(1), "p03_workspace.js:toast")
    # state labels map + chart/tab titles: single-quoted and double-quoted
    for m in re.finditer(r"'([A-Za-z][A-Za-z0-9 ,\.\-\u2014\?:%!]{3,})'", js):
        add(m.group(1), "p03_workspace.js:sq")
    for m in SIMPLE_STR_RE.finditer(js):
        add(m.group(1), "p03_workspace.js:dq")

    # tellme xml too
    tm = (SRC / "p03_tellme.xml").read_text(encoding="utf-8")
    for m in TEXT_RE.finditer(tm):
        add(m.group(1), "p03_tellme.xml:text")
    for m in ATTR_RE.finditer(tm):
        add(m.group(2), f"p03_tellme.xml:{m.group(1)}")

    out = [
        {"text": k, "count": v["count"], "where": sorted(v["where"])}
        for k, v in sorted(inventory.items(), key=lambda kv: (-kv[1]["count"], kv[0]))
    ]
    print(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"\n# unique strings: {len(out)}", file=sys.stderr)


if __name__ == "__main__":
    main()
