# libs/py/fix_events/replay.py — Time-Travel Event Replay & DLQ Recovery (EP-06 / P09-M01-T05).
"""Event Replay Engine and Dead-Letter Queue (DLQ) Recovery (EP-06).

Implements:
1. Replay from timestamp across all Kafka partitions:
   - Seeks partition offsets to target timestamp (ISO-8601 or epoch seconds).
   - Enables out-of-band audit verification and state reconstruction (e.g. M51 VAT tax register).
2. DLQ Inspection and Recovery:
   - Diagnoses poison-pill events routed to dead-letter topics.
   - Provides payload remediation and re-injection into primary topics.

Both paths talk to the bus through its public surface only
(``seek_to_timestamp`` / ``read_topic_from`` / ``committed_offsets`` /
``commit_offsets`` / ``produce``), so they run unchanged over the real Kafka
transport (kafka_backend.KafkaBackend) and the in-memory transport
(kafka_bus.InMemoryBus).
"""

from __future__ import annotations

import datetime
import logging
import time
from collections.abc import Callable
from typing import Any

from .kafka_backend import EventBus
from .kafka_bus import get_kafka_client

logger = logging.getLogger(__name__)

# Consumer group under which the DLQ re-drive position is committed (idempotent re-drive).
DLQ_REPLAY_GROUP = "fix-events-dlq-replay"


class EventReplayEngine:
    """Manages offset-seeking time travel and DLQ reprocessing across Kafka topics."""

    def __init__(self, kafka_client: EventBus | None = None):
        self.kafka_client: EventBus = kafka_client or get_kafka_client()

    def replay_from_timestamp(
        self,
        topic: str,
        timestamp: float | str,
        target_handler: Callable[[dict[str, Any]], None],
        max_records: int = 10000,
    ) -> dict[str, Any]:
        """Replay messages from a specific historical timestamp across all partitions.

        Args:
            topic: Kafka topic name (e.g., 'fix.events.service_order')
            timestamp: epoch seconds or ISO-8601 string (e.g., '2026-10-18T00:00:00Z');
                an ISO string without an offset is UTC (never the host's local time)
            target_handler: callback receiving each replayed event payload
            max_records: safety ceiling

        Returns:
            dict summarizing replayed count, starting partition offsets, and duration
        """
        if isinstance(timestamp, str):
            # Parse ISO-8601
            dt = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.UTC)
            timestamp_s = dt.timestamp()
        else:
            timestamp_s = float(timestamp)

        t0 = time.perf_counter()
        partition_offsets = self.kafka_client.seek_to_timestamp(topic, timestamp_s)
        replayed_records = self.kafka_client.read_topic_from(
            topic, partition_offsets, limit_per_partition=max_records
        )

        # Sort replayed records chronologically
        replayed_records.sort(key=lambda r: (r.timestamp, r.offset))

        processed = 0
        for rec in replayed_records[:max_records]:
            target_handler(rec.value)
            processed += 1

        duration_ms = (time.perf_counter() - t0) * 1000.0
        logger.info(
            "Replayed %d records from topic %s (timestamp: %s) across partitions %s in %.2f ms",
            processed,
            topic,
            timestamp,
            partition_offsets,
            duration_ms,
        )

        return {
            "topic": topic,
            "timestamp": timestamp,
            "starting_offsets": partition_offsets,
            "replayed_count": processed,
            "duration_ms": round(duration_ms, 3),
            "status": "COMPLETED",
        }

    def replay_dlq(
        self,
        dlq_topic: str,
        target_topic: str,
        remediator: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Extract poison pills from DLQ, remediate payloads, and re-publish to target topic.

        Idempotent: the re-drive position is committed per DLQ partition (consumer group
        DLQ_REPLAY_GROUP), so a repeated call only re-drives records dead-lettered since.
        The remediator receives (and returns) the event's domain payload; the re-published
        event keeps the original aggregate key (per-entity ordering) and event_id
        (consumer-side dedup), with the original event_type in a header.
        """
        t0 = time.perf_counter()
        reprocessed = 0

        committed = self.kafka_client.committed_offsets(DLQ_REPLAY_GROUP, dlq_topic)
        start = {p: committed.get(p, 0) for p in self.kafka_client.topic_partitions(dlq_topic)}
        records = self.kafka_client.read_topic_from(dlq_topic, start, limit_per_partition=limit)

        for rec in records[:limit]:
            envelope = rec.value
            val = dict(envelope.get("payload", envelope))
            if remediator:
                val = remediator(val)
            # Re-publish to target topic
            repub_meta = dict(rec.headers)
            repub_meta["reprocessed_from_dlq"] = "true"
            repub_meta["original_dlq_offset"] = str(rec.offset)
            repub_meta["original_event_type"] = str(envelope.get("event_type", ""))
            repub_meta.setdefault("event_id", envelope.get("event_id"))

            self.kafka_client.produce(
                event_type=target_topic.replace("fix.events.", "") + ".replayed",
                aggregate=envelope.get("aggregate", "fix.generic"),
                aggregate_id=int(envelope.get("aggregate_id", 1)),
                payload=val,
                metadata=repub_meta,
            )
            self.kafka_client.commit_offsets(
                DLQ_REPLAY_GROUP, dlq_topic, {rec.partition: rec.offset + 1}
            )
            reprocessed += 1

        duration_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "dlq_topic": dlq_topic,
            "target_topic": target_topic,
            "reprocessed_count": reprocessed,
            "duration_ms": round(duration_ms, 3),
            "status": "RECOVERED",
        }


_global_replay_engine: EventReplayEngine | None = None


def get_replay_engine() -> EventReplayEngine:
    global _global_replay_engine
    if _global_replay_engine is None:
        _global_replay_engine = EventReplayEngine()
    return _global_replay_engine
