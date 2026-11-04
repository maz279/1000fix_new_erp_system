# The M01 hand-backs and the abandoned-device path (A02 audit B2, M01-P2).
#
# Field service (M02), the workshop (M31) and logistics (M03) publish when
# their part of a job is done, and nothing on the order listened: a completed
# field job, a workshop release and a delivered consignment left the order
# where it was. These R8 relay consumers move the order on through its OWN
# transition methods, so every gate still applies.
#
# Payload contract (agreed with streams S2 and S3, the publishers):
#   payload["service_order_id"]  int (or False), the order to move
#   payload["field_order_id"] / ["workshop_job_id"], else aggregate_id:
#                                the source record (field order, job, leg)
# A consumer falls back to the source record's own order link, so it works
# before the publisher sends the key.
#
# Each consumer is superuser-only (consume_* is RPC-reachable), idempotent (an
# order already at or past the target is left alone) and refuses a stale
# state (an order cancelled, or not yet approved, is not moved; the refusal is
# posted on the order, and the event is not retried).
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_service_order import ABANDON_AFTER_DAYS_PARAM, GROUP_SUPERVISOR

logger = logging.getLogger(__name__)

# How far each hand-back takes the order, and the states it is already past.
_PAST_REPAIR = ("qc_pending", "qc_failed", "ready", "delivered", "closed")


class FixServiceOrderHandback(models.Model):
    _inherit = "fix.service.order"

    # ------------------------------------------------------------------ helpers
    def _fix_assert_relay(self):
        if not self.env.su:
            raise AccessError("Service-order event consumers run only from the event relay.")

    @api.model
    def _fix_handback_order(self, event, source_model, link_field, source_key=None):
        """The order an event is about: payload key first, else the source
        record's link (S2/S3 contract above). The source record is the
        payload's own id key (field_order_id, workshop_job_id), else the
        event's aggregate."""
        payload = event.get("payload") or {}
        order_id = payload.get("service_order_id") or payload.get("order_id")
        source = None
        Source = self.env.get(source_model)
        source_id = (payload.get(source_key) if source_key else None) or event.get("aggregate_id")
        if Source is not None and source_id:
            source = Source.sudo().browse(int(source_id)).exists()
        if not order_id and source and link_field in source._fields:
            order_id = source[link_field].id
        order = self.sudo().browse(int(order_id or 0)).exists()
        return order, source

    def _fix_handback_refused(self, what, reason):
        self.ensure_one()
        self.message_post(body="%s: the order was not moved (%s)." % (what, reason))
        return {"moved": False, "reason": reason}

    def _fix_handback_to_qc(self, what):
        """approved -> in_repair -> qc_pending through the order's actions."""
        self.ensure_one()
        if self.state in _PAST_REPAIR:
            return {"moved": False, "reason": "already %s" % self.state}
        if self.state not in ("approved", "in_repair"):
            return self._fix_handback_refused(
                what, "the order is %s, not approved or in repair" % self.state
            )
        try:
            with self.env.cr.savepoint():
                if self.state == "approved":
                    self.action_start_repair()
                self.action_submit_qc()
        except (UserError, ValidationError) as exc:
            return self._fix_handback_refused(what, str(exc))
        return {"moved": True, "state": self.state}

    # ---------------------------------------------------------------- consumers
    @api.model
    def consume_field_order_completed(self, event: dict) -> dict:
        """M02 field job completed on site: the repair is done, so the order
        goes to QC. The completing technician is recorded as the repairer, so
        QC's segregation of duties sees the right person."""
        self._fix_assert_relay()
        order, field_order = self._fix_handback_order(
            event, "fix.field.order", "order_id", "field_order_id"
        )
        if not order:
            return {"moved": False, "reason": "no service order"}
        result = order._fix_handback_to_qc("Field order completed")
        tech_user = field_order.technician_id.user_id if field_order else None
        if result.get("moved") and tech_user:
            order._guarded().write({"repair_completed_by": tech_user.id})
        return result

    @api.model
    def consume_workshop_job_delivered(self, event: dict) -> dict:
        """M31 released the job from the bench: the order goes to QC, and on
        to Ready only if M01's own QC checklist has passed (the workshop's
        QC is not the order's release inspection). M31's own delivery sync
        usually moves the order first; an order already past QC is left
        alone."""
        self._fix_assert_relay()
        order, _job = self._fix_handback_order(
            event, "fix.workshop.job", "order_id", "workshop_job_id"
        )
        if not order:
            return {"moved": False, "reason": "no service order"}
        result = order._fix_handback_to_qc("Workshop job delivered")
        if order.state == "qc_pending":
            checklists = order.qc_checklist_ids
            if checklists and all(c.state == "passed" and c.item_ids for c in checklists):
                try:
                    with self.env.cr.savepoint():
                        order.action_ready()
                    result = {"moved": True, "state": order.state}
                except (UserError, ValidationError) as exc:
                    logger.info("Order %s stays in QC: %s", order.name, exc)
        return result

    @api.model
    def consume_consignment_delivered(self, event: dict) -> dict:
        """M03 leg delivered. A PICKUP leg brought the device in: a draft
        order is taken in, and the 'awaiting pickup' SLA hold lifts. A
        DELIVERY leg handed it to the customer against a verified POD: a
        Ready order is delivered, only once the money is settled or the job
        is zero-charge (the relay is the superuser, so the settlement check
        the delivery gate skips for it is made here)."""
        self._fix_assert_relay()
        order, leg = self._fix_handback_order(event, "fix.consignment", "service_order_id")
        if not order or not leg:
            return {"moved": False, "reason": "no service order or consignment"}
        if leg.consignment_type == "pickup":
            if order.state == "draft":
                order.action_intake()
            elif order.state == "cancelled":
                return order._fix_handback_refused("Pickup delivered", "the order is cancelled")
            order._fix_sync_sla_pause()
            return {"moved": order.state == "intake", "state": order.state}
        if leg.consignment_type != "delivery":
            return {"moved": False, "reason": "a %s leg moves no order" % leg.consignment_type}
        if order.state in ("delivered", "closed"):
            return {"moved": False, "reason": "already %s" % order.state}
        if order.state != "ready":
            return order._fix_handback_refused(
                "Delivery leg %s delivered" % leg.name, "the order is %s, not Ready" % order.state
            )
        if not leg.pod_verified_at:
            return order._fix_handback_refused(
                "Delivery leg %s delivered" % leg.name, "no verified proof of delivery"
            )
        due = order._fix_amount_due()
        if not (
            order._fix_zero_charge_basis()
            or due <= 0
            or order.payment_settlement_state == "credit_approved"
            or order._fix_settlement_covers(due)
        ):
            return order._fix_handback_refused(
                "Delivery leg %s delivered" % leg.name,
                "BDT %.2f is due and no verified settlement covers it" % due,
            )
        try:
            with self.env.cr.savepoint():
                order.action_deliver()
        except (UserError, ValidationError) as exc:
            return order._fix_handback_refused("Delivery leg %s delivered" % leg.name, str(exc))
        order.message_post(
            body="Delivered to the customer by logistics leg %s (POD verified)." % leg.name
        )
        return {"moved": True, "state": order.state}

    # ------------------------------------------------------- abandoned devices
    @api.model
    def _cron_flag_abandoned(self):
        """A02 audit M01-P2: a repaired device left uncollected N days after
        Ready is flagged abandoned, and the branch supervisors get a to-do
        (contact the customer, then cancel with reason 'abandoned' under the
        branch's disposal policy). Off while the switch is 0."""
        try:
            days = int(
                self.env["ir.config_parameter"].sudo().get_param(ABANDON_AFTER_DAYS_PARAM, "0")
            )
        except (TypeError, ValueError):
            days = 0
        if days <= 0:
            return 0
        cutoff = fields.Datetime.now() - timedelta(days=days)
        stale = self.sudo().search(
            [
                ("state", "=", "ready"),
                ("is_abandoned", "=", False),
                "|",
                ("ready_at", "<", cutoff),
                "&",
                ("ready_at", "=", False),
                ("write_date", "<", cutoff),
            ]
        )
        supervisors = self.env.ref(GROUP_SUPERVISOR, raise_if_not_found=False)
        flagged = 0
        for order in stale:
            try:
                with self.env.cr.savepoint():
                    reason = "Uncollected %d days after it was Ready" % days
                    order._guarded().write(
                        {
                            "is_abandoned": True,
                            "abandoned_at": fields.Datetime.now(),
                            "abandon_reason": reason,
                        }
                    )
                    order.message_post(body="Device flagged abandoned: %s." % reason)
                    for user in order._fix_branch_users(supervisors):
                        order.activity_schedule(
                            "mail.mail_activity_data_todo",
                            summary="Abandoned device: %s" % order.name,
                            note=reason,
                            user_id=user.id,
                        )
                    flagged += 1
            except Exception:
                logger.exception("Abandoned flag failed for order %s", order.name)
        return flagged

    def _fix_branch_users(self, group):
        """Active internal holders of ``group`` for this order's company,
        those in the order's operating unit first."""
        self.ensure_one()
        if not group:
            return self.env["res.users"]
        users = group.sudo().all_user_ids.filtered(
            lambda u: u.active and not u.share and self.company_id in u.company_ids
        )
        ou = self.operating_unit_id or self.branch_id.operating_unit_id
        if ou and "operating_unit_ids" in users._fields:
            users = users.filtered(lambda u: ou in u.operating_unit_ids) or users
        return users
