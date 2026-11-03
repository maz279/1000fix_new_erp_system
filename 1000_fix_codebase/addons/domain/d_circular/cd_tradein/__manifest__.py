# cd_tradein — M14 (P09).
{
    "name": "1000FiX Trade-In, Refurbishment & Resale",
    "summary": "M14: Trade-In, Refurbishment & Resale (CD-M14-01)",
    "description": """
CD-M14-01 (P09) — Trade-In, Refurbishment & Resale.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Trade-In, Refurbishment & Resale",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_party_master",
        "cd_device_registry",
        "cd_catalogue",
        "cd_service_order",
        "cd_data_case",
        "cd_consignment",
        "cd_workshop",
        "cd_cash_position",
        "cd_inventory",
        "cd_event_outbox",
        "cd_workflow_engine",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/cd_tradein_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M14-01",
    "x_module_id": "M14",
    "x_wave": "W6",
    "x_owner": "Trade-In, Refurbishment & Resale",
    "x_category": "Phase9",
    "x_tier": "T9",
}
