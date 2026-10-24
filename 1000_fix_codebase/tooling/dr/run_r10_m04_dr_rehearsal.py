#!/usr/bin/env python3
"""run_r10_m04_dr_rehearsal.py — Milestone R10-M04 Task T03 Disaster Recovery Drill Runner.

Rehearses RB-52 (docs/runbooks/RB-52-dr-disaster-recovery-and-cutover.md):
1. Warm standby continuous replication status (RPO <= 15 minutes).
2. Primary fencing and split-brain prevention.
3. Standby promotion to active read-write mode.
4. Total failover recovery time within the RTO budget (RTO <= 2 hours).
5. Post-failover transactional consistency and write test.

GV-009: this runner never fences, stops or promotes a database and never
writes a test record, so it never reports a replication lag, promotion time
or RTO it did not observe.

Measured (read-only): the RB-52 runbook exists; the primary
(docker-compose.prod.yml) is configured for WAL streaming + archiving; the DR
standby (docker-compose.dr.yml) is declared as a streaming replica.

UNMEASURED: every rehearsal step above (needs the prod + dr compose profiles
running and an operator-executed cutover).

Verdict: FAIL if any check failed, INCOMPLETE while any check is UNMEASURED,
PASS only when every check was measured and passed.
Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE.

Emits docs/traceability/evidence/r10-m04-dr-rehearsal-evidence.json
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
COMPOSE_DIR = REPO_ROOT / "infra" / "compose"
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "RB-52-dr-disaster-recovery-and-cutover.md"
EVIDENCE_FILE = "r10-m04-dr-rehearsal-evidence.json"

PASS, FAIL, UNMEASURED, INCOMPLETE = "PASS", "FAIL", "UNMEASURED", "INCOMPLETE"
EXIT_CODES = {PASS: 0, FAIL: 1}
# PostgreSQL 17 server defaults for the settings inspected below.
PG_DEFAULTS = {"wal_level": "replica", "max_wal_senders": "10", "archive_mode": "off"}
NO_CUTOVER = (
    "requires the prod + dr compose profiles running and an operator-executed RB-52 cutover; "
    "this tool never fences, stops or promotes a database"
)

RPO_TARGET_MINUTES = 15
RTO_TARGET_HOURS = 2


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


def _service(path: Path, name: str, problems: list[str]) -> dict | None:
    """Return one compose service definition, recording why it is missing."""
    if not path.is_file():
        problems.append(f"{path.name} not found")
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        problems.append(f"{path.name} unreadable: {exc}")
        return None
    services = data.get("services") if isinstance(data, dict) else None
    service = services.get(name) if isinstance(services, dict) else None
    if not isinstance(service, dict):
        problems.append(f"service {name} not declared in {path.name}")
        return None
    return service


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


# --------------------------------------------------------------------------- checks
def check_runbook() -> dict:
    present = RUNBOOK.is_file() and RUNBOOK.stat().st_size > 0
    return _result(
        "runbook_present",
        "RB-52 DR & cutover runbook present",
        [] if present else [f"{RUNBOOK.name} missing or empty"],
        [],
        f"{RUNBOOK.name} present",
    )


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


def rehearsal_checks() -> list[dict]:
    return [
        _unmeasured(
            "replication_lag_rpo",
            f"Replication lag within RPO <= {RPO_TARGET_MINUTES} min (RB-52 step 2)",
            NO_CUTOVER,
        ),
        _unmeasured(
            "primary_fencing", "Primary fenced, split-brain prevented (RB-52 step 3)", NO_CUTOVER
        ),
        _unmeasured(
            "standby_promotion", "Standby promoted to read-write (RB-52 step 4)", NO_CUTOVER
        ),
        _unmeasured(
            "ingress_reroute", "Kong / edge re-routed to the DR backend (RB-52 step 5)", NO_CUTOVER
        ),
        _unmeasured(
            "post_cutover_write",
            "Synthetic work order written on the promoted standby (RB-52 step 6)",
            NO_CUTOVER,
        ),
        _unmeasured("rto", f"End-to-end failover within RTO <= {RTO_TARGET_HOURS} h", NO_CUTOVER),
    ]


def execute_dr_rehearsal() -> dict:
    checks = [check_runbook(), check_primary_replication(), check_dr_standby(), *rehearsal_checks()]
    return {
        "test": "R10-M04-T03: Disaster Recovery Warm Standby Rehearsal & Cutover Drill",
        "timestamp": datetime.now(UTC).isoformat(),
        "runbook": "docs/runbooks/RB-52-dr-disaster-recovery-and-cutover.md",
        "target_rpo_minutes": RPO_TARGET_MINUTES,
        "actual_rpo_seconds": None,
        "target_rto_hours": RTO_TARGET_HOURS,
        "actual_rto_seconds": None,
        "rpo_compliant": None,
        "rto_compliant": None,
        "summary": _summary(checks),
        "checks": checks,
        "status": overall_verdict(checks),
    }


def main() -> int:
    print("=" * 80)
    print("1000FiX — Disaster Recovery & Cutover Rehearsal Runner (R10-M04-T03)")
    print("=" * 80)
    drill = execute_dr_rehearsal()
    for check in drill["checks"]:
        print(f"[{check['status']}] {check['name']:<60} - {check['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    out_file.write_bytes((json.dumps(drill, indent=2) + "\n").encode("utf-8"))

    summary = drill["summary"]
    print("-" * 80)
    print(
        f"Rehearsal Outcome: {drill['status']} ({summary['checks_passed']} passed, "
        f"{summary['checks_failed']} failed, {summary['checks_unmeasured']} UNMEASURED)"
    )
    status = {c["id"]: c["status"] for c in drill["checks"]}
    print(f"RPO: {status['replication_lag_rpo']} | RTO: {status['rto']}")
    print(f"Evidence written to: {out_file}")
    print("=" * 80)
    return EXIT_CODES.get(drill["status"], 2)


if __name__ == "__main__":
    sys.exit(main())
