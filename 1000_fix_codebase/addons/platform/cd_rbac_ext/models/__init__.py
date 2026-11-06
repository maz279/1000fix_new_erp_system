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
    fix_role,
    fix_security_ops,
    fix_sod_control,
    # A08 S4 additions (B6): grant-path SoD hooks and time-boxed mitigations.
    # They only _inherit models loaded above, so order stays safe.
    fix_sod_grant_hooks,
    fix_sod_mitigation,
    res_users_ext,
    res_users_sod,
    residency_mixin,
)
