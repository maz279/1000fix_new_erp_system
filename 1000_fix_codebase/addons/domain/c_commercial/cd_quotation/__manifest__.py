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
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Sales/Quotations",
    "depends": ["base", "mail", "cd_entity_config", "cd_event_outbox",
                 "cd_service_order"],
    "data": ["security/ir.model.access.csv", "views/fix_quotation_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M36-02",
    "x_module_id": "M36",
    "x_wave": "W3",
    "x_owner": "Commercial & Finance",
    "x_category": "C_Commercial_Pricing_and_Revenue",
    "x_tier": "T4",
}
