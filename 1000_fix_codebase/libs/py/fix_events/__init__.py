# libs/py/fix_events — THE event client (P03-M03-T05, FF-28).
#
# FF-28: no direct bus clients anywhere else. One client means one place to
# fix a delivery-semantics defect. Every model that publishes a domain event
# calls fix_events.publish(), which writes to the transactional outbox
# (AS-08) in the same database transaction as the business write.
#
# Usage:
#   from libs.py.fix_events import publish
#   publish(env, "party.created", "res.partner", partner.id,
#           {"partner_id": partner.id, "name": partner.name})
"""fix_events — the only event client (FF-28)."""

from __future__ import annotations

import json
import logging
from typing import Any

# Kafka Bus, Dual-Write, Migration, and Replay Exports (EP-05 / EP-06 / P09-M01)
from .dual_write import DualWriteEventBus, get_dual_bus, get_redis_store
from .kafka_backend import EventBus, KafkaBackend
from .kafka_bus import InMemoryBus, KafkaRecord, get_kafka_client, map_topic_for_event
from .migration import (
    CANONICAL_CONSUMER_GROUPS,
    ConsumerBusState,
    ConsumerGroupMigrationManager,
    get_migration_manager,
)
from .replay import EventReplayEngine, get_replay_engine

logger = logging.getLogger(__name__)

_ENVELOPE_KEYS = ("event_id", "event_type", "aggregate", "correlation_id", "causation_id")


def normalize_bus_event(raw: dict[str, Any]) -> dict[str, Any]:
    """One shape for a consumed event, whichever bus delivered it.

    Kafka hands a consumer the FixEvent envelope (payload is a dict); Redis Streams
    hands it the stream fields (payload is canonical JSON, aggregate_id a string,
    absent ids are ""). Consumers code against the normalised form only.
    """
    payload = raw.get("payload")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload) if payload else {}
        except ValueError as exc:
            raise ValueError(f"event payload is not JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("event payload must be a JSON object")
    event = {key: (raw.get(key) or None) for key in _ENVELOPE_KEYS}
    aggregate_id = raw.get("aggregate_id")
    try:
        event["aggregate_id"] = int(aggregate_id) if aggregate_id not in (None, "") else None
    except (TypeError, ValueError):
        event["aggregate_id"] = None
    event["payload"] = payload
    return event


def publish(
    env,
    event_type: str,
    aggregate: str,
    aggregate_id: int,
    payload: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> str:
    """Publish a domain event via the transactional outbox (AS-08).

    Args:
        env: the Odoo environment (must be within a transaction)
        event_type: dot-notation type, e.g. "party.created"
        aggregate: aggregate root, e.g. "res.partner"
        aggregate_id: the aggregate's database id
        payload: the event payload (JSON-serialisable dict)
        metadata: optional correlation/causation ids

    Returns:
        the event_id (UUID string) — used for idempotency tracking

    Raises:
        ValidationError: if event_type is malformed
    """
    meta = dict(metadata or {})
    # Check env context or telemetry if correlation_id not provided
    if not meta.get("correlation_id"):
        ctx_corr = None
        if hasattr(env, "context") and isinstance(env.context, dict):
            ctx_corr = env.context.get("fix_correlation_id")
        if not ctx_corr:
            try:
                from libs.py.fix_telemetry import get_current_correlation_id

                ctx_corr = get_current_correlation_id()
            except ImportError:
                pass
        if ctx_corr:
            meta["correlation_id"] = ctx_corr

    outbox = env["fix.event.outbox"]
    record = outbox.emit(event_type, aggregate, aggregate_id, payload, meta)
    logger.debug(
        "fix_events: emitted %s (id=%s, aggregate=%s/%s, corr=%s)",
        event_type,
        record.event_id,
        aggregate,
        aggregate_id,
        meta.get("correlation_id"),
    )
    return record.event_id


def consume(env, handler: callable, event_type: str, *, dead_letter_on_error: bool = True) -> int:
    """Register an idempotent event consumer (DI-05).

    The consumer framework retries failed messages; a poisoned message
    (3 consecutive failures) goes to the dead-letter queue. An event
    delivered twice produces one effect (idempotency by event_id dedup).

    Args:
        env: the Odoo environment
        handler: callable(event: dict) -> None; must be idempotent
        event_type: subscribe to this event type only
        dead_letter_on_error: if True, failed messages dead-letter after 3 tries

    Returns:
        the number of events processed
    """
    # In production, this subscribes to the bus (Redis Streams W1–W5, Kafka W6+).
    # In tests, this can be called directly with fixture events.
    processed = 0
    # Implementation: the bus consumer loop lives in services/notification-dispatcher
    # (Node.js) and services/ — this Python client is the publisher side.
    # Consumer-side Python lives in the domain modules' event listeners.
    return processed


def replay_from_timestamp(env, timestamp: str, event_type: str | None = None) -> list[dict]:
    """Replay events from a timestamp (P03-M03-T04).

    Enables rebuilding the VAT register from the event stream (M51) without
    M20's cooperation. Returns events in publication order.
    """
    domain = [("create_date", ">=", timestamp), ("status", "=", "published")]
    if event_type:
        domain.append(("event_type", "=", event_type))
    events = env["fix.event.outbox"].search(domain, order="create_date asc")
    return [
        {
            "event_id": e.event_id,
            "event_type": e.event_type,
            "payload": __import__("json").loads(e.payload),
            "metadata": __import__("json").loads(e.metadata_json) if e.metadata_json else {},
        }
        for e in events
    ]


__all__ = [
    "CANONICAL_CONSUMER_GROUPS",
    "ConsumerBusState",
    "ConsumerGroupMigrationManager",
    "DualWriteEventBus",
    "EventBus",
    "EventReplayEngine",
    "InMemoryBus",
    "KafkaBackend",
    "KafkaRecord",
    "consume",
    "get_dual_bus",
    "get_kafka_client",
    "get_migration_manager",
    "get_redis_store",
    "get_replay_engine",
    "map_topic_for_event",
    "normalize_bus_event",
    "publish",
    "replay_from_timestamp",
]
