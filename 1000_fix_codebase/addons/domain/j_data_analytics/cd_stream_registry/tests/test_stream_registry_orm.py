# cd_stream_registry live-ORM tests — P11-M03 (CD-M48-01): IoT health
# transitions, alerting and predictive-maintenance work orders.
import json

import pytest
from odoo.exceptions import UserError


def _events(env, event_type, aggregate, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", aggregate),
            ("aggregate_id", "=", aggregate_id),
        ],
        order="id",
    )
    return [json.loads(r.payload) for r in rows]


@pytest.fixture
def device(odoo_env):
    return odoo_env["fix.iot.device"].create(
        {"name": "Burn-in rack 3", "device_id": "IOT-BR-003", "device_type": "sensor"}
    )


def test_unhealthy_transitions_raise_alerts(odoo_env, device):
    assert device.status == "online"
    device.action_telemetry_received("degraded")
    assert device.status == "degraded"
    assert device.last_telemetry
    alert = device.alert_ids
    assert (alert.severity, alert.message, alert.state) == (
        "minor",
        "Burn-in rack 3 became degraded",
        "new",
    )
    assert alert.name == "IOT/New"  # no sequence configured for the code
    # the event names the ALERT as its aggregate (regression: was the device id)
    assert _events(odoo_env, "iot.alert_raised", "fix.iot.alert", alert.id) == [
        {"device": "IOT-BR-003", "health": "degraded"}
    ]
    # degraded -> offline is not a new online->unhealthy transition: no alert
    device.action_telemetry_received("offline")
    assert device.status == "offline"
    assert len(device.alert_ids) == 1
    # recovery raises nothing; the next outage straight to offline is major
    device.action_telemetry_received("online")
    assert len(device.alert_ids) == 1
    device.action_telemetry_received("offline")
    major = device.alert_ids - alert
    assert (major.severity, major.message) == ("major", "Burn-in rack 3 became offline")


def test_online_heartbeat_raises_nothing(device):
    device.action_telemetry_received("online")
    assert device.status == "online"
    assert not device.alert_ids


def test_alert_reference_from_sequence(odoo_env, device):
    odoo_env["ir.sequence"].create(
        {"name": "IoT alerts", "code": "fix.iot.alert", "prefix": "IOT/", "padding": 5}
    )
    alert = odoo_env["fix.iot.alert"].create({"device_id": device.id, "message": "Probe"})
    assert alert.name == "IOT/00001"


def test_telemetry_record(odoo_env, device):
    point = odoo_env["fix.iot.telemetry"].create(
        {"device_id": device.id, "metric": "temperature", "value": 41.5, "unit": "C"}
    )
    assert point.timestamp
    assert device.alert_ids.ids == []


def test_preventive_work_order_only_for_predicted_failures(odoo_env):
    equipment = odoo_env["fix.equipment"].create({"code": "EQ-OSC-01", "name": "Oscilloscope"})
    Prediction = odoo_env["fix.predictive.maintenance"]
    healthy = Prediction.create({"name": "PdM healthy", "equipment_id": equipment.id})
    with (
        pytest.raises(UserError, match="Only failure predictions create preventive work orders"),
        odoo_env.cr.savepoint(),
    ):
        healthy.action_create_preventive_wo()
    assert healthy.work_order_created is False
    failing = Prediction.create(
        {
            "name": "PdM failure",
            "equipment_id": equipment.id,
            "prediction": "failure_predicted",
            "confidence": 0.92,
            "estimated_days_to_failure": 6,
        }
    )
    failing.action_create_preventive_wo()
    assert failing.work_order_created is True
    assert _events(
        odoo_env, "predictive_maintenance.wo_created", "fix.predictive.maintenance", failing.id
    ) == [{"equipment": "Oscilloscope", "days": 6}]
    with pytest.raises(UserError, match="Work order already created"), odoo_env.cr.savepoint():
        failing.action_create_preventive_wo()
