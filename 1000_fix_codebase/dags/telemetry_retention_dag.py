# telemetry_retention_dag.py — daily PDPA Tier-1 telemetry retention (90 days).
#
# D-030: TimescaleDB is approved for Apache-2.0 features ONLY. Its automated
# retention policy and job scheduler are TSL-licensed, so retention is driven
# from here instead: once a day this DAG calls the Apache-2.0
# drop_chunks wrapper defined in migrations/sql/timescaledb_telemetry_hypertable.sql:
#     SELECT fix_telemetry_apply_retention();
# The Airflow connection ``fix_telemetry_db`` must point at the telemetry
# database (configured by operations; no credentials live in this repo).
from __future__ import annotations

from datetime import datetime, timedelta

try:
    from airflow import DAG
    from airflow.exceptions import AirflowFailException
    from airflow.operators.python import PythonOperator
except ImportError:

    class AirflowFailException(Exception):
        """Shim: Airflow's fail-without-retry task exception."""

    class DAG:
        def __init__(
            self,
            dag_id,
            description=None,
            schedule=None,
            start_date=None,
            catchup=False,
            default_args=None,
            tags=None,
        ):
            self.dag_id = dag_id
            self.description = description
            self.schedule = schedule
            self.start_date = start_date
            self.catchup = catchup
            self.default_args = default_args or {}
            self.tags = tags or []
            self.tasks = {}

    class PythonOperator:
        def __init__(self, task_id, python_callable, op_kwargs=None, dag=None):
            self.task_id = task_id
            self.python_callable = python_callable
            self.op_kwargs = op_kwargs or {}
            self.dag = dag
            if dag:
                dag.tasks[task_id] = self


TELEMETRY_CONN_ID = "fix_telemetry_db"
RETENTION_SQL = "SELECT fix_telemetry_apply_retention();"


def apply_retention(conn_id: str = TELEMETRY_CONN_ID, **kwargs) -> int:
    """Drop telemetry chunks older than the 90-day window; returns chunks dropped."""
    try:
        from airflow.providers.postgres.hooks.postgres import PostgresHook
    except ImportError as exc:
        raise AirflowFailException(
            "apache-airflow-providers-postgres is required to run the telemetry retention"
        ) from exc
    row = PostgresHook(postgres_conn_id=conn_id).get_first(RETENTION_SQL)
    if row is None:
        raise AirflowFailException("fix_telemetry_apply_retention() returned no row")
    return int(row[0])


dag = DAG(
    dag_id="telemetry_retention_daily",
    description="PDPA Tier-1 telemetry retention: drop_chunks older than 90 days (D-030 Apache-only)",
    schedule="@daily",
    start_date=datetime(2026, 10, 1),
    catchup=False,
    default_args={"owner": "1000fix_platform", "retries": 2, "retry_delay": timedelta(minutes=10)},
    tags=["telemetry", "retention", "pdpa"],
)

apply_retention_task = PythonOperator(
    task_id="apply_telemetry_retention",
    python_callable=apply_retention,
    op_kwargs={"conn_id": TELEMETRY_CONN_ID},
    dag=dag,
)
