"""payroll-engine tests — P08-M03 / R06-M03 (CD-M56-01).

DoD-03: 100% of every payroll calculation path, and negative tests. The
kernel is the ONLY calculation authority for M56 — these tests pin each
statutory number (Income Tax Act 2023 / Finance Act 2024-2026 slabs,
Labour (Amendment) Act 2026 gratuity and resignation bands, PF structure,
BEFTN batch calendar, and 128-byte file generation).
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

from libs.py.payroll_engine import (
    BeftnBatchHeader,
    BeftnEntry,
    PayslipInput,
    beftn_settlement_date,
    completed_years,
    compute_payslip,
    generate_beftn_batch_file,
    gratuity,
    income_tax,
    investment_tax_rebate,
    is_pf_deposit_compliant,
    is_working_day,
    overtime_amount,
    provident_fund,
    resignation_compensation,
    retrenchment_compensation,
    validate_routing_number,
)


class TestIncomeTaxFY202627(unittest.TestCase):
    """The slab table exactly as enacted under Income Tax Act 2023 / Finance Act 2024-2026."""

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

    def test_special_categories(self):
        # Female & Senior: threshold 400k
        self.assertEqual(income_tax(Decimal("400000"), category="female_senior"), Decimal("0.00"))
        self.assertEqual(
            income_tax(Decimal("500000"), category="female_senior"), Decimal("10000.00")
        )

        # Disabled & Third Gender: threshold 475k
        self.assertEqual(
            income_tax(Decimal("475000"), category="disabled_third_gender"), Decimal("0.00")
        )
        self.assertEqual(
            income_tax(Decimal("575000"), category="disabled_third_gender"), Decimal("10000.00")
        )

        # War-Wounded Freedom Fighter: threshold 500k
        self.assertEqual(income_tax(Decimal("500000"), category="freedom_fighter"), Decimal("0.00"))
        self.assertEqual(
            income_tax(Decimal("600000"), category="freedom_fighter"), Decimal("10000.00")
        )

    def test_disabled_dependents_additional_threshold(self):
        # General 375k + 2 * 50k = 475k
        self.assertEqual(income_tax(Decimal("475000"), disabled_dependents=2), Decimal("0.00"))
        self.assertEqual(income_tax(Decimal("575000"), disabled_dependents=2), Decimal("10000.00"))

    def test_negative_disabled_dependents_raises(self):
        with self.assertRaises(ValueError):
            income_tax(Decimal("500000"), disabled_dependents=-1)

    def test_unknown_category_raises(self):
        with self.assertRaises(ValueError):
            income_tax(Decimal("500000"), category="unknown_cat")

    def test_minimum_tax_rules(self):
        # Taxable income triggers small tax of 1,000, but Dhaka/CTG min tax is 5,000
        self.assertEqual(
            income_tax(Decimal("385000"), location="dhaka_chattogram_city"), Decimal("5000.00")
        )
        self.assertEqual(income_tax(Decimal("385000"), location="other_city"), Decimal("4000.00"))
        self.assertEqual(income_tax(Decimal("385000"), location="non_city"), Decimal("3000.00"))

        # If tax calculated exceeds minimum tax, calculated tax is kept
        self.assertEqual(
            income_tax(Decimal("675000"), location="dhaka_chattogram_city"), Decimal("30000.00")
        )

        # If zero tax payable (income below threshold), minimum tax does NOT apply
        self.assertEqual(
            income_tax(Decimal("300000"), location="dhaka_chattogram_city"), Decimal("0.00")
        )

    def test_unknown_location_raises(self):
        with self.assertRaises(ValueError):
            income_tax(Decimal("600000"), location="invalid_loc")

    def test_investment_tax_rebate(self):
        # 3% of 675,000 is 20,250. 15% of 100,000 is 15,000. Lower is 15,000.
        rebate = investment_tax_rebate(Decimal("675000"), Decimal("100000"))
        self.assertEqual(rebate, Decimal("15000.00"))

        # Zero investment or negative
        self.assertEqual(investment_tax_rebate(Decimal("675000"), Decimal("0")), Decimal("0.00"))
        self.assertEqual(investment_tax_rebate(Decimal("0"), Decimal("50000")), Decimal("0.00"))
        with self.assertRaises(ValueError):
            investment_tax_rebate(Decimal("675000"), Decimal("-10"))

        # Cap limit 1,000,000
        rebate_cap = investment_tax_rebate(Decimal("50000000"), Decimal("10000000"))
        self.assertEqual(rebate_cap, Decimal("1000000.00"))

        # Tax calculation applying rebate
        # Tax on 675k is 30,000; rebate is 15,000 -> net tax 15,000
        net_tax = income_tax(Decimal("675000"), allowable_investment=Decimal("100000"))
        self.assertEqual(net_tax, Decimal("15000.00"))


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
        with self.assertRaises(ValueError):
            provident_fund(Decimal("100"), Decimal("0"), Decimal("-1"))

    def test_deposit_compliance_timeline(self):
        # Rule 351: 15 days of following month
        self.assertTrue(is_pf_deposit_compliant(date(2026, 9, 30), date(2026, 10, 15)))
        self.assertFalse(is_pf_deposit_compliant(date(2026, 9, 30), date(2026, 10, 16)))
        # December rollover to January
        self.assertTrue(is_pf_deposit_compliant(date(2026, 12, 31), date(2027, 1, 15)))
        self.assertFalse(is_pf_deposit_compliant(date(2026, 12, 31), date(2027, 1, 16)))


class TestServiceYears(unittest.TestCase):
    def test_completed_years_partial_does_not_count(self):
        self.assertEqual(completed_years(date(2020, 6, 15), date(2026, 6, 14)), 5)
        self.assertEqual(completed_years(date(2020, 6, 15), date(2026, 6, 15)), 6)

    def test_reversed_dates_raise(self):
        with self.assertRaises(ValueError):
            completed_years(date(2026, 1, 1), date(2020, 1, 1))


class TestGratuityAct2026(unittest.TestCase):
    """30 days' basic per completed year to 12 years, 45 above, with 5-year vesting cliff."""

    def test_under_5_years_vesting_cliff_is_zero(self):
        # 4 completed years -> below 5 years vesting cliff -> 0.00
        g = gratuity(Decimal("30000"), date(2022, 1, 1), date(2026, 1, 1))
        self.assertEqual(g, Decimal("0.00"))

    def test_between_5_and_12_years(self):
        # 10 years x 30 days x (30000/30) = 10 x 30000 = 300,000
        g = gratuity(Decimal("30000"), date(2016, 1, 1), date(2026, 1, 1))
        self.assertEqual(g, Decimal("300000.00"))

    def test_band_jump_above_12(self):
        # 12y @30 + 3y @45, basic 30,000 (daily 1,000): 360,000 + 135,000 = 495,000
        g = gratuity(Decimal("30000"), date(2011, 1, 1), date(2026, 1, 1))
        self.assertEqual(g, Decimal("495000.00"))

    def test_less_than_a_year_is_zero(self):
        g = gratuity(Decimal("30000"), date(2025, 6, 1), date(2026, 1, 1))
        self.assertEqual(g, Decimal("0.00"))


class TestResignationCompensation(unittest.TestCase):
    def test_band_below_5_years_7_days(self):
        # 3 years x 7 days x daily(1000) = 21,000
        c = resignation_compensation(Decimal("30000"), date(2023, 1, 1), date(2026, 1, 1))
        self.assertEqual(c, Decimal("21000.00"))

    def test_band_5_to_9_15_days(self):
        # 7 years x 15 x 1000 = 105,000
        c = resignation_compensation(Decimal("30000"), date(2019, 1, 1), date(2026, 1, 1))
        self.assertEqual(c, Decimal("105000.00"))

    def test_band_10_plus_30_days(self):
        # 12 years x 30 x 1000 = 360,000
        c = resignation_compensation(Decimal("30000"), date(2014, 1, 1), date(2026, 1, 1))
        self.assertEqual(c, Decimal("360000.00"))


class TestRetrenchmentCompensation(unittest.TestCase):
    def test_retrenchment_full_notice(self):
        # 4 completed years x 30 days x 1000 daily = 120,000. 120 days notice given -> 0 notice pay
        c = retrenchment_compensation(
            Decimal("30000"), date(2022, 1, 1), date(2026, 1, 1), notice_given_days=120
        )
        self.assertEqual(c, Decimal("120000.00"))

    def test_retrenchment_without_notice(self):
        # 4 years service = 120,000 + 120 days notice shortfall = 120,000 -> 240,000
        c = retrenchment_compensation(
            Decimal("30000"), date(2022, 1, 1), date(2026, 1, 1), notice_given_days=0
        )
        self.assertEqual(c, Decimal("240000.00"))

    def test_retrenchment_negative_notice_raises(self):
        with self.assertRaises(ValueError):
            retrenchment_compensation(
                Decimal("30000"), date(2022, 1, 1), date(2026, 1, 1), notice_given_days=-1
            )


class TestOvertime(unittest.TestCase):
    def test_double_rate(self):
        # hourly = 20800/208 = 100; OT 10h -> 100*2*10 = 2,000
        self.assertEqual(overtime_amount(Decimal("20800"), Decimal("10")), Decimal("2000.00"))
        self.assertEqual(overtime_amount(Decimal("30000"), Decimal("10")), Decimal("2884.62"))

    def test_zero_hours(self):
        self.assertEqual(overtime_amount(Decimal("30000"), Decimal("0")), Decimal("0.00"))

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            overtime_amount(Decimal("30000"), Decimal("-1"))


class TestBeftnBatchCalendar(unittest.TestCase):
    """INT-005: cut-off 16:00; Fri/Sat/holiday roll to the next working day."""

    def test_before_cutoff_on_working_day_same_day(self):
        # 2026-10-01 is a Thursday
        self.assertEqual(beftn_settlement_date(datetime(2026, 10, 1, 10, 0)), date(2026, 10, 1))

    def test_after_cutoff_rolls_next_working_day(self):
        # 2026-10-01 Thursday after 16:00 rolls to Sunday 2026-10-04
        self.assertEqual(beftn_settlement_date(datetime(2026, 10, 1, 16, 30)), date(2026, 10, 4))

    def test_after_cutoff_wednesday_rolls_thursday(self):
        self.assertEqual(beftn_settlement_date(datetime(2026, 9, 30, 17, 0)), date(2026, 10, 1))

    def test_friday_rolls_to_sunday(self):
        self.assertEqual(beftn_settlement_date(datetime(2026, 10, 2, 10, 0)), date(2026, 10, 4))

    def test_saturday_rolls_to_sunday(self):
        self.assertEqual(beftn_settlement_date(datetime(2026, 10, 3, 11, 0)), date(2026, 10, 4))

    def test_fixed_holiday_rolls(self):
        # 2026-12-16 Victory Day (Wednesday) -> Thursday 17th
        self.assertEqual(beftn_settlement_date(datetime(2026, 12, 16, 9, 0)), date(2026, 12, 17))

    def test_extra_holiday_respected(self):
        self.assertEqual(
            beftn_settlement_date(datetime(2026, 10, 7, 9, 0), extra_holidays={date(2026, 10, 7)}),
            date(2026, 10, 8),
        )

    def test_is_working_day_weekend(self):
        self.assertFalse(is_working_day(date(2026, 10, 2)))  # Friday
        self.assertFalse(is_working_day(date(2026, 10, 3)))  # Saturday
        self.assertTrue(is_working_day(date(2026, 10, 4)))  # Sunday


class TestBeftnBatchFileGeneration(unittest.TestCase):
    """BEFTN INT-005 128-byte record generator tests."""

    def setUp(self):
        self.header = BeftnBatchHeader(
            company_name="1000 FIX SERVICES",
            company_id="COMP001",
            originating_routing="125272345",
            batch_number=1,
            settlement_date=date(2026, 10, 4),
            description="SALARY",
        )
        self.entries = [
            BeftnEntry(
                employee_id="EMP-001",
                employee_name="RAHIM UDDIN",
                routing_number="085261234",
                account_number="1051234567890",
                amount_bdt=Decimal("45000.50"),
            ),
            BeftnEntry(
                employee_id="EMP-002",
                employee_name="FATIMA BEGUM",
                routing_number="095271234",
                account_number="2059876543210",
                amount_bdt=Decimal("52000.00"),
            ),
        ]

    def test_generate_file_128_byte_lines(self):
        file_content = generate_beftn_batch_file(
            self.header, self.entries, created_at=datetime(2026, 10, 1, 11, 0)
        )
        lines = [line for line in file_content.split("\r\n") if line]
        self.assertEqual(
            len(lines), 6
        )  # File Header, Batch Header, 2 Entries, Batch Control, File Control
        for idx, line in enumerate(lines):
            self.assertEqual(len(line), 128, f"Line {idx} length is not 128 bytes: {len(line)}")

        # Check Record Type indicators
        self.assertEqual(lines[0][0], "1")  # File Header
        self.assertEqual(lines[1][0], "5")  # Batch Header
        self.assertEqual(lines[2][0], "6")  # Entry 1
        self.assertEqual(lines[3][0], "6")  # Entry 2
        self.assertEqual(lines[4][0], "8")  # Batch Control

    def test_routing_validation(self):
        self.assertTrue(validate_routing_number("125272345"))
        self.assertFalse(validate_routing_number("12527234"))  # 8 digits
        self.assertFalse(validate_routing_number("12527234A"))  # alphanumeric

    def test_invalid_originating_routing_raises(self):
        bad_header = BeftnBatchHeader(
            company_name="1000 FIX",
            company_id="COMP001",
            originating_routing="INVALID",
            batch_number=1,
            settlement_date=date(2026, 10, 4),
        )
        with self.assertRaises(ValueError):
            generate_beftn_batch_file(bad_header, self.entries)

    def test_empty_entries_raises(self):
        with self.assertRaises(ValueError):
            generate_beftn_batch_file(self.header, [])

    def test_invalid_beneficiary_routing_raises(self):
        bad_entries = [
            BeftnEntry("EMP-001", "NAME", "BADROUT", "ACC", Decimal("1000")),
        ]
        with self.assertRaises(ValueError):
            generate_beftn_batch_file(self.header, bad_entries)

    def test_negative_or_zero_amount_raises(self):
        bad_entries = [
            BeftnEntry("EMP-001", "NAME", "125272345", "ACC", Decimal("0")),
        ]
        with self.assertRaises(ValueError):
            generate_beftn_batch_file(self.header, bad_entries)


class TestPayslipPath(unittest.TestCase):
    """The monthly calculation path end to end (Journey 13's core)."""

    def test_full_slip(self):
        slip = compute_payslip(
            PayslipInput(
                employee_ref="E-001",
                basic_monthly=Decimal("20800"),
                ot_hours=Decimal("10"),
                incentive=Decimal("1500"),
                pf_employee_pct=Decimal("10"),
                pf_employer_pct=Decimal("10"),
            )
        )
        self.assertEqual(slip.overtime, Decimal("2000.00"))
        self.assertEqual(slip.gross, Decimal("24300.00"))
        self.assertEqual(slip.pf_employee, Decimal("2080.00"))
        self.assertEqual(slip.pf_employer, Decimal("2080.00"))
        # annualised taxable: (24300-2080)*12 = 266,640 -> below 375k: no tax
        self.assertEqual(slip.tax_month, Decimal("0.00"))
        self.assertEqual(slip.net, Decimal("22220.00"))
        self.assertEqual(sum(amount for _, amount in slip.lines), slip.net)

    def test_tax_kicks_in_above_threshold(self):
        slip = compute_payslip(
            PayslipInput(
                employee_ref="E-002", basic_monthly=Decimal("60000"), pf_employee_pct=Decimal("10")
            )
        )
        # employment income = (60000-6000)*12 = 648,000
        # ITA 2023 Para 27 exemption = min(216,000, 450,000) = 216,000
        # taxable 432,000 -> (432,000-375,000) @10% = 5,700/yr = 475/mo
        self.assertEqual(slip.annual_exemption, Decimal("216000.00"))
        self.assertEqual(slip.tax_annual_projection, Decimal("5700.00"))
        self.assertEqual(slip.tax_month, Decimal("475.00"))
        self.assertEqual(slip.net, Decimal("53525.00"))

    def test_ytd_other_income_is_taxed(self):
        slip = compute_payslip(
            PayslipInput(
                employee_ref="E-003",
                basic_monthly=Decimal("30000"),
                annual_taxable_other=Decimal("300000"),
            )
        )
        # Para 27 reaches employment income (360,000 -> exempt 120,000) only;
        # the 300,000 of other income is taxed whole -> 540,000 taxable
        self.assertEqual(slip.tax_annual_projection, Decimal("16500.00"))

    def test_negative_basic_raises(self):
        with self.assertRaises(ValueError):
            compute_payslip(PayslipInput("E", Decimal("-5")))

    def test_payslip_with_tax_category_and_rebate(self):
        slip = compute_payslip(
            PayslipInput(
                employee_ref="E-004",
                basic_monthly=Decimal("80000"),
                pf_employee_pct=Decimal("10"),
                taxpayer_category="female_senior",
                disabled_dependents=1,
                tax_location="dhaka_chattogram_city",
                allowable_investment=Decimal("150000"),
            )
        )
        # Employment income: (80k - 8k) * 12 = 864,000
        # Para 27 exemption: min(288,000, 450,000) -> taxable 576,000
        # Threshold: 400k (female_senior) + 50k (1 disabled child) = 450,000
        # Remaining: 126,000 @10% = 12,600
        # Rebate: min(576k*0.03=17,280, 150k*0.15=22,500, 1,000,000) = 17,280
        # 12,600 - 17,280 -> 0, but s.163 keeps the Dhaka minimum as a floor
        # on a taxpayer inside the charge: 5,000/yr -> 416.67/mo
        self.assertEqual(slip.annual_exemption, Decimal("288000.00"))
        self.assertEqual(slip.tax_annual_projection, Decimal("5000.00"))
        self.assertEqual(slip.tax_month, Decimal("416.67"))
        self.assertEqual(slip.net, Decimal("71583.33"))


if __name__ == "__main__":
    unittest.main()
