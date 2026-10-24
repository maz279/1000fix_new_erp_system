# libs/py/fix_events/kafka_backend.py — the REAL Kafka transport for the event bus (FF-28 / R07).
"""Real Kafka backend for the 1000FiX event bus (R07-M01 rework).

Transport: kafka-python-ng (maintained pure-Python client, Py3.12). Everything
that is NOT transport is shared with the in-memory bus (kafka_bus.py), which is
the single source of the semantics:

- CloudEvents / FixEvent envelope            -> kafka_bus.build_envelope
- topic mapping fix.events.<domain>          -> kafka_bus.map_topic_for_event
- partition key aggregate:aggregate_id       -> kafka_bus.build_message_key
  (per-entity ordering is the broker's murmur2 key partitioning; the in-memory
  bus mimics it with md5 - that hash difference is transport, not semantics)
- DLQ diagnosis headers                      -> kafka_bus.dlq_headers
- offset tracking                            -> real consumer-group commits
- replay index (offsets-for-times)           -> broker OffsetFromTimestamp lookups

Connection: ``KAFKA_BOOTSTRAP_SERVERS`` (comma-separated; default
127.0.0.1:9092,9094,9095 — the host ports of the 3-broker cluster in
infra/compose/docker-compose.asset-ml.yml).

The constructor performs no network I/O (connections are opened lazily on
first use), so building the default client via ``get_kafka_client()`` is safe
in environments without brokers; only produce/consume connect.
"""

from __future__ import annotations

import contextlib
import json
import logging
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kafka import KafkaConsumer, KafkaProducer  # type: ignore[import-untyped]
    from kafka.admin import KafkaAdminClient  # type: ignore[import-untyped]
    from kafka.structs import TopicPartition  # type: ignore[import-untyped]

# kafka-python-ng is imported LAZILY (inside _kafka imports below): the
# stdlib-only service images (identity-lifecycle, notification-dispatcher)
# ship fix_events for the envelope semantics without the broker client;
# constructing the real transport requires the dependency and imports it
# exactly then (a missing module at TRANSPORT time is a clear ImportError,
# not a boot-time crash of a service that never touches Kafka).


def _kafka():
    """Import the kafka client library on first real transport use."""
    from kafka import KafkaConsumer, KafkaProducer  # type: ignore[import-untyped]

    return KafkaConsumer, KafkaProducer


def _kafka_admin():
    from kafka.admin import KafkaAdminClient, NewTopic  # type: ignore[import-untyped]

    return KafkaAdminClient, NewTopic


def _kafka_errors():
    from kafka.errors import TopicAlreadyExistsError  # type: ignore[import-untyped]

    return TopicAlreadyExistsError


def _kafka_structs():
    from kafka.structs import OffsetAndMetadata, TopicPartition  # type: ignore[import-untyped]

    return OffsetAndMetadata, TopicPartition


from .kafka_bus import (  # noqa: E402 - lazy kafka importers sit above on purpose
    InMemoryBus,
    KafkaRecord,
    bootstrap_servers_env,
    build_envelope,
    build_message_key,
    default_headers,
    dlq_headers,
    kafka_security_kwargs,
    map_topic_for_event,
)

logger = logging.getLogger(__name__)

_POLL_EMPTY_STREAK = 3
_POLL_TIMEOUT_MS = 400
# How many times a poll/produce may recover a dead broker connection by
# recreating the client (kafka-python on Windows can raise
# "Invalid file descriptor: -1" from its selector when a connection dies
# mid-poll; the client does not self-heal, a fresh client does).
_MAX_DEAD_CONN_RECOVERIES = 3


def _is_dead_connection_error(exc: BaseException) -> bool:
    return isinstance(exc, ValueError) and "file descriptor" in str(exc).lower()


def _encode_headers(headers: dict) -> list[tuple[str, bytes]]:
    """kafka-python header form: list of (name, bytes); None values are dropped."""
    return [(k, str(v).encode("utf-8")) for k, v in headers.items() if v is not None]


def _decode_headers(headers: list[tuple[str, bytes]] | None) -> dict:
    if not headers:
        return {}
    return {
        k: (v.decode("utf-8", errors="replace") if isinstance(v, bytes) else str(v))
        for k, v in headers
    }


def _commit_next(consumer: KafkaConsumer, tp: TopicPartition, next_offset: int) -> None:
    """Commit the group's next offset for one partition (blocking, sync)."""
    _OAM, _TP = _kafka_structs()
    consumer.commit(offsets={tp: _OAM(next_offset, "")})


class KafkaBackend:
    """Event bus over a real Kafka cluster (same API surface as InMemoryBus)."""

    def __init__(
        self,
        bootstrap_servers: list[str] | None = None,
        num_partitions: int = 3,
        replication_factor: int = 3,
        client_id: str = "fix-events",
        produce_timeout_s: float = 30.0,
        consume_deadline_s: float = 20.0,
    ):
        self.bootstrap_servers = bootstrap_servers or bootstrap_servers_env()
        self._security = kafka_security_kwargs()
        self.num_partitions = num_partitions
        self.replication_factor = replication_factor
        self.client_id = client_id
        self.produce_timeout_s = produce_timeout_s
        self.consume_deadline_s = consume_deadline_s
        self._producer: KafkaProducer | None = None
        self._admin: KafkaAdminClient | None = None
        self._reader: KafkaConsumer | None = None
        self._group_consumers: dict[str, KafkaConsumer] = {}
        self._ensured_topics: set[str] = set()
        self._closed = False

    # ------------------------------------------------------------ connections

    def _check_open(self) -> None:
        if self._closed:
            raise RuntimeError("KafkaBackend is closed")

    def _ensure_producer(self) -> KafkaProducer:
        self._check_open()
        if self._producer is None:
            _KafkaConsumer, _KafkaProducer = _kafka()
            self._producer = _KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                acks="all",
                **self._security,  # RF=3 / min ISR=2 cluster: a write survives a broker loss
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
        return self._producer

    def _ensure_admin(self) -> KafkaAdminClient:
        self._check_open()
        if self._admin is None:
            _Admin, _NewTopic = _kafka_admin()
            self._admin = _Admin(
                bootstrap_servers=self.bootstrap_servers,
                client_id=f"{self.client_id}-admin",
                **self._security,
            )
        return self._admin

    def _ensure_reader(self) -> KafkaConsumer:
        """Group-less consumer for read-only scans (assign/seek, no commits)."""
        self._check_open()
        if self._reader is None:
            _KafkaConsumer, _KafkaProducer = _kafka()
            self._reader = _KafkaConsumer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=f"{self.client_id}-reader",
                group_id=None,
                **self._security,
                enable_auto_commit=False,
                value_deserializer=lambda b: json.loads(b.decode("utf-8")),
            )
        return self._reader

    def _ensure_consumer(self, consumer_group: str) -> KafkaConsumer:
        """Group consumer for offset-tracked reads and commits.

        Deliberately never ``subscribe()``d: joining the group spins up a
        heartbeat thread that races the poll loop on some platforms
        (kafka-python "Invalid file descriptor: -1"). Instead every read
        assigns partitions explicitly and seeks to the group's committed
        offsets (see :meth:`consume`) — same offset semantics, no rebalance.
        """
        self._check_open()
        consumer = self._group_consumers.get(consumer_group)
        if consumer is None:
            _KafkaConsumer, _KafkaProducer = _kafka()
            consumer = _KafkaConsumer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=f"{self.client_id}-{consumer_group}",
                group_id=consumer_group,
                **self._security,
                enable_auto_commit=False,
                value_deserializer=lambda b: json.loads(b.decode("utf-8")),
            )
            self._group_consumers[consumer_group] = consumer
        return consumer

    def _drop_producer(self) -> None:
        if self._producer is not None:
            with contextlib.suppress(Exception):
                self._producer.close(timeout=5)
            self._producer = None

    def _drop_reader(self) -> None:
        if self._reader is not None:
            with contextlib.suppress(Exception):
                self._reader.close()
            self._reader = None

    def _recreate_group_consumer(
        self, consumer_group: str, topic: str, partitions: list[int]
    ) -> KafkaConsumer:
        """Replace a group consumer whose client died mid-poll (dead connection).

        Safe by the bus's at-least-once contract: offsets commit per handled
        record, so the recreated consumer resumes at the group's committed
        position and may re-deliver the in-flight batch only.
        """
        old = self._group_consumers.pop(consumer_group, None)
        if old is not None:
            with contextlib.suppress(Exception):
                old.close()
        consumer = self._ensure_consumer(consumer_group)
        self._assign_from_committed(consumer, topic, partitions)
        return consumer

    def _send_and_await(self, topic: str, message: dict) -> Any:
        """Produce one message (acks=all, sync) with dead-connection recovery."""
        for attempt in range(_MAX_DEAD_CONN_RECOVERIES + 1):
            producer = self._ensure_producer()
            try:
                return producer.send(topic, **message).get(timeout=self.produce_timeout_s)
            except ValueError as exc:
                if not _is_dead_connection_error(exc) or attempt >= _MAX_DEAD_CONN_RECOVERIES:
                    raise
                logger.warning(
                    "kafka_backend: produce to %s hit a dead connection (%s); "
                    "recreating producer (attempt %d, at-least-once redelivery)",
                    topic,
                    exc,
                    attempt + 1,
                )
                self._drop_producer()
        raise RuntimeError("produce retry loop exhausted")  # pragma: no cover

    def _fetch_committed(
        self, consumer: KafkaConsumer, tps: list[TopicPartition]
    ) -> dict[TopicPartition, int | None]:
        """Fresh committed-offset fetch (bypasses the consumer's assignment cache).

        ``KafkaConsumer.committed()`` serves the CACHED value for partitions
        still assigned to the consumer, so a consumer reused across calls would
        read offsets it saw earlier instead of what the group committed since.
        Clearing the assignment first forces the remote OffsetFetch branch.
        """
        if consumer.assignment():
            consumer.assign([])
        return {tp: consumer.committed(tp) for tp in tps}

    def _assign_from_committed(
        self, consumer: KafkaConsumer, topic: str, partitions: list[int]
    ) -> list[TopicPartition]:
        """Assign partitions and seek each to the group's committed offset (else 0)."""
        _OffsetAndMetadata, _TopicPartition = _kafka_structs()
        tps = [_TopicPartition(topic, p) for p in partitions]
        committed = self._fetch_committed(consumer, tps)
        consumer.assign(tps)
        for tp in tps:
            consumer.seek(tp, committed[tp] if committed[tp] is not None else 0)
        return tps

    # ------------------------------------------------------------ topics

    def ensure_topics(self, topics: list[str]) -> None:
        """Create missing topics with the cluster's replication policy (idempotent)."""
        admin = self._ensure_admin()
        existing = set(admin.list_topics())
        missing = [t for t in topics if t not in existing and t not in self._ensured_topics]
        if not missing:
            self._ensured_topics.update(topics)
            return
        _Admin, _NewTopic = _kafka_admin()
        _TopicAlreadyExistsError = _kafka_errors()
        new_topics = [
            _NewTopic(
                name=t,
                num_partitions=self.num_partitions,
                replication_factor=self.replication_factor,
                topic_configs={"min.insync.replicas": "2"},
            )
            for t in missing
        ]
        # A race with another producer only means the topic exists: all we need.
        with contextlib.suppress(_TopicAlreadyExistsError):
            admin.create_topics(new_topics)
        self._ensured_topics.update(topics)
        logger.debug("kafka_backend: ensured topics %s", topics)

    def topic_partitions(self, topic: str) -> list[int]:
        """Existing partitions of a topic ([] when the topic does not exist)."""
        reader = self._ensure_reader()
        parts = reader.partitions_for_topic(topic)
        return sorted(parts) if parts else []

    # ------------------------------------------------------------ produce

    def produce(
        self,
        event_type: str,
        aggregate: str,
        aggregate_id: int,
        payload: dict,
        metadata: dict | None = None,
    ) -> KafkaRecord:
        """Produce a domain event with the shared FixEvent envelope (acks=all)."""
        topic = map_topic_for_event(event_type)
        if topic not in self._ensured_topics:
            self.ensure_topics([topic])

        key = build_message_key(aggregate, aggregate_id)
        headers = default_headers(metadata)
        envelope = build_envelope(event_type, aggregate, aggregate_id, payload, headers)
        meta = self._send_and_await(
            topic,
            {"key": key.encode("utf-8"), "value": envelope, "headers": _encode_headers(headers)},
        )

        rec = KafkaRecord(
            topic=meta.topic,
            partition=meta.partition,
            offset=meta.offset,
            key=key,
            value=envelope,
            headers=headers,
            timestamp=time.time(),
        )
        logger.debug(
            "kafka_backend: produced %s to %s[%d] offset %d",
            event_type,
            topic,
            rec.partition,
            rec.offset,
        )
        return rec

    # ------------------------------------------------------------ consume

    def consume(
        self,
        consumer_group: str,
        topic: str,
        handler: Callable[[dict], None],
        limit: int = 50,
        dlq_on_failure: bool = True,
    ) -> int:
        """Consume up to ``limit`` records for a group; offsets commit per record.

        At-least-once: the group's offset advances only past handled records
        (or dead-lettered ones); with ``dlq_on_failure=False`` a handler error
        propagates and the failed record stays at the head of the group.
        """
        partitions = self.topic_partitions(topic)
        if not partitions:
            return 0
        consumer = self._ensure_consumer(consumer_group)
        self._assign_from_committed(consumer, topic, partitions)
        dlq_topic = f"{topic}.dlq"
        processed = 0
        recoveries = 0
        empty_streak = 0
        deadline = time.monotonic() + self.consume_deadline_s

        while processed < limit and time.monotonic() < deadline:
            try:
                batch = consumer.poll(timeout_ms=_POLL_TIMEOUT_MS, max_records=limit - processed)
            except ValueError as exc:
                if not _is_dead_connection_error(exc) or recoveries >= _MAX_DEAD_CONN_RECOVERIES:
                    raise
                recoveries += 1
                logger.warning(
                    "kafka_backend: poll for %s hit a dead connection (%s); recreating "
                    "consumer (attempt %d)",
                    consumer_group,
                    exc,
                    recoveries,
                )
                consumer = self._recreate_group_consumer(consumer_group, topic, partitions)
                empty_streak = 0
                continue
            if not batch:
                empty_streak += 1
                if empty_streak >= _POLL_EMPTY_STREAK:
                    break  # caught up (or still joining): nothing more available now
                continue
            empty_streak = 0
            for tp, records in batch.items():
                for kr in records:
                    rec = KafkaRecord(
                        topic=kr.topic,
                        partition=kr.partition,
                        offset=kr.offset,
                        key=kr.key.decode("utf-8") if isinstance(kr.key, bytes) else str(kr.key),
                        value=kr.value,
                        headers=_decode_headers(kr.headers),
                        timestamp=(kr.timestamp / 1000.0)
                        if kr.timestamp and kr.timestamp > 0
                        else time.time(),
                    )
                    try:
                        handler(rec.value)
                    except Exception as ex:
                        logger.error(
                            "kafka_backend: consumer error on %s[%d]:%d — %s",
                            topic,
                            rec.partition,
                            rec.offset,
                            ex,
                        )
                        if dlq_on_failure:
                            self.route_to_dlq(dlq_topic, rec, str(ex))
                            _commit_next(consumer, tp, kr.offset + 1)
                            processed += 1
                        else:
                            # Keep the failed record at the head of the group:
                            # commit up to (not past) it, then propagate.
                            _commit_next(consumer, tp, kr.offset)
                            raise
                    else:
                        _commit_next(consumer, tp, kr.offset + 1)
                        processed += 1
        return processed

    def route_to_dlq(
        self, dlq_topic: str, failed_record: KafkaRecord, error_msg: str
    ) -> KafkaRecord:
        """Route failed record to the Dead-Letter Queue with diagnosis headers."""
        if dlq_topic not in self._ensured_topics:
            self.ensure_topics([dlq_topic])
        headers = dlq_headers(failed_record, error_msg)
        meta = self._send_and_await(
            dlq_topic,
            {
                "key": failed_record.key.encode("utf-8"),
                "value": failed_record.value,
                "headers": _encode_headers(headers),
            },
        )
        return KafkaRecord(
            topic=meta.topic,
            partition=meta.partition,
            offset=meta.offset,
            key=failed_record.key,
            value=failed_record.value,
            headers=headers,
            timestamp=time.time(),
        )

    # ------------------------------------------------------------ replay / audit

    def seek_to_timestamp(self, topic: str, timestamp_s: float) -> dict[int, int]:
        """Per-partition offset of the first record at/after a timestamp (replay index).

        A partition with no record that late maps to its log end, matching the
        in-memory semantics. A missing topic maps to {} (no auto-creation).
        """
        parts = self.topic_partitions(topic)
        if not parts:
            return {}
        reader = self._ensure_reader()
        _OAM, _TP = _kafka_structs()
        tps = [_TP(topic, p) for p in parts]
        by_time = reader.offsets_for_times({tp: int(timestamp_s * 1000) for tp in tps}) or {}
        ends = reader.end_offsets(tps)
        result: dict[int, int] = {}
        for tp in tps:
            hit = by_time.get(tp)
            result[tp.partition] = hit.offset if hit is not None else ends[tp]
        return result

    def read_topic_from(
        self, topic: str, offsets: dict[int, int], limit_per_partition: int = 10000
    ) -> list[KafkaRecord]:
        """Read-only scan from per-partition offsets, merged chronologically."""
        wanted = {p: start for p, start in offsets.items() if start is not None}
        parts = [p for p in self.topic_partitions(topic) if p in wanted]
        if not parts:
            return []
        reader = self._ensure_reader()
        _OAM, _TP = _kafka_structs()
        tps = [_TP(topic, p) for p in parts]
        reader.assign(tps)
        for tp in tps:
            reader.seek(tp, wanted[tp.partition])

        records: list[KafkaRecord] = []
        fetched = {tp.partition: 0 for tp in tps}
        empty_streak = 0
        recoveries = 0
        deadline = time.monotonic() + self.consume_deadline_s
        while (
            any(fetched[p.partition] < limit_per_partition for p in tps)
            and empty_streak < _POLL_EMPTY_STREAK
            and time.monotonic() < deadline
        ):
            try:
                batch = reader.poll(timeout_ms=_POLL_TIMEOUT_MS)
            except ValueError as exc:
                if not _is_dead_connection_error(exc) or recoveries >= _MAX_DEAD_CONN_RECOVERIES:
                    raise
                recoveries += 1
                logger.warning(
                    "kafka_backend: scan of %s hit a dead connection (%s); recreating "
                    "reader (attempt %d)",
                    topic,
                    exc,
                    recoveries,
                )
                self._drop_reader()
                reader = self._ensure_reader()
                reader.assign(tps)
                for tp in tps:  # resume each partition where the scan left it
                    reader.seek(tp, wanted[tp.partition] + fetched[tp.partition])
                continue
            if not batch:
                empty_streak += 1
                continue
            empty_streak = 0
            for tp, krs in batch.items():
                for kr in krs:
                    if fetched[tp.partition] >= limit_per_partition:
                        break
                    fetched[tp.partition] += 1
                    records.append(
                        KafkaRecord(
                            topic=kr.topic,
                            partition=kr.partition,
                            offset=kr.offset,
                            key=kr.key.decode("utf-8")
                            if isinstance(kr.key, bytes)
                            else str(kr.key),
                            value=kr.value,
                            headers=_decode_headers(kr.headers),
                            timestamp=(kr.timestamp / 1000.0)
                            if kr.timestamp and kr.timestamp > 0
                            else time.time(),
                        )
                    )
        reader.unsubscribe()
        records.sort(key=lambda r: (r.timestamp, r.offset))
        return records

    def get_topic_records(self, topic: str) -> list[KafkaRecord]:
        """Every record on a topic, merged chronologically ([] if it doesn't exist)."""
        parts = self.topic_partitions(topic)
        return self.read_topic_from(topic, dict.fromkeys(parts, 0)) if parts else []

    def committed_offsets(self, consumer_group: str, topic: str) -> dict[int, int]:
        """Offsets committed by a consumer group ({} when nothing is committed).

        Read-only: a fresh OffsetFetch per partition (never the consumer's
        assignment cache); no group join is forced.
        """
        consumer = self._ensure_consumer(consumer_group)
        parts = self.topic_partitions(topic)
        if not parts:
            return {}
        _OAM, _TP = _kafka_structs()
        fetched = self._fetch_committed(consumer, [_TP(topic, p) for p in parts])
        return {tp.partition: off for tp, off in fetched.items() if off is not None}

    def commit_offsets(self, consumer_group: str, topic: str, offsets: dict[int, int]) -> None:
        """Commit next-offset-per-partition for a group (explicit offset commit).

        The group is never joined (simple-consumer commit): the process-wide
        consumer keeps no membership, so no rebalance can race the commit.
        """
        consumer = self._ensure_consumer(consumer_group)
        _OAM, _TP = _kafka_structs()
        consumer.commit(offsets={_TP(topic, p): _OAM(off, "") for p, off in offsets.items()})

    # ------------------------------------------------------------ lifecycle

    def close(self) -> None:
        """Flush and close every connection (idempotent)."""
        self._closed = True
        if self._producer is not None:
            try:
                self._producer.flush(timeout=10)
                self._producer.close(timeout=10)
            except Exception as exc:  # pragma: no cover - teardown best effort
                logger.warning("kafka_backend: producer close failed: %s", exc)
            self._producer = None
        for consumer in self._group_consumers.values():
            try:
                consumer.close()
            except Exception as exc:  # pragma: no cover - teardown best effort
                logger.warning("kafka_backend: consumer close failed: %s", exc)
        self._group_consumers.clear()
        if self._reader is not None:
            try:
                self._reader.close()
            except Exception as exc:  # pragma: no cover - teardown best effort
                logger.warning("kafka_backend: reader close failed: %s", exc)
            self._reader = None
        if self._admin is not None:
            try:
                self._admin.close()
            except Exception as exc:  # pragma: no cover - teardown best effort
                logger.warning("kafka_backend: admin close failed: %s", exc)
            self._admin = None


#: Union of the two transports implementing the bus semantics (for annotations).
EventBus = InMemoryBus | KafkaBackend
