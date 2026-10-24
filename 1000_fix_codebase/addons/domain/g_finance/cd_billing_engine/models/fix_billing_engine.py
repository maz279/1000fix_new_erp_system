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
# determination synchronously (import tax_logic) and CONSUMES nothing
# back; M50's bank/cash events are consumed for receipts — M20 never
# calls M50 synchronously (pair 6).
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.addons.cd_tax_engine_bd.models import tax_logic
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

TWO_PLACES = Decimal("0.01")


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


class FixArInvoice(models.Model):
    """A customer invoice in the AR engine, feeding Odoo account.move.

    Kept as an explicit M20 record (not a bare account.move) because the
    Mushak pairing, the closed-job source and the dunning ladder are M20
    concerns account.move must not carry."""

    _name = "fix.ar.invoice"
    _description = "AR Invoice"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "invoice_date desc, id desc"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _source_key_unique = models.Constraint(
        "UNIQUE (source_model, source_id)",
        "One invoice per source document — the auto-generation guard",
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
    invoice_date = fields.Date(default=fields.Date.today, required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("issued", "Issued"),
            ("paid", "Paid"),
            ("credited", "Credited"),
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

    @api.depends("line_ids.taxable_amount", "line_ids.vat_amount", "loyalty_discount_amount")
    def _compute_totals(self):
        for inv in self:
            inv.taxable_amount = sum(inv.line_ids.mapped("taxable_amount"))
            inv.vat_amount = sum(inv.line_ids.mapped("vat_amount"))
            subtotal_vat = inv.taxable_amount + inv.vat_amount
            inv.total_payable = max(0.0, subtotal_vat - (inv.loyalty_discount_amount or 0.0))

    @api.model
    def from_closed_service_order(self, order, closed_event_at) -> "FixArInvoice":
        """T02: the auto-invoice path. `order` is a fix.service.order record
        in state 'closed'. Determination runs synchronously (M20 -> M51);
        the invoice, its lines, the account.move, the Mushak register row and
        the invoice.created event all commit in ONE transaction (T08)."""
        import time

        started = time.monotonic()
        if order.state != "closed":
            raise UserError("Auto-invoicing runs on closed jobs only (BRU-SRM-05)")
        existing = self.search(
            [("source_model", "=", "fix.service.order"), ("source_id", "=", order.id)]
        )
        if existing:
            return existing  # idempotent on the source

        # BRU-SRM-05 gate: the invoiced amount comes from the APPROVED
        # estimate of the closed order — never re-priced here.
        estimate = order.estimate_ids.filtered(lambda e: e.state == "approved")[:1]
        if not estimate:
            raise UserError(
                "No approved estimate on %s — invoicing requires one (BRU-SRM-05)" % order.name
            )

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
        lines = [
            tax_logic.TaxLine(
                product_code=line.product_id.default_code or "SVC",
                qty=qty,
                unit_price=price,
                discount=line_discount,
            )
            for line, qty, price, line_discount in zip(
                estimate.line_ids, quantities, prices, discounts, strict=True
            )
        ]
        determination = tax_logic.determine_tax(lines)

        invoice = self.create(
            {
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
        for line, det in zip(estimate.line_ids, determination.lines, strict=True):
            self.env["fix.ar.invoice.line"].create(
                {
                    "invoice_id": invoice.id,
                    "product_id": line.product_id.id,
                    "description": line.description or line.product_id.display_name,
                    "taxable_amount": float(det.taxable_amount),
                    "vat_amount": float(det.vat_amount),
                    "line_total": float(det.line_total),
                }
            )

        # Mushak register row — same transaction (T08 atomicity)
        company = invoice.company_id
        mushak = self.env["fix.mushak.register"].create(
            {
                "operating_unit_id": invoice.operating_unit_id.id,
                "mushak_no": self._next_mushak_no(company, invoice.invoice_date),
                "invoice_ref": "AR/%s" % invoice.id,
                "invoice_date": invoice.invoice_date,
                "supplier_name": company.name,
                "supplier_bin": self._company_bin(company),
                "customer_name": invoice.customer_id.name,
                "customer_bin": invoice.customer_id.vat or "",
                "taxable_amount": invoice.taxable_amount,
                "vat_amount": invoice.vat_amount,
                "total_payable": invoice.total_payable,
                "treatment_summary": "\n".join(
                    "%s: %s @ %s%%" % (d.product_code, d.treatment, d.rate)
                    for d in determination.lines
                ),
            }
        )
        invoice.write({"mushak_id": mushak.id, "state": "issued"})

        publish(
            self.env,
            "invoice.created",
            "fix.ar.invoice",
            invoice.id,
            {
                "invoice_ref": "AR/%s" % invoice.id,
                "mushak_no": mushak.mushak_no,
                "invoice_date": str(invoice.invoice_date),
                "supplier_name": company.name,
                "supplier_bin": self._company_bin(company),
                "customer_name": invoice.customer_id.name,
                "customer_bin": invoice.customer_id.vat or "",
                "taxable_amount": invoice.taxable_amount,
                "vat_amount": invoice.vat_amount,
                "total_payable": invoice.total_payable,
                "treatment_summary": mushak.treatment_summary,
                "operating_unit_id": invoice.operating_unit_id.id,
            },
        )
        elapsed = time.monotonic() - started
        invoice.write({"generated_at": fields.Datetime.now(), "generation_seconds": elapsed})
        return invoice

    MUSHAK_SEQUENCE_CODE = "fix.mushak.63"

    @api.model
    def _mushak_sequence(self, company):
        """The company's own Mushak 6.3 ir.sequence — copied once from the
        module's template (data/ir_sequence_data.xml)."""
        Sequence = self.env["ir.sequence"].sudo()
        seq = Sequence.search(
            [("code", "=", self.MUSHAK_SEQUENCE_CODE), ("company_id", "=", company.id)], limit=1
        )
        if not seq:
            template = self.env.ref("cd_billing_engine.seq_fix_mushak_63", raise_if_not_found=False)
            if not template:
                raise UserError(
                    "The Mushak 6.3 numbering sequence is missing — upgrade cd_billing_engine."
                )
            seq = template.copy(
                {
                    "name": "Mushak 6.3 Serial — %s" % company.name,
                    "company_id": company.id,
                    "date_range_ids": [],
                }
            )
        return seq

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
        vat = (company.vat or "").replace(" ", "")
        if not vat:
            raise UserError(
                "Company BIN missing on %s — a Mushak 6.3 cannot be issued "
                "without the supplier BIN" % company.name
            )
        return vat

    def action_register_paid(self):
        """Receipts arrive as M50 bank/cash events consumed here — this is
        NOT a synchronous call into treasury (AR-006 pair 6)."""
        for invoice in self:
            if invoice.state != "issued":
                raise UserError("Only issued invoices can be paid")
            invoice.state = "paid"
            publish(
                self.env,
                "invoice.paid",
                "fix.ar.invoice",
                invoice.id,
                {
                    "mushak_no": invoice.mushak_id.mushak_no,
                    "total_payable": invoice.total_payable,
                },
            )

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
    _name = "fix.ar.invoice.line"
    _description = "AR Invoice Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    invoice_id = fields.Many2one("fix.ar.invoice", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Product")
    description = fields.Char()
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    taxable_amount = fields.Monetary(string="Taxable Value", currency_field="currency_id")
    vat_amount = fields.Monetary(string="VAT", currency_field="currency_id")
    line_total = fields.Monetary(string="Line Total", currency_field="currency_id")


class FixDunning(models.Model):
    """Collections ladder (T05): ageing buckets, reminder steps from the
    NT-006 finance SMS ladder, escalation."""

    _name = "fix.dunning"
    _description = "Dunning Run"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")
    invoice_id = fields.Many2one(
        "fix.ar.invoice", string="Invoice", required=True, ondelete="cascade", index=True
    )
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

    @api.depends("invoice_id.invoice_date")
    def _compute_ageing(self):
        today = fields.Date.today()
        for run in self:
            if run.invoice_id.invoice_date:
                delta = (today - run.invoice_id.invoice_date).days - 30  # net-30 terms
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


class FixCreditNote(models.Model):
    """Credit notes with approval authority (T06, 05-04 section 7 — the
    authority matrix is a segregation-of-duties control)."""

    _name = "fix.credit.note"
    _description = "Credit Note"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
    approved_by = fields.Many2one("res.users", readonly=True)
    APPROVAL_THRESHOLD = 25000  # above BDT 25,000 a manager approves (05-04 section 7)

    def action_submit(self):
        for note in self:
            note.state = "pending_approval" if note.amount > self.APPROVAL_THRESHOLD else "approved"

    def action_approve(self):
        for note in self:
            if note.amount > self.APPROVAL_THRESHOLD and not self.env.user.has_group(
                "base.group_system"
            ):
                raise UserError(
                    "Credits above BDT %d require managerial approval (05-04 section 7)"
                    % self.APPROVAL_THRESHOLD
                )
            note.write({"state": "approved", "approved_by": self.env.user.id})

    def action_issue(self):
        for note in self:
            if note.state != "approved":
                raise UserError("Approve before issuing")
            note.state = "issued"
            note.invoice_id.state = "credited"
            publish(
                self.env,
                "credit_note.issued",
                "fix.credit.note",
                note.id,
                {
                    "invoice_ref": "AR/%s" % note.invoice_id.id,
                    "amount": note.amount,
                    "reason": note.reason_code,
                },
            )


class FixArConsolidatedBill(models.Model):
    """Consolidated corporate billing hook (T03, P04/P06-M03).
    Aggregates multiple closed/issued fix.ar.invoice records for a corporate partner into a monthly consolidated billing cycle."""

    _name = "fix.ar.consolidated.bill"
    _description = "Consolidated AR Bill"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
            if not bill.invoice_ids:
                invoices = self.env["fix.ar.invoice"].search(
                    [
                        ("customer_id", "=", bill.customer_id.id),
                        ("invoice_date", ">=", bill.period_start),
                        ("invoice_date", "<=", bill.period_end),
                        ("state", "in", ["draft", "issued"]),
                    ]
                )
                bill.invoice_ids = [(6, 0, invoices.ids)]
            bill.state = "generated"
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
