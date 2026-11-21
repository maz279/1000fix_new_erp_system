# cd_ap_ext — goods received not invoiced, as one basis (A06 ERP audit, 20 Nov 2026).
#
# Owner decisions D2 / D5: 100503 Stock Incoming is GRNI. Every goods receipt
# credits it at the receipt value (stream LEDGER: qty accepted x the M15
# receipt unit cost in BDT, at the order's stamped rate); a bill debits it for
# exactly the received value of what it bills, the price difference going to
# 600007 and the rate difference to 500030 (fix_ap_ext._fix_bill_line_split).
#
#   - P05: a service or non-stock line has no stock receipt. Its service-entry
#     confirmation now posts Dr expense / Cr GRNI at the receipt value, so the
#     bill that clears GRNI has something to clear and the service is expensed.
#   - P13 / X26: the GRNI accrual (and the M16 GR/IR report) read ONE as-at
#     basis that ties to the GRNI account: accepted (not rejected) quantity of
#     receipts posted by the date, less returns shipped by then, less what bills
#     posted by then billed net of their return credit notes, at the receipt
#     value in BDT. It used to read received (not accepted) quantity at the
#     live PO price in the PO currency, with no date.
#   - X11: an import without a PO credits GRNI at receipt (cd_import_order);
#     its supplier bill was a non-PO bill that debited expense, so GRNI never
#     cleared and the cost was counted twice. Such a bill is now an "import"
#     bill linked to the received import: matched against it and clearing GRNI.
#   - P09: a non-PO bill buys no stock parts and needs an active supplier (the
#     register is cd_vendor_portal's) or an Accounting Administrator's
#     recorded exception.
#   - P14 / P15: duplicate references compared normalised; a bill on a PO takes
#     the order's payment terms.
import re
from collections import defaultdict

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .ap_gl import ap_account, ap_journal, post_ap_move
from .fix_ap_controls import require_finance
from .fix_ap_ext import RTV_GONE_STATES, _q, allocate

IMPORT_MODEL = "fix.import.order"


def norm_ref(ref):
    """A06 P14: 'INV-001', 'inv 001' and 'INV/001 ' are one reference."""
    return re.sub(r"[^0-9a-z]", "", (ref or "").lower())


# ============================================================ the bill
class FixVendorInvoiceGrni(models.Model):
    _inherit = "fix.vendor.invoice"

    bill_type = fields.Selection(
        selection_add=[("import", "Import without a PO (clears GRNI)")],
        ondelete={"import": "set default"},
    )
    import_order_ref = fields.Reference(
        selection="_fix_import_models",
        string="Import (no PO)",
        help="The received import (M44) this supplier bill is for, when it has no M16 "
        "purchase order: the bill clears the GRNI its receipt credited.",
    )
    non_po_exception_reason = fields.Char(
        string="Non-PO Supplier Exception", readonly=True, copy=False
    )
    non_po_exception_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    non_po_exception_at = fields.Datetime(readonly=True, copy=False)

    @api.model
    def _fix_import_models(self):
        return [(IMPORT_MODEL, "Import Order")] if IMPORT_MODEL in self.env else []

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "non_po_exception_reason",
            "non_po_exception_by_id",
            "non_po_exception_at",
        }

    # ---- P15: the order's payment terms -----------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        Order = self.env["fix.purchase.order"].sudo()
        for vals in vals_list:
            if vals.get("requisition_id") and "payment_term_days" not in vals:
                terms = Order.browse(vals["requisition_id"]).exists().payment_terms or ""
                days = re.search(r"(\d{1,3})", terms)
                if days:
                    vals["payment_term_days"] = int(days.group(1))
        return super().create(vals_list)

    # ---- P14: duplicates ----------------------------------------------------
    def _duplicates(self):
        """Other live bills of the same vendor whose reference is the same
        once case, spaces and punctuation are ignored."""
        self.ensure_one()
        key = norm_ref(self.invoice_ref)
        if not key:
            return super()._duplicates()
        candidates = self.sudo().search(
            [
                ("id", "!=", self.id),
                ("company_id", "=", self.company_id.id),
                ("vendor_id.commercial_partner_id", "=", self.vendor_id.commercial_partner_id.id),
                ("approval_state", "!=", "rejected"),
            ]
        )
        return candidates.filtered(lambda b: norm_ref(b.invoice_ref) == key).with_env(self.env)

    # ---- X11: imports without a PO ------------------------------------------
    @api.constrains("bill_type", "import_order_ref", "requisition_id")
    def _check_import_bill(self):
        for inv in self:
            if inv.bill_type == "import" and inv.requisition_id:
                raise ValidationError(
                    "Bill %s is linked to a purchase order: it uses the three-way match."
                    % (inv.invoice_ref or inv.id)
                )
            if inv.import_order_ref and inv.bill_type != "import":
                raise ValidationError(
                    "Bill %s names an import: make it an import bill." % (inv.invoice_ref or inv.id)
                )

    def _fix_import(self):
        self.ensure_one()
        ref = self.import_order_ref
        return ref.sudo() if ref and ref._name == IMPORT_MODEL else None

    def _fix_import_lines(self, product):
        imp = self._fix_import()
        if not imp:
            return []
        return [ln for ln in imp.line_ids if ln.part_id.product_id == product]

    def _fix_grni_source_lines(self, line):
        result = super()._fix_grni_source_lines(line)
        if result or self.bill_type != "import":
            return result
        imp = self._fix_import()
        if not imp or not imp.goods_move_id:
            return []
        out = []
        for iline in self._fix_import_lines(line.product_id):
            qty = iline.quantity or 0.0
            if qty <= 0:
                continue
            out.append((iline._goods_value_bdt() / qty, qty, imp.fx_rate or 1.0))
        if not out:
            return []
        # bill quantity over the import's lines (earlier import bills first)
        earlier = self.sudo().search(
            [
                ("id", "<", self.id or 0),
                ("bill_type", "=", "import"),
                ("import_order_ref", "=", "%s,%d" % (IMPORT_MODEL, imp.id)),
                ("approval_state", "!=", "rejected"),
            ]
        )
        prior = sum(
            bl.quantity for b in earlier for bl in b.line_ids if bl.product_id == line.product_id
        )
        caps = []
        for value, qty, rate in out:
            take = min(qty, prior)
            prior -= take
            caps.append(((value, rate), qty - take))
        return [(v, q, r) for (v, r), q in allocate(caps, line.quantity or 0.0)]

    @api.depends("import_order_ref", "bill_type")
    def _compute_match(self):
        others = self.filtered(lambda inv: inv.bill_type != "import")
        if others:
            super(FixVendorInvoiceGrni, others)._compute_match()
        for inv in self - others:
            inv.match_state, inv.match_detail = inv._fix_import_match()

    def _fix_import_match(self):
        self.ensure_one()
        imp = self._fix_import()
        if not imp:
            return "unmatched", "No received import linked"
        if imp.purchase_order_id:
            return "blocked", "Import %s has purchase order %s: bill it against the order" % (
                imp.name,
                imp.purchase_order_id.name,
            )
        if not imp.goods_move_id:
            return "blocked", "Import %s is not received yet" % imp.name
        if imp.supplier_id.commercial_partner_id != self.vendor_id.commercial_partner_id:
            return "blocked", "%s is not the supplier of import %s" % (
                self.vendor_id.display_name,
                imp.name,
            )
        if self.currency_id != imp.currency_id:
            return "blocked", "The bill is in %s but import %s is in %s" % (
                self.currency_id.name,
                imp.name,
                imp.currency_id.name,
            )
        my_id = self._origin.id or self.id
        domain = [
            ("bill_type", "=", "import"),
            ("import_order_ref", "=", "%s,%d" % (IMPORT_MODEL, imp.id)),
            ("approval_state", "!=", "rejected"),
        ]
        if isinstance(my_id, int):
            domain.append(("id", "<", my_id))
        earlier = self.sudo().search(domain)
        problems = []
        for product in self.line_ids.product_id:
            ilines = self._fix_import_lines(product)
            if not ilines:
                problems.append("%s: not on import %s" % (product.display_name, imp.name))
                continue
            received = sum(ln.quantity or 0.0 for ln in ilines)
            prior = sum(
                bl.quantity for b in earlier for bl in b.line_ids if bl.product_id == product
            )
            billed = sum(ln.quantity for ln in self.line_ids if ln.product_id == product)
            if billed > received - prior + 1e-6:
                problems.append(
                    "%s: imported %.2f, %.2f already billed, invoiced %.2f"
                    % (product.display_name, received, prior, billed)
                )
            price = max(ln.unit_price or 0.0 for ln in ilines)
            if any(
                ln.unit_price > price + 0.01 for ln in self.line_ids if ln.product_id == product
            ):
                problems.append("%s: price above the import order" % product.display_name)
        if problems:
            return "blocked", "\n".join(problems)
        return "matched", "Import / receipt / invoice reconciled"

    # ---- P09: non-PO bills --------------------------------------------------
    def _fix_is_stock_part(self, product):
        if not product:
            return False
        if "is_storable" in product._fields and product.is_storable:
            return True
        if "fix.spare.part" in self.env:
            return bool(
                self.env["fix.spare.part"].sudo().search_count([("product_id", "=", product.id)])
            )
        return False

    def _fix_non_po_supplier_problems(self):
        """Why the vendor may not be paid on a non-PO bill without an
        exception (filled in by cd_vendor_portal, which owns the register)."""
        return []

    def _fix_check_non_po(self):
        self.ensure_one()
        if self.bill_type != "non_po":
            return
        parts = self.line_ids.product_id.filtered(self._fix_is_stock_part)
        if parts:
            raise UserError(
                "BRU-PRO-01: bill %s buys stock parts (%s) without a purchase order. Stock is "
                "bought on a PO (or recorded as an import) so that it is received and valued."
                % (self.invoice_ref, ", ".join(parts.mapped("display_name")))
            )
        problems = self._fix_non_po_supplier_problems()
        if problems and not self.non_po_exception_by_id:
            raise UserError(
                "BRU-PRO-02: bill %s is a non-PO bill from %s, which %s. An Accounting "
                "Administrator records an exception before it is submitted."
                % (self.invoice_ref, self.vendor_id.display_name, "; ".join(problems))
            )

    def action_approve_non_po_exception(self, reason=None):
        """An Accounting Administrator other than the bill's maker accepts a
        non-PO bill from a supplier that is not active (never a deactivated
        one: cd_vendor_portal refuses those outright)."""
        require_finance(self.env, "Recording a non-PO supplier exception", manager=True)
        for inv in self:
            if inv.bill_type != "non_po" or inv.approval_state not in ("draft", "rejected"):
                raise UserError("Record the exception on a draft non-PO bill.")
            if len((reason or "").strip()) < 10:
                raise UserError(
                    "State why bill %s is accepted from this supplier." % inv.invoice_ref
                )
            if not self.env.su and self.env.user in (inv.sudo().create_uid | inv.submitted_by):
                raise UserError(
                    "Segregation of duties: you raised bill %s; another administrator records "
                    "its exception." % inv.invoice_ref
                )
            inv._guarded().write(
                {
                    "non_po_exception_reason": reason.strip(),
                    "non_po_exception_by_id": self.env.uid,
                    "non_po_exception_at": fields.Datetime.now(),
                }
            )
            inv.message_post(body="Non-PO supplier exception recorded: %s" % reason.strip())
        return True

    def action_submit_approval(self):
        for inv in self:
            inv._fix_check_non_po()
        result = super().action_submit_approval()
        # A06 P33: a bill that passed its three-way match is announced once,
        # when it goes for approval on that match
        for inv in self.filtered(lambda b: b.bill_type in ("po", "import")):
            if inv.match_state == "matched":
                publish(
                    self.env,
                    "invoice.matched",
                    "fix.vendor.invoice",
                    inv.id,
                    {
                        "invoice_ref": inv.invoice_ref,
                        "vendor_id": inv.vendor_id.commercial_partner_id.id,
                        "po_id": inv.requisition_id.id or False,
                        "gross_bdt": inv.gross_amount_bdt,
                        "detail": inv.match_detail or "",
                    },
                )
        return result

    def _post_approved_bill(self):
        self._fix_check_non_po()
        return super()._post_approved_bill()


# ============================================================ service entry
class FixPurchaseServiceEntryGrni(models.Model):
    """P05: a confirmed service entry is the service's receipt; it posts the
    service's cost against GRNI at the receipt value."""

    _inherit = "fix.purchase.service.entry"

    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"move_id"}

    def action_confirm(self):
        result = super().action_confirm()
        for rec in self.filtered(lambda r: r.state == "confirmed" and not r.move_id):
            rec._fix_post_receipt()
        return result

    def _fix_post_receipt(self):
        """Posted as the system once the requester's confirmation passed its
        checks: the requester holds no accounting rights."""
        self.ensure_one()
        env = self.env(su=True)
        order = self.purchase_order_id.sudo()
        company = order.company_id
        rline = self.receipt_id.sudo().line_ids[:1]
        value = _q((rline.unit_value_bdt or 0.0) * (rline.qty_received or 0.0))
        if not value:
            return
        product = self.product_id
        expense = product.product_tmpl_id.with_company(company)._get_product_accounts().get(
            "expense"
        ) or ap_account(env, company, "expense")
        label = "Service entry %s %s %s" % (self.name, order.name, product.display_name)
        partner = order.vendor_id.commercial_partner_id
        move = post_ap_move(
            env,
            company,
            ap_journal(env, company, "purchase"),
            fields.Date.context_today(self),
            label,
            [
                (expense, label, value, 0.0, partner),
                (ap_account(env, company, "grni"), label, 0.0, value, partner),
            ],
            order.operating_unit_id,
        )
        self.sudo()._guarded().write({"move_id": move.id})


# ============================================================ GRNI rows
def _bills_as_of(env, as_of, company):
    domain = [
        ("approval_state", "=", "approved"),
        ("move_id", "!=", False),
        ("invoice_date", "<=", as_of),
    ]
    if company:
        domain.append(("company_id", "=", company.id))
    return env["fix.vendor.invoice"].sudo().search(domain)


def grni_rows_as_of(env, as_of, company=None):
    """X26 / P13: per received line, what GRNI still holds at `as_of`, in BDT.
    Read as the system (it is the reconciliation of an account); callers
    filter the company."""
    Bill = env["fix.vendor.invoice"]
    rows = []
    bills = _bills_as_of(env, as_of, company)
    billed = defaultdict(float)  # (po id, product id) -> qty, net of credit notes
    import_billed = defaultdict(float)
    for bill in bills:
        for line in bill.line_ids:
            if bill.bill_type == "po" and bill.requisition_id:
                billed[(bill.requisition_id.id, line.product_id.id)] += line.quantity
            elif bill.bill_type == "import" and bill.import_order_ref:
                import_billed[(bill.import_order_ref.id, line.product_id.id)] += line.quantity
        for note in bill.note_ids:
            if (
                note.note_type == "decrease"
                and note.state in ("approved", "applied")
                and note.product_id
                and note.return_qty
                and note.note_date <= as_of
            ):
                billed[(bill.requisition_id.id, note.product_id.id)] -= note.return_qty
    returned = defaultdict(float)
    if "fix.stock.rtv" in env:
        rtvs = (
            env["fix.stock.rtv"]
            .sudo()
            .search([("purchase_order_id", "!=", False), ("state", "in", RTV_GONE_STATES)])
        )
        for rtv in rtvs:
            day = fields.Date.to_date(rtv.shipped_at) if rtv.shipped_at else None
            if rtv.quarantine_id or (day and day > as_of):
                continue  # a rejected unit never counted as accepted
            returned[(rtv.purchase_order_id.id, rtv.part_id.product_id.id)] += rtv.qty or 0.0
    domain = [("state", "=", "posted"), ("receipt_id.received_on", "<=", as_of)]
    if company:
        domain.append(("receipt_id.company_id", "=", company.id))
    receipt_lines = env["fix.purchase.receipt.line"].sudo().search(domain)
    by_po_line = defaultdict(float)
    for rl in receipt_lines:
        accepted = rl.qty_received - rl.qty_rejected  # pending inspection still held
        by_po_line[rl.po_line_id] += accepted
    # consume billed + returned quantities per (po, product) over the lines in order
    used = defaultdict(float)
    for key, qty in returned.items():
        used[key] += qty
    for key, qty in billed.items():
        used[key] += qty
    for pol in sorted(by_po_line, key=lambda p: p.id):
        key = (pol.order_id.id, pol.product_id.id)
        accepted = by_po_line[pol]
        take = min(accepted, max(used[key], 0.0))
        used[key] -= take
        open_qty = accepted - take
        if open_qty <= 1e-6:
            continue
        unit = Bill._fix_receipt_unit_value(pol)
        received_on = max(
            (rl.receipt_id.received_on for rl in pol.receipt_line_ids if rl in receipt_lines),
            default=None,
        )
        rows.append(
            {
                "po_line": pol,
                "order_ref": pol.order_id.name or "",
                "vendor": pol.order_id.vendor_id,
                "product": pol.product_id,
                "received": accepted,
                "invoiced": take,
                "open_qty": open_qty,
                "unit_price": round(unit, 6),
                "accrual": _q(open_qty * unit),
                "received_on": received_on,
                "age_days": (as_of - received_on).days if received_on else None,
            }
        )
    # X11: imports without a PO, received by the date
    if IMPORT_MODEL in env:
        domain = [
            ("purchase_order_id", "=", False),
            ("goods_move_id", "!=", False),
            ("received_on", "<=", as_of),
        ]
        if company:
            domain.append(("company_id", "=", company.id))
        for imp in env[IMPORT_MODEL].sudo().search(domain):
            for iline in imp.line_ids:
                product = iline.part_id.product_id
                qty = iline.quantity or 0.0
                key = (imp.id, product.id)
                take = min(qty, import_billed[key])
                import_billed[key] -= take
                open_qty = qty - take
                if open_qty <= 1e-6 or qty <= 0:
                    continue
                unit = iline._goods_value_bdt() / qty
                rows.append(
                    {
                        "po_line": None,
                        "order_ref": imp.name,
                        "vendor": imp.supplier_id,
                        "product": product,
                        "received": qty,
                        "invoiced": take,
                        "open_qty": open_qty,
                        "unit_price": round(unit, 6),
                        "accrual": _q(open_qty * unit),
                        "received_on": imp.received_on,
                        "age_days": (as_of - imp.received_on).days if imp.received_on else None,
                    }
                )
    return rows
