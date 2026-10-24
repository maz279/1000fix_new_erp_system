#!/usr/bin/env python3
"""
run_g5_dr_drill.py — Gate G5 PE-007 Disaster Recovery Drill Runner
Milestone R06-M05-T04 (PE-007 / AR-012: High-Availability & Disaster Recovery Validation).

GV-009: this runner measures only what a workstation can observe; it never
stops, fences or promotes a database, so it never fabricates RPO/RTO.

Measured (read-only inspection of infra/compose and docs/runbooks):
- primary PostgreSQL WAL streaming + archiving settings (docker-compose.prod.yml)
- DR warm standby declared as a streaming replica (docker-compose.dr.yml)
- the RB-52 DR runbook exists

UNMEASURED (needs a running primary + DR standby and an executed failover):
RPO (target <= 15 min), RTO (target <= 30 min), Odoo / Mayan EDMS dual-store
document consistency and post-failover control totals.

Verdict: FAIL if any check failed, INCOMPLETE while any check is UNMEASURED,
PASS only when every check was measured and passed.
Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE.

Outputs structured evidence to:
  docs/traceability/evidence/g5-pe007-dr-drill-evidence.json
"""

import json
import sys
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
EVIDENCE_DIR = ROOT_DIR / "docs" / "traceability" / "evidence"
COMPOSE_DIR = ROOT_DIR / "infra" / "compose"
RUNBOOK = ROOT_DIR / "docs" / "runbooks" / "RB-52-dr-disaster-recovery-and-cutover.md"
EVIDENCE_FILE = "g5-pe007-dr-drill-evidence.json"

PASS, FAIL, UNMEASURED, INCOMPLETE = "PASS", "FAIL", "UNMEASURED", "INCOMPLETE"
EXIT_CODES = {PASS: 0, FAIL: 1}
# PostgreSQL 17 server defaults for the settings inspected below.
PG_DEFAULTS = {"wal_level": "replica", "max_wal_senders": "10", "archive_mode": "off"}
NO_FAILOVER = (
    "requires a running primary + DR standby and an executed failover; "
    "this tool never stops, fences or promotes a database"
)

RPO_TARGET_MINUTES = 15.0
RTO_TARGET_MINUTES = 30.0


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
            "rpo",
            f"RPO <= {RPO_TARGET_MINUTES:g} min (replication lag at primary loss)",
            NO_FAILOVER,
        ),
        _unmeasured(
            "rto", f"RTO <= {RTO_TARGET_MINUTES:g} min (failure to service restored)", NO_FAILOVER
        ),
        _unmeasured(
            "dual_store_consistency",
            "Odoo / Mayan EDMS dual-store document consistency after failover",
            "requires Odoo and Mayan EDMS running on the promoted standby and a document hash "
            "comparison; not exercised",
        ),
        _unmeasured("control_totals", "Post-failover data integrity (control totals)", NO_FAILOVER),
    ]


def execute_dr_drill() -> dict:
    checks = [check_primary_replication(), check_dr_standby(), check_runbook(), *drill_checks()]
    verdict = overall_verdict(checks)
    summary = _summary(checks)
    failed = [c["name"] for c in checks if c["status"] == FAIL]
    return {
        "schema": "1000fix-erp/pe-007-dr-drill/2",
        "gate": "G5",
        "milestone": "R06-M05-T04",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "status": verdict,
        "sla_metrics": {
            "rpo_target_minutes": RPO_TARGET_MINUTES,
            "rpo_achieved_seconds": None,
            "rpo_status": _status_of(checks, "rpo"),
            "rto_target_minutes": RTO_TARGET_MINUTES,
            "rto_achieved_seconds": None,
            "rto_status": _status_of(checks, "rto"),
        },
        "drill_summary": summary,
        "checks": checks,
        "conclusion": (
            f"{verdict}: {summary['checks_passed']} passed, {summary['checks_failed']} failed, "
            f"{summary['checks_unmeasured']} UNMEASURED of {summary['checks_total']} checks."
            + (f" Failed: {', '.join(failed)}." if failed else "")
        ),
    }


def main() -> int:
    print("=" * 70)
    print("Gate G5 PE-007 Profile: Disaster Recovery Drill (AR-012 / PE-007)")
    print("=" * 70)

    report = execute_dr_drill()
    for check in report["checks"]:
        print(f"[{check['status']}] {check['name']}: {check['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    out_file.write_bytes((json.dumps(report, indent=2) + "\n").encode("utf-8"))

    print(f"\n{report['conclusion']}")
    print(f"Saved DR drill evidence to {out_file}")
    return EXIT_CODES.get(report["status"], 2)


if __name__ == "__main__":
    sys.exit(main())
