# Technician GPS telemetry ping (M02, NFR-056): fix.technician.location.
# record_ping existed (throttle, outbox event) with NO production caller —
# the "Fleet Telemetry" surface was a list view over a table nothing wrote.
# This bearer route is the missing producer: the technician app posts its
# position; throttling (<30 s AND <100 m) stays enforced in the model.
import logging

from odoo import http
from odoo.addons.cd_service_order.controllers.technician_api import (
    _error,
    resolve_technician,
)
from odoo.http import request

_logger = logging.getLogger(__name__)


class TelemetryApiController(http.Controller):
    @http.route(
        ["/api/v1/telemetry/ping", "/technician/telemetry/ping"],
        type="jsonrpc",
        auth="bearer",
        methods=["POST"],
    )
    def telemetry_ping(self, **kwargs):
        employee, err = resolve_technician(kwargs)
        if err:
            return err
        lat = kwargs.get("lat")
        lon = kwargs.get("lon")
        if lat is None or lon is None:
            return _error("bad_request", "lat and lon are required")
        ping = request.env["fix.technician.location"].record_ping(
            technician_id=employee.id,
            lat=float(lat),
            lon=float(lon),
            speed=kwargs.get("speed"),
            accuracy=kwargs.get("accuracy"),
            battery=kwargs.get("battery"),
        )
        if not ping:
            # throttled duplicate (<30 s AND <100 m) — acknowledged, not stored
            return {"recorded": False, "reason": "throttled"}
        return {
            "recorded": True,
            "location_id": ping.id,
            "timestamp": str(ping.timestamp),
        }
