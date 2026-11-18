# M10 Loyalty & Rewards: every sub-module page offers the button that captures
# its record (audit 2026-11-13).
#
# Wallet, Vouchers & Coupons and Liability & Breakage showed no button at all.
# Tiers & Enrolment could add a tier but not enrol a member (the enrolment form
# existed, with no chip). Alliance Benefits offered "+ New Tier Configuration".
# Seven working screens - schemes, redemption rules, point types, affiliations,
# cards, campaign hooks, fraud controls - sat on no page, so the schemes,
# redemption rules, point types and affiliations live on fix_real could not be
# reached from the register.
#
# Pass 2 (2026-11-18): the buttons existed but six pages could not capture
# what the spec says they are for, because no model existed: paid membership
# (1), benefit scope (2), the BDT wallet (4 offered a POINTS adjustment),
# voucher batches and stacking (5), referral attribution (6) and the
# period-end liability run Finance publishes (8).
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M02 guard's fixture).
from __future__ import annotations

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
const mod = P03_MODULES.M10;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M10', map);
  const forms = fregPanels('M10', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M10:' + f];
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
console.log(JSON.stringify({ subs,
  nav: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(S).filter(([id]) => id.startsWith('M10-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, back: c.back || null, empty: !!c.empty,
    fields: (c.sections || []).flatMap((s) => s.fields || []).map((f) => ({ name: f.name, value: f.value })) }])) }));
"""

# How each page's record is captured. 'form': a "+ New" or a chip opening an
# in-workspace form. 'system': calculated or written by a workflow, so the
# page offers nothing and every list says where its rows come from.
CAPTURE = {
    "1": "form",  # tier, privilege membership, member enrolment, loyalty card
    "2": "form",  # programme, tier benefit, scheme, redemption rule, point type
    "3": "form",  # points adjustment
    "4": "form",  # BDT wallet transaction (credit, application, payout)
    "5": "form",  # voucher batch, campaign hook, stacking rule
    "6": "form",  # referral code, referral registration
    "7": "form",  # loyalty affiliation (the alliance cohort)
    "8": "form",  # period-end liability run (calculated, then published)
}

# The record each page must be able to capture (pass 2).
PAGE_RECORDS = {
    "1": {"fix.loyalty.membership", "fix.loyalty.account", "fix.loyalty.tier"},
    "2": {"fix.loyalty.benefit", "fix.loyalty.scheme"},
    "4": {"fix.loyalty.wallet.txn"},
    "5": {"fix.loyalty.voucher.batch", "fix.loyalty.stacking.rule", "fix.loyalty.campaign.hook"},
    "6": {"fix.loyalty.referral.code", "fix.loyalty.referral.event"},
    "8": {"fix.loyalty.liability.run"},
}


@pytest.fixture(scope="module")
def m10(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m10_capture")
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


def _sub(m10, no):
    return next(s for s in m10["subs"] if s["no"] == no)


def test_every_page_is_classified(m10):
    assert sorted(s["no"] for s in m10["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_capture(m10, no):
    sub = _sub(m10, no)
    opening = [f for f in sub["forms"] if f["opens"]]
    if CAPTURE[no] == "form":
        assert sub["create"] or opening, "page %s has no + New and no form chip" % no
        for f in sub["forms"]:
            assert f["kind"] == "model_form", "chip %s opens %s" % (f["f"], f["kind"])
    else:
        assert not sub["create"] and not opening, "page %s lets a person type in %s" % (
            no,
            sub["model"],
        )
        assert all(lst["empty"] for lst in sub["lists"]), "page %s: say where rows come from" % no


def test_every_working_screen_sits_on_a_page(m10):
    """A list or report on no page cannot be reached from the register."""
    placed = {sid for s in m10["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid in m10["nav"]
        if m10["screens"].get(sid, {}).get("kind") != "model_form" and sid not in placed
    ]
    assert not orphans, orphans


def test_enrolment_page_enrols_a_member(m10):
    forms = {f["f"]: f for f in _sub(m10, "1")["forms"]}
    assert forms["Member Enrolment"]["model"] == "fix.loyalty.account"
    assert forms["Member Enrolment"]["opens"]
    assert forms["Loyalty Card"]["model"] == "fix.loyalty.card"


def test_benefit_engine_reaches_its_rules(m10):
    sub = _sub(m10, "2")
    assert {"M10-schemes", "M10-burn-rules", "M10-point-types"} <= set(sub["screens"])
    models = {f["model"] for f in sub["forms"] if f["opens"]}
    assert {"fix.loyalty.scheme", "fix.loyalty.burn.rule", "fix.loyalty.point.type"} <= models


@pytest.mark.parametrize("no", sorted(PAGE_RECORDS, key=int))
def test_each_page_captures_its_spec_record(m10, no):
    sub = _sub(m10, no)
    models = {f["model"] for f in sub["forms"] if f["opens"]}
    missing = PAGE_RECORDS[no] - models
    assert not missing, "page %s cannot capture %s" % (no, sorted(missing))


def test_wallet_page_captures_money_not_points(m10):
    """Page 4 offered a POINTS adjustment; the spec's wallet is BDT stored value."""
    sub = _sub(m10, "4")
    assert sub["model"] == "fix.loyalty.wallet"
    assert sub["create"] == "M10-form-wallet-txn"
    assert all(f["model"] != "fix.loyalty.ledger" for f in sub["forms"])
    wallet = m10["screens"]["M10-wallet"]
    assert wallet["model"] == "fix.loyalty.wallet"
    assert wallet["create"] is False and wallet["empty"], "a balance is never typed"
    points = m10["screens"]["M10-points-balances"]
    assert points["create"] is False and points["empty"]


def test_liability_page_runs_the_period_end_calculation(m10):
    sub = _sub(m10, "8")
    assert sub["create"] == "M10-form-liability"
    lst = next(x for x in sub["lists"] if x["id"] == "M10-liability-runs")
    assert {"action_calculate", "action_publish"} <= set(lst["actions"])
    form = m10["screens"]["M10-form-liability"]
    typed = {f["name"] for f in form["fields"]}
    assert "net_liability" in typed  # shown, but the writable whitelist keeps it read-only
    assert "M10-rpt-deferral" in sub["screens"]


def test_voucher_page_issues_batches(m10):
    sub = _sub(m10, "5")
    assert sub["create"] == "M10-form-voucher-batch"
    assert {"M10-voucher-batches", "M10-stacking"} <= set(sub["screens"])


def test_vouchers_are_issued_not_typed(m10):
    sub = _sub(m10, "5")
    assert "M10-hooks" in sub["screens"], "the saved hook must be reachable to Activate it"
    vouchers = m10["screens"]["M10-vouchers"]
    assert vouchers["create"] is False and vouchers["empty"]
    form = m10["screens"]["M10-form-voucher-campaign"]
    assert form["back"] == "M10-hooks"
    reward = next(f for f in form["fields"] if f["name"] == "reward_type")
    assert reward["value"] == "voucher"


def test_alliance_page_captures_an_affiliation_not_a_tier(m10):
    sub = _sub(m10, "7")
    assert sub["model"] == "fix.loyalty.affiliation"
    assert sub["create"] == "M10-form-affiliation"
    assert m10["screens"]["M10-alliance"]["create"] is False


def test_new_records_are_writable_only_through_their_forms():
    """Calculated figures, states and balances never reach the write whitelist."""
    from importlib import util

    spec = util.spec_from_file_location(
        "_a03w", HERE.parent / "controllers" / "a03" / "writable.py"
    )
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    w = mod.WRITABLE
    assert w["fix.loyalty.wallet"] == frozenset()
    for model, forbidden in {
        "fix.loyalty.wallet.txn": {"state", "balance_after", "wallet_id", "dofa_approved"},
        "fix.loyalty.membership": {"state", "started_on", "payment_ref", "deferred_bdt"},
        "fix.loyalty.liability.run": {"net_liability", "gross_liability", "state", "reconciles"},
        "fix.loyalty.referral.event": {"state", "block_reason", "registered_at"},
        "fix.loyalty.voucher.batch": {"state", "issued_at"},
    }.items():
        assert not (w[model] & forbidden), (model, sorted(w[model] & forbidden))
