# cd_import_order — M44 (P09).
{
    "name": "1000FiX Import, Trade Compliance & Landed Cost",
    "summary": "M44: Import, Trade Compliance & Landed Cost (CD-M44-01)",
    "description": """
CD-M44-01 (P09) — Import, Trade Compliance & Landed Cost.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Import, Trade Compliance & Landed Cost",
    "depends": ["base", "mail", "cd_entity_config", "cd_requisition", "cd_gl_ext", "cd_event_outbox"],
    "data": ["security/ir.model.access.csv", "views/cd_import_order_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M44-01",
    "x_module_id": "M44",
    "x_wave": "W6",
    "x_owner": "Import, Trade Compliance & Landed Cost",
    "x_category": "Phase9",
    "x_tier": "T9",
}
