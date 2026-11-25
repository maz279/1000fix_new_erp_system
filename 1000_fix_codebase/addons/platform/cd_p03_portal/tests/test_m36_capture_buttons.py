# M36 Quotations & Tenders: every sub-module page captures the record it names
# (capture audit 2026-11-14).
#
# Before (HEAD f6fc66cc), evaluated with the engine's own fregCreate/fregPanels:
#   * only page 2 Quotation Object had a "+ New";
#   * 1 Estimate Build-Up and 9 Tender & Bid had a chip but no "+ New" (their
#     lists said create: false);
#   * 3 Versioning, 4 Approval Routing, 5 Customer Approval Loop, 6 Partial
#     Accept & Counter, 7 e-Signature, 8 Declined Handling and 10 Templates
#     captured nothing at all;
#   * 4 and 5 listed the same internal review log; no quotation recorded the
#     channel it reached the customer on (FR-QTE-033/039), so "Quote Conversion
#     by Channel" grouped by state; a counter-offer or a line-level partial
#     acceptance (FR-QTE-035/036) had no record anywhere;
#   * 10 named fix.document.template as its record and placed the tender
#     compliance report; bid bonds and variation orders had no chip and the
#     variation list sat on no page.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M30/M32/M35 fixture).
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
CONTROLLER = HERE.parent / "controllers" / "a04" / "m36.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a04" / "writable.py"
QUOTATION = HERE.parents[2] / "domain" / "c_commercial" / "cd_quotation"

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
const mod = P03_MODULES.M36;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M36', map);
  const panels = fregPanels('M36', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M36:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M36.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, label: create ? create.label : null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M36:' + r] || null })) };
});
const pick = (c) => c.pickRecord ? { cols: c.pickRecord.cols || [], domain: c.pickRecord.domain || [] } : null;
const mine = (id) => id.startsWith('M36-') || id === 'M24-form-template';
console.log(JSON.stringify({ subs, forms: mod.forms,
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => mine(id)).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, report: c.report || null, title: c.title || null,
    tabs: (c.tabs || []).map((t) => t.id), pick: pick(c), domain: c.domain || [],
    save: c.saveAction ? { method: c.saveAction.method, kwargs: c.saveAction.kwargs || {} } : null,
    actions: (c.actions || []).map((a) => ({ m: a.m })),
    sections: (c.sections || []).map((s) => ({ tab: s.tab || null })),
    lines: c.lines ? { field: c.lines.field, fields: (c.lines.fields || []).map((f) => ({ name: f.name, readonly: !!f.readonly })) } : null,
    cols: c.cols || [],
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required,
      choices: f.choices ? f.choices.map((x) => x[0]) : null })) }])),
  by_screen: P03_FORM_CHIPS['M36:__by_screen__'] }));
"""

# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen.
CAPTURES = {
    "1": ["M36-form-estimate"],
    "2": ["M36-record"],
    "3": ["M36-form-revise"],
    "4": ["M36-form-submit"],
    "5": ["M36-form-issue", "M36-form-delivery", "M36-form-otp"],
    "6": ["M36-form-counter-offer", "M36-form-counter-decide"],
    "7": ["M36-form-signed", "M36-form-otp"],
    "8": ["M36-form-decline"],
    "9": ["M36-form-tender", "M36-form-bond", "M36-form-variation"],
    "10": ["M36-form-template", "M24-form-template"],
}

RECORDS = {
    "1": "fix.estimate.line",
    "2": "fix.quotation",
    "3": "fix.quotation",
    "4": "fix.quote.review",
    "5": "fix.quotation.delivery",
    "6": "fix.quotation.counter",
    "7": "fix.quotation",
    "8": "fix.quotation",
    "9": "fix.tender",
    "10": "fix.quotation.template",
}

# Forms that act on an EXISTING quotation and run its workflow method: the
# method, the inputs it takes, and the quotation states it may pick from.
PICK_ACTIONS = {
    "M36-form-revise": ("action_revise", set(), ["state", "in", ["sent", "expired", "declined"]]),
    "M36-form-submit": ("action_submit", {"dofa_justification"}, ["state", "=", "draft"]),
    "M36-form-issue": (
        "action_issue_on_channel",
        {"issue_channel", "issue_recipient", "issue_ref"},
        ["state", "=", "approved"],
    ),
    "M36-form-otp": (
        "action_verify_acceptance_otp",
        {"acceptance_code_entry"},
        ["state", "=", "sent"],
    ),
    "M36-form-signed": (
        "action_record_signed_acceptance",
        {"signed_attachment_id"},
        ["state", "=", "sent"],
    ),
    "M36-form-decline": (
        "action_decline",
        {"decline_reason_code", "decline_reason"},
        ["state", "=", "sent"],
    ),
    "M36-form-counter-decide": (
        "action_decide",
        {"decision_choice", "decision_note"},
        ["state", "=", "requested"],
    ),
}

NEW_MODELS = ("fix.quotation.delivery", "fix.quotation.counter", "fix.quotation.counter.line")

# The channels FR-QTE-033 names, as the delivery record stores them.
CHANNELS = {"portal", "app", "whatsapp", "sms", "email", "counter", "onsite", "phone"}


@pytest.fixture(scope="module")
def m36(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m36_capture")
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


# fix.estimate is served by M01, fix.counter.sale by M04 and fix.document.template
# by M24 (one declaration each)
OWNERS = (
    CONTROLLER,
    HERE.parent / "controllers" / "a02" / "m01.py",
    HERE.parent / "controllers" / "a02" / "m04.py",
    HERE.parent / "controllers" / "a10" / "m24.py",
)


def _surfaces(paths=(CONTROLLER,)):
    out = {}
    for path in paths:
        value = _assigned(path, "SURFACES")
        for key, conf in zip(value.keys, value.values, strict=True):
            acts = set()
            for k, v in zip(conf.keys, conf.values, strict=True):
                if ast.literal_eval(k) == "actions" and isinstance(v, ast.Set):
                    acts = {ast.literal_eval(e) for e in v.elts}
            out.setdefault(ast.literal_eval(key), acts)
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


def _sub(m36, no):
    return next(s for s in m36["subs"] if s["no"] == no)


def test_every_page_is_classified(m36):
    assert sorted(s["no"] for s in m36["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m36, no):
    sub = _sub(m36, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m36, no):
    assert _sub(m36, no)["model"] == RECORDS[no]


def test_each_captured_record_is_listed_on_its_page(m36):
    for sub in m36["subs"]:
        listed = {m36["screens"][s]["model"] for s in sub["screens"] if s in m36["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m36):
    placed = {sid for s in m36["subs"] for sid in s["screens"]}
    placed |= {r["route"] for s in m36["subs"] for r in s["reports"]}
    orphans = [
        sid
        for sid, cfg in m36["screens"].items()
        if sid.startswith("M36-")
        and cfg["kind"] in ("model_list", "table_report")
        and sid not in placed
        and not sid.startswith("M36-rpt-")
    ]
    assert not orphans, orphans


def test_the_two_approval_pages_are_not_the_same_list(m36):
    """4 is 1000FiX's internal approval; 5 is the customer's decision."""
    assert set(_sub(m36, "4")["screens"]).isdisjoint(_sub(m36, "5")["screens"])
    loop = m36["screens"]["M36-loop"]
    assert loop["model"] == "fix.quotation" and ["state", "=", "sent"] in loop["domain"]


def test_compliance_sits_with_the_tender(m36):
    assert "M36-compliance" in _sub(m36, "9")["screens"]
    assert "M36-compliance" not in _sub(m36, "10")["screens"]
    assert "M36-variations" in _sub(m36, "9")["screens"]


@pytest.mark.parametrize("sid", sorted(PICK_ACTIONS))
def test_pick_actions_run_the_workflow_not_a_write(m36, sid):
    cfg = m36["screens"][sid]
    method, inputs, clause = PICK_ACTIONS[sid]
    assert cfg["kind"] == "model_form" and cfg["pick"], sid
    assert clause in cfg["pick"]["domain"], sid
    assert cfg["save"] and cfg["save"]["method"] == method, sid
    assert method in _surfaces()[cfg["model"]], "%s is not served" % method
    assert set(cfg["save"]["kwargs"].values()) == inputs, sid
    typed = {f["name"] for f in cfg["fields"] if not f["readonly"]}
    assert not typed, "%s lets %s be written directly" % (sid, sorted(typed))


def test_the_issue_form_offers_every_channel(m36):
    channel = next(
        f for f in m36["screens"]["M36-form-issue"]["fields"] if f["name"] == "issue_channel"
    )
    assert channel["required"]


def test_the_counter_offer_form_names_its_quotation_and_lines(m36):
    cfg = m36["screens"]["M36-form-counter-offer"]
    assert cfg.get("create") is not False and cfg["model"] == "fix.quotation.counter"
    names = {f["name"]: f for f in cfg["fields"]}
    for req in ("quotation_id", "kind", "channel", "customer_request"):
        assert names[req]["required"], req
    assert cfg["lines"] and cfg["lines"]["field"] == "line_ids"
    editable = {f["name"] for f in cfg["lines"]["fields"] if not f["readonly"]}
    assert editable == {"decision"}, editable


def test_the_old_counter_sale_form_is_not_called_a_counter_offer(m36):
    """The walk-in counter SALE form (M04's fix.counter.sale) was titled
    "Counter-Offer"; a counter-offer is the customer's proposal on a quotation."""
    cfg = m36["screens"].get("M36-form-counter")
    if cfg:
        assert cfg["model"] == "fix.counter.sale"
        assert "offer" not in (cfg["title"] or "").lower(), cfg["title"]


def test_workflow_stamps_are_never_typed(m36):
    stamps = {
        "fix.quotation.delivery": {"recorded_by_id", "version", "customer_id"},
        "fix.quotation.counter": {
            "state",
            "decided_by_id",
            "decided_at",
            "decision_note",
            "revised_quotation_id",
            "recorded_by_id",
        },
        "fix.quotation": {"state", "esign_state", "decline_reason", "delivery_channel"},
    }
    writable = _writable()
    for model, names in stamps.items():
        assert not names & writable.get(model, set()), (model, names & writable.get(model, set()))


def test_every_page_report_opens_its_pack(m36):
    reports = _reports()
    for sub in m36["subs"]:
        for r in sub["reports"]:
            assert r["route"], "page %s report %s has no route" % (sub["no"], r["r"])
            assert m36["screens"][r["route"]]["report"] in reports, r


def test_every_module_form_sits_on_a_page(m36):
    placed = {f["f"] for s in m36["subs"] for f in s["forms"]}
    assert set(m36["forms"]) <= placed, set(m36["forms"]) - placed


def test_a_list_offering_new_opens_a_form_of_its_own_model(m36):
    for sid, cfg in m36["screens"].items():
        if cfg["kind"] != "model_list" or cfg.get("create") is False or not sid.startswith("M36-"):
            continue
        form = m36["by_screen"].get(sid)
        assert form, "%s offers + New but opens no form" % sid
        assert m36["screens"][form]["model"] == cfg["model"], sid


def test_every_row_action_is_served(m36):
    surfaces = _surfaces(OWNERS)
    for sid, cfg in m36["screens"].items():
        if not sid.startswith("M36-"):
            continue
        for act in cfg["actions"]:
            assert act["m"] in surfaces[cfg["model"]], "%s %s is not served" % (sid, act["m"])


def test_every_m36_record_is_served(m36):
    for model in NEW_MODELS[:2]:
        assert model in _surfaces(), model
    surfaces = _surfaces(OWNERS)
    for sid, cfg in m36["screens"].items():
        if sid.startswith("M36-") and cfg["kind"] in ("model_list", "model_form"):
            assert cfg["model"] in surfaces, "%s reads %s, which M36 does not serve" % (
                sid,
                cfg["model"],
            )


def test_every_editable_form_field_is_writable(m36):
    writable = _writable()
    for sid, cfg in m36["screens"].items():
        if not sid.startswith("M36-") or cfg["kind"] != "model_form" or cfg["save"]:
            continue
        if cfg["model"] in ("fix.estimate", "fix.counter.sale"):
            continue  # whitelisted by their owner area (a02)
        editable = {f["name"] for f in cfg["fields"] if not f["readonly"]}
        lost = editable - writable.get(cfg["model"], set())
        assert not lost, "%s cannot save %s" % (sid, sorted(lost))


def test_long_forms_are_tabbed(m36):
    for sid, cfg in m36["screens"].items():
        if not sid.startswith("M36-") or cfg["kind"] != "model_form":
            continue
        if len(cfg["fields"]) > 15:
            assert cfg["tabs"], "%s has %d fields and no tabs" % (sid, len(cfg["fields"]))
        for section in cfg["sections"]:
            if cfg["tabs"]:
                assert section["tab"] in cfg["tabs"], sid


def test_new_registers_are_secured_and_fenced():
    acl = (QUOTATION / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rows = [line.split(",") for line in acl.splitlines()[1:] if line.strip()]

    def perms(model, group):
        ref = "model_" + model.replace(".", "_")
        return [r[4:8] for r in rows if r[2] == ref and r[3] == group]

    for model in NEW_MODELS:
        # everyone reads; nobody but the Commercial Manager deletes
        assert perms(model, "base.group_user") == [["1", "0", "0", "0"]], model
        author = perms(model, "group_quotation_user")
        assert author and author[0][3] == "0", model
    rules = (QUOTATION / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW_MODELS[:2]:
        assert 'ref="model_%s"' % model.replace(".", "_") in rules, model


def test_the_delivery_record_knows_every_channel():
    src = (QUOTATION / "models" / "fix_quote_with_customer.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    channels = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CHANNELS":
            channels = {k for k, _ in ast.literal_eval(node.value)}
    assert channels == CHANNELS
