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

from dataclasses import dataclass, replace
from datetime import date
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

    seller_ref: str  # seller/vendor identifier
    basis_amount: Decimal  # what the commission is computed ON
    scheme: str  # the commission scheme id
    occurred_at: str  # ISO date — the period bucket


# Commission schemes: pct of basis, with optional tiered kicker.
SCHEMES: dict[str, dict] = {
    "service_labour": {"pct": Decimal("10")},
    "part_margin": {"pct": Decimal("8")},
    "subscription_reseller": {"pct": Decimal("15")},
    "marketplace_gmv": {
        "pct": Decimal("5"),
        "kicker": {"above": Decimal("100000"), "extra_pct": Decimal("2")},
    },
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
    # The seller's gross sales value for the period: the sum of the commission
    # BASIS amounts the commission was computed on. None when the producer of
    # the line did not carry it (then a statement must be given it explicitly).
    gross_basis: Decimal | None = None


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
    # "draft" | "approved" | "pending_bank_confirmation" | "executed"
    state: str = "draft"
    # The bank-issued settlement reference that confirmed the disbursement.
    bank_reference: str | None = None


def commission_for(event: EarningEvent) -> CommissionLine:
    scheme = SCHEMES.get(event.scheme)
    if scheme is None:
        raise SettlementError(
            f"unknown commission scheme {event.scheme!r} — the register must name it"
        )
    if event.basis_amount < 0:
        raise SettlementError("commission basis cannot be negative")
    rate = scheme["pct"]
    commission = (event.basis_amount * rate / Decimal("100")).quantize(TWO, ROUND_HALF_UP)
    kicker = scheme.get("kicker")
    if kicker and event.basis_amount > kicker["above"]:
        extra = (event.basis_amount * kicker["extra_pct"] / Decimal("100")).quantize(
            TWO, ROUND_HALF_UP
        )
        commission += extra
        rate = rate + kicker["extra_pct"]
    return CommissionLine(event.seller_ref, event.scheme, event.basis_amount, rate, commission)


def settle_period(events: list[EarningEvent], period: str) -> list[PayoutLine]:
    """Aggregate a period's earnings per seller, apply the statutory and
    platform deductions IN ORDER, and produce payout lines.

    Order matters and is fixed: gross commission -> TDS (statutory) ->
    platform fee -> net payable. The same order posts to the ledger."""
    by_seller: dict[str, Decimal] = {}
    basis_by_seller: dict[str, Decimal] = {}
    for event in events:
        if event.occurred_at[:7] != period[:7]:
            continue
        line = commission_for(event)
        by_seller.setdefault(event.seller_ref, Decimal("0"))
        by_seller[event.seller_ref] += line.commission
        basis_by_seller[event.seller_ref] = (
            basis_by_seller.get(event.seller_ref, Decimal("0")) + line.basis
        )
    payouts = []
    for seller, gross in sorted(by_seller.items()):
        gross = gross.quantize(TWO, ROUND_HALF_UP)
        tds = (gross * TDS_SERVICE_PCT / Decimal("100")).quantize(TWO, ROUND_HALF_UP)
        after_tds = gross - tds
        fee = (after_tds * PLATFORM_FEE_PCT / Decimal("100")).quantize(TWO, ROUND_HALF_UP)
        payouts.append(
            PayoutLine(
                seller_ref=seller,
                period=period,
                gross_commission=gross,
                tds=tds,
                platform_fee=fee,
                net_payable=(after_tds - fee).quantize(TWO, ROUND_HALF_UP),
                gross_basis=basis_by_seller[seller].quantize(TWO, ROUND_HALF_UP),
            )
        )
    return payouts


def create_payout_batch(events: list[EarningEvent], period: str, prepared_by: str) -> PayoutBatch:
    """Create a new draft payout batch prepared by a specific user/accountant."""
    if not prepared_by or not prepared_by.strip():
        raise SettlementError("prepared_by is required for payout batch auditability")
    lines = settle_period(events, period)
    gross = sum((line.gross_commission for line in lines), Decimal("0.00")).quantize(
        TWO, ROUND_HALF_UP
    )
    tds = sum((line.tds for line in lines), Decimal("0.00")).quantize(TWO, ROUND_HALF_UP)
    fee = sum((line.platform_fee for line in lines), Decimal("0.00")).quantize(TWO, ROUND_HALF_UP)
    net = sum((line.net_payable for line in lines), Decimal("0.00")).quantize(TWO, ROUND_HALF_UP)
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
            f"Allowed roles: {allowed_roles}"
        )


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
    """Release an approved batch to the disbursement rail. Requires prior approval.

    Releasing is NOT paying: the batch moves to ``pending_bank_confirmation``
    and only confirm_payout_batch() — with the bank's settlement reference —
    makes it ``executed``. (It used to return ``executed`` straight away with
    no bank involvement at all.)"""
    if batch.state != "approved":
        raise SettlementError("Payout batch must be approved before execution")
    return replace(batch, state="pending_bank_confirmation")


def confirm_payout_batch(batch: PayoutBatch, bank_reference: str) -> PayoutBatch:
    """Mark a released batch executed on the bank's confirmation.

    ``bank_reference`` is the reference the BANK issued for the settlement
    (BEFTN settlement / statement reference) — supplied by a person or a real
    bank response, never generated here."""
    if batch.state != "pending_bank_confirmation":
        raise SettlementError(
            f"Cannot confirm batch in state '{batch.state}' (must be 'pending_bank_confirmation')"
        )
    ref = (bank_reference or "").strip()
    if not ref:
        raise SettlementError("A bank settlement reference is required to confirm a payout")
    return replace(batch, state="executed", bank_reference=ref)


def parse_commission_earned_event(payload: dict) -> EarningEvent:
    """Consumes an M12 'commission.earned' event payload (M12<->M53 event break).

    Expected payload keys:
    - seller_ref: string identifier
    - basis_amount / gmv_amount: numeric/string amount
    - scheme: commission scheme id (default: 'marketplace_gmv')
    - occurred_at: ISO date string
    """
    if not isinstance(payload, dict):
        raise SettlementError("Event payload must be a dictionary")

    seller_ref = payload.get("seller_ref") or payload.get("seller_id")
    if not seller_ref:
        raise SettlementError("Event payload missing mandatory 'seller_ref'")

    raw_basis = (
        payload.get("basis_amount") or payload.get("gmv_amount") or payload.get("gross_amount")
    )
    if raw_basis is None:
        raise SettlementError("Event payload missing commission basis amount")

    try:
        basis_decimal = Decimal(str(raw_basis)).quantize(TWO, ROUND_HALF_UP)
    except Exception as exc:
        raise SettlementError(f"Invalid basis amount {raw_basis!r}: {exc}") from exc

    scheme = payload.get("scheme", "marketplace_gmv")
    occurred_at = (
        payload.get("occurred_at") or payload.get("event_time") or date.today().isoformat()
    )

    return EarningEvent(
        seller_ref=str(seller_ref),
        basis_amount=basis_decimal,
        scheme=str(scheme),
        occurred_at=str(occurred_at),
    )


@dataclass(frozen=True)
class SellerStatement:
    """Bilingual seller statement carrying Income Tax Act 2023 §52 withholding certification.
    DE-17 & P10-M02-T06 compliance."""

    statement_id: str
    seller_ref: str
    period: str
    gross_gmv: Decimal  # মোট বিক্রয় মূল্য
    commission_amount: Decimal  # কমিশন
    tds_withheld: Decimal  # উৎসে কর কর্তন (ITA 2023 §52)
    platform_fee: Decimal  # প্ল্যাটফর্ম ফি
    net_payable: Decimal  # প্রদেয় নিট অর্থ
    withholding_cert_ref: str  # প্রত্যয়নপত্র নং
    bilingual_labels: dict[str, dict[str, str]]


def generate_seller_statement(
    payout_line: PayoutLine,
    statement_seq: int = 1,
    cert_year: int = 2026,
    gross_gmv: Decimal | None = None,
) -> SellerStatement:
    """Generate a formal bilingual seller statement with statutory §52 TDS documentation.

    `gross_gmv` is the seller's gross sales value; it defaults to the payout
    line's `gross_basis` (set by settle_period). The commission is NEVER
    reported as gross sales value: with neither available, this refuses."""
    gmv = payout_line.gross_basis if gross_gmv is None else gross_gmv
    if gmv is None:
        raise SettlementError(
            f"gross sales value unavailable for seller {payout_line.seller_ref!r}: "
            "pass gross_gmv (the commission is not the GMV)"
        )
    stmt_id = f"STM-{payout_line.period}-{payout_line.seller_ref}-{statement_seq:04d}"
    cert_ref = f"NBR-TDS52-{cert_year}-{payout_line.seller_ref[:8]}-{statement_seq:04d}"

    bilingual = {
        "gross_gmv": {"en": "Gross Sales Value", "bn": "মোট বিক্রয় মূল্য"},
        "commission": {"en": "Platform Commission", "bn": "প্ল্যাটফর্ম কমিশন"},
        "tds": {
            "en": "Tax Withheld at Source (ITA 2023 §52)",
            "bn": "উৎসে কর কর্তন (আয়কর আইন ২০২৩ ধারা ৫২)",
        },
        "platform_fee": {"en": "Platform Processing Fee", "bn": "প্ল্যাটফর্ম প্রসেসিং ফি"},
        "net_payable": {"en": "Net Disbursed Amount", "bn": "প্রদেয় নিট অর্থ"},
        "statutory_note": {
            "en": "Certified that tax has been deducted at source under Section 52 of the Income Tax Act 2023.",
            "bn": "প্রত্যয়ন করা যাচ্ছে যে, আয়কর আইন ২০২৩ এর ধারা ৫২ মোতাবেক উৎসে কর কর্তন করা হয়েছে।",
        },
    }

    return SellerStatement(
        statement_id=stmt_id,
        seller_ref=payout_line.seller_ref,
        period=payout_line.period,
        gross_gmv=gmv,
        commission_amount=payout_line.gross_commission,
        tds_withheld=payout_line.tds,
        platform_fee=payout_line.platform_fee,
        net_payable=payout_line.net_payable,
        withholding_cert_ref=cert_ref,
        bilingual_labels=bilingual,
    )


@dataclass(frozen=True)
class PayoutReconciliationBreak:
    seller_ref: str
    system_amount: Decimal
    rail_amount: Decimal
    discrepancy: Decimal
    age_days: int
    is_aged: bool  # True if age_days > 30


@dataclass(frozen=True)
class PayoutReconciliationReport:
    """Payout reconciliation comparing count and amount separately (IN-007 §11.3, FF-94).
    Flags unmatched records and verifies unmatched aged > 30 days is zero."""

    batch_ref: str
    system_count: int
    rail_count: int
    count_matched: bool
    system_amount: Decimal
    rail_amount: Decimal
    amount_matched: bool
    unmatched_count: int
    unmatched_amount: Decimal
    aged_unmatched_count: int
    aged_unmatched_amount: Decimal
    breaks: tuple[PayoutReconciliationBreak, ...]
    is_balanced: bool
    divergence_alert: bool


def reconcile_payout_run(
    batch: PayoutBatch,
    rail_records: list[dict],
    as_of_date: date | None = None,
) -> PayoutReconciliationReport:
    """Reconcile system payout batch against rail confirmation records (BR-01..BR-05, FF-94)."""
    today = as_of_date or date.today()
    system_count = len(batch.payout_lines)
    system_amount = batch.total_net_payable

    rail_count = len(rail_records)
    rail_amount = sum(
        (Decimal(str(r.get("amount", "0.00"))) for r in rail_records),
        Decimal("0.00"),
    ).quantize(TWO, ROUND_HALF_UP)

    count_matched = system_count == rail_count
    amount_matched = system_amount == rail_amount

    # Build rail lookup by seller_ref
    rail_by_seller: dict[str, dict] = {
        r["seller_ref"]: r for r in rail_records if "seller_ref" in r
    }

    breaks: list[PayoutReconciliationBreak] = []
    unmatched_count = 0
    unmatched_amount = Decimal("0.00")
    aged_unmatched_count = 0
    aged_unmatched_amount = Decimal("0.00")

    for line in batch.payout_lines:
        rail_rec = rail_by_seller.get(line.seller_ref)
        if not rail_rec:
            # Entirely missing from rail
            unmatched_count += 1
            unmatched_amount += line.net_payable
            breaks.append(
                PayoutReconciliationBreak(
                    seller_ref=line.seller_ref,
                    system_amount=line.net_payable,
                    rail_amount=Decimal("0.00"),
                    discrepancy=line.net_payable,
                    age_days=0,
                    is_aged=False,
                )
            )
        else:
            r_amt = Decimal(str(rail_rec.get("amount", "0.00"))).quantize(TWO, ROUND_HALF_UP)
            rec_date_str = rail_rec.get("record_date")
            age_days = 0
            if rec_date_str:
                try:
                    rec_d = date.fromisoformat(rec_date_str[:10])
                    age_days = max(0, (today - rec_d).days)
                except Exception:
                    age_days = 0

            diff = (line.net_payable - r_amt).copy_abs()
            if diff > Decimal("0.00") or rail_rec.get("status") in ("unmatched", "failed"):
                is_aged = age_days > 30
                unmatched_count += 1
                unmatched_amount += diff
                if is_aged:
                    aged_unmatched_count += 1
                    aged_unmatched_amount += diff
                breaks.append(
                    PayoutReconciliationBreak(
                        seller_ref=line.seller_ref,
                        system_amount=line.net_payable,
                        rail_amount=r_amt,
                        discrepancy=diff,
                        age_days=age_days,
                        is_aged=is_aged,
                    )
                )

    is_balanced = count_matched and amount_matched and (unmatched_count == 0)
    divergence_alert = not is_balanced

    return PayoutReconciliationReport(
        batch_ref=batch.period,
        system_count=system_count,
        rail_count=rail_count,
        count_matched=count_matched,
        system_amount=system_amount,
        rail_amount=rail_amount,
        amount_matched=amount_matched,
        unmatched_count=unmatched_count,
        unmatched_amount=unmatched_amount.quantize(TWO, ROUND_HALF_UP),
        aged_unmatched_count=aged_unmatched_count,
        aged_unmatched_amount=aged_unmatched_amount.quantize(TWO, ROUND_HALF_UP),
        breaks=tuple(breaks),
        is_balanced=is_balanced,
        divergence_alert=divergence_alert,
    )
