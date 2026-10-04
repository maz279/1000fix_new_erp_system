# fix_storefront — M38: cart, checkout, returns (P10-M03).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixStorefrontCart(models.Model):
    _name = "fix.storefront.cart"
    _description = "Storefront Cart"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True,
                       default="New")
    customer_id = fields.Many2one("res.partner", string="Customer",
                                   required=True)
    state = fields.Selection([("open", "Open"), ("checkout", "Checkout"),
                              ("ordered", "Ordered")],
                              default="open", required=True, tracking=True)
    line_ids = fields.One2many("fix.storefront.cart.line", "cart_id",
                                string="Cart Lines")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    total = fields.Monetary(compute="_compute_total", string="Total",
                             currency_field="currency_id")

    @api.depends("line_ids.subtotal")
    def _compute_total(self):
        for rec in self:
            rec.total = sum(rec.line_ids.mapped("subtotal"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fix.storefront.cart") or "CART/New"
        return super().create(vals_list)

    def action_checkout(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError("Cart is empty")
            rec.state = "checkout"

    def action_place_order(self):
        for rec in self:
            rec.state = "ordered"
            publish(self.env, "storefront.order_placed",
                    "fix.storefront.cart", rec.id,
                    {"customer": rec.customer_id.name,
                     "total": float(rec.total)})


class FixStorefrontCartLine(models.Model):
    _name = "fix.storefront.cart.line"
    _description = "Storefront Cart Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    cart_id = fields.Many2one("fix.storefront.cart", required=True,
                               ondelete="cascade")
    product_id = fields.Many2one("product.template", string="Product",
                                  required=True)
    quantity = fields.Float(default=1, required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    unit_price = fields.Monetary(string="Unit Price",
                                  currency_field="currency_id", required=True)
    subtotal = fields.Monetary(compute="_compute_subtotal",
                                string="Subtotal",
                                currency_field="currency_id", store=True)

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.unit_price

    @api.constrains("quantity")
    def _check_qty(self):
        for rec in self:
            if rec.quantity <= 0:
                raise UserError("Quantity must be positive")


class FixStorefrontReturn(models.Model):
    _name = "fix.storefront.return"
    _description = "Storefront Return"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    cart_id = fields.Many2one("fix.storefront.cart", string="Original Order",
                               ondelete="set null")
    customer_id = fields.Many2one("res.partner", string="Customer",
                                   required=True)
    reason = fields.Selection(
        [("defective", "Defective"), ("wrong_item", "Wrong Item"),
         ("not_as_described", "Not As Described"), ("changed_mind", "Changed Mind")],
        required=True, default="defective")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    refund_amount = fields.Monetary(string="Refund Amount",
                                     currency_field="currency_id")
    state = fields.Selection([("requested", "Requested"), ("approved", "Approved"),
                              ("received", "Received"), ("refunded", "Refunded")],
                              default="requested", required=True, tracking=True)
