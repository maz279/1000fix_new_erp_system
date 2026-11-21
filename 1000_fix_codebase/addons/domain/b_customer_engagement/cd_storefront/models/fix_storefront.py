# fix_storefront — M38: cart, checkout, orders, returns (P10-M03 / R08-M03).
#
# A04 workflow audit (2026-11-03) M38-1/2/8/11/12/14/15: an order's state was
# written straight to "paid" or "delivered"; any internal user confirmed a
# payment on a typed TrxID, and one TrxID paid two orders; the total was
# lowered after placement and then paid; delivery needed no consignment or
# proof of delivery; graded stock and delivery slots were never linked to an
# order (a slot took 50 bookings against a capacity of 10); the stored SLA
# status froze; and cancelling a paid order raised no refund. Now:
#   - state, payment, total, consignment and delivery stamps are guarded
#     (fix.guarded.mixin) and move only through the actions below;
#   - payment is confirmed by the gateway callback (verified signature, the
#     superuser service _sf_gateway_confirm) or by a payment officer against a
#     confirmed M20 receipt of this customer covering the total; one TrxID and
#     one receipt pay one order;
#   - the total is the sum of the lines, set at placement and frozen;
#   - dispatch needs a consignment, delivery needs it delivered (M03 POD);
#   - graded stock is reserved at placement and sold on delivery; the slot's
#     bookings are its orders, never above its capacity.
import logging
from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_storefront_refund import GROUP_OPERATOR, GROUP_PAYMENT

logger = logging.getLogger(__name__)

# A04 audit (2026-11-04): an open cart untouched this long is abandoned and
# handed to the M35 recovery journeys (storefront.cart_abandoned). A default
# the business must confirm.
CART_ABANDON_HOURS_PARAM = "cd_storefront.cart_abandon_hours"
CART_ABANDON_HOURS_DEFAULT = 24

PAID_STATES = ("paid", "dispatched", "delivered")

# A04 ERP audit (20 Nov 2026) M38-F7 / AUT-ECM-08: a prepaid order the
# gateway never confirmed is cancelled after this many minutes and its
# reservations released. A DEFAULT THE BUSINESS MUST CONFIRM (OWNER).
PAYMENT_TIMEOUT_PARAM = "cd_storefront.payment_timeout_minutes"
PAYMENT_TIMEOUT_DEFAULT = 60

# M38-F13 / X7: the signed-callback secret of each rail (storefront_api).
GATEWAY_SECRET_PARAM = "cd_storefront.gateway_secret.%s"  # noqa: S105 - a key name


def _whole_units(qty) -> bool:
    """M38-F4: the storefront sells whole units (0.01 of a charger paid 1%)."""
    try:
        return float(qty) > 0 and abs(float(qty) - round(float(qty))) < 1e-9
    except (TypeError, ValueError):
        return False


ORDER_GUARDED = frozenset(
    {
        "state",
        "cart_id",
        "customer_id",
        "currency_id",
        "total_amount",
        "payment_rail",
        "payment_ref",
        "payment_date",
        "payment_source",
        "payment_receipt_id",
        "payment_confirmed_by_id",
        "carrier_consignment_id",
        "slot_id",
        "dispatched_by_id",
        "delivered_at",
        "delivered_by_id",
        "returns_closed",
        "refund_due",
        "cancelled_by_id",
        "placed_by_id",
        "payment_expires_at",
        "posting_state",
    }
)


def _require(env, xmlids, what):
    """Refuse unless the acting user holds one of the roles (superuser code is
    trusted: the gateway callback, crons, the M20 bridge)."""
    if env.su or any(env.user.has_group(x) for x in xmlids):
        return
    names = " or ".join(env.ref(x).name for x in xmlids)
    raise UserError("%s needs the %s role." % (what, names))


class FixStorefrontCart(models.Model):
    _name = "fix.storefront.cart"
    _description = "Storefront Cart"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

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
    abandon_notified_at = fields.Datetime(string="Abandonment Published", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        # A04 audit C2: the cart's stage and the order it produced change only
        # through checkout and placement.
        return super()._fix_guarded_fields() | {"state", "order_id", "abandon_notified_at"}

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
            if rec.state == "ordered":
                raise UserError("Cart %s has already been ordered" % rec.name)
            if not rec.line_ids:
                raise UserError("Cart is empty")
            rec._guarded().write({"state": "checkout"})

    def action_place_order(
        self,
        shipping_address=None,
        shipping_method="standard_delivery",
        payment_rail="bkash",
        slot_id=None,
    ):
        """Checkout ONE cart and generate its customer storefront order.

        A service method: the order is created by the server (superuser) at
        the prices the server sets, after these checks, so placing an order
        needs no order-write right and cannot set a price, a total or a state.

        (The former loop returned inside its first iteration: on a multi-cart
        recordset every cart after the first was silently left unordered.)"""
        self.ensure_one()
        rec = self
        if rec.state == "ordered":
            raise UserError("Cart %s has already been ordered" % rec.name)
        if not rec.line_ids:
            raise UserError("Cart is empty")
        # A04 audit C1 (M38-3) / A04 ERP M38-F1: the price is M11's released
        # storefront price, never the cart's or list_price. Every line is
        # re-priced here (the price can change, or be withdrawn, while the
        # cart waits), so the order is always placed at the price the server
        # sets; a line with no released price refuses the whole order. A
        # graded refurb device sells at its own resale price.
        for line in rec.line_ids:
            info = line._sf_price_info()
            vals = line._sf_price_vals(info)
            if any(line._sf_value_differs(k, v) for k, v in vals.items()):
                line.sudo().write(vals)
        # ...and may still be sold, here, at that price: the M37 item
        # lifecycle and the M11 floor are checked again at checkout, since
        # either can change while the cart waits.
        rec.line_ids._sf_check_sale()
        # The address the customer gave, else the one on their record - never
        # an invented city. Only a branch pickup needs no delivery address.
        address = (shipping_address or "").strip() or (
            rec.customer_id.contact_address or ""
        ).strip()
        if not address:
            if shipping_method != "branch_pickup":
                raise UserError("A shipping address is required for home delivery")
            address = "Branch walk-in pickup"

        # A12 audit P1-4 / D8 (M65 gateways -> M38 checkout): checkout must
        # read the payment-gateway master. A rail whose gateway is
        # configured but not yet LIVE for money (draft, suspended, or still
        # in sandbox mode) must not take an order. A rail with no gateway
        # master configured keeps today's behaviour, so tenants that have
        # not set up M65 are not locked out of their own storefront.
        # A12 finish E5/E12: the row for THIS company and country decides, an
        # archived row still counts (active_test=False), and a rail known only
        # elsewhere is not configured here.
        if payment_rail and payment_rail != "cod":
            country = rec.company_id.sudo().country_id.code or "BD"
            rails = (
                self.env["fix.payment.gateway"]
                .sudo()
                .with_context(active_test=False)
                .search([("provider", "=ilike", payment_rail)])
            )
            gateway = rails.filtered(
                lambda r: r.company_id == rec.company_id
                and (r.country_code or "").upper() == country.upper()
            )
            # A04 ERP audit M38-F13 / X7: a rail with no gateway master took
            # orders nobody could ever pay. Every prepaid rail now needs its
            # live M65 gateway in this company.
            if not gateway:
                raise UserError(
                    "The %s payment gateway is not configured for %s in this company: the "
                    "storefront takes no %s order until it is set up and live in M65."
                    % (payment_rail, country, payment_rail)
                )
            gateway.assert_live_for_checkout("storefront checkout", country_code=country)
            # a customer's own checkout is paid by the signed callback: with
            # no callback secret no payment could ever be confirmed
            channel = rec["channel"] if "channel" in rec._fields else "web"
            secret = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(GATEWAY_SECRET_PARAM % payment_rail)
            )
            if channel in ("web", "app") and not secret:
                raise UserError(
                    "The %s gateway has no callback secret (%s): an online payment could never "
                    "be confirmed, so the storefront takes no %s order."
                    % (payment_rail, GATEWAY_SECRET_PARAM % payment_rail, payment_rail)
                )

        # A04 audit M38-8: the refurb device is reserved for this order now,
        # and the delivery slot is booked, both within their limits.
        stock = rec.line_ids.mapped("graded_stock_id").sudo()
        for item in stock:
            if item.state != "in_stock":
                raise UserError(
                    "Refurbished item %s is %s and can no longer be sold." % (item.name, item.state)
                )
        slot = self.env["fix.storefront.slot"].sudo().browse(int(slot_id)) if slot_id else None
        if slot is not None:
            slot._sf_assert_bookable()

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
            "slot_id": slot.id if slot else False,
            "placed_by_id": self.env.uid,
            # M38-F7: a prepaid order is paid within the timeout or cancelled
            "payment_expires_at": False
            if payment_rail == "cod"
            else fields.Datetime.now() + timedelta(minutes=self._sf_payment_timeout()),
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
                        "graded_stock_id": line.graded_stock_id.id or False,
                        "quantity": line.quantity,
                        "currency_id": rec.currency_id.id,
                        "unit_price": line.unit_price,
                        "subtotal": line.subtotal,
                        # M38-F1: the price lock - what M11 priced it at
                        "unit_price_excl": line.unit_price_excl,
                        "price_card_id": line.price_card_id.id or False,
                        "price_source": line.price_source or False,
                    },
                )
                for line in rec.line_ids
            ],
        }
        order = self.env["fix.storefront.order"].sudo().create(order_vals)
        for item in stock:
            item.action_reserve()
        rec._guarded().write({"order_id": order.id, "state": "ordered"})
        order = order.with_env(self.env)

        publish(
            self.env,
            "storefront.order_placed",
            "fix.storefront.order",
            order.id,
            {
                "order_id": order.id,
                "order_name": order.name,
                "customer": rec.customer_id.name,
                "total": float(order.sudo().total_amount),
                "rail": payment_rail,
            },
        )
        return order

    @api.model
    def _sf_payment_timeout(self) -> int:
        raw = self.env["ir.config_parameter"].sudo().get_param(PAYMENT_TIMEOUT_PARAM)
        try:
            minutes = int(raw) if raw else PAYMENT_TIMEOUT_DEFAULT
        except ValueError:
            minutes = PAYMENT_TIMEOUT_DEFAULT
        return max(minutes, 1)

    @api.model
    def cron_publish_abandoned_carts(self):
        """A04 audit M38-16 / C10: an open cart left untouched for the
        abandonment period is handed to the M35 recovery journeys once
        (storefront.cart_abandoned has a consumer and had no producer).
        Idempotent: a cart is published once (abandon_notified_at)."""
        raw = self.env["ir.config_parameter"].sudo().get_param(CART_ABANDON_HOURS_PARAM)
        try:
            hours = int(raw) if raw else CART_ABANDON_HOURS_DEFAULT
        except ValueError:
            hours = CART_ABANDON_HOURS_DEFAULT
        cutoff = fields.Datetime.now() - timedelta(hours=hours)
        carts = self.sudo().search(
            [
                ("state", "in", ("open", "checkout")),
                ("write_date", "<", cutoff),
                ("abandon_notified_at", "=", False),
                ("line_ids", "!=", False),
            ]
        )
        for cart in carts:
            publish(
                cart.env,
                "storefront.cart_abandoned",
                "fix.storefront.cart",
                cart.id,
                {
                    "cart_id": cart.id,
                    "cart_name": cart.name,
                    "customer_id": cart.customer_id.id,
                    "total": float(cart.total or 0.0),
                    "items": len(cart.line_ids),
                },
            )
        carts._guarded().write({"abandon_notified_at": fields.Datetime.now()})
        return len(carts)


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
    graded_stock_id = fields.Many2one(
        "fix.graded.stock",
        string="Refurbished Item",
        help="A graded refurb device (M15) sold as this line; it sells at its own "
        "resale price, one unit, and is reserved when the order is placed.",
    )
    quantity = fields.Float(default=1, required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    unit_price = fields.Monetary(
        string="Unit Price (incl. VAT)",
        currency_field="currency_id",
        required=True,
        help="What the customer pays per unit, VAT included: the M11 released storefront "
        "price (VAT-exclusive) plus the M51 VAT on it.",
    )
    # A04 ERP audit M38-F1: the price lock - the M11 price this line carries
    unit_price_excl = fields.Monetary(
        string="M11 Price (excl. VAT)", currency_field="currency_id", readonly=True
    )
    price_card_id = fields.Many2one(
        "fix.rate.card", string="M11 Rate Card", readonly=True, ondelete="restrict"
    )
    price_source = fields.Char(string="Price Source", readonly=True)
    subtotal = fields.Monetary(
        compute="_compute_subtotal", string="Subtotal", currency_field="currency_id", store=True
    )

    # ------------------------------------------------------------ M11 price
    @api.model
    def _sf_m11_price(self, product, partner=None, company=None, qty=1.0):
        """A04 ERP audit M38-F1: the storefront price of one unit of the
        product template `product`, from M11 (fix.rate.card.price_for on the
        'storefront' channel) - never product.template.list_price.

        Returns {excl, incl, card_id, source}. Raises UserError when M11 has
        no released price for it or the price is not positive: the storefront
        sells nothing it cannot price (fail closed)."""
        product = product.sudo()
        company = company or self.env.company
        variant = product.product_variant_id
        if "fix.rate.card" not in self.env or not variant:
            raise UserError(
                "%s has no released M11 storefront price (M11 is not installed): it is not "
                "sold online." % product.display_name
            )
        res = (
            self.env["fix.rate.card"]
            .sudo()
            .price_for(
                variant, partner=partner, channel="storefront", qty=qty or 1.0, company=company
            )
        )
        excl = res.get("price")
        if excl is None or excl <= 0.005:
            raise UserError(
                "%s cannot be sold online: %s"
                % (
                    product.display_name,
                    res.get("reason") or "its released M11 storefront price is not positive",
                )
            )
        incl = self._sf_vat_inclusive(excl, variant, company, res.get("vat_rate"))
        if incl <= 0.005:
            raise UserError("%s has no positive storefront price." % product.display_name)
        return {
            "excl": excl,
            "incl": incl,
            "card_id": res.get("card_id") or False,
            "source": res.get("source") or "m11",
        }

    @api.model
    def _sf_vat_inclusive(self, excl, variant, company, vat_rate=None):
        """The VAT-inclusive unit price the customer pays for an M11
        VAT-exclusive price. Here: the standard rate M11 reports (M51 Tax
        Rate Master); cd_storefront_finance replaces it with the M51
        determination the invoice line itself makes, so the invoice
        reproduces the price exactly. No rate known: refused."""
        if vat_rate is None:
            raise UserError(
                "No VAT rate is known for %s (M51 Tax Rate Master): the storefront cannot "
                "state a VAT-inclusive price." % variant.display_name
            )
        currency = self.env.ref("base.BDT")
        return currency.round(excl * (1.0 + float(vat_rate) / 100.0))

    def _sf_price_info(self) -> dict:
        """The price the server sets for this line: the refurb item's resale
        price (A05), else M11's released storefront price."""
        self.ensure_one()
        if self.graded_stock_id:
            return {
                "excl": 0.0,
                "incl": self.graded_stock_id.sudo().resale_price,
                "card_id": False,
                "source": "graded_stock",
            }
        return self._sf_m11_price(
            self.product_id,
            partner=self.cart_id.customer_id,
            company=self.cart_id.company_id or self.company_id,
            qty=self.quantity,
        )

    @api.model
    def _sf_price_vals(self, info) -> dict:
        return {
            "unit_price": info["incl"],
            "unit_price_excl": info["excl"],
            "price_card_id": info["card_id"] or False,
            "price_source": info["source"],
        }

    def _sf_server_price(self) -> float:
        """The VAT-inclusive unit price the server sets (see _sf_price_info)."""
        self.ensure_one()
        return self._sf_price_info()["incl"]

    @api.model_create_multi
    def create(self, vals_list):
        # A04 audit C1 (M38-3) / A04 ERP M38-F1: a cart line's price is set
        # by the server, for everyone (the API too): M11's released
        # storefront price, or the refurb item's resale price. A price passed
        # in is ignored.
        Product = self.env["product.template"].sudo()
        Cart = self.env["fix.storefront.cart"].sudo()
        stock = self.env["fix.graded.stock"].sudo()
        for vals in vals_list:
            if vals.get("graded_stock_id"):
                vals["unit_price"] = stock.browse(vals["graded_stock_id"]).resale_price
                vals.update({"unit_price_excl": 0.0, "price_source": "graded_stock"})
                vals.pop("price_card_id", None)
            elif vals.get("product_id"):
                cart = Cart.browse(vals.get("cart_id") or [])
                info = self._sf_m11_price(
                    Product.browse(vals["product_id"]),
                    partner=cart.customer_id if cart else None,
                    company=cart.company_id if cart else None,
                    qty=float(vals.get("quantity") or 1.0),
                )
                vals.update(self._sf_price_vals(info))
        lines = super().create(vals_list)
        lines._sf_check_sale()
        return lines

    def _sf_check_sale(self):
        """A04 audit (2026-11-04), with M37/M11: the one sale check every
        selling document runs (product.product._fix_check_sale): the
        catalogue item's lifecycle (draft, restricted, brand authorisation)
        and the M11 gate on the storefront channel - a released price, and
        the VAT-exclusive price at or above the floor (or an override
        approved for this line). Raises UserError when the line may not be
        sold."""
        for line in self:
            variant = line.product_id.sudo().product_variant_id
            if not variant or not hasattr(variant, "_fix_check_sale"):
                continue
            if line.graded_stock_id:
                variant._fix_check_sale(unit_price=line.unit_price, channel="storefront")
                continue
            variant._fix_check_sale(
                unit_price=line.unit_price_excl,
                channel="storefront",
                line=line,
                partner=line.cart_id.customer_id,
            )

    def write(self, vals):
        locked = {"unit_price", "graded_stock_id", "unit_price_excl", "price_card_id"}
        if not self.env.su and locked & set(vals):
            raise UserError("A cart line's price comes from M11 and cannot be set by hand.")
        return super().write(vals)

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.unit_price

    @api.constrains("quantity", "graded_stock_id")
    def _check_qty(self):
        for rec in self:
            if rec.quantity <= 0:
                raise UserError("Quantity must be positive")
            if not _whole_units(rec.quantity):
                raise ValidationError(
                    "The storefront sells whole units: %s is not a whole quantity "
                    "(A04 ERP M38-F4)." % rec.quantity
                )
            if rec.graded_stock_id and rec.quantity != 1:
                raise ValidationError("A refurbished item is one device: its quantity is 1.")


class FixStorefrontOrder(models.Model):
    """M38: Placed Storefront Order with Payment Rail and Fulfillment Tracking."""

    _name = "fix.storefront.order"
    _description = "Storefront Customer Order"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    slot_id = fields.Many2one(
        "fix.storefront.slot", string="Delivery Slot", index=True, ondelete="restrict"
    )
    payment_rail = fields.Selection(
        [
            ("bkash", "bKash Direct Pay"),
            ("nagad", "Nagad Direct Pay"),
            # quote-to-cash (13 Nov 2026): the other two MFS wallets on the M20
            # payment-method list, on the same signed-callback contract
            ("rocket", "Rocket (DBBL) Merchant Pay"),
            ("upay", "Upay Merchant Pay"),
            ("sslcommerz", "SSLCOMMERZ Card / Gateway"),
            ("cod", "Cash on Delivery"),
        ],
        default="bkash",
        required=True,
    )
    # The books state of the order. Declared here so every screen that lists
    # orders can show it; cd_storefront_finance (the M20 bridge) owns its
    # value and the posting itself. Without the bridge it stays "none".
    posting_state = fields.Selection(
        [("none", "Nothing to Post"), ("pending", "Pending Posting"), ("posted", "Posted")],
        string="Books",
        default="none",
        required=True,
        readonly=True,
        copy=False,
        index=True,
    )
    payment_expires_at = fields.Datetime(
        string="Pay By",
        readonly=True,
        copy=False,
        help="A prepaid order not paid by then is cancelled by the payment-timeout job "
        "(AUT-ECM-08) and what it reserved is released.",
    )
    payment_ref = fields.Char(string="Payment Rail Reference / TrxID", copy=False)
    payment_date = fields.Datetime(string="Payment Date", copy=False)
    payment_source = fields.Selection(
        [("gateway", "Gateway Callback"), ("m20_receipt", "M20 Receipt")],
        string="Payment Confirmed By",
        readonly=True,
        copy=False,
    )
    payment_receipt_id = fields.Many2one(
        "fix.ar.receipt", string="M20 Receipt", readonly=True, copy=False, ondelete="restrict"
    )
    payment_confirmed_by_id = fields.Many2one(
        "res.users", string="Payment Recorded By", readonly=True, copy=False
    )
    placed_by_id = fields.Many2one("res.users", string="Placed By", readonly=True, copy=False)
    dispatched_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    delivered_at = fields.Datetime(string="Delivered At", readonly=True, copy=False)
    delivered_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    cancelled_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    refund_due = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="Set when a paid order is cancelled: the refund instruction sent to finance.",
    )
    returns_closed = fields.Boolean(
        string="Return Window Closed",
        readonly=True,
        copy=False,
        help="Set by the daily job once the return window has elapsed.",
    )
    return_deadline = fields.Date(
        string="Returnable Until",
        compute="_compute_return_deadline",
        search="_search_return_deadline",
    )
    amount_paid = fields.Monetary(
        currency_field="currency_id", compute="_compute_amount_paid", string="Amount Paid"
    )
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
    # Logistics SLA & Delivery Deadline Tracking (FLAW-38.1)
    delivery_due_date = fields.Datetime(
        string="Delivery SLA Deadline",
        compute="_compute_delivery_due",
        store=True,
        help="Statutory delivery due date under Bangladesh e-Commerce guidelines",
    )
    # A04 audit M38-14: "has the deadline passed" depends on the clock, so it
    # is computed when read (with a search), never stored and frozen.
    delivery_sla_status = fields.Selection(
        [("on_time", "Within SLA"), ("breached", "SLA Breached")],
        string="Delivery SLA Status",
        compute="_compute_delivery_sla",
        search="_search_delivery_sla",
    )
    line_ids = fields.One2many("fix.storefront.order.line", "order_id", string="Order Items")

    # One gateway transaction pays one order (BRU-ECM-05); one M20 receipt
    # backs one order.
    _payment_ref_unique = models.UniqueIndex(
        "(payment_rail, payment_ref) WHERE payment_ref IS NOT NULL",
        "This gateway transaction reference already paid another storefront order.",
    )
    _payment_receipt_unique = models.UniqueIndex(
        "(payment_receipt_id) WHERE payment_receipt_id IS NOT NULL",
        "This M20 receipt already paid another storefront order.",
    )

    # ------------------------------------------------------------ guard
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | ORDER_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields() | {"order_date"}
        rec = self[:1]
        if rec and rec.state not in ("draft", "pending_payment"):
            locked |= {"shipping_method"}
        if rec and rec.state in ("dispatched", "delivered", "cancelled"):
            locked |= {"shipping_address", "operating_unit_id"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                locked = rec._fix_form_locked_fields() - rec._fix_guarded_fields()
                changed = [
                    n
                    for n in locked & set(vals)
                    if n in rec._fields and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "%s cannot be changed on order %s: it is %s."
                        % (
                            ", ".join(sorted(rec._fields[n].string or n for n in changed)),
                            rec.name,
                            dict(rec._fields["state"].selection)[rec.state],
                        )
                    )
        return super().write(vals)

    # ------------------------------------------------------------ computes
    @api.depends("order_date", "shipping_method")
    def _compute_delivery_due(self):
        for rec in self:
            rec.delivery_due_date = rec._sf_due_for(rec.order_date, rec.shipping_method)

    @staticmethod
    def _sf_sla_hours(shipping_method):
        return {"express_courier": 24, "branch_pickup": 72}.get(shipping_method, 48)

    def _sf_due_for(self, order_date, shipping_method):
        if not order_date:
            return False
        return order_date + timedelta(hours=self._sf_sla_hours(shipping_method))

    @api.depends("order_date", "shipping_method", "state", "delivered_at")
    def _compute_delivery_sla(self):
        now = fields.Datetime.now()
        for rec in self:
            due = rec._sf_due_for(rec.order_date, rec.shipping_method)
            late_at = rec.delivered_at or now
            open_order = rec.state not in ("cancelled",)
            rec.delivery_sla_status = (
                "breached" if (due and open_order and late_at > due) else "on_time"
            )

    def _search_delivery_sla(self, operator, value):
        if operator not in ("=", "!=", "in", "not in"):
            raise UserError("Unsupported search on the delivery SLA status.")
        values = [value] if isinstance(value, str) or value is None else list(value)
        want_breached = "breached" in values
        if operator in ("!=", "not in"):
            want_breached = not want_breached
        now = fields.Datetime.now()
        candidates = self.sudo().search([("state", "!=", "cancelled")])
        breached = candidates.filtered(
            lambda o: o.delivery_due_date and (o.delivered_at or now) > o.delivery_due_date
        )
        return [("id", "in" if want_breached else "not in", breached.ids)]

    def _sf_window_days(self) -> int:
        return self.env["fix.storefront.return"]._sf_window_days()

    def _sf_return_deadline(self):
        """The last day a return is accepted: the window counted from delivery,
        else from payment, else from placement (Dhaka date)."""
        self.ensure_one()
        start = self.delivered_at or self.payment_date or self.order_date
        if not start:
            return False
        local = fields.Datetime.context_timestamp(self, start).date()
        return local + timedelta(days=self._sf_window_days())

    def _compute_return_deadline(self):
        for rec in self:
            rec.return_deadline = rec._sf_return_deadline()

    def _search_return_deadline(self, operator, value):
        orders = self.sudo().search([])
        target = fields.Date.to_date(value) if value else False
        ops = {
            "<": lambda d: d and target and d < target,
            "<=": lambda d: d and target and d <= target,
            ">": lambda d: d and target and d > target,
            ">=": lambda d: d and target and d >= target,
            "=": lambda d: d == target,
            "!=": lambda d: d != target,
        }
        if operator not in ops:
            raise UserError("Unsupported search on the return deadline.")
        hit = orders.filtered(lambda o: ops[operator](o._sf_return_deadline()))
        return [("id", "in", hit.ids)]

    def _sf_amount_paid(self) -> float:
        """What the customer has paid on this order: the total once payment is
        confirmed, or once a cash-on-delivery order is delivered (the cash was
        collected at the door against the POD); nothing before."""
        self.ensure_one()
        if self.state not in PAID_STATES:
            return 0.0
        if self.payment_rail == "cod" and not self.payment_date and self.state != "delivered":
            return 0.0
        return self.total_amount or 0.0

    @api.depends("state", "total_amount", "payment_rail", "payment_date")
    def _compute_amount_paid(self):
        for rec in self:
            rec.amount_paid = rec._sf_amount_paid()

    @api.constrains("total_amount", "line_ids")
    def _check_total_is_the_lines(self):
        """A04 audit M38-12: the total is the sum of the lines (an order was
        paid at BDT 1 while its lines summed to 2,500)."""
        for rec in self:
            if not rec.line_ids:
                continue
            lines = sum(rec.line_ids.mapped("subtotal"))
            if rec.currency_id.compare_amounts(lines, rec.total_amount or 0.0) != 0:
                raise ValidationError(
                    "Order %s: the total (%.2f) must equal the sum of its lines (%.2f)."
                    % (rec.name, rec.total_amount or 0.0, lines)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.storefront.order")
                    or f"SO/{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        return super().create(vals_list)

    # ------------------------------------------------------------ payment
    def _sf_find_m20_receipt(self, reference):
        """A confirmed M20 receipt of this customer, numbered or referenced
        `reference`, covering the order total and backing no other order."""
        self.ensure_one()
        partner = self.customer_id.commercial_partner_id
        receipts = (
            self.env["fix.ar.receipt"]
            .sudo()
            .search(
                [
                    ("state", "=", "confirmed"),
                    "|",
                    ("name", "=", reference),
                    ("reference", "=", reference),
                ]
            )
            .filtered(
                lambda r: r.customer_id.commercial_partner_id == partner
                and (r.amount or 0.0) + 0.005 >= (self.total_amount or 0.0)
            )
        )
        for receipt in receipts:
            used = self.sudo().search_count(
                [("id", "!=", self.id), ("payment_receipt_id", "=", receipt.id)]
            )
            if not used:
                return receipt
        return self.env["fix.ar.receipt"]

    def _sf_assert_reference_unused(self, rail, reference):
        self.ensure_one()
        other = self.sudo().search(
            [("id", "!=", self.id), ("payment_rail", "=", rail), ("payment_ref", "=", reference)],
            limit=1,
        )
        if other:
            raise UserError(
                "Transaction %s already paid order %s: one gateway transaction pays one "
                "order (BRU-ECM-05)." % (reference, other.name)
            )

    def action_confirm_payment(self, payment_ref=None, rail=None):
        """Mark the order paid on proof of payment - never on a typed string.

        * The gateway callback (bKash/Nagad/SSLCOMMERZ IPN, signature verified
          in controllers/storefront_api.py) confirms as the superuser through
          _sf_gateway_confirm.
        * A Storefront Payment Officer confirms against a CONFIRMED M20 receipt
          (fix.ar.receipt) of this customer whose number or reference is
          `payment_ref` and which covers the total.
        One reference and one receipt pay one order (A04 audit M38-2)."""
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
            new_rail = rail or rec.payment_rail
            vals = {
                "payment_ref": reference,
                "payment_rail": new_rail,
                "payment_date": fields.Datetime.now(),
                "payment_confirmed_by_id": self.env.uid,
                "state": "paid",
            }
            if self.env.su:
                vals["payment_source"] = "gateway"
            else:
                _require(self.env, [GROUP_PAYMENT], "Confirming a storefront payment")
                if not rec.line_ids:
                    raise UserError("Order %s has no lines: there is nothing to pay." % rec.name)
                receipt = rec._sf_find_m20_receipt(reference)
                if not receipt:
                    raise UserError(
                        "No confirmed M20 receipt '%s' of at least BDT %.2f exists for %s "
                        "that pays no other order. A storefront payment is confirmed by "
                        "the gateway callback or by its M20 receipt, never by a typed "
                        "TrxID." % (reference, rec.total_amount, rec.customer_id.display_name)
                    )
                vals.update({"payment_source": "m20_receipt", "payment_receipt_id": receipt.id})
            rec._sf_assert_reference_unused(new_rail, reference)
            rec._guarded().write(vals)
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
        return True

    @api.model
    def _sf_gateway_confirm(self, rail, order_name, trx_id, amount):
        """The gateway callback's service: called by the controller only after
        the callback's signature has been verified. Confirms the named order
        when the rail is the order's and the amount captured is its total."""
        order = self.sudo().search([("name", "=", order_name)], limit=1)
        if not order:
            raise UserError("Unknown storefront order %s." % order_name)
        if rail != order.payment_rail:
            raise UserError(
                "Order %s is payable by %s, not by %s." % (order.name, order.payment_rail, rail)
            )
        try:
            captured = float(amount)
        except (TypeError, ValueError):
            raise UserError("The gateway amount is not a number.") from None
        if order.currency_id.compare_amounts(captured, order.total_amount) != 0:
            raise UserError(
                "Gateway captured BDT %.2f on order %s, whose total is BDT %.2f."
                % (captured, order.name, order.total_amount)
            )
        if order.payment_date:
            if order.payment_ref == trx_id:
                return order  # the gateway re-sent the same notice
            raise UserError(
                "Order %s is already paid by %s; transaction %s is a second capture to "
                "refund." % (order.name, order.payment_ref, trx_id)
            )
        order.action_confirm_payment(payment_ref=trx_id, rail=rail)
        return order

    # ------------------------------------------------------------ fulfilment
    def _sf_find_consignment(self, ref):
        Consignment = self.env["fix.consignment"].sudo()
        if isinstance(ref, models.BaseModel):
            return ref.sudo().exists()
        try:
            return Consignment.browse(int(ref)).exists()
        except (TypeError, ValueError):
            pass
        text = (str(ref or "")).strip()
        return Consignment.search([("name", "=", text)], limit=1) if text else Consignment

    def action_dispatch(self, carrier_consignment_id=None):
        """Dispatch only a PAID order (a cash-on-delivery order may leave
        unpaid: payment is collected at the door), on its M03 consignment.
        A branch pickup needs no consignment."""
        _require(self.env, [GROUP_OPERATOR], "Dispatching a storefront order")
        for rec in self:
            cod_unpaid = rec.payment_rail == "cod" and rec.state == "pending_payment"
            if rec.state != "paid" and not cod_unpaid:
                raise UserError("Order must be paid before dispatch")
            vals = {"state": "dispatched", "dispatched_by_id": self.env.uid}
            if rec.shipping_method != "branch_pickup":
                consignment = (
                    rec._sf_find_consignment(carrier_consignment_id)
                    if carrier_consignment_id
                    else rec.carrier_consignment_id.sudo()
                )
                if not consignment:
                    raise UserError(
                        "Order %s needs its M03 delivery consignment to be dispatched "
                        "(A04 audit M38-11)." % rec.name
                    )
                # A02 ERP audit M03-F4: a leg on its way back ("returning") carries nothing
                if consignment.state in ("lost", "returned", "returning"):
                    raise UserError(
                        "Consignment %s is %s; it cannot carry order %s."
                        % (consignment.name, consignment.state, rec.name)
                    )
                vals["carrier_consignment_id"] = consignment.id
            rec._guarded().write(vals)
            publish(
                self.env,
                "storefront.order_dispatched",
                "fix.storefront.order",
                rec.id,
                {"order_id": rec.id, "order_name": rec.name},
            )
        return True

    def action_deliver(self):
        """Delivered only on proof of delivery: the order's M03 consignment is
        delivered (its POD verified by the recipient's code or the receiving
        hub). A branch pickup is handed over at the counter by an operator.
        A refurb device on the order is sold now (graded_stock.sold)."""
        _require(self.env, [GROUP_OPERATOR], "Delivering a storefront order")
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Only a dispatched order can be delivered")
            if rec.shipping_method != "branch_pickup":
                consignment = rec.carrier_consignment_id.sudo()
                if not consignment or consignment.state != "delivered":
                    raise UserError(
                        "Order %s is delivered when its consignment is: %s has no verified "
                        "proof of delivery yet (A04 audit M38-11)."
                        % (rec.name, consignment.name if consignment else "no consignment")
                    )
            rec._guarded().write(
                {
                    "state": "delivered",
                    "delivered_at": fields.Datetime.now(),
                    "delivered_by_id": self.env.uid,
                }
            )
            for item in rec.sudo().line_ids.mapped("graded_stock_id"):
                if item.state in ("in_stock", "reserved"):
                    item.action_sell()
        return True

    def action_cancel(self, reason=None):
        """Cancel before dispatch only; a shipped order goes through a return.
        A04 audit M38-15: cancelling a PAID order sends finance the refund
        instruction (storefront.order_cancelled with the refund due), and the
        reserved refurb stock and the slot are released."""
        _require(self.env, [GROUP_OPERATOR], "Cancelling a storefront order")
        for rec in self:
            if rec.state not in ("draft", "pending_payment", "paid"):
                raise UserError(
                    "Order %s is '%s': it can no longer be cancelled (use a return)"
                    % (rec.name, rec.state)
                )
            refund_due = rec.total_amount if rec.state == "paid" else 0.0
            rec._guarded().write(
                {"state": "cancelled", "refund_due": refund_due, "cancelled_by_id": self.env.uid}
            )
            for item in rec.sudo().line_ids.mapped("graded_stock_id"):
                if item.state == "reserved":
                    item.action_release()
            publish(
                self.env,
                "storefront.order_cancelled",
                "fix.storefront.order",
                rec.id,
                {
                    "order_id": rec.id,
                    "order_name": rec.name,
                    "customer_id": rec.customer_id.id,
                    "refund_due": float(refund_due),
                    "currency": rec.currency_id.name,
                    "rail": rec.payment_rail,
                    "payment_ref": rec.payment_ref or "",
                    "receipt_id": rec.payment_receipt_id.id or None,
                    "reason": (str(reason).strip() if reason else "") or "",
                },
            )
        return True

    @api.model
    def cron_expire_unpaid_orders(self, limit=500):
        """A04 ERP audit M38-F7 (AUT-ECM-08): a prepaid order the gateway
        never confirmed is cancelled once its pay-by time has passed, which
        releases its reserved stock and slot. Idempotent: only orders still
        pending payment are touched; cash on delivery never expires."""
        due = self.sudo().search(
            [
                ("state", "=", "pending_payment"),
                ("payment_rail", "!=", "cod"),
                ("payment_expires_at", "!=", False),
                ("payment_expires_at", "<", fields.Datetime.now()),
            ],
            limit=limit,
        )
        for order in due:
            try:
                with self.env.cr.savepoint():
                    order.action_cancel(
                        reason="Payment not received before %s (timeout)."
                        % order.payment_expires_at
                    )
            except UserError as exc:
                logger.warning("storefront order %s did not expire: %s", order.name, exc)
        return len(due)

    @api.model
    def cron_close_return_windows(self):
        """A04 audit C10: a delivered order whose return window has elapsed is
        closed for returns. Idempotent (only orders still open are touched)."""
        today = fields.Date.context_today(self)
        orders = self.sudo().search([("state", "=", "delivered"), ("returns_closed", "=", False)])
        due = orders.filtered(lambda o: (o._sf_return_deadline() or today) < today)
        if due:
            due._guarded().write({"returns_closed": True})
        return len(due)


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
    graded_stock_id = fields.Many2one(
        "fix.graded.stock", string="Refurbished Item", readonly=True, index=True
    )
    quantity = fields.Float(string="Quantity", default=1, required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    unit_price = fields.Monetary(
        string="Unit Price (incl. VAT)", currency_field="currency_id", required=True
    )
    subtotal = fields.Monetary(string="Subtotal", currency_field="currency_id", required=True)
    # A04 ERP audit M38-F1: the M11 price lock carried from the cart
    unit_price_excl = fields.Monetary(
        string="M11 Price (excl. VAT)", currency_field="currency_id", readonly=True
    )
    price_card_id = fields.Many2one(
        "fix.rate.card", string="M11 Rate Card", readonly=True, ondelete="restrict"
    )
    price_source = fields.Char(string="Price Source", readonly=True)

    @api.constrains("quantity", "unit_price")
    def _check_whole_priced(self):
        """M38-F1/F4: a placed line is a whole number of units at a positive
        price."""
        for rec in self:
            if not _whole_units(rec.quantity):
                raise ValidationError(
                    "The storefront sells whole units: %s is not a whole quantity." % rec.quantity
                )
            if (rec.unit_price or 0.0) <= 0.005:
                raise ValidationError(
                    "%s has no positive price: nothing is sold for free online."
                    % rec.product_id.display_name
                )

    def write(self, vals):
        # A04 audit M38-12: a placed order's lines are what the customer
        # bought at the price the server set; nobody edits them afterwards.
        if not self.env.su:
            raise UserError("A placed order's lines cannot be changed.")
        return super().write(vals)


class FixStorefrontReturn(models.Model):
    _name = "fix.storefront.return"
    _description = "Storefront Return & Reverse Logistics"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.storefront.refund.mixin"]
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

    _credit_note_unique = models.UniqueIndex(
        "(credit_note_id) WHERE credit_note_id IS NOT NULL",
        "This credit note already pays another storefront return.",
    )

    def _sf_change_of_mind(self) -> bool:
        return self.reason == "changed_mind"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.storefront.return")
                    or f"RMA/{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        return super().create(vals_list)
