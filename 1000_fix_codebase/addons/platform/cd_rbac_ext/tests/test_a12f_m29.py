"""A12 finish, M29: every engineering item of working/A12_evidence/finish/m29/FINDINGS.md,
proven as NON-admin role holders, through the methods and the same controller the
screens call (/p03/model/write, /p03/model/action, /p03/model/records, /p03/model/form)
with the kwargs the JS sends. test_a12f_eN_* names the finding.
"""

import re
import types
from datetime import timedelta
from pathlib import Path

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.service.model import call_kw

REFUSED = (UserError, ValidationError, AccessError)
APPROVER = "cd_rbac_ext.group_access_approver"
CUSTODIAN = "cd_rbac_ext.group_key_custodian"
OFFICER = "cd_rbac_ext.group_security_officer"
SODX = "cd_rbac_ext.group_fix_sod_exception_approver"
CLEARANCE = "cd_rbac_ext.group_sensitive_data_clearance"
FILL = "contained by isolating the host and rotating credentials"
JS = Path(__file__).resolve().parents[2] / "cd_p03_portal" / "static" / "src" / "a12" / "m29.js"


class Ctx:
    """The cast of a test, each created the first time the test names them: user
    creation runs the SoD doors, so a fixture creating all of them is the slow part."""

    _USERS = {
        "p": ("a12f_plain", ()),
        "p2": ("a12f_plain2", ()),
        "mgr": ("a12f_manager", ()),
        "appr": ("a12f_approver", (APPROVER,)),
        "ua": ("a12f_useradmin", ("base.group_erp_manager",)),
        "cust": ("a12f_custodian", (CUSTODIAN,)),
        "hr": ("a12f_hr", ("hr.group_hr_user",)),
        "sodx": ("a12f_sodx", (SODX,)),
        "sys": ("a12f_system", ("base.group_system",)),
        "off1": ("a12f_officer1", (OFFICER,)),
        "off2": ("a12f_officer2", (OFFICER,)),
        "tgt": ("a12f_target", ()),
    }

    def __getattr__(self, name):
        if name in self._USERS:
            login, groups = self._USERS[name]
            value = _user(self.env, login, groups)
            if name == "tgt":  # reports to mgr: reviewer resolution reads that
                self.e_tgt = _emp(self.env, value, "a12f tgt emp", parent=self.e_mgr)
        elif name == "e_mgr":
            value = _emp(self.env, self.mgr, "a12f mgr emp")
        elif name == "e_p":
            value = _emp(self.env, self.p, "a12f p emp", parent=self.e_mgr)
        elif name == "e_tgt":
            _ = self.tgt  # creating the target creates this too
            return self.__dict__["e_tgt"]
        else:
            raise AttributeError(name)
        setattr(self, name, value)
        return value


def _user(env, login, groups=()):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    ou = env["operating.unit"].search([], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "email": "%s@a12f.test" % login,
                "group_ids": [(6, 0, gids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


def _emp(env, user, name, parent=None):
    vals = {"name": name, "employee_code": name.replace(" ", "")[:18]}
    if user:
        vals["user_id"] = user.id
    if parent:
        vals["parent_id"] = parent.id
    return env["hr.employee"].sudo().create(vals)


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = Ctx()
    x.env = env
    x.role = lambda code: env["fix.role"].sudo().search([("code", "=", code)], limit=1)
    x.admin = env.ref("base.user_admin")
    x.today = fields.Date.context_today(env["fix.access.request"])
    return x


@pytest.fixture
def p03(odoo_env):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()

    def ep(name):
        f = getattr(g.P03GenericApiController, name)
        return getattr(f, "original_endpoint", f)

    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def call(user, name, **kw):
        req = types.SimpleNamespace(env=odoo_env(user=user.id))
        g.request = req
        s.request = req
        return ep(name)(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            write=lambda user, **kw: call(user, "model_write", **kw),
            action=lambda user, **kw: call(user, "model_action", **kw),
            records=lambda user, **kw: call(user, "model_records", **kw),
            form=lambda user, **kw: call(user, "model_form", **kw),
        )
    finally:
        g.request, s.request = old_g, old_s


def has(user, group):
    if isinstance(group, str):
        group = user.env.ref(group)
    user.sudo().invalidate_recordset(["group_ids", "all_group_ids"])
    return group in user.sudo().all_group_ids


def rg(c, code):
    return c.role(code).group_ids.sudo()


def areq(c, by, role, target, **kw):
    vals = {
        "user_id": target.id,
        "role_id": c.role(role).id,
        "reason": "a12f test",
        "request_type": "grant",
    }
    vals.update(kw)
    return c.env["fix.access.request"].with_user(by).create(vals)


def granted(c, role, target):
    r = areq(c, c.p2, role, target)
    r.with_user(c.appr).action_approve()
    r.with_user(c.appr).action_grant()
    assert r.state == "granted"
    return r


def revoke_via_request(c, role, target):
    r = areq(c, c.p2, role, target, request_type="revoke")
    r.with_user(c.appr).action_approve()
    r.with_user(c.appr).action_grant()
    assert r.state == "revoked"
    return r


def audit_count(c, event=None, ref=None):
    domain = []
    if event:
        domain.append(("event", "=", event))
    if ref:
        domain.append(("object_ref", "=", ref))
    return c.env["fix.security.audit"].sudo().search_count(domain)


def left_event(emp):
    return {
        "event_id": "evt-%d" % emp.id,
        "event_type": "employee.left",
        "aggregate_id": emp.id,
        "payload": {"employee_id": emp.id, "left_date": str(fields.Date.today())},
        "metadata": {},
    }


def cert_line(c, role="R-30", user=None, reviewer=None, **kw):
    user = user or c.tgt
    user.sudo().write({"group_ids": [(4, g.id) for g in rg(c, role)]})
    vals = {
        "period": "2026-Q4",
        "user_id": user.id,
        "role_id": c.role(role).id,
        "reviewer_id": (reviewer or c.mgr).id,
    }
    vals.update(kw)
    return c.env["fix.access.certification"].sudo().create(vals)


def incident(c, **kw):
    vals = {"title": "a12f incident", "severity": "critical", "category": "data_leak"}
    vals.update(kw)
    return c.env["fix.security.incident"].sudo().create(vals)


# ================================================================ E1 leaver consumer
def test_a12f_e1_plain_user_cannot_call_the_consumer(c):
    with pytest.raises(REFUSED):
        call_kw(
            c.env["fix.jml.event"].with_user(c.p2),
            "consume_employee_left",
            [left_event(c.e_mgr)],
            {},
        )
    with pytest.raises(REFUSED):
        c.env["fix.jml.event"].with_user(c.p2).consume_employee_left(left_event(c.e_mgr))
    assert c.mgr.sudo().active and c.mgr.sudo().group_ids


def test_a12f_e1_event_for_someone_still_employed_is_not_believed(c):
    assert c.env["fix.jml.event"].sudo().consume_employee_left(left_event(c.e_mgr)) is True
    assert c.mgr.sudo().active
    assert not c.env["fix.jml.event"].sudo().search_count([("employee_id", "=", c.e_mgr.id)])


def test_a12f_e1_admin_survives_a_leaver_event(c):
    _user(c.env, "a12f_sys2", ["base.group_system"])
    emp = (
        c.env["hr.employee"]
        .sudo()
        .with_context(active_test=False)
        .search([("user_id", "=", c.admin.id)], limit=1)
    ) or _emp(c.env, c.admin, "a12f admin emp")
    emp.sudo().write({"left_date": str(fields.Date.today())})
    c.env["fix.jml.event"].sudo().consume_employee_left(left_event(emp))
    admin = c.admin.sudo().with_context(active_test=False)
    admin.invalidate_recordset()
    assert admin.active and c.env.ref("base.group_system") in admin.all_group_ids
    jml = c.env["fix.jml.event"].sudo().search([("employee_id", "=", emp.id)])
    assert jml.state == "applied" and "access kept" in jml.result_note


def test_a12f_e1_shared_login_is_kept(c):
    co = c.env["res.company"].sudo().create({"name": "a12f second co"})
    c.tgt.sudo().write({"company_ids": [(4, co.id)]})
    c.env["hr.employee"].sudo().create(
        {
            "name": "a12f tgt emp2",
            "employee_code": "a12ftgt2",
            "user_id": c.tgt.id,
            "company_id": co.id,
        }
    )
    c.e_tgt.sudo().write({"left_date": str(fields.Date.today())})
    c.env["fix.jml.event"].sudo().consume_employee_left(left_event(c.e_tgt))
    assert c.tgt.sudo().active


def test_a12f_e1_real_leaver_through_outbox_and_relay(c):
    c.tgt.sudo().write({"group_ids": [(4, c.env.ref("hr.group_hr_manager").id)]})
    c.e_tgt.with_user(c.hr).action_mark_left()
    outbox = c.env["fix.event.outbox"].sudo()
    event = outbox.search(
        [("event_type", "=", "employee.left"), ("aggregate_id", "=", str(c.e_tgt.id))],
        limit=1,
        order="id desc",
    )
    assert event, "no outbox row"
    consumer = c.env.ref("cd_rbac_ext.consumer_employee_left_deprovision")
    assert not outbox._relay_deliver(consumer, event)
    tgt = c.tgt.sudo().with_context(active_test=False)
    tgt.invalidate_recordset()
    assert not tgt.active and not tgt.group_ids


def test_a12f_e1_future_leaving_date_waits_on_the_screen(c):
    tomorrow = c.today + timedelta(days=5)
    c.e_tgt.sudo().write({"left_date": str(tomorrow)})
    c.env["fix.jml.event"].sudo().consume_employee_left(left_event(c.e_tgt))
    jml = c.env["fix.jml.event"].sudo().search([("employee_id", "=", c.e_tgt.id)])
    assert jml.state == "pending" and jml.effective_on == tomorrow
    assert c.tgt.sudo().active


# ================================================================ E2 approved request pinned
@pytest.mark.parametrize(
    "vals",
    [
        {"role": "R-33"},
        {"user": True},
        {"request_type": "elevate"},
    ],
)
def test_a12f_e2_approved_request_is_pinned(c, vals):
    r = areq(c, c.p, "R-08", c.tgt)
    r.with_user(c.appr).action_approve()
    write = {}
    if "role" in vals:
        write["role_id"] = c.role(vals["role"]).id
    if "user" in vals:
        write["user_id"] = c.p.id
    if "request_type" in vals:
        write["request_type"] = vals["request_type"]
    with pytest.raises(REFUSED):
        r.with_user(c.p).write(write)


def test_a12f_e2_requester_rewrites_refused_and_platform_admin_not_gained(c):
    r = areq(c, c.p, "R-08", c.p2)
    r.with_user(c.appr).action_approve()
    with pytest.raises(REFUSED):
        r.with_user(c.p).write({"role_id": c.role("R-33").id})
    r.invalidate_recordset()
    assert r.role_id == c.role("R-08")
    assert not has(c.p2, "cd_entity_config.group_platform_admin")


def test_a12f_e2_requested_by_cannot_be_forged(c):
    r = (
        c.env["fix.access.request"]
        .with_user(c.appr)
        .create(
            {
                "user_id": c.tgt.id,
                "role_id": c.role("R-33").id,
                "reason": "x",
                "requested_by_id": c.p2.id,
            }
        )
    )
    assert r.requested_by_id == c.appr
    with pytest.raises(REFUSED):
        r.with_user(c.appr).action_approve()
    with pytest.raises(REFUSED):
        r.with_user(c.appr).write({"requested_by_id": c.p2.id})


def test_a12f_e2_bystander_cannot_edit_a_submitted_request(c):
    r = areq(c, c.p, "R-08", c.tgt)
    with pytest.raises(REFUSED):
        r.with_user(c.p2).write({"user_id": c.p2.id})


def test_a12f_e2_elevated_user_cannot_extend_own_window(c):
    r = areq(c, c.p, "R-30", c.tgt, request_type="elevate", valid_until=c.today + timedelta(days=1))
    r.with_user(c.appr).action_approve()
    r.with_user(c.appr).action_grant()
    with pytest.raises(REFUSED):
        r.with_user(c.tgt).write({"valid_until": str(c.today + timedelta(days=20))})


# ================================================================ E3 revoke removes the access
@pytest.mark.parametrize("code", ["R-13", "R-01", "R-11", "R-42"])
def test_a12f_e3_revoke_on_a_shared_group_role_removes_it(c, code):
    granted(c, code, c.tgt)
    groups = rg(c, code)
    assert all(has(c.tgt, g) for g in groups)
    revoke_via_request(c, code, c.tgt)
    assert not any(g in c.tgt.sudo().group_ids for g in groups)
    assert c.role(code) not in c.env["fix.sod.control"].user_held_roles(c.tgt)


def test_a12f_e3_revoke_keeps_what_another_assigned_role_needs(c):
    granted(c, "R-33", c.tgt)
    granted(c, "R-52", c.tgt)
    revoke_via_request(c, "R-52", c.tgt)
    assert has(c.tgt, "cd_itsm.group_itsm_agent")
    revoke_via_request(c, "R-33", c.tgt)
    assert not has(c.tgt, "cd_itsm.group_itsm_agent")


def test_a12f_e3_every_role_is_fully_revocable_when_it_is_the_only_one(c):
    jml = c.env["fix.jml.event"]
    bad = {}
    portal = c.env.ref("base.group_portal")
    for role in c.env["fix.role"].sudo().search([("active", "=", True)]):
        groups = role.group_ids
        if portal in groups or not groups:
            continue
        user = _user(c.env, "a12f_rv_%s" % role.code.lower().replace("-", ""))
        user.sudo().write({"group_ids": [(4, g.id) for g in groups]})
        jml._apply_role_revoke(user, role)
        left = groups & user.sudo().group_ids
        if left:
            bad[role.code] = left.mapped("name")
    assert not bad


def test_a12f_e3_certification_and_closeout_on_a_shared_role(c):
    cert = cert_line(c, role="R-13")
    cert.with_user(c.mgr).action_revoke()
    assert not has(c.tgt, "cd_itsm.group_itsm_agent")
    other = _user(c.env, "a12f_shared2")
    line = cert_line(c, role="R-13", user=other, due_on=str(c.today - timedelta(days=1)))
    c.env["fix.access.certification"].sudo().cron_close_certifications()
    assert line.decision == "revoked" and not has(other, "cd_itsm.group_itsm_agent")


def test_a12f_e3_revoke_clears_the_employee_master_role(c):
    role = c.role("R-08")
    c.e_tgt.sudo().write({"additional_role_ids": [(4, role.id)]})
    granted(c, "R-08", c.tgt)
    revoke_via_request(c, "R-08", c.tgt)
    assert role not in c.e_tgt.additional_role_ids
    assert role not in c.env["fix.sod.control"].user_held_roles(c.tgt)


# ================================================================ E4 certification lines
def test_a12f_e4_plain_user_cannot_mint_or_edit_a_line(c):
    c.tgt.sudo().write({"group_ids": [(4, c.env.ref("hr.group_hr_manager").id)]})
    vals = {"period": "2026-Q4", "user_id": c.tgt.id, "role_id": c.role("R-30").id}
    with pytest.raises(AccessError):
        c.env["fix.access.certification"].with_user(c.p2).create(vals)
    assert has(c.tgt, "hr.group_hr_manager")
    line = cert_line(c)
    with pytest.raises(REFUSED):
        line.with_user(c.p2).write({"reviewer_id": c.p2.id})
    with pytest.raises(AccessError):
        line.with_user(c.p2).write({"due_on": str(c.today + timedelta(days=99))})
    with pytest.raises(REFUSED):
        line.with_user(c.p2).action_certify()


def test_a12f_e4_admin_cannot_repoint_the_reviewer(c):
    line = cert_line(c)
    with pytest.raises(UserError):
        line.with_user(c.appr).write({"reviewer_id": c.appr.id})


def test_a12f_e4_line_needs_a_held_role(c):
    with pytest.raises(ValidationError):
        c.env["fix.access.certification"].sudo().create(
            {
                "period": "2026-Q4",
                "user_id": c.tgt.id,
                "role_id": c.role("R-33").id,
                "reviewer_id": c.mgr.id,
            }
        )


def test_a12f_e4_line_born_past_due_refused(c):
    c.tgt.sudo().write({"group_ids": [(4, c.env.ref("hr.group_hr_manager").id)]})
    with pytest.raises(ValidationError):
        c.env["fix.access.certification"].with_user(c.appr).create(
            {
                "period": "2026-Q4",
                "user_id": c.tgt.id,
                "role_id": c.role("R-30").id,
                "reviewer_id": c.mgr.id,
                "due_on": str(c.today - timedelta(days=1)),
            }
        )


def test_a12f_e4_reviewer_decides_with_read_only_acl_through_screen(c, p03):
    line = cert_line(c)
    res = p03.action(
        c.mgr, model="fix.access.certification", ids=[line.id], method="action_certify"
    )
    assert res["success"], res
    assert line.decision == "certified"


# ================================================================ E5 no ghost roles
def test_a12f_e5_one_granted_role_holds_exactly_that_role(c):
    Sod = c.env["fix.sod.control"]
    bad = {}
    portal = c.env.ref("base.group_portal")
    for role in c.env["fix.role"].sudo().search([("active", "=", True)]):
        if portal in role.group_ids or not role.group_ids:
            continue
        user = _user(c.env, "a12f_g_%s" % role.code.lower().replace("-", ""))
        c.env["fix.jml.event"]._apply_role_grant(user, role, source="test")
        held = Sod.user_held_roles(user)
        if held != role:
            bad[role.code] = held.mapped("code")
    assert not bad


def test_a12f_e5_no_false_block_from_a_role_never_given(c):
    granted(c, "R-30", c.tgt)
    r = areq(c, c.p, "R-19", c.tgt)
    r.with_user(c.appr).action_approve()
    r.with_user(c.appr).action_grant()
    assert r.state == "granted"


def test_a12f_e5_access_review_counts_true_roles(c):
    from odoo.addons.cd_p03_portal.controllers.a12 import m29

    c.tgt.sudo().write({"group_ids": [(4, c.env.ref("cd_itsm.group_itsm_agent").id)]})
    row = next(
        r for r in m29.access_review(c.env(user=c.ua.id))["rows"] if r["login"] == c.tgt.login
    )
    assert row["role_count"] == 0  # a group three roles share names none of them
    granted(c, "R-13", c.tgt)
    row = next(
        r for r in m29.access_review(c.env(user=c.ua.id))["rows"] if r["login"] == c.tgt.login
    )
    assert row["roles"] == "R-13"


# ================================================================ E6 map + migration
def test_a12f_e6_shipped_map_separates_every_pair(c):
    Sod = c.env["fix.sod.control"].sudo()
    bad = [
        ct.code
        for ct in Sod.search([("control_type", "=", "role"), ("active", "=", True)])
        if ct.role_a_id.group_ids & ct.role_b_id.group_ids
    ]
    assert not bad


def test_a12f_e6_legacy_group_id_is_not_read(c):
    role_a, role_b = c.role("R-30"), c.role("R-19")
    shared = c.env.ref("cd_rbac_ext.group_ws_administration")
    for role in (role_a, role_b):
        role.sudo().write({"group_id": shared.id})
    assert shared not in c.env["fix.sod.control"]._role_groups(role_a)
    granted(c, "R-30", c.tgt)
    assert not has(c.tgt, shared)


def test_a12f_e6_migration_cleared_map_and_old_job(c):
    assert not c.env["fix.role"].sudo().search_count([("group_id", "!=", False)])
    assert not c.env.ref("cd_rbac_ext.ir_cron_access_revoke_expired", raise_if_not_found=False)
    anchor = c.env["fix.security.audit.anchor"].sudo().search([], limit=1)
    assert anchor.legacy_digest


# ================================================================ E7 group_ids everywhere
def test_a12f_e7_every_role_control_is_measurable(c):
    Sod = c.env["fix.sod.control"].sudo()
    controls = Sod.search([("active", "=", True), ("control_type", "=", "role")])
    assert not controls.filtered(lambda ct: not ct.measurable).mapped("code")
    unmeasurable = {row["control"] for row in Sod.fix_report_violations()["unmeasurable"]}
    assert not unmeasurable & set(controls.mapped("code"))


def test_a12f_e7_violation_report_sees_dual_holder(c):
    c.tgt.sudo().with_context(install_mode=True).write(
        {"group_ids": [(4, g.id) for g in rg(c, "R-19") | rg(c, "R-26")]}
    )
    control = c.env["fix.sod.control"].sudo().search([("code", "=", "SOD-01")])
    run = c.env["fix.sod.test"].with_user(c.p).create({"control_id": control.id})
    run.with_user(c.p).action_run()
    assert run.result == "fail"
    rows = c.env["fix.sod.control"].sudo().fix_report_violations()["violations"]
    assert [r for r in rows if r["control"] == "SOD-01" and r["user_id"] == c.tgt.id]


def test_a12f_e7_group_door_blocks_a_role_conflict(c):
    granted(c, "R-19", c.tgt)
    group = c.env.ref("cd_service_order.group_so_commercial_approver")
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        group.with_user(c.ua).write({"user_ids": [(4, c.tgt.id)]})
    assert group not in c.tgt.sudo().group_ids


def test_a12f_e7_warn_control_needs_a_waiver_at_grant(c):
    Sod = c.env["fix.sod.control"].sudo()
    warned = Sod.search([("code", "in", ("SOD-17", "SOD-38", "SOD-47"))])
    assert warned
    for control in warned:
        user = _user(c.env, "a12f_warn_%d" % control.id)
        granted(c, control.role_a_id.code, user)
        r = areq(c, c.p, control.role_b_id.code, user)
        r.with_user(c.appr).action_approve()
        with pytest.raises(ValidationError, match="waiver"), c.env.cr.savepoint():
            r.with_user(c.appr).action_grant()


def test_a12f_e7_unrelated_grant_passes_a_conflict_already_held(c):
    c.tgt.sudo().with_context(install_mode=True).write(
        {"group_ids": [(4, g.id) for g in rg(c, "R-19") | rg(c, "R-26")]}
    )
    r = areq(c, c.p, "R-44", c.tgt)
    r.with_user(c.appr).action_approve()
    r.with_user(c.appr).action_grant()
    assert r.state == "granted"


# ================================================================ E8 exceptions honoured
def test_a12f_e8_approved_exception_lets_a_block_control_through(c):
    a, b = c.role("R-19"), c.role("R-26")
    controls = (
        c.env["fix.sod.control"]
        .sudo()
        .search(
            [
                "|",
                "&",
                ("role_a_id", "=", a.id),
                ("role_b_id", "=", b.id),
                "&",
                ("role_a_id", "=", b.id),
                ("role_b_id", "=", a.id),
            ]
        )
    )
    assert controls
    granted(c, "R-19", c.tgt)
    r = areq(c, c.p, "R-26", c.tgt)
    r.with_user(c.appr).action_approve()
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        r.with_user(c.appr).action_grant()
    for control in controls:
        exception = (
            c.env["fix.sod.mitigation"]
            .with_user(c.p)
            .create(
                {
                    "control_id": control.id,
                    "user_id": c.tgt.id,
                    "mitigating_control": "weekly independent review",
                    "reason": "cover",
                    "valid_from": c.today,
                    "valid_until": c.today + timedelta(days=30),
                }
            )
        )
        exception.with_user(c.sodx).action_approve()
    r.with_user(c.appr).action_grant()
    assert r.state == "granted"
    assert all(has(c.tgt, g) for g in rg(c, "R-26"))


def test_a12f_e8_expired_or_revoked_exception_does_not_count(c):
    control = c.env["fix.sod.control"].sudo().search([("code", "=", "SOD-01")])
    exception = (
        c.env["fix.sod.mitigation"]
        .with_user(c.p)
        .create(
            {
                "control_id": control.id,
                "user_id": c.tgt.id,
                "mitigating_control": "weekly independent review",
                "reason": "cover",
                "valid_from": c.today,
                "valid_until": c.today + timedelta(days=30),
            }
        )
    )
    exception.with_user(c.sodx).action_approve()
    exception.with_user(c.sodx).action_revoke()
    assert not c.env["fix.sod.control"]._fix_excepted(control, c.tgt)


# ================================================================ E9 one expiry clock
def test_a12f_e9_expiry_clock_covers_any_time_boxed_grant_with_audit(c):
    r = areq(c, c.p, "R-30", c.tgt, valid_until=c.today + timedelta(days=1))
    r.with_user(c.appr).action_approve()
    r.with_user(c.appr).action_grant()
    r.sudo().write({"valid_until": c.today - timedelta(days=1)})
    assert c.env["fix.access.request"].sudo().cron_expire_elevations() >= 1
    assert r.state == "revoked" and not has(c.tgt, "hr.group_hr_manager")
    assert audit_count(c, "elevation_expiry", "fix.access.request,%d" % r.id) == 1


def test_a12f_e9_expiry_of_an_elevation_keeps_a_later_permanent_grant(c):
    r = areq(c, c.p, "R-30", c.tgt, request_type="elevate", valid_until=c.today + timedelta(days=1))
    r.with_user(c.appr).action_approve()
    r.with_user(c.appr).action_grant()
    granted(c, "R-30", c.tgt)
    r.sudo().write({"valid_until": c.today - timedelta(days=1)})
    c.env["fix.access.request"].sudo().cron_expire_elevations()
    assert r.state == "revoked" and has(c.tgt, "hr.group_hr_manager")


def test_a12f_e9_only_one_job_ships(c):
    assert c.env.ref("cd_rbac_ext.ir_cron_access_elevation_expiry")
    jobs = c.env["ir.cron"].sudo().search([("code", "like", "cron_revoke_expired")])
    assert not jobs
    assert not hasattr(c.env["fix.access.request"], "cron_revoke_expired")


# ================================================================ E10 break-glass
def test_a12f_e10_walk_through_the_screen(c, p03):
    res = p03.write(
        c.p,
        model="fix.privileged.session",
        values={"access_kind": "db_console", "reason": "fix a lock", "ticket_ref": "CHG-1"},
    )
    assert res.get("id"), res
    s = c.env["fix.privileged.session"].sudo().browse(res["id"])
    assert s.state == "requested" and s.user_id == c.p and s.name.startswith("PS/")
    # nobody opens it, or approves it for himself
    assert not p03.action(c.p, model=s._name, ids=[s.id], method="action_open")["success"]
    assert not p03.action(c.p, model=s._name, ids=[s.id], method="action_approve")["success"]
    assert not p03.action(c.p2, model=s._name, ids=[s.id], method="action_approve")["success"]
    ok = p03.action(c.appr, model=s._name, ids=[s.id], method="action_approve")
    assert ok["success"], ok
    assert s.state == "approved" and s.approver_id == c.appr
    assert s.expires_at <= fields.Datetime.now() + timedelta(hours=4, minutes=1)
    before = (
        c.env["mail.message"].sudo().search_count([("model", "=", s._name), ("res_id", "=", s.id)])
    )
    assert not p03.action(c.p2, model=s._name, ids=[s.id], method="action_open")["success"]
    ok = p03.action(c.p, model=s._name, ids=[s.id], method="action_open")
    assert ok["success"], ok
    assert s.state == "open"
    assert audit_count(c, "session_open", "fix.privileged.session,%d" % s.id) == 1
    assert (
        c.env["mail.message"].sudo().search_count([("model", "=", s._name), ("res_id", "=", s.id)])
        > before
    )
    ok = p03.action(c.p, model=s._name, ids=[s.id], method="action_close")
    assert ok["success"], ok
    assert s.state == "closed" and s.ended_at


def test_a12f_e10_max_duration_from_parameter_default_four_hours(c):
    Session = c.env["fix.privileged.session"].with_user(c.p)
    with pytest.raises(ValidationError):
        Session.create({"reason": "x", "duration_hours": 5})
    c.env["ir.config_parameter"].sudo().set_param("fix_rbac_ext.break_glass_max_hours", "8")
    s = Session.create({"reason": "x", "duration_hours": 5})
    s.with_user(c.appr).action_approve()
    assert s.expires_at <= fields.Datetime.now() + timedelta(hours=5, minutes=1)


def test_a12f_e10_reject_needs_a_reason_and_approval_lapses(c, p03):
    s = c.env["fix.privileged.session"].with_user(c.p).create({"reason": "x"})
    bad = p03.action(c.appr, model=s._name, ids=[s.id], method="action_reject")
    assert not bad["success"]
    ok = p03.action(
        c.appr, model=s._name, ids=[s.id], method="action_reject", kwargs={"reason": "no ticket"}
    )
    assert ok["success"] and s.state == "rejected" and s.decision_note == "no ticket"
    s2 = c.env["fix.privileged.session"].with_user(c.p).create({"reason": "x"})
    s2.with_user(c.appr).action_approve()
    s2.sudo().write({"expires_at": fields.Datetime.now() - timedelta(minutes=1)})
    with pytest.raises(UserError):
        s2.with_user(c.p).action_open()
    c.env["fix.privileged.session"].sudo().cron_close_stale_sessions()
    assert s2.state == "expired"


def test_a12f_e10_open_session_closed_at_its_expiry(c):
    s = c.env["fix.privileged.session"].with_user(c.p).create({"reason": "x", "duration_hours": 1})
    s.with_user(c.appr).action_approve()
    s.with_user(c.p).action_open()
    s.sudo().write({"expires_at": fields.Datetime.now() - timedelta(minutes=1)})
    c.env["fix.privileged.session"].sudo().cron_close_stale_sessions()
    assert s.state == "closed"
    assert audit_count(c, "session_timeout", "fix.privileged.session,%d" % s.id) == 1


# ================================================================ E11 session stamps
def test_a12f_e11_session_stamps_guarded(c):
    s = (
        c.env["fix.privileged.session"]
        .with_user(c.p)
        .create({"reason": "x", "user_id": c.admin.id, "started_at": "2020-01-01 00:00:00"})
    )
    assert s.user_id == c.p and s.started_at.year != 2020
    for vals in (
        {"started_at": str(fields.Datetime.now() - timedelta(minutes=1))},
        {"user_id": c.admin.id},
        {"expires_at": str(fields.Datetime.now() + timedelta(days=9))},
        {"approver_id": c.admin.id},
    ):
        with pytest.raises(REFUSED):
            s.with_user(c.p).write(vals)


# ================================================================ E12 JML two-person
def test_a12f_e12_applier_is_neither_beneficiary_nor_filer(c):
    emp = _emp(c.env, c.appr, "a12f appr emp")
    own = (
        c.env["fix.jml.event"]
        .with_user(c.hr)
        .create({"event_type": "joiner", "employee_id": emp.id, "role_id": c.role("R-30").id})
    )
    with pytest.raises(UserError):
        own.with_user(c.appr).action_apply()
    filed = (
        c.env["fix.jml.event"]
        .with_user(c.appr)
        .create({"event_type": "joiner", "employee_id": c.e_tgt.id, "role_id": c.role("R-08").id})
    )
    with pytest.raises(UserError):
        filed.with_user(c.appr).action_apply()
    assert not has(c.appr, "hr.group_hr_manager") and not has(
        c.tgt, "cd_rbac_ext.group_ws_front_desk"
    )


def test_a12f_e12_leaver_for_a_cannot_name_b(c):
    ev = (
        c.env["fix.jml.event"]
        .with_user(c.p)
        .create({"event_type": "leaver", "employee_id": c.e_p.id, "user_id": c.mgr.id})
    )
    assert ev.user_id == c.p
    nologin = _emp(c.env, False, "a12f nologin")
    ev2 = (
        c.env["fix.jml.event"]
        .with_user(c.p)
        .create({"event_type": "leaver", "employee_id": nologin.id, "user_id": c.mgr.id})
    )
    assert not ev2.user_id
    with pytest.raises(REFUSED):
        ev.with_user(c.p).write({"user_id": c.mgr.id})


def test_a12f_e12_walk_filed_by_hr_applied_by_approver(c, p03):
    res = p03.write(
        c.hr,
        model="fix.jml.event",
        values={
            "event_type": "joiner",
            "employee_id": c.e_tgt.id,
            "role_id": c.role("R-08").id,
            "effective_on": str(c.today),
        },
    )
    assert res.get("id"), res
    ok = p03.action(c.appr, model="fix.jml.event", ids=[res["id"]], method="action_apply")
    assert ok["success"], ok
    assert has(c.tgt, "cd_rbac_ext.group_ws_front_desk")
    res = p03.write(
        c.hr,
        model="fix.jml.event",
        values={
            "event_type": "leaver",
            "employee_id": c.e_tgt.id,
            "effective_on": str(c.today),
        },
    )
    ok = p03.action(c.appr, model="fix.jml.event", ids=[res["id"]], method="action_apply")
    assert ok["success"], ok
    tgt = c.tgt.sudo().with_context(active_test=False)
    tgt.invalidate_recordset()
    assert not tgt.active and not tgt.group_ids


# ================================================================ E13 buttons with arguments
def test_a12f_e13_rotate_and_severity_as_pressed(c, p03):
    js = JS.read_text(encoding="utf-8")
    assert re.search(r"m: 'action_rotate'.*kwarg: 'new_vault_ref'", js)
    assert re.search(r"m: 'action_set_severity'.*kwarg: 'severity'", js)
    key = (
        c.env["fix.encryption.key"]
        .sudo()
        .create(
            {
                "code": "A12F-B1",
                "name": "k",
                "vault_ref": "vault://kv/fix/a12f-b1",
                "custodian_id": c.cust.id,
            }
        )
    )
    ok = p03.action(
        c.cust,
        model="fix.encryption.key",
        ids=[key.id],
        method="action_rotate",
        kwargs={"new_vault_ref": "vault://kv/fix/a12f-b1b"},
    )
    assert ok["success"], ok
    inc = incident(c)
    ok = p03.action(
        c.off1,
        model="fix.security.incident",
        ids=[inc.id],
        method="action_set_severity",
        kwargs={"severity": "high"},
    )
    assert ok["success"], ok
    assert inc.severity_pending == "high"


# ================================================================ E14 forms can create
def test_a12f_e14_certification_line_from_form(c, p03):
    c.tgt.sudo().write({"group_ids": [(4, c.env.ref("hr.group_hr_manager").id)]})
    for who in (c.ua, c.sys, c.appr):
        form = p03.form(
            who,
            model="fix.access.certification",
            fields=[{"name": n} for n in ("user_id", "role_id", "reviewer_id")],
        )
        assert not [f["name"] for f in form["fields"] if f["readonly"]]
    res = p03.write(
        c.appr,
        model="fix.access.certification",
        values={
            "period": "2026-Q4",
            "user_id": c.tgt.id,
            "role_id": c.role("R-30").id,
            "due_on": str(c.today + timedelta(days=14)),
        },
    )
    assert res.get("id"), res
    # empty reviewer: the user's manager
    assert c.env["fix.access.certification"].sudo().browse(res["id"]).reviewer_id == c.mgr


def test_a12f_e14_key_from_form_and_jml_user_input(c, p03):
    res = p03.write(
        c.cust,
        model="fix.encryption.key",
        values={
            "code": "A12F-F1",
            "name": "form key",
            "purpose": "backup",
            "algorithm": "aes_256_gcm",
            "vault_ref": "vault://kv/fix/a12f-form",
            "rotations_per_year": 1,
            "custodian_id": c.cust.id,
        },
    )
    assert res.get("id"), res
    nologin = _emp(c.env, False, "a12f nouser")
    res = p03.write(
        c.hr,
        model="fix.jml.event",
        values={
            "event_type": "joiner",
            "employee_id": nologin.id,
            "user_id": c.tgt.id,
            "role_id": c.role("R-08").id,
            "effective_on": str(c.today),
        },
    )
    assert res.get("id"), res
    assert c.env["fix.jml.event"].sudo().browse(res["id"]).user_id == c.tgt


# ================================================================ E15 severity two-person
def test_a12f_e15_reporter_registers_a_critical(c, p03):
    res = p03.write(
        c.p,
        model="fix.security.incident",
        values={
            "title": "laptop stolen",
            "category": "unauthorised_access",
            "severity": "critical",
        },
    )
    assert res.get("id"), res
    inc = c.env["fix.security.incident"].sudo().browse(res["id"])
    assert (
        inc.severity == "critical" and inc.severity_set_by_id == c.p and inc.detected_by_id == c.p
    )


def test_a12f_e15_named_witness_does_nothing_and_second_officer_confirms(c):
    inc = incident(c)
    with pytest.raises(REFUSED):
        inc.with_user(c.p).action_set_severity("low", confirmed_by_id=c.admin.id)
    inc.with_user(c.off1).action_set_severity("low", confirmed_by_id=c.admin.id)
    assert inc.severity == "critical" and inc.severity_pending == "low"
    assert not inc.severity_confirmed_by_id
    with pytest.raises(UserError):
        inc.with_user(c.off1).action_confirm_severity()
    inc.with_user(c.off2).action_confirm_severity()
    assert inc.severity == "low" and not inc.severity_pending
    assert inc.severity_set_by_id == c.off1 and inc.severity_confirmed_by_id == c.off2


def test_a12f_e15_severity_not_typed_after_filing_and_change_can_be_refused(c):
    inc = incident(c)
    with pytest.raises(UserError):
        inc.with_user(c.off1).write({"severity": "low"})
    inc.with_user(c.off1).action_set_severity("low")
    inc.with_user(c.off2).action_reject_severity()
    assert inc.severity == "critical" and not inc.severity_pending


# ================================================================ E16 incident handling
def test_a12f_e16_plain_user_cannot_read_or_touch(c, p03):
    inc = incident(c, description="payroll export leaked", breach_assessment="4,000 data subjects")
    res = p03.records(
        c.p,
        model="fix.security.incident",
        cols=["title", "description", "breach_assessment"],
        domain=[("id", "=", inc.id)],
    )
    assert not res.get("rows")
    res = p03.form(
        c.p, model="fix.security.incident", record_id=inc.id, fields=[{"name": "breach_assessment"}]
    )
    assert res.get("error")
    res = p03.write(
        c.p, model="fix.security.incident", record_id=inc.id, values={"category": "policy_breach"}
    )
    assert res.get("error")
    assert not p03.action(c.p, model=inc._name, ids=[inc.id], method="action_contain")["success"]
    inc.invalidate_recordset()
    assert inc.category == "data_leak"


def test_a12f_e16_reporter_reads_own_report_officer_reads_all(c, p03):
    res = p03.write(
        c.p, model="fix.security.incident", values={"title": "mine", "category": "phishing"}
    )
    assert p03.records(
        c.p, model="fix.security.incident", cols=["title"], domain=[("id", "=", res["id"])]
    )["rows"]
    assert not p03.records(
        c.p2, model="fix.security.incident", cols=["title"], domain=[("id", "=", res["id"])]
    )["rows"]
    assert p03.records(
        c.off1, model="fix.security.incident", cols=["title"], domain=[("id", "=", res["id"])]
    )["rows"]


def test_a12f_e16_leak_cannot_be_recategorised_and_needs_assessment(c, p03):
    inc = incident(c, containment=FILL, root_cause=FILL)
    assert p03.action(c.off1, model=inc._name, ids=[inc.id], method="action_contain")["success"]
    res = p03.write(c.off1, model=inc._name, record_id=inc.id, values={"category": "policy_breach"})
    assert res.get("error")
    with pytest.raises(UserError):
        inc.with_user(c.off1).write({"category": "policy_breach"})
    assert not p03.action(c.off1, model=inc._name, ids=[inc.id], method="action_close")["success"]
    res = p03.write(c.off1, model=inc._name, record_id=inc.id, values={"breach_assessment": FILL})
    assert not res.get("error"), res
    ok = p03.action(c.off1, model=inc._name, ids=[inc.id], method="action_close")
    assert ok["success"], ok
    assert inc.state == "closed" and inc.resolved_on


def test_a12f_e16_closed_record_frozen(c, p03):
    inc = incident(c, containment=FILL, root_cause=FILL, breach_assessment=FILL)
    inc.with_user(c.off1).action_contain()
    inc.with_user(c.off1).action_close()
    res = p03.write(
        c.off2, model=inc._name, record_id=inc.id, values={"root_cause": "rewritten after closure"}
    )
    assert res.get("error")
    with pytest.raises(UserError):
        inc.with_user(c.off2).write({"root_cause": "rewritten after closure"})
    with pytest.raises(UserError):
        inc.with_user(c.off2).action_set_severity("low")
    assert audit_count(c, "incident", "fix.security.incident,%d" % inc.id) == 2  # contain + close


# ================================================================ E17 campaign
def test_a12f_e17_campaign_walk_through_the_screen(c, p03):
    granted(c, "R-30", c.tgt)
    # a user whose only manager is himself falls back to an approver, never himself
    loner = _user(c.env, "a12f_loner")
    _emp(c.env, loner, "a12f loner")
    granted(c, "R-08", loner)
    assert not p03.write(
        c.p, model="fix.access.certification.campaign", values={"period": "2026-Q9"}
    ).get("id")
    res = p03.write(
        c.appr,
        model="fix.access.certification.campaign",
        values={"period": "2026-Q9", "due_on": str(c.today + timedelta(days=14))},
    )
    assert res.get("id"), res
    ok = p03.action(
        c.p, model="fix.access.certification.campaign", ids=[res["id"]], method="action_generate"
    )
    assert not ok["success"]
    ok = p03.action(
        c.appr, model="fix.access.certification.campaign", ids=[res["id"]], method="action_generate"
    )
    assert ok["success"], ok
    campaign = c.env["fix.access.certification.campaign"].sudo().browse(res["id"])
    assert campaign.state == "generated"
    Cert = c.env["fix.access.certification"].sudo()
    line = Cert.search([("campaign_id", "=", campaign.id), ("user_id", "=", c.tgt.id)])
    assert line.role_id == c.role("R-30") and line.reviewer_id == c.mgr
    assert line.activity_ids.user_id == c.mgr
    fallback = Cert.search([("campaign_id", "=", campaign.id), ("user_id", "=", loner.id)])
    assert fallback.reviewer_id and fallback.reviewer_id != loner
    assert fallback.reviewer_id.has_group(APPROVER)
    assert not Cert.search([("campaign_id", "=", campaign.id)]).filtered(
        lambda r: r.reviewer_id == r.user_id
    )
    assert (
        audit_count(
            c, "certification_campaign", "fix.access.certification.campaign,%d" % campaign.id
        )
        == 1
    )
    # locked, generated once, and the manager decides through the screen
    assert p03.write(
        c.appr, model=line._name, record_id=line.id, values={"reviewer_id": c.appr.id}
    ).get("error")
    assert not p03.action(
        c.appr, model=campaign._name, ids=[campaign.id], method="action_generate"
    )["success"]
    ok = p03.action(c.mgr, model=line._name, ids=[line.id], method="action_revoke")
    assert ok["success"], ok
    assert not has(c.tgt, "hr.group_hr_manager") and not line.activity_ids


def test_a12f_e17_generator_is_not_public(c):
    with pytest.raises(REFUSED):
        c.env["fix.access.certification"].with_user(c.ua)._fix_generate_campaign_lines(
            c.env["fix.access.certification.campaign"].sudo().create({"period": "2026-Q8"})
        )


# ================================================================ E18 log_event
def test_a12f_e18_log_event_not_reachable_over_rpc(c):
    before = audit_count(c)
    with pytest.raises(AccessError):
        call_kw(
            c.env["fix.security.audit"].with_user(c.p), "log_event", ["grant", "x", "forged"], {}
        )
    assert audit_count(c) == before
    # the cross-builder contract still works from server code, with the true actor
    row = c.env["fix.security.audit"].with_user(c.p).log_event("probe", "x", "d")
    assert row.sudo().actor_id == c.p


# ================================================================ E19 keys
def _key(c, **kw):
    v = {
        "code": "A12F-K1",
        "name": "probe key",
        "vault_ref": "vault://kv/fix/a12f-probe",
        "custodian_id": c.cust.id,
        "rotations_per_year": 2,
    }
    v.update(kw)
    return c.env["fix.encryption.key"].sudo().create(v)


def test_a12f_e19_successor_carries_the_clock(c):
    key = _key(c)
    key.with_user(c.cust).action_rotate(new_vault_ref="vault://kv/fix/a12f-probe-2")
    successor = key.successor_id
    assert successor.state == "active" and successor.last_rotated_on and successor.next_rotation_on
    assert key.state == "retired" and not key.next_rotation_on


def test_a12f_e19_vault_ref_only_through_rotation(c, p03):
    key = _key(c)
    with pytest.raises(UserError):
        key.with_user(c.cust).write({"vault_ref": "vault://kv/attacker/x"})
    assert p03.write(
        c.cust, model=key._name, record_id=key.id, values={"vault_ref": "vault://x"}
    ).get("error")
    assert key.vault_ref == "vault://kv/fix/a12f-probe"


def test_a12f_e19_ref_hidden_from_plain_and_absent_from_audit(c, p03):
    key = _key(c)
    res = p03.records(
        c.p, model=key._name, cols=["code", "vault_ref"], domain=[("id", "=", key.id)]
    )
    assert res["rows"] and "vault_ref" not in res["rows"][0]
    res = p03.records(
        c.cust, model=key._name, cols=["code", "vault_ref"], domain=[("id", "=", key.id)]
    )
    assert res["rows"][0]["vault_ref"]
    with pytest.raises(AccessError):
        key.with_user(c.p).read(["vault_ref"])
    p03.write(c.p, model=key._name, record_id=key.id, values={"vault_ref": "vault://x"})
    assert key.vault_ref == "vault://kv/fix/a12f-probe"
    key.with_user(c.cust).action_rotate(new_vault_ref="vault://kv/fix/a12f-probe-3")
    row = (
        c.env["fix.security.audit"]
        .sudo()
        .search(
            [("event", "=", "key_rotation"), ("object_ref", "=", "fix.encryption.key,%d" % key.id)]
        )
    )
    assert "vault://" not in row.detail


def test_a12f_e19_custodian_change_audited(c):
    key = _key(c)
    key.with_user(c.sys).write({"custodian_id": c.sys.id})
    assert audit_count(c, "key_custodian_change", "fix.encryption.key,%d" % key.id) == 1


# ================================================================ E20 audit trail
def _verify(c):
    return c.env["fix.security.audit"].sudo().search([], limit=1).action_verify_chain()


def _refused_summary(c):
    c.env.invalidate_all()
    with pytest.raises(UserError) as info:
        _verify(c)
    return str(info.value)


def _seed_rows(c, tag):
    audit = c.env["fix.security.audit"].sudo()
    for i in range(3):
        audit.log_event("grant", "%s-%d" % (tag, i), "d%d" % i)


def test_a12f_e20_clean_chain_is_a_result_not_an_error(c, p03):
    _seed_rows(c, "clean")
    row = c.env["fix.security.audit"].sudo().search([], limit=1)
    res = p03.action(c.p, model="fix.security.audit", ids=[row.id], method="action_verify_chain")
    assert res["success"], res
    assert "0 discontinuity" in res["result"]["note"] and "legacy-format" in res["result"]["note"]


def test_a12f_e20_tail_deletion_detected(c):
    _seed_rows(c, "tail")
    c.env.cr.execute("DELETE FROM fix_security_audit WHERE object_ref = 'tail-2'")
    assert "the tail" in _refused_summary(c)


@pytest.mark.parametrize(
    "sql",
    [
        "UPDATE fix_security_audit SET detail = 'tampered' WHERE object_ref = 'edit-1'",
        "UPDATE fix_security_audit SET ip_address = '203.0.113.9' WHERE object_ref = 'edit-1'",
    ],
)
def test_a12f_e20_payload_and_ip_edits_detected(c, sql):
    _seed_rows(c, "edit")
    c.env.cr.execute(sql)
    assert "sequence" in _refused_summary(c)


def test_a12f_e20_legacy_rows_reported_apart_then_sealed(c):
    """E20's decision: history is not rewritten. A row in an old format is labelled,
    sealed and reported as legacy; the same row edited afterwards is tampering."""
    audit = c.env["fix.security.audit"].sudo()
    _seed_rows(c, "old")
    # three rows as the seed wrote them: a hash nothing can recompute, links intact
    first = audit.search([("object_ref", "=", "old-0")])
    c.env.cr.execute(
        "UPDATE fix_security_audit SET entry_hash = %s WHERE id = %s", ["0" * 64, first.id]
    )
    c.env.cr.execute(
        "UPDATE fix_security_audit SET prev_hash = %s WHERE object_ref = 'old-1'", ["0" * 64]
    )
    anchor = audit.env["fix.security.audit.anchor"]._fix_get()
    anchor.write({"legacy_through": 0, "legacy_digest": False})
    c.env.invalidate_all()
    assert "discontinuity" in _refused_summary(c)  # before the anchor: reads as tampering

    audit._fix_anchor_chain()
    c.env.invalidate_all()
    note = _verify(c)["note"]
    assert "0 discontinuity" in note
    assert int(re.search(r"(\d+) legacy-format", note).group(1)) >= 3
    assert first.hash_version == 0
    assert (
        audit.search([("event", "=", "audit.chain_anchor")], order="id desc", limit=1).hash_version
        == 2
    )
    audit.log_event("grant", "after-anchor", "d")  # the chain carries on in the current format
    assert "0 discontinuity" in _verify(c)["note"]

    c.env.cr.execute(
        "UPDATE fix_security_audit SET detail = 'rewritten' WHERE object_ref = 'old-0'"
    )
    assert "seal" in _refused_summary(c)


@pytest.mark.parametrize(
    "act",
    ["approve", "reject", "joiner", "mover", "contain", "open"],
)
def test_a12f_e20_each_action_writes_a_row(c, act):
    if act in ("approve", "reject"):
        r = areq(c, c.p, "R-08", c.tgt)
        before = audit_count(c, ref="fix.access.request,%d" % r.id)
        if act == "approve":
            r.with_user(c.appr).action_approve()
        else:
            r.with_user(c.appr).action_reject(reason="not needed")
        assert audit_count(c, ref="fix.access.request,%d" % r.id) == before + 1
    elif act in ("joiner", "mover"):
        ev = (
            c.env["fix.jml.event"]
            .with_user(c.hr)
            .create({"event_type": act, "employee_id": c.e_tgt.id, "role_id": c.role("R-08").id})
        )
        ev.with_user(c.appr).action_apply()
        assert audit_count(c, act, "fix.jml.event,%d" % ev.id) == 1
    elif act == "contain":
        inc = incident(c, containment=FILL)
        inc.with_user(c.off1).action_contain()
        assert audit_count(c, "incident", "fix.security.incident,%d" % inc.id) == 1
    else:
        s = c.env["fix.privileged.session"].with_user(c.p).create({"reason": "x"})
        s.with_user(c.appr).action_approve()
        s.with_user(c.p).action_open()
        assert audit_count(c, "session_open", "fix.privileged.session,%d" % s.id) == 1


# ================================================================ E21 SoD tests
def test_a12f_e21_run_stamps_itself_and_stays_on_its_control(c, p03):
    control = c.env["fix.sod.control"].sudo().search([("code", "=", "SOD-01")])
    res = p03.write(
        c.p,
        model="fix.sod.test",
        values={
            "control_id": control.id,
            "users_checked": 999,
            "tested_by_id": c.admin.id,
            "tested_on": "2020-01-01",
        },
    )
    assert res.get("id"), res
    run = c.env["fix.sod.test"].sudo().browse(res["id"])
    assert run.tested_by_id != c.admin and run.users_checked != 999 and run.tested_on.year != 2020
    ok = p03.action(c.p, model="fix.sod.test", ids=[run.id], method="action_run")
    assert ok["success"], ok
    assert run.tested_by_id == c.p and run.users_checked > 0
    other = c.env["fix.sod.control"].sudo().search([("code", "=", "SOD-02")])
    with pytest.raises(UserError):
        run.with_user(c.p).write({"control_id": other.id})
    with pytest.raises(REFUSED):
        run.with_user(c.p).write({"tested_on": str(c.today + timedelta(days=30))})
    with pytest.raises(UserError):
        run.with_user(c.p).action_run()


def test_a12f_e21_scheduled_measurement_ships_and_runs(c):
    job = c.env.ref("cd_rbac_ext.ir_cron_sod_tests_weekly")
    assert job.active and "cron_run_sod_tests" in job.code
    with pytest.raises(AccessError):
        c.env["fix.sod.test"].with_user(c.p).cron_run_sod_tests()
    ran = c.env["fix.sod.test"].sudo().cron_run_sod_tests()
    measurable = (
        c.env["fix.sod.control"].sudo().search([("active", "=", True)]).filtered("measurable")
    )
    assert ran == len(measurable)


# ================================================================ E22 frozen, bounded
def test_a12f_e22_decided_line_and_applied_event_frozen(c, p03):
    line = cert_line(c)
    line.with_user(c.mgr).action_certify()
    assert p03.write(c.appr, model=line._name, record_id=line.id, values={"period": "2020-Q1"}).get(
        "error"
    )
    with pytest.raises(UserError):
        line.with_user(c.appr).write({"note": "edited after decision"})
    ev = (
        c.env["fix.jml.event"]
        .with_user(c.hr)
        .create({"event_type": "joiner", "employee_id": c.e_tgt.id, "role_id": c.role("R-08").id})
    )
    ev.with_user(c.appr).action_apply()
    assert p03.write(c.hr, model=ev._name, record_id=ev.id, values={"event_type": "leaver"}).get(
        "error"
    )
    with pytest.raises(UserError):
        ev.with_user(c.hr).write({"effective_on": "2020-01-01"})
    assert ev.event_type == "joiner"


def test_a12f_e22_reviewed_user_cannot_move_the_deadline(c, p03):
    line = cert_line(c, due_on=str(c.today + timedelta(days=1)))
    res = p03.write(
        c.tgt,
        model=line._name,
        record_id=line.id,
        values={"due_on": str(c.today + timedelta(days=3650))},
    )
    assert res.get("error")
    line.invalidate_recordset()
    assert line.due_on == c.today + timedelta(days=1)


def test_a12f_e22_elevation_bounded_by_parameter_default_30(c):
    assert c.tgt and c.p  # created outside the savepoint below
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        areq(
            c, c.p, "R-30", c.tgt, request_type="elevate", valid_until=c.today + timedelta(days=31)
        )
    r = areq(
        c, c.p, "R-30", c.tgt, request_type="elevate", valid_until=c.today + timedelta(days=30)
    )
    assert r.valid_until
    c.env["ir.config_parameter"].sudo().set_param("fix_rbac_ext.elevation_max_days", "5")
    with pytest.raises(ValidationError):
        areq(c, c.p, "R-08", c.tgt, request_type="elevate", valid_until=c.today + timedelta(days=6))


# ================================================================ E23 who executes
def test_a12f_e23_grant_authority(c):
    r = areq(c, c.p2, "R-30", c.tgt)
    r.with_user(c.appr).action_approve()
    for user in (c.tgt, c.p2, c.p):
        with pytest.raises(UserError):
            r.with_user(user).action_grant()
    assert r.state == "approved"


def test_a12f_e23_approver_who_lost_authority(c):
    r = areq(c, c.p, "R-30", c.tgt)
    r.with_user(c.appr).action_approve()
    c.appr.sudo().write({"group_ids": [(3, c.env.ref(APPROVER).id)]})
    other = _user(c.env, "a12f_approver2", [APPROVER])
    with pytest.raises(UserError):
        r.with_user(other).action_grant()
    assert r.state == "approved"


# ================================================================ E24 lifecycle
def test_a12f_e24_mover_ends_the_old_role(c):
    granted(c, "R-08", c.tgt)
    ev = (
        c.env["fix.jml.event"]
        .with_user(c.hr)
        .create({"event_type": "mover", "employee_id": c.e_tgt.id, "role_id": c.role("R-30").id})
    )
    ev.with_user(c.appr).action_apply()
    assert has(c.tgt, "hr.group_hr_manager")
    assert not has(c.tgt, "cd_rbac_ext.group_ws_front_desk")
    assert c.env["fix.sod.control"].user_held_roles(c.tgt) == c.role("R-30")


def test_a12f_e24_mover_into_a_conflict_refused(c):
    granted(c, "R-19", c.tgt)
    ev = (
        c.env["fix.jml.event"]
        .with_user(c.hr)
        .create({"event_type": "mover", "employee_id": c.e_tgt.id, "role_id": c.role("R-26").id})
    )
    with pytest.raises(REFUSED):
        ev.with_user(c.appr).action_apply()


def test_a12f_e24_future_leaver_waits(c):
    ev = (
        c.env["fix.jml.event"]
        .with_user(c.hr)
        .create(
            {
                "event_type": "leaver",
                "employee_id": c.e_tgt.id,
                "effective_on": str(c.today + timedelta(days=30)),
            }
        )
    )
    with pytest.raises(UserError):
        ev.with_user(c.appr).action_apply()
    assert c.tgt.sudo().active


def test_a12f_e24_leaver_loses_api_keys_and_stays_out(c, p03):
    c.env["res.users.apikeys"].with_user(c.tgt).sudo()._generate(
        "rpc", "probe", fields.Datetime.now() + timedelta(days=1)
    )
    ev = (
        c.env["fix.jml.event"]
        .with_user(c.hr)
        .create({"event_type": "leaver", "employee_id": c.e_tgt.id})
    )
    ev.with_user(c.appr).action_apply()
    assert not c.env["res.users.apikeys"].sudo().search_count([("user_id", "=", c.tgt.id)])
    res = p03.write(c.ua, model="res.users", record_id=c.tgt.id, values={"active": True})
    assert res.get("error"), res
    tgt = c.tgt.sudo().with_context(active_test=False)
    tgt.invalidate_recordset()
    assert not tgt.active
    # and the sanctioned way back: a joiner event filed and applied by two people
    back = (
        c.env["fix.jml.event"]
        .with_user(c.hr)
        .create({"event_type": "joiner", "employee_id": c.e_tgt.id, "role_id": c.role("R-08").id})
    )
    back.with_user(c.appr).action_apply()
    tgt.invalidate_recordset()
    assert tgt.active and has(c.tgt, "cd_rbac_ext.group_ws_front_desk")


def test_a12f_e24_rejection_needs_a_reason(c, p03):
    r = areq(c, c.p, "R-30", c.tgt)
    assert not p03.action(c.appr, model=r._name, ids=[r.id], method="action_reject")["success"]
    ok = p03.action(
        c.appr, model=r._name, ids=[r.id], method="action_reject", kwargs={"reason": "not in post"}
    )
    assert ok["success"], ok
    assert r.state == "rejected" and r.decision_note == "not in post"
    assert re.search(
        r"m: 'action_reject', l: 'Reject', ask: 'Why is this request rejected\?', kwarg: 'reason'",
        JS.read_text(encoding="utf-8"),
    )


def test_a12f_e24_form_deactivation_is_audited(c, p03):
    res = p03.write(c.ua, model="res.users", record_id=c.tgt.id, values={"active": False})
    assert not res.get("error"), res
    assert audit_count(c, "user_active", "res.users,%d" % c.tgt.id) == 1


# ================================================================ E25 portal + posture
def _portal(c, login):
    return (
        c.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, [c.env.ref("base.group_portal").id])],
            }
        )
    )


def test_a12f_e25_workspace_groups_refused_on_portal_users(c):
    portal = _portal(c, "a12f_portal")
    assert portal.share
    group = c.env.ref("cd_rbac_ext.group_ws_administration")
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        portal.sudo().write({"group_ids": [(4, group.id)]})
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        group.sudo().write({"user_ids": [(4, portal.id)]})
    r = areq(c, c.p, "R-08", portal)
    r.with_user(c.appr).action_approve()
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        r.with_user(c.appr).action_grant()
    assert group not in portal.sudo().all_group_ids


def test_a12f_e25_colleague_posture_hidden(c, p03):
    cols = ["login", "fix_group_names", "fix_dofa_tier", "fix_role_codes"]
    rows = p03.records(c.p, model="res.users", cols=cols, domain=[("id", "=", c.ua.id)])["rows"]
    assert rows and not rows[0]["fix_group_names"] and not rows[0]["fix_dofa_tier"]
    rows = p03.records(c.p, model="res.users", cols=cols, domain=[("id", "=", c.p.id)])["rows"]
    assert rows[0]["fix_group_names"]
    rows = p03.records(c.appr, model="res.users", cols=cols, domain=[("id", "=", c.ua.id)])["rows"]
    assert rows[0]["fix_group_names"]
    from odoo.addons.cd_p03_portal.controllers.a12 import m29

    assert [r["login"] for r in m29.access_review(c.env(user=c.p.id))["rows"]] == [c.p.login]


# ================================================================ E26 the User form
def _user_form_fields():
    js = JS.read_text(encoding="utf-8")
    block = js[js.index("'M29-form-user': {") : js.index("'M29-form-jml': {")]
    return [{"name": n} for n in re.findall(r"name: '(\w+)'", block)]


def test_a12f_e26_user_form_opens_and_saves_for_admins(c, p03):
    spec = _user_form_fields()
    assert "barcode" not in [f["name"] for f in spec]
    for who in (c.sys, c.ua):
        got = p03.form(who, model="res.users", fields=spec, record_id=c.tgt.id)
        assert not got.get("error"), got
        res = p03.write(
            who,
            model="res.users",
            record_id=c.tgt.id,
            values={"phone": "01700000001", "name": "a12f renamed"},
        )
        assert not res.get("error"), res
    got = p03.form(c.p, model="res.users", fields=spec, record_id=c.p.id)
    assert not got.get("error"), got


def test_a12f_e26_group_ids_still_not_typed_on_the_form(c, p03):
    p03.write(
        c.ua,
        model="res.users",
        record_id=c.tgt.id,
        values={"group_ids": [[4, c.env.ref("base.group_system").id]]},
    )
    assert not has(c.tgt, "base.group_system")


# ================================================================ E27 small screen defects
def test_a12f_e27_every_form_back_link_exists(c):
    js = JS.read_text(encoding="utf-8")
    screens = set(re.findall(r"^\s*'(M29-[\w-]+)': \{", js, re.M))
    assert not {b for b in re.findall(r"back: '([\w-]+)'", js) if b not in screens}
    block = js[js.index("'M29-form-session': {") :]
    assert re.search(r"back: '([\w-]+)'", block).group(1) == "M29-privileged"


def test_a12f_e27_tier_form_saves_for_system_admin(c, p03):
    tier = c.env["fix.isolation.tier"].sudo().search([("code", "=", "T2")])
    res = p03.write(
        c.sys, model=tier._name, record_id=tier.id, values={"description": "Branch scoped."}
    )
    assert not res.get("error"), res


def test_a12f_e27_model_and_field_by_technical_name(c, p03):
    res = p03.write(
        c.sys,
        model="fix.field.rule",
        values={
            "fix_model_name": "fix.role",
            "fix_field_name": "description",
            "permission": "hidden",
        },
    )
    assert res.get("id"), res
    rule = c.env["fix.field.rule"].sudo().browse(res["id"])
    assert rule.model_id.model == "fix.role" and rule.field_id.name == "description"
    bad = p03.write(
        c.sys, model="fix.field.rule", values={"fix_model_name": "no.such", "permission": "hidden"}
    )
    assert bad.get("error")
    res = p03.write(
        c.sys,
        model="ir.model.access",
        values={"name": "a12f row", "fix_model_name": "fix.role", "perm_read": True},
    )
    assert res.get("id"), res
    assert c.env["ir.model.access"].sudo().browse(res["id"]).model_id.model == "fix.role"
    res = p03.write(
        c.sys,
        model="ir.rule",
        values={"name": "a12f rule", "fix_model_name": "fix.role", "domain_force": "[(1, '=', 1)]"},
    )
    assert res.get("id"), res


def test_a12f_e27_no_duplicate_open_request(c):
    areq(c, c.p, "R-08", c.tgt)
    with pytest.raises(ValidationError):
        areq(c, c.p2, "R-08", c.tgt)


def test_a12f_e27_session_named_from_a_sequence(c):
    s = c.env["fix.privileged.session"].with_user(c.p).create({"reason": "x"})
    assert re.match(r"PS/\d{4}/\d+", s.name)


# ================================================================ E28 field rules and masking
def _rule(c, model, field, permission, roles=None):
    fld = c.env["ir.model.fields"].sudo()._get(model, field)
    return (
        c.env["fix.field.rule"]
        .sudo()
        .create(
            {
                "model_id": fld.model_id.id,
                "field_id": fld.id,
                "permission": permission,
                "role_ids": [(6, 0, roles.ids)] if roles else [],
            }
        )
    )


def test_a12f_e28_hidden_rule_on_list_and_form_for_a_plain_user(c, p03):
    role = c.role("R-30")
    role.sudo().write({"description": "secret text"})
    _rule(c, "fix.role", "description", "hidden")
    rows = p03.records(
        c.p, model="fix.role", cols=["code", "description"], domain=[("id", "=", role.id)]
    )["rows"]
    assert rows and "description" not in rows[0]
    form = p03.form(
        c.p, model="fix.role", fields=[{"name": "code"}, {"name": "description"}], record_id=role.id
    )
    assert "description" not in [f["name"] for f in form["fields"]]
    assert "description" not in form["record"]
    # cleared: a system admin and a clearance holder
    cleared = _user(c.env, "a12f_cleared", [CLEARANCE])
    for who in (c.sys, cleared):
        rows = p03.records(
            who, model="fix.role", cols=["code", "description"], domain=[("id", "=", role.id)]
        )["rows"]
        assert rows[0]["description"] == "secret text"


def test_a12f_e28_masked_rule_and_write_back_cannot_overwrite(c, p03):
    role = c.role("R-30")
    role.sudo().write({"description": "secret text"})
    _rule(c, "fix.role", "description", "masked")
    rows = p03.records(c.p, model="fix.role", cols=["description"], domain=[("id", "=", role.id)])[
        "rows"
    ]
    assert rows[0]["description"] == "***"
    form = p03.form(c.p, model="fix.role", fields=[{"name": "description"}], record_id=role.id)
    entry = next(f for f in form["fields"] if f["name"] == "description")
    assert entry["readonly"] and form["record"]["description"] == "***"
    # someone who may write the model but is not cleared posts the form back
    editor = _user(c.env, "a12f_editor")
    c.env["ir.model.access"].sudo().create(
        {
            "name": "a12f role editor",
            "model_id": c.env["ir.model"]._get("fix.role").id,
            "group_id": c.env.ref("base.group_user").id,
            "perm_read": True,
            "perm_write": True,
        }
    )
    res = p03.write(
        editor, model="fix.role", record_id=role.id, values={"description": "***", "name_bn": "x"}
    )
    assert not res.get("error"), res
    role.invalidate_recordset()
    assert role.description == "secret text"


def test_a12f_e28_rule_by_role_and_explicit_clearance_by_role(c, p03):
    role = c.role("R-30")
    role.sudo().write({"description": "secret text"})
    _rule(c, "fix.role", "description", "masked", roles=c.role("R-08"))
    rows = p03.records(c.p, model="fix.role", cols=["description"], domain=[("id", "=", role.id)])[
        "rows"
    ]
    assert rows[0]["description"] == "secret text"  # the rule names R-08, and he does not hold it
    granted(c, "R-08", c.p)
    rows = p03.records(c.p, model="fix.role", cols=["description"], domain=[("id", "=", role.id)])[
        "rows"
    ]
    assert rows[0]["description"] == "***"
    _rule(c, "fix.role", "description", "read", roles=c.role("R-08"))
    rows = p03.records(c.p, model="fix.role", cols=["description"], domain=[("id", "=", role.id)])[
        "rows"
    ]
    assert rows[0]["description"] == "secret text"


@pytest.mark.parametrize(
    "rule,expected",
    [("last4", "***text"), ("full", "***"), ("none", "secret text")],
)
def test_a12f_e28_classification_masks_on_the_read_path(c, p03, rule, expected):
    role = c.role("R-30")
    role.sudo().write({"description": "secret text"})
    c.env["fix.sensitive.field"].sudo().create(
        {
            "name": "a12f class",
            "model_name": "fix.role",
            "field_name": "description",
            "sensitivity": "s3",
            "data_class": "pii",
            "masking_rule": rule,
        }
    )
    rows = p03.records(c.p, model="fix.role", cols=["description"], domain=[("id", "=", role.id)])[
        "rows"
    ]
    assert rows[0]["description"] == expected


def test_a12f_e28_hash_masking(c, p03):
    role = c.role("R-30")
    role.sudo().write({"description": "secret text"})
    c.env["fix.sensitive.field"].sudo().create(
        {"name": "a", "model_name": "fix.role", "field_name": "description", "masking_rule": "hash"}
    )
    rows = p03.records(c.p, model="fix.role", cols=["description"], domain=[("id", "=", role.id)])[
        "rows"
    ]
    assert rows[0]["description"] != "secret text" and len(rows[0]["description"]) == 12


def test_a12f_e28_screens_say_what_is_enforced_and_where(c):
    js = JS.read_text(encoding="utf-8")
    assert "Not enforced in the Odoo back end" in js
    assert "A documented register" in js
    src = (Path(__file__).resolve().parents[1] / "models" / "fix_field_rule.py").read_text(
        encoding="utf-8"
    )
    assert "This model IS that engine" not in src
    assert "runtime engine" not in src


# ================================================================ E29 crons and helpers over RPC
@pytest.mark.parametrize(
    "model,method",
    [
        ("fix.access.request", "cron_expire_elevations"),
        ("fix.access.certification", "cron_close_certifications"),
        ("fix.privileged.session", "cron_close_stale_sessions"),
        ("fix.sod.test", "cron_run_sod_tests"),
        ("fix.jml.event", "consume_employee_left"),
    ],
)
def test_a12f_e29_crons_refuse_a_plain_user_over_rpc(c, model, method):
    args = [left_event(c.e_mgr)] if method == "consume_employee_left" else []
    with pytest.raises(REFUSED):
        call_kw(c.env[model].with_user(c.p), method, args, {})


# ================================================================ N-M28-6 roles carry the seats
def test_a12f_n_m28_6_roles_carry_integration_admin_and_cab(c):
    assert c.env.ref("cd_itsm.group_integration_admin") in c.role("R-33").group_ids
    assert c.env.ref("cd_itsm.group_itsm_cab_member") in c.role("R-02").group_ids
    assert c.env.ref("cd_rbac_ext.group_security_officer") in c.role("R-33").group_ids


def test_a12f_n_m28_6_holder_gets_them_through_a_request(c):
    granted(c, "R-33", c.tgt)
    assert has(c.tgt, "cd_itsm.group_integration_admin")
    assert has(c.tgt, OFFICER)
    second = _user(c.env, "a12f_cto")
    granted(c, "R-02", second)
    assert has(second, "cd_itsm.group_itsm_cab_member")
    assert has(second, "cd_itsm.group_itsm_change_manager")


# ================================================================ Screen wiring
def test_a12f_every_list_action_is_on_its_surface(c):
    from odoo.addons.cd_p03_portal.controllers.p03_generic_api import SURFACES

    js = JS.read_text(encoding="utf-8")
    for model, method in (
        ("fix.privileged.session", "action_open"),
        ("fix.security.incident", "action_confirm_severity"),
        ("fix.access.certification.campaign", "action_generate"),
    ):
        assert method in SURFACES[model]["actions"]
        assert "m: '%s'" % method in js
    assert "fix.role.assignment" in SURFACES
