{
    "name": "1000FiX Supplier Qualification",
    "summary": "M42 qualification questionnaires, immutable versioned qualifications, the fail-closed activation gate and integrity screening (CD-M42-02)",
    "description": """
CD-M42-02 (M42 spec §5.2, §5.3, T-01..T-03):

- fix.qualification.questionnaire / .question — category- and tier-specific
  templates with weights and a pass threshold (FR-SRM2-008)
- fix.supplier.qualification — versioned, immutable once approved (T-03);
  the scorer cannot be the sole approver at high/critical tiers; approval
  activates the supplier; daily expiry de-activates on lapse (FR-SRM2-011)
- check_activation(partner, category, company, date) — the synchronous
  decision M16 calls before a PO; fails CLOSED (FR-SRM2-010, T-01/T-02)
- fix.supplier.screening — sanctions / conflict-of-interest / related-party
  screening with the anti-bribery and code-of-conduct declarations
  (FR-SRM2-019/020)
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Purchase/Supplier Relationship",
    "depends": ["base", "mail", "product", "cd_entity_config", "cd_event_outbox",
                 "cd_vendor_ext"],
    "data": [
        "security/ir.model.access.csv",
        "data/fix_supplier_qualification_cron.xml",
        "views/fix_supplier_qualification_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M42-02",
    "x_module_id": "M42",
    "x_wave": "W4",
    "x_owner": "Supply Chain",
    "x_category": "E_Supply_Chain_and_Inventory",
    "x_tier": "T9",
}
