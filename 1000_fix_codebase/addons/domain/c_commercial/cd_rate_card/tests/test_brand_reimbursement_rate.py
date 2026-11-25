# M11 capture audit (2026-11-13): the brand reimbursement rate card
# (FR-PRC-015, BRU-PRC-12). Exercised as non-admin users on the live ORM
# (`odoo_env`, rolled back): a Pricing Officer records a brand's rate, a
# Price-Book Releaser who did not author it releases it from the M63 inbox, a
# later circular supersedes it from its own date, and a claim on any service
# date reads the version that was in force then.
import itertools
import uuid
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TAG = "BRR-%s" % uuid.uuid4().hex[:6]
_SEQ = itertools.count(1)
OFFICER = "cd_rate_card.group_pricing_officer"
RELEASER = "cd_rate_card.group_price_releaser"


def _user(env, tag, groups=()):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %s %d" % (TAG, tag, n),
                "login": "%s.%s.%d@brr.test" % (TAG.lower(), tag, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


@pytest.fixture
def ppl(odoo_env):
    class P:
        clerk = _user(odoo_env, "clerk")
        officer = _user(odoo_env, "officer", [OFFICER])
        releaser = _user(odoo_env, "rel", [RELEASER])
        releaser_officer = _user(odoo_env, "relof", [RELEASER, OFFICER])

    return P


@pytest.fixture
def brand(odoo_env):
    return odoo_env["fix.brand"].sudo().create({"name": "%s brand" % TAG, "code": TAG})


def _rate(env, user, brand, start, labour=1200.0, markup=10.0, level="l1"):
    return (
        env["fix.brand.reimbursement.rate"]
        .with_user(user)
        .create(
            {
                "brand_id": brand.id,
                "repair_level": level,
                "labour_rate": labour,
                "parts_markup_pct": markup,
                "valid_from": start,
            }
        )
    )


def _today(env):
    return fields.Date.context_today(env["res.users"])


def test_a_plain_user_reads_but_does_not_record_a_brand_rate(odoo_env, ppl, brand):
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        _rate(odoo_env, ppl.clerk, brand, _today(odoo_env))


@pytest.mark.parametrize(
    "vals", [{"labour_rate": 0.0}, {"labour_rate": -5.0}, {"parts_markup_pct": 150.0}]
)
def test_a_rate_is_positive_and_its_markup_bounded(odoo_env, ppl, brand, vals):
    base = {
        "brand_id": brand.id,
        "labour_rate": 1000.0,
        "valid_from": _today(odoo_env),
        **vals,
    }
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        odoo_env["fix.brand.reimbursement.rate"].with_user(ppl.officer).create(base)


def test_the_state_and_version_are_never_typed(odoo_env, ppl, brand):
    rate = _rate(odoo_env, ppl.officer, brand, _today(odoo_env))
    for vals in ({"state": "active"}, {"version": 3}, {"approved_by": ppl.officer.id}):
        with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
            rate.with_user(ppl.officer).write(vals)


def test_a_draft_rate_values_no_claim(odoo_env, ppl, brand):
    _rate(odoo_env, ppl.officer, brand, _today(odoo_env))
    assert not odoo_env["fix.brand.reimbursement.rate"].rate_for(brand, "l1")


def test_release_by_a_releaser_who_is_not_the_author(odoo_env, ppl, brand):
    rate = _rate(odoo_env, ppl.releaser_officer, brand, _today(odoo_env))
    rate.with_user(ppl.releaser_officer).action_submit()
    assert rate.state == "in_review"
    # the author holds the releaser role too, and still cannot release it
    task = inbox_task(rate, ppl.releaser_officer)
    if task:
        with pytest.raises(UserError), odoo_env.cr.savepoint():
            task.with_user(ppl.releaser_officer).action_approve()
    # pressing the release directly is refused: it is decided from the inbox
    with pytest.raises(UserError, match="approver's inbox"), odoo_env.cr.savepoint():
        rate.with_user(ppl.releaser).action_approve()
    approve_via_inbox(rate, ppl.releaser, requester=ppl.releaser_officer)
    assert rate.state == "active"
    assert rate.version == 1
    assert rate.approved_by == ppl.releaser
    assert odoo_env["fix.brand.reimbursement.rate"].rate_for(brand, "l1") == rate


def test_a_released_rate_is_never_edited(odoo_env, ppl, brand):
    rate = _rate(odoo_env, ppl.officer, brand, _today(odoo_env))
    rate.with_user(ppl.officer).action_submit()
    approve_via_inbox(rate, ppl.releaser, requester=ppl.officer)
    with pytest.raises(UserError, match="cannot change any more"), odoo_env.cr.savepoint():
        rate.with_user(ppl.officer).write({"labour_rate": 9999.0})


def test_a_new_circular_supersedes_and_claims_read_their_service_date(odoo_env, ppl, brand):
    Rate = odoo_env["fix.brand.reimbursement.rate"]
    today = _today(odoo_env)
    first_day = today - timedelta(days=60)
    old = _rate(odoo_env, ppl.officer, brand, first_day, labour=1000.0)
    old.with_user(ppl.officer).action_submit()
    approve_via_inbox(old, ppl.releaser, requester=ppl.officer)
    new = _rate(odoo_env, ppl.officer, brand, today, labour=1500.0, markup=0.0)
    new.with_user(ppl.officer).action_submit()
    approve_via_inbox(new, ppl.releaser, requester=ppl.officer)
    assert (old.state, new.state) == ("superseded", "active")
    assert (old.version, new.version) == (1, 2)
    assert old.valid_to == today - timedelta(days=1)
    # BRU-PRC-12: a job serviced last month is valued at last month's rate
    assert Rate.rate_for(brand, "l1", on_date=today - timedelta(days=10)) == old
    assert Rate.rate_for(brand, "l1", on_date=today) == new
    assert not Rate.rate_for(brand, "l1", on_date=first_day - timedelta(days=1))
    assert old.reimbursement_for(parts_cost=500.0) == 1550.0  # 1000 + 500 x 1.10
    assert new.reimbursement_for(parts_cost=500.0) == 2000.0


def test_a_back_dated_version_cannot_rewrite_history(odoo_env, ppl, brand):
    today = _today(odoo_env)
    current = _rate(odoo_env, ppl.officer, brand, today)
    current.with_user(ppl.officer).action_submit()
    approve_via_inbox(current, ppl.releaser, requester=ppl.officer)
    earlier = _rate(odoo_env, ppl.officer, brand, today - timedelta(days=30), labour=900.0)
    with pytest.raises(UserError, match="already prices this brand"), odoo_env.cr.savepoint():
        earlier.with_user(ppl.officer).action_submit()


def test_retirement_needs_a_releaser_and_a_reason_and_keeps_history(odoo_env, ppl, brand):
    today = _today(odoo_env)
    rate = _rate(odoo_env, ppl.officer, brand, today - timedelta(days=5))
    rate.with_user(ppl.officer).action_submit()
    approve_via_inbox(rate, ppl.releaser, requester=ppl.officer)
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        rate.with_user(ppl.officer).action_retire(reason="agreement ended")
    with pytest.raises(UserError, match="State why"), odoo_env.cr.savepoint():
        rate.with_user(ppl.releaser).action_retire(reason=" ")
    rate.with_user(ppl.releaser).action_retire(reason="agreement ended")
    assert rate.state == "retired"
    Rate = odoo_env["fix.brand.reimbursement.rate"]
    assert Rate.rate_for(brand, "l1", on_date=today - timedelta(days=2)) == rate
    assert not Rate.rate_for(brand, "l1", on_date=today + timedelta(days=1))
