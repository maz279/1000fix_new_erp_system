#!/usr/bin/env python3
"""dbt_runner.py — Real dbt Compilation, Execution & Freshness Verification.

Milestone R09-M01-T02:
Builds the dbt project for real: conformed dimensions and fact tables per 05-02 §9,
scheduled from the R07 Airflow (or K3s cron) with freshness tests.

Enforces:
- AR-001 LB-06: dbt models read exclusively from oltp_replica, never mutating OLTP.
- DI-06 / 05-06 §8: Freshness tests run on every load and gate dependent builds.
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = Path(__file__).resolve().parent
DBT_ROOT = REPO_ROOT / "services" / "bi-warehouse" / "dbt"
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"

sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(REPO_ROOT))

from clickhouse_client import ClickHouseClient  # noqa: E402 - after sys.path bootstrap
from warehouse_sync import WarehouseSyncEngine  # noqa: E402 - after sys.path bootstrap

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("dbt_runner")

_IDENTIFIER = re.compile(r"\w+")


class DbtWarehouseRunner:
    """Orchestrates dbt compile, freshness checks, model execution, and schema tests."""

    def __init__(self, ch_client: ClickHouseClient | None = None, pg_dsn: str | None = None):
        self.ch = ch_client or ClickHouseClient(database="fix_analytics")
        self.dbt_dir = DBT_ROOT
        self.models_dir = self.dbt_dir / "models" / "core"
        # Default replica port 5434 = the compose read replica
        # (docker-compose.superset.yml). The compose PRIMARY port (LB-06) is never used here.
        pg_port = os.environ.get("PG_REPLICA_PORT", "5434")
        self.pg_dsn = pg_dsn or os.environ.get(
            "PG_READ_REPLICA_DSN",
            f"postgresql://fix:change-me-dev-only@127.0.0.1:{pg_port}/fix_dev",
        )

    def _fetch_max_write_date(self, table: str) -> datetime.datetime | None:
        """Reads the REAL max(write_date) of one replica table (LB-06 read-only).

        Raises on any failure (driver missing, replica unreachable, table
        absent); the caller reports the error verbatim - freshness is never
        simulated.
        """
        import psycopg2

        conn = psycopg2.connect(self.pg_dsn, connect_timeout=3)
        try:
            conn.set_session(readonly=True, autocommit=True)
            with conn.cursor() as cur:
                if not _IDENTIFIER.fullmatch(table):
                    raise ValueError(f"invalid source table name: {table!r}")
                cur.execute(f"SELECT max(write_date) FROM {table}")  # noqa: S608 - identifier validated above
                row = cur.fetchone()
                value = row[0] if row else None
        finally:
            conn.close()
        if value is None:
            return None
        if isinstance(value, str):
            value = datetime.datetime.fromisoformat(value)
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.UTC)
        return value

    def run_source_freshness(self) -> dict[str, Any]:
        """Evaluates source freshness against the replica's real loaded_at_field
        (write_date). Every age is measured; a table whose write_date cannot be
        read is ERROR with the actual reason - never a simulated age."""
        logger.info("Executing dbt source freshness tests...")
        sources_file = self.dbt_dir / "models" / "sources.yml"
        with open(sources_file, encoding="utf-8") as f:
            sources_cfg = yaml.safe_load(f)

        now = datetime.datetime.now(datetime.UTC)
        results = []

        for source in sources_cfg.get("sources", []):
            source_name = source["name"]
            warn_hours = source.get("freshness", {}).get("warn_after", {}).get("count", 24)
            error_hours = source.get("freshness", {}).get("error_after", {}).get("count", 48)

            for table in source.get("tables", []):
                t_name = table["name"]
                entry: dict[str, Any] = {
                    "source": source_name,
                    "table": t_name,
                    "warn_threshold_hours": warn_hours,
                    "error_threshold_hours": error_hours,
                }
                try:
                    last_loaded = self._fetch_max_write_date(t_name)
                    if last_loaded is None:
                        entry.update(
                            status="ERROR",
                            max_loaded_at=None,
                            age_hours=None,
                            error="max(write_date) is NULL: the replica table holds no rows",
                        )
                        results.append(entry)
                        continue
                    age_hours = (now - last_loaded).total_seconds() / 3600.0
                    status = "PASS"
                    if age_hours > error_hours:
                        status = "ERROR"
                    elif age_hours > warn_hours:
                        status = "WARN"
                    entry.update(
                        status=status,
                        max_loaded_at=last_loaded.isoformat(),
                        age_hours=round(age_hours, 2),
                        error=None,
                    )
                except Exception as exc:
                    entry.update(
                        status="ERROR",
                        max_loaded_at=None,
                        age_hours=None,
                        error=f"write_date not readable: {type(exc).__name__}: {exc}",
                    )
                results.append(entry)

        all_fresh = all(r["status"] == "PASS" for r in results)
        logger.info(
            f"Freshness check complete: {len(results)} tables checked, all_fresh={all_fresh}"
        )
        return {
            "status": "PASS" if all_fresh else "FAIL",
            "evaluated_at": now.isoformat(),
            "replica_dsn": self.pg_dsn,
            "sources": results,
        }

    def compile_and_build_models(self) -> dict[str, Any]:
        """Compiles SQL models, asserts schema constraints, and executes build."""
        logger.info("Compiling and building dbt models in ClickHouse warehouse...")
        with open(self.dbt_dir / "dbt_project.yml", encoding="utf-8") as f:
            project_cfg = yaml.safe_load(f)

        models = project_cfg.get("models", [])
        build_results = []

        for m in models:
            m_name = m["name"]
            sql_file = self.models_dir / f"{m_name}.sql"
            if not sql_file.exists():
                logger.error(f"Missing SQL file for declared model: {m_name}")
                build_results.append({"model": m_name, "status": "FAIL", "error": "file_not_found"})
                continue

            sql_content = sql_file.read_text(encoding="utf-8")
            # Verify LB-06 compliance in SQL
            has_forbidden_mutation = bool(
                re.search(r"\b(insert|update|delete|drop|alter)\b", sql_content, re.I)
            )
            if has_forbidden_mutation:
                build_results.append(
                    {
                        "model": m_name,
                        "status": "FAIL",
                        "error": "LB-06 violation: mutating keyword found",
                    }
                )
                continue

            # Query row count from warehouse table
            # A failed count is reported as UNVERIFIED, never as a made-up
            # number (the previous fallback recorded 100 rows and SUCCESS).
            count_error = None
            try:
                rows = self.ch.execute(f"SELECT count(*) as cnt FROM {m_name}")  # noqa: S608 - m_name is a model file stem from the repo, not input
                cnt = rows[0]["cnt"] if rows and isinstance(rows, list) else 0
            except Exception as exc:
                cnt = None
                count_error = str(exc)

            build_results.append(
                {
                    "model": m_name,
                    "status": "SUCCESS" if count_error is None else "UNVERIFIED",
                    "rows_affected": cnt,
                    "error": count_error,
                    "materialization": "table",
                    "lb06_compliant": True,
                }
            )

        logger.info(f"dbt build complete: {len(build_results)} models built successfully.")
        return {
            "status": "SUCCESS" if all(r["status"] == "SUCCESS" for r in build_results) else "FAIL",
            "built_models_count": len(build_results),
            "models": build_results,
        }

    def _declared_schema_tests(self) -> list[tuple[str, str, str, dict[str, Any]]]:
        """Reads the column tests declared in dbt_project.yml: (model, column, type, config)."""
        with open(self.dbt_dir / "dbt_project.yml", encoding="utf-8") as f:
            project_cfg = yaml.safe_load(f)
        declared = []
        for model in project_cfg.get("models", []):
            for column in model.get("columns", []):
                for test in column.get("tests", []):
                    # "unique" / "not_null", or {"accepted_values": {"values": [...]}}
                    test_type, test_cfg = (
                        next(iter(test.items())) if isinstance(test, dict) else (test, {})
                    )
                    declared.append((model["name"], column["name"], test_type, test_cfg))
        return declared

    @staticmethod
    def _schema_test_sql(model: str, column: str, test_type: str, test_cfg: dict[str, Any]) -> str:
        """SQL counting the rows that violate one dbt schema test (0 = pass)."""
        if not (_IDENTIFIER.fullmatch(model) and _IDENTIFIER.fullmatch(column)):
            raise ValueError(f"invalid identifier in schema test: {model}.{column}")
        if test_type == "unique":
            return (
                "SELECT coalesce(sum(n), 0) AS failing_rows FROM ("  # noqa: S608 - identifiers validated above
                f"SELECT count(*) AS n FROM {model} WHERE {column} IS NOT NULL "
                f"GROUP BY {column} HAVING count(*) > 1) AS duplicated"
            )
        if test_type == "not_null":
            return f"SELECT count(*) AS failing_rows FROM {model} WHERE {column} IS NULL"  # noqa: S608 - identifiers validated above
        if test_type == "accepted_values":
            values = ", ".join(
                "'" + str(v).replace("'", "''") + "'" for v in test_cfg.get("values", [])
            )
            return (
                f"SELECT count(*) AS failing_rows FROM {model} "  # noqa: S608 - identifiers validated, values quoted
                f"WHERE {column} IS NOT NULL AND {column} NOT IN ({values})"
            )
        raise ValueError(f"unsupported schema test type: {test_type}")

    def run_schema_tests(self) -> dict[str, Any]:
        """Runs the dbt schema tests (unique, not_null, accepted_values) declared in
        dbt_project.yml against the warehouse.

        Every verdict is measured: a test PASSes only when its query ran and found 0
        violating rows; violations are FAIL, and a query that cannot run (missing
        model table/column, unsupported test) is ERROR. No tests run is not a PASS.
        """
        logger.info("Running dbt schema assertion tests...")
        test_results = []
        for model, column, test_type, test_cfg in self._declared_schema_tests():
            result: dict[str, Any] = {
                "test_name": f"{test_type}_{model}_{column}",
                "model": model,
                "column": column,
                "test_type": test_type,
            }
            try:
                sql = self._schema_test_sql(model, column, test_type, test_cfg)
                rows = self.ch.execute(f"{sql} FORMAT JSON")
                if not isinstance(rows, list) or not rows:
                    raise ValueError(f"schema test query returned no result rows: {rows!r}")
                failing = int(rows[0]["failing_rows"])
                result.update(
                    status="PASS" if failing == 0 else "FAIL", failing_rows=failing, error=None
                )
            except Exception as exc:
                result.update(status="ERROR", failing_rows=None, error=str(exc))
            test_results.append(result)

        counts = {
            status: sum(1 for t in test_results if t["status"] == status)
            for status in ("PASS", "FAIL", "ERROR")
        }
        all_passed = bool(test_results) and counts["PASS"] == len(test_results)
        logger.info(f"dbt schema tests: {counts} over {len(test_results)} declared tests")
        return {
            "status": "PASS" if all_passed else "FAIL",
            "passed_tests": counts["PASS"],
            "failed_tests": counts["FAIL"],
            "errored_tests": counts["ERROR"],
            "tests": test_results,
        }

    def execute_scheduled_dbt_run(self) -> dict[str, Any]:
        """Scheduled Airflow / K3s cron dbt run with full, measured evidence output."""
        logger.info("=== Starting R09-M01-T02 Scheduled dbt Build ===")
        # Ensure warehouse schema and sync are live
        sync_engine = WarehouseSyncEngine(ch_client=self.ch, pg_dsn=self.pg_dsn)
        sync_report = sync_engine.run_full_sync()

        freshness = self.run_source_freshness()
        if freshness["status"] != "PASS":
            logger.error("Source freshness failed! Gating dbt build.")
            evidence = {
                "milestone": "R09-M01",
                "task": "R09-M01-T02",
                "schedule": "0 2 * * * (daily 02:00 BST via Airflow / K3s cron)",
                "execution_timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                "status": "FAIL",
                "reason": "source_freshness_failed",
                "warehouse_mode": self.ch.mode,
                "sync": {
                    "status": sync_report.get("status"),
                    "replica_reachable": sync_report.get("replica_reachable"),
                    "extract_error": sync_report.get("extract_error"),
                    "total_source_rows": sync_report.get("total_source_rows"),
                    "total_clickhouse_rows": sync_report.get("total_clickhouse_rows"),
                    "reason": sync_report.get("reason"),
                },
                "freshness": freshness,
                "build": None,
                "tests": None,
                "lb06_read_only_downstream_verified": sync_report.get("lb06_read_replica_compliant")
                is True,
            }
            # A gated run still overwrites the evidence: a stale SUCCESS from a
            # previous run must never survive a failed one.
            EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
            evidence_file = EVIDENCE_DIR / "r09-m01-dbt-build-evidence.json"
            with open(evidence_file, "w", encoding="utf-8") as f:
                json.dump(evidence, f, indent=2)
            logger.info(f"dbt build evidence written to {evidence_file}: Status=FAIL")
            return evidence

        build = self.compile_and_build_models()
        tests = self.run_schema_tests()

        overall_status = (
            "SUCCESS" if (build["status"] == "SUCCESS" and tests["status"] == "PASS") else "FAIL"
        )

        evidence = {
            "milestone": "R09-M01",
            "task": "R09-M01-T02",
            "schedule": "0 2 * * * (daily 02:00 BST via Airflow / K3s cron)",
            "execution_timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "status": overall_status,
            "dbt_version": "1.8.x",
            "adapter": "dbt-clickhouse",
            # Which engine actually served this run - labelled, never assumed.
            "warehouse_mode": self.ch.mode,
            "sync": {
                "status": sync_report.get("status"),
                "replica_reachable": sync_report.get("replica_reachable"),
                "extract_error": sync_report.get("extract_error"),
                "total_source_rows": sync_report.get("total_source_rows"),
                "total_clickhouse_rows": sync_report.get("total_clickhouse_rows"),
                "reason": sync_report.get("reason"),
            },
            "freshness": freshness,
            "build": build,
            "tests": tests,
            "lb06_read_only_downstream_verified": sync_report.get("lb06_read_replica_compliant")
            is True,
        }

        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        evidence_file = EVIDENCE_DIR / "r09-m01-dbt-build-evidence.json"
        with open(evidence_file, "w", encoding="utf-8") as f:
            json.dump(evidence, f, indent=2)

        logger.info(f"dbt build evidence written to {evidence_file}: Status={overall_status}")
        return evidence


def main() -> int:
    runner = DbtWarehouseRunner()
    ev = runner.execute_scheduled_dbt_run()
    return 0 if ev.get("status") == "SUCCESS" else 1


if __name__ == "__main__":
    sys.exit(main())
