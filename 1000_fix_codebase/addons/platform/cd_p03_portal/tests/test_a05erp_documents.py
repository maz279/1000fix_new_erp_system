"""A05 ERP audit XC-10 / M13-24 / M14-18 / M18-18 (20 Nov 2026): the A05
records print. Each document renders through its QWeb report with the
commercial document standard (company header and BIN, party, SL / code / qty
lines, amount in words where money moves, bilingual labels) and is handed out
by /p03/doc/print_url.
"""

import datetime
import types
from datetime import timedelta

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_commercial_docs as docs_ctl
from odoo.addons.cd_p03_portal.controllers.a05 import m13
from odoo.addons.cd_p03_portal.tests.a05erp_helpers import SEQ, branch, set_cols
from odoo.exceptions import UserError

_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="


def _html(env, report, record):
    html, _kind = env["ir.actions.report"]._render_qweb_html(report, record.ids)
    return html.decode() if isinstance(html, bytes) else html


def _print_url(env, model, record_id):
    ctl = docs_ctl.P03CommercialDocs()
    fn = getattr(docs_ctl.P03CommercialDocs.doc_print_url, "original_endpoint", None)
    fn = fn or docs_ctl.P03CommercialDocs.doc_print_url
    old = getattr(docs_ctl, "request", None)
    docs_ctl.request = types.SimpleNamespace(env=env)
    try:
        return fn(ctl, model=model, record_id=record_id)["url"]
    finally:
        docs_ctl.request = old


@pytest.fixture
def d(odoo_env):
    env = odoo_env
    for model in ("fix.rental.reservation", "fix.tradein.request", "fix.ewaste.batch"):
        if model not in env:
            pytest.skip("%s not installed" % model)
    x = types.SimpleNamespace(env=env)
    x.today = m13.dhaka_today(env)
    x.branch = branch(env)
    i = next(SEQ)
    x.customer = env["res.partner"].create(
        {"name": "A05ERP Doc Customer %d" % i, "phone": "0171500%04d" % i}
    )
    return x


def _rental(d):
    env = d.env
    tmpl = env["product.template"].create({"name": "A05ERP Doc Camera", "default_code": "A5E-CAM"})
    item = env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id})
    sku = env["fix.rental.sku"].create(
        {"catalogue_item_id": item.id, "daily_rate": 1000, "security_deposit": 5000}
    )
    asset = env["fix.rental.asset"].create(
        {
            "name": "A05ERP-DOC-CAM",
            "rental_sku_id": sku.id,
            "serial_no": "A05ERP-DOC-SN",
            "category": "camera",
            "operating_unit_id": d.branch.operating_unit_id.id,
        }
    )
    res = env["fix.rental.reservation"].create(
        {
            "customer_id": d.customer.id,
            "rental_sku_id": sku.id,
            "rental_asset_id": asset.id,
            "operating_unit_id": d.branch.operating_unit_id.id,
            "branch_id": d.branch.id,
            "date_from": d.today,
            "date_to": d.today + timedelta(days=4),
        }
    )
    set_cols(res, rental_charge=5000, deposit_collected=5000, duration_days=5)
    return res


def test_rental_agreement_condition_report_and_deposit_receipt(d):
    env = d.env
    res = _rental(d)
    html = _html(env, "cd_p03_portal.report_a05_rental_agreement", res)
    assert "RENTAL AGREEMENT" in html and "ভাড়া চুক্তি" in html
    assert res.name in html and "A05ERP-DOC-SN" in html
    assert "In Words" in html and "5,000.00" in html
    assert "DRAFT — NOT SIGNED" in html  # never printed as signed when it is not

    cond = env["fix.rental.condition"].create(
        {"reservation_id": res.id, "report_type": "pre_delivery", "grade": "a"}
    )
    att = env["ir.attachment"].create({"name": "front.png", "datas": _PNG, "mimetype": "image/png"})
    env["fix.rental.condition.photo"].create(
        {"condition_id": cond.id, "attachment_id": att.id, "view_code": "front"}
    )
    html = _html(env, "cd_p03_portal.report_a05_condition_report", cond)
    assert "CONDITION REPORT — OUTBOUND" in html
    assert "data:image/png;base64," in html  # the photograph is on the page
    assert "Outbound vs return" in html

    env.cr.execute(
        """INSERT INTO fix_rental_deposit (name, company_id, reservation_id, customer_id, kind,
               amount, currency_id, method, date, gl_state)
           VALUES ('A05ERP-DEP-1', %s, %s, %s, 'collect', 5000, %s, 'bkash', %s, 'posted')
           RETURNING id""",
        [env.company.id, res.id, d.customer.id, env.ref("base.BDT").id, d.today],
    )
    deposit = env["fix.rental.deposit"].browse(env.cr.fetchone()[0])
    html = _html(env, "cd_p03_portal.report_a05_deposit_receipt", deposit)
    assert "SECURITY DEPOSIT RECEIPT" in html and "জামানত" in html
    assert "In Words" in html and "A05ERP-DEP-1" in html


def test_tradein_voucher_job_card_and_warranty_card(d):
    env = d.env
    req = env["fix.tradein.request"].create(
        {
            "customer_id": d.customer.id,
            "offered_value": 9000,
            "operating_unit_id": d.branch.operating_unit_id.id,
        }
    )
    with pytest.raises(UserError, match="no accepted offer"):
        _html(env, "cd_p03_portal.report_a05_tradein_voucher", req)
    set_cols(
        req,
        state="accepted",
        accepted_offer_value=9000,
        graded_value=9000,
        customer_nid="1234567890",
        accepted_at=datetime.datetime(2026, 11, 20, 6, 0),
    )
    html = _html(env, "cd_p03_portal.report_a05_tradein_voucher", req)
    assert "TRADE-IN PURCHASE VOUCHER" in html and "বিক্রেতার ঘোষণা" in html
    assert "9,000.00" in html and "In Words" in html
    assert "XXXXXX7890" in html and "1234567890" not in html  # the NID is masked

    step = env["fix.refurbishment"].create({"name": "Screen replaced", "tradein_id": req.id})
    html = _html(env, "cd_p03_portal.report_a05_refurb_job_card", step)
    assert "REFURBISHMENT JOB CARD" in html and "Screen replaced" in html

    warranty = env["fix.tradein.warranty"].create({"tradein_id": req.id, "months": 6})
    html = _html(env, "cd_p03_portal.report_a05_resale_warranty", warranty)
    assert "RESALE WARRANTY CARD" in html and "Buyer disclosure" in html


def test_ewaste_manifest_certificate_and_doe_return(d):
    env = d.env
    partner = env["fix.ewaste.partner"].create({"name": "A05ERP Recycler %d" % next(SEQ)})
    batch = env["fix.ewaste.batch"].create({"material_type": "battery", "partner_id": partner.id})
    manifest = env["fix.ewaste.manifest"].create(
        {
            "batch_id": batch.id,
            "partner_id": partner.id,
            "licence_no": "DOE-LIC-1",
            "hazardous": True,
            "hazmat_declaration": "UN3480 lithium-ion cells, terminals taped.",
            "total_weight_kg": 12.5,
            "item_count": 1,
            "issued_on": d.today,
        }
    )
    env["fix.ewaste.manifest.line"].create(
        {
            "manifest_id": manifest.id,
            "description": "Laptop batteries",
            "weight_kg": 12.5,
            "hazardous": True,
            "un_number": "3480",
        }
    )
    html = _html(env, "cd_p03_portal.report_a05_ewaste_manifest", manifest)
    assert "FORM-1" in html and "UN3480 lithium-ion" in html and "12.5" in html

    cert = env["fix.ewaste.certificate"].create(
        {"partner_id": partner.id, "batch_id": batch.id, "material_type": "battery"}
    )
    html = _html(env, "cd_p03_portal.report_a05_disposal_certificate", cert)
    assert "DISPOSAL / RECYCLING CERTIFICATE" in html and "NOT ISSUED" in html

    ret = env["fix.ewaste.return"].create({"period": "2001-01", "due_date": d.today})
    html = _html(env, "cd_p03_portal.report_a05_doe_return", ret)
    assert "STATUTORY E-WASTE RETURN" in html and "2001-01" in html


def test_print_url_hands_out_every_a05_document(d):
    env = d.env
    res = _rental(d)
    url = _print_url(env, "fix.rental.reservation", res.id)
    assert url == "/report/pdf/cd_p03_portal.report_a05_rental_agreement/%d" % res.id
    for model, report in (
        ("fix.rental.condition", "report_a05_condition_report"),
        ("fix.rental.deposit", "report_a05_deposit_receipt"),
        ("fix.tradein.request", "report_a05_tradein_voucher"),
        ("fix.refurbishment", "report_a05_refurb_job_card"),
        ("fix.tradein.warranty", "report_a05_resale_warranty"),
        ("fix.ewaste.manifest", "report_a05_ewaste_manifest"),
        ("fix.ewaste.certificate", "report_a05_disposal_certificate"),
        ("fix.ewaste.return", "report_a05_doe_return"),
    ):
        action = env.ref("cd_p03_portal.action_%s" % report)
        assert action.model == model and action.report_name == "cd_p03_portal.%s" % report
        any_rec = env[model].search([], limit=1)
        if any_rec:
            assert _print_url(env, model, any_rec.id).startswith(
                "/report/pdf/cd_p03_portal.%s/" % report
            )
