# fix.sod.control — 61 segregation-of-duties controls (P03-M02-T04).
# The register of record is SP-006 (61 controls); 05-04 section 6 lists 30.
# Build to the register of record; record the discrepancy.
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
    _code_unique = models.Constraint('UNIQUE (code)', 'SoD control code must be unique')

    code = fields.Char(string="SoD Code", required=True, size=10)
    name = fields.Char(string="Description", required=True)
    # AS-03: company_id + operating_unit_id
    company_id = fields.Many2one("res.company", string="Company", index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    role_a_id = fields.Many2one("fix.role", string="Role A", required=True,
                                ondelete="cascade")
    role_b_id = fields.Many2one("fix.role", string="Role B", required=True,
                                ondelete="cascade")
    conflict_action = fields.Selection(
        [("block", "Block Assignment"), ("warn", "Warn + Require Approval"),
         ("log", "Log Only")],
        default="block", required=True,
        help="block = the role assignment is refused (the default for financial controls)")
    rationale = fields.Text(string="Why these roles conflict")
    active = fields.Boolean(default=True)

    @api.constrains("role_a_id", "role_b_id")
    def _check_different_roles(self):
        for rec in self:
            if rec.role_a_id == rec.role_b_id:
                raise ValidationError("SoD control cannot reference the same role twice.")

    @api.model
    def check_assignment(self, role_a: int, role_b: int) -> bool:
        """Check whether assigning both roles violates any SoD control.

        Returns True if the assignment is permitted, raises ValidationError
        if a 'block' control matches. Called from fix.role assignment paths.
        """
        conflict = self.search([
            ("role_a_id", "in", [role_a, role_b]),
            ("role_b_id", "in", [role_a, role_b]),
            ("conflict_action", "=", "block"),
            ("active", "=", True),
        ], limit=1)
        if conflict:
            raise ValidationError(
                f"SoD control {conflict.code}: {conflict.name} — "
                f"these roles cannot be held simultaneously.")
        return True
