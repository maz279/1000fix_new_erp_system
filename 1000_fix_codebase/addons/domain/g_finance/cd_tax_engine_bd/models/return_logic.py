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
    (2, 21),  # Shaheed Day / Language Martyrs' Day
    (3, 17),  # Sheikh Mujibur Rahman's Birthday
    (3, 26),  # Independence Day
    (4, 14),  # Bengali New Year
    (5, 1),  # May Day
    (8, 15),  # National Mourning Day
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
    period: str  # YYYY-MM
    lines: tuple
    total_taxable: Decimal
    total_output_vat: Decimal
    total_input_vat: Decimal  # from purchase Mushak 6.3s held
    net_payable: Decimal
    nil_return: bool
    due_date: date


def next_working_day(candidate: date, holidays: set[date]) -> date:
    """Roll forward past weekends and holidays — the holiday-rollover rule."""
    while (
        candidate.weekday() in WEEKEND_WEEKDAYS
        or candidate in holidays
        or (candidate.month, candidate.day) in FIXED_HOLIDAYS
    ):
        candidate += timedelta(days=1)
    return candidate


def vat_return_due_date(period: str, holidays: set[date] | None = None) -> date:
    """The 15th of the month after the period; rolled to the next working
    day when it lands on a weekend or holiday."""
    year, month = int(period[:4]), int(period[5:7])
    month_after = month + 1 if month < 12 else 1
    year_after = year if month < 12 else year + 1
    return next_working_day(date(year_after, month_after, 15), holidays or set())


def prepare_vat_return(
    company_bin: str,
    period: str,
    register_totals: dict[str, tuple[Decimal, Decimal]],
    input_vat: Decimal = Decimal("0"),
    holidays: set[date] | None = None,
) -> VatReturn:
    """Prepare the Mushak 9.1 from the register's per-treatment totals.

    register_totals: {treatment: (taxable_value, output_vat)} — normally
    aggregated from fix.mushak.register for the period.
    A period with NO transactions still returns a return with nil_return
    True — the mandatory nil return.
    """
    if not (len(company_bin) == 13 and company_bin.isdigit()):
        raise ReturnError("The company BIN must be 13 digits")
    lines = tuple(
        VatReturnLine(
            t,
            Decimal(str(totals[0])).quantize(TWO, ROUND_HALF_UP),
            Decimal(str(totals[1])).quantize(TWO, ROUND_HALF_UP),
        )
        for t, totals in sorted(register_totals.items())
    )
    total_taxable = sum((line.taxable_value for line in lines), Decimal("0")).quantize(TWO)
    total_output = sum((line.output_vat for line in lines), Decimal("0")).quantize(TWO)
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


# ------------------------------------------------- register classification ----

# The ad-valorem rates that identify exactly one treatment (15% is only ever
# the standard rate; 5 / 7.5 / 10 only ever the scheduled reduced rates).
_RATE_TREATMENTS = {
    Decimal("15"): "standard_15",
    Decimal("10"): "reduced_10",
    Decimal("7.5"): "reduced_7.5",
    Decimal("5"): "reduced_5",
}
UNCLASSIFIED_PREFIX = "unclassified"


def _rate_key(rate: Decimal) -> str:
    return format(rate.normalize(), "f")


def _summary_treatments(summary: str) -> set[str]:
    """Treatment keys named in a register row's ``treatment_summary``
    (lines "<product>: <treatment> @ <rate>%", as written by M20)."""
    keys: set[str] = set()
    for raw in (summary or "").splitlines():
        line = raw.strip()
        if not line or ":" not in line or "@" not in line:
            continue
        treatment_part, _, rate_part = line.rsplit(":", 1)[1].partition("@")
        treatment = treatment_part.strip()
        if not treatment:
            continue
        if treatment == "reduced":
            try:
                rate = Decimal(rate_part.strip().rstrip("%").strip())
            except ArithmeticError:
                return set()  # unreadable rate: the summary cannot classify
            keys.add(f"reduced_{_rate_key(rate)}")
        else:
            keys.add(treatment)
    return keys


def _treatment_rate(key: str) -> Decimal | None:
    """The VAT rate a treatment key itself declares, when it names one —
    ``standard_15`` 15, ``reduced_<r>`` r, the 0% treatments 0; anything else
    (``zero_or_exempt`` and unknown keys) names no rate."""
    if key == "standard_15":
        return Decimal("15")
    if key.startswith("reduced_"):
        try:
            return Decimal(key[len("reduced_") :])
        except ArithmeticError:
            return None
    if key in ("zero_rated", "exempt", "truncated"):
        return Decimal("0")
    return None


def classify_register_row(taxable: Decimal | float, vat: Decimal | float, summary: str = "") -> str:
    """The Mushak 9.1 line a register row belongs to — never a silent default.

    1. The row's own ``treatment_summary``: when every line names the same
       treatment AND the row's amounts agree with that treatment's rate
       (within a paisa of rounding), the row is that treatment
       (``standard_15``, ``reduced_<rate>``, ``zero_rated``, ``exempt``,
       ``truncated``). A named treatment whose amounts disagree — e.g. a
       summary that omits a 0% line while the row's VAT is short of the
       standard rate — is NOT trusted: the row is flagged, never folded.
    2. A row WITHOUT a summary: its effective rate, when that identifies
       exactly one treatment (15 / 10 / 7.5 / 5 %, within a paisa of rounding).
    3. Anything else is summed per actual rate and visibly flagged, NOT folded
       into the standard line: ``unclassified_mixed_rate_<r>`` for a row mixing
       treatments (the register keeps only row totals, not per-line amounts),
       ``unclassified_rate_<r>`` for a summary-less row at a non-identifying
       rate — including 0%, where zero-rated, exempt and truncated supplies
       are indistinguishable.
    """
    taxable_d = Decimal(str(taxable or 0))
    vat_d = Decimal(str(vat or 0))
    named = _summary_treatments(summary)
    if len(named) == 1:
        only = next(iter(named))
        rate = _treatment_rate(only)
        if rate is not None and abs(vat_d - taxable_d * rate / 100) <= TWO:
            return only
        # The amounts disagree with the named treatment, or the key names no
        # rate (zero_or_exempt: the 0% kind is unknown): fall through to the
        # flagged paths — a summary is corroborated, never blindly trusted.
    if taxable_d == 0:
        return f"{UNCLASSIFIED_PREFIX}_rate_0" if vat_d == 0 else f"{UNCLASSIFIED_PREFIX}_vat_only"
    effective = (vat_d * 100 / taxable_d).quantize(TWO, ROUND_HALF_UP)
    if named:
        # Several treatments on one row: its blended rate can coincide with a
        # scheduled rate (15% + exempt halves to 7.5%), so it is never inferred.
        return f"{UNCLASSIFIED_PREFIX}_mixed_rate_{_rate_key(effective)}"
    for rate, key in _RATE_TREATMENTS.items():
        if abs(vat_d - taxable_d * rate / 100) <= TWO:
            return key
    return f"{UNCLASSIFIED_PREFIX}_rate_{_rate_key(effective)}"


def aggregate_register(
    rows: list[tuple[Decimal | float, Decimal | float, str]],
) -> dict[str, tuple[Decimal, Decimal]]:
    """Sum (taxable, vat, treatment_summary) register rows per Mushak 9.1
    treatment line (see classify_register_row)."""
    totals: dict[str, tuple[Decimal, Decimal]] = {}
    for taxable, vat, summary in rows:
        key = classify_register_row(taxable, vat, summary)
        t, v = totals.get(key, (Decimal("0"), Decimal("0")))
        totals[key] = (t + Decimal(str(taxable or 0)), v + Decimal(str(vat or 0)))
    return totals


# ------------------------------------------------------------------- TDS ----

TDS_QUARTER_DEADLINES = {
    1: (10, 25),  # Q1 (Jul-Sep) -> 25 Oct
    2: (1, 25),  # Q2 (Oct-Dec) -> 25 Jan
    3: (4, 25),  # Q3 (Jan-Mar) -> 25 Apr
    4: (7, 25),  # Q4 (Apr-Jun) -> 25 Jul
}


@dataclass(frozen=True)
class TdsReturn:
    quarter: str  # e.g. "2026-Q1"
    fiscal_year: str  # FY starts 1 July (BD fiscal year)
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


def prepare_tds_return(
    withheld_totals: dict[str, Decimal],
    any_date_in_quarter: date,
    holidays: set[date] | None = None,
) -> TdsReturn:
    quarter, fiscal_year = tds_quarter_for_date(any_date_in_quarter)
    total = sum((Decimal(str(v)) for v in withheld_totals.values()), Decimal("0")).quantize(
        TWO, ROUND_HALF_UP
    )
    if total < 0:
        raise ReturnError("withheld total cannot be negative")
    return TdsReturn(
        quarter=quarter,
        fiscal_year=fiscal_year,
        total_withheld=total,
        deductor_count=len(withheld_totals),
        due_date=tds_return_due_date(quarter, holidays),
    )


# --------------------------------------------------- Sub-Ledger Reconciliation ----


@dataclass(frozen=True)
class SubledgerReconciliation:
    period: str
    subledger_output_vat: Decimal
    gl_output_vat: Decimal
    output_vat_variance: Decimal
    subledger_input_vat: Decimal
    gl_input_vat: Decimal
    input_vat_variance: Decimal
    is_reconciled: bool
    status: str  # "RECONCILED" | "VARIANCE_DETECTED"
    variance_reason: str = ""

    @property
    def output_variance(self) -> Decimal:
        return self.output_vat_variance

    @property
    def input_variance(self) -> Decimal:
        return self.input_vat_variance

    @property
    def notes(self) -> list[str]:
        return [r.strip() for r in self.variance_reason.split(";") if r.strip()]


def reconcile_vat_subledger(
    period: str,
    subledger_output_vat: Decimal | float | int | None = None,
    gl_output_vat: Decimal | float | int | None = None,
    subledger_input_vat: Decimal | float | int | None = None,
    gl_input_vat: Decimal | float | int | None = None,
    register_output_vat: Decimal | float | int | None = None,
    gl_210100_output_vat: Decimal | float | int | None = None,
    register_input_vat: Decimal | float | int | None = None,
    gl_110500_input_vat: Decimal | float | int | None = None,
    output_account_code: str | None = None,
    input_account_code: str | None = None,
) -> SubledgerReconciliation:
    """T02: Strict comparison between operational VAT sub-ledgers and General Ledger accounts.
    Output VAT: fix.mushak.register vs the configured VAT output account.
    Input VAT: purchase bills vs the configured VAT input account.
    The variance message names the accounts actually reconciled
    (`output_account_code` / `input_account_code`; fix_real: 200902 / 200901),
    never a hard-coded chart code. (The gl_210100 / gl_110500 keyword names are
    kept for callers; they carry whatever account the return reconciled.)
    Variances are never silently absorbed (IRB-09 zero-absorption mandate)."""
    raw_out_sub = register_output_vat if register_output_vat is not None else subledger_output_vat
    raw_out_gl = gl_210100_output_vat if gl_210100_output_vat is not None else gl_output_vat
    raw_in_sub = register_input_vat if register_input_vat is not None else subledger_input_vat
    raw_in_gl = gl_110500_input_vat if gl_110500_input_vat is not None else gl_input_vat

    out_sub = Decimal(str(raw_out_sub or 0)).quantize(TWO, ROUND_HALF_UP)
    out_gl = Decimal(str(raw_out_gl or 0)).quantize(TWO, ROUND_HALF_UP)
    in_sub = Decimal(str(raw_in_sub or 0)).quantize(TWO, ROUND_HALF_UP)
    in_gl = Decimal(str(raw_in_gl or 0)).quantize(TWO, ROUND_HALF_UP)

    out_var = (out_sub - out_gl).quantize(TWO, ROUND_HALF_UP)
    in_var = (in_sub - in_gl).quantize(TWO, ROUND_HALF_UP)
    is_rec = out_var == 0 and in_var == 0
    status = "RECONCILED" if is_rec else "VARIANCE_DETECTED"
    reasons: list[str] = []
    out_name = output_account_code or "VAT output account"
    in_name = input_account_code or "VAT input account"
    if out_var != 0:
        reasons.append(
            f"GL {out_name} Output VAT variance: subledger={out_sub}, gl={out_gl}, delta={out_var}"
        )
    if in_var != 0:
        reasons.append(
            f"GL {in_name} Input VAT variance: subledger={in_sub}, gl={in_gl}, delta={in_var}"
        )

    return SubledgerReconciliation(
        period=period,
        subledger_output_vat=out_sub,
        gl_output_vat=out_gl,
        output_vat_variance=out_var,
        subledger_input_vat=in_sub,
        gl_input_vat=in_gl,
        input_vat_variance=in_var,
        is_reconciled=is_rec,
        status=status,
        variance_reason="; ".join(reasons),
    )


# --------------------------------------------------- Statutory TDS Sections ----

TDS_SECTION_RATES = {
    "52": Decimal("0.05"),
    "sec_52": Decimal("0.05"),
    "52AA": Decimal("0.10"),
    "52aa": Decimal("0.10"),
    "sec_52aa": Decimal("0.10"),
    "53A": Decimal("0.05"),
    "53a": Decimal("0.05"),
    "sec_53a": Decimal("0.05"),
    "53F": Decimal("0.10"),
    "53f": Decimal("0.10"),
    "sec_53f": Decimal("0.10"),
    "56": Decimal("0.20"),
    "sec_56": Decimal("0.20"),
}


@dataclass(frozen=True)
class TdsLine:
    vendor_tin: str
    vendor_name: str
    section: str = ""
    section_code: str = ""
    base_amount: Decimal = Decimal("0")
    withheld_amount: Decimal = Decimal("0")
    tds_amount: Decimal = Decimal("0")
    rate: Decimal = Decimal("0")
    rate_percent: Decimal = Decimal("0")
    vendor_bin: str = ""
    challan_no: str = ""
    challan_date: str | date = ""

    def __post_init__(self) -> None:
        sec = self.section_code or self.section or "52"
        object.__setattr__(self, "section", sec)
        object.__setattr__(self, "section_code", sec)

        base = Decimal(str(self.base_amount or 0))
        object.__setattr__(self, "base_amount", base)

        withheld = Decimal(str(self.tds_amount or self.withheld_amount or 0))
        object.__setattr__(self, "withheld_amount", withheld)
        object.__setattr__(self, "tds_amount", withheld)

        if base < 0 or withheld < 0:
            raise ReturnError("TDS amounts cannot be negative")
        if sec not in TDS_SECTION_RATES:
            raise ReturnError(f"Unknown TDS statutory section {sec!r}")


# --------------------------------------------------- Mushak 6.6 VDS Certificate ----


@dataclass(frozen=True)
class VdsCertificateData:
    """Statutory Mushak 6.6 layout under Rule 40(1)/(2) of VAT & SD Rules 2016."""

    certificate_no: str
    issue_date: date
    deductor_bin: str
    deductor_name: str
    deductee_bin: str
    deductee_name: str
    supplier_invoice_no: str
    supplier_invoice_date: date
    total_invoice_amount: Decimal
    vat_amount: Decimal
    vds_amount: Decimal
    treasury_challan_no: str
    treasury_challan_date: date
    supplier_address: str = ""
    bank_branch: str = ""
    vat_rate: Decimal = Decimal("0.15")

    @property
    def supplier_bin(self) -> str:
        return self.deductee_bin

    @property
    def supplier_name(self) -> str:
        return self.deductee_name

    @property
    def net_payable_to_supplier(self) -> Decimal:
        return (self.total_invoice_amount + self.vat_amount - self.vds_amount).quantize(TWO)


def prepare_vds_certificate(
    certificate_no: str,
    issue_date: date | None = None,
    deductor_bin: str = "",
    deductor_name: str = "",
    deductee_bin: str = "",
    deductee_name: str = "",
    customer_bin: str = "",
    customer_name: str = "",
    supplier_bin: str = "",
    supplier_name: str = "",
    supplier_address: str = "",
    invoice_no: str = "",
    invoice_date: date | None = None,
    total_amount: Decimal | float | int | None = None,
    taxable_amount: Decimal | float | int | None = None,
    vat_rate: Decimal | float | int = Decimal("0.15"),
    vat_amount: Decimal | float | int = Decimal("0"),
    vds_amount: Decimal | float | int = Decimal("0"),
    challan_no: str = "",
    treasury_challan_no: str = "",
    challan_date: date | None = None,
    treasury_challan_date: date | None = None,
    bank_branch: str = "",
) -> VdsCertificateData:
    """Validate and construct Mushak 6.6 VDS certificate data per Rule 40."""
    eff_deductor_bin = (deductor_bin or customer_bin or "").strip()
    eff_deductor_name = (deductor_name or customer_name or "1000 FiX Services Ltd.").strip()
    eff_deductee_bin = (deductee_bin or supplier_bin or "").strip()
    eff_deductee_name = (deductee_name or supplier_name or "").strip()

    if not (len(eff_deductor_bin) == 13 and eff_deductor_bin.isdigit()):
        raise ReturnError("Deductor BIN must be 13 digits")
    if not (len(eff_deductee_bin) == 13 and eff_deductee_bin.isdigit()):
        raise ReturnError("Deductee BIN must be 13 digits under Rule 40(1)")

    raw_tot = total_amount if total_amount is not None else taxable_amount
    tot = Decimal(str(raw_tot or 0)).quantize(TWO, ROUND_HALF_UP)
    vat = Decimal(str(vat_amount or 0)).quantize(TWO, ROUND_HALF_UP)
    vds = Decimal(str(vds_amount or 0)).quantize(TWO, ROUND_HALF_UP)

    if vds <= 0 or vds > vat:
        raise ReturnError("VDS amount must be positive and cannot exceed total VAT")

    return VdsCertificateData(
        certificate_no=certificate_no,
        issue_date=issue_date or date.today(),
        deductor_bin=eff_deductor_bin,
        deductor_name=eff_deductor_name,
        deductee_bin=eff_deductee_bin,
        deductee_name=eff_deductee_name,
        supplier_invoice_no=invoice_no,
        supplier_invoice_date=invoice_date or date.today(),
        total_invoice_amount=tot,
        vat_amount=vat,
        vds_amount=vds,
        treasury_challan_no=treasury_challan_no or challan_no,
        treasury_challan_date=treasury_challan_date or challan_date or date.today(),
        supplier_address=supplier_address,
        bank_branch=bank_branch,
        vat_rate=Decimal(str(vat_rate)),
    )
