# A06 ERP audit (20 Nov 2026), M15 stream.
#   X21: every ledger bucket carries the operating unit of the location that
#        holds it (the location's own, else its branch's). fix_real had 4,863
#        buckets (BDT 38.4M) stamped with the main OU while their location was a
#        branch's, so the branch's own users could not see its stock.
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    result = env["fix.stock.onhand"]._fix_repair_ou_stamps()
    _logger.info("A06 X21 operating-unit repair of the M15 ledger: %s", result)
