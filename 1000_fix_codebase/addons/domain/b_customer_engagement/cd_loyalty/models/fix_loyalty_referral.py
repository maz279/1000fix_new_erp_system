# M10 · Referral codes — the acquisition hook of the loyalty programme.
# A code belongs to a referrer; conversion is recorded when the referee's
# first qualifying service posts. Nothing is auto-awarded: the ledger line is
# the evidence and the referral only stores the outcome.
from odoo import fields, models
from odoo.exceptions import UserError


class FixLoyaltyReferralCode(models.Model):
    _name = "fix.loyalty.referral.code"
    _description = "Loyalty Referral Code"
    _order = "create_date desc, id desc"

    name = fields.Char(string="Referral Code", required=True, index=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    program_id = fields.Many2one("fix.loyalty.program", required=True, ondelete="restrict")
    referrer_partner_id = fields.Many2one(
        "res.partner", string="Referrer", required=True, index=True, ondelete="restrict"
    )
    referee_partner_id = fields.Many2one(
        "res.partner", string="Referred Customer", index=True, ondelete="restrict"
    )
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("converted", "Converted"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="pending",
    )
    points_awarded = fields.Integer(default=0, readonly=True)
    converted_at = fields.Datetime(readonly=True)
    note = fields.Char()

    def action_mark_converted(self):
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only pending referral codes can be converted")
            rec.write({"state": "converted", "converted_at": fields.Datetime.now()})
        return True
