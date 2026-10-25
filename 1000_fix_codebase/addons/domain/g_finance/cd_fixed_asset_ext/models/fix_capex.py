# fix_capex — M49 capital budget and capex requests.
#
# Capital budget (approved by an accounting manager, SoD) -> capex request
# (draft -> submitted -> approved by a manager who is not the requester, and
# only within the budget's available amount) -> CWIP project -> capitalised
# asset. The budget's consumption is computed from the approved requests
# (committed) and from the CWIP cost booked against them (actual).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_asset_common import MANAGER_GROUP, USER_GROUP, check_sod, money, require_group

COMMITTED_STATES = ("approved", "cwip", "capitalised")


class FixCapexBudget(models.Model):
    _name = "fix.capex.budget"
    _description = "Capital Budget"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Branch", help="Leave empty: a company-wide budget."
    )
    name = fields.Char(string="Budget", required=True, tracking=True)
    fiscal_year = fields.Char(string="Fiscal Year", help="For example FY2026-27 (July-June).")
    date_from = fields.Date(string="Start Date", required=True, tracking=True)
    date_to = fields.Date(string="End Date", required=True, tracking=True)
    category_id = fields.Many2one(
        "fix.asset.category", string="Asset Category", help="Leave empty: any category."
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    amount = fields.Monetary(string="Budget Amount", required=True, tracking=True)
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", default=lambda self: self.env.user, readonly=True
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("closed", "Closed")],
        default="draft",
        required=True,
        tracking=True,
    )
    request_ids = fields.One2many("fix.capex.request", "budget_id", string="Capex Requests")
    committed_amount = fields.Monetary(string="Committed", compute="_compute_consumption")
    actual_amount = fields.Monetary(
        string="Actual (CWIP / Capitalised)", compute="_compute_consumption"
    )
    available_amount = fields.Monetary(string="Available", compute="_compute_consumption")
    utilisation_pct = fields.Float(
        string="Utilisation %", compute="_compute_consumption", digits=(5, 1)
    )

    @api.depends("amount", "request_ids.state", "request_ids.amount", "request_ids.actual_cost")
    def _compute_consumption(self):
        for rec in self:
            committed = rec.request_ids.filtered(lambda r: r.state in COMMITTED_STATES)
            rec.committed_amount = money(sum(committed.mapped("amount")))
            rec.actual_amount = money(sum(committed.mapped("actual_cost")))
            rec.available_amount = money(rec.amount - rec.committed_amount)
            rec.utilisation_pct = (
                round(rec.committed_amount / rec.amount * 100.0, 1) if rec.amount else 0.0
            )

    @api.constrains("date_from", "date_to", "amount")
    def _check_budget(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError(self.env._("The budget ends before it starts."))
            if rec.amount <= 0:
                raise ValidationError(self.env._("The budget amount must be above zero."))
            if rec.state != "draft" and rec.amount < rec.committed_amount:
                raise ValidationError(
                    self.env._("The budget cannot drop below the amount already committed.")
                )

    def action_approve(self):
        require_group(self.env, MANAGER_GROUP, "Approving a capital budget")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft budgets can be approved."))
            check_sod(self.env, rec.prepared_by_id, rec.name)
            rec.write({"state": "approved", "approved_by_id": self.env.user.id})
        return True

    def action_close(self):
        require_group(self.env, MANAGER_GROUP, "Closing a capital budget")
        for rec in self:
            if rec.state != "approved":
                raise UserError(self.env._("Only approved budgets can be closed."))
            rec.state = "closed"
        return True


class FixCapexRequest(models.Model):
    _name = "fix.capex.request"
    _description = "Capex Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "request_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Branch", tracking=True)
    name = fields.Char(string="Reference", readonly=True, copy=False, default="/")
    title = fields.Char(string="Title", required=True, tracking=True)
    justification = fields.Text(string="Business Justification")
    request_date = fields.Date(
        string="Request Date", required=True, default=fields.Date.context_today
    )
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user, readonly=True
    )
    category_id = fields.Many2one("fix.asset.category", string="Asset Category", tracking=True)
    life_months = fields.Integer(string="Useful Life (Months)")
    budget_id = fields.Many2one(
        "fix.capex.budget",
        string="Capital Budget",
        domain="[('state', '=', 'approved'), ('company_id', '=', company_id)]",
        tracking=True,
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    amount = fields.Monetary(string="Requested Amount", required=True, tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("cwip", "In CWIP"),
            ("capitalised", "Capitalised"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_date = fields.Date(string="Approval Date", readonly=True, copy=False)
    rejection_reason = fields.Text(string="Rejection Reason")
    cwip_ids = fields.One2many("fix.cwip.entry", "capex_request_id", string="CWIP Projects")
    actual_cost = fields.Monetary(string="Actual Cost", compute="_compute_actual_cost")

    @api.depends("cwip_ids.amount")
    def _compute_actual_cost(self):
        for rec in self:
            rec.actual_cost = money(sum(rec.cwip_ids.mapped("amount")))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.capex.request") or "/"
        return super().create(vals_list)

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(self.env._("The requested amount must be above zero."))

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft requests can be submitted."))
            if not rec.budget_id:
                raise UserError(self.env._("Link %s to a capital budget first.", rec.name))
            rec.state = "submitted"
        return True

    def action_approve(self):
        """Approve within the budget (fail closed on overspend), by an
        accounting manager who did not raise the request."""
        require_group(self.env, MANAGER_GROUP, "Approving a capex request")
        for rec in self:
            if rec.state != "submitted":
                raise UserError(self.env._("Only submitted requests can be approved."))
            check_sod(self.env, rec.requested_by_id, rec.name)
            budget = rec.budget_id
            if budget.state != "approved":
                raise UserError(self.env._("The capital budget %s is not approved.", budget.name))
            if not budget.date_from <= rec.request_date <= budget.date_to:
                raise UserError(self.env._("%s is dated outside the budget period.", rec.name))
            if budget.category_id and rec.category_id != budget.category_id:
                raise UserError(
                    self.env._(
                        "The budget %s is for category %s only.",
                        budget.name,
                        budget.category_id.name,
                    )
                )
            if budget.operating_unit_id and rec.operating_unit_id != budget.operating_unit_id:
                raise UserError(self.env._("The budget %s belongs to another branch.", budget.name))
            if money(rec.amount) > money(budget.available_amount):
                raise UserError(
                    self.env._(
                        "%s (%s) exceeds the budget's available amount (%s).",
                        rec.name,
                        rec.amount,
                        budget.available_amount,
                    )
                )
            rec.write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_date": fields.Date.context_today(rec),
                }
            )
        return True

    def action_reject(self):
        require_group(self.env, MANAGER_GROUP, "Rejecting a capex request")
        for rec in self:
            if rec.state != "submitted":
                raise UserError(self.env._("Only submitted requests can be rejected."))
            rec.state = "rejected"
        return True

    def action_create_cwip(self):
        """Open the CWIP project the request's costs accumulate on."""
        require_group(self.env, USER_GROUP, "Opening a CWIP project")
        cwips = self.env["fix.cwip.entry"]
        for rec in self:
            if rec.state != "approved":
                raise UserError(self.env._("Only approved requests move to CWIP."))
            cwips |= cwips.create(
                {
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                    "name": rec.title,
                    "capex_request_id": rec.id,
                    "category_id": rec.category_id.id,
                    "life_months": rec.life_months or rec.category_id.useful_life_months,
                    "amount": 0.0,
                }
            )
            rec.state = "cwip"
        return {"cwip_ids": cwips.ids}
