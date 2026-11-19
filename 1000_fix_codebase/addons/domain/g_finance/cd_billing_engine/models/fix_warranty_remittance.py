# An OEM warranty remittance reaches AR (A02 ERP audit X-10, 19 Nov 2026).
#
# A Claim Decision Officer records the brand's payment against its bank
# reference (cd_warranty_claims action_record_remittance). That wrote the
# amount on the claim and published warranty_claim.remitted, which nothing
# consumes: the brand's M20 invoice for the claim stayed open on AR after the
# claim was remitted and closed, aged and chased for money already received.
#
# A remittance is now booked: a confirmed M20 bank receipt on the brand
# (Dr bank / Cr AR) applied to the claim's OEM invoice up to its residual. The
# money is collected against the receivable the books hold, so a remittance
# that arrives BEFORE finance has issued that invoice waits on the claim and
# is booked the moment the invoice is issued (the claim already cannot close
# without the invoice, E3-07).
from odoo import fields, models


class FixWarrantyClaimRemittanceReceipt(models.Model):
    _inherit = "fix.warranty.claim"

    remittance_receipt_ids = fields.Many2many(
        "fix.ar.receipt",
        "fix_warranty_claim_remittance_receipt_rel",
        "claim_id",
        "receipt_id",
        string="Remittance Receipts (M20)",
        readonly=True,
        copy=False,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"remittance_receipt_ids"}

    def action_record_remittance(self, amount: float, bank_ref: str):
        result = super().action_record_remittance(amount, bank_ref)
        for claim in self:
            claim._fix_book_pending_remittance()
        return result

    def _fix_remittance_unbooked(self) -> float:
        self.ensure_one()
        booked = sum(
            self.remittance_receipt_ids.filtered(lambda r: r.state == "confirmed").mapped("amount")
        )
        return round((self.remittance_amount or 0.0) - booked, 2)

    def _fix_book_pending_remittance(self):
        """Book what the brand remitted and the books do not hold yet, once
        the claim's OEM invoice is issued; until then say so on the claim."""
        self.ensure_one()
        pending = self._fix_remittance_unbooked()
        if pending <= 0.005:
            return self.env["fix.ar.receipt"]
        invoice = self._oem_invoice()
        if not invoice or invoice.state not in ("issued", "paid"):
            self.message_post(
                body="Remittance of BDT %.2f is recorded but not yet on AR: it is booked against "
                "the brand's OEM invoice when finance issues it." % pending
            )
            return self.env["fix.ar.receipt"]
        refs = [r.strip() for r in (self.remittance_ref or "").split(",") if r.strip()]
        return self._fix_book_remittance(invoice, pending, refs[-1] if refs else self.claim_no)

    def _fix_book_remittance(self, invoice, amount, bank_ref):
        self.ensure_one()
        Receipt = self.env["fix.ar.receipt"].sudo().with_company(invoice.company_id)
        receipt = Receipt.create(
            {
                "company_id": invoice.company_id.id,
                "operating_unit_id": invoice.operating_unit_id.id or False,
                "branch_id": invoice.branch_id.id or False,
                "customer_id": invoice.customer_id.id,
                "amount": amount,
                "method": "bank_transfer",
                "reference": (bank_ref or "").strip() or self.claim_no,
                "receipt_date": fields.Date.context_today(self),
            }
        )
        receipt.action_confirm()
        self._guarded().write({"remittance_receipt_ids": [(4, receipt.id)]})
        invoice.invalidate_recordset(["amount_residual"])
        applied = round(min(receipt.amount, invoice.amount_residual), 2)
        if invoice.state == "issued" and applied > 0.005:
            self.env["fix.ar.allocation"].sudo().create(
                {"receipt_id": receipt.id, "invoice_id": invoice.id, "amount": applied}
            )
        self.message_post(
            body="Remittance %s of BDT %.2f booked as receipt %s; BDT %.2f applied to OEM "
            "invoice %s." % (bank_ref, amount, receipt.name, max(applied, 0.0), invoice.name)
        )
        return receipt


class FixArInvoiceBooksClaimRemittance(models.Model):
    _inherit = "fix.ar.invoice"

    def action_issue(self):
        result = super().action_issue()
        Claim = self.env["fix.warranty.claim"].sudo()
        for invoice in self.filtered(
            lambda i: i.source_model == "fix.warranty.claim" and i.state in ("issued", "paid")
        ):
            claim = Claim.browse(invoice.source_id).exists()
            if claim:
                claim._fix_book_pending_remittance()
        return result
