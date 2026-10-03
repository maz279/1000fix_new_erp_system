"""return_logic tests — P07-M04-T08 (DoD-03: 100% of return-calc paths).

Statutory correctness: holiday rollover, nil returns, TDS quarter mapping
against the BD fiscal year, BIN validation.
"""
from __future__ import annotations

import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))

from return_logic import (  # noqa: E402
    ReturnError,
    next_working_day,
    prepare_tds_return,
    prepare_vat_return,
    tds_quarter_for_date,
    tds_return_due_date,
    vat_return_due_date,
)

D = Decimal


class TestHolidayRollover(unittest.TestCase):
    def test_weekend_friday_rolls_to_sunday(self):
        # 2026-01-16 is a Friday -> rolls to Saturday -> Sunday 18th
        self.assertEqual(next_working_day(date(2026, 1, 16), set()), date(2026, 1, 18))

    def test_saturday_rolls_to_sunday(self):
        self.assertEqual(next_working_day(date(2026, 1, 17), set()), date(2026, 1, 18))

    def test_working_day_unchanged(self):
        self.assertEqual(next_working_day(date(2026, 1, 19), set()), date(2026, 1, 19))  # Mon

    def test_extra_holiday_rolls(self):
        # Monday 2026-10-19 declared a holiday -> Tuesday
        self.assertEqual(next_working_day(date(2026, 10, 19), {date(2026, 10, 19)}),
                         date(2026, 10, 20))

    def test_fixed_holiday_16_december(self):
        self.assertEqual(next_working_day(date(2026, 12, 16), set()), date(2026, 12, 17))


class TestVatReturnDueDate(unittest.TestCase):
    def test_normal_fifteenth(self):
        # 2026-11-15 is a Sunday
        self.assertEqual(vat_return_due_date("2026-10"), date(2026, 11, 15))

    def test_fifteenth_on_weekend_rolls(self):
        # Period 2026-02 -> due 2026-03-15: Sunday, a WORKING day in BD
        # (weekend is Fri+Sat) -> stays
        self.assertEqual(vat_return_due_date("2026-02"), date(2026, 3, 15))
        # Period 2026-12 -> due 2027-01-15: a FRIDAY -> rolls Sat -> Sun 17th
        self.assertEqual(vat_return_due_date("2026-12"), date(2027, 1, 17))

    def test_december_period_rolls_year(self):
        # Period 2026-11 -> due 2026-12-15: Tuesday -> stays
        self.assertEqual(vat_return_due_date("2026-11"), date(2026, 12, 15))


class TestPrepareVatReturn(unittest.TestCase):
    def test_full_return(self):
        ret = prepare_vat_return(
            "1234567890123", "2026-10",
            {"standard_15": (D("100000"), D("15000")), "zero_rated": (D("5000"), D("0"))},
            input_vat=D("3000"))
        self.assertFalse(ret.nil_return)
        self.assertEqual(ret.total_taxable, D("105000.00"))
        self.assertEqual(ret.total_output_vat, D("15000.00"))
        self.assertEqual(ret.net_payable, D("12000.00"))

    def test_nil_return_mandatory(self):
        """A period with no transactions still returns a return."""
        ret = prepare_vat_return("1234567890123", "2026-10", {})
        self.assertTrue(ret.nil_return)
        self.assertEqual(ret.net_payable, D("0.00"))

    def test_input_vat_exceeds_output(self):
        ret = prepare_vat_return("1234567890123", "2026-10",
                                 {"standard_15": (D("1000"), D("150"))},
                                 input_vat=D("300"))
        self.assertEqual(ret.net_payable, D("-150.00"))  # refund position

    def test_bad_bin_refused(self):
        with self.assertRaises(ReturnError):
            prepare_vat_return("12345", "2026-10", {})

    def test_lines_quantised(self):
        ret = prepare_vat_return("1234567890123", "2026-10",
                                 {"standard_15": (D("99.999"), D("15"))})
        self.assertEqual(ret.lines[0].taxable_value, D("100.00"))


class TestTdsQuarters(unittest.TestCase):
    def test_july_is_q1_fy2027(self):
        quarter, fy = tds_quarter_for_date(date(2026, 7, 15))
        self.assertEqual(quarter, "2026-Q1")
        self.assertEqual(fy, "FY2027")

    def test_june_is_q4_fy2027(self):
        quarter, fy = tds_quarter_for_date(date(2027, 6, 30))
        self.assertEqual(quarter, "2026-Q4")
        self.assertEqual(fy, "FY2027")

    def test_january_is_q3(self):
        quarter, fy = tds_quarter_for_date(date(2027, 1, 15))
        self.assertEqual(quarter, "2026-Q3")

    def test_october_is_q2(self):
        quarter, fy = tds_quarter_for_date(date(2026, 10, 2))
        self.assertEqual(quarter, "2026-Q2")


class TestTdsDueDates(unittest.TestCase):
    def test_four_statutory_dates(self):
        self.assertEqual(tds_return_due_date("2026-Q1"), date(2026, 10, 25))
        self.assertEqual(tds_return_due_date("2026-Q2"), date(2027, 1, 25))
        self.assertEqual(tds_return_due_date("2026-Q3"), date(2027, 4, 25))
        self.assertEqual(tds_return_due_date("2026-Q4"), date(2027, 7, 25))

    def test_prepare_tds_return(self):
        ret = prepare_tds_return({"vendor-A": D("5000"), "vendor-B": D("3000")},
                                 date(2026, 8, 15))
        self.assertEqual(ret.quarter, "2026-Q1")
        self.assertEqual(ret.total_withheld, D("8000.00"))
        self.assertEqual(ret.dedor_count if hasattr(ret, 'dedor_count') else ret.deductor_count, 2)

    def test_negative_withheld_refused(self):
        with self.assertRaises(ReturnError):
            prepare_tds_return({"v": D("-1")}, date(2026, 8, 15))


class TestPurity(unittest.TestCase):
    def test_no_odoo_imports(self):
        import inspect
        import return_logic
        source = inspect.getsource(return_logic)
        self.assertNotIn("from odoo", source)


if __name__ == "__main__":
    unittest.main()
