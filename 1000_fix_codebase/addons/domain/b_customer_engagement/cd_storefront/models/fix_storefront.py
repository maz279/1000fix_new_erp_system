# fix_storefront — M38: cart, checkout, orders, returns (P10-M03 / R08-M03).
import logging
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

logger = logging.getLogger(__name__)


class FixStorefrontCart(models.Model):
    _name = "fix.storefront.cart"
    _description = "Storefront Cart"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    state = fields.Selection(
        [("open", "Open"), ("checkout", "Checkout"), ("ordered", "Ordered")],
        default="open",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.storefront.cart.line", "cart_id", string="Cart Lines")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    total = fields.Monetary(
        compute="_compute_total", string="Total", currency_field="currency_id", store=True
    )
    order_id = fields.Many2one("fix.storefront.order", string="Generated Order", readonly=True)

    @api.depends("line_ids.subtotal")
    def _compute_total(self):
        for rec in self:
            rec.total = sum(rec.line_ids.mapped("subtotal"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.storefront.cart")
                    or f"CART/{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        return super().create(vals_list)

    def action_checkout(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError("Cart is empty")
            rec.state = "checkout"

    def action_place_order(
        self, shipping_address=None, shipping_method="standard_delivery", payment_rail="bkash"
    ):
        """Checkout ONE cart and generate its customer storefront order.

        (The former loop returned inside its first iteration: on a multi-cart
        recordset every cart after the first was silently left unordered.)"""
        self.ensure_one()
        rec = self
        if not rec.line_ids:
            raise UserError("Cart is empty")
        # The address the customer gave, else the one on their record - never
        # an invented city. Only a branch pickup needs no delivery address.
        address = (shipping_address or "").strip() or (
            rec.customer_id.contact_address or ""
        ).strip()
        if not address:
            if shipping_method != "branch_pickup":
                raise UserError("A shipping address is required for home delivery")
            address = "Branch walk-in pickup"

        order_vals = {
            "cart_id": rec.id,
            "customer_id": rec.customer_id.id,
            "company_id": rec.company_id.id,
            "operating_unit_id": rec.operating_unit_id.id if rec.operating_unit_id else False,
            "currency_id": rec.currency_id.id,
            "total_amount": rec.total,
            "shipping_address": address,
            "shipping_method": shipping_method,
            "payment_rail": payment_rail,
            "state": "pending_payment",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "company_id": rec.company_id.id,
                        "operating_unit_id": rec.operating_unit_id.id
                        if rec.operating_unit_id
                        else False,
                        "product_id": line.product_id.id,
                        "quantity": line.quantity,
                        "currency_id": rec.currency_id.id,
                        "unit_price": line.unit_price,
                        "subtotal": line.subtotal,
                    },
                )
                for line in rec.line_ids
            ],
        }
        order = self.env["fix.storefront.order"].create(order_vals)
        rec.order_id = order.id
        rec.state = "ordered"

        publish(
            self.env,
            "storefront.order_placed",
            "fix.storefront.order",
            order.id,
            {
                "order_id": order.id,
                "order_name": order.name,
                "customer": rec.customer_id.name,
                "total": float(order.total_amount),
                "rail": payment_rail,
            },
        )
        return order


class FixStorefrontCartLine(models.Model):
    _name = "fix.storefront.cart.line"
    _description = "Storefront Cart Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    cart_id = fields.Many2one("fix.storefront.cart", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.template", string="Product", required=True)
    quantity = fields.Float(default=1, required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id", required=True)
    subtotal = fields.Monetary(
        compute="_compute_subtotal", string="Subtotal", currency_field="currency_id", store=True
    )

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.unit_price

    @api.constrains("quantity")
    def _check_qty(self):
        for rec in self:
            if rec.quantity <= 0:
                raise UserError("Quantity must be positive")


class FixStorefrontOrder(models.Model):
    """M38: Placed Storefront Order with Payment Rail and Fulfillment Tracking."""

    _name = "fix.storefront.order"
    _description = "Storefront Customer Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(
        string="Order Reference", required=True, copy=False, readonly=True, default="New"
    )
    cart_id = fields.Many2one("fix.storefront.cart", string="Originating Cart", readonly=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    order_date = fields.Datetime(string="Order Date", default=fields.Datetime.now, required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    total_amount = fields.Monetary(
        string="Total Amount", currency_field="currency_id", required=True
    )
    shipping_address = fields.Text(string="Shipping Address", required=True)
    shipping_method = fields.Selection(
        [
            ("standard_delivery", "Standard Home Delivery (48h)"),
            ("express_courier", "Express Courier (24h)"),
            ("branch_pickup", "Branch Walk-in Pickup"),
        ],
        default="standard_delivery",
        required=True,
    )
    carrier_consignment_id = fields.Many2one(
        "fix.consignment",
        string="Logistics Consignment",
        help="Linked M03 consignment tracking fulfillment",
    )
    payment_rail = fields.Selection(
        [
            ("bkash", "bKash Direct Pay"),
            ("nagad", "Nagad Direct Pay"),
            ("sslcommerz", "SSLCOMMERZ Card / Gateway"),
            ("cod", "Cash on Delivery"),
        ],
        default="bkash",
        required=True,
    )
    payment_ref = fields.Char(string="Payment Rail Reference / TrxID")
    payment_date = fields.Datetime(string="Payment Date")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending_payment", "Pending Payment"),
            ("paid", "Payment Confirmed"),
            ("dispatched", "Dispatched for Delivery"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelled"),
        ],
        default="pending_payment",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.storefront.order.line", "order_id", string="Order Items")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.storefront.order")
                    or f"SO/{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        return super().create(vals_list)

    def action_confirm_payment(self, payment_ref=None, rail=None):
        """Mark the order paid on the payment gateway's REAL transaction
        reference (bKash/Nagad TrxID, SSLCOMMERZ val_id, COD receipt). Without
        one the order stays unpaid - a reference is never generated here."""
        for rec in self:
            if rec.state == "paid":
                continue
            if rec.state not in ("draft", "pending_payment"):
                raise UserError(
                    "Order %s is '%s': only an unpaid order can be confirmed paid"
                    % (rec.name, rec.state)
                )
            reference = (payment_ref or rec.payment_ref or "").strip()
            if not reference:
                raise UserError(
                    "Payment confirmation needs the gateway transaction reference (TrxID)"
                )
            rec.payment_ref = reference
            if rail:
                rec.payment_rail = rail
            rec.payment_date = fields.Datetime.now()
            rec.state = "paid"
            publish(
                self.env,
                "storefront.payment_confirmed",
                "fix.storefront.order",
                rec.id,
                {
                    "order_id": rec.id,
                    "order_name": rec.name,
                    "payment_ref": rec.payment_ref,
                    "rail": rec.payment_rail,
                    "total": float(rec.total_amount),
                },
            )

    def action_dispatch(self, carrier_consignment_id=None):
        """Dispatch only a PAID order; a cash-on-delivery order may leave
        unpaid (payment is collected at the door)."""
        for rec in self:
            cod_unpaid = rec.payment_rail == "cod" and rec.state == "pending_payment"
            if rec.state != "paid" and not cod_unpaid:
                raise UserError("Order must be paid before dispatch")
            if carrier_consignment_id:
                rec.carrier_consignment_id = carrier_consignment_id
            rec.state = "dispatched"
            publish(
                self.env,
                "storefront.order_dispatched",
                "fix.storefront.order",
                rec.id,
                {"order_id": rec.id, "order_name": rec.name},
            )

    def action_deliver(self):
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Only a dispatched order can be delivered")
            rec.state = "delivered"

    def action_cancel(self):
        """Cancel before dispatch only; a shipped order goes through a return."""
        for rec in self:
            if rec.state not in ("draft", "pending_payment", "paid"):
                raise UserError(
                    "Order %s is '%s': it can no longer be cancelled (use a return)"
                    % (rec.name, rec.state)
                )
            rec.state = "cancelled"


class FixStorefrontOrderLine(models.Model):
    _name = "fix.storefront.order.line"
    _description = "Storefront Order Item Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    order_id = fields.Many2one("fix.storefront.order", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.template", string="Product Item", required=True)
    quantity = fields.Float(string="Quantity", default=1, required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id", required=True)
    subtotal = fields.Monetary(string="Subtotal", currency_field="currency_id", required=True)


class FixStorefrontReturn(models.Model):
    _name = "fix.storefront.return"
    _description = "Storefront Return & Reverse Logistics"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="RMA Number", required=True, copy=False, default="New")
    cart_id = fields.Many2one("fix.storefront.cart", string="Original Cart", ondelete="set null")
    order_id = fields.Many2one("fix.storefront.order", string="Original Order", ondelete="set null")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    reason = fields.Selection(
        [
            ("defective", "Defective Item"),
            ("wrong_item", "Wrong Item Delivered"),
            ("not_as_described", "Not As Described"),
            ("changed_mind", "Customer Changed Mind"),
        ],
        required=True,
        default="defective",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    refund_amount = fields.Monetary(string="Refund Amount", currency_field="currency_id")
    carrier_consignment_id = fields.Many2one(
        "fix.consignment",
        string="Reverse Logistics Consignment",
        help="M03 reverse logistics courier pickup",
    )
    inspected_condition = fields.Selection(
        [
            ("grade_a", "Grade A (Like New / Resalable)"),
            ("grade_b", "Grade B (Minor Wear / Refurbishable)"),
            ("scrap", "Damaged / Scrap Only"),
        ],
        string="Inspection Result",
    )
    state = fields.Selection(
        [
            ("requested", "Return Requested"),
            ("approved", "Return Approved"),
            ("received", "Item Received & Inspected"),
            ("refunded", "Refund Disbursed"),
            ("rejected", "Return Rejected"),
        ],
        default="requested",
        required=True,
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.storefront.return")
                    or f"RMA/{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            if rec.state != "requested":
                raise UserError("Only a requested return can be approved")
            rec.state = "approved"

    def action_receive_and_inspect(self, condition=None):
        """Record the inspector's result - never a default grade."""
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved return can be received")
            result = condition or rec.inspected_condition
            if not result:
                raise UserError("Record the inspection result before receiving the return")
            rec.inspected_condition = result
            rec.state = "received"

    def action_approve_refund(self):
        for rec in self:
            if rec.state != "received":
                raise UserError("Cannot refund prior to physical receipt and inspection")
            rec.state = "refunded"
            publish(
                self.env,
                "storefront.refund_processed",
                "fix.storefront.return",
                rec.id,
                {
                    "rma_number": rec.name,
                    "customer": rec.customer_id.name,
                    "refund_amount": float(rec.refund_amount or 0.0),
                    "condition": rec.inspected_condition,
                },
            )
