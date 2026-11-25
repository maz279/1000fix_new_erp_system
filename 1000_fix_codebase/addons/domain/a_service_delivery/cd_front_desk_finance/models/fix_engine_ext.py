# cd_front_desk_finance — the counter sale as a source of the engines it
# posts through: the M19 posting log (who posted what, from where) and the
# M15 valuation suspense (the stock movement the period close moves to GL),
# plus the branch's counter stock location.
from odoo import fields, models

SOURCE = "counter_sale"
# the reconciled drawer variance (fix_cash_shift_posting)
SHIFT_SOURCE = "cash_shift"
# a drawer cash-out: petty expense, staff advance, safe drop, field shortage
# (fix_cash_movement_posting)
MOVEMENT_SOURCE = "cash_movement"


def _suspense_to_shipment(rows):
    """Uninstalling the bridge keeps its suspense rows as stock that left the
    company (same sign convention: the row carries the movement itself)."""
    rows.sudo()._guarded().write({"entry_type": "shipment"})


class FixJournalPostingLogCounter(models.Model):
    _inherit = "fix.journal.posting.log"

    source = fields.Selection(
        selection_add=[
            (SOURCE, "Counter Sale (M04)"),
            (SHIFT_SOURCE, "Cash Shift Variance (M04)"),
            (MOVEMENT_SOURCE, "Drawer Cash-Out (M04)"),
        ],
        ondelete={
            SOURCE: "set default",
            SHIFT_SOURCE: "set default",
            MOVEMENT_SOURCE: "set default",
        },
    )


class FixValuationSuspenseCounter(models.Model):
    _inherit = "fix.inventory.valuation.suspense"

    # STOCK_EFFECT has no entry for it: the default (+1) is right, the row
    # carries the movement itself (an issue -, a refund's return +)
    entry_type = fields.Selection(
        selection_add=[(SOURCE, "Counter Sale")], ondelete={SOURCE: _suspense_to_shipment}
    )


class FixBranchCounterStock(models.Model):
    _inherit = "fix.branch"

    counter_stock_location_id = fields.Many2one(
        "fix.stock.location",
        string="Counter Stock Location",
        domain="[('branch_id', '=', id), ('location_type', 'in', ('branch', 'central'))]",
        help="Where a part sold over this branch's counter leaves the M15 ledger when the "
        "sale names no location. Unset: the one branch location holding the part, else the "
        "sale waits for its location.",
    )
