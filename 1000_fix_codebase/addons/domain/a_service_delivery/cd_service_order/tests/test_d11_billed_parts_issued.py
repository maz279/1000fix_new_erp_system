# D-11 (E2E rehearsal on a fix_real copy, 11 Nov 2026): two orders billed a
# RAM on their approved estimates, were delivered, closed and invoiced, and
# the RAM never left stock — nobody recorded a work-order part line and the
# close checked nothing. On-hand was unchanged by the sale.
#
# The close is the estate's commercial point (the billing engine invoices a
# closed order), so the close gate now refuses an order whose approved
# estimate bills a stocked part that no M15 issue for this order covers,
# naming the part, the quantity billed and the quantity issued. A part that
# is not stocked (a service, or a product with no M15 spare-part record) is
# exempt. A part comes off the ledger only through the normal issue path
# (work-order / workshop / field part line, or an M15 issue against the job),
# so its serial, location and quarantine rules all still apply.
#
# Every step runs as the non-admin users of the shared M01 fixture.
# ruff: noqa: F811 - `w` is the shared M01 fixture of test_a02_p0_m01.
import pytest
from odoo import Command
from odoo.addons.cd_service_order.tests.test_a02_p0_m01 import (  # noqa: F401 (fixtures)
    attempt,
    handover_evidence,
    order,
    w,
)

_N = iter(range(1, 10_000))


@pytest.fixture
def d11(w):
    env = w.env
    n = next(_N)
    ou = w.branch.operating_unit_id
    entity = w.branch.entity_id
    w.store_branch = env["fix.branch"].create(
        {
            "name": "D11 Branch %s" % n,
            "code": "D11B%s" % n,
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    w.store = env["fix.stock.location"].create(
        {
            "name": "D11 Store %s" % n,
            "code": "D11S%s" % n,
            "location_type": "branch",
            "branch_id": w.store_branch.id,
        }
    )
    w.ram_product = env["product.product"].create(
        {"name": "D11 RAM 8GB %s" % n, "default_code": "D11RAM%s" % n, "list_price": 1000.0}
    )
    w.ram = env["fix.spare.part"].create(
        {
            "name": "D11 RAM 8GB %s" % n,
            "part_number": "D11RAM%s" % n,
            "unit_cost": 700.0,
            "product_id": w.ram_product.id,
        }
    )
    env["fix.stock.onhand"]._apply(w.ram, w.store, "owned", 5.0, 700.0)
    w.tech = env["hr.employee"].create({"name": "D11 Tech %s" % n})
    return w


def _onhand(w):
    w.env.invalidate_all()
    row = w.env["fix.stock.onhand"]._bucket(w.ram, w.store, "owned")
    return row.qty if row else 0.0


def _estimate(w, o, lines):
    est = (
        w.env["fix.estimate"]
        .with_user(w.clerk)
        .create(
            {
                "order_id": o.id,
                "line_ids": [Command.create(dict(line)) for line in lines],
            }
        )
    )
    est.action_send()
    est.with_user(w.clerk2).action_approve()
    return est


def _part_line(w, qty=1.0, product=None):
    product = product or w.ram_product
    return {
        "line_type": "part",
        "product_id": product.id,
        "description": product.name,
        "quantity": qty,
        "unit_price": product.lst_price,
    }


LABOUR = {"line_type": "labour", "description": "bench labour", "quantity": 1, "unit_price": 500.0}


def _delivered(w, lines):
    """Diagnosis -> estimate (with these lines) approved -> repair -> QC ->
    ready -> paid at the counter -> handed over. Returns the order."""
    o = order(w, branch_id=w.store_branch.id)
    o.action_intake()
    o.action_start_diagnostic()
    o.action_request_estimate()
    est = _estimate(w, o, lines)
    assert o.state == "approved"
    o.action_start_repair()
    o.action_submit_qc()
    qc = (
        w.env["fix.qc.checklist"]
        .with_user(w.clerk)
        .create(
            {"order_id": o.id, "item_ids": [Command.create({"name": "power on", "passed": True})]}
        )
    )
    qc.with_user(w.inspector).action_complete()
    o.action_ready()
    o.with_user(w.cashier).action_mark_settled("POS-D11-%s" % o.id, est.grand_total, tender="cash")
    handover_evidence(w, o)
    o.with_user(w.clerk).action_deliver()
    assert o.state == "delivered"
    return o


def _fit(w, o, qty=1.0, product=None):
    """The technician records the part fitted on a work order: the normal
    M15 issue (branch store, no van)."""
    WorkOrder = w.env["fix.work.order"]
    wo = WorkOrder.search([("order_id", "=", o.id)], limit=1)
    if not wo:
        vals = {"order_id": o.id, "technician_id": w.tech.id, "sequence": 1}
        if "certification_waiver" in WorkOrder._fields:
            # M22's competency gate is not under test here (cd_competency)
            vals["certification_waiver"] = True
        wo = WorkOrder.create(vals)
    return w.env["fix.work.order.part"].create(
        {
            "work_order_id": wo.id,
            "product_id": (product or w.ram_product).id,
            "quantity": qty,
        }
    )


def test_d11_close_refuses_a_billed_part_never_issued_and_names_it(d11):
    w = d11
    o = _delivered(w, [_part_line(w), LABOUR])
    msg = attempt(w, lambda: o.with_user(w.clerk).action_close()) or ""
    assert w.ram.part_number in msg and "billed 1" in msg and "issued 0" in msg
    assert o.state == "delivered" and _onhand(w) == 5.0
    # the technician records the RAM fitted: it leaves the store, the order closes
    line = _fit(w, o)
    assert line.m15_consumption_id.state == "consumed"
    assert line.m15_consumption_id.location_id == w.store
    assert _onhand(w) == 4.0
    o.with_user(w.clerk).action_close()
    assert o.state == "closed"


def test_d11_a_partial_issue_is_refused_with_the_shortfall(d11):
    w = d11
    o = _delivered(w, [_part_line(w, qty=2.0)])
    _fit(w, o, qty=1.0)
    msg = attempt(w, lambda: o.with_user(w.clerk).action_close()) or ""
    assert "billed 2" in msg and "issued 1" in msg
    _fit(w, o, qty=1.0)
    o.with_user(w.clerk).action_close()
    assert o.state == "closed" and _onhand(w) == 3.0


def test_d11_a_returned_issue_does_not_count(d11):
    w = d11
    o = _delivered(w, [_part_line(w)])
    issue = _fit(w, o).m15_consumption_id
    issue.sudo().action_return_part(reason="wrong_diagnosis")
    assert issue.state == "returned" and _onhand(w) == 5.0
    msg = attempt(w, lambda: o.with_user(w.clerk).action_close()) or ""
    assert "issued 0" in msg and o.state == "delivered"


def test_d11_another_orders_issue_does_not_count(d11):
    w = d11
    mine = _delivered(w, [_part_line(w)])
    other = _delivered(w, [_part_line(w)])
    _fit(w, other)
    assert attempt(w, lambda: mine.with_user(w.clerk).action_close())
    other.with_user(w.clerk).action_close()
    assert (mine.state, other.state) == ("delivered", "closed")


def test_d11_an_m15_issue_against_the_job_counts(d11):
    """Any normal issue path counts, not only the work-order part line: an
    M15 issue the storekeeper scans against the service order."""
    w = d11
    o = _delivered(w, [_part_line(w)])
    issue = (
        w.env["fix.stock.consumption"]
        .sudo()
        .create(
            {
                "service_order_ref": o.name,
                "product_id": w.ram.id,
                "location_id": w.store.id,
                "technician_id": w.tech.id,
                "quantity": 1.0,
                "scanned_code": w.ram.part_number,
            }
        )
    )
    issue.action_scan_and_consume()
    o.with_user(w.clerk).action_close()
    assert o.state == "closed" and _onhand(w) == 4.0


def test_d11_unstocked_lines_are_exempt(d11):
    """A service product, a product with no spare-part record and a free-text
    part line are not stock: they need no issue."""
    w = d11
    service = w.env["product.product"].create(
        {"name": "D11 cleaning", "list_price": 200.0, "type": "service"}
    )
    loose = w.env["product.product"].create({"name": "D11 screw kit", "list_price": 50.0})
    # Commercial document standard (17 Nov 2026): a service product is billed
    # on a charge line - a part line refuses a non-stock item.
    o = _delivered(
        w,
        [
            dict(_part_line(w, product=service), line_type="service"),
            _part_line(w, product=loose),
            {"line_type": "part", "description": "thermal paste", "quantity": 1, "unit_price": 30},
            LABOUR,
        ],
    )
    o.with_user(w.clerk).action_close()
    assert o.state == "closed" and _onhand(w) == 5.0


def test_d11_the_shortfall_is_readable_before_the_close(d11):
    w = d11
    o = _delivered(w, [_part_line(w, qty=2.0)])
    _fit(w, o, qty=1.0)
    gaps = o._fix_unissued_billed_parts()
    assert [(g["part"], g["billed"], g["issued"]) for g in gaps] == [(w.ram, 2.0, 1.0)]
