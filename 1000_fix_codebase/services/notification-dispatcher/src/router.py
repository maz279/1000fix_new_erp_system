"""Router — NT-001 event-channel matrix + §2.2 channel-selection rules.

P04-M05-T02/T06. "Every module publishes an event; exactly one component
decides how it is delivered" — this module is that component. A domain module
never chooses a channel; it publishes `service.order.estimate_ready` and the
matrix decides SMS + push + email.

Channel-selection rules transcribed:
- CH-01  one event, one primary channel per audience; a second channel needs
         a matrix-stated reason (both three-channel events are in the matrix)
- CH-03  must-be-retrievable → email or in-app, never SMS alone
- CH-04  act-now → push with SMS fallback
- CH-06  internal alerts never go to a customer channel

Fallback ladder per NT-001 §4:
- SMS undeliverable  → retry once, then next channel in the matrix
- push not delivered → SMS for CH-04 events
- email bounce       → flag address + SMS fallback
- all channels fail  → operational task (never silent drop) — delivery.py
"""
from __future__ import annotations

from dataclasses import dataclass

# Audiences that are internal — CH-06 keeps them off customer channels.
INTERNAL_AUDIENCES = frozenset(
    {"technician", "branch", "on_call", "employee", "manager", "approver", "warranty_officer"}
)

CUSTOMER_AUDIENCES = frozenset({"customer", "corporate_admin", "seller", "rider", "vendor", "audience_any"})

# The act-now events (CH-04): push first, SMS fallback.
ACT_NOW_EVENTS = frozenset(
    {"service.order.technician_enroute", "security.otp_requested", "approval.requested"}
)

# Channel fallback ladder, in order, per NT-001 §4.
FALLBACK_LADDER = {
    "sms": ["email", "in_app"],      # after its one retry
    "push": ["sms", "email"],        # CH-04: push → SMS
    "email": ["sms"],                # bounce → flag + SMS
    "in_app": [],                    # reference channel — no fallback, it retries itself
    "alert": ["email"],              # on-call alert → email page
}


class RoutingError(RuntimeError):
    """An event the matrix cannot resolve. Aborts loudly — never guesses."""


@dataclass(frozen=True)
class Routing:
    event: str
    audience: str
    channels: tuple[str, ...]      # primary first
    consent_class: str
    templates: tuple[str, ...]
    wave: str


class Router:
    def __init__(self, registry: dict, active_wave: str = "W1") -> None:
        self.matrix = registry["event_matrix"]
        self.active_wave = active_wave
        self._wave_rank = {"W1": 1, "W2": 2, "W3": 3, "W4": 4, "W5": 5}

    def resolve(self, event: str) -> list[Routing]:
        """All audience routings for one event, matrix order."""
        if event not in self.matrix:
            raise RoutingError(f"event {event!r} is not in the NT-001 matrix")
        row = self.matrix[event]
        if self._wave_rank[row["wave"]] > self._wave_rank[self.active_wave]:
            raise RoutingError(
                f"event {event!r} is a {row['wave']} event; active wave is {self.active_wave} "
                "(the matrix knows about the future; the dispatcher must not act on it)"
            )
        out = []
        for audience, channels in row["channels"].items():
            # CH-06 — internal alerts never go to a customer channel: the
            # `alert` channel (NT-021 on-call) is internal-only. Internal
            # people still receive their own channels (technicians get push
            # via NT-016, branches get in-app via NT-018).
            if "alert" in channels and audience not in INTERNAL_AUDIENCES:
                raise RoutingError(f"{event}/{audience}: alert channel routed to a non-internal audience (CH-06)")
            # CH-04 — act-now events lead with push.
            if event in ACT_NOW_EVENTS and "push" in channels and channels[0] != "push":
                channels = ["push"] + [c for c in channels if c != "push"]
            out.append(
                Routing(
                    event=event,
                    audience=audience,
                    channels=tuple(channels),
                    consent_class=row["consent_class"],
                    templates=tuple(row["templates"]),
                    wave=row["wave"],
                )
            )
        return out

    def fallbacks_for(self, channel: str) -> tuple[str, ...]:
        return tuple(FALLBACK_LADDER.get(channel, ()))
