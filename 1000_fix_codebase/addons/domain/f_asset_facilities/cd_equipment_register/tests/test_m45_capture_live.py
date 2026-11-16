# M45 capture audit (2026-11-16): the records the sub-module pages now capture,
# driven the way the workspace drives them: the form schema is read from
# static/src/a07/m45.js with node, forms are saved through /p03/model/write
# with the echo the browser posts, and buttons go through /p03/model/action,
# as NON-ADMIN users holding the real roles. Rolled back (`odoo_env`).
from __future__ import annotations

import itertools
import json
import shutil
import subprocess
import types
from datetime import timedelta
from pathlib import Path

import odoo.addons.cd_p03_portal as portal
import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import assigned, inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

TAG = "M45CAP"
ROLE_QM = "cd_equipment_register.group_quality_manager"
ROLE_CAL = "cd_equipment_register.group_calibration_technician"
ROLE_KEEPER = "cd_equipment_register.group_equipment_custodian"
TIER_2 = "cd_entity_config.group_dofa_tier_2"
PARAM_ROLE = "cd_equipment_register.calibration_requires_role"
PARAM_DECISION = "cd_equipment_register.usage_decision_required"
REFUSED = (UserError, ValidationError, AccessError)
SRC = Path(portal.__file__).parent / "static" / "src" / "a07" / "m45.js"
_SEQ = itertools.count(1)


@pytest.fixture(scope="module")
def js(tmp_path_factory):
    node = shutil.which("node")
    assert node, "node evaluates the screens: without it these tests prove nothing"
    tmp = tmp_path_factory.mktemp("m45cap")
    (tmp / "m45.mjs").write_text(SRC.read_text(encoding="utf-8"), "utf-8")
    (tmp / "run.mjs").write_text(
        "import * as M from './m45.mjs';\n"
        "console.log(JSON.stringify({screens: M.SCREENS, chips: M.FORM_CHIPS}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our probe file
        [node, str(tmp / "run.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


def _user(env, tag, groups=()):
    n = next(_SEQ)
    ou = env["operating.unit"].search([], limit=1)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %s %d" % (TAG, tag, n),
                "login": "%s.%s.%d@m45.test" % (TAG.lower(), tag, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    user.employee_id = env["hr.employee"].create(
        {"name": "%s %s %d (emp)" % (TAG, tag, n), "user_id": user.id}
    )
    return user


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, n=0)
    x.today = fields.Date.context_today(env["fix.equipment"])
    x.clerk = _user(env, "clerk")
    x.clerk2 = _user(env, "clerk2")
    x.tech = _user(env, "tech", [ROLE_CAL])
    x.qm = _user(env, "qm", [ROLE_QM])
    x.qm2 = _user(env, "qm2", [ROLE_QM])
    x.keeper = _user(env, "keeper", [ROLE_KEEPER])
    x.keeper2 = _user(env, "keeper2", [ROLE_KEEPER])
    x.manager = _user(env, "manager", [TIER_2])
    x.manager2 = _user(env, "manager2", [TIER_2])
    entity = env["fix.entity"].create(
        {"code": TAG, "legal_name": "%s entity" % TAG, "company_id": env.company.id}
    )
    x.branch = env["fix.branch"].create(
        {
            "name": "%s Branch" % TAG,
            "code": "M45CB",
            "entity_id": entity.id,
            "operating_unit_id": env["operating.unit"].search([], limit=1).id,
        }
    )
    ICP = env["ir.config_parameter"].sudo()
    ICP.set_param(PARAM_ROLE, False)
    ICP.set_param(PARAM_DECISION, False)
    Cat = env["fix.equipment.category"].with_user(x.qm)
    x.meters = Cat.create(
        {"code": TAG + "-MI", "name": "Multimeters", "classification": "measuring_instrument"}
    )
    x.tools = Cat.create(
        {"code": TAG + "-GT", "name": "Hand tools", "classification": "general_tool"}
    )
    x.laptops = Cat.create({"code": TAG + "-IT", "name": "Laptops", "classification": "it_asset"})
    x.standards = Cat.create(
        {
            "code": TAG + "-STD",
            "name": "Reference standards",
            "classification": "calibration_standard",
        }
    )
    return x


@pytest.fixture
def ui(c, monkeypatch):
    cls = api.P03GenericApiController
    ctl = cls()

    def call(name, user, **kw):
        monkeypatch.setattr(
            api, "request", types.SimpleNamespace(env=c.env(user=user.id, su=False))
        )
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    return types.SimpleNamespace(
        form=lambda user, **kw: call("model_form", user, **kw),
        write=lambda user, **kw: call("model_write", user, **kw),
        action=lambda user, **kw: call("model_action", user, **kw),
        report=lambda user, **kw: call("model_report", user, **kw),
    )


def cfg_fields(js, screen):
    return [f for section in js["screens"][screen]["sections"] for f in section["fields"]]


def save(ui, user, js, screen, record_id=False, changes=None, new_rows=None):
    """What the browser's formSave posts: every field the form holds."""
    cfg = js["screens"][screen]
    out = ui.form(
        user,
        model=cfg["model"],
        fields=cfg_fields(js, screen),
        record_id=record_id,
        lines=cfg.get("lines") or False,
    )
    assert "error" not in out, out
    held = dict(out["record"] or out["defaults"] or {})
    held.update(changes or {})
    values = {
        f["name"]: held[f["name"]]
        for f in cfg_fields(js, screen)
        if held.get(f["name"]) is not None and held.get(f["name"]) != ""
    }
    lines = None
    if cfg.get("lines"):
        grid = cfg["lines"]
        rows = [{"id": None, "values": dict(r)} for r in (new_rows or [])]
        lines = {"field": grid["field"], "rows": rows, "removed": []}
    return ui.write(user, model=cfg["model"], record_id=record_id, values=values, lines=lines)


def save_action(ui, user, js, screen, record, **values):
    """What formSaveAction posts: the picked record, the kwargs from the form."""
    act = js["screens"][screen]["saveAction"]
    kwargs = {kw: values[field] for kw, field in act["kwargs"].items() if field in values}
    return ui.action(
        user,
        model=js["screens"][screen]["model"],
        ids=record.ids,
        method=act["method"],
        kwargs=kwargs,
    )


def assert_refused(out, *needles):
    assert out.get("error") or out.get("success") is False, out
    text = out.get("error") or ""
    for needle in needles:
        assert needle in text, text


def assert_done(out):
    assert not out.get("error") and out.get("success") is not False, out


def new_id(out):
    assert_done(out)
    return out.get("id") or out.get("record_id") or (out.get("record") or {}).get("id")


def eq(c, category=None, **kw):
    c.n += 1
    vals = {"code": "%s-EQ-%02d" % (TAG, c.n), "name": "%s item %d" % (TAG, c.n)}
    if category:
        vals["category_id"] = category.id
    vals.update(kw)
    return c.env["fix.equipment"].create(vals)


def cal(c, e, user=None, on=None, due=None, result="pass", **kw):
    vals = {
        "equipment_id": e.id,
        "calibrated_on": on or c.today - timedelta(days=10),
        "standard_ref": "STD-%s" % TAG,
        "certificate_ref": "CERT-%s" % TAG,
        "performed_by": "%s Lab" % TAG,
        "next_due": due or c.today + timedelta(days=355),
        "result": result,
    }
    vals.update(kw)
    return c.env["fix.calibration"].with_user(user or c.tech).create(vals)


# ================================================ 1. the class decides the control
def test_01_class_is_kept_by_the_quality_manager(c, ui, js):
    assert_refused(
        save(
            ui,
            c.keeper,
            js,
            "M45-form-category",
            changes={"code": "X1", "name": "X", "classification": "general_tool"},
        )
    )
    rid = new_id(
        save(
            ui,
            c.qm,
            js,
            "M45-form-category",
            changes={
                "code": TAG + "-ESD",
                "name": "ESD straps",
                "classification": "safety_equipment",
            },
        )
    )
    esd = c.env["fix.equipment.category"].browse(rid)
    assert not esd.requires_calibration and not esd.data_bearing
    assert c.meters.requires_calibration and c.laptops.data_bearing


def test_02_a_tool_is_registered_with_identity_and_issued_without_calibration(c, ui, js):
    rid = new_id(
        save(
            ui,
            c.keeper,
            js,
            "M45-form-equipment",
            changes={
                "code": TAG + "-SD1",
                "name": "Torx driver set",
                "category_id": c.tools.id,
                "manufacturer": "Wera",
                "model_name": "Kraftform",
                "serial_no": "SN-001",
                "branch_id": c.branch.id,
                "warranty_until": str(c.today + timedelta(days=300)),
            },
        )
    )
    tool = c.env["fix.equipment"].browse(rid)
    assert tool.asset_tag, "the asset tag is generated"
    assert (tool.measurement_critical, tool.calibration_state) == (False, "not_required")
    assert tool.warranty_active
    # before: "has never been calibrated" refused every item without a certificate
    assert_done(
        save(
            ui,
            c.keeper,
            js,
            "M45-form-issue",
            changes={
                "equipment_id": tool.id,
                "custodian_id": c.clerk.employee_id.id,
                "issued_on": str(c.today),
            },
        )
    )
    assert tool.operational_status == "issued"


def test_03_a_measuring_instrument_keeps_its_calibration_gate(c, ui, js):
    meter = eq(c, c.meters)
    unclassified = eq(c)
    for item in (meter, unclassified):
        assert item.measurement_critical and item.calibration_state == "never"
        assert_refused(
            save(
                ui,
                c.keeper,
                js,
                "M45-form-issue",
                changes={
                    "equipment_id": item.id,
                    "custodian_id": c.clerk.employee_id.id,
                    "issued_on": str(c.today),
                },
            ),
            "never been calibrated",
        )


def test_04_only_the_quality_manager_moves_an_item_out_of_calibration_control(c, ui, js):
    meter = eq(c, c.meters)
    assert_refused(
        save(ui, c.keeper, js, "M45-form-equipment", meter.id, {"category_id": c.tools.id}),
        "Quality Manager",
    )
    assert meter.category_id == c.meters
    assert_done(save(ui, c.qm, js, "M45-form-equipment", meter.id, {"category_id": c.tools.id}))
    assert not meter.measurement_critical


def test_05_a_tool_cannot_produce_a_qc_result(c, ui, js):
    tool = eq(c, c.tools)
    out = save(
        ui,
        c.keeper,
        js,
        "M45-form-usage",
        changes={
            "equipment_id": tool.id,
            "job_ref": "JOB-1",
            "used_on": str(c.today),
            "qc_result": "pass",
        },
    )
    assert_refused(out, "not a measurement-critical instrument")
    assert_done(
        save(
            ui,
            c.keeper,
            js,
            "M45-form-usage",
            changes={
                "equipment_id": tool.id,
                "job_ref": "JOB-1",
                "used_on": str(c.today),
                "qc_result": "na",
            },
        )
    )


# ================================================ 2. reference standards (BRU-EAM-04)
def test_06_no_calibration_against_a_lapsed_standard(c, ui, js):
    std = eq(c, c.standards)
    meter = eq(c, c.meters)
    changes = {
        "equipment_id": meter.id,
        "calibrated_on": str(c.today - timedelta(days=1)),
        "standard_ref": "In-house",
        "standard_equipment_id": std.id,
        "result": "pass",
        "next_due": str(c.today + timedelta(days=300)),
        "performed_by": "Bench",
        "certificate_ref": "C-1",
    }
    assert_refused(save(ui, c.tech, js, "M45-form-calibration", changes=changes), "BRU-EAM-04")
    # a plain tool is not a standard
    assert_refused(
        save(
            ui,
            c.tech,
            js,
            "M45-form-calibration",
            changes=dict(changes, standard_equipment_id=eq(c, c.tools).id),
        ),
        "not registered as a calibration standard",
    )
    cal(c, std, on=c.today - timedelta(days=20))
    rid = new_id(save(ui, c.tech, js, "M45-form-calibration", changes=changes))
    row = c.env["fix.calibration"].browse(rid)
    assert row.standard_equipment_id == std
    assert meter.calibration_state == "current"
    # the traceability is evidence: fixed once recorded
    with pytest.raises(REFUSED):
        row.with_user(c.tech).write({"standard_equipment_id": False})


# ================================================ 3. recall (FR-EAM-029)
def test_07_recall_takes_the_instrument_out_until_it_passes_again(c, ui, js):
    meter = eq(c, c.meters)
    cal(c, meter, on=c.today - timedelta(days=30))
    meter.custodian_id = c.clerk.employee_id
    assert_refused(
        save_action(ui, c.clerk, js, "M45-form-recall", meter, calibration_recall_note="Drift"),
        "Calibration Technician",
    )
    assert_refused(save_action(ui, c.tech, js, "M45-form-recall", meter), "why")
    assert_done(
        save_action(
            ui, c.tech, js, "M45-form-recall", meter, calibration_recall_note="Drift suspected"
        )
    )
    hold = c.env["fix.equipment.oos"].search(
        [("equipment_id", "=", meter.id), ("state", "=", "open")]
    )
    assert hold.hold_type == "recall" and meter.operational_status == "out_of_service"
    assert meter.activity_ids.filtered(lambda a: a.user_id == c.clerk)
    assert_refused(
        save_action(ui, c.tech, js, "M45-form-recall", meter, calibration_recall_note="Again"),
        "already recalled",
    )
    # back to service only on a passing calibration after the recall, by another QM
    assert_refused(
        ui.action(c.qm, model=hold._name, ids=hold.ids, method="action_resolve"),
        "passing calibration",
    )
    cal(c, meter, on=c.today)
    assert_done(ui.action(c.qm, model=hold._name, ids=hold.ids, method="action_resolve"))
    assert meter.operational_status == "available"


def test_08_a_tool_returns_from_a_fault_without_a_calibration(c, ui, js):
    tool = eq(c, c.tools)
    hold = (
        c.env["fix.equipment.oos"]
        .with_user(c.clerk)
        .create({"equipment_id": tool.id, "reason": "Bent"})
    )
    assert_refused(ui.action(c.clerk2, model=hold._name, ids=hold.ids, method="action_resolve"))
    assert_done(ui.action(c.keeper, model=hold._name, ids=hold.ids, method="action_resolve"))
    assert tool.operational_status == "available"


# ================================================ 4. return with its condition
def test_09_return_form_records_the_condition_and_the_damage(c, ui, js):
    tool = eq(c, c.tools)
    issue = (
        c.env["fix.equipment.issue"]
        .with_user(c.keeper)
        .create(
            {"equipment_id": tool.id, "custodian_id": c.clerk.employee_id.id, "issued_on": c.today}
        )
    )
    assert js["chips"]["M45:Return"] == "M45-form-return"
    assert_done(
        save_action(
            ui,
            c.keeper,
            js,
            "M45-form-return",
            issue,
            return_condition="damaged",
            condition_in="Cracked handle",
        )
    )
    assert (issue.state, issue.return_condition, issue.condition_in) == (
        "returned",
        "damaged",
        "Cracked handle",
    )
    hold = c.env["fix.equipment.oos"].search(
        [("equipment_id", "=", tool.id), ("state", "=", "open")]
    )
    assert hold.hold_type == "damaged" and tool.operational_status == "out_of_service"


# ================================================ 5. PM plans (FR-EAM-032)
def test_10_an_elapsed_plan_raises_one_job_and_rolls_on_completion(c, ui, js):
    tool = eq(c, c.tools)
    changes = {
        "equipment_id": tool.id,
        "trigger_type": "elapsed",
        "interval_value": 6,
        "interval_unit": "months",
        "start_on": str(c.today - timedelta(days=200)),
        "task": "Clean and inspect",
    }
    assert_refused(save(ui, c.clerk, js, "M45-form-pm-plan", changes=changes))
    plan = c.env["fix.equipment.pm.plan"].browse(
        new_id(save(ui, c.keeper, js, "M45-form-pm-plan", changes=changes))
    )
    assert plan.next_due and plan.next_due <= c.today
    assert_done(ui.action(c.keeper, model=plan._name, ids=plan.ids, method="action_raise_due_jobs"))
    job = plan.job_ids
    assert len(job) == 1 and job.pm_type == "preventive" and job.description == "Clean and inspect"
    # while it is open nothing more is raised
    assert plan._m45_raise_due_jobs() == c.env["fix.equipment.pm"]
    job.with_user(c.keeper).write({"notes": "Done", "technician_id": c.clerk.employee_id.id})
    job.with_user(c.keeper).action_done()
    plan.invalidate_recordset()
    assert plan.next_due > c.today and not plan._m45_raise_due_jobs()
    with pytest.raises(REFUSED):
        job.with_user(c.keeper).write({"plan_id": False})


def test_11_a_usage_plan_counts_uses_and_a_plan_has_one_scope(c, ui, js):
    tool = eq(c, c.tools)
    with pytest.raises(REFUSED):
        c.env["fix.equipment.pm.plan"].with_user(c.keeper).create(
            {
                "equipment_id": tool.id,
                "category_id": c.tools.id,
                "interval_value": 5,
                "trigger_type": "usage",
                "interval_unit": "uses",
                "task": "x",
            }
        )
    with pytest.raises(REFUSED):
        c.env["fix.equipment.pm.plan"].with_user(c.keeper).create(
            {
                "equipment_id": tool.id,
                "interval_value": 5,
                "trigger_type": "usage",
                "interval_unit": "months",
                "task": "x",
            }
        )
    plan = (
        c.env["fix.equipment.pm.plan"]
        .with_user(c.keeper)
        .create(
            {
                "category_id": c.tools.id,
                "interval_value": 5,
                "trigger_type": "usage",
                "interval_unit": "uses",
                "task": "Replace bits",
                "start_on": c.today - timedelta(days=5),
            }
        )
    )
    assert not plan._m45_raise_due_jobs()
    c.env["fix.equipment.usage"].with_user(c.keeper).create(
        {"equipment_id": tool.id, "job_ref": "J", "used_on": c.today, "uses": 5}
    )
    assert plan._m45_raise_due_jobs().equipment_id == tool


# ================================================ 6. loss and damage (FR-EAM-040/041)
def test_12_a_loss_is_accountable_and_its_reporter_never_approves_the_write_off(c, ui, js):
    meter = eq(c, c.meters, acquisition_cost=12000.0, custodian_id=c.clerk2.employee_id.id)
    rid = new_id(
        save(
            ui,
            c.manager,
            js,
            "M45-form-loss",
            changes={
                "equipment_id": meter.id,
                "kind": "stolen",
                "occurred_on": str(c.today),
                "circumstances": "Taken from the van",
                "police_report_ref": "GD-77",
                "recharge_employee_id": c.clerk2.employee_id.id,
                "recharge_amount": 2000.0,
            },
        )
    )
    loss = c.env["fix.equipment.loss"].browse(rid)
    assert (loss.reported_by_id, loss.custodian_at_loss_id, loss.value_impact) == (
        c.manager,
        c.clerk2.employee_id,
        12000.0,
    )
    assert meter.operational_status == "missing"
    # the stamps cannot be typed
    with pytest.raises(REFUSED):
        loss.with_user(c.manager).write({"value_impact": 1.0})
    # a second open report on the same item is refused
    assert_refused(
        save(
            ui,
            c.clerk,
            js,
            "M45-form-loss",
            changes={"equipment_id": meter.id, "kind": "lost", "circumstances": "x"},
        ),
        "already has an open",
    )
    assert_done(
        ui.action(c.keeper, model=loss._name, ids=loss.ids, method="action_request_writeoff")
    )
    assert loss.state == "writeoff_requested" and meter.approval_state == "pending"
    route = assigned(meter)
    assert c.manager not in route and c.manager2 in route, route.mapped("name")
    with pytest.raises(UserError, match="BRU-EAM-12"):
        meter.with_user(c.manager).action_approve_writeoff()
    inbox_task(meter, c.manager2).with_user(c.manager2).action_approve()
    assert meter.operational_status == "retired" and loss.state == "written_off"
    assert loss.decided_by_id == c.manager2


def test_13_a_found_item_is_recovered_with_where_it_was(c, ui, js):
    tool = eq(c, c.tools)
    loss = (
        c.env["fix.equipment.loss"]
        .with_user(c.clerk)
        .create({"equipment_id": tool.id, "kind": "lost", "circumstances": "Not on the bench"})
    )
    assert tool.operational_status == "missing"
    assert_refused(
        ui.action(
            c.clerk2,
            model=loss._name,
            ids=loss.ids,
            method="action_recover",
            kwargs={"note": "Drawer"},
        )
    )
    assert_refused(
        ui.action(c.keeper, model=loss._name, ids=loss.ids, method="action_recover"), "where"
    )
    assert_done(
        ui.action(
            c.keeper,
            model=loss._name,
            ids=loss.ids,
            method="action_recover",
            kwargs={"note": "Drawer 3"},
        )
    )
    assert (loss.state, loss.decision_note, tool.operational_status) == (
        "recovered",
        "Drawer 3",
        "available",
    )


def test_14_damage_goes_out_of_service_and_to_repair(c, ui, js):
    tool = eq(c, c.tools)
    loss = (
        c.env["fix.equipment.loss"]
        .with_user(c.clerk)
        .create(
            {"equipment_id": tool.id, "kind": "damaged", "circumstances": "Dropped, casing cracked"}
        )
    )
    assert tool.operational_status == "out_of_service"
    assert_done(ui.action(c.keeper, model=loss._name, ids=loss.ids, method="action_send_to_repair"))
    job = loss.repair_job_id
    assert job.pm_type == "corrective" and "casing cracked" in job.symptom
    assert loss.state == "repair"


# ================================================ 7. blind count (FR-EAM-038)
def test_15_a_blind_count_records_what_nobody_found(c, ui, js):
    found = eq(c, c.tools, branch_id=c.branch.id, acquisition_cost=500.0)
    lost = eq(c, c.tools, branch_id=c.branch.id, acquisition_cost=700.0)
    out_on_issue = eq(c, c.tools, branch_id=c.branch.id)
    c.env["fix.equipment.issue"].with_user(c.keeper).create(
        {
            "equipment_id": out_on_issue.id,
            "custodian_id": c.clerk.employee_id.id,
            "issued_on": c.today,
        }
    )
    others = c.env["fix.equipment"].search(
        [("branch_id", "=", c.branch.id), ("id", "not in", (found | lost | out_on_issue).ids)]
    )
    changes = {
        "branch_id": c.branch.id,
        "scope": "all",
        "scheduled_for": str(c.today),
        "counter_id": c.clerk2.employee_id.id,
    }
    assert_refused(save(ui, c.clerk, js, "M45-form-audit", changes=changes))
    rid = new_id(
        save(
            ui,
            c.keeper,
            js,
            "M45-form-audit",
            changes=changes,
            new_rows=[{"equipment_id": found.id, "found_location": "Shelf B"}]
            + [
                {"equipment_id": o.id}
                for o in others
                if o.operational_status in ("available", "out_of_service", "missing")
            ],
        )
    )
    audit = c.env["fix.equipment.audit"].browse(rid)
    assert_done(ui.action(c.keeper, model=audit._name, ids=audit.ids, method="action_start"))
    # the counter signs for the count
    assert_refused(
        ui.action(c.keeper, model=audit._name, ids=audit.ids, method="action_complete"), "counter"
    )
    assert_done(ui.action(c.clerk2, model=audit._name, ids=audit.ids, method="action_complete"))
    assert audit.state == "done" and audit.missing_count == 1 and audit.variance_value == 700.0
    assert lost.operational_status == "missing" and found.operational_status == "available"
    assert out_on_issue.operational_status == "issued", "custody accounts for an issued item"
    with pytest.raises(REFUSED):
        audit.line_ids[:1].with_user(c.clerk2).write({"found_location": "x"})


def test_16_a_custodian_does_not_count_their_own_store(c, ui, js):
    eq(c, c.tools, branch_id=c.branch.id, custodian_id=c.clerk2.employee_id.id)
    audit = (
        c.env["fix.equipment.audit"]
        .with_user(c.keeper)
        .create({"branch_id": c.branch.id, "counter_id": c.clerk2.employee_id.id})
    )
    assert_refused(
        ui.action(c.clerk2, model=audit._name, ids=audit.ids, method="action_complete"),
        "Segregation of duties",
    )


# ================================================ 8. retirement and disposal
def test_17_a_data_bearing_item_leaves_only_with_its_erasure_certificate(c, ui, js):
    laptop = eq(c, c.laptops, acquisition_cost=20000.0)
    assert laptop.data_bearing and not laptop.measurement_critical
    rid = new_id(
        save(
            ui,
            c.keeper,
            js,
            "M45-form-retirement",
            changes={
                "equipment_id": laptop.id,
                "basis": "age",
                "justification": "Five years old",
                "disposal_route": "ewaste",
                "disposal_ref": "EW-1",
            },
        )
    )
    ret = c.env["fix.equipment.retirement"].browse(rid)
    assert_refused(
        ui.action(c.qm, model=ret._name, ids=ret.ids, method="action_dispose"), "not retired"
    )
    assert_done(ui.action(c.keeper, model=ret._name, ids=ret.ids, method="action_request"))
    assert laptop.approval_state == "pending"
    approver = assigned(laptop)[:1]
    assert approver and approver != c.keeper
    inbox_task(laptop, approver).with_user(approver).action_approve()
    assert ret.state == "approved" and laptop.operational_status == "retired"
    assert_refused(
        ui.action(c.qm, model=ret._name, ids=ret.ids, method="action_dispose"), "BRU-EAM-16"
    )
    assert_done(
        save(ui, c.qm, js, "M45-form-retirement", ret.id, {"erasure_certificate_ref": "M06-ER-9"})
    )
    assert_done(ui.action(c.qm, model=ret._name, ids=ret.ids, method="action_dispose"))
    assert ret.state == "disposed" and ret.disposed_by_id == c.qm


# ================================================ 9. branch profile and reports
def test_18_branch_profile_shows_the_capability_gap(c, ui, js):
    rid = new_id(
        save(
            ui,
            c.qm,
            js,
            "M45-form-branch-profile",
            changes={
                "branch_id": c.branch.id,
                "category_id": c.meters.id,
                "minimum_quantity": 2,
                "critical": True,
            },
        )
    )
    line = c.env["fix.branch.equipment.profile"].browse(rid)
    held = line.held_count
    assert line.shortfall == max(0, 2 - held)
    meter = eq(c, c.meters, branch_id=c.branch.id)
    line.invalidate_recordset()
    assert line.held_count == held + 1
    if not line.fit_count:
        assert line.capability_exception
    cal(c, meter)
    line.invalidate_recordset()
    assert line.fit_count >= 1 and not line.capability_exception
    out = ui.report(c.qm, module="M45", report="register_completeness", params={})
    assert any(r["category"] == "Multimeters" for r in out["rows"]), out
    assert_refused(save(ui, c.keeper, js, "M45-form-branch-profile", rid, {"minimum_quantity": 1}))
