#!/usr/bin/env python3
"""reset_training_cohort.py — Reset hook for Training Environment (infra/environments.yaml).

Data rule for `training`: "curated scenario, resettable per cohort;
residency_classified: never".

GV-009: the previous version reset nothing - it wrote a record claiming
"status": "SUCCESS", five models reset and "fixtures_reseeded": 42 without
touching any database. This hook still performs NO reset, because no programme
document specifies what a reset restores. PE-002 §5.8, QA-004 TDM-28 / §7.1,
TS-002 TD-15 / §4.10-§4.11, TS-001 §4.7 and CH-002 §9.2 require a per-cohort,
automated reset to "the same starting state", but none names the baseline
artefact (a snapshot, a template database or a versioned TS-002 /
curated-scenario pack) or how it is restored. The repository holds no such
artefact either: db/seeds/seed.py is the append-only synthetic developer seed.
The script records what it actually observes:

  TRAINING_DATA_RULE   infra/environments.yaml declares the training environment
                       with residency_classified 'never' and a per-cohort
                       resettable data rule
  TRAINING_TARGET      infra/compose/docker-compose.training.yml defines
                       postgres-training and odoo-training under the 'training'
                       profile with FIX_ENV=training, each published on
                       127.0.0.1 only; the probe endpoints are taken from it
  TRAINING_ENV_UP      TCP probe of those verified endpoints; UNMEASURED when
                       the stack is not running or no endpoint was verified
  COHORT_RESET         FAIL: no reset was performed (no reset specification)

It never writes to any database. Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
ENVIRONMENTS_YAML = REPO_ROOT / "infra" / "environments.yaml"
TRAINING_COMPOSE = REPO_ROOT / "infra" / "compose" / "docker-compose.training.yml"

PASS, FAIL, UNMEASURED, INCOMPLETE = "PASS", "FAIL", "UNMEASURED", "INCOMPLETE"

TRAINING_ENV = "training"
# Services of docker-compose.training.yml whose published ports are probed.
TRAINING_SERVICES = ("postgres-training", "odoo-training")
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}

RESET_NOT_IMPLEMENTED = (
    "no reset performed: PE-002 sec 5.8, QA-004 TDM-28/sec 7.1, TS-002 TD-15/sec 4.11 and "
    "CH-002 sec 9.2 require a per-cohort reset to the same starting state but no document "
    "names the baseline it restores (snapshot, template database or versioned "
    "TS-002/curated-scenario pack) and the repository contains none"
)


def make_check(check_id: str, status: str, detail: str, **measured: object) -> dict:
    return {"id": check_id, "status": status, "detail": detail, **measured}


def overall_verdict(checks: list[dict]) -> str:
    statuses = {check["status"] for check in checks}
    if not statuses:
        return INCOMPLETE
    if FAIL in statuses:
        return FAIL
    return PASS if statuses == {PASS} else INCOMPLETE


def exit_code(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def tcp_open(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def data_rule_check(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return make_check("TRAINING_DATA_RULE", FAIL, f"{path.name} unreadable: {exc}")
    envs = data.get("environments") if isinstance(data, dict) else None
    training = next(
        (e for e in envs or [] if isinstance(e, dict) and e.get("name") == "training"), None
    )
    if training is None:
        return make_check(
            "TRAINING_DATA_RULE", FAIL, f"{path.name} declares no 'training' environment"
        )
    residency = str(training.get("residency_classified"))
    rule = str(training.get("data"))
    ok = residency == "never" and "resettable per cohort" in rule
    return make_check(
        "TRAINING_DATA_RULE",
        PASS if ok else FAIL,
        f"training: data '{rule}', residency_classified '{residency}'",
        data_rule=rule,
        residency_classified=residency,
    )


def _env_mapping(environment: object) -> dict[str, str]:
    """Compose `environment:` as a mapping (accepts the mapping and list forms)."""
    if isinstance(environment, dict):
        return {str(k): str(v) for k, v in environment.items()}
    if isinstance(environment, list):
        pairs = (str(item).split("=", 1) for item in environment)
        return {p[0]: (p[1] if len(p) == 2 else "") for p in pairs}
    return {}


def _published_ports(ports: object) -> list[tuple[str, int]]:
    """(host_ip, published_port) for each compose port entry; host_ip '' = all interfaces."""
    found: list[tuple[str, int]] = []
    for entry in ports if isinstance(ports, list) else []:
        if isinstance(entry, dict):
            host, published = str(entry.get("host_ip", "")), entry.get("published")
        else:
            parts = str(entry).rsplit(":", 2)
            host = parts[0] if len(parts) == 3 else ""
            published = parts[-2] if len(parts) >= 2 else None
        try:
            found.append((host.strip("[]"), int(str(published))))
        except ValueError:
            continue
    return found


def training_target_check(path: Path) -> tuple[dict, list[tuple[str, str, int]]]:
    """Verify the training compose definition and return the endpoints it publishes.

    Only services that declare the training profile and FIX_ENV=training and publish
    exactly one loopback-bound port yield an endpoint; anything else is a FAIL.
    """
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return make_check("TRAINING_TARGET", FAIL, f"{path.name} unreadable: {exc}"), []
    services = data.get("services") if isinstance(data, dict) else None
    services = services if isinstance(services, dict) else {}
    problems: list[str] = []
    endpoints: list[tuple[str, str, int]] = []
    targets: dict[str, dict] = {}
    for name in TRAINING_SERVICES:
        svc = services.get(name)
        if not isinstance(svc, dict):
            problems.append(f"{name}: not defined")
            continue
        env = _env_mapping(svc.get("environment"))
        raw_ports = svc.get("ports") if isinstance(svc.get("ports"), list) else []
        ports = _published_ports(raw_ports)
        profiles = svc.get("profiles") if isinstance(svc.get("profiles"), list) else []
        issues = []
        if TRAINING_ENV not in profiles:
            issues.append(f"profiles {profiles} lack '{TRAINING_ENV}'")
        if env.get("FIX_ENV") != TRAINING_ENV:
            issues.append(f"FIX_ENV is {env.get('FIX_ENV')!r}, not '{TRAINING_ENV}'")
        if len(raw_ports) != 1 or len(ports) != 1:
            issues.append(f"port entries {raw_ports}, expected exactly 1 host-published port")
        elif ports[0][0] not in LOOPBACK_HOSTS:
            issues.append(f"port {ports[0][1]} bound to {ports[0][0] or 'all interfaces'}")
        targets[name] = {"fix_env": env.get("FIX_ENV"), "ports": ports}
        if name == "postgres-training":
            targets[name]["database"] = env.get("POSTGRES_DB")
            if not env.get("POSTGRES_DB"):
                issues.append("POSTGRES_DB not declared")
        if issues:
            problems.append(f"{name}: " + "; ".join(issues))
        else:
            endpoints.append((name, ports[0][0], ports[0][1]))
    if problems:
        return make_check(
            "TRAINING_TARGET", FAIL, f"{path.name}: {problems}", targets=targets
        ), endpoints
    summary = {n: f"{h}:{p}" for n, h, p in endpoints}
    return make_check(
        "TRAINING_TARGET",
        PASS,
        f"{path.name}: training services verified {summary}, "
        f"database {targets['postgres-training']['database']!r}",
        targets=targets,
    ), endpoints


def env_up_check(endpoints: list[tuple[str, str, int]], probe=tcp_open) -> dict:
    if not endpoints:
        return make_check(
            "TRAINING_ENV_UP",
            UNMEASURED,
            "no verified training endpoint to probe (see TRAINING_TARGET)",
            reachable={},
        )
    states = {name: probe(host, port) for name, host, port in endpoints}
    labels = {name: f"{host}:{port}" for name, host, port in endpoints}
    if all(states.values()) and len(endpoints) == len(TRAINING_SERVICES):
        return make_check("TRAINING_ENV_UP", PASS, f"reachable: {labels}", reachable=states)
    down = [f"{n} ({labels[n]})" for n, up in states.items() if not up]
    unverified = [n for n in TRAINING_SERVICES if n not in states]
    detail = f"training stack not reachable: {down}" if down else "training stack reachable"
    if unverified:
        detail += f"; not probed (unverified target): {unverified}"
    return make_check("TRAINING_ENV_UP", UNMEASURED, detail, reachable=states)


def reset_cohort(
    cohort_id: str,
    *,
    environments_yaml: Path = ENVIRONMENTS_YAML,
    compose_yaml: Path = TRAINING_COMPOSE,
    probe=tcp_open,
) -> dict:
    target, endpoints = training_target_check(compose_yaml)
    checks = [
        data_rule_check(environments_yaml),
        target,
        env_up_check(endpoints, probe),
        make_check("COHORT_RESET", FAIL, RESET_NOT_IMPLEMENTED),
    ]
    return {
        "action": "RESET_TRAINING_COHORT",
        "cohort_id": cohort_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "environment": "training",
        "reset_performed": False,
        "models_reset": [],
        "fixtures_reseeded": 0,
        "checks": checks,
        "status": overall_verdict(checks),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reset training cohort dataset")
    parser.add_argument("--cohort", default="cohort-alpha", help="Cohort identifier to reset")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", args.cohort):
        parser.error("--cohort may contain only letters, digits, '.', '_' and '-'")

    record = reset_cohort(args.cohort)
    for check in record["checks"]:
        print(f"  [{check['status']}] {check['id']}: {check['detail']}")
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / f"r10-m04-training-reset-{args.cohort}.json"
    out_file.write_bytes((json.dumps(record, indent=2) + "\n").encode("utf-8"))
    print(f"[{record['status']}] Training cohort {record['cohort_id']}: no records were reset.")
    print(f"Record written: {out_file}")
    return exit_code(record["status"])


if __name__ == "__main__":
    sys.exit(main())
