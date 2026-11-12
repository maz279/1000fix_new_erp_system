{
    "name": "1000FiX Professional Document Suite",
    "summary": "Branded QWeb PDF document suite: quotation, estimate, service-order customer copy, "
    "delivery challan, tax invoice, proforma, money receipt, purchase order, RFQ, "
    "vendor bill + e-mail templates with automatic PDF attachment (P0-P1 document layer)",
    "description": """
Document output layer per the 2026-11-10 capability report (Downloads/Report_Output):

- ONE branded letterhead: res.company is configured (logo, A4 paperformat, header/footer,
  brand colors, BIN) and web.external_layout_standard is inherited with a 1000FiX teal
  rule — every native AND suite document inherits the same brand (top-ERP pattern:
  Odoo external_layout / NetSuite template binding / D365FO print management).
- Ten transactional documents bound to the fix.* models with ir.actions.report
  (QWeb/wkhtmltopdf, A4 portrait, bilingual-ready, statutory Bengali CSS reused):
    sales    : Quotation, Repair Estimate, Service Order (customer copy), Delivery
               Challan, Tax Invoice (commercial Mushak-aligned), Proforma Invoice,
               Money Receipt
    purchase : Purchase Order, RFQ, Vendor Bill
- Mushak 6.3 statutory register print upgraded with the Rule-40 amount-in-words line
  (amount_in_words() from cd_tax_engine_bd.statutory_format, lakh-crore wording).
- amount_in_words_en computed on every documented model so all documents carry
  "in figures AND in words" (DT-013).
- One mail.template per document with report_template_ids: composer sends the branded
  PDF as an attachment (Send & Print parity with top-class ERPs).

Excludes: the workspace modal fix (cd_p03_portal) and statement export wiring, which
live in their owning modules.
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Portal",
    "depends": [
        "base",
        "mail",
        "web",
        "cd_service_order",
        "cd_quotation",
        "cd_billing_engine",
        "cd_tax_engine_bd",
        "cd_requisition",
        "cd_ap_ext",
    ],
    "data": [
        "report/report_paperformat_layout.xml",
        "data/res_company_brand.xml",
        "report/report_documents_sales.xml",
        "report/report_documents_finance.xml",
        "report/report_documents_purchase.xml",
        "data/ir_mail_templates.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "cd_doc_suite/static/src/css/doc_suite.css",
        ],
    },
    "installable": True,
    "application": False,
    "x_cd_id": "CD-DOC-SUITE",
    "x_module_id": "M99",
    "x_wave": "W5",
    "x_owner": "Commercial & Finance",
    "x_category": "Platform",
    "x_tier": "T5",
    "x_note": "Document output layer from the 2026-11-10 capability report: branded "
    "letterhead + 10 transactional documents + e-mail attachments. The "
    "legacy Unisoft invoice (TFSL/SI/RT-006) is the quality benchmark.",
}
