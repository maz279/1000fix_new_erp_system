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
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .ap_gl import ap_account, ap_journal, post_ap_move

TWO = Decimal("0.01")

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

# fields of an approved bill that may no longer change
LOCKED_FIELDS = {
    "vendor_id",
    "invoice_date",
    "line_ids",
    "vat_amount",
    "vds_rate_id",
    "requisition_id",
    "currency_id",
    "company_id",
}


def _q(value):
    return float(Decimal(str(value or 0)).quantize(TWO, ROUND_HALF_UP))


# Match states a bill may be paid in: a reconciled three-way match, or a
# non-PO bill (approval-controlled).
PAYABLE_MATCH_STATES = ("matched", "not_required")


class FixVendorInvoice(models.Model):
    """A vendor invoice entering the three-way match (T03)."""

    _name = "fix.vendor.invoice"
    _description = "Vendor Invoice (three-way match)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
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
    vds_amount = fields.Monetary(
        string="VDS Deducted", currency_field="currency_id", compute="_compute_totals", store=True
    )
    tds_amount = fields.Monetary(
        string="TDS Deducted", currency_field="currency_id", compute="_compute_totals", store=True
    )
    total_payable = fields.Monetary(
        string="Total Payable", currency_field="currency_id", compute="_compute_totals", store=True
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

    @api.depends(
        "line_ids.line_total", "line_ids.tds_amount", "vat_amount", "vds_rate_id", "invoice_date"
    )
    def _compute_totals(self) -> None:
        for inv in self:
            subtotal = sum(inv.line_ids.mapped("line_total"))
            tds = sum(inv.line_ids.mapped("tds_amount"))
            vds = 0.0
            if inv.vds_rate_id and subtotal:
                vds = _q(subtotal * inv.vds_rate_id.rate / 100.0)
                if inv.vat_amount > 0:  # never withhold more VAT than the 6.3 states
                    vds = min(vds, inv.vat_amount)
            inv.subtotal = subtotal
            inv.tds_amount = _q(tds)
            inv.vds_amount = vds
            inv.gross_amount = _q(subtotal + inv.vat_amount)
            inv.total_payable = _q(subtotal + inv.vat_amount - tds - vds)

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
            for po_line in po.line_ids:
                po_lines.setdefault(po_line.product_id.id, []).append(po_line)
            invoiced, label, order = {}, {}, []
            for line in inv.line_ids:
                pid = line.product_id.id
                if pid not in invoiced:
                    invoiced[pid] = 0.0
                    label[pid] = line.description
                    order.append(pid)
                invoiced[pid] += line.quantity or 0.0
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
                qty_ok = Decimal(str(round(accepted - prior, 6))) >= Decimal(str(invoiced[pid]))
                if not qty_ok:
                    if prior:
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
                approved = [p.approved_unit_price for p in pols if p.approved_qty]
                basis = max(approved) if approved else max(p.unit_price for p in pols)
                lines = inv.line_ids.filtered(lambda ln, p=pid: ln.product_id.id == p)
                ceiling = Decimal(str(basis or 0)) + TOLERANCE
                if any(Decimal(str(ln.unit_price)) > ceiling for ln in lines):
                    problems.append("%s: price above PO" % label[pid])
                elif not approved and qty_ok:
                    problems.append("%s: PO price not approved" % label[pid])
            if problems:
                inv.match_state = "blocked"
                inv.match_detail = "\n".join(problems)
            else:
                inv.match_state = "matched"
                inv.match_detail = "PO / receipt / invoice reconciled"

    @api.constrains("bill_type", "requisition_id")
    def _check_bill_type(self):
        for inv in self:
            if inv.bill_type == "non_po" and inv.requisition_id:
                raise ValidationError(
                    "Bill %s is linked to a purchase order: it must use the three-way match"
                    % (inv.invoice_ref or inv.id)
                )

    # -------------------------------------------------------------- guards --
    def write(self, vals):
        if LOCKED_FIELDS & set(vals) and not self.env.context.get("ap_internal"):
            locked = self.filtered(lambda inv: inv.approval_state in ("to_approve", "approved"))
            if locked:
                raise UserError(
                    "Bill %s is %s — reset it to draft (reject) before changing amounts"
                    % (locked[0].invoice_ref, locked[0].approval_state)
                )
        return super().write(vals)

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
                "amount": self.gross_amount,
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
            dup = inv._duplicates()
            if dup:
                raise UserError(
                    "Duplicate prevention: %s already has bill reference %s (id %s)"
                    % (inv.vendor_id.display_name, inv.invoice_ref, dup[0].id)
                )
            inv.line_ids._compute_tds()
            inv._compute_totals()
            levels = self.env["fix.ap.approval.rule"].levels_for(inv.gross_amount, inv.company_id)
            if not levels:
                raise UserError(
                    "No approval-matrix level covers BDT %.2f in %s — maintain the AP "
                    "approval matrix first" % (inv.gross_amount, inv.company_id.name)
                )
            inv.with_context(ap_internal=True).write(
                {
                    "approval_state": "to_approve",
                    "approval_level": 0,
                    "approval_levels_required": len(levels),
                    "submitted_by": self.env.user.id,
                }
            )
            inv._log("submit")
        return True

    def _next_level(self):
        self.ensure_one()
        levels = self.env["fix.ap.approval.rule"].levels_for(self.gross_amount, self.company_id)
        return levels[self.approval_level] if self.approval_level < len(levels) else None

    def action_approve(self):
        """Approve the next matrix level. Segregation of duties: the approver
        is in the level's group, did not submit the bill and did not approve
        a lower level. The last level posts the bill."""
        user = self.env.user
        for inv in self:
            if inv.approval_state != "to_approve":
                raise UserError("Bill %s is not awaiting approval" % inv.invoice_ref)
            rule = inv._next_level()
            if not rule:
                raise UserError("Bill %s has no pending approval level" % inv.invoice_ref)
            if rule.group_id not in user.all_group_ids:
                raise UserError(
                    "Level %d (%s) must be approved by a member of %s"
                    % (rule.level, rule.name, rule.group_id.display_name)
                )
            if user == inv.submitted_by:
                raise UserError("Segregation of duties: the submitter cannot approve the bill")
            earlier = inv.approval_log_ids.filtered(lambda log: log.action == "approve")
            if user in earlier.mapped("user_id"):
                raise UserError("Segregation of duties: one user approves one level only")
            inv._log("approve", rule)
            level = inv.approval_level + 1
            done = level >= inv.approval_levels_required
            inv.with_context(ap_internal=True).write(
                {"approval_level": level, "approval_state": "approved" if done else "to_approve"}
            )
            if done:
                inv._post_approved_bill()
        return True

    def action_reject(self):
        for inv in self:
            if inv.approval_state != "to_approve":
                raise UserError("Only a bill awaiting approval can be rejected")
            rule = inv._next_level()
            if rule and rule.group_id not in self.env.user.all_group_ids:
                raise UserError("Only a %s member can reject at this level" % rule.group_id.name)
            inv._log("reject", rule)
            inv.with_context(ap_internal=True).write(
                {"approval_state": "rejected", "approval_level": 0}
            )
        return True

    def action_reset_draft(self):
        for inv in self:
            if inv.approval_state != "rejected":
                raise UserError("Only a rejected bill returns to draft")
            inv._log("reset")
            inv.with_context(ap_internal=True).write({"approval_state": "draft"})
        return True

    def _expense_account(self, line):
        """GRNI clearing for PO-received goods, else the product's expense
        account, else the configured default expense role."""
        if self.requisition_id and line.product_id in self.requisition_id.line_ids.product_id:
            return ap_account(self.env, self.company_id, "grni")
        account = (
            line.product_id.product_tmpl_id.with_company(self.company_id)
            ._get_product_accounts()
            .get("expense")
        )
        return account or ap_account(self.env, self.company_id, "expense")

    def _post_approved_bill(self):
        """Dr expense / GRNI, Dr input VAT; Cr TDS payable, Cr VDS payable,
        Cr trade payables — then the deduction lines and the input credit."""
        self.ensure_one()
        env, company = self.env, self.company_id
        partner = self.vendor_id.commercial_partner_id
        label = "Bill %s %s" % (partner.name, self.invoice_ref)
        lines = []
        by_account = defaultdict(float)
        for line in self.line_ids:
            by_account[self._expense_account(line)] += line.line_total
        for account, amount in by_account.items():
            lines.append((account, label, _q(amount), 0.0, partner))
        if self.vat_amount:
            lines.append(
                (
                    ap_account(env, company, "vat_input"),
                    "Input VAT " + label,
                    _q(self.vat_amount),
                    0.0,
                    partner,
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
        lines.append((ap_account(env, company, "ap"), label, 0.0, self.total_payable, partner))
        move = post_ap_move(
            env,
            company,
            ap_journal(env, company, "purchase"),
            self.invoice_date,
            label,
            lines,
            self.operating_unit_id,
        )
        self.with_context(ap_internal=True).write({"move_id": move.id})
        self._create_deductions()
        self._create_input_credit()
        publish(
            env,
            "vendor_bill.approved",
            "fix.vendor.invoice",
            self.id,
            {
                "vendor_id": partner.id,
                "gross": self.gross_amount,
                "tds": self.tds_amount,
                "vds": self.vds_amount,
                "payable": self.total_payable,
                "move_id": move.id,
            },
        )

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
        groups = defaultdict(lambda: [0.0, 0.0])
        for line in self.line_ids.filtered(lambda line: line.tds_amount > 0):
            key = (line.tds_rate_id, line.tds_multiplier)
            groups[key][0] += line.line_total
            groups[key][1] += line.tds_amount
        for (rate, multiplier), (base, _amount) in groups.items():
            # ITA 2023: a missing TIN is a 50% default on top of the non-filer
            # uplift, so the withheld amount is recomputed from the flags rather
            # than trusting the line-level multiplier alone.
            defaults = 1 if multiplier > 1 else 0
            has_tin = bool((profile.tin or "").strip())
            if not has_tin:
                defaults += 1
            statutory = round(1.5**defaults, 3)
            base_q = _q(base)
            withheld = _q(base_q * (rate.rate or 0.0) * statutory / 100.0)
            vals.append(
                {
                    **common,
                    "tax_kind": "tds",
                    "rate_id": rate.id,
                    "section": rate.section,
                    "base_amount": base_q,
                    "rate": rate.rate,
                    "multiplier": statutory,
                    "non_filer": multiplier > 1,
                    "psr_received": multiplier <= 1,
                    "paid_by_bank": True,
                    "amount": withheld,
                }
            )
        if self.vds_amount:
            vals.append(
                {
                    **common,
                    "tax_kind": "vds",
                    "rate_id": self.vds_rate_id.id,
                    "section": self.vds_rate_id.section,
                    "base_amount": self.subtotal,
                    "rate": self.vds_rate_id.rate,
                    "multiplier": 1.0,
                    "amount": self.vds_amount,
                }
            )
        if vals:
            self.env["fix.withholding.line"].create(vals)

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
                "taxable_amount": self.subtotal,
                "vat_amount": self.vat_amount,
                "currency_id": self.currency_id.id,
                "source_ref": self.invoice_ref,
                "vendor_invoice_id": self.id,
            }
        )
        credit.action_check_eligibility()
        self.with_context(ap_internal=True).write({"input_credit_id": credit.id})

    def action_request_payment(self) -> None:
        """T06: M52 raises payment requests as EVENTS — treasury executes
        and publishes confirmation. No synchronous call into M50. Only an
        APPROVED and MATCHED bill can be paid (approval + G3-06)."""
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
            if inv.payment_state != "not_paid":
                raise UserError("Bill %s is already %s" % (inv.invoice_ref, inv.payment_state))
            publish(
                self.env,
                "payment.requested",
                "fix.vendor.invoice",
                inv.id,
                {
                    "vendor_id": inv.vendor_id.id,
                    "amount": inv.total_payable,
                    "currency": inv.currency_id.name,
                    "invoice_ref": inv.invoice_ref,
                    # M50 executes per OU (fix.payment.execution requires it)
                    "operating_unit_id": inv.operating_unit_id.id,
                },
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
    tds_category = fields.Selection(
        TDS_CATEGORIES,
        string="TDS Category",
        default="service_general",
        help="The Tax Rate Master code whose effective rate applies",
    )
    tds_exempt = fields.Boolean(default=False, help="Vendor holds a valid exempt certificate (ATS)")
    tds_rate_id = fields.Many2one(
        "fix.tax.rate", string="TDS Rate Row", compute="_compute_tds", store=True
    )
    tds_section = fields.Char(string="ITA 2023 Section", compute="_compute_tds", store=True)
    tds_rate = fields.Float(
        string="TDS Rate (%)", compute="_compute_tds", store=True, digits=(6, 3)
    )
    tds_multiplier = fields.Float(
        string="Non-filer Multiplier", compute="_compute_tds", store=True, digits=(6, 3)
    )
    tds_amount = fields.Monetary(
        string="TDS", currency_field="currency_id", compute="_compute_tds", store=True
    )

    @api.depends("quantity", "unit_price")
    def _compute_line(self) -> None:
        for line in self:
            line.line_total = line.quantity * line.unit_price

    @api.depends(
        "line_total",
        "tds_category",
        "tds_exempt",
        "invoice_id.invoice_date",
        "invoice_id.vendor_id",
        "invoice_id.company_id",
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
            if rate.non_filer_applies and not (profile and profile.is_filer_on(inv.invoice_date)):
                multiplier = Param.get_value("non_filer_multiplier", inv.invoice_date, company)
            amount = (
                0.0 if line.tds_exempt else _q(line.line_total * rate.rate * multiplier / 100.0)
            )
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
        if self.env.context.get("ap_internal"):
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
        lines = super().create(vals_list)
        lines._check_parent_editable()
        return lines

    def write(self, vals):
        self._check_parent_editable()
        return super().write(vals)

    def unlink(self):
        self._check_parent_editable()
        return super().unlink()
