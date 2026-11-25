# A08 S4 pre-migrate — fix.sod.control grew group-pair controls.
#
# role_a_id/role_b_id were required (NOT NULL) while only role-pair controls
# existed. The A08 finance duty rule set (data/fix_sod_finance_controls.xml)
# loads group-pair controls that name no role, so the two columns become
# optional. Odoo's schema reflection does not DROP an existing NOT NULL on a
# field that becomes optional, so the constraint is dropped here (same
# pattern as cd_grc's 19.0.0.1.1 Char->Many2one pre-migrate).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute(
        """
        ALTER TABLE fix_sod_control
            ALTER COLUMN role_a_id DROP NOT NULL,
            ALTER COLUMN role_b_id DROP NOT NULL
        """
    )
    _logger.info("A08 S4: fix_sod_control.role_a_id/role_b_id are now optional (group pairs)")
