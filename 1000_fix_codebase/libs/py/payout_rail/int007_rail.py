"""libs/py/payout_rail/int007_rail.py — INT-007 seller payout rail.

Complies with:
- IN-007 §12.3: Seller payout rail requirements (per-recipient status, query read-back, 500-2,000 recipients).
- IN-007 §3.2 / IN-007-D-01: First-class `unknown` timeout state; FF-85 (no exit from unknown without read-back).
- IN-007 §5.2 / IN-007-D-03: 7-day idempotency retention window (P7D).
- IN-007 §11.3 / FF-94: Count and amount reported separately.
- BEFTN Operating Rules: Fallback file generation via standard 128-byte layout.
- GV-009 fail-closed: execution outcomes come from a REAL bank endpoint call
  or not at all — without an endpoint the rail refuses rather than fabricating
  per-recipient confirmed/failed results. An OUTAGE may be simulated (honest
  UNKNOWN); a SUCCESS may not.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

from libs.py.payroll_engine.beftn import (
    BeftnBatchHeader,
    BeftnEntry,
    generate_beftn_batch_file,
    validate_routing_number,
)

TWO = Decimal("0.01")
SEVEN_DAYS_SECONDS = 7 * 24 * 60 * 60


class PayoutStatus(StrEnum):
    INITIATED = "initiated"
    EXECUTING = "executing"
    CONFIRMED = "confirmed"
    UNKNOWN = "unknown"
    FAILED = "failed"


class PayoutRailError(Exception):
    """Base exception for payout rail errors."""


class IdempotencyConflictError(PayoutRailError):
    """Raised when an idempotency key is reused with a different request payload."""


class InvalidRoutingError(PayoutRailError):
    """Raised when a bank routing number is invalid."""


class InvalidStatusTransitionError(PayoutRailError):
    """Raised on invalid state transition, e.g., leaving unknown without read-back (FF-85)."""


class BankEndpointNotConfiguredError(PayoutRailError):
    """GV-009: raised when an execution path is attempted with no bank payout
    endpoint configured — the rail refuses to fabricate an execution result."""


@dataclass(frozen=True)
class PayoutRecipient:
    seller_ref: str
    seller_name: str
    account_number: str
    routing_number: str
    amount_bdt: Decimal
    disbursement_ref: str
    wallet_number: str | None = None
    rail_preference: str = "bank"  # "bank" | "bKash" | "Nagad"


@dataclass(frozen=True)
class RecipientResult:
    seller_ref: str
    status: PayoutStatus
    rail_tx_id: str | None
    amount_bdt: Decimal
    failure_reason: str | None = None


@dataclass(frozen=True)
class PayoutBatchRequest:
    batch_ref: str
    period: str
    recipients: tuple[PayoutRecipient, ...]
    idempotency_key: str
    total_amount: Decimal
    recipient_count: int


@dataclass(frozen=True)
class PayoutBatchResult:
    batch_ref: str
    rail_batch_id: str
    idempotency_key: str
    status: PayoutStatus
    submission_time: str
    recipient_results: tuple[RecipientResult, ...]
    total_amount: Decimal
    recipient_count: int
    confirmed_count: int
    confirmed_amount: Decimal
    failed_count: int
    failed_amount: Decimal
    unknown_count: int
    unknown_amount: Decimal
    rail_type: str
    beftn_raw: str | None = None


def _tx_id(entry: dict) -> str | None:
    """The rail's own transaction id for a recipient, or None when it sent none."""
    value = entry.get("rail_tx_id")
    return str(value) if value else None


class InMemoryIdempotencyStore:
    """7-day in-memory idempotency store for payout submissions (IN-007-D-03)."""

    def __init__(self, ttl_seconds: int = SEVEN_DAYS_SECONDS):
        self._store: dict[str, tuple[float, str, PayoutBatchResult]] = {}
        self._ttl_seconds = ttl_seconds

    def get(self, key: str) -> tuple[str, PayoutBatchResult] | None:
        self._evict_expired()
        entry = self._store.get(key)
        if not entry:
            return None
        _, payload_hash, result = entry
        return payload_hash, result

    def set(self, key: str, payload_hash: str, result: PayoutBatchResult) -> None:
        self._evict_expired()
        self._store[key] = (time.time(), payload_hash, result)

    def replace_result(self, key: str, result: PayoutBatchResult) -> bool:
        """Swap in a newer outcome of the SAME rail batch (read-back resolution),
        keeping the payload hash and the original retention clock. A key that
        expired or now belongs to another rail batch is left untouched."""
        self._evict_expired()
        entry = self._store.get(key)
        if entry is None or entry[2].rail_batch_id != result.rail_batch_id:
            return False
        stored_at, payload_hash, _ = entry
        self._store[key] = (stored_at, payload_hash, result)
        return True

    def _evict_expired(self) -> None:
        now = time.time()
        expired = [k for k, (t, _, _) in self._store.items() if now - t > self._ttl_seconds]
        for k in expired:
            del self._store[k]


class INT007PayoutRail:
    """INT-007 seller payout rail handler."""

    BANK_URL_ENV = "FIX_INT007_BANK_API_URL"
    DEFAULT_TX_FAILURE_REASON = "Beneficiary account rejected by receiving bank"

    def __init__(
        self,
        idempotency_store: InMemoryIdempotencyStore | None = None,
        originating_routing: str = "125272355",  # Default corporate sponsor routing
        company_name: str = "1000FiX Services Ltd",
        company_id: str = "FIX-CORP-01",
        bank_api_url: str | None = None,
    ):
        self.store = idempotency_store or InMemoryIdempotencyStore()
        self.originating_routing = originating_routing
        self.company_name = company_name
        self.company_id = company_id
        self.bank_api_url = (
            bank_api_url if bank_api_url is not None else os.environ.get(self.BANK_URL_ENV, "")
        ).strip()
        # In-memory rail registry so read-back and idempotent replay serve the
        # SAME outcome the submission produced (kept for tests and read-back).
        self._gateway_state: dict[str, PayoutBatchResult] = {}

    def _compute_payload_hash(self, request: PayoutBatchRequest) -> str:
        h = hashlib.sha256()
        h.update(request.batch_ref.encode("utf-8"))
        h.update(str(request.total_amount).encode("utf-8"))
        h.update(str(request.recipient_count).encode("utf-8"))
        for r in request.recipients:
            h.update(
                f"{r.seller_ref}:{r.amount_bdt}:{r.account_number}:{r.routing_number}".encode()
            )
        return h.hexdigest()

    def _admit(self, request: PayoutBatchRequest) -> tuple[str, PayoutBatchResult | None]:
        """Admission shared by EVERY rail (API and BEFTN fallback): mandatory
        Idempotency-Key (IN-007 §5.1), 7-day replay / conflict (IN-007-D-03) and
        control totals (FF-94). Returns (payload_hash, cached result or None)."""
        if not request.idempotency_key or not request.idempotency_key.strip():
            raise PayoutRailError("Idempotency-Key is mandatory for money operations (IN-007 §5.1)")

        payload_hash = self._compute_payload_hash(request)
        cached = self.store.get(request.idempotency_key)
        if cached:
            cached_hash, cached_result = cached
            if cached_hash != payload_hash:
                raise IdempotencyConflictError(
                    f"Idempotency-Key '{request.idempotency_key}' reused with different payout payload"
                )
            return payload_hash, cached_result

        # Validate control totals
        computed_count = len(request.recipients)
        computed_total = sum((r.amount_bdt for r in request.recipients), Decimal("0.00")).quantize(
            TWO, ROUND_HALF_UP
        )
        if computed_count != request.recipient_count or computed_total != request.total_amount:
            raise PayoutRailError(
                f"Control totals mismatch: declared count={request.recipient_count}, amount={request.total_amount}; "
                f"computed count={computed_count}, amount={computed_total} (FF-94)"
            )
        return payload_hash, None

    def _unknown_result(
        self,
        request: PayoutBatchRequest,
        rail_batch_id: str,
        submission_time: str,
        rail_type: str,
        reason: str,
    ) -> PayoutBatchResult:
        """IN-007 §3.2 / IN-007-D-01: an inconclusive submission enters the
        first-class UNKNOWN state — never a fabricated success or failure."""
        unknown_lines = tuple(
            RecipientResult(
                seller_ref=r.seller_ref,
                status=PayoutStatus.UNKNOWN,
                rail_tx_id=None,
                amount_bdt=r.amount_bdt,
                failure_reason=reason,
            )
            for r in request.recipients
        )
        return PayoutBatchResult(
            batch_ref=request.batch_ref,
            rail_batch_id=rail_batch_id,
            idempotency_key=request.idempotency_key,
            status=PayoutStatus.UNKNOWN,
            submission_time=submission_time,
            recipient_results=unknown_lines,
            total_amount=request.total_amount,
            recipient_count=request.recipient_count,
            confirmed_count=0,
            confirmed_amount=Decimal("0.00"),
            failed_count=0,
            failed_amount=Decimal("0.00"),
            unknown_count=request.recipient_count,
            unknown_amount=request.total_amount,
            rail_type=rail_type,
        )

    def _submit_to_bank(self, request: PayoutBatchRequest, rail_batch_id: str) -> dict | None:
        """POST the batch to the configured bank payout endpoint. Returns the
        parsed rail response, or None on any transport/HTTP failure (IN-007
        §3.2: money may have moved, so the caller records UNKNOWN — the rail
        never turns an unreachable endpoint into a fabricated outcome)."""
        body = {
            "batch_ref": request.batch_ref,
            "rail_batch_id": rail_batch_id,
            "idempotency_key": request.idempotency_key,
            "total_amount": str(request.total_amount),
            "recipient_count": request.recipient_count,
            "recipients": [
                {
                    "seller_ref": r.seller_ref,
                    "amount_bdt": str(r.amount_bdt),
                    "account_number": r.account_number,
                    "routing_number": r.routing_number,
                    "rail_preference": r.rail_preference,
                    "wallet_number": r.wallet_number,
                }
                for r in request.recipients
            ],
        }
        http_request = urllib.request.Request(  # noqa: S310 - operator-configured bank endpoint
            f"{self.bank_api_url.rstrip('/')}/payout-batches",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Idempotency-Key": request.idempotency_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_request, timeout=30) as response:  # noqa: S310
                parsed = json.loads(response.read() or b"{}")
            return parsed if isinstance(parsed, dict) else None
        except (urllib.error.URLError, TimeoutError, OSError):
            return None

    def submit_payout_batch(
        self,
        request: PayoutBatchRequest,
        rail_type: str = "api",
        simulate_timeout: bool = False,
    ) -> PayoutBatchResult:
        """Submit a payout batch with 7-day idempotency guarantee.

        The per-recipient execution outcomes come from a REAL call to the
        configured bank endpoint (GV-009). `simulate_timeout` is the honest
        outage lever (IN-007 §3.2 UNKNOWN); without an endpoint the rail
        refuses rather than fabricating confirmed/failed lines."""
        payload_hash, cached = self._admit(request)
        if cached is not None:
            return cached

        # Validate routing numbers for bank disbursements
        for r in request.recipients:
            if r.rail_preference == "bank" and not validate_routing_number(r.routing_number):
                raise InvalidRoutingError(
                    f"Recipient {r.seller_ref} has invalid Bangladesh routing number: {r.routing_number}"
                )

        submission_time = datetime.now().isoformat()
        rail_batch_id = f"RAIL-{request.batch_ref}-{int(time.time())}"

        # Timeout handling: enter UNKNOWN state (IN-007 §3.2, IN-007-D-01)
        if simulate_timeout:
            result = self._unknown_result(
                request,
                rail_batch_id,
                submission_time,
                rail_type,
                "Gateway connection timed out after 30s. Awaiting read-back.",
            )
            # Store in idempotency store & gateway state
            self.store.set(request.idempotency_key, payload_hash, result)
            self._gateway_state[rail_batch_id] = result
            return result

        # GV-009 fail-closed: no bank endpoint configured means no execution
        # result may be produced — confirmed/failed only ever come from a
        # real rail call.
        if not self.bank_api_url:
            raise BankEndpointNotConfiguredError(
                "INT-007 bank payout endpoint not configured "
                f"(set {self.BANK_URL_ENV}) - refusing to simulate payout execution"
            )

        response = self._submit_to_bank(request, rail_batch_id)
        if response is None:
            result = self._unknown_result(
                request,
                rail_batch_id,
                submission_time,
                rail_type,
                "Rail endpoint unreachable after submission attempt. Awaiting read-back.",
            )
            self.store.set(request.idempotency_key, payload_hash, result)
            self._gateway_state[rail_batch_id] = result
            return result

        recipient_results: list[RecipientResult] = []
        confirmed_count = 0
        confirmed_amount = Decimal("0.00")
        failed_count = 0
        failed_amount = Decimal("0.00")
        unknown_count = 0
        unknown_amount = Decimal("0.00")

        by_ref: dict[str, dict] = {}
        for entry in response.get("recipients") or []:
            if isinstance(entry, dict) and entry.get("seller_ref"):
                by_ref[str(entry["seller_ref"])] = entry

        for r in request.recipients:
            entry = by_ref.get(r.seller_ref, {})
            raw_status = str(entry.get("status", "unknown")).strip().lower()
            if raw_status in ("confirmed", "successful", "completed"):
                confirmed_count += 1
                confirmed_amount += r.amount_bdt
                recipient_results.append(
                    RecipientResult(
                        seller_ref=r.seller_ref,
                        status=PayoutStatus.CONFIRMED,
                        rail_tx_id=_tx_id(entry),
                        amount_bdt=r.amount_bdt,
                    )
                )
            elif raw_status in ("failed", "rejected"):
                failed_count += 1
                failed_amount += r.amount_bdt
                recipient_results.append(
                    RecipientResult(
                        seller_ref=r.seller_ref,
                        status=PayoutStatus.FAILED,
                        rail_tx_id=_tx_id(entry),
                        amount_bdt=r.amount_bdt,
                        failure_reason=str(
                            entry.get("failure_reason") or self.DEFAULT_TX_FAILURE_REASON
                        ),
                    )
                )
            else:
                # The rail did not report a terminal outcome for this
                # recipient — UNKNOWN, resolved only by a read-back (FF-85).
                unknown_count += 1
                unknown_amount += r.amount_bdt
                recipient_results.append(
                    RecipientResult(
                        seller_ref=r.seller_ref,
                        status=PayoutStatus.UNKNOWN,
                        rail_tx_id=entry.get("rail_tx_id"),
                        amount_bdt=r.amount_bdt,
                        failure_reason=str(
                            entry.get("failure_reason")
                            or "Rail reported no terminal outcome. Awaiting read-back."
                        ),
                    )
                )

        if unknown_count:
            overall_status = PayoutStatus.UNKNOWN
        elif failed_count == 0:
            overall_status = PayoutStatus.CONFIRMED
        elif confirmed_count == 0:
            overall_status = PayoutStatus.FAILED
        else:
            # FF-94: a partial failure rolls up confirmed; the failure is
            # first-class on its own line.
            overall_status = PayoutStatus.CONFIRMED

        result = PayoutBatchResult(
            batch_ref=request.batch_ref,
            rail_batch_id=rail_batch_id,
            idempotency_key=request.idempotency_key,
            status=overall_status,
            submission_time=submission_time,
            recipient_results=tuple(recipient_results),
            total_amount=request.total_amount,
            recipient_count=request.recipient_count,
            confirmed_count=confirmed_count,
            confirmed_amount=confirmed_amount,
            failed_count=failed_count,
            failed_amount=failed_amount,
            unknown_count=unknown_count,
            unknown_amount=unknown_amount,
            rail_type=rail_type,
        )

        self.store.set(request.idempotency_key, payload_hash, result)
        self._gateway_state[rail_batch_id] = result
        return result

    def read_back_status(
        self,
        batch_ref: str,
        rail_batch_id: str,
        rail_outcome: PayoutStatus | None = None,
        *,
        bank_reference: str = "",
    ) -> PayoutBatchResult:
        """Record a read-back for status resolution (IN-007 §5.4, PT-05, FF-85).

        This library has no bank status query of its own: the outcome is the
        one the bank reported, passed in as ``rail_outcome`` together with the
        bank's own ``bank_reference`` for that read-back. Without an outcome
        the batch is returned unchanged — a read-back with no bank answer
        resolves nothing (it used to default to CONFIRMED)."""
        existing = self._gateway_state.get(rail_batch_id)
        if not existing:
            raise PayoutRailError(f"Rail batch '{rail_batch_id}' not found in rail registry")

        if rail_outcome is None or existing.status == rail_outcome:
            return existing  # nothing to resolve (no bank answer, or already in that state)
        if rail_outcome not in (PayoutStatus.CONFIRMED, PayoutStatus.FAILED):
            # FF-85: an inconclusive read-back never fabricates per-recipient outcomes
            raise InvalidStatusTransitionError(
                f"Read-back outcome '{rail_outcome.value}' cannot resolve rail batch "
                f"'{rail_batch_id}' from '{existing.status.value}' (FF-85)"
            )
        if not (bank_reference or "").strip():
            raise PayoutRailError(
                f"Resolving rail batch '{rail_batch_id}' to '{rail_outcome.value}' needs the "
                "bank's read-back reference"
            )

        # Resolve UNKNOWN into confirmed or failed via read-back
        resolved_recipients = []
        confirmed_count = 0
        confirmed_amount = Decimal("0.00")
        failed_count = 0
        failed_amount = Decimal("0.00")

        for rec in existing.recipient_results:
            if rail_outcome == PayoutStatus.CONFIRMED:
                confirmed_count += 1
                confirmed_amount += rec.amount_bdt
                resolved_recipients.append(
                    RecipientResult(
                        seller_ref=rec.seller_ref,
                        status=PayoutStatus.CONFIRMED,
                        rail_tx_id=rec.rail_tx_id,
                        amount_bdt=rec.amount_bdt,
                    )
                )
            else:
                failed_count += 1
                failed_amount += rec.amount_bdt
                resolved_recipients.append(
                    RecipientResult(
                        seller_ref=rec.seller_ref,
                        status=PayoutStatus.FAILED,
                        rail_tx_id=rec.rail_tx_id,
                        amount_bdt=rec.amount_bdt,
                        failure_reason=f"Bank read-back {bank_reference.strip()}: transfer failed",
                    )
                )

        updated_result = PayoutBatchResult(
            batch_ref=existing.batch_ref,
            rail_batch_id=existing.rail_batch_id,
            idempotency_key=existing.idempotency_key,
            status=rail_outcome,
            submission_time=existing.submission_time,
            recipient_results=tuple(resolved_recipients),
            total_amount=existing.total_amount,
            recipient_count=existing.recipient_count,
            confirmed_count=confirmed_count,
            confirmed_amount=confirmed_amount,
            failed_count=failed_count,
            failed_amount=failed_amount,
            unknown_count=0,
            unknown_amount=Decimal("0.00"),
            rail_type=existing.rail_type,
        )

        # Update cache and gateway state: an idempotent replay must not keep
        # serving the pre-resolution UNKNOWN outcome
        self._gateway_state[rail_batch_id] = updated_result
        self.store.replace_result(existing.idempotency_key, updated_result)
        return updated_result

    def generate_beftn_fallback_batch(
        self,
        request: PayoutBatchRequest,
        batch_number: int = 1,
        settlement_date: date | None = None,
    ) -> PayoutBatchResult:
        """Generate BEFTN 128-byte fallback file when direct API is unavailable.

        Same admission as the primary rail (mandatory key, payload conflict,
        control totals FF-94). For a key already cached:
        - a BEFTN result is replayed as-is (never a second file);
        - a definitive no-money API failure (FAILED, nothing confirmed or
          unknown) is a legitimate new attempt on this rail, and its BEFTN
          result replaces the cache entry;
        - any API outcome where money moved or may have moved is refused
          (a file would be a double payout; FF-85 needs a read-back first)."""
        payload_hash, cached = self._admit(request)
        if cached is not None:
            if cached.rail_type == "beftn":
                return cached
            no_money_moved = (
                cached.status == PayoutStatus.FAILED
                and cached.confirmed_count == 0
                and cached.unknown_count == 0
            )
            if not no_money_moved:
                raise PayoutRailError(
                    f"BEFTN fallback refused for Idempotency-Key '{request.idempotency_key}': "
                    f"the {cached.rail_type} rail outcome is '{cached.status.value}' "
                    f"(confirmed={cached.confirmed_count}, unknown={cached.unknown_count}); "
                    "a fallback file could pay twice"
                )

        settle_d = settlement_date or date.today()
        header = BeftnBatchHeader(
            company_name=self.company_name,
            company_id=self.company_id,
            originating_routing=self.originating_routing,
            batch_number=batch_number,
            settlement_date=settle_d,
            description="SELLER_PAYOUT",
        )

        entries = [
            BeftnEntry(
                employee_id=r.seller_ref,
                employee_name=r.seller_name,
                routing_number=r.routing_number,
                account_number=r.account_number,
                amount_bdt=r.amount_bdt,
            )
            for r in request.recipients
        ]

        raw_file = generate_beftn_batch_file(header, entries)
        rail_batch_id = f"BEFTN-{request.batch_ref}-{settle_d.strftime('%Y%m%d')}"

        # A generated BEFTN file is not a settled transfer: every line stays
        # UNKNOWN until the bank's read-back reports it (it used to be
        # CONFIRMED the moment the file was written).
        recipient_results = tuple(
            RecipientResult(
                seller_ref=r.seller_ref,
                status=PayoutStatus.UNKNOWN,
                rail_tx_id=None,
                amount_bdt=r.amount_bdt,
                failure_reason="BEFTN file generated; awaiting bank read-back.",
            )
            for r in request.recipients
        )

        result = PayoutBatchResult(
            batch_ref=request.batch_ref,
            rail_batch_id=rail_batch_id,
            idempotency_key=request.idempotency_key,
            status=PayoutStatus.UNKNOWN,
            submission_time=datetime.now().isoformat(),
            recipient_results=recipient_results,
            total_amount=request.total_amount,
            recipient_count=request.recipient_count,
            confirmed_count=0,
            confirmed_amount=Decimal("0.00"),
            failed_count=0,
            failed_amount=Decimal("0.00"),
            unknown_count=request.recipient_count,
            unknown_amount=request.total_amount,
            rail_type="beftn",
            beftn_raw=raw_file,
        )

        self.store.set(request.idempotency_key, payload_hash, result)
        self._gateway_state[rail_batch_id] = result
        return result
