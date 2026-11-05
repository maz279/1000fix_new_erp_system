# fix.working.calendar — branch working hours and holidays (P03-M04-T04).
# M02's W2 availability and SLA-clock pausing (M01 out-of-hours) read this.
# Bangladesh public holidays — including moon-dependent dates — are calendar
# lines, not code (05-06 §9); the data pack loads via fix.country.pack.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .fix_entity import require_platform_admin

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
        return super().create(vals_list)

    def write(self, vals):
        require_platform_admin(self.env, "The working-calendar register")
        return super().write(vals)

    def unlink(self):
        require_platform_admin(self.env, "The working-calendar register")
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

    @api.constrains("date_from", "date_to")
    def _check_range(self):
        for holiday in self:
            if holiday.date_to < holiday.date_from:
                raise ValidationError("Holiday end precedes its start")

    # A12 X4 / M30-6 (b07): the finding's attack WAS a holiday row. The M65
    # country pack loads the national calendar as superuser (trusted); an
    # interactive user needs Platform Admin.
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
