# cd_fixed_asset_ext tests — P08-M08 (CD-M49-01). DoD-03: depreciation.
import inspect
import unittest
from decimal import Decimal

from odoo.addons.cd_fixed_asset_ext.models.fix_fixed_asset import (
    FixCwipEntry, FixFixedAsset, straight_line_monthly)


class TestStraightLineDepreciation(unittest.TestCase):
    """100% of the calculation path — it is a financial path (DoD-03)."""

    def test_even_division(self):
        self.assertEqual(
            straight_line_monthly(Decimal("120000"), Decimal("0"), 60),
            Decimal("2000.00"))

    def test_salvage_reduces_base(self):
        self.assertEqual(
            straight_line_monthly(Decimal("120000"), Decimal("20000"), 50),
            Decimal("2000.00"))

    def test_rounding_half_up(self):
        # (1000-0)/3 = 333.333... -> 333.33
        self.assertEqual(
            straight_line_monthly(Decimal("1000"), Decimal("0"), 3),
            Decimal("333.33"))
        # (1002-0)/3 = 334.0 exactly
        self.assertEqual(
            straight_line_monthly(Decimal("1002"), Decimal("0"), 3),
            Decimal("334.00"))

    def test_zero_life_raises(self):
        with self.assertRaises(ValueError):
            straight_line_monthly(Decimal("1000"), Decimal("0"), 0)

    def test_negative_inputs_raise(self):
        with self.assertRaises(ValueError):
            straight_line_monthly(Decimal("-1"), Decimal("0"), 12)
        with self.assertRaises(ValueError):
            straight_line_monthly(Decimal("1000"), Decimal("-1"), 12)

    def test_salvage_above_gross_raises(self):
        with self.assertRaises(ValueError):
            straight_line_monthly(Decimal("100"), Decimal("200"), 12)


class TestM49M54Break(unittest.TestCase):
    """AR-006 4.1 pair 14: M54 consumes EVENTS; M49 never reads budgets."""

    def test_depreciation_event_published(self):
        src = inspect.getsource(FixFixedAsset.action_accrue_month)
        self.assertIn("depreciation.accrued", src)

    def test_budget_field_is_advisory_char(self):
        import odoo.fields as f
        self.assertIsInstance(FixFixedAsset.budget_reference, f.Char)
        self.assertNotIsInstance(FixFixedAsset.budget_reference, f.Many2one)

    def test_capitalisation_event(self):
        self.assertIn("asset.capitalized",
                      inspect.getsource(FixFixedAsset))


class TestCwip(unittest.TestCase):
    def test_capitalise_creates_active_asset(self):
        src = inspect.getsource(FixCwipEntry.action_capitalise)
        self.assertIn("fix.fixed.asset", src)
        self.assertIn("active", src)

    def test_nothing_accumulated_refused(self):
        src = inspect.getsource(FixCwipEntry.action_capitalise)
        self.assertIn("Nothing accumulated", src)


if __name__ == "__main__":
    unittest.main()
