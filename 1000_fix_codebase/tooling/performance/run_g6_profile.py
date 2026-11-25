#!/usr/bin/env python3
"""
run_g6_profile.py — Gate G6 Performance Profile at 1.5x Peak (DoD-14 / PE-004)
Milestone R07-M05-T05 (DoD-14: Peak load capacity validation for New Asset Businesses).

GV-009: every latency, count and status written here is measured in the run.

What this measure-only tool does:
- Probes the Odoo JSON-RPC kernel with a handful (PROBE_SAMPLES) of sequential,
  read-only `common.version` calls and reports their real latency and errors
  (unloaded latency — not a load test). Failed requests are counted as errors,
  never timed as successes.
- Reports the PE-004 1.5x-peak check of every W6 workload as UNMEASURED: no load
  is generated (no load against the running dev Odoo; the perf environment is the
  right target), and the rental/trade-in, data-services, ML gateway, Kafka outbox
  and corporate SSO workloads have no probe endpoint here. The previous version
  timed GET /web/login for every workload, capped samples at 65 ms, multiplied
  the target rps by 1.05 as "achieved", and hard-coded a 52.4 % capacity margin
  and four conformance assertions.

Overall status: FAIL if a check failed, INCOMPLETE while any check is UNMEASURED,
PASS only when every check passed. Exit code 0 PASS, 1 FAIL, 2 INCOMPLETE.

Outputs structured evidence to:
  docs/traceability/evidence/g6-pe004-performance-evidence.json
"""

from __future__ import annotations

import json
import os
import socket
import sys
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
EVIDENCE_DIR = ROOT_DIR / "docs" / "traceability" / "evidence"
EVIDENCE_FILE = "g6-pe004-performance-evidence.json"

PASSED = "PASS"
FAILED = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

BASE_URL = os.environ.get("FIX_PERF_BASE_URL", "http://127.0.0.1:8069")
PROBE_SAMPLES = 5
PROBE_TIMEOUT_S = 5.0
P95_BUDGET_MS = 250.0  # PE-004 G6 threshold

# (workload, target rps at 1.5x peak, probe-able via the Odoo JSON-RPC kernel)
WORKLOADS = [
    ("Odoo JSON-RPC Kernel Operations", 45.0, True),
    ("Circular Asset Rental & Trade-in Engine", 35.0, False),
    ("Data Services Z4 Custody Sanitization", 25.0, False),
    ("ML Gateway Dispatch Scoring & Forecast", 60.0, False),
    ("Kafka EventBus High-Throughput Outbox", 80.0, False),
    ("Corporate Client SSO Federation (INT-046)", 30.0, False),
]


def tcp_reachable(host: str, port: int, timeout: float = 0.5) -> tuple[bool, str]:
    """Read-only reachability probe: open and close one TCP connection."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"{host}:{port} accepted a TCP connection"
    except OSError as exc:
        return False, f"{host}:{port} unreachable ({type(exc).__name__})"


def jsonrpc_version_call(base_url: str = BASE_URL, timeout: float = PROBE_TIMEOUT_S) -> None:
    """One read-only JSON-RPC call (common.version); raises on any transport/RPC error."""
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "call",
            "id": 1,
            "params": {"service": "common", "method": "version", "args": []},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/jsonrpc",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "1000FiX-G6-Probe/2.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        reply = json.loads(resp.read().decode("utf-8"))
    if "error" in reply or "result" not in reply:
        raise RuntimeError(f"JSON-RPC error: {str(reply.get('error'))[:200]}")


def _percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    return sorted_values[min(len(sorted_values) - 1, int(len(sorted_values) * q))]


def measure_probe(fetch: Callable[[], None], samples: int = PROBE_SAMPLES) -> dict[str, Any]:
    """Sequential probe: successes are timed; failures are counted as errors."""
    latencies: list[float] = []
    errors: list[str] = []
    for _ in range(samples):
        t0 = time.perf_counter()
        try:
            fetch()
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}"[:200])
            continue
        latencies.append((time.perf_counter() - t0) * 1000.0)
    latencies.sort()
    measured = {
        "p50": _percentile(latencies, 0.50),
        "p95": _percentile(latencies, 0.95),
        "max": latencies[-1] if latencies else None,
        "mean": sum(latencies) / len(latencies) if latencies else None,
    }
    return {
        "samples": samples,
        "successes": len(latencies),
        "errors": len(errors),
        "error_rate_pct": round(len(errors) * 100.0 / samples, 2) if samples else None,
        "error_samples": errors[:3],
        "latency_ms": {k: (round(v, 2) if v is not None else None) for k, v in measured.items()},
    }


def overall_status(checks: list[dict[str, Any]]) -> str:
    statuses = [c["status"] for c in checks]
    if FAILED in statuses:
        return FAILED
    if not statuses or UNMEASURED in statuses:
        return INCOMPLETE
    return PASSED


def exit_code_for(status: str) -> int:
    return {PASSED: 0, FAILED: 1}.get(status, 2)


def run_profile(
    base_url: str = BASE_URL,
    fetch: Callable[[], None] | None = None,
    reach: Callable[[str, int], tuple[bool, str]] = tcp_reachable,
    samples: int = PROBE_SAMPLES,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    parsed = urllib.parse.urlparse(base_url)
    reachable, reach_detail = reach(parsed.hostname or "127.0.0.1", parsed.port or 80)
    probe: dict[str, Any] | None = None
    if not reachable:
        reason = f"Odoo not reachable at {base_url} ({reach_detail})"
        checks.append(
            {"check": "odoo_jsonrpc_probe_error_free", "status": UNMEASURED, "detail": reason}
        )
        checks.append(
            {
                "check": "odoo_jsonrpc_unloaded_p95_within_budget",
                "status": UNMEASURED,
                "detail": reason,
            }
        )
    else:
        probe = measure_probe(fetch or (lambda: jsonrpc_version_call(base_url)), samples)
        checks.append(
            {
                "check": "odoo_jsonrpc_probe_error_free",
                "status": PASSED if probe["errors"] == 0 else FAILED,
                "detail": f"{probe['successes']}/{samples} read-only common.version calls succeeded; "
                f"errors {probe['error_samples'] or 'none'}",
            }
        )
        p95 = probe["latency_ms"]["p95"]
        checks.append(
            {
                "check": "odoo_jsonrpc_unloaded_p95_within_budget",
                "status": UNMEASURED
                if p95 is None
                else (PASSED if p95 <= P95_BUDGET_MS else FAILED),
                "detail": f"unloaded p95 {p95} ms vs budget {P95_BUDGET_MS} ms over {probe['successes']} timed calls"
                if p95 is not None
                else "no successful call to time",
            }
        )

    workloads = []
    for name, rps, probed in WORKLOADS:
        reason = (
            f"no load generated at {rps} req/s: this measure-only tool sends {samples} sequential "
            "read-only calls; the 1.5x-peak profile needs a load harness against the perf environment"
            if probed
            else "no endpoint for this workload is probed by this tool (the previous version timed "
            "GET /web/login under this workload's name)"
        )
        checks.append({"check": f"pe004_1_5x_peak::{name}", "status": UNMEASURED, "detail": reason})
        workloads.append(
            {"workload": name, "target_rps_1_5x_peak": rps, "status": UNMEASURED, "reason": reason}
        )

    return {
        "probe_target": f"{base_url}/jsonrpc common.version (read-only)",
        "odoo_reachable": reachable,
        "odoo_reachability_detail": reach_detail,
        "unloaded_probe": probe,
        "workloads": workloads,
        "checks": checks,
        "status": overall_status(checks),
    }


def main() -> int:
    start_time = time.time()
    print("Gate G6 PE-004 Profile (DoD-14) - measure-only probe...")
    res = run_profile()
    for c in res["checks"]:
        print(f"  [{c['status']}] {c['check']}: {c['detail']}")

    evidence = {
        "profile": "PE-004: Gate G6 1.5x Peak Load Profile & Asset Businesses Benchmark",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "duration_seconds": round(time.time() - start_time, 2),
        "overall_status": res["status"],
        "sla_threshold_p95_ms": P95_BUDGET_MS,
        "measurement": res,
    }
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    out_file.write_bytes((json.dumps(evidence, indent=2) + "\n").encode("utf-8"))
    print(f"\nGate G6 PE-004 evidence written -> {out_file} (overall_status {res['status']})")
    return exit_code_for(res["status"])


if __name__ == "__main__":
    sys.exit(main())
