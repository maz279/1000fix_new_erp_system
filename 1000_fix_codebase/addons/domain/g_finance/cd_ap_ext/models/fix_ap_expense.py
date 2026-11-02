# cd_ap_ext — employee expense (CD-M52-01): claims on the M21-core employee
# master (MV-01) with per-diem / mileage lines from an effective-dated rate
# master, an expense policy enforced on SUBMISSION, segregation of duties on
# approval, GL posting, and employee advances & floats with settlement
# against claims and recovery of any unspent balance.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .ap_gl import ap_account, ap_journal, post_ap_move
from .fix_ap_ext import _q


class FixExpenseGrade(models.Model):
    """Employee grade for expense entitlements (policy limits, rates)."""

    _name = "fix.expense.grade"
    _description = "Expense Grade"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", help="Company-wide: leave empty")
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)


class HrEmployeeExpense(models.Model):
    _inherit = "hr.employee"

    expense_grade_id = fields.Many2one("fix.expense.grade", string="Expense Grade")


class FixExpenseCategory(models.Model):
    _name = "fix.expense.category"
    _description = "Expense Category"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", help="Company-wide: leave empty")
    name = fields.Char(required=True)
    code = fields.Char(required=True)
    line_type = fields.Selection(
        [("actual", "Actual cost (receipt)"), ("per_diem", "Per-diem"), ("mileage", "Mileage")],
        required=True,
        default="actual",
    )
    account_id = fields.Many2one(
        "account.account", string="Expense Account", help="Empty = the default expense role"
    )
    active = fields.Boolean(default=True)


class FixExpenseRate(models.Model):
    """Per-diem and mileage rate master (company policy, effective-dated)."""

    _name = "fix.expense.rate"
    _description = "Per-Diem & Mileage Rate"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "rate_type, grade_id, location, date_from desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", help="Company-wide: leave empty")
    rate_type = fields.Selection(
        [("per_diem", "Per-diem (per day)"), ("mileage", "Mileage (per km)")], required=True
    )
    grade_id = fields.Many2one("fix.expense.grade", help="Empty = every grade")
    location = fields.Char(
        help="Per-diem location class (e.g. Dhaka, divisional city, other); empty = anywhere"
    )
    vehicle = fields.Selection(
        [("motorcycle", "Motorcycle"), ("car", "Car"), ("other", "Other")],
        help="Mileage: vehicle class",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    rate = fields.Monetary(currency_field="currency_id", required=True)
    date_from = fields.Date(required=True, default=fields.Date.context_today)
    date_to = fields.Date()
    active = fields.Boolean(default=True)

    @api.constrains("rate", "date_from", "date_to")
    def _check_rate(self):
        for row in self:
            if row.rate <= 0:
                raise ValidationError("A rate is positive")
            if row.date_to and row.date_to < row.date_from:
                raise ValidationError("Valid To cannot be before Valid From")

    @api.model
    def find(self, rate_type, on_date, grade=None, location=None, vehicle=None, company=None):
        """Most specific effective row: grade and location/vehicle match beat blanks."""
        company = company or self.env.company
        rows = self.search(
            [
                ("company_id", "=", company.id),
                ("rate_type", "=", rate_type),
                ("date_from", "<=", on_date),
                "|",
                ("date_to", "=", False),
                ("date_to", ">=", on_date),
            ]
        )
        best, best_score = None, -1
        for row in rows:
            if row.grade_id and row.grade_id != grade:
                continue
            if (
                rate_type == "per_diem"
                and row.location
                and (row.location or "").lower() != (location or "").lower()
            ):
                continue
            if rate_type == "mileage" and row.vehicle and row.vehicle != vehicle:
                continue
            score = (2 if row.grade_id else 0) + (1 if (row.location or row.vehicle) else 0)
            if score > best_score:
                best, best_score = row, score
        if not best:
            raise UserError(
                "No %s rate effective on %s for this grade/location — maintain the "
                "Per-Diem & Mileage rate master" % (rate_type.replace("_", "-"), on_date)
            )
        return best


class FixExpensePolicy(models.Model):
    """Expense policy: limits per category and grade, enforced on submit."""

    _name = "fix.expense.policy"
    _description = "Expense Policy Limit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "category_id, grade_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", help="Company-wide: leave empty")
    category_id = fields.Many2one("fix.expense.category", required=True, ondelete="cascade")
    grade_id = fields.Many2one("fix.expense.grade", help="Empty = every grade")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    limit_per_line = fields.Monetary(
        string="Limit per Expense", currency_field="currency_id", help="0 = no limit"
    )
    limit_per_day = fields.Monetary(
        string="Limit per Day", currency_field="currency_id", help="0 = no limit"
    )
    receipt_required_above = fields.Monetary(
        currency_field="currency_id", help="A receipt (attachment) is required above this amount"
    )
    blocked = fields.Boolean(string="Not Reimbursable", help="The category is not claimable")
    active = fields.Boolean(default=True)

    @api.model
    def for_line(self, category, grade, company):
        rows = self.search([("company_id", "=", company.id), ("category_id", "=", category.id)])
        exact = rows.filtered(lambda r: r.grade_id == grade)[:1]
        return exact or rows.filtered(lambda r: not r.grade_id)[:1]


class FixExpenseClaim(models.Model):
    """T02: employee expense on the M21-core employee master (MV-01)."""

    _name = "fix.expense.claim"
    _description = "Expense Claim"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "expense_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    description = fields.Char(required=True)
    line_ids = fields.One2many("fix.expense.claim.line", "claim_id", string="Expense Lines")
    amount = fields.Monetary(
        string="Claimed Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
        readonly=False,
    )
    expense_date = fields.Date(default=fields.Date.today, required=True)
    advance_id = fields.Many2one(
        "fix.employee.advance", string="Settles Advance", domain=[("state", "=", "disbursed")]
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("paid", "Paid"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    policy_notes = fields.Text(readonly=True)
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)
    # above this a finance manager (account.group_account_manager) approves
    APPROVAL_THRESHOLD = 25000

    @api.depends("line_ids.amount")
    def _compute_amount(self):
        for claim in self:
            if claim.line_ids:
                claim.amount = _q(sum(claim.line_ids.mapped("amount")))
            else:
                claim.amount = claim.amount or 0.0  # no lines: the typed amount stands

    @api.model_create_multi
    def create(self, vals_list):
        # A claim created together with its lines in ONE request (the
        # workspace form's path) can have its stored amount computed before
        # the one2many lands; re-derive from the now-attached lines.
        claims = super().create(vals_list)
        claims.filtered(lambda c: c.line_ids)._compute_amount()
        return claims

    def write(self, vals):
        # employees keep self-service write on their drafts; approval fields
        # are set by the accounting workflow only (A08 rule 5)
        sensitive = {"approved_by", "move_id"} & set(vals) or vals.get("state") in (
            "approved",
            "paid",
        )
        if (
            sensitive
            and not self.env.su
            and not self.env.user.has_group("account.group_account_user")
        ):
            raise UserError("Only accounting approves or pays expense claims")
        return super().write(vals)

    def _policy_breaches(self):
        """Every policy breach of the claim (empty = compliant)."""
        self.ensure_one()
        breaches = []
        grade = self.employee_id.expense_grade_id
        Policy = self.env["fix.expense.policy"]
        per_day = {}
        for line in self.line_ids:
            policy = Policy.for_line(line.category_id, grade, self.company_id)
            if not policy:
                continue
            label = "%s (%s)" % (line.category_id.name, line.date)
            if policy.blocked:
                breaches.append("%s: category not reimbursable" % label)
            if policy.limit_per_line and line.amount > policy.limit_per_line + 0.005:
                breaches.append(
                    "%s: BDT %.2f above the per-expense limit %.2f"
                    % (label, line.amount, policy.limit_per_line)
                )
            if (
                policy.receipt_required_above
                and line.amount > policy.receipt_required_above
                and not line.receipt_attachment_ids
            ):
                breaches.append(
                    "%s: receipt required above BDT %.2f" % (label, policy.receipt_required_above)
                )
            key = (line.category_id, line.date)
            daily = line.amount / line.quantity if line.line_type == "per_diem" else line.amount
            per_day[key] = per_day.get(key, 0.0) + daily
            if policy.limit_per_day and per_day[key] > policy.limit_per_day + 0.005:
                breaches.append(
                    "%s: BDT %.2f per day above the daily limit %.2f"
                    % (label, per_day[key], policy.limit_per_day)
                )
        return list(dict.fromkeys(breaches))

    def action_submit(self) -> None:
        """Submit: a positive amount and the expense policy enforced (a
        breach BLOCKS, with every breach listed)."""
        for claim in self:
            if claim.state not in ("draft", "rejected"):
                raise UserError("Claim is already %s" % claim.state)
            # A claim created together with its lines in one request (the
            # workspace form saves header + lines together) can still carry
            # the pre-lines compute result; lines are the single source of
            # the claimed amount.
            if claim.line_ids:
                claim.amount = _q(sum(claim.line_ids.mapped("amount")))
            if (claim.amount or 0.0) <= 0:
                raise UserError("A claim must carry a positive amount")
            breaches = claim._policy_breaches()
            if breaches:
                claim.policy_notes = "\n".join(breaches)
                raise UserError("Expense policy breached:\n%s" % "\n".join(breaches))
            claim.write(
                {"state": "submitted", "submitted_by": self.env.user.id, "policy_notes": False}
            )

    def action_approve(self) -> None:
        """Approve a SUBMITTED claim. SoD: neither the submitter nor the
        claimant approves; above the threshold an accounting manager does.
        Posts Dr expense / Cr employee payable; payment is requested unless
        the claim settles an advance (the advance settlement pays the rest)."""
        user = self.env.user
        for claim in self:
            # an approved/paid/rejected claim must not raise a second
            # payment.requested (re-approval re-requested payment)
            if claim.state != "submitted":
                raise UserError("Only submitted claims can be approved (%s)" % claim.state)
            if claim.amount <= 0:
                raise UserError("A claim must carry a positive amount")
            if user == claim.submitted_by or user == claim.employee_id.user_id:
                raise UserError("Segregation of duties: a claim is approved by someone else")
            if claim.amount > self.APPROVAL_THRESHOLD and not user.has_group(
                "account.group_account_manager"
            ):
                raise UserError(
                    "Claims above BDT %d are approved by an accounting manager"
                    % self.APPROVAL_THRESHOLD
                )
            claim._post()
            claim.write({"state": "approved", "approved_by": user.id})
            if not claim.advance_id:
                # Payment rides the same event path as vendor invoices (M50 executes)
                publish(
                    self.env,
                    "payment.requested",
                    "fix.expense.claim",
                    claim.id,
                    {
                        "employee_id": claim.employee_id.id,
                        "amount": claim.amount,
                        "currency": claim.currency_id.name,
                        "invoice_ref": "EXP/%s" % claim.id,
                        "operating_unit_id": claim.operating_unit_id.id,
                    },
                )

    def action_reject(self):
        for claim in self:
            if claim.state != "submitted":
                raise UserError("Only a submitted claim can be rejected")
            claim.state = "rejected"

    def _post(self):
        self.ensure_one()
        env, company = self.env, self.company_id
        partner = self.employee_id.work_contact_id or self.employee_id.user_id.partner_id
        label = "Expense claim EXP/%s %s" % (self.id, self.employee_id.name)
        default_expense = None
        lines = []
        if self.line_ids:
            for line in self.line_ids:
                account = line.category_id.account_id
                if not account:
                    default_expense = default_expense or ap_account(env, company, "expense")
                    account = default_expense
                lines.append(
                    (
                        account,
                        "%s %s" % (label, line.category_id.name),
                        _q(line.amount),
                        0.0,
                        partner,
                    )
                )
        else:
            lines.append(
                (ap_account(env, company, "expense"), label, _q(self.amount), 0.0, partner)
            )
        lines.append(
            (ap_account(env, company, "employee_payable"), label, 0.0, _q(self.amount), partner)
        )
        move = post_ap_move(
            env,
            company,
            ap_journal(env, company, "purchase"),
            self.expense_date,
            label,
            lines,
            self.operating_unit_id,
        )
        self.move_id = move.id


class FixExpenseClaimLine(models.Model):
    _name = "fix.expense.claim.line"
    _description = "Expense Claim Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date, id"

    claim_id = fields.Many2one("fix.expense.claim", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="claim_id.company_id", store=True)
    currency_id = fields.Many2one(related="claim_id.currency_id")
    category_id = fields.Many2one("fix.expense.category", required=True)
    line_type = fields.Selection(related="category_id.line_type", store=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    description = fields.Char()
    location = fields.Char(help="Per-diem location class")
    vehicle = fields.Selection([("motorcycle", "Motorcycle"), ("car", "Car"), ("other", "Other")])
    quantity = fields.Float(
        default=1.0, help="Days (per-diem) or kilometres (mileage); 1 for actual cost"
    )
    rate_id = fields.Many2one("fix.expense.rate", string="Rate Row", readonly=True)
    unit_amount = fields.Monetary(
        currency_field="currency_id", help="Actual cost, or the rate master's rate"
    )
    amount = fields.Monetary(currency_field="currency_id", compute="_compute_amount", store=True)
    receipt_attachment_ids = fields.Many2many("ir.attachment", string="Receipts")

    @api.depends("quantity", "unit_amount")
    def _compute_amount(self):
        for line in self:
            line.amount = _q(line.quantity * line.unit_amount)

    def _apply_rate(self):
        for line in self:
            if line.line_type not in ("per_diem", "mileage"):
                continue
            rate = self.env["fix.expense.rate"].find(
                line.line_type,
                line.date,
                grade=line.claim_id.employee_id.expense_grade_id,
                location=line.location,
                vehicle=line.vehicle,
                company=line.claim_id.company_id,
            )
            super(FixExpenseClaimLine, line).write({"rate_id": rate.id, "unit_amount": rate.rate})

    @api.constrains("quantity")
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError("Quantity (days / km) must be positive")

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._check_claim_editable()
        lines._apply_rate()
        return lines

    def write(self, vals):
        self._check_claim_editable()
        res = super().write(vals)
        if {"date", "location", "vehicle", "category_id"} & set(vals):
            self._apply_rate()
        elif "unit_amount" in vals and self.filtered(
            lambda line: line.line_type in ("per_diem", "mileage")
        ):
            self._apply_rate()  # per-diem / mileage come from the master only
        return res

    def _check_claim_editable(self):
        if self.claim_id.filtered(lambda c: c.state not in ("draft", "rejected")):
            raise UserError("Lines of a submitted claim cannot change")


class FixEmployeeAdvance(models.Model):
    """Employee advance / float: approved, disbursed through treasury,
    settled against approved expense claims, any unspent balance recovered."""

    _name = "fix.employee.advance"
    _description = "Employee Advance / Float"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "request_date desc, id desc"

    name = fields.Char(readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    advance_type = fields.Selection(
        [("advance", "Advance (one purpose)"), ("float", "Float (revolving)")],
        required=True,
        default="advance",
    )
    purpose = fields.Char(required=True)
    request_date = fields.Date(required=True, default=fields.Date.context_today)
    settle_by = fields.Date(string="Settle By")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True, tracking=True)
    claim_ids = fields.One2many("fix.expense.claim", "advance_id", string="Claims Settled")
    settled_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_balance", store=True
    )
    recovered_amount = fields.Monetary(currency_field="currency_id", readonly=True, default=0.0)
    balance = fields.Monetary(
        string="Open Balance", currency_field="currency_id", compute="_compute_balance", store=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("disbursed", "Disbursed"),
            ("settled", "Settled"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    requested_by = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True, copy=False
    )
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    execution_id = fields.Many2one("fix.payment.execution", readonly=True, copy=False)
    disbursement_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    settlement_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    recovery_method = fields.Selection(
        [("cash", "Cash / bank refund"), ("payroll", "Payroll deduction (A09)")],
        help="How an unspent balance is recovered",
    )

    @api.depends("amount", "recovered_amount", "claim_ids.state", "claim_ids.amount", "state")
    def _compute_balance(self):
        for adv in self:
            settled = sum(
                adv.claim_ids.filtered(lambda c: c.state in ("approved", "paid")).mapped("amount")
            )
            adv.settled_amount = min(settled, adv.amount)
            adv.balance = _q(adv.amount - adv.settled_amount - adv.recovered_amount)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.employee.advance") or "ADV"
        return super().create(vals_list)

    @api.constrains("amount")
    def _check_amount(self):
        for adv in self:
            if adv.amount <= 0:
                raise ValidationError("An advance is a positive amount")

    def _employee_bank(self):
        """The employee's primary bank account (HR-restricted field, read as
        superuser only to address the disbursement)."""
        employee = self.employee_id.sudo()
        bank = self.env["res.partner.bank"]
        if "primary_bank_account_id" in employee._fields:
            bank = employee.primary_bank_account_id
        if not bank and "bank_account_ids" in employee._fields:
            bank = employee.bank_account_ids[:1]
        return bank

    def _partner(self):
        return self.employee_id.work_contact_id or self.employee_id.user_id.partner_id

    def action_approve(self):
        """Approve (SoD: not the requester, not the employee) and hand the
        disbursement to treasury as a payment execution."""
        user = self.env.user
        for adv in self:
            if adv.state != "draft":
                raise UserError("Advance %s is %s" % (adv.name, adv.state))
            if user in (adv.requested_by, adv.employee_id.user_id):
                raise UserError("Segregation of duties: an advance is approved by someone else")
            open_advances = self.search(
                [
                    ("employee_id", "=", adv.employee_id.id),
                    ("state", "=", "disbursed"),
                    ("advance_type", "=", "advance"),
                    ("id", "!=", adv.id),
                ]
            )
            if adv.advance_type == "advance" and open_advances:
                raise UserError(
                    "%s still holds unsettled advance %s — settle it first"
                    % (adv.employee_id.name, open_advances[0].name)
                )
            if "fix.payment.execution" not in self.env:
                raise UserError("Treasury (cd_cash_position) is not installed")
            Execution = self.env["fix.payment.execution"]
            journal = ap_journal(self.env, adv.company_id, "payment")
            vals = {
                "company_id": adv.company_id.id,
                "operating_unit_id": adv.operating_unit_id.id,
                "source_model": adv._name,
                "source_id": adv.id,
                "payee": "employee:%s %s" % (adv.employee_id.id, adv.employee_id.name),
                "currency_id": adv.currency_id.id,
                "amount": adv.amount,
                "method": "bank_transfer",
            }
            optional = {
                "partner_id": adv._partner().id,
                "partner_bank_id": adv._employee_bank().id or False,
                "journal_id": journal.id,
                "rail": "beftn",  # treasury may change the rail before release
                # the advance books its own disbursement entry: treasury posts nothing
                "source_posts_gl": True,
            }
            vals.update({k: v for k, v in optional.items() if k in Execution._fields})
            execution = Execution.create(vals)
            adv.write({"state": "approved", "approved_by": user.id, "execution_id": execution.id})
        return True

    def action_confirm_disbursement(self):
        """Once treasury executed the payment: Dr employee advance / Cr bank."""
        for adv in self:
            if adv.state != "approved":
                raise UserError("Advance %s is not awaiting disbursement" % adv.name)
            execution = adv.execution_id
            asserted = (
                "confirmation_source" in execution._fields
                and execution.confirmation_source == "caller_asserted"
            )
            if execution.state != "executed" or asserted:
                raise UserError(
                    "Treasury has no bank confirmation of the disbursement of %s yet (%s)"
                    % (adv.name, adv.execution_id.state or "no execution")
                )
            env, company = self.env, adv.company_id
            journal = (
                execution.journal_id
                if "journal_id" in execution._fields and execution.journal_id
                else ap_journal(env, company, "payment")
            )
            label = "Advance %s %s" % (adv.name, adv.employee_id.name)
            move = post_ap_move(
                env,
                company,
                journal,
                fields.Date.context_today(self),
                label,
                [
                    (
                        ap_account(env, company, "employee_advance"),
                        label,
                        adv.amount,
                        0.0,
                        adv._partner(),
                    ),
                    (journal.default_account_id, label, 0.0, adv.amount, adv._partner()),
                ],
                adv.operating_unit_id,
            )
            adv.write({"state": "disbursed", "disbursement_move_id": move.id})
        return True

    def action_settle(self):
        """Settle against the approved claims linked to the advance:
        Dr employee payable / Cr employee advance for the settled part. A
        claim total above the advance is paid to the employee (payment
        request); an unspent balance must be recovered before closing."""
        for adv in self:
            if adv.state != "disbursed":
                raise UserError("Only a disbursed advance is settled")
            claims = adv.claim_ids.filtered(lambda c: c.state in ("approved", "paid"))
            if not claims:
                raise UserError("No approved claims are linked to %s" % adv.name)
            env, company = self.env, adv.company_id
            settled = adv.settled_amount
            label = "Advance settlement %s" % adv.name
            move = post_ap_move(
                env,
                company,
                ap_journal(env, company, "purchase"),
                fields.Date.context_today(self),
                label,
                [
                    (
                        ap_account(env, company, "employee_payable"),
                        label,
                        settled,
                        0.0,
                        adv._partner(),
                    ),
                    (
                        ap_account(env, company, "employee_advance"),
                        label,
                        0.0,
                        settled,
                        adv._partner(),
                    ),
                ],
                adv.operating_unit_id,
            )
            excess = _q(sum(claims.mapped("amount")) - adv.amount)
            if excess > 0:
                publish(
                    env,
                    "payment.requested",
                    "fix.employee.advance",
                    adv.id,
                    {
                        "employee_id": adv.employee_id.id,
                        "amount": excess,
                        "currency": adv.currency_id.name,
                        "invoice_ref": "%s/EXCESS" % adv.name,
                        "operating_unit_id": adv.operating_unit_id.id,
                    },
                )
            adv.settlement_move_id = move.id
            if adv.balance <= 0.005:
                adv.state = "settled"
        return True

    def action_record_recovery(self):
        """Recover the unspent balance: cash/bank refund posts Dr bank / Cr
        advance; payroll deduction is requested from payroll (A09) as an
        event and closes the advance on its confirmation."""
        for adv in self:
            if adv.state != "disbursed" or adv.balance <= 0.005:
                raise UserError("%s has no open balance to recover" % adv.name)
            if not adv.recovery_method:
                raise UserError("Choose the recovery method first")
            env, company = self.env, adv.company_id
            amount = adv.balance
            if adv.recovery_method == "cash":
                journal = ap_journal(env, company, "payment")
                label = "Advance refund %s" % adv.name
                post_ap_move(
                    env,
                    company,
                    journal,
                    fields.Date.context_today(self),
                    label,
                    [
                        (journal.default_account_id, label, amount, 0.0, adv._partner()),
                        (
                            ap_account(env, company, "employee_advance"),
                            label,
                            0.0,
                            amount,
                            adv._partner(),
                        ),
                    ],
                    adv.operating_unit_id,
                )
                adv.write({"recovered_amount": adv.recovered_amount + amount, "state": "settled"})
            else:
                publish(
                    env,
                    "advance.recovery_requested",
                    "fix.employee.advance",
                    adv.id,
                    {
                        "employee_id": adv.employee_id.id,
                        "amount": amount,
                        "currency": adv.currency_id.name,
                    },
                )
                adv.message_post(
                    body="Payroll deduction of BDT %.2f requested from payroll (A09); the "
                    "advance closes when payroll confirms the deduction." % amount
                )
        return True
