# cd_grc — M60 (P09).
{
    "name": "1000FiX Governance, Risk & Compliance",
    "summary": "M60: Governance, Risk & Compliance (CD-M60-01)",
    "description": """
CD-M60-01 (P09) — Governance, Risk & Compliance.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Governance, Risk & Compliance",
    "depends": ["base", "mail", "hr", "cd_entity_config", "cd_event_outbox", "cd_document_core"],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "views/cd_grc_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M60-01",
    "x_module_id": "M60",
    "x_wave": "W6",
    "x_owner": "Governance, Risk & Compliance",
    "x_category": "Phase9",
    "x_tier": "T9",
}
