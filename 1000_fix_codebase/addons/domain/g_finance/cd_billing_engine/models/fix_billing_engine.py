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
    amount_residual = fields.Monetary(
        string="Residual",
        currency_field="currency_id",
        compute="_compute_payment",
        store=True,
    )

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
            inv.amount_residual = max(
                inv.total_payable - inv.amount_paid - inv.credited_amount - inv.vds_settled_amount,
                0.0,
            )

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

    def _ar_posting_dims(self, branch_id=None):
        """Dimensions for every AR-family GL posting: the branch, plus the
        configured default cost centre and business line (COA-03 may require
        any of them per account). Defaults come from config params so each
        deployment sets its own; postings never invent values beyond these
        configured defaults."""
        param = self.env["ir.config_parameter"].sudo().get_param
        return {
            "branch_id": branch_id or False,
            "cost_centre": param("cd_billing_engine.default_cost_centre") or "CORP",
            "business_line": param("cd_billing_engine.default_business_line") or "RETAIL",
        }

    INVOICE_SEQUENCE_CODE = "fix.ar.invoice"

    @api.model
    def _invoice_sequence(self, company):
        """The company's own invoice-number sequence — copied once from the
        module template (the Mushak pattern, without fiscal-year ranges:
        FR-ARB-005 gapless per entity)."""
        Sequence = self.env["ir.sequence"].sudo()
        seq = Sequence.search(
            [("code", "=", self.INVOICE_SEQUENCE_CODE), ("company_id", "=", company.id)], limit=1
        )
        if not seq:
            template = self.env.ref(
                "cd_billing_engine.seq_fix_ar_invoice", raise_if_not_found=False
            )
            if not template:
                raise UserError(
                    "The invoice numbering sequence is missing — upgrade cd_billing_engine."
                )
            seq = template.copy(
                {
                    "name": "AR Invoice No — %s" % company.name,
                    "company_id": company.id,
                    "date_range_ids": [],
                }
            )
        return seq

    def _next_invoice_no(self) -> str:
        self.ensure_one()
        return self._invoice_sequence(self.company_id).next_by_id(sequence_date=self.invoice_date)

    def _post_issue_gl(self):
        """The issue posting through M19's hardened engine (source='ar'):
        Dr AR control / Cr Revenue / Cr VAT output, branch dimension on every
        line. Companies without the accounts/journal SKIP with an honest
        gl_note — invoicing is never blocked by GL configuration."""
        from .fix_ar_engine import _ar_account, _post_ar_move

        for inv in self:
            if inv.total_payable <= 0.005:
                inv.gl_note = "Zero-total invoice — no GL effect"
                return
            company = inv.company_id
            ar = _ar_account(inv.env, company, "ar")
            revenue = _ar_account(inv.env, company, inv._revenue_role())
            vat = _ar_account(inv.env, company, "vat_output")
            if not (ar and revenue and vat):
                inv.gl_note = (
                    "GL not posted: AR/revenue/VAT account unconfigured for %s" % company.name
                )
                return
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
            )
            inv.write({"posted_move_id": move.id if move else False, "gl_note": note or False})
            if move and inv.mushak_id:
                # the flag the register has carried unset since day one
                inv.mushak_id.sudo().posted = True

    def _post_reversal_gl(self, label, debit_lines, credit_lines):
        """A mirror posting for cancellations/write-offs; refuses (never
        skips) when the posting accounts are missing — these are finance
        actions, the GL IS the point."""
        from .fix_ar_engine import _ar_journal, _post_ar_move

        self.ensure_one()
        journal = _ar_journal(self.env, self.company_id)
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
        move, note = _post_ar_move(
            self.env,
            self.company_id,
            fields.Date.today(),
            label,
            lines,
            dims,
            source="ar",
        )
        if not move:
            raise UserError("Posting refused: %s" % (note or "engine refused the move"))
        return move

    def action_cancel(self, reason=""):
        """FR-ARB-011: unpaid invoices only, approved reason, number
        retained; the GL mirror is posted when the issue was posted."""
        from .fix_ar_engine import _ar_account

        for inv in self:
            if inv.state not in ("draft", "issued"):
                raise UserError("Only draft/issued invoices can be cancelled")
            if (
                inv.amount_paid > 0.005
                or inv.credited_amount > 0.005
                or inv.vds_settled_amount > 0.005
            ):
                raise UserError(
                    "Paid/credited invoices cannot be cancelled — issue a credit note instead"
                )
            if not (reason or "").strip():
                raise UserError("A cancellation reason is required (FR-ARB-011)")
            if inv.posted_move_id:
                ar = _ar_account(inv.env, inv.company_id, "ar")
                revenue = _ar_account(inv.env, inv.company_id, inv._revenue_role())
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
                )
            inv.state = "cancelled"
            publish(
                inv.env,
                "invoice.cancelled",
                "fix.ar.invoice",
                inv.id,
                {"invoice": inv.name, "reason": reason[:500]},
            )

    def action_write_off(self, reason=""):
        """FR-ARB-041: authority-matrix write-off — above BDT 25,000 a
        manager approves (the credit-note ladder)."""
        from .fix_ar_engine import _ar_account

        for inv in self:
            if inv.state != "issued":
                raise UserError("Only issued invoices can be written off")
            if inv.amount_residual <= 0.005:
                raise UserError("Nothing residual to write off on %s" % inv.name)
            if not (reason or "").strip():
                raise UserError("A write-off reason is required (FR-ARB-041)")
            if inv.amount_residual > 25000 and not self.env.user.has_group("base.group_system"):
                raise UserError(
                    "Write-offs above BDT 25,000 require managerial approval (05-04 section 7)"
                )
            writeoff = _ar_account(inv.env, inv.company_id, "writeoff_expense")
            ar = _ar_account(inv.env, inv.company_id, "ar")
            inv._post_reversal_gl(
                "WRITE-OFF INV %s — %s" % (inv.name, reason),
                [("writeoff_expense", writeoff, inv.amount_residual, False)],
                [("ar", ar, inv.amount_residual, inv.customer_id.id)],
            )
            inv.state = "written_off"
            publish(
                inv.env,
                "invoice.written_off",
                "fix.ar.invoice",
                inv.id,
                {"invoice": inv.name, "amount": inv.amount_residual, "reason": reason[:500]},
            )

    @api.model
    def create_manual_invoice(self, vals, lines, reason_code):
        """FR-ARB-010: the manual exception path. A reason code is mandatory
        and the invoice starts as draft — issue (Mushak + number + GL) is a
        separate deliberate step."""
        if not (reason_code or "").strip():
            raise UserError("Manual invoices need a reason code (FR-ARB-010)")
        vals = dict(vals)
        vals.update({"source_model": "manual", "source_id": 0, "manual_reason": reason_code})
        invoice = self.create(vals)
        # keep the one-invoice-per-source guard meaningful for manual rows;
        # flushed immediately so a following manual create cannot race the key
        invoice.source_id = -invoice.id
        self.env.flush_all()
        for line in lines:
            self.env["fix.ar.invoice.line"].create(dict(line, invoice_id=invoice.id))
        return invoice

    def action_issue(self):
        """Issue a manual/draft invoice: draws the gapless number, writes the
        Mushak 6.3 row, posts to GL, publishes invoice.created."""
        for inv in self:
            if inv.state != "draft":
                raise UserError("Only draft invoices can be issued")
            if not inv.line_ids:
                raise UserError("An invoice needs at least one line")
            if inv.total_payable <= 0.005:
                raise UserError("Invoice total must be positive")
            if not (inv.manual_reason or "").strip():
                raise UserError("Manual invoices need a reason code (FR-ARB-010)")
            # A03 audit W5 (M33-3): the draft-party switch (no-op under 'allow').
            if hasattr(inv.customer_id, "_fix_assert_party_usable_downstream"):
                inv.customer_id._fix_assert_party_usable_downstream("an invoice")
            inv._credit_hold_check()
            company = inv.company_id
            mushak = self.env["fix.mushak.register"].create(
                {
                    "operating_unit_id": inv.operating_unit_id.id,
                    "mushak_no": self._next_mushak_no(company, inv.invoice_date),
                    "invoice_ref": "AR/%s" % inv.id,
                    "invoice_date": inv.invoice_date,
                    "supplier_name": company.name,
                    "supplier_bin": self._company_bin(company),
                    "customer_name": inv.customer_id.name,
                    "customer_bin": inv.customer_id.vat or "",
                    "taxable_amount": inv.taxable_amount,
                    "vat_amount": inv.vat_amount,
                    "total_payable": inv.total_payable,
                    "treatment_summary": "manual entry (%s)" % inv.manual_reason,
                }
            )
            inv.write({"name": inv._next_invoice_no(), "mushak_id": mushak.id, "state": "issued"})
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
                    "customer_name": inv.customer_id.name,
                    "customer_bin": inv.customer_id.vat or "",
                    "taxable_amount": inv.taxable_amount,
                    "vat_amount": inv.vat_amount,
                    "total_payable": inv.total_payable,
                    "treatment_summary": mushak.treatment_summary,
                    "operating_unit_id": inv.operating_unit_id.id,
                },
            )
            inv.write({"generated_at": fields.Datetime.now(), "generation_seconds": 0.0})
            inv._post_issue_gl()

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
        estimate = order.estimate_ids.filtered(lambda e: e.state == "approved")[:1]
        if not estimate:
            raise UserError(
                "No approved estimate on %s — invoicing requires one (BRU-SRM-05)" % order.name
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
        invoice.write(
            {
                "mushak_id": mushak.id,
                "state": "issued",
                "name": invoice._next_invoice_no(),
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
        # the M19 posting the docstrings always claimed (skips with an
        # honest gl_note when the company's GL is unconfigured)
        invoice._post_issue_gl()
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
        return "; ".join(parts)

    def _mark_paid(self):
        """The evidence-bearing paid transition for the close-out and VDS
        settlement paths (receipt allocations keep their own)."""
        for invoice in self:
            invoice.write({"state": "paid", "paid_date": fields.Date.today()})
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
        created = advanced = suppressed = skipped = 0
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
            if dunnable <= 0.005:
                if existing and not existing.suppressed:
                    existing.write({"suppressed": True, "suppression_reason": "dispute"})
                    suppressed += 1
                elif not existing:
                    skipped += 1
                continue
            if existing:
                if existing.suppressed:
                    existing.write({"suppressed": False, "suppression_reason": False})
                nxt, grace = self.LADDER.get(existing.step, (False, 0))
                if (
                    nxt
                    and existing.step_date
                    and (today - existing.step_date).days >= grace
                    and existing.step != "escalate"
                ):
                    existing.write({"step": nxt, "step_date": today, "overdue_amount": dunnable})
                    advanced += 1
                else:
                    existing.write({"overdue_amount": dunnable})
            else:
                self.create(
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
        }

    def _cron_run_dunning(self):
        """Daily cron entry: run the ladder."""
        self.action_run_dunning()

    def action_suppress(self, reason):
        for run in self:
            if reason not in ("dispute", "payment_plan", "strategic"):
                raise UserError("Pick a suppression reason (FR-ARB-033)")
            run.write({"suppressed": True, "suppression_reason": reason})


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
            ("subscription_refund", "Subscription Cancellation Refund"),
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
    issued_at = fields.Datetime(readonly=True, copy=False)
    posted_move_id = fields.Many2one("account.move", string="GL Move", readonly=True, copy=False)
    gl_note = fields.Char(readonly=True, copy=False)
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
        """Issue = apply + post. Partial credits keep the invoice issued with
        a residual; only a fully-credited invoice flips to 'credited'. The GL
        mirror reverses revenue/VAT pro-rata — a credit note never invents
        VAT relief beyond the invoice's own ratio."""
        for note in self:
            if note.state != "approved":
                raise UserError("Approve before issuing")
            invoice = note.invoice_id
            if invoice.state not in ("issued", "paid"):
                raise UserError(
                    "Credit notes apply to issued/paid invoices only (state: %s)" % invoice.state
                )
            if note.amount > invoice.total_payable + 0.005:
                raise UserError(
                    "Credit %s exceeds invoice total %s" % (note.amount, invoice.total_payable)
                )
            note.write({"state": "issued", "issued_at": fields.Datetime.now()})
            note._post_credit_gl()
            # partial application: only fully-credited invoices flip state
            if invoice.amount_residual <= 0.005:
                invoice.state = "credited"
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

    def _post_credit_gl(self):
        """The statutory mirror posting (FR-ARB-039): Dr Revenue + Dr VAT
        pro-rata / Cr AR — only when the invoice itself posted to GL."""
        from .fix_ar_engine import _ar_account, _post_ar_move

        for note in self:
            invoice = note.invoice_id
            if not invoice.posted_move_id:
                note.gl_note = "GL not posted: invoice %s has no GL move" % invoice.name
                continue
            company = invoice.company_id
            ar = _ar_account(note.env, company, "ar")
            revenue = _ar_account(note.env, company, invoice._revenue_role())
            vat = _ar_account(note.env, company, "vat_output")
            if not (ar and revenue and vat):
                note.gl_note = "GL not posted: accounts unconfigured for %s" % company.name
                continue
            ratio = (invoice.vat_amount / invoice.total_payable) if invoice.total_payable else 0.0
            vat_part = note.amount * ratio
            revenue_part = note.amount - vat_part
            _dims = invoice._ar_posting_dims(invoice.branch_id.id)
            dims = dict.fromkeys(range(3), _dims)
            move, gl_note = _post_ar_move(
                note.env,
                company,
                fields.Date.today(),
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
            )
            note.write({"posted_move_id": move.id if move else False, "gl_note": gl_note or False})


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

    def action_send(self):
        """Mark the consolidated bill sent. The delivery channel itself
        (portal/email/WhatsApp) is porting phase — never faked."""
        for bill in self:
            if bill.state != "generated":
                raise UserError("Generate the bill before sending")
            bill.state = "sent"
            publish(
                self.env,
                "consolidated_bill.sent",
                "fix.ar.consolidated.bill",
                bill.id,
                {"bill_ref": bill.bill_ref, "customer_id": bill.customer_id.id},
            )
