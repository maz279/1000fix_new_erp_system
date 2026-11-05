# A10 P1-3 pre-migrate — role_a/role_b became Many2one fix.role.
#
# On databases seeded before the A10 build (fix_dev lineage) the two
# columns carry CHAR values (role titles such as "Vendor Master
# Steward"); Odoo's column-type conversion then fails with
# InvalidTextRepresentation: invalid input syntax for type integer.
# Map every text value to the fix.role row whose code or name matches,
# drop the ones with no match to NULL (the field is required, so a
# mismatched row must be re-pointed by hand — but no data is destroyed:
# the original text is preserved in the log), and let the type
# conversion then find only integers/NULLs. Databases where the columns
# are already integer (fresh installs, fix_test lineage) are untouched.
import logging

from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)


def _migrate_text_role_column(cr, column):
    cr.execute(
        "SELECT id, %s FROM fix_grc_sod_rule WHERE %s IS NOT NULL" % (column, column)
    )
    rows = cr.fetchall()
    if not rows:
        return
    fixed, dropped = 0, 0
    for rec_id, value in rows:
        if isinstance(value, int):
            continue
        cr.execute(
            "SELECT id FROM fix_role WHERE code = %s OR name = %s LIMIT 1",
            (value, value),
        )
        hit = cr.fetchone()
        if hit:
            cr.execute(
                "UPDATE fix_grc_sod_rule SET %s = %%s WHERE id = %%s" % column,
                (hit[0], rec_id),
            )
            fixed += 1
        else:
            # the row's role references a title that exists as no fix.role:
            # the control governs nothing and cannot survive as a Many2one.
            # Delete it (logged) — the control is re-authored against real
            # roles through the A10 surface.
            _logger.warning(
                "cd_grc pre-migrate: sod rule %s (%r on %s) matches no fix.role "
                "— legacy control deleted; re-author it against real roles",
                rec_id,
                value,
                column,
            )
            cr.execute("DELETE FROM fix_grc_sod_rule WHERE id = %s", (rec_id,))
            dropped += 1
    if fixed or dropped:
        _logger.info(
            "cd_grc pre-migrate %s: %d mapped to fix.role, %d cleared", column, fixed, dropped
        )


def migrate(cr, version):
    if not column_exists(cr, "fix_grc_sod_rule", "role_a"):
        return
    # only act when the column is still text (pre-A10 databases)
    cr.execute(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name = 'fix_grc_sod_rule' AND column_name = 'role_a'"
    )
    dtype = cr.fetchone()
    if not dtype or dtype[0] != "character varying":
        return
    _migrate_text_role_column(cr, "role_a")
    _migrate_text_role_column(cr, "role_b")
