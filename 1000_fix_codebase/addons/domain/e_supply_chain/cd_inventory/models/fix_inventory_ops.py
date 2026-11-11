# fix_inventory_ops — M15: the per-location stock ledger and the control
# documents the workspace screens read: on-hand by ownership class and stock
# status, lots, goods receipts (inspection gate), transfers, blind counts,
# van reconciliation, quarantine/scrap, RTV and ownership-class changes.
#
# A06 audit (2026-11-03) M15-1..M15-15: every state, quantity and cost on
# these documents was a plain field; stock could be created from nothing five
# ways; there was no approval, no stock status and no cost layer. Now:
#   - fix.stock.onhand is the ledger, written only by the movements below
#     (users have read access only); it carries a STATUS (unrestricted /
#     quarantine / in transit / staged) and only unrestricted stock can be
#     reserved or issued (BRU-INV-08);
#   - a receipt values the bucket at its weighted-average cost; issues,
#     returns, transfers and scrap move stock at the bucket's average cost;
#   - every workflow field is guarded (fix.guarded.mixin) and every
#     approval is a two-person Inventory Controller decision
#     (fix.inventory.approval.mixin); posted documents are final;
#   - every valued movement books a suspense entry for M19.
import logging

from odoo import SUPERUSER_ID, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_inventory_approval import (
    APPROVER_BRANCH_GROUP,
    APPROVER_FINANCE_GROUP,
    CONTROLLER_GROUP,
    COST_GROUP,
    PARAM_COUNT_TOLERANCE_PCT,
    PARAM_TRANSFER_THRESHOLD,
    PARAM_VAN_TOLERANCE_PCT,
    PARAM_WRITEOFF_THRESHOLD,
    VALUED_CLASSES,
    VAN_VARIANCE_GROUPS,
    check_location_usable,
    check_quantity,
    inv_param,
    location_class,
)

_logger = logging.getLogger(__name__)

OWNERSHIP_CLASSES = [
    ("owned", "Owned Stock"),
    ("consignment", "Supplier Consignment"),
    ("customer", "Customer Property"),
    ("van", "Van Stock"),
    ("bench", "Bench / WIP"),
    ("warranty", "Warranty Reserve"),
]

STOCK_STATUSES = [
    ("unrestricted", "Unrestricted"),
    ("quarantine", "Quarantine"),
    ("in_transit", "In Transit"),
    ("staged", "Staged for Dispatch"),
]

COUNT_REASONS = [
    ("damage", "Damage / breakage"),
    ("loss", "Loss / theft"),
    ("unrecorded_issue", "Unrecorded issue"),
    ("unrecorded_receipt", "Unrecorded receipt"),
    ("prior_miscount", "Prior miscount"),
    ("data_error", "Data / unit error"),
    ("other", "Other (explained in the note)"),
]

EPS = 1e-6

# A06 final pass B3: a PO a receipt may be taken against
RECEIPT_PO_STATES = ("sent", "acknowledged", "partially_received", "received")
# A06 final pass B15: what happens to a transfer's short quantity
TRANSFER_RESOLUTIONS = ("found", "returned", "quarantine")


def _changes(records, vals):
    """True when vals would change any stored value of records."""
    for rec in records:
        for name, value in vals.items():
            field = rec._fields.get(name)
            if field is None:
                continue
            if rec._fix_guard_differs(name, value, rec[name]):
                return True
    return False


def _event(env, event_type, aggregate, aggregate_id, payload):
    """Publish inside the transaction (a failed publish fails the movement:
    an event the ledger promised must not be silently dropped)."""
    publish(env, event_type, aggregate, aggregate_id, payload)


class FixStockOnhand(models.Model):
    """On-hand quantity of one part at one location, ownership class and status."""

    _name = "fix.stock.onhand"
    _description = "Stock On Hand"
    _order = "part_id, location_id"
    _inherit = ["fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="cascade", index=True
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Location", required=True, ondelete="cascade", index=True
    )
    ownership_class = fields.Selection(
        OWNERSHIP_CLASSES, required=True, default="owned", index=True
    )
    stock_status = fields.Selection(
        STOCK_STATUSES,
        string="Stock Status",
        required=True,
        default="unrestricted",
        index=True,
        help="Only unrestricted stock can be reserved or issued (BRU-INV-08).",
    )
    qty = fields.Float(string="Quantity")
    # 0, never NULL: SQL and BI sums over a NULL bucket read "unknown", and the
    # available-quantity compute already treats a missing value as 0
    reserved = fields.Float(string="Reserved", default=0.0)
    available_qty = fields.Float(string="Available", compute="_compute_available", store=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    unit_cost = fields.Monetary(
        string="Unit Cost",
        currency_field="currency_id",
        groups=COST_GROUP,
        help="Weighted-average cost of the quantity in this bucket.",
    )
    # A06 final pass B19: weighted average is what runs. FIFO has no cost
    # layers behind it, so choosing it would be a label only: refused below.
    valuation_method = fields.Selection(
        [("fifo", "FIFO"), ("wac", "WAC (Weighted Average)"), ("standard", "Standard Cost")],
        required=True,
        default="wac",
    )
    last_move_date = fields.Date(string="Last Movement")

    _part_loc_class_unique = models.Constraint(
        "UNIQUE (part_id, location_id, ownership_class, stock_status)",
        "One on-hand row per part, location, ownership class and stock status",
    )
    _qty_non_negative = models.Constraint(
        "CHECK (qty >= 0 AND reserved >= 0 AND reserved <= qty)",
        "Quantities cannot be negative and reserved cannot exceed on-hand",
    )

    def _fix_guarded_fields(self) -> set:
        # The ledger is written only by the movements (A06 audit M15-1).
        return super()._fix_guarded_fields() | {
            "part_id",
            "location_id",
            "ownership_class",
            "stock_status",
            "qty",
            "reserved",
            "unit_cost",
            "valuation_method",
            "company_id",
            "last_move_date",
        }

    @api.depends("qty", "reserved")
    def _compute_available(self):
        for rec in self:
            rec.available_qty = round((rec.qty or 0.0) - (rec.reserved or 0.0), 3)

    @api.constrains("valuation_method")
    def _check_valuation_method(self):
        for rec in self:
            if rec.valuation_method != "wac":
                raise ValidationError(
                    "FIFO and standard cost are not available: the ledger values every bucket "
                    "at its weighted average cost and holds no FIFO cost layers."
                )

    # ------------------------------------------------------------------ core
    @api.model
    def _bucket(self, part, location, ownership, status="unrestricted"):
        """The ledger row, as sudo: movements read its cost and write it for
        users who may see neither (spec section 13). Never returned to a
        caller outside the ledger's own code."""
        return self.sudo().search(
            [
                ("part_id", "=", part.id),
                ("location_id", "=", location.id),
                ("ownership_class", "=", ownership),
                ("stock_status", "=", status),
            ],
            limit=1,
        )

    @api.model
    def _fix_check_bins(self, part, location, qty):
        """BRU-WMS-01 / M41-1 (A06 final pass B9): at a location a warehouse
        breaks down into bins, the slots are part of the ledger. An M15 issue,
        transfer, quarantine, RTV or class change names no bin, so it may take
        only the stock that is NOT slotted; slotted stock leaves through a wave
        pick or an approved floor count. Refusing is the smaller correct
        option: choosing a slot would need a bin scan on every M15 screen, and
        a silent choice would be M41 authoring a movement nobody confirmed."""
        warehouses = (
            self.env["fix.warehouse"].sudo().search([("stock_location_id", "=", location.id)])
        )
        if not warehouses:
            return
        slots = (
            self.env["fix.wms.slot"]
            .sudo()
            .search(
                [
                    ("part_id", "=", part.id),
                    ("bin_id.zone_id.warehouse_id", "in", warehouses.ids),
                ]
            )
        )
        binned = sum(slots.mapped("qty"))
        if binned <= EPS:
            return
        rows = self.sudo().search(
            [
                ("part_id", "=", part.id),
                ("location_id", "=", location.id),
                ("stock_status", "=", "unrestricted"),
            ]
        )
        free = round(sum(rows.mapped("qty")) - binned, 4)
        if qty > free + EPS:
            raise UserError(
                "%s of %s at %s is in warehouse bins; only %s is outside them. Bin stock "
                "leaves through a wave pick or a floor count, so that the bins and the "
                "ledger agree (BRU-WMS-01)."
                % (round(binned, 4), part.part_number, location.code, max(free, 0.0))
            )

    @api.model
    def _apply(
        self,
        part,
        location,
        ownership,
        delta,
        unit_cost=None,
        must_exist=True,
        status="unrestricted",
        from_reserved=False,
    ):
        """Move `delta` into (or out of) a part/location/class/status bucket.

        Positive deltas create the bucket and value it at the WEIGHTED
        AVERAGE of what it held and what arrives (`unit_cost`; when no cost is
        given the bucket keeps its cost). Negative deltas never go below zero
        and never take reserved stock unless `from_reserved` (the reserving
        document consumes its own reservation). Returns the bucket.
        """
        if not delta:
            raise UserError("A stock movement needs a non-zero quantity.")
        check_quantity(part, abs(delta), "movement")
        if not location.active or location.state != "active":
            raise UserError("Location %s is not active and cannot move stock." % location.code)
        row = self._bucket(part, location, ownership, status)
        Ledger = self.sudo()
        today = fields.Date.context_today(self)
        if not row and delta > 0:
            cost = unit_cost
            if cost is None:
                master = part.sudo()
                cost = master.average_cost or master.unit_cost
            return Ledger.create(
                {
                    "company_id": location.company_id.id or part.company_id.id,
                    "operating_unit_id": location.operating_unit_id.id or False,
                    "part_id": part.id,
                    "location_id": location.id,
                    "ownership_class": ownership,
                    "stock_status": status,
                    "qty": delta,
                    "reserved": 0.0,
                    "unit_cost": cost or 0.0,
                    "last_move_date": today,
                }
            )
        if not row:
            # A ledger-native movement always demands its bucket; the legacy
            # flag only lets a caller ask "nothing there" without an error.
            if not must_exist:
                return row
            raise UserError(
                "No %s %s stock of %s at %s to move."
                % (status.replace("_", " "), ownership, part.part_number, location.code)
            )
        old_qty = row.qty or 0.0
        new_qty = old_qty + delta
        if new_qty < -EPS:
            raise UserError(
                "Moving %s of %s out of %s would leave %s: insufficient on-hand."
                % (abs(delta), part.part_number, location.code, round(new_qty, 4))
            )
        vals = {"qty": max(new_qty, 0.0), "last_move_date": today}
        if delta > 0 and unit_cost is not None:
            total = old_qty + delta
            vals["unit_cost"] = round(
                (old_qty * (row.unit_cost or 0.0) + delta * unit_cost) / total, 4
            )
        if delta < 0:
            free = old_qty - (row.reserved or 0.0)
            if from_reserved:
                take = min(row.reserved or 0.0, abs(delta))
                vals["reserved"] = round((row.reserved or 0.0) - take, 4)
            elif abs(delta) > free + EPS:
                raise UserError(
                    "Only %s of %s at %s is unreserved; %s is reserved for other work."
                    % (round(free, 4), part.part_number, location.code, row.reserved)
                )
            if vals["qty"] < (vals.get("reserved", row.reserved) or 0.0) - EPS:
                vals["reserved"] = vals["qty"]
        row.sudo().write(vals)
        return row

    @api.model
    def _fix_move_status(self, part, location, ownership, qty, from_status, to_status):
        """Move qty between two statuses of one location/class at its cost."""
        source = self._bucket(part, location, ownership, from_status)
        cost = source.unit_cost if source else None
        self._apply(part, location, ownership, -qty, status=from_status)
        self._apply(part, location, ownership, qty, unit_cost=cost, status=to_status)
        return cost or 0.0

    # ------------------------------------------------- cross-builder contract
    @api.model
    def _fix_reserve(self, part, location, ownership, qty, ref):
        """Reserve `qty` of unrestricted stock for `ref`; refuses to reserve
        more than is available (on hand minus what is already reserved)."""
        check_quantity(part, qty, "reservation")
        row = self._bucket(part, location, ownership)
        available = (row.qty - row.reserved) if row else 0.0
        if qty > available + EPS:
            raise UserError(
                "Cannot reserve %s of %s at %s for %s: only %s is available."
                % (qty, part.part_number, location.code, ref or "-", round(available, 4))
            )
        row.sudo().write({"reserved": round((row.reserved or 0.0) + qty, 4)})
        _logger.info("reserved %s %s at %s for %s", qty, part.part_number, location.code, ref)
        return row

    @api.model
    def _fix_unreserve(self, part, location, ownership, qty, ref):
        """Release a reservation; refuses to release more than is reserved."""
        check_quantity(part, qty, "reservation release")
        row = self._bucket(part, location, ownership)
        reserved = row.reserved if row else 0.0
        if qty > reserved + EPS:
            raise UserError(
                "Cannot release %s of %s at %s for %s: only %s is reserved."
                % (qty, part.part_number, location.code, ref or "-", reserved)
            )
        row.sudo().write({"reserved": round(reserved - qty, 4)})
        return row

    @api.model
    def _fix_revalue(self, part, location, ownership, amount, ref):
        """Add `amount` (BDT, may be negative) to the bucket's value without
        changing its quantity: unit cost += amount / qty. The part's average
        cost follows (it is computed from the buckets). Refuses an empty
        bucket and a revaluation below zero. Books a revaluation entry."""
        row = self._bucket(part, location, ownership)
        if not row or (row.qty or 0.0) <= EPS:
            raise UserError(
                "Cannot revalue %s at %s (%s): the bucket holds no quantity."
                % (part.part_number, location.code, ownership)
            )
        new_cost = (row.unit_cost or 0.0) + (amount or 0.0) / row.qty
        if new_cost < -EPS:
            raise UserError(
                "Revaluing %s at %s by %s would make its unit cost negative."
                % (part.part_number, location.code, amount)
            )
        row.sudo().write({"unit_cost": round(max(new_cost, 0.0), 4)})
        if amount and ownership in VALUED_CLASSES:
            self.env["fix.inventory.valuation.suspense"]._fix_post(
                "revaluation", part, 1.0, amount, ref, location=location, ownership=ownership
            )
        return row


class FixStockLot(models.Model):
    """A serial or lot in the ledger, with its current location and age."""

    _name = "fix.stock.lot"
    _description = "Stock Serial / Lot"
    _order = "received_on desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(string="Serial / Lot", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="cascade", index=True
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Location", ondelete="set null", index=True
    )
    qty = fields.Float(string="Quantity")
    status = fields.Selection(
        [
            ("in_stock", "In Stock"),
            ("issued", "Issued"),
            ("quarantined", "Quarantined"),
            ("scrapped", "Scrapped"),
            ("returned", "Returned to Vendor"),
            ("in_transit", "In Transit"),
            ("staged", "Staged for Dispatch"),
            ("shipped", "Shipped"),
        ],
        required=True,
        default="in_stock",
        index=True,
    )
    received_on = fields.Date()
    warranty_until = fields.Date()
    source_ref = fields.Char(string="Source Reference")

    _qty_non_negative = models.Constraint("CHECK (qty >= 0)", "Lot quantity cannot be negative")

    def _fix_guarded_fields(self) -> set:
        # A06 audit M15-5/E85: a quarantined serial was set back in stock
        # with qty 50 through the Lot form. Lots move only with the ledger.
        return super()._fix_guarded_fields() | {
            "name",
            "part_id",
            "location_id",
            "qty",
            "status",
            "received_on",
        }

    @api.constrains("qty", "part_id")
    def _check_serial_is_one_unit(self):
        for lot in self:
            if lot.part_id.is_serialized and lot.qty > 1.0 + EPS:
                raise ValidationError(
                    "%s is serialized: serial %s is one unit, not %s."
                    % (lot.part_id.part_number, lot.name, lot.qty)
                )

    @api.model
    def _fix_find(self, part, name):
        return self.sudo().search([("part_id", "=", part.id), ("name", "=", name)], limit=1)

    def _fix_check_movable(self, part, location):
        """BRU-WMS-10 / M15-5: a serial moves only when it is this part's, in
        stock, at the location the movement leaves from."""
        self.ensure_one()
        lot = self.sudo()
        if lot.part_id != part:
            raise UserError("Serial %s is not a serial of %s." % (lot.name, part.part_number))
        if lot.status != "in_stock" or lot.location_id != location or (lot.qty or 0.0) < 1.0:
            raise UserError(
                "Serial %s is %s at %s, not in stock at %s: it cannot move."
                % (
                    lot.name,
                    dict(lot._fields["status"].selection).get(lot.status),
                    lot.location_id.code or "-",
                    location.code,
                )
            )

    def _fix_move(self, status, location=None, qty=None):
        """The serial follows its movement (system path: a technician or an
        approver holds no lot rights)."""
        vals = {"status": status}
        if location is not None:
            vals["location_id"] = location.id
        if qty is not None:
            vals["qty"] = qty
        self.sudo()._guarded().write(vals)


# =========================================================================
# Goods receipt
# =========================================================================
class FixStockReceipt(models.Model):
    """Goods receipt with the inspection gate (accepted / rejected)."""

    _name = "fix.stock.receipt"
    _description = "Goods Receipt"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, ondelete="restrict"
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Receiving Location", required=True, ondelete="restrict"
    )
    ownership_class = fields.Selection(
        OWNERSHIP_CLASSES,
        string="Ownership Class",
        required=True,
        default="owned",
        help="The class the goods are received into: brand consignment and customer "
        "property are held stock, never valued (BRU-INV-02/05).",
    )
    purchase_order_id = fields.Many2one(
        "fix.purchase.order", string="Purchase Order", index=True, ondelete="restrict"
    )
    source_model = fields.Char(string="Source Document Model", index=True)
    source_res_id = fields.Integer(string="Source Document ID", index=True)
    source_ref = fields.Char(string="Source Reference", index=True)
    direct_reason = fields.Char(
        string="Reason (no purchase order)",
        help="Why these goods are received with no purchase order: an Inventory Controller "
        "posts such a receipt, on this recorded reason or source reference (A06 M15-9).",
    )
    received_on = fields.Date(required=True, default=fields.Date.context_today)
    inspection_notes = fields.Char()
    state = fields.Selection(
        [("draft", "Draft"), ("inspected", "Inspected"), ("posted", "Posted")],
        required=True,
        default="draft",
    )
    inspected_by_id = fields.Many2one("res.users", string="Inspected By", readonly=True)
    inspected_at = fields.Datetime(string="Inspected On", readonly=True)
    posted_by_id = fields.Many2one("res.users", string="Posted By", readonly=True)
    posted_at = fields.Datetime(string="Posted On", readonly=True)
    line_ids = fields.One2many("fix.stock.receipt.line", "receipt_id", string="Lines")

    _DOC_FIELDS = (
        "partner_id",
        "location_id",
        "ownership_class",
        "purchase_order_id",
        "received_on",
        "company_id",
        "source_model",
        "source_res_id",
        "source_ref",
        "direct_reason",
    )

    def _fix_guarded_fields(self) -> set:
        # source_model / source_res_id mark a system hand-off (M16, M44, M14),
        # which is exempt from the direct-receipt rule: never typed by a user.
        return super()._fix_guarded_fields() | {
            "state",
            "inspected_by_id",
            "inspected_at",
            "posted_by_id",
            "posted_at",
            "source_model",
            "source_res_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(self._DOC_FIELDS) | {"line_ids"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.stock.receipt") or "GRN/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in self._DOC_FIELDS if k in vals}
            if (frozen and _changes(self.filtered(lambda r: r.state != "draft"), frozen)) or (
                "line_ids" in vals and self.filtered(lambda r: r.state != "draft")
            ):
                raise UserError(
                    "An inspected or posted goods receipt is final: correct it with a new "
                    "receipt, a return to vendor or a count."
                )
        return super().write(vals)

    @api.constrains("purchase_order_id", "partner_id")
    def _check_po_partner(self):
        for rec in self:
            po = rec.purchase_order_id.sudo()
            vendor = po.vendor_id if "vendor_id" in po._fields else po.browse()
            if vendor and vendor.commercial_partner_id != rec.partner_id.commercial_partner_id:
                raise ValidationError(
                    "Receipt %s is from %s but purchase order %s is with %s."
                    % (rec.name, rec.partner_id.name, po.display_name, vendor.name)
                )

    # ---- A06 final pass B3 / M15-9: where a manual receipt's goods come from ----
    def _is_system_handoff(self) -> bool:
        """M16 goods receipt, M44 import, M14 harvest: their own module already
        checked the quantity and set the cost (M44's provisional landed cost
        must not be replaced by the PO price)."""
        self.ensure_one()
        return bool(self.source_model)

    def _check_source(self):
        """A receipt names its purchase order, or records why it has none."""
        self.ensure_one()
        if self._is_system_handoff() or self.env.su:
            return
        if self.purchase_order_id:
            self._check_against_po()
            return
        if not (self.direct_reason or "").strip() and not (self.source_ref or "").strip():
            raise UserError(
                "Receipt %s names no purchase order: record the reason or the source "
                "document before it is inspected or posted." % self.name
            )
        retired = self.line_ids.mapped("part_id").filtered(lambda p: p.state != "active")
        if retired:
            raise UserError(
                "%s is no longer purchased (%s): new stock of it needs an open purchase "
                "order." % (retired[:1].part_number, retired[:1].state)
            )

    def _po_lines_for(self, part):
        self.ensure_one()
        product = part.sudo().product_id
        order = self.purchase_order_id.sudo()
        return order.line_ids.filtered(lambda ln: product and ln.product_id == product)

    def _check_against_po(self):
        """The accepted quantity of each part stays within what the purchase
        order still has open across its posted M15 receipts."""
        self.ensure_one()
        order = self.purchase_order_id.sudo()
        if order.state not in RECEIPT_PO_STATES:
            raise UserError(
                "Purchase order %s is %s: goods are received only against an issued order."
                % (order.name, order.state)
            )
        Line = self.env["fix.stock.receipt.line"].sudo()
        for part in self.line_ids.mapped("part_id"):
            po_lines = self._po_lines_for(part)
            if not po_lines:
                raise UserError(
                    "Purchase order %s does not order %s (map the part to its purchased "
                    "product if it does)." % (order.name, part.part_number)
                )
            ordered = sum(po_lines.mapped("qty_ordered"))
            done = sum(
                Line.search(
                    [
                        ("part_id", "=", part.id),
                        ("is_posted", "=", True),
                        ("receipt_id.purchase_order_id", "=", order.id),
                        ("receipt_id", "!=", self.id),
                    ]
                ).mapped("qty_accepted")
            )
            accepted = sum(
                self.line_ids.filtered(lambda ln, p=part: ln.part_id == p).mapped("qty_accepted")
            )
            if accepted > ordered - done + EPS:
                raise UserError(
                    "Purchase order %s has %s of %s open; this receipt accepts %s."
                    % (order.name, round(ordered - done, 4), part.part_number, accepted)
                )

    def _po_unit_cost(self, part):
        """The price the order was approved at, in the company's currency
        (several lines of one part: their weighted average)."""
        self.ensure_one()
        po_lines = self._po_lines_for(part)
        company = self.company_id
        total = qty = 0.0
        for line in po_lines:
            price = line.unit_price or 0.0
            currency = line.currency_id
            if currency and company.currency_id and currency != company.currency_id:
                price = currency._convert(
                    price, company.currency_id, company, fields.Date.context_today(self)
                )
            total += price * (line.qty_ordered or 0.0)
            qty += line.qty_ordered or 0.0
        return round(total / qty, 4) if qty else 0.0

    def _line_cost(self, line):
        """What a posted line is valued at. A PO receipt takes the PO's price,
        never a typed one; a direct receipt the cost a cost-viewer typed, else
        the part's average or standard cost; a system hand-off its own."""
        self.ensure_one()
        row = line.sudo()
        if self._is_system_handoff():
            return row.unit_cost or 0.0
        master = row.part_id
        if self.purchase_order_id and (self._po_lines_for(master) or not self.env.su):
            cost = self._po_unit_cost(master)
        else:
            cost = row.unit_cost or master.average_cost or master.unit_cost or 0.0
        if abs((row.unit_cost or 0.0) - cost) > EPS:
            row._guarded().write({"unit_cost": cost})
        return cost

    def action_inspect(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Inspect a draft receipt")
            if not rec.line_ids:
                raise UserError("A receipt needs at least one line")
            rec._check_source()
            if any(line.qty_accepted <= 0 for line in rec.line_ids):
                raise UserError("The inspection gate requires an accepted quantity on every line")
            for line in rec.line_ids:
                check_quantity(line.part_id, line.qty_received, "received quantity")
                check_quantity(line.part_id, line.qty_accepted, "accepted quantity")
            rec._guarded().write(
                {
                    "state": "inspected",
                    "inspected_by_id": self.env.user.id,
                    "inspected_at": fields.Datetime.now(),
                }
            )
        return True

    def action_post(self):
        Onhand = self.env["fix.stock.onhand"]
        Lots = self.env["fix.stock.lot"]
        Suspense = self.env["fix.inventory.valuation.suspense"]
        for rec in self:
            if rec.state != "inspected":
                raise UserError("Post an inspected receipt")
            rec._check_source()
            if (
                not self.env.su
                and not rec._is_system_handoff()
                and not rec.purchase_order_id
                and not self.env.user.has_group(CONTROLLER_GROUP)
            ):
                raise AccessError(
                    "Receipt %s names no purchase order: only an Inventory Controller posts "
                    "a direct receipt." % rec.name
                )
            check_location_usable(rec.location_id, self.env)
            cls = location_class(rec.location_id, rec.ownership_class)
            for line in rec.line_ids:
                part = line.part_id
                cost = rec._line_cost(line)
                rejected = round((line.qty_received or 0.0) - (line.qty_accepted or 0.0), 4)
                lot_vals = {}
                if part.is_serialized:
                    if not line.line_no:
                        raise UserError(
                            "%s is serialized: every receipt line needs its serial number."
                            % part.part_number
                        )
                    if abs((line.qty_received or 0.0) - 1.0) > EPS:
                        raise UserError(
                            "%s is serialized: one receipt line receives one serial (one "
                            "unit), not %s." % (part.part_number, line.qty_received)
                        )
                    if Lots._fix_find(part, line.line_no):
                        raise UserError(
                            "Serial %s of %s has already been received: a serial is "
                            "received once (BRU-INV-14)." % (line.line_no, part.part_number)
                        )
                Onhand._apply(part, rec.location_id, cls, line.qty_accepted, cost)
                Suspense._fix_post(
                    "receipt",
                    part,
                    line.qty_accepted,
                    cost,
                    rec.name,
                    location=rec.location_id,
                    ownership=cls,
                )
                if line.line_no:
                    lot = Lots._fix_find(part, line.line_no)
                    if lot:
                        lot._guarded().write(
                            {
                                "qty": (lot.qty or 0.0) + line.qty_accepted,
                                "location_id": rec.location_id.id,
                                "status": "in_stock",
                            }
                        )
                    else:
                        lot = Lots.sudo().create(
                            {
                                "name": line.line_no,
                                "company_id": rec.company_id.id,
                                "part_id": part.id,
                                "location_id": rec.location_id.id,
                                "qty": line.qty_accepted,
                                "received_on": rec.received_on,
                                "source_ref": rec.name,
                            }
                        )
                    lot_vals["lot_id"] = lot.id
                if rejected > EPS:
                    # R5: rejected quantity is held in quarantine, never dropped.
                    Onhand._apply(
                        part,
                        rec.location_id,
                        cls,
                        rejected,
                        cost,
                        status="quarantine",
                    )
                    Suspense._fix_post(
                        "receipt",
                        part,
                        rejected,
                        cost,
                        rec.name,
                        location=rec.location_id,
                        ownership=cls,
                    )
                    quarantine = (
                        self.env["fix.stock.quarantine"]
                        .sudo()
                        ._guarded()
                        .with_context(fix_quarantine_in_place=True)
                        .create(
                            {
                                "part_id": part.id,
                                "location_id": rec.location_id.id,
                                "company_id": rec.company_id.id,
                                "ownership_class": cls,
                                "qty": rejected,
                                "reason": "defective",
                                "notes": "Rejected at inspection of %s" % rec.name,
                                "source_ref": rec.name,
                            }
                        )
                    )
                    lot_vals["quarantine_id"] = quarantine.id
                lot_vals["is_posted"] = True
                line._guarded().write(lot_vals)
            rec._guarded().write(
                {
                    "state": "posted",
                    "posted_by_id": self.env.user.id,
                    "posted_at": fields.Datetime.now(),
                }
            )
            _event(
                self.env,
                "stock.received",
                "fix.stock.receipt",
                rec.id,
                {
                    "receipt": rec.name,
                    "location_id": rec.location_id.id,
                    "ownership_class": cls,
                    "purchase_order_id": rec.purchase_order_id.id or None,
                    "source_ref": rec.source_ref or None,
                    "lines": [
                        {
                            "part_id": line.part_id.id,
                            "accepted": line.qty_accepted,
                            "rejected": line.qty_rejected,
                            "unit_cost": line.sudo().unit_cost,
                        }
                        for line in rec.line_ids
                    ],
                },
            )
        return True


class FixStockReceiptLine(models.Model):
    _name = "fix.stock.receipt.line"
    _description = "Goods Receipt Line"
    _order = "receipt_id, id"
    _inherit = ["fix.guarded.mixin"]

    receipt_id = fields.Many2one("fix.stock.receipt", required=True, ondelete="cascade", index=True)
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    qty_received = fields.Float(string="Received")
    qty_accepted = fields.Float(string="Accepted")
    qty_rejected = fields.Float(string="Rejected", compute="_compute_rejected", store=True)
    line_no = fields.Char(string="Serial / Lot")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    unit_cost = fields.Monetary(string="Unit Cost", currency_field="currency_id", groups=COST_GROUP)
    source_line_ref = fields.Char(string="Source Line Reference")
    is_posted = fields.Boolean(string="Posted", readonly=True, copy=False)
    lot_id = fields.Many2one("fix.stock.lot", string="Lot Created", readonly=True, copy=False)
    quarantine_id = fields.Many2one(
        "fix.stock.quarantine", string="Rejected Qty Quarantine", readonly=True, copy=False
    )

    _qty_bounds = models.Constraint(
        "CHECK (qty_received >= 0 AND qty_accepted >= 0 AND qty_accepted <= qty_received)",
        "Accepted quantity must be between 0 and the received quantity",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"is_posted", "lot_id", "quarantine_id"}

    @api.depends("receipt_id.name", "part_id.part_number", "qty_accepted")
    def _compute_display_name(self):
        """A put-away picks its receipt line by this name (A06 final pass A3)."""
        for rec in self:
            rec.display_name = "%s / %s x %s" % (
                rec.receipt_id.name or "-",
                rec.part_id.part_number or "-",
                rec.qty_accepted,
            )

    @api.depends("qty_received", "qty_accepted")
    def _compute_rejected(self):
        for rec in self:
            rec.qty_rejected = round((rec.qty_received or 0.0) - (rec.qty_accepted or 0.0), 3)

    def _refuse_unless_draft(self, receipts):
        if not self._fix_guard_open() and receipts.filtered(lambda r: r.state != "draft"):
            raise UserError(
                "The lines of an inspected or posted goods receipt are final (A06 audit "
                "M15-9): correct it with a new receipt, an RTV or a count."
            )

    @api.model_create_multi
    def create(self, vals_list):
        ids = {v.get("receipt_id") for v in vals_list if v.get("receipt_id")}
        self._refuse_unless_draft(self.env["fix.stock.receipt"].browse(list(ids)))
        return super().create(vals_list)

    def write(self, vals):
        if self:
            self._refuse_unless_draft(self.mapped("receipt_id"))
        return super().write(vals)

    def unlink(self):
        self._refuse_unless_draft(self.mapped("receipt_id"))
        return super().unlink()


# =========================================================================
# Transfers
# =========================================================================
class FixStockTransfer(models.Model):
    """An inter-branch stock transfer: raise, approve, dispatch (in transit),
    receive. Raiser, approver, dispatcher and receiver are recorded; the
    approver is never the requester and the receiver never the dispatcher."""

    _name = "fix.stock.transfer"
    _description = "Stock Transfer"
    _order = "create_date desc, id desc"
    _inherit = ["fix.inventory.approval.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    from_location_id = fields.Many2one(
        "fix.stock.location", string="From", required=True, ondelete="restrict"
    )
    to_location_id = fields.Many2one(
        "fix.stock.location", string="To", required=True, ondelete="restrict"
    )
    requested_on = fields.Date(required=True, default=fields.Date.context_today)
    dispatched_on = fields.Date()
    received_on = fields.Date()
    dispatched_by_id = fields.Many2one("res.users", string="Dispatched By", readonly=True)
    received_by_id = fields.Many2one("res.users", string="Received By", readonly=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("approved", "Approved"),
            ("dispatched", "Dispatched"),
            ("discrepancy", "Received with Discrepancy"),
            ("received", "Received"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    line_ids = fields.One2many("fix.stock.transfer.line", "transfer_id", string="Lines")
    transfer_value = fields.Float(
        string="Transfer Value (BDT)",
        compute="_compute_transfer_value",
        store=False,
        groups=COST_GROUP,
    )
    discrepancy_resolution = fields.Selection(
        [
            ("found", "Found: delivered to the destination"),
            ("returned", "Returned to the sender's stock"),
            ("quarantine", "Quarantined at the sender for write-off"),
        ],
        string="Discrepancy Resolution",
        readonly=True,
        copy=False,
    )

    _different_locations = models.Constraint(
        "CHECK (from_location_id <> to_location_id)",
        "A transfer moves stock between two different locations",
    )

    _DOC_FIELDS = ("from_location_id", "to_location_id", "company_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "dispatched_on",
            "received_on",
            "dispatched_by_id",
            "received_by_id",
            "discrepancy_resolution",
        }

    def _inv_approver_groups(self) -> tuple:
        # spec section 13: R06 approves transfers
        return (*super()._inv_approver_groups(), APPROVER_BRANCH_GROUP)

    def _inv_excluded_users(self):
        # who dispatched or received a short transfer never closes it
        return super()._inv_excluded_users() | self.dispatched_by_id | self.received_by_id

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(self._DOC_FIELDS)
            if self.state != "dispatched":
                locked |= {"line_ids"}
        return locked

    def _fix_line_costs(self):
        """(quantity, unit cost at the source) of each line."""
        self.ensure_one()
        Onhand = self.env["fix.stock.onhand"]
        cls = location_class(self.from_location_id)
        rows = []
        for line in self.line_ids:
            bucket = Onhand._bucket(line.part_id, self.from_location_id, cls)
            cost = bucket.unit_cost if bucket else line.part_id.sudo().average_cost
            rows.append((line.qty or 0.0, cost or 0.0))
        return rows

    def _fix_cost_known(self) -> bool:
        """False when any line moves stock that carries no cost: its value is
        then unknown, which is not the same as small."""
        self.ensure_one()
        return all(cost > EPS for _qty, cost in self._fix_line_costs())

    @api.depends("line_ids.qty", "line_ids.part_id", "from_location_id")
    def _compute_transfer_value(self):
        for rec in self:
            rec.transfer_value = round(sum(q * c for q, c in rec._fix_line_costs()), 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.stock.transfer") or "TRF/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in self._DOC_FIELDS if k in vals}
            moving = self.filtered(lambda r: r.state != "draft")
            # the receiver records what arrived on a dispatched transfer's
            # existing lines (fix.stock.transfer.line.write allows nothing else)
            receiving = (
                "line_ids" in vals
                and all(r.state == "dispatched" for r in moving)
                and all(cmd[0] == 1 for cmd in vals["line_ids"])
            )
            if (frozen and _changes(moving, frozen)) or (
                "line_ids" in vals and moving and not receiving
            ):
                raise UserError(
                    "A submitted, approved or dispatched transfer is final: cancel it and "
                    "raise a new one."
                )
        return super().write(vals)

    def _require(self, states, what):
        for rec in self:
            if rec.state not in states:
                raise UserError(
                    "Transfer %s cannot %s: it is %s."
                    % (rec.name, what, dict(self._fields["state"].selection)[rec.state])
                )

    def _check_serial_lines(self):
        """BRU-WMS-10 / M15-11: a serialized part travels one serial per line."""
        self.ensure_one()
        seen = self.env["fix.stock.lot"]
        for line in self.line_ids:
            part = line.part_id
            if not part.is_serialized:
                continue
            if not line.lot_id or abs((line.qty or 0.0) - 1.0) > EPS:
                raise UserError(
                    "%s is serialized: transfer it one unit per line, naming the serial."
                    % part.part_number
                )
            if line.lot_id in seen:
                raise UserError("Serial %s is on this transfer twice." % line.lot_id.name)
            seen |= line.lot_id
            line.lot_id._fix_check_movable(part, self.from_location_id)

    def action_submit(self):
        self._require(("draft",), "be submitted")
        threshold = inv_param(self.env, PARAM_TRANSFER_THRESHOLD, 0.0)
        for rec in self:
            if not rec.line_ids:
                raise UserError("A transfer needs at least one line")
            for line in rec.line_ids:
                check_quantity(line.part_id, line.qty, "transfer quantity")
            rec._check_serial_lines()
            rec._inv_stamp_request()
            value = rec.sudo().transfer_value
            # Uncosted stock valued the transfer at BDT 0.00, inside any
            # threshold: every transfer auto-approved (2026-11-10 audit).
            if threshold > 0 and rec._fix_cost_known() and value <= threshold:
                # a known value below the configured threshold needs no second person
                rec._guarded().write(
                    {
                        "state": "approved",
                        "approval_note": "auto-approved: value %.2f within the threshold %.2f"
                        % (value, threshold),
                    }
                )
            else:
                rec._guarded().write({"state": "submitted"})
        return True

    def action_approve(self):
        self._require(("submitted",), "be approved")
        self._inv_check_approver()
        for rec in self.sudo():
            rec._inv_stamp_approval()
            rec._guarded().write({"state": "approved"})
        return True

    def action_reject(self):
        self._require(("submitted",), "be rejected")
        self._inv_check_approver()
        self.sudo()._guarded().write({"state": "cancelled"})
        return True

    def action_cancel(self):
        self._require(("draft", "submitted", "approved"), "be cancelled")
        self._guarded().write({"state": "cancelled"})
        return True

    def action_dispatch(self):
        """Move the lines out of the source into the source's IN-TRANSIT
        bucket, at the source's average cost (BRU-INV-16: the sender keeps the
        value until receipt)."""
        Onhand = self.env["fix.stock.onhand"]
        for rec in self:
            if rec.state != "approved":
                if rec.state == "draft" and not rec.line_ids:
                    raise UserError("A transfer needs at least one line")
                raise UserError(
                    "Dispatch an approved transfer: submit it and have an Inventory "
                    "Controller approve it first."
                )
            if not rec.line_ids:
                raise UserError("A transfer needs at least one line")
            check_location_usable(rec.from_location_id, self.env)
            rec._check_serial_lines()
            cls = location_class(rec.from_location_id)
            for line in rec.line_ids:
                Onhand._fix_check_bins(line.part_id, rec.from_location_id, line.qty)
                cost = Onhand._fix_move_status(
                    line.part_id, rec.from_location_id, cls, line.qty, "unrestricted", "in_transit"
                )
                line.sudo()._guarded().write(
                    {"unit_cost": cost, "is_dispatched": True, "received_qty": line.qty}
                )
                if line.lot_id:
                    # the sender keeps it (BRU-INV-16), but it is on the road
                    line.lot_id._fix_move("in_transit")
            rec._guarded().write(
                {
                    "state": "dispatched",
                    "dispatched_on": fields.Date.context_today(self),
                    "dispatched_by_id": self.env.user.id,
                }
            )
        return True

    def action_receive(self):
        Onhand = self.env["fix.stock.onhand"]
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Receive a dispatched transfer")
            if not self.env.su and rec.dispatched_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you dispatched %s, so a different person must "
                    "receive it." % rec.name
                )
            check_location_usable(rec.to_location_id, self.env)
            src_cls = location_class(rec.from_location_id)
            dst_cls = location_class(rec.to_location_id)
            discrepancies = []
            moved = []
            for line in rec.line_ids:
                # A06 final pass B15: what arrived, not what was sent. The short
                # quantity stays in transit, the sender's (BRU-INV-16), until
                # the discrepancy is resolved.
                arrived = line._received_quantity()
                check_quantity(line.part_id, arrived, "received quantity", allow_zero=True)
                short = round((line.qty or 0.0) - arrived, 4)
                if line.is_dispatched:
                    cost = line.sudo().unit_cost
                    if arrived > EPS:
                        Onhand._apply(
                            line.part_id,
                            rec.from_location_id,
                            src_cls,
                            -arrived,
                            status="in_transit",
                        )
                else:
                    # dispatched before the in-transit ledger existed: the stock
                    # never left the source bucket, take it from there
                    source = Onhand._bucket(line.part_id, rec.from_location_id, src_cls)
                    cost = source.unit_cost if source else 0.0
                    if arrived > EPS:
                        Onhand._apply(line.part_id, rec.from_location_id, src_cls, -arrived)
                if arrived > EPS:
                    Onhand._apply(line.part_id, rec.to_location_id, dst_cls, arrived, cost)
                    if line.lot_id:
                        line.lot_id._fix_move("in_stock", rec.to_location_id)
                line.sudo()._guarded().write(
                    {"received_qty": arrived, "discrepancy_qty": short if line.is_dispatched else 0}
                )
                moved.append({"part_id": line.part_id.id, "sent": line.qty, "received": arrived})
                if short > EPS and line.is_dispatched:
                    discrepancies.append(
                        {"part_id": line.part_id.id, "short": short, "unit_cost": cost}
                    )
            rec._guarded().write(
                {
                    "state": "discrepancy" if discrepancies else "received",
                    "received_on": fields.Date.context_today(self),
                    "received_by_id": self.env.user.id,
                }
            )
            publish(
                self.env,
                "stock.transfer_received",
                "fix.stock.transfer",
                rec.id,
                {
                    "transfer": rec.name,
                    "from_location_id": rec.from_location_id.id,
                    "to_location_id": rec.to_location_id.id,
                    "lines": moved,
                    "discrepancies": discrepancies,
                },
            )
        return True

    def action_resolve_discrepancy(self, resolution=None, note=None):
        """AUT-INV-17: an approver who neither dispatched nor received it closes
        a short transfer: the missing quantity was found (it goes on to the
        destination), came back to the sender, or goes to quarantine at the
        sender, from where its write-off follows the normal approval."""
        resolution = (resolution or "").strip().lower()
        if resolution not in TRANSFER_RESOLUTIONS:
            raise UserError("Give the resolution: %s." % ", ".join(TRANSFER_RESOLUTIONS))
        if not (note or "").strip():
            raise UserError("Record how the transfer discrepancy was resolved.")
        self._require(("discrepancy",), "have a discrepancy resolved")
        self._inv_check_approver()
        Onhand = self.env["fix.stock.onhand"]
        for rec in self.sudo():
            src_cls = location_class(rec.from_location_id)
            dst_cls = location_class(rec.to_location_id)
            for line in rec.line_ids.filtered(lambda ln: (ln.discrepancy_qty or 0.0) > EPS):
                short = line.discrepancy_qty
                part = line.part_id
                if resolution == "found":
                    Onhand._apply(part, rec.from_location_id, src_cls, -short, status="in_transit")
                    Onhand._apply(part, rec.to_location_id, dst_cls, short, line.unit_cost)
                    if line.lot_id:
                        line.lot_id._fix_move("in_stock", rec.to_location_id)
                elif resolution == "returned":
                    Onhand._fix_move_status(
                        part, rec.from_location_id, src_cls, short, "in_transit", "unrestricted"
                    )
                    if line.lot_id:
                        line.lot_id._fix_move("in_stock")
                else:
                    Onhand._fix_move_status(
                        part, rec.from_location_id, src_cls, short, "in_transit", "quarantine"
                    )
                    if line.lot_id:
                        line.lot_id._fix_move("quarantined")
                    self.env["fix.stock.quarantine"].sudo()._guarded().with_context(
                        fix_quarantine_in_place=True
                    ).create(
                        {
                            "part_id": part.id,
                            "location_id": rec.from_location_id.id,
                            "company_id": rec.company_id.id,
                            "ownership_class": src_cls,
                            "lot_id": line.lot_id.id or False,
                            "qty": short,
                            "reason": "damaged",
                            "notes": "Short on transfer %s: %s" % (rec.name, note),
                            "source_ref": rec.name,
                        }
                    )
            rec._inv_stamp_approval(note)
            rec._guarded().write({"state": "received", "discrepancy_resolution": resolution})
        return True


class FixStockTransferLine(models.Model):
    _name = "fix.stock.transfer.line"
    _description = "Stock Transfer Line"
    _order = "transfer_id, id"
    _inherit = ["fix.guarded.mixin"]

    transfer_id = fields.Many2one(
        "fix.stock.transfer", required=True, ondelete="cascade", index=True
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    qty = fields.Float(string="Quantity")
    lot_id = fields.Many2one(
        "fix.stock.lot",
        string="Serial",
        ondelete="restrict",
        help="The serial this line moves (required for a serialized part: one per line).",
    )
    unit_cost = fields.Float(
        string="Dispatch Cost (BDT)", readonly=True, copy=False, groups=COST_GROUP
    )
    is_dispatched = fields.Boolean(string="Dispatched", readonly=True, copy=False)
    received_qty = fields.Float(
        string="Received",
        copy=False,
        help="What physically arrived. Filled with the sent quantity at dispatch; the "
        "receiver corrects it before Receive when less arrived.",
    )
    discrepancy_qty = fields.Float(string="Short", readonly=True, copy=False)

    _qty_positive = models.Constraint("CHECK (qty > 0)", "Transfer quantity must be positive")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"unit_cost", "is_dispatched", "discrepancy_qty"}

    def _received_quantity(self):
        """What arrived. A line dispatched before the in-transit ledger existed
        was never put in transit and is taken whole."""
        self.ensure_one()
        return self.received_qty if self.is_dispatched else self.qty

    def _refuse_unless_draft(self, transfers):
        if not self._fix_guard_open() and transfers.filtered(lambda t: t.state != "draft"):
            raise UserError(
                "The lines of a submitted, approved or dispatched transfer are final "
                "(A06 audit M15-11)."
            )

    @api.model_create_multi
    def create(self, vals_list):
        ids = {v.get("transfer_id") for v in vals_list if v.get("transfer_id")}
        self._refuse_unless_draft(self.env["fix.stock.transfer"].browse(list(ids)))
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for line in self:
                changed = {
                    k
                    for k in vals
                    if k in self._fields and line._fix_guard_differs(k, vals[k], line[k])
                }
                if not changed:
                    continue
                transfer = line.transfer_id
                if transfer.state == "draft" and "received_qty" not in changed:
                    continue
                if transfer.state == "dispatched" and changed == {"received_qty"}:
                    # the receiver, never the dispatcher, records what arrived
                    if transfer.dispatched_by_id == self.env.user:
                        raise UserError(
                            "Segregation of duties: you dispatched %s, so a different person "
                            "records what arrived." % transfer.name
                        )
                    value = float(vals["received_qty"] or 0.0)
                    if value < 0 or value > (line.qty or 0.0) + EPS:
                        raise UserError(
                            "Received quantity %s must be between 0 and the %s sent; surplus "
                            "stock is found by a count." % (value, line.qty)
                        )
                    check_quantity(line.part_id, value, "received quantity", allow_zero=True)
                    continue
                if "received_qty" in changed and transfer.state != "dispatched":
                    raise UserError("The received quantity is recorded when the goods arrive.")
                self._refuse_unless_draft(transfer)
        return super().write(vals)

    def unlink(self):
        self._refuse_unless_draft(self.mapped("transfer_id"))
        return super().unlink()


# =========================================================================
# Blind counts
# =========================================================================
class FixStockCount(models.Model):
    """A blind cycle or full count at one location.

    The expected quantity is snapshotted by the system when each line is
    created and is hidden from the counter (fix.stock.count.snapshot is
    readable by Inventory Controllers only). Submitting compares the count
    with the snapshot: inside the tolerance it posts; outside it asks for a
    recount; a recount still outside needs a reason code and the approval of
    an Inventory Controller who is not the counter (BRU-INV-10/11/23)."""

    _name = "fix.stock.count"
    _description = "Stock Count"
    _order = "create_date desc, id desc"
    # BRU-INV-11: above the controller limit the adjustment is also a routed
    # DOFA approval (CFO) on its value
    _inherit = ["fix.inventory.writeoff.dofa.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    location_id = fields.Many2one(
        "fix.stock.location", string="Location", required=True, ondelete="restrict"
    )
    count_type = fields.Selection(
        [("cycle", "Cycle Count"), ("full", "Full Count")],
        required=True,
        default="cycle",
    )
    counted_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("draft", "Counting"),
            ("recount", "Recount Required"),
            ("to_approve", "Awaiting Approval"),
            ("to_dofa", "Awaiting DOFA Approval"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    counted_by_id = fields.Many2one("res.users", string="Counted By", readonly=True)
    recount_requested = fields.Boolean(string="Recount Requested", readonly=True, copy=False)
    submitted_at = fields.Datetime(string="Submitted On", readonly=True)
    posted_at = fields.Datetime(string="Posted On", readonly=True)
    reason_code = fields.Selection(COUNT_REASONS, string="Variance Reason")
    reason_note = fields.Char(string="Variance Explanation")
    # the counter sees neither (blind count), and cost is restricted anyway
    variance_value = fields.Float(
        string="Variance Value (BDT)",
        compute="_compute_variance_value",
        store=False,
        groups=COST_GROUP,
        help="Gains less losses, at the cost when each line was snapshotted.",
    )
    adjustment_value = fields.Float(
        string="Adjustment Value (BDT)",
        compute="_compute_variance_value",
        store=False,
        groups=COST_GROUP,
        help="Gains plus losses: the value the approval matrix decides on (BRU-INV-11).",
    )
    line_ids = fields.One2many("fix.stock.count.line", "count_id", string="Lines")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "counted_by_id",
            "recount_requested",
            "submitted_at",
            "posted_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state not in ("draft", "recount"):
            locked |= {"location_id", "count_type", "counted_on", "line_ids", "reason_code"}
        if len(self) == 1 and self.state != "draft":
            locked |= {"location_id"}
        return locked

    def _inv_excluded_users(self):
        # SOD-05: the counter never approves the adjustment from his count.
        return super()._inv_excluded_users() | self.counted_by_id

    def _inv_approver_groups(self) -> tuple:
        # spec section 13: R06 variance resolution, R26 adjustments
        return (*super()._inv_approver_groups(), APPROVER_BRANCH_GROUP, APPROVER_FINANCE_GROUP)

    @api.depends("line_ids.counted_qty", "line_ids.recount_qty", "state")
    def _compute_variance_value(self):
        for rec in self:
            rows = [
                (line._line_delta(), line._snapshot().unit_cost or 0.0) for line in rec.line_ids
            ]
            rec.variance_value = round(sum(delta * cost for delta, cost in rows), 2)
            rec.adjustment_value = round(sum(abs(delta) * cost for delta, cost in rows), 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.stock.count") or "CNT/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            closed = self.filtered(lambda r: r.state not in ("draft", "recount"))
            frozen = {
                k: vals[k]
                for k in ("location_id", "count_type", "counted_on", "reason_code", "reason_note")
                if k in vals
            }
            if (frozen and _changes(closed, frozen)) or ("line_ids" in vals and closed):
                raise UserError("A submitted or posted count is final.")
            if "location_id" in vals and _changes(
                self.filtered(lambda r: r.line_ids), {"location_id": vals["location_id"]}
            ):
                raise UserError("Start a new count to count another location.")
        return super().write(vals)

    def _tolerance_ok(self, line):
        pct = inv_param(self.env, PARAM_COUNT_TOLERANCE_PCT, 0.0)
        expected = line._snapshot().expected_qty
        delta = abs(line._line_delta())
        if delta <= EPS:
            return True
        return delta <= abs(expected) * pct / 100.0 + EPS

    def action_submit(self):
        """The counter submits. Inside tolerance -> posted. Outside -> recount
        (first time) or approval (after the recount, with a reason code)."""
        for rec in self:
            if rec.state not in ("draft", "recount"):
                raise UserError("Count %s has already been submitted." % rec.name)
            if not rec.line_ids:
                raise UserError("A count needs at least one line")
            check_location_usable(rec.location_id, self.env)
            for line in rec.line_ids:
                check_quantity(line.part_id, line.counted_qty, "counted quantity", allow_zero=True)
                if rec.state == "recount":
                    check_quantity(
                        line.part_id, line.recount_qty, "recounted quantity", allow_zero=True
                    )
            now = fields.Datetime.now()
            if rec.state == "draft":
                rec._guarded().write({"counted_by_id": self.env.user.id, "submitted_at": now})
            outside = rec.line_ids.filtered(lambda ln, r=rec: not r._tolerance_ok(ln))
            if not outside:
                rec._post_count()
                continue
            if rec.state == "draft":
                for line in rec.line_ids:
                    line._guarded().write({"recount_qty": line.counted_qty})
                rec._guarded().write({"state": "recount", "recount_requested": True})
                continue
            if not rec.reason_code:
                raise UserError(
                    "Count %s is still outside tolerance after the recount: give the "
                    "variance reason before submitting it for approval." % rec.name
                )
            if rec.reason_code == "other" and not (rec.reason_note or "").strip():
                raise UserError("Explain an 'Other' variance reason in the note.")
            rec._inv_stamp_request()
            rec._guarded().write({"state": "to_approve"})
        return True

    def action_post(self):
        """Kept for the workspace button: a draft or recount is submitted, a
        count awaiting approval is approved (both apply their own checks)."""
        for rec in self:
            if rec.state in ("draft", "recount"):
                rec.action_submit()
            elif rec.state == "to_approve":
                rec.action_approve()
            elif rec.state == "to_dofa":
                raise UserError(
                    "Count %s awaits its DOFA approval in the approver's inbox." % rec.name
                )
            else:
                raise UserError("Post a draft count")
        return True

    def _writeoff_value(self) -> float:
        """The value the adjustment moves: every line's variance at its
        snapshot cost, gains and losses alike."""
        self.ensure_one()
        return round(
            sum(
                abs(line._line_delta()) * (line._snapshot().unit_cost or 0.0)
                for line in self.line_ids
            ),
            2,
        )

    def action_approve(self, note=None):
        for rec in self:
            if rec.state != "to_approve":
                raise UserError("Count %s is not awaiting approval." % rec.name)
        self._inv_check_approver()
        for rec in self.sudo():
            rec._inv_stamp_approval(note)
            if rec._inv_needs_dofa():
                # above the controller's limit: the CFO decides it in M63 too
                rec._guarded().write({"state": "to_dofa"})
                rec._inv_route_dofa(
                    "Count %s: variance of BDT %.2f at %s (%s). %s"
                    % (
                        rec.name,
                        rec._writeoff_value(),
                        rec.location_id.code,
                        dict(self._fields["reason_code"].selection).get(rec.reason_code, "-"),
                        rec.reason_note or "",
                    )
                )
            else:
                rec._post_count()
        return True

    @api.depends("state", "line_ids.counted_qty", "line_ids.recount_qty")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _inv_dofa_apply(self):
        for rec in self.filtered(lambda r: r.state == "to_dofa"):
            rec._post_count()

    def _approval_on_rejected(self, comment):
        # the rejecting approver need not hold store rights on the record
        for rec in self.sudo().filtered(lambda r: r.state == "to_dofa"):
            rec._guarded().write({"state": "cancelled"})
            rec.line_ids.mapped("floor_count_id")._fix_cancel_from_m15()

    def action_reject(self, note=None):
        for rec in self:
            if rec.state != "to_approve":
                raise UserError("Count %s is not awaiting approval." % rec.name)
        self._inv_check_approver()
        for rec in self.sudo():
            rec._inv_stamp_approval(note or "rejected")
            rec._guarded().write({"state": "cancelled"})
            rec.line_ids.mapped("floor_count_id")._fix_cancel_from_m15()
        return True

    def _post_count(self):
        """Apply every line's variance to the ledger (system path)."""
        self.ensure_one()
        Onhand = self.env["fix.stock.onhand"]
        Suspense = self.env["fix.inventory.valuation.suspense"]
        moved = []
        for line in self.line_ids:
            delta = round(line._line_delta(), 4)
            snap = line._snapshot()
            if abs(delta) > EPS:
                bucket = Onhand._apply(
                    line.part_id,
                    self.location_id,
                    line.ownership_class,
                    delta,
                    unit_cost=None,
                    from_reserved=True,
                )
                cost = bucket.sudo().unit_cost if bucket else snap.unit_cost
                Suspense._fix_post(
                    "adjustment",
                    line.part_id,
                    delta,
                    cost,
                    self.name,
                    location=self.location_id,
                    ownership=line.ownership_class,
                )
                moved.append({"part_id": line.part_id.id, "delta": delta, "unit_cost": cost})
            if line.floor_count_id:
                line.floor_count_id._fix_apply_posted_variance(delta)
            line._guarded().write({"is_posted": True})
        self._guarded().write({"state": "posted", "posted_at": fields.Datetime.now()})
        if moved:
            _event(
                self.env,
                "stock.adjusted",
                "fix.stock.count",
                self.id,
                {
                    "count": self.name,
                    "location_id": self.location_id.id,
                    "reason_code": self.reason_code or None,
                    "approved_by": self.approved_by_id.id or None,
                    "lines": moved,
                },
            )


class FixStockCountSnapshot(models.Model):
    """The system's expected quantity for one count line, taken when the line
    was created. Readable by Inventory Controllers only: the count is blind."""

    _name = "fix.stock.count.snapshot"
    _description = "Stock Count Expected Snapshot"

    line_id = fields.Many2one("fix.stock.count.line", required=True, ondelete="cascade", index=True)
    expected_qty = fields.Float(string="Expected", readonly=True)
    unit_cost = fields.Float(string="Unit Cost at Snapshot", readonly=True)
    taken_at = fields.Datetime(readonly=True, default=fields.Datetime.now)

    _line_unique = models.Constraint("UNIQUE (line_id)", "One snapshot per count line")


class FixStockCountLine(models.Model):
    _name = "fix.stock.count.line"
    _description = "Stock Count Line"
    _order = "count_id, id"
    _inherit = ["fix.guarded.mixin"]

    count_id = fields.Many2one("fix.stock.count", required=True, ondelete="cascade", index=True)
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    ownership_class = fields.Selection(
        OWNERSHIP_CLASSES,
        string="Ownership Class",
        help="Defaults to the location's own class (owned, or van at a van).",
    )
    expected_qty = fields.Float(
        string="Expected",
        compute="_compute_expected",
        help="The system's quantity when the line was created. Hidden from the counter "
        "until the count is posted (blind count, FR-INV-048).",
    )
    expected_visible = fields.Boolean(compute="_compute_expected")
    counted_qty = fields.Float(string="Counted")
    recount_qty = fields.Float(string="Recounted")
    variance = fields.Float(compute="_compute_expected", string="Variance")
    is_posted = fields.Boolean(string="Posted", readonly=True, copy=False)
    floor_count_id = fields.Many2one(
        "fix.wms.floor.count", string="Floor Count", readonly=True, copy=False, index=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"is_posted", "floor_count_id"}

    def _snapshot(self):
        self.ensure_one()
        snap = (
            self.env["fix.stock.count.snapshot"].sudo().search([("line_id", "=", self.id)], limit=1)
        )
        return snap

    def _final_qty(self):
        """The recount replaces the first count once a recount was asked for."""
        self.ensure_one()
        return self.recount_qty if self.count_id.recount_requested else self.counted_qty

    def _line_delta(self):
        self.ensure_one()
        if not self.id:
            return 0.0
        return (self._final_qty() or 0.0) - (self._snapshot().expected_qty or 0.0)

    @api.depends_context("uid")
    @api.depends("counted_qty", "recount_qty", "count_id.state")
    def _compute_expected(self):
        # blind to the counter, also when the workspace reads the row as sudo:
        # the acting USER decides, not the sudo flag
        user = self.env.user
        sees = self.env.uid == SUPERUSER_ID or any(
            user.has_group(group)
            for group in (CONTROLLER_GROUP, APPROVER_BRANCH_GROUP, APPROVER_FINANCE_GROUP)
        )
        for line in self:
            visible = bool(line.id) and (sees or line.count_id.state in ("posted", "cancelled"))
            line.expected_visible = visible
            if visible:
                line.expected_qty = line._snapshot().expected_qty
                line.variance = round(line._line_delta(), 3)
            else:
                line.expected_qty = 0.0
                line.variance = 0.0

    def _refuse_unless_open(self, counts):
        if self._fix_guard_open():
            return
        if counts.filtered(lambda c: c.state != "draft"):
            raise UserError("The lines of a submitted or posted count are final (A06 audit M15-8).")

    def _take_snapshot(self):
        Onhand = self.env["fix.stock.onhand"]
        Snap = self.env["fix.stock.count.snapshot"].sudo()
        for line in self:
            bucket = Onhand._bucket(line.part_id, line.count_id.location_id, line.ownership_class)
            Snap.search([("line_id", "=", line.id)]).unlink()
            Snap.create(
                {
                    "line_id": line.id,
                    "expected_qty": bucket.qty if bucket else 0.0,
                    "unit_cost": (bucket.unit_cost if bucket else 0.0)
                    or line.part_id.sudo().average_cost,
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        Count = self.env["fix.stock.count"]
        ids = {v.get("count_id") for v in vals_list if v.get("count_id")}
        self._refuse_unless_open(Count.browse(list(ids)))
        for vals in vals_list:
            # the expected quantity is the system's, never typed
            vals.pop("expected_qty", None)
            vals.pop("variance", None)
            vals.pop("recount_qty", None)
            if not vals.get("ownership_class") and vals.get("count_id"):
                vals["ownership_class"] = location_class(Count.browse(vals["count_id"]).location_id)
        lines = super().create(vals_list)
        lines._take_snapshot()
        return lines

    def write(self, vals):
        vals = dict(vals)
        vals.pop("expected_qty", None)
        vals.pop("variance", None)
        if self and not self._fix_guard_open():
            guarded = self._fix_guarded_fields()
            for line in self:
                state = line.count_id.state
                # guarded fields are refused by the guard itself (super)
                keys = {
                    k
                    for k in vals
                    if k not in guarded and line._fix_guard_differs(k, vals[k], line[k])
                }
                if not keys:
                    continue
                if state == "draft" and "recount_qty" not in keys:
                    continue
                if state == "recount" and keys <= {"recount_qty"}:
                    continue
                raise UserError(
                    "Count %s: the first count is entered while counting, the recount only "
                    "when a recount is asked for, and a submitted or posted count is final "
                    "(A06 audit M15-8)." % line.count_id.name
                )
        result = super().write(vals)
        if {"part_id", "ownership_class"} & set(vals):
            self._take_snapshot()
        return result

    def unlink(self):
        self._refuse_unless_open(self.mapped("count_id"))
        return super().unlink()

    def action_set_recount(self, qty):
        """The counter records his recount of this line (recount state)."""
        for line in self:
            if line.count_id.state != "recount":
                raise UserError("Count %s does not ask for a recount." % line.count_id.name)
            check_quantity(line.part_id, qty, "recounted quantity", allow_zero=True)
            line.write({"recount_qty": qty})
        return True


# =========================================================================
# Van reconciliation
# =========================================================================
class FixStockVanRecon(models.Model):
    """The technician's daily van-stock reconciliation.

    The expected quantity is the van's ledger when the recon is raised (never
    typed). A variance outside the tolerance is a discrepancy: it publishes
    stock.van_variance_detected and holds the van's next issue until an
    Inventory Controller (not the technician, not the counter) resolves it.
    The per-part ledger correction is a count at the van."""

    _name = "fix.stock.van.recon"
    _description = "Van Stock Reconciliation"
    _order = "recon_date desc, id desc"
    _inherit = ["fix.inventory.approval.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Van Location", required=True, ondelete="restrict"
    )
    technician_id = fields.Many2one("hr.employee", string="Technician")
    recon_date = fields.Date(required=True, default=fields.Date.context_today)
    # BRU-INV-12 / M15-8: the count is blind. The technician sees neither what
    # the van should hold nor how far off he is, only the outcome (state).
    expected_qty = fields.Float(string="Expected (pcs)", readonly=True, groups=VAN_VARIANCE_GROUPS)
    counted_qty = fields.Float(string="Counted (pcs)")
    variance = fields.Float(
        compute="_compute_variance", store=True, string="Variance", groups=VAN_VARIANCE_GROUPS
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("discrepancy", "Discrepancy"),
            ("resolved", "Discrepancy Resolved"),
        ],
        required=True,
        default="draft",
    )
    confirmed_by_id = fields.Many2one("res.users", string="Confirmed By", readonly=True)
    notes = fields.Char()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "expected_qty", "confirmed_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= {"location_id", "technician_id"}
            if self.state != "draft":
                locked |= {"counted_qty", "recon_date"}
        return locked

    def _inv_excluded_users(self):
        return super()._inv_excluded_users() | self.confirmed_by_id | self.technician_id.user_id

    def _inv_approver_groups(self) -> tuple:
        # spec section 13: R06 variance resolution
        return (*super()._inv_approver_groups(), APPROVER_BRANCH_GROUP)

    @api.depends("expected_qty", "counted_qty")
    def _compute_variance(self):
        for rec in self:
            rec.variance = round((rec.counted_qty or 0.0) - (rec.expected_qty or 0.0), 3)

    @api.model
    def _van_ledger_qty(self, location):
        rows = (
            self.env["fix.stock.onhand"]
            .sudo()
            .search([("location_id", "=", location.id), ("stock_status", "=", "unrestricted")])
        )
        return round(sum(rows.mapped("qty")), 4)

    @api.model_create_multi
    def create(self, vals_list):
        Location = self.env["fix.stock.location"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.stock.van.recon") or "VRC/New"
                )
            location = Location.browse(vals.get("location_id"))
            if not location or location.location_type != "van":
                raise ValidationError(
                    "A van reconciliation is for a van location (got %s)."
                    % (location.code if location else "none")
                )
            if not vals.get("technician_id"):
                vals["technician_id"] = location.technician_id.id
            elif vals["technician_id"] != location.technician_id.id:
                raise ValidationError(
                    "Van %s is in the custody of %s: only its custodian is reconciled."
                    % (location.code, location.technician_id.name or "nobody")
                )
            # the expected quantity is the van ledger, never typed (FR-INV-031)
            vals.pop("expected_qty", None)
        records = super().create(vals_list)
        for rec in records:
            rec.sudo()._guarded().write({"expected_qty": self._van_ledger_qty(rec.location_id)})
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in ("location_id", "technician_id") if k in vals}
            if frozen and _changes(self, frozen):
                raise UserError("Raise a new reconciliation for another van or technician.")
            closed = self.filtered(lambda r: r.state != "draft")
            later = {k: vals[k] for k in ("counted_qty", "recon_date") if k in vals}
            if later and _changes(closed, later):
                raise UserError(
                    "A confirmed van reconciliation is final: its count cannot be retyped."
                )
        return super().write(vals)

    def action_confirm(self):
        pct = inv_param(self.env, PARAM_VAN_TOLERANCE_PCT, 0.0)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Reconciliation %s has already been confirmed." % rec.name)
            if (rec.counted_qty or 0.0) < 0:
                raise UserError("A counted quantity cannot be negative.")
            # re-read the ledger at confirmation: what the van holds NOW
            expected = self._van_ledger_qty(rec.location_id)
            variance = round((rec.counted_qty or 0.0) - expected, 4)
            within = abs(variance) <= EPS or abs(variance) <= abs(expected) * pct / 100.0 + EPS
            rec.sudo()._guarded().write(
                {
                    "expected_qty": expected,
                    "state": "confirmed" if within else "discrepancy",
                    "confirmed_by_id": self.env.user.id,
                }
            )
            if not within:
                _event(
                    self.env,
                    "stock.van_variance_detected",
                    "fix.stock.van.recon",
                    rec.id,
                    {
                        "recon": rec.name,
                        "van_id": rec.location_id.id,
                        "van_code": rec.location_id.code,
                        "technician_id": rec.technician_id.id or None,
                        "expected_qty": expected,
                        "counted_qty": rec.counted_qty,
                        "variance": variance,
                    },
                )
        return True

    def action_resolve(self, note=None):
        """An Inventory Controller (not the technician or the counter)
        accepts the investigation of a discrepancy; the van may issue again."""
        for rec in self:
            if rec.state != "discrepancy":
                raise UserError("Reconciliation %s has no open discrepancy." % rec.name)
        if not (note or "").strip():
            raise UserError("Record how the van discrepancy was resolved.")
        self._inv_check_approver()
        for rec in self.sudo():
            rec._inv_stamp_approval(note)
            rec._guarded().write({"state": "resolved"})
        return True


# =========================================================================
# Quarantine / scrap
# =========================================================================
class FixStockQuarantine(models.Model):
    """A quarantined or scrapped quantity with its reason.

    Creating it MOVES the quantity from unrestricted to the quarantine status
    of the same location, so it can no longer be reserved or issued. Release
    moves it back; scrap writes it off. A write-off above the configured
    value needs an Inventory Controller who is not the quarantiner."""

    _name = "fix.stock.quarantine"
    _description = "Stock Quarantine / Scrap"
    _order = "create_date desc, id desc"
    # BRU-INV-24: a write-off above the controller limit is also a routed
    # DOFA approval (CFO) on its value
    _inherit = ["fix.inventory.writeoff.dofa.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="cascade", index=True
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Location", required=True, ondelete="restrict"
    )
    ownership_class = fields.Selection(OWNERSHIP_CLASSES, string="Ownership Class")
    lot_id = fields.Many2one("fix.stock.lot", string="Serial / Lot", ondelete="set null")
    qty = fields.Float(string="Quantity")
    unit_cost = fields.Float(string="Unit Cost (BDT)", readonly=True, groups=COST_GROUP)
    reason = fields.Selection(
        [
            ("damaged", "Damaged in Handling"),
            ("defective", "Defective / DOA"),
            ("expired", "Expired"),
            ("suspect", "Suspect Counterfeit"),
            ("customer_return", "Customer Return"),
        ],
        required=True,
        default="damaged",
    )
    quarantined_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("quarantined", "Quarantined"),
            ("released", "Released"),
            ("scrap_pending", "Write-off Awaiting Approval"),
            ("scrap_dofa", "Write-off Awaiting DOFA Approval"),
            ("scrapped", "Scrapped"),
            ("returned", "Returned to Vendor"),
        ],
        required=True,
        default="quarantined",
    )
    source_ref = fields.Char(string="Source Reference", readonly=True)
    scrapped_at = fields.Datetime(string="Scrapped On", readonly=True)
    notes = fields.Char()

    _qty_positive = models.Constraint("CHECK (qty > 0)", "Quarantine quantity must be positive")

    _DOC_FIELDS = ("part_id", "location_id", "lot_id", "qty", "ownership_class", "company_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "unit_cost",
            "source_ref",
            "scrapped_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= set(self._DOC_FIELDS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        in_place = self._fix_guard_has_token() and self.env.context.get("fix_quarantine_in_place")
        Location = self.env["fix.stock.location"]
        Part = self.env["fix.spare.part"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.stock.quarantine") or "QRN/New"
                )
            if not vals.get("ownership_class"):
                vals["ownership_class"] = location_class(Location.browse(vals.get("location_id")))
        records = super().create(vals_list)
        Onhand = self.env["fix.stock.onhand"]
        for rec in records:
            part = Part.browse(rec.part_id.id)
            check_quantity(part, rec.qty, "quarantine quantity")
            if in_place:
                bucket = Onhand._bucket(part, rec.location_id, rec.ownership_class, "quarantine")
                cost = bucket.unit_cost if bucket else 0.0
            else:
                check_location_usable(rec.location_id, self.env)
                rec._check_lot_for_quarantine()
                Onhand._fix_check_bins(part, rec.location_id, rec.qty)
                cost = Onhand._fix_move_status(
                    part,
                    rec.location_id,
                    rec.ownership_class,
                    rec.qty,
                    "unrestricted",
                    "quarantine",
                )
                if rec.lot_id and part.is_serialized:
                    rec.lot_id._fix_move("quarantined")
            rec.sudo()._guarded().write({"unit_cost": cost})
        return records

    def _check_lot_for_quarantine(self):
        for rec in self:
            lot = rec.lot_id
            if not lot:
                continue
            if lot.part_id != rec.part_id:
                raise ValidationError(
                    "Lot %s is not a lot of %s." % (lot.name, rec.part_id.part_number)
                )
            if lot.status != "in_stock":
                raise UserError("Lot %s is %s, not in stock." % (lot.name, lot.status))
            if rec.qty > (lot.qty or 0.0) + EPS:
                raise UserError(
                    "Lot %s holds %s; %s cannot be quarantined from it."
                    % (lot.name, lot.qty, rec.qty)
                )

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in self._DOC_FIELDS if k in vals}
            if frozen and _changes(self, frozen):
                raise UserError(
                    "A quarantine has already moved its stock: release it and raise a new "
                    "one instead of editing the part, location, lot or quantity."
                )
        return super().write(vals)

    def _require(self, states, what):
        for rec in self:
            if rec.state not in states:
                raise UserError(
                    "%s cannot %s: it is %s."
                    % (rec.name, what, dict(self._fields["state"].selection)[rec.state])
                )

    def _inv_excluded_users(self):
        # §13: the quarantiner never approves the write-off
        return super()._inv_excluded_users()

    def _inv_approver_groups(self) -> tuple:
        # spec section 13: R26 write-offs
        return (*super()._inv_approver_groups(), APPROVER_FINANCE_GROUP)

    def _writeoff_value(self):
        self.ensure_one()
        rec = self.sudo()
        return round((rec.qty or 0.0) * (rec.unit_cost or 0.0), 2)

    def action_release(self):
        Onhand = self.env["fix.stock.onhand"]
        for rec in self:
            if rec.state != "quarantined":
                raise UserError("Release a quarantined quantity")
            check_location_usable(rec.location_id, self.env)
            Onhand._fix_move_status(
                rec.part_id,
                rec.location_id,
                rec.ownership_class,
                rec.qty,
                "quarantine",
                "unrestricted",
            )
            if rec.lot_id and rec.lot_id.status == "quarantined":
                rec.lot_id._guarded().write({"status": "in_stock"})
            rec._guarded().write({"state": "released"})
        return True

    def action_scrap(self):
        """Scrap directly when the write-off has a known value within the
        configured threshold; above it, or with no cost recorded, the
        write-off needs approval first."""
        threshold = inv_param(self.env, PARAM_WRITEOFF_THRESHOLD, 0.0)
        for rec in self:
            if rec.state != "quarantined":
                raise UserError("Scrap a quarantined quantity")
            if rec._writeoff_value() <= EPS:
                # BDT 0.00 passed every threshold, the default 0 included, so
                # uncosted stock was scrapped by one person (2026-11-10 audit)
                raise UserError(
                    "%s has no unit cost recorded, so its value cannot be set against the "
                    "write-off approval threshold: request the write-off and have an "
                    "Inventory Controller approve it." % rec.name
                )
            if rec._writeoff_value() > threshold + EPS:
                raise UserError(
                    "Writing off %s is BDT %.2f, above the write-off approval threshold "
                    "BDT %.2f: request the write-off and have an Inventory Controller "
                    "approve it." % (rec.name, rec._writeoff_value(), threshold)
                )
            rec._do_scrap()
        return True

    def action_request_scrap(self):
        self._require(("quarantined",), "be submitted for write-off")
        for rec in self:
            rec._inv_stamp_request()
            rec._guarded().write({"state": "scrap_pending"})
        return True

    def action_approve_scrap(self, note=None):
        self._require(("scrap_pending",), "be approved for write-off")
        self._inv_check_approver()
        for rec in self.sudo():
            rec._inv_stamp_approval(note)
            if rec._inv_needs_dofa():
                rec._guarded().write({"state": "scrap_dofa"})
                rec._inv_route_dofa(
                    "Write-off %s: %s x %s = BDT %.2f (%s). %s"
                    % (
                        rec.name,
                        rec.qty,
                        rec.part_id.part_number,
                        rec._writeoff_value(),
                        dict(self._fields["reason"].selection).get(rec.reason),
                        rec.notes or "",
                    )
                )
            else:
                rec._do_scrap()
        return True

    @api.depends("state", "qty", "unit_cost")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _inv_dofa_apply(self):
        for rec in self.filtered(lambda r: r.state == "scrap_dofa"):
            rec._do_scrap()

    def _approval_on_rejected(self, comment):
        for rec in self.sudo().filtered(lambda r: r.state == "scrap_dofa"):
            rec._guarded().write({"state": "quarantined"})

    def action_reject_scrap(self, note=None):
        self._require(("scrap_pending",), "be rejected")
        self._inv_check_approver()
        for rec in self.sudo():
            rec._inv_stamp_approval(note or "write-off rejected")
            rec._guarded().write({"state": "quarantined"})
        return True

    def _do_scrap(self):
        self.ensure_one()
        Onhand = self.env["fix.stock.onhand"]
        cost = self.sudo().unit_cost
        Onhand._apply(
            self.part_id, self.location_id, self.ownership_class, -self.qty, status="quarantine"
        )
        lot = self.lot_id.sudo()
        if lot and self.part_id.is_serialized:
            lot._guarded().write({"qty": 0.0, "status": "scrapped"})
        elif lot:
            # scrapping part of a lot leaves the rest of it (A06 audit E61)
            remaining = round(max((lot.qty or 0.0) - self.qty, 0.0), 4)
            lot._guarded().write(
                {"qty": remaining, "status": "scrapped" if remaining <= EPS else "in_stock"}
            )
        self.env["fix.inventory.valuation.suspense"]._fix_post(
            "write_off",
            self.part_id,
            -self.qty,
            cost,
            self.name,
            location=self.location_id,
            ownership=self.ownership_class,
        )
        self._guarded().write({"state": "scrapped", "scrapped_at": fields.Datetime.now()})
        _event(
            self.env,
            "stock.written_off",
            "fix.stock.quarantine",
            self.id,
            {
                "quarantine": self.name,
                "part_id": self.part_id.id,
                "location_id": self.location_id.id,
                "qty": self.qty,
                "unit_cost": cost,
                "value": self._writeoff_value(),
                "reason": self.reason,
                "approved_by": self.approved_by_id.id or None,
            },
        )


# =========================================================================
# Return to vendor
# =========================================================================
class FixStockRtv(models.Model):
    """A return-to-vendor request for defective or wrong stock.

    Approved by an Inventory Controller who did not raise it; once approved
    the quantity, vendor, part, location and source are pinned. It ships only
    with the vendor's RMA reference and closes when the credit is recorded."""

    _name = "fix.stock.rtv"
    _description = "Return to Vendor"
    _order = "create_date desc, id desc"
    _inherit = ["fix.inventory.approval.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one("res.partner", string="Vendor", required=True, ondelete="restrict")
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="From Location", required=True, ondelete="restrict"
    )
    quarantine_id = fields.Many2one(
        "fix.stock.quarantine",
        string="From Quarantine",
        ondelete="restrict",
        help="Return quarantined stock (it ships from the quarantine status).",
    )
    lot_id = fields.Many2one(
        "fix.stock.lot",
        string="Serial",
        ondelete="restrict",
        help="The serial returned (required for a serialized part not sent from quarantine).",
    )
    qty = fields.Float(string="Quantity")
    reason = fields.Selection(
        [
            ("doa", "Dead on Arrival"),
            ("wrong_part", "Wrong Part Shipped"),
            ("warranty", "Warranty Claim"),
            ("quality", "Quality Defect"),
        ],
        required=True,
        default="doa",
    )
    requested_on = fields.Date(required=True, default=fields.Date.context_today)
    rtv_ref = fields.Char(string="RTV Reference")
    credit_ref = fields.Char(string="Credit Note / Replacement Ref")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("approved", "Approved"),
            ("shipped", "Shipped"),
            ("credited", "Credited / Closed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    unit_cost = fields.Float(string="Unit Cost (BDT)", readonly=True, groups=COST_GROUP)
    shipped_at = fields.Datetime(readonly=True)
    credited_at = fields.Datetime(readonly=True)
    vendor_note_res_id = fields.Integer(
        string="AP Credit Note ID",
        readonly=True,
        copy=False,
        help="The draft vendor credit note (fix.vendor.note, M20) raised for this RTV.",
    )
    vendor_note_status = fields.Char(string="AP Credit Note", readonly=True, copy=False)
    notes = fields.Char()

    _qty_positive = models.Constraint("CHECK (qty > 0)", "RTV quantity must be positive")

    _PINNED = (
        "partner_id",
        "part_id",
        "location_id",
        "quarantine_id",
        "lot_id",
        "qty",
        "company_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "unit_cost",
            "shipped_at",
            "credited_at",
            "credit_ref",
            "vendor_note_res_id",
            "vendor_note_status",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state not in ("draft",):
            locked |= set(self._PINNED) | {"reason"}
        if len(self) == 1 and self.state in ("shipped", "credited", "cancelled"):
            locked |= {"rtv_ref"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.stock.rtv") or "RTV/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            pinned = {k: vals[k] for k in (*self._PINNED, "reason") if k in vals}
            if pinned and _changes(self.filtered(lambda r: r.state != "draft"), pinned):
                raise UserError(
                    "An RTV submitted for or past approval is pinned: its vendor, part, "
                    "location and quantity cannot change (cancel it and raise a new one)."
                )
            if "rtv_ref" in vals and _changes(
                self.filtered(lambda r: r.state in ("shipped", "credited", "cancelled")),
                {"rtv_ref": vals["rtv_ref"]},
            ):
                raise UserError("The RMA reference of a shipped RTV is final.")
        return super().write(vals)

    def _require(self, states, what):
        for rec in self:
            if rec.state not in states:
                raise UserError(
                    "RTV %s cannot %s: it is %s."
                    % (rec.name, what, dict(self._fields["state"].selection)[rec.state])
                )

    def _source_status(self):
        self.ensure_one()
        return "quarantine" if self.quarantine_id else "unrestricted"

    def _check_serial(self):
        """M15-5: a serialized part leaving unrestricted stock names its serial
        (from quarantine the serial is the quarantine's)."""
        self.ensure_one()
        if self.quarantine_id or not self.part_id.is_serialized:
            return
        if not self.lot_id or abs((self.qty or 0.0) - 1.0) > EPS:
            raise UserError(
                "%s is serialized: return it one unit per RTV, naming the serial."
                % self.part_id.part_number
            )
        self.lot_id._fix_check_movable(self.part_id, self.location_id)

    def action_submit(self):
        self._require(("draft",), "be submitted")
        for rec in self:
            check_quantity(rec.part_id, rec.qty, "RTV quantity")
            if rec.quarantine_id and (
                rec.quarantine_id.state != "quarantined"
                or rec.quarantine_id.part_id != rec.part_id
                or rec.quarantine_id.location_id != rec.location_id
                or abs(rec.qty - rec.quarantine_id.qty) > EPS
            ):
                raise UserError("RTV %s does not match an open quarantine." % rec.name)
            rec._check_serial()
            rec._inv_stamp_request()
            rec._guarded().write({"state": "submitted"})
        return True

    def action_approve(self, note=None):
        # approving a draft submits it in its RAISER's name, never the approver's
        for draft in self.filtered(lambda r: r.state == "draft"):
            draft.action_submit()
            draft._inv_stamp_request(draft.create_uid)
        self._require(("submitted",), "be approved")
        self._inv_check_approver()
        for rec in self:
            rec._inv_stamp_approval(note)
            rec._guarded().write({"state": "approved"})
        return True

    def action_cancel(self):
        self._require(("draft", "submitted", "approved"), "be cancelled")
        self._guarded().write({"state": "cancelled"})
        return True

    def action_ship(self):
        Onhand = self.env["fix.stock.onhand"]
        for rec in self:
            if rec.state != "approved":
                raise UserError("Ship an approved RTV")
            if not (rec.rtv_ref or "").strip():
                raise UserError(
                    "RTV %s needs the vendor's RMA / return authorisation reference before "
                    "it ships (FR-INV-052)." % rec.name
                )
            check_location_usable(rec.location_id, self.env)
            cls = (
                rec.quarantine_id.ownership_class
                if rec.quarantine_id
                else location_class(rec.location_id)
            )
            status = rec._source_status()
            bucket = Onhand._bucket(rec.part_id, rec.location_id, cls, status)
            cost = bucket.unit_cost if bucket else 0.0
            if status == "unrestricted":
                rec._check_serial()
                Onhand._fix_check_bins(rec.part_id, rec.location_id, rec.qty)
            Onhand._apply(rec.part_id, rec.location_id, cls, -rec.qty, status=status)
            if rec.quarantine_id:
                rec.quarantine_id._guarded().write({"state": "returned"})
                lot = rec.quarantine_id.lot_id
                if lot and rec.part_id.is_serialized:
                    lot._fix_move("returned", qty=0.0)
            elif rec.lot_id and rec.part_id.is_serialized:
                rec.lot_id._fix_move("returned", qty=0.0)
            self.env["fix.inventory.valuation.suspense"]._fix_post(
                "rtv",
                rec.part_id,
                -rec.qty,
                cost,
                rec.name,
                location=rec.location_id,
                ownership=cls,
            )
            rec.sudo()._guarded().write(
                {"state": "shipped", "unit_cost": cost, "shipped_at": fields.Datetime.now()}
            )
        return True

    def action_mark_credited(self, credit_ref=None):
        self._require(("shipped",), "be closed")
        ref = (credit_ref or "").strip()
        if not ref:
            raise UserError("Record the vendor credit note or replacement reference.")
        self._guarded().write(
            {"state": "credited", "credit_ref": ref, "credited_at": fields.Datetime.now()}
        )
        for rec in self:
            rec._raise_vendor_credit_note(ref)
        return True

    def _raise_vendor_credit_note(self, ref):
        """A06 M15-13: hand the credit to AP. When cd_ap_ext is installed, a
        DRAFT vendor credit note (Mushak 6.7) for the RTV value is raised on
        the vendor's latest bill that still has room for it, linked back to
        this RTV; AP approves it under its own segregation of duties. Without
        AP, or without a bill to credit, the RTV says so."""
        self.ensure_one()
        if "fix.vendor.note" not in self.env or "fix.vendor.invoice" not in self.env:
            return False
        value = round((self.qty or 0.0) * (self.sudo().unit_cost or 0.0), 2)
        if value <= 0:
            self._guarded().write({"vendor_note_status": "no value to credit"})
            return False
        vendor = self.partner_id.commercial_partner_id
        Invoice = self.env["fix.vendor.invoice"].sudo()
        domain = [("company_id", "=", self.company_id.id)]
        if "approval_state" in Invoice._fields:
            domain.append(("approval_state", "!=", "rejected"))
        bills = Invoice.search(domain, order="id desc").filtered(
            lambda b: b.vendor_id.commercial_partner_id == vendor
        )
        for bill in bills:
            credited = sum(
                bill.note_ids.filtered(
                    lambda n: n.note_type == "decrease" and n.state != "cancelled"
                ).mapped("amount")
            )
            if (bill.subtotal or 0.0) - credited + 0.005 < value:
                continue
            note = (
                self.env["fix.vendor.note"]
                .sudo()
                .create(
                    {
                        "invoice_id": bill.id,
                        "company_id": bill.company_id.id,
                        "operating_unit_id": bill.operating_unit_id.id,
                        "note_type": "decrease",
                        "reason": "return",
                        "mushak_ref": ref,
                        "amount": value,
                        "description": "Return to vendor %s (%s x %s)"
                        % (self.name, self.qty, self.part_id.part_number),
                    }
                )
            )
            self._guarded().write(
                {
                    "vendor_note_res_id": note.id,
                    "vendor_note_status": "draft %s" % note.display_name,
                }
            )
            return note
        self._guarded().write(
            {"vendor_note_status": "no bill of %s with room for BDT %.2f" % (vendor.name, value)}
        )
        return False


# =========================================================================
# Ownership-class change
# =========================================================================
class FixStockClassChange(models.Model):
    """BRU-INV-06: stock changes ownership class (consignment -> owned on
    purchase, owned -> warranty reserve...) only through this document,
    approved by an Inventory Controller who did not request it. The move is
    at the source bucket's cost; a change into or out of a valued class books
    the value to the M19 suspense."""

    _name = "fix.stock.class.change"
    _description = "Ownership-Class Change"
    _order = "create_date desc, id desc"
    _inherit = ["fix.inventory.approval.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Location", required=True, ondelete="restrict"
    )
    from_class = fields.Selection(OWNERSHIP_CLASSES, string="From Class", required=True)
    to_class = fields.Selection(OWNERSHIP_CLASSES, string="To Class", required=True)
    qty = fields.Float(string="Quantity", required=True)
    reason = fields.Char(string="Reason", required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("done", "Applied"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
    )
    unit_cost = fields.Float(string="Unit Cost Moved (BDT)", readonly=True, groups=COST_GROUP)

    _classes_differ = models.Constraint(
        "CHECK (from_class <> to_class)", "A class change moves stock between two classes"
    )
    _qty_positive = models.Constraint("CHECK (qty > 0)", "Class change quantity must be positive")

    _PINNED = ("part_id", "location_id", "from_class", "to_class", "qty", "reason", "company_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "unit_cost"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state != "draft":
            locked |= set(self._PINNED)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.stock.class.change")
                    or "CLS/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            pinned = {k: vals[k] for k in self._PINNED if k in vals}
            if pinned and _changes(self.filtered(lambda r: r.state != "draft"), pinned):
                raise UserError("A submitted class change is pinned; raise a new one.")
        return super().write(vals)

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Submit a draft class change")
            check_quantity(rec.part_id, rec.qty, "class change quantity")
            if not (rec.reason or "").strip():
                raise UserError("A class change needs its reason.")
            rec._inv_stamp_request()
            rec._guarded().write({"state": "submitted"})
        return True

    def action_approve(self, note=None):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Class change %s is not awaiting approval." % rec.name)
        self._inv_check_approver()
        Onhand = self.env["fix.stock.onhand"]
        Suspense = self.env["fix.inventory.valuation.suspense"]
        for rec in self:
            check_location_usable(rec.location_id, self.env)
            source = Onhand._bucket(rec.part_id, rec.location_id, rec.from_class)
            cost = source.unit_cost if source else 0.0
            Onhand._fix_check_bins(rec.part_id, rec.location_id, rec.qty)
            Onhand._apply(rec.part_id, rec.location_id, rec.from_class, -rec.qty)
            Onhand._apply(rec.part_id, rec.location_id, rec.to_class, rec.qty, cost)
            valued_from = rec.from_class in VALUED_CLASSES
            valued_to = rec.to_class in VALUED_CLASSES
            if valued_from != valued_to:
                Suspense._fix_post(
                    "class_change",
                    rec.part_id,
                    rec.qty if valued_to else -rec.qty,
                    cost,
                    rec.name,
                    location=rec.location_id,
                    ownership=rec.to_class if valued_to else rec.from_class,
                )
            rec._inv_stamp_approval(note)
            rec.sudo()._guarded().write({"state": "done", "unit_cost": cost})
        return True

    def action_reject(self, note=None):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Class change %s is not awaiting approval." % rec.name)
        self._inv_check_approver()
        for rec in self:
            rec._inv_stamp_approval(note or "rejected")
            rec._guarded().write({"state": "rejected"})
        return True
