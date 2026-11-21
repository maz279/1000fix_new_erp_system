# fix_import_ap — the import's side of accounts payable (A06 ERP audit 20 Nov
# 2026: X08 / M44-19, X11, D6 scope, M44-16 / X15).
#
#  - X11: a supplier bill raised against an import with no M16 PO debited the
#    product's expense account while the import receipt had credited GRNI, so
#    GRNI never cleared and the goods were counted twice. A bill that names its
#    import now debits the import's GRNI role, the account the receipt credited.
#  - X08 / M44-19: a cost document (C&F, freight, insurance, bank charge) is
#    capitalised by the final landed cost, which credits the landed-cost
#    accrual (201279). Its bill was expensed in AP as well. A cost document now
#    names the AP bill that pays it; that bill debits the landed-cost accrual
#    (relieving it) instead of an expense, and only when the documents it
#    carries add up to the bill: nothing is expensed and capitalised twice.
#  - D6: an LC remittance made before a no-PO import's bill exists is an
#    advance in the import's scope; the import's bill takes it back.
#  - M44-16 / X15: a paid Bill of Entry's import VAT reaches M51's input-VAT
#    register (Mushak 6.1 side) through the import.duty_paid consumer.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_import_common import FINANCE, import_account, require_group


class FixVendorInvoiceImport(models.Model):
    _inherit = "fix.vendor.invoice"

    # A06 integration: ONE link from a bill to its import. AP (cd_ap_ext, X11)
    # owns the no-PO import bill: bill_type "import" + import_order_ref, its
    # three-way match against the received import and the GRNI clearing at the
    # receipt value. This Many2one is the same fact seen from M44 (stored,
    # searchable: the LC settlement scope and the import's bill list): set it
    # and the bill becomes that import's bill; it follows import_order_ref.
    import_order_id = fields.Many2one(
        "fix.import.order",
        string="Import Order (M44)",
        index=True,
        ondelete="restrict",
        compute="_compute_import_order_id",
        inverse="_inverse_import_order_id",
        store=True,
        readonly=False,
        help="The import this supplier bill is for. With no M16 PO, it is an import bill that "
        "clears the import's GRNI (X11).",
    )
    import_cost_ids = fields.One2many(
        "fix.import.cost", "bill_id", string="Import Cost Documents Billed"
    )

    @api.depends("import_order_ref")
    def _compute_import_order_id(self):
        for bill in self:
            ref = bill.import_order_ref
            if ref and ref._name == "fix.import.order":
                bill.import_order_id = ref.id
            elif not bill.requisition_id:
                bill.import_order_id = False

    def _inverse_import_order_id(self):
        for bill in self:
            order = bill.import_order_id
            if bill.requisition_id:
                continue  # a PO-linked import bill uses the PO's three-way match
            vals = {"import_order_ref": "fix.import.order,%d" % order.id if order else False}
            if order:
                vals["bill_type"] = "import"
            bill.write(vals)

    @api.constrains("import_order_id", "vendor_id", "company_id")
    def _check_import_order(self):
        for bill in self.filtered("import_order_id"):
            order = bill.import_order_id.sudo()
            if order.company_id != bill.company_id:
                raise ValidationError("Import %s belongs to another company." % order.name)

    def _expense_account(self, line):
        cost_docs = self.sudo().import_cost_ids
        if cost_docs:
            # X08: the document is capitalised by the landed cost; its bill
            # relieves the accrual the final sheet credits
            return import_account(self.env, self.company_id, "landed_accrual")
        # X11 (goods of an import with no PO) is AP's import bill: it clears
        # GRNI at the receipt value with the FX split (cd_ap_ext fix_ap_grni)
        return super()._expense_account(line)

    # ---- A06 integration: no withholding on an import supplier's goods ----
    def _fix_is_import_goods_bill(self):
        """The foreign supplier's bill for imported goods: income tax (AIT,
        ITA 2023 s.120) and VAT/AT were collected by customs on the Bill of
        Entry, so no TDS or VDS is withheld again from the supplier. A local
        cost document's bill (C&F agent, freight, bank) is NOT one."""
        self.ensure_one()
        if self.sudo().import_cost_ids:
            return False
        if self.bill_type == "import" or self.import_order_id:
            return True
        po = self.requisition_id.sudo()
        return bool(po and "import_order_ids" in po._fields and po.import_order_ids)

    def _fix_clear_import_vds(self):
        for bill in self:
            if bill.vds_rate_id and bill._fix_is_import_goods_bill():
                bill.sudo()._guarded().write({"vds_rate_id": False})

    @api.model_create_multi
    def create(self, vals_list):
        bills = super().create(vals_list)
        bills._fix_clear_import_vds()
        return bills

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("fix_import_vds_cleared") and (
            {"bill_type", "import_order_ref", "requisition_id", "vds_rate_id"} & set(vals)
        ):
            self.with_context(fix_import_vds_cleared=True)._fix_clear_import_vds()
        return res

    def _post_approved_bill(self):
        docs = self.sudo().import_cost_ids
        if docs:
            # the documents' amounts are in the company currency (BDT on the
            # estate): the bill paying them must be in it too
            if self.currency_id != self.company_id.currency_id:
                raise UserError(
                    "Bill %s carries import cost documents and must be in %s."
                    % (self.invoice_ref, self.company_id.currency_id.name)
                )
            total = round(sum(docs.mapped("amount_bdt")), 2)
            if abs(total - round(self.subtotal, 2)) > 0.005:
                raise UserError(
                    "Bill %s is %.2f but the import cost documents it pays (%s) total %.2f: a "
                    "bill that pays landed cost carries exactly its cost documents (X08)."
                    % (
                        self.invoice_ref,
                        self.subtotal,
                        ", ".join(docs.mapped("document_ref")),
                        total,
                    )
                )
            if docs.filtered(lambda d: d.state == "rejected"):
                raise UserError(
                    "Bill %s pays a rejected import cost document: unlink it first."
                    % self.invoice_ref
                )
        return super()._post_approved_bill()

    def _fix_lc_advance_scope(self):
        scope = super()._fix_lc_advance_scope()
        if self.import_order_id and not scope:
            return [("scope_key", "=", self.import_order_id._import_scope_key())]
        return scope


class FixVendorInvoiceLineImport(models.Model):
    _inherit = "fix.vendor.invoice.line"

    @api.depends(
        "invoice_id.bill_type",
        "invoice_id.import_order_ref",
        "invoice_id.requisition_id",
        "invoice_id.import_cost_ids",
    )
    def _compute_tds(self):
        """A06 integration: the import supplier's goods bill withholds no TDS:
        AIT was collected at import on the Bill of Entry (ITA 2023 s.120)."""
        super()._compute_tds()
        for line in self:
            inv = line.invoice_id
            if inv and inv._fix_is_import_goods_bill():
                line.update(
                    {
                        "tds_amount": 0.0,
                        "tds_multiplier": 1.0,
                        "tds_section": "AIT collected at import (ITA 2023 s.120)",
                    }
                )


class FixImportCostBill(models.Model):
    _inherit = "fix.import.cost"

    bill_id = fields.Many2one(
        "fix.vendor.invoice",
        string="AP Bill",
        index=True,
        ondelete="restrict",
        copy=False,
        help="The supplier bill that pays this document. It debits the landed-cost accrual, "
        "never an expense (X08).",
    )
    order_line_id = fields.Many2one(
        "fix.import.order.line",
        string="Charged to Line",
        ondelete="restrict",
        help="A charge that belongs to one line only (e.g. a line's own inspection fee) is "
        "allocated to it directly (M44-09).",
    )

    @api.constrains("bill_id", "billed_by_id", "category", "order_line_id", "order_id")
    def _check_bill(self):
        for rec in self:
            if rec.order_line_id and rec.order_line_id.order_id != rec.order_id:
                raise ValidationError(
                    "%s is not a line of import %s."
                    % (rec.order_line_id.display_name, rec.order_id.name)
                )
            bill = rec.bill_id.sudo()
            if not bill:
                continue
            if rec.category == "other":
                raise ValidationError(
                    "An 'other' charge is not capitalised: its bill is expensed in AP as usual."
                )
            if bill.company_id != rec.company_id:
                raise ValidationError("Bill %s belongs to another company." % bill.invoice_ref)
            if bill.vendor_id.commercial_partner_id != rec.billed_by_id.commercial_partner_id:
                raise ValidationError(
                    "Bill %s is from %s but the document was billed by %s."
                    % (bill.invoice_ref, bill.vendor_id.name, rec.billed_by_id.name)
                )

    def write(self, vals):
        if "bill_id" in vals and not self.env.su:
            require_group(self.env, FINANCE, "Linking an import cost document to its bill")
            for rec in self:
                old = rec.sudo().bill_id
                if old and old.move_id and old.id != (vals["bill_id"] or False):
                    raise UserError(
                        "Cost document %s is paid by posted bill %s: the link is final."
                        % (rec.document_ref, old.invoice_ref)
                    )
            new = self.env["fix.vendor.invoice"].sudo().browse(vals["bill_id"] or 0).exists()
            if new and new.move_id:
                raise UserError(
                    "Bill %s is already posted: link its cost documents before it is approved."
                    % new.invoice_ref
                )
        return super().write(vals)


class FixImportOrderAp(models.Model):
    _inherit = "fix.import.order"

    @api.model
    def _import_default_params(self):
        from .fix_import_common import default_params

        return default_params(self.env)

    def _import_direct_costs(self, currency):
        """{order line id: amount} of reconciled capitalisable cost documents
        charged to one line (M44-09), in the sheet's currency."""
        self.ensure_one()
        from .fix_import_capture import COST_BUCKETS

        out = {}
        for doc in self.sudo().cost_ids.filtered(
            lambda d: d.state == "reconciled" and d.order_line_id and COST_BUCKETS.get(d.category)
        ):
            out[doc.order_line_id.id] = round(
                out.get(doc.order_line_id.id, 0.0) + doc._cost_in(currency, self), 2
            )
        return out


class FixImportBoeInputVat(models.Model):
    _inherit = "fix.import.boe"

    @api.model
    def consume_duty_paid(self, event):
        """import.duty_paid -> M51: the import VAT paid at customs is an input
        credit of the Bill of Entry's period (Mushak 6.1 side), recorded once
        per Bill of Entry. Eligibility is decided by M51's own check."""
        boe = self.sudo().browse(event.get("aggregate_id") or 0).exists()
        if not boe or "fix.input.vat.credit" not in self.env:
            return 0
        vat = boe.booked_vat if boe.levies_booked else boe.vat_amount
        if vat <= 0:
            return 0
        Credit = self.env["fix.input.vat.credit"].sudo()
        ref = "BoE %s" % boe.boe_no
        if Credit.search_count([("company_id", "=", boe.company_id.id), ("source_ref", "=", ref)]):
            return 0
        order = boe.order_id
        Credit.create(
            {
                "company_id": boe.company_id.id,
                "operating_unit_id": boe.operating_unit_id.id or False,
                "partner_id": (order.supplier_id or boe.company_id.partner_id).id,
                "supplier_mushak_no": boe.boe_no,
                "invoice_date": boe.boe_date,
                "currency_id": self.env.ref("base.BDT").id,
                "taxable_amount": round(boe.assessable_total, 2),
                "vat_amount": round(vat, 2),
                "adjustment_type": "invoice",
                "source_ref": ref,
            }
        )
        return 1
