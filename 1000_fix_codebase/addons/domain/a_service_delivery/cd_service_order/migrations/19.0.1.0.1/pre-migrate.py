# Give every service order still carrying the old placeholder reference "NEW"
# (the field default's fallback before the sequence existed) a real number from
# the fix.service.order sequence, in creation order, so the UNIQUE (name)
# constraint added in this version can be created.
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        "SELECT id FROM fix_service_order WHERE name IS NULL OR name = 'NEW' ORDER BY create_date, id"
    )
    ids = [row[0] for row in cr.fetchall()]
    if not ids:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    seq = env["ir.sequence"]
    for order_id in ids:
        ref = seq.next_by_code("fix.service.order")
        if not ref:
            raise RuntimeError("fix.service.order sequence missing; cannot renumber service orders")
        cr.execute("UPDATE fix_service_order SET name = %s WHERE id = %s", (ref, order_id))
    _logger.info(
        "cd_service_order: renumbered %d service orders that carried the 'NEW' placeholder",
        len(ids),
    )
