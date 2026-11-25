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

    # A04 ERP audit (20 Nov 2026): how the period was billed and the revenue
    # account its income belongs to (M08-F5). In arrears the service is
    # already rendered: the invoice credits the family's revenue account
    # directly. In advance it is a contract liability, and M53's recognition
    # moves it to this account as the period is served.
    billing_timing = fields.Selection(
        [("arrears", "In arrears"), ("advance", "In advance")], readonly=True
    )
    revenue_account_id = fields.Many2one(
        "account.account",
        string="Revenue Account",
        readonly=True,
        help="The contract family's revenue account (cd_billing_engine.account_code."
        "contract_revenue_<family>): credited at issue in arrears, by M53's "
        "recognition when billed in advance.",
    )

    # ------------------------------------------------------------------ job
    @api.model
    def cron_bill_contracts(self):
        """Daily: invoice every due, unbilled period of every in-force
        contract, and the last periods of a contract that expired before the
        walk reached them (A04 ERP audit M08-F18). Returns the number of
        invoices raised. Off until Finance sets
        cd_billing_engine.contract_auto_billing = 1."""
        self._assert_hand_off()
        param = self.env["ir.config_parameter"].sudo().get_param(AUTO_BILLING_PARAM, "0")
        if param != "1":
            return 0
        today = fields.Date.context_today(self)
        Contract = self.env["fix.contract"].sudo()
        base = [
            ("annual_value", ">", 0.0),
            ("date_start", "!=", False),
            ("date_end", "!=", False),
        ]
        contracts = Contract.search([("state", "in", BILLABLE_STATES), *base])
        # M08-F18: an expired contract whose last period the walk never
        # reached (the cron missed the end date) is still billed to its end.
        contracts |= Contract.search([("state", "=", "expired"), *base]).filtered(
            lambda c: not c.billed_through_date or c.billed_through_date < c.date_end
        )
        raised = 0
        for contract in contracts:
            try:
                with self.env.cr.savepoint():
                    raised += self._bill_contract(contract, min(today, contract.date_end))
            except (UserError, ValidationError) as exc:
                # One refusing contract (bad term, unbillable schedule) must
                # not stop the others; the contract's chatter carries the why.
                contract.message_post(
                    body="Billing hand-off skipped this contract: %s"
                    % (exc.args[0] if exc.args else exc)
                )
                continue
        return raised

    def _assert_hand_off(self):
        if not self.env.su:
            raise AccessError(
                "The contract billing hand-off runs as the scheduled service only "
                "(report C10); a person issues the drafts it leaves behind."
            )

    @staticmethod
    def _row_due(contract, row, today):
        """In arrears a period is due once it has ended; in advance once it
        has started (A04 ERP audit M08-F6)."""
        if contract.billing_timing == "advance":
            return row["period_start"] <= today
        return row["period_end"] <= today

    def _bill_contract(self, contract, today):
        """Raise the draft invoices for one contract's due periods and
        advance its billed-through date. Returns the invoices raised."""
        contract.ensure_one()
        schedule = contract._fix_billing_schedule()
        due = [
            row
            for row in schedule
            if not row["billed"] and row["amount"] > 0.0 and self._row_due(contract, row, today)
        ]
        if not due:
            return 0
        raised = 0
        for row in due:
            period = self._period_for(contract, row)
            if not period.invoice_id:
                period.invoice_id = self._period_invoice(contract, period, schedule)
                raised += 1
        through = max(row["period_end"] for row in due)
        contract.message_post(
            body="Billing hand-off (C10): %d draft invoice(s) for the periods %s to %s. "
            "Finance reviews and issues them; the contract is billed through %s, so "
            "amendments cannot reach inside a billed period."
            % (raised, min(row["period_start"] for row in due), through, through)
        )
        # The hand-off's own service (su-only, refuses to move backwards).
        if not contract.billed_through_date or through > contract.billed_through_date:
            contract.mark_billed_through(through)
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
                "billing_timing": contract.billing_timing or "arrears",
            }
        )

    def _contract_invoices(self, contract, exclude=None):
        periods = self.sudo().search([("contract_id", "=", contract.id)])
        if exclude:
            periods -= exclude
        return periods.mapped("invoice_id").filtered(lambda i: i.state != "cancelled")

    def _period_vat(self, contract, period, det, schedule, invoice_date):
        """M51's VAT on the period. The LAST period of the term carries the
        rounding of the term's VAT, so per-period rounding never leaves the
        term a paisa away from the VAT on its value (M08-F6: 17,100.01)."""
        vat = Decimal(str(det.vat_amount))
        last = bool(schedule) and schedule[-1]["period_start"] == period.period_start
        if not last:
            return vat
        target = contract._fix_billing_target()
        term = m51_determine(
            self.env,
            [
                tax_logic.TaxLine(
                    product_code="AMC",
                    qty=Decimal("1"),
                    unit_price=Decimal(str(target)).quantize(TWO, ROUND_HALF_UP),
                )
            ],
            on_date=invoice_date,
            company=contract.company_id,
        ).lines[0]
        billed = sum(
            (Decimal(str(inv.vat_amount)) for inv in self._contract_invoices(contract, period)),
            Decimal("0"),
        )
        adjusted = Decimal(str(term.vat_amount)) - billed
        # only a rounding residue is absorbed (a rate change mid-term is not)
        if abs(adjusted - vat) <= TWO * len(schedule) and adjusted >= 0:
            return adjusted.quantize(TWO, ROUND_HALF_UP)
        return vat

    def _assert_within_accepted(self, contract, period, line_total):
        """M36-F2: what the term invoices never exceeds the total the customer
        accepted (quotation / tender award), unless the term itself moved."""
        accepted = contract.accepted_total or 0.0
        if accepted <= 0.0 or contract.amendment_version or contract.terminated_on:
            return
        billed = sum(self._contract_invoices(contract, period).mapped("total_payable"))
        if billed + line_total > accepted + 0.01:
            raise UserError(
                "Contract %s would invoice BDT %.2f over its term, above the BDT %.2f the "
                "customer accepted: the schedule and the accepted price disagree."
                % (contract.code, billed + line_total, accepted)
            )

    def _period_invoice(self, contract, period, schedule=None):
        """The period's draft invoice: one line, VAT by M51's synchronous
        determination (the M39 subscription-charge pattern, product code
        AMC), a truthful manual_reason so finance's action_issue has its
        FR-ARB-010 reason, the branch of the contract's unit (M08-F4) and the
        family's revenue account (M08-F5)."""
        from .fix_a04_contract_billing import contract_revenue_account

        schedule = schedule if schedule is not None else contract._fix_billing_schedule()
        invoice_date = self._period_invoice_date(contract, period)
        taxable = Decimal(str(period.amount)).quantize(TWO, ROUND_HALF_UP)
        determination = m51_determine(
            self.env,
            [tax_logic.TaxLine(product_code="AMC", qty=Decimal("1"), unit_price=taxable)],
            on_date=invoice_date,
            company=contract.company_id,
        )
        det = determination.lines[0]
        vat = self._period_vat(contract, period, det, schedule, invoice_date)
        line_total = Decimal(str(det.taxable_amount)) + vat
        self._assert_within_accepted(contract, period, float(line_total))
        branch = contract._fix_billing_branch()
        invoice = (
            self.env["fix.ar.invoice"]
            .sudo()
            .create(
                {
                    "company_id": contract.company_id.id,
                    "customer_id": contract.customer_id.id,
                    "operating_unit_id": contract.operating_unit_id.id,
                    "branch_id": branch.id or False,
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
                                "vat_amount": float(vat),
                                "line_total": float(line_total),
                            },
                        )
                    ],
                }
            )
        )
        account = contract_revenue_account(self.env, contract)
        timing = contract.billing_timing or "arrears"
        period.sudo().write({"billing_timing": timing, "revenue_account_id": account.id or False})
        if timing == "arrears" and account:
            invoice._guarded().write({"revenue_account_id": account.id})
        return invoice

    def _period_invoice_date(self, contract, period):
        """E3-04 (third rehearsal): a period billed in ARREARS is invoiced at
        its END, one billed in ADVANCE at its START (M08-F6); never inside a
        locked period: once that month is closed the date moves to the first
        open day after the lock (the C8 rule action_issue enforces, read from
        the same lock source)."""
        day = period.period_start if contract.billing_timing == "advance" else period.period_end
        return ar_first_open_date(self.env, contract.company_id, day)
