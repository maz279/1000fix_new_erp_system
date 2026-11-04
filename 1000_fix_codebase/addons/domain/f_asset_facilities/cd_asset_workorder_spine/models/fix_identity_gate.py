# fix_identity_gate — A07 P1 bridge: M17 BRU-AST-03 on the M01 invoice and the
# M09 warranty claim.
#
# M17 (A07 P2) provides fix.device.assert_identity_resolved(): a provisional
# identity (identified incompletely at intake) is usable for intake and
# diagnosis, and reaches no customer invoice and no warranty claim until it is
# confirmed. M17 calls it on warranty verification; the two downstream paths
# are gated here, because neither M01 nor M09 depends on the new method. The
# identity state is read as superuser: a claim clerk may lack device read
# rights in another company, and the gate must not turn into an AccessError.
from odoo import api, models


class FixArInvoiceIdentityGate(models.Model):
    _inherit = "fix.ar.invoice"

    @api.model
    def from_closed_service_order(self, order, closed_event_at):
        # the auto-invoice of a closed M01 job (T02); idempotent re-calls return
        # the existing invoice, which the gate does not block
        existing = self.search(
            [("source_model", "=", "fix.service.order"), ("source_id", "=", order.id)]
        )
        if not existing:
            order.device_id.sudo().assert_identity_resolved("be invoiced to the customer")
        return super().from_closed_service_order(order, closed_event_at)


class FixWarrantyClaimIdentityGate(models.Model):
    _inherit = "fix.warranty.claim"

    @api.model_create_multi
    def create(self, vals_list):
        claims = super().create(vals_list)
        # A07 P1 wiring (2026-11-04): read the device link itself as superuser
        # too (it reaches through the service order, possibly in another company)
        claims.sudo().mapped("device_id").assert_identity_resolved("be claimed under warranty")
        return claims

    def action_submit(self):
        self.sudo().mapped("device_id").assert_identity_resolved("be claimed under warranty")
        return super().action_submit()
