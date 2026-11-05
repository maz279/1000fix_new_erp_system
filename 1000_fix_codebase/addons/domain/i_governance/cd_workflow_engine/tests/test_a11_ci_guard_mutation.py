"""A11 audit P3 — the mutation regression the build report claimed but did
not ship: a live offending ACL row is planted (inside this test's rolled-back
transaction) on an unguarded M63 configuration model, and the CI guard's own
detection logic must name it.

This exercises the guard's query and guarded/unguarded discrimination — the
data-level proof that test_a11_ci_guard fails closed on a real offender, not
just on an empty table. Companion to the manual 10-mutation exercise recorded
in working/A11_Build_Report.md §4 (M10): that run planted the row by hand;
this test keeps the proof in the suite forever.
"""

# The same universe test_a11_ci_guard scans (kept in sync deliberately:
# changing one without the other is caught by test_no_unguarded_m63...).
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


def _scan_offenders(env):
    """The same scan test_a11_ci_guard runs, factored so the mutation test
    can assert on its OUTPUT instead of its silence."""
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
                offenders.append(model_name)
    return offenders


def test_planted_offending_acl_is_caught_by_the_guard_scan(odoo_env):
    """Plant a base.group_user WRITE line on the unguarded matrix model and
    require the scan to name it. Everything rolls back with the test."""
    env = odoo_env
    matrix = env["ir.model"].sudo().search([("model", "=", "fix.approval.matrix")], limit=1)
    assert matrix, "fix.approval.matrix is not registered — the guard would scan nothing"

    env["ir.model.access"].sudo().create(
        {
            "name": "MUTATION planted offending ACL (rolled back)",
            "model_id": matrix.id,
            "group_id": env.ref("base.group_user").id,
            "perm_read": True,
            "perm_write": True,
            "perm_create": False,
            "perm_unlink": False,
        }
    )

    offenders = _scan_offenders(env)
    assert "fix.approval.matrix" in offenders, (
        "the CI guard scan did NOT catch a planted base.group_user write line on "
        "fix.approval.matrix — the guard's detection is broken: %s" % offenders
    )


def test_planted_line_on_a_guarded_model_is_not_an_offender(odoo_env):
    """The discriminator, not just the query: the same planted line on a
    guard-policed model (fix.approval.substitution keeps base write by
    design, policed by fix.guarded.mixin) must NOT be named."""
    env = odoo_env
    sub = env["ir.model"].sudo().search(
        [("model", "=", "fix.approval.substitution")], limit=1
    )
    assert sub, "fix.approval.substitution is not registered"
    assert hasattr(env["fix.approval.substitution"], "_fix_guarded_fields"), (
        "fix.approval.substitution lost its guard — the base-write ACL is now an "
        "open door"
    )

    env["ir.model.access"].sudo().create(
        {
            "name": "MUTATION planted guarded-model line (rolled back)",
            "model_id": sub.id,
            "group_id": env.ref("base.group_user").id,
            "perm_read": True,
            "perm_write": True,
            "perm_create": False,
            "perm_unlink": False,
        }
    )

    offenders = _scan_offenders(env)
    assert "fix.approval.substitution" not in offenders, (
        "the scan flags the deliberately self-service, guard-policed substitution "
        "model as an offender — the guarded/unguarded discrimination is broken: %s"
        % offenders
    )
