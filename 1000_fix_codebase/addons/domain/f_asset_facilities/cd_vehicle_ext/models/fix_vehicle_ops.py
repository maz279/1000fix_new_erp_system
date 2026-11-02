# fix_vehicle_ops — M46: drivers, statutory documents, off-road records, daily
# pre-use checks, PM by odometer, fuel transactions, telematics snapshots and
# accidents. The vehicle register (fleet.vehicle extension) and dispatch
# assignments live in fix_vehicle.py.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixDriver(models.Model):
    _name = "fix.driver"
    _description = "Fleet Driver"
    _order = "name"

    name = fields.Char(required=True)
    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, ondelete="restrict", index=True
    )
    license_no = fields.Char(string="Driving Licence No", required=True)
    license_class = fields.Char(string="Licence Class")
    license_expiry = fields.Date(string="Licence Expiry")
    phone = fields.Char()
    state = fields.Selection(
        [("active", "Active"), ("suspended", "Suspended")], required=True, default="active"
    )

    _employee_unique = models.Constraint("UNIQUE (employee_id)", "One driver record per employee")

    def action_suspend(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Suspend an active driver")
            rec.state = "suspended"


class FixVehicleDocument(models.Model):
    _name = "fix.vehicle.document"
    _description = "Vehicle Statutory Document"
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    doc_type = fields.Selection(
        [
            ("fitness", "Fitness Certificate"),
            ("insurance", "Insurance"),
            ("tax", "Token Tax"),
            ("route_permit", "Route Permit"),
            ("other", "Other"),
        ],
        required=True,
        default="fitness",
    )
    number = fields.Char(string="Document Number")
    valid_from = fields.Date()
    valid_to = fields.Date()
    state = fields.Selection(
        [("valid", "Valid"), ("expired", "Expired")], required=True, default="valid"
    )
    is_valid = fields.Boolean(compute="_compute_is_valid", store=True)

    @api.depends("state", "valid_to")
    def _compute_is_valid(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_valid = bool(
                rec.state == "valid" and (not rec.valid_to or rec.valid_to >= today)
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.document") or "VDOC/New"
                )
        return super().create(vals_list)


class FixVehicleOffroad(models.Model):
    _name = "fix.vehicle.offroad"
    _description = "Vehicle Off-Road Record"
    _order = "started_on desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    reason = fields.Char(required=True)
    started_on = fields.Date(required=True, default=fields.Date.context_today)
    ended_on = fields.Date()
    state = fields.Selection(
        [("offroad", "Off Road"), ("returned", "Returned to Service")],
        required=True,
        default="offroad",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.offroad") or "VOFF/New"
                )
        return super().create(vals_list)

    def action_return(self):
        for rec in self:
            if rec.state != "offroad":
                raise UserError("Return an off-road vehicle")
            rec.write({"state": "returned", "ended_on": fields.Date.context_today(self)})


class FixVehicleCheck(models.Model):
    _name = "fix.vehicle.check"
    _description = "Vehicle Daily Pre-Use Check"
    _order = "checked_on desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    driver_id = fields.Many2one("fix.driver", string="Driver", ondelete="set null")
    checked_on = fields.Date(required=True, default=fields.Date.context_today)
    odometer = fields.Integer(string="Odometer (km)")
    tyres_ok = fields.Boolean(string="Tyres OK", default=True)
    lights_ok = fields.Boolean(string="Lights OK", default=True)
    fluids_ok = fields.Boolean(string="Fluids OK", default=True)
    brakes_ok = fields.Boolean(string="Brakes OK", default=True)
    defects = fields.Text()
    passed = fields.Boolean(string="Passed", compute="_compute_passed", store=True)

    @api.depends("tyres_ok", "lights_ok", "fluids_ok", "brakes_ok")
    def _compute_passed(self):
        for rec in self:
            rec.passed = all([rec.tyres_ok, rec.lights_ok, rec.fluids_ok, rec.brakes_ok])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.check") or "VCHK/New"
                )
        return super().create(vals_list)


class FixVehiclePm(models.Model):
    _name = "fix.vehicle.pm"
    _description = "Vehicle PM by Odometer"
    _order = "scheduled_on desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    pm_type = fields.Selection(
        [("service", "Scheduled Service"), ("repair", "Repair"), ("tyres", "Tyres")],
        required=True,
        default="service",
    )
    odometer = fields.Integer(string="Odometer at Service (km)")
    due_odometer = fields.Integer(string="Due Odometer (km)")
    scheduled_on = fields.Date(required=True, default=fields.Date.context_today)
    done_on = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    cost = fields.Monetary(currency_field="currency_id")
    state = fields.Selection([("open", "Open"), ("done", "Done")], required=True, default="open")
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.vehicle.pm") or "VPM/New"
        return super().create(vals_list)

    def action_done(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Complete an open PM job")
            rec.write({"state": "done", "done_on": fields.Date.context_today(self)})


class FixVehicleFuel(models.Model):
    _name = "fix.vehicle.fuel"
    _description = "Vehicle Fuel Transaction"
    _order = "filled_on desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    driver_id = fields.Many2one("fix.driver", string="Driver", ondelete="set null")
    filled_on = fields.Date(required=True, default=fields.Date.context_today)
    litres = fields.Float(string="Litres", required=True)
    odometer = fields.Integer(string="Odometer (km)", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Amount", currency_field="currency_id")
    station = fields.Char()

    _litres_positive = models.Constraint("CHECK (litres > 0)", "Fuel litres must be positive")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.fuel") or "VFUEL/New"
                )
        return super().create(vals_list)


class FixVehicleTelemetry(models.Model):
    _name = "fix.vehicle.telemetry"
    _description = "Vehicle Telemetry Snapshot"
    _order = "last_ping desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    device_ref = fields.Char(string="Telematics Device")
    last_ping = fields.Datetime(string="Last Ping")
    odometer = fields.Integer(string="Odometer (km)")
    fuel_level_pct = fields.Integer(string="Fuel Level %", default=100)
    state = fields.Selection(
        [("online", "Online"), ("stale", "Stale"), ("offline", "Offline")],
        required=True,
        default="online",
    )

    _fuel_range = models.Constraint(
        "CHECK (fuel_level_pct >= 0 AND fuel_level_pct <= 100)",
        "Fuel level is a 0–100 percentage",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.telemetry") or "VTEL/New"
                )
        return super().create(vals_list)


class FixVehicleAccident(models.Model):
    _name = "fix.vehicle.accident"
    _description = "Vehicle Accident / Incident"
    _order = "occurred_on desc, id desc"

    name = fields.Char(required=True, default="New")
    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Vehicle", required=True, ondelete="cascade", index=True
    )
    driver_id = fields.Many2one("fix.driver", string="Driver", ondelete="set null")
    occurred_on = fields.Date(required=True, default=fields.Date.context_today)
    description = fields.Text(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    damage_cost = fields.Monetary(currency_field="currency_id")
    claim_ref = fields.Char(string="Insurance Claim Ref")
    state = fields.Selection(
        [("reported", "Reported"), ("claimed", "Claim Filed"), ("closed", "Closed")],
        required=True,
        default="reported",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vehicle.accident") or "VACC/New"
                )
        return super().create(vals_list)

    def action_claim(self):
        for rec in self:
            if rec.state != "reported":
                raise UserError("File a claim for a reported accident")
            rec.state = "claimed"

    def action_close(self):
        for rec in self:
            if rec.state != "claimed":
                raise UserError("Close a claimed accident")
            rec.state = "closed"
