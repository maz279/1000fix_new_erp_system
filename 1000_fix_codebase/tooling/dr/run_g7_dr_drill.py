#!/usr/bin/env python3
"""
run_g7_dr_drill.py — Gate G7 Disaster Recovery Drill Runner (PE-007 / AR-012)
Milestone R08-M05-T03: High-Availability & Disaster Recovery Validation for Marketplace Go-Live (Month 30).

GV-009: this runner measures only what a workstation can observe; it never
crashes a node, partitions a network or promotes a standby, so it never
fabricates RPO/RTO, replication lag or branch counts.

Measured (read-only inspection of infra/compose and docs/runbooks):
- primary PostgreSQL WAL streaming + archiving settings (docker-compose.prod.yml)
- DR warm standby declared as a streaming replica (docker-compose.dr.yml)
- Kafka KRaft quorum shape and broker healthchecks (docker-compose.asset-ml.yml)
- the RB-52 DR runbook exists

UNMEASURED (needs the running estate and an executed drill): RPO (target 0 s),
RTO (target < 60 s), marketplace / settlement state preservation, 53-branch
offline continuity, post-failover intake and settlement operations.

Verdict: FAIL if any check failed, INCOMPLETE while any check is UNMEASURED,
PASS only when every check was measured and passed.
Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE.

Outputs structured evidence to:
  docs/traceability/evidence/g7-pe007-dr-drill-evidence.json
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
COMPOSE_DIR = ROOT_DIR / "infra" / "compose"
RUNBOOK = ROOT_DIR / "docs" / "runbooks" / "RB-52-dr-disaster-recovery-and-cutover.md"
EVIDENCE_FILE = "g7-pe007-dr-drill-evidence.json"
KAFKA_COMPOSE = "docker-compose.asset-ml.yml"

PASS, FAIL, UNMEASURED, INCOMPLETE = "PASS", "FAIL", "UNMEASURED", "INCOMPLETE"
EXIT_CODES = {PASS: 0, FAIL: 1}
# PostgreSQL 17 server defaults for the settings inspected below.
PG_DEFAULTS = {"wal_level": "replica", "max_wal_senders": "10", "archive_mode": "off"}
ALWAYS_HEALTHY = re.compile(r"\|\|\s*(?:exit\s+0|true)\s*$")
NO_FAILOVER = (
    "requires a running primary + DR standby and an executed failover; "
    "this tool never stops, fences or promotes a database"
)

RPO_TARGET_SECONDS = 0.0
RTO_TARGET_SECONDS = 60.0


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
        _unmeasured(
            "rpo", f"RPO = {RPO_TARGET_SECONDS:g} s (zero data loss at failover)", NO_FAILOVER
        ),
        _unmeasured(
            "rto", f"RTO < {RTO_TARGET_SECONDS:g} s (standby promotion + re-route)", NO_FAILOVER
        ),
        _unmeasured(
            "marketplace_state",
            "Multi-tenant marketplace & settlement state preserved across failover",
            "requires a failover with ledger / INT-007 payout checksums compared before and "
            "after; not exercised",
        ),
        _unmeasured(
            "branch_offline_continuity",
            "53-branch offline cache continuity & sync-queue recovery",
            "requires branch edge clients connected during a failover; not reachable from a "
            "workstation",
        ),
        _unmeasured(
            "post_failover_operations",
            "Service intake & settlement payout on promoted infrastructure",
            NO_FAILOVER,
        ),
    ]


def execute_dr_drill() -> dict:
    checks = [
        check_primary_replication(),
        check_dr_standby(),
        check_kafka_quorum(),
        check_kafka_healthchecks(),
        check_runbook(),
        *drill_checks(),
    ]
    return {
        "gate": "G7",
        "milestone": "R08-M05",
        "task": "R08-M05-T03",
        "standard": "PE-007 / AR-012 (Disaster Recovery & High Availability)",
        "drill_executed_at": datetime.now(UTC).isoformat(),
        "verdict": overall_verdict(checks),
        "metrics": {
            "rpo_target_seconds": RPO_TARGET_SECONDS,
            "rpo_measured_seconds": None,
            "rto_target_seconds": RTO_TARGET_SECONDS,
            "rto_measured_seconds": None,
            "data_loss_records": None,
            "replication_lag_ms": None,
            "branches_verified_online": None,
            "note": "None = not measured: no failover was executed by this run",
        },
        "drill_scenario": "Sudden Primary DB & Marketplace Gateway Crash with Multi-Division Zone Partition",
        "summary": _summary(checks),
        "checks": checks,
    }


def main() -> int:
    print("Executing Gate G7 Disaster Recovery Drill (PE-007 / AR-012)...")
    evidence = execute_dr_drill()
    for check in evidence["checks"]:
        print(f"  [{check['status']}] {check['name']}: {check['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    out_file.write_bytes(
        (json.dumps(evidence, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    )

    summary = evidence["summary"]
    print(
        f"Gate G7 DR Drill verdict: {evidence['verdict']} ({summary['checks_passed']} passed, "
        f"{summary['checks_failed']} failed, {summary['checks_unmeasured']} UNMEASURED)"
    )
    print(f"Evidence written to {out_file}")
    return EXIT_CODES.get(evidence["verdict"], 2)


if __name__ == "__main__":
    sys.exit(main())
