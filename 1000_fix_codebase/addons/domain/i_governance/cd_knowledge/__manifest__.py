# cd_knowledge — M61 (P09).
{
    "name": "1000FiX Knowledge Management & Technical Library",
    "summary": "M61: Knowledge Management & Technical Library (CD-M61-01)",
    "description": """
CD-M61-01 (P09) — Knowledge Management & Technical Library.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Knowledge Management & Technical Library",
    "depends": ["base", "mail", "cd_entity_config", "cd_event_outbox"],
    "data": ["security/ir.model.access.csv", "views/cd_knowledge_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M61-01",
    "x_module_id": "M61",
    "x_wave": "W6",
    "x_owner": "Knowledge Management & Technical Library",
    "x_category": "Phase9",
    "x_tier": "T9",
}
