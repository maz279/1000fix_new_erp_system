# A warranty-claim write-off reaches AR (A02 ERP pass 2, X5-05 / owner D24).
#
# M09 writes off what a brand will never pay (fix.claim.writeoff, approved by
# a Finance Manager who raised nothing, BRU-WTY-07) and publishes
# warranty_claim.written_off. Nothing consumed it: the brand's M20 invoice for
# the claim stayed open on AR - aged, chased by dunning, and counted in the
# receivables - for money the business had already decided to forgo.
#
# Owner decision D24: the M09 Finance Manager approval IS the M20 approval, so
# the write-off is not put to the M20 ladder a second time. The consumer books
# an fix.ar.writeoff on the claim's OEM invoice stamped with the M09 decider
# and posts it through M20's own posting (Dr loss allowance up to its balance,
# the rest Dr bad debts - 510008 on fix_real through
# cd_billing_engine.account_code.writeoff_expense - / Cr AR on the brand).
#
#   * relay only (superuser), like every R8 consumer;
#   * the payload is a claim, not evidence: the write-off is re-read by its
#     reference on the claim, must be approved, and the amount is the record's;
#   * idempotent per write-off: fix.ar.writeoff.claim_writeoff_id is UNIQUE;
#   * the invoice is written off by what the claim wrote off, never more than
#     its residual: a partial write-off leaves the rest owing (issued);
#   * an invoice finance has not issued yet holds nothing to write off: the
#     write-off waits on the claim and is booked when the invoice is issued,
#     after any pending remittance (fix_warranty_remittance).
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError


class FixArWriteoffClaimSource(models.Model):
    _inherit = "fix.ar.writeoff"

    claim_writeoff_id = fields.Many2one(
        "fix.claim.writeoff",
        string="Warranty Claim Write-off (M09)",
        readonly=True,
        copy=False,
        index=True,
        ondelete="restrict",
        help="The M09 write-off this AR write-off books. Its Finance Manager approval "
        "is the M20 approval (owner decision D24).",
    )

    _claim_writeoff_unique = models.Constraint(
        "UNIQUE (claim_writeoff_id)", "A warranty-claim write-off is booked on AR once."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"claim_writeoff_id"}

    def _fin_after_approve(self):
        """M20 closes the invoice as written off. A claim write-off may cover
        only part of the brand's invoice: the rest is still owed, so the
        invoice stays issued with the lower residual."""
        result = super()._fin_after_approve()
        for wo in self.sudo().filtered("claim_writeoff_id"):
            invoice = wo.invoice_id
            invoice.invalidate_recordset(["amount_residual", "written_off_amount"])
            if invoice.state == "written_off" and invoice.amount_residual > 0.005:
                invoice._guarded().write({"state": "issued"})
        return result


class FixClaimWriteoffBooksAr(models.Model):
    _inherit = "fix.claim.writeoff"

    ar_writeoff_id = fields.Many2one(
        "fix.ar.writeoff",
        string="AR Write-off (M20)",
        readonly=True,
        copy=False,
        index=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"ar_writeoff_id"}

    def _fix_book_ar_writeoff(self):
        """Book this approved write-off on the claim's OEM invoice. Returns
        the fix.ar.writeoff, or an empty recordset when there is nothing to
        book yet (the invoice is not issued) or at all (nothing residual)."""
        self.ensure_one()
        ARWriteoff = self.env["fix.ar.writeoff"].sudo()
        rec = self.sudo()
        if rec.state != "approved":
            return ARWriteoff
        if rec.ar_writeoff_id:
            return rec.ar_writeoff_id
        existing = ARWriteoff.search([("claim_writeoff_id", "=", rec.id)], limit=1)
        if existing:
            rec._guarded().write({"ar_writeoff_id": existing.id})
            return existing
        claim = rec.claim_id
        invoice = claim._oem_invoice()
        if not invoice or invoice.state == "draft":
            claim.message_post(
                body="Write-off %s (BDT %.2f) is approved but not yet on AR: it is booked "
                "against the brand's OEM invoice when finance issues it." % (rec.name, rec.amount)
            )
            return ARWriteoff
        invoice.invalidate_recordset(["amount_residual"])
        amount = round(min(rec.amount, invoice.amount_residual), 2)
        if invoice.state != "issued" or amount <= 0.005:
            claim.message_post(
                body="Write-off %s (BDT %.2f) is not booked on AR: OEM invoice %s is %s with "
                "BDT %.2f residual, so nothing of it is still open."
                % (rec.name, rec.amount, invoice.name, invoice.state, invoice.amount_residual)
            )
            return ARWriteoff
        decider = rec.approved_by_id
        wo = ARWriteoff.create(
            {
                "invoice_id": invoice.id,
                "claim_writeoff_id": rec.id,
                "reason": (
                    "Warranty claim %s write-off %s: %s"
                    % (claim.claim_no, rec.name, (rec.reason or "").strip())
                )[:250],
                "recovery_history": "Claim %s: approved BDT %.2f, remitted BDT %.2f by the brand. "
                "Write-off %s of BDT %.2f requested by %s and approved by %s (Finance Manager, "
                "M09 BRU-WTY-07) on %s; that approval is the M20 approval (owner decision D24)."
                % (
                    claim.claim_no,
                    claim.approved_amount or 0.0,
                    claim.remittance_amount or 0.0,
                    rec.name,
                    rec.amount,
                    rec.requested_by_id.name or rec.create_uid.name or "-",
                    decider.name or "-",
                    rec.decided_at or "-",
                ),
            }
        )
        wo._guarded().write(
            {
                "state": "requested",
                "amount": amount,
                "requested_by_id": (rec.requested_by_id or rec.create_uid).id,
                "requested_at": rec.create_date,
                "fin_approved_by_id": decider.id,
                "fin_approved_at": rec.decided_at or fields.Datetime.now(),
                "fin_approved_amount": amount,
            }
        )
        wo._fin_after_approve()
        rec._guarded().write({"ar_writeoff_id": wo.id})
        claim.message_post(
            body="Write-off %s booked on AR as %s: BDT %.2f written off OEM invoice %s "
            "(GL %s)." % (rec.name, wo.name, amount, invoice.name, wo.move_id.name or "-")
        )
        return wo


class FixA04ClaimConsumersWriteoff(models.AbstractModel):
    _inherit = "fix.a04.claim.consumers"

    @api.model
    def consume_warranty_claim_written_off(self, event: dict) -> dict:
        """warranty_claim.written_off -> the write-off on the OEM invoice."""
        if not self.env.su:
            raise AccessError("Claim consumers run only from the event relay (X5-05).")
        label = "Warranty claim write-off hand-off"
        aggregate = event.get("aggregate")
        if aggregate and aggregate != "fix.warranty.claim":
            raise UserError(
                "%s refused: the event's aggregate is %s, not fix.warranty.claim."
                % (label, aggregate)
            )
        payload = event.get("payload") or {}
        try:
            claim_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            claim_id = 0
        claim = (
            self.env["fix.warranty.claim"].sudo().browse(claim_id).exists() if claim_id else None
        )
        if not claim:
            raise UserError("%s refused: there is no fix.warranty.claim #%s." % (label, claim_id))
        name = (payload.get("writeoff_no") or "").strip()
        writeoff = (
            self.env["fix.claim.writeoff"]
            .sudo()
            .search([("claim_id", "=", claim.id), ("name", "=", name)], limit=1)
            if name
            else None
        )
        if not writeoff:
            raise UserError(
                "%s refused: claim %s has no write-off %r." % (label, claim.claim_no, name)
            )
        if writeoff.state != "approved":
            raise UserError(
                "%s refused: write-off %s is %s, not approved." % (label, name, writeoff.state)
            )
        claimed = payload.get("amount")
        if claimed is not None:
            try:
                claimed = float(claimed)
            except (TypeError, ValueError):
                raise UserError("%s refused: amount is not a number." % label) from None
            if abs(claimed - writeoff.amount) > 0.005:
                raise UserError(
                    "%s refused: the event says BDT %.2f but write-off %s says BDT %.2f."
                    % (label, claimed, name, writeoff.amount)
                )
        booked = writeoff._fix_book_ar_writeoff()
        return {
            "model": "fix.ar.writeoff",
            "id": booked.id or False,
            "booked": bool(booked),
            "claim_writeoff": writeoff.name,
        }


class FixArInvoiceBooksClaimWriteoff(models.Model):
    _inherit = "fix.ar.invoice"

    def action_issue(self):
        """An approved claim write-off waiting for the brand's invoice is
        booked once the invoice is issued (after any pending remittance,
        which fix_warranty_remittance books in the method this one extends)."""
        result = super().action_issue()
        Writeoff = self.env["fix.claim.writeoff"].sudo()
        for invoice in self.filtered(
            lambda i: i.source_model == "fix.warranty.claim" and i.state == "issued"
        ):
            pending = Writeoff.search(
                [
                    ("claim_id", "=", invoice.source_id),
                    ("state", "=", "approved"),
                    ("ar_writeoff_id", "=", False),
                ],
                order="id asc",
            )
            for writeoff in pending:
                writeoff._fix_book_ar_writeoff()
        return result
