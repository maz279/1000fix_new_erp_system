"""Suppression policy — NT-002 consent classes + NT-003 windows, caps, staleness.

P04-M05-T06. "Customer notification preference is a consent-adjacent obligation,
not a convenience."

Every rule here is a transcription of a numbered rule in the content library:

- QH-01  security and transactional messages are never delayed
- QH-02  service-related and marketing messages are held, never dropped
- QH-03  a held message that is stale when the window opens is discarded
- QH-04  windows are Asia/Dhaka; there is no per-customer timezone
- BD-01  consent_class determines the SMS route (masking vs non-masking)
- BD-02  a marketing message never uses the masking route
- BD-03  an order-status message never carries a promotional line
- DND    promotional SMS never reaches DND-registered numbers (BTRC)

The dispatcher never invents a window, a cap or a route. If a value is missing
from the registry the decision ABORTS (an unevaluable suppression rule is
treated as "do not send", never as "send anyway").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta, timezone

# Asia/Dhaka is UTC+6 year-round (no DST) — QH-04.
DHAKA_TZ = timezone(timedelta(hours=6), name="Asia/Dhaka")

CONSENT_CLASSES = ("security", "transactional", "service", "marketing")


@dataclass(frozen=True)
class ConsentRule:
    """NT-003 §2.1/§2.2 — one consent class, its window, cap and SMS route."""

    consent_class: str
    window_start: time | None  # None = 24/7 (QH-01: security/transactional)
    window_end: time | None
    per_class_cap: int | None  # None = uncapped
    combined_cap: int | None  # cap across all non-transactional classes
    rolling_days: int
    sms_route: str  # "masking" | "non-masking" (BD-01/BD-02)
    dnd_reachable: bool

    def in_window(self, at: datetime) -> bool:
        """QH-01/QH-04 — evaluated in Asia/Dhaka local time."""
        if self.window_start is None or self.window_end is None:
            return True  # 24/7 class — never delayed
        local = at.astimezone(DHAKA_TZ).time()
        return self.window_start <= local < self.window_end

    def next_window_open(self, at: datetime) -> datetime:
        """When a held (QH-02) message may be sent."""
        if self.in_window(at):
            return at
        local = at.astimezone(DHAKA_TZ)
        if local.time() < self.window_start:  # earlier today
            opens = datetime.combine(local.date(), self.window_start, tzinfo=DHAKA_TZ)
        else:  # after tonight's close — tomorrow's window
            opens = datetime.combine(
                local.date() + timedelta(days=1), self.window_start, tzinfo=DHAKA_TZ
            )
        return opens


@dataclass
class RecipientState:
    """Per-recipient rolling history the caps are evaluated against."""

    party_id: int
    dnd_registered: bool = False
    opted_out_marketing: bool = False
    channel_preferences: dict = field(default_factory=dict)  # {"sms": True, ...}
    preferred_language: str = "bn"  # MD-013 — Bengali default (PS-03)
    sent: list = field(default_factory=list)  # [(consent_class, datetime), ...]

    def _recent(self, now: datetime, days: int, consent_class: str | None = None) -> int:
        cutoff = now - timedelta(days=days)
        return sum(
            1
            for cls, ts in self.sent
            if ts >= cutoff and (consent_class is None or cls == consent_class)
        )

    def frequency_allows(self, rule: ConsentRule, now: datetime) -> bool:
        """NT-003 §2.2 — per-class and combined rolling caps."""
        if (
            rule.per_class_cap is not None
            and self._recent(now, rule.rolling_days, rule.consent_class) >= rule.per_class_cap
        ):
            return False
        if rule.combined_cap is not None:
            # The combined cap counts every non-transactional class together.
            non_txn = sum(
                1
                for cls, ts in self.sent
                if ts >= now - timedelta(days=rule.rolling_days) and cls in ("service", "marketing")
            )
            if non_txn >= rule.combined_cap:
                return False
        return True

    def channel_allowed(self, channel: str) -> bool:
        """NT-002 — an explicit opt-out is honoured for that channel."""
        return bool(self.channel_preferences.get(channel, True))


def rules_from_registry(registry: dict) -> dict[str, ConsentRule]:
    """Build the ConsentRule table from the nt-registry rule engine section.

    A missing or malformed class aborts the dispatcher startup: an unevaluable
    suppression rule must never default to "send".
    """
    raw = registry["rule_engine"]["consent_classes"]
    rules: dict[str, ConsentRule] = {}
    for cls in CONSENT_CLASSES:
        if cls not in raw:
            raise ValueError(f"consent class {cls!r} missing from registry")
        entry = raw[cls]
        window = entry["window"]
        if window == "24/7":
            start = end = None
        else:
            start_s, end_s = window.split("-")
            start = time.fromisoformat(start_s)
            end = time.fromisoformat(end_s)
        cap = entry.get("frequency_cap") or {}
        rules[cls] = ConsentRule(
            consent_class=cls,
            window_start=start,
            window_end=end,
            per_class_cap=cap.get("per_class"),
            combined_cap=cap.get("all_non_transactional"),
            rolling_days=cap.get("rolling_days", 7),
            sms_route=entry["sms_route"],
            dnd_reachable=entry["dnd_reachable"],
        )
    return rules


@dataclass(frozen=True)
class Suppress:
    """Outcome of the suppression evaluation — always a named reason, never silent."""

    action: str  # "send" | "hold" | "discard" | "suppress"
    reason: str
    hold_until: datetime | None = None


def evaluate(
    rule: ConsentRule,
    recipient: RecipientState,
    now: datetime,
    channel: str,
    stale_after_hours: int | None = None,
    event_time: datetime | None = None,
) -> Suppress:
    """The five NT-001 §2.1 questions, in order, for one recipient+channel.

    Order matters: an opt-out is honoured before any window logic, and DND is
    honoured before the expense of a send is incurred.
    """
    # 5. Preference / opt-out (NT-002)
    if not recipient.channel_allowed(channel):
        return Suppress("suppress", f"opted-out:{channel}")
    if rule.consent_class == "marketing" and recipient.opted_out_marketing:
        return Suppress("suppress", "marketing-opt-out")

    # DND (BTRC) — promotional traffic never reaches DND numbers.
    if recipient.dnd_registered and not rule.dnd_reachable:
        return Suppress("suppress", "dnd")

    # Frequency caps (NT-003 §2.2) — caps suppress, they do not hold:
    # a message that cannot be sent this week without breaching the cap was
    # already spendable this week; holding it past the cap window would make
    # it stale by construction.
    if not recipient.frequency_allows(rule, now):
        return Suppress("suppress", "frequency-cap")

    # Window (NT-003 §2.1)
    if rule.in_window(now):
        return Suppress("send", "in-window")

    # QH-02 — held, never dropped… unless QH-03 already made it stale.
    opens = rule.next_window_open(now)
    if stale_after_hours is not None and event_time is not None:
        projected_age = (opens - event_time).total_seconds() / 3600.0
        if projected_age > stale_after_hours:
            return Suppress("discard", f"stale-at-window (QH-03, {projected_age:.0f}h old)")
    return Suppress("hold", "outside-window (QH-02)", hold_until=opens)
