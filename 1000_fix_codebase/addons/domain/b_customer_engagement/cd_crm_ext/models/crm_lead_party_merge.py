# party.merged consumer for M07 leads and opportunities (A03 audit W1, R8).
#
# A supervised merge (cd_party_master fix.party.merge) moves only the party
# kernel's own records; each module re-points its own references. An open
# lead stayed on the tombstoned victim, so the seller worked a customer that
# no longer existed. Won and lost leads are history and stay where they were
# made. The re-point is logged (fix.party.repoint.log), so a merge reversal
# moves it back.
from odoo import api, models


class CrmLeadPartyMerge(models.Model):
    _inherit = "crm.lead"

    @api.model
    def consume_party_merged(self, event):
        """Open leads (active, neither won nor lost) follow the survivor.
        Idempotent: a second delivery finds none left on the victim."""
        Log = self.env["fix.party.repoint.log"]
        merge = Log._event_merge(event)
        if not merge:
            return 0
        survivor, victim = merge.survivor_id, merge.victim_id
        leads = self.sudo().search(
            [
                ("partner_id", "=", victim.id),
                ("active", "=", True),
                ("won_status", "=", "pending"),
            ]
        )
        return len(Log.repoint(merge, leads, "partner_id", victim, survivor))
