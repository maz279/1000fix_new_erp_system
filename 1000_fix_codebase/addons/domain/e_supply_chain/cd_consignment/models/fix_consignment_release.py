# A02 ERP audit, pass 2 (20 Nov 2026): what a service-order leg needs before
# the device moves, and the cash a delivery leg collects at the door.
#
# M03-01 (P0) / M03-02 / X5-04, owner decision D1: a repaired device went out
# on a delivery leg unpaid and un-QC'd. The leg was confirmed and started with
# no look at the order; only the M01 hand-back noticed, after the customer
# already had the device. A delivery leg of a service order is now confirmed
# and started only when the order is Ready AND paid / credit-released
# (fix.service.order._fix_delivery_leg_allowed, the M01 rule), OR the leg is a
# cash-on-delivery leg: ``cod_amount`` is the order's amount due, set when the
# leg is raised for an unpaid Ready order. At the verified POD the rider's (or
# courier's) collection is recorded on the order through M01's own settlement
# method (source "cod", tender "cod"): finance books it into COD clearing and
# the rider settlement / courier remittance clears it.
#
# M03-04: a pickup leg left the customer's door with no proof of what was
# collected or from whom. Before a pickup leg of a service order starts
# transit it needs the customer's sign-off (a pickup OTP sent to the
# customer's phone, or a signature image), a package photo, the scanned serial
# (compared with the order's device), and the outbound seal and dispatch
# weight the receiving hub checks.
#
# M03-09: a rider assigned legs to himself. The rider and the courier of a leg
# are a hub decision.
#
# A02 pass 2 review (P2): the outbound seal and dispatch weight of a pickup are
# put on the parcel at the customer's door, after the hub confirmed the leg,
# but the confirmed leg locked them, so the pickup proof could never be
# completed. They stay open on a confirmed pickup leg of a service order and
# lock when transit starts (the receiving hub checks what left the door).
import hmac
import logging
import os
import secrets
from datetime import datetime, time, timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import misc

from libs.py.fix_events import publish  # FF-28

from .fix_consignment import GROUP_HUB, GROUP_MANAGER, GROUP_RIDER
from .fix_consignment_ext import _normalize_bd_phone

_logger = logging.getLogger(__name__)

PICKUP_HMAC_SCOPE = "cd_consignment.pickup_otp"
# M03-04: the pickup proof gate (default on, data record noupdate).
PICKUP_PROOF_PARAM = "cd_consignment.pickup_proof_required"
# M03-08 / D20: an own rider's COD collection is handed in by the end of the
# next business day; after that the rider takes no new COD leg.
COD_HANDIN_DAYS_PARAM = "cd_consignment.cod_handin_business_days"

# what a pickup leg records at the customer's door (open until transit)
PICKUP_DOOR_EVIDENCE = frozenset(
    {"outbound_seal_number", "security_bag_barcode", "dispatch_weight_g"}
)

_RELEASE_GUARDED = frozenset(
    {
        "cod_amount",
        "cod_collected_at",
        "cod_collected_by_id",
        "cod_reference",
        "cod_remitted_at",
        "pickup_otp_issued_at",
        "pickup_otp_channel",
        "pickup_otp_verified_at",
        "pickup_signature_attachment_id",
        "pickup_photo_attachment_id",
        "pickup_serial_scanned",
        "pickup_proof_by_id",
    }
)


def _param_on(env, key, default="1"):
    raw = env["ir.config_parameter"].sudo().get_param(key, default)
    return str(raw if raw is not None else default).strip().lower() in ("1", "true", "yes", "on")


def delivery_release_verdict(order):
    """D1: may the order leave on a prepaid delivery leg? ``(ok, reason)``.
    M01's rule (_fix_delivery_leg_allowed: Ready + paid or credit-released)
    decides when it is installed; this fallback asks the same questions of
    the order.

    A02 pass 2 review B1: M01's rule returns ``(ok, reason)``; reading that
    tuple as a bool made every refusal True, so an unpaid Ready order left on
    a leg collecting nothing. A plain bool is still accepted."""
    order = order.sudo()
    rule = getattr(order, "_fix_delivery_leg_allowed", None)
    if rule is not None:
        result = rule()
        if isinstance(result, tuple | list):
            ok = bool(result[0]) if result else False
            reason = str(result[1] or "") if len(result) > 1 else ""
            return ok, reason
        return bool(result), ""
    if order.state != "ready":
        return False, "order %s is %s, not Ready" % (order.name, order.state)
    due = order._fix_amount_due()
    ok = bool(
        order._fix_zero_charge_basis()
        or due <= 0.005
        or order.payment_settlement_state == "credit_approved"
        or order._fix_settlement_covers(due)
    )
    return ok, ""


def order_released_for_delivery(order) -> bool:
    """D1: the order may leave on a prepaid delivery leg."""
    return delivery_release_verdict(order)[0]


def order_cod_amount(order) -> float:
    """What a cash-on-delivery leg collects: what is still to collect on the
    order - the amount due less every payment already recorded on it (a part
    payment taken on site, D3). Collecting the full amount due again
    over-collected and the order then refused the COD at the door."""
    order = order.sudo()
    outstanding = getattr(order, "_fix_amount_outstanding", None)
    amount = outstanding() if outstanding is not None else order._fix_amount_due()
    return round(max(amount or 0.0, 0.0), 2)


class FixConsignmentRelease(models.Model):
    _inherit = "fix.consignment"

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
    )
    # ------------------------------------------------------------- COD (D1)
    cod_amount = fields.Monetary(
        string="Cash To Collect (COD, BDT)",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The service order's amount due, collected by the rider or courier at the "
        "verified hand-over. Set by the system when the delivery leg is raised for an unpaid "
        "Ready order; zero for a prepaid or credit-released order.",
    )
    cod_collected_at = fields.Datetime(string="COD Collected At", readonly=True, copy=False)
    cod_collected_by_id = fields.Many2one(
        "res.users", string="COD Recorded By", readonly=True, copy=False
    )
    cod_reference = fields.Char(string="COD Reference", readonly=True, copy=False)
    cod_remitted_at = fields.Datetime(
        string="COD Handed In At",
        readonly=True,
        copy=False,
        help="When the rider's settlement or the courier's remittance cleared this collection.",
    )
    # ------------------------------------------------- pickup proof (M03-04)
    pickup_otp_hash = fields.Char(copy=False, groups="base.group_system")
    pickup_otp_issued_at = fields.Datetime(string="Pickup Code Sent At", readonly=True, copy=False)
    pickup_otp_channel = fields.Char(string="Pickup Code Sent To", readonly=True, copy=False)
    pickup_otp_verified_at = fields.Datetime(
        string="Customer Confirmed Pickup At", readonly=True, copy=False
    )
    pickup_signature_attachment_id = fields.Many2one(
        "ir.attachment", string="Customer Signature (Pickup)", readonly=True, copy=False
    )
    pickup_photo_attachment_id = fields.Many2one(
        "ir.attachment", string="Package Photo (Pickup)", readonly=True, copy=False
    )
    pickup_serial_scanned = fields.Char(
        string="Serial Scanned At Pickup", readonly=True, copy=False
    )
    pickup_proof_by_id = fields.Many2one(
        "res.users", string="Pickup Proof Recorded By", readonly=True, copy=False
    )

    # ------------------------------------------------------------------ guard
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | _RELEASE_GUARDED

    def _fix_dispatch_locked(self) -> set:
        locked = super()._fix_dispatch_locked()
        if (
            self.state == "confirmed"
            and self.consignment_type == "pickup"
            and self.service_order_id
        ):
            locked = locked - PICKUP_DOOR_EVIDENCE
        return locked

    def write(self, vals):
        # M03-09: the rider / courier of a leg is a hub decision (a rider
        # assigned legs to himself). The custody lock in fix_consignment
        # still fixes the carrier once the leg is on the road.
        carrier = {"rider_id", "courier_partner_id"} & set(vals)
        if carrier and self and not self._fix_guard_open():
            changed = [
                rec
                for rec in self
                for name in carrier
                if rec._fix_guard_differs(name, vals[name], rec[name])
            ]
            if changed and not self.env.user.has_group(GROUP_HUB):
                raise UserError(
                    "The rider or courier of a consignment is assigned by a Logistics Hub "
                    "Operator, not by the rider."
                )
            if changed and vals.get("rider_id"):
                self._m03_refuse_overdue_cod_rider(vals["rider_id"])
        # M03-09: a rider (who is not also a hub operator) changes only the
        # legs assigned to him: he started transit and closed PODs on other
        # riders' legs of his unit.
        if self and not self.env.su and not self.env.user.has_group(GROUP_HUB):
            foreign = self.filtered(lambda c: c.sudo().rider_id.user_id != self.env.user)
            if foreign and self.env.user.has_group(GROUP_RIDER):
                raise UserError(
                    "%s is not assigned to you: a rider works only his own legs."
                    % ", ".join(foreign.sudo().mapped("name"))
                )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        if (
            not self._fix_guard_open()
            and not self.env.user.has_group(GROUP_HUB)
            and any(vals.get("rider_id") or vals.get("courier_partner_id") for vals in vals_list)
        ):
            raise UserError(
                "The rider or courier of a consignment is assigned by a Logistics Hub "
                "Operator, not by the rider."
            )
        for vals in vals_list:
            if vals.get("rider_id"):
                self._m03_refuse_overdue_cod_rider(vals["rider_id"])
        records = super().create(vals_list)
        for rec in records:
            rec._m03_set_cod_amount()
        return records

    # ------------------------------------------------------------ COD (D1)
    def _m03_is_service_delivery(self) -> bool:
        self.ensure_one()
        return self.consignment_type == "delivery" and bool(self.service_order_id)

    def _m03_set_cod_amount(self):
        """The amount the leg collects: the order's amount due when the order
        is Ready and not otherwise released (D1), else nothing. Re-derived
        while the leg is a draft (the estimate or a payment may change)."""
        for rec in self:
            if not rec._m03_is_service_delivery() or rec.state != "draft":
                continue
            order = rec.service_order_id.sudo()
            amount = 0.0
            if order.state == "ready" and not order_released_for_delivery(order):
                amount = order_cod_amount(order)
            if abs((rec.cod_amount or 0.0) - amount) > 0.005:
                # system-derived (the front desk raising the leg holds no
                # consignment write right)
                rec.sudo()._guarded().write({"cod_amount": amount})

    def _m03_delivery_release_problem(self) -> str:
        """Why this delivery leg may not leave with the device, or ''."""
        self.ensure_one()
        if not self._m03_is_service_delivery():
            return ""
        order = self.service_order_id.sudo()
        if order.state != "ready":
            return (
                "service order %s is %s: a device goes out on a delivery leg only once the "
                "order is Ready (repaired and passed QC)" % (order.name, order.state)
            )
        released, reason = delivery_release_verdict(order)
        if released:
            return ""
        due = order_cod_amount(order)
        if self.cod_amount > 0.005 and abs(self.cod_amount - due) <= 0.005:
            if self.courier_partner_id and not self.courier_partner_id.cod_supported:
                return "courier %s does not collect cash on delivery" % (
                    self.courier_partner_id.name
                )
            return ""
        if self.cod_amount > 0.005:
            return (
                "the leg collects BDT %.2f but BDT %.2f is due on %s now: return the leg and "
                "raise a new one" % (self.cod_amount, due, order.name)
            )
        # M01's own reason says what would release it
        why = " (%s)" % reason.rstrip(".") if reason else ""
        return (
            "BDT %.2f is due on %s and it is neither paid, credit-released nor a "
            "cash-on-delivery leg%s" % (due, order.name, why)
        )

    def _m03_check_delivery_release(self):
        for rec in self:
            problem = rec._m03_delivery_release_problem()
            if problem:
                raise UserError("%s cannot leave: %s (D1)." % (rec.name, problem))

    def action_confirm(self):
        self._m03_set_cod_amount()
        self._m03_check_delivery_release()
        return super().action_confirm()

    def action_start_transit(self):
        self._m03_check_delivery_release()
        self._m03_check_pickup_proof()
        return super().action_start_transit()

    def action_deliver(self):
        # the collection is recorded before the leg closes, so the M01
        # hand-back (consignment.delivered) finds the order paid
        for rec in self:
            rec._m03_record_cod_collection()
        return super().action_deliver()

    def _m03_record_cod_collection(self):
        """D1: at the verified hand-over the rider (or courier) collected the
        COD amount: recorded on the order by M01's own settlement method,
        once. An order that was paid some other way meanwhile collects
        nothing (the door is told so)."""
        self.ensure_one()
        if (
            not self._m03_is_service_delivery()
            or self.cod_amount <= 0.005
            or self.cod_collected_at
            or not self.pod_verified_at
        ):
            return False
        order = self.service_order_id.sudo()
        if order_released_for_delivery(order):
            self.message_post(
                body="No cash collected at the door: %s was paid or credit-released before "
                "the hand-over." % order.name
            )
            self._guarded().write({"cod_amount": 0.0})
            return False
        reference = "COD/%s" % self.name
        # as the system on the rider's behalf (riders hold no order rights);
        # the tender tells finance the cash is in COD clearing, not a drawer
        order.with_context(fd_settlement_tender="cod")._fix_record_settlement(
            self.cod_amount, reference, source="cod"
        )
        now = fields.Datetime.now()
        self._guarded().write(
            {
                "cod_collected_at": now,
                "cod_collected_by_id": self.env.uid,
                "cod_reference": reference,
            }
        )
        self.message_post(
            body="Cash on delivery BDT %.2f collected by %s for %s (%s)."
            % (
                self.cod_amount,
                self.courier_partner_id.name or self.rider_id.name or self.env.user.name,
                order.name,
                reference,
            )
        )
        publish(
            self.env,
            "consignment.cod_collected",
            "fix.consignment",
            self.id,
            {
                "consignment": self.name,
                "service_order_id": order.id,
                "amount_bdt": self.cod_amount,
                "reference": reference,
                "rider_id": self.rider_id.id or False,
                "courier_partner_id": self.courier_partner_id.id or False,
                "collected_at": fields.Datetime.to_string(now),
            },
        )
        return True

    # ------------------------------------------------- COD hand-in (D20)
    @api.model
    def _m03_cod_handin_cutoff(self):
        """Collections before this moment are overdue for hand-in: the end of
        the next business day (Friday is the weekly holiday) after the day of
        collection, in Dhaka."""
        try:
            days = int(
                self.env["ir.config_parameter"].sudo().get_param(COD_HANDIN_DAYS_PARAM, "1") or 1
            )
        except (TypeError, ValueError):
            days = 1
        tz = pytz.timezone("Asia/Dhaka")
        today = datetime.now(tz).date()
        # walk back `days` business days: a collection on that day or earlier
        # had until the end of today at the latest
        day, left = today, days
        while left > 0:
            day -= timedelta(days=1)
            if day.weekday() != 4:  # Friday
                left -= 1
        start_of_day = tz.localize(datetime.combine(day, time.min)).astimezone(pytz.utc)
        return start_of_day.replace(tzinfo=None)

    @api.model
    def _m03_overdue_cod_legs(self, rider):
        legs = self.sudo().search(
            [
                ("rider_id", "=", rider.id),
                ("courier_partner_id", "=", False),
                ("cod_collected_at", "!=", False),
                ("cod_collected_at", "<", self._m03_cod_handin_cutoff()),
                ("cod_remitted_at", "=", False),
            ]
        )
        return legs._m03_not_handed_in()

    def _m03_not_handed_in(self):
        """These legs less those already in a rider's COD settlement that is
        not disputed (cd_cash_position). A02 pass 2 review: a leg the rider
        had handed in (settlement submitted, waiting for its approver) still
        blocked him here, while the settlement's own check had let him go."""
        Settlement = self.env.get("fix.cod.settlement")
        if not self or Settlement is None or "consignment_ids" not in Settlement._fields:
            return self
        handed = (
            Settlement.sudo()
            .search([("state", "!=", "disputed"), ("consignment_ids", "in", self.ids)])
            .mapped("consignment_ids")
        )
        return self - handed

    @api.model
    def _m03_refuse_overdue_cod_rider(self, rider_id):
        """D20 / M03-08: a rider still holding COD cash past the hand-in
        deadline takes no new leg until it is handed in."""
        rider = self.env["hr.employee"].sudo().browse(int(rider_id or 0)).exists()
        if not rider:
            return
        overdue = self._m03_overdue_cod_legs(rider)
        if overdue:
            raise UserError(
                "Rider %s still holds cash on delivery past the hand-in deadline (%s): no new "
                "leg until it is handed in (D20)." % (rider.name, ", ".join(overdue.mapped("name")))
            )

    def _m03_mark_cod_remitted(self):
        """The rider settlement / courier remittance that cleared these
        collections calls this (cd_cash_position)."""
        legs = self.filtered(lambda c: c.cod_collected_at and not c.cod_remitted_at)
        if legs:
            legs._guarded().write({"cod_remitted_at": fields.Datetime.now()})

    @api.model
    def _cron_alert_overdue_cod(self):
        """D20: the logistics manager and finance hear of COD cash held past
        the hand-in deadline, once per leg."""
        legs = (
            self.sudo()
            .search(
                [
                    ("courier_partner_id", "=", False),
                    ("cod_collected_at", "!=", False),
                    ("cod_collected_at", "<", self._m03_cod_handin_cutoff()),
                    ("cod_remitted_at", "=", False),
                ]
            )
            ._m03_not_handed_in()
        )
        groups = [
            self.env.ref(GROUP_MANAGER, raise_if_not_found=False),
            self.env.ref("account.group_account_manager", raise_if_not_found=False),
        ]
        users = self.env["res.users"]
        for group in groups:
            if group:
                users |= group.sudo().all_user_ids.filtered(lambda u: u.active and not u.share)
        alerted = 0
        for leg in legs:
            summary = "COD overdue: %s" % leg.name
            if leg.activity_ids.filtered(lambda a, s=summary: a.summary == s):
                continue
            for user in users:
                leg.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary=summary,
                    note="Rider %s collected BDT %.2f on %s and has not handed it in (D20)."
                    % (leg.rider_id.name, leg.cod_amount, leg.cod_collected_at),
                    user_id=user.id,
                )
            alerted += 1
        return alerted

    # ------------------------------------------------- pickup proof (M03-04)
    def _m03_pickup_proof_missing(self):
        """What a pickup leg of a service order still lacks before the rider
        takes the device away, in plain words (empty = complete)."""
        self.ensure_one()
        if self.consignment_type != "pickup" or not self.service_order_id:
            return []
        if not _param_on(self.env, PICKUP_PROOF_PARAM, "1"):
            return []
        missing = []
        if not (self.pickup_otp_verified_at or self.pickup_signature_attachment_id):
            missing.append("the customer's sign-off (pickup code or signature)")
        if not self.pickup_photo_attachment_id:
            missing.append("a photo of the package")
        serial = (self.service_order_id.sudo().device_serial or "").strip()
        if serial and not self.pickup_serial_scanned:
            missing.append("the device serial scanned at the door")
        if not (self.outbound_seal_number or "").strip():
            missing.append("the outbound seal number")
        if not self.dispatch_weight_g:
            missing.append("the dispatch weight in grams")
        return missing

    def _m03_check_pickup_proof(self):
        for rec in self:
            if rec.state != "confirmed":
                # not at the door yet (or already gone): the transit itself
                # refuses a leg that is not confirmed, with its own reason
                continue
            missing = rec._m03_pickup_proof_missing()
            if missing:
                raise UserError(
                    "%s cannot leave the customer's door without %s (M03-04)."
                    % (rec.name, "; ".join(missing))
                )

    def _m03_require_pickup_leg(self, what):
        self._logistics_require(GROUP_RIDER, GROUP_HUB, what=what)
        for rec in self:
            if rec.consignment_type != "pickup" or not rec.service_order_id:
                raise UserError("%s is not a pickup from a customer." % rec.name)
            if rec.state != "confirmed":
                raise UserError(
                    "The pickup proof of %s is recorded at the customer's door, before transit "
                    "(it is %s)." % (rec.name, rec.state)
                )
            rider_user = rec.rider_id.user_id
            if (
                rider_user
                and rider_user != self.env.user
                and not self.env.user.has_group(GROUP_HUB)
            ):
                raise UserError("%s is assigned to %s." % (rec.name, rec.rider_id.name))

    def _pickup_hash(self, code):
        self.ensure_one()
        return misc.hmac(
            self.env(su=True), PICKUP_HMAC_SCOPE, "%s:%s" % (self.id, str(code).strip())
        )

    def action_send_pickup_otp(self):
        """Send the customer a one-time code that confirms the hand-over of
        the device to the rider. Never shown to the rider."""
        self._m03_require_pickup_leg("Sending the pickup code")
        result = {}
        for rec in self:
            phone = rec._pod_recipient_phone_pickup()
            if not phone:
                raise UserError(
                    "%s: the customer has no valid mobile number for the pickup code; take "
                    "the customer's signature instead." % rec.name
                )
            code = "".join(secrets.choice("0123456789") for _ in range(6))
            masked = phone[:3] + "*****" + phone[-3:]
            try:
                rec._pod_send_otp(phone, code)
            except Exception as exc:
                if os.environ.get("FIX_ENV") != "local":
                    _logger.warning(
                        "pickup code for %s not sent (%s)", rec.name, type(exc).__name__
                    )
                    raise UserError(
                        "The pickup code could not be sent to %s; try again or take the "
                        "customer's signature." % masked
                    ) from None
                result = {"dev_code": code}
            rec._guarded().sudo().write(
                {
                    "pickup_otp_hash": rec._pickup_hash(code),
                    "pickup_otp_issued_at": fields.Datetime.now(),
                    "pickup_otp_channel": masked,
                }
            )
        return result

    def _pod_recipient_phone_pickup(self):
        return _normalize_bd_phone(self.service_order_id.sudo().customer_id.phone)

    def action_verify_pickup_otp(self, otp=None):
        self._m03_require_pickup_leg("Confirming the pickup code")
        for rec in self:
            stored = rec.sudo().pickup_otp_hash
            if not stored:
                raise UserError("No pickup code was sent for %s." % rec.name)
            if not otp or not hmac.compare_digest(stored, rec._pickup_hash(otp)):
                raise UserError("Pickup code mismatch for %s." % rec.name)
            rec._guarded().sudo().write(
                {
                    "pickup_otp_verified_at": fields.Datetime.now(),
                    "pickup_otp_hash": False,
                    "pickup_proof_by_id": self.env.uid,
                }
            )
        return True

    def action_attach_pickup_evidence(self, attachment_id=None, kind="photo"):
        """Link the customer's signature image or the package photo, uploaded
        on this consignment, as pickup proof."""
        self._m03_require_pickup_leg("Recording pickup proof")
        kind = (kind or "photo").strip().lower()
        if kind not in ("photo", "signature"):
            raise UserError("Pickup evidence is a 'photo' or a 'signature'.")
        attachment = self.env["ir.attachment"].sudo().browse(int(attachment_id or 0)).exists()
        if not attachment:
            raise UserError("Upload the image on the consignment first.")
        if not (attachment.mimetype or "").startswith("image/") or not attachment.file_size:
            raise UserError("Pickup evidence is an image.")
        for rec in self:
            if attachment.res_model != rec._name or attachment.res_id != rec.id:
                raise UserError("Upload the image on %s itself." % rec.name)
            field = (
                "pickup_signature_attachment_id"
                if kind == "signature"
                else "pickup_photo_attachment_id"
            )
            if rec[field] and rec[field] != attachment:
                raise UserError("%s already has its pickup %s recorded." % (rec.name, kind))
            rec._guarded().write({field: attachment.id, "pickup_proof_by_id": self.env.uid})
        return True

    def action_scan_pickup_serial(self, serial=None):
        """The serial read off the device at the door must be the order's."""
        self._m03_require_pickup_leg("Scanning the device at pickup")
        serial = (str(serial).strip() if serial else "") or ""
        if not serial:
            raise UserError("Scan or type the serial on the device.")
        for rec in self:
            expected = (rec.service_order_id.sudo().device_serial or "").strip()
            if expected and serial.upper() != expected.upper():
                raise UserError(
                    "Serial %s does not match the device of %s (%s): do not take this device."
                    % (serial, rec.service_order_id.sudo().name, expected)
                )
            rec._guarded().write(
                {"pickup_serial_scanned": serial, "pickup_proof_by_id": self.env.uid}
            )
        return True
