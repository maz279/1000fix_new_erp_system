# M21 Core HR & Lifecycle, capture audit pass 2 (2026-11-19): each page now
# captures the record the spec names there that nothing could capture before.
#
# Before (HEAD 422b005b), evaluated with the engine's own fregCreate/fregPanels:
#   * pages 2 and 4: a probation was confirmed or extended by a bare list
#     button; no probation review existed (FR-HCM-016/029, AUT-HCM-03,
#     KPI-218);
#   * page 3: an employee had one position and one solid-line manager; no
#     dual role, acting charge or dotted line could be recorded (FR-HCM-024,
#     BRU-HCM-10 H, T-06);
#   * page 7: the manager's side of MSS captured nothing (FR-HCM-041), and the
#     employee's change request covered bank, MFS, NID and e-TIN only - not
#     address, contact, emergency contact or family (FR-HCM-040/042);
#   * page 8: the exit clearance had no knowledge handover (FR-HCM-036).
from __future__ import annotations

import ast
import csv
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
HRCORE = HERE.parents[2] / "domain" / "h_people" / "cd_hr_core"
MODELS = HRCORE / "models"
CONTROLLER = HERE.parent / "controllers" / "a09" / "m21.py"

_spec = importlib.util.spec_from_file_location("_m21_pass1", HERE / "test_m21_capture_buttons.py")
_pass1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pass1)
m21 = _pass1.m21  # the engine-evaluated pages (node), a module-scoped fixture

NEW = {
    "fix.hr.probation.review": "M21-form-probation-review",
    "fix.hr.additional.assignment": "M21-form-assignment",
    "fix.hr.exit.handover": "M21-form-exit-handover",
}
# page -> {chip label: model} the page must now offer
EXPECTED = {
    "2": {"Probation Review": "fix.hr.probation.review"},
    "3": {"Additional Assignment": "fix.hr.additional.assignment"},
    "4": {"Probation Review": "fix.hr.probation.review"},
    "7": {"Probation Review": "fix.hr.probation.review", "Transfer": "fix.hr.transfer"},
    "8": {"Exit Handover": "fix.hr.exit.handover"},
}


def _model_fields():
    """{model: {field: {required, default}}} from the cd_hr_core sources."""
    out = {}
    for path in MODELS.glob("*.py"):
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
                        "default": "default" in kw or "related" in kw or "compute" in kw,
                    }
    return out


def _surfaces():
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "SURFACES":
            return ast.literal_eval(node.value)
    raise AssertionError("no SURFACES")


def test_each_page_offers_the_capture_the_spec_names_there(m21):
    pages = {s["no"]: s for s in m21["subs"]}
    for no, chips in EXPECTED.items():
        offered = {f["f"]: f for f in pages[no]["forms"]}
        for label, model in chips.items():
            assert label in offered, "page %s has no %s chip" % (no, label)
            chip = offered[label]
            assert chip["model"] == model and chip["opens"], (no, chip)


def test_each_new_record_is_listed_on_its_page(m21):
    pages = {s["no"]: s for s in m21["subs"]}
    lists = {
        "2": "M21-probation-reviews",
        "3": "M21-assignments",
        "4": "M21-probation-reviews",
        "7": "M21-probation-reviews",
        "8": "M21-exit-handovers",
    }
    for no, screen in lists.items():
        assert screen in pages[no]["screens"], (no, screen)
        assert m21["screens"][screen]["kind"] == "model_list"


def test_every_form_field_exists_on_its_model_and_no_required_field_is_missing(m21):
    fields_by_model = _model_fields()
    for model, screen in NEW.items():
        form = m21["screens"][screen]
        assert form["kind"] == "model_form" and form["model"] == model
        on_form = {f["name"] for f in form["fields"]}
        known = fields_by_model[model]
        assert on_form <= set(known), "%s: unknown %s" % (screen, sorted(on_form - set(known)))
        # a required field with no default must be on the form, or the server
        # must set it (the probation contract follows the employee reviewed)
        server_set = {"contract_id"} if model == "fix.hr.probation.review" else set()
        for name, spec in known.items():
            if spec["required"] and not spec["default"] and name not in server_set:
                assert name in on_form, "%s cannot save: %s is not on it" % (screen, name)


def test_the_master_change_form_carries_the_contact_and_family_fields(m21):
    form = m21["screens"]["M21-form-master-change"]
    names = {f["name"] for f in form["fields"]}
    src = (MODELS / "fix_hr_capture2.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    personal = None
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and getattr(node.targets[0], "id", "") == "_PERSONAL_PROPOSALS"
        ):
            personal = ast.literal_eval(node.value)
    assert personal, "no _PERSONAL_PROPOSALS"
    for prop in [*personal, "proposed_children", "proposed_children_set"]:
        assert prop in names, prop
    writable = _pass1._writable()["fix.hr.master.change"]
    assert set(personal) <= writable


def test_each_new_model_is_served_with_its_list_actions_and_pickers(m21):
    surfaces = _surfaces()
    lists = {
        "fix.hr.probation.review": "M21-probation-reviews",
        "fix.hr.additional.assignment": "M21-assignments",
        "fix.hr.exit.handover": "M21-exit-handovers",
    }
    for model, screen in lists.items():
        assert model in surfaces, model
        acts = {a["m"] for a in m21["screens"][screen]["actions"]}
        assert acts <= surfaces[model]["actions"], (model, acts - surfaces[model]["actions"])
        assert surfaces[model].get("pickers"), "%s offers unfiltered pickers" % model
    assert surfaces["fix.hr.probation.review"]["pickers"]["employee_id"] == [
        ("fix_on_probation", "=", True)
    ]


def test_access_rows_and_rules_are_declared():
    rows = list(
        csv.DictReader((HRCORE / "security" / "ir.model.access.csv").open(encoding="utf-8"))
    )
    by_model = {}
    for row in rows:
        by_model.setdefault(row["model_id:id"], []).append(row["group_id:id"])
    for model in NEW:
        assert by_model.get("model_" + model.replace(".", "_")), model
    # the dual role / acting / dotted line is HR's alone
    assert "base.group_user" not in by_model["model_fix_hr_additional_assignment"]
    manifest = (HRCORE / "__manifest__.py").read_text(encoding="utf-8")
    assert "security/fix_a09_m21_capture2_rules.xml" in manifest
    rules = (HRCORE / "security" / "fix_a09_m21_capture2_rules.xml").read_text(encoding="utf-8")
    for model in NEW:
        assert 'ref="model_%s"' % model.replace(".", "_") in rules, model
