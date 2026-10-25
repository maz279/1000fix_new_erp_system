# cd_cash_position — M50 Treasury, cash & banking core (P06-M04, CD-M50-01;
# A08 rebuild 2026-10-26).
#
# T06: treasury EXECUTES payment requests raised as events by M52 and M20,
# publishing confirmations — nothing in finance calls treasury synchronously
# (AR-006 section 4.1 pairs 6/9, implemented as the event seam here).
#
# A08 fixes:
#   * a payment is no longer "executed" by a bare state flip: it is released
#     to the bank (instruction file, state "sent") and only becomes executed
#     on the BANK's confirmation — a matched statement line or a bank
#     reference recorded by treasury — and that confirmation posts the GL;
#   * auto-match requires the amount AND a whole-token reference (or a
#     unique payee + amount + date-window candidate); the old substring rule
#     paired "AR/5" with "AR/55" and accepted reference-only matches;
#   * the cash position reads the bank balance from the posted GL and the
#     pending payments from the execution queue instead of manual inputs.
from __future__ import annotations

import base64
import csv
import hashlib
import io
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .treasury_common import bank_account_of, gl_balance, has_token, post_treasury_move

# legacy source-document reference prefixes (kept: banks still quote them)
# requesting documents that post their own payment entry on confirmation
SELF_POSTING_SOURCES = {"fix.payment.run.line"}
LEGACY_PREFIX = {
    "fix.ar.invoice": "AR",
    "fix.expense.claim": "EXP",
    "fix.vendor.invoice": "AP",
}
MATCH_WINDOW_DAYS = 10


class FixPaymentExecution(models.Model):
    """The execution side of the payment-request event seam.

    pending -> sent (instruction released; awaiting the bank) -> executed
    (bank-confirmed, GL posted) | failed (bank rejection, with reason)."""

    _name = "fix.payment.execution"
    _description = "Payment Execution"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _request_key_unique = models.Constraint(
        "UNIQUE (source_model, source_id)",
        "A payment request is executed exactly once — DI-04 idempotency",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(string="Instruction Ref", readonly=True, copy=False, index=True)
    source_model = fields.Char(string="Source Model", required=True, index=True)
    source_id = fields.Integer(string="Source ID", required=True, index=True)
    payee = fields.Char(string="Payee", required=True)
    partner_id = fields.Many2one("res.partner", string="Payee Partner", index=True)
    partner_bank_id = fields.Many2one(
        "res.partner.bank",
        string="Payee Account / Wallet",
        help="The payee's bank account (BEFTN/RTGS/NPSB) or MFS wallet",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Amount", currency_field="currency_id", required=True)
    method = fields.Selection(
        [
            ("bank_transfer", "Bank Transfer"),
            ("cheque", "Cheque"),
            ("cash", "Cash"),
            ("mobile_fs", "bKash/Nagad Merchant Pay"),
        ],
        default="bank_transfer",
        required=True,
    )
    rail = fields.Selection(
        [("beftn", "BEFTN"), ("rtgs", "RTGS"), ("npsb", "NPSB"), ("cheque", "Cheque")],
        string="Rail",
        help="Clearing rail (bank transfers: BEFTN / RTGS / NPSB)",
    )
    source_posts_gl = fields.Boolean(
        string="Source Posts GL",
        help="The requesting document books its own payment entry when this execution is "
        "confirmed (AP payment runs do) — treasury then posts nothing, so the bank is never "
        "credited twice.",
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Paid From",
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]",
        help="The company bank/cash account the money leaves from",
    )
    debit_account_id = fields.Many2one(
        "account.account",
        string="Debit Account",
        help="Liability cleared by this payment (e.g. AP control). Empty: the configured "
        "outgoing-payments clearing account.",
    )
    value_date = fields.Date(string="Value Date", default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("sent", "Sent — Awaiting Bank Confirmation"),
            ("executed", "Executed"),
            ("failed", "Failed"),
        ],
        default="pending",
        required=True,
        tracking=True,
    )
    sent_at = fields.Datetime(readonly=True, copy=False)
    sent_by_id = fields.Many2one("res.users", string="Released By", readonly=True, copy=False)
    executed_at = fields.Datetime(readonly=True)
    bank_reference = fields.Char(
        string="Bank Reference", tracking=True, copy=False, help="The bank's / wallet's trx id"
    )
    statement_line_id = fields.Many2one(
        "fix.bank.statement.line", string="Bank Statement Line", readonly=True, copy=False
    )
    confirmation_source = fields.Selection(
        [
            ("statement", "Bank Statement Match"),
            ("bank_reference", "Bank Reference Recorded"),
            ("caller_asserted", "Caller-Asserted (No Bank Evidence)"),
        ],
        readonly=True,
        copy=False,
    )
    bank_confirmed = fields.Boolean(
        compute="_compute_bank_confirmed", store=True, string="Bank Confirmed"
    )
    failure_reason = fields.Char(string="Failure Reason", tracking=True, copy=False)
    instruction_attachment_id = fields.Many2one(
        "ir.attachment", string="Instruction File", readonly=True, copy=False
    )
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)
    gl_note = fields.Char(string="GL Note", readonly=True, copy=False)

    @api.depends("state", "statement_line_id", "confirmation_source")
    def _compute_bank_confirmed(self):
        for pay in self:
            pay.bank_confirmed = pay.state == "executed" and (
                bool(pay.statement_line_id) or pay.confirmation_source == "bank_reference"
            )

    @api.constrains("amount")
    def _check_amount(self):
        for pay in self:
            if pay.amount < 0:
                raise ValidationError("A payment amount cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.payment.execution") or "PEX"
                )
            if vals.get("source_model") in SELF_POSTING_SOURCES:
                vals.setdefault("source_posts_gl", True)
        return super().create(vals_list)

    @api.model
    def consume_payment_requested(self, event: dict) -> FixPaymentExecution:
        """The M52/M20 -> M50 seam: consume a payment.requested event.
        Idempotent on (source_model, source_id) — a replayed request never
        double-pays (DI-04: money is where idempotency defects cost most)."""
        payload = event.get("payload", {})
        source_model = event.get("aggregate", "")
        source_id = event.get("aggregate_id", 0)
        existing = self.search([("source_model", "=", source_model), ("source_id", "=", source_id)])
        if existing:
            return existing
        # operating_unit_id is REQUIRED on the execution; the request never
        # carried it, so every consumed request failed on the NOT NULL. Take
        # it from the event, else from the requesting document.
        operating_unit_id = payload.get("operating_unit_id")
        if (
            not operating_unit_id
            and source_model in self.env
            and "operating_unit_id" in self.env[source_model]._fields
        ):
            operating_unit_id = (
                self.env[source_model].browse(source_id).exists().operating_unit_id.id
            )
        if not operating_unit_id:
            raise UserError(
                "payment.requested %s/%s carries no operating unit" % (source_model, source_id)
            )
        if payload.get("payee"):
            payee = payload["payee"]
        elif payload.get("employee_id"):  # expense claims pay the employee
            payee = "employee:%s" % payload["employee_id"]
        else:
            payee = "vendor:%s" % payload.get("vendor_id", "?")
        vals = {
            "source_model": source_model,
            "source_id": source_id,
            "operating_unit_id": operating_unit_id,
            "payee": payee,
            "amount": payload.get("amount", 0.0),
        }
        vendor = (
            payload.get("vendor_id")
            and self.env["res.partner"].browse(payload["vendor_id"]).exists()
        )
        if vendor:
            vals["partner_id"] = vendor.id
        return self.create(vals)

    # ------------------------------------------------------------------ release

    def _check_releasable(self):
        self.ensure_one()
        if self.state != "pending":
            raise UserError(
                "%s is '%s': only pending payments are released." % (self.name, self.state)
            )
        if self.amount <= 0:
            raise UserError("%s has no amount to pay." % self.name)
        bank_account_of(self.journal_id)
        if self.journal_id.company_id != self.company_id:
            raise UserError("The paying bank account belongs to another company.")
        if self.method == "cash" and self.journal_id.type != "cash":
            raise UserError("A cash payment is paid from a cash journal.")
        if (
            self.method in ("bank_transfer", "mobile_fs", "cheque")
            and self.journal_id.type != "bank"
        ):
            raise UserError("A %s is paid from a bank journal." % self.method)
        if self.method == "bank_transfer":
            if self.rail not in ("beftn", "rtgs", "npsb"):
                raise UserError("Select the bank rail (BEFTN / RTGS / NPSB) for %s." % self.name)
            acct = self.partner_bank_id
            if not acct or not acct.acc_number:
                raise UserError("%s needs the payee's bank account." % self.name)
            if self.rail in ("beftn", "rtgs") and not acct.fix_routing_number:
                raise UserError(
                    "%s: the payee account %s has no routing number (BEFTN/RTGS need it)."
                    % (self.name, acct.acc_number)
                )
            if self.rail == "rtgs":
                minimum = float(
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("cd_cash_position.rtgs_min_amount")
                    or 0.0
                )
                if minimum and self.amount < minimum:
                    raise UserError(
                        "RTGS is for amounts of at least %s (system parameter "
                        "cd_cash_position.rtgs_min_amount); use BEFTN." % minimum
                    )
        if self.method == "mobile_fs" and not (
            self.partner_bank_id and self.partner_bank_id.acc_number
        ):
            raise UserError("%s needs the payee's MFS wallet number." % self.name)

    def _instruction_csv(self) -> str:
        """A neutral instruction file. Bank-specific BEFTN/RTGS layouts differ
        per bank and are NOT verified — the treasury team uploads this to the
        bank portal or maps it to the bank's own template."""
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            [
                "instruction_ref",
                "value_date",
                "rail",
                "debit_account",
                "payee",
                "payee_account",
                "routing_number",
                "amount",
                "currency",
            ]
        )
        for pay in self:
            writer.writerow(
                [
                    pay.name,
                    pay.value_date or fields.Date.context_today(pay),
                    pay.rail or pay.method,
                    pay.journal_id.bank_acc_number or pay.journal_id.code,
                    pay.partner_bank_id.acc_holder_name or pay.payee,
                    pay.partner_bank_id.acc_number or "",
                    pay.partner_bank_id.fix_routing_number or "",
                    "%.2f" % pay.amount,
                    pay.currency_id.name,
                ]
            )
        return buf.getvalue()

    def action_release(self):
        """Release the instruction to the bank: validates the rail data,
        writes the instruction file (bank transfer / MFS) or the issued
        cheque, and waits for the bank's confirmation (state "sent")."""
        for pay in self:
            pay._check_releasable()
            vals = {"state": "sent", "sent_at": fields.Datetime.now(), "sent_by_id": self.env.uid}
            if pay.method in ("bank_transfer", "mobile_fs"):
                attachment = self.env["ir.attachment"].create(
                    {
                        "name": "%s.csv" % (pay.name or "instruction").replace("/", "-"),
                        "raw": pay._instruction_csv().encode("utf-8"),
                        "mimetype": "text/csv",
                        "res_model": pay._name,
                        "res_id": pay.id,
                    }
                )
                vals["instruction_attachment_id"] = attachment.id
            pay.write(vals)
            if pay.method == "cheque" and not self.env["fix.cheque"].search_count(
                [("payment_execution_id", "=", pay.id)]
            ):
                self.env["fix.cheque"].create(
                    {
                        "company_id": pay.company_id.id,
                        "operating_unit_id": pay.operating_unit_id.id,
                        "direction": "issued",
                        "cheque_no": pay.bank_reference or pay.name,
                        "partner_id": pay.partner_id.id,
                        "payee_name": pay.payee,
                        "amount": pay.amount,
                        "currency_id": pay.currency_id.id,
                        "cheque_date": pay.value_date or fields.Date.context_today(pay),
                        "journal_id": pay.journal_id.id,
                        "payment_execution_id": pay.id,
                    }
                )
            pay.message_post(body="Instruction released — awaiting the bank's confirmation.")
        return True

    # ------------------------------------------------------------- confirmation

    def _confirm_executed(self, source, statement_line=None, reference=None):
        """The bank confirmed the debit: post Dr liability / Cr bank and
        publish payment.executed (exactly once)."""
        self.ensure_one()
        if self.state != "sent":
            raise UserError(
                "%s is '%s': only a sent payment is confirmed." % (self.name, self.state)
            )
        bank = bank_account_of(self.journal_id)
        move = self.env["account.move"]
        note = False
        if self.source_posts_gl:
            note = "Payment entry booked by the requesting document (%s)" % self.source_model
        else:
            debit = self.debit_account_id
            if not debit:
                from .treasury_common import treasury_account

                debit = treasury_account(self.env, self.company_id, "outgoing_clearing")
            when = statement_line.date if statement_line else fields.Date.context_today(self)
            move = post_treasury_move(
                self.env,
                self.company_id,
                when,
                "PAY %s — %s" % (self.name, self.payee),
                [
                    (debit, "Payment %s" % self.name, self.amount, 0.0, self.partner_id),
                    (bank, "Paid %s" % self.payee, 0.0, self.amount, self.partner_id),
                ],
                source="treasury",
            )
        self.write(
            {
                "state": "executed",
                "executed_at": fields.Datetime.now(),
                "confirmation_source": source,
                "statement_line_id": statement_line.id if statement_line else False,
                "bank_reference": reference or self.bank_reference,
                "move_id": move.id,
                "gl_note": note,
            }
        )
        self._publish_executed()

    def _publish_executed(self):
        publish(
            self.env,
            "payment.executed",
            "fix.payment.execution",
            self.id,
            {
                "source_model": self.source_model,
                "source_id": self.source_id,
                "amount": self.amount,
                "method": self.method,
            },
        )

    def action_confirm_bank(self):
        """Treasury records the bank's confirmation (the bank / wallet trx
        reference typed on the record). A statement match does the same
        automatically (fix.bank.statement.line.auto_match)."""
        for pay in self:
            if not (pay.bank_reference or "").strip():
                raise UserError(
                    "Record the bank's reference on %s before confirming — no confirmation "
                    "without bank evidence." % pay.name
                )
            pay._confirm_executed("bank_reference", reference=pay.bank_reference.strip())
        return True

    def action_mark_failed(self):
        for pay in self:
            if pay.state != "sent":
                raise UserError("Only a sent payment can be rejected by the bank.")
            if not (pay.failure_reason or "").strip():
                raise UserError("Record the bank's rejection reason on %s first." % pay.name)
            pay.write({"state": "failed"})
            publish(
                self.env,
                "payment.failed",
                "fix.payment.execution",
                pay.id,
                {
                    "source_model": pay.source_model,
                    "source_id": pay.source_id,
                    "reason": pay.failure_reason,
                },
            )
        return True

    def action_retry(self):
        for pay in self:
            if pay.state != "failed":
                raise UserError("Only a failed payment is re-queued.")
            pay.write({"state": "pending", "sent_at": False, "instruction_attachment_id": False})
        return True

    def action_execute(self) -> None:
        """LEGACY direct execution, kept for existing callers (cd_tradein):
        marks the payment executed WITHOUT bank evidence — recorded as
        "caller-asserted", left un-bank-confirmed (bank_confirmed=False) and
        no GL is posted, so it shows on the reconciliation exceptions until
        a statement line confirms it. Treasury screens use action_release /
        action_confirm_bank instead."""
        for payment in self:
            if payment.state != "pending":
                raise UserError("Only pending payments execute")
            payment.write(
                {
                    "state": "executed",
                    "executed_at": fields.Datetime.now(),
                    "confirmation_source": "caller_asserted",
                    "gl_note": "Not posted: executed by the caller without bank evidence",
                }
            )
            payment._publish_executed()


class FixBankStatementImport(models.Model):
    """One uploaded bank statement file (CSV or MT940)."""

    _name = "fix.bank.statement.import"
    _description = "Bank Statement Import"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

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
    file = fields.Binary(string="Statement File", attachment=True)
    filename = fields.Char(string="File Name")
    format_type = fields.Selection(
        [("auto", "Auto-Detect"), ("csv", "CSV"), ("mt940", "MT940")],
        default="auto",
        required=True,
        string="Format",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("imported", "Imported"), ("duplicate", "Duplicate File")],
        default="draft",
        required=True,
        tracking=True,
    )
    imported_count = fields.Integer(string="Lines Imported", readonly=True)
    file_hash = fields.Char(string="File Hash", readonly=True)
    line_ids = fields.One2many("fix.bank.statement.line", "import_id", string="Lines")

    def action_import(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("This statement file was already processed.")
            if not rec.file:
                raise UserError("Attach the bank statement file first.")
            content = base64.b64decode(rec.file).decode("utf-8-sig", errors="replace")
            result = (
                self.env["fix.bank.statement.line"]
                .with_company(rec.company_id)
                .import_bank_feed(
                    content,
                    format_type=rec.format_type,
                    journal_id=rec.journal_id.id,
                    import_id=rec.id,
                )
            )
            rec.write(
                {
                    "state": "duplicate" if result["status"] == "duplicate_file" else "imported",
                    "imported_count": result["imported"],
                    "file_hash": result["file_hash"],
                }
            )
        return True


class FixBankStatementLine(models.Model):
    """A bank statement line awaiting reconciliation (T07)."""

    _name = "fix.bank.statement.line"
    _description = "Bank Statement Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
        help="Empty = company-wide bank account",
    )
    journal_id = fields.Many2one(
        "account.journal", string="Bank Account", index=True, domain="[('type', '=', 'bank')]"
    )
    import_id = fields.Many2one("fix.bank.statement.import", string="Import", index=True)
    date = fields.Date(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    reference = fields.Char(string="Bank Reference", index=True)
    narration = fields.Char()
    match_state = fields.Selection(
        [("unmatched", "Unmatched"), ("auto", "Auto-Matched"), ("manual", "Manually Matched")],
        default="unmatched",
        required=True,
    )
    matched_payment_id = fields.Many2one("fix.payment.execution", string="Matched Payment")
    matched_deposit_id = fields.Many2one("fix.cash.deposit", string="Matched Cash Deposit")
    matched_cheque_id = fields.Many2one("fix.cheque", string="Matched Cheque")
    matched_gateway_id = fields.Many2one("fix.gateway.settlement", string="Matched Settlement")
    matched_invoice_ref = fields.Char(string="Matched Invoice")
    matched_kind = fields.Selection(
        [
            ("payment", "Outgoing Payment"),
            ("deposit", "Branch Cash Deposit"),
            ("cheque", "Cheque"),
            ("gateway", "Gateway / MFS Settlement"),
            ("charge", "Bank Charge"),
        ],
        string="Matched To",
        readonly=True,
    )
    is_bank_charge = fields.Boolean(string="Bank Charge")
    charge_move_id = fields.Many2one("account.move", string="Charge Entry", readonly=True)
    statement_sequence = fields.Char(string="Statement Sequence", index=True)
    statement_file_hash = fields.Char(string="Statement File Hash", index=True)

    @api.model
    def import_bank_feed(
        self, file_content: str, format_type: str = "auto", journal_id=None, import_id=None
    ) -> dict:
        """INT-006: Ingest electronic bank statement feed with deduplication and sequence audit."""
        file_hash = hashlib.sha256(file_content.encode("utf-8")).hexdigest()

        existing = self.search([("statement_file_hash", "=", file_hash)], limit=1)
        if existing:
            return {"imported": 0, "status": "duplicate_file", "file_hash": file_hash}

        common = {
            "company_id": self.env.company.id,
            "statement_file_hash": file_hash,
            "journal_id": journal_id or False,
            "import_id": import_id or False,
        }
        lines_to_create = []
        try:
            from services.reconciliation.src.bank_feed_parser import parse_bank_feed

            parsed = parse_bank_feed(file_content, format_type=format_type)
            for item in parsed.lines:
                lines_to_create.append(
                    dict(
                        common,
                        date=item.date,
                        amount=float(item.amount),
                        reference=item.reference,
                        narration=item.narration,
                        statement_sequence=parsed.sequence_number,
                    )
                )
        except Exception:
            # discard anything the parser produced before it failed — the
            # fallback re-reads the whole file (no duplicated lines)
            lines_to_create = []
            reader = csv.DictReader(io.StringIO(file_content))
            for row in reader:
                dt_str = row.get("Date") or row.get("date")
                amt_str = (
                    row.get("Amount")
                    or row.get("amount")
                    or row.get("Credit")
                    or row.get("credit", "0")
                )
                if dt_str and amt_str:
                    lines_to_create.append(
                        dict(
                            common,
                            date=dt_str,
                            amount=float(amt_str),
                            reference=row.get("Reference") or row.get("reference") or "",
                            narration=row.get("Description") or row.get("narration") or "",
                        )
                    )

        if lines_to_create:
            self.create(lines_to_create)

        return {"imported": len(lines_to_create), "status": "success", "file_hash": file_hash}

    # ------------------------------------------------------------------ matching

    def _text(self):
        return "%s %s" % (self.reference or "", self.narration or "")

    def _in_window(self, start_date):
        if not start_date:
            return True
        return (
            start_date - timedelta(days=1)
            <= self.date
            <= start_date + timedelta(days=MATCH_WINDOW_DAYS)
        )

    def _payment_candidates(self, taken):
        """Outgoing payments this line can confirm: same company/currency,
        amount equal (to the paisa), sent or executed-without-bank-evidence."""
        payments = self.env["fix.payment.execution"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("currency_id", "=", self.currency_id.id),
                "|",
                ("state", "=", "sent"),
                "&",
                ("state", "=", "executed"),
                ("statement_line_id", "=", False),
            ]
        )
        # cheque payments are confirmed by their cheque clearing (fix.cheque)
        return payments.filtered(
            lambda p: (
                p.id not in taken
                and p.method != "cheque"
                and abs(abs(self.amount) - p.amount) < 0.005
                and (not self.journal_id or not p.journal_id or p.journal_id == self.journal_id)
            )
        )

    def _match_payment(self, taken):
        text = self._text()
        candidates = self._payment_candidates(taken)
        if not candidates:
            return False
        by_ref = candidates.filtered(
            lambda p: (
                has_token(text, p.name)
                or has_token(text, p.bank_reference)
                or (
                    LEGACY_PREFIX.get(p.source_model)
                    and has_token(text, "%s/%s" % (LEGACY_PREFIX[p.source_model], p.source_id))
                )
            )
        )
        chosen = by_ref if len(by_ref) == 1 else False
        if not chosen and not by_ref:
            # rule 2: payee named on the line + amount + date window, unique only
            by_payee = candidates.filtered(
                lambda p: (
                    p.payee
                    and p.payee.upper() in text.upper()
                    and self._in_window(p.sent_at.date() if p.sent_at else None)
                )
            )
            chosen = by_payee if len(by_payee) == 1 else False
        if not chosen:
            return False
        ref = chosen.name
        if LEGACY_PREFIX.get(chosen.source_model):
            legacy = "%s/%s" % (LEGACY_PREFIX[chosen.source_model], chosen.source_id)
            ref = legacy if has_token(text, legacy) else ref
        if chosen.state == "sent":
            chosen._confirm_executed("statement", statement_line=self, reference=self.reference)
        else:
            chosen.write({"statement_line_id": self.id})
        return {
            "matched_payment_id": chosen.id,
            "matched_invoice_ref": ref or str(chosen.source_id),
            "matched_kind": "payment",
        }

    def _match_deposit(self):
        if self.amount <= 0:
            return False
        deposits = self.env["fix.cash.deposit"].search(
            [("company_id", "=", self.company_id.id), ("state", "=", "in_transit")]
        )
        text = self._text()
        # The deposit slip number identifies the deposit; the bank's credited
        # amount is then taken as evidence — a short / over credit becomes a
        # variance on the deposit (never silently absorbed), the GL keeps the
        # difference in cash-in-transit until it is resolved.
        hits = deposits.filtered(
            lambda d: (
                (not self.journal_id or d.journal_id == self.journal_id)
                and has_token(text, d.slip_no or d.name)
            )
        )
        if len(hits) != 1:
            return False
        hits._credit_from_statement(self)
        return {
            "matched_deposit_id": hits.id,
            "matched_invoice_ref": hits.name,
            "matched_kind": "deposit",
        }

    def _match_cheque(self):
        cheques = self.env["fix.cheque"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("state", "in", ("deposited", "issued")),
            ]
        )
        text = self._text()
        hits = cheques.filtered(
            lambda c: (
                abs(abs(self.amount) - c.amount) < 0.005
                and ((c.direction == "received") == (self.amount > 0))
                and has_token(text, c.cheque_no)
            )
        )
        if len(hits) != 1:
            return False
        hits._clear_from_statement(self)
        return {
            "matched_cheque_id": hits.id,
            "matched_invoice_ref": hits.cheque_no,
            "matched_kind": "cheque",
        }

    def _match_gateway(self):
        if self.amount <= 0:
            return False
        batches = self.env["fix.gateway.settlement"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("state", "in", ("imported", "matched", "exceptions")),
                ("statement_line_id", "=", False),
            ]
        )
        text = self._text()
        hits = batches.filtered(
            lambda b: (
                abs(b.total_net - self.amount) < 0.005
                and (not self.journal_id or b.journal_id == self.journal_id)
                and self.date >= (b.settlement_date or self.date) - timedelta(days=1)
                and (
                    has_token(text, b.name)
                    or has_token(text, b.provider_batch_ref)
                    or b.provider_label() in text.upper()
                )
            )
        )
        if len(hits) != 1:
            return False
        hits.write({"statement_line_id": self.id})
        hits._recompute_match()
        return {
            "matched_gateway_id": hits.id,
            "matched_invoice_ref": hits.name,
            "matched_kind": "gateway",
        }

    @api.model
    def auto_match(self) -> int:
        """T07: the in-Odoo half of reconciliation. A line matches ONE
        document only when the amount agrees to the paisa AND a whole-token
        reference (or, for payments, a unique payee + date-window candidate)
        identifies it; anything ambiguous stays unmatched for a human."""
        matched = 0
        pending = self.search(
            [("match_state", "=", "unmatched"), ("company_id", "in", self.env.companies.ids)]
        )
        taken: set[int] = set()
        for line in pending:
            vals = (
                line._match_payment(taken)
                or line._match_deposit()
                or line._match_cheque()
                or line._match_gateway()
            )
            if vals:
                if vals.get("matched_payment_id"):
                    taken.add(vals["matched_payment_id"])
                vals["match_state"] = "auto"
                line.write(vals)
                matched += 1
        return matched

    def action_confirm_manual_match(self):
        """A human paired the line with a document on the form: the same
        amount rule applies, then the document is confirmed by the bank."""
        for line in self:
            if line.match_state != "unmatched":
                raise UserError("This line is already matched.")
            picked = [
                f
                for f in (
                    "matched_payment_id",
                    "matched_deposit_id",
                    "matched_cheque_id",
                    "matched_gateway_id",
                )
                if line[f]
            ]
            if len(picked) != 1:
                raise UserError("Pick exactly one document to match this line to.")
            doc = line[picked[0]]
            amount = doc.total_net if picked[0] == "matched_gateway_id" else doc.amount
            if abs(abs(line.amount) - amount) > 0.005:
                raise UserError(
                    "Amounts differ (line %s vs document %s): a match needs the same amount."
                    % (line.amount, amount)
                )
            if picked[0] == "matched_payment_id":
                if doc.state == "sent":
                    doc._confirm_executed(
                        "statement", statement_line=line, reference=line.reference
                    )
                elif doc.state == "executed" and not doc.statement_line_id:
                    doc.statement_line_id = line.id
                else:
                    raise UserError("%s is not awaiting a bank confirmation." % doc.name)
                kind = "payment"
            elif picked[0] == "matched_deposit_id":
                doc._credit_from_statement(line)
                kind = "deposit"
            elif picked[0] == "matched_cheque_id":
                doc._clear_from_statement(line)
                kind = "cheque"
            else:
                doc.write({"statement_line_id": line.id})
                doc._recompute_match()
                kind = "gateway"
            line.write(
                {
                    "match_state": "manual",
                    "matched_kind": kind,
                    "matched_invoice_ref": doc.display_name,
                }
            )
        return True

    def action_post_bank_charge(self):
        """A debit line the bank charged (fees, excise duty, SMS charges):
        post Dr bank charges / Cr bank and close the line."""
        from .treasury_common import treasury_account

        for line in self:
            if line.match_state != "unmatched" or line.amount >= 0:
                raise UserError("Only an unmatched debit line is booked as a bank charge.")
            bank = bank_account_of(line.journal_id)
            expense = treasury_account(self.env, line.company_id, "bank_charges")
            amount = abs(line.amount)
            move = post_treasury_move(
                self.env,
                line.company_id,
                line.date,
                "BANK CHARGE %s %s" % (line.reference or "", line.narration or ""),
                [
                    (expense, line.narration or "Bank charge", amount, 0.0, None),
                    (bank, line.narration or "Bank charge", 0.0, amount, None),
                ],
                source="treasury",
            )
            line.write(
                {
                    "is_bank_charge": True,
                    "charge_move_id": move.id,
                    "match_state": "manual",
                    "matched_kind": "charge",
                }
            )
        return True


class FixCashPosition(models.Model):
    """Cash position snapshot across bank (posted GL), branch drawers (M04
    cash shifts), petty cash and cash-in-transit, less payments released or
    queued but not yet confirmed by the bank."""

    _name = "fix.cash.position"
    _description = "Cash Position Snapshot"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "as_of desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    as_of = fields.Datetime(default=fields.Datetime.now, required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    bank_balance = fields.Monetary(
        string="Bank",
        currency_field="currency_id",
        compute="_compute_position",
        store=True,
        help="Posted GL balance of the company's bank journals' accounts at the snapshot time",
    )
    drawer_float_total = fields.Monetary(
        string="Branch Drawers",
        currency_field="currency_id",
        compute="_compute_drawers",
        store=True,
    )
    petty_cash_total = fields.Monetary(
        string="Petty Cash", currency_field="currency_id", compute="_compute_position", store=True
    )
    cash_in_transit_total = fields.Monetary(
        string="Cash-in-Transit",
        currency_field="currency_id",
        compute="_compute_position",
        store=True,
    )
    pending_payments = fields.Monetary(
        string="Pending Payments",
        currency_field="currency_id",
        compute="_compute_position",
        store=True,
        help="Payments queued or sent but not yet confirmed by the bank",
    )
    total_position = fields.Monetary(
        string="Total Position", currency_field="currency_id", compute="_compute_total", store=True
    )

    @api.depends(
        "bank_balance",
        "drawer_float_total",
        "petty_cash_total",
        "cash_in_transit_total",
        "pending_payments",
    )
    def _compute_total(self) -> None:
        for snap in self:
            snap.total_position = (
                snap.bank_balance
                + snap.drawer_float_total
                + snap.petty_cash_total
                + snap.cash_in_transit_total
                - snap.pending_payments
            )

    @api.depends("company_id", "as_of")
    def _compute_position(self) -> None:
        for snap in self:
            company = snap.company_id
            journals = self.env["account.journal"].search(
                [("type", "=", "bank"), ("company_id", "=", company.id)]
            )
            accounts = journals.mapped("default_account_id")
            as_of_date = (snap.as_of or fields.Datetime.now()).date()
            snap.bank_balance = gl_balance(self.env, accounts, company, date_to=as_of_date)
            funds = self.env["fix.imprest.fund"].search(
                [("company_id", "=", company.id), ("state", "=", "active")]
            )
            snap.petty_cash_total = sum(funds.mapped("book_balance"))
            snap.cash_in_transit_total = sum(
                self.env["fix.cash.deposit"]
                .search([("company_id", "=", company.id), ("state", "=", "in_transit")])
                .mapped("amount")
            )
            snap.pending_payments = sum(
                self.env["fix.payment.execution"]
                .search([("company_id", "=", company.id), ("state", "in", ("pending", "sent"))])
                .mapped("amount")
            )

    # Without any dependency Odoo never computes a stored field, so every
    # snapshot carried drawer_float_total = 0. The snapshot's own company and
    # timestamp drive it: computed at creation, re-taken when as_of moves.
    @api.depends("company_id", "as_of")
    def _compute_drawers(self) -> None:
        """Open M04 cash shifts carry their expected closing as float — only
        the snapshot's OWN company's drawers (the search was company-blind,
        so one entity's position counted every other entity's cash)."""
        for snap in self:
            shifts = self.env["fix.cash.shift"].search(
                [("state", "in", ("open", "counting")), ("company_id", "=", snap.company_id.id)]
            )
            snap.drawer_float_total = sum(shifts.mapped("expected_closing"))

    def action_take_snapshot(self):
        """Take a fresh snapshot for each selected snapshot's company."""
        created = self.browse()
        for company in self.mapped("company_id") or self.env.company:
            created |= self.create({"company_id": company.id, "as_of": fields.Datetime.now()})
        return {"snapshot_ids": created.ids}
