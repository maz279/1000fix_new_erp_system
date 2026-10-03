# fix_hr_core — M21 complete: contracts, statutory leave, org structure (P08-M01).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

# Bangladesh Labour Act 2006 statutory leave entitlements (SC-008), in days
STATUTORY_LEAVE = {
    "annual": 20,       # s.117 casual+earned composite floor as practised
    "sick": 14,         # s. 148 sick leave
    "festival": 11,     # s. 146 festival holidays
    "maternity": 112,   # s. 46: 16 weeks (maternity, female workers)
    "paternity": 10,    # policy floor (not statutory; recorded as policy)
}
PROBATION_CAP_MONTHS = 6  # Labour Rules 2021 r.25: probation <= 6 months


class HrEmployeeCdCoreExt(models.Model):
    """M21 completion fields on the W1 master slice.

    PII routing (SC-007/FF-09): NID/TIN/biometric templates NEVER land on
    hr.employee — they live in fix.identity.document (cd_party_master),
    which the residency service classifies. This extension references the
    identity store only.
    """
    _inherit = "hr.employee"

    employee_code = fields.Char(string="Employee Code", index=True,
                                help="Payroll reference (M56); the identity "
                                     "documents carry the PII, not this model")
    position_id = fields.Many2one("fix.org.position", string="Position")
    contract_count = fields.Integer(compute="_compute_contract_count",
                                    string="Contracts")

    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = self.env["fix.employment.contract"].search_count(
                [("employee_id", "=", rec.id)])

    # P08-M01-T06: the W1 joiner/mover/leaver event set still drives M29
    # provisioning at full scale - re-verified here, not assumed.
    def write(self, vals):
        result = super().write(vals)
        if "department_id" in vals or "job_id" in vals or "work_location" in vals:
            for rec in self:
                publish(self.env, "employee.moved", "hr.employee", rec.id, {
                    "employee_code": rec.employee_code or "",
                    "department": rec.department_id.name or "",
                })
        return result


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixOrgPosition(models.Model):
    """Organisation structure: reporting lines and position management."""
    _name = "fix.org.position"
    _description = "Organisation Position"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    name = fields.Char(required=True, tracking=True)
    parent_id = fields.Many2one("fix.org.position", string="Reports To",
                                ondelete="restrict", index=True)
    employee_ids = fields.One2many("hr.employee", "position_id",
                                   string="Holders")
    grade = fields.Char(string="Grade", help="M57 compensation band reference")

    def _check_hierarchy(self):
        for rec in self:
            seen, node = {rec.id}, rec.parent_id
            while node:
                if node.id in seen:
                    raise ValidationError(
                        "Reporting line loop at %s" % rec.name)
                seen.add(node.id)
                node = node.parent_id


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixEmploymentContract(models.Model):
    """Labour Act 2006 employment artefacts (P08-M01-T05) — where the
    category-H statutory density lives."""
    _name = "fix.employment.contract"
    _description = "Employment Contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "employee_id, joining_date desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    employee_id = fields.Many2one("hr.employee", string="Employee",
                                  required=True, ondelete="cascade", index=True)
    contract_type = fields.Selection(
        [("permanent", "Permanent"), ("probation", "Probation"),
         ("fixed_term", "Fixed Term"), ("part_time", "Part Time")],
        required=True, default="probation", tracking=True)
    joining_date = fields.Date(required=True)
    probation_end = fields.Date(
        help="Labour Rules 2021 r.25: probation may not exceed 6 months")
    weekly_hours = fields.Float(string="Statutory Weekly Hours", default=48,
                                required=True,
                                help="s. 102: 48 hours/week ceiling")
    basic_monthly = fields.Monetary(string="Basic Salary (Monthly)",
                                    currency_field="currency_id", required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"),
         ("expired", "Expired"), ("terminated", "Terminated")],
        default="draft", required=True, tracking=True)
    identity_document_note = fields.Char(
        string="Identity Store Ref",
        help="PII pointer: the NID/passport artefact lives in "
             "fix.identity.document (Z4 residency), referenced, never copied")

    def action_activate(self):
        for rec in self:
            rec._validate_statutory()
            rec.state = "active"
            publish(self.env, "employment.contract.activated",
                    "fix.employment.contract", rec.id, {
                        "employee": rec.employee_id.name,
                        "contract_type": rec.contract_type,
                        "joining": str(rec.joining_date)})

    def action_terminate(self):
        for rec in self:
            rec.state = "terminated"
            # The M21 leave event M29 consumes (leaver de-provisions)
            publish(self.env, "employee.leaver", "hr.employee",
                    rec.employee_id.id, {"contract": rec.name or rec.id})

    def _validate_statutory(self):
        for rec in self:
            if rec.probation_end:
                cap_months = (PROBATION_CAP_MONTHS * 30)
                span = (fields.Date.to_date(rec.probation_end)
                        - fields.Date.to_date(rec.joining_date)).days
                if span > cap_months:
                    raise ValidationError(
                        "Probation exceeds the 6-month statutory cap "
                        "(Labour Rules 2021 r.25)")
            if rec.weekly_hours > 48:
                raise ValidationError(
                    "s.102: weekly hours may not exceed 48")
            if rec.basic_monthly <= 0:
                raise ValidationError("Basic salary must be positive")


class FixLeaveType(models.Model):
    """Statutory leave catalogue (Bangladesh Labour Act 2006, SC-008)."""
    _name = "fix.leave.type"
    _description = "Leave Type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    name_bn = fields.Char(string="Leave Name (Bengali)", help="DE-17")
    entitlement_days = fields.Integer(required=True)
    encashable = fields.Boolean(
        help="Annual leave is encashable at separation (s.118)")
    maternity = fields.Boolean()

    def action_validate_statutory(self):
        """The entitlement must be at least the statutory floor."""
        for rec in self:
            floor = STATUTORY_LEAVE.get(rec.code)
            if floor and rec.entitlement_days < floor:
                raise ValidationError(
                    "%s entitlement below the statutory floor (%d days)"
                    % (rec.code, floor))


    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
class FixLeaveRequest(models.Model):
    """Leave and absence management on the statutory floors."""
    _name = "fix.leave.request"
    _description = "Leave Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    leave_type_id = fields.Many2one("fix.leave.type", required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    days = fields.Integer(compute="_compute_days", store=True)
    reason = fields.Text()
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("rejected", "Rejected")],
        default="draft", required=True, tracking=True)

    @api.depends("date_from", "date_to")
    def _compute_days(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to >= rec.date_from:
                rec.days = (fields.Date.to_date(rec.date_to)
                            - fields.Date.to_date(rec.date_from)).days + 1
            else:
                rec.days = 0

    def action_approve(self):
        for rec in self:
            rec.leave_type_id.action_validate_statutory()
            taken = self.search_count([
                ("employee_id", "=", rec.employee_id.id),
                ("leave_type_id", "=", rec.leave_type_id.id),
                ("state", "=", "approved")])
            if taken + rec.days > rec.leave_type_id.entitlement_days:
                raise UserError(
                    "Entitlement exhausted: %d approved + %d requested > %d"
                    % (taken, rec.days, rec.leave_type_id.entitlement_days))
            rec.state = "approved"
            publish(self.env, "leave.approved", "fix.leave.request", rec.id,
                    {"employee": rec.employee_id.name, "days": rec.days})

    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")