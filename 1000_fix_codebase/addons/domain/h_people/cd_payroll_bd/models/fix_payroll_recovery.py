# fix_payroll_recovery — BRU-PAY-04 / T-07 (A09 round 2, second pass): an
# OVERPAID salary is recovered as a deduction on the employee's next runs,
# never by editing the paid slip.
#
#   * a recovery names the paid payslip it corrects, the amount and why; it is
#     a routed decision (a Payroll Manager who did not prepare it);
#   * once approved, each monthly calculation deducts what is still owed,
#     up to the company's monthly cap (a setting; 0 = the whole balance in the
#     next run) and never more than the slip's net, and records a line on the
#     slip; a recalculation of that run releases the line (it is deleted with
#     the slip it rode) and the next calculation takes it again;
#   * the deduction is after tax (a net overpayment comes back net) and is
#     booked to the company's overpayment-recovery account.
#
# M56 capture audit (2026-11-17), FR-PAY-031/032/033: a SALARY ADVANCE paid as
# an off-cycle payment was never recovered - nothing deducted it and nothing
# recorded what the employee owed. The same record now also carries an advance
# recovery schedule: it names the advance, the amount owed and the monthly
# instalment; it is routed like an overpayment; the advance is released to the
# bank only once its approved schedule covers it; and each monthly run deducts
# the instalment (after tax, within the monthly cap) until it is repaid. An
# advance is recovered only through the monthly run, never from a bonus or
# another off-cycle payment.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_payroll_ops import PAID_PERIOD_STATES, routed_payroll_decision
from .fix_payroll_statutory import digest_rows

PAYROLL_OFFICER = "cd_payroll_bd.group_payroll_officer"
PAYROLL_MANAGER = "cd_payroll_bd.group_payroll_manager"


class FixPayrollRecovery(models.Model):
    _name = "fix.payroll.recovery"
    _description = "Salary Overpayment Recovery"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "fix.people.approval.mixin",
        "fix.payroll.state.lock",
    ]
    _order = "id desc"

    _approval_domain = "hr_offcycle"
    _approval_apply_method = "action_approve"
    _approval_group = PAYROLL_MANAGER

    name = fields.Char(default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")
    recovery_type = fields.Selection(
        [("overpayment", "Salary Overpayment"), ("advance", "Salary Advance")],
        string="Recovers",
        required=True,
        default="overpayment",
        index=True,
    )
    # an overpayment names the paid payslip it corrects (enforced below)
    correction_slip_id = fields.Many2one(
        "fix.payslip", string="Overpaid Payslip", index=True, ondelete="restrict"
    )
    # an advance names the off-cycle advance it recovers
    advance_id = fields.Many2one(
        "fix.payroll.offcycle",
        string="Salary Advance",
        index=True,
        ondelete="restrict",
        domain=[("payment_type", "=", "advance")],
    )
    instalment = fields.Monetary(
        currency_field="currency_id",
        string="Monthly Instalment",
        help="Deducted from each monthly run until repaid; 0 = the whole balance, "
        "within the company's monthly cap.",
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True, string="Overpaid Amount")
    reason = fields.Text(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
    )
    prepared_by_id = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user, string="Prepared By"
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, string="Approved By")
    approved_on = fields.Datetime(readonly=True)
    approved_digest = fields.Char(readonly=True)
    line_ids = fields.One2many("fix.payroll.recovery.line", "recovery_id", readonly=True)
    recovered_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_recovered", store=True
    )
    remaining_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_recovered", store=True
    )
    fully_recovered = fields.Boolean(compute="_compute_recovered", store=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "prepared_by_id",
            "approved_by_id",
            "approved_on",
            "approved_digest",
            "line_ids",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft" or self.approval_state == "pending":
            locked |= {"correction_slip_id", "employee_id", "amount", "reason", "company_id"}
            locked |= {"recovery_type", "advance_id", "instalment"}
            locked |= {"currency_id", "operating_unit_id"}
        return locked

    @api.depends("amount", "line_ids.amount")
    def _compute_recovered(self):
        for rec in self:
            done = round(sum(rec.line_ids.mapped("amount")), 2)
            rec.recovered_amount = done
            rec.remaining_amount = round(max((rec.amount or 0.0) - done, 0.0), 2)
            rec.fully_recovered = bool(rec.amount) and rec.remaining_amount <= 0.0

    @api.constrains(
        "amount",
        "correction_slip_id",
        "employee_id",
        "company_id",
        "recovery_type",
        "advance_id",
        "instalment",
    )
    def _check_recovery(self):
        for rec in self:
            if rec.instalment < 0:
                raise ValidationError("A monthly instalment is not negative.")
            if rec.recovery_type == "advance":
                rec._check_advance_schedule()
                continue
            slip = rec.correction_slip_id.sudo()
            if not slip:
                raise ValidationError("An overpayment recovery names the paid payslip it corrects.")
            if rec.advance_id:
                raise ValidationError("An overpayment recovery names no advance.")
            if rec.amount <= 0:
                raise ValidationError("An overpayment recovery is a positive amount.")
            if slip.period_id.state not in PAID_PERIOD_STATES:
                raise ValidationError(
                    "Only a PAID payslip's overpayment is recovered; an unpaid run is recalculated."
                )
            if slip.employee_id != rec.employee_id or slip.company_id != rec.company_id:
                raise ValidationError(
                    "A recovery is taken from the employee and company of the payslip it corrects."
                )
            if rec.amount > slip.net + 1e-6:
                raise ValidationError(
                    "A recovery of %.2f exceeds the %.2f the payslip paid." % (rec.amount, slip.net)
                )

    def _check_advance_schedule(self):
        """An advance schedule recovers one off-cycle salary advance of the same
        employee and company, never more than was advanced, once."""
        self.ensure_one()
        adv = self.advance_id.sudo()
        if not adv or adv.payment_type != "advance":
            raise ValidationError("An advance recovery names the salary advance it recovers.")
        if self.correction_slip_id:
            raise ValidationError("An advance recovery names no payslip.")
        if adv.state == "cancelled":
            raise ValidationError("Advance %s is cancelled: nothing to recover." % adv.name)
        if adv.employee_id != self.employee_id or adv.company_id != self.company_id:
            raise ValidationError(
                "An advance is recovered from the employee and company it was paid to."
            )
        if self.amount <= 0:
            raise ValidationError("An advance recovery is a positive amount.")
        if self.amount > adv.amount + 1e-6:
            raise ValidationError(
                "A recovery of %.2f exceeds the %.2f advanced." % (self.amount, adv.amount)
            )
        if self.instalment > self.amount + 1e-6:
            raise ValidationError("The monthly instalment cannot exceed the amount owed.")
        others = self.sudo().search(
            [("advance_id", "=", adv.id), ("state", "!=", "cancelled"), ("id", "!=", self.id)]
        )
        if others:
            raise ValidationError(
                "Advance %s already has recovery schedule %s." % (adv.name, others[0].name)
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not (self.env.su or self.env.user.has_group(PAYROLL_OFFICER)):
            raise AccessError("Only payroll raises an overpayment recovery.")
        for vals in vals_list:
            if vals.get("advance_id"):
                adv = self.env["fix.payroll.offcycle"].sudo().browse(vals["advance_id"])
                vals.setdefault("recovery_type", "advance")
                vals.setdefault("employee_id", adv.employee_id.id)
                vals.setdefault("company_id", adv.company_id.id)
                if not vals.get("amount"):
                    vals["amount"] = adv.amount
            if vals.get("correction_slip_id"):
                slip = self.env["fix.payslip"].sudo().browse(vals["correction_slip_id"])
                vals.setdefault("employee_id", slip.employee_id.id)
                vals.setdefault("company_id", slip.company_id.id)
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"name": "REC/%d" % rec.id})
        return records

    # ---- the routed decision -------------------------------------------------
    def _approval_amount(self) -> float:
        return float(self.amount or 0.0)

    def _approval_preparers(self):
        return (self.prepared_by_id | self.create_uid).sudo()

    def _digest(self):
        self.ensure_one()
        if self.recovery_type == "advance":
            return digest_rows(
                [
                    (
                        "advance",
                        str(self.id),
                        str(self.advance_id.id),
                        str(self.employee_id.id),
                        "%.2f" % self.amount,
                        "%.2f" % (self.instalment or 0.0),
                    )
                ]
            )
        return digest_rows(
            [
                (
                    str(self.id),
                    str(self.correction_slip_id.id),
                    str(self.employee_id.id),
                    "%.2f" % self.amount,
                )
            ]
        )

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft recovery is sent for approval.")
            if not (rec.reason or "").strip():
                raise UserError(
                    "State the advance's repayment terms."
                    if rec.recovery_type == "advance"
                    else "State what was overpaid and why."
                )
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        routed_payroll_decision(
            self, "an overpayment recovery", lambda rec: rec._approval_preparers()
        )
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a draft recovery.")
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": rec._people_decider().id,
                    "approved_on": fields.Datetime.now(),
                    "approved_digest": rec._digest(),
                }
            )

    def action_cancel(self):
        for rec in self:
            if rec.approval_state == "pending":
                raise UserError("Recall the approval request before cancelling %s." % rec.name)
            if rec.line_ids:
                raise UserError("Recovery %s has already been partly recovered." % rec.name)
            if rec.state == "approved" and not (
                self.env.su or self.env.user.has_group(PAYROLL_MANAGER)
            ):
                raise AccessError("Only a Payroll Manager cancels an approved recovery.")
            rec._guarded().write({"state": "cancelled"})
        return True

    # ---- what a calculation deducts ------------------------------------------
    @api.model
    def _due(self, employee, company, month, available, extra_domain=(), include_advance=False):
        """[(recovery, amount)] a payment of `available` net to `employee` in
        `month` (YYYY-MM) deducts: approved, unchanged recoveries still owing,
        oldest first. The company's monthly cap holds per recovery across
        EVERY payment of the month (run, off-cycle, bonus); together never
        more than the payment's net. An advance schedule is due only on the
        monthly run (`include_advance`), once its advance was paid, and at
        most its own instalment a month."""
        kinds = ["overpayment", "advance"] if include_advance else ["overpayment"]
        recs = self.sudo().search(
            [
                ("employee_id", "=", employee.id),
                ("company_id", "=", company.id),
                ("state", "=", "approved"),
                ("fully_recovered", "=", False),
                ("recovery_type", "in", kinds),
                "|",
                ("recovery_type", "=", "overpayment"),
                ("advance_id.state", "in", ("paid", "posted")),
                *extra_domain,
            ],
            order="id",
        )
        company_cap = company.payroll_recovery_monthly_cap or 0.0
        available = max(available or 0.0, 0.0)
        out = []
        for rec in recs:
            if rec.approved_digest != rec._digest():
                continue  # changed after approval (tampered row): never deducted
            take = rec.remaining_amount
            caps = [c for c in (company_cap, rec.instalment or 0.0) if c > 0]
            cap = min(caps) if caps else 0.0
            if cap > 0:
                this_month = sum(
                    rec.line_ids.filtered(lambda ln: ln.month == month).mapped("amount")
                )
                take = min(take, max(cap - this_month, 0.0))
            take = round(min(take, available), 2)
            if take <= 0:
                continue
            out.append((rec, take))
            available -= take
        return out

    @api.model
    def _due_for(self, slip):
        """What a monthly payslip deducts (never a recovery of its own run)."""
        return self._due(
            slip.employee_id,
            slip.company_id,
            slip.period_id.period_start.strftime("%Y-%m"),
            slip.net,
            [
                "|",
                ("correction_slip_id", "=", False),
                ("correction_slip_id.period_id", "!=", slip.period_id.id),
            ],
            include_advance=True,
        )

    @api.model
    def _record(self, due, month, **target):
        """The recovery lines of one payment; returns their total."""
        if not due:
            return 0.0
        self.env["fix.payroll.recovery.line"].sudo()._guarded().create(
            [
                {"recovery_id": rec.id, "amount": amount, "month": month, **target}
                for rec, amount in due
            ]
        )
        return round(sum(amount for _rec, amount in due), 2)

    @api.model
    def _apply(self, slip):
        """Deduct what is due on a freshly calculated slip and record the lines."""
        due = self._due_for(slip)
        if not due:
            return 0.0
        total = round(sum(amount for _rec, amount in due), 2)
        slip._guarded().write({"recovery_deduction": total})
        self._record(due, slip.period_id.period_start.strftime("%Y-%m"), slip_id=slip.id)
        return total


class FixPayrollRecoveryLine(models.Model):
    _name = "fix.payroll.recovery.line"
    _description = "Salary Overpayment Recovery Deduction"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id"

    recovery_id = fields.Many2one(
        "fix.payroll.recovery", required=True, ondelete="cascade", index=True, readonly=True
    )
    company_id = fields.Many2one(related="recovery_id.company_id", store=True)
    operating_unit_id = fields.Many2one("operating.unit", readonly=True)
    currency_id = fields.Many2one(related="recovery_id.currency_id")
    # the payment it rode - a payslip, an off-cycle payment or a festival
    # bonus line - and is released with: a recalculation, a recompute or a
    # recalled request takes it again
    slip_id = fields.Many2one("fix.payslip", ondelete="cascade", index=True, readonly=True)
    offcycle_id = fields.Many2one(
        "fix.payroll.offcycle", ondelete="cascade", index=True, readonly=True
    )
    bonus_line_id = fields.Many2one(
        "fix.payroll.bonus.line", ondelete="cascade", index=True, readonly=True
    )
    month = fields.Char(index=True, readonly=True, help="YYYY-MM the deduction falls in")
    amount = fields.Monetary(currency_field="currency_id", readonly=True)

    _one_payment = models.Constraint(
        "CHECK (num_nonnulls(slip_id, offcycle_id, bonus_line_id) = 1)",
        "A recovery deduction rides exactly one payment.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "recovery_id",
            "operating_unit_id",
            "slip_id",
            "offcycle_id",
            "bonus_line_id",
            "month",
            "amount",
        }
