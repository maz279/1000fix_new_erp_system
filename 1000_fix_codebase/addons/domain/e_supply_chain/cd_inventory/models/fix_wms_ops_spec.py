# fix_wms_ops_spec — M41 capture pass 2 (2026-11-19). The file name sorts after
# fix_wms_ops_floor on purpose: these classes extend models both files define.
#
# Pass 1 (14 Nov) gave every M41 page a "+ New". Read against FR-WMS-001..041
# and the §10.1 entities, the forms behind those buttons still could not hold
# the records the spec names:
#   * Physical Structure: no warehouse enablement, no zone types beyond six,
#     no bin coordinate, pick face, weight or volume (cd_wms_structure), and a
#     bin block left no history once lifted (FR-WMS-034).
#   * Inbound & Put-Away: the "directed" put-away was a bin the user typed; no
#     strategy, no rejected bins, no override reason or approval (FR-WMS-013,
#     014, T-01, BRU-WMS-06); no put-away exception (FR-WMS-015); no dock door
#     master (FR-WMS-008); no handling unit (FR-WMS-010, T-11); no cross-dock
#     (FR-WMS-016, BRU-WMS-15); no return receiving (FR-WMS-017).
#   * Wave Planning: no outbound demand queue (FR-WMS-018), templates without
#     purpose, release rule or destination (FR-WMS-019), no cluster or
#     pick-and-pass strategy (FR-WMS-021), no pick path (FR-WMS-022).
#   * Picking: a short pick never re-sourced from another bin (FR-WMS-024).
#   * Labour & Analytics: counts only one bin at a time, never by zone or
#     velocity class (FR-WMS-031); no time standard and no productivity record
#     (FR-WMS-040, §10.1 fix.wh.productivity).
# M41 still never authors a stock quantity (BRU-WMS-01): every ledger effect
# below goes through fix.stock.onhand, as the existing floor records do.
import json
from collections import defaultdict
from datetime import datetime, time, timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_inventory_approval import (
    check_quantity,
    is_supervisor,
    is_whole_unit,
    location_class,
    require_supervisor,
)
from .fix_wms_ops import EPS, _differs, _scan_item
from .fix_wms_ops_floor import _require_floor_admin, _warehouse_of

NO_PUTAWAY_ZONES = ("inspection", "quarantine", "returns", "staging", "dispatch", "receiving")
STRATEGIES = [
    ("fixed", "Fixed bin (the part's pick face)"),
    ("existing", "Addition to existing stock"),
    ("near_pick", "Near the pick face"),
    ("empty", "Nearest empty bin"),
    ("bulk", "Bulk zone"),
    ("manual", "No eligible bin: chosen by hand"),
]
OVERRIDE_REASONS = [
    ("bin_full", "Directed bin physically full"),
    ("closer", "Closer to the pick face"),
    ("consolidate", "Consolidate with stock already in the bin"),
    ("rack_damage", "Rack or bin damaged"),
    ("other", "Other (see note)"),
]
EXCEPTION_CAUSES = [
    ("full_bin", "Directed bin is full"),
    ("blocked_bin", "Directed bin is blocked / not accessible"),
    ("damaged_item", "Item damaged"),
]
PRIORITIES = [("normal", "Normal"), ("urgent", "Urgent"), ("emergency", "Emergency (job down)")]
DEMAND_SOURCES = [
    ("transfer", "Branch transfer (M15)"),
    ("van", "Van replenishment"),
    ("rtv", "Return to vendor dispatch"),
    ("refurb", "Refurbishment issue"),
    ("job", "Job-driven urgent issue"),
    ("manual", "Manual demand"),
]
TASK_TYPES = [
    ("pick", "Pick"),
    ("putaway", "Put-Away"),
    ("count", "Count"),
    ("replenish", "Replenish"),
    ("move", "Internal Move"),
]
_PRIO_RANK = {"normal": 0, "urgent": 1, "emergency": 2}


def _seq(env, code, fallback):
    return env["ir.sequence"].sudo().next_by_code(code) or fallback


def _receipt_location(line):
    return line.receipt_id.location_id


def _part_measure(part):
    """kg and m³ of one unit, from the product M16 buys it as (M37 owns them)."""
    product = part.sudo().product_id
    return (product.weight or 0.0, product.volume or 0.0) if product else (0.0, 0.0)


def _bin_load(env, bin_record):
    """(units, kg, m³) the bin's slots hold now."""
    slots = env["fix.wms.slot"].sudo().search([("bin_id", "=", bin_record.id)])
    units = kg = m3 = 0.0
    for slot in slots:
        w, v = _part_measure(slot.part_id)
        units += slot.qty or 0.0
        kg += (slot.qty or 0.0) * w
        m3 += (slot.qty or 0.0) * v
    return units, kg, m3


def _remaining_to_put_away(env, line, skip_putaways=None, skip_crossdocks=None):
    """What a POSTED receipt line accepted and nothing has yet taken: done
    put-aways, cross-docked quantities and return restocks all draw on it."""
    done = (
        env["fix.wms.putaway"]
        .sudo()
        .search([("receipt_line_id", "=", line.id), ("state", "=", "done")])
    )
    if skip_putaways:
        done -= skip_putaways
    docked = (
        env["fix.wms.crossdock"]
        .sudo()
        .search([("receipt_line_id", "=", line.id), ("state", "in", ("staged", "dispatched"))])
    )
    if skip_crossdocks:
        docked -= skip_crossdocks
    return round(
        (line.qty_accepted or 0.0) - sum(done.mapped("qty")) - sum(docked.mapped("qty")), 4
    )


# ============================================================ warehouse
class FixWarehouseWmsGuard(models.Model):
    _inherit = "fix.warehouse"

    def write(self, vals):
        if "wms_enabled" in vals and not vals["wms_enabled"]:
            Slot = self.env["fix.wms.slot"].sudo()
            Task = self.env["fix.wms.task"].sudo()
            for rec in self.filtered("wms_enabled"):
                held = Slot.search_count(
                    [("bin_id.zone_id.warehouse_id", "=", rec.id), ("qty", ">", 0)]
                )
                open_tasks = Task.search_count(
                    [
                        ("bin_id.zone_id.warehouse_id", "=", rec.id),
                        ("state", "in", ("open", "assigned")),
                    ]
                )
                if held or open_tasks:
                    raise UserError(
                        "Warehouse %s still holds stock in %d bin slot(s) and has %d open "
                        "task(s): empty the bins and close the work before turning warehouse "
                        "execution off (BRU-WMS-02)." % (rec.name, held, open_tasks)
                    )
        return super().write(vals)


# ============================================================ bins
class FixWarehouseBinLog(models.Model):
    """FR-WMS-034: a bin is blocked "with an audit record". The bin keeps only
    its current block; the log keeps every block and unblock, by whom, why and
    for how long."""

    _inherit = "fix.warehouse.bin"

    block_log_ids = fields.One2many("fix.wms.bin.block.log", "bin_id", string="Block History")

    def action_block(self, reason=None):
        res = super().action_block(reason)
        Log = self.env["fix.wms.bin.block.log"].sudo()
        for rec in self:
            Log.create(
                {
                    "bin_id": rec.id,
                    "event": "block",
                    "reason": (reason or "").strip(),
                    "user_id": self.env.user.id,
                }
            )
        publish(
            self.env,
            "wh.bin_blocked",
            "fix.warehouse.bin",
            self[:1].id,
            {"bins": self.ids, "reason": (reason or "").strip()},
        )
        return res

    def _fix_open_bin(self, note):
        last = (
            self.env["fix.wms.bin.block.log"]
            .sudo()
            .search([("bin_id", "=", self.id), ("event", "=", "block")], limit=1)
        )
        res = super()._fix_open_bin(note)
        hours = 0.0
        if last:
            hours = round((fields.Datetime.now() - last.at).total_seconds() / 3600.0, 2)
        self.env["fix.wms.bin.block.log"].sudo().create(
            {
                "bin_id": self.id,
                "event": "unblock",
                "reason": (note or "").strip() or "-",
                "user_id": self.env.user.id,
                "blocked_hours": hours,
            }
        )
        return res


class FixWmsBinBlockLog(models.Model):
    _name = "fix.wms.bin.block.log"
    _description = "Bin Block History"
    _order = "at desc, id desc"

    bin_id = fields.Many2one("fix.warehouse.bin", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(
        related="bin_id.zone_id.warehouse_id.company_id", store=True, index=True
    )
    event = fields.Selection([("block", "Blocked"), ("unblock", "Unblocked")], required=True)
    reason = fields.Char(required=True)
    user_id = fields.Many2one("res.users", string="By", required=True)
    at = fields.Datetime(string="On", required=True, default=fields.Datetime.now)
    blocked_hours = fields.Float(string="Blocked For (h)")

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("The block history is written by Block / Unblock only.")
        return super().create(vals_list)

    def write(self, vals):
        raise AccessError("The block history is append-only.")

    def unlink(self):
        raise AccessError("The block history is append-only.")


class FixWmsSlotMeasure(models.Model):
    _inherit = "fix.wms.slot"

    @api.constrains("qty", "bin_id")
    def _check_weight_volume(self):
        """BRU-WMS-09: a bin's weight and volume limits hold, not only its count."""
        for bin_record in self.mapped("bin_id"):
            limit_kg = bin_record.max_weight_kg or 0.0
            limit_m3 = bin_record._fix_volume_limit()
            if not limit_kg and not limit_m3:
                continue
            _units, kg, m3 = _bin_load(self.env, bin_record)
            if limit_kg and kg > limit_kg + EPS:
                raise ValidationError(
                    "Bin %s carries at most %s kg; this would put %s kg in it (BRU-WMS-09)."
                    % (bin_record.name, limit_kg, round(kg, 3))
                )
            if limit_m3 and m3 > limit_m3 + EPS:
                raise ValidationError(
                    "Bin %s holds at most %s m³; this would put %s m³ in it (BRU-WMS-09)."
                    % (bin_record.name, limit_m3, round(m3, 4))
                )


# ============================================================ dock doors
class FixWmsDockDoor(models.Model):
    """FR-WMS-008: inbound deliveries are scheduled against dock slots: the
    doors themselves are master data of the warehouse."""

    _name = "fix.wms.dock.door"
    _description = "Dock Door"
    _order = "warehouse_id, code"

    warehouse_id = fields.Many2one("fix.warehouse", required=True, ondelete="restrict", index=True)
    company_id = fields.Many2one(related="warehouse_id.company_id", store=True, index=True)
    code = fields.Char(string="Door", required=True)
    name = fields.Char(string="Description")
    direction = fields.Selection(
        [("inbound", "Inbound"), ("outbound", "Outbound"), ("both", "Both")],
        required=True,
        default="both",
    )
    max_vehicle = fields.Selection(
        [("van", "Van / pickup"), ("truck", "Covered truck"), ("container", "Container")],
        string="Largest Vehicle",
        default="truck",
    )
    active = fields.Boolean(default=True)

    _door_unique = models.Constraint(
        "UNIQUE (warehouse_id, code)", "A door code is unique in its warehouse"
    )

    @api.depends("code", "warehouse_id.code")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s / %s" % (rec.warehouse_id.code or "-", rec.code or "-")

    @api.model_create_multi
    def create(self, vals_list):
        _require_floor_admin(self.env, "define a dock door")
        return super().create(vals_list)

    def write(self, vals):
        _require_floor_admin(self.env, "change a dock door")
        return super().write(vals)


class FixWmsDockTimes(models.Model):
    _inherit = "fix.wms.dock"

    door_id = fields.Many2one("fix.wms.dock.door", string="Dock Door", ondelete="restrict")
    arrived_at = fields.Datetime(string="Arrived", readonly=True, copy=False)
    unload_started_at = fields.Datetime(string="Unloading Started", readonly=True, copy=False)
    completed_at = fields.Datetime(string="Completed", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"arrived_at", "unload_started_at", "completed_at"}

    @api.constrains("door_id", "dock_type")
    def _check_door(self):
        for rec in self.filtered("door_id"):
            if rec.door_id.direction not in ("both", rec.dock_type):
                raise ValidationError(
                    "Door %s is %s only; this appointment is %s."
                    % (rec.door_id.code, rec.door_id.direction, rec.dock_type)
                )

    @api.constrains("dock_no", "door_id", "slot_start", "slot_end", "state")
    def _check_overlap(self):
        """One appointment per DOOR per window. Door codes repeat across
        warehouses (D1 at Tejgaon and D1 at Chattogram), so a door-booked
        appointment clashes only with its own door; a free-text dock keeps the
        company-wide dock-number check it had."""
        for rec in self.filtered(lambda d: d.state != "cancelled"):
            domain = [
                ("id", "!=", rec.id),
                ("company_id", "=", rec.company_id.id),
                ("state", "!=", "cancelled"),
                ("slot_start", "<", rec.slot_end),
                ("slot_end", ">", rec.slot_start),
            ]
            if rec.door_id:
                domain.append(("door_id", "=", rec.door_id.id))
            else:
                domain += [("door_id", "=", False), ("dock_no", "=", rec.dock_no)]
            clash = self.sudo().search(domain, limit=1)
            if clash:
                raise ValidationError(
                    "Dock %s is already booked %s - %s (%s)."
                    % (
                        rec.door_id.display_name or rec.dock_no,
                        clash.slot_start,
                        clash.slot_end,
                        clash.name,
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        Door = self.env["fix.wms.dock.door"].sudo()
        for vals in vals_list:
            if vals.get("door_id"):
                vals["dock_no"] = Door.browse(vals["door_id"]).code
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("door_id"):
            vals = dict(
                vals, dock_no=self.env["fix.wms.dock.door"].sudo().browse(vals["door_id"]).code
            )
        return super().write(vals)

    def action_check_in(self):
        res = super().action_check_in()
        self._guarded().write({"arrived_at": fields.Datetime.now()})
        return res

    def action_start_unload(self):
        """FR-WMS-008: record when unloading starts (the unload clock, AUT-WMS-01)."""
        for rec in self:
            if rec.state != "checked_in" or rec.unload_started_at:
                raise UserError("Start unloading a checked-in appointment, once.")
            rec._guarded().write({"unload_started_at": fields.Datetime.now()})
        return True

    def action_complete(self):
        res = super().action_complete()
        self._guarded().write({"completed_at": fields.Datetime.now()})
        return res


# ============================================================ directed put-away
class FixWmsPutawayDirected(models.Model):
    """FR-WMS-013/014/015, T-01, BRU-WMS-06: the system directs the bin.

    The directive runs the strategy sequence fixed bin -> addition to existing
    stock -> near the pick face -> nearest empty bin -> bulk, under capacity
    (count, weight, volume), storage class and ownership class, and stores the
    strategy that answered and every bin it rejected, so "why here?" has an
    answer. A person who wants another bin records a reason; the put-away then
    waits for a Warehouse Supervisor other than that person to approve it."""

    _inherit = "fix.wms.putaway"

    to_bin_id = fields.Many2one(required=False)
    directed_bin_id = fields.Many2one(
        "fix.warehouse.bin", string="Directed Bin", readonly=True, copy=False
    )
    strategy_used = fields.Selection(STRATEGIES, string="Strategy", readonly=True, copy=False)
    rejected_bins = fields.Text(string="Bins Rejected (why)", readonly=True, copy=False)
    directed_at = fields.Datetime(string="Directed On", readonly=True, copy=False)
    override_reason = fields.Selection(OVERRIDE_REASONS, string="Override Reason")
    override_note = fields.Char(string="Override Note")
    override_state = fields.Selection(
        [("none", "No Override"), ("pending", "Awaiting Approval"), ("approved", "Approved")],
        string="Override",
        required=True,
        default="none",
        copy=False,
    )
    override_by_id = fields.Many2one("res.users", string="Overridden By", readonly=True, copy=False)
    override_approved_by_id = fields.Many2one(
        "res.users", string="Override Approved By", readonly=True, copy=False
    )
    exception_ids = fields.One2many("fix.wms.putaway.exception", "putaway_id", string="Exceptions")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "directed_bin_id",
            "strategy_used",
            "rejected_bins",
            "directed_at",
            "override_state",
            "override_by_id",
            "override_approved_by_id",
        }

    def _remaining_on_line(self, line):
        return _remaining_to_put_away(self.env, line, skip_putaways=self)

    # ---------------------------------------------------------------- engine
    def _fix_bin_refusal(self, bin_record, part, qty, ownership, exclude):
        if bin_record in exclude:
            return "excluded after an exception"
        if bin_record._fix_is_blocked():
            return "blocked"
        zone = bin_record.zone_id
        if zone.zone_type in NO_PUTAWAY_ZONES:
            return "%s zone takes no put-away" % zone.zone_type
        if (part.storage_class or "general") == "hazardous" and bin_record.storage_class != (
            "hazardous"
        ):
            return "not a hazardous-class bin"
        bin_class = bin_record.ownership_class or "any"
        if bin_class != "any" and bin_class != ownership:
            return "holds %s stock only" % bin_class
        units, kg, m3 = _bin_load(self.env, bin_record)
        w, v = _part_measure(part)
        if bin_record.capacity_qty and units + qty > bin_record.capacity_qty + EPS:
            return "full (%s of %s)" % (round(units, 3), bin_record.capacity_qty)
        if bin_record.max_weight_kg and kg + qty * w > bin_record.max_weight_kg + EPS:
            return "over its weight limit"
        limit_m3 = bin_record._fix_volume_limit()
        if limit_m3 and m3 + qty * v > limit_m3 + EPS:
            return "over its volume limit"
        return None

    def _fix_direct(self, exclude=None):
        """Return (bin, strategy, rejected[]) for this put-away (T-01)."""
        self.ensure_one()
        exclude = exclude or self.env["fix.warehouse.bin"]
        line = self.receipt_line_id
        if not line:
            raise UserError("A put-away is directed from the receipt line it puts away.")
        location = _receipt_location(line)
        warehouses = (
            self.env["fix.warehouse"]
            .sudo()
            .search([("stock_location_id", "=", location.id), ("wms_enabled", "=", True)])
        )
        if not warehouses:
            raise UserError(
                "No warehouse that runs warehouse execution breaks down %s: there are no bins "
                "to direct to (BRU-WMS-02)." % location.code
            )
        part, qty = self.part_id, self.qty
        ownership = line.receipt_id.ownership_class or "owned"
        Bin = self.env["fix.warehouse.bin"].sudo()
        Slot = self.env["fix.wms.slot"].sudo()
        bins = Bin.search(
            [("zone_id.warehouse_id", "in", warehouses.ids)], order="pick_sequence, id"
        )
        part_slots = Slot.search([("part_id", "=", part.id), ("bin_id", "in", bins.ids)])
        held = {s.bin_id.id for s in Slot.search([("bin_id", "in", bins.ids), ("qty", ">", EPS)])}
        pick_faces = part_slots.filtered(lambda s: s.slot_type == "pick").mapped("bin_id")
        pick_zones = pick_faces.mapped("zone_id")
        candidates = [
            ("fixed", pick_faces),
            ("existing", part_slots.filtered(lambda s: s.qty > EPS).mapped("bin_id") - pick_faces),
            (
                "near_pick",
                bins.filtered(lambda b: b.zone_id in pick_zones and b.id not in held),
            ),
            (
                "empty",
                bins.filtered(
                    lambda b: b.id not in held and b.zone_id.zone_type in ("storage", "pick")
                ),
            ),
            ("bulk", bins.filtered(lambda b: b.zone_id.zone_type == "bulk")),
        ]
        rejected, seen = [], set()
        for strategy, group in candidates:
            for bin_record in group.sorted(lambda b: (b.pick_sequence, b.id)):
                why = self._fix_bin_refusal(bin_record, part, qty, ownership, exclude)
                if not why:
                    return bin_record, strategy, rejected
                if bin_record.id not in seen and len(rejected) < 25:
                    seen.add(bin_record.id)
                    rejected.append({"bin": bin_record.name, "strategy": strategy, "why": why})
        return Bin.browse(), "manual", rejected

    def _fix_apply_direction(self, exclude=None):
        for rec in self:
            target, strategy, rejected = rec._fix_direct(exclude)
            vals = {
                "directed_bin_id": target.id or False,
                "strategy_used": strategy,
                "rejected_bins": json.dumps(rejected, ensure_ascii=False, indent=0),
                "directed_at": fields.Datetime.now(),
            }
            rec._guarded().write(vals)
            if target and (not rec.to_bin_id or rec.override_state == "none"):
                rec._guarded().write({"to_bin_id": target.id})

    # ---------------------------------------------------------------- CRUD
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list, strict=True):
            if not rec.receipt_line_id:
                continue
            chosen = rec.to_bin_id
            rec._fix_apply_direction()
            if chosen and rec.directed_bin_id != chosen:
                rec._fix_record_override(chosen, vals.get("override_reason"))
        return records

    def write(self, vals):
        if "to_bin_id" not in vals or self._fix_guard_open():
            return super().write(vals)
        res = True
        for rec in self:
            target = self.env["fix.warehouse.bin"].browse(vals["to_bin_id"] or 0)
            if rec.state != "pending" or target == rec.to_bin_id:
                res = super(FixWmsPutawayDirected, rec).write(vals)
                continue
            rest = {k: v for k, v in vals.items() if k != "to_bin_id"}
            if rest:
                super(FixWmsPutawayDirected, rec).write(rest)
            if rec.directed_bin_id and target == rec.directed_bin_id:
                rec._guarded().write(
                    {
                        "to_bin_id": target.id,
                        "override_state": "none",
                        "override_by_id": False,
                        "override_approved_by_id": False,
                    }
                )
            else:
                rec._fix_record_override(target, vals.get("override_reason"))
        return res

    def _fix_record_override(self, target, reason=None):
        """BRU-WMS-06 / FR-WMS-014: another bin than the directive's needs a reason
        and a supervisor's approval (never the overrider's own)."""
        self.ensure_one()
        reason = reason or self.override_reason
        if not reason and self.env.su:
            # trusted system code (seeds, hand-offs) names its bin on purpose
            reason = "other"
        if not reason:
            raise UserError(
                "The directive sends this put-away to %s (%s). Putting it into %s instead is "
                "an override: give the override reason (BRU-WMS-06)."
                % (
                    self.directed_bin_id.name or "no eligible bin",
                    dict(STRATEGIES).get(self.strategy_used, "-"),
                    target.name,
                )
            )
        if self.env.su:
            state, approver = "approved", self.env.user.id
        else:
            state, approver = "pending", False
        self._guarded().write(
            {
                "to_bin_id": target.id,
                "override_reason": reason,
                "override_state": state,
                "override_by_id": self.env.user.id,
                "override_approved_by_id": approver,
            }
        )

    # ---------------------------------------------------------------- actions
    def action_direct(self):
        """Re-run the directive (FR-WMS-013) on a pending put-away."""
        for rec in self:
            if rec.state != "pending":
                raise UserError("Direct a pending put-away.")
            rec._guarded().write(
                {
                    "override_state": "none",
                    "override_by_id": False,
                    "override_approved_by_id": False,
                }
            )
            rec._fix_apply_direction()
            if not rec.directed_bin_id:
                raise UserError(
                    "No bin of the warehouse can take %s x %s: %s"
                    % (rec.qty, rec.part_id.part_number, rec.rejected_bins or "no bins")
                )
        return True

    def action_approve_override(self):
        require_supervisor(self.env, "approve a put-away override")
        for rec in self:
            if rec.override_state != "pending":
                raise UserError("Put-away %s has no override awaiting approval." % rec.name)
            if rec.override_by_id == self.env.user and not self.env.su:
                raise AccessError(
                    "You overrode the directive on %s: another supervisor approves it "
                    "(spec section 13 segregation of duties)." % rec.name
                )
            rec._guarded().write(
                {"override_state": "approved", "override_approved_by_id": self.env.user.id}
            )
            publish(
                self.env,
                "wh.directive_overridden",
                "fix.wms.putaway",
                rec.id,
                {
                    "putaway": rec.name,
                    "intended_bin": rec.directed_bin_id.name or None,
                    "actual_bin": rec.to_bin_id.name,
                    "reason": rec.override_reason,
                    "by": rec.override_by_id.id,
                    "approved_by": self.env.user.id,
                },
            )
        return True

    def action_reject_override(self):
        require_supervisor(self.env, "reject a put-away override")
        for rec in self:
            if rec.override_state != "pending":
                raise UserError("Put-away %s has no override awaiting approval." % rec.name)
            rec._guarded().write(
                {
                    "to_bin_id": rec.directed_bin_id.id or False,
                    "override_state": "none",
                    "override_by_id": False,
                }
            )
        return True

    def action_report_exception(self, cause=None, note=None):
        """FR-WMS-015: the directed bin is full or blocked, or the item is
        damaged. The cause is recorded; a full or blocked bin re-directs to the
        next eligible bin and gets a count-back (FR-WMS-033)."""
        if cause not in dict(EXCEPTION_CAUSES):
            raise UserError("Say what went wrong: full bin, blocked bin or damaged item.")
        Exc = self.env["fix.wms.putaway.exception"].sudo()
        Task = self.env["fix.wms.task"].sudo()
        for rec in self:
            if rec.state != "pending":
                raise UserError("Report an exception on a pending put-away.")
            bin_record = rec.to_bin_id
            exc = Exc.create(
                {
                    "putaway_id": rec.id,
                    "cause": cause,
                    "bin_id": bin_record.id or False,
                    "note": (note or "").strip() or False,
                    "reported_by_id": self.env.user.id,
                }
            )
            if cause == "damaged_item":
                continue
            if bin_record and cause == "full_bin":
                Task.create(
                    {
                        "company_id": rec.company_id.id,
                        "task_type": "count",
                        "ref": "Count-back %s (full bin)" % rec.name,
                        "part_id": rec.part_id.id,
                        "bin_id": bin_record.id,
                        "qty": 0.0,
                    }
                )
            exclude = rec.exception_ids.mapped("bin_id")
            rec._guarded().write(
                {
                    "override_state": "none",
                    "override_by_id": False,
                    "override_approved_by_id": False,
                }
            )
            rec._fix_apply_direction(exclude=exclude)
            if not rec.directed_bin_id:
                rec._guarded().write({"to_bin_id": False})
            exc.sudo().write({"redirected_bin_id": rec.directed_bin_id.id or False})
        return True

    def action_complete(self, bin_code=None, item_code=None):
        for rec in self:
            if not rec.to_bin_id:
                raise UserError(
                    "Put-away %s has no bin: direct it first (no eligible bin was found)."
                    % rec.name
                )
            if rec.override_state == "pending":
                raise UserError(
                    "Put-away %s goes to %s against the directive (%s): a supervisor approves "
                    "the override first (BRU-WMS-06)."
                    % (rec.name, rec.to_bin_id.name, rec.directed_bin_id.name or "no bin")
                )
        return super().action_complete(bin_code, item_code)


class FixWmsPutawayException(models.Model):
    _name = "fix.wms.putaway.exception"
    _description = "Put-Away Exception"
    _order = "reported_at desc, id desc"

    putaway_id = fields.Many2one("fix.wms.putaway", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="putaway_id.company_id", store=True, index=True)
    part_id = fields.Many2one(related="putaway_id.part_id", string="Spare Part")
    cause = fields.Selection(EXCEPTION_CAUSES, required=True)
    bin_id = fields.Many2one("fix.warehouse.bin", string="Bin Found")
    redirected_bin_id = fields.Many2one("fix.warehouse.bin", string="Re-directed To")
    note = fields.Char()
    reported_by_id = fields.Many2one("res.users", string="Reported By", required=True)
    reported_at = fields.Datetime(string="Reported On", required=True, default=fields.Datetime.now)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("Report an exception from its put-away (Report Exception).")
        return super().create(vals_list)


class FixWmsPutawayExceptionEntry(models.Model):
    """Inputs of the Report Exception form (never stored on the put-away)."""

    _inherit = "fix.wms.putaway"

    exception_cause_entry = fields.Selection(
        EXCEPTION_CAUSES, string="What Went Wrong", compute="_compute_exception_entries"
    )
    exception_note_entry = fields.Char(string="Note", compute="_compute_exception_entries")
    scan_bin_entry = fields.Char(string="Scan the Bin", compute="_compute_exception_entries")
    scan_item_entry = fields.Char(string="Scan the Item", compute="_compute_exception_entries")

    def _compute_exception_entries(self):
        for rec in self:
            rec.exception_cause_entry = False
            rec.exception_note_entry = False
            rec.scan_bin_entry = False
            rec.scan_item_entry = False


# ============================================================ handling unit
class FixWmsHandlingUnit(models.Model):
    """FR-WMS-010 / T-11: a licence-plated pallet, carton, tote or cage that is
    moved, stored and traced as one object. One level of nesting. A handling
    unit is a container record: it never moves a ledger quantity."""

    _name = "fix.wms.handling.unit"
    _description = "Handling Unit (Licence Plate)"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(string="Licence Plate", required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    warehouse_id = fields.Many2one("fix.warehouse", required=True, ondelete="restrict", index=True)
    hu_type = fields.Selection(
        [("pallet", "Pallet"), ("carton", "Carton"), ("tote", "Tote"), ("cage", "Cage")],
        string="Type",
        required=True,
        default="pallet",
    )
    parent_id = fields.Many2one(
        "fix.wms.handling.unit", string="Inside Handling Unit", ondelete="restrict"
    )
    child_ids = fields.One2many("fix.wms.handling.unit", "parent_id", string="Nested Units")
    receipt_id = fields.Many2one("fix.stock.receipt", string="Received On", ondelete="restrict")
    wave_id = fields.Many2one("fix.wms.wave", string="Outbound Wave", ondelete="restrict")
    current_bin_id = fields.Many2one(
        "fix.warehouse.bin", string="Stored In Bin", readonly=True, copy=False
    )
    gross_weight_kg = fields.Float(string="Gross Weight (kg)")
    line_ids = fields.One2many("fix.wms.handling.unit.line", "hu_id", string="Contents")
    contents_qty = fields.Float(string="Units (incl. nested)", compute="_compute_contents")
    state = fields.Selection(
        [
            ("open", "Open"),
            ("closed", "Closed / Labelled"),
            ("stored", "Stored"),
            ("dispatched", "Dispatched"),
            ("dissolved", "Dissolved"),
        ],
        required=True,
        default="open",
    )
    closed_by_id = fields.Many2one("res.users", string="Closed By", readonly=True, copy=False)
    closed_at = fields.Datetime(string="Closed On", readonly=True, copy=False)
    scan_bin_entry = fields.Char(string="Scan the Bin", compute="_compute_entry")

    def _compute_entry(self):
        for rec in self:
            rec.scan_bin_entry = False

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "current_bin_id",
            "closed_by_id",
            "closed_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "open":
            locked |= {"warehouse_id", "hu_type", "parent_id", "receipt_id", "wave_id", "line_ids"}
        return locked

    @api.depends("line_ids.qty", "child_ids.line_ids.qty")
    def _compute_contents(self):
        for rec in self:
            rec.contents_qty = round(
                sum(rec.line_ids.mapped("qty")) + sum(rec.child_ids.mapped("line_ids.qty")), 4
            )

    @api.constrains("parent_id", "warehouse_id")
    def _check_nesting(self):
        for rec in self:
            parent = rec.parent_id
            if not parent:
                continue
            if parent == rec or parent.parent_id:
                raise ValidationError(
                    "Handling units nest one level only: %s is already inside %s (T-11)."
                    % (parent.name, parent.parent_id.name or parent.name)
                )
            if rec.child_ids:
                raise ValidationError(
                    "%s holds nested units itself, so it cannot go inside another (T-11)."
                    % rec.name
                )
            if parent.warehouse_id != rec.warehouse_id:
                raise ValidationError("A handling unit nests only inside one of its warehouse.")
            if parent.state != "open":
                raise ValidationError(
                    "Nest into an open handling unit (%s is %s)." % (parent.name, parent.state)
                )

    @api.constrains("line_ids", "receipt_id")
    def _check_against_receipt(self):
        """Contents of a received unit cannot exceed what its receipt accepted."""
        Line = self.env["fix.wms.handling.unit.line"].sudo()
        for receipt in self.mapped("receipt_id"):
            accepted = defaultdict(float)
            for line in receipt.line_ids:
                accepted[line.part_id.id] += line.qty_accepted or line.qty_received or 0.0
            packed = defaultdict(float)
            for line in Line.search(
                [("hu_id.receipt_id", "=", receipt.id), ("hu_id.state", "!=", "dissolved")]
            ):
                packed[line.part_id.id] += line.qty
            for part_id, qty in packed.items():
                if qty > accepted.get(part_id, 0.0) + EPS:
                    part = self.env["fix.spare.part"].browse(part_id)
                    raise ValidationError(
                        "Receipt %s accepted %s of %s; its handling units would hold %s."
                        % (receipt.name, accepted.get(part_id, 0.0), part.part_number, qty)
                    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.wms.handling.unit", "HU/New")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {
                k: vals[k]
                for k in ("warehouse_id", "hu_type", "parent_id", "receipt_id", "wave_id")
                if k in vals
            }
            if (frozen and _differs(self.filtered(lambda h: h.state != "open"), frozen)) or (
                "line_ids" in vals and self.filtered(lambda h: h.state != "open")
            ):
                raise UserError("A closed handling unit's contents are final: dissolve it first.")
        return super().write(vals)

    def action_close(self):
        """Close and label: the contents are now fixed (T-10 label, FR-WMS-010)."""
        for rec in self:
            if rec.state != "open":
                raise UserError("Close an open handling unit.")
            if not rec.line_ids and not rec.child_ids:
                raise UserError("Handling unit %s is empty." % rec.name)
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_by_id": self.env.user.id,
                    "closed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_store(self, bin_code=None):
        """Store the unit in a bin, confirmed by scanning the bin (BRU-WMS-05)."""
        Bin = self.env["fix.warehouse.bin"].sudo()
        code = (bin_code or "").strip()
        for rec in self:
            if rec.state not in ("closed", "stored"):
                raise UserError("Close the handling unit before storing it.")
            if rec.parent_id:
                raise UserError(
                    "%s travels inside %s: store that one." % (rec.name, rec.parent_id.name)
                )
            target = Bin.search(
                [
                    ("zone_id.warehouse_id", "=", rec.warehouse_id.id),
                    "|",
                    ("barcode", "=", code),
                    ("name", "=", code),
                ],
                limit=1,
            )
            if not code or not target:
                raise UserError(
                    "Scanned bin %r is not a bin of %s." % (code, rec.warehouse_id.name)
                )
            if target._fix_is_blocked():
                raise UserError("Bin %s is blocked (BRU-WMS-12)." % target.name)
            rec._guarded().write({"state": "stored", "current_bin_id": target.id})
            rec.child_ids._guarded().write({"state": "stored", "current_bin_id": target.id})
        return True

    def action_dissolve(self):
        for rec in self:
            if rec.state in ("dispatched", "dissolved"):
                raise UserError("Handling unit %s is already %s." % (rec.name, rec.state))
            rec.child_ids._guarded().write({"parent_id": False})
            rec._guarded().write({"state": "dissolved", "current_bin_id": False})
        return True


class FixWmsHandlingUnitLine(models.Model):
    _name = "fix.wms.handling.unit.line"
    _description = "Handling Unit Content"
    _order = "hu_id, id"

    hu_id = fields.Many2one("fix.wms.handling.unit", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="hu_id.company_id", store=True, index=True)
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    qty = fields.Float(string="Quantity", required=True, default=1.0)
    lot_id = fields.Many2one("fix.stock.lot", string="Serial / Lot", ondelete="restrict")

    _qty_positive = models.Constraint("CHECK (qty > 0)", "A content line holds a positive quantity")

    @api.constrains("part_id", "qty", "lot_id")
    def _check_line(self):
        for rec in self:
            check_quantity(rec.part_id, rec.qty, "content quantity")
            if rec.lot_id and rec.lot_id.part_id != rec.part_id:
                raise ValidationError(
                    "Serial %s is not a %s." % (rec.lot_id.name, rec.part_id.part_number)
                )
            if rec.part_id.is_serialized and rec.lot_id and abs(rec.qty - 1.0) > EPS:
                raise ValidationError("A serial is one unit (BRU-WMS-10).")
        self.mapped("hu_id")._check_against_receipt()

    def _refuse_closed(self, units):
        if not self.env.su and units.filtered(lambda h: h.state != "open"):
            raise UserError("A closed handling unit's contents are final: dissolve it first.")

    @api.model_create_multi
    def create(self, vals_list):
        ids = {v.get("hu_id") for v in vals_list if v.get("hu_id")}
        self._refuse_closed(self.env["fix.wms.handling.unit"].browse(list(ids)))
        return super().create(vals_list)

    def write(self, vals):
        self._refuse_closed(self.mapped("hu_id"))
        return super().write(vals)

    def unlink(self):
        self._refuse_closed(self.mapped("hu_id"))
        return super().unlink()


# ============================================================ cross-dock
class FixWmsCrossdock(models.Model):
    """FR-WMS-016 / BRU-WMS-15 / AUT-WMS-05: an inbound line whose demand is
    already waiting goes straight to an outbound staging lane. Only a POSTED
    receipt line's stock that nobody has put away, only for a demand line of a
    wave that is not yet released, in the same warehouse location."""

    _name = "fix.wms.crossdock"
    _description = "Cross-Dock"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    receipt_line_id = fields.Many2one(
        "fix.stock.receipt.line", string="Received Line", required=True, ondelete="restrict"
    )
    wave_line_id = fields.Many2one(
        "fix.wms.wave.line", string="Waiting Demand (wave line)", ondelete="set null"
    )
    wave_id = fields.Many2one("fix.wms.wave", string="Wave", readonly=True, copy=False)
    part_id = fields.Many2one(related="receipt_line_id.part_id", string="Spare Part", store=True)
    qty = fields.Float(string="Quantity", required=True)
    stage_lane = fields.Char(string="Outbound Staging Lane", required=True)
    load_ref = fields.Char(string="Load / Vehicle Ref", readonly=True, copy=False)
    demand_qty_before = fields.Float(string="Demand Before", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("proposed", "Proposed"),
            ("staged", "Staged"),
            ("dispatched", "Dispatched"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="proposed",
    )
    staged_by_id = fields.Many2one("res.users", string="Staged By", readonly=True, copy=False)
    staged_at = fields.Datetime(string="Staged On", readonly=True, copy=False)
    dispatched_by_id = fields.Many2one(
        "res.users", string="Dispatched By", readonly=True, copy=False
    )
    dispatched_at = fields.Datetime(string="Dispatched On", readonly=True, copy=False)
    scan_item_entry = fields.Char(string="Scan the Item", compute="_compute_entries")
    load_ref_entry = fields.Char(string="Load / Vehicle Ref", compute="_compute_entries")

    _qty_positive = models.Constraint("CHECK (qty > 0)", "A cross-dock moves a positive quantity")

    def _compute_entries(self):
        for rec in self:
            rec.scan_item_entry = False
            rec.load_ref_entry = False

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "wave_id",
            "load_ref",
            "demand_qty_before",
            "staged_by_id",
            "staged_at",
            "dispatched_by_id",
            "dispatched_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "proposed":
            locked |= {"receipt_line_id", "wave_line_id", "qty", "stage_lane"}
        return locked

    def _fix_check(self):
        for rec in self:
            line, demand = rec.receipt_line_id, rec.wave_line_id
            if line.receipt_id.state != "posted":
                raise UserError(
                    "Only stock a POSTED receipt accepted is cross-docked (BRU-WMS-04)."
                )
            if not demand:
                raise UserError("Name the waiting demand (wave line) this stock goes to.")
            if demand.part_id != line.part_id:
                raise UserError(
                    "The demand is for %s; the received line is %s."
                    % (demand.part_id.part_number, line.part_id.part_number)
                )
            if demand.state != "pending" or demand.wave_id.state != "draft":
                raise UserError(
                    "Wave %s is already released: cross-dock applies only before the wave is "
                    "released (BRU-WMS-15)." % demand.wave_id.name
                )
            if rec.qty > (demand.qty or 0.0) + EPS:
                raise UserError(
                    "The demand asks for %s; %s cannot be cross-docked to it."
                    % (demand.qty, rec.qty)
                )
            remaining = _remaining_to_put_away(rec.env, line, skip_crossdocks=rec)
            if rec.qty > remaining + EPS:
                raise UserError(
                    "Only %s of receipt %s is still on the dock (the rest was put away or "
                    "cross-docked)." % (remaining, line.receipt_id.name)
                )
            location = _receipt_location(line)
            wave_loc = rec._fix_wave_location(demand.wave_id)
            if wave_loc and wave_loc != location:
                raise UserError(
                    "Receipt %s is at %s; wave %s ships from %s."
                    % (line.receipt_id.name, location.code, demand.wave_id.name, wave_loc.code)
                )
            check_quantity(line.part_id, rec.qty, "cross-dock quantity")
            if line.part_id.is_serialized:
                raise UserError(
                    "%s is serialized: put it away and pick it with its serial (BRU-WMS-10)."
                    % line.part_id.part_number
                )

    @staticmethod
    def _fix_wave_location(wave):
        bins = wave.line_ids.mapped("bin_id")
        warehouse = wave.warehouse_id or bins[:1].zone_id.warehouse_id
        return warehouse.stock_location_id if warehouse else False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.wms.crossdock", "XD/New")
        records = super().create(vals_list)
        records._fix_check()
        for rec in records:
            rec._guarded().write({"wave_id": rec.wave_line_id.wave_id.id})
        return records

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {
                k: vals[k]
                for k in ("receipt_line_id", "wave_line_id", "qty", "stage_lane")
                if k in vals
            }
            if frozen and _differs(self.filtered(lambda r: r.state != "proposed"), frozen):
                raise UserError("A staged cross-dock is final.")
        res = super().write(vals)
        if self and {"receipt_line_id", "wave_line_id", "qty"} & set(vals):
            self.filtered(lambda r: r.state == "proposed")._fix_check()
        return res

    def action_confirm(self, item_code=None):
        """Scan the item on the dock: the quantity moves to STAGED in M15 and the
        waiting demand is fulfilled by it (its wave line shrinks or goes)."""
        Onhand = self.env["fix.stock.onhand"]
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Cross-dock %s is already %s." % (rec.name, rec.state))
            if not self.env.su:
                _scan_item(rec.part_id, item_code)
            rec._fix_check()
            line, demand = rec.receipt_line_id, rec.wave_line_id
            location = _receipt_location(line)
            cls = location_class(location, line.receipt_id.ownership_class or "owned")
            Onhand._fix_move_status(rec.part_id, location, cls, rec.qty, "unrestricted", "staged")
            before = demand.qty
            if rec.qty >= before - EPS:
                demand._guarded().unlink()
            else:
                demand._guarded().write({"qty": round(before - rec.qty, 4)})
            rec._guarded().write(
                {
                    "state": "staged",
                    "demand_qty_before": before,
                    "staged_by_id": self.env.user.id,
                    "staged_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "wh.cross_docked",
                "fix.wms.crossdock",
                rec.id,
                {
                    "crossdock": rec.name,
                    "receipt": line.receipt_id.name,
                    "wave": rec.wave_id.name,
                    "part_id": rec.part_id.id,
                    "qty": rec.qty,
                    "stage": rec.stage_lane,
                },
            )
        return True

    def action_dispatch(self, load_ref=None):
        """Load and dispatch the staged cross-dock: M15 loses the staged stock."""
        load_ref = (load_ref or "").strip()
        if not load_ref:
            raise UserError("Give the load / vehicle reference it leaves on.")
        Onhand = self.env["fix.stock.onhand"]
        Suspense = self.env["fix.inventory.valuation.suspense"]
        for rec in self:
            if rec.state != "staged":
                raise UserError("Dispatch a staged cross-dock.")
            line = rec.receipt_line_id
            location = _receipt_location(line)
            cls = location_class(location, line.receipt_id.ownership_class or "owned")
            bucket = Onhand._bucket(rec.part_id, location, cls, "staged")
            cost = bucket.unit_cost if bucket else 0.0
            Onhand._apply(rec.part_id, location, cls, -rec.qty, status="staged")
            Suspense._fix_post(
                "shipment", rec.part_id, -rec.qty, cost, rec.name, location=location, ownership=cls
            )
            rec._guarded().write(
                {
                    "state": "dispatched",
                    "load_ref": load_ref,
                    "dispatched_by_id": self.env.user.id,
                    "dispatched_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "wh.dispatched",
                "fix.wms.crossdock",
                rec.id,
                {
                    "crossdock": rec.name,
                    "location_id": location.id,
                    "load_ref": load_ref,
                    "lines": [{"part_id": rec.part_id.id, "qty": rec.qty}],
                },
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Only a proposed cross-dock is cancelled; a staged one ships.")
            rec._guarded().write({"state": "cancelled"})
        return True


# ============================================================ return receiving
class FixWmsReturnReceipt(models.Model):
    """FR-WMS-017: branch returns, RTV rejects, customer-supplied parts and
    harvested components arrive in the returns area and wait for a disposition
    decision. The decision is a second person's (a Warehouse Supervisor or
    Inventory Controller, never the receiver). Restock raises a directed
    put-away of the receipt line that brought the stock in; the other
    dispositions are M15 records (quarantine, RTV, scrap) the decision names."""

    _name = "fix.wms.return.receipt"
    _description = "Return Receiving"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    warehouse_id = fields.Many2one("fix.warehouse", required=True, ondelete="restrict")
    source_type = fields.Selection(
        [
            ("branch_return", "Branch return"),
            ("rtv_reject", "RTV reject (vendor refused)"),
            ("customer_supplied", "Customer-supplied part"),
            ("harvested", "Harvested component"),
        ],
        string="Return Type",
        required=True,
    )
    source_ref = fields.Char(string="Source Document", required=True)
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    qty = fields.Float(string="Quantity", required=True, default=1.0)
    lot_id = fields.Many2one("fix.stock.lot", string="Serial / Lot", ondelete="restrict")
    receipt_line_id = fields.Many2one(
        "fix.stock.receipt.line",
        string="M15 Receipt Line",
        ondelete="restrict",
        help="The posted M15 receipt line that brought the return into the ledger.",
    )
    returns_bin_id = fields.Many2one(
        "fix.warehouse.bin", string="Returns Bin", required=True, ondelete="restrict"
    )
    condition = fields.Selection(
        [
            ("good", "Good / unused"),
            ("used", "Used, working"),
            ("faulty", "Faulty"),
            ("damaged", "Physically damaged"),
        ],
        required=True,
        default="good",
    )
    disposition = fields.Selection(
        [
            ("restock", "Restock (put away)"),
            ("quarantine", "Quarantine"),
            ("rtv", "Return to vendor"),
            ("refurbish", "Send to refurbishment"),
            ("scrap", "Scrap"),
        ],
        string="Disposition",
    )
    disposition_note = fields.Char(string="Disposition Note / M15 Reference")
    state = fields.Selection(
        [("received", "Received - Awaiting Disposition"), ("disposed", "Disposed")],
        required=True,
        default="received",
    )
    received_by_id = fields.Many2one(
        "res.users", string="Received By", readonly=True, default=lambda self: self.env.user
    )
    disposed_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    disposed_at = fields.Datetime(string="Decided On", readonly=True, copy=False)
    putaway_id = fields.Many2one(
        "fix.wms.putaway", string="Restock Put-Away", readonly=True, copy=False
    )

    _qty_positive = models.Constraint("CHECK (qty > 0)", "A return holds a positive quantity")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "received_by_id",
            "disposed_by_id",
            "disposed_at",
            "putaway_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "received":
            locked |= {
                "warehouse_id",
                "source_type",
                "source_ref",
                "part_id",
                "qty",
                "lot_id",
                "receipt_line_id",
                "returns_bin_id",
                "condition",
                "disposition",
                "disposition_note",
            }
        return locked

    @api.constrains("returns_bin_id", "warehouse_id", "receipt_line_id", "part_id", "qty", "lot_id")
    def _check_return(self):
        for rec in self:
            if rec.returns_bin_id.zone_id.zone_type != "returns":
                raise ValidationError(
                    "Bin %s is not in a returns zone: returns are held apart (FR-WMS-017)."
                    % rec.returns_bin_id.name
                )
            if _warehouse_of(rec.returns_bin_id) != rec.warehouse_id:
                raise ValidationError("The returns bin belongs to another warehouse.")
            check_quantity(rec.part_id, rec.qty, "returned quantity")
            if rec.lot_id and rec.lot_id.part_id != rec.part_id:
                raise ValidationError(
                    "Serial %s is not a %s." % (rec.lot_id.name, rec.part_id.part_number)
                )
            line = rec.receipt_line_id
            if line and line.part_id != rec.part_id:
                raise ValidationError("Receipt line %s is for another part." % line.receipt_id.name)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.wms.return.receipt", "RET/New")
        return super().create(vals_list)

    def write(self, vals):
        if (
            self
            and not self._fix_guard_open()
            and self.filtered(lambda r: r.state != "received")
            and set(vals) - {"disposition_note"}
        ):
            raise UserError("A disposed return is final.")
        return super().write(vals)

    def action_dispose(self):
        if not (
            is_supervisor(self.env)
            or self.env.user.has_group("cd_wms_structure.group_inventory_controller")
        ):
            raise AccessError(
                "A Warehouse Supervisor or Inventory Controller decides a return's disposition."
            )
        Putaway = self.env["fix.wms.putaway"]
        for rec in self:
            if rec.state != "received":
                raise UserError("Return %s is already disposed." % rec.name)
            if not rec.disposition:
                raise UserError("Choose the disposition first.")
            if rec.received_by_id == self.env.user and not self.env.su:
                raise AccessError(
                    "You received return %s: another person decides its disposition." % rec.name
                )
            vals = {
                "state": "disposed",
                "disposed_by_id": self.env.user.id,
                "disposed_at": fields.Datetime.now(),
            }
            if rec.disposition == "restock":
                line = rec.receipt_line_id
                if not line or line.receipt_id.state != "posted":
                    raise UserError(
                        "Restock puts away stock a POSTED M15 receipt brought in: link the "
                        "receipt line of return %s." % rec.name
                    )
                if rec.condition in ("faulty", "damaged"):
                    raise UserError("A %s part is not restocked." % rec.condition)
                putaway = Putaway.sudo().create(
                    {
                        "company_id": rec.company_id.id,
                        "part_id": rec.part_id.id,
                        "qty": rec.qty,
                        "receipt_line_id": line.id,
                        "lot_id": rec.lot_id.id or False,
                        "from_ref": rec.name,
                    }
                )
                vals["putaway_id"] = putaway.id
            elif not (rec.disposition_note or "").strip():
                raise UserError(
                    "Name the M15 %s record that carries this return (disposition note)."
                    % dict(self._fields["disposition"].selection)[rec.disposition]
                )
            rec._guarded().write(vals)
            publish(
                self.env,
                "wh.return_disposed",
                "fix.wms.return.receipt",
                rec.id,
                {
                    "return": rec.name,
                    "part_id": rec.part_id.id,
                    "qty": rec.qty,
                    "disposition": rec.disposition,
                    "ref": rec.disposition_note or None,
                },
            )
        return True


# ============================================================ outbound demand
WAVE_STRATEGIES_ADD = [("cluster", "Cluster Picking"), ("pick_pass", "Pick-and-Pass")]
_STRATEGY_ONDELETE = {"cluster": "set default", "pick_pass": "set default"}
NO_PICK_ZONES = ("inspection", "quarantine", "returns", "staging", "dispatch", "receiving")


class FixWmsWaveTemplateSpec(models.Model):
    """FR-WMS-019: a template by purpose, with its own release rule, cut-off,
    priority, pick strategy and destination filter."""

    _inherit = "fix.wms.wave.template"

    strategy = fields.Selection(selection_add=WAVE_STRATEGIES_ADD, ondelete=_STRATEGY_ONDELETE)
    warehouse_id = fields.Many2one("fix.warehouse", string="Warehouse", ondelete="restrict")
    purpose = fields.Selection(
        [
            ("branch_run", "Scheduled branch run"),
            ("urgent", "Urgent job-driven"),
            ("van", "Van replenishment"),
            ("rtv", "RTV consolidation"),
            ("refurb", "Refurbishment issue"),
        ],
        required=True,
        default="branch_run",
    )
    release_rule = fields.Selection(
        [
            ("cutoff", "At the cut-off"),
            ("manual", "When a supervisor releases"),
            ("immediate", "As soon as it is waved (urgent)"),
        ],
        string="Release Rule",
        required=True,
        default="cutoff",
    )
    priority = fields.Selection(PRIORITIES, required=True, default="normal")
    dest_location_ids = fields.Many2many(
        "fix.stock.location",
        string="Destinations (empty: any)",
        help="Only demand bound for these locations joins a wave of this template.",
    )

    @api.constrains("cutoff")
    def _check_cutoff(self):
        for rec in self:
            value = (rec.cutoff or "").strip()
            if value:
                try:
                    datetime.strptime(value, "%H:%M")
                except ValueError:
                    raise ValidationError("Cut-off %r is not a time (HH:MM)." % value) from None


class FixWmsWaveSpec(models.Model):
    _inherit = "fix.wms.wave"

    strategy = fields.Selection(selection_add=WAVE_STRATEGIES_ADD, ondelete=_STRATEGY_ONDELETE)
    template_id = fields.Many2one("fix.wms.wave.template", string="Template", ondelete="restrict")
    cutoff_at = fields.Datetime(string="Cut-off")
    priority = fields.Selection(
        PRIORITIES, compute="_compute_priority", store=True, string="Priority"
    )
    demand_ids = fields.One2many("fix.wms.outbound.demand", "wave_id", string="Demand Waved")

    @api.depends("line_ids.priority")
    def _compute_priority(self):
        for rec in self:
            ranks = [_PRIO_RANK.get(p or "normal", 0) for p in rec.line_ids.mapped("priority")]
            top = max(ranks) if ranks else 0
            rec.priority = {v: k for k, v in _PRIO_RANK.items()}[top]

    @api.model_create_multi
    def create(self, vals_list):
        Template = self.env["fix.wms.wave.template"].sudo()
        for vals in vals_list:
            template = Template.browse(vals.get("template_id") or 0).exists()
            if template:
                vals.setdefault("strategy", template.strategy)
                if template.warehouse_id:
                    vals.setdefault("warehouse_id", template.warehouse_id.id)
                if template.cutoff and not vals.get("cutoff_at"):
                    try:
                        hhmm = datetime.strptime(template.cutoff.strip(), "%H:%M").time()
                        vals["cutoff_at"] = datetime.combine(
                            fields.Date.context_today(self), time(hhmm.hour, hhmm.minute)
                        ) - timedelta(hours=6)  # Asia/Dhaka (UTC+6) wall time -> UTC
                    except ValueError:
                        pass
        return super().create(vals_list)

    def action_release(self):
        res = super().action_release()
        # FR-WMS-022 / T-09: the pick tasks are walked in bin sequence
        Task = self.env["fix.wms.task"].sudo()
        for rec in self:
            ordered = rec.line_ids.sorted(lambda ln: (ln.bin_id.pick_sequence, ln.bin_id.id, ln.id))
            for seq, line in enumerate(ordered, start=1):
                line._guarded().write({"pick_sequence": seq})
                Task.search([("wave_line_id", "=", line.id)])._guarded().write(
                    {"pick_sequence": seq}
                )
        return res


class FixWmsWaveLineSpec(models.Model):
    _inherit = "fix.wms.wave.line"
    _order = "wave_id, pick_sequence, id"

    source_type = fields.Selection(DEMAND_SOURCES, string="Demand Source", default="manual")
    source_ref = fields.Char(string="Source Document")
    dest_location_id = fields.Many2one(
        "fix.stock.location", string="Destination", ondelete="restrict"
    )
    priority = fields.Selection(PRIORITIES, default="normal")
    demand_id = fields.Many2one(
        "fix.wms.outbound.demand", string="Demand", readonly=True, copy=False
    )
    pick_sequence = fields.Integer(string="Pick Sequence", readonly=True, copy=False)
    resourced_from_id = fields.Many2one(
        "fix.wms.wave.line", string="Re-sourced From", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"demand_id", "pick_sequence", "resourced_from_id"}

    def action_scan_short_pick(self, bin_code=None, item_code=None, found_qty=None, serial=None):
        res = super().action_scan_short_pick(bin_code, item_code, found_qty, serial)
        for line in self.filtered(lambda ln: ln.state == "short"):
            line._fix_resource()
        return res

    def _fix_pick_slots(self, part, warehouse, exclude_bins=None):
        """Slots a wave may pick this part from: active, pickable, owned or
        unrestricted bins of the warehouse; pick faces first, then walk order."""
        exclude_bins = exclude_bins or self.env["fix.warehouse.bin"]
        slots = (
            self.env["fix.wms.slot"]
            .sudo()
            .search(
                [
                    ("part_id", "=", part.id),
                    ("state", "=", "active"),
                    ("bin_id.zone_id.warehouse_id", "=", warehouse.id),
                ]
            )
        )
        ok = slots.filtered(
            lambda s: s.bin_id not in exclude_bins
            and not s.bin_id._fix_is_blocked()
            and s.bin_id.zone_id.reservable
            and s.bin_id.zone_id.zone_type not in NO_PICK_ZONES
            and (s.bin_id.ownership_class or "any") in ("any", "owned")
        )
        return ok.sorted(lambda s: (s.slot_type != "pick", s.bin_id.pick_sequence, s.id))

    def _fix_resource(self):
        """FR-WMS-024 / AUT-WMS-09: the shortfall is re-sourced from another bin
        with free stock: a new pick line, allocated in M15 and on the slot, with
        its pick task. The short line closes at what it really picked."""
        self.ensure_one()
        Onhand = self.env["fix.stock.onhand"]
        Task = self.env["fix.wms.task"].sudo()
        wave = self.wave_id
        warehouse, location = wave._wave_location()
        cls = location_class(location)
        shortfall = round((self.qty or 0.0) - (self.picked_qty or 0.0), 4)
        for slot in self._fix_pick_slots(self.part_id, warehouse, exclude_bins=self.bin_id):
            free = round((slot.qty or 0.0) - (slot.reserved_qty or 0.0), 4)
            take = min(free, shortfall)
            if is_whole_unit(self.part_id):
                take = float(int(take + EPS))
            if take <= EPS:
                continue
            Onhand._fix_reserve(self.part_id, location, cls, take, wave.name)
            slot._guarded().write({"reserved_qty": round((slot.reserved_qty or 0.0) + take, 4)})
            new = (
                self.env["fix.wms.wave.line"]
                ._guarded()
                .create(
                    {
                        "wave_id": wave.id,
                        "part_id": self.part_id.id,
                        "bin_id": slot.bin_id.id,
                        "qty": take,
                        "reserved_qty": take,
                        "source_type": self.source_type,
                        "source_ref": self.source_ref,
                        "dest_location_id": self.dest_location_id.id or False,
                        "priority": self.priority,
                        "demand_id": self.demand_id.id or False,
                        "resourced_from_id": self.id,
                    }
                )
            )
            Task.create(
                {
                    "company_id": wave.company_id.id,
                    "task_type": "pick",
                    "ref": "%s (re-sourced)" % wave.name,
                    "wave_line_id": new.id,
                    "part_id": self.part_id.id,
                    "bin_id": slot.bin_id.id,
                    "qty": take,
                }
            )
            if (self.picked_qty or 0.0) > EPS:
                self._guarded().write({"qty": self.picked_qty, "state": "picked"})
            else:
                self._guarded().write({"state": "cancelled"})
            return new
        return self.browse()


class FixWmsOutboundDemand(models.Model):
    """FR-WMS-018: outbound demand queues with its source, destination,
    priority and cut-off until a wave takes it (FR-WMS-020). Building a wave
    chooses the pick bins from free slot stock, pick faces first."""

    _name = "fix.wms.outbound.demand"
    _description = "Outbound Demand"
    _order = "state, priority desc, cutoff_at, id"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    warehouse_id = fields.Many2one("fix.warehouse", required=True, ondelete="restrict")
    source_type = fields.Selection(
        DEMAND_SOURCES, string="Source", required=True, default="transfer"
    )
    source_ref = fields.Char(string="Source Document", required=True)
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    qty = fields.Float(string="Quantity", required=True, default=1.0)
    dest_location_id = fields.Many2one(
        "fix.stock.location", string="Destination", required=True, ondelete="restrict"
    )
    priority = fields.Selection(PRIORITIES, required=True, default="normal")
    cutoff_at = fields.Datetime(string="Needed By (cut-off)")
    template_id = fields.Many2one(
        "fix.wms.wave.template", string="Wave Template", ondelete="restrict"
    )
    state = fields.Selection(
        [("queued", "Queued"), ("waved", "Waved"), ("cancelled", "Cancelled")],
        required=True,
        default="queued",
    )
    wave_id = fields.Many2one("fix.wms.wave", string="Wave", readonly=True, copy=False)
    short_note = fields.Char(string="Waiting Because", readonly=True, copy=False)

    _qty_positive = models.Constraint("CHECK (qty > 0)", "Demand is for a positive quantity")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "wave_id", "short_note"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "queued":
            locked |= {
                "warehouse_id",
                "source_type",
                "source_ref",
                "part_id",
                "qty",
                "dest_location_id",
                "priority",
                "cutoff_at",
                "template_id",
            }
        return locked

    @api.constrains("part_id", "qty", "warehouse_id", "dest_location_id", "template_id")
    def _check_demand(self):
        for rec in self:
            check_quantity(rec.part_id, rec.qty, "demand quantity")
            if not rec.warehouse_id.wms_enabled:
                raise ValidationError(
                    "Warehouse %s does not run warehouse execution (BRU-WMS-02)."
                    % rec.warehouse_id.name
                )
            if rec.dest_location_id == rec.warehouse_id.stock_location_id:
                raise ValidationError("Demand goes to another location than the warehouse itself.")
            tpl = rec.template_id
            if tpl and tpl.dest_location_ids and rec.dest_location_id not in tpl.dest_location_ids:
                raise ValidationError(
                    "Template %s serves %s only."
                    % (tpl.name, ", ".join(tpl.dest_location_ids.mapped("code")))
                )
            if tpl and tpl.warehouse_id and tpl.warehouse_id != rec.warehouse_id:
                raise ValidationError("Template %s belongs to another warehouse." % tpl.name)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.wms.outbound.demand", "OBD/New")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open() and self.filtered(lambda r: r.state != "queued"):
            raise UserError("Waved or cancelled demand is final.")
        return super().write(vals)

    def action_cancel(self):
        for rec in self:
            if rec.state != "queued":
                raise UserError(
                    "Only queued demand is cancelled (%s is %s)." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "cancelled"})
        return True

    def action_build_wave(self, skip_short=False):
        """FR-WMS-020: group the queued demand into one draft wave per warehouse
        and template; each line picks from the bins that hold it free (pick faces
        first, then walk order), split across bins when one is not enough. The
        supervisor then releases the wave (BRU-WMS-13).

        skip_short (the automatic release, AUT-WMS-07): demand the bins cannot
        cover stays queued with the reason, and the rest is waved; nothing is
        ever half-waved."""
        queued = self.filtered(lambda r: r.state == "queued")
        if not queued:
            raise UserError("Choose queued demand to wave.")
        Wave = self.env["fix.wms.wave"]
        Line = self.env["fix.wms.wave.line"]
        waves = Wave.browse()
        groups = defaultdict(lambda: self.browse())
        for rec in queued:
            groups[(rec.warehouse_id.id, rec.template_id.id)] |= rec
        for (wh_id, tpl_id), demands in groups.items():
            warehouse = self.env["fix.warehouse"].browse(wh_id)
            if not warehouse.stock_location_id:
                raise UserError("Warehouse %s has no M15 stock location." % warehouse.name)
            planned = defaultdict(float)
            plan = []
            for rec in demands.sorted(
                lambda d: (-_PRIO_RANK[d.priority], d.cutoff_at or datetime.max, d.id)
            ):
                need = rec.qty
                mine = []
                for slot in Line._fix_pick_slots(rec.part_id, warehouse):
                    free = round(
                        (slot.qty or 0.0) - (slot.reserved_qty or 0.0) - planned[slot.id], 4
                    )
                    take = min(free, need)
                    if is_whole_unit(rec.part_id):
                        take = float(int(take + EPS))
                    if take <= EPS:
                        continue
                    planned[slot.id] += take
                    mine.append((rec, slot.bin_id, take, slot.id))
                    need = round(need - take, 4)
                    if need <= EPS:
                        break
                if need > EPS and skip_short:
                    for _rec, _bin, take, slot_id in mine:
                        planned[slot_id] -= take
                    rec._guarded().write(
                        {
                            "short_note": "%s: only %s of %s free in the bins"
                            % (
                                fields.Datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
                                round(rec.qty - need, 4),
                                rec.qty,
                            )
                        }
                    )
                    continue
                plan.extend((r, b, t) for r, b, t, _s in mine)
                if need > EPS:
                    raise UserError(
                        "%s: the bins of %s hold only %s of %s free; %s asks for %s."
                        % (
                            rec.name,
                            warehouse.name,
                            round(rec.qty - need, 4),
                            rec.part_id.part_number,
                            rec.source_ref,
                            rec.qty,
                        )
                    )
            if not plan:
                continue
            demands = self.browse(list(dict.fromkeys(r.id for r, _b, _t in plan)))
            wave_vals = {"warehouse_id": warehouse.id, "company_id": demands[0].company_id.id}
            if tpl_id:
                wave_vals["template_id"] = tpl_id
            cutoffs = [d.cutoff_at for d in demands if d.cutoff_at]
            if cutoffs:
                wave_vals["cutoff_at"] = min(cutoffs)
            wave = Wave.create(wave_vals)
            Line.create(
                [
                    {
                        "wave_id": wave.id,
                        "part_id": rec.part_id.id,
                        "bin_id": bin_record.id,
                        "qty": take,
                        "source_type": rec.source_type,
                        "source_ref": rec.source_ref,
                        "dest_location_id": rec.dest_location_id.id or False,
                        "priority": rec.priority,
                    }
                    for rec, bin_record, take in plan
                ]
            )
            for line, (rec, _bin, _take) in zip(wave.line_ids.sorted("id"), plan, strict=True):
                line._guarded().write({"demand_id": rec.id})
            demands._guarded().write({"state": "waved", "wave_id": wave.id, "short_note": False})
            waves |= wave
        return waves.ids


# ============================================================ counts
class FixWmsFloorCountSpec(models.Model):
    _inherit = "fix.wms.floor.count"

    plan_id = fields.Many2one("fix.wms.count.plan", string="Count Plan", readonly=True, copy=False)
    count_type = fields.Selection(
        [
            ("cycle", "Cycle count"),
            ("zero_cross", "Zero-crossing count"),
            ("count_back", "Count-back after exception"),
            ("full", "Full count"),
        ],
        string="Count Type",
        required=True,
        default="cycle",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"plan_id"}


class FixWmsCountPlan(models.Model):
    """FR-WMS-031: counts are generated by bin, zone or velocity (ABC) class,
    blind (the counter never sees the expected quantity) and executed on the
    floor; each result goes to M15 for approval (BRU-WMS-16)."""

    _name = "fix.wms.count.plan"
    _description = "Floor Count Plan"
    _order = "planned_on desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    warehouse_id = fields.Many2one("fix.warehouse", required=True, ondelete="restrict")
    scope = fields.Selection(
        [
            ("bin", "Chosen bins"),
            ("zone", "A zone"),
            ("velocity", "A velocity (ABC) class"),
            ("warehouse", "Whole warehouse"),
        ],
        required=True,
        default="zone",
    )
    zone_id = fields.Many2one("fix.warehouse.zone", string="Zone", ondelete="restrict")
    bin_ids = fields.Many2many("fix.warehouse.bin", string="Bins")
    velocity = fields.Selection(
        [("fast", "A - Fast movers"), ("medium", "B - Medium"), ("slow", "C - Slow movers")],
        string="Velocity Class",
    )
    count_type = fields.Selection(
        [("cycle", "Cycle count"), ("full", "Full count")], required=True, default="cycle"
    )
    planned_on = fields.Date(required=True, default=fields.Date.context_today)
    assignee_id = fields.Many2one("hr.employee", string="Counter")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("generated", "Counting"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    floor_count_ids = fields.One2many("fix.wms.floor.count", "plan_id", string="Counts")
    counts_total = fields.Integer(compute="_compute_progress", string="Counts")
    counts_open = fields.Integer(compute="_compute_progress", string="Still Open")
    generated_by_id = fields.Many2one("res.users", string="Generated By", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "generated_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "draft":
            locked |= {
                "warehouse_id",
                "scope",
                "zone_id",
                "bin_ids",
                "velocity",
                "count_type",
                "planned_on",
            }
        return locked

    @api.depends("floor_count_ids.state")
    def _compute_progress(self):
        for rec in self:
            counts = rec.floor_count_ids
            rec.counts_total = len(counts)
            rec.counts_open = len(counts.filtered(lambda c: c.state in ("draft", "recount")))

    @api.constrains("scope", "zone_id", "bin_ids", "velocity", "warehouse_id")
    def _check_scope(self):
        for rec in self:
            if rec.scope == "zone" and not rec.zone_id:
                raise ValidationError("A zone count names its zone.")
            if rec.scope == "bin" and not rec.bin_ids:
                raise ValidationError("A bin count names its bins.")
            if rec.scope == "velocity" and not rec.velocity:
                raise ValidationError("A velocity count names its class (A, B or C).")
            if rec.zone_id and rec.zone_id.warehouse_id != rec.warehouse_id:
                raise ValidationError("Zone %s is in another warehouse." % rec.zone_id.name)
            if rec.bin_ids.filtered(lambda b, wh=rec.warehouse_id: _warehouse_of(b) != wh):
                raise ValidationError("Every bin of the plan belongs to its warehouse.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.wms.count.plan", "CNTP/New")
        return super().create(vals_list)

    def write(self, vals):
        if (
            self
            and not self._fix_guard_open()
            and self.filtered(lambda r: r.state != "draft")
            and set(vals) - {"assignee_id"}
        ):
            raise UserError("A generated count plan is final; cancel it and plan again.")
        return super().write(vals)

    def _fix_slots(self):
        self.ensure_one()
        domain = [("bin_id.zone_id.warehouse_id", "=", self.warehouse_id.id)]
        if self.scope == "zone":
            domain.append(("bin_id.zone_id", "=", self.zone_id.id))
        elif self.scope == "bin":
            domain.append(("bin_id", "in", self.bin_ids.ids))
        elif self.scope == "velocity":
            domain.append(("velocity", "=", self.velocity))
        return self.env["fix.wms.slot"].sudo().search(domain)

    def action_generate(self):
        """One blind floor count and one count task per slot in scope; a slot
        already under an open count is skipped (it is being counted)."""
        Count = self.env["fix.wms.floor.count"]
        Task = self.env["fix.wms.task"].sudo()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Generate a draft count plan.")
            made = 0
            for slot in rec._fix_slots():
                if slot.bin_id._fix_is_blocked():
                    continue
                busy = Count.sudo().search_count(
                    [
                        ("bin_id", "=", slot.bin_id.id),
                        ("part_id", "=", slot.part_id.id),
                        ("state", "in", ("draft", "recount", "submitted")),
                    ]
                )
                if busy:
                    continue
                count = Count._guarded().create(
                    {
                        "company_id": rec.company_id.id,
                        "bin_id": slot.bin_id.id,
                        "part_id": slot.part_id.id,
                        "plan_id": rec.id,
                        "count_type": rec.count_type,
                        "counted_on": rec.planned_on,
                    }
                )
                Task.create(
                    {
                        "company_id": rec.company_id.id,
                        "task_type": "count",
                        "ref": "%s %s" % (rec.name, slot.bin_id.name),
                        "part_id": slot.part_id.id,
                        "bin_id": slot.bin_id.id,
                        "qty": 0.0,
                        "floor_count_id": count.id,
                        "assignee_id": rec.assignee_id.id or False,
                    }
                )
                made += 1
            if not made:
                raise UserError(
                    "Nothing to count in %s: no slot in scope, or every one is blocked or "
                    "already under an open count." % rec.name
                )
            rec._guarded().write({"state": "generated", "generated_by_id": self.env.user.id})
        return True

    def action_close(self):
        for rec in self:
            if rec.state != "generated":
                raise UserError("Close a plan that is being counted.")
            if rec.counts_open:
                raise UserError("%d count(s) of %s are still open." % (rec.counts_open, rec.name))
            rec._guarded().write({"state": "closed"})
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "generated"):
                raise UserError("Plan %s is already %s." % (rec.name, rec.state))
            open_counts = rec.floor_count_ids.filtered(lambda c: c.state in ("draft", "recount"))
            open_counts._guarded().write({"state": "cancelled"})
            self.env["fix.wms.task"].sudo().search(
                [("floor_count_id", "in", open_counts.ids), ("state", "in", ("open", "assigned"))]
            )._guarded().write({"state": "cancelled"})
            rec._guarded().write({"state": "cancelled"})
        return True


# ============================================================ labour
class FixWmsTimeStandard(models.Model):
    """FR-WMS-035/040: the time a task of a type should take, per warehouse
    and optionally per zone: per task plus per unit handled."""

    _name = "fix.wms.time.standard"
    _description = "Task Time Standard"
    _order = "warehouse_id, task_type, zone_id"

    warehouse_id = fields.Many2one("fix.warehouse", required=True, ondelete="restrict")
    company_id = fields.Many2one(related="warehouse_id.company_id", store=True, index=True)
    task_type = fields.Selection(TASK_TYPES, string="Task Type", required=True)
    zone_id = fields.Many2one("fix.warehouse.zone", string="Zone (empty: all)", ondelete="restrict")
    seconds_per_task = fields.Integer(string="Seconds per Task", required=True, default=60)
    seconds_per_unit = fields.Integer(string="Seconds per Unit", default=0)
    active = fields.Boolean(default=True)

    _standard_unique = models.Constraint(
        "UNIQUE (warehouse_id, task_type, zone_id)", "One standard per task type and zone"
    )

    @api.constrains("seconds_per_task", "seconds_per_unit", "zone_id", "warehouse_id")
    def _check_standard(self):
        for rec in self:
            if rec.seconds_per_task <= 0 or rec.seconds_per_unit < 0:
                raise ValidationError("A time standard is a positive number of seconds.")
            if rec.zone_id and rec.zone_id.warehouse_id != rec.warehouse_id:
                raise ValidationError("Zone %s is in another warehouse." % rec.zone_id.name)

    @api.model_create_multi
    def create(self, vals_list):
        _require_floor_admin(self.env, "set a time standard")
        return super().create(vals_list)

    def write(self, vals):
        _require_floor_admin(self.env, "change a time standard")
        return super().write(vals)


class FixWmsTaskLabour(models.Model):
    _inherit = "fix.wms.task"

    pick_sequence = fields.Integer(string="Walk Order", readonly=True, copy=False)
    claimed_at = fields.Datetime(string="Started (claimed / assigned)", readonly=True, copy=False)
    time_standard_sec = fields.Integer(string="Standard Time (s)", compute="_compute_time_standard")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"pick_sequence", "claimed_at"}

    @api.depends("task_type", "qty", "bin_id")
    def _compute_time_standard(self):
        Std = self.env["fix.wms.time.standard"].sudo()
        for rec in self:
            seconds = 0
            if rec.bin_id:
                wh = _warehouse_of(rec.bin_id)
                std = Std.search(
                    [
                        ("warehouse_id", "=", wh.id),
                        ("task_type", "=", rec.task_type),
                        ("zone_id", "in", [rec.bin_id.zone_id.id, False]),
                    ]
                ).sorted(lambda s: not s.zone_id)[:1]
                if std:
                    seconds = int(std.seconds_per_task + std.seconds_per_unit * (rec.qty or 0.0))
            rec.time_standard_sec = seconds

    def _fix_stamp_start(self):
        self.filtered(lambda t: t.state == "assigned" and not t.claimed_at)._guarded().write(
            {"claimed_at": fields.Datetime.now()}
        )

    def action_assign(self):
        res = super().action_assign()
        self._fix_stamp_start()
        return res

    def action_claim(self):
        res = super().action_claim()
        self._fix_stamp_start()
        return res


class FixWmsProductivityRun(models.Model):
    """FR-WMS-040 / AUT-WMS-15: tasks and units per operative, actual against
    standard time and pick accuracy, measured from the tasks the system
    recorded as done (never typed)."""

    _name = "fix.wms.productivity.run"
    _description = "Labour Productivity Run"
    _order = "date_to desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    warehouse_id = fields.Many2one("fix.warehouse", required=True, ondelete="restrict")
    date_from = fields.Date(required=True, default=fields.Date.context_today)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Measured")], required=True, default="draft"
    )
    line_ids = fields.One2many("fix.wms.productivity", "run_id", string="Productivity")
    computed_by_id = fields.Many2one("res.users", string="Measured By", readonly=True, copy=False)
    computed_at = fields.Datetime(string="Measured On", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "computed_by_id", "computed_at"}

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError("The period ends after it starts.")
            if (rec.date_to - rec.date_from).days > 92:
                raise ValidationError("Measure at most one quarter at a time.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.wms.productivity.run", "PROD/New")
        return super().create(vals_list)

    def action_compute(self):
        if not self.env.su:
            require_supervisor(self.env, "measure labour productivity")
        Task = self.env["fix.wms.task"].sudo()
        Prod = self.env["fix.wms.productivity"].sudo()
        for rec in self:
            start = datetime.combine(rec.date_from, time.min) - timedelta(hours=6)
            end = datetime.combine(rec.date_to + timedelta(days=1), time.min) - timedelta(hours=6)
            tasks = Task.search(
                [
                    ("state", "=", "done"),
                    ("done_at", ">=", start),
                    ("done_at", "<", end),
                    ("done_by_id", "!=", False),
                    ("assignee_id", "!=", False),
                    ("bin_id.zone_id.warehouse_id", "=", rec.warehouse_id.id),
                ]
            )
            buckets = defaultdict(lambda: Task.browse())
            for task in tasks:
                local_day = (task.done_at + timedelta(hours=6)).date()
                buckets[(task.assignee_id.id, local_day, task.task_type)] |= task
            rec.line_ids.sudo().unlink()
            rows = []
            for (emp_id, day, ttype), group in buckets.items():
                actual = sum(
                    (t.done_at - t.claimed_at).total_seconds()
                    for t in group
                    if t.claimed_at and t.done_at >= t.claimed_at
                )
                standard = sum(group.mapped("time_standard_sec"))
                accuracy = 0.0
                if ttype == "pick":
                    lines = group.mapped("wave_line_id")
                    if lines:
                        exact = lines.filtered(
                            lambda ln: ln.state == "picked"
                            and not ln.resourced_from_id
                            and abs((ln.picked_qty or 0.0) - (ln.qty or 0.0)) <= EPS
                        )
                        accuracy = round(100.0 * len(exact) / len(lines), 2)
                rows.append(
                    {
                        "run_id": rec.id,
                        "operative_id": emp_id,
                        "date": day,
                        "task_type": ttype,
                        "tasks_completed": len(group),
                        "units": round(sum(group.mapped("qty")), 3),
                        "actual_seconds": int(actual),
                        "standard_seconds": int(standard),
                        "efficiency_pct": round(100.0 * standard / actual, 1)
                        if actual and standard
                        else 0.0,
                        "accuracy_pct": accuracy,
                    }
                )
            Prod.create(rows)
            rec._guarded().write(
                {
                    "state": "done",
                    "computed_by_id": self.env.user.id,
                    "computed_at": fields.Datetime.now(),
                }
            )
            for row in rows:
                publish(
                    self.env,
                    "wh.productivity_recorded",
                    "fix.wms.productivity.run",
                    rec.id,
                    {k: (str(v) if k == "date" else v) for k, v in row.items() if k != "run_id"},
                )
        return True

    @api.model
    def _cron_nightly(self):
        """AUT-WMS-15: measure yesterday for every warehouse that runs execution."""
        yesterday = fields.Date.context_today(self) - timedelta(days=1)
        for warehouse in self.env["fix.warehouse"].sudo().search([("wms_enabled", "=", True)]):
            run = self.sudo().create(
                {
                    "company_id": warehouse.company_id.id,
                    "warehouse_id": warehouse.id,
                    "date_from": yesterday,
                    "date_to": yesterday,
                }
            )
            run.action_compute()


class FixWmsProductivity(models.Model):
    _name = "fix.wms.productivity"
    _description = "Labour Productivity"
    _order = "date desc, operative_id, task_type"

    run_id = fields.Many2one(
        "fix.wms.productivity.run", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="run_id.company_id", store=True, index=True)
    warehouse_id = fields.Many2one(related="run_id.warehouse_id", store=True)
    operative_id = fields.Many2one("hr.employee", string="Operative", required=True)
    date = fields.Date(required=True)
    task_type = fields.Selection(TASK_TYPES, string="Task Type", required=True)
    tasks_completed = fields.Integer(string="Tasks")
    units = fields.Float(string="Units")
    actual_seconds = fields.Integer(string="Actual (s)")
    standard_seconds = fields.Integer(string="Standard (s)")
    efficiency_pct = fields.Float(string="Efficiency %")
    accuracy_pct = fields.Float(string="Pick Accuracy %")

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("Productivity is measured by a productivity run, never typed.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise AccessError("Productivity is measured, never typed.")
        return super().write(vals)
