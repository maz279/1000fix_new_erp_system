# A04 ERP audit round 2 (21 Nov 2026): the deferred M11 features
# (M11-F19) and the consumers of the catalogue / stock events (AUT-PRC-08..12).
#
# - FR-PRC-012  labour rate card: a rate card of kind 'labour_hour' holds a
#               rate per hour by repair level, skill band, brand, delivery mode
#               and branch; price_for prices a labour line with an SRT at
#               rate x standard repair time (M37).
# - FR-PRC-017  quantity / value / committed-volume breaks on a card, bracket
#               or cumulative.
# - FR-PRC-020  channel differential with a governed maximum spread
#   BRU-PRC-14  (cd_rate_card.max_channel_spread_pct; unset = no spread).
# - FR-PRC-032  every manual price override in a permanent log.
# - FR-PRC-036/045, AUT-PRC-11/12  exception, consistency and leakage scans.
# - AUT-PRC-08  a discontinued / superseded item: the pricing officer is told,
#               then its released rates are retired (contract rates stay until
#               the item is obsolete, BRU-CAT-10).
# - AUT-PRC-09  an SRT re-baseline moves no labour price until a releaser
#               accepts the review.
# - AUT-PRC-10  an M15 cost movement flags the cards now under the floor.
# - M37-F5      an M39 plan definition gives a subscription its price and cycle.
import logging
from collections import defaultdict
from datetime import timedelta
from itertools import pairwise

from odoo import api, fields, models
from odoo.addons.cd_catalogue.models.fix_catalogue_item import REPAIR_LEVELS
from odoo.addons.cd_catalogue.models.fix_catalogue_structure import DELIVERY_MODES
from odoo.addons.cd_catalogue.models.fix_catalogue_usage import SKILL_BANDS
from odoo.exceptions import AccessError, UserError, ValidationError

from .pricing_money import money
from .pricing_roles import (
    ROLE_OFFICER,
    ROLE_RELEASER,
    require_releaser_not_author,
    require_role,
)

_logger = logging.getLogger(__name__)

SPREAD_PARAM = "cd_rate_card.max_channel_spread_pct"
TARGET_MARGIN_PARAM = "cd_rate_card.margin_target_pct"
LEAKAGE_PARAM = "cd_rate_card.leakage_alert_pct"
WINDOW_PARAM = "cd_rate_card.consistency_window_days"
SCAN_CHANNELS = ("service", "quotation", "storefront", "marketplace")
RATE_KINDS = [
    ("unit", "Price per unit"),
    ("labour_hour", "Labour rate per hour (x standard repair time)"),
]
KIND_TERMS = frozenset(
    {
        "rate_kind",
        "repair_level",
        "skill_band",
        "brand_id",
        "delivery_mode",
        "operating_unit_id",
        "break_basis",
        "break_treatment",
    }
)
CHANNELS = [
    ("service", "Branch service (M01)"),
    ("quotation", "Quotation (M36)"),
    ("storefront", "Web / app storefront (M38)"),
    ("marketplace", "Marketplace (M12)"),
    ("contract", "Corporate contract (M08)"),
    ("subscription", "Subscription (M39)"),
    ("reseller", "Partner / reseller (M40)"),
]
M39_CYCLES = {"monthly": "monthly", "quarterly": "quarterly", "yearly": "annual"}


def _param_float(env, name):
    """The float value of a parameter, or None when unset / not a number."""
    raw = env["ir.config_parameter"].sudo().get_param(name)
    if raw in (None, False, ""):
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        _logger.warning("%s is not a number (%r); treated as unset.", name, raw)
        return None


# =========================================================================
# FR-PRC-012 / FR-PRC-017 on the rate card
# =========================================================================
class FixRateCardKinds(models.Model):
    _inherit = "fix.rate.card"

    rate_kind = fields.Selection(
        RATE_KINDS,
        string="Rate Kind",
        required=True,
        default="unit",
        index=True,
        help="Per unit (the price of the item), or a labour rate per hour that prices a "
        "labour line at rate x the M37 standard repair time (FR-PRC-012).",
    )
    repair_level = fields.Selection(REPAIR_LEVELS, string="Repair Level")
    skill_band = fields.Selection(SKILL_BANDS, string="Skill Band")
    brand_id = fields.Many2one("fix.brand", string="Brand", ondelete="restrict")
    delivery_mode = fields.Selection(DELIVERY_MODES, string="Delivery Mode")
    operating_unit_id = fields.Many2one(
        "operating.unit", string="Branch", help="Empty: every branch."
    )
    break_basis = fields.Selection(
        [
            ("quantity", "Quantity on the line"),
            ("value", "Line value at the card price"),
            ("committed", "Committed volume (contract)"),
        ],
        string="Break Basis",
        default="quantity",
    )
    break_treatment = fields.Selection(
        [
            ("bracket", "Bracket: every unit at the break reached"),
            ("cumulative", "Cumulative: each unit at the price of its band"),
        ],
        string="Break Treatment",
        default="bracket",
    )
    price_break_ids = fields.One2many("fix.price.break", "card_id", string="Volume Breaks")

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields()
        if any(card.state != "draft" for card in self):
            guarded |= KIND_TERMS
        return guarded

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(card.state != "draft" for card in self):
            locked |= KIND_TERMS | {"price_break_ids"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("rate_kind") == "labour_hour":
                vals["line_type"] = "labour"
                if not vals.get("product_code"):
                    vals["product_code"] = self._labour_code(vals)
        return super().create(vals_list)

    @api.model
    def _labour_code(self, vals):
        brand = (
            self.env["fix.brand"].browse(vals.get("brand_id")).exists()
            if vals.get("brand_id")
            else None
        )
        parts = [
            "LAB",
            (vals.get("repair_level") or "ALL").upper(),
            (vals.get("skill_band") or "ANY").upper(),
            (
                (brand.code if brand and "code" in brand._fields else None)
                or (brand.name if brand else "")
                or "ALL"
            )
            .upper()
            .replace(" ", ""),
            (vals.get("delivery_mode") or "ANY").upper(),
        ]
        if vals.get("operating_unit_id"):
            parts.append("OU%s" % vals["operating_unit_id"])
        return "-".join(parts)

    @api.constrains("rate_kind", "repair_level", "catalogue_item_id", "partner_id")
    def _check_kind(self):
        for card in self.filtered(lambda c: c.rate_kind == "labour_hour"):
            if not card.repair_level:
                raise ValidationError(
                    "A labour rate names the repair level it is paid at (FR-PRC-012)."
                )
            if card.catalogue_item_id:
                raise ValidationError(
                    "A labour rate prices every operation of its level by its standard repair "
                    "time; it names no single catalogue item."
                )
            if card.partner_id:
                raise ValidationError("A labour rate is a tier or contract rate, not a customer's.")
        for card in self:
            if card.break_treatment == "cumulative" and card.break_basis == "value":
                raise ValidationError(
                    "Cumulative breaks band units; a value break is a bracket (FR-PRC-017)."
                )

    @api.constrains("unit_price")
    def _check_card_breaks(self):
        """A card's breaks stay at or under its price (FR-PRC-017)."""
        self.mapped("price_break_ids")._check_break()

    # ---- FR-PRC-017 ---------------------------------------------------------
    def _apply_breaks(self, base, qty, facts=None):
        """(unit price, breaks used) of `qty` units on this card."""
        self.ensure_one()
        breaks = self.price_break_ids.sorted("threshold")
        if not breaks:
            return base, None
        qty = float(qty or 0.0)
        if self.break_basis == "committed":
            measure = float((facts or {}).get("committed_qty") or 0.0)
        elif self.break_basis == "value":
            measure = qty * base
        else:
            measure = qty
        if self.break_treatment == "bracket" or self.break_basis == "value":
            reached = breaks.filtered(lambda b: b.threshold <= measure + 1e-9)
            return (reached[-1].unit_price, reached[-1]) if reached else (base, None)
        if qty <= 0:
            return base, None
        bands = [(0.0, base)] + [(b.threshold, b.unit_price) for b in breaks]
        total = 0.0
        for n, (start, price) in enumerate(bands):
            end = bands[n + 1][0] if n + 1 < len(bands) else float("inf")
            total += max(0.0, min(qty, end) - start) * price
        return money(total / qty), breaks

    # ---- FR-PRC-032 --------------------------------------------------------
    @api.model
    def record_override(self, line, original, override, reason, approval=None, product=None):
        """Write the permanent record of a manual price override (FR-PRC-032):
        the document line, the released price, the price used, who, why and
        the approval behind it. For M01, M36, M38 and any selling line."""
        if not line:
            return self.env["fix.price.override.log"]
        product = product or (line["product_id"] if "product_id" in line._fields else None)
        parent = None
        for name in ("estimate_id", "quotation_id", "order_id"):
            if name in line._fields and line[name]:
                parent = line[name]
                break
        company = line["company_id"] if "company_id" in line._fields else None
        if not company and parent and "company_id" in parent._fields:
            company = parent.company_id
        return (
            self.env["fix.price.override.log"]
            .sudo()
            .create(
                {
                    "company_id": (company or self.env.company).id,
                    "res_model": line._name,
                    "res_id": line.id,
                    "document": (parent or line).display_name,
                    "product_id": product.id if product else False,
                    "original_price": float(original or 0.0),
                    "override_price": float(override or 0.0),
                    "actor_id": self.env.uid,
                    "reason": (reason or "").strip() or "(no reason recorded)",
                    "approval_ref": approval.display_name if approval else False,
                    "override_id": approval.id
                    if approval and approval._name == "fix.price.override"
                    else False,
                }
            )
        )

    # ---- FR-PRC-010 / BRU-PRC-17 -------------------------------------------
    @api.model
    def indicative_band(self, code, device_model=None, company=None):
        """The anonymous indicative price band of a published item:
        {item, item_bn, code, currency, low, high, vat, indicative}. It names
        no cost, margin, rule or card and no customer price (BRU-PRC-17):
        standard prices only (no customer, tier 0), on the storefront and
        branch channels, VAT-inclusive. None when the item is not published,
        does not sell, or has no released price."""
        company = company or self.env.company
        _variant, code, item = self._price_target(code)
        if not item or not item.is_published or item._sale_refusal("storefront"):
            return None
        models_ = [device_model] if device_model else [None]
        if not device_model and item.item_type in ("labour", "service", "inspection"):
            baselines = (
                self.env["fix.srt.baseline"]
                .sudo()
                .search([("item_id", "=", item.id), ("applied_at", "!=", False)])
            )
            models_ += list(baselines.mapped("device_model_id"))
        prices = []
        for channel in ("storefront", "service"):
            for model in models_:
                res = self.price_for(
                    item,
                    channel=channel,
                    company=company,
                    facts={"device_model": model} if model else None,
                )
                if res["price"] is not None and res.get("price_incl") is not None:
                    prices.append(res["price_incl"])
        if not prices:
            return None
        return {
            "item": item.name,
            "item_bn": item.name_bn or None,
            "code": code,
            "currency": "BDT",
            "low": min(prices),
            "high": max(prices),
            "vat": "inclusive",
            "indicative": True,
        }


class FixPriceBreak(models.Model):
    """FR-PRC-017: one break of a rate card."""

    _name = "fix.price.break"
    _description = "Rate Card Volume Break"
    _order = "card_id, threshold"

    card_id = fields.Many2one("fix.rate.card", required=True, index=True, ondelete="cascade")
    company_id = fields.Many2one(related="card_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="card_id.currency_id")
    threshold = fields.Float(
        required=True, help="From this quantity / value / committed volume the price applies."
    )
    unit_price = fields.Monetary(string="Unit Price From Here", required=True)

    def _locked(self):
        if self.env.su:
            return
        require_role(self.env, (ROLE_OFFICER,), "Changing a volume break")
        if any(b.card_id.state != "draft" for b in self):
            raise UserError(
                "The breaks of a released rate are part of the released price: change them "
                "through a new rate version."
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._locked()
        return records

    def write(self, vals):
        self._locked()
        return super().write(vals)

    def unlink(self):
        self._locked()
        return super().unlink()

    @api.constrains("threshold", "unit_price", "card_id")
    def _check_break(self):
        for brk in self:
            card = brk.card_id
            if brk.threshold <= 0 or brk.unit_price <= 0:
                raise ValidationError("A break has a positive threshold and a positive price.")
            if brk.unit_price > card.unit_price + 0.005:
                raise ValidationError("A volume break never raises the price above the card.")
            siblings = card.price_break_ids.sorted("threshold")
            if len(set(siblings.mapped("threshold"))) != len(siblings):
                raise ValidationError("Two breaks of one rate cannot share a threshold.")
            prices = siblings.mapped("unit_price")
            if any(later > earlier + 0.005 for earlier, later in pairwise(prices)):
                raise ValidationError("A higher break never has a higher price.")
            card._assert_not_below_floor(brk.unit_price)


# =========================================================================
# FR-PRC-020 / BRU-PRC-14
# =========================================================================
class FixChannelDifferential(models.Model):
    """A declared price differential of a channel against the card, within
    the governed maximum spread across channels (BRU-PRC-14)."""

    _name = "fix.channel.differential"
    _description = "Channel Price Differential"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "company_id, product_code, channel"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    channel = fields.Selection(CHANNELS, required=True, tracking=True)
    product_code = fields.Char(string="Item Code", index=True, help="Empty: the whole category.")
    category_id = fields.Many2one(
        "product.category", string="Category", help="Empty with no code: every item."
    )
    adjustment_pct = fields.Float(
        string="Differential (%)", required=True, tracking=True, help="+ above the card, - below."
    )
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    reason = fields.Text(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("released", "Released"), ("retired", "Retired")],
        default="draft",
        required=True,
        readonly=True,
        index=True,
        tracking=True,
    )
    released_by = fields.Many2one("res.users", readonly=True, copy=False)
    released_at = fields.Datetime(readonly=True, copy=False)

    _TERMS = frozenset(
        {"company_id", "channel", "product_code", "category_id", "adjustment_pct", "valid_from"}
    )

    @api.depends("channel", "product_code", "category_id", "adjustment_pct")
    def _compute_name(self):
        for rec in self:
            scope = rec.product_code or (rec.category_id.name if rec.category_id else "all items")
            rec.name = "%s %+g%% (%s)" % (rec.channel or "?", rec.adjustment_pct or 0.0, scope)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {"state", "released_by", "released_at"}
        if any(rec.state != "draft" for rec in self):
            guarded |= self._TERMS
        return guarded

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Declaring a channel differential")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            require_role(self.env, (ROLE_OFFICER,), "Changing a channel differential")
        return super().write(vals)

    @api.constrains("adjustment_pct", "valid_from", "valid_to")
    def _check_values(self):
        for rec in self:
            if rec.adjustment_pct <= -100:
                raise ValidationError("A differential cannot take the price to zero.")
            if rec.valid_to and rec.valid_to < rec.valid_from:
                raise ValidationError("Validity window is inverted.")

    def _same_scope(self):
        self.ensure_one()
        domain = [
            ("id", "!=", self.id),
            ("state", "=", "released"),
            ("company_id", "=", self.company_id.id),
            ("product_code", "=", self.product_code or False),
            ("category_id", "=", self.category_id.id or False),
            "|",
            ("valid_to", "=", False),
            ("valid_to", ">=", self.valid_from),
        ]
        if self.valid_to:
            domain.append(("valid_from", "<=", self.valid_to))
        return self.sudo().search(domain)

    def _check_spread(self):
        """BRU-PRC-14: the spread between the channels of one scope (the
        channels with no differential sell at the card, 0%) never exceeds the
        configured maximum. Unset maximum: no spread is permitted."""
        limit = _param_float(self.env, SPREAD_PARAM)
        for rec in self:
            others = rec._same_scope()
            if others.filtered(lambda o, ch=rec.channel: o.channel == ch):
                raise UserError(
                    "%s already has a released differential on the %s channel for this scope; "
                    "retire it first." % (rec.product_code or "This scope", rec.channel)
                )
            pcts = [0.0, rec.adjustment_pct, *others.mapped("adjustment_pct")]
            spread = max(pcts) - min(pcts)
            if spread > (limit or 0.0) + 1e-9:
                raise UserError(
                    "The channels of %s would be %.2f%% apart; the permitted maximum spread is "
                    "%s (BRU-PRC-14, %s)."
                    % (
                        rec.product_code or rec.category_id.name or "all items",
                        spread,
                        "%.2f%%" % limit if limit is not None else "not set (no spread allowed)",
                        SPREAD_PARAM,
                    )
                )

    def action_release(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a Draft differential is released.")
            require_releaser_not_author(
                self.env,
                self.env.user,
                self.env.user,
                rec,
                rec.create_uid,
                "Releasing a channel differential",
            )
            rec._check_spread()
            rec._guarded().write(
                {
                    "state": "released",
                    "released_by": self.env.uid,
                    "released_at": fields.Datetime.now(),
                }
            )
        return True

    def action_retire(self):
        require_role(self.env, (ROLE_RELEASER,), "Retiring a channel differential")
        self.filtered(lambda r: r.state == "released")._guarded().write({"state": "retired"})
        return True

    @api.model
    def _for(self, channel, code, item, company, day):
        """The released differential that applies: the item's own, else its
        category's (nearest ancestor), else the all-items one."""
        base = [
            ("state", "=", "released"),
            ("company_id", "=", company.id),
            ("channel", "=", channel),
            ("valid_from", "<=", day),
            "|",
            ("valid_to", "=", False),
            ("valid_to", ">=", day),
        ]
        Diff = self.sudo()
        if code:
            found = Diff.search([*base, ("product_code", "=", code)], limit=1)
            if found:
                return found
        categ = item.category_id if item else None
        while categ:
            found = Diff.search(
                [*base, ("product_code", "=", False), ("category_id", "=", categ.id)], limit=1
            )
            if found:
                return found
            categ = categ.parent_id
        return Diff.search(
            [*base, ("product_code", "=", False), ("category_id", "=", False)], limit=1
        )


# =========================================================================
# FR-PRC-032: the permanent override record
# =========================================================================
class FixPriceOverrideLog(models.Model):
    _name = "fix.price.override.log"
    _description = "Price Override Record"
    _order = "id desc"

    company_id = fields.Many2one("res.company", required=True, index=True)
    res_model = fields.Char(string="Line Model", required=True, index=True)
    res_id = fields.Integer(string="Line ID", required=True, index=True)
    document = fields.Char(required=True)
    product_id = fields.Many2one("product.product", string="Item")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    original_price = fields.Monetary(string="Released Price")
    override_price = fields.Monetary(string="Price Used")
    actor_id = fields.Many2one("res.users", string="By", required=True)
    reason = fields.Text(required=True)
    approval_ref = fields.Char(string="Approval")
    override_id = fields.Many2one("fix.price.override", string="Below-Floor Override")
    at = fields.Datetime(required=True, default=fields.Datetime.now)

    def write(self, vals):
        raise UserError("A price override record is permanent (FR-PRC-032).")

    def unlink(self):
        if not self.env.context.get("_force_unlink"):
            raise UserError("A price override record is permanent (FR-PRC-032).")
        return super().unlink()


# =========================================================================
# AUT-PRC-08..12: the pricing review (re-pricing task)
# =========================================================================
REVIEW_KINDS = [
    ("discontinued", "Item discontinued / superseded"),
    ("srt", "Standard repair time re-baselined"),
    ("cost", "Cost moved: price under the floor / target"),
    ("spread", "Price spread beyond the permitted maximum"),
    ("leakage", "Discount leakage outlier"),
]
REVIEW_STATES = [
    ("open", "Open"),
    ("done", "Disposed"),
    ("accepted", "Accepted"),
    ("rejected", "Rejected"),
]


class FixPriceReview(models.Model):
    """A pricing task raised by an event or a scan, disposed by the Pricing
    Officer (SRT reviews accepted by a Price-Book Releaser)."""

    _name = "fix.price.review"
    _description = "Pricing Review"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, deadline, id desc"

    name = fields.Char(readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    kind = fields.Selection(REVIEW_KINDS, required=True, index=True)
    state = fields.Selection(
        REVIEW_STATES, required=True, default="open", index=True, tracking=True
    )
    rate_card_id = fields.Many2one("fix.rate.card", string="Rate Card", index=True)
    catalogue_item_id = fields.Many2one("fix.catalogue.item", string="Item", index=True)
    successor_item_id = fields.Many2one("fix.catalogue.item", string="Live Successor")
    product_code = fields.Char(index=True)
    baseline_id = fields.Many2one("fix.srt.baseline", string="SRT Baseline", index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Branch")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    current_price = fields.Monetary()
    proposed_price = fields.Monetary(string="Price After the Change")
    floor_price = fields.Monetary()
    cost = fields.Monetary(string="M15 Cost")
    held_minutes = fields.Float(string="Minutes Priced Until Accepted")
    new_minutes = fields.Float(string="Re-Baselined Minutes")
    card_retired = fields.Boolean(string="Rate Retired")
    deadline = fields.Date(string="Decide By")
    detail = fields.Text(required=True)
    event_ref = fields.Char(index=True, copy=False)
    disposition = fields.Text(string="Disposition")
    decided_by = fields.Many2one("res.users", readonly=True, copy=False)
    decided_at = fields.Datetime(readonly=True, copy=False)

    # everything but the disposition note is the system's
    _SYSTEM_FIELDS = frozenset(
        {
            "name",
            "company_id",
            "kind",
            "state",
            "rate_card_id",
            "catalogue_item_id",
            "successor_item_id",
            "product_code",
            "baseline_id",
            "operating_unit_id",
            "currency_id",
            "current_price",
            "proposed_price",
            "floor_price",
            "cost",
            "held_minutes",
            "new_minutes",
            "card_retired",
            "deadline",
            "detail",
            "event_ref",
            "decided_by",
            "decided_at",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self._SYSTEM_FIELDS)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise AccessError("A pricing review is raised by M11's events and scans only.")
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"name": "PRV/%s/%05d" % (rec.create_date.year, rec.id)})
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            require_role(self.env, (ROLE_OFFICER, ROLE_RELEASER), "Working a pricing review")
        return super().write(vals)

    # ---- notify -------------------------------------------------------------
    def _notify_officers(self):
        """An activity for every Pricing Officer (else every releaser) on each
        review; logged when nobody holds the role (M11-F12 is the owner's)."""
        Users = self.env["res.users"].sudo()
        group = self.env.ref(ROLE_OFFICER, raise_if_not_found=False)
        holders = group and Users.search([("group_ids", "in", group.ids), ("share", "=", False)])
        if not holders:
            group = self.env.ref(ROLE_RELEASER, raise_if_not_found=False)
            holders = group and Users.search(
                [("group_ids", "in", group.ids), ("share", "=", False)]
            )
        holders = (holders or Users).filtered(lambda u: u.id != 1)
        for rec in self:
            if not holders:
                _logger.warning("M11 review %s: no Pricing Officer holds the role.", rec.name)
                continue
            for user in holders:
                rec.sudo().activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=rec.deadline or fields.Date.context_today(rec),
                    summary="Pricing review %s: %s" % (rec.name, dict(REVIEW_KINDS)[rec.kind]),
                    note=rec.detail,
                    user_id=user.id,
                )
        return holders

    @api.model
    def _raise(self, vals, notify=True):
        rec = self.sudo()._guarded().create(vals)
        if notify:
            rec._notify_officers()
        return self.browse(rec.ids)

    # ---- dispose ------------------------------------------------------------
    def action_dispose(self, note=None):
        require_role(self.env, (ROLE_OFFICER, ROLE_RELEASER), "Disposing a pricing review")
        note = (note or "").strip()
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open review is disposed.")
            if rec.kind == "srt":
                raise UserError("An SRT review is accepted or rejected by a Price-Book Releaser.")
            text = note or (rec.disposition or "").strip()
            if not text:
                raise UserError("State what was done about it.")
            rec._decide("done", text)
        return True

    def action_accept(self, note=None):
        """AUT-PRC-09: the re-baselined standard time moves the labour price."""
        for rec in self:
            if rec.kind != "srt" or rec.state != "open":
                raise UserError("Only an open SRT review is accepted.")
            base = rec.baseline_id.sudo()
            require_releaser_not_author(
                self.env,
                self.env.user,
                self.env.user,
                rec,
                base.proposed_by | base.approved_by | base.create_uid,
                "Accepting a re-baselined labour price",
            )
            base._release_price_effect()
            rec._decide("accepted", note or rec.disposition or "Accepted")
        return True

    def action_reject(self, note=None):
        """The labour price stays at the previous standard time."""
        require_role(self.env, (ROLE_RELEASER,), "Rejecting a re-baselined labour price")
        if not (note or "").strip():
            raise UserError("State why the new labour price is not taken.")
        for rec in self:
            if rec.kind != "srt" or rec.state != "open":
                raise UserError("Only an open SRT review is rejected.")
            rec._decide("rejected", note)
        return True

    def _decide(self, state, note):
        self.ensure_one()
        self._guarded().write(
            {
                "state": state,
                "disposition": note,
                "decided_by": self.env.uid,
                "decided_at": fields.Datetime.now(),
            }
        )
        self.activity_ids.sudo().action_feedback(feedback=note)
        self.message_post(body="%s by %s: %s" % (state.title(), self.env.user.name, note))

    # ---- AUT-PRC-10 ---------------------------------------------------------
    @api.model
    def _flag_cost(self, card):
        """Open a cost review when the card sits under its floor (or under
        the target margin, when the owner set one). Idempotent per card."""
        card = card.sudo()
        Card = self.env["fix.rate.card"]
        info = Card._floor_info(
            card.catalogue_item_id or card.product_code, company=card.company_id
        )
        price, cost = card.unit_price, info["cost"]
        why = []
        if info["floor"] and price + 0.005 < info["floor"]:
            why.append(
                "the rate %.2f is under the floor %.2f (%s)"
                % (price, info["floor"], info["floor_basis"])
            )
        target = _param_float(self.env, TARGET_MARGIN_PARAM)
        if target is not None and cost and price and (price - cost) / price * 100.0 < target:
            why.append(
                "the margin %.1f%% is under the target %g%%"
                % ((price - cost) / price * 100.0, target)
            )
        if not why:
            return self.browse()
        if self.sudo().search_count(
            [("kind", "=", "cost"), ("rate_card_id", "=", card.id), ("state", "=", "open")]
        ):
            return self.browse()
        return self._raise(
            {
                "kind": "cost",
                "company_id": card.company_id.id,
                "rate_card_id": card.id,
                "catalogue_item_id": card.catalogue_item_id.id or False,
                "product_code": card.product_code,
                "current_price": price,
                "floor_price": info["floor"],
                "cost": cost,
                "deadline": fields.Date.context_today(self) + timedelta(days=7),
                "detail": "%s: M15 cost is now %.2f; %s. Re-price it (AUT-PRC-10)."
                % (card.name, cost, "; ".join(why)),
            }
        )

    @api.model
    def cron_cost_scan(self):
        """AUT-PRC-10, daily: every released unit rate against its floor."""
        cards = (
            self.env["fix.rate.card"]
            .sudo()
            .search([("state", "=", "released"), ("rate_kind", "=", "unit"), ("active", "=", True)])
        )
        return sum(len(self._flag_cost(card)) for card in cards)

    # ---- AUT-PRC-11 / FR-PRC-045 --------------------------------------------
    @api.model
    def cron_consistency_scan(self):
        """AUT-PRC-11, nightly: the same item priced beyond the permitted
        spread across channels (released prices) or branches (sold lines in
        the window). Without a configured spread the scan reports nothing."""
        limit = _param_float(self.env, SPREAD_PARAM)
        if limit is None:
            _logger.warning(
                "M11 consistency scan: %s is not set; nothing is scanned.", SPREAD_PARAM
            )
            return 0
        Card = self.env["fix.rate.card"].sudo()
        raised = 0
        cards = Card.search(
            [
                ("state", "=", "released"),
                ("rate_kind", "=", "unit"),
                ("min_tier", "=", 0),
                ("partner_id", "=", False),
            ]
        )
        for company in cards.mapped("company_id"):
            for code in sorted(
                set(cards.filtered(lambda c, co=company: c.company_id == co).mapped("product_code"))
            ):
                prices = {}
                for channel in SCAN_CHANNELS:
                    res = Card.price_for(code, channel=channel, company=company)
                    if res["price"]:
                        prices[channel] = res["price"]
                if len(prices) < 2:
                    continue
                low, high = min(prices.values()), max(prices.values())
                spread = (high - low) / low * 100.0
                if spread > limit + 1e-9:
                    raised += len(
                        self._flag_spread(
                            company,
                            code,
                            "%s is priced %s across channels: %.1f%% apart, the maximum is %g%%."
                            % (
                                code,
                                ", ".join("%s %.2f" % kv for kv in sorted(prices.items())),
                                spread,
                                limit,
                            ),
                        )
                    )
        raised += self._branch_spread(limit)
        return raised

    @api.model
    def _flag_spread(self, company, code, detail, unit=None):
        if self.sudo().search_count(
            [
                ("kind", "=", "spread"),
                ("company_id", "=", company.id),
                ("product_code", "=", code),
                ("operating_unit_id", "=", unit.id if unit else False),
                ("state", "=", "open"),
            ]
        ):
            return self.browse()
        return self._raise(
            {
                "kind": "spread",
                "company_id": company.id,
                "product_code": code,
                "operating_unit_id": unit.id if unit else False,
                "deadline": fields.Date.context_today(self) + timedelta(days=7),
                "detail": detail,
            }
        )

    @api.model
    def _window_start(self, days_default=30):
        days = _param_float(self.env, WINDOW_PARAM)
        return fields.Datetime.now() - timedelta(days=int(days or days_default))

    @api.model
    def _sold_lines(self, since):
        """[(company, unit, agent, product, list price, net unit price, qty)]
        of M01 estimate lines with a released price, since `since`."""
        Line = self.env.get("fix.estimate.line")
        if Line is None or "card_price" not in Line._fields:
            return []
        out = []
        for line in Line.sudo().search([("card_price", ">", 0), ("create_date", ">=", since)]):
            est = line.estimate_id
            if est.state in ("cancel", "cancelled", "rejected", "declined"):
                continue
            pct = line["discount_pct"] if "discount_pct" in line._fields else 0.0
            net = (line.unit_price or 0.0) * (1.0 - (pct or 0.0) / 100.0)
            out.append(
                (
                    est.company_id,
                    est.operating_unit_id,
                    line.create_uid,
                    line.product_id,
                    line.card_price,
                    net,
                    line.quantity or 0.0,
                )
            )
        return out

    @api.model
    def _branch_spread(self, limit):
        prices = defaultdict(lambda: defaultdict(list))
        for company, unit, _agent, product, _list, net, _qty in self._sold_lines(
            self._window_start()
        ):
            if unit and product:
                prices[(company, product)][unit].append(net)
        raised = 0
        for (company, product), by_unit in prices.items():
            if len(by_unit) < 2:
                continue
            avg = {u: sum(v) / len(v) for u, v in by_unit.items()}
            low, high = min(avg.values()), max(avg.values())
            if low <= 0 or (high - low) / low * 100.0 <= limit + 1e-9:
                continue
            raised += len(
                self._flag_spread(
                    company,
                    product.default_code or product.display_name,
                    "%s sold at %s across branches: %.1f%% apart, the maximum is %g%%."
                    % (
                        product.display_name,
                        ", ".join("%s %.2f" % (u.name, p) for u, p in avg.items()),
                        (high - low) / low * 100.0,
                        limit,
                    ),
                )
            )
        return raised

    # ---- AUT-PRC-12 ---------------------------------------------------------
    @api.model
    def _leakage(self, since):
        """{(company, 'branch'|'agent', record): [list total, realised total]}."""
        out = defaultdict(lambda: [0.0, 0.0])
        for company, unit, agent, _product, card, net, qty in self._sold_lines(since):
            for kind, rec in (("branch", unit), ("agent", agent)):
                if rec:
                    out[(company, kind, rec)][0] += card * qty
                    out[(company, kind, rec)][1] += net * qty
        return out

    @api.model
    def cron_leakage_scan(self):
        """AUT-PRC-12, weekly: realised-vs-released by branch and agent over
        the last 7 days; an outlier past the configured leakage raises a
        review. Without a configured threshold the figures are logged only."""
        threshold = _param_float(self.env, LEAKAGE_PARAM)
        raised = 0
        for (company, kind, rec), (listed, realised) in self._leakage(
            fields.Datetime.now() - timedelta(days=7)
        ).items():
            if listed <= 0:
                continue
            leak = (listed - realised) / listed * 100.0
            _logger.info("M11 leakage %s %s: %.1f%%", kind, rec.display_name, leak)
            if threshold is None or leak <= threshold + 1e-9:
                continue
            raised += len(
                self._raise(
                    {
                        "kind": "leakage",
                        "company_id": company.id,
                        "operating_unit_id": rec.id if kind == "branch" else False,
                        "current_price": realised,
                        "proposed_price": listed,
                        "deadline": fields.Date.context_today(self) + timedelta(days=7),
                        "detail": "%s %s sold at %.1f%% under the released price in the last "
                        "7 days (BDT %.2f realised of %.2f); the alert threshold is %g%%."
                        % (kind.title(), rec.display_name, leak, realised, listed, threshold),
                    }
                )
            )
        return raised


# =========================================================================
# The consumers of the catalogue and stock events
# =========================================================================
class FixM11PricingConsumers(models.AbstractModel):
    _name = "fix.m11.pricing.consumers"
    _description = "M11 Pricing Event Consumers"

    def _record(self, event, model, label):
        if not self.env.su:
            raise AccessError("Pricing consumers run only from the event relay.")
        aggregate = event.get("aggregate")
        if aggregate and aggregate != model:
            raise UserError("%s refused: the aggregate is %s, not %s." % (label, aggregate, model))
        try:
            res_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            res_id = 0
        rec = self.env[model].sudo().browse(res_id).exists() if res_id else None
        if not rec:
            raise UserError("%s refused: there is no %s #%s." % (label, model, res_id))
        return rec

    @api.model
    def _item_cards(self, item, contract_too=True):
        code = (item.sudo().product_tmpl_id.default_code or "").strip()
        domain = [("state", "=", "released"), ("rate_kind", "=", "unit")]
        if code:
            domain += ["|", ("catalogue_item_id", "=", item.id), ("product_code", "=", code)]
        else:
            domain.append(("catalogue_item_id", "=", item.id))
        if not contract_too:
            domain.append(("min_tier", "!=", 99))
        return self.env["fix.rate.card"].sudo().search(domain)

    # ---- AUT-PRC-08 ---------------------------------------------------------
    @api.model
    def consume_item_discontinued(self, event: dict) -> dict:
        """The pricing officer is told about every released rate of the
        discontinued item (and its live successor), then the rates are
        retired. A contract rate stays until the item is obsolete
        (BRU-CAT-10: still serviced under the contract)."""
        label = "Discontinued-item pricing"
        item = self._record(event, "fix.catalogue.item", label)
        if item.state not in ("deprecated", "obsolete"):
            raise UserError("%s refused: %s is not discontinued." % (label, item.display_name))
        Review = self.env["fix.price.review"]
        ref = event.get("event_id") or "item:%d:%s" % (item.id, item.discontinued_at)
        if Review.sudo().search_count([("event_ref", "=", ref)]):
            return {"model": item._name, "id": item.id, "created": False}
        payload = event.get("payload") or {}
        deadline = (
            fields.Date.to_date(payload.get("end_of_support"))
            if payload.get("end_of_support")
            else (item.end_of_support_date or fields.Date.context_today(self))
        )
        live = item.successor_id._fix_live_successor() if item.successor_id else item.browse()
        cards = self._item_cards(item)
        keep = (
            cards.filtered(lambda c: c.min_tier == 99)
            if item.state == "deprecated"
            else cards.browse()
        )
        retire = cards - keep
        reviews = Review.browse()
        for card in cards:
            retired = card in retire
            reviews |= Review._raise(
                {
                    "kind": "discontinued",
                    "company_id": card.company_id.id,
                    "rate_card_id": card.id,
                    "catalogue_item_id": item.id,
                    "successor_item_id": live.id or False,
                    "product_code": card.product_code,
                    "current_price": card.unit_price,
                    "card_retired": retired,
                    "deadline": deadline,
                    "event_ref": ref,
                    "detail": "%s is %s. Rate %s (BDT %.2f) %s.%s"
                    % (
                        item.display_name,
                        dict(item._fields["state"].selection)[item.state],
                        card.name,
                        card.unit_price,
                        "is retired"
                        if retired
                        else "stays for its contract until the item " "is obsolete (BRU-CAT-10)",
                        " Release a rate for its successor %s." % live.display_name if live else "",
                    ),
                },
                notify=False,
            )
        if not cards and live:
            reviews |= Review._raise(
                {
                    "kind": "discontinued",
                    "company_id": item.company_id.id,
                    "catalogue_item_id": item.id,
                    "successor_item_id": live.id,
                    "deadline": deadline,
                    "event_ref": ref,
                    "detail": "%s is discontinued; its successor %s needs its own released rate."
                    % (item.display_name, live.display_name),
                },
                notify=False,
            )
        # the officer is told first, then the rates stop pricing
        reviews._notify_officers()
        for card in retire:
            card._guarded().write({"state": "retired", "active": False})
            card.message_post(
                body="Retired: catalogue item %s was discontinued (AUT-PRC-08)." % item.display_name
            )
        return {
            "model": item._name,
            "id": item.id,
            "created": bool(reviews),
            "retired": len(retire),
        }

    # ---- AUT-PRC-09 ---------------------------------------------------------
    @api.model
    def consume_srt_rebaselined(self, event: dict) -> dict:
        label = "SRT re-baseline pricing"
        base = self._record(event, "fix.srt.baseline", label)
        Review = self.env["fix.price.review"]
        if base.price_effect != "held" or Review.sudo().search_count(
            [("baseline_id", "=", base.id)]
        ):
            return {"model": base._name, "id": base.id, "created": False}
        item = base.item_id.sudo()
        Card = self.env["fix.rate.card"].sudo()
        code = (item.product_tmpl_id.default_code or "").strip()
        if code and Card._resolve(code, company=base.company_id):
            # a fixed rate prices the operation; its standard time moves no price
            base._release_price_effect()
            return {"model": base._name, "id": base.id, "created": False}
        old = float((event.get("payload") or {}).get("old_minutes") or base._previous_minutes())
        new = base.minutes
        rates = Card.search(
            [
                ("rate_kind", "=", "labour_hour"),
                ("state", "=", "released"),
                ("company_id", "=", base.company_id.id),
                ("repair_level", "=", base.repair_level),
            ]
        ).filtered(lambda c: not c.brand_id or c.brand_id == item.brand_id)
        lines = [
            "%s: BDT %.2f -> %.2f"
            % (c.name, money(c.unit_price * old / 60.0), money(c.unit_price * new / 60.0))
            for c in rates
        ]
        default = (
            rates.filtered(
                lambda c: not (c.brand_id or c.skill_band or c.delivery_mode or c.operating_unit_id)
                and c.min_tier == 0
            )[:1]
            or rates[:1]
        )
        review = Review._raise(
            {
                "kind": "srt",
                "company_id": base.company_id.id,
                "catalogue_item_id": item.id,
                "baseline_id": base.id,
                "rate_card_id": default.id or False,
                "held_minutes": old,
                "new_minutes": new,
                "current_price": money(default.unit_price * old / 60.0) if default else 0.0,
                "proposed_price": money(default.unit_price * new / 60.0) if default else 0.0,
                "deadline": fields.Date.context_today(self) + timedelta(days=7),
                "event_ref": event.get("event_id") or False,
                "detail": "The standard time of %s moved from %g to %g min (baseline #%d). "
                "Labour is priced at %g min until a releaser accepts this review "
                "(AUT-PRC-09). Impact: %s"
                % (item.display_name, old, new, base.id, old, "; ".join(lines) or "no labour rate"),
            }
        )
        return {"model": review._name, "id": review.id, "created": True}

    # ---- AUT-PRC-10 ---------------------------------------------------------
    @api.model
    def _cost_moved(self, event, label):
        if not self.env.su:
            raise AccessError("Pricing consumers run only from the event relay.")
        Part = self.env.get("fix.spare.part")
        if Part is None:
            return {"created": False}
        ids = [
            int(line.get("part_id"))
            for line in (event.get("payload") or {}).get("lines") or []
            if line.get("part_id")
        ]
        Review = self.env["fix.price.review"]
        Card = self.env["fix.rate.card"].sudo()
        raised = Review.browse()
        for part in Part.sudo().browse(ids).exists():
            code = (part.product_id.default_code or "").strip()
            if not code:
                continue
            for card in Card.search(
                [
                    ("state", "=", "released"),
                    ("rate_kind", "=", "unit"),
                    ("product_code", "=", code),
                ]
            ):
                raised |= Review._flag_cost(card)
        return {"model": "fix.price.review", "ids": raised.ids, "created": bool(raised)}

    @api.model
    def consume_stock_received(self, event: dict) -> dict:
        return self._cost_moved(event, "Received-stock cost check")

    @api.model
    def consume_stock_adjusted(self, event: dict) -> dict:
        return self._cost_moved(event, "Adjusted-stock cost check")


# =========================================================================
# The catalogue side
# =========================================================================
class FixCatalogueItemPricingUsage(models.Model):
    _inherit = "fix.catalogue.item"

    def _fix_impact_refs(self):
        """FR-CAT-046: also the cards keyed by the item's code, and the
        contracts of its contract rates."""
        out = super()._fix_impact_refs()
        cards = self.env["fix.m11.pricing.consumers"]._item_cards(self)
        if cards:
            out.append(("Rate cards", cards))
        Contract = self.env.get("fix.contract")
        numbers = [n for n in cards.filtered(lambda c: c.min_tier == 99).mapped("contract_no") if n]
        if Contract is not None and numbers and "code" in Contract._fields:
            contracts = (
                Contract.sudo().search([("code", "in", numbers)]).filtered(self._impact_is_open)
            )
            if contracts:
                out.append(("Contracts", contracts))
        return out

    @api.model
    def cron_obsolete_discontinued(self):
        """An item past its end of support becomes Obsolete; then its
        contract rates retire too (BRU-CAT-10 ends there)."""
        today = fields.Date.context_today(self)
        due = self.search(
            [
                ("state", "=", "deprecated"),
                ("end_of_support_date", "!=", False),
                ("end_of_support_date", "<", today),
            ]
        )
        result = super().cron_obsolete_discontinued()
        Consumers = self.env["fix.m11.pricing.consumers"]
        for item in due.filtered(lambda i: i.state == "obsolete"):
            for card in Consumers._item_cards(item):
                card._guarded().write({"state": "retired", "active": False})
                card.message_post(body="Retired: %s is obsolete." % item.display_name)
        return result


class FixSubscriptionPlanDefPricing(models.Model):
    """M37-F5: a subscription created from a plan takes its cycle from the
    plan definition and its price from M11 (channel 'subscription')."""

    _inherit = "fix.subscription.plan.def"

    def _fix_subscription_vals(self, partner=None, company=None, date=None, contract=None):
        """The values cd_subscription sets on a subscription made from this
        plan: {billing_cycle, recurring_amount (VAT-exclusive, per cycle),
        currency_id, commitment_months, plan_def_id, catalogue_item_id,
        price_source, rate_card_id}. Raises when the plan cannot be sold or
        has no released price (no typed amount stands in for it)."""
        self.ensure_one()
        plan = self.sudo()
        if not plan.active:
            raise UserError("Plan %s is archived." % plan.display_name)
        cycle = M39_CYCLES.get(plan.billing_frequency)
        if not cycle:
            raise UserError(
                "Plan %s bills %s; M39 bills monthly, quarterly or annually."
                % (plan.display_name, plan.billing_frequency)
            )
        plan.item_id._fix_assert_sellable("subscription")
        res = self.env["fix.rate.card"].price_for(
            plan.item_id,
            partner=partner,
            channel="subscription",
            date=date,
            company=company or plan.company_id,
            contract=contract,
        )
        if res["price"] is None:
            raise UserError(
                "Plan %s has no released M11 price: %s." % (plan.display_name, res["reason"])
            )
        return {
            "billing_cycle": cycle,
            "recurring_amount": res["price"],
            "currency_id": res["currency_id"],
            "commitment_months": plan.commitment_months,
            "plan_def_id": plan.id,
            "catalogue_item_id": plan.item_id.id,
            "price_source": res["source"],
            "rate_card_id": res["card_id"],
        }

    @api.model
    def _fix_for_item(self, item):
        return self.sudo().search([("item_id", "=", item.id), ("active", "=", True)], limit=1)
