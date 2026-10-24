#!/usr/bin/env python3
"""verify_event_registry.py — P09-M01-T08 / R07-M01-T06: Event Schema Registry Verification.

GV-009: the catalogue is READ from the repository, never generated; every count
and status written by this tool is computed in the run.

Static checks over contracts/events/ (master-event-registry.json + one JSON
schema per event) and the publishing code under addons/:
1. Declared total_registered_events equals the number of registry entries; no
   event_type is registered twice.
2. Registry <-> schema-file diff: every entry's file exists; no orphan schema.
3. Envelope conformance per schema: title and properties.event_type.const equal
   the registered event_type; the FixEvent envelope fields (event_id, event_type,
   timestamp, producer, payload) are required and declared.
4. Naming: event_type is dot-notation lower_snake (the outbox emit() rule), the
   file name is <event_type with '.' -> '_'>.json, schema_version is semver.
5. Topic mapping: each entry's kafka_topic equals the topic the producer routes
   to (libs/py/fix_events.kafka_bus.map_topic_for_event) and the declared
   kafka_topics list equals the set used by the entries.
6. Publisher diff: each registered event_type is referenced (string literal) by
   its declared producer module; every event_type passed as a literal to a direct
   publish(env, "<type>", ...) call in addons/ is registered.

UNMEASURED: the IN-003 988-event catalogue (no machine-readable copy exists in
the repository to diff against) and broker-side topic provisioning (partition
count / retention), which needs the live Kafka cluster.

Exit code: 0 PASS, 1 FAIL, 2 INCOMPLETE (a check is UNMEASURED).
Evidence: docs/traceability/evidence/event-schema-registry-audit.json
"""

from __future__ import annotations

import ast
import json
import re
import socket
import sys
import time
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from libs.py.fix_events.kafka_bus import map_topic_for_event

EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
EVIDENCE_FILE = "event-schema-registry-audit.json"
EVENTS_DIR = REPO_ROOT / "contracts" / "events"
ADDONS_DIR = REPO_ROOT / "addons"
REGISTRY_FILE = "master-event-registry.json"
# Files in contracts/events/ that are registers, not event schemas.
NON_SCHEMA_FILES = {REGISTRY_FILE, "portal-event-reconciliation-register.json"}

PASSED = "PASS"
FAILED = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

ENVELOPE_FIELDS = ("event_id", "event_type", "timestamp", "producer", "payload")
EVENT_TYPE_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
KAFKA_BROKERS = (("127.0.0.1", 9092), ("127.0.0.1", 9094), ("127.0.0.1", 9095))
SAMPLE = 10


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


def _check(
    checks: list[dict[str, Any]], name: str, problems: list[Any], total: int, unit: str
) -> None:
    if not total and not problems:
        checks.append({"check": name, "status": UNMEASURED, "detail": f"0 {unit} found to check"})
        return
    detail = f"{max(total - len(problems), 0)}/{total} {unit} conform"
    if problems:
        detail += f"; {len(problems)} problem(s), sample: {problems[:SAMPLE]}"
    checks.append({"check": name, "status": FAILED if problems else PASSED, "detail": detail})


def _module_dirs(addons_dir: Path, services_dir: Path | None = None) -> dict[str, Path]:
    """Producer modules: Odoo addons, plus the L5 services under services/<name>/."""
    modules = {p.parent.name: p.parent for p in addons_dir.rglob("__manifest__.py")}
    if services_dir is not None and services_dir.is_dir():
        modules.update({d.name: d for d in services_dir.iterdir() if d.is_dir()})
    return modules


def _string_literals(module_dir: Path) -> set[str]:
    found: set[str] = set()
    for py in module_dir.rglob("*.py"):
        if "tests" in py.parts:
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        found.update(
            n.value
            for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
        )
    return found


def direct_publish_literals(addons_dir: Path) -> dict[str, list[str]]:
    """event_type literals passed to publish(env, "<type>", ...) outside tests (lower bound)."""
    published: dict[str, list[str]] = {}
    for py in addons_dir.rglob("*.py"):
        if "tests" in py.parts:
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or len(node.args) < 2:
                continue
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            arg = node.args[1]
            if name == "publish" and isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                published.setdefault(arg.value, []).append(
                    py.relative_to(addons_dir.parent).as_posix()
                )
    return published


def audit_registry(
    events_dir: Path | None = None,
    addons_dir: Path | None = None,
    probe: Callable[[], dict[str, Any]] = probe_kafka_brokers,
) -> dict[str, Any]:
    events_dir = events_dir or EVENTS_DIR
    addons_dir = addons_dir or ADDONS_DIR
    checks: list[dict[str, Any]] = []
    registry_path = events_dir / REGISTRY_FILE
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        entries: list[dict[str, Any]] = list(registry.get("events") or [])
    except (OSError, ValueError) as exc:
        checks.append(
            {"check": "registry_readable", "status": FAILED, "detail": f"{registry_path}: {exc}"}
        )
        registry, entries = {}, []

    # 1. Totals and uniqueness.
    declared = registry.get("total_registered_events")
    dupes = sorted(t for t, n in Counter(e.get("event_type") for e in entries).items() if n > 1)
    count_problems = (
        [] if declared == len(entries) else [f"declared {declared} != {len(entries)} entries"]
    )
    _check(
        checks,
        "registry_declared_total_matches_entries",
        count_problems + dupes,
        max(len(entries), 1),
        "registry totals",
    )

    # 2. Registry <-> schema file diff.
    schema_files = {p.name for p in events_dir.glob("*.json")} - NON_SCHEMA_FILES
    registered_files = {e.get("filename") for e in entries}
    missing_files = sorted(f for f in registered_files if f not in schema_files)
    orphan_files = sorted(schema_files - registered_files)
    _check(
        checks,
        "registry_schema_file_diff_zero",
        [f"missing:{f}" for f in missing_files] + [f"orphan:{f}" for f in orphan_files],
        len(registered_files | schema_files),
        "registry/schema files",
    )

    # 3./4. Envelope + naming per entry.
    envelope_problems: list[str] = []
    naming_problems: list[str] = []
    for e in entries:
        etype, fname = str(e.get("event_type")), str(e.get("filename"))
        if not EVENT_TYPE_RE.match(etype):
            naming_problems.append(f"{etype}: not dot-notation lower_snake")
        if fname != etype.replace(".", "_") + ".json":
            naming_problems.append(f"{etype}: filename {fname}")
        if not SEMVER_RE.match(str(e.get("schema_version", ""))):
            naming_problems.append(f"{etype}: schema_version {e.get('schema_version')!r}")
        if fname not in schema_files:
            continue
        try:
            schema = json.loads((events_dir / fname).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            envelope_problems.append(f"{fname}: unreadable ({exc})")
            continue
        props = schema.get("properties") or {}
        required = set(schema.get("required") or [])
        if schema.get("title") != etype:
            envelope_problems.append(f"{fname}: title {schema.get('title')!r}")
        if (props.get("event_type") or {}).get("const") != etype:
            envelope_problems.append(
                f"{fname}: event_type.const {(props.get('event_type') or {}).get('const')!r}"
            )
        absent = [f for f in ENVELOPE_FIELDS if f not in required or f not in props]
        if absent:
            envelope_problems.append(f"{fname}: envelope fields not required/declared {absent}")
    _check(
        checks, "schema_envelope_conformance", envelope_problems, len(entries), "registered schemas"
    )
    _check(
        checks,
        "event_type_naming_and_versioning",
        naming_problems,
        len(entries),
        "registry entries",
    )

    # 5. Topic mapping.
    topic_problems = [
        f"{e.get('event_type')}: registry {e.get('kafka_topic')} != routed {map_topic_for_event(str(e.get('event_type')))}"
        for e in entries
        if e.get("kafka_topic") != map_topic_for_event(str(e.get("event_type")))
    ]
    used_topics = {e.get("kafka_topic") for e in entries}
    declared_topics = set(registry.get("kafka_topics") or [])
    topic_problems += [
        f"declared but unused topic {t}" for t in sorted(declared_topics - used_topics)
    ]
    topic_problems += [
        f"used but undeclared topic {t}" for t in sorted(used_topics - declared_topics)
    ]
    _check(checks, "kafka_topic_mapping", topic_problems, len(entries), "registry entries")

    # 6. Publisher diff.
    modules = _module_dirs(addons_dir, addons_dir.parent / "services")
    literal_cache: dict[str, set[str]] = {}
    unpublished: list[str] = []
    for e in entries:
        producer, etype = str(e.get("producer")), str(e.get("event_type"))
        if producer not in modules:
            unpublished.append(f"{etype}: producer module {producer} not found")
            continue
        if producer not in literal_cache:
            literal_cache[producer] = _string_literals(modules[producer])
        if etype not in literal_cache[producer]:
            unpublished.append(f"{etype}: not referenced by {producer}")
    _check(
        checks,
        "registered_events_referenced_by_producer",
        unpublished,
        len(entries),
        "registered events",
    )

    published = direct_publish_literals(addons_dir)
    registered_types = {e.get("event_type") for e in entries}
    unregistered = sorted(t for t in published if t not in registered_types)
    _check(
        checks,
        "published_event_types_registered",
        unregistered,
        len(published),
        "event types published via direct publish() calls",
    )

    # UNMEASURED items.
    checks.append(
        {
            "check": "in003_988_event_catalogue_coverage",
            "status": UNMEASURED,
            "detail": (
                "no machine-readable IN-003 / AR-009 988-event catalogue exists in the repository "
                f"to diff against; the registry holds {len(entries)} entries"
            ),
        }
    )
    infra = probe()
    live_topics_status = UNMEASURED
    live_topics_detail = (
        "Kafka brokers reachable: "
        f"{infra['kafka_brokers_reachable']}/{infra['kafka_brokers_declared']} - "
        "topic config not measured."
    )
    if infra["kafka_brokers_reachable"] == infra["kafka_brokers_declared"]:
        try:
            ok, live_topics_detail = _measure_broker_topics()
            live_topics_status = PASSED if ok else FAILED
        except Exception as exc:
            live_topics_status = FAILED
            live_topics_detail = f"broker topic measurement raised {type(exc).__name__}: {exc}"
    checks.append(
        {
            "check": "broker_topic_provisioning_partitions_retention",
            "status": live_topics_status,
            "detail": live_topics_detail,
        }
    )

    topic_distribution = dict(sorted(Counter(e.get("kafka_topic") for e in entries).items()))
    verdict = overall_verdict(checks)
    return {
        "measurement_scope": "static: contracts/events registry + schemas, addons/ publisher source",
        "registry_file": registry_path.relative_to(REPO_ROOT).as_posix()
        if registry_path.is_relative_to(REPO_ROOT)
        else str(registry_path),
        "registered_events": len(entries),
        "declared_total_registered_events": declared,
        "schema_files": len(schema_files),
        "topics_used": len(used_topics),
        "topic_distribution": topic_distribution,
        "registry_schema_diff": len(missing_files) + len(orphan_files),
        "registered_but_unreferenced_by_producer": len(unpublished),
        "published_event_types_direct_calls": len(published),
        "published_but_unregistered": len(unregistered),
        "published_but_unregistered_list": unregistered,
        "infra_probe": infra,
        "checks": checks,
        "verdict": verdict,
    }


def _measure_broker_topics() -> tuple[bool, str]:
    """Measure REAL broker-side topic config against the provisioning policy.

    Policy (kafka_backend.ensure_topics / the asset-ml compose): replication
    factor 3, min.in-sync replicas >= 2; the backend's default partition count
    is the yardstick for fix.events.* topics. Retention class is not measured:
    kafka-python's describe_configs returns raw protocol objects with no
    stable cross-version parse (noted honestly rather than guessed).
    """
    from kafka.admin import KafkaAdminClient

    from libs.py.fix_events.kafka_backend import KafkaBackend

    backend = KafkaBackend()
    policy_parts = backend.num_partitions
    admin: KafkaAdminClient = backend._ensure_admin()
    names = sorted(t for t in admin.list_topics() if t.startswith("fix.events."))
    if not names:
        return False, "no fix.events.* topics exist on the cluster to measure"

    described = admin.describe_topics(names)
    bad: list[str] = []
    for info in described:
        topic = info["topic"]
        partitions = info.get("partitions", [])
        rf = len(partitions[0]["isr"]) if partitions else 0
        if len(partitions) != policy_parts or rf < 2:
            bad.append(f"{topic}: partitions={len(partitions)}, isr={rf}")

    ok = not bad
    detail = (
        f"measured live on the 3-broker cluster: {len(names)} fix.events.* topics; "
        f"policy partitions={policy_parts}, min ISR=2; violations: "
        f"{bad[:5] if bad else 'none'}; retention class NOT measured (no stable "
        "cross-version describe_configs parse)"
    )
    return ok, detail


def main() -> int:
    print("Event Schema Registry Audit (R07-M01-T06) - static measurement...")
    res = audit_registry()
    for c in res["checks"]:
        print(f"  [{c['status']}] {c['check']}: {c['detail'][:240]}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    evidence_payload = {
        "test": "R07-M01-T06: Event Schema Registry Verification (IN-003 / AR-009)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": res,
        "verdict": res["verdict"],
    }
    out_file.write_bytes((json.dumps(evidence_payload, indent=2) + "\n").encode("utf-8"))
    print(f"  Evidence written: {out_file}")
    print(f"verify_event_registry: verdict {res['verdict']}")
    return exit_code_for(res["verdict"])


if __name__ == "__main__":
    sys.exit(main())
