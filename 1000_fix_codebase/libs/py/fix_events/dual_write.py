# libs/py/fix_events/dual_write.py — Dual-Write Event Bus for Expand-Contract Migration (EP-05 / P09-M01-T03).
"""Dual-write event bus coordinator (EP-05 expand phase).

During the migration window:
- Outbox emitter writes to both Redis Streams and Kafka cluster.
- Validates sequence numbers, correlation IDs, and payload hashes.
- Tracks dual-write latency overhead and parity health.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from typing import Any

from .kafka_backend import EventBus
from .kafka_bus import KafkaRecord, get_kafka_client

logger = logging.getLogger(__name__)


def payload_digest(payload: Any) -> str:
    """SHA-256 of the canonical JSON form of a payload (the parity / shadow key)."""
    payload_json = json.dumps(payload, default=str, sort_keys=True)
    return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()


class MockRedisStreamStore:
    """Represents the Redis 7.2 Streams engine (XADD) on port 6380."""

    def __init__(self):
        self._streams: dict[str, list[dict]] = {}

    def xadd(self, stream_key: str, fields: dict[str, Any]) -> str:
        if stream_key not in self._streams:
            self._streams[stream_key] = []
        msg_id = f"{int(time.time()*1000)}-{len(self._streams[stream_key])}"
        record = {
            "id": msg_id,
            "fields": dict(fields),
            "timestamp": time.time(),
        }
        self._streams[stream_key].append(record)
        return msg_id

    def get_messages(self, stream_key: str) -> list[dict]:
        return self._streams.get(stream_key, [])


class RedisStreamStore:
    """The REAL Redis 7.2 Streams engine behind the mock's interface.

    Minimal RESP2 client over a socket - no external dependency, exactly the
    commands the bus needs (XADD / XRANGE / DEL / PING). Endpoint from
    ``REDIS_URL`` (default: the compose Redis on 6380). Connection is lazy;
    transport errors raise (fail closed - a dual-write that cannot reach
    Redis must never report success).
    """

    def __init__(self, url: str | None = None):
        import os
        import socket
        from urllib.parse import urlparse

        raw = url or os.environ.get("REDIS_URL", "redis://127.0.0.1:6380/0")
        parsed = urlparse(raw)
        self._host = parsed.hostname or "127.0.0.1"
        self._port = parsed.port or 6379
        self._db = int((parsed.path or "/0").lstrip("/") or 0)
        self._password = parsed.password
        self._sock: socket.socket | None = None
        self._file = None

    # ------------------------------------------------------ transport

    def _connect(self):
        import socket

        if self._sock is not None:
            return
        self._sock = socket.create_connection((self._host, self._port), timeout=5.0)
        self._file = self._sock.makefile("rb")
        if self._password:
            self._command(b"AUTH", self._password.encode())
        if self._db:
            self._command(b"SELECT", str(self._db).encode())

    def _close(self):
        if self._file is not None:
            self._file.close()
            self._file = None
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    @staticmethod
    def _encode(arg: bytes) -> bytes:
        return b"$%d\r\n%s\r\n" % (len(arg), arg)

    def _read_reply(self):
        line = self._file.readline()
        if not line:
            raise ConnectionError("redis: connection closed")
        kind, body = line[:1], line[1:-2]
        if kind == b"+":
            return body.decode()
        if kind == b"-":
            raise RuntimeError(f"redis: {body.decode()}")
        if kind == b":":
            return int(body)
        if kind == b"$":
            length = int(body)
            if length == -1:
                return None
            data = self._file.read(length + 2)[:-2]
            return data.decode()
        if kind == b"*":
            count = int(body)
            if count == -1:
                return None
            return [self._read_reply() for _ in range(count)]
        raise RuntimeError(f"redis: unknown reply kind {kind!r}")

    def _command(self, *args: bytes):
        self._connect()
        payload = [b"*%d\r\n" % len(args)]
        for arg in args:
            payload.append(b"$%d\r\n%s\r\n" % (len(arg), arg))
        self._sock.sendall(b"".join(payload))
        return self._read_reply()

    # -------------------------------------------------- stream interface

    def ping(self) -> bool:
        return self._command(b"PING") == "PONG"

    def xadd(self, stream_key: str, fields: dict[str, Any]) -> str:
        args = [b"XADD", stream_key.encode(), b"*"]
        for key, value in fields.items():
            args.extend((key.encode(), str(value).encode()))
        return self._command(*args)

    def get_messages(self, stream_key: str) -> list[dict]:
        reply = self._command(b"XRANGE", stream_key.encode(), b"-", b"+")
        messages: list[dict] = []
        for msg_id, flat in reply or []:
            fields: dict[str, str] = {}
            for i in range(0, len(flat), 2):
                fields[flat[i]] = flat[i + 1]
            messages.append({"id": msg_id, "fields": fields})
        return messages

    def delete_streams(self, *stream_keys: str) -> int:
        if not stream_keys:
            return 0
        return int(self._command(b"DEL", *[k.encode() for k in stream_keys]))

    # DI-05 consumer-side dedup barrier: SADD returns 1 only the FIRST time a
    # member is seen - exactly the apply-once semantics an idempotent consumer
    # needs over an at-least-once transport.
    def dedup_add(self, key: str, member: str) -> bool:
        return self._command(b"SADD", key.encode(), member.encode()) == 1

    def dedup_count(self, key: str) -> int:
        return int(self._command(b"SCARD", key.encode()))

    def delete_keys(self, *keys: str) -> int:
        if not keys:
            return 0
        return int(self._command(b"DEL", *[k.encode() for k in keys]))


_global_redis_store: MockRedisStreamStore | RedisStreamStore | None = None


def get_redis_store() -> MockRedisStreamStore | RedisStreamStore:
    """The process-wide Redis store.

    Default is the in-memory mock (hermetic tests, offline drills). Setting
    ``FIX_EVENT_BUS_LIVE=1`` switches to the REAL Redis Streams engine (REDIS_URL)
    - used by the live dual-write parity window; connection errors then fail
    closed instead of silently measuring a stand-in.
    """
    global _global_redis_store
    import os

    if _global_redis_store is None:
        if os.environ.get("FIX_EVENT_BUS_LIVE") == "1":
            _global_redis_store = RedisStreamStore()
        else:
            _global_redis_store = MockRedisStreamStore()
    return _global_redis_store


def reset_redis_store() -> None:
    """Test seam: force re-resolution of the process-wide store."""
    global _global_redis_store
    _global_redis_store = None


class DualWriteEventBus:
    """Coordinates dual-publishing across Redis Streams and Apache Kafka."""

    def __init__(self, kafka_client: EventBus | None = None, redis_store=None):
        # Injectable so a live KafkaBackend (real cluster) or an InMemoryBus
        # (hermetic tests / offline drills) can drive the same coordinator -
        # and likewise a real RedisStreamStore or the Mock store.
        self.kafka_client: EventBus = kafka_client or get_kafka_client()
        self.redis_store = redis_store if redis_store is not None else get_redis_store()
        self.stats = {
            "dual_write_total": 0,
            "redis_success": 0,
            "kafka_success": 0,
            "parity_mismatches": 0,
            "avg_redis_latency_ms": 0.0,
            "avg_kafka_latency_ms": 0.0,
        }

    def publish_dual(
        self,
        event_type: str,
        aggregate: str,
        aggregate_id: int,
        payload: dict,
        metadata: dict | None = None,
    ) -> dict:
        """Publish event to both Redis Streams and Kafka."""
        meta = dict(metadata or {})
        # ONE event_id for both copies: it is the consumers' idempotency key (DI-05),
        # so a Redis-path consumer must see the same id a Kafka-path consumer sees.
        meta["event_id"] = meta.get("event_id") or f"evt-{uuid.uuid4().hex}"
        payload_json = json.dumps(payload, default=str, sort_keys=True)
        payload_hash = payload_digest(payload)

        # 1. Publish to Redis Streams (Legacy/Retiring Primary)
        stream_key = f"fix:events:{event_type.split('.')[0]}"
        t_redis_start = time.perf_counter()
        redis_msg_id = self.redis_store.xadd(
            stream_key,
            {
                "event_id": meta["event_id"],
                "event_type": event_type,
                "aggregate": aggregate,
                "aggregate_id": str(aggregate_id),
                "payload": payload_json,
                "payload_sha256": payload_hash,
                "correlation_id": meta.get("correlation_id", ""),
                "causation_id": meta.get("causation_id", ""),
                "emitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )
        t_redis_end = time.perf_counter()

        # 2. Publish to Kafka (New Primary)
        t_kafka_start = time.perf_counter()
        kafka_meta = dict(meta)
        kafka_meta["redis_msg_id"] = redis_msg_id
        kafka_meta["payload_sha256"] = payload_hash
        kafka_rec: KafkaRecord = self.kafka_client.produce(
            event_type=event_type,
            aggregate=aggregate,
            aggregate_id=aggregate_id,
            payload=payload,
            metadata=kafka_meta,
        )
        t_kafka_end = time.perf_counter()

        # 3. Update stats
        self.stats["dual_write_total"] += 1
        self.stats["redis_success"] += 1
        self.stats["kafka_success"] += 1

        redis_lat = (t_redis_end - t_redis_start) * 1000.0
        kafka_lat = (t_kafka_end - t_kafka_start) * 1000.0

        n = self.stats["dual_write_total"]
        self.stats["avg_redis_latency_ms"] = (
            self.stats["avg_redis_latency_ms"] * (n - 1) + redis_lat
        ) / n
        self.stats["avg_kafka_latency_ms"] = (
            self.stats["avg_kafka_latency_ms"] * (n - 1) + kafka_lat
        ) / n

        return {
            "event_id": meta["event_id"],
            "event_type": event_type,
            "redis_stream": stream_key,
            "redis_msg_id": redis_msg_id,
            "kafka_topic": kafka_rec.topic,
            "kafka_partition": kafka_rec.partition,
            "kafka_offset": kafka_rec.offset,
            "payload_sha256": payload_hash,
        }

    def verify_parity(self, event_type: str) -> dict:
        """Audit parity between Redis Streams and Kafka topic for an event family."""
        import collections

        stream_key = f"fix:events:{event_type.split('.')[0]}"
        topic_name = f"fix.events.{event_type.split('.')[0]}"

        redis_msgs = self.redis_store.get_messages(stream_key)
        kafka_recs = self.kafka_client.get_topic_records(topic_name)

        redis_hashes = [m["fields"]["payload_sha256"] for m in redis_msgs]
        kafka_hashes = [r.headers.get("payload_sha256") for r in kafka_recs]

        # 1. Multiset parity: exactly same message set & payload hashes
        count_match = len(redis_hashes) == len(kafka_hashes)
        multiset_match = collections.Counter(redis_hashes) == collections.Counter(kafka_hashes)

        # 2. Per-partition key FIFO sequence verification
        key_ordering_match = True
        redis_by_key: dict[str, list[str]] = collections.defaultdict(list)
        for m in redis_msgs:
            k = f"{m['fields'].get('aggregate', '')}:{m['fields'].get('aggregate_id', '')}"
            redis_by_key[k].append(m["fields"]["payload_sha256"])

        kafka_by_key: dict[str, list[str]] = collections.defaultdict(list)
        for r in kafka_recs:
            kafka_by_key[r.key].append(r.headers.get("payload_sha256"))

        for k, hashes in redis_by_key.items():
            if kafka_by_key.get(k) != hashes:
                key_ordering_match = False
                break

        is_parity = count_match and multiset_match and key_ordering_match
        discrepancies = (
            0
            if is_parity
            else (
                abs(len(redis_hashes) - len(kafka_hashes))
                or sum(
                    (collections.Counter(redis_hashes) - collections.Counter(kafka_hashes)).values()
                )
                or (0 if key_ordering_match else 1)
            )
        )

        return {
            "stream_key": stream_key,
            "kafka_topic": topic_name,
            "redis_count": len(redis_hashes),
            "kafka_count": len(kafka_hashes),
            "parity_match": is_parity,
            "key_ordering_match": key_ordering_match,
            "discrepancies": discrepancies,
        }


_global_dual_bus: DualWriteEventBus | None = None


def get_dual_bus() -> DualWriteEventBus:
    global _global_dual_bus
    if _global_dual_bus is None:
        _global_dual_bus = DualWriteEventBus()
    return _global_dual_bus
