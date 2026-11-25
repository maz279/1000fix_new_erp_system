# fix_event_relay — deliver outbox events to the in-Odoo consumers (A03 audit R8).
#
# The outbox was written faithfully and read by nobody: 26,192 events pending
# against 9 published on fix_dev, so every cross-module hand-off (a merged
# party re-pointing its loyalty account, a closed order sending its survey, a
# 72-hour escalation reaching the COO) stopped at the outbox row. The bus
# publisher (Redis/Kafka) is infrastructure that does not run here; consumers
# that live in Odoo do not need it.
#
# A module registers a consumer as data:
#   <record model="fix.event.consumer"> event_type, model, method
# The relay cron hands each new event to every matching subscription once.
# Delivery is recorded per (subscription, event), so a redelivery is a no-op
# (DI-05 idempotency); a failing consumer is retried and dead-letters after
# three attempts without blocking the others. The outbox row's bus `status`
# is untouched: in-process delivery and bus publication are separate.
import json
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3

# M28: set to true only on a deployment whose external publisher (Redis/Kafka)
# actually runs — it stands the no-bus drain cron down.
BUS_PUBLISHER_KEY = "fix_event_outbox.bus_publisher"


def _require_server_code(env, what):
    """Cron bodies and relay services are public methods, so JSON-RPC can
    reach them: refuse anyone but server code (M28-D10, the cd_itsm pattern).
    The estate's ir.cron rows run as the superuser, so the production crons
    pass; an interactive caller does not."""
    if not env.su:
        raise AccessError("%s runs from the server only." % what)


class FixEventConsumer(models.Model):
    """One in-Odoo consumer of one event type."""

    _name = "fix.event.consumer"
    _description = "In-Process Event Consumer"
    _order = "event_type, model, method"

    _consumer_unique = models.Constraint(
        "UNIQUE (event_type, model, method)", "A consumer subscribes to an event type once"
    )

    name = fields.Char(required=True)
    event_type = fields.Char(
        required=True,
        index=True,
        help="Exact type ('party.merged'), or a prefix ending in '.*' ('service_order.*')",
    )
    model = fields.Char(string="Consumer Model", required=True)
    method = fields.Char(
        string="Consumer Method",
        required=True,
        help="An @api.model method named consume_*; it receives the event dict and must be idempotent.",
    )
    active = fields.Boolean(default=True)
    active_from = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
        help="Events older than this are not delivered (no surprise backfill). "
        "Use Backfill to replay older ones deliberately.",
    )
    module = fields.Char(string="Owning Module")
    delivery_ids = fields.One2many("fix.event.consumer.delivery", "subscription_id")

    @api.constrains("method")
    def _check_method(self):
        for sub in self:
            if not (sub.method or "").startswith("consume_"):
                raise ValidationError(
                    "A consumer method must be named consume_*: the relay calls it as "
                    "superuser, so it may not point at an arbitrary method."
                )

    def _matches(self, event_type):
        self.ensure_one()
        if self.event_type.endswith(".*"):
            return event_type.startswith(self.event_type[:-1])
        return event_type == self.event_type

    def action_backfill(self, since=None):
        """Deliberately replay this consumer's events since `since` (default: all).

        M28-D5: this has the same effect as the second-admin-gated replay
        (full-history redelivery of a topic), so it is an Integration-Admin
        action and leaves an audit row — not a button any internal user can
        press over RPC."""
        if not self.env.su:
            try:
                allowed = self.env.user.has_group("cd_itsm.group_integration_admin")
            except Exception:
                allowed = False
            if not allowed:
                raise AccessError(
                    "Backfill redelivers a topic's whole history: only an "
                    "Integration Admin runs it (ask for fix.event.consumer.replay "
                    "otherwise)."
                )
        Outbox = self.env["fix.event.outbox"].sudo()
        for sub in self:
            start = fields.Datetime.to_datetime(since) if since else None
            prefix = sub.event_type[:-1] if sub.event_type.endswith(".*") else None
            domain = (
                [("event_type", "=like", prefix + "%")]
                if prefix
                else [("event_type", "=", sub.event_type)]
            )
            if start:
                domain.append(("create_date", ">=", start))
            events = Outbox.search(domain)
            sub.sudo().write(
                {"active_from": min(events.mapped("create_date") or [sub.active_from])}
            )
            events.write({"relayed_at": False})
            # The audit trail of who replayed what (M28-D5): an event on the
            # outbox, which the M28 audit screens read like any other.
            Outbox.emit(
                "integration.consumer_backfilled",
                "fix.event.consumer",
                sub.id,
                {
                    "consumer": sub.name,
                    "event_type": sub.event_type,
                    "since": str(start or "all"),
                    "events_queued": len(events),
                    "by": self.env.user.login,
                },
            )
        return True


class FixEventConsumerDelivery(models.Model):
    """That subscription S received event E — or why it did not."""

    _name = "fix.event.consumer.delivery"
    _description = "Event Delivery"
    _order = "id desc"

    _once = models.Constraint(
        "UNIQUE (subscription_id, event_id)", "An event is delivered to a consumer once"
    )

    subscription_id = fields.Many2one(
        "fix.event.consumer", required=True, index=True, ondelete="cascade"
    )
    event_id = fields.Many2one("fix.event.outbox", required=True, index=True, ondelete="cascade")
    event_type = fields.Char(related="event_id.event_type", store=True)
    state = fields.Selection(
        [("done", "Delivered"), ("failed", "Failed (will retry)"), ("dead", "Dead-lettered")],
        required=True,
        default="done",
        index=True,
    )
    attempts = fields.Integer(default=1)
    last_error = fields.Text()
    delivered_at = fields.Datetime(default=fields.Datetime.now)


class FixEventOutbox(models.Model):
    _inherit = "fix.event.outbox"

    relayed_at = fields.Datetime(
        string="Relayed In-Process",
        index=True,
        readonly=True,
        help="Every in-Odoo subscription has been handed this event (or dead-lettered it).",
    )

    def _relay_event_dict(self):
        self.ensure_one()
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate": self.aggregate,
            "aggregate_id": self.aggregate_id,
            "payload": json.loads(self.payload or "{}"),
            "metadata": json.loads(self.metadata_json) if self.metadata_json else {},
            "company_id": self.company_id.id,
        }

    @api.model
    def cron_relay(self, limit=500):
        """Hand each unrelayed event to its subscriptions. Returns the count handled."""
        _require_server_code(self.env, "Event relay")
        subs = self.env["fix.event.consumer"].sudo().search([("active", "=", True)])
        Outbox = self.sudo()
        if not subs:
            return 0
        oldest = min(subs.mapped("active_from"))
        # Nothing listens to events older than every subscription: mark them in
        # one statement rather than walking a 26,000-row backlog.
        self.env.cr.execute(
            "UPDATE fix_event_outbox SET relayed_at = now() AT TIME ZONE 'UTC' "
            "WHERE relayed_at IS NULL AND create_date < %s",
            (oldest,),
        )
        events = Outbox.search(
            [("relayed_at", "=", False)], order="create_date asc, id asc", limit=limit
        )
        Delivery = self.env["fix.event.consumer.delivery"].sudo()
        handled = 0
        for event in events:
            matching = subs.filtered(
                lambda s, e=event: s._matches(e.event_type) and s.active_from <= e.create_date
            )
            settled = True
            for sub in matching:
                delivery = Delivery.search(
                    [("subscription_id", "=", sub.id), ("event_id", "=", event.id)], limit=1
                )
                if delivery.state in ("done", "dead"):
                    continue
                error = self._relay_deliver(sub, event)
                if delivery:
                    attempts = delivery.attempts + 1
                    state = (
                        "done" if not error else ("dead" if attempts >= MAX_ATTEMPTS else "failed")
                    )
                    delivery.write(
                        {
                            "state": state,
                            "attempts": attempts,
                            "last_error": error or False,
                            "delivered_at": fields.Datetime.now(),
                        }
                    )
                else:
                    state = "done" if not error else "failed"
                    Delivery.create(
                        {
                            "subscription_id": sub.id,
                            "event_id": event.id,
                            "state": state,
                            "last_error": error or False,
                        }
                    )
                if state == "failed":
                    settled = False
            if settled:
                event.write({"relayed_at": fields.Datetime.now()})
            handled += 1
        return handled

    def _relay_deliver(self, sub, event):
        """Run one consumer inside a savepoint. '' on success, else the error."""
        if sub.model not in self.env:
            return "consumer model %s is not installed" % sub.model
        consumer = self.env[sub.model].sudo().with_company(event.company_id)
        method = getattr(consumer, sub.method, None)
        if not callable(method):
            return "%s has no method %s" % (sub.model, sub.method)
        try:
            with self.env.cr.savepoint():
                method(event._relay_event_dict())
        except Exception as exc:  # a consumer's failure must not stop the others
            _logger.warning(
                "event relay: %s.%s failed on %s: %s", sub.model, sub.method, event.event_id, exc
            )
            return ("%s: %s" % (type(exc).__name__, exc))[:2000]
        return ""

    @api.model
    def relay_health(self):
        """Lag and dead letters, for the alert cron and the dashboards."""
        oldest = self.sudo().search([("relayed_at", "=", False)], order="create_date asc", limit=1)
        Delivery = self.env["fix.event.consumer.delivery"].sudo()
        age = (fields.Datetime.now() - oldest.create_date).total_seconds() / 60.0 if oldest else 0.0
        oldest_bus = self.sudo().search(
            [("status", "=", "pending")], order="create_date asc", limit=1
        )
        bus_age = (
            (fields.Datetime.now() - oldest_bus.create_date).total_seconds() / 3600.0
            if oldest_bus
            else 0.0
        )
        return {
            "unrelayed": self.sudo().search_count([("relayed_at", "=", False)]),
            "oldest_unrelayed_minutes": round(age, 1),
            "failed_deliveries": Delivery.search_count([("state", "=", "failed")]),
            "dead_letters": Delivery.search_count([("state", "=", "dead")]),
            "bus_pending": self.sudo().search_count([("status", "=", "pending")]),
            "oldest_bus_pending_hours": round(bus_age, 1),
        }

    @api.model
    def cron_mark_relayed_published(self, limit=5000):
        """M28: bound the bus backlog when no external publisher runs.

        This estate's Redis/Kafka publisher does not run (the module header
        says so): `status='pending'` then counts events that were ALREADY
        delivered to every in-Odoo consumer — a phantom backlog that grew to
        26k+ rows and nothing ever drained, alerted on, or purged. When
        `fix_event_outbox.bus_publisher` is off, a relayed event that no
        webhook delivery still needs is FINISHED: mark it published so the
        counter, the retention purge and the M28 tiles tell the truth. Set the
        parameter to true on a deployment with a real publisher — then this
        cron stands down and pending really means pending.
        """
        _require_server_code(self.env, "Bus drain")
        flag = self.env["ir.config_parameter"].sudo().get_param(BUS_PUBLISHER_KEY, "") or ""
        if flag.strip().lower() in ("1", "true", "yes", "on"):
            return 0
        batch = self.sudo().search(
            [("status", "=", "pending"), ("relayed_at", "!=", False)],
            order="id asc",
            limit=limit,
        )
        if not batch:
            return 0
        if "fix.webhook.delivery" in self.env:
            held = (
                self.env["fix.webhook.delivery"]
                .sudo()
                .search([("event_id", "in", batch.ids), ("state", "not in", ("sent",))])
                .event_id
            )
            batch -= held
        if batch:
            batch.mark_published()
        return len(batch)

    @api.model
    def cron_relay_age_alert(self):
        """Outbox-age alert: warn when the relay falls behind, dead-letters, or
        the bus backlog stops draining (M28: the 26k-row silent backlog)."""
        _require_server_code(self.env, "Event relay alert")
        limit = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("fix_event_outbox.relay_alert_minutes", 30)
        )
        health = self.relay_health()
        lagging = health["oldest_unrelayed_minutes"] > limit
        bus_hours = float(
            self.env["ir.config_parameter"].sudo().get_param("fix_event_outbox.bus_alert_hours", 24)
        )
        bus_stuck = health["oldest_bus_pending_hours"] > bus_hours
        if lagging or health["dead_letters"] or bus_stuck:
            _logger.warning("event relay unhealthy: %s", health)
            last = self.sudo().search(
                [("event_type", "=", "outbox.relay_unhealthy")], order="create_date desc", limit=1
            )
            if not last or last.create_date < fields.Datetime.now() - timedelta(hours=1):
                self.emit("outbox.relay_unhealthy", "fix.event.outbox", 0, health)
        return health
