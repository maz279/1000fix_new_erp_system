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
from datetime import timedelta

from odoo import fields, models
from odoo.exceptions import AccessError, UserError

from .fix_payroll_statutory import (
    death_rules,
    notice_served_days,
    separation_figures,
    statutory_basis,
)

# A contract that RAN: active now, or ended (terminated, expired, superseded).
# A fixed-term contract the expiry cron moved to "expired" is what a
# contract-end exit is settled on; it was refused before (M21 audit E7).
RAN_STATES = ("active", "terminated", "expired", "superseded")

# M56-F21: BLA 2006 s.30 and s.123(2) - every due is payable within 30
# WORKING days of the termination (sourced statutory figure: Friday/Saturday
# weekend, confirmed company holidays excluded).
SETTLEMENT_DUE_WORKING_DAYS = 30


def settlement_due_date(env, company, last_working_day):
    """The statutory final-settlement due date: `last_working_day` plus 30
    WORKING days. A working day is no Friday, no Saturday (the estate's
    weekend) and no confirmed company holiday of `fix.hr.holiday`. False when
    there is no last working day."""
    if not last_working_day:
        return False
    day = fields.Date.to_date(last_working_day)
    holidays = set()
    Holiday = env.get("fix.hr.holiday")
    if Holiday is not None:
        holidays = {
            fields.Date.to_date(h.date)
            for h in Holiday.sudo().search(
                [
                    ("company_id", "=", company.id if company else False),
                    ("date", ">", day),
                    ("tentative", "=", False),
                ]
            )
        }
    left = SETTLEMENT_DUE_WORKING_DAYS
    while left > 0:
        day += timedelta(days=1)
        if day.weekday() in (4, 5) or day in holidays:  # Friday, Saturday
            continue
        left -= 1
    return day


def separation_contract(env, employee, as_of, pinned=None):
    """(basic, joining date) for a separation at `as_of`.

    The basic is the exit's PINNED contract (the one in force when its notice
    was confirmed) when there is one, otherwise the latest contract that ran.
    A draft version the settlement closed (terminated, never activated) is
    never the basic: it made the settled figure unpayable (M21 audit E8).
    Service runs from the earliest contract that ran."""
    contracts = (
        env["fix.employment.contract"]
        .sudo()
        .search(
            [("employee_id", "=", employee.id), ("joining_date", "<=", as_of)],
            order="joining_date desc, id desc",
        )
    )
    never_ran = "activated_on" in contracts._fields

    def ran(c):
        if c.state not in RAN_STATES:
            return False
        return not (
            never_ran and c.state == "terminated" and c.previous_contract_id and not c.activated_on
        )

    ran_contracts = contracts.filtered(ran)
    if not ran_contracts:
        raise UserError(
            "No active or terminated contract of %s starts on or before %s (none that ever "
            "ran): there is no basic to compute a separation from." % (employee.display_name, as_of)
        )
    current = ran_contracts.filtered(lambda c: c.state != "superseded") or ran_contracts
    basic_from = pinned if pinned and pinned in ran_contracts else current[0]
    return basic_from.basic_monthly, fields.Date.to_date(ran_contracts[-1].joining_date)


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
        pinned = self.contract_id if "contract_id" in self._fields else None
        basic, joining = separation_contract(self.env, employee, last_day, pinned=pinned)
        death = {}
        if self.exit_type == "death":
            min_years, at_work = death_rules(self)
            death = {"death_min_service_years": min_years, "death_at_work": at_work}
        years, lines = separation_figures(
            basic,
            joining,
            last_day,
            self.exit_type,
            notice_served_days=notice_served_days(self.notice_date, last_day),
            unused_leave_days=unused_leave_days(employee, last_day),
            **death,
            **self._fix_settlement_notice_terms(),
        )
        company = self.company_id or employee.company_id
        # M56-11: the statutory pack in force on the last day names the rule set
        pack = self.env["fix.statutory.pack"]._pack_for(company, last_day)
        net = float(sum(amount for _key, _label, amount in lines))
        basis = (
            "exit=%s; joined=%s; last_day=%s; completed_years=%d; basic=%.2f; %s; "
            "final month's salary is paid by the monthly run prorated to the last day (I3)"
            % (self.exit_type, joining, last_day, years, basic, statutory_basis(company, pack))
        )
        return {
            "lines": [(label, float(amount)) for _key, label, amount in lines],
            "net": round(net, 2),
            "basis": basis,
        }

    def _fix_settlement_notice_terms(self):
        """The notice terms M21 decided at confirmation, for payroll's lines:
        the notice the exit requires (s.26: 120 days permanent, 30 temporary),
        whether the worker is permanent (s.26(4) compensation), and the days a
        resigning worker pays in lieu (s.27(3), "Wages in Lieu of Notice")."""
        self.ensure_one()
        terms = {}
        contract = self.contract_id if "contract_id" in self._fields else None
        if contract:
            terms["permanent"] = contract.contract_type == "permanent"
        if "notice_required_days" in self._fields and self.exit_type == "termination":
            terms["notice_required_days"] = self.notice_required_days
        if (
            "notice_shortfall_treatment" in self._fields
            and self.exit_type == "resignation"
            and self.notice_shortfall_treatment == "pay_in_lieu"
        ):
            terms["shortfall_recovery_days"] = self.notice_shortfall_days
        return terms

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
            if rec.exit_type == "death":
                # BLA s.19: the benefit goes to the NOMINEES, one payment each,
                # with the share M21 pinned at settlement
                created |= rec._fix_nominee_payments(OffCycle, user, breakdown)
                continue
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

    def _fix_nominee_payments(self, OffCycle, user, breakdown):
        """One DRAFT off-cycle per pinned nominee payee of a death exit. The
        payees and amounts are M21's pin (exit._fix_nominee_payees()); they
        must add up to the settlement net."""
        self.ensure_one()
        payees = self._fix_nominee_payees() if hasattr(self, "_fix_nominee_payees") else []
        if not payees:
            raise UserError(
                "Exit %s has no pinned nominee split: compute its settlement first (BLA s.19 "
                "pays the nominees)." % self.display_name
            )
        currency = self.currency_id or self.env.ref("base.BDT")
        total = currency.round(sum(float(p.get("amount") or 0.0) for p in payees))
        if currency.compare_amounts(total, breakdown["net"]) != 0:
            raise UserError(
                "Exit %s's nominee split totals %.2f but the settlement is %.2f."
                % (self.display_name, total, breakdown["net"])
            )
        created = OffCycle
        for payee in payees:
            amount = float(payee.get("amount") or 0.0)
            if amount <= 0:
                continue
            created |= OffCycle._guarded().create(
                {
                    "prepared_by_id": user.id,
                    "employee_id": self.employee_id.id,
                    "company_id": self.company_id.id,
                    "payment_type": "settlement",
                    "payment_date": fields.Date.context_today(self),
                    "exit_id": self.id,
                    "amount": amount,
                    "nominee_dependant_id": payee.get("dependant_id") or False,
                    "nominee_name": payee.get("name") or False,
                    "nominee_share_pct": float(payee.get("share_pct") or 0.0),
                    "reason": "Death-in-service settlement of %s (BLA s.19): %s, %.2f%% nominee"
                    % (self.display_name, payee.get("name") or "?", payee.get("share_pct") or 0.0),
                }
            )
        return created
