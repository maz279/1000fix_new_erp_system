# G12 (owner decision 12 Nov 2026): the customer is never billed for a part
# that was never fitted.
#
# An APPROVED billed-part-not-fitted exemption (fix.so.part.exemption,
# cd_service_order) is honoured in one of two ways:
#
#   * the order is not invoiced yet: from_closed_service_order leaves the
#     exempted quantity off the invoice (fix_billing_engine.py), and D3-01
#     accepts the invoice lower than the accepted quotation by exactly the
#     approved exemptions;
#   * the order was invoiced BEFORE the exemption (e.g. one of the D-11 orders
#     closed and invoiced before the close gate existed): the exemption raises
#     an M20 credit note for the part through the credit-note API
#     (fix.credit.note._fix_request_credit). The note is created and
#     submitted; it then runs its own approval ladder (a second Accountant
#     within the band, the Accounting Administrator above it), so the branch
#     manager who approved the exemption never approves the money.
#
# The note is requested as the approving user (sudo keeps the uid), so its
# requester is a real person and is excluded from deciding it.
from odoo import fields, models

CREDIT_REASON = "part_not_fitted"
_CREDITABLE_STATES = ("issued", "paid")


class FixSoPartExemptionBilling(models.Model):
    _inherit = "fix.so.part.exemption"

    credit_note_id = fields.Many2one(
        "fix.credit.note",
        string="Credit Note",
        readonly=True,
        copy=False,
        help="The M20 credit note raised for this part when the order was invoiced before "
        "the exemption was approved.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"credit_note_id"}

    def _fix_order_invoice(self):
        """The auto-invoice of this exemption's order, if one was raised."""
        self.ensure_one()
        return (
            self.env["fix.ar.invoice"]
            .sudo()
            .search(
                [("source_model", "=", "fix.service.order"), ("source_id", "=", self.order_id.id)],
                order="id desc",
                limit=1,
            )
        )

    def _fix_after_approved(self):
        super()._fix_after_approved()
        for rec in self:
            if rec.credit_note_id:
                continue
            invoice = rec._fix_order_invoice()
            if not invoice:
                continue  # the invoice, when raised, leaves the part off
            if invoice.state not in _CREDITABLE_STATES:
                rec._fix_log(
                    "Billed part not fitted: invoice %s is %s, so no credit note is raised for "
                    "%s." % (invoice.name, invoice.state, rec._fix_part_label())
                )
                continue
            note = (
                self.env["fix.credit.note"]
                .sudo()
                ._fix_request_credit(
                    invoice,
                    rec.amount,
                    CREDIT_REASON,
                    note="Billed part not fitted: %s x %s on %s (%s). Exemption approved by %s."
                    % (
                        ("%.4f" % rec.quantity).rstrip("0").rstrip("."),
                        rec._fix_part_label(),
                        rec.order_id.name,
                        rec.reason,
                        self.env.user.name,
                    ),
                )
            )
            rec._guarded().write({"credit_note_id": note.id})
            rec._fix_log(
                "Billed part not fitted: order %s was already invoiced (%s); credit note #%s "
                "of BDT %.2f raised for %s and submitted for approval."
                % (rec.order_id.name, invoice.name, note.id, note.amount, rec._fix_part_label())
            )
