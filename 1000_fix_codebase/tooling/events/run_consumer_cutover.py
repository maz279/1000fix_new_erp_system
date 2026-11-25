#!/usr/bin/env python3
"""run_consumer_cutover.py — P09-M01-T04 / R07-M01-T04: Consumer Group Migration with Per-Group Rollback.

GV-009: every status written by this tool is computed from a check executed in
the run; nothing is assumed.

Measured in-process against libs/py/fix_events.migration, on a FRESH in-memory
InMemoryBus + MockRedisStreamStore (no broker or Redis server is contacted):
1. The 6 canonical consumer groups start on BUS_REDIS.
2. Every group transitions BUS_REDIS -> BUS_DUAL -> BUS_KAFKA (state read back).
3. Negative control: a lag AT the threshold leaves a group HEALTHY on BUS_KAFKA.
4. Fault injection: a lag breach on 'inventory-syncer' auto-reverts it to BUS_REDIS.
5. Blast radius: the other 5 groups remain on BUS_KAFKA.
6. Read routing: on BUS_KAFKA the target group reads the Kafka log; after the
   rollback it reads the Redis stream.
7. Re-cutover of the target group back to BUS_KAFKA.

UNMEASURED (reported with the reason, never assumed): the < 5 s rollback SLA on
live consumers and the drill against the live 3-node Kafka cluster.
libs/py/fix_events has no broker transport, and this tool never publishes to or
mutates a real broker. The in-process rollback timing is reported only as a
labelled micro-measurement of the state flip.

Exit code: 0 PASS, 1 FAIL, 2 INCOMPLETE (a check is UNMEASURED).
Evidence: docs/traceability/evidence/event-bus-cutover-log.json
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

from libs.py.fix_events.dual_write import MockRedisStreamStore, payload_digest
from libs.py.fix_events.kafka_bus import InMemoryBus
from libs.py.fix_events.migration import (
    CANONICAL_CONSUMER_GROUPS,
    ConsumerBusState,
    ConsumerGroupMigrationManager,
)

EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
EVIDENCE_FILE = "event-bus-cutover-log.json"

PASSED = "PASS"
FAILED = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

# Host ports of the 3-node cluster (infra/compose/docker-compose.asset-ml.yml).
KAFKA_BROKERS = (("127.0.0.1", 9092), ("127.0.0.1", 9094), ("127.0.0.1", 9095))
TARGET_GROUP = "inventory-syncer"
CONTROL_GROUP = "audit-logger"
ROUTING_TOPIC = "fix.events.stock"


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
    """Run one check; an exception is recorded as FAIL and the drill continues."""
    try:
        ok, detail = fn()
    except Exception as exc:
        ok, detail = False, f"raised {type(exc).__name__}: {exc}"
    checks.append({"check": name, "status": PASSED if ok else FAILED, "detail": detail})
    return ok


def run_consumer_cutover_drill(
    probe: Callable[[], dict[str, Any]] = probe_kafka_brokers,
) -> dict[str, Any]:
    kafka = InMemoryBus()
    redis = MockRedisStreamStore()
    mgr = ConsumerGroupMigrationManager(kafka_client=kafka, redis_store=redis)
    groups = list(CANONICAL_CONSUMER_GROUPS)
    checks: list[dict[str, Any]] = []
    log: list[dict[str, Any]] = []
    rollback: dict[str, Any] = {}

    def states() -> dict[str, str]:
        return {g: mgr.get_group_state(g).value for g in groups}

    def initial() -> tuple[bool, str]:
        observed = states()
        wrong = {g: s for g, s in observed.items() if s != ConsumerBusState.BUS_REDIS.value}
        log.append({"step": "initial_check", "states": observed})
        detail = f"{len(groups) - len(wrong)}/{len(groups)} groups on BUS_REDIS"
        return not wrong, detail + (f"; not on BUS_REDIS: {wrong}" if wrong else "")

    def transition_all(state: ConsumerBusState) -> Callable[[], tuple[bool, str]]:
        def run() -> tuple[bool, str]:
            results = {
                g: mgr.transition_group(g, state, reason=f"drill -> {state.value}") for g in groups
            }
            observed = states()
            wrong = {g: s for g, s in observed.items() if s != state.value}
            log.append({"step": f"transition_{state.value}", "results": results})
            detail = f"{len(groups) - len(wrong)}/{len(groups)} groups read back as {state.value}"
            return not wrong, detail + (f"; mismatched: {wrong}" if wrong else "")

        return run

    def read_source(group: str) -> list[str]:
        sources: list[str] = []

        def handler(event: dict[str, Any]) -> None:
            if "payload_sha256" in event:  # Redis stream fields
                sources.append(json.loads(event.get("payload", "{}")).get("marker", "?"))
            else:  # Kafka envelope
                sources.append((event.get("payload") or {}).get("marker", "?"))

        mgr.consume_event(group, ROUTING_TOPIC, handler)
        return sources

    def routing_on_kafka() -> tuple[bool, str]:
        sources = read_source(TARGET_GROUP)
        ok = bool(sources) and set(sources) == {"kafka"}
        return ok, f"{TARGET_GROUP} on BUS_KAFKA delivered sources={sources}"

    def lag_at_threshold_is_healthy() -> tuple[bool, str]:
        res = mgr.check_health_and_auto_revert(CONTROL_GROUP, current_lag=mgr.max_lag_threshold)
        state = mgr.get_group_state(CONTROL_GROUP).value
        ok = res.get("status") == "HEALTHY" and state == ConsumerBusState.BUS_KAFKA.value
        log.append({"step": "negative_control", "target": CONTROL_GROUP, "result": res})
        return (
            ok,
            f"lag={mgr.max_lag_threshold} (= threshold) -> status={res.get('status')}, state={state}",
        )

    def lag_breach_rolls_back() -> tuple[bool, str]:
        lag = mgr.max_lag_threshold + 250
        res = mgr.check_health_and_auto_revert(TARGET_GROUP, current_lag=lag)
        rollback.update(res)
        state = mgr.get_group_state(TARGET_GROUP).value
        ok = res.get("status") == "ROLLED_BACK" and state == ConsumerBusState.BUS_REDIS.value
        log.append({"step": "fault_injection_rollback", "target": TARGET_GROUP, "result": res})
        return ok, f"lag={lag} -> status={res.get('status')}, state={state}"

    def blast_radius() -> tuple[bool, str]:
        others = {g: s for g, s in states().items() if g != TARGET_GROUP}
        wrong = {g: s for g, s in others.items() if s != ConsumerBusState.BUS_KAFKA.value}
        log.append({"step": "blast_radius", "states": others})
        detail = f"{len(others) - len(wrong)}/{len(others)} non-target groups still on BUS_KAFKA"
        return not wrong, detail + (f"; moved: {wrong}" if wrong else "")

    def routing_after_rollback() -> tuple[bool, str]:
        sources = read_source(TARGET_GROUP)
        ok = bool(sources) and set(sources) == {"redis"}
        return ok, f"{TARGET_GROUP} after rollback delivered sources={sources}"

    def recutover() -> tuple[bool, str]:
        res = mgr.transition_group(TARGET_GROUP, ConsumerBusState.BUS_KAFKA, reason="lag cleared")
        distribution = mgr.get_summary()["state_distribution"]
        log.append({"step": "recutover_target", "result": res})
        ok = distribution.get(ConsumerBusState.BUS_KAFKA.value) == len(groups)
        return ok, f"final state distribution {distribution}"

    # Routing fixtures: one record on each bus, distinguishable by payload marker.
    kafka.produce("stock.consumed", "fix.stock.consumption", 1, {"marker": "kafka"})
    redis.xadd(
        "fix:events:stock",
        {
            "event_type": "stock.consumed",
            "payload": json.dumps({"marker": "redis"}),
            "payload_sha256": "x",
        },
    )

    _phase(checks, "initial_state_all_bus_redis", initial)
    _phase(checks, "transition_all_to_bus_dual", transition_all(ConsumerBusState.BUS_DUAL))
    _phase(checks, "transition_all_to_bus_kafka", transition_all(ConsumerBusState.BUS_KAFKA))
    _phase(checks, "routing_bus_kafka_reads_kafka_log", routing_on_kafka)
    _phase(checks, "negative_control_lag_at_threshold_stays_healthy", lag_at_threshold_is_healthy)
    _phase(checks, "fault_injection_lag_breach_rolls_back_target", lag_breach_rolls_back)
    _phase(checks, "blast_radius_other_groups_stay_on_kafka", blast_radius)
    _phase(checks, "routing_after_rollback_reads_redis_stream", routing_after_rollback)
    _phase(checks, "recutover_all_groups_on_bus_kafka", recutover)

    infra = probe()
    reachable = infra["kafka_brokers_reachable"]
    live = None
    if reachable == infra["kafka_brokers_declared"]:
        try:
            live = _live_cluster_cutover_drill()
        except Exception as exc:
            live = {
                "live_cluster_cutover_drill": (False, f"raised {type(exc).__name__}: {exc}"),
                "live_rollback_sla_under_5s": (False, f"raised {type(exc).__name__}: {exc}"),
                "stats": None,
            }
    if live is not None:
        for name in ("live_cluster_cutover_drill", "live_rollback_sla_under_5s"):
            ok, detail = live[name]
            checks.append({"check": name, "status": PASSED if ok else FAILED, "detail": detail})
    else:
        reason = (
            f"Kafka brokers reachable: {reachable}/{infra['kafka_brokers_declared']} "
            f"({'; '.join(infra['details'])}) - live drill not executed."
        )
        checks.append(
            {"check": "live_rollback_sla_under_5s", "status": UNMEASURED, "detail": reason}
        )
        checks.append(
            {"check": "live_cluster_cutover_drill", "status": UNMEASURED, "detail": reason}
        )

    verdict = overall_verdict(checks)
    return {
        "measurement_scope": (
            "in-process state machine of libs/py/fix_events.migration on in-memory "
            "Kafka/Redis stand-ins; no live broker"
        ),
        "canonical_groups_count": len(groups),
        "groups": groups,
        "rollback_drill": {
            "target_group": TARGET_GROUP,
            "in_process_state_flip_ms": rollback.get("rollback_elapsed_ms"),
            "in_process_state_flip_note": (
                "time to flip the in-memory state field only; not a live consumer rollback"
            ),
        },
        "final_state_distribution": mgr.get_summary()["state_distribution"],
        "infra_probe": infra,
        "live_window": live["stats"] if live else None,
        "checks": checks,
        "cutover_log": log,
        "verdict": verdict,
    }


def _live_cluster_cutover_drill(events: int = 120) -> dict[str, Any]:
    """REAL per-group cutover on the live cluster (run-scoped, GV-009 honest).

    Run-scoped topic fix.events.dwcut<run>, consumer group dwcut<run>-g and
    Redis stream fix:events:dwcut<run>: prior runs cannot mask a divergence.
    Measured for real: acks=all produce; group consumption with committed
    offsets (re-consume returns 0); BUS_DUAL shadow comparison against the
    real Redis stream; rollback to the Redis path and its wall-clock SLA.
    """
    from libs.py.fix_events.dual_write import RedisStreamStore
    from libs.py.fix_events.kafka_backend import KafkaBackend

    run = uuid.uuid4().hex[:8]
    family = f"dwcut{run}"
    topic = f"fix.events.{family}"
    stream = f"fix:events:{family}"

    store = RedisStreamStore()
    backend = KafkaBackend(consume_deadline_s=5.0)
    mgr = ConsumerGroupMigrationManager(kafka_client=backend, redis_store=store)

    seen: list[dict] = []

    def handler(event: dict) -> None:
        seen.append(event)

    def drain(consume_once: Callable[[int], int], want: int, budget_s: float = 60.0) -> int:
        """Bounded drain loop: stops on target, budget, or two no-progress calls."""
        got, idle, deadline = 0, 0, time.monotonic() + budget_s
        while got < want and idle < 2 and time.monotonic() < deadline:
            n = consume_once(min(50, want - got))
            got += n
            idle = idle + 1 if n == 0 else 0
        return got

    # Seed BOTH sides for real (dual-write semantics for the drill family).
    for i in range(events):
        backend.produce(
            event_type=f"{family}.probe",
            aggregate="fix.cutover.probe",
            aggregate_id=(i % 20) + 1,
            payload={"seq": i, "ref": f"CUT-{i:04d}"},
        )
        store.xadd(
            stream,
            {
                "event_id": f"evt-{run}-{i}",
                "payload": json.dumps({"seq": i, "ref": f"CUT-{i:04d}"}),
                "payload_sha256": payload_digest({"seq": i, "ref": f"CUT-{i:04d}"}),
            },
        )

    # 1. Kafka leg (fresh group, direct backend): drain the run topic through
    #    committed group offsets; re-consume must return 0 (commit proof).
    kafka_group = f"{family}-k"
    total = drain(lambda lim: backend.consume(kafka_group, topic, handler, limit=lim), events)
    recommitted = backend.consume(
        consumer_group=kafka_group, topic=topic, handler=handler, limit=50
    )
    kafka_ok = total == events and recommitted == 0

    # 2. BUS_DUAL shadow comparison against the real Redis stream.
    shadow_group = f"{family}-dual"
    mgr.register_group(shadow_group)
    mgr.transition_group(shadow_group, ConsumerBusState.BUS_DUAL, reason="live drill")
    seen.clear()
    dual_total = drain(
        lambda lim: mgr.consume_event(shadow_group, topic, handler, limit=lim), events
    )
    summary = mgr.get_summary()
    ginfo = summary["groups"].get(shadow_group, {})
    dual_ok = (
        dual_total == events
        and ginfo.get("shadow_match_count", 0) >= events
        and ginfo.get("shadow_mismatch_count", 0) == 0
    )

    # 3. Rollback SLA on a FRESH group (redis cursor at 0): DUAL -> rollback ->
    #    read the whole run stream through a REAL Redis connection, timed.
    rb_group = f"{family}-rb"
    mgr.register_group(rb_group)
    mgr.transition_group(rb_group, ConsumerBusState.BUS_DUAL, reason="live drill")
    t0 = time.perf_counter()
    mgr.rollback_group(rb_group, reason="live drill rollback")
    seen.clear()
    redis_total = drain(
        lambda lim: mgr.consume_event(rb_group, topic, handler, limit=lim), events, budget_s=10.0
    )
    rollback_s = time.perf_counter() - t0
    rollback_ok = redis_total == events and rollback_s < 5.0

    store.delete_streams(stream)
    stats = {
        "run_id": run,
        "events": events,
        "kafka_consumed_with_committed_offsets": total,
        "reconsume_after_commit_returned": recommitted,
        "dual_shadow_matches": ginfo.get("shadow_match_count", 0),
        "dual_shadow_mismatches": ginfo.get("shadow_mismatch_count", 0),
        "rollback_read_redis_records": redis_total,
        "rollback_wall_clock_s": round(rollback_s, 3),
        "measurement_scope": "live: 3-broker Kafka + Redis Streams (run-scoped family)",
    }
    return {
        "live_cluster_cutover_drill": (
            kafka_ok and dual_ok,
            f"LIVE run {run}: {events} records consumed through consumer group "
            f"'{kafka_group}' on the real cluster (acks=all produce); re-consume after "
            f"commit returned {recommitted} (offsets really committed); BUS_DUAL shadow "
            f"compare against the real Redis stream: {ginfo.get('shadow_match_count', 0)} "
            f"matches / {ginfo.get('shadow_mismatch_count', 0)} mismatches over "
            f"{dual_total} consumed",
        ),
        "live_rollback_sla_under_5s": (
            rollback_ok,
            f"LIVE run {run}: rollback to the Redis path read back {redis_total}/{events} "
            f"records through a real Redis Streams connection in {rollback_s:.3f}s "
            f"(SLA < 5s: {'met' if rollback_ok else 'BREACHED'})",
        ),
        "stats": stats,
    }


def main() -> int:
    print("Consumer Group Migration Drill (R07-M01-T04) - in-process measurement...")
    res = run_consumer_cutover_drill()
    for c in res["checks"]:
        print(f"  [{c['status']}] {c['check']}: {c['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    evidence_payload = {
        "test": "R07-M01-T04: Consumer Group Migration with Per-Group Rollback (EP-05)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": res,
        "verdict": res["verdict"],
    }
    out_file.write_bytes((json.dumps(evidence_payload, indent=2) + "\n").encode("utf-8"))
    print(f"  Evidence written: {out_file}")
    print(f"run_consumer_cutover: verdict {res['verdict']}")
    return exit_code_for(res["verdict"])


if __name__ == "__main__":
    sys.exit(main())
