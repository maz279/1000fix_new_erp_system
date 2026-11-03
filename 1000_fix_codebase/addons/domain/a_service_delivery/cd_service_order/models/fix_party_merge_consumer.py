# party.merged consumers for service orders and devices (A03 audit M33-5, R8).
#
# A supervised merge (cd_party_master fix.party.merge) moves only the party
# kernel's own records and publishes party.merged; every other module
# re-points its own references. Nothing listened, so a merged customer's open
# repair stayed on the tombstone. Delivered, closed and cancelled orders are
# history and stay where they were made.
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

# A service order in one of these is history, not an open document.
_DONE_STATES = ("delivered", "closed", "cancelled")


class FixServiceOrderPartyMerge(models.Model):
    _inherit = "fix.service.order"

    @api.model
    def consume_party_merged(self, event):
        """Open and draft orders of the merged-away customer move to the
        survivor. Idempotent: a second delivery finds none left on the victim,
        and a merge reversed before delivery re-points nothing."""
        parties = self.env["res.partner"]._fix_merge_event_parties(event)
        if not parties:
            return 0
        survivor, victim = parties
        orders = (
            self.sudo()
            .with_context(active_test=False)
            .search([("customer_id", "=", victim.id), ("state", "not in", _DONE_STATES)])
        )
        for order in orders:
            order.write({"customer_id": survivor.id})
            order.message_post(
                body="Customer re-pointed from merged party %s to %s (merge #%s)."
                % (
                    victim.display_name,
                    survivor.display_name,
                    (event.get("payload") or {}).get("merge_id") or "?",
                )
            )
        if orders:
            _logger.info(
                "party.merged: %d service orders re-pointed %s -> %s",
                len(orders),
                victim.id,
                survivor.id,
            )
        return len(orders)


class FixDevicePartyMerge(models.Model):
    _inherit = "fix.device"

    @api.model
    def consume_party_merged(self, event):
        """A device's CURRENT owner follows the merge: the owner is the same
        person under one record now. Past ownership transfers
        (fix.device.ownership) are history and are not rewritten.
        Idempotent: a second delivery finds no device owned by the victim."""
        parties = self.env["res.partner"]._fix_merge_event_parties(event)
        if not parties:
            return 0
        survivor, victim = parties
        devices = self.sudo().with_context(active_test=False).search([("owner_id", "=", victim.id)])
        if devices:
            devices.write({"owner_id": survivor.id})
        return len(devices)
