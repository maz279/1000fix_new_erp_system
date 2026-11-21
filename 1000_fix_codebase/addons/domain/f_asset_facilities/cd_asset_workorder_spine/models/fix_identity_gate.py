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


class FixArInvoiceSourceIdentityGate(models.Model):
    _inherit = "fix.ar.invoice"

    @api.model_create_multi
    def create(self, vals_list):
        # A07 ERP audit M17-06 (BRU-AST-03, AUT-AST-02): every invoice raised
        # from a service order, by whatever path (auto-invoice, manual invoice
        # from a proforma, quotation supply), not only the auto-invoice above.
        Order = self.env["fix.service.order"].sudo()
        for vals in vals_list:
            if vals.get("source_model") == "fix.service.order" and vals.get("source_id"):
                order = Order.browse(vals["source_id"]).exists()
                order.device_id.assert_identity_resolved("be invoiced to the customer")
        return super().create(vals_list)


class FixDeviceTransferConsequences(models.Model):
    """M17-18 / owner decision D12: what an ownership change does to the M08
    contract coverage and the M09 protection plans of the device."""

    _inherit = "fix.device"

    def _a07_after_transfer(self, old_owner, new_owner, row):
        super()._a07_after_transfer(old_owner, new_owner, row)
        device = self.sudo()
        new_entity = new_owner.commercial_partner_id
        # M08: a contract of another client no longer covers the device.
        if "fix.contract" in self.env:
            contracts = (
                self.env["fix.contract"].sudo().search([("covered_device_ids", "in", device.ids)])
            )
            for contract in contracts.filtered(
                lambda c: c.customer_id.commercial_partner_id != new_entity
            ):
                writer = contract._guarded() if hasattr(contract, "_guarded") else contract
                writer.write({"covered_device_ids": [(3, device.id)]})
                contract.message_post(
                    body="%s left the covered assets: ownership transfer %s to %s (M17)."
                    % (device.display_name, row.display_name, new_owner.name)
                )
        # M09 (D12): a protection plan follows the device only through the
        # four-eyes M09 warranty transfer; otherwise it lapses at the change.
        Policy = self.env["fix.protection.policy"].sudo()
        policies = Policy.search(
            [("device_id", "=", device.id), ("state", "in", ("sold", "active"))]
        ).filtered(lambda p: p.partner_id.commercial_partner_id != new_entity)
        if self.env.context.get("fix_m09_rehome_policies"):
            for policy in policies:
                policy._guarded().write({"partner_id": new_owner.id})
                policy.message_post(
                    body="Re-homed to %s with M09 warranty transfer (%s)."
                    % (new_owner.name, row.display_name)
                )
        elif policies:
            policies.action_cancel(
                reason="Lapsed at the ownership change %s: a protection plan passes to a new "
                "owner only through an M09 warranty transfer (owner decision D12)."
                % row.display_name
            )


class FixWarrantyTransferCarries(models.Model):
    _inherit = "fix.warranty.transfer"

    def action_effect(self):
        # D12(a): the cover this four-eyes transfer moves is carried to the new
        # owner (and the device's protection plans re-homed), not lapsed.
        for rec in self:
            super(
                FixWarrantyTransferCarries,
                rec.with_context(
                    fix_m09_warranty_ids=rec.warranty_id.ids, fix_m09_rehome_policies=True
                ),
            ).action_effect()
        return True
