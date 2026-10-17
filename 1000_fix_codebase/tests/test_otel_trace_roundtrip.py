# tests/test_otel_trace_roundtrip.py — OpenTelemetry & Correlation-ID Round-Trip
# Validates NFR-092, PE-008, P06-M08-T05/T06, and discharges GP-10.
from __future__ import annotations

import json
import unittest
import uuid
from typing import Any

from libs.py.fix_telemetry import (
    CORRELATION_HEADER,
    TRACEPARENT_HEADER,
    Span,
    TraceContext,
    extract_trace_context,
    get_current_correlation_id,
    get_in_memory_spans,
    inject_trace_context,
    reset_in_memory_spans,
    set_current_correlation_id,
    start_span,
    stamp_outbox_metadata,
)
from libs.py.fix_events import publish


class MockOutboxRecord:
    def __init__(self, event_id: str, event_type: str, metadata: dict[str, Any]):
        self.event_id = event_id
        self.event_type = event_type
        self.metadata = metadata


class MockOutboxModel:
    def __init__(self):
        self.records: list[MockOutboxRecord] = []

    def emit(self, event_type: str, aggregate: str, aggregate_id: int, payload: dict, metadata: dict | None = None):
        rec = MockOutboxRecord(str(uuid.uuid4()), event_type, metadata or {})
        self.records.append(rec)
        return rec


class MockEnvironment:
    def __init__(self, correlation_id: str | None = None):
        self.context = {"fix_correlation_id": correlation_id} if correlation_id else {}
        self.outbox = MockOutboxModel()

    def __getitem__(self, item: str):
        if item == "fix.event.outbox":
            return self.outbox
        raise KeyError(item)


class TestOpenTelemetryTraceRoundtrip(unittest.TestCase):
    """Discharges GP-10: verifies OpenTelemetry trace round-trip and correlation-id propagation."""

    def setUp(self):
        reset_in_memory_spans()

    def test_single_hop_span_creation(self):
        """Verifies basic span creation, timing, and attribute capture."""
        test_corr_id = str(uuid.uuid4())
        ctx = TraceContext(correlation_id=test_corr_id)

        with start_span("portal.order.create", attributes={"fix.tenant_id": "T01"}, context=ctx) as span:
            span.set_attribute("order.amount", 2500.0)

        spans = get_in_memory_spans()
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0]["name"], "portal.order.create")
        self.assertEqual(spans[0]["correlation_id"], test_corr_id)
        self.assertEqual(spans[0]["attributes"]["fix.correlation_id"], test_corr_id)
        self.assertEqual(spans[0]["attributes"]["fix.tenant_id"], "T01")
        self.assertEqual(spans[0]["attributes"]["order.amount"], 2500.0)
        self.assertEqual(spans[0]["status"], "OK")
        self.assertGreaterEqual(spans[0]["duration_ms"], 0.0)

    def test_four_hop_trace_propagation_and_correlation_id_preservation(self):
        """Verifies multi-hop propagation across Client -> Gateway -> Odoo -> Outbox Worker -> Downstream.

        Must preserve the identical x-fix-correlation-id across all hops without mutation.
        """
        origin_correlation_id = str(uuid.uuid4())

        # Hop 1: Ingress (Client -> API Gateway / Next.js)
        client_headers = {
            CORRELATION_HEADER: origin_correlation_id,
        }
        gw_ctx = extract_trace_context(client_headers)
        self.assertEqual(gw_ctx.correlation_id, origin_correlation_id)

        gw_headers: dict[str, str] = {}
        with start_span("gateway.route_dispatch", context=gw_ctx) as gw_span:
            gw_span.set_attribute("http.method", "POST")
            gw_span.set_attribute("http.route", "/api/odoo/service/order")
            gw_headers = inject_trace_context(context=gw_ctx)

        self.assertEqual(gw_headers[CORRELATION_HEADER], origin_correlation_id)
        self.assertIn(TRACEPARENT_HEADER, gw_headers)

        # Hop 2: Odoo Backend Service (reads headers, processes order, writes to outbox)
        odoo_ctx = extract_trace_context(gw_headers)
        self.assertEqual(odoo_ctx.correlation_id, origin_correlation_id)
        self.assertEqual(odoo_ctx.trace_id, gw_ctx.trace_id)

        mock_env = MockEnvironment(correlation_id=odoo_ctx.correlation_id)
        with start_span("odoo.service_order.process", context=odoo_ctx) as odoo_span:
            odoo_span.set_attribute("operating_unit_id", 1)
            # Publishes outbox event using fix_events
            publish(mock_env, "service.order.created", "fix.service.order", 101, {
                "order_id": 101,
                "amount": 1500.0,
            })

        self.assertEqual(len(mock_env.outbox.records), 1)
        outbox_event = mock_env.outbox.records[0]
        self.assertEqual(outbox_event.metadata.get("correlation_id"), origin_correlation_id)

        # Hop 3: Outbox Publisher / Bus Worker (reads outbox metadata)
        worker_ctx = TraceContext(
            correlation_id=outbox_event.metadata["correlation_id"],
            trace_id=odoo_ctx.trace_id,
            parent_span_id=odoo_span.span_id,
        )
        downstream_headers: dict[str, str] = {}
        with start_span("worker.outbox_drain", context=worker_ctx) as worker_span:
            worker_span.set_attribute("event_type", outbox_event.event_type)
            downstream_headers = inject_trace_context(context=worker_ctx)

        # Hop 4: Downstream Notification Dispatcher
        notif_ctx = extract_trace_context(downstream_headers)
        with start_span("notification.sms.send", context=notif_ctx) as notif_span:
            notif_span.set_attribute("channel", "sms")
            notif_span.set_attribute("recipient", "01700000000")

        # Trace Verification (discharges GP-10)
        spans = get_in_memory_spans()
        self.assertEqual(len(spans), 4)

        span_names = [s["name"] for s in spans]
        self.assertEqual(span_names, [
            "gateway.route_dispatch",
            "odoo.service_order.process",
            "worker.outbox_drain",
            "notification.sms.send",
        ])

        # All 4 spans must share the EXACT SAME correlation ID
        for s in spans:
            self.assertEqual(s["correlation_id"], origin_correlation_id)
            self.assertEqual(s["attributes"]["fix.correlation_id"], origin_correlation_id)
            self.assertEqual(s["trace_id"], gw_ctx.trace_id)

    def test_span_exception_recording(self):
        """Verifies that unhandled exceptions properly mark the span as ERROR."""
        corr_id = str(uuid.uuid4())
        ctx = TraceContext(correlation_id=corr_id)

        try:
            with start_span("payment.settle", context=ctx) as span:
                span.set_attribute("gateway", "bKash")
                raise ValueError("bKash API timeout after 5000ms")
        except ValueError:
            pass

        spans = get_in_memory_spans()
        self.assertEqual(len(spans), 1)
        err_span = spans[0]
        self.assertEqual(err_span["status"], "ERROR")
        self.assertIn("bKash API timeout", err_span["status_message"])
        self.assertTrue(err_span["attributes"].get("error"))
        self.assertEqual(len(err_span["events"]), 1)
        self.assertEqual(err_span["events"][0]["name"], "exception")
        self.assertEqual(err_span["events"][0]["attributes"]["exception.type"], "ValueError")


if __name__ == "__main__":
    unittest.main()
