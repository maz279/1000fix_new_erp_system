# A06 final pass, M16-7 / BRU-PRO-11 and -16: goods wait for their inspection.
#
# A PO receipt used to put plain parts into available stock at once, so a later
# rejection moved only what was still there, and nothing if it had been issued;
# serialized parts were skipped. Now goods sit in a held status, or on their draft
# M15 receipt, until the inspection is confirmed, and a rejection raises a draft RTV.
import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, AccessError, ValidationError)
GR = "cd_requisition.group_fix_procurement_receiver"
PARAM_INSPECTION = "cd_requisition.receipt_inspection_required"


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


@pytest.fixture
def w(inv):
    env = inv.env
    inv.vendor = env["res.partner"].create(
        {"name": "A06F PO Vendor " + inv.tag, "is_company": True}
    )
    inv.prod = env["product.product"].create({"name": "A06F Display " + inv.tag})
    inv.sprod = env["product.product"].create({"name": "A06F Board " + inv.tag})
    inv.other = env["product.product"].create({"name": "A06F Stationery " + inv.tag})
    inv.part.product_id = inv.prod
    inv.spart.product_id = inv.sprod
    inv.po = env["fix.purchase.order"].create(
        {
            "operating_unit_id": inv.ou.id,
            "vendor_id": inv.vendor.id,
            "line_ids": [
                (0, 0, {"product_id": inv.prod.id, "qty_ordered": 5, "unit_price": 200.0}),
                (0, 0, {"product_id": inv.sprod.id, "qty_ordered": 3, "unit_price": 8000.0}),
                (0, 0, {"product_id": inv.other.id, "qty_ordered": 9, "unit_price": 10.0}),
            ],
        }
    )
    inv.po.write({"state": "sent"})  # trusted setup: approved and sent
    inv.receiver = inv.user("receiver", GR)
    env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.po_receiving_location_id", str(inv.central.id)
    )
    return inv


def receive(w, qty_by_product):
    lines = {
        line.id: qty_by_product[line.product_id]
        for line in w.po.line_ids
        if qty_by_product.get(line.product_id)
    }
    w.po.with_user(w.receiver).action_record_receipt(lines)
    return w.po.receipt_ids.sorted("id")[-1]


def inspect(w, grn, product, accepted):
    line = grn.line_ids.filtered(lambda ln: ln.product_id == product)
    rec = (
        w.env["fix.procurement.inspection"]
        .with_user(w.receiver)
        .create({"receipt_line_id": line.id, "qty_accepted": accepted})
    )
    rec.with_user(w.receiver).action_confirm()
    return rec


def rtvs(w):
    return w.env["fix.stock.rtv"].sudo().search([("partner_id", "=", w.vendor.id)])


# --------------------------------------------------------- B1: plain parts
def test_b1_received_goods_are_held_and_cannot_be_issued(w):
    grn = receive(w, {w.prod: 3})
    m15 = grn.stock_receipt_ids
    assert m15.state == "posted" and m15.inspection_held
    assert w.qty(w.part, w.central) == 10.0  # available stock did not move
    assert w.qty(w.part, w.central, status="inspection") == 3.0
    # the stock on hand was all there is: asking for more than it is refused
    Onhand = w.env["fix.stock.onhand"]
    refused(w, lambda: Onhand._fix_reserve(w.part, w.central, "owned", 11, "attack"), "only 10")
    assert not m15.line_ids.quarantine_id


def test_b1_full_acceptance_releases_into_available(w):
    grn = receive(w, {w.prod: 3})
    inspect(w, grn, w.prod, 3)
    assert w.qty(w.part, w.central) == 13.0
    assert w.qty(w.part, w.central, status="inspection") == 0.0
    assert w.bucket(w.part, w.central).unit_cost == pytest.approx(
        (10 * 500 + 3 * 200) / 13, abs=1e-3
    )
    assert not rtvs(w)


def test_b1_partial_rejection_splits_and_the_value_is_kept(w):
    grn = receive(w, {w.prod: 3})
    inspect(w, grn, w.prod, 1)
    assert w.qty(w.part, w.central) == 11.0
    assert w.qty(w.part, w.central, status="inspection") == 0.0
    assert w.qty(w.part, w.central, status="quarantine") == 2.0
    assert w.bucket(w.part, w.central, status="quarantine").unit_cost == pytest.approx(200.0)
    line = grn.stock_receipt_ids.line_ids
    assert line.qty_accepted == 1.0 and line.qty_rejected == 2.0 and line.quarantine_id


def test_b1_full_rejection_moves_all_of_it_even_with_nothing_available(w):
    """The audit's case: the rejected goods could already have been issued, and the
    old move then took nothing, silently. Available stock is gone; the held goods
    are not, because nobody could reach them."""
    grn = receive(w, {w.prod: 3})
    bucket = w.bucket(w.part, w.central)
    bucket.sudo().write({"qty": 0.0})
    inspect(w, grn, w.prod, 0)
    assert w.qty(w.part, w.central) == 0.0
    assert w.qty(w.part, w.central, status="quarantine") == 3.0
    assert w.qty(w.part, w.central, status="inspection") == 0.0


def test_b1_two_receipts_settle_independently(w):
    first = receive(w, {w.prod: 2})
    second = receive(w, {w.prod: 3})
    assert w.qty(w.part, w.central, status="inspection") == 5.0
    inspect(w, first, w.prod, 2)
    assert w.qty(w.part, w.central, status="inspection") == 3.0
    assert w.qty(w.part, w.central) == 12.0
    inspect(w, second, w.prod, 0)
    assert w.qty(w.part, w.central, status="quarantine") == 3.0


def test_b1_no_second_settlement(w):
    grn = receive(w, {w.prod: 3})
    done = inspect(w, grn, w.prod, 3)
    refused(w, lambda: done.with_user(w.receiver).action_confirm(), "draft inspection")
    second = (
        w.env["fix.procurement.inspection"]
        .with_user(w.receiver)
        .create({"receipt_line_id": grn.line_ids.id, "qty_accepted": 0})
    )
    refused(w, lambda: second.with_user(w.receiver).action_confirm(), "already has")
    assert w.qty(w.part, w.central) == 13.0


def test_b1_the_consumer_does_not_move_it_again(w):
    grn = receive(w, {w.prod: 3})
    insp = inspect(w, grn, w.prod, 1)
    outbox = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "inspection.rejected"), ("aggregate_id", "=", insp.id)])
    )
    assert len(outbox) == 1
    Quarantine = w.env["fix.stock.quarantine"]
    assert Quarantine.consume_inspection_rejected(outbox._relay_event_dict()) == 0
    assert w.qty(w.part, w.central) == 11.0
    assert w.qty(w.part, w.central, status="quarantine") == 2.0
    assert len(rtvs(w)) == 1


def test_b1_inspection_not_required_is_available_at_once_as_before(w):
    w.env["ir.config_parameter"].sudo().set_param(PARAM_INSPECTION, "0")
    grn = receive(w, {w.prod: 3})
    assert not grn.stock_receipt_ids.inspection_held
    assert w.qty(w.part, w.central) == 13.0
    assert w.qty(w.part, w.central, status="inspection") == 0.0


def test_b1_a_receipt_posted_before_this_rule_keeps_the_old_path(w):
    """fix_dev holds receipts whose goods are already unrestricted: confirming their
    inspection must not look for held stock, and the consumer still quarantines."""
    w.env["ir.config_parameter"].sudo().set_param(PARAM_INSPECTION, "0")
    grn = receive(w, {w.prod: 3})
    grn.line_ids._guarded().write({"inspection_required": True})
    insp = inspect(w, grn, w.prod, 1)  # no held stock: nothing moves synchronously
    assert w.qty(w.part, w.central) == 13.0
    outbox = (
        w.env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", "inspection.rejected"), ("aggregate_id", "=", insp.id)])
    )
    Quarantine = w.env["fix.stock.quarantine"]
    assert Quarantine.consume_inspection_rejected(outbox._relay_event_dict()) == 1
    assert Quarantine.consume_inspection_rejected(outbox._relay_event_dict()) == 0
    assert w.qty(w.part, w.central) == 11.0
    assert w.qty(w.part, w.central, status="quarantine") == 2.0
    assert rtvs(w).quarantine_id.source_ref == "inspection.rejected:%d" % insp.id


# --------------------------------------------------------- B1: serialized parts
def test_b1_serialized_goods_cannot_be_posted_before_inspection(w):
    grn = receive(w, {w.sprod: 2})
    draft = grn.stock_receipt_ids
    assert draft.state == "draft" and len(draft.line_ids) == 2
    for n, line in enumerate(draft.line_ids):
        line.with_user(w.keeper).write({"line_no": "F-SN-%d-%s" % (n, w.tag)})
    refused(w, lambda: draft.with_user(w.keeper).action_inspect(), "BRU-PRO-11")
    assert w.qty(w.spart, w.central) == 2.0
    inspect(w, grn, w.sprod, 2)
    draft.with_user(w.keeper).action_inspect()
    draft.with_user(w.keeper).action_post()
    assert w.qty(w.spart, w.central) == 4.0
    assert not rtvs(w)


def test_b1_rejected_serialized_units_leave_the_receipt_and_are_quarantined(w):
    grn = receive(w, {w.sprod: 3})
    draft = grn.stock_receipt_ids
    named = draft.line_ids[:1]
    named.with_user(w.keeper).write({"line_no": "F-SN-KEEP-%s" % w.tag})
    inspect(w, grn, w.sprod, 1)
    assert draft.line_ids == named  # units with no serial yet are the ones taken
    assert w.qty(w.spart, w.central, status="quarantine") == 2.0
    assert w.bucket(w.spart, w.central, status="quarantine").unit_cost == pytest.approx(8000.0)
    rtv = rtvs(w)
    assert (rtv.state, rtv.qty, rtv.part_id) == ("draft", 2.0, w.spart)
    draft.with_user(w.keeper).action_inspect()
    draft.with_user(w.keeper).action_post()
    assert w.qty(w.spart, w.central) == 3.0


def test_b1_a_fully_rejected_serialized_receipt_leaves_no_draft_to_post(w):
    grn = receive(w, {w.sprod: 2})
    inspect(w, grn, w.sprod, 0)
    assert not grn.stock_receipt_ids
    assert w.qty(w.spart, w.central) == 2.0
    assert w.qty(w.spart, w.central, status="quarantine") == 2.0


# --------------------------------------------------------- B2: the draft RTV
def test_b2_a_rejection_raises_a_draft_rtv_a_controller_can_carry_through(w):
    grn = receive(w, {w.prod: 3})
    inspect(w, grn, w.prod, 1)
    rtv = rtvs(w)
    assert (rtv.state, rtv.qty, rtv.part_id, rtv.location_id) == ("draft", 2.0, w.part, w.central)
    assert rtv.quarantine_id.state == "quarantined" and rtv.quarantine_id.qty == 2.0
    assert rtv.reason == "quality"
    rtv.with_user(w.keeper).action_submit()
    assert rtv.state == "submitted"


def test_b2_acceptance_raises_none_and_unmapped_goods_have_nothing_to_return(w):
    grn = receive(w, {w.prod: 3, w.other: 9})
    inspect(w, grn, w.prod, 3)
    inspect(w, grn, w.other, 0)  # stationery maps to no spare part: no M15 stock
    assert not rtvs(w)
    line = grn.line_ids.filtered(lambda ln: ln.product_id == w.other)
    assert line.inspection_state == "failed"  # the match still sees the rejection
