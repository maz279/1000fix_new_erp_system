# cd_partner — M40 (P10).
{
    "name": "1000FiX Partner, Channel & Franchise",
    "summary": "M40: Partner, Channel & Franchise (CD-M40-01)",
    "description": """
CD-M40-01 (P10) — Partner, Channel & Franchise.
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Partner, Channel & Franchise",
    "depends": [
        "base",
        "portal",
        "mail",
        "cd_entity_config",
        "cd_rbac_ext",
        "cd_party_master",
        "cd_contract_core",
        "cd_event_outbox",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_partner_security.xml",
        "security/ir.model.access.csv",
        "views/cd_partner_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M40-01",
    "x_module_id": "M40",
    "x_wave": "W7",
    "x_owner": "Partner, Channel & Franchise",
    "x_category": "Phase10",
    "x_tier": "T10",
}
