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
#
# A06 final pass: pick and put-away confirm by scanning bin and item, whole-wave
# picking is a supervisor's recorded exception, release raises one pick task per
# line and needs the supervisor grant, a wave can be cancelled (reservations and
# picked stock go back), a block closes the whole bin, ship needs a scanned
# carton manifest, and serials follow the stock from bin to shipment.
from datetime import timedelta

from odoo import api, fields, models
from odoo.addons.cd_wms_structure.models.fix_wms_layout import may_configure
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_inventory_approval import (
    CONTROLLER_GROUP,
    SUPERVISOR_GROUP,
    check_location_usable,
    check_quantity,
    inv_param,
    is_supervisor,
    location_class,
    part_codes,
    require_supervisor,
)

EPS = 1e-6
# F31: zones a put-away never stores stock in, whatever the override says
NO_PUTAWAY_ZONE_TYPES = ("inspection", "quarantine", "returns", "staging", "dispatch", "receiving")
# O4 (A06 ERP audit 20 Nov 2026): a WMS bin count has its own tolerance, 0 by
# default: every bin variance is recounted and then approved by a second person.
PARAM_WMS_COUNT_TOLERANCE_PCT = "cd_inventory.wms_count_tolerance_pct"
# O6 / F03: the ownership class a slot's stock is booked in. A bin of class "any"
# holds OWNED stock only; any other class needs a bin of that very class.
SLOT_CLASSES = [
    ("owned", "Owned Stock"),
    ("consignment", "Supplier Consignment"),
    ("customer", "Customer Property"),
    ("bench", "Bench / WIP"),
    ("warranty", "Warranty Reserve"),
]
# F08 / F12: a slot under one of these counts neither moves nor allocates
FROZEN_COUNT_STATES = ("recount", "submitted")
FREEZING_COUNT_TYPES = ("count_back", "zero_cross")
QM_GROUPS = (
    "cd_qms_process.group_qms_quality_manager",
    "cd_equipment_register.group_quality_manager",
)


def bin_class(bin_record) -> str:
    """O6: the class of stock a bin holds (an "any" bin holds owned stock only)."""
    cls = bin_record.sudo().ownership_class or "any"
    return "owned" if cls == "any" else cls


def location_warehouses(env, location):
    if not location:
        return env["fix.warehouse"]
    return env["fix.warehouse"].sudo().search([("stock_location_id", "=", location.id)])


def slotted_qty(env, part, location, slot_cls=None) -> float:
    """What the bins of the warehouse(s) breaking `location` down hold of the
    part (of one ownership class, or of every class)."""
    warehouses = location_warehouses(env, location)
    if not warehouses:
        return 0.0
    domain = [("part_id", "=", part.id), ("bin_id.zone_id.warehouse_id", "in", warehouses.ids)]
    if slot_cls:
        domain.append(("ownership_class", "=", slot_cls))
    return round(sum(env["fix.wms.slot"].sudo().search(domain).mapped("qty")), 4)


def unslotted_qty(env, part, location, slot_cls) -> float:
    """BRU-WMS-01: unrestricted M15 on-hand of the class at the location that no
    bin slot holds yet. A slot may only ever be filled out of this."""
    bucket = env["fix.stock.onhand"]._bucket(part, location, location_class(location, slot_cls))
    on_hand = bucket.qty if bucket else 0.0
    return round(on_hand - slotted_qty(env, part, location, slot_cls), 4)


def check_slot_cap(env, part, location, slot_cls, qty, what):
    """Refuse slotting more than the M15 ledger holds unslotted (F02 / F07)."""
    free = unslotted_qty(env, part, location, slot_cls)
    if qty > free + EPS:
        raise UserError(
            "%s: M15 holds only %s %s of %s at %s outside the bins; %s cannot be slotted. "
            "A bin never holds more than the ledger (BRU-WMS-01)."
            % (what, max(free, 0.0), slot_cls, part.part_number, location.code, qty)
        )


def line_in_inspection(env, line) -> bool:
    """F02 / BRU-WMS-04: a PO receipt posted into the In Inspection status
    waits for its inspection outcome before any of it is put away or moved on."""
    receipt = line.sudo().receipt_id
    if not line or not receipt or not receipt.inspection_held:
        return False
    ref = line.sudo().source_line_ref or ""
    if ref.startswith("PRL:") and "fix.purchase.receipt.line" in env:
        prl = env["fix.purchase.receipt.line"].sudo().browse(int(ref[4:])).exists()
        return bool(prl) and prl.inspection_state == "pending"
    return True


def operative_employee(env):
    return (
        env["hr.employee"]
        .sudo()
        .search([("user_id", "=", env.uid), ("company_id", "in", env.companies.ids)], limit=1)
    )


def require_operative_profile(env, warehouse, zone=None, what="work here"):
    """O7 / F16: a floor action is an operative's of THIS warehouse (an active
    operative profile there, and the zone among the zones worked when the
    profile names any). A supervisor and trusted code are exempt."""
    if env.su or is_supervisor(env) or not warehouse:
        return
    employee = operative_employee(env)
    profile = (
        env["fix.wms.operative"]
        .sudo()
        .search(
            [
                ("employee_id", "=", employee.id or 0),
                ("warehouse_id", "=", warehouse.id),
                ("active", "=", True),
            ],
            limit=1,
        )
    )
    if not profile:
        raise AccessError(
            "You hold no operative profile at warehouse %s: only its operatives %s (T-13)."
            % (warehouse.name, what)
        )
    if zone and profile.zone_ids and zone not in profile.zone_ids:
        raise AccessError(
            "Your profile at %s does not cover zone %s (T-13)." % (warehouse.name, zone.name)
        )


def may_block(env) -> bool:
    """O5 / F24: a Warehouse Supervisor (or Inventory Controller) or the Quality
    Manager blocks a bin; operatives report one."""
    if env.su or is_supervisor(env) or env.user.has_group(CONTROLLER_GROUP):
        return True
    groups = env.user.sudo().all_group_ids
    for xmlid in QM_GROUPS:
        group = env.ref(xmlid, raise_if_not_found=False)
        if group and group in groups:
            return True
    return False


def _scan_bin(bin_record, code):
    """BRU-WMS-05: the scan must read this bin (barcode or name)."""
    code = (code or "").strip()
    if not code or code not in {bin_record.barcode or "", bin_record.name or ""}:
        raise UserError("Scanned bin %r is not the bin %s." % (code, bin_record.name))
    return code


def _scan_item(part, code):
    """BRU-WMS-05: the scan must read this part (barcode, QR, part number)."""
    code = (code or "").strip()
    if not code or code not in part_codes(part):
        raise UserError("Scanned item %r is not %s." % (code, part.part_number))
    return code


def _refuse_reassign(records, vals):
    """BRU-WMS-14: a task has one operative. A free task may be claimed by the
    operative himself; taking it from someone, or handing it to someone else, is
    a supervisor's reassignment."""
    if "assignee_id" not in vals or not records or records._fix_guard_open():
        return
    if is_supervisor(records.env):
        return
    me = records.env.user
    for rec in records:
        if not rec._fix_guard_differs("assignee_id", vals["assignee_id"], rec.assignee_id):
            continue
        target = records.env["hr.employee"].sudo().browse(vals["assignee_id"] or 0)
        if rec.assignee_id or target.user_id != me:
            raise AccessError(
                "%s: only a Warehouse Supervisor reassigns work (BRU-WMS-14)." % rec.name
            )


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

    # F06: one warehouse breaks a location down (two would double-slot it)
    _stock_location_unique = models.Constraint(
        "UNIQUE (stock_location_id)", "An M15 location is broken down by one warehouse only"
    )

    _LEDGER_TIES = ("stock_location_id", "company_id", "operating_unit_id")

    def _fix_holds_stock(self) -> bool:
        """A bin of this warehouse holds or has allocated stock."""
        return bool(
            self.env["fix.wms.slot"]
            .sudo()
            .search_count(
                [
                    ("bin_id.zone_id.warehouse_id", "in", self.ids),
                    "|",
                    ("qty", ">", EPS),
                    ("reserved_qty", ">", EPS),
                ]
            )
        )

    @api.model_create_multi
    def create(self, vals_list):
        if any(v.get("stock_location_id") for v in vals_list) and not may_configure(self.env):
            raise AccessError(
                "Only a Warehouse Supervisor or the IT administrator ties a warehouse to its "
                "M15 location (F06)."
            )
        return super().create(vals_list)

    def write(self, vals):
        """F06: the fields that tie the bins to the ledger are a supervisor's or the
        IT administrator's, and frozen once a bin holds stock."""
        tied = [k for k in self._LEDGER_TIES if k in vals]
        if self and tied and not self.env.su:
            changing = self.filtered(
                lambda r: any((r[k].id or False) != (vals[k] or False) for k in tied)
            )
            if changing and not may_configure(self.env):
                raise AccessError(
                    "Only a Warehouse Supervisor or the IT administrator changes a warehouse's "
                    "M15 location, company or operating unit (F06)."
                )
            if changing and changing._fix_holds_stock():
                raise UserError(
                    "Warehouse %s holds stock in its bins: its M15 location, company and "
                    "operating unit are frozen until the bins are empty (BRU-WMS-01)."
                    % changing[0].name
                )
        return super().write(vals)


def _bin_location(bin_record):
    warehouse = bin_record.zone_id.warehouse_id
    location = warehouse.stock_location_id
    if not location:
        raise UserError(
            "Warehouse %s is not linked to an M15 stock location: set its M15 Stock "
            "Location before moving stock through its bins (BRU-WMS-01)." % warehouse.name
        )
    return location


class FixWarehouseBinBlock(models.Model):
    """BRU-WMS-12 (A06 final pass B11): a block closes the BIN, for every part
    and for a bin with no slot yet; a controller who did not block it reopens it."""

    _name = "fix.warehouse.bin"
    _inherit = ["fix.warehouse.bin", "fix.inventory.approval.mixin"]

    blocked = fields.Boolean(readonly=True, copy=False)
    block_reason = fields.Char(string="Block Reason", readonly=True, copy=False)
    # O5 / F24: the floor REPORTS a bin it finds unusable; a supervisor or the
    # Quality Manager decides the block
    block_reported_by_id = fields.Many2one(
        "res.users", string="Block Reported By", readonly=True, copy=False
    )
    block_reported_at = fields.Datetime(string="Block Reported On", readonly=True, copy=False)
    block_report_reason = fields.Char(string="Reported Problem", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "blocked",
            "block_reason",
            "block_reported_by_id",
            "block_reported_at",
            "block_report_reason",
        }

    def action_report_block(self, reason=None):
        """O5: an operative (or an RF exception) reports a bin that cannot be used.
        Nothing is blocked: a Warehouse Supervisor or the Quality Manager decides."""
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say what is wrong with the bin.")
        for rec in self:
            if rec._fix_is_blocked():
                raise UserError("Bin %s is already blocked." % rec.name)
            rec._guarded().write(
                {
                    "block_reported_by_id": self.env.user.id,
                    "block_reported_at": fields.Datetime.now(),
                    "block_report_reason": reason,
                }
            )
        return True

    def _inv_excluded_users(self):
        # the blocker never unblocks his own block
        return self.requested_by_id

    def _inv_approval_label(self) -> str:
        self.ensure_one()
        return "unblocking bin %s" % self.name

    def _fix_is_blocked(self):
        """Blocked here, or on one of its slots (a block raised before the block
        moved to the bin still closes it)."""
        self.ensure_one()
        rec = self.sudo()
        return rec.blocked or bool(
            self.env["fix.wms.slot"]
            .sudo()
            .search_count([("bin_id", "=", rec.id), ("state", "=", "blocked")])
        )

    def action_block(self, reason=None):
        if not may_block(self.env):
            raise AccessError(
                "Only a Warehouse Supervisor or the Quality Manager blocks a bin; report the "
                "problem instead (Report Bin Problem, spec section 13)."
            )
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Give the reason the bin is blocked.")
        for rec in self:
            if rec._fix_is_blocked():
                raise UserError("Bin %s is already blocked." % rec.name)
            rec._inv_stamp_request()
            rec._guarded().write(
                {
                    "blocked": True,
                    "block_reason": reason,
                    "block_reported_by_id": False,
                    "block_reported_at": False,
                    "block_report_reason": False,
                }
            )
            slots = self.env["fix.wms.slot"].sudo().search([("bin_id", "=", rec.id)])
            slots._inv_stamp_request()
            slots._guarded().write({"state": "blocked", "block_reason": reason})
        return True

    def action_unblock(self, note=None):
        for rec in self:
            if not rec._fix_is_blocked():
                raise UserError("Bin %s is not blocked." % rec.name)
        self._inv_check_approver()
        for rec in self.sudo():
            rec._fix_open_bin(note)
        return True

    def _fix_open_bin(self, note):
        self.ensure_one()
        self._inv_stamp_approval(note)
        self._guarded().write({"blocked": False})
        slots = (
            self.env["fix.wms.slot"]
            .sudo()
            .search([("bin_id", "=", self.id), ("state", "=", "blocked")])
        )
        slots._inv_stamp_approval(note)
        slots._guarded().write({"state": "active"})


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
    company_id = fields.Many2one(
        related="bin_id.zone_id.warehouse_id.company_id", string="Company", store=True, index=True
    )
    qty = fields.Float(string="Quantity in Bin", readonly=True)
    reserved_qty = fields.Float(string="Allocated to Waves", readonly=True)
    ownership_class = fields.Selection(
        SLOT_CLASSES,
        string="Ownership Class",
        compute="_compute_ownership_class",
        store=True,
        index=True,
        help="O6 / F03: the M15 class this slot's stock is booked in: the bin's own class "
        "(an 'any' bin holds owned stock only). Every ledger call of the slot uses it.",
    )
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

    @api.depends("bin_id.ownership_class")
    def _compute_ownership_class(self):
        for slot in self:
            slot.ownership_class = bin_class(slot.bin_id) if slot.bin_id else "owned"

    def _fix_ledger_class(self, location):
        """The M15 class the slot moves (owned at a van location is `van`)."""
        self.ensure_one()
        return location_class(location, self.ownership_class or "owned")

    def _fix_open_count(self):
        """F08 / F12: the floor count that freezes this slot: one being recounted
        or awaiting its M15 approval, or an open count-back / zero-crossing."""
        self.ensure_one()
        return (
            self.env["fix.wms.floor.count"]
            .sudo()
            .search(
                [
                    ("part_id", "=", self.part_id.id),
                    ("bin_id", "=", self.bin_id.id),
                    "|",
                    ("state", "in", FROZEN_COUNT_STATES),
                    "&",
                    ("state", "=", "draft"),
                    ("count_type", "in", FREEZING_COUNT_TYPES),
                ],
                limit=1,
            )
        )

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
            bin_record = slot.bin_id
            if slot.state == "blocked" or bin_record._fix_is_blocked():
                raise UserError(
                    "Bin %s is blocked (%s): nothing can be picked from or put into it until "
                    "an Inventory Controller unblocks it (BRU-WMS-12)."
                    % (
                        bin_record.name,
                        slot.block_reason or bin_record.sudo().block_reason or "no reason",
                    )
                )
            if not slot.bin_id.zone_id.reservable:
                raise UserError(
                    "Bin %s is in the %s zone: its stock is not reservable or pickable "
                    "(BRU-INV-08 / BRU-WMS-04)." % (slot.bin_id.name, slot.bin_id.zone_id.zone_type)
                )
            counting = slot.id and slot._fix_open_count()
            if counting:
                raise UserError(
                    "Bin %s is being counted for %s (%s): nothing moves in or out of it until "
                    "the count is settled (BRU-WMS-07/16)."
                    % (slot.bin_id.name, slot.part_id.part_number, counting.name)
                )

    def action_block(self, reason=None):
        """The button on a slot row blocks the slot's whole bin (BRU-WMS-12)."""
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Give the reason the bin is blocked.")
        for slot in self:
            if slot.state != "active":
                raise UserError("Slot %s is already blocked." % slot.bin_id.name)
        self.mapped("bin_id").action_block(reason)
        return True

    def action_unblock(self, note=None):
        for slot in self:
            if slot.state != "blocked":
                raise UserError("Slot %s is not blocked." % slot.bin_id.name)
        self._inv_check_approver()
        for bin_record in self.sudo().mapped("bin_id"):
            bin_record._fix_open_bin(note)
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
    # F07: stock that ARRIVED BY M15 TRANSFER is put away from the transfer line
    transfer_line_id = fields.Many2one(
        "fix.stock.transfer.line",
        string="Received Transfer Line",
        ondelete="restrict",
        help="The received M15 transfer line whose stock is put away (stock that arrived "
        "from another location rather than from a supplier).",
    )
    lot_id = fields.Many2one("fix.stock.lot", string="Serial / Lot", ondelete="restrict")
    from_ref = fields.Char(string="Source Reference")
    assignee_id = fields.Many2one("hr.employee", string="Assigned To")
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done"), ("cancelled", "Cancelled")],
        required=True,
        default="pending",
    )
    cancel_reason = fields.Char(string="Cancellation Reason", readonly=True, copy=False)
    done_at = fields.Datetime(readonly=True)
    done_by_id = fields.Many2one("res.users", string="Done By", readonly=True)
    scanned_bin = fields.Char(string="Scanned Bin", readonly=True, copy=False)
    scanned_item = fields.Char(string="Scanned Item", readonly=True, copy=False)

    _qty_positive = models.Constraint("CHECK (qty > 0)", "Put-away quantity must be positive")

    _DOC = (
        "part_id",
        "qty",
        "to_bin_id",
        "receipt_line_id",
        "transfer_line_id",
        "lot_id",
        "company_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "done_at",
            "done_by_id",
            "scanned_bin",
            "scanned_item",
            "cancel_reason",
        }

    # ---------------------------------------------------------------- source
    def _fix_source_location(self):
        """The M15 location the put-away's stock was received at."""
        self.ensure_one()
        if self.receipt_line_id:
            return self.receipt_line_id.receipt_id.location_id
        if self.transfer_line_id:
            return self.transfer_line_id.transfer_id.to_location_id
        return self.env["fix.stock.location"]

    def _fix_source_class(self) -> str:
        """The ownership class the stock was received in (a transfer receives owned)."""
        self.ensure_one()
        if self.receipt_line_id:
            return self.receipt_line_id.receipt_id.ownership_class or "owned"
        return "owned"

    def _fix_source_name(self) -> str:
        self.ensure_one()
        if self.receipt_line_id:
            return self.receipt_line_id.receipt_id.name
        return self.transfer_line_id.transfer_id.name or "-"

    def _fix_in_inspection(self) -> bool:
        self.ensure_one()
        return line_in_inspection(self.env, self.receipt_line_id)

    def _fix_check_source(self, location):
        """The put-away's stock was received at this location and is not yet
        all put away (F02, F07, BRU-WMS-04)."""
        self.ensure_one()
        line, tline = self.receipt_line_id, self.transfer_line_id
        if line and tline:
            raise UserError("A put-away puts away one received line: a receipt or a transfer.")
        if line:
            if line.receipt_id.state != "posted":
                raise UserError(
                    "Put-away %s needs the POSTED goods-receipt line it puts away: only "
                    "stock that was received and passed inspection is put away (BRU-WMS-04)."
                    % self.name
                )
            if self._fix_in_inspection():
                raise UserError(
                    "Receipt %s is still in inspection: its stock is put away once the "
                    "inspection outcome is recorded (BRU-WMS-04)." % line.receipt_id.name
                )
            src_part = line.part_id
        elif tline:
            if tline.transfer_id.state not in ("received", "discrepancy"):
                raise UserError(
                    "Transfer %s has not been received here: only stock that arrived is put "
                    "away (BRU-WMS-04)." % tline.transfer_id.name
                )
            src_part = tline.part_id
        else:
            raise UserError(
                "Put-away %s needs the POSTED goods-receipt line (or the received M15 "
                "transfer line) it puts away; stock already on hand is slotted by a "
                "supervisor's opening slot load (BRU-WMS-04)." % self.name
            )
        if src_part != self.part_id:
            raise UserError(
                "%s is for %s, not %s."
                % (self._fix_source_name(), src_part.part_number, self.part_id.part_number)
            )
        source_location = self._fix_source_location()
        if source_location != location:
            raise UserError(
                "%s was received at %s; bin %s belongs to %s."
                % (
                    self._fix_source_name(),
                    source_location.code,
                    self.to_bin_id.name,
                    location.code,
                )
            )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state in ("done", "cancelled"):
            locked |= set(self._DOC) | {"from_ref", "assignee_id"}
        elif len(self) == 1 and self.assignee_id and not self.env.user.has_group(SUPERVISOR_GROUP):
            locked |= {"assignee_id"}
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
            if frozen and _differs(self.filtered(lambda r: r.state != "pending"), frozen):
                raise UserError("A completed or cancelled put-away is final.")
            _refuse_reassign(self, vals)
        return super().write(vals)

    def _remaining_on_line(self, line):
        done = self.sudo().search(
            [("receipt_line_id", "=", line.id), ("state", "=", "done"), ("id", "not in", self.ids)]
        )
        return round((line.qty_accepted or 0.0) - sum(done.mapped("qty")), 4)

    def _remaining_on_transfer_line(self, tline):
        done = self.sudo().search(
            [
                ("transfer_line_id", "=", tline.id),
                ("state", "=", "done"),
                ("id", "not in", self.ids),
            ]
        )
        return round((tline.received_qty or 0.0) - sum(done.mapped("qty")), 4)

    def action_cancel(self, reason=None):
        """F30: a supervisor cancels a pending put-away, with a reason."""
        require_supervisor(self.env, "cancel a put-away")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Record why the put-away is cancelled.")
        for rec in self:
            if rec.state != "pending":
                raise UserError("Put-away %s is already %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason})
            self.env["fix.wms.task"].sudo().search(
                [("putaway_id", "=", rec.id), ("state", "in", ("open", "assigned"))]
            )._guarded().write({"state": "cancelled"})
        return True

    def action_complete(self, bin_code=None, item_code=None):
        """BRU-WMS-05: the operative confirms the put-away by scanning the target
        bin and the item (trusted system code has no scanner)."""
        Slot = self.env["fix.wms.slot"]
        for rec in self:
            if rec.state != "pending":
                raise UserError("Complete a pending put-away")
            evidence = {}
            if not self.env.su:
                evidence = {
                    "scanned_bin": _scan_bin(rec.to_bin_id, bin_code),
                    "scanned_item": _scan_item(rec.part_id, item_code),
                }
            check_quantity(rec.part_id, rec.qty, "put-away quantity")
            if (
                not self.env.su
                and rec.assignee_id.user_id
                and rec.assignee_id.user_id != self.env.user
            ):
                raise UserError(
                    "Put-away %s is assigned to %s (BRU-WMS-14)." % (rec.name, rec.assignee_id.name)
                )
            location = _bin_location(rec.to_bin_id)
            require_operative_profile(
                self.env, rec.to_bin_id.zone_id.warehouse_id, rec.to_bin_id.zone_id, "put away"
            )
            rec._fix_check_source(location)
            line = rec.receipt_line_id
            if line:
                remaining = rec._remaining_on_line(line)
            else:
                remaining = rec._remaining_on_transfer_line(rec.transfer_line_id)
            if rec.qty > remaining + EPS:
                raise UserError(
                    "Only %s of %s remains to be put away; %s cannot be."
                    % (remaining, rec._fix_source_name(), rec.qty)
                )
            if rec.part_id.is_serialized and (
                not rec.lot_id or rec.lot_id.part_id != rec.part_id or abs(rec.qty - 1.0) > EPS
            ):
                raise UserError(
                    "%s is serialized: put away one unit with its serial (BRU-WMS-10)."
                    % rec.part_id.part_number
                )
            if rec.lot_id and rec.part_id.is_serialized:
                rec.lot_id._fix_check_movable(rec.part_id, location)
            if (rec.part_id.storage_class or "general") == "hazardous" and (
                rec.to_bin_id.storage_class != "hazardous"
            ):
                raise UserError(
                    "%s is hazardous: it goes only into a hazardous-class bin, not %s "
                    "(BRU-WMS-11)." % (rec.part_id.part_number, rec.to_bin_id.name)
                )
            received_class = rec._fix_source_class()
            if bin_class(rec.to_bin_id) != received_class:
                # O6: an "any" bin holds owned stock only; other classes need their own
                raise UserError(
                    "Bin %s holds %s stock only; %s received %s stock (BRU-WMS-03)."
                    % (
                        rec.to_bin_id.name,
                        bin_class(rec.to_bin_id),
                        rec._fix_source_name(),
                        received_class,
                    )
                )
            # F02: never more than the ledger holds outside the bins
            check_slot_cap(
                self.env, rec.part_id, location, received_class, rec.qty, "Put-away %s" % rec.name
            )
            slot = Slot._slot_for(rec.part_id, rec.to_bin_id, create=True)
            slot._check_pickable()
            zone = rec.to_bin_id.zone_id
            if zone.zone_type in NO_PUTAWAY_ZONE_TYPES:
                # F31: no override, approved or not, stores stock in these zones
                raise UserError(
                    "Bin %s is in the %s zone: stock is not stored there (FR-WMS-013)."
                    % (rec.to_bin_id.name, zone.zone_type)
                )
            slot._guarded().write(
                {
                    "qty": (slot.qty or 0.0) + rec.qty,
                    "last_slotted_on": fields.Date.context_today(self),
                }
            )
            rec._guarded().write(
                {
                    "state": "done",
                    "done_at": fields.Datetime.now(),
                    "done_by_id": self.env.user.id,
                    **evidence,
                }
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
                    "receipt": rec._fix_source_name(),
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
            ("cancelled", "Cancelled"),
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
    pick_all_reason = fields.Char(string="Pick-All Exception Reason", readonly=True, copy=False)
    pick_all_by_id = fields.Many2one(
        "res.users", string="Pick-All Exception By", readonly=True, copy=False
    )
    cancel_reason = fields.Char(string="Cancellation Reason", readonly=True, copy=False)
    cancelled_by_id = fields.Many2one("res.users", string="Cancelled By", readonly=True, copy=False)
    cancelled_at = fields.Datetime(string="Cancelled On", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "released_at",
            "released_by_id",
            "shipped_at",
            "shipped_by_id",
            "pick_all_reason",
            "pick_all_by_id",
            "cancel_reason",
            "cancelled_by_id",
            "cancelled_at",
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
        """BRU-WMS-13: release only what M15 can allocate. A supervisor releases
        (spec section 13); every line becomes one pick task on the RF queue."""
        require_supervisor(self.env, "release a wave")
        Onhand = self.env["fix.stock.onhand"]
        Slot = self.env["fix.wms.slot"]
        Task = self.env["fix.wms.task"].sudo()
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
            for line in rec.line_ids:
                check_quantity(line.part_id, line.qty, "wave quantity")
                slot = Slot._slot_for(line.part_id, line.bin_id)
                if not slot:
                    raise UserError(
                        "Bin %s holds no %s: the line cannot be allocated."
                        % (line.bin_id.name, line.part_id.part_number)
                    )
                slot._check_pickable()
                # F03: the slot's own class is what M15 allocates
                cls = slot._fix_ledger_class(location)
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
                Task.create(
                    {
                        "company_id": rec.company_id.id,
                        "task_type": "pick",
                        "ref": rec.name,
                        "wave_line_id": line.id,
                        "part_id": line.part_id.id,
                        "bin_id": line.bin_id.id,
                        "qty": line.qty,
                    }
                )
            rec._guarded().write(
                {
                    "state": "released",
                    "warehouse_id": warehouse.id,
                    "released_at": fields.Datetime.now(),
                    "released_by_id": self.env.user.id,
                }
            )
            publish(
                self.env,
                "wh.wave_released",
                "fix.wms.wave",
                rec.id,
                {"wave": rec.name, "lines": len(rec.line_ids), "strategy": rec.strategy},
            )
        return True

    def _pick_lines(self, lines):
        """Pick the given PENDING lines of this wave: bin -> staged in M15."""
        self.ensure_one()
        Onhand = self.env["fix.stock.onhand"]
        Slot = self.env["fix.wms.slot"]
        Task = self.env["fix.wms.task"]
        _warehouse, location = self._wave_location()
        now = fields.Datetime.now()
        for line in lines.filtered(lambda ln: ln.state == "pending"):
            slot = Slot._slot_for(line.part_id, line.bin_id)
            if not slot:
                raise UserError(
                    "Bin %s holds no %s." % (line.bin_id.name, line.part_id.part_number)
                )
            slot._check_pickable()
            cls = slot._fix_ledger_class(location)
            picked = min(line.qty or 0.0, slot.qty or 0.0)
            # FR-WMS-024: the operative found less in the bin than the ledger
            # says (action_scan_short_pick); the count-back settles the bin
            found = (self.env.context.get("fix_found_qty") or {}).get(line.id)
            if found is not None:
                picked = min(picked, max(found, 0.0))
            if line.lot_id and picked > EPS:
                line.lot_id._fix_move("staged")
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
            # the line's pick task (raised at release) is finished with the line
            Task.sudo().search(
                [("wave_line_id", "=", line.id), ("state", "in", ("open", "assigned"))]
            )._guarded().write(
                {"state": "done", "done_at": now, "done_by_id": self.env.user.id, "qty": picked}
            )
            if short:
                publish(
                    self.env,
                    "wh.short_pick",
                    "fix.wms.wave.line",
                    line.id,
                    {
                        "wave": self.name,
                        "part_id": line.part_id.id,
                        "bin_id": line.bin_id.id,
                        "requested": line.qty,
                        "picked": picked,
                        "shortfall": round((line.qty or 0.0) - picked, 4),
                    },
                )
                # BRU-WMS-07: a short pick raises an immediate count-back: a blind
                # floor count with its task (F12), which freezes the bin's phantom
                # stock until it is settled
                self.env["fix.wms.floor.count"]._fix_raise_count(
                    line.part_id, line.bin_id, "count_back", "Count-back %s" % self.name
                )
            elif slot.qty <= EPS:
                # BRU-WMS-08: a pick that empties the bin confirms it with a count
                self.env["fix.wms.floor.count"]._fix_raise_count(
                    line.part_id, line.bin_id, "zero_cross", "Zero-crossing %s" % self.name
                )
            if picked > EPS:
                publish(
                    self.env,
                    "wh.pick_confirmed",
                    "fix.wms.wave.line",
                    line.id,
                    {
                        "wave": self.name,
                        "part_id": line.part_id.id,
                        "bin_id": line.bin_id.id,
                        "qty": picked,
                        "serial": line.lot_id.name or None,
                    },
                )
        if self.state == "released":
            self._guarded().write({"state": "picking"})

    def action_pick_all(self, reason=None):
        """Pick every PENDING line WITHOUT scans. BRU-WMS-05 wants a bin and item
        scan on every pick, so this is a supervisor's exception with a recorded
        reason (a scanner is down), never the normal path, and never for a
        serialized part, whose serial must be scanned. Idempotent: lines already
        picked or short are never picked again, so re-running it moves nothing."""
        require_supervisor(self.env, "pick a whole wave without scans")
        reason = (reason or "").strip()
        if not reason and not self.env.su:
            raise UserError("Picking a wave without scans is an exception: record the reason.")
        for rec in self:
            if rec.state not in ("released", "picking"):
                raise UserError("Pick a released wave")
            pending = rec.line_ids.filtered(lambda ln: ln.state == "pending")
            serial = pending.filtered(lambda ln: ln.part_id.is_serialized)
            if serial:
                raise UserError(
                    "%s is serialized: scan-pick it with its serial (BRU-WMS-10)."
                    % serial[0].part_id.part_number
                )
            rec._pick_lines(rec.line_ids)
            if pending:
                rec._guarded().write(
                    {"pick_all_reason": reason, "pick_all_by_id": self.env.user.id}
                )
        return True

    def action_cancel(self, reason=None):
        """M41-5: a supervisor cancels a wave that has not been loaded, with a
        reason: its reservations are released, stock already picked goes back to
        its bin and to unrestricted, serials back in stock, open pick tasks are
        cancelled and sealed cartons reopened."""
        require_supervisor(self.env, "cancel a wave")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Record why the wave is cancelled.")
        Onhand = self.env["fix.stock.onhand"]
        Slot = self.env["fix.wms.slot"]
        Task = self.env["fix.wms.task"].sudo()
        for rec in self:
            if rec.state in ("shipped", "cancelled"):
                raise UserError("Wave %s is already %s." % (rec.name, rec.state))
            if rec.stage_ids.filtered(lambda s: s.state != "staging"):
                raise UserError("Wave %s is loaded: it cannot be cancelled." % rec.name)
            if rec.state != "draft":
                _warehouse, location = rec._wave_location()
                for line in rec.line_ids:
                    slot = Slot._slot_for(line.part_id, line.bin_id, create=True)
                    cls = slot._fix_ledger_class(location)
                    reserved = line.reserved_qty or 0.0
                    picked = line.picked_qty if line.state in ("picked", "short") else 0.0
                    if reserved:
                        Onhand._fix_unreserve(line.part_id, location, cls, reserved, rec.name)
                    if picked > EPS:
                        Onhand._fix_move_status(
                            line.part_id, location, cls, picked, "staged", "unrestricted"
                        )
                    if line.lot_id.sudo().status == "staged":
                        line.lot_id._fix_move("in_stock")
                    slot._guarded().write(
                        {
                            "qty": round((slot.qty or 0.0) + picked, 4),
                            "reserved_qty": round(
                                max((slot.reserved_qty or 0.0) - reserved, 0.0), 4
                            ),
                        }
                    )
            rec.line_ids._guarded().write(
                {"reserved_qty": 0.0, "picked_qty": 0.0, "state": "cancelled"}
            )
            Task.search(
                [("wave_line_id", "in", rec.line_ids.ids), ("state", "in", ("open", "assigned"))]
            )._guarded().write({"state": "cancelled"})
            rec.carton_ids.filtered(lambda c: c.state == "sealed")._guarded().write(
                {"state": "open", "sealed_by_id": False}
            )
            rec._guarded().write(
                {
                    "state": "cancelled",
                    "cancel_reason": reason,
                    "cancelled_by_id": self.env.user.id,
                    "cancelled_at": fields.Datetime.now(),
                }
            )
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
            publish(
                self.env,
                "wh.packed",
                "fix.wms.wave",
                rec.id,
                {"wave": rec.name, "cartons": sealed.mapped("name"), "qty": picked},
            )
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
        reference. F01 / X16 (A06 ERP audit): M41 never takes stock out of the
        ledger itself. Every picked line was handed to the M15 document behind
        it (transfer, RTV or job issue, see fix_wms_ops_spec_flow), which made
        its own ledger movement; a line with no document behind it cannot leave
        the warehouse. wh.shipped is published."""
        for rec in self:
            if rec.state != "staged":
                raise UserError("Ship a staged wave")
            stage = rec.stage_ids.filtered(
                lambda s: s.state == "loaded" and (s.load_ref or "").strip() and s.manifest_verified
            )
            if not stage:
                raise UserError(
                    "Wave %s ships from a LOADED staging record with its load / vehicle "
                    "reference and a scanned carton manifest (BRU-WMS-17)." % rec.name
                )
            loose = rec.line_ids.filtered(lambda ln: ln.state == "picked")
            if loose:
                raise UserError(
                    "Wave %s: %s x %s has no M15 transfer, return to vendor or job issue behind "
                    "it. Nothing leaves the warehouse without an M15 document: cancel the wave, "
                    "or raise the demand through the outbound demand queue (BRU-WMS-01)."
                    % (rec.name, loose[0].picked_qty, loose[0].part_id.part_number)
                )
            _warehouse, location = rec._wave_location()
            shipped = [
                {"part_id": line.part_id.id, "qty": line.picked_qty}
                for line in rec.line_ids.filtered(lambda ln: ln.state == "handed")
            ]
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
    company_id = fields.Many2one(
        related="wave_id.company_id", string="Company", store=True, index=True
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    bin_id = fields.Many2one("fix.warehouse.bin", string="Pick Bin", ondelete="set null")
    qty = fields.Float(string="Quantity")
    # F14: what the line first asked for. `qty` closes at what was picked when a
    # short is accepted, re-sourced or substituted; this one never moves, so pick
    # accuracy is measured against the request, not against itself.
    requested_qty = fields.Float(string="Requested", readonly=True, copy=False)
    ownership_class = fields.Selection(
        SLOT_CLASSES,
        string="Ownership Class",
        compute="_compute_ownership_class",
        store=True,
        help="F03: the class of the bin it picks from (an 'any' bin: owned).",
    )
    lot_id = fields.Many2one("fix.stock.lot", string="Picked Serial", readonly=True, copy=False)
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
            "lot_id",
            "requested_qty",
        }

    @api.depends("bin_id.ownership_class")
    def _compute_ownership_class(self):
        for line in self:
            line.ownership_class = bin_class(line.bin_id) if line.bin_id else "owned"

    @api.depends("wave_id.name", "part_id.part_number", "qty")
    def _compute_display_name(self):
        """A pick task names its wave line by this (A06 final pass A3)."""
        for line in self:
            line.display_name = "%s / %s x %s" % (
                line.wave_id.name or "-",
                line.part_id.part_number or "-",
                line.qty,
            )

    def action_scan_pick(self, bin_code=None, item_code=None, serial=None):
        """BRU-WMS-05: pick one line by scanning its bin and the item. The
        scans must name the line's bin (barcode or name) and its part
        (barcode, QR or part number); they are kept as the pick evidence. A
        serialized part also scans its serial (BRU-WMS-10), which then travels
        with the pick. A line whose task another operative holds is his."""
        Task = self.env["fix.wms.task"].sudo()
        for line in self:
            if line.state != "pending":
                raise UserError("Wave line %s is already %s." % (line.id, line.state))
            bin_code = _scan_bin(line.bin_id, bin_code)
            part = line.part_id
            item_code = _scan_item(part, item_code)
            wave = line.wave_id
            line._fix_check_pick_holder(Task)
            evidence = {"scanned_bin": bin_code, "scanned_item": item_code}
            if part.is_serialized:
                if not (serial or "").strip() or abs((line.qty or 0.0) - 1.0) > EPS:
                    raise UserError(
                        "%s is serialized: pick one unit per line and scan its serial "
                        "(BRU-WMS-10)." % part.part_number
                    )
                lot = self.env["fix.stock.lot"]._fix_find(part, serial.strip())
                if not lot:
                    raise UserError(
                        "Serial %s of %s was never received." % (serial, part.part_number)
                    )
                _warehouse, location = wave._wave_location()
                lot._fix_check_movable(part, location)
                evidence["lot_id"] = lot.id
            # the evidence first: the pick moves the serial it names
            line._guarded().write(evidence)
            wave._pick_lines(line)
        return True

    def _fix_check_pick_holder(self, Task=None):
        """The line's wave is released, and no other operative holds its pick
        task (BRU-WMS-14)."""
        self.ensure_one()
        Task = Task if Task is not None else self.env["fix.wms.task"].sudo()
        if self.wave_id.state not in ("released", "picking"):
            raise UserError("Wave %s is not released." % self.wave_id.name)
        if is_supervisor(self.env):
            return
        if self.bin_id:
            require_operative_profile(
                self.env, self.bin_id.zone_id.warehouse_id, self.bin_id.zone_id, "pick"
            )
        others = Task.search(
            [("wave_line_id", "=", self.id), ("state", "in", ("open", "assigned"))]
        ).filtered(lambda t: t.assignee_id and t.assignee_id.user_id != self.env.user)
        if others:
            raise UserError(
                "This pick is assigned to %s (BRU-WMS-14)." % others[0].assignee_id.name
            )

    def action_scan_short_pick(self, bin_code=None, item_code=None, found_qty=None, serial=None):
        """FR-WMS-024 / BRU-WMS-07: the bin holds less than the line asks for.
        The operative scans the bin, says how many are really there (and scans
        the item when there is any); that many are picked, the line is short,
        and the bin gets an immediate count-back. The ledger is never
        corrected here: the count-back goes to M15 for approval."""
        Task = self.env["fix.wms.task"].sudo()
        for line in self:
            if line.state != "pending":
                raise UserError("Wave line %s is already %s." % (line.id, line.state))
            try:
                found = float(found_qty)
            except (TypeError, ValueError):
                raise UserError("Give the quantity actually found in the bin.") from None
            if found < 0 or found + EPS >= (line.qty or 0.0):
                raise UserError(
                    "A short pick finds fewer than the %s the line asks for; %s is not short "
                    "(scan a normal pick instead)." % (line.qty, found)
                )
            if found > EPS:
                line.with_context(fix_found_qty={line.id: found}).action_scan_pick(
                    bin_code, item_code, serial
                )
                continue
            # nothing there: the bin is scanned, there is no item to scan
            scanned = _scan_bin(line.bin_id, bin_code)
            line._fix_check_pick_holder(Task)
            line._guarded().write({"scanned_bin": scanned})
            line.wave_id.with_context(fix_found_qty={line.id: 0.0})._pick_lines(line)
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
        lines = super().create(vals_list)
        for line in lines:
            line._guarded().write({"requested_qty": line.qty})
        return lines

    def write(self, vals):
        if self:
            self._refuse_unless_draft(self.mapped("wave_id"))
        res = super().write(vals)
        if "qty" in vals:
            # a draft line's request is whatever it asks for; a released one's is fixed
            for line in self.filtered(lambda ln: ln.wave_id.state == "draft"):
                line._guarded().write({"requested_qty": line.qty})
        return res

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
    # F23: a carton of cable by the metre holds 2.5; whole pieces are still checked
    contents_qty = fields.Float(string="Contents (qty)")
    state = fields.Selection(
        [("open", "Open"), ("sealed", "Sealed"), ("dispatched", "Dispatched")],
        required=True,
        default="open",
    )
    sealed_by_id = fields.Many2one("res.users", string="Sealed By", readonly=True)
    load_scanned = fields.Boolean(string="Scanned on Load", readonly=True, copy=False)

    _weight_positive = models.Constraint(
        "CHECK (weight_kg >= 0 AND contents_qty >= 0)",
        "Packing weights and counts cannot be negative",
    )

    _DOC = ("wave_id", "carton_size", "weight_kg", "contents_qty")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "sealed_by_id", "load_scanned"}

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
    manifest_scan = fields.Char(string="Scanned Manifest", readonly=True, copy=False)
    manifest_verified = fields.Boolean(string="Manifest Verified", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "loaded_by_id",
            "manifest_scan",
            "manifest_verified",
        }

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

    def action_load(self, carton_scans=None):
        """BRU-WMS-17: loading scans every carton of the wave (space-separated
        codes as the RF device sends them). The scan must be the wave's sealed
        cartons, all of them and nothing else. A stage loaded before the manifest
        existed runs this again to verify it."""
        for rec in self:
            if rec.state not in ("staging", "loaded") or rec.manifest_verified:
                raise UserError("Load a staging record")
            if not rec.wave_id or rec.wave_id.state != "staged":
                raise UserError("Only a staged wave is loaded (stage the packed wave first).")
            if not (rec.load_ref or "").strip():
                raise UserError("Record the load / vehicle reference before loading.")
            sealed = rec.wave_id.carton_ids.filtered(lambda c: c.state == "sealed")
            scanned = set(str(carton_scans or "").replace(",", " ").split())
            expected = set(sealed.mapped("name"))
            if scanned != expected:
                raise UserError(
                    "The scanned manifest does not match wave %s: missing %s; not on this "
                    "wave %s (BRU-WMS-17)."
                    % (
                        rec.wave_id.name,
                        ", ".join(sorted(expected - scanned)) or "none",
                        ", ".join(sorted(scanned - expected)) or "none",
                    )
                )
            sealed._guarded().write({"load_scanned": True})
            rec._guarded().write(
                {
                    "state": "loaded",
                    "loaded_by_id": self.env.user.id,
                    "manifest_scan": " ".join(sorted(scanned)),
                    "manifest_verified": True,
                }
            )
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
        elif len(self) == 1 and self.assignee_id and not self.env.user.has_group(SUPERVISOR_GROUP):
            locked |= {"assignee_id"}
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
            _refuse_reassign(self, vals)
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
        RF device sends it (then the serial, for a serialized part), or give
        bin_scan / item_scan."""
        serial = None
        if scan and not (bin_scan or item_scan):
            parts = str(scan).replace("|", " ").replace(",", " ").split()
            bin_scan = parts[0] if parts else None
            item_scan = parts[1] if len(parts) > 1 else None
            serial = parts[2] if len(parts) > 2 else None
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
                    line.action_scan_pick(bin_scan, item_scan, serial)
            elif rec.task_type == "putaway":
                if not rec.putaway_id:
                    raise UserError("A put-away task completes its put-away: link it.")
                if rec.putaway_id.state == "pending":
                    rec.putaway_id.action_complete(bin_scan, item_scan)
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
        """F30: cancelling work is a supervisor's decision (BRU-WMS-14)."""
        require_supervisor(self.env, "cancel a warehouse task")
        for rec in self:
            if rec.state in ("done", "cancelled"):
                raise UserError("Task %s is already closed." % rec.name)
            rec._guarded().write({"state": "cancelled"})
        return True


class FixWmsFloorCount(models.Model):
    """A blind bin-level floor count. The expected quantity is the slot's at
    the moment the count is entered (F08: never a stale figure from when the
    count was raised), it is never typed and the counter never sees it (F13).
    Any variance (O4: tolerance 0 by default) is recounted, then submitted as
    an M15 count for approval by another person; the slot is frozen meanwhile
    and moves when that count posts (BRU-WMS-16)."""

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
    # F13: blind. Only a supervisor (or controller) reads the expectation.
    expected_qty = fields.Float(string="Expected", readonly=True, groups=SUPERVISOR_GROUP)
    counted_qty = fields.Float(string="Counted")
    variance = fields.Float(
        compute="_compute_variance", store=True, string="Variance", groups=SUPERVISOR_GROUP
    )
    slot_only_qty = fields.Float(
        string="Found Unslotted",
        readonly=True,
        copy=False,
        groups=SUPERVISOR_GROUP,
        help="F07: part of a gain that is stock M15 already holds outside the bins: it is "
        "slotted, never added to the ledger a second time.",
    )
    expected_taken_at = fields.Datetime(string="Expectation Taken", readonly=True, copy=False)
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
            "slot_only_qty",
            "expected_taken_at",
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

    @api.depends("expected_qty", "counted_qty", "expected_taken_at")
    def _compute_variance(self):
        for rec in self:
            if not rec.expected_taken_at:
                rec.variance = 0.0
                continue
            rec.variance = round((rec.counted_qty or 0.0) - (rec.expected_qty or 0.0), 3)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.wms.floor.count") or "FLCT/New"
                )
            # the slot's, taken when the count is entered: never typed
            vals.pop("expected_qty", None)
            vals.pop("slot_only_qty", None)
        return super().create(vals_list)

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

    @api.model
    def _fix_raise_count(self, part, bin_record, count_type, ref):
        """F12: a count-back or zero-crossing is a real blind floor count with
        its task, so the task can be completed and the bin is settled."""
        company = bin_record.sudo().zone_id.warehouse_id.company_id or self.env.company
        count = (
            self.sudo()
            ._guarded()
            .create(
                {
                    "company_id": company.id,
                    "bin_id": bin_record.id,
                    "part_id": part.id,
                    "count_type": count_type,
                }
            )
        )
        self.env["fix.wms.task"].sudo().create(
            {
                "company_id": company.id,
                "task_type": "count",
                "ref": ref,
                "part_id": part.id,
                "bin_id": bin_record.id,
                "qty": 0.0,
                "floor_count_id": count.id,
            }
        )
        return count.with_env(self.env)

    def _within_tolerance(self):
        self.ensure_one()
        rec = self.sudo()
        pct = inv_param(self.env, PARAM_WMS_COUNT_TOLERANCE_PCT, 0.0)
        return (
            abs(rec.variance) <= EPS
            or abs(rec.variance) <= abs(rec.expected_qty) * pct / 100.0 + EPS
        )

    def _fix_take_expected(self):
        """F08: the expectation is the slot as it stands when the count is
        entered; the slot is frozen from then until the count settles."""
        Slot = self.env["fix.wms.slot"]
        for rec in self:
            slot = Slot._slot_for(rec.part_id, rec.bin_id).sudo()
            # the counter writes nothing he may not read: the system takes it (F13)
            rec.sudo()._guarded().write(
                {
                    "expected_qty": slot.qty if slot else 0.0,
                    "expected_taken_at": fields.Datetime.now(),
                }
            )

    def action_post(self):
        for rec in self:
            if rec.state not in ("draft", "recount"):
                raise UserError("Post a draft floor count")
            check_quantity(rec.part_id, rec.counted_qty, "counted quantity", allow_zero=True)
            if rec.state == "draft":
                rec._guarded().write({"counted_by_id": self.env.user.id})
                rec._fix_take_expected()
            variance = rec.sudo().variance
            if abs(variance) <= EPS:
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
        """Hand the bin variance to M15 as a count of the warehouse location, in
        the slot's ownership class: counted = the class's on-hand + the part of
        the variance M15 does not already hold (F07: a gain that is stock M15
        holds outside the bins is slotted, not booked twice). Created in the
        counter's name so he can never approve it."""
        self.ensure_one()
        rec = self.sudo()
        location = _bin_location(self.bin_id)
        slot_cls = bin_class(self.bin_id)
        cls = location_class(location, slot_cls)
        Count = self.env["fix.stock.count"].sudo()
        bucket = self.env["fix.stock.onhand"]._bucket(self.part_id, location, cls)
        on_hand = bucket.qty if bucket else 0.0
        variance = rec.variance
        absorbed = 0.0
        if variance > EPS:
            free = unslotted_qty(self.env, self.part_id, location, slot_cls)
            absorbed = max(min(variance, free), 0.0)
        ledger_delta = round(variance - absorbed, 4)
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
                    (
                        0,
                        0,
                        {
                            "part_id": self.part_id.id,
                            "ownership_class": cls,
                            "counted_qty": on_hand + ledger_delta,
                        },
                    )
                ],
            }
        )
        count.line_ids._guarded().write({"floor_count_id": self.id})
        self.sudo()._guarded().write({"slot_only_qty": absorbed})
        if self._within_tolerance():
            count.with_user(self.env.user).sudo().action_submit()
        else:
            # the floor recount already happened: straight to approval
            count.line_ids._guarded().write({"recount_qty": on_hand + ledger_delta})
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
        publish(
            self.env,
            "wh.count_submitted",
            "fix.wms.floor.count",
            self.id,
            {
                "count": self.name,
                "bin_id": self.bin_id.id,
                "part_id": self.part_id.id,
                "counted": self.counted_qty,
                "m15_count": count.name,
            },
        )

    def _fix_apply_posted_variance(self, delta):
        """Called when the M15 count posts: the slot follows the ledger. F08:
        recomputed at approval: the slot never rises above what the ledger now
        holds outside the bins."""
        Slot = self.env["fix.wms.slot"]
        for rec in self:
            move = round(delta + (rec.sudo().slot_only_qty or 0.0), 4)
            slot = Slot._slot_for(rec.part_id, rec.bin_id, create=move > 0)
            if slot and move > EPS:
                location = _bin_location(rec.bin_id)
                free = unslotted_qty(self.env, rec.part_id, location, slot.ownership_class)
                move = max(min(move, free), 0.0)
            if slot:
                slot._guarded().write({"qty": round(max((slot.qty or 0.0) + move, 0.0), 4)})
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
    # F16: a template and a station are their company's (record rules)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    zone_id = fields.Many2one("fix.warehouse.zone", string="Zone")
    cutoff = fields.Char(string="Cut-off (HH:MM)", default="16:00")
    active = fields.Boolean(default=True)


class FixWmsPackingStation(models.Model):
    _name = "fix.wms.packing.station"
    _description = "Packing Station"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    warehouse_id = fields.Many2one("fix.warehouse", string="Warehouse", ondelete="restrict")
    lane = fields.Char(string="Lane")
    printer = fields.Char(string="Label Printer")
    active = fields.Boolean(default=True)
