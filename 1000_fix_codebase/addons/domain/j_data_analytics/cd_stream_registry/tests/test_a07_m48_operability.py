# cd_stream_registry - A07 operability: can a person do the M48 job on the workspace?
#
# Each test walks the real path as a NON-ADMIN user with the real IoT role, through the
# endpoints the workspace calls (/p03/model/form, /write, /action). The screens are read
# by evaluating static/src/a07/m48.js with node, so a column or button the file declares
# is what is checked, not its source text.
from __future__ import annotations

import base64
import hashlib
import json
import shutil
import subprocess
import threading
import types
import uuid
from datetime import timedelta
from pathlib import Path

import odoo.addons.cd_p03_portal as portal
import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers.a07 import m48 as m48_surface
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

TAG = uuid.uuid4().hex[:6].upper()
REFUSED = (UserError, ValidationError, AccessError)
OPERATOR = "cd_stream_registry.group_iot_operator"
ADMIN = "cd_stream_registry.group_iot_admin"
MANAGER = "cd_stream_registry.group_iot_manager"
CONSENT = "cd_stream_registry.group_iot_consent_officer"
DIRECTOR = "cd_facility.group_operations_director"
TIER2 = "cd_entity_config.group_dofa_tier_2"
MODEL = "m26.predictive.maintenance"
MODEL_CHECK = "cd_stream_registry.prediction_model_check"
SRC = Path(portal.__file__).parent / "static" / "src"
PDF = base64.b64encode(b"%PDF-1.4 signed disclosure").decode()


@pytest.fixture(scope="module")
def js(tmp_path_factory):
    node = shutil.which("node")
    assert node, "node evaluates the registry: without it these tests prove nothing"
    tmp = tmp_path_factory.mktemp("m48js")
    (tmp / "m48.mjs").write_text((SRC / "a07" / "m48.js").read_text(encoding="utf-8"), "utf-8")
    (tmp / "m63.mjs").write_text((SRC / "a11" / "m63.js").read_text(encoding="utf-8"), "utf-8")
    (tmp / "run.mjs").write_text(
        "import * as M from './m48.mjs';\n"
        "import * as I from './m63.mjs';\n"
        "console.log(JSON.stringify({module: M.MODULE, screens: M.SCREENS, chips: M.FORM_CHIPS,"
        " inbox: I.SCREENS['M63-inbox']}));\n",
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


def offered(js, screen):
    out = {}
    for section in js["screens"][screen]["sections"]:
        for field in section["fields"]:
            out[field["name"]] = field
    return out


def buttons(js, screen):
    return {a["m"]: a for a in js["screens"][screen].get("actions", [])}


def nav_ids(js):
    return {s["id"] for g in js["module"]["groups"] for s in g["screens"]}


def refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED:
        return True
    return False


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    env["ir.config_parameter"].sudo().set_param(MODEL_CHECK, "create")
    ou = env["operating.unit"].search([], limit=1)
    n = {"i": 0}

    def user(*xmlids):
        n["i"] += 1
        login = "a07m48op_%d_%s" % (n["i"], TAG)
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "group_ids": [(6, 0, groups)],
                    "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                    "default_operating_unit_id": ou.id,
                }
            )
        )

    x = types.SimpleNamespace(env=env, user=user, ou=ou)
    x.clerk = user()
    x.operator, x.operator2 = user(OPERATOR), user(OPERATOR)
    x.admin = user(ADMIN)
    x.cto = user(MANAGER)
    x.officer, x.officer2 = user(CONSENT), user(CONSENT)
    x.equipment = env["fix.equipment"].create(
        {"code": f"M48OP-EQ-{TAG}", "name": f"M48OP Pump {TAG}", "category": "Electrical"}
    )
    x.device = env["fix.iot.device"].create(
        {"name": f"M48OP Dev {TAG}", "device_id": f"M48OP-{TAG}", "equipment_id": x.equipment.id}
    )
    x.stream = env["fix.iot.stream"].create(
        {"device_id": x.device.id, "metric": "vibration", "unit": "mm/s"}
    )
    x.stream.action_activate()
    x.tech = env["hr.employee"].create({"name": f"M48OP Tech {TAG}"})
    return x


@pytest.fixture
def ui(c, monkeypatch):
    cls = api.P03GenericApiController
    ctl = cls()

    def call(name, user, **kw):
        env = c.env(user=user.id)
        monkeypatch.setattr(api, "request", types.SimpleNamespace(env=env))
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    return types.SimpleNamespace(
        form=lambda user, **kw: call("model_form", user, **kw),
        write=lambda user, **kw: call("model_write", user, **kw),
        action=lambda user, **kw: call("model_action", user, **kw),
        records=lambda user, **kw: call("model_records", user, **kw),
    )


def pred(c, **kw):
    vals = {
        "name": f"M48OP-PDM-{uuid.uuid4().hex[:5]}",
        "equipment_id": c.equipment.id,
        "prediction": "failure_predicted",
        "confidence": 0.8,
        "estimated_days_to_failure": 10,
        "model_name": MODEL,
    }
    vals.update(kw)
    return c.env["fix.predictive.maintenance"].create(vals)


def act(c, prediction=None, user=None, **kw):
    vals = {
        "prediction_id": (prediction or pred(c)).id,
        "action_type": "inspect",
        "technician_id": c.tech.id,
    }
    vals.update(kw)
    return c.env["fix.iot.action"].with_user(user or c.operator).create(vals)


def empty_group(env, xmlid):
    """Nobody holds this role, whichever group implies it."""
    group = env.ref(xmlid).sudo()
    for g in group | group.all_implied_by_ids:
        g.write({"user_ids": [(5, 0, 0)]})
    env.invalidate_all()
    assert not group.all_user_ids


def with_key(env, adapter):
    """Give `adapter` a key the way the Administrator's rotation stores it."""
    key = "k-%s-%s" % (uuid.uuid4().hex, uuid.uuid4().hex)
    env.cr.execute(
        "UPDATE fix_iot_adapter SET api_key_hash=%s, state='enabled' WHERE id=%s",
        [hashlib.sha256(key.encode()).hexdigest(), adapter.id],
    )
    adapter.invalidate_recordset()
    return key


# ======================================================== 1 + 2: recording a prediction
def test_1_a_new_prediction_keeps_its_score_through_the_form(c, ui):
    out = ui.form(
        c.operator,
        model="fix.predictive.maintenance",
        fields=[{"name": "prediction"}, {"name": "confidence"}, {"name": "model_name"}],
    )
    assert not any(f["readonly"] for f in out["fields"])
    res = ui.write(
        c.operator,
        model="fix.predictive.maintenance",
        values={
            "name": "scored",
            "equipment_id": c.equipment.id,
            "prediction": "failure_predicted",
            "confidence": 0.8,
            "estimated_days_to_failure": 4,
            "model_name": MODEL,
        },
    )
    assert "error" not in res, res
    rec = c.env["fix.predictive.maintenance"].browse(res["id"])
    assert (rec.prediction, rec.confidence, rec.model_name) == ("failure_predicted", 0.8, MODEL)
    assert rec.estimated_days_to_failure == 4
    assert rec.last_evaluated, "a recorded score says when it was evaluated"


def test_1_an_existing_prediction_stays_locked_on_the_form(c, ui):
    rec = pred(c)
    out = ui.form(
        c.operator,
        model="fix.predictive.maintenance",
        record_id=rec.id,
        fields=[{"name": "prediction"}, {"name": "equipment_id"}],
    )
    assert all(f["readonly"] for f in out["fields"])
    res = ui.write(
        c.operator,
        model="fix.predictive.maintenance",
        record_id=rec.id,
        values={"prediction": "healthy"},
    )
    assert "error" in res
    assert rec.prediction == "failure_predicted"


def test_1_only_the_iot_operator_records_a_prediction(c, ui):
    vals = {
        "name": "x",
        "equipment_id": c.equipment.id,
        "prediction": "failure_predicted",
        "model_name": MODEL,
    }
    res = ui.write(c.clerk, model="fix.predictive.maintenance", values=dict(vals))
    assert "IoT Operator" in res.get("error", "")


@pytest.mark.parametrize("name", ["m26-pdm-v2", "made-up", False])
def test_2_an_unpublished_model_is_refused_naming_the_published_ones(c, ui, name):
    res = ui.write(
        c.operator,
        model="fix.predictive.maintenance",
        values={
            "name": "x",
            "equipment_id": c.equipment.id,
            "prediction": "failure_predicted",
            "confidence": 0.8,
            "model_name": name,
        },
    )
    assert MODEL in res.get("error", ""), res


# ===================================================== 3: who approves an action
def test_3_with_no_director_the_request_goes_to_dofa_tier_2(c, ui):
    empty_group(c.env, DIRECTOR)
    t2 = c.user(TIER2)
    action = act(c)
    res = ui.action(
        c.operator,
        model="fix.iot.action",
        ids=[action.id],
        method="action_request_approval",
        kwargs={"justification": "bearing failing"},
    )
    assert res["success"], res
    assert t2 in assigned(action)
    approve_via_inbox(action, t2, requester=c.operator)
    assert action.state == "approved" and action.approved_by == t2


def test_3_with_a_director_the_request_goes_to_the_director(c):
    director = c.user(DIRECTOR)
    t2 = c.user(TIER2)
    action = act(c)
    action.with_user(c.operator).action_request_approval(justification="failing")
    assert director in assigned(action) and t2 not in assigned(action)
    approve_via_inbox(action, director, requester=c.operator)
    assert action.state == "approved"


def test_3_a_tier_2_task_stays_decidable_when_a_director_is_appointed_meanwhile(c):
    empty_group(c.env, DIRECTOR)
    t2 = c.user(TIER2)
    action = act(c)
    action.with_user(c.operator).action_request_approval(justification="failing")
    c.user(DIRECTOR)
    task = inbox_task(action, t2)
    task.with_user(t2).action_approve()
    assert action.state == "approved"


def test_3_the_button_says_who_decides(js):
    label = buttons(js, "M48-routing")["action_request_approval"]["l"]
    assert "Operations Director" in label and "Tier 2" in label


# ===================================================== 6: relaxing the consent policy
def test_6_the_consent_officer_relaxes_through_the_action(c, ui, js):
    assert {"policy", "reason"} == {
        a["kwarg"] for a in buttons(js, "M48-streams")["action_set_consent_policy"]["asks"]
    }
    c.stream.write({"consent_policy": "required"})
    call = {
        "model": "fix.iot.stream",
        "ids": [c.stream.id],
        "method": "action_set_consent_policy",
    }
    res = ui.action(c.admin, **call, kwargs={"policy": "inherit", "reason": "site sensor"})
    assert not res["success"] and "Consent Officer" in res["error"]
    res = ui.action(c.officer, **call, kwargs={"policy": "inherit", "reason": " "})
    assert not res["success"] and "reason" in res["error"].lower()
    res = ui.action(c.officer, **call, kwargs={"policy": "nonsense", "reason": "x"})
    assert not res["success"] and "inherit" in res["error"]
    res = ui.action(c.officer, **call, kwargs={"policy": "inherit", "reason": "site sensor"})
    assert res["success"], res
    assert c.stream.consent_policy == "inherit"
    bodies = c.stream.message_ids.mapped("body")
    assert any("site sensor" in str(b) for b in bodies), "the change is in the chatter"
    # the Administrator still cannot relax by writing the field
    c.stream.write({"consent_policy": "required"})
    res = ui.write(
        c.admin,
        model="fix.iot.stream",
        record_id=c.stream.id,
        values={"consent_policy": "inherit"},
    )
    assert "Consent Officer" in res.get("error", "")


# ===================================================== 7: cancelling an action
def _approved(c):
    action = act(c)
    action._guarded().write({"state": "approved"})
    return action


@pytest.mark.parametrize("kind", ["proposed", "pending", "approved"])
def test_7_a_proposed_or_approved_action_is_cancelled(c, ui, js, kind):
    assert buttons(js, "M48-routing")["action_cancel"]["kwarg"] == "reason"
    action = _approved(c) if kind == "approved" else act(c)
    if kind == "pending":
        c.user(DIRECTOR)
        action.with_user(c.operator).action_request_approval(justification="failing")
    call = {"model": "fix.iot.action", "ids": [action.id], "method": "action_cancel"}
    res = ui.action(c.clerk, **call, kwargs={"reason": "x"})
    assert not res["success"] and "IoT Operator" in res["error"]
    res = ui.action(c.operator, **call, kwargs={"reason": ""})
    assert not res["success"]
    res = ui.action(c.operator, **call, kwargs={"reason": "asset replaced under warranty"})
    assert res["success"], res
    assert action.state == "cancelled"
    assert action.cancel_reason == "asset replaced under warranty"
    assert action.cancelled_by == c.operator
    assert action.approval_state == "none"
    assert not action.approval_request_id.task_ids.filtered(lambda t: t.state == "pending")


@pytest.mark.parametrize("state", ["dispatched", "done", "cancelled"])
def test_7_a_later_action_is_not_cancelled(c, state):
    action = act(c)
    action._guarded().write({"state": state})
    assert refused(c.env, lambda: action.with_user(c.operator).action_cancel(reason="x"))


# ===================================================== 8: consent treatment and telemetry
def _readings(c, stream, count, start_hours=48):
    now = fields.Datetime.now()
    made = c.env["fix.iot.telemetry"]
    for i in range(count):
        made |= (
            c.env["fix.iot.telemetry"]
            .sudo()
            ._guarded()
            .create(
                {
                    "company_id": stream.device_id.company_id.id,
                    "device_id": stream.device_id.id,
                    "metric": stream.metric,
                    "value": 1.0 + i,
                    "timestamp": now - timedelta(hours=start_hours, minutes=i),
                }
            )
        )
    return made


def _consent(c, treatment, device=None, **kw):
    return c.env["fix.iot.consent"].create(
        {
            "subject_type": "device",
            "device_id": (device or c.device).id,
            "revocation_treatment": treatment,
            "evidence_ref": "signed form",
            "granted_by": "the owner",
            "signal_groups_permitted": "vibration",
            **kw,
        }
    )


def test_8_telemetry_is_on_a_read_only_screen(c, ui, js):
    screen = js["screens"]["M48-telemetry"]
    assert screen["model"] == "fix.iot.telemetry" and screen["create"] is False
    assert "M48-telemetry" in nav_ids(js)
    assert m48_surface.SURFACES["fix.iot.telemetry"]["actions"] == set()
    row = _readings(c, c.stream, 1)
    out = ui.records(
        c.operator,
        model="fix.iot.telemetry",
        cols=screen["cols"],
        domain=[["id", "=", row.id]],
    )
    assert {r["id"] for r in out["rows"]} == {row.id}
    assert set(screen["cols"]) <= set(out["rows"][0]), "a column the server does not know is lost"
    res = ui.write(c.admin, model="fix.iot.telemetry", record_id=row.id, values={"value": 99})
    assert "error" in res
    assert row.value == 1.0


def test_8_anonymisation_really_anonymises_and_counts(c, ui, js):
    assert "action_record_treatment" in buttons(js, "M48-consent")
    other = _readings(c, c.stream, 3)
    gps = c.env["fix.iot.stream"].create({"device_id": c.device.id, "metric": "gps_lat"})
    gps.action_activate()
    located = _readings(c, gps, 2)
    consent = _consent(c, "anonymise", signal_groups_permitted=False)
    consent.with_user(c.clerk).action_revoke(evidence_ref="letter")
    assert consent.treatment_state == "manual" and consent.readings_treated == 0
    call = {"model": "fix.iot.consent", "ids": [consent.id], "method": "action_record_treatment"}
    res = ui.action(c.clerk, **call, kwargs={"note": "as agreed"})
    assert not res["success"]
    res = ui.action(c.officer, **call, kwargs={"note": "as agreed at grant"})
    assert res["success"], res
    assert consent.treatment_state == "applied" and consent.readings_treated == 5
    c.env.invalidate_all()
    assert not located.exists(), "a location series cannot be anonymised: it is deleted"
    for reading in other:
        assert reading.anonymised and not reading.device_id
        assert reading.timestamp.minute == 0 and reading.timestamp.second == 0
    assert not c.env["fix.iot.telemetry"].search_count([("device_id", "=", c.device.id)])
    assert "as agreed at grant" in consent.treatment_note
    res = ui.action(c.officer, **call, kwargs={"note": "again"})
    assert not res["success"], "the task is closed"


def test_8_a_reading_with_no_device_is_only_an_anonymised_one(c):
    with pytest.raises(Exception), c.env.cr.savepoint():  # noqa: B017 - the CHECK
        c.env["fix.iot.telemetry"].sudo()._guarded().create(
            {"metric": "x", "value": 1.0, "company_id": c.env.company.id}
        )


def test_8_revoking_after_suspension_still_treats_the_readings(c):
    rows = _readings(c, c.stream, 4)
    consent = _consent(c, "delete")
    c.stream.action_suspend()
    consent.with_user(c.clerk).action_revoke(evidence_ref="letter")
    assert not rows.exists(), "the agreed treatment applied to the held readings"
    assert (consent.treatment_state, consent.readings_treated) == ("applied", 4)


def test_8_deleting_also_removes_the_aggregates_of_those_readings(c):
    rows = _readings(c, c.stream, 4)
    policy = c.env["fix.iot.downsample"].create({"stream_id": c.stream.id})
    policy._fix_activate()
    c.env["fix.iot.downsample"].cron_retention()
    assert policy.rollup_ids
    consent = _consent(c, "delete")
    consent.with_user(c.clerk).action_revoke(evidence_ref="letter")
    assert not rows.exists()
    c.env.invalidate_all()
    assert not policy.rollup_ids


def test_8_another_valid_consent_keeps_the_readings(c):
    rows = _readings(c, c.stream, 2)
    _consent(c, "retain")
    consent = _consent(c, "delete")
    consent.with_user(c.clerk).action_revoke(evidence_ref="letter")
    assert rows.exists() and consent.readings_treated == 0
    assert c.stream.state == "active"


# ===================================================== 9: switching a policy off
def _policy(c, **kw):
    return c.env["fix.iot.downsample"].create({"stream_id": c.stream.id, **kw})


def test_9_an_active_policy_is_switched_off_through_the_approved_change(c, ui, js):
    assert "action_request_deactivation" in buttons(js, "M48-downsample")
    policy = _policy(c)
    policy._fix_activate()
    call = {
        "model": "fix.iot.downsample",
        "ids": [policy.id],
        "method": "action_request_deactivation",
    }
    res = ui.action(c.admin, **call, kwargs={"reason": ""})
    assert not res["success"]
    res = ui.action(c.admin, **call, kwargs={"reason": "sensor retired"})
    assert res["success"], res
    assert policy.state == "active", "only the approval switches it off"
    change = c.env["fix.iot.retention.change"].search([("downsample_id", "=", policy.id)])
    assert change.change_type == "deactivate" and change.state == "requested"
    res = ui.action(c.admin, **call, kwargs={"reason": "again"})
    assert not res["success"], "a second request while one is open"
    assert refused(c.env, lambda: change.with_user(c.admin).action_apply())
    approve_via_inbox(change, c.cto, requester=c.admin)
    assert change.state == "applied" and policy.state == "draft"
    assert not policy.activated_on


def test_9_a_draft_policy_has_nothing_to_switch_off(c):
    policy = _policy(c)
    assert refused(c.env, lambda: policy.with_user(c.admin).action_request_deactivation(reason="x"))


# ===================================================== 10-12: screens
def test_10_aggregates_are_on_a_read_only_screen(c, ui, js):
    screen = js["screens"]["M48-rollups"]
    assert screen["model"] == "fix.iot.telemetry.rollup" and screen["create"] is False
    assert "M48-rollups" in nav_ids(js)
    _readings(c, c.stream, 2)
    policy = _policy(c)
    policy._fix_activate()
    c.env["fix.iot.downsample"].cron_retention()
    row = policy.rollup_ids[0]
    out = ui.records(
        c.operator,
        model="fix.iot.telemetry.rollup",
        cols=screen["cols"],
        domain=[["id", "=", row.id]],
    )
    assert out["rows"][0]["id"] == row.id
    assert set(screen["cols"]) <= set(out["rows"][0])
    res = ui.write(c.admin, model="fix.iot.telemetry.rollup", record_id=row.id, values={"value": 9})
    assert "error" in res


def test_11_an_alert_shows_what_it_recorded_read_only(c, ui, js):
    assert js["chips"]["M48:__by_screen__"]["M48-lifecycle"] == "M48-form-alert"
    fields_ = offered(js, "M48-form-alert")
    for name in ("resolution_note", "acked_on", "resolved_on", "stream_id", "last_value"):
        assert fields_[name]["readonly"], name
    assert all(f.get("readonly") for f in fields_.values()), "a platform record is not typed"
    rule = c.env["fix.iot.rule"].create(
        {"stream_id": c.stream.id, "operator": "gt", "threshold": 5.0}
    )
    alert = rule._fix_evaluate(c.stream, 9.0, fields.Datetime.now())
    alert.with_user(c.operator).action_ack()
    alert.with_user(c.operator).action_resolve(resolution_note="bearing greased")
    out = ui.form(
        c.operator,
        model="fix.iot.alert",
        record_id=alert.id,
        fields=[{"name": n} for n in fields_],
    )
    assert out["record"]["resolution_note"] == "bearing greased"
    assert out["record"]["stream_id"]["id"] == c.stream.id
    assert out["record"]["last_value"] == 9.0


def test_12_routing_shows_the_order_it_raised(c, ui, js):
    cols = js["screens"]["M48-routing"]["cols"]
    assert {"spine_work_order_id", "spine_service_order_id"} <= set(cols)
    fields_ = offered(js, "M48-form-action")
    assert fields_["spine_work_order_id"]["readonly"]
    assert fields_["spine_service_order_id"]["readonly"]
    action = act(c)
    out = ui.records(c.operator, model="fix.iot.action", cols=cols, domain=[["id", "=", action.id]])
    assert set(cols) <= set(out["rows"][0])


# ===================================================== 14: the disclosure upload
def test_14_the_disclosure_is_uploaded_not_picked_from_other_files(c, ui, js):
    fields_ = offered(js, "M48-form-consent")
    assert "disclosure_document_id" not in fields_, "it listed other records' file names"
    assert fields_["disclosure_file"]["type"] == "file"
    assert "disclosure_filename" in fields_
    res = ui.write(
        c.clerk,
        model="fix.iot.consent",
        values={
            "subject_type": "device",
            "device_id": c.device.id,
            "granted_by": "the owner",
            "signal_groups_permitted": "vibration",
            "disclosure_file": PDF,
            "disclosure_filename": "signed.pdf",
        },
    )
    assert "error" not in res, res
    consent = c.env["fix.iot.consent"].browse(res["id"])
    attachment = consent.disclosure_document_id
    assert attachment.name == "signed.pdf"
    assert (attachment.res_model, attachment.res_id) == ("fix.iot.consent", consent.id)
    assert base64.b64decode(attachment.datas) == base64.b64decode(PDF)
    assert consent.disclosure_name == "signed.pdf"
    consent.with_user(c.officer).action_verify()
    assert consent.verification == "verified"
    # a new upload is a change of the grant: it goes back for verification
    res = ui.write(
        c.clerk,
        model="fix.iot.consent",
        record_id=consent.id,
        values={"disclosure_file": PDF, "disclosure_filename": "second.pdf"},
    )
    assert "error" not in res, res
    assert consent.disclosure_name == "second.pdf" and consent.verification == "pending"


# ===================================================== 16-20: small labels
def test_16_the_revision_note_is_shown(c, js):
    assert offered(js, "M48-form-action")["revision_note"]["readonly"]
    assert "revision_note" in js["screens"]["M48-routing"]["cols"]


def test_17_a_recalled_rule_stops_showing_its_suppression(c):
    c.user(MANAGER)
    rule = c.env["fix.iot.rule"].create(
        {
            "stream_id": c.stream.id,
            "threshold": 5.0,
            "suppression_until": fields.Date.context_today(c.env["fix.iot.rule"]),
        }
    )
    rule.with_user(c.admin).action_pause(reason="maintenance window")
    assert rule.suppression_kind == "pause"
    rule.with_user(c.admin).action_recall_approval()
    assert not rule.suppression_kind and not rule.suppression_requested_by
    assert rule.approval_state == "none" and rule.state == "active"


def test_18_labels_and_back_links(js):
    assert js["screens"]["M48-form-stream"]["status"]["labels"]["silent"] == "Silent"
    assert js["screens"]["M48-form-downsample"]["back"] == "M48-downsample"


def test_19_the_coverage_note_counts_only_live_streams(c, ui):
    env = c.env
    env["fix.iot.stream"].create({"device_id": c.device.id, "metric": "draft_metric"})
    suspended = env["fix.iot.stream"].create({"device_id": c.device.id, "metric": "susp"})
    suspended.action_activate()
    suspended.action_suspend()
    pack = m48_surface.telemetry_coverage(env)
    live = [r for r in pack["rows"] if r["state"] in ("Active", "Silent") and r["coverage"] < 80]
    assert "%d live stream(s)" % len(live) in pack["notes"][0]


def test_20_the_inbox_shows_the_justification(c, ui, js):
    assert "justification" in js["inbox"]["cols"]
    c.user(DIRECTOR)
    director = c.user(DIRECTOR)
    action = act(c)
    action.with_user(c.operator).action_request_approval(justification="bearing failing")
    task = inbox_task(action, director)
    out = ui.records(
        director,
        model="fix.workflow.task",
        cols=js["inbox"]["cols"],
        domain=[["id", "=", task.id]],
    )
    assert out["rows"][0]["justification"] == "bearing failing"


# ===================================================== logic bugs
def test_activation_pending_locks_the_terms_and_refuses_a_second_request(c, ui):
    policy = _policy(c)
    call = {"model": "fix.iot.downsample", "ids": [policy.id], "method": "action_activate"}
    res = ui.action(c.admin, **call)
    assert res["success"], res
    out = ui.form(
        c.admin,
        model="fix.iot.downsample",
        record_id=policy.id,
        fields=[{"name": "target_interval_sec"}],
    )
    assert out["fields"][0]["readonly"]
    res = ui.write(
        c.admin,
        model="fix.iot.downsample",
        record_id=policy.id,
        values={"target_interval_sec": 3600},
    )
    assert "error" in res
    assert refused(c.env, lambda: policy.with_user(c.admin).write({"target_interval_sec": 3600}))
    res = ui.action(c.admin, **call)
    assert not res["success"], "a second activation request"
    assert (
        c.env["fix.iot.retention.change"].search_count(
            [("downsample_id", "=", policy.id), ("state", "=", "requested")]
        )
        == 1
    )
    # recalled: editable again
    change = c.env["fix.iot.retention.change"].search([("downsample_id", "=", policy.id)])
    change.with_user(c.admin).action_recall_approval()
    policy.with_user(c.admin).write({"target_interval_sec": 3600})
    assert policy.target_interval_sec == 3600


def _rule(c, **kw):
    return c.env["fix.iot.rule"].create(
        {
            "stream_id": c.stream.id,
            "threshold": 5.0,
            "severity": "major",
            "cooldown_min": 15,
            "duration_min": 0,
            "suppression_reason": "planned shutdown",
            "suppression_until": fields.Date.context_today(c.env["fix.iot.rule"])
            + timedelta(days=3),
            **kw,
        }
    )


@pytest.mark.parametrize(
    "vals",
    [{"severity": "minor"}, {"cooldown_min": 999999}, {"duration_min": 600}],
)
def test_a_setting_that_silences_a_rule_is_not_writable(c, ui, vals):
    rule = _rule(c)
    res = ui.write(c.admin, model="fix.iot.rule", record_id=rule.id, values=dict(vals))
    assert "error" in res, res
    assert refused(c.env, lambda: rule.with_user(c.admin).write(dict(vals)))
    rule.invalidate_recordset()
    assert (rule.severity, rule.cooldown_min, rule.duration_min) == ("major", 15, 0)


def test_tightening_a_setting_applies_at_once(c, ui, js):
    assert "action_change_settings" in buttons(js, "M48-alerts")
    rule = _rule(c, severity="minor", duration_min=30)
    res = ui.action(
        c.admin,
        model="fix.iot.rule",
        ids=[rule.id],
        method="action_change_settings",
        kwargs={"severity": "major", "cooldown_min": "5", "duration_min": ""},
    )
    assert res["success"], res
    assert (rule.severity, rule.cooldown_min, rule.duration_min) == ("major", 5, 30)
    assert rule.approval_state == "none"


def test_loosening_a_setting_needs_the_suppression_approval_and_lapses(c):
    rule = _rule(c)
    rule.with_user(c.admin).action_change_settings(
        severity="minor", cooldown_min="600", reason="planned shutdown"
    )
    assert (rule.severity, rule.cooldown_min) == ("major", 15), "nothing moves before approval"
    assert rule.approval_state == "pending" and rule.suppression_kind == "settings"
    assert refused(c.env, lambda: rule.with_user(c.admin).action_approve_suppression())
    task = rule.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == c.cto)
    task.with_user(c.cto).action_approve()
    assert (rule.severity, rule.cooldown_min) == ("minor", 600)
    assert rule.suppressed_by == c.cto
    # it ends at its expiry, and the earlier settings come back
    rule.sudo().write({"suppression_until": fields.Date.context_today(rule) - timedelta(days=1)})
    rule._fix_lapse_suppressions()
    assert (rule.severity, rule.cooldown_min) == ("major", 15)
    assert not rule.suppression_kind


def test_loosening_needs_a_reason_and_an_expiry(c):
    rule = _rule(c, suppression_until=False, suppression_reason=False)
    assert refused(c.env, lambda: rule.with_user(c.admin).action_change_settings(cooldown_min="60"))
    assert refused(c.env, lambda: rule.with_user(c.admin).action_change_settings())


def test_a_new_adapter_is_born_disabled_and_enable_needs_a_key(c, ui, js):
    assert "action_rotate_key" in buttons(js, "M48-adapters")
    res = ui.write(
        c.admin,
        model="fix.iot.adapter",
        values={"name": "gateway", "protocol": "mqtt", "auth_mode": "token"},
    )
    assert "error" not in res, res
    adapter = c.env["fix.iot.adapter"].browse(res["id"])
    assert adapter.state == "disabled" and not adapter.key_set
    adapter.with_user(c.admin).write({"credential_ref": "vault:iot/gateway"})
    call = {"model": "fix.iot.adapter", "ids": [adapter.id]}
    res = ui.action(c.admin, **call, method="action_enable")
    assert not res["success"] and "key" in res["error"].lower()
    # only the Administrator rotates
    res = ui.action(c.operator, **call, method="action_rotate_key")
    assert not res["success"]
    res = ui.action(c.admin, **call, method="action_rotate_key")
    assert res["success"], res
    key = res["result"]["secret"]
    assert key in res["result"]["note"], "shown once, in what the workspace displays"
    assert adapter.key_set and adapter.key_rotated_by == c.admin
    assert adapter.credential_rotated_on == fields.Date.context_today(adapter)
    stored = adapter.sudo().api_key_hash
    assert key not in stored and stored == hashlib.sha256(key.encode()).hexdigest()
    res = ui.action(c.admin, **call, method="action_enable")
    assert res["success"], res
    assert adapter.state == "enabled"
    # a rotation takes effect at once: the old key is dead
    res = ui.action(c.admin, **call, method="action_rotate_key")
    assert res["result"]["secret"] != key


def test_rotation_refuses_an_adapter_with_no_authentication(c):
    adapter = c.env["fix.iot.adapter"].create({"name": "open", "auth_mode": "none"})
    assert refused(c.env, lambda: adapter.with_user(c.admin).action_rotate_key())


def test_a_supplied_key_must_be_long_and_is_stored_hashed(c):
    adapter = c.env["fix.iot.adapter"].create({"name": "pasted", "auth_mode": "token"})
    assert refused(c.env, lambda: adapter.with_user(c.admin).action_rotate_key(key="short"))
    key = "z" * 40
    out = adapter.with_user(c.admin).action_rotate_key(key=key)
    assert key not in str(out), "the person already holds it: it is not echoed"
    assert adapter.sudo().api_key_hash == hashlib.sha256(key.encode()).hexdigest()


def test_an_officer_with_no_evidence_records_a_pending_consent(c, ui):
    res = ui.write(
        c.officer,
        model="fix.iot.consent",
        values={"subject_type": "device", "device_id": c.device.id},
    )
    assert "error" not in res, res
    bare = c.env["fix.iot.consent"].browse(res["id"])
    assert bare.verification == "pending" and not bare.verified_by
    assert not bare._fix_is_valid()
    res = ui.write(
        c.officer,
        model="fix.iot.consent",
        values={
            "subject_type": "device",
            "device_id": c.device.id,
            "evidence_ref": "signed form 12",
            "granted_by": "the owner",
            "signal_groups_permitted": "vibration",
        },
    )
    full = c.env["fix.iot.consent"].browse(res["id"])
    assert full.verification == "verified" and full.verified_by == c.officer


def test_preventive_wo_needs_the_role_and_the_confidence(c, ui):
    call = {"model": "fix.predictive.maintenance", "method": "action_create_preventive_wo"}
    good = pred(c)
    res = ui.action(c.clerk, **call, ids=[good.id])
    assert not res["success"] and "IoT Operator" in res["error"]
    assert not good.work_order_created
    weak = pred(c, confidence=0.05)
    res = ui.action(c.operator, **call, ids=[weak.id])
    assert not res["success"] and "0.5" in res["error"]
    assert not weak.work_order_created
    res = ui.action(c.operator, **call, ids=[good.id])
    assert res["success"], res
    assert good.work_order_created


def test_the_minimum_confidence_is_a_setting(c):
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_stream_registry.preventive_min_confidence", "0.9"
    )
    p = pred(c, confidence=0.8)
    assert refused(c.env, lambda: p.with_user(c.operator).action_create_preventive_wo())
    # a setting nobody can read closes, it does not open
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_stream_registry.preventive_min_confidence", "lots"
    )
    weak = pred(c, confidence=0.05)
    assert refused(c.env, lambda: weak.with_user(c.operator).action_create_preventive_wo())


def _done(c, action):
    action._guarded().write({"state": "dispatched", "outcome_evidence_ref": "JC-1"})
    action.with_user(c.operator2).action_done(outcome="confirmed", note="found it")


def test_a_second_action_cannot_overwrite_the_outcome(c):
    prediction = pred(c)
    first, second = act(c, prediction), act(c, prediction)
    _done(c, first)
    assert prediction.outcome == "confirmed" and prediction.outcome_action_id == first
    # it can neither go for approval ...
    assert refused(
        c.env,
        lambda: second.with_user(c.operator).action_request_approval(justification="again"),
    )
    # ... nor complete if it was already on its way
    second._guarded().write({"state": "dispatched", "outcome_evidence_ref": "JC-2"})
    assert refused(
        c.env,
        lambda: second.with_user(c.operator2).action_done(outcome="not_confirmed", note="no"),
    )
    prediction.invalidate_recordset()
    assert prediction.outcome == "confirmed" and prediction.outcome_action_id == first


def test_only_one_action_is_in_flight_on_a_prediction(c):
    c.user(DIRECTOR)
    prediction = pred(c)
    first, second = act(c, prediction), act(c, prediction)
    first.with_user(c.operator).action_request_approval(justification="x")
    assert refused(
        c.env, lambda: second.with_user(c.operator).action_request_approval(justification="y")
    )


def test_an_active_stream_keeps_its_device_and_metric(c, ui):
    other = c.env["fix.iot.device"].create(
        {"name": "other", "device_id": f"M48OP-O-{TAG}", "equipment_id": c.equipment.id}
    )
    for vals in ({"device_id": other.id}, {"metric": "temperature"}):
        res = ui.write(c.admin, model="fix.iot.stream", record_id=c.stream.id, values=dict(vals))
        assert "error" in res, vals
        assert refused(c.env, lambda v=vals: c.stream.with_user(c.admin).write(v))
    out = ui.form(
        c.admin,
        model="fix.iot.stream",
        record_id=c.stream.id,
        fields=[{"name": "device_id"}, {"name": "metric"}],
    )
    assert all(f["readonly"] for f in out["fields"])
    # a draft stream is still being set up
    draft = c.env["fix.iot.stream"].create({"device_id": c.device.id, "metric": "t"})
    draft.with_user(c.admin).write({"metric": "temperature"})
    assert draft.metric == "temperature"


# ===================================================== 5: the ingest entry point
def _adapter(c, **kw):
    adapter = c.env["fix.iot.adapter"].create(
        {"name": f"Gateway {uuid.uuid4().hex[:5]}", "auth_mode": "token", **kw}
    )
    return adapter, with_key(c.env, adapter)


def _handle(c, key, body):
    from odoo.addons.cd_stream_registry.controllers.iot_ingest import handle_ingest

    raw = body if isinstance(body, bytes) else json.dumps(body).encode()
    return handle_ingest(c.env, key, raw)


def test_5_a_keyed_adapter_records_a_reading_and_the_rules_fire(c):
    adapter, key = _adapter(c)
    c.stream.write({"adapter_id": adapter.id})
    rule = c.env["fix.iot.rule"].create(
        {"stream_id": c.stream.id, "operator": "gt", "threshold": 5.0, "severity": "major"}
    )
    status, payload = _handle(c, key, {"stream": c.stream.name, "value": 9.5})
    assert status == 200, payload
    reading = c.env["fix.iot.telemetry"].browse(payload["reading"])
    assert (reading.value, reading.metric, reading.device_id) == (9.5, "vibration", c.device)
    assert c.env["fix.iot.alert"].search_count([("rule_id", "=", rule.id)]) == 1
    assert payload["alerts"] == 1


@pytest.mark.parametrize("key", [None, "", "wrong-key"])
def test_5_no_key_or_a_wrong_key_is_401(c, key):
    adapter, _good = _adapter(c)
    c.stream.write({"adapter_id": adapter.id})
    before = c.env["fix.iot.telemetry"].search_count([("device_id", "=", c.device.id)])
    status, payload = _handle(c, key, {"stream": c.stream.name, "value": 1})
    assert status == 401 and payload["error"] == "unauthorized"
    assert c.env["fix.iot.telemetry"].search_count([("device_id", "=", c.device.id)]) == before


def test_5_an_adapter_never_rotated_is_closed(c):
    adapter = c.env["fix.iot.adapter"].create(
        {"name": f"Legacy {TAG}", "auth_mode": "token", "state": "enabled"}
    )
    c.stream.write({"adapter_id": adapter.id})
    status, _payload = _handle(c, "anything", {"stream": c.stream.name, "value": 1})
    assert status == 401
    status, _payload = _handle(c, "", {"stream": c.stream.name, "value": 1})
    assert status == 401
    # and the method itself refuses an adapter with no key
    assert refused(c.env, lambda: c.stream.ingest(1.0))


def test_5_a_key_works_only_on_its_own_adapters_streams(c):
    mine, key = _adapter(c)
    theirs, _other = _adapter(c)
    c.stream.write({"adapter_id": theirs.id})
    own = c.env["fix.iot.stream"].create(
        {"device_id": c.device.id, "metric": "own", "adapter_id": mine.id}
    )
    own.action_activate()
    status, _payload = _handle(c, key, {"stream": c.stream.name, "value": 1})
    assert status == 401, "another adapter's stream"
    status, payload = _handle(c, key, {"stream": own.name, "value": 1})
    assert status == 200, payload
    status, _payload = _handle(c, key, {"stream": "NO-SUCH-STREAM", "value": 1})
    assert status == 401


def test_5_a_disabled_or_unauthenticated_adapter_is_refused(c):
    adapter, key = _adapter(c)
    c.stream.write({"adapter_id": adapter.id})
    adapter._guarded().write({"state": "disabled"})
    status, payload = _handle(c, key, {"stream": c.stream.name, "value": 1})
    assert status == 403 and payload["error"] == "adapter_disabled"
    c.env.cr.execute(
        "UPDATE fix_iot_adapter SET state='enabled', auth_mode='none' WHERE id=%s", [adapter.id]
    )
    adapter.invalidate_recordset()
    status, payload = _handle(c, key, {"stream": c.stream.name, "value": 1})
    assert status == 403 and payload["error"] == "adapter_unauthenticated"


def test_5_consent_still_applies_and_names_nobody(c):
    customer = c.env["res.partner"].create({"name": f"Private Person {TAG}"})
    device = c.env["fix.iot.device"].create(
        {
            "name": "customer device",
            "device_id": f"M48OP-C-{TAG}",
            "equipment_id": c.equipment.id,
            "partner_id": customer.id,
        }
    )
    adapter, key = _adapter(c)
    stream = c.env["fix.iot.stream"].create(
        {"device_id": device.id, "metric": "vibration", "adapter_id": adapter.id}
    )
    stream.action_activate()
    status, payload = _handle(c, key, {"stream": stream.name, "value": 1})
    assert status == 403 and payload["error"] == "consent_required"
    assert customer.name not in json.dumps(payload)
    assert not c.env["fix.iot.telemetry"].search_count([("device_id", "=", device.id)])


def test_5_a_stream_not_live_is_refused(c):
    adapter, key = _adapter(c)
    draft = c.env["fix.iot.stream"].create(
        {"device_id": c.device.id, "metric": "d", "adapter_id": adapter.id}
    )
    status, payload = _handle(c, key, {"stream": draft.name, "value": 1})
    assert status == 409 and payload["error"] == "stream_not_active"


@pytest.mark.parametrize(
    "body",
    [
        b"not json",
        b"[1, 2]",
        {"value": 1},
        {"stream": "S"},
        {"stream": "S", "value": "abc"},
        {"stream": "S", "value": True},
        b'{"stream": "S", "value": NaN}',
        {"stream": "S", "value": 1, "timestamp": "yesterday"},
    ],
)
def test_5_a_bad_body_is_a_clean_400(c, body):
    adapter, key = _adapter(c)
    c.stream.write({"adapter_id": adapter.id, "name": "S"})
    status, payload = _handle(c, key, body)
    assert status == 400, payload
    assert "Traceback" not in json.dumps(payload)
    assert set(payload) == {"error", "message"}


def test_5_a_replay_and_a_future_reading_are_refused_cleanly(c):
    adapter, key = _adapter(c)
    c.stream.write({"adapter_id": adapter.id})
    stamp = "2026-01-02T03:04:05Z"
    body = {"stream": c.stream.name, "value": 1, "timestamp": stamp}
    status, payload = _handle(c, key, body)
    assert status == 200, payload
    reading = c.env["fix.iot.telemetry"].browse(payload["reading"])
    assert str(reading.timestamp) == "2026-01-02 03:04:05"
    status, payload = _handle(c, key, body)
    assert status == 409 and payload["error"] == "reading_rejected"
    future = fields.Datetime.to_string(fields.Datetime.now() + timedelta(days=1))
    status, payload = _handle(c, key, {"stream": c.stream.name, "value": 1, "timestamp": future})
    assert status == 409 and payload["error"] == "reading_rejected"


def test_5_an_unexpected_fault_leaves_no_stack_trace(c, monkeypatch):
    adapter, key = _adapter(c)
    c.stream.write({"adapter_id": adapter.id})
    cls = type(c.env["fix.iot.stream"])

    def boom(self, value, timestamp=None):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(cls, "ingest", boom)
    status, payload = _handle(c, key, {"stream": c.stream.name, "value": 1})
    assert status == 500 and payload["error"] == "server_error"
    assert "secret internal detail" not in json.dumps(payload)


def test_5_the_route_is_public_post_only(c, monkeypatch):
    # the routing map reads the database name from the serving thread
    monkeypatch.setattr(threading.current_thread(), "dbname", c.env.cr.dbname, raising=False)
    router = c.env["ir.http"].routing_map().bind("localhost")
    endpoint, _args = router.match("/iot/v1/ingest", method="POST")
    routing = endpoint.routing
    assert routing["auth"] == "none" and routing["csrf"] is False
    assert routing["type"] == "http"
    assert list(routing["methods"]) == ["POST"]


def _post(c, body, **headers):
    """Through Odoo's real WSGI application, on its own cursor: it cannot see this
    test's uncommitted rows, so it proves the route's refusals, and the positive
    path is handle_ingest above."""
    from odoo.http import root
    from werkzeug.test import Client

    return Client(root).post(
        "/iot/v1/ingest",
        data=body,
        content_type="application/json",
        headers={"X-Odoo-Database": c.env.cr.dbname, **headers},
    )


def test_5_the_real_route_answers_401_in_json_with_no_or_a_wrong_key(c):
    body = json.dumps({"stream": "NO-SUCH", "value": 1})
    for headers in ({}, {"X-Adapter-Key": "wrong"}):
        response = _post(c, body, **headers)
        assert response.status_code == 401
        assert response.get_json()["error"] == "unauthorized"
    assert _post(c, "x" * 5000, **{"X-Adapter-Key": "k"}).status_code == 413


def test_5_the_body_size_is_limited():
    from odoo.addons.cd_stream_registry.controllers import iot_ingest

    class Fake:
        content_length = None
        body = b"{}"

        def get_data(self, cache=True):
            assert self.content_length is not None, "an undeclared body is never read"
            assert self.content_length <= iot_ingest.MAX_BODY_BYTES, "checked before reading"
            return self.body

    undeclared = Fake()
    assert iot_ingest.read_body(undeclared) is None
    declared_big = Fake()
    declared_big.content_length = iot_ingest.MAX_BODY_BYTES + 1
    assert iot_ingest.read_body(declared_big) is None
    understated = Fake()
    understated.content_length = 2
    understated.body = b"x" * (iot_ingest.MAX_BODY_BYTES + 1)
    assert iot_ingest.read_body(understated) is None
    small = Fake()
    small.content_length = 2
    assert iot_ingest.read_body(small) == b"{}"
