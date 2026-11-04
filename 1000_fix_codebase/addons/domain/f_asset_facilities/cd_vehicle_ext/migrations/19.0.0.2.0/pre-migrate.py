# A07 P1 M46-20: fix.vehicle.document.state becomes a read-time field over
# the stored recorded_state. Keep each row's recorded lifecycle (valid, or
# expired by action_expire / the expiry job) by renaming the column before
# the registry loads, instead of losing it to a fresh default.
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        """SELECT column_name FROM information_schema.columns
            WHERE table_name = 'fix_vehicle_document'
              AND column_name IN ('state', 'recorded_state')"""
    )
    present = {row[0] for row in cr.fetchall()}
    if "state" in present and "recorded_state" not in present:
        cr.execute("ALTER TABLE fix_vehicle_document RENAME COLUMN state TO recorded_state")
        _logger.info("fix.vehicle.document: state column kept as recorded_state")
