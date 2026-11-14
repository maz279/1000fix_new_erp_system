# cd_rbac_ext — M29 RBAC extension (P03-M02)
# Import order is ruff-isort alphabetised; it is also order-SAFE: the
# display-roll extensions live inside their base model files, and
# access_posture_display only inherits res.users (a base model).
from . import (
    access_posture_display,
    fix_access_ops,
    fix_feature_flag_ext,
    fix_field_rule,
    fix_isolation_tier,
    fix_module_permission,
    fix_role,
    fix_role_assignment,
    fix_security_ops,
    fix_sod_control,
    # A08 S4 additions (B6): the group-pair extension (same _name, merges
    # into fix.sod.control), then the grant-path hooks and mitigations that
    # call it. Order matters: the extension must load after the base.
    fix_sod_control_groups,
    fix_sod_grant_hooks,
    fix_sod_mitigation,
    fix_vulnerability,
    res_users_ext,
    res_users_sod,
    residency_mixin,
)
