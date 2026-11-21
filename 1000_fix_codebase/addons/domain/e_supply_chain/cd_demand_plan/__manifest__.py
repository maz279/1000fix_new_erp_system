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
    "version": "19.0.0.4.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Demand Planning & Replenishment",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_catalogue",
        "cd_event_outbox",
        "cd_requisition",
        "cd_inventory",
    ],
    "data": [
        "security/fix_demand_plan_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/fix_demand_config.xml",
        "data/ir_cron.xml",
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
