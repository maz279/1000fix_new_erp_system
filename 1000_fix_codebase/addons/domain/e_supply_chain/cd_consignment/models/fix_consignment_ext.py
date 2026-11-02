# M03 extensions (P06-M07 follow-up): the missing pieces the module always
# promised — POD with OTP, a reachable in_transit state, a guarded confirm,
# and the service-order bridge that left the module with zero consignments
# while the order book held hundreds of pick&drop jobs.
import secrets

from odoo import fields, models
from odoo.exceptions import UserError


class FixConsignmentExt(models.Model):
    _inherit = "fix.consignment"

    # POD with OTP (the module header promised it; no OTP existed anywhere)
    pod_otp = fields.Char(
        string="POD OTP",
        copy=False,
        help="Six-digit one-time code shown to the customer at hand-over; "
        "the rider enters it to close delivery.",
    )
    pod_verified_at = fields.Datetime(string="POD Verified At", readonly=True, copy=False)
    pod_verified_by = fields.Many2one(
        "res.users", string="POD Verified By", readonly=True, copy=False
    )

    def action_confirm(self):
        """Guarded confirm: only drafts confirm (the old body accepted any
        state, so a delivered consignment could be 're-confirmed')."""
        for consignment in self:
            if consignment.state != "draft":
                raise UserError(
                    "Only draft consignments can be confirmed (current: %s)." % consignment.state
                )
            consignment.state = "confirmed"

    def action_start_transit(self):
        """The reachable in_transit transition — the state existed in the
        selection but no action ever set it. Requires confirmation and stamps
        the first custody link when the chain is still empty."""
        Scan = self.env["fix.custody.scan"]
        for consignment in self:
            if consignment.state != "confirmed":
                raise UserError(
                    "Only confirmed consignments can start transit (current: %s)."
                    % consignment.state
                )
            if not consignment.custody_ids:
                Scan.create(
                    {
                        "consignment_id": consignment.id,
                        "step": "picked_up",
                        "device_serial": consignment.service_order_id.device_serial or "",
                    }
                )
            consignment.state = "in_transit"

    def action_generate_otp(self):
        """Issue the delivery OTP. One live code at a time; regenerating
        invalidates the previous by replacement."""
        for consignment in self:
            if consignment.state not in ("in_transit", "confirmed"):
                raise UserError(
                    "POD OTP is issued for consignments in transit (current: %s)."
                    % consignment.state
                )
            consignment.pod_otp = "".join(secrets.choice("0123456789") for _ in range(6))
            consignment.message_post(
                body="POD OTP issued to the customer for hand-over verification."
            )
        return True

    def action_verify_pod(self, otp=None):
        """Close delivery with the customer's OTP. A correct code stamps the
        terminal 'delivered' custody scan (the chain's own POD evidence) and
        runs the guarded action_deliver; a wrong code refuses and stays put."""
        Scan = self.env["fix.custody.scan"]
        for consignment in self:
            if not consignment.pod_otp:
                raise UserError("No POD OTP has been issued for %s." % consignment.name)
            if not otp or str(otp).strip() != consignment.pod_otp:
                raise UserError(
                    "POD OTP mismatch for %s — delivery is refused, the device stays "
                    "in custody." % consignment.name
                )
            last = consignment.custody_ids.sorted("scanned_at")[-1:]
            if not last or last.step != "out_for_delivery":
                # the chain must reach out_for_delivery before the POD close;
                # stamp it now (the rider IS at the door with the customer)
                Scan.create(
                    {
                        "consignment_id": consignment.id,
                        "step": "out_for_delivery",
                        "device_serial": consignment.service_order_id.device_serial or "",
                    }
                )
            Scan.create(
                {
                    "consignment_id": consignment.id,
                    "step": "delivered",
                    "device_serial": consignment.service_order_id.device_serial or "",
                }
            )
            consignment.pod_verified_at = fields.Datetime.now()
            consignment.pod_verified_by = consignment.env.user.id
            consignment.pod_otp = False  # single-use
            consignment.action_deliver()

    def action_report_lost(self):
        for consignment in self:
            if consignment.state in ("delivered", "returned"):
                raise UserError(
                    "%s is already %s — it cannot be reported lost."
                    % (consignment.name, consignment.state)
                )
        return super().action_report_lost()

    def action_verify_hub_intake(self, inbound_seal=None, receive_weight_g=None):
        """FLAW-03.3: Verify tamper-evident security seal match and scale weight
        variance (±20g tolerance) upon hub/branch arrival."""
        Scan = self.env["fix.custody.scan"]
        for consignment in self:
            if inbound_seal is not None:
                consignment.inbound_seal_number = inbound_seal
            if receive_weight_g is not None:
                consignment.receive_weight_g = float(receive_weight_g)

            if consignment.outbound_seal_number:
                if not consignment.inbound_seal_number:
                    raise UserError(
                        f"FLAW-03.3 Security Seal Gate: Consignment {consignment.name} requires "
                        "an Inbound Security Seal scan to verify against Outbound Seal "
                        f"'{consignment.outbound_seal_number}'."
                    )
                if (
                    consignment.inbound_seal_number.strip()
                    != consignment.outbound_seal_number.strip()
                ):
                    consignment.seal_status = "tampered_mismatch"
                    raise UserError(
                        f"FLAW-03.3 Tamper Alert: Inbound seal '{consignment.inbound_seal_number}' "
                        f"does not match outbound seal '{consignment.outbound_seal_number}' on {consignment.name}!"
                    )
                consignment.seal_status = "verified"

            if consignment.dispatch_weight_g > 0 and consignment.receive_weight_g > 0:
                variance = abs(consignment.receive_weight_g - consignment.dispatch_weight_g)
                if variance > 20.0:
                    consignment.seal_status = "tampered_mismatch"
                    raise UserError(
                        f"FLAW-03.3 Weight Variance Gate: Consignment {consignment.name} scale weight "
                        f"variance is {variance:.1f}g (exceeds ±20.0g security tolerance)."
                    )

            existing_hub = consignment.custody_ids.filtered(lambda s: s.step == "hub_scan")
            if not existing_hub:
                Scan.create(
                    {
                        "consignment_id": consignment.id,
                        "step": "hub_scan",
                        "location_branch_id": consignment.dest_branch_id.id
                        if consignment.dest_branch_id
                        else False,
                        "device_serial": consignment.service_order_id.device_serial
                        if consignment.service_order_id
                        else "",
                    }
                )
            consignment.message_post(
                body=f"Hub intake security seal ({consignment.inbound_seal_number or 'N/A'}) and scale weight verified."
            )


class FixServiceOrderConsignmentBridge(models.Model):
    _inherit = "fix.service.order"

    consignment_ids = fields.One2many("fix.consignment", "service_order_id", string="Consignments")
    consignment_count = fields.Integer(compute="_compute_consignment_count")

    def _compute_consignment_count(self):
        for order in self:
            order.consignment_count = len(order.consignment_ids)

    def action_create_consignment(self):
        """Hand a service order to logistics (M03). Collection and mail-in
        orders get a PICKUP (customer -> branch); an order entering delivery
        gets a DELIVERY leg (branch -> customer). Branch pairing: pickup
        originates at the customer's nearest... no origin branch exists for a
        customer, so pickup runs branch-to-branch to the ORDER branch as
        destination; delivery originates at the order branch."""
        Consignment = self.env["fix.consignment"]
        created = Consignment
        for order in self:
            if order.state in ("closed", "cancelled"):
                raise UserError(
                    "Order %s is %s — no new logistics legs." % (order.name, order.state)
                )
            branch = order.branch_id
            if not branch:
                raise UserError("Order %s has no branch for a logistics leg." % order.name)
            if order.service_type in ("collection", "mail_in"):
                ctype, origin, dest = "pickup", False, branch.id
            else:
                ctype, origin, dest = "delivery", branch.id, False
            ou = order.operating_unit_id or branch.operating_unit_id
            created |= Consignment.create(
                {
                    "consignment_type": ctype,
                    "scheduled_date": fields.Datetime.now(),
                    "origin_branch_id": origin,
                    "dest_branch_id": dest,
                    "service_order_id": order.id,
                    "operating_unit_id": ou.id,
                }
            )
        return created
