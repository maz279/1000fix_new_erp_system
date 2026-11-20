# M41 RF API (spec §12.5, CD-M41-04 server side, T-04/T-06/T-07/T-15).
#
# Security model (as the P02 technician API):
# - every route is ``auth="bearer"``: the OPERATIVE's own Odoo API key in
#   ``Authorization: Bearer`` (or an interactive session). The acting operative
#   is the hr.employee linked to that user; nothing in the body selects it.
# - the handheld names itself with ``device_code`` (body) or ``X-Device-Code``
#   (header). An unknown or deactivated device, or one issued to someone else,
#   is refused (T-15). Every call stamps the device's last-seen time.
# - every action runs in the operative's environment, under the same rules,
#   record rules and scans as the workspace forms; confirmations carry an
#   idempotency key and replay returns the stored outcome (T-07).
# - no cost or value field is ever returned (spec section 13).
from typing import Any

from odoo import http
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request

REFUSED = (UserError, ValidationError, AccessError)


def _device(kwargs: dict[str, Any]):
    code = kwargs.get("device_code") or request.httprequest.headers.get("X-Device-Code")
    return request.env["fix.wms.device"]._rf_resolve(code)


def _error(exc) -> dict[str, Any]:
    kind = "forbidden" if isinstance(exc, AccessError) else "refused"
    return {"error": {"code": kind, "message": str(exc.args[0] if exc.args else exc)}}


class WmsRfApi(http.Controller):
    @http.route("/api/v1/wh/tasks/next", type="jsonrpc", auth="bearer", readonly=False)
    def tasks_next(self, **kwargs: Any) -> dict[str, Any]:
        """The operative's current task and the next three (T-06)."""
        try:
            device, employee = _device(kwargs)
            return {"device": device.device_code, "tasks": device._rf_next(employee)}
        except REFUSED as exc:
            return _error(exc)

    @http.route("/api/v1/wh/tasks/<int:task_id>/claim", type="jsonrpc", auth="bearer")
    def task_claim(self, task_id: int, **kwargs: Any) -> dict[str, Any]:
        return self._run(task_id, "claim", kwargs)

    @http.route("/api/v1/wh/tasks/<int:task_id>/confirm", type="jsonrpc", auth="bearer")
    def task_confirm(self, task_id: int, **kwargs: Any) -> dict[str, Any]:
        return self._run(task_id, "confirm", kwargs)

    @http.route("/api/v1/wh/tasks/<int:task_id>/exception", type="jsonrpc", auth="bearer")
    def task_exception(self, task_id: int, **kwargs: Any) -> dict[str, Any]:
        return self._run(task_id, "exception", kwargs)

    @http.route("/api/v1/wh/sync", type="jsonrpc", auth="bearer")
    def sync(self, entries=None, **kwargs: Any) -> dict[str, Any]:
        """Offline journal replay (T-06): each entry runs once per key, in order."""
        try:
            device, _employee = _device(kwargs)
        except REFUSED as exc:
            return _error(exc)
        results = []
        for entry in entries or []:
            if not isinstance(entry, dict):
                results.append({"ok": False, "error": "malformed entry"})
                continue
            results.append(
                {
                    "key": entry.get("key"),
                    **device._rf_run(
                        entry.get("key"),
                        entry.get("op"),
                        entry.get("task_id"),
                        entry,
                        offline=True,
                    ),
                }
            )
        return {"device": device.device_code, "results": results}

    @http.route("/api/v1/wh/handling-units/<string:code>", type="jsonrpc", auth="bearer")
    def handling_unit(self, code: str, **kwargs: Any) -> dict[str, Any]:
        """Resolve a licence plate to its contents (T-11), nested units included."""
        try:
            device, _employee = _device(kwargs)
            hu = request.env["fix.wms.handling.unit"].search(
                [("name", "=", code), ("warehouse_id", "=", device.warehouse_id.id)], limit=1
            )
            if not hu:
                raise UserError("No handling unit %s in this warehouse." % code)

            def lines(unit):
                return [
                    {"part": ln.part_id.part_number, "qty": ln.qty, "serial": ln.lot_id.name or ""}
                    for ln in unit.line_ids
                ]

            return {
                "code": hu.name,
                "type": hu.hu_type,
                "state": hu.state,
                "bin": hu.current_bin_id.name or "",
                "contents": lines(hu),
                "nested": [{"code": c.name, "contents": lines(c)} for c in hu.child_ids],
            }
        except REFUSED as exc:
            return _error(exc)

    def _run(self, task_id: int, op: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        try:
            device, _employee = _device(kwargs)
        except REFUSED as exc:
            return _error(exc)
        return device._rf_run(kwargs.get("key"), op, task_id, kwargs)
