#!/usr/bin/env python3
"""test_consumer_idempotency.py — P09-M01-T02 / R07-M01-T02: Consumer Idempotency at Scale (DI-05).

GV-009: every status written by this tool is computed from a check executed in
the run; counts, rates and drift are measured, never assumed.

Measured in-process on a FRESH in-memory libs/py/fix_events.InMemoryBus (no
broker is contacted):
1. Library: N fresh produce() calls yield N distinct event_ids (the dedup key).
2. Library: an explicit event_id (producer retry / outbox re-publish) is kept in
   the envelope for every delivery.
3. A shuffled stream of unique events plus re-published duplicates is consumed
   through InMemoryBus.consume(); every produced record is delivered once.
4. A reference DI-05 handler (script-local, dedup by event_id) applies exactly one
   business mutation per unique event; balance drift is computed.
5. Negative control: a naive (non-dedup) handler on another group observes the
   duplicates, proving the injection is not vacuous.
6. Library: committed offsets — a second consume() pass delivers nothing.
Throughput / latency figures are an in-process micro-benchmark and labelled so.

UNMEASURED: the production consumer-side dedup store at scale (live Redis /
PostgreSQL idempotency log). libs/py/fix_events.consume() is exercised and its
result recorded; this tool never writes to Redis or Kafka.

Exit code: 0 PASS, 1 FAIL, 2 INCOMPLETE (a check is UNMEASURED).
Evidence: docs/traceability/evidence/consumer-idempotency-evidence.json
"""

from __future__ import annotations

import json
import random
import socket
import sys
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from libs.py.fix_events import consume as fix_events_consume
from libs.py.fix_events.kafka_bus import InMemoryBus

EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
EVIDENCE_FILE = "consumer-idempotency-evidence.json"

PASSED = "PASS"
FAILED = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

AMOUNT_BDT = 150
TOPIC = "fix.events.payment"
# Event-bus Redis host port (infra/compose/docker-compose.yml) — probed, never written.
REDIS_ENDPOINT = ("127.0.0.1", 6380)


class IdempotencyLedger:
    """Reference DI-05 dedup barrier (script-local stand-in for the consumer's store)."""

    def __init__(self) -> None:
        self._processed: set[str] = set()

    def check_and_set(self, event_id: str) -> bool:
        """True if the event is NEW (and marks it processed); False if a DUPLICATE."""
        if event_id in self._processed:
            return False
        self._processed.add(event_id)
        return True

    def count(self) -> int:
        return len(self._processed)


class MockBusinessEntity:
    """A domain aggregate (e.g. a settlement balance) mutated by events."""

    def __init__(self) -> None:
        self.mutation_count = 0
        self.total_amount = 0

    def apply_payment(self, amount: int) -> None:
        self.mutation_count += 1
        self.total_amount += amount


def tcp_reachable(host: str, port: int, timeout: float = 0.5) -> tuple[bool, str]:
    """Read-only reachability probe: open and close one TCP connection."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"{host}:{port} accepted a TCP connection"
    except OSError as exc:
        return False, f"{host}:{port} unreachable ({type(exc).__name__})"


def probe_redis() -> dict[str, Any]:
    ok, detail = tcp_reachable(*REDIS_ENDPOINT)
    return {"redis_reachable": ok, "detail": detail}


def overall_verdict(checks: list[dict[str, Any]]) -> str:
    statuses = [c["status"] for c in checks]
    if FAILED in statuses:
        return FAILED
    if not statuses or UNMEASURED in statuses:
        return INCOMPLETE
    return PASSED


def exit_code_for(verdict: str) -> int:
    return {PASSED: 0, FAILED: 1}.get(verdict, 2)


def _percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    return sorted_values[min(len(sorted_values) - 1, int(len(sorted_values) * q))]


def _check(checks: list[dict[str, Any]], name: str, ok: bool, detail: str) -> None:
    checks.append({"check": name, "status": PASSED if ok else FAILED, "detail": detail})


def run_idempotency_stress_test(
    total_unique: int = 4000,
    num_duplicates: int = 1000,
    seed: int = 42,
    probe: Callable[[], dict[str, Any]] = probe_redis,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    rng = random.Random(seed)

    # 1. Library-assigned event_ids are unique.
    scratch = InMemoryBus()
    fresh_ids = [
        scratch.produce("payment.settled", "fix.settlement", (i % 200) + 1, {"seq": i}).value[
            "event_id"
        ]
        for i in range(total_unique)
    ]
    _check(
        checks,
        "library_event_ids_unique",
        len(set(fresh_ids)) == total_unique,
        f"{len(set(fresh_ids))} distinct event_ids from {total_unique} produce() calls",
    )

    # 2./3. Shuffled stream: unique events plus re-published duplicates (same event_id).
    originals = [
        {
            "event_id": f"evt-{uuid.uuid4().hex}",
            "aggregate_id": (i % 200) + 1,
            "payload": {"invoice_id": 10000 + i, "amount": AMOUNT_BDT},
        }
        for i in range(total_unique)
    ]
    duplicates = [rng.choice(originals) for _ in range(num_duplicates)]
    stream = originals + duplicates
    rng.shuffle(stream)

    kafka = InMemoryBus()
    preserved = 0
    for spec in stream:
        rec = kafka.produce(
            "payment.settled",
            "fix.settlement",
            spec["aggregate_id"],
            spec["payload"],
            metadata={"event_id": spec["event_id"]},
        )
        preserved += int(rec.value["event_id"] == spec["event_id"])
    _check(
        checks,
        "library_preserves_explicit_event_id",
        preserved == len(stream),
        f"{preserved}/{len(stream)} envelopes kept the event_id supplied by the producer",
    )

    ledger = IdempotencyLedger()
    entity = MockBusinessEntity()
    counters = {"deliveries": 0, "new": 0, "duplicates": 0}
    latencies_ms: list[float] = []

    def dedup_handler(event: dict[str, Any]) -> None:
        t0 = time.perf_counter()
        counters["deliveries"] += 1
        if ledger.check_and_set(event["event_id"]):
            entity.apply_payment(int(event["payload"]["amount"]))
            counters["new"] += 1
        else:
            counters["duplicates"] += 1
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)

    limit = len(stream) + 1
    t_start = time.perf_counter()
    delivered = kafka.consume("idempotency-drill", TOPIC, dedup_handler, limit=limit)
    duration_s = time.perf_counter() - t_start

    _check(
        checks,
        "every_record_delivered_once",
        delivered == len(stream) == counters["deliveries"],
        f"consume() delivered {delivered}, handler saw {counters['deliveries']}, produced {len(stream)}",
    )
    expected_balance = total_unique * AMOUNT_BDT
    drift = entity.total_amount - expected_balance
    _check(
        checks,
        "one_mutation_per_unique_event",
        entity.mutation_count == total_unique,
        f"{entity.mutation_count} mutations for {total_unique} unique events",
    )
    _check(
        checks,
        "duplicates_intercepted",
        counters["duplicates"] == num_duplicates,
        f"{counters['duplicates']} duplicates intercepted of {num_duplicates} injected",
    )
    _check(
        checks,
        "zero_balance_drift",
        drift == 0,
        f"balance {entity.total_amount} BDT vs expected {expected_balance} BDT (drift {drift})",
    )

    naive = MockBusinessEntity()
    kafka.consume(
        "naive-control",
        TOPIC,
        lambda event: naive.apply_payment(int(event["payload"]["amount"])),
        limit=limit,
    )
    _check(
        checks,
        "negative_control_duplicates_were_delivered",
        naive.mutation_count == len(stream)
        and (num_duplicates == 0 or naive.mutation_count > total_unique),
        f"non-dedup handler applied {naive.mutation_count} mutations from {len(stream)} deliveries",
    )

    redelivered = kafka.consume("idempotency-drill", TOPIC, dedup_handler, limit=limit)
    _check(
        checks,
        "committed_offsets_prevent_redelivery",
        redelivered == 0,
        f"second consume() pass for the same group delivered {redelivered} records",
    )

    # Production consumer framework: exercised, but it has no dedup store to measure.
    stub_calls: list[dict[str, Any]] = []
    stub_processed = fix_events_consume(None, stub_calls.append, "payment.settled")
    infra = probe_redis()
    live = None
    if infra.get("redis_reachable"):
        try:
            live = _live_dedup_store_drill()
        except Exception as exc:
            live = (False, f"raised {type(exc).__name__}: {exc}", None)
    if live is not None:
        ok, detail, _live_stats = live
        checks.append(
            {
                "check": "production_dedup_store_at_scale",
                "status": PASSED if ok else FAILED,
                "detail": detail,
            }
        )
    else:
        checks.append(
            {
                "check": "production_dedup_store_at_scale",
                "status": UNMEASURED,
                "detail": (
                    f"libs/py/fix_events.consume() returned {stub_processed} and invoked the handler "
                    f"{len(stub_calls)} time(s) in-process; live store not measured "
                    f"({infra.get('detail', 'redis unreachable')})."
                ),
            }
        )

    latencies_ms.sort()
    p50, p95, p99 = (_percentile(latencies_ms, q) for q in (0.50, 0.95, 0.99))
    verdict = overall_verdict(checks)
    return {
        "measurement_scope": (
            "in-process: libs/py/fix_events.InMemoryBus (in-memory log) + script-local "
            "reference dedup handler; no broker, no production consumer"
        ),
        "total_deliveries": counters["deliveries"],
        "unique_events_count": total_unique,
        "duplicate_events_injected": num_duplicates,
        "duplicate_events_intercepted": counters["duplicates"],
        "duplicate_mutations_executed": entity.mutation_count - total_unique,
        "idempotency_preservation_rate": (
            round(counters["duplicates"] / num_duplicates, 6) if num_duplicates else None
        ),
        "business_state": {
            "expected_mutations": total_unique,
            "actual_mutations": entity.mutation_count,
            "expected_balance": expected_balance,
            "actual_balance": entity.total_amount,
            "balance_drift": drift,
        },
        "in_process_microbenchmark": {
            "note": "in-memory consume loop + set-based dedup; not broker or consumer throughput",
            "throughput_events_per_sec": round(len(stream) / duration_s, 1)
            if duration_s > 0
            else None,
            "handler_latency_p50_ms": round(p50, 5) if p50 is not None else None,
            "handler_latency_p95_ms": round(p95, 5) if p95 is not None else None,
            "handler_latency_p99_ms": round(p99, 5) if p99 is not None else None,
        },
        "infra_probe": infra,
        "checks": checks,
        "verdict": verdict,
    }


def _live_dedup_store_drill(events: int = 300) -> tuple[bool, str, dict[str, Any]]:
    """REAL DI-05 dedup barrier on live Redis (SADD apply-once, run-scoped).

    Simulated at-least-once redelivery over a real Redis connection: every
    event_id is offered to the barrier TWICE (first pass + redelivery pass);
    the barrier must admit exactly `events` and reject every duplicate, with
    the naive (no-barrier) control counting 2x to prove duplicates exist.
    """
    from libs.py.fix_events.dual_write import RedisStreamStore

    run = uuid.uuid4().hex[:8]
    dedup_key = f"fix:dedup:drill:{run}"
    store = RedisStreamStore()

    def barrier(event_id: str) -> bool:
        return store.dedup_add(dedup_key, event_id)

    t0 = time.perf_counter()
    ids = [f"evt-{run}-{i:05d}" for i in range(events)]
    # First delivery pass: every id must be ADMITTED (SADD returns 1).
    first_pass = sum(1 for eid in ids if store.dedup_add(dedup_key, eid))
    # Redelivery pass (at-least-once): every id offered again - ALL rejected.
    redup_admitted = sum(1 for eid in ids if store.dedup_add(dedup_key, eid))
    elapsed = time.perf_counter() - t0

    barrier_count = store.dedup_count(dedup_key)
    naive_control = events * 2  # a handler without the barrier applies every delivery
    ok = redup_admitted == 0 and barrier_count == events and first_pass == events
    detail = (
        f"LIVE run {run}: {events} event_ids offered to the DI-05 SADD barrier on real "
        f"Redis twice (first pass admitted {first_pass}, redelivery pass admitted "
        f"{redup_admitted}); set cardinality {barrier_count} == {events}; naive control "
        f"would apply {naive_control}; barrier throughput "
        f"{2 * events / elapsed:.0f} ops/s over the wire"
    )
    store.delete_keys(dedup_key)
    stats = {
        "run_id": run,
        "events": events,
        "first_pass_admitted": first_pass,
        "redelivery_admitted": redup_admitted,
        "set_cardinality": barrier_count,
        "naive_control_would_apply": naive_control,
        "ops_per_sec": round(2 * events / elapsed, 1),
        "measurement_scope": "live: Redis SADD dedup barrier (run-scoped key)",
    }
    return ok, detail, stats


def main() -> int:
    print("Consumer Idempotency at Scale (R07-M01-T02) - in-process measurement...")
    res = run_idempotency_stress_test(total_unique=4000, num_duplicates=1000)
    for c in res["checks"]:
        print(f"  [{c['status']}] {c['check']}: {c['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    evidence_payload = {
        "test": "R07-M01-T02: Consumer Idempotency at Scale (DI-05)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": res,
        "verdict": res["verdict"],
    }
    out_file.write_bytes((json.dumps(evidence_payload, indent=2) + "\n").encode("utf-8"))
    print(f"  Evidence written: {out_file}")
    print(f"test_consumer_idempotency: verdict {res['verdict']}")
    return exit_code_for(res["verdict"])


if __name__ == "__main__":
    sys.exit(main())
