# M12 Marketplace & Sellers: every sub-module page offers the button that
# captures its record (audit 2026-11-13).
#
# Six of the eleven M12 pages named no form. Agreements & Tiers, Commission &
# Fees, Wallet & Payouts, Execution Oversight, Ratings and Performance
# Consequences offered no button at all. The Chargeback, Marketplace Order and
# Seller Bid forms sat on no page. "Commission Schemes" showed the revenue
# report a second time, although M53's seller commission scheme is what a
# marketplace commission accrues on (and with none in force nothing accrues).
# The Payout Run form let a person type seller statements, which the system
# issues when the run is executed. Performance Consequences had no record to
# capture: probation, suspension and the appeal against them had no store.
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments.
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
ROOT = HERE.parent
SRC = ROOT / "static" / "src"
CONTROLLER = ROOT / "controllers" / "a04" / "m12.py"

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
const mod = P03_MODULES.M12;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M12', map);
  const forms = fregPanels('M12', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M12:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const lists = (map.screens || []).map((id) => ({ id, cfg: P03_DATA_SCREENS[id] || {} }))
    .filter((x) => x.cfg.kind === 'model_list')
    .map((x) => ({ id: x.id, model: x.cfg.model, create: x.cfg.create !== false, empty: !!x.cfg.empty,
      actions: (x.cfg.actions || []).map((a) => a.m) }));
  return { no: s[0], model: map.model || null, domain: map.domain || null, create, forms, lists };
});
const S = P03_DATA_SCREENS;
console.log(JSON.stringify({ forms: mod.forms, subs, screens: Object.fromEntries(
  Object.entries(S).filter(([id]) => id.startsWith('M12-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, pickRecord: c.pickRecord || null,
    saveAction: c.saveAction || null, empty: !!c.empty, domain: c.domain || null,
    lines: c.lines ? { field: c.lines.field, readonlyGrid: !!c.lines.readonlyGrid } : null,
    fields: (c.sections || []).flatMap((x) => x.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, value: f.value === undefined ? null : f.value })),
    actions: (c.actions || []).map((a) => a.m) }])) }));
"""

# How each page's record is captured: 'form' = a "+ New" or a chip that opens
# an in-workspace form (a pick-then-act form counts: it runs the workflow
# step on the record the user picks).
CAPTURE = {
    "1": ("form", "M12-form-seller"),  # Seller Application (the module button)
    "2": ("form", "M08-record"),  # Seller Agreement: M08's contract form, Marketplace family
    "3": ("form", "M12-form-listing"),  # Listing
    "4": ("form", "M12-form-marketplace-order"),  # broadcast a job; Seller Bid chip
    "5": ("form", "M12-form-job-complete"),  # Record Job Completion
    "6": ("form", "M12-form-signoff"),  # Record Customer Sign-off (the rating)
    "7": ("form", "M12-form-consequence"),  # Seller Consequence
    "8": ("form", "M12-form-dispute"),  # Dispute Case; Chargeback chip
    "9": ("form", "M12-form-scheme"),  # Seller Commission Scheme (M53)
    "10": ("form", "M12-form-payout"),  # Payout Run
    "11": ("form", "M12-form-consequence"),  # suspension on a trust finding
}


@pytest.fixture(scope="module")
def m12(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m12_capture")
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


def _sub(m12, no):
    return next(s for s in m12["subs"] if s["no"] == no)


def test_every_page_is_classified(m12):
    assert sorted(s["no"] for s in m12["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m12, no):
    sub = _sub(m12, no)
    _kind, screen = CAPTURE[no]
    create = sub["create"] or {}
    offered = "M12-form-seller" if create.get("module") else create.get("screen")
    assert offered == screen, "page %s: + New opens %s, expected %s" % (no, offered, screen)
    assert sub["forms"], "page %s names no form chip" % no
    for f in sub["forms"]:
        assert f["kind"] == "model_form" and f["opens"], "chip %s on page %s is dead" % (
            f["f"],
            no,
        )


def test_every_module_form_sits_on_a_page(m12):
    on_pages = {f["f"] for s in m12["subs"] for f in s["forms"]}
    assert set(m12["forms"]) <= on_pages, set(m12["forms"]) - on_pages
    for name in ("Chargeback", "Marketplace Order", "Seller Bid"):
        assert name in on_pages


def test_a_record_made_on_a_filtered_page_lands_on_it(m12):
    """The agreement and the scheme start with the page's filter filled in."""
    assert _sub(m12, "2")["create"]["presets"] == {"family": "marketplace"}
    assert _sub(m12, "9")["create"]["presets"] == {"scheme_type": "seller"}
    # and from its own list's "+ New", through the field's starting value
    scheme = {f["name"]: f for f in m12["screens"]["M12-form-scheme"]["fields"]}
    assert scheme["scheme_type"]["value"] == "seller"


def test_commission_schemes_lists_the_seller_schemes(m12):
    screen = m12["screens"]["M12-commission"]
    assert screen["kind"] == "model_list" and screen["model"] == "fix.commission.scheme"
    assert screen["domain"] == [["scheme_type", "=", "seller"]] and screen["empty"]


def test_payout_statements_are_never_typed(m12):
    """fix.seller.statement rows are issued by the run's execution."""
    lines = m12["screens"]["M12-form-payout"]["lines"]
    assert lines["field"] == "statement_ids" and lines["readonlyGrid"]
    from importlib import util

    spec = util.spec_from_file_location("a08w", ROOT / "controllers" / "a08" / "writable.py")
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert "statement_ids" not in mod.WRITABLE["fix.payout.run"]


def test_workflow_step_forms_run_the_real_method(m12):
    done = m12["screens"]["M12-form-job-complete"]
    assert done["pickRecord"]["domain"] == [["state", "=", "in_progress"]]
    assert done["saveAction"]["method"] == "action_complete"
    sign = m12["screens"]["M12-form-signoff"]
    assert sign["pickRecord"]["domain"] == [["state", "=", "completed"]]
    assert sign["saveAction"]["method"] == "action_review"
    assert sign["saveAction"]["kwargs"] == {"rating": "review_rating"}
    # nothing on a step form is written by the generic save
    for screen in (done, sign):
        assert all(f["readonly"] for f in screen["fields"])


def test_scores_stay_measured(m12):
    score = m12["screens"]["M12-seller-score"]
    assert score["create"] is False and score["empty"]
    assert _sub(m12, "6")["create"]["screen"] != "M12-seller-score"


def test_consequence_actions_are_whitelisted():
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    surfaces = next(
        n.value
        for n in tree.body
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SURFACES"
    )
    allowed = ast.literal_eval(surfaces)["fix.seller.consequence"]["actions"]
    assert {
        "action_impose",
        "action_appeal",
        "action_uphold_appeal",
        "action_dismiss_appeal",
        "action_lift",
        "action_cancel",
    } == allowed


def test_list_actions_are_served(m12):
    """Every list button names a method its model's surface whitelists."""
    api = {}
    for area in ("a04", "a08"):
        for f in (ROOT / "controllers" / area).glob("m*.py"):
            tree = ast.parse(f.read_text(encoding="utf-8"))
            for n in tree.body:
                if not (
                    isinstance(n, ast.Assign)
                    and getattr(n.targets[0], "id", "") == "SURFACES"
                    and isinstance(n.value, ast.Dict)
                ):
                    continue
                for key, conf in zip(n.value.keys, n.value.values, strict=False):
                    if not (isinstance(key, ast.Constant) and isinstance(conf, ast.Dict)):
                        continue
                    for k, v in zip(conf.keys, conf.values, strict=False):
                        if isinstance(k, ast.Constant) and k.value == "actions":
                            try:
                                actions = ast.literal_eval(v)
                            except ValueError:
                                actions = set()  # set() - a surface with no actions
                            api.setdefault(key.value, set()).update(actions)
    bad = [
        "%s.%s" % (sid, m)
        for sid, cfg in m12["screens"].items()
        if cfg["kind"] == "model_list"
        for m in cfg["actions"]
        if m not in api.get(cfg["model"], set())
    ]
    assert not bad, bad


def test_m12_does_not_edit_m08_contracts(m12):
    """fix.contract is M08's: one editor, with its amendments, entitlements,
    parties and obligations. M12 lists the Marketplace slice and opens it."""
    own = [sid for sid, c in m12["screens"].items() if c["kind"] == "model_form"]
    assert not [sid for sid in own if m12["screens"][sid]["model"] == "fix.contract"]
    agreements = m12["screens"]["M12-agreement-list"]
    assert agreements["create"] is False and agreements["empty"]
    assert agreements["domain"] == [["family", "=", "marketplace"]]
