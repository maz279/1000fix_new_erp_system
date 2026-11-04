# cd_hr_core — the A09 hand-off interfaces between modules.
#
# Core HR (this module) cannot import payroll, attendance or performance:
# they depend on it, not the other way round. Where a core-HR step needs a
# figure another module owns, the step calls a hook declared here and the
# owning module overrides it. A hook that nobody has overridden refuses: a
# step that needs a computed figure must never fall back to a typed one
# (A09 audit M21: a typed 9,999,999 settlement was accepted).
#
#   I1  fix.hr.exit._fix_settlement_breakdown()       owner: cd_payroll_bd
#   I2  hr.employee._fix_unused_annual_leave_days()   owner: the leave
#       controls in this module (fix_leave_controls.py)
from datetime import date

from odoo import fields, models
from odoo.exceptions import UserError


class FixHrExitSettlementHook(models.Model):
    _inherit = "fix.hr.exit"

    def _fix_settlement_breakdown(self):
        """The final settlement for this exit, computed by payroll.

        Returns {"lines": [(label, amount), ...], "net": float, "basis": str}.
        cd_payroll_bd overrides this; without it there is no settlement figure
        to approve, so settling is refused rather than taking a typed amount."""
        self.ensure_one()
        raise UserError(
            "The final settlement for %s is computed by payroll (cd_payroll_bd), "
            "which is not installed." % self.employee_id.display_name
        )


class HrEmployeeLeaveBalanceHook(models.Model):
    _inherit = "hr.employee"

    def _fix_unused_annual_leave_days(self, as_of=None):
        """Annual (earned) leave days still unused at `as_of` (default today).

        The source for leave encashment at exit (BLA s.117(4)) and for the
        payslip's unused_leave_days. This placeholder keeps the pre-audit
        rule (entitlement less approved days this calendar year); the leave
        controls replace it with the statutory accrual."""
        self.ensure_one()
        as_of = fields.Date.to_date(as_of) if as_of else fields.Date.context_today(self)
        Type = self.env["fix.leave.type"].sudo()
        annual = Type.search([("code", "=", "annual")], limit=1)
        if not annual:
            return 0.0
        taken = sum(
            self.env["fix.leave.request"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", self.id),
                    ("leave_type_id", "=", annual.id),
                    ("state", "=", "approved"),
                    ("date_from", ">=", date(as_of.year, 1, 1)),
                    ("date_from", "<=", as_of),
                ]
            )
            .mapped("days")
        )
        return max(float(annual.entitlement_days or 0) - taken, 0.0)
