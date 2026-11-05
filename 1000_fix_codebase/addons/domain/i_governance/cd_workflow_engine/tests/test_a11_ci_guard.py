"""A11 audit P3 — the CI guard: no M63 configuration model grants create or
write to base.group_user unless the model itself is guard-policed.

E1 closed the rule book with ACLs (matrix, automation, business rule,
workflow instance: read-only for internal users, writable by the DoA
administrator). Two models deliberately keep base write/create access for
self-service — fix.approval.substitution (the absent approver records their
own) and fix.workflow.task (the assignee decides their own) — and both are
policed by fix.guarded.mixin write guards. This test fails the build if a
future ACL line hands an UNGUARDED M63 model to every internal user.
"""

M63_CONFIG_MODELS = (
    "fix.approval.matrix",
    "fix.approval.substitution",
    "fix.approval.request",
    "fix.approval.history",
    "fix.business.rule",
    "fix.automation",
    "fix.workflow.instance",
    "fix.workflow.task",
)


def test_no_unguarded_m63_config_model_is_writable_by_base_users(odoo_env):
    env = odoo_env
    Access = env["ir.model.access"].sudo()
    offenders = []
    for model_name in M63_CONFIG_MODELS:
        if model_name not in env:
            continue
        model = env[model_name]
        guarded = hasattr(model, "_fix_guarded_fields")
        for access in Access.search(
            [
                ("model_id.model", "=", model_name),
                ("group_id", "=", env.ref("base.group_user").id),
            ]
        ):
            if (access.perm_create or access.perm_write) and not guarded:
                offenders.append(
                    "%s grants base.group_user %s%s on %s (unguarded)"
                    % (
                        access.name,
                        "create" if access.perm_create else "",
                        "write" if access.perm_write else "",
                        model_name,
                    )
                )
    assert not offenders, (
        "unguarded M63 configuration writable by every internal user: %s" % offenders
    )


def test_the_rule_book_is_read_only_for_base_users(odoo_env):
    """The E1 core: matrix, automation, business rule and workflow instance
    carry NO base.group_user write or create line at all — the DoA
    administrator owns them."""
    env = odoo_env
    Access = env["ir.model.access"].sudo()
    for model_name in (
        "fix.approval.matrix",
        "fix.automation",
        "fix.business.rule",
        "fix.workflow.instance",
    ):
        lines = Access.search(
            [
                ("model_id.model", "=", model_name),
                ("group_id", "=", env.ref("base.group_user").id),
                "|",
                ("perm_write", "=", True),
                ("perm_create", "=", True),
            ]
        )
        assert not lines, "%s is writable by base.group_user again: %s" % (
            model_name,
            lines.mapped("name"),
        )
