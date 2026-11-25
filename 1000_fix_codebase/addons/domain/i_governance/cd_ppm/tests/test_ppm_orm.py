"""cd_ppm — live-ORM behaviour of M67 projects, milestones and tasks.

A12 rewrite (2026-11-05): activation now needs the DOFA budget approval
(unbudgeted projects fall at tier_0 = no approval), milestone completion
needs recorded customer acceptance, task state is guarded (cancelled via
action_cancel, not an assignment), and the baseline freezes at activation.
Runs as the superuser; the role gates live in test_a12_m67_controls.py.

A12 finish (2026-11-07): the old variance test TYPED actual_cost (F13, the
defect); cost is now measured from task hours at a rate parameter. Activation
now needs a manager and G1 and G2 passed (F12, F17).
"""

from __future__ import annotations

import json
from decimal import Decimal

import pytest
from odoo.exceptions import UserError

D = Decimal


def _events(env, event_type, aggregate_id):
    domain = [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)]
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def _ready_for_activation(env, project):
    """The entry conditions of F12 and F17, as the superuser."""
    if not project.manager_id:
        project.manager_id = env["hr.employee"].create({"name": "PPM ORM Manager"})
    for key in ("g1_initiation", "g2_planning"):
        gate = env["fix.project.gate"].create({"project_id": project.id, "gate": key})
        gate.action_record_decision("pass", checklist_passed=True)
        gate.action_hold()
        gate.action_close()
    return project


def test_project_code_event_and_variance(odoo_env):
    project = odoo_env["fix.project"].create(
        {"name": "Sylhet hub fit-out", "project_type": "infrastructure", "budget": 1000000.0}
    )
    assert project.code.startswith("PRJ/")
    assert _events(odoo_env, "project.created", project.id) == [
        {"name": "Sylhet hub fit-out", "type": "infrastructure"}
    ]
    # Nothing measures this project yet: no variance is claimed.
    assert project.cost_measured is False
    assert project.cost_basis == "Not measured"
    assert D(str(project.budget_variance)) == D("0.0")
    # 450 hours at 2,500 = 1,125,000 against 1,000,000.
    odoo_env["ir.config_parameter"].sudo().set_param("fix_ppm.cost_rate_per_hour", "2500")
    odoo_env["fix.project.task"].create(
        {"name": "Fit-out", "project_id": project.id, "actual_hours": 450.0}
    )
    project.invalidate_recordset()
    assert D(str(project.actual_cost)) == D("1125000.0")
    assert D(str(project.budget_variance)).quantize(D("0.01")) == D("-125000.00")
    assert project.variance_pct == -12.5  # -125,000 / 1,000,000
    unbudgeted = odoo_env["fix.project"].create({"name": "Pilot"})
    odoo_env["fix.project.task"].create(
        {"name": "Pilot run", "project_id": unbudgeted.id, "actual_hours": 0.2}
    )
    unbudgeted.invalidate_recordset()
    assert (unbudgeted.variance_pct, unbudgeted.budget_variance) == (0.0, -500.0)


def test_completion_gates(odoo_env):
    project = odoo_env["fix.project"].create({"name": "Warehouse WMS"})
    # Unbudgeted: DOFA tier_0, activation needs no financial sign-off.
    _ready_for_activation(odoo_env, project).action_activate()
    assert project.state == "active"
    assert project.baseline_budget == 0.0
    milestone = odoo_env["fix.project.milestone"].create(
        {"name": "Go-live", "project_id": project.id}
    )
    tasks = odoo_env["fix.project.task"].create(
        [
            {"name": "Barcode labels", "project_id": project.id, "milestone_id": milestone.id},
            {"name": "Training", "project_id": project.id, "milestone_id": milestone.id},
            {"name": "Optional report", "project_id": project.id, "milestone_id": milestone.id},
        ]
    )
    with pytest.raises(UserError, match="1 milestone\\(s\\) still open"), odoo_env.cr.savepoint():
        project.action_complete()
    tasks[0].action_start()
    assert tasks[0].state == "in_progress"
    # BRU-PPM-11: no acceptance, no completion — acceptance is checked first,
    # so this fires even with all three tasks still open.
    with (
        pytest.raises(UserError, match="no recorded acceptance"),
        odoo_env.cr.savepoint(),
    ):
        milestone.action_complete()
    milestone.action_accept("Client sign-off SO-4471")
    assert milestone.accepted_by_id
    with (
        pytest.raises(UserError, match="3 task\\(s\\) still open in milestone"),
        odoo_env.cr.savepoint(),
    ):
        milestone.action_complete()
    (tasks[0] | tasks[1]).action_done()
    tasks[2].action_cancel()  # cancelled work does not block (guard: via action)
    milestone.action_complete()
    assert milestone.state == "done"
    assert _events(odoo_env, "project.milestone_completed", milestone.id) == [
        {"milestone": "Go-live", "project": "Warehouse WMS"}
    ]
    # BRU-PPM-14 (M67 capture audit): a lesson passed to Quality before closure.
    lesson = odoo_env["fix.project.lesson"].create(
        {"project_id": project.id, "observation": "o", "recommendation": "r"}
    )
    lesson.action_share()
    if project.project_type == "internal":
        benefit = odoo_env["fix.project.benefit"].create(
            {
                "name": "b",
                "project_id": project.id,
                "business_case_target": 1.0,
                "unit": "u",
                "measurement_method": "m",
            }
        )
        benefit.action_record_measurement(measured_value=1, evidence="e")
    project.action_complete()
    assert project.state == "completed"
    assert _events(odoo_env, "project.completed", project.id) == [{"name": "Warehouse WMS"}]
