"""payroll-engine tests — P08-M03 (CD-M56-01).

DoD-03: 100% of every payroll calculation path, and negative tests. The
kernel is the ONLY calculation authority for M56 — these tests pin each
statutory number (FY 2026-27 slabs, Labour (Amendment) Act 2026 gratuity
and resignation bands, PF structure, BEFTN batch calendar).
"""
from __future__ import annotations

import sys
import unittest
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import pytest

pytestmark = [pytest.mark.financial, pytest.mark.tax]

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # codebase root (libs.py.*)

from libs.py.payroll_engine import (  # noqa: E402
    PayslipInput, beftn_settlement_date, completed_years, compute_payslip,
    gratuity, income_tax, is_working_day, overtime_amount, provident_fund,
    q2, resignation_compensation)  # noqa


class TestIncomeTaxFY202627(unittest.TestCase):
    """The slab table exactly as enacted in the June 2026 budget."""

    def test_below_threshold_is_zero(self):
        self.assertEqual(income_tax(Decimal("375000")), Decimal("0.00"))
        self.assertEqual(income_tax(Decimal("0")), Decimal("0.00"))

    def test_first_band_10_percent(self):
        # 375k tax-free + 300k @10% = 30,000 at 675k
        self.assertEqual(income_tax(Decimal("675000")), Decimal("30000.00"))

    def test_second_band_15_percent(self):
        # 30,000 + 400k@15% = 90,000 at 1,075,000
        self.assertEqual(income_tax(Decimal("1075000")), Decimal("90000.00"))

    def test_third_band_20_percent(self):
        # 90,000 + 500k@20% = 190,000 at 1,575,000
        self.assertEqual(income_tax(Decimal("1575000")), Decimal("190000.00"))

    def test_fourth_band_25_percent(self):
        # 190,000 + 2,000k@25% = 690,000 at 3,575,000
        self.assertEqual(income_tax(Decimal("3575000")), Decimal("690000.00"))

    def test_top_band_30_percent_on_balance(self):
        # 690,000 + 1,000k@30% = 990,000 at 4,575,000
        self.assertEqual(income_tax(Decimal("4575000")), Decimal("990000.00"))

    def test_mid_band_boundaries_round_half_up(self):
        # 500k taxable: 125k@10% = 12,500 exactly
        self.assertEqual(income_tax(Decimal("500000")), Decimal("12500.00"))

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            income_tax(Decimal("-1"))


class TestProvidentFund(unittest.TestCase):
    def test_both_wings(self):
        pf = provident_fund(Decimal("30000"), Decimal("10"), Decimal("10"))
        self.assertEqual(pf["employee"], Decimal("3000.00"))
        self.assertEqual(pf["employer"], Decimal("3000.00"))

    def test_asymmetric_structure(self):
        pf = provident_fund(Decimal("40000"), Decimal("7.5"), Decimal("7.5"))
        self.assertEqual(pf["employee"], Decimal("3000.00"))

    def test_negative_pct_raises(self):
        with self.assertRaises(ValueError):
            provident_fund(Decimal("100"), Decimal("-1"), Decimal("0"))


class TestServiceYears(unittest.TestCase):
    def test_completed_years_partial_does_not_count(self):
        self.assertEqual(completed_years(date(2020, 6, 15), date(2026, 6, 14)), 5)
        self.assertEqual(completed_years(date(2020, 6, 15), date(2026, 6, 15)), 6)

    def test_reversed_dates_raise(self):
        with self.assertRaises(ValueError):
            completed_years(date(2026, 1, 1), date(2020, 1, 1))


class TestGratuityAct2026(unittest.TestCase):
    """30 days' basic per completed year to 12 years, 45 above."""

    def test_under_12_years(self):
        # 10 years x 30 days x (30000/30) = 10 x 30000 = 300,000
        g = gratuity(Decimal("30000"), date(2016, 1, 1), date(2026, 1, 1))
        self.assertEqual(g, Decimal("300000.00"))

    def test_band_jump_above_12(self):
        # 12y @30 + 3y @45, basic 30,000 (daily 1,000): 360,000 + 135,000
        g = gratuity(Decimal("30000"), date(2011, 1, 1), date(2026, 1, 1))
        self.assertEqual(g, Decimal("495000.00"))

    def test_less_than_a_year_is_zero(self):
        g = gratuity(Decimal("30000"), date(2025, 6, 1), date(2026, 1, 1))
        self.assertEqual(g, Decimal("0.00"))


class TestResignationCompensation(unittest.TestCase):
    def test_band_below_5_years_7_days(self):
        # 3 years x 7 days x daily(1000) = 21,000
        c = resignation_compensation(
            Decimal("30000"), date(2023, 1, 1), date(2026, 1, 1))
        self.assertEqual(c, Decimal("21000.00"))

    def test_band_5_to_9_15_days(self):
        # 7 years x 15 x 1000 = 105,000
        c = resignation_compensation(
            Decimal("30000"), date(2019, 1, 1), date(2026, 1, 1))
        self.assertEqual(c, Decimal("105000.00"))

    def test_band_10_plus_30_days(self):
        # 12 years x 30 x 1000 = 360,000
        c = resignation_compensation(
            Decimal("30000"), date(2014, 1, 1), date(2026, 1, 1))
        self.assertEqual(c, Decimal("360000.00"))


class TestOvertime(unittest.TestCase):
    def test_double_rate(self):
        # hourly = 30000/30/8 = 125; OT 10h -> 125*2*10 = 2,500
        self.assertEqual(overtime_amount(Decimal("30000"), Decimal("10")),
                         Decimal("2500.00"))

    def test_zero_hours(self):
        self.assertEqual(overtime_amount(Decimal("30000"), Decimal("0")),
                         Decimal("0.00"))

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            overtime_amount(Decimal("30000"), Decimal("-1"))


class TestBeftnBatchCalendar(unittest.TestCase):
    """INT-005: cut-off 16:00; Fri/Sat/holiday roll to the next working day."""

    def test_before_cutoff_on_working_day_same_day(self):
        # 2026-10-01 is a Thursday
        self.assertEqual(
            beftn_settlement_date(datetime(2026, 10, 1, 10, 0)),
            date(2026, 10, 1))

    def test_after_cutoff_rolls_next_working_day(self):
        # 2026-10-01 is a Thursday; 16:30 is past the cut-off, the next day
        # (Friday) is a weekend day -> settles Sunday 2026-10-04
        self.assertEqual(
            beftn_settlement_date(datetime(2026, 10, 1, 16, 30)),
            date(2026, 10, 4))

    def test_after_cutoff_wednesday_rolls_thursday(self):
        self.assertEqual(
            beftn_settlement_date(datetime(2026, 9, 30, 17, 0)),
            date(2026, 10, 1))

    def test_friday_rolls_to_sunday(self):
        # 2026-10-02 Friday -> settles Sunday 2026-10-04
        self.assertEqual(
            beftn_settlement_date(datetime(2026, 10, 2, 10, 0)),
            date(2026, 10, 4))

    def test_saturday_rolls_to_sunday(self):
        self.assertEqual(
            beftn_settlement_date(datetime(2026, 10, 3, 11, 0)),
            date(2026, 10, 4))

    def test_fixed_holiday_rolls(self):
        # 2026-12-16 Victory Day (Wednesday) -> Thursday 17th
        self.assertEqual(
            beftn_settlement_date(datetime(2026, 12, 16, 9, 0)),
            date(2026, 12, 17))

    def test_extra_holiday_respected(self):
        self.assertEqual(
            beftn_settlement_date(datetime(2026, 10, 7, 9, 0),
                                  extra_holidays={date(2026, 10, 7)}),
            date(2026, 10, 8))

    def test_is_working_day_weekend(self):
        self.assertFalse(is_working_day(date(2026, 10, 2)))  # Friday
        self.assertFalse(is_working_day(date(2026, 10, 3)))  # Saturday
        self.assertTrue(is_working_day(date(2026, 10, 4)))   # Sunday


class TestPayslipPath(unittest.TestCase):
    """The monthly calculation path end to end (Journey 13's core)."""

    def test_full_slip(self):
        slip = compute_payslip(PayslipInput(
            employee_ref="E-001", basic_monthly=Decimal("30000"),
            ot_hours=Decimal("10"), incentive=Decimal("1500"),
            pf_employee_pct=Decimal("10"), pf_employer_pct=Decimal("10")))
        self.assertEqual(slip.overtime, Decimal("2500.00"))
        self.assertEqual(slip.gross, Decimal("34000.00"))
        self.assertEqual(slip.pf_employee, Decimal("3000.00"))
        self.assertEqual(slip.pf_employer, Decimal("3000.00"))
        # annualised taxable: (34000-3000)*12 = 372,000 -> below 375k: no tax
        self.assertEqual(slip.tax_month, Decimal("0.00"))
        self.assertEqual(slip.net, Decimal("31000.00"))
        # net equals gross - pf - tax, and lines reconcile to net
        self.assertEqual(sum(l for _, l in slip.lines), slip.net)

    def test_tax_kicks_in_above_threshold(self):
        slip = compute_payslip(PayslipInput(
            employee_ref="E-002", basic_monthly=Decimal("60000"),
            pf_employee_pct=Decimal("10")))
        # taxable annual = (60000-6000)*12 = 648,000 -> tax = 27,300/yr = 2,275/mo
        self.assertEqual(slip.tax_annual_projection, Decimal("27300.00"))
        self.assertEqual(slip.tax_month, Decimal("2275.00"))
        self.assertEqual(slip.net, Decimal("51725.00"))

    def test_ytd_other_income_is_taxed(self):
        slip = compute_payslip(PayslipInput(
            employee_ref="E-003", basic_monthly=Decimal("30000"),
            annual_taxable_other=Decimal("300000")))
        # annual = 30000*12 + 300000 = 660,000 -> 28,500/yr
        self.assertEqual(slip.tax_annual_projection, Decimal("28500.00"))

    def test_negative_basic_raises(self):
        with self.assertRaises(ValueError):
            compute_payslip(PayslipInput("E", Decimal("-5")))


if __name__ == "__main__":
    unittest.main()
