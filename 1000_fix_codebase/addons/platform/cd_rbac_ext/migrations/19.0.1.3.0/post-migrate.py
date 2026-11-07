# A12 finish: bring an existing database to what the code now means.
#
# noupdate data does not refresh on -u, so everything below is done here:
# - E6: clear the fix.role.group_id scratch map. The shipped map in
#   data/fix_role_group_map.xml is not noupdate and has already been re-applied.
# - E9: delete the second expiry job (ir_cron_access_revoke_expired). It is a noupdate
#   row that outlives its data file.
# - E3/E5: open fix.role.assignment rows from what the workflow really did.
# - E20: anchor the audit chain, labelling and sealing the existing rows.
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("UPDATE fix_role SET group_id = NULL WHERE group_id IS NOT NULL")
    _logger.info("M29 finish: cleared %d legacy fix.role.group_id value(s)", cr.rowcount)
    env.invalidate_all()
    old_cron = env.ref("cd_rbac_ext.ir_cron_access_revoke_expired", raise_if_not_found=False)
    if old_cron:
        old_cron.unlink()
        _logger.info("M29 finish: removed the retired ir_cron_access_revoke_expired job")
    opened = env["fix.role.assignment"]._fix_backfill_from_history()
    _logger.info("M29 finish: opened %d role assignment(s) from history", opened)
    env["fix.security.audit"]._fix_anchor_chain()
