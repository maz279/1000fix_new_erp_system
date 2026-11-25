# cd_fixed_asset_ext tests — P08-M08 (CD-M49-01). DoD-03: depreciation.
#
# A08 M49-13: the source-grep "tests" (inspect.getsource) that certified the
# events and CWIP refusals by reading the code are gone; the behaviour is
# tested on the live ORM (test_fixed_asset_orm.py, test_a08_m49_controls.py).
import unittest
from decimal import Decimal

import pytest
from odoo.addons.cd_fixed_asset_ext.models.fix_fixed_asset import (
    FixFixedAsset,
    annual_wdv_month,
    reducing_balance_monthly,
    remaining_straight_line,
    straight_line_monthly,
)
from odoo.addons.cd_fixed_asset_ext.models.fix_lease import lease_present_value, lease_schedule

pytestmark = [pytest.mark.financial]  # depreciation is a DoD-03 money path


class TestStraightLineDepreciation(unittest.TestCase):
    """100% of the calculation path — it is a financial path (DoD-03)."""

    def test_even_division(self):
        self.assertEqual(
            straight_line_monthly(Decimal("120000"), Decimal("0"), 60), Decimal("2000.00")
        )

    def test_salvage_reduces_base(self):
        self.assertEqual(
            straight_line_monthly(Decimal("120000"), Decimal("20000"), 50), Decimal("2000.00")
        )

    def test_rounding_half_up(self):
        # (1000-0)/3 = 333.333... -> 333.33
        self.assertEqual(straight_line_monthly(Decimal("1000"), Decimal("0"), 3), Decimal("333.33"))
        # (1002-0)/3 = 334.0 exactly
        self.assertEqual(straight_line_monthly(Decimal("1002"), Decimal("0"), 3), Decimal("334.00"))

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


class TestRemainingLifeAndTaxBook(unittest.TestCase):
    def test_remaining_straight_line(self):
        self.assertEqual(remaining_straight_line(100000.0, 0.0, 50), 2000.0)
        self.assertEqual(remaining_straight_line(1000.0, 0.0, 3), 333.33)
        self.assertEqual(remaining_straight_line(333.34, 0.0, 1), 333.34)  # last month: remainder
        self.assertEqual(remaining_straight_line(500.0, 500.0, 5), 0.0)  # at salvage
        self.assertEqual(remaining_straight_line(500.0, 0.0, 0), 0.0)  # life exhausted

    def test_reducing_balance_monthly(self):
        self.assertEqual(reducing_balance_monthly(120000.0, 20.0), 2000.0)
        self.assertEqual(reducing_balance_monthly(0.0, 20.0), 0.0)
        self.assertEqual(reducing_balance_monthly(1000.0, 0.0), 0.0)


class TestLeaseMaths(unittest.TestCase):
    def test_present_value(self):
        # 12 x 1,000 in arrears at 1%/month: annuity factor 11.2551
        self.assertEqual(lease_present_value(1000.0, 12, 0.01, False), 11255.08)
        # in advance: x 1.01
        self.assertEqual(lease_present_value(1000.0, 12, 0.01, True), 11367.63)
        self.assertEqual(lease_present_value(1000.0, 12, 0.0, True), 12000.0)
        with self.assertRaises(ValueError):
            lease_present_value(1000.0, 0, 0.01, True)

    def test_schedule_unwinds_to_zero(self):
        for advance in (True, False):
            pv = lease_present_value(1000.0, 12, 0.01, advance)
            rows = lease_schedule(pv, 1000.0, 12, 0.01, advance)
            self.assertEqual(rows[-1]["closing"], 0.0)
            self.assertAlmostEqual(sum(r["principal"] for r in rows), pv, places=2)
            self.assertAlmostEqual(sum(r["interest"] for r in rows), 12000.0 - pv, places=2)
        arrears = lease_schedule(11255.08, 1000.0, 12, 0.01, False)
        self.assertEqual(arrears[0]["interest"], 112.55)


class TestM49M54Break(unittest.TestCase):
    """AR-006 4.1 pair 14: M54 consumes EVENTS; M49 never reads budgets."""

    def test_budget_field_is_advisory_char(self):
        import odoo.fields as f

        self.assertIsInstance(FixFixedAsset.budget_reference, f.Char)
        self.assertNotIsInstance(FixFixedAsset.budget_reference, f.Many2one)


class TestAnnualWrittenDownValue(unittest.TestCase):
    """A08 M49-8: the Third Schedule allowance is the opening annual WDV x
    rate (30,000 on 100,000 at 30%), not WDV x rate / 12 compounded monthly
    (26,200.16)."""

    def test_a_year_charges_the_annual_allowance(self):
        charged = 0.0
        for month in range(12):
            charged += annual_wdv_month(100000.0, 30.0, month, charged)
        self.assertEqual(round(charged, 2), 30000.0)

    def test_the_last_month_absorbs_rounding(self):
        charged = 0.0
        for month in range(11):
            charged += annual_wdv_month(1000.0, 10.0, month, charged)  # 8.33 each
        self.assertEqual(annual_wdv_month(1000.0, 10.0, 11, charged), round(100.0 - charged, 2))

    def test_nothing_on_a_nil_wdv_or_rate(self):
        self.assertEqual(annual_wdv_month(0.0, 30.0, 0, 0.0), 0.0)
        self.assertEqual(annual_wdv_month(1000.0, 0.0, 0, 0.0), 0.0)


if __name__ == "__main__":
    unittest.main()
