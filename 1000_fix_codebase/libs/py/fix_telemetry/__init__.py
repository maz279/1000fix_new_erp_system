# libs/py/fix_telemetry/__init__.py — 1000FiX OpenTelemetry & Correlation-ID Engine
# Implements NFR-092, PE-008, P06-M08-T05, and discharges GP-10.
"""1000FiX Telemetry package for distributed tracing and correlation-id propagation."""

from __future__ import annotations

from .tracer import (
    CORRELATION_HEADER,
    TRACEPARENT_HEADER,
    TRACESTATE_HEADER,
    Span,
    TraceContext,
    extract_trace_context,
    get_current_correlation_id,
    get_current_span,
    get_in_memory_spans,
    inject_trace_context,
    reset_in_memory_spans,
    set_current_correlation_id,
    start_span,
    trace_step,
    stamp_outbox_metadata,
)

__all__ = [
    "CORRELATION_HEADER",
    "TRACEPARENT_HEADER",
    "TRACESTATE_HEADER",
    "Span",
    "TraceContext",
    "extract_trace_context",
    "get_current_correlation_id",
    "get_current_span",
    "get_in_memory_spans",
    "inject_trace_context",
    "reset_in_memory_spans",
    "set_current_correlation_id",
    "start_span",
    "trace_step",
    "stamp_outbox_metadata",
]
