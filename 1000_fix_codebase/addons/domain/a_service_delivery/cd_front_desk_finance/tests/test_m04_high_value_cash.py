# ruff: noqa: F811  (the posting suite's fixtures are imported and used as parameters)
"""M04 capture audit (18 Nov 2026): the high-value cash ID check.

FR-FRD-019 (P0) / BRU-FRD-04: cash receipts above the statutory threshold
need the customer's NID; BRU-FRD-13: the PDPA transparency notice is
presented and the consent recorded BEFORE the NID is written; BRU-FRD-14: the
NID lives in the Bangladesh-resident store only.

Before: a counter sale or basket posts straight to the books and never
becomes an M20 receipt, so M20's NID rule never ran at the counter. A BDT
60,000 cash sale confirmed with no NID and no consent, and Payment Capture
had nothing to record them with.
"""

from __future__ import annotations

import pytest
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import m04  # noqa: F401
from odoo.addons.cd_front_desk.tests.test_m04_submodule_capture import (  # noqa: F401
    _form_values,
    screens,
    ui,
)
from odoo.addons.cd_front_desk_finance.tests.test_counter_sale_posting import fin  # noqa: F401
from odoo.exceptions import AccessError, UserError

THRESHOLD = 50000.0
NID = "1990123456789"  # 13 digits: not a National ID format the check accepts
NID17 = "19901234567890123"


@pytest.fixture
def hv(fin):
    m = fin
    env = m.env
    # M51 master data: a company row pins the threshold for this test
    env["fix.tax.parameter"].sudo().create(
        {
            "company_id": env.company.id,
            "key": "nid_cash_threshold",
            "value": THRESHOLD,
            "date_from": "2020-01-01",
        }
    )
    m.notice = (
        env["fix.transparency.notice"]
        .sudo()
        .create(
            {
                "version": "9.%d" % m.branch.id,
                "text_en": "Why we take your NID for cash above BDT 50,000.",
                "text_bn": "নগদ লেনদেনে এনআইডি কেন নেওয়া হয়।",
            }
        )
    )
    m.big = m.env["product.product"].create(
        {"name": "M04 HV laptop board", "list_price": 1000.0, "type": "consu"}
    )
    m.shift_rec = m.shift()
    return m


def _cash_sale(m, price=60000.0, method="cash", customer=True):
    sale = m.sale(None, price=price, method=method)
    sale.sudo().write(
        {
            "product_id": m.big.id,
            "unit_price": price,
            "tendered_amount": price if method == "cash" else 0.0,
            "transaction_ref": False if method == "cash" else "TRX-HV-1",
            "customer_id": m.customer.id if customer else False,
        }
    )
    return sale


def _check(m, ui, screens, user=None, **vals):
    cfg = screens["M04-form-idcheck"]
    base = {"partner_id": m.customer.id, "notice_version_id": m.notice.id, "notice_presented": True}
    base.update(vals)
    return ui.write(user or m.cashier, model="fix.cash.id.check", values=_form_values(cfg, base))


def test_cash_above_the_threshold_is_refused_without_the_customers_nid(hv):
    m = hv
    sale = _cash_sale(m)
    with pytest.raises(UserError, match="High-Value Cash ID Check"), m.env.cr.savepoint():
        sale.with_user(m.cashier).action_confirm()
    assert sale.state == "draft"


def test_the_counter_records_consent_then_nid_and_the_sale_confirms(hv, ui, screens):
    m = hv
    sale = _cash_sale(m)
    res = _check(m, ui, screens, sale_id=sale.id, nid_number=NID17)
    assert "error" not in res, res
    check = m.env["fix.cash.id.check"].browse(res["id"])
    assert check.name.startswith("HVC/") and check.amount == 60000.0
    assert check.threshold == THRESHOLD and check.recorded_by_id == m.cashier
    # BRU-FRD-13: the consent is against the notice shown
    consent = check.consent_id
    assert consent.partner_id == m.customer and consent.notice_version_id == m.notice
    assert (consent.purpose, consent.channel, consent.state) == (
        "high_value_cash_id",
        "counter",
        "granted",
    )
    # BRU-FRD-14: the NID went to the identity document; the check keeps 4 digits
    doc = check.identity_document_id
    assert doc.partner_id == m.customer and doc.document_type == "nid_17"
    assert check.nid_last4 == NID17[-4:]
    m.env.flush_all()
    m.env.cr.execute(
        "SELECT row_to_json(c)::text FROM fix_cash_id_check c WHERE id = %s", [check.id]
    )
    assert NID17 not in m.env.cr.fetchone()[0]
    assert not check.nid_number
    # consent first, then the NID; the NID capture is on the PDPA record
    assert consent.create_date <= doc.create_date and consent.id
    rec = (
        m.env["fix.processing.record"]
        .sudo()
        .search([("consent_id", "=", consent.id), ("source", "=", "counter_id_check")])
    )
    assert rec.lawful_basis == "legal_obligation" and rec.party_id == m.customer
    res = ui.action(m.cashier, model="fix.counter.sale", ids=[sale.id], method="action_confirm")
    assert res["success"], res
    sale.invalidate_recordset()
    assert sale.state == "confirmed"
    listed = ui.records(m.cashier, model="fix.cash.id.check", cols=["name", "nid_last4"])
    assert check.id in {r["id"] for r in listed["rows"]}


def test_no_nid_is_taken_before_the_notice_is_shown(hv, ui, screens):
    m = hv
    sale = _cash_sale(m)
    docs_before = (
        m.env["fix.identity.document"].sudo().search_count([("partner_id", "=", m.customer.id)])
    )
    res = _check(m, ui, screens, sale_id=sale.id, nid_number=NID17, notice_presented=False)
    assert "error" in res and "BRU-FRD-13" in res["error"]
    assert (
        m.env["fix.identity.document"].sudo().search_count([("partner_id", "=", m.customer.id)])
        == docs_before
    )
    res = _check(m, ui, screens, sale_id=sale.id)
    assert "error" in res and "NID" in res["error"]
    res = _check(m, ui, screens, sale_id=sale.id, nid_number=NID)
    assert "error" in res and "10" in res["error"]


def test_no_nid_is_collected_where_the_law_does_not_ask(hv, ui, screens):
    m = hv
    small = _cash_sale(m, price=40000.0)
    res = _check(m, ui, screens, sale_id=small.id, nid_number=NID17)
    assert "error" in res and "no NID is needed" in res["error"]
    small.with_user(m.cashier).action_confirm()
    assert small.state == "confirmed"
    wallet = _cash_sale(m, method="bkash")
    res = _check(m, ui, screens, sale_id=wallet.id, nid_number=NID17)
    assert "error" in res and "not paid in cash" in res["error"]
    wallet.with_user(m.cashier).action_confirm()
    assert wallet.state == "confirmed"


def test_a_cash_basket_above_the_threshold_needs_its_check(hv, ui, screens):
    m = hv
    cash = m.env["fix.payment.method"].search([("code", "=", "CASH")])
    basket = (
        m.env["fix.counter.basket"]
        .with_user(m.cashier)
        .create(
            {
                "operating_unit_id": m.ou.id,
                "branch_id": m.branch.id,
                "payment_method_id": cash.id,
                "tendered_amount": 60000.0,
                "line_ids": [
                    (0, 0, {"product_id": m.product.id, "quantity": 1, "unit_price": 30000.0}),
                    (0, 0, {"product_id": m.product.id, "quantity": 1, "unit_price": 30000.0}),
                ],
            }
        )
    )
    with pytest.raises(UserError, match="High-Value Cash ID Check"), m.env.cr.savepoint():
        basket.action_confirm()
    assert basket.state == "draft" and not basket.sale_ids
    res = _check(m, ui, screens, basket_id=basket.id, nid_number="1234567890")
    assert "error" not in res, res
    check = m.env["fix.cash.id.check"].browse(res["id"])
    assert check.basket_id == basket and check.identity_document_id.document_type == "nid_10"
    basket.invalidate_recordset()
    assert basket.customer_id == m.customer  # the check names who paid
    basket.action_confirm()
    assert basket.state == "confirmed" and len(basket.sale_ids) == 2


def test_a_check_is_evidence_and_only_the_till_records_it(hv, ui, screens):
    m = hv
    sale = _cash_sale(m)
    assert "error" in _check(m, ui, screens, user=m.plain, sale_id=sale.id, nid_number=NID17)
    with pytest.raises(AccessError), m.env.cr.savepoint():
        m.env["fix.cash.id.check"].with_user(m.plain).create(
            {
                "sale_id": sale.id,
                "partner_id": m.customer.id,
                "notice_version_id": m.notice.id,
                "notice_presented": True,
                "nid_number": NID17,
            }
        )
    check = m.env["fix.cash.id.check"].browse(
        _check(m, ui, screens, sale_id=sale.id, nid_number=NID17)["id"]
    )
    with pytest.raises(UserError, match="not changed"), m.env.cr.savepoint():
        check.with_user(m.manager).write({"partner_id": m.plain.partner_id.id})
    with pytest.raises(UserError, match="never deleted"), m.env.cr.savepoint():
        check.with_user(m.manager).unlink()
    # one check per sale
    res = _check(m, ui, screens, sale_id=sale.id, nid_number=NID17)
    assert "error" in res and "already" in res["error"]


def test_the_check_is_for_the_customer_on_the_sale(hv, ui, screens):
    m = hv
    sale = _cash_sale(m)
    other = m.env["res.partner"].create({"name": "M04 HV someone else"})
    res = _check(m, ui, screens, partner_id=other.id, sale_id=sale.id, nid_number=NID17)
    assert "error" in res and "same customer" in res["error"]
    # an NID already on file is used without retyping it
    on_file = (
        m.env["fix.identity.document"]
        .sudo()
        .create(
            {
                "partner_id": m.customer.id,
                "document_type": "nid_10",
                "document_number": "9876543210",
            }
        )
    )
    res = _check(m, ui, screens, sale_id=sale.id, identity_document_id=on_file.id)
    assert "error" not in res, res
    check = m.env["fix.cash.id.check"].browse(res["id"])
    assert check.identity_document_id == on_file and not check.nid_last4
    # someone else's NID on file is refused
    sale2 = _cash_sale(m)
    theirs = (
        m.env["fix.identity.document"]
        .sudo()
        .create(
            {"partner_id": other.id, "document_type": "nid_10", "document_number": "1112223334"}
        )
    )
    res = _check(m, ui, screens, sale_id=sale2.id, identity_document_id=theirs.id)
    assert "error" in res and "own" in res["error"]
