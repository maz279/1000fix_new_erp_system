# cd_quotation — M36 Quotation & Estimation (P06-M06-T05/T07, CD-M36-02).
#
# T07: ONE estimate concept, not two — this module EXTENDS M01's
# fix.estimate (AS-01: a single estimate model across the estate) with the
# quotation lifecycle: sent -> negotiated -> accepted/declined, the
# approval loop (CD-M36-03) and tender seam data.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28


class FixEstimate(models.Model):
    """Extend M01's estimate with the M36 quotation lifecycle."""

    _inherit = "fix.estimate"

    quotation_state = fields.Selection(
        [
            ("internal", "Internal Estimate"),
            ("quoted", "Quoted to Customer"),
            ("negotiating", "Negotiating"),
            ("accepted", "Accepted"),
            ("declined", "Declined"),
        ],
        string="Quotation State",
        default="internal",
        tracking=True,
        help="M01 created the estimate; M36 quotes it — one record, one lifecycle",
    )
    valid_days = fields.Integer(
        default=15,
        help="Quotation validity window in days (BRU-SRM-13: "
        "expired estimates are re-issued, never extended)",
    )
    sent_at = fields.Datetime(readonly=True)
    accepted_at = fields.Datetime(readonly=True)
    approval_ids = fields.One2many(
        "fix.discount.approval", "quotation_id", string="Discount Approvals"
    )
    tender_ref = fields.Char(
        string="Tender Reference",
        index=True,
        help="Tender management seam (CD-M36-05, P04 portal W4+)",
    )

    def action_quote(self):
        for estimate in self:
            if estimate.state != "approved":
                raise UserError("Only an approved estimate can be quoted (one concept, one flow)")
            pending = estimate.approval_ids.filtered(lambda a: a.state == "pending")
            if pending:
                raise UserError("A pending discount approval blocks quoting")
            estimate.write({"quotation_state": "quoted", "sent_at": fields.Datetime.now()})
            publish(
                self.env,
                "quotation.sent",
                "fix.estimate",
                estimate.id,
                {
                    "version": estimate.version,
                    "grand_total": estimate.grand_total,
                    "valid_days": estimate.valid_days,
                },
            )

    def action_accept(self):
        for estimate in self:
            if estimate.quotation_state not in ("quoted", "negotiating"):
                raise UserError("Only a quoted quotation can be accepted")
            estimate.write({"quotation_state": "accepted", "accepted_at": fields.Datetime.now()})
            publish(
                self.env,
                "quotation.accepted",
                "fix.estimate",
                estimate.id,
                {
                    "version": estimate.version,
                    "grand_total": estimate.grand_total,
                },
            )

    def action_decline(self):
        for estimate in self:
            estimate.quotation_state = "declined"

    @api.constrains("valid_days")
    def _check_validity(self):
        for estimate in self:
            if estimate.valid_days <= 0:
                raise UserError("The quotation validity window must be positive")


class FixDiscountApproval(models.Model):
    """T03 (P06-M06): discount governance — an agent-entered discount above
    the delegated authority requires approval BEFORE the quote is sent. A
    segregation-of-duties control attached to the unified estimate."""

    _name = "fix.discount.approval"
    _description = "Discount Approval"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]

    # A03 audit R7: a discount above the agent's 5% is approved from the
    # approver's M63 inbox (Request Approval), not by pressing Approve.
    _approval_domain = "discount"
    _approval_apply_method = "action_approve"
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    quotation_id = fields.Many2one(
        "fix.estimate", string="Quotation", required=True, ondelete="cascade"
    )
    discount_pct = fields.Float(string="Discount (%)", required=True)
    justification = fields.Text(required=True)
    state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
        required=True,
        tracking=True,
    )
    approved_by = fields.Many2one("res.users", readonly=True)
    rejection_reason = fields.Char(readonly=True)
    # Authority matrix (05-04 section 7): agent 5%, branch manager 10%,
    # above that the commercial director.
    AGENT_MAX = 5.0
    MANAGER_MAX = 10.0

    def _fix_guarded_fields(self) -> set:
        # A 15% approval was set by writing state='approved' (A03 audit).
        return super()._fix_guarded_fields() | {"state", "approved_by", "rejection_reason"}

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.discount_pct <= self.AGENT_MAX:
                rec._guarded().write({"state": "approved"})  # within delegated authority
        return records

    def _approval_needed(self) -> bool:
        return self.state == "pending" and self.discount_pct > self.AGENT_MAX

    def _approval_amount(self) -> float:
        return self.discount_pct

    def _approval_group_xmlid(self):
        if self.discount_pct > self.MANAGER_MAX:
            return "cd_entity_config.group_dofa_tier_3"
        return "cd_entity_config.group_dofa_tier_2"

    def _approval_on_rejected(self, comment):
        for approval in self.filtered(lambda a: a.state == "pending"):
            approval._guarded().write({"state": "rejected", "rejection_reason": comment})

    def action_approve(self):
        self._approval_assert_routed()
        for approval in self:
            if approval.state != "pending":
                raise UserError("Only a pending discount request can be approved")
            # 5-10% is the branch manager's; above that the commercial
            # director's. It was "anyone" and "base.group_system" (an IT
            # admin role), with no segregation of duties (A03 audit).
            needed = (
                "cd_entity_config.group_dofa_tier_3"
                if approval.discount_pct > self.MANAGER_MAX
                else "cd_entity_config.group_dofa_tier_2"
            )
            # A delegate decides with the absent approver's authority.
            if not approval._approval_authority_user().has_group(needed):
                if approval.discount_pct > self.MANAGER_MAX:
                    raise UserError(
                        "Discounts above %.1f%% require commercial-director approval "
                        "(DOFA Tier 3)" % self.MANAGER_MAX
                    )
                raise UserError(
                    "Discounts above %.1f%% require branch-manager approval (DOFA Tier 2)"
                    % self.AGENT_MAX
                )
            if approval.create_uid in approval._approval_acting_users():
                raise UserError(
                    "Segregation of duties: you requested this discount, so someone "
                    "else must approve it."
                )
            approval._guarded().write({"state": "approved", "approved_by": self.env.user.id})
            publish(
                self.env,
                "discount.approved",
                "fix.discount.approval",
                approval.id,
                {"pct": approval.discount_pct},
            )

    def action_reject(self, reason=None):
        """There was no way to refuse a discount request. Since R7 a rejection
        is an approver's decision, taken from their M63 inbox."""
        self._approval_assert_routed()
        if not (reason or "").strip():
            raise UserError("A rejected discount request needs its reason")
        for approval in self:
            if approval.state != "pending":
                raise UserError("Only a pending discount request can be rejected")
            approval._guarded().write({"state": "rejected", "rejection_reason": reason})
