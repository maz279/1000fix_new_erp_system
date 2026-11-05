# fix_payroll_gratuity — FR-PAY-022 / AUT-PAY-10: the monthly gratuity
# provision (A09 round 2).
#
# The audit found gratuity computed only at separation, with no accrual, so
# the liability never reached the books until someone left (M56 §4, BRU-PAY-11).
# A monthly cron now records, per employee under an active contract, the
# gratuity the company would owe at the month end under the EXISTING
# separation rule (the engine bands the statutory pack names: nothing new is
# ruled here) and the month's movement against the previous month's figure.
# It is idempotent: one row per employee and month, a re-run adds nothing.
# When finance has configured the gratuity expense and provision accounts,
# the month's net movement per company is posted (Dr expense / Cr provision,
# reversed for a release); until then the rows are the provision register.
import calendar
from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.payroll_engine import completed_years, gratuity

from .fix_payroll_disbursement import post_two_line_entry
from .fix_payroll_statutory import statutory_basis


class FixPayrollGratuityAccrual(models.Model):
    _name = "fix.payroll.gratuity.accrual"
    _description = "Gratuity Provision (monthly accrual)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "month desc, employee_id"

    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", readonly=True)
    employee_id = fields.Many2one("hr.employee", required=True, index=True, readonly=True)
    contract_id = fields.Many2one("fix.employment.contract", readonly=True)
    month = fields.Char(required=True, index=True, readonly=True, help="YYYY-MM")
    as_of = fields.Date(required=True, readonly=True)
    completed_years = fields.Integer(readonly=True)
    currency_id = fields.Many2one("res.currency", readonly=True)
    basic = fields.Monetary(currency_field="currency_id", readonly=True)
    liability = fields.Monetary(
        currency_field="currency_id", readonly=True, string="Gratuity Owed at Month End"
    )
    previous_liability = fields.Monetary(currency_field="currency_id", readonly=True)
    accrual = fields.Monetary(
        currency_field="currency_id", readonly=True, string="Month's Provision Movement"
    )
    statutory_basis = fields.Char(readonly=True)
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True)

    _employee_month_unique = models.Constraint(
        "UNIQUE (employee_id, month)", "One gratuity provision row per employee and month."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "company_id",
            "operating_unit_id",
            "employee_id",
            "contract_id",
            "month",
            "as_of",
            "completed_years",
            "currency_id",
            "basic",
            "liability",
            "previous_liability",
            "accrual",
            "statutory_basis",
            "move_id",
        }

    @api.model
    def _accrue_month(self, as_of):
        """Rows for the month ending `as_of`; returns the rows it created."""
        month = as_of.strftime("%Y-%m")
        Accrual = self.sudo()._guarded()
        Contract = self.env["fix.employment.contract"].sudo()
        contracts = Contract.search(
            [("state", "=", "active"), ("joining_date", "<=", as_of)],
            order="employee_id, joining_date desc, id desc",
        )
        done = set(Accrual.search([("month", "=", month)]).mapped("employee_id").ids)
        seen = set()
        vals_list = []
        for contract in contracts:
            emp = contract.employee_id
            if emp.id in seen or emp.id in done:
                continue
            seen.add(emp.id)
            company = contract.company_id or emp.company_id
            joining = fields.Date.to_date(contract.joining_date)
            basic = Decimal(str(contract.basic_monthly or 0.0))
            owed = float(gratuity(basic, joining, as_of)) if basic > 0 else 0.0
            previous = Accrual.search(
                [("employee_id", "=", emp.id), ("month", "<", month)], order="month desc", limit=1
            )
            prev = previous.liability if previous else 0.0
            pack = self.env["fix.statutory.pack"]._pack_for(company, as_of)
            vals_list.append(
                {
                    "company_id": company.id,
                    "employee_id": emp.id,
                    "contract_id": contract.id,
                    "month": month,
                    "as_of": as_of,
                    "completed_years": completed_years(joining, as_of),
                    "currency_id": company.currency_id.id,
                    "basic": float(basic),
                    "liability": owed,
                    "previous_liability": prev,
                    "accrual": round(owed - prev, 2),
                    "statutory_basis": statutory_basis(company, pack),
                }
            )
        rows = Accrual.create(vals_list)
        for company in rows.mapped("company_id"):
            mine = rows.filtered(lambda r, c=company: r.company_id == c)
            rows._post(company, mine, month, as_of)
        return rows

    def _post(self, company, rows, month, as_of):
        """The month's net movement to the GL, once finance configured it."""
        if not (
            company.payroll_journal_id
            and company.payroll_gratuity_expense_account_id
            and company.payroll_gratuity_provision_account_id
        ):
            return
        net = company.currency_id.round(sum(rows.mapped("accrual")))
        if company.currency_id.is_zero(net):
            return
        debit, credit = (
            ("payroll_gratuity_expense_account_id", "payroll_gratuity_provision_account_id")
            if net > 0
            else ("payroll_gratuity_provision_account_id", "payroll_gratuity_expense_account_id")
        )
        move = post_two_line_entry(
            self.env(su=True),
            company,
            "Gratuity Provision - %s" % month,
            as_of,
            abs(net),
            "Gratuity provision %s (%d employees)" % (month, len(rows)),
            debit,
            credit,
        )
        rows._guarded().write({"move_id": move.id})

    @api.model
    def cron_accrue_gratuity(self, as_of=None):
        """Monthly: the provision as at the end of the last completed month.
        Idempotent (one row per employee and month)."""
        if as_of:
            day = fields.Date.to_date(as_of)
        else:
            first = fields.Date.context_today(self).replace(day=1)
            day = first - relativedelta(days=1)
        last = date(day.year, day.month, calendar.monthrange(day.year, day.month)[1])
        if day != last:
            raise UserError("A gratuity provision is taken as at a month end, not %s." % day)
        return len(self.sudo()._accrue_month(last))
