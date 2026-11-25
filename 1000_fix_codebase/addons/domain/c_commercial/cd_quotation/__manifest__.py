{
    "name": "1000FiX Quotation & Estimation",
    "summary": "M36: the quotation lifecycle on M01's unified estimate + discount governance (CD-M36-02/03)",
    "description": """
CD-M36-02/03: quotation and estimation.

- fix.estimate EXTENDED (AS-01: ONE estimate concept — M01 created it, M36
  quotes it; no second model): quotation_state lifecycle, validity window
  (BRU-SRM-13 — expired quotes are re-issued, never extended), quotation
  events, tender seam field
- fix.discount.approval — T03 discount governance: the 05-04 section 7
  authority matrix (agent 5% delegated, manager 10%, above that
  commercial director); a pending approval BLOCKS quoting
- Tender management (CD-M36-05) is a seam (tender_ref) consumed by the P04
  corporate portal in Phase 7
- A04 C2-C13 build (2026-11-04): fix.quotation lifecycle (value-band M63
  approval, issue, customer acceptance by OTP / provider e-signature /
  signed copy, decline, revise, expiry cron, hand-off to the M01 order or an
  M08 contract); tenders with bid / no-bid, compliance matrix, bid security
  gate and a Tender Committee award that creates the M08 contract; bank
  guarantees with routed DOFA release / claim and an expiry cron; roles
  (Quotation Author, Bid Coordinator, Tender Committee, Commercial Manager)
""",
    "version": "19.0.1.6.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Sales/Quotations",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_event_outbox",
        "cd_service_order",
        "cd_workflow_engine",
        # Quote-to-cash P1 (12 Nov 2026): payment terms (account) and the
        # customer payment-method master (M20). No cycle: the billing
        # engine reads quotations through the registry only.
        "account",
        "cd_billing_engine",
        # P2: deliveries for goods lines; the contract scope on M08 contracts.
        "stock",
        "cd_contract_core",
        # A10 deep audit (2026-11-23, D-A10-4): the quote e-signature runs
        # through the M24 document kernel + envelope (one evidence model).
        "cd_document_core",
        "cd_esignature",
    ],
    "data": [
        "security/cd_quotation_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
        "data/ir_cron_capture3.xml",
        "data/fix_quotation_template_data.xml",
        # A04 ERP audit (20 Nov 2026, B2): decline and variation consumers.
        "data/fix_a04_quote_consumers.xml",
        # A10 deep audit (2026-11-23, D-A10-4): the quotation PDF + the M24
        # envelope completion consumer.
        "report/fix_quotation_report.xml",
        "data/fix_quotation_m24_consumers.xml",
        "views/fix_quotation_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M36-02",
    "x_module_id": "M36",
    "x_wave": "W3",
    "x_owner": "Commercial & Finance",
    "x_category": "C_Commercial_Pricing_and_Revenue",
    "x_tier": "T4",
}
