# M39 Subscriptions & Recurring: every sub-module page captures the record the
# spec gives it (capture audit 2026-11-19).
#
# Before (HEAD 742e46bc) only page 1 had a "+ New":
#   * pages 2-7 and 9 listed models whose lists said `create: false`, and pages
#     8 and 10 opted out, so nine pages had no "+";
#   * pages 5 (Usage Rating), 6 (Billing Runs), 8 (Suspend / Cancel / Renew) and
#     10 (Metrics & Forecast) had no chip at all;
#   * the "Billing Schedule" chip opened a BLANK cycle charge: a charge typed
#     there was never invoiced and then blocked the real cycle (one charge per
#     subscription and period);
#   * the "Dunning Step" chip opened a BLANK subscription form, so it created a
#     subscription called a dunning step;
#   * no billing schedule, charge line / usage tariff, billing run, credit /
#     adjustment, pause / renew request or churn record existed to capture.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M29 guard's fixture).
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
const mod = P03_MODULES.M39;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M39', map);
  const panels = fregPanels('M39', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M39:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M39.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, label: create ? create.label : null, forms };
});
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M39-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create === undefined ? null : c.create,
    domain: c.domain || null,
    actions: (c.actions || []).map((a) => a.m),
    lines: c.lines ? { field: c.lines.field, fixed: !!c.lines.fixedRows,
      cols: c.lines.fields.map((f) => ({ name: f.name, readonly: !!f.readonly })) } : null,
    fields: (c.sections || []).flatMap((s) => (s.fields || [])).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required })) }])) }));
"""

# What each page must let a person capture: the page's own "+ New" first,
# then every other record the page covers, by its form screen.
CAPTURES = {
    "1": ["M39-record"],
    "2": ["M39-form-billing-schedule"],
    "3": ["M39-form-line"],
    "4": ["M39-form-proration", "M39-form-line"],
    "5": ["M39-form-usage"],
    "6": ["M39-form-billing-run"],
    "7": ["M39-form-adjustment", "M39-form-proration"],
    "8": ["M39-form-lifecycle"],
    "9": ["M39-form-autopay"],
    "10": ["M39-form-churn"],
}

RECORDS = {
    "1": "fix.subscription",
    "2": "fix.subscription.schedule",
    "3": "fix.subscription.line",
    "4": "fix.subscription.proration",
    "5": "fix.subscription.usage",
    "6": "fix.subscription.billing.run",
    "7": "fix.subscription.adjustment",
    "8": "fix.subscription.lifecycle",
    "9": "fix.subscription.autopay",
    "10": "fix.subscription.churn",
}

# System-written: a person opens an existing one, never a blank one.
NEVER_BLANK = ("M39-form-schedule", "M39-form-dunning")


@pytest.fixture(scope="module")
def m39(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m39_capture")
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


def _surface_actions():
    """SURFACES[model]['actions'] of controllers/a04/m39.py, read without Odoo."""
    tree = ast.parse((HERE.parent / "controllers" / "a04" / "m39.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "SURFACES":
            out = {}
            for key, conf in zip(node.value.keys, node.value.values, strict=True):
                acts = set()
                for k, v in zip(conf.keys, conf.values, strict=True):
                    if ast.literal_eval(k) == "actions" and isinstance(v, ast.Set):
                        acts = {ast.literal_eval(e) for e in v.elts}
                out[ast.literal_eval(key)] = acts
            return out
    return {}


def _sub(m39, no):
    return next(s for s in m39["subs"] if s["no"] == no)


def test_every_page_is_classified(m39):
    assert sorted(s["no"] for s in m39["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m39, no):
    sub = _sub(m39, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)
    for f in sub["forms"]:
        assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m39, no):
    assert _sub(m39, no)["model"] == RECORDS[no]


def test_each_captured_record_is_listed_on_its_page(m39):
    for sub in m39["subs"]:
        listed = {m39["screens"][s]["model"] for s in sub["screens"] if s in m39["screens"]}
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


@pytest.mark.parametrize("form", NEVER_BLANK)
def test_system_written_records_never_open_blank(m39, form):
    """The cycle charge is raised by billing (a typed one was never invoiced and
    blocked the real cycle); the dunning step is the daily ladder's."""
    assert m39["screens"][form]["create"] is False
    for sub in m39["subs"]:
        for f in sub["forms"]:
            if f["id"] == form:
                assert f["opens"] is False


def test_the_cycle_charge_list_still_refuses_new(m39):
    assert m39["screens"]["M39-runs"]["create"] is False


def test_every_new_list_is_in_the_navigation(m39):
    for sid in (
        "M39-schedules",
        "M39-lines",
        "M39-billing-runs",
        "M39-adjustments",
        "M39-lifecycle",
        "M39-churn",
        "M39-usage-exceptions",
    ):
        assert sid in m39["nav"], sid


def test_every_list_action_is_served(m39):
    served = _surface_actions()
    for sid, cfg in m39["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        model = cfg["model"]
        # fix.subscription is served by M53's surface
        if model == "fix.subscription":
            continue
        missing = set(cfg["actions"]) - served.get(model, set())
        assert not missing, "%s offers %s, not served" % (sid, missing)


def test_the_unrated_usage_queue_is_the_exception_state(m39):
    q = m39["screens"]["M39-usage-exceptions"]
    assert q["model"] == "fix.subscription.usage" and q["domain"] == [["state", "=", "exception"]]
    assert "action_rerate" in q["actions"]


def test_usage_reading_carries_its_tariff_and_source_key(m39):
    names = {f["name"] for f in m39["screens"]["M39-form-usage"]["fields"]}
    assert {"line_id", "source_module", "source_key"} <= names
    ro = {f["name"] for f in m39["screens"]["M39-form-usage"]["fields"] if f["readonly"]}
    assert {"overage_quantity", "overage_charge", "state", "charge_id", "exception_cause"} <= ro


def test_a_plan_change_can_be_a_quantity_change(m39):
    fields = {f["name"]: f for f in m39["screens"]["M39-form-proration"]["fields"]}
    assert "line_id" in fields and "new_quantity" in fields
    assert fields["old_quantity"]["readonly"] and fields["amount"]["readonly"]


def test_server_filled_grids_are_read_only(m39):
    sched = m39["screens"]["M39-form-billing-schedule"]["lines"]
    assert sched["field"] == "period_ids" and sched["fixed"]
    assert all(c["readonly"] for c in sched["cols"])
    run = m39["screens"]["M39-form-billing-run"]["lines"]
    assert run["field"] == "unit_ids" and run["fixed"]
    editable = {c["name"] for c in run["cols"] if not c["readonly"]}
    assert editable == {"disposition", "disposition_note"}


def test_decision_stamps_are_never_typed(m39):
    stamps = {
        "M39-form-billing-schedule": {"state", "activated_by_id", "planned_total"},
        "M39-form-line": {"state", "approved_by_id", "amount", "billed_charge_id"},
        "M39-form-billing-run": {
            "state",
            "dry_run_by_id",
            "reviewed_by_id",
            "committed_at",
            "total_amount",
        },
        "M39-form-adjustment": {
            "state",
            "approval_state",
            "applied_charge_id",
            "dofa_tier_required",
        },
        "M39-form-lifecycle": {"state", "approved_by_id", "notice_ok", "notice_required_days"},
        "M39-form-churn": {"lost_mrr", "cohort"},
    }
    for form, names in stamps.items():
        fields = {f["name"]: f for f in m39["screens"][form]["fields"]}
        for name in names:
            assert fields[name]["readonly"], "%s.%s is typed" % (form, name)
