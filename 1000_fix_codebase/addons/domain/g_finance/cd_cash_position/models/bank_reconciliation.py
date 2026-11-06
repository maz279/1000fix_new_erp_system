# cd_cash_position — the bank reconciliation statement (A08 · M50, M50-6,
# FR-TRE-012, BRU-TRE-19).
#
# One statement per bank account and period, prepared by an accountant and
# reviewed by a different Accounting Administrator:
#
#     closing balance per the bank's statement       (typed from the statement)
#   + entries in our books the bank has not shown    (posted GL, no statement line)
#   = adjusted bank balance
#
#     balance per the GL at period end
#   + lines the bank has shown that our books do not (unmatched / unbooked lines)
#   = adjusted book balance
#
# The two must agree; a difference is explained in words, and so is every
# reconciling item at or beyond the configured age. Payments released but not
# confirmed and deposits in transit post to the bank's GL account only on the
# bank's evidence (treasury's posting rule), so they are on neither side: they
# are listed for the reviewer and do not enter the arithmetic.
#
# The figures are recomputed at submission and again at review: a statement
# whose ledger moved after it was prepared is not signed off.
from __future__ import annotations

import re
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .treasury_common import (
    GROUP_ACCOUNTANT,
    GROUP_ADMIN,
    float_param,
    gl_balance,
    require_other_person,
    require_role,
)

PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
# Spec: "every reconciling item older than the threshold is explained", with no
# value given. 0 means every reconciling item is explained.
PARAM_ITEM_AGE = "cd_cash_position.recon_item_age_days"
PENNY = 0.005

ITEM_KINDS = [
    ("statement_line", "On the Bank Statement, Not Matched"),
    ("statement_unbooked", "Matched, Not Yet in the Books"),
    ("book_item", "In the Books, Not on the Statement"),
    ("payment_sent", "Payment Released, Awaiting Bank (info)"),
    ("deposit_in_transit", "Deposit in Transit (info)"),
]
STATEMENT_KINDS = ("statement_line", "statement_unbooked")


class FixBankReconciliation(models.Model):
    _name = "fix.bank.reconciliation"
    _description = "Bank Reconciliation Statement"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "period desc, journal_id, id desc"
    _journal_period_unique = models.Constraint(
        "UNIQUE (company_id, journal_id, period)",
        "This bank account already has a reconciliation statement for the period.",
    )

    name = fields.Char(compute="_compute_name", store=True, string="Statement")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    journal_id = fields.Many2one(
        "account.journal",
        string="Bank Account",
        required=True,
        index=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
    )
    period = fields.Char(required=True, size=7, index=True, help="YYYY-MM")
    date_to = fields.Date(string="Period End", compute="_compute_date_to", store=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    statement_ref = fields.Char(string="Bank Statement No. / Page", tracking=True)
    statement_balance = fields.Monetary(
        string="Closing Balance per Statement", currency_field="currency_id", tracking=True
    )
    gl_balance = fields.Monetary(
        string="Balance per GL", currency_field="currency_id", readonly=True
    )
    unmatched_net = fields.Monetary(
        string="On Statement, Not in Books", currency_field="currency_id", readonly=True
    )
    book_items_net = fields.Monetary(
        string="In Books, Not on Statement", currency_field="currency_id", readonly=True
    )
    adjusted_bank_balance = fields.Monetary(
        string="Adjusted Bank Balance",
        currency_field="currency_id",
        compute="_compute_adjusted",
        store=True,
    )
    adjusted_book_balance = fields.Monetary(
        string="Adjusted Book Balance",
        currency_field="currency_id",
        compute="_compute_adjusted",
        store=True,
    )
    difference = fields.Monetary(
        currency_field="currency_id", compute="_compute_adjusted", store=True
    )
    difference_note = fields.Char(string="Explanation of the Difference", tracking=True)
    line_ids = fields.One2many(
        "fix.bank.reconciliation.line", "reconciliation_id", string="Reconciling Items"
    )
    item_count = fields.Integer(compute="_compute_item_counts", string="Items")
    unexplained_count = fields.Integer(compute="_compute_item_counts", string="Unexplained")
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted for Review"), ("reviewed", "Reviewed")],
        default="draft",
        required=True,
        tracking=True,
    )
    prepared_by_id = fields.Many2one("res.users", string="Prepared By", readonly=True, copy=False)
    prepared_at = fields.Datetime(string="Prepared On", readonly=True, copy=False)
    reviewed_by_id = fields.Many2one("res.users", string="Reviewed By", readonly=True, copy=False)
    reviewed_at = fields.Datetime(string="Reviewed On", readonly=True, copy=False)
    return_reason = fields.Char(string="Returned Because", readonly=True, copy=False, tracking=True)

    _RECON_GUARDED = frozenset(
        {
            "gl_balance",
            "unmatched_net",
            "book_items_net",
            "line_ids",
            "state",
            "prepared_by_id",
            "prepared_at",
            "reviewed_by_id",
            "reviewed_at",
            "return_reason",
        }
    )
    _RECON_TERMS = frozenset(
        {
            "journal_id",
            "period",
            "company_id",
            "currency_id",
            "statement_ref",
            "statement_balance",
            "difference_note",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._RECON_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"journal_id", "period", "company_id", "currency_id"}
            if any(r.state != "draft" for r in self):
                locked |= set(self._RECON_TERMS)
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            moving = set(self._RECON_TERMS) & set(vals)
            for rec in self:
                changed = [f for f in moving if rec._fix_guard_differs(f, vals[f], rec[f])]
                if rec.state != "draft" and changed:
                    raise UserError(
                        "%s is %s: return it to draft before changing %s."
                        % (rec.name, rec.state, ", ".join(sorted(changed)))
                    )
                if rec.line_ids and {"journal_id", "period", "company_id"} & set(changed):
                    raise UserError("%s is prepared for its account and period." % rec.name)
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _fix_unlink_draft_only(self):
        if any(rec.state != "draft" for rec in self):
            raise UserError("A submitted or reviewed reconciliation statement is not deleted.")

    @api.constrains("period")
    def _check_period(self):
        for rec in self:
            if not PERIOD_RE.match(rec.period or ""):
                raise ValidationError("The reconciliation period is YYYY-MM.")

    @api.constrains("journal_id", "company_id")
    def _check_journal(self):
        for rec in self:
            if rec.journal_id.type != "bank" or rec.journal_id.company_id != rec.company_id:
                raise ValidationError("A reconciliation statement is for a bank account.")

    @api.depends("journal_id", "period")
    def _compute_name(self):
        for rec in self:
            rec.name = "REC/%s/%s" % (rec.journal_id.code or "", rec.period or "")

    @api.depends("period")
    def _compute_date_to(self):
        for rec in self:
            if PERIOD_RE.match(rec.period or ""):
                first = date(int(rec.period[:4]), int(rec.period[5:7]), 1)
                rec.date_to = first + relativedelta(months=1, days=-1)
            else:
                rec.date_to = False

    @api.depends("statement_balance", "gl_balance", "unmatched_net", "book_items_net")
    def _compute_adjusted(self):
        for rec in self:
            rec.adjusted_bank_balance = round(rec.statement_balance + rec.book_items_net, 2)
            rec.adjusted_book_balance = round(rec.gl_balance + rec.unmatched_net, 2)
            rec.difference = round(rec.adjusted_bank_balance - rec.adjusted_book_balance, 2)

    def _compute_item_counts(self):
        for rec in self:
            lines = rec.sudo().line_ids.filtered("counts")
            rec.item_count = len(lines)
            rec.unexplained_count = len(rec._fix_unexplained())

    # ------------------------------------------------------------ the figures

    def _fix_evidenced_moves(self, matched):
        """(moves the matched statement lines evidence, the matched lines whose
        posting cannot be named: a received cheque posts through its AR receipt,
        a batch not yet posted has none)."""
        moves = self.env["account.move"]
        loose = matched.browse()
        for line in matched:
            found = (
                line.charge_move_id
                | line.matched_payment_id.move_id
                | line.matched_deposit_id.credit_move_id
                | line.matched_gateway_id.move_id
                | line.matched_cheque_id.payment_execution_id.move_id
            )
            if found:
                moves |= found
            else:
                loose |= line
        return moves, loose

    def _fix_items(self):
        """The reconciling items at the period end, computed from the ledger and
        the imported lines (sudo with an explicit company: a figure must not
        depend on which operating units the preparer sees)."""
        self.ensure_one()
        env = self.env
        company, journal, end = self.company_id, self.journal_id, self.date_to
        Line = env["fix.bank.statement.line"].sudo()
        scope = [
            ("company_id", "=", company.id),
            ("journal_id", "=", journal.id),
            ("statement_file_hash", "!=", False),
            ("date", "<=", end),
        ]
        items = []

        def add(kind, day, reference, amount, key, counts=True):
            items.append(
                {
                    "kind": kind,
                    "date": day,
                    "reference": reference or "",
                    "amount": round(amount, 2),
                    "counts": counts,
                    "age_days": max((end - day).days, 0) if day else 0,
                    "source_key": key,
                }
            )

        for line in Line.search([*scope, ("match_state", "=", "unmatched")], order="date, id"):
            add(
                "statement_line",
                line.date,
                line.reference or line.narration,
                line.amount,
                "stmt:%s" % line.id,
            )
        moves, loose = self._fix_evidenced_moves(
            Line.search([*scope, ("match_state", "!=", "unmatched")], order="date, id")
        )
        account = journal.default_account_id
        book = (
            env["account.move.line"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("account_id", "=", account.id),
                    ("parent_state", "=", "posted"),
                    ("date", "<=", end),
                    ("move_id", "not in", moves.ids),
                ],
                order="date, id",
            )
        )
        book = list(book)
        for line in loose:
            # its posting cannot be named: the unexplained book line of the same
            # amount is that posting; with none, the bank has what the books lack
            twin = next((b for b in book if abs(b.balance - line.amount) < PENNY), None)
            if twin:
                book.remove(twin)
            else:
                add(
                    "statement_unbooked",
                    line.date,
                    line.reference or line.narration,
                    line.amount,
                    "stmt:%s" % line.id,
                )
        for aml in book:
            add(
                "book_item",
                aml.date,
                aml.move_id.name or aml.name,
                aml.balance,
                "aml:%s" % aml.id,
            )
        Payment = env["fix.payment.execution"].sudo()
        for pay in Payment.search(
            [
                ("company_id", "=", company.id),
                ("state", "=", "sent"),
                "|",
                ("released_journal_id", "=", journal.id),
                ("journal_id", "=", journal.id),
            ],
            order="id",
        ):
            sent = pay.sent_at.date() if pay.sent_at else end
            if sent <= end:
                add(
                    "payment_sent",
                    sent,
                    pay.name,
                    -(pay.released_amount or pay.amount),
                    "pex:%s" % pay.id,
                    counts=False,
                )
        for dep in (
            env["fix.cash.deposit"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("journal_id", "=", journal.id),
                    ("state", "=", "in_transit"),
                    ("business_date", "<=", end),
                ],
                order="id",
            )
        ):
            add(
                "deposit_in_transit",
                dep.business_date,
                dep.slip_no or dep.name,
                dep.amount,
                "dep:%s" % dep.id,
                counts=False,
            )
        return items

    def _fix_figures(self, items):
        self.ensure_one()
        return {
            "gl_balance": gl_balance(
                self.env(su=True),
                self.journal_id.default_account_id,
                self.company_id,
                date_to=self.date_to,
            ),
            "unmatched_net": round(
                sum(i["amount"] for i in items if i["kind"] in STATEMENT_KINDS), 2
            ),
            "book_items_net": round(sum(i["amount"] for i in items if i["kind"] == "book_item"), 2),
        }

    def _fix_explanations(self):
        """What earlier statements of this account said about an item still open."""
        self.ensure_one()
        lines = (
            self.env["fix.bank.reconciliation.line"]
            .sudo()
            .search(
                [
                    ("reconciliation_id.journal_id", "=", self.journal_id.id),
                    ("reconciliation_id.period", "<=", self.period),
                    ("explanation", "!=", False),
                ],
                order="id",
            )
        )
        return {ln.source_key: ln for ln in lines}

    def _fix_rebuild(self):
        self.ensure_one()
        items = self._fix_items()
        known = self._fix_explanations()
        for item in items:
            prior = known.get(item["source_key"])
            if prior:
                item["explanation"] = prior.explanation
                item["explained_by_id"] = prior.explained_by_id.id
        self.sudo().line_ids._guarded().unlink()
        self._guarded().write({**self._fix_figures(items), "line_ids": [(0, 0, i) for i in items]})

    def _fix_unexplained(self):
        """Reconciling items at or beyond the configured age with no explanation."""
        self.ensure_one()
        age = float_param(self.env, PARAM_ITEM_AGE, 0.0)
        return self.sudo().line_ids.filtered(
            lambda ln: ln.counts and ln.age_days >= age and not (ln.explanation or "").strip()
        )

    # --------------------------------------------------------------- workflow

    def action_prepare(self):
        """(Re)compute the statement from the ledger and the imported lines."""
        require_role(self.env, GROUP_ACCOUNTANT, "Preparing a bank reconciliation")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is %s: return it to draft first." % (rec.name, rec.state))
            rec._fix_rebuild()
            rec._guarded().write(
                {"prepared_by_id": self.env.uid, "prepared_at": fields.Datetime.now()}
            )
        return True

    def action_submit(self):
        """The preparer states the bank's closing balance; every aged item and
        any difference is explained, on figures recomputed now."""
        require_role(self.env, GROUP_ACCOUNTANT, "Submitting a bank reconciliation")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            if not (rec.statement_ref or "").strip():
                raise UserError(
                    "%s: name the bank statement the closing balance is taken from." % rec.name
                )
            rec._fix_rebuild()
            unexplained = rec._fix_unexplained()
            if unexplained:
                raise UserError(
                    "%s: %d reconciling item(s) are not explained (%s)."
                    % (
                        rec.name,
                        len(unexplained),
                        ", ".join(unexplained[:5].mapped("reference")),
                    )
                )
            if abs(rec.difference) > PENNY and not (rec.difference_note or "").strip():
                raise UserError(
                    "%s does not reconcile by %.2f: explain the difference."
                    % (rec.name, rec.difference)
                )
            rec._guarded().write(
                {
                    "state": "submitted",
                    "prepared_by_id": self.env.uid,
                    "prepared_at": fields.Datetime.now(),
                    "return_reason": False,
                }
            )
        return True

    def action_review(self):
        """A different Accounting Administrator signs the statement off."""
        require_role(self.env, GROUP_ADMIN, "Reviewing a bank reconciliation")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted statement is reviewed.")
            require_other_person(
                self.env,
                rec.prepared_by_id | rec.create_uid,
                "Reviewing %s" % rec.name,
            )
            items = rec._fix_items()
            now = rec._fix_figures(items)
            moved = [name for name, value in now.items() if abs(value - rec[name]) > PENNY]
            if moved:
                raise UserError(
                    "%s: the ledger moved after it was prepared (%s). Return it so the "
                    "preparer re-states it." % (rec.name, ", ".join(sorted(moved)))
                )
            rec._guarded().write(
                {
                    "state": "reviewed",
                    "reviewed_by_id": self.env.uid,
                    "reviewed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_return(self, reason=None):
        """Back to the preparer, with the reason. A reviewed statement reopens
        the same way when a later entry falls into its period."""
        require_role(self.env, GROUP_ADMIN, "Returning a bank reconciliation")
        why = (reason or "").strip()
        if not why:
            raise UserError("State why the statement is returned.")
        for rec in self:
            if rec.state == "draft":
                raise UserError("%s is already a draft." % rec.name)
            rec._guarded().write(
                {
                    "state": "draft",
                    "return_reason": why,
                    "reviewed_by_id": False,
                    "reviewed_at": False,
                }
            )
        return True


class FixBankReconciliationLine(models.Model):
    """One reconciling item, written by the statement's preparation."""

    _name = "fix.bank.reconciliation.line"
    _description = "Bank Reconciliation Item"
    _inherit = ["fix.guarded.mixin"]
    _order = "reconciliation_id desc, date, id"

    reconciliation_id = fields.Many2one(
        "fix.bank.reconciliation", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="reconciliation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="reconciliation_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="reconciliation_id.currency_id")
    state = fields.Selection(related="reconciliation_id.state", string="Statement State")
    kind = fields.Selection(ITEM_KINDS, required=True)
    date = fields.Date()
    reference = fields.Char()
    amount = fields.Monetary(currency_field="currency_id")
    counts = fields.Boolean(string="In the Arithmetic", default=True)
    age_days = fields.Integer(string="Age (Days)")
    source_key = fields.Char(index=True, help="stmt:<id>, aml:<id>, pex:<id>, dep:<id>")
    explanation = fields.Char()
    explained_by_id = fields.Many2one("res.users", string="Explained By", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "reconciliation_id",
            "kind",
            "date",
            "reference",
            "amount",
            "counts",
            "age_days",
            "source_key",
            "explanation",
            "explained_by_id",
        }

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError("Reconciling items come from preparing the statement.")
        return super().create(vals_list)

    def unlink(self):
        if not self._fix_guard_open():
            raise UserError("Reconciling items come from preparing the statement.")
        return super().unlink()

    def action_explain(self, explanation=None):
        """The preparer's explanation of an item, while the statement is a draft."""
        require_role(self.env, GROUP_ACCOUNTANT, "Explaining a reconciling item")
        text = (explanation or "").strip()
        if not text:
            raise UserError("State the explanation of the reconciling item.")
        for line in self:
            if line.reconciliation_id.state != "draft":
                raise UserError("%s is not a draft." % line.reconciliation_id.name)
            line._guarded().write({"explanation": text, "explained_by_id": self.env.uid})
        return True
