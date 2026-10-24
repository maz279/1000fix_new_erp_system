# brand_warranty_submission_dag.py — Dynamic Brand Warranty Submission Workflows (R05-M01-T03)
#
# Generates 18 Apache Airflow DAGs dynamically from configuration (brand_templates.json).
# Architecture decision (P07-M02-T06):
#   "Why Apache Airflow and not custom code: the transformation is configuration
#    that changes when a brand changes its template, not code that requires a release.
#    The claim record, the evidence pack and the reconciliation stay in Odoo."
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

# Fallback shims for environment where airflow is not pip-installed
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

        def __rshift__(self, other):
            return other


import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.workflow.brand_submission_engine import (  # noqa: E402 - after sys.path bootstrap
    BrandSubmissionWorkflow,
    BrandTemplateRegistry,
)

CONFIG_PATH = Path(__file__).resolve().parents[1] / "services" / "workflow" / "brand_templates.json"

default_args = {
    "owner": "1000fix_service_operations",
    "depends_on_past": False,
    "email_on_failure": True,
    "email": ["warranty-operations@1000fix.com"],
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

registry = BrandTemplateRegistry(CONFIG_PATH)
templates = registry.list_all_templates()


def _slug(brand_name: str) -> str:
    return brand_name.lower().replace(" ", "_")


def fetch_task_id(brand_name: str) -> str:
    return f"fetch_ready_{_slug(brand_name)}_claims"


def check_task_id(brand_name: str) -> str:
    return f"blocking_completeness_check_{_slug(brand_name)}"


def submit_task_id(brand_name: str) -> str:
    return f"transform_and_submit_{_slug(brand_name)}"


def _task_fetch_ready_claims(brand_code: str, **kwargs):
    """Task 1: Fetch claims in 'ready' state for this brand.

    The Odoo query (fix.warranty.claim, brand_code == brand_code, state ==
    'ready') is not wired yet; claims arrive through the DAG run's conf
    (``{"claims": [...]}``). The count is the number actually received - an
    empty run reports 0, it never claims a fetched claim that does not exist.
    """
    dag_run = kwargs.get("dag_run")
    conf = (getattr(dag_run, "conf", None) or {}) if dag_run is not None else {}
    claims = [
        claim
        for claim in conf.get("claims", [])
        if isinstance(claim, dict) and claim.get("brand_code", brand_code) == brand_code
    ]
    return {
        "brand_code": brand_code,
        "status": "claims_fetched" if claims else "no_ready_claims",
        "count": len(claims),
        "claims": claims,
    }


def _pull_claims(ti, upstream_task_id: str) -> list[dict]:
    """Pull the claims an upstream task pushed to XCom; [] when there are none."""
    if ti is None:
        raise AirflowFailException(
            "no task instance in context - cannot pull claims from XCom; refusing to validate"
        )
    pushed = ti.xcom_pull(task_ids=upstream_task_id)
    if not isinstance(pushed, dict):
        return []
    claims = pushed.get("claims")
    return [c for c in claims if isinstance(c, dict)] if isinstance(claims, list) else []


def _task_blocking_completeness_check(brand_code: str, upstream_task_id: str, **kwargs):
    """Task 2: The BLOCKING completeness check — blocks incomplete packs.

    Validates the REAL claims fetched by ``upstream_task_id`` (pulled from
    XCom). No claim to validate fails the task: the gate never passes on a
    sample. An incomplete pack raises CompletenessViolationError.
    """
    template = registry.get_template(brand_code)
    workflow = BrandSubmissionWorkflow(template)
    claims = _pull_claims(kwargs.get("ti"), upstream_task_id)
    if not claims:
        raise AirflowFailException(
            f"{brand_code}: no claim in XCom from {upstream_task_id!r} - "
            "nothing was validated, the completeness gate cannot pass"
        )
    for claim in claims:
        workflow.check_completeness(claim)
    return {
        "status": "completeness_verified",
        "claim_nos": [c.get("claim_no") for c in claims],
        "claims": claims,
    }


def _task_transform_and_submit(brand_code: str, upstream_task_id: str, **kwargs):
    """Task 3 & 4: Transform the claims that passed the blocking check into the
    brand schema and dispatch them to the brand portal/API."""
    template = registry.get_template(brand_code)
    workflow = BrandSubmissionWorkflow(template)
    claims = _pull_claims(kwargs.get("ti"), upstream_task_id)
    if not claims:
        raise AirflowFailException(
            f"{brand_code}: no completeness-verified claim in XCom from {upstream_task_id!r} - "
            "nothing to submit"
        )
    return [workflow.execute_submission(claim) for claim in claims]


# Dynamically register one DAG per brand template
generated_dags = {}

for tmpl in templates:
    b_code = tmpl["brand_code"]
    b_name = _slug(tmpl["brand_name"])
    dag_id = f"warranty_submission_{b_name}"

    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        description=f"Automated warranty submission workflow for {tmpl['brand_name']} ({b_code})",
        schedule="0 */2 * * *",  # Every 2 hours
        start_date=datetime(2026, 10, 1),
        catchup=False,
        tags=["warranty", "brand_submission", b_name, b_code],
    )

    t1 = PythonOperator(
        task_id=fetch_task_id(tmpl["brand_name"]),
        python_callable=_task_fetch_ready_claims,
        op_kwargs={"brand_code": b_code},
        dag=dag,
    )

    t2 = PythonOperator(
        task_id=check_task_id(tmpl["brand_name"]),
        python_callable=_task_blocking_completeness_check,
        op_kwargs={"brand_code": b_code, "upstream_task_id": t1.task_id},
        dag=dag,
    )

    t3 = PythonOperator(
        task_id=submit_task_id(tmpl["brand_name"]),
        python_callable=_task_transform_and_submit,
        op_kwargs={"brand_code": b_code, "upstream_task_id": t2.task_id},
        dag=dag,
    )

    t1 >> t2 >> t3
    generated_dags[dag_id] = dag
    globals()[dag_id] = dag
