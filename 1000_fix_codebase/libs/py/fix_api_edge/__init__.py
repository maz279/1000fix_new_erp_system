"""fix_api_edge - the API edge for external routes (M28-3 / M28-5, decision B-7).

No gateway exists (BRU-IPF-03 is still a target): the quota gate had no caller and
the integration log had no writer. An external route now calls both:

    @http.route("/brand/claims", type="jsonrpc", auth="bearer")
    @api_edge("/brand/claims")
    def claims(self, **kwargs): ...

Before the route runs, the authenticated user's partner is matched to a registered
fix.api.consumer and its quotas are checked (fix.api.quota.check_request_allowed).
After it runs, one measured row goes to fix.integration.log.

What it does not do: a public route has no consumer, so it is logged with no quota
applied. Rate limits on public routes are the routes' own.

The edge must never take a route down. fix.integration.log lives in cd_itsm, which
these addons do not depend on, so a database without it just serves. Any failure in
the edge is logged and the request is served: losing a log row is better than losing
a payment callback. The log row is written on its own cursor: a read-only route has
no writable one, and a request that fails rolls back everything on its own.
"""

from __future__ import annotations

import contextlib
import functools
import logging
import time
from collections.abc import Callable, Iterator
from typing import Any

from odoo import SUPERUSER_ID, api
from odoo.http import request

_logger = logging.getLogger(__name__)

LOG_MODEL = "fix.integration.log"
HTTP_TOO_MANY_REQUESTS = 429
HTTP_GONE = 410


@contextlib.contextmanager
def _log_environment() -> Iterator[api.Environment]:
    """A superuser environment on its own committed cursor. Tests replace this,
    because their transaction is never committed."""
    with request.env.registry.cursor() as cr:
        yield api.Environment(cr, SUPERUSER_ID, {})


def _write_log(**values: Any) -> None:
    try:
        with _log_environment() as env:
            env[LOG_MODEL]._log_request("api", **values)
    except Exception:
        _logger.exception("api edge: could not log %s", values.get("route"))


def _resolve(route: str) -> tuple[Any, Any]:
    """(consumer id or None, endpoint id or None) for the current request."""
    env = request.env
    su = env(user=SUPERUSER_ID, su=True)
    endpoint = su["fix.api.endpoint"].search([("path", "=", route), ("active", "=", True)], limit=1)
    consumer = su["fix.api.consumer"]
    user = env.user
    if user and not user._is_public():
        partner = user.sudo().partner_id
        consumer = consumer.search(
            [
                ("partner_id", "in", (partner | partner.commercial_partner_id).ids),
                ("active", "=", True),
                ("registration_state", "=", "registered"),
            ],
            limit=1,
        )
    return consumer.id or None, endpoint.id or None


def _refusal(consumer_id: int | None, endpoint_id: int | None) -> str:
    """The violated limit, or '' when the request may run. Fails open."""
    if not consumer_id:
        return ""
    su = request.env(user=SUPERUSER_ID, su=True)
    verdict = su["fix.api.quota"].check_request_allowed(consumer_id, endpoint_id)
    return "" if verdict["allowed"] else verdict["reason"]


def _is_sunset(route: str, endpoint_id: int | None) -> bool:
    """The catalogue retired this route and nothing live replaced it (FR-IPF-014)."""
    if endpoint_id:
        return False
    su = request.env(user=SUPERUSER_ID, su=True)
    return bool(
        su["fix.api.endpoint"]
        .with_context(active_test=False)
        .search_count([("path", "=", route), ("lifecycle", "=", "sunset")])
    )


def _signal_deprecation(endpoint_id: int | None) -> None:
    """FR-IPF-014: Deprecation and Sunset headers on a superseded version."""
    if not endpoint_id:
        return
    su = request.env(user=SUPERUSER_ID, su=True)
    endpoint = su["fix.api.endpoint"].browse(endpoint_id)
    if endpoint.lifecycle != "deprecated":
        return
    headers = request.future_response.headers
    headers["Deprecation"] = "true"
    if endpoint.sunset_on:
        headers["Sunset"] = endpoint.sunset_on.strftime("%a, %d %b %Y 00:00:00 GMT")


def _result_status(result: Any) -> tuple[str, int | None]:
    """(log status, HTTP status) from what the route returned."""
    code = getattr(result, "status_code", None)
    if isinstance(code, int):
        return ("failed" if code >= 400 else "success"), code
    if isinstance(result, dict) and result.get("error"):
        return "failed", None
    return "success", None


def _refused_reply(code: str, message: str, status: int, http_route: bool) -> Any:
    body = {"error": {"code": code, "message": message}}
    if http_route:
        return request.make_json_response(body, status=status)
    return body


def api_edge(route: str, http_route: bool = False) -> Callable[[Callable], Callable]:
    """Gate and log one external route. `route` is the catalogue path; `http_route`
    is True for type="http" routes, which answer a refusal with a real 429."""

    def decorator(endpoint: Callable) -> Callable:
        @functools.wraps(endpoint)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # No bound request (a unit test calling the method) or no log model
            # (cd_itsm not installed): nothing to gate and nowhere to log.
            if not request or LOG_MODEL not in request.env:
                return endpoint(*args, **kwargs)
            consumer_id = endpoint_id = None
            refusal = ""
            gone = False
            try:
                consumer_id, endpoint_id = _resolve(route)
                gone = _is_sunset(route, endpoint_id)
                refusal = _refusal(consumer_id, endpoint_id)
                _signal_deprecation(endpoint_id)
            except Exception:
                _logger.exception("api edge: gate failed on %s; serving", route)
            logged = {"consumer": consumer_id, "endpoint": endpoint_id, "route": route}
            if gone:
                _write_log(
                    status="failed",
                    status_code=HTTP_GONE,
                    outcome="version sunset",
                    **logged,
                )
                return _refused_reply("gone", "This API version was sunset.", HTTP_GONE, http_route)
            if refusal:
                _write_log(
                    status="throttled",
                    status_code=HTTP_TOO_MANY_REQUESTS,
                    outcome=refusal,
                    **logged,
                )
                return _refused_reply(
                    "rate_limited",
                    f"Rate limit reached: {refusal}",
                    HTTP_TOO_MANY_REQUESTS,
                    http_route,
                )
            started = time.monotonic()
            status, code = "failed", None
            try:
                result = endpoint(*args, **kwargs)
                status, code = _result_status(result)
                return result
            finally:
                _write_log(
                    status=status,
                    status_code=code,
                    latency_ms=int((time.monotonic() - started) * 1000),
                    **logged,
                )

        return wrapper

    return decorator
