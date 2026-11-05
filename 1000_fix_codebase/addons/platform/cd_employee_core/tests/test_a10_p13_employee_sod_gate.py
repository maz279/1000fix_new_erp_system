# A10 remediation (2026-11-05), P1-3: the employee master as a grant path
# (M60-4/-5).
#
# The business roles a person holds live here (primary + additional) — but
# the old gate compared one hand-picked pair, and a direct write() compared
# nothing at all. Both now clear the full-set gate, and the set spans both
# stores: the employee's own roles plus the register roles the linked
# user's Odoo groups carry.
import contextlib
import itertools

import pytest
from odoo.exceptions import ValidationError

_SEQ = itertools.count(1)


@contextlib.contextmanager
def _rejects(env, exc, match):
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


def _role(env, code, name=None):
    return env["fix.role"].create({"code": code, "name": name or code})


def _user(env, name):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 P13 %s %d" % (name, n),
                "login": "a10p13.%s.%d@a10.test" % (name.replace(" ", "").lower(), n),
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
            }
        )
    )


def _control(env, code, role_a, role_b, action="block"):
    return env["fix.sod.control"].create(
        {
            "code": code,
            "name": "%s (P13 employee gate)" % code,
            "role_a_id": role_a.id,
            "role_b_id": role_b.id,
            "conflict_action": action,
        }
    )


def test_employee_role_writes_gate_on_the_full_set(odoo_env):
    env = odoo_env
    keeper = _role(env, "R-P13k1", "Branch Store Keeper")
    counter = _role(env, "R-P13k2", "Inventory Manager")
    viewer = _role(env, "R-P13k3", "Viewer")
    _control(env, "SOD-P13k", keeper, counter)
    emp = env["hr.employee"].create({"name": "A10 P13 Keeper", "primary_role_id": keeper.id})
    with _rejects(env, ValidationError, match="SoD control SOD-P13k"):
        emp.write({"additional_role_ids": [(4, counter.id)]})
    emp.write({"additional_role_ids": [(4, viewer.id)]})  # a compatible role passes
    assert viewer in emp.additional_role_ids
    with _rejects(env, ValidationError, match="SoD control SOD-P13k"):
        emp.assign_role("R-P13k2")
    # born with both sides is a conflict, not a fresh start
    with _rejects(env, ValidationError, match="SoD control SOD-P13k"):
        env["hr.employee"].create(
            {
                "name": "A10 P13 Born Conflict",
                "primary_role_id": keeper.id,
                "additional_role_ids": [(4, counter.id)],
            }
        )


def test_the_gate_spans_the_linked_users_group_roles(odoo_env):
    env = odoo_env
    group = env["res.groups"].create({"name": "A10 P13 bridge group"})
    bridge = env["fix.role"].create({"code": "R-P13g1", "name": "Group Side", "group_id": group.id})
    master = _role(env, "R-P13g2", "Employee Side")
    _control(env, "SOD-P13g", bridge, master)
    # employee side first: the user's group arrives later and the group
    # write itself must surface the conflict with the employee's roles
    other = _user(env, "Other")
    env["hr.employee"].create(
        {"name": "A10 P13 Linked", "user_id": other.id, "primary_role_id": master.id}
    )
    with _rejects(env, ValidationError, match="SoD control SOD-P13g"):
        other.write({"group_ids": [(4, group.id)]})
    # group side first: the user already holds the bridge, so any employee
    # role write for them must surface the same conflict
    linked = _user(env, "Linked")
    linked.write({"group_ids": [(4, group.id)]})
    emp2 = env["hr.employee"].create({"name": "A10 P13 Grouped", "user_id": linked.id})
    with _rejects(env, ValidationError, match="SoD control SOD-P13g"):
        emp2.write({"primary_role_id": master.id})
