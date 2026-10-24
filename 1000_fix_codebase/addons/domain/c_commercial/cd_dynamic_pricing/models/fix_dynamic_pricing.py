# fix_dynamic_pricing — M11 W7: dynamic pricing rules with audit explanations (P10-M05 / R08-M03).
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixDynamicPriceRule(models.Model):
    """M11 W7: dynamic pricing with bounds, surge/off-peak logic, and explanations."""

    _name = "fix.dynamic.price.rule"
    _description = "Dynamic Price Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    rate_card_id = fields.Many2one(
        "fix.rate.card",
        string="Rate Card Base",
        ondelete="set null",
        help="Linked base rate card from cd_rate_card",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    rule_type = fields.Selection(
        [
            ("demand_surge", "Demand Surge"),
            ("off_peak", "Off-Peak Discount"),
            ("inventory_clearance", "Inventory Clearance"),
            ("loyalty_tier", "Loyalty Tier Pricing"),
        ],
        required=True,
        default="demand_surge",
    )
    adjustment_pct = fields.Float(string="Adjustment %", default=0.0)
    surge_multiplier = fields.Float(string="Surge Multiplier", default=1.0)
    min_adjustment = fields.Float(string="Min Adjustment %", default=-50.0)
    max_adjustment = fields.Float(string="Max Adjustment %", default=100.0)
    channel = fields.Selection(
        [("marketplace", "Marketplace"), ("storefront", "Storefront"), ("both", "Both")],
        default="both",
        required=True,
    )
    active = fields.Boolean(default=True)

    @api.constrains("adjustment_pct", "max_adjustment", "min_adjustment")
    def _check_bounds(self):
        for rec in self:
            if rec.adjustment_pct > rec.max_adjustment:
                raise UserError(
                    "Adjustment %s exceeds the maximum %s"
                    % (rec.adjustment_pct, rec.max_adjustment)
                )
            if rec.adjustment_pct < rec.min_adjustment:
                raise UserError(
                    "Adjustment %s below the minimum %s" % (rec.adjustment_pct, rec.min_adjustment)
                )

    def apply_to(self, base_price):
        self.ensure_one()
        if base_price < 0:
            raise UserError("Base price cannot be negative")
        mult = self.surge_multiplier if self.surge_multiplier > 0 else 1.0
        adjusted = base_price * (1 + self.adjustment_pct / 100.0) * mult
        return round(adjusted, 2)

    def calculate_and_explain(self, base_price, context_info=None):
        """Calculate dynamic price and persist audit explanation trail."""
        self.ensure_one()
        final_price = self.apply_to(base_price)
        explanation_text = (
            f"Rule '{self.name}' ({self.rule_type}): adjustment {self.adjustment_pct}%, "
            f"surge mult {self.surge_multiplier}. Base: {base_price:.2f} -> Final: {final_price:.2f}. "
            f"Context: {context_info or 'Standard dispatch request'}"
        )
        explanation = self.env["fix.price.explanation"].create(
            {
                "name": f"EXP/{self.name}/{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "company_id": self.company_id.id,
                "operating_unit_id": self.operating_unit_id.id if self.operating_unit_id else False,
                "rule_id": self.id,
                "base_price": base_price,
                "final_price": final_price,
                "rules_applied": explanation_text,
                "model_driven": self.rule_type == "demand_surge",
            }
        )
        publish(
            self.env,
            "pricing.calculated",
            "fix.dynamic.price.rule",
            self.id,
            {
                "rule_name": self.name,
                "base_price": float(base_price),
                "final_price": float(final_price),
            },
        )
        return {
            "final_price": final_price,
            "explanation_id": explanation.id,
            "text": explanation_text,
        }


class FixPriceExplanation(models.Model):
    """Every dynamic price is reconstructable — the audit trail."""

    _name = "fix.price.explanation"
    _description = "Price Explanation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    rule_id = fields.Many2one("fix.dynamic.price.rule", string="Applied Rule", ondelete="set null")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    base_price = fields.Float(string="Base Price")
    final_price = fields.Float(string="Final Price")
    rules_applied = fields.Text(string="Rules Applied")
    model_driven = fields.Boolean(string="ML Model Driven")
