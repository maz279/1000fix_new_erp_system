# cd_fpa: M54 capture audit (2026-11-17), the four new records on a real
# database. Every decision runs as a NON-ADMIN user holding the real finance
# role (the users of test_a08_m54_controls' fixture): acct and acct2 are
# Accountants, mgr and mgr2 Accounting Administrators holding the CFO tier.
# Arrangement that is not under test (a posted ledger entry, a budget version
# approved through the M63 inbox) uses the same helpers as the control tests.
# Everything rolls back (odoo_env).
from __future__ import annotations

from datetime import date, timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

from . import test_a08_m54_controls as _base

# the shared fixture and helpers of the M54 control tests
c = _base.c
p03 = _base.p03
version = _base.version
approve_as = _base.approve_as
je = _base.je
_SEQ = _base._SEQ

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
SEP_FROM, SEP_TO = date(2026, 9, 1), date(2026, 9, 30)


def _approved_version(c, planned=100000.0, **kw):
    ver = version(c, c.acct, planned=planned, **kw)
    ver.with_user(c.acct).action_submit()
    approve_as(c, ver, c.mgr)
    assert ver.state == "approved"
    return ver


def _centre(c, user, **kw):
    vals = {
        "code": "CC-%s" % next(_SEQ),
        "name": "Dhanmondi Workshop",
        "owner_id": c.acct2.id,
        "centre_type": "absorbing",
    }
    vals.update(kw)
    return c.env["fix.cost.centre"].with_user(user).create(vals)


# ------------------------------------------------------------------ cost centres
def test_cost_centre_is_maintained_by_administrators_with_a_named_owner(c):
    with pytest.raises(AccessError), c.env.cr.savepoint():
        _centre(c, c.acct)  # an accountant reads, never maintains
    parent = _centre(c, c.mgr, centre_type="allocating")
    child = _centre(c, c.mgr, parent_id=parent.id)
    assert child.owner_id == c.acct2
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        parent.with_user(c.mgr).write({"parent_id": child.id})  # no cycle
    with pytest.raises(AccessError), c.env.cr.savepoint():
        child.with_user(c.mgr).unlink()  # deactivated, never deleted
    assert c.env["fix.cost.centre"].owner_for_code(child.code, c.co) == c.acct2


# ------------------------------------------------------------------ activity rates
def _rate(c, user, **kw):
    vals = {
        "activity_type": "technician_hour",
        "planned_rate": 650.0,
        "effective_from": fields.Date.context_today(c.env.user),
        "basis": "Gross pay + employer PF + van + tools + 20% non-productive time",
    }
    vals.update(kw)
    return c.env["fix.activity.rate"].with_user(user).create(vals)


def test_rate_is_approved_by_another_administrator_and_then_frozen(c):
    rate = _rate(c, c.mgr)
    assert rate.name.startswith("ACR/")
    rate.with_user(c.mgr).action_submit()
    with pytest.raises(UserError), c.env.cr.savepoint():
        rate.with_user(c.acct).action_approve()  # an accountant does not approve
    with pytest.raises(UserError), c.env.cr.savepoint():
        rate.with_user(c.mgr).action_approve()  # nor its preparer
    rate.with_user(c.mgr2).action_approve()
    assert rate.state == "approved" and rate.approved_by == c.mgr2
    with pytest.raises(UserError), c.env.cr.savepoint():
        rate.with_user(c.mgr2).write({"planned_rate": 999.0})
    with pytest.raises(UserError), c.env.cr.savepoint():
        rate.with_user(c.mgr2).unlink()


def test_submitter_cannot_approve_and_rejection_needs_a_reason(c):
    rate = _rate(c, c.acct)
    rate.with_user(c.mgr).action_submit()
    with pytest.raises(UserError), c.env.cr.savepoint():
        rate.with_user(c.mgr).action_approve()  # the submitter
    with pytest.raises(UserError), c.env.cr.savepoint():
        rate.with_user(c.mgr2).action_reject(reason="  ")
    rate.with_user(c.mgr2).action_reject(reason="Vehicle cost double counted")
    assert rate.state == "rejected"
    rate.with_user(c.acct).write({"planned_rate": 600.0})  # back to the preparer
    rate.with_user(c.acct).action_submit()
    assert rate.state == "submitted" and not rate.rejection_reason


def test_rate_state_and_measures_cannot_be_typed(c):
    rate = _rate(c, c.acct)
    for vals in ({"state": "approved"}, {"approved_by": c.mgr.id}, {"measured_rate": 1.0}):
        with pytest.raises(UserError), c.env.cr.savepoint():
            rate.with_user(c.acct).write(vals)
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        _rate(c, c.acct, planned_rate=0.0)
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        _rate(c, c.acct, basis=" ")
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        _rate(c, c.plain)  # no finance role


def test_a_new_rate_closes_the_old_one_and_never_rewrites_the_past(c):
    today = fields.Date.context_today(c.env.user)
    old = _rate(c, c.acct, effective_from=today - timedelta(days=90))
    old.with_user(c.acct).action_submit()
    old.with_user(c.mgr).action_approve()
    backdated = _rate(c, c.acct, planned_rate=700.0, effective_from=today - timedelta(days=10))
    backdated.with_user(c.acct).action_submit()
    with pytest.raises(UserError, match="already past"), c.env.cr.savepoint():
        backdated.with_user(c.mgr).action_approve()
    new = _rate(c, c.acct, planned_rate=720.0, effective_from=today + timedelta(days=1))
    new.with_user(c.acct).action_submit()
    new.with_user(c.mgr).action_approve()
    assert old.state == "approved" and old.effective_to == today
    assert old.superseded_by_id == new
    book = c.env["fix.activity.rate"].rate_book("technician_hour", c.co.ids)
    assert book(False, today) == 650.0
    assert book(False, today + timedelta(days=1)) == 720.0


# ------------------------------------------------------------------ budget targets
def test_targets_are_issued_by_an_administrator_and_read_against_the_plan(c):
    ver = version(c, c.acct, planned=100000.0)  # one cost line
    vals = {
        "version_id": ver.id,
        "scope_type": "company",
        "target_type": "cost",
        "target_amount": 80000.0,
    }
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        c.env["fix.budget.target"].with_user(c.acct).create(vals)
    target = c.env["fix.budget.target"].with_user(c.mgr).create(vals)
    assert target.plan_amount == 100000.0 and target.departure == 20000.0
    assert target.departure_pct == 25.0
    target.with_user(c.mgr).action_issue()
    assert target.state == "issued" and target.issued_by == c.mgr
    with pytest.raises(UserError), c.env.cr.savepoint():
        target.with_user(c.mgr).write({"target_amount": 120000.0})
    twin = c.env["fix.budget.target"].with_user(c.mgr).create(vals)
    with pytest.raises(UserError, match="already issued"), c.env.cr.savepoint():
        twin.with_user(c.mgr).action_issue()
    ver.with_user(c.acct).action_submit()
    note = ver.message_ids.filtered(lambda m: "issued targets" in (m.body or ""))
    assert note and "80000.00" in note[0].body
    with pytest.raises(UserError), c.env.cr.savepoint():
        target.with_user(c.mgr).action_withdraw(reason="")
    target.with_user(c.mgr).action_withdraw(reason="Superseded by the board guidance")
    assert target.state == "withdrawn"


def test_a_target_has_exactly_one_scope(c):
    ver = version(c, c.acct)
    T = c.env["fix.budget.target"].with_user(c.mgr)
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        T.create(
            {
                "version_id": ver.id,
                "scope_type": "branch",
                "target_type": "revenue",
                "target_amount": 1.0,
            }
        )
    centre = _centre(c, c.mgr)
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        T.create(
            {
                "version_id": ver.id,
                "scope_type": "company",
                "cost_centre_id": centre.id,
                "target_type": "revenue",
                "target_amount": 1.0,
            }
        )


# ------------------------------------------------------------------ variance explanations
def _unbudgeted_branch(c):
    """A branch of its own (fix_test holds none), so no other budget reads it."""
    tag = next(_SEQ)
    entity = c.env["fix.entity"].create(
        {"code": "M54E%s" % tag, "legal_name": "M54 Entity %s" % tag, "company_id": c.co.id}
    )
    return c.env["fix.branch"].create(
        {
            "code": "M54B%s" % tag,
            "name": "M54 Branch %s" % tag,
            "entity_id": entity.id,
            "operating_unit_id": c.ou.id,
        }
    )


def _explain(c, user, line, **kw):
    vals = {
        "scope_type": "line",
        "budget_line_id": line.id,
        "date_from": SEP_FROM,
        "date_to": SEP_TO,
    }
    vals.update(kw)
    return c.env["fix.variance.explanation"].with_user(user).create(vals)


def test_variance_is_measured_from_the_approved_budget_and_the_ledger(c):
    ver = _approved_version(c)
    je(c, date(2026, 9, 12), 30000.0, c.exp, c.cash)
    line = ver.budget_ids.line_ids
    exp = _explain(c, c.acct, line)
    assert exp.name.startswith("VEX/")
    assert (exp.planned, exp.actual, exp.variance) == (100000.0, 30000.0, 70000.0)
    assert exp.variance_pct == 70.0 and exp.breached and exp.version_id == ver
    assert exp.owner_id == c.acct  # no cost centre: the version's submitter
    assert exp.due_date > fields.Date.context_today(c.env.user)
    for vals in ({"planned": 1.0}, {"variance": 0.0}, {"state": "accepted"}):
        with pytest.raises(UserError), c.env.cr.savepoint():
            exp.with_user(c.acct).write(vals)
    with pytest.raises(UserError, match="measured for this scope"), c.env.cr.savepoint():
        exp.with_user(c.acct).write({"date_to": date(2026, 9, 15)})
    with pytest.raises(UserError, match="already covers"), c.env.cr.savepoint():
        _explain(c, c.acct, line)


def test_only_the_owner_explains_and_another_administrator_reviews(c):
    ver = _approved_version(c)
    line = ver.budget_ids.line_ids
    exp = _explain(c, c.acct, line)
    with pytest.raises(UserError), c.env.cr.savepoint():
        exp.with_user(c.acct).write({"owner_id": c.acct2.id})  # reassigning is the admin's
    exp.with_user(c.mgr).write({"owner_id": c.acct2.id})
    with pytest.raises(UserError, match="accountable owner"), c.env.cr.savepoint():
        exp.with_user(c.acct).write({"explanation": "Not mine to write"})
    with pytest.raises(UserError, match="accountable owner"), c.env.cr.savepoint():
        exp.with_user(c.acct).action_submit()
    with pytest.raises(UserError, match="root cause"), c.env.cr.savepoint():
        exp.with_user(c.acct2).action_submit()
    exp.with_user(c.acct2).write(
        {"explanation": "Workshop rent invoice posted in October", "root_cause": "timing"}
    )
    exp.with_user(c.acct2).action_submit()
    with pytest.raises(UserError), c.env.cr.savepoint():
        exp.with_user(c.acct2).write({"explanation": "changed after submitting"})
    with pytest.raises(UserError), c.env.cr.savepoint():
        exp.with_user(c.acct).action_accept()  # an accountant does not review
    exp.with_user(c.mgr).action_return(reason="Name the invoice")
    assert exp.state == "returned" and exp.return_reason == "Name the invoice"
    exp.with_user(c.acct2).write({"explanation": "Rent invoice INV/2026/0042 posted 2 Oct"})
    exp.with_user(c.acct2).action_submit()
    exp.with_user(c.mgr).action_accept()
    assert exp.state == "accepted" and exp.accepted_by == c.mgr
    with pytest.raises(UserError), c.env.cr.savepoint():
        exp.with_user(c.mgr).write({"action_committed": "late edit"})
    with pytest.raises(UserError), c.env.cr.savepoint():
        exp.with_user(c.mgr).unlink()


def test_owner_who_is_an_administrator_cannot_accept_their_own(c):
    ver = _approved_version(c)
    exp = _explain(c, c.acct, ver.budget_ids.line_ids)
    exp.with_user(c.mgr2).write({"owner_id": c.mgr2.id})
    exp.with_user(c.mgr2).write({"explanation": "One-off repair", "root_cause": "one_off"})
    exp.with_user(c.mgr2).action_submit()
    with pytest.raises(UserError, match="Segregation"), c.env.cr.savepoint():
        exp.with_user(c.mgr2).action_accept()
    exp.with_user(c.mgr).action_accept()


def test_a_variance_is_measured_only_on_an_approved_version(c):
    draft = version(c, c.acct)
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        _explain(c, c.acct, draft.budget_ids.line_ids)


def test_branch_variance_reads_every_approved_line_of_the_branch(c):
    branch = _unbudgeted_branch(c)
    ver = version(c, c.acct, planned=40000.0)
    ver.budget_ids.line_ids.write({"branch_id": branch.id})
    ver.with_user(c.acct).action_submit()
    approve_as(c, ver, c.mgr)
    exp = (
        c.env["fix.variance.explanation"]
        .with_user(c.acct)
        .create(
            {
                "scope_type": "branch",
                "branch_id": branch.id,
                "date_from": SEP_FROM,
                "date_to": SEP_TO,
            }
        )
    )
    assert exp.planned == 40000.0 and exp.version_id == ver
    with pytest.raises(UserError, match="no variance to explain"), c.env.cr.savepoint():
        c.env["fix.variance.explanation"].with_user(c.acct).create(
            {
                "scope_type": "branch",
                "branch_id": branch.id,
                "date_from": date(2025, 1, 1),
                "date_to": date(2025, 1, 31),
            }
        )


def test_monthly_job_raises_explanations_for_the_cost_centre_owner(c):
    centre = _centre(c, c.mgr)
    ver = version(c, c.acct, planned=200000.0)
    big = ver.budget_ids.line_ids
    big.write({"cost_centre": centre.code})
    small = c.env["fix.budget.line"].create(  # under the BDT 50,000 threshold
        {
            "budget_id": ver.budget_ids.id,
            "account_id": c.exp.id,
            "date_from": SEP_FROM,
            "date_to": SEP_TO,
            "planned_amount": 1000.0,
        }
    )
    ver.with_user(c.acct).action_submit()
    approve_as(c, ver, c.mgr)
    Exp = c.env["fix.variance.explanation"]
    raised = Exp._cron_raise_explanations(today=date(2026, 10, 5))
    mine = raised.filtered(lambda e: e.budget_line_id == big)
    assert mine and mine.owner_id == c.acct2  # the cost-centre owner
    assert (mine.date_from, mine.date_to) == (SEP_FROM, SEP_TO)
    assert mine.activity_ids and mine.activity_ids[0].user_id == c.acct2
    assert not raised.filtered(lambda e: e.budget_line_id == small)
    again = Exp._cron_raise_explanations(today=date(2026, 10, 5))
    assert not again.filtered(lambda e: e.budget_line_id == big)
    late = Exp._cron_overdue(today=mine.due_date + timedelta(days=1))
    assert mine in late


# ------------------------------------------------------------------ the workspace path
def test_workspace_saves_a_branch_explanation_and_refuses_typed_figures(c, p03):
    branch = _unbudgeted_branch(c)
    ver = version(c, c.acct, planned=40000.0)
    ver.budget_ids.line_ids.write({"branch_id": branch.id})
    ver.with_user(c.acct).action_submit()
    approve_as(c, ver, c.mgr)
    p03.as_user(c.acct)
    res = p03.write(
        model="fix.variance.explanation",
        record_id=False,
        values={
            "scope_type": "branch",
            "branch_id": branch.id,
            "date_from": "2026-09-01",
            "date_to": "2026-09-30",
        },
    )
    assert res.get("id"), res
    exp = c.env["fix.variance.explanation"].browse(res["id"])
    assert exp.scope_type == "branch" and exp.planned == 40000.0
    res = p03.write(model="fix.variance.explanation", record_id=exp.id, values={"planned": 1.0})
    assert res.get("error") or exp.planned == 40000.0, res
    res = p03.write(
        model="fix.activity.rate",
        record_id=False,
        values={
            "activity_type": "technician_hour",
            "planned_rate": 650.0,
            "effective_from": "2026-12-01",
            "basis": "Pay + PF + van",
            "currency_id": c.env.ref("base.BDT").id,
        },
    )
    assert res.get("id"), res
    res = p03.write(model="fix.activity.rate", record_id=res["id"], values={"state": "approved"})
    assert res.get("error") or c.env["fix.activity.rate"].browse(res.get("id")).state == "draft"
