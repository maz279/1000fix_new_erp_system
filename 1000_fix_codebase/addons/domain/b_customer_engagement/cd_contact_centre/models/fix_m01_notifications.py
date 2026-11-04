# Customer notifications for M01 service-order events (A02 audit B2).
#
# estimate.sent and service_order.ready were published and nobody told the
# customer: an estimate waited on a decision the customer did not know was
# due, and a repaired device sat uncollected. These R8 consumers queue a
# transactional SMS through the one exit, fix.notif.delivery.queue(), so the
# consent verdict, the BTRC curfew, the provider and the evidence row all
# apply. Purpose service_updates on a contract basis: the customer asked for
# the repair.
#
# M01 (cd_service_order) is not a dependency of the contact centre, so the
# order is read through the registry, as the answer-SLA engine is.
import logging

from odoo import api, models
from odoo.exceptions import AccessError, ValidationError

logger = logging.getLogger(__name__)

_BODIES = {
    "estimate": {
        "en": "1000FiX: the repair estimate for order {order} is BDT {total}. Reply or "
        "call 16743 to approve it.",
        "bn": "1000FiX: অর্ডার {order}-এর মেরামত খরচের প্রাক্কলন {total} টাকা। অনুমোদনের "
        "জন্য 16743-এ কল করুন।",
    },
    "ready": {
        "en": "1000FiX: your device for order {order} is ready for collection at {branch}. "
        "Bring this message; a handover code will be sent to this phone.",
        "bn": "1000FiX: অর্ডার {order}-এর ডিভাইসটি {branch}-এ সংগ্রহের জন্য প্রস্তুত। "
        "হস্তান্তরের কোড এই নম্বরে পাঠানো হবে।",
    },
}


class FixNotifDeliveryM01(models.Model):
    _inherit = "fix.notif.delivery"

    @api.model
    def _m01_assert_relay(self):
        if not self.env.su:
            raise AccessError("Notification event consumers run only from the event relay.")

    @api.model
    def _m01_notify(self, event, order, kind, values):
        """Queue the SMS once per event (dedup key), or say why not."""
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
                dedup_key="m01-notify:%s:%s" % (kind, event.get("event_id") or order.id),
                operating_unit=order.operating_unit_id or order.branch_id.operating_unit_id,
                company=order.company_id,
            )
        except ValidationError as exc:
            # No phone on file is not worth three retries and a dead letter.
            order.message_post(body="Customer not notified (%s): %s" % (kind, exc))
            return {"queued": False, "reason": str(exc)}
        return {"queued": delivery.state != "suppressed", "delivery_id": delivery.id}

    @api.model
    def consume_estimate_sent(self, event: dict) -> dict:
        """Tell the customer the estimate is waiting on their decision."""
        self._m01_assert_relay()
        Estimate = self.env.get("fix.estimate")
        if Estimate is None:
            return {"queued": False, "reason": "M01 not installed"}
        est = Estimate.sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        if not est or not est.order_id or est.state != "sent":
            return {"queued": False, "reason": "no estimate with the customer"}
        return self._m01_notify(
            event, est.order_id, "estimate", {"total": "%.2f" % (est.grand_total or 0.0)}
        )

    @api.model
    def consume_service_order_ready(self, event: dict) -> dict:
        """Tell the customer the device is ready for collection."""
        self._m01_assert_relay()
        Order = self.env.get("fix.service.order")
        if Order is None:
            return {"queued": False, "reason": "M01 not installed"}
        payload = event.get("payload") or {}
        order_id = payload.get("service_order_id") or event.get("aggregate_id")
        order = Order.sudo().browse(int(order_id or 0)).exists()
        if not order or order.state != "ready":
            return {"queued": False, "reason": "the order is not ready"}
        return self._m01_notify(
            event, order, "ready", {"branch": order.branch_id.name or "the branch"}
        )
