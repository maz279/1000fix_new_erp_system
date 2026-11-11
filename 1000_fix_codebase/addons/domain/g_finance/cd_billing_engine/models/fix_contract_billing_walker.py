# fix_contract_billing_walker - the C10 bridge the A04 report left open
# (§7.10 "still open, honestly" item 4): _fix_billing_schedule() and
# mark_billed_through() existed as service APIs, but no cron walked a
# contract's due periods into M20 invoices - the AR ledger only ever saw a
# contract if finance typed one in by hand.
#
# The shape is the estate's own M39 precedent (cd_subscription's
# cron_generate_due_charges + FixSubscriptionCharge._create_invoice):
#   * the job is DAILY and IDEMPOTENT - one period raises at most one
#     invoice (fix.ar.invoice's UNIQUE (source_model, source_id) backs the
#     search, fix.contract.billing.period's UNIQUE (contract_id,
#     period_start) backs the period row), and a rerun after a partial
#     failure re-links and still advances the billed-through date;
#   * it is OFF until Finance sets cd_billing_engine.contract_auto_billing
#     = 1 (it raises draft invoices; nobody's AR ledger changes on deploy);
#   * every invoice is DRAFT with a truthful manual_reason - issue (gapless
#     number, Mushak 6.3, GL) stays finance's deliberate action_issue, and
#     VAT is M51's synchronous determination (standard 15% unless the
#     tariff says otherwise), never a local constant;
#   * suspended, draft, expired and terminated contracts are not billed:
#     only the states that are in force (active/expiring);
#   * each contract runs in its own savepoint, so one bad contract is
#     skipped (and logged on its chatter), not the whole run.
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.addons.cd_tax_engine_bd.models import tax_logic
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_billing_engine import ar_first_open_date, m51_determine

TWO = Decimal("0.01")

# The switch (off on deploy): the walker raises draft invoices on the AR
# ledger, so Finance turns it on per environment, like M39's
# cd_subscription.auto_billing.
AUTO_BILLING_PARAM = "cd_billing_engine.contract_auto_billing"

# Only the states in force are billed; the contract module owns the state
# machine (IN_FORCE = active/expiring).
BILLABLE_STATES = ("active", "expiring")


class FixContractBillingWalker(models.Model):
    """The M20 billing hand-off for fix.contract (C10)."""

    _inherit = "fix.contract.billing.period"

    invoice_id = fields.Many2one(
        "fix.ar.invoice",
        string="Invoice",
        readonly=True,
        copy=False,
        index=True,
        help="The draft invoice the hand-off raised for this period.",
    )
    invoice_state = fields.Selection(related="invoice_id.state", string="Invoice State")

    # ------------------------------------------------------------------ job
    @api.model
    def cron_bill_contracts(self):
        """Daily: invoice every due, unbilled period of every in-force
        contract. Returns the number of invoices raised. Off until Finance
        sets cd_billing_engine.contract_auto_billing = 1."""
        self._assert_hand_off()
        param = self.env["ir.config_parameter"].sudo().get_param(AUTO_BILLING_PARAM, "0")
        if param != "1":
            return 0
        today = fields.Date.context_today(self)
        contracts = (
            self.env["fix.contract"]
            .sudo()
            .search(
                [
                    ("state", "in", BILLABLE_STATES),
                    ("annual_value", ">", 0.0),
                    ("date_start", "!=", False),
                    ("date_end", "!=", False),
                ],
            )
        )
        raised = 0
        for contract in contracts:
            try:
                with self.env.cr.savepoint():
                    raised += self._bill_contract(contract, today)
            except (UserError, ValidationError):
                # One refusing contract (bad term, unbillable schedule) must
                # not stop the others; the contract's chatter carries the why.
                contract.message_post(
                    body="Billing hand-off skipped this contract (its schedule refused; "
                    "see the run's dead letters)."
                )
                continue
        return raised

    def _assert_hand_off(self):
        if not self.env.su:
            raise AccessError(
                "The contract billing hand-off runs as the scheduled service only "
                "(report C10); a person issues the drafts it leaves behind."
            )

    def _bill_contract(self, contract, today):
        """Raise the draft invoices for one contract's due periods and
        advance its billed-through date. Returns the invoices raised."""
        contract.ensure_one()
        schedule = contract._fix_billing_schedule()
        due = [
            row
            for row in schedule
            if row["period_end"] <= today and not row["billed"] and row["amount"] > 0.0
        ]
        if not due:
            return 0
        raised = 0
        for row in due:
            period = self._period_for(contract, row)
            if not period.invoice_id:
                period.invoice_id = self._period_invoice(contract, period)
                raised += 1
        contract.message_post(
            body="Billing hand-off (C10): %d draft invoice(s) for the periods ending "
            "%s to %s. Finance reviews and issues them; the billed-through date is now "
            "%s, so amendments cannot reach inside a billed period."
            % (
                raised,
                min(row["period_end"] for row in due),
                max(row["period_end"] for row in due),
                max(row["period_end"] for row in due),
            )
        )
        # The hand-off's own service (su-only, refuses to move backwards).
        contract.mark_billed_through(max(row["period_end"] for row in due))
        return raised

    def _period_for(self, contract, row):
        """The period row for a schedule entry: found by the UNIQUE
        (contract_id, period_start) key, else created. Re-runs after a
        partial failure find yesterday's row, not a twin."""
        existing = self.sudo().search(
            [("contract_id", "=", contract.id), ("period_start", "=", row["period_start"])],
            limit=1,
        )
        if existing:
            return existing
        return self.sudo().create(
            {
                "contract_id": contract.id,
                "period_start": row["period_start"],
                "period_end": row["period_end"],
                "amount": row["amount"],
            }
        )

    def _period_invoice(self, contract, period):
        """The period's draft invoice: one line, VAT by M51's synchronous
        determination (the M39 subscription-charge pattern, product code
        AMC), a truthful manual_reason so finance's action_issue has its
        FR-ARB-010 reason, and the arrears invoice date (_period_invoice_date)."""
        invoice_date = self._period_invoice_date(contract, period)
        determination = m51_determine(
            self.env,
            [
                tax_logic.TaxLine(
                    product_code="AMC",
                    qty=Decimal("1"),
                    unit_price=Decimal(str(period.amount)).quantize(TWO, ROUND_HALF_UP),
                )
            ],
            on_date=invoice_date,
            company=contract.company_id,
        )
        det = determination.lines[0]
        invoice = (
            self.env["fix.ar.invoice"]
            .sudo()
            .create(
                {
                    "company_id": contract.company_id.id,
                    "customer_id": contract.customer_id.id,
                    "operating_unit_id": contract.operating_unit_id.id,
                    "currency_id": contract.currency_id.id,
                    "source_model": period._name,
                    "source_id": period.id,
                    "invoice_date": invoice_date,
                    "manual_reason": "Contract billing hand-off %s: %s to %s"
                    % (contract.code, period.period_start, period.period_end),
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "description": "%s — %s to %s"
                                % (contract.name, period.period_start, period.period_end),
                                "taxable_amount": float(det.taxable_amount),
                                "vat_amount": float(det.vat_amount),
                                "line_total": float(det.line_total),
                            },
                        )
                    ],
                }
            )
        )
        return invoice

    def _period_invoice_date(self, contract, period):
        """E3-04 (third rehearsal): the period is billed in ARREARS, so its
        invoice is dated at the period END - never at its start, which pushed
        the GL entry and the Mushak 6.3 into an earlier month - and never
        inside a locked period: once that month is closed the date moves to
        the first open day after the lock (the C8 rule action_issue enforces,
        read from the same lock source)."""
        return ar_first_open_date(self.env, contract.company_id, period.period_end)
