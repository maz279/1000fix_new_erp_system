# fix_attendance — M55: records, roster, INT-041 biometric devices, the attendance lock (P08-M02 / R06-M02).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

# Bangladesh Labour Act 2006 (and 2013, 2018, 2026 amendments) Working-Time Standards:
STANDARD_DAY_HOURS = 8.0  # s. 100 BLA 2006: standard daily hours
MAX_DAILY_HOURS = 10.0  # s. 102 / s. 108 BLA 2006: daily ceiling with overtime
MAX_DAILY_OT_HOURS = 2.0  # s. 108 BLA 2006: maximum daily overtime hours
STANDARD_WEEKLY_HOURS = 48.0  # s. 102 BLA 2006: normal weekly limit
MAX_WEEKLY_HOURS = 60.0  # s. 102 BLA 2006: weekly ceiling with overtime
MAX_WEEKLY_OT_HOURS = 12.0  # s. 108 BLA 2006: maximum weekly overtime hours
OT_DIVISOR_HOURS = 208.0  # BLR 2015 formula: 208-hour monthly divisor shared with M56
MIN_SHIFT_REST_HOURS = (
    11.0  # s. 101 / s. 105 BLA 2006: minimum rest between shifts (spreadover 11-12h)
)
OVERTIME_RATE_MULTIPLIER = 2.0  # s. 108 BLA 2006: overtime paid at twice ordinary wage rate

# M55 AUT-WFM-02: flagged mobile clock-ins are decided by the attendance officers
# (hr_attendance "Officer: Manage all attendances", implied by its Administrator).
APPROVER_GROUP = "hr_attendance.group_hr_attendance_user"


class FixShiftTemplate(models.Model):
    _name = "fix.shift.template"
    _description = "Shift Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    start_hour = fields.Float(required=True)
    end_hour = fields.Float(required=True)

    @api.constrains("start_hour", "end_hour")
    def _check_hours(self):
        for rec in self:
            if not (0 <= rec.start_hour < 24 and 0 <= rec.end_hour < 24):
                raise ValidationError("Shift hours must be within 0-24")


class FixRosterSlot(models.Model):
    """The roster — the real answer to 'is this technician available?'."""

    _name = "fix.roster.slot"
    _description = "Roster Slot"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date, employee_id"
    _rec_name = "display_label"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    date = fields.Date(required=True, index=True)
    shift_id = fields.Many2one("fix.shift.template", string="Shift", required=True)
    branch_id = fields.Many2one("fix.branch", string="Branch")
    on_leave = fields.Boolean(help="Set when an approved fix.leave.request covers this date")
    display_label = fields.Char(compute="_compute_label")

    @api.depends("employee_id", "date")
    def _compute_label(self):
        for rec in self:
            rec.display_label = "%s @ %s" % (
                rec.employee_id.name if rec.employee_id else "",
                rec.date or "",
            )


class FixBiometricDevice(models.Model):
    """INT-041 Biometric Attendance Terminal (S3 residency classification).

    Device registration and punch ingestion for INT-041 hardware.
    The biometric template itself NEVER lands here or in any regional store —
    S3 residency data routes strictly through fix.identity.document (Z4 vault).
    """

    _name = "fix.biometric.device"
    _description = "INT-041 Biometric Attendance Device"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "device_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    device_id = fields.Char(
        string="Device Identifier",
        required=True,
        index=True,
        help="INT-041 hardware identifier / serial code",
    )
    name = fields.Char(string="Device Name", required=True)
    model_type = fields.Char(string="Device Model", default="INT-041", required=True)
    branch_id = fields.Many2one("fix.branch", string="Branch / Facility")
    ip_address = fields.Char(string="IP Address / Hostname")
    location_desc = fields.Char(string="Physical Location")
    active = fields.Boolean(default=True)
    last_sync_at = fields.Datetime(string="Last Ingest Sync")
    status = fields.Selection(
        [("online", "Online"), ("offline", "Offline"), ("syncing", "Syncing")],
        default="online",
        tracking=True,
    )

    # Odoo 19 ignores the legacy `_sql_constraints` list (the registry logs
    # "no longer supported"), so the uniqueness was never enforced.
    _device_id_uniq = models.Constraint("UNIQUE (device_id)", "INT-041 device ID must be unique!")

    def action_ingest_punch(
        self, employee_id, check_time, punch_type="check_in", biometric_template=None
    ):
        """Ingests punch from this INT-041 device with S3 biometric residency routing.

        Args:
            employee_id: int (hr.employee ID) or hr.employee record
            check_time: datetime or str
            punch_type: 'check_in' or 'check_out'
            biometric_template: optional raw template string/bytes (routed to Z4)
        """
        self.ensure_one()
        emp = self.env["hr.employee"].browse(
            employee_id.id if hasattr(employee_id, "id") else employee_id
        )
        if not emp.exists():
            raise UserError("Invalid employee reference for biometric ingest: %s" % employee_id)

        # S3 Residency Routing: raw template routed strictly to fix.identity.document (Z4 storage).
        # `document_number` is the document's residency-classified field: the
        # residency.mixin sends its value to Z4 and stores only the pointer.
        # (The former `document_data` / `name` keys are not fields of the
        # model, so every template ingest crashed with "Invalid field".)
        if biometric_template:
            partner = emp.partner_id or (emp.user_id.partner_id if emp.user_id else None)
            if partner:
                self.env["fix.identity.document"].create(
                    {
                        "partner_id": partner.id,
                        "document_type": "biometric",
                        "document_number": str(biometric_template),
                        "company_id": self.company_id.id,
                    }
                )

        check_dt = fields.Datetime.to_datetime(check_time)
        check_date = check_dt.date()

        # Lock check
        lock = self.env["fix.attendance.lock"].search(
            [
                ("state", "=", "locked"),
                ("period_start", "<=", check_date),
                ("period_end", ">=", check_date),
            ],
            limit=1,
        )
        if lock:
            raise UserError("Attendance period %s is locked — biometric punch rejected" % lock.name)

        Record = self.env["fix.attendance.record"]
        if punch_type == "check_in":
            rec = Record.create(
                {
                    "employee_id": emp.id,
                    "check_in": check_dt,
                    "source": "biometric",
                    "device_ref": self.device_id,
                    "company_id": self.company_id.id,
                }
            )
        else:
            rec = Record.search(
                [("employee_id", "=", emp.id), ("check_out", "=", False)],
                order="check_in desc",
                limit=1,
            )
            if rec:
                rec.write({"check_out": check_dt})
            else:
                rec = Record.create(
                    {
                        "employee_id": emp.id,
                        "check_in": check_dt,
                        "check_out": check_dt,
                        "source": "biometric",
                        "device_ref": self.device_id,
                        "company_id": self.company_id.id,
                    }
                )

        self.last_sync_at = fields.Datetime.now()
        return rec


class FixAttendanceRecord(models.Model):
    """A check-in/out pair. Immutable once the period is LOCKED."""

    _name = "fix.attendance.record"
    _description = "Attendance Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "check_in desc"
    _rec_name = "display_label"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    check_in = fields.Datetime(required=True)
    check_out = fields.Datetime()
    source = fields.Selection(
        [
            ("biometric", "Biometric Device"),
            ("mobile", "Mobile (Geofenced)"),
            ("mobile_offline", "Mobile (Offline Journal)"),
            ("manual", "Manual"),
        ],
        default="biometric",
        required=True,
    )
    device_ref = fields.Char(
        string="Device Reference",
        help="INT-041 device id. The biometric TEMPLATE never lands here - "
        "S3 residency data routes through fix.identity.document",
    )
    geo_lat = fields.Float(string="Latitude (P02 geofence)")
    geo_long = fields.Float(string="Longitude (P02 geofence)")
    # M55 AUT-WFM-02 / T-06: a mobile clock-in is evaluated server-side (own-zone
    # geofence + GPS accuracy) and RECORDED with its result; anything but a clean
    # result is flagged for approval - never silently accepted, never dropped.
    accuracy_m = fields.Float(
        string="GPS Accuracy (m)", help="Reported accuracy radius of the GPS fix"
    )
    geofence_result = fields.Selection(
        [
            ("inside", "Inside Own-Zone Geofence"),
            ("outside", "Outside Own-Zone Geofence"),
            ("no_zone", "No Dispatch Zone"),
            ("no_geofence", "Zone Without Geofence"),
            ("low_accuracy", "Low GPS Accuracy"),
        ],
        string="Geofence Result",
        readonly=True,
        tracking=True,
    )
    approval_state = fields.Selection(
        [
            ("not_required", "Not Required"),
            ("pending", "Pending Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Approval",
        default="not_required",
        required=True,
        index=True,
        tracking=True,
    )
    approval_reason = fields.Char(string="Flag Reason", readonly=True)
    approved_by = fields.Many2one("res.users", string="Decided By", readonly=True, tracking=True)
    approved_at = fields.Datetime(string="Decided At", readonly=True)
    worked_hours = fields.Float(compute="_compute_hours", store=True)
    overtime_hours = fields.Float(
        compute="_compute_hours", store=True, help="Hours beyond the statutory 8/day (s. 100/108)"
    )
    week_start = fields.Date(
        string="ISO Week Start", compute="_compute_hours", store=True, index=True
    )
    is_rest_day = fields.Boolean(
        string="Weekly Rest Day Call-In",
        default=False,
        help="BLA s.103/108: work performed on scheduled weekly rest day",
    )
    rest_day_hours = fields.Float(
        string="Rest-Day Worked Hours", compute="_compute_hours", store=True
    )
    weekly_worked_hours = fields.Float(
        string="Weekly Worked Hours", compute="_compute_weekly_totals"
    )
    weekly_ot_hours = fields.Float(string="Weekly Overtime Hours", compute="_compute_weekly_totals")
    weekly_ot_limit_exceeded = fields.Boolean(
        string="Weekly OT Cap Exceeded", compute="_compute_weekly_totals"
    )
    display_label = fields.Char(compute="_compute_label")
    hr_attendance_id = fields.Many2one(
        "hr.attendance", string="Odoo Attendance Sync", ondelete="set null"
    )
    compliance_status = fields.Selection(
        [
            ("compliant", "Compliant"),
            ("daily_limit_exceeded", "Daily Limit Exceeded (>10h)"),
            ("rest_interval_violation", "Rest Interval Violation (<11h)"),
            ("weekly_limit_exceeded", "Weekly Limit Exceeded (>60h)"),
        ],
        default="compliant",
        compute="_compute_compliance",
        store=True,
        tracking=True,
    )
    statutory_notes = fields.Char(
        string="Compliance Notes", compute="_compute_compliance", store=True
    )

    @api.depends("check_in", "check_out", "approval_state", "is_rest_day")
    def _compute_hours(self):
        for rec in self:
            if rec.check_in:
                cdate = rec.check_in.date()
                rec.week_start = cdate - timedelta(days=cdate.weekday())
            else:
                rec.week_start = False
            # a REJECTED clock-in is no worked time (and no overtime for M56)
            if rec.check_in and rec.check_out and rec.approval_state != "rejected":
                span = (rec.check_out - rec.check_in).total_seconds() / 3600
                rec.worked_hours = round(span, 2)
                if rec.is_rest_day:
                    rec.rest_day_hours = round(span, 2)
                    rec.overtime_hours = round(span, 2)
                else:
                    rec.rest_day_hours = 0.0
                    rec.overtime_hours = round(max(span - STANDARD_DAY_HOURS, 0), 2)
            else:
                rec.worked_hours = 0.0
                rec.overtime_hours = 0.0
                rec.rest_day_hours = 0.0

    @api.depends(
        "worked_hours",
        "overtime_hours",
        "rest_day_hours",
        "week_start",
        "employee_id",
        "approval_state",
    )
    def _compute_weekly_totals(self):
        for rec in self:
            if not rec.employee_id or not rec.week_start:
                rec.weekly_worked_hours = rec.worked_hours or 0.0
                rec.weekly_ot_hours = rec.overtime_hours or 0.0
                rec.weekly_ot_limit_exceeded = (
                    rec.weekly_ot_hours > MAX_WEEKLY_OT_HOURS
                    or rec.weekly_worked_hours > MAX_WEEKLY_HOURS
                )
                continue
            w_start_dt = fields.Datetime.to_datetime(rec.week_start)
            w_end_dt = fields.Datetime.to_datetime(rec.week_start + timedelta(days=7))
            siblings = self.search(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("approval_state", "!=", "rejected"),
                    ("check_in", ">=", w_start_dt),
                    ("check_in", "<", w_end_dt),
                ]
            )
            if rec.id and rec not in siblings:
                siblings |= rec
            w_worked = round(sum(siblings.mapped("worked_hours")), 2)
            w_daily_ot = round(sum(siblings.mapped("overtime_hours")), 2)
            if not rec.id and rec.approval_state != "rejected":
                w_worked = round(w_worked + (rec.worked_hours or 0.0), 2)
                w_daily_ot = round(w_daily_ot + (rec.overtime_hours or 0.0), 2)
            w_excess_ot = round(max(w_worked - STANDARD_WEEKLY_HOURS, 0.0), 2)
            rec.weekly_worked_hours = w_worked
            rec.weekly_ot_hours = max(w_daily_ot, w_excess_ot)
            rec.weekly_ot_limit_exceeded = (
                rec.weekly_ot_hours > MAX_WEEKLY_OT_HOURS or w_worked > MAX_WEEKLY_HOURS
            )

    @api.depends("worked_hours", "overtime_hours", "employee_id", "check_in", "check_out")
    def _compute_compliance(self):
        for rec in self:
            status = "compliant"
            notes = "Standard shift compliant per BLA 2006"
            if rec.worked_hours > MAX_DAILY_HOURS:
                status = "daily_limit_exceeded"
                notes = (
                    "BLA 2006 s.102/108 breach: %.2fh worked exceeds 10.0h daily limit"
                    % rec.worked_hours
                )
            elif rec.check_in and rec.employee_id:
                # Check consecutive rest from previous check_out for this employee
                prev = self.search(
                    [
                        ("employee_id", "=", rec.employee_id.id),
                        ("id", "!=", rec.id or 0),
                        ("check_out", "<=", rec.check_in),
                    ],
                    order="check_out desc",
                    limit=1,
                )
                if prev and prev.check_out:
                    rest_span = (rec.check_in - prev.check_out).total_seconds() / 3600
                    if 0 < rest_span < MIN_SHIFT_REST_HOURS:
                        status = "rest_interval_violation"
                        notes = (
                            "BLA 2006 s.101/105 breach: %.2fh rest between shifts is under statutory 11.0h"
                            % rest_span
                        )
                if status == "compliant":
                    cdate = rec.check_in.date()
                    w_start = cdate - timedelta(days=cdate.weekday())
                    siblings = self.search(
                        [
                            ("employee_id", "=", rec.employee_id.id),
                            ("approval_state", "!=", "rejected"),
                            ("check_in", ">=", fields.Datetime.to_datetime(w_start)),
                            (
                                "check_in",
                                "<",
                                fields.Datetime.to_datetime(w_start + timedelta(days=7)),
                            ),
                        ]
                    )
                    w_worked = round(sum(siblings.mapped("worked_hours")), 2)
                    w_ot = max(
                        round(sum(siblings.mapped("overtime_hours")), 2),
                        round(max(w_worked - STANDARD_WEEKLY_HOURS, 0.0), 2),
                    )
                    if w_worked > MAX_WEEKLY_HOURS:
                        status = "weekly_limit_exceeded"
                        notes = (
                            "BLA 2006 s.102 breach: %.2fh worked in week exceeds 60.0h weekly limit"
                            % w_worked
                        )
                    elif w_ot > MAX_WEEKLY_OT_HOURS:
                        status = "weekly_limit_exceeded"
                        notes = (
                            "BLA 2006 s.108 breach: %.2fh overtime in week exceeds 12.0h weekly OT cap"
                            % w_ot
                        )
            rec.compliance_status = status
            rec.statutory_notes = notes

    @api.depends("employee_id", "check_in")
    def _compute_label(self):
        for rec in self:
            rec.display_label = "%s @ %s" % (
                rec.employee_id.name if rec.employee_id else "",
                rec.check_in or "",
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            cin = vals.get("check_in")
            if cin:
                cdate = fields.Datetime.to_datetime(cin).date()
                lock = self.env["fix.attendance.lock"].search(
                    [
                        ("state", "=", "locked"),
                        ("period_start", "<=", cdate),
                        ("period_end", ">=", cdate),
                    ],
                    limit=1,
                )
                if lock:
                    raise UserError(
                        "Cannot create attendance record in locked period %s" % lock.name
                    )
        return super().create(vals_list)

    def write(self, vals):
        # P08-M02-T05: the lock. Payroll calculates on LOCKED periods only -
        # an edit after the lock is a payroll error, not a convenience.
        if set(vals) - {"message_follower_ids", "activity_ids", "message_ids"}:
            lock = self.env["fix.attendance.lock"].search([("state", "=", "locked")])
            for rec in self:
                for period_lock in lock:
                    if period_lock.period_start <= rec.check_in.date() <= period_lock.period_end:
                        raise UserError(
                            "Attendance %s is locked in period %s - unlock "
                            "before editing" % (rec.display_label, period_lock.name)
                        )
        return super().write(vals)

    def unlink(self):
        for rec in self:
            # check_in is required (NOT NULL): every stored record has one.
            cdate = rec.check_in.date()
            lock = self.env["fix.attendance.lock"].search(
                [
                    ("state", "=", "locked"),
                    ("period_start", "<=", cdate),
                    ("period_end", ">=", cdate),
                ],
                limit=1,
            )
            if lock:
                raise UserError("Cannot delete attendance record in locked period %s" % lock.name)
        return super().unlink()

    # --- AUT-WFM-02 approval of flagged clock-ins ------------------------------

    def _check_approver(self):
        if not self.env.user.has_group(APPROVER_GROUP):
            raise AccessError(
                "Only an attendance officer may approve or reject a flagged clock-in (M55 AUT-WFM-02)"
            )

    def _decide(self, state, note):
        self._check_approver()
        for rec in self:
            if rec.approval_state != "pending":
                raise UserError(
                    "Attendance %s is not pending approval (it is %s)"
                    % (rec.display_label, rec.approval_state)
                )
            rec.write(
                {
                    "approval_state": state,
                    "approved_by": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body=note)
            # Literal event types: the registry (FF / contracts check) needs the
            # name in the producer module - a composed f-string cannot be registered.
            event_type = "attendance.approved" if state == "approved" else "attendance.rejected"
            publish(
                self.env,
                event_type,
                "fix.attendance.record",
                rec.id,
                {"employee": rec.employee_id.name, "reason": rec.approval_reason},
            )

    def action_approve(self):
        """Accept a flagged clock-in: it counts as worked time."""
        self._decide("approved", "Flagged clock-in approved")

    def action_reject(self, reason=""):
        """Refuse a flagged clock-in: it stays recorded but is no worked time."""
        self._decide("rejected", "Flagged clock-in rejected: %s" % (reason or "no reason given"))

    @api.model
    def pending_in_period(self, period_start, period_end, company=None):
        """Flagged clock-ins of [period_start, period_end] still pending approval
        (BRU-WFM-01: a period is locked and paid only on VERIFIED attendance)."""
        domain = [
            ("approval_state", "=", "pending"),
            ("check_in", ">=", fields.Datetime.to_datetime(period_start)),
            ("check_in", "<", fields.Datetime.to_datetime(period_end + timedelta(days=1))),
        ]
        if company:
            domain.append(("company_id", "=", company.id))
        return self.search(domain, order="check_in")

    def action_checkout(self):
        for rec in self:
            if rec.check_out:
                raise UserError("Already checked out")
            rec.check_out = fields.Datetime.now()
            publish(
                self.env,
                "attendance.checked_out",
                "fix.attendance.record",
                rec.id,
                {
                    "employee": rec.employee_id.name,
                    "hours": rec.worked_hours,
                    "compliance": rec.compliance_status,
                },
            )


class FixAttendanceLock(models.Model):
    """The monthly attendance lock — journey 13's first gate."""

    _name = "fix.attendance.lock"
    _description = "Attendance Lock"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_start desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("locked", "Locked"), ("unlocked", "Re-opened")],
        default="draft",
        required=True,
        tracking=True,
    )

    def action_lock(self):
        for rec in self:
            if rec.period_end >= fields.Date.today():
                raise UserError("Only a fully PAST period may be locked")
            # BRU-WFM-01: lock VERIFIED attendance only - a pending clock-in could
            # never be decided afterwards (locked records are immutable)
            pending = self.env["fix.attendance.record"].pending_in_period(
                rec.period_start, rec.period_end, rec.company_id
            )
            if pending:
                raise UserError(
                    "Attendance period %s has %d clock-in(s) pending approval - approve or "
                    "reject them before locking: %s"
                    % (rec.name, len(pending), ", ".join(pending.mapped("display_label")))
                )
            rec.state = "locked"
            publish(
                self.env, "attendance.locked", "fix.attendance.lock", rec.id, {"period": rec.name}
            )

    def action_unlock(self):
        """Re-opening records WHY (audit): payroll recalculations only."""
        for rec in self:
            rec.state = "unlocked"
            publish(
                self.env, "attendance.unlocked", "fix.attendance.lock", rec.id, {"period": rec.name}
            )

    def action_export_form10_overtime_register(self):
        """BLR 2015 Rule 102 / Form 10: Statutory Overtime Register using 208-hour divisor."""
        from decimal import Decimal

        from libs.py.payroll_engine import OT_DIVISOR_HOURS, overtime_amount

        self.ensure_one()
        records = self.env["fix.attendance.record"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("approval_state", "!=", "rejected"),
                ("check_in", ">=", fields.Datetime.to_datetime(self.period_start)),
                ("check_in", "<", fields.Datetime.to_datetime(self.period_end + timedelta(days=1))),
            ],
            order="employee_id, check_in",
        )
        by_emp = {}
        for att in records:
            emp = att.employee_id
            bucket = by_emp.setdefault(
                emp.id,
                {
                    "employee_id": emp.id,
                    "employee_code": emp.employee_code or "",
                    "employee_name": emp.name or "",
                    "worked_hours": 0.0,
                    "overtime_hours": 0.0,
                    "rest_day_hours": 0.0,
                },
            )
            bucket["worked_hours"] = round(bucket["worked_hours"] + (att.worked_hours or 0.0), 2)
            bucket["overtime_hours"] = round(
                bucket["overtime_hours"] + (att.overtime_hours or 0.0), 2
            )
            bucket["rest_day_hours"] = round(
                bucket["rest_day_hours"] + (att.rest_day_hours or 0.0), 2
            )

        rows = []
        for idx, (emp_id, data) in enumerate(by_emp.items(), start=1):
            contract = self.env["fix.employment.contract"].search(
                [("employee_id", "=", emp_id), ("state", "=", "active")],
                order="joining_date desc, id desc",
                limit=1,
            )
            emp = self.env["hr.employee"].browse(emp_id)
            basic = Decimal(str((contract.basic_monthly if contract else emp.basic_wage) or 0.0))
            dearness = Decimal(str((contract.dearness_allowance if contract else 0.0) or 0.0))
            adhoc = Decimal(str((contract.adhoc_allowance if contract else 0.0) or 0.0))
            ot_hrs = Decimal(str(data["overtime_hours"]))
            ot_pay = overtime_amount(
                basic,
                ot_hrs,
                dearness_monthly=dearness,
                adhoc_monthly=adhoc,
                divisor_hours=OT_DIVISOR_HOURS,
            )
            hourly_rate = (
                round(float((basic + dearness + adhoc) / OT_DIVISOR_HOURS * Decimal("2")), 2)
                if basic > 0
                else 0.0
            )
            rows.append(
                {
                    "serial": idx,
                    **data,
                    "basic_wage": float(basic),
                    "hourly_ot_rate": hourly_rate,
                    "overtime_pay": float(ot_pay),
                    "divisor_hours": int(OT_DIVISOR_HOURS),
                    "statutory_form": "Form 10 (BLR 2015 r.102 / BLA 2006 s.108)",
                }
            )
        return rows


class FixWorkOrderAvailabilityExt(models.Model):
    """P08-M02-T03: the M02 -> M55 stub CLOSED in the live assignment path.

    The W2 seam answered 'available within working calendar' (M30). The
    real check now consults the ROSTER: a technician without a roster slot
    for the day, or one flagged on leave, is NOT assignable — a blocking
    error, not a warning.
    """

    _inherit = "fix.work.order"

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    def action_check_technician_availability(self):
        # Every record is checked: an early `return True` inside the loop used
        # to wave the rest of a multi-record call through unchecked.
        for rec in self:
            if not rec.technician_id:
                continue
            day = fields.Date.today()
            slot = self.env["fix.roster.slot"].search(
                [("employee_id", "=", rec.technician_id.id), ("date", "=", day)], limit=1
            )
            if not slot:
                raise UserError(
                    "M55 availability: %s has no roster slot for %s — "
                    "assign from the roster, not the calendar" % (rec.technician_id.name, day)
                )
            if slot.on_leave:
                raise UserError(
                    "M55 availability: %s is on approved leave for %s"
                    % (rec.technician_id.name, day)
                )
            rejected_punch = self.env["fix.attendance.record"].search(
                [
                    ("employee_id", "=", rec.technician_id.id),
                    ("check_in", ">=", fields.Datetime.to_datetime(day)),
                    ("check_in", "<", fields.Datetime.to_datetime(day + timedelta(days=1))),
                    ("approval_state", "=", "rejected"),
                ],
                limit=1,
            )
            if rejected_punch:
                raise UserError(
                    "M55 availability: %s has a rejected geofence clock-in for %s"
                    % (rec.technician_id.name, day)
                )
            publish(
                self.env,
                "attendance.availability.verified",
                "fix.work.order",
                rec.id,
                {
                    "technician_id": rec.technician_id.id,
                    "technician": rec.technician_id.name,
                    "date": str(day),
                    "roster_slot_id": slot.id,
                },
            )
        return True

    def write(self, vals):
        result = super().write(vals)
        if vals.get("technician_id"):
            for rec in self:
                rec.action_check_technician_availability()
        return result
