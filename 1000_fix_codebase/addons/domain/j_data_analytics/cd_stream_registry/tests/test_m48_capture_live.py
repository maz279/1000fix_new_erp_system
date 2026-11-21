# M48 capture audit (2026-11-17): the records the sub-module pages now capture,
# driven the way the workspace drives them: the form schema is read from
# static/src/a07/m48.js with node, forms are saved through /p03/model/write
# with the echo the browser posts, and buttons go through /p03/model/action,
# as NON-ADMIN users holding the real M48 roles. Rolled back (`odoo_env`).
from __future__ import annotations

import base64
import hashlib
import json
import shutil
import subprocess
import types
import uuid
from datetime import timedelta
from pathlib import Path

import odoo.addons.cd_p03_portal as portal
import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

TAG = uuid.uuid4().hex[:6].upper()
REFUSED = (UserError, ValidationError, AccessError)
OPERATOR = "cd_stream_registry.group_iot_operator"
ADMIN = "cd_stream_registry.group_iot_admin"
MANAGER = "cd_stream_registry.group_iot_manager"
DWELL = "cd_stream_registry.rule_dwell_enforced"
MODEL = "m26.predictive.maintenance"
SRC = Path(portal.__file__).parent / "static" / "src" / "a07" / "m48.js"


@pytest.fixture(scope="module")
def js(tmp_path_factory):
    node = shutil.which("node")
    assert node, "node evaluates the screens: without it these tests prove nothing"
    tmp = tmp_path_factory.mktemp("m48cap")
    (tmp / "m48.mjs").write_text(SRC.read_text(encoding="utf-8"), "utf-8")
    (tmp / "run.mjs").write_text(
        "import * as M from './m48.mjs';\n"
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


def refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED:
        return True
    return False


def events(env, event_type, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    env["ir.config_parameter"].sudo().set_param(DWELL, "0")
    ou = env["operating.unit"].search([], limit=1)
    n = {"i": 0}

    def user(*xmlids):
        n["i"] += 1
        login = "m48cap_%d_%s" % (n["i"], TAG)
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

    x = types.SimpleNamespace(env=env, user=user)
    x.clerk = user()
    x.operator, x.operator2 = user(OPERATOR), user(OPERATOR)
    x.admin = user(ADMIN)
    x.cto, x.cto2 = user(MANAGER), user(MANAGER)
    x.equipment = env["fix.equipment"].create(
        {"code": f"M48CAP-EQ-{TAG}", "name": f"M48CAP Chiller {TAG}"}
    )
    x.adapter = env["fix.iot.adapter"].create(
        {"name": f"M48CAP File {TAG}", "protocol": "file", "auth_mode": "token"}
    )
    env.cr.execute(
        "UPDATE fix_iot_adapter SET api_key_hash=%s, state='enabled' WHERE id=%s",
        [hashlib.sha256(TAG.encode()).hexdigest(), x.adapter.id],
    )
    x.adapter.invalidate_recordset()
    x.device = env["fix.iot.device"].create(
        {"name": f"M48CAP Dev {TAG}", "device_id": f"M48CAP-{TAG}", "equipment_id": x.equipment.id}
    )
    x.stream = env["fix.iot.stream"].create(
        {
            "device_id": x.device.id,
            "adapter_id": x.adapter.id,
            "metric": "vibration",
            "unit": "mm/s",
        }
    )
    x.stream.action_activate()
    x.tech = env["hr.employee"].create({"name": f"M48CAP Tech {TAG}"})
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


def pred(c, engine=False, **kw):
    """Recorded by the IoT Operator, or (engine=True) by the M26 inference path:
    A07 ERP audit (2026-11-20) M48-02, only an engine score drives work."""
    vals = {
        "name": f"M48CAP-PDM-{uuid.uuid4().hex[:5]}",
        "equipment_id": c.equipment.id,
        "prediction": "failure_predicted",
        "confidence": 0.8,
        "estimated_days_to_failure": 10,
        "model_name": MODEL,
    }
    vals.update(kw)
    Pred = c.env["fix.predictive.maintenance"]
    return (Pred if engine else Pred.with_user(c.operator)).create(vals)


# ================================================ page 1: onboarding
def test_01_every_new_chip_form_opens_for_its_role(c, ui, js):
    for sid, role in (
        ("M48-form-iot-device", c.admin),
        ("M48-form-signal", c.admin),
        ("M48-form-scope", c.admin),
        ("M48-form-file-batch", c.admin),
        ("M48-form-window", c.operator),
        ("M48-form-outcome", c.operator2),
        ("M48-form-action", c.operator),
        ("M48-form-prediction", c.operator),
        ("M48-form-stream", c.admin),
        ("M48-form-rule", c.admin),
        ("M48-form-consent", c.admin),
    ):
        cfg = js["screens"][sid]
        out = ui.form(
            role,
            model=cfg["model"],
            fields=cfg_fields(js, sid),
            record_id=False,
            lines=cfg.get("lines") or False,
        )
        assert "error" not in out, (sid, out)


def test_02_a_signal_is_the_administrators_and_flags_a_value_out_of_range(c, ui, js):
    spec = {
        "code": f"bearing_temp_{TAG.lower()}",
        "name": "Bearing temperature",
        "canonical_unit": "C",
        "has_range": True,
        "expected_min": 0.0,
        "expected_max": 90.0,
        "sampling_interval_sec": 30,
    }
    assert_refused(save(ui, c.clerk, js, "M48-form-signal", changes=spec))
    sig = c.env["fix.iot.signal"].browse(
        new_id(save(ui, c.admin, js, "M48-form-signal", changes=spec))
    )
    # the stream takes its metric, unit and interval from the signal
    sid = new_id(
        save(
            ui,
            c.admin,
            js,
            "M48-form-stream",
            changes={
                "device_id": c.device.id,
                "adapter_id": c.adapter.id,
                "signal_id": sig.id,
                "metric": "anything",
                "source_address": "plant/chiller/bearing/temp",
            },
        )
    )
    stream = c.env["fix.iot.stream"].browse(sid)
    assert (stream.metric, stream.unit, stream.sample_interval_sec) == (sig.code, "C", 30)
    assert stream.source_address == "plant/chiller/bearing/temp"
    stream.action_activate()
    ok, _ = stream.ingest(55.0)
    hot, _ = stream.ingest(140.0)
    assert ok.sudo().quality_flag == "good"
    assert hot.sudo().quality_flag == "out_of_range"  # kept and flagged, not dropped
    assert refused(c.env, lambda: hot.with_user(c.cto).write({"quality_flag": "good"}))
    # a code that streams carry stays
    assert refused(c.env, lambda: sig.with_user(c.admin).write({"code": "renamed"}))


def test_03_a_device_records_its_identity_and_reports_through_a_gateway(c, ui, js):
    gw = new_id(
        save(
            ui,
            c.admin,
            js,
            "M48-form-iot-device",
            changes={
                "name": "Gateway",
                "device_id": f"GW-{TAG}",
                "device_type": "gateway",
                "connectivity": "cellular",
                "site_id": False,
            },
        )
    )
    dev = new_id(
        save(
            ui,
            c.admin,
            js,
            "M48-form-iot-device",
            changes={
                "name": "Sensor",
                "device_id": f"SN-{TAG}",
                "device_type": "sensor",
                "firmware": "2.4.1",
                "serial_no": f"SER-{TAG}",
                "connectivity": "lorawan",
                "gateway_id": gw,
                "equipment_id": c.equipment.id,
            },
        )
    )
    d = c.env["fix.iot.device"].browse(dev)
    assert (d.firmware, d.connectivity, d.gateway_id.id) == ("2.4.1", "lorawan", gw)
    # a sensor is not a gateway, and one physical device is registered once
    assert_refused(
        save(
            ui,
            c.admin,
            js,
            "M48-form-iot-device",
            record_id=dev,
            changes={"gateway_id": c.device.id},
        )
    )
    assert_refused(
        save(
            ui,
            c.admin,
            js,
            "M48-form-iot-device",
            changes={"name": "Dup", "device_id": f"SN-{TAG}", "device_type": "sensor"},
        )
    )
    # status and the decommission stamps are never typed
    assert_refused(
        save(ui, c.admin, js, "M48-form-iot-device", record_id=dev, changes={"status": "offline"})
    )


def test_04_decommissioning_a_stream_stops_it_and_closes_its_alerts(c, ui):
    c.env["fix.iot.rule"].create(
        {"stream_id": c.stream.id, "operator": "gt", "threshold": 5.0, "severity": "major"}
    )
    _, alert = c.stream.ingest(9.0)
    assert alert and alert.sudo().state == "new"
    assert_refused(
        ui.action(
            c.clerk,
            model="fix.iot.stream",
            ids=c.stream.ids,
            method="action_decommission",
            kwargs={"reason": "sensor removed"},
        )
    )
    assert_refused(
        ui.action(
            c.admin,
            model="fix.iot.stream",
            ids=c.stream.ids,
            method="action_decommission",
            kwargs={},
        )
    )
    assert_done(
        ui.action(
            c.admin,
            model="fix.iot.stream",
            ids=c.stream.ids,
            method="action_decommission",
            kwargs={"reason": "sensor removed"},
        )
    )
    c.env.invalidate_all()
    assert c.stream.state == "decommissioned"
    assert alert.sudo().state == "resolved" and "decommissioned" in alert.sudo().resolution_note
    assert refused(c.env, lambda: c.stream.ingest(1.0))
    assert refused(c.env, lambda: c.stream.action_activate())
    assert events(c.env, "telemetry.stream_decommissioned", c.stream.id)


def test_05_decommissioning_a_device_takes_its_streams_and_bars_new_ones(c, ui):
    assert_done(
        ui.action(
            c.admin,
            model="fix.iot.device",
            ids=c.device.ids,
            method="action_decommission",
            kwargs={"reason": "replaced"},
        )
    )
    c.env.invalidate_all()
    assert c.device.decommissioned and c.device.decommission_reason == "replaced"
    assert c.stream.state == "decommissioned"
    assert refused(
        c.env,
        lambda: c.env["fix.iot.stream"]
        .with_user(c.admin)
        .create({"device_id": c.device.id, "metric": "temp"}),
    )


# ================================================ page 1 / 5: criticality and health
def test_06_a_criticality_assessment_is_reasoned_and_drives_health(c, ui, js):
    base = {
        "equipment_id": c.equipment.id,
        "criticality": "high",
        "failure_consequence": "Cold room above 8 C spoils stock",
        "selection_rationale": "Vibration precedes compressor failure",
        "review_due": fields.Date.to_string(
            fields.Date.context_today(c.env.user) + timedelta(days=180)
        ),
    }
    assert_refused(save(ui, c.operator, js, "M48-form-scope", changes=base))  # IoT Administrator's
    assert_refused(
        save(ui, c.admin, js, "M48-form-scope", changes=dict(base, selection_rationale=" "))
    )
    # one asset: the equipment or the site, never neither
    assert_refused(save(ui, c.admin, js, "M48-form-scope", changes=dict(base, equipment_id=False)))
    scope = c.env["fix.iot.monitoring.scope"].browse(
        new_id(save(ui, c.admin, js, "M48-form-scope", changes=base))
    )
    assert scope.assessed_by_id == c.admin
    assert scope.device_count == 1
    assert_refused(
        ui.action(
            c.clerk,
            model="fix.iot.monitoring.scope",
            ids=scope.ids,
            method="action_score_now",
            kwargs={},
        )
    )
    assert_done(
        ui.action(
            c.operator,
            model="fix.iot.monitoring.scope",
            ids=scope.ids,
            method="action_score_now",
            kwargs={},
        )
    )
    first = c.env["fix.iot.health"].search([("device_id", "=", c.device.id)])
    assert len(first) == 1 and first.trend == "first"
    # no reading in 24 h: 100 - 20 = 80, healthy
    assert (first.index_value, first.band) == (80, "healthy")
    # three open alerts and the score worsens: 100 - 36 = 64 watch
    c.env["fix.iot.rule"].create(
        {"stream_id": c.stream.id, "operator": "gt", "threshold": 5.0, "severity": "major"}
    )
    c.env["fix.iot.rule"].create(
        {"stream_id": c.stream.id, "operator": "gt", "threshold": 6.0, "severity": "minor"}
    )
    c.env["fix.iot.rule"].create(
        {"stream_id": c.stream.id, "operator": "gt", "threshold": 7.0, "severity": "minor"}
    )
    c.stream.ingest(9.0)
    assert_done(
        ui.action(
            c.operator,
            model="fix.iot.monitoring.scope",
            ids=scope.ids,
            method="action_score_now",
            kwargs={},
        )
    )
    latest = c.env["fix.iot.health"].search(
        [("device_id", "=", c.device.id)], order="id desc", limit=1
    )
    assert (latest.index_value, latest.band, latest.trend, latest.previous_index) == (
        64,
        "watch",
        "worsening",
        80,
    )
    assert "3 open alert" in latest.factors
    assert events(c.env, "asset.health_degraded", latest.id)
    # history is written by scoring only
    assert refused(c.env, lambda: latest.with_user(c.cto).write({"index_value": 100}))
    assert refused(
        c.env,
        lambda: c.env["fix.iot.health"]
        .with_user(c.cto)
        .create(
            {
                "device_id": c.device.id,
                "computed_at": fields.Datetime.now(),
                "index_value": 99,
                "band": "healthy",
                "trend": "first",
            }
        ),
    )


def test_07_the_nightly_job_scores_every_active_scope(c):
    c.env["fix.iot.monitoring.scope"].with_user(c.admin).create(
        {
            "equipment_id": c.equipment.id,
            "criticality": "medium",
            "failure_consequence": "x",
            "selection_rationale": "y",
            "review_due": fields.Date.context_today(c.env.user) + timedelta(days=30),
        }
    )
    assert c.env["fix.iot.monitoring.scope"].cron_health() >= 1
    assert c.env["fix.iot.health"].search_count([("device_id", "=", c.device.id)]) == 1


# ================================================ page 2: file batch channel
def _csv(rows):
    text = "stream,timestamp,value\n" + "\n".join(",".join(r) for r in rows) + "\n"
    return base64.b64encode(text.encode()).decode()


def test_08_a_file_batch_goes_through_the_live_ingest_gates(c, ui, js):
    c.env["fix.iot.rule"].create(
        {"stream_id": c.stream.id, "operator": "gt", "threshold": 5.0, "severity": "major"}
    )
    now = fields.Datetime.now()
    stamp = lambda h: fields.Datetime.to_string(now - timedelta(hours=h))  # noqa: E731
    future = fields.Datetime.to_string(now + timedelta(days=2))
    content = _csv(
        [
            (c.stream.name, stamp(3), "1.5"),
            (c.stream.name, stamp(2), "9.0"),  # breach: one alert
            (c.stream.name, stamp(2), "9.0"),  # replay: duplicate refused
            ("NO-SUCH-STREAM", stamp(1), "1.0"),
            (c.stream.name, "yesterday", "1.0"),
            (c.stream.name, future, "1.0"),  # future dated
            (c.stream.name, stamp(1), "abc"),
        ]
    )
    batch_vals = {
        "adapter_id": c.adapter.id,
        "batch_file": content,
        "batch_filename": "export.csv",
        "source_ref": "EXP-1",
    }
    assert_refused(save(ui, c.clerk, js, "M48-form-file-batch", changes=batch_vals))
    bid = new_id(save(ui, c.admin, js, "M48-form-file-batch", changes=batch_vals))
    out = ui.action(
        c.admin, model="fix.iot.file.batch", ids=[bid], method="action_process", kwargs={}
    )
    assert_done(out)
    batch = c.env["fix.iot.file.batch"].browse(bid)
    assert (
        batch.state,
        batch.rows_total,
        batch.rows_accepted,
        batch.rows_rejected,
        batch.alerts_raised,
    ) == ("processed", 7, 2, 5, 1)
    assert "NO-SUCH-STREAM" in batch.report and "row 6" in batch.report
    assert c.env["fix.iot.telemetry"].search_count([("device_id", "=", c.device.id)]) == 2
    # processed evidence is kept as it was
    assert_refused(
        save(
            ui, c.admin, js, "M48-form-file-batch", record_id=bid, changes={"source_ref": "changed"}
        )
    )
    assert refused(c.env, lambda: batch.with_user(c.admin).unlink())
    assert_refused(
        ui.action(
            c.admin, model="fix.iot.file.batch", ids=[bid], method="action_process", kwargs={}
        )
    )


# ================================================ page 4: maintenance window
def test_09_a_maintenance_window_is_bounded_and_approved_by_another_manager(c, ui, js):
    now = fields.Datetime.now()
    window = {
        "device_id": c.device.id,
        # a day either side: the form reads times in the user's zone (UTC+6)
        "date_from": fields.Datetime.to_string(now - timedelta(days=1)),
        "date_to": fields.Datetime.to_string(now + timedelta(days=1)),
        "reason": "Compressor overhaul",
    }
    assert_refused(save(ui, c.clerk, js, "M48-form-window", changes=window))
    assert_refused(
        save(
            ui,
            c.operator,
            js,
            "M48-form-window",
            changes=dict(window, date_to=fields.Datetime.to_string(now + timedelta(days=45))),
        )
    )
    wid = new_id(save(ui, c.cto, js, "M48-form-window", changes=window))
    w = c.env["fix.iot.maintenance.window"].browse(wid)
    assert_done(
        ui.action(
            c.cto, model="fix.iot.maintenance.window", ids=[wid], method="action_request", kwargs={}
        )
    )
    assert_refused(
        ui.action(
            c.cto, model="fix.iot.maintenance.window", ids=[wid], method="action_approve", kwargs={}
        )
    )
    assert_refused(
        ui.action(
            c.operator,
            model="fix.iot.maintenance.window",
            ids=[wid],
            method="action_approve",
            kwargs={},
        )
    )
    assert_refused(
        save(ui, c.cto, js, "M48-form-window", record_id=wid, changes={"reason": "longer"})
    )
    # one device or one site, never neither (an empty field is not even posted)
    assert_refused(save(ui, c.cto, js, "M48-form-window", changes=dict(window, device_id=False)))
    assert_done(
        ui.action(
            c.cto2,
            model="fix.iot.maintenance.window",
            ids=[wid],
            method="action_approve",
            kwargs={},
        )
    )
    c.env["fix.iot.rule"].create(
        {"stream_id": c.stream.id, "operator": "gt", "threshold": 5.0, "severity": "major"}
    )
    _, raised = c.stream.ingest(9.0)
    assert not raised
    c.env.invalidate_all()
    assert w.suppressed_count == 1
    # after the window, the same breach alerts
    c.env.cr.execute(
        "UPDATE fix_iot_maintenance_window SET date_to=%s WHERE id=%s",
        [now - timedelta(minutes=5), wid],
    )
    c.env.invalidate_all()
    _, raised = c.stream.ingest(9.5)
    assert raised


# ================================================ page 6: prediction outcome
def test_10_an_unactioned_prediction_gets_its_outcome_from_someone_else(c, ui, js):
    p = pred(
        c,
        estimated_days_to_failure=10,
        failure_mode="bearing wear",
        rul_low_days=6,
        rul_high_days=15,
    )
    # the operator who recorded the score does not mark it right
    assert_refused(
        save_action(
            ui,
            c.operator,
            js,
            "M48-form-outcome",
            p,
            outcome="confirmed",
            outcome_note="it failed",
            outcome_evidence_ref="JC-1",
        )
    )
    # a false alarm is known only after the horizon
    assert_refused(
        save_action(
            ui,
            c.operator2,
            js,
            "M48-form-outcome",
            p,
            outcome="false_alarm",
            outcome_note="no failure",
        )
    )
    # a confirmed failure needs its evidence
    assert_refused(
        save_action(
            ui,
            c.operator2,
            js,
            "M48-form-outcome",
            p,
            outcome="confirmed",
            outcome_note="it failed",
        )
    )
    assert_refused(
        save_action(
            ui,
            c.clerk,
            js,
            "M48-form-outcome",
            p,
            outcome="confirmed",
            outcome_note="it failed",
            outcome_evidence_ref="JC-1",
        )
    )
    assert_done(
        save_action(
            ui,
            c.operator2,
            js,
            "M48-form-outcome",
            p,
            outcome="confirmed",
            outcome_note="bearing seized",
            outcome_evidence_ref="JC-77",
        )
    )
    c.env.invalidate_all()
    assert (p.outcome, p.outcome_evidence_ref, p.outcome_recorded_by) == (
        "confirmed",
        "JC-77",
        c.operator2,
    )
    assert (
        events(c.env, "intervention.outcome_recorded", p.id)[0]["intervention_performed"] is False
    )
    assert_refused(
        save_action(
            ui, c.operator2, js, "M48-form-outcome", p, outcome="unknown", outcome_note="again"
        )
    )
    # the outcome is never typed on the prediction form
    assert_refused(
        save(
            ui,
            c.operator2,
            js,
            "M48-form-prediction",
            record_id=p.id,
            changes={"outcome": "false_alarm"},
        )
    )


def test_11_after_its_horizon_a_prediction_can_be_a_false_alarm_or_unknown(c, ui, js):
    old = fields.Datetime.now() - timedelta(days=5)
    p = c.env["fix.predictive.maintenance"].create(
        {
            "name": f"M48CAP-OLD-{TAG}",
            "equipment_id": c.equipment.id,
            "prediction": "degrading",
            "confidence": 0.7,
            "estimated_days_to_failure": 2,
            "model_name": MODEL,
            "last_evaluated": old,
        }
    )
    assert_done(
        save_action(
            ui,
            c.operator2,
            js,
            "M48-form-outcome",
            p,
            outcome="unknown",
            outcome_note="asset sold before the horizon",
        )
    )
    healthy = pred(c, prediction="healthy")
    assert_refused(
        save_action(
            ui,
            c.operator2,
            js,
            "M48-form-outcome",
            healthy,
            outcome="confirmed",
            outcome_note="x",
            outcome_evidence_ref="y",
        )
    )


def test_12_an_action_under_way_records_the_outcome_itself(c, ui, js):
    p = pred(c)
    action = (
        c.env["fix.iot.action"]
        .with_user(c.operator)
        .create({"prediction_id": p.id, "action_type": "inspect", "technician_id": c.tech.id})
    )
    action.sudo()._guarded().write({"state": "approved"})
    assert_refused(
        save_action(
            ui,
            c.operator2,
            js,
            "M48-form-outcome",
            p,
            outcome="confirmed",
            outcome_note="x",
            outcome_evidence_ref="y",
        ),
        "under way",
    )


def test_13_the_rul_interval_brackets_the_estimate(c):
    assert refused(
        c.env, lambda: pred(c, estimated_days_to_failure=10, rul_low_days=12, rul_high_days=20)
    )
    assert refused(
        c.env, lambda: pred(c, estimated_days_to_failure=10, rul_low_days=2, rul_high_days=8)
    )
    assert pred(c, estimated_days_to_failure=10, rul_low_days=5, rul_high_days=20)


# ================================================ page 7: parts and skill
def test_14_an_intervention_names_its_parts_and_skill(c, ui, js):
    c.user("cd_facility.group_operations_director")  # the approver exists
    part = c.env["product.product"].create({"name": f"Bearing 6204 {TAG}"})
    comp = c.env["fix.competency"].create({"code": f"HVAC-{TAG}", "name": "HVAC compressor"})
    p = pred(c, engine=True)
    base = {
        "prediction_id": p.id,
        "action_type": "replace",
        "priority": "high",
        "technician_id": c.tech.id,
        "recommended_action": "Replace the drive-end bearing",
    }
    assert_refused(
        save(
            ui,
            c.operator,
            js,
            "M48-form-action",
            changes=dict(base, skill_code="NOPE"),
            new_rows=[{"product_id": part.id, "quantity": 2}],
        )
    )
    aid = new_id(
        save(
            ui,
            c.operator,
            js,
            "M48-form-action",
            changes=dict(base, skill_code=comp.code),
            new_rows=[{"product_id": part.id, "quantity": 2}],
        )
    )
    action = c.env["fix.iot.action"].browse(aid)
    assert action.skill_name == "HVAC compressor"
    assert len(action.part_ids) == 1 and action.part_ids.quantity == 2
    assert action.parts_state in ("unknown", "short")  # nothing in stock
    assert_done(
        ui.action(
            c.operator,
            model="fix.iot.action",
            ids=[aid],
            method="action_request_approval",
            kwargs={"justification": "bearing wear predicted"},
        )
    )
    payload = events(c.env, "intervention.proposed", aid)[0]
    assert payload["skill"] == comp.code and payload["parts"][0]["quantity"] == 2
    # what was approved is fixed: parts and skill change only through Revise Terms
    action.sudo()._guarded().write({"state": "approved"})
    assert refused(c.env, lambda: action.part_ids.with_user(c.operator).write({"quantity": 5}))
    assert refused(c.env, lambda: action.with_user(c.operator).write({"skill_code": False}))
