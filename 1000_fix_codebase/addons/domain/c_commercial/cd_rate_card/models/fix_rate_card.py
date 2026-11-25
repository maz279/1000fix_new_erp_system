# cd_rate_card — M11 Pricing core (P06-M06, CD-M11-02).
#
# Price books and rate cards on M37's catalogue kernel; the computation
# lives in services/pricing-engine (L5 pure — T02). This module carries the
# DATA: cards, tiers, contract lanes, validity windows. Discount governance
# lives in cd_quotation (it is the quotation lifecycle's control).
import sys
from decimal import Decimal
from pathlib import Path

from odoo import api, fields, models
from odoo.exceptions import UserError

from .pricing_roles import ROLE_OFFICER, require_role

# A04 audit (2026-11-04) M11-5 (rc_01): what a released card prices with.
# These change only through an approved fix.price.change.
CARD_PRICE_FIELDS = frozenset(
    {
        "product_code",
        "line_type",
        "unit_price",
        "currency_id",
        "catalogue_item_id",
        "min_tier",
        "contract_no",
        "valid_from",
        "valid_to",
        "company_id",
        "partner_id",
        "version_id",
    }
)

# services/pricing-engine is a hyphenated (non-package) service folder: its
# module is imported from its src/ directory (same pattern as
# cd_tax_engine_bd's e-VAT client). parents[5] = the codebase root.
PRICING_ENGINE_SRC = Path(__file__).resolve().parents[5] / "services" / "pricing-engine" / "src"


class FixRateCard(models.Model):
    """A rate card: product -> rate per customer tier (min_tier), with
    contract cards at tier 99 (a signed contract is not a tier entitlement).

    Mirrors services/pricing-engine's RateCardLine — the card is the data;
    the engine is the computation (M64's BRU-MDM-15 shape: data here,
    execution in the service)."""

    _name = "fix.rate.card"
    _description = "Rate Card"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "product_code, min_tier"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    # NULLS NOT DISTINCT (PostgreSQL 15+): a TIER card has no contract_no,
    # and with plain UNIQUE two NULLs never collide - duplicate tier rates for
    # one product slipped through and made the engine's resolution ambiguous.
    # A04 ERP audit (20 Nov 2026) M11-F4/F13: the key also carries the
    # company, the customer and the start date, so next year's card is a new
    # version beside this year's (no overlap: _check_no_overlap) and a
    # company's card never blocks another company's.
    _product_tier_unique = models.Constraint(
        "UNIQUE NULLS NOT DISTINCT "
        "(company_id, product_code, min_tier, contract_no, partner_id, valid_from)",
        "One rate per company, product, tier, contract, customer and start date",
    )

    name = fields.Char(string="Rate Line Name", compute="_compute_name", store=True)
    product_code = fields.Char(
        string="Product Code",
        required=True,
        index=True,
        help="Catalogue item code (product.default_code)",
    )
    line_type = fields.Selection(
        [
            ("labour", "Labour"),
            ("part", "Part"),
            ("consumable", "Consumable"),
            ("transport", "Transport"),
        ],
        required=True,
        default="labour",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    unit_price = fields.Monetary(
        string="Rate (VAT-exclusive)", currency_field="currency_id", required=True
    )
    catalogue_item_id = fields.Many2one(
        "fix.catalogue.item",
        string="Catalogue Item",
        index=True,
        help="Optional link to the catalogue item: enables margin and realised-price analysis.",
    )
    min_tier = fields.Integer(
        string="Minimum Tier",
        default=0,
        help="Customer tier >= this applies. 99 = CONTRACT rate (requires contract_no)",
    )
    contract_no = fields.Char(
        string="Contract No.", index=True, help="Set for contract rates (min_tier 99)"
    )
    valid_from = fields.Date(string="Valid From")
    valid_to = fields.Date(string="Valid To")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    # A04 ERP audit (20 Nov 2026) M11-F2/F3: the customer lane (a price agreed
    # for one customer, below the contract lane and above the tier lane).
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        index=True,
        ondelete="restrict",
        help="A customer-specific rate. Empty = a tier or standard rate.",
    )
    # M11-F5: a card that belongs to a price-book version prices only while
    # that version is in force.
    version_id = fields.Many2one(
        "fix.price.version",
        string="Price-Book Version",
        index=True,
        ondelete="restrict",
        help="The price-book version this rate belongs to; it prices only while that "
        "version is in force.",
    )
    active = fields.Boolean(default=True)
    # A04 audit (2026-11-04) M11-5: a card prices nothing until a Price-Book
    # Releaser who did not raise it releases it (fix.price.change); a
    # released card's price changes the same way. Cards that existed before
    # this control were released by the 19.0.1.1.0 migration.
    state = fields.Selection(
        [("draft", "Draft"), ("released", "Released"), ("retired", "Retired")],
        required=True,
        default="draft",
        readonly=True,
        index=True,
    )
    released_by = fields.Many2one("res.users", readonly=True, copy=False)
    released_at = fields.Datetime(readonly=True, copy=False)
    proposed_unit_price = fields.Monetary(
        string="Proposed Rate", currency_field="currency_id", copy=False
    )
    change_reason = fields.Text(copy=False)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {"state", "released_by", "released_at"}
        if self:
            guarded |= {"active"}
        if any(card.state != "draft" for card in self):
            guarded |= CARD_PRICE_FIELDS
        return guarded

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(card.state != "draft" for card in self):
            locked |= CARD_PRICE_FIELDS
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, (ROLE_OFFICER,), "Creating a rate card")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            require_role(self.env, (ROLE_OFFICER,), "Changing a rate card")
        return super().write(vals)

    def _raise_change(self, change_type, value, reason):
        Change = self.env["fix.price.change"]
        for card in self:
            why = (reason or card.change_reason or "").strip()
            if not why and change_type == "release":
                why = "Release of the new rate %s" % card.name
            if not why:
                raise UserError("State why the rate changes (FR-PRC-034).")
            Change.create(
                {
                    "target_type": "rate_card",
                    "change_type": change_type,
                    "rate_card_id": card.id,
                    "proposed_value": value(card),
                    "reason": why,
                }
            ).action_submit()
            card.write({"proposed_unit_price": 0.0, "change_reason": False})
        return True

    def action_request_release(self):
        """Draft -> Released, once a releaser approves (M63 inbox)."""
        require_role(self.env, (ROLE_OFFICER,), "Raising a rate release")
        return self._raise_change("release", lambda c: c.proposed_unit_price or c.unit_price, None)

    def action_request_change(self):
        """Change a released rate to the staged Proposed Rate."""
        require_role(self.env, (ROLE_OFFICER,), "Raising a rate change")
        return self._raise_change("change", lambda c: c.proposed_unit_price, None)

    def action_request_retire(self, reason=None):
        require_role(self.env, (ROLE_OFFICER,), "Raising a rate retirement")
        return self._raise_change("retire", lambda c: 0.0, reason)

    @api.model
    def _resolve(
        self,
        product_code,
        tier=0,
        contract_no=None,
        on_date=None,
        company=None,
        partner=None,
        currency=None,
    ):
        """The released card that prices `product_code` on `on_date`
        (BRU-PRC-11): the contract lane first, then the customer's own rate,
        then the highest tier the customer reaches (tier 0 = the standard
        rate). Only cards of `company` (default: the current one) and of
        `currency` (when given), within their validity window and, for a
        card of a price-book version, while that version is in force
        (A04 ERP audit 20 Nov 2026, M11-F4/F5/F13/F14). Consumers: price_for
        (the M11 price service), the price simulation."""
        if not product_code:
            return self.browse()
        day = on_date or fields.Date.context_today(self)
        company = company or self.env.company
        base = [
            ("product_code", "=", product_code),
            ("state", "=", "released"),
            ("company_id", "=", company.id),
            # A04 ERP round 2 FR-PRC-012: a labour rate per hour prices by the
            # standard repair time (price_for), never as an item's unit price
            ("rate_kind", "!=", "labour_hour"),
            "|",
            ("valid_from", "=", False),
            ("valid_from", "<=", day),
            "|",
            ("valid_to", "=", False),
            ("valid_to", ">=", day),
        ]
        if currency:
            base.append(("currency_id", "=", currency.id))
        Card = self.sudo()

        def first(domain, order="valid_from desc, id desc"):
            found = Card.search(domain, order=order)
            return found.filtered(lambda c: c._version_in_force(day))[:1]

        if contract_no:
            card = first([*base, ("min_tier", "=", 99), ("contract_no", "=", contract_no)])
            if card:
                return card
        customer = partner.commercial_partner_id if partner else None
        if customer:
            card = first([*base, ("min_tier", "!=", 99), ("partner_id", "=", customer.id)])
            if card:
                return card
        return first(
            [
                *base,
                ("min_tier", "<=", int(tier or 0)),
                ("min_tier", "!=", 99),
                ("partner_id", "=", False),
            ],
            order="min_tier desc, valid_from desc, id desc",
        )

    def _version_in_force(self, day):
        """M11-F5: a card with no version is governed by its own window; a
        card of a price-book version prices while that version is Active, or
        - for a document dated in the past - while it was the version in
        force (from its effective date to the day its successor took over)."""
        self.ensure_one()
        version = self.version_id.sudo()
        if not version:
            return True
        if version.effective_from and version.effective_from > day:
            return False
        if version.state == "active":
            return True
        if version.state == "superseded":
            nxt = version.superseded_by_id
            return bool(nxt and nxt.effective_from and day < nxt.effective_from)
        return False

    @api.depends("product_code", "min_tier", "contract_no")
    def _compute_name(self):
        for card in self:
            scope = (
                "contract %s" % card.contract_no if card.contract_no else "tier %d" % card.min_tier
            )
            card.name = "%s @ %s" % (card.product_code, scope)

    @api.constrains("min_tier", "contract_no", "unit_price", "catalogue_item_id")
    def _check_card(self):
        for card in self:
            # A04 audit M37-2 (ci_08): a discontinued item gets no new rate
            # (BRU-CAT-14, AUT-CAT-07).
            item = card.catalogue_item_id.sudo()
            if item and item.state in ("deprecated", "obsolete"):
                raise UserError(
                    "Catalogue item %s is %s: it is no longer sold, so it takes no rate."
                    % (item.name, dict(item._fields["state"].selection)[item.state])
                )
            if card.min_tier == 99 and not card.contract_no:
                raise UserError(
                    "A tier-99 rate is a CONTRACT rate — the contract number is required"
                )
            if card.contract_no and card.min_tier != 99:
                raise UserError("Contract rates carry min_tier 99 (the engine's contract lane)")
            if card.unit_price <= 0:
                raise UserError("A rate must be positive")
            if card.valid_from and card.valid_to and card.valid_to < card.valid_from:
                raise UserError("Validity window is inverted")
            # A04 ERP audit (20 Nov 2026) M11-F8: a card was created at 400
            # under a 950 floor; only the mass change looked at floors.
            card._assert_not_below_floor(card.unit_price)

    def _assert_not_below_floor(self, price):
        """A rate never sits below the item's floor: the M11 price floors for
        its code or item, and the M15 cost margin floor (M11-F8/F9)."""
        self.ensure_one()
        info = self._floor_info(
            self.catalogue_item_id or self.product_code, company=self.company_id
        )
        if info["floor"] and (price or 0.0) + 0.005 < info["floor"]:
            raise UserError(
                "Rate %s at BDT %.2f is below the floor of BDT %.2f (%s). A rate is "
                "never released below its floor (BRU-PRC-04)."
                % (self.name or self.product_code, price or 0.0, info["floor"], info["floor_basis"])
            )

    @api.constrains(
        "state",
        "valid_from",
        "valid_to",
        "product_code",
        "min_tier",
        "contract_no",
        "partner_id",
        "company_id",
        "currency_id",
        "active",
    )
    def _check_no_overlap(self):
        """M11-F4: two released rates of the same lane never overlap in time,
        so the price on a document date is never ambiguous."""
        for card in self.filtered(lambda c: c.state == "released" and c.active):
            domain = [
                ("id", "!=", card.id),
                ("state", "=", "released"),
                ("company_id", "=", card.company_id.id),
                ("product_code", "=", card.product_code),
                ("min_tier", "=", card.min_tier),
                ("contract_no", "=", card.contract_no or False),
                ("partner_id", "=", card.partner_id.id or False),
                ("currency_id", "=", card.currency_id.id),
                ("version_id", "=", card.version_id.id or False),
            ]
            if card.valid_to:
                domain += ["|", ("valid_from", "=", False), ("valid_from", "<=", card.valid_to)]
            if card.valid_from:
                domain += ["|", ("valid_to", "=", False), ("valid_to", ">=", card.valid_from)]
            clash = self.sudo().search(domain, limit=1)
            if clash:
                raise UserError(
                    "%s overlaps %s (%s to %s): a new rate starts after the one in force "
                    "ends (M11 effective dating)."
                    % (
                        card.name,
                        clash.name,
                        clash.valid_from or "open",
                        clash.valid_to or "open",
                    )
                )

    def to_engine_line(self):
        """Project this card to the pricing engine's RateCardLine.

        (`from services.pricing_engine import ...` could never resolve - the
        folder is `pricing-engine` - so the projection always raised
        ModuleNotFoundError; a coverage exclusion comment hid it from the gate.)"""
        self.ensure_one()
        if str(PRICING_ENGINE_SRC) not in sys.path:
            sys.path.insert(0, str(PRICING_ENGINE_SRC))
        from pricing_engine import RateCardLine

        return RateCardLine(
            product_code=self.product_code,
            line_type=self.line_type,
            unit_price=Decimal(str(self.unit_price)),
            min_tier=self.min_tier,
        )
