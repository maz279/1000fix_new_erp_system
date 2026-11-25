# M40 co-marketing: the partner <-> campaign link (declared gap
# M40-comarketing closed, 12 Nov 2026).
#
# fix.campaign (M35) carried no fix.partner key - the partner_id on its
# touches, responses and journey members is the CUSTOMER reached, not a
# channel partner - and an MDF accrual (fix.partner.rebate, kind 'mdf')
# carried no campaign key, so co-marketing spend and results could not be
# tied to a campaign.
#
#   * fix.campaign.partner_ids - the co-marketing partners of a campaign
#     (the same link is fix.partner.comarketing_campaign_ids, so the M40
#     partner form maintains it too). Named by a Channel Officer; only an
#     onboarded partner co-markets; a partner with a live MDF accrual on the
#     campaign stays on it until that MDF is cancelled.
#   * fix.partner.rebate.campaign_id - the campaign an MDF funds (optional;
#     MDF only; the partner must co-fund the campaign; pinned once accrued).
from odoo import fields, models
from odoo.exceptions import ValidationError

from .fix_partner import GROUP_OFFICER, fix_require

COMARKETING_REL = "fix_campaign_partner_rel"
LIVE_MDF_STATES = ("draft", "accrued", "approved", "paid")
LIVE_CLAIM_STATES = ("draft", "submitted", "approved", "paid")


def _link_pairs(campaigns_to_partners):
    return {(c, p) for c, partners in campaigns_to_partners.items() for p in partners}


def check_comarketing_change(env, before, after):
    """Validate a change of the campaign<->partner link set.

    ``before``/``after`` are {campaign_id: set(partner_ids)}, read after the
    write (an exception here rolls it back). Changing the link is a Channel
    Officer's; an added partner must be onboarded; a removed one may not have
    a live MDF on the campaign."""
    old, new = _link_pairs(before), _link_pairs(after)
    added, removed = new - old, old - new
    if not (added or removed):
        return  # the form posts the link unchanged on every save
    fix_require(env, [GROUP_OFFICER], "Changing the co-marketing partners of a campaign")
    if added:
        partners = env["fix.partner"].sudo().browse({p for _c, p in added})
        not_ready = partners.filtered(lambda p: p.state != "onboarded")
        if not_ready:
            raise ValidationError(
                "Only an onboarded partner co-markets a campaign: %s is not onboarded."
                % ", ".join(not_ready.mapped("name"))
            )
    for campaign_id, partner_id in removed:
        live = (
            env["fix.partner.rebate"]
            .sudo()
            .search(
                [
                    ("kind", "=", "mdf"),
                    ("campaign_id", "=", campaign_id),
                    ("partner_id", "=", partner_id),
                    ("state", "in", LIVE_MDF_STATES),
                ],
                limit=1,
            )
        )
        if live:
            raise ValidationError(
                "%s funds campaign %s through MDF %s (%s): the partner stays on the "
                "campaign while that MDF stands (a draft or accrued one is cancelled first)."
                % (live.partner_id.name, live.campaign_id.name, live.name, live.state)
            )
        # A04 ERP audit M40-F26: the MDF is a claim on the partner's fund now
        claim = (
            env["fix.mdf.claim"]
            .sudo()
            .search(
                [
                    ("campaign_id", "=", campaign_id),
                    ("partner_id", "=", partner_id),
                    ("state", "in", LIVE_CLAIM_STATES),
                ],
                limit=1,
            )
        )
        if claim:
            raise ValidationError(
                "%s claims MDF on campaign %s (claim %s, %s): the partner stays on the "
                "campaign while that claim stands (a refused claim does not count)."
                % (claim.partner_id.name, claim.campaign_id.name, claim.name, claim.state)
            )


class FixCampaignComarketing(models.Model):
    _inherit = "fix.campaign"

    partner_ids = fields.Many2many(
        "fix.partner",
        COMARKETING_REL,
        "campaign_id",
        "partner_id",
        string="Co-Marketing Partners",
        help="Channel partners co-funding this campaign (their MDF accruals name it).",
    )

    def write(self, vals):
        if "partner_ids" not in vals:
            return super().write(vals)
        before = {c.id: set(c.partner_ids.ids) for c in self}
        res = super().write(vals)
        check_comarketing_change(self.env, before, {c.id: set(c.partner_ids.ids) for c in self})
        return res


class FixPartnerComarketing(models.Model):
    _inherit = "fix.partner"

    comarketing_campaign_ids = fields.Many2many(
        "fix.campaign",
        COMARKETING_REL,
        "partner_id",
        "campaign_id",
        string="Co-Marketing Campaigns",
        help="Campaigns this partner co-funds (M35).",
    )

    def write(self, vals):
        if "comarketing_campaign_ids" not in vals:
            return super().write(vals)
        before_by_partner = {p.id: set(p.comarketing_campaign_ids.ids) for p in self}
        res = super().write(vals)
        before, after = {}, {}
        for p in self:
            for c in before_by_partner[p.id]:
                before.setdefault(c, set()).add(p.id)
            for c in p.comarketing_campaign_ids.ids:
                after.setdefault(c, set()).add(p.id)
        for c in set(before) | set(after):
            before.setdefault(c, set())
            after.setdefault(c, set())
        check_comarketing_change(self.env, before, after)
        return res
