# Warranty expiry (A02 audit B4).
#
# Nothing ever wrote status='expired': cover past its end date stayed
# 'active' (or 'pending') for ever, and only the date check inside
# is_under_warranty kept it from giving a free job. The daily cron moves every
# live fix.warranty row past its end date to expired. It acts on the
# warranty rows only; fix.device.warranty_status is computed from them.
import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class FixWarrantyExpiry(models.Model):
    _inherit = "fix.warranty"

    @api.model
    def _cron_expire_warranties(self):
        """Expire active or pending cover whose end date has passed.

        A07 P1 (M17, AUT-AST-10) runs in the same job: each expiry is published
        as device.warranty_expired, and cover about to end is announced once."""
        today = fields.Date.context_today(self)
        stale = self.sudo().search(
            [("status", "in", ("active", "pending")), ("end_date", "<", today)]
        )
        expired = 0
        for warranty in stale:
            try:
                with self.env.cr.savepoint():
                    warranty._guarded().write({"status": "expired"})
                    warranty.message_post(
                        body="Warranty expired: its cover ended on %s." % warranty.end_date
                    )
                    warranty._announce_expired()
                    expired += 1
            except Exception:
                logger.exception("Could not expire warranty %s", warranty.id)
        self._announce_expiring_cover()
        return expired
