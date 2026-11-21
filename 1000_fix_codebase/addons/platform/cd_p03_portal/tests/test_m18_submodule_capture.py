# M18 E-Waste & Recycling: every Function Register sub-module page captures
# what its function records.
#
# Reported 2026-11-13: "not all the sub-modules have a relevant data capture
# button". Measured over the real registry with the engine's own page rule
# (p03_workspace.js fregCreate), before the fix:
#   3 Data Destruction, 9 ESG & Carbon -> no button at all (9 is right: its
#     figures are computed, BRU-ESG-11; 3 is the destruction gate itself);
#   5 Green Certificates -> "+ Green & Destruction Certificate", which the
#     server REFUSES for everyone (a certificate is recorded from its
#     processed batch): a dead button;
#   10 Compliance Pack -> page 8's return again; the DoE registration the
#     returns are filed under had no page;
#   Basel PIC, recycler money and registration lists were on no page.
# Found on the way: every evidence link (recycler licence, processing
# evidence, recycler certificate, battery photo, PIC, registration) was a
# picker over EXISTING attachments, read with sudo across the company - no one
# could upload a scan, so no recycler could be approved or dispatched to and
# no certificate issued from the workspace.
#
# The page rule is JavaScript, so it is EXECUTED in node over the real
# registry; the steps run through the endpoints the forms use, as non-admin
# users holding only the M18 roles (cd_ewaste's own fixtures).
from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from odoo.addons.cd_ewaste.tests.m18_fixtures import M18, refused
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a05.writable import WRITABLE

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
FREG_CREATE = re.compile(r"^    (fregCreate\(mid, map\) \{\n.*?\n    \})\n", re.S | re.M)
COL, BATCH, CERT = "fix.ewaste.collection", "fix.ewaste.batch", "fix.ewaste.certificate"
SCAN = base64.b64encode(b"%PDF-1.4 recycler scan").decode()

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %s
const subs = P03_MODULES.M18.freg.sub.map((s) => ({ no: s[0], title: s[1], map: s[3] || null,
  create: fregCreate('M18', s[3] || null) }));
const forms = {};
for (const [id, cfg] of Object.entries(P03_DATA_SCREENS)) {
  if (cfg.kind === 'model_form') forms[id] = cfg;
}
console.log(JSON.stringify({ subs, forms,
  chips: Object.fromEntries(Object.entries(P03_FORM_CHIPS).filter(([k]) => k.startsWith('M18:'))),
  moduleForms: P03_MODULES.M18.forms, screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS)
    .filter(([k]) => k.startsWith('M18-'))) }));
"""


@pytest.fixture(scope="module")
def reg(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m18_capture")
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


def _m18_forms(reg):
    return {k: v for k, v in reg["forms"].items() if k.startswith("M18-")}


# --- what each page offers -----------------------------------------------------

EXPECTED = {
    "1": {"module": True},  # + New Collection Intake
    "2": "M18-form-triage",
    "3": "M18-form-destruction",  # the destruction gate (bind + release are chips)
    "4": "M18-form-batch",
    "5": "M18-form-cert-record",  # from the processed batch, never typed
    "6": "M18-form-event",
    "7": "M18-form-battery",
    "8": "M18-form-return",
    # capture pass 2 (19 Nov): the figures stay computed (BRU-ESG-11 / T-07);
    # what page 9 captures is the versioned factor set (FR-ESG-019 / T-08)
    "9": "M18-form-factor",
    # capture pass 2: page 10's record is the regulatory register (FR-ESG-016);
    # the DoE registration is a chip on it
    "10": "M18-form-obligation",
}


def test_the_scan_sees_ten_submodules(reg):
    assert [s["no"] for s in reg["subs"]] == [str(n) for n in range(1, 11)]


@pytest.mark.parametrize("no", sorted(EXPECTED, key=int))
def test_each_submodule_page_offers_its_capture(reg, no):
    sub = _sub(reg, no)
    want, got = EXPECTED[no], sub["create"]
    if want is None or isinstance(want, dict):
        assert got == want, "%s/%s offers %s" % (no, sub["title"], got)
    else:
        assert got and got.get("screen") == want, "%s/%s offers %s" % (no, sub["title"], got)
        assert got.get("label")


def test_no_two_pages_offer_the_same_button(reg):
    screens = [
        s["create"]["screen"] for s in reg["subs"] if s["create"] and "screen" in s["create"]
    ]
    assert len(screens) == len(set(screens)), screens


def test_every_capture_form_is_on_its_page_and_chip(reg):
    chips = reg["chips"]
    for sub in reg["subs"]:
        names = sub["map"]["forms"]
        for name in names:
            assert chips.get("M18:" + name) in reg["forms"], "%s: chip %s" % (sub["no"], name)
        screen = sub["create"] and sub["create"].get("screen")
        if screen:
            assert any(chips.get("M18:" + n) == screen for n in names), sub["title"]
    assert set(reg["moduleForms"]) == {k[4:] for k in chips if "__" not in k}


def test_every_m18_list_screen_sits_on_a_page(reg):
    on_pages = {s for sub in reg["subs"] for s in sub["map"]["screens"]}
    for sid in ("M18-pic", "M18-registration", "M18-settlements"):
        assert sid in on_pages, sid


def test_no_page_offers_a_create_the_server_refuses(reg):
    """A disposal certificate is recorded by its processed batch: its list
    offers no + New and its form only completes an existing draft."""
    screens, forms = reg["screens"], reg["forms"]
    assert screens["M18-certs"].get("create") is False and screens["M18-certs"]["empty"]
    assert forms["M18-form-cert"].get("create") is False
    assert forms["M18-form-cert"]["pickRecord"]["domain"] == [["state", "=", "draft"]]
    for fid in ("M18-form-destruction", "M18-form-release", "M18-form-cert-record"):
        assert forms[fid].get("pickRecord") and forms[fid].get("saveAction"), fid


def test_evidence_is_uploaded_not_picked(reg):
    """Every evidence link is filled by an upload; the link itself is shown
    read-only, and no workspace write may set it to some other attachment."""
    links = {
        "M18-form-cert": ("evidence_attachment_id", "evidence_file"),
        "M18-form-batch": ("processing_evidence_id", "processing_file"),
        "M18-form-battery": ("inspection_evidence_id", "inspection_file"),
        "M18-form-partner": ("licence_attachment_id", "licence_file"),
        "M18-form-pic": ("evidence_attachment_id", "evidence_file"),
        "M18-form-registration": ("evidence_attachment_id", "evidence_file"),
    }
    forms = reg["forms"]
    for fid, (link, upload) in links.items():
        spec = {f["name"]: f for s in forms[fid]["sections"] for f in s["fields"]}
        assert spec[link].get("readonly"), fid
        assert spec[upload].get("type") == "file", fid
        model = forms[fid]["model"]
        assert link not in WRITABLE[model] and upload in WRITABLE[model], model


def test_every_form_field_and_filter_exists(reg, odoo_env):
    """No phantom field on any M18 form (a missing one is dropped silently),
    every picker/step filter is one the server accepts, and every step's
    method is on its surface."""
    for fid, cfg in _m18_forms(reg).items():
        model = odoo_env[cfg["model"]]
        for sec in cfg["sections"]:
            for f in sec["fields"]:
                assert f["name"] in model._fields, "%s: %s" % (fid, f["name"])
                if f.get("domain"):
                    comodel = model._fields[f["name"]].comodel_name
                    assert api._choice_domain(odoo_env, comodel, f["domain"]) == f["domain"]
        pick = cfg.get("pickRecord")
        if pick:
            for col in pick["cols"]:
                assert col in model._fields, "%s pick col %s" % (fid, col)
            for leaf in pick["domain"]:
                if isinstance(leaf, list):
                    assert leaf[0].split(".")[0] in model._fields, "%s filter %s" % (fid, leaf)
            model.search(pick["domain"], limit=1)  # well-formed
        act = cfg.get("saveAction")
        if act:
            assert act["method"] in api.SURFACES[cfg["model"]]["actions"], fid


# --- each step, done the legitimate way through the endpoints -----------------


@pytest.fixture
def m(odoo_env):
    x = M18(odoo_env)
    try:
        yield x
    finally:
        x.close()


def _ok(out):
    assert out.get("success") or (out and not out.get("error")), out
    return out


def _new_id(out):
    return out.get("id") or out.get("record_id") or (out.get("record") or {}).get("id")


def test_page3_destruction_gate_bind_start_release(m):
    """Bind the M06 certificate, start destruction, release - each through the
    endpoint its form uses; the release is refused until M06 has verified."""
    dev = m.device()
    col = m.collection(device_id=dev.id, weight_kg=0.5)
    m.triage(col, "recycle", data_bearing=True)
    assert col.state == "triaged"
    cert = m.verified_cert(dev.serial_number, col)
    _ok(m.p03_write(m.clerk, COL, col.id, {"wipe_certificate_id": cert.id}))
    _ok(m.p03_action(m.clerk, COL, [col.id], "action_secure_destruction"))
    col.invalidate_recordset()
    assert col.state == "destruction" and col.wipe_certificate_id == cert
    _ok(m.p03_action(m.clerk, COL, [col.id], "action_recycle_estimated"))
    col.invalidate_recordset()
    assert col.state == "recycled" and col.esg_co2_saved_kg > 0


def test_page3_release_without_a_verified_certificate_is_refused(m):
    dev = m.device()
    col = m.collection(device_id=dev.id, weight_kg=0.5)
    m.triage(col, "recycle", data_bearing=True)
    _ok(
        m.p03_action(m.clerk, COL, [col.id], "action_secure_destruction")
    )  # raises an unverified one
    out = m.p03_action(m.clerk, COL, [col.id], "action_recycle_estimated")
    assert not out.get("success")
    col.invalidate_recordset()
    assert col.state == "destruction"


def test_page5_certificate_recorded_from_batch_then_scan_uploaded_and_issued(m):
    item = m.ready_item(weight=0.5)
    batch = m.processed_batch([item])
    _ok(m.p03_action(m.dispatcher, BATCH, [batch.id], "action_record_certificate"))
    cert = batch.certificate_ids
    assert cert.state == "draft"
    # the link itself is no longer a workspace input
    other = m.env["ir.attachment"].create({"name": "someone-elses.pdf", "datas": SCAN})
    assert m.p03_write(m.dispatcher, CERT, cert.id, {"evidence_attachment_id": other.id}).get(
        "error"
    )
    _ok(
        m.p03_write(
            m.dispatcher,
            CERT,
            cert.id,
            {
                "certificate_no": "REC-UP-1",
                "recycler_stated_weight_kg": batch.processed_weight_kg,
                "evidence_file": SCAN,
                "evidence_filename": "recycler-cert.pdf",
            },
        )
    )
    cert.invalidate_recordset()
    att = cert.evidence_attachment_id
    assert att.name == "recycler-cert.pdf"
    assert (att.res_model, att.res_id) == (CERT, cert.id)
    _ok(m.p03_action(m.compliance, CERT, [cert.id], "action_issue"))
    cert.invalidate_recordset()
    item.invalidate_recordset()
    assert cert.state == "issued" and item.state == "certified"
    # an issued certificate's scan is frozen, upload included
    out = m.p03_write(
        m.dispatcher, CERT, cert.id, {"evidence_file": SCAN, "evidence_filename": "x.pdf"}
    )
    assert out.get("error")
    assert {"evidence_file", "evidence_filename"} <= api._locked_fields(cert)


def test_certificate_is_still_never_typed(m):
    partner = m.approved_partner()
    assert refused(
        m.env,
        lambda: m.env[CERT].with_user(m.compliance).create({"partner_id": partner.id}),
    )


def test_recycler_licence_scan_uploaded_makes_it_approvable_and_dispatchable(m):
    out = _ok(
        m.p03_write(
            m.clerk,
            "fix.ewaste.partner",
            None,
            {
                "name": "Upload Recycler",
                "certification": "doe",
                "certificate_no": "DOE-UP-1",
                "valid_from": str(m.today),
                "valid_to": str(m.today.replace(year=m.today.year + 1)),
                "licence_file": SCAN,
                "licence_filename": "doe-licence.pdf",
            },
        )
    )
    partner = m.env["fix.ewaste.partner"].search([("name", "=", "Upload Recycler")])
    assert partner and (not _new_id(out) or _new_id(out) == partner.id)
    assert partner.licence_attachment_id.name == "doe-licence.pdf"
    assert partner.licence_attachment_id.res_id == partner.id


def test_processing_evidence_is_uploaded_only_once_received(m):
    batch = m.dispatched_batch()
    out = m.p03_write(
        m.dispatcher, BATCH, batch.id, {"processing_file": SCAN, "processing_filename": "p.pdf"}
    )
    assert out.get("error"), "evidence before the recycler received the batch"
    batch.write({"received_weight_kg": batch.weight_kg, "recycler_receipt_ref": "RCV-UP"})
    batch.action_receive()
    _ok(
        m.p03_write(
            m.dispatcher,
            BATCH,
            batch.id,
            {"processing_file": SCAN, "processing_filename": "processed.pdf"},
        )
    )
    batch.invalidate_recordset()
    assert batch.processing_evidence_id.name == "processed.pdf"
    batch.action_process()
    assert batch.state == "processed"


def test_battery_photo_uploaded_on_intake_lets_hse_inspect(m):
    _ok(
        m.p03_write(
            m.clerk,
            "fix.ewaste.battery",
            None,
            {
                "chemistry": "li_ion",
                "weight_kg": 0.3,
                "inspection_file": SCAN,
                "inspection_filename": "taped.jpg",
            },
        )
    )
    bat = m.env["fix.ewaste.battery"].search([], order="id desc", limit=1)
    assert bat.inspection_evidence_id.name == "taped.jpg"
    _ok(m.p03_action(m.hse, "fix.ewaste.battery", [bat.id], "action_inspect_and_quarantine"))
    bat.invalidate_recordset()
    assert bat.terminal_taped and bat.inspected_by_id == m.hse


def test_page10_registration_with_its_scan_is_confirmed_by_another_officer(m):
    _ok(
        m.p03_write(
            m.compliance,
            "fix.ewaste.registration",
            None,
            {
                "authority": "doe",
                "role": "collection_centre",
                "registration_no": "DOE-EW-UP-1",
                "valid_from": str(m.today),
                "valid_to": str(m.today.replace(year=m.today.year + 1)),
                "evidence_file": SCAN,
                "evidence_filename": "doe-registration.pdf",
            },
        )
    )
    reg = m.env["fix.ewaste.registration"].search(
        [("registration_no", "=", "DOE-EW-UP-1")], limit=1
    )
    assert reg.evidence_attachment_id.name == "doe-registration.pdf"
    out = m.p03_action(m.compliance, "fix.ewaste.registration", [reg.id], "action_activate")
    assert not out.get("success"), "four eyes: the recorder does not confirm"
    _ok(m.p03_action(m.compliance2, "fix.ewaste.registration", [reg.id], "action_activate"))
    reg.invalidate_recordset()
    assert reg.state == "active"
