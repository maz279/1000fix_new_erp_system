"""A12 / M29 remediation controls (B1: X1, X2, R1, R2, R3, R5, X5) proven on
the live ORM (`odoo_env` on fix_test_a12b1, rolled back per test). Every
control is attacked as NON-ADMIN users where the attack is a user attack, and
paired with the proper path still working.

Finding ids map to A12_Workflow_and_Approval_Report §6 / M29.md:
  X1  self-approval of access requests (M29-9)
  X2  leaver never deprovisioned (M29-5)
  R1  roles mapped to menu-only groups (M29-1/13)
  R2  SoD register never enforced (M29-2)
  R3  elevations/sessions/certifications never expire (M29-6)
  R5  audit trail forgeable, keys rotatable by anyone (M29-8/10)
  X5  device-log sudo leak (M29-11)
"""

import re
from datetime import timedelta
from pathlib import Path

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

APPROVER_GROUP = "cd_rbac_ext.group_access_approver"
CUSTODIAN_GROUP = "cd_rbac_ext.group_key_custodian"


# ---------------------------------------------------------------- helpers ----


def _user(env, login, groups=()):
    vals = {
        "name": login,
        "login": login,
        "email": "%s@a12.test" % login,
        "group_ids": [(6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])],
    }
    ou = env["operating.unit"].search([], limit=1)
    if ou:
        vals["default_operating_unit_id"] = ou.id
        vals["assigned_operating_unit_ids"] = [(6, 0, ou.ids)]
    return env["res.users"].with_context(no_reset_password=True).create(vals)


def _group(env, name):
    return env["res.groups"].create({"name": name})


def _role(env, code, groups):
    return env["fix.role"].create({"code": code, "name": code, "group_ids": [(6, 0, groups.ids)]})


def _control(env, code, role_a, role_b, action="block"):
    return env["fix.sod.control"].create(
        {
            "code": code,
            "name": code,
            "role_a_id": role_a.id,
            "role_b_id": role_b.id,
            "conflict_action": action,
        }
    )


def _request(env, vals):
    Rec = env["fix.access.request"]
    if vals.get("by"):
        Rec = Rec.with_user(vals["by"])  # so requested_by_id is the requester
    return Rec.create(
        {
            "request_type": "grant",
            "user_id": vals["user"].id,
            "role_id": vals["role"].id,
            "reason": "A12 test request",
            **vals.get("extra", {}),
        }
    )


def _approve(env, request, by):
    """The proper path: a real approver approves as themselves."""
    request.with_user(by).action_approve()


def _audit(env, event, ref_like=None):
    domain = [("event", "=", event)]
    if ref_like:
        domain.append(("object_ref", "like", ref_like))
    return env["fix.security.audit"].sudo().search(domain)


# ------------------------------------------------------------------ X1 ------


def test_x1_requester_beneficiary_and_bystander_cannot_approve(odoo_env):
    env = odoo_env
    ga = _group(env, "A12 X1 GA")
    role = _role(env, "R-X01", ga)
    requester = _user(env, "a12x1_requester")
    beneficiary = _user(env, "a12x1_benef")
    bystander = _user(env, "a12x1_bystander")
    req = _request(env, {"user": beneficiary, "role": role, "by": requester})

    with (
        pytest.raises(UserError, match="never the requester or the beneficiary"),
        env.cr.savepoint(),
    ):
        req.with_user(requester).action_approve()
    with (
        pytest.raises(UserError, match="never the requester or the beneficiary"),
        env.cr.savepoint(),
    ):
        req.with_user(beneficiary).action_approve()
    with pytest.raises(UserError, match="Access Approver"), env.cr.savepoint():
        req.with_user(bystander).action_approve()
    assert req.state == "submitted"


def test_x1_approver_group_and_requesters_manager_can_approve(odoo_env):
    env = odoo_env
    ga = _group(env, "A12 X1 GC")
    role = _role(env, "R-X02", ga)
    requester = _user(env, "a12x1_req2")
    approver = _user(env, "a12x1_approver", [APPROVER_GROUP])
    req = _request(env, {"user": requester, "role": role, "by": requester})

    # a member of the shipped (empty-by-design) approver group decides
    req.with_user(approver).action_approve()
    assert req.state == "approved"
    assert req.approver_id == approver
    assert req.decided_on

    # the requester's people manager is authority too
    manager = _user(env, "a12x1_mgr")
    mgr_emp = env["hr.employee"].create(
        {"name": "A12 Mgr", "employee_code": "A12X1M", "user_id": manager.id}
    )
    env["hr.employee"].create(
        {
            "name": "A12 Req2",
            "employee_code": "A12X1R",
            "user_id": requester.id,
            "parent_id": mgr_emp.id,
        }
    )
    role2 = _role(env, "R-X02b", _group(env, "A12 X1 GC2"))  # req is still open on role
    req2 = _request(env, {"user": requester, "role": role2, "by": requester})
    req2.with_user(manager).action_approve()
    assert req2.state == "approved"
    assert req2.approver_id == manager


def test_x1_decision_record_is_guarded_and_grant_rechecks_it(odoo_env):
    env = odoo_env
    ga = _group(env, "A12 X1 GD")
    role = _role(env, "R-X03", ga)
    requester = _user(env, "a12x1_req3")
    req = _request(env, {"user": requester, "role": role, "by": requester})

    # the state cannot be typed, even by a user with write ACL on the model
    with pytest.raises(UserError, match="cannot be set directly"), env.cr.savepoint():
        req.with_user(requester).write({"state": "approved", "approver_id": requester.id})

    # a forged approval (su edit) does not survive the grant re-check
    req.sudo().write(
        {"state": "approved", "approver_id": requester.id, "decided_on": fields.Datetime.now()}
    )
    with pytest.raises(UserError, match="intact approved request"), env.cr.savepoint():
        env["fix.access.request"].browse(req.id).action_grant()

    # a "real" approval whose approver is the beneficiary is equally refused
    req.sudo().write({"state": "submitted", "approver_id": False, "decided_on": False})
    req.sudo().write(
        {"state": "approved", "approver_id": requester.id, "decided_on": fields.Datetime.now()}
    )
    with pytest.raises(UserError, match="intact approved request"), env.cr.savepoint():
        env["fix.access.request"].browse(req.id).action_grant()


def test_x1_grant_provisions_as_a_service_and_audits(odoo_env):
    env = odoo_env
    ga, gb = _group(env, "A12 X1 GE"), _group(env, "A12 X1 GF")
    role = _role(env, "R-X04", ga | gb)  # R1: ALL mapped groups, not one
    beneficiary = _user(env, "a12x1_user4")
    approver = _user(env, "a12x1_appr4", [APPROVER_GROUP])  # NO Access Rights
    requester = _user(env, "a12x1_req4")
    req = _request(env, {"user": beneficiary, "role": role, "by": requester})

    req.with_user(approver).action_approve()
    # the requester cannot execute it (E23)...
    with pytest.raises(UserError, match="never the requester"), env.cr.savepoint():
        env["fix.access.request"].browse(req.id).with_user(requester).action_grant()
    # ...the approver can, with no erp_manager: the service write escalates
    env["fix.access.request"].browse(req.id).with_user(approver).action_grant()

    assert req.state == "granted"
    assert {ga.id, gb.id} <= set(beneficiary.sudo().group_ids.ids)
    rows = _audit(env, "grant", "fix.access.request,%d" % req.id)
    assert rows and "R-X04" in rows[0].detail and rows[0].actor_id.id == approver.id


def test_x1_revoke_of_an_unheld_role_is_refused(odoo_env):
    env = odoo_env
    ga = _group(env, "A12 X1 GG")
    role = _role(env, "R-X05", ga)
    beneficiary = _user(env, "a12x1_user5")
    approver = _user(env, "a12x1_appr5", [APPROVER_GROUP])
    req = _request(
        env,
        {"user": beneficiary, "role": role, "extra": {"request_type": "revoke"}},
    )
    req.with_user(approver).action_approve()
    with pytest.raises(UserError, match="nothing to revoke"), env.cr.savepoint():
        env["fix.access.request"].browse(req.id).action_grant()


# ------------------------------------------------------------------ X2 ------


def _leaver_fixture(env, tag, with_assets=True):
    g_role, g_extra = _group(env, "A12 %s RoleG" % tag), _group(env, "A12 %s ExtraG" % tag)
    role = _role(env, "R-X06", g_role)
    user = _user(env, "a12%s_user" % tag.lower())
    user.sudo().write({"group_ids": [(4, g_role.id), (4, g_extra.id)]})  # incl. a NON-role group
    employee = env["hr.employee"].create(
        {
            "name": "A12 %s Leaver" % tag,
            "employee_code": tag,
            "user_id": user.id,
            "left_date": fields.Date.today(),
        }
    )
    assets = env["fix.itsm.asset"]
    if with_assets and "fix.itsm.asset" in env:
        assets = env["fix.itsm.asset"].create(
            [
                {
                    "name": "A12 %s Laptop" % tag,
                    "asset_tag": "A12-%s-1" % tag,
                    "assigned_to_id": employee.id,
                },
                {
                    "name": "A12 %s Phone" % tag,
                    "asset_tag": "A12-%s-2" % tag,
                    "assigned_to_id": employee.id,
                },
            ]
        )
    return role, user, employee, assets


def _left_event(employee):
    return {
        "event_id": "evt-a12-%d" % employee.id,
        "event_type": "employee.left",
        "aggregate_id": employee.id,
        "payload": {
            "employee_id": employee.id,
            "employee_code": employee.employee_code,
            "left_date": fields.Date.today().isoformat(),
        },
        "metadata": {},
    }


def test_x2_consumer_is_registered_for_employee_left(odoo_env):
    consumers = (
        odoo_env["fix.event.consumer"]
        .sudo()
        .search([("event_type", "=", "employee.left"), ("method", "=", "consume_employee_left")])
    )
    assert consumers, "the employee.left -> M29 deprovision consumer must ship"
    assert consumers[0].model == "fix.jml.event"


def test_x2_leaver_deprovisioned_for_real(odoo_env):
    env = odoo_env
    role, user, employee, assets = _leaver_fixture(env, "X2A")

    env["fix.jml.event"].consume_employee_left(_left_event(employee))

    jml = (
        env["fix.jml.event"]
        .sudo()
        .search([("event_type", "=", "leaver"), ("employee_id", "=", employee.id)])
    )
    assert len(jml) == 1 and jml.state == "applied"
    assert "login deactivated" in jml.result_note
    user.invalidate_recordset(["group_ids", "active"])
    assert not user.active
    # ALL groups go — including the one no business role maps to (M29-5)
    assert not user.sudo().group_ids
    leaver_rows = _audit(env, "leaver", "res.users,%d" % user.id)
    assert leaver_rows and "login deactivated" in leaver_rows[0].detail


def test_x2_leaver_unassigns_itsm_assets(odoo_env):
    env = odoo_env
    if "fix.itsm.asset" not in env:
        pytest.skip("fix.itsm.asset not installed on this database")
    role, user, employee, assets = _leaver_fixture(env, "X2B")

    env["fix.jml.event"].consume_employee_left(_left_event(employee))

    assert not any(assets.mapped("assigned_to_id"))
    rows = _audit(env, "itsm_asset_unassign", "hr.employee,%d" % employee.id)
    assert rows and "2 ITSM asset(s)" in rows[0].detail


def test_x2_consumer_is_idempotent_on_redelivery(odoo_env):
    env = odoo_env
    role, user, employee, assets = _leaver_fixture(env, "X2C")

    env["fix.jml.event"].consume_employee_left(_left_event(employee))
    assert env["fix.jml.event"].consume_employee_left(_left_event(employee)) is True
    jml = (
        env["fix.jml.event"]
        .sudo()
        .search([("event_type", "=", "leaver"), ("employee_id", "=", employee.id)])
    )
    assert len(jml) == 1  # a redelivery created no second event


def test_x2_leaver_without_a_linked_user_is_recorded_not_crashed(odoo_env):
    env = odoo_env
    employee = env["hr.employee"].create(
        {"name": "A12 X2D No Login", "employee_code": "A12X2D", "left_date": fields.Date.today()}
    )
    assert env["fix.jml.event"].consume_employee_left(_left_event(employee)) is True
    jml = env["fix.jml.event"].sudo().search([("employee_id", "=", employee.id)])
    assert jml.state == "applied" and "no linked user" in jml.result_note


# ------------------------------------------------------------------ R1 ------


def test_r1_roles_map_to_real_permission_groups(odoo_env):
    env = odoo_env
    roles = env["fix.role"].search([])
    assert len(roles) >= 50, "the 53-role register must be present"
    system = env.ref("base.group_system")
    unmapped = roles.filtered(lambda r: not (r.group_id or r.group_ids) and r.code != "R-53")
    # R-53 (PPM project manager) is shipped by B4 after this module; every
    # other role carries a real group mapping
    assert not unmapped, "roles mapped to nothing: %s" % ", ".join(unmapped.mapped("code"))
    assert not roles.filtered(
        lambda r: system in (r.group_id | r.group_ids)
    ), "no business role may map to Settings (group_system)"
    hr_mgr = env.ref("hr.group_hr_manager")
    r30 = env.ref("cd_rbac_ext.role_r30")
    assert hr_mgr in (r30.group_id | r30.group_ids)


def test_r1_revoke_keeps_groups_another_held_role_requires(odoo_env):
    env = odoo_env
    g1, g2, g3 = _group(env, "A12 R1 G1"), _group(env, "A12 R1 G2"), _group(env, "A12 R1 G3")
    role_a = _role(env, "R-X07", g1 | g2)  # shares g2 with role b
    _role(env, "R-X08", g2 | g3)  # its groups stay held after role_a revoke
    user = _user(env, "a12r1_user")
    user.sudo().write({"group_ids": [(6, 0, [g1.id, g2.id, g3.id])]})
    approver = _user(env, "a12r1_appr", [APPROVER_GROUP])

    req = _request(env, {"user": user, "role": role_a, "extra": {"request_type": "revoke"}})
    req.with_user(approver).action_approve()
    env["fix.access.request"].browse(req.id).action_grant()

    user.invalidate_recordset(["group_ids"])
    held = set(user.sudo().group_ids.ids)
    assert g1.id not in held  # only role_a required it
    assert g2.id in held  # role_b still requires it — the coarse-revoke bug
    assert g3.id in held
    assert _audit(env, "revoke", "fix.access.request,%d" % req.id)


# ------------------------------------------------------------------ R2 ------


def _conflict_fixture(env, tag):
    ga, gb = _group(env, "A12 %s CA" % tag), _group(env, "A12 %s CB" % tag)
    ra, rb = _role(env, "R-%s1" % tag, ga), _role(env, "R-%s2" % tag, gb)
    _control(env, "SOD-%s" % tag, ra, rb)
    return ga, gb, ra, rb


def test_r2_check_user_assignment_tests_every_held_role(odoo_env):
    env = odoo_env
    ga, gb, ra, rb = _conflict_fixture(env, "R2A")
    gc = _group(env, "A12 R2A CC")
    rc = _role(env, "R-2AC", gc)
    user = _user(env, "a12r2_user")
    # the user holds the conflicting pair already: the gate on ANY new role
    # must still name the breach when one side is held (regression guard)
    user.sudo().write({"group_ids": [(4, ga.id)]})
    with pytest.raises(ValidationError, match="SOD-R2A"), env.cr.savepoint():
        env["fix.sod.control"].check_user_assignment(user, rb)
    assert env["fix.sod.control"].check_user_assignment(user, rc) is True
    # the group-level convenience gate resolves groups to roles
    with pytest.raises(ValidationError, match="SOD-R2A"), env.cr.savepoint():
        env["fix.sod.control"].check_user_groups(user, [gb.id])


def test_r2_gate_blocks_the_access_request_grant(odoo_env):
    env = odoo_env
    ga, gb, ra, rb = _conflict_fixture(env, "R2B")
    user = _user(env, "a12r2b_user")
    user.sudo().write({"group_ids": [(4, ga.id)]})
    approver = _user(env, "a12r2b_appr", [APPROVER_GROUP])
    req = _request(env, {"user": user, "role": rb})
    req.with_user(approver).action_approve()
    with pytest.raises(ValidationError, match="SOD-R2B"), env.cr.savepoint():
        env["fix.access.request"].browse(req.id).action_grant()
    user.invalidate_recordset(["group_ids"])
    assert gb.id not in set(user.sudo().group_ids.ids)  # nothing leaked through


def test_r2_gate_blocks_the_jml_apply_path(odoo_env):
    env = odoo_env
    ga, gb, ra, rb = _conflict_fixture(env, "R2C")
    user = _user(env, "a12r2c_user")
    user.sudo().write({"group_ids": [(4, ga.id)]})
    employee = env["hr.employee"].create(
        {"name": "A12 R2C Mover", "employee_code": "A12R2C", "user_id": user.id}
    )
    jml = env["fix.jml.event"].create(
        {
            "event_type": "mover",
            "employee_id": employee.id,
            "role_id": rb.id,
            "effective_on": fields.Date.today(),
        }
    )
    with pytest.raises(ValidationError, match="SOD-R2C"), env.cr.savepoint():
        jml.action_apply()
    assert jml.state == "pending"


def test_r2_gate_blocks_a_direct_group_write(odoo_env):
    env = odoo_env
    ga, gb, ra, rb = _conflict_fixture(env, "R2D")
    user = _user(env, "a12r2d_user")
    user.sudo().write({"group_ids": [(4, ga.id)]})
    admin = _user(env, "a12r2d_admin", ["base.group_erp_manager"])  # Access Rights
    with pytest.raises(ValidationError, match="SOD-R2D"), env.cr.savepoint():
        env["res.users"].browse(user.id).with_user(admin).write({"group_ids": [(4, gb.id)]})
    user.invalidate_recordset(["group_ids"])
    assert gb.id not in set(user.sudo().group_ids.ids)


def test_r2_gate_blocks_an_expired_and_conflicting_elevation(odoo_env):
    env = odoo_env
    ga, gb, ra, rb = _conflict_fixture(env, "R2E")
    user = _user(env, "a12r2e_user")
    user.sudo().write({"group_ids": [(4, ga.id)]})
    approver = _user(env, "a12r2e_appr", [APPROVER_GROUP])
    req = _request(
        env,
        {
            "user": user,
            "role": rb,
            "extra": {
                "request_type": "elevate",
                "valid_until": fields.Date.today() - timedelta(days=1),
            },
        },
    )
    req.with_user(approver).action_approve()
    with pytest.raises(UserError, match="expired"), env.cr.savepoint():
        env["fix.access.request"].browse(req.id).action_grant()


def test_r2_gate_runs_on_the_certification_keep(odoo_env):
    env = odoo_env
    ga, gb, ra, rb = _conflict_fixture(env, "R2F")
    user = _user(env, "a12r2f_user")
    user.sudo().write({"group_ids": [(4, ga.id), (4, gb.id)]})  # holds the conflict
    reviewer = _user(env, "a12r2f_rev")
    cert = env["fix.access.certification"].create(
        {"period": "2099-Q9", "user_id": user.id, "role_id": ra.id, "reviewer_id": reviewer.id}
    )
    with pytest.raises(ValidationError, match="SOD-R2F"), env.cr.savepoint():
        cert.with_user(reviewer).action_certify()
    assert cert.decision == "pending"


# ------------------------------------------------------------------ R3 ------


def test_r3_the_three_crons_are_registered(odoo_env):
    env = odoo_env
    crons = (
        env["ir.cron"]
        .sudo()
        .search(
            [
                (
                    "code",
                    "in",
                    (
                        "model.cron_expire_elevations()",
                        "model.cron_close_certifications()",
                        "model.cron_close_stale_sessions()",
                    ),
                )
            ]
        )
    )
    assert len(crons) == 3


def test_r3_elevation_expiry_cron_revokes_lapsed_access(odoo_env):
    env = odoo_env
    ga = _group(env, "A12 R3 GA")
    role = _role(env, "R-X09", ga)
    user = _user(env, "a12r3_user")
    user.sudo().write({"group_ids": [(4, ga.id)]})
    approver = _user(env, "a12r3_appr", [APPROVER_GROUP])
    req = _request(
        env,
        {
            "user": user,
            "role": role,
            "extra": {"request_type": "elevate", "valid_until": fields.Date.today()},
        },
    )
    req.with_user(approver).action_approve()
    env["fix.access.request"].browse(req.id).action_grant()
    req.sudo().write({"valid_until": fields.Date.today() - timedelta(days=5)})

    assert env["fix.access.request"].cron_expire_elevations() == 1
    user.invalidate_recordset(["group_ids"])
    assert ga.id not in set(user.sudo().group_ids.ids)
    assert req.state == "revoked"
    assert _audit(env, "elevation_expiry", "fix.access.request,%d" % req.id)


def test_r3_certification_closeout_revokes_unconfirmed_access(odoo_env):
    env = odoo_env
    ga = _group(env, "A12 R3 GB")
    role = _role(env, "R-X10", ga)
    user = _user(env, "a12r3b_user")
    user.sudo().write({"group_ids": [(4, ga.id)]})
    cert = env["fix.access.certification"].create(
        {
            "period": "2099-Q4",
            "user_id": user.id,
            "role_id": role.id,
            "reviewer_id": _user(env, "a12r3b_rev").id,
            "due_on": fields.Date.today() - timedelta(days=1),
        }
    )
    assert env["fix.access.certification"].cron_close_certifications() >= 1
    cert.invalidate_recordset()
    assert cert.decision == "revoked"
    user.invalidate_recordset(["group_ids"])
    assert ga.id not in set(user.sudo().group_ids.ids)
    assert _audit(env, "certification", "fix.access.certification,%d" % cert.id)


def test_r3_session_timeout_cron_force_closes_stale_sessions(odoo_env):
    env = odoo_env
    user = _user(env, "a12r3c_user")
    session = env["fix.privileged.session"].create(
        {
            "user_id": user.id,
            "access_kind": "sudo_admin",
            "reason": "A12 stale session probe",
            "state": "open",  # E10: a session opens only once approved
            "started_at": fields.Datetime.now() - timedelta(hours=10),
        }
    )
    assert env["fix.privileged.session"].cron_close_stale_sessions() >= 1
    session.invalidate_recordset()
    assert session.state == "closed" and session.duration_minutes >= 590
    assert _audit(env, "session_timeout", "fix.privileged.session,%d" % session.id)


# ------------------------------------------------------------------ R5 ------


def test_r5_audit_row_is_server_written(odoo_env):
    env = odoo_env
    other = _user(env, "a12r5_scapegoat")
    forged = (
        env["fix.security.audit"]
        .sudo()
        .create(
            {
                "event": "r5.forged",
                "sequence": 99999,
                "occurred_at": "2020-01-01 00:00:00",
                "actor_id": other.id,
                "prev_hash": "callerprev",
                "entry_hash": "callerhash",
            }
        )
    )
    assert forged.sequence != 99999
    assert forged.actor_id.id == env.uid  # the writing env, not the scapegoat
    assert forged.prev_hash != "callerprev" and forged.entry_hash != "callerhash"
    assert forged.occurred_at.year >= 2026


def test_r5_no_user_can_append_to_the_trail_directly(odoo_env):
    env = odoo_env
    for login, groups in (
        ("a12r5_plain", []),
        ("a12r5_admin", ["base.group_erp_manager"]),
        ("a12r5_sys", ["base.group_system"]),
    ):
        actor = _user(env, login, groups)
        with pytest.raises(AccessError), env.cr.savepoint():
            env["fix.security.audit"].with_user(actor).create(
                {"event": "r5.sneaky", "object_ref": "x", "detail": "typed"}
            )
    # ... and the contract path still works and records the CALLING user
    human = _user(env, "a12r5_human")
    row = (
        env["fix.security.audit"]
        .with_user(human)
        .log_event(
            "integration.key_rotated",
            "fix.api.consumer,42",
            "free-form event names are the contract",
        )
    )
    assert row.actor_id == human and row.event == "integration.key_rotated"


def test_r5_audit_is_append_only_and_hash_chained(odoo_env):
    env = odoo_env
    first = env["fix.security.audit"].sudo().log_event("r5.one", "fix.x,1", "first")
    second = env["fix.security.audit"].sudo().log_event("r5.two", "fix.x,2", "second")
    assert second.prev_hash == first.entry_hash
    with pytest.raises(UserError, match="append-only"), env.cr.savepoint():
        env["fix.security.audit"].sudo().browse(first.id).write({"detail": "rewritten"})
    with pytest.raises(UserError, match="append-only"), env.cr.savepoint():
        env["fix.security.audit"].sudo().browse(first.id).unlink()


def test_r5_verifier_recomputes_and_detects_an_in_row_edit(odoo_env):
    env = odoo_env
    Audit = env["fix.security.audit"].sudo()  # ONE env: cache + verify must agree
    Audit.log_event("r5.verify", "fix.x,3", "chain probe")

    def _discontinuities():
        # the record cache is per-transaction and survives the raw SQL below:
        # drop it entirely, or verify recomputes from stale pre-edit values
        env.invalidate_all(flush=False)
        # E27: a clean chain answers with a result; a broken one refuses
        try:
            text = Audit.action_verify_chain()["note"]
        except UserError as exc:
            text = str(exc)
        return int(re.search(r"(\d+) discontinuit", text).group(1))

    before = _discontinuities()
    victim = env["fix.security.audit"].sudo().search([], order="id desc", limit=1)
    env.cr.execute(  # raw SQL: the ORM write guard must not be the only defence
        "UPDATE fix_security_audit SET detail = %s WHERE id = %s",
        ("edited behind the ORM", victim.id),
    )
    env["fix.security.audit"].invalidate_recordset()
    after = _discontinuities()
    assert after > before, "an in-row edit must surface as a chain discontinuity"


def test_r5_keys_are_custodian_only_and_rotation_is_real(odoo_env):
    env = odoo_env
    key = env["fix.encryption.key"].create(
        {"code": "A12-R5-KEY", "name": "A12 probe", "vault_ref": "vault://kv/a12/1"}
    )
    plain = _user(env, "a12r5_keyplain")
    custodian = _user(env, "a12r5_cust", [CUSTODIAN_GROUP])

    with pytest.raises(AccessError), env.cr.savepoint():
        env["fix.encryption.key"].browse(key.id).with_user(plain).write({"algorithm": "rsa_4096"})
    with pytest.raises(UserError, match="Key Custodian"), env.cr.savepoint():
        env["fix.encryption.key"].browse(key.id).with_user(plain).action_rotate("vault://kv/a12/2")
    # the state is action-only, even for the custodian
    with pytest.raises(UserError, match="cannot be set directly"), env.cr.savepoint():
        env["fix.encryption.key"].browse(key.id).with_user(custodian).write({"state": "retired"})
    # key material may never be typed
    with pytest.raises(UserError, match="vault://"), env.cr.savepoint():
        env["fix.encryption.key"].browse(key.id).with_user(custodian).action_rotate("hsm://a12/raw")

    env["fix.encryption.key"].browse(key.id).with_user(custodian).action_rotate("vault://kv/a12/2")
    key.invalidate_recordset()
    assert key.state == "retired" and key.successor_id.code == "A12-R5-KEY/V1"
    assert key.successor_id.state == "active" and key.last_rotated_on == fields.Date.today()
    assert _audit(env, "key_rotation", "fix.encryption.key,%d" % key.id)


def test_r5_sensitive_field_classification_is_read_only(odoo_env):
    env = odoo_env
    plain = _user(env, "a12r5_sf")
    with pytest.raises(AccessError), env.cr.savepoint():
        env["fix.sensitive.field"].with_user(plain).create(
            {
                "model_name": "res.partner",
                "field_name": "vat",
                "sensitivity": "s3",
                "data_class": "financial",
                "masking_rule": "full",
            }
        )


def test_r5_incident_closure_discipline(odoo_env):
    env = odoo_env
    reporter = _user(env, "a12r5_inc")
    officer = _user(env, "a12r5_off", ["cd_rbac_ext.group_security_officer"])
    Incident = env["fix.security.incident"].with_user(reporter)

    # a workflow field cannot be typed at create either
    with pytest.raises(UserError, match="cannot be set directly"), env.cr.savepoint():
        Incident.create({"title": "A12 born closed", "category": "malware", "state": "closed"})

    # anyone may report; handling it is the officer's (E16)
    inc = Incident.create({"title": "A12 leak", "category": "data_leak"}).with_user(officer)
    with pytest.raises(UserError, match="Close a contained incident"), env.cr.savepoint():
        inc.action_close()
    inc.write({"containment": "revoked the sessions and forced a password reset"})
    inc.action_contain()
    with pytest.raises(UserError, match="root cause"), env.cr.savepoint():
        inc.action_close()
    inc.write({"root_cause": "a shared service account was reused across two branches"})
    with pytest.raises(UserError, match="breach assessment"), env.cr.savepoint():
        inc.action_close()
    inc.write({"breach_assessment": "no personal data exposed; 0 data subjects; no PDPA clock"})
    inc.action_close()
    assert inc.state == "closed" and inc.resolved_on
    assert _audit(env, "incident", "fix.security.incident,%d" % inc.id)


def test_r5_severity_change_needs_a_second_person(odoo_env):
    env = odoo_env
    reporter = _user(env, "a12r5_sev")
    officer = _user(env, "a12r5_sev1", ["cd_rbac_ext.group_security_officer"])
    colleague = _user(env, "a12r5_sev2", ["cd_rbac_ext.group_security_officer"])
    created = (
        env["fix.security.incident"]
        .with_user(reporter)
        .create({"title": "A12 severity probe", "category": "phishing"})
    )
    inc = created.with_user(officer)
    # naming a witness changes nothing: E15, the witness acts himself
    inc.action_set_severity("critical", confirmed_by_id=colleague.id)
    assert inc.severity == "medium" and inc.severity_pending == "critical"
    with pytest.raises(UserError, match="second person"), env.cr.savepoint():
        inc.action_confirm_severity()
    created.with_user(colleague).action_confirm_severity()
    assert inc.severity == "critical"
    assert inc.severity_set_by_id == officer and inc.severity_confirmed_by_id == colleague
    assert _audit(env, "incident", "fix.security.incident,%d" % inc.id).filtered(
        lambda r: "severity" in (r.detail or "")
    )


def test_r5_certification_reviewer_may_not_be_the_reviewed(odoo_env):
    env = odoo_env
    user = _user(env, "a12r5_cert")
    role = _role(env, "R-X11", _group(env, "A12 R5 CG"))
    with pytest.raises(ValidationError, match="self-certification"), env.cr.savepoint():
        env["fix.access.certification"].create(
            {"period": "2099-Q1", "user_id": user.id, "role_id": role.id, "reviewer_id": user.id}
        )


# ------------------------------------------------------------------ X5 ------


def test_x5_personal_data_surfaces_read_under_record_rules():
    from odoo.addons.cd_p03_portal.controllers.a12 import m29 as ctrl

    assert ctrl.SURFACES["res.device.log"]["rules"] is True
    assert ctrl.SURFACES["res.users"]["rules"] is True


def test_x5_writable_covers_every_surface_and_excludes_workflow_fields():
    from odoo.addons.cd_p03_portal.controllers.a12 import m29 as ctrl

    assert set(ctrl.WRITABLE) == set(ctrl.SURFACES), "every surface must declare WRITABLE"
    locked = {
        "state",
        "decision",
        "resolution",
        "in_force",
        "ruled_by",
        "ruled_on",
        "approver_id",
        "decided_on",
        "resolved_on",
        "entry_hash",
    }
    for surface, fields_ in ctrl.WRITABLE.items():
        leaked = locked & set(fields_)
        assert not leaked, "%s exposes workflow fields %s" % (surface, sorted(leaked))
    assert ctrl.WRITABLE["fix.security.audit"] == ()
    assert ctrl.WRITABLE["res.device.log"] == ()
    assert ctrl.WRITABLE["res.groups"] == ()


def test_x5_workspace_forms_do_not_edit_workflow_fields():
    js = (
        Path(__file__).resolve().parents[2] / "cd_p03_portal" / "static" / "src" / "a12" / "m29.js"
    ).read_text(encoding="utf-8")
    for name in (
        "state",
        "decision",
        "resolution",
        "last_rotated_on",
        "next_rotation_on",
    ):
        assert not re.search(r"name:\s*'%s'" % name, js), (
            "m29.js still offers %s as a typed form field" % name
        )
