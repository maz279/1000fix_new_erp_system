# A08 · M53 — the workspace registry (static/src/a08/m53.js, merged by
# p03_modules_meta.js) agrees with the backend surface (controllers/a08/m53.py)
# and the live models; the M53 reports and KPI metrics compute from real
# posted data; the workflow actions run through the generic action endpoint.
from __future__ import annotations

import json
import re
import shutil
import subprocess
import uuid
from datetime import date
from pathlib import Path
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a08 import m53

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
CODE = "M53"


def load_registry(tmp_path_factory, code):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp(f"p03_registry_{code.lower()}")
    # every area folder the registry imports (a02, a08, ...)
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    probe = tmp / "probe.mjs"
    probe.write_text(
        "import * as M from './meta.mjs';\n"
        f"const pick = (o) => Object.fromEntries(Object.entries(o).filter(([k]) => k.startsWith('{code}')));\n"
        f"console.log(JSON.stringify({{module: M.P03_MODULES.{code},\n"
        "  screens: pick(M.P03_DATA_SCREENS), routes: pick(M.P03_REPORT_ROUTES),\n"
        f"  forms: pick(M.P03_FORM_MODELS), create: M.P03_MODULE_CREATE.{code}}}));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv built in-process, no shell
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=60
    )
    return json.loads(out.stdout)


@pytest.fixture(scope="module")
def registry(tmp_path_factory):
    return load_registry(tmp_path_factory, CODE)


def test_every_registry_screen_has_a_real_screen(registry):
    ids = [s["id"] for g in registry["module"]["groups"] for s in g["screens"]]
    assert len(ids) == len(set(ids))
    assert set(ids) == set(registry["screens"]), "screens without an in-workspace entry"
    for group in registry["module"]["groups"]:
        for s in group["screens"]:
            assert s.get("bn"), s["id"]
    names = {s["en"] for g in registry["module"]["groups"] for s in g["screens"]}
    # the rename: seller / partner rate tables, technician incentives moved to Payroll
    assert "Commission Schemes" in names and "Incentive Schemes" not in names
    for wanted in (
        "Performance Obligations",
        "Contract Assets & Liabilities",
        "Partner / Referral Payouts",
        "Escrow & Clawbacks",
        "AMC & Subscription Contracts",
        "Payout Reconciliation",
        "Warranty Provision (IAS 37)",
    ):
        assert wanted in names


def test_model_list_screens_match_surfaces_and_fields(registry, odoo_env):
    for sid, cfg in registry["screens"].items():
        if cfg["kind"] != "model_list":
            continue
        model = cfg["model"]
        assert model in m53.SURFACES, f"{sid}: {model} not served"
        fields_ = odoo_env[model]._fields
        for col in cfg["cols"]:
            assert col in fields_, f"{sid}: {model}.{col} is not a field"
        if cfg.get("stateField"):
            assert cfg["stateField"] in fields_
        for act in cfg.get("actions", []):
            assert act["m"] in m53.SURFACES[model]["actions"], f"{sid}: {act['m']}"
            assert callable(getattr(odoo_env[model], act["m"], None))
        for leaf in cfg.get("domain", []):
            assert leaf[0] in fields_
    for model, conf in m53.SURFACES.items():
        for method in conf["actions"]:
            assert callable(getattr(odoo_env[model], method, None)), f"{model}.{method}"


def test_wired_actions_are_on_the_screens(registry):
    wired = {
        (cfg["model"], a["m"])
        for cfg in registry["screens"].values()
        if cfg["kind"] == "model_list"
        for a in cfg.get("actions", [])
    }
    for pair in (
        ("fix.seller.statement", "action_issue_statement"),
        ("fix.seller.statement", "action_settle_statement"),
        ("fix.payout.run", "action_query_status"),
        ("fix.payout.run", "action_post_payout_to_gl"),
        ("fix.revenue.schedule", "action_recognize_period"),
        ("fix.subscription", "action_generate_charge"),
        ("fix.subscription", "action_trigger_dunning"),
        ("fix.subscription", "action_reinstate"),
        ("fix.subscription", "action_request_refund"),
        ("fix.payout.reconciliation", "action_run_reconciliation"),
        ("fix.warranty.provision", "action_post"),
    ):
        assert pair in wired, pair


def test_table_reports_name_real_report_functions(registry):
    reports = [c for c in registry["screens"].values() if c["kind"] == "table_report"]
    assert {c["report"] for c in reports} == set(m53.REPORTS)
    assert {c["module"] for c in reports} == {CODE}


def test_report_and_form_chips_route_to_real_targets(registry, odoo_env):
    module = registry["module"]
    for chip in module["reports"]:
        target = registry["routes"].get(f"{CODE}:{chip}")
        assert target in registry["screens"], f"report chip {chip!r} unrouted"
    for chip in module["forms"]:
        model = registry["forms"].get(f"{CODE}:{chip}")
        assert model and model in odoo_env, f"form chip {chip!r} unmapped"
    assert registry["create"]["model"] in odoo_env


def test_kpi_tiles_name_real_metrics(registry, odoo_env):
    builtin = {"commission_accrued_count", "payout_runs_open", "revenue_schedules_count"}
    keys = set(m53.kpis(odoo_env)) | builtin
    for kpi in registry["module"]["kpis"]:
        assert kpi.get("m") in keys, f"KPI tile {kpi['l']!r} has no metric"


# --------------------------------------------------------------------------- reports on real data


@pytest.fixture
def contract(odoo_env):
    env = odoo_env
    if not env.company.vat:
        env.company.vat = "1234567890123"
    partner = env["res.partner"].create({"name": f"Rev Rec Cust {uuid.uuid4().hex[:5]}"})
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    sub = env["fix.subscription"].create(
        {
            "name": f"AMC Report {uuid.uuid4().hex[:5]}",
            "customer_id": partner.id,
            "operating_unit_id": ou.id,
            "recurring_amount": 3000.0,
            "start_date": date(2026, 1, 1),
            "next_invoice_date": date(2026, 1, 1),
            "contract_value": 36500.0,
            "contract_end_date": date(2027, 1, 1),
        }
    )
    amc = env["fix.performance.obligation"].create(
        {
            "subscription_id": sub.id,
            "name": "AMC visits",
            "obligation_type": "amc_service",
            "standalone_price": 1.0,
        }
    )
    sub.action_allocate_price()
    amc.action_create_schedule()
    sub.action_generate_charge()  # Jan cycle: 3000 + VAT, issued below
    sub.charge_ids.invoice_id.action_issue()
    amc.schedule_id.action_recognize_period(as_of=date(2026, 2, 1))  # 3100.00
    return sub


def test_contract_balances_report(odoo_env, contract):
    out = m53.contract_balances(odoo_env, date_from="2026-01-01", date_to="2026-02-28")
    (row,) = [r for r in out["rows"] if r["contract"] == contract.name]
    # billed 3000.00 (VAT excl.) vs recognised 3100.00 -> contract ASSET 100.00
    assert (row["billed"], row["recognised"]) == (3000.0, 3100.0)
    assert (row["contract_liability"], row["contract_asset"]) == (0.0, 100.0)
    assert row["transaction_price"] == 36500.0
    assert set(out["cols"]) <= set(out["labels"]) and out["totals"]
    # as at January 31 nothing was recognised yet: a 3000.00 LIABILITY
    jan = m53.contract_balances(odoo_env, date_from="2026-01-01", date_to="2026-01-31")
    (row,) = [r for r in jan["rows"] if r["contract"] == contract.name]
    assert (row["contract_liability"], row["contract_asset"]) == (3000.0, 0.0)


def test_deferred_revenue_bridge_report(odoo_env, contract):
    out = m53.deferred_revenue_bridge(odoo_env, date_from="2026-02-01", date_to="2026-02-28")
    amc = [r for r in out["rows"] if r["stream"] == "AMC Service (stand-ready)"]
    assert amc, out["rows"]
    row = amc[0]
    assert row["opening"] + row["new"] - row["recognised"] - row["released"] == pytest.approx(
        row["closing"], abs=0.01
    )
    assert row["recognised"] >= 3100.0
    assert set(out["cols"]) <= set(out["labels"])


def test_kpis_read_real_balances(odoo_env, contract):
    k = m53.kpis(odoo_env)
    assert set(k) == {"deferred_revenue_balance", "recognised_mtd", "escrow_held_amount"}
    assert k["deferred_revenue_balance"] >= 33400.0  # 36,500 - 3,100 still deferred


def test_generic_action_endpoint_runs_and_refuses_cleanly(odoo_env, contract):
    class FakeRequest:
        def __init__(self, env):
            self.env = env

    with mock.patch.object(api, "request", FakeRequest(odoo_env)):
        ctl = api.P03GenericApiController()
        schedule = contract.obligation_ids.schedule_id
        res = ctl.model_action(
            model="fix.revenue.schedule", ids=[schedule.id], method="action_recognize_period"
        )
        assert res["success"] is True
        assert schedule.recognized_amount > 3100.0  # recognised up to today
        run = odoo_env["fix.payout.run"].create({"period": "2026-10"})
        res = ctl.model_action(
            model="fix.payout.run", ids=[run.id], method="action_post_payout_to_gl"
        )
        assert res["success"] is False and "only a confirmed" in res["error"]
        res = ctl.model_records(
            model="fix.performance.obligation",
            cols=["name", "allocated_amount", "state"],
            state_field="state",
            state_filter="scheduled",
        )
        assert any(r["name"] == "AMC visits" for r in res["rows"])
