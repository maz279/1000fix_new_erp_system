# FR-PRC-010 / BRU-PRC-17 (A04 ERP round 2, 21 Nov 2026): the anonymous,
# rate-limited indicative price band of a published service or item, for the
# customer portal and the public website (P01). It returns a band and the
# item's name only: no cost, margin, rule, card or customer-specific price.
import time
from collections import defaultdict, deque

from odoo import http
from odoo.http import request

LIMIT_PARAM = "cd_rate_card.indicative_requests_per_minute"
LIMIT_DEFAULT = 30
_HITS = defaultdict(deque)


def allow(key, limit, now=None, window=60.0):
    """Sliding-window limiter: True when `key` made fewer than `limit`
    requests in the last `window` seconds (this request is counted)."""
    now = time.monotonic() if now is None else now
    hits = _HITS[key]
    while hits and now - hits[0] >= window:
        hits.popleft()
    if len(hits) >= limit:
        return False
    hits.append(now)
    return True


class M11IndicativePrice(http.Controller):
    @http.route(
        "/api/v1/pricing/indicative",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
        readonly=True,
    )
    def indicative(self, code=None, device_model=None, **_kw):
        env = request.env
        try:
            limit = int(env["ir.config_parameter"].sudo().get_param(LIMIT_PARAM, LIMIT_DEFAULT))
        except (TypeError, ValueError):
            limit = LIMIT_DEFAULT
        if not allow(request.httprequest.remote_addr or "?", max(limit, 1)):
            return request.make_json_response({"error": "too many requests"}, status=429)
        if not (code or "").strip():
            return request.make_json_response({"error": "code is required"}, status=400)
        model = None
        if device_model:
            model = env["fix.device.model"].sudo().search([("name", "=", device_model)], limit=1)
        band = env["fix.rate.card"].sudo().indicative_band(code.strip(), device_model=model or None)
        if not band:
            return request.make_json_response({"error": "no indicative price"}, status=404)
        return request.make_json_response(band)
