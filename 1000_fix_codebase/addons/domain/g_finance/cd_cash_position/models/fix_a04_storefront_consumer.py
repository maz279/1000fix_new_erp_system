# fix_a04_storefront_consumer - the R8 consumer of storefront.refund_approved
# (A04 build, report §6 C7: "refund -> M20 credit note (real Mushak 6.7)").
#
# A storefront refund is approved under the return-window, inspection-grade and
# DOFA controls (M38), the event is published - and nothing consumed it: the
# customer's money moved only if finance noticed. Same rules as the A02
# hand-backs:
#   * relay only (consume_* is superuser, from cron_relay);
#   * the payload is a claim, not evidence: the return is re-read, its state
#     must be refund_approved, and the amount comes from the record;
#   * idempotent per source (M50 is UNIQUE (source_model, source_id));
#   * nothing is paid: the refund goes back the way it came (the rail the
#     order paid on) as a PENDING M50 instruction treasury releases. When the
#     order carries a creditable M20 invoice the refund is a draft credit note
#     against it instead (the Mushak 6.7 path; storefront orders raise
#     receipts today, so the invoice branch is ready but not the live one).
from odoo import api, models
from odoo.exceptions import AccessError, UserError

# the order's payment rail -> the M50 method the money goes back by
RAIL_METHOD = {
    "bkash": "mobile_fs",
    "nagad": "mobile_fs",
    "rocket": "mobile_fs",
    "upay": "mobile_fs",
    "mobile_wallet": "mobile_fs",
    "sslcommerz": "bank_transfer",
    "card": "bank_transfer",
    "bank_transfer": "bank_transfer",
    "cash": "cash",
    "cash_on_delivery": "cash",
}


class FixA04StorefrontConsumers(models.AbstractModel):
    """R8 consumer of the A04 storefront money event (no table of its own)."""

    _name = "fix.a04.storefront.consumers"
    _description = "A04 Storefront Event Consumers"

    @api.model
    def consume_storefront_refund_approved(self, event: dict) -> dict:
        self._assert_relay()
        label = "Storefront refund hand-off"
        aggregate = event.get("aggregate")
        if aggregate and aggregate != "fix.storefront.return":
            raise UserError(
                "%s refused: the event's aggregate is %s, not fix.storefront.return."
                % (label, aggregate)
            )
        payload = event.get("payload") or {}
        try:
            rec_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            rec_id = 0
        ret = self.env["fix.storefront.return"].sudo().browse(rec_id).exists() if rec_id else None
        if not ret:
            raise UserError("%s refused: there is no fix.storefront.return #%s." % (label, rec_id))
        if ret.state != "refund_approved":
            raise UserError(
                "%s refused: return %s is %s, not refund_approved." % (label, ret.name, ret.state)
            )
        amount = ret.refund_amount or 0.0
        claimed = payload.get("refund_amount")
        if claimed is not None:
            try:
                claimed = float(claimed)
            except (TypeError, ValueError):
                raise UserError("%s refused: refund_amount is not a number." % label) from None
            if abs(claimed - amount) > 0.005:
                raise UserError(
                    "%s refused: the event says BDT %.2f but the return says BDT %.2f."
                    % (label, claimed, amount)
                )
        if amount <= 0.005:
            raise UserError("%s refused: return %s has no refund amount." % (label, ret.name))

        order = ret.order_id.sudo()
        customer = ret.customer_id
        if not customer:
            raise UserError("%s refused: return %s has no customer." % (label, ret.name))

        # the Mushak 6.7 path first: a credit note against the order's own
        # invoice, when there is one left to credit
        if "fix.credit.note" in self.env and "fix.ar.invoice" in self.env:
            CreditNote = self.env["fix.credit.note"].sudo()
            existing_note = CreditNote.search(
                [("source_model", "=", ret._name), ("source_id", "=", ret.id)], limit=1
            )
            if existing_note:
                return {"model": existing_note._name, "id": existing_note.id, "created": False}
            invoice = (
                self.env["fix.ar.invoice"]
                .sudo()
                .search(
                    [
                        ("source_model", "=", order._name),
                        ("source_id", "=", order.id),
                        ("state", "in", ("issued", "paid")),
                    ],
                    limit=1,
                )
            )
            if (
                invoice
                and invoice.customer_id.commercial_partner_id == customer.commercial_partner_id
            ):
                creditable = round(invoice.total_payable - invoice.credited_amount, 2)
                if creditable > 0.005:
                    credit = min(amount, creditable)
                    note = CreditNote.create(
                        {
                            "company_id": invoice.company_id.id,
                            "operating_unit_id": invoice.operating_unit_id.id,
                            "invoice_id": invoice.id,
                            "customer_id": invoice.customer_id.id,
                            "amount": credit,
                            "reason_code": "return",
                            "source_model": ret._name,
                            "source_id": ret.id,
                            "source_amount": credit,
                        }
                    )
                    note.message_post(
                        body="Raised by the storefront.refund_approved hand-off of %s: draft "
                        "credit note for BDT %.2f against invoice %s, for finance to approve "
                        "and issue." % (ret.name, credit, invoice.name)
                    )
                    return {"model": note._name, "id": note.id, "created": True}

        # otherwise the money goes back the way it came: a pending M50
        # instruction on the order's rail, released by treasury
        Execution = self.env["fix.payment.execution"].sudo()
        existing = Execution.search(
            [("source_model", "=", ret._name), ("source_id", "=", ret.id)], limit=1
        )
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}
        company = order.company_id or self.env.company
        pay = Execution.create(
            {
                "company_id": company.id,
                "operating_unit_id": (order.operating_unit_id or self._any_ou(company)).id,
                "source_model": ret._name,
                "source_id": ret.id,
                "payee": customer.name,
                "partner_id": customer.id,
                "amount": amount,
                "method": RAIL_METHOD.get(order.payment_rail, "bank_transfer"),
            }
        )
        pay.message_post(
            body="Raised by the storefront.refund_approved hand-off of %s: refund BDT %.2f to "
            "%s back over the %s rail. Treasury releases it; nothing is paid before then."
            % (ret.name, amount, customer.name, order.payment_rail or "unspecified")
        )
        return {"model": pay._name, "id": pay.id, "created": True}

    def _assert_relay(self):
        if not self.env.su:
            raise AccessError("A04 storefront consumers run only from the event relay (report C7).")

    def _any_ou(self, company):
        return self.env["operating.unit"].sudo().search([("company_id", "=", company.id)], limit=1)
