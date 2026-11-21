# A04 ERP audit round 2 (21 Nov 2026).
#
# M40-F26: one MDF mechanism. An MDF raised as a rebate that was never
# approved is cancelled with a pointer to the MDF fund / claim registers;
# approved and paid ones keep their history (0 rows on fix_real).
#
# M40-F28: an alliance scheme's typed benefit_ref becomes the M11 promotion
# whose code it named, in the scheme's company. The old column outlives the
# field (Odoo keeps it), so it is read once here; an unmatched text is left
# for pricing to resolve and logged (0 schemes on fix_real).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cancelled = env["fix.partner.rebate"]._fix_migrate_mdf_rebates()
    if cancelled:
        _logger.warning(
            "M40-F26: %d unapproved MDF rebate(s) cancelled: %s", len(cancelled), cancelled
        )
    cr.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name = 'fix_alliance_scheme' AND column_name = 'benefit_ref'"
    )
    if not cr.fetchone():
        return
    cr.execute(
        """
        UPDATE fix_alliance_scheme s
           SET benefit_promotion_id = p.id
          FROM fix_promotion p
         WHERE s.benefit_promotion_id IS NULL
           AND COALESCE(TRIM(s.benefit_ref), '') <> ''
           AND p.code = TRIM(s.benefit_ref)
           AND p.company_id = s.company_id
        """
    )
    cr.execute(
        "SELECT id, code, benefit_ref FROM fix_alliance_scheme "
        "WHERE benefit_promotion_id IS NULL AND COALESCE(TRIM(benefit_ref), '') <> ''"
    )
    for sid, code, ref in cr.fetchall():
        _logger.warning(
            "M40-F28: alliance scheme %s (%s) names benefit %r, which is no M11 promotion code "
            "of its company: link its promotion by hand.",
            code,
            sid,
            ref,
        )
