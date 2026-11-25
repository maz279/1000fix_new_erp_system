# A10 remediation (2026-11-05), P1-3: the preventive SoD gates on every
# grant path (M60-4/-5).
#
# The audit found the 61-control register enforced nowhere that mattered:
# check_assignment had one caller checking one hand-picked pair, the access
# request granted its group unchecked, and the raw res.users group write —
# the operation that actually hands a person power — checked nothing.
# Every path now gates on the person's FULL register set (group-mapped
# roles plus their employee roles); a warn control on the request channel
# needs a real waiver: an approver who is not the beneficiary, an expiry
# and a reason — and the expiry is enforced by a cron, not believed.
import contextlib
import datetime
import itertools

import pytest
from odoo import fields
from odoo.exceptions import UserError, ValidationError

_SEQ = itertools.count(1)


@contextlib.contextmanager
def _rejects(env, exc, match):
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


def _user(env, name, approver=False):
    n = next(_SEQ)
    groups = [env.ref("base.group_user").id]
    if approver:
        # A12 X1: an access request is decided by an Access Approver (or
        # the requester's manager) — never a bystander. The fixtures that
        # decide requests hold the group.
        groups.append(env.ref("cd_rbac_ext.group_access_approver").id)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 P13 %s %d" % (name, n),
                "login": "a10p13.%s.%d@a10.test" % (name.replace(" ", "").lower(), n),
                "group_ids": [(6, 0, groups)],
            }
        )
    )


def _grouped_role(env, code, name):
    group = env["res.groups"].create({"name": "A10 P13 group %s" % code})
    return env["fix.role"].create({"code": code, "name": name, "group_ids": [(6, 0, group.ids)]})


# ---------------------------------------------------------- the raw group write
def test_group_write_refuses_a_register_block_conflict(odoo_env):
    env = odoo_env
    role_a = _grouped_role(env, "R-P13a", "Vendor Creator")
    role_b = _grouped_role(env, "R-P13b", "Invoice Approver")
    env["fix.sod.control"].create(
        {
            "code": "SOD-P13a",
            "name": "Create vendor + approve vendor invoice (P13)",
            "role_a_id": role_a.id,
            "role_b_id": role_b.id,
            "conflict_action": "block",
        }
    )
    holder = _user(env, "Holder")
    # the people who hand out groups: superuser code passes this door and is
    # recorded on the audit trail (test_superuser_write_is_recorded below)
    admin = _user(env, "Access Admin")
    admin.write({"group_ids": [(4, env.ref("base.group_erp_manager").id)]})
    holder.with_user(admin).write({"group_ids": [(4, role_a.group_ids.id)]})  # one side is fine
    with _rejects(env, ValidationError, match="SoD control SOD-P13a"):
        holder.with_user(admin).write({"group_ids": [(4, role_b.group_ids.id)]})
    # a user born with both sides is a conflict, not a fresh start
    with _rejects(env, ValidationError, match="SoD control SOD-P13a"):
        env["res.users"].with_user(admin).with_context(no_reset_password=True).create(
            {
                "name": "A10 P13 Born Bad",
                "login": "a10p13.bornbad@a10.test",
                "group_ids": [
                    (
                        6,
                        0,
                        [env.ref("base.group_user").id, role_a.group_ids.id, role_b.group_ids.id],
                    )
                ],
            }
        )
    # a removal never creates a conflict, even on a legacy conflicted user
    legacy = (
        env["res.users"]
        .with_context(install_mode=True, no_reset_password=True)
        .create(
            {
                "name": "A10 P13 Legacy",
                "login": "a10p13.legacy@a10.test",
                "group_ids": [
                    (
                        6,
                        0,
                        [env.ref("base.group_user").id, role_a.group_ids.id, role_b.group_ids.id],
                    )
                ],
            }
        )
    )
    legacy.write({"group_ids": [(3, role_b.group_ids.id)]})
    assert role_b.group_ids not in legacy.group_ids
    # a group outside the register passes untouched
    passer = env["res.groups"].create({"name": "A10 P13 unregistered group"})
    holder.with_user(admin).write({"group_ids": [(4, passer.id)]})


def test_superuser_write_is_recorded(odoo_env):
    env = odoo_env
    role_a = _grouped_role(env, "R-P13s1", "Vendor Creator")
    role_b = _grouped_role(env, "R-P13s2", "Invoice Approver")
    env["fix.sod.control"].create(
        {
            "code": "SOD-P13s",
            "name": "Superuser conflict is logged (P13)",
            "role_a_id": role_a.id,
            "role_b_id": role_b.id,
            "conflict_action": "block",
        }
    )
    holder = _user(env, "Service Holder")
    holder.sudo().write({"group_ids": [(4, role_a.group_ids.id), (4, role_b.group_ids.id)]})
    rows = (
        env["fix.security.audit"]
        .sudo()
        .search([("object_ref", "=", "res.users,%d" % holder.id), ("detail", "like", "SOD-P13s")])
    )
    assert rows and "superuser" in rows[0].detail


# ------------------------------------------------------- the access request path
def test_warn_conflict_needs_a_real_waiver_to_grant(odoo_env):
    env = odoo_env
    role_a = _grouped_role(env, "R-P13w1", "Customer Creator")
    role_b = _grouped_role(env, "R-P13w2", "Credit Approver")
    env["fix.sod.control"].create(
        {
            "code": "SOD-P13w",
            "name": "Create customer + approve credit limit (P13)",
            "role_a_id": role_a.id,
            "role_b_id": role_b.id,
            "conflict_action": "warn",
        }
    )
    beneficiary = _user(env, "Beneficiary")
    approver = _user(env, "Approver", approver=True)
    beneficiary.write({"group_ids": [(4, role_a.group_ids.id)]})
    # the raw write is the register's own semantics: a warn control logs and
    # passes — the approval it asks for lives on the request channel
    beneficiary.write({"group_ids": [(4, role_b.group_ids.id)]})
    assert role_b.group_ids in beneficiary.group_ids
    beneficiary.write({"group_ids": [(3, role_b.group_ids.id)]})  # back to one side
    # no waiver on the request: no expiry -> refused
    req = env["fix.access.request"].create(
        {
            "user_id": beneficiary.id,
            "role_id": role_b.id,
            "reason": "Credit desk cover during leave",
        }
    )
    req.with_user(approver).action_approve()
    assert req.approver_id == approver
    with _rejects(env, UserError, match="no expiry"):
        req.action_grant()
    # the beneficiary approving their own conflict is not a waiver — under
    # the A12 X1 control the self-approval is refused at the DECISION, a
    # layer earlier than the grant-time SoD waiver check it used to be
    self_req = env["fix.access.request"].create(
        {
            "user_id": beneficiary.id,
            "role_id": role_b.id,
            "reason": "I promise to be careful",
            "request_type": "elevate",
            "valid_until": fields.Date.today() + datetime.timedelta(days=7),
        }
    )
    with _rejects(env, UserError, match="never the requester or the beneficiary"):
        self_req.with_user(beneficiary).action_approve()
    # a real waiver: someone else, an expiry, a reason — and the log records it
    req.write({"valid_until": fields.Date.today() + datetime.timedelta(days=7)})
    req.action_grant()
    assert req.state == "granted"
    assert role_b.group_ids in beneficiary.group_ids
    assert "SoD waiver applied — control SOD-P13w" in req.message_ids[0].body


def test_block_conflict_is_refused_even_with_a_full_waiver(odoo_env):
    env = odoo_env
    role_a = _grouped_role(env, "R-P13b1", "Journal Preparer")
    role_b = _grouped_role(env, "R-P13b2", "Posting Approver")
    env["fix.sod.control"].create(
        {
            "code": "SOD-P13b",
            "name": "Prepare journal entry + approve posting (P13)",
            "role_a_id": role_a.id,
            "role_b_id": role_b.id,
            "conflict_action": "block",
        }
    )
    beneficiary = _user(env, "Preparer")
    approver = _user(env, "CFO", approver=True)
    beneficiary.write({"group_ids": [(4, role_a.group_ids.id)]})
    req = env["fix.access.request"].create(
        {
            "user_id": beneficiary.id,
            "role_id": role_b.id,
            "reason": "Month-end crunch",
            "valid_until": fields.Date.today() + datetime.timedelta(days=3),
        }
    )
    req.with_user(approver).action_approve()
    with _rejects(env, ValidationError, match="SOD-P13b.*only override"):
        req.action_grant()
    assert req.state == "approved"  # nothing was granted
    assert role_b.group_ids not in beneficiary.group_ids


def test_expired_access_loses_its_group_and_waiver(odoo_env):
    env = odoo_env
    role_a = _grouped_role(env, "R-P13e1", "Returns Inspector")
    role_b = _grouped_role(env, "R-P13e2", "Refund Approver")
    env["fix.sod.control"].create(
        {
            "code": "SOD-P13e",
            "name": "Inspect return + approve refund (P13)",
            "role_a_id": role_a.id,
            "role_b_id": role_b.id,
            "conflict_action": "warn",
        }
    )
    beneficiary = _user(env, "Expired")
    approver = _user(env, "Still There", approver=True)
    beneficiary.write({"group_ids": [(4, role_a.group_ids.id)]})
    req = env["fix.access.request"].create(
        {
            "user_id": beneficiary.id,
            "role_id": role_b.id,
            "reason": "Peak season cover",
            # the waiver gate reads the company's local day, not UTC: at 01:00
            # in Dhaka fields.Date.today() is still yesterday
            "valid_until": fields.Date.context_today(env["fix.sod.control"]),
        }
    )
    req.with_user(approver).action_approve()
    req.action_grant()  # the window is open today
    assert role_b.group_ids in beneficiary.group_ids
    # time passes: the window closes and the cron takes the access with it
    req.write({"valid_until": fields.Date.today() - datetime.timedelta(days=1)})
    Request = env["fix.access.request"]
    assert Request.cron_expire_elevations() >= 1
    req.invalidate_recordset()
    assert req.state == "revoked"
    assert role_b.group_ids not in beneficiary.group_ids
    assert "Expired on" in req.message_ids[0].body
    # the clock is idempotent within the day
    assert not Request.search(
        [("state", "=", "granted"), ("valid_until", "<", fields.Date.today()), ("id", "=", req.id)]
    )
