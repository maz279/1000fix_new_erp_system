# M61 Knowledge & Technical Library: every sub-module page captures each
# record it covers (capture audit 2026-11-18).
#
# Before (HEAD 32e24dc9), evaluated with the engine's own fregCreate/fregPanels:
#   * page 1 (Authoring & Versioning) offered the article only: no field
#     capture (FR-KMS-023/024/027), no review request - its "Review Workflow"
#     list re-listed articles with a Publish button asking for a reviewer's
#     numeric user ID - and no version history (FR-KMS-007);
#   * page 3 (Technical Library) captured nothing: its list showed articles
#     (create: false), there was no library entry with a file, a brand/model
#     index or licence terms (FR-KMS-004, BRU-KMS-16), and the media form
#     existed on no chip;
#   * page 4 (Search & Surfacing) captured nothing: no operational link to
#     fault codes, models or brands (FR-KMS-006/015);
#   * page 5 (Offline Distribution) captured nothing: no technician offline
#     set with a scope and a storage budget (FR-KMS-017/018);
#   * page 6 (Feedback & Health) offered "+ New Article": no usefulness
#     feedback (FR-KMS-030), and the usefulness tile divided by a view
#     counter that nothing increments;
#   * page 8 (Expertise Mapping) offered "+ New Article" over a list of
#     articles: the expertise map is derived (FR-KMS-035), never typed.
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
CONTROLLER = HERE.parent / "controllers" / "a10" / "m61.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a10" / "writable.py"
KMS = HERE.parents[2] / "domain" / "i_governance" / "cd_knowledge"

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
const mod = P03_MODULES.M61;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M61', map);
  const panels = fregPanels('M61', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M61:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M61.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, report: map.report || null,
    screens: map.screens || [], create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M61:' + r] || null })) };
});
const screen = (c) => ({
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null,
    tabs: (c.tabs || []).length, lines: c.lines ? c.lines.field : null,
    lineFields: c.lines ? c.lines.fields.map((f) => f.name) : [],
    actions: (c.actions || []).map((a) => ({ m: a.m, kwargs: (a.asks || []).map((q) => q.kwarg).concat(a.kwarg ? [a.kwarg] : []) })),
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) });
console.log(JSON.stringify({ subs, forms: mod.forms,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M61-')).map(([id, c]) => [id, screen(c)])) }));
"""


@pytest.fixture(scope="module")
def m61(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m61_capture")
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


def _report_keys():
    value = _assigned(CONTROLLER, "REPORTS")
    return {ast.literal_eval(k) for k in value.keys}


def _writable():
    out = {}
    value = _assigned(WRITABLE_FILE, "WRITABLE")
    for key, val in zip(value.keys, value.values, strict=True):
        names = set()
        if isinstance(val, ast.Call) and val.args:
            names = set(ast.literal_eval(val.args[0]))
        out[ast.literal_eval(key)] = names
    return out


def _model_classes():
    """{model: ({fields}, {methods})} defined or extended in cd_knowledge."""
    out = {}
    for path in (KMS / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            names, flds = set(), set()
            for stmt in cls.body:
                if not (isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name)):
                    continue
                target = stmt.targets[0].id
                if target in ("_name", "_inherit") and isinstance(stmt.value, ast.Constant):
                    names.add(stmt.value.value)
                elif (
                    isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Attribute)
                    and getattr(stmt.value.func.value, "id", "") == "fields"
                ):
                    flds.add(target)
            methods = {f.name for f in cls.body if isinstance(f, ast.FunctionDef)}
            for name in names:
                entry = out.setdefault(name, (set(), set()))
                entry[0].update(flds)
                entry[1].update(methods)
    return out


# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen. Page 8 is derived: nothing.
CAPTURES = {
    "1": ["M61-form-article", "M61-form-capture", "M61-form-review"],
    "2": ["M61-form-tree", "M61-form-review", "M61-form-link"],
    "3": ["M61-form-library", "M61-form-media"],
    "4": ["M61-form-link"],
    "5": ["M61-form-offline-set"],
    "6": ["M61-form-feedback"],
    "7": ["M61-form-bulletin", "M61-form-recipient"],
    "8": [],
}

NEW_MODELS = (
    "fix.knowledge.capture",
    "fix.knowledge.review",
    "fix.knowledge.library",
    "fix.knowledge.link",
    "fix.knowledge.offline.set",
    "fix.knowledge.feedback",
)
ALL_NEW = (*NEW_MODELS, "fix.knowledge.article.version", "fix.knowledge.tree.node")

# What a form must never let a person type: the state, every decision stamp
# and every measured or answered figure.
NEVER_TYPED = {
    "fix.knowledge.capture": {
        "name",
        "state",
        "captured_by_id",
        "captured_on",
        "reviewer_id",
        "taken_on",
        "article_id",
        "handled_on",
    },
    "fix.knowledge.review": {
        "name",
        "state",
        "requested_by_id",
        "requested_on",
        "content_hash",
        "safety_required",
        "comments",
        "decided_on",
        "safety_approved_by_id",
        "safety_approved_on",
        "content_changed",
    },
    "fix.knowledge.library": {
        "state",
        "offline_allowed",
        "made_available_by_id",
        "made_available_on",
        "withdrawn_reason",
    },
    "fix.knowledge.link": {"link_type", "linked_by_id"},
    "fix.knowledge.offline.set": {
        "name",
        "article_ids",
        "article_count",
        "stale_count",
        "total_mb",
        "over_budget_count",
        "computed_on",
        "computed_by_id",
        "last_synced_on",
    },
    "fix.knowledge.feedback": {"version", "user_id", "captured_on"},
    "fix.knowledge.article": {
        "state",
        "version",
        "content_hash",
        "reviewed_by_id",
        "reviewed_on",
        "owner_id",
        "contributor_id",
        "capture_id",
        "original_capture_text",
        "feedback_count",
        "avg_rating",
        "resolution_rate",
        "flagged_on",
        "flag_reason",
        "review_status",
        "views",
        "helpful_votes",
    },
    "fix.knowledge.tree": {"state", "reviewed_by_id", "reviewed_on", "node_count"},
    "fix.knowledge.article.version": {"version", "content", "content_hash", "changed_by_id"},
}


def _sub(m61, no):
    return next(s for s in m61["subs"] if s["no"] == no)


def test_every_page_is_classified(m61):
    assert sorted(s["no"] for s in m61["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m61, no):
    sub = _sub(m61, no)
    wanted = CAPTURES[no]
    if not wanted:
        assert sub["create"] is None and not [f for f in sub["forms"] if f["opens"]], sub
        return
    own, *others = wanted
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]} | {sub["create"]}
    missing = [form for form in wanted if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


def test_feedback_and_expertise_pages_no_longer_offer_an_article(m61):
    assert _sub(m61, "6")["create"] == "M61-form-feedback"
    assert _sub(m61, "6")["model"] == "fix.knowledge.feedback"
    expertise = _sub(m61, "8")
    assert expertise["create"] is None and expertise["report"] == "expertise_map"


def test_the_library_page_lists_library_entries_not_articles(m61):
    assert m61["screens"]["M61-manuals"]["model"] == "fix.knowledge.library"
    assert _sub(m61, "3")["model"] == "fix.knowledge.library"


def test_the_review_page_lists_review_requests(m61):
    assert m61["screens"]["M61-review"]["model"] == "fix.knowledge.review"


def test_publish_no_longer_asks_for_a_typed_reviewer_id(m61):
    for sid in ("M61-articles", "M61-trees"):
        acts = {a["m"]: a for a in m61["screens"][sid]["actions"]}
        assert acts["action_publish"]["kwargs"] == [], sid


def test_each_captured_record_is_listed_on_its_page(m61):
    for sub in m61["subs"]:
        listed = {m61["screens"][s]["model"] for s in sub["screens"] if s in m61["screens"]}
        listed.add(sub["model"])
        captures = list(sub["forms"])
        if sub["create"]:
            captures.append({"model": m61["screens"][sub["create"]]["model"]})
        for f in captures:
            # a review or link captured beside a tree is listed on page 1 / 4
            if sub["no"] == "2" and f["model"] in ("fix.knowledge.review", "fix.knowledge.link"):
                continue
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_creatable_list_on_a_page_has_its_capture(m61):
    for sub in m61["subs"]:
        captured = {f["model"] for f in sub["forms"] if f["opens"]}
        if sub["create"]:
            captured.add(m61["screens"][sub["create"]]["model"])
        for sid in sub["screens"]:
            cfg = m61["screens"].get(sid, {})
            if cfg.get("kind") == "model_list" and cfg.get("create") is not False:
                assert cfg["model"] in captured, "page %s lists %s (%s) with no capture" % (
                    sub["no"],
                    cfg["model"],
                    sid,
                )


def test_every_working_screen_sits_on_a_page(m61):
    placed = {sid for s in m61["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m61["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m61["screens"].items()
        if cfg["kind"] in ("model_list", "table_report") and sid not in placed
    ]
    assert not orphans, orphans


def test_every_screen_on_a_page_has_a_navigation_label(m61):
    labelled = set(m61["labelled"])
    unlabelled = sorted(
        sid
        for sub in m61["subs"]
        for sid in sub["screens"]
        if sid in m61["screens"] and sid not in labelled
    )
    assert not unlabelled, unlabelled


def test_every_report_is_routed_and_computed(m61):
    keys = _report_keys()
    for sub in m61["subs"]:
        for r in sub["reports"]:
            assert r["route"], "page %s report %s has no screen" % (sub["no"], r["r"])
            assert m61["screens"][r["route"]]["report"] in keys, r
        if sub["report"]:
            assert sub["report"] in keys, sub


def test_every_served_action_exists_on_its_model():
    classes = _model_classes()
    for model, acts in _surfaces().items():
        methods = classes.get(model, (set(), set()))[1]
        missing = acts - methods
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m61):
    surfaces = _surfaces()
    for sid, cfg in m61["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces[cfg["model"]]
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


def test_every_list_column_exists_on_its_model(m61):
    """A column the model lacks is dropped silently by the endpoint."""
    classes = _model_classes()
    for sid, cfg in m61["screens"].items():
        if cfg["kind"] != "model_list" or cfg["model"] not in classes:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "display_name"}
        unknown = [c for c in cfg["cols"] if c not in known]
        assert not unknown, "%s lists %s, not fields of %s" % (sid, unknown, cfg["model"])


def test_every_form_field_exists_on_its_model(m61):
    classes = _model_classes()
    for sid, cfg in m61["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in classes:
            continue
        known = classes[cfg["model"]][0] | {"name", "state", "active"}
        unknown = [f["name"] for f in cfg["fields"] if f["name"] not in known]
        assert not unknown, "%s shows %s, not fields of %s" % (sid, unknown, cfg["model"])
        if cfg["lines"]:
            child = {
                "node_ids": "fix.knowledge.tree.node",
            }[cfg["lines"]]
            unknown = [n for n in cfg["lineFields"] if n not in classes[child][0]]
            assert not unknown, "%s grid shows %s, not fields of %s" % (sid, unknown, child)


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m61, model):
    assert model in _surfaces()
    forms = [
        c for c in m61["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert forms, "%s has no workspace form" % model
    typed = {f["name"] for c in forms for f in c["fields"] if not f["readonly"]}
    typed |= {c["lines"] for c in forms if c["lines"]}
    assert _writable()[model] == typed


@pytest.mark.parametrize("model", sorted(NEVER_TYPED))
def test_stamps_and_measured_figures_are_never_typed(model):
    leaked = _writable().get(model, set()) & NEVER_TYPED[model]
    assert not leaked, (model, sorted(leaked))


def test_the_tree_form_edits_its_decision_steps(m61):
    assert m61["screens"]["M61-form-tree"]["lines"] == "node_ids"
    assert "node_ids" in _writable()["fix.knowledge.tree"]


def test_forms_over_fifteen_fields_are_tabbed(m61):
    """AGENTS.md: a form of more than 15 fields is split into tabs."""
    for sid, cfg in m61["screens"].items():
        if cfg["kind"] == "model_form" and len(cfg["fields"]) > 15:
            assert cfg["tabs"] >= 2, sid


def test_decisions_ask_for_their_reason(m61):
    for sid, method, kwarg in (
        ("M61-review", "action_return", "note"),
        ("M61-manuals", "action_withdraw", "reason"),
        ("M61-captures", "action_merge", "article_ref"),
    ):
        acts = {a["m"]: a for a in m61["screens"][sid]["actions"]}
        assert acts[method]["kwargs"] == [kwarg], sid


def test_new_models_are_secured():
    acl = (KMS / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (KMS / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    own = (KMS / "security" / "fix_m61_capture_rules.xml").read_text(encoding="utf-8")
    rows = [r.split(",") for r in acl.splitlines()[1:] if r.strip()]
    for model in ALL_NEW:
        xmlid = "model_" + model.replace(".", "_")
        assert [r for r in rows if r[2] == xmlid], "%s has no ACL" % model
        assert 'ref="%s"' % xmlid in rules, "%s has no company rule" % model
    assert 'ref="model_fix_knowledge_offline_set"' in own
    user = {r[2]: r[4:8] for r in rows if r[3] == "base.group_user"}
    # evidence is never deleted; versions are never typed; feedback is kept as given
    for xmlid in (
        "model_fix_knowledge_capture",
        "model_fix_knowledge_review",
        "model_fix_knowledge_feedback",
        "model_fix_knowledge_article_version",
    ):
        assert user[xmlid][3] == "0", xmlid
    assert user["model_fix_knowledge_article_version"] == ["1", "0", "0", "0"]
    assert user["model_fix_knowledge_feedback"][1] == "0"
    # library entries and offline sets are the technical library owner's
    assert user["model_fix_knowledge_library"] == ["1", "0", "0", "0"]
    assert user["model_fix_knowledge_offline_set"] == ["1", "0", "0", "0"]


def test_the_new_file_loads_after_the_models_it_extends():
    init = (KMS / "models" / "__init__.py").read_text(encoding="utf-8")
    line = next(x for x in init.splitlines() if x.startswith("from . import"))
    names = [n.strip() for n in line.split("import", 1)[1].split(",")]
    assert names[-1] == "fix_m61_capture", names
    manifest = (KMS / "__manifest__.py").read_text(encoding="utf-8")
    assert '"cd_service_order"' in manifest
