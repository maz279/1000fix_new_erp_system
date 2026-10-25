# cd_ap_ext — the AP side of M51's compliance records (CD-M52-01).
#
# cd_tax_engine_bd sits BELOW cd_ap_ext in the module graph, so the pointers
# from its deduction lines, input credits and audit pack to M52's bills and
# notes live here, on the AP side of the boundary (dependency-cycle finding).
from odoo import fields, models


class FixWithholdingLineAp(models.Model):
    _inherit = "fix.withholding.line"

    vendor_invoice_id = fields.Many2one(
        "fix.vendor.invoice", string="Vendor Bill", index=True, ondelete="restrict"
    )
    payment_run_id = fields.Many2one(
        "fix.payment.run",
        string="Payment Run",
        compute="_compute_payment_run",
        help="The run that paid the bill net of this deduction",
    )

    def _compute_payment_run(self):
        for line in self:
            run_line = self.env["fix.payment.run.line"].search(
                [("bill_ids", "in", line.vendor_invoice_id.ids)], order="id desc", limit=1
            )
            line.payment_run_id = run_line.run_id

    def _certificate_vals(self):
        vals = super()._certificate_vals()
        vals["vendor_invoice_id"] = self.vendor_invoice_id.id
        return vals


class FixInputVatCreditAp(models.Model):
    _inherit = "fix.input.vat.credit"

    vendor_invoice_id = fields.Many2one(
        "fix.vendor.invoice", string="Vendor Bill", index=True, ondelete="restrict"
    )


class FixTaxAuditPackAp(models.Model):
    _inherit = "fix.tax.audit.pack"

    def _pack_sections(self):
        sections = super()._pack_sections()
        c = [("company_id", "=", self.company_id.id)]
        sections += [
            (
                "mushak_6_7_6_8_vendor_notes.csv",
                "fix.vendor.note",
                [*c, ("note_date", ">=", self.date_from), ("note_date", "<=", self.date_to)],
                [
                    "name",
                    "note_type",
                    "mushak_ref",
                    "note_date",
                    "vendor_id",
                    "invoice_id",
                    "amount",
                    "vat_amount",
                    "state",
                ],
            ),
            (
                "vendor_bills.csv",
                "fix.vendor.invoice",
                [*c, ("invoice_date", ">=", self.date_from), ("invoice_date", "<=", self.date_to)],
                [
                    "invoice_ref",
                    "vendor_id",
                    "invoice_date",
                    "supplier_mushak_no",
                    "subtotal",
                    "vat_amount",
                    "tds_amount",
                    "vds_amount",
                    "total_payable",
                    "approval_state",
                    "payment_state",
                    "move_id",
                ],
            ),
        ]
        return sections
