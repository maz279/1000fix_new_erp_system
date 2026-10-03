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

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17 Bengali-first")
    description = fields.Text()
    catalogue_item_id = fields.Many2one(
        "fix.catalogue.item", string="Catalogue Item", required=True,
        ondelete="cascade", index=True,
        help="The parent catalogue item — must be type 'bundle' or 'service'")
    component_ids = fields.One2many(
        "fix.service.kit.component", "kit_id", string="Components",
        help="The parts, labour items and time allocations that make up this kit")

    # AS-10: Monetary with explicit currency_id — NEVER Float
    estimated_cost = fields.Monetary(
        string="Estimated Cost", currency_field="currency_id",
        compute="_compute_estimated", store=True,
        help="Sum of component standard costs")
    currency_id = fields.Many2one(
        "res.currency", string="Currency", required=True,
        default=lambda self: self.env.ref("base.BDT"),
        help="AS-10: explicit currency for every Monetary field")

    # Time
    estimated_time = fields.Float(
        string="Estimated Time (hours)", compute="_compute_estimated", store=True,
        help="Sum of component times — consumed by M02 for dispatch scheduling")
    active = fields.Boolean(default=True, tracking=True)

    @api.depends("component_ids.standard_cost", "component_ids.time_allocation")
    def _compute_estimated(self):
        for kit in self:
            kit.estimated_cost = sum(kit.component_ids.mapped("standard_cost"))
            kit.estimated_time = sum(kit.component_ids.mapped("time_allocation"))

    @api.constrains("component_ids")
    def _check_has_components(self):
        for kit in self:
            if not kit.component_ids:
                raise ValidationError(
                    f"Service kit '{kit.name}' must have at least one component.")


class FixServiceKitComponent(models.Model):
    """A single component (part, labour, or time allocation) within a kit."""
    _name = "fix.service.kit.component"
    _description = "Service Kit Component"

    kit_id = fields.Many2one("fix.service.kit", required=True, ondelete="cascade")
    component_type = fields.Selection(
        [("part", "Spare Part"), ("labour", "Labour"),
         ("diagnostic", "Diagnostic"), ("consumable", "Consumable")],
        required=True, default="part")
    product_id = fields.Many2one(
        "product.product", string="Product",
        help="The specific product variant for this component")
    quantity = fields.Float(default=1.0, required=True,
                            digits="Product Unit of Measure")
    # AS-10: Monetary
    standard_cost = fields.Monetary(
        string="Standard Cost", currency_field="currency_id", default=0.0,
        help="The per-unit cost used for kit cost estimation")
    currency_id = fields.Many2one(
        "res.currency", required=True,
        default=lambda self: self.env.ref("base.BDT"))
    time_allocation = fields.Float(
        string="Time Allocation (hours)", default=0.0,
        help="How many technician-hours this component consumes (labour only)")
    notes = fields.Char()
