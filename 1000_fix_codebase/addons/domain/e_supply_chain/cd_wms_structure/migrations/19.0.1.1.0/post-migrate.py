# M41 capture pass 2: warehouse execution is opt-in (FR-WMS-003). A warehouse
# already laid out in zones before the flag existed keeps running.


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        "UPDATE fix_warehouse SET wms_enabled = TRUE "
        "WHERE id IN (SELECT DISTINCT warehouse_id FROM fix_warehouse_zone)"
    )
