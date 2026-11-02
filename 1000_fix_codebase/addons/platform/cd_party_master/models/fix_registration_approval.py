# fix.registration.approval — multi-tier registration approval (M33,
# FR-CPM-010, BRU-CPM-02). Dealer, corporate and government accounts
# transact only after the client's OWN line manager AND a 1000FiX
# administrator have both approved (Service App SOW).
from odoo import fields, models
from odoo.exceptions import ValidationError


class FixRegistrationApproval(models.Model):
    """The two-tier approval chain for a dealer / corporate / government
    party: client line manager first, 1000FiX administrator second."""

    _name = "fix.registration.approval"
    _description = "Registration Approval"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "requested_at desc, id desc"

    partner_id = fields.Many2one(
        "res.partner", string="Party", required=True, ondelete="cascade", index=True
    )
    party_class = fields.Selection(
        [
            ("dealer", "Dealer"),
            ("corporate", "Corporate"),
            ("government", "Government"),
        ],
        string="Party Class",
        required=True,
        tracking=True,
    )
    lm_state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        string="Client Line Manager",
        default="pending",
        required=True,
        tracking=True,
    )
    admin_state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        string="1000FiX Administrator",
        default="pending",
        required=True,
        tracking=True,
    )
    requested_at = fields.Datetime(
        string="Requested At", default=fields.Datetime.now, readonly=True
    )
    lm_decided_by = fields.Many2one("res.users", string="LM Decided By", readonly=True)
    lm_decided_at = fields.Datetime(string="LM Decided At", readonly=True)
    admin_decided_by = fields.Many2one("res.users", string="Admin Decided By", readonly=True)
    admin_decided_at = fields.Datetime(string="Admin Decided At", readonly=True)
    reason = fields.Char(string="Reason / Notes")
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    def _fully_approved(self) -> bool:
        return self.lm_state == "approved" and self.admin_state == "approved"

    def action_lm_approve(self):
        for approval in self:
            if approval.lm_state != "pending":
                raise ValidationError("The line-manager step is already %s" % approval.lm_state)
            approval.write(
                {
                    "lm_state": "approved",
                    "lm_decided_by": self.env.user.id,
                    "lm_decided_at": fields.Datetime.now(),
                }
            )
            approval._activate_if_complete()
        return True

    def action_admin_approve(self):
        for approval in self:
            # BRU-CPM-02: the administrator acts only AFTER the client's own
            # line manager — one approval step is not enough.
            if approval.lm_state != "approved":
                raise ValidationError(
                    "The client line manager must approve before the 1000FiX "
                    "administrator (BRU-CPM-02)"
                )
            if approval.admin_state != "pending":
                raise ValidationError("The administrator step is already %s" % approval.admin_state)
            approval.write(
                {
                    "admin_state": "approved",
                    "admin_decided_by": self.env.user.id,
                    "admin_decided_at": fields.Datetime.now(),
                }
            )
            approval._activate_if_complete()
        return True

    def action_reject(self, reason=None):
        if not reason:
            raise ValidationError("A rejection needs its reason")
        for approval in self:
            approval.write({"lm_state": "rejected", "admin_state": "rejected", "reason": reason})
        return True

    def _activate_if_complete(self):
        """Both tiers approved → the party may transact (party.activated)."""
        for approval in self:
            if approval._fully_approved() and approval.partner_id.party_status in (
                "draft",
                "pending_approval",
            ):
                approval.partner_id.write({"party_status": "active"})
                from libs.py.fix_events import publish

                publish(
                    self.env,
                    "party.activated",
                    "res.partner",
                    approval.partner_id.id,
                    {"party_class": approval.party_class, "chain": "line_manager+administrator"},
                )
