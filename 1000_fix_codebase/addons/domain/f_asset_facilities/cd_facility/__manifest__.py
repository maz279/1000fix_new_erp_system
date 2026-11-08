# cd_facility — M47 (P10).
{
    "name": "1000FiX Facility & Branch Infrastructure",
    "summary": "M47: Facility & Branch Infrastructure (CD-M47-01)",
    "description": """
CD-M47-01 (P10) — Facility & Branch Infrastructure.
""",
    "version": "19.0.0.1.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Facility & Branch Infrastructure",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_equipment_register",
        "cd_event_outbox",
        # A07 P0 recipe: the routed approval engine (fix.approvable.mixin)
        "cd_workflow_engine",
    ],
    "data": [
        # A07 P1: the M47 roles load before the ACLs that name them
        "security/cd_facility_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/fix_facility_scope_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
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
