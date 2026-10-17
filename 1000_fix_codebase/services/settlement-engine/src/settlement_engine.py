"""settlement-engine — P07-M03-T07 (CD-M53-nn; TSS §20.2 W4). L5 standalone.

Commission and payout computation as PURE functions — 100% of calculation
paths unit-testable without a database. **Commission and payout must post
to the ledger** — the SaaS marketplace is not the system of record for
money the Company owes; the settlement engine computes, M53's Odoo side
posts, the ledger is the ledger.

AR-006 §4.1 pair 12: commission CALCULATION is M53's; commission EARNING
is an M12 event (Phase 10) — M12 must not call M53. The engine consumes
earning events; it never reaches into the marketplace.

R05-M02-T04: Payout-run readiness with two-person Segregation of Duties (SoD)
approval authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

TWO = Decimal("0.01")


class SettlementError(ValueError):
    """Refuse to guess: an unknown scheme or negative basis raises."""


class SoDViolationError(SettlementError):
    """Raised when Segregation of Duties rules are violated."""


@dataclass(frozen=True)
class EarningEvent:
    """One commission-earning event (from M12, or the subscription engine's
    own recurring events)."""
    seller_ref: str            # seller/vendor identifier
    basis_amount: Decimal      # what the commission is computed ON
    scheme: str                # the commission scheme id
    occurred_at: str           # ISO date — the period bucket


# Commission schemes: pct of basis, with optional tiered kicker.
SCHEMES: dict[str, dict] = {
    "service_labour": {"pct": Decimal("10")},
    "part_margin": {"pct": Decimal("8")},
    "subscription_reseller": {"pct": Decimal("15")},
    "marketplace_gmv": {"pct": Decimal("5"),
                        "kicker": {"above": Decimal("100000"), "extra_pct": Decimal("2")}},
}
# Payout deductions order (statutory + platform):
TDS_SERVICE_PCT = Decimal("10")
PLATFORM_FEE_PCT = Decimal("3")

ALLOWED_APPROVER_ROLES = ("finance_manager", "cfo", "system_admin")


@dataclass(frozen=True)
class CommissionLine:
    seller_ref: str
    scheme: str
    basis: Decimal
    rate: Decimal
    commission: Decimal


@dataclass(frozen=True)
class PayoutLine:
    seller_ref: str
    period: str
    gross_commission: Decimal
    tds: Decimal
    platform_fee: Decimal
    net_payable: Decimal


@dataclass(frozen=True)
class PayoutBatch:
    """Aggregated payout run ready for SoD approval and execution."""
    period: str
    payout_lines: tuple[PayoutLine, ...]
    total_gross: Decimal
    total_tds: Decimal
    total_platform_fee: Decimal
    total_net_payable: Decimal
    seller_count: int
    prepared_by: str
    approved_by: str | None = None
    state: str = "draft"  # "draft" | "approved" | "executed"


def commission_for(event: EarningEvent) -> CommissionLine:
    scheme = SCHEMES.get(event.scheme)
    if scheme is None:
        raise SettlementError(
            f"unknown commission scheme {event.scheme!r} — the register must name it")
    if event.basis_amount < 0:
        raise SettlementError("commission basis cannot be negative")
    rate = scheme["pct"]
    commission = (event.basis_amount * rate / Decimal("100")).quantize(TWO, ROUND_HALF_UP)
    kicker = scheme.get("kicker")
    if kicker and event.basis_amount > kicker["above"]:
        extra = (event.basis_amount * kicker["extra_pct"] / Decimal("100")).quantize(
            TWO, ROUND_HALF_UP)
        commission += extra
        rate = rate + kicker["extra_pct"]
    return CommissionLine(event.seller_ref, event.scheme, event.basis_amount,
                          rate, commission)


def settle_period(events: list[EarningEvent], period: str) -> list[PayoutLine]:
    """Aggregate a period's earnings per seller, apply the statutory and
    platform deductions IN ORDER, and produce payout lines.

    Order matters and is fixed: gross commission -> TDS (statutory) ->
    platform fee -> net payable. The same order posts to the ledger."""
    by_seller: dict[str, Decimal] = {}
    for event in events:
        if event.occurred_at[:7] != period[:7]:
            continue
        line = commission_for(event)
        by_seller.setdefault(event.seller_ref, Decimal("0"))
        by_seller[event.seller_ref] += line.commission
    payouts = []
    for seller, gross in sorted(by_seller.items()):
        gross = gross.quantize(TWO, ROUND_HALF_UP)
        tds = (gross * TDS_SERVICE_PCT / Decimal("100")).quantize(TWO, ROUND_HALF_UP)
        after_tds = gross - tds
        fee = (after_tds * PLATFORM_FEE_PCT / Decimal("100")).quantize(TWO, ROUND_HALF_UP)
        payouts.append(PayoutLine(
            seller_ref=seller, period=period, gross_commission=gross,
            tds=tds, platform_fee=fee, net_payable=(after_tds - fee).quantize(TWO, ROUND_HALF_UP)))
    return payouts


def create_payout_batch(events: list[EarningEvent], period: str, prepared_by: str) -> PayoutBatch:
    """Create a new draft payout batch prepared by a specific user/accountant."""
    if not prepared_by or not prepared_by.strip():
        raise SettlementError("prepared_by is required for payout batch auditability")
    lines = settle_period(events, period)
    gross = sum((l.gross_commission for l in lines), Decimal("0.00")).quantize(TWO, ROUND_HALF_UP)
    tds = sum((l.tds for l in lines), Decimal("0.00")).quantize(TWO, ROUND_HALF_UP)
    fee = sum((l.platform_fee for l in lines), Decimal("0.00")).quantize(TWO, ROUND_HALF_UP)
    net = sum((l.net_payable for l in lines), Decimal("0.00")).quantize(TWO, ROUND_HALF_UP)
    return PayoutBatch(
        period=period,
        payout_lines=tuple(lines),
        total_gross=gross,
        total_tds=tds,
        total_platform_fee=fee,
        total_net_payable=net,
        seller_count=len(lines),
        prepared_by=prepared_by,
        state="draft",
    )


def validate_payout_sod(
    prepared_by: str,
    approver_id: str,
    approver_role: str,
    allowed_roles: tuple[str, ...] = ALLOWED_APPROVER_ROLES,
) -> None:
    """Validate Segregation of Duties for payout approval.

    Rules:
    1. Preparer cannot approve their own payout run (two-person rule).
    2. Approver must hold an authorized role with payout sign-off privilege.
    """
    if not approver_id or not approver_id.strip():
        raise SoDViolationError("approver_id is required")
    if prepared_by.strip().lower() == approver_id.strip().lower():
        raise SoDViolationError("SoD Violation: Preparer cannot approve their own payout run.")
    if approver_role not in allowed_roles:
        raise SoDViolationError(
            f"SoD Violation: Role '{approver_role}' does not possess payout approval authority. "
            f"Allowed roles: {allowed_roles}")


def approve_payout_batch(
    batch: PayoutBatch,
    approver_id: str,
    approver_role: str,
) -> PayoutBatch:
    """Approve a draft payout batch after verifying two-person SoD rules."""
    if batch.state != "draft":
        raise SettlementError(f"Cannot approve batch in state '{batch.state}' (must be 'draft')")
    if not batch.payout_lines:
        raise SettlementError("Cannot approve payout batch with zero commission lines")
    if batch.total_net_payable <= Decimal("0.00"):
        raise SettlementError("Cannot approve payout batch with zero or negative net payable")

    # Enforce SoD validation
    validate_payout_sod(batch.prepared_by, approver_id, approver_role)

    return PayoutBatch(
        period=batch.period,
        payout_lines=batch.payout_lines,
        total_gross=batch.total_gross,
        total_tds=batch.total_tds,
        total_platform_fee=batch.total_platform_fee,
        total_net_payable=batch.total_net_payable,
        seller_count=batch.seller_count,
        prepared_by=batch.prepared_by,
        approved_by=approver_id,
        state="approved",
    )


def execute_payout_batch(batch: PayoutBatch) -> PayoutBatch:
    """Execute payout disbursement rail. Requires prior approval."""
    if batch.state != "approved":
        raise SettlementError("Payout batch must be approved before execution")
    return PayoutBatch(
        period=batch.period,
        payout_lines=batch.payout_lines,
        total_gross=batch.total_gross,
        total_tds=batch.total_tds,
        total_platform_fee=batch.total_platform_fee,
        total_net_payable=batch.total_net_payable,
        seller_count=batch.seller_count,
        prepared_by=batch.prepared_by,
        approved_by=batch.approved_by,
        state="executed",
    )
