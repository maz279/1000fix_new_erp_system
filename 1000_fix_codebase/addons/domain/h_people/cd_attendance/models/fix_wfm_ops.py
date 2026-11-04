# fix_wfm_ops — M55: holiday calendar (incl. moon-dependent) and on-call /
# standby records. Attendance, rosters, devices and locks live in fix_attendance.py.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class FixHrHoliday(models.Model):
    """Public / religious / moon-dependent holidays for the working calendar."""

    _name = "fix.hr.holiday"
    _description = "Holiday (moon-dependent aware)"
    _order = "date"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    date = fields.Date(required=True, index=True)
    name_bn = fields.Char(string="Holiday (Bengali)", help="DE-17")
    holiday_type = fields.Selection(
        [
            ("public", "Public Holiday"),
            ("religious", "Religious"),
            ("moon", "Moon-Dependent (subject to sighting)"),
            ("company", "Company Day"),
        ],
        required=True,
        default="public",
    )
    tentative = fields.Boolean(
        string="Tentative (sighting-dependent)",
        help="Moon-dependent dates are announced after the sighting; tentative rows are "
        "confirmed by clearing this flag.",
    )
    notes = fields.Char()

    _date_name = models.Constraint(
        "UNIQUE (date, company_id)", "One holiday record per date per company"
    )

    # FR-WFM-037: the calendar is APPLIED - to the leave day count and to the
    # valuation of the attendance worked that day (M55-12, F17, H4)
    def _fix_apply_calendar(self, keys):
        Leave = self.env["fix.leave.request"].sudo()
        Record = self.env["fix.attendance.record"].sudo()
        days = set()
        for company_id, day in keys:
            if not day:
                continue
            days.add(day)
            leaves = Leave.search(
                [
                    ("company_id", "=", company_id),
                    ("state", "in", ("draft", "submitted")),
                    ("date_from", "<=", day),
                    ("date_to", ">=", day),
                ]
            )
            if leaves:
                self.env.add_to_compute(Leave._fields["days"], leaves)
                leaves.flush_recordset()
            start = fields.Datetime.to_datetime(day)
            recs = Record.search(
                [
                    ("company_id", "=", company_id),
                    ("check_in", ">=", start),
                    ("check_in", "<", start + timedelta(days=1)),
                ]
            )
            Record._fix_recompute_days([r._fix_day_key() for r in recs])

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        recs._fix_apply_calendar([(r.company_id.id, r.date) for r in recs])
        return recs

    def write(self, vals):
        before = [(r.company_id.id, r.date) for r in self]
        res = super().write(vals)
        if {"date", "company_id", "tentative"} & set(vals):
            self._fix_apply_calendar(before + [(r.company_id.id, r.date) for r in self])
        return res

    def unlink(self):
        keys = [(r.company_id.id, r.date) for r in self]
        res = super().unlink()
        self.env["fix.hr.holiday"]._fix_apply_calendar(keys)
        return res


class FixHrOncall(models.Model):
    """On-call / standby shift with its allowance."""

    _name = "fix.hr.oncall"
    _description = "On-Call / Standby Shift"
    _inherit = ["fix.guarded.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade", index=True)
    shift_id = fields.Many2one("fix.shift.template", string="Shift")
    date_from = fields.Datetime(required=True)
    date_to = fields.Datetime(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    allowance = fields.Monetary(currency_field="currency_id", string="Standby Allowance")
    phone = fields.Char(string="Contact Number")
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="planned",
        readonly=True,
    )

    _dates_ordered = models.Constraint(
        "CHECK (date_to >= date_from)", "On-call end cannot precede its start"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.hr.oncall") or "ONC/New"
        return super().create(vals_list)

    def _fix_guarded_fields(self) -> set:
        # A09 P3: the on-call state is the lifecycle, not a typed field
        return super()._fix_guarded_fields() | {"state"}

    def write(self, vals):
        frozen = {"employee_id", "date_from", "date_to", "allowance", "currency_id"} & set(vals)
        if frozen and not self.env.su:
            done = self.filtered(lambda r: r.state in ("completed", "cancelled"))
            if done:
                raise UserError(
                    "On-call %s is %s: its employee, window and allowance are final."
                    % (done[0].name, done[0].state)
                )
        return super().write(vals)

    def action_start(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError("Start a planned on-call shift")
            rec._guarded().write({"state": "active"})

    def action_complete(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Complete an active on-call shift")
            rec._guarded().write({"state": "completed"})

    def action_cancel(self):
        # H2: a COMPLETED shift (allowance earned) is not cancelled away
        for rec in self:
            if rec.state not in ("planned", "active"):
                raise UserError(
                    "Only a planned or active on-call shift is cancelled (%s is %s)."
                    % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "cancelled"})
