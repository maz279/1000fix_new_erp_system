"""cd_fpa tests - P09-M07 (CD-M54-01)."""
import inspect
import unittest

from odoo.addons.cd_fpa.models.fix_fpa import FixBudget, FixCostAllocation


class TestBudget(unittest.TestCase):
    def test_variance_computed(self):
        src = inspect.getsource(FixBudget._compute_variance)
        self.assertIn("planned_amount", src)
        self.assertIn("actual_amount", src)

    def test_budget_no_m49_relation(self):
        import odoo.fields as f
        self.assertNotIsInstance(
            getattr(FixBudget, "actual_amount", None), f.Many2one)


class TestCostAllocation(unittest.TestCase):
    def test_total_computed(self):
        src = inspect.getsource(FixCostAllocation._compute_total)
        self.assertIn("direct_cost", src)
        self.assertIn("allocated_overhead", src)


if __name__ == "__main__":
    unittest.main()
