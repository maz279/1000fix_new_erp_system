"""cd_stream_registry ops behaviour (live ORM, rolled back): streams and rule
evaluation, adapters, downsampling, alert lifecycle, predictions and
prescriptive actions, consent, report packs and the KPI payload."""

from __future__ import annotations

import importlib
import uuid
from datetime import date, timedelta

import pytest
from odoo.exceptions import UserError
from psycopg2 import IntegrityError

TAG = uuid.uuid4().hex[:6].upper()
m48 = importlib.import_module("odoo.addons.cd_p03_portal.controllers.a07.m48")


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    equipment = env["fix.equipment"].create(
        {"code": f"IOT-EQ-{TAG}", "name": f"IoT Tester {TAG}", "category": "Electrical"}
    )
    adapter = env["fix.iot.adapter"].create(
        {
            "name": f"Adapter {TAG}",
            "protocol": "mqtt",
            "endpoint": "mqtt://broker.test",
            "auth_mode": "token",
            # in service: born disabled, enabled by an administrator with a key
            "state": "enabled",
            "api_key_hash": "0" * 64,
        }
    )
    device = env["fix.iot.device"].create(
        {
            "name": f"Device {TAG}",
            "device_id": f"DEV-{TAG}",
            "device_type": "sensor",
            "equipment_id": equipment.id,
            "status": "online",
        }
    )
    stream = env["fix.iot.stream"].create(
        {
            "device_id": device.id,
            "adapter_id": adapter.id,
            "metric": "vibration",
            "unit": "mm/s",
            "sample_interval_sec": 60,
            "state": "active",
        }
    )
    return {
        "env": env,
        "equipment": equipment,
        "adapter": adapter,
        "device": device,
        "stream": stream,
    }


def test_stream_sequence_and_interval_rule(ctx):
    env, stream = ctx["env"], ctx["stream"]
    assert stream.name.startswith("STRM/")
    with pytest.raises(UserError, match="active"), env.cr.savepoint():
        # an active stream cannot be activated again
        stream.action_activate()
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.iot.stream"].create(
            {"device_id": ctx["device"].id, "metric": "temp", "sample_interval_sec": 0}
        )


def test_rule_matching_and_ingest_raises_alert(ctx):
    env, stream = ctx["env"], ctx["stream"]
    rule = env["fix.iot.rule"].create(
        {"stream_id": stream.id, "operator": "gt", "threshold": 4.5, "severity": "major"}
    )
    assert rule.name.startswith("IRUL/")
    assert rule.matches(5.0) is True
    assert rule.matches(4.5) is False
    telemetry, alerts = stream.ingest(6.2)
    assert telemetry.metric == "vibration"
    assert telemetry.value == 6.2
    assert len(alerts) == 1
    assert alerts.severity == "major"
    assert alerts.name.startswith("IOT/")
    assert stream.last_seen >= telemetry.timestamp
    # A07 P0 recipe: pausing is a routed suppression (test_a07_p0_recipe_governance);
    # here the trusted superuser fixture pauses it to test evaluation only.
    rule.write({"state": "paused"})
    _, alerts2 = stream.ingest(7.0)
    assert len(alerts2) == 0


def test_ingest_requires_active_stream(ctx):
    env, stream = ctx["env"], ctx["stream"]
    stream.action_suspend()
    with pytest.raises(UserError, match="active"), env.cr.savepoint():
        stream.ingest(1.0)
    with pytest.raises(UserError, match="active"), env.cr.savepoint():
        stream.action_suspend()


def test_downsampling_interval_rule(ctx):
    env, stream = ctx["env"], ctx["stream"]
    policy = env["fix.iot.downsample"].create(
        {
            "stream_id": stream.id,
            "raw_interval_sec": 60,
            "target_interval_sec": 300,
            "aggregation": "avg",
        }
    )
    assert policy.name.startswith("IDSP/")
    policy.action_activate()
    assert policy.state == "active"
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.iot.downsample"].create(
            {"stream_id": stream.id, "raw_interval_sec": 300, "target_interval_sec": 60}
        )


def test_alert_lifecycle(ctx):
    env, device = ctx["env"], ctx["device"]
    alert = env["fix.iot.alert"].create(
        {"device_id": device.id, "severity": "minor", "message": "test alert"}
    )
    alert.action_ack()
    assert alert.state == "acked"
    assert alert.acked_on
    alert.action_resolve(resolution_note="sensor reseated")
    assert alert.state == "resolved"
    assert alert.resolved_on
    with pytest.raises(UserError, match="already resolved"), env.cr.savepoint():
        alert.action_resolve(resolution_note="again")


def test_prediction_creates_one_work_order(ctx):
    env, equipment = ctx["env"], ctx["equipment"]
    prediction = env["fix.predictive.maintenance"].create(
        {
            "name": f"PDM-{TAG}",
            "equipment_id": equipment.id,
            "prediction": "failure_predicted",
            "confidence": 0.8,
            "estimated_days_to_failure": 12,
            "outcome": "pending",
            # A07 P1 BRU-IOT-10: only a published M26 model's output is applied.
            "model_name": "m26.predictive.maintenance",
        }
    )
    assert prediction.name == f"PDM-{TAG}"
    # A07 ERP audit (2026-11-20) M48-03: the request is a prescriptive action the
    # Operations Director approves (someone must hold the role)
    director = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": f"PDM Director {TAG}",
                "login": f"pdm_director_{TAG}",
                "group_ids": [(6, 0, [env.ref("cd_facility.group_operations_director").id])],
            }
        )
    )
    assert director
    prediction.action_create_preventive_wo()
    assert prediction.work_order_created is True
    assert prediction.preventive_action_id.approval_state == "pending"
    with pytest.raises(UserError, match="already requested"), env.cr.savepoint():
        prediction.action_create_preventive_wo()
    healthy = env["fix.predictive.maintenance"].create(
        {"name": f"PDM-H-{TAG}", "equipment_id": equipment.id, "prediction": "healthy"}
    )
    with pytest.raises(UserError, match="Only failure"), env.cr.savepoint():
        healthy.action_create_preventive_wo()


def test_prescriptive_action_lifecycle(ctx):
    env, equipment = ctx["env"], ctx["equipment"]
    prediction = env["fix.predictive.maintenance"].create(
        {
            "name": f"PDM-A-{TAG}",
            "equipment_id": equipment.id,
            "prediction": "failure_predicted",
            "estimated_days_to_failure": 9,
            "model_name": "m26.predictive.maintenance",
        }
    )
    # A07 P0 recipe: dispatch needs a technician and done records an outcome.
    technician = env["hr.employee"].create({"name": f"Tech {TAG}"})
    action = env["fix.iot.action"].create(
        {"prediction_id": prediction.id, "action_type": "inspect", "technician_id": technician.id}
    )
    assert action.name.startswith("IACT/")
    action.action_approve()
    action.action_dispatch()
    action.outcome_evidence_ref = "JC-OPS-1"  # A07 P1: completion needs evidence
    # A07 ERP audit (2026-11-20) M48-08: the order raised at dispatch comes first;
    # here its demand waits for a site and is settled under the job card
    demand = env["fix.maintenance.demand"].search([("iot_action_id", "=", action.id)])
    with pytest.raises(UserError, match="no order yet"), env.cr.savepoint():
        action.action_done(outcome="confirmed", note="worn bearing")
    demand.action_dismiss("done under job card JC-OPS-1")
    action.action_done(outcome="confirmed", note="worn bearing")
    assert action.state == "done"
    assert prediction.outcome == "confirmed"
    with pytest.raises(UserError, match="dispatched"), env.cr.savepoint():
        action.action_done(outcome="confirmed", note="again")


def test_consent_revoke(ctx):
    env, device = ctx["env"], ctx["device"]
    consent = env["fix.iot.consent"].create(
        {
            "subject_type": "device",
            "device_id": device.id,
            "purpose": "service",
            "valid_to": date.today() + timedelta(days=365),
        }
    )
    assert consent.name.startswith("ICNS/")
    consent.action_revoke()
    assert consent.state == "revoked"
    with pytest.raises(UserError, match="active"), env.cr.savepoint():
        consent.action_revoke()


def test_report_packs_and_kpis(ctx):
    env, adapter, device, stream = ctx["env"], ctx["adapter"], ctx["device"], ctx["stream"]
    env["fix.iot.rule"].create(
        {"stream_id": stream.id, "operator": "gt", "threshold": 1.0, "severity": "major"}
    )
    stream.ingest(2.0)
    quality = m48.stream_quality(env)
    assert any(r["device"] == device.name for r in quality["rows"])
    coverage = m48.telemetry_coverage(env)
    assert any(r["device"] == device.name for r in coverage["rows"])
    health = m48.asset_health(env)
    row = next(r for r in health["rows"] if r["device"] == device.name)
    # A07 ERP audit (2026-11-20) M48-13: the pack shows the STORED index
    assert row["band"] == "Not scored" and row["score"] == "—"
    env["fix.iot.health"]._fix_score(device)
    row = next(r for r in m48.asset_health(env)["rows"] if r["device"] == device.name)
    assert 0 <= row["score"] <= 100 and "open alert" in row["factors"]
    pipeline = m48.pipeline_health(env)
    assert any(r["adapter"] == adapter.name for r in pipeline["rows"])
    storm = m48.alert_storm(env)
    assert any(r["device"] == device.name for r in storm["rows"])
    payload = m48.kpis(env)
    assert payload["streams_ingesting"] >= 1
    assert payload["open_alerts"] >= 1
    assert payload["ingest_rate_per_hour"] >= 0
