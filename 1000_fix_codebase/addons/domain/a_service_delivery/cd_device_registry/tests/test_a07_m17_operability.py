"""A07 M17: can a person do the registry's job on the P03 workspace?

The A07 build passed tests that called methods directly; no screen was driven.
Each test here goes through the endpoints the workspace calls (model_form,
model_write, model_action, model_records, model_lookup, model_report) as a real
NON-ADMIN user with the role they would hold. The screens are read by evaluating
static/src/a07/m17.js and a04/m09.js with node, never by grepping source text.
"""

from __future__ import annotations

import base64
import importlib.util
import json
import shutil
import subprocess
import types
from datetime import timedelta
from pathlib import Path

import odoo.addons.cd_device_registry as registry_module
import odoo.addons.cd_p03_portal as portal
import odoo.addons.cd_p03_portal.controllers.a07 as a07
import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo.addons.cd_device_registry.tests.test_a07_p1_controls import (
    AGENT,
    IMEI_A,
    IMEI_B,
    _user,
    c,  # noqa: F401 - the fixture
    dev,
    doc,
    events,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import UserError, ValidationError

PDF = base64.b64encode(b"%PDF-1.4 m17 evidence").decode()
SRC = Path(portal.__file__).parent / "static" / "src"
SATELLITES = (
    "fix.device.ownership",
    "fix.device.custody",
    "fix.device.condition",
    "fix.device.component",
    "fix.device.pm",
    "fix.device.identifier",
    "fix.device.identity",
    "fix.device.history",
    "fix.warranty",
)


@pytest.fixture(scope="module")
def js(tmp_path_factory):
    node = shutil.which("node")
    assert node, "node evaluates the registry: without it these tests prove nothing"
    tmp = tmp_path_factory.mktemp("m17js")
    (tmp / "m17.mjs").write_text((SRC / "a07" / "m17.js").read_text(encoding="utf-8"), "utf-8")
    (tmp / "m09.mjs").write_text((SRC / "a04" / "m09.js").read_text(encoding="utf-8"), "utf-8")
    (tmp / "run.mjs").write_text(
        "import * as A from './m17.mjs';\nimport * as B from './m09.mjs';\n"
        "console.log(JSON.stringify({module: A.MODULE, screens: {...B.SCREENS, ...A.SCREENS},"
        " chips: A.FORM_CHIPS}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our probe file
        [node, str(tmp / "run.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


def offered(js, screen):
    cfg = js["screens"][screen]
    tabs = {t["id"] for t in cfg.get("tabs", [])}
    out = {}
    for section in cfg["sections"]:
        if tabs:
            assert section.get("tab") in tabs, f"{screen}: a section in no tab renders invisible"
        for field in section["fields"]:
            out[field["name"]] = field
    return out


def buttons(js, screen):
    return {a["m"]: a for a in js["screens"][screen].get("actions", [])}


@pytest.fixture
def ui(c):  # noqa: F811
    cls = api.P03GenericApiController
    ctl = cls()
    old = getattr(api, "request", None)

    def call(name, user, **kw):
        api.request = types.SimpleNamespace(env=c.env(user=user.id))
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            records=lambda user, **kw: call("model_records", user, **kw),
            form=lambda user, **kw: call("model_form", user, **kw),
            write=lambda user, **kw: call("model_write", user, **kw),
            action=lambda user, **kw: call("model_action", user, **kw),
            lookup=lambda user, **kw: call("model_lookup", user, **kw),
            report=lambda user, **kw: call("model_report", user, **kw),
        )
    finally:
        api.request = old


def saved(out):
    assert "error" not in out, out
    return out["id"]


def ok(out):
    assert out.get("success"), out
    return out


def choices(ui, user, model, name):
    out = ui.form(user, model=model, fields=[{"name": name}])
    assert "error" not in out, out
    return {r["id"] for r in out["fields"][0]["choices"]}


def press(ui, user, record, method, **kwargs):
    return ui.action(user, model=record._name, ids=[record.id], method=method, kwargs=kwargs)


def warranty_vals(c, device):  # noqa: F811
    return {
        "device_id": device.id,
        "warranty_type": "manufacturer",
        "start_date": str(c.today - timedelta(days=10)),
        "end_date": str(c.today + timedelta(days=300)),
        "company_id": c.env.company.id,
        "currency_id": c.env.ref("base.BDT").id,
    }


def confirmed_grade(c, device):  # noqa: F811
    grade = (
        c.env["fix.device.condition"]
        .with_user(c.clerk)
        .create({"device_id": device.id, "grade": "b"})
    )
    grade.with_user(c.clerk2).action_confirm()
    return grade


def merged_pair(c, **dup_vals):  # noqa: F811
    survivor = dev(c, user=c.clerk)
    dup = dev(c, user=c.clerk, **dup_vals)
    identity = (
        c.env["fix.device.identity"]
        .with_user(c.clerk)
        .create(
            {
                "primary_device_id": survivor.id,
                "duplicate_device_id": dup.id,
                "match_reason": "same label",
            }
        )
    )
    return survivor, dup, identity


# ------------------------------------------------------------ 1 identifier correction
def test_1_the_quality_manager_corrects_an_identifier_from_the_form_and_button(c, ui, js):  # noqa: F811
    form = offered(js, "M17-form-asset")
    assert {"correction_field", "correction_value", "correction_reason"} <= set(form)
    assert "action_correct_identifier" in buttons(js, "M17-assets")
    d = dev(c, user=c.clerk, imei_1=IMEI_A)
    # the field itself stays locked: only the correction changes it
    assert "error" in ui.write(c.qm, model="fix.device", record_id=d.id, values={"imei_1": IMEI_B})
    saved(
        ui.write(
            c.qm,
            model="fix.device",
            record_id=d.id,
            values={"correction_field": "imei_1", "correction_value": IMEI_B},
        )
    )
    assert "reason" in press(ui, c.qm, d, "action_correct_identifier")["error"]
    d.write({"correction_reason": "board swap J-9"})
    refused = press(ui, c.agent, d, "action_correct_identifier")
    assert not refused["success"] and "Quality Manager" in refused["error"]
    assert d.imei_1 == IMEI_A
    ok(press(ui, c.qm, d, "action_correct_identifier"))
    d.invalidate_recordset()
    assert d.imei_1 == IMEI_B
    assert not (d.correction_field or d.correction_value or d.correction_reason)
    rows = c.env["fix.device.identifier"].search(
        [("device_id", "=", d.id), ("identifier_type", "=", "imei_1")]
    )
    old = rows.filtered(lambda r: r.value == IMEI_A)
    assert not old.is_current and old.supersede_reason == "board swap J-9"
    assert rows.filtered(lambda r: r.value == IMEI_B).is_current


def test_1_a_correction_needs_the_field_and_a_value(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk, imei_1=IMEI_A)
    assert "which identifier" in press(ui, c.qm, d, "action_correct_identifier")["error"].lower()
    d.write({"correction_field": "imei_1", "correction_reason": "typo"})
    assert "new value" in press(ui, c.qm, d, "action_correct_identifier")["error"].lower()
    assert d.imei_1 == IMEI_A


# ------------------------------------------------------------ 2 warranty proof
def test_2_both_warranty_forms_offer_the_proof_and_its_upload(js):
    for screen in ("M17-form-warranty", "M09-form-warranty"):
        form = offered(js, screen)
        assert form["proof_file"]["type"] == "file", screen
        assert {"proof_document_id", "proof_filename"} <= set(form), screen
        assert "readonly" not in form["proof_document_id"], screen


def test_2_request_refuses_early_with_no_proof_then_an_upload_reaches_active(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    wid = saved(ui.write(c.clerk, model="fix.warranty", values=warranty_vals(c, d)))
    w = c.env["fix.warranty"].browse(wid)
    refused = press(ui, c.clerk, w, "action_request_approval", justification="card on file")
    assert not refused["success"] and "Attach" in refused["error"]
    assert w.approval_state != "pending"
    saved(
        ui.write(
            c.clerk,
            model="fix.warranty",
            record_id=wid,
            values={"proof_file": PDF, "proof_filename": "warranty-card.pdf"},
        )
    )
    w.invalidate_recordset()
    proof = w.proof_document_id
    assert proof.document_type == "warranty_card" and proof.name == "warranty-card.pdf"
    assert (proof.res_model, proof.res_id) == ("fix.warranty", wid)
    assert base64.b64decode(proof.attachment_id.datas) == b"%PDF-1.4 m17 evidence"
    assert w.verification_blocker == "Proof is attached - ready to Verify"
    approve_via_inbox(w, c.officer, requester=c.clerk, justification="card on file")
    assert w.status == "active" and w.verified_by == c.officer


def test_2_a_verified_warranty_takes_no_new_proof(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    w = (
        c.env["fix.warranty"]
        .with_user(c.clerk)
        .create(
            {
                **warranty_vals(c, d),
                "proof_file": PDF,
                "proof_filename": "card.pdf",
            }
        )
    )
    first = w.proof_document_id
    assert first
    approve_via_inbox(w, c.officer, requester=c.clerk, justification="card on file")
    out = ui.write(
        c.clerk,
        model="fix.warranty",
        record_id=w.id,
        values={"proof_file": PDF, "proof_filename": "other.pdf"},
    )
    assert "error" in out
    w.invalidate_recordset()
    assert w.proof_document_id == first


def test_2_the_proof_picker_offers_cards_and_receipts_only(c, ui):  # noqa: F811
    card = doc(c, doc_type="warranty_card")
    receipt = doc(c, doc_type="invoice")
    deal = doc(c, doc_type="contract")
    offered_ids = choices(ui, c.clerk, "fix.warranty", "proof_document_id")
    assert {card.id, receipt.id} <= offered_ids and deal.id not in offered_ids


def test_2_a_contract_is_refused_as_proof_by_the_server(c):  # noqa: F811
    d = dev(c, user=c.clerk)
    w = (
        c.env["fix.warranty"]
        .with_user(c.clerk)
        .create({**warranty_vals(c, d), "proof_document_id": doc(c, doc_type="contract").id})
    )
    with pytest.raises(UserError, match="cannot serve as"), c.env.cr.savepoint():
        w.with_user(c.clerk).action_request_approval(justification="on file")


# ------------------------------------------------------------ 3 evidence upload
def test_3_a_transfer_is_made_with_a_file_uploaded_on_the_form(c, ui, js):  # noqa: F811
    form = offered(js, "M17-form-asset")
    assert form["transfer_evidence_file"]["type"] == "file"
    d = dev(c, user=c.clerk)
    saved(
        ui.write(
            c.agent,
            model="fix.device",
            record_id=d.id,
            values={
                "transfer_to_partner_id": c.buyer.id,
                "transfer_type_pending": "gift",
                "transfer_reason": "given to a brother",
                "transfer_evidence_file": PDF,
                "transfer_evidence_filename": "handover.pdf",
            },
        )
    )
    d.invalidate_recordset()
    staged = d.transfer_evidence_document_id
    assert staged.document_type == "asset_document" and staged.name == "handover.pdf"
    assert (staged.res_model, staged.res_id) == ("fix.device", d.id)
    ok(press(ui, c.agent, d, "action_transfer_ownership"))
    d.invalidate_recordset()
    row = c.env["fix.device.ownership"].search([("device_id", "=", d.id)])
    assert d.owner_id == c.buyer and row.evidence_document_id == staged
    assert (row.transfer_type, row.reason, row.channel) == (
        "gift",
        "given to a brother",
        "back_office",
    )


def test_3_a_release_is_made_with_a_photo_uploaded_on_the_custody_form(c, ui, js):  # noqa: F811
    assert offered(js, "M17-form-custody")["evidence_file"]["type"] == "file"
    d = dev(c, user=c.clerk)
    grade = confirmed_grade(c, d)
    vals = {
        "device_id": d.id,
        "event": "issued",
        "to_party_id": c.owner.id,
        "event_date": str(c.today),
        "condition_id": grade.id,
        "accessories_reconciled": True,
    }
    assert "photographic" in ui.write(c.clerk, model="fix.device.custody", values=vals)["error"]
    cid = saved(
        ui.write(
            c.clerk,
            model="fix.device.custody",
            values={**vals, "evidence_file": PDF, "evidence_filename": "handover.jpg"},
        )
    )
    row = c.env["fix.device.custody"].browse(cid)
    photo = row.evidence_document_id
    assert photo.document_type == "custody_photo" and photo.name == "handover.jpg"
    assert (photo.res_model, photo.res_id) == ("fix.device", d.id)
    assert base64.b64decode(photo.attachment_id.datas) == b"%PDF-1.4 m17 evidence"


def test_3_a_refused_release_leaves_no_uploaded_document_behind(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    before = c.env["fix.document"].search_count([("res_model", "=", "fix.device")])
    out = ui.write(
        c.clerk,
        model="fix.device.custody",
        values={
            "device_id": d.id,
            "event": "issued",
            "to_party_id": c.owner.id,
            "event_date": str(c.today),
            "evidence_file": PDF,
            "evidence_filename": "handover.jpg",
        },
    )
    assert "error" in out
    assert c.env["fix.document"].search_count([("res_model", "=", "fix.device")]) == before


# ------------------------------------------------------------ 4 provisional
def test_4_a_person_registers_a_provisional_device_and_confirms_it(c, ui, js):  # noqa: F811
    form = offered(js, "M17-form-asset")
    assert {"register_provisional", "provisional_reason"} <= set(form)
    assert not form["serial_number"].get("required")
    vals = {"device_model_id": c.model.id, "owner_id": c.owner.id, "register_provisional": True}
    assert "why" in ui.write(c.clerk, model="fix.device", values=vals)["error"].lower()
    did = saved(
        ui.write(
            c.clerk,
            model="fix.device",
            values={**vals, "provisional_reason": "serial label worn off"},
        )
    )
    d = c.env["fix.device"].browse(did)
    assert d.state == "provisional" and d.provisional_reason == "serial label worn off"
    assert events(c, "device.provisional_raised", d.id)
    assert any("serial label worn off" in (m.body or "") for m in d.message_ids)
    assert "Capture" in press(ui, c.agent, d, "action_confirm_identity")["error"]
    # first capture stays open on the form, and the reason is not rewritten
    saved(ui.write(c.clerk, model="fix.device", record_id=did, values={"serial_number": "PROV-1"}))
    assert "error" in ui.write(
        c.clerk, model="fix.device", record_id=did, values={"provisional_reason": "other"}
    )
    ok(press(ui, c.agent, d, "action_confirm_identity"))
    d.invalidate_recordset()
    assert d.state == "registered" and d.identity_confirmed_by_id == c.agent
    assert events(c, "device.identity_confirmed", d.id)


# ------------------------------------------------------------ 5 identifier backfill
def _backfill_migration():
    path = Path(registry_module.__file__).parent / "migrations" / "19.0.1.1.0" / "post-migrate.py"
    spec = importlib.util.spec_from_file_location("m17_backfill", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_5_the_migration_records_what_the_device_row_says_once(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk, imei_1=IMEI_A, imei_2=IMEI_B)
    bare = dev(c, serial_number=False, state="provisional", provisional_reason="unreadable")
    archived = dev(c, user=c.clerk)
    archived._guarded().write({"active": False})
    # the history as it stands live: the rows never existed for these devices
    c.env.flush_all()
    c.env.cr.execute(
        "DELETE FROM fix_device_identifier WHERE device_id = ANY(%s)", ([d.id, archived.id],)
    )
    c.env.invalidate_all()
    devices_before = c.env["fix.device"].with_context(active_test=False).search_count([])
    migration = _backfill_migration()
    migration.migrate(c.env.cr, "19.0.1.0.0")
    c.env.invalidate_all()
    Identifier = c.env["fix.device.identifier"]
    rows = Identifier.search([("device_id", "=", d.id)])
    assert {(r.identifier_type, r.value) for r in rows} == {
        ("serial_number", d.serial_number),
        ("imei_1", IMEI_A),
        ("imei_2", IMEI_B),
    }
    assert set(rows.mapped("source")) == {"backfill"} and all(rows.mapped("is_current"))
    assert not Identifier.search([("device_id", "=", bare.id)])
    assert Identifier.search_count([("device_id", "=", archived.id)]) == 1
    count = Identifier.search_count([])
    migration.migrate(c.env.cr, "19.0.1.0.0")
    c.env.invalidate_all()
    assert Identifier.search_count([]) == count
    assert c.env["fix.device"].with_context(active_test=False).search_count([]) == devices_before
    # the NEIR actions now have something to act on
    imei = rows.filtered(lambda r: r.identifier_type == "imei_1")
    ok(press(ui, c.bm, imei, "action_neir_registered", reference="BTRC-1"))
    d.invalidate_recordset()
    assert imei.neir_status == "registered" and d.neir_status == "registered"
    listed = ui.records(c.clerk, model="fix.device.identifier", cols=["value"], search=IMEI_A)[
        "rows"
    ]
    assert imei.id in {r["id"] for r in listed}


def test_5_the_migration_leaves_a_current_row_alone(c):  # noqa: F811
    d = dev(c, user=c.clerk, imei_1=IMEI_A)
    rows = c.env["fix.device.identifier"].search([("device_id", "=", d.id)])
    assert set(rows.mapped("source")) == {"registration"}
    _backfill_migration().migrate(c.env.cr, "19.0.1.0.0")
    c.env.invalidate_all()
    assert c.env["fix.device.identifier"].search([("device_id", "=", d.id)]) == rows
    assert set(rows.mapped("source")) == {"registration"}


# ------------------------------------------------------------ 6-7 reach
def test_6_owner_and_transfer_to_reach_a_party_past_the_first_300(c, ui):  # noqa: F811
    partners = c.env["res.partner"].create(
        [{"name": "M17 Far Partner %04d" % i} for i in range(310)]
    )
    for name in ("owner_id", "transfer_to_partner_id"):
        out = ui.form(c.clerk, model="fix.device", fields=[{"name": name}])
        assert out["fields"][0]["remote"] is True, name
        found = ui.lookup(c.clerk, model="fix.device", field=name, term="Far Partner 0309")
        assert [r["id"] for r in found["rows"]] == [partners[-1].id], name


def test_7_a_device_and_its_history_past_the_first_page_are_reached(c, ui, monkeypatch):  # noqa: F811
    devices = [dev(c, user=c.clerk) for _ in range(3)]
    monkeypatch.setitem(api.SURFACES["fix.device"], "limit", 2)
    first = ui.records(c.clerk, model="fix.device", cols=["name"], search="A7P1-SN")
    assert first["count"] == 2 and first["total"] >= 3
    rest = ui.records(c.clerk, model="fix.device", cols=["name"], search="A7P1-SN", offset=2)
    assert devices[0].id in {r["id"] for r in rest["rows"]}
    # Quick Find reaches an IMEI through a device picker too
    d = dev(c, user=c.clerk, imei_1=IMEI_A)
    picked = ui.lookup(c.clerk, model="fix.device.custody", field="device_id", term=IMEI_A)
    assert [r["id"] for r in picked["rows"]] == [d.id]
    for n in range(3):
        d.add_history("other", "M17 paging %d" % n)
    monkeypatch.setitem(api.SURFACES["fix.device.history"], "limit", 2)
    page1 = ui.records(c.clerk, model="fix.device.history", cols=["description"], search="paging")
    page2 = ui.records(
        c.clerk, model="fix.device.history", cols=["description"], search="paging", offset=2
    )
    assert page1["count"] == 2 and page1["total"] == 3 and page2["count"] == 1


# ------------------------------------------------------------ 8 scope
@pytest.fixture
def scope(c):  # noqa: F811
    """One device with a row on every satellite, in c.ou, plus the people who
    should and should not read it."""
    env = c.env
    other_co = env["res.company"].create({"name": "M17 Other Company"})
    outsider = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "m17_outsider",
                "login": "m17_outsider",
                "company_id": other_co.id,
                "company_ids": [(6, 0, other_co.ids)],
                "group_ids": [(6, 0, env.ref("base.group_user").ids)],
            }
        )
    )
    d = dev(c, user=c.clerk, imei_1=IMEI_A)
    assert d.operating_unit_id == c.ou
    twin = dev(c, user=c.clerk)
    d.add_history("other", "M17 scope history")
    rows = {
        "fix.device.condition": confirmed_grade(c, d),
        "fix.device.custody": env["fix.device.custody"]
        .with_user(c.clerk)
        .create({"device_id": d.id, "event": "returned"}),
        "fix.device.component": env["fix.device.component"]
        .with_user(c.clerk)
        .create({"device_id": d.id, "part_name": "Panel"}),
        "fix.device.pm": env["fix.device.pm"]
        .with_user(c.clerk)
        .create({"device_id": d.id, "next_due": c.today + timedelta(days=40)}),
        "fix.device.identity": env["fix.device.identity"]
        .with_user(c.clerk)
        .create({"primary_device_id": d.id, "duplicate_device_id": twin.id, "match_reason": "x"}),
        "fix.device.identifier": env["fix.device.identifier"].search([("device_id", "=", d.id)]),
        "fix.device.history": env["fix.device.history"].search([("device_id", "=", d.id)]),
        "fix.warranty": env["fix.warranty"].with_user(c.clerk).create(warranty_vals(c, d)),
    }
    d.with_user(c.agent).action_transfer_ownership(
        c.buyer.id, reason="sold", evidence_document_id=doc(c, doc_type="invoice").id
    )
    rows["fix.device.ownership"] = env["fix.device.ownership"].search([("device_id", "=", d.id)])
    rows["fix.device"] = d
    assert all(rows[m] for m in (*SATELLITES, "fix.device"))
    return types.SimpleNamespace(rows=rows, device=d, outsider=outsider)


def _listed(ui, user, record):
    out = ui.records(user, model=record._name, cols=["id"], domain=[("id", "in", record.ids)])
    assert "error" not in out, out
    return {r["id"] for r in out["rows"]}


def test_8_another_company_lists_nothing_of_a_devices_records(c, ui, scope):  # noqa: F811
    for model, record in scope.rows.items():
        assert not _listed(ui, scope.outsider, record), model


def test_8_another_unit_lists_nothing_of_a_devices_records(c, ui, scope):  # noqa: F811
    for model, record in scope.rows.items():
        assert not _listed(ui, c.clerk_b, record), model


def test_8_a_same_unit_user_lists_all_of_it(c, ui, scope):  # noqa: F811
    for model, record in scope.rows.items():
        assert _listed(ui, c.clerk2, record) == set(record.ids), model


def test_8_a_record_of_another_unit_does_not_open_by_id(c, ui, scope):  # noqa: F811
    d = scope.device
    fields_ = [{"name": "imei_1"}, {"name": "owner_id"}]
    out = ui.form(c.clerk_b, model="fix.device", fields=fields_, record_id=d.id)
    assert "error" in out and not out.get("record")
    row = scope.rows["fix.device.ownership"]
    out = ui.form(
        c.clerk_b,
        model="fix.device.ownership",
        fields=[{"name": "to_partner_id"}],
        record_id=row.id,
    )
    assert "error" in out and not out.get("record")
    assert ui.form(c.clerk2, model="fix.device", fields=fields_, record_id=d.id)["record"]


def test_8_reports_and_kpis_follow_the_same_scope(c, ui, scope):  # noqa: F811
    d = scope.device
    for user, seen in ((scope.outsider, False), (c.clerk_b, False), (c.clerk2, True)):
        out = ui.report(user, module="M17", report="identifiers", params={})
        assert (IMEI_A in {r["imei_1"] for r in out["rows"]}) is seen
    assert a07.kpis(c.env(user=c.clerk2.id), "M17")["M17"]["devices_active"] >= 1
    assert d.id  # the scoped device still exists after the outsiders' reads


# ------------------------------------------------------------ 10 evidence is what it says
def test_10_an_employment_contract_is_not_offered_or_accepted_as_transfer_evidence(c, ui, js):  # noqa: F811
    contract = doc(c, doc_type="contract")
    deed = doc(c, doc_type="asset_document")
    receipt = doc(c, doc_type="invoice")
    offered_ids = choices(ui, c.agent, "fix.device", "transfer_evidence_document_id")
    assert {deed.id, receipt.id} <= offered_ids and contract.id not in offered_ids
    d = dev(c, user=c.clerk)
    refused = d.with_user(c.agent)
    with pytest.raises(UserError, match="cannot serve as"), c.env.cr.savepoint():
        refused.action_transfer_ownership(
            c.buyer.id, reason="sold", evidence_document_id=contract.id
        )
    assert d.owner_id == c.owner
    # no text claims an acceptance the system does not record
    note = " ".join(s.get("note", "") for s in js["screens"]["M17-form-asset"]["sections"]).lower()
    assert "accepted" not in note
    assert "accepted" not in (c.env["fix.device"]._fields["transfer_evidence_document_id"].help)


def test_10_custody_evidence_is_a_photograph_or_evidence_pack(c, ui):  # noqa: F811
    photo = doc(c, doc_type="custody_photo")
    deal = doc(c, doc_type="contract")
    offered_ids = choices(ui, c.clerk, "fix.device.custody", "evidence_document_id")
    assert photo.id in offered_ids and deal.id not in offered_ids
    d = dev(c, user=c.clerk)
    grade = confirmed_grade(c, d)
    out = ui.write(
        c.clerk,
        model="fix.device.custody",
        values={
            "device_id": d.id,
            "event": "issued",
            "to_party_id": c.owner.id,
            "event_date": str(c.today),
            "condition_id": grade.id,
            "evidence_document_id": deal.id,
            "accessories_reconciled": True,
        },
    )
    assert "cannot serve as" in out["error"]


# ------------------------------------------------------------ 12 lost agrees with the state
def _open_lost(c, user):  # noqa: F811
    return a07.kpis(c.env(user=user.id), "M17")["M17"]["custody_open_lost"]


def _exceptions(ui, user, device):
    out = ui.report(user, module="M17", report="custody_exceptions", params={})
    assert "error" not in out, out
    return [r for r in out["rows"] if r["device"] == device.name]


def test_12_the_kpi_the_report_and_the_chain_follow_a_registry_flag(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    base = _open_lost(c, c.clerk)
    ok(press(ui, c.clerk, d, "action_mark_lost", reason="Owner reported theft GD-1"))
    chain = c.env["fix.device.custody"].search([("device_id", "=", d.id)])
    assert chain.mapped("event") == ["lost"] and "GD-1" in chain.notes
    assert _open_lost(c, c.clerk) == base + 1
    rows = _exceptions(ui, c.clerk, d)
    assert len(rows) == 1 and rows[0]["note"] == "open: flagged lost"
    ok(press(ui, c.bm, d, "action_clear_lost", reason="found at the police station"))
    assert _open_lost(c, c.clerk) == base
    chain = c.env["fix.device.custody"].search([("device_id", "=", d.id)], order="id")
    assert chain.mapped("event") == ["lost", "found"]
    assert "police station" in chain[1].notes
    rows = {r["event"]: r["note"] for r in _exceptions(ui, c.clerk, d)}
    assert rows["Reported Lost"] == "flag cleared" and rows["Recovered"] == "flag cleared"


def test_12_a_found_event_with_the_flag_still_on_stays_open(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    base = _open_lost(c, c.clerk)
    Custody = c.env["fix.device.custody"].with_user(c.clerk)
    Custody.create({"device_id": d.id, "event": "lost", "notes": "reported"})
    Custody.create({"device_id": d.id, "event": "found", "notes": "brought in"})
    assert d.state == "lost" and _open_lost(c, c.clerk) == base + 1
    notes = {r["event"]: r["note"] for r in _exceptions(ui, c.clerk, d)}
    assert notes["Recovered"] == "recovered: flag not yet cleared"


def test_12_a_device_flagged_before_the_chain_was_written_still_shows(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    d.action_mark_lost(reason="old flag")
    c.env.flush_all()
    c.env.cr.execute("DELETE FROM fix_device_custody WHERE device_id = %s", (d.id,))
    c.env.invalidate_all()
    rows = _exceptions(ui, c.clerk, d)
    assert len(rows) == 1 and rows[0]["note"] == "open: flagged lost"


def test_12_a_lost_flag_keeps_the_custodian_for_the_ownership_check(c):  # noqa: F811
    d = dev(c, user=c.clerk)
    emp = c.env["hr.employee"].create({"name": "M17 Custodian", "user_id": c.agent.id})
    c.env["fix.device.custody"].with_user(c.clerk).create(
        {"device_id": d.id, "event": "returned", "custodian_id": emp.id}
    )
    d.with_user(c.clerk).action_mark_lost(reason="reported")
    d.with_user(c.bm).action_clear_lost(reason="withdrawn")
    with pytest.raises(UserError, match="Segregation of duties"), c.env.cr.savepoint():
        d.with_user(c.agent).action_transfer_ownership(
            c.buyer.id, reason="sold", evidence_document_id=doc(c, doc_type="invoice").id
        )


# ------------------------------------------------------------ 13 dispositions
def test_13_every_disposition_has_a_button(c, ui, js):  # noqa: F811
    screen = buttons(js, "M17-components")
    Component = c.env["fix.device.component"].with_user(c.clerk)
    d = dev(c, user=c.clerk)
    for method, expected in (
        ("action_dispose_harvested", "harvested"),
        ("action_dispose_returned_to_brand", "returned_to_brand"),
        ("action_dispose_returned", "returned_to_customer"),
        ("action_dispose_scrapped", "scrapped"),
    ):
        assert method in screen, method
        part = Component.create({"device_id": d.id, "part_name": "Part %s" % method})
        ok(press(ui, c.clerk, part, "action_remove"))
        ok(press(ui, c.clerk, part, method))
        part.invalidate_recordset()
        assert part.disposition == expected
        # recorded once
        assert not press(ui, c.clerk, part, method)["success"]
    part = Component.create({"device_id": d.id, "part_name": "Direct"})
    ok(press(ui, c.clerk, part, "action_remove"))
    assert not press(ui, c.clerk, part, "action_record_disposition", disposition="eaten")["success"]
    ok(press(ui, c.clerk, part, "action_record_disposition", disposition="harvested"))


# ------------------------------------------------------------ 15, 17 what the screens say
def test_15_the_ownership_transfer_chip_points_at_the_asset_register(js):
    target = js["chips"]["M17:Ownership Transfer"]
    cfg = js["screens"][target]
    assert cfg["back"] == "M17-assets"
    # it offers no field to fill: there is nothing here that a save could record
    assert not [f for s in cfg["sections"] for f in s["fields"] if not f.get("readonly")]
    assert "Asset Register" in " ".join(s.get("note", "") for s in cfg["sections"])


def test_15_a_save_on_it_says_where_a_transfer_is_made(c, ui):  # noqa: F811
    out = ui.write(c.agent, model="fix.device.ownership", values={})
    assert "Asset Register" in out["error"]


def test_17_the_warranty_screen_offers_what_its_note_describes(js):
    screen = buttons(js, "M17-wty")
    assert {"action_request_approval", "action_recall_approval"} <= set(screen)
    assert screen["action_request_approval"]["kwarg"] == "justification"
    note = " ".join(s.get("note", "") for s in js["screens"]["M17-form-warranty"]["sections"])
    assert "Request Verification" in note


# ------------------------------------------------------------ 19 the due date
def test_19_next_due_moves_only_by_a_reasoned_reschedule(c, ui, js):  # noqa: F811
    assert "action_reschedule" in buttons(js, "M17-pm")
    d = dev(c, user=c.clerk)
    start = c.today + timedelta(days=5)
    pid = saved(
        ui.write(
            c.clerk,
            model="fix.device.pm",
            values={"device_id": d.id, "plan_type": "annual", "next_due": str(start)},
        )
    )
    plan = c.env["fix.device.pm"].browse(pid)
    later = c.today + timedelta(days=400)
    out = ui.write(c.clerk, model="fix.device.pm", record_id=pid, values={"next_due": str(later)})
    assert "error" in out and plan.next_due == start
    with pytest.raises(UserError, match="Reschedule"), c.env.cr.savepoint():
        plan.with_user(c.clerk).write({"next_due": later})
    # an echo of the same date with another edit still saves
    saved(
        ui.write(
            c.clerk,
            model="fix.device.pm",
            record_id=pid,
            values={"next_due": str(start), "notes": "keep"},
        )
    )
    refused = press(ui, c.clerk, plan, "action_reschedule", next_due=str(later), reason="x")
    assert not refused["success"] and "Branch Manager" in refused["error"]
    assert "reason" in press(ui, c.bm, plan, "action_reschedule", next_due=str(later))["error"]
    past = str(c.today - timedelta(days=2))
    assert "past" in press(ui, c.bm, plan, "action_reschedule", next_due=past, reason="x")["error"]
    assert not press(ui, c.bm, plan, "action_reschedule", next_due="soon", reason="x")["success"]
    ok(press(ui, c.bm, plan, "action_reschedule", next_due=str(later), reason="Customer abroad"))
    plan.invalidate_recordset()
    assert plan.next_due == later
    assert any("Customer abroad" in (m.body or "") for m in d.message_ids)


# ------------------------------------------------------------ 20 identifiers
def test_20_a_registration_with_no_identifier_is_refused(c, ui):  # noqa: F811
    vals = {"device_model_id": c.model.id, "owner_id": c.owner.id}
    out = ui.write(c.clerk, model="fix.device", values=vals)
    assert "serial" in out["error"].lower() and "provisional" in out["error"].lower()
    with pytest.raises(UserError, match="provisional"), c.env.cr.savepoint():
        c.env["fix.device"].with_user(c.clerk).create(vals)
    # an IMEI alone is an identifier
    saved(ui.write(c.clerk, model="fix.device", values={**vals, "imei_1": IMEI_A}))


# ------------------------------------------------------------ 21 plan type
def test_21_changing_the_plan_type_with_the_old_interval_echoed_saves(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    pid = saved(
        ui.write(
            c.clerk,
            model="fix.device.pm",
            values={
                "device_id": d.id,
                "plan_type": "annual",
                "next_due": str(c.today + timedelta(days=5)),
            },
        )
    )
    plan = c.env["fix.device.pm"].browse(pid)
    assert plan.interval_months == 12
    saved(
        ui.write(
            c.clerk,
            model="fix.device.pm",
            record_id=pid,
            values={"plan_type": "quarterly", "interval_months": 12},
        )
    )
    plan.invalidate_recordset()
    assert (plan.plan_type, plan.interval_months) == ("quarterly", 3)
    # another interval on a fixed type is refused, and says what to choose
    out = ui.write(
        c.clerk,
        model="fix.device.pm",
        record_id=pid,
        values={"plan_type": "quarterly", "interval_months": 5},
    )
    assert "Custom interval" in out["error"]
    saved(
        ui.write(
            c.clerk,
            model="fix.device.pm",
            record_id=pid,
            values={"plan_type": "custom", "interval_months": 5},
        )
    )
    plan.invalidate_recordset()
    assert (plan.plan_type, plan.interval_months) == ("custom", 5)
    # both changed and disagreeing is still refused
    out = ui.write(
        c.clerk,
        model="fix.device.pm",
        record_id=pid,
        values={"plan_type": "annual", "interval_months": 7},
    )
    assert "every 12 months" in out["error"]


def test_21_a_new_plan_with_a_blank_interval_takes_its_types(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    pid = saved(
        ui.write(
            c.clerk,
            model="fix.device.pm",
            values={
                "device_id": d.id,
                "plan_type": "biannual",
                "interval_months": 0,
                "next_due": str(c.today + timedelta(days=5)),
            },
        )
    )
    assert c.env["fix.device.pm"].browse(pid).interval_months == 6


# ------------------------------------------------------------ 22 lifecycle
def test_22_a_vintage_device_returns_to_active(c, ui, js):  # noqa: F811
    assert "action_return_to_active" in buttons(js, "M17-assets")
    form = offered(js, "M17-form-asset")
    assert form["end_of_support_date"]["readonly"] and form["lost_cleared_by_id"]["readonly"]
    d = dev(c, user=c.clerk)
    assert "vintage" in press(ui, c.bm, d, "action_return_to_active", reason="x")["error"]
    ok(press(ui, c.bm, d, "action_set_vintage", reason="parts ageing"))
    assert not press(ui, c.clerk, d, "action_return_to_active", reason="x")["success"]
    assert "basis" in press(ui, c.bm, d, "action_return_to_active", reason=" ")["error"]
    ok(press(ui, c.bm, d, "action_return_to_active", reason="OEM resumed parts"))
    d.invalidate_recordset()
    assert d.lifecycle_stage == "active" and d.lifecycle_reason == "OEM resumed parts"


# ------------------------------------------------------------ 23-24 labels
def test_23_the_labels_say_what_the_system_does(c, ui, js):  # noqa: F811
    desc = js["module"]["desc"]
    assert "six identifiers" not in desc and "five identifiers" in desc
    form = js["screens"]["M17-form-asset"]
    states = set(dict(c.env["fix.device"]._fields["state"].selection))
    assert set(form["status"]["labels"]) == states
    # nothing in the code sets these; offering them promised a lifecycle that does not run
    assert not {"in_service", "repaired", "returned"} & states
    dev(c, user=c.clerk)
    out = ui.report(c.clerk, module="M17", report="asset_360", params={})
    assert "newest last" not in " ".join(out["notes"])
    names = [r["device"] for r in out["rows"]]
    assert names == sorted(names, reverse=True)
    assert "sorted by device name" in " ".join(out["notes"]).lower()


# ------------------------------------------------------------ logic bugs
def test_a_later_intake_of_a_merged_identifier_names_the_survivor(c, ui):  # noqa: F811
    survivor, dup, identity = merged_pair(c, imei_1=IMEI_A)
    approve_via_inbox(identity, c.qm, requester=c.clerk)
    assert not dup.active
    for vals in (
        {"serial_number": dup.serial_number},
        {"serial_number": " %s " % dup.serial_number.lower()},
        {"serial_number": "M17-NEW-1", "imei_1": IMEI_A},
        {"serial_number": "M17-NEW-2", "imei_2": IMEI_A},
    ):
        out = ui.write(
            c.clerk,
            model="fix.device",
            values={"device_model_id": c.model.id, "owner_id": c.owner.id, **vals},
        )
        assert survivor.display_name in out["error"], vals
    # the intake lookup resolves it to the survivor
    Device = c.env["fix.device"].with_user(c.clerk)
    assert Device.resolve_identifier(dup.serial_number) == survivor
    assert Device.resolve_identifier(" %s " % dup.serial_number.lower()) == survivor
    assert Device.resolve_identifier(IMEI_A) == survivor
    assert Device.resolve_identifier(survivor.serial_number) == survivor
    assert not Device.resolve_identifier("NO-SUCH-SERIAL")
    assert not Device.resolve_identifier("  ")


def test_resolve_identifier_follows_a_chain_and_stops_at_a_reversal(c):  # noqa: F811
    middle, first, identity = merged_pair(c)
    approve_via_inbox(identity, c.qm, requester=c.clerk)
    last, middle_again, identity2 = None, middle, None
    last = dev(c, user=c.clerk)
    identity2 = (
        c.env["fix.device.identity"]
        .with_user(c.clerk)
        .create(
            {
                "primary_device_id": last.id,
                "duplicate_device_id": middle_again.id,
                "match_reason": "same again",
            }
        )
    )
    approve_via_inbox(identity2, c.qm, requester=c.clerk)
    Device = c.env["fix.device"].with_user(c.clerk)
    assert Device.resolve_identifier(first.serial_number) == last
    identity2.merge_id.with_user(c.qm).action_reverse(reason="not the same")
    assert Device.resolve_identifier(first.serial_number) == middle


def test_a_merge_moves_the_duplicates_documents_and_a_reversal_moves_them_back(c):  # noqa: F811
    survivor, dup, identity = merged_pair(c)
    filed = doc(c, "fix.device", dup.id, "asset_document")
    kept = doc(c, "fix.device", survivor.id, "asset_document")
    approve_via_inbox(identity, c.qm, requester=c.clerk)
    filed.invalidate_recordset()
    assert filed.res_id == survivor.id
    survivor.invalidate_recordset()
    assert {filed, kept} <= set(survivor.document_ids)
    lineage = identity.merge_id
    assert filed.id in json.loads(lineage.reference_map)["fix.document"]["res_id"]
    lineage.with_user(c.qm).action_reverse(reason="not the same device")
    filed.invalidate_recordset()
    assert filed.res_id == dup.id and kept.res_id == survivor.id


def test_evidence_is_not_reused_for_a_second_transfer(c):  # noqa: F811
    d = dev(c, user=c.clerk)
    proof = doc(c, doc_type="invoice")
    d.with_user(c.agent).action_transfer_ownership(
        c.buyer.id, reason="sold", evidence_document_id=proof.id
    )
    with pytest.raises(UserError, match="already"), c.env.cr.savepoint():
        d.with_user(c.agent).action_transfer_ownership(
            c.owner.id, reason="sold back", evidence_document_id=proof.id
        )
    assert d.owner_id == c.buyer


def test_a_release_photo_is_not_reused_for_a_second_release(c):  # noqa: F811
    d = dev(c, user=c.clerk)
    grade = confirmed_grade(c, d)
    Custody = c.env["fix.device.custody"].with_user(c.clerk)
    for photo, refusal in (
        # filed on the device, as an upload on the form is
        (doc(c, "fix.device", d.id, "custody_photo"), "already"),
        # unfiled: the first release files it on that event
        (doc(c, doc_type="custody_photo"), "another record"),
    ):
        vals = {
            "device_id": d.id,
            "event": "issued",
            "to_party_id": c.owner.id,
            "condition_id": grade.id,
            "evidence_document_id": photo.id,
            "accessories_reconciled": True,
        }
        Custody.create(vals)
        with pytest.raises(UserError, match=refusal), c.env.cr.savepoint():
            Custody.create(vals)


def test_scrap_needs_the_customers_instruction(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    refused = press(ui, c.clerk, d, "action_request_approval", justification="beyond repair")
    assert not refused["success"] and "instruction" in refused["error"]
    assert d.approval_state != "pending"
    saved(
        ui.write(
            c.clerk,
            model="fix.device",
            record_id=d.id,
            values={"eol_customer_instruction": "recycle"},
        )
    )
    approve_via_inbox(d, c.qm, requester=c.clerk, justification="beyond repair")
    assert d.state == "scrapped"


def test_scrap_is_refused_at_the_decision_when_the_instruction_was_withdrawn(c):  # noqa: F811
    d = dev(c, user=c.clerk, eol_customer_instruction="recycle")
    d.with_user(c.clerk).action_request_approval(justification="beyond repair")
    d.with_user(c.clerk).write({"eol_customer_instruction": False})
    with pytest.raises((UserError, ValidationError), match="instruction"), c.env.cr.savepoint():
        approve_via_inbox(d, c.qm, requester=c.clerk)
    assert d.state != "scrapped"


def test_a_device_with_no_owner_scraps_without_an_instruction(c):  # noqa: F811
    d = dev(c, user=c.clerk, owner_id=False)
    approve_via_inbox(d, c.qm, requester=c.clerk, justification="found in the store, no owner")
    assert d.state == "scrapped"


def test_data_quality_does_not_mark_an_individual_down_for_having_no_estate(c, ui):  # noqa: F811
    person = dev(c, user=c.clerk)
    firm = c.env["res.partner"].create({"name": "M17 Firm Ltd", "is_company": True})
    staff = c.env["res.partner"].create({"name": "M17 Staffer", "parent_id": firm.id})
    corporate = dev(c, user=c.clerk, owner_id=staff.id)
    out = ui.report(c.clerk, module="M17", report="data_quality", params={})
    rows = {r["device"]: r for r in out["rows"]}
    assert "no estate" not in rows[person.name]["problems"]
    assert "no estate" in rows[corporate.name]["problems"]
    assert rows[person.name]["score_pct"] == rows[corporate.name]["score_pct"] + 20


def test_a_blank_transfer_type_is_refused_on_the_form_path(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    saved(
        ui.write(
            c.agent,
            model="fix.device",
            record_id=d.id,
            values={
                "transfer_to_partner_id": c.buyer.id,
                "transfer_reason": "sold",
                "transfer_evidence_document_id": doc(c, doc_type="invoice").id,
            },
        )
    )
    out = press(ui, c.agent, d, "action_transfer_ownership")
    assert not out["success"] and "Transfer Type" in out["error"]
    assert d.owner_id == c.owner


def test_the_agent_role_is_what_the_transfer_button_says(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    clerk = _user(c.env, "m17_plain", c.ou)
    assert not clerk.has_group(AGENT)
    out = press(ui, clerk, d, "action_transfer_ownership", new_owner_id=c.buyer.id, reason="x")
    assert not out["success"] and "Registry Agent" in out["error"]
