"""A06 ERP audit (20 Nov 2026) X23/X24/A06, owner decision D3, on the workshop
bench: Reserve holds the part in M15 (and Release gives it back), an M15 part
never leaves through an Odoo stock move, and a warranty job draws from the
warranty store. Uses the A02 M31 fixture; `odoo_env` rolls back."""

from odoo.exceptions import UserError

from . import test_a02_p0_m31 as a02
from .test_a06_m15_workshop_issue import _bucket_qty, _job_in_repair, _m15

m31 = a02.m31
refused, _line = a02.refused, a02._line


def test_x23_reserve_holds_the_part_in_m15_and_release_gives_it_back(m31):
    part, store = _m15(m31)
    job = _job_in_repair(m31)
    line = _line(m31, job, qty=2.0, cost=400.0)
    line.action_reserve()
    held = line.m15_reservation_id
    assert held.state == "active" and held.location_id == store and held.qty == 2.0
    m31.env.invalidate_all()
    bucket = m31.env["fix.stock.onhand"]._bucket(part, store, "owned")
    assert (bucket.qty, bucket.reserved) == (5.0, 2.0)
    line.action_release_reservation()
    assert held.state == "released"
    m31.env.invalidate_all()
    assert m31.env["fix.stock.onhand"]._bucket(part, store, "owned").reserved == 0.0


def test_x23_the_fit_draws_the_lines_own_reservation(m31):
    part, store = _m15(m31, qty=2.0)
    job = _job_in_repair(m31)
    line = _line(m31, job, qty=2.0, cost=400.0)
    line.action_reserve()
    line.action_consume_part()
    assert line.m15_consumption_id.reservation_id == line.m15_reservation_id
    assert line.m15_reservation_id.state == "consumed"
    assert _bucket_qty(m31, part, store) == 0.0


def test_x24_an_m15_part_never_leaves_through_an_odoo_move(m31):
    part, store = _m15(m31)
    odoo_store = m31.env.ref("stock.stock_location_stock")
    m31.workshop.write({"stock_location_id": odoo_store.id})
    m31.product.sudo().write({"type": "consu"})
    job = _job_in_repair(m31)
    line = _line(m31, job, qty=1.0, cost=400.0)
    line.action_reserve()
    line.action_consume_part()
    assert not line.stock_move_id
    assert line.m15_consumption_id.location_id == store
    assert _bucket_qty(m31, part, store) == 4.0


def test_d3_a_warranty_bench_job_needs_a_warranty_store(m31):
    part, store = _m15(m31)
    job = _job_in_repair(m31)
    m31.env.flush_all()
    m31.env.cr.execute(
        "UPDATE fix_service_order SET order_category = 'warranty' WHERE id = %s",
        [job.order_id.id],
    )
    job.order_id.invalidate_recordset(["order_category"])
    line = _line(m31, job, qty=1.0, cost=400.0)
    with refused(m31.env, UserError, ""):
        line.action_consume_part()
    wstore = m31.env["fix.stock.location"].create(
        {
            "name": "A06 Workshop Warranty Store",
            "code": "A6WW-%s" % m31.workshop.id,
            "location_type": "branch",
            "stock_type": "warranty",
            "branch_id": store.branch_id.id,
            "operating_unit_id": store.operating_unit_id.id,
        }
    )
    m31.env["fix.stock.onhand"]._apply(part, wstore, "owned", 1.0, 400.0)
    line.action_consume_part()
    assert line.m15_consumption_id.location_id == wstore
    assert _bucket_qty(m31, part, store) == 5.0
