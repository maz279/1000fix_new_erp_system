# fix.refurb.grade — refurbishment grades for M14 (P03-M06-T04).
# The grade hierarchy that determines refurbishment pricing and quality.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .catalogue_roles import ROLE_OFFICER, require_role

# M37 capture audit, third pass (2026-11-19), FR-CAT-040: the grade bands are
# a fixed set, but their objective criteria, warranty and permitted channels
# are defined by the catalogue. No role could write any of it (ACL read-only),
# so the page offered nothing to capture. A Catalogue Officer now maintains
# exactly these fields; the code and M14's price multiplier stay fixed.
GRADE_DEFINITION = frozenset(
    {
        "name_bn",
        "description",
        "cosmetic_criteria",
        "functional_criteria",
        "warranty_days",
        "sell_counter",
        "sell_online",
        "sell_marketplace",
        "sell_b2b",
    }
)


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
    cosmetic_criteria = fields.Text(
        string="Cosmetic Criteria", help="Objective, checkable: scratches, dents, screen marks."
    )
    functional_criteria = fields.Text(
        string="Functional Criteria", help="Battery health, test results, missing functions."
    )
    sell_counter = fields.Boolean(string="Sold at the Counter / POS", default=True)
    sell_online = fields.Boolean(string="Sold Online (website / app)", default=True)
    sell_marketplace = fields.Boolean(string="Sold on the Marketplace", default=True)
    sell_b2b = fields.Boolean(string="Sold to Corporate (B2B)", default=True)
    active = fields.Boolean(default=True)

    @api.depends("code")
    def _compute_name(self):
        mapping = dict(self._fields["code"].selection)
        for rec in self:
            rec.name = mapping.get(rec.code, rec.code)

    def write(self, vals):
        if not self.env.su:
            require_role(self.env, (ROLE_OFFICER,), "Defining a refurbishment grade")
            fixed = sorted(
                n
                for n in set(vals) - GRADE_DEFINITION
                if n in self._fields
                and any(
                    (rec[n].id if self._fields[n].type == "many2one" else rec[n]) != vals[n]
                    for rec in self
                )
            )
            if fixed:
                raise UserError(
                    "A grade's code and price multiplier are fixed (M14 prices against them); "
                    "the catalogue defines its criteria, warranty and channels only (%s)."
                    % ", ".join(fixed)
                )
        return super().write(vals)
