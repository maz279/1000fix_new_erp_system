# fix_attendance — M55: records, roster, the attendance lock (P08-M02).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

STANDARD_DAY_HOURS = 8.0   # s.102 Labour Act context (48h/6 days)


class FixShiftTemplate(models.Model):
    _name = "fix.shift.template"
    _description = "Shift Template"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M55",
        "form": "Shift Pattern",
        "fields": ["name", "start_hour", "end_hour"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    name = fields.Char(required=True)
    start_hour = fields.Float(required=True)
    end_hour = fields.Float(required=True)

    @api.constrains("start_hour", "end_hour")
    def _check_hours(self):
        for rec in self:
            if not (0 <= rec.start_hour < 24 and 0 <= rec.end_hour < 24):
                raise ValidationError("Shift hours must be within 0-24")


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixRosterSlot(models.Model):
    """The roster — the real answer to 'is this technician available?'."""
    _name = "fix.roster.slot"
    _description = "Roster Slot"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date, employee_id"
    _rec_name = "display_label"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    date = fields.Date(required=True, index=True)
    shift_id = fields.Many2one("fix.shift.template", string="Shift",
                               required=True)
    branch_id = fields.Many2one("fix.branch", string="Branch")
    on_leave = fields.Boolean(
        help="Set when an approved fix.leave.request covers this date")
    display_label = fields.Char(compute="_compute_label")

    @api.depends("employee_id", "date")
    def _compute_label(self):
        for rec in self:
            rec.display_label = "%s @ %s" % (
                rec.employee_id.name, rec.date or "")


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixAttendanceRecord(models.Model):
    """A check-in/out pair. Immutable once the period is LOCKED."""
    _name = "fix.attendance.record"
    _description = "Attendance Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "check_in desc"
    _rec_name = "display_label"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    check_in = fields.Datetime(required=True)
    check_out = fields.Datetime()
    source = fields.Selection(
        [("biometric", "Biometric Device"), ("mobile", "Mobile (Geofenced)"),
         ("manual", "Manual")], default="biometric", required=True)
    device_ref = fields.Char(
        string="Device Reference",
        help="INT-041 device id. The biometric TEMPLATE never lands here - "
             "S3 residency data routes through fix.identity.document")
    geo_lat = fields.Float(string="Latitude (P02 geofence)")
    geo_long = fields.Float(string="Longitude (P02 geofence)")
    worked_hours = fields.Float(compute="_compute_hours", store=True)
    overtime_hours = fields.Float(compute="_compute_hours", store=True,
                                  help="Hours beyond the statutory 8/day")
    display_label = fields.Char(compute="_compute_label")

    @api.depends("check_in", "check_out")
    def _compute_hours(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                span = (rec.check_out - rec.check_in).total_seconds() / 3600
                rec.worked_hours = round(span, 2)
                rec.overtime_hours = round(max(span - STANDARD_DAY_HOURS, 0), 2)
            else:
                rec.worked_hours = 0.0
                rec.overtime_hours = 0.0

    @api.depends("employee_id", "check_in")
    def _compute_label(self):
        for rec in self:
            rec.display_label = "%s @ %s" % (rec.employee_id.name,
                                             rec.check_in or "")

    def write(self, vals):
        # P08-M02-T05: the lock. Payroll calculates on LOCKED periods only -
        # an edit after the lock is a payroll error, not a convenience.
        if set(vals) - {"message_follower_ids", "activity_ids", "message_ids"}:
            lock = self.env["fix.attendance.lock"].search([
                ("state", "=", "locked")])
            for rec in self:
                for l in lock:
                    if (l.period_start <= rec.check_in.date()
                            <= l.period_end):
                        raise UserError(
                            "Attendance %s is locked in period %s - unlock "
                            "before editing" % (rec.display_label, l.name))
        return super().write(vals)

    def action_checkout(self):
        for rec in self:
            if rec.check_out:
                raise UserError("Already checked out")
            rec.check_out = fields.Datetime.now()
            publish(self.env, "attendance.checked_out",
                    "fix.attendance.record", rec.id,
                    {"employee": rec.employee_id.name,
                     "hours": rec.worked_hours})


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixAttendanceLock(models.Model):
    """The monthly attendance lock — journey 13's first gate."""
    _name = "fix.attendance.lock"
    _description = "Attendance Lock"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_start desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    name = fields.Char(required=True)
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    state = fields.Selection([("draft", "Draft"), ("locked", "Locked"),
                              ("unlocked", "Re-opened")],
                             default="draft", required=True, tracking=True)

    def action_lock(self):
        for rec in self:
            if rec.period_end >= fields.Date.today():
                raise UserError("Only a fully PAST period may be locked")
            rec.state = "locked"
            publish(self.env, "attendance.locked", "fix.attendance.lock",
                    rec.id, {"period": rec.name})

    def action_unlock(self):
        """Re-opening records WHY (audit): payroll recalculations only."""
        for rec in self:
            rec.state = "unlocked"
            publish(self.env, "attendance.unlocked", "fix.attendance.lock",
                    rec.id, {"period": rec.name})


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixWorkOrderAvailabilityExt(models.Model):
    """P08-M02-T03: the M02 -> M55 stub CLOSED in the live assignment path.

    The W2 seam answered 'available within working calendar' (M30). The
    real check now consults the ROSTER: a technician without a roster slot
    for the day, or one flagged on leave, is NOT assignable — a blocking
    error, not a warning.
    """
    _inherit = "fix.work.order"

    def action_check_technician_availability(self):
        for rec in self:
            if not rec.technician_id:
                return True
            day = fields.Date.today()
            slot = self.env["fix.roster.slot"].search([
                ("employee_id", "=", rec.technician_id.id),
                ("date", "=", day)], limit=1)
            if not slot:
                raise UserError(
                    "M55 availability: %s has no roster slot for %s — "
                    "assign from the roster, not the calendar"
                    % (rec.technician_id.name, day))
            if slot.on_leave:
                raise UserError(
                    "M55 availability: %s is on approved leave for %s"
                    % (rec.technician_id.name, day))
            return True

    def write(self, vals):
        result = super().write(vals)
        if vals.get("technician_id"):
            for rec in self:
                rec.action_check_technician_availability()
        return result

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")