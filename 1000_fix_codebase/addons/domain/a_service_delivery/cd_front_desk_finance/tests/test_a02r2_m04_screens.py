"""A02 pass 2: the M04 workspace figures and the books-pending screen.

- X5-20 (P2): a counter sale, a variance or a cash-out whose posting is
  pending was invisible and its retry was not served: the books-pending
  report lists them with why, and the retries are workspace actions.
- X5-24 (P3): the Branch Daily Cash Summary breaks every drawer down (sales,
  settlements, field cash, refunds, cash-outs) and adds the non-cash takings.
- M04-06 / X5-17 (P3): the M04 tile is scoped to the reader's branches and
  shows today's intake, work in progress, ready devices and takings; the
  average wait is not taken over a capped subset.
- X5-19: the basket form shows the counter sales it raised.
"""

# ruff: noqa: F811  (the posting suite's fixtures are imported and used as parameters)
import pytest
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import m04  # noqa: F401
from odoo.addons.cd_front_desk_finance.tests.test_a02r2_cash_out_posting import co  # noqa: F401
from odoo.addons.cd_front_desk_finance.tests.test_counter_sale_posting import (  # noqa: F401
    fin,
)
from odoo.addons.cd_p03_portal.controllers import a02
from odoo.addons.cd_p03_portal.controllers.a02 import m04 as m04_ctl

pytestmark = [pytest.mark.financial]

PARAM = "cd_front_desk_finance.account_code."


def test_pending_postings_are_listed_and_retried_from_the_workspace(co):
    m = co
    m.params.set_param(PARAM + "petty_expense", False)
    mv = m.cash_out(m.shift(), "petty_expense", 75.0, reason="Courier for spare")
    rows = m04_ctl.REPORTS["books_pending"](m.env)["rows"]
    row = next(r for r in rows if r["model"] == "fix.cash.movement" and r["id"] == mv.id)
    assert PARAM + "petty_expense" in row["note"] and row["retry"] == "action_retry_posting"
    assert m04_ctl.kpis(m.env)["books_pending"] >= 1
    # the retries are workspace actions
    assert "action_retry_posting" in a02.SURFACES["fix.cash.movement"]["actions"]
    assert "action_retry_posting" in a02.SURFACES["fix.counter.sale"]["actions"]
    assert "action_retry_variance_posting" in a02.SURFACES["fix.cash.shift"]["actions"]
    m.params.set_param(PARAM + "petty_expense", m.acc.misc.code)
    mv.with_user(m.cashier).action_retry_posting()
    rows = m04_ctl.REPORTS["books_pending"](m.env)["rows"]
    assert not [r for r in rows if r["model"] == "fix.cash.movement" and r["id"] == mv.id]


def test_the_daily_cash_summary_breaks_the_drawer_down(co):
    m = co
    s = m.shift()
    m.confirmed(1150.0, "cash", shift=s)  # a cash counter sale
    m.confirmed(1150.0, "bkash", shift=s, trx="BKX-SUMMARY-1")  # non-cash
    m.cash_out(s, "petty_expense", 100.0)
    m.cash_out(s, "safe_drop", 1000.0)
    report = m04_ctl.REPORTS["daily_cash"](m.env)
    row = next(r for r in report["rows"] if r.get("operator") == m.cashier_emp.name and r["sales"])
    assert (row["opening"], row["sales"], row["cash_outs"]) == (5000.0, 1150.0, 1100.0)
    assert row["expected"] == 5050.0
    day = next(
        r
        for r in report["rows"]
        if r["operator"].startswith("Non-cash") and r["branch"] == m.branch.name
    )
    assert day["non_cash"] >= 1150.0


def test_the_m04_tile_is_the_readers_branches_and_today(co):
    m = co
    k = m04_ctl.kpis(m.env(user=m.cashier.id))
    for key in (
        "intakes_today",
        "orders_wip",
        "orders_ready",
        "takings_today_bdt",
        "books_pending",
    ):
        assert key in k
    # a reader fenced to another operating unit sees none of this branch's drawers
    s = m.shift()
    m.confirmed(1150.0, "cash", shift=s)
    mine = m04_ctl.kpis(m.env(user=m.cashier.id))
    assert mine["shifts_open"] >= 1 and mine["takings_today_bdt"] >= 1150.0
    other_ou = m.env["operating.unit"].create(
        {
            "name": "R2 elsewhere",
            "code": "R2ELS%s" % m.acc.drawer.code[-4:],
            "company_id": m.env.company.id,
            "partner_id": m.env.company.partner_id.id,
        }
    )
    stranger = (
        m.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "R2 other branch",
                "login": "a02r2.other.%s@test" % m.acc.drawer.code,
                "group_ids": [(6, 0, [m.env.ref("base.group_user").id])],
            }
        )
    )
    field = (
        "assigned_operating_unit_ids"
        if "assigned_operating_unit_ids" in stranger._fields
        else "operating_unit_ids"
    )
    stranger.write({field: [(6, 0, [other_ou.id])]})
    theirs = m04_ctl.kpis(m.env(user=stranger.id))
    assert theirs["shifts_open"] == 0 and theirs["takings_today_bdt"] == 0.0


def test_the_basket_form_shows_its_counter_sales():
    from odoo.addons.cd_front_desk.tests.test_m04_build2 import _screens

    form = _screens()["M04-form-basket"]
    grid = next(g for g in form["grids"] if g["field"] == "sale_ids")
    assert grid["readonlyGrid"] and {"name", "total", "posting_state"} <= {
        f["name"] for f in grid["fields"]
    }
