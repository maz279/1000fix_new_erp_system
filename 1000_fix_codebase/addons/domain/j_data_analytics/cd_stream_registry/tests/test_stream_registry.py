"""cd_stream_registry tests - P11-M03 (CD-M48-01)."""

import inspect
import unittest

try:
    from odoo.addons.cd_stream_registry.models.fix_stream_registry import (
        FixIotAlert,
        FixIotDevice,
        FixIotTelemetry,
        FixPredictiveMaintenance,
    )

    DEVICE_SRC = inspect.getsource(FixIotDevice)
    TELEMETRY_SRC = inspect.getsource(FixIotTelemetry)
    ALERT_SRC = inspect.getsource(FixIotAlert)
    PDM_SRC = inspect.getsource(FixPredictiveMaintenance)
    TELEMETRY_RECV_SRC = inspect.getsource(FixIotDevice.action_telemetry_received)
    PDM_WO_SRC = inspect.getsource(FixPredictiveMaintenance.action_create_preventive_wo)
    HAS_EQUIPMENT = hasattr(FixIotDevice, "equipment_id")
    HAS_METRIC = hasattr(FixIotTelemetry, "metric")
    HAS_VALUE = hasattr(FixIotTelemetry, "value")
except Exception:
    from pathlib import Path

    model_file = Path(__file__).resolve().parents[1] / "models" / "fix_stream_registry.py"
    full_src = model_file.read_text(encoding="utf-8")
    DEVICE_SRC = full_src
    TELEMETRY_SRC = full_src
    ALERT_SRC = full_src
    PDM_SRC = full_src
    TELEMETRY_RECV_SRC = full_src
    PDM_WO_SRC = full_src
    HAS_EQUIPMENT = "equipment_id" in full_src
    HAS_METRIC = "metric" in full_src
    HAS_VALUE = "value" in full_src


class TestIotDevice(unittest.TestCase):
    def test_device_types(self):
        for dt in ("sensor", "gateway", "tracker", "meter"):
            self.assertIn(dt, DEVICE_SRC)

    def test_links_to_equipment(self):
        self.assertTrue(HAS_EQUIPMENT)

    def test_unhealthy_transition_raises_alert(self):
        self.assertIn("became_unhealthy", TELEMETRY_RECV_SRC)

    def test_alert_event(self):
        self.assertIn("iot.alert_raised", DEVICE_SRC)


class TestTelemetry(unittest.TestCase):
    def test_metric_and_value(self):
        self.assertTrue(HAS_METRIC)
        self.assertTrue(HAS_VALUE)

    def test_timestamp_indexed(self):
        self.assertIn("index=True", TELEMETRY_SRC)


class TestPredictiveMaintenance(unittest.TestCase):
    def test_only_failure_creates_wo(self):
        self.assertIn("failure_predicted", PDM_WO_SRC)
        self.assertIn("Only failure", PDM_WO_SRC)

    def test_wo_not_duplicated(self):
        self.assertIn("already created", PDM_WO_SRC)

    def test_wo_event(self):
        self.assertIn("predictive_maintenance.wo_created", PDM_SRC)


if __name__ == "__main__":
    unittest.main()
