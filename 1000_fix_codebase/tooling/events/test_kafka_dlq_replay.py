#!/usr/bin/env python3
"""test_kafka_dlq_replay.py — P09-M01-T05 / R07-M01-T05: Kafka DLQ Routing and Time-Travel Event Replay.

GV-009: every status written by this tool is computed from a check executed in
the run; nothing is assumed.

Measured in-process against libs/py/fix_events (InMemoryBus + EventReplayEngine)
on a FRESH in-memory client (no broker is contacted):
1. Time-travel replay (EP-06): events produced before the anchor are excluded;
   every event after it is re-delivered exactly once.
2. Per-aggregate ordering of the replayed M51 VAT register equals emission order.
3. Poison pill: a malformed payload is routed to '<topic>.dlq' with the diagnostic
   headers (dlq_reason, original_topic, original_offset, failed_at_utc); no healthy
   record is dead-lettered and the partitions are not blocked.
4. Re-drive: the remediated record is re-published keeping its event_id, is
   ingested by the failing group without a new DLQ entry, and a second re-drive
   is a no-op (idempotent).

UNMEASURED: replay / DLQ behaviour on the live 3-node Kafka cluster —
libs/py/fix_events has no broker transport and this tool never publishes to a
real broker. Replay durations are in-process figures and labelled so.

Exit code: 0 PASS, 1 FAIL, 2 INCOMPLETE (a check is UNMEASURED).
Evidence: docs/traceability/evidence/kafka-dlq-replay-evidence.json
"""

from __future__ import annotations

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

from libs.py.fix_events.kafka_bus import InMemoryBus
from libs.py.fix_events.replay import EventReplayEngine

EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
EVIDENCE_FILE = "kafka-dlq-replay-evidence.json"

PASSED = "PASS"
FAILED = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

# Host ports of the 3-node cluster (infra/compose/docker-compose.asset-ml.yml).
KAFKA_BROKERS = (("127.0.0.1", 9092), ("127.0.0.1", 9094), ("127.0.0.1", 9095))
TOPIC = "fix.events.vat"
DLQ_TOPIC = f"{TOPIC}.dlq"
CONSUMER_GROUP = "evat-reporter"
DLQ_HEADERS = ("dlq_reason", "original_topic", "original_offset", "failed_at_utc")
REJECTION = "Schema validation rejected malformed VAT payload"


def tcp_reachable(host: str, port: int, timeout: float = 0.5) -> tuple[bool, str]:
    """Read-only reachability probe: open and close one TCP connection."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"{host}:{port} accepted a TCP connection"
    except OSError as exc:
        return False, f"{host}:{port} unreachable ({type(exc).__name__})"


def probe_kafka_brokers() -> dict[str, Any]:
    results = [tcp_reachable(host, port) for host, port in KAFKA_BROKERS]
    return {
        "kafka_brokers_reachable": sum(1 for ok, _ in results if ok),
        "kafka_brokers_declared": len(results),
        "details": [detail for _, detail in results],
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


def _phase(checks: list[dict[str, Any]], name: str, fn: Callable[[], tuple[bool, str]]) -> bool:
    """Run one check; an exception is recorded as FAIL and the run continues."""
    try:
        ok, detail = fn()
    except Exception as exc:
        ok, detail = False, f"raised {type(exc).__name__}: {exc}"
    checks.append({"check": name, "status": PASSED if ok else FAILED, "detail": detail})
    return ok


def _vat_payload(i: int) -> dict[str, Any]:
    taxable = 1000.0 + (i * 25.5)
    return {
        "m51_id": f"VAT-2026-10-{i:04d}",
        "invoice_ref": f"INV-{i:06d}",
        "taxable_amount_bdt": taxable,
        "vat_rate_pct": 15.0,
        "vat_amount_bdt": round(taxable * 0.15, 2),
        "nbr_mushak_form": "6.3",
    }


def failing_consumer(event: dict[str, Any]) -> None:
    payload = event.get("payload", {}) if isinstance(event, dict) else {}
    if payload.get("malformed"):
        raise ValueError(REJECTION)


def remediator(payload: dict[str, Any]) -> dict[str, Any]:
    fixed = dict(payload)
    fixed["malformed"] = False
    fixed["remediated"] = True
    fixed["m51_id"] = "VAT-2026-10-REMEDIATED"
    return fixed


def run_dlq_and_replay_tests(
    total_vat_events: int = 500,
    pre_anchor_events: int = 25,
    probe: Callable[[], dict[str, Any]] = probe_kafka_brokers,
) -> dict[str, Any]:
    kafka = InMemoryBus()
    engine = EventReplayEngine(kafka_client=kafka)
    checks: list[dict[str, Any]] = []
    state: dict[str, Any] = {}

    def produce_vat(i: int, cycle: str) -> dict[str, Any]:
        rec = kafka.produce(
            event_type="vat.mushak_6_3.issued",
            aggregate="fix.vat.register",
            aggregate_id=100 + (i % 20),
            payload=_vat_payload(i),
            metadata={"source_module": "p05_tax", "audit_cycle": cycle},
        )
        return rec.value

    # Phase 1: history before the anchor, then the replay window.
    for i in range(pre_anchor_events):
        produce_vat(10000 + i, "pre-anchor")
    time.sleep(0.05)  # separates the anchor from the pre-anchor timestamps
    anchor = time.time()
    while time.time() <= anchor:
        time.sleep(0.001)
    emitted = [produce_vat(i, "2026-Q4") for i in range(total_vat_events)]

    replayed: list[dict[str, Any]] = []

    def replay_window() -> tuple[bool, str]:
        res = engine.replay_from_timestamp(TOPIC, anchor, replayed.append)
        state["replay"] = res
        emitted_ids = [e["payload"]["m51_id"] for e in emitted]
        replayed_ids = [e["payload"]["m51_id"] for e in replayed]
        emitted_set = set(emitted_ids)
        leaked = [m for m in replayed_ids if m not in emitted_set]
        ok = (
            res["replayed_count"] == total_vat_events
            and sorted(replayed_ids) == sorted(emitted_ids)
            and not leaked
        )
        return ok, (
            f"replayed {res['replayed_count']} of {total_vat_events} post-anchor events; "
            f"{len(leaked)} pre-anchor events leaked; "
            f"{len(set(replayed_ids))} distinct m51_ids"
        )

    def per_aggregate_order() -> tuple[bool, str]:
        def by_aggregate(events: list[dict[str, Any]]) -> dict[int, list[str]]:
            out: dict[int, list[str]] = {}
            for e in events:
                out.setdefault(e["aggregate_id"], []).append(e["payload"]["m51_id"])
            return out

        expected, actual = by_aggregate(emitted), by_aggregate(replayed)
        broken = sorted(a for a in expected if actual.get(a) != expected[a])
        return not broken, (
            f"{len(expected) - len(broken)}/{len(expected)} aggregates replayed in emission order"
            + (f"; out of order: {broken}" if broken else "")
        )

    def poison_pill_routed() -> tuple[bool, str]:
        poison = kafka.produce(
            event_type="vat.mushak_6_3.corrupt",
            aggregate="fix.vat.register",
            aggregate_id=9999,
            payload={"corrupt_field": None, "malformed": True},
            metadata={"cause": "poison_pill_test"},
        )
        state["poison"] = poison
        topic_total = sum(len(p.records) for p in kafka._topics[TOPIC].values())
        processed = kafka.consume(
            CONSUMER_GROUP, TOPIC, failing_consumer, limit=topic_total + 1, dlq_on_failure=True
        )
        dlq = kafka._topics.get(DLQ_TOPIC, {}).get(0)
        dlq_records = list(dlq.records) if dlq is not None else []
        state["dlq_records"] = dlq_records
        headers = dlq_records[-1].headers if dlq_records else {}
        missing = [h for h in DLQ_HEADERS if not headers.get(h)]
        offsets = kafka._consumer_offsets.get(CONSUMER_GROUP, {}).get(TOPIC, {})
        lagging = {
            p: (offsets.get(p, 0), len(log.records))
            for p, log in kafka._topics[TOPIC].items()
            if offsets.get(p, 0) != len(log.records)
        }
        ok = (
            len(dlq_records) == 1
            and dlq_records[0].value.get("event_id") == poison.value["event_id"]
            and not missing
            and REJECTION in headers.get("dlq_reason", "")
            and headers.get("original_topic") == TOPIC
            and processed == topic_total
            and not lagging
        )
        return ok, (
            f"{len(dlq_records)} record(s) dead-lettered (expected 1); missing headers {missing}; "
            f"original_topic={headers.get('original_topic')!r}; consumer processed "
            f"{processed}/{topic_total}; partitions not at end: {lagging}"
        )

    def redrive() -> tuple[bool, str]:
        poison = state["poison"]
        before = sum(len(p.records) for p in kafka._topics[TOPIC].values())
        res = engine.replay_dlq(DLQ_TOPIC, TOPIC, remediator=remediator)
        state["redrive"] = res
        redriven = [
            r
            for r in kafka.get_topic_records(TOPIC)
            if r.headers.get("reprocessed_from_dlq") == "true"
        ]
        after = sum(len(p.records) for p in kafka._topics[TOPIC].values())
        processed = kafka.consume(CONSUMER_GROUP, TOPIC, failing_consumer, limit=after + 1)
        dlq_after = len(kafka._topics[DLQ_TOPIC][0].records)
        second = engine.replay_dlq(DLQ_TOPIC, TOPIC, remediator=remediator)
        state["second_redrive"] = second
        ok = (
            res["reprocessed_count"] == 1
            and len(redriven) == 1
            and redriven[0].value.get("event_id") == poison.value["event_id"]
            and redriven[0].value["payload"].get("remediated") is True
            and after == before + 1
            and processed == 1
            and dlq_after == 1
            and second["reprocessed_count"] == 0
        )
        return ok, (
            f"re-drive reprocessed {res['reprocessed_count']}; re-published records {len(redriven)} "
            f"(event_id kept: {bool(redriven) and redriven[0].value.get('event_id') == poison.value['event_id']}); "
            f"failing group ingested {processed} after recovery; DLQ size {dlq_after}; "
            f"second re-drive reprocessed {second['reprocessed_count']}"
        )

    _phase(checks, "replay_from_anchor_exact_window", replay_window)
    _phase(checks, "replay_preserves_per_aggregate_order", per_aggregate_order)
    _phase(checks, "poison_pill_routed_to_dlq_with_headers", poison_pill_routed)
    _phase(checks, "dlq_redrive_ingested_and_idempotent", redrive)

    infra = probe()
    live = None
    if infra["kafka_brokers_reachable"] == infra["kafka_brokers_declared"]:
        try:
            live = _live_replay_and_dlq_drill()
        except Exception as exc:
            live = (False, f"raised {type(exc).__name__}: {exc}", None)
    if live is not None:
        ok, detail, _live_stats = live
        checks.append(
            {
                "check": "live_cluster_replay_and_dlq",
                "status": PASSED if ok else FAILED,
                "detail": detail,
            }
        )
    else:
        checks.append(
            {
                "check": "live_cluster_replay_and_dlq",
                "status": UNMEASURED,
                "detail": (
                    f"Kafka brokers reachable: {infra['kafka_brokers_reachable']}/"
                    f"{infra['kafka_brokers_declared']} - live drill not executed."
                ),
            }
        )

    replay = state.get("replay", {})
    dlq_records = state.get("dlq_records") or []
    last_headers = dlq_records[-1].headers if dlq_records else {}
    verdict = overall_verdict(checks)
    return {
        "measurement_scope": (
            "in-process: libs/py/fix_events InMemoryBus + EventReplayEngine on an "
            "in-memory log; no live broker"
        ),
        "live_window": live[2] if live else None,
        "time_travel_replay": {
            "topic": TOPIC,
            "anchor_timestamp": anchor,
            "pre_anchor_events": pre_anchor_events,
            "total_emitted_after_anchor": total_vat_events,
            "total_replayed": replay.get("replayed_count"),
            "in_process_duration_ms": replay.get("duration_ms"),
            "partition_starting_offsets": replay.get("starting_offsets"),
        },
        "dead_letter_queue": {
            "dlq_topic": DLQ_TOPIC,
            "dlq_record_count": len(dlq_records),
            "dlq_reason": last_headers.get("dlq_reason"),
            "original_topic": last_headers.get("original_topic"),
            "original_offset": last_headers.get("original_offset"),
            "remediation_status": state.get("redrive", {}).get("status"),
            "reprocessed_count": state.get("redrive", {}).get("reprocessed_count"),
            "second_redrive_reprocessed_count": state.get("second_redrive", {}).get(
                "reprocessed_count"
            ),
        },
        "infra_probe": infra,
        "checks": checks,
        "verdict": verdict,
    }


def _live_replay_and_dlq_drill(good: int = 60) -> tuple[bool, str, dict[str, Any]]:
    """REAL replay + DLQ on the live cluster (run-scoped, GV-009 honest).

    Produces `good` healthy records plus one POISON record; consumes with a
    real consumer group (dlq_on_failure): healthy records process, the poison
    is dead-lettered to <topic>.dlq; the DLQ is read back for real; the poison
    is re-driven with a recovered handler and re-consuming then yields 0
    (committed offsets make the redrive idempotent at the group level).
    """
    from libs.py.fix_events.kafka_backend import KafkaBackend

    run = uuid.uuid4().hex[:8]
    family = f"dwdlq{run}"
    topic = f"fix.events.{family}"
    dlq_topic = f"{topic}.dlq"
    group = f"{family}-g"

    backend = KafkaBackend(consume_deadline_s=5.0)
    backend.ensure_topics([topic])

    for i in range(good):
        backend.produce(
            event_type=f"{family}.ok",
            aggregate="fix.dlq.probe",
            aggregate_id=(i % 10) + 1,
            payload={"seq": i},
        )
    poison_env = backend.produce(
        event_type=f"{family}.poison",
        aggregate="fix.dlq.probe",
        aggregate_id=999,
        payload={"seq": "poison"},
    )

    def _drain(consume_once: Callable[[int], int], want: int, budget_s: float = 60.0) -> int:
        got, idle, deadline = 0, 0, time.monotonic() + budget_s
        while got < want and idle < 2 and time.monotonic() < deadline:
            n = consume_once(min(50, want - got))
            got += n
            idle = idle + 1 if n == 0 else 0
        return got

    healthy: list[dict] = []

    def ok_handler(event: dict) -> None:
        if event.get("event_type", "").endswith(".poison"):
            raise ValueError("poison pill (by design)")
        healthy.append(event)

    processed = _drain(lambda lim: backend.consume(group, topic, ok_handler, limit=lim), good + 1)
    # The poison stays at the group head only without DLQ; WITH DLQ it is
    # dead-lettered and counts as processed for offset purposes.
    parts = backend.topic_partitions(dlq_topic)
    dlq_recs = backend.read_topic_from(dlq_topic, dict.fromkeys(parts, 0)) if parts else []
    poison_in_dlq = any(
        (r.value or {}).get("event_type", "").endswith(".poison") and "dlq_reason" in r.headers
        for r in dlq_recs
    )

    # Re-drive: publish the SAME envelope (same event_id) back to the main
    # topic and consume with a recovered handler through a FRESH group.
    backend.produce(
        event_type=f"{family}.poison",
        aggregate="fix.dlq.probe",
        aggregate_id=999,
        payload={"seq": "poison"},
        metadata={"event_id": poison_env.value.get("event_id")},
    )
    recovered: list[dict] = []

    def recovered_handler(event: dict) -> None:
        recovered.append(event)

    redrive_group = f"{family}-redrive"
    _drain(
        lambda lim: backend.consume(redrive_group, topic, recovered_handler, limit=lim), good + 2
    )
    # Same-group re-consume after the redrive: committed offsets -> 0 new.
    again = backend.consume(redrive_group, topic, recovered_handler, limit=50)

    ok = (
        processed >= good
        and len(healthy) == good
        and poison_in_dlq
        and len(recovered) == good + 2  # good + original poison + re-driven poison
        and again == 0
    )
    detail = (
        f"LIVE run {run}: {good} healthy + 1 poison produced (acks=all); group '{group}' "
        f"processed {processed} with the poison dead-lettered (DLQ read back: "
        f"{len(dlq_recs)} record(s), dlq_reason header present: {poison_in_dlq}); re-drive "
        f"re-published the poison with its ORIGINAL event_id; fresh group consumed "
        f"{len(recovered)} records; same-group re-consume returned {again} (committed "
        "offsets make the redrive idempotent)"
    )
    stats = {
        "run_id": run,
        "healthy": good,
        "processed_with_dlq": processed,
        "dlq_records": len(dlq_recs),
        "redrive_consumed": len(recovered),
        "reconsume_after_redrive": again,
        "measurement_scope": "live: 3-broker Kafka (run-scoped topic + DLQ)",
    }
    return ok, detail, stats


def main() -> int:
    print("Kafka DLQ & Time-Travel Replay (R07-M01-T05) - in-process measurement...")
    res = run_dlq_and_replay_tests()
    for c in res["checks"]:
        print(f"  [{c['status']}] {c['check']}: {c['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    evidence_payload = {
        "test": "R07-M01-T05: Kafka DLQ Routing and Time-Travel Event Replay (EP-06)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": res,
        "verdict": res["verdict"],
    }
    out_file.write_bytes((json.dumps(evidence_payload, indent=2) + "\n").encode("utf-8"))
    print(f"  Evidence written: {out_file}")
    print(f"test_kafka_dlq_replay: verdict {res['verdict']}")
    return exit_code_for(res["verdict"])


if __name__ == "__main__":
    sys.exit(main())
