# cd_cash_position — Cash-in-Transit (A08 · M50): branch cash leaving the
# drawer for the bank. Dispatch moves the money from branch cash to the
# cash-in-transit account; the bank's credit (a statement line) moves it to
# the bank. A short/over credit is a variance, never silently absorbed.
#
# A08 workflow audit (M50-11): state and evidence stamps are guarded (a
# deposit forged to "in transit" was credited without ever being debited,
# leaving cash-in-transit negative); only a DISPATCHED deposit is credited,
# and only from an imported statement credit; cash-in-transit is never
# relieved beyond what was dispatched (an over-credit goes to cash over/short
# for review); a variance is closed only by an Accounting Administrator, with
# a reason, who did not dispatch the deposit.
from __future__ import annotations

from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .treasury_common import (
    GROUP_ACCOUNTANT,
    GROUP_ADMIN,
    bank_account_of,
    float_param,
    post_treasury_move,
    require_other_person,
    require_role,
    treasury_account,
    treasury_alert,
)

# BRU-TRE-07 / AUT-TRE-09: a dispatched deposit the bank has not credited
# within this many days is an incident. The spec says "the threshold" without
# a value, so the default is 3 days.
PARAM_CIT_INCIDENT_DAYS = "cd_cash_position.cit_unmatched_incident_days"
DEFAULT_CIT_INCIDENT_DAYS = 3


class FixCashDeposit(models.Model):
    _name = "fix.cash.deposit"
    _description = "Branch Cash Deposit (Cash-in-Transit)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    dispatched_by_id = fields.Many2one(
        "res.users", string="Dispatched By", readonly=True, copy=False
    )
    variance_reason = fields.Char(
        string="Variance Explanation",
        tracking=True,
        help="Why the bank credited a different amount; required to close the variance.",
    )
    incident_raised_at = fields.Datetime(
        string="Unmatched Incident Raised",
        readonly=True,
        copy=False,
        help="Set when the deposit stayed uncredited beyond the incident threshold.",
    )
    variance_resolved_by_id = fields.Many2one(
        "res.users", string="Variance Closed By", readonly=True, copy=False
    )
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

    _DEPOSIT_GUARDED = frozenset(
        {
            "name",
            "state",
            "dispatched_at",
            "dispatched_by_id",
            "statement_line_id",
            "credited_amount",
            "credited_date",
            "variance_amount",
            "dispatch_move_id",
            "credit_move_id",
            "variance_move_id",
            "variance_resolved_by_id",
            "incident_raised_at",
        }
    )
    _DEPOSIT_TERMS = ("amount", "branch_id", "journal_id", "business_date", "slip_no", "company_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._DEPOSIT_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(d.state != "draft" for d in self):
            locked |= set(self._DEPOSIT_TERMS)
        return locked

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            terms = set(self._DEPOSIT_TERMS) & set(vals)
            for dep in self.filtered(lambda d: d.state != "draft"):
                changed = [f for f in terms if dep._fix_guard_differs(f, vals[f], dep[f])]
                if changed:
                    raise UserError(
                        "%s left the branch: %s cannot change." % (dep.name, ", ".join(changed))
                    )
        return super().write(vals)

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
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.cash.deposit") or "CIT"
                )
            if not vals.get("operating_unit_id") and vals.get("branch_id"):
                branch = self.env["fix.branch"].browse(vals["branch_id"])
                vals["operating_unit_id"] = branch.operating_unit_id.id
        if self.env.su or self._fix_guard_has_token():
            return super().create(vals_list)
        # the name is the system's sequence; every other stamp is refused
        guarded = self._fix_guarded_fields() - {"name"}
        for vals in vals_list:
            bad = [k for k in guarded & set(vals) if vals[k] not in (False, None, "", 0, 0.0)]
            if vals.get("state", "draft") != "draft":
                bad.append("state")
            if bad:
                self._fix_guard_refuse(set(bad))
        return super(FixCashDeposit, self._guarded()).create(vals_list).with_env(self.env)

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
        require_role(self.env, GROUP_ACCOUNTANT, "Dispatching a branch deposit")
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
            dep._guarded().write(
                {
                    "state": "in_transit",
                    "dispatched_at": fields.Datetime.now(),
                    "dispatched_by_id": self.env.uid,
                    "dispatch_move_id": move.id,
                }
            )
        return True

    def _credit_from_statement(self, line):
        """The bank credited the deposit (called by statement matching).
        Cash-in-transit is relieved by at most what was dispatched: an
        over-credit goes to cash over/short, never below zero in transit."""
        self.ensure_one()
        if self.state != "in_transit" or not self.dispatch_move_id:
            raise UserError("%s was never dispatched: there is nothing in transit." % self.name)
        if line.amount <= 0:
            raise UserError("A deposit is matched to a bank CREDIT line.")
        if not line.statement_file_hash:
            raise UserError("A deposit is credited only from an imported bank statement line.")
        cit = treasury_account(self.env, self.company_id, "cash_in_transit")
        bank = bank_account_of(self.journal_id)
        credited = round(line.amount, 2)
        relieved = min(credited, round(self.amount, 2))
        lines = [
            (bank, "Deposit %s credited" % self.name, credited, 0.0, None),
            (cit, "Cash in transit %s" % self.name, 0.0, relieved, None),
        ]
        if credited > relieved + 0.005:
            over = treasury_account(self.env, self.company_id, "cash_shortage")
            lines.append((over, "Deposit over %s" % self.name, 0.0, credited - relieved, None))
        move = post_treasury_move(
            self.env,
            self.company_id,
            line.date,
            "CIT CREDIT %s — %s" % (self.name, line.reference or ""),
            lines,
            branch=self.branch_id,
            source="treasury",
        )
        variance = round(credited - self.amount, 2)
        self._guarded().write(
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
        """Close a short/over credit. A short credit's difference, still in
        cash-in-transit, is written off to cash shortage/over; an over-credit
        was already booked there at the credit. Either way an Accounting
        Administrator who did not dispatch the deposit closes it, with a
        reason (M50-11)."""
        require_role(self.env, GROUP_ADMIN, "Writing off a deposit variance")
        for dep in self:
            if dep.state != "variance":
                raise UserError("Only a deposit in variance is resolved.")
            if not (dep.variance_reason or "").strip():
                raise UserError("Record why the bank credited a different amount first.")
            require_other_person(
                self.env, dep.dispatched_by_id | dep.create_uid, "Writing off %s" % dep.name
            )
            diff = round(dep.amount - dep.credited_amount, 2)  # >0 short, <0 over
            move = self.env["account.move"]
            if diff > 0.005:
                cit = treasury_account(self.env, dep.company_id, "cash_in_transit")
                short = treasury_account(self.env, dep.company_id, "cash_shortage")
                move = post_treasury_move(
                    self.env,
                    dep.company_id,
                    fields.Date.context_today(self),
                    "CIT VARIANCE %s — %s" % (dep.name, dep.variance_reason),
                    [
                        (short, "Deposit short %s" % dep.name, diff, 0.0, None),
                        (cit, "CIT short", 0.0, diff, None),
                    ],
                    branch=dep.branch_id,
                    source="treasury",
                )
            dep._guarded().write(
                {
                    "state": "credited",
                    "variance_move_id": move.id or False,
                    "variance_resolved_by_id": self.env.uid,
                }
            )
            dep.message_post(
                body="Variance %.2f closed by %s: %s"
                % (diff, self.env.user.name, dep.variance_reason)
            )
        return True

    @api.model
    def _cron_unmatched_deposit_incidents(self):
        """AUT-TRE-09 (ir.cron): deposits dispatched more than the threshold
        ago and still not credited by the bank are raised as incidents, not
        held as reconciling items (BRU-TRE-07). Once per deposit."""
        days = float_param(self.env, PARAM_CIT_INCIDENT_DAYS, DEFAULT_CIT_INCIDENT_DAYS)
        cutoff = fields.Datetime.now() - timedelta(days=days)
        late = self.sudo().search(
            [
                ("state", "=", "in_transit"),
                ("dispatched_at", "!=", False),
                ("dispatched_at", "<=", cutoff),
                ("incident_raised_at", "=", False),
            ]
        )
        for dep in late:
            treasury_alert(
                dep,
                "Unmatched cash deposit",
                "%s of %.2f from %s (slip %s) was dispatched on %s and is not credited by the "
                "bank after %g days (%s)."
                % (
                    dep.name,
                    dep.amount,
                    dep.branch_id.name,
                    dep.slip_no or "-",
                    dep.dispatched_at,
                    days,
                    PARAM_CIT_INCIDENT_DAYS,
                ),
            )
            dep._guarded().write({"incident_raised_at": fields.Datetime.now()})
        return len(late)

    def action_cancel(self):
        for dep in self:
            if dep.state != "draft":
                raise UserError("Only a draft deposit is cancelled; a dispatched one is credited.")
            dep._guarded().write({"state": "cancelled"})
        return True
