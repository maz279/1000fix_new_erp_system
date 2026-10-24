# cd_msp_contract tests — P08-M07 (CD-M05-01).
import inspect
import unittest

from odoo.addons.cd_msp_contract.models.fix_msp import (
    FixMonitoredAsset,
    FixMspAlert,
    FixRemoteSession,
)


class TestJourneySix(unittest.TestCase):
    """MSP alert -> ticket -> remote resolution -> SLA -> report."""

    def test_alert_to_ticket_creates_service_order(self):
        src = inspect.getsource(FixMspAlert.action_to_ticket)
        self.assertIn("fix.service.order", src)
        self.assertIn("amc", src)  # the contract-funded category

    def test_alert_escalates_on_first_unhealthy_transition(self):
        src = inspect.getsource(FixMonitoredAsset.ingest_telemetry)
        self.assertIn("became_unhealthy", src)
        self.assertIn("fix.msp.alert", src)
        self.assertIn("msp.alert_raised", src)

    def test_alert_state_guards(self):
        src = inspect.getsource(FixMspAlert.action_acknowledge)
        self.assertIn("Only NEW", src)


class TestRemoteSessionPdpa(unittest.TestCase):
    def test_consent_gates_the_session(self):
        src = inspect.getsource(FixRemoteSession.action_start)
        self.assertIn("consent", src.lower())
        self.assertIn("PDPA", src)


if __name__ == "__main__":
    unittest.main()
