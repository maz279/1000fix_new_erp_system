# fix_wms_ops_floor — M41 floor records the capture audit found missing
# (2026-11-14). The file name sorts after fix_wms_ops on purpose: ruff I001
# keeps models/__init__.py alphabetical, and these classes extend the models
# fix_wms_ops defines.
#
# Before this file, four of M41's nine sub-module pages captured nothing:
#   * Replenishment (FR-WMS-028/029/030): a "replenish" task completed without
#     moving anything, and no bin-to-bin move existed at all. fix.wms.move is
#     that move: it shifts a bin slot inside the SAME M15 location, so the
#     ledger total never changes (BRU-WMS-01), under the put-away rules
#     (blocked bin, hazard class, ownership class, capacity: BRU-WMS-03/09/11/12).
#     A pick-face slot names its minimum; falling below it raises the move
#     from a bulk slot (AUT-WMS-11).
#   * RF Execution (FR-WMS-036/038, T-04, T-15): an operative could not claim a
#     task in one step, and no RF handheld was enrolled anywhere. action_claim
#     locks the row (two devices never claim one task) and fix.wms.device is
#     the enrolment register (deactivating a lost device).
#   * Labour & Analytics (FR-WMS-039/040, BRU-WMS-18): no operative profile and
#     no handling equipment existed, so "equipment the operative does not hold"
#     could not even be stated. fix.wms.operative and fix.wms.equipment hold it;
#     a task that needs equipment is assigned only to an operative holding it.
#   * Picking: the Scan Pick / Short Pick forms take their scans through the
#     input fields below (never stored: the workflow method keeps the evidence).
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2.errors import LockNotAvailable

from .fix_inventory_approval import check_quantity, is_supervisor, is_whole_unit
from .fix_wms_ops import EPS, _differs, _scan_bin, _scan_item

MOVE_TYPES = [
    ("replenish", "Pick-Face Replenishment"),
    ("move", "Ad-hoc Bin Move"),
    ("consolidate", "Consolidation"),
    ("reslot", "Re-Slotting"),
]
MOVE_REASONS = [
    ("replenish", "Pick face below its minimum"),
    ("wrong_bin", "Stock found in the wrong bin"),
    ("damage", "Bin or rack damaged"),
    ("consolidate", "Part split across bins"),
    ("reslot", "Velocity changed (re-slot)"),
    ("other", "Other"),
]
EQUIPMENT_TYPES = [
    ("trolley", "Picking Trolley"),
    ("ladder", "Ladder / Step"),
    ("pallet_truck", "Pallet Truck"),
    ("forklift", "Forklift / Reach Truck"),
    ("cage_key", "Secure Cage Key"),
]
SHIFTS = [
    ("morning", "Morning (06-14)"),
    ("afternoon", "Afternoon (14-22)"),
    ("night", "Night (22-06)"),
]


def _warehouse_of(bin_record):
    return bin_record.zone_id.warehouse_id


def _require_floor_admin(env, what):
    """Profiles, equipment and devices: a Warehouse Supervisor (or an Inventory
    Controller, who holds the grant) or the IT administrator (R33)."""
    if env.su or is_supervisor(env) or env.user.has_group("base.group_system"):
        return
    raise AccessError("Only a Warehouse Supervisor or the IT administrator may %s." % what)


# ============================================================ internal move
class FixWmsMove(models.Model):
    _name = "fix.wms.move"
    _description = "Internal Move / Replenishment"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    move_type = fields.Selection(MOVE_TYPES, string="Move Type", required=True, default="move")
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict", index=True
    )
    from_bin_id = fields.Many2one(
        "fix.warehouse.bin", string="From Bin", required=True, ondelete="restrict"
    )
    to_bin_id = fields.Many2one(
        "fix.warehouse.bin", string="To Bin", required=True, ondelete="restrict"
    )
    qty = fields.Float(string="Quantity", required=True)
    reason_code = fields.Selection(MOVE_REASONS, string="Reason", required=True)
    note = fields.Char(string="Note")
    assignee_id = fields.Many2one("hr.employee", string="Assigned To")
    trigger_qty = fields.Float(string="Pick Face Held (when raised)", readonly=True, copy=False)
    task_id = fields.Many2one("fix.wms.task", string="Task", readonly=True, copy=False)
    state = fields.Selection(
        [("open", "Open"), ("done", "Done"), ("cancelled", "Cancelled")],
        required=True,
        default="open",
    )
    done_at = fields.Datetime(string="Moved On", readonly=True, copy=False)
    done_by_id = fields.Many2one("res.users", string="Moved By", readonly=True, copy=False)
    scanned_from = fields.Char(string="Scanned From Bin", readonly=True, copy=False)
    scanned_to = fields.Char(string="Scanned To Bin", readonly=True, copy=False)
    scanned_item = fields.Char(string="Scanned Item", readonly=True, copy=False)
    # the Confirm Move form's scans (inputs only: the move keeps the evidence)
    scan_from_entry = fields.Char(string="Scan the From Bin", compute="_compute_entries")
    scan_to_entry = fields.Char(string="Scan the To Bin", compute="_compute_entries")
    scan_item_entry = fields.Char(string="Scan the Item", compute="_compute_entries")

    _qty_positive = models.Constraint("CHECK (qty > 0)", "A move moves a positive quantity")

    def _compute_entries(self):
        for rec in self:
            rec.scan_from_entry = False
            rec.scan_to_entry = False
            rec.scan_item_entry = False

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "done_at",
            "done_by_id",
            "scanned_from",
            "scanned_to",
            "scanned_item",
            "trigger_qty",
            "task_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "open":
            locked |= {
                "move_type",
                "part_id",
                "from_bin_id",
                "to_bin_id",
                "qty",
                "reason_code",
                "note",
                "assignee_id",
            }
        return locked

    @api.constrains("from_bin_id", "to_bin_id")
    def _check_bins(self):
        for rec in self:
            if rec.from_bin_id == rec.to_bin_id:
                raise ValidationError("A move goes to another bin.")
            if _warehouse_of(rec.from_bin_id) != _warehouse_of(rec.to_bin_id):
                raise ValidationError(
                    "Bins %s and %s are in different warehouses: that is a stock transfer "
                    "(M15), not a bin move." % (rec.from_bin_id.name, rec.to_bin_id.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.wms.move") or "MOVE/New"
                )
        records = super().create(vals_list)
        Task = self.env["fix.wms.task"].sudo()
        for rec in records:
            check_quantity(rec.part_id, rec.qty, "move quantity")
            # FR-WMS-035: every physical action is a task in the queue
            task = Task.create(
                {
                    "company_id": rec.company_id.id,
                    "task_type": "replenish" if rec.move_type == "replenish" else "move",
                    "ref": rec.name,
                    "part_id": rec.part_id.id,
                    "bin_id": rec.from_bin_id.id,
                    "qty": rec.qty,
                    "assignee_id": rec.assignee_id.id or False,
                    "move_id": rec.id,
                }
            )
            rec._guarded().write({"task_id": task.id})
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {
                k: vals[k]
                for k in ("move_type", "part_id", "from_bin_id", "to_bin_id", "qty", "reason_code")
                if k in vals
            }
            if frozen and _differs(self.filtered(lambda m: m.state != "open"), frozen):
                raise UserError("A completed or cancelled move is final.")
        return super().write(vals)

    def action_confirm(self, from_code=None, to_code=None, item_code=None):
        """BRU-WMS-05: confirmed by scanning the bin it leaves, the bin it goes
        to and the item. The slot quantity moves between two bins of one M15
        location, so the ledger total is unchanged (BRU-WMS-01)."""
        Slot = self.env["fix.wms.slot"]
        for rec in self:
            if rec.state != "open":
                raise UserError("Move %s is already %s." % (rec.name, rec.state))
            if (
                not self.env.su
                and rec.assignee_id.user_id
                and rec.assignee_id.user_id != self.env.user
                and not is_supervisor(self.env)
            ):
                raise UserError(
                    "Move %s is assigned to %s (BRU-WMS-14)." % (rec.name, rec.assignee_id.name)
                )
            evidence = {}
            if not self.env.su:
                evidence = {
                    "scanned_from": _scan_bin(rec.from_bin_id, from_code),
                    "scanned_to": _scan_bin(rec.to_bin_id, to_code),
                    "scanned_item": _scan_item(rec.part_id, item_code),
                }
            check_quantity(rec.part_id, rec.qty, "move quantity")
            source = Slot._slot_for(rec.part_id, rec.from_bin_id)
            if not source:
                raise UserError(
                    "Bin %s holds no %s." % (rec.from_bin_id.name, rec.part_id.part_number)
                )
            source._check_pickable()
            free = round((source.qty or 0.0) - (source.reserved_qty or 0.0), 4)
            if rec.qty > free + EPS:
                raise UserError(
                    "Bin %s has %s of %s free (the rest is allocated to waves); %s cannot move."
                    % (rec.from_bin_id.name, free, rec.part_id.part_number, rec.qty)
                )
            target = rec.to_bin_id
            if target._fix_is_blocked():
                raise UserError(
                    "Bin %s is blocked (%s): nothing is put into it (BRU-WMS-12)."
                    % (target.name, target.sudo().block_reason or "no reason")
                )
            if not target.zone_id.reservable:
                raise UserError(
                    "Bin %s is in the %s zone: stock goes there through an M15 quarantine "
                    "or inspection record, not a bin move."
                    % (target.name, target.zone_id.zone_type)
                )
            if (rec.part_id.storage_class or "general") == "hazardous" and (
                target.storage_class != "hazardous"
            ):
                raise UserError(
                    "%s is hazardous: it goes only into a hazardous-class bin, not %s "
                    "(BRU-WMS-11)." % (rec.part_id.part_number, target.name)
                )
            src_class = rec.from_bin_id.ownership_class or "any"
            dst_class = target.ownership_class or "any"
            if dst_class != "any" and src_class != dst_class:
                raise UserError(
                    "Bin %s holds %s stock only; bin %s is %s, so its stock's class is not "
                    "proven (BRU-WMS-03)."
                    % (
                        target.name,
                        dst_class,
                        rec.from_bin_id.name,
                        "unrestricted" if src_class == "any" else src_class,
                    )
                )
            dest = Slot._slot_for(rec.part_id, target, create=True)
            source._guarded().write({"qty": round((source.qty or 0.0) - rec.qty, 4)})
            # the capacity constraint on the slot refuses an over-full bin (BRU-WMS-09)
            dest._guarded().write(
                {
                    "qty": round((dest.qty or 0.0) + rec.qty, 4),
                    "last_slotted_on": fields.Date.context_today(self),
                }
            )
            now = fields.Datetime.now()
            rec._guarded().write(
                {"state": "done", "done_at": now, "done_by_id": self.env.user.id, **evidence}
            )
            rec.task_id.sudo().filtered(lambda t: t.state in ("open", "assigned"))._guarded().write(
                {"state": "done", "done_at": now, "done_by_id": self.env.user.id}
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Move %s is already %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "cancelled"})
            rec.task_id.sudo().filtered(lambda t: t.state in ("open", "assigned"))._guarded().write(
                {"state": "cancelled"}
            )
        return True


# ============================================================ slot minimums
class FixWmsSlotReplenish(models.Model):
    _inherit = "fix.wms.slot"

    min_qty = fields.Float(
        string="Replenish When Below",
        help="Pick-face minimum: below it a replenishment move is raised from a bulk slot.",
    )
    max_qty = fields.Float(string="Replenish Up To", help="Empty: up to the minimum.")

    @api.constrains("min_qty", "max_qty")
    def _check_replenish_levels(self):
        for slot in self:
            if slot.min_qty < 0 or slot.max_qty < 0:
                raise ValidationError("Replenishment levels cannot be negative.")
            if slot.max_qty and slot.max_qty + EPS < slot.min_qty:
                raise ValidationError("Replenish up to at least the minimum.")

    def _fix_replenish_source(self):
        """The bulk or reserve slot of the same part, in the same warehouse and
        of a compatible ownership class, with the most free stock."""
        self.ensure_one()
        warehouse = _warehouse_of(self.bin_id)
        dst_class = self.bin_id.ownership_class or "any"
        best, best_free = self.browse(), 0.0
        candidates = self.sudo().search(
            [
                ("part_id", "=", self.part_id.id),
                ("id", "!=", self.id),
                ("slot_type", "in", ("bulk", "reserve")),
                ("state", "=", "active"),
                ("bin_id.zone_id.warehouse_id", "=", warehouse.id),
            ]
        )
        for slot in candidates:
            if slot.bin_id._fix_is_blocked() or not slot.bin_id.zone_id.reservable:
                continue
            src_class = slot.bin_id.ownership_class or "any"
            if dst_class != "any" and src_class != dst_class:
                continue
            free = (slot.qty or 0.0) - (slot.reserved_qty or 0.0)
            if free > best_free + EPS:
                best, best_free = slot, free
        return best.with_env(self.env), best_free

    def _fix_raise_replenishment(self, quiet=False):
        Move = self.env["fix.wms.move"]
        made = Move.browse()
        for slot in self:
            problem = None
            if slot.slot_type != "pick":
                problem = "Only a pick-face slot is replenished (bin %s is %s)." % (
                    slot.bin_id.name,
                    slot.slot_type,
                )
            elif not slot.min_qty:
                problem = "Set the pick-face minimum of %s in bin %s first." % (
                    slot.part_id.part_number,
                    slot.bin_id.name,
                )
            elif (slot.qty or 0.0) + EPS >= slot.min_qty:
                problem = "Bin %s holds %s, not below its minimum %s." % (
                    slot.bin_id.name,
                    slot.qty,
                    slot.min_qty,
                )
            elif Move.sudo().search_count(
                [
                    ("to_bin_id", "=", slot.bin_id.id),
                    ("part_id", "=", slot.part_id.id),
                    ("move_type", "=", "replenish"),
                    ("state", "=", "open"),
                ]
            ):
                problem = "A replenishment of bin %s is already open." % slot.bin_id.name
            source, free = (None, 0.0) if problem else slot._fix_replenish_source()
            if not problem and not source:
                problem = "No bulk or reserve bin of this warehouse holds free %s." % (
                    slot.part_id.part_number
                )
            if problem:
                if quiet:
                    continue
                raise UserError(problem)
            qty = min((slot.max_qty or slot.min_qty) - (slot.qty or 0.0), free)
            if is_whole_unit(slot.part_id):
                qty = float(int(qty + EPS))
            if qty <= EPS:
                if quiet:
                    continue
                raise UserError(
                    "Less than one piece of %s is free to replenish from."
                    % (slot.part_id.part_number)
                )
            made |= Move.create(
                {
                    "company_id": slot.company_id.id or self.env.company.id,
                    "move_type": "replenish",
                    "reason_code": "replenish",
                    "part_id": slot.part_id.id,
                    "from_bin_id": source.bin_id.id,
                    "to_bin_id": slot.bin_id.id,
                    "qty": round(qty, 4),
                }
            )
            made[-1:]._guarded().write({"trigger_qty": slot.qty})
        return made

    def action_raise_replenishment(self):
        """FR-WMS-028: raise the bulk-to-pick-face move for a pick face below
        its minimum (AUT-WMS-11 does the same after every pick)."""
        self._fix_raise_replenishment()
        return True


class FixWmsWaveReplenish(models.Model):
    _inherit = "fix.wms.wave"

    def _pick_lines(self, lines):
        res = super()._pick_lines(lines)
        # AUT-WMS-11: a pick face the pick took below its minimum is replenished
        Slot = self.env["fix.wms.slot"].sudo()
        for line in lines:
            slot = Slot._slot_for(line.part_id, line.bin_id)
            if slot and slot.slot_type == "pick" and slot.min_qty and slot.qty + EPS < slot.min_qty:
                slot._fix_raise_replenishment(quiet=True)
        return res


# ============================================================ pick inputs
class FixWmsWaveLineScan(models.Model):
    _inherit = "fix.wms.wave.line"

    scan_bin_entry = fields.Char(string="Scan the Bin", compute="_compute_scan_entries")
    scan_item_entry = fields.Char(string="Scan the Item", compute="_compute_scan_entries")
    scan_serial_entry = fields.Char(
        string="Scan the Serial (serialized parts)", compute="_compute_scan_entries"
    )
    found_qty_entry = fields.Float(
        string="Quantity Actually in the Bin", compute="_compute_scan_entries"
    )

    def _compute_scan_entries(self):
        for line in self:
            line.scan_bin_entry = False
            line.scan_item_entry = False
            line.scan_serial_entry = False
            line.found_qty_entry = 0.0


# ============================================================ tasks
class FixWmsTaskFloor(models.Model):
    _inherit = "fix.wms.task"

    task_type = fields.Selection(
        selection_add=[("move", "Internal Move")], ondelete={"move": "set default"}
    )
    move_id = fields.Many2one("fix.wms.move", string="Internal Move", readonly=True, copy=False)
    equipment_required = fields.Selection(EQUIPMENT_TYPES, string="Equipment Needed")
    scan_entry = fields.Char(
        string="Scan (bin, then item, then serial; a move: from bin, to bin, item)",
        compute="_compute_scan_entry",
    )

    def _compute_scan_entry(self):
        for rec in self:
            rec.scan_entry = False

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"move_id"}

    def _fix_check_equipment(self, employee):
        """BRU-WMS-18: a task that needs equipment goes only to an operative
        whose profile at this warehouse holds that equipment."""
        Operative = self.env["fix.wms.operative"].sudo()
        for rec in self:
            if not rec.equipment_required or not employee:
                continue
            warehouse = _warehouse_of(rec.bin_id) if rec.bin_id else None
            domain = [("employee_id", "=", employee.id), ("active", "=", True)]
            if warehouse:
                domain.append(("warehouse_id", "=", warehouse.id))
            needed = rec.equipment_required
            held = (
                Operative.search(domain)
                .mapped("equipment_ids")
                .filtered(lambda e, needed=needed: e.active and e.equipment_type == needed)
            )
            if not held:
                label = dict(EQUIPMENT_TYPES)[rec.equipment_required]
                raise UserError(
                    "Task %s needs a %s, which %s does not hold (BRU-WMS-18)."
                    % (rec.name, label, employee.name)
                )

    def action_assign(self):
        for rec in self:
            rec._fix_check_equipment(rec.assignee_id)
        return super().action_assign()

    def action_claim(self):
        """FR-WMS-036 pull option / T-04: the operative takes a free task. The
        row is locked first, so two devices can never claim the same task."""
        employee = (
            self.env["hr.employee"]
            .sudo()
            .search(
                [("user_id", "=", self.env.user.id), ("company_id", "in", self.env.companies.ids)],
                limit=1,
            )
        )
        if not employee:
            raise UserError("You have no employee record: a task is claimed by an operative.")
        for rec in self:
            try:
                with self.env.cr.savepoint():
                    self.env.cr.execute(
                        "SELECT id FROM fix_wms_task WHERE id = %s FOR UPDATE NOWAIT", (rec.id,)
                    )
            except LockNotAvailable:
                raise UserError("Task %s is being claimed on another device." % rec.name) from None
            rec.invalidate_recordset(["state", "assignee_id"])
            if rec.state != "open":
                raise UserError(
                    "Task %s is %s: only an open task is claimed." % (rec.name, rec.state)
                )
            if rec.assignee_id and rec.assignee_id != employee:
                raise UserError(
                    "Task %s is already %s's (BRU-WMS-14)." % (rec.name, rec.assignee_id.name)
                )
            rec._fix_check_equipment(employee)
            rec.write({"assignee_id": employee.id})
            rec._guarded().write({"state": "assigned"})
        return True

    def action_done(self, scan=None, bin_scan=None, item_scan=None):
        moves = self.filtered(lambda t: t.move_id and t.move_id.state == "open")
        rest = self - moves
        for rec in moves:
            if rec.state != "assigned":
                raise UserError(
                    "Complete an assigned task (task %s is %s)." % (rec.name, rec.state)
                )
            if not self.env.su and rec.assignee_id.user_id != self.env.user:
                raise UserError(
                    "Task %s is assigned to %s: only that operative completes it."
                    % (rec.name, rec.assignee_id.name)
                )
            parts = str(scan or "").replace("|", " ").replace(",", " ").split()
            from_code = parts[0] if parts else bin_scan
            to_code = parts[1] if len(parts) > 1 else None
            item_code = parts[2] if len(parts) > 2 else item_scan
            # the move closes its task
            rec.move_id.action_confirm(from_code, to_code, item_code)
        if rest:
            return super(FixWmsTaskFloor, rest).action_done(scan, bin_scan, item_scan)
        return True


# ============================================================ labour
class FixWmsEquipment(models.Model):
    _name = "fix.wms.equipment"
    _description = "Material-Handling Equipment"
    _order = "warehouse_id, code"

    warehouse_id = fields.Many2one(
        "fix.warehouse", string="Warehouse", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(
        related="warehouse_id.company_id", string="Company", store=True, index=True
    )
    code = fields.Char(string="Equipment Code", required=True)
    name = fields.Char(string="Description", required=True)
    equipment_type = fields.Selection(EQUIPMENT_TYPES, string="Type", required=True)
    capacity_kg = fields.Float(string="Safe Working Load (kg)")
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "UNIQUE (warehouse_id, code)", "Equipment code must be unique in the warehouse"
    )

    @api.model_create_multi
    def create(self, vals_list):
        _require_floor_admin(self.env, "register handling equipment")
        return super().create(vals_list)

    def write(self, vals):
        _require_floor_admin(self.env, "change handling equipment")
        return super().write(vals)

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s · %s" % (rec.code or "-", rec.name or "")


class FixWmsOperative(models.Model):
    _name = "fix.wms.operative"
    _description = "Warehouse Operative Profile"
    _order = "warehouse_id, employee_id"
    _rec_name = "employee_id"

    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, ondelete="restrict", index=True
    )
    warehouse_id = fields.Many2one(
        "fix.warehouse", string="Warehouse", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(
        related="warehouse_id.company_id", string="Company", store=True, index=True
    )
    zone_ids = fields.Many2many("fix.warehouse.zone", string="Zones Worked")
    equipment_ids = fields.Many2many("fix.wms.equipment", string="Equipment Held / Certified On")
    shift = fields.Selection(SHIFTS, string="Shift", required=True, default="morning")
    active = fields.Boolean(default=True)

    _employee_unique = models.Constraint(
        "UNIQUE (employee_id, warehouse_id)", "One operative profile per employee and warehouse"
    )

    @api.constrains("warehouse_id", "zone_ids", "equipment_ids")
    def _check_same_warehouse(self):
        for rec in self:
            wh = rec.warehouse_id
            stray_zones = rec.zone_ids.filtered(lambda z, wh=wh: z.warehouse_id != wh)
            stray_kit = rec.equipment_ids.filtered(lambda e, wh=wh: e.warehouse_id != wh)
            if stray_zones or stray_kit:
                raise ValidationError(
                    "%s: zones and equipment must belong to warehouse %s."
                    % (rec.employee_id.name, rec.warehouse_id.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        _require_floor_admin(self.env, "create an operative profile")
        return super().create(vals_list)

    def write(self, vals):
        _require_floor_admin(self.env, "change an operative profile")
        return super().write(vals)


# ============================================================ RF devices
class FixWmsDevice(models.Model):
    _name = "fix.wms.device"
    _description = "RF Handheld Device"
    _order = "warehouse_id, device_code"
    _rec_name = "device_code"
    _inherit = ["fix.guarded.mixin"]

    warehouse_id = fields.Many2one(
        "fix.warehouse", string="Warehouse", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(
        related="warehouse_id.company_id", string="Company", store=True, index=True
    )
    device_code = fields.Char(string="Device Code", required=True)
    model_name = fields.Char(string="Make / Model")
    operative_id = fields.Many2one("hr.employee", string="Issued To")
    app_version = fields.Char(string="App Version")
    enrolled_at = fields.Datetime(
        string="Enrolled On", readonly=True, default=fields.Datetime.now, copy=False
    )
    enrolled_by_id = fields.Many2one(
        "res.users", string="Enrolled By", readonly=True, default=lambda self: self.env.user
    )
    last_seen_at = fields.Datetime(string="Last Seen", readonly=True, copy=False)
    state = fields.Selection(
        [("active", "Active"), ("deactivated", "Deactivated")],
        required=True,
        default="active",
    )
    deactivation_reason = fields.Char(string="Deactivation Reason", readonly=True, copy=False)
    deactivated_by_id = fields.Many2one(
        "res.users", string="Deactivated By", readonly=True, copy=False
    )

    _code_unique = models.Constraint("UNIQUE (device_code)", "A device is enrolled once")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "enrolled_at",
            "enrolled_by_id",
            "last_seen_at",
            "deactivation_reason",
            "deactivated_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= {"device_code", "warehouse_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        _require_floor_admin(self.env, "enrol an RF device")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            _require_floor_admin(self.env, "change an RF device")
            frozen = {k: vals[k] for k in ("device_code", "warehouse_id") if k in vals}
            if frozen and _differs(self, frozen):
                raise UserError("Enrol a replacement device instead of re-coding this one.")
        return super().write(vals)

    def action_deactivate(self, reason=None):
        """T-15: a lost or retired handheld is cut off at once."""
        _require_floor_admin(self.env, "deactivate an RF device")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Give the reason the device is deactivated (lost, damaged, retired).")
        for rec in self:
            if rec.state != "active":
                raise UserError("Device %s is already deactivated." % rec.device_code)
            rec._guarded().write(
                {
                    "state": "deactivated",
                    "deactivation_reason": reason,
                    "deactivated_by_id": self.env.user.id,
                }
            )
        return True

    def action_reactivate(self):
        _require_floor_admin(self.env, "reactivate an RF device")
        for rec in self:
            if rec.state != "deactivated":
                raise UserError("Device %s is active." % rec.device_code)
            if rec.deactivated_by_id == self.env.user and not self.env.su:
                raise UserError(
                    "Device %s: another administrator reactivates a device you deactivated."
                    % rec.device_code
                )
            rec._guarded().write(
                {"state": "active", "deactivation_reason": False, "deactivated_by_id": False}
            )
        return True
