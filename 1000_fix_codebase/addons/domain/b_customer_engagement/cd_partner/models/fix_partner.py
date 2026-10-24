# fix_partner — M40: partner, referral, franchise (P10-M04).
from odoo import fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixPartner(models.Model):
    """M40: a partner is a PARTY ROLE on M33."""

    _name = "fix.partner"
    _description = "Channel Partner"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    partner_id = fields.Many2one(
        "res.partner", string="Party (M33)", required=True, ondelete="restrict"
    )
    partner_type = fields.Selection(
        [
            ("referral", "Referral Partner"),
            ("reseller", "Reseller"),
            ("franchise", "Franchise"),
            ("alliance", "Strategic Alliance"),
        ],
        required=True,
        default="referral",
    )
    commission_rate = fields.Float(string="Commission Rate", default=0.05)
    territory = fields.Char(string="Territory")
    contract_id = fields.Many2one("fix.contract", string="Agreement (M08)", ondelete="set null")
    state = fields.Selection(
        [("prospective", "Prospective"), ("onboarded", "Onboarded"), ("suspended", "Suspended")],
        default="prospective",
        required=True,
        tracking=True,
    )

    def action_onboard(self):
        for rec in self:
            rec.state = "onboarded"
            publish(
                self.env,
                "partner.onboarded",
                "fix.partner",
                rec.id,
                {"partner": rec.name, "type": rec.partner_type},
            )


class FixReferral(models.Model):
    """M40: referral with commission through M53's event engine."""

    _name = "fix.referral"
    _description = "Referral"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    partner_id = fields.Many2one(
        "fix.partner", string="Referring Partner", required=True, ondelete="cascade"
    )
    referred_partner_id = fields.Many2one(
        "res.partner", string="Referred Customer", ondelete="set null"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    base_amount = fields.Monetary(
        string="Referred Revenue (Gross)",
        currency_field="currency_id",
        tracking=True,
        help="The gross value of the converted business the commission is earned on",
    )
    commission_amount = fields.Monetary(
        string="Commission Earned", currency_field="currency_id", readonly=True
    )
    state = fields.Selection(
        [("submitted", "Submitted"), ("converted", "Converted"), ("commissioned", "Commissioned")],
        default="submitted",
        required=True,
        tracking=True,
    )

    def action_convert(self, base_amount=None):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted referral can be converted")
            if base_amount is not None:
                rec.base_amount = base_amount
            rec.state = "converted"
            publish(
                self.env,
                "referral.converted",
                "fix.referral",
                rec.id,
                {"partner": rec.partner_id.name},
            )

    def action_earn_commission(self):
        """Publishes commission.earned — M53's engine consumes it."""
        for rec in self:
            if rec.state != "converted":
                raise UserError("Convert before commissioning")
            if rec.base_amount <= 0:
                raise UserError(
                    "Referral %s has no referred revenue: the commission base is required"
                    % rec.name
                )
            rate = rec.partner_id.commission_rate
            if not 0 < rate <= 1:
                raise UserError(
                    "Partner %s has no valid commission rate (%s)" % (rec.partner_id.name, rate)
                )
            # the partner's agreed rate on the real base - never a flat amount
            commission = rec.currency_id.round(rec.base_amount * rate)
            rec.write({"state": "commissioned", "commission_amount": commission})
            publish(
                self.env,
                "commission.earned",
                "fix.referral",
                rec.id,
                {
                    "partner_id": rec.partner_id.partner_id.id,
                    "gross": float(rec.base_amount),
                    "rate": rate,
                    "commission": float(commission),
                },
            )
