# fix.cash.shift — cash drawer and shift control (P04-M02-T04).
# AS-10: money is Monetary with explicit currency. Reconciles to M19 in Phase 6.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

import logging

logger = logging.getLogger(__name__)


class FixCashShift(models.Model):
    """A cash-drawer shift with opening/closing balances and reconciliation."""
    _name = "fix.cash.shift"
    _description = "Cash Shift"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "shift_date desc, branch_id"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)

    branch_id = fields.Many2one("fix.branch", string="Branch", required=True)
    shift_date = fields.Date(default=fields.Date.today, required=True)
    shift_type = fields.Selection(
        [("morning", "Morning"), ("afternoon", "Afternoon"), ("evening", "Evening"),
         ("full_day", "Full Day")],
        required=True, default="full_day")
    operator_id = fields.Many2one("hr.employee", string="Shift Operator", required=True)

    state = fields.Selection(
        [("open", "Open"), ("counting", "Counting"), ("closed", "Closed"),
         ("reconciled", "Reconciled"), ("discrepancy", "Discrepancy")],
        default="open", required=True, tracking=True)

    # AS-10: all cash amounts are Monetary with explicit currency
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    opening_float = fields.Monetary(string="Opening Float", currency_field="currency_id",
                                     required=True, tracking=True)
    closing_counted = fields.Monetary(string="Closing Counted", currency_field="currency_id")
    expected_closing = fields.Monetary(string="Expected Closing", currency_field="currency_id",
                                       compute="_compute_expected", store=True)
    variance = fields.Monetary(string="Variance", currency_field="currency_id",
                               compute="_compute_expected", store=True)

    opened_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    closed_at = fields.Datetime(readonly=True)

    # Transaction summary
    cash_payments = fields.Monetary(string="Cash Payments", currency_field="currency_id")
    cash_refunds = fields.Monetary(string="Cash Refunds", currency_field="currency_id")
    cash_advances = fields.Monetary(string="Cash Advances", currency_field="currency_id")

    reconciliation_notes = fields.Text()
    reconciled_by = fields.Many2one("res.users", readonly=True)
    reconciled_at = fields.Datetime(readonly=True)

    @api.depends("opening_float", "cash_payments", "cash_refunds", "cash_advances",
                 "closing_counted")
    def _compute_expected(self):
        for rec in self:
            rec.expected_closing = (rec.opening_float + rec.cash_payments
                                    - rec.cash_refunds - rec.cash_advances)
            rec.variance = (rec.closing_counted - rec.expected_closing
                            if rec.closing_counted else 0.0)

    def action_close_shift(self):
        for rec in self:
            if rec.state != "open":
                raise ValidationError("Only open shifts can be closed.")
            rec.state = "counting"

    def action_reconcile(self):
        """Complete the reconciliation (T07: end-of-shift report, Bengali-first)."""
        for rec in self:
            rec.closed_at = fields.Datetime.now()
            if abs(rec.variance) < 0.01:
                rec.state = "reconciled"
            else:
                rec.state = "discrepancy"
            rec.reconciled_by = self.env.uid
            rec.reconciled_at = fields.Datetime.now()
            self._emit("shift.closed", rec)

    def _emit(self, event: str, rec):
        from libs.py.fix_events import publish
        publish(self.env, event, "fix.cash.shift", rec.id, {
            "shift_id": rec.id, "branch": rec.branch_id.name,
            "variance": rec.variance, "currency": rec.currency_id.name,
        })
