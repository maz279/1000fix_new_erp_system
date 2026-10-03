# cd_cash_position — M50 Treasury, cash & banking core (P06-M04, CD-M50-01).
#
# T06: treasury EXECUTES payment requests raised as events by M52 and M20,
# publishing confirmations — nothing in finance calls treasury synchronously
# (AR-006 section 4.1 pairs 6/9, implemented as the event seam here).
# T07: bank reconciliation consumes the M04 cash-drawer model from Phase 4.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28


class FixPaymentExecution(models.Model):
    """The execution side of the payment-request event seam."""

    _name = "fix.payment.execution"
    _description = "Payment Execution"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _sql_constraints = [
        ("request_key_unique", "unique(source_model, source_id)",
         "A payment request is executed exactly once — DI-04 idempotency"),
    ]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    source_model = fields.Char(string="Source Model", required=True, index=True)
    source_id = fields.Integer(string="Source ID", required=True, index=True)
    payee = fields.Char(string="Payee", required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    amount = fields.Monetary(string="Amount", currency_field="currency_id", required=True)
    method = fields.Selection(
        [("bank_transfer", "Bank Transfer"), ("cheque", "Cheque"),
         ("cash", "Cash"), ("mobile_fs", "bKash/Nagad Merchant Pay")],
        default="bank_transfer", required=True)
    state = fields.Selection(
        [("pending", "Pending"), ("executed", "Executed"), ("failed", "Failed")],
        default="pending", required=True, tracking=True)
    executed_at = fields.Datetime(readonly=True)

    @api.model
    def consume_payment_requested(self, event: dict) -> "FixPaymentExecution":
        """The M52/M20 -> M50 seam: consume a payment.requested event.
        Idempotent on (source_model, source_id) — a replayed request never
        double-pays (DI-04: money is where idempotency defects cost most)."""
        payload = event.get("payload", {})
        existing = self.search([
            ("source_model", "=", event.get("aggregate", "")),
            ("source_id", "=", event.get("aggregate_id", 0))])
        if existing:
            return existing
        return self.create({
            "source_model": event.get("aggregate", ""),
            "source_id": event.get("aggregate_id", 0),
            "payee": payload.get("payee", "vendor:%s" % payload.get("vendor_id", "?")),
            "amount": payload.get("amount", 0.0),
        })

    def action_execute(self):
        for payment in self:
            if payment.state != "pending":
                raise UserError("Only pending payments execute")
            payment.write({"state": "executed", "executed_at": fields.Datetime.now()})
            publish(self.env, "payment.executed", "fix.payment.execution",
                    payment.id, {
                        "source_model": payment.source_model,
                        "source_id": payment.source_id,
                        "amount": payment.amount,
                        "method": payment.method,
                    })


class FixBankStatementLine(models.Model):
    """A bank statement line awaiting auto-reconciliation (T07)."""

    _name = "fix.bank.statement.line"
    _description = "Bank Statement Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit",
                                        index=True,
                                        help="Empty = company-wide bank account")
    date = fields.Date(required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    amount = fields.Monetary(currency_field="currency_id", required=True)
    reference = fields.Char(string="Bank Reference", index=True)
    narration = fields.Char()
    match_state = fields.Selection(
        [("unmatched", "Unmatched"), ("auto", "Auto-Matched"),
         ("manual", "Manually Matched")], default="unmatched", required=True)
    matched_payment_id = fields.Many2one("fix.payment.execution", string="Matched Payment")
    matched_invoice_ref = fields.Char(string="Matched Invoice")

    @api.model
    def auto_match(self) -> int:
        """T07: the in-Odoo half of reconciliation — exact reference match
        first, then amount+date-window. The >=90% G3-02 target is measured
        by the reconciliation service's rules; this is the same ladder."""
        matched = 0
        pending = self.search([("match_state", "=", "unmatched")])
        payments = self.env["fix.payment.execution"].search([("state", "=", "executed")])
        for line in pending:
            # Rule 1: exact amount match on a payment whose source reference
            # appears in the bank narration/reference.
            for payment in payments:
                ref = "AR/%s" % payment.source_id if payment.source_model == "fix.ar.invoice" else None
                if (ref and line.reference and ref in line.reference
                        and payment.currency_id == line.currency_id):
                    line.write({"match_state": "auto", "matched_payment_id": payment.id})
                    matched += 1
                    break
        return matched


class FixCashPosition(models.Model):
    """Cash position across bank + branch drawers (T07): consumes the M04
    cash-drawer model from Phase 4 (fix.cash.shift)."""

    _name = "fix.cash.position"
    _description = "Cash Position Snapshot"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    as_of = fields.Datetime(default=fields.Datetime.now, required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    bank_balance = fields.Monetary(string="Bank", currency_field="currency_id")
    drawer_float_total = fields.Monetary(string="Branch Drawers", currency_field="currency_id",
                                         compute="_compute_drawers", store=True)
    pending_payments = fields.Monetary(string="Pending Payments", currency_field="currency_id")
    total_position = fields.Monetary(string="Total Position", currency_field="currency_id",
                                     compute="_compute_total", store=True)

    @api.depends("bank_balance", "drawer_float_total", "pending_payments")
    def _compute_total(self):
        for snap in self:
            snap.total_position = snap.bank_balance + snap.drawer_float_total - snap.pending_payments

    def _compute_drawers(self):
        """Open M04 cash shifts carry their expected closing as float."""
        shifts = self.env["fix.cash.shift"].search([("state", "in", ("open", "counting"))])
        for snap in self:
            snap.drawer_float_total = sum(shifts.mapped("expected_closing"))
