# M28 Integration, API & Events: every sub-module page captures the records it
# covers (capture audit 2026-11-14).
#
# Before:
#   * Subscriptions & DLQ had no capture at all: both of its lists are
#     engine-fed (dead letters), so the page offered nothing, although the
#     subscription (FR-IPF-026) is what the page is about and its form is on
#     the page as a chip.
#   * Offline Sync had no capture: conflicts are raised by the sync engine,
#     and the only human act - deciding a conflict (FR-IPF-049, BRU-IPF-17) -
#     was four row buttons on another list.
#   * Reconciliation listed OFFLINE SYNC CONFLICTS (fix.sync.conflict), not
#     reconciliation runs. The nightly runs, the suppressions and the
#     investigation record (FR-IPF-052, BRU-IPF-19) were on no sub-module
#     page, so the page could capture nothing of its own.
#   * Gateway offered "+ New API Endpoint", the same button as Versioning &
#     Portals: the gateway's own record, the per-consumer rate limit
#     (FR-IPF-004), could not be captured from it.
#   * Allowed Hosts (needed before any webhook or connector may send) and
#     Connector Credentials were on no sub-module page.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M26/M27 guards' fixture).
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
ROOT = HERE.parents[2]

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
const mod = P03_MODULES.M28;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M28', map);
  const forms = fregPanels('M28', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M28:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M28.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, module: !!(create && create.module), forms };
});
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M28-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, cols: c.cols || [],
    pick: !!c.pickRecord, pickDomain: (c.pickRecord && c.pickRecord.domain) || null,
    saveAction: c.saveAction || null,
    actions: (c.actions || []).map((a) => a.m),
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required,
      choices: f.choices || null })) }])),
  by_screen: P03_FORM_CHIPS['M28:__by_screen__'] }));
"""

# What each page must let a person capture: the page's own "+ New" first,
# then every other record the page covers, by its form screen.
CAPTURES = {
    "1": ["M28-form-quota"],
    "2": ["M28-form-endpoint", "M28-form-consumer"],
    "3": ["M28-form-topic", "M28-form-schema"],
    "4": ["M28-form-subscription"],
    "5": ["M28-form-subscription", "M28-form-allowed-host"],
    "6": ["M28-form-connector", "M28-form-credential"],
    "7": ["M28-form-conflict-resolve"],
    "8": ["M28-form-recon-investigation", "M28-form-suppression"],
}

# The record each page lists (its grid), so a capture lands where it was made.
RECORDS = {
    "1": "fix.api.quota",
    "2": "fix.api.endpoint",
    "3": "fix.event.topic",
    "4": "fix.event.dlq",
    "5": "fix.event.subscription",
    "6": "fix.connector",
    "7": "fix.sync.conflict",
    "8": "fix.integration.reconciliation.run",
}


@pytest.fixture(scope="module")
def m28(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m28_capture")
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


def _assigned(name):
    """A top-level dict literal of controllers/a12/m28.py, read without Odoo."""
    tree = ast.parse((HERE.parent / "controllers" / "a12" / "m28.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == name for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("%s not found" % name)


def _sub(m28, no):
    return next(s for s in m28["subs"] if s["no"] == no)


def _fields(m28, screen):
    return {f["name"]: f for f in m28["screens"][screen]["fields"]}


def test_every_page_is_classified(m28):
    assert sorted(s["no"] for s in m28["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m28, no):
    sub = _sub(m28, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m28, no):
    assert _sub(m28, no)["model"] == RECORDS[no]


def test_gateway_and_versioning_no_longer_share_one_button(m28):
    assert _sub(m28, "1")["create"] != _sub(m28, "2")["create"]


def test_reconciliation_shows_runs_and_suppressions_not_sync_conflicts(m28):
    screens = _sub(m28, "8")["screens"]
    assert {"M28-reconciliation", "M28-suppressions"} <= set(screens)
    assert "M28-conflicts" not in screens


def test_the_investigation_picks_an_open_divergence(m28):
    form = m28["screens"]["M28-form-recon-investigation"]
    assert form["model"] == "fix.integration.reconciliation.run"
    assert form["pick"]
    assert ["state", "in", ["divergent", "suppressed"]] in form["pickDomain"]
    assert ["resolved_at", "=", False] in form["pickDomain"]
    assert form["saveAction"]["method"] == "action_resolve"
    assert form["saveAction"]["kwargs"] == {"note": "resolution_note"}
    fields = _fields(m28, "M28-form-recon-investigation")
    assert fields["resolution_note"]["required"]
    editable = {n for n, f in fields.items() if not f["readonly"]}
    assert editable == {"resolution_note"}, "the run's measured figures are evidence"


def test_the_conflict_decision_picks_a_pending_conflict(m28):
    form = m28["screens"]["M28-form-conflict-resolve"]
    assert form["model"] == "fix.sync.conflict"
    assert form["pick"] and form["pickDomain"] == [["resolution", "=", "pending"]]
    assert form["saveAction"]["method"] == "action_resolve_decision"
    assert form["saveAction"]["kwargs"] == {"decision": "resolution", "note": "resolution_note"}
    fields = _fields(m28, "M28-form-conflict-resolve")
    decision = fields["resolution"]
    assert decision["required"]
    assert [c[0] for c in decision["choices"]] == [
        "local_wins",
        "remote_wins",
        "merged",
        "dismissed",
    ], "pending is not a decision"
    evidence = {"device_ref", "res_model", "res_id", "field_name", "local_value", "remote_value"}
    assert all(fields[n]["readonly"] for n in evidence), "the collided values are evidence"


def test_every_working_screen_sits_on_a_page(m28):
    placed = {sid for s in m28["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid, cfg in m28["screens"].items()
        if cfg["kind"] == "model_list" and sid not in placed and sid != "M28-log"
    ]
    assert not orphans, orphans


def test_a_list_offering_new_opens_a_form_of_its_own_model(m28):
    for sid, cfg in m28["screens"].items():
        if cfg["kind"] != "model_list" or cfg.get("create") is False:
            continue
        form = m28["by_screen"].get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m28["screens"][form]["model"] == cfg["model"], sid


def test_engine_raised_lists_still_create_nothing(m28):
    for sid in ("M28-dlq", "M28-replay", "M28-deliveries", "M28-conflicts", "M28-reconciliation"):
        assert m28["screens"][sid]["create"] is False, sid


def test_every_decision_form_runs_a_served_action(m28):
    surfaces = _assigned("SURFACES")
    for sid, cfg in m28["screens"].items():
        act = cfg.get("saveAction")
        if not act:
            continue
        assert act["method"] in surfaces[cfg["model"]]["actions"], sid


def test_every_editable_form_field_is_writable_or_carried_by_its_action(m28):
    """A field a form lets the user type either saves through the write
    whitelist or travels to the form's workflow method - never neither."""
    writable = _assigned("WRITABLE")
    for sid, cfg in m28["screens"].items():
        if cfg["kind"] != "model_form":
            continue
        carried = set((cfg.get("saveAction") or {}).get("kwargs", {}).values())
        editable = {f["name"] for f in cfg["fields"] if not f["readonly"]}
        lost = editable - set(writable[cfg["model"]]) - carried
        assert not lost, "%s cannot save %s" % (sid, sorted(lost))
    assert not {"resolution", "resolution_note"} & set(writable["fix.sync.conflict"])
    assert not {"resolution_note", "state"} & set(writable["fix.integration.reconciliation.run"])


def test_the_decision_method_keeps_the_row_buttons_gates():
    text = (ROOT / "domain/i_governance/cd_itsm/models/fix_integration.py").read_text(
        encoding="utf-8"
    )
    body = text[text.index("def action_resolve_decision") :]
    body = body[: body.index("\n    def ", 10)]
    assert "self._resolve(" in body, "the one-step decision must go through _resolve"
