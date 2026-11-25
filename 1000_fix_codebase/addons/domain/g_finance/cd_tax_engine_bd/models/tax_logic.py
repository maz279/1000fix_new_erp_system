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

ZERO = Decimal("0")
TWO_PLACES = Decimal("0.01")


@dataclass(frozen=True)
class VatRates:
    """The VAT rates in force, as the effective-dated master (fix.tax.rate)
    holds them on the supply date (A08 M51-5, BRU-TAX-01): the Odoo layer
    reads them (fix.vat.treatment._fix_determine_tax) and passes them in."""

    standard: Decimal
    reduced: frozenset = frozenset()
    source: str = "master"


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
    rates_source: str = "master"

    @property
    def requires_mushak(self) -> bool:
        """A Mushak 6.3 must be issued when VAT applies to any line OR the
        supply value exceeds BDT 25,000 (mandatory-invoice threshold)."""
        return any(line.vat_amount > 0 for line in self.lines) or self.total_taxable > Decimal(
            "25000"
        )


def _rate_for(line: TaxLine, rates: VatRates) -> tuple[str, Decimal]:
    if line.treatment and line.treatment not in VALID_TREATMENTS:
        raise DeterminationError(f"unknown treatment {line.treatment!r}")
    treatment = line.treatment or "standard_15"
    standard = Decimal(str(rates.standard))
    reduced = {Decimal(str(r)) for r in rates.reduced}
    if line.rate_override is not None:
        rate = Decimal(str(line.rate_override))
        if treatment == "standard_15" and rate != standard:
            raise DeterminationError("the standard rate cannot be overridden")
        if treatment == "reduced" and rate not in reduced:
            raise DeterminationError(f"reduced rate {rate} is not a scheduled rate")
        if treatment in ("zero_rated", "exempt") and rate != ZERO:
            raise DeterminationError(f"{treatment} rate must be zero")
        return treatment, rate
    if treatment == "reduced":
        # a reduced supply names its scheduled rate (tariff row); never guessed
        raise DeterminationError(
            f"reduced-rate line {line.product_code!r} carries no scheduled rate"
        )
    return {
        "standard_15": (treatment, standard),
        "zero_rated": (treatment, ZERO),
        "exempt": (treatment, ZERO),
        "truncated": (treatment, ZERO),  # fixed base handled by tariff config
    }[treatment]


def determine_tax(lines: list[TaxLine], rates: VatRates | None = None) -> Determination:
    """The synchronous determination API (AR-006 §4.2 worked example).

    The rates are the effective-dated master's, always passed in (BRU-TAX-01):
    env["fix.vat.treatment"]._fix_determine_tax(lines, on_date, company) reads
    them; there is no rate in this code to fall back on.

    Rounding is half-up at TWO decimal places per line — per-line rounding,
    never on the total, is where silent money loss is prevented (P06-M03-T08).
    """
    if rates is None:
        raise DeterminationError(
            "the VAT rates in force were not passed: call "
            "fix.vat.treatment._fix_determine_tax, which reads the Tax Rate Master"
        )
    if rates.standard is None or Decimal(str(rates.standard)) <= 0:
        raise DeterminationError("no standard VAT rate in force (Tax Rate Master)")
    determined: list[DeterminedLine] = []
    total_taxable = total_vat = ZERO
    has_truncated = False
    for line in lines:
        treatment, rate = _rate_for(line, rates)
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
        rates_source=rates.source,
    )


# ------------------------------------------------------------------- TDS ----
# A08 M51-5 (T06): the in-code TDS schedule (TDS_DEFAULT_RATES /
# determine_tds) disagreed with the effective-dated master on rent,
# contractor and professional fees and was called by nothing. Withholding is
# determined ONLY from fix.tax.rate (cd_ap_ext reads find_rate); there is no
# second schedule.
