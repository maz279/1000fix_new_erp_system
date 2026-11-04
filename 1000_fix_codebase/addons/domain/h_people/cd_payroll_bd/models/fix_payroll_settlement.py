# fix_payroll_settlement — M56's side of the exit hand-off (A09 interface I1).
#
# The A09 audit found a typed 9,999,999 final settlement accepted (M21), a
# "Compute Separation" button that always failed, and computed gratuity that
# never reached a payment (M56-12). Payroll now computes the settlement:
#   * fix.hr.exit._fix_settlement_breakdown() returns the lines, the net and
#     the basis (the rule set pinned from the company's decision flags); M21's
#     settle step pins that net and never takes a typed figure;
#   * action_create_settlement_payment() turns a SETTLED exit into a DRAFT
#     off-cycle payment of exactly that net, which then goes through its own
#     routed approval, release, BEFTN file and GL entry.
from odoo import fields, models
from odoo.exceptions import AccessError, UserError

from .fix_payroll_statutory import notice_served_days, separation_figures, statutory_basis


def separation_contract(env, employee, as_of):
    """(basic, joining date) for a separation at `as_of`: the basic of the
    latest active or terminated contract, service from the earliest one."""
    contracts = (
        env["fix.employment.contract"]
        .sudo()
        .search(
            [
                ("employee_id", "=", employee.id),
                ("state", "in", ("active", "terminated")),
                ("joining_date", "<=", as_of),
            ],
            order="joining_date desc, id desc",
        )
    )
    if not contracts:
        raise UserError(
            "No active or terminated contract of %s starts on or before %s: there is no basic "
            "to compute a separation from." % (employee.display_name, as_of)
        )
    return contracts[0].basic_monthly, fields.Date.to_date(contracts[-1].joining_date)


def unused_leave_days(employee, as_of):
    """I2: the leave controls' figure, never a typed one."""
    return float(employee.sudo()._fix_unused_annual_leave_days(as_of=as_of) or 0.0)


class FixHrExitPayrollSettlement(models.Model):
    _inherit = "fix.hr.exit"

    def _fix_settlement_breakdown(self):
        """I1: {"lines": [(label, amount)], "net": float, "basis": str}."""
        self.ensure_one()
        employee = self.employee_id
        last_day = fields.Date.to_date(self.last_working_day)
        if not last_day:
            raise UserError("Set the last working day of %s before settling." % self.display_name)
        basic, joining = separation_contract(self.env, employee, last_day)
        years, lines = separation_figures(
            basic,
            joining,
            last_day,
            self.exit_type,
            notice_served_days=notice_served_days(self.notice_date, last_day),
            unused_leave_days=unused_leave_days(employee, last_day),
        )
        company = self.company_id or employee.company_id
        net = float(sum(amount for _key, _label, amount in lines))
        basis = (
            "exit=%s; joined=%s; last_day=%s; completed_years=%d; basic=%.2f; %s; "
            "final month's salary is paid by the monthly run prorated to the last day (I3)"
            % (self.exit_type, joining, last_day, years, basic, statutory_basis(company))
        )
        return {
            "lines": [(label, float(amount)) for _key, label, amount in lines],
            "net": round(net, 2),
            "basis": basis,
        }

    def action_create_settlement_payment(self):
        """A settled exit -> a DRAFT off-cycle payment of the pinned net."""
        user = self.env.user
        if not (
            self.env.su
            or user.has_group("cd_payroll_bd.group_payroll_officer")
            or user.has_group("cd_hr_core.group_hr_officer")
        ):
            raise AccessError("Only HR or payroll raises a final-settlement payment.")
        # The payment is created by this transition only (exit_id, amount and
        # payee are guarded on the off-cycle); the caller is its preparer.
        OffCycle = self.env["fix.payroll.offcycle"].sudo()
        created = OffCycle
        for rec in self:
            if rec.state != "settled":
                raise UserError(
                    "Exit %s is %s: only a settled exit is paid." % (rec.display_name, rec.state)
                )
            breakdown = rec._fix_settlement_breakdown()
            pinned = rec.settlement_amount or 0.0
            currency = rec.currency_id or rec.env.ref("base.BDT")
            if currency.compare_amounts(pinned, breakdown["net"]) != 0:
                raise UserError(
                    "Exit %s was settled at %.2f but payroll computes %.2f today: the settlement "
                    "no longer matches its computation, so nothing is paid from it."
                    % (rec.display_name, pinned, breakdown["net"])
                )
            existing = OffCycle.search([("exit_id", "=", rec.id), ("state", "!=", "cancelled")])
            if existing:
                raise UserError(
                    "Exit %s already has settlement payment %s."
                    % (rec.display_name, existing[0].name)
                )
            created |= OffCycle._guarded().create(
                {
                    "prepared_by_id": user.id,
                    "employee_id": rec.employee_id.id,
                    "company_id": rec.company_id.id,
                    "payment_type": "settlement",
                    "payment_date": fields.Date.context_today(rec),
                    "exit_id": rec.id,
                    "amount": breakdown["net"],
                    "reason": "Final settlement of %s: %s"
                    % (
                        rec.display_name,
                        "; ".join("%s %.2f" % line for line in breakdown["lines"]) or "no lines",
                    ),
                }
            )
        return {"offcycle_ids": created.ids}
