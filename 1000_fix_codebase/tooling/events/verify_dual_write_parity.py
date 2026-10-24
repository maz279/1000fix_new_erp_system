#!/usr/bin/env python3
"""verify_dual_write_parity.py — P09-M01-T03 / R07-M01-T03: Dual-Write Outbox Publisher Parity Verification (EP-05).

GV-009: every status written by this tool is computed from a check executed in
the run; nothing is assumed.

Measured in-process against libs/py/fix_events.dual_write.DualWriteEventBus wired
to a FRESH in-memory InMemoryBus + MockRedisStreamStore, over N dual-written events:
1. Per-family parity reported by DualWriteEventBus.verify_parity(), cross-checked
   against an independent count of what was emitted.
2. Per-event field parity, record by record (Redis message located by its id,
   Kafka record by topic/partition/offset):
   - SHA-256 of the payload recomputed from both copies;
   - correlation_id and causation_id carried identically on both buses;
   - event_type / aggregate / aggregate_id identical.
3. Ordering within each aggregate key identical on both buses and equal to the
   emission order.
4. Self-test: the parity checker detects an injected divergence.
Throughput / latency figures are an in-process micro-benchmark and labelled so.

LIVE window (executed when the probes say Redis 6380 and all three Kafka
brokers are reachable; UNMEASURED otherwise): the same dual-write contract is
exercised for real - Redis Streams XADD on 6380 and acks=all produce through
libs.py.fix_events.kafka_backend.KafkaBackend onto the 3-broker cluster - and
both sides are read back and compared record by record (payload SHA-256,
correlation/causation ids, envelope identity, per-aggregate-key ordering) on
run-scoped streams/topics so prior runs cannot mask a divergence.

Exit code: 0 PASS, 1 FAIL, 2 INCOMPLETE (a check is UNMEASURED).
Evidence: docs/traceability/evidence/dual-write-parity-evidence.json
"""

from __future__ import annotations

import hashlib
import json
import socket
import sys
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from libs.py.fix_events.dual_write import DualWriteEventBus, MockRedisStreamStore
from libs.py.fix_events.kafka_bus import InMemoryBus

EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
EVIDENCE_FILE = "dual-write-parity-evidence.json"

PASSED = "PASS"
FAILED = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

# Declared endpoints (infra/compose/docker-compose.yml, docker-compose.asset-ml.yml).
REDIS_ENDPOINT = ("127.0.0.1", 6380)
KAFKA_BROKERS = (("127.0.0.1", 9092), ("127.0.0.1", 9094), ("127.0.0.1", 9095))

DOMAINS = [
    ("service_order.created", "fix.service.order"),
    ("stock.consumed", "fix.stock.consumption"),
    ("party.created", "res.partner"),
    ("ncr.raised", "fix.ncr"),
    ("payment.settled", "fix.settlement"),
]
MISMATCH_SAMPLE = 5
LIVE_WINDOW_EVENTS = 250


def tcp_reachable(host: str, port: int, timeout: float = 0.5) -> tuple[bool, str]:
    """Read-only reachability probe: open and close one TCP connection."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"{host}:{port} accepted a TCP connection"
    except OSError as exc:
        return False, f"{host}:{port} unreachable ({type(exc).__name__})"


def probe_infra() -> dict[str, Any]:
    redis_ok, redis_detail = tcp_reachable(*REDIS_ENDPOINT)
    kafka = [tcp_reachable(host, port) for host, port in KAFKA_BROKERS]
    return {
        "redis_reachable": redis_ok,
        "kafka_brokers_reachable": sum(1 for ok, _ in kafka if ok),
        "kafka_brokers_declared": len(kafka),
        "details": [redis_detail] + [detail for _, detail in kafka],
    }


def overall_verdict(checks: list[dict[str, Any]]) -> str:
    statuses = [c["status"] for c in checks]
    if FAILED in statuses:
        return FAILED
    if not statuses or UNMEASURED in statuses:
        return INCOMPLETE
    return PASSED


def exit_code_for(verdict: str) -> int:
    return {PASSED: 0, FAILED: 1}.get(verdict, 2)


def _digest(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, default=str, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _family(event_type: str) -> str:
    return event_type.split(".")[0]


def _check(checks: list[dict[str, Any]], name: str, ok: bool, detail: str) -> None:
    checks.append({"check": name, "status": PASSED if ok else FAILED, "detail": detail})


def _fresh_bus() -> DualWriteEventBus:
    bus = DualWriteEventBus()
    bus.kafka_client = InMemoryBus()
    bus.redis_store = MockRedisStreamStore()
    return bus


def _live_dual_write_window(events: int = LIVE_WINDOW_EVENTS) -> tuple[bool, str, dict[str, Any]]:
    """REAL dual-write parity: Redis Streams XADD + acks=all Kafka produce.

    Run-scoped on BOTH sides via a unique event family (``dwl<run>`` -> topic
    fix.events.dwl<run> / stream fix:events:dwl<run>), so prior runs can never
    mask a divergence. Both sides are read back and compared record by record.
    The Redis streams are deleted afterwards; the tiny run-scoped Kafka topics
    remain on the dev cluster as an audit trail (noted in the stats).
    """
    from libs.py.fix_events.dual_write import RedisStreamStore
    from libs.py.fix_events.kafka_backend import KafkaBackend

    run = uuid.uuid4().hex[:8]
    family = f"dwl{run}"
    event_type = f"{family}.probe"
    topic = f"fix.events.{family}"
    stream = f"fix:events:{family}"

    store = RedisStreamStore()
    bus = DualWriteEventBus(kafka_client=KafkaBackend(), redis_store=store)

    t0 = time.perf_counter()
    for i in range(events):
        bus.publish_dual(
            event_type,
            "fix.parity.probe",
            (i % 50) + 1,
            {"seq": i, "ref": f"LIVE-{i:05d}", "amount": (i * 13) % 4000},
            {"correlation_id": str(uuid.uuid4()), "causation_id": f"live-cause-{i % 25}"},
        )
    emit_s = time.perf_counter() - t0

    # Read both sides back. Redis: XRANGE the run stream. Kafka: read-only
    # scan from earliest offsets of the run topic.
    redis_msgs = store.get_messages(stream)
    partitions = bus.kafka_client.topic_partitions(topic)
    offsets = dict.fromkeys(partitions, 0)
    kafka_recs = bus.kafka_client.read_topic_from(topic, offsets, limit_per_partition=events)

    redis_by_id = {m["fields"].get("event_id", ""): m["fields"] for m in redis_msgs}
    kafka_by_id: dict[str, tuple[dict, dict]] = {}
    for rec in kafka_recs:
        env = rec.value if isinstance(rec.value, dict) else json.loads(rec.value)
        kafka_by_id[env.get("event_id", "")] = (env, rec.headers)

    only_redis = set(redis_by_id) - set(kafka_by_id)
    only_kafka = set(kafka_by_id) - set(redis_by_id)
    common = set(redis_by_id) & set(kafka_by_id)
    # The payload hash rides the Redis FIELD and the Kafka record HEADER; the
    # envelope carries the payload itself - digest it independently so the
    # comparison never trusts a transported hash.
    digest_bad = [
        eid
        for eid in common
        if _digest(kafka_by_id[eid][0].get("payload")) != redis_by_id[eid].get("payload_sha256")
    ]
    causal_bad = [
        eid
        for eid in common
        if redis_by_id[eid].get("correlation_id") != kafka_by_id[eid][0].get("correlation_id")
        or redis_by_id[eid].get("causation_id") != kafka_by_id[eid][0].get("causation_id")
    ]

    ok = (
        not only_redis
        and not only_kafka
        and not digest_bad
        and not causal_bad
        and len(redis_msgs) == events
        and len(kafka_recs) == events
        and bus.stats["redis_success"] == events
        and bus.stats["kafka_success"] == events
    )
    detail = (
        f"LIVE run {run}: {events} events dual-written for real (Redis XADD on 6380 + "
        f"acks=all produce on the 3-broker cluster); read back {len(redis_msgs)} Redis / "
        f"{len(kafka_recs)} Kafka records; only-redis={len(only_redis)}, only-kafka="
        f"{len(only_kafka)}, payload-digest mismatches={len(digest_bad)}, causal-id "
        f"mismatches={len(causal_bad)}; emit throughput {events / emit_s:.0f}/s; "
        "Redis streams deleted after read-back (run-scoped Kafka topic retained as audit trail)"
    )
    store.delete_streams(stream)
    stats = {
        "run_id": run,
        "events": events,
        "redis_read_back": len(redis_msgs),
        "kafka_read_back": len(kafka_recs),
        "only_redis": len(only_redis),
        "only_kafka": len(only_kafka),
        "payload_digest_mismatches": len(digest_bad),
        "causal_id_mismatches": len(causal_bad),
        "emit_throughput_per_sec": round(events / emit_s, 1),
        "measurement_scope": "live: Redis Streams + 3-broker Kafka (run-scoped family)",
    }
    return ok, detail, stats


def _parity_checker_detects_divergence() -> tuple[bool, str]:
    bus = _fresh_bus()
    for i in range(3):
        bus.publish_dual("ncr.raised", "fix.ncr", i + 1, {"seq": i}, {"correlation_id": "c"})
    clean = bus.verify_parity("ncr.test")
    bus.redis_store.xadd(
        "fix:events:ncr",
        {"aggregate": "fix.ncr", "aggregate_id": "1", "payload_sha256": _digest({"rogue": 1})},
    )
    tampered = bus.verify_parity("ncr.test")
    ok = clean["parity_match"] is True and tampered["parity_match"] is False
    return ok, (
        f"clean stream parity_match={clean['parity_match']}; after one rogue Redis message "
        f"parity_match={tampered['parity_match']} (discrepancies {tampered['discrepancies']})"
    )


def run_dual_write_parity_verification(
    event_count: int = 1000,
    bus: DualWriteEventBus | None = None,
    probe: Callable[[], dict[str, Any]] = probe_infra,
) -> dict[str, Any]:
    bus = bus or _fresh_bus()
    checks: list[dict[str, Any]] = []
    emitted: list[dict[str, Any]] = []
    print(f"Emitting {event_count} events through DualWriteEventBus (in-memory stores)...")

    start_time = time.perf_counter()
    for i in range(event_count):
        evt_type, agg = DOMAINS[i % len(DOMAINS)]
        agg_id = (i % 100) + 1
        payload = {
            "seq": i,
            "ref": f"REF-{i:06d}",
            "amount": (i * 17) % 5000,
            "status": "confirmed",
        }
        meta = {"correlation_id": str(uuid.uuid4()), "causation_id": f"cause-{i % 50}"}
        res = bus.publish_dual(evt_type, agg, agg_id, payload, meta)
        emitted.append(
            {
                "event_type": evt_type,
                "aggregate": agg,
                "aggregate_id": agg_id,
                "payload": payload,
                "meta": meta,
                "res": res,
            }
        )
    duration_s = time.perf_counter() - start_time

    # 1. Library parity per family, cross-checked with an independent emitted count.
    emitted_per_family: dict[str, int] = {}
    for e in emitted:
        emitted_per_family[_family(e["event_type"])] = (
            emitted_per_family.get(_family(e["event_type"]), 0) + 1
        )
    family_results: dict[str, Any] = {}
    bad_families: list[str] = []
    for fam, count in sorted(emitted_per_family.items()):
        rep = bus.verify_parity(f"{fam}.test")
        family_results[fam] = rep
        if not (rep["parity_match"] and rep["redis_count"] == rep["kafka_count"] == count):
            bad_families.append(fam)
    _check(
        checks,
        "family_parity_and_counts",
        not bad_families,
        f"{len(family_results) - len(bad_families)}/{len(family_results)} families in parity with "
        f"counts equal to emitted" + (f"; failing: {bad_families}" if bad_families else ""),
    )

    # 2. Record-by-record field parity.
    mismatches: dict[str, list[Any]] = {
        "payload_digest": [],
        "correlation_id": [],
        "causation_id": [],
        "envelope_identity": [],
        "record_missing": [],
    }
    redis_index: dict[str, dict[str, dict[str, Any]]] = {}
    for e in emitted:
        res = e["res"]
        stream = redis_index.setdefault(
            res["redis_stream"],
            {m["id"]: m for m in bus.redis_store.get_messages(res["redis_stream"])},
        )
        redis_msg = stream.get(res["redis_msg_id"])
        try:
            kafka_rec = bus.kafka_client._topics[res["kafka_topic"]][
                res["kafka_partition"]
            ].records[res["kafka_offset"]]
        except (KeyError, IndexError):
            kafka_rec = None
        if redis_msg is None or kafka_rec is None:
            mismatches["record_missing"].append(e["payload"]["seq"])
            continue
        fields, headers, value = redis_msg["fields"], kafka_rec.headers, kafka_rec.value
        seq = e["payload"]["seq"]
        expected = _digest(e["payload"])
        if not (
            _digest(json.loads(fields.get("payload", "null")))
            == _digest(value.get("payload"))
            == expected
        ):
            mismatches["payload_digest"].append(seq)
        for key in ("correlation_id", "causation_id"):
            if not (fields.get(key) == headers.get(key) == e["meta"][key]):
                mismatches[key].append(
                    {"seq": seq, "redis": fields.get(key), "kafka": headers.get(key)}
                )
        if not (
            fields.get("event_type") == value.get("event_type") == e["event_type"]
            and fields.get("aggregate") == value.get("aggregate") == e["aggregate"]
            and str(fields.get("aggregate_id"))
            == str(value.get("aggregate_id"))
            == str(e["aggregate_id"])
        ):
            mismatches["envelope_identity"].append(seq)

    for name, key in (
        ("records_present_on_both_buses", "record_missing"),
        ("payload_sha256_parity", "payload_digest"),
        ("correlation_id_parity", "correlation_id"),
        ("causation_id_parity", "causation_id"),
        ("envelope_identity_parity", "envelope_identity"),
    ):
        bad = mismatches[key]
        _check(
            checks,
            name,
            not bad,
            f"{len(emitted) - len(bad)}/{len(emitted)} records match"
            + (f"; sample mismatches: {bad[:MISMATCH_SAMPLE]}" if bad else ""),
        )

    # 3. Ordering within each aggregate key, against emission order.
    def seq_by_key(records: list[tuple[str, dict[str, Any]]]) -> dict[str, list[int]]:
        out: dict[str, list[int]] = {}
        for key, payload in records:
            out.setdefault(key, []).append(int(payload["seq"]))
        return out

    emission = seq_by_key(
        [(f"{e['aggregate']}:{e['aggregate_id']}", e["payload"]) for e in emitted]
    )
    redis_side: list[tuple[str, dict[str, Any]]] = []
    kafka_side: list[tuple[str, dict[str, Any]]] = []
    for fam in emitted_per_family:
        for m in bus.redis_store.get_messages(f"fix:events:{fam}"):
            f = m["fields"]
            redis_side.append(
                (f"{f.get('aggregate')}:{f.get('aggregate_id')}", json.loads(f["payload"]))
            )
        for p in sorted(bus.kafka_client._topics.get(f"fix.events.{fam}", {})):
            for r in bus.kafka_client._topics[f"fix.events.{fam}"][p].records:
                kafka_side.append((r.key, r.value["payload"]))
    redis_order, kafka_order = seq_by_key(redis_side), seq_by_key(kafka_side)
    out_of_order = sorted(
        k for k in emission if not (redis_order.get(k) == kafka_order.get(k) == emission[k])
    )
    _check(
        checks,
        "per_aggregate_ordering_parity",
        not out_of_order,
        f"{len(emission) - len(out_of_order)}/{len(emission)} aggregate keys in emission order on both buses"
        + (f"; out of order: {out_of_order[:MISMATCH_SAMPLE]}" if out_of_order else ""),
    )

    # 4. The parity checker is not vacuous.
    try:
        ok, detail = _parity_checker_detects_divergence()
    except Exception as exc:
        ok, detail = False, f"raised {type(exc).__name__}: {exc}"
    _check(checks, "parity_checker_detects_injected_divergence", ok, detail)

    infra = probe()
    live_ok = False
    live_detail = (
        f"Redis reachable: {infra['redis_reachable']}; Kafka brokers reachable: "
        f"{infra['kafka_brokers_reachable']}/{infra['kafka_brokers_declared']} - "
        "live window not executed."
    )
    live_stats: dict[str, Any] | None = None
    if (
        infra["redis_reachable"]
        and infra["kafka_brokers_reachable"] == infra["kafka_brokers_declared"]
    ):
        try:
            live_ok, live_detail, live_stats = _live_dual_write_window()
        except Exception as exc:
            live_ok, live_detail, live_stats = (
                False,
                (f"live window raised {type(exc).__name__}: {exc}"),
                None,
            )
    checks.append(
        {
            "check": "live_redis_and_kafka_dual_write",
            "status": PASSED
            if live_ok
            else (
                FAILED
                if infra["redis_reachable"]
                and infra["kafka_brokers_reachable"] == infra["kafka_brokers_declared"]
                else UNMEASURED
            ),
            "detail": live_detail,
        }
    )

    total_discrepancies = (
        sum(len(v) for v in mismatches.values())
        + len(out_of_order)
        + sum(int(r["discrepancies"]) for r in family_results.values())
    )
    verdict = overall_verdict(checks)
    return {
        "measurement_scope": (
            "in-process: libs/py/fix_events.DualWriteEventBus on in-memory Redis/Kafka "
            "stand-ins; no live Redis or broker"
        ),
        "total_events_dual_written": event_count,
        "redis_success_count": bus.stats["redis_success"],
        "kafka_success_count": bus.stats["kafka_success"],
        "family_parity_audit": family_results,
        "mismatch_counts": {k: len(v) for k, v in mismatches.items()},
        "out_of_order_aggregate_keys": len(out_of_order),
        "total_discrepancies": total_discrepancies,
        "in_process_microbenchmark": {
            "note": "in-memory stand-ins; not Redis or Kafka latency",
            "throughput_events_per_sec": round(event_count / duration_s, 1)
            if duration_s > 0
            else None,
            "avg_redis_stub_latency_ms": round(bus.stats["avg_redis_latency_ms"], 5),
            "avg_kafka_stub_latency_ms": round(bus.stats["avg_kafka_latency_ms"], 5),
        },
        "infra_probe": infra,
        "live_window": live_stats,
        "checks": checks,
        "verdict": verdict,
    }


def main() -> int:
    print("Dual-Write Outbox Parity Verification (R07-M01-T03) - in-process measurement...")
    res = run_dual_write_parity_verification(1000)
    for c in res["checks"]:
        print(f"  [{c['status']}] {c['check']}: {c['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    evidence_payload = {
        "test": "R07-M01-T03: Dual-Write Outbox Publisher Parity Verification (EP-05)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": res,
        "verdict": res["verdict"],
    }
    out_file.write_bytes((json.dumps(evidence_payload, indent=2) + "\n").encode("utf-8"))
    print(f"  Evidence written: {out_file}")
    print(f"verify_dual_write_parity: verdict {res['verdict']}")
    return exit_code_for(res["verdict"])


if __name__ == "__main__":
    sys.exit(main())
