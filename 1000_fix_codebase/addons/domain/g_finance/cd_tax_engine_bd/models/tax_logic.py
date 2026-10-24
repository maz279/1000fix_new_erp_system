"""VAT determination — the M51-core tax engine (P06-M02-T02, MV-03).

PURE FUNCTIONS, no Odoo imports: unit-testable without a database, and
callable from the pricing engine, the billing engine and M52 synchronously
(AR-006 §4.1 pair 7/8 — the call direction is M20/M52 -> M51, always).

Treatments under the VAT & SD Act 2012 (verified 2026-10; DoD-17 record in
docs/p06/vat-reading-record.md):

  standard_15   — 15% standard rate (the estate default for services)
  reduced_N     — reduced rates (5 / 7.5 / 10) on scheduled supplies
  zero_rated    — 0% with input credit (exports)
  exempt        — no output VAT, no input credit
  truncated     — fixed-rate base for specified services (no input credit)

The default catalogue service line is standard_15 unless the tariff entry
says otherwise; the tariff itself loads from M30's country pack (T06 — the
dependency is cd_entity_config's fix.country.pack, never M65).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

STANDARD_RATE = Decimal("15")
REDUCED_RATES = {Decimal("5"), Decimal("7.5"), Decimal("10")}
ZERO = Decimal("0")
TWO_PLACES = Decimal("0.01")

VALID_TREATMENTS = ("standard_15", "reduced", "zero_rated", "exempt", "truncated")


class DeterminationError(ValueError):
    """An input the engine refuses to guess on. Statutory code never
    silently defaults — a malformed line raises."""


@dataclass(frozen=True)
class TaxLine:
    """One invoice line in, one determined line out."""

    product_code: str
    qty: Decimal
    unit_price: Decimal  # exclusive of VAT
    discount: Decimal = ZERO
    hs_code: str = ""  # tariff lookup key where applicable
    treatment: str = ""  # override; empty = tariff/standard default
    rate_override: Decimal | None = None

    def __post_init__(self) -> None:
        if self.qty < 0 or self.unit_price < 0 or self.discount < 0:
            raise DeterminationError(f"negative value on line {self.product_code!r}")
        if self.discount > self.qty * self.unit_price:
            raise DeterminationError(f"discount exceeds line amount on {self.product_code!r}")


@dataclass(frozen=True)
class DeterminedLine:
    product_code: str
    treatment: str
    rate: Decimal
    taxable_amount: Decimal
    vat_amount: Decimal
    line_total: Decimal  # taxable + VAT


@dataclass(frozen=True)
class Determination:
    """determine_tax(line_set) -> treatment set (the M51 public API)."""

    lines: list[DeterminedLine] = field(default_factory=list)
    total_taxable: Decimal = ZERO
    total_vat: Decimal = ZERO
    total_payable: Decimal = ZERO
    # Truncated-value supplies never enter the VAT register as calculated
    # VAT — they carry their fixed base separately (Mushak register reads
    # this flag).
    has_truncated: bool = False

    @property
    def requires_mushak(self) -> bool:
        """A Mushak 6.3 must be issued when VAT applies to any line OR the
        supply value exceeds BDT 25,000 (mandatory-invoice threshold)."""
        return any(line.vat_amount > 0 for line in self.lines) or self.total_taxable > Decimal(
            "25000"
        )


def _rate_for(line: TaxLine) -> tuple[str, Decimal]:
    if line.treatment and line.treatment not in VALID_TREATMENTS:
        raise DeterminationError(f"unknown treatment {line.treatment!r}")
    treatment = line.treatment or "standard_15"
    if line.rate_override is not None:
        rate = Decimal(str(line.rate_override))
        if treatment == "standard_15" and rate != STANDARD_RATE:
            raise DeterminationError("standard_15 rate cannot be overridden")
        if treatment == "reduced" and rate not in REDUCED_RATES:
            raise DeterminationError(f"reduced rate {rate} is not a scheduled rate")
        if treatment in ("zero_rated", "exempt") and rate != ZERO:
            raise DeterminationError(f"{treatment} rate must be zero")
        return treatment, rate
    return {
        "standard_15": (treatment, STANDARD_RATE),
        "reduced": (treatment, Decimal("5")),  # default reduced; tariff may set 7.5/10
        "zero_rated": (treatment, ZERO),
        "exempt": (treatment, ZERO),
        "truncated": (treatment, ZERO),  # fixed base handled by tariff config
    }[treatment]


def determine_tax(lines: list[TaxLine]) -> Determination:
    """The synchronous determination API (AR-006 §4.2 worked example).

    Rounding is half-up at TWO decimal places per line — per-line rounding,
    never on the total, is where silent money loss is prevented (P06-M03-T08).
    """
    determined: list[DeterminedLine] = []
    total_taxable = total_vat = ZERO
    has_truncated = False
    for line in lines:
        treatment, rate = _rate_for(line)
        gross = (line.qty * line.unit_price).quantize(TWO_PLACES, ROUND_HALF_UP)
        taxable = (gross - line.discount).quantize(TWO_PLACES, ROUND_HALF_UP)
        vat = (taxable * rate / Decimal("100")).quantize(TWO_PLACES, ROUND_HALF_UP)
        determined.append(
            DeterminedLine(
                product_code=line.product_code,
                treatment=treatment,
                rate=rate,
                taxable_amount=taxable,
                vat_amount=vat,
                line_total=taxable + vat,
            )
        )
        total_taxable += taxable
        total_vat += vat
        if treatment == "truncated":
            has_truncated = True
    return Determination(
        lines=determined,
        total_taxable=total_taxable,
        total_vat=total_vat,
        total_payable=total_taxable + total_vat,
        has_truncated=has_truncated,
    )


# ------------------------------------------------------------------- TDS ----

# Bangladesh TDS schedule (VAT & SD Act / Income Tax Ordinance rates in
# common service use; the authoritative schedule is the country pack — these
# are the engine defaults the pack overrides).
TDS_DEFAULT_RATES: dict[str, Decimal] = {
    "rent_commercial": Decimal("15"),
    "service_general": Decimal("10"),
    "service_contractor": Decimal("7.5"),
    "professional_fees": Decimal("10"),
    "commission": Decimal("10"),
    "supply_of_goods": Decimal("5"),
    "transport": Decimal("3"),
}


@dataclass(frozen=True)
class TdsDetermination:
    category: str
    base_amount: Decimal
    rate: Decimal
    tds_amount: Decimal
    exempt: bool = False


def determine_tds(
    category: str, base_amount: Decimal, exempt_certificate: bool = False
) -> TdsDetermination:
    """M52 calls this synchronously before posting a vendor bill (pair 8).

    An exempt-certificate holder (ATS) suffers no deduction; the certificate
    number is captured by the caller, not the engine."""
    if base_amount < 0:
        raise DeterminationError("negative TDS base")
    if category not in TDS_DEFAULT_RATES:
        raise DeterminationError(
            f"unknown TDS category {category!r} — the schedule must name it "
            "(never guess a rate on statutory money)"
        )
    rate = TDS_DEFAULT_RATES[category]
    amount = (
        ZERO
        if exempt_certificate
        else (base_amount * rate / Decimal("100")).quantize(TWO_PLACES, ROUND_HALF_UP)
    )
    return TdsDetermination(
        category=category,
        base_amount=base_amount,
        rate=rate,
        tds_amount=amount,
        exempt=exempt_certificate,
    )
