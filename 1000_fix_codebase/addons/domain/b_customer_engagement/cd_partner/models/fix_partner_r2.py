# A04 ERP audit (21 Nov 2026), round 2: the M40 links into M07 and M11.
#
#   * crm.lead (M07)          - the partner attribution of a hand-off: the
#                               channel partner, and the partner lead or won
#                               deal registration it came from (M40-F23).
#                               Guarded: written by the hand-off only.
#   * fix.promotion (M11)     - a promotion an alliance scheme names is
#                               member-only: usable only under an eligible
#                               check of that scheme (M40-F28, BRU-PCM-19).
#   * fix.rate.card.price_for - an alliance check in the context grants its
#                               promotion only to the customer it validated.
from odoo import api, fields, models

from .fix_partner_capture import ALLIANCE_CHECK_CTX


class CrmLeadPartnerAttribution(models.Model):
    _inherit = "crm.lead"

    fix_partner_id = fields.Many2one(
        "fix.partner",
        string="Channel Partner (M40)",
        readonly=True,
        copy=False,
        index=True,
        help="The channel partner this lead or opportunity was handed over by (M40 lead or "
        "won deal registration).",
    )
    fix_partner_lead_id = fields.Many2one(
        "fix.partner.lead", string="Partner Lead (M40)", readonly=True, copy=False, index=True
    )
    fix_partner_deal_id = fields.Many2one(
        "fix.partner.deal", string="Partner Deal (M40)", readonly=True, copy=False, index=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "fix_partner_id",
            "fix_partner_lead_id",
            "fix_partner_deal_id",
        }


class FixPromotionAlliance(models.Model):
    _inherit = "fix.promotion"

    alliance_scheme_ids = fields.One2many(
        "fix.alliance.scheme",
        "benefit_promotion_id",
        string="Alliance Schemes (member-only)",
        readonly=True,
    )

    def _fix_alliance_only(self) -> bool:
        self.ensure_one()
        return bool(self.sudo().with_context(active_test=False).alliance_scheme_ids)

    def _usable_on(self, channel=None, on_date=None):
        """A member-only promotion is usable only under an eligible alliance
        check of a scheme that names it (the check is validated again here:
        result, customer named, scheme active and in force)."""
        usable = super()._usable_on(channel=channel, on_date=on_date)
        if not usable or not self._fix_alliance_only():
            return usable
        check_id = self.env.context.get(ALLIANCE_CHECK_CTX)
        if not check_id:
            return False
        check = self.env["fix.alliance.eligibility.check"].sudo().browse(int(check_id)).exists()
        return bool(
            check
            and check.scheme_id.benefit_promotion_id.id == self.id
            and not check._fix_grants_benefit(on_date=on_date)
        )


class FixRateCardAlliance(models.Model):
    _inherit = "fix.rate.card"

    @api.model
    def price_for(self, product, partner=None, channel="quotation", *args, **kwargs):
        """An alliance check in the context counts only for the customer it
        validated, on a day its scheme is in force; otherwise it is dropped
        and no member-only promotion applies."""
        check_id = self.env.context.get(ALLIANCE_CHECK_CTX)
        rate_card = self
        if check_id:
            day = kwargs.get("date")
            check = self.env["fix.alliance.eligibility.check"].sudo().browse(int(check_id)).exists()
            if not check or check._fix_grants_benefit(
                partner or self.env["res.partner"], fields.Date.to_date(day) if day else None
            ):
                rate_card = self.with_context(**{ALLIANCE_CHECK_CTX: False})
        return super(FixRateCardAlliance, rate_card).price_for(
            product, partner, channel, *args, **kwargs
        )
