"""M10 capture audit, pass 2 (2026-11-18): the records six sub-module pages
could not capture, tested as NON-ADMIN users against the database.

Each control is checked both ways: the bypass is refused and the
legitimate path works. The superuser is trusted by the guards, so every
actor is a freshly created user holding only the groups named.
"""

from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers.a03 import m10 as m10_api
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError

T2 = "cd_entity_config.group_dofa_tier_2"
T3 = "cd_entity_config.group_dofa_tier_3"
FIN = "account.group_account_manager"


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def make_user(env):
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "M10 Capture Probe %d" % counter["n"],
                    "login": "m10.cap2.probe.%d@a03.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def clerk(make_user):
    return make_user()


@pytest.fixture
def program(env):
    program = env["fix.loyalty.program"].create(
        {
            "name": "M10 Cap2 Privilege",
            "code": "M10CAP2",
            "points_per_bdt": 0.01,
            "bdt_per_point": 0.5,
        }
    )
    env["fix.loyalty.tier"].create(
        {
            "program_id": program.id,
            "name": "Privilege",
            "code": "CAP2PRIV",
            "sequence": 1,
            "membership_fee_bdt": 1200.0,
            "membership_duration_months": 12,
            "membership_grace_days": 15,
        }
    )
    return program


@pytest.fixture
def tier(program):
    return program.tier_ids[:1]


def _partner(env, name, **kw):
    return env["res.partner"].create(dict({"name": name}, **kw))


# ---------------------------------------------------------------------------
# Page 1 - paid membership
# ---------------------------------------------------------------------------
def test_membership_activates_only_on_confirmed_payment(env, clerk, program, tier):
    member = _partner(env, "Cap2 Member A")
    m = (
        env["fix.loyalty.membership"]
        .with_user(clerk)
        .create({"partner_id": member.id, "program_id": program.id, "tier_id": tier.id})
    )
    assert m.state == "pending" and m.price_bdt == 1200.0 and m.duration_months == 12
    assert m.name.startswith("MEM/")
    with pytest.raises(UserError, match="M20"):
        m.action_confirm_payment()
    with pytest.raises(UserError):
        m.write({"state": "active"})
    m.action_confirm_payment(payment_ref="RCPT-001")
    assert m.state == "active" and m.started_on and m.expires_on
    assert (m.expires_on - m.started_on).days in (364, 365)
    assert m.deferred_bdt + m.recognised_bdt == pytest.approx(1200.0)
    assert m.deferred_bdt > 1100.0, "BRU-LOY-12: the fee is not earned at sale"
    with pytest.raises(UserError, match="fixed once paid"):
        m.write({"price_bdt": 1.0})


def test_one_open_membership_per_member_and_renewal_waits(env, clerk, program, tier):
    member = _partner(env, "Cap2 Member B")
    M = env["fix.loyalty.membership"].with_user(clerk)
    m = M.create({"partner_id": member.id, "program_id": program.id, "tier_id": tier.id})
    with pytest.raises(ValidationError, match="open membership"), env.cr.savepoint():
        M.create({"partner_id": member.id, "program_id": program.id, "tier_id": tier.id})
    m.action_confirm_payment(payment_ref="RCPT-002")
    m.action_renew()
    renewal = M.search([("renewal_of_id", "=", m.id)])
    assert renewal.state == "pending"
    renewal.action_confirm_payment(payment_ref="RCPT-003")
    assert renewal.started_on == m.expires_on + timedelta(days=1), "no overlap, no gap"


def test_lapse_withdraws_benefits_on_the_stated_date(env, clerk, program, tier):
    member = _partner(env, "Cap2 Member C")
    m = (
        env["fix.loyalty.membership"]
        .with_user(clerk)
        .create({"partner_id": member.id, "program_id": program.id, "tier_id": tier.id})
    )
    m.action_confirm_payment(payment_ref="RCPT-004")
    old = fields.Date.today() - timedelta(days=400)
    m.sudo()._guarded().write({"started_on": old})
    env["fix.loyalty.membership"].cron_membership_lifecycle()
    assert m.state == "lapsed"
    assert m.benefits_withdrawn_on == m.grace_until + timedelta(days=1)
    assert not env["fix.loyalty.membership"]._live_for(member, program)


def test_cancel_and_suspend_need_a_reason(env, clerk, program, tier):
    m = (
        env["fix.loyalty.membership"]
        .with_user(clerk)
        .create(
            {
                "partner_id": _partner(env, "Cap2 Member D").id,
                "program_id": program.id,
                "tier_id": tier.id,
            }
        )
    )
    m.action_confirm_payment(payment_ref="RCPT-005")
    with pytest.raises(UserError):
        m.action_suspend()
    m.action_suspend(reason="non-payment of instalment")
    assert m.state == "suspended"
    m.action_reinstate()
    with pytest.raises(UserError):
        m.action_cancel()
    m.action_cancel(reason="customer request")
    assert m.state == "cancelled" and m.benefits_withdrawn_on == fields.Date.context_today(m)


# ---------------------------------------------------------------------------
# Page 2 - BRU-LOY-01
# ---------------------------------------------------------------------------
def test_privilege_discount_never_reaches_parts(env, clerk, tier):
    B = env["fix.loyalty.benefit"].with_user(clerk)
    with pytest.raises(ValidationError, match="BRU-LOY-01"), env.cr.savepoint():
        B.create(
            {
                "tier_id": tier.id,
                "code": "LD",
                "name": "Labour 50",
                "value": 50,
                "benefit_type": "labour_discount",
                "applies_to": "parts",
            }
        )
    with pytest.raises(ValidationError, match="BRU-LOY-01"), env.cr.savepoint():
        tier.with_user(clerk).write({"parts_discount_pct": 10.0})
    ok = B.create(
        {
            "tier_id": tier.id,
            "code": "LD",
            "name": "Labour 50",
            "value": 50,
            "benefit_type": "labour_discount",
            "applies_to": "labour",
        }
    )
    assert ok.discount_for("labour", 1000) == 500.0
    for kind in ("parts", "consumables", "transport"):
        assert ok.discount_for(kind, 1000) == 0.0, "AC-01: no discount on %s" % kind


# ---------------------------------------------------------------------------
# Page 4 - BDT wallet
# ---------------------------------------------------------------------------
def _credit(env, user, partner, amount, kind="refund"):
    txn = (
        env["fix.loyalty.wallet.txn"]
        .with_user(user)
        .create(
            {
                "partner_id": partner.id,
                "entry_type": kind,
                "amount": amount,
                "source_ref": "RF-1",
                "reason": "goodwill" if kind == "goodwill" else False,
            }
        )
    )
    txn.action_post()
    return txn


def test_wallet_credit_needs_a_source_and_cannot_be_overdrawn(env, clerk, make_user):
    cust = _partner(env, "Cap2 Wallet A")
    Txn = env["fix.loyalty.wallet.txn"].with_user(clerk)
    bare = Txn.create({"partner_id": cust.id, "entry_type": "refund", "amount": 500})
    with pytest.raises(UserError, match="source"):
        bare.action_post()
    credit = _credit(env, clerk, cust, 500.0)
    assert credit.wallet_id.partner_id == cust and credit.wallet_id.balance_bdt == 500.0
    with pytest.raises(UserError):
        credit.write({"amount": 9000})
    with pytest.raises(UserError):
        credit.wallet_id.write({"balance_bdt": 99999})
    doc = (
        env["fix.identity.document"]
        .sudo()
        .create({"partner_id": cust.id, "document_type": "nid_10", "document_number": "1234567890"})
    )
    doc.sudo()._guarded().write({"verification_status": "verified"})
    payout = Txn.create(
        {
            "partner_id": cust.id,
            "entry_type": "payout",
            "amount": 800,
            "payout_method": "bkash",
            "payout_account": "01700000000",
            "id_document_id": doc.id,
        }
    )
    with pytest.raises(UserError, match="holds BDT 500"):
        payout.with_user(make_user()).action_post()  # not the credit's author (SOD-18)


def test_points_never_convert_into_wallet_money():
    from odoo.addons.cd_loyalty.models import fix_loyalty_capture as cap

    kinds = cap.CREDIT_TYPES + cap.DEBIT_TYPES
    assert not [k for k in kinds if "point" in k], "BRU-LOY-07 / AC-05"


def test_payout_needs_verified_identity_and_separated_approval(env, clerk, make_user):
    cust = _partner(env, "Cap2 Wallet B")
    _credit(env, clerk, cust, 20000.0)
    Txn = env["fix.loyalty.wallet.txn"]
    unverified = (
        env["fix.identity.document"]
        .sudo()
        .create({"partner_id": cust.id, "document_type": "nid_10", "document_number": "9876543210"})
    )
    small = Txn.with_user(clerk).create(
        {
            "partner_id": cust.id,
            "entry_type": "payout",
            "amount": 1000,
            "payout_method": "nagad",
            "payout_account": "01800000000",
            "id_document_id": unverified.id,
        }
    )
    with pytest.raises(UserError, match="BRU-LOY-13"):
        small.action_post()
    unverified.sudo()._guarded().write({"verification_status": "verified"})
    # below the BDT 5,000 bar: no approval, but SOD-18 still bars the credit's author
    with pytest.raises(UserError, match="SOD-18"):
        small.action_post()
    teller = make_user()
    small.with_user(teller).action_post()
    assert small.state == "posted" and small.wallet_id.balance_bdt == 19000.0

    big = Txn.with_user(teller).create(
        {
            "partner_id": cust.id,
            "entry_type": "payout",
            "amount": 15000,
            "payout_method": "bank",
            "payout_account": "0123456789",
            "id_document_id": unverified.id,
            "dofa_justification": "customer leaving the city; balance returned",
        }
    )
    assert big.dofa_tier_required == "tier_2"
    with pytest.raises((UserError, ValidationError)):
        big.with_user(teller).action_post()
    approver = make_user(T2)
    approve_via_inbox(big, approver, requester=teller)
    assert big.dofa_approved
    big.with_user(teller).action_post()
    assert big.wallet_id.balance_bdt == 4000.0


# ---------------------------------------------------------------------------
# Page 5 - voucher batches and stacking
# ---------------------------------------------------------------------------
def test_voucher_batch_issues_within_limit_and_closes(env, clerk, program):
    a, b = _partner(env, "Cap2 V A"), _partner(env, "Cap2 V B")
    Batch = env["fix.loyalty.voucher.batch"].with_user(clerk)
    with pytest.raises(ValidationError), env.cr.savepoint():
        Batch.create(
            {
                "name": "Too big",
                "code_prefix": "BIG",
                "program_id": program.id,
                "batch_type": "bulk",
                "quantity": 20000,
                "discount_value": 100,
                "valid_until": fields.Date.today() + timedelta(days=30),
            }
        )
    pers = Batch.create(
        {
            "name": "Eid",
            "code_prefix": "EID26",
            "program_id": program.id,
            "batch_type": "personalised",
            "partner_ids": [(6, 0, [a.id, b.id])],
            "discount_value": 200,
            "valid_until": fields.Date.today() + timedelta(days=30),
        }
    )
    pers.action_issue()
    assert pers.state == "issued" and pers.issued_count == 2
    assert set(pers.voucher_ids.mapped("partner_id")) == {a, b}
    assert all(v.name.startswith("EID26-") for v in pers.voucher_ids)
    with pytest.raises(UserError):
        pers.write({"discount_value": 5000})
    bulk = Batch.create(
        {
            "name": "Flyer",
            "code_prefix": "FLY",
            "program_id": program.id,
            "batch_type": "bulk",
            "quantity": 5,
            "discount_value": 10,
            "discount_type": "percentage",
            "valid_until": fields.Date.today() + timedelta(days=30),
        }
    )
    bulk.action_issue()
    assert bulk.issued_count == 5 and not bulk.voucher_ids.mapped("partner_id")
    bulk.action_close()
    assert bulk.closed_unredeemed == 5
    assert set(bulk.voucher_ids.mapped("state")) == {"cancelled"}


def test_batch_eligibility_is_enforced_at_redemption(env, clerk, program):
    a, b = _partner(env, "Cap2 E A"), _partner(env, "Cap2 E B")
    batch = (
        env["fix.loyalty.voucher.batch"]
        .with_user(clerk)
        .create(
            {
                "name": "Big spend",
                "code_prefix": "BIGS",
                "program_id": program.id,
                "batch_type": "personalised",
                "partner_ids": [(6, 0, [a.id])],
                "discount_value": 300,
                "min_spend_bdt": 5000,
                "valid_until": fields.Date.today() + timedelta(days=30),
            }
        )
    )
    batch.action_issue()
    voucher = batch.voucher_ids
    assert "minimum spend" in "; ".join(voucher._batch_eligibility_errors(a, amount=100))
    assert voucher._batch_eligibility_errors(b, amount=9000)
    assert not voucher._batch_eligibility_errors(a, amount=9000)


def test_stacking_is_deterministic_and_capped(env, clerk, program):
    S = env["fix.loyalty.stacking.rule"].with_user(clerk)
    S.create(
        {
            "program_id": program.id,
            "component_a": "voucher",
            "component_b": "promotion",
            "allowed": False,
        }
    )
    S.create(
        {
            "program_id": program.id,
            "component_a": "tier_benefit",
            "component_b": "voucher",
            "allowed": True,
            "max_aggregate_pct": 40,
        }
    )
    with pytest.raises(ValidationError), env.cr.savepoint():
        S.create({"program_id": program.id, "component_a": "promotion", "component_b": "voucher"})
    comps = [
        {"kind": "promotion", "pct": 15},
        {"kind": "voucher", "pct": 25},
        {"kind": "tier_benefit", "pct": 30},
    ]
    out = S.evaluate(program, comps)
    again = S.evaluate(program, list(reversed(comps)))
    assert out == again, "AC-06: the same inputs give the same outcome"
    assert [c["kind"] for c in out["dropped"]] == ["promotion"]
    assert out["total_pct"] == 40.0, "AC-07: the combined ceiling holds"
    assert len(out["fired"]) == 2


# ---------------------------------------------------------------------------
# Page 6 - referral attribution
# ---------------------------------------------------------------------------
@pytest.fixture
def code(env, program):
    referrer = _partner(
        env, "Cap2 Referrer", phone="+8801711000001", street="12 Road 5", city="Dhaka"
    )
    return env["fix.loyalty.referral.code"].create(
        {"name": "CAP2REF", "program_id": program.id, "referrer_partner_id": referrer.id}
    )


def test_self_and_household_referrals_are_blocked(env, clerk, code):
    Ev = env["fix.loyalty.referral.event"].with_user(clerk)
    same_phone = _partner(env, "Cap2 Cousin", phone="+880 1711-000001")
    same_home = _partner(env, "Cap2 Spouse", street="12 Road 5", city="Dhaka")
    self_ref = Ev.create({"code_id": code.id, "referee_partner_id": code.referrer_partner_id.id})
    assert self_ref.block_reason == "self-referral (same customer or company)"
    assert Ev.create({"code_id": code.id, "referee_partner_id": same_phone.id}).state == "blocked"
    home = Ev.create({"code_id": code.id, "referee_partner_id": same_home.id})
    assert home.state == "blocked" and "household" in home.block_reason
    fresh = Ev.create({"code_id": code.id, "referee_partner_id": _partner(env, "Cap2 New").id})
    assert fresh.state == "registered" and fresh.name.startswith("REF/")
    with pytest.raises(UserError):
        fresh.write({"state": "rewarded"})


def test_first_attribution_wins_and_cap_applies(env, clerk, code, program):
    Ev = env["fix.loyalty.referral.event"].with_user(clerk)
    newbie = _partner(env, "Cap2 Newbie")
    Ev.create({"code_id": code.id, "referee_partner_id": newbie.id})
    other = env["fix.loyalty.referral.code"].create(
        {
            "name": "CAP2REF2",
            "program_id": program.id,
            "referrer_partner_id": _partner(env, "Cap2 Other Referrer").id,
        }
    )
    second = Ev.create({"code_id": other.id, "referee_partner_id": newbie.id})
    assert second.state == "blocked" and "first attribution" in second.block_reason
    program.sudo().write({"referral_cap_per_month": 1})
    capped = Ev.create({"code_id": code.id, "referee_partner_id": _partner(env, "Cap2 N2").id})
    assert capped.state == "blocked" and "cap" in capped.block_reason


def test_referral_qualifies_only_on_a_completed_service(env, clerk, code):
    ev = (
        env["fix.loyalty.referral.event"]
        .with_user(clerk)
        .create({"code_id": code.id, "referee_partner_id": _partner(env, "Cap2 Q").id})
    )
    with pytest.raises(UserError, match="completed service"):
        ev.action_qualify()


# ---------------------------------------------------------------------------
# Page 8 - liability run
# ---------------------------------------------------------------------------
def test_liability_run_reconciles_and_is_published_by_another_finance_user(env, make_user, program):
    acct = env["fix.loyalty.account"].create(
        {"partner_id": _partner(env, "Cap2 Points").id, "program_id": program.id}
    )
    line = env["fix.loyalty.ledger"].create(
        {
            "account_id": acct.id,
            "transaction_type": "accrual",
            "points": 400,
            "company_id": acct.company_id.id,
            "notes": "test accrual",
        }
    )
    line.action_post()
    analyst, fin1, fin2 = make_user(), make_user(FIN), make_user(FIN)
    run = (
        env["fix.loyalty.liability.run"]
        .with_user(analyst)
        .create({"program_id": program.id, "period_end": fields.Date.today()})
    )
    assert run.name.startswith("LIAB/")
    with pytest.raises(UserError):
        run.write({"net_liability": 1.0})
    run.with_user(fin1).action_calculate()
    assert run.points_outstanding == 400 and run.gross_liability == 200.0
    assert run.reconciles
    with pytest.raises(AccessError):
        run.with_user(analyst).action_publish()
    with pytest.raises(UserError, match="Segregation"):
        run.with_user(fin1).action_publish()
    run.with_user(fin2).action_publish()
    assert run.state == "published" and run.published_by == fin2
    with pytest.raises(UserError):
        run.with_user(fin2).action_calculate()


def test_breakage_needs_its_basis_before_publication(env, make_user, program):
    program.sudo().write({"expected_breakage_pct": 20.0})
    fin1, fin2 = make_user(FIN), make_user(FIN)
    run = (
        env["fix.loyalty.liability.run"]
        .with_user(fin1)
        .create({"program_id": program.id, "period_end": fields.Date.today() - timedelta(days=1)})
    )
    run.action_calculate()
    with pytest.raises(UserError, match="basis"):
        run.with_user(fin2).action_publish()
    run.with_user(fin1).write({"breakage_basis": "Auditor-agreed launch assumption (Q-04)."})
    run.with_user(fin2).action_publish()
    assert run.state == "published"


def test_aggregate_cap_is_a_director_decision(env, clerk, program):
    with pytest.raises(UserError, match="Tier 3"):
        program.with_user(clerk).write({"max_aggregate_discount_pct": 60.0})
    program.with_user(clerk).write({"max_aggregate_discount_pct": 100.0})  # unchanged re-post


def test_deferral_report_reads_the_memberships(env, clerk, program, tier):
    m = (
        env["fix.loyalty.membership"]
        .with_user(clerk)
        .create(
            {
                "partner_id": _partner(env, "Cap2 Report").id,
                "program_id": program.id,
                "tier_id": tier.id,
            }
        )
    )
    m.action_confirm_payment(payment_ref="RCPT-RPT")
    pack = m10_api.membership_deferral(env)
    row = next(r for r in pack["rows"] if r["membership"] == m.name)
    assert row["price"] == 1200.0 and row["deferred"] > 0
