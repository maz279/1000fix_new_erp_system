# cd_storefront_finance — the storefront order as a source of the M15
# valuation suspense (the stock movement the period close moves to GL).
from odoo import fields, models

SOURCE = "storefront_sale"


def _suspense_to_shipment(rows):
    """Uninstalling the bridge keeps its suspense rows as stock that left the
    company (same sign convention: the row carries the movement itself)."""
    rows.sudo()._guarded().write({"entry_type": "shipment"})


class FixValuationSuspenseStorefront(models.Model):
    _inherit = "fix.inventory.valuation.suspense"

    # STOCK_EFFECT has no entry for it: the default (+1) is right, the row
    # carries the movement itself (a dispatch -, a return's restock +)
    entry_type = fields.Selection(
        selection_add=[(SOURCE, "Storefront Sale")], ondelete={SOURCE: _suspense_to_shipment}
    )
