# Cost centre for people cost (A09 M56-5 / FR-PAY-053).
#
# The general ledger carries a free-form `cost_centre` dimension (cd_gl_ext,
# MD-* finance set; a chart account may require it, COA-03), but nothing on
# the people side said which cost centre an employee's pay belongs to, so the
# payroll entry could be split by unit and branch only. A department holds its
# cost centre; an employee may carry an override (a technician seconded to
# another centre). Payroll pins the effective code on each payslip.
from odoo import fields, models


class HrDepartmentCostCentre(models.Model):
    _inherit = "hr.department"

    fix_cost_centre = fields.Char(
        string="Cost Centre",
        tracking=True,
        help="GL cost centre code (cd_gl_ext dimension) the department's pay is booked to.",
    )


class HrEmployeeCostCentre(models.Model):
    _inherit = "hr.employee"

    fix_cost_centre = fields.Char(
        string="Cost Centre Override",
        tracking=True,
        groups="hr.group_hr_user",
        help="Books this employee's pay to another cost centre than the department's.",
    )

    def _fix_effective_cost_centre(self):
        """The employee's override, else the department's cost centre."""
        self.ensure_one()
        emp = self.sudo()
        return (emp.fix_cost_centre or emp.department_id.fix_cost_centre or "").strip() or False
