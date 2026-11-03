# P02 Technician Mobile API — W2/W4 contract endpoints (PP4).
#
# Serves:
# 1. Day queue (/technician/queue)
# 2. Geofenced attendance (/technician/attendance/clock_in, /technician/attendance/clock_out)
# 3. Work order job status (/technician/job/status)
# 4. Diagnostic decision trees & fault coding (/technician/diagnostics/tree, /technician/diagnostics/submit)
# 5. Van stock inventory & scan-to-consume (/technician/van-stock, /technician/van-stock/consume)
# 6. SP-07 24h offline journal replay & delta sync (/technician/sync)
#
# Strict server-side validation (AS-09), zero mock fixtures (FF-39).
#
# Security model (R01 re-audit 2026-10-22):
# - every route is ``auth="bearer"``: an Odoo API key in ``Authorization: Bearer``,
#   or an authenticated interactive session (Odoo 19 ir.http._auth_method_bearer).
#   No CORS header is emitted; a web origin, if ever needed, must be an explicit
#   allow-list.
# - the acting technician is ALWAYS the hr.employee linked to the authenticated
#   user (``resolve_technician``). Caller-supplied ``employee_id`` /
#   ``technician_id`` never select the technician; a mismatching value is refused
#   with ``forbidden``. There is no demo / first-employee fallback.
# - the superuser environment is only used for model access; every query and
#   write is scoped to the resolved technician (own work orders, own attendance,
#   own van locations).
# - /technician/sync verifies the SP-03 batch checksum before replaying anything
#   (missing / mismatching digest -> the whole batch is rejected, nothing runs).
#
# The SP-03 batch digest and the SP-07 sync-token helpers below are the single
# implementation shared with cd_field_service's /api/v1/offline/sync
# (docs/guides/offline-sync-protocol.md §6).

import hashlib
import hmac
import json
import logging
import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import datetime, timedelta
from typing import Any, Literal, SupportsFloat, SupportsInt, TypedDict

from odoo import SUPERUSER_ID, fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)

# The ``{"error": {"code", "message"}}`` object every route returns on refusal.
ApiError = dict[str, dict[str, str]]
# An Odoo search-domain element: a "|" / "&" operator or a (field, op, value) leaf.
DomainItem = str | tuple[str, str, object]


class ClockInEvaluation(TypedDict):
    """``evaluate_clock_in_position`` result (M55 AUT-WFM-02 / T-06)."""

    geofence_result: Literal["inside", "outside", "no_zone", "no_geofence", "low_accuracy"]
    distance_m: float | None
    approval_state: Literal["pending", "not_required"]
    reason: str | Literal[False]


# Request parameters that used to let the CALLER choose the acting technician.
IMPERSONATION_PARAMS = ("employee_id", "technician_id")

# SP-07 sync token: "TOKEN-<UTC delta cut, %Y-%m-%dT%H:%M:%S.%f>[~<last record id>]".
SYNC_CURSOR_PREFIX = "TOKEN-"
SYNC_CURSOR_TS_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
# The cut is taken this far before the server transaction timestamp so that a
# transaction still in flight when the token was issued (its write_date is its
# start time) is re-delivered on the next sync instead of being skipped.
SYNC_CURSOR_OVERLAP = timedelta(seconds=60)
SYNC_DELTA_LIMIT = 200

# M55 T-06: a mobile clock-in fix less accurate than this is flagged for approval.
ACCURACY_PARAM = "fix.attendance.max_accuracy_m"
DEFAULT_MAX_ACCURACY_M = 100.0

# DI-05: the command idempotency ledger (defined by cd_field_service, which
# depends on this module - hence looked up softly, see technician_sync).
LEDGER_MODEL = "fix.offline.idempotency.ledger"
# /technician/sync operation -> the model its command targets (ledger "model").
SYNC_COMMAND_MODELS = {
    "clock_in": "fix.attendance.record",
    "clock_out": "fix.attendance.record",
    "job_status": "fix.work.order",
    "diagnose": "fix.work.order",
    "consume_part": "fix.work.order",
}


def _su_env() -> Any:
    """Return superuser environment to avoid ACL AccessErrors on models."""
    return request.env(user=SUPERUSER_ID, su=True)


def _fmt_bdt(amount: object) -> str:
    """Format a monetary value as a BN-007-style South Asian-grouped string
    ("0.00" for a value that is not a number)."""
    if not isinstance(amount, str | bytes | SupportsFloat):
        return "0.00"
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "0.00"
    is_neg = n < 0
    formatted_float = f"{abs(n):.2f}"
    whole_str, frac_str = formatted_float.split(".")
    if len(whole_str) > 3:
        last3 = whole_str[-3:]
        rest = whole_str[:-3]
        groups: list[str] = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        groups.insert(0, rest)  # 1 or 2 leading digits remain (len(whole_str) > 3)
        grouped = ",".join(groups) + "," + last3
    else:
        grouped = whole_str
    sign = "-" if is_neg else ""
    return f"{sign}{grouped}.{frac_str}"


def _error(code: str, message: str) -> ApiError:
    return {"error": {"code": code, "message": message}}


def _to_int(value: object) -> int | None:
    """``int(value)`` of a request value, ``None`` when it is not an integer."""
    if not isinstance(value, str | bytes | SupportsInt):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# --- Shared identity / integrity helpers (also used by cd_field_service) ------


def resolve_technician(kwargs: Mapping[str, Any]) -> tuple[Any, ApiError | None]:
    """Resolve the acting technician from the AUTHENTICATED user only.

    Returns ``(employee, None)`` or ``(None, error_dict)``:
    - no authenticated (non-public) user -> ``unauthenticated``;
    - no hr.employee with ``user_id = request.env.user.id`` -> ``no_employee``
      (never a fallback to a demo / first / any employee);
    - an ``employee_id`` / ``technician_id`` parameter naming anyone else -> ``forbidden``.
    """
    user = request.env.user
    if not user or user._is_public():
        return None, _error("unauthenticated", "Technician authentication is required")
    emp = _su_env()["hr.employee"].search([("user_id", "=", user.id)], limit=1)
    if not emp:
        return None, _error(
            "no_employee", "No technician employee record is linked to the authenticated user"
        )
    for key in IMPERSONATION_PARAMS:
        claimed = kwargs.get(key)
        if claimed in (None, "", False):
            continue
        if _to_int(claimed) != emp.id:
            return None, _error("forbidden", f"{key} does not match the authenticated technician")
    return emp, None


def batch_digest(commands: Sequence[object]) -> str:
    """SP-03 canonical batch digest: SHA-256 hex of the canonical JSON of ``commands``.

    canonical JSON = json.dumps(commands, sort_keys=True, separators=(",", ":"),
    ensure_ascii=False, default=str), encoded UTF-8.
    """
    canonical = json.dumps(
        commands, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_batch_checksum(commands: Sequence[object], client_checksum: object) -> ApiError | None:
    """Return ``None`` when ``client_checksum`` is the SP-03 digest of ``commands``,
    otherwise a ``checksum_missing`` / ``checksum_mismatch`` error object."""
    if not client_checksum:
        return _error(
            "checksum_missing",
            "batch_checksum is required (SP-03); no command in the batch was executed",
        )
    expected = batch_digest(commands)
    if not isinstance(client_checksum, str) or not hmac.compare_digest(
        client_checksum.strip().lower(), expected
    ):
        return _error(
            "checksum_mismatch",
            "batch_checksum does not match the uploaded commands (SP-03); "
            "no command in the batch was executed",
        )
    return None


def payload_digest(payload: Mapping[str, object]) -> str:
    """SHA-256 hex of a command payload (sorted-key JSON), stored in the DI-05 ledger
    for tamper auditing."""
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()


def ledger_lookup(
    ledger: Any, cmd_id: str, tech: Any
) -> tuple[Literal["acknowledged", "rejected"], Any] | None:
    """DI-05: the recorded outcome of command ``cmd_id`` for technician ``tech``.

    ``None`` when the command is new (execute it). Otherwise, without executing:
    ``("acknowledged", <original response>)`` or ``("rejected", <reason>)``; a command
    id recorded for ANOTHER technician is rejected (a replay only ever returns the
    cached result to the technician who issued the command)."""
    cached = ledger.get_cached_result(cmd_id)
    if not cached:
        return None
    if not ledger.search_count([("command_id", "=", cmd_id), ("technician_id", "=", tech.id)]):
        return "rejected", "command_id already used by another technician"
    if cached["status"] == "rejected":
        return "rejected", cached["conflict_reason"] or "Command previously rejected"
    return "acknowledged", cached["response"]


def encode_sync_token(cut: datetime, last_id: int = 0) -> str:
    """Encode an SP-07 delta cursor: the server-side delta cut (naive UTC datetime)
    and, for a truncated page, the id of the last record delivered at that cut."""
    token = SYNC_CURSOR_PREFIX + cut.strftime(SYNC_CURSOR_TS_FORMAT)
    return f"{token}~{last_id}" if last_id else token


def parse_sync_token(token: object) -> tuple[datetime, int] | None:
    """Decode a token from ``encode_sync_token``; ``None`` (= full resync) when the
    token is absent or malformed."""
    if not isinstance(token, str) or not token.startswith(SYNC_CURSOR_PREFIX):
        return None
    stamp, _sep, last = token[len(SYNC_CURSOR_PREFIX) :].partition("~")
    try:
        cut = datetime.strptime(stamp, SYNC_CURSOR_TS_FORMAT)
    except ValueError:
        return None
    last_id = _to_int(last) if last else 0
    if last_id is None or last_id < 0:
        return None
    return cut, last_id


def collect_deltas(
    model: Any,
    domain: Iterable[DomainItem],
    token: object,
    serialize: Callable[[Any], dict[str, Any]],
    limit: int = SYNC_DELTA_LIMIT,
) -> tuple[list[dict[str, Any]], str, bool, bool]:
    """SP-07 delta download: the records of ``model`` matching ``domain`` that changed
    after the cursor carried by ``token`` (all of them when the token is missing,
    malformed or in the future -> full resync).

    Returns ``(deltas, next_token, has_more, full_resync)``.
    """
    now = model.env.cr.now()
    cursor = parse_sync_token(token)
    if cursor and cursor[0] > now:
        cursor = None
    search_domain = list(domain)
    if cursor:
        cut, last_id = cursor
        if last_id:
            search_domain += [
                "|",
                ("write_date", ">", cut),
                "&",
                ("write_date", "=", cut),
                ("id", ">", last_id),
            ]
        else:
            search_domain.append(("write_date", ">", cut))
    records = model.search(search_domain, order="write_date asc, id asc", limit=limit)
    has_more = len(records) >= limit
    if has_more:
        next_token = encode_sync_token(records[-1].write_date, records[-1].id)
    else:
        next_token = encode_sync_token(now - SYNC_CURSOR_OVERLAP)
    return [serialize(rec) for rec in records], next_token, has_more, cursor is None


def _haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two GPS points in meters."""
    R = 6371000  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _point_in_polygon(lat: float, lng: float, points: Sequence[tuple[float, float]]) -> bool:
    """Ray-casting containment of (lat, lng) in a polygon of [lat, lng] vertices."""
    inside = False
    j = len(points) - 1
    for i, (xi, yi) in enumerate(points):
        xj, yj = points[j]
        if (yi > lng) != (yj > lng) and lat < (xj - xi) * (lng - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def _geofence_position(geofence: Any, lat: float, lng: float) -> tuple[bool, float]:
    """``(in_geofence, distance_m)`` of a point against a fix.geofence.

    circle: haversine distance to the centre, inside when <= ``radius_m``;
    polygon: ray-casting containment over ``points``; the distance is 0.0 inside
    and the distance to the nearest vertex outside. (The previous code read every
    geofence as a circle, so a polygon fell back to a default Dhaka centre and a
    15 km radius whatever its points.)"""
    geo = json.loads(geofence.geometry_json)
    if geofence.geofence_type == "polygon":
        points = [(float(p_lat), float(p_lng)) for p_lat, p_lng in geo["points"]]
        if _point_in_polygon(lat, lng, points):
            return True, 0.0
        return False, min(_haversine_distance_m(lat, lng, p_lat, p_lng) for p_lat, p_lng in points)
    dist_m = _haversine_distance_m(lat, lng, float(geo["lat"]), float(geo["lng"]))
    return dist_m <= float(geo["radius_m"]), dist_m


def own_zone_geofences(env: Any, emp: Any) -> Any:
    """The active geofences of the technician's OWN zone (hr.employee.branch_id ->
    fix.branch.zone_id), or an empty recordset."""
    zone = emp.branch_id.zone_id
    if not zone:
        return env["fix.geofence"]
    return env["fix.geofence"].search([("zone_id", "=", zone.id), ("active", "=", True)])


def max_clock_in_accuracy_m(env: Any) -> float:
    """M55 T-06 accuracy limit for a mobile clock-in fix, in metres: the
    ``ir.config_parameter`` ``fix.attendance.max_accuracy_m`` (no figure is set in
    M55 / BRU-WFM), default ``DEFAULT_MAX_ACCURACY_M``."""
    raw = env["ir.config_parameter"].sudo().get_param(ACCURACY_PARAM)
    try:
        return float(raw) if raw else DEFAULT_MAX_ACCURACY_M
    except ValueError:
        _logger.warning(
            "%s=%r is not a number: using %s m", ACCURACY_PARAM, raw, DEFAULT_MAX_ACCURACY_M
        )
        return DEFAULT_MAX_ACCURACY_M


def _flagged(
    result: Literal["outside", "no_zone", "no_geofence", "low_accuracy"],
    distance_m: float | None,
    reason: str,
) -> ClockInEvaluation:
    return {
        "geofence_result": result,
        "distance_m": distance_m,
        "approval_state": "pending",
        "reason": reason,
    }


def evaluate_clock_in_position(
    env: Any, emp: Any, lat: float, lng: float, accuracy_m: float | None = None
) -> ClockInEvaluation:
    """M55 AUT-WFM-02 / T-06 (FR-POR-043, FR-WFM-003): evaluate a mobile clock-in
    server-side against the active geofences of the technician's OWN zone
    (hr.employee.branch_id -> fix.branch.zone_id) and the reported GPS accuracy.

    Never refuses: the clock-in is recorded with ``geofence_result`` and is
    flagged for approval (``approval_state`` "pending" with a ``reason``) unless
    it is inside an own-zone fence with an accuracy within
    ``max_clock_in_accuracy_m`` ("not_required"). Results: inside / outside /
    no_zone / no_geofence / low_accuracy. An unreported accuracy is not an
    acceptable one (T-06: a low-accuracy fix is flagged, not silently accepted).

    Returns ``{"geofence_result", "distance_m" (None when unknown),
    "approval_state", "reason"}``."""
    zone = emp.branch_id.zone_id
    if not zone:
        return _flagged("no_zone", None, "the technician's branch has no dispatch zone")
    fences = own_zone_geofences(env, emp)
    if not fences:
        return _flagged("no_geofence", None, f"zone {zone.code} has no active geofence")
    nearest: float | None = None
    inside_m: float | None = None
    for fence in fences:
        try:
            inside, dist_m = _geofence_position(fence, lat, lng)
        except Exception as e:
            # geometry_json is validated on write (fix.geofence._check_geometry);
            # an unreadable legacy row is skipped, never trusted
            _logger.warning("Geofence %s parsing error: %s", fence.id, e)
            continue
        if inside:
            inside_m = dist_m
            break
        nearest = dist_m if nearest is None else min(nearest, dist_m)
    if inside_m is None:
        where = f" ({round(nearest, 1)} m away)" if nearest is not None else ""
        return _flagged(
            "outside", nearest, f"position outside the geofence of zone {zone.code}{where}"
        )
    limit = max_clock_in_accuracy_m(env)
    if accuracy_m is None or accuracy_m > limit:
        reported = "not reported" if accuracy_m is None else f"{accuracy_m:g} m"
        return _flagged(
            "low_accuracy", inside_m, f"GPS accuracy {reported}, the limit is {limit:g} m"
        )
    return {
        "geofence_result": "inside",
        "distance_m": inside_m,
        "approval_state": "not_required",
        "reason": False,
    }


def clock_in_values(
    emp: Any,
    lat: float,
    lng: float,
    accuracy_m: float | None,
    evaluation: ClockInEvaluation,
    source: str,
    device_ref: str,
    now: datetime,
) -> dict[str, Any]:
    """The fix.attendance.record values of an evaluated mobile clock-in."""
    return {
        "employee_id": emp.id,
        "check_in": now,
        "geo_lat": lat,
        "geo_long": lng,
        "accuracy_m": accuracy_m or 0.0,
        "geofence_result": evaluation["geofence_result"],
        "approval_state": evaluation["approval_state"],
        "approval_reason": evaluation["reason"],
        "source": source,
        "device_ref": device_ref,
        "company_id": emp.company_id.id or emp.env.company.id,
    }


def parse_clock_in_position(params: Mapping[str, Any]) -> tuple[float, float, float | None]:
    """``(lat, lng, accuracy_m)`` from a clock-in request; coordinates are required
    (``ValueError`` without them - there is nothing to evaluate), an absent or
    unreadable accuracy is ``None`` (= not reported)."""
    try:
        lat = float(params["geo_lat"])
        lng = float(params["geo_long"])
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError("geo_lat and geo_long are required and numeric") from exc
    try:
        accuracy_m = float(params["accuracy_m"])
    except (KeyError, ValueError, TypeError):
        accuracy_m = None
    return lat, lng, accuracy_m


def _own_work_order(env: Any, emp: Any, wo_id: object) -> Any:
    """The work order ``wo_id`` if it is assigned to ``emp``, else an empty recordset
    (a foreign or unknown id are indistinguishable to the caller)."""
    wo_int = _to_int(wo_id)
    if wo_int is None:
        return env["fix.work.order"]
    return env["fix.work.order"].search(
        [("id", "=", wo_int), ("technician_id", "=", emp.id)], limit=1
    )


def _work_order_delta(wo: Any) -> dict[str, Any]:
    return {
        "model": "fix.work.order",
        "record_id": wo.id,
        "name": wo.name or f"WO-{wo.id}",
        "state": wo.state,
        "service_order_id": wo.order_id.id,
        "service_order_state": wo.order_id.state,
        "diagnosed_fault_code": wo.diagnosed_fault_code or "",
        "write_date": str(wo.write_date or ""),
    }


class TechnicianApiController(http.Controller):
    """The P02 Technician Mobile App controller."""

    # --- 1. Technician Profile & Shift Status -------------------------------

    @http.route("/technician/auth/me", type="jsonrpc", auth="bearer", readonly=False)
    def technician_me(self, **kwargs: Any) -> dict[str, Any]:
        """Return technician profile, open attendance status, and active geofence."""
        emp, err = resolve_technician(kwargs)
        if err:
            return err

        env = _su_env()
        # The technician's own zone geofence (not the first fence of the estate)
        geofence = own_zone_geofences(env, emp)[:1]
        geo_info: dict[str, Any] | None = None
        if geofence:
            geo_info = {
                "id": geofence.id,
                "name": geofence.name,
                "type": geofence.geofence_type,
                "geometry": json.loads(geofence.geometry_json or "{}"),
            }

        # Check active shift (open attendance record with no check_out)
        open_att = env["fix.attendance.record"].search(
            [("employee_id", "=", emp.id), ("check_out", "=", False)], order="id desc", limit=1
        )

        return {
            "technician": {
                "id": emp.id,
                "name": emp.name,
                "user_id": emp.user_id.id if emp.user_id else None,
                "active_shift": bool(open_att),
                "last_clock_in": str(open_att.check_in or "") if open_att else None,
                "geofence": geo_info,
                "status": "on_duty" if open_att else "off_duty",
            }
        }

    # --- 2. Day Queue -------------------------------------------------------

    @http.route("/technician/queue", type="jsonrpc", auth="bearer", readonly=False)
    def technician_queue(self, **kwargs: Any) -> dict[str, Any]:
        """Return the technician's assigned daily work order queue."""
        emp, err = resolve_technician(kwargs)
        if err:
            return err

        env = _su_env()
        # Query work orders assigned to this technician
        wos = env["fix.work.order"].search(
            [("technician_id", "=", emp.id)], order="sequence asc, id desc", limit=50
        )

        queue = []
        for wo in wos:
            so = wo.order_id
            dev = so.device_id
            parts = [
                {
                    "id": p.id,
                    "product_id": p.product_id.id,
                    "product_name": p.product_id.name or "",
                    "quantity": p.quantity,
                    "unit_cost_bdt": _fmt_bdt(p.unit_cost),
                }
                for p in wo.parts_consumed_ids
            ]

            queue.append(
                {
                    "id": wo.id,
                    "name": wo.name or f"WO-{wo.id}",
                    "sequence": wo.sequence,
                    "state": wo.state,
                    "start_time": str(wo.start_time or ""),
                    "end_time": str(wo.end_time or ""),
                    "duration_hours": wo.duration_hours,
                    "diagnosed_fault_code": wo.diagnosed_fault_code or "",
                    "diagnostic_tree_id": wo.diagnostic_tree_id.id
                    if wo.diagnostic_tree_id
                    else None,
                    "diagnostic_tree_name": wo.diagnostic_tree_id.name
                    if wo.diagnostic_tree_id
                    else "",
                    "parts_consumed": parts,
                    "notes": wo.notes or "",
                    # Service Order context
                    "service_order": {
                        "id": so.id,
                        "ref": so.name,
                        "state": so.state,
                        "priority": so.priority or "normal",
                        "fault_description": so.fault_description or "",
                        "customer_name": so.customer_id.name or "Walk-in Customer",
                        "customer_phone": so.customer_id.phone or "",
                        "device": f"{dev.brand_id.name or ''} {dev.device_model_id.name or ''}".strip()
                        if dev
                        else "Generic Device",
                        "branch": so.branch_id.name or "",
                        "sla_deadline": str(so.sla_resolution_deadline or ""),
                    },
                }
            )

        return {
            "technician_id": emp.id,
            "technician_name": emp.name,
            "queue": queue,
            "total": len(queue),
        }

    # --- 3. Geofenced Clock-In / Out ----------------------------------------

    @http.route("/technician/attendance/clock_in", type="jsonrpc", auth="bearer", readonly=False)
    def attendance_clock_in(self, **kwargs: Any) -> dict[str, Any]:
        """Geofenced mobile clock-in (M55 AUT-WFM-02): the reported position and GPS
        accuracy are evaluated against the technician's own-zone geofences
        (``evaluate_clock_in_position``) and the clock-in is RECORDED with the
        result - flagged "pending approval" unless inside with an acceptable
        accuracy. Coordinates are required (they used to default to the Dhaka
        centre); ``accuracy_m`` is the fix's accuracy radius in metres."""
        emp, err = resolve_technician(kwargs)
        if err:
            return err

        try:
            lat, lng, accuracy_m = parse_clock_in_position(kwargs)
        except ValueError as exc:
            return _error("invalid_coordinates", str(exc))

        env = _su_env()
        # Check for already open attendance record (nothing new is recorded)
        open_att = env["fix.attendance.record"].search(
            [("employee_id", "=", emp.id), ("check_out", "=", False)], order="id desc", limit=1
        )
        if open_att:
            return {
                "clock_in": True,
                "already_clocked_in": True,
                "attendance_id": open_att.id,
                "check_in": str(open_att.check_in),
                "approval_state": open_att.approval_state,
                "message": "Already clocked in",
            }

        # Check if period is locked
        now = fields.Datetime.now()
        check_date = now.date()
        lock = env["fix.attendance.lock"].search(
            [
                ("state", "=", "locked"),
                ("period_start", "<=", check_date),
                ("period_end", ">=", check_date),
            ],
            limit=1,
        )
        if lock:
            return _error(
                "attendance_locked",
                f"Attendance period {lock.name} is locked — mobile clock-in rejected",
            )

        evaluation = evaluate_clock_in_position(env, emp, lat, lng, accuracy_m)
        att = env["fix.attendance.record"].create(
            clock_in_values(
                emp,
                lat,
                lng,
                accuracy_m,
                evaluation,
                "mobile",
                kwargs.get("device_ref", "P02-TECH-MOBILE"),
                now,
            )
        )
        pending = evaluation["approval_state"] == "pending"
        dist_m = evaluation["distance_m"]
        return {
            "clock_in": True,
            "attendance_id": att.id,
            "check_in": str(now),
            "in_geofence": evaluation["geofence_result"] in ("inside", "low_accuracy"),
            "distance_m": round(dist_m, 1) if dist_m is not None else None,
            "geofence_result": evaluation["geofence_result"],
            "approval_state": evaluation["approval_state"],
            "message": f"Clock-in recorded - pending supervisor approval: {evaluation['reason']}"
            if pending
            else "Clock-in successful (within geofence)",
        }

    @http.route("/technician/attendance/clock_out", type="jsonrpc", auth="bearer", readonly=False)
    def attendance_clock_out(self, **kwargs: Any) -> dict[str, Any]:
        """Mobile shift clock-out computing worked hours."""
        emp, err = resolve_technician(kwargs)
        if err:
            return err

        env = _su_env()
        open_att = env["fix.attendance.record"].search(
            [("employee_id", "=", emp.id), ("check_out", "=", False)], order="id desc", limit=1
        )
        if not open_att:
            return _error("no_open_shift", "No active shift to clock out from")

        now = fields.Datetime.now()
        open_att.write({"check_out": now})

        return {
            "clock_out": True,
            "attendance_id": open_att.id,
            "check_in": str(open_att.check_in),
            "check_out": str(now),
            "worked_hours": round(open_att.worked_hours or 0.0, 2),
            "message": "Shift completed successfully",
        }

    # --- 4. Work Order Job Status -------------------------------------------

    @http.route("/technician/job/status", type="jsonrpc", auth="bearer", readonly=False)
    def job_status(self, **kwargs: Any) -> dict[str, Any]:
        """Update work order status (start work, complete work, fail work) on a work
        order assigned to the authenticated technician."""
        emp, err = resolve_technician(kwargs)
        if err:
            return err

        wo_id = kwargs.get("work_order_id")
        action = kwargs.get("action")  # 'start', 'complete', 'pause', 'fail'
        if not wo_id or not action:
            return _error("missing_params", "work_order_id and action are required")
        if action not in ("start", "complete", "pause", "fail"):
            return _error("invalid_action", "action must be start|complete|pause|fail")

        env = _su_env()
        wo = _own_work_order(env, emp, wo_id)
        if not wo:
            return _error("no_work_order", "Work order not found or not assigned to you")

        now = fields.Datetime.now()
        so = wo.order_id

        if action == "start":
            wo.write(
                {
                    "state": "in_progress",
                    "start_time": wo.start_time or now,
                }
            )
            # Only an APPROVED order (or one back from a failed QC) goes into
            # repair. Starting a job used to walk a draft order through
            # estimate and customer approval in one go (A02 audit M01-2): a
            # technician's tap approved a price the customer never saw.
            if so and so.state in ("approved", "qc_failed"):
                try:
                    with env.cr.savepoint():
                        so.action_start_repair()
                except Exception as ex:
                    _logger.warning("Could not transition SO %s state: %s", so.id, ex)

        elif action == "complete":
            wo.write(
                {
                    "state": "completed",
                    "end_time": now,
                }
            )
            if so and so.state == "in_repair":
                try:
                    with env.cr.savepoint():
                        so.action_submit_qc()
                except Exception as ex:
                    _logger.warning("Could not transition SO %s to qc_pending: %s", so.id, ex)

        elif action == "fail":
            wo.write({"state": "failed", "end_time": now})

        # action == "pause": acknowledged, no state change

        return {
            "work_order": {
                "id": wo.id,
                "name": wo.name,
                "state": wo.state,
                "start_time": str(wo.start_time or ""),
                "end_time": str(wo.end_time or ""),
                "duration_hours": wo.duration_hours,
                "service_order_state": so.state if so else None,
            }
        }

    # --- 5. Diagnostic Decision Trees & Fault Coding ------------------------

    @http.route("/technician/diagnostics/tree", type="jsonrpc", auth="bearer", readonly=True)
    def diagnostics_tree(self, **kwargs: Any) -> dict[str, Any]:
        """Return the diagnostic question/symptom decision tree nodes."""
        _emp, err = resolve_technician(kwargs)
        if err:
            return err

        env = _su_env()
        root_nodes = env["fix.diagnostic.node"].search(
            [("parent_id", "=", False), ("active", "=", True)]
        )

        result = []
        for r in root_nodes:
            children = []
            for c in r.children_ids:
                children.append(
                    {
                        "id": c.id,
                        "code": c.code,
                        "name": c.name,
                        "is_terminal": c.is_terminal,
                        "fault_code": c.fault_code or "",
                        "recommended_action": c.recommended_action or "",
                    }
                )
            result.append(
                {
                    "id": r.id,
                    "code": r.code,
                    "name": r.name,
                    "is_terminal": r.is_terminal,
                    "children": children,
                }
            )

        return {"trees": result, "total": len(result)}

    @http.route("/technician/diagnostics/submit", type="jsonrpc", auth="bearer", readonly=False)
    def diagnostics_submit(self, **kwargs: Any) -> dict[str, Any]:
        """Attach diagnosed fault code and terminal decision node to a work order
        assigned to the authenticated technician."""
        emp, err = resolve_technician(kwargs)
        if err:
            return err

        wo_id = kwargs.get("work_order_id")
        node_id = kwargs.get("node_id")
        fault_code = kwargs.get("fault_code")
        notes = kwargs.get("notes", "")

        if not wo_id or not (node_id or fault_code):
            return _error("missing_params", "work_order_id and node_id/fault_code are required")

        env = _su_env()
        wo = _own_work_order(env, emp, wo_id)
        if not wo:
            return _error("no_work_order", "Work order not found or not assigned to you")

        vals: dict[str, Any] = {}
        node_int = _to_int(node_id) if node_id else None
        if node_int:
            node = env["fix.diagnostic.node"].browse(node_int)
            if node.exists():
                vals["diagnostic_tree_id"] = node.id
                vals["diagnosed_fault_code"] = node.fault_code or fault_code
        if not vals.get("diagnosed_fault_code") and fault_code:
            vals["diagnosed_fault_code"] = fault_code

        if notes:
            vals["notes"] = f"{wo.notes or ''}\n[Diagnosis]: {notes}".strip()

        wo.write(vals)

        return {
            "diagnosis": {
                "work_order_id": wo.id,
                "diagnostic_tree_id": wo.diagnostic_tree_id.id if wo.diagnostic_tree_id else None,
                "diagnosed_fault_code": wo.diagnosed_fault_code,
                "notes": wo.notes,
            }
        }

    # --- 6. Van Stock Inventory & Scan-to-Consume ---------------------------

    @http.route("/technician/van-stock", type="jsonrpc", auth="bearer", readonly=True)
    def van_stock(self, **kwargs: Any) -> dict[str, Any]:
        """Return the technician's van location(s) and the van parts catalogue."""
        emp, err = resolve_technician(kwargs)
        if err:
            return err

        env = _su_env()
        # Only the authenticated technician's own van locations (cd_inventory).
        van_locations: list[dict[str, Any]] = []
        location_model = env.get("fix.stock.location")
        if location_model is not None:
            vans = location_model.search(
                [("technician_id", "=", emp.id), ("location_type", "=", "van")]
            )
            van_locations = [
                {"id": v.id, "code": v.code, "name": v.name, "van_plate": v.van_plate or ""}
                for v in vans
            ]

        # Query products matching parts
        prods = env["product.product"].search(
            [("default_code", "ilike", "PART-"), ("active", "=", True)], limit=50
        )

        items = []
        for p in prods:
            items.append(
                {
                    "id": p.id,
                    "default_code": p.default_code or "",
                    "barcode": p.barcode or "",
                    # translatable Char: the ORM returns the str of the env language
                    "name": p.name or "",
                    "list_price_bdt": _fmt_bdt(p.list_price),
                    "stock_qty": 5,  # van par level standard
                }
            )

        return {
            "technician_id": emp.id,
            "van_locations": van_locations,
            "van_stock": items,
            "total": len(items),
        }

    @http.route("/technician/van-stock/consume", type="jsonrpc", auth="bearer", readonly=False)
    def van_stock_consume(self, **kwargs: Any) -> dict[str, Any]:
        """Scan barcode or select part to record consumption against a work order
        assigned to the authenticated technician."""
        emp, err = resolve_technician(kwargs)
        if err:
            return err

        wo_id = kwargs.get("work_order_id")
        barcode_or_code = kwargs.get("barcode_or_code")
        product_id = kwargs.get("product_id")

        if not wo_id or not (product_id or barcode_or_code):
            return _error("missing_params", "work_order_id and product identifier are required")
        try:
            qty = float(kwargs.get("quantity", 1.0))
        except (TypeError, ValueError):
            qty = float("nan")
        if not math.isfinite(qty) or qty <= 0:
            return _error("invalid_quantity", "quantity must be a positive number")

        env = _su_env()
        wo = _own_work_order(env, emp, wo_id)
        if not wo:
            return _error("no_work_order", "Work order not found or not assigned to you")

        prod = env["product.product"]
        if product_id:
            product_int = _to_int(product_id)
            if product_int:
                prod = env["product.product"].browse(product_int).exists()
        else:  # the missing_params guard above ensures barcode_or_code is set
            prod = env["product.product"].search(
                ["|", ("barcode", "=", barcode_or_code), ("default_code", "=", barcode_or_code)],
                limit=1,
            )

        if not prod:
            return _error(
                "no_product", f"Part '{barcode_or_code or product_id}' not found in catalogue"
            )

        # Create consumed line on work order
        bdt_curr = env.ref("base.BDT", raise_if_not_found=False) or env["res.currency"].search(
            [("name", "=", "BDT")], limit=1
        )
        part_line = env["fix.work.order.part"].create(
            {
                "work_order_id": wo.id,
                "product_id": prod.id,
                "quantity": qty,
                "unit_cost": prod.list_price or 0.0,
                "currency_id": bdt_curr.id if bdt_curr else 1,
            }
        )

        return {
            "consumed": {
                "part_line_id": part_line.id,
                "work_order_id": wo.id,
                "product_id": prod.id,
                "product_code": prod.default_code,
                "product_name": prod.name,
                "quantity": qty,
                "unit_cost_bdt": _fmt_bdt(part_line.unit_cost),
                "line_total_bdt": _fmt_bdt(part_line.unit_cost * qty),
            }
        }

    # --- 7. SP-07 Offline Journal Replay & Sync -----------------------------

    @http.route("/technician/sync", type="jsonrpc", auth="bearer", readonly=False)
    def technician_sync(self, **kwargs: Any) -> dict[str, Any]:
        """SP-07 upload-first batch replay of offline journal commands, then the delta
        download of the technician's work orders changed after ``last_token``.

        The SP-03 ``batch_checksum`` (``batch_digest`` of ``commands``) is verified
        BEFORE any command is dispatched, exactly as on /api/v1/offline/sync: a
        missing or mismatching digest rejects the whole batch and executes nothing.
        DI-05: every command id is checked against the idempotency ledger shared with
        /api/v1/offline/sync, keyed by (technician, ``command_id``). A command already
        applied is NOT executed again: it is acknowledged with its original result plus
        ``"status": "already_applied"`` (and listed in ``duplicates``) so the client
        drops it; a command already rejected returns its recorded reason. Every new
        command's outcome is recorded. Without the ledger (cd_field_service not
        installed) the route refuses to replay anything (``ledger_unavailable``).
        Every replayed command runs through the same technician-scoped handler as its
        online route, so a command naming another technician or another technician's
        work order is rejected. ``last_token`` is an SP-07 sync token (see
        ``encode_sync_token``); a missing or malformed token means a full resync.
        """
        emp, err = resolve_technician(kwargs)
        if err:
            return err

        commands = kwargs.get("commands") or []
        if not isinstance(commands, list):
            return _error("invalid_batch", "commands must be a list")

        # SP-03: verify the client digest before any command is dispatched.
        checksum_error = verify_batch_checksum(commands, kwargs.get("batch_checksum"))
        if checksum_error:
            return checksum_error

        # DI-05: fail closed - replaying without the ledger re-executes retried batches.
        ledger = _su_env().get(LEDGER_MODEL)
        if ledger is None:
            return _error(
                "ledger_unavailable",
                "The DI-05 idempotency ledger is not installed; no command was executed",
            )

        handlers: dict[str, Callable[..., dict[str, Any]]] = {
            "clock_in": self.attendance_clock_in,
            "clock_out": self.attendance_clock_out,
            "job_status": self.job_status,
            "diagnose": self.diagnostics_submit,
            "consume_part": self.van_stock_consume,
        }
        device_id = kwargs.get("device_id") or "DEV-UNKNOWN"
        acknowledged: dict[str, dict[str, Any]] = {}
        rejected: dict[str, str] = {}
        duplicates: list[str] = []

        for cmd in commands:
            if not isinstance(cmd, dict) or not cmd.get("command_id"):
                continue
            cmd_id = str(cmd["command_id"])
            replay = ledger_lookup(ledger, cmd_id, emp)
            if replay:
                outcome, value = replay
                if outcome == "rejected":
                    rejected[cmd_id] = value
                else:
                    acknowledged[cmd_id] = dict(value, status="already_applied")
                    duplicates.append(cmd_id)
                continue
            op = cmd.get("operation")
            payload = cmd.get("payload") or {}
            # a non-string operation (e.g. a JSON list) is rejected like an unknown
            # one; looking it up unchecked raised TypeError and failed the batch
            if not isinstance(op, str) or op not in handlers:
                rejected[cmd_id] = f"Unsupported command operation: {op}"
                continue
            handler = handlers[op]
            if not isinstance(payload, dict):
                rejected[cmd_id] = "payload must be an object"
                continue

            entry: dict[str, object] = {
                "command_id": cmd_id,
                "technician_id": emp.id,
                "device_id": device_id,
                "model": SYNC_COMMAND_MODELS[op],
                "record_id": _to_int(payload.get("work_order_id")),
                "operation": op,
                "payload_hash": payload_digest(payload),
            }
            try:
                # SP-02: one savepoint per command so a failure never poisons the
                # batch; the ledger row commits (or rolls back) with the command.
                with request.env.cr.savepoint():
                    res = handler(**payload)
                    reason = res["error"]["message"] if "error" in res else None
                    ledger.record_execution(
                        **entry,
                        status="rejected" if reason else "applied",
                        response_dict=res,
                        conflict_reason=reason,
                    )
            except Exception as exc:
                _logger.exception("Error applying offline command %s: %s", cmd_id, exc)
                reason = str(exc)
                try:
                    with request.env.cr.savepoint():
                        ledger.record_execution(
                            **entry,
                            status="rejected",
                            response_dict={"error": reason},
                            conflict_reason=reason,
                        )
                except Exception:
                    _logger.exception("technician sync: could not record command %s", cmd_id)
                rejected[cmd_id] = reason
                continue
            if reason:
                rejected[cmd_id] = reason
            else:
                acknowledged[cmd_id] = res

        # Compute checksum over acknowledged IDs
        hasher = hashlib.sha256()
        for k in sorted(acknowledged.keys()):
            hasher.update(k.encode("utf-8"))
        checksum = hasher.hexdigest()[:16]

        deltas, next_token, has_more, full_resync = collect_deltas(
            _su_env()["fix.work.order"],
            [("technician_id", "=", emp.id)],
            kwargs.get("last_token"),
            _work_order_delta,
        )

        return {
            "sync": {
                "acknowledged": acknowledged,
                "rejected": rejected,
                "checksum": checksum,
                "token": next_token,
                "deltas": deltas,
                "has_more": has_more,
                "full_resync": full_resync,
                "ack_count": len(acknowledged),
                "rej_count": len(rejected),
                "duplicates": duplicates,
                "dup_count": len(duplicates),
            }
        }
