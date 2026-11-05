# cd_hr_core 19.0.0.3.0 — move the clear personal identifiers into the
# Bangladesh-resident store (A09 M21-A6, BRU-HCM-06): hr_employee's NID, birth
# registration, e-TIN, passport and nominee NID, and fix_hr_dependant's NID.
# The fields became computed (fix_hr_identity_residency.py); the old columns
# keep their values until this moves them.
#
# Idempotent, and it never fails the upgrade because the store is down: such a
# row keeps its value (its hash is set already, so duplicates are caught) and
# the daily cron M21 "move clear NID ..." moves it later.
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    result = env["hr.employee"]._fix_identity_move_clear_values()
    _logger.info("cd_hr_core %s: identity residency move %s", version, result)
