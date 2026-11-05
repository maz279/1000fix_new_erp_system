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
    # account: fix.project.billing.invoice_id -> account.move (A12 M67-1,
    # "Mark invoiced" creates the real customer invoice).
    "depends": [
        "base",
        "mail",
        "account",
        "cd_entity_config",
        "cd_hr_core",
        "cd_event_outbox",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        # A12: roles first so the ACL rows below can reference them.
        "security/fix_ppm_a12_groups.xml",
        "security/ir.model.access.csv",
        "data/ppm_ops_sequences.xml",
        "data/fix_ppm_a12_sequences.xml",
        "data/fix_ppm_a12_crons.xml",
        "data/fix_a12_event_consumers.xml",
        "views/cd_ppm_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M67-01",
    "x_module_id": "M67",
    "x_wave": "W7",
    "x_owner": "Project, Program & Portfolio Management",
    "x_category": "Phase10",
    "x_tier": "T10",
}
