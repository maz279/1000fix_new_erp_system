# fix_payout_reconciliation.py — Payout reconciliation comparing counts & amounts (IN-007 §11, FF-94).
#
# A08 remediation (B4, M53-14, BRU-REV-13): the "rail" side was typed — an
# unpaid draft run reconciled "balanced" and a detected break was written
# back to balanced. The disbursed side is now READ from the run's M50
# payment instructions: what the bank statement confirmed (count and
# amount, per payee). A run with nothing released to treasury has nothing
# to reconcile, and the outcome (state) is the run's, never typed.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixPayoutReconciliation(models.Model):
    """Payout reconciliation comparing count and amount separately (IN-007 §11.3, FF-94).
    Enforces zero aged breaks > 30 days for clean audit status."""

    _name = "fix.payout.reconciliation"
    _description = "Payout Reconciliation / পরিশোধ সমন্বয়"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "reconciliation_date desc, id desc"

    name = fields.Char(
        string="Reconciliation Ref", required=True, copy=False, readonly=True, default="New"
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    payout_run_id = fields.Many2one(
        "fix.payout.run", string="Payout Run", required=True, index=True
    )
    rail_name = fields.Char(
        string="Rail / Gateway Name", required=True, default="INT-007 Seller Payout Rail"
    )
    reconciliation_date = fields.Date(
        string="Reconciliation Date", default=fields.Date.context_today
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )

    # Separate Count and Amount comparisons (FF-94)
    system_count = fields.Integer(string="System Recipient Count", readonly=True)
    rail_count = fields.Integer(
        string="Bank-Confirmed Count",
        default=0,
        readonly=True,
        help="Payee instructions the imported bank statement confirmed (M50).",
    )
    count_matched = fields.Boolean(
        string="Count Matched", compute="_compute_reconciliation", store=True
    )

    system_amount = fields.Monetary(
        string="System Total Payable", currency_field="currency_id", readonly=True
    )
    rail_amount = fields.Monetary(
        string="Bank-Confirmed Amount",
        currency_field="currency_id",
        default=0.0,
        readonly=True,
        help="The amounts the imported bank statement debited for the run (M50).",
    )
    amount_matched = fields.Boolean(
        string="Amount Matched", compute="_compute_reconciliation", store=True
    )

    unmatched_count = fields.Integer(
        string="Unmatched Records Count", compute="_compute_reconciliation", store=True
    )
    unmatched_amount = fields.Monetary(
        string="Unmatched Discrepancy Amount",
        currency_field="currency_id",
        compute="_compute_reconciliation",
        store=True,
    )

    aged_unmatched_count = fields.Integer(
        string="Unmatched Aged > 30 Days", compute="_compute_reconciliation", store=True
    )
    aged_unmatched_amount = fields.Monetary(
        string="Aged Discrepancy Amount",
        currency_field="currency_id",
        compute="_compute_reconciliation",
        store=True,
    )

    state = fields.Selection(
        [
            # A reconciliation that has not been run is NOT balanced (the
            # default used to be "balanced" before anything was compared).
            ("draft", "Not Run / চালানো হয়নি"),
            ("balanced", "Balanced / সমন্বিত"),
            ("break_detected", "Break Detected / অসঙ্গতি"),
            ("investigating", "Investigating / তদন্তাধীন"),
            ("resolved", "Resolved / সমাধানকৃত"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    break_notes = fields.Text(string="Break Notes / অসঙ্গতি বিবরণ")
    line_ids = fields.One2many(
        "fix.payout.reconciliation.line", "reconciliation_id", string="Break Lines"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "system_count",
            "system_amount",
            "rail_count",
            "rail_amount",
            "line_ids",
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.payout.reconciliation")
                    or f"REC/{fields.Date.today().year}/New"
                )
        return super().create(vals_list)

    def _fix_bank_side(self):
        """{payee: (confirmed amount, confirmed?)} from the run's M50
        instructions: an instruction counts once the bank statement confirmed
        it (executed with an imported statement line)."""
        self.ensure_one()
        out = {}
        for line in self.payout_run_id.line_ids.filtered(lambda ln: ln.amount > 0.005):
            pay = line.payment_execution_id.sudo()
            confirmed = bool(pay) and pay.state == "executed" and bool(pay.statement_line_id)
            amount = (
                (pay["released_amount"] if "released_amount" in pay._fields else 0.0) or pay.amount
                if confirmed
                else 0.0
            )
            out[line] = (amount, confirmed)
        return out

    @api.depends(
        "system_count",
        "rail_count",
        "system_amount",
        "rail_amount",
        "line_ids.is_aged",
        "line_ids.discrepancy",
    )
    def _compute_reconciliation(self):
        for rec in self:
            rec.count_matched = rec.system_count == rec.rail_count
            rec.amount_matched = abs(rec.system_amount - rec.rail_amount) < 0.01

            break_lines = rec.line_ids
            rec.unmatched_count = len(break_lines)
            rec.unmatched_amount = sum(break_lines.mapped("discrepancy"))

            aged_lines = break_lines.filtered(lambda line: line.is_aged)
            rec.aged_unmatched_count = len(aged_lines)
            rec.aged_unmatched_amount = sum(aged_lines.mapped("discrepancy"))

    def action_run_reconciliation(self):
        """Execute reconciliation run. Reports count & amount separately (FF-94, BR-01..BR-05)."""
        for rec in self:
            if not rec.payout_run_id:
                raise UserError("Select a payout run to reconcile")

            run = rec.payout_run_id
            lines = run.line_ids.filtered(lambda ln: ln.amount > 0.005)
            if not lines.filtered("payment_execution_id"):
                raise UserError(
                    "Payout run %s has released nothing to treasury (%s): there is no "
                    "disbursement to reconcile." % (run.name, run.state)
                )
            bank = rec._fix_bank_side()
            Line = self.env["fix.payout.reconciliation.line"].sudo()
            rec.line_ids.sudo().unlink()
            for line, (amount, confirmed) in bank.items():
                if confirmed and abs(amount - line.amount) <= 0.005:
                    continue
                Line.create(
                    {
                        "reconciliation_id": rec.id,
                        "seller_partner_id": line.partner_id.id,
                        "system_amount": line.amount,
                        "rail_amount": amount,
                        "discrepancy": round(line.amount - amount, 2),
                        "record_date": fields.Date.to_date(
                            line.payment_execution_id.create_date
                        )
                        if line.payment_execution_id
                        else fields.Date.context_today(rec),
                        "status": "discrepancy" if confirmed else "unmatched",
                    }
                )
            rec._guarded().write(
                {
                    "system_count": len(lines),
                    "system_amount": run.approved_total or run.total_payable,
                    "rail_count": len([1 for _a, ok in bank.values() if ok]),
                    "rail_amount": round(sum(a for a, ok in bank.values() if ok), 2),
                }
            )

            rec._compute_reconciliation()

            if not rec.count_matched or not rec.amount_matched or rec.unmatched_count > 0:
                rec._guarded().write({"state": "break_detected"})
                publish(
                    self.env,
                    "platform.reconciliation_divergence",
                    "fix.payout.reconciliation",
                    rec.id,
                    {
                        "reconciliation_ref": rec.name,
                        "payout_run": rec.payout_run_id.name,
                        "count_diff": rec.system_count - rec.rail_count,
                        # rounded to the paisa: the raw float difference
                        # leaked artefacts (410.45 -> 410.4500000000007)
                        "amount_diff": rec.currency_id.round(rec.system_amount - rec.rail_amount),
                        "aged_unmatched": rec.aged_unmatched_count,
                    },
                )
            else:
                rec._guarded().write({"state": "balanced"})


class FixPayoutReconciliationLine(models.Model):
    """Line item detailing individual counterparty discrepancy in payout reconciliation."""

    _name = "fix.payout.reconciliation.line"
    _description = "Payout Reconciliation Break Line"

    reconciliation_id = fields.Many2one(
        "fix.payout.reconciliation",
        string="Reconciliation",
        ondelete="cascade",
        required=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company", related="reconciliation_id.company_id", store=True, index=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="reconciliation_id.operating_unit_id", store=True
    )
    seller_partner_id = fields.Many2one("res.partner", string="Seller", required=True)
    currency_id = fields.Many2one("res.currency", related="reconciliation_id.currency_id")
    system_amount = fields.Monetary(string="System Net Payable", currency_field="currency_id")
    rail_amount = fields.Monetary(string="Rail Cleared Amount", currency_field="currency_id")
    discrepancy = fields.Monetary(string="Discrepancy Amount", currency_field="currency_id")
    record_date = fields.Date(string="Record Date", default=fields.Date.context_today)
    age_days = fields.Integer(string="Age in Days", compute="_compute_age", store=True)
    is_aged = fields.Boolean(string="Aged > 30 Days", compute="_compute_age", store=True)
    status = fields.Selection(
        [
            ("matched", "Matched"),
            ("unmatched", "Unmatched"),
            ("discrepancy", "Discrepancy"),
        ],
        default="discrepancy",
        required=True,
    )

    @api.depends("record_date")
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.record_date:
                days = (today - rec.record_date).days
                rec.age_days = max(0, days)
                rec.is_aged = rec.age_days > 30
            else:
                rec.age_days = 0
                rec.is_aged = False
