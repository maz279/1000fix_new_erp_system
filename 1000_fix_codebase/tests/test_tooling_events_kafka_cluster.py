"""GV-009: tooling/events/verify_kafka_cluster.py parses the compose definition
and probes the brokers - a mis-configured cluster is a FAIL, unreachable brokers
and the broker-loss drill are UNMEASURED, and the verdict is never a literal
PASS."""

from __future__ import annotations

import importlib.util
import json
import socket
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "events" / "verify_kafka_cluster.py"
DIGEST = "sha256:" + "ab" * 32


def _load():
    spec = importlib.util.spec_from_file_location("verify_kafka_cluster_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod(monkeypatch, tmp_path):
    def no_network(*args, **kwargs):
        raise OSError("network disabled in tests")

    monkeypatch.setattr(socket, "create_connection", no_network)
    module = _load()
    monkeypatch.setattr(module, "EVIDENCE_DIR", tmp_path / "evidence")
    return module


def _node(node_id: int, host_port: int, min_isr: int = 2, digest: str = DIGEST) -> str:
    return f"""  kafka-{node_id}:
    image: apache/kafka@{digest}
    environment:
      KAFKA_NODE_ID: {node_id}
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka-1:9093,2@kafka-2:9093,3@kafka-3:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: {min_isr}
    ports:
      - "127.0.0.1:{host_port}:9092"
"""


def _write(tmp_path: Path, nodes: list[str]) -> tuple[Path, Path]:
    compose = tmp_path / "compose.yml"
    compose.write_text("services:\n" + "".join(nodes), encoding="utf-8")
    lock = tmp_path / "versions.lock"
    lock.write_text(f"COMPOSE_DIGEST_apache_kafka={DIGEST}\n", encoding="utf-8")
    return compose, lock


def _statuses(res):
    return {c["check"]: c["status"] for c in res["checks"]}


def test_valid_compose_with_unreachable_brokers_is_incomplete(mod, tmp_path):
    compose, lock = _write(tmp_path, [_node(1, 9092), _node(2, 9094), _node(3, 9095)])
    res = mod.run_cluster_verification(compose, lock)
    statuses = _statuses(res)
    assert statuses.pop("live_brokers_reachable") == "UNMEASURED"
    assert statuses.pop("single_broker_loss_drill") == "UNMEASURED"
    assert set(statuses.values()) == {"PASS"}
    assert res["verdict"] == "INCOMPLETE"


def test_misconfigured_cluster_is_a_fail(mod, tmp_path):
    compose, lock = _write(
        tmp_path,
        [_node(1, 9092, min_isr=3), _node(2, 9094, digest="sha256:" + "cd" * 32)],
    )
    res = mod.run_cluster_verification(compose, lock)
    statuses = _statuses(res)
    assert statuses["three_kraft_nodes_with_distinct_ids"] == "FAIL"
    assert statuses["images_pinned_to_versions_lock_digest"] == "FAIL"
    assert statuses["min_insync_replicas_2_on_every_node"] == "FAIL"
    assert statuses["config_tolerates_single_broker_loss"] == "FAIL"
    assert res["verdict"] == "FAIL"
    assert mod.exit_code_for(res["verdict"]) == 1


def test_partially_reachable_cluster_fails_and_full_reach_still_not_pass(mod, tmp_path):
    compose, lock = _write(tmp_path, [_node(1, 9092), _node(2, 9094), _node(3, 9095)])
    partial = mod.run_cluster_verification(compose, lock, reach=lambda h, p: (p != 9094, "stub"))
    assert _statuses(partial)["live_brokers_reachable"] == "FAIL"
    full = mod.run_cluster_verification(compose, lock, reach=lambda h, p: (True, "stub"))
    assert _statuses(full)["live_brokers_reachable"] == "PASS"
    assert full["verdict"] == "INCOMPLETE"  # the broker-loss drill is never assumed


def test_main_writes_the_computed_verdict(mod, tmp_path, monkeypatch):
    compose, lock = _write(tmp_path, [_node(1, 9092), _node(2, 9094), _node(3, 9095)])
    monkeypatch.setattr(mod, "COMPOSE_FILE", compose)
    monkeypatch.setattr(mod, "VERSIONS_LOCK", lock)
    assert mod.main() == 2
    evidence = json.loads((tmp_path / "evidence" / mod.EVIDENCE_FILE).read_text(encoding="utf-8"))
    assert evidence["verdict"] == "INCOMPLETE"
    assert evidence["single_broker_failure_drill"]["status"] == "UNMEASURED"
