# fix_device_ops — M17: corporate estates, PM plans, condition grading, identity
# resolution, custody events and installed components. The device master,
# warranties, ownership transfers and history live beside this file.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixDeviceEstate(models.Model):
    _name = "fix.device.estate"
    _description = "Corporate Estate"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    client_id = fields.Many2one("res.partner", string="Client", required=True, index=True)
    site = fields.Char(string="Site")
    department = fields.Char()
    cost_centre = fields.Char()
    manager_id = fields.Many2one("hr.employee", string="Estate Manager")
    active = fields.Boolean(default=True)
    notes = fields.Text()


class FixDeviceExtend(models.Model):
    _inherit = "fix.device"

    estate_id = fields.Many2one(
        "fix.device.estate", string="Corporate Estate", ondelete="set null", index=True
    )


class FixDevicePm(models.Model):
    _name = "fix.device.pm"
    _description = "Device PM Plan"
    _order = "next_due"

    name = fields.Char(required=True, default="New")
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    plan_type = fields.Selection(
        [("quarterly", "Quarterly"), ("biannual", "Bi-annual"), ("annual", "Annual")],
        required=True,
        default="annual",
    )
    interval_months = fields.Integer(string="Interval (months)", default=12)
    last_done = fields.Date(string="Last Done")
    next_due = fields.Date(required=True)
    state = fields.Selection(
        [("active", "Active"), ("paused", "Paused")], required=True, default="active"
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.device.pm") or "DPM/New"
        return super().create(vals_list)

    def action_complete(self):
        for rec in self:
            rec.write({"last_done": fields.Date.context_today(self), "state": "active"})


class FixDeviceCondition(models.Model):
    _name = "fix.device.condition"
    _description = "Device Condition Grade"
    _order = "graded_on desc, id desc"

    name = fields.Char(required=True, default="New")
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    grade = fields.Selection(
        [("a", "A — Like new"), ("b", "B — Good"), ("c", "C — Fair"), ("d", "D — Poor")],
        required=True,
        default="b",
    )
    cosmetic_notes = fields.Char()
    functional_ok = fields.Boolean(default=True)
    battery_health_pct = fields.Integer(string="Battery Health %", default=100)
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    graded_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")], required=True, default="draft"
    )
    notes = fields.Text()

    _battery_range = models.Constraint(
        "CHECK (battery_health_pct >= 0 AND battery_health_pct <= 100)",
        "Battery health is a 0–100 percentage",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.device.condition") or "DCON/New"
                )
        return super().create(vals_list)

    def action_confirm(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Confirm a draft condition record")
            rec.state = "confirmed"


class FixDeviceIdentity(models.Model):
    _name = "fix.device.identity"
    _description = "Device Identity Resolution"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    primary_device_id = fields.Many2one(
        "fix.device", string="Surviving Device", required=True, ondelete="cascade", index=True
    )
    duplicate_device_id = fields.Many2one(
        "fix.device", string="Duplicate Device", required=True, ondelete="cascade", index=True
    )
    match_reason = fields.Char(required=True)
    match_score = fields.Float(string="Match Score %", default=100.0)
    state = fields.Selection(
        [("candidate", "Candidate"), ("merged", "Merged"), ("rejected", "Rejected")],
        required=True,
        default="candidate",
    )
    resolved_on = fields.Date()
    notes = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.device.identity") or "DIDR/New"
                )
        return super().create(vals_list)

    def action_merge(self):
        for rec in self:
            if rec.primary_device_id == rec.duplicate_device_id:
                raise UserError("A device cannot be merged into itself")
            if rec.state != "candidate":
                raise UserError("Only a candidate resolution can be merged")
            rec.duplicate_device_id.write({"active": False})
            rec.write({"state": "merged", "resolved_on": fields.Date.context_today(self)})

    def action_reject(self):
        for rec in self:
            rec.write({"state": "rejected", "resolved_on": fields.Date.context_today(self)})


class FixDeviceCustody(models.Model):
    _name = "fix.device.custody"
    _description = "Device Custody Event"
    _order = "event_date desc, id desc"

    name = fields.Char(required=True, default="New")
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    event = fields.Selection(
        [
            ("issued", "Issued to Customer"),
            ("returned", "Returned to 1000FiX"),
            ("transferred", "Transferred"),
            ("lost", "Reported Lost"),
            ("found", "Recovered"),
        ],
        required=True,
        default="issued",
    )
    from_party_id = fields.Many2one("res.partner", string="From")
    to_party_id = fields.Many2one("res.partner", string="To")
    custodian_id = fields.Many2one("hr.employee", string="Custodian")
    event_date = fields.Date(required=True, default=fields.Date.context_today)
    reference = fields.Char()
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.device.custody") or "DCUS/New"
                )
        return super().create(vals_list)


class FixDeviceComponent(models.Model):
    _name = "fix.device.component"
    _description = "Installed Device Component"
    _order = "installed_on desc, id desc"

    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    part_name = fields.Char(string="Part / Component", required=True)
    serial_no = fields.Char(string="Component Serial")
    installed_on = fields.Date(required=True, default=fields.Date.context_today)
    removed_on = fields.Date()
    source_ref = fields.Char(string="Source Order / PO")
    state = fields.Selection(
        [("installed", "Installed"), ("removed", "Removed")], required=True, default="installed"
    )
    notes = fields.Char()

    def action_remove(self):
        for rec in self:
            if rec.state != "installed":
                raise UserError("Remove an installed component")
            rec.write({"state": "removed", "removed_on": fields.Date.context_today(self)})
