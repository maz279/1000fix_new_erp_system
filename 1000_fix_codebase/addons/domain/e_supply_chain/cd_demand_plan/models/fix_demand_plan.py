# fix_demand_plan — M43: demand planning and replenishment (P09-M07).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixDemandPlan(models.Model):
    """Demand planning on M15's reorder seam: the forecast feeds the
    replenishment policy; the M26 model supplies the numbers."""
    _name = "fix.demand.plan"
    _description = "Demand Plan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_start desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    product_id = fields.Many2one("product.template", string="Product",
                                 required=True)
    forecast_quantity = fields.Float(
        string="Forecast Quantity",
        help="The M26 forecast model's output; replaces heuristics")
    override_quantity = fields.Float(
        string="Planner Override", tracking=True,
        help="Set by an applied fix.forecast.override; the statistical "
             "forecast above is retained (BRU-DPL-06)")
    final_quantity = fields.Float(compute="_compute_recommended",
                                  string="Final Forecast", store=True)
    override_ids = fields.One2many("fix.forecast.override", "demand_plan_id",
                                   string="Overrides")
    current_stock = fields.Float(string="Current Stock")
    reorder_point = fields.Float(string="Reorder Point",
                                 help="M15's reorder seam, consumed here")
    recommended_order = fields.Float(compute="_compute_recommended",
                                     string="Recommended Order Qty",
                                     store=True)
    state = fields.Selection([("draft", "Draft"), ("approved", "Approved")],
                             default="draft", required=True, tracking=True)

    @api.depends("forecast_quantity", "override_quantity", "current_stock",
                 "reorder_point")
    def _compute_recommended(self):
        for rec in self:
            # the planner's applied override wins; the statistical
            # forecast_quantity stays untouched beside it
            rec.final_quantity = rec.override_quantity or rec.forecast_quantity
            gap = rec.final_quantity - rec.current_stock
            rec.recommended_order = max(gap, 0) if gap > rec.reorder_point else 0

    def action_approve(self):
        for rec in self:
            if rec.recommended_order <= 0:
                raise UserError("Nothing to replenish — forecast within stock")
            rec.state = "approved"
            publish(self.env, "demand_plan.approved", "fix.demand.plan",
                    rec.id, {"product": rec.product_id.name,
                             "quantity": rec.recommended_order})
