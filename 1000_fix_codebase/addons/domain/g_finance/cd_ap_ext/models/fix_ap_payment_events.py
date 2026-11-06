# cd_ap_ext -- treasury's answer to a payment request (A08 M52-4, M52-9).
#
# payment.executed / payment.failed had no consumer: a claim stayed `approved`
# for ever after the bank paid it, and the payable it carried was never cleared.
#
# M50 books the bank side of a claim, a bill's Request Payment and an advance
# excess itself (Dr outgoing clearing / Cr bank: they are not self-posting
# sources), so the document clears its own payable against that clearing here.
# Payment runs and advance disbursements post their own payment entry when a
# person reads the bank status: they are not handled here.
#
# The payload is a pointer: the instruction is re-read. A caller-asserted
# (legacy) execution is not a bank confirmation and moves nothing.
from odoo import api, fields, models
from odoo.addons.cd_cash_position.models.treasury_common import treasury_account
from odoo.exceptions import AccessError, UserError

from .ap_gl import ap_account, ap_journal, post_ap_move
from .fix_ap_ext import _q

EXCESS_SOURCE = "fix.employee.advance.excess"


class FixApPaymentEvents(models.AbstractModel):
    _name = "fix.ap.payment.events"
    _description = "AP: treasury payment events"

    def _execution(self, event):
        if not self.env.su:
            raise AccessError("Treasury's payment events are consumed by the event relay only.")
        return self.env["fix.payment.execution"].browse(event.get("aggregate_id") or 0).exists()

    def _document(self, execution):
        """(document, payable role, move field, partner) of a source we settle."""
        model, res_id = execution.source_model, execution.source_id
        if model == "fix.expense.claim":
            doc = self.env[model].browse(res_id).exists()
            return doc, "employee_payable", "payment_move_id", self._employee_partner(doc)
        if model == "fix.vendor.invoice":
            doc = self.env[model].browse(res_id).exists()
            return doc, "ap", "payment_move_id", doc.vendor_id.commercial_partner_id
        if model == EXCESS_SOURCE:
            doc = self.env["fix.employee.advance"].browse(res_id).exists()
            return doc, "employee_payable", "excess_payment_move_id", self._employee_partner(doc)
        return self.env["res.users"].browse(), None, None, None

    @staticmethod
    def _employee_partner(doc):
        employee = doc.employee_id.sudo()
        return employee.work_contact_id or employee.user_id.partner_id

    def _clearing_account(self, execution):
        return execution.debit_account_id or treasury_account(
            self.env, execution.company_id, "outgoing_clearing"
        )

    def _post_clearing(self, execution, doc, role, partner, label, reverse=False):
        """Dr payable / Cr the account treasury debited (reversed on a return)."""
        company = execution.company_id
        amount = _q(execution.released_amount or execution.amount)
        payable = (ap_account(self.env, company, role), label, amount, 0.0, partner)
        clearing = (self._clearing_account(execution), label, 0.0, amount, partner)
        if reverse:
            payable = (payable[0], label, 0.0, amount, partner)
            clearing = (clearing[0], label, amount, 0.0, partner)
        return post_ap_move(
            self.env,
            company,
            ap_journal(self.env, company, "purchase"),
            fields.Date.context_today(self),
            label,
            [payable, clearing],
            doc.operating_unit_id,
        )

    @api.model
    def consume_payment_executed(self, event):
        execution = self._execution(event)
        if not execution or execution.state != "executed":
            return False
        if execution.confirmation_source == "caller_asserted":
            return False
        doc, role, move_field, partner = self._document(execution)
        if not doc or doc[move_field]:
            return False  # not ours, or already settled: a replay moves nothing
        vals = {}
        # treasury's own entry is what this clears; without one there is nothing
        if execution.move_id:
            label = "%s paid: %s" % (doc.display_name, execution.name)
            vals[move_field] = self._post_clearing(execution, doc, role, partner, label).id
        if execution.source_model == "fix.expense.claim":
            self._claim_paid(doc, execution, vals)
        elif execution.source_model == "fix.vendor.invoice":
            self._bill_paid(doc, execution, vals)
        else:
            self._excess_paid(doc, vals)
        return True

    def _claim_paid(self, claim, execution, vals):
        if claim.state not in ("approved", "paid"):
            raise UserError(
                "Treasury paid %s on claim EXP/%s, which is %s."
                % (execution.name, claim.id, claim.state)
            )
        claim._guarded().write({**vals, "state": "paid", "payment_failure": False})

    def _bill_paid(self, bill, execution, vals):
        lock = self.env["fix.ap.bill.payment"].search(
            [("bill_id", "=", bill.id), ("state", "=", "open"), ("run_line_id", "=", False)],
            limit=1,
        )
        if lock:
            lock.write({"state": "paid", "execution_id": execution.id})
        bill._guarded().write({**vals, "payment_state": "paid", "payment_failure": False})
        if bill.payment_channel == "bank" and execution.method not in (
            "bank_transfer",
            "cheque",
        ):
            bill.message_post(
                body="Treasury paid bill %s by %s, but its withholding was computed for a bank "
                "payment: the non-bank uplift was not withheld (BRU-APE-08). Raise it with tax."
                % (bill.invoice_ref, execution.method)
            )

    def _excess_paid(self, advance, vals):
        advance._guarded().write(vals)
        advance.claim_ids.filtered(lambda c: c.state == "approved")._guarded().write(
            {"state": "paid"}
        )

    @api.model
    def consume_payment_failed(self, event):
        """The bank rejected the instruction, or returned it after clearing.
        The instruction can still be re-queued by treasury, so nothing else may
        pay the document meanwhile: a bill keeps its lock. A return after
        clearing also takes back this document's clearing entry."""
        execution = self._execution(event)
        if not execution or execution.state != "failed":
            return False
        doc, role, move_field, partner = self._document(execution)
        if not doc:
            return False
        reason = execution.failure_reason or (event.get("payload") or {}).get("reason") or "-"
        vals = {}
        if doc[move_field]:
            label = "Return of %s: %s (%s)" % (doc.display_name, execution.name, reason)
            self._post_clearing(execution, doc, role, partner, label, reverse=True)
            vals[move_field] = False
        if execution.source_model == "fix.expense.claim":
            vals.update({"state": "approved", "payment_failure": reason[:250]})
        elif execution.source_model == "fix.vendor.invoice":
            self.env["fix.ap.bill.payment"].search(
                [("bill_id", "=", doc.id), ("state", "=", "paid"), ("run_line_id", "=", False)]
            ).write({"state": "open"})
            vals.update({"payment_state": "in_run", "payment_failure": reason[:250]})
        if vals:
            doc._guarded().write(vals)
        doc.message_post(
            body="Bank rejected payment %s: %s. Treasury re-queues or cancels the instruction."
            % (execution.name, reason)
        )
        return True
