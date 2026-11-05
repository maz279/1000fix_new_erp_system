# fix.field.rule — the field-level permission engine (P03-M02-T05).
# security/<module>_field_rules.xml is mandatory wherever field-level
# permissions apply. This model IS that engine.
from odoo import fields, models


class FixFieldRule(models.Model):
    """A field-level permission rule: controls read/write/hidden per field per role.

    XML declaration lives in each module's security/<module>_field_rules.xml;
    this model is the runtime engine that applies them.
    """

    _name = "fix.field.rule"
    _description = "Field-Level Permission Rule"
    _order = "model_id, field_id"

    model_id = fields.Many2one("ir.model", string="Model", required=True, ondelete="cascade")
    field_id = fields.Many2one("ir.model.fields", string="Field", required=True, ondelete="cascade")
    role_ids = fields.Many2many(
        "fix.role", string="Roles", help="Empty = applies to all roles (deny-all default)"
    )
    permission = fields.Selection(
        [
            ("read", "Read Only"),
            ("write", "Read + Write"),
            ("hidden", "Hidden"),
            ("masked", "Masked (shows ***)"),
        ],
        default="hidden",
        required=True,
        help="hidden = the field is stripped from read results entirely",
    )
    operating_unit_ids = fields.Many2many(
        "operating.unit", string="Scope (OUs)", help="Empty = all OUs"
    )
    active = fields.Boolean(default=True)


class FixFieldRuleDisplayRoll(models.Model):
    """Read-only role-name roll for the D365 Field Rule form (M29 wiring
    pass, 2026-11-05) — the role m2m itself has no workspace editor."""

    _inherit = "fix.field.rule"
    _description = "Fix Field Rule M29 Display Roll"

    fix_role_roll = fields.Char(
        string="Roles",
        compute="_compute_display_rolls",
        help="The roles this field rule applies to; empty means every role " "(deny-all default).",
    )

    def _compute_display_rolls(self):
        for rec in self:
            codes = rec.role_ids.mapped("code")
            rec.fix_role_roll = ", ".join(sorted(codes)) if codes else "All roles"
