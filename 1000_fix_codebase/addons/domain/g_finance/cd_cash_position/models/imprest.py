# cd_cash_position — Petty Cash (Imprest) (A08 · M50).
#
# An imprest fund per branch holds a fixed ceiling. Vouchers spend from it
# (Dr expense / Cr petty cash, approved by someone other than the custodian
# who raised them); top-ups replenish it from the bank up to the ceiling
# (Dr petty cash / Cr bank); a surprise count reconciles the cash in the box
# against the book balance and books any shortage/over.
#
# A08 workflow audit (M50-7, M50-16, P1-3): every state and stamp is guarded
# (submitted_by_id / requested_by_id / counted_by_id were rewritten to defeat
# the maker-checker check); an approved voucher posts exactly the amount
# approved; the custodian never approves the fund's vouchers; a top-up above
# the ceiling is refused when it is raised; and a count is reconciled as
#   variance = cash counted + approved-but-unposted vouchers - book balance
# (the slips in the box are money already spent, not a shortage), recomputed
# when it is booked rather than read from a stored, editable figure.
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .treasury_common import (
    GROUP_ACCOUNTANT,
    GROUP_ADMIN,
    bank_account_of,
    gl_balance,
    post_treasury_move,
    require_other_person,
    require_role,
    treasury_account,
)


def _require_manager(env, what):
    require_role(env, GROUP_ADMIN, what)


def _guarded_create(model, vals_list, extra_ok=("name",)):
    """Refuse guarded values sent by a user on create (the stamps are the
    system's); the system's own defaults are then written under the token."""
    if model.env.su or model._fix_guard_has_token():
        return None
    guarded = model._fix_guarded_fields() - set(extra_ok)
    defaults = model.default_get(list(guarded))
    empty = model.browse()
    for vals in vals_list:
        bad = [
            k
            for k in guarded & set(vals)
            if empty._fix_guard_differs(
                k,
                vals[k],
                empty._fields[k].convert_to_record(
                    empty._fields[k].convert_to_cache(defaults.get(k), empty), empty
                ),
            )
        ]
        if bad:
            model._fix_guard_refuse(set(bad))
    return True


class FixImprestFund(models.Model):
    _name = "fix.imprest.fund"
    _description = "Petty Cash (Imprest) Fund"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True, index=True)
    custodian_id = fields.Many2one("hr.employee", string="Custodian", required=True, tracking=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    imprest_limit = fields.Monetary(
        string="Imprest Ceiling", currency_field="currency_id", required=True, tracking=True
    )
    voucher_limit = fields.Monetary(
        string="Per-Voucher Limit",
        currency_field="currency_id",
        tracking=True,
        help="A single voucher above this amount is refused (0 = no per-voucher limit)",
    )
    account_id = fields.Many2one(
        "account.account",
        string="Petty Cash GL Account",
        required=True,
        help="This fund's own cash account (one account per fund keeps the book balance exact)",
    )
    state = fields.Selection(
        [("active", "Active"), ("closed", "Closed")], default="active", required=True, tracking=True
    )
    book_balance = fields.Monetary(
        string="Book Balance",
        currency_field="currency_id",
        compute="_compute_balances",
        help="Posted GL balance of the fund's petty cash account",
    )
    pending_vouchers = fields.Monetary(
        currency_field="currency_id", compute="_compute_balances", string="Unposted Vouchers"
    )
    replenish_amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_balances",
        string="Top-Up To Ceiling",
    )
    voucher_ids = fields.One2many("fix.imprest.voucher", "fund_id", string="Vouchers")
    topup_ids = fields.One2many("fix.imprest.topup", "fund_id", string="Top-Ups")
    count_ids = fields.One2many("fix.imprest.count", "fund_id", string="Cash Counts")

    _account_unique = models.Constraint(
        "UNIQUE (account_id)", "Each imprest fund keeps its own petty cash account."
    )

    @api.constrains("imprest_limit", "voucher_limit")
    def _check_limits(self):
        for fund in self:
            if fund.imprest_limit <= 0:
                raise ValidationError("The imprest ceiling must be positive.")
            if fund.voucher_limit < 0 or fund.voucher_limit > fund.imprest_limit:
                raise ValidationError("The per-voucher limit must lie within the ceiling.")

    def _compute_balances(self):
        for fund in self:
            fund.book_balance = gl_balance(self.env, fund.account_id, fund.company_id)
            fund.pending_vouchers = sum(
                fund.voucher_ids.filtered(lambda v: v.state in ("submitted", "approved")).mapped(
                    "amount"
                )
            )
            open_topups = sum(
                fund.topup_ids.filtered(lambda t: t.state in ("requested", "approved")).mapped(
                    "amount"
                )
            )
            fund.replenish_amount = max(fund.imprest_limit - fund.book_balance - open_topups, 0.0)

    def _fix_approved_unposted(self) -> float:
        """Vouchers approved (cash paid out of the box) but not yet posted."""
        self.ensure_one()
        return round(
            sum(
                self.voucher_ids.filtered(lambda v: v.state == "approved").mapped("approved_amount")
            ),
            2,
        )

    def action_request_topup(self):
        """Raise a top-up request for exactly what restores the ceiling."""
        created = self.env["fix.imprest.topup"]
        for fund in self:
            if fund.state != "active":
                raise UserError("%s is closed." % fund.name)
            fund.invalidate_recordset(["book_balance", "replenish_amount"])
            if fund.replenish_amount <= 0.005:
                raise UserError("%s is at its ceiling — nothing to top up." % fund.name)
            created |= created.create({"fund_id": fund.id, "amount": fund.replenish_amount})
        return {"topup_ids": created.ids}


class FixImprestVoucher(models.Model):
    _name = "fix.imprest.voucher"
    _description = "Petty Cash Voucher"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "voucher_date desc, id desc"

    name = fields.Char(string="Voucher No", readonly=True, copy=False, index=True)
    fund_id = fields.Many2one("fix.imprest.fund", required=True, index=True, ondelete="restrict")
    company_id = fields.Many2one(related="fund_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="fund_id.operating_unit_id", store=True, index=True)
    currency_id = fields.Many2one(related="fund_id.currency_id")
    voucher_date = fields.Date(required=True, default=fields.Date.context_today)
    description = fields.Char(required=True)
    payee = fields.Char()
    expense_account_id = fields.Many2one("account.account", string="Expense Account", required=True)
    amount = fields.Monetary(currency_field="currency_id", required=True)
    receipt_ref = fields.Char(string="Receipt / Bill Ref")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("posted", "Posted"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    submitted_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_amount = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The amount the approver signed off; the voucher posts exactly this.",
    )
    move_id = fields.Many2one("account.move", readonly=True, copy=False)

    _VOUCHER_GUARDED = frozenset(
        {"name", "state", "submitted_by_id", "approved_by_id", "approved_amount", "move_id"}
    )
    _VOUCHER_TERMS = ("fund_id", "amount", "expense_account_id", "voucher_date", "receipt_ref")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._VOUCHER_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(v.state != "draft" for v in self):
            locked |= set(self._VOUCHER_TERMS) | {"description", "payee"}
        return locked

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            terms = set(self._VOUCHER_TERMS) & set(vals)
            for v in self.filtered(lambda x: x.state != "draft"):
                changed = [f for f in terms if v._fix_guard_differs(f, vals[f], v[f])]
                if changed:
                    raise UserError(
                        "Voucher %s was submitted: %s cannot change (approval covers what was "
                        "submitted)." % (v.name, ", ".join(changed))
                    )
        return super().write(vals)

    @api.constrains("amount")
    def _check_amount(self):
        for v in self:
            if v.amount <= 0:
                raise ValidationError("A voucher amount must be positive.")

    @api.model_create_multi
    def create(self, vals_list):
        refused = _guarded_create(self, vals_list)
        for vals in vals_list:
            if refused or not vals.get("name"):
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.imprest.voucher") or "PCV"
                )
        if refused:
            return super(FixImprestVoucher, self._guarded()).create(vals_list).with_env(self.env)
        return super().create(vals_list)

    def action_submit(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Submitting a petty cash voucher")
        for v in self:
            if v.state != "draft":
                raise UserError("Only a draft voucher is submitted.")
            if v.fund_id.state != "active":
                raise UserError("%s is closed." % v.fund_id.name)
            if v.fund_id.voucher_limit and v.amount > v.fund_id.voucher_limit + 0.005:
                raise UserError(
                    "Voucher %s exceeds the per-voucher limit %s of %s."
                    % (v.amount, v.fund_id.voucher_limit, v.fund_id.name)
                )
            if not (v.receipt_ref or "").strip():
                raise UserError("Attach the receipt / bill reference before submitting.")
            v._guarded().write({"state": "submitted", "submitted_by_id": self.env.uid})
        return True

    def action_approve(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Approving a petty cash voucher")
        for v in self:
            if v.state != "submitted":
                raise UserError("Only a submitted voucher is approved.")
            if not self.env.su and v.submitted_by_id == self.env.user:
                raise UserError("Segregation of duties: the submitter cannot approve the voucher.")
            custodian = v.fund_id.custodian_id.sudo().user_id
            if not self.env.su and custodian and custodian == self.env.user:
                raise UserError(
                    "Segregation of duties: the custodian of %s does not approve its vouchers."
                    % v.fund_id.name
                )
            v._guarded().write(
                {"state": "approved", "approved_by_id": self.env.uid, "approved_amount": v.amount}
            )
        return True

    def action_reject(self):
        for v in self:
            if v.state not in ("submitted", "approved"):
                raise UserError("Only a voucher awaiting posting is rejected.")
            v._guarded().write({"state": "rejected"})
        return True

    def action_post(self):
        """Dr expense / Cr petty cash — refused when the box lacks the cash."""
        require_role(self.env, GROUP_ACCOUNTANT, "Posting a petty cash voucher")
        for v in self:
            if v.state != "approved" or not v.approved_by_id:
                raise UserError("Only an approved voucher is posted.")
            if abs(v.amount - v.approved_amount) > 0.005:
                raise UserError(
                    "Voucher %s was approved for %.2f but reads %.2f: it is not posted."
                    % (v.name, v.approved_amount, v.amount)
                )
            v.fund_id.invalidate_recordset(["book_balance", "replenish_amount"])
            if v.amount > v.fund_id.book_balance + 0.005:
                raise UserError(
                    "%s holds %s — voucher %s cannot be paid; top up first."
                    % (v.fund_id.name, v.fund_id.book_balance, v.amount)
                )
            move = post_treasury_move(
                self.env,
                v.company_id,
                v.voucher_date,
                "PCV %s — %s" % (v.name, v.description),
                [
                    (v.expense_account_id, v.description, v.approved_amount, 0.0, None),
                    (
                        v.fund_id.account_id,
                        "Petty cash %s" % v.fund_id.name,
                        0.0,
                        v.approved_amount,
                        None,
                    ),
                ],
                branch=v.fund_id.branch_id,
                source="treasury",
            )
            v._guarded().write({"state": "posted", "move_id": move.id})
        return True


class FixImprestTopup(models.Model):
    _name = "fix.imprest.topup"
    _description = "Petty Cash Top-Up"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(string="Top-Up Ref", readonly=True, copy=False, index=True)
    fund_id = fields.Many2one("fix.imprest.fund", required=True, index=True, ondelete="restrict")
    company_id = fields.Many2one(related="fund_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="fund_id.operating_unit_id", store=True, index=True)
    currency_id = fields.Many2one(related="fund_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id", required=True)
    journal_id = fields.Many2one(
        "account.journal",
        string="Paid From",
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
    )
    topup_date = fields.Date(default=fields.Date.context_today, required=True)
    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("paid", "Paid"),
            ("rejected", "Rejected"),
        ],
        default="requested",
        required=True,
        tracking=True,
    )
    requested_by_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True, copy=False
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    move_id = fields.Many2one("account.move", readonly=True, copy=False)

    _TOPUP_GUARDED = frozenset({"name", "state", "requested_by_id", "approved_by_id", "move_id"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._TOPUP_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(t.state != "requested" for t in self):
            locked |= {"fund_id", "amount", "journal_id"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        refused = _guarded_create(self, vals_list)
        for vals in vals_list:
            if refused or not vals.get("name"):
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.imprest.topup") or "PCT"
                )
        if refused:
            return super(FixImprestTopup, self._guarded()).create(vals_list).with_env(self.env)
        return super().create(vals_list)

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            terms = {"fund_id", "amount"} & set(vals)
            for t in self.filtered(lambda x: x.state != "requested"):
                changed = [f for f in terms if t._fix_guard_differs(f, vals[f], t[f])]
                if changed:
                    raise UserError(
                        "Top-up %s was approved: %s cannot change." % (t.name, ", ".join(changed))
                    )
        return super().write(vals)

    @api.constrains("amount", "fund_id", "state")
    def _check_request_ceiling(self):
        """M50-16: a request above what restores the ceiling is refused when it
        is raised, not only when someone approves it."""
        for t in self.filtered(lambda x: x.state in ("requested", "approved")):
            t._check_ceiling()

    def _check_ceiling(self):
        self.mapped("fund_id").invalidate_recordset(["book_balance", "replenish_amount"])
        for t in self:
            if t.amount <= 0:
                raise UserError("A top-up must be positive.")
            others = sum(
                t.fund_id.topup_ids.filtered(
                    lambda x, t=t: x.id != t.id and x.state in ("requested", "approved")
                ).mapped("amount")
            )
            if t.fund_id.book_balance + others + t.amount > t.fund_id.imprest_limit + 0.005:
                raise UserError(
                    "Top-up %s would take %s above its ceiling %s (book %s, other open top-ups "
                    "%s)."
                    % (
                        t.amount,
                        t.fund_id.name,
                        t.fund_id.imprest_limit,
                        t.fund_id.book_balance,
                        others,
                    )
                )

    def action_approve(self):
        for t in self:
            if t.state != "requested":
                raise UserError("Only a requested top-up is approved.")
            require_other_person(
                self.env, t.requested_by_id | t.create_uid, "Approving top-up %s" % t.name
            )
            _require_manager(self.env, "Approving a petty cash top-up")
            t._check_ceiling()
            t._guarded().write({"state": "approved", "approved_by_id": self.env.uid})
        return True

    def action_pay(self):
        """Dr petty cash / Cr bank."""
        require_role(self.env, GROUP_ACCOUNTANT, "Paying a petty cash top-up")
        for t in self:
            if t.state != "approved" or not t.approved_by_id:
                raise UserError("Only an approved top-up is paid.")
            t._check_ceiling()
            bank = bank_account_of(t.journal_id)
            move = post_treasury_move(
                self.env,
                t.company_id,
                t.topup_date,
                "PCT %s — %s" % (t.name, t.fund_id.name),
                [
                    (t.fund_id.account_id, "Imprest top-up %s" % t.name, t.amount, 0.0, None),
                    (bank, "Imprest top-up %s" % t.fund_id.name, 0.0, t.amount, None),
                ],
                branch=t.fund_id.branch_id,
                source="treasury",
            )
            t._guarded().write({"state": "paid", "move_id": move.id})
        return True

    def action_reject(self):
        for t in self:
            if t.state not in ("requested", "approved"):
                raise UserError("Only an unpaid top-up is rejected.")
            t._guarded().write({"state": "rejected"})
        return True


class FixImprestCount(models.Model):
    """Imprest reconciliation: a physical count against the book balance."""

    _name = "fix.imprest.count"
    _description = "Petty Cash Count"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "count_date desc, id desc"

    fund_id = fields.Many2one("fix.imprest.fund", required=True, index=True, ondelete="restrict")
    company_id = fields.Many2one(related="fund_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="fund_id.operating_unit_id", store=True, index=True)
    currency_id = fields.Many2one(related="fund_id.currency_id")
    count_date = fields.Date(required=True, default=fields.Date.context_today)
    counted_by_id = fields.Many2one("res.users", default=lambda self: self.env.user, readonly=True)
    counted_amount = fields.Monetary(currency_field="currency_id", required=True)
    book_balance = fields.Monetary(currency_field="currency_id", readonly=True)
    pending_vouchers_amount = fields.Monetary(
        string="Approved Unposted Vouchers",
        currency_field="currency_id",
        readonly=True,
        help="Vouchers approved and paid out of the box but not yet posted at the count",
    )
    variance = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        help="Cash counted + approved unposted vouchers - book balance (system-computed)",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("balanced", "Balanced"),
            ("variance", "Variance"),
            ("booked", "Variance Booked"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    move_id = fields.Many2one("account.move", readonly=True, copy=False)

    _COUNT_GUARDED = frozenset(
        {"state", "counted_by_id", "book_balance", "pending_vouchers_amount", "variance", "move_id"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._COUNT_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(c.state != "draft" for c in self):
            locked |= {"fund_id", "counted_amount", "count_date"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if _guarded_create(self, vals_list, extra_ok=()):
            return super(FixImprestCount, self._guarded()).create(vals_list).with_env(self.env)
        return super().create(vals_list)

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            terms = {"fund_id", "counted_amount", "count_date"} & set(vals)
            for c in self.filtered(lambda x: x.state != "draft"):
                changed = [f for f in terms if c._fix_guard_differs(f, vals[f], c[f])]
                if changed:
                    raise UserError(
                        "A reconciled count is evidence: %s cannot change." % (", ".join(changed))
                    )
        return super().write(vals)

    def _fix_compute_variance(self):
        """(book, pending vouchers, variance) from the live GL and vouchers."""
        self.ensure_one()
        self.fund_id.invalidate_recordset(["book_balance"])
        book = round(self.fund_id.book_balance, 2)
        pending = self.fund_id._fix_approved_unposted()
        return book, pending, round(self.counted_amount + pending - book, 2)

    def action_reconcile(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Reconciling a petty cash count")
        for c in self:
            if c.state != "draft":
                raise UserError("This count was already reconciled.")
            book, pending, variance = c._fix_compute_variance()
            c._guarded().write(
                {
                    "book_balance": book,
                    "pending_vouchers_amount": pending,
                    "variance": variance,
                    "state": "balanced" if abs(variance) < 0.005 else "variance",
                }
            )
        return True

    def action_book_variance(self):
        """Book the difference to cash shortage/over (manager, not the counter)."""
        for c in self:
            if c.state != "variance":
                raise UserError("Only a count with a variance is booked.")
            if not self.env.su and c.counted_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: the counter cannot book their own variance."
                )
            _require_manager(self.env, "Booking a petty cash variance")
            custodian = c.fund_id.custodian_id.sudo().user_id
            if not self.env.su and custodian and custodian == self.env.user:
                raise UserError(
                    "Segregation of duties: the custodian does not book the fund's variance."
                )
            _book, _pending, variance = c._fix_compute_variance()
            if abs(variance - c.variance) > 0.005:
                raise UserError(
                    "The fund moved since this count (variance now %.2f, counted %.2f): count "
                    "the box again." % (variance, c.variance)
                )
            short = treasury_account(self.env, c.company_id, "cash_shortage")
            fund_acc = c.fund_id.account_id
            amt = abs(variance)
            lines = (
                [
                    (short, "Petty cash short", amt, 0.0, None),
                    (fund_acc, "Petty cash short", 0.0, amt, None),
                ]
                if variance < 0
                else [
                    (fund_acc, "Petty cash over", amt, 0.0, None),
                    (short, "Petty cash over", 0.0, amt, None),
                ]
            )
            move = post_treasury_move(
                self.env,
                c.company_id,
                c.count_date,
                "PETTY CASH COUNT %s" % c.fund_id.name,
                lines,
                branch=c.fund_id.branch_id,
                source="treasury",
            )
            c._guarded().write({"state": "booked", "move_id": move.id})
        return True
