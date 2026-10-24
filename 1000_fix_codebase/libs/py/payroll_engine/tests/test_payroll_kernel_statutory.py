"""libs/py/payroll_engine kernel - statutory calculation tests (DoD-03).

Lib-level behavioural suite for the Bangladesh payroll kernel: every
statutory number is pinned here on its own (no reliance on the
services/payroll-engine suite):

- Income Tax Act 2023 / Finance Act 2024-2026: tax-free thresholds per
  taxpayer category, the +50,000 disabled-dependent uplift, the five slabs,
  the Section 78 investment rebate and the Section 173 minimum tax.
- Provident fund (Section 264 / Rule 351): both wings and the 15-day
  deposit deadline.
- Labour (Amendment) Act 2026: completed-years rule, gratuity (5-year cliff,
  30/45 days), resignation bands (7/15/30 days), retrenchment (30 days per
  year + 120 days' notice pay in lieu), overtime at 2x basic hourly.
- The monthly payslip path (OT -> gross -> PF -> annualised tax -> net).
"""

from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial, pytest.mark.tax]

_ROOT = Path(__file__).resolve().parents[4]  # codebase root (libs.py.*)
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from libs.py import payroll_engine as pe

D = Decimal


# ---------------------------------------------------------------------------
# Statutory constants
# ---------------------------------------------------------------------------


def test_tax_free_thresholds_fy_2026_27() -> None:
    thresholds = pe.TAX_FREE_THRESHOLDS
    assert thresholds == {
        "general": D("375000"),
        "female_senior": D("400000"),
        "disabled_third_gender": D("475000"),
        "freedom_fighter": D("500000"),
    }
    default = pe.TAX_FREE_THRESHOLD
    assert default == thresholds["general"]  # backwards-compatible alias


def test_tax_slab_table_widths_and_rates() -> None:
    slabs = pe.TAX_SLABS
    assert slabs == [
        (D("300000"), D("0.10")),
        (D("400000"), D("0.15")),
        (D("500000"), D("0.20")),
        (D("2000000"), D("0.25")),
        (None, D("0.30")),
    ]


def test_minimum_tax_by_location() -> None:
    assert pe.MINIMUM_TAX_LOCATIONS["dhaka_chattogram_city"] == D("5000")
    assert pe.MINIMUM_TAX_LOCATIONS["dhaka_chattogram"] == D("5000")
    assert pe.MINIMUM_TAX_LOCATIONS["other_city"] == D("4000")
    assert pe.MINIMUM_TAX_LOCATIONS["other_city_corporation"] == D("4000")
    assert pe.MINIMUM_TAX_LOCATIONS["non_city"] == D("3000")
    assert pe.MINIMUM_TAX_LOCATIONS["non_city_corporation"] == D("3000")


def test_labour_act_constants() -> None:
    assert pe.GRATUITY_MIN_YEARS_VESTING == 5
    assert pe.GRATUITY_DAYS_UPTO_12Y == 30
    assert pe.GRATUITY_DAYS_ABOVE_12Y == 45
    assert pe.RESIGNATION_BANDS == [(0, 7), (5, 15), (10, 30)]
    day_hours = pe.STANDARD_DAY_HOURS
    assert day_hours == D("8")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (D("0.125"), D("0.13")),  # half-up, not banker's (0.12)
        (D("0.124"), D("0.12")),
        (D("-0.125"), D("-0.13")),
        (D("100"), D("100.00")),
    ],
)
def test_q2_rounds_half_up_to_paisa(value: Decimal, expected: Decimal) -> None:
    assert pe.q2(value) == expected
    assert pe.q2(value).as_tuple().exponent == -2


# ---------------------------------------------------------------------------
# Income tax - slabs, categories, dependents
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("taxable", "expected"),
    [
        (D("0"), D("0.00")),
        (D("375000"), D("0.00")),  # threshold itself is tax-free
        (D("375001"), D("0.10")),  # first taka above threshold at 10%
        (D("500000"), D("12500.00")),
        (D("675000"), D("30000.00")),  # end of 10% band
        (D("1075000"), D("90000.00")),  # end of 15% band
        (D("1575000"), D("190000.00")),  # end of 20% band
        (D("3575000"), D("690000.00")),  # end of 25% band
        (D("4575000"), D("990000.00")),  # 1,000,000 of balance @30%
        (D("10000000"), D("2617500.00")),
    ],
)
def test_income_tax_general_slab_schedule(taxable: Decimal, expected: Decimal) -> None:
    assert pe.income_tax(taxable) == expected


@pytest.mark.parametrize(
    ("band_start", "rate"),
    [
        (D("375000"), D("0.10")),
        (D("675000"), D("0.15")),
        (D("1075000"), D("0.20")),
        (D("1575000"), D("0.25")),
        (D("3575000"), D("0.30")),
    ],
)
def test_income_tax_marginal_rate_inside_each_band(band_start: Decimal, rate: Decimal) -> None:
    low = band_start + D("1000")
    assert pe.income_tax(low + D("10000")) - pe.income_tax(low) == D("10000") * rate


def test_income_tax_rounds_half_up_to_paisa() -> None:
    # 0.05 above the threshold @10% = 0.005 -> 0.01 (half-up)
    assert pe.income_tax(D("375000.05")) == D("0.01")
    assert pe.income_tax(D("375000.04")) == D("0.00")


@pytest.mark.parametrize(
    ("category", "threshold"),
    [
        ("general", D("375000")),
        ("female_senior", D("400000")),
        ("disabled_third_gender", D("475000")),
        ("freedom_fighter", D("500000")),
    ],
)
def test_income_tax_category_thresholds(category: str, threshold: Decimal) -> None:
    assert pe.income_tax(threshold, category=category) == D("0.00")
    assert pe.income_tax(threshold + D("300000"), category=category) == D("30000.00")
    assert pe.income_tax(threshold + D("700000"), category=category) == D("90000.00")


@pytest.mark.parametrize(
    ("category", "dependents", "threshold"),
    [
        ("general", 1, D("425000")),
        ("general", 3, D("525000")),
        ("female_senior", 2, D("500000")),
        ("freedom_fighter", 1, D("550000")),
    ],
)
def test_disabled_dependent_uplift_is_50000_each(
    category: str, dependents: int, threshold: Decimal
) -> None:
    kwargs = {"category": category, "disabled_dependents": dependents}
    assert pe.income_tax(threshold, **kwargs) == D("0.00")
    assert pe.income_tax(threshold + D("100000"), **kwargs) == D("10000.00")


def test_income_tax_rejects_negative_income() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        pe.income_tax(D("-0.01"))


def test_income_tax_rejects_unknown_category() -> None:
    with pytest.raises(ValueError, match="unknown taxpayer category 'student'"):
        pe.income_tax(D("500000"), category="student")


def test_income_tax_rejects_negative_dependents() -> None:
    with pytest.raises(ValueError, match="disabled dependents"):
        pe.income_tax(D("500000"), disabled_dependents=-1)


# ---------------------------------------------------------------------------
# Section 78 investment rebate
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("taxable", "investment", "expected"),
    [
        (D("1000000"), D("1000000"), D("30000.00")),  # 3% of taxable binds
        (D("675000"), D("100000"), D("15000.00")),  # 15% of investment binds
        (D("50000000"), D("10000000"), D("1000000.00")),  # BDT 1,000,000 cap binds
        (D("1000000.50"), D("1000000"), D("30000.02")),  # 30000.015 half-up
        (D("675000"), D("0"), D("0.00")),  # no investment, no rebate
        (D("0"), D("50000"), D("0.00")),  # no taxable income, no rebate
        (D("-1"), D("50000"), D("0.00")),
    ],
)
def test_investment_tax_rebate_lower_of_three_limits(
    taxable: Decimal, investment: Decimal, expected: Decimal
) -> None:
    assert pe.investment_tax_rebate(taxable, investment) == expected


def test_investment_tax_rebate_default_investment_is_zero() -> None:
    assert pe.investment_tax_rebate(D("900000")) == D("0.00")


def test_investment_tax_rebate_rejects_negative_investment() -> None:
    with pytest.raises(ValueError, match="investment cannot be negative"):
        pe.investment_tax_rebate(D("675000"), D("-10"))


def test_income_tax_deducts_rebate() -> None:
    # 30,000 slab tax - 15,000 rebate
    assert pe.income_tax(D("675000"), allowable_investment=D("100000")) == D("15000.00")


def test_rebate_never_makes_tax_negative() -> None:
    # slab tax 1,000; rebate min(11,550, 15,000) = 11,550 -> floored at zero
    assert pe.income_tax(D("385000"), allowable_investment=D("100000")) == D("0.00")


def test_investment_below_threshold_is_irrelevant() -> None:
    assert pe.income_tax(D("300000"), allowable_investment=D("100000")) == D("0.00")


# ---------------------------------------------------------------------------
# Section 173 minimum tax
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("location", "minimum"),
    [
        ("dhaka_chattogram_city", D("5000.00")),
        ("dhaka_chattogram", D("5000.00")),
        ("other_city", D("4000.00")),
        ("other_city_corporation", D("4000.00")),
        ("non_city", D("3000.00")),
        ("non_city_corporation", D("3000.00")),
    ],
)
def test_minimum_tax_floors_small_payable_tax(location: str, minimum: Decimal) -> None:
    # slab tax on 385,000 is 1,000 -> lifted to the location minimum
    assert pe.income_tax(D("385000"), location=location) == minimum


def test_computed_tax_above_minimum_is_kept() -> None:
    assert pe.income_tax(D("675000"), location="dhaka_chattogram_city") == D("30000.00")


def test_minimum_tax_not_charged_below_threshold() -> None:
    assert pe.income_tax(D("300000"), location="dhaka_chattogram_city") == D("0.00")


def test_minimum_tax_applies_after_rebate() -> None:
    # slab 2,500 - rebate min(12,000, 1,500) = 1,000 -> Dhaka minimum 5,000
    assert pe.income_tax(
        D("400000"), location="dhaka_chattogram_city", allowable_investment=D("10000")
    ) == D("5000.00")


def test_unknown_location_rejected_when_tax_payable() -> None:
    with pytest.raises(ValueError, match="unknown tax location 'sylhet_town'"):
        pe.income_tax(D("600000"), location="sylhet_town")


# ---------------------------------------------------------------------------
# Provident fund
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("basic", "emp_pct", "er_pct", "employee", "employer"),
    [
        (D("30000"), D("10"), D("10"), D("3000.00"), D("3000.00")),
        (D("40000"), D("7.5"), D("10"), D("3000.00"), D("4000.00")),
        (D("1.25"), D("10"), D("0"), D("0.13"), D("0.00")),  # 0.125 half-up
        (D("30000"), D("0"), D("0"), D("0.00"), D("0.00")),
    ],
)
def test_provident_fund_both_wings(
    basic: Decimal, emp_pct: Decimal, er_pct: Decimal, employee: Decimal, employer: Decimal
) -> None:
    assert pe.provident_fund(basic, emp_pct, er_pct) == {
        "employee": employee,
        "employer": employer,
    }


@pytest.mark.parametrize(("emp_pct", "er_pct"), [(D("-1"), D("10")), (D("10"), D("-0.5"))])
def test_provident_fund_rejects_negative_percentages(emp_pct: Decimal, er_pct: Decimal) -> None:
    with pytest.raises(ValueError, match="PF percentages cannot be negative"):
        pe.provident_fund(D("30000"), emp_pct, er_pct)


@pytest.mark.parametrize(
    ("period_end", "deposit", "compliant"),
    [
        (date(2026, 9, 30), date(2026, 10, 15), True),  # deadline day is inclusive
        (date(2026, 9, 30), date(2026, 10, 16), False),
        (date(2026, 9, 30), date(2026, 9, 30), True),  # early deposit
        (date(2026, 1, 31), date(2026, 2, 15), True),
        (date(2026, 12, 31), date(2027, 1, 15), True),  # December rolls into January
        (date(2026, 12, 31), date(2027, 1, 16), False),
        (date(2026, 12, 31), date(2026, 1, 15), True),
    ],
)
def test_pf_deposit_deadline_15th_of_following_month(
    period_end: date, deposit: date, compliant: bool
) -> None:
    assert pe.is_pf_deposit_compliant(period_end, deposit) is compliant


# ---------------------------------------------------------------------------
# Completed years of service
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("joining", "as_of", "years"),
    [
        (date(2020, 6, 15), date(2026, 6, 14), 5),  # partial year does not count
        (date(2020, 6, 15), date(2026, 6, 15), 6),  # anniversary completes the year
        (date(2026, 6, 15), date(2026, 6, 15), 0),
        (date(2025, 12, 31), date(2026, 1, 1), 0),
        (date(2020, 2, 29), date(2021, 2, 28), 0),  # leap-day joiner
        (date(2020, 2, 29), date(2021, 3, 1), 1),
    ],
)
def test_completed_years(joining: date, as_of: date, years: int) -> None:
    assert pe.completed_years(joining, as_of) == years


def test_completed_years_rejects_end_before_joining() -> None:
    with pytest.raises(ValueError, match="service end before joining"):
        pe.completed_years(date(2026, 1, 2), date(2026, 1, 1))


# ---------------------------------------------------------------------------
# Gratuity - 5-year cliff, 30 days to 12 years, 45 days above
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("joining", "separation", "expected"),
    [
        (date(2025, 6, 1), date(2026, 1, 1), D("0.00")),
        (date(2022, 1, 1), date(2026, 1, 1), D("0.00")),  # 4 years: below the cliff
        (date(2021, 1, 2), date(2026, 1, 1), D("0.00")),  # one day short of 5 years
        (date(2021, 1, 1), date(2026, 1, 1), D("150000.00")),  # 5 x 30 x 1,000
        (date(2016, 1, 1), date(2026, 1, 1), D("300000.00")),
        (date(2014, 1, 1), date(2026, 1, 1), D("360000.00")),  # 12 x 30 x 1,000
        (date(2013, 1, 1), date(2026, 1, 1), D("405000.00")),  # + 1 x 45 x 1,000
        (date(2011, 1, 1), date(2026, 1, 1), D("495000.00")),
        (date(2006, 1, 1), date(2026, 1, 1), D("720000.00")),  # 360k + 8 x 45k
    ],
)
def test_gratuity_schedule(joining: date, separation: date, expected: Decimal) -> None:
    assert pe.gratuity(D("30000"), joining, separation) == expected


def test_gratuity_recurring_daily_rate_rounds_to_paisa() -> None:
    # 25,000 / 30 is a recurring decimal; 5 x 30 days must land on 125,000.00
    assert pe.gratuity(D("25000"), date(2021, 1, 1), date(2026, 1, 1)) == D("125000.00")


# ---------------------------------------------------------------------------
# Voluntary resignation - 7 / 15 / 30 days per completed year
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("joining", "expected"),
    [
        (date(2025, 6, 1), D("0.00")),  # under a year
        (date(2022, 1, 1), D("28000.00")),  # 4 x 7 x 1,000
        (date(2021, 1, 1), D("75000.00")),  # 5 x 15 x 1,000 (band starts at 5)
        (date(2017, 1, 1), D("135000.00")),  # 9 x 15
        (date(2016, 1, 1), D("300000.00")),  # 10 x 30 (band starts at 10)
        (date(2014, 1, 1), D("360000.00")),  # 12 x 30
    ],
)
def test_resignation_compensation_bands(joining: date, expected: Decimal) -> None:
    assert pe.resignation_compensation(D("30000"), joining, date(2026, 1, 1)) == expected


# ---------------------------------------------------------------------------
# Retrenchment / termination - 30 days per year + 120 days' notice in lieu
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("joining", "notice_days", "expected"),
    [
        (date(2022, 1, 1), 0, D("240000.00")),  # 120k service + 120k notice pay
        (date(2022, 1, 1), 30, D("210000.00")),  # 90 days' shortfall
        (date(2022, 1, 1), 120, D("120000.00")),  # full notice served
        (date(2022, 1, 1), 200, D("120000.00")),  # excess notice is not a deduction
        (date(2025, 6, 1), 0, D("120000.00")),  # notice pay only
    ],
)
def test_retrenchment_compensation(joining: date, notice_days: int, expected: Decimal) -> None:
    got = pe.retrenchment_compensation(
        D("30000"), joining, date(2026, 1, 1), notice_given_days=notice_days
    )
    assert got == expected


def test_retrenchment_default_is_no_notice_given() -> None:
    assert pe.retrenchment_compensation(D("30000"), date(2022, 1, 1), date(2026, 1, 1)) == D(
        "240000.00"
    )


def test_retrenchment_rejects_negative_notice() -> None:
    with pytest.raises(ValueError, match="notice given days cannot be negative"):
        pe.retrenchment_compensation(
            D("30000"), date(2022, 1, 1), date(2026, 1, 1), notice_given_days=-1
        )


# ---------------------------------------------------------------------------
# Overtime - 2x basic hourly (basic / 30 / 8)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("basic", "hours", "expected"),
    [
        (D("30000"), D("10"), D("2500.00")),  # 125/h x 2 x 10
        (D("30000"), D("1.5"), D("375.00")),
        (D("30000"), D("0"), D("0.00")),
        (D("10000"), D("1"), D("83.33")),  # 41.666.../h x 2
    ],
)
def test_overtime_double_basic_hourly(basic: Decimal, hours: Decimal, expected: Decimal) -> None:
    assert pe.overtime_amount(basic, hours) == expected


def test_overtime_rejects_negative_hours() -> None:
    with pytest.raises(ValueError, match="overtime hours cannot be negative"):
        pe.overtime_amount(D("30000"), D("-0.5"))


# ---------------------------------------------------------------------------
# The monthly payslip path
# ---------------------------------------------------------------------------


def test_payslip_input_defaults() -> None:
    inp = pe.PayslipInput(employee_ref="E-1", basic_monthly=D("1000"))
    assert inp.ot_hours == D("0")
    assert inp.incentive == D("0")
    assert inp.period_days == 30
    assert inp.taxpayer_category == "general"
    assert inp.disabled_dependents == 0
    assert inp.tax_location is None
    assert inp.allowable_investment == D("0")


def test_payslip_below_threshold_full_breakdown() -> None:
    slip = pe.compute_payslip(
        pe.PayslipInput(
            employee_ref="E-001",
            basic_monthly=D("30000"),
            ot_hours=D("10"),
            incentive=D("1500"),
            pf_employee_pct=D("10"),
            pf_employer_pct=D("10"),
        )
    )
    assert slip.basic == D("30000.00")
    assert slip.overtime == D("2500.00")
    assert slip.incentive == D("1500.00")
    assert slip.gross == D("34000.00")
    assert slip.pf_employee == D("3000.00")
    assert slip.pf_employer == D("3000.00")
    # (34,000 - 3,000) x 12 = 372,000 -> under the 375,000 threshold
    assert slip.tax_annual_projection == D("0.00")
    assert slip.tax_month == D("0.00")
    assert slip.net == D("31000.00")
    assert slip.lines == [
        ("basic", D("30000.00")),
        ("overtime", D("2500.00")),
        ("incentive", D("1500.00")),
        ("pf_employee", D("-3000.00")),
        ("tax_withheld", D("-0.00")),
    ]
    assert sum(amount for _, amount in slip.lines) == slip.net


def test_payslip_annualised_tax_withheld_monthly() -> None:
    slip = pe.compute_payslip(
        pe.PayslipInput(employee_ref="E-002", basic_monthly=D("60000"), pf_employee_pct=D("10"))
    )
    # (60,000 - 6,000) x 12 = 648,000 -> 27,300/yr -> 2,275/mo
    assert slip.tax_annual_projection == D("27300.00")
    assert slip.tax_month == D("2275.00")
    assert slip.net == D("51725.00")
    assert sum(amount for _, amount in slip.lines) == slip.net


def test_payslip_ytd_taxable_outside_the_slip_is_included() -> None:
    slip = pe.compute_payslip(
        pe.PayslipInput(
            employee_ref="E-003", basic_monthly=D("30000"), annual_taxable_other=D("300000")
        )
    )
    # 360,000 + 300,000 = 660,000 -> 28,500
    assert slip.tax_annual_projection == D("28500.00")
    assert slip.tax_month == D("2375.00")


def test_payslip_category_dependents_rebate_and_location() -> None:
    slip = pe.compute_payslip(
        pe.PayslipInput(
            employee_ref="E-004",
            basic_monthly=D("80000"),
            pf_employee_pct=D("10"),
            taxpayer_category="female_senior",
            disabled_dependents=1,
            tax_location="dhaka_chattogram_city",
            allowable_investment=D("150000"),
        )
    )
    # 864,000 taxable; threshold 450,000; slab 47,100; rebate 22,500 -> 24,600
    assert slip.tax_annual_projection == D("24600.00")
    assert slip.tax_month == D("2050.00")
    assert slip.net == D("69950.00")


def test_payslip_minimum_tax_spread_over_twelve_months() -> None:
    slip = pe.compute_payslip(
        pe.PayslipInput(
            employee_ref="E-005", basic_monthly=D("32000"), tax_location="dhaka_chattogram_city"
        )
    )
    # 384,000 -> slab 900 -> Dhaka minimum 5,000 -> 416.67/mo
    assert slip.tax_annual_projection == D("5000.00")
    assert slip.tax_month == D("416.67")
    assert slip.net == D("31583.33")
    assert sum(amount for _, amount in slip.lines) == slip.net


def test_payslip_negative_annual_taxable_is_clamped_to_zero() -> None:
    slip = pe.compute_payslip(
        pe.PayslipInput(employee_ref="E-006", basic_monthly=D("1000"), incentive=D("-5000"))
    )
    assert slip.gross == D("-4000.00")
    assert slip.tax_annual_projection == D("0.00")
    assert slip.net == D("-4000.00")


def test_payslip_rejects_negative_basic() -> None:
    with pytest.raises(ValueError, match="basic cannot be negative"):
        pe.compute_payslip(pe.PayslipInput("E-007", D("-5")))


def test_payslip_propagates_tax_input_errors() -> None:
    with pytest.raises(ValueError, match="unknown taxpayer category"):
        pe.compute_payslip(pe.PayslipInput("E-008", D("30000"), taxpayer_category="nobody"))
