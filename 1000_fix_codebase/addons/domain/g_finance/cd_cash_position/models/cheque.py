# cd_cash_position — Cheque Management (A08 · M50).
#
# The cheque register: received cheques (customer payments, incl. post-dated
# cheques held until their date) and issued cheques (treasury payments by
# cheque, numbered from the paying account's cheque book). Clearing is
# confirmed by an imported bank statement line; a bounce is recorded with
# the bank's reason and published (cheque.bounced).
#
# A08 workflow audit (M50-8, M50-13):
#   * a bounce AFTER clearing unwinds the money: an issued cheque's payment
#     is reversed and re-opened (failed, re-queueable); a received cheque's
#     bank debit is booked against the returned-cheques receivable of the
#     drawer, so the customer owes it again;
#   * state / clearing / bounce stamps are guarded;
#   * the register is unique per company, direction, drawee and number with
#     an EMPTY drawee counted as one value (the NULL loophole), and issued
#     cheques come from a numbered cheque book (BRU-TRE-17).
from __future__ import annotations

from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .treasury_common import (
    GROUP_ADMIN,
    bank_account_of,
    post_treasury_move,
    require_role,
    treasury_account,
    treasury_alert,
)


def _norm(text):
    return " ".join((text or "").split()).upper()


class FixChequeBook(models.Model):
    """A numbered cheque book of one of our bank accounts. Issued cheques
    take its leaves in order, so no number is ever unaccounted for."""

    _name = "fix.cheque.book"
    _description = "Cheque Book"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "journal_id, first_number"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    journal_id = fields.Many2one(
        "account.journal",
        string="Bank Account",
        required=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
    )
    first_number = fields.Integer(required=True)
    last_number = fields.Integer(required=True)
    number_width = fields.Integer(default=6, help="Leaves are zero-padded to this width")
    next_number = fields.Integer(readonly=True, copy=False)
    state = fields.Selection(
        [("active", "In Use"), ("exhausted", "Exhausted"), ("closed", "Closed")],
        default="active",
        required=True,
        tracking=True,
    )

    _LEAF_TERMS = ("first_number", "last_number", "number_width", "journal_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"next_number", "state"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= set(self._LEAF_TERMS)
        return locked

    @api.constrains("first_number", "last_number", "journal_id")
    def _check_range(self):
        for book in self:
            if book.first_number <= 0 or book.last_number < book.first_number:
                raise ValidationError("A cheque book runs from a positive first leaf to its last.")
            clash = self.sudo().search(
                [
                    ("id", "!=", book.id),
                    ("journal_id", "=", book.journal_id.id),
                    ("first_number", "<=", book.last_number),
                    ("last_number", ">=", book.first_number),
                ],
                limit=1,
            )
            if clash:
                raise ValidationError(
                    "Leaves %s-%s overlap cheque book %s of the same account."
                    % (book.first_number, book.last_number, clash.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, GROUP_ADMIN, "Registering a cheque book")
        books = super().create(vals_list)
        for book in books:
            book._guarded().write({"next_number": book.first_number})
        return books

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            for book in self:
                changed = [
                    f
                    for f in set(self._LEAF_TERMS) & set(vals)
                    if book._fix_guard_differs(f, vals[f], book[f])
                ]
                if changed:
                    raise UserError("A registered cheque book's leaves cannot be renumbered.")
        return super().write(vals)

    @api.model
    def _fix_active_book(self, journal):
        book = self.search(
            [("journal_id", "=", journal.id), ("state", "=", "active")],
            order="first_number",
            limit=1,
        )
        if not book:
            raise UserError(
                "No cheque book in use for %s: register the cheque book before issuing a "
                "cheque (BRU-TRE-17)." % journal.display_name
            )
        return book

    def _fix_take_leaf(self) -> str:
        """The next leaf, in order; the book is exhausted after its last."""
        self.ensure_one()
        self.flush_recordset(["next_number"])
        self.env.cr.execute(
            "SELECT next_number FROM fix_cheque_book WHERE id = %s FOR UPDATE", (self.id,)
        )
        number = self.env.cr.fetchone()[0] or self.first_number
        if number > self.last_number:
            self._guarded().write({"state": "exhausted"})
            raise UserError("Cheque book %s is exhausted." % self.name)
        nxt = number + 1
        self._guarded().write(
            {"next_number": nxt, "state": "exhausted" if nxt > self.last_number else "active"}
        )
        return str(number).zfill(self.number_width or 0)

    def action_close(self):
        require_role(self.env, GROUP_ADMIN, "Closing a cheque book")
        self._guarded().write({"state": "closed"})
        return True


class FixCheque(models.Model):
    _name = "fix.cheque"
    _description = "Cheque"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "cheque_date desc, id desc"
    _cheque_unique = models.Constraint(
        "UNIQUE (company_id, direction, drawee_bank, cheque_no)",
        "This cheque is already in the register.",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    direction = fields.Selection(
        [("received", "Received"), ("issued", "Issued")], required=True, default="received"
    )
    cheque_no = fields.Char(string="Cheque No", required=True, index=True, tracking=True)
    drawee_bank = fields.Char(string="Drawn On (Bank / Branch)")
    cheque_book_id = fields.Many2one("fix.cheque.book", string="Cheque Book", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Party", index=True)
    payee_name = fields.Char(string="Payee / Drawer Name")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    cheque_date = fields.Date(string="Cheque Date", required=True, index=True)
    received_date = fields.Date(
        string="Received / Issued On", default=fields.Date.context_today, required=True
    )
    is_pdc = fields.Boolean(
        string="Post-Dated", compute="_compute_pdc", store=True, help="Dated after it was received"
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Our Bank Account",
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
        help="Received: the account deposited into. Issued: the account drawn on.",
    )
    source_ref = fields.Char(
        string="Source Document", help="AR receipt / invoice number the cheque settles"
    )
    payment_execution_id = fields.Many2one(
        "fix.payment.execution",
        string="Payment Execution",
        index=True,
        ondelete="set null",
        readonly=True,
    )
    state = fields.Selection(
        [
            ("received", "Received (Held)"),
            ("deposited", "Deposited"),
            ("issued", "Issued"),
            ("cleared", "Cleared"),
            ("bounced", "Bounced"),
            ("cancelled", "Cancelled"),
        ],
        default="received",
        required=True,
        tracking=True,
    )
    deposited_date = fields.Date(readonly=True, copy=False)
    cleared_date = fields.Date(readonly=True, copy=False)
    statement_line_id = fields.Many2one(
        "fix.bank.statement.line", string="Bank Statement Line", readonly=True, copy=False
    )
    bounce_reason = fields.Char(tracking=True)
    # R7 (CIH capability report, 2026-11-09): the bank's return memo carries
    # a standard reason; keep it as a catalogued selection (the free-text
    # detail stays in bounce_reason) so bounce analytics by reason work.
    bounce_reason_code = fields.Selection(
        [
            ("insufficient_funds", "Insufficient funds"),
            ("refer_to_drawer", "Refer to drawer"),
            ("stale", "Stale cheque (past validity)"),
            ("post_dated", "Post-dated cheque presented early"),
            ("signature_differs", "Signature differs / irregular"),
            ("amount_differs", "Amount in words and figures differ"),
            ("altered", "Materially altered"),
            ("stop_payment", "Payment stopped by drawer"),
            ("account_closed", "Account closed"),
            ("drawer_deceased", "Drawer deceased / insolvency"),
            ("no_instruction", "No such account / clearing instruction"),
            ("others", "Others (see detail)"),
        ],
        string="Return Reason (bank memo)",
        tracking=True,
    )
    bounce_count = fields.Integer(readonly=True, copy=False)
    bounce_move_id = fields.Many2one(
        "account.move", string="Bounce Entry", readonly=True, copy=False
    )
    # R1 (CIH capability report, 2026-11-09): the settlement entry posted when
    # the bank cleared a RECEIVED cheque — Dr bank / Cr cheque-in-hand —
    # leaving the staging account (legacy GL 16556556) exactly as the legacy
    # books did. Empty when the cheque was never staged (captured straight
    # into the register, no AR receipt behind it).
    clearing_move_id = fields.Many2one(
        "account.move", string="Clearing Settlement Entry", readonly=True, copy=False
    )

    _CHEQUE_GUARDED = frozenset(
        {
            "state",
            "deposited_date",
            "cleared_date",
            "statement_line_id",
            "bounce_count",
            "bounce_move_id",
            "clearing_move_id",
            "payment_execution_id",
            "cheque_book_id",
        }
    )
    _CHEQUE_TERMS = (
        "cheque_no",
        "drawee_bank",
        "amount",
        "direction",
        "journal_id",
        "currency_id",
        "cheque_date",
        "partner_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._CHEQUE_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(c.state != "received" or c.payment_execution_id for c in self):
            locked |= set(self._CHEQUE_TERMS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        trusted = self.env.su or self._fix_guard_has_token()
        for vals in vals_list:
            if vals.get("direction") == "issued":
                if not trusted:
                    raise UserError(
                        "Issued cheques are written by treasury's payment release, from the "
                        "cheque book; they are not typed into the register."
                    )
                if vals.get("state", "received") == "received":
                    vals["state"] = "issued"
        return super().create(vals_list)

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            terms = set(self._CHEQUE_TERMS) & set(vals)
            for chq in self:
                if terms and (chq.state != "received" or chq.payment_execution_id):
                    changed = [f for f in terms if chq._fix_guard_differs(f, vals[f], chq[f])]
                    if changed:
                        raise UserError(
                            "Cheque %s is %s: %s cannot change."
                            % (chq.cheque_no, chq.state, ", ".join(sorted(changed)))
                        )
        return super().write(vals)

    @api.depends("cheque_date", "received_date")
    def _compute_pdc(self):
        for chq in self:
            chq.is_pdc = bool(
                chq.cheque_date and chq.received_date and chq.cheque_date > chq.received_date
            )

    @api.constrains("amount")
    def _check_amount(self):
        for chq in self:
            if chq.amount <= 0:
                raise ValidationError("A cheque amount must be positive.")

    @api.constrains("company_id", "direction", "drawee_bank", "cheque_no")
    def _check_unique_number(self):
        """The database key treats an empty drawee as 'unknown' (NULL), so the
        same number registered twice whenever the drawee was left blank. Here
        an empty drawee is one value, and spacing/case do not make a new one."""
        for chq in self:
            same = (
                self.sudo()
                .search(
                    [
                        ("id", "!=", chq.id),
                        ("company_id", "=", chq.company_id.id),
                        ("direction", "=", chq.direction),
                        ("cheque_no", "=ilike", (chq.cheque_no or "").strip()),
                    ]
                )
                .filtered(lambda c, chq=chq: _norm(c.drawee_bank) == _norm(chq.drawee_bank))
            )
            if same:
                raise ValidationError(
                    "Cheque %s%s is already in the register (%s)."
                    % (
                        chq.cheque_no,
                        " on %s" % chq.drawee_bank if chq.drawee_bank else "",
                        same[:1].display_name,
                    )
                )

    def action_deposit(self):
        """Present a received cheque to our bank — never before its date
        (a post-dated cheque presented early is dishonoured), and never
        stale: banking practice under the Negotiable Instruments Act 1881
        honours a cheque for six months from its date, and a bank returns
        an older one. A stale presentation needs an Accounting Administrator
        (R7, CIH capability report 2026-11-09)."""
        today = fields.Date.context_today(self)
        stale_after = timedelta(days=182)
        for chq in self:
            if chq.direction != "received" or chq.state not in ("received", "bounced"):
                raise UserError(
                    "Only a held (or bounced, re-presented) received cheque is deposited."
                )
            if chq.cheque_date > today:
                raise UserError(
                    "Cheque %s is post-dated to %s — it cannot be presented before then."
                    % (chq.cheque_no, chq.cheque_date)
                )
            if chq.cheque_date < today - stale_after:
                require_role(
                    self.env,
                    GROUP_ADMIN,
                    "Presenting stale cheque %s (dated %s, over six months old)"
                    % (chq.cheque_no, chq.cheque_date),
                )
                chq.message_post(
                    body="Stale presentation: cheque %s dated %s is past the six-month "
                    "validity of banking practice (NI Act 1881) — deposited on an "
                    "Accounting Administrator's authority." % (chq.cheque_no, chq.cheque_date)
                )
            if not chq.journal_id:
                raise UserError("Select the bank account the cheque is deposited into.")
            chq._guarded().write({"state": "deposited", "deposited_date": today})
        return True

    def _staged_receipt(self):
        """The confirmed M20 cheque receipt that staged THIS cheque into the
        cheque-in-hand account (matched the way the bounce consumer matches:
        cheque number / source reference, same company and amount). Exactly
        one means the CIH debit exists; zero means the cheque was captured
        straight into the register and nothing was staged."""
        self.ensure_one()
        if "fix.ar.receipt" not in self.env:
            return self.env["fix.ar.receipt"]
        keys = [k for k in {(self.cheque_no or "").strip(), (self.source_ref or "").strip()} if k]
        if not keys:
            return self.env["fix.ar.receipt"]
        base = [
            ("company_id", "=", self.company_id.id),
            ("state", "=", "confirmed"),
            ("method", "=", "cheque"),
        ]
        found = (
            self.env["fix.ar.receipt"]
            .sudo()
            .search([*base, "|", ("name", "in", keys), ("reference", "in", keys)])
        )
        if not found and self.source_ref:
            invoices = (
                self.env["fix.ar.invoice"]
                .sudo()
                .search([("company_id", "=", self.company_id.id), ("name", "=", self.source_ref)])
            )
            found = invoices.allocation_ids.receipt_id.filtered_domain(base)
        found = found.filtered(lambda r, amt=self.amount: abs(r.amount - amt) <= 0.005)
        return found[:1] if len(found) == 1 else self.env["fix.ar.receipt"]

    def _settle_cih_on_clearing(self):
        """R1 (CIH capability report, 2026-11-09): when the bank clears a
        RECEIVED cheque, the staged money leaves the cheque-in-hand account —
        Dr bank / Cr cheque-in-hand — mirroring the legacy 16556556 cycles.
        Posted only when the cheque was staged by an AR receipt (the CIH
        debit exists); a register-only cheque books nothing here and the
        note says so, so the GL never moves what was never staged."""
        self.ensure_one()
        cih = treasury_account(self.env, self.company_id, "cheque_in_hand", required=False)
        if not cih:
            self.message_post(
                body="Cheque-in-hand GL not configured "
                "(cd_cash_position.account_code.cheque_in_hand): no clearing settlement "
                "entry was posted for this cheque."
            )
            return self.env["account.move"]
        receipt = self._staged_receipt()
        if not receipt:
            self.message_post(
                body="No staged AR receipt behind cheque %s: nothing was held in the "
                "cheque-in-hand account for it, so the clearing settles no staging entry "
                "(the bank side books with the statement)." % self.cheque_no
            )
            return self.env["account.move"]
        bank = bank_account_of(self.journal_id)
        move = post_treasury_move(
            self.env,
            self.company_id,
            self.cleared_date or fields.Date.context_today(self),
            "CHEQUE CLEARED %s — %s" % (self.cheque_no, receipt.customer_id.display_name),
            [
                (bank, "Cheque %s cleared" % self.cheque_no, self.amount, 0.0, self.partner_id),
                (
                    cih,
                    "Cheque %s cleared out of hand" % self.cheque_no,
                    0.0,
                    self.amount,
                    self.partner_id,
                ),
            ],
            branch=self.operating_unit_id.branch_id
            if "branch_id" in self.operating_unit_id._fields
            else None,
            source="treasury",
        )
        self._guarded().write({"clearing_move_id": move.id})
        self.message_post(
            body="Cleared: settlement entry %s moved %.2f from cheque-in-hand to the bank "
            "(staged by receipt %s)." % (move.name, self.amount, receipt.name)
        )
        return move

    def _clear_from_statement(self, line):
        self.ensure_one()
        if self.state not in ("deposited", "issued"):
            raise UserError("Cheque %s is not awaiting clearing." % self.cheque_no)
        if not line.statement_file_hash:
            raise UserError("A cheque clears only on an imported bank statement line.")
        if (self.direction == "received") != (line.amount > 0):
            raise UserError("The statement line's sign does not fit a %s cheque." % self.direction)
        self._guarded().write(
            {"state": "cleared", "cleared_date": line.date, "statement_line_id": line.id}
        )
        if self.direction == "received":
            self._settle_cih_on_clearing()
        pay = self.payment_execution_id
        if pay and pay.state == "sent":
            pay._confirm_executed("statement", statement_line=line, reference=self.cheque_no)

    def _fix_bounce_received_after_clearing(self):
        """The bank debits back a cleared customer cheque: Dr returned-cheques
        receivable (the drawer owes it again) / Cr bank."""
        self.ensure_one()
        receivable = treasury_account(self.env, self.company_id, "cheque_returned")
        bank = bank_account_of(self.journal_id)
        return post_treasury_move(
            self.env,
            self.company_id,
            fields.Date.context_today(self),
            "CHEQUE RETURNED %s — %s" % (self.cheque_no, self.bounce_reason),
            [
                (
                    receivable,
                    "Returned cheque %s" % self.cheque_no,
                    self.amount,
                    0.0,
                    self.partner_id,
                ),
                (bank, "Returned cheque %s" % self.cheque_no, 0.0, self.amount, self.partner_id),
            ],
            source="treasury",
        )

    def action_bounce(self):
        """The bank returned the cheque: record it with the bank's reason,
        unwind the money where it had already cleared, and publish
        cheque.bounced (AR re-opens the invoice against the returned-cheque
        receivable; the paying module re-queues its payment)."""
        for chq in self:
            if chq.state not in ("deposited", "issued", "cleared"):
                raise UserError("Only a presented cheque bounces.")
            if not (chq.bounce_reason or "").strip() and not chq.bounce_reason_code:
                raise UserError(
                    "Record the bank's return reason first — the memo reason "
                    "(Return Reason) and/or its detail."
                )
            was_cleared = chq.state == "cleared"
            if was_cleared:
                require_role(self.env, GROUP_ADMIN, "Recording the return of a cleared cheque")
            vals = {"state": "bounced", "bounce_count": chq.bounce_count + 1}
            if was_cleared and chq.direction == "received":
                vals["bounce_move_id"] = chq._fix_bounce_received_after_clearing().id
            chq._guarded().write(vals)
            pay = chq.payment_execution_id.sudo()
            reason = "Cheque %s returned: %s" % (chq.cheque_no, chq.bounce_reason)
            if pay and pay.state == "sent":
                pay._guarded().write({"failure_reason": reason, "state": "failed"})
                pay._publish_failed(reason)
            elif pay and pay.state == "executed":
                pay._fix_return_after_clearing(reason)
            publish(
                self.env,
                "cheque.bounced",
                "fix.cheque",
                chq.id,
                {
                    "cheque_no": chq.cheque_no,
                    "direction": chq.direction,
                    "amount": chq.amount,
                    "source_ref": chq.source_ref or "",
                    "reason": (
                        chq.bounce_reason_code
                        and dict(self._fields["bounce_reason_code"].selection).get(
                            chq.bounce_reason_code
                        )
                    )
                    or chq.bounce_reason
                    or "",
                },
            )
            if chq.direction == "received":
                # R7 (NI Act 1881 s.138, Bangladesh): the payee must send the
                # drawer a written notice within 30 days of the dishonour memo.
                treasury_alert(
                    chq,
                    "Dishonour notice due (NI Act s.138)",
                    "Cheque %s of %.2f from %s was returned (%s). Serve the drawer a "
                    "written notice within 30 days of the dishonour memo; unpaid after a "
                    "further 30 days, a complaint may be filed."
                    % (
                        chq.cheque_no,
                        chq.amount,
                        chq.partner_id.display_name or chq.payee_name or "unknown drawer",
                        dict(self._fields["bounce_reason_code"].selection).get(
                            chq.bounce_reason_code
                        )
                        or chq.bounce_reason
                        or "reason not recorded",
                    ),
                    deadline=fields.Date.context_today(self) + timedelta(days=30),
                )
        return True

    def action_cancel(self):
        """Void an issued cheque that never left / was returned uncashed."""
        for chq in self:
            if chq.direction != "issued" or chq.state not in ("issued", "bounced"):
                raise UserError("Only an uncleared issued cheque is cancelled.")
            chq._guarded().write({"state": "cancelled"})
        return True
