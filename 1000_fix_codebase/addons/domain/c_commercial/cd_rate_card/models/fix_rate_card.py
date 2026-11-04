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
    _product_tier_unique = models.Constraint(
        "UNIQUE NULLS NOT DISTINCT (product_code, min_tier, contract_no)",
        "One rate per product, tier and contract",
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
    def _resolve(self, product_code, tier=0, contract_no=None, on_date=None):
        """The released card that prices `product_code` (BRU-PRC-11: the
        contract lane first, else the highest tier the customer reaches),
        within its validity window. Consumers: estimates, quotations, the
        price simulation."""
        if not product_code:
            return self.browse()
        day = on_date or fields.Date.context_today(self)
        base = [
            ("product_code", "=", product_code),
            ("state", "=", "released"),
            "|",
            ("valid_from", "=", False),
            ("valid_from", "<=", day),
            "|",
            ("valid_to", "=", False),
            ("valid_to", ">=", day),
        ]
        Card = self.sudo()
        if contract_no:
            card = Card.search(
                [*base, ("min_tier", "=", 99), ("contract_no", "=", contract_no)], limit=1
            )
            if card:
                return card
        return Card.search(
            [*base, ("min_tier", "<=", int(tier or 0)), ("min_tier", "!=", 99)],
            order="min_tier desc",
            limit=1,
        )

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
