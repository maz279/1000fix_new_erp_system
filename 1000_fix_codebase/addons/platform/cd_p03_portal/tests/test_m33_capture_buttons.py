# M33 Customer & Party Master: every sub-module page captures the record it
# names (capture audit 2026-11-14).
#
# Before (HEAD cc24bf5a):
#   * 2 Classification offered "+ New Party Role"; the class (Individual /
#     Dealer / Corporate / Government, FR-CPM-003) is the party's own field.
#   * 4 Addresses listed and captured PARTIES. The Address-with-GPS form
#     (FR-CPM-014..016) was a chip only, and fix_real held 0 addresses.
#   * 8 Golden Record & Quality and 12 Status Lifecycle had no capture.
#   * 9 Consent & DSR showed no form chip at all: no data-subject request,
#     transparency notice or withdrawal, and the record of processing
#     (FR-CPM-044, P0) had no register anywhere.
#   * The duplicate form let the match score and factors be typed (T-03),
#     the party form let anyone edit the status and a second credit limit,
#     and the notice form offered a computed 'active' and no purposes.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M32 guard's fixture).
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
CONTROLLER = HERE.parent / "controllers" / "a03" / "m33.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a03" / "writable.py"

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
const mod = P03_MODULES.M33;
const describe = (c) => ({
  kind: c.kind, model: c.model || null, create: c.create, back: c.back || null,
  domain: c.domain || [],
  pick: c.pickRecord ? { cols: c.pickRecord.cols || [], domain: c.pickRecord.domain || [] } : null,
  save: c.saveAction ? { method: c.saveAction.method, kwargs: c.saveAction.kwargs || {} } : null,
  actions: (c.actions || []).map((a) => a.m),
  cols: c.cols || [],
  fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
    name: f.name, readonly: !!f.readonly, required: !!f.required,
    choices: (f.choices || []).map((x) => x[0]) })) });
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M33', map);
  const panels = fregPanels('M33', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M33:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M33.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    cols: map.cols || [], create: own || null, forms };
});
const chipTargets = Object.entries(P03_FORM_CHIPS).filter(([k]) => k.startsWith('M33:') && typeof P03_FORM_CHIPS[k] === 'string').map(([, v]) => v);
const ids = new Set([...Object.keys(P03_DATA_SCREENS).filter((id) => id.startsWith('M33-')), ...chipTargets]);
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries([...ids].filter((id) => P03_DATA_SCREENS[id]).map((id) => [id, describe(P03_DATA_SCREENS[id])])),
  by_screen: P03_FORM_CHIPS['M33:__by_screen__'],
  by_model: P03_FORM_CHIPS['M33:__by_model__'] }));
"""

# What each page lets a person capture: its "+ New" first, then the other
# records the page covers, by their form screen.
CAPTURES = {
    "1": ["M33-form-party", "M33-form-role"],
    "2": ["M33-form-classify", "M33-form-role"],
    "3": ["M33-form-hierarchy"],
    "4": ["M33-form-address", "M33-form-party"],
    "5": ["M33-form-identity"],
    "6": ["M33-form-approval"],
    "7": ["M33-form-duplicate", "M33-form-merge", "M33-form-dedup-job", "M33-form-dedup-rule"],
    "8": ["M33-form-score", "M64-form-goldenrule"],
    "9": [
        "M33-form-consent",
        "M33-form-withdraw",
        "M33-form-dsr",
        "M33-form-transparency",
        "M33-form-processing",
    ],
    "10": ["M33-form-segment"],
    "11": ["M33-form-credit"],
    "12": ["M33-form-party-status", "M33-form-reactivate"],
    "13": ["M33-form-party-import"],
}

# The record each page lists.
RECORDS = {
    "1": "fix.party.role",
    "2": "fix.party.role",
    "3": "fix.party.hierarchy",
    "4": "fix.bd.address",
    "5": "fix.identity.document",
    "6": "fix.registration.approval",
    "7": "fix.party.duplicate",
    "8": "fix.party.quality",
    "9": "fix.consent",
    "10": "fix.segment",
    "11": "fix.credit.profile",
    "12": "res.partner",
    "13": "fix.party.import.batch",
}

# Pick forms that run one workflow method on an existing record, and the
# fields a person types into them (everything else is shown, not typed).
PICK_FORMS = {
    "M33-form-score": ("action_score_quality", set()),
    "M33-form-withdraw": ("action_withdraw", set()),
    "M33-form-party-status": ("action_set_party_status", {"party_status", "status_reason"}),
    "M33-form-reactivate": ("action_reactivate_party", {"status_reason"}),
}


@pytest.fixture(scope="module")
def m33(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m33_capture")
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


def _surfaces():
    """SURFACES of controllers/a03/m33.py (model -> served actions), read without Odoo."""
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "SURFACES"
        ):
            out = {}
            for key, conf in zip(node.value.keys, node.value.values, strict=True):
                acts = set()
                for k, v in zip(conf.keys, conf.values, strict=True):
                    if ast.literal_eval(k) == "actions" and isinstance(v, ast.Set):
                        acts = {ast.literal_eval(e) for e in v.elts}
                out[ast.literal_eval(key)] = acts
            return out
    raise AssertionError("m33.py defines no SURFACES")


def _writable():
    tree = ast.parse(WRITABLE_FILE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == "WRITABLE":
            out = {}
            for key, val in zip(node.value.keys, node.value.values, strict=True):
                names = set()
                if isinstance(val, ast.Call) and val.args:
                    names = set(ast.literal_eval(val.args[0]))
                out[ast.literal_eval(key)] = names
            return out
    raise AssertionError("writable.py defines no WRITABLE")


def _sub(m33, no):
    return next(s for s in m33["subs"] if s["no"] == no)


def _field(cfg, name):
    return next(f for f in cfg["fields"] if f["name"] == name)


def test_every_page_is_classified(m33):
    assert sorted(s["no"] for s in m33["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_what_it_names(m33, no):
    sub = _sub(m33, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    # the page's own list opens its "+ New" form; every other capture is a chip
    missing = [form for form in others if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m33, no):
    assert _sub(m33, no)["model"] == RECORDS[no]


def test_the_address_page_lists_party_addresses(m33):
    sub = _sub(m33, "4")
    listing = m33["screens"]["M33-addresses"]
    assert listing["model"] == "fix.bd.address"
    assert ["party_id", "!=", False] in listing["domain"]
    assert "M33-addresses" in sub["screens"] and "M33-addresses" in m33["nav"]
    form = m33["screens"]["M33-form-address"]
    assert _field(form, "party_id")["required"] and _field(form, "address_tag")["required"]
    assert form["back"] == "M33-addresses"
    assert {"party_id", "is_default", "latitude", "longitude"} <= _writable()["fix.bd.address"]


@pytest.mark.parametrize("sid", sorted(PICK_FORMS))
def test_pick_forms_act_on_an_existing_record_through_its_workflow(m33, sid):
    method, typed_ok = PICK_FORMS[sid]
    cfg = m33["screens"][sid]
    assert cfg["kind"] == "model_form" and cfg["pick"], "%s does not pick a record" % sid
    assert cfg["save"] and cfg["save"]["method"] == method, sid
    assert method in _surfaces()[cfg["model"]], "%s is not served" % sid
    typed = {f["name"] for f in cfg["fields"] if not f["readonly"]}
    assert typed == typed_ok, "%s lets %s be typed" % (sid, sorted(typed))
    for field in cfg["save"]["kwargs"].values():
        assert field in typed, "%s passes %s, which the form does not offer" % (sid, field)


def test_status_change_offers_only_the_restrictive_statuses(m33):
    cfg = m33["screens"]["M33-form-party-status"]
    assert _field(cfg, "party_status")["choices"] == [
        "dormant",
        "blocked",
        "credit_hold",
        "blacklisted",
    ]
    assert cfg["save"]["kwargs"] == {"status": "party_status", "reason": "status_reason"}
    assert ["party_status", "not in", ["merged", "blacklisted"]] in cfg["pick"]["domain"]
    react = m33["screens"]["M33-form-reactivate"]["pick"]["domain"]
    assert ["party_status", "in", ["draft", "dormant", "blocked", "credit_hold"]] in react


def test_classification_sets_the_party_class(m33):
    cfg = m33["screens"]["M33-form-classify"]
    assert cfg["model"] == "res.partner" and cfg["pick"] and not cfg["save"]
    assert _field(cfg, "party_class")["required"] and not _field(cfg, "party_class")["readonly"]
    assert _field(cfg, "party_status")["readonly"]
    assert "party_class" in _writable()["res.partner"]


def test_withdrawal_picks_only_granted_consents(m33):
    assert ["state", "=", "granted"] in m33["screens"]["M33-form-withdraw"]["pick"]["domain"]


def test_the_party_form_no_longer_edits_status_or_a_second_credit_limit(m33):
    cfg = m33["screens"]["M33-form-party"]
    for name in ("party_status", "status_reason", "credit_limit"):
        assert _field(cfg, name)["readonly"], name
    assert "credit_limit" not in _writable()["res.partner"]


def test_a_duplicate_score_is_measured_not_typed(m33):
    cfg = m33["screens"]["M33-form-duplicate"]
    assert _field(cfg, "score")["readonly"] and _field(cfg, "factors")["readonly"]
    assert not {"score", "factors"} & _writable()["fix.party.duplicate"]


def test_consent_forms_require_the_notice_and_the_proof(m33):
    cfg = m33["screens"]["M33-form-consent"]
    assert _field(cfg, "notice_version_id")["required"] and _field(cfg, "proof")["required"]
    notice = m33["screens"]["M33-form-transparency"]
    for name in ("text_en", "text_bn", "purpose_set"):
        assert _field(notice, name)["required"], name
    assert _field(notice, "active")["readonly"]
    assert "active" not in _writable()["fix.transparency.notice"]


def test_the_dedup_rule_form_states_what_a_match_does(m33):
    assert _field(m33["screens"]["M33-form-dedup-rule"], "action")["required"]


def test_the_processing_record_is_a_served_register(m33):
    assert "fix.processing.record" in _surfaces()
    listing = m33["screens"]["M33-processing"]
    assert listing["model"] == "fix.processing.record"
    assert m33["by_screen"]["M33-processing"] == "M33-form-processing"
    assert m33["by_model"]["fix.processing.record"] == "M33-form-processing"
    form = m33["screens"]["M33-form-processing"]
    for name in ("party_id", "purpose", "lawful_basis", "categories", "retention_months"):
        assert _field(form, name)["required"], name
    # the system's own source stamp is never typed
    assert "source" not in {f["name"] for f in form["fields"]}
    assert "source" not in _writable()["fix.processing.record"]


def test_survivorship_is_m64s_golden_rule_form(m33):
    cfg = m33["screens"]["M64-form-goldenrule"]
    assert cfg["kind"] == "model_form" and cfg["model"] == "fix.mdm.golden.rule"


def test_new_screens_are_on_the_nav_and_on_a_page(m33):
    placed = {sid for s in m33["subs"] for sid in s["screens"]}
    for sid in ("M33-addresses", "M33-processing"):
        assert sid in m33["nav"] and sid in placed, sid
    for sid in PICK_FORMS:
        assert sid in m33["nav"], sid


def test_a_list_offering_new_opens_a_form_of_its_own_model(m33):
    for sid, cfg in m33["screens"].items():
        if cfg["kind"] != "model_list" or cfg.get("create") is not True:
            continue
        form = m33["by_screen"].get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m33["screens"][form]["model"] == cfg["model"], sid
