# fix.otp.log — contact-point verification events (M33, FR-CPM-022).
# M33 records the verification EVENT; the code itself is issued and checked
# by the channel owner (M27 contact centre / portal) — the raw code and the
# raw destination are NEVER stored here, only the masked destination and the
# outcome.
from odoo import fields, models


class FixOtpLog(models.Model):
    """One OTP verification attempt on a mobile number or email address."""

    _name = "fix.otp.log"
    _description = "OTP Verification Log"
    _order = "requested_at desc, id desc"

    partner_id = fields.Many2one(
        "res.partner", string="Party", required=True, ondelete="cascade", index=True
    )
    channel = fields.Selection(
        [("mobile", "Mobile (SMS)"), ("email", "Email")],
        string="Channel",
        required=True,
    )
    destination_masked = fields.Char(
        string="Destination (masked)",
        help="Masked destination — the raw phone/email is PII and is not "
        "recorded on the log (e.g. 01***4471)",
    )
    state = fields.Selection(
        [("pending", "Pending"), ("verified", "Verified"), ("expired", "Expired")],
        string="State",
        default="pending",
        required=True,
    )
    requested_at = fields.Datetime(
        string="Requested At", default=fields.Datetime.now, readonly=True
    )
    verified_at = fields.Datetime(string="Verified At", readonly=True)
    channel_ref = fields.Char(
        string="Channel Reference",
        help="M27 message/dispatch reference for the code that was sent",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    def action_mark_verified(self, channel_ref=None):
        """Record a successful verification — emits contact_point.verified so
        M27/M35 refresh their channel state (spec §12.3)."""
        for log in self:
            log.write(
                {
                    "state": "verified",
                    "verified_at": fields.Datetime.now(),
                    "channel_ref": channel_ref or log.channel_ref,
                }
            )
            from libs.py.fix_events import publish

            publish(
                self.env,
                "contact_point.verified",
                "res.partner",
                log.partner_id.id,
                {"channel": log.channel},
            )
        return True

    def action_expire(self):
        self.write({"state": "expired"})
        return True
