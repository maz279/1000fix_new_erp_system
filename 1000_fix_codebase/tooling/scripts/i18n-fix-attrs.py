#!/usr/bin/env python3
"""Repair the malformed t()/t-att wraps emitted by the first transformer
pass and re-emit them XML-safe.

Correct form (single-quote XML attribute, double-quote JS string):
    t-esc='t("Approve & Post")'
    t-att-placeholder='t("— pick —")'
XML-escaping inside the single-quoted attribute: & &lt; &gt; &apos;
JS-escaping inside the double-quoted string: backslash and double-quote.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
XML = ROOT / "addons" / "platform" / "cd_p03_portal" / "static" / "src" / "p03_workspace.xml"

BAD = re.compile(r'(-esc|-placeholder|-aria-label|-title)="t\((?:\'([^"\']*)\'|"([^"\']*))\)"')


def emit(key: str) -> str:
    js = '"' + key.replace("\\", "\\\\").replace('"', '\\"') + '"'
    xml = js.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;")
    return f"'t({xml})'"


def main() -> None:
    text = XML.read_text(encoding="utf-8")
    count = 0

    def repl(m):
        nonlocal count
        key = m.group(2) if m.group(2) is not None else m.group(3)
        # the first pass left keys UNESCAPED at the JS level (raw & < >),
        # which is what the dictionary expects — keep them raw.
        count += 1
        return emit(key)

    out = BAD.sub(repl, text)
    XML.write_text(out, encoding="utf-8", newline="\n")
    print(f"repaired {count} wraps")


if __name__ == "__main__":
    main()
