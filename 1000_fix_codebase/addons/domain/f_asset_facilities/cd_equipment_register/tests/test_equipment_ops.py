"""cd_equipment_register ops behaviour (live ORM, rolled back): kits, issue and
return custody, transfers, verification, out-of-service enforcement, PM and
usage capture."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from odoo.exceptions import UserError
from psycopg2 import IntegrityError

TAG = uuid.uuid4().hex[:6].upper()


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    equipment = env["fix.equipment"].create(
        {"code": f"EQ-{TAG}", "name": f"Tester {TAG}", "category": "Electrical"}
    )
    employee = env["hr.employee"].create({"name": f"Tech {TAG}"})
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": f"E{TAG[:5]}", "legal_name": f"Entity {TAG}", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": f"Branch {TAG}",
            "code": f"B{TAG[:5]}",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    return {"env": env, "equipment": equipment, "employee": employee, "branch": branch}


def test_kit_lines_unique(ctx):
    env, equipment = ctx["env"], ctx["equipment"]
    kit = env["fix.equipment.kit"].create(
        {
            "name": f"Kit {TAG}",
            "code": f"K-{TAG}",
            "line_ids": [(0, 0, {"equipment_id": equipment.id})],
        }
    )
    with pytest.raises(IntegrityError), env.cr.savepoint():
        env["fix.equipment.kit.line"].create({"kit_id": kit.id, "equipment_id": equipment.id})


def test_issue_sets_status_and_return_restores(ctx):
    env, equipment, employee = ctx["env"], ctx["equipment"], ctx["employee"]
    issue = env["fix.equipment.issue"].create(
        {
            "equipment_id": equipment.id,
            "custodian_id": employee.id,
            "due_on": date.today() - timedelta(days=1),
        }
    )
    assert issue.name.startswith("EISS/")
    assert equipment.operational_status == "issued"
    assert issue.is_overdue is True
    issue.action_return()
    assert issue.state == "returned"
    assert equipment.operational_status == "available"
    with pytest.raises(UserError, match="issued"), env.cr.savepoint():
        issue.action_return()


def test_transfer_record(ctx):
    env, equipment, employee, branch = ctx["env"], ctx["equipment"], ctx["employee"], ctx["branch"]
    transfer = env["fix.equipment.transfer"].create(
        {
            "equipment_id": equipment.id,
            "to_branch_id": branch.id,
            "from_custodian_id": employee.id,
            "to_custodian_id": employee.id,
        }
    )
    assert transfer.name.startswith("ETRF/")


def test_verification_missing_state(ctx):
    env, equipment = ctx["env"], ctx["equipment"]
    record = env["fix.equipment.verification"].create(
        {
            "equipment_id": equipment.id,
            "campaign_ref": f"CAM-{TAG}",
            "found": False,
        }
    )
    assert record.name.startswith("EVER/")
    assert record.state == "missing"


def test_out_of_service_blocks_then_resolves(ctx):
    env, equipment = ctx["env"], ctx["equipment"]
    oos = env["fix.equipment.oos"].create(
        {"equipment_id": equipment.id, "reason": "failed calibration"}
    )
    assert oos.name.startswith("EOOS/")
    assert equipment.operational_status == "out_of_service"
    oos.action_resolve()
    assert oos.state == "resolved"
    assert equipment.operational_status == "available"
    with pytest.raises(UserError, match="open"), env.cr.savepoint():
        oos.action_resolve()


def test_assert_usable_refuses_overdue_equipment(ctx):
    env, equipment = ctx["env"], ctx["equipment"]
    env["fix.calibration"].create(
        {
            "equipment_id": equipment.id,
            "calibrated_on": date.today() - timedelta(days=400),
            "standard_ref": f"STD-{TAG}",
            "result": "pass",
            "next_due": date.today() - timedelta(days=1),
        }
    )
    with pytest.raises(UserError, match="calibrat"), env.cr.savepoint():
        equipment.action_assert_usable()


def test_pm_completion_and_usage(ctx):
    env, equipment = ctx["env"], ctx["equipment"]
    job = env["fix.equipment.pm"].create({"equipment_id": equipment.id, "cost": 1500})
    assert job.name.startswith("EPM/")
    job.action_done()
    assert job.done_on
    usage = env["fix.equipment.usage"].create(
        {"equipment_id": equipment.id, "job_ref": f"WO-{TAG}", "uses": 2}
    )
    assert usage.uses == 2
    with pytest.raises(IntegrityError), env.cr.savepoint():
        usage.uses = 0
