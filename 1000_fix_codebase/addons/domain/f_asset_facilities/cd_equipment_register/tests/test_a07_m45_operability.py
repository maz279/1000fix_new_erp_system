# A07 operability: can a person do the M45 job on the P03 workspace?
#
# Each test drives what the workspace drives: the form schema is read by evaluating
# static/src/a07/m45.js with node, a form is opened through /p03/model/form, saved
# through /p03/model/write with the same echo the browser posts, and buttons go
# through /p03/model/action, all as NON-ADMIN users holding the real role. The
# database is rolled back (`odoo_env`).
from __future__ import annotations

import base64
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

TAG = "A7M45O"
ROLE_QM = "cd_equipment_register.group_quality_manager"
ROLE_CAL = "cd_equipment_register.group_calibration_technician"
ROLE_KEEPER = "cd_equipment_register.group_equipment_custodian"
TIER_2 = "cd_entity_config.group_dofa_tier_2"
PARAM_ROLE = "cd_equipment_register.calibration_requires_role"
PARAM_DECISION = "cd_equipment_register.usage_decision_required"
REFUSED = (UserError, ValidationError, AccessError)
PDF = base64.b64encode(b"%PDF-1.4 calibration certificate").decode()
SRC = Path(portal.__file__).parent / "static" / "src" / "a07" / "m45.js"
_SEQ = itertools.count(1)


@pytest.fixture(scope="module")
def js(tmp_path_factory):
    node = shutil.which("node")
    assert node, "node evaluates the screens: without it these tests prove nothing"
    tmp = tmp_path_factory.mktemp("m45js")
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
                "login": "%s.%s.%d@a07.test" % (TAG.lower(), tag, n),
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
    x.manager = _user(env, "branch-manager", [TIER_2])
    ICP = env["ir.config_parameter"].sudo()
    ICP.set_param(PARAM_ROLE, False)
    ICP.set_param(PARAM_DECISION, False)
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
        records=lambda user, **kw: call("model_records", user, **kw),
        form=lambda user, **kw: call("model_form", user, **kw),
        write=lambda user, **kw: call("model_write", user, **kw),
        action=lambda user, **kw: call("model_action", user, **kw),
        report=lambda user, **kw: call("model_report", user, **kw),
    )


def cfg_fields(js, screen):
    return [f for section in js["screens"][screen]["sections"] for f in section["fields"]]


def buttons(js, screen):
    return {a["m"]: a for a in js["screens"][screen].get("actions", [])}


def open_form(ui, user, js, screen, record_id=False):
    cfg = js["screens"][screen]
    out = ui.form(
        user,
        model=cfg["model"],
        fields=cfg_fields(js, screen),
        record_id=record_id,
        lines=cfg.get("lines") or False,
    )
    assert "error" not in out, out
    return out


def save(ui, user, js, screen, record_id=False, changes=None, new_rows=None, removed=None):
    """What the browser's formSave posts: every field the form holds, read-only
    ones included, and every grid row it shows."""
    cfg = js["screens"][screen]
    changes = changes or {}
    out = open_form(ui, user, js, screen, record_id)
    held = dict(out["record"] or out["defaults"] or {})
    held.update(changes)
    values = {}
    for field in cfg_fields(js, screen):
        value = held.get(field["name"])
        if value is not None and value != "":
            values[field["name"]] = value
        elif record_id and field["name"] in changes:
            values[field["name"]] = False
    lines = None
    grid = cfg.get("lines")
    if grid and not grid.get("readonlyGrid"):
        rows = []
        for row in (out["lines"]["rows"] or []) + list(new_rows or []):
            vals = {
                f["name"]: row[f["name"]]
                for f in grid["fields"]
                if row.get(f["name"]) is not None and row.get(f["name"]) != ""
            }
            if vals:
                rows.append({"id": row.get("id"), "values": vals})
        lines = {"field": grid["field"], "rows": rows, "removed": removed or []}
    return ui.write(user, model=cfg["model"], record_id=record_id, values=values, lines=lines)


def field_meta(out, name):
    return next(f for f in out["fields"] if f["name"] == name)


def eq(c, **kw):
    c.n += 1
    vals = {"code": "%s-EQ-%02d" % (TAG, c.n), "name": "%s meter %d" % (TAG, c.n)}
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


def profiled(c, provider="any", verification=False):
    e = eq(c)
    profile = (
        c.env["fix.calibration.profile"]
        .with_user(c.qm)
        .create(
            {
                "equipment_id": e.id,
                "interval_months": 12,
                "provider_requirement": provider,
                "verification_only": verification,
                "point_ids": []
                if verification
                else [
                    (
                        0,
                        0,
                        {
                            "name": "DCV 10V",
                            "unit": "V",
                            "tolerance_low": 9.99,
                            "tolerance_high": 10.01,
                        },
                    )
                ],
            }
        )
    )
    return e, profile


def new_calibration_values(e, **kw):
    vals = {
        "equipment_id": e.id,
        "calibrated_on": str(fields.Date.today() - timedelta(days=1)),
        "standard_ref": "STD-%s" % TAG,
    }
    vals.update(kw)
    return vals


def assert_refused(out, *needles):
    assert out.get("error") or out.get("success") is False, out
    text = out.get("error") or ""
    for needle in needles:
        assert needle in text, text


def assert_done(out):
    assert not out.get("error") and out.get("success") is not False, out


# ========================================================== 2. reject and readings
def test_02_reject_asks_for_the_note_and_takes_it(c, ui, js):
    button = buttons(js, "M45-certificates")["action_reject_calibration"]
    assert button["kwarg"] == "decision_note" and button["ask"]
    e = eq(c)
    row = cal(c, e)
    assert_refused(
        ui.action(c.qm, model=row._name, ids=row.ids, method="action_reject_calibration"),
        "State why",
    )
    assert row.decision_state == "pending"
    out = ui.action(
        c.qm,
        model=row._name,
        ids=row.ids,
        method="action_reject_calibration",
        kwargs={"decision_note": "Certificate not traceable"},
    )
    assert_done(out)
    assert (row.decision_state, row.decision_note) == ("rejected", "Certificate not traceable")
    assert e.calibration_state == "rejected" and e.operational_status == "out_of_service"


def test_02_saving_a_calibration_with_readings_does_not_resend_them(c, ui, js):
    e, profile = profiled(c)
    point = profile.point_ids
    out = save(
        ui,
        c.tech,
        js,
        "M45-form-calibration",
        changes=new_calibration_values(
            e,
            result="pass",
            certificate_ref="CERT-1",
            performed_by="Lab",
        ),
        new_rows=[{"point_id": point.id, "as_found": 10.0}],
    )
    assert_done(out)
    row = c.env["fix.calibration"].browse(out["id"])
    assert len(row.reading_ids) == 1
    # the Quality Manager's save re-sends the header and the shown row: only the note changes
    out = save(
        ui,
        c.qm,
        js,
        "M45-form-calibration",
        record_id=row.id,
        changes={"decision_note": "Traceable to BSTI"},
    )
    assert_done(out)
    row.invalidate_recordset()
    assert row.decision_note == "Traceable to BSTI" and len(row.reading_ids) == 1
    # a reading stays insert-only: adding or removing one on a saved record is refused
    assert_refused(
        save(
            ui,
            c.qm,
            js,
            "M45-form-calibration",
            record_id=row.id,
            new_rows=[{"point_id": point.id, "as_found": 9.0}],
        )
    )
    assert_refused(
        save(ui, c.qm, js, "M45-form-calibration", record_id=row.id, removed=row.reading_ids.ids)
    )
    assert len(row.reading_ids) == 1


# ========================================================== 3. found on the verification
def test_03_leaving_found_alone_stores_found(c, ui, js):
    e = eq(c)
    out = open_form(ui, c.clerk, js, "M45-form-verification")
    assert out["defaults"]["found"] is True
    res = save(
        ui,
        c.clerk,
        js,
        "M45-form-verification",
        changes={"equipment_id": e.id, "campaign_ref": "Q4 count"},
    )
    assert_done(res)
    row = c.env["fix.equipment.verification"].browse(res["id"])
    assert (row.found, row.state) == (True, "verified")
    assert e.operational_status == "available"


@pytest.mark.parametrize("unticked", [False, 0, None])
def test_03_unticking_found_stores_missing(c, ui, js, unticked):
    e = eq(c)
    # whatever a caller sends for "not found" is a loss, never a verified row
    res = ui.write(
        c.clerk,
        model="fix.equipment.verification",
        record_id=False,
        values={"equipment_id": e.id, "campaign_ref": "Q4 count", "found": unticked},
    )
    assert_done(res)
    row = c.env["fix.equipment.verification"].browse(res["id"])
    assert (bool(row.found), row.state) == (False, "missing")
    assert e.operational_status == "missing" and e.missing_verification_id == row


def test_03_a_role_holder_cannot_clear_a_loss_by_leaving_the_form_alone(c, ui, js):
    e = eq(c)
    res = save(
        ui,
        c.clerk,
        js,
        "M45-form-verification",
        changes={"equipment_id": e.id, "campaign_ref": "Q4 count", "found": False},
    )
    lost = c.env["fix.equipment.verification"].browse(res["id"])
    # the next count: the box is ticked by default and no one says where it was found
    assert_refused(
        save(
            ui,
            c.keeper,
            js,
            "M45-form-verification",
            changes={"equipment_id": e.id, "campaign_ref": "Q1 count"},
        ),
        "where it was found",
    )
    assert e.operational_status == "missing" and e.missing_verification_id == lost
    # no role: never
    assert_refused(
        save(
            ui,
            c.clerk,
            js,
            "M45-form-verification",
            changes={"equipment_id": e.id, "campaign_ref": "Q1", "location": "Rack 3"},
        ),
    )
    assert e.operational_status == "missing"
    # the store keeper who says where it was found recovers it
    assert_done(
        save(
            ui,
            c.keeper,
            js,
            "M45-form-verification",
            changes={"equipment_id": e.id, "campaign_ref": "Q1", "location": "Rack 3"},
        )
    )
    assert e.operational_status == "available" and not e.missing_verification_id
    # the recorded loss stays final
    assert lost.state == "missing"
    assert_refused(
        ui.write(
            c.keeper,
            model=lost._name,
            record_id=lost.id,
            values={"found": True},
        ),
    )


# ========================================================== 4. kit out
def _kit(c, *members, **kw):
    c.n += 1
    vals = {
        "code": "%s-KIT-%02d" % (TAG, c.n),
        "name": "%s kit %d" % (TAG, c.n),
        "issue_to_id": c.clerk.employee_id.id,
        "line_ids": [(0, 0, {"equipment_id": m.id}) for m in members],
    }
    vals.update(kw)
    return c.env["fix.equipment.kit"].create(vals)


def _kit_action(ui, user, kit, method):
    return ui.action(user, model=kit._name, ids=kit.ids, method=method)


def test_04_condition_can_be_saved_while_the_kit_is_out_and_is_not_reused(c, ui, js):
    meter = eq(c)
    cal(c, meter)
    kit = _kit(c, meter)
    assert_done(_kit_action(ui, c.keeper, kit, "action_issue_kit"))
    assert kit.state == "issued"
    # the form re-sends the member grid: an unchanged echo does not reach the guard
    assert_done(
        save(
            ui, c.keeper, js, "M45-form-kit", record_id=kit.id, changes={"return_condition": "good"}
        )
    )
    assert kit.return_condition == "good"
    # a real change of members while it is out is still refused
    other = eq(c)
    assert_refused(
        save(
            ui,
            c.keeper,
            js,
            "M45-form-kit",
            record_id=kit.id,
            new_rows=[{"equipment_id": other.id}],
        ),
        "out on issue",
    )
    assert_done(_kit_action(ui, c.keeper, kit, "action_return_kit"))
    assert meter.operational_status == "available"
    assert not kit.return_condition, "a stale condition would be reused on the next return"
    # the next return, with nothing stated, is not read as serviceable
    assert_done(_kit_action(ui, c.keeper, kit, "action_issue_kit"))
    assert_done(_kit_action(ui, c.keeper, kit, "action_return_kit"))
    assert meter.operational_status == "out_of_service"
    assert kit.issue_ids.sorted("id")[-1].return_condition is False


def test_kit_members_returned_one_by_one_release_the_kit(c, ui, js):
    first, second = eq(c), eq(c)
    cal(c, first)
    cal(c, second)
    kit = _kit(c, first, second, return_condition="good")
    assert_done(_kit_action(ui, c.keeper, kit, "action_issue_kit"))
    issues = kit.issue_ids.sorted("id")
    assert len(issues) == 2
    assert_done(
        ui.action(
            c.keeper,
            model=issues._name,
            ids=issues[0].ids,
            method="action_return",
            kwargs={"condition": "good"},
        )
    )
    assert kit.accountable_employee_id and kit.state == "partial"
    assert_done(
        ui.action(
            c.keeper,
            model=issues._name,
            ids=issues[1].ids,
            method="action_return",
            kwargs={"condition": "good"},
        )
    )
    assert not kit.accountable_employee_id and kit.state == "available"
    assert kit.completeness_checked_at and not kit.return_condition
    # and it goes out again
    assert_done(_kit_action(ui, c.keeper, kit, "action_issue_kit"))
    assert kit.state == "issued" and kit.accountable_employee_id == c.clerk.employee_id


# ========================================================== 5. technician's request
def test_05_calibration_technician_requests_an_interval_change_from_the_form(c, ui, js):
    e, profile = profiled(c)
    res = save(
        ui,
        c.tech,
        js,
        "M45-form-profile",
        record_id=profile.id,
        changes={
            "proposed_interval_months": 18,
            "interval_change_reason": "3 clean as-found results",
        },
    )
    assert_done(res)
    assert profile.proposed_interval_months == 18
    assert_done(
        ui.action(c.tech, model=profile._name, ids=profile.ids, method="action_request_approval")
    )
    assert profile.approval_state == "pending"
    # the profile's own facts stay the Quality Manager's
    e2, profile2 = profiled(c)
    assert_refused(
        save(
            ui,
            c.tech,
            js,
            "M45-form-profile",
            record_id=profile2.id,
            changes={"required_traceability": "typed by a technician"},
        ),
        "Quality Manager",
    )
    assert not profile2.required_traceability
    assert_done(
        save(
            ui,
            c.qm,
            js,
            "M45-form-profile",
            record_id=profile2.id,
            changes={"required_traceability": "ISO/IEC 17025"},
        )
    )
    assert profile2.required_traceability == "ISO/IEC 17025"


# ========================================================== 6. the impact form lists the uses
def test_06_impact_form_lists_every_affected_use_read_only(c, ui, js):
    e = eq(c)
    cal(c, e, on=c.today - timedelta(days=30))
    uses = c.env["fix.equipment.usage"].create(
        [
            {"equipment_id": e.id, "job_ref": "JOB-1", "used_on": c.today - timedelta(days=20)},
            {"equipment_id": e.id, "job_ref": "JOB-2", "used_on": c.today - timedelta(days=10)},
        ]
    )
    row = cal(c, e, on=c.today, result="fail", due=c.today + timedelta(days=1))
    impact = row.impact_id
    assert impact.affected_uses == 2
    grid = js["screens"]["M45-form-impact"]["lines"]
    assert grid["readonlyGrid"] is True
    out = open_form(ui, c.qm, js, "M45-form-impact", record_id=impact.id)
    assert {r["job_ref"] for r in out["lines"]["rows"]} == set(uses.mapped("job_ref"))
    assert all(f["readonly"] for f in out["lines"]["fields"])
    # the grid edits nothing
    assert_refused(
        ui.write(
            c.qm,
            model=impact._name,
            record_id=impact.id,
            values={},
            lines={"field": grid["field"], "rows": [], "removed": uses.ids},
        ),
        "does not edit",
    )
    assert impact.affected_uses == 2
    # a disposition still saves through the form with the grid on it
    assert_done(
        save(
            ui,
            c.qm,
            js,
            "M45-form-impact",
            record_id=impact.id,
            changes={"disposition": "valid", "disposition_note": "Re-measured a sample"},
        )
    )
    assert impact.disposition == "valid"


# ========================================================== 7. link to the fixed asset
def test_07_fixed_asset_shows_read_only_on_the_equipment_form(c, ui, js):
    e = eq(c)
    out = open_form(ui, c.keeper, js, "M45-form-equipment", record_id=e.id)
    assert field_meta(out, "fixed_asset_id")["readonly"] is True
    assert "fixed_asset_id" not in api.SURFACES["fix.equipment"]["writable"]


# ========================================================== 8. compliance report
def test_08_compliance_report_survives_a_rejected_row_and_reads_pending_true(c, ui):
    rejected, pending, passed, failed, never = eq(c), eq(c), eq(c), eq(c), eq(c)
    row = cal(c, rejected)
    row.with_user(c.qm).action_reject_calibration(decision_note="Not traceable")
    cal(c, pending)
    cal(c, passed)
    passed.calibration_ids.sudo()._guarded().write({"decision_state": "accepted"})
    cal(c, failed, result="fail", due=c.today + timedelta(days=1))
    c.env["ir.config_parameter"].sudo().set_param(PARAM_DECISION, "True")
    c.env.invalidate_all()
    out = ui.report(c.clerk, module="M45", report="calibration_compliance")
    assert "error" not in out, out
    status = {r["code"]: r["status"] for r in out["rows"]}
    assert status[rejected.code] == "rejected at usage decision"
    assert status[pending.code] == "awaiting usage decision"
    assert status[passed.code] == "current"
    assert status[failed.code] == "failed"
    assert status[never.code] == "never calibrated"
    # with the switch off a recorded pass does not wait for anyone
    c.env["ir.config_parameter"].sudo().set_param(PARAM_DECISION, False)
    c.env.invalidate_all()
    out = ui.report(c.clerk, module="M45", report="calibration_compliance")
    assert {r["code"]: r["status"] for r in out["rows"]}[pending.code] == "current"


# ========================================================== 9. display name
def test_09_a_calibration_reads_as_instrument_date_and_result(c):
    e = eq(c, name="Fluke 87V")
    row = cal(c, e, on=c.today - timedelta(days=3))
    label = row.display_name
    assert "Fluke 87V" in label and str(c.today - timedelta(days=3)) in label and "Pass" in label
    assert "fix.calibration" not in label
    failed = cal(c, e, on=c.today, result="fail", due=c.today + timedelta(days=1))
    assert (
        "fix.calibration,"
        not in e.env["fix.equipment.oos"]
        .search([("equipment_id", "=", e.id), ("state", "=", "open")])
        .reason
    )
    assert "fix.calibration," not in failed.impact_id.calibration_id.display_name
    ncr = c.env["fix.ncr"].browse(failed.impact_id.ncr_res_id)
    assert "fix.calibration," not in ncr.description and "Fluke 87V" in ncr.description


# ========================================================== 10. reading point picker
def test_10_the_reading_point_names_its_instrument_and_shows_the_band(c, ui, js):
    e, profile = profiled(c)
    other, other_profile = profiled(c)
    out = open_form(ui, c.tech, js, "M45-form-calibration")
    names = {f["name"] for f in out["lines"]["fields"]}
    assert {"tolerance_low", "tolerance_high"} <= names
    assert field_meta(out["lines"], "tolerance_low")["readonly"] is True
    labels = {o["id"]: o["label"] for o in field_meta(out["lines"], "point_id")["choices"]}
    label = labels[profile.point_ids.id]
    assert e.name in label and "DCV 10V" in label and "9.99" in label and "10.01" in label
    assert other.name in labels[other_profile.point_ids.id]
    # a wrong pick still refuses, and says whose point it must be
    assert_refused(
        save(
            ui,
            c.tech,
            js,
            "M45-form-calibration",
            changes=new_calibration_values(e, result="pass", certificate_ref="C", performed_by="L"),
            new_rows=[{"point_id": other_profile.point_ids.id, "as_found": 10.0}],
        ),
        e.name,
    )
    # a saved reading shows the band it was judged against
    res = save(
        ui,
        c.tech,
        js,
        "M45-form-calibration",
        changes=new_calibration_values(e, result="pass", certificate_ref="C", performed_by="L"),
        new_rows=[{"point_id": profile.point_ids.id, "as_found": 10.0}],
    )
    assert_done(res)
    out = open_form(ui, c.tech, js, "M45-form-calibration", record_id=res["id"])
    assert out["lines"]["rows"][0]["tolerance_high"] == 10.01


def test_10_points_of_a_verification_only_profile_are_not_offered(c, ui, js):
    e, profile = profiled(c)
    point = profile.point_ids
    assert point.id in {
        o["id"]
        for o in field_meta(open_form(ui, c.tech, js, "M45-form-calibration")["lines"], "point_id")[
            "choices"
        ]
    }
    profile.sudo().verification_only = True
    assert point.id not in {
        o["id"]
        for o in field_meta(open_form(ui, c.tech, js, "M45-form-calibration")["lines"], "point_id")[
            "choices"
        ]
    }


# ========================================================== 11. lists nobody can add to
def test_11_impact_list_has_no_new_button_and_create_is_refused(c, ui, js):
    assert js["screens"]["M45-impacts"]["create"] is False
    assert js["screens"]["M45-alerts"]["create"] is False
    e = eq(c)
    row = cal(c, e)
    assert_refused(
        ui.write(
            c.qm,
            model="fix.calibration.impact",
            record_id=False,
            values={"calibration_id": row.id, "equipment_id": e.id},
        ),
    )
    # the lists a role can add to keep the button
    for screen in ("M45-register", "M45-certificates", "M45-issue", "M45-profiles", "M45-kits"):
        assert js["screens"][screen].get("create") is not False, screen


# ========================================================== 12. the chip
def test_12_write_off_chip_opens_the_register_not_a_blank_form(js):
    target = js["chips"]["M45:Write-Off"]
    assert target == "M45-register"
    assert js["screens"][target]["kind"] == "model_list"
    assert "action_request_approval" in buttons(js, target)


# ========================================================== 13. who decides a write-off
def test_13_the_text_names_who_really_decides_a_write_off(c, ui, js):
    note = next(
        s for s in js["screens"]["M45-form-equipment"]["sections"] if s["title"] == "Write-Off"
    )["note"]
    assert "Branch / Operations Manager" in note and "CFO" in note
    assert "Quality Manager" not in note
    e = eq(c, retirement_reason="Beyond repair")
    assert_refused(
        ui.action(c.keeper, model=e._name, ids=e.ids, method="action_request_approval"),
        "Branch / Operations Manager",
    )
    e.acquisition_cost = 10000.0
    assert_done(ui.action(c.keeper, model=e._name, ids=e.ids, method="action_request_approval"))
    route = assigned(e)
    assert c.manager in route, "routed to %s" % route.mapped("name")
    assert c.qm not in route, "a Quality Manager holds no tier 2 authority"


# ========================================================== 14. interval routing
def test_14_interval_request_is_not_routed_to_who_calibrated_it(c, ui):
    e, profile = profiled(c)
    # the first Quality Manager recorded a calibration of this instrument
    cal(
        c,
        e,
        user=c.qm,
        reading_ids=[(0, 0, {"point_id": profile.point_ids.id, "as_found": 10.0})],
    )
    profile.with_user(c.tech).write(
        {"proposed_interval_months": 24, "interval_change_reason": "Stable"}
    )
    assert_done(
        ui.action(c.tech, model=profile._name, ids=profile.ids, method="action_request_approval")
    )
    route = assigned(profile)
    assert c.qm not in route and c.qm2 in route, route.mapped("name")
    # and the approver it reached can decide it
    inbox_task(profile, c.qm2).with_user(c.qm2).action_approve()
    assert profile.interval_months == 24
    # the justification answered that request: the next one needs its own
    assert not profile.interval_change_reason
    profile.with_user(c.tech).write({"proposed_interval_months": 36})
    assert_refused(
        ui.action(c.tech, model=profile._name, ids=profile.ids, method="action_request_approval"),
        "Justify",
    )
    assert profile.interval_months == 24


# ========================================================== 15. retirement
def test_15_approved_write_off_closes_the_holds_and_the_kpi_ignores_retired(c, ui):
    from odoo.addons.cd_p03_portal.controllers.a07 import m45 as surface

    e = eq(c, acquisition_cost=10000.0, retirement_reason="Beyond repair")
    hold = (
        c.env["fix.equipment.oos"]
        .with_user(c.clerk)
        .create({"equipment_id": e.id, "reason": "Burnt out"})
    )
    assert e.operational_status == "out_of_service"
    before = surface.kpis(c.env(user=c.clerk.id, su=False))["oos_open"]
    assert_done(ui.action(c.keeper, model=e._name, ids=e.ids, method="action_request_approval"))
    inbox_task(e, c.manager).with_user(c.manager).action_approve()
    assert e.operational_status == "retired"
    assert (hold.state, hold.resolved_by_id) == ("resolved", c.manager)
    assert hold.resolved_on == c.today
    after = surface.kpis(c.env(user=c.clerk.id, su=False))["oos_open"]
    assert after == before - 1
    # an older retired row whose hold was left open is not an open hold either
    old = eq(c)
    c.env["fix.equipment.oos"].create({"equipment_id": old.id, "reason": "Old fault"})
    old.sudo()._guarded().write({"operational_status": "retired"})
    assert surface.kpis(c.env(user=c.clerk.id, su=False))["oos_open"] == after


# ========================================================== 16. kit status chip
def test_16_kit_status_chip_filters(c, ui, js):
    meter, idle = eq(c), eq(c)
    cal(c, meter)
    out_kit = _kit(c, meter)
    home_kit = _kit(c, idle)
    assert_done(_kit_action(ui, c.keeper, out_kit, "action_issue_kit"))
    cols = ["code", "state"]
    issued = ui.records(
        c.clerk, model="fix.equipment.kit", cols=cols, state_filter="issued", state_field="state"
    )
    assert "error" not in issued, issued
    assert out_kit.id in {r["id"] for r in issued["rows"]}
    assert home_kit.id not in {r["id"] for r in issued["rows"]}
    available = ui.records(
        c.clerk, model="fix.equipment.kit", cols=cols, state_filter="available", state_field="state"
    )
    assert home_kit.id in {r["id"] for r in available["rows"]}
    assert_done(_kit_action(ui, c.keeper, out_kit, "action_return_kit"))
    available = ui.records(
        c.clerk, model="fix.equipment.kit", cols=cols, state_filter="available", state_field="state"
    )
    assert out_kit.id in {r["id"] for r in available["rows"]}


# ========================================================== 17. what the switches do
def test_17_the_calibration_note_says_what_the_switches_do_and_it_is_true(c, ui, js):
    note = next(
        s for s in js["screens"]["M45-form-calibration"]["sections"] if s["title"] == "Calibration"
    )["note"]
    assert "second-person acceptance" in note and "is off" in note and "is on" in note
    # off: the recorded pass certifies on its own
    e = eq(c)
    row = cal(c, e)
    assert e.calibration_state == "current"
    assert_done(ui.action(c.clerk, model=e._name, ids=e.ids, method="action_assert_usable"))
    # on: not usable until another Quality Manager accepts it
    c.env["ir.config_parameter"].sudo().set_param(PARAM_DECISION, "True")
    c.env.invalidate_all()
    assert e.calibration_state == "pending"
    assert_refused(
        ui.action(c.clerk, model=e._name, ids=e.ids, method="action_assert_usable"), "awaits"
    )
    assert_done(ui.action(c.qm, model=row._name, ids=row.ids, method="action_accept_calibration"))
    assert e.calibration_state == "current"
    # the role switch: off anyone records, on only the two roles
    assert cal(c, e, user=c.clerk)
    c.env["ir.config_parameter"].sudo().set_param(PARAM_ROLE, "True")
    with pytest.raises(UserError, match="Calibration Technician"), c.env.cr.savepoint():
        cal(c, e, user=c.clerk)
    assert cal(c, e, user=c.tech)


# ========================================================== 18. accredited provider
def test_18_accredited_provider_is_enforced_when_the_profile_requires_it(c, ui, js):
    e, profile = profiled(c, provider="accredited")
    assert profile.provider_requirement == "accredited"
    reading = {"point_id": profile.point_ids.id, "as_found": 10.0}
    pass_vals = {"result": "pass", "certificate_ref": "C-1", "performed_by": "Lab"}
    assert_refused(
        save(
            ui,
            c.tech,
            js,
            "M45-form-calibration",
            changes=new_calibration_values(e, **pass_vals),
            new_rows=[reading],
        ),
        "accredited",
    )
    assert not e.calibration_ids
    res = save(
        ui,
        c.tech,
        js,
        "M45-form-calibration",
        changes=new_calibration_values(e, provider_accredited=True, **pass_vals),
        new_rows=[reading],
    )
    assert_done(res)
    row = c.env["fix.calibration"].browse(res["id"])
    assert row.provider_accredited is True
    # the ticked box is evidence: it does not change afterwards
    with pytest.raises(UserError), c.env.cr.savepoint():
        row.with_user(c.qm).write({"provider_accredited": False})
    # a failed calibration certifies nothing, so it needs no accreditation to be recorded
    bad = save(
        ui,
        c.tech,
        js,
        "M45-form-calibration",
        changes=new_calibration_values(e),
        new_rows=[{"point_id": profile.point_ids.id, "as_found": 50.0}],
    )
    assert_done(bad)
    assert c.env["fix.calibration"].browse(bad["id"]).result == "fail"
    # an "any provider" profile asks nothing
    e2, profile2 = profiled(c, provider="any")
    assert_done(
        save(
            ui,
            c.tech,
            js,
            "M45-form-calibration",
            changes=new_calibration_values(e2, **pass_vals),
            new_rows=[{"point_id": profile2.point_ids.id, "as_found": 10.0}],
        )
    )


# ========================================================== 19. certificate file
def test_19_certificate_file_is_kept_on_the_calibration(c, ui, js):
    e = eq(c)
    offered = {f["name"]: f for f in cfg_fields(js, "M45-form-calibration")}
    assert offered["certificate_file"]["type"] == "file"
    assert "certificate_filename" in offered
    res = save(
        ui,
        c.tech,
        js,
        "M45-form-calibration",
        changes=new_calibration_values(
            e,
            result="pass",
            next_due=str(c.today + timedelta(days=100)),
            certificate_ref="C-9",
            performed_by="Lab",
            certificate_file=PDF,
            certificate_filename="cert-c9.pdf",
        ),
    )
    assert_done(res)
    row = c.env["fix.calibration"].browse(res["id"])
    raw = row.certificate_file
    assert (raw.decode() if isinstance(raw, bytes) else raw) == PDF
    assert row.certificate_filename == "cert-c9.pdf"
    # reopened, it is read-only with its download, the echo saves, and it cannot be swapped
    out = open_form(ui, c.qm, js, "M45-form-calibration", record_id=row.id)
    assert field_meta(out, "certificate_file")["readonly"] is True
    assert out["record"]["certificate_file"]
    assert_done(
        save(
            ui,
            c.qm,
            js,
            "M45-form-calibration",
            record_id=row.id,
            changes={"decision_note": "Seen"},
        )
    )
    with pytest.raises(UserError), c.env.cr.savepoint():
        row.with_user(c.qm).write({"certificate_file": base64.b64encode(b"other").decode()})


# ========================================================== logic: certificate bypass
def test_blank_result_with_good_readings_still_needs_certificate_and_performer(c, ui, js):
    e, profile = profiled(c, provider="any")
    reading = (0, 0, {"point_id": profile.point_ids.id, "as_found": 10.0})
    Calibration = c.env["fix.calibration"].with_user(c.tech)
    base = {"equipment_id": e.id, "standard_ref": "STD", "reading_ids": [reading]}
    with pytest.raises(UserError, match="certificate"), c.env.cr.savepoint():
        Calibration.create(dict(base))
    assert not e.calibration_ids
    # the same blank result from the screen
    assert_refused(
        save(
            ui,
            c.tech,
            js,
            "M45-form-calibration",
            changes=new_calibration_values(e),
            new_rows=[{"point_id": profile.point_ids.id, "as_found": 10.0}],
        ),
        "certificate",
    )
    # with the evidence, the derived pass stands
    row = Calibration.create(dict(base, certificate_ref="C-1", performed_by="Lab"))
    assert row.result == "pass"
    # a derived fail never needed a certificate
    bad = Calibration.create(
        dict(base, reading_ids=[(0, 0, {"point_id": profile.point_ids.id, "as_found": 50.0})])
    )
    assert bad.result == "fail"


# ========================================================== logic: transfer cancel
def test_transfer_cancel_needs_the_role_except_for_your_own_draft(c, ui):
    entity = c.env["fix.entity"].search([("company_id", "=", c.env.company.id)], limit=1) or c.env[
        "fix.entity"
    ].create({"code": "A7M45O", "legal_name": "M45 entity", "company_id": c.env.company.id})
    branch = c.env["fix.branch"].create(
        {
            "name": "%s branch" % TAG,
            "code": "A7M45OB",
            "entity_id": entity.id,
            "operating_unit_id": c.env["operating.unit"].search([], limit=1).id,
        }
    )
    e = eq(c)
    draft = (
        c.env["fix.equipment.transfer"]
        .with_user(c.clerk)
        .create({"equipment_id": e.id, "to_branch_id": branch.id})
    )
    assert_refused(
        ui.action(c.clerk2, model=draft._name, ids=draft.ids, method="action_cancel"), "role"
    )
    assert draft.state == "draft"
    assert_done(ui.action(c.clerk, model=draft._name, ids=draft.ids, method="action_cancel"))
    assert draft.state == "cancelled"
    sent = (
        c.env["fix.equipment.transfer"]
        .with_user(c.clerk)
        .create({"equipment_id": e.id, "to_branch_id": branch.id})
    )
    assert_done(ui.action(c.keeper, model=sent._name, ids=sent.ids, method="action_dispatch"))
    # once dispatched the item is on the road: its raiser cannot withdraw it
    assert_refused(
        ui.action(c.clerk, model=sent._name, ids=sent.ids, method="action_cancel"), "role"
    )
    assert sent.state == "dispatched"
    assert_done(ui.action(c.keeper2, model=sent._name, ids=sent.ids, method="action_cancel"))
    assert sent.state == "cancelled"


# ========================================================== logic: usage gate at used_on
def _use(c, ui, e, used_on, **kw):
    values = {"equipment_id": e.id, "job_ref": "JOB-LATE", "used_on": str(used_on)}
    values.update(kw)
    return ui.write(c.clerk, model="fix.equipment.usage", record_id=False, values=values)


def test_an_honest_late_entry_after_a_fail_is_accepted_and_is_suspect(c, ui):
    e = eq(c)
    good = cal(c, e, on=c.today - timedelta(days=30))
    bad = cal(c, e, on=c.today - timedelta(days=5), result="fail", due=c.today + timedelta(days=1))
    assert e.operational_status == "out_of_service"
    # used while the instrument was certified, written down after the fail
    used_on = c.today - timedelta(days=10)
    res = _use(c, ui, e, used_on)
    assert_done(res)
    use = c.env["fix.equipment.usage"].browse(res["id"])
    assert use.calibration_id == good and use.fitness_state_at_use == "current"
    # it falls in the suspect window: the open assessment now lists it
    assert use in bad.impact_id.usage_ids and bad.impact_id.affected_uses == 1
    # after the fail it is refused, whatever the entry claims
    assert_refused(_use(c, ui, e, c.today - timedelta(days=2)), "failed")
    assert_refused(_use(c, ui, e, c.today), "failed")
    # before any calibration there was no certificate
    assert_refused(_use(c, ui, e, c.today - timedelta(days=60)), "no calibration")
    # never in the future
    assert_refused(_use(c, ui, e, c.today + timedelta(days=1)), "future")


def test_late_entry_tests_the_holds_and_the_certificate_at_that_date(c, ui):
    e = eq(c)
    cal(c, e, on=c.today - timedelta(days=100), due=c.today - timedelta(days=50))
    # past its next-due on that day
    assert_refused(_use(c, ui, e, c.today - timedelta(days=40)), "overdue")
    assert_done(_use(c, ui, e, c.today - timedelta(days=60)))
    held = eq(c)
    cal(c, held, on=c.today - timedelta(days=30))
    hold = c.env["fix.equipment.oos"].create({"equipment_id": held.id, "reason": "Fault"})
    hold.sudo()._guarded().write({"started_on": c.today - timedelta(days=5)})
    assert_refused(_use(c, ui, held, c.today - timedelta(days=2)), "out of service")
    assert_done(_use(c, ui, held, c.today - timedelta(days=10)))
    # today's use is still gated by today's status
    assert_refused(_use(c, ui, held, c.today), "Out of Service")


def test_use_date_and_qc_result_lock_after_create(c, ui, js):
    e = eq(c)
    cal(c, e)
    res = _use(c, ui, e, c.today, qc_result="pass")
    assert_done(res)
    use = c.env["fix.equipment.usage"].browse(res["id"])
    out = open_form(ui, c.clerk, js, "M45-form-usage", record_id=use.id)
    assert field_meta(out, "used_on")["readonly"] and field_meta(out, "qc_result")["readonly"]
    for values in ({"used_on": str(c.today - timedelta(days=1))}, {"qc_result": "fail"}):
        assert_refused(
            ui.write(c.clerk, model=use._name, record_id=use.id, values=values), "read-only"
        )
        with pytest.raises(UserError), c.env.cr.savepoint():
            use.with_user(c.clerk).write(values)
    assert (use.used_on, use.qc_result) == (c.today, "pass")
    # the form still saves a note with the locked fields echoed
    assert_done(
        save(ui, c.clerk, js, "M45-form-usage", record_id=use.id, changes={"notes": "Bench 3"})
    )
    assert use.notes == "Bench 3"


# ========================================================== logic: M49 capitalisation
def test_cost_entered_for_a_write_off_raises_no_capitalisation(c, ui, js):
    Req = c.env["fix.asset.finance.request"].sudo()
    requests = lambda e: Req.search(  # noqa: E731
        [
            ("source_model", "=", "fix.equipment"),
            ("source_res_id", "=", e.id),
            ("kind", "=", "capitalise"),
        ]
    )
    # cost and reason typed on the Write-Off section in one save
    e = eq(c)
    assert_done(
        save(
            ui,
            c.keeper,
            js,
            "M45-form-equipment",
            record_id=e.id,
            changes={"acquisition_cost": 90000.0, "retirement_reason": "Dropped and destroyed"},
        )
    )
    assert e.acquisition_cost == 90000.0 and not requests(e)
    # a cost on a working item still goes to finance
    working = eq(c)
    assert_done(
        save(
            ui,
            c.keeper,
            js,
            "M45-form-equipment",
            record_id=working.id,
            changes={"acquisition_cost": 90000.0},
        )
    )
    assert len(requests(working)) == 1
    # an item already retired never does
    retired = eq(c)
    retired.sudo()._guarded().write({"operational_status": "retired"})
    Req._m49_capitalise_equipment(retired)
    retired.sudo().acquisition_cost = 5000000.0
    assert not requests(retired)
