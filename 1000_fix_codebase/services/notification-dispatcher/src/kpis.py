"""Notification KPIs — P04-M05-T10 (DoD-09).

Delivery rate, latency, channel mix, opt-out rate — the four M25 needs in
Phase 7. OTP bodies are never counted (NT-007 security rule) and message text
never enters a KPI.
"""

from __future__ import annotations

from dataclasses import dataclass

from .delivery import DeliveryRecord


@dataclass
class Snapshot:
    total: int = 0
    delivered: int = 0
    failed: int = 0
    suppressed: int = 0
    held: int = 0
    discarded: int = 0
    dead: int = 0
    opt_outs: int = 0
    latencies_ms: tuple = ()

    @property
    def delivery_rate(self) -> float:
        decided = self.total - self.held  # held messages are undecided, not undelivered
        return round(self.delivered / decided, 4) if decided else 1.0

    @property
    def p50_latency_ms(self) -> int | None:
        if not self.latencies_ms:
            return None
        ordered = sorted(self.latencies_ms)
        return ordered[len(ordered) // 2]

    @property
    def p95_latency_ms(self) -> int | None:
        if not self.latencies_ms:
            return None
        ordered = sorted(self.latencies_ms)
        return ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]

    @property
    def opt_out_rate(self) -> float:
        return round(self.opt_outs / self.total, 4) if self.total else 0.0


def snapshot(records: list[DeliveryRecord]) -> Snapshot:
    """Reduce delivery records to the four KPI families."""
    latencies = []
    counts = {"delivered": 0, "failed": 0, "suppressed": 0, "held": 0, "discarded": 0, "dead": 0}
    opt_outs = 0
    for record in records:
        # OTP events are excluded from KPI aggregates entirely (NT-007).
        if record.event == "security.otp_requested":
            continue
        counts[record.state if record.state in counts else "failed"] += 1
        if record.state == "delivered" and record.latency_ms is not None:
            latencies.append(record.latency_ms)
        for attempt in record.attempts:
            if attempt.detail.startswith("opted-out") or attempt.detail == "marketing-opt-out":
                opt_outs += 1
                break
    total = sum(counts.values())
    return Snapshot(
        total=total,
        delivered=counts["delivered"],
        failed=counts["failed"],
        suppressed=counts["suppressed"],
        held=counts["held"],
        discarded=counts["discarded"],
        dead=counts["dead"],
        opt_outs=opt_outs,
        latencies_ms=tuple(latencies),
    )


def channel_mix(records: list[DeliveryRecord]) -> dict[str, int]:
    """Deliveries per final channel — the channel-mix KPI."""
    mix: dict[str, int] = {}
    for record in records:
        if record.state == "delivered" and record.final_channel:
            mix[record.final_channel] = mix.get(record.final_channel, 0) + 1
    return dict(sorted(mix.items(), key=lambda kv: -kv[1]))
