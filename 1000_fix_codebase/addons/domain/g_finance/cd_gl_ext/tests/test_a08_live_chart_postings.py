# Every account the statutory chart links, through every automated posting helper.
#
# The first run on a copy of live data found that no bill could be marked paid: the
# payment line on the bank account had no branch, and the test database had no statutory
# chart, so no test had ever met the rule. Linking the chart in the harness covered most
# paths, and measuring it showed what it did not: treasury, payroll and import suites use
# their own account codes, and 8 of the 17 linked accounts were never met, among them TDS
# payable, input VAT and salaries. These tests reach them all, on the real chart codes.
from __future__ import annotations

from datetime import date

import pytest
from odoo.addons.cd_ap_ext.models.ap_gl import post_ap_move
from odoo.addons.cd_cash_position.models.treasury_common import post_treasury_move
from odoo.addons.cd_gl_ext.models.fix_chart_loader import ODOO_CHART_MAPPING
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.addons.cd_payroll_bd.models.fix_payroll_disbursement import post_two_line_entry
from odoo.addons.cd_tax_engine_bd.models.fix_tax_compliance import post_tax_move
from odoo.exceptions import UserError

ENTRY_DATE = date(2030, 3, 15)  # after any lock a shared test database might carry


def _account(env, code):
    account = (
        env["account.account"]
        .with_company(env.company)
        .search([("code", "=", code), ("company_ids", "in", env.company.id)], limit=1)
    )
    assert account, "chart code %s is not in the test company's chart" % code
    return account


def _other_side(env):
    """A line on an account the statutory chart does not link, so it adds no rule."""
    return _account(env, "101404")  # Outstanding Payments


def _journal(env):
    return env["account.journal"].search(
        [("type", "=", "general"), ("company_id", "=", env.company.id)], limit=1
    )


def _dimensions_on(env, move, account):
    line = move.line_ids.filtered(lambda ln: ln.account_id == account)
    return env["fix.journal.dimension"].search([("move_line_id", "in", line.ids)])


def _required_by_chart(env, code):
    row = env["fix.chart.account"].search(
        [("company_id", "=", env.company.id), ("account_code", "=", ODOO_CHART_MAPPING[code])],
        limit=1,
    )
    return {d.strip() for d in (row.requires_dimension or "").split(";") if d.strip()}


def _vals(env, account, other):
    return {
        "move_type": "entry",
        "journal_id": _journal(env).id,
        "company_id": env.company.id,
        "date": ENTRY_DATE,
        "ref": "A08 live chart",
        "line_ids": [
            (0, 0, {"account_id": account.id, "name": "x", "debit": 100.0, "credit": 0.0}),
            (0, 0, {"account_id": other.id, "name": "x", "debit": 0.0, "credit": 100.0}),
        ],
    }


# ------------------------------------------------------ every linked account, both doors
@pytest.mark.parametrize("code", sorted(ODOO_CHART_MAPPING))
def test_a_subledger_posting_meets_every_linked_account(odoo_env, code):
    """The default fills what the chart requires, and the row records it."""
    env = odoo_env
    account = _account(env, code)
    move, _dims = post_with_dimensions(
        env, _vals(env, account, _other_side(env)), {}, source="treasury"
    )
    assert move.state == "posted"
    required = _required_by_chart(env, code)
    assert required, "%s has no rule, so this test proves nothing about it" % code
    row = _dimensions_on(env, move, account)
    if "branch" in required:
        assert row.branch_id.code == "HO"
    if "cost_centre" in required:
        assert row.cost_centre == "CORP"
    if "business_line" in required:
        assert row.business_line == "SERVICE"


@pytest.mark.parametrize("code", sorted(ODOO_CHART_MAPPING))
def test_a_caller_that_must_state_dimensions_is_refused_on_every_linked_account(odoo_env, code):
    """Proves the rule is really on: the default is not a hole in it."""
    env = odoo_env
    with pytest.raises(UserError, match="Posting requires dimension"), env.cr.savepoint():
        post_with_dimensions(
            env, _vals(env, _account(env, code), _other_side(env)), {}, source="api"
        )


# ------------------------------------------------------ every automated posting helper
def test_payables_bill_meets_rent_input_vat_tds_and_trade_payables(odoo_env):
    env = odoo_env
    rent, vat, payable, tds = (_account(env, c) for c in ("612000", "131000", "211000", "252000"))
    move = post_ap_move(
        env,
        env.company,
        _journal(env),
        ENTRY_DATE,
        "A08 bill",
        [
            (rent, "rent", 1000.0, 0.0, None),
            (vat, "input VAT", 150.0, 0.0, None),
            (payable, "payable", 0.0, 1050.0, None),
            (tds, "TDS", 0.0, 100.0, None),
        ],
    )
    assert move.state == "posted"
    assert _dimensions_on(env, move, rent).branch_id.code == "HO"
    assert _dimensions_on(env, move, vat).cost_centre


def test_treasury_payment_meets_the_bank_and_its_charges(odoo_env):
    env = odoo_env
    bank, charges = _account(env, "101401"), _account(env, "620000")
    move = post_treasury_move(
        env,
        env.company,
        ENTRY_DATE,
        "A08 bank charge",
        [(charges, "charge", 50.0, 0.0, None), (bank, "charge", 0.0, 50.0, None)],
    )
    assert move.state == "posted"
    assert _dimensions_on(env, move, bank).branch_id.code == "HO"


@pytest.mark.parametrize("code", ["252000", "251000"])
def test_tax_deposit_meets_the_liability_and_the_bank(odoo_env, code):
    """A TDS or VAT challan: refused on live before, with no branch and no cost centre."""
    env = odoo_env
    liability, bank = _account(env, code), _account(env, "101401")
    move = post_tax_move(
        env,
        env.company,
        _journal(env),
        ENTRY_DATE,
        "A08 challan",
        [(liability, "deposit", 500.0, 0.0, None), (bank, "deposit", 0.0, 500.0, None)],
    )
    assert move.state == "posted"
    assert _dimensions_on(env, move, bank).branch_id.code == "HO"


def test_payroll_entry_meets_salary_expense_and_salaries_payable(odoo_env):
    """A bonus or off-cycle entry names no branch at all: it would have been refused."""
    env = odoo_env
    company = env.company.sudo()
    company.write(
        {
            "payroll_journal_id": _journal(env).id,
            "payroll_salary_expense_account_id": _account(env, "630000").id,
            "payroll_net_payable_account_id": _account(env, "230000").id,
        }
    )
    move = post_two_line_entry(
        env,
        company,
        "A08 payroll",
        ENTRY_DATE,
        1000.0,
        "bonus",
        "payroll_salary_expense_account_id",
        "payroll_net_payable_account_id",
    )
    assert move.state == "posted"
    payable = _dimensions_on(env, move, _account(env, "230000"))
    assert payable.branch_id.code == "HO" and payable.cost_centre == "CORP"


def test_cost_allocation_takes_the_default_for_what_its_rule_leaves_blank(odoo_env):
    """A rule splits an allocation, with no one to ask. Its control checks still apply."""
    env = odoo_env
    move, _dims = post_with_dimensions(
        env,
        _vals(env, _account(env, "612000"), _other_side(env)),
        {},
        source="allocation",
    )
    assert move.state == "posted"
    assert _dimensions_on(env, move, _account(env, "612000")).branch_id.code == "HO"


def test_no_default_means_the_refusal_stands(odoo_env):
    """A database with no configured default fails closed, as a fresh install must."""
    env = odoo_env
    env["ir.config_parameter"].sudo().set_param("cd_gl_ext.default_branch_code", False)
    with pytest.raises(UserError, match="branch"), env.cr.savepoint():
        post_with_dimensions(
            env, _vals(env, _account(env, "101401"), _other_side(env)), {}, source="treasury"
        )
