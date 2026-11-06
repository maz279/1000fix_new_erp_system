# fix.sod.control — 61 segregation-of-duties controls (P03-M02-T04).
# The register of record is SP-006 (61 controls); 05-04 section 6 lists 30.
# Build to the register of record; record the discrepancy.
#
# A12 audit (2026-11-04) R2: check_assignment worked but nothing called it,
# and it only compared the single pair passed in. The gates below are the
# cross-builder contract: every grant path (access request action_grant,
# JML apply, elevation, certification keep and the res.users group write
# override in res_users_ext.py) calls check_user_assignment, which tests
# EVERY role the user already holds x the incoming role.
import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class FixSodControl(models.Model):
    """A segregation-of-duties control: two roles that must not be held
    simultaneously by the same person (SP-006, the register of record)."""

    _name = "fix.sod.control"
    _description = "Segregation of Duties Control"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint("UNIQUE (code)", "SoD control code must be unique")

    code = fields.Char(string="SoD Code", required=True, size=10)
    name = fields.Char(string="Description", required=True)
    # AS-03: company_id + operating_unit_id
    company_id = fields.Many2one(
        "res.company", string="Company", index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    # Optional since the A08 S4 group-pair controls: a control pairs two
    # roles OR two Odoo groups (fix_sod_control_groups.py, pre-migrate
    # 19.0.1.2.1 drops the legacy NOT NULL).
    role_a_id = fields.Many2one("fix.role", string="Role A", ondelete="cascade")
    role_b_id = fields.Many2one("fix.role", string="Role B", ondelete="cascade")
    conflict_action = fields.Selection(
        [("block", "Block Assignment"), ("warn", "Warn + Require Approval"), ("log", "Log Only")],
        default="block",
        required=True,
        help="block = the role assignment is refused (the default for financial controls)",
    )
    rationale = fields.Text(string="Why these roles conflict")
    active = fields.Boolean(default=True)

    @api.constrains("role_a_id", "role_b_id")
    def _check_different_roles(self):
        for rec in self:
            if rec.role_a_id == rec.role_b_id:
                raise ValidationError("SoD control cannot reference the same role twice.")

    # ------------------------------------------------------------------
    # Resolution helpers: groups <-> roles (R1 mapping makes these real)
    # ------------------------------------------------------------------

    @api.model
    def _role_groups(self, role):
        """Every Odoo group a role maps to (the M2M register + legacy M2O)."""
        return (role.group_id | role.group_ids) if role else self.env["res.groups"]

    @api.model
    def roles_for_groups(self, group_ids):
        """Active roles whose mapped groups intersect `group_ids` (ids or records)."""
        if not group_ids:
            return self.env["fix.role"]
        if isinstance(group_ids, int):
            wanted = {group_ids}
        else:
            wanted = {g if isinstance(g, int) else g.id for g in group_ids}
        roles = self.env["fix.role"].sudo().search([("active", "=", True)])
        return roles.filtered(lambda r, w=wanted: w & set(self._role_groups(r).ids))

    @api.model
    def user_held_roles(self, user):
        """Every active role the user holds, measured through real group
        membership (the R1 role -> group mapping). Runs sudo internally: it
        is a governance read of group membership, not a data read."""
        user = user if hasattr(user, "_name") else self.env["res.users"].browse(user)
        groups = set(user.sudo().group_ids.ids)
        roles = self.env["fix.role"].sudo().search([("active", "=", True)])
        return roles.filtered(lambda r, g=groups: g & set(self._role_groups(r).ids))

    # ------------------------------------------------------------------
    # The gates
    # ------------------------------------------------------------------

    @api.model
    def check_assignment(self, role_a: int, role_b: int) -> bool:
        """Check whether assigning both roles violates any SoD control.

        Returns True if the assignment is permitted, raises ValidationError
        if a 'block' control matches. Called from fix.role assignment paths.
        """
        conflict = self.search(
            [
                ("role_a_id", "in", [role_a, role_b]),
                ("role_b_id", "in", [role_a, role_b]),
                ("conflict_action", "=", "block"),
                ("active", "=", True),
            ],
            limit=1,
        )
        if conflict:
            raise ValidationError(
                f"SoD control {conflict.code}: {conflict.name} — "
                f"these roles cannot be held simultaneously."
            )
        return True

    @api.model
    def check_user_assignment(self, user, role) -> bool:
        """A12 R2 SoD gate — the cross-builder contract.

        Tests EVERY role the user already holds (through real Odoo group
        membership) against the incoming role, not just one pair.

        Callable as:
            env["fix.sod.control"].check_user_assignment(user, role)
        with `user` a res.users record or id, `role` a fix.role record or
        id. Returns True when permitted; raises ValidationError listing
        every blocking control when the grant would create a conflict.
        Never call it under a waiver assumption: a waiver path (FR-SEC-024)
        is a business decision and is not shipped.
        """
        role = role if hasattr(role, "_name") else self.env["fix.role"].browse(role)
        if not role:
            return True
        held = self.user_held_roles(user) - role
        if not held:
            return True
        conflicts = self.search(
            [
                ("role_a_id", "in", [*held.ids, role.id]),
                ("role_b_id", "in", [*held.ids, role.id]),
                ("conflict_action", "=", "block"),
                ("active", "=", True),
            ],
        ).filtered(
            # a control fires when one side is the incoming role and the
            # other side is a role the user already holds
            lambda c, r=role, h=held: (c.role_a_id == r and c.role_b_id in h)
            or (c.role_b_id == r and c.role_a_id in h)
        )
        if conflicts:
            raise ValidationError(
                "SoD conflict: granting %s (%s) to a holder of %s breaks %s. "
                "Revoke one side first or route an exception per FR-SEC-024."
                % (
                    role.code,
                    role.name,
                    ", ".join(held.mapped("code")),
                    "; ".join("%s %s" % (c.code, c.name) for c in conflicts),
                )
            )
        return True

    @api.model
    def check_user_groups(self, user, group_ids) -> bool:
        """Convenience gate for group-level changes: maps the groups being
        ADDED to their roles and runs check_user_assignment for each."""
        for role in self.roles_for_groups(group_ids):
            self.check_user_assignment(user, role)
        return True

    # ---------------------------------------------- the preventive gate (A10 P1-3)
    @api.model
    def conflicts_in_role_set(self, role_ids) -> "FixSodControl":
        """Active controls whose role pair sits entirely inside role_ids."""
        ids = list({int(r) for r in role_ids if r})
        if len(ids) < 2:
            return self.browse()
        return self.search(
            [("role_a_id", "in", ids), ("role_b_id", "in", ids), ("active", "=", True)]
        )

    @api.model
    def check_role_set(self, role_ids, waiver=None) -> "FixSodControl":
        """The preventive SoD gate over one person's FULL final role set
        (A10 P1-3, M60-4/-5): the register only ever bit on one hand-written
        pair, so a grant could assemble a conflict role by role.

        block -> always refused (a documented GRC exception is the override,
                 not this path); warn  -> refused unless `waiver` carries an
        approver who is not the beneficiary, an expiry and a reason.
        Returns the waived warn controls so the caller logs them.
        """
        conflicts = self.conflicts_in_role_set(role_ids)
        for control in conflicts.filtered(lambda c: c.conflict_action == "block"):
            raise ValidationError(
                "SoD control %s: %s — one person cannot hold both roles. A "
                "documented GRC exception is the only override." % (control.code, control.name)
            )
        warn = conflicts.filtered(lambda c: c.conflict_action != "block")
        if warn:
            if not waiver:
                raise ValidationError(
                    "SoD control(s) %s — this combination needs a waiver: an "
                    "approved access request whose approver is someone else "
                    "and which states when the exception expires."
                    % ", ".join(warn.mapped("code"))
                )
            if not waiver.get("approver_id"):
                raise ValidationError("The SoD waiver has no approver.")
            if waiver.get("approver_id") == waiver.get("user_id"):
                raise ValidationError("The conflicted user cannot approve their own SoD waiver.")
            if not waiver.get("valid_until"):
                raise ValidationError(
                    "The SoD waiver has no expiry — state when the exception ends."
                )
            if fields.Date.to_date(waiver["valid_until"]) < fields.Date.context_today(self):
                raise ValidationError("The SoD waiver has already expired.")
            if not (waiver.get("reason") or "").strip():
                raise ValidationError("The SoD waiver has no reason.")
        return warn

    @api.model
    def gate_role_set(self, role_ids, user=None) -> "FixSodControl":
        """The register's own semantics for DIRECT writes (A10 P1-3):
        block refuses; warn is allowed but logged — the approval a warn
        control asks for lives on the access request, so a direct write
        leaves this warning as the trail the access review reads instead
        of an approval record. The strict waiver gate is check_role_set,
        used by the access-request channel."""
        conflicts = self.conflicts_in_role_set(role_ids)
        for control in conflicts.filtered(lambda c: c.conflict_action == "block"):
            raise ValidationError(
                "SoD control %s: %s — one person cannot hold both roles. A "
                "documented GRC exception is the only override." % (control.code, control.name)
            )
        warn = conflicts.filtered(lambda c: c.conflict_action != "block")
        for control in warn:
            _logger.warning(
                "SoD control %s (%s): %s holds both roles after a direct "
                "assignment — warn controls need an approved access request; "
                "this line is the trail for the access review.",
                control.code,
                control.name,
                user.login if user else "the user",
            )
        return warn

    # ------------------------------------------------ register bridges (A10 P1-3)
    @api.model
    def _role_of_group(self) -> dict:
        """The group→role side of the register bridge: fix.role rows that
        map to a real Odoo group. Empty until mappings are authored — the
        gate then honestly reports nothing rather than guessing."""
        return {
            r.group_id.id: r.id
            for r in self.env["fix.role"]
            .sudo()
            .search([("group_id", "!=", False), ("active", "=", True)])
        }

    @api.model
    def _employee_role_ids(self, user) -> set:
        """The business roles the user's employee record carries (hr lives
        downstream of this module; absent means no employee state to read)."""
        if "employee_ids" not in self.env["res.users"]._fields or not user:
            return set()
        roles = self.env["fix.role"].browse()
        for emp in user.sudo().employee_ids:
            roles |= emp.primary_role_id | emp.additional_role_ids
        return set(roles.ids)

    @api.model
    def _user_role_ids(self, user) -> set:
        """Everything the register knows about a user today: the roles the
        employee master records plus the roles their Odoo groups map to."""
        if not user:
            return set()
        role_of_group = self._role_of_group()
        return self._employee_role_ids(user) | {
            role_of_group[g] for g in user.sudo().group_ids.ids if g in role_of_group
        }

    @staticmethod
    def _final_groups(current, commands) -> set:
        """Apply res.users group commands to a current group-id set."""
        final = set(current)
        for cmd in commands or ():
            if isinstance(cmd, int):
                final.add(cmd)
            elif cmd[0] == 3:
                final.discard(cmd[1])
            elif cmd[0] == 4:
                final.add(cmd[1])
            elif cmd[0] == 5:
                final = set()
            elif cmd[0] == 6:
                final = set(cmd[2])
        return final

    @api.model
    def _check_users_group_write(self, users, commands):
        """The res.users write gate: a group ADDITION is the moment a person
        gains power, so the person's whole final register set — group-mapped
        roles plus their employee roles — is checked. Removals and groups
        outside the register change no business role and pass untouched;
        module installs are vendor acts recorded in the server log."""
        if self.env.context.get("install_mode"):
            return
        role_of_group = self._role_of_group()
        if not role_of_group:
            return
        for user in users:
            current = set(user.sudo().group_ids.ids)
            final = self._final_groups(current, commands)
            if not {role_of_group[g] for g in final - current if g in role_of_group}:
                continue  # nothing from the register is being added
            self.gate_role_set(
                {role_of_group[g] for g in final if g in role_of_group}
                | self._employee_role_ids(user),
                user=user,
            )

    @api.model
    def _check_new_user_groups(self, vals_list):
        """The res.users create gate: a user born holding a conflicting
        register pair is a conflict, not a fresh start."""
        if self.env.context.get("install_mode"):
            return
        role_of_group = self._role_of_group()
        if not role_of_group:
            return
        for vals in vals_list:
            commands = vals.get("group_ids") or vals.get("groups_id")
            if not commands:
                continue
            role_ids = {
                role_of_group[g]
                for g in self._final_groups(set(), commands)
                if g in role_of_group
            }
            if len(role_ids) >= 2:
                self.gate_role_set(role_ids)

