# fix_wms_ops — M41: the warehouse execution documents behind the registry
# screens. Structure (warehouse/zone/bin) lives in cd_wms_structure.
#
# NOTE: these models live in cd_inventory (not cd_wms_structure) because
# cd_inventory already depends on the structure module; adding the reverse
# dependency would create a module cycle.
#
# A06 audit (2026-11-03) M41-1..M41-13, remediation R1: M41 was a label layer
# whose bin quantities were free-typed and never reached M15, while its
# surface let a plain user write the M15 on-hand. BRU-WMS-01 now holds: M41
# never authors a stock quantity. A warehouse names the M15 location its bins
# break down (stock_location_id) and every physical confirmation goes through
# the M15 ledger in the same transaction:
#   - put-away only of stock a POSTED receipt line accepted, and only up to
#     what is not yet put away; capacity, zone, blocked-slot and hazard rules;
#   - wave release RESERVES in M15 (fix.stock.onhand._fix_reserve) and on the
#     slot, refusing over-allocation;
#   - pick moves the stock from the bin to STAGED in M15, once (Pick All is
#     idempotent); a short pick raises a count-back task, a bin driven to 0 a
#     zero-crossing count;
#   - pack needs sealed cartons that reconcile to the picked quantity, stage
#     a staging record, ship a LOADED stage with a load reference; ship
#     decrements M15 and publishes wh.shipped;
#   - floor counts are blind snapshots that go to an M15 count for approval.
# Every state, quantity and evidence field is guarded.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_inventory_approval import (
    PARAM_COUNT_TOLERANCE_PCT,
    check_location_usable,
    check_quantity,
    inv_param,
    location_class,
)

EPS = 1e-6


def _differs(records, vals):
    return any(
        rec._fix_guard_differs(k, v, rec[k])
        for rec in records
        for k, v in vals.items()
        if k in rec._fields
    )


class FixWarehouseLedger(models.Model):
    """The M15 location a warehouse's bins are a breakdown of (BRU-WMS-02)."""

    _inherit = "fix.warehouse"

    stock_location_id = fields.Many2one(
        "fix.stock.location",
        string="M15 Stock Location",
        ondelete="restrict",
        help="The M15 ledger location this warehouse's bins break down. Put-away, "
        "wave release, pick and ship move this location's stock.",
    )


def _bin_location(bin_record):
    warehouse = bin_record.zone_id.warehouse_id
    location = warehouse.stock_location_id
    if not location:
        raise UserError(
            "Warehouse %s is not linked to an M15 stock location: set its M15 Stock "
            "Location before moving stock through its bins (BRU-WMS-01)." % warehouse.name
        )
    return location


class FixWmsSlot(models.Model):
    """A part's slot: which bin holds it and how it moves. The quantity is
    a breakdown of the M15 location ledger and is moved only by put-away,
    pick and approved counts."""

    _name = "fix.wms.slot"
    _description = "Bin Slot"
    _order = "bin_id, part_id"
    _inherit = ["fix.inventory.approval.mixin"]

    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="cascade", index=True
    )
    bin_id = fields.Many2one(
        "fix.warehouse.bin", string="Bin", required=True, ondelete="cascade", index=True
    )
    zone_id = fields.Many2one(related="bin_id.zone_id", string="Zone", store=True)
    qty = fields.Float(string="Quantity in Bin", readonly=True)
    reserved_qty = fields.Float(string="Allocated to Waves", readonly=True)
    velocity = fields.Selection(
        [("fast", "Fast Mover"), ("medium", "Medium"), ("slow", "Slow")],
        required=True,
        default="medium",
    )
    slot_type = fields.Selection(
        [("pick", "Pick Face"), ("bulk", "Bulk Reserve"), ("reserve", "Reserve")],
        required=True,
        default="pick",
    )
    last_slotted_on = fields.Date(readonly=True)
    state = fields.Selection(
        [("active", "Active"), ("blocked", "Blocked")], required=True, default="active"
    )
    block_reason = fields.Char(string="Block Reason")

    _slot_unique = models.Constraint("UNIQUE (part_id, bin_id)", "One slot per part and bin")
    _qty_non_negative = models.Constraint(
        "CHECK (qty >= 0 AND reserved_qty >= 0 AND reserved_qty <= qty)",
        "Slot quantity cannot be negative and allocation cannot exceed it",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "qty",
            "reserved_qty",
            "state",
            "last_slotted_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= {"part_id", "bin_id", "block_reason"}
        return locked

    def _inv_excluded_users(self):
        # the blocker never unblocks his own block
        return self.requested_by_id

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in ("part_id", "bin_id") if k in vals}
            if frozen and _differs(self.filtered(lambda s: s.qty or s.reserved_qty), frozen):
                raise UserError("A slot holding stock cannot be moved to another part or bin.")
        return super().write(vals)

    @api.constrains("qty", "bin_id")
    def _check_capacity(self):
        for bin_record in self.mapped("bin_id"):
            capacity = bin_record.capacity_qty or 0.0
            if capacity <= 0:
                continue
            total = sum(self.sudo().search([("bin_id", "=", bin_record.id)]).mapped("qty"))
            if total > capacity + EPS:
                raise ValidationError(
                    "Bin %s holds at most %s; this would put %s in it (BRU-WMS-09)."
                    % (bin_record.name, capacity, round(total, 4))
                )

    @api.model
    def _slot_for(self, part, bin_record, create=False):
        slot = self.sudo().search(
            [("part_id", "=", part.id), ("bin_id", "=", bin_record.id)], limit=1
        )
        if not slot and create:
            slot = self.sudo().create(
                {"part_id": part.id, "bin_id": bin_record.id, "velocity": "medium"}
            )
        return slot.with_env(self.env)

    def _check_pickable(self):
        for slot in self:
            if slot.state == "blocked":
                raise UserError(
                    "Bin %s is blocked for %s (%s): it cannot be picked or filled until an "
                    "Inventory Controller unblocks it (BRU-WMS-12)."
                    % (slot.bin_id.name, slot.part_id.part_number, slot.block_reason or "no reason")
                )
            if not slot.bin_id.zone_id.reservable:
                raise UserError(
                    "Bin %s is in the %s zone: its stock is not reservable or pickable "
                    "(BRU-INV-08 / BRU-WMS-04)." % (slot.bin_id.name, slot.bin_id.zone_id.zone_type)
                )

    def action_block(self, reason=None):
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Give the reason the bin is blocked.")
        for slot in self:
            if slot.state != "active":
                raise UserError("Slot %s is already blocked." % slot.bin_id.name)
            slot._inv_stamp_request()
            slot._guarded().write({"state": "blocked", "block_reason": reason})
        return True

    def action_unblock(self, note=None):
        for slot in self:
            if slot.state != "blocked":
                raise UserError("Slot %s is not blocked." % slot.bin_id.name)
        self._inv_check_approver()
        for slot in self:
            slot._inv_stamp_approval(note)
            slot._guarded().write({"state": "active"})
        return True


class FixWmsDock(models.Model):
    _name = "fix.wms.dock"
    _description = "Dock Appointment"
    _order = "slot_start desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    dock_no = fields.Char(string="Dock", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner / Carrier")
    carrier = fields.Char()
    dock_type = fields.Selection(
        [("inbound", "Inbound"), ("outbound", "Outbound")],
        required=True,
        default="inbound",
    )
    slot_start = fields.Datetime(required=True, default=fields.Datetime.now)
    slot_end = fields.Datetime(
        required=True, default=lambda self: fields.Datetime.now() + timedelta(hours=1)
    )
    receipt_id = fields.Many2one("fix.stock.receipt", string="Goods Receipt", ondelete="restrict")
    wave_id = fields.Many2one("fix.wms.wave", string="Outbound Wave", ondelete="restrict")
    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("checked_in", "Checked In"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="scheduled",
    )
    notes = fields.Char()

    _window_ordered = models.Constraint(
        "CHECK (slot_end > slot_start)", "The dock window must end after it starts"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    @api.constrains("dock_no", "slot_start", "slot_end", "state")
    def _check_overlap(self):
        for rec in self.filtered(lambda d: d.state != "cancelled"):
            clash = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("dock_no", "=", rec.dock_no),
                    ("state", "!=", "cancelled"),
                    ("slot_start", "<", rec.slot_end),
                    ("slot_end", ">", rec.slot_start),
                ],
                limit=1,
            )
            if clash:
                raise ValidationError(
                    "Dock %s is already booked %s - %s (%s)."
                    % (rec.dock_no, clash.slot_start, clash.slot_end, clash.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.wms.dock") or "DOCK/New"
                )
        return super().create(vals_list)

    def action_check_in(self):
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("Check in a scheduled appointment")
            rec._guarded().write({"state": "checked_in"})
        return True

    def action_complete(self):
        for rec in self:
            if rec.state != "checked_in":
                raise UserError("Complete a checked-in appointment")
            if rec.dock_type == "inbound" and not rec.receipt_id:
                raise UserError(
                    "Inbound appointment %s completes with the goods receipt it delivered: "
                    "link the receipt first." % rec.name
                )
            if rec.dock_type == "outbound" and rec.wave_id and rec.wave_id.state != "shipped":
                raise UserError("Wave %s has not shipped yet." % rec.wave_id.name)
            rec._guarded().write({"state": "completed"})
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state in ("completed", "cancelled"):
                raise UserError("Appointment %s is already closed." % rec.name)
            rec._guarded().write({"state": "cancelled"})
        return True


class FixWmsPutaway(models.Model):
    _name = "fix.wms.putaway"
    _description = "Directed Put-Away"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="cascade", index=True
    )
    qty = fields.Float(string="Quantity")
    to_bin_id = fields.Many2one(
        "fix.warehouse.bin", string="Target Bin", required=True, ondelete="restrict"
    )
    receipt_line_id = fields.Many2one(
        "fix.stock.receipt.line",
        string="Received Line",
        ondelete="restrict",
        help="The posted goods-receipt line whose accepted stock is put away.",
    )
    lot_id = fields.Many2one("fix.stock.lot", string="Serial / Lot", ondelete="restrict")
    from_ref = fields.Char(string="Source Reference")
    assignee_id = fields.Many2one("hr.employee", string="Assigned To")
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done")], required=True, default="pending"
    )
    done_at = fields.Datetime(readonly=True)
    done_by_id = fields.Many2one("res.users", string="Done By", readonly=True)

    _qty_positive = models.Constraint("CHECK (qty > 0)", "Put-away quantity must be positive")

    _DOC = ("part_id", "qty", "to_bin_id", "receipt_line_id", "lot_id", "company_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "done_at", "done_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state == "done":
            locked |= set(self._DOC) | {"from_ref", "assignee_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.wms.putaway") or "PUTA/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in (*self._DOC, "from_ref", "assignee_id") if k in vals}
            if frozen and _differs(self.filtered(lambda r: r.state == "done"), frozen):
                raise UserError("A completed put-away is final.")
        return super().write(vals)

    def _remaining_on_line(self, line):
        done = self.sudo().search(
            [("receipt_line_id", "=", line.id), ("state", "=", "done"), ("id", "not in", self.ids)]
        )
        return round((line.qty_accepted or 0.0) - sum(done.mapped("qty")), 4)

    def action_complete(self):
        Slot = self.env["fix.wms.slot"]
        for rec in self:
            if rec.state != "pending":
                raise UserError("Complete a pending put-away")
            check_quantity(rec.part_id, rec.qty, "put-away quantity")
            if (
                not self.env.su
                and rec.assignee_id.user_id
                and rec.assignee_id.user_id != self.env.user
            ):
                raise UserError(
                    "Put-away %s is assigned to %s (BRU-WMS-14)." % (rec.name, rec.assignee_id.name)
                )
            line = rec.receipt_line_id
            if not line or line.receipt_id.state != "posted":
                raise UserError(
                    "Put-away %s needs the POSTED goods-receipt line it puts away: only "
                    "stock that was received and passed inspection is put away (BRU-WMS-04)."
                    % rec.name
                )
            if line.part_id != rec.part_id:
                raise UserError(
                    "Receipt line %s is for %s, not %s."
                    % (line.receipt_id.name, line.part_id.part_number, rec.part_id.part_number)
                )
            location = _bin_location(rec.to_bin_id)
            if line.receipt_id.location_id != location:
                raise UserError(
                    "Receipt %s was received at %s; bin %s belongs to %s."
                    % (
                        line.receipt_id.name,
                        line.receipt_id.location_id.code,
                        rec.to_bin_id.name,
                        location.code,
                    )
                )
            remaining = rec._remaining_on_line(line)
            if rec.qty > remaining + EPS:
                raise UserError(
                    "Only %s of receipt line %s remains to be put away; %s cannot be."
                    % (remaining, line.receipt_id.name, rec.qty)
                )
            if rec.part_id.is_serialized and (
                not rec.lot_id or rec.lot_id.part_id != rec.part_id or abs(rec.qty - 1.0) > EPS
            ):
                raise UserError(
                    "%s is serialized: put away one unit with its serial (BRU-WMS-10)."
                    % rec.part_id.part_number
                )
            if (rec.part_id.storage_class or "general") == "hazardous" and (
                rec.to_bin_id.storage_class != "hazardous"
            ):
                raise UserError(
                    "%s is hazardous: it goes only into a hazardous-class bin, not %s "
                    "(BRU-WMS-11)." % (rec.part_id.part_number, rec.to_bin_id.name)
                )
            bin_class = rec.to_bin_id.ownership_class or "any"
            received_class = line.receipt_id.ownership_class
            if bin_class != "any" and bin_class != received_class:
                raise UserError(
                    "Bin %s holds %s stock only; receipt %s received %s stock (BRU-WMS-03)."
                    % (rec.to_bin_id.name, bin_class, line.receipt_id.name, received_class)
                )
            slot = Slot._slot_for(rec.part_id, rec.to_bin_id, create=True)
            slot._check_pickable()
            slot._guarded().write(
                {
                    "qty": (slot.qty or 0.0) + rec.qty,
                    "last_slotted_on": fields.Date.context_today(self),
                }
            )
            rec._guarded().write(
                {"state": "done", "done_at": fields.Datetime.now(), "done_by_id": self.env.user.id}
            )
            publish(
                self.env,
                "wh.putaway_completed",
                "fix.wms.putaway",
                rec.id,
                {
                    "putaway": rec.name,
                    "part_id": rec.part_id.id,
                    "bin_id": rec.to_bin_id.id,
                    "qty": rec.qty,
                    "receipt": line.receipt_id.name,
                    "location_id": location.id,
                },
            )
        return True


class FixWmsWave(models.Model):
    _name = "fix.wms.wave"
    _description = "Pick Wave"
    _order = "wave_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    warehouse_id = fields.Many2one("fix.warehouse", string="Warehouse", ondelete="restrict")
    wave_date = fields.Date(required=True, default=fields.Date.context_today)
    strategy = fields.Selection(
        [("single", "Single Order"), ("zone", "Zone Batch"), ("batch", "Batch Picking")],
        required=True,
        default="zone",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("released", "Released"),
            ("picking", "Picking"),
            ("packed", "Packed"),
            ("staged", "Staged"),
            ("shipped", "Shipped"),
        ],
        required=True,
        default="draft",
    )
    line_ids = fields.One2many("fix.wms.wave.line", "wave_id", string="Lines")
    carton_ids = fields.One2many("fix.wms.carton", "wave_id", string="Cartons")
    stage_ids = fields.One2many("fix.wms.stage", "wave_id", string="Staging")
    released_at = fields.Datetime(readonly=True)
    released_by_id = fields.Many2one("res.users", string="Released By", readonly=True)
    shipped_at = fields.Datetime(readonly=True)
    shipped_by_id = fields.Many2one("res.users", string="Shipped By", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "released_at",
            "released_by_id",
            "shipped_at",
            "shipped_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state not in (False, "draft"):
            locked |= {"line_ids", "warehouse_id", "strategy", "wave_date"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.wms.wave") or "WAVE/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in ("warehouse_id",) if k in vals}
            moving = self.filtered(lambda w: w.state != "draft")
            if (frozen and _differs(moving, frozen)) or ("line_ids" in vals and moving):
                raise UserError("A released wave's lines and warehouse are final.")
        return super().write(vals)

    def _require(self, states, what):
        for rec in self:
            if rec.state not in states:
                raise UserError(
                    "Wave %s cannot %s: it is %s."
                    % (rec.name, what, dict(self._fields["state"].selection)[rec.state])
                )

    def _wave_location(self):
        self.ensure_one()
        bins = self.line_ids.mapped("bin_id")
        warehouses = bins.mapped("zone_id.warehouse_id")
        if self.warehouse_id:
            warehouses |= self.warehouse_id
        if len(warehouses) != 1:
            raise UserError(
                "Wave %s must pick from the bins of one warehouse (found %d)."
                % (self.name, len(warehouses))
            )
        location = _bin_location(bins[:1] if bins else self.env["fix.warehouse.bin"])
        return warehouses, location

    def action_release(self):
        """BRU-WMS-13: release only what M15 can allocate."""
        Onhand = self.env["fix.stock.onhand"]
        Slot = self.env["fix.wms.slot"]
        for rec in self:
            if rec.state != "draft":
                raise UserError("Release a draft wave")
            if not rec.line_ids:
                raise UserError("A wave needs at least one line")
            for line in rec.line_ids:
                if not line.bin_id:
                    raise UserError("Every wave line needs its pick bin.")
            warehouse, location = rec._wave_location()
            check_location_usable(location, self.env)
            cls = location_class(location)
            for line in rec.line_ids:
                check_quantity(line.part_id, line.qty, "wave quantity")
                slot = Slot._slot_for(line.part_id, line.bin_id)
                if not slot:
                    raise UserError(
                        "Bin %s holds no %s: the line cannot be allocated."
                        % (line.bin_id.name, line.part_id.part_number)
                    )
                slot._check_pickable()
                free = (slot.qty or 0.0) - (slot.reserved_qty or 0.0)
                if line.qty > free + EPS:
                    raise UserError(
                        "Bin %s has %s of %s free to allocate; wave %s asks for %s "
                        "(over-allocation, BRU-WMS-13)."
                        % (
                            line.bin_id.name,
                            round(free, 4),
                            line.part_id.part_number,
                            rec.name,
                            line.qty,
                        )
                    )
                Onhand._fix_reserve(line.part_id, location, cls, line.qty, rec.name)
                slot._guarded().write({"reserved_qty": (slot.reserved_qty or 0.0) + line.qty})
                line._guarded().write({"reserved_qty": line.qty})
            rec._guarded().write(
                {
                    "state": "released",
                    "warehouse_id": warehouse.id,
                    "released_at": fields.Datetime.now(),
                    "released_by_id": self.env.user.id,
                }
            )
        return True

    def _pick_lines(self, lines):
        """Pick the given PENDING lines of this wave: bin -> staged in M15."""
        self.ensure_one()
        Onhand = self.env["fix.stock.onhand"]
        Slot = self.env["fix.wms.slot"]
        Task = self.env["fix.wms.task"]
        _warehouse, location = self._wave_location()
        cls = location_class(location)
        now = fields.Datetime.now()
        for line in lines.filtered(lambda ln: ln.state == "pending"):
            slot = Slot._slot_for(line.part_id, line.bin_id)
            if not slot:
                raise UserError(
                    "Bin %s holds no %s." % (line.bin_id.name, line.part_id.part_number)
                )
            slot._check_pickable()
            picked = min(line.qty or 0.0, slot.qty or 0.0)
            reserved = line.reserved_qty or 0.0
            if reserved:
                Onhand._fix_unreserve(line.part_id, location, cls, reserved, self.name)
            if picked > EPS:
                Onhand._fix_move_status(
                    line.part_id, location, cls, picked, "unrestricted", "staged"
                )
            slot._guarded().write(
                {
                    "qty": round((slot.qty or 0.0) - picked, 4),
                    "reserved_qty": round(max((slot.reserved_qty or 0.0) - reserved, 0.0), 4),
                }
            )
            short = picked + EPS < (line.qty or 0.0)
            line._guarded().write(
                {
                    "picked_qty": picked,
                    "reserved_qty": 0.0,
                    "state": "short" if short else "picked",
                    "picked_by_id": self.env.user.id,
                    "picked_at": now,
                }
            )
            if short:
                # BRU-WMS-07: a short pick raises an immediate count-back
                Task.sudo().create(
                    {
                        "company_id": self.company_id.id,
                        "task_type": "count",
                        "ref": "Count-back %s" % self.name,
                        "part_id": line.part_id.id,
                        "bin_id": line.bin_id.id,
                        "qty": 0.0,
                    }
                )
            elif slot.qty <= EPS:
                # BRU-WMS-08: a pick that empties the bin confirms it with a count
                Task.sudo().create(
                    {
                        "company_id": self.company_id.id,
                        "task_type": "count",
                        "ref": "Zero-crossing %s" % self.name,
                        "part_id": line.part_id.id,
                        "bin_id": line.bin_id.id,
                        "qty": 0.0,
                    }
                )
        if self.state == "released":
            self._guarded().write({"state": "picking"})

    def action_pick_all(self):
        """Pick every PENDING line. Idempotent: lines already picked or short
        are never picked again, so re-running it moves nothing."""
        for rec in self:
            if rec.state not in ("released", "picking"):
                raise UserError("Pick a released wave")
            rec._pick_lines(rec.line_ids)
        return True

    def action_accept_short(self):
        """Close the short lines at what was actually picked (a line that
        picked nothing is cancelled) so the wave can be packed."""
        self._require(("picking",), "accept a short pick")
        for rec in self:
            for line in rec.line_ids.filtered(lambda ln: ln.state == "short"):
                if line.picked_qty > EPS:
                    line._guarded().write({"qty": line.picked_qty, "state": "picked"})
                else:
                    line._guarded().write({"state": "cancelled"})
        return True

    def _picked_total(self):
        self.ensure_one()
        return round(
            sum(self.line_ids.filtered(lambda ln: ln.state == "picked").mapped("picked_qty")), 4
        )

    def action_packed(self):
        for rec in self:
            if rec.state != "picking":
                raise UserError("Pack a picked wave")
            if any(line.state not in ("picked", "cancelled") for line in rec.line_ids):
                raise UserError("Every line must be picked before packing")
            picked = rec._picked_total()
            if picked <= EPS:
                raise UserError("Wave %s picked nothing: there is nothing to pack." % rec.name)
            sealed = rec.carton_ids.filtered(lambda c: c.state == "sealed")
            packed = sum(sealed.mapped("contents_qty"))
            if not sealed or abs(packed - picked) > EPS:
                raise UserError(
                    "Wave %s picked %s; its sealed cartons hold %s. Pack every picked unit "
                    "into sealed cartons first (handling units, §8.2)." % (rec.name, picked, packed)
                )
            rec._guarded().write({"state": "packed"})
        return True

    def action_stage(self):
        for rec in self:
            if rec.state != "packed":
                raise UserError("Stage a packed wave")
            if not rec.stage_ids.filtered(lambda s: s.state == "staging"):
                raise UserError(
                    "Wave %s needs a staging record (lane) before it is staged." % rec.name
                )
            rec._guarded().write({"state": "staged"})
        return True

    def action_ship(self):
        """BRU-WMS-17: ship a staged wave from a LOADED stage with a load
        reference; M15 loses the staged stock and wh.shipped is published."""
        Onhand = self.env["fix.stock.onhand"]
        Suspense = self.env["fix.inventory.valuation.suspense"]
        for rec in self:
            if rec.state != "staged":
                raise UserError("Ship a staged wave")
            stage = rec.stage_ids.filtered(
                lambda s: s.state == "loaded" and (s.load_ref or "").strip()
            )
            if not stage:
                raise UserError(
                    "Wave %s ships from a LOADED staging record with its load / vehicle "
                    "reference (BRU-WMS-17)." % rec.name
                )
            _warehouse, location = rec._wave_location()
            cls = location_class(location)
            shipped = []
            for line in rec.line_ids.filtered(lambda ln: ln.state == "picked"):
                bucket = Onhand._bucket(line.part_id, location, cls, "staged")
                cost = bucket.unit_cost if bucket else 0.0
                Onhand._apply(line.part_id, location, cls, -line.picked_qty, status="staged")
                Suspense._fix_post(
                    "shipment",
                    line.part_id,
                    -line.picked_qty,
                    cost,
                    rec.name,
                    location=location,
                    ownership=cls,
                )
                shipped.append(
                    {"part_id": line.part_id.id, "qty": line.picked_qty, "unit_cost": cost}
                )
            rec.carton_ids.filtered(lambda c: c.state == "sealed")._guarded().write(
                {"state": "dispatched"}
            )
            stage[:1]._guarded().write({"state": "dispatched"})
            rec._guarded().write(
                {
                    "state": "shipped",
                    "shipped_at": fields.Datetime.now(),
                    "shipped_by_id": self.env.user.id,
                }
            )
            publish(
                self.env,
                "wh.shipped",
                "fix.wms.wave",
                rec.id,
                {
                    "wave": rec.name,
                    "warehouse_id": rec.warehouse_id.id or None,
                    "location_id": location.id,
                    "load_ref": stage[:1].load_ref,
                    "cartons": len(rec.carton_ids),
                    "lines": shipped,
                },
            )
        return True


class FixWmsWaveLine(models.Model):
    _name = "fix.wms.wave.line"
    _description = "Pick Wave Line"
    _order = "wave_id, id"
    _inherit = ["fix.guarded.mixin"]

    wave_id = fields.Many2one("fix.wms.wave", required=True, ondelete="cascade", index=True)
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    bin_id = fields.Many2one("fix.warehouse.bin", string="Pick Bin", ondelete="set null")
    qty = fields.Float(string="Quantity")
    reserved_qty = fields.Float(string="Allocated", readonly=True)
    picked_qty = fields.Float(string="Picked", readonly=True)
    picked_by_id = fields.Many2one("res.users", string="Picked By", readonly=True)
    picked_at = fields.Datetime(string="Picked On", readonly=True)
    scanned_bin = fields.Char(string="Scanned Bin", readonly=True, copy=False)
    scanned_item = fields.Char(string="Scanned Item", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("picked", "Picked"),
            ("short", "Short"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="pending",
    )

    _qty_positive = models.Constraint("CHECK (qty > 0)", "Wave line quantity must be positive")
    _picked_bound = models.Constraint(
        "CHECK (picked_qty >= 0 AND picked_qty <= qty)",
        "Picked quantity must be between 0 and the wave quantity",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "reserved_qty",
            "picked_qty",
            "picked_by_id",
            "picked_at",
            "state",
            "scanned_bin",
            "scanned_item",
        }

    def action_scan_pick(self, bin_code=None, item_code=None):
        """BRU-WMS-05: pick one line by scanning its bin and the item. The
        scans must name the line's bin (barcode or name) and its part
        (barcode, QR or part number); they are kept as the pick evidence."""
        for line in self:
            if line.state != "pending":
                raise UserError("Wave line %s is already %s." % (line.id, line.state))
            bin_code = (bin_code or "").strip()
            item_code = (item_code or "").strip()
            bin_record = line.bin_id
            if not bin_code or bin_code not in {bin_record.barcode or "", bin_record.name or ""}:
                raise UserError(
                    "Scanned bin %r is not the pick bin %s." % (bin_code, bin_record.name)
                )
            part = line.part_id
            if not item_code or item_code not in {
                part.barcode or "",
                part.qr_code or "",
                part.part_number or "",
            }:
                raise UserError("Scanned item %r is not %s." % (item_code, part.part_number))
            wave = line.wave_id
            if wave.state not in ("released", "picking"):
                raise UserError("Wave %s is not released." % wave.name)
            wave._pick_lines(line)
            line._guarded().write({"scanned_bin": bin_code, "scanned_item": item_code})
        return True

    def _refuse_unless_draft(self, waves):
        if not self._fix_guard_open() and waves.filtered(lambda w: w.state != "draft"):
            raise UserError(
                "The lines of a released wave are final: they cannot be added, edited or "
                "deleted (A06 audit M41-11)."
            )

    @api.model_create_multi
    def create(self, vals_list):
        ids = {v.get("wave_id") for v in vals_list if v.get("wave_id")}
        self._refuse_unless_draft(self.env["fix.wms.wave"].browse(list(ids)))
        return super().create(vals_list)

    def write(self, vals):
        if self:
            self._refuse_unless_draft(self.mapped("wave_id"))
        return super().write(vals)

    def unlink(self):
        self._refuse_unless_draft(self.mapped("wave_id"))
        return super().unlink()


class FixWmsCarton(models.Model):
    _name = "fix.wms.carton"
    _description = "Packing Carton"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    wave_id = fields.Many2one("fix.wms.wave", string="Wave", ondelete="set null", index=True)
    carton_size = fields.Selection(
        [("s", "Small"), ("m", "Medium"), ("l", "Large"), ("xl", "XL")],
        required=True,
        default="m",
    )
    weight_kg = fields.Float(string="Weight (kg)")
    contents_qty = fields.Integer(string="Contents (pcs)")
    state = fields.Selection(
        [("open", "Open"), ("sealed", "Sealed"), ("dispatched", "Dispatched")],
        required=True,
        default="open",
    )
    sealed_by_id = fields.Many2one("res.users", string="Sealed By", readonly=True)

    _weight_positive = models.Constraint(
        "CHECK (weight_kg >= 0 AND contents_qty >= 0)",
        "Packing weights and counts cannot be negative",
    )

    _DOC = ("wave_id", "carton_size", "weight_kg", "contents_qty")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "sealed_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state not in (False, "open"):
            locked |= set(self._DOC)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.wms.carton") or "CART/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in self._DOC if k in vals}
            if frozen and _differs(self.filtered(lambda c: c.state != "open"), frozen):
                raise UserError("A sealed carton is final.")
        return super().write(vals)

    def action_seal(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Seal an open carton")
            wave = rec.wave_id
            if not wave or wave.state != "picking":
                raise UserError("A carton is sealed for a wave that is being picked and packed.")
            if rec.contents_qty <= 0 or (rec.weight_kg or 0.0) <= 0:
                raise UserError("Record the carton's contents and weight before sealing it.")
            already = sum(
                wave.carton_ids.filtered(lambda c, me=rec: c.state == "sealed" and c != me).mapped(
                    "contents_qty"
                )
            )
            picked = wave._picked_total()
            if already + rec.contents_qty > picked + EPS:
                raise UserError(
                    "Wave %s picked %s; sealing %s more would pack %s (contents must "
                    "reconcile to the picked lines)."
                    % (wave.name, picked, rec.contents_qty, already + rec.contents_qty)
                )
            rec._guarded().write({"state": "sealed", "sealed_by_id": self.env.user.id})
        return True


class FixWmsStage(models.Model):
    _name = "fix.wms.stage"
    _description = "Staging & Load"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    wave_id = fields.Many2one("fix.wms.wave", string="Wave", ondelete="set null", index=True)
    lane = fields.Char(string="Staging Lane", required=True)
    load_ref = fields.Char(string="Load / Vehicle Ref")
    state = fields.Selection(
        [("staging", "Staging"), ("loaded", "Loaded"), ("dispatched", "Dispatched")],
        required=True,
        default="staging",
    )
    loaded_by_id = fields.Many2one("res.users", string="Loaded By", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "loaded_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state not in (False, "staging"):
            locked |= {"wave_id", "lane", "load_ref"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.wms.stage") or "STAG/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in ("wave_id", "lane", "load_ref") if k in vals}
            if frozen and _differs(self.filtered(lambda s: s.state != "staging"), frozen):
                raise UserError("A loaded staging record is final.")
        return super().write(vals)

    def action_load(self):
        for rec in self:
            if rec.state != "staging":
                raise UserError("Load a staging record")
            if not rec.wave_id or rec.wave_id.state != "staged":
                raise UserError("Only a staged wave is loaded (stage the packed wave first).")
            if not (rec.load_ref or "").strip():
                raise UserError("Record the load / vehicle reference before loading.")
            rec._guarded().write({"state": "loaded", "loaded_by_id": self.env.user.id})
        return True

    def action_dispatch(self):
        """Dispatching the load ships its wave (one path: the wave's ship)."""
        for rec in self:
            if rec.state != "loaded":
                raise UserError("Dispatch a loaded record")
            rec.wave_id.action_ship()
        return True


class FixWmsTask(models.Model):
    _name = "fix.wms.task"
    _description = "Warehouse Task"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    task_type = fields.Selection(
        [("pick", "Pick"), ("putaway", "Put-Away"), ("count", "Count"), ("replenish", "Replenish")],
        required=True,
        default="pick",
    )
    ref = fields.Char(string="Reference")
    part_id = fields.Many2one("fix.spare.part", string="Spare Part", ondelete="set null")
    bin_id = fields.Many2one("fix.warehouse.bin", string="Bin", ondelete="set null")
    qty = fields.Float(string="Quantity")
    wave_line_id = fields.Many2one("fix.wms.wave.line", string="Wave Line", ondelete="set null")
    putaway_id = fields.Many2one("fix.wms.putaway", string="Put-Away", ondelete="set null")
    floor_count_id = fields.Many2one(
        "fix.wms.floor.count", string="Floor Count", ondelete="set null"
    )
    assignee_id = fields.Many2one("hr.employee", string="Assignee")
    state = fields.Selection(
        [("open", "Open"), ("assigned", "Assigned"), ("done", "Done"), ("cancelled", "Cancelled")],
        required=True,
        default="open",
    )
    done_at = fields.Datetime(readonly=True)
    done_by_id = fields.Many2one("res.users", string="Done By", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "done_at", "done_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state in ("done", "cancelled"):
            locked |= {"task_type", "part_id", "bin_id", "qty", "assignee_id", "ref"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.wms.task") or "TASK/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {
                k: vals[k]
                for k in (
                    "task_type",
                    "part_id",
                    "bin_id",
                    "qty",
                    "assignee_id",
                    "wave_line_id",
                    "putaway_id",
                )
                if k in vals
            }
            if frozen and _differs(
                self.filtered(lambda t: t.state in ("done", "cancelled")), frozen
            ):
                raise UserError("A completed or cancelled task is final.")
        return super().write(vals)

    def action_assign(self):
        for rec in self:
            if rec.state != "open":
                raise UserError(
                    "Only an open task is assigned (task %s is %s)." % (rec.name, rec.state)
                )
            if not rec.assignee_id:
                raise UserError("Assign a task to a warehouse operator")
            rec._guarded().write({"state": "assigned"})
        return True

    def action_done(self, scan=None, bin_scan=None, item_scan=None):
        """BRU-WMS-14: the assigned operative completes the task, and a task
        that moves stock completes the movement it represents. A pick task
        needs the bin and item scans (BRU-WMS-05): `scan` is "BIN ITEM" as the
        RF device sends it, or give bin_scan / item_scan."""
        if scan and not (bin_scan or item_scan):
            parts = str(scan).replace("|", " ").replace(",", " ").split()
            bin_scan = parts[0] if parts else None
            item_scan = parts[1] if len(parts) > 1 else None
        for rec in self:
            if rec.state != "assigned":
                raise UserError(
                    "Complete an assigned task (task %s is %s)." % (rec.name, rec.state)
                )
            if not self.env.su and rec.assignee_id.user_id != self.env.user:
                raise UserError(
                    "Task %s is assigned to %s: only that operative completes it."
                    % (rec.name, rec.assignee_id.name)
                )
            if rec.task_type == "pick":
                line = rec.wave_line_id
                if not line:
                    raise UserError(
                        "A pick task completes the wave line it picks: link the wave line."
                    )
                if line.state == "pending":
                    line.action_scan_pick(bin_scan, item_scan)
            elif rec.task_type == "putaway":
                if not rec.putaway_id:
                    raise UserError("A put-away task completes its put-away: link it.")
                if rec.putaway_id.state == "pending":
                    rec.putaway_id.action_complete()
            elif rec.task_type == "count":
                if not rec.floor_count_id or rec.floor_count_id.state in (
                    "draft",
                    "recount",
                    "cancelled",
                ):
                    raise UserError("A count task completes with its submitted floor count.")
            rec._guarded().write(
                {"state": "done", "done_at": fields.Datetime.now(), "done_by_id": self.env.user.id}
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state in ("done", "cancelled"):
                raise UserError("Task %s is already closed." % rec.name)
            rec._guarded().write({"state": "cancelled"})
        return True


class FixWmsFloorCount(models.Model):
    """A blind bin-level floor count: the expected quantity is the slot's
    when the count is raised (never typed). A variance outside tolerance is
    recounted, then submitted as an M15 count for Inventory Controller
    approval; the slot moves when that count posts (BRU-WMS-16)."""

    _name = "fix.wms.floor.count"
    _description = "Floor Count (Bin)"
    _order = "counted_on desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    bin_id = fields.Many2one(
        "fix.warehouse.bin", string="Bin", required=True, ondelete="cascade", index=True
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    expected_qty = fields.Float(string="Expected", readonly=True)
    counted_qty = fields.Float(string="Counted")
    variance = fields.Float(compute="_compute_variance", store=True, string="Variance")
    reason_code = fields.Selection(
        [
            ("damage", "Damage / breakage"),
            ("loss", "Loss / theft"),
            ("misplaced", "Misplaced / wrong bin"),
            ("unrecorded_move", "Unrecorded movement"),
            ("other", "Other"),
        ],
        string="Variance Reason",
    )
    recount_requested = fields.Boolean(readonly=True, copy=False)
    stock_count_id = fields.Many2one(
        "fix.stock.count", string="M15 Count", readonly=True, copy=False
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("recount", "Recount Required"),
            ("submitted", "Submitted to M15"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    counted_by_id = fields.Many2one("res.users", string="Counted By", readonly=True)
    counted_on = fields.Date(required=True, default=fields.Date.context_today)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "expected_qty",
            "recount_requested",
            "stock_count_id",
            "counted_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= {"bin_id", "part_id"}
            if self.state not in ("draft", "recount"):
                locked |= {"counted_qty", "reason_code", "counted_on"}
        return locked

    @api.depends("expected_qty", "counted_qty")
    def _compute_variance(self):
        for rec in self:
            rec.variance = round((rec.counted_qty or 0.0) - (rec.expected_qty or 0.0), 3)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.wms.floor.count") or "FLCT/New"
                )
            vals.pop("expected_qty", None)  # the slot's, never typed
        records = super().create(vals_list)
        Slot = self.env["fix.wms.slot"]
        for rec in records:
            slot = Slot._slot_for(rec.part_id, rec.bin_id)
            rec._guarded().write({"expected_qty": slot.qty if slot else 0.0})
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in ("bin_id", "part_id") if k in vals}
            if frozen and _differs(self, frozen):
                raise UserError("Raise a new floor count for another bin or part.")
            later = {k: vals[k] for k in ("counted_qty", "reason_code", "counted_on") if k in vals}
            if later and _differs(
                self.filtered(lambda r: r.state not in ("draft", "recount")), later
            ):
                raise UserError("A submitted floor count is final.")
        return super().write(vals)

    def _within_tolerance(self):
        self.ensure_one()
        pct = inv_param(self.env, PARAM_COUNT_TOLERANCE_PCT, 0.0)
        return (
            abs(self.variance) <= EPS
            or abs(self.variance) <= abs(self.expected_qty) * pct / 100.0 + EPS
        )

    def action_post(self):
        for rec in self:
            if rec.state not in ("draft", "recount"):
                raise UserError("Post a draft floor count")
            check_quantity(rec.part_id, rec.counted_qty, "counted quantity", allow_zero=True)
            if rec.state == "draft":
                rec._guarded().write({"counted_by_id": self.env.user.id})
            if abs(rec.variance) <= EPS:
                rec._guarded().write({"state": "posted"})
                continue
            if not rec._within_tolerance() and not rec.recount_requested:
                rec._guarded().write({"state": "recount", "recount_requested": True})
                continue
            if not rec._within_tolerance() and not rec.reason_code:
                raise UserError(
                    "Floor count %s is still outside tolerance after the recount: give the "
                    "variance reason." % rec.name
                )
            rec._submit_to_m15()
        return True

    def _submit_to_m15(self):
        """Hand the bin variance to M15 as a count of the warehouse location:
        counted = the location's on-hand + this bin's variance. Created in
        the counter's name so he can never approve it."""
        self.ensure_one()
        location = _bin_location(self.bin_id)
        cls = location_class(location)
        Count = self.env["fix.stock.count"].sudo()
        bucket = self.env["fix.stock.onhand"]._bucket(self.part_id, location, cls)
        on_hand = bucket.qty if bucket else 0.0
        count = Count.create(
            {
                "location_id": location.id,
                "company_id": location.company_id.id or self.company_id.id,
                "operating_unit_id": location.operating_unit_id.id or False,
                "count_type": "cycle",
                "reason_code": "other",
                "reason_note": "Floor count %s (bin %s): %s"
                % (self.name, self.bin_id.name, self.reason_code or "within tolerance"),
                "line_ids": [
                    (0, 0, {"part_id": self.part_id.id, "counted_qty": on_hand + self.variance})
                ],
            }
        )
        count.line_ids._guarded().write({"floor_count_id": self.id})
        if self._within_tolerance():
            count.with_user(self.env.user).sudo().action_submit()
        else:
            # the floor recount already happened: straight to approval
            count.line_ids._guarded().write({"recount_qty": on_hand + self.variance})
            count._guarded().write(
                {
                    "state": "to_approve",
                    "recount_requested": True,
                    "counted_by_id": self.env.user.id,
                    "submitted_at": fields.Datetime.now(),
                    "requested_by_id": self.env.user.id,
                    "requested_at": fields.Datetime.now(),
                }
            )
        if self.state not in ("posted",):
            self._guarded().write({"state": "submitted", "stock_count_id": count.id})
        else:
            self._guarded().write({"stock_count_id": count.id})

    def _fix_apply_posted_variance(self, delta):
        """Called when the M15 count posts: the slot follows the ledger."""
        Slot = self.env["fix.wms.slot"]
        for rec in self:
            slot = Slot._slot_for(rec.part_id, rec.bin_id, create=delta > 0)
            if slot:
                slot._guarded().write({"qty": round(max((slot.qty or 0.0) + delta, 0.0), 4)})
            rec._guarded().write({"state": "posted"})

    def _fix_cancel_from_m15(self):
        self._guarded().write({"state": "cancelled"})


class FixWmsWaveTemplate(models.Model):
    _name = "fix.wms.wave.template"
    _description = "Wave Template"
    _order = "name"

    name = fields.Char(required=True)
    strategy = fields.Selection(
        [("single", "Single Order"), ("zone", "Zone Batch"), ("batch", "Batch Picking")],
        required=True,
        default="zone",
    )
    zone_id = fields.Many2one("fix.warehouse.zone", string="Zone")
    cutoff = fields.Char(string="Cut-off (HH:MM)", default="16:00")
    active = fields.Boolean(default=True)


class FixWmsPackingStation(models.Model):
    _name = "fix.wms.packing.station"
    _description = "Packing Station"
    _order = "name"

    name = fields.Char(required=True)
    lane = fields.Char(string="Lane")
    printer = fields.Char(string="Label Printer")
    active = fields.Boolean(default=True)
