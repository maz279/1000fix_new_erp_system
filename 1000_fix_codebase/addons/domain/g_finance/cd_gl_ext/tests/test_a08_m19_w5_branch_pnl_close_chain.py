# A08 wave 5 (B11) — M19-F4 branch/OU P&L, M19-F10 subledger close gate and
# M19-F11 posting-log hash chain. Live ORM on the rolled-back fix_test_w5
# database; every monetary expectation is written by hand.
from __future__ import annotations

import itertools
from datetime import date

import pytest
from odoo import Command
from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import compute_pnl
from odoo.addons.cd_gl_ext.models.fix_gl_chain import CHAIN_GENESIS, verify_chain
from odoo.addons.cd_gl_ext.models.fix_gl_dimension_pnl import pnl_by_branch
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.exceptions import UserError

pytestmark = [pytest.mark.financial]

WINDOW_FROM = date(2026, 10, 1)
WINDOW_TO = date(2026, 10, 31)
CLOSE_PERIOD = date(2026, 9, 30)
PERIOD_DATE = date(2026, 9, 15)

_SEQ = itertools.count(1)


def _journal(env, company):
    return env["account.journal"].search(
        [("type", "=", "general"), ("company_id", "=", company.id)], limit=1
    )


def _account(env, company, account_type, code_prefix, label):
    """An account the statutory chart does not link: no dimension rule applies."""
    code = "%s%05d" % (code_prefix, next(_SEQ))
    return (
        env["account.account"]
        .with_company(company)
        .create(
            {
                "name": label,
                "code": code,
                "account_type": account_type,
                "company_ids": [(6, 0, [company.id])],
            }
        )
    )


def _branch(env, company, code):
    # fix.entity is one-per-company (fix_entity_company_unique); both branches
    # hang off the company's entity, as the real branch register does.
    entity = env["fix.entity"].sudo().search([("company_id", "=", company.id)], limit=1)
    if not entity:
        entity = (
            env["fix.entity"]
            .sudo()
            .create(
                {
                    "code": "PBL%s" % company.id,
                    "legal_name": "Wave 5 P&L entity",
                    "company_id": company.id,
                }
            )
        )
    unit = env["operating.unit"].sudo().search([("company_id", "=", company.id)], limit=1)
    return (
        env["fix.branch"]
        .sudo()
        .create(
            {
                "code": code,
                "name": "Branch %s" % code,
                "entity_id": entity.id,
                "operating_unit_id": unit.id,
            }
        )
    )


def _entry_vals(env, company, day, debit, credit, amount, ref):
    return {
        "move_type": "entry",
        "journal_id": _journal(env, company).id,
        "company_id": company.id,
        "date": day,
        "ref": ref,
        "line_ids": [
            Command.create({"account_id": debit.id, "name": ref, "debit": amount, "credit": 0.0}),
            Command.create({"account_id": credit.id, "name": ref, "debit": 0.0, "credit": amount}),
        ],
    }


def _post(env, company, day, debit, credit, amount, dims, ref, source="treasury"):
    move, _dimensions = post_with_dimensions(
        env,
        _entry_vals(env, company, day, debit, credit, amount, ref),
        dims,
        source=source,
        source_ref=ref,
    )
    return move


def _post_without_dimensions(env, company, day, debit, credit, amount, ref):
    """A legacy-style posting with no fix.journal.dimension rows at all."""
    move = env["account.move"].create(_entry_vals(env, company, day, debit, credit, amount, ref))
    move.action_post()
    return move


# ------------------------------------------------------------------ (a) branch P&L
def test_branch_pnl_ties_to_company_pnl_and_shows_the_unallocated_bucket(odoo_env):
    env = odoo_env
    company = env.company
    income = _account(env, company, "income", "49", "Wave 5 service revenue")
    expense = _account(env, company, "expense", "69", "Wave 5 branch cost")
    cash = _account(env, company, "asset_cash", "109", "Wave 5 branch cash")

    branch_one = _branch(env, company, "PB1")
    branch_two = _branch(env, company, "PB2")
    dims_one = {
        0: {"branch_id": branch_one.id, "cost_centre": "CC1", "business_line": "SERVICE"},
        1: {"branch_id": branch_one.id, "cost_centre": "CC1", "business_line": "SERVICE"},
    }
    dims_two = {
        0: {"branch_id": branch_two.id, "cost_centre": "CC2", "business_line": "SERVICE"},
        1: {"branch_id": branch_two.id, "cost_centre": "CC2", "business_line": "SERVICE"},
    }
    _post(env, company, date(2026, 10, 5), cash, income, 1000.0, dims_one, "PNL-B1")
    _post(env, company, date(2026, 10, 6), expense, cash, 400.0, dims_two, "PNL-B2")
    # M19-F6's take-on lanes post P&L lines with no dimension row: the slice
    # must show them as unallocated, not silently drop them.
    _post_without_dimensions(env, company, date(2026, 10, 7), cash, income, 250.0, "PNL-NO-DIM")

    report = pnl_by_branch(env, WINDOW_FROM, WINDOW_TO)
    company_pnl = compute_pnl(env, company, WINDOW_FROM, WINDOW_TO)

    assert report["group_by"] == "branch"
    assert report["ties_to_company_pnl"] is True
    assert report["totals"]["revenue"] == 1250.0
    assert report["totals"]["expense"] == 400.0
    assert report["totals"]["net_profit"] == company_pnl["net_profit"] == 850.0
    assert report["unallocated"]["revenue"] == 250.0
    assert report["unallocated"]["expense"] == 0.0
    assert report["unallocated"]["net_profit"] == 250.0
    assert report["unallocated"]["line_count"] == 1
    assert report["unallocated"]["accounts"][0]["account_code"] == income.code

    by_branch = {row["branch_id"]: row for row in report["rows"] if row.get("branch_id")}
    assert by_branch[branch_one.id]["revenue"] == 1000.0
    assert by_branch[branch_one.id]["expense"] == 0.0
    assert by_branch[branch_two.id]["revenue"] == 0.0
    assert by_branch[branch_two.id]["expense"] == 400.0
    assert by_branch[branch_two.id]["net_profit"] == -400.0

    # The operating-unit slice groups both branches (same OU) and keeps the
    # dimension-less line unallocated; totals are the same company P&L.
    ou_report = pnl_by_branch(env, WINDOW_FROM, WINDOW_TO, group_by="operating_unit")
    assert ou_report["ties_to_company_pnl"] is True
    assert ou_report["totals"]["revenue"] == 1250.0
    assert ou_report["totals"]["expense"] == 400.0
    assert ou_report["unallocated"]["revenue"] == 250.0
    allocated = [row for row in ou_report["rows"] if row.get("operating_unit_id")]
    assert len(allocated) == 1
    assert allocated[0]["revenue"] == 1000.0 and allocated[0]["expense"] == 400.0


def test_branch_pnl_rejects_an_unknown_slice_and_an_inverted_window(odoo_env):
    with pytest.raises(UserError, match="FR-FIN-031"):
        pnl_by_branch(odoo_env, WINDOW_FROM, WINDOW_TO, group_by="warehouse")
    with pytest.raises(UserError, match="FR-FIN-031"):
        pnl_by_branch(odoo_env, WINDOW_TO, WINDOW_FROM)


# --------------------------------------------------- (b) subledger close gate
def _ar_control(env, company):
    account = (
        env["account.account"]
        .with_company(company)
        .search([("code", "=", "121000"), ("company_ids", "in", company.id)], limit=1)
    )
    assert account, "fixture: the test company has no Account Receivable 121000"
    return account


def _post_ar_move(env, company, debit_account, amount, ref, day=PERIOD_DATE):
    income = _account(env, company, "income", "47", "Wave 5 AR counterpart")
    # A negative amount is the clearing receipt: swap the two sides so no
    # journal item ever carries a negative debit/credit.
    debit, credit = (debit_account, income) if amount >= 0 else (income, debit_account)
    amount = abs(amount)
    # source "treasury" lets the chart's default branch/cost-centre fill the
    # AR control line (MD-035: receivable requires branch;cost_centre).
    return _post(env, company, day, debit, credit, amount, {}, ref, source="treasury")


def test_close_refuses_on_a_subledger_variance_and_passes_when_reconciled(odoo_env):
    env = odoo_env
    company = env.company
    ar = _ar_control(env, company)

    # An AR debit with no invoice behind it: the GL control is 100.00, the AR
    # sub-ledger is 0.00 — exactly the unexplained difference BRU-FIN-20 blocks.
    _post_ar_move(env, company, ar, 100.0, "W5-AR-OPEN")
    close = env["fix.period.close"].create({"period_end": CLOSE_PERIOD, "state": "ready_to_close"})
    with pytest.raises(UserError) as refused:
        close.action_close()
    message = str(refused.value)
    assert "FR-FIN-022" in message and "BRU-FIN-20" in message
    assert "AR — Trade receivables" in message
    assert "100.00" in message and "121000" in message
    assert close.state == "ready_to_close"
    assert not company.fiscalyear_lock_date

    # The receipt that clears the control account: GL 0.00 = sub-ledger 0.00.
    _post_ar_move(env, company, ar, -100.0, "W5-AR-CLEARED")
    close.action_close()
    assert close.state == "closed"
    assert company.fiscalyear_lock_date == CLOSE_PERIOD


def test_close_fails_closed_when_a_control_account_is_not_configured(odoo_env):
    env = odoo_env
    company = env["res.company"].create({"name": "Wave 5 Unconfigured Close Co"})
    close = env["fix.period.close"].create(
        {
            "company_id": company.id,
            "period_end": CLOSE_PERIOD,
            "state": "ready_to_close",
        }
    )
    with pytest.raises(UserError) as refused:
        close.action_close()
    message = str(refused.value)
    assert "FR-FIN-022" in message
    # fail closed with the parameter named: never a silent "reconciled" pass
    assert "cd_billing_engine.account_code.ar" in message
    assert close.state == "ready_to_close"
    assert not company.fiscalyear_lock_date


# ------------------------------------------------------ (c)/(d) audit hash chain
def _simple_post(env, company, amount, ref):
    income = _account(env, company, "income", "46", "Wave 5 chain income")
    cash = _account(env, company, "asset_cash", "108", "Wave 5 chain cash")
    return _post(env, company, PERIOD_DATE, cash, income, amount, {}, ref, source="api")


def _chain_rows(env, company):
    return (
        env["fix.journal.posting.log"]
        .sudo()
        .search(
            [("company_id", "=", company.id), ("chain_hash", "!=", False)],
            order="chain_seq asc, id asc",
        )
    )


def test_hash_chain_verifies_after_posting_and_catches_a_tampered_row(odoo_env):
    env = odoo_env
    company = env.company
    _simple_post(env, company, 111.0, "W5-CHAIN-1")
    _simple_post(env, company, 222.0, "W5-CHAIN-2")
    env.flush_all()

    result = verify_chain(env, company)
    rows = _chain_rows(env, company)
    assert result["ok"] is True, result["broken"]
    assert result["checked"] == len(rows) == 2
    assert [row.chain_seq for row in rows] == [1, 2]
    assert rows[0].prev_chain_hash == CHAIN_GENESIS
    assert rows[1].prev_chain_hash == rows[0].chain_hash
    assert result["head_hash"] == rows[-1].chain_hash
    head = env["fix.journal.chain.head"].sudo().search([("company_id", "=", company.id)])
    assert head.last_log_id == rows[-1] and head.log_count == 2

    # Changing ANY historical row's amount breaks verification at that row.
    rows[0].with_context(force_edit=True).sudo().write({"amount": 999999.0})
    broken = verify_chain(env, company)
    assert broken["ok"] is False
    assert broken["broken_row_id"] == rows[0].id
    assert broken["broken"]["reason"] == "row content changed after it was chained"
    assert broken["broken"]["stored_hash"] != broken["broken"]["expected_hash"]


def test_sequential_postings_produce_one_valid_chain(odoo_env):
    """The second posting takes the head lock the first released and links to
    its hash — two postings can never chain from the same predecessor."""
    env = odoo_env
    company = env.company
    _simple_post(env, company, 10.0, "W5-SEQ-1")
    env.flush_all()
    _simple_post(env, company, 20.0, "W5-SEQ-2")
    env.flush_all()

    rows = _chain_rows(env, company)
    assert rows[1].prev_chain_hash == rows[0].chain_hash
    assert rows[0].prev_chain_hash == CHAIN_GENESIS
    assert verify_chain(env, company)["ok"] is True
