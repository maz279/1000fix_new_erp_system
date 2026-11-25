# The M11 price service (A04 ERP audit, 20 Nov 2026, M11-F1..F10).
#
# fix_real had no released price at all, every stocked item carried the
# list_price placeholder 1.00, and the documents that sell either typed their
# own price (M01 estimate, M38, M12, M08, M39) or fell back to that list price
# (M36). A real order was priced at BDT 1.00 and the floor passed it.
#
# This file is the ONE place a selling document asks what an item costs and
# whether a price is allowed:
#
#   fix.rate.card.price_for(product, partner, channel, qty, date, company,
#                           contract, currency)       -> the released price
#   fix.rate.card.check_sale_price(product, unit_price, channel, ...)
#                                                     -> the floor gate
#
# No released price means no price (None), never list_price. The floor is the
# higher of the M11 price floors and the M15 average cost plus the margin
# floor; below it a sale needs a below-floor override (fix.price.override)
# approved for THAT document line, used once, before it expires.
import logging
from datetime import timedelta

from odoo import SUPERUSER_ID, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_pricing_ops import DOFA_TIER_GROUP, DOFA_TIERS, FixPriceFloor
from .pricing_money import money
from .pricing_roles import ROLE_OFFICER, require_role

_logger = logging.getLogger(__name__)

# The margin a sale must keep over its M15 average cost, in percent
# (FR-PRC-028). The business sets it; until then 0 = never below cost.
MARGIN_FLOOR_PARAM = "cd_rate_card.margin_floor_pct"

# Channels a customer buys on without a salesperson: a line with no released
# price is refused there (no typed price stands in for it).
CUSTOMER_CHANNELS = frozenset({"storefront", "marketplace"})
# The names callers already use for a channel, mapped to the service's own.
CHANNEL_ALIASES = {"estimate": "service", "web": "storefront", "order": "service"}
# fix.promotion.channel speaks of portal / branch / corporate.
PROMOTION_CHANNEL = {
    "storefront": "portal",
    "marketplace": "portal",
    "service": "branch",
    "quotation": "branch",
    "contract": "corporate",
    "subscription": "corporate",
    "reseller": "corporate",
}
# Item types priced by a released parts scheme on M15 cost when no rate card
# names them (FR-PRC-013).
PART_ITEM_TYPES = ("part", "accessory", "finished_good")
# Item types a technician performs: with no fixed rate they are priced at a
# labour rate x their standard repair time (FR-PRC-012).
LABOUR_ITEM_TYPES = ("labour", "service", "inspection")
# Transaction-scoped one-shot pass: an estimate line that cleared the floor
# with its own bound override lets the line-less re-check that follows it
# (product._fix_check_sale) through once. See check_sale_price.
_CLEARED_KEY = "fix_m11_floor_cleared"


def _channel(channel):
    channel = (channel or "quotation").strip().lower()
    return CHANNEL_ALIASES.get(channel, channel)


class ResPartnerPriceTier(models.Model):
    """M11-F3: where a customer's price tier lives. A rate card of tier N
    prices every customer whose tier is N or more; tier 0 is everyone."""

    _inherit = "res.partner"

    fix_price_tier = fields.Integer(
        string="Price Tier (M11)",
        default=0,
        help="The M11 rate-card tier this customer is priced at (0 = standard). Set by a "
        "Pricing Officer.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        if any(v.get("fix_price_tier") for v in vals_list):
            require_role(self.env, (ROLE_OFFICER,), "Setting a customer's price tier")
        return super().create(vals_list)

    def write(self, vals):
        if "fix_price_tier" in vals and any(
            (p.fix_price_tier or 0) != int(vals["fix_price_tier"] or 0) for p in self
        ):
            require_role(self.env, (ROLE_OFFICER,), "Changing a customer's price tier")
            if set(vals) == {"fix_price_tier"} and not self.env.su:
                # the role is the gate for this one pricing field; a Pricing
                # Officer need not hold the contact-editing groups
                return super(ResPartnerPriceTier, self.sudo()).write(vals)
        return super().write(vals)


class FixRateCardPriceService(models.Model):
    _inherit = "fix.rate.card"

    # ------------------------------------------------------------------ inputs
    @api.model
    def _price_target(self, product):
        """(product.product, code, fix.catalogue.item) for any of the inputs
        price_for accepts: a variant, a template, a catalogue item or a code."""
        Product = self.env["product.product"].sudo()
        Item = self.env["fix.catalogue.item"].sudo()
        variant, item, code = Product.browse(), Item.browse(), ""
        if isinstance(product, str):
            code = product.strip()
            if code:
                variant = Product.search([("default_code", "=", code)], limit=1)
        elif product:
            if product._name == "product.product":
                variant = Product.browse(product[:1].id)
            elif product._name == "product.template":
                variant = product.sudo()[:1].product_variant_id
            elif product._name == "fix.catalogue.item":
                item = Item.browse(product[:1].id)
                variant = item.product_tmpl_id.product_variant_id
        if variant:
            code = code or (variant.default_code or "").strip()
            item = item or variant.product_tmpl_id.catalogue_item_id[:1]
        elif item:
            code = code or (item.product_tmpl_id.default_code or "").strip()
        return variant, code, item

    @api.model
    def _m15_cost(self, variant, company=None):
        """The M15 average cost of the part behind `variant` (the weighted
        average of its owned ledger, else its standard cost), or 0.0 when M15
        holds no cost for it. product.standard_price is empty on fix_real and
        is never read (M11-F18)."""
        Part = self.env.get("fix.spare.part")
        if Part is None or not variant:
            return 0.0
        domain = [("product_id", "=", variant.id)]
        if company:
            domain.append(("company_id", "in", [company.id, False]))
        part = Part.sudo().with_context(active_test=False).search(domain, limit=1)
        if not part:
            return 0.0
        return float(part.average_cost or part.unit_cost or 0.0)

    @api.model
    def _margin_floor_pct(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(MARGIN_FLOOR_PARAM, "0")
        try:
            return max(float(raw or 0.0), 0.0)
        except (TypeError, ValueError):
            _logger.warning("%s is not a number (%r); 0 is used.", MARGIN_FLOOR_PARAM, raw)
            return 0.0

    @api.model
    def _floor_info(self, product, company=None, cost=None):
        """{floor, floor_basis, price_floor, cost_floor, cost} for `product`:
        the floor is the higher of the active M11 price floors on its code
        or catalogue item (this company's or shared) and its M15 cost plus
        the margin floor (M11-F9, FR-PRC-028)."""
        company = company or self.env.company
        variant, code, item = self._price_target(product)
        floors = self.env["fix.price.floor"]._floors_matching(code, item, company)
        price_floor = max(floors.mapped("floor_price") or [0.0])
        if cost is None:
            cost = self._m15_cost(variant, company)
        pct = self._margin_floor_pct()
        cost_floor = money(cost * (1.0 + pct / 100.0)) if cost else 0.0
        floor = max(price_floor, cost_floor)
        if not floor:
            basis = "no floor"
        elif cost_floor >= price_floor:
            basis = "M15 cost %.2f + %g%% margin floor" % (cost, pct)
        else:
            basis = "M11 price floor"
        return {
            "floor": floor,
            "floor_basis": basis,
            "price_floor": price_floor,
            "cost_floor": cost_floor,
            "cost": float(cost or 0.0),
        }

    @api.model
    def _vat_rate(self, company, day):
        """The standard VAT rate in force (M51 Tax Rate Master), or None when
        no master answers. Prices here are VAT-EXCLUSIVE (M11-F15)."""
        Rate = self.env.get("fix.tax.rate")
        if Rate is None or not hasattr(Rate, "_fix_vat_rates"):
            return None
        try:
            return float(Rate._fix_vat_rates(day, company).standard)
        except (UserError, ValidationError, AttributeError):
            return None

    @api.model
    def _vat_rate_for(self, item, company, day):
        """M11-F15: the VAT rate of the item's M37 VAT class. Exempt and
        zero-rated items carry none; a reduced or truncated item's rate is the
        M51 determination's on the invoice (None here); otherwise the
        standard rate in force."""
        vat_class = item.vat_class if item and "vat_class" in item._fields else False
        if vat_class in ("exempt", "zero_rated"):
            return 0.0
        if vat_class in ("reduced", "truncated"):
            return None
        return self._vat_rate(company, day)

    # ------------------------------------------------- FR-PRC-012 labour
    @api.model
    def _srt_for_pricing(self, item, day, device_model=None, level=None):
        """(minutes, baseline, held) the labour price of `item` is computed
        on: the newest applied SRT baseline of the device model (else the
        general one), else the item's standard labour time. A re-baseline
        M11 has not accepted yet prices at the time it replaced (AUT-PRC-09)."""
        Baseline = self.env["fix.srt.baseline"].sudo()
        domain = [
            ("item_id", "=", item.id),
            ("applied_at", "!=", False),
            ("state", "in", ("approved", "superseded")),
            ("effective_from", "<=", day),
        ]
        if level:
            domain.append(("repair_level", "=", level))
        found = Baseline.browse()
        for model in ([device_model] if device_model else []) + [False]:
            found = Baseline.search(
                [*domain, ("device_model_id", "=", model.id if model else False)],
                order="effective_from desc, id desc",
                limit=1,
            )
            if found:
                break
        if not found:
            return float(item.standard_labour_time or 0.0) * 60.0, None, False
        if found.price_effect == "held":
            return found._previous_minutes(), found, True
        return float(found.minutes), found, False

    @api.model
    def _labour_rate_card(self, item, level, tier, contract_no, day, company, currency, facts):
        """The released labour rate that fits the job most closely: the
        contract lane first, then the most specific match on brand, skill
        band, delivery mode and branch, then the highest tier reached."""
        domain = [
            ("rate_kind", "=", "labour_hour"),
            ("state", "=", "released"),
            ("company_id", "=", company.id),
            ("repair_level", "=", level),
            "|",
            ("valid_from", "=", False),
            ("valid_from", "<=", day),
            "|",
            ("valid_to", "=", False),
            ("valid_to", ">=", day),
        ]
        if currency:
            domain.append(("currency_id", "=", currency.id))
        unit = facts.get("operating_unit")
        unit_id = unit.id if hasattr(unit, "id") else (int(unit) if unit else 0)
        band = facts.get("skill_band") or item.required_skill_band
        mode = facts.get("delivery_mode")

        def fits(c):
            if c.brand_id and c.brand_id != item.brand_id:
                return False
            if c.skill_band and c.skill_band != band:
                return False
            if c.delivery_mode and c.delivery_mode != mode:
                return False
            if c.operating_unit_id and c.operating_unit_id.id != unit_id:
                return False
            if c.min_tier == 99:
                return bool(contract_no) and c.contract_no == contract_no
            return c.min_tier <= int(tier or 0)

        cards = self.sudo().search(domain).filtered(lambda c: fits(c) and c._version_in_force(day))
        if not cards:
            return cards

        def key(c):
            specific = sum(
                bool(x) for x in (c.brand_id, c.skill_band, c.delivery_mode, c.operating_unit_id)
            )
            return (c.min_tier == 99, specific, c.min_tier, c.valid_from or day.min, c.id)

        return max(cards, key=key)

    @api.model
    def _labour_price(self, item, tier, contract_no, day, company, currency, facts):
        level = facts.get("repair_level") or item.repair_level
        if not level:
            return None
        model = facts.get("device_model")
        if model and not hasattr(model, "id"):
            model = self.env["fix.device.model"].browse(int(model)).exists()
        minutes, baseline, held = self._srt_for_pricing(item, day, model or None, level)
        if not minutes or minutes <= 0:
            return None
        card = self._labour_rate_card(item, level, tier, contract_no, day, company, currency, facts)
        if not card:
            return None
        return {
            "price": money(card.unit_price * minutes / 60.0),
            "card": card,
            "rate": card.unit_price,
            "minutes": minutes,
            "baseline_id": baseline.id if baseline else False,
            "held": held,
        }

    # --------------------------------------------------------------- the price
    @api.model
    def price_for(
        self,
        product,
        partner=None,
        channel="quotation",
        qty=1.0,
        date=None,
        company=None,
        contract=None,
        currency=None,
        premiums=None,
        facts=None,
    ):
        """THE M11 price of one unit of `product` (BRU-PRC-01).

        Args:
            product: product.product | product.template | fix.catalogue.item
                | str (the item / charge code).
            partner: res.partner, the customer. Its commercial entity's own
                rate (the customer lane) and its M11 price tier
                (res.partner.fix_price_tier) are read from it.
            channel: 'service' (M01; 'estimate' is accepted), 'quotation'
                (M36), 'storefront' (M38), 'marketplace' (M12), 'contract'
                (M08), 'subscription' (M39), 'reseller' (M40).
            qty: the quantity (informational: rates are per unit).
            date: the DOCUMENT date the price is effective on (default: today,
                Asia/Dhaka).
            company: res.company (default: the current company). Only this
                company's cards, floors, schemes, promotions price it.
            contract: fix.contract or its code: the contract lane.
            currency: res.currency (default BDT). Only cards in it price.
            premiums: optional adjustment kinds that apply to the job
                (express, emergency, after_hours, weekend, holiday, zone,
                distance), with `facts` (distance_km, hour, operating_unit).

        Precedence: the contract card, else the customer's card, else the
        highest tier card the customer reaches, else the standard (tier 0)
        card; for a spare part with no card, the released parts scheme on
        its M15 cost. Then the declared premiums are added, the best active
        promotion is taken off, and (storefront / marketplace) an active
        dynamic rule moves it inside the corridor. A promotion or a dynamic
        rule never takes a price below the floor (it stops at the floor).

        Returns a dict:
            price       float | None  VAT-exclusive unit price; None = no
                                      released price (never list_price)
            list_price  float | None  the released price before promotions
                                      and dynamic rules: the base an off-list
                                      discount is measured from (FR-PRC-031)
            source      str           'contract' | 'customer' | 'tier' |
                                      'card' | 'parts_scheme' | 'none'
            card_id     int | False   the fix.rate.card used
            floor       float         the minimum unit price (price floor /
                                      M15 cost margin floor)
            floor_basis str
            cost        float         M15 average cost, 0.0 when unknown
            reason      str           why price is None ('' otherwise)
            promotions  [codes], promotion_discount float, premiums
                        [{code, amount}], dynamic_rule_id int | False,
            currency_id int, vat_basis 'exclusive', vat_rate float | None,
            vat_class   the catalogue item's VAT class (M37) or False
        """
        channel = _channel(channel)
        company = company or self.env.company
        currency = currency or self.env.ref("base.BDT", raise_if_not_found=False)
        day = fields.Date.to_date(date) if date else fields.Date.context_today(self)
        variant, code, item = self._price_target(product)
        cost = self._m15_cost(variant, company)
        floor = self._floor_info(variant or item or code, company=company, cost=cost)
        result = {
            "price": None,
            "list_price": None,
            "source": "none",
            "card_id": False,
            "floor": floor["floor"],
            "floor_basis": floor["floor_basis"],
            "cost": floor["cost"],
            "reason": "",
            "promotions": [],
            "promotion_discount": 0.0,
            "premiums": [],
            "dynamic_rule_id": False,
            "currency_id": currency.id if currency else False,
            "vat_basis": "exclusive",
            "vat_rate": self._vat_rate_for(item, company, day),
            "price_incl": None,
            "vat_class": item.vat_class if item and "vat_class" in item._fields else False,
            "qty": float(qty or 0.0),
        }
        if not code and not variant:
            result["reason"] = "no item to price"
            return result
        contract_no = None
        if contract:
            contract_no = contract if isinstance(contract, str) else contract.sudo().code
        tier = partner.commercial_partner_id.sudo().fix_price_tier if partner else 0
        card = self._resolve(
            code,
            tier=tier,
            contract_no=contract_no,
            on_date=day,
            company=company,
            partner=partner,
            currency=currency,
        )
        facts = dict(facts or {})
        # A04 ERP round 2 M37-F7: a closed item names the item sold instead
        if (
            item
            and item.state in ("deprecated", "obsolete")
            and hasattr(item, "_fix_sale_substitute")
        ):
            result["successor_item_id"] = item._fix_sale_substitute(channel).id or False
        price = None
        labour = None
        if card:
            price = card.unit_price
            result["card_id"] = card.id
            if card.min_tier == 99:
                result["source"] = "contract"
            elif card.partner_id:
                result["source"] = "customer"
            elif card.min_tier > 0:
                result["source"] = "tier"
            else:
                result["source"] = "card"
            # FR-PRC-017: quantity / value / committed-volume breaks
            broke, used = card._apply_breaks(price, qty, facts)
            if used:
                price = broke
                result["price_breaks"] = used.ids
        elif item and item.item_type in LABOUR_ITEM_TYPES:
            # FR-PRC-012: a labour line with no fixed rate = labour rate x SRT
            labour = self._labour_price(item, tier, contract_no, day, company, currency, facts)
            if labour:
                price = labour["price"]
                result.update(
                    source="labour_rate",
                    card_id=labour["card"].id,
                    labour_rate=labour["rate"],
                    srt_minutes=labour["minutes"],
                    srt_held=labour["held"],
                )
        if price is None and not card and item and item.item_type in PART_ITEM_TYPES and cost > 0:
            price = self._scheme_price(item, variant, cost, day, company)
            if price is not None:
                result["source"] = "parts_scheme"
        if price is None:
            result["reason"] = (
                "no released M11 price for %s on %s (no rate card of company %s in %s, no "
                "labour rate for its standard repair time, and no parts scheme)"
                % (
                    code or variant.display_name,
                    day,
                    company.name,
                    currency.name if currency else "",
                )
            )
            return result
        price = money(price)
        priced_card = card or (labour["card"] if labour else None)
        line_type = priced_card.line_type if priced_card else "part"
        # FR-PRC-020: the declared channel differential (never on a contract
        # rate: BRU-PRC-11, the contract's price overrides every other book)
        if result["source"] != "contract":
            diff = self.env["fix.channel.differential"]._for(channel, code, item, company, day)
            if diff:
                price = money(price * (1.0 + diff.adjustment_pct / 100.0))
                result["channel_differential_id"] = diff.id
        if premiums:
            premium_facts = {
                k: facts[k] for k in ("distance_km", "hour", "operating_unit") if k in facts
            }
            lines = self.env["fix.price.adjustment"].premiums_for(
                premiums, price, on_date=day, company=company, line_type=line_type, **premium_facts
            )
            result["premiums"] = [{"code": p.code, "amount": amount} for p, amount in lines]
            price = money(price + sum(a for _p, a in lines))
        result["list_price"] = price
        Promo = self.env["fix.promotion"].sudo()
        promos = Promo.search([("state", "=", "active"), ("company_id", "=", company.id)])
        if promos:
            used, discount = Promo.best_combination(
                promos, price, channel=PROMOTION_CHANNEL.get(channel), product_code=code
            )
            if discount > 0:
                result["promotions"] = used.mapped("code")
                result["promotion_discount"] = discount
                price = money(price - discount)
        price, rule = self._price_for_dynamic(price, card, channel, company, code)
        if rule:
            result["dynamic_rule_id"] = rule.id
        # a promotion or a dynamic rule never takes the price under the floor
        if price + 0.005 < floor["floor"] <= result["list_price"] + 0.005:
            price = floor["floor"]
            result["floor_clamped"] = True
        result["price"] = money(price)
        # FR-PRC-009 / M11-F15: both figures, the inclusive one on the M51 rate
        # of the item's VAT class (None when M51 decides it on the invoice)
        if result["vat_rate"] is not None:
            result["price_incl"] = money(result["price"] * (1.0 + result["vat_rate"] / 100.0))
        return result

    @api.model
    def _scheme_price(self, item, variant, cost, day, company):
        Scheme = self.env["fix.parts.price.scheme"]
        scheme = Scheme.scheme_for(
            category=item.category_id or variant.categ_id,
            brand=item.brand_id,
            grade=item.provenance_grade,
            on_date=day,
            company=company,
        )
        if not scheme:
            return None
        try:
            return scheme.price_for(cost, item.provenance_grade)
        except UserError:
            return None

    def _price_for_dynamic(self, price, card, channel, company, code):
        """Hook for cd_dynamic_pricing: (price, rule) after the dynamic rule
        of the channel, inside the corridor. No rule here."""
        return price, None

    # --------------------------------------------------------------- the gate
    @api.model
    def check_sale_price(
        self,
        product,
        unit_price,
        channel,
        partner=None,
        date=None,
        company=None,
        override=None,
        line=None,
    ):
        """The floor gate every selling document runs (BRU-PRC-04).

        Raises UserError when
          - the channel faces the customer (storefront / marketplace) and
            price_for has no released price for the item; or
          - `unit_price` is below the floor (M11 price floor / M15 cost margin
            floor, see _floor_info) and no approved below-floor override is
            bound to this document line.

        The override is a fix.price.override approved for the line: pass it as
        `override`, or pass the document line as `line` (or as `override`) and
        it is looked up. It covers that line only, at or above the price it was
        approved for; it is used once (consumed on first use; the same line may
        be re-checked at that price) and lapses unused at its expiry date.

        Returns the floor info dict (floor, floor_basis, cost, ...).
        """
        channel = _channel(channel)
        company = company or self.env.company
        variant, code, item = self._price_target(product)
        if channel in CUSTOMER_CHANNELS:
            res = self.price_for(
                variant or item or code,
                partner=partner,
                channel=channel,
                date=date,
                company=company,
            )
            if res["price"] is None:
                raise UserError(
                    "Cannot sell %s on the %s channel: %s. A customer channel sells only at a "
                    "released price (M11)." % (code or variant.display_name, channel, res["reason"])
                )
        info = self._floor_info(variant or item or code, company=company)
        if unit_price is None:
            return info
        price = float(unit_price or 0.0)
        if not info["floor"] or price + 0.005 >= info["floor"]:
            return info
        Override = self.env["fix.price.override"].sudo()
        if override is not None and override and override._name != "fix.price.override":
            line, override = override, None
        if not override and line:
            override = Override._bound_to(line)
        if override:
            first_use = override.sudo().state == "approved"
            override.sudo()._use_for(line, variant, price)
            if first_use and line:
                # FR-PRC-032: the permanent record of the approved override
                listed = self.price_for(
                    variant or item or code,
                    partner=partner,
                    channel=channel,
                    date=date,
                    company=company,
                )["list_price"]
                self.record_override(
                    line,
                    listed if listed is not None else info["floor"],
                    price,
                    "Below-floor price approved by override %s" % override.sudo().name,
                    approval=override.sudo(),
                    product=variant,
                )
            if line:
                cleared = self.env.cr.precommit.data.setdefault(_CLEARED_KEY, set())
                cleared.add((variant.id, channel, money(price)))
            return info
        cleared = self.env.cr.precommit.data.get(_CLEARED_KEY) or set()
        token = (variant.id, channel, money(price))
        if token in cleared:
            cleared.discard(token)
            return info
        raise UserError(
            "%s cannot be sold at BDT %.2f: the floor is BDT %.2f (%s). A lower price needs "
            "a below-floor override approved for this document line (BRU-PRC-04)."
            % (code or variant.display_name, price, info["floor"], info["floor_basis"])
        )

    # ------------------------------------------------------- M09 brand rates
    @api.model
    def rate_for(self, brand, repair_level="l1", on_date=None, company=None):
        """M11-F10: the released brand reimbursement rate (FR-PRC-015) a
        warranty job of `brand` at `repair_level` is valued at on its service
        date. Empty recordset when the brand has none. For M09."""
        return self.env["fix.brand.reimbursement.rate"].rate_for(
            brand, repair_level=repair_level, on_date=on_date, company=company
        )

    @api.model
    def reimbursement_for(
        self, brand, repair_level="l1", parts_cost=0.0, on_date=None, company=None
    ):
        """What `brand` owes for one warranty job: {amount, rate_id, labour,
        parts_markup_pct}; amount None when no released rate exists (M09 then
        claims nothing it cannot price)."""
        rate = self.rate_for(brand, repair_level, on_date=on_date, company=company)
        if not rate:
            return {"amount": None, "rate_id": False, "labour": 0.0, "parts_markup_pct": 0.0}
        return {
            "amount": rate.reimbursement_for(parts_cost),
            "rate_id": rate.id,
            "labour": rate.labour_rate,
            "parts_markup_pct": rate.parts_markup_pct,
        }

    # ---------------------------------------------------- effective dating
    def _supersede_price(self, new_price, effective_from):
        """M11-F4: a released card's price changes as a NEW version from
        `effective_from`; this one keeps its window up to the day before, so a
        document dated earlier is still priced at the old rate. A change
        effective on or before the card's own start replaces it in place.
        Returns the card that carries the new price."""
        self.ensure_one()
        start = self.valid_from
        if not effective_from or (start and effective_from <= start):
            self._guarded().write({"unit_price": new_price})
            return self
        if self.valid_to and effective_from > self.valid_to:
            raise UserError(
                "%s ends on %s; a change from %s is a new rate, not a change of this one."
                % (self.name, self.valid_to, effective_from)
            )
        old_end = self.valid_to
        self._guarded().write({"valid_to": effective_from - timedelta(days=1)})
        vals = {
            "product_code": self.product_code,
            "line_type": self.line_type,
            "currency_id": self.currency_id.id,
            "unit_price": new_price,
            "catalogue_item_id": self.catalogue_item_id.id or False,
            "min_tier": self.min_tier,
            "contract_no": self.contract_no or False,
            "valid_from": effective_from,
            "valid_to": old_end or False,
            "company_id": self.company_id.id,
            "partner_id": self.partner_id.id or False,
            "version_id": self.version_id.id or False,
        }
        if "contract_id" in self._fields:
            vals["contract_id"] = self.contract_id.id or False
        new = self.sudo().with_context(fix_card_successor=True).create(vals)
        new._guarded().write(
            {
                "state": "released",
                "released_by": self.env.uid,
                "released_at": fields.Datetime.now(),
            }
        )
        return self.browse(new.ids)


class FixPriceChangeDating(models.Model):
    """M11-F4/F8/F20 on the one way a live rate changes."""

    _inherit = "fix.price.change"

    effective_from = fields.Date(
        string="Effective From",
        default=fields.Date.context_today,
        help="A rate change takes effect from this date as a new version of the rate; "
        "documents dated earlier keep the old rate.",
    )
    new_rate_card_id = fields.Many2one("fix.rate.card", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {"new_rate_card_id"}
        if any(rec.state != "draft" for rec in self):
            guarded |= {"effective_from"}
        return guarded

    def _validate(self):
        super()._validate()
        target = self._target().sudo()
        if self.target_type != "rate_card":
            return
        if self.change_type in ("release", "change"):
            # M11-F8: a rate is never set below its floor.
            target._assert_not_below_floor(self.proposed_value)
        if self.change_type == "release" and target.rate_kind != "labour_hour":
            # M11-F20: a card is released for an item that exists and sells
            # (a labour rate per hour names a repair level, not an item).
            Product = self.env["product.product"].sudo()
            product = Product.search([("default_code", "=", target.product_code)], limit=1)
            if not product:
                raise UserError(
                    "No item or charge code %s exists: a rate is released for a real code."
                    % target.product_code
                )
            item = target.catalogue_item_id or product.product_tmpl_id.catalogue_item_id[:1]
            item = item.sudo()
            if item and item.state not in ("approved", "published", "restricted"):
                raise UserError(
                    "Catalogue item %s is %s: a rate is released only for an Active item "
                    "(BRU-CAT-14)."
                    % (item.display_name, dict(item._fields["state"].selection)[item.state])
                )

    def action_apply(self):
        """The 'change' of a released rate becomes a new dated version
        (M11-F4) instead of overwriting the price in place."""
        dated = self.filtered(
            lambda r: r.state == "pending"
            and r.target_type == "rate_card"
            and r.change_type == "change"
        )
        if not dated:
            return super().action_apply()
        rest = self - dated
        if rest:
            super(FixPriceChangeDating, rest).action_apply()
        for rec in dated:
            card = rec.rate_card_id.sudo()
            old_start, old_price = card.valid_from, card.unit_price
            # the parent applies the change in place (and runs every check:
            # routing, releaser != author, unchanged target); then the dated
            # version is split off when the change starts after the card did
            super(FixPriceChangeDating, rec).action_apply()
            eff = rec.effective_from
            if eff and (not old_start or eff > old_start):
                card._guarded().write({"unit_price": old_price})
                new = card._supersede_price(rec.proposed_value, eff)
                rec._guarded().write({"new_rate_card_id": new.id})
        return True


class FixPriceOverride(models.Model):
    """A below-floor price for ONE document line (M11-F7).

    The floor's own DOFA override was a standing permission: once approved,
    600 on the storefront, 650 by another user and 600 on a quotation all
    passed, with no expiry and no document. An override is now requested for
    a named document line at a named price, approved through M63 by a holder
    of the tier the depth below the floor derives (the person who asked never
    approves it), used once by that line, and lapses unused at its expiry."""

    _name = "fix.price.override"
    _description = "Below-Floor Price Override"
    _inherit = ["mail.thread", "fix.dofa.mixin"]
    _order = "id desc"

    _DOFA_DISCOUNT_THRESHOLDS = FixPriceFloor._DOFA_DISCOUNT_THRESHOLDS
    _approval_domain = "pricing_floor_override"
    _approval_apply_method = "action_approve_dofa_override"
    _approval_routed = True

    name = fields.Char(readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # The one document line the price is for: an M01 estimate line by name,
    # any other selling line (quotation, storefront order, listing) by its
    # model and id.
    estimate_line_id = fields.Many2one(
        "fix.estimate.line", string="Estimate Line", index=True, ondelete="cascade"
    )
    res_model = fields.Selection(
        selection="_line_models",
        string="Document Line Type",
        compute="_compute_res",
        store=True,
        readonly=False,
        index=True,
    )
    res_id = fields.Integer(
        string="Document Line ID", compute="_compute_res", store=True, readonly=False, index=True
    )
    product_id = fields.Many2one("product.product", string="Item", required=True)
    requested_price = fields.Monetary(string="Requested Unit Price", required=True)
    floor_price = fields.Monetary(string="Floor When Requested", readonly=True)
    floor_basis = fields.Char(readonly=True)
    cost = fields.Monetary(string="M15 Cost When Requested", readonly=True)
    valid_until = fields.Date(
        string="Use By",
        required=True,
        help="The override lapses if the line has not used it by this date.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Awaiting Approval"),
            ("approved", "Approved"),
            ("consumed", "Used"),
            ("expired", "Expired"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
        readonly=True,
        index=True,
        tracking=True,
    )
    consumed_at = fields.Datetime(readonly=True, copy=False)
    consumed_by = fields.Many2one("res.users", readonly=True, copy=False)

    _TERMS = frozenset(
        {
            "estimate_line_id",
            "res_model",
            "res_id",
            "product_id",
            "requested_price",
            "company_id",
            "currency_id",
        }
    )

    @api.model
    def _line_models(self):
        return [
            ("fix.estimate.line", "Estimate line"),
            ("fix.quotation.line", "Quotation line"),
            ("fix.storefront.order.line", "Storefront order line"),
            ("fix.marketplace.listing", "Marketplace listing"),
        ]

    @api.depends("estimate_line_id")
    def _compute_res(self):
        for rec in self:
            if rec.estimate_line_id:
                rec.res_model = "fix.estimate.line"
                rec.res_id = rec.estimate_line_id.id
            else:
                rec.res_model = rec.res_model or False
                rec.res_id = rec.res_id or 0

    def _line(self):
        """The document line this override names (empty when it is gone)."""
        self.ensure_one()
        if not self.res_model or self.res_model not in self.env or not self.res_id:
            return None
        return self.env[self.res_model].sudo().browse(self.res_id).exists()

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "state",
            "floor_price",
            "floor_basis",
            "cost",
            "consumed_at",
            "consumed_by",
            "name",
        }
        if any(rec.state != "draft" for rec in self):
            guarded |= self._TERMS | {"valid_until"}
        return guarded

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | set(self._TERMS)

    # ---- DOFA ----------------------------------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        if not self.floor_price or not self.requested_price:
            return 0.0
        short = self.floor_price - self.requested_price
        return (short / self.floor_price) * 100.0 if short > 0 else 0.0

    def _dofa_thresholds(self):
        return self._DOFA_DISCOUNT_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "a price %.1f%% below the floor of %s" % (
            self._dofa_amount(),
            self.product_id.display_name or "",
        )

    @api.depends("floor_price", "requested_price")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    # ---- create / write ------------------------------------------------------
    def _snapshot(self):
        Card = self.env["fix.rate.card"]
        for rec in self:
            info = Card._floor_info(rec.product_id, company=rec.company_id)
            if not info["floor"] or rec.requested_price + 0.005 >= info["floor"]:
                raise UserError(
                    "BDT %.2f is not below the floor of %s (BDT %.2f): no override is needed."
                    % (rec.requested_price, rec.product_id.display_name, info["floor"])
                )
            if rec.requested_price <= 0:
                raise UserError("An override names a positive price.")
            if rec.valid_until < fields.Date.context_today(rec):
                raise UserError("The use-by date of an override cannot be in the past.")
            line = rec._line()
            if not line:
                raise UserError(
                    "Name the document line the below-floor price is for: an override covers "
                    "one line only."
                )
            line_product = line["product_id"] if "product_id" in line._fields else None
            if line_product and line_product != rec.product_id:
                raise UserError("The override's item is not the item on that document line.")
            rec._guarded().write(
                {
                    "floor_price": info["floor"],
                    "floor_basis": info["floor_basis"],
                    "cost": info["cost"],
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            model = "fix.estimate.line" if vals.get("estimate_line_id") else vals.get("res_model")
            rid = vals.get("estimate_line_id") or vals.get("res_id")
            if not vals.get("product_id") and model in self.env and rid:
                line = self.env[model].sudo().browse(int(rid)).exists()
                if line and "product_id" in line._fields:
                    vals["product_id"] = line.product_id.id
        records = super().create(vals_list)
        records._snapshot()
        for rec in records:
            rec._guarded().write({"name": "PFO/%s/%05d" % (rec.create_date.year, rec.id)})
        return self.browse(records.ids)

    def write(self, vals):
        res = super().write(vals)
        if not self._fix_guard_open() and {
            "requested_price",
            "product_id",
            "estimate_line_id",
            "res_model",
            "res_id",
        } & set(vals):
            self._snapshot()
        return res

    # ---- lifecycle -----------------------------------------------------------
    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state not in ("draft", "pending"):
                raise UserError("Only a Draft override is submitted.")
            rec._snapshot()
            rec._guarded().write({"state": "pending"})
        return super().action_request_approval(justification=justification)

    def action_submit(self):
        return self.action_request_approval()

    def action_approve_dofa_override(self):
        """From the approver's M63 inbox: the tier of the depth below the
        floor, never the requester (fix.dofa.mixin)."""
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only an override awaiting approval is approved.")
            if not self.env.su:
                tier = rec._dofa_current_tier()
                group = DOFA_TIER_GROUP.get(tier)
                if group and not rec._dofa_authority_user().has_group(group):
                    raise UserError(
                        "DOFA authority insufficient: %s requires %s."
                        % (rec._dofa_amount_label(), dict(DOFA_TIERS)[tier])
                    )
            rec.action_dofa_approve()
            rec._guarded().write({"state": "approved"})
        return True

    def _approval_on_rejected(self, comment):
        self.filtered(lambda r: r.state == "pending")._guarded().write({"state": "rejected"})
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "pending")._guarded().write({"state": "draft"})
        return result

    # ---- use -----------------------------------------------------------------
    @api.model
    def _bound_to(self, line):
        """The approved (or already used) override of `line`, newest first."""
        if not line:
            return self.browse()
        return self.sudo().search(
            [
                ("res_model", "=", line._name),
                ("res_id", "=", line[:1].id),
                ("state", "in", ("approved", "consumed")),
            ],
            order="id desc",
            limit=1,
        )

    def _use_for(self, line, variant, price):
        """Raise unless this override covers `line` selling `variant` at
        `price`; consume it on first use."""
        self.ensure_one()
        rec = self.sudo()
        if not line:
            raise UserError(
                "Override %s is used only by the document line it names; name the line." % rec.name
            )
        if rec.res_model != line._name or rec.res_id != line[:1].id:
            raise UserError(
                "Override %s was approved for another document line; it covers that line "
                "only." % rec.name
            )
        if variant and rec.product_id != variant:
            raise UserError("Override %s is for another item." % rec.name)
        if rec.state not in ("approved", "consumed"):
            raise UserError("Override %s is %s." % (rec.name, rec.state))
        if price + 0.005 < rec.requested_price:
            raise UserError(
                "BDT %.2f is below the BDT %.2f override %s was approved for; a lower price "
                "needs a new override." % (price, rec.requested_price, rec.name)
            )
        rec._dofa_assert_approved("A below-floor price")
        if rec.state == "approved":
            if rec.valid_until < fields.Date.context_today(rec):
                rec._guarded().write({"state": "expired"})
                raise UserError("Override %s lapsed unused on %s." % (rec.name, rec.valid_until))
            rec._guarded().write(
                {
                    "state": "consumed",
                    "consumed_at": fields.Datetime.now(),
                    "consumed_by": self.env.uid,
                }
            )
            rec.message_post(body="Used by %s at BDT %.2f." % (line.display_name, price))
        return True

    @api.model
    def cron_expire_overrides(self):
        """Approved overrides past their use-by date lapse (Dhaka date)."""
        due = self.search(
            [("state", "=", "approved"), ("valid_until", "<", fields.Date.context_today(self))]
        )
        due._guarded().write({"state": "expired"})
        return len(due)


class ProductTemplatePriceGuard(models.Model):
    """M11-F11: product.template.list_price was the live price and anyone
    with product rights changed it, with no trail. It prices nothing now
    (price_for never reads it), and changing it still needs the Pricing
    Officer role and leaves a line in the product's chatter."""

    _inherit = "product.template"

    def write(self, vals):
        if (
            "list_price" in vals
            and self.env.uid != SUPERUSER_ID
            and not self.env.context.get("install_mode")
        ):
            new = float(vals["list_price"] or 0.0)
            moved = self.filtered(lambda t: abs((t.list_price or 0.0) - new) > 0.005)
            if moved:
                # the acting user's role, also under sudo(): the charge code
                # pushed its rate into list_price as superuser
                if not self.env.user.has_group(ROLE_OFFICER):
                    raise UserError(
                        "Changing the list price of %s needs the Pricing Officer role (M11). "
                        "Prices are M11 rate cards released by a Price-Book Releaser."
                        % moved[0].display_name
                    )
                old = {t.id: t.list_price for t in moved}
                res = super().write(vals)
                for tmpl in moved:
                    tmpl.sudo().message_post(
                        body="List price changed from %.2f to %.2f by %s."
                        % (old[tmpl.id], new, self.env.user.name)
                    )
                return res
        return super().write(vals)
