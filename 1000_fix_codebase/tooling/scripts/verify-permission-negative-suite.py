#!/usr/bin/env python3
"""
verify-permission-negative-suite.py — Milestone R02-M02 Permission Negative Suite Verifier
Evidence producer for G1a-5 (DoD-07): 53 roles × 6 isolation tiers × 61 SoD controls.

Validates:
1. 53 reconciled roles (R-01..R-53) exist in the live dev database.
2. 6 data isolation tiers (T0..T5) exist in the live dev database.
3. 61 segregation-of-duties controls (SOD-01..SOD-61) from SP-006 exist.
4. The test_permissions_negative.py suite runs green (counts read from its JUnit report).
5. The T5 tier carries requires_step_up and requires_audit.
6. The R08-M04 cross-tenant negative suite runs green (counts read from its JUnit report).
Emits machine-readable evidence to tooling/fitness/evidence/permission-negative-suite-latest.json.

GV-009: every check is measured in this run. The database is read with
SELECTs inside a read-only transaction (PGOPTIONS default_transaction_read_only);
an unreachable database or a suite that collected/ran nothing is UNMEASURED,
never PASS. Overall verdict: FAIL if any check failed, INCOMPLETE if any is
UNMEASURED, PASS only when every check passed. Exit 0 PASS / 1 FAIL / 2 INCOMPLETE.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
EVIDENCE_FILE = (
    ROOT_DIR / "tooling" / "fitness" / "evidence" / "permission-negative-suite-latest.json"
)

PG_CONTAINER = os.environ.get("FIX_PG_CONTAINER", "compose-postgres-1")
PG_USER = os.environ.get("FIX_PG_USER", "fix")
PG_DB = os.environ.get("FIX_PG_DB", "fix_dev")

PERMISSION_SUITE = "addons/platform/cd_rbac_ext/tests/test_permissions_negative.py"
TENANT_SUITE = "addons/domain/d_circular/cd_marketplace/tests/test_tenant_isolation_negative.py"

EXPECTED_ROLES = [f"R-{i:02d}" for i in range(1, 54)]
EXPECTED_TIERS = ["T0", "T1", "T2", "T3", "T4", "T5"]
EXPECTED_SOD_CONTROLS = [f"SOD-{i:02d}" for i in range(1, 62)]

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
TRUE_FLAGS = ("t", "true", "1")


class InfraUnavailable(RuntimeError):
    """The database could not be queried - the check measured nothing."""


def run_psql_query(query: str) -> str:
    """One read-only SELECT through the dev Postgres container."""
    cmd = [
        "docker",
        "exec",
        "-e",
        "PGOPTIONS=-c default_transaction_read_only=on",
        "-i",
        PG_CONTAINER,
        "psql",
        "-U",
        PG_USER,
        "-d",
        PG_DB,
        "-v",
        "ON_ERROR_STOP=1",
        "-P",
        "pager=off",
        "-t",
        "-A",
        "-c",
        query,
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise InfraUnavailable(f"docker/psql not runnable: {exc}") from exc
    if res.returncode != 0:
        raise InfraUnavailable(f"psql exit {res.returncode}: {res.stderr.strip()[:300]}")
    return res.stdout.strip()


def run_pytest(target: str, timeout: int = 900) -> dict[str, Any]:
    """Run one pytest target and read its counts from the JUnit XML it writes.

    PASS needs exit 0 with >= 1 test passed and 0 failed/errored; a run that
    collected nothing or skipped everything is UNMEASURED; otherwise FAIL."""
    with tempfile.TemporaryDirectory() as tmp:
        junit = Path(tmp) / "junit.xml"
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            target,
            "-p",
            "no:cacheprovider",
            "-W",
            "ignore",
            f"--junitxml={junit}",
        ]
        started = time.perf_counter()
        try:
            proc = subprocess.run(
                cmd, cwd=str(ROOT_DIR), capture_output=True, text=True, timeout=timeout, check=False
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"status": UNMEASURED, "reason": f"pytest not runnable: {exc}"}
        duration = round(time.perf_counter() - started, 2)
        counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
        if junit.is_file():
            root = ET.parse(junit).getroot()  # noqa: S314 - the JUnit file pytest just wrote
            for suite in [root] if root.tag == "testsuite" else root.iter("testsuite"):
                for key in counts:
                    counts[key] += int(suite.get(key, "0") or 0)
    passed = counts["tests"] - counts["failures"] - counts["errors"] - counts["skipped"]
    result: dict[str, Any] = {
        "target": target,
        "exit_code": proc.returncode,
        "tests_run": counts["tests"],
        "tests_passed": passed,
        "tests_failed": counts["failures"],
        "tests_errored": counts["errors"],
        "tests_skipped": counts["skipped"],
        "duration_seconds": duration,
    }
    if proc.returncode == 0 and passed > 0 and not counts["failures"] and not counts["errors"]:
        result["status"] = PASS
    elif proc.returncode in (0, 5) and not counts["failures"] and not counts["errors"]:
        result["status"] = UNMEASURED
        result["reason"] = "suite collected or ran no test (all skipped / none collected)"
    else:
        result["status"] = FAIL
        result["output_tail"] = (proc.stdout + proc.stderr)[-800:]
    return result


def check_code_set(query: str, expected: list[str], query_fn=run_psql_query) -> dict[str, Any]:
    """Live codes vs the expected register: PASS iff exactly the expected set."""
    try:
        rows = query_fn(query)
    except InfraUnavailable as exc:
        return {"status": UNMEASURED, "reason": str(exc), "expected_count": len(expected)}
    raw = [r.strip() for r in rows.splitlines() if r.strip()]
    live = sorted(set(raw))
    missing = [c for c in expected if c not in live]
    unexpected = [c for c in live if c not in expected]
    duplicates = sorted({c for c in raw if raw.count(c) > 1})
    ok = not missing and not unexpected and not duplicates
    out: dict[str, Any] = {
        "status": PASS if ok else FAIL,
        "expected_count": len(expected),
        "actual_count": len(raw),
        "missing": missing,
    }
    if unexpected:
        out["unexpected"] = unexpected
    if duplicates:
        out["duplicates"] = duplicates
    return out


def check_t5_invariants(query_fn=run_psql_query) -> dict[str, Any]:
    try:
        row = query_fn(
            "SELECT requires_step_up, requires_audit FROM fix_isolation_tier WHERE code = 'T5';"
        )
    except InfraUnavailable as exc:
        return {"status": UNMEASURED, "reason": str(exc)}
    parts = [x.strip().lower() for x in row.split("|")] if row else []
    if len(parts) != 2:
        return {"status": FAIL, "reason": f"T5 tier row not found or malformed: {row!r}"}
    step_up, audit = (p in TRUE_FLAGS for p in parts)
    return {
        "status": PASS if step_up and audit else FAIL,
        "requires_step_up": step_up,
        "requires_audit": audit,
    }


def derive_verdict(statuses: list[str]) -> str:
    if not statuses:
        return "INCOMPLETE"
    if FAIL in statuses:
        return FAIL
    if any(s != PASS for s in statuses):
        return "INCOMPLETE"
    return PASS


def exit_code_for(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def build_evidence(query_fn=run_psql_query, pytest_fn=run_pytest) -> dict[str, Any]:
    started = time.perf_counter()
    results: dict[str, Any] = {}

    print("\n[Check 1/6] Live database: 53 reconciled roles (R-01..R-53)...")
    results["roles"] = check_code_set(
        "SELECT code FROM fix_role WHERE code ~ '^R-(0[1-9]|[1-4][0-9]|5[0-3])$' ORDER BY code;",
        EXPECTED_ROLES,
        query_fn,
    )

    print("[Check 2/6] Live database: 6 isolation tiers (T0..T5)...")
    tiers = check_code_set(
        "SELECT code FROM fix_isolation_tier ORDER BY code;", EXPECTED_TIERS, query_fn
    )
    results["isolation_tiers"] = tiers

    print("[Check 3/6] Live database: 61 SoD controls (SOD-01..SOD-61)...")
    results["sod_controls"] = check_code_set(
        "SELECT code FROM fix_sod_control WHERE code LIKE 'SOD-%' ORDER BY code;",
        EXPECTED_SOD_CONTROLS,
        query_fn,
    )

    print(f"[Check 4/6] Running {PERMISSION_SUITE} ...")
    results["test_suite"] = pytest_fn(PERMISSION_SUITE)

    print("[Check 5/6] Live database: T5 step-up + audit flags...")
    results["t5_invariants"] = check_t5_invariants(query_fn)

    print(f"[Check 6/6] Running {TENANT_SUITE} (R08-M04) ...")
    tenant = pytest_fn(TENANT_SUITE)
    tenant["milestone"] = "R08-M04"
    results["tenant_isolation"] = tenant

    for name, res in results.items():
        if res.get("reason"):
            detail = res["reason"]
        elif "tests_run" in res:
            detail = f"{res['tests_passed']}/{res['tests_run']} tests passed"
        elif "requires_step_up" in res:
            detail = f"requires_step_up={res['requires_step_up']}, requires_audit={res['requires_audit']}"
        else:
            detail = f"{res.get('actual_count')} found / {res.get('expected_count')} expected"
        print(f"  [{res['status']}] {name}: {detail}")

    statuses = [r["status"] for r in results.values()]
    verdict = derive_verdict(statuses)
    return {
        "timestamp": datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
        "milestone": "R02-M02",
        "description": "Permission negative tests: 53 roles × 6 isolation tiers × 61 SoD controls",
        "governance_rule": "DoD-07",
        "gate_criterion": "G1a-5",
        "database": {"container": PG_CONTAINER, "db": PG_DB, "access": "read-only SELECT"},
        "results": results,
        "checks_total": len(statuses),
        "checks_passed": statuses.count(PASS),
        "checks_failed": statuses.count(FAIL),
        "checks_unmeasured": statuses.count(UNMEASURED),
        "duration_seconds": round(time.perf_counter() - started, 2),
        "overall_verdict": verdict,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):  # a cp1252 console must not crash the run
        sys.stdout.reconfigure(errors="replace")
    print("===============================================================================")
    print("Milestone R02-M02: Permission Negative Suite (53 Roles × 6 Tiers × 61 SoD)")
    print("===============================================================================")
    evidence = build_evidence()
    EVIDENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_FILE.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"\n[Evidence] Saved evidence to: {EVIDENCE_FILE}")
    print(
        f"\nSummary: {evidence['checks_passed']}/{evidence['checks_total']} checks passed, "
        f"{evidence['checks_failed']} failed, {evidence['checks_unmeasured']} unmeasured "
        f"in {evidence['duration_seconds']}s -> {evidence['overall_verdict']}"
    )
    return exit_code_for(evidence["overall_verdict"])


if __name__ == "__main__":
    sys.exit(main())
