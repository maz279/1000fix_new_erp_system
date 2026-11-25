# party.merged consumer for M17 corporate estates (A03 audit W1, R8).
#
# A corporate estate is keyed on its client (fix.device.estate.client_id).
# After a supervised merge it stayed on the tombstoned victim, so the estate's
# devices and PM plans belonged to a party that no longer exists. The
# re-point is logged (fix.party.repoint.log), so a merge reversal moves it
# back.
from odoo import api, models


class FixDeviceEstatePartyMerge(models.Model):
    _inherit = "fix.device.estate"

    @api.model
    def consume_party_merged(self, event):
        """Estates (archived ones too) follow the survivor. Idempotent: a
        second delivery finds none left on the victim."""
        Log = self.env["fix.party.repoint.log"]
        merge = Log._event_merge(event)
        if not merge:
            return 0
        survivor, victim = merge.survivor_id, merge.victim_id
        estates = (
            self.sudo().with_context(active_test=False).search([("client_id", "=", victim.id)])
        )
        return len(Log.repoint(merge, estates, "client_id", victim, survivor))
