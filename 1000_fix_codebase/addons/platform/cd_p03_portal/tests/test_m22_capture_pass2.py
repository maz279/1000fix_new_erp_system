# M22 Learning & Certification, capture audit pass 2 (2026-11-19): each page
# now captures the record the spec names there that nothing could capture.
#
# Before (HEAD a6ca660a), evaluated with the engine's own fregCreate/fregPanels:
#   * page 1: a learning path held ONE minimum level for all its competencies
#     and named its role as free text: no per-competency role requirement
#     (FR-LMS-002), so no gap analysis (FR-LMS-005);
#   * pages 2 and 4: no training need (FR-LMS-031, BRU-LMS-13, lifecycle 8.2)
#     and no training plan (FR-LMS-032) existed anywhere;
#   * page 4: no participant feedback (FR-LMS-036); an enrolment could not be
#     withdrawn or substituted (FR-LMS-021);
#   * page 5 "OJT & Mentoring": no mentoring record (FR-LMS-028);
#   * page 6: no effectiveness evaluation (FR-LMS-035, BRU-LMS-15).
from __future__ import annotations

import ast
import csv
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMP = HERE.parents[2] / "domain" / "h_people" / "cd_competency"
MODELS = COMP / "models"
CONTROLLER = HERE.parent / "controllers" / "a09" / "m22.py"

_spec = importlib.util.spec_from_file_location("_m22_pass1", HERE / "test_m22_capture_buttons.py")
_pass1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pass1)
m22 = _pass1.m22  # the engine-evaluated pages (node), a module-scoped fixture

NEW = {
    "fix.training.need": "M22-form-need",
    "fix.training.plan": "M22-form-plan",
    "fix.training.feedback": "M22-form-feedback",
    "fix.mentoring": "M22-form-mentoring",
    "fix.mentoring.interaction": "M22-form-mentoring-log",
    "fix.training.effectiveness": "M22-form-effectiveness",
}
# page -> {chip label: model} the page must now offer
EXPECTED = {
    "1": {"Learning Path": "fix.learning.path"},
    "2": {"Training Need": "fix.training.need"},
    "4": {
        "Training Need": "fix.training.need",
        "Training Plan": "fix.training.plan",
        "Training Feedback": "fix.training.feedback",
    },
    "5": {"Mentoring": "fix.mentoring", "Mentoring Interaction": "fix.mentoring.interaction"},
    "6": {"Effectiveness Evaluation": "fix.training.effectiveness"},
}
LISTS = {
    "2": ["M22-role-gaps", "M22-needs"],
    "4": ["M22-needs", "M22-plans", "M22-feedback"],
    "5": ["M22-mentoring", "M22-mentoring-log"],
    "6": ["M22-effectiveness"],
}


def _model_fields():
    """{model: {field: {required, default}}} from the cd_competency sources."""
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


def test_each_page_offers_the_capture_the_spec_names_there(m22):
    pages = {s["no"]: s for s in m22["subs"]}
    for no, chips in EXPECTED.items():
        offered = {f["f"]: f for f in pages[no]["forms"]}
        for label, model in chips.items():
            assert label in offered, "page %s has no %s chip" % (no, label)
            chip = offered[label]
            assert chip["model"] == model and chip["opens"], (no, chip)


def test_each_new_record_is_listed_on_its_page_and_in_the_navigation(m22):
    pages = {s["no"]: s for s in m22["subs"]}
    for no, screens in LISTS.items():
        for screen in screens:
            assert screen in pages[no]["screens"], (no, screen)
            assert screen in m22["nav"], screen
    assert m22["screens"]["M22-role-gaps"]["kind"] == "table_report"


def test_every_form_field_exists_on_its_model_and_no_required_field_is_missing(m22):
    fields_by_model = _model_fields()
    for model, screen in NEW.items():
        form = m22["screens"][screen]
        assert form["kind"] == "model_form" and form["model"] == model
        on_form = {f["name"] for f in form["fields"]}
        known = fields_by_model[model]
        assert on_form <= set(known), "%s: unknown %s" % (screen, sorted(on_form - set(known)))
        for name, spec in known.items():
            if spec["required"] and not spec["default"]:
                assert name in on_form, "%s cannot save: %s is not on it" % (screen, name)
                editable = {f["name"] for f in form["fields"] if not f["readonly"]}
                assert name in editable, "%s: required %s is read-only" % (screen, name)


def test_the_learning_path_captures_the_role_requirement_per_competency(m22):
    """FR-LMS-002: competency + minimum level + mandatory + effective date,
    and the positions the role applies to (what the gap analysis measures)."""
    path_form = _pass1._fields(m22, "M22-form-path")
    assert "position_ids" in path_form
    src = (HERE.parent / "static" / "src" / "a09" / "m22.js").read_text(encoding="utf-8")
    block = src[src.index("'M22-form-path'") : src.index("'M22-form-competency'")]
    assert "field: 'requirement_ids'" in block
    for name in ("competency_id", "min_level", "mandatory", "effective_from"):
        assert "name: '%s'" % name in block, name
    known = _model_fields()["fix.role.competency"]
    assert {"competency_id", "min_level", "mandatory", "effective_from"} <= set(known)
    writable = _pass1_writable()
    assert {"position_ids", "requirement_ids"} <= writable["fix.learning.path"]


def _pass1_writable():
    text = (HERE.parent / "controllers" / "a09" / "writable.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "WRITABLE":
            out = {}
            for k, v in zip(node.value.keys, node.value.values, strict=True):
                items = v.args[0].elts if v.args else []
                out[k.value] = {e.value for e in items}
            return out
    raise AssertionError("no WRITABLE")


def test_workflow_fields_are_never_typed(m22):
    """States, deciders and outcomes move by actions only."""
    writable = _pass1_writable()
    for model, banned in {
        "fix.training.need": {"state", "enrollment_id", "closed_on", "raised_by_id"},
        "fix.training.plan": {"state", "approved_by_id", "submitted_by_id"},
        "fix.mentoring": {"state", "outcome", "closed_by_id"},
        "fix.mentoring.interaction": {"recorded_by_id"},
        "fix.training.effectiveness": {"state", "evaluated_by_id", "result", "change"},
        "fix.training.feedback": {"recorded_by_id", "submitted_on", "employee_id"},
        "fix.training.enrollment": {"withdraw_reason", "substitute_of_id", "state"},
    }.items():
        leaked = banned & writable[model]
        assert not leaked, "%s accepts %s from the form" % (model, sorted(leaked))


def test_each_new_list_action_is_served_and_pickers_are_fenced(m22):
    surfaces = _surfaces()
    lists = {
        "fix.training.need": "M22-needs",
        "fix.training.plan": "M22-plans",
        "fix.mentoring": "M22-mentoring",
        "fix.training.effectiveness": "M22-effectiveness",
        "fix.training.enrollment": "M22-schedule",
        "fix.learning.path": "M22-paths",
    }
    for model, screen in lists.items():
        assert model in surfaces, model
        acts = set(m22["screens"][screen].get("actions") or [])
        assert acts, screen
        assert acts <= surfaces[model]["actions"], (model, acts - surfaces[model]["actions"])
    for model in ("fix.training.feedback", "fix.mentoring.interaction", "fix.role.competency"):
        assert model in surfaces, model
    assert surfaces["fix.training.need"]["pickers"]["plan_id"] == [("state", "=", "draft")]
    assert surfaces["fix.mentoring.interaction"]["pickers"]["mentoring_id"] == [
        ("state", "=", "active")
    ]
    assert surfaces["fix.training.effectiveness"]["pickers"]["session_id"] == [
        ("state", "=", "done")
    ]
    assert {"action_withdraw", "action_substitute"} <= set(
        m22["screens"]["M22-schedule"]["actions"]
    )
    assert "action_raise_gap_needs" in m22["screens"]["M22-paths"]["actions"]


def test_the_role_gap_and_effectiveness_reports_are_served():
    text = CONTROLLER.read_text(encoding="utf-8")
    assert '"role_gap_analysis": role_gap_analysis' in text
    assert '"evaluated"' in text and "fix.training.effectiveness" in text


def test_access_rows_and_rules_are_declared():
    rows = list(csv.DictReader((COMP / "security" / "ir.model.access.csv").open(encoding="utf-8")))
    by_model = {}
    for row in rows:
        by_model.setdefault(row["model_id:id"], {})[row["group_id:id"]] = (
            row["perm_read"],
            row["perm_write"],
            row["perm_create"],
            row["perm_unlink"],
        )
    for model in [*NEW, "fix.role.competency"]:
        assert by_model.get("model_" + model.replace(".", "_")), model
    # needs, plans, mentoring and evaluations are the Training Manager's to create
    for model in ("fix_training_need", "fix_training_plan", "fix_mentoring"):
        assert by_model["model_" + model]["base.group_user"] == ("1", "0", "0", "0"), model
    # the plan is decided by the Training Budget Approver
    assert (
        by_model["model_fix_training_plan"]["cd_competency.group_training_budget_approver"][1]
        == "1"
    )
    manifest = (COMP / "__manifest__.py").read_text(encoding="utf-8")
    assert "security/fix_a09_m22_capture2_rules.xml" in manifest
    rules = (COMP / "security" / "fix_a09_m22_capture2_rules.xml").read_text(encoding="utf-8")
    for model in [*NEW, "fix.role.competency"]:
        assert 'ref="model_%s"' % model.replace(".", "_") in rules, model
    # BRU-LMS-12: a need (a competency gap), a mentoring and feedback are S2
    for rid in (
        "rule_fix_training_need_own",
        "rule_fix_mentoring_own",
        "rule_fix_mentoring_interaction_own",
        "rule_fix_training_feedback_own",
    ):
        assert 'id="%s"' % rid in rules, rid
