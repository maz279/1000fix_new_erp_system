# The AR invoice as a professional customer document (17 Nov 2026).
#
# The invoice header said only customer + date; its lines only taxable / VAT.
# It now carries the document header standard (cd_catalogue): the customer
# category (individual, walk-in, cash, corporate, dealer, government) and
# what each must state - the walk-in's name and phone, the buyer's BIN, the
# customer PO, sales person, service item, challan, delivery address and
# vehicle (Mushak 6.3) - plus the footer the print needs: item count,
# quantity, amount before discount, discount, taxable, VAT, grand total.
from datetime import timedelta

from odoo import api, fields, models
from odoo.addons.cd_catalogue.models.fix_commercial_line import (
    BIN_CATEGORIES,
    CATEGORY_LABELS,
    PAY_NOW_CATEGORIES,
)
from odoo.exceptions import UserError

from .fix_billing_engine import FixArInvoice

# Invoices typed by a person (the manual path, a converted proforma): their
# header is checked against the customer category before issue.
DOCUMENT_SOURCES = ("manual", "fix.sales.proforma")

# Printed on the Mushak 6.3: frozen with it once the invoice is issued.
HEADER_LOCKED = (
    "customer_category",
    "bill_to_name",
    "bill_to_phone",
    "bill_to_address",
    "customer_bin",
    "customer_po_ref",
    "customer_po_date",
    "delivery_address",
    "vehicle_no",
    "challan_ref",
    "service_item",
    "salesperson_id",
)


class FixArInvoiceDocument(models.Model):
    _name = "fix.ar.invoice"
    _inherit = ["fix.ar.invoice", "fix.commercial.document.mixin"]

    INVOICE_LOCKED = FixArInvoice.INVOICE_LOCKED + HEADER_LOCKED

    payment_method_id = fields.Many2one(
        "fix.payment.method",
        string="Payment Method",
        help="How a walk-in / cash customer pays at the point of sale (cash, bKash, card...).",
    )
    item_count = fields.Integer(string="Items", compute="_compute_doc_footer")
    total_quantity = fields.Float(string="Total Quantity", compute="_compute_doc_footer")
    gross_total = fields.Monetary(
        string="Amount before Discount",
        currency_field="currency_id",
        compute="_compute_doc_footer",
    )
    discount_total = fields.Monetary(
        string="Discount", currency_field="currency_id", compute="_compute_doc_footer"
    )
    date_due = fields.Date(
        string="Due Date",
        compute="_compute_date_due",
        help="Walk-in and cash customers pay on the invoice date; others by their payment "
        "terms.",
    )

    @api.depends("customer_id")
    def _compute_customer_category(self):
        return super()._compute_customer_category()

    def _fix_doc_partner(self):
        return self.customer_id

    def _fix_doc_lines(self):
        return self.line_ids.sorted(lambda r: (r.sequence, r.id))

    @api.depends(
        "line_ids.gross_amount", "line_ids.discount_amount", "line_ids.quantity", "line_ids"
    )
    def _compute_doc_footer(self):
        for inv in self:
            lines = inv.line_ids
            inv.item_count = len(lines)
            inv.total_quantity = sum(lines.mapped("quantity"))
            inv.gross_total = sum(lines.mapped("gross_amount"))
            inv.discount_total = sum(lines.mapped("discount_amount"))

    @api.depends("invoice_date", "customer_category", "customer_id")
    def _compute_date_due(self):
        for inv in self:
            if not inv.invoice_date:
                inv.date_due = False
            elif inv.customer_category in PAY_NOW_CATEGORIES:
                inv.date_due = inv.invoice_date
            else:
                days = inv._payment_terms_days() if inv.customer_id else 0
                inv.date_due = inv.invoice_date + timedelta(days=days or 0)

    def _fix_mushak_buyer(self):
        self.ensure_one()
        party = self._fix_doc_party()
        return party["name"], party["bin"]

    @api.model_create_multi
    def create(self, vals_list):
        Partner = self.env["res.partner"]
        for vals in vals_list:
            partner = Partner.browse(vals.get("customer_id")).exists()
            if partner and not vals.get("customer_bin") and partner.vat:
                vals["customer_bin"] = partner.vat
        return super().create(vals_list)

    def _fix_issue_problems(self):
        """What a manual invoice lacks for its customer category; the system
        paths (closed jobs, contracts, storefront) state their own party."""
        problems = []
        for inv in self.filtered(lambda r: r.source_model in DOCUMENT_SOURCES):
            problems += inv._fix_doc_problems()
        return problems

    def action_issue(self):
        problems = self._fix_issue_problems()
        if problems and not self.env.su:
            raise UserError("The invoice cannot be issued yet:\n- " + "\n- ".join(problems))
        return super().action_issue()

    def _fix_category_label(self):
        self.ensure_one()
        return CATEGORY_LABELS.get(self.customer_category or "", "")

    def _fix_print_title(self):
        """The heading the invoice prints under."""
        self.ensure_one()
        # a draft prints the same title under a DRAFT chip and watermark
        if self.customer_category in PAY_NOW_CATEGORIES:
            return "CASH MEMO / TAX INVOICE"
        if self.customer_category in BIN_CATEGORIES:
            return "TAX INVOICE"
        return "SALES / SERVICE INVOICE"
