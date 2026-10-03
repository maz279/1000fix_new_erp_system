# cd_rate_card — M11 Pricing core (P06-M06, CD-M11-02).
#
# Price books and rate cards on M37's catalogue kernel; the computation
# lives in services/pricing-engine (L5 pure — T02). This module carries the
# DATA: cards, tiers, contract lanes, validity windows. Discount governance
# lives in cd_quotation (it is the quotation lifecycle's control).
from odoo import api, fields, models
from odoo.exceptions import UserError

from decimal import Decimal

from libs.py.fix_events import publish  # FF-28


class FixRateCard(models.Model):
    """A rate card: product -> rate per customer tier (min_tier), with
    contract cards at tier 99 (a signed contract is not a tier entitlement).

    Mirrors services/pricing-engine's RateCardLine — the card is the data;
    the engine is the computation (M64's BRU-MDM-15 shape: data here,
    execution in the service)."""

    _name = "fix.rate.card"
    _description = "Rate Card"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "product_code, min_tier"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _product_tier_unique = models.Constraint('UNIQUE (product_code, min_tier, contract_no)', 'One rate per product, tier and contract')

    name = fields.Char(string="Rate Line Name", compute="_compute_name", store=True)
    product_code = fields.Char(string="Product Code", required=True, index=True,
                               help="Catalogue item code (product.default_code)")
    line_type = fields.Selection(
        [("labour", "Labour"), ("part", "Part"), ("consumable", "Consumable"),
         ("transport", "Transport")], required=True, default="labour")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    unit_price = fields.Monetary(string="Rate (VAT-exclusive)", currency_field="currency_id",
                                 required=True)
    min_tier = fields.Integer(
        string="Minimum Tier", default=0,
        help="Customer tier >= this applies. 99 = CONTRACT rate (requires contract_no)")
    contract_no = fields.Char(string="Contract No.", index=True,
                              help="Set for contract rates (min_tier 99)")
    valid_from = fields.Date(string="Valid From")
    valid_to = fields.Date(string="Valid To")
    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    @api.depends("product_code", "min_tier", "contract_no")
    def _compute_name(self):
        for card in self:
            scope = "contract %s" % card.contract_no if card.contract_no else "tier %d" % card.min_tier
            card.name = "%s @ %s" % (card.product_code, scope)

    @api.constrains("min_tier", "contract_no", "unit_price")
    def _check_card(self):
        for card in self:
            if card.min_tier == 99 and not card.contract_no:
                raise UserError("A tier-99 rate is a CONTRACT rate — the contract number is required")
            if card.contract_no and card.min_tier != 99:
                raise UserError("Contract rates carry min_tier 99 (the engine's contract lane)")
            if card.unit_price <= 0:
                raise UserError("A rate must be positive")
            if card.valid_from and card.valid_to and card.valid_to < card.valid_from:
                raise UserError("Validity window is inverted")

    def to_engine_line(self):
        """Project this card to the pricing engine's RateCardLine."""
        from services.pricing_engine import RateCardLine  # pragma: no cover - path at runtime
        return RateCardLine(
            product_code=self.product_code, line_type=self.line_type,
            unit_price=Decimal(str(self.unit_price)), min_tier=self.min_tier)
