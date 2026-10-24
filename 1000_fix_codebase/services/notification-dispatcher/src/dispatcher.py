"""Notification dispatcher — P04-M05-T02 (CD-M27-nn).

The single component that decides how a domain event is delivered
(AR-009 / AS-08). Domain modules publish events to the cd_event_outbox;
libs/py/fix_events (FF-28, the ONLY event client) hands them to
`Dispatcher.handle()`; the NT-001 matrix decides audience, channel, language
and suppression; the channel adapters render and send.

Flow of one event::

    fix_events.consume(handler=dispatcher.handle, event_type="*")
      -> Router.resolve(event)                one Routing per audience
      -> policy.evaluate(rule, recipient)     send | hold | discard | suppress
      -> channels[channel].send(...)          delivery or dry-run
      -> DeliveryTracker                      retry-once, fallback ladder, DLQ

Nothing here invents a decision: every window, cap, route and fallback is read
from templates/nt-registry.json, which summarises the 26 NT-* content files
(their governance lives in NT-026, never here).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from . import kpis
from .channels import BaseChannel, SendRefused, build_channels
from .delivery import DeliveryTracker
from .policy import ConsentRule, RecipientState, evaluate, rules_from_registry
from .router import Router, RoutingError

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"


def load_registry(path: Path | None = None) -> dict:
    """Load the NT registry. A corrupt registry aborts startup — an
    unevaluable policy must never default to 'send'."""
    registry_path = path or (TEMPLATES_DIR / "nt-registry.json")
    with open(registry_path, encoding="utf-8") as handle:
        return json.load(handle)


class Dispatcher:
    def __init__(
        self,
        registry: dict | None = None,
        channels: dict[str, BaseChannel] | None = None,
        active_wave: str = "W1",
        now: datetime | None = None,
    ) -> None:
        self.registry = registry or load_registry()
        self.rules: dict[str, ConsentRule] = rules_from_registry(self.registry)
        self.router = Router(self.registry, active_wave=active_wave)
        self.channels = channels or build_channels()
        self.tracker = DeliveryTracker()
        self._now = now  # injectable clock for deterministic tests

    def _clock(self) -> datetime:
        return self._now or datetime.now(UTC)

    # ------------------------------------------------------------------ body

    def _body_for(self, event: str, language: str) -> tuple[str, str, dict]:
        """(template_id, rendered-template, variables) for an event+language."""
        bodies = self.registry["bodies"]
        for body in bodies.values():
            if (
                isinstance(body, dict)
                and body.get("event") == event
                and "channel" in body
                and body["channel"] in ("sms", "alert")
            ):
                return (
                    body["template_id"],
                    body.get(language) or body["bn"],
                    body.get("variables", {}),
                )
        raise RoutingError(
            f"no body registered for {event!r} — the matrix names templates the body table must carry"
        )

    # ---------------------------------------------------------------- handle

    def handle(self, event: dict) -> list[dict]:
        """fix_events consumer entry point. Returns the decision record."""
        event_type = event.get("event_type", "")
        payload = event.get("payload", {})
        recipients: list[RecipientState] = payload.get("recipients", [])
        event_time = (
            datetime.fromtimestamp(payload["event_time"], tz=UTC)
            if "event_time" in payload
            else self._clock()
        )
        decisions: list[dict] = []

        try:
            routings = self.router.resolve(event_type)
        except RoutingError as exc:
            # An unmapped or later-wave event is a programming error upstream;
            # it becomes a dead-letter with the reason — never a silent drop.
            record = self.tracker.open(
                event=event_type,
                party_id=0,
                recipient="(unrouted)",
                consent_class="transactional",
                language="en",
                rendered="",
            )
            self.tracker.mark_dead(record, str(exc))
            return [{"event": event_type, "state": "dead", "reason": str(exc)}]

        for routing in routings:
            rule = self.rules[routing.consent_class]
            # A RecipientState carries no audience tag: like an untagged dict
            # it applies to every audience of the event.
            audience_recipients = [
                r
                for r in recipients
                if (r.get("audience") if isinstance(r, dict) else None) in (None, routing.audience)
            ]
            for recipient_state in audience_recipients:
                state = (
                    RecipientState(**{k: v for k, v in recipient_state.items() if k != "audience"})
                    if isinstance(recipient_state, dict)
                    else recipient_state
                )
                decision = self._deliver_one(routing, rule, state, event_time, payload)
                decisions.append(decision)
        return decisions

    # ------------------------------------------------------------ one send

    def _deliver_one(
        self,
        routing,
        rule: ConsentRule,
        recipient: RecipientState,
        event_time: datetime,
        payload: dict,
    ) -> dict:
        now = self._clock()
        _template_id, body, variables = self._body_for(routing.event, recipient.preferred_language)
        variables = {**variables, **payload.get("variables", {})}
        address = payload.get("addresses", {}).get(routing.audience, f"party:{recipient.party_id}")

        record = self.tracker.open(
            event=routing.event,
            party_id=recipient.party_id,
            recipient=address,
            consent_class=rule.consent_class,
            language=recipient.preferred_language,
            rendered="(redacted)",  # OTP content never enters a tracking record
        )

        # Channel ladder: primary, then matrix fallbacks (NT-001 §4). Each
        # channel appears once, in first-seen order: it gets its send plus the
        # one retry, never a second round when it re-appears as a fallback.
        ladder: list[str] = []
        for primary in routing.channels:
            for channel in (primary, *self.router.fallbacks_for(primary)):
                if channel not in ladder:
                    ladder.append(channel)

        for channel in ladder:
            if channel not in self.channels:
                continue
            verdict = evaluate(
                rule,
                recipient,
                now=now,
                channel=channel,
                stale_after_hours=payload.get("stale_after_hours"),
                event_time=event_time,
            )
            if verdict.action == "suppress":
                self.tracker.mark_suppressed(record, verdict.reason)
                return self._decision(record, verdict.reason)
            if verdict.action == "discard":
                self.tracker.mark_discarded(record, verdict.reason)
                return self._decision(record, verdict.reason)
            if verdict.action == "hold":
                # Only the first channel's hold is recorded; a held recipient
                # is re-evaluated when the window opens (QH-02).
                self.tracker.mark_held(record, verdict.reason)
                return self._decision(record, verdict.reason)

            adapter = self.channels[channel]
            rendered = adapter.render(body, variables)
            sms_route = rule.sms_route if channel == "sms" else ""
            retrying = False
            while True:  # the send, then retries while the tracker allows one
                try:
                    result = adapter.send(address, rendered, sms_route=sms_route)
                except SendRefused as exc:
                    self.tracker.record_attempt(record, channel, "failed", f"refused: {exc}")
                    break
                if result is None:
                    break
                detail = f"retry: {result.detail}" if retrying else result.detail
                self.tracker.record_attempt(record, channel, result.status, detail)
                if result.status in ("delivered", "dry-run"):
                    self.tracker.mark_delivered(record, channel)
                    recipient.sent.append((rule.consent_class, now))
                    outcome = "retry" if retrying else result.status
                    return self._decision(record, f"sent:{channel}:{outcome}")
                # failed — NT-001 §4: retry once on the same channel, then the
                # ladder continues to the fallback.
                if not self.tracker.should_retry(record, channel):
                    break
                retrying = True

        task = self.tracker.mark_dead(record, "all channels failed (NT-001 §4)")
        return self._decision(record, "dead:task-raised", task=task)

    @staticmethod
    def _decision(record, reason: str, task: dict | None = None) -> dict:
        out = {
            "event": record.event,
            "party_id": record.party_id,
            "state": record.state,
            "reason": reason,
        }
        if task:
            out["task"] = task
        return out

    # ----------------------------------------------------------------- KPIs

    def kpi_snapshot(self) -> dict:
        snap = kpis.snapshot(self.tracker.records)
        return {
            "delivery_rate": snap.delivery_rate,
            "p50_latency_ms": snap.p50_latency_ms,
            "p95_latency_ms": snap.p95_latency_ms,
            "opt_out_rate": snap.opt_out_rate,
            "channel_mix": kpis.channel_mix(self.tracker.records),
            "counts": {
                "total": snap.total,
                "delivered": snap.delivered,
                "failed": snap.failed,
                "suppressed": snap.suppressed,
                "held": snap.held,
                "discarded": snap.discarded,
                "dead": snap.dead,
            },
        }
