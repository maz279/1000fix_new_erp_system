# cd_gl_ext — a dated trial balance carries what the accounts brought into the
# period (finance audit, 10 Nov 2026).
#
# compute_trial_balance(date_from, date_to) summed only the journal items inside
# the window, so cash that held BDT 12,200 on the first day read 600 at the end
# of the month. A trial balance for a period is opening + movement = closing:
# balance-sheet accounts bring their whole history, income and expense accounts
# only this fiscal year's, and the profit or loss of earlier years sits on the
# undistributed-earnings account, so the closing column still nets to zero.
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

pytestmark = [pytest.mark.financial, pytest.mark.unlinked_chart]

D = Decimal
WINDOW = (date(2026, 10, 1), date(2026, 10, 31))


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


def _company(env, label, unaffected_account=True):
    """A chart-less company on the Bangladesh fiscal year (July to June)."""
    company = env["res.company"].create(
        {
            "name": "TB Opening %s Test Co" % label,
            "fiscalyear_last_month": "6",
            "fiscalyear_last_day": 30,
        }
    )
    env["operating.unit"].create(
        {
            "name": "OU %s" % company.name,
            "code": "OU-%s" % company.id,
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    journal = env["account.journal"].create(
        {"name": "Misc", "code": "MSC", "type": "general", "company_id": company.id}
    )
    Account = env["account.account"].with_company(company)

    def account(code, name, account_type):
        return Account.create(
            {
                "name": name,
                "code": code,
                "account_type": account_type,
                "company_ids": [(6, 0, company.ids)],
            }
        )

    accs = {
        "journal": journal,
        "cash": account("101401", "Bank", "asset_cash"),
        "capital": account("300001", "Share Capital", "equity"),
        "income": account("400001", "Income", "income"),
        "expense": account("500001", "Expense", "expense"),
    }
    if unaffected_account:
        accs["unaffected"] = account("399999", "Undistributed Profits", "equity_unaffected")
    return company, accs


def _post(env, accs, on, debit, credit, amount):
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    journal = accs["journal"]
    move, _dims = post_with_dimensions(
        env,
        {
            "journal_id": journal.id,
            "company_id": journal.company_id.id,
            "date": on,
            "line_ids": [
                (
                    0,
                    0,
                    {"name": "dr", "account_id": accs[debit].id, "debit": amount, "credit": 0.0},
                ),
                (
                    0,
                    0,
                    {"name": "cr", "account_id": accs[credit].id, "debit": 0.0, "credit": amount},
                ),
            ],
        },
        {},
        source="api",
    )
    assert move.state == "posted"
    return move


def _history(env, accs):
    """Entries before the fiscal year, in it before the window, inside the
    window, and after it."""
    _post(env, accs, date(2026, 3, 10), "cash", "capital", 10000.0)  # earlier fiscal year
    _post(env, accs, date(2026, 3, 11), "cash", "income", 2000.0)  # earlier year's profit
    _post(env, accs, date(2026, 8, 5), "cash", "income", 500.0)  # this year, before
    _post(env, accs, date(2026, 9, 5), "expense", "cash", 300.0)  # this year, before
    _post(env, accs, date(2026, 10, 10), "cash", "income", 700.0)  # inside
    _post(env, accs, date(2026, 10, 20), "expense", "cash", 100.0)  # inside
    _post(env, accs, date(2026, 11, 2), "cash", "income", 50.0)  # after


def _rows(report):
    return {row["account_code"]: row for row in report["lines"]}


class TestDatedTrialBalance:
    def test_opening_plus_movement_is_closing(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import compute_trial_balance

        company, accs = _company(odoo_env, "carry")
        _history(odoo_env, accs)
        tb = compute_trial_balance(odoo_env, company, *WINDOW)
        rows = _rows(tb)

        # the bank brought 10,000 + 2,000 + 500 - 300 into October
        cash = rows["101401"]
        assert _money(cash["balance"]) == D("12800.00")
        assert _money(cash["opening_balance"]) == D("12200.00")
        assert (_money(cash["debit"]), _money(cash["credit"])) == (D("700.00"), D("100.00"))
        # an account that did not move in the window still shows what it holds
        capital = rows["300001"]
        assert _money(capital["opening_balance"]) == D("-10000.00")
        assert (_money(capital["debit"]), _money(capital["credit"])) == (D("0.00"), D("0.00"))
        assert _money(capital["balance"]) == D("-10000.00")
        # income and expense: this fiscal year only (July onwards)
        assert _money(rows["400001"]["opening_balance"]) == D("-500.00")
        assert _money(rows["400001"]["balance"]) == D("-1200.00")
        assert _money(rows["500001"]["opening_balance"]) == D("300.00")
        assert _money(rows["500001"]["balance"]) == D("400.00")
        # the earlier year's profit is on the undistributed-earnings account
        assert _money(rows["399999"]["opening_balance"]) == D("-2000.00")
        assert _money(rows["399999"]["balance"]) == D("-2000.00")

        for row in tb["lines"]:
            assert _money(row["opening_balance"]) + _money(row["debit"]) - _money(
                row["credit"]
            ) == _money(row["balance"]), row
        # period movement: debits = credits
        assert _money(tb["total_debit"]) == _money(tb["total_credit"]) == D("800.00")
        # opening and closing columns each net to zero
        assert sum(_money(r["opening_balance"]) for r in tb["lines"]) == D("0.00")
        assert sum(_money(r["balance"]) for r in tb["lines"]) == D("0.00")
        assert _money(tb["total_closing_debit"]) == _money(tb["total_closing_credit"])
        assert _money(tb["total_closing_debit"]) == D("13200.00")  # bank 12,800 + expense 400
        assert tb["balanced"] is True

    def test_closing_agrees_with_the_balance_sheet(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import (
            compute_balance_sheet,
            compute_trial_balance,
        )

        company, accs = _company(odoo_env, "agree")
        _history(odoo_env, accs)
        tb = _rows(compute_trial_balance(odoo_env, company, *WINDOW))
        bs = _rows(compute_balance_sheet(odoo_env, company, WINDOW[1]))
        assert _money(tb["101401"]["balance"]) == _money(bs["101401"]["balance"])
        assert _money(tb["300001"]["balance"]) == _money(bs["300001"]["balance"])

    def test_earlier_years_profit_without_an_earnings_account_gets_its_own_line(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import compute_trial_balance

        company, accs = _company(odoo_env, "noacc", unaffected_account=False)
        _history(odoo_env, accs)
        tb = compute_trial_balance(odoo_env, company, *WINDOW)
        earlier = [r for r in tb["lines"] if not r["account_code"]]
        assert len(earlier) == 1
        assert _money(earlier[0]["opening_balance"]) == D("-2000.00")
        assert _money(earlier[0]["balance"]) == D("-2000.00")
        assert sum(_money(r["balance"]) for r in tb["lines"]) == D("0.00")
        assert tb["balanced"] is True

    def test_window_from_the_first_day_of_the_fiscal_year(self, odoo_env):
        """Income and expense start the fiscal year at zero."""
        from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import compute_trial_balance

        company, accs = _company(odoo_env, "fystart")
        _history(odoo_env, accs)
        tb = compute_trial_balance(odoo_env, company, date(2026, 7, 1), date(2026, 10, 31))
        rows = _rows(tb)
        assert _money(rows["400001"]["opening_balance"]) == D("0.00")
        assert _money(rows["400001"]["balance"]) == D("-1200.00")
        assert _money(rows["101401"]["opening_balance"]) == D("12000.00")
        assert _money(rows["101401"]["balance"]) == D("12800.00")
        assert _money(rows["399999"]["opening_balance"]) == D("-2000.00")
        assert tb["balanced"] is True

    def test_single_company_statements_hold_only_that_company(self, odoo_env):
        """Company fence: another company's entries on the same account codes
        reach none of this company's statements."""
        from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import (
            compute_balance_sheet,
            compute_pnl,
            compute_trial_balance,
        )

        company, accs = _company(odoo_env, "fence-a")
        _history(odoo_env, accs)
        other, other_accs = _company(odoo_env, "fence-b")
        _post(odoo_env, other_accs, date(2026, 9, 1), "cash", "capital", 99000.0)
        _post(odoo_env, other_accs, date(2026, 10, 12), "cash", "income", 7777.0)

        tb = compute_trial_balance(odoo_env, company, *WINDOW)
        assert _money(tb["total_debit"]) == _money(tb["total_credit"]) == D("800.00")
        assert (_money(_rows(tb)["101401"]["debit"]), _money(_rows(tb)["101401"]["credit"])) == (
            D("700.00"),
            D("100.00"),
        )
        pnl = compute_pnl(odoo_env, company, *WINDOW)
        assert _money(pnl["net_profit"]) == D("600.00")
        bs = compute_balance_sheet(odoo_env, company, WINDOW[1])
        assert _money(_rows(bs)["101401"]["balance"]) == D("12800.00")
        assert bs["balanced"] is True
        theirs = compute_trial_balance(odoo_env, other, *WINDOW)
        assert _money(theirs["total_debit"]) == D("7777.00")
        their_bs = compute_balance_sheet(odoo_env, other, WINDOW[1])
        assert _money(_rows(their_bs)["101401"]["balance"]) == D("106777.00")

    def test_an_empty_ledger_reports_zero_not_minus_zero(self, odoo_env):
        """No income or expense posted: net profit and the unclosed P&L are
        0.0, not -0.0 (the P&L screen printed "৳ -0", the packs "-0.00")."""
        import math

        from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import (
            compute_balance_sheet,
            compute_pnl,
        )

        company, accs = _company(odoo_env, "empty")
        _post(odoo_env, accs, date(2026, 10, 5), "cash", "capital", 1000.0)  # balance sheet only
        pnl = compute_pnl(odoo_env, company, *WINDOW)
        assert pnl["lines"] == []
        assert pnl["net_profit"] == 0.0
        assert math.copysign(1.0, pnl["net_profit"]) == 1.0
        assert "%.2f" % pnl["net_profit"] == "0.00"
        bs = compute_balance_sheet(odoo_env, company, WINDOW[1])
        assert math.copysign(1.0, bs["unclosed_profit_and_loss"]) == 1.0
        assert bs["balanced"] is True
