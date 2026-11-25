# M01 quality events reach M23 (A02 ERP pass 2, X5-14, 20 Nov 2026).
#
# M01 publishes service_order.qc_failed (spec §12: consumers M23, M31) and,
# from this pass, rework.detected (M23, M57, M26); M23's own spec lists both
# as its inbound interface ("QC results, rework detection, quality events").
# Nothing consumed them: a failed final QC or a comeback under the repair
# warranty left no nonconformity in the QMS unless a checklist happened to
# be failed by hand, so the nonconformance rate and COPQ read clean.
#
#   * relay only (superuser), like every R8 consumer;
#   * the payload is a claim: the service order is re-read;
#   * idempotent: one NCR per QC-failure event and one per rework order
#     (fix.ncr.relay_key is UNIQUE), however often the relay redelivers;
#   * a QC failure on an order that already has an OPEN QC / service-order
#     NCR (the checklist path raised one, or an earlier iteration did) adds
#     to that NCR instead of stacking a second one.
#
# This file extends fix.ncr, so it loads after fix_qms (models/__init__.py).
from odoo import api, fields, models
from odoo.exceptions import AccessError


class FixNcrA02r2Consumers(models.Model):
    _inherit = "fix.ncr"

    relay_key = fields.Char(
        string="Raised By Event",
        copy=False,
        readonly=True,
        index=True,
        help="The relay fact this NCR was raised from (one NCR per fact).",
    )

    _relay_key_unique = models.Constraint(
        "UNIQUE (relay_key)", "An event raises its nonconformity once."
    )

    @api.model
    def _a02r2_assert_relay(self):
        if not self.env.su:
            raise AccessError("Quality event consumers run only from the event relay.")

    @api.model
    def _a02r2_order(self, order_id):
        Order = self.env.get("fix.service.order")
        if Order is None or not order_id:
            return None
        try:
            return Order.sudo().browse(int(order_id)).exists() or None
        except (TypeError, ValueError):
            return None

    @api.model
    def _a02r2_raise(self, key, order, severity, description):
        ncr = self.sudo().create(
            {
                "source": "service_order",
                "order_id": order.id,
                "severity": severity,
                "company_id": order.company_id.id or self.env.company.id,
                "operating_unit_id": (
                    order.operating_unit_id or order.branch_id.operating_unit_id
                ).id
                or False,
                "description": description,
                "relay_key": key,
            }
        )
        ncr.message_post(body="Raised through the event relay: %s." % key)
        return ncr

    @api.model
    def consume_service_order_qc_failed(self, event: dict) -> dict:
        """service_order.qc_failed -> a minor NCR on the order (an in-house
        catch before delivery), or a note on the open one."""
        self._a02r2_assert_relay()
        payload = event.get("payload") or {}
        order = self._a02r2_order(payload.get("order_id") or event.get("aggregate_id"))
        if not order:
            return {"created": 0, "reason": "no service order"}
        key = "service_order.qc_failed:%s" % (event.get("event_id") or order.id)
        existing = self.sudo().search([("relay_key", "=", key)], limit=1)
        if existing:
            return {"created": 0, "ncr": existing.name, "reason": "already raised"}
        open_ncr = self.sudo().search(
            [
                ("order_id", "=", order.id),
                ("source", "in", ("qc", "service_order")),
                ("state", "!=", "closed"),
            ],
            order="id desc",
            limit=1,
        )
        if open_ncr:
            open_ncr.message_post(
                body="Order %s failed QC again (event %s)." % (order.name, event.get("event_id"))
            )
            return {"created": 0, "ncr": open_ncr.name, "reason": "added to the open NCR"}
        ncr = self._a02r2_raise(
            key,
            order,
            "minor",
            "Final QC failed on service order %s: the repair goes back to the bench." % order.name,
        )
        return {"created": 1, "ncr": ncr.name}

    @api.model
    def consume_rework_detected(self, event: dict) -> dict:
        """rework.detected -> a major NCR: the customer came back with the
        same fault inside the repair warranty. One per rework order."""
        self._a02r2_assert_relay()
        payload = event.get("payload") or {}
        rework_id = payload.get("rework_order_id")
        if not rework_id and event.get("aggregate") in (None, "fix.service.order"):
            rework_id = event.get("aggregate_id")
        rework = self._a02r2_order(rework_id)
        if not rework:
            return {"created": 0, "reason": "no rework order"}
        original = (
            self._a02r2_order(payload.get("original_order_id") or payload.get("rework_of_id"))
            or ("rework_of_id" in rework._fields and rework.rework_of_id)
            or None
        )
        key = "rework.detected:%d" % rework.id
        existing = self.sudo().search([("relay_key", "=", key)], limit=1)
        if existing:
            return {"created": 0, "ncr": existing.name, "reason": "already raised"}
        fault = payload.get("fault") or payload.get("fault_code") or ""
        attribution = payload.get("attribution") or payload.get("attributed_to") or ""
        ncr = self._a02r2_raise(
            key,
            rework,
            "major",
            "Rework: %s came back as %s%s%s."
            % (
                original.name if original else "an earlier repair",
                rework.name,
                (" - fault %s" % fault) if fault else "",
                (", attributed to %s" % attribution) if attribution else "",
            ),
        )
        return {"created": 1, "ncr": ncr.name}
