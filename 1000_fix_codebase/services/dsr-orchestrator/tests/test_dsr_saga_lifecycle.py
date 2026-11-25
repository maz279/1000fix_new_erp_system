"""dsr-orchestrator saga lifecycle: status transitions, resume and retry (P07-M08-T04)."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dsr_orchestrator import (
    DsrError,
    DsrRequest,
    DsrState,
    DsrType,
    SagaState,
    SagaStep,
    run_erasure_saga,
)


def _recording_executors(calls, fail_at=None):
    def make(step):
        def run(party_ref):
            calls.append((step, party_ref))
            if step is fail_at:
                raise RuntimeError(f"{step.value} exploded")

        return run

    return {step: make(step) for step in SagaStep}


def test_explicit_due_date_is_kept():
    req = DsrRequest("R9", DsrType.ERASURE, "party:9", date(2027, 5, 1), due_on=date(2027, 5, 10))
    assert req.due_on == date(2027, 5, 10)
    assert req.state is DsrState.RECEIVED
    assert req.verified is False


def test_fresh_saga_is_in_progress():
    assert SagaState("S0", "party:0").status == "in_progress"


def test_partially_completed_saga_is_in_progress():
    state = SagaState("S0", "party:0", completed=[SagaStep.ANONYMIZE_REGIONAL])
    assert state.status == "in_progress"


def test_resume_skips_already_completed_steps():
    calls = []
    done = [SagaStep.ANONYMIZE_REGIONAL, SagaStep.TOMBSTONE_RESIDENT]
    state = SagaState("S1", "party:1", completed=list(done))
    run_erasure_saga(state, _recording_executors(calls))
    executed = [step for step, _ in calls]
    assert SagaStep.ANONYMIZE_REGIONAL not in executed
    assert SagaStep.TOMBSTONE_RESIDENT not in executed
    assert executed == list(SagaStep)[2:]
    assert state.status == "completed"


def test_failure_on_first_step_has_nothing_to_compensate():
    calls = []
    state = SagaState("S2", "party:2")
    with pytest.raises(DsrError, match="failed at anonymize_regional") as excinfo:
        run_erasure_saga(state, _recording_executors(calls, fail_at=SagaStep.ANONYMIZE_REGIONAL))
    assert isinstance(excinfo.value.__cause__, RuntimeError)
    assert "compensations run: []" in str(excinfo.value)
    assert state.failed_at is SagaStep.ANONYMIZE_REGIONAL
    assert state.compensations_run == []
    assert state.completed == []
    assert state.status == "failing"


def test_failure_after_progress_is_rolled_back():
    state = SagaState("S3", "party:3")
    with pytest.raises(DsrError):
        run_erasure_saga(state, _recording_executors([], fail_at=SagaStep.PURGE_REPLICAS))
    assert state.completed == []
    assert state.compensations_run == [
        SagaStep.TOMBSTONE_RESIDENT.compensation,
        SagaStep.ANONYMIZE_REGIONAL.compensation,
    ]
    assert state.status == "rolled_back"


def test_regression_retry_after_rollback_reports_completed():
    """Regression: a saga re-run to completion after a rolled-back attempt
    used to keep reporting "rolled_back" because the stale ``failed_at``
    was checked before the all-steps-completed condition."""
    state = SagaState("S4", "party:4")
    with pytest.raises(DsrError):
        run_erasure_saga(state, _recording_executors([], fail_at=SagaStep.PURGE_WAREHOUSE))
    assert state.status == "rolled_back"

    run_erasure_saga(state, _recording_executors([]))
    assert state.completed == list(SagaStep)
    assert state.status == "completed"
    # the audit trail of the failed attempt is preserved
    assert state.failed_at is SagaStep.PURGE_WAREHOUSE
    assert state.compensations_run


def test_regression_retry_after_first_step_failure_reports_completed():
    """Regression: same stale-status defect for the nothing-to-compensate case
    (previously "failing" forever)."""
    state = SagaState("S5", "party:5")
    with pytest.raises(DsrError):
        run_erasure_saga(state, _recording_executors([], fail_at=SagaStep.ANONYMIZE_REGIONAL))
    assert state.status == "failing"
    run_erasure_saga(state, _recording_executors([]))
    assert state.status == "completed"
