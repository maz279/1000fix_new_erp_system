# Generated scaffold upgraded to T0 implementation — P03-M04 (M30 Platform Administration).
# Manifest conforms to AR-007 section 3.2: 1000FiX mandatory keys present.
{
    "name": "1000FiX Platform Administration & Configuration",
    "summary": "Entity, branch, cost centre, zone, working calendar, feature flags, BD address hierarchy, country-pack interface, notification routing",
    "description": """
M30 Platform Administration — the T0 configuration module.

Owns:
- fix.entity (legal entity on res.company)
- fix.branch (51+ operational branches, the OU isolation unit)
- fix.cost.center (financial cost centre)
- fix.zone + fix.geofence (dispatch zones)
- fix.working.calendar (M02's availability stub calls this)
- fix.feature.flag (every capability ships behind a flag — OPS-06)
- fix.bd.address (8 divisions / 64 districts / upazilas / unions)
- fix.country.pack (interface M51 consumes instead of M65)
- fix.notification.config (Novu channel routing, ADR-022)

CD items: CD-M30-01..CD-M30-nn per tooling/cd-register.yaml.
    """,
    "version": "19.0.1.2.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "website": "https://1000fix.com",
    "category": "Platform/Administration",
    "depends": [
        "hr",
        "base",
        "mail",
        "operating_unit",
    ],
    "data": [
        "data/fix_dofa_ladder_data.xml",
        "data/platform_ops_sequences.xml",
        "security/fix_isolation_rules.xml",
        "security/cd_entity_config_security.xml",
        "security/cd_dofa_security.xml",
        # A12: platform/MDM roles first so the ACL rows can reference them.
        "security/fix_platform_a12_groups.xml",
        "security/ir.model.access.csv",
        "data/platform_ops2_sequences.xml",
        "data/platform_ops3_sequences.xml",
        "data/platform_ops4_data.xml",
        "data/fix_a12_crons.xml",
        "views/fix_portal_shell_views.xml",
        "views/fix_entity_views.xml",
        "views/fix_branch_views.xml",
        "views/fix_zone_views.xml",
        "views/fix_working_calendar_views.xml",
        "views/fix_feature_flag_views.xml",
        "views/fix_admin_extra_views.xml",
        "data/main_company_bd.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    # --- 1000FiX mandatory keys (AR-007 section 3.2, FF-16 validated) --------
    "x_cd_id": "CD-M30-01",
    "x_module_id": "M30",
    "x_wave": "W1",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T0",
}
