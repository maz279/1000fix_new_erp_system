# cd_tax_engine_bd — the statutory withholding certificates as RENDERED
# documents: Mushak 6.6 (VAT deducted at source, rule 40(1)) and the ITA 2023
# s.52 withholding certificate, plus the BN-007 amount formatting they use.
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from odoo.addons.cd_tax_engine_bd.models.statutory_format import (
    amount_in_words,
    bn_numerals,
    format_bdt,
    format_rate,
    group_lakh,
)
from odoo.exceptions import UserError

pytestmark = [pytest.mark.tax, pytest.mark.financial]

THIN = " "
DEDUCTOR_BIN = "1234567890123"
SUPPLIER_BIN = "9876543210123"


# --------------------------------------------------------------------------- BN-007 (pure)


@pytest.mark.parametrize(
    ("amount", "en", "bn"),
    [
        (0, "BDT 0.00", "৳ ০.০০"),
        (999.5, "BDT 999.50", "৳ ৯৯৯.৫০"),
        (150000, "BDT 1,50,000.00", "৳ ১,৫০,০০০.০০"),
        (12345678.9, "BDT 1,23,45,678.90", "৳ ১,২৩,৪৫,৬৭৮.৯০"),
        (Decimal("0.005"), "BDT 0.01", "৳ ০.০১"),  # half-up, never banker's
        (-1234.5, "-BDT 1,234.50", "-৳ ১,২৩৪.৫০"),  # sign before the symbol
    ],
)
def test_bn007_amounts(amount, en, bn):
    assert format_bdt(amount) == en.replace(" ", THIN, 1)
    assert format_bdt(amount, "bn") == bn.replace(" ", THIN, 1)


def test_lakh_grouping_and_numerals():
    assert [group_lakh(w) for w in ("7", "123", "1234", "123456", "1234567890")] == [
        "7",
        "123",
        "1,234",
        "1,23,456",
        "1,23,45,67,890",
    ]
    assert bn_numerals("VDS-6.6/202610/00042") == "VDS-৬.৬/২০২৬১০/০০০৪২"


def test_rates_to_three_decimals():
    assert [format_rate(r) for r in (15, 7.5, 0.0005, None)] == [
        "15.000%",
        "7.500%",
        "0.001%",  # half-up
        "0.000%",
    ]


def test_amount_in_words():
    assert amount_in_words(15000) == "Taka Fifteen Thousand Only"
    assert amount_in_words(Decimal("150101.50")) == (
        "Taka One Lakh Fifty Thousand One Hundred and One and Poisha Fifty Only"
    )
    assert amount_in_words(12345678) == (
        "Taka One Crore Twenty-Three Lakh Forty-Five Thousand Six Hundred and Seventy-Eight Only"
    )
    assert amount_in_words(0) == "Taka Zero Only"
    with pytest.raises(ValueError, match="cannot be negative"):
        amount_in_words(-1)


# --------------------------------------------------------------------------- rendered certificates


@pytest.fixture
def certs(odoo_env):
    """A private deductor company (own BIN, address, OU) — the shared
    fix_test database is used by concurrent suites."""
    company = odoo_env["res.company"].create(
        {
            "name": "1000FiX Withholding Report Test Ltd",
            "vat": DEDUCTOR_BIN,
            "street": "House 12, Road 5, Tejgaon I/A",
            "city": "Dhaka",
        }
    )
    env = odoo_env(context=dict(odoo_env.context, allowed_company_ids=company.ids))
    ou = env["operating.unit"].create(
        {
            "name": "WHT OU",
            "code": "WHT",
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    vendor = env["res.partner"].create({"name": "Apex Logistics Ltd."})
    screen = env["product.product"].create({"name": "LCD screen"})
    invoice = env["fix.vendor.invoice"].create(
        {
            "operating_unit_id": ou.id,
            "vendor_id": vendor.id,
            "invoice_ref": "APX-INV-0091",
            "invoice_date": date(2026, 10, 5),
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": screen.id,
                        "description": "LCD screens",
                        "quantity": 4,
                        "unit_price": 20000.0,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": screen.id,
                        "description": "Courier",
                        "quantity": 1,
                        "unit_price": 20000.0,
                    },
                ),
            ],
        }
    )

    def make(**vals):
        base = {
            "vendor_invoice_id": invoice.id,
            "supplier_name": "Apex Logistics Ltd.",
            "supplier_bin": SUPPLIER_BIN,
            "supplier_address": "Plot 7, Uttara, Dhaka 1230",
            "base_amount": 100000.0,
            "rate_percent": 15.0,
            "withheld_amount": 15000.0,
            "challan_no": "TC-2026-10-0042",
            "challan_date": date(2026, 10, 8),
            "bank_branch": "Sonali Bank, Tejgaon Branch",
        }
        base.update(vals)
        cert = env["fix.withholding.certificate"].create(base)
        if base.get("challan_no"):
            # A08 M51-4: a certificate is issued only for the deduction its
            # verified challan deposited (system arrangement of that deposit)
            kind = "vds" if base.get("certificate_type", "mushak_6_6") == "mushak_6_6" else "tds"
            challan = env["fix.tax.challan"].search(
                [("challan_no", "=", base["challan_no"]), ("company_id", "=", company.id)]
            ) or env["fix.tax.challan"].create(
                {
                    "challan_no": base["challan_no"],
                    "challan_date": base.get("challan_date") or date(2026, 10, 8),
                    "tax_kind": kind,
                    "amount": base["withheld_amount"],
                    "state": "deposited",
                    "verification_ref": "IBAS-OK",
                    "verified_by_id": env.uid,
                }
            )
            rate = env.ref(
                "cd_tax_engine_bd.tax_rate_vds_rent"
                if kind == "vds"
                else "cd_tax_engine_bd.tax_rate_tds_service_general"
            )
            env["fix.withholding.line"].create(
                {
                    "tax_kind": kind,
                    "partner_id": vendor.id,
                    "partner_tin": "123456789012",
                    "psr_received": True,
                    "paid_by_bank": True,
                    "rate_id": rate.id,
                    "document_date": date(2026, 10, 5),
                    "base_amount": base["withheld_amount"] * 100.0 / rate.rate,
                    "amount": base["withheld_amount"],
                    "vendor_invoice_id": invoice.id,
                    "challan_id": challan.id,
                    "state": "deposited",
                    "certificate_id": cert.id,
                }
            )
        return cert

    return env, make


def _render(env, report, certificates) -> str:
    html, kind = env["ir.actions.report"]._render_qweb_html(report, certificates.ids)
    assert kind == "html"
    return html.decode("utf-8")


class TestMushak66Report:
    def test_statutory_content(self, certs):
        env, make = certs
        cert = make()
        cert.action_issue()
        html = _render(env, "cd_tax_engine_bd.report_mushak66", cert)

        assert "fix-statutory-bn" in html  # the Bengali font path (TR-07)
        for text in (
            "মূসক-৬.৬ / Mushak-6.6",
            "ক্রমিক নং / SL",  # the serial column of the NBR form
            "উৎসে কর কর্তন সনদপত্র",
            "Certificate of VAT Deduction at Source",
            "See rule 40(1), VAT",
            "SD Rules 2016",
            cert.certificate_no,
            date.today().strftime("%d/%m/%Y"),
            "1000FiX Withholding Report Test Ltd",
            DEDUCTOR_BIN,
            "Tejgaon I/A",
            "Apex Logistics Ltd.",
            SUPPLIER_BIN,
            "Plot 7, Uttara, Dhaka 1230",
            "APX-INV-0091",
            "05/10/2026",  # supplier challan date
            "LCD screens, Courier",
            f"BDT{THIN}1,00,000.00",  # value of supply
            "15.000%",
            f"BDT{THIN}15,000.00",  # VAT deducted
            "Taka Fifteen Thousand Only",
            "TC-2026-10-0042",  # treasury deposit
            "08/10/2026",
            "Sonali Bank, Tejgaon Branch",
            "উৎসে কর্তনকৃত মূল্য সংযোজন কর সরকারি কোষাগারে জমা প্রদান করা হইয়াছে",
            "seal of the authorised officer",
        ):
            assert text in html, text

    def test_several_certificates_render_together(self, certs):
        env, make = certs
        first, second = (
            make(),
            make(withheld_amount=7500.5, base_amount=50003.33, challan_no="TC-2"),
        )
        (first | second).action_issue()
        html = _render(env, "cd_tax_engine_bd.report_mushak66", first | second)
        assert html.count('class="page fix-statutory-bn mushak66"') == 2
        assert f"BDT{THIN}7,500.50" in html
        assert "Taka Seven Thousand Five Hundred and Poisha Fifty Only" in html
        assert f"BDT{THIN}50,003.33" in html

    def test_only_issued_deposited_vds_certificates_print(self, certs):
        """DT-013 FM-13-a/b: a draft, a certificate without its treasury
        deposit, or an income-tax certificate never prints as Mushak 6.6."""
        env, make = certs
        draft = make()
        undeposited = make(challan_no=False)
        # A08 M51-4: such a certificate can no longer be issued; a legacy row
        # issued before the control is arranged directly to test the report
        undeposited.write({"state": "issued", "certificate_no": "LEGACY-%s" % undeposited.id})
        income_tax = make(certificate_type="section_52_income_tax", supplier_bin=False)
        income_tax.action_issue()
        with pytest.raises(UserError) as refused, env.cr.savepoint():
            _render(env, "cd_tax_engine_bd.report_mushak66", draft | undeposited | income_tax)
        message = str(refused.value)
        assert message.startswith("Mushak 6.6 cannot be printed")
        assert "draft #%s is not issued" % draft.id in message
        assert (
            "%s has no treasury deposit (challan) reference" % undeposited.certificate_no in message
        )
        assert "%s is of another certificate type" % income_tax.certificate_no in message


class TestIncomeTaxWithholdingReport:
    def test_statutory_content(self, certs):
        env, make = certs
        tds_return = env["fix.tds.return"].create({"quarter": "2026-Q2"})
        cert = make(
            certificate_type="section_52_income_tax",
            supplier_bin=False,
            supplier_tin="123456789012",
            base_amount=100000.0,
            rate_percent=5.0,
            withheld_amount=5000.0,
            fix_tds_return_id=tds_return.id,
        )
        cert.action_issue()
        html = _render(env, "cd_tax_engine_bd.report_withholding_certificate", cert)

        assert "fix-statutory-bn" in html
        for text in (
            "উৎসে কর কর্তনের সনদপত্র",
            "ক্রমিক নং / SL",
            "Certificate of Tax Deducted at Source",
            "আয়কর আইন ২০২৩, ধারা ৫২ / Income Tax Act 2023, Section 52",
            cert.certificate_no,
            "2026-Q2",
            "1000FiX Withholding Report Test Ltd",
            "Apex Logistics Ltd.",
            "123456789012",  # deductee e-TIN
            "APX-INV-0091",
            f"BDT{THIN}1,00,000.00",
            "5.000%",
            f"BDT{THIN}5,000.00",
            "Taka Five Thousand Only",
            "TC-2026-10-0042",
            "08/10/2026",
            "Sonali Bank, Tejgaon Branch",
            "deducted at source under Section 52 of the Income Tax Act 2023",
        ):
            assert text in html, text

    def test_missing_tin_is_stated_not_invented(self, certs):
        env, make = certs
        cert = make(
            certificate_type="section_52_income_tax", supplier_bin=False, challan_date=False
        )
        cert.action_issue()
        html = _render(env, "cd_tax_engine_bd.report_withholding_certificate", cert)
        assert "প্রদান করা হয়নি / not provided" in html

    def test_vds_certificate_is_not_an_income_tax_certificate(self, certs):
        env, make = certs
        vds = make()
        vds.action_issue()
        with (
            pytest.raises(UserError, match="Income-tax withholding certificate cannot be printed"),
            env.cr.savepoint(),
        ):
            _render(env, "cd_tax_engine_bd.report_withholding_certificate", vds)


def test_reports_are_bound_to_the_certificate_model(odoo_env):
    for xmlid, name in (
        ("cd_tax_engine_bd.action_report_fix_mushak66", "cd_tax_engine_bd.report_mushak66"),
        (
            "cd_tax_engine_bd.action_report_fix_withholding_certificate",
            "cd_tax_engine_bd.report_withholding_certificate",
        ),
    ):
        action = odoo_env.ref(xmlid)
        assert (action.model, action.report_name, action.report_type) == (
            "fix.withholding.certificate",
            name,
            "qweb-pdf",
        )
        assert action.binding_model_id.model == "fix.withholding.certificate"


def test_mushak63_applies_the_bengali_font(odoo_env):
    company = odoo_env["res.company"].create({"name": "1000FiX Mushak 6.3 Font Test Ltd"})
    env = odoo_env(context=dict(odoo_env.context, allowed_company_ids=company.ids))
    ou = env["operating.unit"].create(
        {
            "name": "M63 OU",
            "code": "M63",
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    row = env["fix.mushak.register"].create(
        {
            "operating_unit_id": ou.id,
            "mushak_no": "2026-000777",
            "invoice_ref": "AR/777",
            "invoice_date": date(2026, 10, 9),
            "supplier_name": "1000 FiX Services Ltd.",
            "supplier_bin": DEDUCTOR_BIN,
            "customer_name": "Karim Electronics",
            "taxable_amount": 1000.0,
            "vat_amount": 150.0,
            "total_payable": 1150.0,
        }
    )
    html, _kind = env["ir.actions.report"]._render_qweb_html(
        "cd_tax_engine_bd.report_mushak63", row.ids
    )
    html = html.decode("utf-8")
    # regression: a monetary widget placed ON a <td> made Odoo 19 refuse to
    # render the statutory invoice at all
    assert 'class="page fix-statutory-bn mushak63"' in html
    for text in ("মুশক ৬.৩ — কর চালানপত্র", "2026-000777", DEDUCTOR_BIN, "Karim Electronics"):
        assert text in html, text
    assert all(amount in html for amount in ("1,000.00", "150.00", "1,150.00"))


def test_statutory_css_carries_the_token_family():
    """The report-asset CSS names the design-token family (literal first for
    wkhtmltopdf, then the token variable)."""
    from pathlib import Path

    css = (
        Path(__file__).resolve().parents[1] / "static" / "src" / "css" / "statutory_bn.css"
    ).read_text(encoding="utf-8")
    rule = css[: css.index("}")]
    assert '"Noto Sans Bengali"' in rule
    assert "var(--fix-typography-font-bengali-family)" in rule
    assert rule.index('"Noto Sans Bengali"') < rule.index(
        "var(--fix-typography-font-bengali-family)"
    )
