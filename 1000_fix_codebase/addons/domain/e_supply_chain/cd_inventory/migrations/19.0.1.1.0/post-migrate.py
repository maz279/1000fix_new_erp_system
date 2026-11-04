# A06 remediation S9 (blind counts): the expected quantity of a count line
# moved from a typed column (fix_stock_count_line.expected_qty) to a system
# snapshot (fix.stock.count.snapshot) readable by Inventory Controllers only.
# Keep the evidence of counts recorded before the change: copy the old column
# into a snapshot for every line that has none. The old column is left in
# place (read by nothing), so nothing is lost.


def migrate(cr, version):
    cr.execute(
        """SELECT 1 FROM information_schema.columns
           WHERE table_name = 'fix_stock_count_line' AND column_name = 'expected_qty'"""
    )
    if not cr.fetchone():
        return
    cr.execute(
        """INSERT INTO fix_stock_count_snapshot
               (line_id, expected_qty, unit_cost, taken_at, create_date, write_date)
           SELECT l.id, COALESCE(l.expected_qty, 0), COALESCE(p.unit_cost, 0),
                  COALESCE(l.create_date, NOW()), NOW(), NOW()
             FROM fix_stock_count_line l
             JOIN fix_spare_part p ON p.id = l.part_id
            WHERE NOT EXISTS (
                SELECT 1 FROM fix_stock_count_snapshot s WHERE s.line_id = l.id
            )"""
    )
    # Lines counted before the change carried no ownership class: the
    # location's own class (owned, or van at a van) is what they adjusted.
    cr.execute(
        """UPDATE fix_stock_count_line l
              SET ownership_class = CASE WHEN loc.location_type = 'van' THEN 'van'
                                         ELSE 'owned' END
             FROM fix_stock_count c
             JOIN fix_stock_location loc ON loc.id = c.location_id
            WHERE c.id = l.count_id AND l.ownership_class IS NULL"""
    )
