# fix_payroll_capture - M56 capture audit (2026-11-17): the records the
# Income Tax, Provident Fund, Gratuity and Loans & Advances pages had no way
# to capture, although the calculation needs them.
#
#   * fix.investment.declaration (FR-PAY-013/014, BRU-PAY-10 H): the payslip
#     sent the engine an investment of 0 because "there is no declaration
#     model", so no employee ever received the investment rebate. A declaration
#     is recorded by payroll with its evidence and validated by a SECOND
#     payroll user (never the recorder, never the employee); the validated
#     eligible amounts of the fiscal year are what the calculation now sends.
#   * fix.pf.member (FR-PAY-020): every payslip deducted 10% + 10% provident
#     fund whatever the employee's membership. A membership names the rates
#     and the date the employee joined the fund, with the opening balances
#     taken on, and is approved by a Payroll Manager who did not record it.
#     ONLY members contribute, at their own rates (M56-F12): a company with
#     an empty register pays no PF at all - a fund that does not exist (spec
#     Q-03) is not deducted from anyone by default.
#   * fix.payroll.gratuity.opening (FR-PAY-022, spec Q-05 and 16.4): the
#     first monthly accrual of an employee treated the whole historical
#     liability as that month's movement and posted it as one month's expense,
#     although the books may already carry the provision. An opening
#     provision, taken on from the legacy books with its evidence and approved
#     by a second Payroll Manager, is what the first accrual moves from.
#   * Salary advances (FR-PAY-031/032): an advance is released to the bank
#     only once its approved recovery schedule (fix.payroll.recovery,
#     recovery_type = advance) covers it.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_payroll_statutory import fiscal_year_bounds

PAYROLL_OFFICER = "cd_payroll_bd.group_payroll_officer"
PAYROLL_MANAGER = "cd_payroll_bd.group_payroll_manager"


def _payroll_only(env, what):
    if not (env.su or env.user.has_group(PAYROLL_OFFICER)):
        raise AccessError("Only payroll %s." % what)


def _second_person(rec, what, manager=False):
    """The decision of a payroll user who neither recorded the record nor is
    its employee; a Payroll Manager where `manager`."""
    env = rec.env
    if env.su:
        return
    group = PAYROLL_MANAGER if manager else PAYROLL_OFFICER
    if not env.user.has_group(group):
        raise AccessError(
            "Only a %s %s." % ("Payroll Manager" if manager else "payroll user", what)
        )
    if env.user in (rec.recorded_by_id | rec.create_uid):
        raise UserError("A second payroll user %s: it was recorded by you." % what)
    if rec.employee_id.sudo().user_id == env.user:
        raise UserError("Nobody %s for themself." % what)


# ------------------------------------------------------- investment declaration


class FixInvestmentDeclaration(models.Model):
    _name = "fix.investment.declaration"
    _description = "Investment Declaration (tax rebate)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.payroll.state.lock"]
    _order = "fy_start desc, employee_id, id desc"

    name = fields.Char(default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    fiscal_year = fields.Char(
        required=True, string="Income Year", help="Bangladesh fiscal year, e.g. 2026-27"
    )
    fy_start = fields.Date(compute="_compute_fy_start", store=True, index=True)
    instrument = fields.Selection(
        [
            ("savings_certificate", "Sanchayapatra / Savings Certificate"),
            ("dps", "Deposit Pension Scheme (DPS)"),
            ("life_insurance", "Life Insurance Premium"),
            ("listed_shares", "Listed Shares / Mutual Fund"),
            ("govt_securities", "Government Securities / Bonds"),
            ("approved_pension", "Approved Pension / Superannuation Fund"),
            ("other", "Other Eligible Investment (ITA 2023 Sch. 6 Part 3)"),
        ],
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    declared_amount = fields.Monetary(currency_field="currency_id", required=True)
    eligible_amount = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        string="Eligible Amount (validated)",
        help="What the validator accepted from the evidence; the rebate is computed on it.",
    )
    evidence_file = fields.Binary(string="Evidence", attachment=True)
    evidence_filename = fields.Char()
    note = fields.Text(string="Details (certificate / policy number)")
    state = fields.Selection(
        [
            ("draft", "Declared"),
            ("validated", "Validated"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
    )
    recorded_by_id = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user, string="Recorded By"
    )
    validated_by_id = fields.Many2one("res.users", readonly=True, string="Validated By")
    validated_on = fields.Datetime(readonly=True)
    rejection_reason = fields.Text(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "eligible_amount",
            "recorded_by_id",
            "validated_by_id",
            "validated_on",
            "rejection_reason",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {
                "employee_id",
                "fiscal_year",
                "instrument",
                "declared_amount",
                "evidence_file",
                "evidence_filename",
                "company_id",
                "currency_id",
            }
        return locked

    @api.depends("fiscal_year")
    def _compute_fy_start(self):
        for rec in self:
            try:
                rec.fy_start = fiscal_year_bounds(rec.fiscal_year)[0] if rec.fiscal_year else False
            except UserError:
                rec.fy_start = False

    @api.constrains("fiscal_year", "declared_amount")
    def _check_declaration(self):
        for rec in self:
            fiscal_year_bounds(rec.fiscal_year)
            if rec.declared_amount <= 0:
                raise ValidationError("A declared investment is a positive amount.")

    @api.model_create_multi
    def create(self, vals_list):
        _payroll_only(self.env, "records an investment declaration")
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"name": "INV/%d" % rec.id})
        return records

    def action_validate(self, eligible_amount=None):
        """A second payroll user accepts the declaration against its evidence,
        at the declared amount or a lower eligible amount."""
        for rec in self:
            _second_person(rec, "validates an investment declaration")
            if rec.state != "draft":
                raise UserError("Only a declared investment is validated.")
            if not rec.evidence_file:
                raise UserError("Attach the evidence before validating %s." % rec.name)
            eligible = rec.declared_amount if eligible_amount in (None, "") else eligible_amount
            try:
                eligible = round(float(eligible), 2)
            except (TypeError, ValueError) as err:
                raise UserError("The eligible amount is a number.") from err
            if eligible <= 0 or eligible > rec.declared_amount + 1e-6:
                raise UserError(
                    "The eligible amount is more than 0 and at most the %.2f declared."
                    % rec.declared_amount
                )
            rec._guarded().write(
                {
                    "state": "validated",
                    "eligible_amount": eligible,
                    "validated_by_id": self.env.user.id,
                    "validated_on": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why the declaration is rejected.")
        for rec in self:
            _second_person(rec, "rejects an investment declaration")
            if rec.state != "draft":
                raise UserError("Only a declared investment is rejected.")
            rec._guarded().write(
                {
                    "state": "rejected",
                    "rejection_reason": reason.strip(),
                    "validated_by_id": self.env.user.id,
                    "validated_on": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self):
        for rec in self:
            _payroll_only(self.env, "cancels an investment declaration")
            if rec.state == "validated" and not (
                self.env.su or self.env.user.has_group(PAYROLL_MANAGER)
            ):
                raise AccessError("Only a Payroll Manager withdraws a validated declaration.")
            if rec.state in ("rejected", "cancelled"):
                raise UserError("Declaration %s is already closed." % rec.name)
            rec._guarded().write({"state": "cancelled"})
        return True

    @api.model
    def _allowance_for(self, employee, company, day):
        """The validated eligible investment of `employee` for the fiscal year
        holding `day` - what the tax calculation sends as the investment."""
        start = fiscal_year_bounds("%d-%02d" % self._fy_years(day))[0]
        rows = self.sudo().search(
            [
                ("employee_id", "=", employee.id),
                ("company_id", "=", company.id),
                ("state", "=", "validated"),
                ("fy_start", "=", start),
            ]
        )
        return round(sum(rows.mapped("eligible_amount")), 2)

    @staticmethod
    def _fy_years(day):
        start_year = day.year if day.month >= 7 else day.year - 1
        return start_year, (start_year + 1) % 100


# ------------------------------------------------------------ provident fund


class FixPfMember(models.Model):
    _name = "fix.pf.member"
    _description = "Provident Fund Membership"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.payroll.state.lock"]
    _order = "joined_fund_on desc, id desc"

    name = fields.Char(default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    joined_fund_on = fields.Date(required=True, string="Joined the Fund On")
    employee_rate = fields.Float(
        required=True, default=10.0, string="Employee Contribution (% of basic)"
    )
    employer_rate = fields.Float(
        required=True, default=10.0, string="Employer Contribution (% of basic)"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    opening_as_of = fields.Date(string="Opening Balance As Of")
    opening_employee_balance = fields.Monetary(
        currency_field="currency_id", string="Opening Employee Balance"
    )
    opening_employer_balance = fields.Monetary(
        currency_field="currency_id", string="Opening Employer Balance"
    )
    evidence_file = fields.Binary(string="Evidence (nomination / fund statement)", attachment=True)
    evidence_filename = fields.Char()
    state = fields.Selection(
        [
            ("draft", "Recorded"),
            ("active", "Member"),
            ("left", "Left the Fund"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
    )
    recorded_by_id = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user, string="Recorded By"
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, string="Approved By")
    approved_on = fields.Datetime(readonly=True)
    left_on = fields.Date(readonly=True, string="Left the Fund On")
    leave_reason = fields.Text(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "recorded_by_id",
            "approved_by_id",
            "approved_on",
            "left_on",
            "leave_reason",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {
                "employee_id",
                "joined_fund_on",
                "employee_rate",
                "employer_rate",
                "opening_as_of",
                "opening_employee_balance",
                "opening_employer_balance",
                "evidence_file",
                "evidence_filename",
                "company_id",
                "currency_id",
            }
        return locked

    @api.constrains(
        "employee_rate",
        "employer_rate",
        "opening_employee_balance",
        "opening_employer_balance",
        "opening_as_of",
        "employee_id",
        "company_id",
        "state",
    )
    def _check_member(self):
        for rec in self:
            if not 0 < rec.employee_rate <= 100 or not 0 <= rec.employer_rate <= 100:
                raise ValidationError(
                    "Contribution rates are percentages of basic: the employee's above 0, "
                    "both at most 100."
                )
            if rec.opening_employee_balance < 0 or rec.opening_employer_balance < 0:
                raise ValidationError("An opening fund balance is not negative.")
            if (rec.opening_employee_balance or rec.opening_employer_balance) and not (
                rec.opening_as_of
            ):
                raise ValidationError("State the date the opening balance is taken on at.")
            if rec.state in ("draft", "active"):
                twin = self.sudo().search(
                    [
                        ("employee_id", "=", rec.employee_id.id),
                        ("company_id", "=", rec.company_id.id),
                        ("state", "in", ("draft", "active")),
                        ("id", "!=", rec.id),
                    ],
                    limit=1,
                )
                if twin:
                    raise ValidationError(
                        "%s already has fund membership %s." % (rec.employee_id.name, twin.name)
                    )

    @api.model_create_multi
    def create(self, vals_list):
        _payroll_only(self.env, "records a provident fund membership")
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"name": "PFM/%d" % rec.id})
        return records

    def action_approve(self):
        for rec in self:
            _second_person(rec, "approves a provident fund membership", manager=True)
            if rec.state != "draft":
                raise UserError("Only a recorded membership is approved.")
            rec._guarded().write(
                {
                    "state": "active",
                    "approved_by_id": self.env.user.id,
                    "approved_on": fields.Datetime.now(),
                }
            )
        return True

    def action_leave(self, reason=None):
        if not (reason or "").strip():
            raise UserError("State why the employee leaves the fund.")
        for rec in self:
            _second_person(rec, "closes a provident fund membership", manager=True)
            if rec.state != "active":
                raise UserError("Only an active member leaves the fund.")
            rec._guarded().write(
                {
                    "state": "left",
                    "left_on": fields.Date.context_today(self),
                    "leave_reason": reason.strip(),
                }
            )
        return True

    def action_cancel(self):
        for rec in self:
            _payroll_only(self.env, "cancels a provident fund membership")
            if rec.state != "draft":
                raise UserError("Only a recorded (unapproved) membership is cancelled.")
            rec._guarded().write({"state": "cancelled"})
        return True

    @api.model
    def _slip_rates(self, employee, company, period_start, period_end):
        """The PF rates a payslip of `period_start`..`period_end` computes with.

        M56-F12: a provident-fund deduction is taken ONLY from an employee
        with an approved membership in `fix.pf.member` covering the period, at
        THAT membership's rates; everyone else - including an employee of a
        company whose register is still empty - computes 0/0. The earlier
        "empty register means everyone pays 10% + 10%" default deducted a fund
        that does not exist (spec Q-03); it is gone. The rates a member pays
        are the membership's own (the register IS the ruled list of members)."""
        member = self.sudo().search(
            [
                ("employee_id", "=", employee.id),
                ("company_id", "=", company.id),
                ("joined_fund_on", "<=", period_end),
                "|",
                ("state", "=", "active"),
                "&",
                ("state", "=", "left"),
                ("left_on", ">=", period_start),
            ],
            order="joined_fund_on desc, id desc",
            limit=1,
        )
        if not member:
            return {"pf_employee_pct": 0.0, "pf_employer_pct": 0.0}
        return {"pf_employee_pct": member.employee_rate, "pf_employer_pct": member.employer_rate}


# -------------------------------------------------- gratuity opening provision


class FixGratuityOpening(models.Model):
    _name = "fix.payroll.gratuity.opening"
    _description = "Gratuity Opening Provision (take-on)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.payroll.state.lock"]
    _order = "as_of desc, id desc"

    name = fields.Char(default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    as_of = fields.Date(required=True, string="Provision As Of (month end)")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    opening_liability = fields.Monetary(
        currency_field="currency_id",
        required=True,
        string="Provision Carried in the Books",
    )
    legacy_reference = fields.Char(required=True, string="Legacy Ledger / Schedule Reference")
    evidence_file = fields.Binary(string="Evidence (provision schedule)", attachment=True)
    evidence_filename = fields.Char()
    note = fields.Text()
    state = fields.Selection(
        [("draft", "Recorded"), ("approved", "Approved"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
    )
    recorded_by_id = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user, string="Recorded By"
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, string="Approved By")
    approved_on = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "recorded_by_id",
            "approved_by_id",
            "approved_on",
        }

    def _payroll_state_locked_fields(self) -> set:
        locked = super()._payroll_state_locked_fields()
        if self.state != "draft":
            locked |= {
                "employee_id",
                "as_of",
                "opening_liability",
                "legacy_reference",
                "evidence_file",
                "evidence_filename",
                "company_id",
                "currency_id",
            }
        return locked

    @api.constrains("as_of", "opening_liability")
    def _check_opening(self):
        for rec in self:
            if rec.opening_liability < 0:
                raise ValidationError("An opening gratuity provision is not negative.")
            nxt = fields.Date.add(rec.as_of, days=1)
            if nxt.day != 1:
                raise ValidationError(
                    "An opening provision is taken as at a month end, not %s." % rec.as_of
                )

    @api.model_create_multi
    def create(self, vals_list):
        _payroll_only(self.env, "records an opening gratuity provision")
        records = super().create(vals_list)
        for rec in records:
            rec._guarded().write({"name": "GOP/%d" % rec.id})
        return records

    def action_approve(self):
        Accrual = self.env["fix.payroll.gratuity.accrual"].sudo()
        for rec in self:
            _second_person(rec, "approves an opening gratuity provision", manager=True)
            if rec.state != "draft":
                raise UserError("Only a recorded opening provision is approved.")
            if not rec.evidence_file:
                raise UserError("Attach the legacy provision schedule before approving.")
            if Accrual.search_count([("employee_id", "=", rec.employee_id.id)], limit=1):
                raise UserError(
                    "%s already has monthly gratuity provisions: an opening provision is "
                    "taken on before the first one." % rec.employee_id.name
                )
            twin = self.sudo().search(
                [
                    ("employee_id", "=", rec.employee_id.id),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "approved"),
                ],
                limit=1,
            )
            if twin:
                raise UserError(
                    "%s already has opening provision %s." % (rec.employee_id.name, twin.name)
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_on": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self):
        for rec in self:
            _payroll_only(self.env, "cancels an opening gratuity provision")
            if rec.state != "draft":
                raise UserError("Only a recorded (unapproved) opening provision is cancelled.")
            rec._guarded().write({"state": "cancelled"})
        return True

    @api.model
    def _opening_for(self, employee, company, month_start):
        """The approved opening provision the first accrual from `month_start`
        moves from (0.0 when none was taken on)."""
        row = self.sudo().search(
            [
                ("employee_id", "=", employee.id),
                ("company_id", "=", company.id),
                ("state", "=", "approved"),
                ("as_of", "<", month_start),
            ],
            order="as_of desc, id desc",
            limit=1,
        )
        return row.opening_liability if row else 0.0


# ----------------------------------------------------- salary advance release


class FixOffcycleAdvanceRecovery(models.Model):
    _inherit = "fix.payroll.offcycle"

    advance_recovery_ids = fields.One2many(
        "fix.payroll.recovery", "advance_id", string="Recovery Schedule", readonly=True
    )
    advance_outstanding = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_advance_outstanding",
        string="Still Owed on the Advance",
    )

    def _compute_advance_outstanding(self):
        for rec in self:
            live = rec.sudo().advance_recovery_ids.filtered(lambda r: r.state == "approved")
            rec.advance_outstanding = (
                round(sum(live.mapped("remaining_amount")), 2)
                if rec.payment_type == "advance"
                else 0.0
            )

    def action_pay(self):
        """FR-PAY-032: a salary advance leaves the bank only with its approved
        recovery schedule for the whole amount advanced."""
        for rec in self.filtered(lambda r: r.payment_type == "advance"):
            schedule = rec.sudo().advance_recovery_ids.filtered(lambda r: r.state == "approved")
            covered = round(sum(schedule.mapped("amount")), 2)
            if covered + 1e-6 < round(rec.amount, 2):
                raise UserError(
                    "Salary advance %s is released only with its approved recovery schedule "
                    "for the %.2f advanced (approved: %.2f)." % (rec.name, rec.amount, covered)
                )
        return super().action_pay()
