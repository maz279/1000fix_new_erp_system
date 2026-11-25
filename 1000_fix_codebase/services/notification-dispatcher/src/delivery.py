"""Delivery tracking, retry, dead-letter and the fallback register.

P04-M05-T08/T09.

NT-001 §4, transcribed:

| Failure            | Behaviour                                            |
|--------------------|------------------------------------------------------|
| SMS undeliverable  | retry once, then fall back to the next channel       |
| Push not delivered | fall back to SMS for CH-04 events                    |
| Email bounces      | flag the address, notify the account owner, fallback |
| All channels fail  | raise an operational task; do not silently drop      |
| Gateway down       | manual fallback per IP-09 and OP-014                 |

"A notification that silently failed is worse than one that visibly failed."
The dead-letter queue is a first-class citizen: it is inspectable, it ages,
and an ageing DLQ raises the NT-021 integration alert.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

# P0 integrations with a NAMED fallback (IP-09 fallback register, P04-M05-T09).
FALLBACK_REGISTER: dict[str, str] = {
    "INT-010 SMS": "retry once, then email/in-app fallback per matrix; manual bulk re-send per OP-014 if the aggregator is down",
    "INT-011 redundant SMS": "W2 — automatic takeover of INT-010 traffic on route failure",
    "INT-012 WhatsApp": "template-approval-bound; falls back to SMS when the template is rejected",
    "INT-013 email": "Mailpit capture in every non-production environment (EP-11); bounce → flag address + SMS fallback",
    "Novu push": "CH-04 events fall back to SMS immediately; non-urgent push waits for recovery",
}

# How long a DLQ entry may age before it raises the NT-021 alert.
DLQ_ALERT_AFTER = timedelta(hours=1)


@dataclass
class Attempt:
    channel: str
    status: str
    detail: str = ""
    at: float = field(default_factory=time.monotonic)


@dataclass
class DeliveryRecord:
    """One recipient's journey through the channels for one event."""

    event: str
    party_id: int
    recipient: str
    consent_class: str
    language: str
    rendered: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    attempts: list[Attempt] = field(default_factory=list)
    state: str = "pending"  # pending | delivered | dead | suppressed | held | discarded
    final_channel: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    delivered_at: datetime | None = None

    @property
    def latency_ms(self) -> int | None:
        if self.delivered_at is None:
            return None
        return int((self.delivered_at - self.created_at).total_seconds() * 1000)

    def channel_attempt_count(self, channel: str) -> int:
        return sum(1 for a in self.attempts if a.channel == channel)


class DeliveryTracker:
    """In-process tracker. The production deployment persists these records to
    the outbox tables (AS-08); this class keeps the decision logic testable
    without a database."""

    def __init__(self) -> None:
        self.records: list[DeliveryRecord] = []
        self.dead_letters: list[DeliveryRecord] = []
        self.operational_tasks: list[dict] = []

    def open(self, **kwargs) -> DeliveryRecord:
        record = DeliveryRecord(**kwargs)
        self.records.append(record)
        return record

    def record_attempt(
        self, record: DeliveryRecord, channel: str, status: str, detail: str = ""
    ) -> None:
        record.attempts.append(Attempt(channel=channel, status=status, detail=detail))

    def mark_delivered(self, record: DeliveryRecord, channel: str) -> None:
        record.state = "delivered"
        record.final_channel = channel
        record.delivered_at = datetime.now(UTC)

    def mark_suppressed(self, record: DeliveryRecord, reason: str) -> None:
        record.state = "suppressed"
        record.attempts.append(Attempt(channel="(policy)", status="suppressed", detail=reason))

    def mark_held(self, record: DeliveryRecord, reason: str) -> None:
        record.state = "held"
        record.attempts.append(Attempt(channel="(policy)", status="held", detail=reason))

    def mark_discarded(self, record: DeliveryRecord, reason: str) -> None:
        record.state = "discarded"
        record.attempts.append(Attempt(channel="(policy)", status="discarded", detail=reason))

    def should_retry(self, record: DeliveryRecord, channel: str) -> bool:
        """SMS retries exactly once (NT-001 §4); every channel the same rule."""
        return record.channel_attempt_count(channel) < 2

    def mark_dead(self, record: DeliveryRecord, reason: str) -> dict:
        """All channels failed — raise an operational task, never drop silently."""
        record.state = "dead"
        self.dead_letters.append(record)
        task = {
            "task": "notification.all_channels_failed",
            "event": record.event,
            "party_id": record.party_id,
            "record_id": record.id,
            "reason": reason,
            "fallback_register": "IP-09 / OP-014",
            "raised_at": datetime.now(UTC).isoformat(),
        }
        self.operational_tasks.append(task)
        return task

    def dlq_needs_alert(self, now: datetime) -> list[DeliveryRecord]:
        return [r for r in self.dead_letters if now - r.created_at > DLQ_ALERT_AFTER]
