# cd_ap_ext — M52 Accounts Payable core (P06-M04, CD-M52-01).
#
# T03: THREE-WAY MATCH lives HERE, not in M16 (AR-006 section 4.1 pair 11)
# — the seam is M52's, consuming requisition (M16) and goods-receipt events.
# G3-06: an unmatched vendor invoice is BLOCKED, not warned about.
# T04: TDS determination is a synchronous call into M51 (pair 8).
# T06: payment requests to M50 go as EVENTS — no synchronous back-call.
from odoo import api, fields, models
from odoo.exceptions import UserError

from decimal import Decimal

from libs.py.fix_events import publish  # FF-28

from cd_tax_engine_bd.models import tax_logic


class FixVendorInvoice(models.Model):
    """A vendor invoice entering the three-way match (T03)."""

    _name = "fix.vendor.invoice"
    _description = "Vendor Invoice (three-way match)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "invoice_date desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    vendor_id = fields.Many2one("res.partner", string="Vendor", required=True,
                                index=True, ondelete="restrict")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    invoice_ref = fields.Char(string="Vendor Invoice Ref", required=True, index=True)
    invoice_date = fields.Date(default=fields.Date.today, required=True)
    line_ids = fields.One2many("fix.vendor.invoice.line", "invoice_id", string="Lines")
    subtotal = fields.Monetary(string="Subtotal", currency_field="currency_id",
                               compute="_compute_totals", store=True)
    tds_amount = fields.Monetary(string="TDS Deducted", currency_field="currency_id",
                                 compute="_compute_totals", store=True)
    total_payable = fields.Monetary(string="Total Payable", currency_field="currency_id",
                                    compute="_compute_totals", store=True)
    # Three-way match (T03)
    requisition_id = fields.Many2one("fix.purchase.order", string="Purchase Order",
                                     index=True, ondelete="restrict")
    match_state = fields.Selection(
        [("unmatched", "Unmatched"), ("matched", "Matched"), ("blocked", "Blocked")],
        compute="_compute_match", store=True, string="Three-Way Match")
    match_detail = fields.Text(readonly=True)

    @api.depends("line_ids.line_total", "line_ids.tds_category")
    def _compute_totals(self):
        for inv in self:
            subtotal = sum(inv.line_ids.mapped("line_total"))
            tds = sum(
                tax_logic.determine_tds(
                    line.tds_category or "service_general",
                    Decimal(str(line.line_total)),
                    exempt_certificate=bool(line.tds_exempt),
                ).tds_amount
                for line in inv.line_ids
            )
            inv.subtotal = subtotal
            inv.tds_amount = tds
            inv.total_payable = subtotal - tds

    @api.depends("line_ids", "requisition_id")
    def _compute_match(self):
        """G3-06: the three-way check — invoice lines vs the PO's ordered
        and RECEIVED quantities. Any variance beyond tolerance BLOCKS."""
        TOLERANCE = Decimal("0.01")
        for inv in self:
            if not inv.requisition_id:
                inv.match_state = "unmatched"
                inv.match_detail = "No purchase order linked"
                continue
            received = {r.product_id.id: r.qty_received for r in inv.requisition_id.line_ids}
            ordered = {r.product_id.id: r.qty_ordered for r in inv.requisition_id.line_ids}
            problems = []
            for line in inv.line_ids:
                pid = line.product_id.id
                if pid not in ordered:
                    problems.append("%s: not on the PO" % line.description)
                    continue
                if Decimal(str(received.get(pid, 0.0))) < Decimal(str(line.quantity)):
                    problems.append(
                        "%s: received %.2f < invoiced %.2f"
                        % (line.description, received.get(pid, 0.0), line.quantity))
                if Decimal(str(line.unit_price)) > Decimal(str(
                        inv.requisition_id.line_ids.filtered(
                            lambda l: l.product_id.id == pid)[:1].unit_price or 0)) + TOLERANCE:
                    problems.append("%s: price above PO" % line.description)
            if problems:
                inv.match_state = "blocked"
                inv.match_detail = "\n".join(problems)
            else:
                inv.match_state = "matched"
                inv.match_detail = "PO / receipt / invoice reconciled"

    def action_request_payment(self):
        """T06: M52 raises payment requests as EVENTS — treasury executes
        and publishes confirmation. No synchronous call into M50."""
        for inv in self:
            if inv.match_state != "matched":
                raise UserError(
                    "G3-06: an unmatched vendor invoice cannot be paid "
                    "(state: %s — %s)" % (inv.match_state, inv.match_detail))
            publish(self.env, "payment.requested", "fix.vendor.invoice", inv.id, {
                "vendor_id": inv.vendor_id.id,
                "amount": inv.total_payable,
                "currency": inv.currency_id.name,
                "invoice_ref": inv.invoice_ref,
            })


class FixVendorInvoiceLine(models.Model):
    _name = "fix.vendor.invoice.line"
    _description = "Vendor Invoice Line"

    invoice_id = fields.Many2one("fix.vendor.invoice", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Product", required=True)
    description = fields.Char(required=True)
    quantity = fields.Float(required=True, default=1.0)
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id",
                                 required=True)
    line_total = fields.Monetary(string="Line Total", currency_field="currency_id",
                                 compute="_compute_line", store=True)
    tds_category = fields.Selection(
        [(c, c) for c in tax_logic.TDS_DEFAULT_RATES],
        string="TDS Category", default="service_general")
    tds_exempt = fields.Boolean(default=False,
                                help="Vendor holds a valid exempt certificate (ATS)")

    @api.depends("quantity", "unit_price")
    def _compute_line(self):
        for line in self:
            line.line_total = line.quantity * line.unit_price


class FixExpenseClaim(models.Model):
    """T02: employee expense on the M21-core employee master (MV-01)."""

    _name = "fix.expense.claim"
    _description = "Expense Claim"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True,
                                  index=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    description = fields.Char(required=True)
    amount = fields.Monetary(string="Claimed Amount", currency_field="currency_id",
                             required=True)
    expense_date = fields.Date(default=fields.Date.today, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"),
         ("approved", "Approved"), ("paid", "Paid"), ("rejected", "Rejected")],
        default="draft", required=True, tracking=True)
    APPROVAL_THRESHOLD = 25000

    def action_submit(self):
        for claim in self:
            if claim.amount <= 0:
                raise UserError("A claim must carry a positive amount")
            claim.state = ("submitted" if claim.amount <= self.APPROVAL_THRESHOLD
                           else "draft")  # above threshold: manager approval activity first

    def action_approve(self):
        for claim in self:
            claim.state = "approved"
            # Payment rides the same event path as vendor invoices (M50 executes)
            publish(self.env, "payment.requested", "fix.expense.claim", claim.id, {
                "employee_id": claim.employee_id.id,
                "amount": claim.amount,
                "currency": claim.currency_id.name,
                "invoice_ref": "EXP/%s" % claim.id,
            })
