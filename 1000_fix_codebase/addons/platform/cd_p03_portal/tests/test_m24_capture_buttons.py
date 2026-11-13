# M24 Documents & E-Signature: every sub-module page offers the button that
# captures ITS record (audit 2026-11-13).
#
# Before: Auto-Filing and Retention & Holds offered "+ New Document" (a manual
# upload) although neither page's record is an upload; Versioning & Control
# listed every document, controlled or not, and its + New made an
# uncontrolled one; the Signature Envelope form had no signer grid, so an
# envelope made in the workspace could never be sent ("An envelope needs at
# least one signer"); the Document Template form could never save (a template
# is bilingual by default and then needs its Bengali name, which the form did
# not show); no page could place a legal hold or dispose of a document,
# although both methods were served; Classification & Search and Evidence
# Packs showed no chip at all.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M37 guard's fixture).
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
CONTROLLER = HERE.parent / "controllers" / "a10" / "m24.py"
ADDONS = HERE.parents[2]

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
const mod = P03_MODULES.M24;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M24', map);
  const forms = fregPanels('M24', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M24:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  return { no: s[0], title: s[1], model: map.model || null, domain: map.domain || [],
    create: create && (create.screen || (create.module ? 'module' : null)),
    label: create ? (create.label || null) : null,
    presets: (create && create.presets) || null, forms };
});
const S = P03_DATA_SCREENS;
console.log(JSON.stringify({ subs,
  module_create: P03_MODULE_CREATE.M24,
  screens: Object.fromEntries(Object.entries(S).filter(([id]) => id.startsWith('M24-') || id === 'M31-form-evidence').map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, back: c.back || null, empty: !!c.empty,
    domain: c.domain || [], newLabel: c.newLabel || null,
    pick: c.pickRecord ? { domain: c.pickRecord.domain || [] } : null,
    saveAction: c.saveAction || null,
    actions: (c.actions || []).map((a) => ({ m: a.m, asks: (a.asks || []).map((x) => x.kwarg) })),
    lines: c.lines ? { field: c.lines.field, fields: c.lines.fields.map((f) => ({ name: f.name, required: !!f.required, readonly: !!f.readonly })) } : null,
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({ name: f.name, value: f.value, readonly: !!f.readonly, required: !!f.required })) }])),
  by_screen: P03_FORM_CHIPS['M24:__by_screen__'] }));
"""

# What each page captures (the form its "+ New" opens).
CAPTURE = {
    "1": "module",  # an uploaded document
    "2": "M24-form-template",  # the template a transaction generates from
    "3": "module",  # an uploaded document, classified at capture
    "4": "M24-form-controlled",  # a controlled document draft
    "5": "M24-form-envelope",  # a signature envelope with its signers
    "6": "M24-form-hold",  # a legal hold on an existing document
    "7": None,  # packs are filed by the workshop / claim: chip to M31's form
}


@pytest.fixture(scope="module")
def m24(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m24_capture")
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


def _sub(m24, no):
    return next(s for s in m24["subs"] if s["no"] == no)


def _served_actions():
    """{model: {method}} the M24 controller serves (SURFACES literal)."""
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "SURFACES":
            surfaces = ast.literal_eval(node.value)
            return {m: set(cfg.get("actions") or ()) for m, cfg in surfaces.items()}
    raise AssertionError("m24.py no longer declares SURFACES")


def _model_source(model):
    for py in ADDONS.rglob("models/*.py"):
        text = py.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'_name = ["\']%s["\']' % re.escape(model), text):
            return text
    raise AssertionError("no source declares %s" % model)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_every_page_captures_its_own_record(m24, no):
    sub = _sub(m24, no)
    assert sub["create"] == CAPTURE[no], "%s %s offers %s" % (no, sub["title"], sub["create"])
    if CAPTURE[no] is None:
        assert sub["forms"], "%s %s has neither a + New nor a chip" % (no, sub["title"])


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_every_chip_opens_a_form(m24, no):
    for f in _sub(m24, no)["forms"]:
        assert f["opens"], "%s chip %s opens %s" % (no, f["f"], f["id"])


def test_only_the_repository_pages_offer_an_upload(m24):
    """'+ New Document' (the module button) is a manual upload: right on the
    repository and classification pages, wrong where the record is a
    template, a hold or a pack."""
    assert m24["module_create"]["screen"] == "M24-form-document"
    upload = sorted(s["no"] for s in m24["subs"] if s["create"] == "module")
    assert upload == ["1", "3"]


def test_auto_filing_lists_filed_documents_and_captures_templates(m24):
    sub = _sub(m24, "2")
    assert ["res_model", "!=", False] in sub["domain"]
    assert [f["f"] for f in sub["forms"]] == ["Document Template"]


def test_template_form_can_satisfy_the_bilingual_rule(m24):
    """fix.document.template: bilingual defaults True and then name_bn is
    required (_check_bilingual). Without name_bn on the form no template
    could be saved."""
    src = _model_source("fix.document.template")
    assert re.search(r"bilingual = fields\.Boolean\(\s*default=True", src)
    names = {f["name"]: f for f in m24["screens"]["M24-form-template"]["fields"]}
    assert "name_bn" in names and not names["name_bn"]["readonly"]
    assert "bilingual" in names and not names["bilingual"]["readonly"]


def test_versioning_page_is_controlled_documents_only(m24):
    sub = _sub(m24, "4")
    assert ["is_controlled", "=", True] in sub["domain"]
    assert ["is_controlled", "=", True] in m24["screens"]["M24-controlled"]["domain"]
    form = m24["screens"]["M24-form-controlled"]
    flag = next(f for f in form["fields"] if f["name"] == "is_controlled")
    assert flag["value"] is True and not flag["readonly"]
    assert form["newLabel"] == "New Controlled Document"
    assert m24["by_screen"]["M24-controlled"] == "M24-form-controlled"


def test_an_envelope_can_be_given_its_signers(m24):
    """action_send refuses an envelope with no signer; signers join only on
    the envelope form (the signer list refuses + New)."""
    assert "An envelope needs at least one signer" in _model_source("fix.esignature.envelope")
    lines = m24["screens"]["M24-form-envelope"]["lines"]
    assert lines and lines["field"] == "signer_ids"
    by = {f["name"]: f for f in lines["fields"]}
    assert by["partner_id"]["required"] and not by["partner_id"]["readonly"]
    # the signature is stamped by the signer's own act, never typed
    for stamped in ("signed_at", "auth_method"):
        assert by[stamped]["readonly"]
    assert m24["screens"]["M24-audit"]["create"] is False


def test_a_hold_is_placed_through_the_served_method(m24):
    form = m24["screens"]["M24-form-hold"]
    assert form["pick"] and ["legal_hold", "=", False] in form["pick"]["domain"]
    act = form["saveAction"]
    assert act["method"] == "action_legal_hold"
    assert act["kwargs"] == {"matter_ref": "legal_hold_reason"}
    assert "action_legal_hold" in _served_actions()["fix.document"]
    assert "def action_legal_hold(self, matter_ref" in _model_source("fix.document")
    # the matter reference is guarded on the record: an input only through saveAction
    reason = next(f for f in form["fields"] if f["name"] == "legal_hold_reason")
    assert reason["readonly"] and reason["required"]


def test_disposal_is_offered_only_for_expired_unheld_documents(m24):
    form = m24["screens"]["M24-form-dispose"]
    dom = form["pick"]["domain"]
    assert ["legal_hold", "=", False] in dom
    assert ["state", "in", ["expired", "pending_destruction"]] in dom
    assert form["saveAction"]["method"] == "action_dispose"
    assert "action_dispose" in _served_actions()["fix.document"]
    on_page = [f["f"] for f in _sub(m24, "6")["forms"]]
    assert on_page == ["Place Legal Hold", "Dispose of Document", "Retention Policy"]


def test_every_list_action_is_served(m24):
    served = _served_actions()
    bad = [
        "%s %s" % (sid, a["m"])
        for sid, cfg in m24["screens"].items()
        if sid.startswith("M24-")
        for a in cfg["actions"]
        if a["m"] not in served.get(cfg["model"], set())
    ]
    assert not bad, bad


def test_the_document_browser_reaches_hold_and_disposal(m24):
    acts = {a["m"]: a["asks"] for a in m24["screens"]["M24-browser"]["actions"]}
    assert acts.get("action_legal_hold") == ["matter_ref"]
    assert acts.get("action_release_hold") == ["reason"]
    assert "action_dispose" in acts


def test_evidence_packs_chip_to_the_workshop_evidence_form(m24):
    sub = _sub(m24, "7")
    assert ["document_type", "=", "evidence_pack"] in sub["domain"]
    chip = next(f for f in sub["forms"] if f["f"] == "Workshop Evidence Item")
    assert chip["id"] == "M31-form-evidence" and chip["model"] == "fix.workshop.evidence"
    # the workshop factory files its upload as an evidence-pack document
    assert 'document_type="evidence_pack"' in _model_source("fix.workshop.evidence")


@pytest.mark.parametrize("sid", ["M24-browser", "M24-controlled", "M24-holds", "M24-disposal"])
def test_system_written_lists_explain_their_empty_state(m24, sid):
    assert m24["screens"][sid]["empty"]
