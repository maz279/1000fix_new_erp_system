# fix_facility_ops — M47: site leases, statutory licences, utility accounts,
# occupancy/condition inspections, building PM, safety equipment, security
# incidents and site open/close projects. Sites and facility work orders live in
# fix_facility.py.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixSiteLease(models.Model):
    _name = "fix.site.lease"
    _description = "Site Lease"
    _order = "end_date desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    lessor_id = fields.Many2one("res.partner", string="Lessor", required=True)
    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    monthly_rent = fields.Monetary(currency_field="currency_id")
    escalation_pct = fields.Float(string="Escalation %", default=0.0)
    deposit = fields.Monetary(currency_field="currency_id")
    state = fields.Selection(
        [("active", "Active"), ("expired", "Expired"), ("terminated", "Terminated")],
        required=True,
        default="active",
    )
    notes = fields.Char()

    _dates_ordered = models.Constraint(
        "CHECK (end_date >= start_date)", "Lease end cannot precede its start"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.site.lease") or "LEASE/New"
        return super().create(vals_list)


class FixSiteLicence(models.Model):
    _name = "fix.site.licence"
    _description = "Site Statutory Licence"
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    licence_type = fields.Selection(
        [
            ("trade", "Trade Licence"),
            ("fire", "Fire Safety"),
            ("health", "Health / Sanitation"),
            ("environment", "Environment"),
            ("other", "Other"),
        ],
        required=True,
        default="trade",
    )
    number = fields.Char(string="Licence Number")
    issued_on = fields.Date()
    valid_to = fields.Date()
    state = fields.Selection(
        [("valid", "Valid"), ("expired", "Expired"), ("suspended", "Suspended")],
        required=True,
        default="valid",
    )
    is_valid = fields.Boolean(string="Valid Today", compute="_compute_is_valid", store=True)

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
                    self.env["ir.sequence"].next_by_code("fix.site.licence") or "SLIC/New"
                )
        return super().create(vals_list)


class FixSiteUtility(models.Model):
    _name = "fix.site.utility"
    _description = "Site Utility Account"
    _order = "period desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    period = fields.Char(required=True, help="YYYY-MM")
    utility_type = fields.Selection(
        [("power", "Electricity"), ("water", "Water"), ("gas", "Gas"), ("internet", "Internet")],
        required=True,
        default="power",
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    usage = fields.Float(string="Usage")
    unit = fields.Char(string="Unit", default="kWh")
    flagged = fields.Boolean(string="Anomaly Flagged", default=False)
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.utility") or "SUTL/New"
                )
        return super().create(vals_list)

    def action_flag(self):
        for rec in self:
            rec.flagged = True


class FixSiteCondition(models.Model):
    _name = "fix.site.condition"
    _description = "Site Occupancy & Condition"
    _order = "inspected_on desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    inspected_on = fields.Date(required=True, default=fields.Date.context_today)
    occupancy_pct = fields.Float(string="Occupancy %", default=100.0)
    condition_grade = fields.Selection(
        [("a", "A — Excellent"), ("b", "B — Good"), ("c", "C — Fair"), ("d", "D — Poor")],
        required=True,
        default="b",
    )
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    notes = fields.Text()

    _occupancy_range = models.Constraint(
        "CHECK (occupancy_pct >= 0 AND occupancy_pct <= 100)",
        "Occupancy is a 0–100 percentage",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.condition") or "SCND/New"
                )
        return super().create(vals_list)


class FixSitePm(models.Model):
    _name = "fix.site.pm"
    _description = "Building Services PM"
    _order = "scheduled_on desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    service_type = fields.Selection(
        [
            ("hvac", "HVAC"),
            ("lift", "Lift / Elevator"),
            ("fire", "Fire Systems"),
            ("generator", "Generator"),
            ("pest", "Pest Control"),
            ("cleaning", "Deep Cleaning"),
        ],
        required=True,
        default="hvac",
    )
    provider_id = fields.Many2one("res.partner", string="Service Provider")
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
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.site.pm") or "SPM/New"
        return super().create(vals_list)

    def action_done(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Complete an open PM job")
            rec.write({"state": "done", "done_on": fields.Date.context_today(self)})


class FixSiteSafety(models.Model):
    _name = "fix.site.safety"
    _description = "Site Safety Equipment"
    _order = "next_check"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    equipment_type = fields.Selection(
        [
            ("extinguisher", "Fire Extinguisher"),
            ("alarm", "Fire Alarm"),
            ("cctv", "CCTV"),
            ("first_aid", "First Aid Kit"),
            ("other", "Other"),
        ],
        required=True,
        default="extinguisher",
    )
    ref = fields.Char(string="Tag / Reference")
    last_check = fields.Date()
    next_check = fields.Date(required=True)
    state = fields.Selection(
        [("ok", "OK"), ("due", "Due"), ("overdue", "Overdue")],
        required=True,
        default="ok",
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.site.safety") or "SSAF/New"
        return super().create(vals_list)

    def action_check(self):
        for rec in self:
            rec.write({"last_check": fields.Date.context_today(self), "state": "ok"})


class FixSiteIncident(models.Model):
    _name = "fix.site.incident"
    _description = "Site Security Incident"
    _order = "occurred_on desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    incident_type = fields.Selection(
        [
            ("theft", "Theft / Burglary"),
            ("trespass", "Trespass"),
            ("injury", "Injury"),
            ("fire", "Fire"),
            ("other", "Other"),
        ],
        required=True,
        default="theft",
    )
    occurred_on = fields.Date(required=True, default=fields.Date.context_today)
    description = fields.Text(required=True)
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")], required=True, default="open"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.incident") or "SINC/New"
                )
        return super().create(vals_list)

    def action_close(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Close an open incident")
            rec.state = "closed"


class FixSiteProject(models.Model):
    _name = "fix.site.project"
    _description = "Site Open / Close Project"
    _order = "planned_on desc, id desc"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    project_type = fields.Selection(
        [("open", "Site Opening"), ("close", "Site Closure"), ("relocate", "Relocation")],
        required=True,
        default="open",
    )
    planned_on = fields.Date(required=True, default=fields.Date.context_today)
    done_on = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    budget = fields.Monetary(currency_field="currency_id")
    state = fields.Selection(
        [("planned", "Planned"), ("in_progress", "In Progress"), ("done", "Done")],
        required=True,
        default="planned",
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.site.project") or "SPRJ/New"
                )
        return super().create(vals_list)

    def action_start(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError("Start a planned project")
            rec.state = "in_progress"

    def action_done(self):
        for rec in self:
            if rec.state != "in_progress":
                raise UserError("Complete an in-progress project")
            rec.write({"state": "done", "done_on": fields.Date.context_today(self)})


class FixSiteAsset(models.Model):
    """Building plant at a site: the register behind M47 Branch Asset Register."""

    _name = "fix.site.asset"
    _description = "Site Infrastructure Asset"
    _order = "site_id, asset_type, name"

    name = fields.Char(required=True, default="New")
    site_id = fields.Many2one(
        "fix.site", string="Site", required=True, ondelete="cascade", index=True
    )
    asset_type = fields.Selection(
        [
            ("hvac", "HVAC Plant"),
            ("lift", "Lift / Elevator"),
            ("generator", "Generator"),
            ("fire_pump", "Fire Pump"),
            ("ups", "UPS"),
            ("cctv", "CCTV System"),
            ("electrical", "Electrical Distribution"),
            ("other", "Other"),
        ],
        required=True,
        default="hvac",
    )
    tag = fields.Char(string="Asset Tag")
    serial_no = fields.Char(string="Serial No")
    installed_on = fields.Date()
    warranty_end = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    value = fields.Monetary(currency_field="currency_id")
    state = fields.Selection(
        [
            ("operational", "Operational"),
            ("maintenance", "Under Maintenance"),
            ("retired", "Retired"),
        ],
        required=True,
        default="operational",
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.site.asset") or "SASET/New"
        return super().create(vals_list)

    def action_maintenance(self):
        for rec in self:
            if rec.state != "operational":
                raise UserError("Take an operational asset into maintenance")
            rec.state = "maintenance"

    def action_restore(self):
        for rec in self:
            if rec.state != "maintenance":
                raise UserError("Restore an asset that is under maintenance")
            rec.state = "operational"

    def action_retire(self):
        for rec in self:
            rec.state = "retired"
