"""M17 capture audit (2026-11-13): the captures the sub-module pages lacked,
driven through the endpoints the workspace calls, as NON-ADMIN users.

- Bulk Registration (FR-AST-039, BRU-AST-18, T-10): an estate file is
  validated row by row through the rules a single registration meets, the
  rejects are reported line by line, and the commit registers every row or none.
- Ownership & Custody: the transfer form runs the governed transfer with an
  uploaded evidence file; the lost/stolen form raises the flag.
- Corporate Estates: a device is placed in an estate its client owns.
"""

from __future__ import annotations

import base64
import io

import openpyxl
import pytest
from odoo.addons.cd_device_registry.tests.test_a07_m17_operability import (
    PDF,
    js,  # noqa: F401 - the fixture
    ok,
    saved,
    ui,  # noqa: F401 - the fixture
)
from odoo.addons.cd_device_registry.tests.test_a07_p1_controls import (
    IMEI_A,
    IMEI_B,
    c,  # noqa: F401 - the fixture
    dev,
    events,
)
from odoo.exceptions import UserError


@pytest.fixture
def estate(c):  # noqa: F811
    c.client = c.env["res.partner"].create({"name": "M17CAP Client Ltd", "is_company": True})
    c.bulk_model = c.env["fix.device.model"].create(
        {"name": "M17CAP Laptop", "model_code": "M17CAP-L1", "brand_id": c.model.brand_id.id}
    )
    return c.env["fix.device.estate"].create({"name": "M17CAP HQ", "client_id": c.client.id})


def _csv(*rows):
    text = "\n".join(",".join(r) for r in rows) + "\n"
    return base64.b64encode(text.encode()).decode()


def _upload(ui, user, estate, data, name="estate.csv"):  # noqa: F811
    return ui.write(
        user,
        model="fix.device.bulk.load",
        values={"estate_id": estate.id, "upload_file": data, "upload_filename": name},
    )


def _load(c, load_id):  # noqa: F811
    load = c.env["fix.device.bulk.load"].browse(load_id)
    load.invalidate_recordset()
    return load


def _by_row(load):
    return {ln.row_no: ln for ln in load.line_ids}


# ------------------------------------------------------------ bulk registration
def test_an_uploaded_file_is_validated_and_rejects_are_reported_per_line(c, ui, estate):  # noqa: F811
    other = dev(c, user=c.clerk)  # registered to someone who is not the client
    before = len(events(c, "device.registered"))
    data = _csv(
        ("Model", "Serial Number", "IMEI 1"),
        ("M17CAP-L1", "M17CAP-SN-1", ""),  # 2 good
        ("No Such Model", "M17CAP-SN-2", ""),  # 3 not in the catalogue
        ("M17CAP Laptop", "m17cap-sn-1 ", ""),  # 4 same serial as row 2 (normalised)
        ("M17CAP-L1", other.serial_number, ""),  # 5 another owner's device
        ("M17CAP-L1", "", "12345"),  # 6 the registration's own IMEI rule
        ("M17CAP-L1", "", ""),  # 7 no identifier
    )
    load = _load(c, saved(_upload(ui, c.clerk, estate, data)))
    rows = _by_row(load)
    assert load.state == "rejected"
    assert rows[2].status == "new" and rows[2].device_model_id == c.bulk_model
    assert rows[3].status == "error" and "catalogue" in rows[3].message
    assert rows[4].status == "error" and "row 2" in rows[4].message
    assert rows[5].status == "error" and "ownership transfer" in rows[5].message
    assert rows[6].status == "error" and "IMEI" in rows[6].message
    assert rows[7].status == "error"
    # the validation registered nothing and announced nothing
    assert not c.env["fix.device"].search([("serial_number", "=", "M17CAP-SN-1")])
    assert len(events(c, "device.registered")) == before
    # a rejected file is not committed
    refused = ui.action(
        c.agent, model="fix.device.bulk.load", ids=[load.id], method="action_commit", kwargs={}
    )
    assert not refused["success"] and "not validated clean" in refused["error"]


def test_a_clean_file_commits_as_a_set_by_a_registry_agent(c, ui, estate):  # noqa: F811
    owned = dev(c, user=c.clerk, owner_id=c.client.id)  # the client's, not yet placed
    data = _csv(
        ("Serial", "IMEI", "Model", "Purchase Date"),
        ("M17CAP-SN-10", IMEI_A, "M17CAP-L1", "2026-01-15"),
        ("M17CAP-SN-11", "", "m17cap laptop", ""),
        (owned.serial_number, "", "M17CAP-L1", ""),
    )
    load = _load(c, saved(_upload(ui, c.clerk, estate, data)))
    assert load.state == "validated", [(ln.row_no, ln.message) for ln in load.line_ids]
    assert (load.new_count, load.place_count, load.error_count) == (2, 1, 0)
    # the commit needs the Device Registry Agent role
    refused = ui.action(
        c.clerk, model="fix.device.bulk.load", ids=[load.id], method="action_commit", kwargs={}
    )
    assert not refused["success"] and "role" in refused["error"]
    ok(
        ui.action(
            c.agent, model="fix.device.bulk.load", ids=[load.id], method="action_commit", kwargs={}
        )
    )
    load = _load(c, load.id)
    assert load.state == "committed" and load.committed_by_id == c.agent
    new = c.env["fix.device"].search([("serial_number", "in", ["M17CAP-SN-10", "M17CAP-SN-11"])])
    assert len(new) == 2
    assert set(new.mapped("owner_id")) == {c.client}
    assert set(new.mapped("estate_id")) == {estate}
    assert new.filtered(lambda d: d.imei_1 == IMEI_A).purchase_date.isoformat() == "2026-01-15"
    owned.invalidate_recordset()
    assert owned.estate_id == estate
    assert set(load.line_ids.mapped("status")) == {"done", "placed"}
    # a committed registration is a record
    assert "error" in ui.write(
        c.clerk, model="fix.device.bulk.load", record_id=load.id, values={"notes": "edited"}
    )


def test_the_commit_registers_every_row_or_none(c, ui, estate):  # noqa: F811
    data = _csv(
        ("Model", "Serial Number"),
        ("M17CAP-L1", "M17CAP-SN-20"),
        ("M17CAP-L1", "M17CAP-SN-21"),
    )
    load = _load(c, saved(_upload(ui, c.clerk, estate, data)))
    assert load.state == "validated"
    # row 3's serial is registered elsewhere between validation and commit
    dev(c, serial_number="M17CAP-SN-21")
    with pytest.raises(UserError, match="Row 3"):
        load.with_user(c.agent).action_commit()
    assert not c.env["fix.device"].search([("serial_number", "=", "M17CAP-SN-20")])


def test_an_excel_file_keeps_imeis_whole(c, ui, estate):  # noqa: F811
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.append(["Model Code", "IMEI 1", "IMEI 2"])
    sheet.append(["M17CAP-L1", int(IMEI_A), int(IMEI_B)])  # Excel stores them as numbers
    buf = io.BytesIO()
    book.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    load = _load(c, saved(_upload(ui, c.clerk, estate, data, "estate.xlsx")))
    line = load.line_ids
    assert (line.imei_1, line.imei_2) == (IMEI_A, IMEI_B)
    assert load.state == "validated", line.message


def test_a_file_without_a_model_column_is_refused_at_upload(c, ui, estate):  # noqa: F811
    out = _upload(ui, c.clerk, estate, _csv(("Serial",), ("X-1",)))
    assert "error" in out and "Model column" in out["error"]


def test_replacing_the_file_validates_it_again(c, ui, estate):  # noqa: F811
    load_id = saved(
        _upload(ui, c.clerk, estate, _csv(("Model", "Serial"), ("Nope", "M17CAP-SN-30")))
    )
    assert _load(c, load_id).state == "rejected"
    saved(
        ui.write(
            c.clerk,
            model="fix.device.bulk.load",
            record_id=load_id,
            values={"upload_file": _csv(("Model", "Serial"), ("M17CAP-L1", "M17CAP-SN-30"))},
        )
    )
    load = _load(c, load_id)
    assert load.state == "validated" and len(load.line_ids) == 1


def test_the_state_is_never_typed(c, ui, estate):  # noqa: F811
    load_id = saved(
        _upload(ui, c.clerk, estate, _csv(("Model", "Serial"), ("Nope", "M17CAP-SN-40")))
    )
    with pytest.raises(UserError):
        c.env["fix.device.bulk.load"].with_user(c.clerk).browse(load_id).write(
            {"state": "validated"}
        )


# ------------------------------------------------------------ ownership & custody
def test_the_transfer_form_uploads_its_evidence_and_transfers(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    # the kwargs the M17-form-transfer-record saveAction sends
    ok(
        ui.action(
            c.agent,
            model="fix.device",
            ids=[d.id],
            method="action_transfer_ownership",
            kwargs={
                "new_owner_id": c.buyer.id,
                "transfer_type": "sale",
                "reason": "sold at the branch",
                "evidence_file": PDF,
                "evidence_filename": "receipt.pdf",
            },
        )
    )
    d.invalidate_recordset()
    assert d.owner_id == c.buyer
    row = c.env["fix.device.ownership"].search([("device_id", "=", d.id)])
    assert row.evidence_document_id and row.reason == "sold at the branch"
    assert row.evidence_document_id.res_model == "fix.device"


def test_the_lost_form_raises_the_flag(c, ui):  # noqa: F811
    d = dev(c, user=c.clerk)
    ok(
        ui.action(
            c.clerk,
            model="fix.device",
            ids=[d.id],
            method="action_mark_lost",
            kwargs={"reason": "customer reported theft, GD 123"},
        )
    )
    d.invalidate_recordset()
    assert d.state == "lost" and d.lost_flagged_by_id == c.clerk


# ------------------------------------------------------------ corporate estates
def test_a_device_is_placed_only_in_its_owners_estate(c, ui, estate):  # noqa: F811
    mine = dev(c, user=c.clerk, owner_id=c.client.id)
    theirs = dev(c, user=c.clerk)
    # the placement form posts the read-only echoes it shows plus the estate
    saved(
        ui.write(
            c.clerk,
            model="fix.device",
            record_id=mine.id,
            values={"name": mine.name, "owner_id": c.client.id, "estate_id": estate.id},
        )
    )
    mine.invalidate_recordset()
    assert mine.estate_id == estate
    out = ui.write(
        c.clerk, model="fix.device", record_id=theirs.id, values={"estate_id": estate.id}
    )
    assert "error" in out
