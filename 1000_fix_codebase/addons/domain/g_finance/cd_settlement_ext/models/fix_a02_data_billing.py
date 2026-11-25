# fix_a02_data_billing — M06 data recovery billing to M20 (A02 ERP audit
# M06-F1, P0, builder stream B1).
#
# M06 never billed: no invoice, payment, deposit or VAT anywhere; the
# data_case.quote_accepted / recovered / purged events had no consumer, and
# the recovered data was handed over with nothing paid (spec §12.2: the M20
# receivable is the evaluation, recovery and destruction fees). The outcome
# events are now R8 relay consumers that raise the case's M20 invoice, in
# draft, for finance to issue (number, Mushak 6.3, GL) and collect:
#
#   data_case.recovered     -> the accepted quotation's recovery fee and the
#                              donor fee;
#   data_case.unrecoverable -> under no-data-no-fee only the donor fee (or
#                              nothing); without the guarantee the quotation
#                              stands.
#
# What a case bills is the case's own rule (cd_data_case,
# fix.data.recovery.case._data_billable), so the hand-over gate there and the
# invoice here agree. The pattern is the A02 hand-backs (fix_a02_handback):
# superuser only, the payload is a claim (the case is re-read and must be in
# the outcome the event announces), idempotent per case (one invoice per
# source record, the billing engine's key), never paid here. VAT is M51's
# determination and the GL accounts the billing engine's configuration, as
# for every source invoice (_fix_ar_invoice_from_source).
from odoo import api, models
from odoo.exceptions import UserError

from .fix_a02_handback import RELAY_ONLY

CASE = "fix.data.recovery.case"


class FixDataCaseBilling(models.AbstractModel):
    """The R8 consumers of the M06 case outcomes (no table of its own)."""

    _name = "fix.data.case.billing"
    _description = "M06 Data Recovery Billing Consumers"

    @api.model
    def consume_data_case_recovered(self, event: dict) -> dict:
        return self._bill_case(event, "recovered")

    @api.model
    def consume_data_case_unrecoverable(self, event: dict) -> dict:
        return self._bill_case(event, "unrecoverable")

    def _bill_case(self, event, outcome):
        Handback = self.env["fix.finance.handback"]
        Handback._handback_assert_relay()
        label = "Data recovery billing"
        case, _payload = Handback._handback_source(event, CASE, label)
        Invoice = self.env["fix.ar.invoice"].sudo()
        existing = Invoice.search(
            [("source_model", "=", CASE), ("source_id", "=", case.id)], limit=1
        )
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}
        quote, lines, actual = case._data_billable()
        if actual != outcome:
            raise UserError(
                "%s refused: case %s is '%s', not %s." % (label, case.name, case.state, outcome)
            )
        marker = "M20 billing:"
        if not lines:
            why = (
                "no accepted quotation"
                if not quote
                else "no-data-no-fee applies and there is no donor fee"
            )
            Handback._handback_note(case, marker, "nothing to bill (%s)." % why)
            return {"model": False, "id": False, "created": False, "billed": 0.0}
        invoice = Invoice._fix_ar_invoice_from_source(
            case,
            case.customer_id,
            [{"description": desc, "taxable_amount": amount} for desc, amount in lines],
            "Data recovery case %s, quotation %s accepted (%s)" % (case.name, quote.name, outcome),
            operating_unit=case.operating_unit_id or None,
            issue=False,
        )
        total = round(sum(amount for _d, amount in lines), 2)
        invoice.message_post(
            body="Draft raised from data recovery case %s (%s), quotation %s, BDT %.2f before "
            "VAT, for finance to issue and collect. The recovered data is handed over only "
            "once this invoice is paid, or on a recorded credit approval or waiver."
            % (case.name, outcome, quote.name, total)
        )
        Handback._handback_note(
            case,
            marker,
            "draft invoice #%s of BDT %.2f before VAT (%s), for finance to issue."
            % (invoice.id, total, ", ".join(desc for desc, _a in lines)),
        )
        return {"model": invoice._name, "id": invoice.id, "created": True, "billed": total}


class FixArInvoiceDataCase(models.Model):
    """A data-case invoice is raised by the relay only: a user cannot
    pre-create one under the case's key, or re-point one to a case."""

    _inherit = "fix.ar.invoice"

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and any(vals.get("source_model") == CASE for vals in vals_list):
            raise UserError("A data recovery invoice %s." % RELAY_ONLY)
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su and (
            vals.get("source_model") == CASE
            or (
                {"source_model", "source_id"} & set(vals)
                and any(inv.source_model == CASE for inv in self)
            )
        ):
            raise UserError("A data recovery invoice %s." % RELAY_ONLY)
        return super().write(vals)
