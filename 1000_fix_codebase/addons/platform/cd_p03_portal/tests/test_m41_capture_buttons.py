# M41 Warehouse Management: every sub-module page captures the record it names
# (capture audit 2026-11-14).
#
# Before (HEAD 54dd2ae3), evaluated with the engine's own fregCreate/fregPanels:
#   * 5 Picking, 7 Replenishment, 8 RF Execution and 9 Labour & Analytics had
#     no "+ New" and no form chip at all (their mappings said create: false);
#   * 2 Slotting had a "+ New" but no chip; 1, 4 and 6 had a chip for only one
#     of the records they list (no zone, warehouse, wave or staging chip);
#   * the zone list and the pick-line list (the only place a pick is scanned)
#     sat on no page; wave templates and packing stations had a form but no
#     list anywhere;
#   * a "replenish" task completed without moving anything, no bin-to-bin move
#     existed, a bin holding less than the ledger could not be reported short,
#     no operative profile, handling equipment or RF device existed (FR-WMS-028,
#     029, 024, 039, T-15) - the spec's §10.1 floor records.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M36 fixture).
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
CONTROLLER = HERE.parent / "controllers" / "a06" / "m41.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a06" / "writable.py"
INVENTORY = HERE.parents[2] / "domain" / "e_supply_chain" / "cd_inventory"

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
const mod = P03_MODULES.M41;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M41', map);
  const panels = fregPanels('M41', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M41:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M41.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M41:' + r] || null })) };
});
const pick = (c) => c.pickRecord ? { cols: c.pickRecord.cols || [], domain: c.pickRecord.domain || [] } : null;
const mine = (id) => id.startsWith('M41-') || id === 'M15-form-receipt';
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => mine(id)).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null, title: c.title || null,
    pick: pick(c), domain: c.domain || [],
    save: c.saveAction ? { method: c.saveAction.method, kwargs: c.saveAction.kwargs || {} } : null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) }])) }));
"""

# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen.
CAPTURES = {
    "1": ["M41-form-bin", "M41-form-zone", "M41-form-warehouse"],
    "2": ["M41-form-slot"],
    "3": ["M41-form-putaway", "M41-form-dock", "M15-form-receipt"],
    "4": ["M41-form-wave", "M41-form-template"],
    "5": ["M41-form-scan-pick", "M41-form-short-pick"],
    "6": ["M41-form-carton", "M41-form-stage", "M41-form-station"],
    "7": ["M41-form-move", "M41-form-move-confirm"],
    "8": ["M41-form-task-scan", "M41-form-claim", "M41-form-task", "M41-form-device"],
    "9": ["M41-form-operative", "M41-form-equipment", "M41-form-floor-count"],
}

RECORDS = {
    "1": "fix.warehouse.bin",
    "2": "fix.wms.slot",
    "3": "fix.wms.putaway",
    "4": "fix.wms.wave",
    "5": "fix.wms.wave.line",
    "6": "fix.wms.carton",
    "7": "fix.wms.move",
    "8": "fix.wms.task",
    "9": "fix.wms.operative",
}

# Forms that act on an EXISTING record through its workflow method: the
# method, the inputs it takes, and the clause that limits what can be picked.
PICK_ACTIONS = {
    "M41-form-scan-pick": (
        "action_scan_pick",
        {"scan_bin_entry", "scan_item_entry", "scan_serial_entry"},
        ["state", "=", "pending"],
    ),
    "M41-form-short-pick": (
        "action_scan_short_pick",
        {"scan_bin_entry", "found_qty_entry", "scan_item_entry"},
        ["state", "=", "pending"],
    ),
    "M41-form-move-confirm": (
        "action_confirm",
        {"scan_from_entry", "scan_to_entry", "scan_item_entry"},
        ["state", "=", "open"],
    ),
    "M41-form-task-scan": ("action_done", {"scan_entry"}, ["state", "=", "assigned"]),
    "M41-form-claim": ("action_claim", set(), ["state", "=", "open"]),
}

NEW_MODELS = ("fix.wms.move", "fix.wms.operative", "fix.wms.equipment", "fix.wms.device")


@pytest.fixture(scope="module")
def m41(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m41_capture")
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


def _writable():
    out = {}
    value = _assigned(WRITABLE_FILE, "WRITABLE")
    for key, val in zip(value.keys, value.values, strict=True):
        names = set()
        if isinstance(val, ast.Call) and val.args:
            names = set(ast.literal_eval(val.args[0]))
        out[ast.literal_eval(key)] = names
    return out


def _model_methods():
    """{model: {method names}} defined in cd_inventory's model files."""
    out = {}
    for path in (INVENTORY / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            names = set()
            for stmt in cls.body:
                if (
                    isinstance(stmt, ast.Assign)
                    and isinstance(stmt.targets[0], ast.Name)
                    and stmt.targets[0].id in ("_name", "_inherit")
                    and isinstance(stmt.value, ast.Constant)
                ):
                    names.add(stmt.value.value)
            methods = {f.name for f in cls.body if isinstance(f, ast.FunctionDef)}
            for name in names:
                out.setdefault(name, set()).update(methods)
    return out


def _sub(m41, no):
    return next(s for s in m41["subs"] if s["no"] == no)


def test_every_page_is_classified(m41):
    assert sorted(s["no"] for s in m41["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m41, no):
    sub = _sub(m41, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m41, no):
    assert _sub(m41, no)["model"] == RECORDS[no]


def test_each_captured_record_is_listed_on_its_page(m41):
    for sub in m41["subs"]:
        listed = {m41["screens"][s]["model"] for s in sub["screens"] if s in m41["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m41):
    placed = {sid for s in m41["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m41["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m41["screens"].items()
        if sid.startswith("M41-")
        and cfg["kind"] in ("model_list", "table_report")
        and sid not in placed
        and not sid.startswith("M41-rpt-")
    ]
    assert not orphans, orphans


@pytest.mark.parametrize("sid", sorted(PICK_ACTIONS))
def test_pick_actions_run_the_workflow_not_a_write(m41, sid):
    cfg = m41["screens"][sid]
    method, inputs, clause = PICK_ACTIONS[sid]
    assert cfg["kind"] == "model_form" and cfg["pick"], sid
    assert clause in cfg["pick"]["domain"], sid
    assert cfg["save"] and cfg["save"]["method"] == method, sid
    assert method in _surfaces()[cfg["model"]], "%s is not served" % method
    assert set(cfg["save"]["kwargs"].values()) == inputs, sid
    typed = {f["name"] for f in cfg["fields"] if not f["readonly"]}
    assert not typed, "%s lets %s be written directly" % (sid, sorted(typed))


def test_every_served_action_exists_on_its_model():
    methods = _model_methods()
    for model, acts in _surfaces().items():
        if model not in methods:
            continue  # served from another addon (stock location, spare part...)
        missing = acts - methods[model]
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m41):
    surfaces = _surfaces()
    for sid, cfg in m41["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces.get(cfg["model"], set())
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m41, model):
    assert model in _surfaces()
    forms = [
        c for c in m41["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    assert _writable()[model] == typed


def test_the_ledger_and_evidence_are_never_typed(m41):
    """BRU-WMS-01: no form types a bin quantity, a move's state or its scans."""
    never = {
        "fix.wms.move": {
            "state",
            "done_by_id",
            "done_at",
            "scanned_from",
            "scanned_to",
            "scanned_item",
            "task_id",
            "trigger_qty",
        },
        "fix.wms.slot": {"qty", "reserved_qty", "state"},
        "fix.wms.device": {
            "state",
            "enrolled_at",
            "enrolled_by_id",
            "last_seen_at",
            "deactivation_reason",
        },
        "fix.wms.task": {"state", "move_id", "done_at", "done_by_id"},
        "fix.wms.wave.line": {"picked_qty", "reserved_qty", "state", "scanned_bin", "scanned_item"},
    }
    writable = _writable()
    for model, fields in never.items():
        assert not (writable.get(model, set()) & fields), (model, writable[model] & fields)


def test_the_short_pick_list_action_takes_what_was_found(m41):
    acts = {a["m"]: a for a in m41["screens"]["M41-pick-lines"]["actions"]}
    assert set(acts["action_scan_short_pick"]["kwargs"]) == {"bin_code", "found_qty", "item_code"}
    assert "action_raise_replenishment" in {
        a["m"] for a in m41["screens"]["M41-slotting"]["actions"]
    }
    assert "action_claim" in {a["m"] for a in m41["screens"]["M41-tasks"]["actions"]}


def test_new_models_are_secured():
    acl = (INVENTORY / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (INVENTORY / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS:
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        # nobody may delete; a plain employee only reads
        assert all(r[-1].strip() == "0" for r in rows), model
        plain = [r for r in rows if r[3] == "base.group_user"]
        assert plain and plain[0][4:8] == ["1", "0", "0", "0"], model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model


def test_the_new_file_loads_after_the_models_it_extends():
    init = (INVENTORY / "models" / "__init__.py").read_text(encoding="utf-8")
    assert init.index("fix_wms_ops,") < init.index("fix_wms_ops_floor,")


def test_every_screen_on_a_page_has_a_navigation_label(m41):
    """A list that sits on a page but in no navigation group shows as its raw
    id ("M41-devices") in the page's screen chips."""
    labelled = set(m41["labelled"])
    unlabelled = sorted(
        sid
        for sub in m41["subs"]
        for sid in sub["screens"]
        if sid in m41["screens"]
        and m41["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled
