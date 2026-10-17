# libs/py/fix_telemetry/tracer.py — Core OpenTelemetry & Correlation-ID Engine
# Implements NFR-092, PE-008, P06-M08-T05/T06, and discharges GP-10.
from __future__ import annotations

import contextvars
import json
import logging
import re
import secrets
import time
import uuid
from typing import Any, Callable

logger = logging.getLogger(__name__)

CORRELATION_HEADER = "x-fix-correlation-id"
TRACEPARENT_HEADER = "traceparent"
TRACESTATE_HEADER = "tracestate"

# Regex for W3C traceparent: version-trace_id-parent_id-trace_flags
# e.g., 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
TRACEPARENT_REGEX = re.compile(
    r"^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$"
)

# Context variables for distributed context propagation
_current_trace_context: contextvars.ContextVar[TraceContext | None] = contextvars.ContextVar(
    "current_trace_context", default=None
)
_current_span: contextvars.ContextVar[Span | None] = contextvars.ContextVar(
    "current_span", default=None
)

# In-memory buffer of completed spans (discharges GP-10: loopback trace verification)
_span_buffer: list[dict[str, Any]] = []


def generate_trace_id() -> str:
    """Generate a 128-bit hex string for W3C Trace ID."""
    return secrets.token_hex(16)


def generate_span_id() -> str:
    """Generate a 64-bit hex string for W3C Span ID."""
    return secrets.token_hex(8)


class TraceContext:
    """Represents distributed tracing context with correlation-id and W3C traceparent."""

    def __init__(
        self,
        correlation_id: str | None = None,
        trace_id: str | None = None,
        parent_span_id: str | None = None,
        trace_flags: str = "01",
        baggage: dict[str, str] | None = None,
    ):
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.trace_id = trace_id or generate_trace_id()
        self.parent_span_id = parent_span_id
        self.trace_flags = trace_flags
        self.baggage = baggage or {}

    def format_traceparent(self, current_span_id: str | None = None) -> str:
        """Format W3C traceparent header string."""
        span_id = current_span_id or self.parent_span_id or generate_span_id()
        return f"00-{self.trace_id}-{span_id}-{self.trace_flags}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "trace_flags": self.trace_flags,
            "baggage": self.baggage.copy(),
        }


class Span:
    """An OpenTelemetry-compatible span."""

    def __init__(
        self,
        name: str,
        context: TraceContext,
        parent_span_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ):
        self.name = name
        self.context = context
        self.span_id = generate_span_id()
        self.parent_span_id = parent_span_id
        self.start_time_ns = time.time_ns()
        self.end_time_ns: int | None = None
        self.status: str = "OK"  # "OK", "ERROR", "UNSET"
        self.status_message: str | None = None
        self.attributes: dict[str, Any] = {
            "fix.correlation_id": context.correlation_id,
            **(attributes or {}),
        }
        self.events: list[dict[str, Any]] = []
        self._token = None

    def set_attribute(self, key: str, value: Any) -> Span:
        self.attributes[key] = value
        return self

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> Span:
        self.events.append({
            "name": name,
            "timestamp_ns": time.time_ns(),
            "attributes": attributes or {},
        })
        return self

    def record_exception(self, exc: BaseException, escaped: bool = True) -> Span:
        self.status = "ERROR"
        self.status_message = str(exc)
        self.add_event("exception", {
            "exception.type": exc.__class__.__name__,
            "exception.message": str(exc),
            "exception.escaped": escaped,
        })
        self.set_attribute("error", True)
        return self

    def finish(self, status: str | None = None) -> None:
        if self.end_time_ns is not None:
            return
        self.end_time_ns = time.time_ns()
        if status:
            self.status = status

        span_record = {
            "name": self.name,
            "trace_id": self.context.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "correlation_id": self.context.correlation_id,
            "start_time_ns": self.start_time_ns,
            "end_time_ns": self.end_time_ns,
            "duration_ms": (self.end_time_ns - self.start_time_ns) / 1_000_000.0,
            "status": self.status,
            "status_message": self.status_message,
            "attributes": self.attributes.copy(),
            "events": self.events.copy(),
        }
        _span_buffer.append(span_record)
        logger.debug(
            "fix_telemetry: span finished: name=%s trace=%s span=%s corr=%s duration=%.2fms",
            self.name,
            self.context.trace_id,
            self.span_id,
            self.context.correlation_id,
            span_record["duration_ms"],
        )

    def __enter__(self) -> Span:
        self._token = _current_span.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val is not None:
            self.record_exception(exc_val)
        self.finish()
        if self._token:
            _current_span.reset(self._token)


def get_current_trace_context() -> TraceContext:
    """Retrieve active TraceContext or construct a root context."""
    ctx = _current_trace_context.get()
    if ctx is None:
        ctx = TraceContext()
        _current_trace_context.set(ctx)
    return ctx


def get_current_correlation_id() -> str:
    """Return active correlation ID (NFR-092)."""
    return get_current_trace_context().correlation_id


def set_current_correlation_id(correlation_id: str) -> None:
    """Explicitly set current correlation ID in context."""
    ctx = _current_trace_context.get()
    if ctx:
        ctx.correlation_id = correlation_id
    else:
        _current_trace_context.set(TraceContext(correlation_id=correlation_id))


def get_current_span() -> Span | None:
    """Return the currently executing span."""
    return _current_span.get()


def extract_trace_context(headers: dict[str, str]) -> TraceContext:
    """Extract W3C traceparent and x-fix-correlation-id from incoming request headers."""
    # Normalize headers to lowercase
    norm_headers = {k.lower(): str(v) for k, v in headers.items()}
    
    correlation_id = norm_headers.get(CORRELATION_HEADER.lower())
    traceparent = norm_headers.get(TRACEPARENT_HEADER.lower())
    
    trace_id = None
    parent_span_id = None
    trace_flags = "01"
    
    if traceparent:
        m = TRACEPARENT_REGEX.match(traceparent.strip())
        if m:
            _version, trace_id, parent_span_id, trace_flags = m.groups()
            
    ctx = TraceContext(
        correlation_id=correlation_id or str(uuid.uuid4()),
        trace_id=trace_id or generate_trace_id(),
        parent_span_id=parent_span_id,
        trace_flags=trace_flags,
    )
    _current_trace_context.set(ctx)
    return ctx


def inject_trace_context(
    headers: dict[str, str] | None = None,
    context: TraceContext | None = None,
) -> dict[str, str]:
    """Inject x-fix-correlation-id and W3C traceparent into outgoing request headers."""
    out = dict(headers or {})
    ctx = context or get_current_trace_context()
    current_span = get_current_span()
    current_span_id = current_span.span_id if current_span else ctx.parent_span_id
    
    out[CORRELATION_HEADER] = ctx.correlation_id
    out[TRACEPARENT_HEADER] = ctx.format_traceparent(current_span_id=current_span_id)
    return out


def start_span(
    name: str,
    attributes: dict[str, Any] | None = None,
    context: TraceContext | None = None,
) -> Span:
    """Start and return a new span within context."""
    ctx = context or get_current_trace_context()
    active_span = get_current_span()
    parent_span_id = active_span.span_id if active_span else ctx.parent_span_id
    
    span = Span(name=name, context=ctx, parent_span_id=parent_span_id, attributes=attributes)
    return span


def trace_step(step_name: str, attributes: dict[str, Any] | None = None):
    """Decorator to automatically wrap a function execution in an OpenTelemetry span."""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            with start_span(step_name, attributes=attributes) as span:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator


def stamp_outbox_metadata(
    metadata: dict[str, Any] | None = None,
    context: TraceContext | None = None,
) -> dict[str, Any]:
    """Stamp correlation-id and trace context into outbox event metadata (AS-08)."""
    meta = dict(metadata or {})
    ctx = context or get_current_trace_context()
    current_span = get_current_span()
    
    meta["correlation_id"] = meta.get("correlation_id") or ctx.correlation_id
    meta["trace_id"] = ctx.trace_id
    meta["span_id"] = current_span.span_id if current_span else ctx.parent_span_id
    meta["traceparent"] = ctx.format_traceparent(current_span_id=meta["span_id"])
    return meta


def get_in_memory_spans() -> list[dict[str, Any]]:
    """Return all finished spans in the loopback buffer (for GP-10 verification)."""
    return list(_span_buffer)


def reset_in_memory_spans() -> None:
    """Clear in-memory span buffer."""
    _span_buffer.clear()
