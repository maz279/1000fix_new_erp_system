# M03 extensions (P06-M07 follow-up): the missing pieces the module always
# promised — POD with OTP, a reachable in_transit state, hub intake, and the
# service-order bridge that left the module with zero consignments while the
# order book held hundreds of pick&drop jobs.
#
# A02 audit (2026-11-03) M03-4/8: the POD code was a plain field the rider
# could read (and type), and a seal mismatch raised an error that rolled back
# its own tamper verdict. The code is now kept only as a keyed hash that no
# workspace user can read, and it is sent to the recipient's phone; the hub
# verdict is recorded and the consignment is put on hold without an error.
import hmac
import logging
import os
import secrets
from datetime import timedelta

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools import misc

from libs.py.fix_events import publish  # FF-28

from .fix_consignment import (
    FROZEN_STATES,
    GROUP_HUB,
    GROUP_MANAGER,
    GROUP_RIDER,
    POD_OTP_TYPES,
    RECEIPT_TYPES,
)

_logger = logging.getLogger(__name__)

POD_HMAC_SCOPE = "cd_consignment.pod_otp"
# A02 ERP audit M03-F20: how many hours after its scheduled dispatch an
# own-fleet leg is promised to arrive. A business figure (OWNER): unset, an
# own-fleet leg is not judged on-time or late.
OWN_FLEET_SLA_PARAM = "cd_consignment.own_fleet_sla_hours"
# FLAW-03.3: the hub scale tolerance (today's value; a policy number).
WEIGHT_TOLERANCE_G = 20.0


def _normalize_bd_phone(phone):
    """``01XXXXXXXXX`` for a valid Bangladesh mobile number, else ``None``."""
    cleaned = "".join(c for c in str(phone or "").strip() if c.isdigit())
    if cleaned.startswith("880"):
        cleaned = "0" + cleaned[3:]
    elif not cleaned.startswith("0") and len(cleaned) == 10:
        cleaned = "0" + cleaned
    if len(cleaned) != 11 or not cleaned.startswith("01"):
        return None
    return cleaned


class FixConsignmentExt(models.Model):
    _inherit = "fix.consignment"

    # A02 audit M03-4: the code itself is never stored. Only its HMAC
    # (keyed with the database secret, so the hash cannot be brute-forced
    # offline) is kept, in a field only system administrators can read.
    pod_otp_hash = fields.Char(string="POD OTP Hash", copy=False, groups="base.group_system")
    pod_otp_issued_at = fields.Datetime(string="POD OTP Issued At", readonly=True, copy=False)
    pod_otp_channel = fields.Char(
        string="POD OTP Sent To",
        readonly=True,
        copy=False,
        help="The masked phone the code was sent to.",
    )
    pod_verified_at = fields.Datetime(string="POD Verified At", readonly=True, copy=False)
    pod_verified_by = fields.Many2one(
        "res.users", string="POD Verified By", readonly=True, copy=False
    )

    # ------------------------------------------------------------ helpers
    def _scan(self, step, **vals):
        """Stamp one custody link from a transition."""
        self.ensure_one()
        return (
            self.env["fix.custody.scan"]
            ._guarded()
            .create(
                {
                    "consignment_id": self.id,
                    "step": step,
                    "device_serial": self.service_order_id.device_serial or "",
                    **vals,
                }
            )
        )

    def _last_step(self):
        self.ensure_one()
        return self._custody_chain()[-1:].step or False

    def _pod_hash(self, code):
        self.ensure_one()
        return misc.hmac(self.env(su=True), POD_HMAC_SCOPE, "%s:%s" % (self.id, str(code).strip()))

    def _pod_recipient_phone(self):
        """The phone the POD code goes to: the customer of the service order
        for a delivery leg, the vendor for a return-to-vendor leg."""
        self.ensure_one()
        partner = self.env["res.partner"]
        if self.consignment_type == "delivery":
            partner = self.service_order_id.sudo().customer_id
        elif self.consignment_type == "return_to_vendor":
            order = self.purchase_order_id.sudo()
            partner = order.vendor_id if "vendor_id" in order._fields else partner
        return _normalize_bd_phone(partner.phone)

    def _pod_send_otp(self, phone, code):
        """Hand the code to the notification dispatcher's SMS channel (the
        same direct path as the customer-portal login OTP, which keeps the
        code out of the outbox). Raises unless it was accepted."""
        from odoo.addons.cd_customer_portal.controllers import otp_delivery

        otp_delivery.send_otp(phone, code, 24 * 3600, "bn")

    # ------------------------------------------------------------ transitions
    def action_start_transit(self):
        """The rider takes custody: stamps the pickup (when the chain is still
        empty) and the departure. The in_transit scan was never recorded
        before (A02 audit: 0 in_transit scans across 24 live chains)."""
        self._logistics_require(GROUP_RIDER, GROUP_HUB, what="Starting transit")
        for consignment in self:
            if consignment.state != "confirmed":
                raise UserError(
                    "Only confirmed consignments can start transit (current: %s)."
                    % consignment.state
                )
            # A02 ERP audit M03-F2: the dispatch gates run again at hand-over
            # (BRU-LOG-12 value, BRU-LOG-03 insurance and countersignature,
            # BRU-LOG-05/10 carrier certification, which may have lapsed)
            if consignment.declared_value_bdt <= 0:
                raise UserError(
                    "%s has no declared value: it cannot leave (BRU-LOG-12)." % consignment.name
                )
            consignment._check_dispatch_controls(confirming=False)
            # in_transit first, so the scans the transition stamps are legal
            consignment._guarded().write({"state": "in_transit"})
            if not consignment.custody_ids:
                consignment._scan("picked_up")
            if consignment._last_step() == "picked_up":
                consignment._scan("in_transit")
        return True

    def action_out_for_delivery(self):
        """The rider leaves for the recipient's door (customer or vendor legs)."""
        self._logistics_require(GROUP_RIDER, GROUP_HUB, what="Marking out for delivery")
        for consignment in self:
            if consignment.consignment_type not in POD_OTP_TYPES:
                raise UserError(
                    "%s ends at one of our branches; it is closed by the receiving hub, "
                    "not taken out for delivery." % consignment.name
                )
            if consignment.state != "in_transit":
                raise UserError(
                    "Only a consignment in transit can go out for delivery (current: %s)."
                    % consignment.state
                )
            if consignment._last_step() != "out_for_delivery":
                consignment._scan("out_for_delivery")
        return True

    def action_generate_otp(self):
        """Issue the delivery OTP to the recipient's phone. One live code at a
        time; regenerating replaces the previous one. The code is never shown
        to the person who issues it (A02 audit M03-4)."""
        self._logistics_require(GROUP_RIDER, GROUP_HUB, what="Issuing the POD code")
        result = {}
        for consignment in self:
            if consignment.consignment_type not in POD_OTP_TYPES:
                raise UserError(
                    "%s ends at one of our branches; the receiving hub confirms receipt "
                    "instead of a POD code." % consignment.name
                )
            if consignment.state != "in_transit":
                raise UserError(
                    "POD OTP is issued for consignments in transit (current: %s)."
                    % consignment.state
                )
            phone = consignment._pod_recipient_phone()
            if not phone:
                raise UserError(
                    "%s has no valid recipient mobile number to send the POD code to. "
                    "Correct the customer's phone first." % consignment.name
                )
            code = "".join(secrets.choice("0123456789") for _ in range(6))
            masked = phone[:3] + "*****" + phone[-3:]
            try:
                consignment._pod_send_otp(phone, code)
            except Exception as exc:
                # DE-11: only the synthetic local environment hands the code
                # back to the caller, as the customer-portal login OTP does.
                if os.environ.get("FIX_ENV") != "local":
                    _logger.warning(
                        "POD OTP for %s not sent (%s)", consignment.name, type(exc).__name__
                    )
                    raise UserError(
                        "The POD code could not be sent to %s. Nothing was issued; try again "
                        "shortly." % masked
                    ) from None
                result = {"dev_code": code}
            consignment._guarded().sudo().write(
                {
                    "pod_otp_hash": consignment._pod_hash(code),
                    "pod_otp_issued_at": fields.Datetime.now(),
                    "pod_otp_channel": masked,
                }
            )
            consignment.message_post(body="POD OTP sent to the recipient (%s)." % masked)
        return result

    def action_verify_pod(self, otp=None):
        """Close delivery with the recipient's OTP: the rider at the door
        enters the code the recipient received by SMS. A correct code stamps
        the terminal 'delivered' custody scan and runs the delivery gate; a
        wrong code refuses and the device stays in custody."""
        self._logistics_require(GROUP_RIDER, GROUP_MANAGER, what="Verifying a POD")
        for consignment in self:
            if consignment.consignment_type not in POD_OTP_TYPES:
                raise UserError(
                    "%s ends at one of our branches; close it with Confirm Receipt at the "
                    "destination hub." % consignment.name
                )
            if consignment.state != "in_transit":
                raise UserError(
                    "Only a consignment in transit can be delivered (%s is %s)."
                    % (consignment.name, consignment.state)
                )
            # A02 audit M03-4: the POD is bound to the assigned rider.
            rider_user = consignment.rider_id.user_id
            if rider_user and rider_user != self.env.user and not self._is_logistics_manager():
                raise UserError(
                    "%s is assigned to %s; only that rider (or a logistics manager) can "
                    "close it." % (consignment.name, consignment.rider_id.name)
                )
            stored = consignment.sudo().pod_otp_hash
            if not stored:
                raise UserError("No POD OTP has been issued for %s." % consignment.name)
            if not otp or not hmac.compare_digest(stored, consignment._pod_hash(otp)):
                raise UserError(
                    "POD OTP mismatch for %s — delivery is refused, the device stays "
                    "in custody." % consignment.name
                )
            if consignment._last_step() != "out_for_delivery":
                raise UserError(
                    "%s is not out for delivery yet; record that step before the hand-over."
                    % consignment.name
                )
            consignment._scan("delivered")
            consignment._guarded().sudo().write(
                {
                    "pod_verified_at": fields.Datetime.now(),
                    "pod_verified_by": self.env.user.id,
                    "pod_otp_hash": False,  # single-use
                }
            )
            consignment.action_deliver()
        return True

    def action_confirm_receipt(self):
        """The receiving hub closes a leg that ends at one of our branches.

        The receipt is the proof of delivery: it needs the hub intake (the
        seal and weight check) and is signed by a hub operator who is not the
        rider who carried it (segregation of duties)."""
        self._logistics_require(GROUP_HUB, what="Confirming receipt at the hub")
        for consignment in self:
            if consignment.consignment_type not in RECEIPT_TYPES:
                raise UserError(
                    "%s ends at the recipient; close it with the recipient's POD code."
                    % consignment.name
                )
            if consignment.state != "in_transit":
                raise UserError(
                    "Only a consignment in transit can be received (%s is %s)."
                    % (consignment.name, consignment.state)
                )
            rider_user = consignment.rider_id.user_id
            if rider_user and rider_user == self.env.user and not self.env.su:
                raise UserError(
                    "Segregation of duties: the rider who carried %s cannot sign its receipt."
                    % consignment.name
                )
            if consignment._last_step() != "hub_scan":
                raise UserError(
                    "%s has no hub intake yet; run the hub intake (seal and weight check) "
                    "before confirming receipt." % consignment.name
                )
            # A02 ERP audit M03-F1: the intake itself, not only its scan
            missing = consignment._hub_intake_missing()
            if missing:
                raise UserError(
                    "%s cannot be received: its hub intake is not complete (%s)."
                    % (consignment.name, missing)
                )
            consignment._scan("delivered", location_branch_id=consignment.dest_branch_id.id)
            consignment._guarded().write(
                {"pod_verified_at": fields.Datetime.now(), "pod_verified_by": self.env.user.id}
            )
            consignment.action_deliver()
        return True

    def _m03_due_at(self):
        """When the leg was promised to arrive, or None (A02 ERP audit
        M03-F20). The scheduled date is the planned dispatch (every create
        path stamps it at creation), so on-time was ~0%. The promise is that
        date plus the courier's contractual SLA, or, for our own riders, the
        own-fleet SLA hours setting (OWNER figure: unset = the leg is not
        judged, never judged late)."""
        self.ensure_one()
        if not self.scheduled_date:
            return None
        hours = 0.0
        if self.courier_partner_id:
            hours = float(self.courier_partner_id.sudo().sla_delivery_hours or 0)
        else:
            raw = self.env["ir.config_parameter"].sudo().get_param(OWN_FLEET_SLA_PARAM)
            try:
                hours = float(raw) if raw not in (None, False, "") else 0.0
            except (TypeError, ValueError):
                hours = 0.0
        if hours <= 0:
            return None
        return self.scheduled_date + timedelta(hours=hours)

    def _hub_intake_missing(self):
        """What the hub intake still lacks, or '' when it is complete
        (A02 ERP audit M03-F1). A hold a logistics manager released, with a
        written reason, stands for the checks it reviewed. Otherwise: the
        seal verified when an outbound seal was fitted, and a receive weight
        within tolerance when a dispatch weight was recorded."""
        self.ensure_one()
        if self.seal_status == "tampered_mismatch":
            return "" if self.hold_released_by_id else "the seal or weight check failed"
        missing = []
        if (self.outbound_seal_number or "").strip() and self.seal_status != "verified":
            missing.append("the inbound seal is not verified")
        if self.dispatch_weight_g > 0:
            if not self.receive_weight_g:
                missing.append("no receive weight")
            elif abs(self.receive_weight_g - self.dispatch_weight_g) > WEIGHT_TOLERANCE_G:
                missing.append("the receive weight is outside tolerance")
        return "; ".join(missing)

    def _hold_for_tamper(self, reason):
        """A02 audit M03-8: record the tamper verdict and stop the
        consignment, without raising — an error here rolled the verdict back
        with itself, so the record kept reading 'intact'."""
        self.ensure_one()
        self._guarded().write(
            {"seal_status": "tampered_mismatch", "state": "held", "hold_reason": reason}
        )
        self.message_post(body="Tamper alert — consignment held: %s" % reason)
        publish(
            self.env,
            "consignment.tamper_detected",
            "fix.consignment",
            self.id,
            {
                "consignment": self.name,
                "reason": reason,
                "outbound_seal": self.outbound_seal_number or "",
                "inbound_seal": self.inbound_seal_number or "",
                "dispatch_weight_g": self.dispatch_weight_g,
                "receive_weight_g": self.receive_weight_g,
            },
        )

    def action_verify_hub_intake(self, inbound_seal=None, receive_weight_g=None):
        """FLAW-03.3: Verify tamper-evident security seal match and scale weight
        variance (±20g tolerance) upon hub/branch arrival.

        A mismatch puts the consignment on exception hold and returns a
        warning; it does not raise (A02 audit M03-8). The inbound seal and
        receive weight are recorded only here, never typed on the form.

        A02 audit M03-P2: the workspace prompts one value per press, so the
        weight gate never ran (P03 could not send a weight). Each press now
        records what it is given (the seal, or the weight in grams) and the
        intake completes - hub scan stamped - once every check the leg needs
        has its value: the seal when an outbound seal was fitted, the weight
        when a dispatch weight was recorded. A recorded seal or weight is
        evidence and is not overwritten with a different value."""
        self._logistics_require(GROUP_HUB, what="Hub intake")
        inbound_seal = (
            str(inbound_seal).strip() if inbound_seal not in (None, False) else ""
        ) or None
        if receive_weight_g in ("", False):
            receive_weight_g = None
        if receive_weight_g is not None:
            try:
                receive_weight_g = float(str(receive_weight_g).strip().rstrip("gG").strip())
            except (TypeError, ValueError):
                raise UserError("The receive weight must be a number of grams.") from None
            if receive_weight_g <= 0:
                raise UserError("The receive weight must be more than 0 grams.")
        warnings = []
        for consignment in self:
            if consignment.state != "in_transit":
                raise UserError(
                    "Hub intake is for consignments in transit (%s is %s)."
                    % (consignment.name, consignment.state)
                )
            vals = {}
            if inbound_seal is not None:
                recorded = (consignment.inbound_seal_number or "").strip()
                if recorded and recorded != inbound_seal:
                    raise UserError(
                        "%s already has inbound seal '%s' recorded; a recorded seal is "
                        "evidence and is not replaced." % (consignment.name, recorded)
                    )
                vals["inbound_seal_number"] = inbound_seal
            if receive_weight_g is not None:
                recorded_g = consignment.receive_weight_g or 0.0
                if recorded_g and abs(recorded_g - receive_weight_g) > 0.005:
                    raise UserError(
                        "%s already has a receive weight of %.1f g recorded; a recorded "
                        "weight is evidence and is not replaced." % (consignment.name, recorded_g)
                    )
                vals["receive_weight_g"] = receive_weight_g
            if vals:
                consignment._guarded().write(vals)

            # A hold a logistics manager released (with a written reason)
            # stands: re-running the intake must not hold the leg again for
            # the verdict that was already reviewed.
            released = (
                consignment.seal_status == "tampered_mismatch" and consignment.hold_released_by_id
            )
            missing = []
            if not released and consignment.outbound_seal_number:
                if not consignment.inbound_seal_number:
                    missing.append(
                        "the inbound seal (outbound seal '%s')" % consignment.outbound_seal_number
                    )
                elif (
                    consignment.inbound_seal_number.strip()
                    != consignment.outbound_seal_number.strip()
                ):
                    reason = (
                        f"FLAW-03.3 Tamper Alert: Inbound seal '{consignment.inbound_seal_number}' "
                        f"does not match outbound seal '{consignment.outbound_seal_number}' "
                        f"on {consignment.name}."
                    )
                    consignment._hold_for_tamper(reason)
                    warnings.append(reason)
                    continue
                elif consignment.seal_status != "verified":
                    consignment._guarded().write({"seal_status": "verified"})

            if not released and consignment.dispatch_weight_g > 0:
                if not consignment.receive_weight_g:
                    missing.append(
                        "the receive weight in grams (dispatched at %.1f g)"
                        % consignment.dispatch_weight_g
                    )
                else:
                    variance = abs(consignment.receive_weight_g - consignment.dispatch_weight_g)
                    if variance > WEIGHT_TOLERANCE_G:
                        reason = (
                            f"FLAW-03.3 Weight Variance Gate: Consignment {consignment.name} "
                            f"scale weight variance is {variance:.1f}g (exceeds "
                            f"±{WEIGHT_TOLERANCE_G:.1f}g security tolerance)."
                        )
                        consignment._hold_for_tamper(reason)
                        warnings.append(reason)
                        continue

            if missing:
                # recorded so far, not raised: the next press supplies the rest
                warnings.append(
                    "%s: hub intake recorded; still needed: %s."
                    % (consignment.name, " and ".join(missing))
                )
                continue

            if not consignment.custody_ids.filtered(lambda s: s.step == "hub_scan"):
                consignment._scan("hub_scan", location_branch_id=consignment.dest_branch_id.id)
            consignment.message_post(
                body=f"Hub intake security seal ({consignment.inbound_seal_number or 'N/A'}) "
                f"and scale weight ({consignment.receive_weight_g or 0.0:.1f} g) verified."
            )
        if warnings:
            return {"warning": " ".join(warnings)}
        return True

    def action_record_receive_weight(self, receive_weight_g=None):
        """The weight half of the hub intake, for the workspace button (it
        prompts one value per press). A02 audit M03-P2."""
        if receive_weight_g in (None, False, ""):
            raise UserError("Enter the receive scale weight in grams.")
        return self.action_verify_hub_intake(receive_weight_g=receive_weight_g)

    def action_release_hold(self, reason=None):
        """A logistics manager releases a consignment from exception hold,
        with a written reason. The tamper verdict stays on the record."""
        self._logistics_require(GROUP_MANAGER, what="Releasing an exception hold")
        reason = (str(reason).strip() if reason else "") or False
        if not reason:
            raise UserError("Give the reason for releasing the hold.")
        for consignment in self:
            if consignment.state != "held":
                raise UserError("%s is not on exception hold." % consignment.name)
            consignment._guarded().write(
                {
                    "state": "in_transit",
                    "hold_released_by_id": self.env.user.id,
                    "hold_released_at": fields.Datetime.now(),
                    "hold_release_reason": reason,
                }
            )
            consignment.message_post(body="Exception hold released: %s" % reason)
            # A02 audit B2: the to-dos the tamper consumer raised are done
            consignment.activity_ids.filtered(
                lambda a, c=consignment: a.summary == "Tamper hold: %s" % c.name
            ).sudo().action_feedback(feedback="Hold released: %s" % reason)
        return True


class FixServiceOrderConsignmentBridge(models.Model):
    _inherit = "fix.service.order"

    consignment_ids = fields.One2many("fix.consignment", "service_order_id", string="Consignments")
    consignment_count = fields.Integer(compute="_compute_consignment_count")

    def _compute_consignment_count(self):
        for order in self:
            order.consignment_count = len(order.consignment_ids)

    def _fix_next_leg_type(self):
        """The next leg of this order's journey (FR-LOG-002: customer ->
        branch -> workshop -> branch -> customer).

        A collection or mail-in order starts with a PICKUP. M03 capture audit
        2026-11-18: the type used to follow the service type alone, so once
        the pickup had arrived, a second press raised another pickup (a rider
        sent for a device already in the shop) and the return DELIVERY could
        not be raised at all. The device is home once a pickup leg is
        delivered; from then on the next leg is the delivery, and only when
        the order is ready to go back. Every other order type is delivered
        to the customer, as before."""
        self.ensure_one()
        if self.service_type not in ("collection", "mail_in"):
            return "delivery"
        arrived = self.consignment_ids.filtered(
            lambda c: c.consignment_type == "pickup" and c.state == "delivered"
        )
        if not arrived and self.state != "ready":
            return "pickup"
        if self.state != "ready":
            raise UserError(
                "Order %s: the device already arrived at the branch (%s). Its return "
                "delivery is raised once the order is ready."
                % (self.name, ", ".join(arrived.mapped("name")))
            )
        return "delivery"

    def action_create_consignment(self):
        """Hand a service order to logistics (M03): raise the next leg of its
        journey (``_fix_next_leg_type``). Collection and mail-in orders get a
        PICKUP (customer -> branch) and, once ready, the DELIVERY back; other
        orders get a DELIVERY leg (branch -> customer). Branch pairing: pickup
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
            ctype = order._fix_next_leg_type()
            if ctype == "pickup":
                origin, dest = False, branch.id
            else:
                origin, dest = branch.id, False
            # M03 audit 2026-11-13: a second press made a second live leg for
            # the same move (two riders sent for one device). A02 ERP audit
            # M03-F3: any live leg, of any type (the model checks it again)
            live = order.consignment_ids.filtered(lambda c: c.state not in FROZEN_STATES)
            if live:
                raise UserError(
                    "Order %s already has a live leg (%s); finish or return it before "
                    "raising another." % (order.name, ", ".join(live.mapped("name")))
                )
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
