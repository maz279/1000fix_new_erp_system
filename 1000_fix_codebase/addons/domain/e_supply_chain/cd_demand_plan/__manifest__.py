# cd_demand_plan — M43 (P09).
{
    "name": "1000FiX Demand Planning & Replenishment",
    "summary": "M43: Demand Planning & Replenishment (CD-M43-01)",
    "description": """
CD-M43-01 (P09) — Demand Planning & Replenishment.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Demand Planning & Replenishment",
    "depends": ["base", "mail", "cd_entity_config", "cd_catalogue", "cd_event_outbox"],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "views/cd_demand_plan_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M43-01",
    "x_module_id": "M43",
    "x_wave": "W6",
    "x_owner": "Demand Planning & Replenishment",
    "x_category": "Phase9",
    "x_tier": "T9",
}
