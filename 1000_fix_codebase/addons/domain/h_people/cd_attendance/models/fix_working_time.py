# fix_working_time — M55 T-07/T-08: working-time rules as versioned, effective-dated data.
#
# A09 audit M55-12: the limits were module constants and two company fields,
# with no version and no effective date, so a ruling (48 h vs 60 h, the s.101
# interval, the s.105 spread-over, the 56 h annual average) needed a release
# and changed the valuation of the past. Now every figure the valuation and
# the compliance checks read comes from the rule version in force on the day
# (`_fix_values_for`), each attendance record stores the version it was valued
# with (T-08), and a version that has taken effect is never edited: a change
# is a new version from a future date.
#
# Version 1 holds what the code did before the audit: the weekly limit and the
# rest between shifts from the company settings, the s.100 10 h day and the
# s.100/108 2 h overtime cap. The figures the code never held (the s.101
# interval, the s.105 spread-over, the s.102 56 h annual average) are 0, which
# means "not checked", until the business rules them (A09 report §7.4). Each
# of the four statutory checks is a label (flagged, as today) or a block
# (the attendance is refused), per version; the default is label.
from datetime import date, timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_attendance import (
    MAX_DAILY_HOURS,
    MAX_DAILY_OT_HOURS,
    MAX_WEEKLY_HOURS,
    MIN_SHIFT_REST_HOURS,
    _locked_lock,
)

RULE_MANAGER_GROUP = "hr.group_hr_manager"
MODES = [("label", "Label (flag only)"), ("block", "Block (refuse the attendance)")]
# what applies to a company with no rule version recorded: the code's own
# pre-audit figures (version 1 is seeded with exactly these)
DEFAULTS = {
    "daily_max_hours": MAX_DAILY_HOURS,
    "daily_ot_cap_hours": MAX_DAILY_OT_HOURS,
    "weekly_limit_hours": MAX_WEEKLY_HOURS,
    "min_rest_hours": MIN_SHIFT_REST_HOURS,
    "short_rest_mode": "label",
    "rest_interval_after_hours": 0.0,
    "rest_interval_minutes": 0.0,
    "rest_interval_after_hours_2": 0.0,
    "rest_interval_minutes_2": 0.0,
    "rest_interval_mode": "label",
    "spread_over_max_hours": 0.0,
    "spread_over_mode": "label",
    "annual_avg_weekly_hours": 0.0,
    "annual_average_mode": "label",
}
TERMS = (*DEFAULTS, "company_id", "date_from")
# the first version reaches back over every record already captured
EPOCH = date(2000, 1, 1)
# the former stored company settings, read once to seed version 1 (fixed SQL,
# columns in sorted order)
LEGACY_SETTINGS_SQL = {
    frozenset({"fix_att_max_weekly_hours", "fix_att_min_rest_hours"}): (
        "SELECT fix_att_max_weekly_hours, fix_att_min_rest_hours FROM res_company WHERE id = %s"
    ),
    frozenset({"fix_att_max_weekly_hours"}): (
        "SELECT fix_att_max_weekly_hours FROM res_company WHERE id = %s"
    ),
    frozenset({"fix_att_min_rest_hours"}): (
        "SELECT fix_att_min_rest_hours FROM res_company WHERE id = %s"
    ),
}


class FixWorkingTimeRule(models.Model):
    """One version of a company's working-time rules (T-07)."""

    _name = "fix.working.time.rule"
    _description = "Working-Time Rule Version"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "company_id, date_from desc"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    version = fields.Integer(readonly=True, copy=False)
    date_from = fields.Date(string="In Force From", required=True, index=True, tracking=True)
    date_to = fields.Date(
        string="In Force Until",
        compute="_compute_date_to",
        store=True,
        help="The day before the next version takes effect; empty while it is the latest.",
    )
    basis = fields.Text(help="The ruling or source this version records.")
    # ---- daily and weekly limits (BLA s.100, s.102, s.108) --------------------
    daily_max_hours = fields.Float(
        string="Daily Ceiling (h)",
        default=DEFAULTS["daily_max_hours"],
        help="BLA s.100: 8 h a day, up to 10 h with overtime (s.108). Also the payable cap "
        "on a weekly rest day.",
    )
    daily_ot_cap_hours = fields.Float(
        string="Daily Overtime Cap (h)",
        default=DEFAULTS["daily_ot_cap_hours"],
        help="BLA s.100/108: at most 2 h of overtime a working day.",
    )
    weekly_limit_hours = fields.Float(
        string="Weekly Limit (h)",
        default=DEFAULTS["weekly_limit_hours"],
        help="Flagged above this. BLA s.102: 48 h ordinary, up to 60 h with overtime; the M55 "
        "spec says 48 h. 60 h before the A09 audit (A09 decision).",
    )
    # ---- rest between shifts (the company's own rule) --------------------------
    min_rest_hours = fields.Float(
        string="Minimum Rest Between Shifts (h)",
        default=DEFAULTS["min_rest_hours"],
        help="The company's rest-between-shifts rule; 0 = not checked. Not a BLA figure "
        "(s.101 is the interval inside a day). 11 h before the A09 audit.",
    )
    short_rest_mode = fields.Selection(MODES, string="Short Rest: Mode", default="label")
    # ---- s.101 interval for rest or meal inside a day ------------------------------
    rest_interval_after_hours = fields.Float(
        string="s.101 Interval Needed After (h)",
        help="BLA s.101: no more than this many hours worked without the interval below. "
        "0 = not checked (not ruled; A09 decision).",
    )
    rest_interval_minutes = fields.Float(string="s.101 Interval Length (min)")
    rest_interval_after_hours_2 = fields.Float(
        string="s.101 Second Tier: After (h)",
        help="A second tier of s.101 (e.g. a shorter interval after fewer hours). 0 = none.",
    )
    rest_interval_minutes_2 = fields.Float(string="s.101 Second Tier: Interval (min)")
    rest_interval_mode = fields.Selection(MODES, string="s.101 Interval: Mode", default="label")
    # ---- s.105 spread-over ----------------------------------------------------------
    spread_over_max_hours = fields.Float(
        string="s.105 Spread-Over Limit (h)",
        help="BLA s.105: first check-in to last check-out of a day, intervals included. "
        "0 = not checked (not ruled; A09 decision).",
    )
    spread_over_mode = fields.Selection(MODES, string="s.105 Spread-Over: Mode", default="label")
    # ---- s.102 annual average ---------------------------------------------------------
    annual_avg_weekly_hours = fields.Float(
        string="s.102 Annual Average Weekly Hours",
        help="BLA s.102: the hours of a calendar year may not exceed this average a week "
        "(checked as the year's total against this x the weeks of the year). 0 = not "
        "checked (not ruled; A09 decision).",
    )
    annual_average_mode = fields.Selection(
        MODES, string="s.102 Annual Average: Mode", default="label"
    )

    _company_from = models.Constraint(
        "UNIQUE (company_id, date_from)", "One working-time rule version per company and day"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"version"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self._fix_in_force_or_past():
            locked |= set(TERMS)
        return locked

    @api.depends("company_id", "version", "date_from")
    def _compute_name(self):
        for rec in self:
            rec.name = "Working-Time Rules v%s from %s" % (rec.version or "?", rec.date_from or "")

    @api.depends("company_id", "date_from")
    def _compute_date_to(self):
        for rec in self:
            nxt = self.sudo().search(
                [("company_id", "=", rec.company_id.id), ("date_from", ">", rec.date_from)],
                order="date_from",
                limit=1,
            )
            rec.date_to = (nxt.date_from - timedelta(days=1)) if nxt else False

    @api.constrains(
        "daily_max_hours",
        "daily_ot_cap_hours",
        "weekly_limit_hours",
        "min_rest_hours",
        "rest_interval_after_hours",
        "rest_interval_minutes",
        "rest_interval_after_hours_2",
        "rest_interval_minutes_2",
        "spread_over_max_hours",
        "annual_avg_weekly_hours",
    )
    def _check_figures(self):
        for rec in self:
            for name in DEFAULTS:
                if name.endswith("_mode"):
                    continue
                if (rec[name] or 0.0) < 0:
                    raise ValidationError("%s cannot be negative." % rec._fields[name].string)
            if rec.daily_ot_cap_hours > rec.daily_max_hours > 0:
                raise ValidationError("The daily overtime cap cannot exceed the daily ceiling.")
            for after, minutes in (
                (rec.rest_interval_after_hours, rec.rest_interval_minutes),
                (rec.rest_interval_after_hours_2, rec.rest_interval_minutes_2),
            ):
                if bool(after) != bool(minutes):
                    raise ValidationError(
                        "An s.101 interval needs both the hours after which it is due and its "
                        "length (or neither)."
                    )

    def _fix_in_force_or_past(self):
        self.ensure_one()
        return bool(self.date_from and self.date_from <= fields.Date.context_today(self))

    def _fix_assert_manager(self):
        if not (self.env.su or self.env.user.has_group(RULE_MANAGER_GROUP)):
            raise AccessError("Only an HR Manager records a working-time rule version.")

    # ---- lifecycle: a version in force is never edited --------------------------
    @api.model_create_multi
    def create(self, vals_list):
        self._fix_assert_manager()
        today = fields.Date.context_today(self)
        for vals in vals_list:
            start = fields.Date.to_date(vals.get("date_from"))
            if not self.env.su and start and start <= today:
                raise UserError(
                    "A working-time rule version takes effect from a future day (%s is not): "
                    "the past stays valued with the rules then in force (T-08)." % start
                )
        recs = super().create(vals_list)
        for rec in recs:
            top = self.sudo().search(
                [("company_id", "=", rec.company_id.id), ("id", "!=", rec.id)],
                order="version desc",
                limit=1,
            )
            rec._guarded().write({"version": (top.version or 0) + 1})
        recs._fix_after_change()
        return recs

    def write(self, vals):
        # who may write at all is the ACL's (HR Manager); what may change is here
        if self and not self.env.su:
            terms = set(TERMS) & set(vals)
            if terms:
                for rec in self:
                    changed = [n for n in terms if rec._fix_guard_differs(n, vals[n], rec[n])]
                    if changed and rec._fix_in_force_or_past():
                        raise UserError(
                            "%s has taken effect: its figures are what the attendance since %s "
                            "was valued with. Record a new version from a future day."
                            % (rec.name, rec.date_from)
                        )
                if "date_from" in vals:
                    start = fields.Date.to_date(vals["date_from"])
                    if start and start <= fields.Date.context_today(self):
                        raise UserError("A rule version takes effect from a future day.")
        res = super().write(vals)
        if set(TERMS) & set(vals):
            self._fix_after_change()
        return res

    def unlink(self):
        if not self.env.su:
            self._fix_assert_manager()
            if any(r._fix_in_force_or_past() for r in self):
                raise UserError("A working-time rule version that has taken effect is kept.")
        companies = self.mapped("company_id")
        res = super().unlink()
        for company in companies:
            self.sudo().search([("company_id", "=", company.id)])._compute_date_to()
        return res

    def _fix_after_change(self):
        """Neighbours' end dates follow, and attendance from the new date on
        (outside locked periods) is valued again with the version now in force."""
        Rule = self.sudo()
        for company in self.mapped("company_id"):
            versions = Rule.search([("company_id", "=", company.id)])
            self.env.add_to_compute(self._fields["date_to"], versions)
            versions.flush_recordset()
        if self.env.context.get("fix_wt_no_revalue"):
            return
        Record = self.env["fix.attendance.record"].sudo()
        for rec in self:
            records = Record.search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("check_in", ">=", fields.Datetime.to_datetime(rec.date_from)),
                ]
            )
            # a locked period keeps the figures it was locked (and paid) with
            open_records = records.filtered(
                lambda r: not _locked_lock(self.env, r.company_id, r.check_in.date())
            )
            self.env.add_to_compute(Record._fields["wt_rule_id"], records)
            Record._fix_recompute_days({r._fix_day_key() for r in open_records})

    # ---- reading ---------------------------------------------------------------------
    @api.model
    def _fix_rule_for(self, company, day):
        """The version of `company` in force on `day` (empty: none recorded)."""
        if not company or not day:
            return self.browse()
        return self.sudo().search(
            [("company_id", "=", company.id), ("date_from", "<=", day)],
            order="date_from desc",
            limit=1,
        )

    @api.model
    def _fix_values_for(self, company, day):
        """{figure: value, 'rule': version} for `company` on `day`."""
        rule = self._fix_rule_for(company, day)
        values = dict(DEFAULTS)
        if rule:
            values.update({name: rule[name] for name in DEFAULTS})
        values["rule"] = rule
        return values

    # ---- version 1 ---------------------------------------------------------------------
    @api.model
    def _fix_seed_version_one(self):
        """Data hook (idempotent): every company without a rule gets version 1
        with the figures the code used before the audit, its weekly limit and
        minimum rest taken from the former company settings."""
        Rule = self.sudo()
        cr = self.env.cr
        cr.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'res_company' "
            "AND column_name IN ('fix_att_max_weekly_hours', 'fix_att_min_rest_hours')"
        )
        columns = {row[0] for row in cr.fetchall()}
        made = 0
        for company in self.env["res.company"].sudo().search([]):
            if Rule.search_count([("company_id", "=", company.id)]):
                continue
            vals = {
                "company_id": company.id,
                "date_from": EPOCH,
                "basis": "Version 1: the figures the code used before the A09 audit (weekly "
                "limit and minimum rest from the former company settings; s.100 10 h day and "
                "2 h overtime cap). s.101, s.105 and the s.102 annual average are not ruled.",
            }
            if columns:
                cr.execute(LEGACY_SETTINGS_SQL[frozenset(columns)], [company.id])
                row = dict(zip(sorted(columns), cr.fetchone(), strict=True))
                for column, name in (
                    ("fix_att_max_weekly_hours", "weekly_limit_hours"),
                    ("fix_att_min_rest_hours", "min_rest_hours"),
                ):
                    if row.get(column):
                        vals[name] = row[column]
            Rule.with_context(fix_wt_no_revalue=True).create(vals)
            made += 1
        if made:
            # T-08: every record names the version it was valued with (no
            # revaluation: version 1 holds exactly the figures already used)
            Record = self.env["fix.attendance.record"].sudo()
            records = Record.search([])
            self.env.add_to_compute(Record._fields["wt_rule_id"], records)
            records.flush_recordset(["wt_rule_id"])
        return made


class ResCompanyWorkingTime(models.Model):
    _inherit = "res.company"

    # A09 T-07: these were the only configurable figures; they now show the
    # version in force today. A change is a new fix.working.time.rule version.
    fix_att_max_weekly_hours = fields.Float(
        string="Weekly Hours Limit (in force today)",
        compute="_compute_fix_att_rules",
        help="From the working-time rule version in force today (fix.working.time.rule).",
    )
    fix_att_min_rest_hours = fields.Float(
        string="Minimum Rest Between Shifts (in force today)",
        compute="_compute_fix_att_rules",
        help="From the working-time rule version in force today (fix.working.time.rule).",
    )

    def _compute_fix_att_rules(self):
        Rule = self.env["fix.working.time.rule"]
        today = fields.Date.context_today(self)
        for company in self:
            values = Rule._fix_values_for(company, today)
            company.fix_att_max_weekly_hours = values["weekly_limit_hours"]
            company.fix_att_min_rest_hours = values["min_rest_hours"]
