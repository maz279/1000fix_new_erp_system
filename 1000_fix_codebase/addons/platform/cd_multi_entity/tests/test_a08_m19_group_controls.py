# A08 remediation, M19 group controls on cd_multi_entity models (IC, consolidation,
# nil return). Prepared by B3 with models/fix_a08_group_controls.py; ids follow
# working/A08_evidence/probes/m19/probe_m19.py (I*, C*, N*).
from datetime import date

import pytest
from odoo import Command, fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
ACC_USER = "account.group_account_user"
ACC_MGR = "account.group_account_manager"
PE = date(2026, 9, 30)
_SEQ = iter(range(1, 100000))


class Ctx:
    pass


def _user(env, login, groups=(), companies=None):
    companies = companies or env.company
    ou = env["operating.unit"].search([], limit=1)
    return env["res.users"].with_context(no_reset_password=True).create(
        {
            "name": login,
            "login": login,
            "group_ids": [(6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])],
            "company_ids": [(6, 0, companies.ids)],
            "company_id": companies[0].id,
            "assigned_operating_unit_ids": [(6, 0, ou.ids)],
            "default_operating_unit_id": ou.id,
        }
    )


@pytest.fixture
def ic(odoo_env):
    env = odoo_env
    bdt = env.ref("base.BDT")
    n = next(_SEQ)
    co1 = env["res.company"].create({"name": "B3 IC Parent %d" % n, "currency_id": bdt.id})
    co2 = env["res.company"].create({"name": "B3 IC Sub %d" % n, "currency_id": bdt.id})
    e1 = env["fix.entity"].create({"code": "B3P%d" % n, "legal_name": "B3 Parent", "company_id": co1.id})
    e2 = env["fix.entity"].create({"code": "B3S%d" % n, "legal_name": "B3 Sub", "company_id": co2.id})

    def acc(co, t, rec=False):
        k = next(_SEQ)
        return env["account.account"].create(
            {"code": "8%05d" % k, "name": "B3 %s %d" % (t, k), "account_type": t, "reconcile": rec,
             "company_ids": [(6, 0, co.ids)]}
        )

    def jr(co):
        k = next(_SEQ)
        return env["account.journal"].create({"name": "B3 J%d" % k, "code": "B%04d" % k, "type": "general", "company_id": co.id})

    y = Ctx()
    y.env, y.bdt = env, bdt
    y.co1, y.co2, y.e1, y.e2 = co1, co2, e1, e2
    both = co1 | co2
    y.ctx = {"allowed_company_ids": both.ids}
    y.acct = _user(env, "b3ic_acct", [ACC_USER], both)
    y.acct2 = _user(env, "b3ic_acct2", [ACC_USER], both)
    y.mgr = _user(env, "b3ic_mgr", [ACC_USER, ACC_MGR], both)
    y.mgr2 = _user(env, "b3ic_mgr2", [ACC_USER, ACC_MGR], both)
    y.income = acc(co1, "income")
    y.rule = env["fix.intercompany.rule"].create(
        {
            "name": "IT shared service",
            "code": "B3IC%d" % n,
            "company_id": co1.id,
            "source_entity_id": e1.id,
            "target_entity_id": e2.id,
            "transaction_type": "shared_service",
            "source_journal_id": jr(co1).id,
            "source_receivable_account_id": acc(co1, "asset_receivable", True).id,
            "source_income_account_id": y.income.id,
            "target_journal_id": jr(co2).id,
            "target_expense_account_id": acc(co2, "expense").id,
            "target_payable_account_id": acc(co2, "liability_payable", True).id,
        }
    )
    return y


def _txn(y, user, amount=100000.0):
    return y.env["fix.intercompany.transaction"].with_user(user).with_context(**y.ctx).with_company(y.co1).create(
        {
            "name": "IT recharge",
            "company_id": y.co1.id,
            "source_entity_id": y.e1.id,
            "target_entity_id": y.e2.id,
            "rule_id": y.rule.id,
            "amount": amount,
            "currency_id": y.bdt.id,
            "transaction_date": date(2026, 9, 20),
        }
    )


def _as(rec, user, y):
    return rec.with_user(user).with_context(**y.ctx)


def _matched(y):
    t = _txn(y, y.acct)
    _as(t, y.acct, y).action_generate_mirror()
    _as(t, y.acct2, y).action_match()
    return t


def _book(y, user):
    return y.env["fix.consolidation.book"].with_user(user).with_context(**y.ctx).with_company(y.co1).create(
        {
            "name": "B3 Group",
            "code": "B3CONS%d" % next(_SEQ),
            "company_id": y.co1.id,
            "currency_id": y.bdt.id,
            "parent_entity_id": y.e1.id,
            "entity_ids": [(6, 0, (y.e1 | y.e2).ids)],
            "consolidation_date": PE,
        }
    )


def test_m19_I02_poster_of_both_sides_cannot_match(ic):
    t = _txn(ic, ic.acct)
    _as(t, ic.acct, ic).action_generate_mirror()
    with pytest.raises(UserError, match="Segregation of duties"):
        _as(t, ic.acct, ic).action_match()
    _as(t, ic.acct2, ic).action_match()
    assert t.state == "matched" and t.mirrored_by_id == ic.acct and t.matched_by_id == ic.acct2


def test_m19_I03_state_cannot_be_typed(ic):
    t = _txn(ic, ic.acct)
    with pytest.raises(UserError, match="changes only through its workflow"):
        _as(t, ic.acct, ic).write({"state": "settled"})


def test_m19_C03_run_by_cannot_be_rewritten(ic):
    _matched(ic)
    b = _book(ic, ic.mgr)
    _as(b, ic.mgr, ic).action_run_consolidation()
    _as(b, ic.mgr, ic).action_generate_eliminations()
    with pytest.raises(UserError, match="changes only through its workflow"):
        _as(b, ic.mgr, ic).write({"run_by_id": ic.acct.id})
    with pytest.raises(UserError, match="Segregation of duties"):
        _as(b, ic.mgr, ic).action_close()
    _as(b, ic.mgr2, ic).action_close()
    assert b.state == "closed"


def test_m19_C04_typed_elimination_refused(ic):
    _matched(ic)
    b = _book(ic, ic.acct)
    _as(b, ic.acct, ic).action_run_consolidation()
    _as(b, ic.acct, ic).action_generate_eliminations()
    assert b.elimination_ids and all(b.elimination_ids.mapped("transaction_id"))
    with pytest.raises(UserError, match="typed elimination is refused"):
        ic.env["fix.elimination.entry"].with_user(ic.acct).with_context(**ic.ctx).create(
            {"book_id": b.id, "name": "typed", "elimination_type": "receivable_payable",
             "from_entity_id": ic.e1.id, "to_entity_id": ic.e2.id, "amount": 480000.0}
        )


def test_m19_C05_amount_pinned_after_mirror(ic):
    t = _matched(ic)
    with pytest.raises(UserError, match="pinned"):
        _as(t, ic.acct, ic).write({"amount": 1000000.0})
    assert t.amount == 100000.0


def test_m19_C06_closed_book_frozen(ic):
    _matched(ic)
    b = _book(ic, ic.acct)
    _as(b, ic.acct, ic).action_run_consolidation()
    _as(b, ic.acct, ic).action_generate_eliminations()
    _as(b, ic.mgr, ic).action_close()
    line = b.line_ids.filtered(lambda l: l.account_type == "revenue")[:1]
    with pytest.raises(UserError, match="frozen"):
        _as(line, ic.acct, ic).write({"original_amount": line.original_amount + 5000000.0})
    with pytest.raises(UserError, match="frozen"):
        _as(b.elimination_ids[:1], ic.acct, ic).write({"amount": 1.0})


def _entity(env):
    return env["fix.entity"].create(
        {"code": "B3NIL%d" % next(_SEQ), "legal_name": "B3 Nil", "company_id": env.company.id,
         "bin_number": "1882991029102", "tin_number": "881920391029"}
    )


def test_m19_N02_sales_after_verify_block_the_filing(odoo_env):
    env = odoo_env
    acct = _user(env, "b3nil_acct", [ACC_USER])
    nr = env["fix.nil.return.generator"].with_user(acct).create(
        {"entity_id": _entity(env).id, "period_year": 2026, "period_month": 8}
    )
    nr.with_user(acct).action_verify_eligibility()
    A = env["account.account"]
    misc = env["account.journal"].search([("code", "=", "MISC"), ("company_id", "=", env.company.id)], limit=1)
    move = env["account.move"].create(
        {
            "move_type": "entry",
            "journal_id": misc.id,
            "date": date(2026, 8, 15),
            "line_ids": [
                Command.create({"account_id": A.search([("code", "=", "101401")], limit=1).id, "debit": 2000000.0}),
                Command.create({"account_id": A.search([("code", "=", "400000")], limit=1).id, "credit": 2000000.0}),
            ],
        }
    )
    move.action_post()
    with pytest.raises(ValidationError, match="standard"):
        nr.with_user(acct).action_generate_nil_packs()
    assert nr.state == "verified"


def test_m19_N03_state_cannot_be_typed(odoo_env):
    env = odoo_env
    acct = _user(env, "b3nil_acct2", [ACC_USER])
    nr = env["fix.nil.return.generator"].with_user(acct).create(
        {"entity_id": _entity(env).id, "period_year": 2026, "period_month": 8}
    )
    with pytest.raises(UserError, match="changes only through its workflow"):
        nr.with_user(acct).write({"state": "acknowledged"})
    assert nr.state == "draft" and fields.Date.today()


def test_m19_I05_priced_charge_uses_only_an_approved_rate(ic):
    """BRU-FPA-18: a charge whose rule carries a markup is refused until an
    Accounting Administrator other than the proposer approves a rate; it is then
    priced at the approved rate, and an approved rate is frozen."""
    env = ic.env
    ic.rule.sudo().write({"markup_percent": 10.0})
    assert not ic.rule.transfer_pricing_compliant
    t = _txn(ic, ic.acct)
    with pytest.raises(UserError, match="no transfer-pricing rate is"):
        _as(t, ic.acct, ic).action_generate_mirror()
    Rate = env["fix.transfer.price.rate"]
    rate = Rate.with_user(ic.acct).with_context(**ic.ctx).create(
        {"rule_id": ic.rule.id, "markup_percent": 10.0, "date_from": date(2026, 7, 1),
         "study_ref": "TP study FY27 (cost plus)"}
    )
    with pytest.raises(UserError, match="changes only through its workflow"):
        _as(rate, ic.acct, ic).write({"state": "active"})
    with pytest.raises(UserError, match="Accounting Administrator"):
        _as(rate, ic.acct, ic).action_activate()
    own = Rate.with_user(ic.mgr).with_context(**ic.ctx).create(
        {"rule_id": ic.rule.id, "markup_percent": 10.0, "date_from": date(2027, 7, 1),
         "study_ref": "own"}
    )
    with pytest.raises(UserError, match="Segregation of duties"):
        _as(own, ic.mgr, ic).action_activate()
    _as(rate, ic.mgr, ic).action_activate()
    assert rate.state == "active" and rate.approved_by_id == ic.mgr
    assert ic.rule.transfer_pricing_compliant
    with pytest.raises(UserError, match="frozen"):
        _as(rate, ic.mgr, ic).write({"markup_percent": 25.0})
    # a rule markup that differs from the approved rate is refused
    ic.rule.sudo().write({"markup_percent": 12.0})
    with pytest.raises(UserError, match="approved rate is 10.00"):
        _as(t, ic.acct, ic).action_generate_mirror()
    ic.rule.sudo().write({"markup_percent": 10.0})
    _as(t, ic.acct, ic).action_generate_mirror()
    income = -sum(
        t.source_move_id.sudo().line_ids.filtered(lambda line: line.account_id == ic.income).mapped("balance")
    )
    assert (income, t.cost_amount, t.amount, t.tp_rate_id) == (110000.0, 100000.0, 110000.0, rate)
    _as(t, ic.acct2, ic).action_match()
    assert t.state == "matched"


def test_m19_I01_cost_recharge_proper_path(ic):
    """Reference: a 0% rule needs no rate; the counterparty's accountant matches."""
    t = _matched(ic)
    assert t.state == "matched" and not t.tp_rate_id and t.amount == 100000.0


def test_m19_N02b_filing_needs_a_locked_period(odoo_env):
    env = odoo_env
    acct = _user(env, "b3nil_acct3", [ACC_USER])
    nr = env["fix.nil.return.generator"].with_user(acct).create(
        {"entity_id": _entity(env).id, "period_year": 2026, "period_month": 7}
    )
    nr.with_user(acct).action_verify_eligibility()
    nr.with_user(acct).action_generate_nil_packs()
    nr.with_user(acct).write({"filing_reference": "EVAT-ACK-1"})
    with pytest.raises(UserError, match="Close and lock 2026-07"):
        nr.with_user(acct).action_submit_to_nbr()
    env.company.sudo().fiscalyear_lock_date = date(2026, 7, 31)
    nr.with_user(acct).action_submit_to_nbr()
    assert nr.state == "acknowledged"
