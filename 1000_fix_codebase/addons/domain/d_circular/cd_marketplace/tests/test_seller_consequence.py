"""M12 seller consequences and the customer rating (capture audit, 13 Nov 2026).

Sub-module 7 "Performance Consequences" had no record: probation, suspension
and the appeal against them (FR-MKP-053..055, seller lifecycle s.8.1) had no
store, so the page had nothing to capture. fix.seller.consequence is that
record, exercised as the roles that use it:

  * an operator records and imposes it; a probation needs its remediation
    plan and review date; its terms are pinned once imposed;
  * lifting it, or deciding the seller's appeal, is another operator's
    (BRU-MKP-18);
  * while a suspension is in force (an appeal does not lift it) the seller's
    live listings are paused and no quote, award or listing goes live
    (BRU-MKP-11);
  * a consequence in force past its end date expires (daily cron).

The customer's sign-off rating feeds the seller score; it was stored as given
(7, -3). It is now a whole number from 1 to 5, or none.
"""

import types
from contextlib import contextmanager
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, AccessError, ValidationError)
OPERATOR = "cd_marketplace.group_marketplace_operator"
SELLER_PORTAL = "cd_marketplace.group_fix_marketplace_seller"
CQ = "fix.seller.consequence"


@contextmanager
def _refused(env, exc=REFUSED, match=None):
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def cq(odoo_env):
    env = odoo_env
    users = env["res.users"].with_context(no_reset_password=True)

    def user(login, *groups):
        return users.create(
            {
                "name": login.replace("_", " ").title(),
                "login": login,
                "group_ids": [Command.set([env.ref(g).id for g in groups])],
            }
        )

    x = types.SimpleNamespace(env=env)
    x.plain = user("cq_plain", "base.group_user")
    x.operator = user("cq_operator", "base.group_user", OPERATOR)
    x.operator2 = user("cq_operator_two", "base.group_user", OPERATOR)
    x.seller_user = user("cq_seller", SELLER_PORTAL)
    x.category = env["product.category"].create({"name": "CQ Screen Repair"})
    # a verified, CFO-approved seller, set up as trusted (sudo) code
    x.seller = (
        env["fix.marketplace.seller"]
        .sudo()
        .create(
            {
                "name": "CQ Shop",
                "partner_id": x.seller_user.partner_id.id,
                "category_ids": [Command.set(x.category.ids)],
                "kyc_status": "verified",
                "cfo_approved": True,
            }
        )
    )
    x.listing = (
        env["fix.marketplace.listing"]
        .sudo()
        .create(
            {
                "name": "CQ Screen Swap",
                "seller_id": x.seller.id,
                "category_id": x.category.id,
                "state": "active",
            }
        )
    )
    x.customer = env["res.partner"].create({"name": "CQ Customer"})
    x.today = fields.Date.context_today(env[CQ])
    return x


def _new(x, user=None, **vals):
    base = {
        "seller_id": x.seller.id,
        "consequence_type": "suspension",
        "trigger": "counterfeit",
        "reason": "Non-genuine display fitted on job MKT/0001; test report attached.",
    }
    base.update(vals)
    return x.env[CQ].with_user(user or x.operator).create(base)


def _order(x):
    return (
        x.env["fix.marketplace.order"]
        .with_user(x.operator)
        .create(
            {
                "order_type": "service_quote",
                "customer_id": x.customer.id,
                "category_id": x.category.id,
                "description": "CQ screen replacement",
                "customer_consent": True,
                "consent_method": "signed",
            }
        )
    )


# ---------------------------------------------------------------- capture


def test_an_operator_records_and_imposes_it(cq):
    rec = _new(cq)
    assert rec.state == "draft" and rec.name.startswith("SCQ/")
    rec.with_user(cq.operator).action_impose()
    assert rec.state == "active" and rec.imposed_by_id == cq.operator
    assert rec.imposed_at


def test_a_plain_user_records_nothing(cq):
    with _refused(cq.env):
        _new(cq, user=cq.plain)


def test_a_probation_needs_its_plan_and_review_date(cq):
    rec = _new(cq, consequence_type="probation", trigger="score")
    with _refused(cq.env, match="remediation plan"):
        rec.with_user(cq.operator).action_impose()
    rec.with_user(cq.operator).write(
        {
            "remediation_plan": "Complete the evidence-capture course; 10 jobs with full photos.",
            "review_date": cq.today + timedelta(days=30),
        }
    )
    rec.with_user(cq.operator).action_impose()
    assert rec.state == "active"


def test_its_terms_are_pinned_once_imposed(cq):
    rec = _new(cq)
    rec.with_user(cq.operator).action_impose()
    with _refused(cq.env, match="pinned"):
        rec.with_user(cq.operator).write({"consequence_type": "warning"})
    with _refused(cq.env):
        rec.with_user(cq.operator).write({"state": "lifted"})


def test_dates_run_forward(cq):
    with _refused(cq.env, match="ends on or after"):
        _new(cq, effective_from=cq.today, effective_to=cq.today - timedelta(days=1))


# ---------------------------------------------------------------- appeal / lift


def test_the_imposer_does_not_decide_the_appeal(cq):
    rec = _new(cq)
    rec.with_user(cq.operator).action_impose()
    rec.with_user(cq.operator).action_appeal(reason="The part was supplied by the customer.")
    assert rec.state == "appealed"
    with _refused(cq.env, match="Segregation"):
        rec.with_user(cq.operator).action_uphold_appeal(note="Upheld")
    rec.with_user(cq.operator2).action_dismiss_appeal(
        note="Purchase invoice shows the seller bought it."
    )
    assert rec.state == "active" and rec.decided_by_id == cq.operator2


def test_another_operator_lifts_it_on_verified_remediation(cq):
    rec = _new(cq)
    rec.with_user(cq.operator).action_impose()
    with _refused(cq.env, match="Segregation"):
        rec.with_user(cq.operator).action_lift(note="done")
    with _refused(cq.env, match="verified"):
        rec.with_user(cq.operator2).action_lift(note="  ")
    rec.with_user(cq.operator2).action_lift(note="Stock audited; genuine parts only.")
    assert rec.state == "lifted"


# ---------------------------------------------------------------- suspension bites


def test_a_suspension_pauses_live_listings_and_blocks_going_live(cq):
    rec = _new(cq)
    rec.with_user(cq.operator).action_impose()
    assert cq.listing.state == "paused"
    with _refused(cq.env, match="suspended"):
        cq.listing.with_user(cq.operator).action_resume()
    # an appeal does not lift it
    rec.with_user(cq.operator).action_appeal(reason="Disputed")
    with _refused(cq.env, match="suspended"):
        cq.listing.with_user(cq.operator).action_resume()


def test_a_suspended_seller_cannot_quote(cq):
    order = _order(cq)
    _new(cq).with_user(cq.operator).action_impose()
    with _refused(cq.env, match="suspended"):
        cq.env["fix.seller.quote"].with_user(cq.operator).create(
            {
                "marketplace_order_id": order.id,
                "seller_id": cq.seller.id,
                "quoted_price": 1500.0,
                "eta_days": 2,
            }
        )


def test_a_quote_received_before_the_suspension_is_not_awarded(cq):
    order = _order(cq)
    quote = (
        cq.env["fix.seller.quote"]
        .with_user(cq.operator)
        .create(
            {
                "marketplace_order_id": order.id,
                "seller_id": cq.seller.id,
                "quoted_price": 1500.0,
                "eta_days": 2,
            }
        )
    )
    _new(cq).with_user(cq.operator).action_impose()
    with _refused(cq.env, match="suspended"):
        quote.with_user(cq.operator).action_select()


def test_a_warning_does_not_block_transacting(cq):
    _new(cq, consequence_type="warning", trigger="evidence").with_user(cq.operator).action_impose()
    assert not cq.seller._active_suspension()


def test_a_lapsed_consequence_expires(cq):
    rec = _new(cq, effective_from=cq.today - timedelta(days=10))
    rec.with_user(cq.operator).action_impose()
    rec.sudo().write({"effective_to": cq.today - timedelta(days=1)})
    assert cq.env[CQ].cron_expire_consequences() >= 1
    assert rec.state == "expired"
    assert not cq.seller._active_suspension()


# ---------------------------------------------------------------- rating


def _completed(cq):
    order = _order(cq)
    order.sudo()._guarded().write({"state": "completed"})
    return order


@pytest.mark.parametrize("rating", [7, -3, 0.5, "x"])
def test_a_rating_outside_1_to_5_is_refused(cq, rating):
    order = _completed(cq)
    with _refused(cq.env, match="1 to 5"):
        order.with_user(cq.operator).action_review(rating=rating)


@pytest.mark.parametrize("rating,stored", [(5, 5), ("4", 4), (None, 0), ("", 0)])
def test_a_rating_from_1_to_5_or_none_is_recorded(cq, rating, stored):
    order = _completed(cq)
    order.with_user(cq.operator).action_review(rating=rating)
    assert order.state == "reviewed" and order.review_rating == stored
