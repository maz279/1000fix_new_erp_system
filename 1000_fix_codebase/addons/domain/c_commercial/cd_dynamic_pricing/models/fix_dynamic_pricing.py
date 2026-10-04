# fix_dynamic_pricing — M11 W7: dynamic pricing rules (P10-M05).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixDynamicPriceRule(models.Model):
    """M11 W7: dynamic pricing with bounds and explanations."""
    _name = "fix.dynamic.price.rule"
    _description = "Dynamic Price Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    rule_type = fields.Selection(
        [("demand_surge", "Demand Surge"), ("off_peak", "Off-Peak Discount"),
         ("inventory_clearance", "Inventory Clearance"),
         ("loyalty_tier", "Loyalty Tier Pricing")],
        required=True, default="demand_surge")
    adjustment_pct = fields.Float(string="Adjustment %")
    min_adjustment = fields.Float(string="Min Adjustment %")
    max_adjustment = fields.Float(string="Max Adjustment %")
    channel = fields.Selection([("marketplace", "Marketplace"),
                                 ("storefront", "Storefront"),
                                 ("both", "Both")],
                                default="both", required=True)
    active = fields.Boolean(default=True)

    @api.constrains("adjustment_pct", "max_adjustment", "min_adjustment")
    def _check_bounds(self):
        for rec in self:
            if rec.adjustment_pct > rec.max_adjustment:
                raise UserError(
                    "Adjustment %s exceeds the maximum %s" % (
                        rec.adjustment_pct, rec.max_adjustment))
            if rec.adjustment_pct < rec.min_adjustment:
                raise UserError(
                    "Adjustment %s below the minimum %s" % (
                        rec.adjustment_pct, rec.min_adjustment))

    def apply_to(self, base_price):
        self.ensure_one()
        return round(base_price * (1 + self.adjustment_pct / 100.0), 2)


class FixPriceExplanation(models.Model):
    """Every dynamic price is reconstructable — the audit trail."""
    _name = "fix.price.explanation"
    _description = "Price Explanation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    base_price = fields.Float(string="Base Price")
    final_price = fields.Float(string="Final Price")
    rules_applied = fields.Text(string="Rules Applied")
    model_driven = fields.Boolean(string="ML Model Driven")
