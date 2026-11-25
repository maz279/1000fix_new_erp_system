# fix_storefront_checkout - M38 checkout pricing, idempotent placement,
# customer self-cancel and per-line returns (A04 ERP audit, round 2,
# 21 Nov 2026).
#
#   M38-F14  The delivery fee and a checkout voucher are priced on the server
#            at placement, from M11: the fee is the released storefront price
#            (fix.rate.card.price_for) of the fee product the shipping method
#            names (cd_storefront.delivery_fee_code.<method>); the voucher is
#            an M11 promotion flagged as a checkout voucher, applied through
#            the M11 promotion engine (usable_on / covers / discount_on, never
#            below the floor) and consumed by the order it priced. Both are
#            order lines, so the total stays the sum of the lines.
#   M38-F20  An idempotency key on placement: a replay returns the order the
#            first call placed. A customer may cancel their own order before
#            dispatch; it runs the round-1 cancel / refund path.
#   M38-F8   A return names the order lines, quantities and amounts it takes
#            back; it can never take back more than was sold. Restock and
#            credit follow the lines (cd_storefront_finance).
from odoo import api, fields, models
from odoo.addons.cd_rate_card.models.pricing_money import money
from odoo.addons.cd_rate_card.models.pricing_roles import ROLE_OFFICER, require_role
from odoo.exceptions import UserError, ValidationError

from .fix_storefront import _whole_units

# The fee product (its default_code) a shipping method charges, priced by M11
# on the storefront channel. Unset (or "none"): the method charges no fee.
# The codes and their M11 prices are THE BUSINESS'S to set (OWNER).
DELIVERY_FEE_PARAM = "cd_storefront.delivery_fee_code.%s"
KEY_CHARS = set("-_:.")
KEY_MAX = 80
CANCELLABLE_BY_CUSTOMER = ("pending_payment", "paid")


# =========================================================================
# M11 promotion: the checkout voucher flag
# =========================================================================
class FixPromotionStorefrontVoucher(models.Model):
    """A promotion the customer must name at checkout. M11 applies every
    other active promotion by itself (price_for); a checkout voucher is
    left out of that and is applied only to the order whose customer entered
    its code."""

    _inherit = "fix.promotion"

    storefront_voucher = fields.Boolean(
        string="Checkout Voucher",
        help="On: the promotion is a voucher the customer enters at the storefront "
        "checkout; it is never applied automatically. Fixed once the promotion leaves "
        "Draft.",
    )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= {"storefront_voucher"}
        return locked

    def write(self, vals):
        if "storefront_voucher" in vals and not self._fix_guard_open():
            require_role(self.env, (ROLE_OFFICER,), "Marking a promotion as a checkout voucher")
            moved = self.filtered(
                lambda p: bool(p.storefront_voucher) != bool(vals["storefront_voucher"])
            )
            if moved.filtered(lambda p: p.state != "draft"):
                raise UserError(
                    "%s is no longer a draft: whether it is a checkout voucher is fixed."
                    % moved[0].display_name
                )
        return super().write(vals)

    @api.model
    def best_combination(self, promotions, base_price, channel=None, product_code=None):
        # a checkout voucher is never applied automatically by price_for
        promotions = promotions.filtered(lambda p: not p.storefront_voucher)
        return super().best_combination(
            promotions, base_price, channel=channel, product_code=product_code
        )


# =========================================================================
# Cart: idempotency, fee, voucher
# =========================================================================
class FixStorefrontCartCheckout(models.Model):
    _inherit = "fix.storefront.cart"

    # ------------------------------------------------------------ M38-F20
    @api.model
    def _sf_clean_key(self, key):
        key = str(key or "").strip()
        if not key:
            return ""
        if len(key) > KEY_MAX or not all(ch.isalnum() or ch in KEY_CHARS for ch in key):
            raise UserError(
                "An idempotency key is 1 to %d letters, digits, '-', '_', ':' or '.'." % KEY_MAX
            )
        return key

    def _sf_replayed_order(self, idempotency_key):
        """Lock the cart (one placement at a time), then: the order this cart
        or its customer already placed under `idempotency_key`, or None."""
        self.ensure_one()
        key = self._sf_clean_key(idempotency_key)
        self.env.flush_all()
        self.env.cr.execute(
            "SELECT id FROM fix_storefront_cart WHERE id = %s FOR UPDATE", [self.id]
        )
        self.invalidate_recordset()
        if not key:
            return None
        cart = self.sudo()
        found = (
            self.env["fix.storefront.order"]
            .sudo()
            .search(
                [("customer_id", "=", cart.customer_id.id), ("idempotency_key", "=", key)], limit=1
            )
        )
        if not found and cart.order_id and cart.order_id.idempotency_key == key:
            found = cart.order_id
        return found.with_env(self.env) if found else None

    # ------------------------------------------------------------ M38-F14
    def _sf_delivery_fee(self, shipping_method):
        """{product, variant, excl, incl, card_id, source, code} of the fee the
        shipping method charges, priced by M11 now; None when the method
        charges none. A configured fee with no released price refuses the
        order (fail closed)."""
        self.ensure_one()
        code = (
            self.env["ir.config_parameter"].sudo().get_param(DELIVERY_FEE_PARAM % shipping_method)
            or ""
        ).strip()
        if not code or code.lower() == "none":
            return None
        variant = self.env["product.product"].sudo().search([("default_code", "=", code)], limit=1)
        if not variant:
            raise UserError(
                "The %s delivery fee names product %s (%s), which does not exist: the storefront "
                "takes no such order until the fee is configured."
                % (shipping_method, code, DELIVERY_FEE_PARAM % shipping_method)
            )
        res = (
            self.env["fix.rate.card"]
            .sudo()
            .price_for(
                variant,
                partner=self.customer_id,
                channel="storefront",
                qty=1.0,
                company=self.company_id,
            )
        )
        excl = res.get("price")
        if excl is None or excl <= 0.005:
            raise UserError(
                "The %s delivery fee (%s) has no released M11 storefront price: %s. The storefront "
                "takes no %s order until it is priced."
                % (
                    shipping_method,
                    code,
                    res.get("reason") or "its price is not positive",
                    shipping_method,
                )
            )
        incl = self.env["fix.storefront.cart.line"]._sf_vat_inclusive(
            excl, variant, self.company_id, res.get("vat_rate")
        )
        return {
            "product": variant.product_tmpl_id,
            "variant": variant,
            "excl": excl,
            "incl": incl,
            "card_id": res.get("card_id") or False,
            "source": res.get("source") or "card",
            "code": code,
        }

    def _sf_voucher_discount(self, voucher_code):
        """{promotion, code, excl, incl, shares} of the checkout voucher on this
        cart, through the M11 promotion engine. `shares` maps each covered cart
        line to the VAT-inclusive amount taken off it. Raises UserError when the
        code is not a usable checkout voucher of the company, or covers nothing."""
        self.ensure_one()
        code = (voucher_code or "").strip()
        Promo = self.env["fix.promotion"].sudo()
        promo = Promo.search(
            [("code", "=ilike", code), ("company_id", "=", self.company_id.id)], limit=1
        )
        if not promo or not promo.storefront_voucher:
            raise UserError("%s is not a storefront checkout voucher." % code)
        if not promo._usable_on("portal"):
            raise UserError(
                "Voucher %s cannot be used now: it is not active, out of its dates, not for the "
                "online channel, or its budget or usage cap is spent." % promo.code
            )
        Card = self.env["fix.rate.card"].sudo()
        rows = []
        for line in self.line_ids.sudo().filtered(
            lambda ln: not ln.graded_stock_id and (ln.unit_price_excl or 0.0) > 0.005
        ):
            variant = line.product_id.product_variant_id
            if not promo.covers(variant.default_code):
                continue
            base = line.unit_price_excl * line.quantity
            rows.append((line, base, self._sf_voucher_room(line, variant, Card)))
        if not rows:
            raise UserError("Voucher %s applies to none of the items in the cart." % promo.code)
        base_total = sum(r[1] for r in rows)
        wanted = promo.discount_on(base_total)
        currency = self.currency_id
        shares, excl_total, incl_total = {}, 0.0, 0.0
        for line, base, room in rows:
            share = min(money(wanted * base / base_total), money(room))
            if share <= 0.005:
                continue
            incl = currency.round(share * line.unit_price / line.unit_price_excl)
            incl = min(incl, currency.round(line.subtotal - 0.01))
            shares[line.id] = incl
            excl_total += share
            incl_total += incl
        if incl_total <= 0.005:
            raise UserError(
                "Voucher %s gives no discount on this cart (its items are at their price floor)."
                % promo.code
            )
        return {
            "promotion": promo,
            "code": promo.code,
            "excl": money(excl_total),
            "incl": currency.round(incl_total),
            "shares": shares,
        }

    def _sf_voucher_room(self, line, variant, Card):
        """How much (VAT-exclusive) a voucher may take off line: down to
        the floor and no further, as M11 stops a promotion at it."""
        floor = Card._floor_info(variant, company=self.company_id)["floor"] or 0.0
        return max(0.0, (line.unit_price_excl - floor) * line.quantity)

    def _sf_spend_voucher(self, quote):
        """The voucher's use and budget are spent by the order it priced."""
        if quote["discount"]:
            quote["discount"]["promotion"].sudo().consume(quote["discount"]["excl"])

    def _sf_checkout_quote(self, shipping_method, voucher_code=None):
        """What the customer pays, priced by the server now: the goods (the
        cart lines at their M11 prices), the delivery fee and the voucher.
        Placement uses exactly this; a client value is never read."""
        self.ensure_one()
        currency = self.currency_id
        goods = currency.round(sum(self.line_ids.mapped("subtotal")))
        fee = self._sf_delivery_fee(shipping_method or "standard_delivery")
        disc = self._sf_voucher_discount(voucher_code) if (voucher_code or "").strip() else None
        total = currency.round(
            goods + (fee["incl"] if fee else 0.0) - (disc["incl"] if disc else 0.0)
        )
        if total <= 0.005:
            raise UserError("Cart %s would cost nothing: the order is not placed." % self.name)
        return {"goods": goods, "fee": fee, "discount": disc, "total": total}

    def _sf_extra_order_lines(self, quote):
        """The fee and discount lines of the order, as (0, 0, vals)."""
        self.ensure_one()
        base = {
            "company_id": self.company_id.id,
            "operating_unit_id": self.operating_unit_id.id or False,
            "currency_id": self.currency_id.id,
            "quantity": 1.0,
        }
        lines = []
        fee = quote["fee"]
        if fee:
            lines.append(
                (
                    0,
                    0,
                    dict(
                        base,
                        line_type="delivery",
                        product_id=fee["product"].id,
                        unit_price=fee["incl"],
                        subtotal=fee["incl"],
                        unit_price_excl=fee["excl"],
                        price_card_id=fee["card_id"] or False,
                        price_source=fee["source"],
                    ),
                )
            )
        disc = quote["discount"]
        if disc:
            lines.append(
                (
                    0,
                    0,
                    dict(
                        base,
                        line_type="discount",
                        promotion_id=disc["promotion"].id,
                        unit_price=-disc["incl"],
                        subtotal=-disc["incl"],
                        unit_price_excl=-disc["excl"],
                        price_source="promotion",
                    ),
                )
            )
        return lines


# =========================================================================
# Order: the priced checkout, the key, the customer's cancellation
# =========================================================================
class FixStorefrontOrderCheckout(models.Model):
    _inherit = "fix.storefront.order"

    goods_amount = fields.Monetary(
        string="Goods", currency_field="currency_id", readonly=True, copy=False
    )
    delivery_fee = fields.Monetary(
        string="Delivery Fee", currency_field="currency_id", readonly=True, copy=False
    )
    discount_amount = fields.Monetary(
        string="Voucher Discount", currency_field="currency_id", readonly=True, copy=False
    )
    voucher_code = fields.Char(string="Voucher", readonly=True, copy=False)
    promotion_id = fields.Many2one(
        "fix.promotion", string="Voucher Promotion (M11)", readonly=True, copy=False
    )
    idempotency_key = fields.Char(string="Idempotency Key", readonly=True, copy=False, index=True)
    cancelled_by_customer = fields.Boolean(readonly=True, copy=False)

    _idempotency_key_unique = models.UniqueIndex(
        "(customer_id, idempotency_key) WHERE idempotency_key IS NOT NULL",
        "This idempotency key already placed another order of this customer.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "goods_amount",
            "delivery_fee",
            "discount_amount",
            "voucher_code",
            "promotion_id",
            "idempotency_key",
            "cancelled_by_customer",
        }

    def _sf_customer_may_cancel(self) -> bool:
        self.ensure_one()
        return self.state in CANCELLABLE_BY_CUSTOMER and not self.sudo().dispatched_by_id

    def action_customer_cancel(self, reason=None):
        """M38-F20: the customer cancels their own order before it is
        dispatched. The storefront API calls it (as the system) for the
        order's owner or the guest session that placed it; a signed-in
        customer may call it on their own order. It runs the operator's
        cancellation, so a paid order is refunded by the round-1 path (M20
        credit note, or the M20 refund of the captured receipt)."""
        for rec in self:
            if not self.env.su:
                user = self.env.user
                mine = (
                    rec.sudo().customer_id.commercial_partner_id
                    == user.partner_id.commercial_partner_id
                )
                if user._is_internal() or not mine:
                    raise UserError("Only the customer cancels their own order here.")
            if not rec.sudo()._sf_customer_may_cancel():
                raise UserError(
                    "Order %s is %s: it can be cancelled by the customer only before it is "
                    "dispatched (use a return once it is on its way)."
                    % (rec.sudo().name, dict(rec._fields["state"].selection)[rec.sudo().state])
                )
            text = (str(reason).strip() if reason else "") or "no reason given"
            rec.sudo().action_cancel(reason="Cancelled by the customer: %s" % text[:200])
            rec.sudo()._guarded().write({"cancelled_by_customer": True})
        return True


# =========================================================================
# M38-F8: per-line returns
# =========================================================================
class FixStorefrontReturnLine(models.Model):
    _name = "fix.storefront.return.line"
    _description = "Storefront Return Line"
    _order = "return_id, id"

    return_id = fields.Many2one(
        "fix.storefront.return", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        "res.company", related="return_id.company_id", store=True, index=True, readonly=True
    )
    currency_id = fields.Many2one(related="return_id.currency_id", readonly=True)
    order_line_id = fields.Many2one(
        "fix.storefront.order.line",
        string="Order Line",
        required=True,
        ondelete="restrict",
        index=True,
    )
    product_id = fields.Many2one(
        "product.template", related="order_line_id.product_id", store=True, readonly=True
    )
    quantity = fields.Float(string="Quantity Returned", required=True, default=1.0)
    unit_refund = fields.Monetary(
        string="Paid per Unit",
        currency_field="currency_id",
        readonly=True,
        help="What the customer paid per unit of the order line (its voucher share taken "
        "off), set by the server.",
    )
    amount = fields.Monetary(
        string="Line Refund", currency_field="currency_id", compute="_compute_amount", store=True
    )
    credit_amount = fields.Monetary(
        string="Credited (M20)",
        currency_field="currency_id",
        readonly=True,
        help="This line's share of the refund the M20 credit note pays.",
    )
    restock_state = fields.Selection(
        [
            ("none", "Not Evaluated"),
            ("not_required", "Nothing to Restock"),
            ("restocked", "Restocked"),
        ],
        string="Restock",
        default="none",
        required=True,
        readonly=True,
    )

    _TERMS = frozenset({"return_id", "order_line_id", "quantity"})
    _SERVER = frozenset({"unit_refund", "credit_amount", "restock_state"})

    @api.depends("quantity", "unit_refund")
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.currency_id.round((rec.quantity or 0.0) * (rec.unit_refund or 0.0))

    @api.model
    def _unit_paid(self, order_line):
        order_line = order_line.sudo()
        if not order_line.quantity:
            return 0.0
        return money((order_line.net_subtotal or 0.0) / order_line.quantity)

    @api.model_create_multi
    def create(self, vals_list):
        Return = self.env["fix.storefront.return"].sudo()
        OrderLine = self.env["fix.storefront.order.line"].sudo()
        for vals in vals_list:
            ret = Return.browse(vals.get("return_id") or [])
            if ret and ret.state != "requested":
                raise UserError(
                    "%s is authorised: the lines it returns are fixed." % ret.display_name
                )
            for name in self._SERVER:
                vals.pop(name, None)
            vals["unit_refund"] = self._unit_paid(OrderLine.browse(vals.get("order_line_id") or []))
        return super().create(vals_list)

    def write(self, vals):
        if self._SERVER & set(vals) and not self.env.su:
            raise UserError("The refund and restock of a return line are set by the system.")
        if "unit_refund" in vals:
            raise UserError("What the customer paid for a line is read from the order.")
        if self._TERMS & set(vals):
            for rec in self:
                if rec.return_id.state != "requested":
                    raise UserError(
                        "%s is authorised: the lines it returns are fixed."
                        % rec.return_id.display_name
                    )
            if "order_line_id" in vals:
                vals = dict(vals)
                vals["unit_refund"] = self._unit_paid(
                    self.env["fix.storefront.order.line"].sudo().browse(vals["order_line_id"])
                )
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.return_id.state != "requested":
                raise UserError(
                    "%s is authorised: the lines it returns are fixed." % rec.return_id.display_name
                )
        return super().unlink()

    @api.model
    def _sf_live_returned(self, order_line, exclude=None):
        """Units of `order_line` named by live (not rejected) returns."""
        lines = (
            self.sudo()
            .search([("order_line_id", "=", order_line.id), ("return_id.state", "!=", "rejected")])
            .filtered(lambda r: not exclude or r not in exclude)
        )
        return sum(lines.mapped("quantity"))

    @api.constrains("order_line_id", "quantity", "return_id")
    def _check_line(self):
        for rec in self.sudo():
            line = rec.order_line_id
            if line.order_id != rec.return_id.order_id:
                raise ValidationError(
                    "%s returns a line of order %s, not of %s."
                    % (rec.return_id.display_name, line.order_id.name, rec.return_id.order_id.name)
                )
            if line.line_type != "product":
                raise ValidationError(
                    "Only goods are returned; the delivery fee and the voucher are not lines "
                    "of a return."
                )
            if not _whole_units(rec.quantity):
                raise ValidationError(
                    "A return takes back whole units: %s is not a whole quantity." % rec.quantity
                )
            returned = self._sf_live_returned(line)
            if returned > (line.quantity or 0.0) + 1e-9:
                raise ValidationError(
                    "%s: %s unit(s) of %s are returned in all, but order %s sold %s."
                    % (
                        rec.return_id.display_name,
                        _qty(returned),
                        line.product_id.display_name,
                        line.order_id.name,
                        _qty(line.quantity),
                    )
                )


def _qty(value):
    return ("%.4f" % (value or 0.0)).rstrip("0").rstrip(".")


class FixStorefrontReturnLines(models.Model):
    _inherit = "fix.storefront.return"

    line_ids = fields.One2many("fix.storefront.return.line", "return_id", string="Returned Lines")
    lines_amount = fields.Monetary(
        string="Lines Total", currency_field="currency_id", compute="_compute_lines_amount"
    )

    @api.depends("line_ids.amount")
    def _compute_lines_amount(self):
        for rec in self:
            rec.lines_amount = sum(rec.line_ids.mapped("amount"))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # a return that names its lines asks, by default, for what they cost
        for rec in records.filtered(lambda r: r.line_ids and not r.refund_amount):
            rec.write({"refund_amount": sum(rec.line_ids.mapped("amount"))})
        return records

    @api.constrains("line_ids", "refund_amount", "order_id", "state")
    def _check_lines_bound_the_refund(self):
        """A return that names its lines refunds at most what the customer
        paid for them; and one order is returned either line by line or as a
        whole, never both (the whole-order restock would bring the named
        lines back twice)."""
        for rec in self:
            if rec.state == "rejected":
                continue
            if rec.line_ids:
                cap = sum(rec.line_ids.mapped("amount"))
                if (rec.refund_amount or 0.0) > cap + 0.005:
                    raise ValidationError(
                        "%s: the refund of BDT %.2f exceeds the BDT %.2f the customer paid for "
                        "the lines returned." % (rec.name, rec.refund_amount or 0.0, cap)
                    )
            if not rec.order_id:
                continue
            others = self.sudo().search(
                [
                    ("order_id", "=", rec.order_id.id),
                    ("id", "!=", rec.id),
                    ("state", "!=", "rejected"),
                ]
            )
            if others and any(bool(o.line_ids) != bool(rec.line_ids) for o in others):
                raise ValidationError(
                    "Order %s is already being returned %s: name the lines returned on every "
                    "return of it, or on none."
                    % (
                        rec.order_id.name,
                        "line by line" if others.filtered("line_ids") else "as a whole",
                    )
                )

    def _sf_restock_graded_stock(self, condition):
        """A05's refurbished return path, unchanged for a whole-order return.
        A return that names its lines brings back only the refurbished devices
        on those lines, by the same rule (grade A/B to stock, scrap scrapped)."""
        self.ensure_one()
        if not self.line_ids:
            return super()._sf_restock_graded_stock(condition)
        stock = self.line_ids.sudo().mapped("order_line_id.graded_stock_id")
        for item in stock.filtered(lambda s: s.state in ("reserved", "sold")):
            item.write({"state": "scrapped" if condition == "scrap" else "in_stock"})
