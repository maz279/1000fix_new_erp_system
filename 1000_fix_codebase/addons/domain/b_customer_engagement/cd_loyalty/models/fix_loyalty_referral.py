# M10 · Referral codes — the acquisition hook of the loyalty programme.
# A code belongs to a referrer; conversion is recorded when the referee's
# first qualifying service closes. Conversion awards the programme's referral
# points as posted ledger lines (A03 audit M10-10: points_awarded was never
# written, so a converted referral paid nothing). The ledger line is the
# evidence; the referral stores the outcome.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixLoyaltyReferralCode(models.Model):
    _name = "fix.loyalty.referral.code"
    _description = "Loyalty Referral Code"
    _inherit = ["fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    def _fix_guarded_fields(self) -> set:
        # Conversion now mints points; its outcome is set by the conversion.
        return super()._fix_guarded_fields() | {"state", "points_awarded", "converted_at"}

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

    def _check_convertible(self):
        """A conversion pays points, so it needs the evidence it claims."""
        self.ensure_one()
        if self.state != "pending":
            raise UserError("Only pending referral codes can be converted")
        if not self.referee_partner_id:
            raise UserError("Name the referred customer before converting the referral.")
        referrer = self.referrer_partner_id.commercial_partner_id
        referee = self.referee_partner_id.commercial_partner_id
        if referrer == referee:
            raise UserError("A customer cannot refer themselves or their own household or company.")
        closed = (
            self.env["fix.service.order"]
            .sudo()
            .search_count(
                [("customer_id", "=", self.referee_partner_id.id), ("state", "=", "closed")],
                limit=1,
            )
        )
        if not closed:
            raise UserError(
                "The referred customer has no closed service order yet. A referral "
                "converts on the referee's first completed service."
            )

    def action_mark_converted(self):
        for rec in self:
            rec._check_convertible()
            rec._convert()
        return True

    def _convert(self):
        """Mark converted and post the programme's referral awards."""
        self.ensure_one()
        awarded = self._award_points()
        self._guarded().write(
            {"state": "converted", "converted_at": fields.Datetime.now(), "points_awarded": awarded}
        )
        return awarded

    def _award_points(self) -> int:
        """Post referral_bonus lines to the referrer and, if set, the referee.

        These are system lines: the amount is the programme's configured
        award, not a figure a person keyed in, so they are not manual-credit
        DOFA. A referrer with no active account in the programme earns
        nothing, and the referral says so."""
        self.ensure_one()
        program = self.program_id
        Account = self.env["fix.loyalty.account"].sudo()
        Ledger = self.env["fix.loyalty.ledger"].sudo()
        Receipt = self.env["fix.loyalty.event.receipt"]
        total = 0
        for role, partner, points in (
            ("referrer", self.referrer_partner_id, program.referral_referrer_points),
            ("referee", self.referee_partner_id, program.referral_referee_points),
        ):
            if points <= 0 or not partner:
                continue
            key = "referral:%d:%s" % (self.id, role)
            if Receipt._seen(key):
                continue
            account = Account.search(
                [("partner_id", "=", partner.id), ("program_id", "=", program.id)], limit=1
            )
            if not account or account.state != "active":
                Receipt._record(
                    key,
                    {},
                    "No award: the %s has no active account in %s." % (role, program.name),
                    account=account or None,
                )
                continue
            line = Ledger.create(
                {
                    "account_id": account.id,
                    "transaction_type": "referral_bonus",
                    "points": points,
                    "company_id": account.company_id.id,
                    "notes": "Referral %s converted: %s award." % (self.name, role),
                }
            )
            line.action_post()
            Receipt._record(key, {}, "Awarded %d points to the %s." % (points, role), account, line)
            total += points
        return total

    @api.model
    def _convert_on_first_service(self, order) -> int:
        """Called by the service_order.closed consumer: the referee's closed
        order is the conversion evidence. Returns the number converted."""
        codes = self.sudo().search(
            [("state", "=", "pending"), ("referee_partner_id", "=", order.customer_id.id)]
        )
        converted = 0
        for code in codes:
            if code.referrer_partner_id.commercial_partner_id == (
                code.referee_partner_id.commercial_partner_id
            ):
                continue  # self-referral never converts
            code._convert()
            converted += 1
        return converted
