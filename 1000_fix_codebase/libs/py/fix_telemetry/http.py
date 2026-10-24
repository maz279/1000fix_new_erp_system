# libs/py/fix_telemetry/http.py — HTTP request-span instrumentation (R01 re-audit 2026-10-23).
"""One import for HTTP services: extract the W3C trace context from the
incoming request, run the handler inside a span, and stamp the response with
the correlation id + traceparent so the next hop continues the trace.

Works for both server styles in this repo:
- FastAPI (dispatch-scoring, ml-gateway): ``app.middleware("http")(http_span_middleware("svc"))``
- stdlib BaseHTTPRequestHandler (notification-dispatcher, identity-lifecycle):
  call :func:`observe_http` at the top of do_GET/do_POST.

NFR-092 / PE-08: OTel spans + correlation-id propagation on every HTTP hop.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from .tracer import (
    CORRELATION_HEADER,
    TRACEPARENT_HEADER,
    extract_trace_context,
    get_current_trace_context,
    inject_trace_context,
    start_span,
)


def observe_http(
    service: str,
    route: str,
    headers: dict[str, str],
    status: int = 200,
) -> tuple[str, dict[str, str]]:
    """Begin observing one stdlib-handler request. Returns (correlation_id,
    response_headers) - the caller stamps them on the reply and calls
    :func:`end_http` with the final status."""
    ctx = extract_trace_context(headers)
    response_headers = inject_trace_context({CORRELATION_HEADER: ctx.correlation_id})
    span = start_span(
        f"{service} {route}",
        attributes={"http.request.method": route, "service.name": service},
    )
    span.set_attribute("http.route", route)
    ctx.__dict__.setdefault("_span", span)  # type: ignore[attr-defined]
    return ctx.correlation_id, {k: str(v) for k, v in response_headers.items()}


def end_http(status: int) -> None:
    """Finish the request span opened by observe_http with the final status."""
    span = get_current_trace_context().__dict__.get("_span")  # type: ignore[attr-defined]
    if span is not None:
        span.set_attribute("http.response.status_code", status)
        span.finish(status="OK" if status < 500 else "ERROR")


def http_span_middleware(
    service: str,
) -> Callable[[Any, Any, Callable[[Any], Awaitable[Any]]], Awaitable[Any]]:
    """FastAPI/Starlette middleware factory: per-request span + headers."""

    async def middleware(request: Any, call_next: Callable[[Any], Awaitable[Any]]) -> Any:
        headers = {k.lower(): v for k, v in request.headers.items()}
        ctx = extract_trace_context(headers)
        start = time.perf_counter()
        span = start_span(
            f"{service} {request.method} {request.url.path}",
            attributes={
                "service.name": service,
                "http.request.method": request.method,
                "http.route": request.url.path,
            },
        )
        try:
            response = await call_next(request)
        except Exception:
            span.finish(status="ERROR")
            raise
        finally:
            span.set_attribute("duration_ms", round((time.perf_counter() - start) * 1000, 2))
        response.headers[CORRELATION_HEADER] = ctx.correlation_id
        response.headers[TRACEPARENT_HEADER] = ctx.format_traceparent()
        span.set_attribute("http.response.status_code", response.status_code)
        span.finish(status="OK" if response.status_code < 500 else "ERROR")
        return response

    return middleware


__all__ = ["end_http", "http_span_middleware", "observe_http"]
