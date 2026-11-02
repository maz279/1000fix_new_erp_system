# cd_facility — M47 (P10).
{
    "name": "1000FiX Facility & Branch Infrastructure",
    "summary": "M47: Facility & Branch Infrastructure (CD-M47-01)",
    "description": """
CD-M47-01 (P10) — Facility & Branch Infrastructure.
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Facility & Branch Infrastructure",
    "depends": ["base", "mail", "cd_entity_config", "cd_equipment_register", "cd_event_outbox"],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/cd_facility_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M47-01",
    "x_module_id": "M47",
    "x_wave": "W7",
    "x_owner": "Facility & Branch Infrastructure",
    "x_category": "Phase10",
    "x_tier": "T10",
}
