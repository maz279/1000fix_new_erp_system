"""return_logic — P07-M04-T01/T04 (M51 completion; TSS §14.6; SC-008).

PURE FUNCTIONS: Mushak 9.1 monthly VAT-return preparation and quarterly TDS
returns, with the statutory rules that are easy to get wrong:

  - Due by the 15th; if the 15th is a weekend or a listed holiday, the
    NEXT WORKING DAY (holiday rollover).
  - A NIL RETURN is mandatory when there are no transactions — a
    multi-entity rollout hits this the month a new entity registers.
  - TDS quarters close 25 Oct / 25 Jan / 25 Apr / 25 Jul — statutory dates.
  - Manual filing was abolished 1 July 2026: the only route is online;
    "manual fallback" means keying the NBR portal by hand, not a paper
    return (the runbook states this).

A wrong VAT return is a regulatory event, not a bug (DoD-03): 100% of
return-calculation paths are unit-tested.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

TWO = Decimal("0.01")


class ReturnError(ValueError):
    """Refuse to guess on statutory code."""


# Bangladesh weekend = Friday+Saturday (post-2025 workweek).
WEEKEND_WEEKDAYS = {4, 5}  # Mon=0 .. Fri=4, Sat=5

# Moon-dependent public holidays vary by year and lunar sighting — the
# authoritative calendar is M30's country pack. The engine takes a SET of
# holiday dates as input; it never hard-codes them (the pack owns them).
# Below: fixed-date national holidays observed every year.
FIXED_HOLIDAYS = {
    (2, 21),   # Shaheed Day / Language Martyrs' Day
    (3, 17),   # Sheikh Mujibur Rahman's Birthday
    (3, 26),   # Independence Day
    (4, 14),   # Bengali New Year
    (5, 1),    # May Day
    (8, 15),   # National Mourning Day
    (12, 16),  # Victory Day
    (12, 25),  # Christmas Day
}


@dataclass(frozen=True)
class VatReturnLine:
    """One line of the Mushak 9.1: output tax by treatment."""
    treatment: str
    taxable_value: Decimal
    output_vat: Decimal


@dataclass(frozen=True)
class VatReturn:
    company_bin: str
    period: str                 # YYYY-MM
    lines: tuple
    total_taxable: Decimal
    total_output_vat: Decimal
    total_input_vat: Decimal    # from purchase Mushak 6.3s held
    net_payable: Decimal
    nil_return: bool
    due_date: date


def next_working_day(candidate: date, holidays: set[date]) -> date:
    """Roll forward past weekends and holidays — the holiday-rollover rule."""
    while candidate.weekday() in WEEKEND_WEEKDAYS or candidate in holidays \
            or (candidate.month, candidate.day) in FIXED_HOLIDAYS:
        candidate += timedelta(days=1)
    return candidate


def vat_return_due_date(period: str, holidays: set[date] | None = None) -> date:
    """The 15th of the month after the period; rolled to the next working
    day when it lands on a weekend or holiday."""
    year, month = int(period[:4]), int(period[5:7])
    month_after = month + 1 if month < 12 else 1
    year_after = year if month < 12 else year + 1
    return next_working_day(date(year_after, month_after, 15), holidays or set())


def prepare_vat_return(company_bin: str, period: str,
                       register_totals: dict[str, tuple[Decimal, Decimal]],
                       input_vat: Decimal = Decimal("0"),
                       holidays: set[date] | None = None) -> VatReturn:
    """Prepare the Mushak 9.1 from the register's per-treatment totals.

    register_totals: {treatment: (taxable_value, output_vat)} — normally
    aggregated from fix.mushak.register for the period.
    A period with NO transactions still returns a return with nil_return
    True — the mandatory nil return.
    """
    if not (len(company_bin) == 13 and company_bin.isdigit()):
        raise ReturnError("The company BIN must be 13 digits")
    lines = tuple(
        VatReturnLine(t, Decimal(str(totals[0])).quantize(TWO, ROUND_HALF_UP),
                      Decimal(str(totals[1])).quantize(TWO, ROUND_HALF_UP))
        for t, totals in sorted(register_totals.items())
    )
    total_taxable = sum((l.taxable_value for l in lines), Decimal("0")).quantize(TWO)
    total_output = sum((l.output_vat for l in lines), Decimal("0")).quantize(TWO)
    input_v = Decimal(str(input_vat)).quantize(TWO, ROUND_HALF_UP)
    return VatReturn(
        company_bin=company_bin,
        period=period,
        lines=lines,
        total_taxable=total_taxable,
        total_output_vat=total_output,
        total_input_vat=input_v,
        net_payable=(total_output - input_v).quantize(TWO, ROUND_HALF_UP),
        nil_return=(total_output == 0 and input_v == 0),
        due_date=vat_return_due_date(period, holidays),
    )


# ------------------------------------------------------------------- TDS ----

TDS_QUARTER_DEADLINES = {
    1: (10, 25),   # Q1 (Jul-Sep) -> 25 Oct
    2: (1, 25),    # Q2 (Oct-Dec) -> 25 Jan
    3: (4, 25),    # Q3 (Jan-Mar) -> 25 Apr
    4: (7, 25),    # Q4 (Apr-Jun) -> 25 Jul
}


@dataclass(frozen=True)
class TdsReturn:
    quarter: str               # e.g. "2026-Q1"
    fiscal_year: str           # FY starts 1 July (BD fiscal year)
    total_withheld: Decimal
    deductor_count: int
    due_date: date


def tds_quarter_for_date(d: date) -> tuple[str, str]:
    """Map a calendar date to (quarter, fiscal-year). BD fiscal year runs
    1 July -> 30 June: FY2027 = 1 Jul 2026 - 30 Jun 2027.
    Quarters: Jul-Sep=Q1, Oct-Dec=Q2, Jan-Mar=Q3, Apr-Jun=Q4."""
    fy_start_year = d.year if d.month >= 7 else d.year - 1
    fiscal_year = "FY%d" % (fy_start_year + 1)
    quarter = ((d.month + 5) % 12) // 3 + 1
    return "%d-Q%d" % (fy_start_year, quarter), fiscal_year


def tds_return_due_date(quarter: str, holidays: set[date] | None = None) -> date:
    """The statutory quarter deadlines: 25 Oct / 25 Jan / 25 Apr / 25 Jul,
    rolled forward over weekends/holidays. The quarter label carries the
    FY-START year (e.g. 2026-Q2 = Oct-Dec 2026): Q2 and Q3 deadlines fall
    in the FOLLOWING calendar year."""
    fy_start = int(quarter[:4])
    q = int(quarter[-1])
    deadline_year = fy_start if q == 1 else fy_start + 1
    month, day = TDS_QUARTER_DEADLINES[q]
    return next_working_day(date(deadline_year, month, day), holidays or set())


def prepare_tds_return(withheld_totals: dict[str, Decimal],
                       any_date_in_quarter: date,
                       holidays: set[date] | None = None) -> TdsReturn:
    quarter, fiscal_year = tds_quarter_for_date(any_date_in_quarter)
    total = sum((Decimal(str(v)) for v in withheld_totals.values()),
                Decimal("0")).quantize(TWO, ROUND_HALF_UP)
    if total < 0:
        raise ReturnError("withheld total cannot be negative")
    return TdsReturn(
        quarter=quarter, fiscal_year=fiscal_year,
        total_withheld=total, deductor_count=len(withheld_totals),
        due_date=tds_return_due_date(quarter, holidays),
    )
