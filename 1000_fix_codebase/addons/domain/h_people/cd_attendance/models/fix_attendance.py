# fix_attendance — M55: records, roster, INT-041 biometric devices, the attendance lock (P08-M02 / R06-M02).
#
# A09 workflow audit (M55-2..M55-6, M55-8, M55-10, M55-12): the employee
# approved his own flagged clock-in by writing `approval_state`, typed manual,
# "mobile" and "biometric" rows for himself and colleagues that were paid,
# stretched an approved 8 h day to 14 h, and was paid overtime nobody approved;
# a lock could be born 'locked' over pending clock-ins, records could be
# re-dated into a locked month, and the supervisor unlocked a paid month with
# no reason. What holds now:
#
#   * capture: biometric rows come only from a registered, active device
#     (action_ingest_punch, replays de-duplicated); mobile rows only from the
#     technician API (superuser, evaluated); everything a user types is
#     'manual', needs a reason and is born PENDING;
#   * approval: the workflow fields are guarded (fix.guarded.mixin); a pending
#     record is decided through a routed regularisation (line manager first,
#     then the attendance officers; requester, creator and subject never
#     decide); a decided record whose hours change goes back to pending;
#   * valuation: per employee-day, so a split shift keeps its overtime;
#     PAYABLE overtime = min(recorded excess, approved overtime request, the
#     s.108 daily cap) and 0 for an employee not overtime-eligible;
#   * the lock: guarded state, the past-period and pending checks (company-wide,
#     as superuser) wherever the state becomes 'locked', one lock per period,
#     new dates checked as well as old, unlock by a separate role with a reason
#     and never once payroll has taken the period.
from datetime import date, datetime, time, timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

# Bangladesh Labour Act 2006 (and 2013, 2018, 2026 amendments) Working-Time Standards:
STANDARD_DAY_HOURS = 8.0  # s. 100 BLA 2006: standard daily hours
MAX_DAILY_HOURS = 10.0  # s. 100 / s. 108 BLA 2006: daily ceiling with overtime
MAX_DAILY_OT_HOURS = 2.0  # s. 100 / s. 108 BLA 2006: at most 2 h overtime a day
STANDARD_WEEKLY_HOURS = 48.0  # s. 102 BLA 2006: normal weekly limit
# s.102 allows up to 60 h with overtime (average 56 h over a year); the
# module spec (BRU-WFM-05) says 48 h. The ceiling the checks use is a company
# setting (res.company.fix_att_max_weekly_hours, default 60.0 as coded before
# the audit) until the business rules on it (A09 report §7.4).
MAX_WEEKLY_HOURS = 60.0
OT_DIVISOR_HOURS = 208.0  # BLR 2015 formula: 208-hour monthly divisor shared with M56
# The module's own rest-between-shifts rule. It is NOT BLA s.101 (which is
# the rest/meal interval inside a day) - a company setting, default 11.0 h as
# coded before the audit (res.company.fix_att_min_rest_hours).
MIN_SHIFT_REST_HOURS = 11.0
OVERTIME_RATE_MULTIPLIER = 2.0  # s. 108 BLA 2006: overtime paid at twice ordinary wage rate
# BLA 2006 s.109: no woman works between 10 p.m. and 6 a.m. without her consent.
NIGHT_START_HOUR = 22.0
NIGHT_END_HOUR = 6.0

# M55 AUT-WFM-02: flagged clock-ins are decided by the line manager first, then
# the attendance officers (hr_attendance "Officer: Manage all attendances").
APPROVER_GROUP = "hr_attendance.group_hr_attendance_user"
SUPERVISOR_GROUP = "cd_attendance.group_attendance_supervisor"
LOCK_MANAGER_GROUP = "cd_attendance.group_attendance_lock_manager"
PAYABLE_STATES = ("not_required", "approved")
# payroll states in which a period has taken the attendance (cd_payroll_bd)
PAYROLL_OPEN_STATES = ("draft",)
# FR-WFM-052: once payroll has PAID a period, a correction is carried forward
# as an approved adjustment into the next payroll; while the run is between
# verification and payment the period stays shut (the slips would diverge).
PAYROLL_PAID_STATES = ("paid", "posted")


def _day_bounds(day):
    start = datetime.combine(day, time.min)
    return start, start + timedelta(days=1)


DHAKA_TZ = "Asia/Dhaka"  # the business day (brief: UTC+6, weekend Fri-Sat)


def _dhaka_day_bounds_utc(day):
    """(start, end) naive-UTC datetimes of the Dhaka calendar day `day`: the
    stored datetimes are UTC while the business day is Asia/Dhaka, so a UTC
    midnight window is 6 h off every evening."""
    tz = pytz.timezone(DHAKA_TZ)
    start = (
        tz.localize(datetime.combine(fields.Date.to_date(day), time.min))
        .astimezone(pytz.utc)
        .replace(tzinfo=None)
    )
    return start, start + timedelta(days=1)


def _dhaka_wall(moment):
    """A stored (UTC) datetime as the Dhaka wall-clock hour (float), for the
    roster shift comparisons (a shift template's hours are local)."""
    moment = fields.Datetime.to_datetime(moment)
    local = pytz.utc.localize(moment).astimezone(pytz.timezone(DHAKA_TZ))
    return local.hour + local.minute / 60.0


def _locked_lock(env, company, day):
    """The LOCKED lock of `company` covering `day` (superuser: every OU)."""
    if not day:
        return env["fix.attendance.lock"]
    domain = [
        ("state", "=", "locked"),
        ("period_start", "<=", day),
        ("period_end", ">=", day),
    ]
    if company:
        domain.append(("company_id", "=", company.id))
    return env["fix.attendance.lock"].sudo().search(domain, limit=1)


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

    def _fix_duration(self):
        self.ensure_one()
        span = self.end_hour - self.start_hour
        return span if span > 0 else span + 24.0

    def _fix_covers_night(self):
        """True when any part of the shift falls in 22:00-06:00 (s.109)."""
        self.ensure_one()
        if self.end_hour <= self.start_hour:  # crosses midnight
            return True
        return self.start_hour < NIGHT_END_HOUR or self.end_hour > NIGHT_START_HOUR


class FixRosterSlot(models.Model):
    """The roster — the real answer to 'is this technician available?'."""

    _name = "fix.roster.slot"
    _description = "Roster Slot"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    on_leave = fields.Boolean(
        readonly=True,
        help="Set by the leave workflow when an approved fix.leave.request covers this date",
    )
    display_label = fields.Char(compute="_compute_label")

    def _fix_guarded_fields(self) -> set:
        # M55-10: nothing set this flag, and a supervisor could type it
        return super()._fix_guarded_fields() | {"on_leave"}

    @api.depends("employee_id", "date")
    def _compute_label(self):
        for rec in self:
            rec.display_label = "%s @ %s" % (
                rec.employee_id.name if rec.employee_id else "",
                rec.date or "",
            )

    @api.constrains("employee_id", "date", "shift_id")
    def _check_daily_schedule(self):
        # E3: day + night shift on one day = 16 h scheduled (s.100: 10 h a day)
        Rule = self.env["fix.working.time.rule"]
        for rec in self:
            day = self.sudo().search(
                [("employee_id", "=", rec.employee_id.id), ("date", "=", rec.date)]
            )
            hours = sum(s.shift_id._fix_duration() for s in day)
            cap = Rule._fix_values_for(rec.company_id, rec.date)["daily_max_hours"]
            if cap and hours > cap:
                raise ValidationError(
                    "%s would be rostered %.1f h on %s (BLA s.100: at most %.0f h a day "
                    "with overtime)." % (rec.employee_id.name, hours, rec.date, cap)
                )

    @api.constrains("employee_id", "date", "shift_id")
    def _check_women_night_work(self):
        # BRU-WFM-06 / BLA s.109: a woman works 22:00-06:00 only with her consent
        Consent = self.env["fix.night.work.consent"].sudo()
        for rec in self:
            emp = rec.employee_id.sudo()
            if emp.sex != "female" or not rec.shift_id._fix_covers_night():
                continue
            if not Consent._fix_covering(emp, rec.date):
                raise ValidationError(
                    "%s cannot be rostered on %s (%s) between 10 p.m. and 6 a.m. without her "
                    "recorded consent (BLA s.109)." % (emp.name, rec.date, rec.shift_id.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        slots = super().create(vals_list)
        slots._fix_sync_on_leave()
        return slots

    def write(self, vals):
        res = super().write(vals)
        if {"employee_id", "date"} & set(vals):
            self._fix_sync_on_leave()
        return res

    def _fix_sync_on_leave(self):
        """on_leave = an APPROVED leave covers the slot's date (M55-10)."""
        Leave = self.env["fix.leave.request"].sudo()
        for slot in self.sudo():
            covered = bool(
                Leave.search_count(
                    [
                        ("employee_id", "=", slot.employee_id.id),
                        ("state", "=", "approved"),
                        ("date_from", "<=", slot.date),
                        ("date_to", ">=", slot.date),
                    ]
                )
            )
            if slot.on_leave != covered:
                slot._guarded().write({"on_leave": covered})


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

        M55-8: only a registered, ACTIVE, online device of the employee's
        company ingests; the caller is the device integration (attendance
        supervisor or superuser); a replayed punch returns the record it
        already created instead of a second one.

        Args:
            employee_id: int (hr.employee ID) or hr.employee record
            check_time: datetime or str
            punch_type: 'check_in' or 'check_out'
            biometric_template: optional raw template string/bytes (routed to Z4)
        """
        self.ensure_one()
        if not (self.env.su or self.env.user.has_group(SUPERVISOR_GROUP)):
            raise AccessError(
                "Punches are ingested by the biometric integration (Attendance Supervisor), "
                "not by employees."
            )
        device = self.sudo()
        if not device.active or device.status == "offline":
            raise UserError(
                "Device %s is %s: an inactive or offline terminal cannot ingest punches."
                % (device.device_id, "inactive" if not device.active else "offline")
            )
        emp = (
            self.env["hr.employee"]
            .sudo()
            .browse(employee_id.id if hasattr(employee_id, "id") else employee_id)
        )
        if not emp.exists():
            raise UserError("Invalid employee reference for biometric ingest: %s" % employee_id)
        if emp.company_id and emp.company_id != device.company_id:
            raise UserError(
                "Device %s belongs to %s; %s works for %s."
                % (device.device_id, device.company_id.name, emp.name, emp.company_id.name)
            )

        # BRU-WFM-08 / T-02 (PDPA 2026): no biometric processing without the
        # employee's specific consent; the alternatives (mobile, manual) stay open.
        check_dt = fields.Datetime.to_datetime(check_time)
        if not self.env["fix.biometric.consent"]._fix_has_consent(emp, check_dt.date()):
            raise UserError(
                "%s has no recorded consent to biometric processing (BRU-WFM-08): the punch "
                "is not ingested. Record it through another capture method (mobile or a "
                "manual entry with a reason), or record the employee's consent first." % emp.name
            )

        # S3 Residency Routing: raw template routed strictly to fix.identity.document (Z4 storage).
        # `document_number` is the document's residency-classified field: the
        # residency.mixin sends its value to Z4 and stores only the pointer.
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

        lock = _locked_lock(self.env, device.company_id, check_dt.date())
        if lock:
            raise UserError("Attendance period %s is locked — biometric punch rejected" % lock.name)

        Record = self.env["fix.attendance.record"].sudo()._guarded()
        base = {
            "employee_id": emp.id,
            "source": "biometric",
            "device_ref": device.device_id,
            "device_id": device.id,
            "company_id": device.company_id.id,
        }
        if punch_type == "check_in":
            rec = Record.search(
                [("employee_id", "=", emp.id), ("check_in", "=", check_dt)], limit=1
            )
            if not rec:  # a replay of the same punch is the same record (T-05)
                rec = Record.create({**base, "check_in": check_dt})
        else:
            rec = Record.search(
                [("employee_id", "=", emp.id), ("check_out", "=", check_dt)], limit=1
            ) or Record.search(
                [
                    ("employee_id", "=", emp.id),
                    ("check_out", "=", False),
                    ("check_in", "<=", check_dt),
                ],
                order="check_in desc",
                limit=1,
            )
            if rec and not rec.check_out:
                rec.write({"check_out": check_dt})
            elif not rec:
                rec = Record.create({**base, "check_in": check_dt, "check_out": check_dt})

        device.last_sync_at = fields.Datetime.now()
        return rec.with_env(self.env)

    # --- M55-F7: device health (AUT-WFM-04) ----------------------------------------
    @api.model
    def cron_check_device_health(self):
        """AUT-WFM-04 (M55-F7): every ACTIVE terminal whose last ingest sync
        is older than `fix.attendance.device_stale_hours`
        (ir.config_parameter, default 1.0 per AUT-WFM-04's "alert within 1 h")
        is flagged: a to-do for the attendance supervisors of its company, a
        chatter note and an event for the record. The terminal's own status is
        left to the supervisor: setting it offline here would refuse the
        terminal's FIRST revived punch (action_ingest_punch refuses an offline
        device), so an automatic offline would brick a recovered terminal.

        Note: last_sync_at advances only on ingest, so a quiet-but-healthy
        terminal with no traffic inside the interval also alerts — the
        interval (and a push-based heartbeat, if wanted) is the business's."""
        self = self.sudo()
        try:
            hours = float(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("fix.attendance.device_stale_hours", "1.0")
                or "1.0"
            )
        except ValueError:
            hours = 1.0
        cutoff = fields.Datetime.now() - timedelta(hours=max(hours, 0.0))
        stale = self.search([("active", "=", True)]).filtered(
            lambda d: (d.last_sync_at or d.create_date)
            and (d.last_sync_at or d.create_date) < cutoff
        )
        for device in stale:
            device._fix_flag_stale(hours)
        return len(stale)

    def _fix_flag_stale(self, hours):
        """One to-do per supervisor of the company (idempotent per device and
        per note) and one event for the record."""
        self.ensure_one()
        stale_since = self.last_sync_at or self.create_date
        summary = "Biometric terminal not syncing: %s" % self.name
        note = (
            "No ingest sync since %s (older than the configured %.1f h). Branch fallback: "
            "capture continues through the mobile app or manual entries with a reason."
            % (stale_since, hours)
        )
        already = self.env["mail.activity"].search(
            [("res_model", "=", self._name), ("res_id", "=", self.id), ("summary", "=", summary)]
        )
        if not already:
            group = self.env.ref(SUPERVISOR_GROUP, raise_if_not_found=False)
            users = (group.sudo().user_ids if group else self.env["res.users"]).filtered(
                lambda u: u.active and not u.share and self.company_id in u.company_ids
            )
            for user in users:
                self.activity_schedule(
                    "mail.mail_activity_data_todo", summary=summary, note=note, user_id=user.id
                )
            self.message_post(body="%s. %s" % (summary, note))
        publish(
            self.env,
            "attendance.device.stale",
            self._name,
            self.id,
            {
                "device": self.device_id,
                "last_sync_at": str(stale_since or ""),
                "stale_hours": hours,
                "branch": self.branch_id.name or "",
            },
        )
        return True


class FixAttendanceRecord(models.Model):
    """A check-in/out pair. Immutable once the period is LOCKED."""

    _name = "fix.attendance.record"
    _description = "Attendance Record"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
        # M55-3/8: what a user types is a manual entry; biometric and mobile
        # rows are written only by the device ingest and the technician API
        default="manual",
        required=True,
    )
    device_ref = fields.Char(
        string="Device Reference",
        help="INT-041 device id. The biometric TEMPLATE never lands here - "
        "S3 residency data routes through fix.identity.document",
    )
    device_id = fields.Many2one(
        "fix.biometric.device", string="Registered Device", readonly=True, index=True
    )
    manual_reason = fields.Char(
        string="Reason for Manual Entry", help="BRU-WFM-11: a manual entry states why."
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
        readonly=True,
    )
    approval_reason = fields.Char(string="Flag Reason", readonly=True)
    approved_by = fields.Many2one("res.users", string="Decided By", readonly=True, tracking=True)
    approved_at = fields.Datetime(string="Decided At", readonly=True)
    regularisation_ids = fields.One2many(
        "fix.attendance.regularisation", "record_id", string="Regularisations", readonly=True
    )
    retro_change = fields.Boolean(
        string="Changed After a Lock",
        readonly=True,
        help="Created or changed while its period was re-opened after a lock: payroll "
        "must carry the difference (FR-WFM-052).",
    )
    worked_hours = fields.Float(compute="_compute_hours", store=True)
    recorded_overtime_hours = fields.Float(
        string="Recorded Overtime",
        compute="_compute_hours",
        store=True,
        help="Hours worked beyond the statutory 8-hour day (s.100), counted per employee "
        "and day across every punch.",
    )
    overtime_hours = fields.Float(
        string="Payable Overtime",
        compute="_compute_hours",
        store=True,
        help="BRU-WFM-02: the recorded overtime that an APPROVED overtime request covers, "
        "at most 2 h a day (s.100/108), and none for an employee not eligible (s.108); "
        "capped per employee-week at the weekly limit less 48 h (M55-F23, s.102). "
        "This is what payroll pays.",
    )
    unapproved_overtime_hours = fields.Float(
        string="Unapproved Overtime", compute="_compute_hours", store=True
    )
    week_start = fields.Date(
        string="ISO Week Start", compute="_compute_hours", store=True, index=True
    )
    is_rest_day = fields.Boolean(
        string="Weekly Rest Day Call-In",
        default=False,
        readonly=True,
        help="BLA s.103/108: work performed on the scheduled weekly rest day. Set by the "
        "attendance supervisor (action_mark_rest_day), never by the employee.",
    )
    rest_day_hours = fields.Float(
        string="Rest-Day Worked Hours", compute="_compute_hours", store=True
    )
    holiday_hours = fields.Float(
        string="Public-Holiday Hours",
        compute="_compute_hours",
        store=True,
        help="FR-WFM-020: hours worked on a confirmed public holiday of the calendar.",
    )
    festival_hours = fields.Float(
        string="Festival-Holiday Hours",
        compute="_compute_hours",
        store=True,
        help="M55-F3/F12 (BLA s.118): hours worked on a confirmed FESTIVAL holiday of the "
        "calendar — the statutory festival days that count against the festival entitlement. "
        "What payroll reads for festival-day work.",
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
            ("rest_break_missing", "No s.101 Rest/Meal Interval"),
            ("spread_over_exceeded", "s.105 Spread-Over Exceeded"),
            ("rest_interval_violation", "Rest Between Shifts Below Company Minimum"),
            ("weekly_limit_exceeded", "Weekly Limit Exceeded"),
            ("annual_average_exceeded", "s.102 Annual Average Exceeded"),
        ],
        default="compliant",
        compute="_compute_compliance",
        store=True,
        tracking=True,
    )
    statutory_notes = fields.Char(
        string="Compliance Notes", compute="_compute_compliance", store=True
    )
    # T-08: the working-time rule version the record is valued and checked with
    wt_rule_id = fields.Many2one(
        "fix.working.time.rule",
        string="Working-Time Rule Version",
        compute="_compute_wt_rule",
        store=True,
        index=True,
    )

    # fields only a transition writes (M55-2, M55-3, M55-8, D5)
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "approval_state",
            "approved_by",
            "approved_at",
            "approval_reason",
            "geofence_result",
            "source",
            "device_ref",
            "device_id",
            "is_rest_day",
            "retro_change",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields() | {"geo_lat", "geo_long", "accuracy_m"}
        if self and self.approval_state == "rejected":
            locked |= {"check_in", "check_out", "employee_id"}
        if self:
            locked |= {"employee_id", "manual_reason"}
        return locked

    # ---- valuation ------------------------------------------------------------
    def _fix_day_key(self):
        self.ensure_one()
        if not (self.employee_id and self.check_in):
            return None
        return (self.employee_id.id, self.check_in.date())

    def _fix_day_records(self, key):
        """Every stored record of the employee-day (superuser: valuation must
        not depend on what the caller may read)."""
        emp_id, day = key
        start, end = _day_bounds(day)
        return (
            self.env["fix.attendance.record"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", emp_id),
                    ("check_in", ">=", start),
                    ("check_in", "<", end),
                ]
            )
        )

    def _fix_value_day(self, items, emp, day, company):
        """items: [(token, check_in, check_out, state, rest_day)] of one day.

        Returns {token: (worked, recorded_ot, payable_ot, rest, holiday, festival)}.
        The payable figure here still carries only the DAILY caps; the weekly
        payable ceiling (M55-F23) is applied by _compute_hours afterwards."""
        rows = sorted(
            (
                (ci, token, (co - ci).total_seconds() / 3600.0, state, rest)
                for token, ci, co, state, rest in items
                if ci and co and co > ci and state != "rejected"
            ),
            key=lambda r: (r[0], str(r[1])),
        )
        rest_day = any(r[4] for r in rows)
        # a confirmed holiday of the calendar; festival rows (BLA s.118: the
        # statutory festival days with wages) are valued separately so payroll
        # can pay festival-day work as such (M55-F3/F12)
        holiday_row = (
            self.env["fix.hr.holiday"]
            .sudo()
            .search(
                [("date", "=", day), ("company_id", "=", company.id), ("tentative", "=", False)],
                limit=1,
            )
            if company
            else self.env["fix.hr.holiday"]
        )
        holiday = bool(holiday_row)
        festival = bool(holiday_row and holiday_row.holiday_type == "festival")
        eligible = (
            bool(emp.sudo().overtime_eligible) if "overtime_eligible" in emp._fields else True
        )
        approved = 0.0
        if eligible:
            approved = sum(
                self.env["fix.overtime.request"]
                .sudo()
                .search(
                    [("employee_id", "=", emp.id), ("date", "=", day), ("state", "=", "approved")]
                )
                .mapped("approved_hours")
            )
        # T-07: the caps of the rule version in force that day
        rule = self.env["fix.working.time.rule"]._fix_values_for(company, day)
        cap = rule["daily_max_hours"] if rest_day else rule["daily_ot_cap_hours"]
        payable_left = min(approved, cap)
        out = {}
        cum = 0.0
        for _ci, token, span, state, _rest in rows:
            before, cum = cum, cum + span
            if rest_day:
                recorded = span
            else:
                recorded = max(cum - STANDARD_DAY_HOURS, 0.0) - max(
                    before - STANDARD_DAY_HOURS, 0.0
                )
            payable = 0.0
            if state in PAYABLE_STATES and payable_left > 0:
                payable = min(recorded, payable_left)
                payable_left -= payable
            out[token] = (
                round(span, 2),
                round(recorded, 2),
                round(payable, 2),
                round(span, 2) if rest_day else 0.0,
                round(span, 2) if holiday else 0.0,
                round(span, 2) if festival else 0.0,
            )
        return out

    @api.depends("check_in", "check_out", "approval_state", "is_rest_day", "employee_id")
    def _compute_hours(self):
        values = {}
        daily_payable = {}  # rec id -> payable after the DAILY caps only
        for rec in self:
            if rec.check_in:
                cdate = rec.check_in.date()
                rec.week_start = cdate - timedelta(days=cdate.weekday())
            else:
                rec.week_start = False
            key = rec._fix_day_key()
            result = None
            if key:
                if rec.id and isinstance(rec.id, int):
                    if key not in values:
                        day = rec._fix_day_records(key)
                        items = [
                            (r.id, r.check_in, r.check_out, r.approval_state, r.is_rest_day)
                            for r in day
                            if r.id not in self.ids
                        ] + [
                            (r.id, r.check_in, r.check_out, r.approval_state, r.is_rest_day)
                            for r in self
                            if r.id and r._fix_day_key() == key
                        ]
                        values[key] = rec._fix_value_day(
                            items, rec.employee_id, key[1], rec.company_id
                        )
                    result = values[key].get(rec.id)
                else:  # an unsaved form: value it with the stored records of its day
                    day = rec._fix_day_records(key)
                    items = [
                        (r.id, r.check_in, r.check_out, r.approval_state, r.is_rest_day)
                        for r in day
                        if r.id != rec._origin.id
                    ] + [("new", rec.check_in, rec.check_out, rec.approval_state, rec.is_rest_day)]
                    result = rec._fix_value_day(items, rec.employee_id, key[1], rec.company_id).get(
                        "new"
                    )
            worked, recorded, payable, rest, holiday, festival = result or (
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            )
            rec.worked_hours = worked
            rec.recorded_overtime_hours = recorded
            rec.rest_day_hours = rest
            rec.holiday_hours = holiday
            rec.festival_hours = festival
            if rec.id and isinstance(rec.id, int):
                daily_payable[rec.id] = payable
            else:  # an unsaved form has no week siblings to share a budget with
                rec.overtime_hours = payable
                rec.unapproved_overtime_hours = round(recorded - payable, 2)
        self._fix_apply_weekly_payable_cap(daily_payable)

    def _fix_weekly_payable_cap(self, company, day):
        """M55-F23: the employee-week's payable-overtime ceiling, from the
        working-time rule version in force: weekly_limit_hours - 48 h (s.102:
        the 48 h ordinary week). None while the rule sets no weekly limit —
        then payable overtime is capped per day only."""
        values = self.env["fix.working.time.rule"]._fix_values_for(company, day)
        weekly = values["weekly_limit_hours"]
        if not weekly:
            return None
        return max(weekly - STANDARD_WEEKLY_HOURS, 0.0)

    def _fix_apply_weekly_payable_cap(self, daily_payable):
        """Cap the batch's payable overtime per employee-week (M55-F23).

        The week's records are valued in check-in order; once the ceiling is
        spent the rest of the week's approved overtime stays recorded but not
        payable (unapproved_overtime_hours). Stored records of the same week
        that are NOT in this batch keep the payable figure they were valued
        with and consume the budget first (in check-in order among
        themselves); _fix_recompute_days re-values the whole week whenever a
        day of it changes, so the split never goes stale."""
        if not daily_payable:
            return
        groups = {}
        for rec in self:
            if rec.id and isinstance(rec.id, int) and rec.employee_id and rec.week_start:
                groups.setdefault((rec.employee_id.id, rec.week_start), []).append(rec)
        if not groups:
            return
        employees = sorted({e for e, _w in groups})
        weeks = {w for _e, w in groups}
        siblings = self.sudo().search(
            [
                ("employee_id", "in", employees),
                ("approval_state", "!=", "rejected"),
                ("check_in", ">=", fields.Datetime.to_datetime(min(weeks))),
                ("check_in", "<", fields.Datetime.to_datetime(max(weeks) + timedelta(days=7))),
            ]
        )
        by_week = {}
        for sib in siblings:
            if sib.week_start:
                by_week.setdefault((sib.employee_id.id, sib.week_start), []).append(sib)
        caps = {}
        for (_emp_id, week_start), recs in groups.items():
            for rec in recs:
                if rec.company_id.id not in caps:
                    caps[rec.company_id.id] = self._fix_weekly_payable_cap(
                        rec.company_id, week_start
                    )
        for (emp_id, week_start), recs in groups.items():
            cap = caps.get(recs[0].company_id.id)
            if cap is None:  # no weekly limit in force: the daily caps stand
                for rec in recs:
                    rec.overtime_hours = daily_payable.get(rec.id, 0.0)
                    rec.unapproved_overtime_hours = round(
                        rec.recorded_overtime_hours - rec.overtime_hours, 2
                    )
                continue
            week_recs = sorted(
                by_week.get((emp_id, week_start), []), key=lambda r: (r.check_in, r.id or 0)
            )
            batch_ids = {r.id for r in recs}
            # stored payable of the week that this batch is NOT re-valuing
            outside = [r for r in week_recs if r.id not in batch_ids]
            remaining = cap - sum(r.overtime_hours or 0.0 for r in outside)
            for rec in sorted(recs, key=lambda r: (r.check_in, r.id or 0)):
                payable = min(daily_payable.get(rec.id, 0.0), max(remaining, 0.0))
                remaining -= payable
                rec.overtime_hours = round(payable, 2)
                rec.unapproved_overtime_hours = round(
                    rec.recorded_overtime_hours - rec.overtime_hours, 2
                )

    def _fix_company(self):
        return self.company_id or self.env.company

    @api.depends(
        "worked_hours",
        "recorded_overtime_hours",
        "rest_day_hours",
        "week_start",
        "employee_id",
        "approval_state",
    )
    def _compute_weekly_totals(self):
        Rule = self.env["fix.working.time.rule"]
        for rec in self:
            day = rec.week_start or (rec.check_in and rec.check_in.date())
            limit = (
                Rule._fix_values_for(rec._fix_company(), day)["weekly_limit_hours"]
                or MAX_WEEKLY_HOURS
            )
            ot_cap = max(limit - STANDARD_WEEKLY_HOURS, 0.0)
            if not rec.employee_id or not rec.week_start:
                rec.weekly_worked_hours = rec.worked_hours or 0.0
                rec.weekly_ot_hours = rec.recorded_overtime_hours or 0.0
                rec.weekly_ot_limit_exceeded = (
                    rec.weekly_ot_hours > ot_cap or rec.weekly_worked_hours > limit
                )
                continue
            w_start_dt = fields.Datetime.to_datetime(rec.week_start)
            w_end_dt = fields.Datetime.to_datetime(rec.week_start + timedelta(days=7))
            siblings = self.sudo().search(
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
            w_daily_ot = round(sum(siblings.mapped("recorded_overtime_hours")), 2)
            if not rec.id and rec.approval_state != "rejected":
                w_worked = round(w_worked + (rec.worked_hours or 0.0), 2)
                w_daily_ot = round(w_daily_ot + (rec.recorded_overtime_hours or 0.0), 2)
            w_excess_ot = round(max(w_worked - STANDARD_WEEKLY_HOURS, 0.0), 2)
            rec.weekly_worked_hours = w_worked
            rec.weekly_ot_hours = max(w_daily_ot, w_excess_ot)
            rec.weekly_ot_limit_exceeded = rec.weekly_ot_hours > ot_cap or w_worked > limit

    @api.depends("check_in", "company_id")
    def _compute_wt_rule(self):
        Rule = self.env["fix.working.time.rule"]
        for rec in self:
            rec.wt_rule_id = (
                Rule._fix_rule_for(rec._fix_company(), rec.check_in.date())
                if rec.check_in
                else False
            )

    # ---- working-time checks (T-07; BLA s.100, s.101, s.102, s.105) ---------------
    def _fix_wt_intervals(self):
        """[(check_in, check_out)] worked that employee-day, this record's own
        (possibly unsaved) values included; rejected records are no work."""
        self.ensure_one()
        key = self._fix_day_key()
        if not key:
            return []
        out = [
            (r.check_in, r.check_out)
            for r in self._fix_day_records(key)
            if r.id != self._origin.id
            and r.approval_state != "rejected"
            and r.check_out
            and r.check_out > r.check_in
        ]
        if self.approval_state != "rejected" and self.check_out and self.check_out > self.check_in:
            out.append((self.check_in, self.check_out))
        return sorted(out)

    def _fix_wt_breaches(self):
        """[(code, mode, note)] of every working-time rule this record's day
        breaks, in priority order, under the rule version in force that day."""
        self.ensure_one()
        if not (self.check_in and self.employee_id):
            return []
        company = self._fix_company()
        day = self.check_in.date()
        rule = self.env["fix.working.time.rule"]._fix_values_for(company, day)
        # the version is recorded on the record (wt_rule_id, T-08), not in the note
        tag = ""
        out = []
        intervals = self._fix_wt_intervals()
        day_worked = sum((co - ci).total_seconds() / 3600.0 for ci, co in intervals)
        if rule["daily_max_hours"] and day_worked > rule["daily_max_hours"] + 1e-6:
            # M55-4 / A6: the limit is per employee-DAY, not per punch
            out.append(
                (
                    "daily_limit_exceeded",
                    "label",
                    "BLA 2006 s.100/108 breach: %.2fh worked that day exceeds the %.1fh daily "
                    "limit%s" % (day_worked, rule["daily_max_hours"], tag),
                )
            )
        # s.101: no stretch longer than N h without an interval of M minutes
        for after, minutes in (
            (rule["rest_interval_after_hours"], rule["rest_interval_minutes"]),
            (rule["rest_interval_after_hours_2"], rule["rest_interval_minutes_2"]),
        ):
            if not (after and minutes and intervals):
                continue
            gap = timedelta(minutes=minutes)
            longest, s_start, s_end = 0.0, intervals[0][0], intervals[0][1]
            for ci, co in intervals[1:]:
                if ci - s_end < gap:
                    s_end = max(s_end, co)
                    continue
                longest = max(longest, (s_end - s_start).total_seconds() / 3600.0)
                s_start, s_end = ci, co
            longest = max(longest, (s_end - s_start).total_seconds() / 3600.0)
            if longest > after + 1e-6:
                out.append(
                    (
                        "rest_break_missing",
                        rule["rest_interval_mode"],
                        "BLA s.101: %.2fh worked without an interval of %d minutes (needed "
                        "after %.1fh)%s" % (longest, minutes, after, tag),
                    )
                )
                break
        # s.105: spread-over, first check-in to last check-out of the day
        if rule["spread_over_max_hours"] and intervals:
            spread = (max(co for _ci, co in intervals) - intervals[0][0]).total_seconds() / 3600.0
            if spread > rule["spread_over_max_hours"] + 1e-6:
                out.append(
                    (
                        "spread_over_exceeded",
                        rule["spread_over_mode"],
                        "BLA s.105: the day spreads over %.2fh, above %.1fh%s"
                        % (spread, rule["spread_over_max_hours"], tag),
                    )
                )
        # the company's rest between shifts
        if rule["min_rest_hours"]:
            prev = self.sudo().search(
                [
                    ("employee_id", "=", self.employee_id.id),
                    ("id", "!=", self._origin.id or 0),
                    ("approval_state", "!=", "rejected"),
                    ("check_out", "<=", self.check_in),
                ],
                order="check_out desc",
                limit=1,
            )
            if prev and prev.check_out and prev.check_in.date() != day:
                rest_span = (self.check_in - prev.check_out).total_seconds() / 3600
                if 0 < rest_span < rule["min_rest_hours"]:
                    out.append(
                        (
                            "rest_interval_violation",
                            rule["short_rest_mode"],
                            "%.2fh rest between shifts is under the company minimum of %.1fh%s"
                            % (rest_span, rule["min_rest_hours"], tag),
                        )
                    )
        # the weekly limit (label)
        w_start = day - timedelta(days=day.weekday())
        siblings = self.sudo().search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("approval_state", "!=", "rejected"),
                ("check_in", ">=", fields.Datetime.to_datetime(w_start)),
                ("check_in", "<", fields.Datetime.to_datetime(w_start + timedelta(days=7))),
            ]
        )
        own = (self.worked_hours or 0.0) if self.approval_state != "rejected" else 0.0
        w_worked = round(sum(r.worked_hours for r in siblings if r.id != self._origin.id) + own, 2)
        weekly_limit = rule["weekly_limit_hours"] or MAX_WEEKLY_HOURS
        if w_worked > weekly_limit:
            out.append(
                (
                    "weekly_limit_exceeded",
                    "label",
                    "%.2fh worked in the week exceeds the weekly limit of %.1fh "
                    "(BLA s.102: 48h, 60h with overtime)%s" % (w_worked, weekly_limit, tag),
                )
            )
        # s.102: the calendar year's hours against the average a week
        if rule["annual_avg_weekly_hours"]:
            y_start, y_end = date(day.year, 1, 1), date(day.year + 1, 1, 1)
            year = self.sudo().search(
                [
                    ("employee_id", "=", self.employee_id.id),
                    ("approval_state", "!=", "rejected"),
                    ("id", "!=", self._origin.id or 0),
                    ("check_in", ">=", fields.Datetime.to_datetime(y_start)),
                    ("check_in", "<", fields.Datetime.to_datetime(y_end)),
                ]
            )
            total = sum(year.mapped("worked_hours")) + own
            ceiling = rule["annual_avg_weekly_hours"] * (y_end - y_start).days / 7.0
            if total > ceiling + 1e-6:
                out.append(
                    (
                        "annual_average_exceeded",
                        rule["annual_average_mode"],
                        "BLA s.102: %.1fh worked in %d exceeds an average of %.1fh a week "
                        "(%.1fh for the year)%s"
                        % (total, day.year, rule["annual_avg_weekly_hours"], ceiling, tag),
                    )
                )
        return out

    @api.depends("worked_hours", "employee_id", "check_in", "check_out", "approval_state")
    def _compute_compliance(self):
        for rec in self:
            breaches = rec._fix_wt_breaches()
            if breaches:
                rec.compliance_status = breaches[0][0]
                rec.statutory_notes = "; ".join(note for _c, _m, note in breaches)[:500]
                continue
            rec.compliance_status = "compliant"
            notes = "Standard shift compliant per BLA 2006"
            weekly = rec.weekly_worked_hours if rec.check_in and rec.employee_id else 0.0
            if (weekly or 0.0) > STANDARD_WEEKLY_HOURS:
                notes = "%.2fh in the week: above the 48h ordinary week (BLA s.102)" % weekly
            rec.statutory_notes = notes

    def _fix_assert_wt_blocks(self):
        """A rule version set to BLOCK refuses the attendance that breaks it,
        whatever its source: a block is the business's ruling."""
        for rec in self.sudo():
            if not rec.check_out or rec.approval_state == "rejected":
                continue
            blocked = [note for _c, mode, note in rec._fix_wt_breaches() if mode == "block"]
            if blocked:
                raise ValidationError(
                    "%s is refused by the working-time rules in force (%s): %s"
                    % (
                        rec.display_label,
                        rec.wt_rule_id.name or "default rules",
                        "; ".join(blocked),
                    )
                )

    @api.depends("employee_id", "check_in")
    def _compute_label(self):
        for rec in self:
            rec.display_label = "%s @ %s" % (
                rec.employee_id.name if rec.employee_id else "",
                rec.check_in or "",
            )

    # ---- integrity -------------------------------------------------------------
    @api.constrains("check_in", "check_out", "employee_id")
    def _check_no_overlap(self):
        # A6: duplicated punches over the same hours (live: 190 overlapping pairs)
        for rec in self:
            if rec.check_out and rec.check_out < rec.check_in:
                raise ValidationError("Check-out cannot precede check-in.")
            end = rec.check_out or rec.check_in
            candidates = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("employee_id", "=", rec.employee_id.id),
                    ("check_in", "<=", end),
                    ("check_in", ">=", rec.check_in - timedelta(days=2)),
                ]
            )
            other = candidates.filtered(
                lambda o, s=rec.check_in, e=end, co=rec.check_out: (
                    (o.check_in < e and (o.check_out or o.check_in) > s)
                    or (o.check_in == s and (not co or not o.check_out) and o.check_out != s)
                    or (o.check_in == s and o.check_out == co and e > s)
                )
            )[:1]
            if other:
                raise ValidationError(
                    "%s already has attendance %s to %s overlapping %s to %s."
                    % (
                        rec.employee_id.name,
                        other.check_in,
                        other.check_out or "open",
                        rec.check_in,
                        rec.check_out or "open",
                    )
                )

    def _fix_assert_period_open(self, company, day, verb):
        lock = _locked_lock(self.env, company, day)
        if lock:
            raise UserError("Cannot %s attendance in locked period %s" % (verb, lock.name))

    def _fix_reopened(self, company, day):
        if not day:
            return False
        return bool(
            self.env["fix.attendance.lock"]
            .sudo()
            .search_count(
                [
                    ("state", "=", "unlocked"),
                    ("company_id", "=", company.id),
                    ("period_start", "<=", day),
                    ("period_end", ">=", day),
                ]
            )
        )

    def _fix_recompute_days(self, keys):
        """Re-value every record of the given employee-days (split shifts,
        overtime approvals and holidays change the siblings' figures), and of
        their whole ISO weeks: the weekly payable-overtime ceiling (M55-F23)
        distributes one budget over the week, so a day that changes can move
        payable overtime onto or off its week-mates."""
        recs = self.env["fix.attendance.record"]
        weeks = {}
        for key in {k for k in keys if k}:
            emp_id, day = key
            recs |= self._fix_day_records(key)
            weeks[(emp_id, day - timedelta(days=day.weekday()))] = True
        for emp_id, week_start in weeks:
            recs |= self.sudo().search(
                [
                    ("employee_id", "=", emp_id),
                    ("check_in", ">=", fields.Datetime.to_datetime(week_start)),
                    ("check_in", "<", fields.Datetime.to_datetime(week_start + timedelta(days=7))),
                ]
            )
        recs = recs.sudo()
        if not recs:
            return
        for name in (
            "worked_hours",
            "recorded_overtime_hours",
            "overtime_hours",
            "unapproved_overtime_hours",
            "rest_day_hours",
            "holiday_hours",
            "festival_hours",
            "week_start",
            "compliance_status",
            "statutory_notes",
        ):
            self.env.add_to_compute(self._fields[name], recs)
        recs.flush_recordset()

    @api.model_create_multi
    def create(self, vals_list):
        trusted = self._fix_guard_open()
        for vals in vals_list:
            cin = vals.get("check_in")
            company = self.env["res.company"].browse(vals.get("company_id")) or self.env.company
            if cin:
                self._fix_assert_period_open(
                    company, fields.Datetime.to_datetime(cin).date(), "create"
                )
            if not trusted and not (vals.get("manual_reason") or "").strip():
                raise UserError(
                    "A manual attendance entry states its reason (BRU-WFM-11); it is then "
                    "approved by the line manager or an attendance officer."
                )
        recs = super().create(vals_list)
        if not trusted:
            name = self.env.user.name
            for rec in recs:
                # BRU-WFM-11: a manual entry is pending until someone else decides it
                rec._guarded().write(
                    {
                        "approval_state": "pending",
                        "approval_reason": "Manual entry by %s: %s" % (name, rec.manual_reason),
                    }
                )
        for rec in recs.sudo():
            if rec._fix_reopened(rec.company_id, rec.check_in.date()):
                rec._guarded().write({"retro_change": True})
        self._fix_recompute_days([r._fix_day_key() for r in recs])
        recs._fix_assert_wt_blocks()
        return recs

    def write(self, vals):
        content = set(vals) - {"message_follower_ids", "activity_ids", "message_ids"}
        if not content or not self:
            return super().write(vals)
        trusted = self._fix_guard_open()
        hours = {"check_in", "check_out", "employee_id"} & set(vals)
        new_cin = (
            fields.Datetime.to_datetime(vals["check_in"]).date() if vals.get("check_in") else None
        )
        old_keys = []
        changed = self.browse()
        for rec in self:
            if not rec.check_in:  # an unsaved record (the form's onchange)
                continue
            old_keys.append(rec._fix_day_key())
            # P08-M02-T05: the lock. Payroll calculates on LOCKED periods only;
            # the NEW date is checked too (C7: a record re-dated into January).
            rec._fix_assert_period_open(rec.company_id, rec.check_in.date(), "edit")
            if new_cin:
                rec._fix_assert_period_open(rec.company_id, new_cin, "move")
            if not trusted and hours:
                differs = [n for n in hours if rec._fix_guard_differs(n, vals[n], rec[n])]
                if not differs:
                    continue
                if "employee_id" in differs:
                    raise UserError(
                        "Attendance is not moved to another employee: record it for them."
                    )
                if rec.approval_state == "rejected":
                    raise UserError(
                        "%s was rejected; a rejected clock-in is not re-opened by editing it."
                        % rec.display_label
                    )
                changed |= rec
        res = super().write(vals)
        if changed:
            name = self.env.user.name
            for rec in changed:
                # a decided record whose hours change is no longer what was decided
                rec.regularisation_ids.sudo()._fix_void("the hours changed after it was raised")
                rec._guarded().write(
                    {
                        "approval_state": "pending",
                        "approval_reason": "Regularisation: hours changed by %s" % name,
                        "approved_by": False,
                        "approved_at": False,
                    }
                )
        for rec in self.sudo():
            if (
                rec.check_in
                and not rec.retro_change
                and rec._fix_reopened(rec.company_id, rec.check_in.date())
            ):
                rec._guarded().write({"retro_change": True})
        if {"check_in", "check_out", "employee_id", "approval_state", "is_rest_day"} & set(vals):
            self._fix_recompute_days(old_keys + [r._fix_day_key() for r in self if r.check_in])
        if hours:
            self._fix_assert_wt_blocks()
        return res

    def unlink(self):
        keys = []
        for rec in self:
            # check_in is required (NOT NULL): every stored record has one.
            rec._fix_assert_period_open(rec.company_id, rec.check_in.date(), "delete")
            keys.append(rec._fix_day_key())
        res = super().unlink()
        self.env["fix.attendance.record"]._fix_recompute_days(keys)
        return res

    # --- AUT-WFM-02: deciding a pending record ------------------------------------
    def _fix_open_regularisation(self):
        self.ensure_one()
        return self.sudo().regularisation_ids.filtered(lambda r: r.state == "open")[:1]

    def action_request_regularisation(self, note=None):
        """Route every pending record to its decider: the line manager first,
        then the attendance officers. The requester, the record's creator and
        the employee never decide it."""
        Reg = self.env["fix.attendance.regularisation"].sudo()
        for rec in self:
            if rec.approval_state != "pending":
                raise UserError("%s is not pending approval." % rec.display_label)
            if rec._fix_open_regularisation():
                raise UserError("%s is already awaiting a decision." % rec.display_label)
            reg = Reg.create(
                {
                    "record_id": rec.id,
                    "reason": "; ".join(p for p in (rec.approval_reason, note) if p),
                }
            )
            # as superuser in the caller's name: the caller is the requester
            # (excluded from deciding) but holds no write on the regularisation
            reg.action_request_approval()
        return True

    def _fix_decide_direct(self, state, note):
        """Superuser only (data repair, legacy imports): decide without routing."""
        for rec in self:
            if rec.approval_state != "pending":
                raise UserError(
                    "Attendance %s is not pending approval (it is %s)"
                    % (rec.display_label, rec.approval_state)
                )
            rec.regularisation_ids._fix_void("decided directly by the superuser")
            rec._fix_apply_decision(state, self.env.user, note)

    def _fix_apply_decision(self, state, user, note):
        self.ensure_one()
        self._guarded().write(
            {"approval_state": state, "approved_by": user.id, "approved_at": fields.Datetime.now()}
        )
        self.message_post(body=note)
        if state == "approved":
            publish(
                self.env,
                "attendance.approved",
                "fix.attendance.record",
                self.id,
                {"employee": self.employee_id.name, "reason": self.approval_reason},
            )
        else:
            publish(
                self.env,
                "attendance.rejected",
                "fix.attendance.record",
                self.id,
                {"employee": self.employee_id.name, "reason": self.approval_reason},
            )

    def action_approve(self):
        """Accept a pending record: it counts as worked time. Decided from the
        approver's task (the workspace button decides the caller's own task)."""
        if self.env.su:
            return self._fix_decide_direct("approved", "Flagged clock-in approved")
        for rec in self:
            reg = rec._fix_open_regularisation()
            if not reg:
                raise UserError(
                    "%s has not been routed for a decision: use Request Approval."
                    % rec.display_label
                )
            reg.with_env(self.env).action_inbox_approve()
        return True

    def action_reject(self, reason=""):
        """Refuse a pending record: it stays recorded but is no worked time."""
        if self.env.su:
            return self._fix_decide_direct(
                "rejected", "Flagged clock-in rejected: %s" % (reason or "no reason given")
            )
        if not (reason or "").strip():
            raise UserError("State why this attendance is rejected.")
        for rec in self:
            reg = rec._fix_open_regularisation()
            if not reg:
                raise UserError(
                    "%s has not been routed for a decision: use Request Approval."
                    % rec.display_label
                )
            reg.with_env(self.env).action_inbox_reject(reason=reason)
        return True

    @api.model
    def cron_route_pending_attendance(self):
        """AUT-WFM-05: every pending record without an open regularisation is
        routed (idempotent; a record nobody can decide is left and retried)."""
        self = self.sudo()
        pending = self.search([("approval_state", "=", "pending")])
        routed = 0
        for rec in pending:
            if rec._fix_open_regularisation():
                continue
            try:
                with self.env.cr.savepoint():
                    rec.action_request_regularisation()
                routed += 1
            except UserError:
                continue
        return routed

    # --- M55-F9 (part): the ordinary exceptions the roster can prove -------------
    @api.model
    def cron_detect_attendance_exceptions(self):
        """FR-WFM-011 (M55-F9, part): end-of-day detection over YESTERDAY's
        Dhaka business day — a still-open shift (missing punch-out), a late
        arrival and an early departure against the rostered shift. Each is
        flagged on the attendance record (approval_state pending with its
        reason), so the routing cron carries it to a decider exactly like the
        capture flags. Absence-without-leave and fraud signals are DEFERRED:
        they need more than the roster and the punches hold."""
        day = fields.Date.context_today(self.with_context(tz="Asia/Dhaka")) - timedelta(days=1)
        return self._fix_detect_day_exceptions(day)

    @api.model
    def _fix_detect_day_exceptions(self, day=None):
        """Detect the ordinary exceptions of one Dhaka day. Idempotent: only
        records still `not_required` are flagged, so a decided or already
        flagged record is never re-flagged."""
        if day is None:
            day = fields.Date.context_today(self.with_context(tz="Asia/Dhaka"))
        day = fields.Date.to_date(day)
        start_utc, end_utc = _dhaka_day_bounds_utc(day)
        records = self.sudo().search([("check_in", ">=", start_utc), ("check_in", "<", end_utc)])
        slots = self.env["fix.roster.slot"].sudo().search([("date", "=", day)])
        by_emp = {}
        for rec in records:
            by_emp.setdefault(rec.employee_id.id, []).append(rec)
        reasons = {}  # record -> [reason, ...]: one flagged record can be late AND early
        for slot in slots.filtered(lambda s: not s.on_leave):
            emp_recs = sorted(by_emp.get(slot.employee_id.id, []), key=lambda r: r.check_in)
            if not emp_recs:
                continue  # a rostered day with no punch at all is the AWOL case: DEFERRED
            shift = slot.shift_id
            first, last = emp_recs[0], emp_recs[-1]
            crosses_midnight = shift.end_hour <= shift.start_hour
            # late arrival: the first punch is after the rostered start
            if first.check_in and first.approval_state == "not_required":
                late_by = _dhaka_wall(first.check_in) - shift.start_hour
                if late_by > 1.0 / 60:  # more than a minute: a same-second punch is on time
                    reasons.setdefault(first.id, []).append(
                        "Late arrival (FR-WFM-011): first punch %.2f:00 Dhaka is %.1f h after "
                        "the rostered %.2f:00 start of %s"
                        % (_dhaka_wall(first.check_in), late_by, shift.start_hour, shift.name)
                    )
            # early departure: the last punch-out is before the rostered end
            # (only for shifts that end on the same calendar day — a shift that
            # crosses midnight ends tomorrow and yesterday's records cannot
            # prove it)
            if last.check_out and last.approval_state == "not_required" and not crosses_midnight:
                early_by = shift.end_hour - _dhaka_wall(last.check_out)
                if early_by > 1.0 / 60:
                    reasons.setdefault(last.id, []).append(
                        "Early departure (FR-WFM-011): last punch-out %.2f:00 Dhaka is %.1f h "
                        "before the rostered %.2f:00 end of %s"
                        % (_dhaka_wall(last.check_out), early_by, shift.end_hour, shift.name)
                    )
            # missing punch-out: a shift left open after its day ended
            for rec in emp_recs:
                if not rec.check_out and rec.approval_state == "not_required":
                    reasons.setdefault(rec.id, []).append(
                        "Missing punch-out (FR-WFM-011): checked in at %s and the day has "
                        "ended with no check-out" % rec.check_in
                    )
        flagged = self.browse([rid for rid in reasons if rid])
        for rec in flagged:
            rec._guarded().write(
                {
                    "approval_state": "pending",
                    "approval_reason": "; ".join(reasons[rec.id]),
                }
            )
        if flagged:
            flagged._fix_recompute_days([r._fix_day_key() for r in flagged])
        return len(flagged)

    # --- M55-F7: exception ageing before the payroll cut-off ----------------------
    @api.model
    def cron_escalate_pending_exceptions(self):
        """AUT-WFM-06 (M55-F7): escalate attendance exceptions still pending
        once the payroll cut-off is close. The window is the company setting
        `fix_attendance_exception_escalate_days` (N days before the next
        payroll period starts; 0, the default, keeps it off — the figure is
        the business's). Inside the window every still-pending record gets a
        to-do for the attendance supervisors of its company and an event for
        the record. Idempotent: one open escalation per record."""
        self = self.sudo()
        today = fields.Date.context_today(self.with_context(tz="Asia/Dhaka"))
        Period = self.env.get("fix.payroll.period", None)
        escalated = 0
        for company in self.env["res.company"].search([]):
            days = company.fix_attendance_exception_escalate_days or 0
            if not days or Period is None:
                continue
            domain = [("period_start", ">=", today)]
            if "company_id" in Period._fields:
                domain.append(("company_id", "=", company.id))
            nxt = Period.search(domain, order="period_start", limit=1)
            if not nxt:
                continue
            window_from = nxt.period_start - timedelta(days=days)
            if not (window_from <= today <= nxt.period_start):
                continue
            pending = self.search(
                [("approval_state", "=", "pending"), ("company_id", "=", company.id)]
            )
            for rec in pending:
                escalated += 1 if rec._fix_escalate_pending(nxt) else 0
        return escalated

    def _fix_escalate_pending(self, payroll_period):
        """One to-do per supervisor of the company and one event, once."""
        self.ensure_one()
        summary = "Attendance exception pending before payroll %s" % payroll_period.name
        open_escalations = self.env["mail.activity"].search(
            [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
                ("summary", "=", summary),
            ]
        )
        if open_escalations:
            return False
        note = (
            "%s (%s) is still pending approval and payroll period %s starts %s: decide it "
            "before the lock."
            % (
                self.display_label,
                self.approval_reason or "flagged",
                payroll_period.name,
                payroll_period.period_start,
            )
        )
        group = self.env.ref(SUPERVISOR_GROUP, raise_if_not_found=False)
        users = (group.sudo().user_ids if group else self.env["res.users"]).filtered(
            lambda u: u.active and not u.share and self.company_id in u.company_ids
        )
        for user in users:
            self.activity_schedule(
                "mail.mail_activity_data_todo", summary=summary, note=note, user_id=user.id
            )
        self.message_post(body="%s. %s" % (summary, note))
        publish(
            self.env,
            "attendance.exception.escalated",
            self._name,
            self.id,
            {
                "employee": self.employee_id.name,
                "reason": self.approval_reason,
                "payroll_period": payroll_period.name,
                "cut_off": str(payroll_period.period_start),
            },
        )
        return True

    def _fix_assert_supervisor(self):
        if not (self.env.su or self.env.user.has_group(SUPERVISOR_GROUP)):
            raise AccessError("Only an Attendance Supervisor marks a weekly rest day.")
        mine = self.filtered(lambda r: r.employee_id.sudo().user_id == self.env.user)
        if mine and not self.env.su:
            raise UserError("You do not mark your own attendance as a rest-day call-in.")

    def action_mark_rest_day(self):
        """BLA s.103: the supervisor records that this was the weekly rest day."""
        self._fix_assert_supervisor()
        for rec in self:
            rec._fix_assert_period_open(rec.company_id, rec.check_in.date(), "edit")
            rec._guarded().write({"is_rest_day": True})
        self._fix_recompute_days([r._fix_day_key() for r in self])
        return True

    def action_clear_rest_day(self):
        self._fix_assert_supervisor()
        for rec in self:
            rec._fix_assert_period_open(rec.company_id, rec.check_in.date(), "edit")
            rec._guarded().write({"is_rest_day": False})
        self._fix_recompute_days([r._fix_day_key() for r in self])
        return True

    @api.model
    def _fix_revalue_open_periods(self):
        """Data hook (upgrade, idempotent): re-value every record outside a
        locked period under the per-day, approved-overtime rules. A locked
        period keeps the figures it was locked and paid with."""
        Record = self.sudo()
        keys = set()
        for rec in Record.search([]):
            if not _locked_lock(self.env, rec.company_id, rec.check_in.date()):
                keys.add(rec._fix_day_key())
        Record._fix_recompute_days(keys)
        return len(keys)

    @api.model
    def pending_in_period(self, period_start, period_end, company=None):
        """Flagged clock-ins of [period_start, period_end] still pending approval
        (BRU-WFM-01: a period is locked and paid only on VERIFIED attendance).

        Searched as superuser: a caller who cannot see a pending record (another
        operating unit) must not lock or pay over it (C8)."""
        domain = [
            ("approval_state", "=", "pending"),
            ("check_in", ">=", fields.Datetime.to_datetime(period_start)),
            ("check_in", "<", fields.Datetime.to_datetime(period_end + timedelta(days=1))),
        ]
        if company:
            domain.append(("company_id", "=", company.id))
        return self.sudo().search(domain, order="check_in")

    # --- M55-F3/F4: the figures payroll (cd_payroll_bd) reads ---------------------
    @api.model
    def _fix_payroll_period_domain(self, employee, date_from, date_to):
        """Records of `employee` checking in inside [date_from, date_to]
        (superuser read: payroll must see every operating unit). The window is
        the same one pending_in_period uses, so both sides of the payroll
        interface agree on the period."""
        end = fields.Date.to_date(date_to) + timedelta(days=1)
        return [
            ("employee_id", "=", employee.id),
            ("check_in", ">=", fields.Datetime.to_datetime(date_from)),
            ("check_in", "<", fields.Datetime.to_datetime(end)),
        ]

    @api.model
    def _fix_payroll_rest_day_hours(self, employee, date_from, date_to):
        """APPROVED weekly rest-day worked hours of `employee` in the period
        (BLA s.103/108): the rest_day_hours of decided records only."""
        records = self.sudo().search(
            [
                *self._fix_payroll_period_domain(employee, date_from, date_to),
                ("approval_state", "in", PAYABLE_STATES),
            ]
        )
        return round(sum(records.mapped("rest_day_hours")), 2)

    @api.model
    def _fix_payroll_holiday_hours(self, employee, date_from, date_to):
        """APPROVED public-holiday worked hours of `employee` in the period
        (any confirmed holiday of the calendar; FR-WFM-020)."""
        records = self.sudo().search(
            [
                *self._fix_payroll_period_domain(employee, date_from, date_to),
                ("approval_state", "in", PAYABLE_STATES),
            ]
        )
        return round(sum(records.mapped("holiday_hours")), 2)

    @api.model
    def _fix_payroll_festival_hours(self, employee, date_from, date_to):
        """APPROVED FESTIVAL-holiday worked hours of `employee` in the period
        (BLA s.118: the statutory festival days). This is the figure the
        2-days'-wages / substitute-holiday ruling (OWNER) prices."""
        records = self.sudo().search(
            [
                *self._fix_payroll_period_domain(employee, date_from, date_to),
                ("approval_state", "in", PAYABLE_STATES),
            ]
        )
        return round(sum(records.mapped("festival_hours")), 2)

    def action_checkout(self):
        for rec in self:
            if rec.check_out:
                raise UserError("Already checked out")
            if not (
                self.env.su
                or rec.employee_id.sudo().user_id == self.env.user
                or self.env.user.has_group(SUPERVISOR_GROUP)
            ):
                raise AccessError("Only the employee clocks out of their own attendance.")
            # the clock-out is the current time, not a typed one
            rec._guarded().write({"check_out": fields.Datetime.now()})
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
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
        readonly=True,
    )
    locked_by_id = fields.Many2one("res.users", string="Locked By", readonly=True)
    locked_at = fields.Datetime(readonly=True)
    unlocked_by_id = fields.Many2one("res.users", string="Re-opened By", readonly=True)
    unlocked_at = fields.Datetime(string="Re-opened At", readonly=True)
    unlock_reason = fields.Text(string="Reason for Re-opening", readonly=True)
    unlock_count = fields.Integer(readonly=True)
    retro_flag = fields.Boolean(
        string="Re-locked After a Re-opening",
        readonly=True,
        help="The period was re-opened and locked again: records flagged 'Changed After a "
        "Lock' carry differences payroll must pick up (FR-WFM-052).",
    )
    payroll_paid = fields.Boolean(
        string="Re-opened After Payment",
        readonly=True,
        help="Re-opened after payroll paid the period: every change becomes a forward "
        "adjustment (fix.attendance.adjustment) for the next payroll (FR-WFM-052).",
    )
    baseline_taken = fields.Boolean(
        string="Paid Figures Recorded",
        readonly=True,
        help="What payroll paid for each employee-day was recorded at the first re-opening "
        "after payment; corrections are measured against it.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "locked_by_id",
            "locked_at",
            "unlocked_by_id",
            "unlocked_at",
            "unlock_reason",
            "unlock_count",
            "retro_flag",
            "payroll_paid",
            "baseline_taken",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {"period_start", "period_end", "company_id", "operating_unit_id"}
        return locked

    @api.constrains("period_start", "period_end", "company_id")
    def _check_one_lock_per_period(self):
        # C10: duplicate locks for one period (live: two September locks)
        for rec in self:
            if rec.period_end < rec.period_start:
                raise ValidationError("A lock period cannot end before it starts.")
            other = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("company_id", "=", rec.company_id.id),
                    ("period_start", "<=", rec.period_end),
                    ("period_end", ">=", rec.period_start),
                ],
                limit=1,
            )
            if other:
                raise ValidationError(
                    "%s already covers %s to %s for %s: one lock per period."
                    % (other.name, other.period_start, other.period_end, rec.company_id.name)
                )

    def _fix_check_lockable(self, require_past=True):
        """The gate, wherever the state becomes 'locked' (P4). A trusted data
        load may lock a running period, but never over pending clock-ins."""
        for rec in self:
            if require_past and rec.period_end >= fields.Date.today():
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

    @api.model_create_multi
    def create(self, vals_list):
        locks = super().create(vals_list)
        # a trusted caller (data load) creating a lock already 'locked' passes
        # the same gate as action_lock (C3: born locked over pending clock-ins)
        locks.filtered(lambda r: r.state == "locked")._fix_check_lockable(require_past=False)
        return locks

    def write(self, vals):
        if self and vals.get("state") == "locked" and self._fix_guard_open():
            self.filtered(lambda r: r.state != "locked" and r.period_end)._fix_check_lockable(
                require_past=False
            )
        if (
            self
            and {"period_start", "period_end", "company_id"} & set(vals)
            and self.filtered(lambda r: r.state != "draft" and r.period_start)
        ):
            raise UserError("A lock's period is fixed once it has been locked.")
        return super().write(vals)

    def action_lock(self):
        if not (self.env.su or self.env.user.has_group(SUPERVISOR_GROUP)):
            raise AccessError("Only an Attendance Supervisor locks an attendance period.")
        for rec in self:
            if rec.state == "locked":
                raise UserError("%s is already locked." % rec.name)
            rec._fix_check_lockable()
            vals = {
                "state": "locked",
                "locked_by_id": self.env.user.id,
                "locked_at": fields.Datetime.now(),
            }
            if rec.state == "unlocked":
                vals["retro_flag"] = True
            rec._guarded().write(vals)
            publish(
                self.env, "attendance.locked", "fix.attendance.lock", rec.id, {"period": rec.name}
            )

    def _fix_payroll_taken(self):
        """Payroll periods of the lock's company that have taken this
        attendance (verified the lock, calculated, approved or paid)."""
        self.ensure_one()
        if "fix.payroll.period" not in self.env:
            return self.env["res.company"]
        Period = self.env["fix.payroll.period"].sudo()
        domain = [
            ("period_start", "<=", self.period_end),
            ("period_end", ">=", self.period_start),
            ("state", "not in", PAYROLL_OPEN_STATES),
        ]
        if "company_id" in Period._fields:
            domain.append(("company_id", "=", self.company_id.id))
        return Period.search(domain)

    def _fix_after_reopen(self):
        """Hook (fix_attendance_adjustment): record what payroll paid."""
        return True

    def action_unlock(self, reason=None):
        """Re-open a locked period: a separate role (SOD-28) and a reason.
        Never while payroll is between verification and payment (C4, C5, C6);
        after payment, every change becomes a forward adjustment (FR-WFM-052)."""
        if not (self.env.su or self.env.user.has_group(LOCK_MANAGER_GROUP)):
            raise AccessError(
                "Only an Attendance Lock Manager re-opens a locked period (SOD-28): the "
                "supervisor who maintains rosters and devices does not."
            )
        if not (reason or "").strip():
            raise UserError("State why the attendance period is re-opened.")
        for rec in self:
            if rec.state != "locked":
                raise UserError(
                    "Only a locked period is re-opened (%s is %s)." % (rec.name, rec.state)
                )
            taken = rec._fix_payroll_taken()
            running = taken.filtered(lambda p: p.state not in PAYROLL_PAID_STATES)
            if running:
                raise UserError(
                    "%s cannot be re-opened: payroll %s has already taken it (%s) and has not "
                    "paid it yet. Once it is paid, a correction is carried into the next "
                    "period as an approved adjustment."
                    % (
                        rec.name,
                        ", ".join(running.mapped("name")),
                        ", ".join(running.mapped("state")),
                    )
                )
            paid = bool(taken)
            rec._guarded().write(
                {
                    "state": "unlocked",
                    "unlocked_by_id": self.env.user.id,
                    "unlocked_at": fields.Datetime.now(),
                    "unlock_reason": reason,
                    "unlock_count": rec.unlock_count + 1,
                    "payroll_paid": paid or rec.payroll_paid,
                }
            )
            if paid:
                rec._fix_after_reopen()
            rec.message_post(
                body="Re-opened: %s%s"
                % (
                    reason,
                    " (after payment: changes become forward adjustments)" if paid else "",
                )
            )
            publish(
                self.env,
                "attendance.unlocked",
                "fix.attendance.lock",
                rec.id,
                {"period": rec.name, "reason": reason},
            )

    def action_export_form10_overtime_register(self):
        """BLR 2015 Rule 102 / Form 10: Statutory Overtime Register using 208-hour divisor."""
        from decimal import Decimal

        from libs.py.payroll_engine import OT_DIVISOR_HOURS, overtime_amount

        self.ensure_one()
        # The register prices overtime from each worker's basic wage, which
        # is HR/payroll data (A09 audit M21-4): the attendance supervisor's run
        # reads contracts and wages through sudo, so the run itself is the
        # supervisor's only.
        if not (self.env.su or self.env.user.has_group(SUPERVISOR_GROUP)):
            raise AccessError("Only an Attendance Supervisor may export the Form 10 register.")
        # C11: the register carries PAYABLE overtime (approved, capped), from
        # decided records only
        records = (
            self.env["fix.attendance.record"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("approval_state", "in", PAYABLE_STATES),
                    ("check_in", ">=", fields.Datetime.to_datetime(self.period_start)),
                    (
                        "check_in",
                        "<",
                        fields.Datetime.to_datetime(self.period_end + timedelta(days=1)),
                    ),
                ],
                order="employee_id, check_in",
            )
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
            contract = (
                self.env["fix.employment.contract"]
                .sudo()
                .search(
                    [("employee_id", "=", emp_id), ("state", "=", "active")],
                    order="joining_date desc, id desc",
                    limit=1,
                )
            )
            emp = self.env["hr.employee"].sudo().browse(emp_id)
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

    # M55-F16: operating_unit_id was re-declared here while cd_service_order's
    # own fix.work.order model already defines it — M02's declaration stands.

    def action_check_technician_availability(self):
        # Every record is checked: an early `return True` inside the loop used
        # to wave the rest of a multi-record call through unchecked. The roster,
        # leave and attendance are read as superuser: a dispatcher who cannot
        # read a technician's attendance must not be told he is available.
        for rec in self:
            if not rec.technician_id:
                continue
            # the night-consent recheck (_fix_recheck_night_consent) decides on
            # the context date; reading the UTC clock here let a withdrawn
            # night consent pass after 18:00 UTC (00:00-06:00 Dhaka) — the two
            # frames must agree, or the M55 control fails open six hours a day.
            day = fields.Date.context_today(rec)
            domain = [("employee_id", "=", rec.technician_id.id), ("date", "=", day)]
            company = rec.technician_id.sudo().company_id or self.env.company
            if company.fix_roster_dispatch_published_only:
                # BRU-WFM-12 (company setting): dispatch reads the PUBLISHED roster only
                domain.append(("state", "=", "published"))
            slot = self.env["fix.roster.slot"].sudo().search(domain, limit=1)
            if not slot:
                raise UserError(
                    "M55 availability: %s has no roster slot for %s — "
                    "assign from the roster, not the calendar" % (rec.technician_id.name, day)
                )
            on_leave = slot.on_leave or self.env["fix.leave.request"].sudo().search_count(
                [
                    ("employee_id", "=", rec.technician_id.id),
                    ("state", "=", "approved"),
                    ("date_from", "<=", day),
                    ("date_to", ">=", day),
                ]
            )
            if on_leave:
                raise UserError(
                    "M55 availability: %s is on approved leave for %s"
                    % (rec.technician_id.name, day)
                )
            if slot.night_consent_flag:
                raise UserError(
                    "M55 availability: %s withdrew her night-work consent (BLA s.109); the "
                    "%s slot of %s is awaiting removal."
                    % (rec.technician_id.name, slot.shift_id.name, day)
                )
            # BRU-WFM-15: a suspended employee is not dispatched (read live)
            if "fix.hr.disciplinary.case" in self.env and self.env[
                "fix.hr.disciplinary.case"
            ].sudo().search_count(
                [
                    ("employee_id", "=", rec.technician_id.id),
                    ("suspended", "=", True),
                    ("suspended_from", "<=", day),
                    ("suspended_until", ">=", day),
                ]
            ):
                raise UserError(
                    "M55 availability: %s is suspended on %s (BLA s.23/24)"
                    % (rec.technician_id.name, day)
                )
            rejected_punch = (
                self.env["fix.attendance.record"]
                .sudo()
                .search(
                    [
                        ("employee_id", "=", rec.technician_id.id),
                        ("check_in", ">=", fields.Datetime.to_datetime(day)),
                        ("check_in", "<", fields.Datetime.to_datetime(day + timedelta(days=1))),
                        ("approval_state", "=", "rejected"),
                    ],
                    limit=1,
                )
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


class ResCompanyAttendanceOps(models.Model):
    """M55-F7 (AUT-WFM-06): the exception-ageing window."""

    _inherit = "res.company"

    fix_attendance_exception_escalate_days = fields.Integer(
        string="Escalate Pending Exceptions N Days Before Payroll",
        default=0,
        help="AUT-WFM-06: this many days before the next payroll period starts, every "
        "attendance exception still pending is escalated to the attendance supervisors. "
        "0 (the default) keeps the escalation off. The figure is the business's (OWNER).",
    )


class FixLeaveRequestPayrollFigures(models.Model):
    """M55-F4 (attendance side): the approved unpaid-leave days payroll reads.

    The `is_unpaid` flag on fix.leave.type arrives with the B2b leave-catalogue
    work; it is read defensively so this helper works before and after it
    lands (before it lands no type is unpaid and the figure is honestly 0)."""

    _inherit = "fix.leave.request"

    @api.model
    def _fix_payroll_unpaid_leave_days(self, employee, date_from, date_to):
        """APPROVED unpaid-leave DAYS of `employee` inside [date_from,
        date_to]: only the days of each approved leave that fall in the
        period (a leave spanning the boundary is split at it). Superuser
        read: payroll must see every operating unit."""
        date_from = fields.Date.to_date(date_from)
        date_to = fields.Date.to_date(date_to)
        leaves = self.sudo().search(
            [
                ("employee_id", "=", employee.id),
                ("state", "=", "approved"),
                ("date_from", "<=", date_to),
                ("date_to", ">=", date_from),
            ]
        )
        days = 0.0
        for leave in leaves:
            leave_type = leave.leave_type_id
            if hasattr(leave_type, "_fix_is_unpaid"):
                # cd_hr_core's predicate (the is_unpaid flag, falling back to
                # the seeded code) is the one source of truth
                unpaid = leave_type._fix_is_unpaid()
            else:
                unpaid = "is_unpaid" in leave_type._fields and bool(leave_type.is_unpaid)
            if not unpaid:
                continue
            overlap = (min(leave.date_to, date_to) - max(leave.date_from, date_from)).days + 1
            days += max(overlap, 0)
        return days


class HrEmployeeLeaveBalanceBatch(models.Model):
    """M55-F17: the leave-balances pack's batch reader for the s.117 ledger.

    Computes what hr.employee._fix_unused_annual_leave_days (cd_hr_core)
    computes, but reads the annual leave types, the annual leave requests and
    the employment contracts ONCE for the whole batch instead of once per
    employee — the pack's 504-employee projection envelope (T-12 ≤ 500 ms).
    The accrual BASIS stays cd_hr_core's: each service year is measured with
    the employee's own _fix_leave_days_worked, so a change there (B2b's
    worked-days basis) flows through unchanged. test_a09_erp_b4_ops.py keeps
    the batch and the single ledgers equal."""

    _inherit = "hr.employee"

    def _fix_unused_annual_leave_days_batch(self, as_of):
        from dateutil.relativedelta import relativedelta
        from odoo.addons.cd_hr_core.models.fix_leave_controls import (
            ANNUAL_LEAVE_DAYS_PER_EARNED_DAY,
        )

        result = {emp.id: 0.0 for emp in self}
        if not self:
            return result
        emp_ids = self.ids
        annual_types = {
            t.company_id.id: t
            for t in self.env["fix.leave.type"].sudo().search([("code", "=", "annual")])
        }
        leaves = (
            self.env["fix.leave.request"]
            .sudo()
            .search(
                [
                    ("employee_id", "in", emp_ids),
                    ("leave_type_id.code", "=", "annual"),
                    ("state", "in", ("approved", "rejected")),
                ]
            )
        )
        by_emp = {}
        for leave in leaves:
            by_emp.setdefault(leave.employee_id.id, []).append(leave)
        contract_joins = {}
        if "fix.employment.contract" in self.env:
            contracts = (
                self.env["fix.employment.contract"]
                .sudo()
                .search([("employee_id", "in", emp_ids), ("state", "!=", "draft")])
            )
            for contract in contracts:
                if contract.joining_date:
                    contract_joins.setdefault(contract.employee_id.id, []).append(
                        contract.joining_date
                    )
        for emp in self:
            annual = annual_types.get(emp.sudo().company_id.id)
            if not annual:
                continue
            # the service start, as _fix_service_start computes it (cd_hr_core)
            dates = [
                emp.sudo()[name]
                for name in ("joining_date", "joined_date")
                if name in emp.sudo()._fields and emp.sudo()[name]
            ]
            dates += contract_joins.get(emp.id, [])
            if not dates:
                continue
            start = min(dates)
            left = emp.sudo().left_date if "left_date" in emp.sudo()._fields else False
            # the completed service years, as _fix_annual_leave_years walks them
            years = []
            k = 0
            while True:
                y_start = start + relativedelta(years=k)
                y_end = start + relativedelta(years=k + 1) - timedelta(days=1)
                if y_end >= as_of:
                    break
                if left and y_start > left:
                    break
                years.append((y_start, min(y_end, left) if left else y_end))
                k += 1
            taken = [
                lv
                for lv in by_emp.get(emp.id, [])
                if lv.state == "approved" and lv.date_from <= as_of
            ]
            refused = [
                lv
                for lv in by_emp.get(emp.id, [])
                if lv.state == "rejected" and lv.date_from <= as_of
            ]
            # the ledger events, as _fix_annual_leave_balance replays them
            events = []
            for y_start, y_end in years:
                worked = emp._fix_leave_days_worked(y_start, y_end)
                events.append(
                    (
                        y_end + timedelta(days=1),
                        0,
                        float(worked // ANNUAL_LEAVE_DAYS_PER_EARNED_DAY),
                    )
                )
            events += [(lv.date_from, 1, -float(lv.days)) for lv in taken]
            cap = annual.carry_forward_limit or 0
            balance = 0.0
            for when, _kind, n in sorted(events):
                if n > 0:
                    extra = float(sum(r.days for r in refused if r.date_from < when))
                    balance += n
                    if cap:
                        balance = min(balance, cap + extra)
                else:
                    balance += n
            result[emp.id] = max(balance, 0.0)
        return result
