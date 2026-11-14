# M35 Marketing Campaigns: every sub-module page captures the record it names
# (capture audit 2026-11-14).
#
# Before (HEAD cc24bf5a):
#   * 2 Audience from Segments offered "+ New Campaign". A campaign's audience
#     was a typed partner filter or a fixed audience type: no campaign could
#     name an M33 segment (BRU-MKT-02), no reach was estimated after
#     suppression (BRU-MKT-03) and there was no holdout (FR-MKT-014).
#   * 3 Journey Orchestration listed behaviour triggers with no trigger chip.
#   * 5 Experimentation let anyone type the experiment's state; there was no
#     start, no conclusion and no winner (FR-MKT-031).
#   * 6 Budget & Attribution had NO capture: spend booked outside the estate
#     could not be recorded (FR-MKT-033, BRU-MKT-11) and the attribution model
#     was no record (BRU-MKT-12).
#   * 7 Portal Advertising had no chip, no advertiser and no run window.
#   * 8 Co-Marketing offered "+ New Campaign"; the campaign form could not name
#     a co-marketing partner, and the report said no partner link existed.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M30/M32 guards' fixture).
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
CONTROLLER = HERE.parent / "controllers" / "a03" / "m35.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a03" / "writable.py"
CAMPAIGN = HERE.parents[2] / "domain" / "b_customer_engagement" / "cd_campaign"

_spec = importlib.util.spec_from_file_location(
    "_estate_pages", HERE / "test_estate_module_pages.py"
)
_estate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_estate)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_MODULE_CREATE, P03_FORM_CHIPS, P03_DATA_SCREENS, P03_REPORT_ROUTES } = M;
function %(create)s
function %(panels)s
const mod = P03_MODULES.M35;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M35', map);
  const panels = fregPanels('M35', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M35:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M35.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, label: create ? create.label : null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M35:' + r] || null })) };
});
const pick = (c) => c.pickRecord ? { cols: c.pickRecord.cols || [], domain: c.pickRecord.domain || [] } : null;
console.log(JSON.stringify({ subs,
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M35-') || id === 'M40-form-rebate').map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).map((t) => t.id), pick: pick(c),
    save: c.saveAction ? { method: c.saveAction.method, kwargs: c.saveAction.kwargs || {} } : null,
    actions: (c.actions || []).map((a) => ({ m: a.m })),
    sections: (c.sections || []).map((s) => ({ tab: s.tab || null })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required,
      choices: f.choices ? f.choices.map((x) => x[0]) : null })) }])),
  by_screen: P03_FORM_CHIPS['M35:__by_screen__'] }));
"""

# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen.
CAPTURES = {
    "1": ["M35-form-campaign"],
    "2": ["M35-form-audience"],
    "3": ["M35-form-journey", "M35-form-trigger"],
    "4": ["M35-form-creative", "M35-form-offer"],
    "5": ["M35-form-experiment", "M35-form-experiment-conclude"],
    "6": ["M35-form-spend", "M35-form-spend-void", "M35-form-attribution-model"],
    "7": ["M35-form-ad"],
    "8": ["M35-form-comarketing", "M40-form-rebate"],
}

RECORDS = {
    "1": "fix.campaign",
    "2": "fix.campaign",
    "3": "fix.campaign.journey",
    "4": "fix.campaign.creative",
    "5": "fix.campaign.experiment",
    "6": "fix.campaign.spend",
    "7": "fix.campaign.ad",
    "8": "fix.campaign",
}

# Forms that act on an EXISTING record and run its workflow method.
PICK_ACTIONS = {
    "M35-form-experiment-conclude": ("action_conclude", {"winner", "result_note"}),
    "M35-form-spend-void": ("action_void", {"void_reason"}),
}
# Forms that pick an existing record and write a few of its fields.
PICK_WRITES = {
    "M35-form-audience": (
        ["state", "=", "draft"],
        {
            "target_audience_type",
            "segment_ids",
            "exclude_segment_ids",
            "holdout_pct",
            "holdout_key",
        },
    ),
    "M35-form-comarketing": (["state", "!=", "completed"], {"partner_ids"}),
}

NEW_MODELS = ("fix.campaign.spend", "fix.attribution.model")


@pytest.fixture(scope="module")
def m35(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m35_capture")
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


def _assigned(path, name):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
        ):
            return node.value
    raise AssertionError("%s defines no %s" % (path.name, name))


def _surfaces():
    out = {}
    value = _assigned(CONTROLLER, "SURFACES")
    for key, conf in zip(value.keys, value.values, strict=True):
        acts = set()
        for k, v in zip(conf.keys, conf.values, strict=True):
            if ast.literal_eval(k) == "actions" and isinstance(v, ast.Set):
                acts = {ast.literal_eval(e) for e in v.elts}
        out[ast.literal_eval(key)] = acts
    return out


def _reports():
    return {ast.literal_eval(k) for k in _assigned(CONTROLLER, "REPORTS").keys}


def _writable():
    out = {}
    value = _assigned(WRITABLE_FILE, "WRITABLE")
    for key, val in zip(value.keys, value.values, strict=True):
        names = set()
        if isinstance(val, ast.Call) and val.args:
            names = set(ast.literal_eval(val.args[0]))
        out[ast.literal_eval(key)] = names
    return out


def _sub(m35, no):
    return next(s for s in m35["subs"] if s["no"] == no)


def test_every_page_is_classified(m35):
    assert sorted(s["no"] for s in m35["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m35, no):
    sub = _sub(m35, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m35, no):
    assert _sub(m35, no)["model"] == RECORDS[no]


def test_each_captured_record_is_listed_on_its_page(m35):
    for sub in m35["subs"]:
        listed = {m35["screens"][s]["model"] for s in sub["screens"] if s in m35["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m35):
    placed = {sid for s in m35["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m35["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m35["screens"].items()
        if sid.startswith("M35-")
        and cfg["kind"] in ("model_list", "table_report")
        and sid not in placed
        and not sid.startswith("M35-rpt-")
    ]
    assert not orphans, orphans


@pytest.mark.parametrize("sid", sorted(PICK_ACTIONS))
def test_pick_actions_run_the_workflow_not_a_write(m35, sid):
    cfg = m35["screens"][sid]
    method, typed_ok = PICK_ACTIONS[sid]
    assert cfg["kind"] == "model_form" and cfg["pick"], sid
    assert cfg["save"] and cfg["save"]["method"] == method, sid
    assert method in _surfaces()[cfg["model"]], "%s is not served" % method
    assert set(cfg["save"]["kwargs"].values()) == typed_ok, sid
    typed = {f["name"] for f in cfg["fields"] if not f["readonly"]}
    assert not typed, "%s lets %s be written directly" % (sid, sorted(typed))


@pytest.mark.parametrize("sid", sorted(PICK_WRITES))
def test_pick_writes_change_only_what_they_name(m35, sid):
    cfg = m35["screens"][sid]
    clause, allowed = PICK_WRITES[sid]
    assert cfg["pick"] and clause in cfg["pick"]["domain"], sid
    typed = {f["name"] for f in cfg["fields"] if not f["readonly"]}
    assert typed == allowed, "%s types %s" % (sid, sorted(typed))
    assert typed <= _writable()[cfg["model"]], sid


def test_the_audience_is_never_a_typed_filter(m35):
    """BRU-MKT-02: no workspace form offers the free partner filter, and the
    audience choice is a governed segment (or everyone)."""
    for sid, cfg in m35["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] != "fix.campaign":
            continue
        names = {f["name"] for f in cfg["fields"]}
        assert "audience_domain" not in names, sid
        for f in cfg["fields"]:
            if f["name"] == "target_audience_type" and not f["readonly"]:
                assert f["choices"] and set(f["choices"]) <= {"segments", "all_customers"}, sid
    assert "audience_domain" not in _writable()["fix.campaign"]


def test_workflow_stamps_are_never_typed(m35):
    stamps = {
        "fix.campaign": {
            "estimated_reach",
            "estimated_at",
            "estimate_breakdown",
            "holdout_partner_ids",
            "attribution_model_id",
            "state",
        },
        "fix.campaign.experiment": {
            "state",
            "winner",
            "result_note",
            "started_at",
            "concluded_at",
            "concluded_by_id",
        },
        "fix.campaign.spend": {"state", "void_reason", "voided_by_id", "voided_at"},
        "fix.attribution.model": {"state", "version", "effective_from", "activated_by_id"},
    }
    writable = _writable()
    for model, names in stamps.items():
        assert not names & writable.get(model, set()), (model, names & writable.get(model, set()))


def test_every_page_report_opens_its_pack(m35):
    reports = _reports()
    for sub in m35["subs"]:
        for r in sub["reports"]:
            assert r["route"], "page %s report %s has no route" % (sub["no"], r["r"])
            assert m35["screens"][r["route"]]["report"] in reports, r


def test_a_list_offering_new_opens_a_form_of_its_own_model(m35):
    for sid, cfg in m35["screens"].items():
        if cfg["kind"] != "model_list" or cfg.get("create") is False or not sid.startswith("M35-"):
            continue
        form = m35["by_screen"].get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m35["screens"][form]["model"] == cfg["model"], sid


def test_every_row_action_is_served(m35):
    surfaces = _surfaces()
    for sid, cfg in m35["screens"].items():
        if not sid.startswith("M35-"):
            continue
        for act in cfg["actions"]:
            assert act["m"] in surfaces[cfg["model"]], "%s %s is not served" % (sid, act["m"])


def test_every_m35_record_is_served(m35):
    surfaces = _surfaces()
    for sid, cfg in m35["screens"].items():
        if sid.startswith("M35-") and cfg["kind"] in ("model_list", "model_form"):
            if cfg["model"] == "fix.partner.rebate":
                continue  # M40's surface serves the fund accruals (one declaration)
            assert cfg["model"] in surfaces, "%s reads %s, which M35 does not serve" % (
                sid,
                cfg["model"],
            )


def test_every_editable_form_field_is_writable(m35):
    writable = _writable()
    for sid, cfg in m35["screens"].items():
        if not sid.startswith("M35-") or cfg["kind"] != "model_form" or cfg["save"]:
            continue
        editable = {f["name"] for f in cfg["fields"] if not f["readonly"]}
        lost = editable - writable.get(cfg["model"], set())
        assert not lost, "%s cannot save %s" % (sid, sorted(lost))


def test_long_forms_are_tabbed(m35):
    for sid, cfg in m35["screens"].items():
        if not sid.startswith("M35-") or cfg["kind"] != "model_form":
            continue
        if len(cfg["fields"]) > 15:
            assert cfg["tabs"], "%s has %d fields and no tabs" % (sid, len(cfg["fields"]))
        for section in cfg["sections"]:
            if cfg["tabs"]:
                assert section["tab"] in cfg["tabs"], sid


def test_new_registers_are_secured_and_fenced():
    acl = (CAMPAIGN / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rows = [line.split(",") for line in acl.splitlines()[1:] if line.strip()]

    def perms(model, group):
        ref = "model_" + model.replace(".", "_")
        return [r[4:8] for r in rows if r[2] == ref and r[3] == group]

    # spend: staff record and void it, never delete it
    assert perms("fix.campaign.spend", "base.group_user") == [["1", "1", "1", "0"]]
    # attribution model: staff read it; only the Marketing Manager configures it
    assert perms("fix.attribution.model", "base.group_user") == [["1", "0", "0", "0"]]
    assert perms("fix.attribution.model", "cd_campaign.group_marketing_manager")
    # the touch ledger is written by the harvest, not by hand
    assert perms("fix.campaign.touch", "base.group_user") == [["1", "0", "0", "0"]]
    rules = (CAMPAIGN / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    assert 'ref="model_fix_campaign_spend"' in rules
