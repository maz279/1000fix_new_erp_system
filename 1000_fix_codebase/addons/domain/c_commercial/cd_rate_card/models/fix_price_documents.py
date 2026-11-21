# M01 estimate lines on the M11 price service (A04 ERP audit, 20 Nov 2026,
# M11-F1/F2/F6 and M37-F3).
#
# cd_rate_card loads after cd_service_order (through cd_contract_core), so it
# records on the estimate line what the price service said: the released
# price the line was measured against, where the line's price came from, and
# why a typed price differs. The estimate's own checks (fix_estimate.py
# _fix_check_price_floor / _dofa_amount) read these fields.
from odoo import api, fields, models
from odoo.exceptions import UserError

PRICE_SOURCES = [
    ("rate_card", "M11 released price"),
    ("changed", "Changed from the released price"),
    ("entered", "Entered (no released price)"),
]


class FixEstimateLinePricing(models.Model):
    _inherit = "fix.estimate.line"

    card_price = fields.Monetary(
        string="Released Price",
        currency_field="currency_id",
        compute="_compute_card_price",
        store=True,
        help="The M11 released unit price (before promotions) on the day the item was put "
        "on the line; 0 when no price is released. A lower line price is a discount the "
        "DOFA ladder counts.",
    )
    card_source = fields.Char(
        string="Released Price Source", compute="_compute_card_price", store=True
    )
    price_source = fields.Selection(
        PRICE_SOURCES, compute="_compute_price_source", store=True, string="Price Source"
    )
    price_override_reason = fields.Char(
        string="Price Change Reason",
        help="Why the line is priced differently from its released price. Required then.",
    )

    @api.depends("product_id", "estimate_id")
    def _compute_card_price(self):
        Card = self.env["fix.rate.card"]
        for line in self:
            if not line.product_id:
                line.card_price, line.card_source = 0.0, False
                continue
            res = Card.price_for(**line._fix_price_context())
            line.card_price = res["list_price"] or 0.0
            line.card_source = res["source"] if res["price"] is not None else False

    @api.depends("unit_price", "card_price", "product_id")
    def _compute_price_source(self):
        for line in self:
            if not line.card_price:
                line.price_source = "entered" if line.product_id else False
            elif abs((line.unit_price or 0.0) - line.card_price) <= 0.005:
                line.price_source = "rate_card"
            else:
                line.price_source = "changed"


class FixEstimateExplosion(models.Model):
    _inherit = "fix.estimate"

    def action_explode_catalogue_item(self, item_id, quantity=1.0, device_model_id=None):
        """M37-F3 (FR-CAT-028/041): put a catalogue service / bundle on the
        estimate as the lines its repair BOM and kit explode into, each priced
        by the M11 price service (no released price: left for the preparer
        to enter). Returns the new lines' ids."""
        self.ensure_one()
        item = self.env["fix.catalogue.item"].browse(int(item_id)).exists()
        if not item:
            raise UserError("No such catalogue item.")
        model = (
            self.env["fix.device.model"].browse(int(device_model_id)).exists()
            if device_model_id
            else None
        )
        item._fix_assert_sellable("service")
        rows = item._fix_explode(float(quantity or 1.0), model)
        if not rows:
            raise UserError(
                "%s has no repair BOM or kit to explode; add the item itself." % item.display_name
            )
        Product = self.env["product.product"]
        vals_list = []
        for row in rows:
            product = row["product"] or Product
            if not product:
                continue
            leaf = row["item"]
            if hasattr(product, "_fix_line_type_for"):
                line_type = product._fix_line_type_for()
            else:
                line_type = (
                    "part" if leaf and leaf.item_type in ("part", "accessory") else "service"
                )
            vals_list.append(
                {
                    "estimate_id": self.id,
                    "product_id": product.id,
                    "description": row.get("description") or product.display_name,
                    "quantity": row["qty"],
                    "line_type": line_type,
                }
            )
        return self.env["fix.estimate.line"].create(vals_list).ids
