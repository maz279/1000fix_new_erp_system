# cd_hr_core — shared pieces of the M21 controls (A09 workflow audit P0-b/P1/P2).
#
# Statutory figures here are the ones the A09 benchmark gives with a primary
# source (working/A09_evidence/ERP_benchmark_people_workforce.md, the
# Bangladesh table, "Verified [45]"). Figures the benchmark marks unverified
# or conflicting are company settings (fix_hr_settings.py), never constants.
import hashlib
import json
import re
from datetime import timedelta

from odoo import fields, models
from odoo.exceptions import UserError

# --- identifier formats (AGENTS.md "Bangladesh Statutory Workforce Master",
# BUILD_BRIEF §6.6) ---------------------------------------------------------
NID_RE = re.compile(r"^(\d{10}|\d{13}|\d{17})$")  # smart card 10, old 13, 17-digit NID
BIRTH_REG_RE = re.compile(r"^\d{17}$")  # BRIS birth registration
TIN_RE = re.compile(r"^\d{12}$")  # e-TIN (ITA 2023)
ROUTING_RE = re.compile(r"^\d{9}$")  # Bangladesh Bank BEFTN routing code
MFS_RE = re.compile(r"^01[3-9]\d{8}$")  # 11-digit BD mobile wallet
BANK_ACCOUNT_RE = re.compile(r"^\d{6,20}$")

# --- BLA 2006 notice (s.26 employer termination, s.20 retrenchment) ---------
# s.26(1)/(2): 120 days' notice for a monthly-rated permanent worker, 30 for a
# monthly-rated temporary worker (every contract here is monthly-rated: the
# wage is basic_monthly). Verified, unchanged in 2026 (benchmark row s.26).
TERMINATION_NOTICE_DAYS = {"permanent": 120, "other": 30}
# s.20(2)(a): one month's written notice (or wages in lieu) for retrenchment.
RETRENCHMENT_NOTICE_DAYS = 30
# s.30 / s.123(2): every due of a separated worker within 30 working days.
SETTLEMENT_WORKING_DAYS = 30
# s.24: written charge, at least 7 days to explain, enquiry within 60 days,
# suspension pending enquiry at most 60 days.
DISCIPLINARY_REPLY_DAYS = 7
DISCIPLINARY_ENQUIRY_DAYS = 60
SUSPENSION_MAX_DAYS = 60
# s.4(8): probation 6 months (clerical) or 3 months (others); a skilled
# worker's probation may be extended by 3 months.
PROBATION_MONTHS = {"clerical": 6, "skilled": 3, "other": 3}
PROBATION_SKILLED_EXTENSION_MONTHS = 3

OFFICER = "cd_hr_core.group_hr_officer"
LEGAL = "cd_hr_core.group_hr_legal_counsel"
EXECUTIVE = "cd_hr_core.group_hr_executive"
FINANCE = "cd_hr_core.group_hr_finance"
CLEAR_IT = "cd_hr_core.group_clearance_it"
CLEAR_ASSETS = "cd_hr_core.group_clearance_assets"


def check_format(value, pattern, label):
    """Raise a clear message when `value` (if any) does not match `pattern`."""
    if value and not pattern.match(str(value).strip()):
        raise UserError("%s %r is not valid." % (label, value))


def digest(values):
    """A stable fingerprint of what was approved (B5: pin, then compare)."""
    blob = json.dumps(values, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


def add_working_days(env, start, days, calendar=None):
    """`start` plus `days` working days on `calendar` (default the company's).

    A working day is a weekday the calendar has attendance on, and not a
    company-wide leave (public holiday) of that calendar. Without a calendar
    Friday, the BLA s.103 weekly holiday as practised, is the only day off."""
    start = fields.Date.to_date(start)
    calendar = calendar or env.company.resource_calendar_id
    weekdays = (
        {int(d) for d in calendar.attendance_ids.mapped("dayofweek")} if calendar else set()
    ) or {0, 1, 2, 3, 5, 6}
    holidays = set()
    if calendar:
        for leave in calendar.global_leave_ids:
            day = leave.date_from.date()
            while day <= leave.date_to.date():
                holidays.add(day)
                day += timedelta(days=1)
    day, counted = start, 0
    while counted < days:
        day += timedelta(days=1)
        if day.weekday() in weekdays and day not in holidays:
            counted += 1
    return day


class FixHrControlMixin(models.AbstractModel):
    """Who-may-act checks shared by the M21 workflow models."""

    _name = "fix.hr.control.mixin"
    _description = "M21 Segregation-of-Duties Helpers"

    def _hr_has(self, xmlid):
        return self.env.su or self.env.user.has_group(xmlid)

    def _hr_require(self, xmlid, what):
        if not self._hr_has(xmlid):
            group = self.env.ref(xmlid, raise_if_not_found=False)
            raise UserError("%s needs the %s role." % (what, group.name if group else xmlid))

    def _hr_subject_users(self):
        return self.mapped("employee_id").sudo().mapped("user_id")

    def _hr_refuse_conflicted(self, what, extra=None):
        """The subject, the creator and `extra` users never take this step."""
        if self.env.su:
            return
        for rec in self:
            barred = rec._hr_subject_users() | rec.sudo().create_uid
            if extra is not None:
                barred |= extra(rec) if callable(extra) else extra
            if self.env.user in barred:
                raise UserError(
                    "You cannot %s %s: you raised it, are its subject or already "
                    "signed another step of it." % (what, rec.display_name)
                )
