# cd_dynamic_pricing — M11 (P10).
{
    "name": "1000FiX Dynamic Pricing (W7)",
    "summary": "M11: Dynamic Pricing (W7) (CD-M11-01)",
    "description": """
CD-M11-01 (P10) — Dynamic Pricing (W7).
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Dynamic Pricing (W7)",
    "depends": ["base", "mail", "cd_entity_config", "cd_rate_card", "cd_event_outbox"],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "views/cd_dynamic_pricing_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M11-01",
    "x_module_id": "M11",
    "x_wave": "W7",
    "x_owner": "Dynamic Pricing (W7)",
    "x_category": "Phase10",
    "x_tier": "T10",
}
