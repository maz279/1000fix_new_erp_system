#!/usr/bin/env python3
"""
run_journey_hardening_pass.py — Milestone R09-M04 Task T01.
Steady-state performance hardening pass: 1.5x peak across all 15 critical business journeys.
Evaluates against PE-004 / NFR-081 / NFR-092 latency budgets:
- Transactional journeys (J01-J10, J12): p95 <= 200 ms
- Reporting / Analytical / Batch journeys (J11, J13-J15): p95 <= 500 ms
- Error rate: 0.0%

GV-009: every latency, count and status written here is measured in the run.

What this measure-only tool does:
- A baseline probe of the Odoo JSON-RPC kernel: a handful (PROBE_SAMPLES) of
  sequential, read-only `common.version` calls, with their real latency and errors.
  It is a reachability/unloaded-latency baseline, NOT a journey measurement.
- Every journey's 1.5x-peak p95 check is UNMEASURED: no journey driver exists, and
  the journeys are multi-step, state-changing flows (bookings, claims, payroll,
  VAT returns) that need a perf environment with synthetic data and a load
  harness. The previous version timed GET /web/login for every journey, capped
  each sample at 48.5 ms, substituted a sleep for failed requests and reported
  the result as each journey's p95 with ">= 75 % headroom".

Overall status: FAIL if a check failed, INCOMPLETE while any check is UNMEASURED,
PASS only when every check passed. Exit code 0 PASS, 1 FAIL, 2 INCOMPLETE.

Outputs structured evidence to:
  docs/traceability/evidence/r09-m04-hardening-evidence.json
"""

from __future__ import annotations

import json
import logging
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
EVIDENCE_DIR = ROOT_DIR / "docs" / "traceability" / "evidence"
EVIDENCE_FILE = "r09-m04-hardening-evidence.json"

PASSED = "PASS"
FAILED = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

BASE_URL = os.environ.get("FIX_PERF_BASE_URL", "http://127.0.0.1:8069")
PROBE_SAMPLES = 5
PROBE_TIMEOUT_S = 5.0


JOURNEY_SPECIFICATIONS = [
    {
        "id": "J01",
        "name": "Customer Books On-Site Repair",
        "domain": "a_service_ops",
        "type": "transactional",
        "modules": ["cd_service_order", "cd_field_service", "cd_p03_portal"],
        "target_rps_1_5x": 350.0,
        "p95_budget_ms": 200.0,
    },
    {
        "id": "J02",
        "name": "Walk-In Counter Intake & Bench Repair Diagnostics",
        "domain": "a_service_ops",
        "type": "transactional",
        "modules": ["cd_front_desk", "cd_workshop", "cd_service_order"],
        "target_rps_1_5x": 420.0,
        "p95_budget_ms": 200.0,
    },
    {
        "id": "J03",
        "name": "Pick & Drop Round-Trip Logistics & Van Tracking",
        "domain": "a_service_ops",
        "type": "transactional",
        "modules": ["cd_service_order", "cd_facility", "cd_vehicle_ext"],
        "target_rps_1_5x": 280.0,
        "p95_budget_ms": 200.0,
    },
    {
        "id": "J04",
        "name": "Brand Warranty Claim Submission & Ledger Reimbursement",
        "domain": "c_commercial",
        "type": "transactional",
        "modules": ["cd_warranty_claims", "cd_billing_engine", "cd_partner"],
        "target_rps_1_5x": 310.0,
        "p95_budget_ms": 200.0,
    },
    {
        "id": "J05",
        "name": "Corporate AMC Preventive Maintenance Dispatch",
        "domain": "c_commercial",
        "type": "transactional",
        "modules": ["cd_contract_core", "cd_ppm", "cd_corporate_portal"],
        "target_rps_1_5x": 250.0,
        "p95_budget_ms": 200.0,
    },
    {
        "id": "J06",
        "name": "MSP Telemetry Ingestion & Auto Parts Replenishment",
        "domain": "e_supply_chain",
        "type": "transactional",
        "modules": ["cd_stream_registry", "cd_inventory", "cd_msp_contract"],
        "target_rps_1_5x": 833.0,
        "p95_budget_ms": 200.0,
    },
    {
        "id": "J07",
        "name": "Device Trade-In Appraisal & Refurbishment Grading",
        "domain": "d_circular",
        "type": "transactional",
        "modules": ["cd_tradein", "cd_workshop", "cd_dynamic_pricing"],
        "target_rps_1_5x": 220.0,
        "p95_budget_ms": 200.0,
    },
    {
        "id": "J08",
        "name": "Marketplace Seller Order Fulfillment & 48h Settlement",
        "domain": "c_commercial",
        "type": "transactional",
        "modules": ["cd_marketplace", "cd_settlement_ext", "cd_storefront"],
        "target_rps_1_5x": 480.0,
        "p95_budget_ms": 200.0,
    },
    {
        "id": "J09",
        "name": "Cleanroom Data Recovery Intake & Forensics Chain of Custody",
        "domain": "k_digital_channel",
        "type": "transactional",
        "modules": ["cd_data_case", "cd_service_order", "cd_qms_process"],
        "target_rps_1_5x": 150.0,
        "p95_budget_ms": 200.0,
    },
    {
        "id": "J10",
        "name": "E-Waste Circular Decommissioning & Wipe Certificate",
        "domain": "d_circular",
        "type": "transactional",
        "modules": ["cd_ewaste", "cd_document_core", "cd_esignature"],
        "target_rps_1_5x": 180.0,
        "p95_budget_ms": 200.0,
    },
    {
        "id": "J11",
        "name": "Analytical Warehouse Sync & BI KPI Aggregations",
        "domain": "j_data_analytics",
        "type": "reporting",
        "modules": ["cd_metric_registry", "bi-warehouse"],
        "target_rps_1_5x": 200.0,
        "p95_budget_ms": 500.0,
    },
    {
        "id": "J12",
        "name": "Three-Way Match Procurement, GRN & AP Settlement",
        "domain": "g_finance",
        "type": "transactional",
        "modules": ["cd_requisition", "cd_import_order", "cd_ap_ext"],
        "target_rps_1_5x": 240.0,
        "p95_budget_ms": 200.0,
    },
    {
        "id": "J13",
        "name": "Monthly Payroll Processing & BEFTN Bank Disbursement",
        "domain": "h_people",
        "type": "batch",
        "modules": ["cd_payroll_bd", "cd_attendance", "cd_cash_position"],
        "target_rps_1_5x": 160.0,
        "p95_budget_ms": 500.0,
    },
    {
        "id": "J14",
        "name": "ISO 9001 QMS Audit Inspection & CAPA Remediation Cycle",
        "domain": "i_governance",
        "type": "batch",
        "modules": ["cd_qms_process", "cd_grc", "cd_hse"],
        "target_rps_1_5x": 120.0,
        "p95_budget_ms": 500.0,
    },
    {
        "id": "J15",
        "name": "Month-Close Financial Reconciliation & Mushak 6.3 VAT Return",
        "domain": "g_finance",
        "type": "batch",
        "modules": ["cd_gl_ext", "cd_tax_engine_bd", "cd_fpa"],
        "target_rps_1_5x": 140.0,
        "p95_budget_ms": 500.0,
    },
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
        headers={"Content-Type": "application/json", "User-Agent": "1000FiX-HardeningProbe/2.0"},
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


def run_hardening_pass(
    base_url: str = BASE_URL,
    fetch: Callable[[], None] | None = None,
    reach: Callable[[str, int], tuple[bool, str]] = tcp_reachable,
    samples: int = PROBE_SAMPLES,
    write_evidence: bool = True,
) -> dict[str, Any]:
    logger.info("Steady-state hardening pass (J01-J15) - measure-only baseline probe...")
    checks: list[dict[str, Any]] = []
    parsed = urllib.parse.urlparse(base_url)
    reachable, reach_detail = reach(parsed.hostname or "127.0.0.1", parsed.port or 80)
    probe: dict[str, Any] | None = None
    if reachable:
        probe = measure_probe(fetch or (lambda: jsonrpc_version_call(base_url)), samples)
        checks.append(
            {
                "check": "odoo_baseline_probe_error_free",
                "status": PASSED if probe["errors"] == 0 else FAILED,
                "detail": f"{probe['successes']}/{samples} read-only common.version calls succeeded "
                f"(unloaded p95 {probe['latency_ms']['p95']} ms); errors {probe['error_samples'] or 'none'}",
            }
        )
    else:
        checks.append(
            {
                "check": "odoo_baseline_probe_error_free",
                "status": UNMEASURED,
                "detail": f"Odoo not reachable at {base_url} ({reach_detail})",
            }
        )

    journeys = []
    for j in JOURNEY_SPECIFICATIONS:
        reason = (
            f"no driver exists for this {j['type']} journey (modules {', '.join(j['modules'])}); "
            f"measuring p95 <= {j['p95_budget_ms']} ms at {j['target_rps_1_5x']} req/s needs a perf "
            "environment with synthetic data and a load harness, and this tool sends no load"
        )
        checks.append(
            {"check": f"{j['id']}::p95_at_1_5x_peak", "status": UNMEASURED, "detail": reason}
        )
        journeys.append(
            {
                "journey_id": j["id"],
                "name": j["name"],
                "domain": j["domain"],
                "type": j["type"],
                "modules": j["modules"],
                "target_rps_1_5x": j["target_rps_1_5x"],
                "p95_budget_ms": j["p95_budget_ms"],
                "status": UNMEASURED,
                "reason": reason,
            }
        )
        logger.info("[%s] %s (%s)", UNMEASURED, j["id"], j["name"])

    status = overall_status(checks)
    evidence = {
        "milestone": "R09-M04",
        "task": "R09-M04-T01",
        "standard": "DoD-14 / PE-004 / NFR-081 / NFR-092 (1.5x Peak Steady-State Hardening)",
        "timestamp": datetime.now(UTC).isoformat(),
        "journeys_declared": len(journeys),
        "journeys_measured": sum(1 for j in journeys if j["status"] != UNMEASURED),
        "baseline_probe_target": f"{base_url}/jsonrpc common.version (read-only)",
        "odoo_reachable": reachable,
        "baseline_probe": probe,
        "journeys": journeys,
        "checks": checks,
        "status": status,
    }

    if write_evidence:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        out_file = EVIDENCE_DIR / EVIDENCE_FILE
        out_file.write_bytes((json.dumps(evidence, indent=2) + "\n").encode("utf-8"))
        logger.info("Hardening pass evidence written to %s (status %s)", out_file, status)
    return evidence


if __name__ == "__main__":
    sys.exit(exit_code_for(run_hardening_pass()["status"]))
