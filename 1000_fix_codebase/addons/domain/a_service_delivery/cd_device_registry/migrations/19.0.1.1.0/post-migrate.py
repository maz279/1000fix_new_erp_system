# A07 operability (2026-11-07), M17: fix_device_identifier held 0 rows against
# 53 live devices with an IMEI, so the NEIR actions and the identifier history
# screen were empty. This records what each device row already says and nothing
# new (fix.device._identifier_backfill); it is idempotent.
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    added = env["fix.device"]._identifier_backfill()
    _logger.info("M17 identifier history: %s rows recorded from the device records", added)
