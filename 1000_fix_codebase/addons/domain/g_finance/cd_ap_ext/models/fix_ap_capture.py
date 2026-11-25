# cd_ap_ext: M52 sub-module capture audit (2026-11-17).
#
# The M52 workspace offered no capture on its Matching, Approval and GRNI
# pages, and several spec records had no model at all:
#
#   * fix.ap.match.tolerance (FR-APE-005 P0): match tolerances by product
#     category and bill value band (quantity %, unit price % and amount).
#     The match was hard-coded to exact quantity and 0.01 on price. A row is
#     approved by an Accounting Administrator other than the requester, then
#     frozen; a change is a new version that supersedes it. No row = the old
#     exact behaviour.
#   * fix.ap.match.exception (FR-APE-007 P0, BRU-APE-03 H): a case for a
#     blocked or unmatched PO bill, with its type, the responsible party, an
#     owner and a due date. It closes only when its cause is fixed (the bill
#     now matches, or was rejected): there is no override of the match.
#   * fix.ap.dispute (FR-APE-017): a dispute on an approved bill. While it is
#     open the bill is held from payment runs and single payment requests.
#     Resolved by someone other than the person who raised it; an upheld
#     dispute names the vendor credit note that settles it.
#   * fix.ap.vendor.statement (FR-APE-016): the vendor's statement balance
#     against our ledger on that date, the difference and its reconciling
#     items, signed off by a second person.
#   * fix.ap.ageing.snapshot (FR-APE-013 P0, BRU-APE-23 H): the payables
#     ageing frozen at a date. Never edited or deleted.
#     A08 M52-F5: the ageing is read AS OF its date. A bill paid, a note
#     netted or a legacy take-on item cleared AFTER the as-of date is still
#     open on that date, at what it still owed then.
#   * fix.ap.grni.accrual (FR-APE-031 P0, BRU-APE-22 H): the received-not-
#     invoiced figure kept for one period end, against the GRNI clearing
#     balance, with the estimated unrecorded liability and its basis,
#     confirmed by a second person. GRNI was only a live report.
#     A08 M52-F1: the confirmation now POSTS the accrual (Dr the lines'
#     expense accounts / Cr the GRNI accrual liability, at the period end,
#     through the AP posting funnel) and its mirror on the first day of the
#     next period, so the vendor bills that arrive supersede it; a confirmed
#     accrual without its posted entry is a close blocker (_fix_close_blockers).
#   * fix.expense.card / fix.expense.card.transaction (FR-APE-038): corporate
#     and fuel cards and their statement lines, each substantiated with a
#     receipt, a category and a cost centre, and approved by finance (never
#     by the cardholder). The "Advances & Cards" page had no card record.
# ruff: noqa: I001
from __future__ import annotations

import re
from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.cd_cash_position.models.treasury_common import require_other_person

from .ap_gl import ap_account, ap_journal, post_ap_move
from .fix_ap_controls import require_finance
from .fix_ap_grni import grni_rows_as_of
from .fix_ap_ext import (
    DEFAULT_TOL_PRICE_ABS,
    DEFAULT_TOL_PRICE_PCT,
    DEFAULT_TOL_QTY_PCT,
    PARAM_TOL_PRICE_ABS,
    PARAM_TOL_PRICE_PCT,
    PARAM_TOL_QTY_PCT,
    PAYABLE_MATCH_STATES,
    _q,
    float_param,
)

LOCK_EXEMPT = {"message_main_attachment_id"}


def _locked_write(records, vals, open_states, what):
    """Refuse a plain write to a record that has left its editable states."""
    trusted = records.env.su or records._fix_guard_has_token()
    if trusted or not set(vals) - LOCK_EXEMPT:
        return
    if any(rec.state not in open_states for rec in records):
        raise UserError("%s is a record of what was decided and cannot be edited." % what)


def _next(env, code, fallback):
    return env["ir.sequence"].sudo().next_by_code(code) or fallback


def _next_period_start(day):
    """The first day of the period FOLLOWING `day`'s month — where a confirmed
    GRNI accrual's mirror entry lands (the recurring engine's auto-reverse
    idiom: fix_gl_engine._next_period_start). Day 28 + 4 always lands in the
    next month, whatever the month's length."""
    return (day.replace(day=28) + timedelta(days=4)).replace(day=1)


# ============================================================ ageing / GRNI
BUCKETS = [
    ("current", "Not Due"),
    ("d1_30", "1-30"),
    ("d31_60", "31-60"),
    ("d61_90", "61-90"),
    ("d90", "90+"),
]


def bucket(days):
    if days <= 0:
        return "current"
    if days <= 30:
        return "d1_30"
    if days <= 60:
        return "d31_60"
    if days <= 90:
        return "d61_90"
    return "d90"


def _entry_date(move):
    """The date a posted entry takes effect on the ledger, or None."""
    return move.date if move and move.state == "posted" and move.date else None


def _in_force_on(paid_on, back_on, as_of):
    """A payment is in force at `as_of` from the day its entry is dated until
    the day the bank's return of it is dated."""
    return bool(paid_on) and paid_on <= as_of and not (back_on and back_on <= as_of)


def _runs_unsettled_at(env, companies, as_of):
    """Payment run lines whose payment had not cleared the payables at `as_of`:
    released to the bank and not yet paid, or paid after that date (A08
    M52-F5). Their bills are paid and their notes netted NOW; on that date
    both were still open."""
    return (
        env["fix.payment.run.line"]
        .sudo()
        .search(
            [
                ("company_id", "in", companies.ids),
                ("state", "in", ("sent", "paid")),
                "|",
                ("move_id", "=", False),
                ("move_id.date", ">", as_of),
            ]
        )
    )


def open_bills_at(env, bills, as_of):
    """[(bill, what it still owed at `as_of`)], only the bills whose payable
    was not cleared on that date (A08 M52-F5).

    A payment counts from the date of the entry that cleared the payable —
    the run's payment entry (the run's payment date), or the clearing entry
    of a Request Payment or an external settlement — and stops counting from
    the date the bank's return of it is posted. An LC remittance that settled
    part of the bill after `as_of` is added back. A bill marked paid that has
    no dated settlement record is left out at every date, as it always was."""
    dated, in_force = set(), set()
    for line in (
        env["fix.payment.run.line"]
        .sudo()
        .search([("bill_ids", "in", bills.ids), ("move_id", "!=", False)])
    ):
        paid_on, back_on = _entry_date(line.move_id), _entry_date(line.reversal_move_id)
        for bill in line.bill_ids & bills:
            dated.add(bill.id)
            if _in_force_on(paid_on, back_on, as_of):
                in_force.add(bill.id)
    later = defaultdict(float)
    # Read as superuser, like the take-on leg above: the ageing is a finance
    # report whose READERSHIP is gated by the surface's own ACL, but a caller
    # without `fix.ap.lc.settlement` rights (the workspace admin is one) made
    # this search raise AccessError and the whole ageing — and the M52
    # payables KPI — returned nothing. The settlement only supplies a DATE and
    # an amount for bills the caller may already read.
    for settlement in (
        env["fix.ap.lc.settlement"]
        .sudo()
        .search([("kind", "=", "bill"), ("bill_id", "in", bills.ids)])
    ):
        dated.add(settlement.bill_id.id)
        if settlement.date > as_of:  # the remittance's date, as its entry is dated
            later[settlement.bill_id.id] += settlement.amount
    out = []
    for bill in bills:
        if bill.payment_move_id:
            dated.add(bill.id)
            if _in_force_on(_entry_date(bill.payment_move_id), None, as_of):
                in_force.add(bill.id)
        if bill.id in in_force:
            continue
        owed = bill.total_payable + later.get(bill.id, 0.0)
        if bill.payment_state == "paid" and (owed <= 0.005 or bill.id not in dated):
            continue
        out.append((bill, owed))
    return out


def open_notes_at(env, notes, as_of):
    """The notes that still count at `as_of` (A08 M52-F5): every one that no
    payment in force on that date has netted. Until the bank has paid the run
    that took a note, the vendor's payable is not reduced by it."""
    netted = env["fix.vendor.note"]
    lines = (
        env["fix.payment.run.line"]
        .sudo()
        .search([("note_ids", "in", notes.ids), ("move_id", "!=", False)])
    )
    for line in lines:
        paid_on, back_on = _entry_date(line.move_id), _entry_date(line.reversal_move_id)
        if _in_force_on(paid_on, back_on, as_of):
            netted |= line.note_ids & notes
    return notes - netted


def ageing_by_vendor(env, companies, as_of):
    """(rows, take-on note) of the payables ageing at `as_of`, read as the
    caller: {label: {"partner_id", bucket: amount...}}. Approved bills net
    of TDS/VDS by days past due, each at what it still owed ON the as-of
    date; notes no payment in force on it has netted are not due; each
    vendor's legacy take-on still open then is its own line (A08 M52-F5)."""
    co = [("company_id", "in", companies.ids)]
    live = [("approval_state", "=", "approved"), ("invoice_date", "<=", as_of)]
    # settled since the as-of date: still open on it (A08 M52-F5)
    lines = _runs_unsettled_at(env, companies, as_of)
    settled_later = (
        lines.bill_ids.ids
        + env["fix.ap.lc.settlement"]
        .sudo()
        .search([("company_id", "in", companies.ids), ("kind", "=", "bill"), ("date", ">", as_of)])
        .mapped("bill_id")
        .ids
    )
    bills = env["fix.vendor.invoice"].search(
        [
            *co,
            *live,
            "|",
            "|",
            ("payment_state", "!=", "paid"),
            ("payment_move_id.date", ">", as_of),
            ("id", "in", settled_later),
        ]
    )
    notes = env["fix.vendor.note"].search(
        [*co, ("state", "in", ("approved", "applied")), ("note_date", "<=", as_of)]
    )
    notes |= lines.note_ids.filtered(lambda n: n.note_date <= as_of)

    def slot():
        return {"partner_id": 0, **dict.fromkeys([k for k, _ in BUCKETS], 0.0)}

    rows = defaultdict(slot)
    for bill, owed in open_bills_at(env, bills, as_of):
        vendor = bill.vendor_id.commercial_partner_id
        row = rows[vendor.display_name]
        row["partner_id"] = vendor.id
        row[bucket((as_of - (bill.due_date or bill.invoice_date)).days)] += owed
    for note in open_notes_at(env, notes, as_of):
        vendor = note.vendor_id.commercial_partner_id
        row = rows[vendor.display_name]
        row["partner_id"] = vendor.id
        row["current"] += note.signed_total
    return rows, _add_payable_takeon(env, companies, rows, as_of)


def takeon_open_at(env, company, account, as_of):
    """{commercial partner id: {"residual", "date"}} of the legacy take-on
    (journal MIG) still open on `account` at `as_of` (A08 M52-F5).

    cd_gl_ext's open_takeon_balances keeps the lines dated by `as_of` but
    reads TODAY'S amount_residual of each: a payment that cleared a take-on
    item after the as-of date had already reduced it. Each line is taken here
    at what was still open ON that date. A reconciliation counts only from
    the date both its sides exist (account.partial.reconcile.max_date, the
    date Odoo's own aged reports go by), so for today's date this is Odoo's
    own residual. `residual` is signed as the GL (+ debit, - credit); `date`
    is the party's earliest take-on date. Lines on an account that
    reconciles nothing carry no residual, as in Odoo. Read as superuser: the
    caller gates who sees it."""
    from odoo.addons.cd_gl_ext.models.fix_ledger_takeon import TAKEON_JOURNAL_CODE

    if not account or not account.reconcile:
        return {}
    lines = (
        env["account.move.line"]
        .sudo()
        .search_read(
            [
                ("company_id", "=", company.id),
                ("account_id", "=", account.id),
                ("parent_state", "=", "posted"),
                ("journal_id.code", "=", TAKEON_JOURNAL_CODE),
                ("date", "<=", as_of),
            ],
            ["partner_id", "debit", "credit", "date"],
        )
    )
    ids = [row["id"] for row in lines]
    # a party is grouped by its commercial partner, as open_takeon_balances
    # groups it; one loaded without its stored commercial partner is its own
    commercial = {
        party.id: (party.commercial_partner_id or party).id
        for party in env["res.partner"]
        .sudo()
        .browse({row["partner_id"][0] for row in lines if row["partner_id"]})
    }
    matched = defaultdict(list)
    if ids:
        Partial = env["account.partial.reconcile"].sudo()
        for part in Partial.search_read(
            ["|", ("debit_move_id", "in", ids), ("credit_move_id", "in", ids)],
            ["debit_move_id", "credit_move_id", "max_date", "amount"],
        ):
            # a match reduces the debit side of it and brings the credit side to zero
            matched[part["debit_move_id"][0]].append((-part["amount"], part["max_date"]))
            matched[part["credit_move_id"][0]].append((part["amount"], part["max_date"]))
    out = {}
    for row in lines:
        residual = (row["debit"] or 0.0) - (row["credit"] or 0.0)
        for amount, on in matched.get(row["id"], ()):
            if on and on <= as_of:
                residual += amount
        slot = out.setdefault(
            commercial.get(row["partner_id"][0], 0) if row["partner_id"] else 0,
            {"residual": 0.0, "date": False},
        )
        slot["residual"] += residual
        if row["date"] and (not slot["date"] or row["date"] < slot["date"]):
            slot["date"] = row["date"]
    return out


def _add_payable_takeon(env, companies, rows, as_of):
    if not env["account.move.line"].has_access("read"):
        return (
            "Opening balances taken on from the legacy system are GL lines, visible to "
            "finance roles only: they are not in this table for your role."
        )
    from odoo.addons.cd_gl_ext.models.fix_ledger_takeon import (
        OPENING_LABEL,
        takeon_control_account,
    )

    Partner = env["res.partner"].sudo()
    configured = False
    for company in companies:
        control = takeon_control_account(env, company, "payable")
        if not control:
            continue
        configured = True
        for partner_id, opening in takeon_open_at(env, company, control, as_of).items():
            owed = -opening["residual"]  # credit-normal: a payable is a credit residual
            if abs(owed) <= 0.005:
                continue
            name = Partner.browse(partner_id).display_name if partner_id else "(no vendor)"
            row = rows["%s · %s" % (name, OPENING_LABEL % opening["date"])]
            row["partner_id"] = partner_id or 0
            row[bucket((as_of - opening["date"]).days)] += owed
    if not configured:
        return (
            "No payable control account is configured for the legacy take-on: legacy "
            "opening balances are not shown."
        )
    return (
        "Opening balances taken on from the legacy system (journal MIG on the payable "
        "control) are each vendor's own line, at what is still open, aged from the take-on "
        "date."
    )


def receipt_dates(env, po_line_ids):
    """Last goods.received event per PO line (the receipt date), from the
    event outbox: metadata only, read as superuser."""
    if not po_line_ids or "fix.event.outbox" not in env:
        return {}
    events = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", "goods.received"),
                ("aggregate", "=", "fix.purchase.order.line"),
                ("aggregate_id", "in", list(po_line_ids)),
            ],
            order="id",
        )
    )
    return {e.aggregate_id: e.create_date.date() for e in events}


def grni_rows(env, as_of, company=None):
    """Goods received not invoiced at `as_of` per received PO line (A06 X26 /
    P13: the one as-at basis the GRNI accrual and the GR/IR report share, at the
    receipt value in BDT; fix_ap_grni.grni_rows_as_of), limited to the caller's
    companies. Import rows (no PO line) are left to the accrual."""
    from .fix_ap_grni import grni_rows_as_of

    allowed = set(env.companies.ids)
    return [
        r
        for r in grni_rows_as_of(env, as_of, company)
        if r["po_line"] and r["po_line"].order_id.company_id.id in allowed
    ]


# ============================================================ tolerances
class FixApMatchTolerance(models.Model):
    """How far a PO bill may exceed its PO price and accepted receipt and
    still match (FR-APE-005)."""

    _name = "fix.ap.match.tolerance"
    _description = "AP Three-Way Match Tolerance"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "company_id, category_id, amount_from desc, effective_from desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    category_id = fields.Many2one(
        "product.category",
        string="Product Category",
        index=True,
        help="Empty: every category. A row for the product's own category (or a parent) "
        "beats the all-categories row.",
    )
    amount_from = fields.Monetary(
        string="Bills From (gross)",
        currency_field="currency_id",
        default=0.0,
        help="The row applies to bills of at least this gross value; the highest band "
        "a bill reaches applies.",
    )
    qty_pct = fields.Float(
        string="Quantity Over Receipt (%)",
        digits=(5, 2),
        help="How much more than the accepted, not yet billed receipt quantity may be "
        "billed. 0 = exact.",
    )
    price_pct = fields.Float(
        string="Unit Price Over PO (%)",
        digits=(5, 2),
        help="How far the billed unit price may exceed the approved PO price, in percent.",
    )
    price_abs = fields.Monetary(
        string="Unit Price Over PO (amount)",
        currency_field="currency_id",
        help="The same as an amount per unit, in BDT. With both set, the larger one applies "
        "(A06 D8: +2 % or +BDT 500, whichever is larger).",
    )
    effective_from = fields.Date(required=True, default=fields.Date.context_today)
    reason = fields.Text(required=True)
    supersedes_id = fields.Many2one(
        "fix.ap.match.tolerance",
        string="Replaces",
        index=True,
        readonly=True,
        copy=False,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("active", "Active"),
            ("superseded", "Superseded"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    requested_at = fields.Datetime(readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    approved_at = fields.Datetime(string="Decided On", readonly=True, copy=False)

    TERMS = (
        "company_id",
        "category_id",
        "amount_from",
        "qty_pct",
        "price_pct",
        "price_abs",
        "effective_from",
        "reason",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "supersedes_id",
            "requested_by_id",
            "requested_at",
            "approved_by_id",
            "approved_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(t.state != "draft" for t in self):
            locked |= set(self.TERMS)
        return locked

    @api.depends("category_id", "amount_from", "qty_pct", "price_pct", "price_abs")
    def _compute_name(self):
        for t in self:
            limits = []
            if t.qty_pct:
                limits.append("quantity +%g%%" % t.qty_pct)
            if t.price_pct:
                limits.append("price +%g%%" % t.price_pct)
            if t.price_abs:
                limits.append("price +%s per unit" % f"{t.price_abs:,.2f}")
            t.name = "%s, bills from %s: %s" % (
                t.category_id.display_name or "All categories",
                f"{t.amount_from or 0.0:,.0f}",
                ", ".join(limits) or "exact match",
            )

    @api.constrains("qty_pct", "price_pct", "price_abs", "amount_from")
    def _check_limits(self):
        for t in self:
            if not (0 <= t.qty_pct <= 100 and 0 <= t.price_pct <= 100):
                raise ValidationError("A tolerance percentage is between 0 and 100.")
            if t.price_abs < 0 or t.amount_from < 0:
                raise ValidationError("A tolerance amount cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        require_finance(self.env, "Proposing a match tolerance")
        return super().create(vals_list)

    def write(self, vals):
        _locked_write(self, vals, ("draft",), "A submitted match tolerance")
        return super().write(vals)

    def unlink(self):
        if any(t.state != "draft" for t in self) and not self.env.su:
            raise UserError("Only a draft tolerance can be deleted; the rest is history.")
        return super().unlink()

    def _same_key(self):
        self.ensure_one()
        return [
            ("id", "!=", self.id),
            ("company_id", "=", self.company_id.id),
            ("category_id", "=", self.category_id.id or False),
            ("amount_from", "=", self.amount_from),
            ("state", "=", "active"),
        ]

    def action_submit(self):
        require_finance(self.env, "Submitting a match tolerance")
        for t in self:
            if t.state != "draft":
                raise UserError("Only a draft tolerance is submitted.")
            current = self.search(t._same_key(), limit=1)
            t._guarded().write(
                {
                    "state": "submitted",
                    "supersedes_id": current.id or False,
                    "requested_by_id": self.env.user.id,
                    "requested_at": fields.Datetime.now(),
                }
            )
        return True

    def action_approve(self):
        require_finance(self.env, "Approving a match tolerance", manager=True)
        for t in self:
            if t.state != "submitted":
                raise UserError("Only a submitted tolerance is approved.")
            require_other_person(
                self.env, t.requested_by_id | t.create_uid, "Approving match tolerance %s" % t.name
            )
            self.search(t._same_key())._guarded().write({"state": "superseded"})
            t._guarded().write(
                {
                    "state": "active",
                    "approved_by_id": self.env.user.id,
                    "approved_at": fields.Datetime.now(),
                }
            )
            t._fix_rematch_open_bills()
        return True

    def action_reject(self):
        require_finance(self.env, "Rejecting a match tolerance", manager=True)
        for t in self:
            if t.state != "submitted":
                raise UserError("Only a submitted tolerance is rejected.")
            require_other_person(
                self.env, t.requested_by_id | t.create_uid, "Rejecting match tolerance %s" % t.name
            )
            t._guarded().write(
                {
                    "state": "rejected",
                    "approved_by_id": self.env.user.id,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def _fix_rematch_open_bills(self):
        """Bills still before approval are matched again under the new rows."""
        Bill = self.env["fix.vendor.invoice"].sudo()
        bills = Bill.search(
            [
                ("company_id", "in", self.company_id.ids),
                ("bill_type", "=", "po"),
                ("approval_state", "in", ("draft", "to_approve")),
            ]
        )
        if bills:
            for name in ("match_state", "match_detail"):
                self.env.add_to_compute(Bill._fields[name], bills)
            bills.flush_recordset(["match_state", "match_detail"])

    @api.model
    def _fix_default_limits(self):
        """A06 D8 (owner decision 20 Nov 2026): no approved row -> price +2 % or
        +BDT 500 a unit (the larger), quantity exact; config parameters."""
        env = self.env
        return (
            max(float_param(env, PARAM_TOL_QTY_PCT, DEFAULT_TOL_QTY_PCT), 0.0),
            max(float_param(env, PARAM_TOL_PRICE_PCT, DEFAULT_TOL_PRICE_PCT), 0.0),
            max(float_param(env, PARAM_TOL_PRICE_ABS, DEFAULT_TOL_PRICE_ABS), 0.0),
            self.browse(),
        )

    @api.model
    def _fix_for(self, invoice, product):
        """(qty %, price %, price amount in BDT, row) for one product on one
        bill. With no approved row the D8 defaults apply."""
        if not invoice.company_id or not invoice.invoice_date:
            return self._fix_default_limits()
        rows = self.sudo().search(
            [
                ("company_id", "=", invoice.company_id.id),
                ("state", "=", "active"),
                ("effective_from", "<=", invoice.invoice_date),
                # A06 P01: the value band is read in BDT
                ("amount_from", "<=", invoice.gross_amount_bdt or 0.0),
            ]
        )
        if not rows:
            return self._fix_default_limits()
        path = product.categ_id.parent_path or ""

        def rank(row):
            if not row.category_id:
                depth = 0
            elif path.startswith(row.category_id.parent_path or "-"):
                depth = len((row.category_id.parent_path or "").split("/"))
            else:
                return None
            return (depth, row.amount_from, row.effective_from, row.id)

        ranked = [(rank(r), r) for r in rows]
        ranked = [x for x in ranked if x[0] is not None]
        if not ranked:
            return self._fix_default_limits()
        best = max(ranked, key=lambda x: x[0])[1]
        return best.qty_pct, best.price_pct, best.price_abs, best


# ============================================================ match exceptions
EXCEPTION_TYPES = [
    ("quantity", "Quantity: billed more than accepted and not yet billed"),
    ("price", "Price above the approved PO price"),
    ("po_price", "PO price not approved"),
    ("not_on_po", "Item not on the purchase order"),
    ("vendor", "Bill vendor is not the PO supplier"),
    ("no_po", "No purchase order linked"),
    ("other", "Other"),
]
RESPONSIBLE = [
    ("buyer", "Buyer (purchase order)"),
    ("receiver", "Receiver (goods receipt / inspection)"),
    ("vendor", "Vendor (bill or credit note)"),
    ("finance", "Finance (bill capture)"),
]
RESOLUTIONS = [
    ("receipt_posted", "Goods receipt posted / inspection completed"),
    ("po_corrected", "Purchase order corrected and re-approved"),
    ("bill_corrected", "Bill corrected"),
    ("credit_note", "Vendor credit note received"),
    ("bill_rejected", "Bill rejected"),
    ("matched", "The bill now matches"),
]
TYPE_PARTY = {
    "quantity": "receiver",
    "price": "buyer",
    "po_price": "buyer",
    "not_on_po": "vendor",
    "vendor": "finance",
    "no_po": "finance",
    "other": "finance",
}


def guess_exception_type(detail):
    text = (detail or "").lower()
    if "no purchase order" in text:
        return "no_po"
    if "is not the supplier" in text:
        return "vendor"
    if "not on the po" in text:
        return "not_on_po"
    if "received" in text and "invoiced" in text:
        return "quantity"
    if "price above po" in text:
        return "price"
    if "po price not approved" in text:
        return "po_price"
    return "other"


class FixApMatchException(models.Model):
    """One blocked PO bill's exception, tracked to its cause being fixed."""

    _name = "fix.ap.match.exception"
    _description = "AP Match Exception Case"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, due_date, id desc"

    _one_open_case_per_bill = models.UniqueIndex(
        "(invoice_id) WHERE state = 'open'",
        "This bill already has an open match exception case.",
    )

    name = fields.Char(readonly=True, copy=False, default="New")
    invoice_id = fields.Many2one(
        "fix.vendor.invoice",
        string="Bill",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("bill_type", "=", "po"), ("match_state", "in", ("unmatched", "blocked"))],
    )
    company_id = fields.Many2one(related="invoice_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="invoice_id.operating_unit_id", store=True, index=True
    )
    vendor_id = fields.Many2one(related="invoice_id.vendor_id", store=True, string="Vendor")
    purchase_order_id = fields.Many2one(
        related="invoice_id.requisition_id", store=True, string="Purchase Order"
    )
    bill_match_state = fields.Selection(related="invoice_id.match_state", string="Bill Match")
    exception_type = fields.Selection(
        EXCEPTION_TYPES, required=True, default="other", tracking=True
    )
    variance_detail = fields.Text(string="Variance (when opened)", readonly=True)
    responsible_party = fields.Selection(
        RESPONSIBLE, required=True, default="finance", tracking=True
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    due_date = fields.Date(
        string="Resolve By",
        required=True,
        default=lambda self: fields.Date.context_today(self) + timedelta(days=7),
    )
    action_note = fields.Text(string="Actions Taken")
    resolution_code = fields.Selection(RESOLUTIONS, string="Resolution", tracking=True)
    resolution_note = fields.Text()
    state = fields.Selection(
        [("open", "Open"), ("resolved", "Resolved")],
        default="open",
        required=True,
        tracking=True,
        index=True,
    )
    opened_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    resolved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    resolved_at = fields.Datetime(readonly=True, copy=False)
    age_days = fields.Integer(string="Age (days)", compute="_compute_age")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "variance_detail",
            "opened_by_id",
            "resolved_by_id",
            "resolved_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"invoice_id"}
            if any(c.state != "open" for c in self):
                locked |= {
                    "exception_type",
                    "responsible_party",
                    "owner_id",
                    "due_date",
                    "action_note",
                    "resolution_code",
                    "resolution_note",
                }
        return locked

    def _compute_age(self):
        today = fields.Date.context_today(self)
        for case in self:
            start = (case.create_date or fields.Datetime.now()).date()
            end = case.resolved_at.date() if case.resolved_at else today
            case.age_days = (end - start).days

    @api.model_create_multi
    def create(self, vals_list):
        require_finance(self.env, "Opening a match exception case")
        Bill = self.env["fix.vendor.invoice"]
        for vals in vals_list:
            bill = Bill.browse(vals.get("invoice_id"))
            if bill.bill_type != "po" or bill.match_state in PAYABLE_MATCH_STATES:
                raise UserError(
                    "Bill %s is not a blocked purchase-order bill: there is no match exception "
                    "to work." % (bill.invoice_ref or "?")
                )
            if "exception_type" not in vals:
                vals["exception_type"] = guess_exception_type(bill.match_detail)
            if "responsible_party" not in vals:
                vals["responsible_party"] = TYPE_PARTY[vals["exception_type"]]
        cases = super().create(vals_list)
        for case in cases:
            case._guarded().write(
                {
                    "name": _next(self.env, "fix.ap.match.exception", "MEX"),
                    "variance_detail": case.invoice_id.match_detail,
                    "opened_by_id": self.env.user.id,
                }
            )
        return cases

    def write(self, vals):
        if (
            "invoice_id" in vals
            and not self.env.su
            and any(c.invoice_id.id != vals["invoice_id"] for c in self)
        ):
            raise UserError("A match exception case stays on the bill it was opened for.")
        _locked_write(self, vals, ("open",), "A resolved match exception case")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("Match exception cases are evidence and cannot be deleted.")
        return super().unlink()

    def _fix_cause_fixed(self):
        self.ensure_one()
        bill = self.invoice_id
        if self.resolution_code == "bill_rejected":
            return bill.approval_state == "rejected"
        return bill.match_state in PAYABLE_MATCH_STATES

    def action_resolve(self):
        """Close the case once its cause is fixed: never an override (BRU-APE-03)."""
        require_finance(self.env, "Resolving a match exception")
        for case in self:
            if case.state != "open":
                raise UserError("Case %s is already resolved." % case.name)
            if not case.resolution_code:
                raise UserError("Choose the resolution before resolving case %s." % case.name)
            if not case._fix_cause_fixed():
                raise UserError(
                    "Bill %s still does not match (%s). A match exception closes when its "
                    "cause is fixed (receipt, PO, bill or credit note) or the bill is "
                    "rejected; the match itself is never overridden (BRU-APE-03)."
                    % (case.invoice_id.invoice_ref, case.invoice_id.match_detail or "")
                )
            case._guarded().write(
                {
                    "state": "resolved",
                    "resolved_by_id": self.env.user.id,
                    "resolved_at": fields.Datetime.now(),
                }
            )
        return True

    @api.model
    def _cron_match_exceptions(self):
        """Daily: open a case for every blocked PO bill that has none, and
        close the cases whose bill now matches or was rejected."""
        Case = self.sudo()
        for case in Case.search([("state", "=", "open")]):
            bill = case.invoice_id
            code = (
                "bill_rejected"
                if bill.approval_state == "rejected"
                else "matched"
                if bill.match_state in PAYABLE_MATCH_STATES
                else None
            )
            if code:
                case._guarded().write(
                    {
                        "resolution_code": code,
                        "resolution_note": case.resolution_note or "Closed by the daily check.",
                        "state": "resolved",
                        "resolved_at": fields.Datetime.now(),
                    }
                )
        bills = (
            self.env["fix.vendor.invoice"]
            .sudo()
            .search(
                [
                    ("bill_type", "=", "po"),
                    ("match_state", "in", ("unmatched", "blocked")),
                    ("approval_state", "!=", "rejected"),
                    ("payment_state", "=", "not_paid"),
                ]
            )
        )
        open_bills = set(Case.search([("state", "=", "open")]).invoice_id.ids)
        for bill in bills.filtered(lambda b: b.id not in open_bills):
            Case.create({"invoice_id": bill.id, "owner_id": bill.create_uid.id or self.env.uid})
        return True


# ============================================================ disputes
DISPUTE_REASONS = [
    ("price", "Price charged"),
    ("quantity", "Quantity billed"),
    ("quality", "Quality / defective goods"),
    ("not_delivered", "Not delivered / service not performed"),
    ("duplicate", "Charged twice"),
    ("terms", "Terms / discount"),
    ("other", "Other"),
]
DISPUTE_OUTCOMES = [
    ("upheld", "Upheld: vendor credit note"),
    ("partly_upheld", "Partly upheld: vendor credit note"),
    ("not_upheld", "Not upheld: the bill is paid in full"),
    ("withdrawn", "Withdrawn"),
]


class FixApDispute(models.Model):
    """A dispute with a vendor about an approved bill (FR-APE-017)."""

    _name = "fix.ap.dispute"
    _description = "AP Vendor Dispute"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, id desc"

    _one_open_dispute_per_bill = models.UniqueIndex(
        "(invoice_id) WHERE state = 'open'",
        "This bill already has an open dispute.",
    )

    name = fields.Char(readonly=True, copy=False, default="New")
    invoice_id = fields.Many2one(
        "fix.vendor.invoice",
        string="Bill",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("approval_state", "=", "approved"), ("payment_state", "=", "not_paid")],
    )
    company_id = fields.Many2one(related="invoice_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="invoice_id.operating_unit_id", store=True, index=True
    )
    vendor_id = fields.Many2one(related="invoice_id.vendor_id", store=True, string="Vendor")
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    bill_payable = fields.Monetary(
        related="invoice_id.total_payable", string="Bill Payable", currency_field="currency_id"
    )
    disputed_amount = fields.Monetary(currency_field="currency_id", required=True, tracking=True)
    reason_code = fields.Selection(DISPUTE_REASONS, string="Reason", required=True, tracking=True)
    description = fields.Text(required=True)
    vendor_ref = fields.Char(string="Vendor's Reference / Acknowledgement")
    owner_id = fields.Many2one(
        "res.users", string="Owner", required=True, default=lambda self: self.env.user
    )
    outcome = fields.Selection(DISPUTE_OUTCOMES, tracking=True)
    note_id = fields.Many2one(
        "fix.vendor.note",
        string="Vendor Credit Note",
        domain="[('invoice_id', '=', invoice_id), ('note_type', '=', 'decrease')]",
    )
    resolution_note = fields.Text()
    state = fields.Selection(
        [("open", "Open: payment held"), ("resolved", "Resolved"), ("withdrawn", "Withdrawn")],
        default="open",
        required=True,
        tracking=True,
        index=True,
    )
    raised_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    raised_at = fields.Datetime(readonly=True, copy=False)
    resolved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    resolved_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "raised_by_id",
            "raised_at",
            "resolved_by_id",
            "resolved_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"invoice_id"}
            if any(d.state != "open" for d in self):
                locked |= {
                    "disputed_amount",
                    "reason_code",
                    "description",
                    "vendor_ref",
                    "owner_id",
                    "outcome",
                    "note_id",
                    "resolution_note",
                }
        return locked

    @api.constrains("disputed_amount", "invoice_id")
    def _check_amount(self):
        for d in self:
            if d.disputed_amount <= 0:
                raise ValidationError("The disputed amount is more than zero.")
            if d.disputed_amount > d.invoice_id.gross_amount + 0.005:
                raise ValidationError(
                    "BDT %.2f is more than bill %s itself (%.2f)."
                    % (d.disputed_amount, d.invoice_id.invoice_ref, d.invoice_id.gross_amount)
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_finance(self.env, "Raising a vendor dispute")
        Bill = self.env["fix.vendor.invoice"]
        for vals in vals_list:
            bill = Bill.browse(vals.get("invoice_id"))
            if bill.approval_state != "approved" or bill.payment_state != "not_paid":
                raise UserError(
                    "A dispute is raised on an approved bill not yet in payment; bill %s is %s "
                    "/ %s." % (bill.invoice_ref or "?", bill.approval_state, bill.payment_state)
                )
            if bill.open_dispute_id:
                raise UserError(
                    "Bill %s already has open dispute %s."
                    % (bill.invoice_ref, bill.open_dispute_id.name)
                )
        disputes = super().create(vals_list)
        for d in disputes:
            d._guarded().write(
                {
                    "name": _next(self.env, "fix.ap.dispute", "APD"),
                    "raised_by_id": self.env.user.id,
                    "raised_at": fields.Datetime.now(),
                }
            )
        return disputes

    def write(self, vals):
        if (
            "invoice_id" in vals
            and not self.env.su
            and any(d.invoice_id.id != vals["invoice_id"] for d in self)
        ):
            raise UserError("A dispute stays on the bill it was raised on.")
        _locked_write(self, vals, ("open",), "A closed dispute")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("Disputes are evidence and cannot be deleted.")
        return super().unlink()

    def action_resolve(self):
        """Someone other than the raiser closes it; an upheld dispute names the
        vendor's credit note, approved, on the same bill."""
        require_finance(self.env, "Resolving a vendor dispute")
        for d in self:
            if d.state != "open":
                raise UserError("Dispute %s is not open." % d.name)
            require_other_person(self.env, d.raised_by_id | d.create_uid, "Resolving %s" % d.name)
            if d.outcome not in ("upheld", "partly_upheld", "not_upheld"):
                raise UserError("Choose the outcome: upheld, partly upheld or not upheld.")
            if not (d.resolution_note or "").strip():
                raise UserError("Write how dispute %s was settled." % d.name)
            if d.outcome in ("upheld", "partly_upheld"):
                note = d.note_id
                if (
                    not note
                    or note.invoice_id != d.invoice_id
                    or note.note_type != "decrease"
                    or note.state not in ("approved", "applied")
                ):
                    raise UserError(
                        "An upheld dispute is settled by the vendor's credit note on bill %s, "
                        "approved: name it first." % d.invoice_id.invoice_ref
                    )
            d._guarded().write(
                {
                    "state": "resolved",
                    "resolved_by_id": self.env.user.id,
                    "resolved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_withdraw(self):
        require_finance(self.env, "Withdrawing a vendor dispute")
        for d in self:
            if d.state != "open":
                raise UserError("Dispute %s is not open." % d.name)
            if not (d.resolution_note or "").strip():
                raise UserError("Write why dispute %s is withdrawn." % d.name)
            d._guarded().write(
                {
                    "state": "withdrawn",
                    "outcome": "withdrawn",
                    "resolved_by_id": self.env.user.id,
                    "resolved_at": fields.Datetime.now(),
                }
            )
        return True


class FixVendorInvoiceCapture(models.Model):
    _inherit = "fix.vendor.invoice"

    match_case_ids = fields.One2many("fix.ap.match.exception", "invoice_id", string="Match Cases")
    open_match_case_id = fields.Many2one(
        "fix.ap.match.exception", string="Exception Case", compute="_compute_open_cases"
    )
    dispute_ids = fields.One2many("fix.ap.dispute", "invoice_id", string="Disputes")
    open_dispute_id = fields.Many2one(
        "fix.ap.dispute", string="Open Dispute", compute="_compute_open_cases"
    )

    @api.depends("match_case_ids.state", "dispute_ids.state")
    def _compute_open_cases(self):
        for bill in self:
            bill.open_match_case_id = bill.match_case_ids.filtered(lambda c: c.state == "open")[:1]
            bill.open_dispute_id = bill.dispute_ids.filtered(lambda d: d.state == "open")[:1]

    def action_open_match_case(self):
        """From Match Exceptions: open the bill's case, owned by the caller."""
        require_finance(self.env, "Opening a match exception case")
        Case = self.env["fix.ap.match.exception"]
        for bill in self:
            if bill.open_match_case_id:
                raise UserError(
                    "Bill %s already has case %s."
                    % (bill.invoice_ref, bill.open_match_case_id.name)
                )
            Case.create({"invoice_id": bill.id})
        return True

    def action_request_payment(self) -> None:
        for bill in self:
            if bill.open_dispute_id:
                raise UserError(
                    "Bill %s is held by dispute %s: it is paid once the dispute is closed."
                    % (bill.invoice_ref, bill.open_dispute_id.name)
                )
        return super().action_request_payment()


class FixPaymentRunCapture(models.Model):
    _inherit = "fix.payment.run"

    def _candidate_bills(self):
        bills = super()._candidate_bills()
        return bills.filtered(lambda b: not b.open_dispute_id)

    def _line_problems(self, lines):
        problems = super()._line_problems(lines)
        for line in lines:
            for bill in line.bill_ids.filtered("open_dispute_id"):
                problems.append(
                    "%s: bill %s is held by dispute %s"
                    % (line.partner_id.name, bill.invoice_ref, bill.open_dispute_id.name)
                )
        return problems


# ============================================================ vendor statements
class FixApVendorStatement(models.Model):
    """A vendor's statement reconciled against the M52 ledger (FR-APE-016)."""

    _name = "fix.ap.vendor.statement"
    _description = "AP Vendor Statement Reconciliation"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "statement_date desc, id desc"

    name = fields.Char(readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    partner_id = fields.Many2one("res.partner", string="Vendor", required=True, index=True)
    statement_date = fields.Date(required=True, default=fields.Date.context_today)
    statement_balance = fields.Monetary(
        string="Balance on the Vendor's Statement",
        currency_field="currency_id",
        required=True,
        help="What the vendor's statement says 1000 FiX owes on the statement date.",
    )
    statement_file = fields.Binary(string="Vendor Statement", attachment=True)
    statement_filename = fields.Char()
    ledger_balance = fields.Monetary(
        string="Our Ledger Balance", currency_field="currency_id", readonly=True
    )
    open_bill_count = fields.Integer(string="Open Bills on Our Ledger", readonly=True)
    difference = fields.Monetary(
        currency_field="currency_id", compute="_compute_difference", store=True
    )
    reconciling_items = fields.Text(
        help="Each item that explains the difference: a bill not yet received, a payment in "
        "transit, a credit note not issued..."
    )
    state = fields.Selection(
        [("draft", "Draft"), ("compared", "Compared"), ("signed", "Signed Off")],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    prepared_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    signed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    signed_at = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "ledger_balance",
            "open_bill_count",
            "prepared_by_id",
            "signed_by_id",
            "signed_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(s.state == "signed" for s in self):
            locked |= {
                "company_id",
                "partner_id",
                "statement_date",
                "statement_balance",
                "statement_file",
                "statement_filename",
                "reconciling_items",
            }
        return locked

    @api.depends("statement_balance", "ledger_balance", "state")
    def _compute_difference(self):
        for s in self:
            s.difference = _q(s.statement_balance - s.ledger_balance) if s.state != "draft" else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        require_finance(self.env, "Reconciling a vendor statement")
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write({"name": _next(self.env, "fix.ap.vendor.statement", "VSR")})
        return recs

    def write(self, vals):
        _locked_write(self, vals, ("draft", "compared"), "A signed-off vendor statement")
        terms = {"partner_id", "statement_date", "company_id"}
        if terms & set(vals) and not self._fix_guard_open():
            # a changed vendor or date makes the comparison stale
            vals = dict(vals)
            res = super().write(vals)
            self.filtered(lambda s: s.state == "compared")._guarded().write({"state": "draft"})
            return res
        return super().write(vals)

    def unlink(self):
        if any(s.state == "signed" for s in self) and not self.env.su:
            raise UserError("A signed-off statement reconciliation is kept.")
        return super().unlink()

    def _fix_ledger(self):
        """(balance, open bills) we owe the vendor on the statement date, each
        bill and note at what it still counted for ON that date (A08 M52-F5:
        a run's payment entry cleared the payable too, not only the Request
        Payment's)."""
        self.ensure_one()
        vendor = self.partner_id.commercial_partner_id
        day = self.statement_date
        bills = self.env["fix.vendor.invoice"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("vendor_id.commercial_partner_id", "=", vendor.id),
                ("approval_state", "=", "approved"),
                ("invoice_date", "<=", day),
            ]
        )
        open_bills = open_bills_at(self.env, bills, day)
        total = sum(owed for _bill, owed in open_bills)
        notes = self.env["fix.vendor.note"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("vendor_id.commercial_partner_id", "=", vendor.id),
                ("state", "in", ("approved", "applied")),
                ("note_date", "<=", day),
            ]
        )
        total += sum(open_notes_at(self.env, notes, day).mapped("signed_total"))
        rows, _note = ageing_by_vendor(self.env, self.company_id, day)
        for label, row in rows.items():
            if row["partner_id"] == vendor.id and "·" in label:
                total += sum(row[k] for k, _ in BUCKETS)
        return _q(total), len(open_bills)

    def action_compare(self):
        require_finance(self.env, "Comparing a vendor statement")
        for s in self:
            if s.state == "signed":
                raise UserError("Statement %s is signed off." % s.name)
            balance, count = s._fix_ledger()
            s._guarded().write(
                {
                    "ledger_balance": balance,
                    "open_bill_count": count,
                    "state": "compared",
                    "prepared_by_id": self.env.user.id,
                }
            )
        return True

    def action_sign_off(self):
        require_finance(self.env, "Signing off a vendor statement")
        for s in self:
            if s.state != "compared":
                raise UserError("Compare statement %s with the ledger first." % s.name)
            require_other_person(
                self.env, s.prepared_by_id | s.create_uid, "Signing off %s" % s.name
            )
            balance, _count = s._fix_ledger()
            if abs(balance - s.ledger_balance) > 0.005:
                raise UserError(
                    "Our ledger for %s moved since it was compared (%.2f, now %.2f): compare "
                    "again." % (s.partner_id.display_name, s.ledger_balance, balance)
                )
            if abs(s.difference) > 0.005 and not (s.reconciling_items or "").strip():
                raise UserError(
                    "Statement %s differs by %.2f: list the reconciling items before signing "
                    "off." % (s.name, s.difference)
                )
            s._guarded().write(
                {
                    "state": "signed",
                    "signed_by_id": self.env.user.id,
                    "signed_at": fields.Datetime.now(),
                }
            )
        return True


# ============================================================ ageing snapshot
class FixApAgeingSnapshot(models.Model):
    """The payables ageing frozen at a date (BRU-APE-23)."""

    _name = "fix.ap.ageing.snapshot"
    _description = "AP Ageing Snapshot"
    _inherit = ["fix.guarded.mixin"]
    _order = "as_of desc, id desc"

    _one_per_date = models.Constraint(
        "UNIQUE(company_id, as_of)", "The payables ageing at this date is already kept."
    )

    name = fields.Char(readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    as_of = fields.Date(string="As Of", required=True, default=fields.Date.context_today)
    note = fields.Char(string="Purpose", help="E.g. the month-end close it belongs to.")
    taken_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    taken_at = fields.Datetime(readonly=True, copy=False)
    current = fields.Monetary(string="Not Due", currency_field="currency_id", readonly=True)
    d1_30 = fields.Monetary(string="1-30", currency_field="currency_id", readonly=True)
    d31_60 = fields.Monetary(string="31-60", currency_field="currency_id", readonly=True)
    d61_90 = fields.Monetary(string="61-90", currency_field="currency_id", readonly=True)
    d90 = fields.Monetary(string="90+", currency_field="currency_id", readonly=True)
    total = fields.Monetary(string="Total Open", currency_field="currency_id", readonly=True)
    vendor_count = fields.Integer(string="Vendors", readonly=True)
    basis = fields.Char(string="Opening Balances", readonly=True)
    line_ids = fields.One2many("fix.ap.ageing.snapshot.line", "snapshot_id", string="Vendor Lines")

    STAMPS = (
        "name",
        "taken_by_id",
        "taken_at",
        "current",
        "d1_30",
        "d31_60",
        "d61_90",
        "d90",
        "total",
        "vendor_count",
        "basis",
        "line_ids",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self.STAMPS)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"company_id", "as_of", "note"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_finance(self.env, "Taking a payables ageing snapshot")
        today = fields.Date.context_today(self)
        for vals in vals_list:
            as_of = fields.Date.to_date(vals.get("as_of")) or today
            if as_of > today:
                raise UserError("A snapshot is taken of a date that has come.")
            company_id = vals.get("company_id") or self.env.company.id
            if self.search_count([("company_id", "=", company_id), ("as_of", "=", as_of)]):
                raise UserError("The payables ageing at %s is already kept." % as_of)
        snaps = super().create(vals_list)
        for snap in snaps:
            snap._fix_take()
        return snaps

    def _fix_take(self):
        self.ensure_one()
        rows, basis = ageing_by_vendor(self.env, self.company_id, self.as_of)
        keys = [k for k, _ in BUCKETS]
        lines, totals = [], dict.fromkeys(keys, 0.0)
        for label in sorted(rows):
            row = rows[label]
            vals = {k: _q(row[k]) for k in keys}
            if not any(vals.values()):
                continue
            for k in keys:
                totals[k] += vals[k]
            lines.append(
                (
                    0,
                    0,
                    {
                        "label": label,
                        "partner_id": row["partner_id"] or False,
                        **vals,
                        "total": _q(sum(vals.values())),
                    },
                )
            )
        self._guarded().write(
            {
                "name": "AGS/%s/%s" % (self.as_of, self.company_id.id),
                "taken_by_id": self.env.user.id,
                "taken_at": fields.Datetime.now(),
                **{k: _q(v) for k, v in totals.items()},
                "total": _q(sum(totals.values())),
                "vendor_count": len(lines),
                "basis": basis[:250],
                "line_ids": lines,
            }
        )

    def write(self, vals):
        if not self._fix_guard_open() and set(vals) - LOCK_EXEMPT:
            raise UserError("A payables ageing snapshot is kept exactly as it was taken.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A payables ageing snapshot is never deleted (BRU-APE-23).")
        return super().unlink()


class FixApAgeingSnapshotLine(models.Model):
    _name = "fix.ap.ageing.snapshot.line"
    _description = "AP Ageing Snapshot Line"
    _order = "snapshot_id, label"

    snapshot_id = fields.Many2one(
        "fix.ap.ageing.snapshot", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="snapshot_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="snapshot_id.currency_id")
    as_of = fields.Date(related="snapshot_id.as_of", store=True)
    label = fields.Char(string="Vendor", required=True)
    partner_id = fields.Many2one("res.partner", string="Vendor Record", index=True)
    current = fields.Monetary(string="Not Due", currency_field="currency_id")
    d1_30 = fields.Monetary(string="1-30", currency_field="currency_id")
    d31_60 = fields.Monetary(string="31-60", currency_field="currency_id")
    d61_90 = fields.Monetary(string="61-90", currency_field="currency_id")
    d90 = fields.Monetary(string="90+", currency_field="currency_id")
    total = fields.Monetary(string="Total Open", currency_field="currency_id")

    @api.model_create_multi
    def create(self, vals_list):
        if not (self.env.su or self.env.context.get("fix_guarded_transition")):
            raise UserError("Snapshot lines are written when the snapshot is taken.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise UserError("A payables ageing snapshot is kept exactly as it was taken.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A payables ageing snapshot is never deleted (BRU-APE-23).")
        return super().unlink()


# ============================================================ GRNI accrual
class FixApGrniAccrual(models.Model):
    """The received-not-invoiced figure kept for one period end (BRU-APE-22)."""

    _name = "fix.ap.grni.accrual"
    _description = "AP GRNI & Unrecorded Liability Accrual"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "period_end desc, id desc"

    _one_confirmed_per_period = models.UniqueIndex(
        "(company_id, period_end) WHERE state = 'confirmed'",
        "The accrual for this period end is already confirmed.",
    )

    name = fields.Char(readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    period_end = fields.Date(required=True)
    line_ids = fields.One2many(
        "fix.ap.grni.accrual.line", "accrual_id", string="Receipts Not Billed"
    )
    line_count = fields.Integer(readonly=True)
    grni_total = fields.Monetary(
        string="Received Not Invoiced", currency_field="currency_id", readonly=True
    )
    clearing_balance = fields.Monetary(
        string="GRNI Clearing Account Balance", currency_field="currency_id", readonly=True
    )
    clearing_note = fields.Char(string="Clearing Account", readonly=True)
    unrecorded_estimate = fields.Monetary(
        string="Estimated Unrecorded Liability",
        currency_field="currency_id",
        help="Services and costs received with no bill and no purchase order (utilities, "
        "rent, couriers...), estimated for the period.",
    )
    unrecorded_basis = fields.Text(string="Basis of the Estimate")
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("confirmed", "Confirmed")],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    computed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    computed_at = fields.Datetime(readonly=True, copy=False)
    confirmed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    confirmed_at = fields.Datetime(readonly=True, copy=False)
    # A08 M52-F1 (FR-APE-031 P0 / BRU-APE-22 H): confirmation posts the money.
    move_id = fields.Many2one(
        "account.move",
        string="Accrual Entry",
        readonly=True,
        copy=False,
        help="The period-end entry posted when the accrual was confirmed: Dr the "
        "received-not-invoiced lines' expense accounts and the unrecorded "
        "estimate, Cr the GRNI accrual liability, at the period end.",
    )
    reversal_move_id = fields.Many2one(
        "account.move",
        string="Reversal Entry",
        readonly=True,
        copy=False,
        help="The mirror of the accrual entry, posted on the first day of the next "
        "period so the vendor bills that arrive supersede the accrual.",
    )

    STAMPS = (
        "name",
        "state",
        "line_ids",
        "line_count",
        "grni_total",
        "clearing_balance",
        "clearing_note",
        "computed_by_id",
        "computed_at",
        "confirmed_by_id",
        "confirmed_at",
        "move_id",
        "reversal_move_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | set(self.STAMPS)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(a.state == "confirmed" for a in self):
            locked |= {"company_id", "period_end", "unrecorded_estimate", "unrecorded_basis"}
        return locked

    @api.constrains("unrecorded_estimate")
    def _check_estimate(self):
        for a in self:
            if a.unrecorded_estimate < 0:
                raise ValidationError("The unrecorded liability estimate cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        require_finance(self.env, "Preparing a GRNI accrual")
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write({"name": _next(self.env, "fix.ap.grni.accrual", "GRNI")})
        return recs

    def write(self, vals):
        _locked_write(self, vals, ("draft", "computed"), "A confirmed GRNI accrual")
        if {"period_end", "company_id"} & set(vals) and not self._fix_guard_open():
            res = super().write(vals)
            self.filtered(lambda a: a.state == "computed")._guarded().write({"state": "draft"})
            return res
        return super().write(vals)

    def unlink(self):
        if any(a.state == "confirmed" for a in self) and not self.env.su:
            raise UserError("A confirmed GRNI accrual is kept.")
        return super().unlink()

    def _fix_clearing(self):
        self.ensure_one()
        try:
            account = ap_account(self.env, self.company_id, "grni")
        except UserError:
            return 0.0, "No GRNI clearing account is configured"
        aml = self.env["account.move.line"].sudo()
        groups = aml._read_group(
            [
                ("company_id", "=", self.company_id.id),
                ("account_id", "=", account.id),
                ("parent_state", "=", "posted"),
                ("date", "<=", self.period_end),
            ],
            [],
            ["balance:sum"],
        )
        balance = groups[0][0] if groups else 0.0
        # a credit-normal liability: what the clearing account holds as owed
        return _q(-(balance or 0.0)), "%s %s" % (account.code, account.name)

    def action_compute(self):
        require_finance(self.env, "Computing a GRNI accrual")
        for a in self:
            if a.state == "confirmed":
                raise UserError("%s is confirmed." % a.name)
            # A06 X26: one as-at basis, PO receipts and imports without a PO
            rows = grni_rows_as_of(self.env, a.period_end, a.company_id)
            clearing, label = a._fix_clearing()
            lines = [(5, 0, 0)]
            for r in rows:
                pol = r["po_line"]
                lines.append(
                    (
                        0,
                        0,
                        {
                            "po_line_id": pol.id if pol else False,
                            "order_ref": r["order_ref"],
                            "vendor_id": r["vendor"].id or False,
                            "product_id": r["product"].id or False,
                            "received": r["received"],
                            "invoiced": r["invoiced"],
                            "open_qty": r["open_qty"],
                            "unit_price": r["unit_price"],
                            "accrual": _q(r["accrual"]),
                            "received_on": r["received_on"] or False,
                        },
                    )
                )
            a._guarded().write(
                {
                    "line_ids": lines,
                    "line_count": len(rows),
                    "grni_total": _q(sum(r["accrual"] for r in rows)),
                    "clearing_balance": clearing,
                    "clearing_note": label,
                    "state": "computed",
                    "computed_by_id": self.env.user.id,
                    "computed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_confirm(self):
        """The second person's confirm is also the posting moment (A08 M52-F1,
        FR-APE-031 P0 / BRU-APE-22 H): the accrual becomes a GL fact — Dr the
        received-not-invoiced lines' expense accounts and the unrecorded
        estimate, Cr the GRNI accrual liability, dated the period end — and its
        mirror lands on the first day of the next period, so the vendor bills
        that arrive supersede it. A zero accrual confirms with no entry."""
        require_finance(self.env, "Confirming a GRNI accrual", manager=True)
        for a in self:
            if a.state != "computed":
                raise UserError("Compute %s before confirming it." % a.name)
            require_other_person(
                self.env, a.computed_by_id | a.create_uid, "Confirming %s" % a.name
            )
            if a.period_end > fields.Date.context_today(self):
                raise UserError("A period end is confirmed once it has come.")
            if a.unrecorded_estimate and not (a.unrecorded_basis or "").strip():
                raise UserError("Give the basis of the unrecorded liability estimate.")
            legs = a._fix_accrual_legs()
            move = reversal = self.env["account.move"]
            if legs:
                move, reversal = a._fix_post_accrual(legs)
            a._guarded().write(
                {
                    "state": "confirmed",
                    "confirmed_by_id": self.env.user.id,
                    "confirmed_at": fields.Datetime.now(),
                    "move_id": move.id or False,
                    "reversal_move_id": reversal.id or False,
                }
            )
            if move:
                a.message_post(
                    body="Confirmed and posted %s (%.2f) at %s; %s reverses it on %s "
                    "(BRU-APE-22 H)."
                    % (
                        move.name,
                        move.amount_total,
                        a.period_end,
                        reversal.name,
                        reversal.date,
                    )
                )
        return True

    def _fix_accrual_legs(self):
        """The debit side of the accrual entry: one leg per computed line at
        its product's expense account (the convention of the P05 service-entry
        and non-stock-goods receipts: the product's account, the module's
        expense role as the fallback), plus one for the unrecorded liability
        estimate at the expense role. [(account, label, amount, partner,
        operating_unit, branch)] — never a guessed account: an unconfigured
        role fails closed before anything posts."""
        self.ensure_one()
        company = self.company_id
        legs = []
        for ln in self.line_ids.sorted("id"):
            amount = _q(ln.accrual)
            if amount <= 0.005:
                continue
            product = ln.product_id
            expense = (
                product.product_tmpl_id.with_company(company)._get_product_accounts().get("expense")
                if product
                else None
            ) or ap_account(self.env, company, "expense")
            order = ln.po_line_id.sudo().order_id
            ou = order.operating_unit_id
            branch = order.branch_id
            if branch and branch.operating_unit_id != ou:
                branch = False  # fix.journal.dimension refuses a branch of another OU
            legs.append(
                (
                    expense,
                    "GRNI accrual %s %s" % (self.name, ln.order_ref or product.display_name),
                    amount,
                    ln.vendor_id.commercial_partner_id,
                    ou,
                    branch,
                )
            )
        if _q(self.unrecorded_estimate) > 0.005:
            legs.append(
                (
                    ap_account(self.env, company, "expense"),
                    "Unrecorded liability estimate %s" % self.name,
                    _q(self.unrecorded_estimate),
                    self.env["res.partner"],  # no vendor: the estimate is ours
                    None,
                    None,
                )
            )
        return legs

    def _fix_post_accrual(self, legs):
        """Post the accrual entry at the period end and its mirror on the first
        day of the next period, through the AP posting funnel (post_ap_move ->
        M19 post_with_dimensions): the AP default cost-centre and business-line
        dimensions, each line's own operating unit / branch where its PO carries
        them, and a fix.journal.posting.log row per entry (source
        ap_subledger). Returns (move, reversal)."""
        self.ensure_one()
        env, company = self.env, self.company_id
        journal = ap_journal(env, company, "purchase")
        accrual_account = ap_account(env, company, "grni_accrual")
        ref = "GRNI accrual %s" % self.name
        lines, dims = [], {}
        for account, label, amount, partner, ou, branch in legs:
            i = len(lines)  # the debit leg's index; its credit mirror follows it
            lines.append((account, label, amount, 0.0, partner))
            lines.append((accrual_account, label, 0.0, amount, partner))
            override = {}
            if ou:
                override["operating_unit_id"] = ou.id
            if branch:
                override["branch_id"] = branch.id
            if override:
                dims[i] = dict(override)  # the debit leg and its credit mirror
                dims[i + 1] = dict(override)  # keep the line's own dimensions
        move = post_ap_move(env, company, journal, self.period_end, ref, lines, None, dims)
        reversal = post_ap_move(
            env,
            company,
            journal,
            _next_period_start(self.period_end),
            "Reversal of " + ref,
            [
                (account, "Reversal — %s" % label, credit, debit, partner)
                for account, label, debit, credit, partner in lines
            ],
            None,
            dims,
        )
        return move, reversal

    # A08 M52-F1: the close seam. cd_gl_ext's fix.period.close.action_close
    # (next to its own _fix_check_* refusals) calls _fix_close_blockers and
    # refuses the close while it returns anything; cd_ap_ext does not edit the
    # M19 model, so the query lives here for the close owner to wire.
    @api.model
    def _fix_close_blockers(self, company, period_end):
        """Confirmed GRNI accruals of `company` dated up to the closing
        `period_end` whose GL legs are not both posted (BRU-APE-22 H: the
        period cannot close without them). Confirmation posts the legs, so this
        should be structurally empty — the guard stands for the record a
        guarded write or a restore could leave behind."""
        return (
            self.sudo()
            .search(
                [
                    ("company_id", "=", company.id if company else False),
                    ("state", "=", "confirmed"),
                    ("period_end", "<=", period_end),
                ]
            )
            .filtered(lambda a: a._fix_close_blocked())
        )

    def _fix_close_blocked(self):
        """True when this confirmed accrual owes GL legs it does not have
        posted. A period with nothing received-not-invoiced and no estimate
        confirms without an entry and blocks nothing."""
        self.ensure_one()
        if _q(self.grni_total + self.unrecorded_estimate) <= 0.005:
            return False
        return not (
            self.move_id
            and self.move_id.state == "posted"
            and self.reversal_move_id
            and self.reversal_move_id.state == "posted"
        )


class FixApGrniAccrualLine(models.Model):
    _name = "fix.ap.grni.accrual.line"
    _description = "AP GRNI Accrual Line"
    _order = "accrual_id, id"

    accrual_id = fields.Many2one(
        "fix.ap.grni.accrual", string="GRNI Accrual", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="accrual_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="accrual_id.currency_id")
    po_line_id = fields.Many2one("fix.purchase.order.line", string="PO Line", ondelete="set null")
    order_ref = fields.Char(string="PO")
    vendor_id = fields.Many2one("res.partner", string="Vendor")
    product_id = fields.Many2one("product.product", string="Product")
    received = fields.Float()
    invoiced = fields.Float()
    open_qty = fields.Float(string="Not Invoiced")
    unit_price = fields.Monetary(
        string="Receipt Value (BDT)",
        currency_field="currency_id",
        help="A06 X26: the unit value at which the receipt entered GRNI.",
    )
    accrual = fields.Monetary(currency_field="currency_id")
    received_on = fields.Date(string="Last Receipt")

    @api.model_create_multi
    def create(self, vals_list):
        if not (self.env.su or self.env.context.get("fix_guarded_transition")):
            raise UserError("GRNI lines are computed, not typed.")
        return super().create(vals_list)

    def write(self, vals):
        if not (self.env.su or self.env.context.get("fix_guarded_transition")):
            raise UserError("GRNI lines are computed, not typed.")
        return super().write(vals)

    def unlink(self):
        if not (self.env.su or self.env.context.get("fix_guarded_transition")):
            raise UserError("GRNI lines are computed, not typed.")
        return super().unlink()


# ============================================================ cards
CARD_TYPES = [("corporate", "Corporate card"), ("fuel", "Fuel card")]


class FixExpenseCard(models.Model):
    """A corporate or fuel card held by an employee (FR-APE-038)."""

    _name = "fix.expense.card"
    _description = "Corporate / Fuel Card"
    _inherit = ["mail.thread"]
    _order = "holder_id, id"

    _one_card_number = models.Constraint(
        "UNIQUE(company_id, issuer, last_digits, card_type)",
        "This card is already registered.",
    )

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", index=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    card_type = fields.Selection(CARD_TYPES, required=True, default="fuel", tracking=True)
    issuer = fields.Char(string="Issuer (bank / fuel company)", required=True)
    last_digits = fields.Char(string="Last 4 Digits", required=True)
    holder_id = fields.Many2one(
        "hr.employee", string="Cardholder", required=True, index=True, tracking=True
    )
    monthly_limit = fields.Monetary(currency_field="currency_id")
    valid_to = fields.Date(string="Expires")
    active = fields.Boolean(default=True, tracking=True)
    transaction_ids = fields.One2many("fix.expense.card.transaction", "card_id")
    unexplained_count = fields.Integer(compute="_compute_unexplained", string="Unexplained Lines")

    @api.depends("card_type", "issuer", "last_digits", "holder_id")
    def _compute_name(self):
        labels = dict(CARD_TYPES)
        for c in self:
            c.name = "%s %s ••%s · %s" % (
                labels.get(c.card_type, ""),
                c.issuer or "",
                c.last_digits or "",
                c.holder_id.name or "?",
            )

    @api.depends("transaction_ids.state")
    def _compute_unexplained(self):
        for c in self:
            c.unexplained_count = len(
                c.transaction_ids.filtered(lambda t: t.state == "unexplained")
            )

    @api.constrains("last_digits")
    def _check_digits(self):
        for c in self:
            if not re.fullmatch(r"\d{4}", c.last_digits or ""):
                raise ValidationError("Give the last four digits of the card only.")

    @api.model_create_multi
    def create(self, vals_list):
        require_finance(self.env, "Registering a card")
        return super().create(vals_list)

    def write(self, vals):
        require_finance(self.env, "Changing a card")
        return super().write(vals)

    def unlink(self):
        if self.transaction_ids and not self.env.su:
            raise UserError("A card with statement lines is archived, not deleted.")
        return super().unlink()


class FixExpenseCardTransaction(models.Model):
    """One card statement line, explained by its holder and approved by
    finance. Spend is coded directly (category and cost centre) with its
    receipt; it is never also claimed, so it is never reimbursed twice."""

    _name = "fix.expense.card.transaction"
    _description = "Card Statement Line"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "txn_date desc, id desc"

    _one_line_per_statement_ref = models.Constraint(
        "UNIQUE(card_id, statement_ref)", "This statement line is already recorded for the card."
    )

    name = fields.Char(compute="_compute_name", store=True)
    card_id = fields.Many2one(
        "fix.expense.card", string="Card", required=True, index=True, ondelete="restrict"
    )
    company_id = fields.Many2one(related="card_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="card_id.operating_unit_id", store=True, index=True)
    holder_id = fields.Many2one(related="card_id.holder_id", store=True, string="Cardholder")
    currency_id = fields.Many2one(related="card_id.currency_id")
    txn_date = fields.Date(string="Transaction Date", required=True)
    merchant = fields.Char(required=True)
    amount = fields.Monetary(currency_field="currency_id", required=True)
    statement_ref = fields.Char(string="Statement Reference", required=True)
    category_id = fields.Many2one("fix.expense.category", string="Expense Category")
    cost_centre = fields.Char(string="Cost Centre / Job")
    purpose = fields.Char()
    receipt_file = fields.Binary(string="Receipt", attachment=True)
    receipt_filename = fields.Char()
    state = fields.Selection(
        [
            ("unexplained", "Unexplained"),
            ("explained", "Explained"),
            ("approved", "Approved"),
            ("disputed", "Disputed with Issuer"),
        ],
        default="unexplained",
        required=True,
        tracking=True,
        index=True,
    )
    explained_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)

    TERMS = ("card_id", "txn_date", "merchant", "amount", "statement_ref")
    CODING = ("category_id", "cost_centre", "purpose", "receipt_file", "receipt_filename")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "explained_by_id",
            "approved_by_id",
            "approved_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= set(self.TERMS)
            if any(t.state in ("approved",) for t in self):
                locked |= set(self.CODING)
        return locked

    @api.depends("card_id", "txn_date", "merchant", "amount")
    def _compute_name(self):
        for t in self:
            t.name = "%s · %s · %s" % (
                t.card_id.last_digits or "?",
                t.txn_date or "",
                t.merchant or "",
            )

    @api.constrains("amount")
    def _check_amount(self):
        for t in self:
            if not t.amount:
                raise ValidationError("A statement line has an amount.")

    @api.model_create_multi
    def create(self, vals_list):
        require_finance(self.env, "Recording card statement lines")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            if set(self.TERMS) & set(vals) and any(
                t[name]
                != t._fields[name].convert_to_record(
                    t._fields[name].convert_to_cache(vals[name], t), t
                )
                for t in self
                for name in set(self.TERMS) & set(vals)
            ):
                raise UserError("A statement line is recorded as the issuer printed it.")
            if set(self.CODING) & set(vals) and any(t.state == "approved" for t in self):
                raise UserError("An approved card line is kept as approved.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("Card statement lines are evidence and cannot be deleted.")
        return super().unlink()

    def action_explain(self):
        """The holder (or finance) codes the spend and attaches the receipt."""
        for t in self:
            if t.state not in ("unexplained", "explained"):
                raise UserError("Line %s is %s." % (t.name, t.state))
            if not (t.category_id and (t.cost_centre or "").strip() and t.receipt_file):
                raise UserError(
                    "Explain line %s with its expense category, cost centre or job, and the "
                    "receipt." % t.name
                )
            t._guarded().write({"state": "explained", "explained_by_id": self.env.user.id})
        return True

    def action_approve(self):
        require_finance(self.env, "Approving card spend")
        for t in self:
            if t.state != "explained":
                raise UserError("Line %s is not explained yet." % t.name)
            holder_user = t.holder_id.user_id
            require_other_person(
                self.env, holder_user | t.explained_by_id, "Approving card line %s" % t.name
            )
            t._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_dispute(self):
        require_finance(self.env, "Disputing a card line")
        for t in self:
            if t.state == "approved":
                raise UserError("An approved line is not disputed.")
            t._guarded().write({"state": "disputed"})
        return True

    def action_reopen(self):
        require_finance(self.env, "Reopening a card line")
        for t in self:
            if t.state not in ("explained", "disputed"):
                raise UserError("Only an explained or disputed line is reopened.")
            t._guarded().write({"state": "unexplained", "explained_by_id": False})
        return True
