# party.merged consumer for business partners (A03 audit W1, R8).
#
# A fix.partner (referral partner, reseller, franchise, alliance) links one
# res.partner. After a supervised merge it stayed on the tombstoned victim,
# so commissions, onboarding and the partner portal followed a party that no
# longer exists. Erased (anonymised) records stay as they are. The re-point
# is logged (fix.party.repoint.log), so a merge reversal moves it back.
from odoo import api, models


class FixPartnerPartyMerge(models.Model):
    _inherit = "fix.partner"

    @api.model
    def consume_party_merged(self, event):
        """Business-partner records follow the survivor. Idempotent: a second
        delivery finds none left on the victim."""
        Log = self.env["fix.party.repoint.log"]
        merge = Log._event_merge(event)
        if not merge:
            return 0
        survivor, victim = merge.survivor_id, merge.victim_id
        partners = (
            self.sudo()
            .with_context(active_test=False)
            .search([("partner_id", "=", victim.id), ("pdpa_erasure_state", "!=", "erased")])
        )
        return len(Log.repoint(merge, partners, "partner_id", victim, survivor))
