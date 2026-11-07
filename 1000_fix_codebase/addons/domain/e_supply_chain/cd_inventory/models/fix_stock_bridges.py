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
#
# A06 final pass, M16-7 / BRU-PRO-11 and -16: goods went into available stock
# at receipt, so a later rejection moved only what was still there, and nothing
# if it had been issued; serialized parts were skipped altogether. When
# inspection is required (cd_requisition.receipt_inspection_required) they now
# wait for it:
#   - plain parts sit in the on-hand status "inspection", which nothing can
#     reserve or issue, until the inspection is confirmed. Accepted goes to
#     unrestricted, rejected to quarantine, in that same transaction;
#   - serialized parts stay on their draft M15 receipt, which cannot be posted
#     before the inspection; rejected units leave it and are quarantined;
#   - a rejection of a mapped part raises a draft RTV for it.
# A receipt posted before this rule (its goods already unrestricted) keeps the
# old path through the event consumer.
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_inventory_approval import location_class

_logger = logging.getLogger(__name__)

PARAM_PO_RECEIVING_LOCATION = "cd_inventory.po_receiving_location_id"
HOLD_KEY = "fix_receipt_hold_for_inspection"
_HOLD = object()  # in-process only: a JSON-RPC context cannot carry this object


class FixStockOnhandInspection(models.Model):
    _inherit = "fix.stock.onhand"

    stock_status = fields.Selection(
        selection_add=[("inspection", "In Inspection")], ondelete={"inspection": "cascade"}
    )

    @api.model
    def _apply(self, part, location, ownership, delta, *args, **kwargs):
        """A receipt posted for inspection lands in the held status."""
        if (
            self.env.context.get(HOLD_KEY) is _HOLD
            and delta > 0
            and kwargs.get("status", "unrestricted") == "unrestricted"
        ):
            kwargs["status"] = "inspection"
        return super()._apply(part, location, ownership, delta, *args, **kwargs)


class FixStockReceiptInspectionHold(models.Model):
    _inherit = "fix.stock.receipt"

    inspection_held = fields.Boolean(
        string="Held for Inspection",
        readonly=True,
        copy=False,
        help="Posted into the In Inspection status; the inspection releases it.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"inspection_held"}

    def _fix_assert_inspected(self):
        """Goods of a PO receipt enter stock only after their inspection."""
        if self.env.context.get(HOLD_KEY) is _HOLD:
            return
        Line = self.env["fix.purchase.receipt.line"].sudo()
        for rec in self.filtered(lambda r: r.source_model == "fix.purchase.receipt"):
            refs = rec.line_ids.mapped("source_line_ref")
            ids = [int(ref[4:]) for ref in refs if ref and ref.startswith("PRL:")]
            pending = Line.browse(ids).exists().filtered(lambda r: r.inspection_state == "pending")
            if pending:
                raise UserError(
                    "Receipt %s waits for the inspection of %s (BRU-PRO-11): confirm the "
                    "inspection outcome first." % (rec.name, pending[0].display_name)
                )

    def action_inspect(self):
        self._fix_assert_inspected()
        return super().action_inspect()

    def action_post(self):
        self._fix_assert_inspected()
        return super().action_post()


class FixProcurementInspectionM15(models.Model):
    _inherit = "fix.procurement.inspection"

    def action_confirm(self):
        result = super().action_confirm()
        for rec in self:
            rec.sudo()._fix_settle_m15()
        return result

    def _fix_settle_m15(self):
        """Release what this inspection judged, once, in its own transaction."""
        self.ensure_one()
        prl = self.receipt_line_id
        lines = (
            self.env["fix.stock.receipt.line"]
            .sudo()
            .search(
                [
                    ("source_line_ref", "=", "PRL:%d" % prl.id),
                    ("receipt_id.source_model", "=", "fix.purchase.receipt"),
                    ("receipt_id.source_res_id", "=", prl.receipt_id.id),
                ]
            )
        )
        held = lines.filtered(lambda ln: ln.receipt_id.inspection_held)
        draft = lines.filtered(lambda ln: ln.receipt_id.state == "draft")
        if held:
            self._fix_release_held(held[:1])
        elif draft:
            self._fix_settle_serials(draft)

    def _fix_release_held(self, line):
        receipt, part = line.receipt_id, line.part_id
        location = receipt.location_id
        cls = location_class(location, receipt.ownership_class)
        Onhand = self.env["fix.stock.onhand"].sudo()
        accepted, rejected = self.qty_accepted or 0.0, self.qty_rejected or 0.0
        if accepted > 0:
            Onhand._fix_move_status(part, location, cls, accepted, "inspection", "unrestricted")
        vals = {"qty_accepted": accepted}
        if rejected > 0:
            Onhand._fix_move_status(part, location, cls, rejected, "inspection", "quarantine")
            quarantine = self._fix_quarantine_rejected(receipt, part, cls, rejected)
            vals["quarantine_id"] = quarantine.id
        line._guarded().write(vals)

    def _fix_settle_serials(self, lines):
        """Rejected units leave the draft receipt (those with no serial yet
        first) and enter quarantine, valued at the PO price. The rest are posted
        with their serials, which the store now may do."""
        rejected = round(self.qty_rejected or 0.0)
        if rejected <= 0:
            return
        receipt, part = lines[0].receipt_id, lines[0].part_id
        cost = lines[0].unit_cost or 0.0
        location = receipt.location_id
        cls = location_class(location, receipt.ownership_class)
        self.env["fix.stock.onhand"].sudo()._apply(
            part, location, cls, rejected, cost, status="quarantine"
        )
        self.env["fix.inventory.valuation.suspense"].sudo()._fix_post(
            "receipt", part, rejected, cost, receipt.name, location=location, ownership=cls
        )
        lines.sorted(lambda ln: (bool(ln.line_no), ln.id))[:rejected].unlink()
        self._fix_quarantine_rejected(receipt, part, cls, rejected)
        if not receipt.line_ids:
            receipt.unlink()

    def _fix_quarantine_rejected(self, receipt, part, cls, qty):
        """The quantity is already in the quarantine status: record it in place.
        The source key makes the inspection.rejected consumer a no-op."""
        order = self.receipt_line_id.receipt_id.purchase_order_id
        quarantine = (
            self.env["fix.stock.quarantine"]
            .sudo()
            ._guarded()
            .with_context(fix_quarantine_in_place=True)
            .create(
                {
                    "part_id": part.id,
                    "location_id": receipt.location_id.id,
                    "company_id": receipt.company_id.id,
                    "ownership_class": cls,
                    "qty": qty,
                    "reason": "defective",
                    "notes": "Rejected at inspection %s of %s (PO %s)"
                    % (self.name, receipt.source_ref or receipt.name, order.name or "-"),
                    "source_ref": "inspection.rejected:%d" % self.id,
                }
            )
        )
        quarantine._fix_raise_draft_rtv(order.vendor_id or receipt.partner_id)
        return quarantine


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
            if any(line.inspection_required for line in self.line_ids):
                receipt._guarded().write({"inspection_held": True})
                receipt = receipt.with_context(**{HOLD_KEY: _HOLD})
            receipt.action_inspect()
            receipt.action_post()
            created |= receipt
        if serial:
            created |= Receipt.create(
                dict(base, line_ids=serial, inspection_notes="Capture each unit's serial")
            )
        return created


class FixStockQuarantineConsumer(models.Model):
    _inherit = "fix.stock.quarantine"

    def _fix_raise_draft_rtv(self, vendor):
        """BRU-PRO-16: a rejected receipt goes back to its vendor. A draft for the
        store to complete with the RMA reference and have approved."""
        self.ensure_one()
        return (
            self.env["fix.stock.rtv"]
            .sudo()
            .create(
                {
                    "partner_id": vendor.id,
                    "part_id": self.part_id.id,
                    "location_id": self.location_id.id,
                    "quarantine_id": self.id,
                    "company_id": self.company_id.id,
                    "qty": self.qty,
                    "reason": "quality",
                    "notes": self.notes,
                }
            )
        )

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
        quarantine = Quarantine.create(
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
        quarantine._fix_raise_draft_rtv(stock_receipt.partner_id)
        return 1
