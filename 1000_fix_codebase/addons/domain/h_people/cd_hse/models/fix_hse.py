# fix_hse — M59: HSE incidents + Labour Rules safety (P09-M08).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixHseIncident(models.Model):
    """M59: Workplace incident and near-miss tracking with automated event publication."""

    _name = "fix.hse.incident"
    _description = "HSE Incident"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    incident_type = fields.Selection(
        [
            ("injury", "Injury / First Aid"),
            ("near_miss", "Near Miss"),
            ("property_damage", "Property Damage"),
            ("fire", "Fire Outbreak"),
            ("battery_thermal", "Battery Thermal Runaway"),
            ("chemical_exposure", "Chemical / Fume Exposure"),
            ("environmental", "Environmental Spill"),
        ],
        required=True,
        default="near_miss",
    )
    severity = fields.Selection(
        [
            ("low", "Low (Minor / First Aid)"),
            ("medium", "Medium (Medical Treatment / Lost Time)"),
            ("high", "High (Critical / Hospitalization / DIFE Reportable)"),
        ],
        default="low",
        required=True,
        tracking=True,
    )
    branch_id = fields.Many2one("fix.branch", string="Branch")
    employee_id = fields.Many2one("hr.employee", string="Reported By")
    injured_employee_id = fields.Many2one("hr.employee", string="Injured Person")
    description = fields.Text(required=True)
    corrective_action = fields.Text()
    statutory_record_id = fields.Many2one(
        "fix.statutory.accident.register", string="Statutory Accident Record", readonly=True
    )
    state = fields.Selection(
        [
            ("reported", "Reported"),
            ("investigating", "Investigating"),
            ("action_taken", "Action Taken"),
            ("closed", "Closed"),
        ],
        default="reported",
        required=True,
        tracking=True,
    )
    reported_at = fields.Datetime(default=fields.Datetime.now, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("fix.hse.incident") or "HSE/New"
        recs = super().create(vals_list)
        for rec in recs:
            publish(
                self.env,
                "hse.incident_reported",
                "fix.hse.incident",
                rec.id,
                {"type": rec.incident_type, "severity": rec.severity},
            )
            # If severe injury, auto-create statutory accident register record
            if rec.incident_type in ("injury", "battery_thermal") and rec.severity in (
                "medium",
                "high",
            ):
                # The Form 33/34 register needs the worker involved (required
                # field): refuse with a named error instead of a NOT NULL
                # database failure when neither person is recorded.
                if not (rec.injured_employee_id or rec.employee_id):
                    raise UserError(
                        "A %s-severity %s must name the injured worker or the reporter: "
                        "the BLA s.89 accident register records the worker involved."
                        % (rec.severity, rec.incident_type)
                    )
                reg = self.env["fix.statutory.accident.register"].create(
                    {
                        "name": f"BLA-Accident: {rec.name}",
                        "incident_id": rec.id,
                        "employee_id": rec.injured_employee_id.id
                        if rec.injured_employee_id
                        else rec.employee_id.id,
                        "company_id": rec.company_id.id,
                        "operating_unit_id": rec.operating_unit_id.id
                        if rec.operating_unit_id
                        else False,
                        "accident_date": fields.Date.today(),
                        "nature_of_injury": rec.description,
                    }
                )
                rec.statutory_record_id = reg.id
        return recs

    def action_investigate(self):
        for rec in self:
            rec.state = "investigating"

    def action_close(self):
        for rec in self:
            rec.state = "closed"


class FixSafetyInspection(models.Model):
    """M59: Branch and cleanroom safety compliance inspections."""

    _name = "fix.safety.inspection"
    _description = "Safety Inspection"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "inspected_on desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True)
    inspected_on = fields.Date(required=True, default=fields.Date.today)
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    fire_extinguisher_ok = fields.Boolean(
        default=True, string="Fire Extinguisher Inspected & Valid"
    )
    emergency_exit_ok = fields.Boolean(default=True, string="Emergency Exits Unobstructed")
    first_aid_ok = fields.Boolean(default=True, string="First Aid Box Stocked (BLR Rule 67)")
    electrical_ok = fields.Boolean(default=True, string="Electrical Wiring & Grounding Safe")
    esd_grounding_ok = fields.Boolean(
        default=True, string="ESD Benches & Mats Grounded (ANSI/ESD S20.20)"
    )
    fume_extraction_ok = fields.Boolean(default=True, string="Soldering Fume Extractor Operational")
    chemical_storage_ok = fields.Boolean(
        default=True, string="IPA & Solvents Stored in Flammable Cabinet"
    )
    findings = fields.Text()
    state = fields.Selection(
        [("scheduled", "Scheduled"), ("done", "Done"), ("follow_up", "Follow-up Required")],
        default="scheduled",
        required=True,
        tracking=True,
    )

    def action_complete(self):
        for rec in self:
            needs = not all(
                [
                    rec.fire_extinguisher_ok,
                    rec.emergency_exit_ok,
                    rec.first_aid_ok,
                    rec.electrical_ok,
                    rec.esd_grounding_ok,
                    rec.fume_extraction_ok,
                    rec.chemical_storage_ok,
                ]
            )
            rec.state = "follow_up" if needs else "done"


class FixSafetyCommittee(models.Model):
    """M59: Statutory Safety Committee established under Bangladesh Labour Act 2006 §90A
    and Bangladesh Labour Rules 2015 Rule 81."""

    _name = "fix.safety.committee"
    _description = "Statutory Safety Committee"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Committee Designation", required=True)
    branch_id = fields.Many2one("fix.branch", string="Service Centre / Branch", required=True)
    formation_date = fields.Date(string="Formation Date", default=fields.Date.today, required=True)
    chairperson_id = fields.Many2one(
        "hr.employee", string="Chairperson (Employer Rep)", required=True
    )
    secretary_id = fields.Many2one("hr.employee", string="Secretary (Worker Rep)", required=True)
    member_count = fields.Integer(string="Total Committee Members", default=6, required=True)
    meeting_frequency = fields.Selection(
        [("monthly", "Monthly"), ("bimonthly", "Every 2 Months"), ("quarterly", "Quarterly")],
        default="monthly",
        required=True,
    )
    last_meeting_date = fields.Date(string="Last Meeting Conducted")
    next_meeting_date = fields.Date(string="Next Scheduled Meeting")
    recent_minutes = fields.Text(string="Minutes of Latest Meeting")
    dife_registered = fields.Boolean(
        string="DIFE Registered",
        default=True,
        help="Committee constitution notified to DIFE Joint Inspector General",
    )
    state = fields.Selection(
        [
            ("active", "Active & Compliant"),
            ("review_needed", "Reconstitution Needed"),
            ("dissolved", "Dissolved"),
        ],
        default="active",
        required=True,
        tracking=True,
    )

    def action_record_meeting(self, minutes_text=""):
        for rec in self:
            rec.last_meeting_date = fields.Date.today()
            if minutes_text:
                rec.recent_minutes = minutes_text
            publish(
                self.env,
                "hse.safety_committee_meeting",
                "fix.safety.committee",
                rec.id,
                {"committee": rec.name, "branch": rec.branch_id.name if rec.branch_id else ""},
            )


class FixStatutoryAccidentRegister(models.Model):
    """M59: Mandatory Accident and Dangerous Occurrence Register under
    Bangladesh Labour Act 2006 §89 & Bangladesh Labour Rules 2015 Rule 80 (Form 33/34)."""

    _name = "fix.statutory.accident.register"
    _description = "Statutory Accident Register (BLA Form 33/34)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "accident_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Statutory Record ID", required=True)
    incident_id = fields.Many2one("fix.hse.incident", string="Linked HSE Incident")
    employee_id = fields.Many2one("hr.employee", string="Worker Involved", required=True)
    accident_date = fields.Date(string="Date of Accident", default=fields.Date.today, required=True)
    nature_of_injury = fields.Text(string="Nature and Cause of Injury", required=True)
    affected_body_part = fields.Char(string="Affected Body Part (e.g. Eye, Hand, Respiratory)")
    lost_work_days = fields.Integer(string="Lost Work Days", default=0)
    dife_notified = fields.Boolean(
        string="DIFE Form 34 Notice Dispatched",
        default=False,
        tracking=True,
        help="Notice to DIFE within 48 hours for reportable injuries under BLR 2015 Rule 80",
    )
    dife_notification_date = fields.Date(string="DIFE Notice Date")
    statutory_compensation_bdt = fields.Float(
        string="Statutory Workers Compensation (BDT)",
        help="Compensation assessed under BLA 2006 Chapter XII (Injury & Disability Schedule)",
    )
    state = fields.Selection(
        [
            ("recorded", "Recorded"),
            ("dife_notified", "DIFE Notified"),
            ("compensation_settled", "Compensation Settled"),
            ("closed", "Closed"),
        ],
        default="recorded",
        required=True,
        tracking=True,
    )

    def action_notify_dife(self):
        for rec in self:
            rec.dife_notified = True
            rec.dife_notification_date = fields.Date.today()
            rec.state = "dife_notified"
            publish(
                self.env,
                "hse.dife_accident_reported",
                "fix.statutory.accident.register",
                rec.id,
                {"worker": rec.employee_id.name, "date": str(rec.accident_date)},
            )


class FixPpeRegister(models.Model):
    """M59: Personal Protective Equipment standard register for workshop technicians."""

    _name = "fix.ppe.register"
    _description = "PPE Safety Equipment Register"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="PPE Item Name", required=True)
    item_type = fields.Selection(
        [
            ("esd_wristband", "Anti-Static / ESD Wristband"),
            ("goggles", "Impact & Chemical Safety Goggles"),
            ("fume_mask", "Soldering Fume Respirator / Activated Carbon Mask"),
            ("thermal_gloves", "Heat-Resistant SMD/BGA Rework Gloves"),
            ("lab_coat", "Anti-Static Workshop Lab Coat"),
            ("first_aid_kit", "First Aid Emergency Kit"),
        ],
        required=True,
        default="esd_wristband",
    )
    regulatory_standard = fields.Char(
        string="Applicable Standard", default="ANSI/ESD S20.20 / OSHA 1910.133"
    )
    stock_quantity = fields.Integer(string="Available In Stock", default=50)
    min_required_quantity = fields.Integer(string="Minimum Threshold", default=10)
    state = fields.Selection(
        [("compliant", "Stock Adequate"), ("replenish", "Replenishment Required")],
        default="compliant",
        required=True,
    )

    def check_replenishment(self):
        for rec in self:
            rec.state = (
                "replenish" if rec.stock_quantity <= rec.min_required_quantity else "compliant"
            )


class FixHazardousSubstanceRegister(models.Model):
    """M59: Hazardous substance, chemical solvent, and battery management register."""

    _name = "fix.hazardous.substance.register"
    _description = "Hazardous Substance Register"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Chemical / Substance Name", required=True)
    un_number = fields.Char(string="UN Transport Number (e.g. UN 1219 for IPA, UN 3481 for Li-Ion)")
    storage_location = fields.Char(string="Approved Storage Location", required=True)
    max_allowable_litres = fields.Float(string="Max Permissible Storage Limit", default=50.0)
    current_stock_litres = fields.Float(string="Current Stock On-Hand", default=15.0)
    msds_on_file = fields.Boolean(string="Safety Data Sheet (MSDS) Available", default=True)
    fire_suppression_type = fields.Char(
        string="Required Fire Extinguisher", default="Class B CO2 / Dry Chemical"
    )
    state = fields.Selection(
        [
            ("safe", "Normal / Safe"),
            ("threshold_exceeded", "Limit Exceeded"),
            ("quarantined", "Quarantined / Defective"),
        ],
        default="safe",
        required=True,
    )
