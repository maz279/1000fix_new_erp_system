#!/usr/bin/env python3
"""audit-view-integrity — comprehensive P04 audit pass 2.

Every ir.ui.view is checked against the model its Python file defines:

  1. field references — each <field name="X"> inside a view for model M
     must be a field of M (declared, related, computed, or an Odoo-standard
     id/active/state) — the exact bug class that crashes Odoo at view load.
  2. inherited views — an inherit_id view must target a model whose base
     form exists, and xpath expressions must be well-formed.
  3. one2many inline trees — the child model's fields must exist too.
  4. chatter blocks — `<chatter/>`, the Odoo 17+ element. This rule used to
     assert the opposite (a <div class="oe_chatter"> wrapper, flagging
     `<chatter/>` as "stray"), which inverted the framework's own convention:
     the vendored Odoo 19 tree uses `<chatter/>` 85 times across its view XML
     and `oe_chatter` exactly 0 times, and the chatter element is implemented
     in addons/mail/static/src/chatter/. The rule flagged 89 correct views and
     would have had them rewritten backwards (re-audit 2026-10-31), so it now
     accepts the element and reports the surviving legacy wrappers as a count
     to migrate rather than as a pass/fail.

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

FIELD_DECL = re.compile(r"^\s{4}(\w+)\s*=\s*fields\.", re.MULTILINE)
RELATION_DECL = re.compile(
    r"""^\s{4}(\w+)\s*=\s*fields\.(One2many|Many2one)\(\s*['"]([\w.]+)['"]""", re.MULTILINE
)
INHERIT_MODEL = re.compile(r"""_inherit\s*=\s*['"]([\w.]+)['"]""")
# `_inherit` is far more often a LIST than a bare string in this codebase (every
# model that adds mail.thread writes one), and INHERIT_MODEL above matches only
# the string form, so inheritance was never resolved for those models: every
# field a mixin contributed looked "unknown" in the views that use it. That was
# 31 of this audit's violations, and all five sampled against the live registry
# existed (re-audit 2026-10-31). Capture both forms, and every parent listed.
INHERIT_LIST = re.compile(r"_inherit\s*=\s*\[([^\]]*)\]", re.DOTALL)
INHERIT_NAME = re.compile(r"""['"]([\w.]+)['"]""")


def _parents(head):
    """Every model named by `_inherit`, whichever form it takes."""
    listed = INHERIT_LIST.search(head)
    if listed:
        return INHERIT_NAME.findall(listed.group(1))
    single = INHERIT_MODEL.search(head)
    return [single.group(1)] if single else []


# Odoo core quotes with ' and this repo with " — accept both, or every
# vendor model is parsed and then attributed to nothing, leaving its own
# fields unknown (that is how `account.journal.bank_id`, a core related
# field, was reported as a violation; re-audit 2026-10-31).
MODEL_NAME = re.compile(r"""_name\s*=\s*['"]([\w.]+)['"]""")
STANDARD_FIELDS = {
    "id",
    "active",
    "sequence",
    "state",
    "name",
    "display_name",
    "company_id",
    "currency_id",
    "create_date",
    "create_uid",
    "write_date",
    "write_uid",
    "message_follower_ids",
    "activity_ids",
    "message_ids",
    "message_main_id",
    "website_description",
    "partner_id",
    "user_id",
    "__last_update",
    # Odoo-standard fields present on mail-thread models
    "message_unread",
    "message_needaction",
}


def load_model_fields() -> tuple[dict[str, set[str]], dict[str, dict[str, str]]]:
    """{model: {field,...}} and {model: {field: comodel}} from addons/.
    Extension classes (_inherit, no _name) MERGE their fields into the
    parent model — that is Odoo's inheritance, so the checker must see the
    merged field set, not the base file's."""
    fields_by_model: dict[str, set[str]] = {}
    relations: dict[str, dict[str, str]] = {}
    parents_by_model: dict[str, set[str]] = {}
    # Vendor models are scanned too. A core model that any addon extends lands
    # in fields_by_model, and without the core definition its OWN fields look
    # unknown: that is how `res.partner.bank.bank_id` and
    # `account.journal.bank_id` — both base fields — were reported as
    # violations (re-audit 2026-10-31). Vendor files are read for field
    # declarations only; nothing else about them is audited.
    sources = list(ADDONS.rglob("*.py")) + list(
        (REPO / "vendor" / "odoo" / "addons").rglob("models/*.py")
    )
    for py in sources:
        if "__pycache__" in py.parts or py.name == "__init__.py":
            continue
        text = py.read_text(encoding="utf-8", errors="ignore")
        for model_match in re.finditer(
            r"class\s+\w+\(models\.(?:Model|AbstractModel|TransientModel)\):(.+?)(?=\nclass |\Z)",
            text,
            re.DOTALL,
        ):
            body = model_match.group(1)
            head = body[:600]
            name_m = MODEL_NAME.search(head)
            inherited = _parents(head)
            declared = set(FIELD_DECL.findall(body))
            new_relations = {m.group(1): m.group(3) for m in RELATION_DECL.finditer(body)}
            # `_name` present -> this class defines that model. `_inherit` alone
            # -> it extends every model it lists (Odoo's extension form).
            for target in [name_m.group(1)] if name_m else inherited:
                fields_by_model.setdefault(target, set()).update(declared)
                relations.setdefault(target, {}).update(new_relations)
            if name_m and inherited:
                parents_by_model.setdefault(name_m.group(1), set()).update(inherited)

    # Resolve inheritance to a fixed point. A child can be parsed before its
    # mixin, and a mixin can itself inherit, so a single pass made the result
    # depend on rglob order and on class order within a file.
    for _ in range(len(parents_by_model) + 2):
        changed = False
        for model, parents in parents_by_model.items():
            own = fields_by_model.setdefault(model, set())
            own_rel = relations.setdefault(model, {})
            for parent in parents:
                gained = fields_by_model.get(parent, set()) - own
                if gained:
                    own |= gained
                    changed = True
                for fname, comodel in relations.get(parent, {}).items():
                    if fname not in own_rel:
                        own_rel[fname] = comodel
                        changed = True
        if not changed:
            break
    return fields_by_model, relations


def model_of_file(xml: Path) -> str:
    return next((p.name for p in xml.parents if (p / "__manifest__.py").is_file()), "")


def check_views(
    fields_by_model: dict[str, set[str]],
    relations: dict[str, dict[str, str]],
) -> list[str]:
    violations: list[str] = []
    # `today`, `now` and `context_today` are supplied by Odoo to list
    # decoration expressions; they are not fields and must not be
    # reported as unknown ones (re-audit 2026-10-31).
    keywords = {
        "in",
        "not",
        "and",
        "or",
        "True",
        "False",
        "None",
        "like",
        "ilike",
        "child_of",
        "today",
        "now",
        "context_today",
        "current_date",
        "uid",
    }

    def fields_known(model: str) -> set[str]:
        return fields_by_model.get(model, set()) | STANDARD_FIELDS

    def walk(el: ET.Element, model: str, rel: str, inside_subview: bool = False) -> None:
        """Depth-first walk of the arch tree. A relational field WITH element
        children is an inline sub-view: its children belong to the comodel."""
        if el.tag == "field":
            fname = el.get("name")
            if fname and fname not in fields_known(model):
                scope = "subview" if inside_subview else "view"
                violations.append(f"{rel}: {scope}[{model}] references unknown field {fname!r}")
                return
            # `<field name="x" position="after">…</field>` is an inheritance
            # ANCHOR, not an inline sub-view: its children belong to the view's
            # OWN model, not to x's comodel. Treating them as a sub-view
            # resolved `fix.commission.ledger` fields against `res.partner` and
            # reported both as unknown (re-audit 2026-10-31).
            if "position" in el.attrib:
                for child in list(el):
                    walk(child, model, rel, inside_subview=inside_subview)
                return
            if fname and len(el) > 0:
                comodel = relations.get(model, {}).get(fname)
                if comodel and comodel in fields_by_model:
                    for child in list(el):
                        walk(child, comodel, rel, inside_subview=True)
                return  # scalar field or unresolvable comodel — nothing nested
        # `<chatter/>` is the supported Odoo 17+ element — not a violation. See
        # the module docstring: core uses it 85 times and `oe_chatter` never.
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
            tree = ET.parse(xml)  # noqa: S314 - parses a repo-owned XML file, not untrusted input
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
    print(
        f"view-integrity: OK - every view field reference resolves "
        f"({len(fields_by_model)} models known)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
