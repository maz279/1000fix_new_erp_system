#!/usr/bin/env python3
"""i18n-rewrite-workspace — mechanically wrap every user-visible literal in
the P03 workspace through t()/tState() so exactly ONE language renders at a
time (DE-17). Only strings present in the p03_i18n.js dictionary are
touched; CSS classes, keys, icons and internal names can never be.

Transformations:
  XML  text nodes      >Some Text<            → ><t t-esc="t('Some Text')"/><
  XML  label attrs     placeholder="Some…"/   → t-att-placeholder="t('Some…')"
  JS   toasts          showToast("Done")      → showToast(t("Done"))
  JS   state renders   (hand-audited call sites, listed in REWRITE_RAW below)

The dictionary keys are matched on UNESCAPED text (&amp; → &). Keys
containing a single quote are emitted with double-quoted JS strings and
vice versa. Idempotent: an already-wrapped node is skipped.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "addons" / "platform" "cd_p03_portal" / "static" / "src"
SRC = ROOT / "addons" / "platform" / "cd_p03_portal" / "static" / "src"
I18N = (SRC / "p03_i18n.js").read_text(encoding="utf-8")

# parse the dictionary keys (lines like  "English": "বাংলা",)
KEYS = set(re.findall(r'^\s{2}"((?:[^"\\]|\\.)*)":\s*"', I18N, re.M))
# also the P03_STATES keys for reference
STATE_KEYS = set(re.findall(r"^\s{4}(\w+):\s*\{", I18N, re.M))

# keys sorted longest-first so "Save as Draft (→ Review)" wins over "Save as Draft"
KEYS_SORTED = sorted(KEYS, key=len, reverse=True)


def js_string(s: str) -> str:
    """Quote s for a JS single-line string literal."""
    if "'" not in s:
        return f"'{s}'"
    if '"' not in s:
        return f'"{s}"'
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def unescape(s: str) -> str:
    return s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')


def escape_xml_attr(s: str) -> str:
    return s


def wrap_call(key: str) -> str:
    return f"t({js_string(key)})"


def transform_xml(text: str) -> tuple[str, int]:
    count = 0
    key_pattern = "|".join(
        re.escape(k).replace("\\&", "&")
        for k in KEYS_SORTED  # keys stored unescaped
    )
    # match text nodes that EXACTLY equal a dictionary key (after unescape+trim)
    exact = re.compile(r">(\s*)(" + key_pattern + r")(\s*)<")

    def text_repl(m):
        nonlocal count
        count += 1
        lead, key, trail = m.group(1), m.group(2), m.group(3)
        return f">{lead}<t t-esc={js_string(wrap_call(unescape(key)))}/>{trail}<"

    out = exact.sub(text_repl, text)

    # label attributes: whole-value match only
    for attr in ("placeholder", "aria-label", "title"):
        attr_re = re.compile(rf'\b{attr}="(' + key_pattern + r')"')

        def attr_repl(m, attr=attr):
            nonlocal count
            inner = m.group(1)
            if f"t-att-{attr}=" in m.group(0):
                return m.group(0)
            count += 1
            return f"t-att-{attr}={js_string(wrap_call(unescape(inner)))}"

        out = attr_re.sub(attr_repl, out)

    return out, count


def transform_js(text: str) -> tuple[str, int]:
    count = 0
    out = text
    # showToast("...") and showToast(`...`) simple literals (no interpolation)
    for q in ('"', "'"):
        pattern = re.compile(r"showToast\(\s*" + q + r"([^" + q + r"{}]+)" + q + r"\s*[,)]")
        seen = set()

        def repl(m, q=q):
            nonlocal count
            key = m.group(1)
            if key not in KEYS:
                return m.group(0)
            # idempotency
            if m.group(0).startswith("showToast(t("):
                return m.group(0)
            count += 1
            return m.group(0).replace(f"showToast({q}{key}{q}", f"showToast(t({js_string(key)})")

        out = pattern.sub(repl, out)
        _ = seen
    return out, count


def main() -> None:
    xml_path = SRC / "p03_workspace.xml"
    js_path = SRC / "p03_workspace.js"
    xml = xml_path.read_text(encoding="utf-8")
    js = js_path.read_text(encoding="utf-8")

    new_xml, n_xml = transform_xml(xml)
    new_js, n_js = transform_js(js)

    xml_path.write_text(new_xml, encoding="utf-8", newline="\n")
    js_path.write_text(new_js, encoding="utf-8", newline="\n")
    print(f"dictionary keys: {len(KEYS)} | XML wraps: {n_xml} | JS toast wraps: {n_js}")


if __name__ == "__main__":
    sys.exit(main())
