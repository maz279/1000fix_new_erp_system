# Quote-to-cash finance (M20): customer TDS / AIT certificates and receipts
# on the one payment-method list.
#
# TDS: a corporate customer deducts income tax at source (ITA 2023 s.89/s.90)
# and certifies it. The certificate is prepared by one accountant, verified by
# another, and settled Dr AIT receivable / Cr AR, which clears that part of the
# invoice residual. Run as NON-ADMIN users holding the real finance roles
# (the c fixture of the A08 control suite).
#
# Receipts: fix.ar.receipt.payment_method_id (fix.payment.method) sets the
# tender `method` (the GL role key); a mismatch and On Account are refused.
import types
import uuid
from datetime import date

import pytest
from odoo.addons.cd_billing_engine.tests.test_a08_m20_controls import (  # noqa: F401
    as_,
    c,
    c_raw,
    inv,
    lines,
    rcpt,
)
from odoo.exceptions import AccessError, UserError, ValidationError

AIT_CODE = "136100"
PARAM = "cd_billing_engine.account_code.ait_receivable"


@pytest.fixture
def ait(c):  # noqa: F811
    """The AIT receivable account, named to the engine by its parameter."""
    account = (
        c.env["account.account"]
        .with_company(c.company)
        .create(
            {
                "name": "Advance Income Tax (TDS by customers)",
                "code": AIT_CODE,
                "account_type": "asset_current",
                "company_ids": [(6, 0, c.company.ids)],
            }
        )
    )
    c.env["ir.config_parameter"].sudo().set_param(PARAM, AIT_CODE)
    return account


def tds(c, user, invoice, amount, no=None, section="s90"):  # noqa: F811
    return as_(c, user)["fix.tds.certificate.received"].create(
        {
            "invoice_id": invoice.id,
            "certificate_no": no or "TDS-%s" % uuid.uuid4().hex[:6],
            "certificate_date": date.today(),
            "tax_section": section,
            "tds_amount": amount,
            "customer_tin": "123456789012",
        }
    )


# ============================================================ TDS proper path
def test_tds_01_verified_by_another_then_settled_clears_residual_and_posts_gl(c, ait):  # noqa: F811
    i = inv(c)  # 10,000 + 15% VAT = 11,500
    cert = tds(c, c.acct, i, 1000.0)
    assert cert.state == "draft" and cert.name.startswith("TDS/")
    assert cert.company_id == c.company and cert.operating_unit_id == c.ou
    assert cert.prepared_by_id == c.acct
    cert.with_user(c.acct2).action_verify()
    assert cert.state == "verified" and cert.verified_by_id == c.acct2
    cert.with_user(c.acct2).action_settle()
    assert cert.state == "settled" and cert.settled_move_id.state == "posted"
    assert lines(cert.settled_move_id) == sorted([(AIT_CODE, 1000.0, 0.0), ("121000", 0.0, 1000.0)])
    ar_line = cert.settled_move_id.line_ids.filtered(lambda ln: ln.credit)
    assert ar_line.partner_id == c.customer
    assert i.tds_settled_amount == 1000.0
    assert i.amount_residual == 10500.0 and i.state == "issued"
    # the cash part pays the rest; the invoice closes on the two together
    r = rcpt(c, c.acct, 10500.0)
    as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": i.id, "amount": 10500.0}
    )
    assert i.amount_residual == 0.0 and i.state == "paid"


def test_tds_02_settling_the_last_open_part_closes_the_invoice(c, ait):  # noqa: F811
    i = inv(c)
    r = rcpt(c, c.acct, 10350.0)
    as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": i.id, "amount": 10350.0}
    )
    cert = tds(c, c.acct, i, 1150.0, section="s89")
    cert.with_user(c.acct2).action_verify()
    cert.with_user(c.acct2).action_settle()
    assert i.amount_residual == 0.0 and i.state == "paid"
    assert "TDS certificates %s" % cert.certificate_no in i._settlement_evidence()


# ============================================================ TDS refusals
def test_tds_03_preparer_cannot_verify(c, ait):  # noqa: F811
    i = inv(c)
    cert = tds(c, c.acct, i, 1000.0)
    with pytest.raises(AccessError):
        cert.action_verify()
    assert cert.state == "draft"
    with pytest.raises(UserError):
        cert.action_settle()  # not verified


def test_tds_04_amount_above_the_open_residual_refused(c, ait):  # noqa: F811
    i = inv(c)
    # a refused create is rolled back by the request; here, by a savepoint
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        tds(c, c.acct, i, 11500.01)
    tds(c, c.acct, i, 6000.0)
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        tds(c, c.acct, i, 5500.01)  # the two together exceed what is open
    tds(c, c.acct, i, 5500.0)  # exactly what is open is accepted
    # money received after the certificate was verified leaves less open:
    # settlement re-checks against the residual of the day
    i2 = inv(c)
    cert = tds(c, c.acct, i2, 1500.0)
    cert.with_user(c.acct2).action_verify()
    r = rcpt(c, c.acct, 11000.0)
    as_(c, c.acct)["fix.ar.allocation"].create(
        {"receipt_id": r.id, "invoice_id": i2.id, "amount": 11000.0}
    )
    with pytest.raises(UserError):
        cert.with_user(c.acct2).action_settle()
    assert cert.state == "verified" and i2.tds_settled_amount == 0.0


def test_tds_05_guarded_fields_cannot_be_written(c, ait):  # noqa: F811
    i = inv(c)
    cert = tds(c, c.acct, i, 1000.0)
    for vals in (
        {"state": "settled"},
        {"state": "verified"},
        {"prepared_by_id": c.acct2.id},
        {"verified_by_id": c.acct2.id},
        {"settled_at": "2026-11-01 00:00:00"},
    ):
        with pytest.raises(UserError):
            cert.write(vals)
    assert cert.state == "draft" and i.tds_settled_amount == 0.0
    move = c.env["account.move"].search([], limit=1)
    if move:
        with pytest.raises(UserError):
            cert.write({"settled_move_id": move.id})
    with pytest.raises(UserError):
        as_(c, c.acct)["fix.tds.certificate.received"].create(
            {
                "invoice_id": i.id,
                "certificate_no": "FORGED-1",
                "certificate_date": date.today(),
                "tds_amount": 100.0,
                "state": "settled",
            }
        )


def test_tds_06_certificate_frozen_once_verified(c, ait):  # noqa: F811
    i = inv(c)
    cert = tds(c, c.acct, i, 500.0)
    cert.write({"tds_amount": 600.0})  # a draft is still the preparer's
    cert.with_user(c.acct2).action_verify()
    for vals in ({"tds_amount": 1000.0}, {"invoice_id": inv(c).id}, {"tax_section": "s89"}):
        with pytest.raises(UserError):
            cert.write(vals)
    cert.with_user(c.acct2).action_settle()
    with pytest.raises(UserError):
        cert.action_cancel()  # a settled certificate is reversed in the GL
    assert lines(cert.settled_move_id) == sorted([(AIT_CODE, 600.0, 0.0), ("121000", 0.0, 600.0)])


def test_tds_07_settle_refused_while_the_ait_account_is_unconfigured(c):  # noqa: F811
    c.env["ir.config_parameter"].sudo().set_param(PARAM, "")
    i = inv(c)
    cert = tds(c, c.acct, i, 1000.0)
    cert.with_user(c.acct2).action_verify()
    with pytest.raises(UserError, match=PARAM):
        cert.with_user(c.acct2).action_settle()
    c.env["ir.config_parameter"].sudo().set_param(PARAM, "999999")  # not in the chart
    with pytest.raises(UserError, match="not in this company's chart"):
        cert.with_user(c.acct2).action_settle()
    assert cert.state == "verified" and not cert.settled_move_id
    assert i.amount_residual == 11500.0


def test_tds_08_plain_user_and_p03_cannot_forge(c, ait):  # noqa: F811
    i = inv(c)
    cert = tds(c, c.acct, i, 1000.0)
    with pytest.raises(AccessError):
        as_(c, c.plain)["fix.tds.certificate.received"].browse(cert.id).write({"note": "x"})
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
    )
    old = getattr(g, "request", None)
    g.request = types.SimpleNamespace(env=as_(c, c.acct))
    try:
        out = mw(
            ctl,
            model="fix.tds.certificate.received",
            record_id=cert.id,
            values={"state": "settled", "verified_by_id": c.acct2.id},
        )
    finally:
        g.request = old
    cert.invalidate_recordset()
    assert out.get("error") and cert.state == "draft" and not cert.verified_by_id


def test_tds_09_cancelled_certificate_frees_the_residual(c, ait):  # noqa: F811
    i = inv(c)
    cert = tds(c, c.acct, i, 11500.0)
    cert.action_cancel()
    assert cert.state == "cancelled"
    tds(c, c.acct, i, 11500.0)  # the cancelled one no longer counts


# ============================================================ receipt payment method
def pm(c, xmlid):  # noqa: F811
    return c.env.ref("cd_billing_engine.%s" % xmlid)


def test_rcpt_01_rocket_receipt_books_as_mobile_wallet(c):  # noqa: F811
    rocket = pm(c, "payment_method_rocket")
    assert rocket.receipt_method == "mobile_wallet"
    r = as_(c, c.acct)["fix.ar.receipt"].create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "customer_id": c.customer.id,
            "amount": 2300.0,
            "payment_method_id": rocket.id,
            "reference": "RKT%s" % uuid.uuid4().hex[:6],
        }
    )
    assert r.method == "mobile_wallet" and r.payment_method_id == rocket
    r.action_confirm()
    assert r.state == "confirmed" and r.account_id.code == "251000"
    assert lines(r.posted_move_id) == sorted([("251000", 2300.0, 0.0), ("121000", 0.0, 2300.0)])
    # the method is frozen with the posting, like the tender
    with pytest.raises(UserError):
        r.write({"payment_method_id": pm(c, "payment_method_upay").id})


def test_rcpt_02_payment_method_and_tender_must_agree(c):  # noqa: F811
    rocket = pm(c, "payment_method_rocket")
    with pytest.raises(ValidationError):
        rcpt(c, c.acct, 500.0, method="cash", confirm=False, payment_method_id=rocket.id)
    r = rcpt(c, c.acct, 500.0, confirm=False, payment_method_id=rocket.id, method="mobile_wallet")
    with pytest.raises(ValidationError):
        r.write({"method": "bkash"})
    # choosing another method moves the tender with it
    r.write({"payment_method_id": pm(c, "payment_method_bkash").id})
    assert r.method == "bkash"
    r.write({"payment_method_id": pm(c, "payment_method_beftn").id})
    assert r.method == "bank_transfer"


def test_rcpt_03_on_account_is_not_a_receipt(c):  # noqa: F811
    on_account = pm(c, "payment_method_on_account")
    assert not on_account.receipt_method
    with pytest.raises(ValidationError):
        rcpt(c, c.acct, 500.0, confirm=False, payment_method_id=on_account.id)


def test_rcpt_04_legacy_receipt_without_a_payment_method_still_books(c):  # noqa: F811
    r = rcpt(c, c.acct, 700.0, method="nagad")
    assert not r.payment_method_id and r.account_id.code == "251000"


def test_rcpt_05_workspace_capture_takes_the_payment_method(c):  # noqa: F811
    from odoo.addons.cd_p03_portal.controllers import p03_ar_api

    rocket = pm(c, "payment_method_rocket")
    old = getattr(p03_ar_api, "request", None)
    p03_ar_api.request = types.SimpleNamespace(env=as_(c, c.acct))
    try:
        ctl = p03_ar_api.P03ArApiController()
        create = getattr(
            p03_ar_api.P03ArApiController.ar_receipt_create,
            "original_endpoint",
            p03_ar_api.P03ArApiController.ar_receipt_create,
        )
        listing = getattr(
            p03_ar_api.P03ArApiController.ar_receipts,
            "original_endpoint",
            p03_ar_api.P03ArApiController.ar_receipts,
        )
        res = create(ctl, customer_id=c.customer.id, amount=900, payment_method_id=rocket.id)
        assert res["success"], res
        receipt = c.env["fix.ar.receipt"].browse(res["receipt_id"])
        assert receipt.payment_method_id == rocket and receipt.method == "mobile_wallet"
        bad = create(
            ctl, customer_id=c.customer.id, amount=900, payment_method_id=rocket.id, method="cash"
        )
        assert not bad["success"]
        offered = {m["id"] for m in listing(ctl)["payment_methods"]}
        assert rocket.id in offered and pm(c, "payment_method_on_account").id not in offered
    finally:
        p03_ar_api.request = old
