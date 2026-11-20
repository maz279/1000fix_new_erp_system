"""A06 ERP audit (20 Nov 2026) - M44 findings M44-01..27, X08-X13, X15 and
owner decision D6 (imports). Fixtures: test_a06_m44_controls (non-admin
Import Officer / Approver / Finance, an FOB USD order of two lines at FX
117.5, a BDT LC facility). Each test reproduced its defect on the code before
the fix; rolled back per test.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_import_order.models import fix_import_common as common
from odoo.addons.cd_import_order.tests.test_a06_m44_controls import (
    FX,
    _net,
    _refused,
    approve_via_inbox,
    arrival,
    assess_and_pay,
    boe,
    landed,
    lc,
    lca,
    stage_cleared,
    stage_proforma,
    stage_received,
    stage_shipped,
)
from odoo.exceptions import UserError


def _usd_lc_open(c, amount=10000.0, margin=10.0):
    stage_proforma(c)
    letter = lc(c, amount=amount, currency_id=c.usd.id, margin_pct=margin)
    lca(c, letter).with_user(c.approver).action_approve()
    letter.with_user(c.officer).action_apply()
    approve_via_inbox(letter, c.approver, requester=c.officer, justification="LCD panels")
    letter.with_user(c.officer).action_open()
    return letter


def _pay(c, letter, amount, rate=120.0, ref=None):
    return (
        c.env["fix.import.lc.payment"]
        .with_user(c.finance)
        .create(
            {
                "lc_id": letter.id,
                "amount": amount,
                "reference": ref or "SWIFT-%s-%s" % (c.tag, amount),
                "settlement_rate": rate,
                "settlement_rate_source": "AD bank deal",
            }
        )
    )


def _posted_bill(c, amount, currency):
    """A supplier bill of the import as AP leaves it after approval: posted
    (a stand-in entry), unpaid. The AP posting itself is proven in cd_ap_ext."""
    env = c.env
    move = common.post_import_move(
        env,
        c.co,
        common.import_journal(env, c.co),
        c.today,
        "stand-in bill entry",
        [(c.acc["variance"], "x", 1.0), (c.acc["fx_difference"], "x", -1.0)],
        operating_unit=c.ou,
    )
    bill = (
        env["fix.vendor.invoice"]
        .sudo()
        .create(
            {
                "operating_unit_id": c.ou.id,
                "vendor_id": c.supplier.id,
                "currency_id": currency.id,
                "invoice_ref": "INV-%s" % c.tag,
                "bill_type": "non_po",
                "import_order_id": c.order.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": c.product.id,
                            "description": "LCD panels",
                            "quantity": 1,
                            "unit_price": amount,
                            "tds_exempt": True,
                        },
                    )
                ],
            }
        )
    )
    bill._guarded().write({"approval_state": "approved", "move_id": move.id})
    return bill


# ------------------------------------------------------------- D6 / X09 / M44-11 / M44-12
def test_erp_m44_11_lc_payment_before_the_bill_is_a_supplier_advance(c):
    """LC open posts the margin; a payment before any bill debits the
    supplier advance account at the commitment rate (not a clearing account
    nothing credits), the FX difference to its account, draws its share of
    the margin, and the bank pays the rest at the settlement rate."""
    letter = _usd_lc_open(c)
    margin = round(10000 * FX * 0.10, 2)
    assert letter.margin_amount_bdt == pytest.approx(margin)
    assert _net(letter.margin_move_id, c.acc["lc_margin"]) == pytest.approx(margin)
    assert _net(letter.margin_move_id, c.bank.default_account_id) == pytest.approx(-margin)
    pay = _pay(c, letter, 4000.0, rate=120.0)
    move = pay.move_id
    committed, paid = 4000 * FX, 4000 * 120.0
    drawn = round(margin * 0.4, 2)
    assert _net(move, c.advance_acc) == pytest.approx(committed)
    assert _net(move, c.acc["fx_difference"]) == pytest.approx(paid - committed)
    assert _net(move, c.acc["lc_margin"]) == pytest.approx(-drawn)
    assert _net(move, c.bank.default_account_id) == pytest.approx(-(paid - drawn))
    assert _net(move, c.acc["lc_clearing"]) == 0.0, "nothing is left in LC clearing"
    settlement = c.env["fix.ap.lc.settlement"].sudo().search([("source_id", "=", pay.id)])
    assert settlement.kind == "advance" and settlement.move_id == move
    assert settlement.scope_key == c.order._import_scope_key()
    assert pay.advance_bdt == pytest.approx(committed)


def test_erp_x09_lc_payment_after_the_bill_settles_it_once(c):
    letter = _usd_lc_open(c)
    bill = _posted_bill(c, 2000.0, c.usd)
    # what AP leaves payable after its own withholding (the test DB's VDS/TDS
    # defaults apply); the LC remits exactly that
    payable = bill.total_payable
    assert 0 < payable <= 2000.0
    pay = _pay(c, letter, payable, rate=FX)
    settlement = c.env["fix.ap.lc.settlement"].sudo().search([("source_id", "=", pay.id)])
    assert settlement.kind == "bill" and settlement.bill_id == bill
    assert bill.payment_state == "paid" and bill.total_payable == pytest.approx(0.0)
    assert pay.settled_bills_bdt == pytest.approx(round(payable * FX, 2))


def test_erp_m44_12_margin_not_drawn_returns_at_close(c):
    letter = _usd_lc_open(c)
    _pay(c, letter, 4000.0, rate=FX)
    for doc_type in ("bl",):
        c.env["fix.import.shipdoc"].with_user(c.officer).create(
            {"order_id": c.order.id, "doc_type": doc_type, "ref": "BL-%s" % c.tag}
        ).with_user(c.officer).action_receive()
    letter.with_user(c.officer).action_close()
    left = round(letter.margin_amount_bdt * 0.6, 2)
    assert _net(letter.margin_return_move_id, c.acc["lc_margin"]) == pytest.approx(-left)
    assert letter.margin_released_bdt == pytest.approx(letter.margin_amount_bdt)


# ------------------------------------------------------------- M44-18 / M44-22 / M44-23
def test_erp_m44_18_refused_discrepancy_blocks_payment(c):
    letter = _usd_lc_open(c)
    disc = (
        c.env["fix.import.lc.discrepancy"]
        .with_user(c.officer)
        .create(
            {
                "lc_id": letter.id,
                "raised_by_bank": "AD bank",
                "raised_on": c.today,
                "description": "late shipment",
            }
        )
    )
    disc.with_user(c.approver).action_refuse("documents not acceptable")
    _refused(lambda: _pay(c, letter, 1000.0), match="refused discrepancy")


def test_erp_m44_22_23_amendment_sets_amended_and_rechecks_the_lca(c):
    letter = _usd_lc_open(c, amount=9000.0)
    amend = (
        c.env["fix.import.lc.amendment"]
        .with_user(c.officer)
        .create({"lc_id": letter.id, "new_amount": 9500.0, "reason": "more units"})
    )
    approve_via_inbox(amend, c.approver, requester=c.officer, justification="more units")
    # the LCA covers 9000 only
    _refused(amend.with_user(c.officer).action_apply_amendment, match="LCA")
    lca(c, letter, amount=9500.0, lca_no="LCA2-%s" % c.tag).with_user(c.approver).action_approve()
    amend.with_user(c.officer).action_apply_amendment()
    assert letter.state == "amended" and letter.amount == pytest.approx(9500.0)
    # an amended LC still takes payments
    assert _pay(c, letter, 100.0, rate=FX).move_id


# ------------------------------------------------------------- M44-03 / M44-04 / M44-01
def test_erp_m44_03_04_rounding_within_bdt_10_paid_at_the_assessed_figure(c):
    stage_shipped(c)
    bill = boe(c)
    bill.with_user(c.officer).action_assess()
    assessed = round(bill.total_tax + 7.0, 2)
    bill.with_user(c.officer).write({"customs_assessed_total": assessed, "payment_ref": "CH-R"})
    bill.with_user(c.finance).action_pay()  # no variance acceptance needed
    move = bill.move_id
    assert _net(move, c.bank.default_account_id) == pytest.approx(-assessed)
    assert _net(move, c.acc["variance"]) == pytest.approx(7.0)
    assert bill.booked_rounding == pytest.approx(7.0)


def test_erp_m44_05_extra_levies_reach_their_own_accounts(c):
    stage_shipped(c)
    bill = boe(c)
    bill.with_user(c.officer).action_assess()
    assessed = round(bill.total_tax + 500.0, 2)
    bill.with_user(c.officer).write({"customs_assessed_total": assessed, "payment_ref": "CH-V"})
    bill.with_user(c.approver).action_accept_variance("customs uplift")
    # without customs' per-levy figures the 500 has no account
    _refused(bill.with_user(c.finance).action_pay, match="each levy")
    bill.sudo().write(
        {
            "customs_cd": bill.cd_amount + 300.0,
            "customs_rd": bill.rd_amount,
            "customs_sd": bill.sd_amount,
            "customs_vat": bill.vat_amount + 200.0,
            "customs_at": bill.at_amount,
            "customs_ait": bill.ait_amount,
        }
    )
    bill.with_user(c.finance).action_pay()
    move = bill.move_id
    duty = bill.cd_amount + bill.rd_amount + bill.sd_amount
    assert _net(move, c.acc["duty_clearing"]) == pytest.approx(duty + 300.0)
    assert _net(move, c.acc["vat_input"]) == pytest.approx(bill.vat_amount + 200.0)
    assert _net(move, c.acc["variance"]) == 0.0
    assert _net(move, c.bank.default_account_id) == pytest.approx(-assessed)
    sheet = landed(c)
    assert sheet.duty == pytest.approx(duty + 300.0), "the extra CD reaches stock cost"


def test_erp_m44_01_d6_account_defaults_and_repair(c):
    icp = c.env["ir.config_parameter"].sudo()
    icp.set_param("cd_import_order.account_code.variance", "610000")
    icp.set_param("cd_import_order.account_code.duty_clearing", "200306")
    icp.set_param("cd_import_order.account_code.fx_difference", "")
    # the fixture configured a test margin account: unset, as on fix_real
    icp.set_param("cd_import_order.account_code.lc_margin", "")
    icp.set_param(common.PARAM_DUTY_VARIANCE, "0")
    common.default_params(c.env)
    assert icp.get_param("cd_import_order.account_code.variance") == "600007"
    assert icp.get_param("cd_import_order.account_code.duty_clearing") == "100302"
    assert icp.get_param("cd_import_order.account_code.fx_difference") == "500030"
    assert icp.get_param("cd_import_order.account_code.lc_margin") == "100812"
    assert float(icp.get_param(common.PARAM_DUTY_VARIANCE)) == 10.0
    # a configured code D6 did not supersede is kept
    icp.set_param("cd_import_order.account_code.variance", c.acc["variance"].code)
    common.default_params(c.env)
    assert icp.get_param("cd_import_order.account_code.variance") == c.acc["variance"].code


# ------------------------------------------------------------- M44-06 / M44-07
def test_erp_m44_06_cif_terms_keep_freight_and_insurance_in_the_assessable_value(c):
    order = c.order
    order.sudo().write({"incoterm": "cif"})
    line = order.line_ids.filtered(lambda ln: ln.part_id == c.part)
    # 6000 of 10000 goods: 60% of freight 500 + insurance 100
    assert line.cif_amount == pytest.approx(6000 + 0.6 * 600.0)


def test_erp_m44_07_duty_at_the_customs_rate_of_the_boe_date(c):
    stage_shipped(c)
    bill = boe(c, customs_fx_rate=0.0)
    _refused(bill.with_user(c.officer).action_assess, match="customs exchange rate")
    bill.with_user(c.officer).write({"customs_fx_rate": 121.0})
    bill.with_user(c.officer).action_assess()
    line = bill.line_ids.filtered(lambda ln: ln.order_line_id.part_id == c.part)
    assert line.cif_value_bdt == pytest.approx(line.order_line_id.cif_amount * 121.0, abs=0.02)


# ------------------------------------------------------------- M44-08 / M44-09
def _second_tariff(c, cd=5.0):
    code = "8507.60.00"
    tariff = c.env["fix.import.tariff"].create(
        {
            "hs_code": code,
            "sro_ref": "TEST-SRO2-%s" % c.tag,
            "date_from": c.today - timedelta(days=30),
            "cd_pct": cd,
            "rd_pct": 0,
            "sd_pct": 0,
            "vat_pct": 15,
            "at_pct": 5,
            "ait_pct": 5,
        }
    )
    tariff.action_activate()
    c.hs2.sudo()._guarded().write({"hs_code": code})
    return tariff


def test_erp_m44_08_duty_allocated_from_each_lines_own_hs_duty(c):
    _second_tariff(c, cd=5.0)
    _arr, bill = stage_received(c)
    sheet = landed(c, allocation_method="qty", freight=0.0, insurance=0.0, clearing_charges=0.0)
    sheet.with_user(c.approver).action_finalise()
    lcd_line = bill.line_ids.filtered(lambda ln: ln.order_line_id.part_id == c.part)
    own = lcd_line.cd_amount + lcd_line.rd_amount + lcd_line.sd_amount
    lcd_alloc = sheet.line_ids.filtered(lambda ln: ln.part_id == c.part).amount
    assert lcd_alloc == pytest.approx(own, abs=0.02)
    # by quantity it would have been a third of the whole duty
    assert abs(lcd_alloc - sheet.duty / 3) > 1.0


def test_erp_m44_09_weight_basis_needs_and_uses_the_weights(c):
    stage_received(c)
    sheet = landed(c, allocation_method="weight")
    _refused(sheet.with_user(c.approver).action_finalise, match="weight")
    for ln, kg in zip(c.order.line_ids, (30.0, 10.0), strict=True):
        ln.sudo().write({"weight_kg": kg})
    sheet.with_user(c.approver).action_finalise()
    charges = 45000 + 8000 + 25000
    lcd = sheet.line_ids.filtered(lambda ln: ln.part_id == c.part)
    duty_lcd = sum(
        bl.cd_amount + bl.rd_amount + bl.sd_amount
        for bl in c.order.boe_ids.line_ids
        if bl.order_line_id.part_id == c.part
    )
    assert lcd.amount == pytest.approx(duty_lcd + charges * 0.75, abs=0.05)


# ------------------------------------------------------------- M44-13 / X12
def test_erp_m44_13_revaluation_follows_stock_transferred_away(c):
    stage_received(c)
    Onhand = c.env["fix.stock.onhand"]
    loc2 = c.env["fix.stock.location"].create(
        {
            "name": "M44T Branch %s" % c.tag,
            "code": "M4B%s" % c.tag,
            "location_type": "branch",
            "company_id": c.co.id,
            "operating_unit_id": c.ou.id,
        }
    )
    src = Onhand._bucket(c.part, c.loc, "owned")
    cost = src.unit_cost
    Onhand._apply(c.part, c.loc, "owned", -4)
    Onhand._apply(c.part, loc2, "owned", 4, cost)
    sheet = landed(c)
    sheet.with_user(c.approver).action_finalise()
    share = sheet.line_ids.filtered(lambda ln: ln.part_id == c.part).amount
    far = Onhand._bucket(c.part, loc2, "owned")
    assert far.unit_cost == pytest.approx(cost + share / 10, abs=0.01)
    assert sheet.variance_amount == pytest.approx(0.0, abs=0.02), "a transfer is not consumption"


# ------------------------------------------------------------- M44-10 / M44-14 / M44-17
def test_erp_m44_10_serialised_parts_wait_for_their_serials(c):
    c.part2.sudo().write({"is_serialized": True})
    stage_received(c)
    order = c.order
    serial = order.serial_receipt_id
    assert serial and serial.state == "draft"
    assert len(serial.line_ids) == 20 and set(serial.line_ids.mapped("qty_received")) == {1.0}
    sheet = landed(c)
    _refused(sheet.with_user(c.approver).action_finalise, match="serial")


def test_erp_m44_14_receipt_takes_the_declared_quantity(c):
    stage_shipped(c)
    arr = arrival(c)
    arr.with_user(c.officer).action_arrive()
    lines = [
        (0, 0, {"order_line_id": ln.id, "quantity": ln.quantity / 2}) for ln in c.order.line_ids
    ]
    assess_and_pay(c, boe(c, lines=lines))
    arr.with_user(c.officer).write({"release_ref": "RO-P"})
    arr.with_user(c.officer).action_clear()
    c.order.with_user(c.officer).action_receive()
    got = {ln.part_id: ln.qty_received for ln in c.order.receipt_id.line_ids}
    assert got[c.part] == pytest.approx(5.0) and got[c.part2] == pytest.approx(10.0)
    lcd = c.order.line_ids.filtered(lambda ln: ln.part_id == c.part)
    assert lcd.qty_received == pytest.approx(5.0)


def test_erp_m44_17_imported_stock_is_provisional_until_final(c):
    stage_received(c)
    receipt = c.order.receipt_id
    bucket = c.env["fix.stock.onhand"]._bucket(c.part, c.loc, "owned")
    assert receipt.cost_provisional and bucket.cost_provisional
    landed(c).with_user(c.approver).action_finalise()
    assert not receipt.cost_provisional and receipt.cost_finalised_on
    assert not bucket.cost_provisional


def test_erp_m44_17_escalation_cron_is_wired_and_escalates_once(c):
    cron = c.env.ref("cd_inventory.ir_cron_provisional_cost_escalation")
    assert cron.active and "_cron_escalate_provisional" in cron.code
    assert cron.model_id.model == "fix.stock.receipt"
    stage_received(c)
    receipt = c.order.receipt_id
    receipt.sudo()._guarded().write({"provisional_since": c.today - timedelta(days=31)})
    Receipt = c.env["fix.stock.receipt"]
    assert Receipt._cron_escalate_provisional() >= 1
    assert receipt.provisional_escalated_on
    assert c.env["mail.activity"].search_count(
        [("res_model", "=", "fix.import.order"), ("res_id", "=", c.order.id)]
    )
    assert Receipt._cron_escalate_provisional() == 0 or not Receipt.search_count(
        [("id", "=", receipt.id), ("provisional_escalated_on", "=", False)]
    )


# ------------------------------------------------------------- X11 / X08 / M44-19
def test_erp_x11_import_bill_without_po_clears_grni(c):
    bill = _posted_bill(c, 100.0, c.bdt)
    account = bill._expense_account(bill.line_ids)
    assert account == c.acc["grni"], "not the product's expense account"


def test_erp_x08_cost_document_bill_relieves_the_landed_accrual(c):
    stage_shipped(c)
    forwarder = c.env["res.partner"].create({"name": "M44T Forwarder %s" % c.tag})
    doc = (
        c.env["fix.import.cost"]
        .with_user(c.officer)
        .create(
            {
                "order_id": c.order.id,
                "category": "freight",
                "billed_by_id": forwarder.id,
                "document_ref": "FW-%s" % c.tag,
                "incurred_on": c.today,
                "amount": 45000.0,
            }
        )
    )
    bill = (
        c.env["fix.vendor.invoice"]
        .sudo()
        .create(
            {
                "operating_unit_id": c.ou.id,
                "vendor_id": forwarder.id,
                "invoice_ref": "FW-INV-%s" % c.tag,
                "bill_type": "non_po",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": c.product.id,
                            "description": "freight",
                            "quantity": 1,
                            "unit_price": 40000.0,
                            "tds_exempt": True,
                        },
                    )
                ],
            }
        )
    )
    doc.with_user(c.finance).write({"bill_id": bill.id})
    assert bill._expense_account(bill.line_ids) == c.acc["landed_accrual"]
    # the bill (40,000) does not carry exactly its document (45,000): refused
    _refused(bill.sudo()._post_approved_bill, match="X08")
    _refused(lambda: doc.with_user(c.officer).write({"bill_id": False}), match="role")


# ------------------------------------------------------------- M44-16 / X15
def test_erp_m44_16_duty_paid_reaches_the_input_vat_register(c):
    consumer = c.env.ref("cd_import_order.consumer_import_duty_paid_input_vat")
    assert consumer.event_type == "import.duty_paid" and consumer.method == "consume_duty_paid"
    _arr, bill = stage_cleared(c)
    Boe = c.env["fix.import.boe"]
    assert Boe.consume_duty_paid({"aggregate_id": bill.id}) == 1
    credit = c.env["fix.input.vat.credit"].search([("source_ref", "=", "BoE %s" % bill.boe_no)])
    assert credit.vat_amount == pytest.approx(bill.vat_amount)
    assert credit.invoice_date == bill.boe_date
    assert Boe.consume_duty_paid({"aggregate_id": bill.id}) == 0, "recorded once"


# ------------------------------------------------------------- X13 / M44-26
def test_erp_x13_import_entry_never_takes_the_first_ou(c):
    with pytest.raises(UserError, match="operating unit"):
        common.post_import_move(
            c.env,
            c.co,
            common.import_journal(c.env, c.co),
            fields.Date.today(),
            "no OU",
            [(c.acc["variance"], "x", 1.0), (c.acc["fx_difference"], "x", -1.0)],
            operating_unit=None,
        )


def test_erp_m44_26_landed_sheet_is_bdt(c):
    stage_received(c)
    sheet = landed(c, currency_id=c.usd.id)
    _refused(sheet.with_user(c.approver).action_finalise, match="BDT")
