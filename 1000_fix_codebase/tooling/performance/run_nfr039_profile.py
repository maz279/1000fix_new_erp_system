#!/usr/bin/env python3
"""run_nfr039_profile.py — NFR-039 Warehouse Analytical Query Performance Benchmark.

Milestone R09-M01-T03:
Verifies NFR-039: Analytical warehouse query <= 10.0 s p95 at 1.5x peak query load.
Executes representative multi-dimensional analytical queries across ClickHouse
fact and dimension tables (fix_analytics) and computes percentile latency metrics.

GV-009: latencies and the status are measured against a LIVE ClickHouse only.
- The ClickHouse HTTP interface is probed read-only (GET /ping). When it is not
  reachable the benchmark is UNMEASURED: the previous version silently fell back
  to the embedded SQLite engine and reported SQLite timings as NFR-039 warehouse
  latency.
- The tool never writes to the warehouse: it no longer triggers a full warehouse
  sync when the fact tables are missing (that is reported as UNMEASURED).
- Only SELECT statements are executed (FORMAT JSON, so row counts are real).

Exit code: 0 PASS, 1 FAIL, 2 UNMEASURED.

Emits:
- docs/traceability/evidence/r09-m01-nfr039-performance-evidence.json
- docs/traceability/evidence/g8-pe004-performance-evidence.json
"""

from __future__ import annotations

import concurrent.futures
import datetime
import json
import logging
import statistics
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "services" / "bi-warehouse" / "src"
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"

sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(REPO_ROOT))

from clickhouse_client import ClickHouseClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("nfr039_profile")

PASSED = "PASS"
FAILED = "FAIL"
UNMEASURED = "UNMEASURED"

NFR039_P95_BUDGET_SECONDS = 10.0
PEAK_MULTIPLIER = 1.5
BASELINE_PEAK_CONCURRENCY = 10
TARGET_CONCURRENCY = int(BASELINE_PEAK_CONCURRENCY * PEAK_MULTIPLIER)  # 15 concurrent threads
TOTAL_QUERIES_TO_EXECUTE = 150
PRECHECK_SQL = "SELECT count() AS n FROM fact_service_orders"


ANALYTICAL_BENCHMARK_QUERIES = [
    (
        "Q1_BRANCH_CATEGORY_PERF",
        """
        SELECT
            b.division,
            so.order_category,
            count(*) as total_orders,
            round(avg(so.resolution_hours), 2) as avg_resolution_hours,
            round(sum(so.sla_met) * 100.0 / count(*), 2) as sla_compliance_pct,
            round(sum(so.revenue_bdt), 2) as total_revenue
        FROM fact_service_orders so
        JOIN dim_branch b ON so.branch_key = b.branch_key
        GROUP BY b.division, so.order_category
        ORDER BY total_orders DESC;
        """,
    ),
    (
        "Q2_MONTHLY_REVENUE_TREND",
        """
        SELECT
            d.year,
            d.quarter,
            d.month_name,
            count(*) as invoice_count,
            round(sum(inv.amount_untaxed), 2) as net_revenue,
            round(sum(inv.amount_tax), 2) as vat_collected,
            round(sum(inv.amount_total), 2) as gross_revenue
        FROM fact_invoices inv
        JOIN dim_date d ON inv.invoice_date = d.date_key
        GROUP BY d.year, d.quarter, d.month, d.month_name
        ORDER BY d.year, d.quarter, d.month;
        """,
    ),
    (
        "Q3_WARRANTY_LOSS_RATIO",
        """
        SELECT
            dev.brand,
            dev.category,
            count(*) as claim_count,
            sum(c.is_oem_reimbursed) as reimbursed_count,
            round(sum(c.covered_amount), 2) as total_covered_bdt
        FROM fact_warranty_claims c
        JOIN dim_device dev ON c.device_key = dev.device_key
        GROUP BY dev.brand, dev.category
        ORDER BY total_covered_bdt DESC;
        """,
    ),
    (
        "Q4_NPS_SENTIMENT_DISTRIBUTION",
        """
        SELECT
            b.name as branch_name,
            n.category as nps_tier,
            count(*) as response_count,
            round(avg(n.score), 2) as avg_nps_score
        FROM fact_nps n
        JOIN dim_branch b ON n.branch_key = b.branch_key
        GROUP BY b.name, n.category
        ORDER BY response_count DESC;
        """,
    ),
    (
        "Q5_TECHNICIAN_EFFICIENCY",
        """
        SELECT
            t.skill_tier,
            count(distinct so.order_key) as jobs_completed,
            round(avg(so.resolution_hours), 2) as avg_hours,
            round(sum(so.revenue_bdt), 2) as revenue_generated
        FROM fact_service_orders so
        JOIN dim_technician t ON so.technician_key = t.technician_key
        WHERE so.order_state = 'completed'
        GROUP BY t.skill_tier
        ORDER BY revenue_generated DESC;
        """,
    ),
]


def _as_json_select(sql: str) -> str:
    """Live ClickHouse returns parsed rows only for FORMAT JSON queries."""
    return sql.strip().rstrip(";").strip() + " FORMAT JSON"


def execute_single_query(ch: ClickHouseClient, query_tuple: tuple[str, str]) -> dict[str, Any]:
    name, sql = query_tuple
    t0 = time.perf_counter()
    success = False
    row_count = 0
    error_msg = None
    try:
        res = ch.execute(_as_json_select(sql))
        duration = time.perf_counter() - t0
        if isinstance(res, list):
            success = True
            row_count = len(res)
        else:
            error_msg = f"unexpected non-row result {res!r}"
    except Exception as e:
        duration = time.perf_counter() - t0
        error_msg = str(e)

    return {
        "query_name": name,
        "duration_sec": duration,
        "duration_ms": duration * 1000.0,
        "row_count": row_count,
        "success": success,
        "error": error_msg,
    }


def _write_evidence(report: dict[str, Any]) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    (EVIDENCE_DIR / "r09-m01-nfr039-performance-evidence.json").write_bytes(payload)
    # Gate G8 PE-004 evidence carries the same measured report.
    (EVIDENCE_DIR / "g8-pe004-performance-evidence.json").write_bytes(payload)


def _base_report(concurrency: int, total_queries: int) -> dict[str, Any]:
    return {
        "milestone": "R09-M01",
        "task": "R09-M01-T03",
        "standard": "NFR-039",
        "target_description": "Warehouse analytical query latency <= 10.0s p95 under 1.5x peak query load",
        "audit_timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "sla_budget_sec": NFR039_P95_BUDGET_SECONDS,
        "workload": {
            "baseline_concurrency": BASELINE_PEAK_CONCURRENCY,
            "peak_multiplier": PEAK_MULTIPLIER,
            "requested_concurrency": concurrency,
            "requested_queries": total_queries,
        },
    }


def run_nfr039_benchmark(
    concurrency: int = TARGET_CONCURRENCY,
    total_queries: int = TOTAL_QUERIES_TO_EXECUTE,
    ch: ClickHouseClient | None = None,
    write_evidence: bool = True,
) -> dict[str, Any]:
    """Runs a concurrent read-only load against a LIVE ClickHouse and computes percentiles."""
    logger.info(
        f"=== NFR-039 Benchmark at 1.5x Peak ({concurrency} workers, {total_queries} queries) ==="
    )
    ch = ch or ClickHouseClient(database="fix_analytics", use_fallback_if_unreachable=False)
    report = _base_report(concurrency, total_queries)
    report["engine"] = {"base_url": ch.base_url, "database": ch.database}

    def unmeasured(reason: str) -> dict[str, Any]:
        report.update({"sla_met": None, "status": UNMEASURED, "reason": reason})
        logger.info("NFR-039 UNMEASURED: %s", reason)
        if write_evidence:
            _write_evidence(report)
        return report

    if not ch.is_connected():
        return unmeasured(
            f"ClickHouse HTTP interface not reachable at {ch.base_url}/ping; the embedded SQLite "
            "fallback is not a measurement of the warehouse"
        )
    try:
        precheck = ch.execute(_as_json_select(PRECHECK_SQL))
    except Exception as exc:
        return unmeasured(
            f"warehouse precheck failed ({type(exc).__name__}: {exc}); populating the warehouse "
            "(warehouse_sync) is a write and is not run by this tool"
        )
    if not isinstance(precheck, list):
        return unmeasured(f"warehouse precheck returned no rows ({precheck!r})")
    report["engine"]["fact_service_orders_rows"] = (precheck[0] if precheck else {}).get("n")

    work_items = [
        ANALYTICAL_BENCHMARK_QUERIES[i % len(ANALYTICAL_BENCHMARK_QUERIES)]
        for i in range(total_queries)
    ]

    t_start = time.perf_counter()
    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(execute_single_query, ch, q) for q in work_items]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())
    total_wall_time = time.perf_counter() - t_start

    durations_sec = sorted(r["duration_sec"] for r in results)
    success_count = sum(1 for r in results if r["success"])
    error_count = len(results) - success_count

    def pct(values: list[float], q: float) -> float:
        return values[min(len(values) - 1, int(len(values) * q))]

    p95_sec = pct(durations_sec, 0.95)
    sla_met = (p95_sec <= NFR039_P95_BUDGET_SECONDS) and (error_count == 0)

    query_breakdown: dict[str, dict[str, Any]] = {}
    for q_name, _ in ANALYTICAL_BENCHMARK_QUERIES:
        q_durations = sorted(r["duration_ms"] for r in results if r["query_name"] == q_name)
        if q_durations:
            query_breakdown[q_name] = {
                "executions": len(q_durations),
                "errors": sum(1 for r in results if r["query_name"] == q_name and not r["success"]),
                "rows_last": next(
                    (r["row_count"] for r in results if r["query_name"] == q_name and r["success"]),
                    None,
                ),
                "p50_ms": round(statistics.median(q_durations), 2),
                "p95_ms": round(pct(q_durations, 0.95), 2),
                "max_ms": round(max(q_durations), 2),
            }

    report.update(
        {
            "workload_measured": {
                "actual_concurrency": concurrency,
                "total_queries_executed": len(results),
                "wall_clock_time_sec": round(total_wall_time, 2),
                "throughput_queries_per_sec": round(len(results) / total_wall_time, 2)
                if total_wall_time > 0
                else None,
            },
            "latencies_sec": {
                "p50": round(statistics.median(durations_sec), 4),
                "p90": round(pct(durations_sec, 0.90), 4),
                "p95": round(p95_sec, 4),
                "p99": round(pct(durations_sec, 0.99), 4),
                "min": round(durations_sec[0], 4),
                "max": round(durations_sec[-1], 4),
            },
            "error_count": error_count,
            "error_rate_pct": round(error_count * 100.0 / len(results), 2),
            "error_samples": [r["error"] for r in results if r["error"]][:3],
            "sla_met": sla_met,
            "status": PASSED if sla_met else FAILED,
            "query_breakdown": query_breakdown,
        }
    )
    if write_evidence:
        _write_evidence(report)
    logger.info(
        f"NFR-039 measured: p95={report['latencies_sec']['p95']}s (Budget: {NFR039_P95_BUDGET_SECONDS}s), "
        f"errors={error_count}, Status={report['status']}"
    )
    return report


def main() -> int:
    rep = run_nfr039_benchmark()
    return {PASSED: 0, FAILED: 1}.get(rep.get("status", ""), 2)


if __name__ == "__main__":
    sys.exit(main())
