# A08 · M19 — the backend of the added screens (controllers/a08/m19.py):
# the REPORTS functions (due-to/due-from balances, close SLA breaches), the
# kpis(env) hook and the workflow actions reached through the generic
# /p03/model/* endpoints. Live ORM on the rolled-back fix_test database.
from __future__ import annotations

import datetime
import itertools
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a08 import m19

_SEQ = itertools.count(1)


class _FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", _FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


def _company(env):
    return env["res.company"].create({"name": f"M19 Report Co {next(_SEQ)}"})


def _entity(env):
    n = next(_SEQ)
    return env["fix.entity"].create(
        {"code": f"MR{n}", "legal_name": f"M19 Entity {n}", "company_id": _company(env).id}
    )


def _journal(env, company):
    n = next(_SEQ)
    return env["account.journal"].create(
        {"name": f"MR J{n}", "code": f"R{n:04d}", "type": "general", "company_id": company.id}
    )


def _acc(env, company, account_type):
    n = next(_SEQ)
    return env["account.account"].create(
        {
            "code": f"8{n:05d}",
            "name": f"MR {account_type} {n}",
            "account_type": account_type,
            "company_ids": [(6, 0, company.ids)],
        }
    )


def _rule(env, src, tgt):
    sc, tc = src.company_id, tgt.company_id
    return env["fix.intercompany.rule"].create(
        {
            "name": "Recharge",
            "code": f"MRR-{next(_SEQ)}",
            "source_entity_id": src.id,
            "target_entity_id": tgt.id,
            "source_journal_id": _journal(env, sc).id,
            "source_receivable_account_id": _acc(env, sc, "asset_current").id,
            "source_income_account_id": _acc(env, sc, "income").id,
            "target_journal_id": _journal(env, tc).id,
            "target_expense_account_id": _acc(env, tc, "expense").id,
            "target_payable_account_id": _acc(env, tc, "liability_current").id,
        }
    )


def _txn(env, rule, amount, day="2026-04-10"):
    return env["fix.intercompany.transaction"].create(
        {
            "name": "Shared service",
            "rule_id": rule.id,
            "source_entity_id": rule.source_entity_id.id,
            "target_entity_id": rule.target_entity_id.id,
            "amount": amount,
            "currency_id": rule.source_entity_id.company_id.currency_id.id,
            "transaction_date": day,
        }
    )


def _row(report, origin):
    rows = [r for r in report["rows"] if r["origin"] == origin]
    assert len(rows) == 1, report["rows"]
    return rows[0]


# --------------------------------------------------------------------------- ic_balances


def test_ic_balances_come_from_the_posted_due_lines(odoo_env):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    rule = _rule(odoo_env, src, tgt)
    for amount in (1_000.0, 250.0):
        _txn(odoo_env, rule, amount).action_generate_mirror()
    _txn(odoo_env, rule, 99.0)  # draft: nothing posted, not a balance
    _txn(odoo_env, rule, 77.0, day="2026-12-01").action_generate_mirror()  # after as-of

    report = m19.ic_balances(odoo_env, date_to="2026-06-30")

    row = _row(report, src.code)
    assert row["counterparty"] == tgt.code
    assert (row["open_count"], row["due_from"], row["due_to"], row["difference"]) == (
        2,
        1_250.0,
        1_250.0,
        0.0,
    )
    assert set(report["cols"]) <= set(report["labels"])
    assert report["title"].endswith("2026-06-30")


def test_ic_balances_show_an_out_of_balance_pair(odoo_env):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    txn = _txn(odoo_env, _rule(odoo_env, src, tgt), 500.0)
    txn.action_generate_mirror()
    txn.target_move_id.button_draft()  # the counterparty un-posts its side
    txn.action_match()

    row = _row(m19.ic_balances(odoo_env, date_to="2026-06-30"), src.code)
    assert (row["due_from"], row["due_to"], row["difference"], row["disputed"]) == (
        500.0,
        0.0,
        500.0,
        1,
    )


def test_ic_balances_drop_settled_transactions(odoo_env):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    txn = _txn(odoo_env, _rule(odoo_env, src, tgt), 300.0)
    txn.action_generate_mirror()
    txn.state = "settled"
    report = m19.ic_balances(odoo_env, date_to="2026-06-30")
    assert not [r for r in report["rows"] if r["origin"] == src.code]


# --------------------------------------------------------------------------- close_sla


def test_close_sla_lists_late_and_overdue_closes(odoo_env):
    company = _company(odoo_env)
    Close = odoo_env["fix.period.close"].with_context(allowed_company_ids=company.ids)
    late = Close.create({"company_id": company.id, "period_end": datetime.date(2019, 1, 31)})
    late.write({"state": "closed", "closed_at": datetime.datetime(2019, 2, 12, 10, 0)})
    on_time = Close.create({"company_id": company.id, "period_end": datetime.date(2019, 2, 28)})
    on_time.write({"state": "closed", "closed_at": datetime.datetime(2019, 3, 3, 10, 0)})
    overdue = Close.create({"company_id": company.id, "period_end": datetime.date(2019, 3, 31)})

    report = m19.close_sla(Close.env)

    by_end = {r["period_end"]: r for r in report["rows"]}
    assert by_end["2019-01-31"]["status"] == "Closed late"
    assert by_end["2019-01-31"]["over_target"] == 7.0  # 12 days vs 5
    assert "2019-02-28" not in by_end
    days_open = (datetime.date.today() - overdue.period_end).days
    assert by_end["2019-03-31"] == {
        "period_end": "2019-03-31",
        "status": "Open past target",
        "days": float(days_open),
        "over_target": float(days_open - 5),
    }


# --------------------------------------------------------------------------- kpis


def test_kpis_gross_margin_and_unmatched_count(odoo_env):
    company = _company(odoo_env)
    env = odoo_env(context=dict(odoo_env.context, allowed_company_ids=company.ids))
    assert m19.kpis(env)["gross_margin_mtd"] is None  # no revenue: no ratio
    journal = _journal(env, company)
    income, cogs, cash = (
        _acc(env, company, "income"),
        _acc(env, company, "expense_direct_cost"),
        _acc(env, company, "asset_cash"),
    )
    move = env["account.move"].create(
        {
            "journal_id": journal.id,
            "company_id": company.id,
            "date": fields.Date.context_today(journal),
            "line_ids": [
                (0, 0, {"name": "sale", "account_id": income.id, "credit": 1_000.0}),
                (0, 0, {"name": "cogs", "account_id": cogs.id, "debit": 600.0}),
                (0, 0, {"name": "cash", "account_id": cash.id, "debit": 400.0}),
            ],
        }
    )
    move.action_post()
    out = m19.kpis(env)
    assert out["gross_margin_mtd"] == "40.0%"
    assert isinstance(out["ic_unmatched"], int)


# --------------------------------------------------------------------------- generic endpoints


def test_mirror_and_match_through_the_workspace_action(odoo_env, call):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    txn = _txn(odoo_env, _rule(odoo_env, src, tgt), 640.0)
    model = "fix.intercompany.transaction"
    res = call(odoo_env, "model_action", model=model, ids=[txn.id], method="action_generate_mirror")
    assert res == {"success": True, "result": {}}
    assert txn.state == "pending_matching"
    res = call(odoo_env, "model_action", model=model, ids=[txn.id], method="action_match")
    assert res["success"] and txn.state == "matched"
    res = call(odoo_env, "model_action", model=model, ids=[txn.id], method="unlink")
    assert res == {"success": False, "error": "Action not available for this surface"}


def test_refused_action_leaves_nothing_behind(odoo_env, call):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    txn = odoo_env["fix.intercompany.transaction"].create(
        {"name": "No rule", "source_entity_id": src.id, "target_entity_id": tgt.id, "amount": 5.0}
    )
    res = call(
        odoo_env,
        "model_action",
        model="fix.intercompany.transaction",
        ids=[txn.id],
        method="action_generate_mirror",
    )
    assert res["success"] is False and "rule" in res["error"]
    assert txn.state == "draft" and not txn.source_move_id


def test_model_records_serves_the_added_surfaces(odoo_env, call):
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    rule = _rule(odoo_env, src, tgt)
    res = call(
        odoo_env,
        "model_records",
        model="fix.intercompany.rule",
        cols=["code", "scope", "source_entity_id", "markup_percent"],
    )
    assert "error" not in res
    row = next(r for r in res["rows"] if r["code"] == rule.code)
    assert row["scope"]["key"] == "intercompany"
    assert row["source_entity_id"]["id"] == src.id


def test_finance_reader_cannot_run_ic_actions(odoo_env, call):
    reader = odoo_env["res.users"].create(
        {
            "name": "M19 Reader",
            "login": f"m19-reader-{next(_SEQ)}@test.local",
            "group_ids": [
                (
                    6,
                    0,
                    [
                        odoo_env.ref("base.group_user").id,
                        odoo_env.ref("account.group_account_readonly").id,
                    ],
                )
            ],
        }
    )
    src, tgt = _entity(odoo_env), _entity(odoo_env)
    txn = _txn(odoo_env, _rule(odoo_env, src, tgt), 10.0)
    txn.company_id = reader.company_id
    res = call(
        odoo_env(user=reader),
        "model_action",
        model="fix.intercompany.transaction",
        ids=[txn.id],
        method="action_generate_mirror",
    )
    assert res["success"] is False
    assert txn.state == "draft"
