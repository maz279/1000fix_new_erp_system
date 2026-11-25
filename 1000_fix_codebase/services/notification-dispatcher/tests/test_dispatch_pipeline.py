"""Dispatcher pipeline tests — suppression outcomes, the NT-001 §4 retry-once
+ fallback ladder, dead-lettering, KPIs, the delivery tracker, the remaining
policy (NT-002/NT-003) and router (CH-06) rules.

Channels are scripted test doubles injected into the Dispatcher, so every
outcome (delivered / failed / refused / no result) is deterministic and no
gateway is ever contacted. Clocks are fixed Asia/Dhaka datetimes (QH-04).
"""

from __future__ import annotations

import copy
import json
import sys
from datetime import UTC, datetime, time, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import kpis
from src.channels import BaseChannel, DeliveryResult, SendRefused
from src.delivery import DLQ_ALERT_AFTER, DeliveryRecord, DeliveryTracker
from src.dispatcher import Dispatcher, load_registry
from src.policy import DHAKA_TZ, ConsentRule, RecipientState, evaluate, rules_from_registry
from src.router import Router, RoutingError

REGISTRY = load_registry()
RULES = rules_from_registry(REGISTRY)
NOON = datetime(2026, 3, 2, 12, tzinfo=DHAKA_TZ)  # a Monday, inside every window
NIGHT = datetime(2026, 3, 2, 22, tzinfo=DHAKA_TZ)  # after the 21:00 service close
CUSTOMER_ADDRESS = "8801700000000"


class ScriptedChannel(BaseChannel):
    """Test double: answers each send with the next scripted outcome (a
    status string, ``None`` or an exception to raise), then ``default``."""

    def __init__(self, name: str, *outcomes: object, default: object = "failed") -> None:
        self.channel = name
        self.url = ""
        self.token = ""
        self.outcomes = list(outcomes)
        self.default = default
        self.calls: list[tuple[str, str, str]] = []

    def send(self, recipient: str, rendered: str, *, sms_route: str = "") -> DeliveryResult:
        self.calls.append((recipient, rendered, sms_route))
        outcome = self.outcomes.pop(0) if self.outcomes else self.default
        if isinstance(outcome, BaseException):
            raise outcome
        if outcome is None:
            return None  # type: ignore[return-value] - a misbehaving adapter
        return DeliveryResult(self.channel, outcome, detail=f"{self.channel}={outcome}")


def dispatcher_with(*adapters: ScriptedChannel, now: datetime = NOON, **kwargs) -> Dispatcher:
    return Dispatcher(
        registry=REGISTRY,
        channels={adapter.channel: adapter for adapter in adapters},
        now=now,
        **kwargs,
    )


def payment_event(*recipients: object, **payload_extra: object) -> dict:
    """payment.received — transactional, one customer audience, sms + email."""
    payload = {
        "recipients": list(recipients),
        "addresses": {"customer": CUSTOMER_ADDRESS},
        "variables": {"customer_name": "Rahim", "amount": "৳1,500", "tracking_ref": "TRK-9"},
        "event_time": NOON.timestamp(),
    }
    payload.update(payload_extra)
    return {"event_type": "payment.received", "payload": payload}


def attempts(dispatcher: Dispatcher, index: int = 0) -> list[tuple[str, str, str]]:
    record = dispatcher.tracker.records[index]
    return [(a.channel, a.status, a.detail) for a in record.attempts]


# ------------------------------------------------------- suppression paths


class TestSuppressionOutcomes:
    def test_regression_opted_out_recipient_is_suppressed_not_a_crash(self):
        """Regression: _deliver_one called getattr(tracker, "mark_suppress"),
        but the tracker method is mark_suppressed — every opt-out, DND or
        frequency-cap suppression raised AttributeError and aborted the
        whole event instead of recording the suppression."""
        sms = ScriptedChannel("sms", "delivered")
        dispatcher = dispatcher_with(sms, ScriptedChannel("email", "delivered"))
        decisions = dispatcher.handle(
            payment_event({"party_id": 3, "channel_preferences": {"sms": False}})
        )
        assert decisions == [
            {
                "event": "payment.received",
                "party_id": 3,
                "state": "suppressed",
                "reason": "opted-out:sms",
            }
        ]
        assert sms.calls == []
        assert attempts(dispatcher) == [("(policy)", "suppressed", "opted-out:sms")]
        snapshot = dispatcher.kpi_snapshot()
        assert snapshot["counts"]["suppressed"] == 1
        assert snapshot["opt_out_rate"] == 1.0

    def test_frequency_cap_suppresses_a_service_message(self):
        recipient = RecipientState(
            party_id=4, sent=[("service", NOON - timedelta(days=d)) for d in (1, 2, 3)]
        )
        adapters = [ScriptedChannel(n, default="delivered") for n in ("sms", "email", "in_app")]
        dispatcher = dispatcher_with(*adapters)
        decisions = dispatcher.handle(
            {"event_type": "service.order.awaiting_parts", "payload": {"recipients": [recipient]}}
        )
        # awaiting_parts has customer/branch/corporate_admin audiences; an
        # untagged RecipientState applies to each, and each is capped.
        assert len(decisions) == 3
        assert {d["state"] for d in decisions} == {"suppressed"}
        assert {d["reason"] for d in decisions} == {"frequency-cap"}
        assert all(adapter.calls == [] for adapter in adapters)
        assert len(recipient.sent) == 3  # nothing was sent

    def test_regression_stale_held_message_is_discarded_not_a_crash(self):
        """Regression: the QH-03 discard went through getattr(tracker,
        "mark_discard") (no such method) and raised AttributeError."""
        dispatcher = dispatcher_with(ScriptedChannel("sms", "delivered"), now=NIGHT)
        event_time = NIGHT - timedelta(hours=20)
        decisions = dispatcher.handle(
            {
                "event_type": "service.order.awaiting_parts",
                "payload": {
                    "recipients": [{"audience": "customer", "party_id": 5}],
                    "event_time": event_time.timestamp(),
                    "stale_after_hours": 24,  # window re-opens 08:00 → 30h old
                },
            }
        )
        assert len(decisions) == 1
        assert decisions[0]["state"] == "discarded"
        assert decisions[0]["reason"] == "stale-at-window (QH-03, 30h old)"
        assert dispatcher.tracker.records[0].state == "discarded"
        assert dispatcher.kpi_snapshot()["counts"]["discarded"] == 1

    def test_out_of_window_service_message_is_held_with_policy_attempt(self):
        dispatcher = dispatcher_with(ScriptedChannel("sms", "delivered"), now=NIGHT)
        decisions = dispatcher.handle(
            {
                "event_type": "service.order.awaiting_parts",
                "payload": {"recipients": [{"audience": "customer", "party_id": 6}]},
            }
        )
        assert decisions[0]["state"] == "held"
        assert attempts(dispatcher) == [("(policy)", "held", "outside-window (QH-02)")]


# --------------------------------------------------------- recipients


class TestRecipients:
    def test_regression_recipient_state_objects_are_accepted(self):
        """Regression: handle() is typed list[RecipientState] and converts
        dicts only when needed, but its audience filter called r.get(...) on
        every recipient — a RecipientState raised AttributeError."""
        recipient = RecipientState(party_id=11, preferred_language="en")
        sms = ScriptedChannel("sms", default="delivered")
        dispatcher = dispatcher_with(sms)
        decisions = dispatcher.handle(payment_event(recipient))
        assert decisions == [
            {
                "event": "payment.received",
                "party_id": 11,
                "state": "delivered",
                "reason": "sent:sms:delivered",
            }
        ]
        assert recipient.sent == [("transactional", NOON)]  # the caller's state is updated

    def test_audience_tag_filters_recipients(self):
        dispatcher = dispatcher_with(ScriptedChannel("sms", default="delivered"))
        decisions = dispatcher.handle(
            payment_event(
                {"audience": "customer", "party_id": 1},
                {"audience": "technician", "party_id": 2},  # not an audience of this event
                {"party_id": 3},  # untagged → every audience
            )
        )
        assert [d["party_id"] for d in decisions] == [1, 3]

    def test_language_falls_back_to_bengali_and_payload_variables_win(self):
        sms = ScriptedChannel("sms", default="delivered")
        dispatcher = dispatcher_with(sms)
        dispatcher.handle(
            payment_event(
                {"party_id": 1, "preferred_language": "en"},
                {"party_id": 2, "preferred_language": "fr"},  # no French copy
            )
        )
        english, bengali = (rendered for _, rendered, _ in sms.calls)
        assert english == "Dear Rahim, we received ৳1,500 for TRK-9. Thank you. -1000FiX"
        assert bengali.startswith("প্রিয় Rahim, TRK-9")
        assert all(route == "masking" for _, _, route in sms.calls)  # BD-01 transactional

    def test_missing_address_falls_back_to_party_reference(self):
        sms = ScriptedChannel("sms", default="delivered")
        dispatcher = dispatcher_with(sms)
        dispatcher.handle(
            {"event_type": "payment.received", "payload": {"recipients": [{"party_id": 77}]}}
        )
        assert sms.calls[0][0] == "party:77"
        assert dispatcher.tracker.records[0].rendered == "(redacted)"


# ----------------------------------------------------- the channel ladder


class TestChannelLadder:
    def test_channel_without_adapter_is_skipped(self):
        email = ScriptedChannel("email", "delivered")
        dispatcher = dispatcher_with(email)  # no sms adapter at all
        decisions = dispatcher.handle(payment_event({"party_id": 1}))
        assert decisions[0]["reason"] == "sent:email:delivered"
        assert attempts(dispatcher) == [("email", "delivered", "email=delivered")]

    def test_refused_send_is_recorded_and_the_ladder_continues(self):
        sms = ScriptedChannel("sms", SendRefused("BD-03 signature"))
        dispatcher = dispatcher_with(sms, ScriptedChannel("email", "delivered"))
        decisions = dispatcher.handle(payment_event({"party_id": 1}))
        assert decisions[0]["reason"] == "sent:email:delivered"
        assert attempts(dispatcher)[0] == ("sms", "failed", "refused: BD-03 signature")
        assert len(sms.calls) == 1  # a policy refusal is not retried

    def test_adapter_returning_nothing_is_skipped(self):
        dispatcher = dispatcher_with(
            ScriptedChannel("sms", None), ScriptedChannel("email", "delivered")
        )
        decisions = dispatcher.handle(payment_event({"party_id": 1}))
        assert decisions[0]["reason"] == "sent:email:delivered"
        assert attempts(dispatcher) == [("email", "delivered", "email=delivered")]

    def test_failed_send_is_retried_once_and_the_retry_can_deliver(self):
        recipient = RecipientState(party_id=8)
        sms = ScriptedChannel("sms", "failed", "delivered")
        dispatcher = dispatcher_with(sms)
        decisions = dispatcher.handle(payment_event(recipient))
        assert decisions[0]["state"] == "delivered"
        assert decisions[0]["reason"] == "sent:sms:retry"
        assert attempts(dispatcher) == [
            ("sms", "failed", "sms=failed"),
            ("sms", "delivered", "retry: sms=delivered"),
        ]
        assert dispatcher.tracker.records[0].final_channel == "sms"
        assert recipient.sent == [("transactional", NOON)]

    def test_failed_retry_falls_back_to_the_next_channel(self):
        dispatcher = dispatcher_with(
            ScriptedChannel("sms", "failed", "failed"), ScriptedChannel("email", "dry-run")
        )
        decisions = dispatcher.handle(payment_event({"party_id": 1}))
        assert decisions[0]["reason"] == "sent:email:dry-run"
        assert [a[:2] for a in attempts(dispatcher)] == [
            ("sms", "failed"),
            ("sms", "failed"),
            ("email", "dry-run"),
        ]

    def test_regression_all_channels_failing_tries_each_channel_once_then_raises_a_task(self):
        """Regression: the ladder concatenated each channel's fallbacks without
        de-duplication — payment.received (sms, email) became sms, email,
        in_app, email, sms — so with every gateway down SMS and email were
        each sent 3 times instead of send + one retry (NT-001 §4)."""
        sms, email, in_app = (ScriptedChannel(n) for n in ("sms", "email", "in_app"))
        dispatcher = dispatcher_with(sms, email, in_app)
        decisions = dispatcher.handle(payment_event({"party_id": 21}))
        assert (len(sms.calls), len(email.calls), len(in_app.calls)) == (2, 2, 2)
        # The attempt log is the true send count, in ladder order.
        assert [a[0] for a in attempts(dispatcher)] == ["sms"] * 2 + ["email"] * 2 + ["in_app"] * 2
        decision = decisions[0]
        assert decision["state"] == "dead"
        assert decision["reason"] == "dead:task-raised"
        task = decision["task"]
        assert task["task"] == "notification.all_channels_failed"
        assert task["party_id"] == 21
        assert task["record_id"] == dispatcher.tracker.records[0].id
        assert dispatcher.tracker.dead_letters == [dispatcher.tracker.records[0]]
        assert dispatcher.tracker.operational_tasks == [task]
        assert dispatcher.kpi_snapshot()["counts"]["dead"] == 1

    def test_regression_act_now_ladder_has_no_repeat_rounds(self):
        """Regression: technician_enroute (CH-04: push, sms) built the ladder
        push, sms, email, sms, email, in_app — SMS and email got a second round
        after their retry. Each channel now appears once, in first-seen order."""
        adapters = [ScriptedChannel(n) for n in ("push", "sms", "email", "in_app")]
        dispatcher = dispatcher_with(*adapters)
        decisions = dispatcher.handle(
            {
                "event_type": "service.order.technician_enroute",
                "payload": {"recipients": [{"audience": "customer", "party_id": 31}]},
            }
        )
        assert decisions[0]["state"] == "dead"
        assert [len(adapter.calls) for adapter in adapters] == [2, 2, 2, 2]
        assert [a[0] for a in attempts(dispatcher)] == [
            "push", "push", "sms", "sms", "email", "email", "in_app", "in_app"
        ]  # fmt: skip

    def test_regression_retry_refused_by_policy_moves_down_the_ladder(self):
        """Regression: the retry send was not guarded — a SendRefused on the
        retry escaped and aborted the whole event."""
        sms = ScriptedChannel("sms", "failed", SendRefused("route suspended"))
        dispatcher = dispatcher_with(sms, ScriptedChannel("email", "delivered"))
        decisions = dispatcher.handle(payment_event({"party_id": 1}))
        assert decisions[0]["reason"] == "sent:email:delivered"
        assert attempts(dispatcher)[:2] == [
            ("sms", "failed", "sms=failed"),
            ("sms", "failed", "refused: route suspended"),
        ]

    def test_regression_retry_without_result_moves_down_the_ladder(self):
        """Regression: a retry returning no result crashed on retry.status."""
        sms = ScriptedChannel("sms", "failed", None)
        dispatcher = dispatcher_with(sms, ScriptedChannel("email", "delivered"))
        decisions = dispatcher.handle(payment_event({"party_id": 1}))
        assert decisions[0]["reason"] == "sent:email:delivered"
        assert [a[:2] for a in attempts(dispatcher)] == [("sms", "failed"), ("email", "delivered")]


# ------------------------------------------------- registry / body lookup


class TestRegistryAndBodies:
    def test_event_without_a_registered_body_aborts_loudly(self):
        # payment.overdue is a W2 matrix row with no body (bodies are W1-only).
        dispatcher = dispatcher_with(ScriptedChannel("sms", "delivered"), active_wave="W2")
        with pytest.raises(RoutingError, match=r"no body registered for 'payment.overdue'"):
            dispatcher.handle(
                {"event_type": "payment.overdue", "payload": {"recipients": [{"party_id": 1}]}}
            )

    def test_body_lookup_ignores_non_sms_bodies_and_comments(self):
        registry = copy.deepcopy(REGISTRY)
        registry["bodies"] = {
            "comment": "free text",
            "push_copy": {
                "event": "payment.received",
                "template_id": "NT-099",
                "channel": "push",
                "bn": "x",
            },
        }
        dispatcher = Dispatcher(registry=registry, now=NOON)
        with pytest.raises(RoutingError, match="no body registered"):
            dispatcher._body_for("payment.received", "bn")

    def test_load_registry_from_explicit_path(self, tmp_path):
        path = tmp_path / "registry.json"
        path.write_text(json.dumps({"event_matrix": {}}), encoding="utf-8")
        assert load_registry(path) == {"event_matrix": {}}

    def test_corrupt_registry_aborts_startup(self, tmp_path):
        path = tmp_path / "registry.json"
        path.write_text("{not json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            load_registry(path)

    def test_default_construction_uses_bundled_registry_and_dry_run_channels(self):
        dispatcher = Dispatcher()
        assert dispatcher.registry == REGISTRY
        assert dispatcher.router.active_wave == "W1"
        assert set(dispatcher.channels) == {"sms", "whatsapp", "email", "push", "in_app", "alert"}
        before = datetime.now(UTC)
        assert dispatcher._clock() >= before  # real clock when none is injected


# -------------------------------------------------------------- tracker


RECORD_FIELDS = {
    "event": "payment.received",
    "party_id": 1,
    "recipient": "r",
    "consent_class": "transactional",
    "language": "bn",
    "rendered": "(redacted)",
}


def record(**overrides: object) -> DeliveryRecord:
    return DeliveryRecord(**{**RECORD_FIELDS, **overrides})


class TestDeliveryTracker:
    def test_latency_is_unknown_until_delivered(self):
        tracker = DeliveryTracker()
        rec = tracker.open(**RECORD_FIELDS)
        assert tracker.records == [rec]
        assert rec.latency_ms is None
        tracker.mark_delivered(rec, "sms")
        assert rec.latency_ms is not None and rec.latency_ms >= 0
        assert (rec.state, rec.final_channel) == ("delivered", "sms")

    @pytest.mark.parametrize(
        ("method", "state"),
        [("mark_suppressed", "suppressed"), ("mark_held", "held"), ("mark_discarded", "discarded")],
    )
    def test_policy_outcomes_leave_a_named_attempt(self, method, state):
        rec = record()
        getattr(DeliveryTracker(), method)(rec, "because")
        assert rec.state == state
        assert [(a.channel, a.status, a.detail) for a in rec.attempts] == [
            ("(policy)", state, "because")
        ]

    def test_ageing_dead_letters_raise_the_nt021_alert(self):
        tracker = DeliveryTracker()
        now = datetime(2026, 3, 2, 12, tzinfo=UTC)
        old = record(created_at=now - DLQ_ALERT_AFTER - timedelta(minutes=1))
        fresh = record(created_at=now - timedelta(minutes=5))
        exactly = record(created_at=now - DLQ_ALERT_AFTER)
        for rec in (old, fresh, exactly):
            tracker.mark_dead(rec, "all channels failed")
        assert tracker.dlq_needs_alert(now) == [old]


# ----------------------------------------------------------------- KPIs


def delivered(latency_ms: int, channel: str = "sms") -> DeliveryRecord:
    rec = record()
    rec.state, rec.final_channel = "delivered", channel
    rec.delivered_at = rec.created_at + timedelta(milliseconds=latency_ms)
    return rec


class TestKpis:
    def test_empty_snapshot(self):
        snap = kpis.snapshot([])
        assert (snap.total, snap.delivery_rate, snap.opt_out_rate) == (0, 1.0, 0.0)
        assert snap.p50_latency_ms is None
        assert snap.p95_latency_ms is None
        assert kpis.channel_mix([]) == {}

    def test_latency_percentiles(self):
        snap = kpis.snapshot([delivered(ms) for ms in (250, 100, 200, 150)])
        assert snap.p50_latency_ms == 200  # upper median of the sorted sample
        assert snap.p95_latency_ms == 250
        assert snap.delivery_rate == 1.0

    def test_opt_outs_counted_once_per_record(self):
        opted_out = record()
        opted_out.state = "suppressed"
        DeliveryTracker().record_attempt(opted_out, "sms", "failed", "gateway down")
        DeliveryTracker().mark_suppressed(opted_out, "opted-out:sms")
        DeliveryTracker().mark_suppressed(opted_out, "opted-out:email")
        marketing = record()
        DeliveryTracker().mark_suppressed(marketing, "marketing-opt-out")
        dnd = record()
        DeliveryTracker().mark_suppressed(dnd, "dnd")  # DND is not an opt-out
        snap = kpis.snapshot([opted_out, marketing, dnd, delivered(10)])
        assert snap.opt_outs == 2
        assert snap.opt_out_rate == 0.5
        assert snap.suppressed == 3
        assert snap.delivery_rate == 0.25

    def test_unknown_states_count_as_failed_and_otp_is_excluded(self):
        pending = record()  # still "pending" → counted as failed, never dropped
        otp = delivered(5)
        otp.event = "security.otp_requested"
        snap = kpis.snapshot([pending, otp])
        assert (snap.total, snap.failed, snap.delivered) == (1, 1, 0)
        assert snap.delivery_rate == 0.0

    def test_channel_mix_orders_by_volume(self):
        undelivered = record()
        undelivered.final_channel = "push"
        records = [delivered(1, "email"), delivered(1, "sms"), delivered(1, "sms"), undelivered]
        assert list(kpis.channel_mix(records).items()) == [("sms", 2), ("email", 1)]


# --------------------------------------------------------------- policy


class TestPolicy:
    def test_next_window_open(self):
        rule = RULES["service"]  # 08:00-21:00 Dhaka
        assert rule.next_window_open(NOON) == NOON  # already open
        early = datetime(2026, 3, 2, 6, tzinfo=DHAKA_TZ)
        assert rule.next_window_open(early) == datetime(2026, 3, 2, 8, tzinfo=DHAKA_TZ)
        assert rule.next_window_open(NIGHT) == datetime(2026, 3, 3, 8, tzinfo=DHAKA_TZ)

    def test_marketing_opt_out_suppresses_marketing_only(self):
        recipient = RecipientState(party_id=1, opted_out_marketing=True)
        marketing = evaluate(RULES["marketing"], recipient, now=NOON, channel="sms")
        assert (marketing.action, marketing.reason) == ("suppress", "marketing-opt-out")
        assert evaluate(RULES["service"], recipient, now=NOON, channel="sms").action == "send"

    def test_fresh_out_of_window_message_is_held_not_discarded(self):
        verdict = evaluate(
            RULES["service"],
            RecipientState(party_id=1),
            now=NIGHT,
            channel="sms",
            stale_after_hours=48,
            event_time=NIGHT - timedelta(hours=1),  # 11h old when the window opens
        )
        assert verdict.action == "hold"
        assert verdict.hold_until == datetime(2026, 3, 3, 8, tzinfo=DHAKA_TZ)

    def test_staleness_needs_an_event_time(self):
        verdict = evaluate(
            RULES["service"],
            RecipientState(party_id=1),
            now=NIGHT,
            channel="sms",
            stale_after_hours=1,
        )
        assert verdict.action == "hold"

    def test_missing_consent_class_aborts_rule_loading(self):
        registry = copy.deepcopy(REGISTRY)
        del registry["rule_engine"]["consent_classes"]["marketing"]
        with pytest.raises(ValueError, match="consent class 'marketing' missing from registry"):
            rules_from_registry(registry)

    def test_rule_without_cap_or_rolling_days_uses_defaults(self):
        registry = copy.deepcopy(REGISTRY)
        registry["rule_engine"]["consent_classes"]["service"]["frequency_cap"] = {"per_class": 1}
        rule = rules_from_registry(registry)["service"]
        assert (rule.per_class_cap, rule.combined_cap, rule.rolling_days) == (1, None, 7)
        assert rule.window_start == time(8) and rule.window_end == time(21)
        assert RULES["security"] == ConsentRule(
            consent_class="security",
            window_start=None,
            window_end=None,
            per_class_cap=None,
            combined_cap=None,
            rolling_days=7,
            sms_route="masking",
            dnd_reachable=True,
        )


# --------------------------------------------------------------- router


def _registry_with_row(event: str, row: dict) -> dict:
    registry = copy.deepcopy(REGISTRY)
    registry["event_matrix"][event] = row
    return registry


class TestRouterRules:
    def test_regression_documentation_key_is_not_an_event(self):
        """Regression: event_matrix carries a "comment" string; resolve("comment")
        indexed it as a row and raised TypeError instead of RoutingError, so
        handle() crashed instead of dead-lettering the event."""
        assert isinstance(REGISTRY["event_matrix"]["comment"], str)
        router = Router(REGISTRY)
        assert "comment" not in router.matrix
        with pytest.raises(RoutingError, match="'comment' is not in the NT-001 matrix"):
            router.resolve("comment")
        dispatcher = dispatcher_with(ScriptedChannel("sms", "delivered"))
        decisions = dispatcher.handle({"event_type": "comment", "payload": {}})
        assert decisions[0]["state"] == "dead"
        assert len(dispatcher.tracker.operational_tasks) == 1

    def test_ch06_alert_to_customer_audience_is_refused(self):
        registry = _registry_with_row(
            "system.misrouted_alert",
            {
                "wave": "W1",
                "consent_class": "security",
                "channels": {"customer": ["alert"]},
                "templates": ["NT-021"],
            },
        )
        with pytest.raises(RoutingError, match="alert channel routed to a non-internal audience"):
            Router(registry).resolve("system.misrouted_alert")

    def test_act_now_event_already_leading_with_push_is_unchanged(self):
        routing = Router(REGISTRY, active_wave="W2").resolve("approval.requested")[0]
        assert routing.channels == ("push", "email")
        assert (routing.audience, routing.consent_class, routing.wave) == (
            "approver",
            "transactional",
            "W2",
        )

    def test_unknown_channel_has_no_fallbacks(self):
        assert Router(REGISTRY).fallbacks_for("carrier-pigeon") == ()
        assert Router(REGISTRY).fallbacks_for("in_app") == ()
