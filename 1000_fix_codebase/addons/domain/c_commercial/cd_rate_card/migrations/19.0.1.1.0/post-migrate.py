# A04 audit (2026-11-04) M11-5 / M11-8.
#
# 1. fix.rate.card gained a lifecycle (draft / released / retired). The
#    column is created with the default 'draft', which would stop every card
#    that was live before the control existed from pricing anything. Those
#    cards were in use, so they are recorded as released (archived ones as
#    retired); from now on a card is released only through fix.price.change.
# 2. fix.price.floor stored a stale DOFA tier (tier_2 on floors with no
#    proposal; current logic gives tier_0). It is recomputed once.
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        "UPDATE fix_rate_card SET state = CASE WHEN active THEN 'released' ELSE 'retired' END "
        "WHERE state = 'draft' OR state IS NULL"
    )
    _logger.info("fix.rate.card: %s pre-control cards recorded as released/retired", cr.rowcount)
    env = api.Environment(cr, SUPERUSER_ID, {})
    floors = env["fix.price.floor"].with_context(active_test=False).search([])
    if floors:
        env.add_to_compute(floors._fields["dofa_tier_required"], floors)
        env.flush_all()
        _logger.info("fix.price.floor: DOFA tier recomputed on %s floors", len(floors))
