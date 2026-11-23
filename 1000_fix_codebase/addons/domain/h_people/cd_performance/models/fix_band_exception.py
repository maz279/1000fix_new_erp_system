# cd_performance — M57-F18 / decision D27 (owner, 2026-11-23).
#
# An out-of-band monthly gross was a hard refusal ("the Compensation Manager
# must change the band first") while an M58 offer over the band could already be
# approved by the CFO tier — so the hire's contract then failed at activation.
# The owner's decision: the CFO tier approves the exception once, with a reason,
# for a named employee and grade and a maximum gross, and the band check lets
# that contract or compensation proposal through.
#
# Routing, the "never your own record" rule and the subject exclusion come from
# the A09 approval spine (fix.people.approval.mixin -> the M63 inbox), so the
# requester cannot approve their own exception and nothing decides without a
# task.
from odoo import api, fields, models
from odoo.exceptions import UserError

CFO_TIER = "cd_entity_config.group_dofa_tier_4"
COMPENSATION = "cd_performance.group_compensation"


class FixBandException(models.Model):
    _name = "fix.band.exception"
    _description = "Above-Band Salary Exception (CFO tier)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.people.approval.mixin"]
    _order = "create_date desc"

    _approval_domain = "hr_incentive"
    _approval_apply_method = "action_approve"
    _approval_group = CFO_TIER

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    employee_id = fields.Many2one("hr.employee", required=True, index=True, ondelete="cascade")
    grade = fields.Char(
        required=True,
        help="The compensation grade whose band the approved gross exceeds.",
    )
    approved_monthly_gross = fields.Float(
        string="Monthly Gross Allowed Up To",
        required=True,
        help="The contract or proposal gross this exception covers: any figure up to it "
        "passes the band check for this employee and grade.",
    )
    reason = fields.Text(required=True)
    contract_id = fields.Many2one(
        "fix.employment.contract",
        string="Contract",
        index=True,
        help="The contract this exception lets through (empty for a proposal-only exception).",
    )
    proposal_id = fields.Many2one(
        "fix.compensation.proposal", string="Compensation Proposal", index=True
    )
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("cancelled", "Cancelled")],
        required=True,
        default="draft",
        tracking=True,
    )
    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_on = fields.Datetime(readonly=True, copy=False)
    cancel_reason = fields.Char(readonly=True, copy=False)

    _gross_positive = models.Constraint(
        "CHECK (approved_monthly_gross > 0)", "An exception allows a positive monthly gross."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "approved_by_id",
            "approved_on",
            "cancel_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" for r in self):
            locked |= {"employee_id", "grade", "approved_monthly_gross", "reason"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.band.exception") or "BEX/New"
                )
        return super().create(vals_list)

    # ---- the decision (routed; the CFO tier decides from the inbox) -----------
    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft exception is sent for approval.")
            if not (rec.reason or "").strip():
                raise UserError("State why the salary is above the band.")
        self._guarded().write({"requested_by_id": self.env.user.id})
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """Run by the approval engine from an inbox task: the CFO tier approves."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft exception.")
        self._guarded().write(
            {
                "state": "approved",
                "approved_by_id": self.env.user.id,
                "approved_on": fields.Datetime.now(),
            }
        )
        return True

    def action_cancel(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Say why the exception is withdrawn.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Withdraw a draft exception (%s is %s)." % (rec.name, rec.state))
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason.strip()})
        return True

    # ---- what it covers --------------------------------------------------------
    def _fix_covers(self, gross, grade=None):
        """Does this approved exception let `gross` through for `grade`?"""
        self.ensure_one()
        if self.state != "approved":
            return False
        if grade and self.grade and self.grade.strip().lower() != str(grade).strip().lower():
            return False
        return float(gross or 0.0) <= float(self.approved_monthly_gross or 0.0)

    @api.model
    def _fix_covering(self, employee, grade, gross, contract=None, proposal=None):
        """The approved exception (if any) that covers this employee's gross.

        An exception linked to the contract (or the proposal) wins; otherwise
        an unlinked one for the employee and grade covers any contract or
        proposal within its figure - the raise case, where the proposal does
        not exist yet when the band check first runs.
        """
        recs = self.sudo().search([("state", "=", "approved"), ("employee_id", "=", employee.id)])
        covering = recs.filtered(lambda r: r._fix_covers(gross, grade))
        for rec in covering:
            if contract is not None and rec.contract_id == contract:
                return rec
            if proposal is not None and rec.proposal_id == proposal:
                return rec
        general = covering.filtered(lambda r: not r.contract_id and not r.proposal_id)
        return general[:1]
