# fix_a05_settlement_consumer - the consumer of ewaste.settlement_approved
# (A05 report "Cross-area follow-ups": the one A05 event FF-48 recorded as
# waiting on a finance consumer; the A05 build hands the approved settlement
# to finance by event and nothing consumed it).
#
# fix.ewaste.settlement is approved under the routed M63 control (amount and
# payee pinned by the A05 guards); this consumer raises the money document:
#   * incentive / recycler_fee (money LEAVES): a PENDING M50 payout
#     instruction on the payee - treasury releases it; nothing is paid before;
#   * recovery_income (money ARRIVES): a DRAFT M20 invoice on the payer,
#     for finance to issue.
# Same rules as the other relay consumers: relay only (superuser, from
# cron_relay); the payload is a claim, not evidence - the settlement is
# re-read, its state must be "approved", and the amount comes from the
# record; idempotent per source.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

PAY_KINDS = ("incentive", "recycler_fee")


class FixA05SettlementConsumers(models.AbstractModel):
    """Consumer of the approved e-waste settlement money event."""

    _name = "fix.a05.settlement.consumers"
    _description = "A05 E-Waste Settlement Event Consumers"

    @api.model
    def consume_ewaste_settlement_approved(self, event: dict) -> dict:
        if not self.env.su:
            raise AccessError("A05 settlement consumers run only from the event relay.")
        label = "E-waste settlement hand-off"
        aggregate = event.get("aggregate")
        if aggregate and aggregate != "fix.ewaste.settlement":
            raise UserError(
                "%s refused: the event's aggregate is %s, not fix.ewaste.settlement."
                % (label, aggregate)
            )
        payload = event.get("payload") or {}
        try:
            rec_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            rec_id = 0
        rec = self.env["fix.ewaste.settlement"].sudo().browse(rec_id).exists() if rec_id else None
        if not rec:
            raise UserError("%s refused: there is no fix.ewaste.settlement #%s." % (label, rec_id))
        if rec.state != "approved":
            raise UserError(
                "%s refused: settlement %s is %s, not approved." % (label, rec.name, rec.state)
            )
        amount = rec.amount or 0.0
        claimed = payload.get("amount")
        if claimed is not None:
            try:
                claimed = float(claimed)
            except (TypeError, ValueError):
                raise UserError("%s refused: the payload amount is not a number." % label) from None
            if abs(claimed - amount) > 0.005:
                raise UserError(
                    "%s refused: the event says BDT %.2f but settlement %s says BDT %.2f."
                    % (label, claimed, rec.name, amount)
                )
        if amount <= 0.005:
            raise UserError("%s refused: settlement %s has no amount." % (label, rec.name))
        if not rec.partner_id:
            raise UserError("%s refused: settlement %s has no payee." % (label, rec.name))
        company = rec.company_id or self.env.company

        if rec.kind in PAY_KINDS:
            # money out: a pending M50 instruction treasury releases
            Execution = self.env["fix.payment.execution"].sudo()
            existing = Execution.search(
                [("source_model", "=", rec._name), ("source_id", "=", rec.id)], limit=1
            )
            if existing:
                return {"model": existing._name, "id": existing.id, "created": False}
            pay = Execution.create(
                {
                    "company_id": company.id,
                    "operating_unit_id": self._any_ou(company).id,
                    "source_model": rec._name,
                    "source_id": rec.id,
                    "payee": rec.partner_id.name,
                    "partner_id": rec.partner_id.id,
                    "amount": amount,
                    "method": "bank_transfer",
                }
            )
            rec.message_post(
                body="Raised by the ewaste.settlement_approved hand-off: pending M50 "
                "payout of BDT %.2f to %s (%s). Treasury releases it; nothing is paid "
                "before then." % (amount, rec.partner_id.name, rec.kind)
            )
            return {"model": pay._name, "id": pay.id, "created": True}

        # recovery_income: money in - a draft M20 invoice on the payer
        Invoice = self.env["fix.ar.invoice"].sudo()
        existing = Invoice.search(
            [("source_model", "=", rec._name), ("source_id", "=", rec.id)], limit=1
        )
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}
        invoice = Invoice.create(
            {
                "company_id": company.id,
                "operating_unit_id": self._any_ou(company).id,
                "customer_id": rec.partner_id.id,
                "currency_id": rec.currency_id.id,
                "source_model": rec._name,
                "source_id": rec.id,
                "invoice_date": fields.Date.context_today(rec),
                "manual_reason": "E-waste material-recovery income %s" % rec.name,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "description": "Material-recovery income %s" % rec.name,
                            "taxable_amount": amount,
                            "vat_amount": 0.0,
                            "line_total": amount,
                        },
                    )
                ],
            }
        )
        rec.message_post(
            body="Raised by the ewaste.settlement_approved hand-off: draft M20 invoice "
            "%s for BDT %.2f on %s, for finance to issue." % (invoice.name, amount, rec.partner_id.name)
        )
        return {"model": invoice._name, "id": invoice.id, "created": True}

    def _any_ou(self, company):
        return self.env["operating.unit"].sudo().search([("company_id", "=", company.id)], limit=1)
