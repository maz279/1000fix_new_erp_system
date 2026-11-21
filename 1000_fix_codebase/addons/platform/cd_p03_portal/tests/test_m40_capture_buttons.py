# M40 Partner, Channel, Alliance & Franchise: every sub-module page captures
# the records the spec puts on it (capture audit 2026-11-19).
#
# Before (HEAD 742e46bc), evaluated with the engine's own fregCreate/fregPanels:
#   * 2 Recruitment & Onboarding: "+ New" opened a BRAND AUTHORISATION; no
#     onboarding checklist or enablement record existed (FR-PCM-007/041,
#     BRU-PCM-01);
#   * 4 Alliances and 7 Resellers: "+ New" made a partner; no alliance scheme,
#     eligibility check (FR-PCM-030/031) or reseller allocation (033);
#   * 10 Performance captured a channel CONFLICT; the technical audits that
#     gate rebates sat on no page;
#   * 1, 3, 5, 6, 8 and 9 captured one record and none of the others the
#     spec names: programme/tier and contacts (003/004/009), brand obligation,
#     audit and engagement (016/017/020/021), referral link and consented lead
#     (022-024, BRU-PCM-06), precedence rule (029), franchise territory and
#     royalty (035/036), MDF fund and claim (039).
#
# Evaluated as the browser evaluates it: node runs the engine's own fregCreate
# and fregPanels over the real registry fragments (the M42 fixture).
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
CONTROLLER = HERE.parent / "controllers" / "a04" / "m40.py"
WRITABLE_FILE = HERE.parent / "controllers" / "a04" / "writable.py"
PARTNER = HERE.parents[2] / "domain" / "b_customer_engagement" / "cd_partner"

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
const mod = P03_MODULES.M40;
const subs = mod.freg.sub.map((s) => {
  const map = s[3];
  const create = fregCreate('M40', map);
  const panels = fregPanels('M40', mod, map);
  const forms = panels.forms.map((f) => {
    const id = P03_FORM_CHIPS['M40:' + f];
    const cfg = P03_DATA_SCREENS[id] || {};
    return { f, id: id || null, kind: cfg.kind || null, model: cfg.model || null,
      opens: cfg.kind === 'model_form' && (cfg.create !== false || !!cfg.pickRecord) };
  });
  const own = create && (create.screen || (create.module ? P03_MODULE_CREATE.M40.screen : null));
  return { no: s[0], title: s[1], model: map.model || null, screens: map.screens || [],
    create: own || null, forms,
    reports: panels.reports.map((r) => ({ r, route: P03_REPORT_ROUTES['M40:' + r] || null })) };
});
console.log(JSON.stringify({ subs,
  labelled: mod.groups.flatMap((g) => g.screens.map((x) => x.id)),
  screens: Object.fromEntries(Object.entries(P03_DATA_SCREENS).filter(([id]) => id.startsWith('M40-')).map(([id, c]) => [id, {
    kind: c.kind, model: c.model || null, create: c.create, tabs: (c.tabs || []).map((t) => t.id),
    cols: c.cols || [],
    grids: (c.grids || []).map((g) => ({ field: g.field, tab: g.tab || null })),
    lines: c.lines ? { field: c.lines.field, readonly: !!c.lines.readonlyGrid } : null,
    actions: (c.actions || []).map((a) => ({ m: a.m, kwarg: a.kwarg || null })),
    fields: (c.sections || []).flatMap((s) => (s.fields || []).map((f) => ({
      name: f.name, readonly: !!f.readonly, required: !!f.required, tab: s.tab || null }))) }])) }));
"""

# What each page lets a person capture: its own "+ New" first, then every
# other record the page covers, by form screen.
CAPTURES = {
    "1": ["M40-form-partner", "M40-form-programme", "M40-form-contact"],
    "2": ["M40-form-onboarding", "M40-form-enablement", "M40-form-partner"],
    "3": [
        "M40-form-auth",
        "M40-form-obligation",
        "M40-form-brand-audit",
        "M40-form-engagement",
    ],
    "4": ["M40-form-scheme", "M40-form-eligibility"],
    "5": ["M40-form-lead", "M40-form-link", "M40-form-referral"],
    "6": ["M40-form-deal", "M40-form-conflict", "M40-form-conflict-rule"],
    "7": ["M40-form-allocation"],
    "8": ["M40-form-franchise", "M40-form-territory", "M40-form-royalty"],
    "9": ["M40-form-rebate", "M40-form-mdf-fund", "M40-form-mdf-claim"],
    "10": ["M40-form-audit"],
}

RECORDS = {
    "1": "fix.partner",
    "2": "fix.partner.onboarding",
    "3": "fix.partner.authorisation",
    "4": "fix.alliance.scheme",
    "5": "fix.partner.lead",
    "6": "fix.partner.deal",
    "7": "fix.reseller.allocation",
    "8": "fix.partner.franchise",
    "9": "fix.partner.rebate",
    "10": "fix.partner.audit",
}

NEW_MODELS = (
    "fix.partner.programme",
    "fix.partner.contact.role",
    "fix.partner.onboarding",
    "fix.partner.enablement",
    "fix.brand.obligation",
    "fix.brand.audit",
    "fix.partner.engagement",
    "fix.alliance.scheme",
    "fix.alliance.eligibility.check",
    "fix.referral.link",
    "fix.partner.lead",
    "fix.channel.conflict.rule",
    "fix.reseller.allocation",
    "fix.franchise.territory",
    "fix.franchise.royalty",
    "fix.mdf.fund",
    "fix.mdf.claim",
)
# registers with a company column get the generated company rule
COMPANY_RULED = (
    "fix.partner.programme",
    "fix.alliance.scheme",
    "fix.referral.link",
    "fix.partner.lead",
    "fix.channel.conflict.rule",
    "fix.reseller.allocation",
    "fix.franchise.territory",
    "fix.mdf.fund",
)


@pytest.fixture(scope="module")
def m40(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_m40_capture")
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
    """{model: {method names}} defined in cd_partner's model files."""
    out = {}
    for path in (PARTNER / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            names = set()
            for stmt in cls.body:
                if (
                    isinstance(stmt, ast.Assign)
                    and isinstance(stmt.targets[0], ast.Name)
                    and stmt.targets[0].id in ("_name", "_inherit")
                ):
                    vals = stmt.value.elts if isinstance(stmt.value, ast.List) else [stmt.value]
                    names |= {v.value for v in vals if isinstance(v, ast.Constant)}
            methods = {f.name for f in cls.body if isinstance(f, ast.FunctionDef)}
            for name in names:
                out.setdefault(name, set()).update(methods)
    # the shared base's helpers reach every register built on it
    base = out.get("fix.partner.capture.base", set())
    for methods in out.values():
        methods |= base
    return out


def _sub(m40, no):
    return next(s for s in m40["subs"] if s["no"] == no)


def test_every_page_is_classified(m40):
    assert sorted(s["no"] for s in m40["subs"]) == sorted(CAPTURES)


@pytest.mark.parametrize("no", sorted(CAPTURES, key=int))
def test_each_page_captures_every_record_it_covers(m40, no):
    sub = _sub(m40, no)
    own, *others = CAPTURES[no]
    assert sub["create"] == own, "page %s + New opens %s" % (no, sub["create"])
    chips = {f["id"] for f in sub["forms"] if f["opens"]}
    missing = [form for form in [own, *others] if form not in chips]
    assert not missing, "page %s has no capture for %s" % (no, missing)


@pytest.mark.parametrize("no", sorted(RECORDS, key=int))
def test_each_page_lists_its_own_record(m40, no):
    assert _sub(m40, no)["model"] == RECORDS[no]


def test_onboarding_page_no_longer_captures_an_authorisation(m40):
    sub = _sub(m40, "2")
    assert sub["create"] != "M40-form-auth"
    assert "fix.partner.authorisation" not in {f["model"] for f in sub["forms"]}


def test_alliance_and_reseller_pages_capture_their_own_records(m40):
    assert _sub(m40, "4")["create"] == "M40-form-scheme"
    assert _sub(m40, "7")["create"] == "M40-form-allocation"


def test_each_captured_record_is_listed_on_its_page(m40):
    for sub in m40["subs"]:
        listed = {m40["screens"][s]["model"] for s in sub["screens"] if s in m40["screens"]}
        listed.add(sub["model"])
        for f in sub["forms"]:
            assert f["model"] in listed, "page %s captures %s but lists none" % (
                sub["no"],
                f["model"],
            )


def test_every_working_screen_sits_on_a_page(m40):
    placed = {sid for s in m40["subs"] for sid in s["screens"]}
    orphans = [
        sid
        for sid, cfg in m40["screens"].items()
        if cfg["kind"] == "model_list" and sid not in placed
    ]
    assert not orphans, orphans


def test_every_form_chip_resolves(m40):
    for sub in m40["subs"]:
        for f in sub["forms"]:
            assert f["id"] and f["kind"] == "model_form", (sub["no"], f)
        for r in sub["reports"]:
            assert r["route"], (sub["no"], r)


# routed-approval actions the rebate inherits from fix.dofa.mixin (cd_workflow_engine)
DOFA_MIXIN_ACTIONS = {"action_request_approval", "action_recall_approval"}


def test_every_served_action_exists_on_its_model():
    methods = _model_methods()
    methods["fix.partner.rebate"] = methods.get("fix.partner.rebate", set()) | DOFA_MIXIN_ACTIONS
    # A04 ERP audit M40-F5: the rate change is a routed DOFA record too
    methods["fix.partner.rate.change"] = (
        methods.get("fix.partner.rate.change", set()) | DOFA_MIXIN_ACTIONS
    )
    for model, acts in _surfaces().items():
        missing = acts - methods.get(model, set())
        assert not missing, "%s serves %s, which the model lacks" % (model, sorted(missing))


def test_every_list_action_is_served(m40):
    surfaces = _surfaces()
    for sid, cfg in m40["screens"].items():
        if cfg["kind"] != "model_list" or not cfg["actions"]:
            continue
        served = surfaces.get(cfg["model"], set())
        for act in cfg["actions"]:
            assert act["m"] in served, "%s offers %s, not served" % (sid, act["m"])


@pytest.mark.parametrize("model", NEW_MODELS)
def test_new_registers_are_served_and_whitelisted(m40, model):
    assert model in _surfaces()
    forms = [
        c for c in m40["screens"].values() if c["kind"] == "model_form" and c["model"] == model
    ]
    assert len(forms) == 1, "%s needs exactly one form, has %d" % (model, len(forms))
    typed = {f["name"] for f in forms[0]["fields"] if not f["readonly"]}
    typed |= {g["field"] for g in forms[0]["grids"]}
    lines = forms[0]["lines"]
    if lines and not lines["readonly"]:
        typed.add(lines["field"])
    assert _writable()[model] == typed


def test_decisions_and_evidence_are_never_typed():
    """States, deciders, codes, attributions and computed money move only
    through their actions."""
    never = {
        "fix.partner.programme": {"state", "version", "published_by_id", "previous_id"},
        "fix.partner.onboarding": {"state", "completed_by_id", "waived_by_id", "waive_reason"},
        "fix.partner.enablement": {"state", "certified_by_id"},
        "fix.brand.obligation": {"state", "met_by_id"},
        "fix.brand.audit": {"state", "closed_by_id", "closed_on"},
        "fix.partner.engagement": {"logged_by_id"},
        "fix.alliance.scheme": {"state", "activated_by_id", "eligible_count"},
        "fix.alliance.eligibility.check": {"checked_at", "checked_by_id"},
        "fix.referral.link": {"state", "code", "revoked_by_id"},
        "fix.partner.lead": {
            "name",
            "state",
            "attributed_at",
            "attribution_window_days",
            "attribution_expires_on",
            "attribution_lapsed",
            "referral_id",
        },
        "fix.channel.conflict.rule": {"state", "approved_by_id"},
        "fix.reseller.allocation": {"name", "state", "consumed_qty", "allocated_by_id"},
        "fix.franchise.territory": {"state", "approved_by_id"},
        "fix.franchise.royalty": {
            "state",
            "revenue_basis",
            "royalty_amount",
            "levy_amount",
            "royalty_rate",
            "invoice_ref",
        },
        "fix.mdf.fund": {"state", "allocated_by_id", "balance", "paid", "approved"},
        "fix.mdf.claim": {"name", "state", "decided_by_id", "payment_ref", "submitted_by_id"},
        "fix.partner": {"state", "tier_id", "commission_rate", "technical_audit_score"},
    }
    writable = _writable()
    for model, names in never.items():
        assert not (writable.get(model, set()) & names), (model, writable[model] & names)


def test_reasons_and_values_are_asked_for(m40):
    asks = {
        ("M40-onboarding", "action_waive"): "reason",
        ("M40-leads", "action_mark_lost"): "reason",
        ("M40-referral-links", "action_revoke"): "reason",
        ("M40-mdf-claims", "action_refuse"): "reason",
        ("M40-allocations", "action_record_draw"): "qty",
        ("M40-partners", "action_change_tier"): "tier_code",
    }
    for (sid, method), kwarg in asks.items():
        acts = {a["m"]: a for a in m40["screens"][sid]["actions"]}
        assert acts[method]["kwarg"] == kwarg, (sid, method)
    # A04 ERP audit M40-F1/F3: a typed reference no longer stands for an
    # invoice or a payment - these actions ask for nothing
    for sid, method in (
        ("M40-mdf-claims", "action_record_payment"),
        ("M40-rebates", "action_record_payout"),
        ("M40-royalties", "action_raise_invoice"),
    ):
        acts = {a["m"]: a for a in m40["screens"][sid]["actions"]}
        assert not acts[method].get("kwarg"), (sid, method)


def test_forms_are_tabbed_and_every_section_sits_on_a_tab(m40):
    for sid, cfg in m40["screens"].items():
        if cfg["kind"] != "model_form" or cfg["model"] not in NEW_MODELS:
            continue
        assert cfg["tabs"], sid
        assert all(f["tab"] in cfg["tabs"] for f in cfg["fields"]), sid
        assert all(g["tab"] in cfg["tabs"] for g in cfg["grids"]), sid


def test_the_programme_form_edits_its_tiers(m40):
    assert m40["screens"]["M40-form-programme"]["lines"] == {"field": "tier_ids", "readonly": False}


def test_parents_show_their_children_read_only(m40):
    """Territories, checks and claims carry their own lifecycle screen; their
    parent shows them and never edits them."""
    for sid, field in (
        ("M40-form-franchise", "territory_ids"),
        ("M40-form-scheme", "check_ids"),
        ("M40-form-mdf-fund", "claim_ids"),
    ):
        assert m40["screens"][sid]["lines"] == {"field": field, "readonly": True}, sid


def test_the_lead_form_demands_consent(m40):
    fields = {f["name"]: f for f in m40["screens"]["M40-form-lead"]["fields"]}
    assert fields["consent_given"]["required"] and fields["consent_method"]["required"]


def test_the_franchise_form_carries_the_royalty_terms(m40):
    names = {f["name"] for f in m40["screens"]["M40-form-franchise"]["fields"]}
    assert {"operating_unit_id", "royalty_rate", "marketing_levy_rate"} <= names


def test_list_columns_exist_on_their_models(m40):
    """/p03/model/records drops an unknown column silently: check them."""
    declared = {}
    for path in (PARTNER / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            names, fields = set(), set()
            for stmt in cls.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name):
                    target = stmt.targets[0].id
                    if target in ("_name", "_inherit"):
                        vals = stmt.value.elts if isinstance(stmt.value, ast.List) else [stmt.value]
                        names |= {v.value for v in vals if isinstance(v, ast.Constant)}
                    elif (
                        isinstance(stmt.value, ast.Call)
                        and isinstance(stmt.value.func, ast.Attribute)
                        and getattr(stmt.value.func.value, "id", "") == "fields"
                    ):
                        fields.add(target)
            for name in names:
                declared.setdefault(name, set()).update(fields)
    for sid, cfg in m40["screens"].items():
        if cfg["kind"] != "model_list" or cfg["model"] not in NEW_MODELS:
            continue
        missing = [c for c in cfg["cols"] if c not in declared[cfg["model"]]]
        assert not missing, (sid, missing)


def test_new_models_are_secured():
    acl = (PARTNER / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
    rules = (PARTNER / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in (*NEW_MODELS, "fix.partner.tier"):
        xmlid = "model_" + model.replace(".", "_")
        rows = [r.split(",") for r in acl.splitlines() if (",%s," % xmlid) in r]
        assert rows, model
        # nobody may delete; a plain employee only reads
        assert all(r[-1].strip() == "0" for r in rows), model
        plain = [r for r in rows if r[3] == "base.group_user"]
        assert plain and plain[0][4:8] == ["1", "0", "0", "0"], model
    for model in COMPANY_RULED:
        assert 'ref="model_%s"' % model.replace(".", "_") in rules, "%s has no company rule" % model


def test_crons_and_sequences_are_wired():
    crons = (PARTNER / "data" / "ir_cron.xml").read_text(encoding="utf-8")
    for code in ("cron_obligation_overdue", "cron_enablement_expiry"):
        assert "model.%s()" % code in crons
    seqs = (PARTNER / "data" / "ir_sequence_data.xml").read_text(encoding="utf-8")
    for code in ("fix.partner.lead", "fix.mdf.claim", "fix.reseller.allocation"):
        assert '<field name="code">%s</field>' % code in seqs


def test_the_new_file_loads_after_the_models_it_extends():
    init = (PARTNER / "models" / "__init__.py").read_text(encoding="utf-8")
    code = init[init.index("from . import") :]
    assert code.index("fix_partner_ops") < code.index("fix_partner_capture")


def test_every_screen_on_a_page_has_a_navigation_label(m40):
    labelled = set(m40["labelled"])
    unlabelled = sorted(
        sid
        for sub in m40["subs"]
        for sid in sub["screens"]
        if sid in m40["screens"]
        and m40["screens"][sid]["kind"] == "model_list"
        and sid not in labelled
    )
    assert not unlabelled, unlabelled
