# libs/py/fix_events/kafka_bus.py — event-bus semantics + the in-memory transport (P09-M01 / R07).
"""Event-bus envelope semantics and the in-memory transport for tests (FF-28).

This module owns the TRANSPORT-NEUTRAL semantics of the 1000FiX event bus:
- CloudEvents / FixEvent envelope construction conforming to AR-009 §5.5.
- Topic mapping ``fix.events.<domain>`` derived from the event_type prefix.
- Partition keying: ``aggregate:aggregate_id`` for per-entity ordering.
- DLQ header contract (original topic/offset, reason, failure time).

Two transports implement those semantics:
- :class:`InMemoryBus` (below): a deterministic in-process log used by unit
  tests and offline drills. It is NOT a Kafka client and never contacts a
  broker; anything measured on it is in-process by construction.
- :class:`libs.py.fix_events.kafka_backend.KafkaBackend`: the real transport
  over the 3-broker cluster (kafka-python-ng), reached via
  ``KAFKA_BOOTSTRAP_SERVERS`` (default 127.0.0.1:9092,9094,9095 — the
  docker-compose.asset-ml.yml host ports).

``get_kafka_client()`` returns the process-wide bus: a real KafkaBackend by
default, or an InMemoryBus when ``FIX_EVENTS_TRANSPORT=memory``. Tests that
must stay hermetic monkeypatch ``_global_kafka_client`` (see
libs/py/fix_events/tests/conftest.py).
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
import uuid
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # runtime import lives in get_kafka_client() to avoid a cycle
    from .kafka_backend import KafkaBackend

logger = logging.getLogger(__name__)

#: Set to ``memory`` to force the in-process transport (unit tests, offline
#: drills). Anything else selects the real Kafka backend.
TRANSPORT_ENV = "FIX_EVENTS_TRANSPORT"
TRANSPORT_MEMORY = "memory"

#: Host ports of the 3-broker cluster in infra/compose/docker-compose.asset-ml.yml.
DEFAULT_BOOTSTRAP_SERVERS = ["127.0.0.1:9092", "127.0.0.1:9094", "127.0.0.1:9095"]
BOOTSTRAP_ENV = "KAFKA_BOOTSTRAP_SERVERS"


def bootstrap_servers_env() -> list[str]:
    """Broker list from ``KAFKA_BOOTSTRAP_SERVERS`` (comma-separated), else the
    compose cluster's default host ports."""
    raw = os.environ.get(BOOTSTRAP_ENV, "")
    servers = [h.strip() for h in raw.split(",") if h.strip()]
    return servers or list(DEFAULT_BOOTSTRAP_SERVERS)


SECURITY_PROTOCOLS = ("PLAINTEXT", "SSL", "SASL_PLAINTEXT", "SASL_SSL")
SASL_MECHANISMS = ("PLAIN", "SCRAM-SHA-256", "SCRAM-SHA-512")


def kafka_security_kwargs(env: dict[str, str] | None = None) -> dict[str, str]:
    """kafka-python connection-security arguments from the environment.

    ``KAFKA_SECURITY_PROTOCOL`` (default PLAINTEXT, the local compose
    cluster); SASL_* protocols need ``KAFKA_SASL_MECHANISM`` plus
    ``KAFKA_SASL_USERNAME``/``KAFKA_SASL_PASSWORD``; SSL protocols may name a
    CA bundle in ``KAFKA_SSL_CAFILE``. Managed brokers (e.g. DigitalOcean
    Kafka) are SASL_SSL-only. A half-configured SASL setup raises instead of
    silently connecting without credentials."""
    env = dict(os.environ) if env is None else env
    protocol = (env.get("KAFKA_SECURITY_PROTOCOL") or "PLAINTEXT").strip().upper()
    if protocol not in SECURITY_PROTOCOLS:
        raise ValueError(f"KAFKA_SECURITY_PROTOCOL {protocol!r} is not one of {SECURITY_PROTOCOLS}")
    kwargs: dict[str, str] = {"security_protocol": protocol}
    if protocol.startswith("SASL_"):
        mechanism = (env.get("KAFKA_SASL_MECHANISM") or "").strip().upper()
        username = env.get("KAFKA_SASL_USERNAME") or ""
        password = env.get("KAFKA_SASL_PASSWORD") or ""
        if mechanism not in SASL_MECHANISMS or not username or not password:
            raise ValueError(
                f"{protocol} needs KAFKA_SASL_MECHANISM (one of {SASL_MECHANISMS}), "
                "KAFKA_SASL_USERNAME and KAFKA_SASL_PASSWORD"
            )
        kwargs.update(
            sasl_mechanism=mechanism,
            sasl_plain_username=username,
            sasl_plain_password=password,
        )
    if protocol.endswith("SSL") and env.get("KAFKA_SSL_CAFILE"):
        kwargs["ssl_cafile"] = env["KAFKA_SSL_CAFILE"]
    return kwargs


def map_topic_for_event(event_type: str) -> str:
    """Map canonical event_type to Kafka topic name."""
    parts = event_type.split(".")
    domain = parts[0] if parts else "general"
    return f"fix.events.{domain}"


def build_message_key(aggregate: str, aggregate_id: int) -> str:
    """Partition key: aggregate + aggregate_id (per-entity ordering, AR-009)."""
    return f"{aggregate}:{aggregate_id}"


def default_headers(metadata: dict | None = None) -> dict:
    """Merge caller metadata with the transport-default record headers."""
    headers = dict(metadata or {})
    headers.setdefault("source", "odoo")
    headers.setdefault("producer", "fix_events")
    headers.setdefault("content_type", "application/json")
    headers.setdefault("emitted_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    return headers


def build_envelope(
    event_type: str,
    aggregate: str,
    aggregate_id: int,
    payload: dict,
    headers: dict,
) -> dict:
    """Build the CloudEvents / FixEvent envelope (AR-009 §5.5).

    ``headers`` must already carry the default headers (see
    :func:`default_headers`); the envelope reads the causal ids and the
    emission timestamp from it, so handlers only need the envelope value.
    """
    # event_id is the consumers' idempotency key (DI-05), so it must be unique
    # per event: never the request-wide correlation_id, never a ms timestamp.
    return {
        "event_id": headers.get("event_id") or f"evt-{uuid.uuid4().hex}",
        # Handlers only see the envelope, so the causal ids (AS-08) travel in it,
        # not just in the record headers.
        "correlation_id": headers.get("correlation_id"),
        "causation_id": headers.get("causation_id"),
        "event_type": event_type,
        "aggregate": aggregate,
        "aggregate_id": aggregate_id,
        "timestamp": headers["emitted_at"],
        "producer": "1000fix_erp",
        "payload": payload,
    }


def dlq_headers(failed_record: KafkaRecord, error_msg: str) -> dict:
    """Diagnosis headers attached to a record routed to the dead-letter queue."""
    dlq = dict(failed_record.headers)
    dlq["dlq_reason"] = error_msg[:500]
    dlq["original_topic"] = failed_record.topic
    dlq["original_offset"] = str(failed_record.offset)
    dlq["failed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return dlq


class KafkaRecord:
    def __init__(
        self,
        topic: str,
        partition: int,
        offset: int,
        key: str,
        value: dict,
        headers: dict,
        timestamp: float,
    ):
        self.topic = topic
        self.partition = partition
        self.offset = offset
        self.key = key
        self.value = value
        self.headers = headers
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "partition": self.partition,
            "offset": self.offset,
            "key": self.key,
            "value": self.value,
            "headers": self.headers,
            "timestamp": self.timestamp,
        }


class KafkaPartitionLog:
    def __init__(self, topic: str, partition: int):
        self.topic = topic
        self.partition = partition
        self.records: list[KafkaRecord] = []
        self._next_offset = 0

    def append(
        self, key: str, value: dict, headers: dict, timestamp: float | None = None
    ) -> KafkaRecord:
        ts = timestamp if timestamp is not None else time.time()
        rec = KafkaRecord(
            topic=self.topic,
            partition=self.partition,
            offset=self._next_offset,
            key=key,
            value=value,
            headers=headers,
            timestamp=ts,
        )
        self.records.append(rec)
        self._next_offset += 1
        return rec

    def read_from(self, offset: int, limit: int = 100) -> list[KafkaRecord]:
        if offset < 0 or offset >= len(self.records):
            return []
        return self.records[offset : offset + limit]

    def find_offset_by_timestamp(self, target_ts: float) -> int:
        """Binary search / linear scan for earliest record with timestamp >= target_ts."""
        for rec in self.records:
            if rec.timestamp >= target_ts:
                return rec.offset
        return self._next_offset


class InMemoryBus:
    """In-process event bus: the same semantics as the Kafka transport, no broker.

    Used by unit tests and offline drills; measured numbers on it are
    in-process by construction. The real transport is
    :class:`libs.py.fix_events.kafka_backend.KafkaBackend`.
    """

    def __init__(self, bootstrap_servers: list[str] | None = None, num_partitions: int = 3):
        self.bootstrap_servers = bootstrap_servers or [
            "127.0.0.1:9092",
            "127.0.0.1:9094",
            "127.0.0.1:9095",
        ]
        self.num_partitions = num_partitions
        self._topics: dict[str, dict[int, KafkaPartitionLog]] = {}
        self._consumer_offsets: dict[
            str, dict[str, dict[int, int]]
        ] = {}  # group -> topic -> partition -> offset

    def _ensure_topic(self, topic: str):
        if topic not in self._topics:
            self._topics[topic] = {
                p: KafkaPartitionLog(topic, p) for p in range(self.num_partitions)
            }

    def _select_partition(self, topic: str, key: str) -> int:
        hash_val = int(hashlib.md5(key.encode("utf-8"), usedforsecurity=False).hexdigest(), 16)
        return hash_val % self.num_partitions

    # ------------------------------------------------------------------ produce

    def produce(
        self,
        event_type: str,
        aggregate: str,
        aggregate_id: int,
        payload: dict,
        metadata: dict | None = None,
    ) -> KafkaRecord:
        """Produce a domain event following the CloudEvents / FixEvent envelope."""
        topic = map_topic_for_event(event_type)
        self._ensure_topic(topic)

        key = build_message_key(aggregate, aggregate_id)
        partition = self._select_partition(topic, key)
        part_log = self._topics[topic][partition]

        headers = default_headers(metadata)
        envelope = build_envelope(event_type, aggregate, aggregate_id, payload, headers)

        rec = part_log.append(key, envelope, headers)
        logger.debug(
            "in_memory_bus: produced %s to %s[%d] offset %d",
            event_type,
            topic,
            partition,
            rec.offset,
        )
        return rec

    # ------------------------------------------------------------------ consume

    def consume(
        self,
        consumer_group: str,
        topic: str,
        handler: Callable[[dict], None],
        limit: int = 50,
        dlq_on_failure: bool = True,
    ) -> int:
        """Consume available messages for a consumer group across all partitions of a topic."""
        self._ensure_topic(topic)
        self._consumer_offsets.setdefault(consumer_group, {}).setdefault(topic, {})

        processed = 0
        dlq_topic = f"{topic}.dlq"

        for p, part_log in self._topics[topic].items():
            curr_offset = self._consumer_offsets[consumer_group][topic].get(p, 0)
            records = part_log.read_from(curr_offset, limit=limit)

            for rec in records:
                try:
                    handler(rec.value)
                    self._consumer_offsets[consumer_group][topic][p] = rec.offset + 1
                    processed += 1
                except Exception as ex:
                    logger.error(
                        "in_memory_bus: consumer error on %s[%d]:%d — %s",
                        topic,
                        p,
                        rec.offset,
                        ex,
                    )
                    if dlq_on_failure:
                        self.route_to_dlq(dlq_topic, rec, str(ex))
                        self._consumer_offsets[consumer_group][topic][p] = rec.offset + 1
                        processed += 1
                    else:
                        raise

        return processed

    def route_to_dlq(
        self, dlq_topic: str, failed_record: KafkaRecord, error_msg: str
    ) -> KafkaRecord:
        """Route failed record to Dead-Letter Queue with diagnosis headers."""
        self._ensure_topic(dlq_topic)
        p = 0
        return self._topics[dlq_topic][p].append(
            failed_record.key, failed_record.value, dlq_headers(failed_record, error_msg)
        )

    # ------------------------------------------------------- replay / audit API

    def seek_to_timestamp(self, topic: str, timestamp_s: float) -> dict[int, int]:
        """Return offset mapping per partition for a given timestamp."""
        self._ensure_topic(topic)
        res = {}
        for p, part_log in self._topics[topic].items():
            res[p] = part_log.find_offset_by_timestamp(timestamp_s)
        return res

    def topic_partitions(self, topic: str) -> list[int]:
        """Existing partitions of a topic (no auto-creation)."""
        return sorted(self._topics.get(topic, {}))

    def read_topic_from(
        self, topic: str, offsets: dict[int, int], limit_per_partition: int = 10000
    ) -> list[KafkaRecord]:
        """Read records from per-partition start offsets, merged chronologically.

        Unlike :meth:`consume` this is a read-only scan that never creates the
        topic, never tracks consumer offsets and never dead-letters.
        """
        out: list[KafkaRecord] = []
        for p, part_log in self._topics.get(topic, {}).items():
            out.extend(part_log.read_from(offsets.get(p, 0), limit=limit_per_partition))
        out.sort(key=lambda r: (r.timestamp, r.offset))
        return out

    def get_topic_records(self, topic: str) -> list[KafkaRecord]:
        self._ensure_topic(topic)
        return self.read_topic_from(topic, dict.fromkeys(self._topics[topic], 0))

    def committed_offsets(self, consumer_group: str, topic: str) -> dict[int, int]:
        """Offsets committed by a consumer group for a topic (missing = none)."""
        return dict(self._consumer_offsets.get(consumer_group, {}).get(topic, {}))

    def commit_offsets(self, consumer_group: str, topic: str, offsets: dict[int, int]) -> None:
        """Persist a consumer group's next-offset-per-partition (idempotent re-drive cursor)."""
        self._consumer_offsets.setdefault(consumer_group, {}).setdefault(topic, {}).update(offsets)

    def close(self) -> None:  # transport shutdown is a no-op in memory
        return None


# Global singleton instance for the running runtime
_global_kafka_client: InMemoryBus | KafkaBackend | None = None


def get_kafka_client() -> InMemoryBus | KafkaBackend:
    """The process-wide event bus (FF-28): real Kafka by default.

    ``FIX_EVENTS_TRANSPORT=memory`` swaps in the in-process transport; tests
    monkeypatch ``_global_kafka_client`` directly (see the suite conftest).
    """
    global _global_kafka_client
    if _global_kafka_client is None:
        if os.environ.get(TRANSPORT_ENV, "").strip().lower() == TRANSPORT_MEMORY:
            _global_kafka_client = InMemoryBus()
        else:
            from .kafka_backend import KafkaBackend  # local import: avoids a cycle

            _global_kafka_client = KafkaBackend()
    return _global_kafka_client
