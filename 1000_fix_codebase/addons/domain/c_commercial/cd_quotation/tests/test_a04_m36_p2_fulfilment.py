# ruff: noqa: F811  (the c / p03 fixtures are imported from the M36 suite)
# Quote-to-cash P2 (12-13 Nov 2026): segments and their terms, the customer's
# withholding, the purchase-order rule, the billing plan, the fulfilment plan
# an accepted quotation runs (deliveries, service orders, contract scope,
# to-dos) and advances taken against the quotation.
from datetime import timedelta

import pytest
from odoo.addons.cd_quotation.tests.test_a04_m36_controls import (  # noqa: F401  (fixtures)
    _approved_quote,
    _quote,
    _sent_quote,
    c,
    p03,
)
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.exceptions import UserError, ValidationError


def _accept(c, monkeypatch, q):
    sent = []
    monkeypatch.setattr(
        fix_otp_util, "dispatch_otp", lambda phone, code, ttl, language="bn": sent.append(code)
    )
    q.with_user(c.author).action_send_acceptance_otp()
    q.with_user(c.author).action_verify_acceptance_otp(otp=sent[-1])
    assert q.state == "accepted", q.state
    return q


def _corporate(c, **kw):
    vals = {"name": "M36P2 Acme Ltd", "is_company": True, "phone": "01711000362"}
    vals.update(kw)
    return c.env["res.partner"].create(vals)


def _goods(c, name="M36P2 Laptop", price=50000.0):
    return c.env["product.product"].create(
        {"name": name, "lst_price": price, "type": "consu", "is_storable": True}
    )


def _device(c, serial):
    return c.env["fix.device"].create(
        {"device_model_id": c.model.id, "serial_number": serial, "owner_id": c.customer.id}
    )


# --------------------------------------------------------------------- segments
def test_a_segment_sets_the_starting_terms(c):
    consumer = _quote(c)
    assert consumer.segment == "consumer" and consumer.tds_rate == 0.0
    codes = set(consumer.payment_method_ids.mapped("code"))
    assert {"CASH", "BKASH", "ROCKET"} <= codes and "RTGS" not in codes

    acme = _corporate(c)
    corp = (
        c.env["fix.quotation"]
        .with_user(c.author)
        .create(
            {
                "customer_id": acme.id,
                "cost_amount": 100.0,
                "valid_until": c.today + timedelta(days=5),
                "quote_type": "contract",
                "operating_unit_id": c.ou.id,
            }
        )
    )
    assert corp.segment == "corporate" and corp.tds_rate == 5.0
    assert corp.payment_term_id == c.env.ref("account.account_payment_term_30days")
    corp_codes = set(corp.payment_method_ids.mapped("code"))
    assert {"BEFTN", "RTGS", "CHEQUE", "ON_ACCOUNT"} <= corp_codes and "CASH" not in corp_codes


def test_a_corporate_quote_shows_the_cash_it_will_actually_receive(c):
    acme = _corporate(c)
    q = _quote(c, customer_id=acme.id, segment="corporate", value=10000.0, expected_vds_rate=15.0)
    # 10,000 + 15% VAT = 11,500; the customer withholds VDS 1,500 and TDS 5% = 500
    assert (q.amount_total, q.expected_vds_amount, q.tds_amount) == (11500.0, 1500.0, 500.0)
    assert q.expected_net_receipt == 9500.0
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        q.with_user(c.author).write({"expected_vds_rate": 150.0})


# --------------------------------------------------------------------- PO rule
def test_a_customer_that_requires_its_po_is_not_accepted_without_it(c, monkeypatch):
    acme = _corporate(c, fix_po_required=True, fix_po_required_above=5000.0)
    q = _sent_quote(c, customer_id=acme.id)
    sent = []
    monkeypatch.setattr(
        fix_otp_util, "dispatch_otp", lambda phone, code, ttl, language="bn": sent.append(code)
    )
    q.with_user(c.author).action_send_acceptance_otp()
    with pytest.raises(UserError, match="purchase order"), c.env.cr.savepoint():
        q.with_user(c.author).action_verify_acceptance_otp(otp=sent[-1])
    assert q.state == "sent"
    q.with_user(c.author).write({"customer_po_ref": "PO-ACME-1"})
    q.with_user(c.author).action_verify_acceptance_otp(otp=sent[-1])
    assert q.state == "accepted"


def test_a_small_order_under_the_po_threshold_needs_no_po(c, monkeypatch):
    acme = _corporate(c, fix_po_required=True, fix_po_required_above=500000.0)
    q = _sent_quote(c, customer_id=acme.id)
    _accept(c, monkeypatch, q)


# --------------------------------------------------------------------- billing plan
def test_submit_fills_the_default_billing_plan(c):
    laptop = _goods(c, price=6000.0)
    q = _quote(
        c,
        quote_type="project",
        line_ids=[
            (0, 0, {"product_id": laptop.id, "line_type": "goods", "unit_price": 6000.0}),
            (
                0,
                0,
                {
                    "description": "Install & configure",
                    "line_type": "installation",
                    "unit_price": 4000.0,
                },
            ),
        ],
    )
    q.with_user(c.author).action_submit(justification="test")
    plan = [(b.kind, b.pct) for b in q.billing_line_ids]
    assert plan == [("on_delivery", 60.0), ("on_completion", 40.0)]
    assert sum(q.billing_line_ids.mapped("amount")) == q.value

    gov = _quote(
        c,
        quote_type="project",
        segment="gov_tender",
        line_ids=[
            (
                0,
                0,
                {"description": "Server AMC setup", "line_type": "service", "unit_price": 10000.0},
            )
        ],
    )
    gov._ensure_billing_plan()
    assert [(b.kind, b.pct) for b in gov.billing_line_ids] == [
        ("on_completion", 90.0),
        ("retention", 10.0),
    ]
    contract = _quote(c)
    contract._ensure_billing_plan()
    assert [(b.kind, b.pct) for b in contract.billing_line_ids] == [("recurring", 100.0)]


def test_a_plan_that_does_not_add_up_is_refused(c):
    q = _quote(
        c,
        billing_line_ids=[
            (0, 0, {"kind": "milestone", "pct": 50.0}),
            (0, 0, {"kind": "on_completion", "pct": 30.0}),
        ],
    )
    with pytest.raises(UserError, match="80.00%"), c.env.cr.savepoint():
        q.with_user(c.author).action_submit(justification="test")


def test_a_billing_plan_change_after_approval_needs_re_approval(c):
    q = _approved_quote(c)
    assert q.billing_line_ids
    q.billing_line_ids[:1].with_user(c.author).write({"note": "after go-live"})
    assert (q.state, q.approval_state) == ("draft", "none")


# --------------------------------------------------------------------- fulfilment
def test_an_accepted_goods_and_works_order_creates_its_documents(c, monkeypatch):
    ptype = c.env["stock.picking.type"].search([("code", "=", "outgoing")], limit=1)
    if not ptype:
        pytest.skip("no outgoing operation type in this database")
    laptop = _goods(c)
    printer = _device(c, "M36P2-PRN-1")
    site = c.env["res.partner"].create(
        {"name": "Banani branch", "parent_id": c.customer.id, "type": "delivery"}
    )
    q = _sent_quote(
        c,
        quote_type="project",
        picking_type_id=ptype.id,
        line_ids=[
            (
                0,
                0,
                {
                    "product_id": laptop.id,
                    "line_type": "goods",
                    "quantity": 2,
                    "unit_price": 50000.0,
                    "site_id": site.id,
                },
            ),
            (
                0,
                0,
                {
                    "description": "Printer repair on site",
                    "line_type": "service",
                    "unit_price": 3000.0,
                    "device_id": printer.id,
                },
            ),
            (
                0,
                0,
                {
                    "description": "Network cabling",
                    "line_type": "installation",
                    "unit_price": 8000.0,
                },
            ),
        ],
    )
    _accept(c, monkeypatch, q)
    kinds = {h.kind: h for h in q.handoff_ids}
    assert set(kinds) == {"delivery", "service_order", "task"}
    picking = c.env["stock.picking"].browse(kinds["delivery"].res_id)
    assert picking.partner_id == site and picking.state not in ("draft", "cancel")
    assert picking.move_ids.product_id == laptop and picking.move_ids.product_uom_qty == 2
    order = c.env["fix.service.order"].browse(kinds["service_order"].res_id)
    assert order.device_id == printer and order.customer_id == c.customer
    assert kinds["task"].state == "pending" and q.activity_ids
    assert q.converted_res_model == "fix.quotation.handoff" and q.converted_ref


def test_an_accepted_contract_quote_carries_its_scope_to_the_contract(c, monkeypatch):
    if "fix.contract" not in c.env:
        pytest.skip("M08 not installed")
    q = _sent_quote(
        c,
        line_ids=[
            (
                0,
                0,
                {
                    "description": "Printer AMC",
                    "line_type": "recurring",
                    "quantity": 4,
                    "unit_price": 3000.0,
                },
            ),
            (0, 0, {"description": "PM visit kit", "line_type": "fee", "unit_price": 1000.0}),
        ],
    )
    _accept(c, monkeypatch, q)
    contract = c.env["fix.contract"].browse(q.converted_res_id)
    assert contract.quotation_id == q and contract.payment_term_id == q.payment_term_id
    assert contract.scope_line_ids.mapped("description") == ["Printer AMC", "PM visit kit"]
    assert sum(contract.scope_line_ids.mapped("subtotal")) == q.value
    assert "contract" in q.handoff_ids.mapped("kind")
    with pytest.raises(UserError), c.env.cr.savepoint():
        contract.scope_line_ids[:1].with_user(c.author).write({"unit_price": 1.0})


def test_a_plan_share_is_drafted_as_an_invoice_once(c, monkeypatch):
    q = _sent_quote(
        c,
        quote_type="project",
        line_ids=[
            (
                0,
                0,
                {
                    "description": "Office fit-out",
                    "line_type": "installation",
                    "unit_price": 20000.0,
                },
            )
        ],
        billing_line_ids=[
            (0, 0, {"kind": "milestone", "pct": 40.0, "note": "design signed"}),
            (0, 0, {"kind": "on_completion", "pct": 60.0}),
        ],
    )
    _accept(c, monkeypatch, q)
    first = q.billing_line_ids.sorted("sequence")[:1]
    first.action_invoice()
    invoice = first.invoice_id
    assert first.state == "invoiced" and invoice.state == "draft"
    assert round(sum(invoice.line_ids.mapped("taxable_amount")), 2) == 8000.0
    assert invoice.customer_id == q.customer_id
    with pytest.raises(UserError, match="already invoiced"), c.env.cr.savepoint():
        first.action_invoice()
    # due by the quotation's payment term (immediate here), not the customer's net-30
    assert invoice._payment_terms_days() == 0
    with pytest.raises(UserError), c.env.cr.savepoint():
        first.with_user(c.author).write({"state": "planned"})


def test_an_engine_billed_share_is_not_drafted_from_the_plan(c, monkeypatch):
    q = _sent_quote(c)
    _accept(c, monkeypatch, q)
    q._ensure_billing_plan()
    with pytest.raises(UserError, match="contract billing"), c.env.cr.savepoint():
        q.billing_line_ids[:1].action_invoice()


# --------------------------------------------------------------------- advances
def test_an_advance_is_a_receipt_against_the_quotation(c):
    q = _sent_quote(c, advance_pct=30.0)
    assert q.advance_amount == round(q.amount_total * 0.3, 2)
    bkash = c.env.ref("cd_billing_engine.payment_method_bkash")
    rtgs = c.env.ref("cd_billing_engine.payment_method_rtgs")
    q.with_user(c.author).write(
        {"advance_entry_amount": 5000.0, "advance_entry_method_id": rtgs.id}
    )
    with (
        pytest.raises(UserError, match="does not offer|not a payment method"),
        c.env.cr.savepoint(),
    ):
        q.with_user(c.author).action_record_advance()
    q.with_user(c.author).write(
        {
            "advance_entry_amount": 5000.0,
            "advance_entry_method_id": bkash.id,
            "advance_entry_ref": "TRX9X8Y7",
        }
    )
    q.with_user(c.author).action_record_advance()
    receipt = q.advance_receipt_ids
    assert (receipt.amount, receipt.method, receipt.state) == (5000.0, "bkash", "draft")
    assert receipt.quotation_id == q and not q.advance_entry_amount
    assert "receipt" in q.handoff_ids.mapped("kind")
    q.with_user(c.author).write(
        {"advance_entry_amount": q.amount_total, "advance_entry_method_id": bkash.id}
    )
    receipt.sudo()._guarded().write({"state": "confirmed"})
    q.invalidate_recordset()
    with pytest.raises(UserError, match="exceed"), c.env.cr.savepoint():
        q.with_user(c.author).action_record_advance()


# --------------------------------------------------------------------- documents & screens
def test_the_quotation_documents_show_plan_withholding_and_advance(c):
    report = c.env.ref("cd_doc_suite.action_report_advance_request", raise_if_not_found=False)
    if not report:
        pytest.skip("cd_doc_suite is not installed")
    acme = _corporate(c)
    q = _quote(
        c, customer_id=acme.id, segment="corporate", expected_vds_rate=15.0, advance_pct=20.0
    )
    q._ensure_billing_plan()
    Report = c.env["ir.actions.report"].sudo()
    html = Report._render_qweb_html(report.report_name, q.ids)[0].decode()
    assert "ADVANCE PAYMENT REQUEST" in html and "not a tax invoice" in html
    assert "3,450.00" in html  # 20% of 17,250
    quote_html = Report._render_qweb_html("cd_doc_suite.report_quotation", q.ids)[0].decode()
    assert "Invoicing:" in quote_html and "Withholding at source" in quote_html


def test_the_billing_form_saves_the_plan_and_the_log_is_read_only(c, p03):
    q = _quote(c)
    res = p03(
        c.author,
        model="fix.quotation",
        record_id=q.id,
        values={},
        lines={
            "field": "billing_line_ids",
            "rows": [{"values": {"kind": "on_completion", "pct": 100.0}}],
            "removed": [],
        },
    )
    assert not res.get("error"), res
    assert q.billing_line_ids.kind == "on_completion"
    handoff = (
        c.env["fix.quotation.handoff"]
        .sudo()
        .create({"quotation_id": q.id, "kind": "task", "state": "pending"})
    )
    with pytest.raises(UserError), c.env.cr.savepoint():
        handoff.with_user(c.author).write({"state": "created"})
