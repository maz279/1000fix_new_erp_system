# M38 E-Commerce Storefront: every sub-module page captures its own record
# (capture audit 2026-11-19).
#
# Before: Storefront & Browse, Cart, Checkout & Payments, Online Orders and
# Recovery & Analytics offered no "+ New" at all; Merchandising and Stock
# Exposure offered "+ New Graded Stock Item" (a unit M14 grades and M15
# stocks); B2B Commerce listed storefront RETURNS. The spec's entities behind
# those pages (content, collections, COD eligibility, order modification,
# exposure policy, return policy, corporate commerce, cart recovery, service
# booking) had no model.
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
CONTROLLER = ROOT / "controllers" / "a04" / "m38.py"

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
const mod = P03_MODULES.M38;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M38', map);
  const forms = fregPanels('M38', mod, map).forms.map((f) => {
    const id = P03_FORM_CHIPS['M38:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord || !!cfg.pick) };
  });
  return { no: s[0], model: map.model || null, create, forms, screens: map.screens || [] };
});
const S = P03_DATA_SCREENS;
console.log(JSON.stringify({ forms: mod.forms, subs, screens: Object.fromEntries(
  Object.entries(S).filter(([id]) => id.startsWith('M38-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, empty: !!c.empty, domain: c.domain || null,
    lines: c.lines ? { field: c.lines.field, fields: c.lines.fields.map((f) => ({ name: f.name, readonly: !!f.readonly })) } : null,
    fields: (c.sections || []).flatMap((x) => x.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly })),
    actions: (c.actions || []).map((a) => a.m) }])) }));
"""

# page -> (the form its "+ New" opens, the model that form captures)
CAPTURE = {
    "1": ("M38-form-content", "fix.storefront.content"),
    "2": ("M38-form-collection", "fix.storefront.collection"),
    "3": ("M38-form-cart", "fix.storefront.cart"),
    "4": ("M38-form-cod-rule", "fix.storefront.cod.rule"),
    "5": ("M38-form-order-change", "fix.storefront.order.change"),
    "6": ("M38-form-exposure", "fix.stock.exposure.policy"),
    "7": ("M38-form-rma", "fix.storefront.rma"),
    "8": ("M38-form-corporate-account", "fix.storefront.corporate.account"),
    "9": ("M38-form-recovery", "fix.storefront.recovery.attempt"),
    "10": ("M38-form-service-booking", "fix.storefront.service.booking"),
}


@pytest.fixture(scope="module")
def m38(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m38_capture")
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


def _sub(m38, no):
    return next(s for s in m38["subs"] if s["no"] == no)


def test_every_page_is_classified(m38):
    assert sorted(s["no"] for s in m38["subs"]) == sorted(CAPTURE)


@pytest.mark.parametrize("no", sorted(CAPTURE, key=int))
def test_each_page_offers_its_own_capture(m38, no):
    sub = _sub(m38, no)
    screen, model = CAPTURE[no]
    create = sub["create"] or {}
    assert create.get("screen") == screen, "page %s: + New opens %s, expected %s" % (
        no,
        create.get("screen"),
        screen,
    )
    assert m38["screens"][screen]["model"] == model
    assert m38["screens"][screen]["kind"] == "model_form"
    assert sub["forms"], "page %s names no form chip" % no
    for f in sub["forms"]:
        assert f["kind"] == "model_form" and f["opens"], "chip %s on page %s is dead" % (f["f"], no)
    # the record it captures is listed on the page
    listed = {
        m38["screens"][sid]["model"]
        for sid in sub["screens"]
        if sid in m38["screens"] and m38["screens"][sid]["kind"] == "model_list"
    }
    assert model in listed, "page %s does not list the %s it captures" % (no, model)


def test_no_page_captures_m15_graded_stock(m38):
    """A refurbished unit is graded in M14 and stocked in M15; the storefront
    sells it. Merchandising and Stock Exposure used to offer "+ New Graded
    Stock Item"."""
    for sub in m38["subs"]:
        assert (sub["create"] or {}).get("screen") != "M38-form-gstock", sub["no"]
    assert m38["screens"]["M38-stock"]["create"] is False
    assert m38["screens"]["M38-form-gstock"]["create"] is False


def test_b2b_page_lists_corporate_records_not_returns(m38):
    b2b = _sub(m38, "8")
    models = {m38["screens"][sid]["model"] for sid in b2b["screens"] if sid in m38["screens"]}
    assert "fix.storefront.return" not in models
    assert models == {"fix.storefront.corporate.account", "fix.storefront.cart"}
    assert m38["screens"]["M38-corporate-orders"]["domain"] == [
        ["corporate_account_id", "!=", False]
    ]
    # the portal's returns now sit with the RMAs
    assert "M38-storefront-return" in _sub(m38, "7")["screens"]


def test_assisted_cart_prices_are_the_servers(m38):
    form = m38["screens"]["M38-form-cart"]
    cols = {f["name"]: f for f in form["lines"]["fields"]}
    assert form["lines"]["field"] == "line_ids"
    assert cols["unit_price"]["readonly"] and cols["subtotal"]["readonly"]
    assert not cols["product_id"]["readonly"] and not cols["quantity"]["readonly"]
    fields = {f["name"]: f for f in form["fields"]}
    for stamp in ("terms_accepted_at", "client_approved_at", "assisted_by_id", "total"):
        assert fields[stamp]["readonly"], stamp


def test_stamps_and_states_are_never_typed(m38):
    stamps = re.compile(
        r"^(state|approved_by_id|approved_at|published_by_id|published_at|"
        r"decided_by_id|decided_at|contacted_by_id|contacted_at|service_order_id|"
        r"confirmed_by_id|confirmed_at|refusal_reason|cancel_reason|converted)$"
    )
    for sid, _model in CAPTURE.values():
        for f in m38["screens"][sid]["fields"]:
            if stamps.match(f["name"]):
                assert f["readonly"], "%s.%s is typed" % (sid, f["name"])


def test_every_module_form_sits_on_a_page(m38):
    on_pages = {f["f"] for s in m38["subs"] for f in s["forms"]}
    assert set(m38["forms"]) <= on_pages, set(m38["forms"]) - on_pages


def _surfaces():
    """The SURFACES action whitelists, with the module's named action sets
    (`set(_REFUND_ACTIONS)`) resolved."""
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    named = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
            try:
                named[n.targets[0].id] = set(ast.literal_eval(n.value))
            except (ValueError, TypeError, SyntaxError):
                continue
    node = next(
        n.value
        for n in tree.body
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SURFACES"
    )
    out = {}
    for key, conf in zip(node.keys, node.values, strict=False):
        for k, v in zip(conf.keys, conf.values, strict=False):
            if not (isinstance(k, ast.Constant) and k.value == "actions"):
                continue
            if isinstance(v, ast.Call) and v.args and isinstance(v.args[0], ast.Name):
                out[key.value] = set(named.get(v.args[0].id, set()))
            elif isinstance(v, ast.Call):
                out[key.value] = set()  # set()
            else:
                out[key.value] = set(ast.literal_eval(v))
    return out


def test_list_actions_are_served(m38):
    api = _surfaces()
    api.setdefault("fix.promotion", set())
    bad = [
        "%s.%s" % (sid, m)
        for sid, cfg in m38["screens"].items()
        if cfg["kind"] == "model_list"
        for m in cfg["actions"]
        if m not in api.get(cfg["model"], set())
    ]
    assert not bad, bad


def test_new_forms_are_writable_only_where_shown(m38):
    spec = importlib.util.spec_from_file_location(
        "a04w", ROOT / "controllers" / "a04" / "writable.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for sid, model in CAPTURE.values():
        shown = {f["name"] for f in m38["screens"][sid]["fields"] if not f["readonly"]}
        allowed = mod.WRITABLE[model]
        for stamp in ("state", "approved_by_id", "terms_accepted_at", "client_approved_at"):
            assert stamp not in allowed, "%s accepts %s" % (model, stamp)
        assert shown <= set(allowed) | {"name"}, (model, shown - set(allowed))
