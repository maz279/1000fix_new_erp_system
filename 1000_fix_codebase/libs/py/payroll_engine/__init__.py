# libs/py/payroll_engine — P08-M03 / R06-M03: Bangladesh payroll calculation kernel (L5 pure).
#
# The ONLY calculation authority for M56 (DoD-03: 100% test coverage on every
# payroll calculation path). Stdlib-only, Decimal money, no Odoo imports —
# reachable from the Odoo module (libs.py.* is on PYTHONPATH), from pytest
# and from services/payroll-engine (its canonical L5 service shell).
#
# Statutory basis (verified current FY 2026-27 / BLA 2006 & Amendment 2026):
#   - Income Tax Act 2023 (Act 12 of 2023) / Finance Act 2024 / 2026:
#     - Tax-free thresholds:
#       * General: BDT 375,000
#       * Female & Senior Citizens (>= 65y): BDT 400,000
#       * Persons with Disabilities & Third Gender: BDT 475,000
#       * Gazetted War-Wounded Freedom Fighters: BDT 500,000
#       * Child with disability exemption: +BDT 50,000 per disabled dependent
#     - Tax Slabs:
#       * First 300,000 @ 10%
#       * Next 400,000 @ 15%
#       * Next 500,000 @ 20%
#       * Next 2,000,000 @ 25%
#       * Balance @ 30%
#     - Investment Tax Rebate (Section 78):
#       * Lower of: 3% of taxable income, 15% of allowable investment, BDT 1,000,000
#     - Minimum Tax (Section 173):
#       * Dhaka & Chattogram City Corporation: BDT 5,000
#       * Other City Corporations: BDT 4,000
#       * Non-City Corporation areas: BDT 3,000
#   - Gratuity, Bangladesh Labour (Amendment) Act 2026:
#     - Minimum 5 completed years required to qualify (vesting threshold).
#     - 30 days' basic per completed year up to 12 years; 45 days' per year above 12.
#   - Voluntary-resignation compensation (BLA 2006 Section 27(3) as amended 2026):
#     - 7 days' wages per year below 5 years' service, 15 days' for 5-<10 years, 30 days' for 10+.
#   - Retrenchment / Termination compensation (BLA 2006 Section 20 & 26):
#     - 30 days basic per completed year + 120 days notice pay.
#   - Provident fund (Section 264 / Rule 351):
#     - Statutory equal contributions (10% employee + 10% employer).
#     - PF Trust deposit timeline: within 15 days of following month.
#   - BEFTN (INT-005):
#     - Sunday-Thursday working week (Bangladesh Bank clearing days).
#     - Final daily cut-off 16:00.
#     - Weekend (Friday/Saturday) and public holiday rollover to next working banking day.
#     - Standard 128-byte fixed-width ASCII batch file format.
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from .beftn import (
    BeftnBatchHeader,
    BeftnEntry,
    generate_beftn_batch_file,
    validate_routing_number,
)

TWO = Decimal("0.01")

# --- FY 2026-27 income-tax thresholds & slabs ---
TAX_FREE_THRESHOLDS: dict[str, Decimal] = {
    "general": Decimal("375000"),
    "female_senior": Decimal("400000"),
    "disabled_third_gender": Decimal("475000"),
    "freedom_fighter": Decimal("500000"),
}
TAX_FREE_THRESHOLD = Decimal("375000")  # General default for backwards compatibility

TAX_SLABS = [  # (width of band, rate) applied above threshold
    (Decimal("300000"), Decimal("0.10")),
    (Decimal("400000"), Decimal("0.15")),
    (Decimal("500000"), Decimal("0.20")),
    (Decimal("2000000"), Decimal("0.25")),
    (None, Decimal("0.30")),  # balance
]

MINIMUM_TAX_LOCATIONS: dict[str, Decimal] = {
    "dhaka_chattogram_city": Decimal("5000"),
    "dhaka_chattogram": Decimal("5000"),
    "other_city": Decimal("4000"),
    "other_city_corporation": Decimal("4000"),
    "non_city": Decimal("3000"),
    "non_city_corporation": Decimal("3000"),
}


# --- Labour (Amendment) Act 2026 constants ---
GRATUITY_MIN_YEARS_VESTING = 5  # continuous service cliff for gratuity
GRATUITY_DAYS_UPTO_12Y = 30  # days of basic per completed year <= 12
GRATUITY_DAYS_ABOVE_12Y = 45  # days of basic per year beyond 12
RESIGNATION_BANDS = [  # (min completed years, days of wages per year)
    (0, 7),
    (5, 15),
    (10, 30),
]
STANDARD_DAY_HOURS = Decimal("8")
OT_DIVISOR_HOURS = Decimal("208")  # BLR 2015 formula: 48h x 52 / 12 = 208 hours/month
OT_BASE_COMPONENTS = ("basic", "dearness", "ad_hoc")  # BLA 2006 s.108
SALARY_EXEMPTION_CEILING = Decimal("450000")  # ITA 2023 Sixth Schedule Part 1 Para 27

# --- Bangladesh public holidays (fixed-date, 2026-2028) for BEFTN settlement ---
FIXED_HOLIDAYS = {(2, 21), (3, 26), (4, 14), (5, 1), (8, 15), (12, 16), (12, 25)}
WEEKEND = {4, 5}  # Friday=4, Saturday=5 (Mon=0); Sun-Thu works


def q2(value: Decimal) -> Decimal:
    return value.quantize(TWO, rounding=ROUND_HALF_UP)


def is_working_day(d: date, extra_holidays: set[date] | None = None) -> bool:
    """Sunday-Thursday working week; Friday+Saturday weekend plus holidays."""
    if d.weekday() in WEEKEND:
        return False
    if (d.month, d.day) in FIXED_HOLIDAYS:
        return False
    return not (extra_holidays and d in extra_holidays)


def beftn_settlement_date(
    submitted: datetime, cutoff_hour: int = 16, extra_holidays: set[date] | None = None
) -> date:
    """INT-005 batch model: in before the final cut-off on a working day ->
    same day; otherwise the next working day (Fri/Sat/holiday roll forward)."""
    d = submitted.date()
    if submitted.hour >= cutoff_hour:
        d = d + timedelta(days=1)
    while not is_working_day(d, extra_holidays):
        d = d + timedelta(days=1)
    return d


def investment_tax_rebate(
    annual_taxable: Decimal, allowable_investment: Decimal = Decimal("0")
) -> Decimal:
    """Section 78 Income Tax Act 2023: lower of 3% taxable, 15% investment, or BDT 1,000,000."""
    if allowable_investment < 0:
        raise ValueError("allowable investment cannot be negative")
    if allowable_investment == 0 or annual_taxable <= 0:
        return Decimal("0.00")
    limit_taxable = annual_taxable * Decimal("0.03")
    limit_investment = allowable_investment * Decimal("0.15")
    limit_cap = Decimal("1000000")
    return q2(min(limit_taxable, limit_investment, limit_cap))


def income_tax(
    annual_taxable: Decimal,
    category: str = "general",
    disabled_dependents: int = 0,
    location: str | None = None,
    allowable_investment: Decimal = Decimal("0"),
) -> Decimal:
    """FY 2026-27 slab tax under Income Tax Act 2023 / Finance Act 2024-2026."""
    if annual_taxable < 0:
        raise ValueError("taxable income cannot be negative")
    if category not in TAX_FREE_THRESHOLDS:
        raise ValueError(f"unknown taxpayer category '{category}'")
    if disabled_dependents < 0:
        raise ValueError("disabled dependents count cannot be negative")

    base_threshold = TAX_FREE_THRESHOLDS[category]
    threshold = base_threshold + (Decimal("50000") * Decimal(str(disabled_dependents)))

    tax = Decimal("0")
    remaining = annual_taxable - threshold
    for width, rate in TAX_SLABS:
        if remaining <= 0:
            break
        band = remaining if width is None else min(remaining, width)
        tax += band * rate
        remaining -= band

    # Whether the taxpayer is inside the charge at all is decided by the slab
    # tax, BEFORE any rebate: s.163 makes the location minimum a FLOOR on the
    # tax payable, so a s.78 rebate reduces liability only down to that floor
    # and never below it. Testing `tax > 0` after the rebate instead let a
    # large rebate wipe out the minimum tax altogether.
    charged = tax > 0

    # Apply investment tax rebate (Section 78)
    if charged and allowable_investment > 0:
        rebate = investment_tax_rebate(annual_taxable, allowable_investment)
        tax = max(tax - rebate, Decimal("0"))

    # Apply minimum tax if tax is payable and location is specified
    if charged and location:
        if location not in MINIMUM_TAX_LOCATIONS:
            raise ValueError(f"unknown tax location '{location}'")
        min_tax = MINIMUM_TAX_LOCATIONS[location]
        tax = max(tax, min_tax)

    return q2(tax)


def provident_fund(
    basic: Decimal, employee_pct: Decimal, employer_pct: Decimal
) -> dict[str, Decimal]:
    """Statutory PF: both wings of the contribution structure."""
    if employee_pct < 0 or employer_pct < 0:
        raise ValueError("PF percentages cannot be negative")
    return {
        "employee": q2(basic * employee_pct / Decimal(100)),
        "employer": q2(basic * employer_pct / Decimal(100)),
    }


def is_pf_deposit_compliant(period_end: date, deposit_date: date) -> bool:
    """Rule 351: PF contribution must be deposited to PF Trust within 15 days of following month."""
    if period_end.month == 12:
        deadline = date(period_end.year + 1, 1, 15)
    else:
        deadline = date(period_end.year, period_end.month + 1, 15)
    return deposit_date <= deadline


def completed_years(joining: date, as_of: date) -> int:
    """Completed years of service - partial years do NOT count (gratuity/resignation)."""
    if as_of < joining:
        raise ValueError("service end before joining")
    years = as_of.year - joining.year
    if (as_of.month, as_of.day) < (joining.month, joining.day):
        years -= 1
    return max(years, 0)


def gratuity(basic_monthly: Decimal, joining: date, separation: date) -> Decimal:
    """Labour (Amendment) Act 2026: 30 days' basic per completed year up to 12
    years, 45 days' per year above 12. Requires minimum 5 years continuous service."""
    years = completed_years(joining, separation)
    if years < GRATUITY_MIN_YEARS_VESTING:
        return Decimal("0.00")
    daily = basic_monthly / Decimal(30)
    upto = min(years, 12) * GRATUITY_DAYS_UPTO_12Y
    above = max(years - 12, 0) * GRATUITY_DAYS_ABOVE_12Y
    return q2(daily * (upto + above))


def resignation_compensation(basic_monthly: Decimal, joining: date, separation: date) -> Decimal:
    """Voluntary resignation is compensable under the 2026 Amendment:
    7/15/30 days' wages per completed year by service band."""
    years = completed_years(joining, separation)
    days_per_year = next(d for min_years, d in reversed(RESIGNATION_BANDS) if years >= min_years)
    daily = basic_monthly / Decimal(30)
    return q2(daily * days_per_year * years)


def retrenchment_compensation(
    basic_monthly: Decimal, joining: date, separation: date, notice_given_days: int = 0
) -> Decimal:
    """Section 20 & 26: 30 days basic per completed year + 120 days notice pay in lieu."""
    if notice_given_days < 0:
        raise ValueError("notice given days cannot be negative")
    years = completed_years(joining, separation)
    daily = basic_monthly / Decimal(30)
    service_comp = daily * Decimal(30) * Decimal(str(years))
    notice_shortfall = max(120 - notice_given_days, 0)
    notice_pay = daily * Decimal(str(notice_shortfall))
    return q2(service_comp + notice_pay)


def salary_exemption(
    annual_employment_income: Decimal,
    ceiling: Decimal = SALARY_EXEMPTION_CEILING,
) -> Decimal:
    """ITA 2023 Sixth Schedule Part 1 Para 27 consolidated salary exemption:
    lower of one-third of annual employment income or the statutory ceiling
    (default BDT 450,000, parameterised for Finance Act updates)."""
    if ceiling < 0:
        raise ValueError("exemption ceiling cannot be negative")
    if annual_employment_income <= 0 or ceiling == 0:
        return Decimal("0.00")
    return q2(min(annual_employment_income / Decimal(3), ceiling))


def overtime_amount(
    basic_monthly: Decimal,
    ot_hours: Decimal,
    dearness_monthly: Decimal = Decimal("0"),
    adhoc_monthly: Decimal = Decimal("0"),
    divisor_hours: Decimal = OT_DIVISOR_HOURS,
) -> Decimal:
    """Overtime per BLA 2006 s.108 & BLR 2015: 2x ordinary hourly rate over 208-hour divisor.
    Ordinary rate base = basic + dearness allowance + ad-hoc/interim wage."""
    if ot_hours < 0:
        raise ValueError("overtime hours cannot be negative")
    if divisor_hours <= 0:
        raise ValueError("overtime divisor hours must be positive")
    base = basic_monthly + dearness_monthly + adhoc_monthly
    hourly = base / divisor_hours
    return q2(hourly * Decimal(2) * ot_hours)


@dataclass
class PayslipInput:
    """One employee-month of inputs. Hours come from LOCKED attendance."""

    employee_ref: str
    basic_monthly: Decimal
    attendance_hours: Decimal = Decimal("0")
    ot_hours: Decimal = Decimal("0")
    incentive: Decimal = Decimal("0")  # from M57's engine
    house_rent: Decimal = Decimal("0")
    medical_allowance: Decimal = Decimal("0")
    conveyance_allowance: Decimal = Decimal("0")
    technical_allowance: Decimal = Decimal("0")
    other_allowance: Decimal = Decimal("0")
    dearness_allowance: Decimal = Decimal("0")
    adhoc_allowance: Decimal = Decimal("0")
    pf_employee_pct: Decimal = Decimal("0")
    pf_employer_pct: Decimal = Decimal("0")
    annual_taxable_other: Decimal = Decimal("0")  # YTD taxable outside this slip
    period_days: int = 30
    taxpayer_category: str = "general"
    disabled_dependents: int = 0
    tax_location: str | None = None
    allowable_investment: Decimal = Decimal("0")
    ot_divisor_hours: Decimal = OT_DIVISOR_HOURS
    exemption_ceiling: Decimal | None = None


@dataclass
class PayslipResult:
    gross: Decimal
    basic: Decimal
    overtime: Decimal
    incentive: Decimal
    pf_employee: Decimal
    pf_employer: Decimal
    tax_month: Decimal
    tax_annual_projection: Decimal
    net: Decimal
    allowances_total: Decimal = Decimal("0.00")
    annual_exemption: Decimal = Decimal("0.00")
    lines: list[tuple[str, Decimal]] = field(default_factory=list)


def compute_payslip(inp: PayslipInput) -> PayslipResult:
    """The monthly calculation path: OT -> allowances -> gross -> PF on basic ->
    ITA 2023 Para 27 exemption -> tax on annualised taxable -> net."""
    if inp.basic_monthly < 0:
        raise ValueError("basic cannot be negative")
    ot = overtime_amount(
        inp.basic_monthly,
        inp.ot_hours,
        dearness_monthly=inp.dearness_allowance,
        adhoc_monthly=inp.adhoc_allowance,
        divisor_hours=inp.ot_divisor_hours,
    )
    allowances = q2(
        inp.house_rent
        + inp.medical_allowance
        + inp.conveyance_allowance
        + inp.technical_allowance
        + inp.other_allowance
        + inp.dearness_allowance
        + inp.adhoc_allowance
    )
    gross = q2(inp.basic_monthly + allowances + ot + inp.incentive)
    pf = provident_fund(inp.basic_monthly, inp.pf_employee_pct, inp.pf_employer_pct)

    # ITA 2023 Sixth Schedule Part 1 Para 27 exempts the lower of one-third of
    # *income from employment* or the ceiling. It is a consolidated exemption on
    # the employment income itself, NOT a re-wrapping of the repealed ITO 1984
    # itemised house-rent/medical/conveyance reliefs: it is therefore due to a
    # basic-only employee exactly as it is to one who receives allowances, and
    # it is computed on the employment income alone (`annual_taxable_other`
    # carries non-employment income, which Para 27 does not reach).
    # Set `exemption_ceiling=0` to switch the exemption off for a payee.
    employment_income_annual = (gross - pf["employee"]) * Decimal(12)
    annual_employment_income = employment_income_annual + inp.annual_taxable_other
    ceiling = (
        inp.exemption_ceiling if inp.exemption_ceiling is not None else SALARY_EXEMPTION_CEILING
    )
    exempt_annual = salary_exemption(max(employment_income_annual, Decimal(0)), ceiling=ceiling)

    annual_taxable = annual_employment_income - exempt_annual
    annual_tax = income_tax(
        max(annual_taxable, Decimal(0)),
        category=inp.taxpayer_category,
        disabled_dependents=inp.disabled_dependents,
        location=inp.tax_location,
        allowable_investment=inp.allowable_investment,
    )
    tax_month = q2(annual_tax / Decimal(12))
    net = q2(gross - pf["employee"] - tax_month)
    lines = [
        ("basic", q2(inp.basic_monthly)),
    ]
    if allowances != Decimal("0.00"):
        lines.append(("allowances", allowances))
    lines.extend(
        [
            ("overtime", ot),
            ("incentive", q2(inp.incentive)),
            ("pf_employee", -pf["employee"]),
            ("tax_withheld", -tax_month),
        ]
    )
    return PayslipResult(
        gross=gross,
        basic=q2(inp.basic_monthly),
        overtime=ot,
        incentive=q2(inp.incentive),
        pf_employee=pf["employee"],
        pf_employer=pf["employer"],
        tax_month=tax_month,
        tax_annual_projection=annual_tax,
        net=net,
        allowances_total=allowances,
        annual_exemption=exempt_annual,
        lines=lines,
    )
