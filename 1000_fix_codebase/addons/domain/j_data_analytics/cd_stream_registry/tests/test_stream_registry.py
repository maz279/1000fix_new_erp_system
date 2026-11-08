"""cd_stream_registry tests - P11-M03 (CD-M48-01).

A07 P3 (2026-11-04): this file used to assert the SOURCE TEXT of the models
(`assertIn("iot.alert_raised", DEVICE_SRC)`), which stayed green whatever the
code did. Each claim it made is now exercised on the live ORM in a rolled-back
transaction: device types, the equipment link, the unhealthy-transition alert
and its event, the telemetry record, and the one-work-order rule."""

from __future__ import annotations

import json
import uuid
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError

TAG = uuid.uuid4().hex[:6].upper()
MODEL = "m26.predictive.maintenance"


def _events(env, event_type, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


@pytest.fixture
def equipment(odoo_env):
    return odoo_env["fix.equipment"].create(
        {"code": f"SR-EQ-{TAG}", "name": f"SR Chamber {TAG}", "category": "Electrical"}
    )


class TestIotDevice:
    @pytest.mark.parametrize("device_type", ["sensor", "gateway", "tracker", "meter"])
    def test_device_types(self, odoo_env, device_type):
        dev = odoo_env["fix.iot.device"].create(
            {
                "name": f"SR {device_type} {TAG}",
                "device_id": f"SR-{device_type}-{TAG}",
                "device_type": device_type,
            }
        )
        assert dev.device_type == device_type

    def test_links_to_equipment(self, odoo_env, equipment):
        dev = odoo_env["fix.iot.device"].create(
            {"name": f"SR Dev {TAG}", "device_id": f"SR-EQ-{TAG}", "equipment_id": equipment.id}
        )
        stream = odoo_env["fix.iot.stream"].create({"device_id": dev.id, "metric": "temperature"})
        assert stream.equipment_id == equipment and stream.company_id == dev.company_id

    def test_unhealthy_transition_raises_alert_and_event(self, odoo_env):
        dev = odoo_env["fix.iot.device"].create(
            {"name": f"SR Rack {TAG}", "device_id": f"SR-RACK-{TAG}"}
        )
        dev.action_telemetry_received("degraded")
        alert = dev.alert_ids
        assert (alert.severity, alert.state) == ("minor", "new")
        assert _events(odoo_env, "iot.alert_raised", alert.id) == [
            {"device": f"SR-RACK-{TAG}", "health": "degraded"}
        ]
        dev.action_telemetry_received("online")
        assert len(dev.alert_ids) == 1  # recovery raises nothing


class TestTelemetry:
    def test_metric_value_and_timestamp(self, odoo_env, equipment):
        dev = odoo_env["fix.iot.device"].create(
            {"name": f"SR T {TAG}", "device_id": f"SR-T-{TAG}", "equipment_id": equipment.id}
        )
        stream = odoo_env["fix.iot.stream"].create({"device_id": dev.id, "metric": "temperature"})
        stream.action_activate()
        reading, _alerts = stream.ingest(41.5)
        assert (reading.metric, reading.value, reading.device_id) == ("temperature", 41.5, dev)
        assert reading.timestamp <= fields.Datetime.now()
        # newest first, and searchable by time (the indexed column)
        older, _ = stream.ingest(40.0, timestamp=reading.timestamp - timedelta(hours=1))
        rows = odoo_env["fix.iot.telemetry"].search([("device_id", "=", dev.id)])
        assert rows.ids == [reading.id, older.id]
        assert odoo_env["fix.iot.telemetry"]._fields["timestamp"].index


class TestPredictiveMaintenance:
    def _pred(self, env, equipment, **kw):
        vals = {
            "name": f"SR PdM {TAG}",
            "equipment_id": equipment.id,
            "prediction": "failure_predicted",
            "estimated_days_to_failure": 5,
            "model_name": MODEL,
        }
        vals.update(kw)
        return env["fix.predictive.maintenance"].create(vals)

    def test_only_failure_creates_wo(self, odoo_env, equipment):
        healthy = self._pred(odoo_env, equipment, prediction="healthy")
        with pytest.raises(UserError, match="Only failure"), odoo_env.cr.savepoint():
            healthy.action_create_preventive_wo()
        assert not healthy.work_order_created

    def test_wo_not_duplicated_and_event(self, odoo_env, equipment):
        p = self._pred(odoo_env, equipment, confidence=0.8)
        p.action_create_preventive_wo()
        with pytest.raises(UserError, match="already requested"), odoo_env.cr.savepoint():
            p.action_create_preventive_wo()
        assert _events(odoo_env, "predictive_maintenance.wo_created", p.id) == [
            {"equipment": equipment.name, "days": 5}
        ]
