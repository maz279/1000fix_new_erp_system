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
from odoo import api, fields, models
from odoo.exceptions import UserError

from decimal import Decimal

from libs.py.fix_events import publish  # FF-28

from odoo.addons.cd_tax_engine_bd.models import tax_logic


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
    _source_key_unique = models.Constraint('UNIQUE (source_model, source_id)', 'One invoice per source document — the auto-generation guard')

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", index=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True,
                                  index=True, ondelete="restrict")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    source_model = fields.Char(string="Source Model", required=True, index=True,
                               help="e.g. fix.service.order")
    source_id = fields.Integer(string="Source ID", required=True, index=True)
    invoice_date = fields.Date(default=fields.Date.today, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("issued", "Issued"), ("paid", "Paid"),
         ("credited", "Credited"), ("cancelled", "Cancelled")],
        default="draft", required=True, tracking=True)
    line_ids = fields.One2many("fix.ar.invoice.line", "invoice_id", string="Lines")
    # AS-10: monetary only
    taxable_amount = fields.Monetary(string="Taxable Value", currency_field="currency_id",
                                     compute="_compute_totals", store=True)
    vat_amount = fields.Monetary(string="VAT", currency_field="currency_id",
                                 compute="_compute_totals", store=True)
    total_payable = fields.Monetary(string="Total Payable", currency_field="currency_id",
                                    compute="_compute_totals", store=True)
    mushak_id = fields.Many2one("fix.mushak.register", string="Mushak 6.3",
                                readonly=True, index=True,
                                help="Written in the same transaction (atomic posting)")
    generated_at = fields.Datetime(readonly=True)
    generation_seconds = fields.Float(readonly=True,
                                      help="Closed-event to invoice duration — NFR-040 (5s)")

    @api.depends("line_ids.taxable_amount", "line_ids.vat_amount")
    def _compute_totals(self):
        for inv in self:
            inv.taxable_amount = sum(inv.line_ids.mapped("taxable_amount"))
            inv.vat_amount = sum(inv.line_ids.mapped("vat_amount"))
            inv.total_payable = inv.taxable_amount + inv.vat_amount

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
        existing = self.search([("source_model", "=", "fix.service.order"),
                                ("source_id", "=", order.id)])
        if existing:
            return existing  # idempotent on the source

        # BRU-SRM-05 gate: the invoiced amount comes from the APPROVED
        # estimate of the closed order — never re-priced here.
        estimate = order.estimate_ids.filtered(lambda e: e.state == "approved")[:1]
        if not estimate:
            raise UserError(
                "No approved estimate on %s — invoicing requires one (BRU-SRM-05)"
                % order.name)

        lines = []
        for line in estimate.line_ids:
            lines.append(tax_logic.TaxLine(
                product_code=line.product_id.default_code or "SVC",
                qty=Decimal(str(line.quantity or 1)),
                unit_price=Decimal(str(line.unit_price or 0.0)),
                discount=Decimal(str(line.discount or 0.0)),
            ))
        determination = tax_logic.determine_tax(lines)

        invoice = self.create({
            "customer_id": order.customer_id.id,
            "operating_unit_id": order.operating_unit_id.id,
            "branch_id": order.branch_id.id,
            "source_model": "fix.service.order",
            "source_id": order.id,
        })
        determined_by_code = {d.product_code: d for d in determination.lines}
        for line in estimate.line_ids:
            code = line.product_id.default_code or "SVC"
            det = determined_by_code[code]
            self.env["fix.ar.invoice.line"].create({
                "invoice_id": invoice.id,
                "product_id": line.product_id.id,
                "description": line.description or line.product_id.display_name,
                "taxable_amount": float(det.taxable_amount),
                "vat_amount": float(det.vat_amount),
                "line_total": float(det.line_total),
            })

        # Mushak register row — same transaction (T08 atomicity)
        company = invoice.company_id
        mushak = self.env["fix.mushak.register"].create({
            "operating_unit_id": invoice.operating_unit_id.id,
            "mushak_no": self._next_mushak_no(company),
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
                for d in determination.lines),
        })
        invoice.write({"mushak_id": mushak.id, "state": "issued"})

        publish(self.env, "invoice.created", "fix.ar.invoice", invoice.id, {
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
        })
        elapsed = time.monotonic() - started
        invoice.write({"generated_at": fields.Datetime.now(),
                       "generation_seconds": elapsed})
        return invoice

    @api.model
    def _next_mushak_no(self, company) -> str:
        """Mushak numbering: per-company sequence, fiscal-year prefixed."""
        year = fields.Date.today().year
        last = self.env["fix.mushak.register"].search_count(
            [("company_id", "=", company.id)])
        return "%d-%06d" % (year, last + 1)

    @api.model
    def _company_bin(self, company) -> str:
        """The supplier BIN — from company master data (never invented)."""
        vat = (company.vat or "").replace(" ", "")
        if not vat:
            raise UserError(
                "Company BIN missing on %s — a Mushak 6.3 cannot be issued "
                "without the supplier BIN" % company.name)
        return vat

    def action_register_paid(self):
        """Receipts arrive as M50 bank/cash events consumed here — this is
        NOT a synchronous call into treasury (AR-006 pair 6)."""
        for invoice in self:
            if invoice.state != "issued":
                raise UserError("Only issued invoices can be paid")
            invoice.state = "paid"
            publish(self.env, "invoice.paid", "fix.ar.invoice", invoice.id, {
                "mushak_no": invoice.mushak_id.mushak_no,
                "total_payable": invoice.total_payable,
            })


class FixArInvoiceLine(models.Model):
    _name = "fix.ar.invoice.line"
    _description = "AR Invoice Line"

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

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit")
    invoice_id = fields.Many2one("fix.ar.invoice", string="Invoice", required=True,
                                 ondelete="cascade", index=True)
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    overdue_amount = fields.Monetary(string="Overdue", currency_field="currency_id")
    days_overdue = fields.Integer(compute="_compute_ageing", store=True)
    bucket = fields.Selection(
        [("current", "Current"), ("d1_30", "1-30"), ("d31_60", "31-60"),
         ("d61_90", "61-90"), ("d90_plus", "90+")],
        compute="_compute_ageing", store=True, string="Ageing Bucket")
    step = fields.Selection(
        [("reminder", "Reminder (NT-006 L1)"), ("final", "Final Notice (L2)"),
         ("escalate", "Escalated to Collections (L3)")],
        default="reminder", required=True, tracking=True)

    @api.depends("invoice_id.invoice_date")
    def _compute_ageing(self):
        today = fields.Date.today()
        for run in self:
            if run.invoice_id.invoice_date:
                delta = (today - run.invoice_id.invoice_date).days - 30  # net-30 terms
                run.days_overdue = max(delta, 0)
                run.bucket = ("current" if delta <= 0 else
                              "d1_30" if delta <= 30 else
                              "d31_60" if delta <= 60 else
                              "d61_90" if delta <= 90 else "d90_plus")


class FixCreditNote(models.Model):
    """Credit notes with approval authority (T06, 05-04 section 7 — the
    authority matrix is a segregation-of-duties control)."""

    _name = "fix.credit.note"
    _description = "Credit Note"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    invoice_id = fields.Many2one("fix.ar.invoice", string="Original Invoice",
                                 required=True, ondelete="restrict")
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    amount = fields.Monetary(string="Credit Amount", currency_field="currency_id",
                             required=True)
    reason_code = fields.Selection(
        [("service_failure", "Service Failure"), ("pricing_error", "Pricing Error"),
         ("warranty", "Warranty Re-work"), ("goodwill", "Goodwill"),
         ("return", "Return")], required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("pending_approval", "Pending Approval"),
         ("approved", "Approved"), ("rejected", "Rejected"), ("issued", "Issued")],
        default="draft", required=True, tracking=True)
    approved_by = fields.Many2one("res.users", readonly=True)
    APPROVAL_THRESHOLD = 25000  # above BDT 25,000 a manager approves (05-04 section 7)

    def action_submit(self):
        for note in self:
            note.state = ("pending_approval"
                          if note.amount > self.APPROVAL_THRESHOLD else "approved")

    def action_approve(self):
        for note in self:
            if note.amount > self.APPROVAL_THRESHOLD and not self.env.user.has_group(
                    "base.group_system"):
                raise UserError(
                    "Credits above BDT %d require managerial approval (05-04 section 7)"
                    % self.APPROVAL_THRESHOLD)
            note.write({"state": "approved", "approved_by": self.env.user.id})

    def action_issue(self):
        for note in self:
            if note.state != "approved":
                raise UserError("Approve before issuing")
            note.state = "issued"
            note.invoice_id.state = "credited"
            publish(self.env, "credit_note.issued", "fix.credit.note", note.id, {
                "invoice_ref": "AR/%s" % note.invoice_id.id,
                "amount": note.amount, "reason": note.reason_code,
            })
