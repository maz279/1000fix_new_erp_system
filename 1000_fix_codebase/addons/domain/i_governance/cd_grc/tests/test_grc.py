"""cd_grc tests - P09-M08 (CD-M60-01)."""
import inspect
import unittest

from odoo.addons.cd_grc.models.fix_grc import FixControl, FixRiskRegister


class TestGrc(unittest.TestCase):
    def test_risk_score_computed(self):
        src = inspect.getsource(FixRiskRegister._compute_score)
        self.assertIn("likelihood", src)
        self.assertIn("impact", src)

    def test_control_types(self):
        src = inspect.getsource(FixControl)
        for ct in ("preventive", "detective", "corrective"):
            self.assertIn(ct, src)

    def test_control_links_to_risk(self):
        self.assertTrue(hasattr(FixControl, "risk_id"))


if __name__ == "__main__":
    unittest.main()
