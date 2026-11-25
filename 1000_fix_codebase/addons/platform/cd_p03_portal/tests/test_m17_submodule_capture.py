# M17 Device & Asset Registry: every sub-module page offers the button that
# captures its record (audit 2026-11-13).
#
# Before: Ownership & Custody had no "+ New" and its only chip opened a
# read-only form, so no custody event, transfer or lost/stolen report could be
# recorded from the page. Bulk Registration was a readiness report with a
# single-asset button (the spec's file upload, FR-AST-039, did not exist).
# Corporate Estates could create an estate but not place a device in one. The
# compatibility and PM forms existed but no page offered them. Alerts, merge
# lineage, identifier history and lost/stolen holds sat on no page.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M10 guard's fixture).
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location("_m10_capture", HERE / "test_m10_capture_buttons.py")
_m10 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m10)

# How each page's record is captured. 'form': a "+ New" or a chip opening an
# in-workspace form. 'system': written by the system, so the page offers no
# button and every list says where its rows come from.
CAPTURE = {
    "1": "form",  # the asset with its identifiers
    "2": "form",  # installed component, part compatibility
    "3": "form",  # custody event, ownership transfer, lost/stolen report
    "4": "system",  # service history is projected from orders (AUT-AST-05)
    "5": "form",  # installed component (part genealogy)
    "6": "system",  # repeat faults are detected from the history (BRU-AST-13)
    "7": "form",  # device warranty
    "8": "form",  # corporate estate, device placement
    "9": "form",  # bulk estate upload (FR-AST-039)
    "10": "form",  # condition grade, PM plan
    "11": "form",  # identity resolution
}


@pytest.fixture(scope="module")
def m17(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m17_capture")
    src = _m10.SRC
    for area in sorted(d for d in src.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    estate = _m10._estate
    meta = (src / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(estate.IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    engine = (src / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    probe = tmp / "probe.mjs"
    probe.write_text(
        _m10.PROBE.replace("M10", "M17")
        % {
            "create": estate._method(engine, "fregCreate(mid, map)"),
            "panels": estate._method(engine, "fregPanels(mid, mod, map)"),
        },
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=120
    )
    return json.loads(out.stdout)


def _sub(m17, no):
    return next(s for s in m17["subs"] if s["no"] == no)


def _chips(m17, no):
    return {f["f"]: f for f in _sub(m17, no)["forms"]}


def test_every_page_is_classified(m17):
    assert sorted(s["no"] for s in m17["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m17, no):
    sub = _sub(m17, no)
    opening = [f for f in sub["forms"] if f["opens"]]
    if CAPTURE[no] == "form":
        assert sub["create"] or opening, "page %s has no + New and no form chip" % no
        for f in sub["forms"]:
            assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])
            assert f["opens"], "chip %s opens a read-only form" % f["f"]
    else:
        assert not sub["create"] and not opening, "page %s lets a person type in %s" % (
            no,
            sub["model"],
        )
        assert all(lst["empty"] for lst in sub["lists"]), "page %s: say where rows come from" % no


def test_every_working_screen_sits_on_a_page(m17):
    """A list or report on no page cannot be reached from the register."""
    placed = {sid for s in m17["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid in m17["nav"]
        if m17["screens"].get(sid, {}).get("kind") != "model_form" and sid not in placed
    ]
    assert not orphans, orphans


def test_a_system_written_list_says_where_its_rows_come_from(m17):
    for sid in (
        "M17-history",
        "M17-ownership",
        "M17-holds",
        "M17-merges",
        "M17-idhistory",
        "M17-bulk-lines",
        "M17-alerts",
    ):
        cfg = m17["screens"][sid]
        assert cfg["create"] is False and cfg["empty"], sid


def test_ownership_and_custody_records_custody_transfer_and_loss(m17):
    sub = _sub(m17, "3")
    assert sub["create"] == "M17-form-custody"
    chips = _chips(m17, "3")
    assert chips["Custody Event"]["model"] == "fix.device.custody"
    # the transfer chip used to open the read-only history form
    assert chips["Ownership Transfer"]["id"] == "M17-form-transfer-record"
    assert chips["Report Lost / Stolen"]["id"] == "M17-form-lost"
    assert "M17-holds" in sub["screens"]


def test_the_transfer_form_runs_the_governed_transfer_with_its_evidence(m17):
    form = m17["screens"]["M17-form-transfer-record"]
    names = {f["name"] for f in form["fields"]}
    assert {
        "transfer_to_partner_id",
        "transfer_type_pending",
        "transfer_reason",
        "transfer_evidence_file",
        "transfer_evidence_document_id",
    } <= names


def test_estates_page_places_a_device_in_an_estate(m17):
    chips = _chips(m17, "8")
    assert chips["Corporate Estate"]["model"] == "fix.device.estate"
    # capture pass 2 (2026-11-19): a dated placement at an estate node
    # (FR-AST-038), no longer a bare write of the device's estate
    assert chips["Estate Assignment"]["id"] == "M17-form-estate-placement"
    assert chips["Estate Assignment"]["model"] == "fix.device.estate.placement"


def test_bulk_registration_uploads_an_estate_file(m17):
    sub = _sub(m17, "9")
    assert sub["model"] == "fix.device.bulk.load"
    assert sub["create"] == "M17-form-bulk"
    assert {"M17-bulk-loads", "M17-bulk-lines"} <= set(sub["screens"])
    actions = next(x for x in sub["lists"] if x["id"] == "M17-bulk-loads")["actions"]
    assert {"action_validate", "action_commit"} <= set(actions)
    form = m17["screens"]["M17-form-bulk"]
    assert {"estate_id", "upload_file"} <= {f["name"] for f in form["fields"]}


def test_the_estate_file_picker_offers_csv_and_excel():
    # the engine's default accept list (PDF, images, Word) hid the estate file
    text = (_m10.SRC / "a07" / "m17.js").read_text(encoding="utf-8")
    line = next(ln for ln in text.splitlines() if "name: 'upload_file'" in ln)
    assert "accept: '.csv,.xlsx'" in line


def test_condition_page_offers_the_pm_plan_and_components_page_the_matrix(m17):
    assert _chips(m17, "10")["PM Plan"]["model"] == "fix.device.pm"
    assert _chips(m17, "2")["Part Compatibility"]["model"] == "fix.device.part.compatibility"
