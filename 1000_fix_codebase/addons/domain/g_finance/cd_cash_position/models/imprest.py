# cd_cash_position — Petty Cash (Imprest) (A08 · M50).
#
# An imprest fund per branch holds a fixed ceiling. Vouchers spend from it
# (Dr expense / Cr petty cash, approved by someone other than the custodian
# who raised them); top-ups replenish it from the bank up to the ceiling
# (Dr petty cash / Cr bank); a surprise count reconciles the cash in the box
# against the book balance and books any shortage/over.
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .treasury_common import bank_account_of, gl_balance, post_treasury_move, treasury_account


def _require_manager(env, what):
    if not env.user.has_group("account.group_account_manager"):
        raise UserError("%s needs the accounting manager role." % what)


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
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
    move_id = fields.Many2one("account.move", readonly=True, copy=False)

    @api.constrains("amount")
    def _check_amount(self):
        for v in self:
            if v.amount <= 0:
                raise ValidationError("A voucher amount must be positive.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.imprest.voucher") or "PCV"
        return super().create(vals_list)

    def action_submit(self):
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
            v.write({"state": "submitted", "submitted_by_id": self.env.uid})
        return True

    def action_approve(self):
        for v in self:
            if v.state != "submitted":
                raise UserError("Only a submitted voucher is approved.")
            if v.submitted_by_id == self.env.user:
                raise UserError("Segregation of duties: the submitter cannot approve the voucher.")
            v.write({"state": "approved", "approved_by_id": self.env.uid})
        return True

    def action_reject(self):
        for v in self:
            if v.state not in ("submitted", "approved"):
                raise UserError("Only a voucher awaiting posting is rejected.")
            v.state = "rejected"
        return True

    def action_post(self):
        """Dr expense / Cr petty cash — refused when the box lacks the cash."""
        for v in self:
            if v.state != "approved":
                raise UserError("Only an approved voucher is posted.")
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
                    (v.expense_account_id, v.description, v.amount, 0.0, None),
                    (v.fund_id.account_id, "Petty cash %s" % v.fund_id.name, 0.0, v.amount, None),
                ],
                branch=v.fund_id.branch_id,
                source="treasury",
            )
            v.write({"state": "posted", "move_id": move.id})
        return True


class FixImprestTopup(models.Model):
    _name = "fix.imprest.topup"
    _description = "Petty Cash Top-Up"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.imprest.topup") or "PCT"
        return super().create(vals_list)

    def _check_ceiling(self):
        self.mapped("fund_id").invalidate_recordset(["book_balance", "replenish_amount"])
        for t in self:
            if t.amount <= 0:
                raise UserError("A top-up must be positive.")
            if t.fund_id.book_balance + t.amount > t.fund_id.imprest_limit + 0.005:
                raise UserError(
                    "Top-up %s would take %s above its ceiling %s."
                    % (t.amount, t.fund_id.name, t.fund_id.imprest_limit)
                )

    def action_approve(self):
        for t in self:
            if t.state != "requested":
                raise UserError("Only a requested top-up is approved.")
            if t.requested_by_id == self.env.user:
                raise UserError("Segregation of duties: the requester cannot approve the top-up.")
            _require_manager(self.env, "Approving a petty cash top-up")
            t._check_ceiling()
            t.write({"state": "approved", "approved_by_id": self.env.uid})
        return True

    def action_pay(self):
        """Dr petty cash / Cr bank."""
        for t in self:
            if t.state != "approved":
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
            t.write({"state": "paid", "move_id": move.id})
        return True

    def action_reject(self):
        for t in self:
            if t.state not in ("requested", "approved"):
                raise UserError("Only an unpaid top-up is rejected.")
            t.state = "rejected"
        return True


class FixImprestCount(models.Model):
    """Imprest reconciliation: a physical count against the book balance."""

    _name = "fix.imprest.count"
    _description = "Petty Cash Count"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "count_date desc, id desc"

    fund_id = fields.Many2one("fix.imprest.fund", required=True, index=True, ondelete="restrict")
    company_id = fields.Many2one(related="fund_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="fund_id.operating_unit_id", store=True, index=True)
    currency_id = fields.Many2one(related="fund_id.currency_id")
    count_date = fields.Date(required=True, default=fields.Date.context_today)
    counted_by_id = fields.Many2one("res.users", default=lambda self: self.env.user, readonly=True)
    counted_amount = fields.Monetary(currency_field="currency_id", required=True)
    book_balance = fields.Monetary(currency_field="currency_id", readonly=True)
    variance = fields.Monetary(currency_field="currency_id", readonly=True)
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

    def action_reconcile(self):
        for c in self:
            if c.state != "draft":
                raise UserError("This count was already reconciled.")
            c.fund_id.invalidate_recordset(["book_balance"])
            book = c.fund_id.book_balance
            variance = round(c.counted_amount - book, 2)
            c.write(
                {
                    "book_balance": book,
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
            if c.counted_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: the counter cannot book their own variance."
                )
            _require_manager(self.env, "Booking a petty cash variance")
            short = treasury_account(self.env, c.company_id, "cash_shortage")
            fund_acc = c.fund_id.account_id
            amt = abs(c.variance)
            lines = (
                [
                    (short, "Petty cash short", amt, 0.0, None),
                    (fund_acc, "Petty cash short", 0.0, amt, None),
                ]
                if c.variance < 0
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
            c.write({"state": "booked", "move_id": move.id})
        return True
