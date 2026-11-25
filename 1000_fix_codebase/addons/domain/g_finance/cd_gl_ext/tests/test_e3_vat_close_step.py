"""C10 (owner decision 12 Nov 2026, D2-12): the period close's VAT step
("VAT Sub-Ledger & Mushak 9.1 Return Preparation") is done only when the
period's Mushak 9.1 return is prepared AND its sub-ledger reconciliation
says ``reconciled``. The evidence used to be checked for existence only, so
a 9.1 in ``variance_detected`` closed the step (second rehearsal).

The rule holds for trusted code as well: it is a statutory fact about the
period, not a permission."""

from __future__ import annotations

from datetime import date

import pytest
from odoo.exceptions import UserError

PE = date(2026, 9, 30)


def reconciled_vat_return(env, company, period_end, status="reconciled", state="prepared"):
    """The period's Mushak 9.1 return in the given state (trusted fixture
    data: the guarded fields are written as the system)."""
    period = period_end.strftime("%Y-%m")
    Return = env["fix.vat.return"].sudo()
    ret = Return.search([("company_id", "=", company.id), ("period", "=", period)], limit=1)
    vals = {"state": state, "subledger_status": status}
    if ret:
        ret.write(vals)
        return ret
    return Return.create(dict(vals, company_id=company.id, period=period))


@pytest.fixture
def k(odoo_env):
    company = odoo_env["res.company"].create({"name": "C10 VAT close Co"})
    env = odoo_env(context=dict(odoo_env.context, allowed_company_ids=company.ids))
    close = env["fix.period.close"].create({"period_end": PE, "company_id": company.id})
    close.action_generate_standard_steps()
    vat = close.line_ids.filtered(lambda s: s.sequence == 50)
    assert "Mushak 9.1" in vat.name
    return env, company, close, vat


def test_no_9_1_return_refuses_the_vat_step(k):
    env, _company, _close, vat = k
    with pytest.raises(UserError, match="9.1") as refused, env.cr.savepoint():
        vat.action_mark_done("VAT-2026-09")
    assert "not prepared" in str(refused.value)
    assert vat.state == "pending"


def test_a_draft_9_1_refuses_the_vat_step(k):
    env, company, _close, vat = k
    reconciled_vat_return(env, company, PE, status="pending", state="draft")
    with pytest.raises(UserError, match="not prepared"), env.cr.savepoint():
        vat.action_mark_done("VAT-2026-09")


@pytest.mark.parametrize("status", ["variance_detected", "pending"])
def test_an_unreconciled_9_1_refuses_the_vat_step(k, status):
    env, company, _close, vat = k
    ret = reconciled_vat_return(env, company, PE, status=status)
    with pytest.raises(UserError, match="not reconciled") as refused, env.cr.savepoint():
        vat.action_mark_done("fix.vat.return,%d" % ret.id)
    assert "2026-09" in str(refused.value)
    assert vat.state == "pending"


def test_a_reconciled_9_1_closes_the_vat_step(k):
    env, company, _close, vat = k
    ret = reconciled_vat_return(env, company, PE)
    vat.action_mark_done("fix.vat.return,%d" % ret.id)
    assert vat.state == "done"
    assert (vat.evidence_model, vat.evidence_res_id) == ("fix.vat.return", ret.id)


def test_another_periods_return_is_not_this_periods_evidence(k):
    env, company, _close, vat = k
    reconciled_vat_return(env, company, PE)
    august = reconciled_vat_return(env, company, date(2026, 8, 31))
    with pytest.raises(UserError, match="2026-08"), env.cr.savepoint():
        vat.action_mark_done("fix.vat.return,%d" % august.id)


def test_other_steps_are_untouched(k):
    env, _company, close, _vat = k
    bank = close.line_ids.filtered(lambda s: s.sequence == 20)
    bank.action_mark_done("BANKREC-2026-09")
    assert bank.state == "done"


def test_a_variance_found_after_the_step_stops_the_ready_check(k):
    env, company, close, vat = k
    ret = reconciled_vat_return(env, company, PE)
    close.line_ids.filtered("blocking").action_mark_done("fix.vat.return,%d" % ret.id)
    reconciled_vat_return(env, company, PE, status="variance_detected")
    with pytest.raises(UserError, match="not reconciled"), env.cr.savepoint():
        close.action_ready()
    assert close.state == "in_progress"


def test_the_vat_step_cannot_be_renamed_out_of_the_rule(k):
    env, _company, _close, vat = k
    user = env["res.users"].create(
        {
            "name": "c10 accountant",
            "login": "c10_acct_vat_rename",
            "group_ids": [(6, 0, [env.ref("account.group_account_user").id])],
            "company_id": _company.id,
            "company_ids": [(6, 0, _company.ids)],
        }
    )
    with pytest.raises(UserError, match="standard close step"), env.cr.savepoint():
        vat.with_user(user).write({"name": "Something else"})
