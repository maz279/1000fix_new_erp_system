# cd_cash_position — Cheque Management (A08 · M50).
#
# The cheque register: received cheques (customer payments, incl. post-dated
# cheques held until their date) and issued cheques (treasury payments by
# cheque). Clearing is confirmed by the bank statement; a bounce is recorded
# with the bank's reason and published so AR / the paying module reopen the
# document. The money postings themselves stay with the documents that
# carry them (AR receipt confirm, payment execution confirm) — the register
# never double-books.
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish


class FixCheque(models.Model):
    _name = "fix.cheque"
    _description = "Cheque"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
        "fix.payment.execution", string="Payment Execution", index=True, ondelete="set null"
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
    bounce_count = fields.Integer(readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("direction") == "issued" and vals.get("state", "received") == "received":
                vals["state"] = "issued"
        return super().create(vals_list)

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

    def action_deposit(self):
        """Present a received cheque to our bank — never before its date
        (a post-dated cheque presented early is dishonoured)."""
        today = fields.Date.context_today(self)
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
            if not chq.journal_id:
                raise UserError("Select the bank account the cheque is deposited into.")
            chq.write({"state": "deposited", "deposited_date": today})
        return True

    def _clear_from_statement(self, line):
        self.ensure_one()
        if self.state not in ("deposited", "issued"):
            raise UserError("Cheque %s is not awaiting clearing." % self.cheque_no)
        self.write({"state": "cleared", "cleared_date": line.date, "statement_line_id": line.id})
        pay = self.payment_execution_id
        if pay and pay.state == "sent":
            pay._confirm_executed("statement", statement_line=line, reference=self.cheque_no)

    def action_bounce(self):
        """The bank returned the cheque: record it with the bank's reason and
        publish cheque.bounced (AR reopens the receipt / the paying module
        re-queues the payment)."""
        for chq in self:
            if chq.state not in ("deposited", "issued", "cleared"):
                raise UserError("Only a presented cheque bounces.")
            if not (chq.bounce_reason or "").strip():
                raise UserError("Record the bank's return reason first.")
            chq.write({"state": "bounced", "bounce_count": chq.bounce_count + 1})
            pay = chq.payment_execution_id
            if pay and pay.state == "sent":
                pay.write(
                    {
                        "failure_reason": "Cheque %s returned: %s"
                        % (chq.cheque_no, chq.bounce_reason)
                    }
                )
                pay.action_mark_failed()
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
                    "reason": chq.bounce_reason,
                },
            )
        return True

    def action_cancel(self):
        """Void an issued cheque that never left / was returned uncashed."""
        for chq in self:
            if chq.direction != "issued" or chq.state not in ("issued", "bounced"):
                raise UserError("Only an uncleared issued cheque is cancelled.")
            chq.state = "cancelled"
        return True
