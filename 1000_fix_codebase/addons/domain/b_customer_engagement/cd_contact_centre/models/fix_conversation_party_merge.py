# party.merged consumer for M27 conversations (A03 audit W1, R8).
#
# An open conversation stayed on the tombstoned victim after a supervised
# merge, so the agent and the bot answered for a party that no longer exists.
# A resolved or abandoned conversation is the record of that contact and
# stays where it was made. The re-point is logged (fix.party.repoint.log), so
# a merge reversal moves it back.
from odoo import api, models


class FixConversationPartyMerge(models.Model):
    _inherit = "fix.conversation"

    @api.model
    def consume_party_merged(self, event):
        """Open conversations follow the survivor. Idempotent: a second
        delivery finds none left on the victim."""
        Log = self.env["fix.party.repoint.log"]
        merge = Log._event_merge(event)
        if not merge:
            return 0
        survivor, victim = merge.survivor_id, merge.victim_id
        conversations = self.sudo().search(
            [("customer_id", "=", victim.id), ("state", "not in", self._CLOSED_STATES)]
        )
        return len(Log.repoint(merge, conversations, "customer_id", victim, survivor))
