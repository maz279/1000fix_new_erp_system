# biometric_webhook — M55 FR-WFM-001 / INT-041: POST /hooks/v1/biometric/<device>.
#
# A09 audit M55-8: there was no device endpoint at all; the ingest method
# trusted whatever employee id it was handed. A terminal now posts its punches
# here, authenticated by its own credential (stored hashed on the device,
# rotated by an Attendance Supervisor):
#
#   POST /hooks/v1/biometric/ZK-DHK-001
#   Authorization: Bearer <device credential>       (or X-Device-Credential)
#   {"company_id": 1,                               (optional; must be the device's)
#    "punches": [{"event_id": "4711", "employee_code": "EMP-0042",
#                 "time": "2026-03-01T09:00:00+06:00", "type": "check_in"}]}
#
# Every punch goes through the guarded ingest (fix.biometric.device.
# action_ingest_punch): registered, active and online device, the employee's
# company, biometric consent, the period lock and replay de-duplication. Each
# device event id is ingested once (fix.biometric.punch.event); a replay is
# answered from the log. An unknown device and a wrong credential get the
# same answer, so the endpoint does not reveal which devices exist.
import json
import logging
from datetime import UTC, datetime

from odoo import SUPERUSER_ID, http
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)

MAX_PUNCHES = 500


def _reply(status, **body):
    return request.make_json_response(body, status=status)


def _presented_credential(headers):
    auth = headers.get("Authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return (headers.get("X-Device-Credential") or "").strip()


def _parse_time(value):
    """ISO 8601 -> naive UTC (an offset is honoured; a naive time is UTC)."""
    stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if stamp.tzinfo:
        stamp = stamp.astimezone(UTC).replace(tzinfo=None)
    return stamp.replace(microsecond=0)


class BiometricWebhook(http.Controller):
    @http.route(
        "/hooks/v1/biometric/<string:device>",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
        save_session=False,
    )
    def biometric_punches(self, device, **kwargs):
        env = request.env(user=SUPERUSER_ID, su=True)
        terminal = (
            env["fix.biometric.device"]
            .with_context(active_test=False)
            .search([("device_id", "=", device)], limit=1)
        )
        presented = _presented_credential(request.httprequest.headers)
        if not terminal or not terminal._fix_credential_ok(presented):
            _logger.warning("biometric webhook: refused credential for device %r", device)
            return _reply(401, error="unauthorized", message="Unknown device or wrong credential")
        if not terminal.active or terminal.status == "offline":
            return _reply(
                403,
                error="device_unavailable",
                message="Device %s is %s"
                % (device, "inactive" if not terminal.active else "offline"),
            )
        try:
            body = json.loads(request.httprequest.get_data() or b"{}")
        except ValueError:
            return _reply(400, error="bad_payload", message="The body is not JSON")
        if not isinstance(body, dict) or not isinstance(body.get("punches"), list):
            return _reply(400, error="bad_payload", message="'punches' must be a list")
        claimed = body.get("company_id")
        if claimed not in (None, "") and str(claimed) != str(terminal.company_id.id):
            return _reply(
                403, error="wrong_company", message="Device %s is not that company's" % device
            )
        punches = body["punches"]
        if len(punches) > MAX_PUNCHES:
            return _reply(400, error="bad_payload", message="At most %d punches" % MAX_PUNCHES)
        results = [self._one(env, terminal, p) for p in punches]
        return _reply(
            200,
            device=device,
            ingested=sum(1 for r in results if r["status"] == "ingested"),
            duplicates=sum(1 for r in results if r["status"] == "duplicate"),
            refused=sum(1 for r in results if r["status"] == "refused"),
            results=results,
        )

    def _employee(self, env, terminal, punch):
        Employee = env["hr.employee"].with_context(active_test=False)
        if punch.get("employee_id"):
            return Employee.browse(int(punch["employee_id"])).exists()
        code = (punch.get("employee_code") or "").strip()
        if not code:
            return Employee.browse()
        # the device's own company first; a code found only elsewhere is still
        # resolved, so the guarded ingest refuses it as the wrong company
        return Employee.search(
            [("employee_code", "=", code), ("company_id", "=", terminal.company_id.id)], limit=1
        ) or Employee.search([("employee_code", "=", code)], limit=1)

    def _one(self, env, terminal, punch):
        Event = env["fix.biometric.punch.event"]
        ref = str((punch or {}).get("event_id") or "").strip() if isinstance(punch, dict) else ""
        if not ref:
            return {"event_id": None, "status": "refused", "error": "event_id is required"}
        done = Event.search(
            [("device_id", "=", terminal.id), ("event_ref", "=", ref), ("state", "=", "ingested")],
            limit=1,
        )
        if done:  # a replay: answered from the log, never ingested twice
            return {"event_id": ref, "status": "duplicate", "record_id": done.record_id.id}
        log = {"device_id": terminal.id, "company_id": terminal.company_id.id, "event_ref": ref}
        try:
            kind = punch.get("type") or "check_in"
            if kind not in ("check_in", "check_out"):
                raise UserError("type is check_in or check_out")
            when = _parse_time(punch.get("time"))
            employee = self._employee(env, terminal, punch)
            if not employee:
                raise UserError("unknown employee")
            log.update({"employee_id": employee.id, "punch_time": when, "punch_type": kind})
            with env.cr.savepoint():
                record = terminal.action_ingest_punch(employee.id, when, punch_type=kind)
                Event.create({**log, "state": "ingested", "record_id": record.id})
            return {"event_id": ref, "status": "ingested", "record_id": record.id}
        except (UserError, ValidationError, AccessError, ValueError, TypeError) as exc:
            message = str(exc.args[0] if getattr(exc, "args", None) else exc)[:250]
            with env.cr.savepoint():
                Event.create({**log, "state": "refused", "message": message})
            return {"event_id": ref, "status": "refused", "error": message}
