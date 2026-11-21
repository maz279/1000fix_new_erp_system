# fix_a05_settlement_consumer - the consumer of ewaste.settlement_approved
# (A05 report "Cross-area follow-ups": the one A05 event FF-48 recorded as
# waiting on a finance consumer; the A05 build hands the approved settlement
# to finance by event and nothing consumed it).
#
# fix.ewaste.settlement is approved under the routed M63 control (amount,
# payee, operating unit, branch, payment method and payee account pinned by
# the A05 guards); this consumer raises the money document:
#   * incentive / recycler_fee (money LEAVES): a PENDING M50 payout
#     instruction through _fix_request_payment - pinned to the approval
#     (payee, account, amount, approver), on the settlement's operating unit,
#     debiting the owner's 'E-waste Collection & Recycling Cost' expense
#     (D1, cd_ewaste.account_code.recycling_cost). Treasury releases it;
#     nothing is paid before;
#   * recovery_income (money ARRIVES): a DRAFT M20 invoice through
#     _fix_ar_invoice_from_source - crediting 400109 Other Income (D1,
#     cd_ewaste.account_code.recovery_income) on the batch's operating unit and
#     branch, VAT by the M51 determination (standard rate, D2), for finance
#     to issue.
#
# A05 ERP build S3 (20 Nov 2026): M18-01..04, FIN-05/06/11, XC-05. The old
# consumer created the execution directly (never pinned: treasury could re-point
# it), with no debit account (Dr Bank Suspense), on the company's first OU, and
# invoiced income at VAT 0 to 400100.
#
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
        if not rec.approved_by_id:
            raise UserError("%s refused: settlement %s has no approver." % (label, rec.name))
        if not rec.operating_unit_id:
            # FIN-11: never the company's first OU
            raise UserError("%s refused: settlement %s has no operating unit." % (label, rec.name))

        if rec.kind in PAY_KINDS:
            return self._fix_pay(rec, amount)
        return self._fix_invoice(rec, amount)

    def _fix_pay(self, rec, amount):
        """Money out: a pending, pinned M50 instruction treasury releases."""
        Execution = self.env["fix.payment.execution"].sudo()
        existing = Execution.search(
            [("source_model", "=", rec._name), ("source_id", "=", rec.id)], limit=1
        )
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}
        if not rec.payment_method:
            raise UserError("Settlement %s names no payment method." % rec.name)
        expense = rec._fix_money_account("recycling_cost")
        pay = Execution._fix_request_payment(
            rec._name,
            rec.id,
            rec.partner_id,
            rec.partner_bank_id,
            amount,
            rec.currency_id,
            rec.name,
            rec.approved_by_id,
            method=rec._fix_pay_method(),
            debit_account_id=expense.id,
            company_id=rec.company_id.id,
            operating_unit_id=rec.operating_unit_id.id,
            # I3 (S6 wiring): the confirmation posts on the settlement's branch
            branch_id=rec.branch_id.id or False,
        )
        rec.message_post(
            body="Raised by the ewaste.settlement_approved hand-off: pending M50 payout %s of "
            "BDT %.2f to %s (%s, %s), debiting %s %s. Treasury releases it; nothing is paid "
            "before then."
            % (
                pay.name,
                amount,
                rec.partner_id.name,
                rec.kind,
                rec.payment_method,
                expense.code,
                expense.name,
            )
        )
        return {"model": pay._name, "id": pay.id, "created": True}

    def _fix_invoice(self, rec, amount):
        """Money in: a draft M20 invoice on the payer, VAT by M51 (D2)."""
        Invoice = self.env["fix.ar.invoice"].sudo()
        existing = Invoice.search(
            [("source_model", "=", rec._name), ("source_id", "=", rec.id)], limit=1
        )
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}
        if not hasattr(Invoice, "_fix_ar_invoice_from_source"):
            raise UserError(
                "Recovery income %s is invoiced through M20 (_fix_ar_invoice_from_source), "
                "which is not installed." % rec.name
            )
        income = rec._fix_money_account("recovery_income")
        lines = rec.recovery_ids
        description = "Recovered material (scrap) sale, batch %s" % rec.batch_id.name
        if lines:
            description += ": " + ", ".join(
                "%s %.3f kg"
                % (
                    dict(line._fields["material_class"].selection).get(
                        line.material_class, line.material_class
                    ),
                    line.weight_kg,
                )
                for line in lines
            )
        invoice = Invoice._fix_ar_invoice_from_source(
            rec,
            rec.partner_id,
            # no treatment code: M51 determines the standard rate (owner D2)
            [{"description": description[:250], "taxable_amount": amount}],
            "E-waste material-recovery income %s approved by %s"
            % (rec.name, rec.approved_by_id.name),
            credit_account=income,
            operating_unit=rec.operating_unit_id,
            branch=rec.branch_id or None,
            invoice_date=fields.Date.context_today(rec.with_context(tz="Asia/Dhaka")),
            issue=False,
        )
        rec.message_post(
            body="Raised by the ewaste.settlement_approved hand-off: draft M20 invoice %s for "
            "BDT %.2f (ex VAT) on %s, crediting %s %s, for finance to issue."
            % (invoice.name, amount, rec.partner_id.name, income.code, income.name)
        )
        return {"model": invoice._name, "id": invoice.id, "created": True}
