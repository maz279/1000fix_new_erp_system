#!/usr/bin/env python3
"""verify_kafka_cluster.py — P09-M01-T01 / R07-M01-T01: Kafka 3-Node HA Cluster & Single-Broker Loss Verification.

GV-009: every status written by this tool is computed from a check executed in
the run; nothing is assumed.

Static checks (parsed YAML of infra/compose/docker-compose.asset-ml.yml):
1. Exactly 3 KRaft nodes (kafka-N services) with distinct KAFKA_NODE_IDs.
2. Every node's image is pinned to the apache/kafka digest recorded in
   tooling/versions.lock (DE-06). Registry existence of the digest is not queried.
3. KAFKA_CONTROLLER_QUORUM_VOTERS on every node lists exactly the declared nodes.
4. Replication: offsets / transaction-state / default replication factor = 3 and
   KAFKA_MIN_INSYNC_REPLICAS = 2 on every node.
5. Derived from the parsed values: replication factor <= node count and
   replication factor - min ISR >= 1, i.e. acks=all writes survive one broker loss.
6. Each node publishes a distinct 127.0.0.1 host port.

Live checks:
- TCP reachability of every published broker port (read-only probe); UNMEASURED
  when the brokers are not reachable (the asset-ml profile is opt-in).
- The single-broker loss drill EXECUTES when a drill executor is wired
  (main() wires the real one): it docker-stops the broker publishing host port
  9094, produces/consumes through the surviving two via the real
  libs/py/fix_events KafkaBackend, restarts the broker and produces/consumes
  again. UNMEASURED when the brokers/docker are not available from this run.

Exit code: 0 PASS, 1 FAIL, 2 INCOMPLETE (a check is UNMEASURED).
Evidence: docs/traceability/evidence/kafka-cluster-survival-evidence.json
"""

from __future__ import annotations

import json
import re
import socket
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
EVIDENCE_FILE = "kafka-cluster-survival-evidence.json"
COMPOSE_FILE = REPO_ROOT / "infra" / "compose" / "docker-compose.asset-ml.yml"
VERSIONS_LOCK = REPO_ROOT / "tooling" / "versions.lock"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PASSED = "PASS"
FAILED = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

# Requirement thresholds (R07-M01-T01), not measurements.
REQUIRED_NODES = 3
REQUIRED_REPLICATION_FACTOR = 3
REQUIRED_MIN_ISR = 2
REPLICATION_KEYS = (
    "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR",
    "KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR",
    "KAFKA_DEFAULT_REPLICATION_FACTOR",
)
NODE_RE = re.compile(r"^kafka-\d+$")
LOCK_KEY = "COMPOSE_DIGEST_apache_kafka"


def tcp_reachable(host: str, port: int, timeout: float = 0.5) -> tuple[bool, str]:
    """Read-only reachability probe: open and close one TCP connection."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"{host}:{port} accepted a TCP connection"
    except OSError as exc:
        return False, f"{host}:{port} unreachable ({type(exc).__name__})"


def overall_verdict(checks: list[dict[str, Any]]) -> str:
    statuses = [c["status"] for c in checks]
    if FAILED in statuses:
        return FAILED
    if not statuses or UNMEASURED in statuses:
        return INCOMPLETE
    return PASSED


def exit_code_for(verdict: str) -> int:
    return {PASSED: 0, FAILED: 1}.get(verdict, 2)


def _check(checks: list[dict[str, Any]], name: str, ok: bool, detail: str) -> None:
    checks.append({"check": name, "status": PASSED if ok else FAILED, "detail": detail})


def lock_digest(lock_path: Path) -> str | None:
    try:
        text = lock_path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(rf"^{LOCK_KEY}=(sha256:[0-9a-f]{{64}})\s*$", text, flags=re.MULTILINE)
    return match.group(1) if match else None


def _env(service: dict[str, Any]) -> dict[str, str]:
    env = service.get("environment") or {}
    if isinstance(env, list):  # ["KEY=value", ...] form
        env = dict(item.split("=", 1) for item in env if "=" in item)
    return {str(k): str(v) for k, v in env.items()}


def _host_ports(service: dict[str, Any]) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    for spec in service.get("ports") or []:
        parts = str(spec).split(":")
        if len(parts) == 3 and parts[1].isdigit():
            out.append((parts[0], int(parts[1])))
        elif len(parts) == 2 and parts[0].isdigit():
            out.append(("", int(parts[0])))  # host IP omitted: all interfaces
    return out


def verify_compose_definition(
    compose_path: Path | None = None, lock_path: Path | None = None
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    compose_path = compose_path or COMPOSE_FILE
    lock_path = lock_path or VERSIONS_LOCK
    checks: list[dict[str, Any]] = []
    try:
        compose = yaml.safe_load(compose_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        _check(checks, "compose_file_readable", False, f"{compose_path}: {exc}")
        return checks, {"nodes_declared": [], "broker_endpoints": []}

    services = compose.get("services") or {}
    nodes = {name: svc for name, svc in services.items() if NODE_RE.match(str(name))}
    envs = {name: _env(svc) for name, svc in nodes.items()}
    node_ids = {name: env.get("KAFKA_NODE_ID") for name, env in envs.items()}

    _check(
        checks,
        "three_kraft_nodes_with_distinct_ids",
        len(nodes) == REQUIRED_NODES
        and len(set(node_ids.values())) == len(nodes)
        and None not in node_ids.values(),
        f"nodes {sorted(nodes)} with KAFKA_NODE_IDs {node_ids}",
    )

    digest = lock_digest(lock_path)
    images = {name: str(svc.get("image", "")) for name, svc in nodes.items()}
    unpinned = {n: i for n, i in images.items() if digest is None or i != f"apache/kafka@{digest}"}
    _check(
        checks,
        "images_pinned_to_versions_lock_digest",
        bool(nodes) and digest is not None and not unpinned,
        f"versions.lock {LOCK_KEY}={digest}; nodes not on that digest: {unpinned or 'none'}",
    )

    def controller_port(env: dict[str, str]) -> str | None:
        match = re.search(r"CONTROLLER://[^,]*:(\d+)", env.get("KAFKA_LISTENERS", ""))
        return match.group(1) if match else None

    expected_voters = {
        f"{node_ids[n]}@{n}:{controller_port(envs[n])}"
        for n in nodes
        if node_ids.get(n) is not None
    }
    voter_problems = {
        n: env.get("KAFKA_CONTROLLER_QUORUM_VOTERS")
        for n, env in envs.items()
        if set(str(env.get("KAFKA_CONTROLLER_QUORUM_VOTERS", "")).split(",")) != expected_voters
    }
    _check(
        checks,
        "quorum_voters_list_all_nodes",
        bool(nodes) and not voter_problems,
        f"expected voters {sorted(expected_voters)}; mismatching nodes: {voter_problems or 'none'}",
    )

    rf_problems = {
        f"{n}.{key}": env.get(key)
        for n, env in envs.items()
        for key in REPLICATION_KEYS
        if env.get(key) != str(REQUIRED_REPLICATION_FACTOR)
    }
    _check(
        checks,
        "replication_factor_3_on_every_node",
        bool(nodes) and not rf_problems,
        f"keys {list(REPLICATION_KEYS)}; deviations: {rf_problems or 'none'}",
    )
    isr_problems = {
        n: env.get("KAFKA_MIN_INSYNC_REPLICAS")
        for n, env in envs.items()
        if env.get("KAFKA_MIN_INSYNC_REPLICAS") != str(REQUIRED_MIN_ISR)
    }
    _check(
        checks,
        "min_insync_replicas_2_on_every_node",
        bool(nodes) and not isr_problems,
        f"deviations: {isr_problems or 'none'}",
    )

    def as_int(value: str | None) -> int | None:
        return int(value) if value is not None and value.isdigit() else None

    rfs = [as_int(env.get("KAFKA_DEFAULT_REPLICATION_FACTOR")) for env in envs.values()]
    isrs = [as_int(env.get("KAFKA_MIN_INSYNC_REPLICAS")) for env in envs.values()]
    tolerant = (
        bool(nodes)
        and None not in rfs
        and None not in isrs
        and all(rf <= len(nodes) and rf - isr >= 1 for rf, isr in zip(rfs, isrs, strict=True))
    )
    _check(
        checks,
        "config_tolerates_single_broker_loss",
        tolerant,
        f"default RF per node {rfs}, min ISR per node {isrs}, nodes {len(nodes)}: "
        "acks=all writes stay available with one broker down iff RF <= nodes and RF - minISR >= 1",
    )

    endpoints = {n: _host_ports(svc) for n, svc in nodes.items()}
    flat = [p for ports in endpoints.values() for p in ports]
    _check(
        checks,
        "distinct_loopback_host_ports",
        bool(nodes)
        and all(len(p) == 1 for p in endpoints.values())
        and len({port for _, port in flat}) == len(flat)
        and all(host == "127.0.0.1" for host, _ in flat),
        f"published host ports {endpoints}",
    )

    info = {
        "compose_file": compose_path.name,
        "nodes_declared": sorted(nodes),
        "node_ids": node_ids,
        "versions_lock_digest": digest,
        "broker_endpoints": [f"127.0.0.1:{port}" for _, port in flat],
    }
    return checks, info


# Broker publishing this host port is the one the drill stops (kafka-2 in the
# asset-ml compose; any broker publishing it would do - resolved from docker ps).
DRILL_VICTIM_HOST_PORT = 9094
UNREACHABLE = "UNREACHABLE"


def _docker(args: list[str], timeout_s: float = 120.0) -> subprocess.CompletedProcess:
    return subprocess.run(  # fixed argv, no shell
        ["docker", *args],
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )


def _find_container_for_host_port(host_port: int) -> str | None:
    """The container name publishing ``127.0.0.1:<host_port>->`` (from docker ps)."""
    ps = _docker(["ps", "--format", "{{.Names}}\t{{.Ports}}"])
    if ps.returncode != 0:
        return None
    for line in ps.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and f"127.0.0.1:{host_port}->" in parts[1]:
            return parts[0].strip()
    return None


def _wait_tcp_state(host: str, port: int, want_open: bool, timeout_s: float) -> tuple[bool, str]:
    """Poll a TCP endpoint until it is open (or refused); returns (ok, detail)."""
    deadline = time.monotonic() + timeout_s
    last = ""
    while time.monotonic() < deadline:
        ok, detail = tcp_reachable(host, port, timeout=1.0)
        last = detail
        if ok == want_open:
            return True, detail
        time.sleep(1.0)
    return (
        False,
        f"still {'unreachable' if want_open else 'reachable'} after {timeout_s:.0f}s ({last})",
    )


def execute_single_broker_loss_drill(broker_endpoints: list[str]) -> dict[str, Any]:
    """REAL single-broker loss drill against the live cluster.

    Stops one broker container (the one publishing DRILL_VICTIM_HOST_PORT),
    produces and consumes through the two survivors via the real
    libs/py/fix_events KafkaBackend, restarts it and produces/consumes again.
    The stopped container is always restarted, whatever the outcome.

    Returns {status: PASS|FAIL|UNMEASURED, reason?, ...measurements}.
    """
    from libs.py.fix_events.kafka_backend import KafkaBackend

    def unmeasured(reason: str) -> dict[str, Any]:
        return {"status": UNMEASURED, "reason": reason}

    # 0. The drill only measures a fully reachable cluster.
    probes = [
        tcp_reachable(h, int(p), timeout=1.5)
        for h, p in (e.rsplit(":", 1) for e in broker_endpoints)
    ]
    down = [e for e, (ok, _) in zip(broker_endpoints, probes, strict=True) if not ok]
    if down:
        return unmeasured(f"brokers not reachable ({', '.join(down)}); the drill was not executed")
    victim = _find_container_for_host_port(DRILL_VICTIM_HOST_PORT)
    if victim is None:
        return unmeasured(
            f"no docker container publishing 127.0.0.1:{DRILL_VICTIM_HOST_PORT}-> found "
            "(docker CLI unavailable or cluster not running under docker); drill not executed"
        )

    survivors = [e for e in broker_endpoints if not e.endswith(f":{DRILL_VICTIM_HOST_PORT}")]
    if len(survivors) != len(broker_endpoints) - 1:
        return unmeasured(f"could not isolate the victim's endpoint from {broker_endpoints}")

    run_token = f"drill{int(time.time())}"
    topic = f"fix.events.{run_token}"
    group = f"{run_token}-consumer"
    steps: list[dict[str, Any]] = []
    result: dict[str, Any] = {
        "drill": "docker stop one broker; produce/consume via survivors; restart",
        "stopped_broker": {"host_port": DRILL_VICTIM_HOST_PORT, "container": victim},
        "bootstrap_during_outage": survivors,
        "topic": topic,
        "consumer_group": group,
        "steps": steps,
    }

    def fail(reason: str) -> dict[str, Any]:
        result["status"] = FAILED
        result["reason"] = reason
        return result

    def produce_batch(bus: KafkaBackend, count: int, tag: str) -> int:
        for i in range(count):
            bus.produce(
                f"{run_token}.broker_loss",
                "fix.drill.cluster",
                i % 5,
                {"seq": i, "phase": tag},
                {"correlation_id": f"{run_token}-{tag}"},
            )
        return count

    backend_all = KafkaBackend(bootstrap_servers=list(broker_endpoints), produce_timeout_s=45.0)
    backend_survivors = KafkaBackend(bootstrap_servers=survivors, produce_timeout_s=45.0)
    stopped = False
    try:
        # Phase A: all three brokers up.
        t0 = time.monotonic()
        produce_batch(backend_all, 20, "before")
        consumed_before = backend_all.consume(group, topic, lambda e: None, limit=100)
        steps.append(
            {
                "phase": "before_outage",
                "produced": 20,
                "consumed": consumed_before,
                "elapsed_s": round(time.monotonic() - t0, 2),
            }
        )
        if consumed_before != 20:
            return fail(f"baseline consume delivered {consumed_before}/20 records")

        # Phase B: stop one broker; produce/consume through the other two.
        t_stop = time.monotonic()
        stop = _docker(["stop", victim], timeout_s=120.0)
        stopped = stop.returncode == 0
        if not stopped:
            return fail(f"docker stop {victim} failed: {stop.stderr.strip()}")
        gone, gone_detail = _wait_tcp_state(
            "127.0.0.1", DRILL_VICTIM_HOST_PORT, want_open=False, timeout_s=45.0
        )
        steps.append(
            {
                "phase": "broker_stopped",
                "container": victim,
                "elapsed_s": round(time.monotonic() - t_stop, 2),
                "port_closed": gone,
                "port_detail": gone_detail,
            }
        )
        if not gone:
            return fail(f"broker {victim} still accepting connections after stop ({gone_detail})")
        survivors_up = all(
            tcp_reachable(h, int(p), timeout=1.5)[0]
            for h, p in (e.rsplit(":", 1) for e in survivors)
        )
        if not survivors_up:
            return fail(f"survivors not reachable during outage: {survivors}")

        t_outage = time.monotonic()
        produce_batch(backend_survivors, 25, "during")
        consumed_during = backend_survivors.consume(group, topic, lambda e: None, limit=100)
        steps.append(
            {
                "phase": "during_outage",
                "produced": 25,
                "consumed": consumed_during,
                "bootstrap": survivors,
                "elapsed_s": round(time.monotonic() - t_outage, 2),
            }
        )
        if consumed_during != 25:
            return fail(
                f"consume during outage delivered {consumed_during}/25 "
                f"(expected 25 via {survivors})"
            )
    except Exception as exc:  # the exception IS the measured failure
        return fail(f"outage phase raised {type(exc).__name__}: {exc}")
    finally:
        # Whatever happened above, the cluster must be restored.
        if stopped:
            t_restart = time.monotonic()
            _docker(["start", victim], timeout_s=120.0)
            back, back_detail = _wait_tcp_state(
                "127.0.0.1", DRILL_VICTIM_HOST_PORT, want_open=True, timeout_s=180.0
            )
            steps.append(
                {
                    "phase": "broker_restarted",
                    "container": victim,
                    "port_reachable": back,
                    "port_detail": back_detail,
                    "elapsed_s": round(time.monotonic() - t_restart, 2),
                }
            )
            time.sleep(5.0)  # let it rejoin the ISR before the recovery probe

    # Phase C: all three again (outside finally so failures here are FAIL, not cleanup).
    try:
        t_after = time.monotonic()
        produce_batch(backend_all, 15, "after")
        consumed_after = backend_all.consume(group, topic, lambda e: None, limit=100)
        steps.append(
            {
                "phase": "after_restart",
                "produced": 15,
                "consumed": consumed_after,
                "elapsed_s": round(time.monotonic() - t_after, 2),
            }
        )
        if consumed_after != 15:
            return fail(f"consume after restart delivered {consumed_after}/15")
    except Exception as exc:  # the exception IS the measured failure
        return fail(f"recovery phase raised {type(exc).__name__}: {exc}")
    finally:
        backend_all.close()
        backend_survivors.close()

    result["status"] = PASSED
    result["reason"] = (
        "acks=all produce and consumer-group reads continued on the two survivors "
        f"while {victim} was stopped, and resumed on all three after restart"
    )
    result["totals"] = {
        "produced": 60,
        "consumed": consumed_before + consumed_during + consumed_after,
    }
    return result


def run_cluster_verification(
    compose_path: Path | None = None,
    lock_path: Path | None = None,
    reach: Callable[[str, int], tuple[bool, str]] = tcp_reachable,
    drill: Callable[[list[str]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    checks, info = verify_compose_definition(compose_path, lock_path)

    probes = []
    for endpoint in info["broker_endpoints"]:
        host, port = endpoint.rsplit(":", 1)
        probes.append(reach(host, int(port)))
    reachable = sum(1 for ok, _ in probes if ok)
    probe_detail = "; ".join(d for _, d in probes) or "no broker endpoints declared"
    summary = f"{reachable}/{len(probes)} brokers reachable ({probe_detail})"
    if probes and reachable == len(probes):
        live_status = PASSED
    elif reachable:
        live_status = FAILED  # a partially reachable cluster is an observed degradation
    else:
        live_status = UNMEASURED
        summary += "; no broker is up (the asset-ml compose profile is opt-in)"
    checks.append({"check": "live_brokers_reachable", "status": live_status, "detail": summary})

    if drill is None:
        drill_result = {
            "status": UNMEASURED,
            "reason": (
                "no drill executor wired (in-process call); executing it needs a live "
                "3-broker cluster, the docker CLI and stopping one broker container"
            ),
        }
    else:
        try:
            drill_result = drill(info["broker_endpoints"])
        except Exception as exc:  # the failure is the measurement
            drill_result = {
                "status": FAILED,
                "reason": f"drill raised {type(exc).__name__}: {exc}",
            }
    drill_status = drill_result.get("status", UNMEASURED)
    drill_detail = drill_result.get("reason") or drill_result.get("detail") or "drill executed"
    if drill_status == PASSED:
        drill_detail = f"{drill_detail}; totals={drill_result.get('totals')}"
    checks.append(
        {"check": "single_broker_loss_drill", "status": drill_status, "detail": drill_detail}
    )

    return {
        "compose_configuration": info,
        "live_probe": {
            "brokers_reachable": reachable,
            "brokers_declared": len(probes),
            "details": probe_detail,
        },
        "single_broker_failure_drill": drill_result,
        "checks": checks,
        "verdict": overall_verdict(checks),
    }


def main() -> int:
    print("Kafka Cluster HA & Broker Loss Verification (R07-M01-T01)...")
    res = run_cluster_verification(drill=execute_single_broker_loss_drill)
    for c in res["checks"]:
        print(f"  [{c['status']}] {c['check']}: {c['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence_payload = {
        "test": "R07-M01-T01: Kafka 3-Node HA Cluster & Single-Broker Loss Verification",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "compose_configuration": res["compose_configuration"],
        "live_probe": res["live_probe"],
        "single_broker_failure_drill": res["single_broker_failure_drill"],
        "checks": res["checks"],
        "verdict": res["verdict"],
    }
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    out_file.write_bytes((json.dumps(evidence_payload, indent=2) + "\n").encode("utf-8"))
    print(f"  Evidence written: {out_file}")
    print(f"verify_kafka_cluster: verdict {res['verdict']}")
    return exit_code_for(res["verdict"])


if __name__ == "__main__":
    sys.exit(main())
