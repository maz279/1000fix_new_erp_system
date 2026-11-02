# fix_hse_ops — M59: hazard register, JSA, lone-worker check-ins, road-safety
# checks, drills and occupational health / return-to-work. Incidents,
# inspections, committees, statutory registers and PPE live in fix_hse.py.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixHseHazard(models.Model):
    _name = "fix.hse.hazard"
    _description = "Hazard Register Entry"
    _order = "risk_score desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    hazard_type = fields.Selection(
        [
            ("electrical", "Electrical"),
            ("chemical", "Chemical"),
            ("ergonomic", "Ergonomic"),
            ("slip_trip", "Slip / Trip"),
            ("height", "Work at Height"),
            ("road", "Road / Driving"),
            ("battery", "Battery / Thermal"),
            ("other", "Other"),
        ],
        required=True,
        default="electrical",
    )
    likelihood = fields.Integer(string="Likelihood (1-5)", default=3)
    severity = fields.Integer(string="Severity (1-5)", default=3)
    risk_score = fields.Integer(string="Risk Score", compute="_compute_risk", store=True)
    controls = fields.Text(string="Existing Controls")
    residual_risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        required=True,
        default="medium",
    )
    state = fields.Selection(
        [("open", "Open"), ("controlled", "Controlled"), ("closed", "Closed")],
        required=True,
        default="open",
    )

    _score_range = models.Constraint(
        "CHECK (likelihood >= 1 AND likelihood <= 5 AND severity >= 1 AND severity <= 5)",
        "Likelihood and severity are 1-5",
    )

    @api.depends("likelihood", "severity")
    def _compute_risk(self):
        for rec in self:
            rec.risk_score = (rec.likelihood or 1) * (rec.severity or 1)

    def action_control(self):
        for rec in self:
            rec.state = "controlled"

    def action_close(self):
        for rec in self:
            rec.state = "closed"


class FixHseJsa(models.Model):
    _name = "fix.hse.jsa"
    _description = "Job Safety Analysis"
    _order = "job_type, id"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    job_type = fields.Char(string="Job / Task Type", required=True)
    steps = fields.Text(string="Job Steps")
    hazards = fields.Text(string="Hazards per Step")
    controls = fields.Text(string="Controls per Step")
    ppe_required = fields.Char(string="PPE Required")
    approved_by_id = fields.Many2one("hr.employee", string="Approved By")
    approved_on = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("retired", "Retired")],
        required=True,
        default="draft",
    )

    def action_approve(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft JSA")
            rec.state = "approved"
            rec.approved_on = fields.Date.context_today(self)


class FixHseLoneWorker(models.Model):
    _name = "fix.hse.loneworker"
    _description = "Lone-Worker Check-In"
    _order = "checkin_time desc, id desc"

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    checkin_time = fields.Datetime(required=True, default=fields.Datetime.now)
    expected_end = fields.Datetime(string="Expected End")
    location = fields.Char()
    buddy_id = fields.Many2one("hr.employee", string="Emergency Contact")
    state = fields.Selection(
        [
            ("checked_in", "Checked In"),
            ("checked_out", "Checked Out"),
            ("escalated", "Escalated"),
            ("missed", "Missed Check-Out"),
        ],
        required=True,
        default="checked_in",
    )
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.hse.loneworker") or "LW/New"
                )
        return super().create(vals_list)

    def action_checkout(self):
        for rec in self:
            if rec.state != "checked_in":
                raise UserError("Check out a checked-in lone worker")
            rec.state = "checked_out"

    def action_escalate(self):
        from libs.py.fix_events import publish

        for rec in self:
            rec.state = "escalated"
            publish(
                self.env,
                "hse.loneworker.escalated",
                "fix.hse.loneworker",
                rec.id,
                {
                    "employee": rec.employee_id.name,
                    "location": rec.location or "",
                    "buddy": rec.buddy_id.name if rec.buddy_id else "",
                },
            )


class FixHseRoadCheck(models.Model):
    _name = "fix.hse.roadcheck"
    _description = "Road & Vehicle Safety Check"
    _order = "checked_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", string="Driver")
    vehicle_ref = fields.Char(string="Vehicle / Plate")
    checked_on = fields.Date(required=True, default=fields.Date.context_today)
    tyres_ok = fields.Boolean(string="Tyres OK", default=True)
    brakes_ok = fields.Boolean(string="Brakes OK", default=True)
    lights_ok = fields.Boolean(string="Lights OK", default=True)
    documents_ok = fields.Boolean(string="Fitness / Insurance OK", default=True)
    defects = fields.Char()
    passed = fields.Boolean(string="Passed", compute="_compute_passed", store=True)

    @api.depends("tyres_ok", "brakes_ok", "lights_ok", "documents_ok")
    def _compute_passed(self):
        for rec in self:
            rec.passed = bool(rec.tyres_ok and rec.brakes_ok and rec.lights_ok and rec.documents_ok)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.hse.roadcheck") or "RCK/New"
                )
        return super().create(vals_list)


class FixHseDrill(models.Model):
    _name = "fix.hse.drill"
    _description = "Emergency Drill"
    _order = "scheduled_on desc, id desc"

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    branch_id = fields.Many2one("fix.branch", string="Branch")
    drill_type = fields.Selection(
        [
            ("fire", "Fire Evacuation"),
            ("earthquake", "Earthquake"),
            ("first_aid", "First Aid"),
            ("chemical", "Chemical Spill"),
            ("battery", "Battery Thermal Incident"),
        ],
        required=True,
        default="fire",
    )
    scheduled_on = fields.Date(required=True, default=fields.Date.context_today)
    completed_on = fields.Date()
    participants = fields.Integer()
    duration_min = fields.Integer(string="Duration (minutes)")
    findings = fields.Char()
    state = fields.Selection(
        [("planned", "Planned"), ("completed", "Completed"), ("cancelled", "Cancelled")],
        required=True,
        default="planned",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.hse.drill") or "DRL/New"
        return super().create(vals_list)

    def action_complete(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError("Complete a planned drill")
            rec.state = "completed"
            rec.completed_on = fields.Date.context_today(self)


class FixHseHealth(models.Model):
    _name = "fix.hse.health"
    _description = "Occupational Health / Return-to-Work"
    _order = "record_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    record_type = fields.Selection(
        [
            ("medical", "Periodic Medical"),
            ("return_to_work", "Return to Work"),
            ("restriction", "Work Restriction"),
            ("vaccination", "Vaccination"),
        ],
        required=True,
        default="medical",
    )
    record_date = fields.Date(required=True, default=fields.Date.context_today)
    valid_until = fields.Date()
    fitness = fields.Selection(
        [
            ("fit", "Fit for Duty"),
            ("fit_restricted", "Fit with Restrictions"),
            ("unfit", "Unfit"),
            ("pending", "Pending Review"),
        ],
        required=True,
        default="pending",
    )
    restrictions = fields.Char()
    clinician = fields.Char()
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")], required=True, default="open"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.hse.health") or "OH/New"
        return super().create(vals_list)

    def action_close(self):
        for rec in self:
            rec.state = "closed"
