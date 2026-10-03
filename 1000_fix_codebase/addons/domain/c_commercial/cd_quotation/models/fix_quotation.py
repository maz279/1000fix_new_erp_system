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
        [("internal", "Internal Estimate"), ("quoted", "Quoted to Customer"),
         ("negotiating", "Negotiating"), ("accepted", "Accepted"),
         ("declined", "Declined")],
        string="Quotation State", default="internal", tracking=True,
        help="M01 created the estimate; M36 quotes it — one record, one lifecycle")
    valid_days = fields.Integer(default=15,
                                help="Quotation validity window in days (BRU-SRM-13: "
                                     "expired estimates are re-issued, never extended)")
    sent_at = fields.Datetime(readonly=True)
    accepted_at = fields.Datetime(readonly=True)
    approval_ids = fields.One2many("fix.discount.approval", "quotation_id",
                                   string="Discount Approvals")
    tender_ref = fields.Char(string="Tender Reference", index=True,
                             help="Tender management seam (CD-M36-05, P04 portal W4+)")

    def action_quote(self):
        for estimate in self:
            if estimate.state != "approved":
                raise UserError("Only an approved estimate can be quoted (one concept, one flow)")
            pending = estimate.approval_ids.filtered(lambda a: a.state == "pending")
            if pending:
                raise UserError("A pending discount approval blocks quoting")
            estimate.write({"quotation_state": "quoted", "sent_at": fields.Datetime.now()})
            publish(self.env, "quotation.sent", "fix.estimate", estimate.id, {
                "version": estimate.version,
                "grand_total": estimate.grand_total,
                "valid_days": estimate.valid_days,
            })

    def action_accept(self):
        for estimate in self:
            if estimate.quotation_state not in ("quoted", "negotiating"):
                raise UserError("Only a quoted quotation can be accepted")
            estimate.write({"quotation_state": "accepted",
                            "accepted_at": fields.Datetime.now()})
            publish(self.env, "quotation.accepted", "fix.estimate", estimate.id, {
                "version": estimate.version,
                "grand_total": estimate.grand_total,
            })

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
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    quotation_id = fields.Many2one("fix.estimate", string="Quotation",
                                   required=True, ondelete="cascade")
    discount_pct = fields.Float(string="Discount (%)", required=True)
    justification = fields.Text(required=True)
    state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending", required=True, tracking=True)
    approved_by = fields.Many2one("res.users", readonly=True)
    # Authority matrix (05-04 section 7): agent 5%, branch manager 10%,
    # above that the commercial director.
    AGENT_MAX = 5.0
    MANAGER_MAX = 10.0

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.discount_pct <= self.AGENT_MAX:
                rec.state = "approved"  # within delegated authority
        return records

    def action_approve(self):
        for approval in self:
            if approval.discount_pct > self.MANAGER_MAX and not self.env.user.has_group(
                    "base.group_system"):
                raise UserError(
                    "Discounts above %.1f%% require commercial-director approval"
                    % self.MANAGER_MAX)
            approval.write({"state": "approved", "approved_by": self.env.user.id})
            publish(self.env, "discount.approved", "fix.discount.approval",
                    approval.id, {"pct": approval.discount_pct})
