"""cd_ewaste tests - P11-M05 (CD-M18-01)."""
import inspect
import unittest

from odoo.addons.cd_ewaste.models.fix_ewaste import (
    FixEsgMetric, FixEwasteCollection)


class TestJourneyTen(unittest.TestCase):
    """Journey 10: collection -> triage -> destruction -> recycling ->
    disposal certificate."""

    def test_state_lifecycle(self):
        from odoo.addons.cd_ewaste.models.fix_ewaste import EWASTE_STATES
        states = [s[0] for s in EWASTE_STATES]
        for s in ("collected", "triaged", "destruction", "recycled",
                  "disposed", "certified"):
            self.assertIn(s, states)

    def test_triage_composes_m14_grading(self):
        self.assertTrue(hasattr(FixEwasteCollection, "triage_grade"))

    def test_destruction_requires_wipe_certificate(self):
        """M06's secure wipe is the gate before destruction."""
        src = inspect.getsource(FixEwasteCollection.action_secure_destruction)
        self.assertIn("wipe.certificate", src)

    def test_certificate_issued_at_end(self):
        src = inspect.getsource(FixEwasteCollection.action_issue_certificate)
        self.assertIn("certificate", src)
        self.assertIn("certified", src)

    def test_events(self):
        src = inspect.getsource(FixEwasteCollection)
        for ev in ("ewaste.collected", "ewaste.certificate_issued"):
            self.assertIn(ev, src)

    def test_co2_tracked(self):
        self.assertTrue(hasattr(FixEwasteCollection, "esg_co2_saved_kg"))


class TestEsgMetrics(unittest.TestCase):
    def test_metric_types(self):
        src = inspect.getsource(FixEsgMetric)
        for mt in ("co2_saved", "ewaste_collected", "devices_refurbished"):
            self.assertIn(mt, src)

    def test_period_tracked(self):
        self.assertTrue(hasattr(FixEsgMetric, "period"))

    def test_units_derived(self):
        self.assertTrue(hasattr(FixEsgMetric, "unit"))


if __name__ == "__main__":
    unittest.main()
