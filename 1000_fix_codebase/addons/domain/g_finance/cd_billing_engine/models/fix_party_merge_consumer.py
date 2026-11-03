# party.merged consumer for M20 credit profiles (A03 audit W1, R8).
#
# A supervised merge left the victim's credit terms and hold on the
# tombstone, so the survivor traded with no credit control at all.
#
# One profile per customer and company (UNIQUE), so:
# - the survivor has no profile in that company: the victim's moves to it;
# - the survivor already has one: neither profile is changed. Which limit,
#   terms and hold apply is a credit decision, not a merge side effect.
#   Both profiles are told, and a hold on the victim's profile is named.
# Issued invoices and posted accounting entries are never re-pointed: they
# are the ledger of what was billed to whom.
# The re-point is logged (fix.party.repoint.log), so a reversal moves it back.
from odoo import api, models


class FixCreditProfilePartyMerge(models.Model):
    _inherit = "fix.credit.profile"

    @api.model
    def consume_party_merged(self, event):
        """Returns how many profiles moved. Idempotent: a moved profile is no
        longer on the victim, and a kept one is noted once per merge."""
        Log = self.env["fix.party.repoint.log"]
        merge = Log._event_merge(event)
        if not merge:
            return 0
        survivor, victim = merge.survivor_id, merge.victim_id
        Profile = self.sudo()
        moved = 0
        for profile in Profile.search([("customer_id", "=", victim.id)]):
            held = Profile.search(
                [("customer_id", "=", survivor.id), ("company_id", "=", profile.company_id.id)],
                limit=1,
            )
            marker = "Party merge #%s:" % merge.id
            if not held:
                moved += len(Log.repoint(merge, profile, "customer_id", victim, survivor))
                profile.message_post(
                    body="%s credit profile moved from %s to %s."
                    % (marker, victim.display_name, survivor.display_name)
                )
                continue
            noted = (
                self.env["mail.message"]
                .sudo()
                .search_count(
                    [
                        ("model", "=", profile._name),
                        ("res_id", "=", profile.id),
                        ("body", "ilike", marker),
                    ]
                )
            )
            if noted:
                continue
            note = (
                "%s %s was merged into %s, which already has credit profile #%s. Neither "
                "profile was changed: credit control decides which limit, terms and hold "
                "apply.%s"
                % (
                    marker,
                    victim.display_name,
                    survivor.display_name,
                    held.id,
                    " The merged-away profile is ON HOLD (%s)." % (profile.hold_reason or "-")
                    if profile.credit_hold
                    else "",
                )
            )
            for rec in profile | held:
                rec.message_post(body=note)
        return moved
