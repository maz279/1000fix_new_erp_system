# m49_capex_bill — the M52 -> M49 capital-invoice hand-off (A08 M49-3 / M49-10).
#
# A vendor bill against a capital purchase order (fix.purchase.order with a
# capex_request_id) debits the capex's CWIP account instead of an expense, and
# its posted CWIP lines are booked to the capex's CWIP project
# (fix.cwip.entry._fix_book_cost). CWIP cost is therefore the posted cost of
# the PO's bills, never a typed figure.
from odoo import models
from odoo.exceptions import UserError


class FixVendorInvoiceCapex(models.Model):
    _inherit = "fix.vendor.invoice"

    def _fix_capex_cwip(self):
        """The open CWIP project of the bill's capex request (opened on the
        first bill of an approved request), or None for a non-capital bill."""
        self.ensure_one()
        order = self.requisition_id.sudo() if self.requisition_id else None
        req = order.capex_request_id if order and "capex_request_id" in order._fields else None
        if not req:
            return None
        req._fix_assert_approved("Billing capital order %s" % order.name)
        cwip = req.cwip_ids.filtered(lambda w: w.state == "open")[:1]
        if not cwip:
            if req.state != "approved":
                raise UserError(
                    "%s has no open CWIP project to book the bill %s to."
                    % (req.name, self.invoice_ref or self.id)
                )
            cwip = self.env["fix.cwip.entry"].sudo().browse(req.action_create_cwip()["cwip_ids"])
        return cwip.sudo()

    def _expense_account(self, line):
        cwip = self._fix_capex_cwip()
        if cwip:
            return cwip._fix_cwip_account()
        return super()._expense_account(line)

    def _post_approved_bill(self):
        result = super()._post_approved_bill()
        cwip = self._fix_capex_cwip()
        if cwip and self.move_id:
            account = cwip._fix_cwip_account()
            lines = self.move_id.sudo().line_ids.filtered(
                lambda ln: ln.account_id == account and ln.debit
            )
            if lines:
                cwip._fix_book_cost(lines)
        return result
