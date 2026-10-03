# libs/py/payroll_engine — P08-M03: Bangladesh payroll calculation kernel (L5 pure).
#
# The ONLY calculation authority for M56 (DoD-03: 100% test coverage on every
# payroll calculation path). Stdlib-only, Decimal money, no Odoo imports —
# reachable from the Odoo module (libs.py.* is on PYTHONPATH), from pytest
# and from services/payroll-engine (its canonical L5 service shell).
#
# Statutory basis (all verified 2026-10-03):
#   - Income tax FY 2026-27 (budget of June 2026): tax-free threshold BDT
#     375,000; then 10% on the next 300,000; 15% on the next 400,000;
#     20% on the next 500,000; 25% on the next 2,000,000; 30% on the balance.
#     Sources: PwC Tax Summaries (FY2026/27), The Daily Star (2026-06-16).
#   - Gratuity, Bangladesh Labour (Amendment) Act 2026 (roadmap-verified
#     2026-08-19): 30 days' basic per COMPLETED year of service up to 12
#     years, 45 days' per year above 12.
#   - Voluntary-resignation compensation (same Act): 7 days' wages per year
#     below 5 years' service, 15 days' for 5-<10 years, 30 days' for 10+.
#   - Provident fund: statutory contribution structure (employee %
#     + employer %), trust governance and reporting timelines.
#   - BEFTN (INT-005): batch settlement, final cut-off 16:00; submissions
#     after the cut-off, or on Friday, Saturday or a public holiday, settle
#     the NEXT WORKING DAY. The Bangladesh working week is Sunday-Thursday
#     (BN-007 / BD-01).
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

TWO = Decimal("0.01")

# --- FY 2026-27 income-tax slabs (salaried individuals, general threshold) ---
TAX_FREE_THRESHOLD = Decimal("375000")
TAX_SLABS = [  # (width of the band, rate) applied above the threshold
    (Decimal("300000"), Decimal("0.10")),
    (Decimal("400000"), Decimal("0.15")),
    (Decimal("500000"), Decimal("0.20")),
    (Decimal("2000000"), Decimal("0.25")),
    (None, Decimal("0.30")),            # the balance
]

# --- Labour (Amendment) Act 2026 constants ---
GRATUITY_DAYS_UPTO_12Y = 30            # days of basic per completed year <= 12
GRATUITY_DAYS_ABOVE_12Y = 45           # days of basic per year beyond 12
RESIGNATION_BANDS = [                  # (min completed years, days of wages per year)
    (0, 7), (5, 15), (10, 30),
]

# --- Bangladesh public holidays (fixed-date, 2026-2028) for BEFTN settlement ---
FIXED_HOLIDAYS = {(2, 21), (3, 26), (4, 14), (5, 1), (8, 15), (12, 16), (12, 25)}

WEEKEND = {4, 5}                       # Friday=4, Saturday=5 (Mon=0); Sun-Thu works


def q2(value: Decimal) -> Decimal:
    return value.quantize(TWO, rounding=ROUND_HALF_UP)


def is_working_day(d: date, extra_holidays: set[date] | None = None) -> bool:
    """Sunday-Thursday working week; Friday+Saturday weekend plus holidays."""
    if d.weekday() in WEEKEND:
        return False
    if (d.month, d.day) in FIXED_HOLIDAYS:
        return False
    if extra_holidays and d in extra_holidays:
        return False
    return True


def beftn_settlement_date(submitted: datetime,
                          cutoff_hour: int = 16,
                          extra_holidays: set[date] | None = None) -> date:
    """INT-005 batch model: in before the final cut-off on a working day ->
    same day; otherwise the next working day (Fri/Sat/holiday roll forward)."""
    d = submitted.date()
    if submitted.hour >= cutoff_hour:
        d = d + timedelta(days=1)
    while not is_working_day(d, extra_holidays):
        d = d + timedelta(days=1)
    return d


def income_tax(annual_taxable: Decimal) -> Decimal:
    """FY 2026-27 slab tax. Negative taxable is a caller error."""
    if annual_taxable < 0:
        raise ValueError("taxable income cannot be negative")
    tax = Decimal("0")
    remaining = annual_taxable - TAX_FREE_THRESHOLD
    for width, rate in TAX_SLABS:
        if remaining <= 0:
            break
        band = remaining if width is None else min(remaining, width)
        tax += band * rate
        remaining -= band
    return q2(tax)


def provident_fund(basic: Decimal, employee_pct: Decimal,
                   employer_pct: Decimal) -> dict[str, Decimal]:
    """Statutory PF: both wings of the contribution structure."""
    if employee_pct < 0 or employer_pct < 0:
        raise ValueError("PF percentages cannot be negative")
    return {
        "employee": q2(basic * employee_pct / Decimal(100)),
        "employer": q2(basic * employer_pct / Decimal(100)),
    }


def completed_years(joining: date, as_of: date) -> int:
    """Completed years of service - partial years do NOT count (gratuity)."""
    if as_of < joining:
        raise ValueError("service end before joining")
    years = as_of.year - joining.year
    if (as_of.month, as_of.day) < (joining.month, joining.day):
        years -= 1
    return max(years, 0)


def gratuity(basic_monthly: Decimal, joining: date, separation: date) -> Decimal:
    """Labour (Amendment) Act 2026: 30 days' basic per completed year to 12
    years, 45 days' per year above 12. Daily basic = monthly/30 (the Act's
    convention for monthly-rated workers)."""
    years = completed_years(joining, separation)
    daily = basic_monthly / Decimal(30)
    upto = min(years, 12) * GRATUITY_DAYS_UPTO_12Y
    above = max(years - 12, 0) * GRATUITY_DAYS_ABOVE_12Y
    return q2(daily * (upto + above))


def resignation_compensation(basic_monthly: Decimal, joining: date,
                             separation: date) -> Decimal:
    """Voluntary resignation is compensable under the 2026 Amendment:
    7/15/30 days' wages per completed year by service band."""
    years = completed_years(joining, separation)
    days_per_year = next(
        d for min_years, d in reversed(RESIGNATION_BANDS) if years >= min_years)
    daily = basic_monthly / Decimal(30)
    return q2(daily * days_per_year * years)


# --- overtime per the Labour Act: 2x the basic rate (8h/day, 48h/week cap) --
STANDARD_DAY_HOURS = Decimal("8")


def overtime_amount(basic_monthly: Decimal, ot_hours: Decimal) -> Decimal:
    if ot_hours < 0:
        raise ValueError("overtime hours cannot be negative")
    hourly = basic_monthly / Decimal(30) / STANDARD_DAY_HOURS
    return q2(hourly * Decimal(2) * ot_hours)


@dataclass
class PayslipInput:
    """One employee-month of inputs. Hours come from LOCKED attendance
    (P08-M02-T05: payroll may only calculate on a locked period)."""
    employee_ref: str
    basic_monthly: Decimal
    attendance_hours: Decimal = Decimal("0")
    ot_hours: Decimal = Decimal("0")
    incentive: Decimal = Decimal("0")           # from M57's engine
    pf_employee_pct: Decimal = Decimal("0")
    pf_employer_pct: Decimal = Decimal("0")
    annual_taxable_other: Decimal = Decimal("0")  # YTD taxable outside this slip
    period_days: int = 30


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
    lines: list[tuple[str, Decimal]] = field(default_factory=list)


def compute_payslip(inp: PayslipInput) -> PayslipResult:
    """The monthly calculation path: OT -> gross -> PF on basic -> tax on the
    annualised taxable (slabs) -> net. Tax is withheld monthly on the
    annualised projection (the common BD payroll convention)."""
    if inp.basic_monthly < 0:
        raise ValueError("basic cannot be negative")
    ot = overtime_amount(inp.basic_monthly, inp.ot_hours)
    gross = q2(inp.basic_monthly + ot + inp.incentive)
    pf = provident_fund(inp.basic_monthly, inp.pf_employee_pct, inp.pf_employer_pct)
    annual_taxable = (
        gross - pf["employee"]) * Decimal(12) + inp.annual_taxable_other
    annual_tax = income_tax(max(annual_taxable, Decimal(0)))
    tax_month = q2(annual_tax / Decimal(12))
    net = q2(gross - pf["employee"] - tax_month)
    lines = [
        ("basic", q2(inp.basic_monthly)),
        ("overtime", ot),
        ("incentive", q2(inp.incentive)),
        ("pf_employee", -pf["employee"]),
        ("tax_withheld", -tax_month),
    ]
    return PayslipResult(
        gross=gross, basic=q2(inp.basic_monthly), overtime=ot,
        incentive=q2(inp.incentive), pf_employee=pf["employee"],
        pf_employer=pf["employer"], tax_month=tax_month,
        tax_annual_projection=annual_tax, net=net, lines=lines)
