# Customer notifications for the A02 service milestones (A02 ERP review,
# 20 Nov 2026).
#
# The specs split the work: "M01 / M02 / M03 raise events; M27 chooses
# channel, language and timing". Of the customer milestones they name
# (NT-001 event matrix; AUT-FSM-04, FR-FSM-037, AUT-LOG-03/05/06), only
# "estimate sent" and "ready for collection" reached the customer
# (fix_m01_notifications). A booked order, a technician on the way, a missed
# visit, a device collected from home or delivered back, a parcel returned
# to the branch, a cancelled order: the events were published and nobody was
# told. These R8 consumers queue the SMS through the one exit,
# fix.notif.delivery.queue(), so consent, the BTRC curfew, the provider and
# the evidence row apply exactly as for the M01 messages, and one event
# queues one message (dedup key).
#
# The A02 modules are not dependencies of the contact centre, so their
# records are read through the registry, as fix_m01_notifications does.
from odoo import api, models
from odoo.exceptions import ValidationError

_BODIES = {
    "received": {
        "en": "1000FiX: we have received your device for order {order} at {branch}. "
        "Call 16743 with this order number for its status.",
        "bn": "1000FiX: অর্ডার {order}-এর ডিভাইসটি {branch}-এ গ্রহণ করা হয়েছে। অবস্থা জানতে "
        "এই অর্ডার নম্বরসহ 16743-এ কল করুন।",
    },
    "cancelled": {
        "en": "1000FiX: order {order} has been cancelled. Any payment due back to you is "
        "refunded by the way you paid; call 16743 with questions.",
        "bn": "1000FiX: অর্ডার {order} বাতিল করা হয়েছে। ফেরতযোগ্য অর্থ যে মাধ্যমে পরিশোধ "
        "করেছেন সেভাবেই ফেরত দেওয়া হবে; প্রশ্নের জন্য 16743-এ কল করুন।",
    },
    "on_the_way": {
        "en": "1000FiX: technician {technician} is on the way for order {order}.",
        "bn": "1000FiX: অর্ডার {order}-এর জন্য টেকনিশিয়ান {technician} রওনা হয়েছেন।",
    },
    "visit_failed": {
        "en": "1000FiX: our technician could not complete the visit for order {order}. "
        "We will call you to arrange a new time, or call 16743.",
        "bn": "1000FiX: অর্ডার {order}-এর ভিজিট সম্পন্ন করা যায়নি। নতুন সময় ঠিক করতে আমরা "
        "আপনাকে কল করব, অথবা 16743-এ কল করুন।",
    },
    "collected": {
        "en": "1000FiX: your device for order {order} has reached our service centre. "
        "We will send the estimate after diagnosis.",
        "bn": "1000FiX: অর্ডার {order}-এর ডিভাইসটি আমাদের সার্ভিস সেন্টারে পৌঁছেছে। "
        "পরীক্ষার পর খরচের প্রাক্কলন পাঠানো হবে।",
    },
    "delivered": {
        "en": "1000FiX: your device for order {order} has been delivered. Thank you for "
        "choosing 1000FiX.",
        "bn": "1000FiX: অর্ডার {order}-এর ডিভাইসটি আপনার কাছে পৌঁছে দেওয়া হয়েছে। 1000FiX "
        "বেছে নেওয়ার জন্য ধন্যবাদ।",
    },
    "returned": {
        "en": "1000FiX: we could not deliver the device for order {order}; it is back at "
        "{branch}. Call 16743 to arrange delivery or collection.",
        "bn": "1000FiX: অর্ডার {order}-এর ডিভাইসটি পৌঁছে দেওয়া যায়নি; এটি {branch}-এ ফেরত "
        "আছে। ডেলিভারি বা সংগ্রহের জন্য 16743-এ কল করুন।",
    },
}


class FixNotifDeliveryA02(models.Model):
    _inherit = "fix.notif.delivery"

    @api.model
    def _a02_notify(self, event, order, kind, values=None):
        """Queue ``kind`` for the order's customer once per event, or say why
        not (the M01 helper's rules: no customer, no phone)."""
        self._m01_assert_relay()
        values = dict(values or {})
        values.setdefault("branch", order.branch_id.name or "the branch")
        partner = order.customer_id
        if not partner:
            return {"queued": False, "reason": "the order has no customer"}
        language = self._preferred_language(partner)
        body = _BODIES[kind].get(language) or _BODIES[kind]["en"]
        try:
            delivery = self.queue(
                channel="sms",
                purpose="service_updates",
                partner=partner,
                body=body.format(order=order.name, **values),
                lawful_basis="contract",
                source_model=order._name,
                source_id=order.id,
                source_event_id=event.get("event_id"),
                dedup_key="a02-notify:%s:%s" % (kind, event.get("event_id") or order.id),
                operating_unit=order.operating_unit_id or order.branch_id.operating_unit_id,
                company=order.company_id,
            )
        except ValidationError as exc:
            # no phone on file is not worth three retries and a dead letter
            order.message_post(body="Customer not notified (%s): %s" % (kind, exc))
            return {"queued": False, "reason": str(exc)}
        return {"queued": delivery.state != "suppressed", "delivery_id": delivery.id}

    @api.model
    def _a02_order(self, order_id):
        Order = self.env.get("fix.service.order")
        if Order is None or not order_id:
            return None
        return Order.sudo().browse(int(order_id)).exists() or None

    # ------------------------------------------------------------------ M01
    @api.model
    def consume_service_order_intake(self, event: dict) -> dict:
        """The order is booked: the customer gets its number (NT booking_received)."""
        self._m01_assert_relay()
        payload = event.get("payload") or {}
        order = self._a02_order(payload.get("service_order_id") or event.get("aggregate_id"))
        if not order or order.state in ("draft", "cancelled"):
            return {"queued": False, "reason": "the order is not booked"}
        return self._a02_notify(event, order, "received")

    @api.model
    def consume_service_order_cancelled(self, event: dict) -> dict:
        self._m01_assert_relay()
        payload = event.get("payload") or {}
        order = self._a02_order(payload.get("service_order_id") or event.get("aggregate_id"))
        if not order or order.state != "cancelled":
            return {"queued": False, "reason": "the order is not cancelled"}
        return self._a02_notify(event, order, "cancelled")

    # ------------------------------------------------------------------ M02
    @api.model
    def consume_field_order_en_route(self, event: dict) -> dict:
        """AUT-FSM-04: the technician departs."""
        self._m01_assert_relay()
        payload = event.get("payload") or {}
        order = self._a02_order(payload.get("service_order_id"))
        if not order:
            return {"queued": False, "reason": "no service order"}
        return self._a02_notify(
            event,
            order,
            "on_the_way",
            {"technician": payload.get("technician_name") or "our technician"},
        )

    @api.model
    def consume_visit_failed(self, event: dict) -> dict:
        """FR-FSM-037: a missed visit is followed up with the customer."""
        self._m01_assert_relay()
        FieldOrder = self.env.get("fix.field.order")
        payload = event.get("payload") or {}
        field_order = (
            FieldOrder.sudo().browse(int(payload.get("field_order_id") or 0)).exists()
            if FieldOrder is not None
            else None
        )
        if not field_order or not field_order.order_id:
            return {"queued": False, "reason": "no service order"}
        return self._a02_notify(event, field_order.order_id.sudo(), "visit_failed")

    # ------------------------------------------------------------------ M03
    @api.model
    def consume_consignment_delivered(self, event: dict) -> dict:
        """AUT-LOG-03: a pickup leg delivered to the centre, or the device
        delivered back to the customer."""
        self._m01_assert_relay()
        payload = event.get("payload") or {}
        kind = {"pickup": "collected", "delivery": "delivered"}.get(payload.get("consignment_type"))
        if not kind:
            return {"queued": False, "reason": "not a customer leg"}
        order = self._a02_order(payload.get("service_order_id"))
        if not order:
            return {"queued": False, "reason": "no service order"}
        return self._a02_notify(event, order, kind)

    @api.model
    def consume_consignment_returned(self, event: dict) -> dict:
        """AUT-LOG-06: delivery attempts exhausted, the device is back."""
        self._m01_assert_relay()
        payload = event.get("payload") or {}
        if payload.get("consignment_type") != "delivery":
            return {"queued": False, "reason": "not a delivery to the customer"}
        order = self._a02_order(payload.get("service_order_id"))
        if not order:
            return {"queued": False, "reason": "no service order"}
        return self._a02_notify(event, order, "returned")
