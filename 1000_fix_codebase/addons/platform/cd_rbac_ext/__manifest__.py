# cd_rbac_ext — M29 Identity, Access & Information Security (P03-M02, CD-M29-nn).
# The isolation tiers, 53 roles mapped to real permission groups (A12 R1),
# 61 SoD controls enforced at every grant path (A12 R2), the access request
# two-person approval (A12 X1), the employee.left leaver consumer (A12 X2),
# the M29 crons (A12 R3), the system-written audit trail (A12 R5).
{
    "name": "1000FiX RBAC Extension",
    "summary": "Six isolation tiers (T0-T5), 53 roles mapped to permission groups, 61 SoD controls enforced at grant, access lifecycle",
    "description": """
CD-M29-nn: the M29 RBAC extension.

Owns:
- fix.role (53 roles per the reconciled register, mapped to the estate's
  permission groups — data/fix_role_group_map.xml, A12 R1)
- fix.isolation.tier (T0 public ... T5 residency-classified, as record rules)
- fix.sod.control (61 segregation-of-duties controls from SP-006 plus the
  A08 finance duty rule set, enforced at every grant path — A12 R2)
- fix.sod.mitigation (time-boxed, approved SoD exceptions, FR-SEC-024)
- fix.field.rule (hidden and masked fields, applied with the fix.sensitive.field
  masking rules on the P03 read path; not on the ORM, reports or exports)
- fix.isolation.tier stays a documented register: no gate reads it
- fix.role.assignment (who was actually given which role: what "held" means)
- fix.access.request (X1: operational two-person approval, SoD gate at
  grant, sudo service provisioning)
- fix.jml.event (X2: consumes employee.left — deactivates the user, removes
  ALL groups, unassigns ITSM assets, audits)
- access certification, privileged sessions (R3 crons: elevation expiry,
  close-out, session timeout), encryption keys (custodian-only, real
  rotation), the hash-chained security audit trail (A12 R5) and incidents.
""",
    "version": "19.0.1.4.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Platform/Security",
    "depends": ["base", "mail", "hr", "cd_entity_config", "cd_event_outbox"],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_sod_groups.xml",
        "security/cd_rbac_ext_security.xml",
        # the groups XML must load BEFORE the ACL CSV: the CSV grants rows to
        # group_access_approver / group_key_custodian defined there
        "security/fix_role_groups.xml",
        "security/ir.model.access.csv",
        "security/fix_m29_finish_rules.xml",
        "data/fix_isolation_tiers.xml",
        "data/fix_roles.xml",
        "data/fix_role_group_map.xml",
        "data/fix_sod_controls.xml",
        "data/fix_sod_finance_controls.xml",
        "data/fix_event_consumers.xml",
        "data/fix_a12_crons.xml",
        "data/fix_a12_finish_crons.xml",
        "data/access_ops_sequences.xml",
        "data/security_ops_sequences.xml",
        "views/fix_rbac_views.xml",
        "views/fix_portal_workspace_views.xml",
        "views/fix_feature_flag_role_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M29-01",
    "x_module_id": "M29",
    "x_wave": "W1",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T0",
}
