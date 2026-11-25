# M36 capture audit, third pass (2026-11-19): the spec items pass 2 left as
# "not built" now have their captures on the pages that own them:
#   p2  Bulk Estate Quotation (asset upload)          FR-QTE-021/022
#   p3  Compare with the Previous Version             FR-QTE-013
#   p5  Send Customer Approval Link                   FR-QTE-034, T-05
# (the reminder / unviewed / renewal automations are crons, tested live).
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
QUOTATION = HERE.parents[2] / "domain" / "c_commercial" / "cd_quotation"

_spec = importlib.util.spec_from_file_location("_m36_pass1b", HERE / "test_m36_capture_buttons.py")
_p1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_p1)

m36 = _p1.m36

PASS3 = {
    "2": ["M36-form-estate"],
    "3": ["M36-form-compare"],
    "5": ["M36-form-approval-link"],
}
PICK_ACTIONS = {
    "M36-form-compare": (
        "action_record_version_comparison",
        set(),
        ["parent_version_id", "!=", False],
    ),
    "M36-form-approval-link": (
        "action_send_approval_link",
        {"approval_link_channel", "approval_link_recipient"},
        ["state", "=", "sent"],
    ),
}


@pytest.mark.parametrize("no", sorted(PASS3, key=int))
def test_each_page_captures_its_remaining_spec_item(m36, no):
    chips = {f["id"] for f in _p1._sub(m36, no)["forms"] if f["opens"]}
    missing = [form for form in PASS3[no] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("sid", sorted(PICK_ACTIONS))
def test_pass3_pick_forms_run_their_method(m36, sid):
    cfg = m36["screens"][sid]
    method, inputs, clause = PICK_ACTIONS[sid]
    assert cfg["kind"] == "model_form" and cfg["pick"], sid
    assert clause in cfg["pick"]["domain"], sid
    assert cfg["save"]["method"] == method
    assert method in _p1._surfaces()["fix.quotation"]
    assert set(cfg["save"]["kwargs"].values()) == inputs
    assert not {f["name"] for f in cfg["fields"] if not f["readonly"]}, sid


def test_the_estate_form_uploads_the_asset_list(m36):
    cfg = m36["screens"]["M36-form-estate"]
    fields = {f["name"]: f for f in cfg["fields"]}
    assert fields["estate_file"]["required"] and not fields["estate_file"]["readonly"]
    assert {"estate_file", "estate_filename"} <= _p1._writable()["fix.quotation"]
    assert "action_import_estate" in _p1._surfaces()["fix.quotation"]


def test_the_approval_token_is_never_writable_or_listed(m36):
    assert "access_token" not in _p1._writable()["fix.quotation"]
    for sid, cfg in m36["screens"].items():
        if sid.startswith("M36-"):
            assert "access_token" not in cfg["cols"], sid
            assert "access_token" not in {f["name"] for f in cfg["fields"]}, sid


def test_the_follow_up_and_renewal_jobs_are_scheduled():
    xml = (QUOTATION / "data" / "ir_cron_capture3.xml").read_text(encoding="utf-8")
    assert "model.cron_quotation_followups()" in xml
    assert "model.cron_renewal_quotations()" in xml
    manifest = (QUOTATION / "__manifest__.py").read_text(encoding="utf-8")
    assert "data/ir_cron_capture3.xml" in manifest
