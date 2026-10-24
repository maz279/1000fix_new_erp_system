"""cd_ppm — live-ORM behaviour of M67 projects, milestones and tasks."""

from __future__ import annotations

import json
from decimal import Decimal

import pytest
from odoo.exceptions import UserError

D = Decimal


def _events(env, event_type, aggregate_id):
    domain = [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)]
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def test_project_code_event_and_variance(odoo_env):
    project = odoo_env["fix.project"].create(
        {"name": "Sylhet hub fit-out", "project_type": "infrastructure", "budget": 1000000.0}
    )
    assert project.code.startswith("PRJ/")
    assert _events(odoo_env, "project.created", project.id) == [
        {"name": "Sylhet hub fit-out", "type": "infrastructure"}
    ]
    assert D(str(project.budget_variance)) == D("1000000.0")
    assert project.variance_pct == 100.0
    project.actual_cost = 1125000.0
    assert D(str(project.budget_variance)).quantize(D("0.01")) == D("-125000.00")
    assert project.variance_pct == -12.5  # -125,000 / 1,000,000
    unbudgeted = odoo_env["fix.project"].create({"name": "Pilot", "actual_cost": 500.0})
    assert (unbudgeted.variance_pct, unbudgeted.budget_variance) == (0.0, -500.0)


def test_completion_gates(odoo_env):
    project = odoo_env["fix.project"].create({"name": "Warehouse WMS"})
    project.action_activate()
    assert project.state == "active"
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
    with (
        pytest.raises(UserError, match="3 task\\(s\\) still open in milestone"),
        odoo_env.cr.savepoint(),
    ):
        milestone.action_complete()
    (tasks[0] | tasks[1]).action_done()
    tasks[2].state = "cancelled"  # cancelled work does not block
    milestone.action_complete()
    assert milestone.state == "done"
    assert _events(odoo_env, "project.milestone_completed", milestone.id) == [
        {"milestone": "Go-live", "project": "Warehouse WMS"}
    ]
    project.action_complete()
    assert project.state == "completed"
    assert _events(odoo_env, "project.completed", project.id) == [{"name": "Warehouse WMS"}]
