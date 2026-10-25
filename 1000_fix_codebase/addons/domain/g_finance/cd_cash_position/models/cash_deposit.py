# cd_cash_position — Cash-in-Transit (A08 · M50): branch cash leaving the
# drawer for the bank. Dispatch moves the money from branch cash to the
# cash-in-transit account; the bank's credit (a statement line) moves it to
# the bank. A short/over credit is a variance, never silently absorbed.
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .treasury_common import bank_account_of, post_treasury_move, treasury_account


class FixCashDeposit(models.Model):
    _name = "fix.cash.deposit"
    _description = "Branch Cash Deposit (Cash-in-Transit)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "business_date desc, id desc"

    name = fields.Char(string="Deposit Ref", readonly=True, copy=False, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True, index=True)
    business_date = fields.Date(
        string="Cash Day", required=True, default=fields.Date.context_today, index=True
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Deposit Into",
        required=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Amount", currency_field="currency_id", required=True)
    slip_no = fields.Char(string="Deposit Slip No", tracking=True)
    carrier = fields.Selection(
        [("staff", "Branch Staff"), ("cit_company", "Cash-in-Transit Company")],
        default="staff",
        required=True,
    )
    carrier_name = fields.Char(string="Carried By")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_transit", "In Transit"),
            ("credited", "Credited by Bank"),
            ("variance", "Variance"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    dispatched_at = fields.Datetime(readonly=True, copy=False)
    statement_line_id = fields.Many2one(
        "fix.bank.statement.line", string="Bank Credit", readonly=True, copy=False
    )
    credited_amount = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)
    credited_date = fields.Date(readonly=True, copy=False)
    variance_amount = fields.Monetary(
        currency_field="currency_id", readonly=True, copy=False, help="Bank credit less deposit"
    )
    dispatch_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    credit_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    variance_move_id = fields.Many2one("account.move", readonly=True, copy=False)

    @api.constrains("amount")
    def _check_amount(self):
        for dep in self:
            if dep.amount <= 0:
                raise ValidationError("A deposit amount must be positive.")

    @api.onchange("branch_id")
    def _onchange_branch(self):
        if self.branch_id.operating_unit_id:
            self.operating_unit_id = self.branch_id.operating_unit_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.cash.deposit") or "CIT"
            if not vals.get("operating_unit_id") and vals.get("branch_id"):
                branch = self.env["fix.branch"].browse(vals["branch_id"])
                vals["operating_unit_id"] = branch.operating_unit_id.id
        return super().create(vals_list)

    def _available_cash(self):
        """Counted cash of the branch's closed shifts on the cash day, less the
        floats they opened with, less what other deposits already took."""
        self.ensure_one()
        shifts = self.env["fix.cash.shift"].search(
            [
                ("branch_id", "=", self.branch_id.id),
                ("shift_date", "=", self.business_date),
                ("state", "in", ("closed", "reconciled", "discrepancy")),
            ]
        )
        counted = sum(shifts.mapped("closing_counted")) - sum(shifts.mapped("opening_float"))
        others = self.search(
            [
                ("branch_id", "=", self.branch_id.id),
                ("business_date", "=", self.business_date),
                ("state", "not in", ("draft", "cancelled")),
                ("id", "!=", self.id),
            ]
        )
        return shifts, round(counted - sum(others.mapped("amount")), 2)

    def action_dispatch(self):
        """Cash leaves the branch: Dr cash-in-transit / Cr branch cash."""
        for dep in self:
            if dep.state != "draft":
                raise UserError("Only a draft deposit is dispatched.")
            shifts, available = dep._available_cash()
            if not shifts:
                raise UserError(
                    "No counted cash shift for %s on %s — count and close the drawer first."
                    % (dep.branch_id.name, dep.business_date)
                )
            if dep.amount > available + 0.005:
                raise UserError(
                    "Deposit %s exceeds the branch's undeposited counted cash for the day (%s)."
                    % (dep.amount, available)
                )
            cit = treasury_account(self.env, dep.company_id, "cash_in_transit")
            cash = treasury_account(self.env, dep.company_id, "branch_cash")
            bank_account_of(dep.journal_id)
            move = post_treasury_move(
                self.env,
                dep.company_id,
                dep.business_date,
                "CIT %s — %s" % (dep.name, dep.branch_id.name),
                [
                    (cit, "Cash in transit %s" % dep.name, dep.amount, 0.0, None),
                    (cash, "Branch cash out %s" % dep.name, 0.0, dep.amount, None),
                ],
                branch=dep.branch_id,
                source="treasury",
            )
            dep.write(
                {
                    "state": "in_transit",
                    "dispatched_at": fields.Datetime.now(),
                    "dispatch_move_id": move.id,
                }
            )
        return True

    def _credit_from_statement(self, line):
        """The bank credited the deposit (called by statement matching)."""
        self.ensure_one()
        if self.state != "in_transit":
            raise UserError("%s is not in transit." % self.name)
        if line.amount <= 0:
            raise UserError("A deposit is matched to a bank CREDIT line.")
        cit = treasury_account(self.env, self.company_id, "cash_in_transit")
        bank = bank_account_of(self.journal_id)
        credited = round(line.amount, 2)
        move = post_treasury_move(
            self.env,
            self.company_id,
            line.date,
            "CIT CREDIT %s — %s" % (self.name, line.reference or ""),
            [
                (bank, "Deposit %s credited" % self.name, credited, 0.0, None),
                (cit, "Cash in transit %s" % self.name, 0.0, credited, None),
            ],
            branch=self.branch_id,
            source="treasury",
        )
        variance = round(credited - self.amount, 2)
        self.write(
            {
                "statement_line_id": line.id,
                "credited_amount": credited,
                "credited_date": line.date,
                "variance_amount": variance,
                "credit_move_id": move.id,
                "state": "credited" if abs(variance) < 0.005 else "variance",
            }
        )

    def action_resolve_variance(self):
        """Close a short/over credit: the difference left in cash-in-transit
        moves to the cash shortage/over account for investigation."""
        for dep in self:
            if dep.state != "variance":
                raise UserError("Only a deposit in variance is resolved.")
            cit = treasury_account(self.env, dep.company_id, "cash_in_transit")
            short = treasury_account(self.env, dep.company_id, "cash_shortage")
            diff = round(dep.amount - dep.credited_amount, 2)  # >0 short, <0 over
            lines = (
                [
                    (short, "Deposit short %s" % dep.name, diff, 0.0, None),
                    (cit, "CIT short", 0.0, diff, None),
                ]
                if diff > 0
                else [
                    (cit, "CIT over", -diff, 0.0, None),
                    (short, "Deposit over %s" % dep.name, 0.0, -diff, None),
                ]
            )
            move = post_treasury_move(
                self.env,
                dep.company_id,
                fields.Date.context_today(self),
                "CIT VARIANCE %s" % dep.name,
                lines,
                branch=dep.branch_id,
                source="treasury",
            )
            dep.write({"state": "credited", "variance_move_id": move.id})
        return True

    def action_cancel(self):
        for dep in self:
            if dep.state != "draft":
                raise UserError("Only a draft deposit is cancelled; a dispatched one is credited.")
            dep.state = "cancelled"
        return True
