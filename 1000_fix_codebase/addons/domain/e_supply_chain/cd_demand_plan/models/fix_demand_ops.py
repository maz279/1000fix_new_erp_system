# fix_demand_ops — M43: forecast cycles, segmentation, safety-stock/ROP policy,
# review cycles, rebalance proposals and what-if scenarios, plus the planned-
# order → purchase-requisition bridge for fix.demand.plan.
from math import sqrt

from odoo import api, fields, models
from odoo.exceptions import UserError

_Z_FACTORS = {90: 1.28, 95: 1.65, 98: 2.05, 99: 2.33}


class FixDemandForecast(models.Model):
    _name = "fix.demand.forecast"
    _description = "Demand Forecast"
    _order = "period desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="cascade", index=True
    )
    period = fields.Char(required=True, help="YYYY-MM")
    forecast_qty = fields.Float(string="Forecast Qty")
    actual_qty = fields.Float(string="Actual Qty")
    variance = fields.Float(string="Variance", compute="_compute_variance", store=True)
    abs_error_pct = fields.Float(string="Absolute Error %", compute="_compute_variance", store=True)
    method = fields.Selection(
        [
            ("moving_average", "Moving Average"),
            ("exponential", "Exponential Smoothing"),
            ("seasonal", "Seasonal"),
            ("manual", "Manual"),
        ],
        required=True,
        default="moving_average",
    )
    source = fields.Selection(
        [("history", "History-derived"), ("model", "Model"), ("manual", "Manual")],
        required=True,
        default="history",
    )
    confidence_pct = fields.Float(string="Confidence %", default=80.0)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("published", "Published")],
        required=True,
        default="draft",
    )
    notes = fields.Char()

    @api.depends("forecast_qty", "actual_qty")
    def _compute_variance(self):
        for rec in self:
            var = (rec.actual_qty or 0.0) - (rec.forecast_qty or 0.0)
            rec.variance = round(var, 3)
            base = rec.actual_qty or rec.forecast_qty
            rec.abs_error_pct = round(abs(var) / base * 100.0, 1) if base else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.demand.forecast") or "DFC/New"
                )
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft forecast")
            if rec.forecast_qty <= 0:
                raise UserError("A forecast needs a positive quantity")
            rec.state = "approved"

    def action_publish(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Publish an approved forecast")
            rec.state = "published"


class FixDemandSegment(models.Model):
    _name = "fix.demand.segment"
    _description = "Demand Segmentation"
    _order = "product_id"

    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="cascade", index=True
    )
    abc_class = fields.Selection(
        [("a", "A — High value"), ("b", "B — Medium"), ("c", "C — Low")],
        required=True,
        default="b",
    )
    xyz_class = fields.Selection(
        [("x", "X — Stable"), ("y", "Y — Variable"), ("z", "Z — Erratic")],
        required=True,
        default="y",
    )
    criticality = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        required=True,
        default="medium",
    )
    assigned_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("active", "Active"), ("archived", "Archived")], required=True, default="active"
    )

    _product_unique = models.Constraint("UNIQUE (product_id)", "One segmentation row per product")


class FixDemandPolicy(models.Model):
    _name = "fix.demand.policy"
    _description = "Safety Stock & Reorder Policy"
    _order = "product_id"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="cascade", index=True
    )
    avg_daily_demand = fields.Float(string="Avg Daily Demand")
    demand_stddev = fields.Float(string="Demand Std Dev")
    lead_time_days = fields.Integer(string="Lead Time (days)", default=7)
    service_level_pct = fields.Selection(
        [("90", "90%"), ("95", "95%"), ("98", "98%"), ("99", "99%")],
        required=True,
        default="95",
    )
    safety_stock = fields.Float(compute="_compute_policy", store=True, string="Safety Stock")
    reorder_point = fields.Float(compute="_compute_policy", store=True, string="Reorder Point")
    state = fields.Selection(
        [("active", "Active"), ("paused", "Paused")], required=True, default="active"
    )

    _daily_positive = models.Constraint(
        "CHECK (avg_daily_demand >= 0 AND demand_stddev >= 0 AND lead_time_days >= 0)",
        "Demand and lead-time inputs cannot be negative",
    )

    @api.depends("avg_daily_demand", "demand_stddev", "lead_time_days", "service_level_pct")
    def _compute_policy(self):
        for rec in self:
            z = _Z_FACTORS.get(int(rec.service_level_pct or 95), 1.65)
            lead = rec.lead_time_days or 0
            rec.safety_stock = round(z * (rec.demand_stddev or 0.0) * sqrt(lead), 2)
            rec.reorder_point = round((rec.avg_daily_demand or 0.0) * lead + rec.safety_stock, 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.demand.policy") or "DPOL/New"
                )
        return super().create(vals_list)

    def action_pause(self):
        for rec in self:
            rec.state = "paused"


class FixDemandReview(models.Model):
    _name = "fix.demand.review"
    _description = "Demand Review Cycle"
    _order = "period desc, id desc"

    name = fields.Char(required=True, default="New")
    period = fields.Char(required=True, help="YYYY-MM")
    owner_id = fields.Many2one("hr.employee", string="Owner")
    due_on = fields.Date(required=True)
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("done", "Done")], required=True, default="scheduled"
    )
    notes = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.demand.review") or "DRVW/New"
                )
        return super().create(vals_list)

    def action_complete(self):
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("Complete a scheduled review")
            rec.state = "done"


class FixDemandRebalance(models.Model):
    _name = "fix.demand.rebalance"
    _description = "Network Rebalance Proposal"
    _order = "proposed_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="restrict", index=True
    )
    source_branch = fields.Char(string="From Branch", required=True)
    target_branch = fields.Char(string="To Branch", required=True)
    qty = fields.Float(string="Quantity")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    unit_cost = fields.Monetary(string="Unit Cost", currency_field="currency_id")
    savings = fields.Monetary(
        string="Estimated Savings (10% of avoided buy)",
        currency_field="currency_id",
        compute="_compute_savings",
        store=True,
    )
    proposed_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("proposed", "Proposed"), ("approved", "Approved"), ("rejected", "Rejected")],
        required=True,
        default="proposed",
    )
    notes = fields.Char()

    _qty_positive = models.Constraint("CHECK (qty > 0)", "Rebalance quantity must be positive")

    @api.depends("qty", "unit_cost")
    def _compute_savings(self):
        for rec in self:
            rec.savings = round((rec.qty or 0.0) * (rec.unit_cost or 0.0) * 0.10, 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.demand.rebalance") or "DRBL/New"
                )
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Approve a proposed rebalance")
            rec.state = "approved"

    def action_reject(self):
        for rec in self:
            rec.state = "rejected"


class FixDemandScenario(models.Model):
    _name = "fix.demand.scenario"
    _description = "What-If Scenario"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="cascade", index=True
    )
    demand_adjust_pct = fields.Float(string="Demand Adjustment %", default=0.0)
    lead_time_delta_days = fields.Integer(string="Lead Time Delta (days)", default=0)
    base_reorder_point = fields.Float(string="Base ROP")
    projected_reorder_point = fields.Float(
        string="Projected ROP", compute="_compute_projected", store=True
    )
    state = fields.Selection([("draft", "Draft"), ("run", "Run")], required=True, default="draft")
    notes = fields.Char()

    @api.depends("base_reorder_point", "demand_adjust_pct")
    def _compute_projected(self):
        for rec in self:
            rec.projected_reorder_point = round(
                (rec.base_reorder_point or 0.0) * (1 + (rec.demand_adjust_pct or 0.0) / 100.0), 2
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.demand.scenario") or "DSCN/New"
                )
        return super().create(vals_list)

    def action_run(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Run a draft scenario")
            rec.state = "run"


class FixDemandPlanExtend(models.Model):
    _inherit = "fix.demand.plan"

    pr_requisition_id = fields.Many2one(
        "fix.requisition", string="Purchase Requisition", readonly=True, copy=False
    )

    def action_generate_pr(self):
        """Bridge the planned order to M16: one approved requisition per plan."""
        reqs = self.env["fix.requisition"]
        employee = self.env["hr.employee"].search([], limit=1)
        for plan in self:
            if plan.state != "approved":
                raise UserError("Approve the plan before generating a requisition")
            if plan.recommended_order <= 0:
                raise UserError("Nothing to order — the plan has no recommended quantity")
            if plan.pr_requisition_id:
                raise UserError("Plan %s already has a requisition" % plan.name)
            # the requisition's operating unit is NOT NULL: the plan's own OU,
            # else the user's default, else the company's first OU
            ou = (
                plan.operating_unit_id
                or self.env.user.default_operating_unit_id
                or self.env["operating.unit"].search(
                    [("company_id", "=", plan.company_id.id)], limit=1
                )
            )
            if not ou:
                raise UserError("Plan %s has no operating unit for its requisition" % plan.name)
            requisition = reqs.create(
                {
                    "description": "Planned order — %s (%s)" % (plan.product_id.name, plan.name),
                    "product_id": plan.product_id.product_variant_id.id,
                    "qty": plan.recommended_order,
                    "estimate_amount": plan.recommended_order
                    * (plan.product_id.standard_price or 0.0),
                    "urgency": "normal",
                    "requested_by": employee.id if employee else False,
                    "operating_unit_id": ou.id,
                    "state": "approved",
                }
            )
            plan.pr_requisition_id = requisition.id
