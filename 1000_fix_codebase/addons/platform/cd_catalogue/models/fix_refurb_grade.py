# fix.refurb.grade — refurbishment grades for M14 (P03-M06-T04).
# The grade hierarchy that determines refurbishment pricing and quality.
from odoo import api, fields, models


class FixRefurbGrade(models.Model):
    """A refurbishment grade: A/B/C/D, determining resale pricing and
    warranty terms for M14's circular business."""

    _name = "fix.refurb.grade"
    _description = "Refurbishment Grade"
    _order = "sequence"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint("UNIQUE (code)", "Grade code must be unique")

    sequence = fields.Integer(default=10)
    code = fields.Selection(
        [
            ("A", "Grade A — Like New"),
            ("B", "Grade B — Minor Cosmetic"),
            ("C", "Grade C — Visible Wear"),
            ("D", "Grade D — Functional Only"),
            ("E", "Grade E — For Parts"),
        ],
        required=True,
        string="Grade",
    )
    name = fields.Char(compute="_compute_name", store=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17")

    # AS-10: pricing factor as Monetary (the multiplier is a percentage,
    # but the resulting price adjustment is Monetary)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    price_multiplier = fields.Float(
        string="Price Multiplier (e.g. 0.8 = 80% of new price)",
        default=1.0,
        help="Applied to the original product price to determine the "
        "refurbished sale price. Not a Monetary field — it is a ratio. "
        "(tracking removed: Odoo 19 rejects the parameter on Float and "
        "this model carries no chatter.)",
    )
    warranty_days = fields.Integer(
        string="Refurb Warranty (days)", help="Warranty period for items sold at this grade"
    )
    description = fields.Text()
    active = fields.Boolean(default=True)

    @api.depends("code")
    def _compute_name(self):
        mapping = dict(self._fields["code"].selection)
        for rec in self:
            rec.name = mapping.get(rec.code, rec.code)
