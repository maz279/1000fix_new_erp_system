# fix_wms_ops — M41: the warehouse execution documents behind the 12 registry
# screens. Structure (warehouse/zone/bin) lives in cd_wms_structure; these
# compose with bin-level slotting and the inbound/outbound/floor flows. Stock
# totals stay in M15's ledger: a put-away or a pick moves a BIN slot, never the
# location on-hand (a location-level count is M15's document).
#
# NOTE: these models live in cd_inventory (not cd_wms_structure) because
# cd_inventory already depends on the structure module; adding the reverse
# dependency would create a module cycle. Same layered pattern as the rental SKU
# in cd_catalogue.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixWmsSlot(models.Model):
    """A part's slot: which bin holds it and how it moves."""

    _name = "fix.wms.slot"
    _description = "Bin Slot"
    _order = "bin_id, part_id"

    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="cascade", index=True
    )
    bin_id = fields.Many2one(
        "fix.warehouse.bin", string="Bin", required=True, ondelete="cascade", index=True
    )
    zone_id = fields.Many2one(related="bin_id.zone_id", string="Zone", store=True)
    qty = fields.Float(string="Quantity in Bin")
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
    last_slotted_on = fields.Date()
    state = fields.Selection(
        [("active", "Active"), ("blocked", "Blocked")], required=True, default="active"
    )

    _slot_unique = models.Constraint("UNIQUE (part_id, bin_id)", "One slot per part and bin")
    _qty_non_negative = models.Constraint("CHECK (qty >= 0)", "Slot quantity cannot be negative")


class FixWmsDock(models.Model):
    _name = "fix.wms.dock"
    _description = "Dock Appointment"
    _order = "slot_start desc, id desc"

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
    slot_end = fields.Datetime(required=True, default=fields.Datetime.now)
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.wms.dock") or "DOCK/New"
        return super().create(vals_list)

    def action_check_in(self):
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("Check in a scheduled appointment")
            rec.state = "checked_in"

    def action_complete(self):
        for rec in self:
            if rec.state != "checked_in":
                raise UserError("Complete a checked-in appointment")
            rec.state = "completed"


class FixWmsPutaway(models.Model):
    _name = "fix.wms.putaway"
    _description = "Directed Put-Away"
    _order = "create_date desc, id desc"

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
    from_ref = fields.Char(string="Source Reference")
    assignee_id = fields.Many2one("hr.employee", string="Assigned To")
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done")], required=True, default="pending"
    )
    done_at = fields.Datetime()

    _qty_positive = models.Constraint("CHECK (qty > 0)", "Put-away quantity must be positive")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.wms.putaway") or "PUTA/New"
        return super().create(vals_list)

    def action_complete(self):
        slots = self.env["fix.wms.slot"]
        for rec in self:
            if rec.state != "pending":
                raise UserError("Complete a pending put-away")
            slot = slots.search(
                [("part_id", "=", rec.part_id.id), ("bin_id", "=", rec.to_bin_id.id)], limit=1
            )
            if slot:
                slot.write(
                    {
                        "qty": (slot.qty or 0.0) + rec.qty,
                        "last_slotted_on": fields.Date.context_today(self),
                    }
                )
            else:
                slots.create(
                    {
                        "part_id": rec.part_id.id,
                        "bin_id": rec.to_bin_id.id,
                        "qty": rec.qty,
                        "velocity": "medium",
                        "last_slotted_on": fields.Date.context_today(self),
                    }
                )
            rec.write({"state": "done", "done_at": fields.Datetime.now()})


class FixWmsWave(models.Model):
    _name = "fix.wms.wave"
    _description = "Pick Wave"
    _order = "wave_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
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
    released_at = fields.Datetime()
    shipped_at = fields.Datetime()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.wms.wave") or "WAVE/New"
        return super().create(vals_list)

    def action_release(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Release a draft wave")
            if not rec.line_ids:
                raise UserError("A wave needs at least one line")
            rec.write({"state": "released", "released_at": fields.Datetime.now()})

    def action_pick_all(self):
        slots = self.env["fix.wms.slot"]
        for rec in self:
            if rec.state not in ("released", "picking"):
                raise UserError("Pick a released wave")
            for line in rec.line_ids:
                # a pick can never silently exceed what the bin holds: the line
                # is marked SHORT with the quantity actually picked
                picked = 0.0
                if line.bin_id:
                    slot = slots.search(
                        [("part_id", "=", line.part_id.id), ("bin_id", "=", line.bin_id.id)],
                        limit=1,
                    )
                    if slot:
                        picked = min(line.qty or 0.0, slot.qty or 0.0)
                        slot.qty = max((slot.qty or 0.0) - picked, 0.0)
                line.write(
                    {
                        "picked_qty": picked,
                        "state": "picked" if picked >= (line.qty or 0.0) else "short",
                    }
                )
            rec.state = "picking"

    def action_packed(self):
        for rec in self:
            if rec.state != "picking":
                raise UserError("Pack a picked wave")
            if any(line.state != "picked" for line in rec.line_ids):
                raise UserError("Every line must be picked before packing")
            rec.state = "packed"

    def action_stage(self):
        for rec in self:
            if rec.state != "packed":
                raise UserError("Stage a packed wave")
            rec.state = "staged"

    def action_ship(self):
        for rec in self:
            if rec.state != "staged":
                raise UserError("Ship a staged wave")
            rec.write({"state": "shipped", "shipped_at": fields.Datetime.now()})


class FixWmsWaveLine(models.Model):
    _name = "fix.wms.wave.line"
    _description = "Pick Wave Line"
    _order = "wave_id, id"

    wave_id = fields.Many2one("fix.wms.wave", required=True, ondelete="cascade", index=True)
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    bin_id = fields.Many2one("fix.warehouse.bin", string="Pick Bin", ondelete="set null")
    qty = fields.Float(string="Quantity")
    picked_qty = fields.Float(string="Picked")
    state = fields.Selection(
        [("pending", "Pending"), ("picked", "Picked"), ("short", "Short")],
        required=True,
        default="pending",
    )

    _qty_positive = models.Constraint("CHECK (qty > 0)", "Wave line quantity must be positive")
    _picked_bound = models.Constraint(
        "CHECK (picked_qty >= 0 AND picked_qty <= qty)",
        "Picked quantity must be between 0 and the wave quantity",
    )


class FixWmsCarton(models.Model):
    _name = "fix.wms.carton"
    _description = "Packing Carton"
    _order = "create_date desc, id desc"

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

    _weight_positive = models.Constraint(
        "CHECK (weight_kg >= 0 AND contents_qty >= 0)",
        "Packing weights and counts cannot be negative",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.wms.carton") or "CART/New"
        return super().create(vals_list)

    def action_seal(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Seal an open carton")
            rec.state = "sealed"


class FixWmsStage(models.Model):
    _name = "fix.wms.stage"
    _description = "Staging & Load"
    _order = "create_date desc, id desc"

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.wms.stage") or "STAG/New"
        return super().create(vals_list)

    def action_load(self):
        for rec in self:
            if rec.state != "staging":
                raise UserError("Load a staging record")
            rec.state = "loaded"

    def action_dispatch(self):
        for rec in self:
            if rec.state != "loaded":
                raise UserError("Dispatch a loaded record")
            rec.state = "dispatched"


class FixWmsTask(models.Model):
    _name = "fix.wms.task"
    _description = "Warehouse Task"
    _order = "create_date desc, id desc"

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
    assignee_id = fields.Many2one("hr.employee", string="Assignee")
    state = fields.Selection(
        [("open", "Open"), ("assigned", "Assigned"), ("done", "Done"), ("cancelled", "Cancelled")],
        required=True,
        default="open",
    )
    done_at = fields.Datetime()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.wms.task") or "TASK/New"
        return super().create(vals_list)

    def action_assign(self):
        for rec in self:
            if not rec.assignee_id:
                raise UserError("Assign a task to a warehouse operator")
            rec.state = "assigned"

    def action_done(self):
        for rec in self:
            if rec.state not in ("open", "assigned"):
                raise UserError("Complete an open or assigned task")
            rec.write({"state": "done", "done_at": fields.Datetime.now()})


class FixWmsFloorCount(models.Model):
    """A bin-level floor count; the ledger adjustment stays with M15 counts."""

    _name = "fix.wms.floor.count"
    _description = "Floor Count (Bin)"
    _order = "counted_on desc, id desc"

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
    expected_qty = fields.Float(string="Expected")
    counted_qty = fields.Float(string="Counted")
    variance = fields.Float(compute="_compute_variance", store=True, string="Variance")
    state = fields.Selection(
        [("draft", "Draft"), ("posted", "Posted")], required=True, default="draft"
    )
    counted_on = fields.Date(required=True, default=fields.Date.context_today)

    @api.depends("expected_qty", "counted_qty")
    def _compute_variance(self):
        for rec in self:
            rec.variance = round((rec.counted_qty or 0.0) - (rec.expected_qty or 0.0), 3)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.wms.floor.count") or "FLCT/New"
                )
        return super().create(vals_list)

    def action_post(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Post a draft floor count")
            rec.state = "posted"


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
