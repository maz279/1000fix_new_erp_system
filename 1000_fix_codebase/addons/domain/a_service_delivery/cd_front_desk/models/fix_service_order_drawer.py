# M01 counter settlements into the M04 cash drawer (A02 audit M04-P2, M04-4).
#
# A Service Order Cashier's counter settlement was recorded on the order and
# verified at once, "accountable in the cash shift", but nothing reached the
# shift: the drawer's expected closing never included order cash, so a
# shortage of exactly that money balanced. The settlement now posts to the
# branch's open shift. cd_front_desk depends on cd_service_order, so the hook
# lives here and the order module needs no knowledge of the drawer.
from odoo import fields, models
from odoo.exceptions import UserError

# What happens to counter cash when the branch has no open shift. The settlement
# is refused, so cash is never taken outside a drawer: that is the default, and
# what an ABSENT parameter means (it was "0", and the parameter is shipped
# nowhere, so the control was off everywhere). An explicit "0" is a branch's
# own choice: the cash is recorded on the order's chatter and posts nothing.
ORDER_CASH_REQUIRES_SHIFT_PARAM = "cd_front_desk.order_cash_requires_open_shift"


def fd_cash_requires_shift(env) -> bool:
    raw = env["ir.config_parameter"].sudo().get_param(ORDER_CASH_REQUIRES_SHIFT_PARAM, "1")
    return str(raw).strip().lower() not in ("0", "false", "no", "off")


class FixServiceOrderDrawer(models.Model):
    _inherit = "fix.service.order"

    counter_shift_id = fields.Many2one(
        "fix.cash.shift",
        string="Counter Cash Shift",
        readonly=True,
        copy=False,
        index=True,
        help="The branch cash shift the counter settlement was posted to.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"counter_shift_id"}

    def _fix_record_settlement(self, amount_bdt, reference, source):
        result = super()._fix_record_settlement(amount_bdt, reference, source)
        if source == "counter":
            self._fd_post_counter_cash()
        return result

    def _fd_post_counter_cash(self):
        """Post the counter settlement to the branch's open cash shift."""
        self.ensure_one()
        Shift = self.env["fix.cash.shift"]
        shift = Shift._fd_open_shift_for(self.branch_id, self.company_id or self.env.company)
        amount = self.amount_settled_bdt or 0.0
        if not shift:
            if fd_cash_requires_shift(self.env):
                raise UserError(
                    "Branch %s has no open cash shift to take the counter payment for %s. "
                    "Open the cash shift first." % (self.branch_id.display_name, self.name)
                )
            self.message_post(
                body="Counter settlement of BDT %.2f taken with no open cash shift at %s: "
                "it is not in any drawer." % (amount, self.branch_id.display_name)
            )
            return False
        shift._post_cash_movement("cash_payments", amount)
        self._guarded().write({"counter_shift_id": shift.id})
        shift.message_post(
            body="Counter settlement %s: BDT %.2f for order %s."
            % (self.invoice_ref or "", amount, self.name)
        )
        return shift
