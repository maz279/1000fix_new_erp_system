# A06 ERP audit (20 Nov 2026), stream P2P: the procure-to-pay money flow.
#
# D5 full FX, D2 GRNI 100503 / PPV 600007 / FX 500030, D8 match tolerance.
# Findings P01 P02 P05 P09 P12 P13 P14 P15 P41, X03 X14 X26 (M16/M42 F-numbers
# renamed P to avoid clashing with M41's). Every test reproduces the defect on
# the base code and passes on the fix; see the mutation notes per test.
from __future__ import annotations

import itertools
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

_SEQ = itertools.count(1)


def _acc(env, code, name, kind):
    Account = env["account.account"]
    company = env.company
    found = Account.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    return found or Account.create(
        {"code": code, "name": name, "account_type": kind, "company_ids": [(6, 0, [company.id])]}
    )


def _rate(env, currency, day, bdt_per_unit):
    Rate = env["res.currency.rate"]
    old = Rate.search(
        [("currency_id", "=", currency.id), ("name", "=", day), ("company_id", "=", env.company.id)]
    )
    old.unlink()
    Rate.create(
        {
            "currency_id": currency.id,
            "name": day,
            "company_id": env.company.id,
            "rate": 1.0 / bdt_per_unit,
        }
    )


@pytest.fixture
def p2p(odoo_env):
    env = odoo_env
    company = env.company
    icp = env["ir.config_parameter"].sudo()
    accounts = {
        "grni": _acc(env, "990503", "Test stock incoming (GRNI)", "asset_current"),
        "ppv": _acc(env, "990007", "Test purchase price variance", "expense"),
        "fx": _acc(env, "990030", "Test FX gain / loss", "expense"),
        "expense": _acc(env, "990600", "Test expense", "expense"),
        "lc": _acc(env, "990812", "Test LC settlement", "asset_current"),
        "tds": _acc(env, "990253", "Test TDS payable", "liability_current"),
        "vds": _acc(env, "990252", "Test VDS payable", "liability_current"),
        "vat": _acc(env, "990131", "Test input VAT", "asset_current"),
    }
    for param, code in (
        ("cd_ap_ext.account_code.grni", "990503"),
        ("cd_ap_ext.account_code.ppv", "990007"),
        ("cd_ap_ext.account_code.fx_gain_loss", "990030"),
        ("cd_ap_ext.account_code.expense", "990600"),
        ("cd_tax_engine_bd.account_code.tds_payable", "990253"),
        ("cd_tax_engine_bd.account_code.vds_payable", "990252"),
        ("cd_tax_engine_bd.vat_input_account_code", "990131"),
        ("cd_requisition.receipt_inspection_required", "0"),
    ):
        icp.set_param(param, code)
    usd = (
        env.ref("base.BDT")
        if env.company.currency_id == env.ref("base.USD")
        else env.ref("base.USD")
    )
    usd.active = True
    today = fields.Date.context_today(env.user)
    days = {"po": today - timedelta(days=10), "bill": today - timedelta(days=2), "pay": today}
    _rate(env, usd, days["po"], 110.0)
    _rate(env, usd, days["bill"], 120.0)
    _rate(env, usd, days["pay"], 125.0)
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    vendor = env["res.partner"].create({"name": "A06 P2P Dhaka Traders %d" % next(_SEQ)})
    env["fix.vendor.tax.profile"].create(
        {
            "partner_id": vendor.id,
            "taxpayer_type": "company",
            "tin": "123456789012",
            "bin": "9876543210123",
            "default_tds_category": "supply_of_goods",
        }
    )
    root = env["product.category"].create({"name": "A06 P2P Parts"})
    if "fix.supplier" in env:
        sup = env["fix.supplier"].create(
            {
                "name": vendor.name,
                "partner_id": vendor.id,
                "status": "active",
                "approved_category_ids": [(6, 0, root.ids)],
            }
        )
        for doc_type in ("trade_licence", "tin", "vat"):
            env["fix.supplier.document"].create(
                {"supplier_id": sup.id, "doc_type": doc_type, "state": "valid"}
            )
    product = env["product.product"].create({"name": "A06 P2P Logic Board", "categ_id": root.id})
    service = env["product.product"].create(
        {"name": "A06 P2P AC Servicing", "type": "service", "categ_id": root.id}
    )
    return {
        "env": env,
        "ou": ou,
        "usd": usd,
        "days": days,
        "accounts": accounts,
        "vendor": vendor,
        "product": product,
        "service": service,
    }


def _sent_po(p, lines, currency=None, rate=None):
    """lines: [(product, qty, unit price)]; approved and sent; `rate` stamps
    the order as if approved on an earlier day."""
    env = p["env"]
    po = env["fix.purchase.order"].create(
        {
            "operating_unit_id": p["ou"].id,
            "vendor_id": p["vendor"].id,
            "currency_id": (currency or env.company.currency_id).id,
            "line_ids": [
                (0, 0, {"product_id": pr.id, "qty_ordered": q, "unit_price": u})
                for pr, q, u in lines
            ],
        }
    )
    po.action_record_requisition_exception(reason="A06 P2P money test PO")
    if rate:
        po._guarded().write({"fx_rate": rate, "fx_rate_date": p["days"]["po"]})
    po._guarded().write(
        {
            "approval_state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": po._dofa_current_tier(),
            "dofa_approved_amount": po._dofa_amount(),
        }
    )
    po.action_send()
    return po


def _bill(p, po, lines, ref=None, day=None, currency=None, **vals):
    env = p["env"]
    return env["fix.vendor.invoice"].create(
        {
            "vendor_id": p["vendor"].id,
            "invoice_ref": ref or "P2P-%d" % next(_SEQ),
            "invoice_date": day or p["days"]["bill"],
            "requisition_id": po.id if po else False,
            "bill_type": "po" if po else vals.pop("bill_type", "non_po"),
            "currency_id": (currency or (po.currency_id if po else env.company.currency_id)).id,
            "operating_unit_id": p["ou"].id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": pr.id,
                        "description": pr.name,
                        "quantity": q,
                        "unit_price": u,
                        "tds_category": "supply_of_goods",
                    },
                )
                for pr, q, u in lines
            ],
            **vals,
        }
    )


def _post(bill):
    """The last approval's posting (the matrix is covered by the A08 suites)."""
    bill._guarded().write({"approval_state": "approved"})
    bill._post_approved_bill()
    return bill.move_id


def _by_account(move):
    out = {}
    for ml in move.line_ids:
        row = out.setdefault(ml.account_id.code, [0.0, 0.0, 0.0])
        row[0] += ml.debit
        row[1] += ml.credit
        row[2] += ml.amount_currency if ml.currency_id != ml.company_currency_id else 0.0
    return out


# ------------------------------------------------------------------ P29 / P01
def test_p29_po_stamps_its_rate_once(p2p):
    """Mutation: drop _a06_stamp_fx_rate from action_send -> fx_rate 0."""
    po = _sent_po(p2p, [(p2p["product"], 10, 100.0)], currency=p2p["usd"])
    assert po.fx_rate == 125.0 and po.fx_rate_date == p2p["days"]["pay"]
    assert po._dofa_amount() == 125000.0


def test_p01_usd_bill_posts_bdt_with_currency_grni_ppv_fx(p2p):
    """The defect: a USD 1,020 bill posted 1,020 as BDT, no amount_currency,
    TDS on 1,020. Now: BDT at the bill-date rate 120, GRNI cleared at the
    receipt value (PO rate 110), FX 500030 and PPV 600007 for the rest, AP
    with its USD figure, TDS on BDT (5 % x 1.5 non-filer uplift: the profile has no PSR).
    Mutations: line_total_bdt = line_total (P01) -> AP 1,020-ish; split
    without the fx leg (X14) -> PPV 12,400; GRNI at bill price (X03) -> 122,400."""
    po = _sent_po(p2p, [(p2p["product"], 10, 100.0)], currency=p2p["usd"], rate=110.0)
    po.action_record_receipt({po.line_ids.id: 10})
    assert po.receipt_ids.line_ids.unit_value_bdt == 11000.0
    bill = _bill(p2p, po, [(p2p["product"], 10, 102.0)])
    assert bill.match_state == "matched", bill.match_detail
    assert "default price tolerance" in bill.match_detail
    assert (bill.fx_rate, bill.subtotal_bdt, bill.tds_amount) == (120.0, 122400.0, 9180.0)
    assert (bill.total_payable_bdt, bill.total_payable) == (113220.0, 943.5)
    move = _post(bill)
    lines = _by_account(move)
    assert lines["990503"][:2] == [110000.0, 0.0] and lines["990503"][2] == 1000.0
    assert lines["990030"][:2] == [10200.0, 0.0]
    assert lines["990007"][:2] == [2200.0, 0.0]
    assert lines["990253"][:2] == [0.0, 9180.0]
    ap = move.line_ids.filtered(lambda ml: ml.currency_id == p2p["usd"] and ml.credit)
    assert (ap.credit, ap.amount_currency) == (113220.0, -943.5)
    assert sum(move.line_ids.mapped("debit")) == sum(move.line_ids.mapped("credit"))
    wht = bill.withholding_line_ids
    assert wht.currency_id == p2p["env"].company.currency_id and wht.base_amount == 122400.0


def test_p01_approval_band_reads_bdt(p2p):
    """USD 5,000 at 120 is BDT 600,000: the BDT band, not the USD one.
    Mutation: _ap_levels reads gross_amount -> the USD band."""
    po = _sent_po(p2p, [(p2p["product"], 50, 100.0)], currency=p2p["usd"], rate=120.0)
    po.action_record_receipt({po.line_ids.id: 50})
    bill = _bill(p2p, po, [(p2p["product"], 50, 100.0)])
    assert bill.gross_amount == 5000.0 and bill.gross_amount_bdt == 600000.0
    assert bill._ap_levels() == bill._ap_levels(amount=600000.0)
    assert bill._ap_levels() != bill._ap_levels(amount=5000.0)


def test_p01_settlement_books_fx_on_payment(p2p):
    """Paid at 125 what was booked at 120: AP cleared at its booked BDT with
    the USD figure, the difference is FX loss (the LC settlement API).
    Mutation: settlement clears AP at the paid amount -> AP left 4,717.50 open."""
    po = _sent_po(p2p, [(p2p["product"], 10, 100.0)], currency=p2p["usd"], rate=110.0)
    po.action_record_receipt({po.line_ids.id: 10})
    bill = _bill(p2p, po, [(p2p["product"], 10, 102.0)])
    _post(bill)
    paid = bill._ap_payable_bdt_on(p2p["days"]["pay"])
    assert paid == 117937.5  # 943.50 x 125
    journal = bill.move_id.journal_id
    move = bill._ap_settle_external(
        paid, p2p["accounts"]["lc"], journal, "LC/TEST/1", p2p["days"]["pay"], "test"
    )
    lines = _by_account(move)
    ap_code = bill.move_id.line_ids.filtered(lambda ml: ml.currency_id == p2p["usd"] and ml.credit)
    ap_code = ap_code.account_id.code
    assert lines[ap_code][:2] == [113220.0, 0.0] and lines[ap_code][2] == 943.5
    assert lines["990030"][:2] == [4717.5, 0.0]
    assert lines["990812"][:2] == [0.0, 117937.5]
    assert bill.payment_state == "paid"
    with pytest.raises(UserError, match="already"), p2p["env"].cr.savepoint():
        bill._ap_settle_external(
            paid, p2p["accounts"]["lc"], journal, "LC/TEST/2", p2p["days"]["pay"], "test"
        )


def test_p01_payment_request_is_bdt_at_the_day_rate(p2p):
    po = _sent_po(p2p, [(p2p["product"], 10, 100.0)], currency=p2p["usd"], rate=110.0)
    po.action_record_receipt({po.line_ids.id: 10})
    bill = _bill(p2p, po, [(p2p["product"], 10, 100.0)])
    _post(bill)
    bill.action_request_payment()
    lock = p2p["env"]["fix.ap.bill.payment"].search([("bill_id", "=", bill.id)])
    assert lock.amount == round(bill.total_payable * 125.0, 2)


def test_p01_missing_rate_fails_closed(p2p):
    env = p2p["env"]
    gbp = env.ref("base.GBP")
    gbp.active = True
    env["res.currency.rate"].search([("currency_id", "=", gbp.id)]).unlink()
    from odoo.addons.cd_requisition.models.fix_requisition import bdt_rate

    with pytest.raises(UserError, match="No GBP exchange rate"):
        bdt_rate(env, gbp, env.company, p2p["days"]["pay"])


# ------------------------------------------------------------------ P02
def test_p02_bill_in_another_currency_blocks(p2p):
    """Mutation: drop the currency check -> a BDT 1,000 bill matches USD 1,000."""
    po = _sent_po(p2p, [(p2p["product"], 10, 100.0)], currency=p2p["usd"], rate=110.0)
    po.action_record_receipt({po.line_ids.id: 10})
    bill = _bill(p2p, po, [(p2p["product"], 10, 100.0)], currency=p2p["env"].company.currency_id)
    assert bill.match_state == "blocked"
    assert "but purchase order" in bill.match_detail


# ------------------------------------------------------------------ P12 / D8
def test_p12_bdt_bill_price_difference_is_ppv(p2p):
    """Mutation: GRNI at the bill price -> 990503 = 10,100, no 990007."""
    po = _sent_po(p2p, [(p2p["product"], 10, 1000.0)])
    po.action_record_receipt({po.line_ids.id: 10})
    bill = _bill(p2p, po, [(p2p["product"], 10, 1010.0)])
    assert bill.match_state == "matched"
    lines = _by_account(_post(bill))
    assert lines["990503"][:2] == [10000.0, 0.0]
    assert lines["990007"][:2] == [100.0, 0.0]


def test_d8_default_tolerance_larger_of_two_percent_or_500(p2p):
    """D8: +2 % or +BDT 500 a unit, whichever is larger; qty exact.
    Mutations: min() in tolerance_allowance -> 1,500 blocks; no default
    limits -> 1,010 blocks."""
    po = _sent_po(p2p, [(p2p["product"], 2, 1000.0)])
    po.action_record_receipt({po.line_ids.id: 2})
    assert _bill(p2p, po, [(p2p["product"], 1, 1500.0)]).match_state == "matched"
    po2 = _sent_po(p2p, [(p2p["product"], 2, 1000.0)])
    po2.action_record_receipt({po2.line_ids.id: 2})
    over = _bill(p2p, po2, [(p2p["product"], 1, 1500.02)])
    assert over.match_state == "blocked" and "price above PO" in over.match_detail
    assert _bill(p2p, po2, [(p2p["product"], 3, 1000.0)]).match_state == "blocked"
    p2p["env"]["ir.config_parameter"].set_param("cd_ap_ext.match_price_tolerance_abs", "0")
    p2p["env"]["ir.config_parameter"].set_param("cd_ap_ext.match_price_tolerance_pct", "0")
    po3 = _sent_po(p2p, [(p2p["product"], 2, 1000.0)])
    po3.action_record_receipt({po3.line_ids.id: 2})
    assert _bill(p2p, po3, [(p2p["product"], 1, 1010.0)]).match_state == "blocked"


# ------------------------------------------------------------------ P41
def test_p41_product_on_two_lines_billed_at_each_lines_price(p2p):
    """5 at 1,000 and 5 at 3,000 of one part: billing the first five at 3,000
    was allowed (every unit at the dearest line's price). Mutation: drop the
    value check -> matched (each unit price is within the dearest line)."""
    po = _sent_po(p2p, [(p2p["product"], 5, 1000.0), (p2p["product"], 5, 3000.0)])
    po.action_record_receipt({line.id: 5 for line in po.line_ids})
    first = _bill(p2p, po, [(p2p["product"], 5, 3000.0)])
    assert first.match_state == "blocked" and "price above PO" in first.match_detail
    first._guarded().write({"approval_state": "rejected"})
    fair = _bill(p2p, po, [(p2p["product"], 5, 1000.0), (p2p["product"], 5, 3000.0)])
    assert fair.match_state == "matched", fair.match_detail


# ------------------------------------------------------------------ P05 / X26
def test_p05_service_entry_posts_expense_against_grni_and_bill_clears_it(p2p):
    """Mutation: no posting on confirm -> no move, GRNI only ever debited."""
    env = p2p["env"]
    po = _sent_po(p2p, [(p2p["service"], 4, 2500.0)])
    entry = env["fix.purchase.service.entry"].create(
        {
            "purchase_order_id": po.id,
            "po_line_id": po.line_ids.id,
            "qty_confirmed": 4,
            "description": "Four AC units serviced at the Mirpur branch",
        }
    )
    entry.action_confirm()
    lines = _by_account(entry.move_id)
    assert lines["990503"][:2] == [0.0, 10000.0]
    expense = {code: row for code, row in lines.items() if code != "990503"}
    assert [row[:2] for row in expense.values()] == [[10000.0, 0.0]]
    bill = _bill(p2p, po, [(p2p["service"], 4, 2500.0)])
    _post(bill)
    grni = env["account.move.line"].search(
        [
            ("account_id", "=", p2p["accounts"]["grni"].id),
            ("move_id", "in", (entry.move_id | bill.move_id).ids),
        ]
    )
    assert sum(grni.mapped("balance")) == 0.0


def test_x26_grni_as_at_ties_to_the_account(p2p):
    """X26 / P13: received 10 (service entries), billed 4: the accrual is 6
    units at the receipt value and equals the GRNI balance of the order; a
    date before the bill shows all 10. Mutations: received (not accepted) at
    the live PO price -> 6 x 2,600 after a price amendment; no as_of on bills
    -> the earlier date shows 6."""
    env = p2p["env"]
    po = _sent_po(p2p, [(p2p["service"], 10, 2500.0)])
    entry = env["fix.purchase.service.entry"].create(
        {
            "purchase_order_id": po.id,
            "po_line_id": po.line_ids.id,
            "qty_confirmed": 10,
            "description": "Ten AC units serviced",
        }
    )
    entry.action_confirm()
    tomorrow = p2p["days"]["pay"] + timedelta(days=1)
    bill = _bill(p2p, po, [(p2p["service"], 4, 2500.0)], day=tomorrow)
    _post(bill)
    from odoo.addons.cd_ap_ext.models.fix_ap_grni import grni_rows_as_of

    mine = [r for r in grni_rows_as_of(env, tomorrow) if r["order_ref"] == po.name]
    assert [(r["open_qty"], r["accrual"]) for r in mine] == [(6.0, 15000.0)]
    balance = sum(
        env["account.move.line"]
        .search(
            [
                ("account_id", "=", p2p["accounts"]["grni"].id),
                ("move_id", "in", (entry.move_id | bill.move_id).ids),
            ]
        )
        .mapped("balance")
    )
    assert -balance == 15000.0
    before = [r for r in grni_rows_as_of(env, p2p["days"]["pay"]) if r["order_ref"] == po.name]
    assert [r["open_qty"] for r in before] == [10.0]


# ------------------------------------------------------------------ P09
def test_p09_non_po_bill_buys_no_stock_and_needs_an_active_supplier(p2p):
    """Mutations: drop _fix_check_non_po -> both bills submit."""
    env = p2p["env"]
    stock = env["product.product"].create({"name": "A06 P2P Stocked Part", "is_storable": True})
    bill = _bill(p2p, None, [(stock, 1, 500.0)])
    with pytest.raises(UserError, match="buys stock parts"), env.cr.savepoint():
        bill.action_submit_approval()
    stranger = env["res.partner"].create({"name": "A06 P2P Unregistered Landlord"})
    rent = _bill(p2p, None, [(p2p["service"], 1, 500.0)], vendor_id=stranger.id)
    if "fix.supplier" in env:
        with pytest.raises(UserError, match="no supplier record"), env.cr.savepoint():
            rent.action_submit_approval()
        rent.action_approve_non_po_exception(reason="Landlord of the Mirpur branch, lease LS-17")
        assert rent.non_po_exception_by_id


# ------------------------------------------------------------------ P14 / P15
def test_p14_duplicate_reference_is_normalised(p2p):
    """Mutation: exact-ref duplicate search -> 'inv 001' slips past 'INV-001'."""
    po = _sent_po(p2p, [(p2p["product"], 10, 100.0)])
    po.action_record_receipt({po.line_ids.id: 10})
    _bill(p2p, po, [(p2p["product"], 5, 100.0)], ref="INV-001")
    second = _bill(p2p, po, [(p2p["product"], 5, 100.0)], ref="inv 001")
    assert second._duplicates()


def test_p15_bill_takes_the_order_payment_terms(p2p):
    po = _sent_po(p2p, [(p2p["product"], 1, 100.0)])
    po._guarded().write({"payment_terms": "Net 45 days"})
    bill = _bill(p2p, po, [(p2p["product"], 1, 100.0)])
    assert bill.payment_term_days == 45


# ------------------------------------------------------------------ X11
def test_x11_import_bill_needs_a_received_import_and_no_po(p2p):
    """An import bill (no PO) is matched against its received import, never
    paid on the approval matrix alone like a non-PO bill."""
    from odoo.exceptions import ValidationError

    env = p2p["env"]
    bill = _bill(p2p, None, [(p2p["product"], 1, 100.0)], bill_type="import")
    assert bill.match_state == "unmatched" and "No received import" in bill.match_detail
    with pytest.raises(UserError, match="G3-06"), env.cr.savepoint():
        bill.action_submit_approval()
    po = _sent_po(p2p, [(p2p["product"], 1, 100.0)])
    with pytest.raises(ValidationError), env.cr.savepoint():
        bill.write({"requisition_id": po.id})


# ------------------------------------------------------------------ D5 advances
def test_d5_foreign_advance_is_taken_back_at_its_own_bdt(p2p):
    """A USD 400 advance paid at BDT 110 (44,000) taken back on a USD bill at
    120: the advance account is credited 44,000 (what was paid), the payable
    is reduced at 120 (48,000), the 4,000 difference is FX gain. Mutation:
    credit the advance at advance_applied (its USD figure) -> unbalanced /
    residue on the advance account."""
    env = p2p["env"]
    from odoo.addons.cd_ap_ext.models.ap_gl import ap_journal, post_ap_move

    adv_acc = _acc(env, "990255", "Test advances to suppliers", "asset_current")
    env["ir.config_parameter"].set_param("cd_ap_ext.account_code.supplier_advance", "990255")
    po = _sent_po(p2p, [(p2p["product"], 10, 100.0)], currency=p2p["usd"], rate=110.0)
    pi = env["fix.purchase.proforma"].create(
        {"purchase_order_id": po.id, "proforma_no": "PI-P2P-%s" % po.id, "amount": po.amount_total}
    )
    pi.action_approve()
    adv = env["fix.purchase.advance"].create({"proforma_id": pi.id, "amount": 400.0})
    partner = p2p["vendor"].commercial_partner_id
    paid = post_ap_move(
        env,
        env.company,
        ap_journal(env, env.company, "purchase"),
        p2p["days"]["po"],
        "Advance paid (test)",
        [
            (adv_acc, "Advance paid", 44000.0, 0.0, partner),
            (p2p["accounts"]["lc"], "Bank (test)", 0.0, 44000.0, partner),
        ],
        p2p["ou"],
    )
    adv._guarded().write({"state": "paid", "payment_move_id": paid.id})
    po.action_record_receipt({po.line_ids.id: 10})
    bill = _bill(p2p, po, [(p2p["product"], 10, 100.0)])
    move = _post(bill)
    lines = _by_account(move)
    assert bill.advance_applied == 400.0
    assert lines["990255"][:2] == [0.0, 44000.0] and lines["990255"][2] == -400.0
    # FX: 10,000 rate loss on the goods (110 -> 120), 4,000 gain on the advance
    assert lines["990030"][:2] == [10000.0, 4000.0]
    assert sum(move.line_ids.mapped("debit")) == pytest.approx(sum(move.line_ids.mapped("credit")))


# ------------------------------------------- A06 integration: non-stock goods
def test_integration_non_stock_goods_receipt_credits_grni_and_the_bill_clears_it(p2p):
    """Goods on a PO that are not spare parts make no M15 receipt, so nothing
    credited GRNI while the bill debited it. The M16 receipt now accrues them
    (Dr expense / Cr GRNI at the receipt value) and the bill nets GRNI to 0.
    Mutation: no accrual on posting -> GRNI keeps the bill's 1,000 debit."""
    env = p2p["env"]
    po = _sent_po(p2p, [(p2p["product"], 10, 100.0)])
    po.action_record_receipt({po.line_ids.id: 10})
    receipt = po.receipt_ids
    accrual = receipt.ap_grni_move_id
    assert accrual, "the non-stock goods receipt posted no GRNI accrual"
    lines = _by_account(accrual)
    assert lines["990503"][:2] == [0.0, 1000.0]
    bill = _bill(p2p, po, [(p2p["product"], 10, 100.0)])
    _post(bill)
    grni = env["account.move.line"].search(
        [
            ("account_id", "=", p2p["accounts"]["grni"].id),
            ("move_id", "in", (accrual | bill.move_id).ids),
        ]
    )
    assert sum(grni.mapped("balance")) == 0.0


def test_integration_a_service_entry_is_accrued_once(p2p):
    """The service entry's own receipt is not accrued a second time."""
    env = p2p["env"]
    po = _sent_po(p2p, [(p2p["service"], 2, 500.0)])
    entry = env["fix.purchase.service.entry"].create(
        {
            "purchase_order_id": po.id,
            "po_line_id": po.line_ids.id,
            "qty_confirmed": 2,
            "description": "Two AC units serviced",
        }
    )
    entry.action_confirm()
    assert entry.move_id and not entry.receipt_id.ap_grni_move_id
