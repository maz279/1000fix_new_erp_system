# cd_rbac_ext — M29 Identity, Access & Information Security (P03-M02, CD-M29-nn).
# The field-level permission engine, the six isolation tiers, 53 roles,
# 61 SoD controls, OIDC federation, step-up auth, access lifecycle.
{
    "name": "1000FiX RBAC Extension",
    "summary": "Field-level permissions, six isolation tiers (T0-T5), 53 roles, 61 SoD controls, OIDC federation",
    "description": """
CD-M29-nn: the M29 RBAC extension.

Owns:
- fix.role (53 roles per the reconciled register, mapped to Keycloak realm roles)
- fix.isolation.tier (T0 public ... T5 residency-classified, as record rules)
- fix.sod.control (61 segregation-of-duties controls from SP-006)
- fix.field.rule (the field-level permission engine — security/<module>_field_rules.xml)
- fix.access.log (privileged session recording, NFR-070/SC-010)
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Platform/Security",
    "depends": ["base", "mail", "cd_entity_config"],
    "data": ["security/ir.model.access.csv", "security/cd_rbac_ext_security.xml",
             "security/fix_role_groups.xml",
             "data/fix_isolation_tiers.xml",
             "data/fix_roles.xml",
             "data/fix_sod_controls.xml",
             "views/fix_rbac_views.xml", "views/fix_portal_workspace_views.xml",
             "views/fix_feature_flag_role_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M29-01",
    "x_module_id": "M29",
    "x_wave": "W1",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T0",
}
