# fix_wfm_ops — M55: holiday calendar (incl. moon-dependent) and on-call /
# standby records. Attendance, rosters, devices and locks live in fix_attendance.py.
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


class FixHrOncall(models.Model):
    """On-call / standby shift with its allowance."""

    _name = "fix.hr.oncall"
    _description = "On-Call / Standby Shift"
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

    def action_start(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError("Start a planned on-call shift")
            rec.state = "active"

    def action_complete(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Complete an active on-call shift")
            rec.state = "completed"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancelled"
