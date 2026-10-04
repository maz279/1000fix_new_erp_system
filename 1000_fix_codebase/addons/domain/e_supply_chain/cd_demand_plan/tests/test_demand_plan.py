"""cd_demand_plan tests - P09-M07 (CD-M43-01)."""
import inspect
import unittest

from odoo.addons.cd_demand_plan.models.fix_demand_plan import FixDemandPlan


class TestDemandPlan(unittest.TestCase):
    def test_recommended_computed(self):
        src = inspect.getsource(FixDemandPlan._compute_recommended)
        self.assertIn("forecast_quantity", src)
        self.assertIn("current_stock", src)

    def test_approval_requires_replenishment(self):
        src = inspect.getsource(FixDemandPlan.action_approve)
        self.assertIn("Nothing to replenish", src)

    def test_event_published(self):
        self.assertIn("demand_plan.approved",
                      inspect.getsource(FixDemandPlan))


if __name__ == "__main__":
    unittest.main()
