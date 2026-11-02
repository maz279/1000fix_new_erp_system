# fix.catalogue.item — catalogue metadata on product.template (P03-M06-T01).
# The catalogue kernel: every downstream module (M01, M11, M12, M13, M14, M15)
# consumes this rather than re-inventing product concepts.
import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

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
    # Without a name source Odoo falls back to "model,id" for display_name,
    # so EVERY many2one pointing at a catalogue item rendered as
    # "fix.catalogue.item,19739" - on the kit list, on estimates, anywhere
    # one was shown. The catalogue wraps a product.template one-to-one, so
    # the product's name is its name.
    # (A04 audit, 2026-11-01, raised from the M37 Kits & Bundles panel.)
    #
    # Done as a compute, NOT as a stored related Char. product.template.name
    # is translatable (jsonb), and Odoo warns that a stored related on a
    # translated field "will not be computed correctly in all languages" -
    # which in a bilingual-by-mandate estate (DE-17) means a Bengali session
    # could read a stale English name. Resolving through the relation each
    # time is always right in the active language.

    # AS-03: company_id + operating_unit_id
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product Template",
        required=True,
        ondelete="cascade",
        index=True,
        help="The product this catalogue item wraps — one-to-one",
    )
    # The English name, mirroring the wrapped product template - the pair to
    # name_bn below, declared the same way for the same reason.
    #
    # This is NOT optional decoration: without it fix.catalogue.item has no
    # name source at all, Odoo falls back to "model,id", and every many2one
    # pointing here renders as "fix.catalogue.item,19739" - on kits, rate
    # cards, rBOM lines, rental SKUs and price simulations.
    #
    # READ-ONLY on purpose. name_bn was once writable here and editing it
    # overwrote the product's English name (R01 re-audit 2026-10-22).
    #
    # Removing this field DROPS the column, and a running Odoo whose registry
    # still expects it then fails every read of this model with
    # UndefinedColumn. Do not delete it without restarting the server
    # (A04 audit, 2026-11-01).
    name = fields.Char(
        related="product_tmpl_id.name",
        string="Name",
        store=True,
        readonly=True,
        index=True,
    )

    # DE-17 Bengali-first
    # R01 re-audit 2026-10-22: this mirrored product_tmpl_id.NAME (the English,
    # translatable name) - the "Bengali" column showed English, and editing it
    # overwrote the product's English name. It mirrors the Bengali name.
    name_bn = fields.Char(
        related="product_tmpl_id.name_bn", string="Name (Bengali)", readonly=False, store=True
    )
    description_bn = fields.Char(string="Description (Bengali)")

    # Catalogue classification
    item_type = fields.Selection(
        [
            ("service", "Service"),
            ("part", "Spare Part"),
            ("accessory", "Accessory"),
            ("bundle", "Bundle / Kit"),
            ("labour", "Labour Only"),
            ("inspection", "Inspection / Diagnostic"),
            # M37 re-audit: the registry's form promises NINE catalogue item
            # types (FR-CAT); the enum only had six. The protection, rental and
            # subscription SKU families are now first-class types.
            ("protection", "Protection Plan"),
            ("rental", "Rental SKU"),
            ("subscription", "Subscription / Contract"),
        ],
        required=True,
        default="service",
        tracking=True,
        help="The catalogue item type determines which modules may consume it",
    )
    category_id = fields.Many2one(
        "product.category",
        string="Product Category",
        help="Odoo's own category tree; the catalogue's organisational spine",
    )
    brand_id = fields.Many2one(
        "fix.brand", string="Brand", help="Brand master — 17+ brand partners"
    )
    device_model_ids = fields.Many2many(
        "fix.device.model",
        string="Compatible Device Models",
        help="Which device models this item is compatible with",
    )

    # AS-10 (FF-22): every price is Monetary with explicit currency_id.
    # NEVER Float for a price field.
    standard_labour_time = fields.Float(
        string="Standard Labour Time (hours)",
        help="The estimated labour hours for this service — used by M01 for "
        "scheduling and M54 for cost allocation",
    )

    # Flags
    is_warranty_eligible = fields.Boolean(
        default=True,
        tracking=True,
        help="Whether this item can be serviced under manufacturer warranty",
    )
    is_out_of_scope = fields.Boolean(
        default=False, help="Items marked out-of-scope are refused at intake (M01)"
    )
    requires_brand_authorisation = fields.Boolean(
        default=False, help="True for items that only a brand-authorised technician may handle"
    )
    active = fields.Boolean(default=True, tracking=True)

    # M37 lifecycle & publication (v2 rebuild): the registry promises an
    # approval queue, a lifecycle view and a publication/Bilingual-gap
    # report — those need a state, an approver and a public flag.
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("published", "Published"),
            ("deprecated", "Deprecated"),
        ],
        required=True,
        default="draft",
        tracking=True,
        index=True,
    )
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    is_published = fields.Boolean(
        string="Published on the Web", help="Visible in the public catalogue."
    )
    srt_observed_minutes = fields.Float(
        string="Observed Repair Minutes",
        help="Measured workshop time for the SRT calibration-variance report.",
    )

    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _product_tmpl_unique = models.Constraint(
        "UNIQUE (product_tmpl_id)", "Each product.template maps to exactly one catalogue item"
    )

    @api.constrains("state", "is_published", "name_bn")
    def _check_bengali_name_on_publish(self):
        """Bangla-first catalogue integrity gate (FLAW-37.1)."""
        for rec in self:
            if (rec.state == "published" or rec.is_published) and not (
                rec.name_bn and rec.name_bn.strip()
            ):
                raise ValidationError(
                    f"Catalogue Item '{rec.product_tmpl_id.name or rec.id}' cannot be published without a Bengali name (name_bn). "
                    "Bangla-first catalogue compliance is mandatory."
                )

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

        publish(
            self.env,
            event_type,
            "fix.catalogue.item",
            rec.id,
            {
                "product_tmpl_id": rec.product_tmpl_id.id,
                "item_type": rec.item_type,
                "brand_id": rec.brand_id.id if rec.brand_id else None,
            },
        )
