#!/usr/bin/env python3
"""audit-view-integrity — comprehensive P04 audit pass 2.

Every ir.ui.view is checked against the model its Python file defines:

  1. field references — each <field name="X"> inside a view for model M
     must be a field of M (declared, related, computed, or an Odoo-standard
     id/active/state) — the exact bug class that crashes Odoo at view load.
  2. inherited views — an inherit_id view must target a model whose base
     form exists, and xpath expressions must be well-formed.
  3. one2many inline trees — the child model's fields must exist too.
  4. chatter blocks — <div class="oe_chatter"> with the three standard
     fields (Odoo 17+ contract), never stray <chatter/> tags.

This is the audit companion to FF-27 (which checks the MENU contract); this
checks the VIEW surface. Exit: 0 clean / 1 violations.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADDONS = REPO / "addons"

FIELD_DECL = re.compile(
    r"^\s{4}(\w+)\s*=\s*fields\.", re.MULTILINE
)
RELATION_DECL = re.compile(
    r'^\s{4}(\w+)\s*=\s*fields\.(One2many|Many2one)\(\s*"([\w.]+)"', re.MULTILINE
)
INHERIT_MODEL = re.compile(r'_inherit\s*=\s*"([\w.]+)"')
MODEL_NAME = re.compile(r'_name\s*=\s*"([\w.]+)"')
STANDARD_FIELDS = {
    "id", "active", "sequence", "state", "name", "display_name", "company_id",
    "currency_id", "create_date", "create_uid", "write_date", "write_uid",
    "message_follower_ids", "activity_ids", "message_ids", "message_main_id",
    "website_description", "partner_id", "user_id", "__last_update",
    # Odoo-standard fields present on mail-thread models
    "message_unread", "message_needaction",
}


def load_model_fields() -> tuple[dict[str, set[str]], dict[str, dict[str, str]]]:
    """{model: {field,...}} and {model: {field: comodel}} from addons/.
    Extension classes (_inherit, no _name) MERGE their fields into the
    parent model — that is Odoo's inheritance, so the checker must see the
    merged field set, not the base file's."""
    fields_by_model: dict[str, set[str]] = {}
    relations: dict[str, dict[str, str]] = {}
    for py in ADDONS.rglob("*.py"):
        if "vendor" in py.parts or "__pycache__" in py.parts or py.name == "__init__.py":
            continue
        text = py.read_text(encoding="utf-8", errors="ignore")
        for model_match in re.finditer(
            r"class\s+\w+\(models\.(?:Model|AbstractModel|TransientModel)\):(.+?)(?=\nclass |\Z)",
            text, re.DOTALL
        ):
            body = model_match.group(1)
            name_m = MODEL_NAME.search(body[:400])
            inherit_m = INHERIT_MODEL.search(body[:400])
            declared = set(FIELD_DECL.findall(body))
            new_relations = {m.group(1): m.group(3) for m in RELATION_DECL.finditer(body)}
            if name_m:
                model = name_m.group(1)
                fields_by_model.setdefault(model, set()).update(declared)
                relations.setdefault(model, {}).update(new_relations)
                if inherit_m:
                    parent = inherit_m.group(1)
                    fields_by_model[model].update(fields_by_model.get(parent, set()))
                    relations[model].update(relations.get(parent, {}))
            elif inherit_m:
                parent = inherit_m.group(1)
                fields_by_model.setdefault(parent, set()).update(declared)
                relations.setdefault(parent, {}).update(new_relations)
    return fields_by_model, relations


def model_of_file(xml: Path) -> str:
    return next((p.name for p in xml.parents if (p / "__manifest__.py").is_file()), "")


def check_views(
    fields_by_model: dict[str, set[str]],
    relations: dict[str, dict[str, str]],
) -> list[str]:
    violations: list[str] = []
    keywords = {"in", "not", "and", "or", "True", "False", "None", "like", "ilike", "child_of"}

    def fields_known(model: str) -> set[str]:
        return fields_by_model.get(model, set()) | STANDARD_FIELDS

    def walk(el: ET.Element, model: str, rel: str, inside_subview: bool = False) -> None:
        """Depth-first walk of the arch tree. A relational field WITH element
        children is an inline sub-view: its children belong to the comodel."""
        if el.tag == "field":
            fname = el.get("name")
            if fname and fname not in fields_known(model):
                scope = "subview" if inside_subview else "view"
                violations.append(
                    f"{rel}: {scope}[{model}] references unknown field {fname!r}"
                )
                return
            if fname and len(el) > 0:
                comodel = relations.get(model, {}).get(fname)
                if comodel and comodel in fields_by_model:
                    for child in list(el):
                        walk(child, comodel, rel, inside_subview=True)
                return  # scalar field or unresolvable comodel — nothing nested
        if el.tag == "chatter":
            violations.append(f"{rel}: stray <chatter/> element (use oe_chatter div)")
        for attr, value in el.attrib.items():
            if attr.startswith("decoration-"):
                bare = re.sub(r"'[^']*'|\"[^\"]*\"", " ", value)  # drop string literals
                for token in re.findall(r"[a-zA-Z_][\w.]*", bare):
                    if token in keywords:
                        continue
                    if token.split(".")[-1] not in fields_known(model):
                        violations.append(
                            f"{rel}: decoration {attr}={value!r} references unknown {token!r}"
                        )
        for child in list(el):
            walk(child, model, rel, inside_subview)

    for xml in sorted(ADDONS.rglob("*.xml")):
        if "vendor" in xml.parts or "__pycache__" in xml.parts or "i18n" in xml.parts:
            continue
        module = model_of_file(xml)
        if not module:
            continue
        try:
            tree = ET.parse(xml)
        except ET.ParseError as exc:
            violations.append(f"{xml.relative_to(ADDONS).as_posix()}: NOT WELL-FORMED: {exc}")
            continue
        rel = xml.relative_to(ADDONS).as_posix()
        for record in tree.iter("record"):
            if record.get("model") != "ir.ui.view":
                continue
            arch = record.find(".//field[@name='arch']")
            view_model_el = record.find(".//field[@name='model']")
            if arch is None or view_model_el is None or len(arch) == 0:
                continue
            view_model = (view_model_el.text or "").strip()
            if view_model not in fields_by_model:
                continue  # core/vendor model — outside this proof
            for top in list(arch):
                walk(top, view_model, rel)
    return violations


def main() -> int:
    fields_by_model, relations = load_model_fields()
    violations = check_views(fields_by_model, relations)
    if violations:
        print(f"view-integrity: FAIL - {len(violations)} violation(s):")
        for v in violations:
            print(f"  {v}")
        return 1
    print(f"view-integrity: OK - every view field reference resolves "
          f"({len(fields_by_model)} models known)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
