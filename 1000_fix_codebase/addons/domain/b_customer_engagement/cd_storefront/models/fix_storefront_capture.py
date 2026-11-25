# fix_storefront_capture — M38 capture audit (19 Nov 2026).
#
# The M38 workspace had ten sub-module pages and four of them could capture
# nothing (Storefront & Browse, Cart, Checkout & Payments, Online Orders,
# Recovery & Analytics), two offered another module's record (Merchandising
# and Stock Exposure offered "+ New Graded Stock Item", a unit M14/M15 grade
# and value), and B2B Commerce listed storefront RETURNS. The spec's own
# entities (§10.1) behind those pages had no model at all. This file adds
# them, each with the rule the spec puts on it:
#
#   page 1  fix.storefront.content       banners / landing / policy pages,
#                                        bilingual before publication (FR-ECM-002, §3.1 #20)
#   page 2  fix.storefront.collection    collections, featured sets, cross- and
#                                        up-sell (FR-ECM-008/009)
#   page 3  assisted cart                a staff-captured cart (R08/R34 assisted
#                                        ordering), its checkout data and the
#                                        item-terms acceptance (FR-ECM-015/026,
#                                        BRU-ECM-07)
#   page 4  fix.storefront.cod.rule      COD governance: value limit, history,
#                                        open COD orders (FR-ECM-025, BRU-ECM-08)
#   page 5  fix.storefront.order.change  address / slot / delivery-mode change
#                                        inside the policy window (FR-ECM-044)
#   page 6  fix.stock.exposure.policy    what may be sold online, from where,
#                                        with what buffer (FR-ECM-014, BRU-ECM-04)
#   page 7  fix.storefront.return.policy return window and restocking fee per
#                                        category (entity fix.return.policy)
#   page 8  fix.storefront.corporate.account + the corporate order (PO
#                                        reference, the client's own approval:
#                                        FR-ECM-052..054, BRU-ECM-14)
#   page 9  fix.storefront.recovery.attempt the recovery contact on an
#                                        abandoned cart (FR-ECM-029)
#   page 10 fix.storefront.service.booking a repair booked as a purchasable
#                                        slot, confirmed into the M01 service
#                                        order (FR-ECM-031..033, BRU-ECM-11)
#
# Policy records (COD, exposure, return, corporate account) take effect only
# once a Storefront Manager who did not write them approves them. Where no
# approved policy exists the storefront behaves as before: switching a
# control on is a business act, recorded on the record that does it.
import math

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_storefront_refund import (
    GROUP_OPERATOR,
    RESTOCKING_FEE_PARAM,
    RESTOCKING_FEE_PCT_DEFAULT,
)

GROUP_MANAGER = "cd_storefront.group_fix_storefront_manager"
GROUP_ASSISTED = "cd_storefront.group_fix_storefront_assisted_sales"
GROUP_MERCHANDISER = "cd_storefront.group_fix_storefront_merchandiser"

# BRU-ECM-04 strict mode: when "1", a product no approved exposure policy
# covers is not sold online at all. Off by default: no fix_real product has a
# policy yet, and turning the storefront off is the Inventory Manager's call.
EXPOSURE_STRICT_PARAM = "cd_storefront.exposure_policy_required"

SHIPPING_METHODS = [
    ("standard_delivery", "Standard Home Delivery (48h)"),
    ("express_courier", "Express Courier (24h)"),
    ("branch_pickup", "Branch Walk-in Pickup"),
]
PAYMENT_RAILS = [
    ("bkash", "bKash Direct Pay"),
    ("nagad", "Nagad Direct Pay"),
    ("rocket", "Rocket (DBBL) Merchant Pay"),
    ("upay", "Upay Merchant Pay"),
    ("sslcommerz", "SSLCOMMERZ Card / Gateway"),
    ("cod", "Cash on Delivery"),
]
AUDIENCES = [("all", "All customers"), ("retail", "Retail customers"), ("corporate", "Corporate")]


def _has(env, *xmlids):
    return env.su or any(env.user.has_group(x) for x in xmlids)


def _require(env, xmlids, what):
    if _has(env, *xmlids):
        return
    names = " or ".join(env.ref(x).name for x in xmlids)
    raise UserError("%s needs the %s role." % (what, names))


class FixStorefrontCaptureMixin(models.AbstractModel):
    """The shared shape of the M38 capture records: guarded workflow stamps,
    fields frozen once the record leaves its editable states, and the
    'decided by someone who did not write it' rule."""

    _name = "fix.storefront.capture.mixin"
    _description = "Storefront Capture Controls"
    _inherit = ["fix.guarded.mixin"]

    # states in which the content fields may still be edited
    _sf_editable_states = ("draft",)
    # fields that freeze outside those states (the record's terms)
    _sf_terms = ()

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and "state" in rec._fields and rec.state not in self._sf_editable_states:
            locked |= set(self._sf_terms)
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            guarded = self._fix_guarded_fields()
            for rec in self:
                if "state" not in rec._fields or rec.state in self._sf_editable_states:
                    continue
                changed = [
                    n
                    for n in set(self._sf_terms) & set(vals)
                    if n not in guarded and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "%s cannot be changed on %s: it is %s. Retire it and record a new one."
                        % (
                            ", ".join(sorted(rec._fields[n].string or n for n in changed)),
                            rec.display_name,
                            dict(rec._fields["state"].selection)[rec.state],
                        )
                    )
        return super().write(vals)

    def _sf_assert_not_author(self, what):
        for rec in self:
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "%s: %s was recorded by you; another Storefront Manager decides it."
                    % (what, rec.display_name)
                )


# --------------------------------------------------------------- page 1
class FixStorefrontContent(models.Model):
    _name = "fix.storefront.content"
    _description = "Storefront Content (Banner / Page)"
    _inherit = ["mail.thread", "fix.storefront.capture.mixin"]
    _order = "valid_from desc, id desc"

    _sf_editable_states = ("draft",)
    _sf_terms = (
        "name",
        "name_bn",
        "code",
        "content_type",
        "slot",
        "body_en",
        "body_bn",
        "image",
        "link_url",
        "audience",
        "valid_from",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(string="Title (English)", required=True, tracking=True)
    name_bn = fields.Char(string="Title (Bengali)")
    code = fields.Char(required=True, copy=False)
    content_type = fields.Selection(
        [
            ("banner", "Banner"),
            ("landing", "Landing Page"),
            ("campaign", "Campaign Page"),
            ("policy", "Policy Page"),
        ],
        required=True,
        default="banner",
    )
    slot = fields.Char(string="Placement Slot", help="Where it shows, e.g. home_hero, cart_top.")
    body_en = fields.Text(string="Content (English)")
    body_bn = fields.Text(string="Content (Bengali)")
    image = fields.Binary(string="Banner Image", attachment=True)
    image_filename = fields.Char()
    link_url = fields.Char(string="Link")
    audience = fields.Selection(AUDIENCES, required=True, default="all")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        default="draft",
        required=True,
        tracking=True,
    )
    published_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    published_at = fields.Datetime(readonly=True, copy=False)

    _code_unique = models.UniqueIndex("(company_id, code)", "This content code is already used.")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "published_by_id", "published_at"}

    @api.constrains("valid_from", "valid_to")
    def _check_dates(self):
        for rec in self:
            if rec.valid_to and rec.valid_to < rec.valid_from:
                raise ValidationError("Content %s ends before it starts." % rec.name)

    def action_publish(self):
        _require(self.env, [GROUP_MERCHANDISER], "Publishing storefront content")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is %s: only a draft is published." % (rec.name, rec.state))
            # FR-ECM-002: Bengali is the default language; nothing goes live
            # in one language only.
            if not (rec.name_bn or "").strip():
                raise UserError("%s needs its Bengali title before publication." % rec.name)
            if rec.content_type == "banner":
                if not rec.image:
                    raise UserError("Banner %s needs its image before publication." % rec.name)
            elif not ((rec.body_en or "").strip() and (rec.body_bn or "").strip()):
                raise UserError(
                    "%s needs its content in both English and Bengali before publication."
                    % rec.name
                )
            if rec.valid_to and rec.valid_to < fields.Date.context_today(rec):
                raise UserError("%s has already expired." % rec.name)
            rec._guarded().write(
                {
                    "state": "published",
                    "published_by_id": self.env.uid,
                    "published_at": fields.Datetime.now(),
                }
            )
        return True

    def action_retire(self):
        _require(self.env, [GROUP_MERCHANDISER], "Retiring storefront content")
        self.filtered(lambda r: r.state != "retired")._guarded().write({"state": "retired"})
        return True


# --------------------------------------------------------------- page 2
class FixStorefrontCollection(models.Model):
    _name = "fix.storefront.collection"
    _description = "Storefront Collection / Merchandising Set"
    _inherit = ["mail.thread", "fix.storefront.capture.mixin"]
    _order = "sequence, id desc"

    _sf_editable_states = ("draft",)
    _sf_terms = (
        "name",
        "name_bn",
        "code",
        "collection_type",
        "anchor_product_id",
        "product_ids",
        "category_id",
        "audience",
        "valid_from",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(string="Name (English)", required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)")
    code = fields.Char(required=True, copy=False)
    sequence = fields.Integer(default=10)
    collection_type = fields.Selection(
        [
            ("collection", "Collection"),
            ("featured", "Featured Set"),
            ("cross_sell", "Cross-sell (companions)"),
            ("up_sell", "Up-sell (better alternatives)"),
        ],
        required=True,
        default="collection",
    )
    anchor_product_id = fields.Many2one(
        "product.template",
        string="Shown With",
        help="Cross- and up-sell: the item on whose page and cart line these are offered.",
    )
    product_ids = fields.Many2many(
        "product.template",
        "fix_sf_collection_product_rel",
        "collection_id",
        "product_id",
        string="Items",
    )
    category_id = fields.Many2one(
        "product.category",
        string="Rule: Category",
        help="Every sellable item of this category (and its sub-categories) belongs to it.",
    )
    audience = fields.Selection(AUDIENCES, required=True, default="all")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("retired", "Retired")],
        default="draft",
        required=True,
        tracking=True,
    )
    published_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    published_at = fields.Datetime(readonly=True, copy=False)

    _code_unique = models.UniqueIndex("(company_id, code)", "This collection code is already used.")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "published_by_id", "published_at"}

    @api.constrains("valid_from", "valid_to", "anchor_product_id", "product_ids")
    def _check_collection(self):
        for rec in self:
            if rec.valid_to and rec.valid_to < rec.valid_from:
                raise ValidationError("Collection %s ends before it starts." % rec.name)
            if rec.anchor_product_id and rec.anchor_product_id in rec.product_ids:
                raise ValidationError(
                    "%s cannot be offered alongside itself in %s."
                    % (rec.anchor_product_id.display_name, rec.name)
                )

    def action_publish(self):
        _require(self.env, [GROUP_MERCHANDISER], "Publishing a collection")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is %s: only a draft is published." % (rec.name, rec.state))
            if not (rec.name_bn or "").strip():
                raise UserError("%s needs its Bengali name before publication." % rec.name)
            if rec.collection_type in ("cross_sell", "up_sell"):
                if not rec.anchor_product_id or not rec.product_ids:
                    raise UserError(
                        "%s offers items alongside one item: name the item and what is "
                        "offered with it." % rec.name
                    )
            elif not rec.product_ids and not rec.category_id:
                raise UserError("%s needs its items or a category rule." % rec.name)
            # FR-ECM-001: only what may be sold online is merchandised.
            for product in rec.product_ids.sudo():
                if not product.sale_ok:
                    raise UserError(
                        "%s is not for sale and cannot be merchandised." % product.display_name
                    )
                # A04 ERP M38-F1: merchandised only at a released M11 price
                info = self.env["fix.storefront.cart.line"]._sf_m11_price(
                    product, company=rec.company_id
                )
                variant = product.product_variant_id
                if variant and hasattr(variant, "_fix_check_sale"):
                    variant._fix_check_sale(unit_price=info["excl"], channel="storefront")
            rec._guarded().write(
                {
                    "state": "published",
                    "published_by_id": self.env.uid,
                    "published_at": fields.Datetime.now(),
                }
            )
        return True

    def action_retire(self):
        _require(self.env, [GROUP_MERCHANDISER], "Retiring a collection")
        self.filtered(lambda r: r.state != "retired")._guarded().write({"state": "retired"})
        return True


# --------------------------------------------------------------- policies
class FixStorefrontPolicyMixin(models.AbstractModel):
    """A policy record: written by its author, activated by a Storefront
    Manager who did not write it, frozen while active, retired to change."""

    _name = "fix.storefront.policy.mixin"
    _description = "Storefront Policy Controls"
    _inherit = ["mail.thread", "fix.storefront.capture.mixin"]

    _sf_editable_states = ("draft",)

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_by_id", "approved_at"}

    def _sf_on_activate(self):
        """Hook: e.g. one active rule per company."""

    def action_activate(self):
        _require(self.env, [GROUP_MANAGER], "Approving a storefront policy")
        self._sf_assert_not_author("Approving")
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "%s is %s: only a draft is approved." % (rec.display_name, rec.state)
                )
        self._sf_on_activate()
        self._guarded().write(
            {
                "state": "active",
                "approved_by_id": self.env.uid,
                "approved_at": fields.Datetime.now(),
            }
        )
        return True

    def action_retire(self):
        _require(self.env, [GROUP_MANAGER], "Retiring a storefront policy")
        self.filtered(lambda r: r.state != "retired")._guarded().write({"state": "retired"})
        return True


def _category_chain(category):
    chain = []
    while category:
        chain.append(category)
        category = category.parent_id
    return chain


# --------------------------------------------------------------- page 4
class FixStorefrontCodRule(models.Model):
    _name = "fix.storefront.cod.rule"
    _description = "Cash-on-Delivery Eligibility Rule"
    _inherit = ["fix.storefront.policy.mixin"]
    _order = "id desc"

    _sf_terms = (
        "name",
        "currency_id",
        "max_order_value",
        "history_value",
        "min_delivered_orders",
        "max_open_cod_orders",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    max_order_value = fields.Monetary(
        string="Largest COD Order", required=True, help="No COD order above this value."
    )
    history_value = fields.Monetary(
        string="History Needed Above",
        help="An order above this value needs the customer's delivery history below.",
    )
    min_delivered_orders = fields.Integer(
        string="Delivered Orders Needed", help="Delivered storefront orders the customer must have."
    )
    max_open_cod_orders = fields.Integer(
        string="Open COD Orders Allowed",
        help="COD orders not yet delivered or cancelled a customer may hold (0 = no limit).",
    )

    @api.constrains(
        "max_order_value", "history_value", "min_delivered_orders", "max_open_cod_orders"
    )
    def _check_rule(self):
        for rec in self:
            if rec.max_order_value <= 0:
                raise ValidationError("A COD rule needs a positive largest order value.")
            if rec.history_value < 0 or rec.min_delivered_orders < 0 or rec.max_open_cod_orders < 0:
                raise ValidationError("COD rule limits cannot be negative.")

    def _sf_on_activate(self):
        # one active rule per company: the new one replaces the old
        for rec in self:
            self.search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "active"),
                    ("id", "!=", rec.id),
                ]
            )._guarded().write({"state": "retired"})

    @api.model
    def _sf_check_cod(self, cart, total):
        rule = self.sudo().search(
            [("company_id", "=", cart.company_id.id), ("state", "=", "active")], limit=1
        )
        if not rule:
            # A04 ERP audit M38-F12 (BRU-ECM-08): COD with no approved rule
            # was unlimited (0 rules on fix_real). Fail closed: no COD until
            # a Storefront Manager approves the company's COD rule (OWNER).
            raise UserError(
                "Cash on delivery is not offered: %s has no approved COD rule. Please choose a "
                "prepaid method." % cart.company_id.name
            )
        if cart.currency_id.compare_amounts(total, rule.max_order_value) > 0:
            raise UserError(
                "Cash on delivery is offered up to BDT %.2f; this order is BDT %.2f. "
                "Please choose a prepaid method (rule %s)."
                % (rule.max_order_value, total, rule.name)
            )
        Order = self.env["fix.storefront.order"].sudo()
        partner = cart.customer_id.commercial_partner_id
        if rule.min_delivered_orders and total > (rule.history_value or 0.0):
            delivered = Order.search_count(
                [("customer_id", "child_of", partner.id), ("state", "=", "delivered")]
            )
            if delivered < rule.min_delivered_orders:
                raise UserError(
                    "Cash on delivery above BDT %.2f needs %d delivered orders; %s has %d "
                    "(rule %s)."
                    % (
                        rule.history_value or 0.0,
                        rule.min_delivered_orders,
                        partner.display_name,
                        delivered,
                        rule.name,
                    )
                )
        if rule.max_open_cod_orders:
            open_cod = Order.search_count(
                [
                    ("customer_id", "child_of", partner.id),
                    ("payment_rail", "=", "cod"),
                    ("state", "in", ("draft", "pending_payment", "paid", "dispatched")),
                ]
            )
            if open_cod >= rule.max_open_cod_orders:
                raise UserError(
                    "%s already holds %d open cash-on-delivery orders, the most allowed "
                    "(rule %s)." % (partner.display_name, open_cod, rule.name)
                )


# --------------------------------------------------------------- page 6
class FixStockExposurePolicy(models.Model):
    _name = "fix.stock.exposure.policy"
    _description = "Online Stock Exposure Policy"
    _inherit = ["fix.storefront.policy.mixin"]
    _order = "id desc"

    _sf_terms = (
        "name",
        "product_id",
        "category_id",
        "location_ids",
        "stock_location_ids",
        "buffer_qty",
        "buffer_pct",
        "max_promise_days",
        "enabled",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True)
    product_id = fields.Many2one("product.template", string="Item")
    category_id = fields.Many2one("product.category", string="Category")
    location_ids = fields.Many2many(
        "stock.location",
        "fix_sf_exposure_location_rel",
        "policy_id",
        "location_id",
        string="Odoo Locations (not used)",
        help="Superseded by the M15 stores below (A04 ERP M38-F11): Odoo stock.quant holds no "
        "stock on this estate.",
    )
    # A04 ERP audit M38-F11: the M15 stores whose stock may be sold online
    stock_location_ids = fields.Many2many(
        "fix.stock.location",
        "fix_sf_exposure_m15_location_rel",
        "policy_id",
        "location_id",
        string="Stores Sold From (M15)",
        help="Unrestricted, owned M15 stock held here may be sold online. Empty: every branch "
        "and central store of the company.",
    )
    buffer_qty = fields.Float(
        string="Buffer (units)", help="Units kept back for walk-in customers."
    )
    buffer_pct = fields.Float(string="Buffer (%)", help="Share of the stock kept back.")
    max_promise_days = fields.Integer(string="Longest Promise (days)")
    enabled = fields.Boolean(
        string="Sold Online",
        default=True,
        help="Off: the item or category is withdrawn from online sale.",
    )

    @api.constrains(
        "name", "product_id", "category_id", "buffer_qty", "buffer_pct", "max_promise_days"
    )
    def _check_policy(self):
        for rec in self:
            if bool(rec.product_id) == bool(rec.category_id):
                raise ValidationError(
                    "Exposure policy %s covers either one item or one category." % rec.name
                )
            if rec.buffer_qty < 0 or not 0.0 <= rec.buffer_pct <= 100.0 or rec.max_promise_days < 0:
                raise ValidationError(
                    "Exposure policy %s: buffers are 0 or more units and 0-100%%." % rec.name
                )

    def _sf_on_activate(self):
        for rec in self:
            scope = (
                [("product_id", "=", rec.product_id.id)]
                if rec.product_id
                else [("category_id", "=", rec.category_id.id)]
            )
            self.search(
                [
                    *scope,
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "active"),
                    ("id", "!=", rec.id),
                ]
            )._guarded().write({"state": "retired"})

    @api.model
    def _sf_policy_for(self, product, company):
        active = self.sudo().search([("company_id", "=", company.id), ("state", "=", "active")])
        if not active:
            return self.browse()
        own = active.filtered(lambda p: p.product_id == product)
        if own:
            return own[:1]
        for category in _category_chain(product.categ_id):
            hit = active.filtered(lambda p, c=category: p.category_id == c)
            if hit:
                return hit[:1]
        return self.browse()

    def _sf_exposable_qty(self, product):
        """Units of `product` this policy offers online: on hand in its
        locations, less the buffer (the larger of units and share)."""
        self.ensure_one()
        on_hand = self._sf_m15_free_qty(product, self.company_id, self.stock_location_ids)
        buffer = max(self.buffer_qty, math.ceil(on_hand * self.buffer_pct / 100.0))
        return max(on_hand - buffer, 0.0)

    @api.model
    def _sf_m15_free_qty(self, product, company, locations=None):
        """A04 ERP audit M38-F11: the unreserved, unrestricted, owned M15
        stock (fix.stock.onhand qty - reserved) of the spare parts behind
        `product` in the company's branch and central stores (or `locations`).
        The policy read Odoo stock.quant, which holds 0 rows here."""
        Part = self.env["fix.spare.part"].sudo()
        parts = Part.search(
            [
                ("product_id.product_tmpl_id", "=", product.id),
                ("company_id", "in", [company.id, False]),
            ]
        )
        if not parts:
            return 0.0
        domain = [
            ("part_id", "in", parts.ids),
            ("location_id.company_id", "=", company.id),
            ("ownership_class", "=", "owned"),
            ("stock_status", "=", "unrestricted"),
        ]
        if locations:
            domain.append(("location_id", "in", locations.ids))
        else:
            domain.append(("location_id.location_type", "in", ("branch", "central")))
        rows = self.env["fix.stock.onhand"].sudo().search(domain)
        return sum(max((r.qty or 0.0) - (r.reserved or 0.0), 0.0) for r in rows)

    @api.model
    def _sf_check_exposure(self, product, qty, company):
        """BRU-ECM-04: only stock within the governed exposure policy is sold
        online. Raises UserError when `qty` of `product` may not be sold."""
        product = product.sudo()
        policy = self._sf_policy_for(product, company)
        if not policy:
            strict = self.env["ir.config_parameter"].sudo().get_param(EXPOSURE_STRICT_PARAM)
            if strict in ("1", "True", "true"):
                raise UserError(
                    "%s is not covered by an approved online exposure policy and is not sold "
                    "online." % product.display_name
                )
            return
        if not policy.enabled:
            raise UserError(
                "%s is withdrawn from online sale (exposure policy %s)."
                % (product.display_name, policy.name)
            )
        if product.type != "consu" or not getattr(product, "is_storable", True):
            return  # services and non-stocked items carry no stock to expose
        exposable = policy._sf_exposable_qty(product)
        if qty > exposable + 1e-6:
            raise UserError(
                "Only %s of %s may be sold online now (exposure policy %s keeps a buffer "
                "for the branches)." % (int(exposable), product.display_name, policy.name)
            )


# --------------------------------------------------------------- page 7
class FixStorefrontReturnPolicy(models.Model):
    _name = "fix.storefront.return.policy"
    _description = "Storefront Return Policy"
    _inherit = ["fix.storefront.policy.mixin"]
    _order = "id desc"

    _sf_terms = ("name", "category_id", "window_days", "restocking_fee_pct")

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True)
    category_id = fields.Many2one(
        "product.category", string="Category", help="Empty: the default for every category."
    )
    window_days = fields.Integer(string="Return Window (days)", required=True, default=7)
    restocking_fee_pct = fields.Float(
        string="Change-of-mind Restocking Fee (%)",
        default=20.0,
        help="Deducted when a change-of-mind return comes back as grade B.",
    )

    @api.constrains("window_days", "restocking_fee_pct")
    def _check_policy(self):
        for rec in self:
            if rec.window_days <= 0:
                raise ValidationError("A return window is at least one day.")
            if not 0.0 <= rec.restocking_fee_pct <= 100.0:
                raise ValidationError("A restocking fee is 0-100%.")

    def _sf_on_activate(self):
        for rec in self:
            self.search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("category_id", "=", rec.category_id.id or False),
                    ("state", "=", "active"),
                    ("id", "!=", rec.id),
                ]
            )._guarded().write({"state": "retired"})

    @api.model
    def _sf_policies_for(self, order):
        """The active policy of each line's category (most specific first,
        then the company default)."""
        active = self.sudo().search(
            [("company_id", "=", order.company_id.id), ("state", "=", "active")]
        )
        if not active:
            return self.browse()
        found = self.browse()
        default = active.filtered(lambda p: not p.category_id)[:1]
        for line in order.sudo().line_ids:
            hit = self.browse()
            for category in _category_chain(line.product_id.categ_id):
                hit = active.filtered(lambda p, c=category: p.category_id == c)[:1]
                if hit:
                    break
            found |= hit or default
        return found or default


class FixStorefrontOrderCapture(models.Model):
    _inherit = "fix.storefront.order"

    po_reference = fields.Char(related="cart_id.po_reference", string="Client PO Reference")
    corporate_account_id = fields.Many2one(
        related="cart_id.corporate_account_id", string="Corporate Account"
    )
    change_ids = fields.One2many("fix.storefront.order.change", "order_id", string="Changes")

    def _sf_window_days(self) -> int:
        # the longest window of the policies its lines fall under: no line
        # loses the window its own category grants
        if len(self) == 1:
            policies = self.env["fix.storefront.return.policy"]._sf_policies_for(self)
            if policies:
                return max(policies.mapped("window_days"))
        return super()._sf_window_days()

    def _sf_restocking_pct(self) -> float:
        if len(self) == 1:
            policies = self.env["fix.storefront.return.policy"]._sf_policies_for(self)
            if policies:
                return min(policies.mapped("restocking_fee_pct"))
        raw = self.env["ir.config_parameter"].sudo().get_param(RESTOCKING_FEE_PARAM)
        try:
            fee = float(raw) if raw else RESTOCKING_FEE_PCT_DEFAULT
        except ValueError:
            fee = RESTOCKING_FEE_PCT_DEFAULT
        return min(max(fee, 0.0), 100.0)


# --------------------------------------------------------------- page 8
class FixStorefrontCorporateAccount(models.Model):
    _name = "fix.storefront.corporate.account"
    _description = "Corporate Commerce Account"
    _inherit = ["fix.storefront.policy.mixin"]
    _order = "id desc"

    _sf_terms = (
        "partner_id",
        "approver_ids",
        "approval_threshold",
        "po_required",
        "category_ids",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(related="partner_id.name", store=True, string="Client")
    partner_id = fields.Many2one(
        "res.partner", string="Corporate Client", required=True, domain=[("is_company", "=", True)]
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    approver_ids = fields.Many2many(
        "res.partner",
        "fix_sf_corporate_approver_rel",
        "account_id",
        "partner_id",
        string="Client Approvers",
        help="The client's own people who approve its orders (BRU-ECM-14).",
    )
    approval_threshold = fields.Monetary(
        string="Client Approval Above",
        help="Orders above this value need a client approver (0: every order).",
    )
    po_required = fields.Boolean(string="PO Reference Required", default=True)
    category_ids = fields.Many2many(
        "product.category",
        "fix_sf_corporate_category_rel",
        "account_id",
        "category_id",
        string="Agreed Catalogue",
        help="The categories this client may order (and their sub-categories). Empty: all.",
    )

    @api.constrains("partner_id", "approver_ids", "approval_threshold")
    def _check_account(self):
        for rec in self:
            if rec.approval_threshold < 0:
                raise ValidationError("The approval threshold cannot be negative.")
            client = rec.partner_id.commercial_partner_id
            strangers = rec.approver_ids.filtered(lambda p, c=client: p.commercial_partner_id != c)
            if strangers:
                raise ValidationError(
                    "%s do not work for %s and cannot approve its orders."
                    % (", ".join(strangers.mapped("display_name")), client.display_name)
                )

    def _sf_on_activate(self):
        for rec in self:
            if not rec.approver_ids:
                raise UserError("%s needs at least one client approver." % rec.name)
            self.search(
                [
                    ("partner_id", "=", rec.partner_id.id),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "active"),
                    ("id", "!=", rec.id),
                ]
            )._guarded().write({"state": "retired"})

    def _sf_check_order(self, cart, total):
        """BRU-ECM-14 and FR-ECM-052/054 at placement."""
        self.ensure_one()
        acct = self.sudo()
        if acct.state != "active":
            raise UserError("Corporate account %s is not active." % acct.name)
        if cart.customer_id.commercial_partner_id != acct.partner_id.commercial_partner_id:
            raise UserError("%s is not a buyer of %s." % (cart.customer_id.display_name, acct.name))
        if acct.po_required and not (cart.po_reference or "").strip():
            raise UserError("%s orders carry the client's purchase-order reference." % acct.name)
        if acct.category_ids:
            for line in cart.line_ids.sudo():
                categ = line.product_id.categ_id
                if not any(c in acct.category_ids for c in _category_chain(categ)):
                    raise UserError(
                        "%s is outside %s's agreed catalogue."
                        % (line.product_id.display_name, acct.name)
                    )
        needs_approval = (
            cart.currency_id.compare_amounts(total, acct.approval_threshold) > 0
            or not acct.approval_threshold
        )
        if needs_approval and not cart.client_approved_at:
            raise UserError(
                "This %s order of BDT %.2f needs the approval of one of the client's "
                "approvers first." % (acct.name, total)
            )


# --------------------------------------------------------------- page 3
class FixStorefrontCartCapture(models.Model):
    _inherit = "fix.storefront.cart"

    channel = fields.Selection(
        [
            ("web", "Web Storefront"),
            ("app", "Mobile App"),
            ("assisted", "Assisted (staff)"),
            ("corporate", "Corporate (P04)"),
        ],
        default="web",
        required=True,
    )
    assisted_by_id = fields.Many2one("res.users", string="Captured By", readonly=True, copy=False)
    delivery_address = fields.Text(string="Delivery Address")
    delivery_method = fields.Selection(SHIPPING_METHODS, default="standard_delivery")
    payment_method = fields.Selection(PAYMENT_RAILS, default="bkash")
    slot_id = fields.Many2one(
        "fix.storefront.slot", string="Delivery / Pickup Slot", domain=[("state", "=", "open")]
    )
    # FR-ECM-026 / BRU-ECM-07: item-specific terms, explicitly accepted
    has_refurbished = fields.Boolean(compute="_compute_has_refurbished")
    terms_method = fields.Selection(
        [
            ("checkbox", "Ticked at checkout"),
            ("otp", "OTP confirmation"),
            ("signed", "Signed form"),
            ("recorded_call", "Recorded call"),
        ],
        string="How Terms Were Accepted",
    )
    terms_reference = fields.Char(string="Terms Acceptance Reference")
    terms_accepted_at = fields.Datetime(readonly=True, copy=False)
    terms_accepted_by_id = fields.Many2one(
        "res.users", string="Terms Recorded By", readonly=True, copy=False
    )
    # FR-ECM-052..054 / BRU-ECM-14: corporate order
    corporate_account_id = fields.Many2one(
        "fix.storefront.corporate.account",
        string="Corporate Account",
        domain=[("state", "=", "active")],
    )
    po_reference = fields.Char(string="Client PO Reference")
    client_approver_id = fields.Many2one("res.partner", string="Client Approver")
    client_approval_ref = fields.Char(string="Client Approval Reference")
    client_approved_at = fields.Datetime(readonly=True, copy=False)
    client_approval_recorded_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    recovery_attempt_ids = fields.One2many(
        "fix.storefront.recovery.attempt", "cart_id", string="Recovery Contacts"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "assisted_by_id",
            "terms_accepted_at",
            "terms_accepted_by_id",
            "client_approved_at",
            "client_approval_recorded_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state == "ordered":
            locked |= {
                "customer_id",
                "delivery_address",
                "delivery_method",
                "payment_method",
                "slot_id",
                "line_ids",
                "corporate_account_id",
                "po_reference",
                "client_approver_id",
                "client_approval_ref",
                "terms_method",
                "terms_reference",
            }
        if rec and rec.terms_accepted_at:
            locked |= {"terms_method", "terms_reference"}
        if rec and rec.client_approved_at:
            locked |= {
                "corporate_account_id",
                "po_reference",
                "client_approver_id",
                "client_approval_ref",
                "customer_id",
            }
        return locked

    @api.depends("line_ids.graded_stock_id")
    def _compute_has_refurbished(self):
        for rec in self:
            rec.has_refurbished = bool(rec.line_ids.filtered("graded_stock_id"))

    @api.model_create_multi
    def create(self, vals_list):
        internal = not self.env.su and self.env.user._is_internal()
        if internal:
            for vals in vals_list:
                vals["channel"] = "corporate" if vals.get("corporate_account_id") else "assisted"
        carts = super().create(vals_list)
        if internal:
            carts._guarded().write({"assisted_by_id": self.env.uid})
        return carts

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                frozen = rec._fix_form_locked_fields() - rec._fix_guarded_fields() - {"line_ids"}
                changed = [
                    n
                    for n in frozen & set(vals)
                    if n in rec._fields and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "%s cannot be changed on cart %s now (it is ordered, or the terms or "
                        "the client's approval are recorded for it)."
                        % (", ".join(sorted(rec._fields[n].string or n for n in changed)), rec.name)
                    )
        return super().write(vals)

    def _sf_lines_frozen(self) -> bool:
        self.ensure_one()
        return self.state == "ordered" or bool(self.client_approved_at)

    def _sf_assert_not_capturer(self, what):
        """A04 ERP audit M38-F5: the person who captured an assisted cart
        does not also record the customer's or the client's consent on it."""
        for rec in self:
            if not self.env.su and rec.assisted_by_id and rec.assisted_by_id == self.env.user:
                raise UserError(
                    "%s: you captured cart %s; another colleague records it (segregation of "
                    "duties, A04 ERP M38-F5)." % (what, rec.name)
                )

    def action_record_terms(self):
        """The customer's acceptance of the item terms, as taken (FR-ECM-026).
        A04 ERP M38-F5: an assisted-sales or storefront operator role, never
        the colleague who captured the cart."""
        _require(self.env, [GROUP_ASSISTED, GROUP_OPERATOR], "Recording the customer's terms")
        self._sf_assert_not_capturer("Recording the customer's terms")
        for rec in self:
            if rec.state == "ordered":
                raise UserError("Cart %s is already ordered." % rec.name)
            if not rec.terms_method:
                raise UserError("Say how the customer accepted the terms.")
            if rec.terms_method != "checkbox" and not (rec.terms_reference or "").strip():
                raise UserError(
                    "An OTP, a signed form or a recorded call has a reference: record it."
                )
            rec.sudo()._guarded().write(
                {"terms_accepted_at": fields.Datetime.now(), "terms_accepted_by_id": self.env.uid}
            )
        return True

    def action_record_client_approval(self):
        """The client's own approver approved this corporate order (BRU-ECM-14).
        A04 ERP M38-F5: a Storefront Operator records it, never the colleague
        who captured the cart."""
        _require(self.env, [GROUP_OPERATOR], "Recording a client's approval")
        self._sf_assert_not_capturer("Recording the client's approval")
        for rec in self:
            acct = rec.corporate_account_id.sudo()
            if not acct:
                raise UserError("Cart %s is not a corporate order." % rec.name)
            if acct.state != "active":
                raise UserError("Corporate account %s is not active." % acct.name)
            if rec.state == "ordered":
                raise UserError("Cart %s is already ordered." % rec.name)
            if not rec.line_ids:
                raise UserError("Cart %s has nothing to approve." % rec.name)
            if rec.client_approver_id not in acct.approver_ids:
                raise UserError("Name the client approver: one of %s's own approvers." % acct.name)
            if not (rec.client_approval_ref or "").strip():
                raise UserError(
                    "Record the reference of the client's approval (email, PO sign-off)."
                )
            rec.sudo()._guarded().write(
                {
                    "client_approved_at": fields.Datetime.now(),
                    "client_approval_recorded_by_id": self.env.uid,
                }
            )
        return True

    def action_place_assisted_order(self):
        """Place the order the cart's own checkout data describes."""
        self.ensure_one()
        if not self.env.user._is_internal() and not self.env.su:
            raise UserError("Assisted ordering is a staff action.")
        _require(self.env, [GROUP_ASSISTED, GROUP_OPERATOR], "Placing an assisted order")
        if self.state == "open":
            self.action_checkout()
        order = self.action_place_order(
            shipping_address=self.delivery_address,
            shipping_method=self.delivery_method or "standard_delivery",
            payment_rail=self.payment_method or "bkash",
            slot_id=self.slot_id.id or None,
        )
        return bool(order)

    def action_place_order(
        self,
        shipping_address=None,
        shipping_method="standard_delivery",
        payment_rail="bkash",
        slot_id=None,
        voucher_code=None,
        idempotency_key=None,
    ):
        self.ensure_one()
        rec = self
        if rec.state != "ordered" and rec.line_ids:
            lines = rec.line_ids.sudo()
            total = sum(line.quantity * line._sf_server_price() for line in lines)
            # A04 ERP round 2 (M38-F14): the COD and credit limits read what the
            # customer will pay - goods plus the delivery fee less the voucher
            fee = rec._sf_delivery_fee(shipping_method or "standard_delivery")
            total += fee["incl"] if fee else 0.0
            if (voucher_code or "").strip():
                total -= rec._sf_voucher_discount(voucher_code)["incl"]
            # BRU-ECM-07: refurbished condition terms are accepted, explicitly
            if lines.filtered("graded_stock_id") and not rec.terms_accepted_at:
                raise UserError(
                    "Cart %s holds a refurbished device: the customer's acceptance of its "
                    "condition and warranty terms is recorded first." % rec.name
                )
            # BRU-ECM-04 / T-05: exposure re-checked at placement
            Exposure = self.env["fix.stock.exposure.policy"]
            for line in lines.filtered(lambda ln: not ln.graded_stock_id):
                Exposure._sf_check_exposure(line.product_id, line.quantity, rec.company_id)
            # BRU-ECM-08
            if payment_rail == "cod":
                self.env["fix.storefront.cod.rule"]._sf_check_cod(rec, total)
            # BRU-ECM-14
            if rec.corporate_account_id:
                rec.corporate_account_id._sf_check_order(rec, total)
        return super().action_place_order(
            shipping_address=shipping_address,
            shipping_method=shipping_method,
            payment_rail=payment_rail,
            slot_id=slot_id,
            voucher_code=voucher_code,
            idempotency_key=idempotency_key,
        )


class FixStorefrontCartLineCapture(models.Model):
    _inherit = "fix.storefront.cart.line"

    @api.model_create_multi
    def create(self, vals_list):
        Cart = self.env["fix.storefront.cart"].sudo()
        Product = self.env["product.template"].sudo()
        Exposure = self.env["fix.stock.exposure.policy"]
        for vals in vals_list:
            cart = Cart.browse(vals.get("cart_id") or [])
            if cart and cart._sf_lines_frozen() and not self.env.su:
                raise UserError("Cart %s is ordered or approved: its lines are fixed." % cart.name)
            if vals.get("product_id") and not vals.get("graded_stock_id"):
                Exposure._sf_check_exposure(
                    Product.browse(vals["product_id"]),
                    float(vals.get("quantity") or 1.0),
                    cart.company_id if cart else self.env.company,
                )
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            for line in self:
                if line.cart_id._sf_lines_frozen():
                    raise UserError(
                        "Cart %s is ordered or approved: its lines are fixed." % line.cart_id.name
                    )
            # the P03 grid posts every column it shows: an unchanged price or
            # refurbished item is not a hand-set one
            vals = dict(vals)
            for name in ("unit_price", "graded_stock_id", "unit_price_excl", "price_card_id"):
                if name in vals and all(
                    not line._sf_value_differs(name, vals[name]) for line in self
                ):
                    vals.pop(name)
            if "quantity" in vals:
                for line in self.filtered(lambda ln: not ln.graded_stock_id):
                    self.env["fix.stock.exposure.policy"]._sf_check_exposure(
                        line.product_id, float(vals["quantity"] or 0.0), line.cart_id.company_id
                    )
        return super().write(vals)

    def _sf_value_differs(self, name, value) -> bool:
        field = self._fields[name]
        if field.type == "many2one":
            value = value.id if hasattr(value, "id") else (value or False)
            return (value or False) != (self[name].id or False)
        if field.type in ("char", "text", "selection"):
            return (value or False) != (self[name] or False)
        return abs(float(value or 0.0) - float(self[name] or 0.0)) > 1e-6

    def unlink(self):
        if not self.env.su:
            for line in self:
                if line.cart_id._sf_lines_frozen():
                    raise UserError(
                        "Cart %s is ordered or approved: its lines are fixed." % line.cart_id.name
                    )
        return super().unlink()


# --------------------------------------------------------------- page 5
class FixStorefrontOrderChange(models.Model):
    _name = "fix.storefront.order.change"
    _description = "Online Order Change Request"
    _inherit = ["mail.thread", "fix.storefront.capture.mixin"]
    _order = "id desc"

    _sf_editable_states = ("requested",)
    _sf_terms = ("order_id", "change_type", "new_address", "new_slot_id", "new_method", "reason")

    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    order_id = fields.Many2one(
        "fix.storefront.order", required=True, ondelete="cascade", index=True
    )
    customer_id = fields.Many2one(related="order_id.customer_id", string="Customer")
    change_type = fields.Selection(
        [
            ("address", "Delivery address"),
            ("slot", "Delivery / pickup slot"),
            ("method", "Delivery mode"),
        ],
        required=True,
        default="address",
    )
    new_address = fields.Text(string="New Address")
    new_slot_id = fields.Many2one(
        "fix.storefront.slot", string="New Slot", domain=[("state", "=", "open")]
    )
    new_method = fields.Selection(SHIPPING_METHODS, string="New Delivery Mode")
    reason = fields.Text(required=True, string="Customer's Reason")
    state = fields.Selection(
        [("requested", "Requested"), ("applied", "Applied"), ("refused", "Refused")],
        default="requested",
        required=True,
        tracking=True,
    )
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_at = fields.Datetime(readonly=True, copy=False)
    refusal_reason = fields.Char(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "decided_by_id",
            "decided_at",
            "refusal_reason",
        }

    def _sf_check_window(self, order, change_type):
        order = order.sudo()
        if order.state not in ("draft", "pending_payment", "paid"):
            raise UserError(
                "Order %s is %s: once dispatched a change goes through the M03 consignment."
                % (order.name, dict(order._fields["state"].selection)[order.state])
            )
        if change_type == "method" and order.state not in ("draft", "pending_payment"):
            raise UserError(
                "Order %s is paid: its delivery mode (and the price it carried) is fixed."
                % order.name
            )

    @api.model_create_multi
    def create(self, vals_list):
        Order = self.env["fix.storefront.order"]
        for vals in vals_list:
            order = Order.browse(vals.get("order_id") or [])
            self._sf_check_window(order, vals.get("change_type") or "address")
            vals.setdefault("company_id", order.sudo().company_id.id)
            vals.setdefault("operating_unit_id", order.sudo().operating_unit_id.id or False)
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.storefront.order.change") or "New"
                )
        changes = super().create(vals_list)
        for rec in changes:
            needed = {"address": "new_address", "slot": "new_slot_id", "method": "new_method"}[
                rec.change_type
            ]
            if not rec[needed]:
                raise ValidationError(
                    "A %s change names the new %s." % (rec.change_type, rec._fields[needed].string)
                )
        return changes

    def action_apply(self):
        _require(self.env, [GROUP_OPERATOR], "Applying an order change")
        for rec in self:
            if rec.state != "requested":
                raise UserError("%s is %s." % (rec.name, rec.state))
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError("%s was recorded by you; another operator applies it." % rec.name)
            order = rec.order_id.sudo()
            rec._sf_check_window(order, rec.change_type)
            if rec.change_type == "address":
                order.write({"shipping_address": rec.new_address})
            elif rec.change_type == "slot":
                rec.new_slot_id.sudo()._sf_assert_bookable()
                order._guarded().write({"slot_id": rec.new_slot_id.id})
            else:
                order.write({"shipping_method": rec.new_method})
            order.message_post(body="%s applied: %s." % (rec.name, rec.reason))
            rec._guarded().write(
                {
                    "state": "applied",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
        return True

    def action_refuse(self, reason=None):
        _require(self.env, [GROUP_OPERATOR], "Refusing an order change")
        reason = (str(reason).strip() if reason else "") or ""
        if not reason:
            raise UserError("Give the reason the change is refused.")
        for rec in self:
            if rec.state != "requested":
                raise UserError("%s is %s." % (rec.name, rec.state))
            rec._guarded().write(
                {
                    "state": "refused",
                    "refusal_reason": reason,
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
        return True


# --------------------------------------------------------------- page 9
class FixStorefrontRecoveryAttempt(models.Model):
    _name = "fix.storefront.recovery.attempt"
    _description = "Abandoned-Cart Recovery Contact"
    _inherit = ["fix.guarded.mixin"]
    _order = "contacted_at desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    cart_id = fields.Many2one(
        "fix.storefront.cart",
        string="Cart",
        required=True,
        ondelete="cascade",
        index=True,
        domain=[("state", "in", ("open", "checkout"))],
    )
    customer_id = fields.Many2one(related="cart_id.customer_id", store=True, string="Customer")
    cart_total = fields.Monetary(related="cart_id.total", string="Cart Value")
    currency_id = fields.Many2one(related="cart_id.currency_id")
    channel = fields.Selection(
        [("call", "Phone call"), ("sms", "SMS"), ("whatsapp", "WhatsApp"), ("email", "Email")],
        required=True,
        default="call",
    )
    outcome = fields.Selection(
        [
            ("no_answer", "No answer"),
            ("reminded", "Reminded, resume link sent"),
            ("will_resume", "Customer will complete"),
            ("declined", "Customer declined"),
            ("wrong_number", "Wrong contact"),
        ],
        required=True,
    )
    note = fields.Char()
    contacted_at = fields.Datetime(readonly=True, copy=False)
    contacted_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    converted = fields.Boolean(
        compute="_compute_converted",
        string="Ordered After Contact",
        help="The cart became an order after this contact.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"contacted_at", "contacted_by_id"}

    @api.depends("cart_id.name", "channel")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s · %s" % (
                rec.cart_id.name or "",
                dict(rec._fields["channel"].selection).get(rec.channel, ""),
            )

    def _compute_converted(self):
        for rec in self:
            order = rec.cart_id.sudo().order_id
            rec.converted = bool(
                order and rec.contacted_at and order.order_date >= rec.contacted_at
            )

    @api.model_create_multi
    def create(self, vals_list):
        Cart = self.env["fix.storefront.cart"].sudo()
        for vals in vals_list:
            cart = Cart.browse(vals.get("cart_id") or [])
            if not cart or cart.state == "ordered":
                raise UserError("Only an open, unordered cart is followed up.")
            vals.setdefault("company_id", cart.company_id.id)
            vals.setdefault("operating_unit_id", cart.operating_unit_id.id or False)
        records = super().create(vals_list)
        records._guarded().write(
            {"contacted_at": fields.Datetime.now(), "contacted_by_id": self.env.uid}
        )
        return records

    def write(self, vals):
        # a contact log: what happened stays as recorded
        if self and not self._fix_guard_open():
            # the form posts every field it shows: only a real change counts
            changed = [
                n
                for n in set(vals) - {"note"}
                if n in self._fields
                and any(rec._fix_guard_differs(n, vals[n], rec[n]) for rec in self)
            ]
            if changed:
                raise UserError("A recovery contact is a log entry: record a new contact instead.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A recovery contact is a log entry and is not deleted.")
        return super().unlink()


# --------------------------------------------------------------- page 10
class FixStorefrontSlotCapture(models.Model):
    _inherit = "fix.storefront.slot"

    slot_type = fields.Selection(
        selection_add=[("service", "Service appointment slot")],
        ondelete={"service": "set default"},
    )
    branch_id = fields.Many2one("fix.branch", string="Branch")
    booking_ids = fields.One2many(
        "fix.storefront.service.booking", "slot_id", string="Service Bookings"
    )

    @api.depends("order_ids.state", "booking_ids.state", "capacity", "is_closed")
    def _compute_booked(self):
        for slot in self:
            orders = len(slot.order_ids.filtered(lambda o: o.state != "cancelled"))
            bookings = len(slot.booking_ids.filtered(lambda b: b.state != "cancelled"))
            slot.booked = orders + bookings
            if slot.is_closed:
                slot.state = "closed"
            elif slot.booked >= slot.capacity:
                slot.state = "full"
            else:
                slot.state = "open"


SERVICE_CHANNELS = {
    "web_portal": "web_portal",
    "mobile_app": "mobile_app",
    "hotline": "hotline",
    "whatsapp": "whatsapp",
}


class FixStorefrontServiceBooking(models.Model):
    _name = "fix.storefront.service.booking"
    _description = "Online Service Booking"
    _inherit = ["mail.thread", "fix.storefront.capture.mixin"]
    _order = "id desc"

    _sf_editable_states = ("requested",)
    _sf_terms = ("customer_id", "device_id", "branch_id", "slot_id", "fault_description", "channel")

    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    device_id = fields.Many2one("fix.device", string="Device", required=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True)
    slot_id = fields.Many2one(
        "fix.storefront.slot",
        string="Appointment Slot",
        required=True,
        ondelete="restrict",
        domain=[("slot_type", "=", "service"), ("state", "=", "open")],
    )
    fault_description = fields.Text(required=True)
    channel = fields.Selection(
        [
            ("web_portal", "Web storefront"),
            ("mobile_app", "Mobile app"),
            ("hotline", "Hotline 16743 (assisted)"),
            ("whatsapp", "WhatsApp (assisted)"),
        ],
        required=True,
        default="hotline",
    )
    photo = fields.Binary(string="Fault Photograph", attachment=True)
    photo_filename = fields.Char()
    state = fields.Selection(
        [("requested", "Requested"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
        default="requested",
        required=True,
        tracking=True,
    )
    service_order_id = fields.Many2one(
        "fix.service.order", string="M01 Service Order", readonly=True, copy=False
    )
    confirmed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    confirmed_at = fields.Datetime(readonly=True, copy=False)
    cancel_reason = fields.Char(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "service_order_id",
            "confirmed_by_id",
            "confirmed_at",
            "cancel_reason",
        }

    @api.constrains("customer_id", "device_id", "slot_id", "branch_id")
    def _check_booking(self):
        for rec in self:
            device = rec.device_id.sudo()
            if device and not device._owner_is(rec.customer_id):
                raise ValidationError(
                    "%s is not registered to %s."
                    % (device.display_name, rec.customer_id.display_name)
                )
            slot = rec.slot_id.sudo()
            if slot.slot_type != "service":
                raise ValidationError("%s is not a service appointment slot." % slot.name)
            if slot.branch_id and slot.branch_id != rec.branch_id:
                raise ValidationError(
                    "%s belongs to %s." % (slot.name, slot.branch_id.display_name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        Slot = self.env["fix.storefront.slot"].sudo()
        for vals in vals_list:
            slot = Slot.browse(vals.get("slot_id") or [])
            slot._sf_assert_bookable()
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.storefront.service.booking") or "New"
                )
        return super().create(vals_list)

    def action_confirm(self):
        """BRU-ECM-11: the booking becomes the M01 service order; the booking
        never holds the service state itself (FR-ECM-033)."""
        _require(self.env, [GROUP_OPERATOR], "Confirming a service booking")
        for rec in self:
            if rec.state != "requested":
                raise UserError("%s is %s." % (rec.name, rec.state))
            slot = rec.slot_id.sudo()
            if slot.is_closed:
                raise UserError("Slot %s is closed." % slot.name)
            if slot.slot_date and slot.slot_date < fields.Date.context_today(rec):
                raise UserError("Slot %s is in the past." % slot.name)
            order = (
                self.env["fix.service.order"]
                .sudo()
                .create(
                    {
                        "company_id": rec.company_id.id,
                        "customer_id": rec.customer_id.id,
                        "device_id": rec.device_id.id,
                        "branch_id": rec.branch_id.id,
                        "fault_description": rec.fault_description,
                        "service_type": SERVICE_CHANNELS[rec.channel],
                        "idempotency_key": "storefront-booking-%s" % rec.id,
                    }
                )
            )
            if rec.photo:
                self.env["ir.attachment"].sudo().create(
                    {
                        "name": rec.photo_filename or "%s-fault-photo" % rec.name,
                        "datas": rec.photo,
                        "res_model": "fix.service.order",
                        "res_id": order.id,
                    }
                )
            order.message_post(
                body="Booked online as %s for slot %s (%s)." % (rec.name, slot.name, slot.slot_date)
            )
            rec._guarded().write(
                {
                    "state": "confirmed",
                    "service_order_id": order.id,
                    "confirmed_by_id": self.env.uid,
                    "confirmed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self, reason=None):
        reason = (str(reason).strip() if reason else "") or ""
        if not reason:
            raise UserError("Give the reason the booking is cancelled.")
        for rec in self:
            if rec.state != "requested":
                raise UserError(
                    "%s is %s: a confirmed booking is the M01 service order now; cancel it there."
                    % (rec.name, rec.state)
                )
            if not (
                self.env.su
                or self.env.user.has_group(GROUP_OPERATOR)
                or rec.create_uid == self.env.user
            ):
                raise UserError("Only its author or a Storefront Operator cancels %s." % rec.name)
            # the author may withdraw their own request: checked above, written
            # as the system (a clerk holds no write right on bookings)
            rec.sudo()._guarded().write({"state": "cancelled", "cancel_reason": reason})
        return True
