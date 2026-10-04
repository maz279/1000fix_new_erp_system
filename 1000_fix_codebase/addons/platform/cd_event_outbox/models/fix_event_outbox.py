# fix.event.outbox — the transactional outbox model (P03-M03-T02, AS-08).
# The outbox write happens in the same transaction as the business write.
# Consumers are idempotent (DI-05); a redelivery produces one effect.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

import json
import uuid


class FixEventOutbox(models.Model):
    """A domain event pending publication — the transactional outbox.

    Written in the SAME database transaction as the business write (AS-08).
    The publisher (libs/py/fix_events) drains pending events to the bus.
    """
    _name = "fix.event.outbox"
    _description = "Event Outbox"
    _order = "create_date desc"
    _rec_name = "event_type"

    # AS-03: company_id + operating_unit_id on transactional models
    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit",
                                        index=True)

    event_id = fields.Char(string="Event ID", required=True, readonly=True,
                           default=lambda self: str(uuid.uuid4()),
                           index=True, copy=False,
                           help="Globally unique event identifier for idempotency")
    event_type = fields.Char(string="Event Type", required=True, index=True,
                             help="Dot-notation type, e.g. 'party.created'")
    aggregate = fields.Char(string="Aggregate", required=True, index=True,
                            help="Aggregate root, e.g. 'res.partner'")
    aggregate_id = fields.Integer(string="Aggregate ID", required=True, index=True)

    payload = fields.Text(string="Payload (JSON)", required=True, readonly=True,
                          help="The event payload as a JSON string")
    metadata_json = fields.Text(string="Metadata (JSON)", readonly=True,
                                help="Correlation id, causation id, source, timestamp")

    status = fields.Selection(
        [("pending", "Pending"), ("published", "Published"), ("failed", "Failed")],
        default="pending", required=True, index=True,
        help="pending = in the outbox, not yet on the bus")
    publish_attempts = fields.Integer(default=0, readonly=True)
    last_error = fields.Text(readonly=True)
    published_at = fields.Datetime(readonly=True)

    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _event_id_unique = models.Constraint('UNIQUE (event_id)', 'Event ID must be globally unique')

    @api.model
    def emit(self, event_type: str, aggregate: str, aggregate_id: int,
             payload: dict, metadata: dict | None = None) -> "FixEventOutbox":
        """Emit a domain event by writing to the outbox.

        MUST be called within the same transaction as the business write
        (AS-08). The publisher drains this table asynchronously.
        """
        if not event_type or "." not in event_type:
            raise ValidationError(f"event_type must be dot-notation, got: {event_type!r}")
        meta = {
            "correlation_id": metadata.get("correlation_id", str(uuid.uuid4())) if metadata else str(uuid.uuid4()),
            "causation_id": metadata.get("causation_id") if metadata else None,
            "source": "odoo",
            "emitted_at": fields.Datetime.now().isoformat(),
        }
        return self.create({
            "event_type": event_type,
            "aggregate": aggregate,
            "aggregate_id": aggregate_id,
            "payload": json.dumps(payload, default=str, sort_keys=True),
            "metadata_json": json.dumps(meta, default=str),
        })

    @api.model
    def drain_pending(self, limit: int = 100) -> list[dict]:
        """Fetch pending events for the publisher (called by fix_events).

        Returns a list of dicts with event_id, event_type, payload, metadata.
        The publisher marks them published/failed; this method is read-only.
        """
        pending = self.search([("status", "=", "pending")], limit=limit,
                              order="create_date asc")
        return [{
            "event_id": e.event_id,
            "event_type": e.event_type,
            "aggregate": e.aggregate,
            "aggregate_id": e.aggregate_id,
            "payload": json.loads(e.payload),
            "metadata": json.loads(e.metadata_json) if e.metadata_json else {},
        } for e in pending]

    def mark_published(self):
        for rec in self:
            rec.write({"status": "published", "published_at": fields.Datetime.now()})

    def mark_failed(self, error: str):
        for rec in self:
            rec.write({"status": "failed", "last_error": error[:2000],
                       "publish_attempts": rec.publish_attempts + 1})
