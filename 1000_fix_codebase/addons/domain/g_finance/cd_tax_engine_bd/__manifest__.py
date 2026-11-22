{
    "name": "1000FiX VAT Engine (M51-core)",
    "summary": "VAT determination, TDS, Mushak 6.3 issuance + register, VAT/TDS returns, withholding certificates (CD-M51-01, P07-M04 completion)",
    "description": """
CD-M51-01..05 (W3 slice per MV-03) + the P07-M04 completion:

- fix.vat.return — Mushak 9.1 monthly preparation from the register, with
  the MANDATORY nil return, holiday-rolled due dates, online-only filing
  (confirmation reference mandatory — manual filing abolished 1 July 2026),
  and the sub-ledger reconciliation
- fix.tds.return — quarterly returns on the statutory deadlines (25
  Oct/Jan/Apr/Jul, holiday-rolled) against the BD fiscal year
- fix.withholding.certificate — the deductee certificate flow
- The CALCULATION is pure (return_logic.py — 21 tests, 100% of return paths)

- tax_logic.determine_tax() / determine_tds() — PURE determination functions
  (no Odoo imports); M20 and M52 call them SYNCHRONOUSLY (AR-006 section 4.1
  pairs 7/8); nothing calls M20 back
- fix.vat.treatment — tariff projection, data source M30's country pack
  (NOT M65 — T06 closes the +5-wave violation)
- fix.mushak.register — the VAT register, populated by CONSUMING
  invoice.created events (never calling M20); rebuilds from the event stream
  alone (T04); BIN-format constraints (13 digits); atomic-posted with the GL
  (T08)
- The statutory Mushak 6.3 QWeb invoice, the Mushak 6.6 VDS certificate and
  the ITA 2023 s.52 withholding certificate, with Bengali rendering (TR-07)

VAT returns and filing (Mushak 9.1) are explicitly W4 (roadmap P06-M02-T09).
""",
    "version": "19.0.1.3.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Finance/Tax",
    "depends": ["base", "mail", "account", "cd_entity_config", "cd_event_outbox", "cd_gl_ext"],
    "data": [
        "security/fix_tax_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "security/fix_a08_rules.xml",
        "data/fix_tax_master_data.xml",
        "data/fix_salary_tds_consumers.xml",
        "data/fix_tax_reminder_cron.xml",
        "data/fix_tax_depreciation_data.xml",
        "data/fix_tax_register_data.xml",
        "data/fix_tax_capture_data.xml",
        "data/fix_tax_event_consumers.xml",
        "views/fix_tax_engine_views.xml",
        "views/fix_tax_compliance_views.xml",
        "views/fix_tax_returns_views.xml",
        "report/report_mushak63.xml",
        "report/report_withholding_certificates.xml",
    ],
    "assets": {
        # TR-07: the Bengali font path of the statutory forms (QWeb PDFs)
        "web.report_assets_common": [
            "cd_tax_engine_bd/static/src/css/statutory_bn.css",
        ],
    },
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M51-01",
    "x_module_id": "M51",
    "x_wave": "W3",
    "x_owner": "Commercial & Finance",
    "x_category": "G_Finance_and_Treasury",
    "x_tier": "T5",
    "x_note": "MV-03 moved determination + Mushak issuance to W3; returns/filing stay W4. Register rows CD-M51-02/03/05 land here; CD-M51-04 (returns) is W4.",
}
