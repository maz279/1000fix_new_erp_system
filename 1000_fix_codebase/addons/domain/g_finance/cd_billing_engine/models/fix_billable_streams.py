# cd_billing_engine — the billable-event streams beyond closed service
# orders (A08 M20-F4, CD-M20-04, 2026-11-23).
#
# The audit finding: fix.billable.event declared subscription and brand_claim
# sources, but the intake drained only service_order.closed and the generate
# action refused every other source. Contract/AMC periods and approved
# warranty claims were invoiced - if at all - by side consumers invisible to
# the queue, its one-hour KPI and the delivered-but-unbilled reconciliation.
# Money that should be invoiced could never be raised from the queue.
#
# The same pattern as the service-order stream is kept:
#   * a cron (or consumer) CREATES queue rows only, one per (stream, source
#     document, period), keyed by a deterministic event_id so a re-run is a
#     no-op and a cancelled row stays cancelled;
#   * no invoice exists until the queue's own action_generate_invoice runs
#     (or the existing "Process All Due" / process cron calls it);
#   * the generation path is the SOURCE MODULE'S existing one - the
#     subscription charge's _create_invoice, the contract walker's
#     _period_invoice, the A04 warranty-claim consumer - never a new
#     invoicing shortcut, and never an invented price: a source with no
#     agreed amount raises a 0-value row with a note naming what finance
#     must set (FR-ARB-002/003).
#
# The reconciliation (compute_leakage and the daily _cron_reconcile) uses the
# same candidate scans, so an uninvoiced subscription period or a recoverable
# claim appears as delivered-but-unbilled instead of silently vanishing.
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

# The streams this module queues. source_type is the queue's own selection;
# source_model is the document the invoice is raised from.
STREAM_SUBSCRIPTION = "subscription"
STREAM_CONTRACT = "contract_period"
STREAM_CLAIM = "brand_claim"

# M39: a past-due subscription is still under contract and keeps billing
# (M39-F15); a held/paused/cancelled one does not.
SUBSCRIPTION_BILLABLE_STATES = ("active", "past_due")
# M08: only a contract in force is billed; an expired one whose last period
# the walk never reached is still billed to its end (M08-F18).
CONTRACT_BILLABLE_STATES = ("active", "expiring")
# M09: the states in which the OEM agreed to pay (in full or in part).
RECOVERABLE_CLAIM_STATES = ("approved", "partially_approved")


def _event_key(source_type, source_model, source_id, period_start=None):
    """The deterministic queue key: one row per (stream, document, period).

    A cancelled row keeps its key, so a later intake run finds it and creates
    nothing - the row is the record of finance's decision, not a gap."""
    if period_start:
        return "%s:%s:%s:%s" % (source_type, source_model, source_id, period_start)
    return "%s:%s:%s" % (source_type, source_model, source_id)


def _candidate(
    source_type, source_model, record, period_start, period_end, amount, note="", customer=None
):
    """One queued-invoice candidate, from any stream.

    `customer` is explicit: a subscription/contract bills its customer, a
    claim bills the brand's OEM partner - never the device owner."""
    return {
        "source_type": source_type,
        "source_model": source_model,
        "source_id": record.id,
        "record": record,
        "company": record.company_id,
        "operating_unit": record.operating_unit_id,
        "customer": customer if customer is not None else record.customer_id,
        "currency": record.currency_id,
        "period_start": period_start,
        "period_end": period_end,
        "amount": round(amount or 0.0, 2),
        "note": note,
    }


# ---------------------------------------------------------------------------
# The due-period scans (M39 subscriptions and M08 contract periods)
# ---------------------------------------------------------------------------
def due_subscription_periods(env):
    """Due, unbilled subscription cycles (M39): next_invoice_date is due and
    the cycle window the module computes carries the agreed recurring price.

    Returns [] when cd_subscription is not installed: this module does not
    depend on it (M39 depends on CD-M20, so a hard dependency would close a
    module cycle)."""
    if "fix.subscription" not in env:
        return []
    today = fields.Date.context_today(env["fix.subscription"])
    Sub = env["fix.subscription"].sudo()
    Charge = env["fix.subscription.charge"].sudo()
    rows = []
    for sub in Sub.search(
        [("state", "in", SUBSCRIPTION_BILLABLE_STATES), ("next_invoice_date", "!=", False)]
    ):
        start = sub.next_invoice_date
        # Every cycle that is due, not only the next one: a subscription the
        # billing run missed for a quarter still owes three periods (FR-ARB-002).
        guard = 0
        while start and start <= today and guard < 240:
            end, amount = sub._fix_cycle_window(start)
            if not end:
                break  # the cycle starts after the contract end: nothing to bill
            charge = Charge.search(
                [("subscription_id", "=", sub.id), ("period_start", "=", start)], limit=1
            )
            if charge and charge.invoice_id and charge.invoice_id.state != "cancelled":
                start = end + timedelta(days=1)
                guard += 1
                continue  # already invoiced by the module's own billing run
            note = ""
            if (amount or 0.0) <= 0.005:
                note = (
                    "Subscription %s carries no agreed recurring amount for %s to %s. Finance "
                    "must set the recurring amount (or the contract value it prices) before "
                    "invoicing; no price is invented (FR-ARB-002/003)." % (sub.name, start, end)
                )
            rows.append(_candidate(STREAM_SUBSCRIPTION, sub._name, sub, start, end, amount, note))
            start = end + timedelta(days=1)
            guard += 1
    return rows


def due_contract_periods(env):
    """Due, unbilled contract billing periods (M08): the contract's own
    schedule says which periods have ended (arrears) or started (advance), and
    the period amount is the schedule's agreed value."""
    if "fix.contract" not in env:
        return []
    Contract = env["fix.contract"].sudo()
    Period = env["fix.contract.billing.period"].sudo()
    today = fields.Date.context_today(Period)
    domain = [
        ("date_start", "!=", False),
        ("date_end", "!=", False),
        ("state", "in", CONTRACT_BILLABLE_STATES),
    ]
    contracts = Contract.search(domain)
    # M08-F18: an expired contract whose last period the walk never reached
    # is still billed to its end.
    contracts |= Contract.search(
        [("date_start", "!=", False), ("date_end", "!=", False), ("state", "=", "expired")]
    ).filtered(lambda c: not c.billed_through_date or c.billed_through_date < c.date_end)
    rows = []
    for contract in contracts:
        try:
            schedule = contract._fix_billing_schedule()
        except (UserError, ValidationError):
            continue
        for row in schedule:
            if row["billed"]:
                continue
            if not Period._row_due(contract, row, today):
                continue
            note = ""
            if (row["amount"] or 0.0) <= 0.005:
                note = (
                    "Contract %s carries no agreed value for %s to %s. Finance must set "
                    "its annual value (the schedule prices from it) before invoicing; no "
                    "price is invented (FR-ARB-002/003)."
                    % (contract.code or contract.name, row["period_start"], row["period_end"])
                )
            rows.append(
                _candidate(
                    STREAM_CONTRACT,
                    contract._name,
                    contract,
                    row["period_start"],
                    row["period_end"],
                    row["amount"],
                    note,
                )
            )
    return rows


# ---------------------------------------------------------------------------
# The recoverable-claim scan (M09)
# ---------------------------------------------------------------------------
def claim_invoices(env, claim):
    """Every OEM invoice the claim's decisions raised (not cancelled)."""
    return env["fix.a04.claim.consumers"].sudo()._claim_invoices(claim)


def claim_booked(env, claim):
    """The VAT-exclusive amount already on AR for the claim."""
    consumer = env["fix.a04.claim.consumers"].sudo()
    return consumer._booked(consumer._claim_invoices(claim))


def recoverable_claims(env, include_invoiced=False):
    """Claims the warranty module marks recoverable from the brand/partner
    (approved or partially approved).

    ``include_invoiced`` is for the queue intake: a claim the A04 C7 side
    consumer already invoiced is still registered on a queue row with
    state=invoiced, so the stream's KPI and the reconciliation see it (the
    finding's "register the side-consumer invoices back onto queue rows").
    The leakage reconciliation leaves them out only when fully billed."""
    if "fix.warranty.claim" not in env:
        return []
    Claim = env["fix.warranty.claim"].sudo()
    rows = []
    for claim in Claim.search([("state", "in", RECOVERABLE_CLAIM_STATES)]):
        amount = round(claim.approved_amount or 0.0, 2)
        invoices = claim_invoices(env, claim)
        booked = claim_booked(env, claim)
        invoiced = booked >= amount - 0.005 if amount > 0.005 else bool(invoices)
        if invoiced and not include_invoiced:
            continue
        brand = claim.brand_id
        partner = brand.billing_partner() if brand and hasattr(brand, "billing_partner") else None
        note = ""
        if amount <= 0.005:
            note = (
                "Claim %s has no approved amount on record. Finance must record the "
                "brand's agreed amount on the claim decision before invoicing; no price "
                "is invented (FR-ARB-002/003)." % claim.claim_no
            )
        elif not partner:
            note = (
                "Claim %s is approved for BDT %.2f but brand %s has no OEM billing "
                "partner: link the brand's legal entity before invoicing (M09-F1)."
                % (claim.claim_no, amount, brand.name if brand else "-")
            )
        candidate = _candidate(
            STREAM_CLAIM,
            claim._name,
            claim,
            claim.decided_at or claim.created_at,
            False,
            amount,
            note,
            customer=partner or False,
        )
        candidate["invoiced"] = invoiced
        candidate["booked"] = booked
        rows.append(candidate)
    return rows


# ---------------------------------------------------------------------------
# The queue rows and their generation
# ---------------------------------------------------------------------------
class FixBillableEventStreams(models.Model):
    """The estate's other revenue streams on the same billable-event queue."""

    _name = "fix.billable.event"
    _inherit = ["fix.billable.event", "fix.guarded.mixin"]

    # The period the row bills (empty for a claim, which has no cycle).
    period_start = fields.Date(index=True, copy=False)
    period_end = fields.Date(copy=False)
    # The candidate's VAT-exclusive value, from the source's own price. 0 is
    # honest: the note says what finance must set.
    amount = fields.Monetary(
        string="Candidate Amount (VAT excl.)", currency_field="currency_id", copy=False
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        copy=False,
        default=lambda self: self.env.company.currency_id,
    )
    description = fields.Text(
        copy=False, help="The candidate line's description (source reference and period)."
    )
    amount_note = fields.Char(copy=False, help="What finance must set before this can be priced.")

    _stream_unique = models.Constraint(
        "UNIQUE (source_type, source_model, source_id, period_start)",
        "One queue row per stream, source document and period",
    )

    source_type = fields.Selection(
        selection_add=[("contract_period", "Contract / AMC Period")],
        ondelete={"contract_period": "set default"},
    )
    state = fields.Selection(
        selection_add=[("cancelled", "Cancelled")],
        ondelete={"cancelled": "set default"},
    )

    # ------------------------------------------------------------ intake
    @api.model
    def _fix_intake_periods(self, candidates):
        created = 0
        for candidate in candidates:
            key = _event_key(
                candidate["source_type"],
                candidate["source_model"],
                candidate["source_id"],
                candidate["period_start"],
            )
            if self.sudo().search_count([("event_id", "=", key)]):
                continue  # already queued: new, failed, invoiced or cancelled
            description = "%s — %s to %s" % (
                candidate["record"].display_name,
                candidate["period_start"],
                candidate["period_end"],
            )
            vals = {
                "event_id": key,
                "source_type": candidate["source_type"],
                "source_model": candidate["source_model"],
                "source_id": candidate["source_id"],
                "company_id": candidate["company"].id or self.env.company.id,
                "operating_unit_id": candidate["operating_unit"].id or False,
                "customer_id": candidate["customer"].id or False,
                "currency_id": candidate["currency"].id or False,
                "period_start": candidate["period_start"],
                "period_end": candidate["period_end"],
                "amount": candidate["amount"],
                "description": description,
                "amount_note": candidate["note"] or False,
            }
            try:
                with self.env.cr.savepoint():
                    self.sudo().create(vals)
                    created += 1
            except (UserError, ValidationError) as exc:
                # One bad source must not stop the other streams; the row is
                # absent, which the reconciliation will report as unbilled.
                _logger.warning("Billable-event intake skipped %s: %s", key, exc)
        return created

    @api.model
    def _fix_intake_claims(self, candidates):
        created = 0
        for candidate in candidates:
            claim = candidate["record"]
            key = _event_key(
                candidate["source_type"], candidate["source_model"], candidate["source_id"]
            )
            if self.sudo().search_count([("event_id", "=", key)]):
                continue
            vals = {
                "event_id": key,
                "source_type": candidate["source_type"],
                "source_model": candidate["source_model"],
                "source_id": candidate["source_id"],
                "company_id": candidate["company"].id
                if candidate["company"]
                else self.env.company.id,
                "operating_unit_id": candidate["operating_unit"].id
                if candidate["operating_unit"]
                else False,
                # A claim whose brand has no OEM billing partner is still
                # queued (with the "link the brand's legal entity" note) so
                # finance sees it; it has no customer yet. This used to crash
                # the hourly intake on customer=False.
                "customer_id": candidate["customer"].id if candidate["customer"] else False,
                "currency_id": candidate["currency"].id if candidate["currency"] else False,
                "amount": candidate["amount"],
                "description": "Warranty claim %s reimbursement (%s)"
                % (claim.claim_no, claim.brand_id.name if claim.brand_id else "-"),
                "amount_note": candidate["note"] or False,
            }
            try:
                with self.env.cr.savepoint():
                    row = self.sudo().create(vals)
                    # A04 C7: the claim's own event consumer may already have
                    # raised the receivable. Register it on the queue row so
                    # the stream's KPI and the reconciliation see it billed -
                    # never raise a second invoice.
                    invoices = claim_invoices(self.env, claim)
                    if candidate.get("invoiced") and invoices:
                        row.write(
                            {
                                "state": "invoiced",
                                "invoice_id": invoices[:1].id,
                                "invoiced_at": fields.Datetime.now(),
                            }
                        )
                    created += 1
            except (UserError, ValidationError) as exc:
                _logger.warning("Billable-event claim intake skipped %s: %s", key, exc)
        return created

    @api.model
    def _cron_intake_streams(self):
        """Hourly: queue due subscription cycles, due contract periods and
        recoverable warranty claims. Creates queue rows only - the invoice is
        raised by action_generate_invoice (the one invoicing action)."""
        created = self._fix_intake_periods(due_subscription_periods(self.env))
        created += self._fix_intake_periods(due_contract_periods(self.env))
        created += self._fix_intake_claims(recoverable_claims(self.env, include_invoiced=True))
        if created:
            _logger.info("AR billable-event stream intake: %d new events queued", created)
        return created

    # ------------------------------------------------------------ generate
    def action_cancel(self):
        """Finance decides a candidate is not billable: the row is cancelled
        and its key stays, so a later intake run never recreates it."""
        for rec in self:
            if rec.state == "invoiced":
                raise UserError(
                    "Queue row %s is already invoiced: the invoice, not the queue, is "
                    "reversed or credited (FR-ARB-011)." % rec.event_id
                )
            rec._guarded().write({"state": "cancelled", "last_error": "Cancelled by finance"})
        return True

    def action_generate_invoice(self):
        """The queue's only invoicing action: service orders keep the base
        path; the new streams use their source module's own invoice creation."""
        for rec in self:
            if rec.state in ("invoiced", "cancelled"):
                continue
            if rec.source_type == "service_order":
                super(FixBillableEventStreams, rec).action_generate_invoice()
                continue
            rec.attempts += 1
            try:
                if rec.source_type == STREAM_SUBSCRIPTION:
                    rec._fix_generate_subscription()
                elif rec.source_type == STREAM_CONTRACT:
                    rec._fix_generate_contract_period()
                elif rec.source_type == STREAM_CLAIM:
                    rec._fix_generate_claim()
                else:
                    raise UserError(
                        "Billable event %s has no invoicing path for source %s "
                        "(FR-ARB-002)." % (rec.event_id, rec.source_type)
                    )
            except (UserError, ValidationError, AccessError) as exc:
                rec.write({"state": "failed", "last_error": str(exc)[:2000]})
                _logger.warning("Billable event %s failed: %s", rec.event_id, exc)

    def _fix_mark_invoiced(self, invoice):
        self.write(
            {
                "state": "invoiced",
                "invoice_id": invoice.id,
                "invoiced_at": fields.Datetime.now(),
            }
        )

    def _fix_generate_subscription(self):
        """A due cycle: reuse the subscription module's own charge and its
        _create_invoice (the billing-run path), never a local invoice."""
        self.ensure_one()
        sub = self.env["fix.subscription"].sudo().browse(self.source_id).exists()
        if not sub:
            self.write({"state": "skipped", "last_error": "Source subscription deleted"})
            return
        if sub.state not in SUBSCRIPTION_BILLABLE_STATES:
            self.write(
                {
                    "state": "skipped",
                    "last_error": "Subscription %s is %s: not billable (M39-F15)."
                    % (sub.name, sub.state),
                }
            )
            return
        start = self.period_start or sub.next_invoice_date
        end = self.period_end
        amount = self.amount or 0.0
        if start:
            computed_end, computed_amount = sub._fix_cycle_window(start)
            if not computed_end:
                raise UserError(
                    "Subscription %s: the cycle starting %s is outside the contract term "
                    "ending %s; renew it before invoicing (FR-ARB-002)."
                    % (sub.name, start, sub.contract_end_date)
                )
            end = computed_end
            amount = round(computed_amount or 0.0, 2)
        if not start or not end:
            raise UserError(
                "Queue row %s has no billing period to invoice (FR-ARB-002)." % self.event_id
            )
        if amount <= 0.005:
            raise UserError(
                "Subscription %s has no agreed recurring amount for %s to %s: set it on "
                "the subscription before invoicing. No price is invented "
                "(FR-ARB-002/003)." % (sub.name, start, end)
            )
        Charge = self.env["fix.subscription.charge"].sudo()
        charge = Charge.search(
            [("subscription_id", "=", sub.id), ("period_start", "=", start)], limit=1
        )
        if charge and charge.invoice_id:
            if charge.invoice_id.state == "cancelled":
                raise UserError(
                    "Subscription %s cycle %s to %s was invoiced by %s, which is "
                    "cancelled: re-billing needs finance review (FR-ARB-011)."
                    % (sub.name, start, end, charge.invoice_id.name)
                )
            self._fix_mark_invoiced(charge.invoice_id)
            return
        if not charge:
            charge = Charge._guarded().create(
                {
                    "company_id": sub.company_id.id,
                    "operating_unit_id": sub.operating_unit_id.id,
                    "subscription_id": sub.id,
                    "period_start": start,
                    "period_end": end,
                    "amount": amount,
                }
            )
            charge = Charge.browse(charge.ids)
        charge._create_invoice()
        if not charge.invoice_id:
            raise UserError(
                "Subscription cycle %s to %s raised no invoice (FR-ARB-002)." % (start, end)
            )
        self._fix_mark_invoiced(charge.invoice_id)
        # Keep the module's own generator on the next cycle: the period is
        # billed exactly once, whether the queue or the billing run bills it.
        if sub.next_invoice_date and sub.next_invoice_date <= start:
            sub._guarded().write({"next_invoice_date": end + timedelta(days=1)})

    def _fix_generate_contract_period(self):
        """A due contract period: reuse the C10 walker's _period_invoice (the
        billing hand-off path), never a local invoice."""
        self.ensure_one()
        contract = self.env["fix.contract"].sudo().browse(self.source_id).exists()
        if not contract:
            self.write({"state": "skipped", "last_error": "Source contract deleted"})
            return
        if contract.state not in CONTRACT_BILLABLE_STATES and contract.state != "expired":
            self.write(
                {
                    "state": "skipped",
                    "last_error": "Contract %s is %s: not billable."
                    % (contract.code or contract.name, contract.state),
                }
            )
            return
        if contract.state == "expired" and (
            contract.billed_through_date and contract.billed_through_date >= contract.date_end
        ):
            self.write(
                {
                    "state": "skipped",
                    "last_error": "Contract %s expired and is billed through its end."
                    % (contract.code or contract.name),
                }
            )
            return
        start = self.period_start
        schedule = contract._fix_billing_schedule()
        row = next((r for r in schedule if r["period_start"] == start), None)
        if not row:
            raise UserError(
                "Contract %s has no billing period starting %s in its schedule "
                "(FR-ARB-002)." % (contract.code or contract.name, start)
            )
        amount = round(row["amount"] or 0.0, 2)
        if amount <= 0.005:
            raise UserError(
                "Contract %s has no agreed value for %s to %s: set its annual value "
                "before invoicing. No price is invented (FR-ARB-002/003)."
                % (contract.code or contract.name, row["period_start"], row["period_end"])
            )
        Period = self.env["fix.contract.billing.period"].sudo()
        period = Period.search(
            [("contract_id", "=", contract.id), ("period_start", "=", start)], limit=1
        )
        if period and period.invoice_id:
            if period.invoice_id.state == "cancelled":
                raise UserError(
                    "Contract %s period %s to %s was invoiced by %s, which is cancelled: "
                    "re-billing needs finance review (FR-ARB-011)."
                    % (
                        contract.code or contract.name,
                        period.period_start,
                        period.period_end,
                        period.invoice_id.name,
                    )
                )
            self._fix_mark_invoiced(period.invoice_id)
            return
        if not period:
            period = Period._period_for(contract, row)
            period = Period.browse(period.ids)
        invoice = Period._period_invoice(contract, period, schedule)
        self._fix_mark_invoiced(invoice)
        if not contract.billed_through_date or period.period_end > contract.billed_through_date:
            contract.sudo().mark_billed_through(period.period_end)

    def _fix_generate_claim(self):
        """A recoverable claim: the A04 C7 consumer's own decision-to-
        receivable path (delta against what the books already hold), so an
        appeal that already raised/credited is never billed twice."""
        self.ensure_one()
        claim = self.env["fix.warranty.claim"].sudo().browse(self.source_id).exists()
        if not claim:
            self.write({"state": "skipped", "last_error": "Source claim deleted"})
            return
        result = (
            self.env["fix.a04.claim.consumers"]
            .sudo()
            .consume_warranty_claim_decided(
                {"aggregate": claim._name, "aggregate_id": claim.id, "payload": {}}
            )
        )
        if result.get("model") == "fix.ar.invoice" and result.get("id"):
            invoice = self.env["fix.ar.invoice"].sudo().browse(result["id"])
            self._fix_mark_invoiced(invoice)
            return
        if result.get("model") == "fix.credit.note":
            # the brand re-decided down: the adjustment is the money leg
            self.write(
                {
                    "state": "skipped",
                    "last_error": "The brand's decision was reduced; credit notes were "
                    "raised instead of an invoice (M09-F7).",
                }
            )
            return
        if result.get("skipped"):
            self.write(
                {
                    "state": "skipped",
                    "last_error": "Claim %s is not billable: %s"
                    % (claim.claim_no, result["skipped"]),
                }
            )
            return
        raise UserError(
            "Claim %s produced no invoice from the warranty-claim hand-off "
            "(FR-ARB-002)." % claim.claim_no
        )
