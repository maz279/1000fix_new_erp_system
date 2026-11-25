# M33 Customer & Party Master, capture audit pass 2 (2026-11-19): each page
# now captures the record the spec names there that nothing could capture.
#
# Before (HEAD 742e46bc), evaluated with the engine's own fregCreate/fregPanels:
#   * pages 1 and 5: no contact point (spec 10.1 fix.contact.point,
#     FR-CPM-022, BRU-CPM-01). An OTP log line verified nothing in
#     particular, and nothing could ever satisfy "activation needs a
#     verified contact".
#   * pages 1 and 3: no party relationship (FR-CPM-006: employer, guardian,
#     referrer, group member, authorised representative).
#   * page 3: no corporate contact role and no contact limit (FR-CPM-009/011).
#   * page 9: no way to mark a minor or a party needing assisted consent, and
#     a consent could not say who gave it on their behalf (FR-CPM-052,
#     BRU-CPM-16).
#   * page 11: the credit limit was a typed field on the profile, its M33/M20
#     form and the AR credit table (FR-CPM-047, BRU-CPM-12, SOD-04).
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADDONS = HERE.parents[2]
MODEL_DIRS = [
    ADDONS / "platform" / "cd_party_master" / "models",
    ADDONS / "domain" / "g_finance" / "cd_billing_engine" / "models",
]
TEMPLATE = HERE.parent / "static" / "src" / "p03_workspace.xml"

_spec = importlib.util.spec_from_file_location("_m33_pass1", HERE / "test_m33_capture_buttons.py")
_pass1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pass1)
m33 = _pass1.m33  # the engine-evaluated pages (node), a module-scoped fixture

NEW_FORMS = {
    "M33-form-contact-point": "fix.contact.point",
    "M33-form-relationship": "fix.party.relationship",
    "M33-form-contact-role": "fix.party.contact.role",
    "M33-form-contact-limit": "res.partner",
    "M33-form-consent-handling": "res.partner",
    "M33-form-credit-change": "fix.credit.limit.change",
}
# page -> {chip label: model} the page must now offer
EXPECTED = {
    "1": {"Contact Point": "fix.contact.point", "Party Relationship": "fix.party.relationship"},
    "3": {
        "Corporate Contact Role": "fix.party.contact.role",
        "Corporate Contact Limit": "res.partner",
        "Party Relationship": "fix.party.relationship",
    },
    "5": {"Contact Point": "fix.contact.point"},
    "9": {"Consent Handling": "res.partner"},
    "11": {"Credit Limit Change": "fix.credit.limit.change"},
}
LISTS = {
    "1": ["M33-contact-points", "M33-relationships"],
    "3": ["M33-contact-roles", "M33-relationships"],
    "5": ["M33-contact-points"],
    "11": ["M33-credit-changes"],
}


def _model_fields():
    """{model: {field: {required, default}}} from the model sources."""
    out = {}
    for folder in MODEL_DIRS:
        for path in folder.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                name = None
                for stmt in node.body:
                    if (
                        isinstance(stmt, ast.Assign)
                        and isinstance(stmt.targets[0], ast.Name)
                        and stmt.targets[0].id in ("_name", "_inherit")
                        and isinstance(stmt.value, ast.Constant)
                        and name is None
                    ):
                        name = stmt.value.value
                if not name:
                    continue
                for stmt in node.body:
                    if (
                        isinstance(stmt, ast.Assign)
                        and isinstance(stmt.targets[0], ast.Name)
                        and isinstance(stmt.value, ast.Call)
                        and isinstance(stmt.value.func, ast.Attribute)
                        and isinstance(stmt.value.func.value, ast.Name)
                        and stmt.value.func.value.id == "fields"
                    ):
                        kw = {k.arg: k.value for k in stmt.value.keywords}
                        req = kw.get("required")
                        out.setdefault(name, {})[stmt.targets[0].id] = {
                            "required": isinstance(req, ast.Constant) and req.value is True,
                            "default": any(k in kw for k in ("default", "related", "compute")),
                        }
    return out


def test_each_page_offers_the_capture_the_spec_names_there(m33):
    pages = {s["no"]: s for s in m33["subs"]}
    for no, chips in EXPECTED.items():
        offered = {f["f"]: f for f in pages[no]["forms"]}
        for label, model in chips.items():
            assert label in offered, "page %s has no %s chip" % (no, label)
            chip = offered[label]
            assert chip["model"] == model and chip["opens"], (no, chip)


def test_each_new_record_is_listed_on_its_page_and_opens_its_form(m33):
    pages = {s["no"]: s for s in m33["subs"]}
    for no, screens in LISTS.items():
        for screen in screens:
            assert screen in pages[no]["screens"], (no, screen)
            assert screen in m33["nav"], screen
            cfg = m33["screens"][screen]
            assert cfg["kind"] == "model_list"
            form = m33["by_screen"][screen]
            assert m33["screens"][form]["model"] == cfg["model"], (screen, form)


def test_every_new_form_field_exists_and_no_required_field_is_missing(m33):
    fields_by_model = _model_fields()
    for screen, model in NEW_FORMS.items():
        form = m33["screens"][screen]
        assert form["kind"] == "model_form" and form["model"] == model
        on_form = {f["name"] for f in form["fields"]}
        if model == "res.partner":
            # pick forms: the party exists; only the fields they set are checked
            assert on_form - {"name"} <= set(fields_by_model["res.partner"]), screen
            continue
        known = fields_by_model[model]
        assert on_form <= set(known), "%s: unknown %s" % (screen, sorted(on_form - set(known)))
        for name, spec in known.items():
            if spec["required"] and not spec["default"]:
                assert name in on_form, "%s cannot save: %s is not on it" % (screen, name)


def test_verification_and_decisions_are_never_typed(m33):
    ro = lambda screen, name: next(  # noqa: E731
        f for f in m33["screens"][screen]["fields"] if f["name"] == name
    )["readonly"]
    for name in ("state", "verified_at", "verification_method"):
        assert ro("M33-form-contact-point", name), name
    for name in ("verified", "verified_by", "verified_at", "date_to"):
        assert ro("M33-form-relationship", name), name
    for name in ("state", "status_note", "date_to"):
        assert ro("M33-form-contact-role", name), name
    for name in ("current_limit", "state", "requested_by", "decided_by", "decided_at"):
        assert ro("M33-form-credit-change", name), name
    assert ro("M33-form-credit", "credit_limit")
    writable = _pass1._writable()
    assert "credit_limit" not in writable["fix.credit.profile"]
    assert {"state", "verified_at"}.isdisjoint(writable["fix.contact.point"])
    assert {"verified", "verified_by"}.isdisjoint(writable["fix.party.relationship"])
    assert {"state", "decided_by", "current_limit"}.isdisjoint(writable["fix.credit.limit.change"])
    assert "assisted_by_id" in writable["fix.consent"]


def test_the_ar_credit_table_no_longer_edits_the_limit():
    xml = TEMPLATE.read_text(encoding="utf-8")
    assert "arProfileSave(row, 'limit'" not in xml


def test_consent_handling_is_a_workflow_with_a_reason(m33):
    form = m33["screens"]["M33-form-consent-handling"]
    assert form["save"] == {
        "method": "action_set_consent_handling",
        "kwargs": {"handling": "consent_handling", "reason": "consent_handling_reason"},
    }
    assert form["pick"] is not None
    consent = {f["name"] for f in m33["screens"]["M33-form-consent"]["fields"]}
    assert "assisted_by_id" in consent


def test_every_list_action_and_save_action_is_served(m33):
    served = _pass1._surfaces()
    for screen in (
        "M33-contact-points",
        "M33-relationships",
        "M33-contact-roles",
        "M33-credit-changes",
    ):
        cfg = m33["screens"][screen]
        assert set(cfg["actions"]) <= served[cfg["model"]], screen
    assert "action_set_consent_handling" in served["res.partner"]
