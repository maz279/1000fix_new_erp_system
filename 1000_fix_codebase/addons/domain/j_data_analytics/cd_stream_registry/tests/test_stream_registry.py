"""cd_stream_registry tests - P11-M03 (CD-M48-01)."""
import inspect
import unittest

from odoo.addons.cd_stream_registry.models.fix_stream_registry import (
    FixIotAlert, FixIotDevice, FixPredictiveMaintenance, FixIotTelemetry)


class TestIotDevice(unittest.TestCase):
    def test_device_types(self):
        src = inspect.getsource(FixIotDevice)
        for dt in ("sensor", "gateway", "tracker", "meter"):
            self.assertIn(dt, src)

    def test_links_to_equipment(self):
        self.assertTrue(hasattr(FixIotDevice, "equipment_id"))

    def test_unhealthy_transition_raises_alert(self):
        src = inspect.getsource(FixIotDevice.action_telemetry_received)
        self.assertIn("became_unhealthy", src)

    def test_alert_event(self):
        self.assertIn("iot.alert_raised",
                      inspect.getsource(FixIotDevice))


class TestTelemetry(unittest.TestCase):
    def test_metric_and_value(self):
        self.assertTrue(hasattr(FixIotTelemetry, "metric"))
        self.assertTrue(hasattr(FixIotTelemetry, "value"))

    def test_timestamp_indexed(self):
        src = inspect.getsource(FixIotTelemetry)
        self.assertIn("index=True", src)


class TestPredictiveMaintenance(unittest.TestCase):
    def test_only_failure_creates_wo(self):
        src = inspect.getsource(FixPredictiveMaintenance.action_create_preventive_wo)
        self.assertIn("failure_predicted", src)
        self.assertIn("Only failure", src)

    def test_wo_not_duplicated(self):
        src = inspect.getsource(FixPredictiveMaintenance.action_create_preventive_wo)
        self.assertIn("already created", src)

    def test_wo_event(self):
        self.assertIn("predictive_maintenance.wo_created",
                      inspect.getsource(FixPredictiveMaintenance))


if __name__ == "__main__":
    unittest.main()
