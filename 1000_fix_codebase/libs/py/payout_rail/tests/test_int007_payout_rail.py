"""libs/py/payout_rail - INT-007 seller payout rail tests (lib-level).

Pins the money-safety contract of the rail on its own:

- IN-007 §5.1: an Idempotency-Key is mandatory for every money operation.
- IN-007 §5.2 / IN-007-D-03: 7-day idempotent replay; a reused key with a
  different payload is a conflict; entries expire after the window.
- IN-007 §11.3 / FF-94: declared count and amount must match the
  recipients; results report count and amount separately per outcome.
- IN-007 §3.2 / IN-007-D-01 / FF-85: a timeout is a first-class UNKNOWN
  state, resolved only by a read-back - and an inconclusive read-back
  never fabricates an outcome (regression).
- BEFTN fallback: the 128-byte file is produced through the payroll kernel.
- GV-009: execution outcomes come from a REAL bank endpoint call - the
  endpoint is faked at the transport boundary (urlopen) so every
  confirmed/failed line below came over the wire, and with no endpoint
  configured the rail refuses instead of simulating execution.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = [pytest.mark.financial]

_ROOT = Path(__file__).resolve().parents[4]  # codebase root (libs.py.*)
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import libs.py.payout_rail as payout_rail
from libs.py.payout_rail import int007_rail as rail_mod
from libs.py.payout_rail.int007_rail import (
    SEVEN_DAYS_SECONDS,
    BankEndpointNotConfiguredError,
    IdempotencyConflictError,
    InMemoryIdempotencyStore,
    INT007PayoutRail,
    InvalidRoutingError,
    InvalidStatusTransitionError,
    PayoutBatchRequest,
    PayoutRailError,
    PayoutRecipient,
    PayoutStatus,
)

D = Decimal
T0 = 1_790_000_000.0


class _Clock:
    def __init__(self, now: float = T0) -> None:
        self.now = now

    def time(self) -> float:
        return self.now


class _FakeBankResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeBankResponse:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


def _bank_answer(monkeypatch: pytest.MonkeyPatch, responder) -> list:
    """Fake the bank payout endpoint at the transport boundary. The responder
    receives the POSTed batch body and returns the rail's response dict (or
    raises an exception to simulate a transport failure)."""
    calls: list = []

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        outcome = responder(json.loads(request.data or b"{}"))
        if isinstance(outcome, Exception):
            raise outcome
        return _FakeBankResponse(json.dumps(outcome).encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    return calls


def _rail_response(body: dict, confirmed: set[str]) -> dict:
    return {
        "status": "confirmed",
        "recipients": [
            {
                "seller_ref": r["seller_ref"],
                "status": "confirmed" if r["seller_ref"] in confirmed else "failed",
                "failure_reason": None
                if r["seller_ref"] in confirmed
                else INT007PayoutRail.DEFAULT_TX_FAILURE_REASON,
            }
            for r in body["recipients"]
        ],
    }


def _confirm_everyone(body: dict) -> dict:
    return _rail_response(body, {r["seller_ref"] for r in body["recipients"]})


def _fail_s2(body: dict) -> dict:
    return _rail_response(body, {"S1"})


def _fail_everyone(body: dict) -> dict:
    return _rail_response(body, set())


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> _Clock:
    """Freeze the rail's view of time.time() (idempotency TTL, rail batch id)."""
    c = _Clock()
    monkeypatch.setattr(rail_mod, "time", SimpleNamespace(time=c.time))
    return c


@pytest.fixture
def rail(clock: _Clock, monkeypatch: pytest.MonkeyPatch) -> INT007PayoutRail:
    """A rail wired to a (transport-faked) REAL bank endpoint confirming
    everyone; tests re-fake the endpoint when they need other outcomes."""
    monkeypatch.setenv(INT007PayoutRail.BANK_URL_ENV, "http://localhost:9/bank")
    _bank_answer(monkeypatch, _confirm_everyone)
    return INT007PayoutRail()


def _recipient(ref: str = "S1", amount: str = "5000.00", **overrides: object) -> PayoutRecipient:
    fields: dict[str, object] = {
        "seller_ref": ref,
        "seller_name": f"Seller {ref}",
        "account_number": "1234567890",
        "routing_number": "125272355",
        "amount_bdt": D(amount),
        "disbursement_ref": f"DISB-{ref}",
    }
    fields.update(overrides)
    return PayoutRecipient(**fields)  # type: ignore[arg-type]


def _request(
    recipients: tuple[PayoutRecipient, ...] | None = None,
    key: str = "IDEMP-KEY-001",
    **overrides: object,
) -> PayoutBatchRequest:
    recips = recipients or (_recipient("S1", "5000.00"), _recipient("S2", "7500.00"))
    fields: dict[str, object] = {
        "batch_ref": "BATCH-2026-10-01",
        "period": "2026-10",
        "recipients": recips,
        "idempotency_key": key,
        "total_amount": sum((r.amount_bdt for r in recips), D("0.00")),
        "recipient_count": len(recips),
    }
    fields.update(overrides)
    return PayoutBatchRequest(**fields)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Package surface
# ---------------------------------------------------------------------------


def test_package_reexports_the_rail_module() -> None:
    assert sorted(payout_rail.__all__) == sorted(
        [
            "BankEndpointNotConfiguredError",
            "INT007PayoutRail",
            "IdempotencyConflictError",
            "PayoutBatchRequest",
            "PayoutBatchResult",
            "PayoutRailError",
            "PayoutRecipient",
            "PayoutStatus",
            "RecipientResult",
        ]
    )
    for name in payout_rail.__all__:
        assert getattr(payout_rail, name) is getattr(rail_mod, name)


def test_error_hierarchy_and_status_values() -> None:
    for exc in (IdempotencyConflictError, InvalidRoutingError, InvalidStatusTransitionError):
        assert issubclass(exc, PayoutRailError)
    assert issubclass(PayoutRailError, Exception)
    assert [s.value for s in PayoutStatus] == [
        "initiated",
        "executing",
        "confirmed",
        "unknown",
        "failed",
    ]
    assert PayoutStatus("unknown") is PayoutStatus.UNKNOWN
    assert PayoutStatus.CONFIRMED == "confirmed"  # str-enum: serialises as its value


def test_recipient_defaults_to_bank_rail() -> None:
    r = _recipient()
    assert r.rail_preference == "bank"
    assert r.wallet_number is None


def test_seven_day_retention_constant() -> None:
    assert SEVEN_DAYS_SECONDS == 604_800


# ---------------------------------------------------------------------------
# Idempotency store
# ---------------------------------------------------------------------------


def test_store_miss_returns_none(clock: _Clock) -> None:
    assert InMemoryIdempotencyStore().get("nope") is None


def test_store_roundtrip_and_expiry_after_seven_days(clock: _Clock, rail: INT007PayoutRail) -> None:
    store = InMemoryIdempotencyStore()
    result = rail.submit_payout_batch(_request())
    store.set("K", "hash-1", result)
    assert store.get("K") == ("hash-1", result)

    clock.now = T0 + SEVEN_DAYS_SECONDS  # exactly at the window edge: retained
    assert store.get("K") == ("hash-1", result)

    clock.now = T0 + SEVEN_DAYS_SECONDS + 1
    assert store.get("K") is None


def test_store_set_evicts_only_expired_entries(clock: _Clock, rail: INT007PayoutRail) -> None:
    store = InMemoryIdempotencyStore(ttl_seconds=10)
    result = rail.submit_payout_batch(_request())
    store.set("old", "h-old", result)
    clock.now = T0 + 5
    store.set("young", "h-young", result)
    clock.now = T0 + 11  # "old" is 11s old, "young" 6s
    store.set("new", "h-new", result)
    assert store.get("old") is None
    assert store.get("young") == ("h-young", result)
    assert store.get("new") == ("h-new", result)


# ---------------------------------------------------------------------------
# Submission
# ---------------------------------------------------------------------------


def test_unconfigured_bank_endpoint_refuses_to_simulate_execution(
    clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """GV-009: with no bank endpoint the rail must not fabricate per-recipient
    confirmed/failed outcomes — it refuses, and nothing is cached."""
    monkeypatch.delenv(INT007PayoutRail.BANK_URL_ENV, raising=False)
    rail = INT007PayoutRail()
    assert rail.bank_api_url == ""
    with pytest.raises(
        BankEndpointNotConfiguredError,
        match=r"bank payout endpoint not configured.*refusing to simulate payout execution",
    ):
        rail.submit_payout_batch(_request())
    assert rail.store.get("IDEMP-KEY-001") is None


def test_execution_posts_the_batch_to_the_bank_endpoint(
    rail: INT007PayoutRail, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = _bank_answer(monkeypatch, _confirm_everyone)
    result = rail.submit_payout_batch(_request())
    assert result.status is PayoutStatus.CONFIRMED
    request, timeout = calls[0]
    assert request.full_url == "http://localhost:9/bank/payout-batches"
    assert request.get_method() == "POST"
    assert request.get_header("Idempotency-key") == "IDEMP-KEY-001"
    assert timeout == 30
    body = json.loads(request.data)
    assert body["batch_ref"] == "BATCH-2026-10-01"
    assert body["idempotency_key"] == "IDEMP-KEY-001"
    assert (body["recipient_count"], body["total_amount"]) == (2, "12500.00")
    assert [r["seller_ref"] for r in body["recipients"]] == ["S1", "S2"]
    assert body["recipients"][0]["amount_bdt"] == "5000.00"
    assert body["recipients"][0]["routing_number"] == "125272355"


def test_transport_failure_is_unknown_never_a_fabricated_outcome(
    clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The endpoint being unreachable is an outage, not a result: the batch
    enters UNKNOWN (money may have moved) and the replay serves it."""
    monkeypatch.setenv(INT007PayoutRail.BANK_URL_ENV, "http://localhost:9/bank")
    rail = INT007PayoutRail()
    _bank_answer(monkeypatch, lambda body: urllib.error.URLError("connection refused"))
    result = rail.submit_payout_batch(_request())
    assert result.status is PayoutStatus.UNKNOWN
    assert (result.unknown_count, result.unknown_amount) == (2, D("12500.00"))
    assert all("Awaiting read-back" in (r.failure_reason or "") for r in result.recipient_results)
    assert rail.submit_payout_batch(_request()) is result


def test_unresolved_rail_recipient_stays_unknown(
    rail: INT007PayoutRail, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A rail response that omits a recipient resolves nothing for them:
    FF-85 keeps the line UNKNOWN; the batch rolls up UNKNOWN."""
    _bank_answer(
        monkeypatch,
        lambda body: {
            "status": "unknown",
            "recipients": [{"seller_ref": "S1", "status": "confirmed"}],
        },
    )
    result = rail.submit_payout_batch(_request())
    assert result.status is PayoutStatus.UNKNOWN
    assert (result.confirmed_count, result.unknown_count) == (1, 1)
    s1, s2 = result.recipient_results
    assert s1.status is PayoutStatus.CONFIRMED
    assert s1.rail_tx_id is None  # the rail sent none; none is invented
    assert s2.status is PayoutStatus.UNKNOWN
    assert "Awaiting read-back" in (s2.failure_reason or "")


def test_successful_submission_confirms_every_recipient(
    clock: _Clock, rail: INT007PayoutRail
) -> None:
    result = rail.submit_payout_batch(_request())
    batch_id = f"RAIL-BATCH-2026-10-01-{int(T0)}"
    assert result.rail_batch_id == batch_id
    assert result.status is PayoutStatus.CONFIRMED
    assert result.rail_type == "api"
    assert result.idempotency_key == "IDEMP-KEY-001"
    assert result.beftn_raw is None
    assert (result.recipient_count, result.total_amount) == (2, D("12500.00"))
    assert (result.confirmed_count, result.confirmed_amount) == (2, D("12500.00"))
    assert (result.failed_count, result.failed_amount) == (0, D("0.00"))
    assert (result.unknown_count, result.unknown_amount) == (0, D("0.00"))
    assert [
        (r.seller_ref, r.status, r.rail_tx_id, r.amount_bdt) for r in result.recipient_results
    ] == [
        ("S1", PayoutStatus.CONFIRMED, None, D("5000.00")),
        ("S2", PayoutStatus.CONFIRMED, None, D("7500.00")),
    ]
    assert all(r.failure_reason is None for r in result.recipient_results)


def test_rail_type_is_recorded(rail: INT007PayoutRail) -> None:
    assert rail.submit_payout_batch(_request(), rail_type="bKash").rail_type == "bKash"


@pytest.mark.parametrize("key", ["", "   "])
def test_idempotency_key_is_mandatory(rail: INT007PayoutRail, key: str) -> None:
    with pytest.raises(PayoutRailError, match=r"Idempotency-Key is mandatory .*IN-007 §5\.1"):
        rail.submit_payout_batch(_request(key=key))


def test_replay_within_window_returns_the_cached_result_without_re_executing(
    clock: _Clock, rail: INT007PayoutRail
) -> None:
    first = rail.submit_payout_batch(_request())
    clock.now = T0 + 3600
    # even a timeout simulation cannot alter a replayed outcome
    again = rail.submit_payout_batch(_request(), simulate_timeout=True)
    assert again is first


def test_replay_ignores_fields_outside_the_payload_hash(rail: INT007PayoutRail) -> None:
    first = rail.submit_payout_batch(_request())
    renamed = (
        _recipient("S1", "5000.00", seller_name="Renamed", disbursement_ref="X"),
        _recipient("S2", "7500.00"),
    )
    assert rail.submit_payout_batch(_request(renamed, period="2026-11")) is first


@pytest.mark.parametrize(
    "changed",
    [
        {"batch_ref": "BATCH-OTHER"},
        {
            "recipients": (
                _recipient("S1", "5000.00"),
                _recipient("S2", "7500.00", account_number="999"),
            )
        },
        {
            "recipients": (
                _recipient("S1", "5000.00"),
                _recipient("S2", "7500.00", routing_number="225262531"),
            )
        },
        {"recipients": (_recipient("S1", "5000.00"), _recipient("S3", "7500.00"))},
        {
            "recipients": (_recipient("S1", "5000.00"), _recipient("S2", "7400.00")),
            "total_amount": D("12400.00"),
        },
    ],
)
def test_reused_key_with_a_different_payload_is_a_conflict(
    rail: INT007PayoutRail, changed: dict[str, object]
) -> None:
    rail.submit_payout_batch(_request())
    with pytest.raises(IdempotencyConflictError, match="'IDEMP-KEY-001' reused"):
        rail.submit_payout_batch(_request(**changed))


def test_key_reuse_after_the_seven_day_window_executes_afresh(
    clock: _Clock, rail: INT007PayoutRail
) -> None:
    first = rail.submit_payout_batch(_request())
    clock.now = T0 + SEVEN_DAYS_SECONDS + 1
    later = rail.submit_payout_batch(_request(batch_ref="BATCH-2026-10-08"))
    assert later.rail_batch_id == f"RAIL-BATCH-2026-10-08-{int(clock.now)}"
    assert later.rail_batch_id != first.rail_batch_id


@pytest.mark.parametrize(
    "overrides",
    [
        {"recipient_count": 3},
        {"total_amount": D("12500.01")},
    ],
)
def test_control_total_mismatch_rejected_and_not_cached(
    rail: INT007PayoutRail, overrides: dict[str, object]
) -> None:
    with pytest.raises(PayoutRailError, match=r"Control totals mismatch.*\(FF-94\)"):
        rail.submit_payout_batch(_request(**overrides))
    assert rail.store.get("IDEMP-KEY-001") is None
    assert rail.submit_payout_batch(_request()).status is PayoutStatus.CONFIRMED


def test_control_total_ignores_trailing_zero_scale(rail: INT007PayoutRail) -> None:
    result = rail.submit_payout_batch(_request(total_amount=D("12500")))
    assert result.confirmed_amount == D("12500.00")


def test_invalid_bank_routing_rejected(rail: INT007PayoutRail) -> None:
    recips = (_recipient("S1"), _recipient("S2", routing_number="12345"))
    with pytest.raises(
        InvalidRoutingError, match="S2 has invalid Bangladesh routing number: 12345"
    ):
        rail.submit_payout_batch(_request(recips))
    assert rail.store.get("IDEMP-KEY-001") is None


def test_bengali_digit_routing_rejected_for_bank_rail(rail: INT007PayoutRail) -> None:
    bengali = "১২৫২৭২৩৫৫"
    with pytest.raises(InvalidRoutingError):
        rail.submit_payout_batch(_request((_recipient("S1", routing_number=bengali),)))


@pytest.mark.parametrize("wallet_rail", ["bKash", "Nagad"])
def test_wallet_rails_do_not_need_a_bank_routing_number(
    rail: INT007PayoutRail, wallet_rail: str
) -> None:
    recips = (
        _recipient(
            "S1", routing_number="", wallet_number="01711000000", rail_preference=wallet_rail
        ),
    )
    result = rail.submit_payout_batch(_request(recips))
    assert result.status is PayoutStatus.CONFIRMED
    assert result.confirmed_amount == D("5000.00")


def test_partial_failure_reports_counts_and_amounts_separately(
    rail: INT007PayoutRail, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bank_answer(monkeypatch, _fail_s2)
    result = rail.submit_payout_batch(_request())
    # FF-94: the batch rolls up as confirmed, the failure is first-class per line
    assert result.status is PayoutStatus.CONFIRMED
    assert (result.confirmed_count, result.confirmed_amount) == (1, D("5000.00"))
    assert (result.failed_count, result.failed_amount) == (1, D("7500.00"))
    s1, s2 = result.recipient_results
    assert s1.status is PayoutStatus.CONFIRMED and s1.failure_reason is None
    assert s2.status is PayoutStatus.FAILED
    assert s2.rail_tx_id is None
    assert s2.failure_reason == "Beneficiary account rejected by receiving bank"


def test_all_recipients_failing_fails_the_batch(
    rail: INT007PayoutRail, monkeypatch: pytest.MonkeyPatch
) -> None:
    _bank_answer(monkeypatch, _fail_everyone)
    result = rail.submit_payout_batch(_request())
    assert result.status is PayoutStatus.FAILED
    assert (result.confirmed_count, result.confirmed_amount) == (0, D("0.00"))
    assert (result.failed_count, result.failed_amount) == (2, D("12500.00"))
    assert rail.store.get("IDEMP-KEY-001")[1] is result


# ---------------------------------------------------------------------------
# Timeout -> UNKNOWN -> read-back
# ---------------------------------------------------------------------------


def test_timeout_enters_first_class_unknown_state(rail: INT007PayoutRail) -> None:
    result = rail.submit_payout_batch(_request(), simulate_timeout=True)
    assert result.status is PayoutStatus.UNKNOWN
    assert (result.unknown_count, result.unknown_amount) == (2, D("12500.00"))
    assert (result.confirmed_count, result.failed_count) == (0, 0)
    assert (result.confirmed_amount, result.failed_amount) == (D("0.00"), D("0.00"))
    for line in result.recipient_results:
        assert line.status is PayoutStatus.UNKNOWN
        assert line.rail_tx_id is None
        assert "Awaiting read-back" in (line.failure_reason or "")
    # the UNKNOWN outcome is what an idempotent replay returns (FF-85: only a
    # read-back may move it)
    assert rail.submit_payout_batch(_request()) is result


def test_read_back_resolves_unknown_to_confirmed(rail: INT007PayoutRail) -> None:
    pending = rail.submit_payout_batch(_request(), simulate_timeout=True, rail_type="Nagad")
    resolved = rail.read_back_status(
        pending.batch_ref, pending.rail_batch_id, PayoutStatus.CONFIRMED, bank_reference=BANK_REF
    )
    assert resolved.status is PayoutStatus.CONFIRMED
    assert (resolved.confirmed_count, resolved.confirmed_amount) == (2, D("12500.00"))
    assert (resolved.failed_count, resolved.unknown_count) == (0, 0)
    assert resolved.unknown_amount == D("0.00")
    assert [r.rail_tx_id for r in resolved.recipient_results] == [None, None]
    # identity fields carried over from the original submission
    assert resolved.rail_batch_id == pending.rail_batch_id
    assert resolved.idempotency_key == pending.idempotency_key
    assert resolved.submission_time == pending.submission_time
    assert resolved.rail_type == "Nagad"
    # a repeated read-back of the now-terminal state is a no-op
    again = rail.read_back_status(pending.batch_ref, pending.rail_batch_id)
    assert again is resolved


def test_read_back_resolves_unknown_to_failed(rail: INT007PayoutRail) -> None:
    pending = rail.submit_payout_batch(_request(), simulate_timeout=True)
    resolved = rail.read_back_status(
        pending.batch_ref, pending.rail_batch_id, PayoutStatus.FAILED, bank_reference=BANK_REF
    )
    assert resolved.status is PayoutStatus.FAILED
    assert (resolved.failed_count, resolved.failed_amount) == (2, D("12500.00"))
    assert (resolved.confirmed_count, resolved.confirmed_amount) == (0, D("0.00"))
    for line in resolved.recipient_results:
        assert line.status is PayoutStatus.FAILED
        assert line.failure_reason == f"Bank read-back {BANK_REF}: transfer failed"


def test_read_back_of_unknown_rail_batch_rejected(rail: INT007PayoutRail) -> None:
    with pytest.raises(PayoutRailError, match="'RAIL-NOPE' not found"):
        rail.read_back_status("B", "RAIL-NOPE")


def test_read_back_of_terminal_batch_with_same_outcome_is_a_no_op(rail: INT007PayoutRail) -> None:
    done = rail.submit_payout_batch(_request())
    assert rail.read_back_status(done.batch_ref, done.rail_batch_id) is done


def test_regression_inconclusive_read_back_keeps_unknown(rail: INT007PayoutRail) -> None:
    """Regression (FF-85): a read-back that is still UNKNOWN used to mark every
    recipient FAILED ("Read-back confirmed transfer failure") with
    failed_count=n under an UNKNOWN batch status - a fabricated failure that
    invites a second disbursement. It must leave the batch untouched."""
    pending = rail.submit_payout_batch(_request(), simulate_timeout=True)
    still = rail.read_back_status(
        pending.batch_ref, pending.rail_batch_id, PayoutStatus.UNKNOWN, bank_reference=BANK_REF
    )
    assert still is pending
    assert (still.unknown_count, still.failed_count) == (2, 0)
    assert all(r.status is PayoutStatus.UNKNOWN for r in still.recipient_results)


@pytest.mark.parametrize("outcome", [PayoutStatus.INITIATED, PayoutStatus.EXECUTING])
def test_regression_non_terminal_read_back_outcome_rejected(
    rail: INT007PayoutRail, outcome: PayoutStatus
) -> None:
    """Regression (FF-85): a non-terminal read-back outcome cannot resolve an
    UNKNOWN batch; it now raises instead of fabricating FAILED lines."""
    pending = rail.submit_payout_batch(_request(), simulate_timeout=True)
    with pytest.raises(InvalidStatusTransitionError, match=f"'{outcome.value}' cannot resolve"):
        rail.read_back_status(pending.batch_ref, pending.rail_batch_id, outcome)
    # the gateway still holds the UNKNOWN batch
    assert (
        rail.read_back_status(pending.batch_ref, pending.rail_batch_id, PayoutStatus.UNKNOWN)
        is pending
    )


def test_regression_confirmed_batch_cannot_regress_to_unknown(rail: INT007PayoutRail) -> None:
    done = rail.submit_payout_batch(_request())
    with pytest.raises(InvalidStatusTransitionError, match="from 'confirmed'"):
        rail.read_back_status(done.batch_ref, done.rail_batch_id, PayoutStatus.UNKNOWN)


# ---------------------------------------------------------------------------
# BEFTN fallback rail
# ---------------------------------------------------------------------------


def test_beftn_fallback_builds_a_128_byte_file(rail: INT007PayoutRail) -> None:
    request = _request(key="IDEMP-BEFTN-001")  # gitleaks:allow
    result = rail.generate_beftn_fallback_batch(
        request, batch_number=7, settlement_date=date(2026, 10, 4)
    )
    assert result.rail_type == "beftn"
    assert result.rail_batch_id == "BEFTN-BATCH-2026-10-01-20261004"
    assert result.status is PayoutStatus.UNKNOWN  # awaiting the bank's read-back
    assert (result.confirmed_count, result.confirmed_amount) == (0, D("0.00"))
    assert (result.unknown_count, result.unknown_amount) == (2, D("12500.00"))
    assert result.failed_count == 0
    assert [r.rail_tx_id for r in result.recipient_results] == [None, None]
    assert result.beftn_raw is not None
    lines = result.beftn_raw.split("\r\n")[:-1]
    assert [line[0] for line in lines] == ["1", "5", "6", "6", "8", "9"]
    assert all(len(line.encode("ascii")) == 128 for line in lines)
    assert lines[0][63:86] == "1000FiX Services Ltd".ljust(23)
    assert lines[1][40:50] == "FIX-CORP-0"  # company id (10-wide)
    assert lines[1][53:63] == "SELLER_PAY"
    assert lines[1][69:75] == "261004"
    assert lines[1][79:94] == "12527235" + "0000007"
    assert lines[2][39:54] == "S1".ljust(15)
    assert lines[2][54:76] == "Seller S1".ljust(22)
    assert lines[3][29:39] == "0000750000"
    assert lines[4][32:44] == "000001250000"
    # cached under its key and registered with the gateway for read-back
    assert rail.submit_payout_batch(request) is result
    assert rail.read_back_status(result.batch_ref, result.rail_batch_id) is result


def test_beftn_fallback_defaults_to_today_and_custom_originator(
    monkeypatch: pytest.MonkeyPatch, clock: _Clock
) -> None:
    class _Today(date):
        @classmethod
        def today(cls):  # type: ignore[override]
            return cls(2026, 10, 5)

    monkeypatch.setattr(rail_mod, "date", _Today)
    store = InMemoryIdempotencyStore()
    custom = INT007PayoutRail(
        idempotency_store=store,
        originating_routing="020260123",
        company_name="FIX MARKETPLACE",
        company_id="MKT-01",
    )
    assert custom.store is store
    result = custom.generate_beftn_fallback_batch(
        _request(key="IDEMP-BEFTN-002")  # gitleaks:allow
    )
    assert result.rail_batch_id == "BEFTN-BATCH-2026-10-01-20261005"
    lines = (result.beftn_raw or "").split("\r\n")
    assert lines[0][13:23] == "020260123 "
    assert lines[0][63:86] == "FIX MARKETPLACE".ljust(23)
    assert lines[1][40:50] == "MKT-01    "
    assert lines[1][69:75] == "261005"
    assert lines[1][87:94] == "0000001"  # default batch number
    assert store.get("IDEMP-BEFTN-002") is not None


def test_beftn_fallback_rejects_an_invalid_beneficiary_routing(rail: INT007PayoutRail) -> None:
    bad = _request(
        (_recipient("S1", routing_number="BADROUT"),),
        key="IDEMP-BEFTN-003",  # gitleaks:allow
    )
    with pytest.raises(ValueError, match="Invalid beneficiary routing number: BADROUT for S1"):
        rail.generate_beftn_fallback_batch(bad, settlement_date=date(2026, 10, 4))
    assert rail.store.get("IDEMP-BEFTN-003") is None


def test_result_objects_are_immutable(rail: INT007PayoutRail) -> None:
    result = rail.submit_payout_batch(_request())
    with pytest.raises(AttributeError):
        result.status = PayoutStatus.FAILED  # type: ignore[misc]
    assert replace(result, status=PayoutStatus.FAILED).status is PayoutStatus.FAILED
    assert result.status is PayoutStatus.CONFIRMED


# ---------------------------------------------------------------------------
# Regression: the BEFTN fallback shares the primary rail's admission checks
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("responder", "simulate_timeout", "status"),
    [
        (_confirm_everyone, False, "confirmed"),  # API paid everyone
        (_fail_s2, False, "confirmed"),  # API paid S1 only
        (None, True, "unknown"),  # money may have moved (FF-85)
    ],
)
def test_regression_fallback_refused_when_api_money_moved_or_may_have(
    rail: INT007PayoutRail,
    monkeypatch: pytest.MonkeyPatch,
    responder,
    simulate_timeout: bool,
    status: str,
) -> None:
    """Regression (c): the fallback ignored the idempotency cache, so a key the
    API rail had already (or possibly) paid produced a second disbursement
    file. It must refuse - neither a file nor the API result is returned."""
    if responder is not None:
        _bank_answer(monkeypatch, responder)
        api = rail.submit_payout_batch(_request())
    else:
        api = rail.submit_payout_batch(_request(), simulate_timeout=True)
    with pytest.raises(PayoutRailError, match=f"outcome is '{status}'.*could pay twice"):
        rail.generate_beftn_fallback_batch(_request(), settlement_date=date(2026, 10, 4))
    assert rail.store.get("IDEMP-KEY-001")[1] is api


@pytest.mark.parametrize("status", [PayoutStatus.INITIATED, PayoutStatus.EXECUTING])
def test_regression_fallback_refused_for_in_flight_api_outcomes(
    rail: INT007PayoutRail, monkeypatch: pytest.MonkeyPatch, status: PayoutStatus
) -> None:
    _bank_answer(monkeypatch, _fail_everyone)
    request = _request()
    in_flight = replace(
        rail.submit_payout_batch(request),
        status=status,
        failed_count=0,
    )
    rail.store.set(request.idempotency_key, rail._compute_payload_hash(request), in_flight)
    with pytest.raises(PayoutRailError, match=f"outcome is '{status.value}'"):
        rail.generate_beftn_fallback_batch(request)


def test_regression_fallback_after_definitive_api_failure_generates_the_file(
    rail: INT007PayoutRail,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression (b), the cd_settlement_ext sequence: API dispatch FAILED for
    every recipient (run stays 'approved'), then the BEFTN fallback under the
    SAME key must produce the file and replace the cached API outcome."""
    _bank_answer(monkeypatch, _fail_everyone)
    request = _request()
    api = rail.submit_payout_batch(request)
    assert (api.status, api.confirmed_count, api.unknown_count) == (PayoutStatus.FAILED, 0, 0)
    fallback = rail.generate_beftn_fallback_batch(request, settlement_date=date(2026, 10, 4))
    assert fallback.beftn_raw is not None
    assert fallback.beftn_raw.encode("ascii")  # what the addon writes
    assert fallback.rail_type == "beftn"
    assert fallback.status is PayoutStatus.UNKNOWN
    assert fallback.idempotency_key == api.idempotency_key
    assert rail.store.get("IDEMP-KEY-001")[1] is fallback
    # (a) a replay of the fallback never produces a second file
    assert rail.generate_beftn_fallback_batch(request) is fallback
    assert rail.submit_payout_batch(request) is fallback


def test_regression_fallback_is_idempotent_on_its_own_key(rail: INT007PayoutRail) -> None:
    first = rail.generate_beftn_fallback_batch(
        _request(key="IDEMP-BEFTN-010"),  # gitleaks:allow
        settlement_date=date(2026, 10, 4),
    )
    again = rail.generate_beftn_fallback_batch(
        _request(key="IDEMP-BEFTN-010"),  # gitleaks:allow
        settlement_date=date(2026, 10, 5),
    )
    assert again is first
    assert again.rail_batch_id == "BEFTN-BATCH-2026-10-01-20261004"


def test_regression_fallback_key_reuse_with_different_payload_conflicts(
    rail: INT007PayoutRail,
) -> None:
    """Regression: a different payload under a cached key overwrote the cache
    entry instead of raising IdempotencyConflictError."""
    paid = rail.submit_payout_batch(_request())
    changed = _request(
        (_recipient("S1", "5000.00"), _recipient("S2", "7500.00", account_number="9"))
    )
    with pytest.raises(IdempotencyConflictError, match="'IDEMP-KEY-001' reused"):
        rail.generate_beftn_fallback_batch(changed)
    assert rail.store.get("IDEMP-KEY-001")[1] is paid


@pytest.mark.parametrize("key", ["", "  "])
def test_regression_fallback_requires_an_idempotency_key(rail: INT007PayoutRail, key: str) -> None:
    with pytest.raises(PayoutRailError, match="Idempotency-Key is mandatory"):
        rail.generate_beftn_fallback_batch(_request(key=key))


@pytest.mark.parametrize("overrides", [{"recipient_count": 1}, {"total_amount": D("13000.00")}])
def test_regression_fallback_enforces_control_totals(
    rail: INT007PayoutRail, overrides: dict[str, object]
) -> None:
    """Regression (FF-94): the fallback reported the declared total as
    confirmed even when it differed from what the file disburses."""
    with pytest.raises(PayoutRailError, match=r"Control totals mismatch.*\(FF-94\)"):
        rail.generate_beftn_fallback_batch(
            _request(key="IDEMP-BEFTN-011", **overrides)  # gitleaks:allow
        )
    assert rail.store.get("IDEMP-BEFTN-011") is None


# ---------------------------------------------------------------------------
# Regression: a read-back resolution reaches the idempotency cache
# ---------------------------------------------------------------------------


def test_regression_replay_after_read_back_returns_the_resolved_outcome(
    rail: INT007PayoutRail,
) -> None:
    """Regression: read_back_status updated only the gateway, so a replay of
    the key kept serving the stale UNKNOWN outcome after resolution."""
    pending = rail.submit_payout_batch(_request(), simulate_timeout=True)
    resolved = rail.read_back_status(
        pending.batch_ref, pending.rail_batch_id, PayoutStatus.CONFIRMED, bank_reference=BANK_REF
    )
    assert rail.submit_payout_batch(_request()) is resolved
    with pytest.raises(PayoutRailError, match="outcome is 'confirmed'"):
        rail.generate_beftn_fallback_batch(_request())


def test_regression_failed_read_back_opens_the_fallback(rail: INT007PayoutRail) -> None:
    """Regression: once a read-back confirms the UNKNOWN batch FAILED, the
    cache must say so - the fallback then generates the file."""
    pending = rail.submit_payout_batch(_request(), simulate_timeout=True)
    with pytest.raises(PayoutRailError, match="outcome is 'unknown'"):
        rail.generate_beftn_fallback_batch(_request())
    rail.read_back_status(
        pending.batch_ref, pending.rail_batch_id, PayoutStatus.FAILED, bank_reference=BANK_REF
    )
    fallback = rail.generate_beftn_fallback_batch(_request())
    assert fallback.rail_type == "beftn"
    assert fallback.beftn_raw is not None


def test_read_back_keeps_the_original_retention_clock(
    clock: _Clock, rail: INT007PayoutRail
) -> None:
    pending = rail.submit_payout_batch(_request(), simulate_timeout=True)
    clock.now = T0 + 6 * 24 * 3600
    rail.read_back_status(
        pending.batch_ref, pending.rail_batch_id, PayoutStatus.CONFIRMED, bank_reference=BANK_REF
    )
    clock.now = T0 + SEVEN_DAYS_SECONDS + 1  # window measured from the submission
    assert rail.store.get("IDEMP-KEY-001") is None


def test_read_back_after_key_expiry_does_not_resurrect_it(
    clock: _Clock, rail: INT007PayoutRail
) -> None:
    pending = rail.submit_payout_batch(_request(), simulate_timeout=True)
    clock.now = T0 + SEVEN_DAYS_SECONDS + 1
    resolved = rail.read_back_status(
        pending.batch_ref, pending.rail_batch_id, PayoutStatus.CONFIRMED, bank_reference=BANK_REF
    )
    assert resolved.status is PayoutStatus.CONFIRMED
    assert rail.store.get("IDEMP-KEY-001") is None
    assert rail.store.replace_result("IDEMP-KEY-001", resolved) is False


def test_read_back_never_overwrites_a_key_reused_by_another_batch(
    clock: _Clock, rail: INT007PayoutRail
) -> None:
    old = rail.submit_payout_batch(_request(), simulate_timeout=True)
    clock.now = T0 + SEVEN_DAYS_SECONDS + 1
    new = rail.submit_payout_batch(_request(batch_ref="BATCH-2026-10-08"))
    rail.read_back_status(
        old.batch_ref, old.rail_batch_id, PayoutStatus.CONFIRMED, bank_reference=BANK_REF
    )
    assert rail.store.get("IDEMP-KEY-001")[1] is new


def test_replace_result_swaps_the_outcome_in_place(clock: _Clock, rail: INT007PayoutRail) -> None:
    store = InMemoryIdempotencyStore()
    pending = rail.submit_payout_batch(_request(), simulate_timeout=True)
    store.set("K", "hash-1", pending)
    resolved = replace(pending, status=PayoutStatus.CONFIRMED)
    assert store.replace_result("K", resolved) is True
    assert store.get("K") == ("hash-1", resolved)


BANK_REF = "BANK-RB-2026-10-02-0001"


def test_read_back_without_a_bank_answer_resolves_nothing(rail: INT007PayoutRail) -> None:
    """A read-back used to default to CONFIRMED; with no bank outcome the
    batch must stay exactly as it was."""
    pending = rail.submit_payout_batch(_request(), simulate_timeout=True)
    assert rail.read_back_status(pending.batch_ref, pending.rail_batch_id) is pending
    assert pending.status is PayoutStatus.UNKNOWN


def test_read_back_resolution_requires_the_bank_reference(rail: INT007PayoutRail) -> None:
    pending = rail.submit_payout_batch(_request(), simulate_timeout=True)
    with pytest.raises(PayoutRailError, match="bank's read-back reference"):
        rail.read_back_status(pending.batch_ref, pending.rail_batch_id, PayoutStatus.CONFIRMED)
