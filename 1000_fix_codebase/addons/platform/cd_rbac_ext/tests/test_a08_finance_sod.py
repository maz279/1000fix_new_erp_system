# A08 S4 / S5 (A12 R2, M29-4): the finance segregation-of-duties rule set is
# enforced at EVERY grant path, for a non-admin granter and for the admin via
# the ORM; an approved, unexpired SoD exception (FR-SEC-024) lets the grant
# through; existing conflicts are reported, not blocked; superuser grants pass
# but are logged; and the synthetic finance staff of db/seeds/appoint_approvers.py
# hold no conflicting pair. Every test runs on the live ORM (`odoo_env`, rolled
# back afterwards).
import ast
import datetime
import itertools
from pathlib import Path

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

_SEQ = itertools.count(1)
SEED = Path(__file__).resolve().parents[4] / "db" / "seeds" / "appoint_approvers.py"

# The finance duty pairs shipped in data/fix_sod_finance_controls.xml (group pairs;
# the per-record maker != checker of journals, bills, credit notes, payouts, capex
# and statutory rates is enforced by the finance modules themselves).
FINANCE_CODES = ["FSOD-01", "FSOD-02"]
PATHS = [
    "user_write",
    "user_write_implied",
    "user_create",
    "group_write",
    "group_implies",
    "access_request",
    "jml_apply",
    "assign_role",
]
GRANTERS = ["non_admin", "admin"]


def _n():
    return next(_SEQ)


def _user(env, label, groups=()):
    n = _n()
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "SoD %s %d" % (label, n),
                "login": "sod.%s.%d@a08.test" % (label.lower().replace(" ", "."), n),
                "group_ids": [(6, 0, [env.ref("base.group_user").id] + [g.id for g in groups])],
            }
        )
    )


def _access_approver(env):
    """A real Access Approver (A12 X1): the one role that may decide an
    access request, and never the requester/beneficiary of it."""
    return _user(env, "Access Approver", [env.ref("cd_rbac_ext.group_access_approver")])


@pytest.fixture
def granters(odoo_env):
    """A non-admin access administrator (Access Rights + HR Officer, not Settings) and
    the Odoo admin acting through the ORM (not the superuser)."""
    env = odoo_env
    clerk = _user(
        env,
        "Granter",
        [
            env.ref("base.group_erp_manager"),  # Access Rights: may change users' groups
            env.ref("base.group_partner_manager"),  # a new login needs its contact
            env.ref("hr.group_hr_user"),  # M21 role assignment on the employee
        ],
    )
    assert not clerk.has_group("base.group_system")
    admin = env.ref("base.user_admin")
    assert admin.has_group("base.group_system") and admin.id != 1
    return {"non_admin": clerk, "admin": admin}


def _control(env, code):
    control = env["fix.sod.control"].search([("code", "=", code)])
    assert control, "%s is not shipped" % code
    pair = control._fix_pair_groups()
    assert pair, "%s cannot be measured: %s" % (code, control.pair_label)
    return control, pair


def _role(env, group):
    n = _n()
    return env["fix.role"].create(
        {"code": "R-Q%d" % n, "name": "SoD probe role %d" % n, "group_ids": [(6, 0, group.ids)]}
    )


def _employee(env, user):
    return env["hr.employee"].create({"name": "SoD Employee %d" % _n(), "user_id": user.id})


def _grant(env, path, actor, target, group):
    """Give `target` the duty `group` through one grant path, acting as `actor`."""
    if path == "user_write":
        target.with_user(actor).write({"group_ids": [(4, group.id)]})
    elif path == "user_write_implied":
        bundle = env["res.groups"].create(
            {"name": "SoD bundle %d" % _n(), "implied_ids": [(4, group.id)]}
        )
        target.with_user(actor).write({"group_ids": [(4, bundle.id)]})
    elif path == "user_create":
        # `target` is a template: a NEW user is created holding its groups + `group`.
        groups = target.group_ids | group
        env["res.users"].with_user(actor).with_context(no_reset_password=True).create(
            {
                "name": "SoD new %d" % _n(),
                "login": "sod.new.%d@a08.test" % _n(),
                "group_ids": [(6, 0, groups.ids)],
            }
        )
    elif path == "group_write":
        group.with_user(actor).write({"user_ids": [(4, target.id)]})
    elif path == "group_implies":
        own = env["res.groups"].create({"name": "SoD team %d" % _n(), "user_ids": [(4, target.id)]})
        own.with_user(actor).write({"implied_ids": [(4, group.id)]})
    elif path == "access_request":
        role = _role(env, group)
        request = env["fix.access.request"].create(
            {"user_id": target.id, "role_id": role.id, "reason": "SoD probe"}
        )
        approver = _access_approver(env)
        request.with_user(approver).action_approve()
        request.with_user(actor).action_grant()
    elif path == "jml_apply":
        role = _role(env, group)
        event = env["fix.jml.event"].create(
            {
                "event_type": "mover",
                "employee_id": _employee(env, target).id,
                "user_id": target.id,
                "role_id": role.id,
            }
        )
        event.with_user(actor).action_apply()
    elif path == "assign_role":
        role = _role(env, group)
        _employee(env, target).with_user(actor).assign_role(role.code)
    else:  # pragma: no cover
        raise AssertionError(path)


def _approver(env):
    return _user(
        env, "Exception Approver", [env.ref("cd_rbac_ext.group_fix_sod_exception_approver")]
    )


def _mitigate(env, control, user, approver=None, days=30, start=None, approve=True):
    approver = approver or _approver(env)
    requester = _user(env, "Exception Requester")
    start = start or fields.Date.context_today(env["fix.sod.mitigation"])
    waiver = (
        env["fix.sod.mitigation"]
        .with_user(requester)
        .create(
            {
                "control_id": control.id,
                "user_id": user.id,
                "mitigating_control": "Every item reviewed weekly by the Finance Controller",
                "reason": "Leave cover",
                "valid_from": start,
                "valid_until": start + datetime.timedelta(days=days),
            }
        )
    )
    if approve:
        waiver.with_user(approver).action_approve()
    return waiver


# --- the rule set ---------------------------------------------------------------


@pytest.mark.parametrize("code", FINANCE_CODES)
def test_finance_rule_is_shipped_blocking_and_measurable(odoo_env, code):
    control, (ga, gb) = _control(odoo_env, code)
    assert control.control_type == "group"
    assert control.conflict_action == "block"
    assert ga != gb and gb not in ga.all_implied_ids and ga not in gb.all_implied_ids
    data = odoo_env["ir.model.data"].search(
        [("model", "=", "fix.sod.control"), ("res_id", "=", control.id)]
    )
    assert data.module == "cd_rbac_ext" and data.noupdate


# --- preventive: every grant path, every pair ---------------------------------------


@pytest.mark.parametrize("granter", GRANTERS)
@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("code", FINANCE_CODES)
def test_conflicting_grant_is_refused(odoo_env, granters, code, path, granter):
    env = odoo_env
    control, (ga, gb) = _control(env, code)
    holder = _user(env, "Holder", [ga])
    with pytest.raises(ValidationError, match="SoD control %s" % code), env.cr.savepoint():
        _grant(env, path, granters[granter], holder, gb)
    holder.invalidate_recordset()
    assert gb not in holder.all_group_ids
    assert not env["fix.sod.control"]._fix_conflicts(user=holder) & control


# An exception names an existing user, so the user-create door has no exception case.
@pytest.mark.parametrize("path", [p for p in PATHS if p != "user_create"])
@pytest.mark.parametrize("code", FINANCE_CODES)
def test_conflicting_grant_passes_with_an_approved_unexpired_exception(
    odoo_env, granters, code, path
):
    env = odoo_env
    control, (ga, gb) = _control(env, code)
    holder = _user(env, "Holder", [ga])
    _mitigate(env, control, holder)
    _grant(env, path, granters["non_admin"], holder, gb)
    assert control in env["fix.sod.control"]._fix_conflicts(user=holder)
    audit = env["fix.security.audit"].search([("object_ref", "=", "res.users,%s" % holder.id)])
    assert any("allowed under exception" in (a.detail or "") for a in audit)


@pytest.mark.parametrize("code", FINANCE_CODES)
def test_proper_path_grant_of_a_compatible_duty_works(odoo_env, granters, code):
    env = odoo_env
    control, (ga, gb) = _control(env, code)
    other = _user(env, "Other")
    # The second duty goes to ANOTHER person: allowed on every path.
    for path in ("user_write", "group_write", "access_request", "jml_apply", "assign_role"):
        person = _user(env, "Checker")
        _grant(env, path, granters["non_admin"], person, gb)
        assert not env["fix.sod.control"]._fix_conflicts(user=person) & control
    _grant(env, "user_write", granters["non_admin"], other, ga)
    assert ga in other.all_group_ids


# --- exceptions (FR-SEC-024) ---------------------------------------------------------


def test_expired_rejected_or_draft_exception_does_not_open_the_grant(odoo_env, granters):
    env = odoo_env
    control, (ga, gb) = _control(env, FINANCE_CODES[0])
    holder = _user(env, "Holder", [ga])
    past = fields.Date.context_today(env["fix.sod.mitigation"]) - datetime.timedelta(days=40)
    lapsed = _mitigate(env, control, holder)
    # Time passes: the approved window ended 10 days ago.
    lapsed.sudo().write({"valid_from": past, "valid_until": past + datetime.timedelta(days=30)})
    assert lapsed.state == "approved" and not lapsed.is_live
    rejected = _mitigate(env, control, holder, approve=False)
    rejected.with_user(_approver(env)).action_reject()
    assert rejected.state == "rejected"
    env["fix.sod.mitigation"].create(
        {
            "control_id": control.id,
            "user_id": holder.id,
            "mitigating_control": "x",
            "reason": "draft only",
            "valid_until": fields.Date.context_today(env["fix.sod.mitigation"]),
        }
    )
    with pytest.raises(ValidationError, match="SoD control"), env.cr.savepoint():
        _grant(env, "user_write", granters["non_admin"], holder, gb)


def test_exception_needs_an_approver_other_than_grantee_and_requester(odoo_env):
    env = odoo_env
    control, (ga, _gb) = _control(env, FINANCE_CODES[0])
    approver_group = env.ref("cd_rbac_ext.group_fix_sod_exception_approver")
    grantee = _user(env, "Grantee", [ga, approver_group])
    requester = _user(env, "Requester", [approver_group])
    plain = _user(env, "Plain")
    today = fields.Date.context_today(env["fix.sod.mitigation"])
    waiver = (
        env["fix.sod.mitigation"]
        .with_user(requester)
        .create(
            {
                "control_id": control.id,
                "user_id": grantee.id,
                "mitigating_control": "Weekly review",
                "reason": "Cover",
                "valid_until": today + datetime.timedelta(days=10),
            }
        )
    )
    assert waiver.requested_by_id == requester
    with pytest.raises(UserError, match="grantee cannot approve"), env.cr.savepoint():
        waiver.with_user(grantee).action_approve()
    with pytest.raises(UserError, match="requester cannot approve"), env.cr.savepoint():
        waiver.with_user(requester).action_approve()
    with pytest.raises(AccessError, match="SoD Exception Approver"), env.cr.savepoint():
        waiver.with_user(plain).action_approve()
    # Forging the decision by a write is refused (guarded fields).
    with pytest.raises(UserError, match="changes only through its workflow"), env.cr.savepoint():
        waiver.with_user(requester).write({"state": "approved", "approved_by_id": plain.id})
    assert waiver.state == "draft"
    third = _user(env, "CFO", [approver_group])
    waiver.with_user(third).action_approve()
    assert waiver.state == "approved" and waiver.approved_by_id == third and waiver.is_live
    # Approved terms are pinned.
    with pytest.raises(UserError, match="cannot change"), env.cr.savepoint():
        waiver.with_user(requester).write({"valid_until": today + datetime.timedelta(days=60)})


def test_exception_is_time_boxed_to_the_configured_maximum(odoo_env):
    env = odoo_env
    control, (ga, _gb) = _control(env, FINANCE_CODES[0])
    grantee = _user(env, "Grantee", [ga])
    today = fields.Date.context_today(env["fix.sod.mitigation"])
    vals = {
        "control_id": control.id,
        "user_id": grantee.id,
        "mitigating_control": "Weekly review",
        "reason": "Cover",
        "valid_from": today,
    }
    with pytest.raises(ValidationError, match="at most 92 days"), env.cr.savepoint():
        env["fix.sod.mitigation"].create({**vals, "valid_until": today + datetime.timedelta(93)})
    env["ir.config_parameter"].set_param("cd_rbac_ext.sod_exception_max_days", "10")
    with pytest.raises(ValidationError, match="at most 10 days"), env.cr.savepoint():
        env["fix.sod.mitigation"].create({**vals, "valid_until": today + datetime.timedelta(11)})
    assert env["fix.sod.mitigation"].create({**vals, "valid_until": today + datetime.timedelta(10)})


def test_revoked_exception_closes_the_grant_again(odoo_env, granters):
    env = odoo_env
    control, (ga, gb) = _control(env, FINANCE_CODES[0])
    holder = _user(env, "Holder", [ga])
    waiver = _mitigate(env, control, holder)
    waiver.with_user(env.ref("base.user_admin")).action_revoke()
    assert waiver.state == "revoked" and not waiver.is_live
    with pytest.raises(ValidationError, match="SoD control"), env.cr.savepoint():
        _grant(env, "user_write", granters["non_admin"], holder, gb)


# --- existing conflicts: reported, never a lock-out ---------------------------------


def test_existing_conflict_is_reported_and_does_not_block_unrelated_changes(odoo_env, granters):
    env = odoo_env
    control, (ga, gb) = _control(env, FINANCE_CODES[0])
    legacy = _user(env, "Legacy", [ga, gb])  # superuser data loading: allowed, logged
    audit = env["fix.security.audit"].search([("object_ref", "=", "res.users,%s" % legacy.id)])
    assert any("superuser / data-loading grant" in (a.detail or "") for a in audit)
    # An unrelated grant and an unrelated revoke still work for the non-admin granter.
    extra = env["res.groups"].create({"name": "SoD unrelated %d" % _n()})
    legacy.with_user(granters["non_admin"]).write({"group_ids": [(4, extra.id)]})
    legacy.with_user(granters["non_admin"]).write({"group_ids": [(3, extra.id)]})
    report = env["fix.sod.control"].fix_report_violations()
    rows = [r for r in report["violations"] if r["user_id"] == legacy.id]
    assert [r["control"] for r in rows if r["control"] == control.code] == [control.code]
    assert not rows[0]["mitigated"] and report["unmitigated"] >= 1
    _mitigate(env, control, legacy)
    rows = [
        r
        for r in env["fix.sod.control"].fix_report_violations()["violations"]
        if r["user_id"] == legacy.id and r["control"] == control.code
    ]
    assert rows[0]["mitigated"] and rows[0]["exception"]


def test_upgrade_leaves_admin_and_seed_users_working(odoo_env, granters):
    """The check runs on CHANGE: the admin can still be given an unrelated group
    and can still grant compatible groups, whatever the admin already holds."""
    env = odoo_env
    admin = env.ref("base.user_admin")
    extra = env["res.groups"].create({"name": "SoD admin extra %d" % _n()})
    admin.with_user(admin).write({"group_ids": [(4, extra.id)]})
    assert extra in admin.group_ids
    report = env["fix.sod.control"].fix_report_violations()
    assert set(report) == {"violations", "unmitigated", "unmeasurable"}


def test_sod_test_run_measures_a_group_pair(odoo_env):
    env = odoo_env
    control, (ga, gb) = _control(env, FINANCE_CODES[0])
    both = _user(env, "Both", [ga, gb])
    run = env["fix.sod.test"].create({"control_id": control.id})
    run.action_run()
    assert run.result == "fail" and both.login in run.users_in_conflict


# --- certification "keep" ------------------------------------------------------------


def test_certifying_a_role_held_in_an_unmitigated_conflict_is_refused(odoo_env, granters):
    env = odoo_env
    control, (ga, gb) = _control(env, FINANCE_CODES[0])
    both = _user(env, "Both", [ga, gb])
    role = _role(env, gb)
    line = env["fix.access.certification"].create(
        {
            "period": "2026-Q4",
            "user_id": both.id,
            "role_id": role.id,
            "reviewer_id": granters["non_admin"].id,  # M29-7: only the assigned reviewer decides
        }
    )
    with pytest.raises(UserError, match=control.code), env.cr.savepoint():
        line.with_user(granters["non_admin"]).action_certify()
    _mitigate(env, control, both)
    line.with_user(granters["non_admin"]).action_certify()
    assert line.decision == "certified"


# --- the role register (SP-006) is enforced the same way -----------------------------


def test_role_pair_control_is_refused_at_access_request_and_assign_role(odoo_env, granters):
    env = odoo_env
    g1 = env["res.groups"].create({"name": "SoD role group A %d" % _n()})
    g2 = env["res.groups"].create({"name": "SoD role group B %d" % _n()})
    ra, rb = _role(env, g1), _role(env, g2)
    env["fix.sod.control"].create(
        {"code": "SOD-Q%d" % _n(), "name": "Probe pair", "role_a_id": ra.id, "role_b_id": rb.id}
    )
    holder = _user(env, "Role Holder", [g1])
    with pytest.raises(ValidationError, match="Probe pair"), env.cr.savepoint():
        _grant(env, "user_write", granters["non_admin"], holder, g2)
    request = env["fix.access.request"].create(
        {"user_id": holder.id, "role_id": rb.id, "reason": "probe"}
    )
    approver = _access_approver(env)
    request.with_user(approver).action_approve()
    with pytest.raises(ValidationError, match="Probe pair"), env.cr.savepoint():
        request.with_user(granters["non_admin"]).action_grant()
    emp = _employee(env, holder)
    with pytest.raises(ValidationError, match="Probe pair"), env.cr.savepoint():
        emp.with_user(granters["non_admin"]).assign_role(rb.code)


def test_superuser_grant_is_allowed_and_logged_but_workflow_grant_is_not(odoo_env):
    env = odoo_env
    control, (ga, gb) = _control(env, FINANCE_CODES[0])
    holder = _user(env, "Holder", [ga])
    holder.write({"group_ids": [(4, gb.id)]})  # superuser: data loading / seeds
    assert gb in holder.all_group_ids
    audit = env["fix.security.audit"].search([("object_ref", "=", "res.users,%s" % holder.id)])
    assert any(control.code in (a.detail or "") for a in audit)
    # The explicit workflow grant is checked whoever calls it, even sudo().
    # (A12 X1 composition: the decision needs a real Access Approver, and
    # the grant needs the intact approved request — superuser staging of the
    # DECISION is refused, so the approver is staged through the group.)
    other = _user(env, "Holder 2", [ga])
    approver = _access_approver(env)
    request = env["fix.access.request"].create(
        {"user_id": other.id, "role_id": _role(env, gb).id, "reason": "probe"}
    )
    request.with_user(approver).action_approve()
    with pytest.raises(ValidationError, match=control.code), env.cr.savepoint():
        request.sudo().action_grant()


# --- S5: the synthetic finance staff hold no conflicting pair -------------------------


class _Inline(ast.NodeTransformer):
    """Replaces the script's UPPER_CASE constant names by their literal values."""

    def __init__(self, consts):
        self.consts = consts

    def visit_Name(self, node):
        if node.id in self.consts:
            return ast.copy_location(ast.Constant(self.consts[node.id]), node)
        return node


def _seed_approvers():
    """APPROVERS as data: parsed, never executed (the script needs odoo-bin shell)."""
    tree = ast.parse(SEED.read_text(encoding="utf-8"))
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = getattr(node.targets[0], "id", None)
            if name and name.isupper():
                value = _Inline(consts).visit(node.value)
                consts[name] = ast.literal_eval(value)
    return consts["APPROVERS"]


def test_seed_finance_staff_hold_no_conflicting_pair(odoo_env):
    env = odoo_env
    rows = _seed_approvers()
    Sod = env["fix.sod.control"]
    finance = [
        Sod.search([("code", "=", c)]) for c in FINANCE_CODES if Sod.search([("code", "=", c)])
    ]
    held_by = {}
    for login, _name, xmlids in rows:
        groups = env["res.groups"]
        for xmlid in xmlids:
            group = env.ref(xmlid, raise_if_not_found=False)
            assert group, "%s (seed %s) is not installed" % (xmlid, login)
            groups |= group
        implied = groups.all_implied_ids
        held_by[login] = implied
        for control in finance:
            pair = control._fix_pair_groups()
            if pair:
                assert not (pair[0] in implied and pair[1] in implied), (
                    "%s holds both sides of %s" % (login, control.code)
                )
    count = {
        x: len([lg for lg, gs in held_by.items() if env.ref(x) in gs])
        for x in (
            "account.group_account_user",
            "account.group_account_manager",
            "account.group_account_invoice",
        )
    }
    assert count["account.group_account_user"] >= 2
    assert count["account.group_account_manager"] >= 2
    assert count["account.group_account_invoice"] >= 1
    # Every side of every finance rule has at least one holder (a seed user, or the
    # admin, who carries the A06 supplier steward role by data).
    held_by["admin"] = env.ref("base.user_admin").all_group_ids
    for control in finance:
        for group in control._fix_pair_groups() or ():
            assert any(group in gs for gs in held_by.values()), "%s: no seed holder for %s" % (
                control.code,
                group.display_name,
            )
