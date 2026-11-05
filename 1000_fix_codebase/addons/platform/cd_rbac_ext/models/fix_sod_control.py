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
from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
    role_a_id = fields.Many2one("fix.role", string="Role A", required=True, ondelete="cascade")
    role_b_id = fields.Many2one("fix.role", string="Role B", required=True, ondelete="cascade")
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
