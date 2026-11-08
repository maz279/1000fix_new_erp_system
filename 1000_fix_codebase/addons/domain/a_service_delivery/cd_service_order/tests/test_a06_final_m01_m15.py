"""A06 final pass B2 (M15-10): a part consumed on a work order leaves the M15
ledger. Runs through the technician route the bench app calls, as the assigned
technician; `odoo_env` rolls back.
"""

import pytest
from odoo.addons.cd_service_order.controllers.technician_api import TechnicianApiController
from odoo.exceptions import UserError

from . import test_technician_api_behaviour as base

world = base.world
_as = base._as


@pytest.fixture
def mapped(world):
    env = world.env
    part = env["fix.spare.part"].create(
        {
            "name": "Tab Screen (M15)",
            "part_number": "A6WO-%s" % world.part.id,
            "unit_cost": 400.0,
            "product_id": world.part.id,
        }
    )
    van = env["fix.stock.location"].create(
        {
            "name": "Tab Van",
            "code": "A6WV-%s" % world.part.id,
            "location_type": "van",
            "technician_id": world.wo.technician_id.id,
        }
    )
    env["fix.stock.onhand"]._apply(part, van, "van", 3.0, 400.0)
    return part, van


def _qty(world, part, location, cls="van"):
    world.env.invalidate_all()
    row = world.env["fix.stock.onhand"]._bucket(part, location, cls)
    return row.qty if row else 0.0


def test_b2_a_mapped_part_leaves_the_technicians_van(world, mapped):
    part, van = mapped
    with _as(world.env, world.tech_user):
        ok = TechnicianApiController().van_stock_consume(
            work_order_id=world.wo.id, product_id=world.part.id, quantity=2
        )
    line = world.env["fix.work.order.part"].browse(ok["consumed"]["part_line_id"])
    issue = line.m15_consumption_id
    assert issue.state == "consumed"
    assert (issue.product_id, issue.location_id, issue.quantity) == (part, van, 2.0)
    assert issue.work_order_ref == world.wo.name
    assert (issue.job_model, issue.job_res_id) == ("fix.service.order", world.wo.order_id.id)
    assert _qty(world, part, van) == 1.0


def test_b2_not_enough_stock_refuses_and_leaves_no_line(world, mapped):
    part, van = mapped
    before = world.env["fix.work.order.part"].search_count([("work_order_id", "=", world.wo.id)])
    with _as(world.env, world.tech_user):
        out = TechnicianApiController().van_stock_consume(
            work_order_id=world.wo.id, product_id=world.part.id, quantity=9
        )
    assert out["error"]["code"] == "m15_refused"
    assert "Insufficient" in out["error"]["message"]
    after = world.env["fix.work.order.part"].search_count([("work_order_id", "=", world.wo.id)])
    assert after == before and _qty(world, part, van) == 3.0


def test_b2_with_no_van_it_issues_from_the_branch_store(world):
    env = world.env
    part = env["fix.spare.part"].create(
        {
            "name": "Tab Screen (store)",
            "part_number": "A6WS-%s" % world.part.id,
            "unit_cost": 100.0,
            "product_id": world.part.id,
        }
    )
    store = env["fix.stock.location"].create(
        {
            "name": "Tab Store",
            "code": "A6WB-%s" % world.part.id,
            "location_type": "branch",
            "branch_id": world.wo.order_id.branch_id.id,
        }
    )
    env["fix.stock.onhand"]._apply(part, store, "owned", 2.0, 100.0)
    line = env["fix.work.order.part"].create(
        {"work_order_id": world.wo.id, "product_id": world.part.id, "quantity": 1.0}
    )
    assert line.m15_consumption_id.location_id == store
    assert _qty(world, part, store, "owned") == 1.0


def test_b2_an_issued_line_cannot_be_deleted_to_hide_it(world, mapped):
    with _as(world.env, world.tech_user):
        ok = TechnicianApiController().van_stock_consume(
            work_order_id=world.wo.id, product_id=world.part.id
        )
    line = world.env["fix.work.order.part"].browse(ok["consumed"]["part_line_id"])
    manager = (
        world.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A6 WO Mgr",
                "login": "a6.wo.mgr@api.test",
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            world.env.ref("base.group_user").id,
                            world.env.ref("base.group_system").id,
                        ],
                    )
                ],
            }
        )
    )
    with pytest.raises(UserError, match="return it"), world.env.cr.savepoint():
        line.with_user(manager).unlink()


def test_b2_unmapped_is_unchanged_unless_the_param_is_on(world):
    with _as(world.env, world.tech_user):
        ok = TechnicianApiController().van_stock_consume(
            work_order_id=world.wo.id, product_id=world.part.id
        )
    assert "consumed" in ok
    world.env["ir.config_parameter"].sudo().set_param("cd_service_order.m15_issue_required", "1")
    with _as(world.env, world.tech_user):
        out = TechnicianApiController().van_stock_consume(
            work_order_id=world.wo.id, product_id=world.part.id
        )
    assert out["error"]["code"] == "m15_refused"
