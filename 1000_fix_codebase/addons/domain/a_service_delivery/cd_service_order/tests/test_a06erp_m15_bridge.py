"""A06 ERP audit (20 Nov 2026) A06/A08/X22, owner decision D3: the work-order
bridge lets M15 pick the store (branch + warranty status), draws the job's own
reservation first, refuses ambiguity instead of taking the first store, and
the job line carries the cost M15 issued at. `odoo_env` rolls back."""

import pytest
from odoo.exceptions import UserError

from . import test_technician_api_behaviour as base

world = base.world


@pytest.fixture(autouse=True)
def _approved_order(world):
    base._so_to(world.so, "approved")


def _part(world, cost=300.0):
    return world.env["fix.spare.part"].create(
        {
            "name": "Bridge Screen",
            "part_number": "A6EB-%s" % world.part.id,
            "unit_cost": cost,
            "product_id": world.part.id,
        }
    )


def _store(world, code, stock_type, part=None, qty=0.0, cost=300.0):
    store = world.env["fix.stock.location"].create(
        {
            "name": "Store %s" % code,
            "code": "A6E%s-%s" % (code, world.part.id),
            "location_type": "branch",
            "branch_id": world.so.branch_id.id,
            "stock_type": stock_type,
        }
    )
    if part and qty:
        world.env["fix.stock.onhand"]._apply(part, store, "owned", qty, cost)
    return store


def _line(world, qty=1.0):
    return world.env["fix.work.order.part"].create(
        {"work_order_id": world.wo.id, "product_id": world.part.id, "quantity": qty}
    )


def _qty(world, part, location):
    world.env.invalidate_all()
    row = world.env["fix.stock.onhand"]._bucket(part, location, "owned")
    return row.qty if row else 0.0


def _warranty(world):
    world.env.flush_all()
    world.env.cr.execute(
        "UPDATE fix_service_order SET order_category = 'warranty' WHERE id = %s", [world.so.id]
    )
    world.so.invalidate_recordset(["order_category"])


def test_a06_a_warranty_job_takes_the_branchs_warranty_store(world):
    part = _part(world)
    plain = _store(world, "NW", "non_warranty", part, 3.0)
    wty = _store(world, "WT", "warranty", part, 3.0)
    _warranty(world)
    line = _line(world)
    assert line.m15_consumption_id.location_id == wty
    assert (_qty(world, part, wty), _qty(world, part, plain)) == (2.0, 3.0)


def test_a06_a_paid_job_never_takes_the_warranty_store(world):
    part = _part(world)
    plain = _store(world, "NW", "non_warranty", part, 3.0)
    wty = _store(world, "WT", "warranty", part, 3.0)
    line = _line(world)
    assert line.m15_consumption_id.location_id == plain
    assert _qty(world, part, wty) == 3.0


def test_a06_two_stocked_stores_of_the_kind_are_refused_not_guessed(world):
    part = _part(world)
    _store(world, "N1", "non_warranty", part, 3.0)
    _store(world, "N2", "buffer", part, 3.0)
    with pytest.raises(UserError, match="ambiguous"), world.env.cr.savepoint():
        _line(world)


def test_a08_the_jobs_own_reservation_is_drawn_first(world):
    part = _part(world)
    first = _store(world, "N1", "non_warranty", part, 3.0)
    second = _store(world, "N2", "buffer", part, 3.0)
    reservation = world.env["fix.stock.reservation"].create(
        {
            "part_id": part.id,
            "location_id": second.id,
            "qty": 1.0,
            "service_order_ref": world.so.name,
        }
    )
    reservation.action_reserve()
    line = _line(world)
    issue = line.m15_consumption_id
    assert issue.location_id == second and issue.reservation_id == reservation
    assert reservation.state == "consumed"
    assert (_qty(world, part, first), _qty(world, part, second)) == (3.0, 2.0)


def test_x22_the_job_line_carries_the_m15_issue_cost(world):
    part = _part(world, cost=100.0)
    _store(world, "NW", "non_warranty", part, 3.0, cost=275.0)
    line = _line(world)
    assert line.m15_consumption_id.sudo().unit_cost == 275.0
    assert line.unit_cost == 275.0
