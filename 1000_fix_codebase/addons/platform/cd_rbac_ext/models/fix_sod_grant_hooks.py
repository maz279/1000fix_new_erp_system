# SoD at every grant path (A08 S4, A12 R2 / M29-4, FR-SEC-022, BRU-SEC-07).
#
# A user's duties change through three ORM doors: res.users (create / write of
# group_ids or role, including groups implied by the added ones), res.groups
# (users added to a group, or a group made to imply another), and hr.employee
# (the M21 primary / additional business roles, which is what
# hr.employee.assign_role writes). Each door snapshots the conflicts of the
# people it touches, lets the write happen, and refuses (rolls back) when the
# write CREATED a conflict that no approved, unexpired SoD exception covers.
# Conflicts a person already had are reported (fix_report_violations), never
# blocked, so an upgrade cannot lock out the existing admin or seed users.
# Superuser code and data loading pass, and every conflict they create is
# written to the security audit trail. There is deliberately no context key
# that skips the check: an RPC caller controls the context.
from odoo import api, models
from odoo.fields import Command

_USER_GROUP_KEYS = {"group_ids", "all_group_ids", "role"}
_GROUP_USER_KEYS = {"user_ids", "all_user_ids", "implied_ids", "implied_by_ids"}


def _command_ids(commands):
    """Record ids a list of x2many commands links or sets."""
    ids = set()
    for cmd in commands or []:
        if isinstance(cmd, int):
            ids.add(cmd)
        elif isinstance(cmd, (list, tuple)) and cmd:
            if cmd[0] == Command.LINK and len(cmd) > 1:
                ids.add(cmd[1])
            elif cmd[0] == Command.SET and len(cmd) > 2:
                ids.update(cmd[2] or [])
    return ids


def _touches_groups(vals):
    return any(
        key in _USER_GROUP_KEYS or key.startswith(("sel_groups_", "in_group_")) for key in vals
    )


class ResUsersSod(models.Model):
    _inherit = "res.users"

    def _fix_sod_snapshot(self, index):
        Sod = self.env["fix.sod.control"]
        return {user.id: Sod._fix_conflicts(user=user, index=index) for user in self.sudo()}

    def _fix_sod_check(self, before, index, path):
        Sod = self.env["fix.sod.control"]
        for user in self.sudo():
            after = Sod._fix_conflicts(user=user, index=index)
            Sod._fix_enforce(user, before.get(user.id, Sod.browse()), after, path)

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        index = self.env["fix.sod.control"]._fix_index()
        users._fix_sod_check({}, index, "user created with groups")
        return users

    def write(self, vals):
        if not self or not _touches_groups(vals):
            return super().write(vals)
        index = self.env["fix.sod.control"]._fix_index()
        before = self._fix_sod_snapshot(index)
        res = super().write(vals)
        self._fix_sod_check(before, index, "user groups changed")
        return res


class ResGroupsSod(models.Model):
    _inherit = "res.groups"

    def _fix_sod_affected_users(self, vals):
        Users = self.env["res.users"].sudo().with_context(active_test=False)
        users = self.sudo().with_context(active_test=False).all_user_ids
        users |= Users.browse(_command_ids(vals.get("user_ids")))
        users |= Users.browse(_command_ids(vals.get("all_user_ids")))
        implying = self.env["res.groups"].sudo().browse(_command_ids(vals.get("implied_by_ids")))
        users |= implying.with_context(active_test=False).all_user_ids
        return users.exists()

    @api.model_create_multi
    def create(self, vals_list):
        Users = self.env["res.users"].sudo().with_context(active_test=False)
        touched = Users.browse()
        for vals in vals_list:
            touched |= Users.browse(_command_ids(vals.get("user_ids")))
        touched = touched.exists()
        if not touched:
            return super().create(vals_list)
        index = self.env["fix.sod.control"]._fix_index()
        before = touched._fix_sod_snapshot(index)
        groups = super().create(vals_list)
        # Enforce as the CALLER (touched was read with sudo).
        touched.with_env(self.env)._fix_sod_check(before, index, "group created with members")
        return groups

    def write(self, vals):
        if not self or not (_GROUP_USER_KEYS & set(vals)):
            return super().write(vals)
        index = self.env["fix.sod.control"]._fix_index()
        touched = self._fix_sod_affected_users(vals)
        before = touched._fix_sod_snapshot(index)
        res = super().write(vals)
        self.env["res.groups"].invalidate_model(["all_user_ids", "all_implied_ids"])
        touched |= self.sudo().with_context(active_test=False).all_user_ids
        # Enforce as the CALLER (touched was read with sudo).
        touched.with_env(self.env)._fix_sod_check(
            before, index, "group membership changed (%s)" % self[:1].name
        )
        return res


class HrEmployeeSod(models.Model):
    _inherit = "hr.employee"

    _FIX_ROLE_KEYS = frozenset({"primary_role_id", "additional_role_ids", "user_id"})

    def _fix_person(self):
        """(user, employees) whose duties this employee's roles add to."""
        self.ensure_one()
        emp = self.sudo()
        Sod = self.env["fix.sod.control"]
        employees = Sod._fix_user_employees(emp.user_id) if emp.user_id else None
        return emp.user_id, (employees or emp)

    def _fix_sod_role_check(self, before, index, path):
        Sod = self.env["fix.sod.control"]
        for emp in self.sudo():
            user, employees = emp._fix_person()
            after = Sod._fix_conflicts(user=user, employees=employees, index=index)
            Sod._fix_enforce(
                user, before.get(emp.id, Sod.browse()), after, path, employees=employees
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not any(self._FIX_ROLE_KEYS & set(vals) for vals in vals_list):
            return super().create(vals_list)
        Sod = self.env["fix.sod.control"]
        index = Sod._fix_index()
        Users = self.env["res.users"].sudo()
        # What the linked login already had (so an existing conflict is not "new").
        by_user = {
            uid: Sod._fix_conflicts(user=Users.browse(uid), index=index)
            for uid in {v.get("user_id") for v in vals_list if v.get("user_id")}
        }
        employees = super().create(vals_list)
        before = {emp.id: by_user.get(emp.sudo().user_id.id, Sod.browse()) for emp in employees}
        employees._fix_sod_role_check(before, index, "employee created with business roles")
        return employees

    def write(self, vals):
        if not self or not (self._FIX_ROLE_KEYS & set(vals)):
            return super().write(vals)
        Sod = self.env["fix.sod.control"]
        index = Sod._fix_index()
        before = {}
        new_user = self.env["res.users"].sudo().browse(vals.get("user_id") or [])
        new_user_had = Sod._fix_conflicts(user=new_user, index=index) if new_user else Sod
        for emp in self.sudo():
            user, employees = emp._fix_person()
            before[emp.id] = (
                Sod._fix_conflicts(user=user, employees=employees, index=index) | new_user_had
            )
        res = super().write(vals)
        self._fix_sod_role_check(before, index, "employee business roles changed")
        return res
