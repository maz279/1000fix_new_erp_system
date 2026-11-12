# M20 AR, Invoicing & Collections: every sub-module page offers the button that
# captures its record (capture-button audit 2026-11-13).
#
# Before: six of the ten pages showed no button. Delivery Channels (consolidated
# corporate bills, FR-ARB-008), Credit Control (limits and terms, FR-ARB-030),
# Dunning & Collections (disputes, FR-ARB-036 P0) and Credit Notes & Refunds
# had nothing, and Matching & Allocation hid its VDS certificate in a chip.
# No screen anywhere could raise a dispute or start a consolidated bill: the
# engine's arDisputeCreate / arConsolidatedGenerate were never called, and the
# consolidated-bill list had no Generate although its surface allowed it.
# Billable-Event Intake listed INVOICES, not the billable-event queue.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M02/M10 guard fixture).
from __future__ import annotations

import ast
import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "static" / "src"
CONTROLLERS = HERE.parent / "controllers" / "a08"

_spec = importlib.util.spec_from_file_location(
    "_estate_pages", HERE / "test_estate_module_pages.py"
)
_estate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_estate)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS } = M;
function %(create)s
function %(panels)s
const mod = P03_MODULES.M20;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M20', map);
  const forms = fregPanels('M20', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M20:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const lists = (map.screens || []).map((id) => ({ id, cfg: P03_DATA_SCREENS[id] || {} }))
    .filter((x) => x.cfg.kind === 'model_list')
    .map((x) => ({ id: x.id, model: x.cfg.model, create: x.cfg.create !== false, empty: !!x.cfg.empty,
      actions: (x.cfg.actions || []).map((a) => a.m) }));
  return { no: s[0], model: map.model || null, screens: map.screens || [],
    create: create && (create.screen || (create.module ? 'module' : null)), forms, lists };
});
const S = P03_DATA_SCREENS;
const keep = (id) => id.startsWith('M20-') || id === 'M33-form-credit';
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(S).filter(([id]) => keep(id)).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, back: c.back || null, empty: !!c.empty,
    actions: (c.actions || []).map((a) => a.m),
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required, domain: f.domain || null })) }])) }));
"""

# How each page's record is captured. 'form': a "+ New" or a chip opening an
# in-workspace form. 'system': fed by a workflow or computed, so the page
# offers nothing to type.
CAPTURE = {
    "1": "system",  # billable events arrive from closed jobs (FR-ARB-001)
    "2": "form",  # manual-invoice exception + consolidated bill
    "3": "system",  # the Mushak 6.3 is rendered when the invoice is issued
    "4": "form",  # consolidated corporate bill
    "5": "form",  # receipt, payment link
    "6": "form",  # the customer's Mushak 6.6 VDS certificate
    "7": "form",  # customer credit profile (limit, terms)
    "8": "form",  # dispute against an issued invoice
    "9": "form",  # credit note / refund request
    "10": "system",  # delivered-but-unbilled is computed
}


@pytest.fixture(scope="module")
def m20(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m20_capture")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(_estate.IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    probe = tmp / "probe.mjs"
    probe.write_text(
        PROBE
        % {
            "create": _estate._method(engine, "fregCreate(mid, map)"),
            "panels": _estate._method(engine, "fregPanels(mid, mod, map)"),
        },
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=120
    )
    return json.loads(out.stdout)


def _sub(m20, no):
    return next(s for s in m20["subs"] if s["no"] == no)


def _surfaces():
    """controllers/a08/m20.py SURFACES, read without importing Odoo."""
    tree = ast.parse((CONTROLLERS / "m20.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "SURFACES" for t in node.targets
        ):
            out = {}
            for key, val in zip(node.value.keys, node.value.values, strict=True):
                conf = {}
                for k, v in zip(val.keys, val.values, strict=True):
                    if k.value == "actions":
                        conf["actions"] = (
                            set() if isinstance(v, ast.Call) else {e.value for e in v.elts}
                        )
                out[key.value] = conf
            return out
    raise AssertionError("SURFACES not found in controllers/a08/m20.py")


def test_every_page_is_classified(m20):
    assert sorted(s["no"] for s in m20["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m20, no):
    sub = _sub(m20, no)
    opening = [f for f in sub["forms"] if f["opens"]]
    if CAPTURE[no] == "form":
        assert sub["create"], "page %s has no + New button" % no
        for f in sub["forms"]:
            # the invoice request chip opens the M20 invoice editor (estate EDITOR_CHIPS)
            if f["f"] == "Invoice Request":
                continue
            assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])
            assert f["opens"], "chip %s opens a form that refuses a new record" % f["f"]
    else:
        assert not sub["create"] and not opening, "page %s lets a person type in %s" % (
            no,
            sub["model"],
        )
        assert all(lst["empty"] for lst in sub["lists"]), "page %s: say where rows come from" % no


def test_every_working_screen_sits_on_a_page(m20):
    """A list or report on no page cannot be reached from the register."""
    placed = {sid for s in m20["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid in m20["nav"]
        if m20["screens"].get(sid, {}).get("kind") != "model_form" and sid not in placed
    ]
    assert not orphans, orphans


def test_billable_event_intake_lists_the_queue_not_invoices(m20):
    sub = _sub(m20, "1")
    assert sub["model"] == "fix.billable.event"
    assert "fix.billable.event" in _surfaces(), "the page's grid needs a served surface"


def test_dunning_page_raises_a_dispute(m20):
    sub = _sub(m20, "8")
    assert sub["create"] == "M20-form-dispute"
    form = m20["screens"]["M20-form-dispute"]
    assert form["model"] == "fix.ar.dispute"
    editable = {f["name"] for f in form["fields"] if not f["readonly"]}
    assert editable == {"invoice_id", "amount_disputed", "reason"}, editable
    invoice = next(f for f in form["fields"] if f["name"] == "invoice_id")
    assert invoice["domain"] == [["state", "in", ["issued", "paid"]]]
    # the outcome is decided by the resolve buttons, never typed (BRU-ARB-17)
    assert {"outcome_code", "state", "resolved_by"} <= {
        f["name"] for f in form["fields"] if f["readonly"]
    }
    assert m20["screens"]["M20-ar-dispute"].get("create") is not False


def test_consolidated_bill_is_started_and_generated(m20):
    sub = _sub(m20, "4")
    assert sub["create"] == "M20-form-consolidated"
    assert any(f["f"] == "Consolidated Bill" and f["opens"] for f in _sub(m20, "2")["forms"])
    form = m20["screens"]["M20-form-consolidated"]
    required = {f["name"] for f in form["fields"] if f["required"]}
    # every NOT NULL field the model has without a default
    assert {
        "customer_id",
        "operating_unit_id",
        "bill_ref",
        "period_start",
        "period_end",
    } <= required
    lst = m20["screens"]["M20-ar-consolidated-bill"]
    assert lst.get("create") is not False
    assert {"action_generate", "action_send"} <= set(lst["actions"])
    assert set(lst["actions"]) <= _surfaces()["fix.ar.consolidated.bill"]["actions"]


def test_credit_control_captures_a_credit_profile(m20):
    sub = _sub(m20, "7")
    assert sub["create"] == "M33-form-credit"
    form = m20["screens"]["M33-form-credit"]
    assert form["model"] == "fix.credit.profile"
    assert {"M20-ecl-rates", "M20-writeoffs"} <= set(sub["screens"])


def test_credit_notes_page_has_its_button(m20):
    assert _sub(m20, "9")["create"] == "M20-form-note"


def test_matching_page_captures_the_vds_certificate(m20):
    sub = _sub(m20, "6")
    assert sub["create"] == "M20-form-vds"
    assert "M20-unapplied" in sub["screens"]


def test_new_forms_are_writable(m20):
    """The write endpoint accepts exactly the forms' editable fields (generated)."""
    text = (CONTROLLERS / "writable.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    writable = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == "WRITABLE":
            for key, val in zip(node.value.keys, node.value.values, strict=True):
                writable[key.value] = {e.value for e in val.args[0].elts} if val.args else set()
    for sid in ("M20-form-dispute", "M20-form-consolidated"):
        form = m20["screens"][sid]
        editable = {f["name"] for f in form["fields"] if not f["readonly"]}
        assert editable <= writable[form["model"]], (sid, editable - writable[form["model"]])
