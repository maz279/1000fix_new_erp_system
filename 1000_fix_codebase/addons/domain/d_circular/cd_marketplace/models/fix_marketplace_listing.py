# M12 marketplace listings: the seller's published service listing.
from odoo import fields, models


class FixMarketplaceListing(models.Model):
    _name = "fix.marketplace.listing"
    _description = "Marketplace Listing"
    _order = "name"

    name = fields.Char(string="Listing Title", required=True)
    seller_id = fields.Many2one(
        "fix.marketplace.seller", required=True, ondelete="cascade", index=True
    )
    category_id = fields.Many2one("product.category", string="Category")
    list_price = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    description = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("paused", "Paused"), ("removed", "Removed")],
        required=True,
        default="draft",
    )
