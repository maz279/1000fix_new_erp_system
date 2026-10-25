# cd_fpa — M54 (P09).
{
    "name": "1000FiX FP&A, Cost Accounting & Budgeting",
    "summary": "M54: FP&A, Cost Accounting & Budgeting (CD-M54-01)",
    "description": """
CD-M54-01 (P09) — FP&A, Cost Accounting & Budgeting.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.0.2.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "FP&A, Cost Accounting & Budgeting",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_gl_ext",
        "cd_fixed_asset_ext",
        "cd_event_outbox",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/fix_business_line_data.xml",
        "views/cd_fpa_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M54-01",
    "x_module_id": "M54",
    "x_wave": "W6",
    "x_owner": "FP&A, Cost Accounting & Budgeting",
    "x_category": "Phase9",
    "x_tier": "T9",
}
