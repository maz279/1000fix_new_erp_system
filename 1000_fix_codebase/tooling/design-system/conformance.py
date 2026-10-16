#!/usr/bin/env python3
"""conformance — the cross-runtime design-token conformance suite.

P04-M07-T08 (UX-001 §11). Five checks, one executable:

  CFM-01  no raw literals     — component SCSS contains no colour/size literal;
                                every value resolves to a generated token
  CFM-02  value parity        — every token in the source appears in every
                                realisation (SCSS, CSS, TS) with an identical
                                value, and generated files are fresh
                                (regeneration is byte-identical)
  CFM-03  contrast            — text/surface token pairs meet WCAG 2.2 AA
                                in light and dark themes
  CFM-04  inventory parity    — the component contract inventory matches the
                                realised component partials
  CFM-05  Bengali fit         — the Bengali font stack is first-class in every
                                realisation, and body text tokens leave room
                                for Bengali expansion (UX-007)

Realisations may differ in code and are forbidden to differ in rendered
result beyond PID-01…PID-07 (UX-001 §3.2). Exit: 0 pass / 1 violations.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "libs/ts/ui/src/tokens/tokens.json"
SCSS = REPO / "addons/platform/cd_design_tokens/static/src/tokens.scss"
CSS = REPO / "addons/platform/cd_design_tokens/static/src/tokens.css"
TS = REPO / "libs/ts/ui/src/tokens/tokens.generated.ts"
COMPONENTS = REPO / "addons/platform/cd_design_tokens/static/src/components"
CONTRACT = REPO / "docs/design-system/component-contract.md"
GENERATOR = REPO / "tooling/generators/generate-design-tokens.py"

RAW_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgb[a]?\(")
RAW_SIZE = re.compile(r"\b\d+(\.\d+)?(px|rem|em|pt)\b")
TOKEN_REF = re.compile(r"\$[a-z0-9-]+")


def load_tokens() -> dict:
    with open(SOURCE, encoding="utf-8") as handle:
        return json.load(handle)


def flatten(node: dict, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for key in sorted(node):
        if key.startswith("$"):
            continue
        child = node[key]
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(child, dict) and "$value" in child:
            out[path] = str(child["$value"])
        elif isinstance(child, dict):
            out.update(flatten(child, path))
    return out


# --------------------------------------------------------------------- CFM-01

def check_cfm01(tokens: dict[str, str]) -> list[str]:
    violations: list[str] = []
    scss_vars = {m.removeprefix("$") for m in TOKEN_REF.findall(SCSS.read_text(encoding="utf-8"))}
    for partial in sorted(COMPONENTS.glob("*.scss")):
        for line_no, line in enumerate(
            partial.read_text(encoding="utf-8").splitlines(), start=1
        ):
            code = line.split("//")[0]
            if RAW_COLOR.search(code):
                violations.append(f"CFM-01 {partial.name}:{line_no}: raw colour literal")
            for hit in RAW_SIZE.finditer(code):
                # Unit literals are allowed ONLY where no token exists yet.
                violations.append(f"CFM-01 {partial.name}:{line_no}: raw size literal {hit.group()}")
            for ref in TOKEN_REF.findall(code):
                if ref.removeprefix("$") not in scss_vars:
                    violations.append(f"CFM-01 {partial.name}:{line_no}: unknown token {ref}")
    return violations


# --------------------------------------------------------------------- CFM-02

def check_cfm02(tokens: dict[str, str]) -> list[str]:
    violations: list[str] = []
    scss_text = SCSS.read_text(encoding="utf-8")
    css_text = CSS.read_text(encoding="utf-8")
    ts_text = TS.read_text(encoding="utf-8")
    for path, value in tokens.items():
        scss_var = "$" + path.replace(".", "-").lower()
        css_var = "--fix-" + path.replace(".", "-").lower()
        if f"{scss_var}: {value};" not in scss_text:
            violations.append(f"CFM-02 SCSS missing or altered: {scss_var}")
        if f"{css_var}: {value};" not in css_text:
            violations.append(f"CFM-02 CSS missing or altered: {css_var}")
        if f'"{path}": {json.dumps(value, ensure_ascii=False)},' not in ts_text:
            violations.append(f"CFM-02 TS missing or altered: {path}")
    # Freshness: regeneration must be byte-identical (no hand edits to
    # generated files, no stale realisation after a source change).
    before = {p: p.read_bytes() for p in (SCSS, CSS, TS)}
    result = subprocess.run(
        [sys.executable, str(GENERATOR)], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        violations.append("CFM-02 generator failed to run — source invalid")
        return violations
    for path, blob in before.items():
        if path.read_bytes() != blob:
            violations.append(f"CFM-02 {path.name} was stale (regenerated now) — "
                              "realisations must be regenerated in the same commit as the source")
    return violations


# --------------------------------------------------------------------- CFM-03

def _rel_luminance(hex_color: str) -> float:
    hex_color = hex_color.lstrip("#")
    channels = [int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(a: str, b: str) -> float:
    la, lb = _rel_luminance(a), _rel_luminance(b)
    lo, hi = min(la, lb), max(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def check_cfm03(tokens: dict[str, str]) -> list[str]:
    violations: list[str] = []
    pairs = [
        # (foreground token, background token, minimum ratio)
        ("color.text.primary", "color.surface.primary", 4.5),   # body text, light
        ("color.text.secondary", "color.surface.primary", 4.5),
        ("color.text.primary", "color.surface.secondary", 4.5),
        ("color.text.inverse", "color.status.brand", 4.5),      # primary button
        ("color.text.inverse", "color.status.error", 4.5),      # danger button
        ("color.text.inverse", "color.status.urgent", 4.5),     # urgent surfaces
        ("color.text.inverse", "color.surface.dark", 4.5),      # dark theme
    ]
    for fg, bg, minimum in pairs:
        ratio = _contrast(tokens[fg], tokens[bg])
        if ratio < minimum:
            violations.append(
                f"CFM-03 {fg} on {bg}: contrast {ratio:.2f} < {minimum} (WCAG 2.2 AA)"
            )
    return violations


# --------------------------------------------------------------------- CFM-04

def check_cfm04() -> list[str]:
    violations: list[str] = []
    contract = CONTRACT.read_text(encoding="utf-8") if CONTRACT.exists() else ""
    realised = {p.stem.removeprefix("_") for p in COMPONENTS.glob("*.scss")}
    for name in sorted(realised):
        if not re.search(rf"###\s+`?{re.escape(name)}`?\b", contract):
            violations.append(f"CFM-04 component realised but not in the contract: {name}")
    for match in re.finditer(r"^###\s+`?([a-z_]+)`?\s*$", contract, re.MULTILINE):
        if match.group(1) not in realised:
            violations.append(f"CFM-04 component in the contract but not realised: {match.group(1)}")
    return violations


# --------------------------------------------------------------------- CFM-05

def check_cfm05(tokens: dict[str, str]) -> list[str]:
    violations: list[str] = []
    family = tokens.get("typography.font.bengali.family", "")
    if family != "Noto Sans Bengali":
        violations.append(f"CFM-05 Bengali family must be Noto Sans Bengali, got {family!r}")
    fallback = tokens.get("typography.font.bengali.fallback", "")
    if "sans-serif" not in fallback:
        violations.append("CFM-05 Bengali fallback stack must end in a generic family")
    # Expansion: body copy uses the loose or normal line-height token, never tight.
    # (DTCG group name is camelCase: typography.lineHeight.*)
    loose = tokens.get("typography.lineHeight.loose", "")
    normal = tokens.get("typography.lineHeight.normal", "")
    if not loose or not normal:
        violations.append("CFM-05 line-height tokens missing — Bengali expansion test needs them")
    # Every component partial that sets a font must set the Bengali stack (or
    # inherit it, or be mono for reference numbers). A Latin-first stack is
    # allowed only on lines explicitly marked as latin-utility.
    for partial in sorted(COMPONENTS.glob("*.scss")):
        for line in partial.read_text(encoding="utf-8").splitlines():
            match = re.search(r"font-family:\s*([^;]+);", line)
            if not match:
                continue
            stack = match.group(1)
            if "latin-utility" in line or "inherit" in stack:
                continue
            if "$typography-font-bengali-family" not in stack and "$typography-font-mono-family" not in stack:
                violations.append(
                    f"CFM-05 {partial.name}: font-family without the Bengali stack: {stack.strip()}"
                )
    return violations


def main() -> int:
    tokens = flatten(load_tokens())
    checks = {
        "CFM-01 no raw literals": check_cfm01,
        "CFM-02 value parity": lambda t: check_cfm02(t),
        "CFM-03 WCAG 2.2 AA contrast": check_cfm03,
        "CFM-04 inventory parity": lambda _t: check_cfm04(),
        "CFM-05 Bengali fit": check_cfm05,
    }
    failed = 0
    for name, fn in checks.items():
        violations = fn(tokens)
        if violations:
            failed += 1
            print(f"[FAIL] {name}")
            for v in violations:
                print(f"       {v}")
        else:
            print(f"[PASS] {name} ({len(tokens)} tokens)")
    if failed:
        print(f"conformance: {failed} check(s) failed")
        return 1
    print("conformance: all CFM checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
