# fix.service.kit — a service defined as a bundle of parts, labour and time
# (P03-M06-T02). A kit is a template: when a service order (M01) uses it,
# the individual components are consumed, not the kit itself.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .catalogue_roles import ROLE_OFFICER, require_role

# The help text has always said a kit sits on a bundle or a service item; a
# kit on a spare part made the part explode into itself (A04 audit M37-4).
KIT_ITEM_TYPES = ("bundle", "service", "inspection", "protection")


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
        # A04 audit (2026-11-04) M37-3: deleting the item cascaded its kits
        # away; a referenced item is now kept (BRU-CAT-03).
        ondelete="restrict",
        index=True,
        help="The parent catalogue item — a bundle, service, inspection or protection item",
    )
    component_ids = fields.One2many(
        "fix.service.kit.component",
        "kit_id",
        string="Components",
        help="The parts, labour items and time allocations that make up this kit",
    )
    # M37 capture audit, third pass (2026-11-19), FR-CAT-041: a bundle has
    # required and optional lines, substitution rules and an explosion point.
    explode_at = fields.Selection(
        [
            ("quotation", "At quotation (lines shown to the customer)"),
            ("issue", "At issue (one line sold, parts issued separately)"),
            ("both", "At quotation and at issue"),
        ],
        string="Explodes",
        required=True,
        default="both",
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

    @api.constrains("catalogue_item_id")
    def _check_item_type(self):
        for kit in self:
            if kit.catalogue_item_id.item_type not in KIT_ITEM_TYPES:
                raise ValidationError(
                    "A service kit sits on a bundle, service, inspection or protection item, "
                    "not on a %s item (%s)."
                    % (
                        dict(kit.catalogue_item_id._fields["item_type"].selection).get(
                            kit.catalogue_item_id.item_type
                        ),
                        kit.catalogue_item_id.name,
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Changing a service kit")
        kits = super().create(vals_list)
        # @api.constrains only fires for fields present in the vals: a kit
        # created without a component_ids key would bypass the invariant.
        kits._check_has_components()
        return kits

    def write(self, vals):
        require_role(self.env, (ROLE_OFFICER,), "Changing a service kit")
        return super().write(vals)

    def unlink(self):
        require_role(self.env, (ROLE_OFFICER,), "Deleting a service kit")
        return super().unlink()


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
    is_optional = fields.Boolean(
        string="Optional", help="Offered with the kit but not required (an add-on line)."
    )
    substitution = fields.Selection(
        [
            ("none", "No substitute"),
            ("crossref", "Any approved cross-reference / alternate"),
            ("any_grade", "Any provenance grade of the same part"),
        ],
        string="Substitution",
        required=True,
        default="none",
    )

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

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Changing a service kit")
        return super().create(vals_list)

    def write(self, vals):
        require_role(self.env, (ROLE_OFFICER,), "Changing a service kit")
        return super().write(vals)

    def unlink(self):
        """A04 audit M37-4 (kit_02): the one-component invariant was checked
        only when the kit was written, so deleting the components directly
        left an empty kit. A kit losing its last component is refused; a kit
        deleted with its components is not (that path never calls this)."""
        require_role(self.env, (ROLE_OFFICER,), "Changing a service kit")
        kits = self.mapped("kit_id")
        for kit in kits:
            if not (kit.component_ids - self):
                raise ValidationError(
                    "Service kit '%s' must have at least one component; add its "
                    "replacement before removing the last one." % kit.name
                )
        return super().unlink()

    @api.depends("quantity", "standard_cost")
    def _compute_subtotal_cost(self):
        for rec in self:
            rec.subtotal_cost = round((rec.quantity or 0.0) * (rec.standard_cost or 0.0), 2)
