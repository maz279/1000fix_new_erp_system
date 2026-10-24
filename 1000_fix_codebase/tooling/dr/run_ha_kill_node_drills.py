#!/usr/bin/env python3
"""run_ha_kill_node_drills.py — High Availability Kill-One-Node Survival Drills (TSS §21.3 / PE-001).

Covers the 4 Total-Outage Critical Components:
1. PostgreSQL 17 Primary: kill primary node -> standby promotes with zero data loss.
2. Keycloak 26: kill node 1 -> node 2 keeps session auth via Infinispan.
3. Kong Gateway: kill node 1 -> node 2 keeps reverse proxying API traffic.
4. Nginx Edge Ingress: kill node 1 -> node 2 keeps edge ingress routing.

GV-009: this runner never stops a container, so it never reports a failover
duration, drop rate or data-loss figure it did not observe.

Measured per component (read-only inspection of infra/compose/docker-compose.ha.yml):
both nodes declared with a healthcheck and a restart policy, plus the
component's own HA wiring (PostgreSQL standby replicates from the primary,
Keycloak nodes share the DB and the Infinispan cache, Kong's declarative
config and Nginx's routing config are mounted into every node).

UNMEASURED: each kill-one-node drill (needs the `ha` profile running and a
controlled node kill with traffic accounting).

Verdict: FAIL if any check failed, INCOMPLETE while any check is UNMEASURED,
PASS only when every check was measured and passed.
Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE.

Emits docs/traceability/evidence/r10-m04-ha-kill-node-evidence.json
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
HA_COMPOSE = "docker-compose.ha.yml"
EVIDENCE_FILE = "r10-m04-ha-kill-node-evidence.json"

PASS, FAIL, UNMEASURED, INCOMPLETE = "PASS", "FAIL", "UNMEASURED", "INCOMPLETE"
EXIT_CODES = {PASS: 0, FAIL: 1}
# PostgreSQL 17 server defaults for the settings inspected below.
PG_DEFAULTS = {"wal_level": "replica", "max_wal_senders": "10"}
RESTART_POLICIES = {"always", "unless-stopped", "on-failure"}
NO_KILL = (
    "requires the `ha` compose profile running and a controlled node kill with traffic "
    "accounting; this tool never stops a container"
)

# (key, component, drill id, node services: first node is the one the drill kills)
COMPONENTS = (
    (
        "postgresql",
        "PostgreSQL 17 Primary / Standby Pair",
        "KILL_PRIMARY_POSTGRES",
        ("postgres-ha-primary", "postgres-ha-standby"),
    ),
    (
        "keycloak",
        "Keycloak 26 Clustered Pair",
        "KILL_KEYCLOAK_NODE_1",
        ("keycloak-ha-01", "keycloak-ha-02"),
    ),
    (
        "kong",
        "Kong API Gateway Clustered Pair",
        "KILL_KONG_GATEWAY_NODE_1",
        ("kong-ha-01", "kong-ha-02"),
    ),
    (
        "nginx",
        "Nginx Edge Ingress Dual-Node Pair",
        "KILL_NGINX_INGRESS_NODE_1",
        ("nginx-ha-01", "nginx-ha-02"),
    ),
)


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


def _load_services(problems: list[str]) -> dict:
    path = COMPOSE_DIR / HA_COMPOSE
    if not path.is_file():
        problems.append(f"{HA_COMPOSE} not found")
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        problems.append(f"{HA_COMPOSE} unreadable: {exc}")
        return {}
    services = data.get("services") if isinstance(data, dict) else None
    if not isinstance(services, dict) or not services:
        problems.append(f"{HA_COMPOSE} declares no services")
        return {}
    return services


def _command(service: dict) -> list[str]:
    command = service.get("command") or []
    return command.split() if isinstance(command, str) else [str(t) for t in command]


def _pg_settings(service: dict) -> dict[str, str]:
    """PostgreSQL settings passed as `-c key=value` on a compose command."""
    tokens = _command(service)
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


def _volume_targets(service: dict) -> list[str]:
    targets = []
    for volume in service.get("volumes") or []:
        if isinstance(volume, dict):
            targets.append(str(volume.get("target", "")))
        else:
            parts = str(volume).split(":")
            targets.append(parts[1] if len(parts) > 1 else parts[0])
    return [t for t in targets if t]


# --------------------------------------------------------------------------- per-component wiring
def _postgres_problems(primary: dict, standby: dict) -> list[str]:
    problems = []
    p = _pg_settings(primary)
    if p["wal_level"] not in ("replica", "logical"):
        problems.append(f"primary wal_level={p['wal_level']} cannot stream")
    if not p["max_wal_senders"].isdigit() or int(p["max_wal_senders"]) < 1:
        problems.append(f"primary max_wal_senders={p['max_wal_senders']}")
    if not _pg_settings(standby).get("primary_conninfo"):
        problems.append("standby has no primary_conninfo - it does not replicate from the primary")
    definition = json.dumps(standby, default=str)
    if "standby.signal" not in definition and "pg_basebackup" not in definition:
        problems.append(
            "standby declares no bootstrap (pg_basebackup -R / standby.signal) - it starts as an "
            "independent empty primary, so there is nothing to promote"
        )
    return problems


def _keycloak_problems(nodes: dict[str, dict]) -> list[str]:
    problems = []
    for name, svc in nodes.items():
        if "--cache=ispn" not in _command(svc) and _env(svc).get("KC_CACHE") != "ispn":
            problems.append(f"{name} does not run the Infinispan (ispn) distributed cache")
    db_hosts = {
        _env(svc).get("KC_DB_URL_HOST") or _env(svc).get("KC_DB_URL") for svc in nodes.values()
    }
    if len(db_hosts) != 1 or None in db_hosts:
        problems.append("Keycloak nodes do not share one database")
    return problems


def _kong_problems(nodes: dict[str, dict]) -> list[str]:
    problems = []
    for name, svc in nodes.items():
        env = _env(svc)
        config = env.get("KONG_DECLARATIVE_CONFIG")
        if env.get("KONG_DATABASE") == "off" and not config:
            problems.append(f"{name} is DB-less with no KONG_DECLARATIVE_CONFIG")
        targets = _volume_targets(svc)
        if config and not any(
            config == t or config.startswith(t.rstrip("/") + "/") for t in targets
        ):
            problems.append(
                f"{name}: KONG_DECLARATIVE_CONFIG {config} is not mounted into the container"
            )
    return problems


def _nginx_problems(nodes: dict[str, dict]) -> list[str]:
    return [
        f"{name} mounts no routing config under /etc/nginx (serves the image default page)"
        for name, svc in nodes.items()
        if not any(t.startswith("/etc/nginx") for t in _volume_targets(svc))
    ]


def check_component_config(key: str, component: str, node_names: tuple[str, ...]) -> dict:
    problems: list[str] = []
    services = _load_services(problems)
    nodes: dict[str, dict] = {}
    for node in node_names:
        svc = services.get(node)
        if not isinstance(svc, dict):
            if services:
                problems.append(f"{node} not declared in {HA_COMPOSE}")
            continue
        nodes[node] = svc
        healthcheck = svc.get("healthcheck")
        if not (isinstance(healthcheck, dict) and healthcheck.get("test")):
            problems.append(f"{node} has no healthcheck")
        restart = str(svc.get("restart", "no"))
        if restart.split(":")[0] not in RESTART_POLICIES:
            problems.append(f"{node} restart policy {restart!r} never restarts a killed node")
    if len(nodes) == len(node_names):
        if key == "postgresql":
            problems += _postgres_problems(*nodes.values())
        elif key == "keycloak":
            problems += _keycloak_problems(nodes)
        elif key == "kong":
            problems += _kong_problems(nodes)
        elif key == "nginx":
            problems += _nginx_problems(nodes)
    return _result(
        f"{key}_ha_config",
        f"{component}: HA pair wiring declared",
        problems,
        [],
        f"{' + '.join(node_names)} declared with healthchecks, restart policy and HA wiring",
    )


def run_drill(key: str, component: str, drill: str, node_names: tuple[str, ...]) -> dict:
    config = check_component_config(key, component, node_names)
    kill = _result(f"{key}_kill_drill", f"{component}: {drill}", [], [NO_KILL], "")
    return {
        "component": component,
        "drill": drill,
        "nodes": list(node_names),
        "node_killed": None,
        "config_check": config,
        "kill_drill": kill,
        "status": overall_verdict([config, kill]),
        "details": f"config {config['status']}: {config['detail']} | kill drill {kill['status']}",
    }


def run_all_ha_drills() -> dict:
    drills = [run_drill(*component) for component in COMPONENTS]
    checks = [c for d in drills for c in (d["config_check"], d["kill_drill"])]
    verdict = overall_verdict(checks)
    return {
        "suite": "R10-M04-T06: High Availability Kill-One-Node Survival Drills",
        "standard": "PE-001 / TSS §21.3 Total-Outage HA Invariant",
        "timestamp": datetime.now(UTC).isoformat(),
        "total_drills": len(drills),
        "drills": drills,
        "summary": _summary(checks),
        "all_passed": verdict == PASS,
        "total_outage_tolerated": None,
        "status": verdict,
    }


def main() -> int:
    print("=" * 80)
    print("1000FiX — High Availability Kill-One-Node Survival Drills (R10-M04-T06)")
    print("=" * 80)
    results = run_all_ha_drills()
    for d in results["drills"]:
        print(f"[{d['status']}] {d['component']:<38} -> {d['details']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    out_file.write_bytes((json.dumps(results, indent=2) + "\n").encode("utf-8"))

    summary = results["summary"]
    print("-" * 80)
    print(
        f"HA Drills Outcome: {results['status']} ({summary['checks_passed']} passed, "
        f"{summary['checks_failed']} failed, {summary['checks_unmeasured']} UNMEASURED)"
    )
    print(f"Evidence written to: {out_file}")
    print("=" * 80)
    return EXIT_CODES.get(results["status"], 2)


if __name__ == "__main__":
    sys.exit(main())
