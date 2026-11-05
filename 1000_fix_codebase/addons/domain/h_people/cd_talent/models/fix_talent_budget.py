# fix_talent_budget — M58: the approved headcount budget (BRU-TAO-01,
# FR-TAO-002, AC-01).
#
# A09 audit M58-F3: a requisition had no budget to be checked against. The
# spec puts the headcount budget with M54 FP&A, which has no headcount model
# in this repository, so the budget is kept here: an approved headcount per
# position (or per department) and year, approved from the CFO tier's inbox
# by someone other than its requester. A requisition that would take its
# scope beyond the approved figure is refused, unless it carries a
# justification, in which case the CFO tier decides it (fix_talent.py).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_talent import CFO_GROUP, _require_recruiter


class FixHeadcountBudget(models.Model):
    _name = "fix.headcount.budget"
    _description = "Approved Headcount Budget"
    _inherit = ["mail.thread", "fix.people.approval.mixin"]
    _order = "year desc, id desc"

    _approval_domain = "hr_requisition"
    _approval_apply_method = "action_approve"
    _approval_group = CFO_GROUP

    _TERMS = ("company_id", "year", "position_id", "department_id", "approved_headcount")

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    year = fields.Integer(
        required=True, default=lambda self: fields.Date.context_today(self).year, index=True
    )
    position_id = fields.Many2one("fix.org.position", string="Position", index=True)
    department_id = fields.Many2one("hr.department", string="Department", index=True)
    approved_headcount = fields.Integer(
        string="Budgeted Headcount",
        required=True,
        help="The headcount the scope may reach in the year: people in post plus open "
        "requisitions.",
    )
    basis = fields.Text(string="Budget Basis", help="Where the figure comes from (M54 plan).")
    used_headcount = fields.Integer(compute="_compute_used", string="In Post + Open")
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_on = fields.Datetime(readonly=True, copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("closed", "Closed")],
        required=True,
        default="draft",
        tracking=True,
    )

    _positive = models.Constraint(
        "CHECK (approved_headcount >= 0)", "A headcount budget is not negative"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_by_id", "approved_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" or r.approval_state == "pending" for r in self):
            locked |= set(self._TERMS)
        return locked

    @api.depends("year", "position_id", "department_id")
    def _compute_name(self):
        for rec in self:
            scope = rec.position_id.name or rec.department_id.name or "?"
            rec.name = "%s %s" % (scope, rec.year or "")

    def _compute_used(self):
        Req = self.env["fix.job.requisition"].sudo()
        for rec in self:
            if rec.position_id:
                scope = [("position_id", "=", rec.position_id.id)]
                held = len(rec.position_id.sudo().employee_ids)
            elif rec.department_id:
                scope = [("department_id", "=", rec.department_id.id)]
                held = self.env["hr.employee"].sudo().search_count(scope)
            else:
                rec.used_headcount = 0
                continue
            reqs = Req.search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("budget_year", "=", rec.year),
                    ("state", "=", "open"),
                    *scope,
                ]
            )
            rec.used_headcount = held + sum(reqs.mapped("openings_left"))

    @api.constrains("position_id", "department_id", "year", "company_id", "state")
    def _check_scope(self):
        for rec in self:
            if bool(rec.position_id) == bool(rec.department_id):
                raise ValidationError(
                    "A headcount budget is for one position or one department, not both."
                )
            if rec.state == "closed":
                continue
            twin = self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("year", "=", rec.year),
                    ("position_id", "=", rec.position_id.id or False),
                    ("department_id", "=", rec.department_id.id or False),
                    ("state", "!=", "closed"),
                ]
            )
            if twin:
                raise ValidationError(
                    "%s already has a headcount budget for %d." % (rec.name, rec.year)
                )

    def write(self, vals):
        terms = set(self._TERMS) & set(vals)
        if terms and not self._fix_guard_open():
            for rec in self:
                if (rec.state != "draft" or rec.approval_state == "pending") and any(
                    rec._fix_guard_differs(n, vals[n], rec[n]) for n in terms
                ):
                    raise UserError(
                        "Headcount budget %s is %s; a new figure is a new budget."
                        % (
                            rec.name,
                            "awaiting approval" if rec.state == "draft" else rec.state,
                        )
                    )
        return super().write(vals)

    def action_request_approval(self, justification=None):
        _require_recruiter(self.env, "submit a headcount budget")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Submit a draft headcount budget.")
            if not (rec.basis or "").strip():
                raise UserError("State the basis of the budgeted headcount of %s." % rec.name)
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """Routed apply method: the CFO tier approves the budget."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft headcount budget.")
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": rec._people_decider().id,
                    "approved_on": fields.Datetime.now(),
                }
            )
        return True

    def action_close(self):
        _require_recruiter(self.env, "close a headcount budget")
        self.filtered(lambda r: r.state == "approved")._guarded().write({"state": "closed"})
        return True
