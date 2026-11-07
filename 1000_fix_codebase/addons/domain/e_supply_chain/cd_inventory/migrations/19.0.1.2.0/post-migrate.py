# A06 final pass.
#   B19: weighted average is the only valuation that runs; a bucket labelled
#        anything else reported a method nothing applied.
#   B15: a line in transit at this upgrade reads received_qty 0, which would
#        now mean "nothing arrived": it starts at what was sent, as at dispatch.


def migrate(cr, version):
    cr.execute(
        """UPDATE fix_stock_onhand SET valuation_method = 'wac'
            WHERE valuation_method IS DISTINCT FROM 'wac'"""
    )
    cr.execute(
        """UPDATE fix_stock_transfer_line l
              SET received_qty = l.qty
             FROM fix_stock_transfer t
            WHERE l.transfer_id = t.id
              AND t.state = 'dispatched'
              AND l.is_dispatched"""
    )
