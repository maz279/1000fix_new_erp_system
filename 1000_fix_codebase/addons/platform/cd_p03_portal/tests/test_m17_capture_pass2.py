# M17 capture pass 2 (2026-11-19): every sub-module page captures the record
# the spec places on it, not only "a" record.
#
# After 13 Nov every page had a "+ New", yet measured against the spec seven
# pages could not record what is recorded there, because no model held it:
# the QR asset label and further identifiers (p1, FR-AST-002/008), the
# accessory register and actual configuration (p2, FR-AST-012/015), the
# population and its reason-coded change (p3, FR-AST-022), the warranty's
# derivation basis (p7, BRU-AST-16), estate sites/departments/users and dated
# placements (p8, FR-AST-038), the end-of-life routing decision (p10,
# FR-AST-048) and the stewardship worklist (p11, FR-AST-051).
#
# Evaluated as the browser evaluates it, through the fixture of
# test_m17_submodule_capture (node runs the engine's fregCreate/fregPanels).
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PORTAL = HERE.parent

_spec = importlib.util.spec_from_file_location(
    "_m17_capture", HERE / "test_m17_submodule_capture.py"
)
_m17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m17)
m17 = _m17.m17  # the module-scoped fixture

# The records each page must offer a form for (pass 2).
PAGE_RECORDS = {
    "1": {"fix.device", "fix.device.label"},
    "2": {"fix.device.accessory", "fix.device.configuration", "fix.device.component"},
    "3": {"fix.device.population.change", "fix.device.custody"},
    "7": {"fix.warranty"},
    "8": {"fix.device.estate", "fix.device.estate.node", "fix.device.estate.placement"},
    "10": {"fix.device.eol.decision", "fix.device.condition", "fix.device.pm"},
    "11": {"fix.device.quality.issue", "fix.device.identity"},
}
# The list each page must show for the new records.
PAGE_LISTS = {
    "1": {"M17-labels"},
    "2": {"M17-accessories", "M17-configs"},
    "3": {"M17-populations"},
    "8": {"M17-estate-nodes", "M17-placements"},
    "10": {"M17-eol"},
    "11": {"M17-quality-issues"},
}
NEW_MODELS = {
    "fix.device.label",
    "fix.device.accessory",
    "fix.device.configuration",
    "fix.device.population.change",
    "fix.device.estate.node",
    "fix.device.estate.placement",
    "fix.device.eol.decision",
    "fix.device.quality.issue",
}


def _sub(data, no):
    return next(s for s in data["subs"] if s["no"] == no)


@pytest.mark.parametrize("no", sorted(PAGE_RECORDS, key=int))
def test_each_page_captures_the_records_the_spec_places_there(m17, no):
    sub = _sub(m17, no)
    offered = {f["model"] for f in sub["forms"] if f["opens"]}
    if sub["create"] == "module":
        offered.add("fix.device")  # the module's own "+ Asset"
    elif sub["create"]:
        offered.add(m17["screens"][sub["create"]]["model"])
    missing = PAGE_RECORDS[no] - offered
    assert not missing, "page %s cannot capture %s" % (no, sorted(missing))


@pytest.mark.parametrize("no", sorted(PAGE_LISTS, key=int))
def test_each_page_lists_its_new_records(m17, no):
    assert PAGE_LISTS[no] <= set(_sub(m17, no)["screens"])


def test_page_one_adds_identifiers_through_the_governed_action(m17):
    chips = {f["f"]: f for f in _sub(m17, "1")["forms"]}
    assert chips["Add Identifier"]["id"] == "M17-form-identifier-add"
    text = (PORTAL / "static" / "src" / "a07" / "m17.js").read_text(encoding="utf-8")
    block = text[text.index("'M17-form-identifier-add'") :]
    block = block[: block.index("\n  },\n")]
    assert "method: 'action_add_identifier'" in block
    assert "pickRecord" in block


def test_the_old_device_pick_placement_form_is_gone(m17):
    """It wrote the device's estate with no date, node or reason."""
    assert "M17-form-placement" not in m17["screens"]


def test_the_warranty_form_records_the_derivation_basis(m17):
    names = {f["name"] for f in m17["screens"]["M17-form-warranty"]["fields"]}
    assert "derivation_basis" in names


def test_accessory_and_stewardship_lists_carry_their_actions(m17):
    lists = {x["id"]: x for s in m17["subs"] for x in s["lists"]}
    assert {"action_return", "action_report_missing"} <= set(lists["M17-accessories"]["actions"])
    assert {"action_start", "action_resolve"} <= set(lists["M17-quality-issues"]["actions"])
    assert {"action_request", "action_approve", "action_reject"} <= set(lists["M17-eol"]["actions"])


def _surfaces():
    text = (PORTAL / "controllers" / "a07" / "m17.py").read_text(encoding="utf-8")
    start = text.index("SURFACES = {")
    return text[start:], set(re.findall(r'^    "([a-z0-9_.]+)": \{', text[start:], re.M))


def test_every_new_model_is_served_and_writable():
    text, served = _surfaces()
    assert served >= NEW_MODELS, sorted(NEW_MODELS - served)
    assert '"action_add_identifier"' in text
    writable = (PORTAL / "controllers" / "a07" / "writable.py").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        assert '"%s": frozenset(\n' % model in writable, model
    a02 = (PORTAL / "controllers" / "a02" / "writable.py").read_text(encoding="utf-8")
    warranty = a02[a02.index('"fix.warranty": frozenset(') :]
    assert '"derivation_basis"' in warranty[: warranty.index("),")]


def test_actions_offered_on_the_lists_are_whitelisted():
    text, _served = _surfaces()
    js = (PORTAL / "static" / "src" / "a07" / "m17.js").read_text(encoding="utf-8")
    for action in (
        "action_return",
        "action_report_missing",
        "action_request",
        "action_approve",
        "action_reject",
        "action_start",
        "action_resolve",
    ):
        assert "m: '%s'" % action in js
        assert '"%s"' % action in text, action
