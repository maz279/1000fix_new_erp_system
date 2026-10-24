"""Behavioural security tests for the offline sync + evidence channel (R01 re-audit 2026-10-22).

Runs against the live ORM (``odoo_env``: database fix_test, rolled back per test)
with ``odoo.http.request`` replaced by a minimal stand-in exposing ``env`` /
``session`` — the controller code itself runs unmodified.
"""

import base64
from contextlib import contextmanager
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo import http
from odoo.addons.cd_field_service.controllers import evidence_api, offline_sync_api
from odoo.addons.cd_field_service.controllers.evidence_api import OfflineEvidenceApiController
from odoo.addons.cd_field_service.controllers.offline_sync_api import OfflineSyncApiController
from odoo.addons.cd_service_order.controllers import technician_api
from odoo.addons.cd_service_order.controllers.technician_api import (
    SYNC_CURSOR_OVERLAP,
    batch_digest,
    encode_sync_token,
    parse_sync_token,
)


class _Request:
    def __init__(self, env):
        self.env = env
        self.session = http.Session(http.get_default_session(), "test-sid", new=True)


@contextmanager
def _as(env, user):
    """Run controller code as ``user`` (a res.users record)."""
    fake = _Request(env(user=user.id))
    with (
        patch.object(technician_api, "request", fake),
        patch.object(offline_sync_api, "request", fake),
        patch.object(evidence_api, "request", fake),
    ):
        yield fake


def _set_write_date(env, record, when):
    env.flush_all()  # pending ORM writes would otherwise re-stamp write_date
    env.cr.execute(
        f'UPDATE "{record._table}" SET write_date = %s WHERE id = %s',
        (when, record.id),
    )
    env.invalidate_all()


def _sync(commands, checksum="auto", **extra):
    payload = {"device_id": "DEV-SEC", "commands": commands, **extra}
    if checksum == "auto":
        payload["batch_checksum"] = batch_digest(commands)
    elif checksum is not None:
        payload["batch_checksum"] = checksum
    return OfflineSyncApiController().offline_sync(**payload)


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "SECENT", "legal_name": "Security Test Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {"name": "Sec Branch", "code": "SECB", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "SecBrand", "code": "SECBR"})
    device_model = env["fix.device.model"].create({"name": "SecPhone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "Sec Customer", "phone": "01711000000"})
    device = env["fix.device"].create(
        {"device_model_id": device_model.id, "owner_id": customer.id, "serial_number": "SN-SEC-1"}
    )
    so = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "No power",
        }
    )
    users = env["res.users"].with_context(no_reset_password=True)
    tech_a_user = users.create({"name": "Tech A", "login": "tech.a@sec.test"})
    tech_b_user = users.create({"name": "Tech B", "login": "tech.b@sec.test"})
    clerk_user = users.create({"name": "Clerk", "login": "clerk@sec.test"})
    tech_a = env["hr.employee"].create({"name": "Tech A", "user_id": tech_a_user.id})
    tech_b = env["hr.employee"].create({"name": "Tech B", "user_id": tech_b_user.id})
    zone = env["fix.zone"].create({"name": "Sec Zone", "code": "SECZ"})
    fo_vals = {"order_id": so.id, "zone_id": zone.id, "operating_unit_id": ou.id}
    fo_a = env["fix.field.order"].create(dict(fo_vals, technician_id=tech_a.id, state="arrived"))
    fo_a2 = env["fix.field.order"].create(dict(fo_vals, technician_id=tech_a.id, state="arrived"))
    fo_b = env["fix.field.order"].create(dict(fo_vals, technician_id=tech_b.id, state="arrived"))
    fo_free = env["fix.field.order"].create(dict(fo_vals, state="arrived"))
    wo_vals = {"order_id": so.id, "certification_waiver": True}
    wo_a = env["fix.work.order"].create(dict(wo_vals, technician_id=tech_a.id))
    wo_b = env["fix.work.order"].create(dict(wo_vals, technician_id=tech_b.id))
    part = env["product.product"].create(
        {"name": "Sec Part", "default_code": "PART-SEC-1", "list_price": 250.0}
    )
    return SimpleNamespace(
        env=env,
        tech_a_user=tech_a_user,
        tech_b_user=tech_b_user,
        clerk_user=clerk_user,
        public_user=env.ref("base.public_user"),
        tech_a=tech_a,
        tech_b=tech_b,
        fo_a=fo_a,
        fo_a2=fo_a2,
        fo_b=fo_b,
        fo_free=fo_free,
        wo_a=wo_a,
        wo_b=wo_b,
        part=part,
    )


def _ledger(env):
    return env["fix.offline.idempotency.ledger"].search([])


def _start(order, cmd_id="cmd-start"):
    return {
        "command_id": cmd_id,
        "model": "fix.field.order",
        "record_id": order.id,
        "operation": "start_order",
        "payload": {},
    }


# --- route declaration ---------------------------------------------------------


@pytest.mark.parametrize(
    "endpoint",
    [OfflineSyncApiController.offline_sync, OfflineEvidenceApiController.upload_chunk],
)
def test_routes_require_bearer_auth_and_send_no_cors(endpoint):
    routing = endpoint.original_routing
    assert routing["auth"] == "bearer"
    assert "cors" not in routing
    assert routing["methods"] == ["POST"]


# --- identity --------------------------------------------------------------------


def test_unauthenticated_and_employee_less_callers_execute_nothing(world):
    commands = [_start(world.fo_a)]
    with _as(world.env, world.public_user):
        assert _sync(commands)["error"]["code"] == "unauthenticated"
    with _as(world.env, world.clerk_user):
        assert _sync(commands)["error"]["code"] == "no_employee"
    assert world.fo_a.state == "arrived"
    assert not _ledger(world.env)


def test_technician_id_impersonation_is_refused(world):
    commands = [_start(world.fo_b)]
    with _as(world.env, world.tech_a_user):
        res = _sync(commands, technician_id=world.tech_b.id)
    assert res["error"]["code"] == "forbidden"
    assert world.fo_b.state == "arrived"
    assert not _ledger(world.env)


# --- SP-03 batch checksum ----------------------------------------------------------


def test_missing_checksum_rejects_the_whole_batch(world):
    commands = [_start(world.fo_a), {"command_id": "cmd-in", "operation": "clock_in"}]
    with _as(world.env, world.tech_a_user):
        res = _sync(commands, checksum=None)
        empty = _sync(commands, checksum="")
    assert res["error"]["code"] == "checksum_missing"
    assert empty["error"]["code"] == "checksum_missing"
    assert world.fo_a.state == "arrived"
    assert not _ledger(world.env)
    assert not world.env["fix.attendance.record"].search([])


def test_mismatching_checksum_rejects_the_whole_batch(world):
    signed = [_start(world.fo_a)]
    tampered = [_start(world.fo_a), _start(world.fo_a2, "cmd-smuggled")]
    with _as(world.env, world.tech_a_user):
        res = _sync(tampered, checksum=batch_digest(signed))
    assert res["error"]["code"] == "checksum_mismatch"
    assert (world.fo_a.state, world.fo_a2.state) == ("arrived", "arrived")
    assert not _ledger(world.env)


def test_correct_checksum_executes_and_records_the_ledger(world):
    commands = [_start(world.fo_a)]
    with _as(world.env, world.tech_a_user):
        res = _sync(commands)
        replay = _sync(commands)
    assert res["status"] == "success"
    assert set(res["acknowledged"]) == {"cmd-start"}
    assert len(res["batch_checksum"]) == 16
    assert world.fo_a.state == "in_progress"
    entry = _ledger(world.env)
    assert entry.command_id == "cmd-start"
    assert entry.technician_id == world.tech_a
    # DI-05: an exact replay is answered from the ledger without re-executing
    assert replay["acknowledged"]["cmd-start"] == res["acknowledged"]["cmd-start"]
    assert len(_ledger(world.env)) == 1


# --- command scoping ----------------------------------------------------------------


def test_commands_on_records_of_other_technicians_are_rejected(world):
    commands = [
        _start(world.fo_b, "cmd-foreign"),
        _start(world.fo_free, "cmd-unassigned"),
        {
            "command_id": "cmd-diag",
            "operation": "diagnose",
            "payload": {"work_order_id": world.wo_b.id, "fault_code": "F-X"},
        },
        {
            "command_id": "cmd-part",
            "operation": "consume_part",
            "payload": {"work_order_id": world.wo_b.id, "product_id": world.part.id},
        },
        {
            "command_id": "cmd-sign",
            "operation": "customer_signature",
            "record_id": world.fo_b.id,
            "payload": {"signer_name": "Mallory"},
        },
        {
            "command_id": "cmd-own-diag",
            "operation": "diagnose",
            "payload": {"work_order_id": world.wo_a.id, "fault_code": "F-OK"},
        },
        {
            "command_id": "cmd-own-part",
            "operation": "consume_part",
            "payload": {"work_order_id": world.wo_a.id, "product_id": world.part.id},
        },
        {
            "command_id": "cmd-bad-qty",
            "operation": "consume_part",
            "payload": {
                "work_order_id": world.wo_a.id,
                "product_id": world.part.id,
                "quantity": -1,
            },
        },
    ]
    with _as(world.env, world.tech_a_user):
        res = _sync(commands)
    assert set(res["rejected"]) == {
        "cmd-foreign",
        "cmd-unassigned",
        "cmd-diag",
        "cmd-part",
        "cmd-sign",
        "cmd-bad-qty",
    }
    assert set(res["acknowledged"]) == {"cmd-own-diag", "cmd-own-part"}
    assert "reassigned" in res["rejected"]["cmd-foreign"]
    assert "not assigned to you" in res["rejected"]["cmd-unassigned"]
    assert (world.fo_b.state, world.fo_free.state) == ("arrived", "arrived")
    assert not world.wo_b.diagnosed_fault_code
    assert not world.wo_b.parts_consumed_ids
    assert world.wo_a.diagnosed_fault_code == "F-OK"
    assert len(world.wo_a.parts_consumed_ids) == 1


def test_ledger_replay_of_another_technicians_command_is_refused(world):
    commands = [_start(world.fo_a, "cmd-shared-uuid")]
    with _as(world.env, world.tech_a_user):
        first = _sync(commands)
    with _as(world.env, world.tech_b_user):
        stolen = _sync(commands)
    assert "cmd-shared-uuid" in first["acknowledged"]
    assert stolen["acknowledged"] == {}
    assert "another technician" in stolen["rejected"]["cmd-shared-uuid"]


# --- SP-07 sync token ---------------------------------------------------------------


def test_sync_token_filters_deltas(world):
    env = world.env
    now = env.cr.now()
    _set_write_date(env, world.fo_a, now - timedelta(hours=2))
    _set_write_date(env, world.fo_a2, now - timedelta(minutes=10))
    with _as(env, world.tech_a_user):
        delta = _sync([], sync_token=encode_sync_token(now - timedelta(hours=1)))
        full = _sync([], sync_token="TOKEN-not-a-timestamp")
        future = _sync([], sync_token=encode_sync_token(now + timedelta(days=1)))
    assert [d["record_id"] for d in delta["deltas"]] == [world.fo_a2.id]
    assert delta["full_resync"] is False
    assert [d["record_id"] for d in full["deltas"]] == [world.fo_a.id, world.fo_a2.id]
    assert full["full_resync"] is True
    assert future["full_resync"] is True
    for res in (delta, full):
        assert world.fo_b.id not in {d["record_id"] for d in res["deltas"]}
        assert world.fo_free.id not in {d["record_id"] for d in res["deltas"]}
    assert full["deltas"][0]["customer_name"] == "Sec Customer"
    assert parse_sync_token(delta["next_token"]) == (now - SYNC_CURSOR_OVERLAP, 0)


# --- SP-09 evidence channel ---------------------------------------------------------


def _chunk(record, uuid="media-1", index=0, total=1, data=None, model="fix.field.order"):
    return {
        "media_uuid": uuid,
        "chunk_index": index,
        "total_chunks": total,
        "chunk_data": data if data is not None else base64.b64encode(b"jpeg-bytes").decode(),
        "media_type": "photo",
        "model": model,
        "record_id": record.id,
        "filename": "before.jpg",
    }


def test_evidence_requires_an_authenticated_technician(world):
    ctrl = OfflineEvidenceApiController()
    with _as(world.env, world.public_user):
        assert ctrl.upload_chunk(**_chunk(world.fo_a))["error"]["code"] == "unauthenticated"
    with _as(world.env, world.tech_a_user):
        res = ctrl.upload_chunk(**_chunk(world.fo_a), technician_id=world.tech_b.id)
        assert res["error"]["code"] == "forbidden"
    assert not world.env["ir.attachment"].search([("res_model", "=", "fix.field.order")])


def test_evidence_only_targets_records_assigned_to_the_technician(world):
    ctrl = OfflineEvidenceApiController()
    with _as(world.env, world.tech_a_user):
        foreign = ctrl.upload_chunk(**_chunk(world.fo_b))
        unassigned = ctrl.upload_chunk(**_chunk(world.fo_free))
        other_model = ctrl.upload_chunk(**_chunk(world.tech_b_user, model="res.users"))
        no_record = ctrl.upload_chunk(**dict(_chunk(world.fo_a), record_id=None))
        own = ctrl.upload_chunk(**_chunk(world.wo_a, model="fix.work.order"))
    assert foreign["error"]["code"] == "forbidden"
    assert unassigned["error"]["code"] == "forbidden"
    assert other_model["error"]["code"] == "invalid_target"
    assert no_record["error"]["code"] == "forbidden"
    assert own["complete"] is True
    attachment = world.env["ir.attachment"].browse(own["attachment_id"])
    assert (attachment.res_model, attachment.res_id) == ("fix.work.order", world.wo_a.id)


def test_evidence_upload_sessions_are_per_technician_and_validated(world):
    ctrl = OfflineEvidenceApiController()
    evidence_api._ACTIVE_CHUNKS.clear()
    try:
        with _as(world.env, world.tech_a_user):
            first = ctrl.upload_chunk(**_chunk(world.fo_a, "shared", 0, 2, "AAAA"))
            rebind = ctrl.upload_chunk(**_chunk(world.fo_a2, "shared", 1, 2, "BBBB"))
            out_of_range = ctrl.upload_chunk(**_chunk(world.fo_a, "other", 5, 2))
            too_many = ctrl.upload_chunk(**_chunk(world.fo_a, "big", 0, 10**6))
            too_large = ctrl.upload_chunk(**_chunk(world.fo_a, "fat", 0, 1, "A" * (2 << 20)))
            bad_hash = ctrl.upload_chunk(**dict(_chunk(world.fo_a, "h"), chunk_hash="0" * 64))
        with _as(world.env, world.tech_b_user):
            # tech B cannot complete (or poison) tech A's upload with the same uuid
            injected = ctrl.upload_chunk(**_chunk(world.fo_b, "shared", 1, 2, "EVIL"))
        with _as(world.env, world.tech_a_user):
            done = ctrl.upload_chunk(**_chunk(world.fo_a, "shared", 1, 2, "BBBB"))
    finally:
        evidence_api._ACTIVE_CHUNKS.clear()
    assert first["status"] == "chunk_accepted"
    assert rebind["error"]["code"] == "invalid_target"
    assert out_of_range["error"]["code"] == "invalid_chunk"
    assert too_many["error"]["code"] == "invalid_chunking"
    assert too_large["error"]["code"] == "invalid_chunk"
    assert bad_hash["error"]["code"] == "checksum_mismatch"
    assert injected["status"] == "chunk_accepted"
    assert injected["received_chunks"] == 1
    assert done["complete"] is True
    attachment = world.env["ir.attachment"].browse(done["attachment_id"])
    assert attachment.res_id == world.fo_a.id
    assert base64.b64decode(attachment.datas) == base64.b64decode("AAAABBBB")
