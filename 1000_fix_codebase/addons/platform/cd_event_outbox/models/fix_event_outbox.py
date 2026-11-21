# fix.event.outbox — the transactional outbox model (P03-M03-T02, AS-08).
# The outbox write happens in the same transaction as the business write.
# Consumers are idempotent (DI-05); a redelivery produces one effect.
import json
import uuid

from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)

    event_id = fields.Char(
        string="Event ID",
        required=True,
        readonly=True,
        default=lambda self: str(uuid.uuid4()),
        index=True,
        copy=False,
        help="Globally unique event identifier for idempotency",
    )
    event_type = fields.Char(
        string="Event Type",
        required=True,
        index=True,
        help="Dot-notation type, e.g. 'party.created'",
    )
    aggregate = fields.Char(
        string="Aggregate", required=True, index=True, help="Aggregate root, e.g. 'res.partner'"
    )
    aggregate_id = fields.Integer(string="Aggregate ID", required=True, index=True)

    payload = fields.Text(
        string="Payload (JSON)",
        required=True,
        readonly=True,
        help="The event payload as a JSON string",
    )
    metadata_json = fields.Text(
        string="Metadata (JSON)",
        readonly=True,
        help="Correlation id, causation id, source, timestamp",
    )

    status = fields.Selection(
        [("pending", "Pending"), ("published", "Published"), ("failed", "Failed")],
        default="pending",
        required=True,
        index=True,
        help="pending = in the outbox, not yet on the bus",
    )
    publish_attempts = fields.Integer(default=0, readonly=True)
    last_error = fields.Text(readonly=True)
    published_at = fields.Datetime(readonly=True)

    # R07-M01: Dual-Write & Kafka migration fields (EP-05)
    bus_target = fields.Selection(
        [
            ("redis", "Redis Streams"),
            ("dual", "Dual-Write (Redis + Kafka)"),
            ("kafka", "Kafka (Production)"),
        ],
        string="Bus Target",
        default="dual",
        required=True,
        index=True,
        help="Target event bus according to migration stage (EP-05)",
    )
    kafka_published_at = fields.Datetime(string="Kafka Published At", readonly=True)
    kafka_partition = fields.Integer(string="Kafka Partition", readonly=True)
    kafka_offset = fields.Integer(string="Kafka Offset", readonly=True)
    payload_sha256 = fields.Char(string="Payload SHA-256", readonly=True, index=True)

    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _event_id_unique = models.Constraint("UNIQUE (event_id)", "Event ID must be globally unique")

    @api.private
    @api.model
    def emit(
        self,
        event_type: str,
        aggregate: str,
        aggregate_id: int,
        payload: dict,
        metadata: dict | None = None,
    ) -> "FixEventOutbox":
        """Emit a domain event by writing to the outbox.

        MUST be called within the same transaction as the business write
        (AS-08). The publisher drains this table asynchronously.

        Authorization: employees hold READ-only access to the outbox, so the
        row is written with sudo(). Company: the aggregate record's own company
        when it has one (FIN-24), else the caller's company (env.company).
        The method is @api.private: server code only, never callable over
        RPC (an employee cannot forge events into the bus).
        """
        if not event_type or "." not in event_type:
            raise ValidationError(f"event_type must be dot-notation, got: {event_type!r}")
        payload_str = json.dumps(payload, default=str, sort_keys=True)
        import hashlib

        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        meta = {
            "correlation_id": metadata.get("correlation_id", str(uuid.uuid4()))
            if metadata
            else str(uuid.uuid4()),
            "causation_id": metadata.get("causation_id") if metadata else None,
            "source": "odoo",
            "emitted_at": fields.Datetime.now().isoformat(),
        }
        return self.sudo().create(
            {
                "company_id": self._fix_event_company(aggregate, aggregate_id).id,
                "event_type": event_type,
                "aggregate": aggregate,
                "aggregate_id": aggregate_id,
                "payload": payload_str,
                "payload_sha256": payload_hash,
                "metadata_json": json.dumps(meta, default=str),
                "bus_target": "dual",
            }
        )

    @api.model
    def _fix_event_company(self, aggregate, aggregate_id):
        """FIN-24 (A07 ERP audit 2026-11-20): the company an event belongs to.

        An event about a company-B record raised by a user working in company A
        belonged to A (env.company), so the outbox and every consumer the relay
        runs `with_company(event.company_id)` saw it in the wrong company. The
        record's own company wins when the aggregate is a model with a company
        field and the record exists and names one (a res.company aggregate is
        its own company); otherwise the caller's company, as before."""
        fallback = self.env.company
        try:
            record_id = int(aggregate_id or 0)
        except (TypeError, ValueError):
            return fallback
        if not aggregate or record_id <= 0 or aggregate not in self.env:
            return fallback
        Model = self.env[aggregate].sudo()
        if aggregate == "res.company":
            return Model.browse(record_id).exists() or fallback
        field = Model._fields.get("company_id")
        if field is None or field.type != "many2one" or field.comodel_name != "res.company":
            return fallback
        record = Model.browse(record_id).exists()
        return record.company_id[:1] or fallback

    @api.private
    @api.model
    def drain_pending(self, limit: int = 100) -> list[dict]:
        """Fetch pending events for the publisher (called by fix_events).

        Returns a list of dicts with event_id, event_type, payload, metadata.
        The publisher marks them published/failed; this method is read-only.
        """
        pending = self.search([("status", "=", "pending")], limit=limit, order="create_date asc")
        return [
            {
                "id": e.id,
                "event_id": e.event_id,
                "event_type": e.event_type,
                "aggregate": e.aggregate,
                "aggregate_id": e.aggregate_id,
                "payload": json.loads(e.payload),
                "metadata": json.loads(e.metadata_json) if e.metadata_json else {},
                "bus_target": e.bus_target,
                "payload_sha256": e.payload_sha256,
            }
            for e in pending
        ]

    @api.private
    def mark_published(self, kafka_partition: int | None = None, kafka_offset: int | None = None):
        vals = {"status": "published", "published_at": fields.Datetime.now()}
        if kafka_partition is not None:
            vals["kafka_partition"] = kafka_partition
            vals["kafka_published_at"] = fields.Datetime.now()
        if kafka_offset is not None:
            vals["kafka_offset"] = kafka_offset
        for rec in self:
            rec.write(vals)

    @api.private
    def mark_failed(self, error: str):
        for rec in self:
            rec.write(
                {
                    "status": "failed",
                    "last_error": error[:2000],
                    "publish_attempts": rec.publish_attempts + 1,
                }
            )
