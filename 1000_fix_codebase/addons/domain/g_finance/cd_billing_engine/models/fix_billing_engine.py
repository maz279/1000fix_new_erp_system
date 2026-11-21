# cd_billing_engine — M20 Accounts Receivable core (P06-M03, CD-M20-01).
#
# The heart is T02: automatic invoice generation from a CLOSED service
# order within 5 seconds (NFR-040, G3-01 "100% of invoices generated
# automatically from closed jobs"). Implementation: the service order's
# closed event (Phase 4 already emits it) is consumed here; invoice,
# determination and Mushak register rows are written in ONE transaction
# (P06-M02-T08 atomic posting).
#
# Call direction (AR-006 section 4.1): this module CALLS M51's
# determination synchronously and CONSUMES nothing back; M50's bank/cash
# events are consumed for receipts — M20 never calls M50 synchronously
# (pair 6).
#
# A08 remediation (B4, 4 Nov 2026), M20-1..M20-15:
#   * every workflow field (invoice / credit note state, numbers, stamps, GL
#     links) is guarded: it changes only through its action (F3, M20-2);
#   * VAT on every user-entered line is M51's determination, never typed
#     (BRU-ARB-03/04, M20-8); an issued invoice and its lines are frozen;
#   * a manual invoice is issued by a second person (BRU-ARB-02); cancelling
#     an issued invoice is an Accounting Administrator's act (FR-ARB-011);
#   * credit notes: never auto-approved; the approver is never the raiser;
#     <= the direct band a second Accountant, above it the Accounting
#     Administrator through M63 (fix.finance.dofa.mixin); total credits never
#     exceed the invoice; the amount is frozen at submit (S3, M20-1/-3/-7);
#   * write-offs are requested, approved on the same ladder and written off
#     against the IFRS 9 loss allowance first (fix.ar.writeoff, M20-6);
#   * dunning suppressions are kept with who / why / until (BRU-ARB-16);
#   * consolidated bills take issued invoices only (M20-14);
#   * the per-company sequences are copied as the system (M20-9).
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

import psycopg2.errors
from odoo import api, fields, models
from odoo.addons.cd_catalogue.models.fix_commercial_line import LINE_TYPES
from odoo.addons.cd_tax_engine_bd.models import tax_logic
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_finance_approval import (
    GROUP_ACCOUNTANT,
    GROUP_ADMINISTRATOR,
    float_param,
    require_role,
)

TWO_PLACES = Decimal("0.01")

# Credit-note and write-off ladders (spec 05-04 §7: credit note <= BDT 10,000
# Finance Officer, above it Finance Manager). The CFO band is off (0) until
# the business rules it (A08 report §7, B3); the M30 DOFA ladder overrides.
PARAM_CREDIT_DIRECT = "cd_billing_engine.credit_note_direct_limit"
PARAM_CREDIT_CFO = "cd_billing_engine.credit_note_cfo_limit"
PARAM_WRITEOFF_DIRECT = "cd_billing_engine.writeoff_direct_limit"
PARAM_WRITEOFF_CFO = "cd_billing_engine.writeoff_cfo_limit"
DEFAULT_DIRECT_LIMIT = 10000.0
# Days a payment-plan / strategic dunning suppression lasts when no end is given.
PARAM_SUPPRESSION_DAYS = "cd_billing_engine.dunning_suppression_days"
DEFAULT_SUPPRESSION_DAYS = 30

# Invoice sources whose lines come from a system determination (not typed).
SYSTEM_SOURCES = ("fix.service.order",)


def allocate_discount(grosses: list[Decimal], discount: Decimal) -> list[Decimal]:
    """Spread an estimate's HEADER discount over its lines, pro rata to each
    line's gross, at 2dp half-up. The rounding residue lands on the largest
    line so the shares sum EXACTLY to the discount (no paisa created or
    lost between the estimate and the Mushak 6.3)."""
    discount = discount.quantize(TWO_PLACES, ROUND_HALF_UP)
    total = sum(grosses, Decimal("0"))
    if discount <= 0:
        return [Decimal("0.00") for _ in grosses]
    if discount > total:
        raise UserError(
            "The estimate discount (%s) exceeds the invoiced lines (%s)" % (discount, total)
        )
    shares = [(g * discount / total).quantize(TWO_PLACES, ROUND_HALF_UP) for g in grosses]
    largest = max(range(len(grosses)), key=lambda i: grosses[i])
    shares[largest] += discount - sum(shares, Decimal("0"))
    return shares


def dhaka_date(moment):
    """The Asia/Dhaka calendar day of a UTC datetime (or a datetime string)."""
    import pytz

    moment = fields.Datetime.to_datetime(moment) or fields.Datetime.now()
    return moment.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone("Asia/Dhaka")).date()


def m51_determine(env, lines, on_date=None, company=None):
    """M51's sales VAT determination (B5 contract, A08 M51-5): the Tax Rate
    Master in force and the tariff rows. Falls back to the pure engine only
    where the M51 service is not installed."""
    Treatment = env["fix.vat.treatment"]
    try:
        if hasattr(Treatment, "_fix_determine_tax"):
            return Treatment._fix_determine_tax(lines, on_date=on_date, company=company)
        return tax_logic.determine_tax(lines)
    except tax_logic.DeterminationError as exc:
        raise UserError("VAT determination (M51) refused: %s" % exc) from exc


def ar_lock_covering(env, company, on_date):
    """C8 (owner decision 12 Nov 2026, D2-11): the lock date that covers
    `on_date` for a statutory AR invoice, or None while the date is open.

    The same source the GL uses (account.move._get_violated_lock_dates via
    _fix_check_not_in_closed_period): the company's Global Lock Date that the
    period close sets, plus the sales, tax and hard locks, honouring an
    approved reopen exception. Read with the invoice journal (C11), so a
    sales lock date counts too."""
    from .fix_ar_engine import _ar_invoice_journal

    if not on_date:
        return None
    journal = _ar_invoice_journal(env, company)
    violated = company._get_violated_lock_dates(fields.Date.to_date(on_date), True, journal)
    return max(lock for lock, _field in violated) if violated else None


def ar_first_open_date(env, company, on_date):
    """`on_date`, or the first day after the lock that covers it (E3-04)."""
    lock = ar_lock_covering(env, company, on_date)
    return lock + timedelta(days=1) if lock else fields.Date.to_date(on_date)


def _issue_mushak_row(env, vals):
    """Write a Mushak 6.3 row through M51's issuing service."""
    Register = env["fix.mushak.register"]
    if hasattr(Register, "_fix_issue_register_row"):
        return Register._fix_issue_register_row(vals)
    return Register.sudo().create(vals)


class FixArInvoice(models.Model):
    """A customer invoice in the AR engine, feeding Odoo account.move.

    Kept as an explicit M20 record (not a bare account.move) because the
    Mushak pairing, the closed-job source and the dunning ladder are M20
    concerns account.move must not carry."""

    _name = "fix.ar.invoice"
    _description = "AR Invoice"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "invoice_date desc, id desc"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _source_key_unique = models.Constraint(
        "UNIQUE (source_model, source_id)",
        "One invoice per source document — the auto-generation guard",
    )
    _source_ref_unique = models.Constraint(
        "UNIQUE (source_model, source_ref)",
        "One invoice per external source reference",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True)
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True, ondelete="restrict"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    source_model = fields.Char(
        string="Source Model", required=True, index=True, help="e.g. fix.service.order"
    )
    source_id = fields.Integer(string="Source ID", required=True, index=True)
    source_ref = fields.Char(
        string="Source Reference",
        index=True,
        copy=False,
        help="The external source reference (contract billing line, OEM claim, "
        "subscription charge) of an invoice raised through _fix_draft_invoice_from_source.",
    )
    invoice_date = fields.Date(default=fields.Date.today, required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("issued", "Issued"),
            ("paid", "Paid"),
            ("credited", "Credited"),
            ("written_off", "Written Off"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many("fix.ar.invoice.line", "invoice_id", string="Lines")
    # AS-10: monetary only
    taxable_amount = fields.Monetary(
        string="Taxable Value", currency_field="currency_id", compute="_compute_totals", store=True
    )
    vat_amount = fields.Monetary(
        string="VAT", currency_field="currency_id", compute="_compute_totals", store=True
    )
    loyalty_points_redeemed = fields.Integer(string="Loyalty Points Redeemed", default=0)
    loyalty_discount_amount = fields.Monetary(
        string="Loyalty Discount", currency_field="currency_id", default=0.0
    )
    total_payable = fields.Monetary(
        string="Total Payable", currency_field="currency_id", compute="_compute_totals", store=True
    )
    mushak_id = fields.Many2one(
        "fix.mushak.register",
        string="Mushak 6.3",
        readonly=True,
        index=True,
        help="Written in the same transaction (atomic posting)",
    )
    generated_at = fields.Datetime(readonly=True)
    generation_seconds = fields.Float(
        readonly=True, help="Closed-event to invoice duration — NFR-040 (5s)"
    )
    # --- M20 engine depth (CD-M20-02) -------------------------------------
    name = fields.Char(
        string="Invoice No",
        default="New",
        copy=False,
        readonly=True,
        index=True,
        help="Gapless per-company sequence drawn at issue (FR-ARB-005)",
    )
    manual_reason = fields.Char(
        readonly=True, help="FR-ARB-010: mandatory reason for manual invoices"
    )
    posted_move_id = fields.Many2one(
        "account.move",
        string="GL Move",
        readonly=True,
        copy=False,
        help="The AR posting through M19's post_with_dimensions (source='ar')",
    )
    gl_note = fields.Char(
        readonly=True,
        copy=False,
        help="Honest skip reason when the GL posting could not run",
    )
    paid_date = fields.Date(readonly=True)
    allocation_ids = fields.One2many("fix.ar.allocation", "invoice_id", string="Allocations")
    credit_note_ids = fields.One2many("fix.credit.note", "invoice_id", string="Credit Notes")
    vds_certificate_ids = fields.One2many(
        "fix.vds.certificate.received", "invoice_id", string="VDS Certificates (Mushak 6.6)"
    )
    tds_certificate_ids = fields.One2many(
        "fix.tds.certificate.received", "invoice_id", string="TDS / AIT Certificates"
    )
    writeoff_ids = fields.One2many("fix.ar.writeoff", "invoice_id", string="Write-offs")
    # A08 B4: who issued / cancelled, and the credit account of a system invoice
    issued_by_id = fields.Many2one("res.users", string="Issued By", readonly=True, copy=False)
    cancelled_by_id = fields.Many2one(
        "res.users", string="Cancellation Approved By", readonly=True, copy=False
    )
    cancel_reason = fields.Char(string="Cancellation Reason", readonly=True, copy=False)
    revenue_account_id = fields.Many2one(
        "account.account",
        string="Credit Account (system invoice)",
        readonly=True,
        copy=False,
        help="Set by the AR invoice API for a non-service supply (e.g. an asset "
        "disposal): the issue credits this account instead of service revenue.",
    )
    amount_paid = fields.Monetary(
        string="Paid",
        currency_field="currency_id",
        compute="_compute_payment",
        store=True,
        help="Receipt allocations applied (the evidence path)",
    )
    credited_amount = fields.Monetary(
        string="Credited",
        currency_field="currency_id",
        compute="_compute_payment",
        store=True,
    )
    vds_settled_amount = fields.Monetary(
        string="VDS Settled",
        currency_field="currency_id",
        compute="_compute_payment",
        store=True,
        help="VAT the customer deducted at source and certified on a Mushak 6.6 that "
        "finance has verified and settled against this invoice",
    )
    tds_settled_amount = fields.Monetary(
        string="TDS Settled",
        currency_field="currency_id",
        compute="_compute_payment",
        store=True,
        help="Income tax the customer deducted at source (ITA 2023 s.89/s.90) and certified, "
        "verified and settled against this invoice as advance income tax",
    )
    written_off_amount = fields.Monetary(
        string="Written Off",
        currency_field="currency_id",
        compute="_compute_payment",
        store=True,
    )
    amount_residual = fields.Monetary(
        string="Residual",
        currency_field="currency_id",
        compute="_compute_payment",
        store=True,
    )

    INVOICE_GUARDED = {
        "state",
        "name",
        "mushak_id",
        "posted_move_id",
        "gl_note",
        "paid_date",
        "generated_at",
        "generation_seconds",
        "issued_by_id",
        "cancelled_by_id",
        "cancel_reason",
        "revenue_account_id",
    }
    # Frozen once the invoice is issued (Mushak 6.3 and GL carry them).
    INVOICE_LOCKED = (
        "customer_id",
        "company_id",
        "operating_unit_id",
        "branch_id",
        "currency_id",
        "invoice_date",
        "loyalty_points_redeemed",
        "loyalty_discount_amount",
        "manual_reason",
        "source_model",
        "source_id",
        "source_ref",
        "line_ids",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.INVOICE_GUARDED

    def _fix_mushak_buyer(self):
        """(name, BIN) of the buyer as the Mushak 6.3 states them."""
        self.ensure_one()
        return self.customer_id.name, self.customer_id.vat or ""

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.INVOICE_LOCKED)
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            touched = set(self.INVOICE_LOCKED) & set(vals)
            if touched and self.filtered(lambda r: r.state != "draft"):
                raise UserError(
                    "An issued invoice is frozen (its Mushak 6.3 and GL entry carry %s): "
                    "correct it with a credit note or cancel it." % ", ".join(sorted(touched))
                )
        return super().write(vals)

    @api.depends("line_ids.taxable_amount", "line_ids.vat_amount", "loyalty_discount_amount")
    def _compute_totals(self):
        for inv in self:
            inv.taxable_amount = sum(inv.line_ids.mapped("taxable_amount"))
            inv.vat_amount = sum(inv.line_ids.mapped("vat_amount"))
            subtotal_vat = inv.taxable_amount + inv.vat_amount
            inv.total_payable = max(0.0, subtotal_vat - (inv.loyalty_discount_amount or 0.0))

    @api.depends(
        "total_payable",
        "allocation_ids.amount",
        "credit_note_ids.amount",
        "credit_note_ids.state",
        "vds_certificate_ids.vds_amount",
        "vds_certificate_ids.state",
        "tds_certificate_ids.tds_amount",
        "tds_certificate_ids.state",
        "writeoff_ids.amount",
        "writeoff_ids.state",
    )
    def _compute_payment(self):
        for inv in self:
            inv.amount_paid = sum(inv.allocation_ids.mapped("amount"))
            inv.credited_amount = sum(
                inv.credit_note_ids.filtered(lambda n: n.state == "issued").mapped("amount")
            )
            inv.vds_settled_amount = sum(
                inv.vds_certificate_ids.filtered(
                    lambda c: c.state in ("settled", "claimed")
                ).mapped("vds_amount")
            )
            inv.tds_settled_amount = sum(
                inv.tds_certificate_ids.filtered(lambda c: c.state == "settled").mapped(
                    "tds_amount"
                )
            )
            inv.written_off_amount = sum(
                inv.writeoff_ids.filtered(lambda w: w.state == "posted").mapped("amount")
            )
            inv.amount_residual = max(inv._raw_residual(), 0.0)

    def _raw_residual(self) -> float:
        """Total less every settlement document, NOT clamped at zero: a
        negative figure is an over-settlement the allocation check refuses."""
        self.ensure_one()
        paid = sum(self.allocation_ids.mapped("amount"))
        credited = sum(
            self.credit_note_ids.filtered(lambda n: n.state == "issued").mapped("amount")
        )
        vds = sum(
            self.vds_certificate_ids.filtered(lambda c: c.state in ("settled", "claimed")).mapped(
                "vds_amount"
            )
        )
        tds = sum(
            self.tds_certificate_ids.filtered(lambda c: c.state == "settled").mapped("tds_amount")
        )
        written = sum(self.writeoff_ids.filtered(lambda w: w.state == "posted").mapped("amount"))
        return self.total_payable - paid - credited - vds - tds - written

    # Invoices billed for a subscription / AMC cycle charge are a CONTRACT
    # LIABILITY until the performance obligations are satisfied (IFRS 15):
    # their issue credits deferred revenue, and M53's recognition run moves
    # it to revenue. Every other invoice credits revenue at issue.
    # fix.contract.billing.period (A04 C10) is the same shape: the contract's
    # in-force term billed period by period.
    DEFERRED_SOURCES = ("fix.subscription.charge", "fix.contract.billing.period")

    def _revenue_role(self) -> str:
        self.ensure_one()
        return "deferred_revenue" if self.source_model in self.DEFERRED_SOURCES else "revenue"

    def _revenue_account(self):
        """The account the issue credits: the API's explicit account, else the role's."""
        from .fix_ar_engine import _ar_account

        self.ensure_one()
        if self.revenue_account_id:
            return self.revenue_account_id
        return _ar_account(self.env, self.company_id, self._revenue_role())

    # ------------------------------------------------------------------
    # M20 engine depth: terms, credit holds, GL posting, lifecycle actions
    # ------------------------------------------------------------------
    def _payment_terms_days(self) -> int:
        """The customer's terms from their credit profile (default net-30 —
        the value that used to be hardcoded in the ageing compute)."""
        self.ensure_one()
        profile = (
            self.env["fix.credit.profile"]
            .sudo()
            .search(
                [
                    ("customer_id", "=", self.customer_id.id),
                    ("company_id", "=", self.company_id.id),
                ],
                limit=1,
            )
        )
        return profile.payment_terms_days if profile else 30

    def _credit_hold_check(self):
        """FR-ARB-031: a held customer blocks new invoicing. Blocking M01/M08
        order intake is a cross-module change (porting phase)."""
        for inv in self:
            self._credit_hold_for(inv.customer_id, inv.company_id)

    @api.model
    def _credit_hold_for(self, customer, company):
        profile = (
            self.env["fix.credit.profile"]
            .sudo()
            .search(
                [
                    ("customer_id", "=", customer.id),
                    ("company_id", "=", company.id),
                    ("credit_hold", "=", True),
                ],
                limit=1,
            )
        )
        if profile:
            raise UserError(
                "Credit hold on %s (%s) — invoicing blocked (FR-ARB-031)"
                % (customer.name, profile.hold_reason or "no reason recorded")
            )

    def _ar_posting_dims(self, branch_id=None, operating_unit_id=None):
        """Dimensions for every AR-family GL posting: the branch and operating
        unit, plus the configured default cost centre and business line
        (COA-03 may require any of them per account). Defaults come from
        config params so each deployment sets its own; postings never invent
        values beyond these configured defaults.

        A04 ERP audit M08-F4 / M38-F18: the operating unit was dropped, so
        M19 fell back to the company's FIRST unit ("Main Operating Unit") for
        every contract, quotation and storefront invoice. The unit now comes
        from, in order: the branch's own unit (M19 refuses a branch under
        another unit), an explicit `operating_unit_id`, and the invoice's own
        unit when this is called on one invoice."""
        param = self.env["ir.config_parameter"].sudo().get_param
        invoice = self if len(self) == 1 and "operating_unit_id" in self._fields else None
        if not branch_id and invoice is not None and "branch_id" in self._fields:
            branch_id = invoice.branch_id.id or None
        branch = self.env["fix.branch"].sudo().browse(branch_id or []).exists()
        ou_id = branch.operating_unit_id.id if branch else False
        if not ou_id:
            ou_id = operating_unit_id or (invoice.operating_unit_id.id if invoice else False)
        dims = {
            "branch_id": branch_id or False,
            "cost_centre": param("cd_billing_engine.default_cost_centre") or "CORP",
            "business_line": param("cd_billing_engine.default_business_line") or "RETAIL",
        }
        if ou_id:
            dims["operating_unit_id"] = ou_id
        return dims

    INVOICE_SEQUENCE_CODE = "fix.ar.invoice"

    @api.model
    def _company_sequence(self, code, template_xmlid, label, company, missing):
        """The company's own copy of a module sequence, made as the system:
        the template copy needs ir.sequence write rights an accountant does
        not hold (A08 M20-9 — the first invoice of a company was refused)."""
        Sequence = self.env["ir.sequence"].sudo()
        seq = Sequence.search([("code", "=", code), ("company_id", "=", company.id)], limit=1)
        if not seq:
            template = self.env.ref(template_xmlid, raise_if_not_found=False)
            if not template:
                raise UserError(missing)
            seq = template.sudo().copy(
                {
                    "name": "%s — %s" % (label, company.name),
                    "company_id": company.id,
                    "date_range_ids": [],
                }
            )
        return seq

    @api.model
    def _invoice_sequence(self, company):
        """The company's own invoice-number sequence — copied once from the
        module template (the Mushak pattern, without fiscal-year ranges:
        FR-ARB-005 gapless per entity)."""
        return self._company_sequence(
            self.INVOICE_SEQUENCE_CODE,
            "cd_billing_engine.seq_fix_ar_invoice",
            "AR Invoice No",
            company,
            "The invoice numbering sequence is missing — upgrade cd_billing_engine.",
        )

    # A04 ERP audit X10: how long an issue waits for a concurrent issue of the
    # same company to commit before it gives up (a PostgreSQL interval).
    INVOICE_SEQUENCE_LOCK_TIMEOUT = "15s"

    def _next_invoice_no(self) -> str:
        """The next gapless number. A04 ERP audit X10: Odoo's no_gap sequence
        takes its row with FOR UPDATE NOWAIT, so the second of two concurrent
        payment confirmations failed outright. The row is now taken first with
        a WAITING lock (bounded by a lock timeout); the NOWAIT that follows in
        the same transaction finds the lock already held and succeeds."""
        self.ensure_one()
        seq = self._invoice_sequence(self.company_id)
        cr = self.env.cr
        cr.execute("SHOW lock_timeout")
        previous = cr.fetchone()[0]
        cr.execute("SET LOCAL lock_timeout = %s", (self.INVOICE_SEQUENCE_LOCK_TIMEOUT,))
        try:
            cr.execute("SELECT id FROM ir_sequence WHERE id = %s FOR UPDATE", (seq.id,))
        except psycopg2.errors.LockNotAvailable:
            raise UserError(
                "Another invoice of %s is being numbered and did not finish within %s: "
                "try again." % (self.company_id.name, self.INVOICE_SEQUENCE_LOCK_TIMEOUT)
            ) from None
        cr.execute("SET LOCAL lock_timeout = %s", (previous,))
        return seq.next_by_id(sequence_date=self.invoice_date)

    def _post_issue_gl(self):
        """The issue posting through M19's hardened engine (source='ar'):
        Dr AR control / Cr Revenue / Cr VAT output, branch dimension on every
        line. Companies without the accounts/journal SKIP with an honest
        gl_note — invoicing is never blocked by GL configuration."""
        from .fix_ar_engine import _ar_account, _ar_invoice_journal, _post_ar_move

        for inv in self:
            if inv.total_payable <= 0.005:
                inv._guarded().write({"gl_note": "Zero-total invoice — no GL effect"})
                continue
            company = inv.company_id
            ar = _ar_account(inv.env, company, "ar")
            revenue = inv._revenue_account()
            vat = _ar_account(inv.env, company, "vat_output")
            if not (ar and revenue and vat):
                inv._guarded().write(
                    {
                        "gl_note": "GL not posted: AR/revenue/VAT account unconfigured for %s"
                        % company.name
                    }
                )
                continue
            # loyalty reduces revenue; if it ever exceeded the taxable value,
            # the VAT credit is reduced rather than inventing a negative line
            vat_credit = inv.vat_amount
            revenue_credit = inv.total_payable - vat_credit
            if revenue_credit < 0:
                vat_credit = inv.total_payable
                revenue_credit = 0.0
            _dims = inv._ar_posting_dims(inv.branch_id.id)
            dims = dict.fromkeys(range(3), _dims)
            move, note = _post_ar_move(
                inv.env,
                company,
                inv.invoice_date,
                "INV %s — %s (Mushak %s)"
                % (inv.name, inv.customer_id.name, inv.mushak_id.mushak_no or "—"),
                [
                    (
                        ar.id,
                        "AR %s" % inv.customer_id.name,
                        inv.total_payable,
                        0.0,
                        inv.customer_id.id,
                    ),
                    (
                        revenue.id,
                        "Contract liability (deferred revenue)"
                        if inv._revenue_role() == "deferred_revenue"
                        else "Service revenue",
                        0.0,
                        revenue_credit,
                        False,
                    ),
                    (
                        vat.id,
                        "VAT output 15%% (Mushak %s)" % (inv.mushak_id.mushak_no or "—"),
                        0.0,
                        vat_credit,
                        False,
                    ),
                ],
                dims,
                source="ar",
                # C11: the Sales journal, not the first general journal
                journal=_ar_invoice_journal(inv.env, company),
            )
            inv._guarded().write(
                {"posted_move_id": move.id if move else False, "gl_note": note or False}
            )
            if move and inv.mushak_id:
                # T08: the register row is marked posted only with its GL entry
                mushak = inv.mushak_id.sudo()
                if hasattr(mushak, "_fix_mark_posted"):
                    mushak._fix_mark_posted(move)
                else:
                    mushak.write({"posted": True})

    def _post_reversal_gl(self, label, debit_lines, credit_lines, journal=None):
        """A mirror posting for cancellations/write-offs; refuses (never
        skips) when the posting accounts are missing — these are finance
        actions, the GL IS the point. `journal`: the cancellation passes the
        invoice journal (C11); a write-off keeps the general journal."""
        from .fix_ar_engine import _ar_journal, _post_ar_move

        self.ensure_one()
        journal = journal or _ar_journal(self.env, self.company_id)
        if not journal:
            raise UserError("Posting refused: no general journal for %s" % self.company_id.name)
        missing = [role for role, acc, *_rest in debit_lines + credit_lines if not acc]
        if missing:
            raise UserError(
                "Posting refused: account role(s) %s unconfigured for %s"
                % (", ".join(missing), self.company_id.name)
            )
        _dims = self._ar_posting_dims(self.branch_id.id)
        dims = dict.fromkeys(range(len(debit_lines) + len(credit_lines)), _dims)
        lines = [
            (acc.id, label, amount, 0.0, partner or False)
            for role, acc, amount, partner in debit_lines
        ] + [
            (acc.id, label, 0.0, amount, partner or False)
            for role, acc, amount, partner in credit_lines
        ]
        # X5-10: the Dhaka business day (UTC "today" put a 00:00-06:00 Dhaka
        # cancellation or write-off into the previous day, and at a month end
        # into the previous period)
        move, note = _post_ar_move(
            self.env,
            self.company_id,
            dhaka_date(fields.Datetime.now()),
            label,
            lines,
            dims,
            source="ar",
            journal=journal,
        )
        if not move:
            raise UserError("Posting refused: %s" % (note or "engine refused the move"))
        return move

    def action_cancel(self, reason=""):
        """FR-ARB-011: unpaid invoices only, approved reason, number
        retained; the GL mirror is posted when the issue was posted.

        A08 M20-8 (spec state table "Finance Manager"): cancelling an ISSUED
        invoice is decided by an Accounting Administrator who neither raised
        nor issued it. A draft (no number, no Mushak, no GL) may be dropped
        by its maker."""
        from .fix_ar_engine import _ar_account, _ar_invoice_journal

        for inv in self:
            if inv.state not in ("draft", "issued"):
                raise UserError("Only draft/issued invoices can be cancelled")
            if (
                inv.amount_paid > 0.005
                or inv.credited_amount > 0.005
                or inv.vds_settled_amount > 0.005
                or inv.tds_settled_amount > 0.005
                or inv.written_off_amount > 0.005
            ):
                raise UserError(
                    "Paid/credited invoices cannot be cancelled — issue a credit note instead"
                )
            if not (reason or "").strip():
                raise UserError("A cancellation reason is required (FR-ARB-011)")
            if inv.state == "issued" and not self.env.su:
                require_role(self.env, GROUP_ADMINISTRATOR, "Cancelling an issued invoice")
                if self.env.user in (inv.create_uid | inv.issued_by_id):
                    raise UserError(
                        "Segregation of duties: you raised or issued invoice %s; another "
                        "Accounting Administrator approves its cancellation." % inv.name
                    )
            if inv.posted_move_id:
                ar = _ar_account(inv.env, inv.company_id, "ar")
                revenue = inv._revenue_account()
                vat = _ar_account(inv.env, inv.company_id, "vat_output")
                vat_credit = min(inv.vat_amount, inv.total_payable)
                revenue_credit = inv.total_payable - vat_credit
                inv._post_reversal_gl(
                    "CANCEL INV %s — %s" % (inv.name, reason),
                    [
                        (inv._revenue_role(), revenue, revenue_credit, False),
                        ("vat_output", vat, vat_credit, False),
                    ],
                    [("ar", ar, inv.total_payable, inv.customer_id.id)],
                    # C11: the cancellation reverses the issue on the Sales journal
                    journal=_ar_invoice_journal(inv.env, inv.company_id),
                )
            inv._guarded().write(
                {
                    "state": "cancelled",
                    "cancel_reason": reason[:500],
                    "cancelled_by_id": self.env.uid,
                }
            )
            publish(
                inv.env,
                "invoice.cancelled",
                "fix.ar.invoice",
                inv.id,
                {"invoice": inv.name, "reason": reason[:500]},
            )

    def action_write_off(self, reason="", recovery_history=""):
        """FR-ARB-041 / BRU-ARB-12: REQUEST the write-off of the open
        residual. The request (fix.ar.writeoff) is approved on the finance
        ladder by someone other than the requester and only then posts,
        against the IFRS 9 loss allowance first. Returns the request."""
        require_role(self.env, GROUP_ACCOUNTANT, "Requesting a write-off")
        if not (recovery_history or "").strip():
            raise UserError(
                "Record the recovery history: the collection steps taken before this write-off "
                "(BRU-ARB-12)."
            )
        WriteOff = self.env["fix.ar.writeoff"]
        requests = WriteOff
        for inv in self:
            requests |= WriteOff.create(
                {
                    "invoice_id": inv.id,
                    "reason": reason,
                    "recovery_history": recovery_history,
                }
            )
        requests.action_submit()
        return requests

    @api.model
    def create_manual_invoice(self, vals, lines, reason_code, overall_discount=0.0, source=None):
        """FR-ARB-010: the manual exception path. A reason code is mandatory
        and the invoice starts as draft — issue (Mushak + number + GL) is a
        separate deliberate step, by a second person (BRU-ARB-02). VAT on the
        lines is M51's determination: a typed VAT that differs is refused.

        Lines are priced by quantity x unit price less their discount %; an
        overall_discount (BDT) is spread over the lines pro rata before VAT,
        so the VAT base on the Mushak 6.3 is the discounted value.

        source: the customer document the invoice comes from (a proforma);
        the one-invoice-per-source key then guards it against a second
        conversion."""
        if not (reason_code or "").strip():
            raise UserError("Manual invoices need a reason code (FR-ARB-010)")
        vals = dict(vals)
        for key in ("source_model", "source_id", "line_ids"):
            vals.pop(key, None)
        if source:
            source.ensure_one()
            vals.update(
                {"source_model": source._name, "source_id": source.id, "manual_reason": reason_code}
            )
        else:
            vals.update({"source_model": "manual", "source_id": 0, "manual_reason": reason_code})
        lines = [dict(line) for line in lines]
        overall = Decimal(str(overall_discount or 0.0))
        if overall < 0:
            raise UserError("An overall discount cannot be negative.")
        if overall > 0:
            nets = []
            for line in lines:
                if "unit_price" in line:
                    gross = Decimal(str(line.get("quantity", 1.0) or 0.0)) * Decimal(
                        str(line.get("unit_price") or 0.0)
                    )
                    pct = Decimal(str(line.get("discount_pct") or 0.0))
                    net = gross - (gross * pct / 100).quantize(TWO_PLACES, ROUND_HALF_UP)
                else:
                    net = Decimal(str(line.get("taxable_amount") or 0.0))
                nets.append(net.quantize(TWO_PLACES, ROUND_HALF_UP))
            if overall > sum(nets, Decimal("0")):
                raise UserError(
                    "The overall discount (BDT %s) exceeds the lines (BDT %s)."
                    % (overall, sum(nets, Decimal("0")))
                )
            for line, share in zip(lines, allocate_discount(nets, overall), strict=True):
                if "unit_price" not in line:
                    line["unit_price"] = line.pop("taxable_amount", 0.0)
                    line.setdefault("quantity", 1.0)
                line["_extra_discount"] = float(share)
        invoice = self.create(vals)
        if not source:
            # keep the one-invoice-per-source guard meaningful for manual rows;
            # flushed immediately so a following manual create cannot race the key
            invoice.source_id = -invoice.id
        self.env.flush_all()
        for seq, line in enumerate(lines, start=1):
            line.setdefault("sequence", seq * 10)
            self.env["fix.ar.invoice.line"].create(dict(line, invoice_id=invoice.id))
        return invoice

    @api.model
    def _fix_ar_invoice_from_source(
        self,
        source,
        customer,
        lines,
        reason,
        credit_account=None,
        operating_unit=None,
        branch=None,
        invoice_date=None,
        issue=True,
    ):
        """CONTRACT (B4 -> B5, A08 P2 "disposal -> M20 invoice"): raise the AR
        invoice of an approved non-service supply (an asset disposal sale)
        and, by default, issue it: number, Mushak 6.3 and GL in one go.

        source          the approved source record (one invoice per source);
        customer        res.partner billed;
        lines           [{"description", "taxable_amount", "vat_treatment_code"?,
                         "product_id"?}] — VAT is M51's determination;
        reason          why the invoice exists (the source's approval);
        credit_account  account.account the issue credits (e.g. disposal
                        proceeds clearing); empty = service revenue.
        Idempotent: a second call for the same source returns the invoice."""
        source.ensure_one()
        company = (
            source.company_id if "company_id" in source._fields else False
        ) or self.env.company
        ou = operating_unit or (
            source.operating_unit_id if "operating_unit_id" in source._fields else False
        )
        return self._fix_source_invoice(
            source._name,
            source.id,
            None,
            customer,
            lines,
            reason,
            company,
            credit_account=credit_account,
            operating_unit=ou,
            branch=branch,
            invoice_date=invoice_date,
            issue=issue,
        )

    @api.model
    def _fix_draft_invoice_from_source(
        self,
        source_model,
        source_ref,
        customer,
        lines,
        reason,
        company=None,
        operating_unit=None,
        branch=None,
        invoice_date=None,
        credit_account=None,
    ):
        """CONTRACT (B4 -> A04 bridge): a DRAFT AR invoice for an external
        source (contract billing, an OEM warranty claim, a subscription
        charge) identified by (source_model, source_ref). Idempotent: a second
        call for the same pair returns the existing invoice, whatever its
        state. VAT is the M51 determination; Finance issues the draft (number,
        Mushak 6.3, GL) by action_issue.

        lines: [{"description", "taxable_amount", "vat_treatment_code"?, "product_id"?}]"""
        source_ref = str(source_ref or "").strip()
        if not source_model or not source_ref or source_model == "manual":
            raise UserError("A source invoice names its source model and reference.")
        existing = self.sudo().search(
            [("source_model", "=", source_model), ("source_ref", "=", source_ref)], limit=1
        )
        if existing:
            return self.browse(existing.id)
        import zlib

        key = -(zlib.crc32(("%s|%s" % (source_model, source_ref)).encode()) & 0x7FFFFFFF) - 1
        return self._fix_source_invoice(
            source_model,
            key,
            source_ref,
            customer,
            lines,
            reason,
            company or self.env.company,
            credit_account=credit_account,
            operating_unit=operating_unit,
            branch=branch,
            invoice_date=invoice_date,
            issue=False,
        )

    @api.model
    def _fix_source_invoice(
        self,
        source_model,
        source_id,
        source_ref,
        customer,
        lines,
        reason,
        company,
        credit_account=None,
        operating_unit=None,
        branch=None,
        invoice_date=None,
        issue=True,
    ):
        Invoice = self.sudo()
        existing = Invoice.search(
            [("source_model", "=", source_model), ("source_id", "=", source_id)], limit=1
        )
        if existing:
            return self.browse(existing.id)
        if not lines:
            raise UserError("The source invoice needs at least one line")
        if not (reason or "").strip():
            raise UserError("State why the invoice is raised (the source approval)")
        ou = operating_unit or self.env["operating.unit"].sudo().search(
            [("company_id", "=", company.id)], limit=1
        )
        if not ou:
            raise UserError("Company %s has no operating unit to invoice from" % company.name)
        invoice = Invoice._guarded().create(
            {
                "company_id": company.id,
                "operating_unit_id": ou.id,
                "branch_id": branch.id if branch else False,
                "customer_id": customer.id,
                "source_model": source_model,
                "source_id": source_id,
                "source_ref": source_ref or False,
                "invoice_date": invoice_date or fields.Date.context_today(self),
                "manual_reason": reason.strip()[:250],
                "revenue_account_id": credit_account.id if credit_account else False,
            }
        )
        Treatment = self.env["fix.vat.treatment"].sudo()
        for line in lines:
            vals = {
                "invoice_id": invoice.id,
                "description": line.get("description") or reason,
                "taxable_amount": line["taxable_amount"],
                "product_id": line.get("product_id") or False,
            }
            # A05 FIN-14: a line earned over a period (fix_ar_revenue_deferral)
            for key in ("service_period_start", "service_period_end"):
                if line.get(key):
                    vals[key] = line[key]
            code = line.get("vat_treatment_code")
            if code:
                row = (
                    Treatment._fix_treatment_for(code, company)
                    if hasattr(Treatment, "_fix_treatment_for")
                    else Treatment.search([("code", "=", code)], limit=1)
                )
                if not row:
                    raise UserError("No active VAT treatment %s in M51" % code)
                vals["vat_treatment_id"] = row.id
            self.env["fix.ar.invoice.line"].sudo()._fix_with_determination(vals)
        if issue:
            invoice.action_issue()
        return self.browse(invoice.id)

    def _fix_assert_date_open(self):
        """C8: a statutory invoice is never issued into a locked period. Issued
        after the October close, an invoice dated 25 Oct posted its GL in the
        open period but kept a Mushak 6.3 dated 25 Oct, so the 9.1 could
        reconcile in neither month (E2E rehearsal 3, D2-11). Refused, with
        the way out: re-date the draft into the open period."""
        for inv in self:
            lock = ar_lock_covering(inv.env, inv.company_id, inv.invoice_date)
            if lock:
                raise UserError(
                    "Invoice %s is dated %s, on or before the lock date %s of %s: that "
                    "period is closed, and a Mushak 6.3 is never back-dated into it (C8). "
                    "Re-date the invoice to %s or later and issue it."
                    % (
                        inv.name if inv.name and inv.name != "New" else "AR/%s" % inv.id,
                        inv.invoice_date,
                        lock,
                        inv.company_id.name,
                        lock + timedelta(days=1),
                    )
                )

    def _fix_assert_issuer(self):
        """BRU-ARB-02: a manually raised invoice is issued by a second person."""
        self.ensure_one()
        if self.env.su or self.source_model != "manual":
            return
        if self.create_uid == self.env.user:
            raise UserError(
                "A manual invoice is approved and issued by someone other than the person who "
                "raised it (BRU-ARB-02): %s raised %s." % (self.env.user.name, self.display_name)
            )

    def action_issue(self):
        """Issue a manual/draft invoice: draws the gapless number, writes the
        Mushak 6.3 row, posts to GL, publishes invoice.created. An Accountant
        issues (a Billing clerk raises the draft: the M20-15 role split)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Issuing an invoice")
        for inv in self:
            if inv.state != "draft":
                raise UserError("Only draft invoices can be issued")
            if not inv.line_ids:
                raise UserError("An invoice needs at least one line")
            if inv.total_payable <= 0.005:
                raise UserError("Invoice total must be positive")
            if not (inv.manual_reason or "").strip():
                raise UserError("Manual invoices need a reason code (FR-ARB-010)")
            inv._fix_assert_issuer()
            inv._fix_assert_date_open()
            # A03 audit W5 (M33-3): the draft-party switch (no-op under 'allow').
            if hasattr(inv.customer_id, "_fix_assert_party_usable_downstream"):
                inv.customer_id._fix_assert_party_usable_downstream("an invoice")
            inv._credit_hold_check()
            company = inv.company_id
            # E3-20: the 6.3 row cites the invoice's gapless number (drawn in
            # this same transaction), never the internal AR/<id>
            invoice_no = inv._next_invoice_no()
            mushak = _issue_mushak_row(
                self.env,
                {
                    "operating_unit_id": inv.operating_unit_id.id,
                    "company_id": company.id,
                    "mushak_no": self._next_mushak_no(company, inv.invoice_date),
                    "invoice_ref": invoice_no,
                    "invoice_date": inv.invoice_date,
                    "supplier_name": company.name,
                    "supplier_bin": self._company_bin(company),
                    "customer_name": inv._fix_mushak_buyer()[0],
                    "customer_bin": inv._fix_mushak_buyer()[1],
                    "taxable_amount": inv.taxable_amount,
                    "vat_amount": inv.vat_amount,
                    "total_payable": inv.total_payable,
                    "treatment_summary": inv._treatment_summary(),
                },
            )
            inv._guarded().write(
                {
                    "name": invoice_no,
                    "mushak_id": mushak.id,
                    "state": "issued",
                    "issued_by_id": self.env.uid,
                }
            )
            publish(
                inv.env,
                "invoice.created",
                "fix.ar.invoice",
                inv.id,
                {
                    "invoice_ref": "AR/%s" % inv.id,
                    "invoice_no": inv.name,
                    "mushak_no": mushak.mushak_no,
                    "invoice_date": str(inv.invoice_date),
                    "supplier_name": company.name,
                    "supplier_bin": self._company_bin(company),
                    "customer_name": inv._fix_mushak_buyer()[0],
                    "customer_bin": inv._fix_mushak_buyer()[1],
                    "taxable_amount": inv.taxable_amount,
                    "vat_amount": inv.vat_amount,
                    "total_payable": inv.total_payable,
                    "treatment_summary": mushak.treatment_summary,
                    "operating_unit_id": inv.operating_unit_id.id,
                },
            )
            inv._guarded().write({"generated_at": fields.Datetime.now(), "generation_seconds": 0.0})
            inv._post_issue_gl()

    def _treatment_summary(self) -> str:
        self.ensure_one()
        parts = []
        for line in self.line_ids:
            row = line.vat_treatment_id
            parts.append(
                "%s: %s"
                % (
                    line.product_id.default_code or line.description or "LINE",
                    row.treatment_type if row else "standard (M51 determination)",
                )
            )
        reason = (self.manual_reason or "").strip()
        head = "manual entry (%s)" % reason if self.source_model == "manual" else reason
        return "\n".join([head, *parts]) if head else "\n".join(parts)

    @api.model
    def _fix_accepted_quotation(self, order):
        """The customer's latest ACCEPTED service quotation for the order
        (cd_quotation, looked up softly: it is not a dependency), or an
        None."""
        if "fix.quotation" not in self.env:
            return None
        return (
            self.env["fix.quotation"]
            .sudo()
            .search(
                [
                    ("state", "=", "accepted"),
                    ("quote_type", "=", "service"),
                    "|",
                    ("service_order_id", "=", order.id),
                    ("estimate_id.order_id", "=", order.id),
                ],
                order="accepted_at desc, id desc",
                limit=1,
            )
        )

    @api.model
    def _fix_assert_matches_accepted_quotation(self, order, estimate, exempted=0.0):
        """D3-01 (owner decision 12 Nov 2026, E3-01): an invoice from a closed
        service order bills what the customer ACCEPTED. The estimate revised
        after acceptance (QTN/2026/00012 accepted at 4,025.00, invoiced at
        4,945.00 — and below BDT 5,000 the revision needed no consent at all)
        is refused until the customer accepts a quotation at the new value.
        An order with no accepted quotation is invoiced as before.

        G12 (owner decision 12 Nov 2026): `exempted` is the value of the
        APPROVED billed-part-not-fitted exemptions, which the invoice leaves
        off. The invoice may be lower than the accepted value by exactly that
        amount; any other difference is still refused."""
        quotation = self._fix_accepted_quotation(order)
        if not quotation:
            return
        exempted = round(exempted or 0.0, 2)
        billed = round((estimate.grand_total or 0.0) - exempted, 2)
        # P0 quote-to-cash review (12 Nov 2026): accepted_value is now the
        # amount BEFORE VAT; the total the customer accepted (incl. VAT) is
        # accepted_total. A quotation accepted before that change has no
        # accepted_total, and its accepted_value was the VAT-inclusive total.
        accepted_total = (
            quotation["accepted_total"] if "accepted_total" in quotation._fields else 0.0
        )
        accepted = round(accepted_total or quotation.accepted_value or 0.0, 2)
        if abs(accepted - exempted - billed) > 0.005:
            raise UserError(
                "%s cannot be invoiced: its approved estimate %s bills BDT %.2f%s, but the "
                "customer accepted quotation %s v%d at BDT %.2f. Quote the revised estimate "
                "and record the customer's acceptance of the new value before invoicing "
                "(D3-01)."
                % (
                    order.name,
                    estimate.display_name,
                    billed,
                    (
                        " after BDT %.2f of approved billed-part-not-fitted exemptions (so "
                        "BDT %.2f is expected)" % (exempted, accepted - exempted)
                        if exempted
                        else ""
                    ),
                    quotation.name,
                    quotation.accepted_version or quotation.version,
                    accepted,
                )
            )

    @api.model
    def from_closed_service_order(self, order, closed_event_at) -> "FixArInvoice":
        """T02: the auto-invoice path. `order` is a fix.service.order record
        in state 'closed'. Determination runs synchronously (M20 -> M51);
        the invoice, its lines, the account.move, the Mushak register row and
        the invoice.created event all commit in ONE transaction (T08)."""
        # BRU-SRM-05: Delivered or Closed. The supply (tax point) is the
        # delivery; the close drain is the safety net (A02 ERP audit X-03).
        if order.state not in ("delivered", "closed"):
            raise UserError("Auto-invoicing runs on delivered or closed jobs only (BRU-SRM-05)")
        return self._fix_invoice_service_order(order, closed_event_at)

    @api.model
    def from_refused_service_order(self, order) -> "FixArInvoice":
        """D6 (A02 pass 2, M01-03): a repair the customer refuses after it is
        done (QC / Ready) is billed its approved estimate, exactly as a
        delivered one would be; the tax point is the refusal."""
        if order.state not in ("qc_pending", "qc_failed", "ready"):
            raise UserError(
                "%s is %s: only a repaired order the customer refuses is billed this way."
                % (order.name, order.state)
            )
        return self._fix_invoice_service_order(order, fields.Datetime.now())

    @api.model
    def _fix_invoice_service_order(self, order, closed_event_at) -> "FixArInvoice":
        import time

        started = time.monotonic()
        existing = self.search(
            [("source_model", "=", "fix.service.order"), ("source_id", "=", order.id)]
        )
        if existing:
            return existing  # idempotent on the source
        # A02 audit M01-8: a warranty job with an approved estimate was
        # invoiced to the customer (BDT 4,600). A job M01 decides is not
        # charged to the customer (warranty cover, AMC contract, approved
        # goodwill or rework, internal intake) is refused here; the warranty
        # job's cost goes to the OEM claim (cd_warranty_claims) instead.
        basis = order._fix_zero_charge_basis() if hasattr(order, "_fix_zero_charge_basis") else ""
        if basis or order.payment_settlement_state == "covered_zero_charge":
            raise UserError(
                "%s is not charged to the customer (%s): no customer invoice is raised"
                % (order.name, basis or "zero-charge")
            )

        # BRU-SRM-05 gate: the invoiced amount comes from the APPROVED
        # estimate of the closed order — never re-priced here.
        # the governing (latest approved) version, the one the customer paid on
        estimate = order._fix_governing_estimate().filtered(lambda e: e.state == "approved")
        if not estimate:
            raise UserError(
                "No approved estimate on %s — invoicing requires one (BRU-SRM-05)" % order.name
            )
        # G12: a billed part that was never fitted is not billed. APPROVED
        # billed-part-not-fitted exemptions (cd_service_order) take their
        # quantity off the line, with its share of the header discount.
        exemptions = order._fix_part_exemptions(estimate)
        exempt_qty = {}
        for ex in exemptions:
            key = ex.estimate_line_id.id
            exempt_qty[key] = exempt_qty.get(key, 0.0) + (ex.quantity or 0.0)

        # D3-01: the customer's accepted quotation binds the invoice, less
        # exactly the approved exemptions (G12).
        self._fix_assert_matches_accepted_quotation(
            order, estimate, exempted=sum(exemptions.mapped("amount"))
        )

        # FR-ARB-031: a held customer blocks invoicing before anything is created
        self._credit_hold_for(order.customer_id, order.company_id)

        # fix.estimate.line carries no discount: the estimate's discount is a
        # HEADER amount (reading line.discount raised AttributeError on every
        # closed order). It is allocated across the lines before determination.
        quantities = [Decimal(str(line.quantity or 1)) for line in estimate.line_ids]
        prices = [Decimal(str(line.unit_price or 0.0)) for line in estimate.line_ids]
        grosses = [
            (q * p).quantize(TWO_PLACES, ROUND_HALF_UP)
            for q, p in zip(quantities, prices, strict=True)
        ]
        discounts = allocate_discount(grosses, Decimal(str(estimate.discount or 0.0)))
        billed_lines = []
        for line, qty, price, line_discount in zip(
            estimate.line_ids, quantities, prices, discounts, strict=True
        ):
            exempt = Decimal(str(exempt_qty.get(line.id, 0.0)))
            if exempt > 0:
                kept = max(qty - exempt, Decimal("0"))
                if kept <= 0:
                    continue  # the whole line was never fitted
                line_discount = (line_discount * kept / qty).quantize(TWO_PLACES, ROUND_HALF_UP)
                qty = kept
            billed_lines.append((line, qty, price, line_discount))
        if not billed_lines:
            raise UserError(
                "Nothing is billed on %s: every line of its approved estimate is exempted as "
                "not fitted, so no customer invoice is raised (G12)." % order.name
            )
        lines = [
            tax_logic.TaxLine(
                product_code=line.product_id.default_code or "SVC",
                qty=qty,
                unit_price=price,
                discount=line_discount,
            )
            for line, qty, price, line_discount in billed_lines
        ]
        # The tax point is the supply: the delivery, on its Dhaka business day
        # (UTC "today" put a 00:00-06:00 delivery on the previous day, and at a
        # month end into the previous VAT period). The invoice belongs to the
        # order's company, never the delivering user's current company.
        tax_point = order.delivered_at or closed_event_at or fields.Datetime.now()
        invoice_date = dhaka_date(tax_point)
        # D21/D22: the wasted-visit fees and pick-and-drop charges the customer
        # paid with the repair are billed on its invoice (they were recorded,
        # reported and collected, and never reached the tax invoice or revenue)
        extra = self._fix_extra_charge_lines(order)
        lines += [tax_line for _vals, tax_line in extra]
        determination = m51_determine(
            self.env, lines, on_date=invoice_date, company=order.company_id
        )

        billed = [
            {
                "line_type": line.line_type,
                "product_id": line.product_id.id,
                "description": line.description or line.product_id.name,
                "uom_id": line.uom_id.id or False,
                "serial_ref": line.serial_ref or False,
                "quantity": float(qty),
                "unit_price": float(price),
                "gross_amount": float((qty * price).quantize(TWO_PLACES, ROUND_HALF_UP)),
                "discount_amount": float(line_discount),
            }
            for line, qty, price, line_discount in billed_lines
        ] + [vals for vals, _tax_line in extra]
        invoice = self._fix_issue_order_invoice(order, billed, determination, invoice_date, started)
        # A02 ERP audit (19 Nov 2026): the order was PAID before it closed
        # (no device leaves unpaid). That money is a confirmed M20 receipt
        # sitting on the customer's AR as a credit; the invoice it paid for
        # stayed open, aged, and dunned a customer who owed nothing.
        invoice._fix_apply_order_settlement(order)
        return invoice

    def _fix_extra_charge_lines(self, order):
        """[(invoice line values, M51 tax line)] for the order's charges
        outside its estimate (D21 wasted visits, D22 pick and drop)."""
        if not hasattr(order, "_fix_extra_charges"):
            return []
        result = []
        Product = self.env["product.product"].sudo()
        for charge in order._fix_extra_charges():
            product = Product.search([("default_code", "=", charge["code"])], limit=1)
            if not product:
                raise UserError(
                    "%s cannot be invoiced: charge code %s (%s) is not in the catalogue."
                    % (order.name, charge["code"], charge["description"])
                )
            net = Decimal(str(charge["net"])).quantize(TWO_PLACES, ROUND_HALF_UP)
            result.append(
                (
                    {
                        "line_type": charge["line_type"],
                        "product_id": product.id,
                        "description": charge["description"],
                        "uom_id": product.uom_id.id or False,
                        "serial_ref": False,
                        "quantity": 1.0,
                        "unit_price": float(net),
                        "gross_amount": float(net),
                        "discount_amount": 0.0,
                    },
                    tax_logic.TaxLine(
                        product_code=charge["code"],
                        qty=Decimal("1"),
                        unit_price=net,
                        discount=Decimal("0"),
                    ),
                )
            )
        return result

    def _fix_issue_order_invoice(self, order, billed, determination, invoice_date, started):
        """Create, number and post the customer invoice of ``order``: its
        lines (``billed`` line values paired by position with the M51
        ``determination``), the Mushak 6.3 row, the invoice.created event and
        the M19 posting, in ONE transaction (T08). Shared by the delivered-
        order invoice and the declined-repair diagnostic fee (FR-SRM-029)."""
        import time

        invoice = self.with_company(order.company_id).create(
            {
                "company_id": order.company_id.id,
                "invoice_date": invoice_date,
                "customer_id": order.customer_id.id,
                # the order's OU is optional; its (required) branch always has one
                "operating_unit_id": (
                    order.operating_unit_id or order.branch_id.operating_unit_id
                ).id,
                "branch_id": order.branch_id.id,
                "source_model": "fix.service.order",
                "source_id": order.id,
            }
        )
        # determine_tax() returns one determined line per input line, in
        # order. Pair by POSITION: keying by product code collapsed two
        # estimate lines sharing a code (e.g. two "SVC" labour lines) onto
        # the last line's amounts and mis-stated the invoice.
        for seq, (vals, det) in enumerate(zip(billed, determination.lines, strict=True), start=1):
            self.env["fix.ar.invoice.line"].sudo().create(
                dict(
                    vals,
                    invoice_id=invoice.id,
                    sequence=seq * 10,
                    taxable_amount=float(det.taxable_amount),
                    vat_amount=float(det.vat_amount),
                    vat_rate=float(det.rate),
                    line_total=float(det.line_total),
                )
            )

        # C8: never a Mushak 6.3 dated inside a locked period
        invoice._fix_assert_date_open()

        # Mushak register row — same transaction (T08 atomicity)
        company = invoice.company_id
        # E3-20: the 6.3 row cites the invoice's gapless number
        invoice_no = invoice._next_invoice_no()
        mushak = _issue_mushak_row(
            self.env,
            {
                "operating_unit_id": invoice.operating_unit_id.id,
                "company_id": company.id,
                "mushak_no": self._next_mushak_no(company, invoice.invoice_date),
                "invoice_ref": invoice_no,
                "invoice_date": invoice.invoice_date,
                "supplier_name": company.name,
                "supplier_bin": self._company_bin(company),
                "customer_name": invoice._fix_mushak_buyer()[0],
                "customer_bin": invoice._fix_mushak_buyer()[1],
                "taxable_amount": invoice.taxable_amount,
                "vat_amount": invoice.vat_amount,
                "total_payable": invoice.total_payable,
                "treatment_summary": "\n".join(
                    "%s: %s @ %s%%"
                    % (d.product_code, d.treatment, format(Decimal(str(d.rate)).normalize(), "f"))
                    for d in determination.lines
                ),
            },
        )
        invoice._guarded().write(
            {
                "mushak_id": mushak.id,
                "state": "issued",
                "name": invoice_no,
                "issued_by_id": self.env.uid,
            }
        )

        publish(
            self.env,
            "invoice.created",
            "fix.ar.invoice",
            invoice.id,
            {
                "invoice_ref": "AR/%s" % invoice.id,
                "invoice_no": invoice.name,
                "mushak_no": mushak.mushak_no,
                "invoice_date": str(invoice.invoice_date),
                "supplier_name": company.name,
                "supplier_bin": self._company_bin(company),
                "customer_name": invoice._fix_mushak_buyer()[0],
                "customer_bin": invoice._fix_mushak_buyer()[1],
                "taxable_amount": invoice.taxable_amount,
                "vat_amount": invoice.vat_amount,
                "total_payable": invoice.total_payable,
                "treatment_summary": mushak.treatment_summary,
                "operating_unit_id": invoice.operating_unit_id.id,
            },
        )
        elapsed = time.monotonic() - started
        invoice._guarded().write(
            {"generated_at": fields.Datetime.now(), "generation_seconds": elapsed}
        )
        # the M19 posting the docstrings always claimed (skips with an
        # honest gl_note when the company's GL is unconfigured)
        invoice._post_issue_gl()
        return invoice

    DIAGNOSTIC_FEE_CODE_PARAM = "cd_billing_engine.diagnostic_fee_product_code"

    def from_declined_service_order(self, order) -> "FixArInvoice":
        """FR-SRM-029 / SP-013 step 19: a declined repair is charged the agreed
        diagnostic fee. The fee was paid at intake (or formally waived) and is
        held as an ADVANCE receipt on the order; the customer is invoiced for
        exactly that amount, VAT inside it (the fee is a customer price, like
        the estimate's grand total), on one Diagnostic / Inspection line, and
        the advance is applied to it. Returns the empty recordset when the
        order holds no advance (fee waived, or not a walk-in)."""
        import time

        started = time.monotonic()
        order.ensure_one()
        if order.state != "cancelled" or order.cancel_reason_code not in (
            "customer_declined",
            "estimate_declined",
        ):
            raise UserError(
                "%s: only a declined repair is invoiced its diagnostic fee (FR-SRM-029)."
                % order.name
            )
        existing = self.search(
            [("source_model", "=", "fix.service.order"), ("source_id", "=", order.id)]
        )
        if existing:
            return existing  # idempotent on the source
        advances = (
            self.env["fix.ar.receipt"]
            .sudo()
            .search(
                [
                    ("source_order_id", "=", order.id),
                    ("state", "=", "confirmed"),
                    ("is_order_advance", "=", True),
                ]
            )
        )
        fee = Decimal(str(round(sum(advances.mapped("unapplied_amount")), 2)))
        if fee <= 0:
            return self
        code = (
            self.env["ir.config_parameter"].sudo().get_param(self.DIAGNOSTIC_FEE_CODE_PARAM)
            or "CHG-DIAG"
        )
        product = self.env["product.product"].sudo().search([("default_code", "=", code)], limit=1)
        if not product:
            raise UserError(
                "The diagnostic fee charge code %s is not in the catalogue: create it (or set "
                "%s) and retry." % (code, self.DIAGNOSTIC_FEE_CODE_PARAM)
            )
        self._credit_hold_for(order.customer_id, order.company_id)
        # the tax point is the decline: the diagnosis was supplied, nothing else
        invoice_date = dhaka_date(fields.Datetime.now())

        def determine(net):
            line = tax_logic.TaxLine(
                product_code=code, qty=Decimal("1"), unit_price=net, discount=Decimal("0")
            )
            return m51_determine(self.env, [line], on_date=invoice_date, company=order.company_id)

        # the fee is what the customer paid: back the VAT out of it, then take
        # the paisa the per-line rounding leaves onto the net price
        rate = Decimal(str(determine(fee).lines[0].rate))
        net = (fee * Decimal("100") / (Decimal("100") + rate)).quantize(TWO_PLACES, ROUND_HALF_UP)
        determination = determine(net)
        for _step in range(3):
            gap = fee - Decimal(str(determination.lines[0].line_total))
            if abs(gap) < Decimal("0.005"):
                break
            net += gap.quantize(TWO_PLACES, ROUND_HALF_UP)
            determination = determine(net)
        billed = [
            {
                "line_type": "diagnostic",
                "product_id": product.id,
                "description": "%s — %s (repair declined)" % (product.name, order.name),
                "uom_id": product.uom_id.id or False,
                "serial_ref": False,
                "quantity": 1.0,
                "unit_price": float(net),
                "gross_amount": float(net),
                "discount_amount": 0.0,
            }
        ]
        invoice = self._fix_issue_order_invoice(order, billed, determination, invoice_date, started)
        Allocation = self.env["fix.ar.allocation"].sudo()
        made = Allocation
        for receipt in advances:
            invoice.invalidate_recordset(["amount_residual"])
            receipt.invalidate_recordset(["unapplied_amount"])
            amount = round(min(receipt.unapplied_amount, invoice.amount_residual), 2)
            if amount > 0.005:
                made |= Allocation.create(
                    {"receipt_id": receipt.id, "invoice_id": invoice.id, "amount": amount}
                )
        invoice.message_post(
            body="Diagnostic fee of declined repair %s: BDT %.2f applied from %s."
            % (order.name, sum(made.mapped("amount")), ", ".join(made.mapped("receipt_id.name")))
        )
        return invoice

    def _fix_apply_order_settlement(self, order):
        """Apply the receipts that settled ``order`` to this invoice, up to
        its residual. A receipt of another customer, or one with nothing
        unapplied, is left alone; what is not applied stays on the receipt
        (the unapplied-cash queue shows it to finance)."""
        self.ensure_one()
        if self.state != "issued":
            return self.env["fix.ar.allocation"]
        Allocation = self.env["fix.ar.allocation"].sudo()
        made = Allocation
        for receipt in order.sudo()._fix_settlement_receipts():
            self.invalidate_recordset(["amount_residual"])
            receipt.invalidate_recordset(["unapplied_amount"])
            if (
                receipt.state != "confirmed"
                or receipt.customer_id.commercial_partner_id
                != self.customer_id.commercial_partner_id
            ):
                continue
            amount = round(min(receipt.unapplied_amount, self.amount_residual), 2)
            if amount <= 0.005:
                continue
            made |= Allocation.create(
                {"receipt_id": receipt.id, "invoice_id": self.id, "amount": amount}
            )
        if made:
            self.message_post(
                body="Paid before release: BDT %.2f applied from %s."
                % (sum(made.mapped("amount")), ", ".join(made.mapped("receipt_id.name")))
            )
        return made

    MUSHAK_SEQUENCE_CODE = "fix.mushak.63"

    @api.model
    def _mushak_sequence(self, company):
        """The company's own Mushak 6.3 ir.sequence — copied once from the
        module's template (data/ir_sequence_data.xml)."""
        return self._company_sequence(
            self.MUSHAK_SEQUENCE_CODE,
            "cd_billing_engine.seq_fix_mushak_63",
            "Mushak 6.3 Serial",
            company,
            "The Mushak 6.3 numbering sequence is missing — upgrade cd_billing_engine.",
        )

    @api.model
    def _next_mushak_no(self, company, invoice_date=None) -> str:
        """Mushak 6.3 serial: a per-company ir.sequence (no_gap, row-locked)
        with one date range per company FISCAL YEAR, so numbering restarts
        each fiscal year; prefix = fiscal-year start year, e.g. 2026-000001.

        Replaces ``search_count + 1``, which raced under concurrent invoicing
        (two invoices could draw the same number) and never reset. A range
        opened for a year that already has register numbers in that format
        (rows written by the old scheme) continues after the highest of them
        instead of colliding with the (mushak_no, company) key."""
        on = invoice_date or fields.Date.context_today(self)
        seq = self._mushak_sequence(company)
        if not seq.date_range_ids.filtered(lambda r: r.date_from <= on <= r.date_to):
            fy = company.compute_fiscalyear_dates(on)
            prefix = "%d-" % fy["date_from"].year
            used = (
                self.env["fix.mushak.register"]
                .sudo()
                .search([("company_id", "=", company.id), ("mushak_no", "=like", prefix + "%")])
            )
            suffixes = [
                int(no[len(prefix) :])
                for no in used.mapped("mushak_no")
                if no[len(prefix) :].isdigit()
            ]
            self.env["ir.sequence.date_range"].sudo().create(
                {
                    "sequence_id": seq.id,
                    "date_from": fy["date_from"],
                    "date_to": fy["date_to"],
                    # number_next_actual: its inverse sets number_next (a plain
                    # number_next is overwritten by the default_get of 1)
                    "number_next_actual": max(suffixes, default=0) + 1,
                }
            )
        return seq.next_by_id(sequence_date=on)

    @api.model
    def _company_bin(self, company) -> str:
        """The supplier BIN — from company master data (never invented)."""
        from odoo.addons.cd_tax_engine_bd.models.fix_tax_engine import (
            normalize_bin,
            valid_bin,
        )

        vat = normalize_bin(company.vat)
        if not valid_bin(vat):
            raise UserError(
                "Company BIN missing or not 13 digits on %s — a Mushak 6.3 cannot be "
                "issued without the supplier BIN" % company.name
            )
        return vat

    def _settlement_evidence(self) -> str:
        """The documents that cleared this invoice, for the paid event."""
        self.ensure_one()
        parts = []
        receipts = [r for r in self.allocation_ids.mapped("receipt_id.name") if r]
        if receipts:
            parts.append("receipts %s" % ", ".join(receipts))
        notes = self.credit_note_ids.filtered(lambda n: n.state == "issued")
        if notes:
            parts.append("credit notes %s" % ", ".join(str(n.id) for n in notes))
        certs = self.vds_certificate_ids.filtered(lambda c: c.state in ("settled", "claimed"))
        if certs:
            parts.append("VDS certificates %s" % ", ".join(certs.mapped("certificate_no")))
        tds = self.tds_certificate_ids.filtered(lambda c: c.state == "settled")
        if tds:
            parts.append("TDS certificates %s" % ", ".join(tds.mapped("certificate_no")))
        return "; ".join(parts)

    def _mark_paid(self):
        """The evidence-bearing paid transition for the close-out and VDS
        settlement paths (receipt allocations keep their own)."""
        for invoice in self:
            invoice._guarded().write({"state": "paid", "paid_date": fields.Date.today()})
            publish(
                self.env,
                "invoice.paid",
                "fix.ar.invoice",
                invoice.id,
                {
                    "invoice": invoice.name,
                    "mushak_no": invoice.mushak_id.mushak_no,
                    "total_payable": invoice.total_payable,
                    "evidence": invoice._settlement_evidence(),
                },
            )

    def action_register_paid(self):
        """Close an issued invoice whose residual is fully covered by real
        settlement documents (receipt allocations, issued credit notes,
        settled VDS certificates). Receipts arrive as M50 bank/cash events
        consumed by M20 — this is NOT a synchronous call into treasury
        (AR-006 pair 6), and it never marks an invoice paid without evidence:
        an open residual refuses."""
        for invoice in self:
            if invoice.state != "issued":
                raise UserError("Only issued invoices can be paid")
            if invoice.amount_residual > 0.005:
                raise UserError(
                    "Invoice %s still has %s outstanding — allocate a receipt, settle a VDS "
                    "certificate or issue a credit note first; an invoice is never marked "
                    "paid without settlement evidence."
                    % (invoice.name, invoice.currency_id.round(invoice.amount_residual))
                )
        self._mark_paid()

    @api.model
    def benchmark_auto_invoice_timing(self, order_ids) -> dict:
        """NFR-040 & Gate G3-01: benchmark auto-invoicing duration across orders.
        Enforces duration <= 5.0s per closed order."""
        orders = (
            self.env["fix.service.order"].browse(order_ids)
            if isinstance(order_ids, list | tuple)
            else order_ids
        )
        durations = []
        invoices = []
        for order in orders:
            inv = self.from_closed_service_order(order, fields.Datetime.now())
            durations.append(inv.generation_seconds)
            invoices.append(inv.id)
        avg_sec = sum(durations) / len(durations) if durations else 0.0
        max_sec = max(durations) if durations else 0.0
        return {
            "invoice_ids": invoices,
            "durations": durations,
            "average_seconds": avg_sec,
            "max_seconds": max_sec,
            "nfr_040_met": max_sec <= 5.0,
        }


class FixArInvoiceLine(models.Model):
    """One invoice line. VAT is M51's determination of the taxable value and
    the line's treatment (BRU-ARB-03/04): a typed VAT that differs is refused.
    Lines of an issued invoice never change.

    Commercial line standard (17 Nov 2026): a line is SL / type / item code /
    description / qty / unit / unit price / discount / taxable / VAT / total.
    The taxable value is quantity x unit price less the discount; a caller
    that passes only a taxable value (the system contracts) gets quantity 1
    at that price, so every line prints the same columns."""

    _name = "fix.ar.invoice.line"
    _description = "AR Invoice Line"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.commercial.line.mixin"]
    _order = "invoice_id, sequence, id"

    invoice_id = fields.Many2one("fix.ar.invoice", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    line_type = fields.Selection(LINE_TYPES, string="Type", default="service")
    product_id = fields.Many2one("product.product", string="Item / Charge Code")
    description = fields.Char()
    quantity = fields.Float(default=1.0, digits="Product Unit of Measure")
    unit_price = fields.Monetary(string="Unit Price (excl. VAT)", currency_field="currency_id")
    discount_pct = fields.Float(string="Discount (%)")
    gross_amount = fields.Monetary(
        string="Amount before Discount",
        currency_field="currency_id",
        help="Quantity x unit price.",
    )
    discount_amount = fields.Monetary(
        string="Discount",
        currency_field="currency_id",
        help="The line discount plus its share of any overall (header) discount, in money.",
    )
    vat_rate = fields.Float(string="VAT Rate (%)", readonly=True, digits=(5, 2))
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    vat_treatment_id = fields.Many2one(
        "fix.vat.treatment",
        string="VAT Treatment (M51 tariff)",
        help="The M51 tariff row that decides the line's treatment. Empty: M51's "
        "determination by product code, else the standard rate in force.",
    )
    taxable_amount = fields.Monetary(string="Taxable Value", currency_field="currency_id")
    vat_amount = fields.Monetary(string="VAT", currency_field="currency_id")
    line_total = fields.Monetary(string="Line Total", currency_field="currency_id")

    TAX_INPUTS = (
        "taxable_amount",
        "vat_amount",
        "line_total",
        "vat_treatment_id",
        "product_id",
        "quantity",
        "unit_price",
        "discount_pct",
        "discount_amount",
    )

    # M37 VAT classes that carry no rate of their own: a catalogue item of one
    # of these classes is determined so even when M51 has no tariff row for it.
    ITEM_RATELESS_CLASSES = ("exempt", "zero_rated")

    @api.model
    def _fix_item_tax_keys(self, invoice, product, product_code):
        """(hs_code, treatment) of the line's M37 catalogue item.

        A04 ERP audit M37-F2: the catalogue item's HS code and VAT class
        never reached M51, so exempt and zero-rated items were taxed at 15%.
        The HS code keys M51's tariff master; the item's class decides an
        exempt / zero-rated line only when M51 has no tariff row for it (the
        tariff stays the authority where it speaks)."""
        if not product or "fix.catalogue.item" not in self.env:
            return "", ""
        item = (
            self.env["fix.catalogue.item"]
            .sudo()
            .search([("product_tmpl_id", "=", product.product_tmpl_id.id)], limit=1)
        )
        if not item:
            return "", ""
        hs_code = (item.hs_code or "").strip() if "hs_code" in item._fields else ""
        vat_class = item.vat_class if "vat_class" in item._fields else False
        if vat_class not in self.ITEM_RATELESS_CLASSES:
            return hs_code, ""
        Treatment = self.env["fix.vat.treatment"]
        company = invoice.company_id if invoice else self.env.company
        if hasattr(Treatment, "_fix_treatment_for") and (
            Treatment._fix_treatment_for(hs_code, company)
            or Treatment._fix_treatment_for(product_code, company)
        ):
            return hs_code, ""
        return hs_code, vat_class

    @api.model
    def _fix_determined(
        self, invoice, taxable, product, treatment, qty=None, unit_price=None, discount=None
    ):
        """M51's determined line for (taxable, product, treatment), or - when
        a quantity and unit price are given - for qty x price less discount."""
        try:
            if unit_price is not None:
                q = Decimal(str(qty if qty is not None else 1.0))
                price = Decimal(str(unit_price or 0.0))
                disc = Decimal(str(discount or 0.0)).quantize(TWO_PLACES, ROUND_HALF_UP)
            else:
                q = Decimal("1")
                price = Decimal(str(taxable or 0.0)).quantize(TWO_PLACES, ROUND_HALF_UP)
                disc = Decimal("0")
            product_code = (product.default_code if product else "") or "SVC"
            hs_code, item_treatment = self._fix_item_tax_keys(invoice, product, product_code)
            line = tax_logic.TaxLine(
                product_code=product_code,
                qty=q,
                unit_price=price,
                discount=disc,
                hs_code=hs_code,
                treatment=(treatment.treatment_type if treatment else "") or item_treatment,
                rate_override=(
                    Decimal(str(treatment.rate))
                    if treatment and treatment.treatment_type == "reduced"
                    else None
                ),
            )
        except tax_logic.DeterminationError as exc:
            raise UserError("VAT determination (M51) refused: %s" % exc) from exc
        det = m51_determine(
            self.env, [line], on_date=invoice.invoice_date, company=invoice.company_id
        )
        return det.lines[0]

    @api.model
    def _fix_apply_determination(self, vals, line=None):
        """Fill vals' VAT and total from M51; refuse a typed VAT that differs."""
        Invoice = self.env["fix.ar.invoice"]
        invoice = Invoice.browse(vals["invoice_id"]) if vals.get("invoice_id") else line.invoice_id
        self._fix_price_inputs(vals, line)
        taxable = vals.get("taxable_amount", line.taxable_amount if line else 0.0)
        product = (
            self.env["product.product"].browse(vals["product_id"])
            if vals.get("product_id")
            else (
                line.product_id
                if line and "product_id" not in vals
                else self.env["product.product"]
            )
        )
        treatment = (
            self.env["fix.vat.treatment"].browse(vals["vat_treatment_id"])
            if vals.get("vat_treatment_id")
            else (
                line.vat_treatment_id
                if line and "vat_treatment_id" not in vals
                else self.env["fix.vat.treatment"]
            )
        )
        det = self._fix_determined(
            invoice,
            taxable,
            product,
            treatment,
            qty=vals["quantity"],
            unit_price=vals["unit_price"],
            discount=vals["discount_amount"],
        )
        typed_taxable = vals.pop("_typed_taxable", None)
        if typed_taxable is not None and abs(typed_taxable - float(det.taxable_amount)) > 0.005:
            raise UserError(
                "Line '%s': the taxable value is quantity x unit price less the discount "
                "(BDT %.2f), not the BDT %.2f entered."
                % (vals.get("description") or "", float(det.taxable_amount), typed_taxable)
            )
        vat = float(det.vat_amount)
        if "vat_amount" in vals and abs((vals.get("vat_amount") or 0.0) - vat) > 0.005:
            raise UserError(
                "VAT on an AR invoice line is M51's determination (BRU-ARB-03/04): BDT %.2f on "
                "a taxable value of %.2f (%s @ %s%%), not the BDT %.2f entered."
                % (
                    vat,
                    float(det.taxable_amount),
                    det.treatment,
                    det.rate,
                    vals["vat_amount"] or 0.0,
                )
            )
        vals["vat_amount"] = vat
        vals["taxable_amount"] = float(det.taxable_amount)
        vals["line_total"] = float(det.taxable_amount) + vat
        vals["vat_rate"] = float(det.rate)
        return vals

    @api.model
    def _fix_price_inputs(self, vals, line=None):
        """Settle quantity, unit price and discount in vals.

        * A line priced by quantity and unit price: discount = the line's
          discount % of quantity x price, plus any money discount the caller
          allocated (an overall discount's share) as _extra_discount, or a
          money discount_amount given on its own.
        * A caller that gives only a taxable value (the system contracts,
          storefront, disposal): quantity 1 at that value, no discount."""
        priced_keys = {"quantity", "unit_price", "discount_pct", "discount_amount"}
        typed_taxable = vals.get("taxable_amount")
        if not (priced_keys & set(vals)) and (
            "taxable_amount" in vals or not line or not line.unit_price
        ):
            amount = float(typed_taxable if typed_taxable is not None else 0.0)
            vals.pop("_extra_discount", None)
            vals.update(
                {
                    "quantity": 1.0,
                    "unit_price": amount,
                    "discount_pct": 0.0,
                    "discount_amount": 0.0,
                    "gross_amount": amount,
                }
            )
            return vals
        qty = float(vals.get("quantity", line.quantity if line else 1.0) or 0.0)
        price = float(vals.get("unit_price", line.unit_price if line else 0.0) or 0.0)
        pct = float(vals.get("discount_pct", line.discount_pct if line else 0.0) or 0.0)
        if qty < 0 or price < 0:
            raise UserError("An invoice line cannot have a negative quantity or price.")
        if not 0.0 <= pct <= 100.0:
            raise UserError("A line discount is between 0 and 100%.")
        gross = round(qty * price, 2)
        extra = float(vals.pop("_extra_discount", 0.0) or 0.0)
        if "discount_amount" in vals and "discount_pct" not in vals:
            disc = float(vals.get("discount_amount") or 0.0)
        elif line and not ({"quantity", "unit_price", "discount_pct"} & set(vals)):
            disc = line.discount_amount or 0.0
        else:
            disc = round(gross * pct / 100.0, 2) + extra
        if disc < 0 or disc > gross + 0.005:
            raise UserError(
                "The discount on '%s' (BDT %.2f) cannot exceed the line amount (BDT %.2f)."
                % (vals.get("description") or (line.description if line else ""), disc, gross)
            )
        if typed_taxable is not None:
            vals["_typed_taxable"] = float(typed_taxable)
        vals.update(
            {
                "quantity": qty,
                "unit_price": price,
                "discount_pct": pct,
                "discount_amount": round(disc, 2),
                "gross_amount": gross,
            }
        )
        return vals

    @api.model
    def _fix_with_determination(self, vals):
        """Create one line with M51's VAT (the system API path)."""
        vals = self._fix_apply_determination(dict(vals))
        return self.create(vals)

    def _fix_assert_draft(self, invoices):
        frozen = invoices.filtered(lambda i: i.state != "draft")
        if frozen:
            raise UserError(
                "Invoice %s is issued: its lines are frozen with the Mushak 6.3 and the GL "
                "entry. Correct it with a credit note." % ", ".join(frozen.mapped("display_name"))
            )

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._fix_commercial_prepare(dict(v)) for v in vals_list]
        Product = self.env["product.product"]
        for vals in vals_list:
            if not vals.get("description") and vals.get("product_id"):
                vals["description"] = Product.browse(vals["product_id"]).name
        if not self.env.su:
            Invoice = self.env["fix.ar.invoice"]
            for vals in vals_list:
                invoice = Invoice.browse(vals.get("invoice_id"))
                self._fix_assert_draft(invoice)
                self._fix_apply_determination(vals)
        else:
            for vals in vals_list:
                # a system path that prices by quantity x unit price (no
                # amounts of its own) is determined like a user's line
                if "unit_price" in vals and "taxable_amount" not in vals:
                    self._fix_apply_determination(vals)
                    continue
                # system paths set the determined amounts themselves; the
                # priced columns still follow them
                if "unit_price" not in vals and "taxable_amount" in vals:
                    amount = float(vals.get("taxable_amount") or 0.0)
                    vals.setdefault("quantity", 1.0)
                    vals["unit_price"] = amount
                    vals.setdefault("gross_amount", amount)
                vals.pop("_extra_discount", None)
                vals.pop("_typed_taxable", None)
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            self._fix_assert_draft(self.mapped("invoice_id"))
            if "invoice_id" in vals:
                self._fix_assert_draft(self.env["fix.ar.invoice"].browse(vals["invoice_id"]))
            if set(self.TAX_INPUTS) & set(vals):
                for line in self:
                    line_vals = dict(vals)
                    self._fix_apply_determination(line_vals, line=line)
                    super(FixArInvoiceLine, line).write(line_vals)
                return True
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            self._fix_assert_draft(self.mapped("invoice_id"))
        return super().unlink()


class FixDunning(models.Model):
    """Collections ladder (T05): ageing buckets, reminder steps from the
    NT-006 finance SMS ladder, escalation.

    A08 M20-11 (BRU-ARB-15/16): a suppression records who, why and until
    when. The nightly run lifts only the dispute suppressions it set itself;
    a payment-plan or strategic suppression stays until its end date."""

    _name = "fix.dunning"
    _description = "Dunning Run"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")
    invoice_id = fields.Many2one(
        "fix.ar.invoice", string="Invoice", required=True, ondelete="cascade", index=True
    )
    name = fields.Char(compute="_compute_name", string="Dunning")
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    overdue_amount = fields.Monetary(string="Overdue", currency_field="currency_id")
    days_overdue = fields.Integer(compute="_compute_ageing", store=True)
    bucket = fields.Selection(
        [
            ("current", "Current"),
            ("d1_30", "1-30"),
            ("d31_60", "31-60"),
            ("d61_90", "61-90"),
            ("d90_plus", "90+"),
        ],
        compute="_compute_ageing",
        store=True,
        string="Ageing Bucket",
    )
    step = fields.Selection(
        [
            ("reminder", "Reminder (NT-006 L1)"),
            ("final", "Final Notice (L2)"),
            ("escalate", "Escalated to Collections (L3)"),
        ],
        default="reminder",
        required=True,
        tracking=True,
    )
    step_date = fields.Date(
        string="Step Date", help="When the current ladder step was set (grace runs from here)"
    )
    suppressed = fields.Boolean(
        help="Dunning suspended for this invoice (dispute / payment plan / strategic)"
    )
    suppression_reason = fields.Selection(
        [
            ("dispute", "Open Dispute"),
            ("payment_plan", "Payment Plan"),
            ("strategic", "Strategic Customer"),
        ],
    )
    suppressed_by_id = fields.Many2one(
        "res.users", string="Suppressed By", readonly=True, copy=False
    )
    suppressed_at = fields.Datetime(string="Suppressed On", readonly=True, copy=False)
    suppressed_until = fields.Date(string="Suppressed Until", readonly=True, copy=False)
    suppression_note = fields.Char(string="Suppression Note", readonly=True, copy=False)

    DUNNING_GUARDED = {
        "step",
        "step_date",
        "overdue_amount",
        "suppressed",
        "suppression_reason",
        "suppressed_by_id",
        "suppressed_at",
        "suppressed_until",
        "suppression_note",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.DUNNING_GUARDED

    # the NT-006 ladder: step -> (next step, grace days before advancing)
    LADDER = {"reminder": ("final", 7), "final": ("escalate", 14)}

    @api.depends("invoice_id.invoice_date")
    def _compute_ageing(self):
        today = fields.Date.today()
        for run in self:
            if run.invoice_id.invoice_date:
                terms = run.invoice_id._payment_terms_days()
                delta = (today - run.invoice_id.invoice_date).days - terms
                run.days_overdue = max(delta, 0)
                run.bucket = (
                    "current"
                    if delta <= 0
                    else "d1_30"
                    if delta <= 30
                    else "d31_60"
                    if delta <= 60
                    else "d61_90"
                    if delta <= 90
                    else "d90_plus"
                )
            else:
                # an unsaved run without its invoice yet (form onchange):
                # stored computes must always assign
                run.days_overdue = 0
                run.bucket = "current"

    # Hooks the ladder policy (fix_ar_capture.py) overrides: the built-in
    # NT-006 ladder, the first reminder the day after the due date, and no
    # arrangement holding a new run.
    def _fix_ladder(self):
        return self.LADDER

    @api.model
    def _fix_first_offset(self, invoice):
        return 1

    @api.model
    def _fix_hold_new(self, invoice, today):
        return False

    def _manual_suppression_active(self, today) -> bool:
        self.ensure_one()
        return (
            self.suppressed
            and self.suppression_reason in ("payment_plan", "strategic")
            and (not self.suppressed_until or self.suppressed_until >= today)
        )

    @api.model
    def action_run_dunning(self, as_of=None):
        """FR-ARB-032/033/036: the dunning engine. Scans issued+overdue
        invoices (by the customer's OWN terms), creates the first run or
        advances the NT-006 ladder after each step's grace days. An open
        dispute suspends dunning for the DISPUTED AMOUNT ONLY — the
        undisputed remainder keeps dunning. Returns measured counts."""
        today = as_of or fields.Date.today()
        Dispute = self.env["fix.ar.dispute"]
        Invoice = self.env["fix.ar.invoice"]
        created = advanced = suppressed = skipped = kept = 0
        invoices = Invoice.search([("state", "=", "issued")]).filtered(
            lambda inv: inv.amount_residual > 0.005
        )
        for inv in invoices:
            terms = inv._payment_terms_days()
            days_past_due = (today - inv.invoice_date).days - terms
            if days_past_due <= 0:
                continue
            disputed = sum(
                Dispute.search([("invoice_id", "=", inv.id), ("state", "=", "open")]).mapped(
                    "amount_disputed"
                )
            )
            dunnable = inv.amount_residual - disputed
            existing = self.search([("invoice_id", "=", inv.id)], limit=1)
            if existing and existing._manual_suppression_active(today):
                # BRU-ARB-15/16: a recorded payment-plan / strategic
                # suppression stands until its end date
                kept += 1
                continue
            if dunnable <= 0.005:
                if existing and not existing.suppressed:
                    existing._guarded().write(
                        {
                            "suppressed": True,
                            "suppression_reason": "dispute",
                            "suppressed_by_id": False,
                            "suppressed_at": fields.Datetime.now(),
                            "suppressed_until": False,
                            "suppression_note": "Open dispute covers the residual",
                        }
                    )
                    suppressed += 1
                elif not existing:
                    skipped += 1
                continue
            if existing:
                if existing.suppressed:
                    note = (
                        "dispute resolved"
                        if existing.suppression_reason == "dispute"
                        else "suppression expired %s" % existing.suppressed_until
                    )
                    existing._guarded().write(
                        {
                            "suppressed": False,
                            "suppression_reason": False,
                            "suppressed_until": False,
                            "suppression_note": False,
                        }
                    )
                    existing.message_post(body="Dunning resumed: %s." % note)
                nxt, grace = existing._fix_ladder().get(existing.step, (False, 0))
                if (
                    nxt
                    and existing.step_date
                    and (today - existing.step_date).days >= grace
                    and existing.step != "escalate"
                ):
                    existing._guarded().write(
                        {"step": nxt, "step_date": today, "overdue_amount": dunnable}
                    )
                    advanced += 1
                else:
                    existing._guarded().write({"overdue_amount": dunnable})
            else:
                if self._fix_hold_new(inv, today):
                    kept += 1
                    continue
                if days_past_due < self._fix_first_offset(inv):
                    continue
                self._guarded().create(
                    {
                        "company_id": inv.company_id.id,
                        "operating_unit_id": inv.operating_unit_id.id,
                        "invoice_id": inv.id,
                        "overdue_amount": dunnable,
                        "step": "reminder",
                        "step_date": today,
                    }
                )
                created += 1
        return {
            "invoices_scanned": len(invoices),
            "created": created,
            "advanced": advanced,
            "suppressed": suppressed,
            "fully_disputed_skipped": skipped,
            "suppression_kept": kept,
        }

    def _cron_run_dunning(self):
        """Daily cron entry: run the ladder."""
        self.action_run_dunning()

    @api.depends("invoice_id.name", "step")
    def _compute_name(self):
        for run in self:
            run.name = "%s / %s" % (
                run.invoice_id.name or "Invoice #%s" % run.invoice_id.id,
                run.step,
            )

    # One button per controlled reason (M20-11): the code is chosen, never typed.
    def action_suppress_payment_plan(self, until=None, note=None):
        return self.action_suppress("payment_plan", until=until, note=note)

    def action_suppress_strategic(self, until=None, note=None):
        return self.action_suppress("strategic", until=until, note=note)

    def action_suppress_dispute(self, until=None, note=None):
        return self.action_suppress("dispute", until=until, note=note)

    def action_suppress(self, reason, until=None, note=None):
        """BRU-ARB-16: suppress dunning with a reason, the suppressor and an
        end date (default: the configured number of days)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Suppressing dunning")
        if reason not in ("dispute", "payment_plan", "strategic"):
            raise UserError("Pick a suppression reason (FR-ARB-033)")
        try:
            end = fields.Date.to_date(until) if until else None
        except ValueError:
            raise UserError("The end date of a suppression is written YYYY-MM-DD.") from None
        if end is None and reason != "dispute":
            days = int(float_param(self.env, PARAM_SUPPRESSION_DAYS, DEFAULT_SUPPRESSION_DAYS))
            end = fields.Date.add(fields.Date.context_today(self), days=days)
        if end and end < fields.Date.context_today(self):
            raise UserError("A suppression ends in the future, not on %s" % end)
        for run in self:
            run._guarded().write(
                {
                    "suppressed": True,
                    "suppression_reason": reason,
                    "suppressed_by_id": self.env.uid,
                    "suppressed_at": fields.Datetime.now(),
                    "suppressed_until": end or False,
                    "suppression_note": (note or "")[:250] or False,
                }
            )
            run.message_post(
                body="Dunning suppressed (%s) by %s until %s."
                % (reason, self.env.user.name, end or "the dispute closes")
            )

    def action_lift_suppression(self, note=None):
        """End a suppression early (logged)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Lifting a dunning suppression")
        for run in self:
            run._guarded().write(
                {
                    "suppressed": False,
                    "suppression_reason": False,
                    "suppressed_until": False,
                    "suppression_note": (note or "")[:250] or False,
                }
            )
            run.message_post(body="Dunning suppression lifted by %s." % self.env.user.name)


CREDIT_GUARDED = {
    "state",
    "approved_by",
    "approved_at",
    "requested_by_id",
    "submitted_at",
    "tier_basis_amount",
    "issued_at",
    "posted_move_id",
    "gl_note",
    "rejected_reason",
    "mushak_note_id",
    "refund_amount",
    "refund_ref",
}
# Frozen once a credit note is submitted: the approval covers them.
CREDIT_LOCKED = ("amount", "invoice_id", "reason_code", "company_id", "operating_unit_id")
CREDIT_OPEN_STATES = ("pending_approval", "approved", "issued")


class FixCreditNote(models.Model):
    """Credit notes with approval authority (T06, 05-04 §7 — the authority
    matrix is a segregation-of-duties control, SOD-04).

    A08 S3: never auto-approved. <= the direct band a second Accountant
    approves; above it the Accounting Administrator through the M63 inbox;
    the raiser / submitter never approves. The approval covers the amount
    frozen at submit; total credits never exceed the invoice."""

    _name = "fix.credit.note"
    _description = "Credit Note"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.finance.dofa.mixin"]
    _approval_domain = "credit_note"
    _fin_direct_param = PARAM_CREDIT_DIRECT
    _fin_direct_default = DEFAULT_DIRECT_LIMIT
    _fin_cfo_param = PARAM_CREDIT_CFO
    _fin_cfo_default = 0.0
    _fin_what = "Credit note"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    invoice_id = fields.Many2one(
        "fix.ar.invoice", string="Original Invoice", required=True, ondelete="restrict"
    )
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    amount = fields.Monetary(string="Credit Amount", currency_field="currency_id", required=True)
    reason_code = fields.Selection(
        [
            ("service_failure", "Service Failure"),
            ("pricing_error", "Pricing Error"),
            ("warranty", "Warranty Re-work"),
            ("goodwill", "Goodwill"),
            ("return", "Return"),
            ("subscription_refund", "Subscription Cancellation Refund"),
            # G12: a billed part that was never fitted, credited after the
            # invoice (fix.so.part.exemption, cd_service_order).
            ("part_not_fitted", "Billed Part Not Fitted"),
        ],
        required=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending_approval", "Pending Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("issued", "Issued"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    requested_by_id = fields.Many2one("res.users", string="Submitted By", readonly=True, copy=False)
    submitted_at = fields.Datetime(readonly=True, copy=False)
    tier_basis_amount = fields.Monetary(
        string="Cumulative Credit (tier basis)",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="This credit plus every other open credit on the invoice at submit: the "
        "approval tier is cumulative per invoice, so a credit split into pieces "
        "reaches the same approver as the whole.",
    )
    rejected_reason = fields.Char(readonly=True, copy=False)
    issued_at = fields.Datetime(readonly=True, copy=False)
    posted_move_id = fields.Many2one("account.move", string="GL Move", readonly=True, copy=False)
    gl_note = fields.Char(readonly=True, copy=False)
    mushak_note_id = fields.Many2one(
        "fix.mushak.register", string="Mushak 6.7", readonly=True, copy=False
    )
    refund_amount = fields.Monetary(
        string="Refund of Money Received",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The part of this credit that covers money the customer already paid: it is "
        "paid back only as an M50 payment instruction (BRU-ARB-11).",
    )
    refund_ref = fields.Char(string="Refund Instruction", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | CREDIT_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(CREDIT_LOCKED)
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            touched = set(CREDIT_LOCKED) & set(vals)
            if touched and self.filtered(lambda r: r.state != "draft"):
                raise UserError(
                    "A submitted credit note is fixed (%s): the approval covers what was "
                    "submitted. Reject it and raise a new one." % ", ".join(sorted(touched))
                )
        return super().write(vals)

    # ---- the ladder ---------------------------------------------------------
    def _other_open_credit(self) -> float:
        self.ensure_one()
        if not self.invoice_id:
            return 0.0
        others = self.invoice_id.credit_note_ids.filtered(
            lambda n: n.id != self.id and n.state in CREDIT_OPEN_STATES
        )
        return sum(others.mapped("amount"))

    def _dofa_amount(self) -> float:
        self.ensure_one()
        if self.state != "draft" and self.tier_basis_amount:
            return self.tier_basis_amount
        return (self.amount or 0.0) + self._other_open_credit()

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (cumulative credit on %s)" % (
            self._dofa_amount(),
            self.invoice_id.name or "the invoice",
        )

    @api.depends("amount", "tier_basis_amount", "state")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _fin_requester(self):
        return self.requested_by_id

    @api.model
    def _fix_request_credit(self, invoice, amount, reason_code, note=None):
        """CONTRACT (B4 -> A04 bridge): request a credit note against an AR
        invoice. The note is created and SUBMITTED: it then runs the routed
        approval (a second Accountant within the band, the Accounting
        Administrator above it) and the cumulative limit (credits never exceed
        the invoice). Nothing is approved or issued here. Returns the note."""
        if not invoice or invoice._name != "fix.ar.invoice":
            raise UserError("A credit note is requested against an AR invoice.")
        invoice = invoice.sudo()
        if reason_code not in dict(self._fields["reason_code"].selection):
            raise UserError("Unknown credit-note reason %r (BRU-ARB-10 taxonomy)." % reason_code)
        credit = self.create(
            {
                "company_id": invoice.company_id.id,
                "operating_unit_id": invoice.operating_unit_id.id,
                "invoice_id": invoice.id,
                "amount": amount,
                "reason_code": reason_code,
            }
        )
        if note:
            credit.message_post(body=note)
        credit.action_submit()
        return credit

    # ---- checks -------------------------------------------------------------
    def _check_credit_cap(self):
        """Credits never exceed what is creditable on the invoice: its total,
        less every other credit (open and issued) and what VDS or a write-off
        already settled. Money the customer PAID stays creditable, but that part
        is not a reduction of the receivable: it is a refund and goes through
        M50 (BRU-ARB-11), so it is refused where treasury cannot pay it."""
        for note in self:
            invoice = note.invoice_id
            if not invoice:
                continue
            if note.amount <= 0:
                raise UserError("A credit note amount must be positive")
            total = note.amount + note._other_open_credit()
            settled = (
                (invoice.vds_settled_amount or 0.0)
                + (invoice.tds_settled_amount or 0.0)
                + (invoice.written_off_amount or 0.0)
            )
            creditable = invoice.total_payable - settled
            if total > creditable + 0.005:
                raise UserError(
                    "Credit %.2f would take the credits on invoice %s to %.2f, above the "
                    "creditable %.2f (total %.2f less VDS and write-off): credits never exceed "
                    "the invoice."
                    % (note.amount, invoice.name, total, creditable, invoice.total_payable)
                )
            if note._refund_part() > 0.005 and "fix.payment.execution" not in self.env:
                raise UserError(
                    "Credit %.2f on invoice %s covers money already received: it is refunded "
                    "through treasury (M50), which is not installed. Credit only the open %.2f."
                    % (note.amount, invoice.name, max(note.amount - note._refund_part(), 0.0))
                )

    def _refund_part(self) -> float:
        """The part of this credit above what is still unpaid on the invoice:
        total - credits - paid is the most that can reduce the receivable."""
        self.ensure_one()
        invoice = self.invoice_id
        settled = (
            (invoice.vds_settled_amount or 0.0)
            + (invoice.tds_settled_amount or 0.0)
            + (invoice.written_off_amount or 0.0)
        )
        unpaid = (
            invoice.total_payable
            - self._other_open_credit()
            - settled
            - (invoice.amount_paid or 0.0)
        )
        return round(max(self.amount - max(unpaid, 0.0), 0.0), 2)

    def _fix_refund_method(self) -> str:
        """The rail a refund on this credit note goes out on. A bridge whose
        invoices were paid over another rail overrides it (the storefront
        refunds a bKash payment to the same wallet, not to a bank account)."""
        self.ensure_one()
        return "bank_transfer"

    def _fix_request_refund(self):
        """BRU-ARB-11: the part of an issued credit that covers money already
        received leaves as a pending M50 instruction to the customer; treasury
        prepares and releases it (Dr receivable / Cr bank)."""
        from .fix_ar_engine import _ar_account

        for note in self:
            refund = note.refund_amount
            if refund <= 0.005 or note.refund_ref:
                continue
            invoice = note.invoice_id
            customer = invoice.customer_id.commercial_partner_id.sudo()
            options = {
                "company_id": invoice.company_id.id,
                "operating_unit_id": invoice.operating_unit_id.id,
                "method": note._fix_refund_method(),
                "payee": customer.display_name,
            }
            ar = _ar_account(note.env, invoice.company_id, "ar")
            if ar:
                options["debit_account_id"] = ar.id
            pay = self.env["fix.payment.execution"]._fix_request_payment(
                "fix.credit.note",
                note.id,
                customer,
                customer.bank_ids[:1],
                refund,
                invoice.currency_id,
                "Refund on credit note #%s (%s)" % (note.id, invoice.name),
                note.approved_by,
                **options,
            )
            note._guarded().write({"refund_ref": pay.name})
            note.message_post(
                body="BDT %.2f of this credit covers money already received: refund instruction "
                "%s is pending with treasury (BRU-ARB-11)." % (refund, pay.name)
            )

    def action_submit(self):
        """Submit for approval: the amount is frozen, the cumulative tier
        basis pinned, and an above-band note routed to M63. Nothing is
        approved here."""
        for note in self:
            if note.state != "draft":
                raise UserError("Only a draft credit note is submitted (%s)" % note.state)
            if note.invoice_id.state not in ("issued", "paid"):
                raise UserError(
                    "Credit notes apply to issued/paid invoices only (state: %s)"
                    % note.invoice_id.state
                )
            note._check_credit_cap()
            note._guarded().write(
                {
                    "state": "pending_approval",
                    "requested_by_id": self.env.uid,
                    "submitted_at": fields.Datetime.now(),
                    "tier_basis_amount": note.amount + note._other_open_credit(),
                }
            )
            note._fin_route(
                "Credit note of BDT %.2f on invoice %s (%s)"
                % (note.amount, note.invoice_id.name, note.reason_code)
            )
        return True

    def action_approve(self):
        """Within the direct band: a second Accountant approves here. Above it
        the approval comes from the Accounting Administrator's M63 inbox task
        (a direct call is refused by the routing guard)."""
        for note in self:
            if note.state != "pending_approval":
                raise UserError("Only a submitted credit note is approved (%s)" % note.state)
            if note._dofa_current_tier() == "tier_0":
                note._fin_approve_direct()
            else:
                note.action_dofa_approve()
        return True

    def _fin_before_approve(self):
        self.ensure_one()
        if self.state != "pending_approval":
            raise UserError("Only a submitted credit note is approved (%s)" % self.state)
        if self.invoice_id.state not in ("issued", "paid"):
            raise UserError("Invoice %s is %s" % (self.invoice_id.name, self.invoice_id.state))
        self._check_credit_cap()

    def _fin_after_approve(self):
        self.ensure_one()
        self.sudo()._guarded().write(
            {"state": "approved", "approved_by": self.env.uid, "approved_at": fields.Datetime.now()}
        )

    def action_reject(self, reason=""):
        """The approver declines (a checker, never the submitter)."""
        if not (reason or "").strip():
            raise UserError("State why the credit note is rejected")
        for note in self:
            if note.state not in ("pending_approval", "approved"):
                raise UserError("Only a submitted or approved credit note is rejected")
            if not self.env.su:
                require_role(self.env, GROUP_ACCOUNTANT, "Rejecting a credit note")
                if self.env.user in (note.requested_by_id | note.create_uid):
                    raise UserError("You raised this credit note; another person decides it.")
            note._fin_void("rejected: %s" % reason)
            note._guarded().write({"state": "rejected", "rejected_reason": reason[:250]})
        return True

    def action_rerequest(self, justification=""):
        """M63 returned the note for more information: the requester answers
        and sends it back, unchanged, into the same ladder (M20-1: it stayed
        pending for ever)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Re-requesting a credit note's approval")
        if not (justification or "").strip():
            raise UserError("Say what information the approver asked for and what it is.")
        for note in self:
            if note.state != "pending_approval" or note.approval_state != "returned":
                raise UserError(
                    "Credit note %s was not returned by its approver (%s / %s)."
                    % (note.display_name, note.state, note.approval_state)
                )
            note.action_request_approval(justification=justification)
        return True

    def action_withdraw_to_draft(self, reason=""):
        """Or the requester takes a returned note back to correct it: the
        approval is voided, the note is a draft again and is submitted anew."""
        require_role(self.env, GROUP_ACCOUNTANT, "Withdrawing a credit note")
        if not (reason or "").strip():
            raise UserError("State why the credit note is withdrawn.")
        for note in self:
            if note.state != "pending_approval" or note.approval_state != "returned":
                raise UserError(
                    "Only a credit note returned by its approver is withdrawn (%s)."
                    % note.display_name
                )
            note._fin_void("withdrawn: %s" % reason)
            note._guarded().write(
                {
                    "state": "draft",
                    "approval_state": "none",
                    "requested_by_id": False,
                    "submitted_at": False,
                    "tier_basis_amount": 0.0,
                }
            )
            note.message_post(body="Withdrawn to draft by %s: %s" % (self.env.user.name, reason))
        return True

    def _approval_on_rejected(self, comment):
        for note in self.sudo():
            if note.state in ("pending_approval", "approved"):
                note._guarded().write(
                    {"state": "rejected", "rejected_reason": (comment or "M63 rejection")[:250]}
                )

    def action_issue(self):
        """Issue = apply + post. Partial credits keep the invoice issued with
        a residual; only a fully-credited invoice flips to 'credited'. The GL
        mirror reverses revenue/VAT pro-rata — a credit note never invents
        VAT relief beyond the invoice's own ratio."""
        for note in self:
            if note.state != "approved":
                raise UserError("Approve before issuing")
            note._fin_assert_approved()
            invoice = note.invoice_id
            if invoice.state not in ("issued", "paid"):
                raise UserError(
                    "Credit notes apply to issued/paid invoices only (state: %s)" % invoice.state
                )
            note._check_credit_cap()
            refund = note._refund_part()
            note._guarded().write(
                {"state": "issued", "issued_at": fields.Datetime.now(), "refund_amount": refund}
            )
            # X5-10: the GL entry and the Mushak 6.7 carry the same Dhaka day
            on_date = dhaka_date(fields.Datetime.now())
            note._post_credit_gl(on_date)
            note._register_mushak_note(on_date)
            note._fix_request_refund()
            # partial application: only fully-credited invoices flip state
            if invoice.state == "issued" and invoice.amount_residual <= 0.005:
                invoice._guarded().write({"state": "credited"})
            publish(
                self.env,
                "credit_note.issued",
                "fix.credit.note",
                note.id,
                {
                    "invoice_ref": "AR/%s" % invoice.id,
                    "invoice": invoice.name,
                    "amount": note.amount,
                    "reason": note.reason_code,
                    "invoice_residual": invoice.amount_residual,
                },
            )

    def _vat_split(self):
        self.ensure_one()
        invoice = self.invoice_id
        ratio = (invoice.vat_amount / invoice.total_payable) if invoice.total_payable else 0.0
        vat_part = self.amount * ratio
        return self.amount - vat_part, vat_part

    def _register_mushak_note(self, on_date=None):
        """The Mushak 6.7 against the invoice's 6.3 (M51's correction service)."""
        on_date = on_date or dhaka_date(fields.Datetime.now())
        Register = self.env["fix.mushak.register"]
        for note in self:
            original = note.invoice_id.mushak_id
            if not original or not hasattr(Register, "_fix_issue_note"):
                continue
            taxable, vat = note._vat_split()
            row = Register._fix_issue_note(
                original,
                "credit_note",
                round(taxable, 2),
                round(vat, 2),
                "Credit note #%s (%s)" % (note.id, note.reason_code),
                ref="CN/%s" % note.id,
                on_date=on_date,
            )
            note._guarded().write({"mushak_note_id": row.id})

    def _post_credit_gl(self, on_date=None):
        """The statutory mirror posting (FR-ARB-039): Dr Revenue + Dr VAT
        pro-rata / Cr AR — only when the invoice itself posted to GL."""
        from .fix_ar_engine import _ar_account, _ar_invoice_journal, _post_ar_move

        on_date = on_date or dhaka_date(fields.Datetime.now())

        for note in self:
            invoice = note.invoice_id
            if not invoice.posted_move_id:
                note._guarded().write(
                    {"gl_note": "GL not posted: invoice %s has no GL move" % invoice.name}
                )
                continue
            company = invoice.company_id
            ar = _ar_account(note.env, company, "ar")
            revenue = invoice._revenue_account()
            vat = _ar_account(note.env, company, "vat_output")
            if not (ar and revenue and vat):
                note._guarded().write(
                    {"gl_note": "GL not posted: accounts unconfigured for %s" % company.name}
                )
                continue
            revenue_part, vat_part = note._vat_split()
            _dims = invoice._ar_posting_dims(invoice.branch_id.id)
            dims = dict.fromkeys(range(3), _dims)
            move, gl_note = _post_ar_move(
                note.env,
                company,
                on_date,
                "CREDIT NOTE INV %s — %s (%s)" % (invoice.name, note.amount, note.reason_code),
                [
                    (revenue.id, "Credit — service revenue", revenue_part, 0.0, False),
                    (vat.id, "Credit — VAT output reversal", vat_part, 0.0, False),
                    (
                        ar.id,
                        "AR credited — %s" % invoice.customer_id.name,
                        0.0,
                        note.amount,
                        invoice.customer_id.id,
                    ),
                ],
                dims,
                source="ar",
                # C11: the credit note reverses the issue on the Sales journal
                journal=_ar_invoice_journal(note.env, company),
            )
            note._guarded().write(
                {"posted_move_id": move.id if move else False, "gl_note": gl_note or False}
            )


WRITEOFF_GUARDED = {
    "state",
    "amount",
    "requested_by_id",
    "requested_at",
    "move_id",
    "allowance_amount",
    "expense_amount",
    "allowance_account_id",
    "rejected_reason",
}


class FixArWriteoff(models.Model):
    """An AR write-off (spec §9 fix.ar.writeoff, FR-ARB-041 / BRU-ARB-12):
    requested with a reason and the recovery history, approved on the
    finance ladder by someone other than the requester, then posted —
    against the IFRS 9 loss allowance first (Dr allowance), the excess only
    to bad-debt expense; never both (A08 M20-6: the loss was expensed twice).
    The amount is the residual at request and is pinned."""

    _name = "fix.ar.writeoff"
    _description = "AR Write-off"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.finance.dofa.mixin"]
    _order = "id desc"
    _approval_domain = "ar_writeoff"
    _fin_direct_param = PARAM_WRITEOFF_DIRECT
    _fin_direct_default = DEFAULT_DIRECT_LIMIT
    _fin_cfo_param = PARAM_WRITEOFF_CFO
    _fin_cfo_default = 0.0
    _fin_what = "Write-off"

    name = fields.Char(default="New", readonly=True, copy=False, index=True)
    invoice_id = fields.Many2one(
        "fix.ar.invoice", string="Invoice", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(related="invoice_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="invoice_id.operating_unit_id", store=True)
    customer_id = fields.Many2one(related="invoice_id.customer_id", store=True, index=True)
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    amount = fields.Monetary(
        string="Amount Written Off", currency_field="currency_id", readonly=True, copy=False
    )
    reason = fields.Char(required=True)
    recovery_history = fields.Text(
        string="Recovery History",
        required=True,
        help="BRU-ARB-12: the collection steps taken before the write-off",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("requested", "Requested"),
            ("posted", "Approved & Posted"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True, copy=False)
    requested_at = fields.Datetime(readonly=True, copy=False)
    allowance_account_id = fields.Many2one(
        "account.account", string="Loss Allowance Account", readonly=True, copy=False
    )
    allowance_amount = fields.Monetary(
        string="Charged to Loss Allowance", currency_field="currency_id", readonly=True, copy=False
    )
    expense_amount = fields.Monetary(
        string="Charged to Bad-Debt Expense",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )
    move_id = fields.Many2one("account.move", string="GL Move", readonly=True, copy=False)
    rejected_reason = fields.Char(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | WRITEOFF_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= {"invoice_id", "reason", "recovery_history"}
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            touched = {"invoice_id", "reason", "recovery_history"} & set(vals)
            if touched and self.filtered(lambda r: r.state != "draft"):
                raise UserError("A requested write-off is fixed; reject it and request again.")
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.ar.writeoff") or "WO/New"
                )
        return super().create(vals_list)

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.amount if self.state != "draft" else (self.invoice_id.amount_residual or 0.0)

    @api.depends("amount", "state")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _fin_requester(self):
        return self.requested_by_id

    def action_submit(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Requesting a write-off")
        for wo in self:
            if wo.state != "draft":
                raise UserError("Only a draft write-off is requested")
            invoice = wo.invoice_id
            if invoice.state != "issued":
                raise UserError("Only issued invoices can be written off")
            if invoice.amount_residual <= 0.005:
                raise UserError("Nothing residual to write off on %s" % invoice.name)
            if not (wo.reason or "").strip():
                raise UserError("A write-off reason is required (FR-ARB-041)")
            if not (wo.recovery_history or "").strip():
                raise UserError("Record the recovery history first (BRU-ARB-12)")
            if invoice.writeoff_ids.filtered(
                lambda w, own=wo.id: w.id != own and w.state == "requested"
            ):
                raise UserError(
                    "Invoice %s already has a write-off awaiting approval" % invoice.name
                )
            wo._guarded().write(
                {
                    "state": "requested",
                    "amount": invoice.amount_residual,
                    "requested_by_id": self.env.uid,
                    "requested_at": fields.Datetime.now(),
                }
            )
            wo._fin_route("Write-off of BDT %.2f on %s: %s" % (wo.amount, invoice.name, wo.reason))
        return True

    def action_approve(self):
        for wo in self:
            if wo.state != "requested":
                raise UserError("Only a requested write-off is approved")
            if wo._dofa_current_tier() == "tier_0":
                wo._fin_approve_direct()
            else:
                wo.action_dofa_approve()
        return True

    def action_reject(self, reason=""):
        if not (reason or "").strip():
            raise UserError("State why the write-off is rejected")
        for wo in self:
            if wo.state != "requested":
                raise UserError("Only a requested write-off is rejected")
            if not self.env.su:
                require_role(self.env, GROUP_ACCOUNTANT, "Rejecting a write-off")
                if self.env.user in (wo.requested_by_id | wo.create_uid):
                    raise UserError("You requested this write-off; another person decides it.")
            wo._fin_void("rejected: %s" % reason)
            wo._guarded().write({"state": "rejected", "rejected_reason": reason[:250]})
        return True

    def _approval_on_rejected(self, comment):
        for wo in self.sudo().filtered(lambda w: w.state == "requested"):
            wo._guarded().write(
                {"state": "rejected", "rejected_reason": (comment or "M63 rejection")[:250]}
            )

    def _fin_before_approve(self):
        self.ensure_one()
        if self.state != "requested":
            raise UserError("Only a requested write-off is approved")
        invoice = self.invoice_id
        if invoice.state != "issued":
            raise UserError("Invoice %s is %s" % (invoice.name, invoice.state))
        if abs(invoice.amount_residual - self.amount) > 0.005:
            raise UserError(
                "Invoice %s now has %.2f outstanding, not the %.2f requested: request the "
                "write-off again." % (invoice.name, invoice.amount_residual, self.amount)
            )

    def _allowance(self):
        """(allowance account, available credit balance) of the IFRS 9 loss
        allowance: the provision account of the company's posted ECL runs,
        else the configured role cd_billing_engine.account_code.ecl_provision."""
        from .fix_ar_engine import _ar_account

        self.ensure_one()
        company = self.invoice_id.company_id
        run = (
            self.env["fix.ar.impairment"]
            .sudo()
            .search(
                [("company_id", "=", company.id), ("state", "=", "posted")],
                order="as_of desc, id desc",
                limit=1,
            )
        )
        account = run.provision_account_id or _ar_account(self.env, company, "ecl_provision")
        if not account:
            return self.env["account.account"], 0.0
        lines = (
            self.env["account.move.line"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("parent_state", "=", "posted"),
                    ("account_id", "=", account.id),
                ]
            )
        )
        return account, max(-sum(lines.mapped("balance")), 0.0)

    def _fin_after_approve(self):
        """Post: Dr loss allowance (up to its balance) + Dr bad-debt expense
        (the excess) / Cr AR, then close the invoice as written off."""
        from .fix_ar_engine import _ar_account

        self.ensure_one()
        wo = self.sudo()
        invoice = wo.invoice_id
        company = invoice.company_id
        allowance_acc, available = wo._allowance()
        use = round(min(wo.amount, available), 2) if allowance_acc else 0.0
        excess = round(wo.amount - use, 2)
        debit_lines = []
        if use > 0.005:
            debit_lines.append(("ecl_provision", allowance_acc, use, invoice.customer_id.id))
        if excess > 0.005:
            debit_lines.append(
                (
                    "writeoff_expense",
                    _ar_account(wo.env, company, "writeoff_expense"),
                    excess,
                    False,
                )
            )
        move = invoice._post_reversal_gl(
            "WRITE-OFF INV %s — %s" % (invoice.name, wo.reason),
            debit_lines,
            [("ar", _ar_account(wo.env, company, "ar"), wo.amount, invoice.customer_id.id)],
        )
        wo._guarded().write(
            {
                "state": "posted",
                "move_id": move.id,
                "allowance_account_id": allowance_acc.id if use > 0.005 else False,
                "allowance_amount": use,
                "expense_amount": excess,
            }
        )
        invoice._guarded().write({"state": "written_off"})
        publish(
            wo.env,
            "invoice.written_off",
            "fix.ar.invoice",
            invoice.id,
            {
                "invoice": invoice.name,
                "amount": wo.amount,
                "allowance_used": use,
                "expense": excess,
                "reason": (wo.reason or "")[:500],
            },
        )


class FixArConsolidatedBill(models.Model):
    """Consolidated corporate billing hook (T03, P04/P06-M03).
    Aggregates multiple ISSUED fix.ar.invoice records for a corporate partner
    into a monthly consolidated billing cycle (A08 M20-14: drafts — no number,
    no Mushak — are never billed)."""

    _name = "fix.ar.consolidated.bill"
    _description = "Consolidated AR Bill"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "period_end desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    customer_id = fields.Many2one(
        "res.partner", string="Corporate Customer", required=True, index=True, ondelete="restrict"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    bill_ref = fields.Char(string="Bill Reference", required=True, index=True)
    period_start = fields.Date(string="Period Start", required=True)
    period_end = fields.Date(string="Period End", required=True)
    invoice_ids = fields.Many2many("fix.ar.invoice", string="Included Invoices")
    total_taxable = fields.Monetary(
        string="Total Taxable", currency_field="currency_id", compute="_compute_totals", store=True
    )
    total_vat = fields.Monetary(
        string="Total VAT", currency_field="currency_id", compute="_compute_totals", store=True
    )
    total_payable = fields.Monetary(
        string="Total Payable", currency_field="currency_id", compute="_compute_totals", store=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("generated", "Generated"),
            ("sent", "Sent"),
            ("paid", "Paid"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state"}

    @api.depends(
        "invoice_ids.taxable_amount", "invoice_ids.vat_amount", "invoice_ids.total_payable"
    )
    def _compute_totals(self):
        for bill in self:
            bill.total_taxable = sum(bill.invoice_ids.mapped("taxable_amount"))
            bill.total_vat = sum(bill.invoice_ids.mapped("vat_amount"))
            bill.total_payable = sum(bill.invoice_ids.mapped("total_payable"))

    def action_generate(self):
        for bill in self:
            if bill.state != "draft":
                raise UserError("Bill %s is already %s" % (bill.bill_ref, bill.state))
            if not bill.invoice_ids:
                invoices = self.env["fix.ar.invoice"].search(
                    [
                        ("company_id", "=", bill.company_id.id),
                        ("customer_id", "=", bill.customer_id.id),
                        ("invoice_date", ">=", bill.period_start),
                        ("invoice_date", "<=", bill.period_end),
                        ("state", "=", "issued"),
                    ]
                )
                bill.invoice_ids = [(6, 0, invoices.ids)]
            unissued = bill.invoice_ids.filtered(lambda i: i.state != "issued")
            if unissued:
                raise UserError(
                    "A consolidated bill carries issued invoices only; %s %s not issued."
                    % (
                        ", ".join(i.name if i.name != "New" else "#%s" % i.id for i in unissued),
                        "is" if len(unissued) == 1 else "are",
                    )
                )
            foreign = bill.invoice_ids.filtered(
                lambda i, b=bill: i.customer_id.commercial_partner_id
                != b.customer_id.commercial_partner_id
                or i.company_id != b.company_id
            )
            if foreign:
                raise UserError("A consolidated bill carries this customer's invoices only.")
            bill._guarded().write({"state": "generated"})
            publish(
                self.env,
                "consolidated_bill.generated",
                "fix.ar.consolidated.bill",
                bill.id,
                {
                    "bill_ref": bill.bill_ref,
                    "customer_id": bill.customer_id.id,
                    "total_payable": bill.total_payable,
                    "invoice_count": len(bill.invoice_ids),
                },
            )

    def action_send(self):
        """Mark the consolidated bill sent. The delivery channel itself
        (portal/email/WhatsApp) is porting phase — never faked."""
        for bill in self:
            if bill.state != "generated":
                raise UserError("Generate the bill before sending")
            bill._guarded().write({"state": "sent"})
            publish(
                self.env,
                "consolidated_bill.sent",
                "fix.ar.consolidated.bill",
                bill.id,
                {"bill_ref": bill.bill_ref, "customer_id": bill.customer_id.id},
            )


# re-exported for the settlement / subscription modules
__all__ = [
    "AccessError",
    "FixArInvoice",
    "FixArWriteoff",
    "FixCreditNote",
    "ValidationError",
]
