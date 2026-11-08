"""A07 P1 (2026-11-04) M48: roles, the scheduler, ingestion controls, liveness
and alert dedup / cooldown / dwell.

Attackers are NON-ADMIN users created in the rolled-back transaction: a plain
internal user (base.group_user + an operating unit) and users holding exactly
the M48 role they would really hold. The superuser is trusted by the guards,
so it only builds fixtures and stands in for the gateway service and crons."""

from __future__ import annotations

import json
import types
import uuid
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

TAG = uuid.uuid4().hex[:6].upper()
REFUSED = (UserError, ValidationError, AccessError)
OPERATOR = "cd_stream_registry.group_iot_operator"
ADMIN = "cd_stream_registry.group_iot_admin"
MANAGER = "cd_stream_registry.group_iot_manager"
CONSENT = "cd_stream_registry.group_iot_consent_officer"
DWELL = "cd_stream_registry.rule_dwell_enforced"


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
        login = "a07p1m48_%d_%s" % (n["i"], TAG)
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
    x.operator = user(OPERATOR)
    x.admin = user(ADMIN)
    x.equipment = env["fix.equipment"].create(
        {"code": f"P1M48-EQ-{TAG}", "name": f"P1M48 Compressor {TAG}", "category": "Electrical"}
    )
    x.adapter = env["fix.iot.adapter"].create(
        {
            "name": f"P1M48 MQTT {TAG}",
            "protocol": "mqtt",
            "auth_mode": "token",
            # in service: born disabled, enabled by an administrator with a key
            "state": "enabled",
            "api_key_hash": "0" * 64,
        }
    )
    x.device = env["fix.iot.device"].create(
        {"name": f"P1M48 Dev {TAG}", "device_id": f"P1M48-{TAG}", "equipment_id": x.equipment.id}
    )
    x.stream = env["fix.iot.stream"].create(
        {
            "device_id": x.device.id,
            "adapter_id": x.adapter.id,
            "metric": "vibration",
            "unit": "mm/s",
            "sample_interval_sec": 60,
        }
    )
    x.stream.action_activate()
    return x


def rule(c, **kw):
    vals = {
        "stream_id": c.stream.id,
        "operator": "gt",
        "threshold": 5.0,
        "severity": "major",
        "cooldown_min": 15,
        "duration_min": 0,
    }
    vals.update(kw)
    return c.env["fix.iot.rule"].create(vals)


# ======================================================================= roles
def test_roles_exist_imply_each_other_and_admin_keeps_access(c):
    env = c.env
    op, adm, mgr, cons = (env.ref(x) for x in (OPERATOR, ADMIN, MANAGER, CONSENT))
    assert op in adm.implied_ids and adm in mgr.implied_ids
    # consent policy is separate from collection configuration (spec §13 SoD)
    assert cons not in mgr.all_implied_ids and adm not in cons.all_implied_ids
    admin = env.ref("base.user_admin")
    for group in (op, adm, mgr, cons):
        assert admin in group.all_user_ids
        assert group.privilege_id == env.ref("cd_stream_registry.privilege_iot")


def test_plain_user_reads_but_configures_nothing(c):
    env, clerk = c.env, c.clerk
    assert env["fix.iot.stream"].with_user(clerk).search_count([("id", "=", c.stream.id)]) == 1
    for model, vals in (
        ("fix.iot.stream", {"device_id": c.device.id, "metric": "temperature"}),
        ("fix.iot.adapter", {"name": "P1M48 rogue", "auth_mode": "token"}),
        ("fix.iot.rule", {"stream_id": c.stream.id, "threshold": 1.0}),
        ("fix.iot.device", {"name": "P1M48 rogue", "device_id": f"ROGUE-{TAG}"}),
    ):
        assert refused(env, lambda m=model, v=vals: env[m].with_user(clerk).create(v)), model
    assert refused(env, lambda: c.stream.with_user(clerk).write({"unit": "g"}))
    assert refused(env, lambda: c.stream.with_user(clerk).ingest(1.0))
    assert refused(env, lambda: c.stream.with_user(clerk).action_suspend())
    # the role holder does the same work
    s = (
        env["fix.iot.stream"]
        .with_user(c.admin)
        .create({"device_id": c.device.id, "metric": "temperature"})
    )
    s.with_user(c.admin).action_activate()
    reading, _ = s.with_user(c.admin).ingest(21.0)
    assert reading.value == 21.0


def test_alert_queue_is_the_operators(c):
    rule(c)
    _, alert = c.stream.ingest(9.0)
    assert refused(c.env, lambda: alert.with_user(c.clerk).action_ack())
    alert.with_user(c.operator).action_ack()
    alert.with_user(c.operator).action_resolve(resolution_note="bearing greased")
    assert (alert.state, alert.acked_by, alert.resolved_by) == (
        "resolved",
        c.operator,
        c.operator,
    )


# ======================================================================= crons
SCHEDULED = [
    ("fix.iot.stream", "cron_liveness"),
    ("fix.iot.consent", "cron_consent_expiry"),
    ("fix.iot.rule", "cron_lapse_suppressions"),
    ("fix.iot.downsample", "cron_retention"),
]


@pytest.mark.parametrize(("model", "method"), SCHEDULED)
def test_every_cron_method_has_an_active_job_that_runs(c, model, method):
    """A cron METHOD with no ir.cron record never runs in production (A03)."""
    env = c.env
    assert hasattr(env[model], method)
    jobs = env["ir.cron"].search([("model_id.model", "=", model), ("code", "like", method)])
    assert jobs and all(j.active for j in jobs), (model, method)
    getattr(env[model], method)()  # superuser-safe and idempotent
    getattr(env[model], method)()


# =================================================================== ingestion
def test_disabled_adapter_stops_ingest_for_everyone(c):
    c.adapter.with_user(c.clerk).action_disable(reason="broker compromised")
    assert (c.adapter.state, c.adapter.disabled_by) == ("disabled", c.clerk)
    with pytest.raises(UserError, match="disabled"), c.env.cr.savepoint():
        c.stream.ingest(1.0)  # even the superuser gateway
    # only the administrator turns it back on, and only with a credential and a key
    assert refused(c.env, lambda: c.adapter.with_user(c.clerk).action_enable())
    assert refused(c.env, lambda: c.adapter.with_user(c.admin).action_enable())
    c.adapter.with_user(c.admin).write({"credential_ref": "vault:iot/mqtt/p1m48"})
    c.adapter.with_user(c.admin).action_enable()
    c.stream.ingest(1.0)


def test_unauthenticated_adapter_and_secret_in_endpoint_refused(c):
    Adapter = c.env["fix.iot.adapter"].with_user(c.admin)
    # born disabled it harms nothing, but it can never be turned on
    opened = Adapter.create({"name": "open", "auth_mode": "none"})
    assert opened.state == "disabled"
    assert refused(c.env, lambda: opened.action_enable())
    assert refused(c.env, lambda: opened.sudo()._guarded().write({"state": "enabled"}))
    assert refused(
        c.env,
        lambda: Adapter.create({"name": "leaky", "endpoint": "mqtt://iot:s3cret@broker.test"}),
    )
    ok = Adapter.create({"name": "fine", "endpoint": "mqtts://broker.test:8883"})
    assert ok.state == "disabled", "born disabled: enabling needs a credential and a key"
    # a legacy enabled adapter with no authentication: ingest refuses it
    c.adapter._guarded().write({"state": "disabled"})
    c.env.flush_all()
    c.env.cr.execute("UPDATE fix_iot_adapter SET auth_mode='none' WHERE id=%s", [c.adapter.id])
    c.env.cr.execute("UPDATE fix_iot_adapter SET state='enabled' WHERE id=%s", [c.adapter.id])
    c.adapter.invalidate_recordset()
    with pytest.raises(UserError, match="unauthenticated"), c.env.cr.savepoint():
        c.stream.ingest(1.0)


def test_gateway_replay_is_deduplicated_server_stamped_repeats_are_not(c):
    ts = fields.Datetime.now() - timedelta(minutes=3)
    c.stream.ingest(1.0, timestamp=ts)
    with pytest.raises(ValidationError, match="Duplicate"), c.env.cr.savepoint():
        c.stream.ingest(1.0, timestamp=ts)
    for _ in range(3):  # three messages in the same second are three readings
        c.stream.ingest(1.0)
    n = c.env["fix.iot.telemetry"].search_count([("device_id", "=", c.device.id)])
    assert n == 4


def test_liveness_cannot_be_typed(c):
    d = c.env["fix.iot.device"].create(
        {"name": f"P1M48 Idle {TAG}", "device_id": f"IDLE-{TAG}", "status": "offline"}
    )
    for u in (c.clerk, c.admin):
        assert refused(c.env, lambda u=u: d.with_user(u).action_telemetry_received("online"))
        assert refused(
            c.env,
            lambda u=u: d.with_user(u).write(
                {"status": "online", "last_telemetry": fields.Datetime.now()}
            ),
        )
    d.invalidate_recordset()
    assert d.status == "offline" and not d.last_telemetry


# ==================================================================== liveness
def test_silent_stream_opens_a_gap_takes_the_device_offline_and_resumes(c):
    env = c.env
    old = fields.Datetime.now() - timedelta(hours=2)
    c.stream.ingest(2.0, timestamp=old)
    assert c.device.status == "online"
    env["fix.iot.stream"].cron_liveness()
    assert c.stream.state == "silent"
    gap = c.stream.gap_ids
    assert (gap.state, gap.gap_from, gap.cause, gap.had_reading) == (
        "open",
        old,
        "device_silent",
        True,
    )
    assert c.device.status == "offline" and c.device.last_telemetry == old
    offline = c.device.alert_ids.filtered(lambda a: "offline" in a.message)
    assert len(offline) == 1 and offline.severity == "major"
    (payload,) = events(env, "telemetry.stream_silent", c.stream.id)
    assert payload["gap"] == gap.name and payload["last_point"]
    # idempotent: a second run flags nothing again
    assert env["fix.iot.stream"].cron_liveness() == 0
    assert len(c.stream.gap_ids) == 1
    # gaps are platform records
    assert refused(env, lambda: gap.with_user(c.admin).write({"gap_to": fields.Datetime.now()}))
    assert refused(env, lambda: gap.with_user(c.admin).unlink())
    # the next reading resumes the stream and closes the gap permanently
    reading, _ = c.stream.with_user(c.admin).ingest(2.5)
    assert c.stream.state == "active" and c.device.status == "online"
    assert gap.state == "closed" and gap.gap_to == reading.timestamp and gap.points_expected > 0


def test_a_stream_that_never_reported_also_falls_silent(c):
    c.stream._guarded().write({"activated_on": fields.Datetime.now() - timedelta(hours=1)})
    c.env["fix.iot.stream"].cron_liveness()
    assert c.stream.state == "silent" and c.stream.gap_ids.had_reading is False


# ============================================================ alert dedup etc.
def test_repeated_breaches_raise_one_alert_counted_on_it(c):
    r = rule(c)
    total = 0
    for i in range(20):
        _, raised = c.stream.ingest(10.0 + i)
        total += len(raised)
    alert = c.env["fix.iot.alert"].search([("rule_id", "=", r.id)])
    assert total == 1 and len(alert) == 1
    assert (alert.occurrence_count, alert.trigger_value, alert.last_value) == (20, 10.0, 29.0)
    assert alert.stream_id == c.stream
    (payload,) = events(c.env, "iot.rule_alert_raised", alert.id)
    assert payload["rule"] == r.name and payload["trigger_value"] == 10.0
    assert payload["equipment_id"] == c.equipment.id


def test_cooldown_holds_a_new_alert_after_resolution(c):
    r = rule(c, cooldown_min=15)
    now = fields.Datetime.now()
    _, first = c.stream.ingest(9.0, timestamp=now - timedelta(minutes=30))
    first.with_user(c.operator).action_ack()
    first.with_user(c.operator).action_resolve(resolution_note="reset")
    _, held = c.stream.ingest(9.0, timestamp=now - timedelta(minutes=25))
    assert not held and r.cooldown_suppressed == 1
    _, again = c.stream.ingest(9.0, timestamp=now - timedelta(minutes=10))
    assert len(again) == 1 and again != first


def test_dwell_switch_holds_the_alert_until_the_breach_lasted(c):
    c.env["ir.config_parameter"].sudo().set_param(DWELL, "1")
    r = rule(c, duration_min=5)
    now = fields.Datetime.now()
    _, raised = c.stream.ingest(9.0, timestamp=now - timedelta(minutes=10))
    assert not raised and r.breach_since
    _, raised = c.stream.ingest(1.0, timestamp=now - timedelta(minutes=8))
    assert not raised and not r.breach_since  # the breach ended: clock reset
    _, raised = c.stream.ingest(9.0, timestamp=now - timedelta(minutes=7))
    assert not raised
    _, raised = c.stream.ingest(9.0, timestamp=now - timedelta(minutes=1))
    assert len(raised) == 1
    # switch off (the default): the first breach alerts at once
    c.env["ir.config_parameter"].sudo().set_param(DWELL, "0")
    r2 = rule(c, duration_min=5, threshold=50.0)
    _, raised = c.stream.ingest(60.0)
    assert len(raised) == 1 and raised.rule_id == r2


def test_evaluator_bookkeeping_is_guarded(c):
    r = rule(c)
    for vals in (
        {"last_alert_on": fields.Datetime.now()},
        {"breach_since": fields.Datetime.now()},
        {"cooldown_suppressed": 9},
    ):
        assert refused(c.env, lambda vals=vals: r.with_user(c.admin).write(vals)), vals
    _, alert = c.stream.ingest(9.0)
    assert refused(c.env, lambda: alert.with_user(c.operator).write({"occurrence_count": 5}))
