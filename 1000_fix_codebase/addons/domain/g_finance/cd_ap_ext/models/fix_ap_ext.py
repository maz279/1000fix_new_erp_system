# cd_ap_ext — M52 Accounts Payable core (P06-M04, CD-M52-01).
#
# T03: THREE-WAY MATCH lives HERE, not in M16 (AR-006 section 4.1 pair 11)
# — the seam is M52's, consuming requisition (M16) and goods-receipt events.
# G3-06: an unmatched vendor invoice is BLOCKED, not warned about.
# T04: TDS determination is a synchronous call into M51 (pair 8) — since the
# A08 build it reads M51's EFFECTIVE-DATED Tax Rate Master (ITA 2023
# sections), with the non-filer multiplier from the Vendor Tax Profile.
# T06: payment requests to M50 go as EVENTS — no synchronous back-call;
# payment RUNS create fix.payment.execution rows (fix_ap_payment_run.py).
#
# A08 approval workflow: draft -> to_approve -> approved (| rejected), an
# amount-based matrix (fix.ap.approval.rule) with segregation of duties and
# an append-only approver log. Final approval posts the bill to the GL and
# records the TDS/VDS deductions and the input VAT credit.
from collections import defaultdict
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.addons.cd_requisition.models.fix_requisition import bdt_rate, float_param
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .ap_gl import ap_account, ap_journal, post_ap_move
from .fix_ap_controls import PARAM_HIGHER_SIGNS_LOWER, bool_param, require_finance

TWO = Decimal("0.01")

# A06 D8 (owner decision 20 Nov 2026): with no approved tolerance row, a PO bill
# matches at up to +2 % or +BDT 500 a unit over the approved price, whichever is
# larger, and exactly on quantity. Config-param defaults, changed by Finance.
PARAM_TOL_PRICE_PCT = "cd_ap_ext.match_price_tolerance_pct"
PARAM_TOL_PRICE_ABS = "cd_ap_ext.match_price_tolerance_abs"
PARAM_TOL_QTY_PCT = "cd_ap_ext.match_qty_tolerance_pct"
DEFAULT_TOL_PRICE_PCT = 2.0
DEFAULT_TOL_PRICE_ABS = 500.0
DEFAULT_TOL_QTY_PCT = 0.0

# TDS categories = Tax Rate Master codes (kind tds). The first seven are the
# historical engine keys (vendor portal and existing bills use them).
TDS_CATEGORIES = [
    ("service_general", "Services - other (s.90)"),
    ("supply_of_goods", "Supply of goods (s.89)"),
    ("service_contractor", "Contract execution (s.89)"),
    ("professional_fees", "Advisory / consultancy (s.90)"),
    ("commission", "Commission / fees (s.94)"),
    ("rent_commercial", "Rent of premises (s.109)"),
    ("transport", "Transport / carriage"),
    ("technical_services", "Technical services (s.90)"),
    ("repair_platform", "Platform repair services (s.90)"),
    ("courier_training_event", "Catering / event / courier / training (s.90)"),
    ("manpower_gross", "Cleaning / security / manpower on gross (s.90)"),
]

# fields of a submitted / approved bill that may no longer change. A08
# M52-5: bill_type was not locked, so an approved unmatched PO bill was
# re-typed non_po and became payable without a match.
LOCKED_FIELDS = {
    "vendor_id",
    "invoice_date",
    "line_ids",
    "vat_amount",
    "vds_rate_id",
    "requisition_id",
    "currency_id",
    "company_id",
    "bill_type",
    "invoice_ref",
    "operating_unit_id",
    "payment_term_days",
    "due_date",
    "supplier_mushak_no",
    "payment_channel",
    "import_order_ref",
}

# A08 M52-2/-3/-4 (F3): workflow and stamp fields only a transition sets.
# approval_state was written to "approved" by an accountant (no GL) and paid;
# submitted_by was rewritten to self-approve; approval_levels_required was
# forged to 1 on a 600,000 bill; payment_state reset to not_paid paid twice.
GUARDED_FIELDS = {
    "approval_state",
    "approval_level",
    "approval_levels_required",
    "submitted_by",
    "payment_state",
    "move_id",
    "input_credit_id",
    "match_state",
    "match_detail",
    "payment_move_id",
    "payment_failure",
    "returns_at_registration",
    "advance_applied",
}

# G5: returns to vendor that count in the match once their goods have left
RTV_GONE_STATES = ("shipped", "credited")


def _q(value):
    return float(Decimal(str(value or 0)).quantize(TWO, ROUND_HALF_UP))


# Match states a bill may be paid in: a reconciled three-way match, or a
# non-PO bill (approval-controlled).
PAYABLE_MATCH_STATES = ("matched", "not_required")


def tolerance_allowance(basis, price_pct, price_abs):
    """FR-APE-005: how far above `basis` a unit price may go. A06 D8: with both
    a percentage and an amount, the LARGER one applies (+2 % or +BDT 500,
    whichever is larger). `price_abs` is in the bill's currency."""
    limits = []
    if price_pct:
        limits.append(Decimal(str(basis or 0)) * Decimal(str(price_pct)) / Decimal(100))
    if price_abs:
        limits.append(Decimal(str(price_abs)))
    return max(limits) if limits else Decimal(0)


def _line_basis(po_line):
    """The unit price the PO approval covered (the live price before approval)."""
    return po_line.approved_unit_price if po_line.approved_qty else po_line.unit_price


def _po_price_basis(po_lines):
    """(approved prices, the unit price a bill may reach) for one product's PO
    lines: the price the PO approval covered, the live price before approval."""
    approved = [p.approved_unit_price for p in po_lines if p.approved_qty]
    return approved, (max(approved) if approved else max(p.unit_price for p in po_lines))


def allocate(capacities, qty):
    """Spread `qty` over [(key, capacity)] in order; what is left lands on the
    last key. Returns [(key, qty)] (A06 P41: a product on several PO lines is
    billed line by line, each at its own price, never all at the dearest)."""
    out = []
    left = qty
    for key, cap in capacities:
        if left <= 1e-9:
            break
        take = min(max(cap, 0.0), left)
        if take > 1e-9:
            out.append((key, take))
            left -= take
    if left > 1e-9 and capacities:
        out.append((capacities[-1][0], left))
    return out


class FixVendorInvoice(models.Model):
    """A vendor invoice entering the three-way match (T03)."""

    _name = "fix.vendor.invoice"
    _description = "Vendor Invoice (three-way match)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "invoice_date desc, id desc"
    _rec_name = "invoice_ref"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    vendor_id = fields.Many2one(
        "res.partner", string="Vendor", required=True, index=True, ondelete="restrict"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id", string="Company Currency", readonly=True
    )
    # A06 P01 / D5: a bill in a foreign currency (a local USD order) is posted in
    # BDT at the bill-date rate, with its own currency figure on every line; the
    # approval band, TDS and VDS are computed on the BDT figure. 0 = no rate.
    fx_rate = fields.Float(
        string="FX Rate (BDT per unit)",
        digits=(16, 6),
        compute="_compute_fx_rate",
        store=True,
        help="Company-currency units per unit of the bill currency on the invoice date, "
        "from the rate table.",
    )
    invoice_ref = fields.Char(string="Vendor Invoice Ref", required=True, index=True)
    invoice_date = fields.Date(default=fields.Date.today, required=True)
    payment_term_days = fields.Integer(string="Payment Terms (days)", default=30)
    due_date = fields.Date(
        compute="_compute_due_date", store=True, readonly=False, index=True, tracking=True
    )
    line_ids = fields.One2many("fix.vendor.invoice.line", "invoice_id", string="Lines")
    subtotal = fields.Monetary(
        string="Subtotal", currency_field="currency_id", compute="_compute_totals", store=True
    )
    # Input VAT as stated on the supplier's Mushak 6.3
    supplier_mushak_no = fields.Char(string="Supplier Mushak 6.3 No", tracking=True)
    vat_amount = fields.Monetary(
        string="Input VAT (6.3)", currency_field="currency_id", default=0.0
    )
    vds_rate_id = fields.Many2one(
        "fix.tax.rate",
        string="VDS Service Code",
        domain=[("tax_kind", "=", "vds")],
        help="VAT deducted at source (1000 FiX is a withholding entity). Empty = no VDS.",
    )
    # A06 P01: withholding is statutory and in BDT, whatever the bill currency
    vds_amount = fields.Monetary(
        string="VDS Deducted",
        currency_field="company_currency_id",
        compute="_compute_totals",
        store=True,
    )
    tds_amount = fields.Monetary(
        string="TDS Deducted",
        currency_field="company_currency_id",
        compute="_compute_totals",
        store=True,
    )
    total_payable = fields.Monetary(
        string="Total Payable", currency_field="currency_id", compute="_compute_totals", store=True
    )
    subtotal_bdt = fields.Monetary(
        string="Subtotal (BDT)",
        currency_field="company_currency_id",
        compute="_compute_totals",
        store=True,
    )
    vat_amount_bdt = fields.Monetary(
        string="Input VAT (BDT)",
        currency_field="company_currency_id",
        compute="_compute_totals",
        store=True,
    )
    gross_amount_bdt = fields.Monetary(
        string="Gross (BDT)",
        currency_field="company_currency_id",
        compute="_compute_totals",
        store=True,
        help="The figure the approval matrix, the DOFA ladder and the tolerance bands read.",
    )
    total_payable_bdt = fields.Monetary(
        string="Total Payable (BDT at bill date)",
        currency_field="company_currency_id",
        compute="_compute_totals",
        store=True,
    )
    # a supplier advance paid against the PO's proforma (M16), taken back on
    # this bill when it posts (fix_ap_supplier_advance.py)
    advance_applied = fields.Monetary(
        string="Advance Deducted", currency_field="currency_id", readonly=True, copy=False
    )
    gross_amount = fields.Monetary(
        string="Gross (incl. VAT)",
        currency_field="currency_id",
        compute="_compute_totals",
        store=True,
    )
    # Three-way match (T03). Rent, utilities and other service bills have no
    # purchase order: they are "non-PO" bills, controlled by the approval
    # matrix instead of a PO/receipt match (two-way control).
    bill_type = fields.Selection(
        [
            ("po", "Purchase order (three-way match)"),
            ("non_po", "Non-PO service / recurring (approval control)"),
        ],
        string="Bill Type",
        default="po",
        required=True,
    )
    requisition_id = fields.Many2one(
        "fix.purchase.order", string="Purchase Order", index=True, ondelete="restrict"
    )
    match_state = fields.Selection(
        [
            ("unmatched", "Unmatched"),
            ("matched", "Matched"),
            ("blocked", "Blocked"),
            ("not_required", "Not required (non-PO)"),
        ],
        compute="_compute_match",
        store=True,
        string="Three-Way Match",
    )
    # Computed with the state (A06 S6): read on its own it was a stale column
    # that only refreshed when match_state happened to be read first.
    match_detail = fields.Text(readonly=True, compute="_compute_match", store=True)
    # G5: the returns to vendor of the bill's PO whose goods had already left
    # when AP registered the bill (",id,id,"), recorded once at registration.
    # A return gone before ANY bill of its PO billed the part is netted from
    # the received quantity by the match; one shipped after a bill is credited
    # on that bill by its RTV credit note. A record, not a clock comparison:
    # a ship and a registration in the same second are still ordered. Empty on
    # bills registered before G5: they netted nothing, so every return on
    # their PO is credited on them as before.
    returns_at_registration = fields.Char(
        string="Returns Gone at Registration", readonly=True, copy=False
    )
    # A06 M16-8: a line's withholding category was defaulted, not chosen.
    tds_category_review = fields.Boolean(
        string="TDS Category to Review",
        compute="_compute_tds_category_review",
        store=True,
        help="A line took the default TDS category because the vendor's tax profile names "
        "none. AP sets the right one, or confirms the default.",
    )
    # Approval workflow (A08)
    approval_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("to_approve", "To Approve"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Approval",
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    approval_level = fields.Integer(string="Levels Approved", readonly=True, default=0)
    approval_levels_required = fields.Integer(string="Levels Required", readonly=True)
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False)
    approval_log_ids = fields.One2many("fix.ap.approval.log", "invoice_id", string="Approver Log")
    payment_state = fields.Selection(
        [("not_paid", "Not Paid"), ("in_run", "In Payment Run"), ("paid", "Paid")],
        default="not_paid",
        required=True,
        tracking=True,
        index=True,
        copy=False,
    )
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)
    # BRU-APE-08 (A08 M52-10): how the bill will be paid decides the withholding.
    # The deduction is booked at approval, before the payment exists, so the
    # bill states it. A non-bank bill suffers the uplift and stays out of payment
    # runs, which pay by bank rails only.
    payment_channel = fields.Selection(
        [
            ("bank", "Bank (BEFTN / RTGS / NPSB / cheque)"),
            ("non_bank", "Cash / non-bank (withholding uplift applies)"),
        ],
        string="Payment Channel",
        default="bank",
        required=True,
        tracking=True,
    )
    # A08 M52-9: the Request Payment path, read back from treasury's events
    payment_move_id = fields.Many2one(
        "account.move",
        string="Payable Cleared By",
        readonly=True,
        copy=False,
        help="Dr trade payables / Cr outgoing clearing, when treasury confirmed the payment.",
    )
    payment_failure = fields.Char(string="Last Bank Rejection", readonly=True, copy=False)
    withholding_line_ids = fields.One2many(
        "fix.withholding.line", "vendor_invoice_id", string="TDS / VDS Deductions"
    )
    input_credit_id = fields.Many2one(
        "fix.input.vat.credit", string="Input VAT Credit", readonly=True, copy=False
    )
    note_ids = fields.One2many("fix.vendor.note", "invoice_id", string="Debit / Credit Notes")

    # ------------------------------------------------------------ computes --
    @api.depends("invoice_date", "payment_term_days")
    def _compute_due_date(self):
        for inv in self:
            if inv.invoice_date:
                inv.due_date = inv.invoice_date + timedelta(days=max(inv.payment_term_days, 0))

    @api.depends("currency_id", "invoice_date", "company_id")
    def _compute_fx_rate(self):
        for inv in self:
            company = inv.company_id or self.env.company
            if not inv.currency_id or inv.currency_id == company.currency_id:
                inv.fx_rate = 1.0
                continue
            try:
                inv.fx_rate = bdt_rate(self.env, inv.currency_id, company, inv.invoice_date)
            except UserError:
                inv.fx_rate = 0.0  # refused at submission and at posting

    def _is_foreign(self):
        self.ensure_one()
        return bool(self.currency_id) and self.currency_id != self.company_id.currency_id

    def _check_fx_rate(self, doing):
        self.ensure_one()
        if self._is_foreign() and not self.fx_rate:
            raise UserError(
                "Bill %s is in %s and there is no %s rate on or before %s: it cannot be %s "
                "(A06 D5). Record the rate first."
                % (
                    self.invoice_ref,
                    self.currency_id.name,
                    self.currency_id.name,
                    self.invoice_date,
                    doing,
                )
            )

    @api.depends(
        "line_ids.line_total",
        "line_ids.line_total_bdt",
        "line_ids.tds_amount",
        "vat_amount",
        "vds_rate_id",
        "invoice_date",
        "advance_applied",
        "fx_rate",
    )
    def _compute_totals(self) -> None:
        for inv in self:
            rate = inv.fx_rate or 0.0
            foreign = inv._is_foreign() if inv.company_id else False
            subtotal = sum(inv.line_ids.mapped("line_total"))
            subtotal_bdt = _q(sum(inv.line_ids.mapped("line_total_bdt")))
            vat_bdt = _q(inv.vat_amount * rate) if foreign else _q(inv.vat_amount)
            tds = _q(sum(inv.line_ids.mapped("tds_amount")))
            vds = 0.0
            if inv.vds_rate_id and subtotal_bdt:
                vds = _q(subtotal_bdt * inv.vds_rate_id.rate / 100.0)
                if vat_bdt > 0:  # never withhold more VAT than the 6.3 states
                    vds = min(vds, vat_bdt)
            advance = inv.advance_applied or 0.0
            advance_bdt = _q(advance * rate) if foreign else advance
            inv.subtotal = subtotal
            inv.subtotal_bdt = subtotal_bdt
            inv.vat_amount_bdt = vat_bdt
            inv.tds_amount = tds
            inv.vds_amount = vds
            inv.gross_amount = _q(subtotal + inv.vat_amount)
            inv.gross_amount_bdt = _q(subtotal_bdt + vat_bdt)
            inv.total_payable_bdt = _q(subtotal_bdt + vat_bdt - tds - vds - advance_bdt)
            if foreign:
                withheld = (tds + vds) / rate if rate else 0.0
                inv.total_payable = inv.currency_id.round(
                    subtotal + inv.vat_amount - withheld - advance
                )
            else:
                inv.total_payable = _q(subtotal + inv.vat_amount - tds - vds - advance)

    # Every quantity/price/receipt the match reads is a dependency: with
    # only ("line_ids", "requisition_id") an invoice line edited AFTER
    # matching kept its stale 'matched' state and could be paid (G3-06).
    #
    # A06 audit (2026-11-03), M16-4/7/8 (S6): the match read the PO line's
    # typed qty_received and live unit_price, per bill and per line, so a
    # buyer raising the PO price unblocked a bill, a typed receipt matched,
    # two bills (or two lines) for one receipt both matched, and a 10/10
    # inspection rejection still matched. It now reads:
    #   - the ACCEPTED quantity of POSTED goods-receipt lines (inspection
    #     outcome applied; goods awaiting inspection are not matchable);
    #   - less what earlier live bills on the same PO already invoiced, so a
    #     receipt line is invoiced once, whoever submits the second bill;
    #   - the price the PO approval covered (approved_unit_price).
    @api.depends(
        "bill_type",
        "requisition_id",
        "currency_id",
        "fx_rate",
        "requisition_id.currency_id",
        "vendor_id.commercial_partner_id",
        "requisition_id.vendor_id.commercial_partner_id",
        "line_ids.product_id",
        "line_ids.quantity",
        "line_ids.unit_price",
        "requisition_id.line_ids.product_id",
        "requisition_id.line_ids.qty_ordered",
        "requisition_id.line_ids.unit_price",
        "requisition_id.line_ids.approved_unit_price",
        "requisition_id.line_ids.approved_qty",
        "requisition_id.line_ids.receipt_line_ids.state",
        "requisition_id.line_ids.receipt_line_ids.qty_received",
        "requisition_id.line_ids.receipt_line_ids.qty_accepted",
        "requisition_id.line_ids.receipt_line_ids.inspection_state",
        "requisition_id.vendor_invoice_ids.approval_state",
        "requisition_id.vendor_invoice_ids.bill_type",
        "requisition_id.vendor_invoice_ids.line_ids.product_id",
        "requisition_id.vendor_invoice_ids.line_ids.quantity",
        "requisition_id.vendor_invoice_ids.returns_at_registration",
        "returns_at_registration",
    )
    def _compute_match(self) -> None:
        """G3-06: the three-way check — invoice lines vs the PO's approved
        price and the goods accepted on posted receipts that no earlier bill
        has claimed. Any variance beyond tolerance BLOCKS."""
        TOLERANCE = Decimal("0.01")
        for inv in self:
            if inv.bill_type == "non_po":
                inv.match_state = "not_required"
                inv.match_detail = "Non-PO bill: controlled by the approval matrix"
                continue
            if not inv.requisition_id:
                inv.match_state = "unmatched"
                inv.match_detail = "No purchase order linked"
                continue
            po = inv.requisition_id.sudo()
            # The bill is the PO supplier's own paper: vendor B's bill matched
            # vendor A's order and receipts, and would have been paid to B.
            payee = inv.sudo().vendor_id.commercial_partner_id
            supplier = po.vendor_id.commercial_partner_id
            if payee != supplier:
                inv.match_state = "blocked"
                inv.match_detail = "%s is not the supplier of the purchase order (%s)" % (
                    payee.display_name or "The bill's vendor",
                    supplier.display_name,
                )
                continue
            # A06 P02 / D5: the bill is in the order's currency; a BDT bill
            # against a USD order compared 1,000 BDT with USD 1,000 and matched
            if inv.currency_id and inv.currency_id != po.currency_id:
                inv.match_state = "blocked"
                inv.match_detail = "The bill is in %s but purchase order %s is in %s" % (
                    inv.currency_id.name,
                    po.name,
                    po.currency_id.name,
                )
                continue
            my_id = inv._origin.id or inv.id
            saved = isinstance(my_id, int)
            earlier = po.vendor_invoice_ids.filtered(
                lambda other, me=my_id, saved=saved: (
                    other.id != me
                    and other.bill_type == "po"
                    and other.approval_state != "rejected"
                    and (not saved or other.id < me)
                )
            )
            po_lines = {}
            for po_line in po.line_ids.sorted("id"):
                po_lines.setdefault(po_line.product_id.id, []).append(po_line)
            gone_before_billing = inv._fix_returns_before_billing(po)
            invoiced, label, order, product = {}, {}, [], {}
            for line in inv.line_ids:
                pid = line.product_id.id
                if pid not in invoiced:
                    invoiced[pid] = 0.0
                    label[pid] = line.description
                    order.append(pid)
                    product[pid] = line.product_id
                invoiced[pid] += line.quantity or 0.0
            # FR-APE-005 (M52 capture audit 2026-11-17): the approved tolerance
            # row for the product's category and the bill's value band; no
            # row = exact quantity and 0.01 on price, as before
            Tolerance = self.env["fix.ap.match.tolerance"]
            used = Tolerance.browse()
            default_used = False
            problems = []
            for pid in order:
                if pid not in po_lines:
                    problems.append("%s: not on the PO" % label[pid])
                    continue
                pols = po_lines[pid]
                receipts = [r for pol in pols for r in pol.receipt_line_ids if r.state == "posted"]
                accepted = sum(r.qty_accepted for r in receipts)
                awaiting = sum(r.qty_received for r in receipts if r.inspection_state == "pending")
                rejected = sum(r.qty_rejected for r in receipts)
                prior = sum(
                    other_line.quantity or 0.0
                    for other in earlier
                    for other_line in other.line_ids
                    if other_line.product_id.id == pid
                )
                # G5: goods sent back before any bill billed them are not
                # billable; a return from quarantine first uses up the units
                # inspection rejected (never part of the accepted quantity)
                from_stock, from_quarantine = gone_before_billing.get(pid, (0.0, 0.0))
                gone = from_stock + max(from_quarantine - rejected, 0.0)
                qty_pct, price_pct, price_abs, tol = Tolerance._fix_for(inv, product[pid])
                available = Decimal(str(round(accepted - gone - prior, 6)))
                billed = Decimal(str(invoiced[pid]))
                qty_ok = available >= billed
                if not qty_ok and qty_pct and available > 0:
                    qty_ok = available * (1 + Decimal(str(qty_pct)) / 100) >= billed
                    if qty_ok:
                        used |= tol
                if not qty_ok:
                    if gone:
                        text = (
                            "%s: received %.2f, %.2f returned to the vendor before it was "
                            "billed, %.2f already invoiced on other bills, invoiced %.2f"
                            % (label[pid], accepted, gone, prior, invoiced[pid])
                        )
                    elif prior:
                        text = (
                            "%s: received %.2f, %.2f already invoiced on other bills, "
                            "invoiced %.2f" % (label[pid], accepted, prior, invoiced[pid])
                        )
                    else:
                        text = "%s: received %.2f < invoiced %.2f" % (
                            label[pid],
                            accepted,
                            invoiced[pid],
                        )
                    if awaiting:
                        text += " (%.2f awaiting inspection)" % awaiting
                    if rejected:
                        text += " (%.2f rejected at inspection)" % rejected
                    problems.append(text)
                approved, basis = _po_price_basis(pols)
                lines = inv.line_ids.filtered(lambda ln, p=pid: ln.product_id.id == p)
                # D8: the BDT allowance in the bill's currency
                abs_cur = price_abs / inv.fx_rate if (price_abs and inv.fx_rate) else 0.0
                exact = Decimal(str(basis or 0)) + TOLERANCE
                ceiling = exact + tolerance_allowance(basis, price_pct, abs_cur)
                # A06 P41: the billed quantity is spread over the product's PO
                # lines in order (after what earlier bills took), each at its
                # own approved price; the bill's value may not exceed that
                caps = inv._fix_line_capacities(pols, prior + float(gone))
                alloc = allocate(caps, invoiced[pid])
                allowed = sum(Decimal(str(q)) * Decimal(str(_line_basis(pol))) for pol, q in alloc)
                allowance = sum(
                    Decimal(str(q)) * tolerance_allowance(_line_basis(pol), price_pct, abs_cur)
                    for pol, q in alloc
                )
                value = sum(
                    Decimal(str(ln.quantity or 0)) * Decimal(str(ln.unit_price)) for ln in lines
                )
                # the 0.01 rounding allowance is per unit, as on the price
                cents = TOLERANCE * Decimal(str(invoiced[pid] or 0))
                if any(Decimal(str(ln.unit_price)) > ceiling for ln in lines) or (
                    value > allowed + allowance + cents
                ):
                    problems.append("%s: price above PO" % label[pid])
                elif any(Decimal(str(ln.unit_price)) > exact for ln in lines) or (
                    value > allowed + cents
                ):
                    used |= tol
                    if not tol:
                        default_used = True
                elif not approved and qty_ok:
                    problems.append("%s: PO price not approved" % label[pid])
            if problems:
                inv.match_state = "blocked"
                inv.match_detail = "\n".join(problems)
            else:
                inv.match_state = "matched"
                inv.match_detail = "PO / receipt / invoice reconciled"
                if used:
                    inv.match_detail += " within the approved tolerance (%s)" % ", ".join(
                        used.mapped("name")
                    )
                elif default_used:
                    inv.match_detail += (
                        " within the default price tolerance (D8: +%g%% or +BDT %s a unit, "
                        "whichever is larger); the difference is price variance"
                        % (
                            float_param(self.env, PARAM_TOL_PRICE_PCT, DEFAULT_TOL_PRICE_PCT),
                            f"{float_param(self.env, PARAM_TOL_PRICE_ABS, DEFAULT_TOL_PRICE_ABS):,.0f}",
                        )
                    )

    def _fix_line_capacities(self, pols, taken):
        """[(po line, accepted qty still unbilled)] in line order, after `taken`
        units (earlier bills and returns) are consumed from the first lines."""
        caps = []
        for pol in pols:
            accepted = sum(r.qty_accepted for r in pol.receipt_line_ids if r.state == "posted")
            use = min(accepted, max(taken, 0.0))
            taken -= use
            caps.append((pol, accepted - use))
        return caps

    def _fix_returns_before_billing(self, po):
        """G5 (owner decision 12 Nov 2026): {product id: (qty returned from
        stock, qty returned from quarantine)} of the PO's returns to vendor
        (fix.stock.rtv, M15) whose goods left (shipped or credited) before any
        live bill of the PO billed that product. The vendor bills the net
        quantity for those, so the match nets them from what was received.
        A return shipped after a bill is credited on that bill by its RTV
        credit note and is not netted here (it would count twice).
        Without the inventory module there are no returns to net."""
        if "fix.stock.rtv" not in self.env or not po:
            return {}
        rtvs = (
            self.env["fix.stock.rtv"]
            .sudo()
            .search([("purchase_order_id", "=", po.id), ("state", "in", RTV_GONE_STATES)])
        )
        if not rtvs:
            return {}
        bills = po.sudo().vendor_invoice_ids.filtered(
            lambda b: b.bill_type == "po" and b.approval_state != "rejected"
        )
        out = {}
        for rtv in rtvs:
            product = rtv.part_id.product_id
            if not product:
                continue
            if rtv.id not in self._fix_returns_seen():
                continue  # it left after this bill was registered
            billed_before = bills.filtered(
                lambda b, p=product, r=rtv.id: p in b.line_ids.product_id
                and r not in b._fix_returns_seen()
            )
            if billed_before:
                continue  # an earlier bill billed it: its credit note carries it
            stock, quarantine = out.get(product.id, (0.0, 0.0))
            if rtv.quarantine_id:
                quarantine += rtv.qty or 0.0
            else:
                stock += rtv.qty or 0.0
            out[product.id] = (stock, quarantine)
        return out

    def _fix_gone_returns(self, po):
        """The ids of the PO's returns to vendor whose goods have left."""
        if "fix.stock.rtv" not in self.env or not po:
            return set()
        return set(
            self.env["fix.stock.rtv"]
            .sudo()
            .search([("purchase_order_id", "=", po.id), ("state", "in", RTV_GONE_STATES)])
            .ids
        )

    def _fix_returns_seen(self):
        """G5: the returns gone when this bill was registered (an unsaved
        bill: the ones gone now)."""
        self.ensure_one()
        if not isinstance(self._origin.id or self.id, int):
            return self._fix_gone_returns(self.requisition_id.sudo())
        return {int(x) for x in (self.returns_at_registration or "").split(",") if x}

    def _fix_record_returns_seen(self):
        for bill in self:
            gone = sorted(bill._fix_gone_returns(bill.requisition_id.sudo()))
            bill._guarded().write(
                {"returns_at_registration": ",%s," % ",".join(map(str, gone)) if gone else False}
            )

    def _fix_return_before_billing(self, rtv):
        """G5: True when the goods of `rtv` had left before this bill was
        registered. Either no earlier bill billed them, so the match netted
        them and the vendor billed net, or an earlier bill did and carries
        their credit. Either way no credit note for them is raised here."""
        self.ensure_one()
        return rtv.id in self._fix_returns_seen()

    @api.depends("line_ids.tds_category_assumed")
    def _compute_tds_category_review(self):
        for inv in self:
            inv.tds_category_review = any(inv.line_ids.mapped("tds_category_assumed"))

    def action_confirm_tds_category(self):
        """AP confirms the default category is the right one for these lines.
        The reviewer is an Accountant or Accounting Administrator; the
        confirmation (who, which categories) is written to the approval log
        the approvers read.

        G4 (owner decision 12 Nov 2026): a second person. The bill's creator
        or submitter does not confirm the category of their own bill, and the
        confirmer does not then submit it (_check_tds_confirmer)."""
        require_finance(self.env, "Confirming a TDS category")
        for inv in self:
            assumed = inv.line_ids.filtered("tds_category_assumed")
            if not assumed:
                continue
            makers = inv.sudo().create_uid | inv.sudo().submitted_by
            if not self.env.su and self.env.user in makers:
                raise UserError(
                    "Segregation of duties: you created or submitted bill %s, so another "
                    "accountant confirms its defaulted TDS category." % inv.invoice_ref
                )
            assumed.write({"tds_category_assumed": False})
            inv._log(
                "tds_confirm",
                note="Defaulted TDS category confirmed: %s"
                % ", ".join(sorted(set(assumed.mapped("tds_category")))),
            )
        return True

    def _check_tds_category_reviewed(self, doing):
        """C9 / D-05 (owner decision 12 Nov 2026): a bill whose withholding
        category was defaulted, not chosen, is not submitted or approved until
        AP sets the right category or confirms the default. A supplier with no
        tax profile otherwise withholds at service_general 10% x 2.25 = 22.5%."""
        self.ensure_one()
        if self.tds_category_review:
            raise UserError(
                "Bill %s cannot be %s: the TDS category of %s was defaulted because vendor %s "
                "has no tax profile category, and nobody has reviewed it. Set the right "
                "category on the line, or have an Accountant confirm the default (Confirm "
                "Defaulted TDS Category)%s."
                % (
                    self.invoice_ref,
                    doing,
                    ", ".join(
                        self.line_ids.filtered("tds_category_assumed").mapped(
                            lambda ln: ln.description or ln.product_id.display_name or "a line"
                        )
                    ),
                    self.vendor_id.display_name,
                    "" if self.approval_state == "draft" else "; reject the bill to draft first",
                )
            )

    def _check_tds_confirmer(self):
        """G4: whoever confirmed the defaulted TDS category is the second
        person; they do not submit the bill as well."""
        self.ensure_one()
        if self.env.su:
            return
        confirmers = (
            self.sudo().approval_log_ids.filtered(lambda log: log.action == "tds_confirm").user_id
        )
        if self.env.user in confirmers:
            raise UserError(
                "Segregation of duties: you confirmed the defaulted TDS category of bill %s, "
                "so another person submits it." % self.invoice_ref
            )

    @api.constrains("vds_rate_id")
    def _check_vds_rate(self):
        # the form's list is every tax rate: the domain binds only Odoo's own form
        for inv in self:
            rate = inv.vds_rate_id.sudo()
            if rate and rate.tax_kind != "vds":
                raise ValidationError("%s is not a VDS service code." % rate.display_name)

    @api.constrains("bill_type", "requisition_id")
    def _check_bill_type(self):
        for inv in self:
            if inv.bill_type == "non_po" and inv.requisition_id:
                raise ValidationError(
                    "Bill %s is linked to a purchase order: it must use the three-way match"
                    % (inv.invoice_ref or inv.id)
                )

    # -------------------------------------------------------------- guards --
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | GUARDED_FIELDS

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(inv.approval_state in ("to_approve", "approved") for inv in self):
            locked |= LOCKED_FIELDS
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        """A08 M52-10: a new bill takes the vendor's default VDS service code
        (the person can clear it on the draft). A vendor outside VDS has none."""
        Partner = self.env["res.partner"].sudo()
        Profile = self.env["fix.vendor.tax.profile"]
        for vals in vals_list:
            if vals.get("vds_rate_id") or not vals.get("vendor_id"):
                continue
            company = self.env["res.company"].browse(vals.get("company_id") or self.env.company.id)
            profile = Profile.for_partner(Partner.browse(vals["vendor_id"]), company)
            if profile.default_vds_rate_id and not profile.vds_exempt:
                vals["vds_rate_id"] = profile.default_vds_rate_id.id
        bills = super().create(vals_list)
        bills._fix_record_returns_seen()  # G5
        return bills

    def write(self, vals):
        # The lock yields to a transition (guard token) or superuser code only:
        # the old ap_internal context key could be sent by any RPC caller.
        if LOCKED_FIELDS & set(vals) and not self._fix_guard_open():
            locked = self.filtered(lambda inv: inv.approval_state in ("to_approve", "approved"))
            if locked:
                changed = [
                    name
                    for name in sorted(LOCKED_FIELDS & set(vals))
                    if name == "line_ids"
                    or any(inv._fix_guard_differs(name, vals[name], inv[name]) for inv in locked)
                ]
                if changed:
                    raise UserError(
                        "Bill %s is %s — reset it to draft (reject) before changing %s"
                        % (locked[0].invoice_ref, locked[0].approval_state, ", ".join(changed))
                    )
        result = super().write(vals)
        if "requisition_id" in vals:
            # G5: a draft bill re-pointed at another PO is registered against it now
            self.filtered(lambda inv: inv.approval_state == "draft")._fix_record_returns_seen()
        return result

    def unlink(self):
        if self.filtered(lambda inv: inv.approval_state != "draft" or inv.move_id):
            raise UserError("Only draft, unposted vendor bills can be deleted")
        return super().unlink()

    # ---------------------------------------------------------- tax helpers --
    def _tax_profile(self):
        self.ensure_one()
        return self.env["fix.vendor.tax.profile"].for_partner(self.vendor_id, self.company_id)

    def _duplicates(self):
        """Other live bills of the same vendor with the same invoice reference."""
        self.ensure_one()
        return self.search(
            [
                ("id", "!=", self.id),
                ("company_id", "=", self.company_id.id),
                ("vendor_id.commercial_partner_id", "=", self.vendor_id.commercial_partner_id.id),
                ("invoice_ref", "=ilike", (self.invoice_ref or "").strip()),
                ("approval_state", "!=", "rejected"),
            ]
        )

    # ------------------------------------------------------------ workflow --
    def _check_match_gate(self, doing):
        """G3-06 before the liability is approved and posted, not only when it
        is paid: a blocked or unmatched PO bill was submitted, approved and
        posted to the GL. A non-PO bill ('not_required') keeps its route."""
        self.ensure_one()
        # G5: the match also reads returns to vendor (M15), which this module
        # cannot declare as a dependency: decide on a fresh match, not the
        # stored one
        for name in ("match_state", "match_detail"):
            self.env.add_to_compute(self._fields[name], self)
        if self.match_state not in PAYABLE_MATCH_STATES:
            raise UserError(
                "G3-06: bill %s cannot be %s while its three-way match is %s (%s)"
                % (self.invoice_ref, doing, self.match_state, self.match_detail)
            )

    def _ap_po_headroom(self):
        """What the PO's approved prices still allow on top of this bill, for
        the quantities it invoices; None for a non-PO bill."""
        self.ensure_one()
        if self.bill_type != "po":
            return None
        po_lines = defaultdict(list)
        for po_line in self.requisition_id.sudo().line_ids:
            po_lines[po_line.product_id.id].append(po_line)
        ceiling = sum(
            line.quantity * _po_price_basis(po_lines[line.product_id.id])[1]
            for line in self.line_ids
            if po_lines.get(line.product_id.id)
        )
        return _q(ceiling - self.subtotal)

    def _log(self, action, rule=None, note=None):
        self.ensure_one()
        self.env["fix.ap.approval.log"].sudo().create(
            {
                "company_id": self.company_id.id,
                "operating_unit_id": self.operating_unit_id.id,
                "invoice_id": self.id,
                "rule_id": rule.id if rule else False,
                "level": rule.level if rule else 0,
                "user_id": self.env.user.id,
                "action": action,
                "amount": self.gross_amount_bdt,
                "note": note or False,
            }
        )

    def action_submit_approval(self):
        """Submit for approval: lines present, no duplicate reference, the
        withholding recomputed against today's tax profile, and the matrix
        levels fixed for this amount (none covering it = refused)."""
        for inv in self:
            if inv.approval_state not in ("draft", "rejected"):
                raise UserError("Bill %s is already %s" % (inv.invoice_ref, inv.approval_state))
            if not inv.line_ids or inv.subtotal <= 0:
                raise UserError("Bill %s has no positive lines" % inv.invoice_ref)
            inv._check_fx_rate("submitted for approval")
            inv._check_match_gate("submitted for approval")
            inv._check_tds_category_reviewed("submitted for approval")
            inv._check_tds_confirmer()
            dup = inv._duplicates()
            if dup:
                raise UserError(
                    "Duplicate prevention: %s already has bill reference %s (id %s)"
                    % (inv.vendor_id.display_name, inv.invoice_ref, dup[0].id)
                )
            if inv.vds_rate_id and inv._tax_profile().vds_exempt:
                raise UserError(
                    "Bill %s carries a VDS service code, but vendor %s is marked VDS Not "
                    "Applicable on its tax profile. Clear one of them."
                    % (inv.invoice_ref, inv.vendor_id.display_name)
                )
            inv.line_ids._compute_tds()
            inv._compute_totals()
            inv._check_tds_exemptions()
            inv._check_capital_lines()
            levels = inv._ap_levels()
            if not levels:
                raise UserError(
                    "No approval-matrix level covers BDT %.2f in %s — maintain the AP "
                    "approval matrix first" % (inv.gross_amount_bdt, inv.company_id.name)
                )
            inv._guarded().write(
                {
                    "approval_state": "to_approve",
                    "approval_level": 0,
                    "approval_levels_required": len(levels),
                    "submitted_by": self.env.user.id,
                }
            )
            inv._log("submit")
        return True

    def _check_tds_exemptions(self):
        """A08 M52-10: a ticked TDS exemption needs the vendor's exemption
        certificate (number, file, expiry) valid on the invoice date."""
        self.ensure_one()
        if not self.line_ids.filtered("tds_exempt"):
            return
        profile = self._tax_profile()
        if not (profile and profile.is_tds_exempt_on(self.invoice_date)):
            raise UserError(
                "Bill %s claims a TDS exemption, but vendor %s has no exemption certificate "
                "(number, attached file, valid on %s) on its tax profile. Untick the "
                "exemption or record the certificate."
                % (self.invoice_ref, self.vendor_id.display_name, self.invoice_date)
            )

    def _ap_conflicted_users(self):
        """Who never approves this bill (A08 M52-3, BRU-APE-04/05): its
        creator and submitter, whoever already signed a level, the vendor's
        creator (SOD-01), and a user who both raised the PO and received its
        goods (SOD-02: any two of the three are allowed, not all three)."""
        self.ensure_one()
        inv = self.sudo()
        users = inv.create_uid | inv.submitted_by
        users |= inv.approval_log_ids.filtered(lambda log: log.action == "approve").mapped(
            "user_id"
        )
        vendor = inv.vendor_id
        users |= vendor.create_uid | vendor.commercial_partner_id.create_uid
        order = inv.requisition_id
        if order:
            raisers = order.create_uid
            if "buyer_id" in order._fields:
                raisers |= order.buyer_id
            receivers = self.env["res.users"]
            if "receipt_ids" in order._fields:
                posted = order.receipt_ids.filtered(lambda r: r.state == "posted")
                receivers |= posted.mapped("create_uid")
                if "receiver_id" in posted._fields:
                    receivers |= posted.mapped("receiver_id")
            users |= raisers & receivers
        # the superuser that loads data and runs services is not a person
        root = self.env.ref("base.user_root", raise_if_not_found=False)
        return users.filtered(lambda u: not root or u != root)

    def _ap_may_sign(self, user, rule):
        """The level's group, or (where policy allows) a higher level's group:
        a finance manager signs level 1 (A08 M52-11)."""
        groups = user.all_group_ids
        if rule.group_id in groups:
            return True
        if not bool_param(self.env, PARAM_HIGHER_SIGNS_LOWER, True):
            return False
        higher = (
            self.env["fix.ap.approval.rule"]
            .sudo()
            .search([("company_id", "=", self.company_id.id), ("level", ">", rule.level)])
        )
        return bool(higher.mapped("group_id") & groups)

    def _ap_levels(self, amount=None):
        """The matrix levels this bill needs, in order (or, with `amount`, the
        levels a bill of that gross would need). The default ladder is
        the AP matrix's own bands (every active level whose minimum the gross
        reaches). When an M30 DOFA ladder is RULED for fix.vendor.invoice (the
        one DoA table, fix.dofa.ladder), it decides how many levels the
        amount needs: tier_N = the matrix's first N levels, each still signed
        by its own group under the SoD rules; a matrix with fewer levels than
        the ruling fails closed."""
        self.ensure_one()
        Rule = self.env["fix.ap.approval.rule"]
        # A06 P01: the band is read in BDT, whatever the bill currency
        gross = self.gross_amount_bdt if amount is None else amount
        levels = Rule.levels_for(gross, self.company_id)
        ruled = None
        if "fix.dofa.ladder" in self.env:
            ruled = self.env["fix.dofa.ladder"].thresholds_for(self._name, company=self.company_id)
        if not ruled:
            return levels
        amount = abs(gross or 0.0)
        tier = next((t for bound, t in ruled if amount <= bound), ruled[-1][1])
        try:
            count = max(int(str(tier).rsplit("_", 1)[-1]), 1)
        except ValueError:
            count = len(levels) or 1
        rows = Rule.sudo().search([("company_id", "=", self.company_id.id)], order="level")
        if len(rows) < count:
            raise UserError(
                "The DOFA ladder in force for vendor bills requires %d approval levels for BDT "
                "%.2f, but the AP matrix of %s has %d. Maintain the matrix first."
                % (count, amount, self.company_id.name, len(rows))
            )
        return Rule.browse(rows[:count].ids)

    def _next_level(self):
        self.ensure_one()
        levels = self._ap_levels()
        return levels[self.approval_level] if self.approval_level < len(levels) else None

    def action_approve(self):
        """Approve the next matrix level. The levels are re-derived from the
        matrix and the live amount at every approval (a stored count is not
        trusted, A08 M52-3). Segregation of duties: the approver holds the
        level's group (or a higher level's, where policy allows), and is not
        the creator, the submitter, an earlier signer, the vendor's creator,
        or the user who both raised the PO and received it. The last level
        posts the bill."""
        user = self.env.user
        for inv in self:
            if inv.approval_state != "to_approve":
                raise UserError("Bill %s is not awaiting approval" % inv.invoice_ref)
            # re-read at every level: a match can break after submission
            inv._check_match_gate("approved")
            inv._check_tds_category_reviewed("approved")
            levels = inv._ap_levels()
            if not levels:
                raise UserError(
                    "No approval-matrix level covers BDT %.2f in %s"
                    % (inv.gross_amount_bdt, inv.company_id.name)
                )
            rule = levels[inv.approval_level] if inv.approval_level < len(levels) else None
            if not rule:
                raise UserError("Bill %s has no pending approval level" % inv.invoice_ref)
            if not inv._ap_may_sign(user, rule):
                raise UserError(
                    "Level %d (%s) must be approved by a member of %s"
                    % (rule.level, rule.name, rule.group_id.display_name)
                )
            if user == inv.submitted_by:
                raise UserError("Segregation of duties: the submitter cannot approve the bill")
            earlier = inv.approval_log_ids.filtered(lambda log: log.action == "approve")
            if user in earlier.mapped("user_id"):
                raise UserError("Segregation of duties: one user approves one level only")
            if user in inv._ap_conflicted_users():
                raise UserError(
                    "Segregation of duties (SOD-01/SOD-02): you created bill %s, created its "
                    "vendor, or raised and received its purchase order; another approver "
                    "approves it." % inv.invoice_ref
                )
            inv._log("approve", rule)
            level = inv.approval_level + 1
            done = level >= len(levels)
            inv._guarded().write(
                {
                    "approval_level": level,
                    "approval_levels_required": len(levels),
                    "approval_state": "approved" if done else "to_approve",
                }
            )
            if done:
                inv._post_approved_bill()
        return True

    def action_reject(self):
        for inv in self:
            if inv.approval_state != "to_approve":
                raise UserError("Only a bill awaiting approval can be rejected")
            rule = inv._next_level()
            # who may sign a level may refuse it (A08 M52-11): a manager signs level 1
            if rule and not inv._ap_may_sign(self.env.user, rule):
                raise UserError("Only a %s member can reject at this level" % rule.group_id.name)
            if self.env.user in (inv.create_uid | inv.submitted_by):
                raise UserError("Segregation of duties: the maker does not decide the bill")
            inv._log("reject", rule)
            inv._guarded().write({"approval_state": "rejected", "approval_level": 0})
        return True

    def action_reset_draft(self):
        for inv in self:
            if inv.approval_state != "rejected":
                raise UserError("Only a rejected bill returns to draft")
            inv._log("reset")
            inv._guarded().write({"approval_state": "draft"})
        return True

    def _fix_clears_grni(self, line):
        """The line bills goods (or a service) whose receipt credited GRNI: a
        product of the linked PO, or of a received import without a PO."""
        if line.cwip_id:
            return False
        po = self.requisition_id.sudo()
        if po and "capex_request_id" in po._fields and po.capex_request_id:
            # A06 X25 (agreed with A07): a capital purchase never passes through
            # GRNI - its receipt posts nothing and the bill debits CWIP
            return False
        if po and line.product_id in po.line_ids.product_id:
            return True
        return bool(self._fix_grni_source_lines(line))  # A06 X11

    def _expense_account(self, line):
        """A capital line debits its CWIP project's account (M49 hand-off);
        else GRNI clearing for PO-received goods, else the product's expense
        account, else the configured default expense role."""
        if line.cwip_id:
            return line.cwip_id.sudo()._fix_cwip_account()
        if self._fix_clears_grni(line):
            return ap_account(self.env, self.company_id, "grni")
        account = (
            line.product_id.product_tmpl_id.with_company(self.company_id)
            ._get_product_accounts()
            .get("expense")
        )
        return account or ap_account(self.env, self.company_id, "expense")

    def _fix_grni_source_lines(self, line):
        """Hook (A06 X11): [(unit receipt value in BDT, qty)] of a received
        document other than a PO whose receipt credited GRNI (an import without
        a PO). Empty: the line is not GRNI-cleared."""
        return []

    # ---- GRNI clearing at the receipt value (A06 D2 / D5, P12, X03, X14) ----
    def _fix_receipt_unit_value(self, po_line):
        """BDT per unit at which the goods of `po_line` entered GRNI: the M15
        receipt cost (what the receipt credited 100503 with), else the value
        the M16 receipt stamped, else the approved price at the order's rate."""
        po_line = po_line.sudo()
        rlines = po_line.receipt_line_ids.filtered(lambda r: r.state == "posted")
        if rlines and "fix.stock.receipt.line" in self.env:
            stock = (
                self.env["fix.stock.receipt.line"]
                .sudo()
                .search([("source_line_ref", "in", ["PRL:%d" % r.id for r in rlines])])
                .filtered(lambda sl: sl.is_posted and (sl.qty_accepted or 0.0) > 0)
            )
            qty = sum(stock.mapped("qty_accepted"))
            if qty > 1e-9:
                return sum(sl.unit_cost * sl.qty_accepted for sl in stock) / qty
        stamped = rlines.filtered(lambda r: r.unit_value_bdt and r.qty_accepted > 0)
        qty = sum(stamped.mapped("qty_accepted"))
        if qty > 1e-9:
            return sum(r.unit_value_bdt * r.qty_accepted for r in stamped) / qty
        return _line_basis(po_line) * po_line.order_id._fix_rate_bdt()

    def _fix_bill_line_split(self, line):
        """{(account, cwip): [BDT, bill-currency figure or None]} for one bill
        line: the GRNI it clears at the goods' receipt value, the part of the
        difference caused only by the rate moving from the order's stamped rate
        to the bill date (FX gain/loss, 500030) and the rest (price variance,
        600007). A line that clears no GRNI is its expense / CWIP account at
        the bill-date BDT figure."""
        company = self.company_id
        account = self._expense_account(line)
        total_bdt = line.line_total_bdt
        if not self._fix_clears_grni(line):
            return {(account, line.cwip_id): [total_bdt, line.line_total]}
        rate_bill = self.fx_rate or 1.0
        units = self._fix_grni_units(line)
        cleared = _q(sum(value * qty for value, qty, _r in units))
        cleared_cur = sum(value * qty / rate for value, qty, rate in units if rate)
        fx = _q(sum((rate_bill - rate) * line.unit_price * qty for _v, qty, rate in units))
        ppv = _q(total_bdt - cleared - fx)
        out = defaultdict(lambda: [0.0, None])
        out[(account, False)] = [cleared, cleared_cur]
        if fx:
            out[(ap_account(self.env, company, "fx_gain_loss"), False)][0] += fx
        if ppv:
            out[(ap_account(self.env, company, "ppv"), False)][0] += ppv
        return out

    def _fix_grni_units(self, line):
        """[(receipt unit value BDT, qty, order rate)] the line's quantity
        clears, spread over the PO lines like the match spreads it."""
        other = self._fix_grni_source_lines(line)
        if other:
            return other
        po = self.requisition_id.sudo()
        pols = po.line_ids.filtered(lambda p: p.product_id == line.product_id).sorted("id")
        if not pols:
            return []
        earlier = po.vendor_invoice_ids.filtered(
            lambda b: b.id < self.id and b.bill_type == "po" and b.approval_state != "rejected"
        )
        prior = sum(
            bl.quantity for b in earlier for bl in b.line_ids if bl.product_id == line.product_id
        )
        # earlier lines of this bill for the same product come first
        prior += sum(
            bl.quantity
            for bl in self.line_ids
            if bl.product_id == line.product_id and bl.id < line.id
        )
        rate = po._fix_rate_bdt()
        caps = self._fix_line_capacities(pols, prior)
        return [
            (self._fix_receipt_unit_value(pol), qty, rate)
            for pol, qty in allocate(caps, line.quantity or 0.0)
        ]

    def _post_approved_bill(self):
        """Dr GRNI at the receipt value (+ price variance, + FX difference) or
        expense, Dr input VAT; Cr TDS payable, Cr VDS payable, Cr trade
        payables — all in BDT at the bill-date rate, with the bill currency's
        own figure on the payable (A06 P01) — then the deduction lines and the
        input credit."""
        self.ensure_one()
        self._check_fx_rate("posted")
        self._check_match_gate("posted")
        env, company = self.env, self.company_id
        partner = self.vendor_id.commercial_partner_id
        label = "Bill %s %s" % (partner.name, self.invoice_ref)
        # the PO's paid supplier advances not yet taken back reduce the payable
        self._apply_supplier_advances()
        cur = self.currency_id
        lines = []
        # capital lines are posted one per CWIP project, with the project in
        # the label, so the posted items can be booked to it (M49-3)
        by_account = defaultdict(float)
        foreign = defaultdict(float)
        for line in self.line_ids:
            for key, (amount, cur_amount) in self._fix_bill_line_split(line).items():
                by_account[key] += amount
                if cur_amount is not None:
                    foreign[key] += cur_amount
        for (account, cwip), amount in by_account.items():
            if not _q(amount):
                continue
            text = "%s CWIP %s" % (label, cwip.sudo().name) if cwip else label
            debit, credit = (_q(amount), 0.0) if amount > 0 else (0.0, _q(-amount))
            fx_line = (cur, foreign[(account, cwip)]) if (account, cwip) in foreign else None
            lines.append((account, text, debit, credit, partner, fx_line))
        if self.vat_amount_bdt:
            lines.append(
                (
                    ap_account(env, company, "vat_input"),
                    "Input VAT " + label,
                    _q(self.vat_amount_bdt),
                    0.0,
                    partner,
                    (cur, self.vat_amount),
                )
            )
        if self.tds_amount:
            lines.append(
                (
                    ap_account(env, company, "tds_payable"),
                    "TDS " + label,
                    0.0,
                    self.tds_amount,
                    partner,
                )
            )
        if self.vds_amount:
            lines.append(
                (
                    ap_account(env, company, "vds_payable"),
                    "VDS " + label,
                    0.0,
                    self.vds_amount,
                    partner,
                )
            )
        if self.advance_applied:
            # D5: an advance is taken back at the BDT it was paid at (its own
            # rate); the payable is reduced at the bill rate, so the
            # difference is FX gain/loss (it used to sit on the advance account)
            own_bdt = _q(self._fix_advance_bdt())
            lines.append(
                (
                    ap_account(env, company, "supplier_advance"),
                    "Advance taken back " + label,
                    0.0,
                    own_bdt,
                    partner,
                    (cur, -self.advance_applied),
                )
            )
            at_bill = (
                _q(self.advance_applied * (self.fx_rate or 1.0))
                if self._is_foreign()
                else (_q(self.advance_applied))
            )
            diff = _q(at_bill - own_bdt)
            if diff:
                fx = ap_account(env, company, "fx_gain_loss")
                text = "FX on advance taken back " + label
                lines.append(
                    (fx, text, 0.0 if diff > 0 else -diff, diff if diff > 0 else 0.0, partner)
                )
        # the payable carries the bill currency's own figure (A06 P01)
        lines.append(
            (
                ap_account(env, company, "ap"),
                label,
                0.0,
                self.total_payable_bdt,
                partner,
                (cur, -self.total_payable),
            )
        )
        move = post_ap_move(
            env,
            company,
            ap_journal(env, company, "purchase"),
            self.invoice_date,
            label,
            lines,
            self.operating_unit_id,
        )
        self._guarded().write({"move_id": move.id})
        self._book_capital_cost(move)
        self._create_deductions()
        self._create_input_credit()
        self._fix_reclass_ineligible_vat(move)
        publish(
            env,
            "vendor_bill.approved",
            "fix.vendor.invoice",
            self.id,
            {
                "vendor_id": partner.id,
                "gross": self.gross_amount_bdt,
                "tds": self.tds_amount,
                "vds": self.vds_amount,
                "payable": self.total_payable_bdt,
                "currency": self.currency_id.name,
                "payable_currency": self.total_payable,
                "move_id": move.id,
            },
        )

    def _fix_advance_bdt(self):
        """The BDT at which the advances taken back on this bill were paid.
        Extended per advance source (M16 proforma advances in
        fix_ap_supplier_advance.py; LC advances carry their own BDT figure)."""
        self.ensure_one()
        total = 0.0
        if "lc_advance_application_ids" in self._fields:
            for app in self.lc_advance_application_ids.sudo():
                leg = app.settlement_id
                amount = leg.amount or 0.0
                bdt = getattr(leg, "amount_bdt", None)
                if amount and bdt:
                    total += app.amount * bdt / amount
                else:
                    total += app.amount * (self.fx_rate or 1.0)
        return total

    def _fix_reclass_ineligible_vat(self, move):
        """A06 P31: input VAT the eligibility check refused (unregistered
        supplier, no valid Mushak 6.3...) is not a recoverable asset: it is
        moved off the input-VAT account onto the bill's cost (its expense /
        GRNI account; on a received PO, to price variance, as the goods are
        already valued) in the same transaction."""
        self.ensure_one()
        credit = self.input_credit_id.sudo()
        if not credit or "state" not in credit._fields or credit.state != "ineligible":
            return
        amount = _q(self.vat_amount_bdt)
        if not amount:
            return
        env, company = self.env, self.company_id
        partner = self.vendor_id.commercial_partner_id
        target = self._expense_account(self.line_ids[:1]) if self.line_ids else None
        if not target or target == ap_account(env, company, "grni"):
            target = ap_account(env, company, "ppv")
        label = "Ineligible input VAT %s %s" % (partner.name, self.invoice_ref)
        post_ap_move(
            env,
            company,
            move.journal_id,
            self.invoice_date,
            label,
            [
                (target, label, amount, 0.0, partner),
                (ap_account(env, company, "vat_input"), label, 0.0, amount, partner),
            ],
            self.operating_unit_id,
        )
        self.message_post(
            body="Input VAT BDT %.2f is not eligible for credit (%s): reclassed to %s %s."
            % (amount, credit.display_name, target.code, target.name)
        )

    def _check_capital_lines(self):
        """A capital line names an OPEN CWIP project of the bill's company whose
        category has a CWIP account (refused at submission, not at posting)."""
        self.ensure_one()
        for cwip in self.line_ids.mapped("cwip_id").sudo():
            if cwip.state != "open" or cwip.company_id != self.company_id:
                raise UserError(
                    "Bill %s books cost to CWIP project %s, which is not an open project of %s."
                    % (self.invoice_ref, cwip.name, self.company_id.name)
                )
            cwip._fix_cwip_account()

    def _book_capital_cost(self, move):
        """M49 contract (B5, A08 M49-3): the posted CWIP items of this bill are
        booked to their projects, so CWIP cost comes from posted bills."""
        self.ensure_one()
        for cwip in self.line_ids.mapped("cwip_id").sudo():
            account = cwip._fix_cwip_account()
            text = "CWIP %s" % cwip.name
            items = move.sudo().line_ids.filtered(
                lambda ml, a=account, t=text: ml.account_id == a and (ml.name or "").endswith(t)
            )
            cwip._fix_book_cost(items)

    def _create_deductions(self):
        self.ensure_one()
        profile = self._tax_profile()
        common = {
            "company_id": self.company_id.id,
            "operating_unit_id": self.operating_unit_id.id,
            "partner_id": self.vendor_id.commercial_partner_id.id,
            "partner_tin": profile.tin or False,
            "partner_bin": profile.bin or False,
            "document_date": self.invoice_date,
            "currency_id": self.currency_id.id,
            "source_ref": self.invoice_ref,
            "vendor_invoice_id": self.id,
        }
        vals = []
        # A06 P01: deductions are statutory BDT figures
        common["currency_id"] = self.company_id.currency_id.id
        groups = defaultdict(lambda: [0.0, 0.0])
        for line in self.line_ids.filtered(lambda line: line.tds_amount > 0):
            key = (line.tds_rate_id, line.tds_multiplier)
            groups[key][0] += line.line_total_bdt
            groups[key][1] += line.tds_amount
        filer = bool(profile) and profile.is_filer_on(self.invoice_date)
        for (rate, multiplier), (base, amount) in groups.items():
            # A08 M52-10: ONE computation. The bill line already applies every
            # ITA 2023 default (no PSR s.142, no TIN s.143/163, payment not by
            # bank) in _compute_tds and the GL posts that amount; the deduction
            # sent to the return and the certificate is the same figure. (It
            # used to be recomputed here as 1.5**2 for a vendor without TIN:
            # GL 1,500, certificate 2,250.)
            vals.append(
                {
                    **common,
                    "tax_kind": "tds",
                    "rate_id": rate.id,
                    "section": rate.section,
                    "base_amount": _q(base),
                    "rate": rate.rate,
                    "multiplier": multiplier,
                    "non_filer": not filer,
                    "psr_received": filer,
                    "paid_by_bank": self.payment_channel == "bank",
                    "amount": _q(amount),
                }
            )
        if self.vds_amount:
            vals.append(
                {
                    **common,
                    "tax_kind": "vds",
                    "rate_id": self.vds_rate_id.id,
                    "section": self.vds_rate_id.section,
                    "base_amount": self.subtotal_bdt,
                    "rate": self.vds_rate_id.rate,
                    "multiplier": 1.0,
                    # VAT at source carries none of the ITA 2023 income-tax
                    # uplifts (PSR / cash payment): state it on the row
                    "psr_received": True,
                    "paid_by_bank": True,
                    "non_filer": False,
                    "amount": self.vds_amount,
                }
            )
        if vals:
            # B5 contract (A08 M51-8): a deduction is recorded with the posted
            # liability entry that credits its payable account (a plain create
            # is refused)
            self.env["fix.withholding.line"]._fix_record_deductions(vals, self.move_id)

    def _create_input_credit(self):
        self.ensure_one()
        if not self.vat_amount:
            return
        profile = self._tax_profile()
        credit = self.env["fix.input.vat.credit"].create(
            {
                "company_id": self.company_id.id,
                "operating_unit_id": self.operating_unit_id.id,
                "partner_id": self.vendor_id.commercial_partner_id.id,
                "supplier_bin": profile.bin or False,
                "supplier_enlisted": profile.turnover_enlisted,
                "supplier_mushak_no": self.supplier_mushak_no or False,
                "invoice_date": self.invoice_date,
                "taxable_amount": self.subtotal_bdt,
                "vat_amount": self.vat_amount_bdt,
                "currency_id": self.company_id.currency_id.id,
                "source_ref": self.invoice_ref,
                "vendor_invoice_id": self.id,
            }
        )
        credit.action_check_eligibility()
        self._guarded().write({"input_credit_id": credit.id})

    def action_request_payment(self) -> None:
        """T06: M52 raises payment requests as EVENTS — treasury executes
        and publishes confirmation. No synchronous call into M50. Only an
        APPROVED and MATCHED bill can be paid (approval + G3-06).

        A08 M52-4: the request takes the bill's payment lock in the same
        transaction, so a payment run no longer proposes it and a second press
        is refused: one bill, one execution. The lock closes on treasury's
        events (fix.ap.payment.events)."""
        require_finance(self.env, "Requesting a bill payment")
        Lock = self.env["fix.ap.bill.payment"].sudo()
        for inv in self:
            if inv.match_state not in PAYABLE_MATCH_STATES:
                raise UserError(
                    "G3-06: an unmatched vendor invoice cannot be paid "
                    "(state: %s — %s)" % (inv.match_state, inv.match_detail)
                )
            if inv.approval_state != "approved":
                raise UserError(
                    "Bill %s is %s — only approved bills are paid"
                    % (inv.invoice_ref, inv.approval_state)
                )
            if not inv.move_id or inv.move_id.state != "posted":
                raise UserError(
                    "Bill %s has no posted liability: only a bill approved through the matrix "
                    "(and so posted to the GL) is paid (A08 M52-2)" % inv.invoice_ref
                )
            if inv.payment_state != "not_paid" or inv._ap_live_payment():
                raise UserError("Bill %s is already %s" % (inv.invoice_ref, inv.payment_state))
            if inv._ap_requested_execution():
                raise UserError(
                    "Treasury cancelled the earlier payment request of bill %s: pay it through "
                    "a payment run." % inv.invoice_ref
                )
            # A06 P01 / D5: treasury pays BDT; a foreign bill is paid at the
            # rate of the day, and the difference to the BDT it was booked at
            # is FX gain/loss when the payment clears the payable
            amount = inv._ap_payable_bdt_on(fields.Date.context_today(inv))
            Lock.create(
                {
                    "company_id": inv.company_id.id,
                    "bill_id": inv.id,
                    "amount": amount,
                }
            )
            inv._guarded().write({"payment_state": "in_run"})
            publish(
                self.env,
                "payment.requested",
                "fix.vendor.invoice",
                inv.id,
                {
                    "vendor_id": inv.vendor_id.id,
                    "amount": amount,
                    "currency": inv.company_id.currency_id.name,
                    "bill_currency": inv.currency_id.name,
                    "bill_amount_currency": inv.total_payable,
                    "invoice_ref": inv.invoice_ref,
                    # M50 executes per OU (fix.payment.execution requires it)
                    "operating_unit_id": inv.operating_unit_id.id,
                    "company_id": inv.company_id.id,
                    "payee_partner_id": inv.vendor_id.commercial_partner_id.id,
                    "approved_by": inv.approval_log_ids.filtered(
                        lambda log: log.action == "approve"
                    )[:1].user_id.id,
                },
            )

    # ---- settling the payable (payments, LC settlement) — A06 P01 / D5 -------
    def _ap_payable_bdt_on(self, on_date):
        """What paying this bill in full costs in BDT on `on_date`: its BDT
        payable for a BDT bill, its currency payable at that day's rate for a
        foreign one."""
        self.ensure_one()
        if not self._is_foreign():
            return _q(self.total_payable)
        rate = bdt_rate(self.env, self.currency_id, self.company_id, on_date)
        return _q(self.total_payable * rate)

    def _ap_settlement_lines(self, paid_bdt, label, partner=None, share=1.0):
        """The payable side of a settlement of this bill: Dr trade payables at
        the BDT the bill booked (its `share`, with the currency figure), and
        the difference to `paid_bdt` on FX gain/loss (Dr a loss, Cr a gain).
        The caller adds the credit side (bank clearing, LC account...)."""
        self.ensure_one()
        env, company = self.env, self.company_id
        partner = partner or self.vendor_id.commercial_partner_id
        booked = _q(self.total_payable_bdt * share)
        lines = [
            (
                ap_account(env, company, "ap"),
                label,
                booked,
                0.0,
                partner,
                (self.currency_id, self.total_payable * share),
            )
        ]
        diff = _q(paid_bdt - booked)
        if diff:
            fx = ap_account(env, company, "fx_gain_loss")
            text = "FX %s on %s" % ("loss" if diff > 0 else "gain", label)
            lines.append((fx, text, diff if diff > 0 else 0.0, -diff if diff < 0 else 0.0, partner))
        return lines

    def _ap_settle_external(self, amount_bdt, credit_account, journal, ref, entry_date, source):
        """Settle this approved, posted, unpaid bill IN FULL from outside AP
        (A06 D6: an LC payment, cd_ap_ext/models/ap_lc_settlement.py): Dr trade
        payables at the BDT the bill booked, Cr `credit_account` with
        `amount_bdt` (what the settlement cost), the difference on FX
        gain/loss; the bill is marked paid under a payment lock naming
        `source`. Returns the posted move."""
        self.ensure_one()
        if self.approval_state != "approved" or not self.move_id:
            raise UserError("Bill %s is not approved and posted." % self.invoice_ref)
        if self.payment_state != "not_paid" or self._ap_live_payment():
            raise UserError("Bill %s is already %s." % (self.invoice_ref, self.payment_state))
        if self.match_state not in PAYABLE_MATCH_STATES:
            raise UserError(
                "G3-06: bill %s is %s and cannot be settled." % (self.invoice_ref, self.match_state)
            )
        partner = self.vendor_id.commercial_partner_id
        label = "%s settles bill %s %s" % (ref, partner.name, self.invoice_ref)
        lines = self._ap_settlement_lines(_q(amount_bdt), label, partner)
        lines.append((credit_account, label, 0.0, _q(amount_bdt), partner))
        move = post_ap_move(
            self.env, self.company_id, journal, entry_date, label, lines, self.operating_unit_id
        )
        self.env["fix.ap.bill.payment"].sudo().create(
            {
                "company_id": self.company_id.id,
                "bill_id": self.id,
                "amount": _q(amount_bdt),
                "state": "paid",
            }
        )
        self._guarded().write({"payment_state": "paid", "payment_move_id": move.id})
        self.message_post(body="Settled by %s (%s): BDT %.2f." % (ref, source, amount_bdt))
        return move

    def _ap_requested_execution(self):
        """Treasury's instruction from this bill's Request Payment, if any."""
        self.ensure_one()
        return (
            self.env["fix.payment.execution"]
            .sudo()
            .search([("source_model", "=", self._name), ("source_id", "=", self.id)], limit=1)
        )

    @api.model
    def _ap_release_cancelled_requests(self, bills):
        """A request treasury CANCELLED pays nothing and never will (a failed
        one can still be re-queued, so its lock stays): the bill returns to the
        pool, where a payment run can take it."""
        Lock = self.env["fix.ap.bill.payment"].sudo()
        locks = Lock.search(
            [("bill_id", "in", bills.ids), ("state", "=", "open"), ("run_line_id", "=", False)]
        )
        for lock in locks:
            bill = lock.bill_id
            if bill._ap_requested_execution().state == "cancelled":
                lock.write({"state": "failed"})
                bill.sudo()._guarded().write({"payment_state": "not_paid"})

    def _ap_live_payment(self):
        """The open or paid payment lock of this bill (BRU-APE-10)."""
        self.ensure_one()
        return (
            self.env["fix.ap.bill.payment"]
            .sudo()
            .search([("bill_id", "=", self.id), ("state", "in", ("open", "paid"))], limit=1)
        )


class FixPurchaseOrderVendorBills(models.Model):
    """The bills against a PO: the three-way match reads what earlier bills
    already claimed (A06 S6)."""

    _inherit = "fix.purchase.order"

    vendor_invoice_ids = fields.One2many(
        "fix.vendor.invoice", "requisition_id", string="Vendor Bills", readonly=True
    )


class FixVendorInvoiceLine(models.Model):
    _name = "fix.vendor.invoice.line"
    _description = "Vendor Invoice Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    invoice_id = fields.Many2one("fix.vendor.invoice", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Product", required=True)
    description = fields.Char(required=True)
    quantity = fields.Float(required=True, default=1.0)
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    unit_price = fields.Monetary(string="Unit Price", currency_field="currency_id", required=True)
    line_total = fields.Monetary(
        string="Line Total", currency_field="currency_id", compute="_compute_line", store=True
    )
    company_currency_id = fields.Many2one(related="invoice_id.company_currency_id")
    line_total_bdt = fields.Monetary(
        string="Line Total (BDT)",
        currency_field="company_currency_id",
        compute="_compute_line",
        store=True,
        help="The line at the bill-date rate (A06 P01).",
    )
    tds_category = fields.Selection(
        TDS_CATEGORIES,
        string="TDS Category",
        default="service_general",
        help="The Tax Rate Master code whose effective rate applies",
    )
    tds_category_assumed = fields.Boolean(
        string="TDS Category Assumed",
        readonly=True,
        copy=False,
        help="Defaulted because the vendor's tax profile names no category; nobody chose it.",
    )
    tds_exempt = fields.Boolean(
        default=False,
        help="Vendor holds a valid exemption certificate. Honoured only when the vendor's "
        "tax profile carries the certificate number, file and expiry (A08 M52-10).",
    )
    tds_rate_id = fields.Many2one(
        "fix.tax.rate", string="TDS Rate Row", compute="_compute_tds", store=True
    )
    cwip_id = fields.Many2one(
        "fix.cwip.entry",
        string="CWIP Project (capital)",
        index=True,
        ondelete="restrict",
        help="A capital purchase: the line debits the project's CWIP account and the posted "
        "cost is booked to the project (M49).",
    )
    tds_section = fields.Char(string="ITA 2023 Section", compute="_compute_tds", store=True)
    tds_rate = fields.Float(
        string="TDS Rate (%)", compute="_compute_tds", store=True, digits=(6, 3)
    )
    tds_multiplier = fields.Float(
        string="Non-filer Multiplier", compute="_compute_tds", store=True, digits=(6, 3)
    )
    tds_amount = fields.Monetary(
        string="TDS", currency_field="company_currency_id", compute="_compute_tds", store=True
    )

    @api.depends("quantity", "unit_price", "invoice_id.fx_rate")
    def _compute_line(self) -> None:
        for line in self:
            line.line_total = line.quantity * line.unit_price
            rate = line.invoice_id.fx_rate if line.invoice_id else 1.0
            line.line_total_bdt = _q(line.line_total * (rate or 0.0))

    @api.constrains("quantity", "unit_price")
    def _check_signs(self):
        # On the line, where it is written (a constraint on the bill's one2many
        # does not fire for a line created or edited by itself). The match sums
        # quantities: a -10 line at price 0 netted a bill for 20 down to the 10
        # received, and it read 'matched'.
        for line in self:
            if line.quantity <= 0 or line.unit_price < 0:
                raise ValidationError(
                    "Bill line %s: the quantity must be positive and the unit price not "
                    "negative. A reduction is the vendor's credit note (Mushak 6.7)."
                    % (line.description or line.id)
                )

    @api.depends(
        "line_total",
        "line_total_bdt",
        "tds_category",
        "tds_exempt",
        "invoice_id.invoice_date",
        "invoice_id.vendor_id",
        "invoice_id.company_id",
        "invoice_id.payment_channel",
    )
    def _compute_tds(self) -> None:
        """Effective-dated TDS from the Tax Rate Master; a payee without a
        valid proof of return (PSR) on the invoice date suffers the
        non-filer multiplier where the rate row says it applies."""
        Rate = self.env["fix.tax.rate"]
        Param = self.env["fix.tax.parameter"]
        Profile = self.env["fix.vendor.tax.profile"]
        for line in self:
            inv = line.invoice_id
            if not inv or not inv.vendor_id or not inv.invoice_date:
                line.update(
                    {
                        "tds_rate_id": False,
                        "tds_section": False,
                        "tds_rate": 0.0,
                        "tds_multiplier": 1.0,
                        "tds_amount": 0.0,
                    }
                )
                continue
            company = inv.company_id or self.env.company
            profile = Profile.for_partner(inv.vendor_id, company)
            payee = (
                profile.taxpayer_type
                if profile.taxpayer_type in ("company", "individual")
                else "any"
            )
            rate = Rate.find_rate(
                "tds", line.tds_category or "service_general", inv.invoice_date, company, payee
            )
            multiplier = 1.0
            if rate.non_filer_applies:
                # ITA 2023 defaults, one uplift each (the rule M51's withholding
                # line enforces): no valid, evidenced PSR (s.142), no TIN
                # (s.143/163), and payment not by bank (BRU-APE-08).
                defaults = 0
                if not (profile and profile.is_filer_on(inv.invoice_date)):
                    defaults += 1
                if not (profile and (profile.tin or "").strip()):
                    defaults += 1
                if inv.payment_channel == "non_bank":
                    defaults += 1
                if defaults:
                    uplift = Param.get_value("non_filer_multiplier", inv.invoice_date, company)
                    multiplier = round(uplift**defaults, 3)
            exempt = (
                line.tds_exempt and bool(profile) and profile.is_tds_exempt_on(inv.invoice_date)
            )
            # A06 P01: on the BDT figure
            amount = 0.0 if exempt else _q(line.line_total_bdt * rate.rate * multiplier / 100.0)
            line.update(
                {
                    "tds_rate_id": rate.id,
                    "tds_section": rate.section,
                    "tds_rate": rate.rate,
                    "tds_multiplier": multiplier,
                    "tds_amount": amount,
                }
            )

    def _check_parent_editable(self):
        # Only a transition may touch the lines of a submitted bill (not even
        # superuser code: the approval covers exactly these lines).
        if self.env["fix.vendor.invoice"]._fix_guard_has_token():
            return
        locked = self.invoice_id.filtered(
            lambda inv: inv.approval_state in ("to_approve", "approved")
        )
        if locked:
            raise UserError(
                "Bill %s is %s — its lines cannot change"
                % (locked[0].invoice_ref, locked[0].approval_state)
            )

    @api.model_create_multi
    def create(self, vals_list):
        # A08 M52-10: a line with no category takes the vendor's default
        Invoice = self.env["fix.vendor.invoice"]
        known = dict(TDS_CATEGORIES)
        for vals in vals_list:
            if vals.get("tds_category") or not vals.get("invoice_id"):
                continue
            profile = Invoice.browse(vals["invoice_id"])._tax_profile()
            code = (profile.default_tds_category or "").strip()
            vals["tds_category"] = code if code in known else "service_general"
            # A06 M16-8: nobody chose this category and it may under-withhold, so
            # the bill says so until AP sets the right one or confirms this one.
            vals["tds_category_assumed"] = code not in known
        lines = super().create(vals_list)
        lines._check_parent_editable()
        return lines

    def write(self, vals):
        self._check_parent_editable()
        if "tds_category" in vals:
            # The form echoes every field it shows: only another category is a choice.
            self.filtered(
                lambda ln: ln.tds_category_assumed and ln.tds_category != vals["tds_category"]
            ).write({"tds_category_assumed": False})
        return super().write(vals)

    def unlink(self):
        self._check_parent_editable()
        return super().unlink()
