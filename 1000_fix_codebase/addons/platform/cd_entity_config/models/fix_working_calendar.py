# fix.working.calendar — branch working hours and holidays (P03-M04-T04).
# M02's W2 availability and SLA-clock pausing (M01 out-of-hours) read this.
# Bangladesh public holidays — including moon-dependent dates — are calendar
# lines, not code (05-06 §9); the data pack loads via fix.country.pack.
#
# A12 finish E19 (M30-6): one Platform Admin's 60-day holiday moved an 8-hour SLA
# by two months with no trace. Every line and holiday change now leaves an audit
# row and chatter; a holiday longer than the configured limit (default 3 days)
# takes a second Platform Admin. A national holiday comes from a certified pack,
# which loads as superuser (already two people).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_entity import audit_event, require_platform_admin

DIRECT_HOLIDAY_DAYS_PARAM = "fix_calendar.max_direct_holiday_days"

_WEEKDAYS = [
    ("mon", "Monday"),
    ("tue", "Tuesday"),
    ("wed", "Wednesday"),
    ("thu", "Thursday"),
    ("fri", "Friday"),
    ("sat", "Saturday"),
    ("sun", "Sunday"),
]


class FixWorkingCalendar(models.Model):
    """Working calendar for a branch (or a template shared by branches)."""

    _name = "fix.working.calendar"
    _description = "Working Calendar"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Calendar Name", required=True, tracking=True)
    template_id = fields.Many2one(
        "fix.working.calendar",
        string="Template",
        help="Inherits day/holiday lines from a template calendar; local "
        "overrides may be added on top (a branch closed on Friday "
        "inherits everything else from the national template).",
    )
    branch_id = fields.Many2one(
        "fix.branch",
        string="Branch",
        help="Empty on template calendars; SLA availability resolves through "
        "the branch -> calendar link (fix.branch.calendar_id).",
    )
    timezone = fields.Selection(
        [("Asia/Dhaka", "Asia/Dhaka (UTC+6)")],
        string="Timezone",
        default="Asia/Dhaka",
        required=True,
        help="QH-04 companion: Asia/Dhaka is the only operational zone",
    )
    active = fields.Boolean(default=True, tracking=True)
    line_ids = fields.One2many("fix.working.calendar.line", "calendar_id", string="Working Hours")
    holiday_ids = fields.One2many("fix.working.calendar.holiday", "calendar_id", string="Holidays")
    pending_closure_name = fields.Char(string="Proposed Closure", readonly=True, copy=False)
    pending_closure_from = fields.Date(string="Closure From", readonly=True, copy=False)
    pending_closure_to = fields.Date(string="Closure To", readonly=True, copy=False)
    pending_closure_by_id = fields.Many2one(
        "res.users", string="Closure Proposed By", readonly=True, copy=False
    )

    def _calendar_audit(self, event, detail):
        for rec in self:
            audit_event(
                rec.env,
                event,
                "fix.working.calendar,%d" % rec.id,
                "%s by %s" % (detail, rec.env.user.name),
            )
            rec.message_post(body=detail)

    def action_propose_closure(self, name=None, date_from=None, date_to=None):
        """First signature on a long closure: nothing moves until confirmed."""
        require_platform_admin(self.env, "The working-calendar register")
        if not ((name or "").strip() and date_from and date_to):
            raise UserError("A closure needs a name, a first day and a last day.")
        try:
            first, last = fields.Date.to_date(date_from), fields.Date.to_date(date_to)
        except ValueError as exc:
            raise UserError("Give the closure dates as YYYY-MM-DD.") from exc
        if last < first:
            raise UserError("A closure cannot end before it starts.")
        for rec in self:
            rec.write(
                {
                    "pending_closure_name": name.strip(),
                    "pending_closure_from": first,
                    "pending_closure_to": last,
                    "pending_closure_by_id": rec.env.uid,
                }
            )
            rec._calendar_audit(
                "calendar.closure_proposed",
                "Closure '%s' proposed for %s to %s" % (name.strip(), first, last),
            )
        return True

    def action_confirm_closure(self):
        require_platform_admin(self.env, "The working-calendar register")
        for rec in self:
            if not rec.pending_closure_name:
                raise UserError("No closure is waiting on calendar %s." % rec.name)
            if not rec.env.su and rec.env.user == rec.pending_closure_by_id:
                raise UserError("A second person confirms a closure: you proposed this one.")
            # sudo after the check: the size limit below binds a person acting alone.
            rec.env["fix.working.calendar.holiday"].sudo().create(
                {
                    "calendar_id": rec.id,
                    "name": rec.pending_closure_name,
                    "date_from": rec.pending_closure_from,
                    "date_to": rec.pending_closure_to,
                }
            )
            rec.write(
                {
                    "pending_closure_name": False,
                    "pending_closure_from": False,
                    "pending_closure_to": False,
                    "pending_closure_by_id": False,
                }
            )
        return True

    # A12 X4 / M30-6 (b07): a clerk's 60-day "holiday" moved an 8-hour SLA
    # deadline by 59 days and zeroed elapsed business time, so nothing could
    # breach. The same calendar drives M63 approval escalation. Calendars and
    # their lines/holidays are governed master data: Platform Admin only (the
    # M65 country pack loads holidays as superuser, which stays trusted).
    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The working-calendar register")
        return super().create(vals_list)

    def write(self, vals):
        require_platform_admin(self.env, "The working-calendar register")
        return super().write(vals)

    def unlink(self):
        require_platform_admin(self.env, "The working-calendar register")
        return super().unlink()


class FixWorkingCalendarLine(models.Model):
    """One weekday's working window on a calendar."""

    _name = "fix.working.calendar.line"
    _description = "Working Calendar Line"

    calendar_id = fields.Many2one("fix.working.calendar", required=True, ondelete="cascade")
    weekday = fields.Selection(_WEEKDAYS, string="Weekday", required=True)
    hour_from = fields.Float(string="From (hour)", required=True, help="0.0-24.0 local Dhaka time")
    hour_to = fields.Float(string="To (hour)", required=True)
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _calendar_weekday_unique = models.Constraint(
        "UNIQUE (calendar_id, weekday)", "Each weekday appears once per calendar"
    )

    @api.constrains("hour_from", "hour_to")
    def _check_window(self):
        for line in self:
            if not (0.0 <= line.hour_from < line.hour_to <= 24.0):
                raise ValidationError("Working window must satisfy 0 <= from < to <= 24")

    # A12 X4 / M30-6: a working line IS the SLA clock (M01 out-of-hours
    # pausing reads it); the same admin gate as the calendar header.
    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The working-calendar register")
        lines = super().create(vals_list)
        for line in lines:
            line.calendar_id._calendar_audit(
                "calendar.line_added",
                "Working line added: %s %s-%s" % (line.weekday, line.hour_from, line.hour_to),
            )
        return lines

    def write(self, vals):
        require_platform_admin(self.env, "The working-calendar register")
        result = super().write(vals)
        for line in self:
            line.calendar_id._calendar_audit(
                "calendar.line_changed",
                "Working line changed: %s %s-%s" % (line.weekday, line.hour_from, line.hour_to),
            )
        return result

    def unlink(self):
        require_platform_admin(self.env, "The working-calendar register")
        for line in self:
            line.calendar_id._calendar_audit(
                "calendar.line_removed", "Working line removed: %s" % line.weekday
            )
        return super().unlink()


class FixWorkingCalendarHoliday(models.Model):
    """A holiday closure — fixed-date or moon-dependent (loaded, never coded)."""

    _name = "fix.working.calendar.holiday"
    _description = "Calendar Holiday"

    calendar_id = fields.Many2one("fix.working.calendar", required=True, ondelete="cascade")
    name = fields.Char(string="Holiday", required=True)
    name_bn = fields.Char(string="Holiday (Bengali)", help="DE-17")
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)
    pack_line_id = fields.Many2one(
        "fix.country.pack.line",
        string="From Country Pack Line",
        readonly=True,
        ondelete="set null",
        help="Set when a certified holiday pack loaded this row; retiring the pack removes it.",
    )

    @api.constrains("date_from", "date_to")
    def _check_range(self):
        for holiday in self:
            if holiday.date_to < holiday.date_from:
                raise ValidationError("Holiday end precedes its start")

    def _check_second_person_needed(self):
        """A long closure moves every SLA deadline on the calendar, so one person
        alone may not enter or widen one. Superuser code stays trusted."""
        if self.env.su:
            return
        limit = int(
            self.env["ir.config_parameter"].sudo().get_param(DIRECT_HOLIDAY_DAYS_PARAM, "3")
        )
        for holiday in self:
            days = (holiday.date_to - holiday.date_from).days + 1
            if days > limit:
                raise UserError(
                    "A closure of %d days moves every SLA deadline on this calendar, so a "
                    "second Platform Admin must confirm it: use Propose Closure on the "
                    "calendar (the direct limit is %d days, ir.config_parameter %s)."
                    % (days, limit, DIRECT_HOLIDAY_DAYS_PARAM)
                )

    # A12 X4 / M30-6 (b07): the finding's attack WAS a holiday row. The M65
    # country pack loads the national calendar as superuser (trusted); an
    # interactive user needs Platform Admin.
    @api.model_create_multi
    def create(self, vals_list):
        require_platform_admin(self.env, "The working-calendar register")
        holidays = super().create(vals_list)
        holidays._check_second_person_needed()
        for holiday in holidays:
            holiday.calendar_id._calendar_audit(
                "calendar.holiday_added",
                "Holiday '%s' added: %s to %s" % (holiday.name, holiday.date_from, holiday.date_to),
            )
        return holidays

    def write(self, vals):
        require_platform_admin(self.env, "The working-calendar register")
        result = super().write(vals)
        self._check_second_person_needed()
        for holiday in self:
            holiday.calendar_id._calendar_audit(
                "calendar.holiday_changed",
                "Holiday '%s' changed: %s to %s"
                % (holiday.name, holiday.date_from, holiday.date_to),
            )
        return result

    def unlink(self):
        require_platform_admin(self.env, "The working-calendar register")
        for holiday in self:
            holiday.calendar_id._calendar_audit(
                "calendar.holiday_removed",
                "Holiday '%s' removed (%s to %s)"
                % (holiday.name, holiday.date_from, holiday.date_to),
            )
        return super().unlink()
