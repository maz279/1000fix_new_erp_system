# A06 remediation follow-up - the M15 hand-offs: PO goods receipt -> M15
# ledger and inspection rejection -> quarantine (M15-9 / M16-7), an issue
# charged to a real job (M15-10), the replenishment requisition with no
# configured requester (M15-12) and the RTV credit handed to AP (M15-13).
import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, AccessError, ValidationError)
GR = "cd_requisition.group_fix_procurement_receiver"


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


@pytest.fixture
def po_world(inv):
    env = inv.env
    w = inv
    w.vendor = env["res.partner"].create({"name": "A06 PO Vendor " + inv.tag, "is_company": True})
    w.prod = env["product.product"].create({"name": "A06 Display (purchased) " + inv.tag})
    w.sprod = env["product.product"].create({"name": "A06 Board (purchased) " + inv.tag})
    w.other = env["product.product"].create({"name": "A06 Stationery " + inv.tag})
    inv.part.product_id = w.prod
    inv.spart.product_id = w.sprod
    w.po = env["fix.purchase.order"].create(
        {
            "operating_unit_id": inv.ou.id,
            "vendor_id": w.vendor.id,
            "line_ids": [
                (0, 0, {"product_id": w.prod.id, "qty_ordered": 5, "unit_price": 200.0}),
                (0, 0, {"product_id": w.sprod.id, "qty_ordered": 2, "unit_price": 8000.0}),
                (0, 0, {"product_id": w.other.id, "qty_ordered": 9, "unit_price": 10.0}),
            ],
        }
    )
    w.po.write({"state": "sent"})  # trusted setup: the PO has been approved and sent
    w.receiver = inv.user("receiver", GR)
    env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.po_receiving_location_id", str(inv.central.id)
    )
    return w


def _no_inspection(w):
    w.env["ir.config_parameter"].sudo().set_param("cd_requisition.receipt_inspection_required", "0")


def _receive(w, qty_by_product):
    lines = {
        line.id: qty_by_product[line.product_id]
        for line in w.po.line_ids
        if qty_by_product.get(line.product_id)
    }
    w.po.with_user(w.receiver).action_record_receipt(lines)
    return w.po.receipt_ids[:1]


# ------------------------------------------------ M15-9: PO receipt -> M15
def test_m15_09_po_receipt_posts_into_the_m15_ledger(po_world):
    """With inspection switched off. With it on, goods wait for it: see
    test_a06_final_m16_bridges.py."""
    w = po_world
    _no_inspection(w)
    grn = _receive(w, {w.prod: 3, w.other: 9})
    m15 = grn.stock_receipt_ids.filtered(lambda r: r.state == "posted")
    assert len(m15) == 1 and m15.purchase_order_id == w.po
    assert (m15.location_id, m15.source_ref, m15.line_ids.qty_accepted) == (
        w.central,
        grn.name,
        3.0,
    )
    assert m15.line_ids.part_id == w.part  # the stationery maps to no part: not stocked
    bucket = w.bucket(w.part, w.central)
    assert bucket.qty == 13.0
    assert bucket.unit_cost == pytest.approx((10 * 500 + 3 * 200) / 13, abs=1e-3)
    # the quantity is the PO's: an over-receipt is refused before anything moves
    refused(w, lambda: _receive(w, {w.prod: 3}), "outside")
    assert w.qty(w.part, w.central) == 13.0


def test_m15_09b_serialized_po_goods_wait_for_their_serials(po_world):
    w = po_world
    _no_inspection(w)
    grn = _receive(w, {w.sprod: 2})
    draft = grn.stock_receipt_ids
    assert draft.state == "draft" and len(draft.line_ids) == 2
    assert w.qty(w.spart, w.central) == 2.0  # nothing posted without serials
    for n, line in enumerate(draft.line_ids):
        line.with_user(w.keeper).write({"line_no": "PO-SN-%d-%s" % (n, w.tag)})
    draft.with_user(w.keeper).action_inspect()
    draft.with_user(w.keeper).action_post()
    assert w.qty(w.spart, w.central) == 4.0


def test_m15_09c_no_receiving_location_is_refused(po_world):
    w = po_world
    w.env["ir.config_parameter"].sudo().set_param("cd_inventory.po_receiving_location_id", "")
    try:
        with w.env.cr.savepoint():
            ou2 = w.env["operating.unit"].create(
                {
                    "name": "A06 OU-R " + w.tag,
                    "code": "R" + w.tag[:5],
                    "partner_id": w.env.company.partner_id.id,
                }
            )
    except Exception as exc:
        pytest.skip("could not create an operating unit: %s" % exc)
    w.po = w.env["fix.purchase.order"].create(
        {
            "operating_unit_id": ou2.id,
            "vendor_id": w.vendor.id,
            "line_ids": [(0, 0, {"product_id": w.prod.id, "qty_ordered": 5, "unit_price": 200.0})],
        }
    )
    w.po.write({"state": "sent"})
    w.receiver.write({"assigned_operating_unit_ids": [(4, ou2.id)]})
    refused(w, lambda: _receive(w, {w.prod: 1}), "no M15 receiving location")


def test_m16_07_rejected_goods_go_to_quarantine_once(po_world):
    """The consumer: goods already in available stock (inspection off, or a
    receipt posted before the hold). It now raises the draft RTV too."""
    w = po_world
    _no_inspection(w)
    grn = _receive(w, {w.prod: 3})
    consumer = w.env.ref("cd_inventory.consumer_inspection_rejected_quarantine")
    assert (consumer.event_type, consumer.method, consumer.active) == (
        "inspection.rejected",
        "consume_inspection_rejected",
        True,
    )
    event = {
        "event_type": "inspection.rejected",
        "aggregate": "fix.procurement.inspection",
        "aggregate_id": 987654,
        "payload": {
            "product_id": w.prod.id,
            "qty_rejected": 2.0,
            "receipt_ref": grn.name,
            "po_ref": w.po.name,
        },
    }
    Quarantine = w.env["fix.stock.quarantine"]
    assert Quarantine.consume_inspection_rejected(event) == 1
    assert Quarantine.consume_inspection_rejected(event) == 0  # idempotent
    assert w.qty(w.part, w.central) == 11.0
    assert w.qty(w.part, w.central, status="quarantine") == 2.0
    q = Quarantine.search([("source_ref", "=", "inspection.rejected:987654")])
    assert len(q) == 1 and q.state == "quarantined"
    rtv = w.env["fix.stock.rtv"].sudo().search([("quarantine_id", "=", q.id)])
    assert (rtv.state, rtv.qty, rtv.partner_id) == ("draft", 2.0, w.vendor)


def test_m16_07b_real_inspection_rejection_reaches_quarantine(po_world):
    w = po_world
    grn = _receive(w, {w.prod: 3})
    insp = (
        w.env["fix.procurement.inspection"]
        .with_user(w.receiver)
        .create({"receipt_line_id": grn.line_ids.id, "qty_accepted": 1})
    )
    insp.with_user(w.receiver).action_confirm()
    outbox = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "inspection.rejected"), ("aggregate_id", "=", insp.id)])
    )
    assert len(outbox) == 1
    # the confirmation itself settled it, held goods being within reach; the
    # event that still goes out for M42 and others moves nothing twice
    assert w.qty(w.part, w.central, status="quarantine") == 2.0
    assert w.qty(w.part, w.central) == 11.0
    assert (
        w.env["fix.stock.quarantine"].consume_inspection_rejected(outbox._relay_event_dict()) == 0
    )
    assert w.qty(w.part, w.central, status="quarantine") == 2.0


# ------------------------------------------------ M15-10: a real job
def test_m15_28_issue_needs_a_real_job(inv):
    rec = inv.issue(inv.keeper, service_order_ref="NO-SUCH-JOB-XYZ")
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "matches no")
    assert inv.qty(inv.part, inv.central) == 10.0
    ok = inv.issue(inv.keeper)
    ok.with_user(inv.keeper).action_scan_and_consume()
    assert (ok.job_model, ok.job_res_id) == ("fix.service.order", inv.job().id)
    refused(inv, lambda: ok.with_user(inv.keeper).write({"job_res_id": 1}), "workflow")


def test_m15_28b_unknown_work_order_refused(inv):
    rec = inv.issue(inv.keeper, work_order_ref="WO-NOPE-" + inv.tag)
    refused(inv, lambda: rec.with_user(inv.keeper).action_scan_and_consume(), "work order")


# ------------------------------------------------ M15-12: requester fallback
def _rule(inv, location, **kw):
    vals = {
        "spare_part_id": inv.part.id,
        "location_id": location.id,
        "branch_id": inv.branch().id,
        "operating_unit_id": inv.ou.id,
    }
    vals.update(kw)
    return inv.env["fix.reorder.rule"].with_user(inv.keeper).create(vals)


def test_m15_78b_van_rule_raises_in_the_custodians_name(inv):
    rule = _rule(inv, inv.van)
    rule.with_user(inv.keeper).action_trigger_reorder()
    assert rule.state == "ordered" and rule.requisition_id.requested_by == inv.tech1


def test_m15_78c_configured_default_then_branch_manager(inv):
    inv.env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.reorder_default_requester_id", str(inv.tech2.id)
    )
    rule = _rule(inv, inv.hub)
    rule.with_user(inv.keeper).action_trigger_reorder()
    assert rule.state == "ordered" and rule.requisition_id.requested_by == inv.tech2
    manager_user = inv.user("branchmgr")
    manager = inv.env["hr.employee"].create(
        {"name": "Branch Manager " + inv.tag, "user_id": manager_user.id}
    )
    inv.branch().manager_id = manager_user
    if "employee_manager_id" in inv.branch()._fields:
        inv.branch().employee_manager_id = manager
    rule2 = _rule(inv, inv.hub, spare_part_id=inv.spart.id)
    rule2.with_user(inv.keeper).action_trigger_reorder()
    assert rule2.requisition_id.requested_by == manager


# ------------------------------------------------ M15-13: credit to AP
def _bill(inv, amount):
    product = inv.env["product.product"].create({"name": "bill " + inv.tag})
    return inv.env["fix.vendor.invoice"].create(
        {
            "operating_unit_id": inv.ou.id,
            "vendor_id": inv.supplier.id,
            "invoice_ref": "BILL-" + inv.tag,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "description": "displays",
                        "quantity": 1,
                        "unit_price": amount,
                    },
                )
            ],
        }
    )


def _credited_rtv(inv, qty=2.0):
    r = inv.rtv(inv.keeper, qty=qty, rtv_ref="RMA-AP-" + inv.tag)
    r.with_user(inv.controller).action_approve()
    r.with_user(inv.keeper).action_ship()
    r.with_user(inv.keeper).action_mark_credited("MUSHAK-67-" + inv.tag)
    return r


def test_m15_67c_credited_rtv_without_a_grn_guesses_no_bill(inv):
    """E3-11 (owner decision 12 Nov 2026): the note used to land on "the
    vendor's latest bill with room", at average cost. An RTV that names no
    goods receipt now raises no note: AP credits the right bill by hand. The
    GRN-linked path (billed price, VAT, TDS) is test_e3_rtv_credit.py."""
    if "fix.vendor.note" not in inv.env:
        pytest.skip("cd_ap_ext is not installed")
    bill = _bill(inv, 5000.0)
    r = _credited_rtv(inv)
    assert r.state == "credited" and not r.vendor_note_res_id
    assert not bill.note_ids
    assert "names no goods receipt" in r.vendor_note_status


def test_m15_67d_no_bill_to_credit_is_recorded(inv):
    if "fix.vendor.note" not in inv.env:
        pytest.skip("cd_ap_ext is not installed")
    r = _credited_rtv(inv)
    assert r.state == "credited" and not r.vendor_note_res_id
    assert "no bill" in r.vendor_note_status
