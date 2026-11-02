# fix_hse — M59: HSE incidents + Labour Rules safety (P09-M08).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


def _add_bd_working_days(start_dt, working_days=2, holiday_dates=()):
    """Advance start_dt by N Bangladesh working days (skipping Fri/Sat and holidays, BLA s.80)."""
    cur = start_dt
    added = 0
    hol_set = set(holiday_dates or ())
    while added < working_days:
        cur = cur + timedelta(days=1)
        if cur.weekday() in (4, 5):  # Friday=4, Saturday=5
            continue
        if cur.date() in hol_set:
            continue
        added += 1
    return cur


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
    accident_datetime = fields.Datetime(string="Accident Date & Time", default=fields.Datetime.now)
    notice_due = fields.Datetime(
        string="DIFE Notice Deadline (2 Working Days, BLA s.80)",
        compute="_compute_notice_due",
        store=True,
    )
    notice_form = fields.Selection(
        [
            ("form_27", "Form 27 - Fatal / Lost-Time Accident Notice (BLR r.70)"),
            ("form_27a", "Form 27(a) - Dangerous Occurrence Notice (BLR r.70)"),
            ("form_27b", "Form 27(b) - Minor Injury Notice (BLR r.70)"),
            ("none", "Not Reportable"),
        ],
        string="Statutory DIFE Notice Form",
        compute="_compute_notice_due",
        store=True,
    )
    immediate_notification_required = fields.Boolean(
        string="Immediate Phone/Fax Notice Required (BLA s.80)",
        compute="_compute_notice_due",
        store=True,
    )
    dife_notice_ref = fields.Char(string="DIFE Form 27/27(a) Dispatch Ref")

    @api.depends("accident_datetime", "reported_at", "incident_type", "severity")
    def _compute_notice_due(self):
        hol_dates = set()
        if "fix.hr.holiday" in self.env:
            hol_dates = set(self.env["fix.hr.holiday"].search([]).mapped("date"))
        for rec in self:
            base_dt = rec.accident_datetime or rec.reported_at or fields.Datetime.now()
            if rec.incident_type in (
                "injury",
                "battery_thermal",
                "fire",
                "chemical_exposure",
            ) and rec.severity in ("medium", "high"):
                rec.notice_due = _add_bd_working_days(base_dt, 2, hol_dates)
                if rec.incident_type == "injury":
                    rec.notice_form = "form_27"
                else:
                    rec.notice_form = "form_27a"
                rec.immediate_notification_required = rec.severity == "high"
            elif rec.incident_type == "injury" and rec.severity == "low":
                rec.notice_due = _add_bd_working_days(base_dt, 2, hol_dates)
                rec.notice_form = "form_27b"
                rec.immediate_notification_required = False
            else:
                rec.notice_due = False
                rec.notice_form = "none"
                rec.immediate_notification_required = False

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
            # If severe injury or dangerous occurrence, auto-create statutory accident register record (BLA s.80/s.90)
            if rec.incident_type in (
                "injury",
                "battery_thermal",
                "fire",
                "chemical_exposure",
            ) and rec.severity in (
                "medium",
                "high",
            ):
                # The Form 28 register needs the worker involved (required
                # field): refuse with a named error instead of a NOT NULL
                # database failure when neither person is recorded.
                if not (rec.injured_employee_id or rec.employee_id):
                    raise UserError(
                        "A %s-severity %s must name the injured worker or the reporter: "
                        "the BLA 2006 s.90 / BLR 2015 r.73 accident register records "
                        "the worker involved." % (rec.severity, rec.incident_type)
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
                        # The statutory register records the date the accident
                        # HAPPENED, not the date it was keyed in: a late-reported
                        # accident was being filed under the wrong date, which
                        # also mis-dated its Form 28 half-yearly return.
                        "accident_date": (
                            fields.Datetime.to_datetime(rec.accident_datetime).date()
                            if rec.accident_datetime
                            else fields.Date.today()
                        ),
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
            # The gate is the existence of a statutory register entry (only a
            # reportable accident opens one) plus an un-dispatched notice. It
            # was previously keyed on `dife_notice_ref == "BLOCK_WITHOUT_DIFE"`,
            # a sentinel no production record ever carries, so every reportable
            # accident could be closed with the DIFE notice still outstanding.
            if rec.statutory_record_id and not rec.statutory_record_id.dife_notified:
                raise UserError(
                    "BLA 2006 s.80 / BLR 2015 r.70: Cannot close a reportable accident "
                    "before the DIFE Form 27/27(a) notice is dispatched. Record the "
                    "dispatch on the incident (Dispatch DIFE Notice) and try again."
                )
            rec.state = "closed"

    def action_dispatch_dife_notice(self, notice_ref="DIFE-FORM27"):
        for rec in self:
            rec.dife_notice_ref = notice_ref
            if rec.statutory_record_id and not rec.statutory_record_id.dife_notified:
                rec.statutory_record_id.action_notify_dife()
                rec.statutory_record_id.dife_ack_ref = notice_ref


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
    # The inspection screen reports how much failed, not just which boxes are
    # unticked: both counts are derived from the checklist so they cannot drift
    # from it. "Critical" is the life-safety subset (BLR r.55/r.57/r.67) —
    # fire, egress, first aid and electrical — which forces a follow-up.
    findings_count = fields.Integer(string="Failed Checks", compute="_compute_findings", store=True)
    critical_findings = fields.Integer(
        string="Critical Failed Checks", compute="_compute_findings", store=True
    )

    _CHECKS = (
        "fire_extinguisher_ok",
        "emergency_exit_ok",
        "first_aid_ok",
        "electrical_ok",
        "esd_grounding_ok",
        "fume_extraction_ok",
        "chemical_storage_ok",
    )
    _CRITICAL_CHECKS = (
        "fire_extinguisher_ok",
        "emergency_exit_ok",
        "first_aid_ok",
        "electrical_ok",
    )

    @api.depends(*_CHECKS)
    def _compute_findings(self):
        for rec in self:
            rec.findings_count = sum(1 for f in rec._CHECKS if not getattr(rec, f))
            rec.critical_findings = sum(1 for f in rec._CRITICAL_CHECKS if not getattr(rec, f))

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
    Bangladesh Labour Act 2006 §80/§89/§90 & Bangladesh Labour Rules 2015 Rule 70 (Forms 27/27a/27b)
    and Rule 73 (Form 28; legacy ref Form 33/34)."""

    _name = "fix.statutory.accident.register"
    _description = "Statutory Accident Register (BLA s.80/s.90 Form 27/28 & Form 33/34)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "accident_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(string="Statutory Record ID", required=True)
    register_entry_no = fields.Char(string="Form 28 Register Serial No", default="New")
    incident_id = fields.Many2one("fix.hse.incident", string="Linked HSE Incident")
    employee_id = fields.Many2one("hr.employee", string="Worker Involved", required=True)
    accident_date = fields.Date(string="Date of Accident", default=fields.Date.today, required=True)
    nature_of_injury = fields.Text(string="Nature and Cause of Injury", required=True)
    affected_body_part = fields.Char(string="Affected Body Part (e.g. Eye, Hand, Respiratory)")
    lost_work_days = fields.Integer(string="Lost Work Days", default=0)
    notice_form_type = fields.Selection(
        [
            ("form_27", "Form 27 - Fatal / Lost-Time Accident (BLR r.70)"),
            ("form_27a", "Form 27(a) - Dangerous Occurrence (BLR r.70)"),
            ("form_27b", "Form 27(b) - Minor Injury Notice (BLR r.70)"),
        ],
        string="Notice Form Type (BLR r.70)",
        default="form_27",
    )
    dife_notified = fields.Boolean(
        string="DIFE Form 27 / 27(a) Notice Dispatched",
        default=False,
        tracking=True,
        help="Notice to DIFE within 2 working days for a reportable injury: "
        "BLA 2006 s.80 with BLR 2015 r.70 (Forms 27 / 27(a) / 27(b)). The "
        "register itself is kept under s.90 with r.73 (Form 28).",
    )
    dife_notification_date = fields.Date(string="DIFE Notice Date")
    dife_ack_ref = fields.Char(string="DIFE Acknowledgement Reference")
    half_year_return_due = fields.Date(
        string="Form 28 Half-Yearly Return Due Date",
        compute="_compute_half_year_due",
        store=True,
    )
    half_year_return_filed_on = fields.Date(string="Form 28 Return Filed On")
    return_to_work_date = fields.Date(
        string="Worker Returned to Work On",
        help="Closes the lost-time period for the Form 28 return and the "
        "BLA 2006 Ch. XII compensation assessment.",
    )
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

    @api.depends("accident_date")
    def _compute_half_year_due(self):
        from datetime import date as dt_date

        for rec in self:
            if rec.accident_date:
                d = fields.Date.to_date(rec.accident_date)
                if d.month <= 6:
                    rec.half_year_return_due = dt_date(d.year, 7, 15)
                else:
                    rec.half_year_return_due = dt_date(d.year + 1, 1, 15)
            else:
                rec.half_year_return_due = False

    @api.model_create_multi
    def create(self, vals_list):
        """Allocate the Form 28 serial (BLR 2015 r.73).

        The field is displayed on the register grid and form as the statutory
        serial, but nothing ever assigned it: every entry carried the literal
        default "New", so the register was not serially numbered at all.
        """
        for vals in vals_list:
            if vals.get("register_entry_no", "New") in ("New", False, ""):
                vals["register_entry_no"] = (
                    self.env["ir.sequence"].next_by_code("fix.statutory.accident.register") or "New"
                )
        return super().create(vals_list)

    def write(self, vals):
        protected = {"employee_id", "accident_date", "nature_of_injury", "incident_id"}
        if protected & set(vals):
            for rec in self:
                if rec.dife_notified or rec.dife_ack_ref:
                    raise UserError(
                        "BLA 2006 s.90 / BLR 2015 r.73: Statutory Form 28 Accident Register is append-only; core accident facts cannot be modified after DIFE notification."
                    )
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.dife_notified or rec.dife_ack_ref or rec.state != "recorded":
                raise UserError(
                    "BLA 2006 s.90 / BLR 2015 r.73: Statutory Form 28 Accident Register entries are append-only and cannot be deleted once notified."
                )
        return super().unlink()

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
