# M06 Data Services & Recovery: every Function Register sub-module page
# captures what its function records.
#
# Reported 2026-11-13: "not all the sub-modules have a relevant data capture
# button". Measured over the real registry and the page rule: pages 6
# (Recovered-Data Inventory), 7 (Secure Handover & Purge) and 10 (Access
# Control & Audit) offered nothing; page 3 (Evaluation & Quotation) offered
# only a firm quotation, which the server refuses until a free evaluation is
# completed - and no page offered the evaluation; page 5 (Attempt Tracking)
# repeated page 4's button. The inventory fields page 6 lists were written by
# nothing at all, and the handover needed a receipt the workspace could not
# upload. fix_real held 0 records in every M06 table.
#
# The page rule is JavaScript (p03_workspace.js fregCreate), so it is
# EXECUTED in node over the real registry; the saves run through the same
# endpoints the forms use, as non-admin users holding only the M06 roles.
from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_data_case.tests.test_a02_p1p2_cd_data_case import (  # noqa: F401
    _cert,
    m6,
)
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import UserError

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
FREG_CREATE = re.compile(r"^    (fregCreate\(mid, map\) \{\n.*?\n    \})\n", re.S | re.M)
CASE = "fix.data.recovery.case"
GUARD = "changes only through its workflow"

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %s
const subs = P03_MODULES.M06.freg.sub.map((s) => ({ no: s[0], title: s[1], map: s[3] || null,
  create: fregCreate('M06', s[3] || null) }));
const forms = {};
for (const [id, cfg] of Object.entries(P03_DATA_SCREENS)) {
  if (cfg.kind === 'model_form' && id.startsWith('M06-')) forms[id] = cfg;
}
console.log(JSON.stringify({ subs, forms, create: P03_MODULE_CREATE.M06 || null,
  chips: Object.fromEntries(Object.entries(P03_FORM_CHIPS).filter(([k]) => k.startsWith('M06:'))),
  moduleForms: P03_MODULES.M06.forms, screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS)
    .filter(([k]) => k.startsWith('M06-'))) }));
"""


@pytest.fixture(scope="module")
def reg(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m06_capture")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    method = FREG_CREATE.search(
        (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    )
    assert method, "p03_workspace.js no longer defines fregCreate(mid, map)"
    probe = tmp / "probe.mjs"
    probe.write_text(PROBE % method.group(1), "utf-8")
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


def _sub(reg, no):
    return next(s for s in reg["subs"] if s["no"] == no)


# --- what each page offers -----------------------------------------------------

EXPECTED = {
    "1": {"module": True},  # + New Recovery Case
    "2": "M06-form-media",  # sealed intake (move and seal break are chips)
    "3": "M06-form-eval",  # the evaluation comes before any quote
    "4": "M06-form-attempt",
    "5": "M06-form-attempt-outcome",
    "6": "M06-form-inventory-line",  # capture pass 2: by file type
    "7": "M06-form-handover",
    "8": "M06-form-backup",
    "9": "M06-form-wipe-request",  # capture pass 2: the request first
    "10": "M06-form-undertaking",  # pass 2: undertaking before access
}


def test_the_scan_sees_ten_submodules(reg):
    assert [s["no"] for s in reg["subs"]] == [str(n) for n in range(1, 11)]


@pytest.mark.parametrize("no", sorted(EXPECTED, key=int))
def test_each_submodule_page_offers_its_capture(reg, no):
    sub = _sub(reg, no)
    want, got = EXPECTED[no], sub["create"]
    if isinstance(want, dict):
        assert got == want, "%s/%s offers %s" % (no, sub["title"], got)
    else:
        assert got and got.get("screen") == want, "%s/%s offers %s" % (no, sub["title"], got)
        assert got.get("label")


def test_every_capture_form_is_on_its_page_and_chip(reg):
    """'Forms Capturing It' lists the form the button opens, and every chip
    on a page opens a declared form."""
    chips = reg["chips"]
    for sub in reg["subs"]:
        names = sub["map"]["forms"]
        for name in names:
            assert chips.get("M06:" + name) in reg["forms"], "%s: chip %s" % (sub["no"], name)
        screen = sub["create"] and sub["create"].get("screen")
        if screen:
            assert any(chips.get("M06:" + n) == screen for n in names), sub["title"]
    assert set(reg["moduleForms"]) == {k[4:] for k in chips if "__" not in k}


def test_every_step_is_reachable_from_a_page(reg):
    """The steps a person performs, each on the page of its function."""
    on_pages = {reg["chips"]["M06:" + n] for s in reg["subs"] for n in s["map"]["forms"]}
    assert {
        "M06-form-eval",
        "M06-form-cleanroom",
        "M06-form-media-move",
        "M06-form-seal-break",
        "M06-form-handover-prep",
        "M06-form-purge",
    } <= on_pages


def test_the_capture_forms_bind_real_fields(reg, odoo_env):
    """A form field or a pick column the model lacks is dropped silently by
    /p03/model/form and /p03/model/records - it would just not appear."""
    bad = []
    for sid, cfg in reg["forms"].items():
        fields = odoo_env[cfg["model"]]._fields
        names = [f["name"] for s in cfg["sections"] for f in s["fields"]]
        pick = cfg.get("pickRecord") or {}
        names += pick.get("cols", []) + [c[0] for c in pick.get("domain", [])]
        bad += ["%s.%s" % (sid, n) for n in names if n not in fields]
    assert not bad, bad


def test_the_workflow_captures_call_whitelisted_methods_with_their_fields(reg):
    for sid, cfg in reg["forms"].items():
        act = cfg.get("saveAction")
        if not act:
            continue
        assert act["method"] in api.SURFACES[cfg["model"]]["actions"], sid
        shown = {f["name"] for s in cfg["sections"] for f in s["fields"]}
        assert set(act["kwargs"].values()) <= shown, sid
        assert cfg.get("pickRecord"), "%s acts on an existing record: it picks one" % sid


def test_the_handover_console_can_complete_a_handover(reg):
    """The handover is refused until the target drive is confirmed and the
    recipient verified: those steps must be on the console too."""
    methods = [a["m"] for a in reg["screens"]["M06-handover"]["actions"]]
    assert {"action_confirm_target_serial", "action_request_handover_otp"} <= set(methods)
    assert methods.index("action_confirm_target_serial") < methods.index("action_handover")


def test_the_pickers_and_pick_lists_are_served(reg, odoo_env):
    """Each form's declared picker filter passes the server's check, and each
    pick list loads through the reader the lists use."""
    ctrl = api.P03GenericApiController()
    with mock.patch.object(api, "request", mock.Mock(env=odoo_env)):
        for sid, cfg in reg["forms"].items():
            fields = [f for s in cfg["sections"] for f in s["fields"]]
            out = ctrl.model_form(model=cfg["model"], fields=fields)
            assert "error" not in out, (sid, out)
            pick = cfg.get("pickRecord")
            if pick:
                rows = ctrl.model_records(
                    model=cfg["model"], cols=pick["cols"], domain=pick["domain"]
                )
                assert "error" not in rows, (sid, rows)


# --- the saves, through the endpoints the forms use ----------------------------


def _kwargs(reg, sid, values):
    """The kwargs formSaveAction builds: server argument <- form field."""
    act = reg["forms"][sid]["saveAction"]
    return {k: values[f] for k, f in act["kwargs"].items() if values.get(f) not in (None, "")}


def _run(m6, reg, sid, who, rec, values):  # noqa: F811 - the imported fixture
    act = reg["forms"][sid]["saveAction"]
    return m6.p03_action(
        who, reg["forms"][sid]["model"], rec, act["method"], _kwargs(reg, sid, values)
    )


def test_the_inventory_is_recorded_by_the_case_staff_and_frozen_at_handover(reg, m6):  # noqa: F811 - the imported fixture
    sid = "M06-form-inventory"
    fresh = m6.new_case(serial="WD-INV-NEW-%d" % m6.n)
    values = {"recovered_files_count": 18250, "recovered_volume_gb": 412.5}
    out = _run(m6, reg, sid, m6.tech, fresh, values)
    assert not out["success"] and "before handover" in out["error"]

    case = m6.recovering(m6.new_case())
    out = _run(m6, reg, sid, m6.tech2, case, values)
    assert not out["success"] and "assigned staff" in out["error"]
    # a typed value is refused: the inventory is evidence
    res = m6.p03_write(m6.tech, CASE, case, {"recovered_files_count": 1})
    assert "error" in res and case.recovered_files_count == 0
    out = _run(m6, reg, sid, m6.tech, case, values)
    assert out["success"], out
    assert case.recovered_files_count == 18250 and case.recovered_volume_gb == 412.5

    m6.image(case)
    case.action_recovered()
    m6.settle(case)  # M06-F1: a billable case goes out paid, on credit or waived
    case.write({"handover_recipient_id": m6.contact.id, "encrypted_target_serial": "T-INV"})
    case.action_confirm_target_serial("T-INV")
    m6.receipt(case)
    case.action_handover(verification=m6.code_for(case)["code"])
    out = _run(m6, reg, sid, m6.tech, case, {"recovered_files_count": 1, "recovered_volume_gb": 1})
    assert not out["success"] and case.recovered_files_count == 18250


def test_the_inventory_report_shows_what_the_lab_recorded(m6):  # noqa: F811 - the imported fixture
    case = m6.recovering(m6.new_case())
    case.with_user(m6.tech).action_record_inventory(files_count=7, volume_gb=1.25)
    with mock.patch.object(api, "request", mock.Mock(env=m6.env(user=m6.tech.id))):
        out = api.P03GenericApiController().model_report(
            module="M06", report="recovered_inventory", params={}
        )
    row = next(r for r in out["rows"] if r["case"] == case.name)
    assert row["recovered_files"] == 7 and row["recovered_gb"] == 1.25
    assert out["labels"]["files"] == "Case Documents"


def test_an_attempt_outcome_closes_the_open_attempt(reg, m6):  # noqa: F811 - the imported fixture
    case = m6.recovering(m6.new_case())
    attempt = (
        m6.env["fix.data.recovery.attempt"]
        .with_user(m6.tech)
        .create({"case_id": case.id, "method": "firmware_repair"})
    )
    out = _run(
        m6,
        reg,
        "M06-form-attempt-outcome",
        m6.tech,
        attempt,
        {"outcome": "partial", "notes": "SA module rebuilt; 81% imaged"},
    )
    assert out["success"], out
    assert attempt.outcome == "partial" and attempt.finished_at
    assert attempt.notes == "SA module rebuilt; 81% imaged"
    # the form offers only real outcomes
    choices = {
        c[0]
        for f in reg["forms"]["M06-form-attempt-outcome"]["sections"][0]["fields"]
        if f["name"] == "outcome"
        for c in f["choices"]
    }
    assert "in_progress" not in choices


def test_the_handover_takes_the_uploaded_receipt(reg, m6):  # noqa: F811 - the imported fixture
    sid = "M06-form-handover"
    case = m6.recovered(m6.new_case())
    m6.settle(case)  # M06-F1: a billable case goes out paid, on credit or waived
    case.with_user(m6.tech).write(
        {"handover_recipient_id": m6.contact.id, "encrypted_target_serial": "TGT-UP"}
    )
    case.action_confirm_target_serial("TGT-UP")
    code = m6.code_for(case)["code"]
    scan = base64.b64encode(b"%PDF-1.4 signed by the courier").decode()
    bad = "000000" if code != "000000" else "111111"
    values = {
        "handover_verification_ref": bad,
        "handover_receipt_file": scan,
        "handover_receipt_filename": "courier-receipt.pdf",
    }
    out = _run(m6, reg, sid, m6.tech, case, values)
    assert not out["success"] and "does not match" in out["error"]
    # a refused handover leaves no receipt behind
    Att = m6.env["ir.attachment"].sudo()
    assert not Att.search([("res_model", "=", CASE), ("res_id", "=", case.id)])

    out = _run(m6, reg, sid, m6.tech, case, dict(values, handover_verification_ref=code))
    assert out["success"], out
    assert case.state == "handover"
    receipt = case.handover_receipt_attachment_id
    assert receipt.name == "courier-receipt.pdf" and receipt.res_id == case.id
    assert receipt.raw == b"%PDF-1.4 signed by the courier"


def test_named_staff_are_assigned_from_the_pickers(reg, m6):  # noqa: F811 - the imported fixture
    case = m6.new_case(staffed=False)
    values = {"assigned_technician_id": m6.tech.id, "z4_custodian_id": m6.custodian.id}
    out = _run(m6, reg, "M06-form-staff", m6.tech, case, values)
    assert out["success"], out
    assert case.assigned_technician_id == m6.tech and case.z4_custodian_id == m6.custodian
    out = _run(m6, reg, "M06-form-staff", m6.tech, case, dict(values, z4_custodian_id=m6.tech2.id))
    assert not out["success"] and "Z4 Custodian role" in out["error"]


def test_media_moves_and_a_witnessed_seal_break(reg, m6):  # noqa: F811 - the imported fixture
    case = m6.new_case()
    unit = (
        m6.env["fix.data.media.unit"]
        .with_user(m6.tech)
        .create(
            {"case_id": case.id, "seal_number": "SEAL-M06-%d" % m6.n, "media_label": "WD10EZEX"}
        )
    )
    # A02 pass 2 M06-03: the move names its receiver, who confirms it
    out = _run(
        m6,
        reg,
        "M06-form-media-move",
        m6.tech,
        unit,
        {"location": "z4_lab", "pending_receiver_id": m6.custodian.id},
    )
    assert out["success"], out
    unit.invalidate_recordset()
    assert unit.pending_location == "z4_lab" and unit.location == "reception"
    unit.with_user(m6.custodian).action_confirm_move()
    assert unit.location == "z4_lab" and m6.custodian.name in unit.holder
    out = _run(m6, reg, "M06-form-seal-break", m6.tech, unit, {"witness_user_id": m6.tech.id})
    assert not out["success"] and unit.seal_state == "sealed"
    out = _run(m6, reg, "M06-form-seal-break", m6.tech, unit, {"witness_user_id": m6.tech2.id})
    assert out["success"], out
    # A02 ERP audit M06-F11: naming the witness only asks; the seal opens when
    # the witness confirms in their own session
    unit.invalidate_recordset()
    assert unit.seal_state == "sealed"
    with pytest.raises(UserError):
        unit.with_user(m6.tech).action_confirm_seal_break()
    unit.with_user(m6.tech2).action_confirm_seal_break()
    unit.invalidate_recordset()
    assert unit.seal_state == "opened_in_lab" and unit.witness_user_id == m6.tech2


def test_a_purge_on_the_picked_certificate(reg, m6):  # noqa: F811 - the imported fixture
    case = m6.handed_over(m6.new_case(serial="WD-PURGE-%d" % m6.n), target="T-PURGE")
    # A02 pass 2 M06-04 (D15): the lab's purge certificate of the case
    cert = m6.purge_cert(case)
    out = _run(m6, reg, "M06-form-purge", m6.tech, case, {"purge_certificate_id": cert.id})
    assert out["success"], out
    assert case.state == "purged" and case.purge_certificate_id == cert
