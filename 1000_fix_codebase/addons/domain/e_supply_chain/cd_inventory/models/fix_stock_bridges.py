# fix_stock_bridges — the M16 -> M15 hand-offs (A06 audit M15-9, M16-7).
#
# M16's goods receipt (fix.purchase.receipt, cd_requisition) recorded goods
# against product.product PO lines and never put them into the M15 ledger,
# and an inspection rejection (inspection.rejected) moved nothing. Now:
#   - a spare part names the product it is purchased as (fix.spare.part.
#     product_id); posting a PO goods receipt posts an M15 goods receipt
#     (purchase_order_id set, the receipt line's quantity, at the PO price)
#     into the PO's receiving location for every line whose product maps to a
#     part. Serialized parts get a DRAFT M15 receipt, one line per unit, for
#     the store to capture the serials and post;
#   - the inspection.rejected consumer moves the rejected quantity of that
#     part into quarantine at the receiving location, once per inspection.
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PARAM_PO_RECEIVING_LOCATION = "cd_inventory.po_receiving_location_id"


class FixPurchaseReceiptM15(models.Model):
    _inherit = "fix.purchase.receipt"

    stock_receipt_ids = fields.One2many(
        "fix.stock.receipt",
        compute="_compute_stock_receipts",
        string="M15 Goods Receipts",
    )

    def _compute_stock_receipts(self):
        Receipt = self.env["fix.stock.receipt"].sudo()
        for rec in self:
            rec.stock_receipt_ids = Receipt.search(
                [("source_model", "=", "fix.purchase.receipt"), ("source_res_id", "=", rec.id)]
            )

    def action_post(self):
        result = super().action_post()
        for rec in self.filtered(lambda r: r.state == "posted"):
            rec._fix_post_to_m15()
        return result

    # ------------------------------------------------------------- helpers
    def _fix_part_for(self, product, company):
        if not product:
            return self.env["fix.spare.part"]
        return (
            self.env["fix.spare.part"]
            .sudo()
            .search([("product_id", "=", product.id), ("company_id", "=", company.id)], limit=1)
        )

    def _fix_receiving_location(self, order):
        """The configured PO receiving location, else the main store of the
        PO's operating unit. Refuses clearly when there is none."""
        Location = self.env["fix.stock.location"].sudo()
        raw = self.env["ir.config_parameter"].sudo().get_param(PARAM_PO_RECEIVING_LOCATION)
        if raw:
            try:
                location = Location.browse(int(raw)).exists()
            except (TypeError, ValueError):
                location = Location.browse()
            if location and location.active and location.state == "active":
                return location
        base = [
            ("company_id", "=", order.company_id.id),
            ("operating_unit_id", "=", order.operating_unit_id.id),
            ("active", "=", True),
            ("state", "=", "active"),
        ]
        for location_type in ("central", "branch"):
            location = Location.search([*base, ("location_type", "=", location_type)], limit=1)
            if location:
                return location
        raise UserError(
            "PO %s maps to spare parts but there is no M15 receiving location: set "
            "%s or give operating unit %s an active central or branch store."
            % (order.name, PARAM_PO_RECEIVING_LOCATION, order.operating_unit_id.display_name)
        )

    def _fix_unit_cost(self, po_line, company):
        price = po_line.unit_price or 0.0
        currency = po_line.currency_id
        if currency and company.currency_id and currency != company.currency_id:
            price = currency._convert(
                price, company.currency_id, company, fields.Date.context_today(self)
            )
        return price

    def _fix_post_to_m15(self):
        """One M15 receipt for the plain parts (posted at once) and one draft
        receipt for the serialized parts (serials are captured by the store)."""
        self.ensure_one()
        order = self.purchase_order_id.sudo()
        company = order.company_id
        plain, serial = [], []
        for line in self.line_ids.filtered(lambda ln: ln.qty_received > 0):
            part = self._fix_part_for(line.product_id, company)
            if not part:
                continue
            cost = self._fix_unit_cost(line.po_line_id, company)
            if part.is_serialized:
                units = round(line.qty_received)
                serial += [
                    (
                        0,
                        0,
                        {
                            "part_id": part.id,
                            "qty_received": 1,
                            "qty_accepted": 1,
                            "unit_cost": cost,
                            "source_line_ref": "PRL:%d" % line.id,
                        },
                    )
                    for _unit in range(units)
                ]
            else:
                plain.append(
                    (
                        0,
                        0,
                        {
                            "part_id": part.id,
                            "qty_received": line.qty_received,
                            "qty_accepted": line.qty_received,
                            "unit_cost": cost,
                            "source_line_ref": "PRL:%d" % line.id,
                        },
                    )
                )
        if not plain and not serial:
            return self.env["fix.stock.receipt"]
        location = self._fix_receiving_location(order)
        Receipt = self.env["fix.stock.receipt"].sudo()
        base = {
            "partner_id": order.vendor_id.id,
            "location_id": location.id,
            "company_id": company.id,
            "operating_unit_id": order.operating_unit_id.id,
            "ownership_class": "owned",
            "purchase_order_id": order.id,
            "source_model": "fix.purchase.receipt",
            "source_res_id": self.id,
            "source_ref": self.name,
        }
        created = Receipt.browse()
        if plain:
            receipt = Receipt.create(dict(base, line_ids=plain))
            receipt.action_inspect()
            receipt.action_post()
            created |= receipt
        if serial:
            created |= Receipt.create(
                dict(base, line_ids=serial, inspection_notes="Capture each unit's serial")
            )
        return created


class FixPurchaseOrderLineRetiredPart(models.Model):
    """A06 final pass B16 (BRU-CAT-10, AUT-CAT-07): a discontinued part is run
    down and an obsolete one is out of service; neither is bought again. A line
    already on an order stays receivable."""

    _inherit = "fix.purchase.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        Part = self.env["fix.spare.part"].sudo()
        Order = self.env["fix.purchase.order"].sudo()
        for vals in vals_list:
            order = Order.browse(vals.get("order_id") or 0)
            if not vals.get("product_id") or not order.exists():
                continue
            retired = Part.search(
                [
                    ("product_id", "=", vals["product_id"]),
                    ("company_id", "=", order.company_id.id),
                    ("state", "!=", "active"),
                ],
                limit=1,
            )
            if retired:
                raise UserError(
                    "%s is %s: it is no longer purchased." % (retired.part_number, retired.state)
                )
        return super().create(vals_list)


class FixStockQuarantineConsumer(models.Model):
    _inherit = "fix.stock.quarantine"

    @api.model
    def consume_inspection_rejected(self, event):
        """M16 inspection.rejected -> M15 quarantine. Idempotent: the
        quarantine carries the inspection as its source, so a second delivery
        of the same event finds it and does nothing."""
        payload = event.get("payload") or {}
        key = "inspection.rejected:%s" % event.get("aggregate_id")
        Quarantine = self.sudo()
        if Quarantine.search_count([("source_ref", "=", key)]):
            return 0
        qty = float(payload.get("qty_rejected") or 0.0)
        product = self.env["product.product"].sudo().browse(payload.get("product_id") or 0).exists()
        receipt_ref = payload.get("receipt_ref")
        if qty <= 0 or not product or not receipt_ref:
            return 0
        stock_receipt = (
            self.env["fix.stock.receipt"]
            .sudo()
            .search(
                [
                    ("source_model", "=", "fix.purchase.receipt"),
                    ("source_ref", "=", receipt_ref),
                    ("state", "=", "posted"),
                ],
                limit=1,
            )
        )
        if not stock_receipt:
            return 0  # the receipt carried no mapped part, or its serials are pending
        part = stock_receipt.line_ids.mapped("part_id").filtered(lambda p: p.product_id == product)[
            :1
        ]
        if not part:
            return 0
        location = stock_receipt.location_id
        cls = stock_receipt.ownership_class
        bucket = self.env["fix.stock.onhand"]._bucket(part, location, cls)
        movable = min(qty, bucket.available_qty if bucket else 0.0)
        if movable <= 0:
            _logger.warning(
                "inspection %s: %s rejected of %s but none unrestricted at %s",
                event.get("aggregate_id"),
                qty,
                part.part_number,
                location.code,
            )
            return 0
        Quarantine.create(
            {
                "part_id": part.id,
                "location_id": location.id,
                "company_id": stock_receipt.company_id.id,
                "ownership_class": cls,
                "qty": movable,
                "reason": "defective",
                "notes": "Rejected at inspection of %s (PO %s)"
                % (receipt_ref, payload.get("po_ref") or "-"),
                "source_ref": key,
            }
        )
        return 1
