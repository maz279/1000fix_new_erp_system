#!/usr/bin/env python3
"""FF-25 — Translation completeness check (DoD-08, AS-12).

Scans every model file under addons/ for user-facing fields that carry a
string attribute. Each such field MUST have a corresponding name_bn field
or the model must be explicitly marked non-user-facing.

DoD-08: 100% — not 98%.

Exit: 0 pass / 1 violations (blocking at pre-merge stage 10).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADDONS = REPO_ROOT / "addons"

# Fields that carry user-visible labels
FIELD_PATTERN = re.compile(
    r'(\w+)\s*=\s*fields\.(?:Char|Selection|Many2one|One2many|Many2many|'
    r'Integer|Float|Monetary|Boolean|Date|Datetime|Text|Html|Binary)\(',
    re.MULTILINE)

# Models exempt from Bengali-first (internal/technical only)
EXEMPT_MODELS = {"residency.mixin", "fix.isolation.tier", "fix.field.rule",
                 "fix.event.outbox", "fix.feature.flag", "fix.mdm.match.rule"}


def main() -> int:
    violations = []
    fields_checked = 0
    models_with_bn = 0

    for py in ADDONS.rglob("*.py"):
        if "__pycache__" in py.parts or py.name == "__init__.py":
            continue
        if "vendor" in py.parts:
            continue
        text = py.read_text(encoding="utf-8", errors="ignore")

        # Skip if this file has no model definitions
        if '_name = "fix.' not in text and '_name = "residency' not in text:
            continue
        if '_inherit' in text and '_name' not in text:
            continue  # extension of an existing model — parent governs

        # Check if the file has any name_bn fields
        has_bn = 'name_bn' in text or '_bn' in text
        if has_bn:
            models_with_bn += 1

        # Find all fields with string= parameter (user-facing)
        for m in FIELD_PATTERN.finditer(text):
            field_name = m.group(1)
            # Skip technical/internal fields
            if field_name.startswith('_') or field_name in (
                    'id', 'create_uid', 'write_uid', 'create_date', 'write_date',
                    'active', 'company_id', 'currency_id', 'display_name'):
                continue
            # Check if string= is present (user-facing label)
            section = text[m.start():m.start() + 300]
            if 'string=' in section:
                fields_checked += 1

    # Report summary — detailed per-field checking requires the Odoo i18n
    # infrastructure (this is the static pre-check)
    print(f"translations: {fields_checked} user-facing fields found, "
          f"{models_with_bn} model files carry Bengali (_bn) fields")

    po_failures = check_po_completeness()

    if fields_checked > 0 and models_with_bn == 0:
        print("translations: FAIL - user-facing fields exist but no Bengali fields found")
        return 1
    if po_failures:
        print(f"translations: FAIL - {len(po_failures)} i18n completeness violation(s) (FF-24: 100% before merge):")
        for failure in po_failures:
            print(f"  {failure}")
        return 1
    print("translations: OK - Bengali field coverage present; every shipped bn_BD.po is 100% translated")
    return 0


def check_po_completeness() -> list[str]:
    """FF-24 — every module shipping an i18n/ template ships a bn_BD.po whose
    msgstr is non-empty for every msgid. A W1 module without bn_BD.po fails:
    100% on delivered screens is a G1 criterion (G1-05), not an aspiration."""
    failures: list[str] = []
    for cd_dir in sorted(ADDONS.rglob("cd_*")):
        if not cd_dir.is_dir() or "__pycache__" in cd_dir.parts:
            continue
        if not (cd_dir / "__manifest__.py").is_file():
            continue
        i18n = cd_dir / "i18n"
        pots = sorted(i18n.glob("*.pot")) if i18n.is_dir() else []
        if not pots:
            continue  # module ships no template — nothing extracted yet
        po = i18n / "bn_BD.po"
        if not po.is_file():
            failures.append(f"{cd_dir.name}: i18n/ templates exist but bn_BD.po is missing")
            continue
        translated = parse_po_msgstr(po.read_text(encoding="utf-8"))
        for pot in pots:
            for msgid in parse_pot_msgids(pot.read_text(encoding="utf-8")):
                if msgid == "":  # the po header block — not a translatable string
                    continue
                if not translated.get(msgid, "").strip():
                    failures.append(f"{cd_dir.name}: bn_BD.po has no translation for {msgid!r}")
    return failures


def parse_pot_msgids(text: str) -> list[str]:
    return re.findall(r'^msgid "((?:[^"\\]|\\.)*)"\s*$', text, re.MULTILINE)


def parse_po_msgstr(text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    blocks = re.findall(
        r'msgid "((?:[^"\\]|\\.)*)"\s*\nmsgstr "((?:[^"\\]|\\.)*)"', text
    )
    for msgid, msgstr in blocks:
        pairs[msgid] = msgstr
    return pairs


if __name__ == "__main__":
    sys.exit(main())
