# fix.catalogue.item — catalogue metadata on product.template (P03-M06-T01).
# The catalogue kernel: every downstream module (M01, M11, M12, M13, M14, M15)
# consumes this rather than re-inventing product concepts.
from odoo import api, fields, models

import logging

logger = logging.getLogger(__name__)


class FixCatalogueItem(models.Model):
    """Catalogue metadata for a product or service.

    Extends product.template via a separate model — one catalogue item per
    product.template. The TSS §3.2 kernel row 2: "a single product catalogue
    with service kits, parts, bundles".
    """
    _name = "fix.catalogue.item"
    _description = "Catalogue Item"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "product_tmpl_id"

    # AS-03: company_id + operating_unit_id
    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    product_tmpl_id = fields.Many2one(
        "product.template", string="Product Template", required=True,
        ondelete="cascade", index=True,
        help="The product this catalogue item wraps — one-to-one")
    # DE-17 Bengali-first
    name_bn = fields.Char(related="product_tmpl_id.name", string="Name",
                          readonly=False, store=True)
    description_bn = fields.Char(string="Description (Bengali)")

    # Catalogue classification
    item_type = fields.Selection(
        [("service", "Service"), ("part", "Spare Part"), ("accessory", "Accessory"),
         ("bundle", "Bundle / Kit"), ("labour", "Labour Only"),
         ("inspection", "Inspection / Diagnostic")],
        required=True, default="service", tracking=True,
        help="The catalogue item type determines which modules may consume it")
    category_id = fields.Many2one(
        "product.category", string="Product Category",
        help="Odoo's own category tree; the catalogue's organisational spine")
    brand_id = fields.Many2one("fix.brand", string="Brand",
                               help="Brand master — 17+ brand partners")
    device_model_ids = fields.Many2many(
        "fix.device.model", string="Compatible Device Models",
        help="Which device models this item is compatible with")

    # AS-10 (FF-22): every price is Monetary with explicit currency_id.
    # NEVER Float for a price field.
    standard_labour_time = fields.Float(
        string="Standard Labour Time (hours)",
        help="The estimated labour hours for this service — used by M01 for "
             "scheduling and M54 for cost allocation")

    # Flags
    is_warranty_eligible = fields.Boolean(
        default=True, tracking=True,
        help="Whether this item can be serviced under manufacturer warranty")
    is_out_of_scope = fields.Boolean(
        default=False,
        help="Items marked out-of-scope are refused at intake (M01)")
    requires_brand_authorisation = fields.Boolean(
        default=False,
        help="True for items that only a brand-authorised technician may handle")
    active = fields.Boolean(default=True, tracking=True)

    _sql_constraints = [
        ("product_tmpl_unique", "unique(product_tmpl_id)",
         "Each product.template maps to exactly one catalogue item"),
    ]

    # Event emission (AS-08)
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            self._emit("catalogue.item_created", rec)
        return records

    def write(self, vals):
        result = super().write(vals)
        if "is_out_of_scope" in vals or "is_warranty_eligible" in vals:
            for rec in self:
                self._emit("catalogue.item_changed", rec)
        return result

    def _emit(self, event_type: str, rec) -> None:
        from libs.py.fix_events import publish
        publish(self.env, event_type, "fix.catalogue.item", rec.id, {
            "product_tmpl_id": rec.product_tmpl_id.id,
            "item_type": rec.item_type,
            "brand_id": rec.brand_id.id if rec.brand_id else None,
        })
