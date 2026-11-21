# A07 ERP audit (2026-11-20) LEAD-01/X28: a fitted component's lot is an M15
# fix.stock.lot. Rows that still name Odoo's stock.lot but hold no lot are
# re-pointed; a row that holds a stock.lot id is left as it is and logged,
# because that id means nothing in fix.stock.lot (fix_real had none).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        "UPDATE fix_device_component SET lot_model = 'fix.stock.lot' "
        "WHERE lot_model = 'stock.lot' AND (lot_id IS NULL OR lot_id = 0)"
    )
    moved = cr.rowcount
    cr.execute(
        "SELECT count(*) FROM fix_device_component WHERE lot_model = 'stock.lot' AND lot_id > 0"
    )
    kept = cr.fetchone()[0]
    _logger.info(
        "M17 component lots: %s rows re-pointed to fix.stock.lot, %s rows keep a stock.lot id",
        moved,
        kept,
    )
