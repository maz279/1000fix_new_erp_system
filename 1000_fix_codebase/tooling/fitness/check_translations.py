#!/usr/bin/env python3
"""FF-25 — Translation completeness check (DoD-08, AS-12).

Per-field check: scans every model class under addons/ (``_name`` in the
fix.* / residency.* namespace, test modules excluded) for user-facing fields
- fields that carry a ``string=`` label. Each such field MUST have a Bengali
rendering, or its model must be explicitly marked non-user-facing
(EXEMPT_MODELS). A field has a Bengali rendering when ANY of:

  * it has a corresponding Bengali counterpart field ``<field>_bn`` in the
    same model (the ``name`` -> ``name_bn`` convention, DE-17 / BRN-01), or
    it is itself such a ``*_bn`` counterpart;
  * its label has a non-empty msgstr in the module's ``i18n/bn_BD.po`` (the
    Odoo mechanism for label translation - AS-12 "all user-facing strings").

A ``_bn`` counterpart for every labelled field, as an earlier revision of
this docstring demanded, is not possible as written: a Many2one, Boolean,
Date or Integer value has no Bengali counterpart value - its Bengali
rendering IS the translated label. The label-translation leg is the closest
measurable equivalent for those fields, and it is checked per field (a stale
.pot that misses a label does not hide it).

Then FF-24: every module shipping an i18n/ template ships a bn_BD.po that
translates every template msgid.

DoD-08: 100% — not 98%.

Exit: 0 pass / 1 violations (blocking at pre-merge stage 10).
"""

from __future__ import annotations

import ast
import re
import sys
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADDONS = REPO_ROOT / "addons"

# Field types that carry user-visible labels
LABELLED_FIELD_TYPES = {
    "Char",
    "Selection",
    "Many2one",
    "One2many",
    "Many2many",
    "Integer",
    "Float",
    "Monetary",
    "Boolean",
    "Date",
    "Datetime",
    "Text",
    "Html",
    "Binary",
}

# Technical/internal fields - never rendered as a user-facing label
TECHNICAL_FIELDS = {
    "id",
    "create_uid",
    "write_uid",
    "create_date",
    "write_date",
    "active",
    "company_id",
    "currency_id",
    "display_name",
}

MODEL_NAMESPACES = ("fix.", "residency.")

# Models exempt from Bengali-first (internal/technical only)
EXEMPT_MODELS = {
    "residency.mixin",
    "fix.isolation.tier",
    "fix.field.rule",
    "fix.event.outbox",
    "fix.feature.flag",
    "fix.mdm.match.rule",
}

SHOW_VIOLATIONS = 25


@dataclass(frozen=True)
class LabelledField:
    module: str
    path: str
    line: int
    model: str
    field: str
    label: str
    sibling_fields: frozenset[str]


def _module_dir(py: Path, addons: Path) -> Path | None:
    for parent in py.parents:
        if parent == addons.parent:
            return None
        if (parent / "__manifest__.py").is_file():
            return parent
    return None


def _string_label(call: ast.Call) -> str | None:
    for kw in call.keywords:
        if kw.arg == "string" and isinstance(kw.value, ast.Constant):
            value = kw.value.value
            return value if isinstance(value, str) and value.strip() else None
    return None


def iter_labelled_fields(addons: Path = ADDONS) -> Iterator[LabelledField]:
    """Every user-facing (``string=``-labelled) field of every non-exempt model."""
    for py in sorted(addons.rglob("*.py")):
        if "__pycache__" in py.parts or "vendor" in py.parts or "tests" in py.parts:
            continue
        if py.name in ("__init__.py", "__manifest__.py"):
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue
        module_dir = _module_dir(py, addons)
        module = module_dir.name if module_dir else "?"
        rel = py.relative_to(addons.parent).as_posix()
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            model = None
            labelled: list[tuple[str, int, str]] = []
            names: set[str] = set()
            for stmt in cls.body:
                if not (
                    isinstance(stmt, ast.Assign)
                    and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)
                ):
                    continue
                target = stmt.targets[0].id
                value = stmt.value
                if target == "_name" and isinstance(value, ast.Constant):
                    model = value.value if isinstance(value.value, str) else None
                    continue
                if (
                    isinstance(value, ast.Call)
                    and isinstance(value.func, ast.Attribute)
                    and isinstance(value.func.value, ast.Name)
                    and value.func.value.id == "fields"
                    and value.func.attr in LABELLED_FIELD_TYPES
                ):
                    names.add(target)
                    label = _string_label(value)
                    if label and not target.startswith("_") and target not in TECHNICAL_FIELDS:
                        labelled.append((target, stmt.lineno, label))
            # A pure extension (_inherit, no _name): the parent model governs.
            if not model or not model.startswith(MODEL_NAMESPACES) or model in EXEMPT_MODELS:
                continue
            siblings = frozenset(names)
            for field, line, label in labelled:
                yield LabelledField(module, rel, line, model, field, label, siblings)


def has_bengali_rendering(field: LabelledField, translations: dict[str, str]) -> bool:
    if field.field.endswith("_bn") or f"{field.field}_bn" in field.sibling_fields:
        return True
    return bool(translations.get(field.label, "").strip())


def check_field_bengali(addons: Path = ADDONS) -> tuple[int, int, list[LabelledField]]:
    """Per-field check. Returns (fields checked, models carrying a *_bn
    counterpart, violations)."""
    po_cache: dict[str, dict[str, str]] = {}
    checked = 0
    models_with_bn: set[str] = set()
    violations: list[LabelledField] = []
    for field in iter_labelled_fields(addons):
        checked += 1
        if any(name.endswith("_bn") for name in field.sibling_fields):
            models_with_bn.add(field.model)
        if field.module not in po_cache:
            po_cache[field.module] = _module_translations(addons, field)
        if not has_bengali_rendering(field, po_cache[field.module]):
            violations.append(field)
    return checked, len(models_with_bn), violations


def _module_translations(addons: Path, field: LabelledField) -> dict[str, str]:
    module_dir = _module_dir(addons.parent / field.path, addons)
    po = module_dir / "i18n" / "bn_BD.po" if module_dir else None
    if po is None or not po.is_file():
        return {}
    return parse_po_msgstr(po.read_text(encoding="utf-8"))


def main() -> int:
    fields_checked, models_with_bn, field_violations = check_field_bengali()
    print(
        f"translations: {fields_checked} user-facing fields checked per field, "
        f"{models_with_bn} models carry Bengali (_bn) counterpart fields"
    )

    po_failures = check_po_completeness()

    failed = False
    if field_violations:
        failed = True
        per_module = Counter(v.module for v in field_violations)
        print(
            f"translations: FAIL - {len(field_violations)} of {fields_checked} user-facing "
            f"field(s) across {len(per_module)} module(s) have no Bengali rendering "
            "(no <field>_bn counterpart, label untranslated in i18n/bn_BD.po):"
        )
        for module, count in per_module.most_common():
            print(f"  {module}: {count}")
        for v in field_violations[:SHOW_VIOLATIONS]:
            print(f"  {v.path}:{v.line}: {v.model}.{v.field} label {v.label!r}")
        if len(field_violations) > SHOW_VIOLATIONS:
            print(f"  ... {len(field_violations) - SHOW_VIOLATIONS} more")
        print(
            "  remedy: re-extract the module template (tooling/scripts/extract-translations.py) "
            "and translate every label in bn_BD.po, add a <field>_bn counterpart, "
            "or mark the model non-user-facing (EXEMPT_MODELS)."
        )
    if po_failures:
        failed = True
        print(
            f"translations: FAIL - {len(po_failures)} i18n completeness violation(s) (FF-24: 100% before merge):"
        )
        for failure in po_failures:
            print(f"  {failure}")
    if failed:
        return 1
    print(
        f"translations: OK - all {fields_checked} user-facing fields have a Bengali rendering; "
        "every shipped bn_BD.po is 100% translated"
    )
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


_PO_KEYWORD = re.compile(r'^(msgctxt|msgid_plural|msgid|msgstr(?:\[(\d+)\])?)\s+"(.*)"$')
_PO_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"'}


def _po_unescape(text: str) -> str:
    return re.sub(r"\\(.)", lambda m: _PO_ESCAPES.get(m.group(1), "\\" + m.group(1)), text)


def parse_po_entries(text: str) -> list[tuple[str, str, bool]]:
    """(msgid, msgstr, fuzzy) for every entry, unescaped.

    Gettext wraps long strings over continuation lines (``msgid ""`` followed
    by ``"part one "`` / ``"part two"`` lines - Odoo's own export does this);
    the parts are joined. Obsolete (``#~``) entries are skipped and a plural
    entry keeps ``msgstr[0]``.
    """
    entries: list[tuple[str, str, bool]] = []
    current: dict | None = None
    key: str | None = None
    flags: set[str] = set()

    def flush() -> None:
        if current is not None and "msgid" in current:
            entries.append(
                (
                    _po_unescape(current["msgid"]),
                    _po_unescape(current.get("msgstr", "")),
                    current["fuzzy"],
                )
            )

    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#,"):
            flags |= {f.strip() for f in s[2:].split(",")}
        if not s or s.startswith("#"):
            key = None
            continue
        m = _PO_KEYWORD.match(s)
        if m:
            kw, index, value = m.groups()
            if kw == "msgctxt" or (kw == "msgid" and (current is None or "msgid" in current)):
                flush()
                current, flags = {"fuzzy": "fuzzy" in flags}, set()
            if current is None:
                continue
            if kw.startswith("msgstr"):
                if index not in (None, "0"):
                    key = None
                    continue
                kw = "msgstr"
            current[kw], key = value, kw
        elif s.startswith('"') and s.endswith('"') and key and current is not None:
            current[key] += s[1:-1]
    flush()
    return entries


def parse_pot_msgids(text: str) -> list[str]:
    return [msgid for msgid, _, _ in parse_po_entries(text)]


def parse_po_msgstr(text: str) -> dict[str, str]:
    """{msgid: msgstr}; a ``#, fuzzy`` entry counts as untranslated (gettext
    and the translator's own flag say it is not a valid translation yet)."""
    return {msgid: ("" if fuzzy else msgstr) for msgid, msgstr, fuzzy in parse_po_entries(text)}


if __name__ == "__main__":
    sys.exit(main())
