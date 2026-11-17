# ruff: noqa: F811  (the c fixture is imported from the M36 suite)
# The commercial document standard (17 Nov 2026): one line standard for the
# estimate, quotation, local proforma and tax invoice; every line carries a
# code (part number or charge code); stock vs charge lines; customer
# categories; the local proforma; the shared print body with SL, codes,
# discount, VAT, totals and the amount in words.
import re
from pathlib import Path

import pytest
from odoo.addons.cd_catalogue.models.fix_commercial_line import (
    CHARGE_LINE_TYPES,
    GENERIC_CHARGE_XMLID,
    LINE_TYPES,
)
from odoo.addons.cd_quotation.tests.test_a04_m36_controls import (  # noqa: F401
    _estimate,
    _quote,
    c,
)
from odoo.exceptions import UserError, ValidationError

ADDONS = Path(__file__).resolve().parents[3]
PORTAL = ADDONS / "platform" / "cd_p03_portal"


def _user(env, login, groups=()):
    user = env["res.users"].search([("login", "=", login)], limit=1)
    if not user:
        user = env["res.users"].create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    return user


@pytest.fixture
def d(c):
    env = c.env
    c.biller = _user(env, "cds_biller", ["account.group_account_invoice"])
    P = env["product.product"]
    c.part = P.create(
        {
            "name": "CDS LCD panel 15.6",
            "default_code": "CDS-LCD-156",
            "type": "consu",
            "is_storable": True,
            "list_price": 6000.0,
        }
    )
    c.goods = P.create(
        {
            "name": "CDS 512GB SSD",
            "default_code": "CDS-SSD-512",
            "type": "consu",
            "is_storable": True,
            "list_price": 5200.0,
        }
    )
    c.corp = env["res.partner"].create(
        {
            "name": "CDS Corporate Ltd",
            "is_company": True,
            "party_class": "corporate",
            "party_status": "active",
            "vat": "000111222-0101",
        }
    )
    # a registered corporate (its two-step registration is M33's own test)
    c.corp._guarded().write({"party_status": "active"})
    c.walk = env.ref("cd_billing_engine.partner_walk_in")
    return c


def _invoice(c, customer, lines, **kw):
    return (
        c.env["fix.ar.invoice"]
        .with_user(c.biller)
        .create_manual_invoice(
            {"customer_id": customer.id, "operating_unit_id": c.ou.id, **kw.pop("header", {})},
            lines,
            "test",
            **kw,
        )
    )


# --------------------------------------------------------------- charge codes
def test_every_charge_type_has_a_generic_non_stock_code(d):
    env = d.env
    assert set(GENERIC_CHARGE_XMLID) == set(CHARGE_LINE_TYPES)
    for line_type, xmlid in GENERIC_CHARGE_XMLID.items():
        code = env.ref(xmlid)
        assert code.charge_type == line_type and code.is_generic
        product = code.product_id
        assert product.default_code == code.code
        assert product.type == "service" and not product.is_storable, code.code
    # sixteen line types: three stock, thirteen charge
    assert len(LINE_TYPES) == 16 and len(CHARGE_LINE_TYPES) == 13


def test_a_new_charge_code_creates_and_follows_its_non_stock_item(d):
    code = d.env["fix.charge.code"].create(
        {
            "code": "CDS-AC-GAS",
            "name": "AC gas refill 1.5 ton",
            "charge_type": "service",
            "default_rate": 2500,
        }
    )
    assert code.product_id.default_code == "CDS-AC-GAS" and code.product_id.lst_price == 2500
    code.write({"name": "AC gas refill (1.5 ton)", "default_rate": 2700})
    assert code.product_id.name == "AC gas refill (1.5 ton)" and code.product_id.lst_price == 2700
    with pytest.raises(ValidationError, match="part number"), d.env.cr.savepoint():
        d.env["fix.charge.code"].create(
            {"code": "CDS-LCD-156", "name": "clash", "charge_type": "fee"}
        )
    with pytest.raises(UserError, match="generic"), d.env.cr.savepoint():
        d.env.ref("cd_catalogue.charge_code_labour").unlink()


# ------------------------------------------------------------ invoice lines
def test_invoice_lines_are_priced_by_qty_price_discount_with_codes(d):
    inv = _invoice(
        d,
        d.corp,
        [
            {
                "line_type": "part",
                "product_id": d.part.id,
                "quantity": 2,
                "unit_price": 1500,
                "discount_pct": 10,
                "serial_ref": "SN-1",
            },
            {
                "line_type": "labour",
                "description": "Board repair",
                "quantity": 1.5,
                "unit_price": 800,
            },
            {
                "line_type": "transport",
                "description": "Pick-up and drop",
                "quantity": 1,
                "unit_price": 300,
            },
        ],
        overall_discount=200,
    )
    lines = inv.line_ids.sorted("sequence")
    assert lines.mapped("item_code") == ["CDS-LCD-156", "CHG-LABOUR", "CHG-TRANSPORT"]
    assert lines.mapped("line_kind") == ["stock", "charge", "charge"]
    assert lines[1].uom_id == d.env.ref("uom.product_uom_hour")
    # 3000 - 300 (10%) - its share of 200; 1200 and 300 take the rest
    assert [ln.gross_amount for ln in lines] == [3000.0, 1200.0, 300.0]
    assert round(sum(lines.mapped("discount_amount")), 2) == 500.0
    assert inv.taxable_amount == 4000.0 and inv.vat_amount == 600.0 and inv.total_payable == 4600.0
    assert all(ln.vat_rate == 15.0 for ln in lines)
    assert inv.gross_total == 4500.0 and inv.discount_total == 500.0 and inv.item_count == 3
    assert inv.amount_in_words_en == "Taka Four Thousand Six Hundred Only"
    assert inv.customer_category == "corporate" and inv.customer_bin == "000111222-0101"


def test_a_typed_taxable_only_line_still_prints_qty_one(d):
    inv = _invoice(d, d.corp, [{"description": "Legacy line", "taxable_amount": 1000.0}])
    line = inv.line_ids
    assert (line.quantity, line.unit_price, line.taxable_amount, line.vat_amount) == (
        1.0,
        1000.0,
        1000.0,
        150.0,
    )
    assert line.item_code == "CHG-SERVICE"


def test_a_typed_vat_or_taxable_that_disagrees_is_refused(d):
    with pytest.raises(UserError, match="BRU-ARB-03"), d.env.cr.savepoint():
        _invoice(
            d, d.corp, [{"line_type": "service", "quantity": 1, "unit_price": 100, "vat_amount": 5}]
        )
    with pytest.raises(UserError, match="quantity x unit price"), d.env.cr.savepoint():
        _invoice(
            d,
            d.corp,
            [{"line_type": "service", "quantity": 2, "unit_price": 100, "taxable_amount": 150}],
        )


def test_stock_lines_take_inventory_items_and_charge_lines_never_do(d):
    inv = _invoice(d, d.corp, [{"line_type": "service", "quantity": 1, "unit_price": 10}])
    Line = d.env["fix.ar.invoice.line"].with_user(d.biller)
    labour_code = d.env.ref("cd_catalogue.charge_code_labour").product_id
    with pytest.raises(ValidationError, match="inventory item"), d.env.cr.savepoint():
        Line.create(
            {
                "invoice_id": inv.id,
                "line_type": "part",
                "product_id": labour_code.id,
                "quantity": 1,
                "unit_price": 5,
            }
        )
    with pytest.raises(ValidationError, match="charge code"), d.env.cr.savepoint():
        Line.create(
            {
                "invoice_id": inv.id,
                "line_type": "labour",
                "product_id": d.part.id,
                "quantity": 1,
                "unit_price": 5,
            }
        )
    # a picked item sets the type when none is given
    line = Line.create(
        {"invoice_id": inv.id, "product_id": d.part.id, "quantity": 1, "unit_price": 5}
    )
    assert line.line_type == "part" and line.description == "CDS LCD panel 15.6"


# -------------------------------------------------------- customer categories
def test_walk_in_invoice_needs_the_persons_name_and_phone(d):
    inv = _invoice(
        d,
        d.walk,
        [{"line_type": "goods", "product_id": d.goods.id, "quantity": 1, "unit_price": 5200}],
    )
    assert inv.customer_category == "walk_in"
    assert inv.date_due == inv.invoice_date
    problems = inv._fix_issue_problems()
    assert any("name" in p for p in problems) and any("phone" in p for p in problems)
    with pytest.raises(UserError, match="walk-in"), d.env.cr.savepoint():
        inv.with_user(d.biller).action_issue()
    inv.write({"bill_to_name": "Md. Rahim", "bill_to_phone": "01819000111"})
    assert inv._fix_issue_problems() == []
    assert inv._fix_mushak_buyer() == ("Md. Rahim", "")
    assert inv._fix_doc_party()["name"] == "Md. Rahim"


def test_corporate_invoice_states_the_buyer_bin(d):
    d.corp.vat = False
    inv = _invoice(d, d.corp, [{"line_type": "service", "quantity": 1, "unit_price": 100}])
    assert any("BIN" in p for p in inv._fix_issue_problems())
    inv.customer_bin = "000999888-0101"
    assert inv._fix_issue_problems() == []
    assert inv._fix_mushak_buyer()[1] == "000999888-0101"


def test_cash_customer_is_due_on_the_invoice_date(d):
    inv = _invoice(d, d.customer, [{"line_type": "service", "quantity": 1, "unit_price": 100}])
    assert inv.customer_category == "individual" and inv.date_due > inv.invoice_date
    inv.customer_category = "cash"
    assert inv.date_due == inv.invoice_date
    assert inv._fix_print_title() == "CASH MEMO / TAX INVOICE"


# ---------------------------------------------------------- estimate / quote
def test_estimate_takes_every_line_type_and_codes_its_charges(d):
    est = _estimate(d)
    Line = d.env["fix.estimate.line"]
    Line.create(
        {
            "estimate_id": est.id,
            "line_type": "transport",
            "description": "Pick-up",
            "quantity": 1,
            "unit_price": 300,
        }
    )
    Line.create(
        {
            "estimate_id": est.id,
            "line_type": "support",
            "description": "Remote support",
            "quantity": 1,
            "unit_price": 500,
        }
    )
    lines = est.line_ids
    assert {"CHG-TRANSPORT", "CHG-SUPPORT"} <= set(lines.mapped("item_code"))
    assert est.other_total == 300.0
    assert (
        est._chargeable_total() == est.parts_total + est.labour_total + est.diagnostic_total + 300.0
    )
    assert est.labour_total >= 500.0


def test_quotation_lines_carry_codes_and_money_discount(d):
    q = _quote(
        d,
        line_ids=[
            (
                0,
                0,
                {
                    "line_type": "goods",
                    "product_id": d.goods.id,
                    "description": "SSD",
                    "quantity": 2,
                    "unit_price": 5200,
                    "discount_pct": 10,
                },
            ),
            (
                0,
                0,
                {
                    "line_type": "installation",
                    "description": "Install",
                    "quantity": 2,
                    "unit_price": 700,
                },
            ),
        ],
    )
    lines = q.line_ids.sorted("sequence")
    assert lines.mapped("item_code") == ["CDS-SSD-512", "CHG-INSTALL"]
    assert lines[0].discount_amount == 1040.0 and q.value == 9360.0 + 1400.0


# ------------------------------------------------------------- the proforma
def test_proforma_from_quotation_converts_to_an_identical_invoice(d):
    q = _quote(
        d,
        customer_id=d.corp.id,
        discount_amount=100.0,
        line_ids=[
            (
                0,
                0,
                {
                    "line_type": "goods",
                    "product_id": d.goods.id,
                    "description": "SSD",
                    "quantity": 10,
                    "unit_price": 5200,
                },
            ),
            (
                0,
                0,
                {
                    "line_type": "installation",
                    "description": "Install",
                    "quantity": 10,
                    "unit_price": 700,
                    "discount_pct": 10,
                },
            ),
        ],
    )
    Proforma = d.env["fix.sales.proforma"]
    pf = Proforma.create(Proforma._vals_from_quotation(q))
    assert pf.quotation_id == q and len(pf.line_ids) == 2 and pf.overall_discount == 100.0
    assert pf.gross_total == 59000.0 and pf.discount_total == 800.0
    assert pf.taxable_amount == 58200.0 and pf.vat_amount == 8730.0 and pf.amount_total == 66930.0
    pf.action_issue()
    assert pf.state == "issued" and pf.name.startswith("PI/")
    with pytest.raises(UserError, match="frozen"), d.env.cr.savepoint():
        pf.with_user(d.biller).write({"overall_discount": 0})
    inv = pf.with_user(d.biller).action_convert_to_invoice()
    assert inv.source_model == "fix.sales.proforma" and inv.source_id == pf.id
    assert (inv.taxable_amount, inv.vat_amount, inv.total_payable) == (58200.0, 8730.0, 66930.0)
    assert inv.line_ids.mapped("item_code") == pf.line_ids.mapped("item_code")
    assert pf.state == "converted" and pf.invoice_id == inv
    assert pf.with_user(d.biller).action_convert_to_invoice() == inv or pf.state == "converted"


def test_proforma_needs_lines_and_the_category_data_to_issue(d):
    pf = d.env["fix.sales.proforma"].create({"customer_id": d.walk.id})
    with pytest.raises(UserError, match="line"), d.env.cr.savepoint():
        pf.action_issue()
    pf.write(
        {
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "line_type": "goods",
                        "product_id": d.goods.id,
                        "quantity": 1,
                        "unit_price": 5200,
                    },
                )
            ]
        }
    )
    with pytest.raises(UserError, match="walk-in"), d.env.cr.savepoint():
        pf.action_issue()
    pf.write({"bill_to_name": "Walk-in buyer", "bill_to_phone": "01700000000"})
    pf.action_issue()
    assert pf.state == "issued"


# ------------------------------------------------------------- the print body
def _html(env, report, record):
    html, _ = env["ir.actions.report"]._render_qweb_html(report, record.ids)
    return html.decode() if isinstance(html, bytes) else html


def test_every_document_prints_sl_codes_totals_and_words(d):
    inv = _invoice(
        d,
        d.corp,
        [
            {
                "line_type": "part",
                "product_id": d.part.id,
                "quantity": 1,
                "unit_price": 6000,
                "serial_ref": "SN-77",
            },
            {"line_type": "labour", "description": "Labour", "quantity": 2, "unit_price": 500},
        ],
        header={"customer_po_ref": "PO-CDS-1", "service_item": "HP Pavilion 15"},
    )
    pf = d.env["fix.sales.proforma"].create(
        {
            "customer_id": d.corp.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "line_type": "goods",
                        "product_id": d.goods.id,
                        "quantity": 1,
                        "unit_price": 5200,
                    },
                )
            ],
        }
    )
    q = _quote(
        d,
        line_ids=[
            (
                0,
                0,
                {
                    "line_type": "installation",
                    "description": "Install",
                    "quantity": 1,
                    "unit_price": 700,
                },
            )
        ],
    )
    est = _estimate(d)
    for report, rec, must in (
        (
            "cd_doc_suite.report_invoice",
            inv,
            [
                "TAX INVOICE",
                "MUSHAK - 6.3",
                "CDS-LCD-156",
                "CHG-LABOUR",
                "S/N: SN-77",
                "PO-CDS-1",
                "HP Pavilion 15",
                "8,050.00",
            ],
        ),
        (
            "cd_doc_suite.report_sales_proforma",
            pf,
            ["PROFORMA INVOICE", "CDS-SSD-512", "not a tax invoice"],
        ),
        ("cd_doc_suite.report_quotation", q, ["QUOTATION", "CHG-INSTALL"]),
        ("cd_doc_suite.report_estimate", est, ["ESTIMATE"]),
    ):
        html = _html(d.env, report, rec)
        assert ">SL<" in html and "Item Code" in html and "In Words" in html, report
        assert "Grand Total" in html or "Total Payable (incl. VAT)" in html, report
        for text in must:
            assert text.lower() in html.lower(), (report, text)


# ------------------------------------------------- the workspace (static checks)
def test_every_workspace_line_grid_numbers_its_rows():
    xml = (PORTAL / "static" / "src" / "p03_workspace.xml").read_text(encoding="utf-8")
    grid = xml[xml.index('class="d365-section d365-lines-card"') :][:4000]
    assert 'class="d365-line-sl"' in grid and "row_index + 1" in grid
    editor = xml[xml.index("M20 · INVOICE EDITOR") :][:30000]
    for text in (
        "Item Code / Part No.",
        "Serial / IMEI",
        "Disc %",
        "Grand Total",
        "In words:",
        "arPickItem",
    ):
        assert text in editor, text


def test_proforma_and_charge_code_screens_are_registered_and_writable():
    m36 = (PORTAL / "static" / "src" / "a04" / "m36.js").read_text(encoding="utf-8")
    m37 = (PORTAL / "static" / "src" / "a04" / "m37.js").read_text(encoding="utf-8")
    assert "'M36-proformas'" in m36 and "'M36-form-proforma'" in m36
    assert "action_convert_to_invoice" in m36 and "action_create_proforma" in m36
    assert "'M37-charge-codes'" in m37 and "'M37-form-charge'" in m37
    writable = (PORTAL / "controllers" / "a04" / "writable.py").read_text(encoding="utf-8")
    assert '"fix.sales.proforma"' in writable and '"fix.charge.code"' in writable
    surfaces = (PORTAL / "controllers" / "a04" / "m36.py").read_text(encoding="utf-8")
    assert re.search(r'"fix.sales.proforma": \{', surfaces)


# ------------------------------------------- legacy services -> charge codes
def test_a_stocked_service_item_is_adopted_as_a_charge_code(d):
    legacy = d.env["product.product"].create(
        {
            "name": "AC Installation-PC99001",
            "default_code": "TST-REF-SP-PC99001",
            "type": "consu",
            "is_storable": True,
            "list_price": 1.0,
        }
    )
    Code = d.env["fix.charge.code"]
    codes = Code._adopt_items(legacy, lambda p: "installation")
    assert len(codes) == 1 and codes.product_id == legacy
    assert codes.code == "TST-REF-SP-PC99001" and codes.charge_type == "installation"
    assert legacy.type == "service" and not legacy.is_storable
    assert codes.default_rate == 0.0  # the BDT 1.00 migration placeholder is not a rate
    # idempotent, and the item now prices as an installation charge line
    assert Code._adopt_items(legacy, lambda p: "service") == codes
    inv = _invoice(d, d.corp, [{"product_id": legacy.id, "quantity": 1, "unit_price": 1500}])
    assert (
        inv.line_ids.line_type == "installation" and inv.line_ids.item_code == "TST-REF-SP-PC99001"
    )


# --------------------------------------------------------- 80 mm receipt
def test_the_80mm_receipt_follows_its_content(d):
    lines = [
        {"line_type": "service", "description": "Service %s" % i, "quantity": 1, "unit_price": 100}
        for i in range(12)
    ]
    short = _invoice(
        d, d.walk, lines[:1], header={"bill_to_name": "Rahim", "bill_to_phone": "0181"}
    )
    long = _invoice(d, d.walk, lines, header={"bill_to_name": "Rahim", "bill_to_phone": "0181"})
    assert long._fix_receipt_height_mm() > short._fix_receipt_height_mm()
    R = d.env["ir.actions.report"]
    paper = d.env.ref("cd_doc_suite.paperformat_1000fix_receipt_80")
    assert paper.page_width == 80
    args = R._build_wkhtmltopdf_args(paper, False, {"data-report-page-height": "231"})
    assert args[args.index("--page-height") + 1] == "231mm"
    assert args[args.index("--page-width") + 1] == "80mm"
    html = _html(d.env, "cd_doc_suite.report_invoice_receipt", short)
    assert 'data-report-page-height="%s"' % short._fix_receipt_page_height() in html
    for text in (
        "CASH MEMO / TAX INVOICE",
        "MUSHAK - 6.3",
        "CHG-SERVICE",
        "Rahim",
        "Grand Total",
        "In words",
        "Thank you",
    ):
        assert text in html, text
    for model_report, rec in (
        (
            "cd_doc_suite.report_sales_proforma_receipt",
            d.env["fix.sales.proforma"].create(
                {
                    "customer_id": d.corp.id,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "line_type": "goods",
                                "product_id": d.goods.id,
                                "quantity": 1,
                                "unit_price": 5200,
                            },
                        )
                    ],
                }
            ),
        ),
        ("cd_doc_suite.report_quotation_receipt", _quote(d)),
        ("cd_doc_suite.report_estimate_receipt", _estimate(d)),
    ):
        html = _html(d.env, model_report, rec)
        assert "Grand Total" in html or "Total Payable (incl. VAT)" in html, model_report


def test_print_is_a_served_action_answering_the_pdf_url(d):
    pf = d.env["fix.sales.proforma"].create(
        {
            "customer_id": d.corp.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "line_type": "goods",
                        "product_id": d.goods.id,
                        "quantity": 1,
                        "unit_price": 5200,
                    },
                )
            ],
        }
    )
    assert pf.action_fix_print() == {
        "print_url": "/report/pdf/cd_doc_suite.report_sales_proforma/%s" % pf.id
    }
    assert pf.action_fix_print_receipt()["print_url"].endswith(
        "report_sales_proforma_receipt/%s" % pf.id
    )
    q = _quote(d)
    assert q.action_fix_print()["print_url"].endswith("report_quotation/%s" % q.id)
