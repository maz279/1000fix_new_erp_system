# party.merged consumer for M34 complaints (A03 audit W1, R8).
#
# An open complaint stayed on the tombstoned victim after a supervised merge,
# so its SLA, its response and its concession named a party that no longer
# exists. A closed or declined complaint is the ISO 10002 record of what was
# decided for whom, and stays where it was made. The re-point is logged
# (fix.party.repoint.log), so a merge reversal moves it back.
from odoo import api, models

from .fix_complaint_lifecycle import FINISHED_STATES


class FixComplaintPartyMerge(models.Model):
    _inherit = "fix.complaint"

    @api.model
    def consume_party_merged(self, event):
        """Complaints not yet closed follow the survivor. Idempotent: a
        second delivery finds none left on the victim."""
        Log = self.env["fix.party.repoint.log"]
        merge = Log._event_merge(event)
        if not merge:
            return 0
        survivor, victim = merge.survivor_id, merge.victim_id
        complaints = self.sudo().search(
            [("customer_id", "=", victim.id), ("state", "not in", FINISHED_STATES)]
        )
        return len(Log.repoint(merge, complaints, "customer_id", victim, survivor))
