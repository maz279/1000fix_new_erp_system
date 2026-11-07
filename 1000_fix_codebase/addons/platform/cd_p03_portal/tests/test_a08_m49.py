# A08 · M49 Fixed Assets & Capex — workspace wiring tests:
#   * the JS registry (MODULE / SCREENS / REPORT_ROUTES / FORM_MODELS / CREATE)
#     is consistent with the backend SURFACES, REPORTS and the real models;
#   * every REPORTS function runs against posted data and reconciles;
#   * the generic action endpoint drives the M49 workflow methods;
#   * the kpis(env) hook serves every KPI key the registry declares.
import base64
import datetime
import itertools
import json
import pathlib
import re
import shutil
import subprocess
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a08 import m49
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

STATIC = pathlib.Path(__file__).resolve().parents[1] / "static" / "src"
_SEQ = itertools.count(1)


# ---------------------------------------------------------------- registry
@pytest.fixture(scope="module")
def registry(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed")
    tmp = tmp_path_factory.mktemp("p03meta")
    # every area folder the registry imports (a02, a08, ...)
    for area in sorted(d for d in STATIC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), encoding="utf-8"
            )
    meta = (STATIC / "p03_modules_meta.js").read_text(encoding="utf-8")
    meta = re.sub(r'from "\./(a\d\d/m\d+)"', r'from "./\1.mjs"', meta)
    (tmp / "meta.mjs").write_text(meta, encoding="utf-8")
    (tmp / "run.mjs").write_text(
        "import * as M from './meta.mjs';\n"
        "const mod = M.P03_MODULES.M49;\n"
        "const ids = mod.groups.flatMap(g => g.screens.map(s => s.id));\n"
        "const screens = Object.fromEntries(ids.map(i => [i, M.P03_DATA_SCREENS[i] || null]));\n"
        "const routes = Object.fromEntries(Object.entries(M.P03_REPORT_ROUTES).filter(([k]) => k.startsWith('M49:')));\n"
        "const forms = Object.fromEntries(Object.entries(M.P03_FORM_MODELS).filter(([k]) => k.startsWith('M49:')));\n"
        "console.log(JSON.stringify({mod, screens, routes, forms, create: M.P03_MODULE_CREATE.M49,"
        " allScreens: M.P03_DATA_SCREENS}));\n",
        encoding="utf-8",
    )
    out = subprocess.run(  # noqa: S603 — fixed argv: node + a generated temp script
        [node, str(tmp / "run.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


def test_every_group_screen_has_a_real_screen(registry):
    missing = [sid for sid, cfg in registry["screens"].items() if not cfg]
    assert not missing, f"screens without a SCREENS entry: {missing}"
    for screen in (s for g in registry["mod"]["groups"] for s in g["screens"]):
        assert screen.get("bn"), f"{screen['id']} has no Bengali label"


def test_model_screens_match_surfaces_and_fields(registry, odoo_env):
    for sid, cfg in registry["screens"].items():
        if cfg["kind"] == "table_report":
            assert cfg["module"] == "M49" and cfg["report"] in m49.REPORTS, sid
            continue
        assert cfg["kind"] == "model_list", sid
        model = cfg["model"]
        assert model in m49.SURFACES, f"{sid}: {model} not in SURFACES"
        fields_ = odoo_env[model]._fields
        for col in cfg["cols"]:
            assert col in fields_, f"{sid}: {model}.{col} is not a field"
        if cfg.get("stateField"):
            assert fields_[cfg["stateField"]].type == "selection", sid
        for act in cfg.get("actions", []):
            assert act["m"] in m49.SURFACES[model]["actions"], f"{sid}: {act['m']} not allowed"
            assert callable(getattr(odoo_env[model], act["m"], None)), f"{model}.{act['m']}"


def test_surface_actions_exist_on_models(odoo_env):
    for model, conf in m49.SURFACES.items():
        for method in conf["actions"]:
            assert callable(getattr(odoo_env[model], method, None)), f"{model}.{method}"


def test_report_chips_route_to_report_screens(registry):
    reports = registry["mod"]["reports"]
    assert reports
    for name in reports:
        target = registry["routes"].get(f"M49:{name}")
        assert target, f"report chip '{name}' has no route"
        assert registry["screens"].get(target), f"'{name}' routes to unknown screen {target}"
        assert registry["screens"][target]["kind"] == "table_report", name


def test_form_chips_map_to_real_models(registry, odoo_env):
    for name in registry["mod"]["forms"]:
        model = registry["forms"].get(f"M49:{name}")
        assert model, f"form chip '{name}' is not mapped"
        assert model in odoo_env, model
    assert registry["create"]["model"] in odoo_env


def test_kpi_keys_are_served(registry, odoo_env):
    served = m49.kpis(odoo_env)
    for kpi in registry["mod"]["kpis"]:
        assert kpi.get("m") in served, f"KPI '{kpi['l']}' has no metric"
        assert served[kpi["m"]] is not None


# ---------------------------------------------------------------- data
def _acc(env, tag, code, kind):
    return env["account.account"].create(
        {
            "code": f"P49{tag:02d}{code}",
            "name": f"P49 {code}",
            "account_type": kind,
            "company_ids": [(6, 0, [env.company.id])],
        }
    )


@pytest.fixture
def m49_data(odoo_env):
    """A configured category, one depreciated + revalued asset, one disposed
    asset, a budget with an approved request, and an active lease."""
    env = odoo_env
    # the tax book refuses a rate the adviser has not confirmed (M49-8): this
    # fixture is about the reports, so the class it uses is confirmed here
    env["fix.tax.rate"].sudo().search([("code", "=", "ITA3-COMPUTER")]).write(
        {"verify_with_adviser": False}
    )
    tag = next(_SEQ)
    acc = {
        k: _acc(env, tag, c, t)
        for k, c, t in [
            ("asset", "01", "asset_fixed"),
            ("accum", "02", "asset_fixed"),
            ("exp", "03", "expense_depreciation"),
            ("cwip", "04", "asset_non_current"),
            ("surplus", "05", "equity"),
            ("impair", "06", "expense"),
            ("gain", "07", "income_other"),
            ("loss", "08", "expense"),
            ("liab", "09", "liability_non_current"),
            ("int", "10", "expense"),
            ("rent", "11", "liability_current"),
        ]
    }
    journal = env["account.journal"].create(
        {"name": f"P49 {tag}", "code": f"P4{tag % 100:02d}", "type": "general"}
    )
    cat = env["fix.asset.category"].create(
        {
            "code": f"P49-{tag}",
            "name": f"P49 Report Category {tag}",
            "useful_life_months": 10,
            "tax_rate_code": "ITA3-COMPUTER",
            "journal_id": journal.id,
            "asset_account_id": acc["asset"].id,
            "accumulated_account_id": acc["accum"].id,
            "expense_account_id": acc["exp"].id,
            "cwip_account_id": acc["cwip"].id,
            "revaluation_surplus_account_id": acc["surplus"].id,
            "impairment_account_id": acc["impair"].id,
            "gain_account_id": acc["gain"].id,
            "loss_account_id": acc["loss"].id,
        }
    )
    Asset = env["fix.fixed.asset"]
    kept = Asset.create(
        {
            "name": "Kept",
            "category_id": cat.id,
            "gross": 10000.0,
            "salvage": 0.0,
            "purchase_date": datetime.date(2025, 6, 10),
            "state": "active",
        }
    )
    sold = Asset.create(
        {
            "name": "Sold",
            "category_id": cat.id,
            "gross": 5000.0,
            "salvage": 0.0,
            "purchase_date": datetime.date(2025, 8, 1),
            "state": "active",
        }
    )
    Run = env["fix.asset.depreciation.run"]
    for month in (datetime.date(2025, 7, 1), datetime.date(2025, 8, 1)):
        for book in ("book", "tax"):
            run = Run.create(
                {"book": book, "period_start": month, "asset_ids": [(6, 0, (kept | sold).ids)]}
            )
            run.action_compute()
            run.action_post()
    users = [
        env["res.users"].create(
            {
                "name": f"P49 Manager {tag}-{i}",
                "login": f"p49-mgr-{tag}-{i}@test.local",
                "group_ids": [(6, 0, [env.ref("account.group_account_manager").id])],
            }
        )
        for i in (1, 2)
    ]
    # these documents are approved in the M63 inbox, by someone holding the DOFA tier
    approver = env["res.users"].create(
        {
            "name": f"P49 Approver {tag}",
            "login": f"p49-approver-{tag}@test.local",
            "group_ids": [
                (
                    6,
                    0,
                    [env.ref("account.group_account_manager").id]
                    + [env.ref("cd_entity_config.group_dofa_tier_%d" % t).id for t in (2, 3, 4, 5)],
                )
            ],
        }
    )
    report = (
        env["ir.attachment"]
        .with_user(users[0])
        .create({"name": "valuer.pdf", "datas": base64.b64encode(b"%PDF-1.4 valuer report")})
    )
    reval = (
        env["fix.asset.revaluation"]
        .with_user(users[0])
        .create(
            {
                "asset_id": kept.id,
                "kind": "revaluation",
                "new_value": 9000.0,
                "date": datetime.date(2025, 9, 1),
                "basis": "Independent valuer, market approach",
                "valuer_report_ids": [(6, 0, report.ids)],
            }
        )
    )
    reval.with_user(users[0]).action_submit()
    approve_via_inbox(reval, approver)
    reval.with_user(users[1]).action_post()
    disposal = (
        env["fix.asset.disposal"]
        .with_user(users[0])
        .create(
            {
                "asset_id": sold.id,
                "kind": "write_off",
                "date": datetime.date(2025, 9, 15),
                "reason": "Obsolete",
                "incident_ref": "INC-P49",
            }
        )
    )
    disposal.with_user(users[0]).action_submit()
    approve_via_inbox(disposal, approver)
    disposal.with_user(users[1]).action_post()
    budget = (
        env["fix.capex.budget"]
        .with_user(users[0])
        .create(
            {
                "name": f"P49 Budget {tag}",
                "date_from": datetime.date(2025, 7, 1),
                "date_to": datetime.date(2026, 6, 30),
                "amount": 100000.0,
            }
        )
    )
    budget.with_user(users[1]).action_approve()
    req = (
        env["fix.capex.request"]
        .with_user(users[0])
        .create(
            {
                "title": "Benches",
                "justification": "Bench for the Dhaka hub",
                "category_id": cat.id,
                "budget_id": budget.id,
                "amount": 40000.0,
                "request_date": datetime.date(2025, 10, 1),
            }
        )
    )
    req.action_submit()
    approve_via_inbox(req, approver)
    rou_cat = cat.copy({"code": f"P49-ROU-{tag}", "name": f"P49 ROU {tag}", "tax_rate_code": False})
    lease = env["fix.lease"].create(
        {
            "name": f"P49 Branch {tag}",
            "category_id": rou_cat.id,
            "commencement_date": datetime.date(2025, 7, 1),
            "term_months": 12,
            "payment_amount": 10000.0,
            "ibr_percent": 12.0,
            "payment_timing": "arrears",
            "liability_account_id": acc["liab"].id,
            "interest_account_id": acc["int"].id,
            "payment_account_id": acc["rent"].id,
        }
    )
    lease.action_activate()
    lease.schedule_line_ids.sorted("sequence")[0].action_post()
    return {
        "env": env,
        "kept": kept,
        "sold": sold,
        "cat": cat,
        "budget": budget,
        "disposal": disposal,
        "lease": lease,
        "reval": reval,
    }


FY = {"date_from": "2025-07-01", "date_to": "2026-06-30"}


def _row(report, key, value):
    return next(r for r in report["rows"] if r[key] == value)


def test_movement_schedule_reconciles(m49_data):
    env, cat = m49_data["env"], m49_data["cat"]
    rep = m49.REPORTS["movement_schedule"](env, **FY)
    row = _row(rep, "category", cat.name)
    # Kept: 10,000 bought before the FY; Sold: 5,000 bought in the FY
    assert row["opening_cost"] == 10000.0 and row["additions"] == 5000.0
    assert row["depreciation"] == 2500.0  # Kept 1,000 x Jul+Aug, Sold 500 x Aug
    assert row["revaluation"] == 1000.0  # NBV 8,000 -> 9,000
    assert row["disposals_cost"] == 5000.0
    assert (
        row["closing_cost"]
        == row["opening_cost"] + row["additions"] + row["revaluation"] - row["disposals_cost"]
    )
    assert (
        row["closing_accum"]
        == row["opening_accum"] + row["depreciation"] + row["impairment"] - row["disposals_accum"]
    )
    assert row["closing_nbv"] == 9000.0
    assert set(rep["cols"]) <= set(rep["labels"]) and rep["totals"]


def test_dual_book_and_nbv_by_category(m49_data):
    env, kept = m49_data["env"], m49_data["kept"]
    rep = m49.REPORTS["dual_book"](env, **FY)
    row = _row(rep, "asset", f"{kept.code} {kept.name}")
    tax_rate = env["fix.asset.tax.rate"].rate_for(
        "ITA3-COMPUTER", datetime.date(2025, 7, 1), env.company
    )
    # the Third Schedule rate on the opening WDV, spread over the year (M49-8)
    month = round(10000.0 * tax_rate.rate_percent / 1200.0, 2)
    assert (row["book_dep"], row["tax_dep"]) == (2000.0, round(month * 2, 2))
    assert row["book_nbv"] == 9000.0 and row["difference"] == round(9000.0 - row["tax_wdv"], 2)
    assert any("not yet verified" in n for n in rep["notes"])
    nbv = m49.REPORTS["nbv_by_category"](env, **FY)
    cat_row = _row(nbv, "category", m49_data["cat"].name)
    assert (cat_row["count"], cat_row["nbv"]) == (1, 9000.0)


def test_capex_disposal_and_lease_reports(m49_data):
    env = m49_data["env"]
    capex = m49.REPORTS["capex_vs_budget"](env, **FY)
    brow = _row(capex, "budget", m49_data["budget"].name)
    assert (brow["committed"], brow["available"], brow["utilisation_pct"]) == (
        40000.0,
        60000.0,
        40.0,
    )
    disp = m49.REPORTS["disposal_gains"](env, **FY)
    drow = _row(disp, "reference", m49_data["disposal"].name)
    assert drow["gain_loss"] == -drow["nbv"] and drow["entry"]
    lease = m49_data["lease"]
    rep = m49.REPORTS["lease_summary"](env, **FY)
    lrow = _row(rep, "lease", f"{lease.reference} {lease.name}")
    lines = lease.schedule_line_ids
    assert lrow["liability"] == 0.0 and lrow["interest"] == round(sum(lines.mapped("interest")), 2)
    assert lrow["unposted_due"] == 11
    assert lrow["rou_nbv"] == round(lease.rou_amount - lines.sorted("sequence")[0].depreciation, 2)


def test_reports_default_window_and_empty(odoo_env):
    for name, fn in m49.REPORTS.items():
        out = fn(odoo_env, date_from="1990-01-01", date_to="1990-12-31")
        assert out["cols"] and "rows" in out and out.get("empty"), name


# ---------------------------------------------------------------- endpoint
class FakeRequest:
    def __init__(self, env):
        self.env = env


def test_generic_endpoints_serve_m49(m49_data):
    env = m49_data["env"]
    with mock.patch.object(api, "request", FakeRequest(env)):
        ctrl = api.P03GenericApiController()
        res = ctrl.model_records(
            model="fix.fixed.asset", cols=["code", "name", "book_nbv", "state"]
        )
        assert m49_data["kept"].id in [r["id"] for r in res["rows"]]
        rep = ctrl.model_report(module="M49", report="nbv_by_category", params=FY)
        assert "error" not in rep and rep["rows"]
        act = ctrl.model_action(
            model="fix.asset.depreciation.run", ids=[999999999], method="action_post"
        )
        assert act == {"success": False, "error": "Record not found"}
        bad = ctrl.model_action(model="fix.fixed.asset", ids=[m49_data["kept"].id], method="unlink")
        assert bad["success"] is False
        # the register's Accrue Month runs end-to-end through the endpoint
        ok = ctrl.model_action(
            model="fix.fixed.asset", ids=[m49_data["kept"].id], method="action_accrue_month"
        )
        assert ok["success"] is True
        again = ctrl.model_action(
            model="fix.fixed.asset", ids=[m49_data["kept"].id], method="action_accrue_month"
        )
        assert again["success"] is False and "already depreciated" in again["error"]
