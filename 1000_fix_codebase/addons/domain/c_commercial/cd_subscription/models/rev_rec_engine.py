"""rev_rec_engine — M53 W4 Revenue Recognition Pure Calculation Engine.

Standalone pure-Python module (zero Odoo/database dependencies) implementing
straight-line revenue recognition for recurring subscriptions, annual maintenance
contracts (AMC/RAMC), and device protection plans.

Enforces BRU-LOY-12: Revenue is recognized ratably over the performance term,
never at the point of sale. 100% unit-testable calculation paths (DoD-03).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

TWO = Decimal("0.01")


class RevRecError(ValueError):
    """Raised when parameters violate statutory or mathematical constraints."""


@dataclass(frozen=True)
class RecognitionPeriodResult:
    """Output of a period recognition calculation."""

    as_of: date
    start_date: date
    end_date: date
    total_amount: Decimal
    term_days: int
    elapsed_days: int
    target_cumulative: Decimal
    already_recognized: Decimal
    incremental_delta: Decimal
    remaining_deferred: Decimal
    is_complete: bool


def compute_straight_line_recognition(
    total_amount: Decimal | float | int | str,
    start_date: date,
    end_date: date,
    as_of: date,
    already_recognized: Decimal | float | int | str = Decimal("0.00"),
) -> RecognitionPeriodResult:
    """Compute straight-line cumulative and incremental revenue recognition.

    Formula:
        target_cumulative = round(total_amount * elapsed_days / term_days, 2)
        incremental_delta = max(0.00, target_cumulative - already_recognized)
        remaining_deferred = max(0.00, total_amount - target_cumulative)

    Constraints:
        - total_amount must be strictly positive
        - end_date must be strictly after start_date
        - already_recognized cannot be negative or exceed total_amount
    """
    total = Decimal(str(total_amount)).quantize(TWO, ROUND_HALF_UP)
    if total <= Decimal("0.00"):
        raise RevRecError("Total deferred amount must be strictly positive")

    if end_date <= start_date:
        raise RevRecError("End date must be strictly after start date (term must be >= 1 day)")

    recognized = Decimal(str(already_recognized)).quantize(TWO, ROUND_HALF_UP)
    if recognized < Decimal("0.00"):
        raise RevRecError("Already recognized amount cannot be negative")
    if recognized > total:
        raise RevRecError("Already recognized amount cannot exceed total deferred amount")

    term_days = (end_date - start_date).days
    if as_of <= start_date:
        elapsed_days = 0
    elif as_of >= end_date:
        elapsed_days = term_days
    else:
        elapsed_days = (as_of - start_date).days

    if elapsed_days >= term_days:
        target = total
        is_complete = True
    else:
        target = (total * Decimal(elapsed_days) / Decimal(term_days)).quantize(TWO, ROUND_HALF_UP)
        is_complete = False

    delta = target - recognized
    if delta < Decimal("0.00"):
        delta = Decimal("0.00")

    remaining = max(Decimal("0.00"), total - (recognized + delta))

    return RecognitionPeriodResult(
        as_of=as_of,
        start_date=start_date,
        end_date=end_date,
        total_amount=total,
        term_days=term_days,
        elapsed_days=elapsed_days,
        target_cumulative=target,
        already_recognized=recognized,
        incremental_delta=delta,
        remaining_deferred=remaining,
        is_complete=is_complete,
    )


@dataclass(frozen=True)
class CancellationRefundResult:
    """Output of mid-cycle subscription cancellation & refund computation."""

    cancellation_date: date
    total_amount: Decimal
    earned_revenue: Decimal
    unearned_refund: Decimal
    cancellation_fee: Decimal
    net_refund_payable: Decimal
    requires_manager_approval: bool


def compute_cancellation_refund(
    total_amount: Decimal | float | int | str,
    start_date: date,
    end_date: date,
    cancellation_date: date,
    cancellation_fee_pct: Decimal | float | int | str = Decimal("0.00"),
    approval_threshold: Decimal = Decimal("25000.00"),
) -> CancellationRefundResult:
    """Compute prorated refund and unearned revenue upon mid-cycle cancellation.

    Statutory and managerial authority rules:
    - Earned revenue = recognized straight-line up to cancellation_date.
    - Unearned revenue = total - earned revenue.
    - Cancellation fee = unearned revenue * cancellation_fee_pct.
    - Net refund payable = unearned revenue - cancellation_fee.
    - If net refund payable > approval_threshold (default BDT 25,000), managerial SoD approval is required.
    """
    total = Decimal(str(total_amount)).quantize(TWO, ROUND_HALF_UP)
    if total <= Decimal("0.00"):
        raise RevRecError("Total amount must be strictly positive")
    if end_date <= start_date:
        raise RevRecError("Term must be >= 1 day")

    fee_pct = Decimal(str(cancellation_fee_pct))
    if fee_pct < Decimal("0.00") or fee_pct > Decimal("100.00"):
        raise RevRecError("Cancellation fee pct must be between 0 and 100")

    term_days = (end_date - start_date).days
    if cancellation_date <= start_date:
        elapsed = 0
    elif cancellation_date >= end_date:
        elapsed = term_days
    else:
        elapsed = (cancellation_date - start_date).days

    earned = (total * Decimal(elapsed) / Decimal(term_days)).quantize(TWO, ROUND_HALF_UP)
    unearned = total - earned
    fee = (unearned * fee_pct / Decimal("100.00")).quantize(TWO, ROUND_HALF_UP)
    net_refund = unearned - fee

    requires_approval = net_refund > approval_threshold

    return CancellationRefundResult(
        cancellation_date=cancellation_date,
        total_amount=total,
        earned_revenue=earned,
        unearned_refund=unearned,
        cancellation_fee=fee,
        net_refund_payable=net_refund,
        requires_manager_approval=requires_approval,
    )
