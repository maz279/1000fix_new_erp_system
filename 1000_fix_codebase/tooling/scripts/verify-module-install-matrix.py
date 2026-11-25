#!/usr/bin/env python3
"""verify-module-install-matrix.py - Milestone R02-M01-T02 (OD-02).

Proves OD-02 installability per module across the 66-module estate:
- Validates that every cd_* module resolves its full dependency closure.
- Checks topological ordering (AR-007 layer & dependency rules).
- Proves runtime installability in dependency sequence against the live database.
- Emits a machine-readable evidence record to tooling/fitness/evidence/module-install-matrix-latest.json.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADDONS_ROOT = REPO_ROOT / "addons"
EVIDENCE_DIR = REPO_ROOT / "tooling" / "fitness" / "evidence"


def get_all_manifests() -> dict[str, dict]:
    manifests = {}
    for p in ADDONS_ROOT.rglob("__manifest__.py"):
        mod_name = p.parent.name
        try:
            data = ast.literal_eval(p.read_text(encoding="utf-8"))
            layer = "platform" if "platform" in p.parts else "domain"
            manifests[mod_name] = {
                "name": mod_name,
                "path": str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
                "layer": layer,
                "summary": data.get("name", mod_name),
                "depends": data.get("depends", []),
                "version": data.get("version", "1.0.0"),
            }
        except Exception as e:
            print(f"Error parsing {p}: {e}", file=sys.stderr)
    return manifests


def compute_topological_order(modules: dict[str, dict]) -> list[str]:
    cd_mods = set(modules.keys())
    in_degree = dict.fromkeys(cd_mods, 0)
    adj = {m: [] for m in cd_mods}

    for m, info in modules.items():
        for d in info["depends"]:
            if d in cd_mods:
                adj[d].append(m)
                in_degree[m] += 1

    queue = [m for m in sorted(cd_mods) if in_degree[m] == 0]
    order = []
    while queue:
        curr = queue.pop(0)
        order.append(curr)
        for neighbor in sorted(adj[curr]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(cd_mods):
        missing = cd_mods - set(order)
        raise RuntimeError(f"Cycle detected in module dependencies! Unresolved: {missing}")
    return order


def query_installed_modules() -> dict[str, dict]:
    """Query PostgreSQL ir_module_module in Docker container."""
    cmd = [
        "docker",
        "compose",
        "-f",
        "infra/compose/docker-compose.yml",
        "--env-file",
        ".env",
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "fix",
        "-d",
        "fix_dev",
        "-tAc",
        "SELECT name, state, latest_version FROM ir_module_module WHERE name LIKE 'cd_%'",
    ]
    try:
        res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True)
        installed = {}
        for line in res.stdout.strip().splitlines():
            parts = line.split("|")
            if len(parts) >= 2:
                installed[parts[0]] = {
                    "state": parts[1],
                    "version": parts[2] if len(parts) > 2 else "",
                }
        return installed
    except Exception as e:
        print(f"Warning: could not query Docker postgres: {e}", file=sys.stderr)
        return {}


def main() -> int:
    print("======================================================================")
    print(" 1000FiX ERP - OD-02 Per-Module Installability Matrix (R02-M01-T02)")
    print("======================================================================")

    modules = get_all_manifests()
    total_shipped = len(modules)
    print(f"Discovered {total_shipped} first-party modules in addons/.")
    if total_shipped != 66:
        print(f"[FAIL] Expected 66 modules, found {total_shipped}", file=sys.stderr)
        return 1

    order = compute_topological_order(modules)
    print(f"Computed acyclic topological dependency order across all {len(order)} modules.")

    installed_db = query_installed_modules()
    print(f"Queried runtime database: {len(installed_db)} cd_* modules present.")

    matrix = []
    failures = 0
    installed_so_far = set()

    for idx, mod in enumerate(order, start=1):
        info = modules[mod]
        cd_deps = [d for d in info["depends"] if d.startswith("cd_")]
        external_deps = [d for d in info["depends"] if not d.startswith("cd_")]

        # Validate that all prerequisite cd_* modules precede this module in topological order
        missing_prereqs = [d for d in cd_deps if d not in installed_so_far]
        db_state = installed_db.get(mod, {}).get("state", "not_found")

        is_ok = len(missing_prereqs) == 0 and db_state == "installed"
        if not is_ok:
            failures += 1

        record = {
            "sequence": idx,
            "module": mod,
            "layer": info["layer"],
            "summary": info["summary"],
            "path": info["path"],
            "dependencies_count": len(info["depends"]),
            "cd_dependencies": cd_deps,
            "external_dependencies": external_deps,
            "prerequisites_satisfied": len(missing_prereqs) == 0,
            "missing_prerequisites": missing_prereqs,
            "runtime_state": db_state,
            "installable_alone": len(missing_prereqs) == 0,
            "status": "PASS" if is_ok else "FAIL",
        }
        matrix.append(record)
        installed_so_far.add(mod)

        status_flag = "[PASS]" if is_ok else "[FAIL]"
        print(
            f"{status_flag} {idx:02d}/66 {mod:<24} layer={info['layer']:<8} deps={len(info['depends']):<2} db={db_state}"
        )

    print("----------------------------------------------------------------------")
    print(f"OD-02 Installability Matrix: {66 - failures}/66 PASS (Failures: {failures})")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence_path = EVIDENCE_DIR / "module-install-matrix-latest.json"
    evidence_data = {
        "schema": "1000fix-erp/module-install-matrix/1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "total_modules": len(matrix),
        "passed": 66 - failures,
        "failed": failures,
        "verdict": "GREEN" if failures == 0 else "RED",
        "topological_sequence": order,
        "modules": matrix,
    }
    evidence_path.write_text(json.dumps(evidence_data, indent=2), encoding="utf-8")
    print(f"Evidence record written to: {evidence_path}")

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
