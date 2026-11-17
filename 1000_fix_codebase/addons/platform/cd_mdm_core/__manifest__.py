# cd_mdm_core — M64-core MDM governance (P03-M07-T01, MV-04).
# The change-request model and the golden-record rule engine.
# It governs the W1 kernels (M33, M37) — it cannot arrive after them.
{
    "name": "1000FiX MDM Core",
    "summary": "MDM governance: change-request model and golden-record rule engine (M64-core, MV-04)",
    "description": """
CD-M64-nn: the MDM governance core (M64-core, moved to W1 by MV-04).

Owns:
- fix.mdm.change.request (the change-request model for master data governance)
- fix.mdm.golden.rule (the golden-record rule engine consumed by M33's dedup)
- fix.mdm.match.rule (field-level match rules for dedup scoring)
- fix.mdm.governed.attribute (what a change request may write)

Wired to M33 (party) and M37 (catalogue) as the governance layer over both.
The rest of M64 (full workflow, data quality dashboards) stays in W2.
""",
    "version": "19.0.1.3.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Platform/MDM",
    "depends": [
        "base",
        "mail",
        "product",
        "cd_entity_config",
        "cd_event_outbox",
        "cd_workflow_engine",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "security/fix_mdm_rules.xml",
        "data/fix_mdm_core_data.xml",
        "data/fix_mdm_governed_data.xml",
        "data/fix_mdm_crons.xml",
        "views/fix_mdm_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M64-01",
    "x_module_id": "M64",
    "x_wave": "W1",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T1",
}
