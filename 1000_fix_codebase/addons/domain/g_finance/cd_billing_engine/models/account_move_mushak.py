# cd_billing_engine — native sales invoices reach the Mushak register (A08 P2,
# B4 side of the B5 contract).
#
# An Odoo sales invoice (account.move out_invoice) or credit note (out_refund)
# posted outside M20 never reached the VAT register, so the Mushak 9.1 missed
# it (A08 M51-9). When one posts, M51's registration service records it
# (fix.mushak.register._fix_register_from_invoice: idempotent per move, as the
# system). M20's own AR invoices are 'entry' moves whose Mushak 6.3 row is
# written at issue, so they are not registered twice.
from odoo import models


class AccountMoveMushak(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        Register = self.env["fix.mushak.register"]
        register = getattr(Register, "_fix_register_from_invoice", None)
        if register:
            for move in posted.filtered(
                lambda m: m.move_type in ("out_invoice", "out_refund") and m.state == "posted"
            ):
                register(move)
        return posted
