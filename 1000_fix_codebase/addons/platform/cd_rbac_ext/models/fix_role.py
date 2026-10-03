# fix.role — 53 reconciled roles (P03-M02-T02).
# Mapped to Keycloak realm roles AND Odoo res.groups.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixRole(models.Model):
    """A business role from the reconciled 53-role register (05-04 section 1).

    Each role maps 1:1 to a Keycloak realm role and an Odoo res.groups.
    SoD controls reference role PAIRS that must not be held simultaneously.
    """
    _name = "fix.role"
    _description = "Business Role"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"
    _sql_constraints = [
        ("code_unique", "unique(code)", "Role code must be unique"),
    ]

    code = fields.Char(string="Role Code (R-nn)", required=True, size=10,
                       help="The reconciled role identifier, e.g. R-01")
    name = fields.Char(string="Role Name", required=True)
    name_bn = fields.Char(string="Role Name (Bengali)", help="DE-17")
    description = fields.Text(string="Description")
    # AS-03: company_id on transactional models
    company_id = fields.Many2one("res.company", string="Company", index=True,
                                 default=lambda self: self.env.company)
    operating_unit_ids = fields.Many2many(
        "operating.unit", string="Operating Units",
        help="AS-03: OUs this role is scoped to; empty = all OUs")
    tier_ids = fields.Many2many("fix.isolation.tier", string="Data Isolation Tiers",
                                help="Which isolation tiers this role may access")
    group_id = fields.Many2one("res.groups", string="Odoo Group",
                               help="The Odoo group this role maps to")
    keycloak_role = fields.Char(string="Keycloak Realm Role",
                                help="The Keycloak realm role name (usually same as code)")
    active = fields.Boolean(default=True, tracking=True)

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            if not rec.code.startswith("R-"):
                raise ValidationError(f"Role code must be R-nn format, got {rec.code}")

    @api.onchange("group_id")
    def _onchange_group(self):
        """P04-M06-T06: a role linked to a workspace group drives menu
        visibility (NVR-22). The link is authored once the reconciled
        05-04 register loads — never guessed here."""
        if self.group_id and not self.keycloak_role:
            self.keycloak_role = self.code
