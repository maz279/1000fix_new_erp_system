"""cd_dynamic_pricing tests - P10-M05 (CD-M11-01)."""
import inspect
import unittest

from odoo.addons.cd_dynamic_pricing.models.fix_dynamic_pricing import (
    FixDynamicPriceRule, FixPriceExplanation)


class TestDynamicPricing(unittest.TestCase):
    def test_price_bounds_enforced(self):
        src = inspect.getsource(FixDynamicPriceRule._check_bounds)
        self.assertIn("exceeds", src)
        self.assertIn("below", src)

    def test_apply_to_pure(self):
        src = inspect.getsource(FixDynamicPriceRule.apply_to)
        self.assertIn("base_price", src)

    def test_explanation_exists(self):
        self.assertTrue(hasattr(FixPriceExplanation, "rules_applied"))


if __name__ == "__main__":
    unittest.main()
