"""A07 ERP audit (2026-11-20) - M48 fixes (builder stream S5), against the ORM.

Each test names the finding it proves. Non-admin users hold the real roles; the
transaction is rolled back after every test."""

from __future__ import annotations

import base64
import types
import uuid
from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

TAG = uuid.uuid4().hex[:6].upper()
REFUSED = (UserError, ValidationError, AccessError)
OPERATOR = "cd_stream_registry.group_iot_operator"
ADMIN = "cd_stream_registry.group_iot_admin"
CONSENT = "cd_stream_registry.group_iot_consent_officer"
DIRECTOR = "cd_facility.group_operations_director"
MODEL = "m26.predictive.maintenance"
SIGNALS = "vibration, temperature, odometer_km"
# the gate itself is tested here: the suite governs the model explicitly
GOVERN_PDM = False


def refused(env, fn):
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED:
        return True
    return False


def govern(env, code=MODEL):
    """Give the model's serving version a passed accuracy gate (what M26 review
    records): only then do its engine scores drive work (M48-02)."""
    model = env["fix.ml.model"].search([("code", "=", code)], limit=1)
    version = model._serving_version()
    env["fix.ml.evaluation.gate"].create(
        {"version_id": version.id, "gate": "accuracy", "result": "passed"}
    )
    return version


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    env["ir.config_parameter"].sudo().set_param(
        "cd_stream_registry.consent_required_for", "customer"
    )
    ou = env["operating.unit"].search([], limit=1)
    n = {"i": 0}

    def user(*xmlids):
        n["i"] += 1
        login = "a07erp48_%d_%s" % (n["i"], TAG)
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
    x.officer, x.officer2 = user(CONSENT), user(CONSENT)
    x.director = user(DIRECTOR)
    x.equipment = env["fix.equipment"].create(
        {"code": f"E48-EQ-{TAG}", "name": f"E48 Pump {TAG}", "category": "Electrical"}
    )
    x.partner = env["res.partner"].create({"name": f"E48 Customer {TAG}"})
    x.device = env["fix.iot.device"].create(
        {"name": f"E48 Dev {TAG}", "device_id": f"E48-{TAG}", "equipment_id": x.equipment.id}
    )
    x.stream = env["fix.iot.stream"].create(
        {"device_id": x.device.id, "metric": "vibration", "unit": "mm/s"}
    )
    x.stream.action_activate()
    x.tech = env["hr.employee"].create({"name": f"E48 Tech {TAG}"})
    return x


def prediction(c, **kw):
    vals = {
        "name": f"E48-PDM-{TAG}",
        "equipment_id": c.equipment.id,
        "prediction": "failure_predicted",
        "confidence": 0.9,
        "estimated_days_to_failure": 5,
        "model_name": MODEL,
    }
    vals.update(kw)
    return c.env["fix.predictive.maintenance"].create(vals)


def customer_consent(c, device, **kw):
    vals = {
        "subject_type": "customer",
        "partner_id": c.partner.id,
        "device_id": device.id,
        "purpose": "service",
        "evidence_ref": "signed form",
        "granted_by": "the customer",
        "signal_groups_permitted": SIGNALS,
    }
    vals.update(kw)
    return c.env["fix.iot.consent"].create(vals)


# ================================================================== M48-01
def test_m48_01_clearing_the_customer_does_not_undo_a_revocation(c):
    env = c.env
    device = env["fix.iot.device"].create(
        {
            "name": f"E48 Cust {TAG}",
            "device_id": f"E48C-{TAG}",
            "equipment_id": c.equipment.id,
            "partner_id": c.partner.id,
        }
    )
    stream = env["fix.iot.stream"].create({"device_id": device.id, "metric": "vibration"})
    stream.action_activate()
    consent = customer_consent(c, device)
    stream.ingest(1.0)
    consent.action_revoke("letter")
    assert stream.state == "suspended" and stream.suspension_cause == "consent"
    assert device.consent_ever_recorded
    # the administrator cannot clear the customer by a plain edit
    assert refused(env, lambda: device.with_user(c.admin).write({"partner_id": False}))
    # nor resume the stream the consent gate stopped
    assert refused(env, lambda: stream.with_user(c.admin).action_activate())
    # the Consent Officer may re-bind, with a reason, but the device remembers the
    # consent: the exemption does not come back and the stream stays refused
    device.with_user(c.officer).action_change_binding("partner_id", False, "sold to company")
    assert not device.partner_id and "sold to company" in device.binding_log
    assert refused(env, lambda: stream.with_user(c.officer).action_activate())
    assert stream.state == "suspended"


def test_m48_01_binding_is_free_while_nothing_was_collected(c):
    env = c.env
    device = env["fix.iot.device"].create({"name": f"E48 New {TAG}", "device_id": f"E48N-{TAG}"})
    device.with_user(c.admin).write({"equipment_id": c.equipment.id})
    assert device.equipment_id == c.equipment


# ================================================================== M48-02
def test_m48_02_a_typed_score_never_drives_work(c):
    govern(c.env)
    typed = prediction(c).with_user(c.operator)
    typed = (
        c.env["fix.predictive.maintenance"]
        .with_user(c.operator)
        .create(
            {
                "name": f"E48-TYPED-{TAG}",
                "equipment_id": c.equipment.id,
                "prediction": "failure_predicted",
                "confidence": 0.95,
                "model_name": MODEL,
            }
        )
    )
    assert typed.score_source == "manual" and not typed.model_published
    with pytest.raises(UserError, match="by hand"):
        typed.with_user(c.operator2).action_create_preventive_wo("needed")


def test_m48_02_an_engine_score_needs_a_governed_version(c):
    engine = prediction(c)
    assert engine.score_source == "engine"
    assert engine.model_version_id, "the serving version is pinned on the score"
    # the seeded aggregator version was never evaluated: it scores nothing that counts
    assert not engine.model_published
    assert "accuracy" in engine._fix_publication_problem()
    govern(c.env)
    engine.invalidate_recordset()
    assert engine.model_published
    # a demoted version no longer drives work
    engine.model_version_id.with_context(ml_promotion_engine=True).write({"state": "demoted"})
    engine.invalidate_recordset()
    assert not engine.model_published


def test_m48_02_the_version_is_not_typed(c):
    version = govern(c.env)
    assert refused(
        c.env,
        lambda: c.env["fix.predictive.maintenance"]
        .with_user(c.operator)
        .create(
            {
                "name": f"E48-V-{TAG}",
                "equipment_id": c.equipment.id,
                "model_name": MODEL,
                "model_version_id": version.id,
            }
        ),
    )


# ================================================================== M48-03 / D17(c)
def test_m48_03_preventive_wo_needs_the_directors_approval(c):
    env = c.env
    govern(env)
    p = prediction(c)
    Outbox = env["fix.event.outbox"]

    def published():
        return Outbox.search_count(
            [("event_type", "=", "predictive_maintenance.wo_created"), ("aggregate_id", "=", p.id)]
        )

    # a reason is required
    assert refused(env, lambda: p.with_user(c.operator).action_create_preventive_wo())
    p.with_user(c.operator).action_create_preventive_wo(
        "bearing failing", scheduled_on="2026-12-01"
    )
    action = p.preventive_action_id
    assert action.preventive_request and action.state == "proposed"
    assert action.approval_state == "pending" and p.work_order_created
    assert published() == 0, "nothing is raised before the approval"
    # the requester does not decide it
    assert not inbox_task(action, c.operator)
    approve_via_inbox(action, c.director, requester=c.operator)
    assert action.state == "approved" and published() == 1
    # D17(c): the approval pins the date
    assert refused(env, lambda: action.with_user(c.operator).write({"scheduled_on": "2026-12-05"}))
    assert str(action.scheduled_on) == "2026-12-01"


def test_m48_03_cancelling_the_request_frees_the_prediction(c):
    govern(c.env)
    p = prediction(c)
    p.with_user(c.operator).action_create_preventive_wo("check it")
    p.preventive_action_id.with_user(c.operator).action_cancel("not needed")
    assert not p.work_order_created and not p.preventive_action_id


# ================================================================== M48-09
def test_m48_09_prevented_is_an_outcome_and_a_true_positive(c, monkeypatch):
    env = c.env
    # the order behind the action is the spine's (its blockers are tested there)
    monkeypatch.setattr(type(env["fix.iot.action"]), "_fix_completion_blockers", lambda self: [])
    govern(env)
    p = prediction(c)
    action = env["fix.iot.action"].create(
        {"prediction_id": p.id, "action_type": "replace", "technician_id": c.tech.id}
    )
    action._guarded().write({"state": "dispatched", "outcome_evidence_ref": "JC-1"})
    action.sudo().action_done_prevented("bearing replaced before seizure")
    assert action.outcome == "prevented" and p.outcome == "prevented"
    from odoo.addons.cd_p03_portal.controllers.a07 import m48 as pack

    pred = env["fix.predictive.maintenance"].browse(p.id)
    precision, tp, fp = pack._precision(pred)
    assert (precision, tp, fp) == (100.0, 1, 0)


# ================================================================== M48-11
def test_m48_11_a_late_reading_is_aggregated_before_purge(c):
    env = c.env
    env["ir.config_parameter"].sudo().set_param("cd_stream_registry.retention_purge_enabled", "1")
    stream = c.stream.sudo()
    stream._guarded().write({"retention_days": 1})
    policy = env["fix.iot.downsample"].create(
        {"stream_id": stream.id, "raw_interval_sec": 60, "target_interval_sec": 300}
    )
    policy.action_activate()
    t0 = fields.Datetime.now().replace(second=0, microsecond=0) - timedelta(days=3)
    t0 = t0 - timedelta(minutes=t0.minute % 5)
    stream.ingest(1.0, t0)
    stream.ingest(3.0, t0 + timedelta(minutes=1))
    policy.cron_retention()
    bucket = policy.rollup_ids.filtered(lambda r: r.bucket_start == t0)
    assert (bucket.value, bucket.points) == (2.0, 2)
    # a late reading in that bucket re-opens it
    stream.ingest(8.0, t0 + timedelta(minutes=2))
    assert policy.dirty_from
    policy.cron_retention()
    bucket = policy.rollup_ids.filtered(lambda r: r.bucket_start == t0)
    assert (bucket.value, bucket.points) == (4.0, 3)
    assert not policy.dirty_from


def test_m48_11_purge_keeps_a_reading_no_aggregate_holds(c):
    env = c.env
    stream = c.stream.sudo()
    policy = env["fix.iot.downsample"].create(
        {"stream_id": stream.id, "raw_interval_sec": 60, "target_interval_sec": 300}
    )
    policy.action_activate()
    old = fields.Datetime.now() - timedelta(days=400)
    reading, _a = stream.ingest(5.0, old)
    reading = reading.sudo()
    # the bucket exists but was written BEFORE the reading arrived
    env["fix.iot.telemetry.rollup"].sudo()._guarded().create(
        {
            "downsample_id": policy.id,
            "bucket_start": policy._fix_bucket(reading.timestamp),
            "bucket_seconds": 300,
            "aggregation": "avg",
            "value": 0.0,
            "points": 0,
        }
    )
    env.cr.execute(
        "UPDATE fix_iot_telemetry_rollup SET create_date = %s WHERE downsample_id = %s",
        (reading.create_date - timedelta(hours=1), policy.id),
    )
    env["fix.iot.telemetry.rollup"].invalidate_model()
    assert not policy._fix_purgeable(reading)


# ================================================================== M48-12
def test_m48_12_file_batch_keeps_the_offset_and_reads_dhaka_local(c):
    env = c.env
    adapter = env["fix.iot.adapter"].create(
        {"name": f"E48 File {TAG}", "protocol": "file", "credential_ref": "vault/e48"}
    )
    adapter.action_rotate_key()
    adapter.action_enable()
    c.stream.sudo().write({"adapter_id": adapter.id})
    day = (fields.Datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    csv = "stream,timestamp,value\n%s,%sT10:00:00+06:00,1\n%s,%s 11:00:00,2\n" % (
        c.stream.name,
        day,
        c.stream.name,
        day,
    )
    batch = env["fix.iot.file.batch"].create(
        {"adapter_id": adapter.id, "batch_file": base64.b64encode(csv.encode()).decode()}
    )
    batch.action_process()
    assert batch.rows_accepted == 2, batch.report
    stamps = sorted(
        env["fix.iot.telemetry"]
        .search([("device_id", "=", c.device.id), ("metric", "=", "vibration")])
        .mapped("timestamp")
    )
    assert [s.strftime("%H:%M") for s in stamps] == ["04:00", "05:00"]


# ================================================================== M48-13
def test_m48_13_the_pack_shows_the_stored_index(c):
    env = c.env
    env["fix.iot.monitoring.scope"].create(
        {
            "equipment_id": c.equipment.id,
            "criticality": "high",
            "failure_consequence": "downtime",
            "selection_rationale": "vibration predicts bearing failure",
            "review_due": fields.Date.today() + timedelta(days=200),
        }
    )
    row = env["fix.iot.health"]._fix_score(c.device)
    from odoo.addons.cd_p03_portal.controllers.a07 import m48 as pack

    out = pack.asset_health(env)
    mine = [r for r in out["rows"] if r["identifier"] == c.device.device_id]
    assert mine and mine[0]["score"] == row.index_value
    assert mine[0]["band"] == dict(row._fields["band"].selection)[row.band]


# ================================================================== M48-14 / D17(b)
def test_d17b_retention_by_criticality_and_tiers(c):
    env = c.env
    signal = env["fix.iot.signal"].create(
        {"code": f"e48_temp_{TAG.lower()}", "name": "Temp", "criticality_class": "high"}
    )
    stream = env["fix.iot.stream"].create({"device_id": c.device.id, "signal_id": signal.id})
    assert stream.retention_days == 365
    low = env["fix.iot.signal"].create(
        {"code": f"e48_low_{TAG.lower()}", "name": "Low", "criticality_class": "low"}
    )
    assert (
        env["fix.iot.stream"].create({"device_id": c.device.id, "signal_id": low.id}).retention_days
        == 30
    )
    # raw purge is ON by default and keeps nothing an hourly aggregate does not hold
    env["ir.config_parameter"].sudo().set_param("cd_stream_registry.retention_purge_enabled", "")
    s = c.stream.sudo()
    s._guarded().write({"retention_days": 30})
    old = fields.Datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(days=60)
    s.ingest(1.0, old)
    s.ingest(3.0, old + timedelta(minutes=10))
    out = env["fix.iot.downsample"].cron_retention()
    aggs = env["fix.iot.telemetry.aggregate"].search([("stream_id", "=", s.id)])
    hour = aggs.filtered(lambda a: a.tier == "hour" and a.bucket_start == old)
    assert (hour.value_avg, hour.points) == (2.0, 2)
    assert aggs.filtered(lambda a: a.tier == "day")
    assert out["tier_raw_dropped"] == 2
    assert not env["fix.iot.telemetry"].search_count(
        [("device_id", "=", c.device.id), ("timestamp", "<", old + timedelta(hours=1))]
    )


def test_m48_14_a_device_that_streamed_is_not_deleted(c):
    manager = c.user("cd_stream_registry.group_iot_manager")
    c.stream.ingest(1.0)
    assert refused(c.env, lambda: c.device.with_user(manager).unlink())


# ================================================================== M48-16
def test_m48_16_consent_day_is_the_dhaka_day(c):
    env = c.env
    root = env.ref("base.user_root")
    root.tz = "Europe/Brussels"
    # 20 Nov 20:00 UTC = 21 Nov 02:00 in Dhaka, still 20 Nov in Brussels
    with freeze_time("2026-11-20 20:00:00"):
        consent = customer_consent(
            c,
            c.device,
            subject_type="device",
            partner_id=False,
            valid_to="2026-11-20",
            granted_on="2026-11-01",
        )
        assert not consent.sudo().with_user(root)._fix_is_valid()


# ================================================================== M48-18
def test_m48_18_offline_alert_closes_when_the_device_reports(c):
    device = c.device.sudo()
    device._fix_mark_offline()
    alert = c.env["fix.iot.alert"].search([("device_id", "=", device.id)])
    assert alert.state == "new"
    c.stream.ingest(2.0)
    assert alert.state == "resolved" and "reporting again" in alert.resolution_note


def test_m48_18_one_silent_stream_of_two_degrades_the_device(c):
    env = c.env
    other = env["fix.iot.stream"].create(
        {"device_id": c.device.id, "metric": "temperature", "sample_interval_sec": 60}
    )
    other.action_activate()
    other.ingest(20.0)
    c.stream.sudo()._guarded().write({"activated_on": fields.Datetime.now() - timedelta(hours=2)})
    with freeze_time(datetime.utcnow() + timedelta(minutes=30)):
        env["fix.iot.stream"].cron_liveness()
    assert c.device.status in ("degraded", "offline")


# ================================================================== M48-19
def test_m48_19_activation_needs_a_scope_in_force(c):
    env = c.env
    signal = env["fix.iot.signal"].create({"code": f"e48_vib_{TAG.lower()}", "name": "Vibration"})
    stream = env["fix.iot.stream"].create({"device_id": c.device.id, "signal_id": signal.id})
    assert refused(env, lambda: stream.with_user(c.admin).action_activate())
    scope = env["fix.iot.monitoring.scope"].create(
        {
            "equipment_id": c.equipment.id,
            "criticality": "high",
            "failure_consequence": "downtime",
            "selection_rationale": "bearing wear",
            "signal_ids": [(6, 0, signal.ids)],
            "review_due": fields.Date.today() + timedelta(days=100),
        }
    )
    stream.with_user(c.admin).action_activate()
    assert stream.state == "active"
    # the review-due job raises the review task once
    scope.write(
        {
            "assessed_on": fields.Date.today() - timedelta(days=10),
            "review_due": fields.Date.today() - timedelta(days=1),
        }
    )
    assert env["fix.iot.monitoring.scope"].cron_review_due() >= 1
    assert scope.review_flagged_for == scope.review_due


# ================================================================== M48-20 / 21
def test_m48_20_clock_skew_and_atomic_duplicates(c):
    env = c.env
    s = c.stream.sudo()
    s.ingest(1.0, fields.Datetime.now() + timedelta(seconds=60))
    assert refused(env, lambda: s.ingest(1.0, fields.Datetime.now() + timedelta(seconds=600)))
    env.cr.execute(
        "SELECT indexdef FROM pg_indexes WHERE tablename = 'fix_iot_telemetry' "
        "AND indexdef ILIKE '%%source_stamped%%'"
    )
    assert env.cr.fetchone(), "the duplicate key is a unique index, not a search"


def test_m48_21_a_back_dated_reading_never_closes_a_gap_before_it_opened(c):
    env = c.env
    s = c.stream.sudo()
    since = fields.Datetime.now() - timedelta(hours=1)
    gap = (
        env["fix.iot.gap"]
        .sudo()
        ._guarded()
        .create({"stream_id": s.id, "gap_from": since, "detected_at": since})
    )
    s._guarded().write({"state": "silent"})
    s.ingest(1.0, since - timedelta(hours=2))
    assert gap.state == "closed" and gap.gap_to >= gap.gap_from


# ================================================================== M48-22
def test_m48_22_only_an_operator_proposes(c):
    p = prediction(c)
    assert refused(
        c.env,
        lambda: c.env["fix.iot.action"].with_user(c.clerk).create({"prediction_id": p.id}),
    )
    c.env["fix.iot.action"].with_user(c.operator).create({"prediction_id": p.id})


# ================================================================== M48-23
def test_m48_23_location_readings_are_for_the_iot_roles(c):
    env = c.env
    device = env["fix.iot.device"].create(
        {"name": f"E48 Trk {TAG}", "device_id": f"E48T-{TAG}", "equipment_id": c.equipment.id}
    )
    stream = env["fix.iot.stream"].create({"device_id": device.id, "metric": "gps_lat"})
    stream.action_activate()
    env["fix.iot.consent"].create(
        {
            "subject_type": "device",
            "device_id": device.id,
            "evidence_ref": "form",
            "granted_by": "driver",
            "signal_groups_permitted": "gps",
        }
    )
    reading, _a = stream.ingest(23.7)
    T = env["fix.iot.telemetry"]
    assert reading.sudo().is_location
    assert not T.with_user(c.clerk).search_count([("id", "=", reading.id)])
    assert T.with_user(c.operator).search_count([("id", "=", reading.id)]) == 1


# ================================================================== M48-10
def test_m48_10_escalation_follows_the_severity_sla(c):
    env = c.env
    env["ir.config_parameter"].sudo().set_param("cd_stream_registry.ack_sla_minutes_major", "30")
    c.device.sudo()._fix_mark_offline()
    alert = env["fix.iot.alert"].search([("device_id", "=", c.device.id)])
    assert alert.severity == "major"
    with freeze_time(datetime.utcnow() + timedelta(minutes=65)):
        assert env["fix.iot.alert"].cron_escalate() == 1
    assert alert.escalation_level == 2
    assert env["fix.event.outbox"].search_count(
        [("event_type", "=", "asset.alert_escalated"), ("aggregate_id", "=", alert.id)]
    )
    # no SLA set for minor: nothing escalates
    env["ir.config_parameter"].sudo().set_param("cd_stream_registry.ack_sla_minutes_major", "")
    with freeze_time(datetime.utcnow() + timedelta(days=2)):
        assert env["fix.iot.alert"].cron_escalate() == 0


def test_m48_10_horizon_sweep_flags_once(c):
    p = prediction(c, estimated_days_to_failure=1)
    p.sudo()._guarded().write({"last_evaluated": fields.Datetime.now() - timedelta(days=10)})
    Pred = c.env["fix.predictive.maintenance"]
    assert Pred.cron_horizon_sweep() >= 1 and p.horizon_flagged
    assert p.id not in Pred.search([("horizon_flagged", "=", False)]).ids


def test_m48_10_monthly_precision_and_suspension(c):
    env = c.env
    govern(env)
    env["ir.config_parameter"].sudo().set_param("cd_stream_registry.precision_threshold_pct", "70")
    Precision = env["fix.ml.m48.precision"]
    model = env["fix.ml.model"].search([("code", "=", MODEL)], limit=1)
    for month, recorded in (
        ("2026-09-15", "2026-09-10 06:00:00"),
        ("2026-10-15", "2026-10-10 06:00:00"),
    ):
        p = prediction(c, name=f"E48-P-{month}")
        p.sudo()._guarded().write({"outcome": "false_alarm", "outcome_recorded_on": recorded})
        Precision.cron_m48_precision(today=fields.Date.to_date(month) + timedelta(days=20))
    assert model.m48_customer_suspended
    assert env["fix.event.outbox"].search_count(
        [("event_type", "=", "telemetry.model_suspended"), ("aggregate_id", "=", model.id)]
    )
