# fix.consent — the consent registry (P03-M05, M33; NT-002 companion).
# Marketing consent and channel preferences are AUDITABLE obligations, not
# profile conveniences: every grant, withdrawal and proof lives here with its
# dates. The notification dispatcher's RecipientState is the projection of
# this table — never a separate source of truth.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixConsent(models.Model):
    """One consent decision: what was consented, on which channel, when, proof."""
    _name = "fix.consent"
    _description = "Consent Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "partner_id, channel, date_granted desc"

    partner_id = fields.Many2one("res.partner", string="Party", required=True,
                                 ondelete="cascade", index=True)
    channel = fields.Selection(
        [("sms", "SMS"), ("whatsapp", "WhatsApp"), ("email", "Email"),
         ("push", "Push"), ("marketing", "Marketing (all channels)")],
        string="Channel", required=True)
    state = fields.Selection(
        [("granted", "Granted"), ("withdrawn", "Withdrawn"), ("expired", "Expired")],
        string="State", required=True, default="granted", tracking=True)
    date_granted = fields.Datetime(string="Granted At", default=fields.Datetime.now)
    date_withdrawn = fields.Datetime(string="Withdrawn At", readonly=True)
    proof = fields.Char(string="Proof Reference",
                        help="Where the consent came from: signed form ID, "
                             "OTP-verified session, legacy import batch — "
                             "an unverifiable grant is not a grant")
    source = fields.Selection(
        [("web", "Web Portal"), ("otp", "OTP-Verified"), ("form", "Paper Form"),
         ("legacy", "Legacy Import"), ("agent", "Agent Captured")],
        string="Source", default="web")
    company_id = fields.Many2one("res.company", string="Company", required=True,
                                 default=lambda self: self.env.company)

    def action_withdraw(self):
        """Withdraw today, keep the record forever — an auditable trail,
        not a deleted row (the BTRC/DND obligation outlives the account)."""
        self.write({"state": "withdrawn",
                    "date_withdrawn": fields.Datetime.now()})
        return True

    @api.constrains("state", "proof")
    def _check_proof_on_grant(self):
        for consent in self:
            if consent.state == "granted" and not consent.proof:
                raise ValidationError(
                    "A granted consent needs its proof reference — "
                    "an unverifiable grant is not a grant")
