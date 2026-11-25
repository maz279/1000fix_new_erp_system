# A06 ERP audit (20 Nov 2026) - one migration for the merged streams.
# LEDGER (D1): every valuation row carries its business date (the Asia/Dhaka
#   date of the movement: the GL date and the period cut-off) and the stock
#   location it moved at. Rows written before this version get them from their
#   creation time and, for a job issue, its consumption. Their status is
#   untouched: rows pending the old cut-over stay pending.
# M15 (X21): every ledger bucket carries the operating unit of the location
#   that holds it (the location's own, else its branch's). fix_real had 4,863
#   buckets (BDT 38.4M) stamped with the main OU while their location was a
#   branch's, so the branch's own users could not see its stock.
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute(
        """UPDATE fix_inventory_valuation_suspense
              SET posting_date = ((create_date AT TIME ZONE 'UTC') AT TIME ZONE 'Asia/Dhaka')::date
            WHERE posting_date IS NULL"""
    )
    cr.execute(
        """UPDATE fix_inventory_valuation_suspense s
              SET location_id = c.location_id
             FROM fix_stock_consumption c
            WHERE s.consumption_id = c.id
              AND s.location_id IS NULL"""
    )
    env = api.Environment(cr, SUPERUSER_ID, {})
    result = env["fix.stock.onhand"]._fix_repair_ou_stamps()
    _logger.info("A06 X21 operating-unit repair of the M15 ledger: %s", result)
