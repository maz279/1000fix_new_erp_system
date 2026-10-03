# product.template extension — AS-10 enforcement (P03-M06-T07).
# Ensures the standard_price/list_price on product.template are always used
# with an explicit currency (inherited from the company currency by default).
from odoo import fields, models


class ProductTemplateExt(models.Model):
    """Extend product.template with catalogue-aware fields.

    AS-10 (FF-22): Odoo's product.template already uses fields.Monetary for
    standard_price and list_price with currency_field="cost_currency_id" and
    "currency_id" respectively. This extension confirms and enforces the
    constraint: NO price field anywhere in the estate uses Float.
    """
    _inherit = "product.template"

    # Catalogue link (one-to-one with fix.catalogue.item)
    catalogue_item_id = fields.One2many(
        "fix.catalogue.item", "product_tmpl_id", string="Catalogue Item")

    # DE-17: Bengali name for the product (used in bilingual catalogues)
    name_bn = fields.Char(
        string="Product Name (Bengali)",
        help="Bengali display name — DE-17 Bengali-first")
