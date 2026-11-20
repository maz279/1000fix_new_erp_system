# A06 ERP D1 (20 Nov 2026): every valuation row carries its business date
# (the Asia/Dhaka date of the movement: the GL date and the period cut-off)
# and the stock location it moved at. Rows written before this version get
# them from their creation time and, for a job issue, its consumption.
# Their status is untouched: rows pending the old cut-over stay pending.


def migrate(cr, version):
    cr.execute(
        """UPDATE fix_inventory_valuation_suspense
              SET posting_date = ((create_date AT TIME ZONE 'UTC') AT TIME ZONE 'Asia/Dhaka')::date
            WHERE posting_date IS NULL"""
    )
    cr.execute(
        """UPDATE fix_inventory_valuation_suspense s
              SET location_id = c.location_id
             FROM fix_stock_consumption c
            WHERE s.consumption_id = c.id
              AND s.location_id IS NULL"""
    )
