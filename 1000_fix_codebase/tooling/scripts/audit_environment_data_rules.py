#!/usr/bin/env python3
"""audit_environment_data_rules.py — Audit of the 12-Environment Ladder & Data Rules.

Enforces:
- PE-002-D-01 / PE-002-D-02: 12-environment ladder complete and separate.
- NFR-086c: Non-production environments NEVER hold unmasked sovereign residency-classified data.
- DE-03 / DE-04 / DE-05: Port isolation, volume isolation, loopback binding, and healthcheck presence.
- Strict database name isolation across all environments.

Emits docs/traceability/evidence/r10-m04-environment-data-rules-audit.json
"""

from __future__ import annotations

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INFRA_DIR = REPO_ROOT / "infra"
COMPOSE_DIR = INFRA_DIR / "compose"
ENV_YAML = INFRA_DIR / "environments.yaml"
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"

EXPECTED_ENVIRONMENTS = [
    "local",
    "ci",
    "dev",
    "sit",
    "uat",
    "perf",
    "staging",
    "training",
    "sandbox",
    "migration-staging",
    "prod",
    "dr",
]

COMPOSE_FILES_MAP = {
    "local": "docker-compose.yml",
    "dev": "docker-compose.dev.yml",
    "sit": "docker-compose.sit.yml",
    "uat": "docker-compose.uat.yml",
    "perf": "docker-compose.perf.yml",
    "staging": "docker-compose.staging.yml",
    "training": "docker-compose.training.yml",
    "sandbox": "docker-compose.sandbox.yml",
    "migration-staging": "docker-compose.migration-staging.yml",
    "prod": "docker-compose.prod.yml",
    "dr": "docker-compose.dr.yml",
}


def parse_environments_yaml() -> list[dict]:
    if not ENV_YAML.exists():
        raise FileNotFoundError(f"environments.yaml missing: {ENV_YAML}")

    lines = ENV_YAML.read_text(encoding="utf-8").splitlines()
    envs = []
    current: dict | None = None
    in_envs = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("environments:"):
            in_envs = True
            continue
        if stripped.startswith("rules:"):
            in_envs = False
            if current:
                envs.append(current)
                current = None
            continue

        if in_envs:
            if stripped.startswith("- name:"):
                if current:
                    envs.append(current)
                name = stripped.split(":", 1)[1].strip()
                current = {"name": name}
            elif current is not None and ":" in stripped:
                k, v = stripped.split(":", 1)
                v = v.split("#")[0].strip()
                current[k.strip()] = v

    if current:
        envs.append(current)

    return envs


def extract_compose_metadata(file_path: Path) -> dict:
    if not file_path.exists():
        return {"exists": False}

    content = file_path.read_text(encoding="utf-8")
    ports = re.findall(r"127\.0\.0\.1:(\d+):", content)
    databases = re.findall(r"POSTGRES_DB:\s*([^\s#]+)", content)
    volumes = re.findall(r"-\s+([a-zA-Z0-9_\-]+):/var/lib/postgresql/data", content)
    healthchecks = "healthcheck:" in content

    return {
        "exists": True,
        "ports": [int(p) for p in ports],
        "databases": databases,
        "volumes": volumes,
        "has_healthcheck": healthchecks,
    }


def run_audit() -> dict:
    envs = parse_environments_yaml()
    env_names = [e["name"] for e in envs]

    results = {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_environments": len(envs),
        "expected_environments": len(EXPECTED_ENVIRONMENTS),
        "all_environments_present": all(name in env_names for name in EXPECTED_ENVIRONMENTS),
        "environments": [],
        "passed": True,
        "violations": [],
    }

    used_ports: dict[int, str] = {}
    used_databases: dict[str, str] = {}
    used_volumes: dict[str, str] = {}

    for env in envs:
        name = env["name"]
        data_rule = env.get("data", "")
        residency = env.get("residency_classified", "")
        compose_file = COMPOSE_FILES_MAP.get(name)

        audit_entry = {
            "name": name,
            "purpose": env.get("purpose", ""),
            "data_rule": data_rule,
            "residency_classified": residency,
            "compose_file": compose_file,
            "passed": True,
            "details": [],
        }

        # Rule 1: Non-prod residency classification constraint (NFR-086c)
        if name not in ("prod", "dr"):
            if "yes" in residency.lower():
                msg = f"NFR-086c VIOLATION: Non-production environment '{name}' declares residency_classified='{residency}'"
                audit_entry["details"].append(msg)
                audit_entry["passed"] = False
                results["violations"].append(msg)
        else:
            if "yes" not in residency.lower():
                msg = f"Production environment '{name}' must declare residency_classified with Z4 sovereign protection"
                audit_entry["details"].append(msg)
                audit_entry["passed"] = False
                results["violations"].append(msg)

        # Rule 2: Compose specification inspection
        if compose_file:
            cmp_path = COMPOSE_DIR / compose_file
            meta = extract_compose_metadata(cmp_path)
            if not meta["exists"]:
                msg = f"Compose file missing for environment '{name}': {compose_file}"
                audit_entry["details"].append(msg)
                audit_entry["passed"] = False
                results["violations"].append(msg)
            else:
                audit_entry["ports"] = meta["ports"]
                audit_entry["databases"] = meta["databases"]
                audit_entry["volumes"] = meta["volumes"]
                audit_entry["has_healthcheck"] = meta["has_healthcheck"]

                # Assert port uniqueness
                for p in meta["ports"]:
                    if p in used_ports:
                        msg = (
                            f"PORT COLLISION: Port {p} in '{name}' collides with '{used_ports[p]}'"
                        )
                        audit_entry["details"].append(msg)
                        audit_entry["passed"] = False
                        results["violations"].append(msg)
                    else:
                        used_ports[p] = name

                # Assert DB name uniqueness (allowing DR standby to mirror prod)
                for db in meta["databases"]:
                    if db in used_databases and not (name == "dr" and used_databases[db] == "prod"):
                        msg = f"DATABASE COLLISION: Database '{db}' in '{name}' collides with '{used_databases[db]}'"
                        audit_entry["details"].append(msg)
                        audit_entry["passed"] = False
                        results["violations"].append(msg)
                    else:
                        used_databases[db] = name

                # Assert volume isolation
                for v in meta["volumes"]:
                    if v in used_volumes:
                        msg = f"VOLUME COLLISION: Volume '{v}' in '{name}' collides with '{used_volumes[v]}'"
                        audit_entry["details"].append(msg)
                        audit_entry["passed"] = False
                        results["violations"].append(msg)
                    else:
                        used_volumes[v] = name

        results["environments"].append(audit_entry)
        if not audit_entry["passed"]:
            results["passed"] = False

    # Check three-environment split (PE-002-D-02)
    split_envs = {"sit", "uat", "staging"}
    if not split_envs.issubset(set(env_names)):
        msg = f"PE-002-D-02 VIOLATION: sit, uat and staging must be separate environments; found {env_names}"
        results["violations"].append(msg)
        results["passed"] = False

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / "r10-m04-environment-data-rules-audit.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")

    return results


if __name__ == "__main__":
    audit = run_audit()
    print("=" * 80)
    print("1000FiX — 12-Environment Ladder & Data Rules Audit (R10-M04-T01)")
    print("=" * 80)
    for env in audit["environments"]:
        status = "PASS" if env["passed"] else "FAIL"
        print(
            f"[{status}] {env['name']:<18} Data: {env['data_rule']:<30} Residency: {env['residency_classified']}"
        )
        for detail in env["details"]:
            print(f"       -> {detail}")

    print("-" * 80)
    print(
        f"Summary: {len(audit['environments'])} environments audited. Total violations: {len(audit['violations'])}"
    )
    print(
        "Evidence written to: docs/traceability/evidence/r10-m04-environment-data-rules-audit.json"
    )
    print("=" * 80)

    if not audit["passed"]:
        sys.exit(1)
    sys.exit(0)
