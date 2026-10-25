# A08 · M54 — behaviour of every controllers/a08/m54.py REPORTS function, the
# kpis(env) hook and the SURFACES actions, on a private company in the
# rolled-back fix_test transaction. Expected figures are worked by hand.
from __future__ import annotations

import itertools
import uuid
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from odoo import Command, fields
from odoo.addons.cd_p03_portal.controllers.a08 import m54
from odoo.exceptions import AccessError

pytestmark = [pytest.mark.financial]

_SEQ = itertools.count(1)


@pytest.fixture
def world(odoo_env):
    """Company + OU + two branches; GL postings dated today; one service
    order at Dhanmondi with an issued invoice, a consumption scan, two
    work-order hours and an approved payslip for its technician."""
    tag = uuid.uuid4().hex[:6].upper()
    root = odoo_env
    company = root["res.company"].create({"name": f"M54 Report Co {tag}"})
    root.user.write({"company_ids": [Command.link(company.id)]})
    env = root(context=dict(root.context, allowed_company_ids=[company.id]))
    today = fields.Date.context_today(env.user)
    ou = env["operating.unit"].create(
        {
            "name": f"M54 OU {tag}",
            "code": f"M{tag}",
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    entity = env["fix.entity"].create(
        {"code": f"E{tag}", "legal_name": "M54 Entity", "company_id": company.id}
    )
    dhk = env["fix.branch"].create(
        {
            "code": f"D{tag[:4]}",
            "name": "Dhanmondi",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    ctg = env["fix.branch"].create(
        {
            "code": f"C{tag[:4]}",
            "name": "Chattogram",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    journal = env["account.journal"].create(
        {"name": "M54 Misc", "code": f"M{tag[:4]}", "type": "general", "company_id": company.id}
    )

    def account(code, name, account_type):
        return (
            env["account.account"]
            .with_company(company)
            .create(
                {
                    "name": name,
                    "code": code,
                    "account_type": account_type,
                    "company_ids": [(6, 0, company.ids)],
                }
            )
        )

    acc = SimpleNamespace(
        income=account("410101", "Repair revenue", "income"),
        direct=account("510101", "Parts consumed", "expense_direct_cost"),
        rent=account("610101", "Branch rent", "expense"),
        bank=account("110101", "Bank", "asset_cash"),
    )

    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    def post(account_, amount, branch=None, business_line=None, credit=False):
        pnl = {"name": "P&L", "account_id": account_.id, "debit": 0.0, "credit": 0.0}
        bank = {"name": "Bank", "account_id": acc.bank.id, "debit": 0.0, "credit": 0.0}
        if credit:
            pnl["credit"], bank["debit"] = amount, amount
        else:
            pnl["debit"], bank["credit"] = amount, amount
        tag_ = {}
        if branch:
            tag_.update(branch_id=branch.id, operating_unit_id=ou.id)
        if business_line:
            tag_["business_line"] = business_line
        post_with_dimensions(
            env,
            {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": today,
                "line_ids": [(0, 0, pnl), (0, 0, bank)],
            },
            {0: tag_} if tag_ else {},
        )

    post(acc.income, 100000.0, branch=dhk, business_line="BL-02", credit=True)
    post(acc.direct, 30000.0, branch=dhk, business_line="BL-02")
    post(acc.income, 20000.0, branch=ctg, business_line="RETAIL", credit=True)
    post(acc.rent, 50000.0, branch=ctg)

    # operations: one service order at Dhanmondi
    brand = env["fix.brand"].create({"name": f"M54Brand{tag}", "code": f"B{tag}"})
    model = env["fix.device.model"].create({"name": "M54 Phone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": f"M54 Customer {tag}"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": f"SN-{tag}"}
    )
    tech = env["hr.employee"].create({"name": f"M54 Technician {tag}"})
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": dhk.id,
            "fault_description": "No display",
        }
    )
    order.write({"state": "intake"})
    start = datetime.combine(today, datetime.min.time()) + timedelta(hours=4)
    env["fix.work.order"].create(
        {
            "order_id": order.id,
            "technician_id": tech.id,
            "start_time": start,
            "end_time": start + timedelta(hours=2),
            "state": "completed",
            # M22 dispatch gating (cd_competency) is not under test here
            "certification_waiver": True,
            "certification_waiver_reason": "M54 costing test",
        }
    )
    invoice = env["fix.ar.invoice"].create(
        {
            "operating_unit_id": ou.id,
            "branch_id": dhk.id,
            "customer_id": customer.id,
            "source_model": "fix.service.order",
            "source_id": order.id,
            "state": "issued",
            "line_ids": [
                (0, 0, {"description": "Screen", "taxable_amount": 5000.0, "vat_amount": 750.0})
            ],
        }
    )
    part = env["fix.spare.part"].create(
        {
            "name": "M54 display",
            "part_number": f"PN-{tag}",
            "barcode": f"BC-{tag}",
            "unit_cost": 450.0,
            "qty_available": 5.0,
        }
    )
    location = env["fix.stock.location"].create({"name": "M54 store", "code": f"L{tag}"})
    env["fix.stock.consumption"].create(
        {
            "service_order_ref": order.name,
            "product_id": part.id,
            "location_id": location.id,
            "technician_id": tech.id,
            "scanned_code": f"PN-{tag}",
            "quantity": 2.0,
            "unit_cost": 450.0,
            "state": "consumed",
        }
    )
    period = env["fix.payroll.period"].create(
        {
            "name": f"M54 payroll {tag}",
            "period_start": today.replace(day=1),
            "period_end": today,
            "state": "approved",
        }
    )
    slip = env["fix.payslip"].create(
        {"period_id": period.id, "employee_id": tech.id, "basic": 30000.0}
    )
    # the window is today only: the period's cost is prorated to one day of it
    period_days = (today - today.replace(day=1)).days + 1
    payroll = (slip.gross + slip.pf_employer) / period_days
    return SimpleNamespace(
        env=env,
        today=today,
        dhk=dhk,
        ctg=ctg,
        acc=acc,
        order=order,
        invoice=invoice,
        tech=tech,
        customer=customer,
        payroll=payroll,
        company=company,
    )


def _run(world, name, **params):
    return m54.REPORTS[name](
        world.env, date_from=str(world.today), date_to=str(world.today), **params
    )


def _user(env, *groups):
    n = next(_SEQ)
    return env["res.users"].create(
        {
            "name": f"M54 Report User {n}",
            "login": f"m54-report-{n}-{uuid.uuid4().hex[:6]}@test.local",
            "company_id": env.company.id,
            "company_ids": [Command.set(env.companies.ids)],
            "group_ids": [Command.set([env.ref(g).id for g in groups])],
        }
    )


def _shape(out):
    assert set(out) >= {"cols", "labels", "rows"}
    for col in out["cols"]:
        assert col in out["labels"], col
    for row in out["rows"]:
        assert set(out["cols"]) <= set(row), row


def test_every_report_is_wired_and_returns_the_table_shape(world):
    assert set(m54.REPORTS) == {
        "job_costing",
        "job_margin_distribution",
        "technician_loaded_cost",
        "business_line_pnl",
        "branch_profitability",
        "customer_profitability",
        "unit_economics",
        "budget_variance",
        "rolling_forecast",
        "board_pack",
    }
    for name in m54.REPORTS:
        _shape(_run(world, name))


def test_business_line_pnl_takes_names_from_master_data(world):
    out = _run(world, "business_line_pnl")
    rows = {r["code"]: r for r in out["rows"]}
    bl02 = rows["BL-02"]
    assert bl02["line"] == "Out-of-warranty paid repair"
    assert (bl02["revenue"], bl02["direct"], bl02["gross"]) == (100000.0, 30000.0, 70000.0)
    assert bl02["margin_pct"] == 70.0
    assert rows["RETAIL"]["line"] == "Not in business-line master data"
    assert rows["—"]["opex"] == 50000.0  # the untagged rent
    assert out["totals"]["contribution"] == 40000.0  # 120000 - 30000 - 50000
    assert any("WRN-DIM-006" in n for n in out["notes"])
    assert out["title"].startswith("Business-line P&L")


def test_branch_league_ranks_by_contribution(world):
    out = _run(world, "branch_profitability")
    ranked = [r for r in out["rows"] if r["rank"]]
    assert [r["branch"].split(" ", 1)[1] for r in ranked] == ["Dhanmondi", "Chattogram"]
    dhk, ctg = ranked
    assert (dhk["contribution"], dhk["jobs"], dhk["per_job"]) == (70000.0, 1, 70000.0)
    assert ctg["contribution"] == -30000.0  # 20000 revenue - 50000 rent
    assert any("1 branch(es) with negative contribution" in n for n in out["notes"])


def test_job_costing_uses_scans_invoices_and_loaded_rate(world):
    out = _run(world, "job_costing")
    (row,) = out["rows"]
    rate = world.payroll / 2.0  # no overhead pool: payroll / 2 productive hours
    assert row["order"] == world.order.name
    assert row["revenue"] == 5000.0  # taxable value, VAT excluded
    assert row["parts_cost"] == 900.0  # 2 x 450 consumption scan
    assert row["labour_hours"] == 2.0
    assert row["labour_cost"] == pytest.approx(round(2.0 * rate, 2))
    assert row["margin"] == pytest.approx(round(5000.0 - 900.0 - 2.0 * rate, 2))
    assert row["gaps"] == "complete"


def test_job_costing_reports_missing_labour_hours_honestly(world):
    world.order.work_order_ids.unlink()
    (row,) = _run(world, "job_costing")["rows"]
    assert "no labour hours recorded" in row["gaps"]
    assert row["labour_cost"] == 0.0
    dist = _run(world, "job_margin_distribution")
    incomplete = next(r for r in dist["rows"] if r["band"].startswith("Costing incomplete"))
    assert incomplete["jobs"] == 1


def test_technician_loaded_cost_needs_payroll_or_manager_access(world):
    out = _run(world, "technician_loaded_cost")
    (row,) = out["rows"]
    assert row["hours"] == 2.0
    assert row["rate"] == pytest.approx(round(world.payroll / 2.0, 2))
    clerk = _user(world.env, "account.group_account_readonly")
    with pytest.raises(AccessError):
        m54.REPORTS["technician_loaded_cost"](world.env(user=clerk))


def test_customer_and_unit_economics(world):
    cust = _run(world, "customer_profitability")
    (row,) = cust["rows"]
    assert (row["rank"], row["decile"], row["orders"]) == (1, 1, 1)
    assert row["revenue"] == 5000.0
    unit = _run(world, "unit_economics")
    (cat,) = unit["rows"]
    assert (cat["orders"], cat["costed"], cat["rev_per_order"], cat["parts_per_order"]) == (
        1,
        1,
        5000.0,
        900.0,
    )


def test_budget_variance_reads_approved_versions_only(world):
    env = world.env
    version = env["fix.budget.version"].create(
        {
            "name": "M54 report budget",
            "fiscal_year": "FYX",
            "date_from": world.today.replace(day=1),
            "date_to": world.today,
        }
    )
    env["fix.budget"].create(
        {
            "name": "Rent",
            "version_id": version.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": world.acc.rent.id,
                        "branch_id": world.ctg.id,
                        "date_from": world.today.replace(day=1),
                        "date_to": world.today,
                        "planned_amount": 45000.0,
                    },
                )
            ],
        }
    )
    assert _run(world, "budget_variance")["rows"] == []  # draft: not reported
    submitter = _user(env, "account.group_account_user")
    version.with_user(submitter).action_submit()
    version.action_approve()
    out = _run(world, "budget_variance")
    (row,) = out["rows"]
    assert (row["planned"], row["actual"], row["variance"], row["flag"]) == (
        45000.0,
        50000.0,
        -5000.0,
        "Adverse",
    )
    kp = m54.kpis(env)
    assert kp["fpa_budget_variance_fytd"] == -5000.0


def test_rolling_forecast_and_board_pack(world):
    out = _run(world, "rolling_forecast")
    (row,) = out["rows"]
    assert row["basis"] == "Actual (month to date)"
    assert (row["revenue"], row["cost"], row["net"]) == (120000.0, 80000.0, 40000.0)
    board = _run(world, "board_pack")
    metrics = {r["metric"]: r for r in board["rows"]}
    assert metrics["Revenue"]["amount"] == 120000.0
    assert metrics["Operating result"]["amount"] == 40000.0
    assert "Dhanmondi" in metrics["Top branch"]["detail"]
    assert metrics["Window net result (actual + forecast)"]["amount"] == 40000.0


def test_kpis_are_real_metrics(world):
    kp = m54.kpis(world.env)
    assert kp["fpa_branch_top"].endswith("Dhanmondi")
    assert kp["fpa_negative_branches"] == 1
    assert kp["fpa_job_costing_coverage"] == "100.0%"


def test_surface_actions_exist_on_their_models(odoo_env):
    for model, conf in m54.SURFACES.items():
        assert model in odoo_env, model
        for method in conf["actions"]:
            assert callable(getattr(odoo_env[model], method, None)), f"{model}.{method}"
