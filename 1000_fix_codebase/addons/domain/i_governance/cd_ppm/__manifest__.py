# cd_ppm — M67 (P10).
{
    "name": "1000FiX Project, Program & Portfolio Management",
    "summary": "M67: Project, Program & Portfolio Management (CD-M67-01)",
    "description": """
CD-M67-01 (P10) — Project, Program & Portfolio Management.
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Project, Program & Portfolio Management",
    "depends": ["base", "mail", "cd_entity_config", "cd_hr_core", "cd_event_outbox"],
    "data": ["security/ir.model.access.csv", "views/cd_ppm_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M67-01",
    "x_module_id": "M67",
    "x_wave": "W7",
    "x_owner": "Project, Program & Portfolio Management",
    "x_category": "Phase10",
    "x_tier": "T10",
}
