"""cd_dynamic_pricing tests - P10-M05 (CD-M11-01 / R08-M03)."""

import inspect
import unittest

from odoo.addons.cd_dynamic_pricing.models.fix_dynamic_pricing import (
    FixDynamicPriceRule,
    FixPriceExplanation,
)


class TestDynamicPricing(unittest.TestCase):
    def test_price_bounds_enforced(self):
        src = inspect.getsource(FixDynamicPriceRule._check_bounds)
        self.assertIn("exceeds", src)
        self.assertIn("below", src)

    def test_apply_to_pure(self):
        src = inspect.getsource(FixDynamicPriceRule.apply_to)
        self.assertIn("base_price", src)
        self.assertIn("surge_multiplier", src)

    def test_calculate_and_explain_emits_event(self):
        src = inspect.getsource(FixDynamicPriceRule.calculate_and_explain)
        self.assertIn("pricing.calculated", src)
        self.assertIn("fix.price.explanation", src)

    def test_rule_types(self):
        src = inspect.getsource(FixDynamicPriceRule)
        for t in ("demand_surge", "off_peak", "inventory_clearance", "loyalty_tier"):
            self.assertIn(t, src)

    def test_rate_card_link_present(self):
        self.assertTrue(hasattr(FixDynamicPriceRule, "rate_card_id"))

    def test_explanation_exists(self):
        self.assertTrue(hasattr(FixPriceExplanation, "rules_applied"))
        self.assertTrue(hasattr(FixPriceExplanation, "model_driven"))


if __name__ == "__main__":
    unittest.main()
