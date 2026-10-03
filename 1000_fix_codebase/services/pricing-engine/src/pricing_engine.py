"""pricing-engine — P06-M06-T02 (CD-M11-01; TSS §20.2 W3; AR-007 §3.1).

An L5 standalone service: PURE COMPUTATION, no database, no Odoo imports,
unit-testable anywhere (100% of price-calculation paths — DoD-03; pricing
is a financial path).

Price resolution order (M11):
  1. CONTRACT rate — an active contract rate card line for the customer's
     tier wins over everything (a signed promise).
  2. CUSTOMER-TIER rate card — the customer's tier in the standard card.
  3. CATALOGUE list price.
Then, in order: line discount (capped by governance), tier privilege
  discount on LABOUR ONLY (BRU-LOY-01), loyalty points redemption
  (M10 seam — closed here; redemption is a payment instrument, excluded
  from the stacked-discount cap), and the stacked-discount cap on
  DISCOUNTS only (BRU-LOY-09).

Every step emits an audit trail entry — a price is explainable after the
fact, always (governance, not convenience).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

TWO = Decimal("0.01")
STACK_CAP_DEFAULT = Decimal("30")  # BRU-LOY-09: max aggregate discount %


class PricingError(ValueError):
    """Refuse to guess. An unknown product/tier is an error, never a
    fallback to list price."""


@dataclass(frozen=True)
class RateCardLine:
    product_code: str
    line_type: str            # "labour" | "part" | "consumable" | "transport"
    unit_price: Decimal       # the tier/contract rate, VAT-exclusive
    min_tier: int = 0         # customer tier >= min_tier applies (contract = tier 99)
    valid_from: str = ""      # ISO date; empty = always
    valid_to: str = ""


@dataclass(frozen=True)
class PriceRequestLine:
    product_code: str
    qty: Decimal
    line_type: str


@dataclass(frozen=True)
class PriceRequest:
    customer_tier: int = 0
    contract_no: str = ""                     # a contract rate card lookup key
    lines: tuple[PriceRequestLine, ...] = ()
    line_discount_pct: Decimal = Decimal("0") # agent-entered, governance-capped
    loyalty_points_to_redeem: int = 0
    point_value: Decimal = Decimal("1")       # BDT per point (from M10 config)
    stack_cap_pct: Decimal = STACK_CAP_DEFAULT


@dataclass(frozen=True)
class PricedLine:
    product_code: str
    line_type: str
    qty: Decimal
    unit_price: Decimal
    gross: Decimal
    discount_amount: Decimal
    privilege_amount: Decimal
    net: Decimal
    basis: str = "catalogue"


@dataclass
class PriceResult:
    lines: list[PricedLine] = field(default_factory=list)
    subtotal: Decimal = Decimal("0")
    total_discount: Decimal = Decimal("0")
    total_privilege: Decimal = Decimal("0")
    loyalty_credit: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    audit: list[str] = field(default_factory=list)


def _resolve_rate(product_code: str, tier: int, has_contract: bool,
                  cards: list[RateCardLine]) -> Optional[RateCardLine]:
    """Contract rate > tier rate > None (catalogue). A contract line
    applies regardless of the customer's tier — a signed contract is not a
    tier entitlement."""
    if has_contract:
        contract_lines = [
            c for c in cards if c.product_code == product_code and c.min_tier == 99
        ]
        if contract_lines:
            return contract_lines[0]
    candidates = [
        c for c in cards
        if c.product_code == product_code and c.min_tier < 99 and tier >= c.min_tier
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda c: c.min_tier)


def price(request: PriceRequest, rate_cards: list[RateCardLine],
          catalogue_prices: dict[str, Decimal]) -> PriceResult:
    """Resolve a full price request. Deterministic; every reduction is
    explained in the audit trail."""
    result = PriceResult()
    has_contract = bool(request.contract_no)

    for line in request.lines:
        rate = _resolve_rate(line.product_code, request.customer_tier,
                             has_contract, rate_cards)
        if rate is not None:
            unit, basis = rate.unit_price, (
                "contract" if rate.min_tier == 99 and has_contract else "tier")
        elif line.product_code in catalogue_prices:
            unit, basis = catalogue_prices[line.product_code], "catalogue"
        else:
            raise PricingError(
                f"no rate for {line.product_code!r} at tier {request.customer_tier} "
                "— pricing never guesses (add the card line or the catalogue price)")

        gross = (line.qty * unit).quantize(TWO, ROUND_HALF_UP)

        # Governance cap on the agent-entered line discount.
        discount = (gross * request.line_discount_pct / Decimal("100")).quantize(
            TWO, ROUND_HALF_UP)

        # BRU-LOY-01: privilege discount applies to LABOUR ONLY.
        privilege = Decimal("0")
        if line.line_type == "labour" and request.customer_tier > 0:
            pct = min(Decimal(str(request.customer_tier)) * Decimal("2.5"),
                      Decimal("15"))  # tier 1..6 -> 2.5%..15%
            privilege = (gross * pct / Decimal("100")).quantize(TWO, ROUND_HALF_UP)

        net = gross - discount - privilege
        result.lines.append(PricedLine(
            product_code=line.product_code, line_type=line.line_type,
            qty=line.qty, unit_price=unit, gross=gross,
            discount_amount=discount, privilege_amount=privilege, net=net,
            basis=basis))
        result.audit.append(
            "%s: %s @ %s x %s = %s; disc %s; priv %s -> %s"
            % (line.product_code, basis, unit, line.qty, gross,
               discount, privilege, net))

        result.subtotal += gross
        result.total_discount += discount
        result.total_privilege += privilege

    # Loyalty redemption (M10 seam, T04): points convert to a credit at the
    # configured point value; the credit can never push the total negative.
    loyalty_credit = (Decimal(request.loyalty_points_to_redeem)
                      * request.point_value).quantize(TWO, ROUND_HALF_UP)
    pre_total = result.subtotal - result.total_discount - result.total_privilege
    loyalty_credit = min(loyalty_credit, pre_total)
    result.loyalty_credit = loyalty_credit

    # BRU-LOY-09: stacked-discount cap on the aggregate DISCOUNT reduction.
    # Loyalty redemption is NOT a discount — it is the customer spending an
    # earned asset (closer to payment) — so it is excluded from the cap and
    # separately clamped so the total never goes negative (BRU-LOY-06's
    # companion: the engine never creates an overdrawn outcome).
    if result.subtotal > 0:
        aggregate_pct = (
            (result.total_discount + result.total_privilege)
            * Decimal("100") / result.subtotal)
        if aggregate_pct > request.stack_cap_pct:
            raise PricingError(
                f"stacked discount {aggregate_pct}% exceeds the "
                f"{request.stack_cap_pct}% cap (BRU-LOY-09)")

    result.total = (pre_total - loyalty_credit).quantize(TWO, ROUND_HALF_UP)
    result.audit.append(
        "subtotal %s; discounts %s; privilege %s; loyalty %s; total %s"
        % (result.subtotal, result.total_discount, result.total_privilege,
           loyalty_credit, result.total))
    return result
