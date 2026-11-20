# fix_fpa — M54: FP&A, cost accounting, budgeting (P09-M07).
from odoo import api, fields, models

from libs.py.fix_events import publish


class FixBudget(models.Model):
    """M54 FP&A: budgeting. The M49<->M54 break (AR-006 pair 14): M54
    consumes depreciation EVENTS; M49 never reads budgets."""
    _name = "fix.budget"
    _description = "Budget"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M54",
        "form": "Budget Version",
        "fields": ["name", "fiscal_year", "planned_amount"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    fiscal_year = fields.Char(required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    planned_amount = fields.Monetary(string="Planned", currency_field="currency_id")
    actual_amount = fields.Monetary(string="Actual", currency_field="currency_id")
    variance = fields.Monetary(compute="_compute_variance", string="Variance",
                               currency_field="currency_id", store=True)
    state = fields.Selection([("draft", "Draft"), ("approved", "Approved")],
                             default="draft", required=True, tracking=True)

    @api.depends("planned_amount", "actual_amount")
    def _compute_variance(self):
        for rec in self:
            rec.variance = rec.planned_amount - rec.actual_amount


class FixCostAllocation(models.Model):
    _name = "fix.cost.allocation"
    _description = "Cost Allocation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    direct_cost = fields.Monetary(string="Direct Cost", currency_field="currency_id")
    allocated_overhead = fields.Monetary(string="Allocated Overhead",
                                         currency_field="currency_id")
    total_cost = fields.Monetary(compute="_compute_total", string="Total",
                                 currency_field="currency_id", store=True)

    @api.depends("direct_cost", "allocated_overhead")
    def _compute_total(self):
        for rec in self:
            rec.total_cost = rec.direct_cost + rec.allocated_overhead
