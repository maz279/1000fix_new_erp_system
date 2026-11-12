"""offline_sync_api — Production-depth offline sync controller (SP-07, SP-01..03, DI-05, AR-010 §6).

Implements the upload-first offline synchronization protocol
(docs/guides/offline-sync-protocol.md):
1. Authenticate (``auth="bearer"``) and resolve the technician from the
   authenticated user only — never from a request parameter.
2. Verify the SP-03 batch checksum BEFORE dispatching anything; a missing or
   mismatching digest rejects the whole batch and executes nothing.
3. Execute each command in an isolated savepoint (SP-02), scoped to records
   assigned to the authenticated technician.
4. Check and record in fix.offline.idempotency.ledger (DI-05 exactly-once semantics).
5. Evaluate server-authoritative conflict matrix (apply, reject, conflict_applied).
6. Download deltas changed after the client's sync_token (full resync when the
   token is missing or malformed).
7. Return single unified response.
"""

import base64
import binascii
import hashlib
import logging
import math

from odoo import SUPERUSER_ID, fields, http
from odoo.addons.cd_service_order.controllers.technician_api import (
    _error,
    _to_int,
    clock_in_values,
    collect_deltas,
    evaluate_clock_in_position,
    ledger_lookup,
    parse_clock_in_position,
    payload_digest,
    resolve_technician,
    verify_batch_checksum,
)
from odoo.http import request

from libs.py.fix_api_edge import api_edge

_logger = logging.getLogger(__name__)

# A02 audit M02-8 (P2): "arrive" checks the technician in with the position
# the app reads, against the order's geofence. Without it the app could not
# reach "arrived" at all, and the workspace button was the only check-in.
FIELD_ORDER_OPERATIONS = ("arrive", "start_order", "complete_order", "decline_order")

# A02 audit M02-2: a signature is an image the customer drew, stored and
# hashed: PNG, JPEG or WEBP, and more than a token's worth of bytes.
_SIGNATURE_MAGIC = {
    b"\x89PNG\r\n\x1a\n": ("image/png", "png"),
    b"\xff\xd8\xff": ("image/jpeg", "jpg"),
    b"RIFF": ("image/webp", "webp"),
}
MIN_SIGNATURE_BYTES = 64
MAX_SIGNATURE_BYTES = 2 * 1024 * 1024


def _decode_signature(data):
    """(raw bytes, mimetype, extension) of a base64 signature image; a
    ValueError names what is wrong."""
    if not isinstance(data, str) or not data.strip():
        raise ValueError("signature_base64 is required")
    text = data.strip()
    if text.startswith("data:") and "," in text:
        text = text.split(",", 1)[1]
    try:
        raw = base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError):
        raise ValueError("signature_base64 is not valid base64") from None
    if not MIN_SIGNATURE_BYTES <= len(raw) <= MAX_SIGNATURE_BYTES:
        raise ValueError("the signature image is too small or too large")
    for magic, (mimetype, ext) in _SIGNATURE_MAGIC.items():
        if raw.startswith(magic):
            return raw, mimetype, ext
    raise ValueError("the signature must be a PNG, JPEG or WEBP image")


def _su_env():
    return request.env(user=SUPERUSER_ID, su=True)


def _field_order_delta(ord_rec):
    return {
        "model": "fix.field.order",
        "record_id": ord_rec.id,
        "state": ord_rec.state,
        "name": ord_rec.name,
        "customer_name": ord_rec.order_id.customer_id.name or "",
        "customer_phone": ord_rec.order_id.customer_id.phone or "",
        "address": ord_rec.customer_address or "",
        "priority": ord_rec.priority,
        "scheduled_date": str(ord_rec.scheduled_start or ""),
        "fault_description": ord_rec.order_id.fault_description or "",
        "write_date": str(ord_rec.write_date or ""),
    }


class OfflineSyncApiController(http.Controller):
    """Production offline sync endpoint for P02 Technician mobile app."""

    @http.route(
        ["/api/v1/offline/sync", "/technician/offline/sync"],
        type="jsonrpc",
        auth="bearer",
        methods=["POST"],
    )
    @api_edge("/api/v1/offline/sync")
    def offline_sync(self, **kwargs):
        """SP-07 Upload-first offline synchronization cycle.

        Payload (the technician is the authenticated user; ``technician_id`` is
        ignored when it names that user's employee and refused otherwise):
        {
            "client_id": "P02-TECH-001",
            "device_id": "DEV-UUID-1234",
            "sync_token": "TOKEN-2026-10-22T08:15:30.123456",
            "batch_checksum": "<sha256 hex of the canonical JSON of commands>",
            "commands": [
                {
                    "command_id": "cmd-uuid-...",
                    "model": "fix.field.order",
                    "record_id": 12,
                    "operation": "start_order",
                    "payload": { ... },
                    "client_created_at": "2026-10-17T08:00:00Z"
                }
            ]
        }
        """
        tech, err = resolve_technician(kwargs)
        if err:
            return err

        commands = kwargs.get("commands") or []
        if not isinstance(commands, list):
            return _error("invalid_batch", "commands must be a list")

        # SP-03: verify the client digest before any command is dispatched.
        checksum_error = verify_batch_checksum(commands, kwargs.get("batch_checksum"))
        if checksum_error:
            return checksum_error

        env = _su_env()
        device_id = kwargs.get("device_id", "DEV-UNKNOWN")
        ledger_model = env["fix.offline.idempotency.ledger"]

        acknowledged = {}
        rejected = {}
        conflicts = {}

        # -----------------------------------------------------------------
        # STEP 1: SP-07 UPLOAD FIRST — Process all commands in journal
        # -----------------------------------------------------------------
        for cmd in commands:
            if not isinstance(cmd, dict) or not cmd.get("command_id"):
                continue
            cmd_id = str(cmd["command_id"])

            model_name = cmd.get("model", "fix.field.order")
            record_id = cmd.get("record_id")
            operation = cmd.get("operation")
            payload = cmd.get("payload") or {}
            client_ts = cmd.get("client_created_at")
            if not isinstance(payload, dict):
                rejected[cmd_id] = "payload must be an object"
                continue

            # DI-05: Check idempotency ledger — a replay only returns the cached
            # result to the technician who issued the command.
            replay = ledger_lookup(ledger_model, cmd_id, tech)
            if replay:
                outcome, value = replay
                (rejected if outcome == "rejected" else acknowledged)[cmd_id] = value
                continue

            # Compute payload SHA-256 for integrity auditing
            payload_hash = payload_digest(payload)

            # SP-02: Isolated transaction per command
            try:
                with env.cr.savepoint():
                    cmd_status, cmd_res, conflict_msg = self._dispatch_command(
                        env, tech, model_name, record_id, operation, payload
                    )

                    ledger_model.record_execution(
                        command_id=cmd_id,
                        technician_id=tech.id,
                        device_id=device_id,
                        model=model_name,
                        record_id=record_id,
                        operation=operation,
                        payload_hash=payload_hash,
                        status=cmd_status,
                        response_dict=cmd_res,
                        conflict_reason=conflict_msg,
                        client_created_at=client_ts,
                    )

                    if cmd_status == "rejected":
                        rejected[cmd_id] = conflict_msg or "Rejected by server policy"
                    else:
                        acknowledged[cmd_id] = cmd_res
                        if cmd_status == "conflict_applied":
                            conflicts[cmd_id] = conflict_msg

            except Exception as exc:
                _logger.exception(
                    "Failed executing offline command %s (%s): %s", cmd_id, operation, exc
                )
                err_msg = str(exc)
                try:
                    with env.cr.savepoint():
                        ledger_model.record_execution(
                            command_id=cmd_id,
                            technician_id=tech.id,
                            device_id=device_id,
                            model=model_name,
                            record_id=record_id,
                            operation=operation,
                            payload_hash=payload_hash,
                            status="rejected",
                            response_dict={"error": err_msg},
                            conflict_reason=err_msg,
                            client_created_at=client_ts,
                        )
                except Exception:
                    _logger.exception("offline sync: could not record rejected command %s", cmd_id)
                rejected[cmd_id] = err_msg

        # Compute server batch checksum over processed commands
        hasher = hashlib.sha256()
        for k in sorted(acknowledged.keys()):
            hasher.update(k.encode("utf-8"))
        for k in sorted(rejected.keys()):
            hasher.update(f"rej:{k}".encode())
        server_checksum = hasher.hexdigest()[:16]

        # -----------------------------------------------------------------
        # STEP 2: SP-07 DOWNLOAD DELTAS — records changed after sync_token
        # -----------------------------------------------------------------
        # fix.field.order is defined by this module, so it is always in the registry.
        deltas, next_sync_token, has_more, full_resync = collect_deltas(
            env["fix.field.order"],
            [("technician_id", "=", tech.id), ("active", "=", True)],
            kwargs.get("sync_token"),
            _field_order_delta,
        )

        return {
            "status": "success",
            "acknowledged": acknowledged,
            "rejected": rejected,
            "conflicts": conflicts,
            "batch_checksum": server_checksum,
            "next_token": next_sync_token,
            "full_resync": full_resync,
            "has_more": has_more,
            "deltas": deltas,
            "stats": {
                "total_uploaded": len(commands),
                "acknowledged_count": len(acknowledged),
                "rejected_count": len(rejected),
                "deltas_count": len(deltas),
            },
        }

    @staticmethod
    def _own_record(env, model_name, record_id, tech):
        """``model_name``/``record_id`` if that record is assigned to ``tech``, else
        an empty recordset (unknown and foreign ids are indistinguishable)."""
        rec_id = _to_int(record_id)
        if rec_id is None:
            return env[model_name]
        return env[model_name].search(
            [("id", "=", rec_id), ("technician_id", "=", tech.id)], limit=1
        )

    # The people a panic alert reaches: dispatch and HSE, in the technician's company.
    PANIC_GROUPS = (
        "cd_field_service.group_fix_field_service_manager",
        "cd_hse.group_hse_officer",
    )
    PANIC_ACTIVE_STATES = ("dispatched", "accepted", "en_route", "arrived", "in_progress")

    def _raise_panic(self, env, tech, payload, now):
        """A panic alert reaches people (FR-FSM-031, M02 capture audit 2026-11-13).

        It used to write a log line and answer ``dispatch_notified: True`` while
        nobody was told. Now: the technician's open lone-worker session escalates
        (M59's contact chain), and every dispatcher and HSE Officer of the
        technician's company, plus the session's buddy and the dispatcher who
        opened it, gets an urgent to-do on the active field order (or on the
        technician). ``dispatch_notified`` says whether anyone was reached.
        """
        lat, lng = payload.get("lat"), payload.get("lng")
        notes = str(payload.get("notes") or "").strip()[:500]
        where = "%s, %s" % (lat, lng) if lat not in (None, "") and lng not in (None, "") else ""
        _logger.critical(
            "PANIC SOS RECEIVED from technician %s at (%s): %s", tech.name, where or "-", notes
        )
        company = tech.company_id or env.company
        users = env["res.users"]
        for xmlid in self.PANIC_GROUPS:
            group = env.ref(xmlid, raise_if_not_found=False)
            if group:
                users |= group.sudo().all_user_ids
        order = env["fix.field.order"].search(
            [("technician_id", "=", tech.id), ("state", "in", self.PANIC_ACTIVE_STATES)],
            order="scheduled_start desc, id desc",
            limit=1,
        )
        escalated = False
        if "fix.hse.loneworker" in env:
            session = env["fix.hse.loneworker"].search(
                [("employee_id", "=", tech.id), ("state", "in", ("checked_in", "missed"))],
                order="checkin_time desc, id desc",
                limit=1,
            )
            if session:
                session._fix_escalate()
                escalated = session.name
                users |= session.buddy_id.user_id | session.opened_by_id
        users = users.filtered(
            lambda u: u.active and not u.share and company in u.company_ids and u != tech.user_id
        )
        target = order or tech
        note = (
            "%s pressed the panic button at %s%s.%s%s Contact them now; open an incident "
            "if they cannot be reached."
        ) % (
            tech.name,
            now,
            " (position %s)" % where if where else " (no position sent)",
            " Field order %s." % order.name if order else "",
            " Message: %s." % notes if notes else "",
        )
        for user in users:
            target.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=fields.Date.context_today(target),
                summary="PANIC SOS: %s" % tech.name,
                note=note,
                user_id=user.id,
            )
        target.message_post(body=note)
        result = {
            "sos_acknowledged": True,
            "timestamp": str(now),
            "dispatch_notified": bool(users),
            "notified_count": len(users),
            "field_order": order.name or False,
            "loneworker_escalated": escalated,
        }
        if not users:
            result["message"] = (
                "No dispatcher or HSE Officer could be alerted: call the 16743 hotline now."
            )
        return ("applied", result, None)

    @staticmethod
    def _find_part(env, payload):
        product_id, barcode = payload.get("product_id"), payload.get("barcode")
        if product_id:
            return env["product.product"].browse(_to_int(product_id) or 0).exists()
        if barcode:
            return env["product.product"].search(
                ["|", ("barcode", "=", barcode), ("default_code", "=", barcode)], limit=1
            )
        return env["product.product"]

    def _consume_field_part(self, env, tech, record_id, payload):
        """Record a part the technician fitted on his field order, on site."""
        order_id = payload.get("field_order_id") or record_id
        order = self._own_record(env, "fix.field.order", order_id, tech)
        if not order:
            return "rejected", {}, f"Field order {order_id} not found or not assigned to you"
        if order.state not in ("arrived", "in_progress"):
            return (
                "rejected",
                {},
                f"Parts are recorded on site; field order {order.name} is {order.state}",
            )
        try:
            qty = float(payload.get("quantity", 1.0))
        except (TypeError, ValueError):
            qty = float("nan")
        if not (math.isfinite(qty) and qty > 0):
            return "rejected", {}, "quantity must be a positive number"
        prod = self._find_part(env, payload)
        if not prod:
            return (
                "rejected",
                {},
                "Part product %s not found in inventory"
                % (payload.get("product_id") or payload.get("barcode") or "(none given)"),
            )
        line = env["fix.field.order.part"].create(
            {
                "field_order_id": order.id,
                "product_id": prod.id,
                "quantity": qty,
                "lot_serial_number": payload.get("lot_serial_number") or False,
            }
        )
        line._guarded().write({"source_ref": "offline sync (%s)" % tech.name})
        line.action_consume()
        return (
            "applied",
            {
                "field_order_id": order.id,
                "part_line_id": line.id,
                "product_code": prod.default_code,
                "quantity": qty,
                "state": line.state,
            },
            None,
        )

    def _dispatch_command(self, env, tech, model_name, record_id, operation, payload):
        """Dispatch individual command and apply conflict authority rules.

        Every record-targeting command must address a record assigned to ``tech``.

        Returns: (status, response_dict, conflict_reason)
        where status is in ('applied', 'rejected', 'conflict_applied')
        """
        now = fields.Datetime.now()

        # 1. Geofenced Clock-in
        if operation == "clock_in":
            # the same own-zone geofence + accuracy evaluation (M55 AUT-WFM-02) as
            # /technician/attendance/clock_in; coordinates are required
            try:
                lat, lng, accuracy_m = parse_clock_in_position(payload)
            except ValueError as exc:
                return "rejected", {}, str(exc)
            device_ref = payload.get("device_ref", "P02-TECH-MOBILE")

            open_att = env["fix.attendance.record"].search(
                [("employee_id", "=", tech.id), ("check_out", "=", False)], order="id desc", limit=1
            )
            if open_att:
                return (
                    "applied",
                    {
                        "attendance_id": open_att.id,
                        "already_clocked_in": True,
                        "check_in": str(open_att.check_in),
                    },
                    None,
                )

            evaluation = evaluate_clock_in_position(env, tech, lat, lng, accuracy_m)
            att = env["fix.attendance.record"].create(
                clock_in_values(
                    tech, lat, lng, accuracy_m, evaluation, "mobile_offline", device_ref, now
                )
            )
            return (
                "applied",
                {
                    "attendance_id": att.id,
                    "check_in": str(now),
                    "geofence_result": evaluation["geofence_result"],
                    "approval_state": evaluation["approval_state"],
                    "approval_reason": evaluation["reason"],
                },
                None,
            )

        # 2. Clock-out
        if operation == "clock_out":
            open_att = env["fix.attendance.record"].search(
                [("employee_id", "=", tech.id), ("check_out", "=", False)], order="id desc", limit=1
            )
            if not open_att:
                return "rejected", {}, "No open attendance shift found for technician"

            open_att.write({"check_out": now})
            return (
                "applied",
                {
                    "attendance_id": open_att.id,
                    "check_out": str(now),
                    "worked_hours": round(open_att.worked_hours or 0.0, 2),
                },
                None,
            )

        # 3. Field Order State Management & Conflicts
        if operation in FIELD_ORDER_OPERATIONS:
            order_id = record_id or payload.get("order_id")
            if not order_id:
                return "rejected", {}, "Missing field order ID"

            order = env["fix.field.order"].browse(_to_int(order_id) or 0).exists()
            if not order:
                return "rejected", {}, f"Field order {order_id} not found on server"

            # Conflict Detection: Technician Assignment (server authoritative)
            if order.technician_id.id != tech.id:
                if order.technician_id:
                    return (
                        "rejected",
                        {},
                        f"Order {order.name} was reassigned to another technician",
                    )
                return "rejected", {}, f"Order {order.name} is not assigned to you"

            # Conflict Detection: Terminal or Locked state
            if order.state in ("cancelled", "closed"):
                return (
                    "rejected",
                    {},
                    f"Order {order.name} is {order.state} on server; technician action disallowed",
                )

            if operation == "arrive":
                if order.state == "arrived":
                    return (
                        "conflict_applied",
                        {"order_id": order.id, "state": order.state},
                        "Order was already marked arrived on server",
                    )
                position = payload.get("position")
                if position in (None, "", False):
                    position = (payload.get("lat"), payload.get("lng"))
                    if None in position:
                        return (
                            "rejected",
                            {},
                            "An arrival needs the device position (lat, lng)",
                        )
                try:
                    lat, lng = order._fix_parse_position(position)
                except Exception as exc:  # UserError: an unreadable position
                    return "rejected", {}, str(exc.args[0] if exc.args else exc)
                order.action_arrive(
                    current_lat=lat,
                    current_lon=lng,
                    is_mock_location=payload.get("is_mock_location") is True,
                )
                return (
                    "applied",
                    {
                        "order_id": order.id,
                        "state": order.state,
                        "arrival_latitude": order.arrival_latitude,
                        "arrival_longitude": order.arrival_longitude,
                    },
                    None,
                )

            if operation == "start_order":
                if order.state == "in_progress":
                    # Idempotent or concurrent start
                    return (
                        "conflict_applied",
                        {
                            "order_id": order.id,
                            "state": order.state,
                            "server_write_date": str(order.write_date or ""),
                        },
                        "Order was already marked in_progress on server",
                    )

                order.action_start_work()
                return (
                    "applied",
                    {
                        "order_id": order.id,
                        "state": order.state,
                    },
                    None,
                )

            if operation == "complete_order":
                if order.state == "completed":
                    return (
                        "conflict_applied",
                        {
                            "order_id": order.id,
                            "state": order.state,
                        },
                        "Order already marked completed on server",
                    )

                res_notes = payload.get("resolution_notes", "")
                if res_notes:
                    order.notes = f"{order.notes or ''}\n[Resolution]: {res_notes}".strip()
                    # the resolution the technician typed is the work summary
                    # completion requires (A02 audit M02-2), unless one exists
                    if not (order.work_summary or "").strip():
                        order.work_summary = res_notes
                order.action_complete()
                return (
                    "applied",
                    {
                        "order_id": order.id,
                        "state": order.state,
                    },
                    None,
                )

            # decline_order
            reason = payload.get("reason") or "other"
            reasons = dict(order._fields["decline_reason"].selection)
            notes = payload.get("notes") or ("" if reason in reasons else str(reason))
            order.action_decline(reason=reason if reason in reasons else "other", notes=notes)
            return (
                "applied",
                {
                    "order_id": order.id,
                    "state": order.state,
                },
                None,
            )

        # 4. Diagnostic Submit
        if operation == "diagnose":
            wo_id = payload.get("work_order_id")
            fault_code = payload.get("fault_code")
            node_id = payload.get("node_id")
            notes = payload.get("notes", "")

            if not wo_id:
                return "rejected", {}, "Missing work_order_id for diagnosis"

            wo = self._own_record(env, "fix.work.order", wo_id, tech)
            if not wo:
                return "rejected", {}, f"Work order {wo_id} not found or not assigned to you"

            vals = {}
            if fault_code:
                vals["diagnosed_fault_code"] = fault_code
            if node_id:
                node = env["fix.diagnostic.node"].browse(_to_int(node_id) or 0)
                if node.exists():
                    vals["diagnostic_tree_id"] = node.id
                    if not vals.get("diagnosed_fault_code") and node.fault_code:
                        vals["diagnosed_fault_code"] = node.fault_code
            if notes:
                vals["notes"] = f"{wo.notes or ''}\n[Diagnosis]: {notes}".strip()

            wo.write(vals)
            return (
                "applied",
                {
                    "work_order_id": wo.id,
                    "fault_code": wo.diagnosed_fault_code,
                },
                None,
            )

        # 5. Parts Consumption
        # A02 audit M02 step 7 (P2): a part fitted on a field job is a line
        # on that field order (fix.field.order.part), which completion checks.
        # The work-order path below stays for the bench app's M01 work orders.
        if operation == "consume_part" and (
            payload.get("field_order_id")
            or (record_id and model_name == "fix.field.order" and not payload.get("work_order_id"))
        ):
            return self._consume_field_part(env, tech, record_id, payload)

        if operation == "consume_part":
            wo_id = payload.get("work_order_id")
            product_id = payload.get("product_id")
            barcode = payload.get("barcode")
            qty = float(payload.get("quantity", 1.0))

            if not wo_id:
                return "rejected", {}, "Missing work_order_id for part consumption"
            if not (product_id or barcode):
                return "rejected", {}, "Missing product_id or barcode for part consumption"
            if not (math.isfinite(qty) and qty > 0):
                return "rejected", {}, "quantity must be a positive number"

            wo = self._own_record(env, "fix.work.order", wo_id, tech)
            if not wo:
                return "rejected", {}, f"Work order {wo_id} not found or not assigned to you"

            if product_id:
                prod = env["product.product"].browse(_to_int(product_id) or 0).exists()
            else:
                prod = env["product.product"].search(
                    ["|", ("barcode", "=", barcode), ("default_code", "=", barcode)], limit=1
                )

            if not prod:
                return (
                    "rejected",
                    {},
                    f"Part product {product_id or barcode} not found in inventory",
                )

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
                    "fitted_serial_number": payload.get("serial_number") or False,
                }
            )

            return (
                "applied",
                {
                    "part_line_id": part_line.id,
                    "product_code": prod.default_code,
                    "quantity": qty,
                },
                None,
            )

        # 6. Customer E-Signature
        # A02 audit M02-2: this op answered verified=True and stored only a
        # chatter line with a client token. It now stores the signature image
        # (or links one uploaded through the evidence channel) as an
        # attachment with its SHA-256; a token alone is refused.
        if operation == "customer_signature":
            order_id = record_id or payload.get("order_id")
            sig_name = payload.get("signer_name", "Customer")

            if not order_id:
                return "rejected", {}, "Missing field order ID for customer signature"
            order = self._own_record(env, "fix.field.order", order_id, tech)
            if not order:
                return "rejected", {}, f"Field order {order_id} not found or not assigned to you"

            attachment = env["ir.attachment"]
            if payload.get("attachment_id"):
                attachment = attachment.search(
                    [
                        ("id", "=", _to_int(payload.get("attachment_id")) or 0),
                        ("res_model", "=", "fix.field.order"),
                        ("res_id", "=", order.id),
                    ],
                    limit=1,
                )
                if not attachment:
                    return "rejected", {}, "The signature attachment is not on this order"
            else:
                try:
                    raw, mimetype, ext = _decode_signature(payload.get("signature_base64"))
                except ValueError as exc:
                    return (
                        "rejected",
                        {},
                        "A signature image is required (%s); a token is not evidence" % exc,
                    )
                attachment = attachment.create(
                    {
                        "name": "customer_signature_%s.%s" % (order.name.replace("/", "_"), ext),
                        "type": "binary",
                        "raw": raw,
                        "mimetype": mimetype,
                        "res_model": "fix.field.order",
                        "res_id": order.id,
                        "description": "Customer signature (%s), captured offline by %s"
                        % (sig_name, tech.name),
                    }
                )
            order._fix_attach_field_evidence(attachment, "signature", signer=sig_name)
            order.message_post(
                body=f"Customer signature captured offline for {sig_name}.",
                attachment_ids=[attachment.id],
            )
            return (
                "applied",
                {
                    "order_id": order.id,
                    "signer": sig_name,
                    "attachment_id": attachment.id,
                    "sha256": order.customer_signature_sha256,
                    "recorded": True,
                },
                None,
            )

        # 7. Panic SOS Distress Signal (M59 slice)
        if operation == "panic_sos":
            return self._raise_panic(env, tech, payload, now)

        return "rejected", {}, f"Unrecognized operation: {operation}"
