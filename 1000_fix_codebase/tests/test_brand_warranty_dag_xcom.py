"""R01-AUDIT: the brand-warranty blocking completeness check validates the
REAL claim pulled from XCom (never a built-in SAMPLE), and fails when the
upstream task pushed no claim."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import dags.brand_warranty_submission_dag as dag_module
from services.workflow.brand_submission_engine import CompletenessViolationError

COMPLETE_EVIDENCE = [
    "photo_before",
    "photo_after",
    "diagnostic",
    "parts_issued",
    "device_serial",
    "technician_cert",
    "purchase_proof",
]


class FakeTaskInstance:
    """Records xcom_pull calls and serves one pushed value per task id."""

    def __init__(self, pushed: dict[str, object]):
        self.pushed = pushed
        self.pulled: list[str] = []

    def xcom_pull(self, task_ids: str, key: str = "return_value"):
        self.pulled.append(task_ids)
        return self.pushed.get(task_ids)


def _complete_claim(claim_no: str) -> dict:
    return {
        "claim_no": claim_no,
        "device_serial": "SN-XCOM-1",
        "fault_code": "FLT-PWR-001",
        "diagnostic_summary": "PSU capacitor replaced",
        "parts_list": [{"part_no": "CAP-100UF", "qty": 2}],
        "total_amount": 2100.0,
        "evidence_keys": list(COMPLETE_EVIDENCE),
    }


class TestBlockingCheckPullsRealClaim(unittest.TestCase):
    def setUp(self):
        self.dag = dag_module.generated_dags["warranty_submission_samsung"]
        self.fetch = self.dag.tasks[dag_module.fetch_task_id("Samsung")]
        self.check = self.dag.tasks[dag_module.check_task_id("Samsung")]
        self.submit = self.dag.tasks[dag_module.submit_task_id("Samsung")]
        self.brand_code = self.check.op_kwargs["brand_code"]

    def _run(self, task, ti):
        return task.python_callable(**task.op_kwargs, ti=ti)

    def test_check_is_wired_to_the_fetch_task(self):
        self.assertEqual(self.check.op_kwargs["upstream_task_id"], self.fetch.task_id)
        self.assertEqual(self.submit.op_kwargs["upstream_task_id"], self.check.task_id)

    def test_complete_claim_from_xcom_passes(self):
        claim = _complete_claim("CLM-XCOM-OK")
        ti = FakeTaskInstance({self.fetch.task_id: {"claims": [claim]}})
        result = self._run(self.check, ti)
        self.assertEqual(ti.pulled, [self.fetch.task_id])
        self.assertEqual(result["claim_nos"], ["CLM-XCOM-OK"])

    def test_incomplete_claim_from_xcom_is_blocked(self):
        claim = _complete_claim("CLM-XCOM-BAD")
        claim["evidence_keys"] = ["photo_before"]
        ti = FakeTaskInstance({self.fetch.task_id: {"claims": [claim]}})
        with self.assertRaises(CompletenessViolationError):
            self._run(self.check, ti)

    def test_missing_claim_fails_the_task(self):
        for pushed in ({}, {self.fetch.task_id: None}, {self.fetch.task_id: {"claims": []}}):
            with self.subTest(pushed=pushed), self.assertRaises(dag_module.AirflowFailException):
                self._run(self.check, FakeTaskInstance(pushed))

    def test_missing_task_instance_fails_the_task(self):
        with self.assertRaises(dag_module.AirflowFailException):
            self.check.python_callable(**self.check.op_kwargs)

    def test_fetch_reports_only_claims_it_received(self):
        empty = self.fetch.python_callable(**self.fetch.op_kwargs)
        self.assertEqual(empty["count"], 0)
        self.assertEqual(empty["claims"], [])
        run = SimpleNamespace(conf={"claims": [_complete_claim("CLM-CONF-1")]})
        fetched = self.fetch.python_callable(**self.fetch.op_kwargs, dag_run=run)
        self.assertEqual(fetched["count"], 1)

    def test_end_to_end_submits_the_validated_claim(self):
        claim = _complete_claim("CLM-E2E-1")
        run = SimpleNamespace(conf={"claims": [claim]})
        fetched = self.fetch.python_callable(**self.fetch.op_kwargs, dag_run=run)
        checked = self._run(self.check, FakeTaskInstance({self.fetch.task_id: fetched}))
        acks = self._run(self.submit, FakeTaskInstance({self.check.task_id: checked}))
        self.assertEqual(len(acks), 1)
        self.assertEqual(acks[0]["status"], "submitted")
        self.assertEqual(acks[0]["brand_code"], self.brand_code)

    def test_submit_without_verified_claim_fails(self):
        with self.assertRaises(dag_module.AirflowFailException):
            self._run(self.submit, FakeTaskInstance({}))


if __name__ == "__main__":
    unittest.main()
