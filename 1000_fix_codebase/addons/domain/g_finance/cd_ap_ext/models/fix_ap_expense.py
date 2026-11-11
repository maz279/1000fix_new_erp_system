# cd_ap_ext — employee expense (CD-M52-01): claims on the M21-core employee
# master (MV-01) with per-diem / mileage lines from an effective-dated rate
# master, an expense policy enforced on SUBMISSION, segregation of duties on
# approval, GL posting, and employee advances & floats with settlement
# against claims and recovery of any unspent balance.
from datetime import timedelta

from odoo import api, fields, models
from odoo.addons.cd_cash_position.models.treasury_common import treasury_account
from odoo.addons.cd_fixed_asset_ext.models.fix_asset_common import (
    attach_upload,
    attachment_names,
)
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .ap_gl import ap_account, ap_journal, post_ap_move
from .fix_ap_controls import (
    DEFAULT_CLAIM_MANAGER_THRESHOLD,
    DEFAULT_CLAIM_SPLIT_DAYS,
    GROUP_MANAGER,
    PARAM_CLAIM_MANAGER_STEP,
    PARAM_CLAIM_MANAGER_THRESHOLD,
    PARAM_CLAIM_REQUIRE_COST_CENTRE,
    PARAM_CLAIM_SPLIT_DAYS,
    bool_param,
    float_param,
    is_finance,
    require_finance,
)
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
    """T02: employee expense on the M21-core employee master (MV-01).

    A08 audit (2026-11-04), M52-7: plain users keep creating and submitting
    their OWN claims, but the workflow fields are guarded (the owner wrote
    state='submitted' to skip the policy), the claimed amount comes from the
    lines only (a lineless 24,999 claim skipped every policy check), a
    receipt is claimed once (BRU-APE-15), an employee's claims inside a
    rolling window are summed for the manager threshold (split claims), a
    line manager approves before finance (spec §8.2), and the maker never
    checks: claimant, submitter, creator and line manager are excluded from
    finance approval."""

    _name = "fix.expense.claim"
    _description = "Expense Claim"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
        help="The sum of the expense lines. A claim has no amount of its own.",
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
    submitted_at = fields.Datetime(readonly=True, copy=False)
    manager_approved_by = fields.Many2one(
        "res.users", string="Line Manager Approval", readonly=True, copy=False
    )
    manager_approved_at = fields.Datetime(readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    policy_notes = fields.Text(readonly=True)
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)
    # A08 M52-9: read back from treasury's events
    payment_move_id = fields.Many2one(
        "account.move",
        string="Payable Cleared By",
        readonly=True,
        copy=False,
        help="Dr employee payable / Cr outgoing clearing, when treasury confirmed the payment.",
    )
    payment_failure = fields.Char(string="Last Bank Rejection", readonly=True, copy=False)
    # Kept for old callers: the default of the configurable threshold.
    APPROVAL_THRESHOLD = 25000

    CLAIM_GUARDED = {
        "state",
        "submitted_by",
        "submitted_at",
        "manager_approved_by",
        "manager_approved_at",
        "approved_by",
        "policy_notes",
        "move_id",
        "amount",
        "payment_move_id",
        "payment_failure",
    }
    CLAIM_TERMS = {
        "employee_id",
        "description",
        "expense_date",
        "advance_id",
        "operating_unit_id",
        "currency_id",
        "company_id",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.CLAIM_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(c.state not in ("draft", "rejected") for c in self):
            locked |= self.CLAIM_TERMS | {"line_ids"}
        return locked

    @api.depends("line_ids.amount")
    def _compute_amount(self):
        for claim in self:
            claim.amount = _q(sum(claim.line_ids.mapped("amount")))

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and not is_finance(self.env):
            employees = (
                self.env["hr.employee"]
                .sudo()
                .browse([v["employee_id"] for v in vals_list if v.get("employee_id")])
            )
            others = employees.filtered(lambda e: e.user_id != self.env.user)
            if others:
                raise UserError(
                    "You file expense claims for yourself only (%s is another employee)."
                    % others[0].name
                )
        claims = super().create(vals_list)
        claims.filtered(lambda c: c.line_ids)._guarded()._compute_amount()
        return claims

    def write(self, vals):
        if self.CLAIM_TERMS & set(vals) and not self._fix_guard_open():
            fixed = self.filtered(lambda c: c.state not in ("draft", "rejected"))
            changed = [
                n
                for n in self.CLAIM_TERMS & set(vals)
                if any(c._fix_guard_differs(n, vals[n], c[n]) for c in fixed)
            ]
            if changed:
                raise UserError(
                    "Claim EXP/%s is %s: %s can no longer change."
                    % (fixed[0].id, fixed[0].state, ", ".join(sorted(changed)))
                )
        if "employee_id" in vals and not self.env.su and not is_finance(self.env):
            employee = self.env["hr.employee"].sudo().browse(vals["employee_id"])
            if employee.user_id != self.env.user:
                raise UserError("You file expense claims for yourself only.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and self.filtered(lambda c: c.state not in ("draft", "rejected")):
            raise UserError("Only a draft or rejected expense claim is deleted.")
        return super().unlink()

    # ------------------------------------------------------------ policy --
    def _policy_breaches(self):
        """Every policy breach of the claim (empty = compliant)."""
        self.ensure_one()
        breaches = []
        if not self.line_ids:
            breaches.append("a claim needs at least one expense line (category, date, receipt)")
        grade = self.employee_id.sudo().expense_grade_id
        Policy = self.env["fix.expense.policy"].sudo()
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
                and not line.sudo().receipt_attachment_ids
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
        breaches += self._duplicate_receipts()
        return list(dict.fromkeys(breaches))

    def _attribution_breaches(self):
        """BRU-APE-16: every line is attributed to a cost centre. Checked when
        the claimant submits, not at approval: a claim already submitted cannot
        change its lines."""
        self.ensure_one()
        if not bool_param(self.env, PARAM_CLAIM_REQUIRE_COST_CENTRE, True):
            return []
        return [
            "%s (%s): name the cost centre this expense belongs to"
            % (line.category_id.name, line.date)
            for line in self.line_ids
            if not (line.cost_centre or "").strip()
        ]

    def _receipt_checksums(self):
        self.ensure_one()
        return {
            att.checksum: line
            for line in self.line_ids
            for att in line.sudo().receipt_attachment_ids
            if att.checksum
        }

    def _duplicate_receipts(self):
        """BRU-APE-15: the same receipt (content hash) is claimed once, on any
        live claim of the company."""
        self.ensure_one()
        found = []
        seen = {}
        for line in self.line_ids:
            for att in line.sudo().receipt_attachment_ids:
                if not att.checksum:
                    continue
                if att.checksum in seen and seen[att.checksum] != line.id:
                    found.append("%s: the same receipt is attached twice" % att.name)
                seen[att.checksum] = line.id
        if not seen:
            return found
        Line = self.env["fix.expense.claim.line"].sudo()
        others = Line.search(
            [
                ("claim_id", "!=", self.id),
                ("claim_id.company_id", "=", self.company_id.id),
                ("claim_id.state", "not in", ("draft", "rejected")),
                ("receipt_attachment_ids.checksum", "in", list(seen)),
            ]
        )
        for other in others:
            claim = other.claim_id
            found.append(
                "receipt already claimed on EXP/%s (%s, %s) — a receipt is reimbursed once"
                % (claim.id, claim.employee_id.name, claim.state)
            )
        return found

    def _window_total(self):
        """This claim plus the employee's other live claims dated inside the
        rolling split-detection window (A08 M52-7: two 20,000 claims the same
        day passed one accountant under the 25,000 threshold)."""
        self.ensure_one()
        days = int(float_param(self.env, PARAM_CLAIM_SPLIT_DAYS, DEFAULT_CLAIM_SPLIT_DAYS))
        total = self.amount
        if days <= 0:
            return total
        others = self.sudo().search(
            [
                ("id", "!=", self.id),
                ("employee_id", "=", self.employee_id.id),
                ("company_id", "=", self.company_id.id),
                ("state", "in", ("submitted", "approved", "paid")),
                ("expense_date", ">", self.expense_date - timedelta(days=days)),
                ("expense_date", "<", self.expense_date + timedelta(days=days)),
            ]
        )
        return _q(total + sum(others.mapped("amount")))

    # ------------------------------------------------------------ people --
    def _claimant_user(self):
        return self.employee_id.sudo().user_id

    def _line_manager_user(self):
        employee = self.employee_id.sudo()
        manager = employee.parent_id
        user = manager.user_id if manager else self.env["res.users"]
        if user and user == employee.user_id:
            return self.env["res.users"]
        return user

    def _manager_step_needed(self):
        self.ensure_one()
        return bool(
            bool_param(self.env, PARAM_CLAIM_MANAGER_STEP, True) and self._line_manager_user()
        )

    def _makers(self):
        self.ensure_one()
        claim = self.sudo()
        return claim.create_uid | claim.submitted_by | claim._claimant_user()

    # ------------------------------------------------------------ actions --
    def action_submit(self) -> None:
        """Submit: at least one line, a positive amount, and the expense policy
        enforced (a breach BLOCKS, with every breach listed). The claimant
        submits their own claim; accounting submits for an employee without a
        login."""
        for claim in self:
            if claim.state not in ("draft", "rejected"):
                raise UserError("Claim is already %s" % claim.state)
            if (
                not self.env.su
                and not is_finance(self.env)
                and claim._claimant_user() != self.env.user
            ):
                raise UserError("You submit your own expense claims only.")
            claim._guarded()._compute_amount()
            breaches = claim._policy_breaches() + claim._attribution_breaches()
            if breaches:
                claim._guarded().write({"policy_notes": "\n".join(breaches)})
                raise UserError("Expense policy breached:\n%s" % "\n".join(breaches))
            if (claim.amount or 0.0) <= 0:
                raise UserError("A claim must carry a positive amount")
            claim._guarded().write(
                {
                    "state": "submitted",
                    "submitted_by": self.env.user.id,
                    "submitted_at": fields.Datetime.now(),
                    "policy_notes": False,
                    "manager_approved_by": False,
                    "manager_approved_at": False,
                }
            )

    def action_manager_approve(self):
        """The line manager approves before finance (spec M52 §8.2)."""
        for claim in self:
            if claim.state != "submitted":
                raise UserError("Only a submitted claim is approved by the line manager.")
            manager = claim._line_manager_user()
            if not manager:
                raise UserError("%s has no line manager with a login." % claim.employee_id.name)
            if not self.env.su and self.env.user != manager:
                raise UserError(
                    "Claim EXP/%s is approved by %s's line manager (%s)."
                    % (claim.id, claim.employee_id.name, manager.name)
                )
            if self.env.user in claim._makers():
                raise UserError("Segregation of duties: a claim is approved by someone else")
            if claim.manager_approved_by:
                raise UserError("Claim EXP/%s is already manager-approved." % claim.id)
            claim.sudo()._guarded().write(
                {"manager_approved_by": self.env.uid, "manager_approved_at": fields.Datetime.now()}
            )
        return True

    def action_approve(self) -> None:
        """Finance verification of a SUBMITTED claim. SoD: neither the claimant,
        the submitter, the creator nor the line manager who approved it;
        above the threshold (this claim plus the employee's claims in the
        split window) an accounting manager. The policy is checked again.
        Posts Dr expense / Cr employee payable; payment is requested unless
        the claim settles an advance (the advance settlement pays the rest)."""
        require_finance(self.env, "Approving an expense claim")
        user = self.env.user
        threshold = float_param(
            self.env, PARAM_CLAIM_MANAGER_THRESHOLD, DEFAULT_CLAIM_MANAGER_THRESHOLD
        )
        for claim in self:
            # an approved/paid/rejected claim must not raise a second
            # payment.requested (re-approval re-requested payment)
            if claim.state != "submitted":
                raise UserError("Only submitted claims can be approved (%s)" % claim.state)
            if not claim.line_ids or claim.amount <= 0:
                raise UserError("A claim must carry a positive amount on its expense lines")
            if user in (claim._makers() | claim.manager_approved_by):
                raise UserError("Segregation of duties: a claim is approved by someone else")
            if claim._manager_step_needed() and not claim.manager_approved_by:
                raise UserError(
                    "Claim EXP/%s awaits its line manager's approval (%s) before finance."
                    % (claim.id, claim._line_manager_user().name)
                )
            breaches = claim._policy_breaches()
            if breaches:
                raise UserError("Expense policy breached:\n%s" % "\n".join(breaches))
            window = claim._window_total()
            if window > threshold and not (self.env.su or user.has_group(GROUP_MANAGER)):
                raise UserError(
                    "Claims above BDT %.0f are approved by an accounting manager (EXP/%s with "
                    "%s's other claims in the last %d days: BDT %.2f)"
                    % (
                        threshold,
                        claim.id,
                        claim.employee_id.name,
                        int(
                            float_param(self.env, PARAM_CLAIM_SPLIT_DAYS, DEFAULT_CLAIM_SPLIT_DAYS)
                        ),
                        window,
                    )
                )
            claim._post()
            claim._guarded().write({"state": "approved", "approved_by": user.id})
            if not claim.advance_id:
                employee = claim.employee_id.sudo()
                partner = employee.work_contact_id or employee.user_id.partner_id
                bank = claim.env["fix.employee.advance"]._bank_of(employee)
                # Payment rides the same event path as vendor invoices: M50's
                # registered consumer turns it into a pinned execution.
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
                        "company_id": claim.company_id.id,
                        "payee_partner_id": partner.id or False,
                        "partner_bank_id": bank.id or False,
                        "approved_by": user.id,
                    },
                )

    def action_reject(self):
        for claim in self:
            if claim.state != "submitted":
                raise UserError("Only a submitted claim can be rejected")
            deciders_ok = (
                self.env.su or is_finance(self.env) or (self.env.user == claim._line_manager_user())
            )
            if not deciders_ok:
                raise UserError("A claim is rejected by accounting or the line manager.")
            if self.env.user in claim._makers():
                raise UserError("Segregation of duties: a claim is decided by someone else")
            claim.sudo()._guarded().write({"state": "rejected"})

    def _post(self):
        self.ensure_one()
        env, company = self.env, self.company_id
        employee = self.employee_id.sudo()
        partner = employee.work_contact_id or employee.user_id.partner_id
        label = "Expense claim EXP/%s %s" % (self.id, employee.name)
        default_expense = None
        lines = []
        dimensions = {}
        for line in self.line_ids:
            dimensions[len(lines)] = {"cost_centre": (line.cost_centre or "").strip()}
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
            line_dimensions=dimensions,
        )
        self._guarded().write({"move_id": move.id})


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
    cost_centre = fields.Char(
        string="Cost Centre",
        help="BRU-APE-16: where this expense belongs. Carried to the GL dimension of the line.",
    )
    receipt_attachment_ids = fields.Many2many("ir.attachment", string="Receipts")
    # A08 M52-7: a receipt uploaded on the line's form becomes an attachment
    receipt_file = fields.Binary(
        string="Upload Receipt",
        compute="_compute_receipt_file",
        inverse="_inverse_receipt_file",
        attachment=False,
    )
    receipt_filename = fields.Char(string="Receipt File Name", copy=False)
    receipt_names = fields.Char(string="Receipts Attached", compute="_compute_receipt_names")

    def _compute_receipt_file(self):
        for line in self:
            line.receipt_file = False

    def _inverse_receipt_file(self):
        for line in self:
            attach_upload(
                line,
                "receipt_attachment_ids",
                line.receipt_file,
                line.receipt_filename,
                "Receipt EXP/%s %s" % (line.claim_id.id, line.date),
            )

    @api.depends("receipt_attachment_ids")
    def _compute_receipt_names(self):
        for line in self:
            line.receipt_names = attachment_names(line.receipt_attachment_ids)

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
                grade=line.claim_id.employee_id.sudo().expense_grade_id,
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
        if "claim_id" in vals:
            # the claim a line arrives in, not only the one it left: a line was
            # moved into an approved claim and raised its settled amount
            self._check_claim_editable()
        if {"date", "location", "vehicle", "category_id"} & set(vals):
            self._apply_rate()
        elif "unit_amount" in vals and self.filtered(
            lambda line: line.line_type in ("per_diem", "mileage")
        ):
            self._apply_rate()  # per-diem / mileage come from the master only
        return res

    def unlink(self):
        self._check_claim_editable()
        return super().unlink()

    def _check_claim_editable(self):
        if self.env.su:
            return
        if self.claim_id.filtered(lambda c: c.state not in ("draft", "rejected")):
            raise UserError("Lines of a submitted claim cannot change")


class FixEmployeeAdvance(models.Model):
    """Employee advance / float: approved, disbursed through treasury,
    settled against approved expense claims, any unspent balance recovered.

    A08 audit (2026-11-04), M52-8: requested_by was rewritten to self-approve
    40,000; state='disbursed' was written with nothing paid; the amount was
    raised after approval (disbursement JE 50,000, bank 5,000); Settle posted
    twice; a second advance was approved while the first was unpaid. The
    workflow fields are guarded, the amount is pinned to the approval and to
    treasury's execution, settlement posts only what is new, and an approved
    or disbursed advance blocks a further one (BRU-APE-17)."""

    _name = "fix.employee.advance"
    _description = "Employee Advance / Float"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    approved_amount = fields.Monetary(
        currency_field="currency_id", readonly=True, copy=False, help="The amount approved."
    )
    claim_ids = fields.One2many("fix.expense.claim", "advance_id", string="Claims Settled")
    settled_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_balance", store=True
    )
    settled_posted = fields.Monetary(
        string="Settlement Posted",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        default=0.0,
        help="What the settlement entries have already moved from the advance.",
    )
    excess_requested = fields.Monetary(
        currency_field="currency_id", readonly=True, copy=False, default=0.0
    )
    recovered_amount = fields.Monetary(currency_field="currency_id", readonly=True, default=0.0)
    recovery_state = fields.Selection(
        [("none", "None"), ("requested", "Payroll Deduction Requested"), ("done", "Recovered")],
        default="none",
        readonly=True,
        copy=False,
    )
    recovery_requested_amount = fields.Monetary(
        currency_field="currency_id", readonly=True, copy=False
    )
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
    disbursement_reversal_move_id = fields.Many2one(
        "account.move",
        readonly=True,
        copy=False,
        help="Posted when the bank returned the disbursement after clearing.",
    )
    settlement_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    excess_payment_move_id = fields.Many2one(
        "account.move",
        string="Excess Payable Cleared By",
        readonly=True,
        copy=False,
        help="Dr employee payable / Cr outgoing clearing for the excess treasury paid.",
    )
    cancel_reason = fields.Char(string="Cancelled Because", readonly=True, copy=False)
    # F11 / E3-17 (owner decision 12 Nov 2026): "cash" was posted to the payment
    # bank journal's account with no bank evidence, so cash handed back at the
    # office became a permanent book-only item of the bank reconciliation.
    # Cash returned debits Cash in Hand; a bank transfer debits the bank.
    recovery_method = fields.Selection(
        [
            ("cash", "Cash returned (cash in hand)"),
            ("bank", "Bank transfer / deposit"),
            ("payroll", "Payroll deduction (A09)"),
        ],
        help="How an unspent balance is recovered: cash handed back debits Cash in Hand; a "
        "bank transfer or deposit debits the payment bank journal's account; a payroll "
        "deduction is requested from payroll.",
    )
    recovery_move_id = fields.Many2one(
        "account.move",
        string="Recovery Entry",
        readonly=True,
        copy=False,
        help="Dr cash in hand or bank / Cr employee advance, for a cash or bank recovery.",
    )

    ADV_GUARDED = {
        "state",
        "requested_by",
        "approved_by",
        "approved_amount",
        "execution_id",
        "disbursement_move_id",
        "disbursement_reversal_move_id",
        "settlement_move_id",
        "settled_posted",
        "excess_requested",
        "recovered_amount",
        "recovery_state",
        "recovery_requested_amount",
        "excess_payment_move_id",
        "cancel_reason",
        "recovery_move_id",
    }
    ADV_TERMS = {
        "amount",
        "employee_id",
        "currency_id",
        "company_id",
        "operating_unit_id",
        "advance_type",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.ADV_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(a.state != "draft" for a in self):
            locked |= self.ADV_TERMS
        return locked

    @api.depends(
        "amount", "recovered_amount", "claim_ids.state", "claim_ids.amount", "claim_ids.move_id"
    )
    def _compute_balance(self):
        for adv in self:
            settled = sum(adv._settling_claims().mapped("amount"))
            adv.settled_amount = min(settled, adv.amount)
            adv.balance = _q(adv.amount - adv.settled_amount - adv.recovered_amount)

    def _settling_claims(self):
        """Approved claims with a posted GL entry (a forged state settles nothing)."""
        self.ensure_one()
        return self.claim_ids.sudo().filtered(
            lambda c: c.state in ("approved", "paid") and c.move_id.state == "posted"
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.employee.advance") or "ADV"
        return super().create(vals_list)

    def write(self, vals):
        if self.ADV_TERMS & set(vals) and not self._fix_guard_open():
            fixed = self.filtered(lambda a: a.state != "draft")
            changed = [
                n
                for n in self.ADV_TERMS & set(vals)
                if any(a._fix_guard_differs(n, vals[n], a[n]) for a in fixed)
            ]
            if changed:
                raise UserError(
                    "Advance %s is %s: %s is fixed by the approval."
                    % (fixed[0].name, fixed[0].state, ", ".join(sorted(changed)))
                )
        return super().write(vals)

    @api.constrains("amount")
    def _check_amount(self):
        for adv in self:
            if adv.amount <= 0:
                raise ValidationError("An advance is a positive amount")

    @api.model
    def _bank_of(self, employee):
        """The employee's primary bank account (HR-restricted field, read as
        superuser only to address the payment)."""
        employee = employee.sudo()
        bank = self.env["res.partner.bank"]
        if "primary_bank_account_id" in employee._fields:
            bank = employee.primary_bank_account_id
        if not bank and "bank_account_ids" in employee._fields:
            bank = employee.bank_account_ids[:1]
        return bank

    def _employee_bank(self):
        return self._bank_of(self.employee_id)

    def _partner(self):
        employee = self.employee_id.sudo()
        return employee.work_contact_id or employee.user_id.partner_id

    def _open_advances(self):
        self.ensure_one()
        return self.sudo().search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("state", "in", ("approved", "disbursed")),
                ("advance_type", "=", "advance"),
                ("id", "!=", self.id),
            ]
        )

    def action_approve(self):
        """Approve (SoD: not the requester, the creator or the employee) and
        hand the disbursement to treasury as a pinned payment request."""
        require_finance(self.env, "Approving an employee advance")
        user = self.env.user
        for adv in self:
            if adv.state != "draft":
                raise UserError("Advance %s is %s" % (adv.name, adv.state))
            if user in (adv.requested_by | adv.create_uid | adv.employee_id.sudo().user_id):
                raise UserError("Segregation of duties: an advance is approved by someone else")
            open_advances = adv._open_advances()
            if adv.advance_type == "advance" and open_advances:
                raise UserError(
                    "%s still holds unsettled advance %s (%s) — settle it first (BRU-APE-17)"
                    % (adv.employee_id.name, open_advances[0].name, open_advances[0].state)
                )
            if "fix.payment.execution" not in self.env:
                raise UserError("Treasury (cd_cash_position) is not installed")
            Execution = self.env["fix.payment.execution"]
            journal = ap_journal(self.env, adv.company_id, "payment")
            label = "employee:%s %s" % (adv.employee_id.id, adv.employee_id.sudo().name)
            # the ONLY way to ask treasury to pay (B1 contract): a pinned
            # draft execution for this payee, account and amount
            execution = Execution._fix_request_payment(
                adv._name,
                adv.id,
                adv._partner(),
                adv._employee_bank(),
                adv.amount,
                adv.currency_id,
                adv.name,
                user,
                method="bank_transfer",
                rail="beftn",  # treasury may change the rail before release
                journal_id=journal.id,
                company_id=adv.company_id.id,
                operating_unit_id=adv.operating_unit_id.id,
                payee=label,
            )
            adv._guarded().write(
                {
                    "state": "approved",
                    "approved_by": user.id,
                    "approved_amount": adv.amount,
                    "execution_id": execution.id,
                }
            )
        return True

    def action_confirm_disbursement(self):
        """Once treasury executed the payment: Dr employee advance / Cr bank,
        for the amount the bank paid, which must be the approved amount."""
        require_finance(self.env, "Confirming an advance disbursement")
        for adv in self:
            if adv.state != "approved":
                raise UserError("Advance %s is not awaiting disbursement" % adv.name)
            execution = adv.execution_id.sudo()
            asserted = (
                "confirmation_source" in execution._fields
                and execution.confirmation_source == "caller_asserted"
            )
            if execution.state != "executed" or asserted:
                raise UserError(
                    "Treasury has no bank confirmation of the disbursement of %s yet (%s)"
                    % (adv.name, execution.state or "no execution")
                )
            paid = _q(execution.amount)
            if abs(paid - _q(adv.amount)) > 0.005 or abs(paid - _q(adv.approved_amount)) > 0.005:
                raise UserError(
                    "Advance %s: approved %.2f, now %.2f, the bank paid %.2f — they must agree."
                    % (adv.name, adv.approved_amount, adv.amount, paid)
                )
            env, company = self.env, adv.company_id
            journal = (
                execution.journal_id
                if "journal_id" in execution._fields and execution.journal_id
                else ap_journal(env, company, "payment")
            )
            label = "Advance %s %s" % (adv.name, adv.employee_id.sudo().name)
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
                        paid,
                        0.0,
                        adv._partner(),
                    ),
                    (journal.default_account_id, label, 0.0, paid, adv._partner()),
                ],
                adv.operating_unit_id,
            )
            adv._guarded().write({"state": "disbursed", "disbursement_move_id": move.id})
        return True

    def action_sync_disbursement(self):
        """Read the disbursement back from treasury (M50). A disbursement
        failed or cancelled AFTER it was executed and booked (a bounce after
        clearing) is reversed here: the advance booked its own entry
        (source_posts_gl), so Dr bank / Cr employee advance, and the advance
        returns to approved, awaiting treasury's re-execution."""
        require_finance(self.env, "Reading an advance disbursement back")
        for adv in self:
            execution = adv.execution_id.sudo()
            if adv.state != "disbursed" or execution.state not in ("failed", "cancelled"):
                continue
            if adv.settled_posted > 0.005 or adv.recovered_amount > 0.005:
                raise UserError(
                    "Advance %s was settled or recovered before the bank returned its "
                    "disbursement: reverse those entries first." % adv.name
                )
            original = adv.disbursement_move_id.sudo()
            label = "Reversal of %s: disbursement of %s returned by the bank (%s)" % (
                original.name or adv.name,
                adv.name,
                execution.failure_reason or execution.state,
            )
            move = post_ap_move(
                self.env,
                adv.company_id,
                original.journal_id,
                fields.Date.context_today(self),
                label,
                [
                    (ml.account_id, label, ml.credit, ml.debit, ml.partner_id)
                    for ml in original.line_ids
                ],
                adv.operating_unit_id,
            )
            adv._guarded().write({"state": "approved", "disbursement_reversal_move_id": move.id})
            adv.message_post(body=label)
        return True

    def action_cancel(self, reason=None):
        """A08 M52-8: an advance not yet paid out is cancelled, with its reason,
        and its open instruction with it: one whose execution failed was stuck
        at approved and blocked every further advance (BRU-APE-17). An instruction
        with the bank is treasury's to resolve first."""
        require_finance(self.env, "Cancelling an employee advance")
        for adv in self:
            if adv.state not in ("draft", "approved"):
                raise UserError(
                    "Advance %s is %s: only a draft or approved advance is cancelled."
                    % (adv.name, adv.state)
                )
            if not (reason or "").strip():
                raise UserError("State why advance %s is cancelled." % adv.name)
            execution = adv.execution_id.sudo()
            if execution.state in ("sent", "executed"):
                raise UserError(
                    "Treasury instruction %s of advance %s is %s: treasury resolves it first."
                    % (execution.name, adv.name, execution.state)
                )
            if execution and execution.state != "cancelled":
                execution.action_cancel()
            adv._guarded().write({"state": "cancelled", "cancel_reason": reason.strip()})
            adv.message_post(body="Advance %s cancelled: %s" % (adv.name, reason.strip()))
        return True

    def action_settle(self):
        """Settle against the approved, posted claims linked to the advance:
        Dr employee payable / Cr employee advance for what is NEW since the
        last settlement (a second press posts nothing). A claim total above
        the advance is paid to the employee (payment request, once); an
        unspent balance must be recovered before closing."""
        require_finance(self.env, "Settling an employee advance")
        for adv in self:
            if adv.state != "disbursed":
                raise UserError("Only a disbursed advance is settled")
            claims = adv._settling_claims()
            if not claims:
                raise UserError("No approved claims are linked to %s" % adv.name)
            env, company = self.env, adv.company_id
            delta = _q(adv.settled_amount - adv.settled_posted)
            excess = _q(sum(claims.mapped("amount")) - adv.amount - adv.excess_requested)
            if delta <= 0.005 and excess <= 0.005:
                raise UserError(
                    "%s has nothing new to settle: %.2f already settled."
                    % (adv.name, adv.settled_posted)
                )
            vals = {}
            if delta > 0.005:
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
                            delta,
                            0.0,
                            adv._partner(),
                        ),
                        (
                            ap_account(env, company, "employee_advance"),
                            label,
                            0.0,
                            delta,
                            adv._partner(),
                        ),
                    ],
                    adv.operating_unit_id,
                )
                vals.update(
                    {
                        "settlement_move_id": move.id,
                        "settled_posted": _q(adv.settled_posted + delta),
                    }
                )
            if excess > 0.005:
                employee = adv.employee_id.sudo()
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
                        "company_id": adv.company_id.id,
                        "payee_partner_id": adv._partner().id or False,
                        "partner_bank_id": adv._bank_of(employee).id or False,
                        "approved_by": self.env.uid,
                    },
                )
                vals["excess_requested"] = _q(adv.excess_requested + excess)
            if adv.balance <= 0.005:
                vals["state"] = "settled"
            adv._guarded().write(vals)
            # claims the advance covers are paid by the set-off; when claims
            # ran above it they are paid when treasury pays the excess
            if adv.excess_requested <= 0.005:
                claims.filtered(lambda c: c.state == "approved")._guarded().write({"state": "paid"})
        return True

    def _recovery_destination(self):
        """(journal, account) a cash or bank recovery debits (F11 / E3-17).

        Bank: the payment bank journal and its account, as before. Cash: Cash
        in Hand, the treasury's branch-cash role (cd_cash_position.account_code.
        branch_cash), else the billing engine's cash role (cd_billing_engine.
        account_code.cash); fail closed when neither is set. The entry goes on
        a cash journal of that account when one exists, else on the general
        journal treasury posts branch cash on, never on the bank journal: the
        bank reconciliation must not see money that never reached the bank."""
        self.ensure_one()
        env, company = self.env, self.company_id
        if self.recovery_method == "bank":
            journal = ap_journal(env, company, "payment")
            return journal, journal.default_account_id
        cash = treasury_account(env, company, "branch_cash", required=False)
        if not cash:
            code = (
                env["ir.config_parameter"].sudo().get_param("cd_billing_engine.account_code.cash")
                or ""
            ).strip()
            if code:
                cash = (
                    env["account.account"]
                    .sudo()
                    .with_company(company)
                    .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
                )
        if not cash:
            raise UserError(
                "No Cash in Hand account in %s for a cash recovery of %s: set system parameter "
                "cd_cash_position.account_code.branch_cash (or cd_billing_engine.account_code."
                "cash) to the account code. Nothing was posted." % (company.name, self.name)
            )
        Journal = env["account.journal"].sudo()
        journal = Journal.search(
            [
                ("company_id", "=", company.id),
                ("type", "=", "cash"),
                ("default_account_id", "=", cash.id),
            ],
            limit=1,
        ) or Journal.search([("company_id", "=", company.id), ("type", "=", "general")], limit=1)
        if not journal:
            raise UserError("%s has no cash or general journal for the recovery." % company.name)
        return journal, cash

    def action_record_recovery(self):
        """Recover the unspent balance: a cash refund posts Dr cash in hand /
        Cr advance, a bank refund Dr bank / Cr advance; payroll deduction is
        requested from payroll (A09) ONCE and closes on payroll's confirmation
        (action_confirm_payroll_recovery)."""
        require_finance(self.env, "Recovering an advance balance")
        for adv in self:
            if adv.state != "disbursed" or adv.balance <= 0.005:
                raise UserError("%s has no open balance to recover" % adv.name)
            if not adv.recovery_method:
                raise UserError("Choose the recovery method first")
            if adv.recovery_state == "requested":
                raise UserError(
                    "A payroll deduction of BDT %.2f is already requested for %s; it closes when "
                    "payroll confirms it." % (adv.recovery_requested_amount, adv.name)
                )
            env, company = self.env, adv.company_id
            amount = adv.balance
            if adv.recovery_method in ("cash", "bank"):
                journal, money_account = adv._recovery_destination()
                label = "Advance refund %s (%s)" % (
                    adv.name,
                    "cash in hand" if adv.recovery_method == "cash" else "bank",
                )
                move = post_ap_move(
                    env,
                    company,
                    journal,
                    fields.Date.context_today(self),
                    label,
                    [
                        (money_account, label, amount, 0.0, adv._partner()),
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
                adv._guarded().write(
                    {
                        "recovered_amount": adv.recovered_amount + amount,
                        "recovery_state": "done",
                        "state": "settled",
                        "recovery_move_id": move.id,
                    }
                )
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
                        "company_id": adv.company_id.id,
                        "advance": adv.name,
                    },
                )
                adv._guarded().write(
                    {"recovery_state": "requested", "recovery_requested_amount": amount}
                )
                adv.message_post(
                    body="Payroll deduction of BDT %.2f requested from payroll (A09); the "
                    "advance closes when payroll confirms the deduction." % amount
                )
        return True

    @api.model
    def consume_advance_recovery_requested(self, event):
        """advance.recovery_requested (A08 M52-8): put the deduction in front of
        payroll as a to-do. Payroll deducts on the next run and accounting (or
        payroll) confirms it here, with the payslip reference. A09 has no input
        that takes an advance deduction by itself: fix.payroll.recovery is for a
        paid payslip that overpaid. Relay only; the payload is not trusted."""
        if not self.env.su:
            raise UserError("This consumer runs only from the event relay.")
        adv = self.browse(event.get("aggregate_id") or 0).exists()
        if not adv or adv.recovery_state != "requested":
            return False
        group = self.env.ref("cd_payroll_bd.group_payroll_officer", raise_if_not_found=False)
        users = group.sudo().all_user_ids.filtered("active") if group else self.env["res.users"]
        summary = "Deduct BDT %.2f (advance %s) from %s on the next payroll" % (
            adv.recovery_requested_amount,
            adv.name,
            adv.employee_id.sudo().name,
        )
        if users:
            adv.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=summary,
                note="Then confirm the deduction on the advance, with the payslip reference.",
                user_id=users[0].id,
            )
        else:
            adv.message_post(body="%s. No payroll officer has a login to take this." % summary)
        return True

    def action_confirm_payroll_recovery(self, amount=None, reference=None):
        """Payroll (A09) confirms the deduction it made: Dr salary payable /
        Cr employee advance. Called by accounting on the advance screen."""
        if not (self.env.su or is_finance(self.env)):
            raise UserError("A payroll recovery is confirmed by payroll or accounting.")
        for adv in self:
            if adv.recovery_state != "requested":
                raise UserError("%s has no payroll deduction awaiting confirmation." % adv.name)
            amount = _q(amount or 0.0)
            if amount <= 0 or amount > _q(adv.recovery_requested_amount) + 0.005:
                raise UserError(
                    "Payroll confirmed %.2f for %s; %.2f was requested."
                    % (amount, adv.name, adv.recovery_requested_amount)
                )
            if not (reference or "").strip():
                raise UserError("Name the payslip / payroll run that made the deduction.")
            env, company = self.env, adv.company_id
            label = "Advance %s recovered through payroll (%s)" % (adv.name, reference.strip())
            post_ap_move(
                env,
                company,
                ap_journal(env, company, "purchase"),
                fields.Date.context_today(self),
                label,
                [
                    (
                        ap_account(env, company, "salary_payable"),
                        label,
                        amount,
                        0.0,
                        adv._partner(),
                    ),
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
            recovered = _q(adv.recovered_amount + amount)
            vals = {"recovered_amount": recovered, "recovery_state": "done"}
            if _q(adv.amount - adv.settled_amount - recovered) <= 0.005:
                vals["state"] = "settled"
            adv._guarded().write(vals)
        return True
