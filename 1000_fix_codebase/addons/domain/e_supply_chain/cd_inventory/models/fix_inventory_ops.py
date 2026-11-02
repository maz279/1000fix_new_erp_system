# fix_inventory_ops — M15: the per-location stock ledger and the control
# documents the workspace screens read: on-hand by ownership class, lots,
# goods receipts (inspection gate), transfers, counts, van reconciliation,
# quarantine/scrap and RTV. fix.spare.part keeps the aggregate qty_available;
# every movement here also keeps it in step.
from odoo import api, fields, models
from odoo.exceptions import UserError

OWNERSHIP_CLASSES = [
    ("owned", "Owned Stock"),
    ("consignment", "Supplier Consignment"),
    ("customer", "Customer Property"),
    ("van", "Van Stock"),
    ("bench", "Bench / WIP"),
    ("warranty", "Warranty Reserve"),
]


class FixStockOnhand(models.Model):
    """On-hand quantity of one part at one location in one ownership class."""

    _name = "fix.stock.onhand"
    _description = "Stock On Hand"
    _order = "part_id, location_id"

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
    qty = fields.Float(string="Quantity")
    reserved = fields.Float(string="Reserved")
    available_qty = fields.Float(string="Available", compute="_compute_available", store=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    unit_cost = fields.Monetary(string="Unit Cost", currency_field="currency_id")
    valuation_method = fields.Selection(
        [("fifo", "FIFO"), ("wac", "Weighted Average"), ("standard", "Standard Cost")],
        required=True,
        default="wac",
    )
    last_move_date = fields.Date(string="Last Movement")

    _part_loc_class_unique = models.Constraint(
        "UNIQUE (part_id, location_id, ownership_class)",
        "One on-hand row per part, location and ownership class",
    )
    _qty_non_negative = models.Constraint(
        "CHECK (qty >= 0 AND reserved >= 0 AND reserved <= qty)",
        "Quantities cannot be negative and reserved cannot exceed on-hand",
    )

    @api.depends("qty", "reserved")
    def _compute_available(self):
        for rec in self:
            rec.available_qty = round((rec.qty or 0.0) - (rec.reserved or 0.0), 3)

    @api.model
    def _apply(self, part, location, ownership, delta, unit_cost=None, must_exist=True):
        """Move `delta` into (or out of) a part/location/class bucket.

        Positive deltas create the bucket; negative deltas refuse to go below
        zero rather than creating a negative row.
        """
        row = self.search(
            [
                ("part_id", "=", part.id),
                ("location_id", "=", location.id),
                ("ownership_class", "=", ownership),
            ],
            limit=1,
        )
        if not row and delta > 0:
            row = self.create(
                {
                    "part_id": part.id,
                    "location_id": location.id,
                    "ownership_class": ownership,
                    "qty": delta,
                    "unit_cost": unit_cost or part.unit_cost or 0.0,
                    "last_move_date": fields.Date.context_today(self),
                }
            )
            return row
        if not row:
            # legacy flows (a scan at a location that predates the ledger) can
            # move the aggregate without a bucket; ledger-native documents
            # (transfer, count, scrap, RTV) still demand the bucket exists
            if not must_exist:
                return row
            raise UserError(
                "No %s stock of %s at %s to move" % (ownership, part.part_number, location.code)
            )
        new_qty = (row.qty or 0.0) + delta
        if new_qty < 0:
            raise UserError(
                "Moving %.2f from %s at %s would leave %.2f — insufficient on-hand"
                % (abs(delta), part.part_number, location.code, new_qty)
            )
        vals = {"qty": new_qty, "last_move_date": fields.Date.context_today(self)}
        if unit_cost:
            vals["unit_cost"] = unit_cost
        row.write(vals)
        return row


class FixStockLot(models.Model):
    """A serial or lot in the ledger, with its current location and age."""

    _name = "fix.stock.lot"
    _description = "Stock Serial / Lot"
    _order = "received_on desc, id desc"

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
        ],
        required=True,
        default="in_stock",
        index=True,
    )
    received_on = fields.Date()
    warranty_until = fields.Date()
    source_ref = fields.Char(string="Source Reference")

    _qty_non_negative = models.Constraint("CHECK (qty >= 0)", "Lot quantity cannot be negative")


class FixStockReceipt(models.Model):
    """Goods receipt with the inspection gate (accepted / rejected)."""

    _name = "fix.stock.receipt"
    _description = "Goods Receipt"
    _order = "create_date desc, id desc"

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
    received_on = fields.Date(required=True, default=fields.Date.context_today)
    inspection_notes = fields.Char()
    state = fields.Selection(
        [("draft", "Draft"), ("inspected", "Inspected"), ("posted", "Posted")],
        required=True,
        default="draft",
    )
    line_ids = fields.One2many("fix.stock.receipt.line", "receipt_id", string="Lines")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.stock.receipt") or "GRN/New"
                )
        return super().create(vals_list)

    def action_inspect(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Inspect a draft receipt")
            if not rec.line_ids:
                raise UserError("A receipt needs at least one line")
            if any(line.qty_accepted <= 0 for line in rec.line_ids):
                raise UserError("The inspection gate requires an accepted quantity on every line")
            rec.state = "inspected"

    def action_post(self):
        onhand = self.env["fix.stock.onhand"]
        lots = self.env["fix.stock.lot"]
        for rec in self:
            if rec.state != "inspected":
                raise UserError("Post an inspected receipt")
            for line in rec.line_ids:
                onhand._apply(
                    line.part_id, rec.location_id, "owned", line.qty_accepted, line.unit_cost
                )
                line.part_id.sudo().write(
                    {"qty_available": (line.part_id.qty_available or 0.0) + line.qty_accepted}
                )
                if line.line_no:
                    lot = lots.search(
                        [("part_id", "=", line.part_id.id), ("name", "=", line.line_no)], limit=1
                    )
                    if lot:
                        lot.write(
                            {
                                "qty": (lot.qty or 0.0) + line.qty_accepted,
                                "location_id": rec.location_id.id,
                                "status": "in_stock",
                            }
                        )
                    else:
                        lots.create(
                            {
                                "name": line.line_no,
                                "part_id": line.part_id.id,
                                "location_id": rec.location_id.id,
                                "qty": line.qty_accepted,
                                "received_on": rec.received_on,
                                "source_ref": rec.name,
                            }
                        )
            rec.state = "posted"


class FixStockReceiptLine(models.Model):
    _name = "fix.stock.receipt.line"
    _description = "Goods Receipt Line"
    _order = "receipt_id, id"

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
    unit_cost = fields.Monetary(string="Unit Cost", currency_field="currency_id")

    _qty_bounds = models.Constraint(
        "CHECK (qty_received >= 0 AND qty_accepted >= 0 AND qty_accepted <= qty_received)",
        "Accepted quantity must be between 0 and the received quantity",
    )

    @api.depends("qty_received", "qty_accepted")
    def _compute_rejected(self):
        for rec in self:
            rec.qty_rejected = round((rec.qty_received or 0.0) - (rec.qty_accepted or 0.0), 3)


class FixStockTransfer(models.Model):
    """An inter-branch stock transfer."""

    _name = "fix.stock.transfer"
    _description = "Stock Transfer"
    _order = "create_date desc, id desc"

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
    state = fields.Selection(
        [("draft", "Draft"), ("dispatched", "Dispatched"), ("received", "Received")],
        required=True,
        default="draft",
    )
    line_ids = fields.One2many("fix.stock.transfer.line", "transfer_id", string="Lines")

    _different_locations = models.Constraint(
        "CHECK (from_location_id <> to_location_id)",
        "A transfer moves stock between two different locations",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.stock.transfer") or "TRF/New"
                )
        return super().create(vals_list)

    def action_dispatch(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Dispatch a draft transfer")
            if not rec.line_ids:
                raise UserError("A transfer needs at least one line")
            rec.write({"state": "dispatched", "dispatched_on": fields.Date.context_today(self)})

    def action_receive(self):
        onhand = self.env["fix.stock.onhand"]
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Receive a dispatched transfer")
            for line in rec.line_ids:
                onhand._apply(line.part_id, rec.from_location_id, "owned", -line.qty)
                onhand._apply(line.part_id, rec.to_location_id, "owned", line.qty)
            rec.write({"state": "received", "received_on": fields.Date.context_today(self)})


class FixStockTransferLine(models.Model):
    _name = "fix.stock.transfer.line"
    _description = "Stock Transfer Line"
    _order = "transfer_id, id"

    transfer_id = fields.Many2one(
        "fix.stock.transfer", required=True, ondelete="cascade", index=True
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    qty = fields.Float(string="Quantity")

    _qty_positive = models.Constraint("CHECK (qty > 0)", "Transfer quantity must be positive")


class FixStockCount(models.Model):
    """A cycle or full count at one location, with its variance lines."""

    _name = "fix.stock.count"
    _description = "Stock Count"
    _order = "create_date desc, id desc"

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
        [("draft", "Draft"), ("posted", "Posted")], required=True, default="draft"
    )
    line_ids = fields.One2many("fix.stock.count.line", "count_id", string="Lines")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.stock.count") or "CNT/New"
        return super().create(vals_list)

    def action_post(self):
        onhand = self.env["fix.stock.onhand"]
        for rec in self:
            if rec.state != "draft":
                raise UserError("Post a draft count")
            if not rec.line_ids:
                raise UserError("A count needs at least one line")
            for line in rec.line_ids:
                delta = (line.counted_qty or 0.0) - (line.expected_qty or 0.0)
                if not delta:
                    continue
                onhand._apply(line.part_id, rec.location_id, "owned", delta)
                line.part_id.sudo().write(
                    {"qty_available": (line.part_id.qty_available or 0.0) + delta}
                )
            rec.state = "posted"


class FixStockCountLine(models.Model):
    _name = "fix.stock.count.line"
    _description = "Stock Count Line"
    _order = "count_id, id"

    count_id = fields.Many2one("fix.stock.count", required=True, ondelete="cascade", index=True)
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    expected_qty = fields.Float(string="Expected")
    counted_qty = fields.Float(string="Counted")
    variance = fields.Float(compute="_compute_variance", store=True, string="Variance")

    @api.depends("expected_qty", "counted_qty")
    def _compute_variance(self):
        for rec in self:
            rec.variance = round((rec.counted_qty or 0.0) - (rec.expected_qty or 0.0), 3)


class FixStockVanRecon(models.Model):
    """The technician's daily van-stock reconciliation."""

    _name = "fix.stock.van.recon"
    _description = "Van Stock Reconciliation"
    _order = "recon_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Van Location", required=True, ondelete="restrict"
    )
    technician_id = fields.Many2one("hr.employee", string="Technician")
    recon_date = fields.Date(required=True, default=fields.Date.context_today)
    expected_qty = fields.Float(string="Expected (pcs)")
    counted_qty = fields.Float(string="Counted (pcs)")
    variance = fields.Float(compute="_compute_variance", store=True, string="Variance")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("discrepancy", "Discrepancy")],
        required=True,
        default="draft",
    )
    notes = fields.Char()

    @api.depends("expected_qty", "counted_qty")
    def _compute_variance(self):
        for rec in self:
            rec.variance = round((rec.counted_qty or 0.0) - (rec.expected_qty or 0.0), 3)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.stock.van.recon") or "VRC/New"
                )
        return super().create(vals_list)

    def action_confirm(self):
        for rec in self:
            rec.state = "confirmed" if not rec.variance else "discrepancy"


class FixStockQuarantine(models.Model):
    """A quarantined or scrapped quantity with its reason."""

    _name = "fix.stock.quarantine"
    _description = "Stock Quarantine / Scrap"
    _order = "create_date desc, id desc"

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
    lot_id = fields.Many2one("fix.stock.lot", string="Serial / Lot", ondelete="set null")
    qty = fields.Float(string="Quantity")
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
        [("quarantined", "Quarantined"), ("released", "Released"), ("scrapped", "Scrapped")],
        required=True,
        default="quarantined",
    )
    notes = fields.Char()

    _qty_positive = models.Constraint("CHECK (qty > 0)", "Quarantine quantity must be positive")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.stock.quarantine") or "QRN/New"
                )
        return super().create(vals_list)

    def action_release(self):
        for rec in self:
            if rec.state != "quarantined":
                raise UserError("Release a quarantined quantity")
            rec.state = "released"

    def action_scrap(self):
        onhand = self.env["fix.stock.onhand"]
        for rec in self:
            if rec.state != "quarantined":
                raise UserError("Scrap a quarantined quantity")
            onhand._apply(rec.part_id, rec.location_id, "owned", -rec.qty)
            rec.part_id.sudo().write(
                {"qty_available": (rec.part_id.qty_available or 0.0) - rec.qty}
            )
            if rec.lot_id:
                rec.lot_id.write({"status": "scrapped", "qty": 0.0})
            rec.state = "scrapped"


class FixStockRtv(models.Model):
    """A return-to-vendor request for defective or wrong stock."""

    _name = "fix.stock.rtv"
    _description = "Return to Vendor"
    _order = "create_date desc, id desc"

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
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("shipped", "Shipped")],
        required=True,
        default="draft",
    )
    notes = fields.Char()

    _qty_positive = models.Constraint("CHECK (qty > 0)", "RTV quantity must be positive")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.stock.rtv") or "RTV/New"
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft RTV")
            rec.state = "approved"

    def action_ship(self):
        onhand = self.env["fix.stock.onhand"]
        for rec in self:
            if rec.state != "approved":
                raise UserError("Ship an approved RTV")
            onhand._apply(rec.part_id, rec.location_id, "owned", -rec.qty)
            rec.part_id.sudo().write(
                {"qty_available": (rec.part_id.qty_available or 0.0) - rec.qty}
            )
            rec.state = "shipped"
