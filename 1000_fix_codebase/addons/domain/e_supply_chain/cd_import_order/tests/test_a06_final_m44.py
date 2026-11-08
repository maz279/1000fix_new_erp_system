"""A06 final pass, M44: the controls and reachability a fresh audit found open.

Each test attacks the control as a non-admin with the real role and asserts the
refusal, then runs the proper path. Live ORM inside the rolled-back odoo_env.
Fixtures and stage helpers come from test_a06_m44_controls. Rates and amounts
are test inputs; no statutory figure is asserted.
"""

from __future__ import annotations

from datetime import timedelta
from unittest import mock

import pytest
from odoo.addons.cd_import_order.tests.test_a06_m44_controls import (
    APPROVER as APPROVER_ROLE,
)
from odoo.addons.cd_import_order.tests.test_a06_m44_controls import (
    FX,
    TIER4,
    _bucket,
    _net,
    _refused,
    _user,
    arrival,
    assess_and_pay,
    boe,
    landed,
    lc,
    lca,
    proforma,
    shipdoc,
    stage_advance,
    stage_cleared,
    stage_lc_applied,
    stage_lc_open,
    stage_proforma,
    stage_received,
    stage_shipped,
)
from odoo.addons.cd_import_order.tests.test_a06_m44_controls import (
    OFFICER as OFFICER_ROLE,
)
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a06 import m44 as m44_ctl
from odoo.addons.cd_requisition.models.fix_requisition import GROUP_RECEIVER


def _usd_lc(c, **kw):
    """An opened LC in the order currency."""
    stage_proforma(c)
    vals = {"amount": 1000.0, "currency_id": c.usd.id, "lc_no": "LCUSD-%s" % c.tag}
    vals.update(kw)
    letter = lc(c, **vals)
    lca(c, letter).with_user(c.approver).action_approve()
    letter.with_user(c.officer).action_apply()
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    approve_via_inbox(letter, c.approver, requester=c.officer, justification="USD LC")
    letter.with_user(c.officer).action_open()
    return letter


def _assessed_with_variance(c, extra=500.0):
    stage_shipped(c)
    bill = boe(c)
    bill.with_user(c.officer).action_assess()
    bill.with_user(c.officer2).write(
        {"customs_assessed_total": bill.total_tax + extra, "payment_ref": "CH-%s" % c.tag}
    )
    return bill


def _form(c, user, model, fields, lines=None, record_id=None):
    method = api.P03GenericApiController.model_form
    method = getattr(method, "original_endpoint", method)
    with mock.patch.object(api, "request", mock.Mock(env=c.env(user=user.id))):
        return method(
            api.P03GenericApiController(),
            model=model,
            fields=fields,
            lines=lines,
            record_id=record_id,
        )


# ================================================================ A2 buttons
def test_a2_reject_and_suspend_need_their_reason_through_p03(c, p03):
    pf = proforma(c)
    p03.as_user(c.approver)
    out = p03.action(model="fix.import.proforma", ids=[pf.id], method="action_reject")
    assert not out["success"] and "why" in out["error"].lower()
    out = p03.action(
        model="fix.import.proforma",
        ids=[pf.id],
        method="action_reject",
        kwargs={"reason": "Wrong beneficiary"},
    )
    assert out["success"], out
    assert pf.state == "rejected" and pf.rejection_reason == "Wrong beneficiary"

    letter = lc(c)
    auth = lca(c, letter)
    _refused(auth.with_user(c.approver).action_reject, match="why")
    auth.with_user(c.approver).action_reject("Bank declined")
    assert auth.state == "rejected" and auth.rejection_reason == "Bank declined"

    _refused(c.irc.with_user(c.approver).action_suspend, match="why")
    c.irc.with_user(c.approver).action_suspend("Under NBR review")
    assert c.irc.state == "suspended" and c.irc.suspension_reason == "Under NBR review"


def test_a2_agent_block_through_p03_with_reason(c, p03):
    p03.as_user(c.approver)
    out = p03.action(model="fix.import.cnf.agent", ids=[c.agent.id], method="action_block")
    assert not out["success"]
    out = p03.action(
        model="fix.import.cnf.agent",
        ids=[c.agent.id],
        method="action_block",
        kwargs={"reason": "Licence under query"},
    )
    assert out["success"] and c.agent.state == "blocked", out


def test_a2_arrival_takes_the_typed_date_and_refuses_a_bad_one(c, p03):
    stage_shipped(c)
    arr = arrival(c, etd=c.today - timedelta(days=20))
    day = c.today - timedelta(days=3)
    p03.as_user(c.officer)
    out = p03.action(
        model="fix.import.arrival",
        ids=[arr.id],
        method="action_arrive",
        kwargs={"arrival_date": "banana"},
    )
    assert not out["success"] and "not a date" in out["error"]
    out = p03.action(
        model="fix.import.arrival",
        ids=[arr.id],
        method="action_arrive",
        kwargs={"arrival_date": str(day)},
    )
    assert out["success"] and arr.arrival_date == day, out


# ================================================================ A3 picker
def test_a3_order_line_names_its_order_and_other_orders_line_refused_at_save(c):
    line = c.order.line_ids[0]
    assert line.display_name.startswith(c.order.name)
    assert "fix.import.order.line," not in line.display_name
    found = c.env["fix.import.order.line"].name_search(c.part.name, limit=5)
    assert line.id in [i for i, _label in found]
    other = (
        c.env["fix.import.order"]
        .with_user(c.officer)
        .create(
            {
                "name": "M44T-OTHER-%s" % c.tag,
                "supplier_id": c.supplier.id,
                "operating_unit_id": c.ou.id,
                "currency_id": c.usd.id,
                "fob_value": 600.0,
                "fx_rate": FX,
                "line_ids": [
                    (
                        0,
                        0,
                        {"part_id": c.part.id, "hs_id": c.hs.id, "quantity": 1, "unit_price": 600},
                    )
                ],
            }
        )
    )
    _refused(
        lambda: boe(
            c,
            lines=[(0, 0, {"order_line_id": other.line_ids.id, "quantity": 1})],
            boe_no="BE-X-%s" % c.tag,
        ),
        match="not a line of import order",
    )


# ================================================================ A4 allocation
def test_a4_weight_is_gone_and_the_allocation_is_on_the_form(c):
    with pytest.raises(ValueError), c.env.cr.savepoint():
        landed(c, allocation_method="weight")
    stage_received(c)
    sheet = landed(c)
    sheet.with_user(c.approver).action_finalise()
    assert len(sheet.line_ids) == 2
    fields = [{"name": "order_id"}, {"name": "allocation_method"}]
    grid = {
        "field": "line_ids",
        "fields": [{"name": n} for n in ("part_id", "quantity", "basis", "amount", "unit_amount")],
    }
    out = _form(c, c.officer, "fix.import.landed", fields, lines=grid, record_id=sheet.id)
    assert "error" not in out, out
    rows = out["lines"]["rows"]
    assert len(rows) == 2 and sum(r["amount"] for r in rows) == pytest.approx(sheet.total_landed)
    choices = [
        ch["key"] for f in out["fields"] if f["name"] == "allocation_method" for ch in f["choices"]
    ]
    assert "weight" not in choices


# ================================================================ B1 variance
def test_b1_variance_refused_for_finance_until_accepted(c):
    bill = _assessed_with_variance(c)
    _refused(bill.with_user(c.finance).action_pay, match="variance")
    _refused(bill.with_user(c.officer).action_accept_variance, "x", match="role")
    _refused(bill.with_user(c.finance).action_accept_variance, "x", match="role")
    _refused(bill.with_user(c.approver).action_accept_variance, match="why")
    assert not bill.variance_accepted_by_id


def test_b1_assessor_or_typist_cannot_accept(c):
    both = _user(
        c.env,
        "m44f_both_%s" % c.tag,
        c.ou,
        "cd_import_order.group_fix_import_officer",
        "cd_import_order.group_fix_import_approver",
    )
    stage_shipped(c)
    bill = boe(c)
    bill.with_user(both).action_assess()
    bill.with_user(c.officer).write({"customs_assessed_total": bill.total_tax + 10})
    _refused(bill.with_user(both).action_accept_variance, "assessor", match="Segregation")
    # a person who typed customs' figure cannot wave it through either
    other = _user(
        c.env,
        "m44f_both2_%s" % c.tag,
        c.ou,
        "cd_import_order.group_fix_import_officer",
        "cd_import_order.group_fix_import_approver",
    )
    bill.with_user(other).write({"customs_assessed_total": bill.total_tax + 20})
    _refused(bill.with_user(other).action_accept_variance, "typist", match="Segregation")


def test_b1_accepted_variance_is_recorded_pinned_and_payable_at_customs_figure(c):
    bill = _assessed_with_variance(c, extra=500.0)
    bill.with_user(c.approver).action_accept_variance(
        "Customs re-rated the HS; appeal not worth it"
    )
    assert bill.variance_accepted_by_id == c.approver
    assert bill.variance_accepted_amount == pytest.approx(500.0)
    assert bill.variance_reason.startswith("Customs re-rated")
    _refused(
        bill.with_user(c.officer).write,
        {"customs_assessed_total": bill.total_tax + 900},
        match="cannot be changed",
    )
    bill.with_user(c.finance).action_pay()
    assert bill.state == "paid"
    move = bill.move_id
    assert _net(move, c.bank.default_account_id) == pytest.approx(-bill.customs_assessed_total)
    assert _net(move, c.acc["variance"]) == pytest.approx(500.0)
    assert sum(move.line_ids.mapped("debit")) == pytest.approx(sum(move.line_ids.mapped("credit")))


def test_b1_a_negative_variance_posts_a_credit(c):
    bill = _assessed_with_variance(c, extra=-300.0)
    bill.with_user(c.approver).action_accept_variance("Customs allowed a rebate")
    bill.with_user(c.finance).action_pay()
    assert _net(bill.move_id, c.acc["variance"]) == pytest.approx(-300.0)
    assert _net(bill.move_id, c.bank.default_account_id) == pytest.approx(
        -bill.customs_assessed_total
    )


def test_b1_cancel_assessed_frees_the_number_and_posts_nothing(c):
    bill = _assessed_with_variance(c)
    _refused(bill.with_user(c.officer).action_cancel_assessed, "x", match="role")
    _refused(bill.with_user(c.approver).action_cancel_assessed, match="why")
    both = _user(
        c.env,
        "m44f_c_%s" % c.tag,
        c.ou,
        "cd_import_order.group_fix_import_officer",
        "cd_import_order.group_fix_import_approver",
    )
    bill.sudo()._guarded().write({"assessed_by_id": both.id})
    _refused(bill.with_user(both).action_cancel_assessed, "own", match="Segregation")
    bill.with_user(c.approver).action_cancel_assessed("Lodged against the wrong invoice")
    assert bill.state == "reversed" and bill.cancelled_by_id == c.approver
    assert not bill.move_id and not bill.reversal_move_id
    assert bill.reversal_reason == "Lodged against the wrong invoice"
    _refused(bill.with_user(c.approver).action_cancel_assessed, "again", match="assessed")
    assert boe(c, boe_no=bill.boe_no).state == "draft"


# ================================================================ B2 M16 + GRNI
def _sent_po(c, **kw):
    """A sent PO in BDT at the commitment value of the import lines."""
    vals = {
        "vendor_id": c.supplier.id,
        "operating_unit_id": c.ou.id,
        "line_ids": [
            (
                0,
                0,
                {
                    "product_id": c.product.id,
                    "qty_ordered": 10,
                    "unit_price": 600.0 * FX,
                    "approved_qty": 10,
                    "approved_unit_price": 600.0 * FX,
                },
            ),
            (
                0,
                0,
                {
                    "product_id": c.product2.id,
                    "qty_ordered": 20,
                    "unit_price": 200.0 * FX,
                    "approved_qty": 20,
                    "approved_unit_price": 200.0 * FX,
                },
            ),
        ],
    }
    vals.update(kw)
    po = c.env["fix.purchase.order"].create(vals)
    po._guarded().write({"state": "sent"})
    return po


def _bill(c, po, ref="SUP-1"):
    return c.env["fix.vendor.invoice"].create(
        {
            "vendor_id": c.supplier.id,
            "invoice_ref": "%s-%s" % (ref, c.tag),
            "requisition_id": po.id,
            "operating_unit_id": c.ou.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": pol.product_id.id,
                        "description": pol.product_id.name,
                        "quantity": pol.qty_ordered,
                        "unit_price": pol.unit_price,
                        "tds_exempt": False,
                    },
                )
                for pol in po.line_ids
            ],
        }
    )


def _inspect_all(c, grn):
    for line in grn.line_ids:
        c.env["fix.procurement.inspection"].create(
            {"receipt_line_id": line.id, "qty_accepted": line.qty_received}
        ).action_confirm()


def _ap_accounts(c):
    """The AP roles the bill's entry needs; GRNI is one account for both sides."""
    icp = c.env["ir.config_parameter"].sudo()
    icp.set_param("cd_ap_ext.account_code.grni", c.acc["grni"].code)
    for i, (key, kind) in enumerate(
        (
            ("cd_ap_ext.account_code.ap", "liability_payable"),
            ("cd_tax_engine_bd.vat_input_account_code", "asset_current"),
            ("cd_tax_engine_bd.account_code.tds_payable", "liability_current"),
            ("cd_tax_engine_bd.account_code.vds_payable", "liability_current"),
        )
    ):
        code = "M44X%s%d" % (c.tag[:3], i)
        c.env["account.account"].create(
            {
                "code": code,
                "name": key,
                "account_type": kind,
                "company_ids": [(6, 0, c.co.ids)],
                "reconcile": kind == "liability_payable",
            }
        )
        icp.set_param(key, code)


def test_b2_po_linked_receipt_matches_the_bill_once_and_clears_grni(c):
    _ap_accounts(c)
    po = _sent_po(c)
    c.order.with_user(c.officer).write({"purchase_order_id": po.id})
    stage_received(c)
    grn = c.order.m16_receipt_id
    assert grn and grn.state == "posted" and grn.import_order_id == c.order
    assert grn.receiver_id == c.officer
    assert po.state == "received" and [ln.qty_received for ln in po.line_ids] == [10, 20]

    # no double stock: the GRN's bridge is silent, the import receipt is the only one
    M15 = c.env["fix.stock.receipt"]
    assert M15.search_count([("purchase_order_id", "=", po.id)]) == 1
    assert grn.stock_receipt_ids == c.order.receipt_id
    assert _bucket(c, c.part).qty == 10 and _bucket(c, c.part2).qty == 20

    # the bill waits for M16's inspection, then matches
    bill = _bill(c, po)
    assert bill.match_state == "blocked" and "awaiting inspection" in bill.match_detail
    _inspect_all(c, grn)
    bill.invalidate_recordset()
    bill._compute_match()
    assert bill.match_state == "matched", bill.match_detail

    # no double GL: one goods entry; the bill's debit clears GRNI to nil
    goods = 10000.0 * FX
    grni = c.acc["grni"]
    assert _net(c.order.goods_move_id, grni) == pytest.approx(-goods)
    assert (
        c.env["account.move"].search_count([("ref", "like", "Import receipt %s" % c.order.name)])
        == 1
    )
    bill._guarded().write({"approval_state": "approved"})
    bill._post_approved_bill()
    lines = c.env["account.move.line"].search(
        [("account_id", "=", grni.id), ("parent_state", "=", "posted")]
    )
    assert sum(lines.mapped("balance")) == pytest.approx(0.0)

    # a second bill for the same goods is refused by the match
    second = _bill(c, po, ref="SUP-2")
    second._compute_match()
    assert second.match_state == "blocked"


def test_b2_inspection_rejection_reaches_the_import_stock(c):
    po = _sent_po(c)
    c.order.with_user(c.officer).write({"purchase_order_id": po.id})
    stage_received(c)
    grn = c.order.m16_receipt_id
    assert c.order.receipt_id.source_model == "fix.purchase.receipt"
    assert c.order.receipt_id.source_ref == grn.name
    line = grn.line_ids.filtered(lambda ln: ln.product_id == c.product)
    product = line.product_id
    moved = c.env["fix.stock.quarantine"].consume_inspection_rejected(
        {
            "aggregate_id": 987654,
            "payload": {"qty_rejected": 4, "product_id": product.id, "receipt_ref": grn.name},
        }
    )
    assert moved == 1


def test_b2_receipt_beyond_the_po_refused_with_nothing_moved(c):
    po = _sent_po(
        c,
        line_ids=[
            (0, 0, {"product_id": c.product.id, "qty_ordered": 5, "unit_price": 600.0 * FX}),
            (0, 0, {"product_id": c.product2.id, "qty_ordered": 20, "unit_price": 200.0 * FX}),
        ],
    )
    c.order.with_user(c.officer).write({"purchase_order_id": po.id})
    stage_cleared(c)
    _refused(c.order.with_user(c.officer).action_receive, match="less of")
    assert c.order.state == "cleared" and not c.order.receipt_id and not _bucket(c, c.part)


def test_b2_buyer_cannot_receive_a_po_linked_import(c):
    po = _sent_po(c, buyer_id=c.officer.id)
    c.order.with_user(c.officer).write({"purchase_order_id": po.id})
    stage_cleared(c)
    _refused(c.order.with_user(c.officer).action_receive, match="SOD-02")
    assert c.order.state == "cleared"


def test_b2_import_without_po_has_no_grn(c):
    stage_received(c)
    assert c.order.state == "received" and not c.order.m16_receipt_id
    assert c.order.receipt_id.source_model == "fix.import.order"


def test_b2_import_mark_cannot_be_forged_to_skip_stock(c):
    po = _sent_po(c)
    grn = c.env["fix.purchase.receipt"].create(
        {
            "purchase_order_id": po.id,
            "line_ids": [(0, 0, {"po_line_id": po.line_ids[0].id, "qty_received": 1})],
        }
    )
    receiver = _user(c.env, "m44f_rcv_%s" % c.tag, c.ou, GROUP_RECEIVER)
    _refused(grn.with_user(receiver).write, {"import_order_id": c.order.id}, match="workflow")
    assert not grn.import_order_id
    # an ordinary GRN still puts its goods into M15 stock. With M16's
    # inspection required (the default) they land held "In Inspection" and
    # only the inspection releases them (B2, BRU-PRO-11); without it they are
    # available at once. Either way the forged mark skipped nothing.
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.po_receiving_location_id", str(c.loc.id)
    )
    grn.with_user(receiver).action_post()
    receipt = grn.stock_receipt_ids
    assert receipt.state == "posted" and receipt.location_id == c.loc
    assert receipt.line_ids.part_id == c.part and receipt.line_ids.qty_received == 1
    Onhand = c.env["fix.stock.onhand"]
    held = Onhand._bucket(c.part, c.loc, "owned", status="inspection")
    available = Onhand._bucket(c.part, c.loc, "owned")
    if receipt.inspection_held:
        assert held.qty == 1 and not available.qty
    else:
        assert available.qty == 1 and not held.qty


# ================================================================ B3 reversal
def test_b3_reversal_before_receipt_reopens_shipment_and_order(c):
    arr, bill = stage_cleared(c)
    assert (arr.state, c.order.state) == ("cleared", "cleared")
    bill.with_user(c.finance).action_reverse("Wrong AV")
    assert (arr.state, c.order.state) == ("arrived", "customs")
    assert not arr.cleared_on and not arr.cleared_by_id
    _refused(c.order.with_user(c.officer).action_receive, match="In Customs")


def test_b3_receive_reads_a_live_paid_boe_not_the_order_state(c):
    arr, bill = stage_cleared(c)
    # the order state alone (legacy rows, or a reversal before this rule) is not enough
    bill.sudo()._guarded().write({"state": "reversed"})
    assert c.order.state == "cleared"
    _refused(c.order.with_user(c.officer).action_receive, match="live Bill of Entry")
    assert not c.order.receipt_id


def test_b3_reversal_after_receipt_refused(c):
    _arr, bill = stage_received(c)
    _refused(bill.with_user(c.finance).action_reverse, "too late", match="already received")
    assert bill.state == "paid" and c.order.state == "received"


def test_b3_clear_again_after_a_new_boe(c):
    arr, bill = stage_cleared(c)
    bill.with_user(c.finance).action_reverse("Wrong AV")
    assess_and_pay(c, boe(c, boe_no="BE-2-%s" % c.tag))
    arr.with_user(c.officer).action_clear()
    assert (arr.state, c.order.state) == ("cleared", "cleared")
    c.order.with_user(c.officer).action_receive()
    assert c.order.state == "received"


# ================================================================ B4 LC cap and LCA
def test_b4_second_lc_cannot_take_the_order_above_its_value(c):
    stage_lc_applied(c)  # the first LC equals the order value
    second = lc(c, lc_no="LC2-%s" % c.tag)
    lca(c, second).with_user(c.approver).action_approve()
    _refused(second.with_user(c.officer).action_apply, match="other LCs already commit")
    assert second.state == "draft"


def test_b4_two_lcs_within_the_order_value_are_allowed(c):
    stage_proforma(c)
    for suffix, amount in (("A", 500000.0), ("B", 675000.0)):
        letter = lc(c, lc_no="LC%s-%s" % (suffix, c.tag), amount=amount)
        lca(c, letter).with_user(c.approver).action_approve()
        letter.with_user(c.officer).action_apply()
        assert letter.state == "applied"


def test_b4_draft_lc_raised_after_lca_approval_refused(c):
    stage_proforma(c)
    letter = lc(c, amount=500000.0)
    lca(c, letter).with_user(c.approver).action_approve()
    letter.with_user(c.officer).write({"amount": 1000000.0})
    _refused(letter.with_user(c.officer).action_apply, match="covers 500000")
    assert letter.state == "draft"


# ================================================================ B5 HS of the part
def test_b5_another_products_ruling_refused(c):
    line = c.order.line_ids.filtered(lambda ln: ln.part_id == c.part)
    _refused(line.with_user(c.officer).write, {"hs_id": c.hs2.id}, match="M44-10")
    assert line.hs_id == c.hs


def test_b5_part_without_product_cannot_take_any_ruling(c):
    bare = c.env["fix.spare.part"].create({"name": "M44T bare", "part_number": "BARE-%s" % c.tag})
    _refused(
        lambda: c.env["fix.import.order.line"]
        .with_user(c.officer)
        .create({"order_id": c.order.id, "part_id": bare.id, "hs_id": c.hs.id, "quantity": 1}),
        match="no purchasing product",
    )


def test_b5_existing_row_refused_at_the_next_step(c):
    """A row written before the rule is not rejected on upgrade; the next
    compliance step refuses it."""
    line = c.order.line_ids.filtered(lambda ln: ln.part_id == c.part)
    c.env.cr.execute(
        "UPDATE fix_import_order_line SET hs_id = %s WHERE id = %s", (c.hs2.id, line.id)
    )
    line.invalidate_recordset()
    pf = proforma(c)
    _refused(pf.with_user(c.approver).action_approve, match="M44-10")


# ================================================================ B6 IRC
def test_b6_lapsed_irc_gates_bl_and_boe(c):
    stage_advance(c)
    bl = shipdoc(c, "bl")
    c.irc.sudo()._guarded().write({"state": "suspended"})
    _refused(bl.with_user(c.officer).action_receive, match="Import Registration")
    assert bl.state == "pending"
    c.irc.sudo()._guarded().write({"state": "valid"})
    stage_shipped(c)
    bill = boe(c)
    c.irc.sudo()._guarded().write({"state": "suspended"})
    _refused(bill.with_user(c.officer).action_assess, match="Import Registration")
    assert bill.state == "draft"


def test_b6_expiry_warning_once_at_the_configured_days(c):
    Irc = c.env["fix.import.irc"]
    icp = c.env["ir.config_parameter"].sudo()
    icp.set_param("cd_import_order.irc_expiry_warning_days", "10")
    far = Irc.create({"irc_no": "FAR-%s" % c.tag, "valid_to": c.today + timedelta(days=11)})
    near = Irc.create({"irc_no": "NEAR-%s" % c.tag, "valid_to": c.today + timedelta(days=9)})
    Irc._cron_expire()
    assert near.expiry_warned_on == c.today and not far.expiry_warned_on
    assert c.approver in near.activity_ids.mapped("user_id")
    count = len(near.activity_ids)
    Irc._cron_expire()
    assert len(near.activity_ids) == count, "asked once"


def test_b6_expired_event_reaches_open_orders(c):
    consumer = c.env.ref("cd_import_order.consumer_import_irc_expired")
    assert consumer.event_type == "import.irc_expired"
    assert consumer.model == "fix.import.order" and consumer.method == "consume_irc_expired"
    told = c.env["fix.import.order"].consume_irc_expired(
        {"aggregate_id": c.irc.id, "payload": {"irc": c.irc.irc_no}}
    )
    assert told >= 1
    assert "IRC expired" in c.order.activity_ids.mapped("summary")


# ================================================================ B7 FX
def _bare_fx_order(c):
    return (
        c.env["fix.import.order"]
        .with_user(c.officer)
        .create(
            {
                "name": "M44T-NOFX-%s" % c.tag,
                "supplier_id": c.supplier.id,
                "operating_unit_id": c.ou.id,
                "currency_id": c.usd.id,
                "fob_value": 600.0,
                "incoterm": "cif",
                "line_ids": [
                    (
                        0,
                        0,
                        {"part_id": c.part.id, "hs_id": c.hs.id, "quantity": 1, "unit_price": 600},
                    )
                ],
            }
        )
    )


def test_b7_foreign_order_needs_rate_source_date_before_leaving_draft(c):
    order = _bare_fx_order(c)
    pf = proforma(c, order_id=order.id, amount=600.0, proforma_no="PIFX-%s" % c.tag)
    _refused(pf.with_user(c.approver).action_approve, match="BRU-ITC-14")
    assert pf.state == "received"
    bl = (
        c.env["fix.import.shipdoc"]
        .with_user(c.officer)
        .create({"order_id": order.id, "doc_type": "bl", "ref": "BLFX"})
    )
    _refused(bl.with_user(c.officer).action_receive, match="BRU-ITC-14")
    assert order.state == "draft"
    order.with_user(c.officer).write(
        {"fx_rate": 120.0, "fx_rate_source": "AD bank contract", "fx_rate_date": c.today}
    )
    pf.with_user(c.approver).action_approve()
    assert pf.state == "approved"


def test_b7_a_bdt_order_needs_no_fx_terms(c):
    order = _bare_fx_order(c)
    order.with_user(c.officer).write({"currency_id": c.bdt.id})
    pf = proforma(
        c, order_id=order.id, amount=600.0, proforma_no="PIBD-%s" % c.tag, currency_id=c.bdt.id
    )
    pf.with_user(c.approver).action_approve()
    assert pf.state == "approved"


def test_b7_a_missing_source_can_still_be_recorded_after_the_pin(c):
    """Rows pinned before the rule had no source: they are not a dead end, and
    once recorded the source is pinned."""
    stage_proforma(c)
    c.order.sudo().write({"fx_rate_source": False, "fx_rate_date": False})
    c.order.with_user(c.officer).write({"fx_rate_source": "BB rate", "fx_rate_date": c.today})
    _refused(c.order.with_user(c.officer).write, {"fx_rate_source": "other"}, match="pinned")
    _refused(c.order.with_user(c.officer).write, {"fx_rate": 1.0}, match="pinned")


def test_b7_usd_payment_needs_settlement_rate_and_posts_the_difference(c):
    letter = _usd_lc(c)
    Pay = c.env["fix.import.lc.payment"].with_user(c.finance)
    base = {"lc_id": letter.id, "amount": 100.0, "reference": "TT-%s" % c.tag}
    _refused(lambda: Pay.create(base), match="settlement rate")
    _refused(
        lambda: Pay.create(dict(base, settlement_rate=120.0)),
        match="settlement rate",
    )
    pay = Pay.create(dict(base, settlement_rate=120.0, settlement_rate_source="AD bank advice"))
    assert pay.commitment_rate == pytest.approx(FX)
    assert pay.amount_bdt == pytest.approx(12000.0)
    assert pay.fx_difference == pytest.approx(100.0 * (120.0 - FX))
    move = pay.move_id
    assert move.state == "posted"
    assert _net(move, c.acc["lc_clearing"]) == pytest.approx(100.0 * FX)
    assert _net(move, c.acc["fx_difference"]) == pytest.approx(100.0 * (120.0 - FX))
    assert _net(move, c.bank.default_account_id) == pytest.approx(-12000.0)
    # a gain credits the difference account
    gain = Pay.create(
        dict(base, reference="TT2", settlement_rate=110.0, settlement_rate_source="AD bank")
    )
    assert _net(gain.move_id, c.acc["fx_difference"]) == pytest.approx(100.0 * (110.0 - FX))


def test_b7_fx_figures_cannot_be_typed(c):
    letter = _usd_lc(c)
    pay = (
        c.env["fix.import.lc.payment"]
        .with_user(c.finance)
        .create(
            {
                "lc_id": letter.id,
                "amount": 100.0,
                "reference": "TT",
                "settlement_rate": FX,
                "settlement_rate_source": "AD bank",
                "fx_difference": 9999.0,
                "commitment_rate": 1.0,
            }
        )
    )
    assert pay.fx_difference == pytest.approx(0.0) and pay.commitment_rate == pytest.approx(FX)
    _refused(pay.with_user(c.finance).write, {"fx_difference": 5.0}, match="final")


def test_b7_payment_refused_with_nothing_posted_when_an_account_is_unset(c):
    letter = stage_lc_open(c)
    c.env["ir.config_parameter"].sudo().set_param("cd_import_order.account_code.lc_clearing", "")
    _refused(
        lambda: c.env["fix.import.lc.payment"]
        .with_user(c.finance)
        .create({"lc_id": letter.id, "amount": 10.0, "reference": "TT"}),
        match="cd_import_order.account_code.lc_clearing",
    )
    assert not letter.payment_ids


def test_b7_bdt_lc_payment_posts_with_no_difference(c):
    letter = stage_lc_open(c)
    pay = (
        c.env["fix.import.lc.payment"]
        .with_user(c.finance)
        .create({"lc_id": letter.id, "amount": 1000.0, "reference": "TT"})
    )
    assert pay.fx_difference == 0.0 and pay.amount_bdt == pytest.approx(1000.0)
    assert _net(pay.move_id, c.acc["lc_clearing"]) == pytest.approx(1000.0)
    assert _net(pay.move_id, c.bank.default_account_id) == pytest.approx(-1000.0)


# ================================================================ B8 advance
def _advance(c, amount=100.0, **kw):
    vals = {
        "order_id": c.order.id,
        "amount": amount,
        "currency_id": c.usd.id,
        "bank": "Test AD Bank",
        "guarantee_ref": "APG-%s" % c.tag,
    }
    vals.update(kw)
    return c.env["fix.import.advance"].with_user(c.officer).create(vals)


def test_b8_bl_refused_with_no_instrument(c):
    bl = shipdoc(c, "bl")
    _refused(bl.with_user(c.officer).action_receive, match="neither an opened LC")
    assert bl.state == "pending" and c.order.state == "draft"
    # a requested, unapproved advance and an LC not yet opened do not count
    adv = _advance(c)
    adv.action_request()
    _refused(bl.with_user(c.officer).action_receive, match="neither an opened LC")
    stage_lc_applied(c)
    _refused(bl.with_user(c.officer).action_receive, match="neither an opened LC")


def test_b8_approved_advance_lets_the_bl_through(c):
    stage_advance(c)
    bl = shipdoc(c, "bl")
    bl.with_user(c.officer).action_receive()
    assert bl.state == "received" and c.order.state == "shipped"


def test_b8_opened_lc_lets_the_bl_through(c):
    stage_lc_open(c)
    bl = shipdoc(c, "bl")
    bl.with_user(c.officer).action_receive()
    assert c.order.state == "shipped"


def test_b8_roles_and_two_person_rule(c):
    adv = _advance(c)
    _refused(adv.with_user(c.clerk).action_request, match="role")
    adv.with_user(c.officer).action_request()
    _refused(adv.with_user(c.officer).action_approve, "x", match="role")
    both = _user(
        c.env,
        "m44f_a_%s" % c.tag,
        c.ou,
        "cd_import_order.group_fix_import_officer",
        "cd_import_order.group_fix_import_approver",
    )
    own = (
        c.env["fix.import.advance"]
        .with_user(both)
        .create(
            {
                "order_id": c.order.id,
                "amount": 50.0,
                "currency_id": c.usd.id,
                "bank": "B",
                "guarantee_ref": "G",
            }
        )
    )
    own.action_request()
    _refused(own.with_user(both).action_approve, "mine", match="Segregation")
    assert own.state == "requested"


def test_b8_state_and_stamps_not_forgeable(c, p03):
    adv = _advance(c)
    _refused(adv.with_user(c.officer).write, {"state": "approved"}, match="workflow")
    p03.as_user(c.officer)
    out = p03.write(model="fix.import.advance", record_id=adv.id, values={"state": "approved"})
    adv.invalidate_recordset()
    assert out.get("error") and adv.state == "draft", out


def test_b8_cap_needs_a_reason_above_and_value_is_a_hard_limit(c):
    adv = _advance(c, amount=100.0)
    adv.with_user(c.officer).action_request()
    # the default cap of 0% means any advance needs a stated reason
    _refused(adv.with_user(c.approver).action_approve, match="state why")
    adv.with_user(c.approver).action_approve("Supplier requires 1% on order")
    assert adv.state == "approved" and adv.above_cap and adv.decided_by_id == c.approver

    c.env["ir.config_parameter"].sudo().set_param("cd_import_order.advance_cap_pct", "50")
    within = _advance(c, amount=100.0, guarantee_ref="G2")
    within.with_user(c.officer).action_request()
    within.with_user(c.approver).action_approve()
    assert within.state == "approved" and not within.above_cap

    over = _advance(c, amount=c.order.fob_value, guarantee_ref="G3")
    over.with_user(c.officer).action_request()
    _refused(
        over.with_user(c.approver).action_approve, "big", match="above the order's invoice value"
    )


def test_b8_decided_advance_is_fixed(c):
    adv = _advance(c)
    adv.with_user(c.officer).action_request()
    _refused(adv.with_user(c.officer).write, {"amount": 5000.0}, match="cannot be changed")
    _refused(adv.with_user(c.approver).action_reject, match="why")
    adv.with_user(c.approver).action_reject("No guarantee on file")
    assert adv.state == "rejected" and adv.decision_reason == "No guarantee on file"
    _refused(adv.with_user(c.officer).action_cancel, match="undecided")


def test_b8_other_ou_cannot_see_the_advance(c):
    adv = _advance(c)
    assert not c.env["fix.import.advance"].with_user(c.outsider).search([("id", "=", adv.id)])


# ================================================================ B9 remittance
def _old_paid_boe(c, days=130):
    stage_shipped(c)
    bill = assess_and_pay(c, boe(c))
    bill.sudo().write({"boe_date": c.today - timedelta(days=days)})
    return bill


def test_b9_link_only_within_the_order_and_only_by_finance(c):
    letter = stage_lc_open(c)
    stage_shipped(c)
    bill = assess_and_pay(c, boe(c))
    pay = (
        c.env["fix.import.lc.payment"]
        .with_user(c.finance)
        .create({"lc_id": letter.id, "amount": 1000.0, "reference": "TT"})
    )
    _refused(pay.with_user(c.officer).action_link_boe, bill.boe_no, match="role")
    _refused(pay.with_user(c.finance).action_link_boe, match="State the Bill of Entry")
    _refused(pay.with_user(c.finance).action_link_boe, "NO-SUCH", match="no assessed or paid")
    pay.with_user(c.finance).action_link_boe(bill.boe_no)
    assert pay.boe_id == bill
    _refused(pay.with_user(c.finance).action_link_boe, bill.boe_no, match="already matched")
    # the link names a Bill of Entry of the LC's own order
    other = _bare_fx_order(c)
    other.sudo().write({"fx_rate": 110, "fx_rate_source": "s", "fx_rate_date": c.today})
    foreign = (
        c.env["fix.import.boe"]
        .with_user(c.officer)
        .create({"order_id": other.id, "boe_no": "BEO-%s" % c.tag, "line_ids": []})
    )
    _refused(
        lambda: c.env["fix.import.lc.payment"]
        .with_user(c.finance)
        .create({"lc_id": letter.id, "amount": 1.0, "reference": "T2", "boe_id": foreign.id}),
        match="belongs to import",
    )


def test_b9_cron_flags_an_unmatched_boe_past_the_window_once(c):
    bill = _old_paid_boe(c)
    Boe = c.env["fix.import.boe"]
    assert Boe._cron_boe_remittance_match() >= 1
    assert bill.remittance_flagged_on == c.today
    assert "Unmatched Bill of Entry" in c.order.activity_ids.mapped("summary")
    n = len(c.order.activity_ids)
    Boe._cron_boe_remittance_match()
    assert len(c.order.activity_ids) == n


def test_b9_window_is_a_parameter_and_a_match_is_not_flagged(c):
    letter = stage_lc_open(c)
    bill = _old_paid_boe(c, days=60)
    Boe = c.env["fix.import.boe"]
    Boe._cron_boe_remittance_match()
    assert not bill.remittance_flagged_on, "inside the default window"
    pay = (
        c.env["fix.import.lc.payment"]
        .with_user(c.finance)
        .create({"lc_id": letter.id, "amount": 1000.0, "reference": "TT", "boe_id": bill.id})
    )
    c.env["ir.config_parameter"].sudo().set_param("cd_import_order.boe_remittance_match_days", "30")
    Boe._cron_boe_remittance_match()
    assert not bill.remittance_flagged_on, "matched"
    assert pay.boe_id == bill


def test_b9_a_remittance_with_no_boe_is_flagged(c):
    letter = stage_lc_open(c)
    pay = (
        c.env["fix.import.lc.payment"]
        .with_user(c.finance)
        .create(
            {
                "lc_id": letter.id,
                "amount": 1000.0,
                "reference": "TT-OLD",
                "payment_date": c.today - timedelta(days=125),
            }
        )
    )
    c.env["fix.import.boe"]._cron_boe_remittance_match()
    assert pay.match_flagged_on == c.today


def test_b9_match_report_lists_both_directions(c):
    letter = stage_lc_open(c)
    bill = _old_paid_boe(c)
    c.env["fix.import.lc.payment"].with_user(c.finance).create(
        {"lc_id": letter.id, "amount": 1000.0, "reference": "TT-UNLINKED"}
    )
    pack = m44_ctl.boe_remittance(c.env(user=c.officer.id))
    rows = {r["ref"]: r for r in pack["rows"]}
    assert rows[bill.boe_no]["status"] == "Overdue"
    assert rows["TT-UNLINKED"]["status"] == "Awaiting Bill of Entry"
    assert "120" in pack["notes"][0] and "4-month" in pack["notes"][0]


def test_b9_crons_shipped(c):
    for xmlid, model, method in (
        ("ir_cron_import_boe_remittance", "fix.import.boe", "_cron_boe_remittance_match"),
        ("ir_cron_import_demurrage_alert", "fix.import.arrival", "_cron_demurrage_alert"),
    ):
        cron = c.env.ref("cd_import_order.%s" % xmlid)
        assert cron.active and cron.model_id.model == model and method in cron.code


# ================================================================ B10 document pack
def test_b10_checklist_reads_documents_and_says_it_is_not_an_integration(c):
    stage_advance(c)
    bl = shipdoc(c, "bl")
    bl.with_user(c.officer).write({"document": "UEs=", "document_name": "bl.pdf"})
    bl.with_user(c.officer).action_receive()
    bl.with_user(c.officer2).action_verify()
    inv = shipdoc(c, "invoice")
    inv.with_user(c.officer).action_receive()
    pack = m44_ctl.document_checklist(c.env(user=c.officer.id))
    row = next(r for r in pack["rows"] if r["order"] == c.order.name)
    assert row["bl"] == "Verified (file)"
    assert row["invoice"] == "Received (no file)"
    assert row["packing"] == "Missing" and row["coo"] == "Missing"
    assert row["pack"] == "Incomplete" and "Packing List" in row["missing"]
    assert "not a live ASYCUDA or BSW integration" in pack["notes"][0]
    _refused(bl.with_user(c.officer).write, {"document": "QUJD"}, match="cannot be changed")
    packing = shipdoc(c, "packing")
    packing.with_user(c.officer).action_receive()
    pack = m44_ctl.document_checklist(c.env(user=c.officer.id))
    assert next(r for r in pack["rows"] if r["order"] == c.order.name)["pack"] == "Complete"


# ================================================================ B11 close and bank charges
def test_b11_close_only_when_received_and_finally_costed(c):
    _refused(c.order.with_user(c.approver).action_close, match="close it once")
    letter = stage_lc_open(c)
    stage_received(c)
    _refused(c.order.with_user(c.approver).action_close, match="close it once")
    sheet = landed(c)
    sheet.with_user(c.approver).action_finalise()
    assert c.order.state == "landed"
    _refused(c.order.with_user(c.officer).action_close, match="role")
    _refused(c.order.with_user(c.approver).action_close, match="an LC not yet closed")
    c.env["fix.import.lc.payment"].with_user(c.finance).create(
        {"lc_id": letter.id, "amount": 1175000.0, "reference": "TT"}
    )
    letter.with_user(c.officer).action_close()
    c.order.with_user(c.approver).action_close()
    assert c.order.state == "closed" and c.order.closed_by_id == c.approver
    _refused(c.order.with_user(c.approver).action_close, match="close it once")
    _refused(c.order.with_user(c.officer).write, {"state": "landed"}, match="workflow")
    rows = m44_ctl.fx_exposure(c.env(user=c.officer.id))["rows"]
    assert c.order.name not in [r["order"] for r in rows]


def test_b11_bank_charges_are_a_capitalised_cost_line(c):
    stage_received(c)
    sheet = landed(c, bank_charges=7000.0)
    assert sheet.total_landed == pytest.approx(45000 + 8000 + 25000 + 7000 + sheet.duty)
    sheet.with_user(c.approver).action_finalise()
    assert _net(sheet.move_id, c.acc["landed_accrual"]) == pytest.approx(
        -(45000 + 8000 + 25000 + 7000)
    )
    assert sum(sheet.line_ids.mapped("amount")) == pytest.approx(sheet.total_landed)


# ================================================================ B12 demurrage
def test_b12_clearing_past_free_days_needs_a_cause(c):
    stage_shipped(c)
    arr = arrival(c, free_days=2)
    arr.with_user(c.officer).action_arrive(str(c.today - timedelta(days=5)))
    assert arr.demurrage_days == 3
    assess_and_pay(c, boe(c))
    arr.with_user(c.officer).write({"release_ref": "RO-%s" % c.tag})
    _refused(arr.with_user(c.officer).action_clear, match="demurrage cause")
    assert arr.state == "arrived"
    arr.with_user(c.officer).write({"demurrage_cause": "customs"})
    arr.with_user(c.officer).action_clear()
    assert arr.state == "cleared"
    _refused(
        arr.with_user(c.officer).write, {"demurrage_cause": "other"}, match="cannot be changed"
    )


def test_b12_free_days_exceeded_alert_once(c):
    stage_shipped(c)
    late = arrival(c, free_days=1)
    late.with_user(c.officer).action_arrive(str(c.today - timedelta(days=4)))
    Arrival = c.env["fix.import.arrival"]
    assert Arrival._cron_demurrage_alert() >= 1
    assert late.demurrage_alerted_on == c.today
    todo = c.order.activity_ids.filtered(lambda a: a.summary == "Demurrage running")
    assert todo and todo.user_id == c.officer
    Arrival._cron_demurrage_alert()
    assert len(c.order.activity_ids.filtered(lambda a: a.summary == "Demurrage running")) == 1


def test_b12_inside_free_days_no_alert(c):
    stage_shipped(c)
    fresh = arrival(c, free_days=7)
    fresh.with_user(c.officer).action_arrive()
    c.env["fix.import.arrival"]._cron_demurrage_alert()
    assert not fresh.demurrage_alerted_on


# ================================================================ the whole path
def test_final_proper_path_to_closed(c):
    po = _sent_po(c)
    c.order.with_user(c.officer).write({"purchase_order_id": po.id})
    letter = stage_lc_open(c)
    arr, bill = stage_received(c)
    assert (arr.state, bill.state) == ("cleared", "paid")
    assert c.order.m16_receipt_id.state == "posted"
    landed(c, bank_charges=1000.0).with_user(c.approver).action_finalise()
    c.env["fix.import.lc.payment"].with_user(c.finance).create(
        {"lc_id": letter.id, "amount": 1175000.0, "reference": "TT", "boe_id": bill.id}
    )
    letter.with_user(c.officer).action_close()
    c.order.with_user(c.approver).action_close()
    assert c.order.state == "closed"


# ================================================================ expiry-only LC amendment
def _amendment(c, letter, user=None, **kw):
    vals = {"lc_id": letter.id, "reason": "Supplier asked for 30 more days"}
    vals.update(kw)
    return c.env["fix.import.lc.amendment"].with_user(user or c.officer).create(vals)


def _inbox_task(record, user):
    return record.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == user
    )


def test_expiry_only_amendment_is_approved_and_applied(c):
    """A blank new amount means "unchanged": the amendment is routed at the
    LC total it leaves in force, approved from the inbox, then applied."""
    letter = stage_lc_open(c)
    old_expiry = letter.expiry
    new_expiry = old_expiry + timedelta(days=30)
    am = _amendment(c, letter, new_expiry=new_expiry)
    assert not am.new_amount
    assert am._dofa_amount() == pytest.approx(letter.amount)
    assert am.dofa_tier_required != "tier_0"
    _refused(am.with_user(c.officer).action_apply_amendment, match="not approved")
    am.with_user(c.officer).action_request_approval(justification="Shipment window")
    assert am.approval_state == "pending"
    task = _inbox_task(am, c.approver)
    assert task, "routed to %s" % am.approval_request_id.task_ids.mapped("assigned_user_id.name")
    task.with_user(c.approver).action_approve(comment="Approved")
    assert am.approval_state == "approved" and am.dofa_approved_by == c.approver
    assert am.dofa_approved_amount == pytest.approx(1175000.0)
    am.with_user(c.officer).action_apply_amendment()
    assert am.state == "applied" and am.old_expiry == old_expiry
    assert letter.expiry == new_expiry and letter.amount == pytest.approx(1175000.0)


def test_amendment_that_changes_nothing_is_refused(c):
    letter = stage_lc_open(c)
    for vals in ({}, {"new_amount": letter.amount, "new_expiry": letter.expiry}):
        am = _amendment(c, letter, **vals)
        _refused(am.with_user(c.officer).action_request_approval, match="changes neither")
        assert am.approval_state != "pending"
        am.with_user(c.officer).action_cancel()


def test_requester_cannot_approve_an_expiry_only_amendment(c):
    both = _user(c.env, "m44f_amend_%s" % c.tag, c.ou, OFFICER_ROLE, APPROVER_ROLE, TIER4)
    letter = stage_lc_open(c)
    am = _amendment(c, letter, user=both, new_expiry=letter.expiry + timedelta(days=10))
    am.with_user(both).action_request_approval(justification="Shipment window")
    assert not _inbox_task(am, both), "never routed to the person who raised it"
    _refused(am.with_user(both).action_dofa_approve)
    assert am.approval_state == "pending"
    _refused(am.with_user(both).action_apply_amendment, match="not approved")
    _inbox_task(am, c.approver).with_user(c.approver).action_approve(comment="Approved")
    am.with_user(both).action_apply_amendment()
    assert am.state == "applied"
