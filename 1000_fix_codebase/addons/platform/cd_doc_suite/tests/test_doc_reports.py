"""cd_doc_suite acceptance tests.

Every suite document must render a real PDF (wkhtmltopdf magic bytes) off a
real ORM record, and every mail template must attach that PDF via
report_template_ids — the "export in PDF, send email" acceptance bar.
"""

from odoo.tests import TransactionCase, tagged


def _first_key(env, model, field):
    meta = env[model].fields_get([field])
    return meta[field]["selection"][0][0]


@tagged("post_install", "-at_install")
class TestDocSuiteRendering(TransactionCase):
    def setUp(self):
        super().setUp()
        env = self.env
        self.partner = env["res.partner"].create(
            {
                "name": "Doc Suite Test Customer Ltd",
                "email": "doctest@example.com",
                "phone": "+8801700000000",
                "street": "Test Road 1",
                "city": "Dhaka",
                "vat": "0011223345567",
            }
        )
        self.vendor = env["res.partner"].create({"name": "Doc Suite Test Vendor"})
        self.currency = (
            env["res.currency"].search([("name", "=", "BDT")], limit=1) or env.company.currency_id
        )
        self.ou = env["operating.unit"].search([], limit=1)
        self.branch = env["fix.branch"].search([], limit=1)
        if not self.branch:  # a service order requires one; thin DBs have none
            entity = env["fix.entity"].create(
                {"code": "DOCSE", "legal_name": "Doc Suite entity", "company_id": env.company.id}
            )
            self.branch = env["fix.branch"].create(
                {
                    "name": "Doc Suite Branch",
                    "code": "DOCSB",
                    "entity_id": entity.id,
                    "operating_unit_id": self.ou.id,
                }
            )
        self.product = (
            env["product.template"]
            .create(
                {
                    "name": "Doc Suite Test Service",
                }
            )
            .product_variant_id
        )
        # A service order requires a device (M17 registry); a thin test
        # database has no device model, so build the chain it needs.
        dmodel = env["fix.device.model"].search([], limit=1)
        if not dmodel:
            brand = env["fix.brand"].create({"name": "Doc Suite Brand", "code": "DOCSB"})
            dmodel = env["fix.device.model"].create(
                {"name": "Doc Suite Phone", "brand_id": brand.id}
            )
        self.device = env["fix.device"].create(
            {
                "device_model_id": dmodel.id,
                "lifecycle_stage": _first_key(env, "fix.device", "lifecycle_stage"),
                "state": _first_key(env, "fix.device", "state"),
            }
        )

    def _render(self, action_xmlid, record):
        action = self.env.ref(action_xmlid)
        self.assertEqual(action.report_type, "qweb-pdf")
        # force_report_rendering: Odoo stubs _render_qweb_pdf to HTML in test
        # mode; the acceptance bar is a REAL wkhtmltopdf document.
        pdf, _ext = (
            self.env["ir.actions.report"]
            .with_context(force_report_rendering=True)
            ._render_qweb_pdf(action, record.ids)
        )
        self.assertTrue(pdf and pdf[:4] == b"%PDF", "%s did not render a PDF" % action_xmlid)
        return pdf

    # ---------------- record factories ----------------

    def _quotation(self):
        return self.env["fix.quotation"].create(
            {
                "name": "QT-TEST-0001",
                "customer_id": self.partner.id,
                "currency_id": self.currency.id,
                "quote_type": "service",
                "state": "sent",
                "version": 1,
                "esign_state": "none",
                "value": 125000.0,
                "vat_rate": 10.0,
                "vat_amount": 12500.0,
            }
        )

    def _estimate(self):
        est = self.env["fix.estimate"].create(
            {
                "order_id": self._service_order().id,
                "currency_id": self.currency.id,
                "state": "sent",
                "version": 1,
                "vat_rate": 10.0,
                "vat_amount": 1000.0,
                "grand_total": 11000.0,
                "parts_total": 6000.0,
                "labour_total": 4000.0,
            }
        )
        self.env["fix.estimate.line"].create(
            [
                {
                    "estimate_id": est.id,
                    "description": "SSD replacement",
                    "line_type": "part",
                    "quantity": 1,
                    "unit_price": 6000.0,
                    "line_total": 6000.0,
                    "currency_id": self.currency.id,
                },
                {
                    "estimate_id": est.id,
                    "description": "Labour + OS setup",
                    "line_type": "labour",
                    "quantity": 2,
                    "unit_price": 2000.0,
                    "line_total": 4000.0,
                    "currency_id": self.currency.id,
                },
            ]
        )
        return est

    def _service_order(self):
        vals = {
            "customer_id": self.partner.id,
            "fault_description": "No display after drop",
            "order_category": "standard",
            "payment_settlement_state": "unpaid",
            "priority": "normal",
            "service_type": "walk_in",
            "state": "intake",
            "customer_phone": "+8801700000000",
        }
        if self.device:
            vals["device_id"] = self.device.id
            vals["device_serial"] = "SN-DOC-TEST-1"
        if self.branch:
            vals["branch_id"] = self.branch.id
        return self.env["fix.service.order"].create(vals)

    def _ar_invoice(self):
        inv = self.env["fix.ar.invoice"].create(
            {
                "customer_id": self.partner.id,
                "currency_id": self.currency.id,
                "invoice_date": "2026-11-10",
                "operating_unit_id": self.ou.id,
                "source_id": 1,
                "source_model": "fix.service.order",
                "state": "issued",
                "taxable_amount": 10000.0,
                "vat_amount": 1000.0,
                "total_payable": 11000.0,
            }
        )
        self.env["fix.ar.invoice.line"].create(
            [
                {
                    "invoice_id": inv.id,
                    "description": "Repair service",
                    "taxable_amount": 10000.0,
                    "vat_amount": 1000.0,
                    "line_total": 11000.0,
                    "product_id": self.product.id,
                },
            ]
        )
        return inv

    def _receipt(self):
        return self.env["fix.ar.receipt"].create(
            {
                "customer_id": self.partner.id,
                "currency_id": self.currency.id,
                "amount": 11000.0,
                "method": "bkash",
                "receipt_date": "2026-11-10",
                "state": "confirmed",
                "reference": "TXN-TEST-1",
            }
        )

    def _po(self):
        po = self.env["fix.purchase.order"].create(
            {
                "vendor_id": self.vendor.id,
                "currency_id": self.currency.id,
                "date_order": "2026-11-10 10:00:00",
                "operating_unit_id": self.ou.id,
                "amount_total": 27000.0,
            }
        )
        self.env["fix.purchase.order.line"].create(
            {
                "order_id": po.id,
                "product_id": self.product.id,
                "description": "Test part",
                "qty_ordered": 2,
                "unit_price": 13500.0,
                "line_total": 27000.0,
            }
        )
        return po

    def _rfq(self):
        return self.env["fix.procurement.rfq"].create(
            {
                "name": "RFQ-TEST-0001",
                "description": "Parts procurement",
                "product_id": self.product.id,
                "qty": 5,
                "currency_id": self.currency.id,
            }
        )

    def _vendor_bill(self):
        bill = self.env["fix.vendor.invoice"].create(
            {
                "vendor_id": self.vendor.id,
                "currency_id": self.currency.id,
                "invoice_date": "2026-11-10",
                "invoice_ref": "VI-TEST-0001",
                "operating_unit_id": self.ou.id,
                "bill_type": "po",
                "approval_state": "draft",
                "payment_channel": "bank",
                "payment_state": "not_paid",
                "subtotal": 13500.0,
                "vat_amount": 1350.0,
                "total_payable": 14850.0,
                "supplier_mushak_no": "0000000000000",
            }
        )
        self.env["fix.vendor.invoice.line"].create(
            {
                "invoice_id": bill.id,
                "product_id": self.product.id,
                "description": "Supplied part",
                "quantity": 1,
                "unit_price": 13500.0,
                "line_total": 13500.0,
            }
        )
        return bill

    def _mushak(self):
        return self.env["fix.mushak.register"].create(
            {
                "currency_id": self.currency.id,
                "mushak_no": "MUS-TEST-0001",
                "invoice_ref": "INV-TEST-0001",
                "invoice_date": "2026-11-10",
                "customer_name": "Doc Suite Test Customer Ltd",
                "customer_bin": "0011223345567",
                "supplier_name": "1000Fix Services Limited",
                "supplier_bin": "0018218330401",
                "operating_unit_id": self.ou.id,
                "row_type": "invoice",
                "taxable_amount": 10000.0,
                "vat_amount": 1000.0,
                "total_payable": 11000.0,
            }
        )

    # ---------------- render tests ----------------

    def test_01_quotation_pdf(self):
        self._render("cd_doc_suite.action_report_quotation", self._quotation())

    def test_02_estimate_pdf(self):
        self._render("cd_doc_suite.action_report_estimate", self._estimate())

    def test_03_service_order_pdf(self):
        self._render("cd_doc_suite.action_report_service_order", self._service_order())

    def test_04_delivery_challan_pdf(self):
        self._render("cd_doc_suite.action_report_delivery_challan", self._service_order())

    def test_05_invoice_pdf(self):
        self._render("cd_doc_suite.action_report_invoice", self._ar_invoice())

    def test_06_proforma_pdf(self):
        self._render("cd_doc_suite.action_report_proforma", self._ar_invoice())

    def test_07_money_receipt_pdf(self):
        self._render("cd_doc_suite.action_report_money_receipt", self._receipt())

    def test_08_po_pdf(self):
        self._render("cd_doc_suite.action_report_po", self._po())

    def test_09_rfq_pdf(self):
        self._render("cd_doc_suite.action_report_rfq", self._rfq())

    def test_10_vendor_bill_pdf(self):
        self._render("cd_doc_suite.action_report_vendor_bill", self._vendor_bill())

    # ---- the commercial document standard on the purchase side (18 Nov 2026) ----

    def _html(self, report, record):
        html, _kind = self.env["ir.actions.report"]._render_qweb_html(report, record.ids)
        return html.decode("utf-8")

    def test_10a_po_prints_the_commercial_standard(self):
        self.product.default_code = "DS-PART-01"
        self.vendor.vat = "0099887766554"
        po = self._po()
        p = po._fix_print_payload()
        row = p["lines"][0]
        self.assertEqual(row["sl"], 1)
        self.assertEqual(row["code"], "DS-PART-01")
        self.assertEqual(row["qty"], "2")
        self.assertEqual(row["uom"], self.product.uom_id.name)
        self.assertEqual(row["amount"], "27,000.00")
        self.assertEqual(p["party_label"], "Supplier")
        self.assertEqual(p["totals"][-1][:3], ("Order Total (excl. VAT)", "27,000.00", "grand"))
        self.assertEqual(p["words"], "Taka Twenty-Seven Thousand Only")
        html = self._html("cd_doc_suite.report_po", po)
        for text in (
            "SL",
            "Item Code",
            "DS-PART-01",
            "Unit Price",
            "Discount",
            "In Words",
            "Supplier BIN",
            "0099887766554",
            "Buyer BIN",
            "PURCHASE ORDER",
        ):
            self.assertIn(text, html)
        # we are the payer: no "Payable to 1000FiX" line on a purchase document
        self.assertNotIn("Payable to", html)
        self.assertEqual(
            po.action_fix_print(), {"print_url": "/report/pdf/cd_doc_suite.report_po/%s" % po.id}
        )
        self.assertEqual(po.action_fix_print_receipt(), {})

    def test_10b_vendor_bill_prints_the_commercial_standard(self):
        self.product.default_code = "DS-PART-01"
        bill = self._vendor_bill()
        p = bill._fix_print_payload()
        row = p["lines"][0]
        self.assertEqual((row["sl"], row["code"], row["qty"]), (1, "DS-PART-01", "1"))
        labels = [t[0] for t in p["totals"]]
        self.assertIn("Input VAT (Mushak-6.3)", labels)
        self.assertTrue(labels[-1].startswith("Net Payable"))
        self.assertEqual(p["totals"][-1][1], f"{bill.total_payable:,.2f}")
        self.assertTrue(p["words"])
        html = self._html("cd_doc_suite.report_vendor_bill", bill)
        for text in (
            "SL",
            "Item Code",
            "DS-PART-01",
            "VENDOR BILL",
            "VI-TEST-0001",
            "Supplier Mushak 6.3 No.",
            "In Words",
        ):
            self.assertIn(text, html)
        self.assertNotIn("Payable to", html)

    def test_10c_mushak63_has_a_serial_column(self):
        html = self._html("cd_tax_engine_bd.action_report_fix_mushak", self._mushak())
        self.assertIn("ক্রমিক নং / SL", html)

    def test_11_mushak63_in_words_pdf(self):
        pdf = self._render("cd_tax_engine_bd.action_report_fix_mushak", self._mushak())
        # the inherited in-words line must not break the statutory template
        self.assertGreater(len(pdf), 3000)

    # ---------------- e-mail template tests ----------------
    # send_mail(force_send=False) builds the mail + attachments and QUEUES it
    # (state outgoing) — nothing leaves the system, but the exact production
    # path (template render + report attachment) is exercised.

    def _queued_mail(self, template_xmlid, record):
        tpl = self.env.ref(template_xmlid)
        mail_id = tpl.with_context(force_report_rendering=True).send_mail(
            record.id, force_send=False
        )
        return self.env["mail.mail"].browse(mail_id)

    def test_20_invoice_email_attaches_pdf(self):
        inv = self._ar_invoice()
        tpl = self.env.ref("cd_doc_suite.email_template_invoice")
        self.assertIn(self.env.ref("cd_doc_suite.action_report_invoice"), tpl.report_template_ids)
        mail = self._queued_mail("cd_doc_suite.email_template_invoice", inv)
        pdfs = [a for a in mail.attachment_ids if a.name and a.name.lower().endswith(".pdf")]
        self.assertTrue(pdfs, "invoice e-mail carries no PDF attachment")
        self.assertEqual(pdfs[0].raw[:4], b"%PDF")
        self.assertEqual(mail.state, "outgoing")  # queued, not sent

    def test_21_quotation_email_renders(self):
        quote = self._quotation()
        mail = self._queued_mail("cd_doc_suite.email_template_quotation", quote)
        self.assertIn(quote.name, mail.subject)
        # template partner_to resolves to the customer partner record
        self.assertIn(quote.customer_id, mail.recipient_ids)
        self.assertIn("doctest@example.com", mail.recipient_ids.mapped("email"))

    def test_22_money_receipt_email_attaches_pdf(self):
        rec = self._receipt()
        mail = self._queued_mail("cd_doc_suite.email_template_money_receipt", rec)
        pdfs = [a for a in mail.attachment_ids if a.name and a.name.lower().endswith(".pdf")]
        self.assertTrue(pdfs)
        self.assertEqual(pdfs[0].raw[:4], b"%PDF")

    def test_23_po_email_attaches_pdf(self):
        po = self._po()
        mail = self._queued_mail("cd_doc_suite.email_template_po", po)
        pdfs = [a for a in mail.attachment_ids if a.name and a.name.lower().endswith(".pdf")]
        self.assertTrue(pdfs)
        self.assertEqual(pdfs[0].raw[:4], b"%PDF")

    # ---------------- amount-in-words ----------------

    def test_30_amount_in_words(self):
        rec = self._receipt()
        self.assertIn("Eleven Thousand", rec.amount_in_words_en)
        self.assertIn("Only", rec.amount_in_words_en)

    def test_31_company_branding_loaded(self):
        company = self.env.ref("base.main_company")
        # company.logo is related to partner_id.image_1920. bin_size reads the
        # attachment's recorded size, so this checks that a logo is configured
        # without needing this process's filestore (pytest does not load the
        # server's data_dir; a template-cloned DB has none). bin_size does not
        # pass through the related field, so read the partner's image.
        self.assertEqual(company._fields["logo"].related, "partner_id.image_1920")
        logo = company.partner_id.with_context(bin_size=True).image_1920
        self.assertTrue(logo, "company logo not configured")
        self.assertTrue(company.paperformat_id)
        self.assertEqual(company.paperformat_id.format, "A4")
        self.assertEqual(company.vat, "001821833-0401")
        self.assertTrue(company.external_report_layout_id)
