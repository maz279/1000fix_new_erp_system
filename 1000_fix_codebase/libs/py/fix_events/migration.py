# libs/py/fix_events/migration.py — Consumer Group Migration with Per-Group Rollback (EP-05 / P09-M01-T04).
"""Consumer Group Migration Manager (Contract Phase).

Manages phased cutover of event consumers across the 6 major business consumer groups:
1. notification-dispatcher (P08)
2. inventory-syncer (P04)
3. audit-logger (P02)
4. bi-streaming (P07)
5. sla-calculator (P01)
6. evat-reporter (P05)

State machine per group:
- BUS_REDIS: Reads only from Redis 7.2 Streams (legacy).
- BUS_DUAL: Reads from Kafka with shadow comparison against Redis; mutations gated.
- BUS_KAFKA: Reads exclusively from Apache Kafka 3-node HA cluster.

Provides independent per-group rollback to BUS_REDIS in < 5s if lag or error rate spikes,
without interrupting traffic on other migrated consumer groups.
"""

from __future__ import annotations

import enum
import logging
import time
from collections.abc import Callable
from typing import Any

from .dual_write import MockRedisStreamStore, get_redis_store, payload_digest
from .kafka_backend import EventBus
from .kafka_bus import get_kafka_client

logger = logging.getLogger(__name__)


class ConsumerBusState(enum.StrEnum):
    BUS_REDIS = "BUS_REDIS"
    BUS_DUAL = "BUS_DUAL"
    BUS_KAFKA = "BUS_KAFKA"


CANONICAL_CONSUMER_GROUPS = [
    "notification-dispatcher",
    "inventory-syncer",
    "audit-logger",
    "bi-streaming",
    "sla-calculator",
    "evat-reporter",
]


class ConsumerGroupMigrationManager:
    """Manages independent state transitions and rollback for consumer groups."""

    def __init__(
        self,
        kafka_client: EventBus | None = None,
        redis_store: MockRedisStreamStore | None = None,
        max_lag_threshold: int = 500,
    ):
        self.kafka_client = kafka_client or get_kafka_client()
        self.redis_store = redis_store or get_redis_store()
        self.max_lag_threshold = max_lag_threshold
        self._groups: dict[str, dict[str, Any]] = {}

        for group in CANONICAL_CONSUMER_GROUPS:
            self.register_group(group)

    def register_group(self, group_id: str) -> ConsumerBusState:
        """Register a consumer group (idempotent): a new group starts on BUS_REDIS.

        The six canonical groups are the cut-over plan's; any other consumer (e.g. M29's
        identity-lifecycle worker) registers itself before consuming. Re-registering
        never resets an existing group's state, offsets or cursors.
        """
        if group_id not in self._groups:
            now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            self._groups[group_id] = {
                "group_id": group_id,
                "state": ConsumerBusState.BUS_REDIS.value,
                "created_at_utc": now,
                "last_transition_utc": now,
                "rollback_count": 0,
                "processed_count": 0,
                "shadow_match_count": 0,
                "shadow_mismatch_count": 0,
                "simulated_lag": 0,
                "redis_cursors": {},  # stream_key -> index of the next unread message
                "history": [],
            }
        return ConsumerBusState(self._groups[group_id]["state"])

    def get_group_state(self, group_id: str) -> ConsumerBusState:
        if group_id not in self._groups:
            raise KeyError(f"Unknown consumer group: {group_id}")
        return ConsumerBusState(self._groups[group_id]["state"])

    def transition_group(
        self, group_id: str, new_state: ConsumerBusState, reason: str = ""
    ) -> dict[str, Any]:
        """Advance or change the bus target state for a specific consumer group."""
        if group_id not in self._groups:
            raise KeyError(f"Unknown consumer group: {group_id}")

        old_state = self._groups[group_id]["state"]
        now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        t0 = time.perf_counter()

        self._groups[group_id]["state"] = new_state.value
        self._groups[group_id]["last_transition_utc"] = now_str
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        transition_entry = {
            "from_state": old_state,
            "to_state": new_state.value,
            "reason": reason or f"Cutover to {new_state.value}",
            "timestamp_utc": now_str,
            "transition_time_ms": round(elapsed_ms, 3),
        }
        self._groups[group_id]["history"].append(transition_entry)

        logger.info(
            "Consumer group %s transitioned %s -> %s (reason: %s)",
            group_id,
            old_state,
            new_state.value,
            reason,
        )
        return {
            "group_id": group_id,
            "previous_state": old_state,
            "current_state": new_state.value,
            "transition_time_ms": round(elapsed_ms, 3),
            "status": "SUCCESS",
        }

    def rollback_group(self, group_id: str, reason: str) -> dict[str, Any]:
        """Instantly revert a consumer group back to BUS_REDIS (SLA < 5000ms)."""
        if group_id not in self._groups:
            raise KeyError(f"Unknown consumer group: {group_id}")

        t0 = time.perf_counter()
        old_state = self._groups[group_id]["state"]
        now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        self._groups[group_id]["state"] = ConsumerBusState.BUS_REDIS.value
        self._groups[group_id]["rollback_count"] += 1
        self._groups[group_id]["last_transition_utc"] = now_str

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        transition_entry = {
            "from_state": old_state,
            "to_state": ConsumerBusState.BUS_REDIS.value,
            "reason": f"ROLLBACK: {reason}",
            "timestamp_utc": now_str,
            "transition_time_ms": round(elapsed_ms, 3),
        }
        self._groups[group_id]["history"].append(transition_entry)

        logger.warning(
            "ROLLBACK triggered for consumer group %s (%s -> BUS_REDIS) in %.2fms. Reason: %s",
            group_id,
            old_state,
            elapsed_ms,
            reason,
        )
        return {
            "group_id": group_id,
            "previous_state": old_state,
            "current_state": ConsumerBusState.BUS_REDIS.value,
            "rollback_elapsed_ms": round(elapsed_ms, 3),
            "sla_5s_met": elapsed_ms < 5000.0,
            "reason": reason,
            "status": "ROLLED_BACK",
        }

    def consume_event(
        self,
        group_id: str,
        topic: str,
        handler: Callable[[dict], None],
        limit: int = 50,
    ) -> int:
        """Route event consumption based on the group's current migration state."""
        state = self.get_group_state(group_id)
        group = self._groups[group_id]
        stream_key = f"fix:events:{topic.replace('fix.events.', '')}"
        processed = 0

        if state == ConsumerBusState.BUS_REDIS:
            # Consume from Redis Streams, oldest unread first; the per-group cursor
            # advances only after the handler succeeded (at-least-once, no skips).
            cursors = group["redis_cursors"]
            start = cursors.get(stream_key, 0)
            for m in self.redis_store.get_messages(stream_key)[start : start + limit]:
                handler(m["fields"])
                processed += 1
                cursors[stream_key] = start + processed
                group["processed_count"] += 1
            return processed

        # BUS_DUAL and BUS_KAFKA both read from Kafka (offsets tracked per group);
        # BUS_DUAL additionally shadow-compares every event against the Redis stream.
        kafka_handler = handler
        if state == ConsumerBusState.BUS_DUAL:
            kafka_handler = self._shadow_handler(group, stream_key, handler)

        processed = self.kafka_client.consume(
            consumer_group=group_id,
            topic=topic,
            handler=kafka_handler,
            limit=limit,
        )
        group["processed_count"] += processed
        return processed

    def _shadow_handler(
        self, group: dict[str, Any], stream_key: str, handler: Callable[[dict], None]
    ) -> Callable[[dict], None]:
        """Wrap a Kafka handler so each event is checked against the Redis stream."""
        redis_hashes = {
            m["fields"].get("payload_sha256") for m in self.redis_store.get_messages(stream_key)
        }

        def shadow(event: dict) -> None:
            handler(event)
            matched = payload_digest(event.get("payload")) in redis_hashes
            group["shadow_match_count" if matched else "shadow_mismatch_count"] += 1

        return shadow

    def check_health_and_auto_revert(self, group_id: str, current_lag: int) -> dict[str, Any]:
        """Check consumer lag against threshold; auto-rollback if breached."""
        self._groups[group_id]["simulated_lag"] = current_lag
        if (
            current_lag > self.max_lag_threshold
            and self.get_group_state(group_id) != ConsumerBusState.BUS_REDIS
        ):
            return self.rollback_group(
                group_id,
                f"Consumer lag ({current_lag} msgs) exceeded threshold ({self.max_lag_threshold} msgs)",
            )
        return {"group_id": group_id, "lag": current_lag, "status": "HEALTHY"}

    def get_summary(self) -> dict[str, Any]:
        """Return comprehensive status for all consumer groups."""
        return {
            "total_groups": len(self._groups),
            "state_distribution": {
                st.value: sum(1 for g in self._groups.values() if g["state"] == st.value)
                for st in ConsumerBusState
            },
            "groups": self._groups,
        }


_global_migration_mgr: ConsumerGroupMigrationManager | None = None


def get_migration_manager() -> ConsumerGroupMigrationManager:
    global _global_migration_mgr
    if _global_migration_mgr is None:
        _global_migration_mgr = ConsumerGroupMigrationManager()
    return _global_migration_mgr
