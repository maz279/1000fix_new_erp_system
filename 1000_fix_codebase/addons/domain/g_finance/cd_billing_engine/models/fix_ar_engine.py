# cd_billing_engine — M20 AR engine depth (CD-M20-02, 2026-10-25).
#
# Closes the three structural breaks found by the M20 audit:
#   1. the billable-event queue (FR-ARB-001/002/043/044) — closed service
#      orders were never invoiced because nothing consumed
#      service_order.closed (21 events stranded in the outbox);
#   2. receipts + matching + allocation (FR-ARB-019..028) — payments were
#      completely disconnected from AR (no receipt model, no open-item
#      accounting, an evidence-free paid flip);
#   3. credit control, disputes, ageing snapshots, payment links — the
#      registry screens had no data surface at all.
#
# GL postings go through M19's hardened post_with_dimensions (source="ar"
# and "receipt"). Accounts resolve per company from ir.config_parameter
# overrides or the chart; a company without the accounts/posts journal
# SKIPS posting with an honest gl_note — invoicing is never blocked by GL
# configuration (the settlement module refuses; AR must not).
from __future__ import annotations

import logging
import uuid
from datetime import date, datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

from .fix_finance_approval import GROUP_ACCOUNTANT, GROUP_ADMINISTRATOR, float_param, require_role

_logger = logging.getLogger(__name__)

# Account roles for AR postings: default code + label. Overridable per
# system parameter cd_billing_engine.account_code.<role> (settlement pattern).
AR_ACCOUNTS = {
    "ar": ("121000", "Trade Receivables control"),
    "revenue": ("400000", "Sales Revenue"),
    "vat_output": ("211000", "VAT Output (Mushak 6.3)"),
    "writeoff_expense": ("630000", "Bad-Debt / Write-off Expense"),
    "cash": ("101401", "Cash"),
    "bank": ("101402", "Bank"),
    "channel_mfs": ("251000", "MFS/Card Channel Clearing (two-stage; M50 settles)"),
    # VAT the customer deducted at source (Mushak 6.6 received): a claim
    # against the VAT payable, adjusted in the Mushak 9.1 return.
    "vds_receivable": ("132000", "VDS Receivable (Mushak 6.6 received, claimed in 9.1)"),
    # IFRS 15 contract liability for subscription / AMC billing.
    "deferred_revenue": ("212000", "Contract Liability (Deferred Revenue)"),
    # A02 audit B2: a transit-damage payout recovered from the liable courier
    # (cd_settlement_ext hand-back). MD-035 4-90-10-010 "Other income" is
    # Odoo 450000, the account rentals use for damage recovery income.
    "claim_recovery": ("450000", "Damage Claim Recovery Income (liable courier)"),
    # A08 M20-5/-6: the IFRS 9 loss allowance and its expense. No default
    # code: the chart has no account that is certainly the allowance, so a
    # write-off without a posted ECL run or this parameter expenses in full.
    "ecl_provision": (None, "Expected Credit Loss Allowance (IFRS 9)"),
    "ecl_expense": (None, "Impairment Loss on Receivables (IFRS 9)"),
}

# The eight capture tenders (FR-ARB-019) and the GL role each clears into.
# Two-stage model: MFS/card money lands in a CHANNEL CLEARING account and is
# settled to bank by M50 later — never booked straight to bank here.
RECEIPT_METHODS = [
    ("cash", "Cash"),
    ("cheque", "Cheque"),
    ("bank_transfer", "Bank Transfer / BEFTN"),
    ("bkash", "bKash"),
    ("nagad", "Nagad"),
    ("card", "Card (POS / SSLCommerz)"),
    ("mobile_wallet", "Other Mobile Wallet"),
    ("adjustment", "Internal Adjustment"),
]
METHOD_ROLE = {
    "cash": "cash",
    "cheque": "bank",
    "bank_transfer": "bank",
    "bkash": "channel_mfs",
    "nagad": "channel_mfs",
    "card": "channel_mfs",
    "mobile_wallet": "channel_mfs",
    # an internal adjustment offsets documents, it moves no money: the
    # account must be picked explicitly (no default is invented).
    "adjustment": None,
}

# Hours a payment link stays valid (FR-ARB-015); 48 h is the engine's
# original default.
PARAM_LINK_HOURS = "cd_billing_engine.payment_link_hours"
# BRU-ARB-22 / FR-ARB-024: a receipt unapplied longer than this is escalated.
# 7 days is the spec's own measure ("Unapplied receipts older than 7 days").
PARAM_UNAPPLIED_DAYS = "cd_billing_engine.unapplied_escalation_days"
DEFAULT_UNAPPLIED_DAYS = 7.0
DEFAULT_LINK_HOURS = 48.0
_HOLD_TOKEN = object()

NID_CASH_THRESHOLD_PARAM = "cd_billing_engine.nid_cash_threshold"
NID_CASH_THRESHOLD_DEFAULT = 50000  # BDT — the rule is M51's (FR-ARB-026)


def _ar_account(env, company, role):
    """The company's GL account for an AR role, or None (honest skip).

    Unlike settlement's refusing helper, AR issuance must never be blocked
    by GL configuration: a missing account means the posting is skipped and
    the reason recorded on the document (gl_note)."""
    default_code, _label = AR_ACCOUNTS[role]
    code = (
        env["ir.config_parameter"].sudo().get_param(f"cd_billing_engine.account_code.{role}")
        or default_code
    )
    if not code:
        return env["account.account"]
    return (
        env["account.account"]
        .with_company(company)
        .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    )


def _ar_journal(env, company):
    """The company's general journal for AR postings, or None (skip)."""
    return env["account.journal"].search(
        [("type", "=", "general"), ("company_id", "=", company.id)], limit=1
    )


def _post_ar_move(env, company, entry_date, ref, lines, dimension_by_line, source):
    """Post through M19's hardened engine; returns (move|None, note).

    `lines`: [(account_id, name, debit, credit, partner_id|False)] — must be
    balanced by the caller."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    journal = _ar_journal(env, company)
    if not journal:
        return None, "GL not posted: no general journal for %s" % company.name
    missing = [line[0] for line in lines if not line[0]]
    if missing:
        return None, "GL not posted: account role unconfigured for %s" % company.name
    move_vals = {
        "journal_id": journal.id,
        "company_id": company.id,
        "date": entry_date,
        "ref": ref,
        "line_ids": [
            (
                0,
                0,
                {
                    "account_id": account_id,
                    "name": name,
                    "debit": debit,
                    "credit": credit,
                    "partner_id": partner_id or False,
                },
            )
            for account_id, name, debit, credit, partner_id in lines
        ],
    }
    Move = env["account.move"]
    if hasattr(Move, "_fix_post_via_m19"):
        move = Move._fix_post_via_m19(move_vals, source, dimension_by_line=dimension_by_line)
    else:
        move, _dims = post_with_dimensions(env, move_vals, dimension_by_line, source=source)
    return move, None


# ---------------------------------------------------------------------------
# A1 — the billable-event queue (FR-ARB-001/002/043/044)
# ---------------------------------------------------------------------------
class FixBillableEvent(models.Model):
    """One revenue event awaiting invoicing (FR-ARB-001: a single typed
    queue from every revenue module). Intake is idempotent on event_id;
    failures are recorded and AGED — never silently expired (FR-ARB-044)."""

    _name = "fix.billable.event"
    _description = "Billable Event"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "first_seen_at desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    event_id = fields.Char(
        string="Event ID", required=True, index=True, copy=False, help="The outbox event UUID"
    )
    source_type = fields.Selection(
        [
            ("service_order", "Closed Service Order"),
            ("subscription", "Subscription Renewal"),
            ("brand_claim", "Brand Claim"),
        ],
        required=True,
        default="service_order",
    )
    source_model = fields.Char(required=True)
    source_id = fields.Integer(required=True, index=True)
    customer_id = fields.Many2one("res.partner", string="Customer", index=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("invoiced", "Invoiced"),
            ("failed", "Failed"),
            ("skipped", "Skipped (not billable)"),
        ],
        default="new",
        required=True,
        tracking=True,
    )
    attempts = fields.Integer(default=0)
    last_error = fields.Text()
    first_seen_at = fields.Datetime(default=fields.Datetime.now, required=True)
    invoiced_at = fields.Datetime(readonly=True)
    invoice_id = fields.Many2one("fix.ar.invoice", string="Invoice", readonly=True)
    age_days = fields.Integer(compute="_compute_age", string="Age (days)")

    _event_unique = models.Constraint("UNIQUE (event_id)", "One queue row per event")

    @api.depends("first_seen_at")
    def _compute_age(self):
        now = fields.Datetime.now()
        for rec in self:
            rec.age_days = (now - rec.first_seen_at).days if rec.first_seen_at else 0

    @api.model
    def consume_order_closed(self, event: dict) -> FixBillableEvent | None:
        """Idempotent intake of one service_order.closed event (the
        cd_cx_feedback consumer pattern). Creates the queue row only; the
        invoice is generated by the process step, never at intake."""
        event_id = event.get("event_id") or ""
        if self.search([("event_id", "=", event_id)], limit=1):
            return None
        order_id = event.get("aggregate_id")
        order = self.env["fix.service.order"].sudo().browse(order_id).exists()
        if not order:
            return None
        return self.create(
            {
                "event_id": event_id,
                "source_type": "service_order",
                "source_model": "fix.service.order",
                "source_id": order_id,
                "customer_id": order.customer_id.id,
                "company_id": order.company_id.id or self.env.company.id,
                "operating_unit_id": (
                    order.operating_unit_id or order.branch_id.operating_unit_id
                ).id,
            }
        )

    @api.model
    def _cron_intake(self):
        """Hourly: drain service_order.closed events from the outbox into the
        queue (idempotent). AR consumes the TABLE — invoice generation must
        not depend on bus delivery (the 21 stranded events were all
        'published')."""
        events = (
            self.env["fix.event.outbox"]
            .sudo()
            .search([("event_type", "=", "service_order.closed")], order="create_date asc")
        )
        taken = 0
        for outbox_row in events:
            import json as _json

            try:
                payload = _json.loads(outbox_row.payload or "{}")
            except ValueError:
                payload = {}
            row = self.consume_order_closed(
                {
                    "event_id": outbox_row.event_id,
                    "aggregate_id": outbox_row.aggregate_id,
                    "payload": payload,
                }
            )
            if row:
                taken += 1
        if taken:
            _logger.info("AR billable-event intake: %d new events queued", taken)

    def action_generate_invoice(self):
        """Generate the invoice for this queue row now (the stranded-event
        recovery path and the screen's per-row action)."""
        for rec in self:
            if rec.state == "invoiced":
                continue
            rec.attempts += 1
            try:
                if rec.source_type != "service_order":
                    raise UserError("Only service-order events generate invoices in this phase")
                order = self.env["fix.service.order"].sudo().browse(rec.source_id).exists()
                if not order:
                    rec.write({"state": "skipped", "last_error": "Source order deleted"})
                    continue
                invoice = (
                    self.env["fix.ar.invoice"]
                    .sudo()
                    .with_company(rec.company_id)
                    .from_closed_service_order(order, rec.first_seen_at or fields.Datetime.now())
                )
                rec.write(
                    {
                        "state": "invoiced",
                        "invoice_id": invoice.id,
                        "invoiced_at": fields.Datetime.now(),
                    }
                )
            except UserError as exc:
                rec.write({"state": "failed", "last_error": str(exc)[:2000]})
                _logger.warning("Billable event %s failed: %s", rec.event_id, exc)

    @api.model
    def action_process_all_due(self):
        """The screen's 'Process All Due' — one button, fully self-contained:
        intakes unconsumed outbox events first (the stranded-event recovery
        path), then processes every new row + failed rows under the retry
        ceiling. One poisoned event never stops the batch."""
        self._cron_intake()
        due = self.search([("state", "in", ["new", "failed"]), ("attempts", "<", 3)])
        due.action_generate_invoice()
        return {
            "processed": len(due),
            "invoiced": len(due.filtered(lambda r: r.state == "invoiced")),
        }

    def _cron_process_due(self):
        self.action_process_all_due()


# ---------------------------------------------------------------------------
# A4 — receipts, matching & allocation (FR-ARB-019..028)
# ---------------------------------------------------------------------------
class FixArReceipt(models.Model):
    """A captured customer receipt. Confirming posts Dr channel-account /
    Cr AR control through M19 (two-stage: MFS/card money sits in channel
    clearing until M50 settles — never booked straight to bank)."""

    _name = "fix.ar.receipt"
    _description = "AR Receipt"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "receipt_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True)
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True, ondelete="restrict"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    name = fields.Char(default="New", copy=False, readonly=True, index=True)
    amount = fields.Monetary(currency_field="currency_id", required=True)
    method = fields.Selection(RECEIPT_METHODS, required=True, default="cash")
    reference = fields.Char(
        string="Reference (trx id / cheque no)",
        index=True,
        help="bKash/Nagad TrxID, cheque number, bank reference — the match key",
    )
    receipt_date = fields.Date(default=fields.Date.today, required=True)
    nid_captured = fields.Char(
        string="Customer NID (cash > BDT 50,000)",
        help="FR-ARB-026: high-value cash must record the NID (rule owned by M51)",
    )
    account_id = fields.Many2one(
        "account.account",
        string="Cleared Into Account",
        readonly=True,
        help="The channel clearing / cash / bank account this receipt posted to",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("reversed", "Reversed"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    allocation_ids = fields.One2many("fix.ar.allocation", "receipt_id", string="Allocations")
    allocated_amount = fields.Monetary(compute="_compute_allocation", store=True)
    unapplied_amount = fields.Monetary(compute="_compute_allocation", store=True)
    unapplied_escalated_at = fields.Datetime(
        string="Unapplied Escalated On",
        readonly=True,
        copy=False,
        help="When this receipt was escalated to the Accounting Administrators for sitting "
        "unapplied past the configured age (BRU-ARB-22). The job only flags it; the receipt "
        "is never netted against another balance.",
    )
    posted_move_id = fields.Many2one("account.move", readonly=True, copy=False)
    gl_note = fields.Char(readonly=True, copy=False)
    reversal_reason = fields.Char(readonly=True)

    RECEIPT_GUARDED = {
        "state",
        "account_id",
        "posted_move_id",
        "gl_note",
        "reversal_reason",
    }
    # Frozen once the receipt is confirmed: its GL entry carries them
    # (A08 M20-4: the amount was raised to 11,500 after a 1,000 posting).
    RECEIPT_LOCKED = (
        "amount",
        "method",
        "customer_id",
        "currency_id",
        "receipt_date",
        "company_id",
        "reference",
        "nid_captured",
        "name",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.RECEIPT_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.RECEIPT_LOCKED)
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            touched = set(self.RECEIPT_LOCKED) & set(vals)
            if touched and self.filtered(lambda r: r.state != "draft"):
                raise UserError(
                    "A confirmed receipt is frozen with its GL posting (%s); reverse it and "
                    "capture a new one." % ", ".join(sorted(touched))
                )
        return super().write(vals)

    @api.depends("amount", "allocation_ids.amount", "state")
    def _compute_allocation(self):
        for rec in self:
            if rec.state == "reversed":
                rec.allocated_amount = 0.0
                rec.unapplied_amount = 0.0
            else:
                allocated = sum(rec.allocation_ids.mapped("amount"))
                rec.allocated_amount = allocated
                rec.unapplied_amount = rec.amount - allocated

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.ar.receipt")
                    or "RCP/%s/New" % fields.Date.today().year
                )
        return super().create(vals_list)

    def _nid_threshold(self) -> int:
        raw = self.env["ir.config_parameter"].sudo().get_param(NID_CASH_THRESHOLD_PARAM)
        try:
            return int(raw) if raw else NID_CASH_THRESHOLD_DEFAULT
        except ValueError:
            return NID_CASH_THRESHOLD_DEFAULT

    def action_confirm(self):
        # a Billing clerk captures the draft; an Accountant confirms the posting
        require_role(self.env, GROUP_ACCOUNTANT, "Confirming a receipt")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only draft receipts can be confirmed")
            if rec.amount <= 0:
                raise UserError("Receipt amount must be positive")
            threshold = rec._nid_threshold()
            if rec.method == "cash" and rec.amount > threshold:
                nid = (rec.nid_captured or "").strip()
                if not nid:
                    raise UserError(
                        "Cash above BDT %s requires the customer NID (FR-ARB-026)" % threshold
                    )
                # BRU-ARB-07: a National ID is 10 (smart card), 13 or 17 digits
                if not (nid.isdigit() and len(nid) in (10, 13, 17)):
                    raise UserError(
                        "Customer NID %r is not a National ID (10, 13 or 17 digits) — "
                        "FR-ARB-026" % nid
                    )
            role = METHOD_ROLE.get(rec.method)
            account = _ar_account(rec.env, rec.company_id, role) if role else None
            if not account:
                if role:
                    raise UserError(
                        "Confirm refused: no GL account for method '%s' (role '%s') — "
                        "configure the chart or cd_billing_engine.account_code.%s. "
                        "Refusing rather than posting untracked money" % (rec.method, role, role)
                    )
                raise UserError(
                    "Confirm refused: internal adjustments need an explicit clearing account"
                )
            # The chart may require the branch dimension on the cash/channel
            # account (COA-03). Resolve a real branch before posting: the
            # receipt's own, else the branch of the customer's latest issued
            # invoice in THIS company — never a branch from another company.
            if not rec.branch_id:
                invoice_branch = (
                    rec.env["fix.ar.invoice"]
                    .search(
                        [
                            ("customer_id", "=", rec.customer_id.id),
                            ("company_id", "=", rec.company_id.id),
                            ("branch_id", "!=", False),
                        ],
                        order="invoice_date desc, id desc",
                        limit=1,
                    )
                    .branch_id
                )
                if invoice_branch:
                    rec.write({"branch_id": invoice_branch.id})
            ar = _ar_account(rec.env, rec.company_id, "ar")
            note = None
            move = None
            if ar:
                try:
                    move, note = _post_ar_move(
                        rec.env,
                        rec.company_id,
                        rec.receipt_date,
                        "RCT %s — %s (%s)" % (rec.name, rec.customer_id.name, rec.method),
                        [
                            (account.id, "Receipt via %s" % rec.method, rec.amount, 0.0, False),
                            (ar.id, "AR applied", 0.0, rec.amount, rec.customer_id.id),
                        ],
                        {
                            0: rec.env["fix.ar.invoice"]._ar_posting_dims(rec.branch_id.id),
                            1: rec.env["fix.ar.invoice"]._ar_posting_dims(rec.branch_id.id),
                        },
                        source="receipt",
                    )
                except UserError as exc:
                    msg = str(exc)
                    if "branch" in msg.lower() and "dimension" in msg.lower():
                        raise UserError(
                            "Set the Branch on receipt %s before confirming — the GL account "
                            "'%s' requires the branch dimension (COA-03)."
                            % (rec.name, account.display_name)
                        ) from exc
                    raise
            else:
                note = "GL not posted: AR control account unconfigured"
            rec._guarded().write(
                {
                    "state": "confirmed",
                    "account_id": account.id,
                    "posted_move_id": move.id if move else False,
                    "gl_note": note or False,
                }
            )
            publish(
                rec.env,
                "receipt.captured",
                "fix.ar.receipt",
                rec.id,
                {
                    "receipt": rec.name,
                    "customer_id": rec.customer_id.id,
                    "amount": rec.amount,
                    "method": rec.method,
                },
            )

    def action_reverse(self, reason):
        """FR-ARB-027: reversal with reason — only receipts with nothing
        applied (un-allocate first); posts the mirror move."""
        require_role(self.env, GROUP_ACCOUNTANT, "Reversing a receipt")
        for rec in self:
            if rec.state != "confirmed":
                raise UserError("Only confirmed receipts can be reversed")
            if rec.unapplied_amount < rec.amount - 0.005:
                raise UserError("Receipt has allocations — remove them before reversing")
            if not (reason or "").strip():
                raise UserError("A reversal reason is required (FR-ARB-027)")
            note = None
            if rec.posted_move_id:
                ar = _ar_account(rec.env, rec.company_id, "ar")
                if ar:
                    _mirror, note = _post_ar_move(
                        rec.env,
                        rec.company_id,
                        fields.Date.today(),
                        "REVERSAL: RCT %s — %s" % (rec.name, reason),
                        [
                            (
                                rec.account_id.id,
                                "Reversal of %s" % rec.name,
                                0.0,
                                rec.amount,
                                False,
                            ),
                            (ar.id, "AR reinstated", rec.amount, 0.0, rec.customer_id.id),
                        ],
                        {
                            0: rec.env["fix.ar.invoice"]._ar_posting_dims(rec.branch_id.id),
                            1: rec.env["fix.ar.invoice"]._ar_posting_dims(rec.branch_id.id),
                        },
                        source="receipt",
                    )
            rec._guarded().write(
                {
                    "state": "reversed",
                    "reversal_reason": reason[:500],
                    "gl_note": note or rec.gl_note,
                }
            )

    @api.model
    def action_auto_match(self):
        """FR-ARB-021: scored proposals for the allocation console — never
        auto-committed. Scores: reference hit 0.99, exact amount 0.95,
        ±2% tolerance 0.75; everything else stays in the exception queue."""
        Invoice = self.env["fix.ar.invoice"]
        proposals = []
        receipts = self.search([("state", "=", "confirmed")]).filtered(
            lambda r: r.unapplied_amount > 0.005
        )
        for receipt in receipts:
            open_invoices = Invoice.search(
                [("customer_id", "=", receipt.customer_id.id), ("state", "=", "issued")],
                order="invoice_date asc",
            ).filtered(lambda inv: inv.amount_residual > 0.005)
            for inv in open_invoices:
                score = 0.0
                ref = (receipt.reference or "").strip()
                if ref and (ref in (inv.name or "") or ref in (inv.mushak_id.mushak_no or "")):
                    score = 0.99
                elif abs(receipt.unapplied_amount - inv.amount_residual) < 0.005:
                    score = 0.95
                elif (
                    inv.amount_residual
                    and (abs(receipt.unapplied_amount - inv.amount_residual) / inv.amount_residual)
                    <= 0.02
                ):
                    score = 0.75
                if score:
                    proposals.append(
                        {
                            "receipt_id": receipt.id,
                            "receipt": receipt.name,
                            "invoice_id": inv.id,
                            "invoice": inv.name,
                            "customer": receipt.customer_id.name,
                            "amount": min(receipt.unapplied_amount, inv.amount_residual),
                            "score": score,
                        }
                    )
        proposals.sort(key=lambda p: -p["score"])
        return proposals


class FixArReceiptUnapplied(models.Model):
    """BRU-ARB-22 / AUT-ARB-20: unapplied receipts are aged and escalated."""

    _inherit = "fix.ar.receipt"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"unapplied_escalated_at"}

    @api.model
    def _cron_escalate_unapplied(self):
        """Daily: flag each confirmed receipt with money unapplied past the
        configured age, once, with a to-do for the Accounting Administrators.
        Moves no money and posts nothing. Returns how many were escalated."""
        days = float_param(self.env, PARAM_UNAPPLIED_DAYS, DEFAULT_UNAPPLIED_DAYS)
        cutoff = fields.Date.context_today(self) - timedelta(days=int(days))
        rows = self.sudo().search(
            [
                ("state", "=", "confirmed"),
                ("unapplied_amount", ">", 0.005),
                ("receipt_date", "<=", cutoff),
                ("unapplied_escalated_at", "=", False),
            ]
        )
        group = self.env.ref(GROUP_ADMINISTRATOR, raise_if_not_found=False)
        holders = group.sudo().all_user_ids.filtered("active") if group else self.env["res.users"]
        for receipt in rows:
            receipt._guarded().write({"unapplied_escalated_at": fields.Datetime.now()})
            body = (
                "Receipt %s: BDT %.2f of %s from %s is still unapplied after %s day(s) "
                "(BRU-ARB-22): apply it to the customer's open invoices or refund it. It is not "
                "netted against other balances."
                % (
                    receipt.name,
                    receipt.unapplied_amount,
                    receipt.method,
                    receipt.customer_id.display_name,
                    (fields.Date.context_today(self) - receipt.receipt_date).days,
                )
            )
            receipt.message_post(body=body)
            for user in holders.filtered(lambda u, r=receipt: r.company_id in u.company_ids)[:1]:
                receipt.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Unapplied receipt %s" % receipt.name,
                    note=body,
                    user_id=user.id,
                )
        return len(rows)


class FixArAllocation(models.Model):
    """Open-item accounting: applying (part of) a receipt to a specific
    invoice (FR-ARB-022/023/025). Full application flips the invoice to
    paid WITH evidence — the path action_register_paid never had."""

    _name = "fix.ar.allocation"
    _description = "AR Receipt Allocation"
    _order = "allocated_at desc, id desc"
    _rec_name = "receipt_id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    receipt_id = fields.Many2one("fix.ar.receipt", required=True, ondelete="restrict", index=True)
    invoice_id = fields.Many2one("fix.ar.invoice", required=True, ondelete="restrict", index=True)
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id", required=True)
    allocated_at = fields.Datetime(default=fields.Datetime.now, required=True)
    allocated_by = fields.Many2one("res.users", default=lambda self: self.env.user)

    @api.model
    def _fix_check_totals(self, receipts, invoices):
        """A08 M20-4: checked on the RESULT, after every row of the call is in
        place (a per-row check let one 11,500 receipt pay two 11,500 invoices
        in one create, and a write raised an allocation past its receipt)."""
        for receipt in receipts:
            allocated = sum(receipt.allocation_ids.mapped("amount"))
            if allocated > receipt.amount + 0.005:
                raise UserError(
                    "Receipt %s of %.2f would be allocated %.2f: an allocation never exceeds "
                    "what the receipt has unapplied." % (receipt.name, receipt.amount, allocated)
                )
        for invoice in invoices:
            if invoice._raw_residual() < -0.005:
                raise UserError(
                    "Invoice %s would be over-settled by %.2f: an allocation never exceeds the "
                    "invoice residual." % (invoice.name, -invoice._raw_residual())
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            receipt = self.env["fix.ar.receipt"].browse(vals.get("receipt_id"))
            invoice = self.env["fix.ar.invoice"].browse(vals.get("invoice_id"))
            if receipt.state != "confirmed":
                raise UserError("Only confirmed receipts can be allocated")
            if invoice.state != "issued":
                raise UserError(
                    "Payments are rejected against %s invoices (FR-ARB-025)"
                    % (invoice.state or "non-issued")
                )
            if receipt.customer_id != invoice.customer_id:
                raise UserError(
                    "Cross-customer allocation refused — receipt %s vs invoice %s"
                    % (receipt.name, invoice.name)
                )
            if vals.get("amount", 0) <= 0:
                raise UserError("Allocation amount must be positive")
            if vals.get("amount", 0) > receipt.unapplied_amount + 0.005:
                raise UserError(
                    "Allocation %s exceeds receipt %s unapplied %s"
                    % (vals.get("amount"), receipt.name, receipt.unapplied_amount)
                )
            if vals.get("amount", 0) > invoice.amount_residual + 0.005:
                raise UserError(
                    "Allocation %s exceeds invoice %s residual %s"
                    % (vals.get("amount"), invoice.name, invoice.amount_residual)
                )
            vals["company_id"] = vals.get("company_id") or receipt.company_id.id
            vals["operating_unit_id"] = (
                vals.get("operating_unit_id") or receipt.operating_unit_id.id
            )
            if not self.env.su:
                vals["allocated_by"] = self.env.uid
        allocations = super().create(vals_list)
        allocations.invalidate_recordset()
        self._fix_check_totals(allocations.receipt_id, allocations.invoice_id)
        allocations._fix_flip_paid()
        return allocations

    def _fix_flip_paid(self):
        # the evidence-bearing paid transition: fully applied => paid
        for invoice in self.invoice_id:
            if invoice.state == "issued" and invoice.amount_residual <= 0.005:
                receipt_refs = ", ".join(invoice.allocation_ids.mapped("receipt_id.name"))
                invoice._guarded().write({"state": "paid", "paid_date": fields.Date.today()})
                publish(
                    invoice.env,
                    "invoice.paid",
                    "fix.ar.invoice",
                    invoice.id,
                    {
                        "invoice": invoice.name,
                        "mushak_no": invoice.mushak_id.mushak_no,
                        "total_payable": invoice.total_payable,
                        "evidence": "receipts %s" % receipt_refs,
                    },
                )

    def write(self, vals):
        if not self.env.su:
            if {"receipt_id", "invoice_id", "company_id", "allocated_by", "allocated_at"} & set(
                vals
            ):
                raise UserError(
                    "An allocation applies one receipt to one invoice; remove it and allocate "
                    "again rather than re-pointing it."
                )
            if "amount" in vals and (vals.get("amount") or 0.0) <= 0:
                raise UserError("Allocation amount must be positive")
        receipts_before = self.receipt_id
        invoices_before = self.invoice_id
        result = super().write(vals)
        if "amount" in vals:
            self.invalidate_recordset()
            self._fix_check_totals(receipts_before | self.receipt_id, invoices_before)
            paid_short = self.invoice_id.filtered(
                lambda i: i.state == "paid" and i.amount_residual > 0.005
            )
            if paid_short:
                raise UserError(
                    "Invoice %s is paid on this allocation; reduce it only by reversing the "
                    "payment, not by editing the evidence." % ", ".join(paid_short.mapped("name"))
                )
            self._fix_flip_paid()
        return result

    def unlink(self):
        for rec in self:
            if rec.invoice_id.state == "paid":
                raise UserError(
                    "Invoice %s is paid on this allocation — reverse via credit note "
                    "or write-off, not by deleting evidence" % rec.invoice_id.name
                )
        return super().unlink()


# ---------------------------------------------------------------------------
# A5 — credit control (FR-ARB-030/031)
# ---------------------------------------------------------------------------
class FixCreditProfile(models.Model):
    """Per-customer credit terms, limits and holds (FR-ARB-030). A hold
    blocks new invoice generation for the customer; blocking M01/M08 order
    intake is a cross-module change labelled porting phase."""

    _name = "fix.credit.profile"
    _description = "Customer Credit Profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True, ondelete="restrict"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    credit_limit = fields.Monetary(currency_field="currency_id", default=0.0)
    payment_terms_days = fields.Integer(
        default=30, required=True, help="Days from invoice to due date (kills hardcoded net-30)"
    )
    credit_hold = fields.Boolean(tracking=True)
    hold_reason = fields.Char(tracking=True)
    hold_by = fields.Many2one("res.users", string="Hold Changed By", readonly=True, copy=False)
    hold_date = fields.Datetime(string="Hold Changed On", readonly=True, copy=False)
    exposure = fields.Monetary(
        compute="_compute_exposure",
        store=True,
        currency_field="currency_id",
        help="Open issued residuals + confirmed-but-unapplied receipts never net here (receipts already reduced AR at confirm)",
    )
    over_limit = fields.Boolean(compute="_compute_exposure", store=True)

    _customer_unique = models.Constraint(
        "UNIQUE (customer_id, company_id)", "One credit profile per customer per company"
    )

    @api.depends("credit_limit", "customer_id")
    def _compute_exposure(self):
        Invoice = self.env["fix.ar.invoice"]
        for rec in self:
            open_residuals = Invoice.search(
                [
                    ("customer_id", "=", rec.customer_id.id),
                    ("state", "=", "issued"),
                    ("company_id", "=", rec.company_id.id),
                ]
            )
            rec.exposure = sum(open_residuals.mapped("amount_residual"))
            rec.over_limit = bool(rec.credit_limit) and rec.exposure > rec.credit_limit

    HOLD_STAMPS = ("hold_by", "hold_date", "hold_placed_by_id")

    hold_placed_by_id = fields.Many2one(
        "res.users", string="Hold Placed By", readonly=True, copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            for vals in vals_list:
                if set(self.HOLD_STAMPS) & {k for k, v in vals.items() if v}:
                    raise UserError("Hold stamps are set by placing or releasing the hold.")
                if vals.get("credit_hold"):
                    vals["hold_placed_by_id"] = self.env.uid
                    vals["hold_by"] = self.env.uid
                    vals["hold_date"] = fields.Datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su and self.env.context.get("fix_credit_hold_toggle") is not _HOLD_TOKEN:
            if set(self.HOLD_STAMPS) & set(vals):
                raise UserError("Hold stamps are set by placing or releasing the hold.")
            if "credit_hold" in vals:
                if not vals["credit_hold"] and self.filtered("credit_hold"):
                    raise UserError(
                        "A credit hold is released only by an Accounting Administrator through "
                        "Release Hold (BRU-ARB-14), never by editing the profile."
                    )
                if vals["credit_hold"] and self.filtered(lambda r: not r.credit_hold):
                    vals = dict(
                        vals,
                        hold_placed_by_id=self.env.uid,
                        hold_by=self.env.uid,
                        hold_date=fields.Datetime.now(),
                    )
        return super().write(vals)

    def action_toggle_hold(self, reason=None):
        """Place or release a credit hold (FR-ARB-031). Placing one records
        the reason (the given one, the one already typed on the profile, or
        an explicit manual-hold note naming the user); both directions are
        stamped with who and when and logged in the chatter.

        A08 M20-12 (BRU-ARB-14): RELEASING needs a role senior to the one that
        raises the commitment — the Accounting Administrator — and never the
        person who placed the hold."""
        now = fields.Datetime.now()
        for rec in self:
            rec = rec.with_context(fix_credit_hold_toggle=_HOLD_TOKEN)
            if rec.credit_hold:
                if not self.env.su:
                    require_role(self.env, GROUP_ADMINISTRATOR, "Releasing a credit hold")
                    if rec.hold_placed_by_id == self.env.user:
                        raise UserError(
                            "Segregation of duties: you placed the hold on %s; another "
                            "Accounting Administrator releases it." % rec.customer_id.name
                        )
                rec.write(
                    {
                        "credit_hold": False,
                        "hold_reason": False,
                        "hold_by": self.env.user.id,
                        "hold_date": now,
                    }
                )
                rec.message_post(body="Credit hold released by %s" % self.env.user.name)
            else:
                why = (reason or rec.hold_reason or "").strip() or (
                    "Manual hold placed by %s" % self.env.user.name
                )
                require_role(self.env, GROUP_ACCOUNTANT, "Placing a credit hold")
                rec.write(
                    {
                        "credit_hold": True,
                        "hold_reason": why,
                        "hold_by": self.env.user.id,
                        "hold_date": now,
                        "hold_placed_by_id": self.env.user.id,
                    }
                )
                rec.message_post(body="Credit hold placed: %s" % why)


# ---------------------------------------------------------------------------
# A6 — disputes (FR-ARB-036)
# ---------------------------------------------------------------------------
DISPUTE_OUTCOMES = [
    ("upheld_credit", "Upheld — credit note issued"),
    ("partially_upheld", "Partially upheld"),
    ("rejected", "Rejected — invoice stands"),
    ("withdrawn", "Withdrawn by the customer"),
    ("payment_plan", "Settled by payment plan"),
]


class FixArDispute(models.Model):
    """A disputed amount on an invoice. An OPEN dispute suspends dunning for
    the disputed amount only — the undisputed remainder keeps dunning
    (FR-ARB-036)."""

    _name = "fix.ar.dispute"
    _description = "AR Dispute"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    invoice_id = fields.Many2one("fix.ar.invoice", required=True, ondelete="cascade", index=True)
    name = fields.Char(compute="_compute_name", string="Dispute")
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    amount_disputed = fields.Monetary(currency_field="currency_id", required=True)
    reason = fields.Char(required=True)
    state = fields.Selection(
        [("open", "Open"), ("resolved", "Resolved")], default="open", required=True, tracking=True
    )
    resolution_note = fields.Char()
    outcome_code = fields.Selection(
        DISPUTE_OUTCOMES,
        string="Outcome",
        readonly=True,
        copy=False,
        help="BRU-ARB-17: a dispute closes with an outcome code.",
    )
    resolved_by = fields.Many2one("res.users", readonly=True)
    resolved_at = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "outcome_code",
            "resolved_by",
            "resolved_at",
            "resolution_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "open" for r in self):
            locked |= {"invoice_id", "amount_disputed", "reason"}
        return locked

    @api.model
    def _fix_check_cap(self, invoices):
        """A08 M20-10: the open disputes of an invoice never exceed what is
        still open on it (23,000 was disputed on an 11,500 invoice)."""
        for invoice in invoices:
            disputed = sum(
                self.search([("invoice_id", "=", invoice.id), ("state", "=", "open")]).mapped(
                    "amount_disputed"
                )
            )
            if disputed > invoice.amount_residual + 0.005:
                raise UserError(
                    "Open disputes on invoice %s would total %.2f, above its open amount %.2f."
                    % (invoice.name, disputed, invoice.amount_residual)
                )

    def write(self, vals):
        if not self._fix_guard_open():
            touched = {"invoice_id", "amount_disputed", "reason"} & set(vals)
            if touched and self.filtered(lambda r: r.state != "open"):
                raise UserError("A resolved dispute is closed evidence and is not edited.")
            if "amount_disputed" in vals and (vals.get("amount_disputed") or 0.0) <= 0:
                raise UserError("Disputed amount must be positive")
        before = self.invoice_id
        result = super().write(vals)
        if {"amount_disputed", "invoice_id"} & set(vals):
            self._fix_check_cap(before | self.invoice_id)
        return result

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            invoice = self.env["fix.ar.invoice"].browse(vals.get("invoice_id"))
            if invoice.state not in ("issued", "paid"):
                raise UserError("Disputes apply to issued/paid invoices only")
            if vals.get("amount_disputed", 0) <= 0:
                raise UserError("Disputed amount must be positive")
            if vals.get("amount_disputed", 0) > invoice.total_payable + 0.005:
                raise UserError("Disputed amount exceeds the invoice total")
            vals["company_id"] = vals.get("company_id") or invoice.company_id.id
            vals["operating_unit_id"] = (
                vals.get("operating_unit_id") or invoice.operating_unit_id.id
            )
        disputes = super().create(vals_list)
        self._fix_check_cap(disputes.invoice_id)
        return disputes

    def action_resolve(self, note="", outcome_code=None):
        """BRU-ARB-17: close with an outcome code and a note, decided by an
        accountant other than the one who raised the dispute."""
        require_role(self.env, GROUP_ACCOUNTANT, "Resolving a dispute")
        if outcome_code not in dict(DISPUTE_OUTCOMES):
            raise UserError(
                "A dispute closes with an outcome code (BRU-ARB-17): one of %s"
                % ", ".join(dict(DISPUTE_OUTCOMES))
            )
        if not (note or "").strip():
            raise UserError("Record the resolution (what was decided and why)")
        for rec in self:
            if rec.state != "open":
                continue
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: you raised dispute %s; another person resolves it."
                    % rec.display_name
                )
            rec._guarded().write(
                {
                    "state": "resolved",
                    "outcome_code": outcome_code,
                    "resolution_note": (note or "")[:500],
                    "resolved_by": rec.env.user.id,
                    "resolved_at": fields.Datetime.now(),
                }
            )

    @api.depends("invoice_id.name")
    def _compute_name(self):
        for rec in self:
            rec.name = "Dispute #%s / %s" % (rec.id or "new", rec.invoice_id.name or "")

    # One button per outcome (BRU-ARB-17): the code is chosen, never typed.
    def action_resolve_upheld_credit(self, note=""):
        return self.action_resolve(note, outcome_code="upheld_credit")

    def action_resolve_partially_upheld(self, note=""):
        return self.action_resolve(note, outcome_code="partially_upheld")

    def action_resolve_rejected(self, note=""):
        return self.action_resolve(note, outcome_code="rejected")

    def action_resolve_withdrawn(self, note=""):
        return self.action_resolve(note, outcome_code="withdrawn")

    def action_resolve_payment_plan(self, note=""):
        return self.action_resolve(note, outcome_code="payment_plan")


# ---------------------------------------------------------------------------
# A7 — ageing snapshots (FR-ARB-029, the D365 point-in-time pattern)
# ---------------------------------------------------------------------------
class FixArAgingSnapshot(models.Model):
    """An immutable point-in-time AR ageing capture (FR-ARB-029). After
    capture the snapshot refuses writes/deletes — it is audit evidence, like
    M19's posting log."""

    _name = "fix.ar.aging.snapshot"
    _description = "AR Ageing Snapshot"
    _order = "as_of_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    as_of_date = fields.Date(required=True, default=fields.Date.today)
    state = fields.Selection(
        [("draft", "Draft"), ("captured", "Captured")], default="draft", required=True
    )
    captured_at = fields.Datetime(readonly=True)
    captured_by = fields.Many2one("res.users", readonly=True)
    line_ids = fields.One2many("fix.ar.aging.line", "snapshot_id", string="Customer Buckets")
    total_open = fields.Monetary(
        compute="_compute_totals", currency_field="currency_id", store=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )

    BUCKETS = ["current", "d1_30", "d31_60", "d61_90", "d90_plus"]

    @api.depends(
        "line_ids.current",
        "line_ids.d1_30",
        "line_ids.d31_60",
        "line_ids.d61_90",
        "line_ids.d90_plus",
    )
    def _compute_totals(self):
        for rec in self:
            rec.total_open = sum(
                sum(getattr(line, b) for b in self.BUCKETS) for line in rec.line_ids
            )

    def action_capture(self, as_of=None):
        """Capture per-customer buckets for every open issued invoice, aged
        as of `as_of` (backdated ageing supported, the D365 pattern)."""
        for rec in self:
            if rec.state == "captured":
                raise UserError("Snapshot already captured — take a new one instead")
            on = as_of or rec.as_of_date or fields.Date.today()
            rec.write({"as_of_date": on})
            per_customer = {}
            invoices = (
                self.env["fix.ar.invoice"]
                .search([("company_id", "=", rec.company_id.id), ("state", "=", "issued")])
                .filtered(lambda inv: inv.amount_residual > 0.005)
            )
            for inv in invoices:
                terms = inv._payment_terms_days()
                days_past_due = (on - inv.invoice_date).days - terms
                bucket = (
                    "current"
                    if days_past_due <= 0
                    else "d1_30"
                    if days_past_due <= 30
                    else "d31_60"
                    if days_past_due <= 60
                    else "d61_90"
                    if days_past_due <= 90
                    else "d90_plus"
                )
                slot = per_customer.setdefault(
                    inv.customer_id.id,
                    dict.fromkeys(self.BUCKETS, 0.0),
                )
                slot[bucket] += inv.amount_residual
            rec.line_ids = [
                (
                    0,
                    0,
                    dict({"customer_id": customer_id}, **amounts),
                )
                for customer_id, amounts in per_customer.items()
            ]
            rec.write(
                {
                    "state": "captured",
                    "captured_at": fields.Datetime.now(),
                    "captured_by": rec.env.user.id,
                }
            )

    def write(self, vals):
        for rec in self:
            if (
                rec.state == "captured"
                and not rec.env.context.get("force_edit")
                and any(k not in ("captured_at",) for k in vals)
            ):
                raise UserError(
                    "Captured ageing snapshots are immutable audit evidence (FR-ARB-029)"
                )
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state == "captured" and not rec.env.context.get("force_edit"):
                raise UserError(
                    "Captured ageing snapshots are immutable audit evidence (FR-ARB-029)"
                )
        return super().unlink()


class FixArAgingLine(models.Model):
    _name = "fix.ar.aging.line"
    _description = "AR Ageing Snapshot Line"
    _order = "snapshot_id desc, id desc"

    snapshot_id = fields.Many2one("fix.ar.aging.snapshot", required=True, ondelete="cascade")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    customer_id = fields.Many2one("res.partner", required=True, ondelete="restrict")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    current = fields.Monetary(currency_field="currency_id", default=0.0)
    d1_30 = fields.Monetary(currency_field="currency_id", default=0.0)
    d31_60 = fields.Monetary(currency_field="currency_id", default=0.0)
    d61_90 = fields.Monetary(currency_field="currency_id", default=0.0)
    d90_plus = fields.Monetary(currency_field="currency_id", default=0.0)


# ---------------------------------------------------------------------------
# A8 — payment links (FR-ARB-015; gateway integration is porting phase)
# ---------------------------------------------------------------------------
class FixArPaymentLink(models.Model):
    """A single-use payment link token for an invoice. Generation only —
    the bKash/Nagad/SSLCommerz checkout URL is porting phase (never
    fabricated)."""

    _name = "fix.ar.payment.link"
    _description = "AR Payment Link"
    _inherit = ["fix.guarded.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    invoice_id = fields.Many2one("fix.ar.invoice", required=True, ondelete="cascade", index=True)
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    amount = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        help="What the link collects: the invoice residual when the link is made "
        "(A08 M20-14: it asked the invoice total).",
    )
    token = fields.Char(
        default=lambda self: uuid.uuid4().hex, required=True, copy=False, index=True
    )
    expires_at = fields.Datetime(
        required=True,
        default=lambda self: fields.Datetime.now() + timedelta(hours=self._link_hours()),
    )
    state = fields.Selection(
        [("new", "New"), ("used", "Used"), ("expired", "Expired")],
        default="new",
        required=True,
    )
    used_at = fields.Datetime(readonly=True)
    gateway_note = fields.Char(
        default="Token only — bKash/Nagad/SSLCommerz checkout is porting phase"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"amount", "state", "used_at"}

    @api.model
    def _link_hours(self) -> float:
        return float_param(self.env, PARAM_LINK_HOURS, DEFAULT_LINK_HOURS)

    @api.model_create_multi
    def create(self, vals_list):
        now = fields.Datetime.now()
        limit = now + timedelta(hours=self._link_hours())
        for vals in vals_list:
            invoice = self.env["fix.ar.invoice"].browse(vals.get("invoice_id"))
            if invoice.state != "issued":
                raise UserError("Payment links attach to issued invoices only")
            if invoice.amount_residual <= 0.005:
                raise UserError("Invoice %s has nothing outstanding to collect" % invoice.name)
            expires = (
                fields.Datetime.to_datetime(vals["expires_at"]) if vals.get("expires_at") else limit
            )
            if expires <= now or expires > limit + timedelta(minutes=1):
                raise UserError(
                    "A payment link expires within %g hours of issue (%s)."
                    % (self._link_hours(), PARAM_LINK_HOURS)
                )
            existing = self.search(
                [("invoice_id", "=", invoice.id), ("state", "=", "new")], limit=1
            )
            if existing:
                raise UserError(
                    "Invoice %s already has an active link (%s)" % (invoice.name, existing.token)
                )
            vals["company_id"] = vals.get("company_id") or invoice.company_id.id
            vals["expires_at"] = expires
        links = super().create(vals_list)
        for link in links:
            link._guarded().write({"amount": link.invoice_id.amount_residual})
        return links

    def write(self, vals):
        if not self._fix_guard_open() and {"invoice_id", "expires_at", "token"} & set(vals):
            raise UserError("A payment link is fixed when made; let it expire and make a new one.")
        return super().write(vals)

    @api.model
    def _cron_expire(self):
        """Expire every new link past its expiry (FR-ARB-015)."""
        due = self.sudo().search(
            [("state", "=", "new"), ("expires_at", "<", fields.Datetime.now())]
        )
        due._guarded().write({"state": "expired"})
        return len(due)

    def is_expired(self) -> bool:
        self.ensure_one()
        return (
            self.state == "new"
            and bool(self.expires_at)
            and self.expires_at < fields.Datetime.now()
        )


# ---------------------------------------------------------------------------
# A8 — computed surfaces: customer statement + revenue leakage (pure functions)
# ---------------------------------------------------------------------------
def compute_customer_statement(env, customer_id, date_from: date, date_to: date) -> dict:
    """An honest open-item statement: opening balance, invoices, credit
    notes and receipts in the window, closing balance. Receipts reduce AR at
    confirm (not at allocation) — that is when the GL moves."""
    Invoice = env["fix.ar.invoice"]
    Receipt = env["fix.ar.receipt"]
    CreditNote = env["fix.credit.note"]

    def _invoices(before=None, window=None):
        domain = [
            ("customer_id", "=", customer_id),
            ("state", "in", ["issued", "paid", "credited"]),
        ]
        if before:
            domain.append(("invoice_date", "<", before))
        if window:
            domain += [("invoice_date", ">=", window[0]), ("invoice_date", "<=", window[1])]
        return Invoice.search(domain)

    def _receipts(before=None, window=None):
        domain = [("customer_id", "=", customer_id), ("state", "=", "confirmed")]
        if before:
            domain.append(("receipt_date", "<", before))
        if window:
            domain += [("receipt_date", ">=", window[0]), ("receipt_date", "<=", window[1])]
        return Receipt.search(domain)

    def _credits(before=None, window=None):
        issued = CreditNote.search(
            [("invoice_id.customer_id", "=", customer_id), ("state", "=", "issued")]
        ).filtered(lambda n: n.issued_at)
        result = []
        for note in issued:
            on = note.issued_at.date()
            if (before and on < before) or (window and window[0] <= on <= window[1]):
                result.append(note)
        return result

    opening = (
        sum(i.total_payable for i in _invoices(before=date_from))
        - sum(r.amount for r in _receipts(before=date_from))
        - sum(n.amount for n in _credits(before=date_from))
    )

    rows = []
    for inv in _invoices(window=(date_from, date_to)):
        rows.append(
            {
                "date": str(inv.invoice_date),
                "kind": "invoice",
                "ref": inv.name,
                "detail": "Mushak %s" % (inv.mushak_id.mushak_no or "—"),
                "charge": inv.total_payable,
            }
        )
    for note in _credits(window=(date_from, date_to)):
        rows.append(
            {
                "date": str(note.issued_at.date()),
                "kind": "credit",
                "ref": "CN %s" % note.id,
                "detail": note.reason_code,
                "charge": -note.amount,
            }
        )
    for rec in _receipts(window=(date_from, date_to)):
        rows.append(
            {
                "date": str(rec.receipt_date),
                "kind": "receipt",
                "ref": rec.name,
                "detail": rec.method,
                "charge": -rec.amount,
            }
        )
    rows.sort(key=lambda r: r["date"])
    closing = opening + sum(r["charge"] for r in rows)
    return {
        "customer_id": customer_id,
        "date_from": str(date_from),
        "date_to": str(date_to),
        "opening": round(opening, 2),
        "rows": rows,
        "closing": round(closing, 2),
        "basis": "invoices at issue, credit notes at issue, receipts at confirm (GL basis)",
    }


def compute_leakage(env, company_id=None) -> dict:
    """FR-ARB-043/044: delivered-but-unbilled work and aged billable events —
    the two places revenue silently dies."""
    Invoice = env["fix.ar.invoice"]
    domain = [("state", "=", "closed")]
    if company_id:
        domain.append(("company_id", "=", company_id))
    closed_orders = env["fix.service.order"].sudo().search(domain)
    invoiced_sources = set(
        Invoice.sudo().search([("source_model", "=", "fix.service.order")]).mapped("source_id")
    )
    unbilled = []
    today = fields.Date.today()
    for order in closed_orders:
        if order.id in invoiced_sources:
            continue
        marker = getattr(order, "closed_date", None) or order.write_date
        age_days = (
            (today - (marker.date() if isinstance(marker, datetime) else marker)).days
            if marker
            else 0
        )
        unbilled.append(
            {
                "order_id": order.id,
                "order": order.name,
                "customer": order.customer_id.name,
                "age_days": age_days,
                "escalation": "60+ days"
                if age_days > 60
                else "30+ days"
                if age_days > 30
                else "recent",
            }
        )
    unbilled.sort(key=lambda r: -r["age_days"])

    events_domain = [("state", "in", ["failed", "skipped"])]
    if company_id:
        events_domain.append(("company_id", "=", company_id))
    failed_events = []
    for ev in env["fix.billable.event"].sudo().search(events_domain):
        failed_events.append(
            {
                "event_id": ev.event_id[:13] + "…",
                "source": "%s/%s" % (ev.source_model, ev.source_id),
                "state": ev.state,
                "attempts": ev.attempts,
                "age_days": ev.age_days,
                "error": (ev.last_error or "")[:120],
            }
        )
    failed_events.sort(key=lambda r: -r["age_days"])
    return {
        "unbilled_closed_orders": unbilled,
        "failed_events": failed_events,
        "basis": "closed service orders without an invoice + billable events failed/skipped (never silently expired)",
    }
