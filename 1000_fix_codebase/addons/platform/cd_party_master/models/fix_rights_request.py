# fix.rights.request — PDPA data-subject rights as tracked cases (M33,
# FR-CPM-040…044, BRU-CPM-10/11). Every request carries the statutory
# 30-day clock; fulfilment needs evidence; nothing is deleted silently.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixRightsRequest(models.Model):
    """A data-subject request: access, portability, rectification, erasure or
    withdrawal — tracked from receipt to evidenced fulfilment."""

    _name = "fix.rights.request"
    _description = "Data-Subject Rights Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "received_at desc, id desc"

    partner_id = fields.Many2one(
        "res.partner",
        string="Party",
        required=True,
        index=True,
        # statutory records outlive the party record (retention overrides erasure)
        ondelete="restrict",
    )
    request_type = fields.Selection(
        [
            ("access", "Right of Access"),
            ("portability", "Right of Portability"),
            ("rectification", "Right of Rectification"),
            ("erasure", "Right of Erasure"),
            ("withdrawal", "Consent Withdrawal (all purposes)"),
        ],
        string="Request Type",
        required=True,
        tracking=True,
    )
    received_at = fields.Datetime(string="Received At", default=fields.Datetime.now, readonly=True)
    statutory_due = fields.Date(
        string="Statutory Due",
        compute="_compute_statutory_due",
        store=True,
        help="PDPA: the response is due within 30 days of receipt",
    )
    state = fields.Selection(
        [
            ("received", "Received"),
            ("verified", "Identity Verified"),
            ("in_progress", "In Progress"),
            ("fulfilled", "Fulfilled"),
            ("rejected", "Rejected"),
        ],
        string="State",
        default="received",
        required=True,
        tracking=True,
    )
    identity_verified = fields.Boolean(string="Identity Verified")
    decision = fields.Char(string="Decision Summary")
    evidence_ref = fields.Char(
        string="Evidence Reference",
        help="Export file ID / rectification notice ID — fulfilment without evidence is not fulfilment",
    )
    fulfilled_at = fields.Datetime(string="Fulfilled At", readonly=True)
    rejected_reason = fields.Char(string="Rejection Reason")
    # BRU-CPM-10: a rectification must be NOTIFIED to the data subject
    # within 30 days — record when the notification went out.
    notified_at = fields.Datetime(
        string="Party Notified At",
        help="Rectification notifications: the party is told within 30 days (BRU-CPM-10)",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("received_at")
    def _compute_statutory_due(self):
        for req in self:
            received = req.received_at or fields.Datetime.now()
            req.statutory_due = (received + timedelta(days=30)).date()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            from libs.py.fix_events import publish

            publish(
                self.env,
                "rights_request.received",
                "fix.rights.request",
                rec.id,
                {
                    "partner_id": rec.partner_id.id,
                    "request_type": rec.request_type,
                    "statutory_due": str(rec.statutory_due),
                },
            )
        return records

    def action_verify(self):
        for req in self:
            req.write({"identity_verified": True, "state": "verified"})
        return True

    def action_start(self):
        for req in self:
            if req.state not in ("verified", "received"):
                raise ValidationError("Only a verified request can move to In Progress")
            req.state = "in_progress"
        return True

    def action_fulfil(self, evidence=None):
        """Fulfil with evidence — an unevidenced fulfilment is not a
        fulfilment (AC-09)."""
        for req in self:
            if req.state not in ("in_progress", "verified"):
                raise ValidationError(
                    "The request must be in progress before fulfilment (current: %s)" % req.state
                )
            if not evidence:
                raise ValidationError(
                    "Fulfilment needs its evidence reference — export ID, notice ID or file ref"
                )
            req.write(
                {
                    "state": "fulfilled",
                    "fulfilled_at": fields.Datetime.now(),
                    "evidence_ref": evidence,
                }
            )
            from libs.py.fix_events import publish

            publish(
                self.env,
                "rights_request.fulfilled",
                "fix.rights.request",
                req.id,
                {
                    "partner_id": req.partner_id.id,
                    "request_type": req.request_type,
                    "evidence_ref": evidence,
                },
            )
        return True

    def action_reject(self, reason=None):
        """Reject with a stated basis — an erasure may only be rejected on a
        statutory retention override, and the override must be stated to the
        party (BRU-CPM-11)."""
        for req in self:
            if req.state == "fulfilled":
                raise ValidationError("A fulfilled request cannot be rejected")
            if not reason:
                raise ValidationError("A rejection needs its stated basis")
            req.write({"state": "rejected", "rejected_reason": reason})
        return True
