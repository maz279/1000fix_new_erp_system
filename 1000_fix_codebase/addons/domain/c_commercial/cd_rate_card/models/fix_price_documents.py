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

    # ---- A04 ERP round 2 FR-PRC-032: the permanent override record ---------
    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._fix_log_price_override()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if {"unit_price", "product_id", "price_override_reason"} & set(vals):
            self._fix_log_price_override()
        return res

    def _fix_log_price_override(self):
        """A line priced away from its released price leaves one permanent
        record per price it was changed to (who, from, to, why)."""
        Log = self.env["fix.price.override.log"].sudo()
        Card = self.env["fix.rate.card"]
        for line in self.filtered(lambda ln: ln.price_source == "changed"):
            last = Log.search([("res_model", "=", line._name), ("res_id", "=", line.id)], limit=1)
            if last and abs(last.override_price - (line.unit_price or 0.0)) <= 0.005:
                continue
            Card.record_override(line, line.card_price, line.unit_price, line.price_override_reason)

    # ---- A04 ERP round 2 M37-F7: offer the live successor -------------------
    def action_use_live_successor(self):
        """Put the live successor of a discontinued item on the line, at its
        released price (BRU-CAT-08)."""
        for line in self:
            item = line.product_id.product_tmpl_id.catalogue_item_id[:1]
            live = item._fix_sale_substitute("service") if item else item
            if not live:
                raise UserError(
                    "%s has no live successor to offer." % (line.product_id.display_name or "")
                )
            variant = live.sudo().product_tmpl_id.product_variant_id
            ctx = dict(line._fix_price_context(), product=variant)
            res = self.env["fix.rate.card"].price_for(**ctx)
            vals = {"product_id": variant.id, "description": variant.display_name}
            if res["price"] is not None:
                vals["unit_price"] = res["price"]
            line.write(vals)
        return True

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
