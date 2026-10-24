"""Behavioural tests for the fix_events public API (libs/py/fix_events/__init__.py).

publish() must write through the transactional outbox and resolve the
correlation id (explicit metadata > env context > telemetry > none);
replay_from_timestamp() must query published events in publication order.
The Odoo env and the outbox model are faked; fix_telemetry is replaced by a
stub module so the suite is independent of the tracer's internals.
"""

from __future__ import annotations

import json
import logging
import sys
import types
from types import SimpleNamespace

import pytest

import libs.py.fix_events as fix_events
from libs.py.fix_events import consume, publish, replay_from_timestamp

TELEMETRY = "libs.py.fix_telemetry"


class FakeOutbox:
    def __init__(self, records=()):
        self.emitted: list[tuple] = []
        self.searches: list[tuple] = []
        self._records = list(records)

    def emit(self, event_type, aggregate, aggregate_id, payload, meta):
        self.emitted.append((event_type, aggregate, aggregate_id, payload, meta))
        return SimpleNamespace(event_id=f"uuid-{len(self.emitted)}")

    def search(self, domain, order=None):
        self.searches.append((domain, order))
        return self._records


class FakeEnv:
    """Minimal Odoo env: model access by name, optional ``context``."""

    def __init__(self, outbox, **attrs):
        self._outbox = outbox
        self.__dict__.update(attrs)

    def __getitem__(self, model):
        assert model == "fix.event.outbox"
        return self._outbox


@pytest.fixture
def telemetry(monkeypatch):
    """Install a stub fix_telemetry whose correlation id the test controls."""
    stub = types.ModuleType(TELEMETRY)
    stub.calls = 0
    stub.value = "trace-corr"

    def get_current_correlation_id():
        stub.calls += 1
        return stub.value

    stub.get_current_correlation_id = get_current_correlation_id
    monkeypatch.setitem(sys.modules, TELEMETRY, stub)
    return stub


# --------------------------------------------------------------------------- publish


def test_publish_writes_through_the_outbox_and_returns_the_event_id(telemetry, caplog):
    outbox = FakeOutbox()
    meta = {"correlation_id": "corr-explicit", "causation_id": "c-1"}
    with caplog.at_level(logging.DEBUG, logger=fix_events.logger.name):
        event_id = publish(
            FakeEnv(outbox, context={"fix_correlation_id": "ctx"}),
            "party.created",
            "res.partner",
            5,
            {"partner_id": 5},
            meta,
        )
    assert event_id == "uuid-1"
    assert outbox.emitted == [
        ("party.created", "res.partner", 5, {"partner_id": 5}, meta),
    ]
    # Explicit metadata wins: neither the context nor telemetry is consulted.
    assert telemetry.calls == 0
    assert "fix_events: emitted party.created (id=uuid-1" in caplog.text
    assert "corr=corr-explicit" in caplog.text


def test_publish_takes_the_correlation_id_from_the_env_context(telemetry):
    outbox = FakeOutbox()
    publish(FakeEnv(outbox, context={"fix_correlation_id": "ctx-7"}), "a.b", "m", 1, {})
    assert outbox.emitted[0][4] == {"correlation_id": "ctx-7"}
    assert telemetry.calls == 0


@pytest.mark.parametrize(
    "attrs",
    [{}, {"context": {}}, {"context": "not-a-dict"}],
    ids=["no-context", "context-without-id", "non-dict-context"],
)
def test_publish_falls_back_to_the_telemetry_correlation_id(telemetry, attrs):
    outbox = FakeOutbox()
    publish(FakeEnv(outbox, **attrs), "a.b", "m", 1, {}, metadata={"correlation_id": ""})
    assert outbox.emitted[0][4] == {"correlation_id": "trace-corr"}
    assert telemetry.calls == 1


def test_publish_without_any_correlation_source_leaves_it_unset(telemetry):
    telemetry.value = ""
    outbox = FakeOutbox()
    publish(FakeEnv(outbox), "a.b", "m", 1, {"x": 1})
    assert outbox.emitted[0][4] == {}


def test_publish_survives_a_missing_telemetry_package(monkeypatch):
    monkeypatch.setitem(sys.modules, TELEMETRY, None)  # makes the import raise ImportError
    outbox = FakeOutbox()
    assert publish(FakeEnv(outbox), "a.b", "m", 1, {}) == "uuid-1"
    assert outbox.emitted[0][4] == {}


def test_outbox_keeps_causation_id_when_correlation_is_resolved_and_replays_both(telemetry):
    """AS-08 guard: both causal ids reach the outbox and come back out of replay."""
    outbox = FakeOutbox()
    ctx = FakeEnv(outbox, context={"fix_correlation_id": "ctx-1"})
    publish(ctx, "a.b", "m", 1, {}, {"causation_id": "evt-parent"})
    publish(FakeEnv(outbox), "a.b", "m", 2, {}, {"causation_id": "evt-parent"})
    assert [e[4] for e in outbox.emitted] == [
        {"causation_id": "evt-parent", "correlation_id": "ctx-1"},
        {"causation_id": "evt-parent", "correlation_id": "trace-corr"},
    ]
    stored = FakeOutbox([_row("e1", "a.b", {}, outbox.emitted[0][4])])
    [event] = replay_from_timestamp(FakeEnv(stored), "2026-10-18")
    assert event["metadata"] == {"causation_id": "evt-parent", "correlation_id": "ctx-1"}


def test_publish_does_not_mutate_the_callers_metadata(telemetry):
    meta = {"causation_id": "c"}
    publish(FakeEnv(FakeOutbox()), "a.b", "m", 1, {}, meta)
    assert meta == {"causation_id": "c"}


# --------------------------------------------------------------------------- consume


def test_consume_is_a_publisher_side_no_op():
    calls = []
    assert consume(FakeEnv(FakeOutbox()), calls.append, "party.created") == 0
    assert consume(FakeEnv(FakeOutbox()), calls.append, "x.y", dead_letter_on_error=False) == 0
    assert calls == []


# --------------------------------------------------------------------------- replay


def _row(event_id, event_type, payload, metadata=None):
    return SimpleNamespace(
        event_id=event_id,
        event_type=event_type,
        payload=json.dumps(payload),
        metadata_json=json.dumps(metadata) if metadata is not None else False,
    )


def test_replay_returns_published_events_in_publication_order():
    rows = [
        _row("e1", "vat.issued", {"n": 1}, {"correlation_id": "c1"}),
        _row("e2", "party.created", {"n": 2}),
    ]
    outbox = FakeOutbox(rows)
    events = replay_from_timestamp(FakeEnv(outbox), "2026-10-18 00:00:00")
    assert outbox.searches == [
        (
            [("create_date", ">=", "2026-10-18 00:00:00"), ("status", "=", "published")],
            "create_date asc",
        )
    ]
    assert events == [
        {
            "event_id": "e1",
            "event_type": "vat.issued",
            "payload": {"n": 1},
            "metadata": {"correlation_id": "c1"},
        },
        {"event_id": "e2", "event_type": "party.created", "payload": {"n": 2}, "metadata": {}},
    ]


def test_replay_can_be_filtered_by_event_type():
    outbox = FakeOutbox()
    assert replay_from_timestamp(FakeEnv(outbox), "2026-10-18", "vat.issued") == []
    domain, _order = outbox.searches[0]
    assert domain[-1] == ("event_type", "=", "vat.issued")
    assert len(domain) == 3


# --------------------------------------------------------------------------- exports


def test_every_public_name_is_exported():
    for name in fix_events.__all__:
        assert getattr(fix_events, name) is not None, name
    assert fix_events.InMemoryBus.__module__ == "libs.py.fix_events.kafka_bus"
    assert fix_events.KafkaBackend.__module__ == "libs.py.fix_events.kafka_backend"
