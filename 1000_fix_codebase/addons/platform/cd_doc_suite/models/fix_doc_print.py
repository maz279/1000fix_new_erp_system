"""The commercial document print standard (17 Nov 2026).

Every customer document - tax invoice (Mushak 6.3), local proforma invoice,
quotation, repair estimate - prints the same professional body, built by the
shared QWeb blocks in report/report_commercial_layout.xml from one payload:

    header      title, status chip, number, date / due / validity, meta rows
    bill_to     name, customer code, address, phone, email, BIN, category
    lines       SL / item code / description (+ type, serial) / qty / unit /
                unit price / discount / amount [/ VAT % / VAT / total]
    totals      items & quantity, subtotal before discount, discount,
                taxable value, VAT, grand total (+ advance / paid / balance)
    words       the grand total in words (lakh-crore, "Taka ... Only")

The payload is computed here (never in the template), from the records'
own stored figures, so the PDF states exactly what the books hold.
"""

from odoo import models
from odoo.addons.cd_catalogue.models.fix_commercial_line import LINE_TYPE_LABELS

from .fix_doc_words import _safe_words

STATE_CHIPS = {
    "draft": "DRAFT",
    "issued": "ISSUED",
    "paid": "PAID",
    "credited": "CREDITED",
    "written_off": "WRITTEN OFF",
    "cancelled": "CANCELLED",
    "converted": "INVOICED",
    "approved": "APPROVED",
    "sent": "SENT",
    "accepted": "ACCEPTED",
    "declined": "DECLINED",
    "rejected": "REJECTED",
    "expired": "EXPIRED",
    "superseded": "SUPERSEDED",
}

# Printed on every service invoice (the legacy TFSL/SI/RT-006 policy block).
UNCLAIMED_POLICY = (
    "Unclaimed product policy: a product not collected within 90 (ninety) days of repair "
    "completion is considered abandoned; 1000FiX may dispose of, scrap or otherwise handle "
    "it and bears no further responsibility for it."
)


def fmt_money(value):
    return f"{float(value or 0.0):,.2f}"


def fmt_qty(value):
    value = float(value or 0.0)
    return ("%d" % value) if value == int(value) else ("%g" % value)


def fmt_date(value):
    return value.strftime("%d-%b-%Y") if value else ""


class FixDocPrintMixin(models.AbstractModel):
    _name = "fix.doc.print.mixin"
    _description = "Commercial Document Print Payload"

    def _fix_doc_line_rows(self, lines, vat_of=None):
        """Line dicts for the shared table; sections / notes as rows of their own."""
        rows, sl = [], 0
        for line in lines:
            display = line.display_type if "display_type" in line._fields else False
            if display:
                rows.append({"section": display == "line_section", "text": line.description or ""})
                continue
            sl += 1
            qty = line.quantity or 0.0
            price = line.unit_price or 0.0
            if "gross_amount" in line._fields:
                gross = line.gross_amount or round(qty * price, 2)
            else:
                gross = round(qty * price, 2)
            disc = line.discount_amount if "discount_amount" in line._fields else 0.0
            if "subtotal" in line._fields:
                amount = line.subtotal
            elif "taxable_amount" in line._fields:
                amount = line.taxable_amount
            else:
                amount = line.line_total
            row = {
                "sl": sl,
                "code": line.item_code or (line.product_id.default_code or ""),
                "type": LINE_TYPE_LABELS.get(line.line_type or "", ""),
                "description": line.description or line.product_id.name or "",
                "serial": line.serial_ref or "",
                "qty": fmt_qty(qty),
                "uom": line.uom_id.name or "",
                "price": fmt_money(price),
                "disc": fmt_money(disc) if disc else "",
                "disc_pct": ("%g%%" % line.discount_pct)
                if "discount_pct" in line._fields and line.discount_pct
                else "",
                "gross": fmt_money(gross),
                "amount": fmt_money(amount),
                "vat_rate": "",
                "vat": "",
                "total": fmt_money(amount),
            }
            if vat_of is not None:
                rate, vat = vat_of(line)
                row["vat_rate"] = ("%g%%" % rate) if rate is not None else ""
                row["vat"] = fmt_money(vat)
                row["total"] = fmt_money((amount or 0.0) + (vat or 0.0))
            rows.append(row)
        return rows

    def _fix_doc_company_block(self):
        company = (
            self.company_id
            if "company_id" in self._fields and self.company_id
            else (self.env.company)
        )
        Invoice = self.env.get("fix.ar.invoice")
        bin_no = company.vat or ""
        if not bin_no and Invoice is not None and hasattr(Invoice, "_company_bin"):
            bin_no = Invoice.sudo()._company_bin(company) or ""
        banks = company.partner_id.bank_ids if company.partner_id else []
        # one line under the seller name (Mushak-6.3 states the supplier's address);
        # the letterhead's multi-line address block is hidden in doc_suite.css
        city_zip = " ".join(x for x in (company.city, company.zip) if x)
        address = ", ".join(
            x for x in (company.street, company.street2, city_zip, company.country_id.name) if x
        )
        return {
            "name": company.name,
            "address": address,
            "bin": bin_no,
            "banks": [
                "%s — A/C %s%s"
                % (
                    b.bank_id.name or "Bank",
                    b.acc_number,
                    (" (%s)" % b.acc_holder_name) if b.acc_holder_name else "",
                )
                for b in banks
            ],
        }


class FixArInvoicePrint(models.Model):
    _name = "fix.ar.invoice"
    _inherit = ["fix.ar.invoice", "fix.doc.print.mixin"]

    def _fix_print_payload(self):
        self.ensure_one()
        party = self._fix_doc_party()
        lines = self.line_ids.sorted(lambda r: (r.sequence, r.id))
        rows = self._fix_doc_line_rows(lines, vat_of=lambda ln: (ln.vat_rate, ln.vat_amount))
        meta = [
            ("Invoice No.", self.name if self.name and self.name != "New" else "(draft)"),
            ("Invoice Date", fmt_date(self.invoice_date)),
            ("Due Date", fmt_date(self.date_due)),
        ]
        if self.mushak_id:
            meta.append(("Mushak 6.3 No.", self.mushak_id.mushak_no or ""))
        if self.customer_po_ref:
            meta.append(
                (
                    "Customer PO / Ref",
                    self.customer_po_ref
                    + ((" · " + fmt_date(self.customer_po_date)) if self.customer_po_date else ""),
                )
            )
        if self.source_model == "fix.service.order" and self.source_id:
            order = self.env["fix.service.order"].sudo().browse(self.source_id).exists()
            if order:
                meta.append(("Service Order", order.name))
        if self.challan_ref:
            meta.append(("Delivery Challan", self.challan_ref))
        if self.salesperson_id:
            meta.append(("Sales Person", self.salesperson_id.name))
        if self.branch_id:
            meta.append(("Branch", self.branch_id.name))
        if self.payment_method_id:
            meta.append(("Payment Method", self.payment_method_id.name))
        totals = [
            ("Total Items / Qty", "%s / %s" % (self.item_count, fmt_qty(self.total_quantity)), ""),
            ("Subtotal (before discount)", fmt_money(self.gross_total), ""),
        ]
        if self.discount_total:
            totals.append(("Less: Discount", "- " + fmt_money(self.discount_total), ""))
        totals += [
            ("Taxable Value", fmt_money(self.taxable_amount), ""),
            ("VAT", fmt_money(self.vat_amount), ""),
        ]
        if self.loyalty_discount_amount:
            totals.append(
                ("Less: Loyalty Redemption", "- " + fmt_money(self.loyalty_discount_amount), "")
            )
        totals.append(("Grand Total (BDT)", fmt_money(self.total_payable), "grand"))
        if self.amount_paid:
            totals.append(("Paid", fmt_money(self.amount_paid), ""))
        if self.state not in ("draft", "cancelled") and self.amount_residual:
            totals.append(("Balance Due", fmt_money(self.amount_residual), "due"))
        title = self._fix_print_title()
        notes = [
            "Issued under the VAT & Supplementary Duty Act 2012 (Mushak-6.3, Rule 40). "
            "Prices exclude VAT; VAT is shown per line at the rate in force.",
        ]
        if self.manual_reason and self.source_model == "manual":
            notes.append("Reason: %s" % self.manual_reason)
        if self.remarks:
            notes.append("Remarks: %s" % self.remarks)
        return {
            "title": title,
            "mushak": True,
            "chip": STATE_CHIPS.get(self.state, (self.state or "").upper()),
            "watermark": "DRAFT" if self.state == "draft" else "",
            "company": self._fix_doc_company_block(),
            "bill_to": party,
            "meta": meta,
            "service_item": self.service_item or "",
            "delivery_address": self.delivery_address or "",
            "vehicle": self.vehicle_no or "",
            "lines": rows,
            "vat_columns": True,
            "totals": totals,
            "words": _safe_words(self.total_payable),
            "notes": notes,
            "policy": UNCLAIMED_POLICY,
            "sign": [
                "Received in good condition by (Customer)",
                "Prepared by",
                "Authorised Signature & Company Seal",
            ],
        }


class FixSalesProformaPrint(models.Model):
    _name = "fix.sales.proforma"
    _inherit = ["fix.sales.proforma", "fix.doc.print.mixin"]

    def _fix_print_payload(self):
        self.ensure_one()
        vat = self._fix_line_vat()
        share = {line.id: float(s) for line, s in self._fix_allocated()}
        lines = self.line_ids.sorted(lambda r: (r.sequence, r.id))

        def vat_of(line):
            rate, amount = vat.get(line.id, (None, 0.0))
            return rate, amount

        rows = self._fix_doc_line_rows(lines, vat_of=vat_of)
        # the amount column shows the line after its share of the overall discount
        priced = [r for r in rows if "sl" in r]
        for row, line in zip(priced, self._fix_doc_lines(), strict=False):
            if share.get(line.id):
                net = (line.subtotal or 0.0) - share[line.id]
                row["amount"] = fmt_money(net)
                row["disc"] = fmt_money((line.discount_amount or 0.0) + share[line.id])
                row["total"] = fmt_money(net + vat.get(line.id, (0, 0.0))[1])
        meta = [
            ("Proforma No.", self.name if self.name and self.name != "New" else "(draft)"),
            ("Date", fmt_date(self.date)),
            ("Valid Until", fmt_date(self.valid_until)),
        ]
        if self.quotation_id:
            meta.append(("Quotation Ref.", self.quotation_id.name))
        if self.customer_po_ref:
            meta.append(("Customer PO / Ref", self.customer_po_ref))
        if self.payment_term_id:
            meta.append(("Payment Terms", self.payment_term_id.name))
        if self.salesperson_id:
            meta.append(("Sales Person", self.salesperson_id.name))
        totals = [
            (
                "Total Items / Qty",
                "%s / %s" % (len(priced), fmt_qty(sum(self._fix_doc_lines().mapped("quantity")))),
                "",
            ),
            ("Subtotal (before discount)", fmt_money(self.gross_total), ""),
        ]
        if self.discount_total:
            totals.append(("Less: Discount", "- " + fmt_money(self.discount_total), ""))
        totals += [
            ("Taxable Value", fmt_money(self.taxable_amount), ""),
            ("VAT", fmt_money(self.vat_amount), ""),
            ("Grand Total (BDT)", fmt_money(self.amount_total), "grand"),
        ]
        if self.advance_amount:
            totals.append(
                (
                    "Advance Payable Now",
                    fmt_money(self.advance_amount),
                    "due",
                    "%g%%" % self.advance_pct,
                )
            )
        notes = [
            "This is a PROFORMA invoice, not a tax invoice: no Mushak 6.3 is issued against it. "
            "The VAT tax invoice is issued on supply / on receipt of payment.",
        ]
        if self.payment_method_ids:
            notes.append(
                "Payment accepted by: %s." % ", ".join(self.payment_method_ids.mapped("name"))
            )
        for label, text in (
            ("Delivery", self.delivery_terms),
            ("Warranty", self.warranty_terms),
            ("Terms", self.terms),
            ("Remarks", self.remarks),
        ):
            if text:
                notes.append("%s: %s" % (label, text))
        return {
            "title": "PROFORMA INVOICE",
            "mushak": False,
            "chip": STATE_CHIPS.get(self.state, (self.state or "").upper()),
            "watermark": "PROFORMA",
            "company": self._fix_doc_company_block(),
            "bill_to": self._fix_doc_party(),
            "meta": meta,
            "service_item": self.service_item or "",
            "delivery_address": self.delivery_address or "",
            "vehicle": "",
            "lines": rows,
            "vat_columns": True,
            "totals": totals,
            "words": _safe_words(self.amount_total),
            "notes": notes,
            "policy": "",
            "sign": [
                "Accepted by (Customer) — name, signature & date",
                "Prepared by",
                "Authorised Signature & Company Seal",
            ],
        }


def _quotation_payload(self):
    self.ensure_one()
    types = dict(self._fields["quote_type"].selection)
    meta = [
        ("Quotation No.", self.name or "(draft)"),
        ("Version", str(self.version or 1)),
        ("Date", fmt_date(self.create_date)),
    ]
    if self.valid_until:
        meta.append(("Valid Until", fmt_date(self.valid_until)))
    meta.append(("Type", types.get(self.quote_type, self.quote_type or "")))
    if self.estimate_id:
        meta.append(("Estimate Ref.", self.estimate_id.display_name))
    if self.customer_po_ref:
        meta.append(("Customer PO / Ref", self.customer_po_ref))
    if self.salesperson_id:
        meta.append(("Sales Person", self.salesperson_id.name))
    if self.operating_unit_id:
        meta.append(("Unit", self.operating_unit_id.name))
    return {
        "title": "QUOTATION",
        "mushak": False,
        "chip": STATE_CHIPS.get(self.state, (self.state or "").upper()),
        "watermark": "",
        "company": self._fix_doc_company_block(),
        "bill_to": self._fix_doc_party(),
        "meta": meta,
        "service_item": self.service_item or "",
        "delivery_address": self.delivery_address or "",
        "vehicle": "",
        "lines": self._fix_print_lines(),
        "vat_columns": False,
        "totals": self._fix_print_totals(),
        "words": _safe_words(self.amount_total),
        "notes": [],
        "policy": "",
        "sign": [
            "Accepted by (Customer) — name, signature & date",
            "For 1000FiX Services Ltd. — Authorised Signature",
        ],
    }


def _estimate_payload(self):
    self.ensure_one()
    order = self.order_id
    meta = [
        ("Estimate Ref.", order.name if order else "EST-%s" % self.id),
        ("Version", str(self.version or 1)),
        ("Date", fmt_date(self.create_date)),
    ]
    if self.expiry_date:
        meta.append(("Valid Until", fmt_date(self.expiry_date)))
    if order and "device_id" in order._fields and order.device_id:
        meta.append(("Device", order.device_id.display_name))
    if order and "device_serial" in order._fields and order.device_serial:
        meta.append(("Serial", order.device_serial))
    if self.salesperson_id:
        meta.append(("Prepared By", self.salesperson_id.name))
    notes = []
    if self.diagnostic_notes:
        notes.append("Diagnosis: %s" % self.diagnostic_notes)
    notes += [
        "Repair starts after your written approval. Additional faults found during repair are "
        "quoted separately before work proceeds.",
        "Replaced parts carry the standard 1000FiX service warranty; physical and liquid damage "
        "are excluded.",
    ]
    return {
        "title": "REPAIR / SERVICE ESTIMATE",
        "mushak": False,
        "chip": STATE_CHIPS.get(self.state, (self.state or "").upper()),
        "watermark": "",
        "company": self._fix_doc_company_block(),
        "bill_to": self._fix_doc_party(),
        "meta": meta,
        "service_item": self.service_item or "",
        "delivery_address": self.delivery_address or "",
        "vehicle": "",
        "lines": self._fix_print_lines(),
        "vat_columns": False,
        "totals": self._fix_print_totals(),
        "words": _safe_words(self.grand_total),
        "notes": notes,
        "policy": UNCLAIMED_POLICY,
        "sign": [
            "Customer Approval — signature & date",
            "For 1000FiX Services Ltd. — Service Manager",
        ],
    }


class FixQuotationPrint(models.Model):
    _name = "fix.quotation"
    _inherit = ["fix.quotation", "fix.doc.print.mixin"]

    _fix_print_payload = _quotation_payload

    def _fix_print_lines(self):
        """The firm lines (sections and notes kept in place) in the shared shape."""
        self.ensure_one()
        firm = self.line_ids.filtered(lambda r: not r.is_optional).sorted(
            lambda r: (r.sequence, r.id)
        )
        return self._fix_doc_line_rows(firm)

    def _fix_print_totals(self):
        self.ensure_one()
        firm = self._scope_lines()
        gross = sum((ln.quantity or 0.0) * (ln.unit_price or 0.0) for ln in firm)
        line_disc = (
            sum(firm.mapped("discount_amount")) if "discount_amount" in firm._fields else 0.0
        )
        totals = [
            (
                "Total Items / Qty",
                "%s / %s" % (len(firm), fmt_qty(sum(firm.mapped("quantity")))),
                "",
            ),
            ("Subtotal (before discount)", fmt_money(gross if firm else self.value), ""),
        ]
        discount = (line_disc or 0.0) + (self.discount_amount or 0.0)
        if discount:
            totals.append(("Less: Discount", "- " + fmt_money(discount), ""))
        totals += [
            ("Amount (excl. VAT)", fmt_money(self.value), ""),
            ("VAT", fmt_money(self.vat_amount), "", "%g%%" % (self.vat_rate or 0.0)),
            ("Total Payable (incl. VAT)", fmt_money(self.amount_total), "grand"),
        ]
        if self.advance_amount:
            totals.append(
                (
                    "Advance with Order",
                    fmt_money(self.advance_amount),
                    "due",
                    "%g%%" % self.advance_pct,
                )
            )
        return totals

    def _fix_print_party(self):
        self.ensure_one()
        return self._fix_doc_party()


class FixEstimatePrint(models.Model):
    _name = "fix.estimate"
    _inherit = ["fix.estimate", "fix.doc.print.mixin"]

    _fix_print_payload = _estimate_payload

    def _fix_print_lines(self):
        self.ensure_one()
        return self._fix_doc_line_rows(self.line_ids.sorted(lambda r: (r.sequence, r.id)))

    def _fix_print_totals(self):
        self.ensure_one()
        lines = self.line_ids
        totals = [
            (
                "Total Items / Qty",
                "%s / %s" % (len(lines), fmt_qty(sum(lines.mapped("quantity")))),
                "",
            ),
        ]
        for label, amount in (
            ("Parts & Products", self.parts_total),
            ("Service & Labour", self.labour_total),
            ("Diagnostic", self.diagnostic_total),
            ("Transport & Other Charges", self.other_total),
        ):
            if amount:
                totals.append((label, fmt_money(amount), ""))
        totals.append(("Subtotal (before discount)", fmt_money(self._chargeable_total()), ""))
        if self.discount:
            totals.append(("Less: Discount", "- " + fmt_money(self.discount), ""))
        totals += [
            (
                "Amount (excl. VAT)",
                fmt_money(self._chargeable_total() - (self.discount or 0.0)),
                "",
            ),
            ("VAT", fmt_money(self.vat_amount), "", "%g%%" % (self.vat_rate or 0.0)),
            ("Grand Total (BDT)", fmt_money(self.grand_total), "grand"),
        ]
        return totals


def _plain_rows(lines, qty_field, sub_of=None):
    """Purchase-side lines in the shared shape. The supplier's lines carry no
    discount, unit or per-line VAT of their own: the code and unit come from
    the product, the discount prints as '—'."""
    rows = []
    for sl, line in enumerate(lines, start=1):
        product = line.product_id
        qty = line[qty_field] or 0.0
        rows.append(
            {
                "sl": sl,
                "code": product.default_code or "",
                "type": sub_of(line) if sub_of else "",
                "description": line.description or product.name or "",
                "serial": "",
                "qty": fmt_qty(qty),
                "uom": product.uom_id.name if product and product.uom_id else "",
                "price": fmt_money(line.unit_price),
                "disc": "",
                "disc_pct": "",
                "gross": fmt_money(line.line_total),
                "amount": fmt_money(line.line_total),
                "vat_rate": "",
                "vat": "",
                "total": fmt_money(line.line_total),
            }
        )
    return rows


def _vendor_block(partner):
    """The supplier, printed where a customer document prints Bill To."""
    if not partner:
        return {"name": "", "code": "", "address": "", "phone": "", "email": "", "bin": ""}
    address = ", ".join(
        x
        for x in (
            partner.street,
            partner.street2,
            " ".join(y for y in (partner.city, partner.zip) if y),
            partner.country_id.name if partner.country_id else "",
        )
        if x
    )
    return {
        "name": partner.name or "",
        "code": getattr(partner, "legacy_reference", "") or partner.ref or "",
        "address": address,
        "phone": partner.phone or "",
        "email": partner.email or "",
        "bin": partner.vat or "",
        "category": "",
    }


PO_STATES = {
    "draft": "DRAFT",
    "sent": "SENT",
    "acknowledged": "ACKNOWLEDGED",
    "partially_received": "PARTIALLY RECEIVED",
    "received": "RECEIVED",
    "closed": "CLOSED",
    "cancelled": "CANCELLED",
    "superseded": "SUPERSEDED",
}
BILL_STATES = {
    "draft": "DRAFT",
    "to_approve": "TO APPROVE",
    "approved": "APPROVED",
    "rejected": "REJECTED",
}


class FixPurchaseOrderPrint(models.Model):
    _name = "fix.purchase.order"
    _inherit = ["fix.purchase.order", "fix.doc.print.mixin"]

    def _fix_print_payload(self):
        self.ensure_one()
        lines = self.line_ids.sorted("id")

        def received(line):
            if line.qty_received or line.qty_accepted:
                return "Received %s / %s" % (fmt_qty(line.qty_received), fmt_qty(line.qty_ordered))
            return ""

        number = self.name or "(draft)"
        if (self.revision or 0) > 1:
            number += " · Rev %s" % self.revision
        meta = [("PO No.", number), ("Order Date", fmt_date(self.date_order))]
        if self.promised_date:
            meta.append(("Expected Delivery", fmt_date(self.promised_date)))
        if self.branch_id:
            meta.append(("Deliver To", self.branch_id.name))
        if self.requisition_id:
            meta.append(("Requisition", self.requisition_id.display_name))
        if self.buyer_id:
            meta.append(("Buyer", self.buyer_id.name))
        if "is_capex" in self._fields and self.is_capex:
            meta.append(("Type", "CAPEX"))
        total_qty = sum(lines.mapped("qty_ordered"))
        totals = [
            ("Total Items / Qty", "%s / %s" % (len(lines), fmt_qty(total_qty)), ""),
            ("Order Total (excl. VAT)", fmt_money(self.amount_total), "grand"),
        ]
        notes = [
            "Prices exclude VAT. The supplier's Mushak-6.3 tax invoice states VAT separately; "
            "input VAT and VDS are settled on the vendor bill.",
            "Delivery to the branch above by the expected date; partial deliveries must be "
            "pre-agreed.",
            "Goods supplied against manufacturer/part warranty; warranty defects are returnable "
            "at supplier cost.",
            "Invoices must quote this PO number and the supplier BIN / Mushak-6.3 reference; "
            "payment is processed per agreed credit terms after 3-way match.",
        ]
        if self.vendor_confirmed_date:
            notes.append("Vendor confirmed: %s." % fmt_date(self.vendor_confirmed_date))
        return {
            "title": "PURCHASE ORDER",
            "mushak": False,
            "chip": PO_STATES.get(self.state, (self.state or "").upper()),
            "watermark": "DRAFT" if self.state == "draft" else "",
            "company": self._fix_doc_company_block(),
            "company_bin_label": "Buyer BIN",
            "party_label": "Supplier",
            "party_bin_label": "Supplier BIN",
            "bill_to": _vendor_block(self.vendor_id),
            "meta": meta,
            "service_item": "",
            "delivery_address": "",
            "vehicle": "",
            "lines": _plain_rows(lines, "qty_ordered", received),
            "vat_columns": False,
            "totals": totals,
            "words": _safe_words(self.amount_total),
            "notes": notes,
            "no_payable_line": True,
            "policy": "",
            "sign": [
                "Prepared by (Procurement)",
                "Approved by — Authorised Signature",
                "Supplier Acceptance — signature, seal & date",
            ],
        }


class FixVendorInvoicePrint(models.Model):
    _name = "fix.vendor.invoice"
    _inherit = ["fix.vendor.invoice", "fix.doc.print.mixin"]

    def _fix_print_payload(self):
        self.ensure_one()
        lines = self.line_ids.sorted("id")
        cur = self.currency_id

        def tds(line):
            if not line.tds_amount:
                return ""
            multiplier = line.tds_multiplier or 1.0
            return "TDS %s @ %g%%%s: %s" % (
                line.tds_section or "",
                line.tds_rate or 0.0,
                (" × %g (non-filer)" % multiplier) if multiplier != 1.0 else "",
                fmt_money(line.tds_amount),
            )

        bill_types = {"po": "PO-based", "non_po": "Non-PO"}
        matches = {
            "unmatched": "Unmatched",
            "matched": "Matched",
            "blocked": "Blocked",
            "not_required": "Not Required",
        }
        meta = [
            ("Bill No.", self.invoice_ref or "(draft)"),
            ("Bill Date", fmt_date(self.invoice_date)),
        ]
        if self.due_date:
            meta.append(("Due Date", fmt_date(self.due_date)))
        if self.supplier_mushak_no:
            meta.append(("Supplier Mushak 6.3 No.", self.supplier_mushak_no))
        meta.append(("Type", bill_types.get(self.bill_type, self.bill_type or "")))
        if self.requisition_id:
            meta.append(("PO", self.requisition_id.display_name))
        meta.append(("3-Way Match", matches.get(self.match_state, self.match_state or "")))
        if self.payment_term_days:
            meta.append(("Payment Terms", "%s days" % self.payment_term_days))
        totals = [
            (
                "Total Items / Qty",
                "%s / %s" % (len(lines), fmt_qty(sum(lines.mapped("quantity")))),
                "",
            ),
            ("Subtotal (excl. VAT)", fmt_money(self.subtotal), ""),
            ("Input VAT (Mushak-6.3)", fmt_money(self.vat_amount), ""),
            ("Gross Amount (incl. VAT)", fmt_money(self.gross_amount), ""),
        ]
        if self.vds_amount:
            totals.append(("Less: VDS withheld", "- " + fmt_money(self.vds_amount), ""))
        if self.tds_amount:
            totals.append(("Less: TDS withheld", "- " + fmt_money(self.tds_amount), ""))
        if self.advance_applied:
            totals.append(("Less: Advance adjusted", "- " + fmt_money(self.advance_applied), ""))
        totals.append(
            ("Net Payable (%s)" % (cur.name or "BDT"), fmt_money(self.total_payable), "grand")
        )
        return {
            "title": "VENDOR BILL",
            "mushak": False,
            "chip": BILL_STATES.get(self.approval_state, (self.approval_state or "").upper()),
            "watermark": "",
            "company": self._fix_doc_company_block(),
            "company_bin_label": "Buyer BIN",
            "party_label": "Supplier",
            "party_bin_label": "Supplier BIN",
            "bill_to": _vendor_block(self.vendor_id),
            "meta": meta,
            "service_item": "",
            "delivery_address": "",
            "vehicle": "",
            "lines": _plain_rows(lines, "quantity", tds),
            "vat_columns": False,
            "totals": totals,
            "words": _safe_words(self.total_payable),
            "notes": [
                "Payment is scheduled per the agreed credit terms after three-way match and "
                "approval. VAT is deducted at source (VDS, Mushak-6.6) and TDS is withheld per "
                "the Income Tax Act 2023; the withholding certificates are issued to the supplier.",
            ],
            "no_payable_line": True,
            "policy": "",
            "sign": ["Submitted by (AP Clerk)", "Checked by", "Approved by (Finance)"],
        }


# The PDFs of each document: (A4, 80 mm receipt or None).
PRINT_REPORTS = {
    "fix.purchase.order": ("cd_doc_suite.report_po", None),
    "fix.vendor.invoice": ("cd_doc_suite.report_vendor_bill", None),
    "fix.ar.invoice": ("cd_doc_suite.report_invoice", "cd_doc_suite.report_invoice_receipt"),
    "fix.sales.proforma": (
        "cd_doc_suite.report_sales_proforma",
        "cd_doc_suite.report_sales_proforma_receipt",
    ),
    "fix.quotation": ("cd_doc_suite.report_quotation", "cd_doc_suite.report_quotation_receipt"),
    "fix.estimate": ("cd_doc_suite.report_estimate", "cd_doc_suite.report_estimate_receipt"),
}


class FixDocPrintActions(models.AbstractModel):
    """Print as a served workspace action: the server checks the user may
    read the record and answers the PDF's URL, which the workspace opens."""

    _inherit = "fix.doc.print.mixin"

    def _fix_print_url(self, receipt=False):
        self.ensure_one()
        self.check_access("read")
        names = PRINT_REPORTS.get(self._name)
        name = names and names[1 if receipt else 0]
        if not name:
            return {}
        return {"print_url": "/report/pdf/%s/%s" % (name, self.id)}

    def action_fix_print(self):
        return self._fix_print_url()

    def action_fix_print_receipt(self):
        return self._fix_print_url(receipt=True)
