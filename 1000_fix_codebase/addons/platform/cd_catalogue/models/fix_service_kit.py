# fix.service.kit — a service defined as a bundle of parts, labour and time
# (P03-M06-T02). A kit is a template: when a service order (M01) uses it,
# the individual components are consumed, not the kit itself.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixServiceKit(models.Model):
    """A service kit: a bundle of parts + labour + time.

    Example: "Screen Replacement — Samsung Galaxy S24" = 1× screen part
    + 1.5 hours labour + diagnostic checklist. When M01 creates a service
    order from this kit, the components are expanded and consumed.
    """

    _name = "fix.service.kit"
    _description = "Service Kit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17 Bengali-first")
    description = fields.Text()
    catalogue_item_id = fields.Many2one(
        "fix.catalogue.item",
        string="Catalogue Item",
        required=True,
        ondelete="cascade",
        index=True,
        help="The parent catalogue item — must be type 'bundle' or 'service'",
    )
    component_ids = fields.One2many(
        "fix.service.kit.component",
        "kit_id",
        string="Components",
        help="The parts, labour items and time allocations that make up this kit",
    )

    # AS-10: Monetary with explicit currency_id — NEVER Float
    estimated_cost = fields.Monetary(
        string="Estimated Cost",
        currency_field="currency_id",
        compute="_compute_estimated",
        store=True,
        help="Sum of component standard costs",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.ref("base.BDT"),
        help="AS-10: explicit currency for every Monetary field",
    )

    # Time
    estimated_time = fields.Float(
        string="Estimated Time (hours)",
        compute="_compute_estimated",
        store=True,
        help="Sum of component times — consumed by M02 for dispatch scheduling",
    )
    component_count = fields.Integer(
        string="Components",
        compute="_compute_component_count",
        store=True,
        help="How many parts/labour rows this kit contains. A kit list that "
        "shows only a name and two computed totals gives no way to tell a "
        "one-line kit from a twenty-line one (A04 audit, 2026-11-01).",
    )
    active = fields.Boolean(default=True, tracking=True)

    @api.depends("component_ids")
    def _compute_component_count(self):
        for kit in self:
            kit.component_count = len(kit.component_ids)

    @api.depends(
        "component_ids.subtotal_cost",
        "component_ids.standard_cost",
        "component_ids.quantity",
        "component_ids.time_allocation",
    )
    def _compute_estimated(self):
        for kit in self:
            kit.estimated_cost = sum(c.subtotal_cost for c in kit.component_ids)
            kit.estimated_time = sum(kit.component_ids.mapped("time_allocation"))

    @api.constrains("component_ids")
    def _check_has_components(self):
        for kit in self:
            if not kit.component_ids:
                raise ValidationError(f"Service kit '{kit.name}' must have at least one component.")

    is_costed = fields.Boolean(
        string="Fully Costed",
        compute="_compute_is_costed",
        store=True,
        help="False while any component carries neither a cost nor a time, "
        "so a kit that cannot price or schedule the work it describes is "
        "visible as such instead of quietly reporting zero.",
    )

    @api.depends("component_ids.standard_cost", "component_ids.time_allocation")
    def _compute_is_costed(self):
        for kit in self:
            comps = kit.component_ids
            kit.is_costed = bool(comps) and all(
                (c.standard_cost or 0.0) > 0.0 or (c.time_allocation or 0.0) > 0.0 for c in comps
            )

    @api.model_create_multi
    def create(self, vals_list):
        kits = super().create(vals_list)
        # @api.constrains only fires for fields present in the vals: a kit
        # created without a component_ids key would bypass the invariant.
        kits._check_has_components()
        return kits


class FixServiceKitComponent(models.Model):
    """A single component (part, labour, or time allocation) within a kit."""

    _name = "fix.service.kit.component"
    _description = "Service Kit Component"

    kit_id = fields.Many2one("fix.service.kit", required=True, ondelete="cascade")
    component_type = fields.Selection(
        [
            ("part", "Spare Part"),
            ("labour", "Labour"),
            ("diagnostic", "Diagnostic"),
            ("consumable", "Consumable"),
        ],
        required=True,
        default="part",
    )
    product_id = fields.Many2one(
        "product.product", string="Product", help="The specific product variant for this component"
    )
    quantity = fields.Float(default=1.0, required=True, digits="Product Unit of Measure")
    # AS-10: Monetary
    standard_cost = fields.Monetary(
        string="Standard Cost",
        currency_field="currency_id",
        default=0.0,
        help="The per-unit cost used for kit cost estimation",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    time_allocation = fields.Float(
        string="Time Allocation (hours)",
        default=0.0,
        help="How many technician-hours this component consumes (labour only)",
    )
    subtotal_cost = fields.Monetary(
        string="Subtotal Cost",
        currency_field="currency_id",
        compute="_compute_subtotal_cost",
        store=True,
        help="Total component cost = quantity * standard_cost",
    )
    notes = fields.Char()

    @api.constrains("product_id", "notes", "quantity")
    def _check_component_is_identified(self):
        """A component must say WHAT it is.

        The seeded kit carried a component with no product, no description,
        no cost and no time - it contributed nothing to the kit's estimated
        cost or estimated time, which is why both read zero. Cost and time
        may be zero (an included step); anonymity may not
        (A04 audit, 2026-11-01).
        """
        for comp in self:
            if not comp.product_id and not (comp.notes or "").strip():
                raise ValidationError(
                    "A kit component must name a product or carry a "
                    "description - kit '%s' has a component that identifies "
                    "nothing." % (comp.kit_id.name or "?")
                )
            if (comp.quantity or 0.0) <= 0.0:
                raise ValidationError(
                    "A kit component needs a positive quantity (kit '%s')."
                    % (comp.kit_id.name or "?")
                )

    @api.depends("quantity", "standard_cost")
    def _compute_subtotal_cost(self):
        for rec in self:
            rec.subtotal_cost = round((rec.quantity or 0.0) * (rec.standard_cost or 0.0), 2)
