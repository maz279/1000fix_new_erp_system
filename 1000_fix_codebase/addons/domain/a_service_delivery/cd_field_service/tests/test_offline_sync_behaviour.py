"""Behavioural tests for /api/v1/offline/sync command dispatch (conflict matrix,
every operation, ledger recording) beyond the security contract in
test_api_security.py. Live ORM (``odoo_env``), ``request`` replaced by a stand-in.
"""

import json
from contextlib import contextmanager
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo import Command, http
from odoo.addons.cd_field_service.controllers import evidence_api, offline_sync_api
from odoo.addons.cd_field_service.controllers.offline_sync_api import OfflineSyncApiController
from odoo.addons.cd_field_service.models.fix_offline_idempotency_ledger import _client_timestamp
from odoo.addons.cd_service_order.controllers import technician_api
from odoo.addons.cd_service_order.controllers.technician_api import batch_digest


class _Request:
    def __init__(self, env):
        self.env = env
        self.session = http.Session(http.get_default_session(), "test-sid", new=True)


@contextmanager
def _as(env, user):
    fake = _Request(env(user=user.id))
    with (
        patch.object(technician_api, "request", fake),
        patch.object(offline_sync_api, "request", fake),
        patch.object(evidence_api, "request", fake),
    ):
        yield fake


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "OSBENT", "legal_name": "Offline Sync Entity", "company_id": env.company.id}
    )
    zone = env["fix.zone"].create({"name": "OS Zone", "code": "OSBZ"})
    env["fix.geofence"].create(
        {
            "name": "OS fence",
            "zone_id": zone.id,
            "geometry_json": '{"lat": 23.8, "lng": 90.4, "radius_m": 500}',
        }
    )
    branch = env["fix.branch"].create(
        {
            "name": "OS Branch",
            "code": "OSBB",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
            "zone_id": zone.id,
        }
    )
    brand = env["fix.brand"].create({"name": "OsbBrand", "code": "OSBBR"})
    device_model = env["fix.device.model"].create({"name": "OsbTV", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "OS Customer", "phone": "01911000000"})
    device = env["fix.device"].create(
        {"device_model_id": device_model.id, "owner_id": customer.id, "serial_number": "SN-OSB-1"}
    )
    so = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "No picture",
        }
    )
    tech_user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": "OS Tech", "login": "os.tech@sync.test"})
    )
    tech = env["hr.employee"].create(
        {"name": "OS Tech", "user_id": tech_user.id, "branch_id": branch.id}
    )
    fo_vals = {
        "order_id": so.id,
        "zone_id": zone.id,
        "operating_unit_id": ou.id,
        "technician_id": tech.id,
    }
    wo = env["fix.work.order"].create(
        {"order_id": so.id, "technician_id": tech.id, "certification_waiver": True}
    )
    part = env["product.product"].create(
        {
            "name": "OS Board",
            "default_code": "PART-OSB-1",
            "barcode": "BC-OSB-1",
            "list_price": 900.0,
        }
    )
    return SimpleNamespace(
        env=env, so=so, tech_user=tech_user, tech=tech, fo_vals=fo_vals, wo=wo, part=part
    )


def _fo(world, state="arrived", **vals):
    return world.env["fix.field.order"].create(dict(world.fo_vals, state=state, **vals))


# the centre of the technician's zone fence, with a good (10 m) GPS fix
DHAKA = {"geo_lat": 23.8, "geo_long": 90.4, "accuracy_m": 10}


def _sync(world, commands, **extra):
    with _as(world.env, world.tech_user):
        return OfflineSyncApiController().offline_sync(
            device_id="DEV-OSB", commands=commands, batch_checksum=batch_digest(commands), **extra
        )


def _cmd(cmd_id, operation, record_id=None, **payload):
    cmd = {"command_id": cmd_id, "operation": operation, "payload": payload}
    if record_id is not None:
        cmd["record_id"] = record_id
    return cmd


def _ledger(world, cmd_id):
    return world.env["fix.offline.idempotency.ledger"].search([("command_id", "=", cmd_id)])


# --- batch handling --------------------------------------------------------------------


def test_batch_shape_validation(world):
    with _as(world.env, world.tech_user):
        res = OfflineSyncApiController().offline_sync(commands={"not": "a list"})
    assert res["error"] == {"code": "invalid_batch", "message": "commands must be a list"}
    out = _sync(world, ["junk", {"operation": "clock_in"}, {"command_id": "osb-p", "payload": [1]}])
    assert (out["acknowledged"], out["rejected"]) == ({}, {"osb-p": "payload must be an object"})
    assert out["stats"] == {
        "total_uploaded": 3,
        "acknowledged_count": 0,
        "rejected_count": 1,
        "deltas_count": 0,
    }


def test_server_checksum_covers_acknowledged_and_rejected_ids(world):
    import hashlib

    out = _sync(world, [_cmd("osb-a", "clock_in", **DHAKA), _cmd("osb-r", "teleport")])
    # sha256("osb-a" + "rej:osb-r")[:16]
    assert out["batch_checksum"] == hashlib.sha256(b"osb-arej:osb-r").hexdigest()[:16]
    assert out["rejected"] == {"osb-r": "Unrecognized operation: teleport"}


# --- attendance ------------------------------------------------------------------------


def test_clock_in_is_idempotent_and_clock_out_needs_a_shift(world):
    out = _sync(
        world,
        [
            _cmd("osb-out0", "clock_out"),
            _cmd(
                "osb-in1",
                "clock_in",
                geo_lat=23.801,
                geo_long=90.401,
                accuracy_m=9,
                device_ref="TAB-3",
            ),
            _cmd("osb-in2", "clock_in", **DHAKA),
            _cmd("osb-out", "clock_out"),
        ],
    )
    assert out["rejected"] == {"osb-out0": "No open attendance shift found for technician"}
    att = world.env["fix.attendance.record"].browse(out["acknowledged"]["osb-in1"]["attendance_id"])
    assert (att.geo_lat, att.geo_long, att.device_ref, att.source) == (
        23.801,
        90.401,
        "TAB-3",
        "mobile_offline",  # replayed from the offline journal
    )
    # ~151 m from the fence centre (radius 500 m), 9 m accuracy: nothing to approve
    assert (att.geofence_result, att.approval_state, att.accuracy_m) == (
        "inside",
        "not_required",
        9.0,
    )
    second = out["acknowledged"]["osb-in2"]
    assert (second["attendance_id"], second["already_clocked_in"]) == (att.id, True)
    assert out["acknowledged"]["osb-out"]["attendance_id"] == att.id
    assert att.check_out
    assert _ledger(world, "osb-out0").status == "rejected"


def test_offline_clock_in_uses_the_same_own_zone_evaluation(world):
    """Regression: the offline clock_in evaluated no geofence at all and defaulted
    missing coordinates to the Dhaka centre. Now: same evaluation as online,
    recorded as source "mobile_offline", flagged for approval when out of fence."""
    out = _sync(
        world,
        [
            _cmd("osb-nc", "clock_in"),
            _cmd("osb-bad", "clock_in", geo_lat="north", geo_long=90.4),
            _cmd("osb-far", "clock_in", geo_lat=23.9, geo_long=90.4, accuracy_m=5),
        ],
    )
    assert out["rejected"] == {
        "osb-nc": "geo_lat and geo_long are required and numeric",
        "osb-bad": "geo_lat and geo_long are required and numeric",
    }
    far = out["acknowledged"]["osb-far"]
    # 0.1 degree of latitude from the fence centre = 11,119.49 m
    reason = "position outside the geofence of zone OSBZ (11119.5 m away)"
    assert (far["geofence_result"], far["approval_state"], far["approval_reason"]) == (
        "outside",
        "pending",
        reason,
    )
    att = world.env["fix.attendance.record"].browse(far["attendance_id"])
    assert (att.source, att.approval_state, att.accuracy_m) == ("mobile_offline", "pending", 5.0)


# --- field-order conflict matrix ------------------------------------------------------


def test_field_order_commands_need_an_existing_order(world):
    out = _sync(
        world,
        [
            _cmd("osb-noid", "start_order"),
            _cmd("osb-gone", "start_order", record_id=999999999),
            _cmd("osb-junk", "complete_order", order_id="abc"),
        ],
    )
    assert out["rejected"] == {
        "osb-noid": "Missing field order ID",
        "osb-gone": "Field order 999999999 not found on server",
        "osb-junk": "Field order abc not found on server",
    }


def test_start_order_applies_once_then_reports_the_conflict(world):
    order = _fo(world)
    out = _sync(world, [_cmd("osb-s1", "start_order", record_id=order.id)])
    again = _sync(world, [_cmd("osb-s2", "start_order", order_id=order.id)])  # id in payload
    assert out["acknowledged"]["osb-s1"] == {"order_id": order.id, "state": "in_progress"}
    assert order.state == "in_progress"
    assert again["conflicts"] == {"osb-s2": "Order was already marked in_progress on server"}
    assert again["acknowledged"]["osb-s2"]["state"] == "in_progress"
    assert _ledger(world, "osb-s2").status == "conflict_applied"


def test_cancelled_order_refuses_technician_actions(world):
    order = _fo(world, state="cancelled")
    out = _sync(world, [_cmd("osb-c", "start_order", record_id=order.id)])
    assert out["rejected"] == {
        "osb-c": f"Order {order.name} is cancelled on server; technician action disallowed"
    }


def test_a_model_error_is_rejected_and_recorded(world):
    order = _fo(world, state="accepted")  # start needs "arrived"
    out = _sync(
        world,
        [
            {
                **_cmd("osb-e", "start_order", record_id=order.id),
                "client_created_at": "2026-10-17T08:00:00Z",
            }
        ],
    )
    reason = "Technician must arrive on site before commencing work."
    assert out["rejected"] == {"osb-e": reason}
    entry = _ledger(world, "osb-e")
    assert (entry.status, entry.conflict_reason) == ("rejected", reason)
    assert json.loads(entry.response_payload) == {"error": reason}
    assert entry.client_created_at == datetime(2026, 10, 17, 8, 0)
    assert order.state == "accepted"


def test_iso_client_timestamps_no_longer_reject_the_command(world):
    """Regression: the documented "...Z" timestamp failed the ledger write, which
    rolled back and rejected every command carrying it."""
    order = _fo(world)
    cmd = {
        **_cmd("osb-ts", "start_order", record_id=order.id),
        "client_created_at": "2026-10-17T14:00:00+06:00",
    }
    out = _sync(world, [cmd])
    assert set(out["acknowledged"]) == {"osb-ts"}
    assert order.state == "in_progress"
    assert _ledger(world, "osb-ts").client_created_at == datetime(2026, 10, 17, 8, 0)


def test_client_timestamp_and_record_id_normalisation():
    assert _client_timestamp("2026-10-17T08:00:00Z") == datetime(2026, 10, 17, 8, 0)
    assert _client_timestamp("2026-10-17 08:00:00") == datetime(2026, 10, 17, 8, 0)
    assert _client_timestamp("yesterday") is None
    assert _client_timestamp(1729152000) is None
    assert _client_timestamp(None) is None


def test_a_ledger_failure_still_rejects_without_effect(world):
    order = _fo(world)
    ledger_class = type(world.env["fix.offline.idempotency.ledger"])
    with patch.object(ledger_class, "record_execution", side_effect=RuntimeError("ledger down")):
        out = _sync(world, [_cmd("osb-l", "start_order", record_id=order.id)])
    assert out["rejected"] == {"osb-l": "ledger down"}
    assert order.state == "arrived"  # rolled back with its savepoint


def test_complete_order_records_resolution_and_detects_double_completion(world):
    noted, plain = (
        _fo(world, state="in_progress", notes="Bring ladder"),
        _fo(world, state="in_progress"),
    )
    out = _sync(
        world,
        [
            _cmd(
                "osb-k1",
                "complete_order",
                record_id=noted.id,
                resolution_notes="Replaced capacitor",
            ),
            _cmd("osb-k2", "complete_order", record_id=plain.id),
            _cmd("osb-k3", "complete_order", record_id=plain.id),
        ],
    )
    assert noted.notes == "Bring ladder\n[Resolution]: Replaced capacitor"
    assert (noted.state, plain.state, plain.notes) == ("completed", "completed", False)
    assert out["conflicts"] == {"osb-k3": "Order already marked completed on server"}


def test_decline_order_maps_free_text_reasons(world):
    known, free, noted = (_fo(world, state="dispatched") for _ in range(3))
    out = _sync(
        world,
        [
            _cmd("osb-d1", "decline_order", record_id=known.id, reason="capacity"),
            _cmd("osb-d2", "decline_order", record_id=free.id, reason="Flat tyre"),
            _cmd("osb-d3", "decline_order", record_id=noted.id, notes="Sick"),
        ],
    )
    assert set(out["acknowledged"]) == {"osb-d1", "osb-d2", "osb-d3"}
    assert known.decline_reason == "capacity" and not known.decline_notes
    assert (free.decline_reason, free.decline_notes) == ("other", "Flat tyre")
    assert (noted.decline_reason, noted.decline_notes) == ("other", "Sick")
    assert not (known | free | noted).technician_id


def test_reassigned_order_is_rejected(world):
    other = world.env["hr.employee"].create({"name": "OS Other"})
    order = _fo(world, technician_id=other.id)
    out = _sync(world, [_cmd("osb-ra", "start_order", record_id=order.id)])
    assert out["rejected"] == {"osb-ra": f"Order {order.name} was reassigned to another technician"}


# --- work-order commands ---------------------------------------------------------------


def test_diagnose_variants(world):
    tree = world.env["fix.diagnostic.node"].create(
        {
            "name": "Picture?",
            "code": "OSB-D1",
            "children_ids": [
                Command.create({"name": "Backlight", "code": "OSB-D1A", "fault_code": "F-BL"})
            ],
        }
    )
    leaf = tree.children_ids
    wo_id = world.wo.id
    out = _sync(
        world,
        [
            _cmd("osb-g0", "diagnose", fault_code="F-X"),
            _cmd("osb-g1", "diagnose", work_order_id=wo_id, node_id=leaf.id),
            _cmd("osb-g2", "diagnose", work_order_id=wo_id, node_id=leaf.id, fault_code="F-OWN"),
            _cmd("osb-g3", "diagnose", work_order_id=wo_id, node_id=99999999, notes="dim"),
            _cmd("osb-g4", "diagnose", work_order_id=wo_id, node_id=tree.id),
            _cmd("osb-g5", "diagnose", work_order_id=wo_id, fault_code="F-FIN"),
        ],
    )
    assert out["rejected"] == {"osb-g0": "Missing work_order_id for diagnosis"}
    ack = out["acknowledged"]
    assert ack["osb-g1"] == {"work_order_id": wo_id, "fault_code": "F-BL"}  # from the node
    assert ack["osb-g2"]["fault_code"] == "F-OWN"  # the technician's code wins
    assert ack["osb-g3"]["fault_code"] == "F-OWN"  # unknown node: unchanged
    assert world.wo.notes == "[Diagnosis]: dim"
    assert ack["osb-g4"]["fault_code"] == "F-OWN"  # a node without a fault code adds none
    assert (world.wo.diagnostic_tree_id, world.wo.diagnosed_fault_code) == (tree, "F-FIN")


def test_consume_part_variants(world):
    wo_id = world.wo.id
    out = _sync(
        world,
        [
            _cmd("osb-p0", "consume_part", product_id=world.part.id),
            _cmd("osb-pn", "consume_part", work_order_id=wo_id),
            _cmd("osb-p1", "consume_part", work_order_id=wo_id, barcode="BC-OSB-1", quantity=2),
            _cmd("osb-p2", "consume_part", work_order_id=wo_id, barcode="NOPE"),
            _cmd("osb-p3", "consume_part", work_order_id=wo_id, product_id=99999999),
            _cmd(
                "osb-p4",
                "consume_part",
                work_order_id=wo_id,
                product_id=world.part.id,
                quantity="lots",
            ),
        ],
    )
    assert out["rejected"] == {
        "osb-p0": "Missing work_order_id for part consumption",
        "osb-pn": "Missing product_id or barcode for part consumption",
        "osb-p2": "Part product NOPE not found in inventory",
        "osb-p3": "Part product 99999999 not found in inventory",
        "osb-p4": "could not convert string to float: 'lots'",
    }
    assert out["acknowledged"]["osb-p1"]["product_code"] == "PART-OSB-1"
    line = world.wo.parts_consumed_ids
    assert (line.quantity, line.unit_cost, line.currency_id.name) == (2.0, 900.0, "BDT")


# --- signature, SOS, unknown ---------------------------------------------------------


def test_customer_signature_is_posted_on_the_own_order(world):
    order = _fo(world)
    out = _sync(
        world,
        [
            _cmd("osb-sig0", "customer_signature", signer_name="Rahim"),
            _cmd(
                "osb-sig1",
                "customer_signature",
                order_id=order.id,
                signer_name="Rahim",
                signature_token="TOK-1",
            ),
            _cmd("osb-sig2", "customer_signature", record_id=order.id, signature_base64="Q" * 40),
            _cmd("osb-sig3", "customer_signature", record_id="abc"),
        ],
    )
    assert out["rejected"] == {
        "osb-sig0": "Missing field order ID for customer signature",
        "osb-sig3": "Field order abc not found or not assigned to you",
    }
    assert out["acknowledged"]["osb-sig1"] == {
        "order_id": order.id,
        "signer": "Rahim",
        "verified": True,
    }
    bodies = order.message_ids.mapped("body")
    assert any("captured offline for Rahim. Token: TOK-1" in b for b in bodies)
    # no token: the first 32 characters of the bitmap stand in
    assert any(f"for Customer. Token: {'Q' * 32}" in b and "Q" * 33 not in b for b in bodies)


def test_panic_sos_and_unknown_operations(world):
    out = _sync(world, [_cmd("osb-sos", "panic_sos", lat=23.7, lng=90.3), _cmd("osb-x", "fly")])
    sos = out["acknowledged"]["osb-sos"]
    assert (sos["sos_acknowledged"], sos["dispatch_notified"]) == (True, True)
    assert out["rejected"] == {"osb-x": "Unrecognized operation: fly"}


# --- SP-09 deferred evidence channel ----------------------------------------------------


def _upload(world, **chunk):
    from odoo.addons.cd_field_service.controllers.evidence_api import OfflineEvidenceApiController

    with _as(world.env, world.tech_user):
        return OfflineEvidenceApiController().upload_chunk(**chunk)


def test_evidence_chunk_validation_and_hash_check(world):
    import base64
    import hashlib

    order = _fo(world)
    data = base64.b64encode(b"voice-bytes").decode()
    base = {"chunk_index": 0, "model": "fix.field.order", "record_id": order.id}
    assert _upload(world, **base)["error"]["code"] == "missing_params"
    assert _upload(world, media_uuid="v-1", chunk_index="first", record_id=order.id)["error"] == {
        "code": "missing_params",
        "message": "media_uuid and chunk_index required",
    }
    signed = _upload(
        world,
        media_uuid="v-1",
        chunk_data=data,
        chunk_hash=hashlib.sha256(data.encode("utf-8")).hexdigest(),
        media_type="voice_note_bengali",
        **base,
    )
    attachment = world.env["ir.attachment"].browse(signed["attachment_id"])
    assert (signed["status"], signed["received_chunks"], signed["total_chunks"]) == (
        "complete",
        1,
        1,
    )
    assert (attachment.mimetype, attachment.name) == ("audio/mp4", "voice_note_bengali_v-1.bin")
    assert base64.b64decode(attachment.datas) == b"voice-bytes"
    assert any(
        "Uploaded offline evidence [voice_note_bengali]" in m.body for m in order.message_ids
    )


def test_evidence_store_failure_is_reported_not_swallowed(world):
    """Regression: a failed store answered "complete" with no attachment and dropped
    the chunks - the client deleted its copy and the evidence was lost."""
    order = _fo(world)
    attachment_class = type(world.env["ir.attachment"])
    with patch.object(attachment_class, "create", side_effect=RuntimeError("disk full")):
        res = _upload(world, media_uuid="v-2", chunk_index=0, chunk_data="QUJD", record_id=order.id)
    assert res == {
        "error": {
            "code": "assembly_failed",
            "message": "Evidence v-2 could not be stored; restart its upload",
        }
    }
    assert (world.tech.id, "v-2") not in evidence_api._ACTIVE_CHUNKS  # restart from chunk 0
    retry = _upload(world, media_uuid="v-2", chunk_index=0, chunk_data="QUJD", record_id=order.id)
    assert retry["complete"] is True and retry["attachment_id"]
