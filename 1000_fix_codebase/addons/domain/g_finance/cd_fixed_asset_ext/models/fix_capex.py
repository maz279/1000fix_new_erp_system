# fix_capex — M49 capital budget and capex requests.
#
# Capital budget (approved by an accounting manager, SoD) -> capex request
# (draft -> submitted -> approved through the M63 inbox by the DOFA tier the
# amount needs, never by the requester, and only within the budget's
# available amount) -> CWIP project -> capitalised asset. The budget's
# consumption is computed from the approved requests (committed) and from the
# CWIP cost booked against them (actual).
#
# A08 workflow audit (2026-11-04): an accountant wrote state='approved' on a
# request with no budget (M49-1), a manager rewrote requested_by_id and
# approved his own (M49-5), the amount was raised 100,000 -> 900,000 after
# approval (M49-4) and 50,000,000 was approved by one manager (M49-6). The
# workflow fields are guarded, the approved terms are frozen, and approval
# is routed by amount (fix.asset.dofa.mixin).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_asset_common import (
    MANAGER_GROUP,
    USER_GROUP,
    capex_ladder,
    check_sod,
    money,
    require_group,
)

COMMITTED_STATES = ("approved", "cwip", "capitalised")


class FixCapexBudget(models.Model):
    _name = "fix.capex.budget"
    _description = "Capital Budget"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
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

    _TERMS = frozenset(
        {"amount", "date_from", "date_to", "category_id", "operating_unit_id", "company_id"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_by_id", "prepared_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._TERMS)
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open() and set(vals) & self._TERMS:
            done = self.filtered(lambda b: b.state != "draft")
            if any(
                b._fix_guard_differs(n, vals[n], b[n])
                for b in done
                for n in set(vals) & self._TERMS
            ):
                raise UserError(
                    self.env._("An approved capital budget's amount and scope are frozen.")
                )
        return super().write(vals)

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
            check_sod(self.env, rec.prepared_by_id, rec.name, rec)
            rec._guarded().write({"state": "approved", "approved_by_id": self.env.user.id})
        return True

    def action_close(self):
        require_group(self.env, MANAGER_GROUP, "Closing a capital budget")
        for rec in self:
            if rec.state != "approved":
                raise UserError(self.env._("Only approved budgets can be closed."))
            rec._guarded().write({"state": "closed"})
        return True


class FixCapexRequest(models.Model):
    _name = "fix.capex.request"
    _description = "Capex Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.asset.dofa.mixin"]
    _order = "request_date desc, id desc"
    _approval_domain = "capex_request"

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

    _TERMS = frozenset(
        {
            "amount",
            "budget_id",
            "category_id",
            "operating_unit_id",
            "company_id",
            "request_date",
            "life_months",
        }
    )

    # ---- DOFA --------------------------------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return abs(self.amount or 0.0)

    def _dofa_thresholds(self):
        return capex_ladder(self.env)

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (capex request %s)" % (self._dofa_amount(), self.name)

    @api.depends("amount")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _fix_terms_fields(self) -> set:
        return set(self._TERMS)

    # ---- guard -------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_date",
            "requested_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state not in ("draft", "rejected"):
            locked |= set(self._TERMS)
        return locked

    def write(self, vals):
        moving = set(vals) & self._TERMS
        if self and moving and not self._fix_guard_open():
            frozen = self.filtered(lambda r: r.state not in ("draft", "rejected"))
            if any(r._fix_guard_differs(n, vals[n], r[n]) for r in frozen for n in moving):
                raise UserError(
                    self.env._(
                        "%s is %s: its amount, budget and scope are what was submitted / "
                        "approved and are frozen. Raise a supplementary request.",
                        frozen[:1].name,
                        frozen[:1].state,
                    )
                )
        return super().write(vals)

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

    def _check_budget_headroom(self):
        """The budget checks that hold at submission and again at approval."""
        self.ensure_one()
        budget = self.budget_id.sudo()
        if not budget:
            raise UserError(self.env._("Link %s to a capital budget first.", self.name))
        if budget.state != "approved":
            raise UserError(self.env._("The capital budget %s is not approved.", budget.name))
        if not budget.date_from <= self.request_date <= budget.date_to:
            raise UserError(self.env._("%s is dated outside the budget period.", self.name))
        if budget.category_id and self.category_id != budget.category_id:
            raise UserError(
                self.env._(
                    "The budget %s is for category %s only.", budget.name, budget.category_id.name
                )
            )
        if budget.operating_unit_id and self.operating_unit_id != budget.operating_unit_id:
            raise UserError(self.env._("The budget %s belongs to another branch.", budget.name))
        if money(self.amount) > money(budget.available_amount):
            raise UserError(
                self.env._(
                    "%s (%s) exceeds the budget's available amount (%s).",
                    self.name,
                    self.amount,
                    budget.available_amount,
                )
            )

    def action_submit(self):
        """Submit within the budget and route the approval by amount."""
        require_group(self.env, USER_GROUP, "Submitting a capex request")
        for rec in self:
            if rec.state not in ("draft", "rejected"):
                raise UserError(self.env._("Only draft requests can be submitted."))
            rec._check_budget_headroom()
            if not (rec.justification or "").strip():
                raise UserError(self.env._("Write the business justification of %s.", rec.name))
            rec._guarded().write({"state": "submitted"})
            if rec._approval_needed():
                rec.action_request_approval(justification=rec.justification)
        return True

    def _fix_before_approve(self):
        if self.state != "submitted":
            raise UserError(self.env._("Only submitted requests can be approved."))
        check_sod(self.env, self.requested_by_id, self.name, self)
        self._check_budget_headroom()

    def _fix_after_approve(self):
        self._fix_stamp_approved({"state": "approved", "approved_date": self._fix_approval_date()})

    def _approval_on_rejected(self, comment):
        self.sudo()._guarded().write({"state": "rejected", "rejection_reason": comment or False})

    def action_reject(self):
        require_group(self.env, MANAGER_GROUP, "Rejecting a capex request")
        for rec in self:
            if rec.state != "submitted":
                raise UserError(self.env._("Only submitted requests can be rejected."))
            check_sod(self.env, rec.requested_by_id, rec.name, rec)
            if rec.approval_state == "pending":
                rec.sudo()._approval_void("the request was rejected")
            rec._guarded().write({"state": "rejected"})
        return True

    def _fix_assert_approved(self, what):
        for rec in self:
            if rec.state not in ("approved", "cwip", "capitalised"):
                raise UserError(
                    self.env._(
                        "%s needs an approved capex request (%s is %s).", what, rec.name, rec.state
                    )
                )
            if rec._approval_needed() and not rec.dofa_approved:
                raise UserError(self.env._("%s: %s carries no DOFA approval.", what, rec.name))
            rec._dofa_assert_approved(what)

    def action_create_cwip(self):
        """Open the CWIP project the request's costs accumulate on."""
        require_group(self.env, USER_GROUP, "Opening a CWIP project")
        cwips = self.env["fix.cwip.entry"]
        for rec in self:
            if rec.state != "approved":
                raise UserError(self.env._("Only approved requests move to CWIP."))
            rec._fix_assert_approved("Opening a CWIP project")
            cwips |= cwips.create(
                {
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                    "name": rec.title,
                    "capex_request_id": rec.id,
                    "category_id": rec.category_id.id,
                    "life_months": rec.life_months or rec.category_id.useful_life_months,
                }
            )
            rec._guarded().write({"state": "cwip"})
        return {"cwip_ids": cwips.ids}
