# Customer commercial documents on one standard (17 Nov 2026).
#
# * The quotation gets the document header standard (customer category,
#   bill-to, buyer BIN, sales person, service item, delivery address...).
# * The customer LOCAL PROFORMA INVOICE, which did not exist: the only
#   "proforma" was a print of a draft AR invoice, and the M16 / M44 proformas
#   are suppliers'. A proforma is a priced offer to pay (advance, LC, a
#   corporate's purchase approval). It is not a tax invoice: it draws no
#   Mushak 6.3 number and posts nothing. It is built from a quotation, an
#   estimate or by hand, with the same lines as every other document, and
#   it converts into the draft tax invoice once the customer commits.
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal
from types import SimpleNamespace

from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models.fix_billing_engine import allocate_discount
from odoo.addons.cd_catalogue.models.fix_commercial_line import LINE_TYPES
from odoo.exceptions import UserError, ValidationError

# Load order: the models this file extends are defined first (Odoo registers
# a module's model classes in definition order).
from . import fix_quote_ops, fix_quote_scope  # noqa: F401

TWO = Decimal("0.01")
PROFORMA_STATES = [
    ("draft", "Draft"),
    ("issued", "Issued to Customer"),
    ("converted", "Converted to Invoice"),
    ("cancelled", "Cancelled"),
]
DEFAULT_VALIDITY_DAYS = 15


class FixQuotationDocument(models.Model):
    _name = "fix.quotation"
    _inherit = ["fix.quotation", "fix.commercial.document.mixin"]

    proforma_ids = fields.One2many("fix.sales.proforma", "quotation_id", string="Proformas")

    @api.depends("customer_id")
    def _compute_customer_category(self):
        return super()._compute_customer_category()

    def _fix_doc_partner(self):
        return self.customer_id

    def _fix_doc_lines(self):
        return self._scope_lines().sorted(lambda r: (r.sequence, r.id))

    def action_create_proforma(self):
        """A proforma invoice of the quotation's firm lines and terms."""
        self.ensure_one()
        if self.state in ("declined", "expired", "cancelled", "superseded"):
            raise UserError("Quotation %s is %s: no proforma is raised." % (self.name, self.state))
        Proforma = self.env["fix.sales.proforma"]
        proforma = Proforma.create(Proforma._vals_from_quotation(self))
        return proforma._fix_open_action()


class FixEstimateProforma(models.Model):
    _inherit = "fix.estimate"

    proforma_ids = fields.One2many("fix.sales.proforma", "estimate_id", string="Proformas")

    def action_create_proforma(self):
        """A proforma invoice of the estimate (e.g. a deposit before parts are
        ordered). Only an estimate the customer may still accept is billed."""
        self.ensure_one()
        if self.state in ("rejected", "expired"):
            raise UserError("Estimate %s is %s: no proforma is raised." % (self.name, self.state))
        Proforma = self.env["fix.sales.proforma"]
        proforma = Proforma.create(Proforma._vals_from_estimate(self))
        return proforma._fix_open_action()


class FixSalesProforma(models.Model):
    _name = "fix.sales.proforma"
    _description = "Proforma Invoice (Local Customer)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.commercial.document.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(string="Proforma No.", default="New", readonly=True, copy=False, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
        default=lambda self: self.env.user.default_operating_unit_id
        if "default_operating_unit_id" in self.env.user._fields
        else False,
    )
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True, ondelete="restrict"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    date = fields.Date(string="Proforma Date", required=True, default=fields.Date.context_today)
    valid_until = fields.Date(
        default=lambda self: fields.Date.context_today(self) + timedelta(days=DEFAULT_VALIDITY_DAYS)
    )
    state = fields.Selection(PROFORMA_STATES, default="draft", required=True, tracking=True)
    quotation_id = fields.Many2one("fix.quotation", string="From Quotation", index=True)
    estimate_id = fields.Many2one("fix.estimate", string="From Estimate", index=True)
    line_ids = fields.One2many("fix.sales.proforma.line", "proforma_id", string="Lines", copy=True)
    overall_discount = fields.Monetary(
        string="Overall Discount (BDT)",
        currency_field="currency_id",
        help="A discount on the whole proforma, spread over the lines before VAT.",
    )
    gross_total = fields.Monetary(
        string="Amount before Discount",
        currency_field="currency_id",
        compute="_compute_totals",
        store=True,
    )
    discount_total = fields.Monetary(
        string="Total Discount", currency_field="currency_id", compute="_compute_totals", store=True
    )
    taxable_amount = fields.Monetary(
        string="Taxable Value", currency_field="currency_id", compute="_compute_totals", store=True
    )
    vat_amount = fields.Monetary(
        string="VAT", currency_field="currency_id", compute="_compute_totals", store=True
    )
    amount_total = fields.Monetary(
        string="Grand Total", currency_field="currency_id", compute="_compute_totals", store=True
    )
    advance_pct = fields.Float(string="Advance Required (%)")
    advance_amount = fields.Monetary(
        string="Advance Required (BDT)",
        currency_field="currency_id",
        compute="_compute_totals",
        store=True,
    )
    payment_term_id = fields.Many2one("account.payment.term", string="Payment Terms")
    payment_method_ids = fields.Many2many(
        "fix.payment.method",
        "fix_sales_proforma_payment_method_rel",
        "proforma_id",
        "method_id",
        string="Payment Methods Accepted",
    )
    delivery_terms = fields.Text()
    warranty_terms = fields.Text()
    terms = fields.Text(string="Terms & Conditions")
    invoice_id = fields.Many2one("fix.ar.invoice", string="Tax Invoice", readonly=True, copy=False)
    issued_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    issued_at = fields.Datetime(readonly=True, copy=False)
    cancel_reason = fields.Char(readonly=True, copy=False)

    LOCKED_WHEN_ISSUED = (
        "customer_id",
        "line_ids",
        "overall_discount",
        "date",
        "currency_id",
        "customer_category",
        "bill_to_name",
        "bill_to_address",
        "customer_bin",
    )

    # ---- document hooks ---------------------------------------------------
    @api.depends("customer_id")
    def _compute_customer_category(self):
        return super()._compute_customer_category()

    def _fix_doc_partner(self):
        return self.customer_id

    def _fix_doc_lines(self):
        return self.line_ids.filtered(lambda r: not r.display_type).sorted(
            lambda r: (r.sequence, r.id)
        )

    # ---- money --------------------------------------------------------------
    def _fix_allocated(self):
        """[(line, overall discount share)] for the priced lines."""
        self.ensure_one()
        lines = self._fix_doc_lines()
        nets = [Decimal(str(ln.subtotal or 0.0)).quantize(TWO, ROUND_HALF_UP) for ln in lines]
        overall = Decimal(str(self.overall_discount or 0.0)).quantize(TWO, ROUND_HALF_UP)
        if not lines:
            return []
        if overall > sum(nets, Decimal("0")):
            overall = sum(nets, Decimal("0"))
        return list(zip(lines, allocate_discount(nets, overall), strict=True))

    def _fix_determination(self):
        """M51's VAT on each line (qty x price less its discount and its share
        of the overall discount), exactly as the tax invoice will state it."""
        self.ensure_one()
        Line = self.env["fix.ar.invoice.line"].sudo()
        frame = SimpleNamespace(
            invoice_date=self.date or fields.Date.context_today(self),
            company_id=self.company_id or self.env.company,
        )
        out = []
        for line, share in self._fix_allocated():
            disc = Decimal(str(line.discount_amount or 0.0)) + share
            det = Line._fix_determined(
                frame,
                0.0,
                line.product_id,
                self.env["fix.vat.treatment"],
                qty=line.quantity or 0.0,
                unit_price=line.unit_price or 0.0,
                discount=float(disc),
            )
            out.append((line, float(disc), det))
        return out

    @api.depends(
        "line_ids.subtotal",
        "line_ids.gross_amount",
        "line_ids.discount_amount",
        "line_ids.product_id",
        "line_ids.display_type",
        "overall_discount",
        "advance_pct",
        "date",
    )
    def _compute_totals(self):
        for rec in self:
            lines = rec._fix_doc_lines()
            rec.gross_total = sum(lines.mapped("gross_amount"))
            taxable = vat = 0.0
            try:
                determined = rec._fix_determination() if lines else []
            except UserError:
                determined = []
            if determined:
                taxable = sum(float(det.taxable_amount) for _l, _d, det in determined)
                vat = sum(float(det.vat_amount) for _l, _d, det in determined)
            else:
                taxable = max(sum(lines.mapped("subtotal")) - (rec.overall_discount or 0.0), 0.0)
            rec.taxable_amount = round(taxable, 2)
            rec.vat_amount = round(vat, 2)
            rec.discount_total = round(rec.gross_total - rec.taxable_amount, 2)
            rec.amount_total = round(rec.taxable_amount + rec.vat_amount, 2)
            rec.advance_amount = round(rec.amount_total * (rec.advance_pct or 0.0) / 100.0, 2)

    def _fix_line_vat(self):
        """{line id: (rate, vat)} for printing."""
        self.ensure_one()
        try:
            return {
                line.id: (float(det.rate), float(det.vat_amount))
                for line, _d, det in self._fix_determination()
            }
        except UserError:
            return {}

    @api.constrains("overall_discount", "advance_pct", "line_ids")
    def _check_amounts(self):
        for rec in self:
            if (rec.overall_discount or 0.0) < 0:
                raise ValidationError("An overall discount cannot be negative.")
            subtotal = sum(rec._fix_doc_lines().mapped("subtotal"))
            if rec.line_ids and (rec.overall_discount or 0.0) > subtotal + 0.005:
                raise ValidationError(
                    "The overall discount (%.2f) cannot exceed the lines (%.2f)."
                    % (rec.overall_discount, subtotal)
                )
            if not 0.0 <= (rec.advance_pct or 0.0) <= 100.0:
                raise ValidationError("An advance is between 0 and 100% of the total.")

    # ---- lifecycle ----------------------------------------------------------
    def write(self, vals):
        if not self.env.su:
            touched = set(self.LOCKED_WHEN_ISSUED) & set(vals)
            frozen = self.filtered(lambda r: r.state != "draft")
            if touched and frozen:
                raise UserError(
                    "Proforma %s is %s: its lines and customer are frozen. Cancel it and raise "
                    "a new one." % (frozen[0].name, frozen[0].state)
                )
        return super().write(vals)

    def unlink(self):
        if self.filtered(lambda r: r.state != "draft"):
            raise UserError("Only a draft proforma is deleted; cancel an issued one.")
        return super().unlink()

    def action_issue(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Proforma %s is already %s." % (rec.name, rec.state))
            if not rec._fix_doc_lines():
                raise UserError("Add at least one line before issuing the proforma.")
            problems = rec._fix_doc_problems()
            if problems:
                raise UserError("The proforma cannot be issued yet:\n- " + "\n- ".join(problems))
            if hasattr(rec.customer_id, "_fix_assert_party_usable_downstream"):
                rec.customer_id._fix_assert_party_usable_downstream("a proforma invoice")
            name = rec.name
            if not name or name == "New":
                name = self.env["ir.sequence"].next_by_code("fix.sales.proforma") or "New"
            rec.sudo().write(
                {
                    "name": name,
                    "state": "issued",
                    "issued_by_id": self.env.uid,
                    "issued_at": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self, reason=None):
        for rec in self:
            if rec.state == "converted":
                raise UserError(
                    "Proforma %s became invoice %s; correct the invoice with a credit note."
                    % (rec.name, rec.invoice_id.display_name)
                )
            rec.sudo().write({"state": "cancelled", "cancel_reason": (reason or "")[:250]})
        return True

    def action_reset_draft(self):
        for rec in self.filtered(lambda r: r.state == "cancelled"):
            rec.sudo().write({"state": "draft"})
        return True

    def action_convert_to_invoice(self):
        """The draft tax invoice of the proforma: same customer, header and
        lines; the Mushak 6.3 number is drawn when Finance issues it."""
        self.ensure_one()
        if self.invoice_id:
            # idempotent: a second press opens the invoice it already became
            return self.invoice_id
        if self.state != "issued":
            raise UserError("Issue the proforma to the customer before invoicing it.")
        Invoice = self.env["fix.ar.invoice"]
        Invoice.check_access("create")
        header = {
            "customer_id": self.customer_id.id,
            "company_id": self.company_id.id,
            "operating_unit_id": (self.operating_unit_id or self._fix_default_ou()).id,
            "currency_id": self.currency_id.id,
        }
        for key in (
            "customer_category",
            "bill_to_name",
            "bill_to_phone",
            "bill_to_address",
            "customer_bin",
            "customer_po_ref",
            "customer_po_date",
            "delivery_address",
            "service_item",
            "remarks",
        ):
            if self[key]:
                header[key] = self[key]
        if self.salesperson_id:
            header["salesperson_id"] = self.salesperson_id.id
        lines = [line._fix_invoice_line_vals() for line in self._fix_doc_lines()]
        invoice = Invoice.create_manual_invoice(
            header,
            lines,
            "Proforma %s accepted by the customer" % self.name,
            overall_discount=self.overall_discount or 0.0,
            source=self,
        )
        self.sudo().write({"invoice_id": invoice.id, "state": "converted"})
        self.message_post(body="Converted to draft tax invoice (id %s)." % invoice.id)
        return invoice

    def _fix_default_ou(self):
        OU = self.env["operating.unit"]
        return self.env.user.default_operating_unit_id or OU.search(
            [("company_id", "=", self.company_id.id)], limit=1
        )

    def _fix_open_action(self):
        """The new proforma: the back-office form, and the workspace's note."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "note": "Draft proforma for %s, BDT %s incl. VAT: review it on Proforma Invoices "
            "(Local), then Issue to Customer."
            % (self.customer_id.name, format(self.amount_total, ",.2f")),
        }

    # ---- sources ------------------------------------------------------------
    @api.model
    def _vals_from_quotation(self, quote):
        lines = []
        for seq, ln in enumerate(quote._fix_doc_lines(), start=1):
            lines.append(
                (
                    0,
                    0,
                    {
                        "sequence": seq * 10,
                        "line_type": ln.line_type,
                        "product_id": ln.product_id.id or False,
                        "description": ln.description,
                        "uom_id": ln.uom_id.id or False,
                        "serial_ref": ln.serial_ref or False,
                        "quantity": ln.quantity,
                        "unit_price": ln.unit_price,
                        "discount_pct": ln.discount_pct,
                    },
                )
            )
        vals = {
            "customer_id": quote.customer_id.id,
            "company_id": quote.company_id.id,
            "operating_unit_id": quote.operating_unit_id.id or False,
            "quotation_id": quote.id,
            "estimate_id": quote.estimate_id.id or False,
            "currency_id": quote.currency_id.id,
            "overall_discount": quote.discount_amount or 0.0,
            "advance_pct": quote.advance_pct or 0.0,
            "payment_term_id": quote.payment_term_id.id or False,
            "payment_method_ids": [(6, 0, quote.payment_method_ids.ids)],
            "delivery_terms": quote.delivery_terms or False,
            "warranty_terms": quote.warranty_terms or False,
            "line_ids": lines,
        }
        for key in (
            "customer_category",
            "bill_to_name",
            "bill_to_phone",
            "bill_to_address",
            "customer_bin",
            "customer_po_ref",
            "customer_po_date",
            "delivery_address",
            "service_item",
        ):
            if quote[key]:
                vals[key] = quote[key]
        return vals

    @api.model
    def _vals_from_estimate(self, estimate):
        customer = estimate._fix_doc_partner()
        if not customer:
            raise UserError("Estimate %s has no customer to bill." % estimate.display_name)
        lines = [
            (
                0,
                0,
                {
                    "sequence": seq * 10,
                    "line_type": ln.line_type,
                    "product_id": ln.product_id.id or False,
                    "description": ln.description,
                    "uom_id": ln.uom_id.id or False,
                    "serial_ref": ln.serial_ref or False,
                    "quantity": ln.quantity,
                    "unit_price": ln.unit_price,
                },
            )
            for seq, ln in enumerate(estimate.line_ids.sorted(lambda r: (r.sequence, r.id)), 1)
        ]
        vals = {
            "customer_id": customer.id,
            "company_id": estimate.company_id.id,
            "operating_unit_id": estimate.operating_unit_id.id or False,
            "estimate_id": estimate.id,
            "currency_id": estimate.currency_id.id,
            "overall_discount": estimate.discount or 0.0,
            "line_ids": lines,
        }
        for key in ("customer_category", "bill_to_name", "bill_to_phone", "service_item"):
            if estimate[key]:
                vals[key] = estimate[key]
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        Partner = self.env["res.partner"]
        for vals in vals_list:
            partner = Partner.browse(vals.get("customer_id")).exists()
            if partner and not vals.get("customer_bin") and partner.vat:
                vals["customer_bin"] = partner.vat
        return super().create(vals_list)


class FixSalesProformaLine(models.Model):
    _name = "fix.sales.proforma.line"
    _description = "Proforma Invoice Line"
    _inherit = ["fix.commercial.line.mixin"]
    _order = "proforma_id, sequence, id"

    proforma_id = fields.Many2one(
        "fix.sales.proforma", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="proforma_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="proforma_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="proforma_id.currency_id")
    sequence = fields.Integer(default=10)
    display_type = fields.Selection([("line_section", "Section"), ("line_note", "Note")])
    line_type = fields.Selection(LINE_TYPES, string="Type", default="part")
    product_id = fields.Many2one("product.product", string="Item / Charge Code")
    description = fields.Char(required=True)
    quantity = fields.Float(default=1.0, digits="Product Unit of Measure")
    unit_price = fields.Monetary(string="Unit Price (excl. VAT)", currency_field="currency_id")
    discount_pct = fields.Float(string="Discount (%)")
    gross_amount = fields.Monetary(
        string="Amount before Discount",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
    )
    discount_amount = fields.Monetary(
        string="Discount", currency_field="currency_id", compute="_compute_amounts", store=True
    )
    subtotal = fields.Monetary(
        string="Amount (excl. VAT)",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
    )

    @api.depends("quantity", "unit_price", "discount_pct", "display_type")
    def _compute_amounts(self):
        for line in self:
            if line.display_type:
                line.gross_amount = line.discount_amount = line.subtotal = 0.0
                continue
            gross = round((line.quantity or 0.0) * (line.unit_price or 0.0), 2)
            disc = round(gross * (line.discount_pct or 0.0) / 100.0, 2)
            line.gross_amount = gross
            line.discount_amount = disc
            line.subtotal = gross - disc

    @api.constrains("quantity", "unit_price", "discount_pct")
    def _check_numbers(self):
        for line in self.filtered(lambda r: not r.display_type):
            if (line.quantity or 0.0) < 0 or (line.unit_price or 0.0) < 0:
                raise ValidationError(
                    "Proforma line '%s' cannot have a negative quantity or price."
                    % line.description
                )
            if not 0.0 <= (line.discount_pct or 0.0) <= 100.0:
                raise ValidationError("A line discount is between 0 and 100%.")

    def _fix_assert_draft(self, proformas):
        if self.env.su:
            return
        frozen = proformas.filtered(lambda r: r.state != "draft")
        if frozen:
            raise UserError(
                "Proforma %s is %s: its lines are frozen." % (frozen[0].name, frozen[0].state)
            )

    @api.model_create_multi
    def create(self, vals_list):
        self._fix_assert_draft(
            self.env["fix.sales.proforma"].browse(
                {v.get("proforma_id") for v in vals_list} - {None, False}
            )
        )
        vals_list = [self._fix_commercial_prepare(dict(v)) for v in vals_list]
        Product = self.env["product.product"]
        for vals in vals_list:
            if vals.get("display_type"):
                vals.update({"quantity": 0.0, "unit_price": 0.0, "discount_pct": 0.0})
                continue
            product = Product.browse(vals.get("product_id")).exists()
            if product and not vals.get("description"):
                vals["description"] = product.name
            if product and vals.get("unit_price") in (None, False, ""):
                vals["unit_price"] = product.lst_price
        lines = super().create(vals_list)
        for line in lines.filtered("product_id"):
            if hasattr(line.product_id, "_fix_check_sale") and not self.env.su:
                line.product_id._fix_check_sale(
                    unit_price=line.unit_price or 0.0, channel="proforma"
                )
        return lines

    def write(self, vals):
        self._fix_assert_draft(self.proforma_id)
        return super().write(vals)

    def unlink(self):
        self._fix_assert_draft(self.proforma_id)
        return super().unlink()

    def _fix_invoice_line_vals(self):
        self.ensure_one()
        return {
            "line_type": self.line_type,
            "product_id": self.product_id.id or False,
            "description": self.description,
            "uom_id": self.uom_id.id or False,
            "serial_ref": self.serial_ref or False,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "discount_pct": self.discount_pct,
            "sequence": self.sequence,
        }
