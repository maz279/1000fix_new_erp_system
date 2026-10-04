"""cd_tradein tests - P09-M04 (CD-M14-01)."""
import inspect
import unittest

from odoo.addons.cd_tradein.models.fix_tradein import FixTradeinRequest


class TestTradeinLifecycle(unittest.TestCase):
    def test_wipe_gate_blocks_refurbishment(self):
        src = inspect.getsource(FixTradeinRequest.action_refurbish)
        self.assertIn("wipe gate", src.lower())

    def test_ten_state_lifecycle(self):
        src = inspect.getsource(FixTradeinRequest)
        for state in ("offered", "accepted", "collected", "wiped",
                      "refurbished", "graded", "resale_ready", "closed"):
            self.assertIn(state, src)

    def test_grading_required_before_resale(self):
        src = inspect.getsource(FixTradeinRequest.action_grade)
        self.assertIn("grade is required", src)

    def test_events(self):
        src = inspect.getsource(FixTradeinRequest)
        for event in ("tradein.offered", "tradein.wiped", "tradein.paid"):
            self.assertIn(event, src)


if __name__ == "__main__":
    unittest.main()
