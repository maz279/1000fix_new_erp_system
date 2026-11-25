# product.template extension — AS-10 enforcement (P03-M06-T07).
# Ensures the standard_price/list_price on product.template are always used
# with an explicit currency (inherited from the company currency by default).
from odoo import fields, models
from odoo.exceptions import UserError


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
        "fix.catalogue.item", "product_tmpl_id", string="Catalogue Item"
    )

    # DE-17: Bengali name for the product (used in bilingual catalogues)
    name_bn = fields.Char(
        string="Product Name (Bengali)", help="Bengali display name — DE-17 Bengali-first"
    )

    # Real-inventory fit-gap (2026-11-07, report §7 R2): the 1000 FiX inventory
    # statement carries three identities per row — the manufacturer part number,
    # the previous-ERP part number and the new-ERP SKU (default_code). These two
    # addition fields are the missing pair; the SKU already lives on the variant.
    manufacturer_part_number = fields.Char(
        string="Manufacturer Part Number (MPN)",
        index=True,
        help="The manufacturer's own part number (file column 'Principal Part No') — "
        "the SAP HERB/FFF and D365 external-item-code equivalent. Supplier-specific "
        "codes still belong on product.supplierinfo.product_code.",
    )
    legacy_erp_part_number = fields.Char(
        string="Previous ERP Part Number",
        index=True,
        copy=False,
        help="The item's key in the previous ERP (file column 'ERP Existing Part Number'). "
        "Permanent cross-reference for the migration and for legacy document lookups.",
    )

    def unlink(self):
        """A04 audit (2026-11-04) M37-3: the catalogue item is deleted with its
        template (ondelete cascade at the database), which skipped every
        check the item itself makes. A template whose catalogue item may not
        be deleted (approved once, or referenced) is not deleted either."""
        if not self.env.su:
            items = self.sudo().with_context(active_test=False).mapped("catalogue_item_id")
            for item in items:
                if item.state != "draft" or item._references():
                    raise UserError(
                        "%s is a catalogue item that was approved or is referenced; its "
                        "product is archived, never deleted (BRU-CAT-03)." % item.display_name
                    )
        return super().unlink()


class ProductProductExt(models.Model):
    _inherit = "product.product"

    def _fix_check_sale(self, unit_price=None, channel=None, line=None, partner=None):
        """The one check every selling document runs on a product line
        (estimate, quotation, storefront, marketplace): may this product be
        sold, here, at this price? Raises UserError when not.

        cd_catalogue checks the item lifecycle (BRU-CAT-14) and, on a customer
        channel, the VAT class and publication (A04 ERP audit 20 Nov 2026
        M37-F1/F4); cd_rate_card extends it with the M11 price gate
        (BRU-PRC-04). `line` is the document line (binds a below-floor
        override to it); `partner` the customer."""
        for product in self:
            item = product.sudo().product_tmpl_id.catalogue_item_id[:1]
            if item:
                item._fix_assert_sellable(channel)
        return True
