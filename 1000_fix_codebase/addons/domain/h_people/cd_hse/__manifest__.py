# cd_hse — M59 (P09).
{
    "name": "1000FiX Health, Safety & Environment",
    "summary": "M59: Health, Safety & Environment (CD-M59-01)",
    "description": """
CD-M59-01 (P09) — Health, Safety & Environment.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Health, Safety & Environment",
    "depends": ["base", "mail", "cd_entity_config", "cd_hr_core", "cd_event_outbox"],
    "data": ["security/ir.model.access.csv", "views/cd_hse_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M59-01",
    "x_module_id": "M59",
    "x_wave": "W6",
    "x_owner": "Health, Safety & Environment",
    "x_category": "Phase9",
    "x_tier": "T9",
}
