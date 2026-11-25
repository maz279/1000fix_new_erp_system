"""A06 workflow audit M15-10: a part fitted on the workshop bench is issued
from the M15 spare-parts ledger.

The audit found that workshop part lines never called M15. A product that is
an M15 spare part (fix.spare.part.product_id) and is not carried by an Odoo
stock move is now issued from the workshop's M15 store when the line is
consumed: the bucket goes down at average cost, the issue names the job, and
the line keeps the issue. Uses the A02 M31 fixture; `odoo_env` rolls back.
"""

from odoo.exceptions import UserError

from . import test_a02_p0_m31 as a02

m31 = a02.m31
refused, _to_repair, _approved_estimate, _line = (
    a02.refused,
    a02._to_repair,
    a02._approved_estimate,
    a02._line,
)


def _m15(m, qty=5.0, cost=400.0):
    """Map the fixture's spare product to an M15 part and stock the
    workshop's branch store."""
    env = m.env
    branch = m.order().branch_id
    part = env["fix.spare.part"].create(
        {
            "name": "A06 bench part",
            "part_number": "A6WS-%s" % m.product.id,
            "unit_cost": cost,
            "product_id": m.product.id,
        }
    )
    store = env["fix.stock.location"].create(
        {
            "name": "A06 Workshop Store",
            "code": "A6WS-%s" % m.workshop.id,
            "location_type": "branch",
            "branch_id": branch.id,
            "operating_unit_id": branch.operating_unit_id.id,
        }
    )
    m.workshop.write({"branch_id": branch.id})
    env["fix.stock.onhand"]._apply(part, store, "owned", qty, cost)
    return part, store


def _bucket_qty(m, part, store):
    m.env.invalidate_all()
    row = m.env["fix.stock.onhand"]._bucket(part, store, "owned")
    return row.qty if row else 0.0


def _job_in_repair(m):
    so = m.order()
    _approved_estimate(m, so, 30000.0)
    return _to_repair(m, m.job(so=so))


def test_m15_10_a_fitted_part_is_issued_from_m15(m31):
    part, store = _m15(m31)
    job = _job_in_repair(m31)
    line = _line(m31, job, qty=2.0, cost=400.0)
    line.action_consume_part()
    issue = line.m15_consumption_id
    assert issue and issue.state == "consumed"
    assert (issue.product_id, issue.location_id, issue.quantity) == (part, store, 2.0)
    assert (issue.job_model, issue.job_res_id) == ("fix.workshop.job", job.id)
    assert line.consumption_ref == issue.name and line.reservation_state == "consumed"
    assert _bucket_qty(m31, part, store) == 3.0


def test_m15_10_not_enough_m15_stock_refuses_the_fit(m31):
    part, store = _m15(m31, qty=1.0)
    job = _job_in_repair(m31)
    line = _line(m31, job, qty=2.0, cost=400.0)
    with refused(m31.env, UserError, ""):
        line.action_consume_part()
    assert _bucket_qty(m31, part, store) == 1.0


def test_m15_10_a_workshop_with_no_m15_store_refuses_a_mapped_part(m31):
    m31.env["fix.spare.part"].create(
        {
            "name": "A06 bench part (no store)",
            "part_number": "A6WS-NS-%s" % m31.product.id,
            "unit_cost": 400.0,
            "product_id": m31.product.id,
        }
    )
    job = _job_in_repair(m31)
    line = _line(m31, job, qty=1.0, cost=400.0)
    with refused(m31.env, UserError, "no M15 parts store"):
        line.action_consume_part()


def test_m15_10_the_switch_refuses_a_product_that_is_not_an_m15_part(m31):
    job = _job_in_repair(m31)
    line = _line(m31, job, qty=1.0, cost=400.0)
    m31.env["ir.config_parameter"].sudo().set_param("cd_workshop.m15_issue_required", "1")
    with refused(m31.env, UserError, "is not an M15 spare part"):
        line.action_consume_part()
    m31.env["ir.config_parameter"].sudo().set_param("cd_workshop.m15_issue_required", "0")
    line.action_consume_part()
    assert line.reservation_state == "consumed" and not line.m15_consumption_id


def test_m15_10_the_issue_link_cannot_be_typed(m31):
    _part, _store = _m15(m31)
    job = _job_in_repair(m31)
    line = _line(m31, job, qty=1.0, cost=400.0)
    other = m31.env["fix.stock.consumption"].search([], limit=1)
    if other:
        with refused(m31.env, UserError, "changes only through its workflow"):
            line.with_user(m31.tech).write({"m15_consumption_id": other.id})


def test_m15_10_a_serialized_part_is_fitted_one_unit_per_line(m31):
    part, _store = _m15(m31)
    part.sudo().write({"is_serialized": True})
    job = _job_in_repair(m31)
    line = _line(m31, job, qty=2.0, cost=400.0)
    with refused(m31.env, UserError, "one unit per part line"):
        line.action_consume_part()


def test_m15_10_an_unused_part_goes_back_to_m15(m31):
    part, store = _m15(m31)
    job = _job_in_repair(m31)
    line = _line(m31, job, qty=2.0, cost=400.0)
    line.action_consume_part()
    assert _bucket_qty(m31, part, store) == 3.0
    with refused(m31.env, UserError, "return reason"):
        line.action_return_to_m15(reason="not-a-reason")
    line.action_return_to_m15(reason="wrong_diagnosis")
    assert line.m15_consumption_id.state != "consumed"
    assert line.reservation_state == "released"
    assert _bucket_qty(m31, part, store) == 5.0
    with refused(m31.env, UserError, "no M15 issue to return"):
        line.action_return_to_m15(reason="wrong_diagnosis")
