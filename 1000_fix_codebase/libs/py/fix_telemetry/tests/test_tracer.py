"""Behavioural tests for libs.py.fix_telemetry (correlation-id + W3C trace context).

No exporter is involved: finished spans land in the module's in-memory
loopback buffer, which is saved and restored around every test, as are the
two context variables, so nothing leaks into other suites sharing the process.
"""

from __future__ import annotations

import itertools
import logging
import re
import sys
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import libs.py.fix_telemetry as telemetry
from libs.py.fix_telemetry import tracer

HEX32 = re.compile(r"^[0-9a-f]{32}$")
HEX16 = re.compile(r"^[0-9a-f]{16}$")
VALID_TP = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"


@pytest.fixture(autouse=True)
def isolated_tracer_state() -> Iterator[None]:
    saved_spans = list(tracer._span_buffer)
    tracer._span_buffer.clear()
    ctx_token = tracer._current_trace_context.set(None)
    span_token = tracer._current_span.set(None)
    yield
    tracer._current_span.reset(span_token)
    tracer._current_trace_context.reset(ctx_token)
    tracer._span_buffer[:] = saved_spans


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Iterator[int]:
    """Deterministic time.time_ns(): 1_000_000_000, 1_002_500_000, ... (2.5 ms steps)."""
    ticks = itertools.count(start=1_000_000_000, step=2_500_000)
    monkeypatch.setattr(tracer.time, "time_ns", lambda: next(ticks))
    return ticks


def test_package_reexports_the_public_api() -> None:
    assert set(telemetry.__all__) <= set(dir(telemetry))
    assert telemetry.start_span is tracer.start_span
    assert telemetry.CORRELATION_HEADER == "x-fix-correlation-id"
    assert telemetry.TRACEPARENT_HEADER == "traceparent"
    assert telemetry.TRACESTATE_HEADER == "tracestate"


def test_id_generators_produce_w3c_sized_random_hex() -> None:
    trace_ids = {tracer.generate_trace_id() for _ in range(20)}
    span_ids = {tracer.generate_span_id() for _ in range(20)}
    assert all(HEX32.match(t) for t in trace_ids) and len(trace_ids) == 20
    assert all(HEX16.match(s) for s in span_ids) and len(span_ids) == 20


# --------------------------------------------------------------------------
# TraceContext
# --------------------------------------------------------------------------


def test_trace_context_defaults() -> None:
    ctx = tracer.TraceContext()
    uuid.UUID(ctx.correlation_id)  # a valid uuid4 string
    assert HEX32.match(ctx.trace_id)
    assert ctx.parent_span_id is None
    assert ctx.trace_flags == "01"
    assert ctx.baggage == {}


def test_trace_context_to_dict_returns_a_baggage_copy() -> None:
    ctx = tracer.TraceContext("corr-1", "a" * 32, "b" * 16, "00", {"tenant": "t1"})
    snapshot = ctx.to_dict()
    assert snapshot == {
        "correlation_id": "corr-1",
        "trace_id": "a" * 32,
        "parent_span_id": "b" * 16,
        "trace_flags": "00",
        "baggage": {"tenant": "t1"},
    }
    snapshot["baggage"]["tenant"] = "mutated"
    assert ctx.baggage == {"tenant": "t1"}


def test_format_traceparent_prefers_current_then_parent_then_fresh_span() -> None:
    ctx = tracer.TraceContext(trace_id="a" * 32, parent_span_id="b" * 16, trace_flags="01")
    assert ctx.format_traceparent("c" * 16) == f"00-{'a' * 32}-{'c' * 16}-01"
    assert ctx.format_traceparent() == f"00-{'a' * 32}-{'b' * 16}-01"

    root = tracer.TraceContext(trace_id="d" * 32)
    m = tracer.TRACEPARENT_REGEX.match(root.format_traceparent())
    assert m is not None
    assert m.group(2) == "d" * 32 and HEX16.match(m.group(3))


# --------------------------------------------------------------------------
# Span
# --------------------------------------------------------------------------


def test_span_attributes_events_and_chaining(clock) -> None:
    ctx = tracer.TraceContext(correlation_id="corr-9")
    span = tracer.Span("work", ctx, parent_span_id="p" * 16, attributes={"job": 7})

    assert span.attributes == {"fix.correlation_id": "corr-9", "job": 7}
    assert span.set_attribute("k", "v") is span
    assert span.add_event("checkpoint") is span
    assert span.add_event("detail", {"n": 1}) is span
    assert span.attributes["k"] == "v"
    assert span.events == [
        {"name": "checkpoint", "timestamp_ns": 1_002_500_000, "attributes": {}},
        {"name": "detail", "timestamp_ns": 1_005_000_000, "attributes": {"n": 1}},
    ]
    assert span.status == "OK" and span.end_time_ns is None


def test_record_exception_marks_span_as_error() -> None:
    span = tracer.Span("work", tracer.TraceContext())
    assert span.record_exception(KeyError("missing"), escaped=False) is span
    assert span.status == "ERROR"
    assert span.status_message == "'missing'"
    assert span.attributes["error"] is True
    (event,) = span.events
    assert event["name"] == "exception"
    assert event["attributes"] == {
        "exception.type": "KeyError",
        "exception.message": "'missing'",
        "exception.escaped": False,
    }


def test_finish_records_span_once_with_duration(clock, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG, logger=tracer.logger.name)
    ctx = tracer.TraceContext(correlation_id="corr-1", trace_id="a" * 32)
    span = tracer.Span("work", ctx, parent_span_id="b" * 16, attributes={"x": 1})

    span.finish()
    span.set_attribute("late", True)
    span.finish(status="ERROR")  # already finished: ignored entirely

    (record,) = telemetry.get_in_memory_spans()
    assert record == {
        "name": "work",
        "trace_id": "a" * 32,
        "span_id": span.span_id,
        "parent_span_id": "b" * 16,
        "correlation_id": "corr-1",
        "start_time_ns": 1_000_000_000,
        "end_time_ns": 1_002_500_000,
        "duration_ms": 2.5,
        "status": "OK",
        "status_message": None,
        "attributes": {"fix.correlation_id": "corr-1", "x": 1},
        "events": [],
    }
    assert span.status == "OK"
    assert "span finished: name=work" in caplog.text and "duration=2.50ms" in caplog.text


def test_finish_with_explicit_status_overrides() -> None:
    span = tracer.Span("work", tracer.TraceContext())
    span.finish(status="UNSET")
    assert span.status == "UNSET"
    assert telemetry.get_in_memory_spans()[0]["status"] == "UNSET"


def test_in_memory_buffer_snapshot_and_reset() -> None:
    tracer.Span("a", tracer.TraceContext()).finish()
    snapshot = telemetry.get_in_memory_spans()
    snapshot.clear()  # a copy: the buffer is untouched
    assert len(telemetry.get_in_memory_spans()) == 1
    telemetry.reset_in_memory_spans()
    assert telemetry.get_in_memory_spans() == []


def test_span_context_manager_sets_and_restores_current_span() -> None:
    assert telemetry.get_current_span() is None
    with telemetry.start_span("outer") as outer:
        assert telemetry.get_current_span() is outer
        with telemetry.start_span("inner") as inner:
            assert telemetry.get_current_span() is inner
            assert inner.parent_span_id == outer.span_id
        assert telemetry.get_current_span() is outer
    assert telemetry.get_current_span() is None
    assert [s["name"] for s in telemetry.get_in_memory_spans()] == ["inner", "outer"]


def test_span_context_manager_records_escaping_exception() -> None:
    with pytest.raises(ValueError, match="bad input"), telemetry.start_span("failing"):
        raise ValueError("bad input")
    (record,) = telemetry.get_in_memory_spans()
    assert record["status"] == "ERROR"
    assert record["status_message"] == "bad input"
    assert [e["name"] for e in record["events"]] == ["exception"]
    assert telemetry.get_current_span() is None


def test_exit_without_enter_finishes_without_touching_current_span() -> None:
    with telemetry.start_span("active") as active:
        orphan = tracer.Span("orphan", tracer.TraceContext())
        orphan.__exit__(None, None, None)
        assert telemetry.get_current_span() is active
    assert [s["name"] for s in telemetry.get_in_memory_spans()] == ["orphan", "active"]


# --------------------------------------------------------------------------
# Current context helpers
# --------------------------------------------------------------------------


def test_current_trace_context_is_created_once_and_reused() -> None:
    first = tracer.get_current_trace_context()
    assert tracer.get_current_trace_context() is first
    assert telemetry.get_current_correlation_id() == first.correlation_id


def test_set_correlation_id_mutates_existing_context() -> None:
    ctx = tracer.get_current_trace_context()
    telemetry.set_current_correlation_id("corr-existing")
    assert tracer.get_current_trace_context() is ctx
    assert ctx.correlation_id == "corr-existing"


def test_set_correlation_id_creates_context_when_absent() -> None:
    telemetry.set_current_correlation_id("corr-new")
    assert telemetry.get_current_correlation_id() == "corr-new"


# --------------------------------------------------------------------------
# Propagation
# --------------------------------------------------------------------------


def test_extract_valid_traceparent_with_case_insensitive_headers() -> None:
    ctx = telemetry.extract_trace_context(
        {"X-Fix-Correlation-Id": "corr-in", "TraceParent": f"  {VALID_TP}  "}
    )
    assert ctx.correlation_id == "corr-in"
    assert ctx.trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert ctx.parent_span_id == "00f067aa0ba902b7"
    assert ctx.trace_flags == "01"
    assert tracer.get_current_trace_context() is ctx


@pytest.mark.parametrize(
    "bad",
    [
        "garbage",
        "00-4BF92F3577B34DA6A3CE929D0E0E4736-00F067AA0BA902B7-01",  # upper-case hex
        "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7",  # missing flags
    ],
)
def test_extract_malformed_traceparent_starts_a_new_trace(bad: str) -> None:
    ctx = telemetry.extract_trace_context({"traceparent": bad})
    assert HEX32.match(ctx.trace_id) and ctx.trace_id != "4bf92f3577b34da6a3ce929d0e0e4736"
    assert ctx.parent_span_id is None
    assert ctx.trace_flags == "01"
    uuid.UUID(ctx.correlation_id)


def test_extract_without_headers_creates_root_context() -> None:
    ctx = telemetry.extract_trace_context({})
    assert HEX32.match(ctx.trace_id) and ctx.parent_span_id is None
    assert tracer.get_current_trace_context() is ctx


def test_inject_uses_context_parent_when_no_span_is_active() -> None:
    ctx = tracer.TraceContext("corr-out", "a" * 32, "b" * 16)
    incoming = {"accept": "application/json"}

    out = telemetry.inject_trace_context(incoming, context=ctx)

    assert out == {
        "accept": "application/json",
        "x-fix-correlation-id": "corr-out",
        "traceparent": f"00-{'a' * 32}-{'b' * 16}-01",
    }
    assert incoming == {"accept": "application/json"}  # input not mutated


def test_inject_uses_active_span_and_current_context() -> None:
    telemetry.extract_trace_context({"traceparent": VALID_TP, "x-fix-correlation-id": "c1"})
    with telemetry.start_span("call-downstream") as span:
        out = telemetry.inject_trace_context()
    assert out["x-fix-correlation-id"] == "c1"
    assert out["traceparent"] == f"00-4bf92f3577b34da6a3ce929d0e0e4736-{span.span_id}-01"
    assert span.parent_span_id == "00f067aa0ba902b7"


def test_start_span_with_explicit_context_and_attributes() -> None:
    ctx = tracer.TraceContext("corr-x", "e" * 32, "f" * 16)
    span = telemetry.start_span("step", attributes={"a": 1}, context=ctx)
    assert span.context is ctx
    assert span.parent_span_id == "f" * 16
    assert span.attributes == {"fix.correlation_id": "corr-x", "a": 1}
    assert telemetry.get_in_memory_spans() == []  # not finished yet


def test_stamp_outbox_metadata_without_active_span() -> None:
    ctx = tracer.TraceContext("corr-o", "a" * 32, "b" * 16)
    original = {"event": "booking.created"}

    meta = telemetry.stamp_outbox_metadata(original, context=ctx)

    assert meta == {
        "event": "booking.created",
        "correlation_id": "corr-o",
        "trace_id": "a" * 32,
        "span_id": "b" * 16,
        "traceparent": f"00-{'a' * 32}-{'b' * 16}-01",
    }
    assert original == {"event": "booking.created"}


def test_stamp_outbox_metadata_keeps_existing_correlation_and_uses_active_span() -> None:
    telemetry.set_current_correlation_id("ambient")
    with telemetry.start_span("publish") as span:
        meta = telemetry.stamp_outbox_metadata({"correlation_id": "upstream"})
    ctx = tracer.get_current_trace_context()
    assert meta["correlation_id"] == "upstream"
    assert meta["trace_id"] == ctx.trace_id
    assert meta["span_id"] == span.span_id
    assert meta["traceparent"] == f"00-{ctx.trace_id}-{span.span_id}-01"


def test_stamp_outbox_metadata_with_no_metadata() -> None:
    meta = telemetry.stamp_outbox_metadata()
    assert meta["correlation_id"] == telemetry.get_current_correlation_id()
    assert tracer.TRACEPARENT_REGEX.match(meta["traceparent"])


# --------------------------------------------------------------------------
# trace_step decorator
# --------------------------------------------------------------------------


def test_trace_step_wraps_call_in_a_span() -> None:
    seen: list[tracer.Span | None] = []

    @telemetry.trace_step("compute", attributes={"unit": "bdt"})
    def compute(a: int, b: int = 0) -> int:
        seen.append(telemetry.get_current_span())
        return a + b

    assert compute(2, b=3) == 5
    (record,) = telemetry.get_in_memory_spans()
    assert record["name"] == "compute"
    assert record["status"] == "OK"
    assert record["attributes"]["unit"] == "bdt"
    assert seen[0] is not None and seen[0].span_id == record["span_id"]
    assert telemetry.get_current_span() is None


def test_regression_trace_step_records_exception_exactly_once() -> None:
    """Regression: the wrapper recorded the exception and Span.__exit__ recorded
    it again, so every failing step carried two "exception" events."""

    @telemetry.trace_step("explode")
    def explode() -> None:
        raise RuntimeError("kaboom")

    with pytest.raises(RuntimeError, match="kaboom"):
        explode()
    (record,) = telemetry.get_in_memory_spans()
    assert record["status"] == "ERROR"
    assert record["status_message"] == "kaboom"
    assert [e["name"] for e in record["events"]] == ["exception"]
    assert record["events"][0]["attributes"]["exception.type"] == "RuntimeError"
