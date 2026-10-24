#!/usr/bin/env python3
"""
run_g8_full_estate_dr_drill.py — Gate G8 Full-Estate Disaster Recovery Drill Runner (PE-007 / AR-012)
Milestone R09-M05-T03: Full-Estate DR Drill (PostgreSQL, ClickHouse, TimescaleDB, Kafka KRaft, Z4 Standby).

Standard: PE-007 / AR-012 / DoD-15
SLA targets: RPO <= 15 min, RTO <= 2 hours, Bangladesh-resident standby for Z4.

GV-009: this runner measures only what a workstation can observe; it never
blacks out a node, partitions a network or promotes a standby, so it never
fabricates RPO/RTO, record counts, branch or portal totals.

Measured (read-only inspection of infra/compose and docs/runbooks):
- primary PostgreSQL WAL streaming + archiving settings (docker-compose.prod.yml)
- DR warm standby declared as a streaming replica (docker-compose.dr.yml)
- Kafka KRaft quorum shape and broker healthchecks (docker-compose.asset-ml.yml)
- ClickHouse warehouse data persisted on a volume (docker-compose.intelligence.yml)
- a TimescaleDB engine declared anywhere in infra/compose
- the RB-52 DR runbook exists

UNMEASURED (needs the production estate and an executed failover): RPO, RTO,
full-estate integrity audit, post-failover portal verification, Z4 residency
of the promoted standby.

Verdict: FAIL if any check failed, INCOMPLETE while any check is UNMEASURED,
PASS only when every check was measured and passed.
Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE.

Outputs:
  docs/traceability/evidence/g8-pe007-full-estate-dr-drill-evidence.json
  docs/traceability/g8-pe007-disaster-recovery-drill-report.md
"""

import json
import re
import sys
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
EVIDENCE_DIR = ROOT_DIR / "docs" / "traceability" / "evidence"
TRACEABILITY_DIR = ROOT_DIR / "docs" / "traceability"
COMPOSE_DIR = ROOT_DIR / "infra" / "compose"
RUNBOOK = ROOT_DIR / "docs" / "runbooks" / "RB-52-dr-disaster-recovery-and-cutover.md"
EVIDENCE_FILE = "g8-pe007-full-estate-dr-drill-evidence.json"
REPORT_FILE = "g8-pe007-disaster-recovery-drill-report.md"
KAFKA_COMPOSE = "docker-compose.asset-ml.yml"

PASS, FAIL, UNMEASURED, INCOMPLETE = "PASS", "FAIL", "UNMEASURED", "INCOMPLETE"
EXIT_CODES = {PASS: 0, FAIL: 1}
# PostgreSQL 17 server defaults for the settings inspected below.
PG_DEFAULTS = {"wal_level": "replica", "max_wal_senders": "10", "archive_mode": "off"}
ALWAYS_HEALTHY = re.compile(r"\|\|\s*(?:exit\s+0|true)\s*$")
NO_FAILOVER = (
    "requires the production estate and an executed failover; this tool never stops, "
    "fences or promotes a database"
)

RPO_TARGET_SECONDS = 900.0  # 15 minutes
RTO_TARGET_SECONDS = 7200.0  # 2 hours

COMPONENTS_IN_SCOPE = [
    "PostgreSQL primary (postgres-prod)",
    "PostgreSQL DR standby (postgres-dr)",
    "ClickHouse analytical warehouse (clickhouse)",
    "TimescaleDB telemetry engine",
    "Apache Kafka KRaft 3-node event bus (kafka-1..3)",
    "53-branch edge service network (OU-01..OU-53)",
    "Next.js customer & seller portals (P01..P12)",
    "Sovereign standby cluster (Z4 Bangladesh residency)",
]


# --------------------------------------------------------------------------- helpers
def _result(
    check_id: str, name: str, problems: list[str], unknowns: list[str], detail: str
) -> dict:
    """FAIL on any problem, UNMEASURED on anything not observable, else PASS."""
    if problems:
        status, detail = FAIL, "; ".join(problems)
    elif unknowns:
        status, detail = UNMEASURED, "; ".join(unknowns)
    else:
        status = PASS
    return {"id": check_id, "name": name, "status": status, "detail": detail}


def _unmeasured(check_id: str, name: str, reason: str) -> dict:
    return _result(check_id, name, [], [reason], "")


def overall_verdict(checks: list[dict]) -> str:
    statuses = [c["status"] for c in checks]
    if FAIL in statuses:
        return FAIL
    if not statuses or UNMEASURED in statuses:
        return INCOMPLETE
    return PASS


def _summary(checks: list[dict]) -> dict:
    return {
        "checks_total": len(checks),
        "checks_passed": sum(c["status"] == PASS for c in checks),
        "checks_failed": sum(c["status"] == FAIL for c in checks),
        "checks_unmeasured": sum(c["status"] == UNMEASURED for c in checks),
    }


def _status_of(checks: list[dict], check_id: str) -> str:
    return next(c["status"] for c in checks if c["id"] == check_id)


def _services(path: Path, problems: list[str]) -> dict:
    """All service definitions of one compose file, recording why there are none."""
    if not path.is_file():
        problems.append(f"{path.name} not found")
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        problems.append(f"{path.name} unreadable: {exc}")
        return {}
    services = data.get("services") if isinstance(data, dict) else None
    if not isinstance(services, dict) or not services:
        problems.append(f"{path.name} declares no services")
        return {}
    return services


def _service(path: Path, name: str, problems: list[str]) -> dict | None:
    services = _services(path, problems)
    service = services.get(name)
    if isinstance(service, dict):
        return service
    if services:
        problems.append(f"service {name} not declared in {path.name}")
    return None


def _pg_settings(service: dict) -> dict[str, str]:
    """PostgreSQL settings passed as `-c key=value` on a compose command."""
    command = service.get("command") or []
    tokens = command.split() if isinstance(command, str) else [str(t) for t in command]
    settings = dict(PG_DEFAULTS)
    for flag, setting in pairwise(tokens):
        if flag == "-c" and "=" in setting:
            key, _, value = setting.partition("=")
            settings[key.strip()] = value.strip()
    return settings


def _env(service: dict) -> dict[str, str]:
    env = service.get("environment") or {}
    if isinstance(env, list):
        return {k: v for k, _, v in (str(item).partition("=") for item in env)}
    return {str(k): str(v) for k, v in env.items()} if isinstance(env, dict) else {}


def _int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


def _kafka_brokers(problems: list[str]) -> dict[str, dict]:
    services = _services(COMPOSE_DIR / KAFKA_COMPOSE, problems)
    brokers = {
        name: svc
        for name, svc in services.items()
        if isinstance(svc, dict) and "kafka" in str(svc.get("image", "")).lower()
    }
    if services and not brokers:
        problems.append(f"no Kafka broker services declared in {KAFKA_COMPOSE}")
    return brokers


# --------------------------------------------------------------------------- checks
def check_primary_replication() -> dict:
    problems: list[str] = []
    detail = ""
    service = _service(COMPOSE_DIR / "docker-compose.prod.yml", "postgres-prod", problems)
    if service is not None:
        s = _pg_settings(service)
        if s["wal_level"] not in ("replica", "logical"):
            problems.append(f"wal_level={s['wal_level']} (streaming needs replica or logical)")
        if not s["max_wal_senders"].isdigit() or int(s["max_wal_senders"]) < 1:
            problems.append(f"max_wal_senders={s['max_wal_senders']} (needs >= 1)")
        if s["archive_mode"] not in ("on", "always"):
            problems.append(f"archive_mode={s['archive_mode']} (WAL archiving off)")
        if not s.get("archive_command"):
            problems.append("archive_command not set")
        sync = s.get("synchronous_standby_names") or "unset (asynchronous: RPO > 0 on primary loss)"
        detail = (
            f"postgres-prod: wal_level={s['wal_level']}, max_wal_senders={s['max_wal_senders']}, "
            f"archive_mode={s['archive_mode']}, synchronous_standby_names={sync}"
        )
    return _result(
        "primary_replication_config",
        "Primary PostgreSQL WAL streaming + archiving configured",
        problems,
        [],
        detail,
    )


def check_dr_standby() -> dict:
    problems: list[str] = []
    unknowns: list[str] = []
    service = _service(COMPOSE_DIR / "docker-compose.dr.yml", "postgres-dr", problems)
    if service is not None:
        s = _pg_settings(service)
        if s.get("hot_standby", "on") != "on":
            problems.append("postgres-dr hot_standby is not on")
        if not s.get("primary_conninfo"):
            problems.append("postgres-dr has no primary_conninfo (nothing to stream from)")
        definition = json.dumps(service, default=str)
        if "standby.signal" not in definition and "pg_basebackup" not in definition:
            image = str(service.get("image", ""))
            if image.startswith("postgres:"):
                problems.append(
                    "postgres-dr declares no standby bootstrap (pg_basebackup -R / standby.signal); "
                    "the stock postgres image initialises an independent primary, so it never "
                    "enters recovery"
                )
            else:
                unknowns.append(f"standby bootstrap not visible in compose (custom image {image})")
        if "pg_is_in_recovery" not in json.dumps(service.get("healthcheck", {}), default=str):
            problems.append("postgres-dr healthcheck does not assert pg_is_in_recovery()")
    return _result(
        "dr_standby_config",
        "DR warm standby declared as a streaming replica",
        problems,
        unknowns,
        "postgres-dr: primary_conninfo set, standby bootstrap declared, "
        "healthcheck asserts recovery mode",
    )


def check_kafka_quorum() -> dict:
    problems: list[str] = []
    detail = ""
    brokers = _kafka_brokers(problems)
    if brokers:
        envs = {name: _env(svc) for name, svc in brokers.items()}
        voter_lists = {e.get("KAFKA_CONTROLLER_QUORUM_VOTERS", "") for e in envs.values()}
        voters = (
            [v for v in next(iter(voter_lists)).split(",") if v] if len(voter_lists) == 1 else []
        )
        controllers = [
            n for n, e in envs.items() if "controller" in e.get("KAFKA_PROCESS_ROLES", "")
        ]
        if len(brokers) < 3:
            problems.append(f"{len(brokers)} Kafka broker(s) declared (needs >= 3)")
        if len(voters) < 3:
            problems.append("brokers do not share one KAFKA_CONTROLLER_QUORUM_VOTERS list of >= 3")
        if len(controllers) < 3:
            problems.append(
                f"{len(controllers)} KRaft controller(s) (a quorum surviving one loss needs >= 3)"
            )
        for name, e in envs.items():
            rf = _int(e.get("KAFKA_DEFAULT_REPLICATION_FACTOR"), 1)
            isr = _int(e.get("KAFKA_MIN_INSYNC_REPLICAS"), 1)
            if rf < 3 or not 2 <= isr < rf:
                problems.append(
                    f"{name}: replication factor {rf} / min ISR {isr} (needs RF >= 3, 2 <= ISR < RF)"
                )
        detail = (
            f"{len(brokers)} brokers, {len(controllers)} KRaft controllers, {len(voters)} quorum "
            "voters; replication factor and min ISR tolerate one broker loss"
        )
    return _result(
        "kafka_kraft_quorum_config",
        "Kafka KRaft quorum survives one broker loss",
        problems,
        [],
        detail,
    )


def check_kafka_healthchecks() -> dict:
    problems: list[str] = []
    brokers = _kafka_brokers(problems)
    for name, svc in brokers.items():
        healthcheck = svc.get("healthcheck")
        test = healthcheck.get("test") if isinstance(healthcheck, dict) else None
        text = " ".join(str(t) for t in test) if isinstance(test, list) else str(test or "")
        if not text or "NONE" in text.split():
            problems.append(f"{name}: no healthcheck")
        elif ALWAYS_HEALTHY.search(text):
            problems.append(
                f"{name}: healthcheck ends in '|| exit 0' and can never report unhealthy"
            )
    return _result(
        "kafka_healthchecks",
        "Kafka broker healthchecks can report an unhealthy broker",
        problems,
        [],
        f"{len(brokers)} broker healthchecks propagate failure",
    )


def check_clickhouse_persistence() -> dict:
    problems: list[str] = []
    service = _service(COMPOSE_DIR / "docker-compose.intelligence.yml", "clickhouse", problems)
    if service is not None and not any(
        "/var/lib/clickhouse" in str(volume) for volume in service.get("volumes") or []
    ):
        problems.append(
            "clickhouse mounts no volume at /var/lib/clickhouse - warehouse data does not "
            "survive the loss of its container"
        )
    return _result(
        "clickhouse_persistence",
        "ClickHouse warehouse data persisted on a volume",
        problems,
        [],
        "clickhouse mounts /var/lib/clickhouse on a volume",
    )


def check_timescaledb_declared() -> dict:
    files = sorted(COMPOSE_DIR.glob("docker-compose*.yml"))
    found: list[str] = []
    for path in files:
        # Parse problems of an unrelated overlay are not this check's concern.
        for name, svc in _services(path, []).items():
            if isinstance(svc, dict) and "timescale" in str(svc.get("image", "")).lower():
                found.append(f"{path.name}:{name}")
    problems = (
        []
        if found
        else [
            f"no service in {len(files)} compose file(s) uses a TimescaleDB image (the telemetry "
            "hypertable DDL needs CREATE EXTENSION timescaledb)"
        ]
    )
    return _result(
        "timescaledb_declared",
        "TimescaleDB telemetry engine declared in infra/compose",
        problems,
        [],
        f"TimescaleDB image declared by {', '.join(found)}",
    )


def check_runbook() -> dict:
    present = RUNBOOK.is_file() and RUNBOOK.stat().st_size > 0
    return _result(
        "runbook_present",
        "RB-52 DR runbook present",
        [] if present else [f"{RUNBOOK.name} missing or empty"],
        [],
        f"{RUNBOOK.name} present",
    )


def drill_checks() -> list[dict]:
    return [
        _unmeasured("rpo", f"RPO <= {RPO_TARGET_SECONDS:g} s (data loss at failover)", NO_FAILOVER),
        _unmeasured(
            "rto", f"RTO <= {RTO_TARGET_SECONDS:g} s (sovereign standby promotion)", NO_FAILOVER
        ),
        _unmeasured(
            "integrity_audit",
            "Full-estate integrity audit (ledgers, escrow, serials, telemetry, ClickHouse views)",
            "requires checksums taken on the primary before and on the promoted standby after a "
            "failover; not exercised",
        ),
        _unmeasured(
            "post_failover_portals",
            "Post-failover portal & JSON-RPC verification (P01..P12)",
            NO_FAILOVER,
        ),
        _unmeasured(
            "z4_residency",
            "Promoted standby resident in Bangladesh (Z4)",
            "requires the Dhaka DR site; data residency of a real host cannot be observed from "
            "a workstation",
        ),
    ]


def execute_full_estate_dr_drill() -> dict:
    checks = [
        check_primary_replication(),
        check_dr_standby(),
        check_kafka_quorum(),
        check_kafka_healthchecks(),
        check_clickhouse_persistence(),
        check_timescaledb_declared(),
        check_runbook(),
        *drill_checks(),
    ]
    return {
        "$schema": "1000fix-erp/evidence/1",
        "gate": "G8",
        "milestone": "R09-M05",
        "task": "R09-M05-T03",
        "standard": "PE-007 / AR-012 / DoD-15",
        "drill_type": "Full-Estate Disaster Recovery & Sovereign Failover Drill",
        "drill_executed_at": datetime.now(UTC).isoformat(),
        "verdict": overall_verdict(checks),
        "targets": {
            "rpo_max_allowed_seconds": RPO_TARGET_SECONDS,
            "rto_max_allowed_seconds": RTO_TARGET_SECONDS,
            "data_loss_records_allowed": 0,
            "sovereign_residency_target": "Bangladesh (Dhaka DC Z4)",
        },
        "measured_metrics": {
            "rpo_measured_seconds": None,
            "rpo_status": _status_of(checks, "rpo"),
            "rto_measured_seconds": None,
            "rto_status": _status_of(checks, "rto"),
            "data_loss_records": None,
            "replication_lag_ms": None,
            "branches_verified_online": None,
            "portals_verified_healthy": None,
            "sovereign_zone_promoted": None,
            "note": "None = not measured: no failover was executed by this run",
        },
        "components_in_scope": COMPONENTS_IN_SCOPE,
        "drill_scenario": "Catastrophic Primary Datacenter Outage with Automated Sovereign Standby Failover to Dhaka DC (Z4)",
        "summary": _summary(checks),
        "checks": checks,
    }


def _cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _measured(seconds: float | None) -> str:
    return "not measured" if seconds is None else f"{seconds:g} s"


def render_report(evidence: dict) -> str:
    verdict = evidence["verdict"]
    metrics = evidence["measured_metrics"]
    summary = evidence["summary"]
    rows = [
        f"| {i} | {_cell(c['name'])} | **{c['status']}** | {_cell(c['detail'])} |"
        for i, c in enumerate(evidence["checks"], start=1)
    ]
    signoff = (
        "Every check was measured and passed; the drill is eligible for sign-off by the "
        "Principal SRE, the Lead Database Architect and the CTO."
        if verdict == PASS
        else f"Not eligible for sign-off: the computed verdict is {verdict}."
    )
    lines = [
        "# Gate G8 Full-Estate Disaster Recovery Drill Report (PE-007)",
        "",
        "- **Standard**: `PE-007` (Disaster Recovery & High Availability) & `AR-012`",
        "- **Milestone**: R09-M05 (Task R09-M05-T03)",
        f"- **Execution Date**: {evidence['drill_executed_at']}",
        f"- **Overall Verdict**: **`{verdict}`** ({summary['checks_passed']} passed, "
        f"{summary['checks_failed']} failed, {summary['checks_unmeasured']} UNMEASURED)",
        "",
        "Generated by `tooling/dr/run_g8_full_estate_dr_drill.py`. A check is PASS or FAIL only "
        "when it was measured in this run; anything that needs the production estate and an "
        "executed failover is UNMEASURED and keeps the verdict from being PASS.",
        "",
        "## 1. SLA Metrics",
        "",
        "| SLA Metric | Target | Measured | Status |",
        "|---|---|---|:---:|",
        f"| RPO | <= {RPO_TARGET_SECONDS:g} s | {_measured(metrics['rpo_measured_seconds'])} "
        f"| **{metrics['rpo_status']}** |",
        f"| RTO | <= {RTO_TARGET_SECONDS:g} s | {_measured(metrics['rto_measured_seconds'])} "
        f"| **{metrics['rto_status']}** |",
        "",
        "## 2. Checks",
        "",
        "| # | Check | Status | Detail |",
        "|---|---|:---:|---|",
        *rows,
        "",
        "## 3. Sign-Off",
        "",
        signoff,
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    print("=== Gate G8 Full-Estate Disaster Recovery Drill (PE-007 / AR-012) ===")
    evidence = execute_full_estate_dr_drill()
    for check in evidence["checks"]:
        print(f"  [{check['status']}] {check['name']}: {check['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    out_file.write_bytes(
        (json.dumps(evidence, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    )
    TRACEABILITY_DIR.mkdir(parents=True, exist_ok=True)
    report_file = TRACEABILITY_DIR / REPORT_FILE
    report_file.write_bytes(render_report(evidence).encode("utf-8"))

    summary = evidence["summary"]
    print(
        f"Gate G8 Full-Estate DR Drill verdict: {evidence['verdict']} ({summary['checks_passed']} "
        f"passed, {summary['checks_failed']} failed, {summary['checks_unmeasured']} UNMEASURED)"
    )
    print(f"Evidence: {out_file}\nReport:   {report_file}")
    return EXIT_CODES.get(evidence["verdict"], 2)


if __name__ == "__main__":
    sys.exit(main())
