# cd_talent 19.0.0.6.0 — M58-F4 (A09 ERP audit 2026-11-23).
#
# The candidate's government identifiers (NID, birth registration number,
# passport number) no longer live in clear columns on fix_candidate: they are
# held in the Bangladesh-resident store (libs/py/fix_residency, the only
# client), and the row keeps a keyed hash and a pointer per identifier.
#
# This moves the values of rows written before the change. Idempotent, and it
# never fails the upgrade because the store is down: such a row keeps its
# value (its hash is set already, so duplicates are caught) and the daily
# erasure cron retries the move.
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    result = env["fix.candidate"]._fix_identity_move_clear_values()
    _logger.info("cd_talent %s: candidate identity residency move %s", version, result)
