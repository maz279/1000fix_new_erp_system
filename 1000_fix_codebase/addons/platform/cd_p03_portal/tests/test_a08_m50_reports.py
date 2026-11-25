# A08 · M50 — the workspace endpoints over the treasury backend: every
# REPORTS function answers through /p03/model/report with the declared
# columns, the KPI hook returns real numbers, model screens read through
# /p03/model/records, and a workflow action runs through /p03/model/action
# (and refuses honestly). The module-level `request` is patched with the
# rolled-back odoo_env (pattern: test_p03_generic_api.py).
from __future__ import annotations

import itertools
from datetime import date, timedelta
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a08 import m50

_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call(odoo_env):
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


def _accountant(env):
    n = next(_SEQ)
    return env["res.users"].create(
        {
            "name": f"M50 Accountant {n}",
            "login": f"m50-acc-{n}@test.local",
            "group_ids": [(6, 0, [env.ref("account.group_account_user").id])],
        }
    )


def _plain_user(env):
    n = next(_SEQ)
    return env["res.users"].create(
        {
            "name": f"M50 Clerk {n}",
            "login": f"m50-clerk-{n}@test.local",
            "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        }
    )


@pytest.mark.parametrize("report", sorted(m50.REPORTS))
def test_every_report_answers_with_its_columns(odoo_env, call, report):
    today = date.today()
    params = {"date_from": str(today - timedelta(days=90)), "date_to": str(today)}
    res = call(odoo_env, "model_report", module="M50", report=report, params=params)
    assert "error" not in res, res
    assert isinstance(res["rows"], list)
    for row in res["rows"]:
        assert set(res["cols"]) <= set(row), report
    if res["cols"]:
        assert set(res["cols"]) <= set(res["labels"]), report


def test_forecast_has_trailing_actuals_and_thirteen_forward_weeks(odoo_env, call):
    res = call(odoo_env, "model_report", module="M50", report="cash_forecast", params={})
    assert len(res["rows"]) == 17
    assert all(r["closing"] is None for r in res["rows"][:4])
    assert all(r["closing"] is not None for r in res["rows"][4:])
    assert all(r["actual"] is not None for r in res["rows"][:5])


def test_kpis_are_numbers(odoo_env):
    out = m50.kpis(odoo_env)
    assert set(out) == {"cash_position", "branch_cash_uncollected", "payments_awaiting_bank"}
    assert all(isinstance(v, int | float) for v in out.values())


def test_bank_account_master_reads_journals_with_bd_fields(odoo_env, call):
    acct = odoo_env["res.partner.bank"].create(
        {
            "partner_id": odoo_env.company.partner_id.id,
            "acc_number": "M50-ACC-%s" % next(_SEQ),
            "fix_routing_number": "060261726",
            "fix_account_type": "current",
        }
    )
    journal = odoo_env["account.journal"].create(
        {"name": "M50 Test Bank", "type": "bank", "code": "M5TB", "bank_account_id": acct.id}
    )
    res = call(
        odoo_env(user=_accountant(odoo_env)),
        "model_records",
        model="account.journal",
        cols=["name", "fix_routing_number", "fix_account_type", "fix_gl_balance"],
        domain=[["type", "=", "bank"]],
    )
    row = next(r for r in res["rows"] if r["id"] == journal.id)
    assert row["fix_routing_number"] == "060261726"
    assert row["fix_account_type"]["key"] == "current"
    assert row["fix_gl_balance"] == 0.0


def test_release_action_runs_through_the_endpoint_and_refuses_honestly(odoo_env, call):
    env = odoo_env(user=_accountant(odoo_env))
    ou = odoo_env["operating.unit"].search([("company_id", "=", odoo_env.company.id)], limit=1)
    pay = odoo_env["fix.payment.execution"].create(
        {
            "operating_unit_id": ou.id,
            "source_model": "m50.endpoint.test",
            "source_id": next(_SEQ),
            "payee": "Endpoint Vendor",
            "amount": 100.0,
        }
    )
    res = call(
        env, "model_action", model="fix.payment.execution", ids=[pay.id], method="action_release"
    )
    # A08 F1: release needs a prepared (and, above the limit, authorised) instruction
    assert res["success"] is False
    assert "prepared" in res["error"]
    assert pay.state == "pending"
    res = call(
        env, "model_action", model="fix.payment.execution", ids=[pay.id], method="action_execute"
    )
    assert res == {"success": False, "error": "Action not available for this surface"}


def test_plain_employee_cannot_read_treasury_lines(odoo_env, call):
    res = call(
        odoo_env(user=_plain_user(odoo_env)),
        "model_records",
        model="fix.bank.statement.line",
        cols=["date", "amount"],
    )
    assert "error" in res
