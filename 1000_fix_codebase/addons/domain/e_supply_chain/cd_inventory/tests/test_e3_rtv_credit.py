# Owner-approved fixes of 12 Nov 2026 (third rehearsal, flow 5): the return to
# vendor and the credit note it hands to AP.
#
#   E3-11  the RTV named no goods receipt, PO or bill: the credit went to "the
#          vendor's latest bill with room" and nothing stopped a return of more
#          than was received or billed. The RTV now names its GRN (or records
#          why it has none); the PO comes from the GRN and the bill from the PO,
#          and the quantity is held to what the GRN accepted and the bill billed.
#   E3-10  the note was valued at the stock's average cost (1,487.50), not the
#          price billed (1,480.00). It is now the billed price; the stock still
#          leaves at average cost, and the difference is stated on the RTV.
#   E3-09  the note carried no VAT; it now carries the share of the bill's VAT
#          the returned quantity bore.
#   E3-13  the TDS withheld on the returned part travels with the note.
import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, AccessError, ValidationError)
GR = "cd_requisition.group_fix_procurement_receiver"


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


def _accounts(env):
    company = env.company
    Account = env["account.account"]

    def acc(code, name, kind):
        found = Account.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
        return found or Account.create(
            {
                "code": code,
                "name": name,
                "account_type": kind,
                "company_ids": [(6, 0, [company.id])],
            }
        )

    acc("990201", "E3 trade payables", "liability_payable")
    acc("990503", "E3 GRNI", "liability_current")
    acc("990131", "Test input VAT", "asset_current")
    acc("990252", "Test VDS payable", "liability_current")
    acc("990253", "Test TDS payable", "liability_current")
    icp = env["ir.config_parameter"].sudo()
    for param, code in (
        ("cd_ap_ext.account_code.ap", "990201"),
        ("cd_ap_ext.account_code.grni", "990503"),
        ("cd_tax_engine_bd.vat_input_account_code", "990131"),
        ("cd_tax_engine_bd.account_code.vds_payable", "990252"),
        ("cd_tax_engine_bd.account_code.tds_payable", "990253"),
    ):
        icp.set_param(param, code)
    purchase = env["account.journal"].search(
        [("company_id", "=", company.id), ("type", "=", "purchase")], limit=1
    )
    icp.set_param("cd_ap_ext.bill_journal_code", purchase.code)


@pytest.fixture
def p2p(inv):
    """A PO for 20 SSDs at 1,480.00 received into the hub (which already
    holds 10 at 1,500.00, so the average cost is not the PO price)."""
    if "fix.vendor.note" not in inv.env:
        pytest.skip("cd_ap_ext is not installed")
    env = inv.env
    w = inv
    _accounts(env)
    w.vendor = env["res.partner"].create({"name": "E3 Lucid " + inv.tag, "is_company": True})
    if "fix.supplier" in env:
        supplier = env["fix.supplier"].create(
            {"name": w.vendor.name, "partner_id": w.vendor.id, "status": "active"}
        )
        for doc_type in ("trade_licence", "tin", "vat"):
            env["fix.supplier.document"].create(
                {"supplier_id": supplier.id, "doc_type": doc_type, "state": "valid"}
            )
    w.prod = env["product.product"].create({"name": "E3 SSD " + inv.tag})
    w.ssd = env["fix.spare.part"].create(
        {
            "name": "E3 SSD",
            "part_number": "E3S-" + inv.tag,
            "unit_cost": 1500.0,
            "product_id": w.prod.id,
        }
    )
    inv.stock(w.ssd, inv.hub, 10.0, 1500.0)
    env["ir.config_parameter"].sudo().set_param(
        "cd_inventory.po_receiving_location_id", str(inv.hub.id)
    )
    env["ir.config_parameter"].sudo().set_param("cd_requisition.receipt_inspection_required", "0")
    w.po = env["fix.purchase.order"].create(
        {
            "operating_unit_id": inv.ou.id,
            "vendor_id": w.vendor.id,
            "line_ids": [
                (0, 0, {"product_id": w.prod.id, "qty_ordered": 20, "unit_price": 1480.0})
            ],
        }
    )
    w.po.action_record_requisition_exception(reason="E3 test PO without requisition")
    w.po._guarded().write(
        {
            "approval_state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": w.po._dofa_current_tier(),
            "dofa_approved_amount": w.po.amount_total,
        }
    )
    w.po.action_send()
    w.receiver = inv.user("receiver", GR)
    w.po.with_user(w.receiver).action_record_receipt({w.po.line_ids.id: 20})
    w.grn = env["fix.stock.receipt"].search([("purchase_order_id", "=", w.po.id)])
    assert len(w.grn) == 1 and w.grn.state == "posted"
    return w


def _bill(w, qty=20.0):
    env = w.env
    bill = env["fix.vendor.invoice"].create(
        {
            "operating_unit_id": w.ou.id,
            "vendor_id": w.vendor.id,
            "invoice_ref": "E3-BILL-%s-%s" % (w.tag, qty),
            "bill_type": "po",
            "requisition_id": w.po.id,
            "vat_amount": round(qty * 1480.0 * 0.15, 2),
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": w.prod.id,
                        "description": "SSD",
                        "quantity": qty,
                        "unit_price": 1480.0,
                    },
                )
            ],
        }
    )
    bill.action_confirm_tds_category()  # D-05: AP reviewed the defaulted category
    assert bill.match_state == "matched", bill.match_detail
    # trusted set-up: the AP matrix approved it (cd_ap_ext's tests cover that)
    bill._guarded().write({"approval_state": "approved"})
    bill._post_approved_bill()
    return bill


def _rtv(w, qty, **kw):
    vals = {"part_id": w.ssd.id, "location_id": w.hub.id, "partner_id": w.vendor.id}
    vals.update(kw)
    return w.rtv(w.keeper, qty=qty, **vals)


def test_e3_11_the_rtv_takes_its_po_and_bill_from_the_grn(p2p):
    bill = _bill(p2p)
    r = _rtv(p2p, 5.0, receipt_id=p2p.grn.id, rtv_ref="RMA-E3-" + p2p.tag)
    r.with_user(p2p.keeper).action_submit()
    assert r.purchase_order_id == p2p.po
    assert (r.vendor_invoice_res_id, r.vendor_invoice_ref) == (bill.id, bill.invoice_ref)


def test_e3_11_returning_more_than_the_grn_received_is_refused(p2p):
    _bill(p2p)
    first = _rtv(p2p, 5.0, receipt_id=p2p.grn.id)
    first.with_user(p2p.keeper).action_submit()
    # the hub holds 25 more, but only 15 of this GRN are left to return
    second = _rtv(p2p, 16.0, receipt_id=p2p.grn.id)
    refused(p2p, lambda: second.with_user(p2p.keeper).action_submit(), "received")
    third = _rtv(p2p, 15.0, receipt_id=p2p.grn.id)
    third.with_user(p2p.keeper).action_submit()


def test_e3_11_returning_more_than_was_billed_is_refused(p2p):
    _bill(p2p, qty=10.0)  # the vendor billed 10 of the 20 received
    r = _rtv(p2p, 12.0, receipt_id=p2p.grn.id)
    refused(p2p, lambda: r.with_user(p2p.keeper).action_submit(), "billed")


def test_e3_11_an_rtv_names_its_grn_or_why_it_has_none(p2p):
    r = _rtv(p2p, 1.0, no_receipt_reason=False)
    refused(p2p, lambda: r.with_user(p2p.keeper).action_submit(), "goods receipt")
    other = p2p.env["fix.stock.receipt"].search(
        [("partner_id", "!=", p2p.vendor.id), ("state", "=", "posted")], limit=1
    )
    if other:
        wrong = _rtv(p2p, 1.0, receipt_id=other.id)
        refused(p2p, lambda: wrong.with_user(p2p.keeper).action_submit())


def test_e3_09_10_13_credit_note_at_billed_price_with_vat_and_tds(p2p):
    bill = _bill(p2p)
    avg = p2p.bucket(p2p.ssd, p2p.hub).unit_cost
    assert abs(avg - 1480.0) > 0.01  # the average is not the PO price
    r = _rtv(p2p, 5.0, receipt_id=p2p.grn.id, rtv_ref="RMA-E3B-" + p2p.tag)
    r.with_user(p2p.controller).action_approve()
    r.with_user(p2p.keeper).action_ship()
    # the stock side is unchanged: out at the average cost
    assert abs(r.sudo().unit_cost - avg) < 0.01
    susp = p2p.suspense(source_ref=r.name, entry_type="rtv")
    assert abs(sum(susp.mapped("total_valuation")) - (-5.0 * avg)) < 0.05
    r.with_user(p2p.keeper).action_mark_credited("MUSHAK-67-" + p2p.tag)
    note = p2p.env["fix.vendor.note"].browse(r.vendor_note_res_id)
    assert note.invoice_id == bill
    assert note.amount == 7400.0  # 5 x the billed 1,480.00
    assert note.vat_amount == 1110.0  # the VAT those 5 bore on the bill
    assert note.tds_amount == round(bill.tds_amount * 5 / 20, 2)
    # the purchase-price variance is stated, not posted (no PPV account exists)
    assert abs(r.sudo().price_variance - round(5.0 * (avg - 1480.0), 2)) < 0.01


def test_e3_11_an_rtv_without_a_grn_raises_no_guessed_note(p2p):
    _bill(p2p)
    r = _rtv(p2p, 1.0, rtv_ref="RMA-E3C-" + p2p.tag, no_receipt_reason="Stock taken on")
    r.with_user(p2p.controller).action_approve()
    r.with_user(p2p.keeper).action_ship()
    r.with_user(p2p.keeper).action_mark_credited("MUSHAK-67C-" + p2p.tag)
    assert r.state == "credited" and not r.vendor_note_res_id
    assert "goods receipt" in r.vendor_note_status
