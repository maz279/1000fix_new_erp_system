"""A03 P2 · M10 loyalty lifecycle repair, tested as NON-ADMIN users.

Covers report §4.2 and the P2 row "M10" (findings M10-1, -2, -4, -6, -7,
-10, -11 and the IFRS 15 breakage decision):

  1. a closed service order earns through the R8 relay, once per order;
     a converted referral pays its configured award;
  2. points_balance is derived from the posted ledger and reconciled;
  3. a zero spend floor no longer counts as met (1 point gave Platinum);
  4. the expiry cron survives a frozen account; vouchers expire by cron;
  5. a fraud-freeze release is routed through the M63 inbox;
  6. the IFRS 15 liability is carried net of a configurable breakage rate;
  7. party.merged moves loyalty to the survivor through ledger lines.

Every actor is a freshly created user holding only the groups named,
because the superuser is trusted by the guards and would hide the gaps.
Each control is checked both ways: the bypass is refused and the
legitimate path works.
"""

from datetime import date, timedelta

import pytest
from odoo.addons.cd_p03_portal.controllers.a03 import m10 as m10_api
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

T2 = "cd_entity_config.group_dofa_tier_2"
T3 = "cd_entity_config.group_dofa_tier_3"


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
                    "name": "M10 P2 Probe %d" % counter["n"],
                    "login": "m10.p2.probe.%d@a03.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def program(env):
    program = env["fix.loyalty.program"].create(
        {"name": "M10P2 Privilege", "code": "M10P2", "points_per_bdt": 0.01, "bdt_per_point": 0.5}
    )
    tiers = env["fix.loyalty.tier"]
    tiers.create({"program_id": program.id, "name": "Silver", "code": "P2SILVER", "sequence": 1})
    tiers.create(
        {
            "program_id": program.id,
            "name": "Gold",
            "code": "P2GOLD",
            "sequence": 2,
            "min_points_threshold": 1000,
            "min_spend_bdt": 50000.0,
        }
    )
    return program


@pytest.fixture
def customer(env):
    return env["res.partner"].create({"name": "M10P2 Member"})


def _account(env, program, partner):
    return env["fix.loyalty.account"].create({"partner_id": partner.id, "program_id": program.id})


@pytest.fixture
def account(env, program, customer):
    return _account(env, program, customer)


@pytest.fixture
def make_order(env):
    """A closed service order for `partner` that settled `amount` BDT."""
    company = env["res.company"].create({"name": "M10P2 Orders Co"})
    entity = env["fix.entity"].create(
        {"code": "M10P2ENT", "legal_name": "M10P2 Entity", "company_id": company.id}
    )
    ou = env["operating.unit"].search([], limit=1)
    branch = env["fix.branch"].create(
        {
            "name": "M10P2 Branch",
            "code": "M10P2BR",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "M10P2Brand", "code": "M10P2B"})
    model = env["fix.device.model"].create({"name": "M10P2 Phone", "brand_id": brand.id})
    counter = {"n": 0}

    def _make(partner, amount, state="closed"):
        counter["n"] += 1
        device = env["fix.device"].create(
            {
                "device_model_id": model.id,
                "owner_id": partner.id,
                "serial_number": "SN-M10P2-%d" % counter["n"],
            }
        )
        return env["fix.service.order"].create(
            {
                "device_id": device.id,
                "customer_id": partner.id,
                "branch_id": branch.id,
                "fault_description": "Screen replacement",
                "state": state,
                "amount_settled_bdt": amount,
            }
        )

    return _make


def _relay(env):
    env["fix.event.consumer"].sudo().search([("module", "=", "cd_loyalty")]).write(
        {"active_from": "2000-01-01 00:00:00"}
    )
    return env["fix.event.outbox"].cron_relay()


def _close(env, order):
    """Publish what cd_service_order publishes when an order closes."""
    return publish(
        env,
        "service_order.closed",
        "fix.service.order",
        order.id,
        {"order_id": order.id, "name": order.name, "customer_id": order.customer_id.id},
    )


def _event(env, event_id):
    return env["fix.event.outbox"].search([("event_id", "=", event_id)])._relay_event_dict()


def _lines(env, account, **filters):
    domain = [("account_id", "=", account.id)] + [(k, "=", v) for k, v in filters.items()]
    return env["fix.loyalty.ledger"].search(domain)


def _post(env, user, account, points, kind="accrual", **vals):
    line = (
        env["fix.loyalty.ledger"]
        .with_user(user)
        .create({"account_id": account.id, "transaction_type": kind, "points": points, **vals})
    )
    line.action_post()
    return line


# ==========================================================================
# 1. Earn on closed service orders (M10-10)
# ==========================================================================
class TestEarnOnClosedOrders:
    def test_the_consumers_are_registered(self, env):
        consumers = env["fix.event.consumer"].search([("module", "=", "cd_loyalty")])
        assert {(c.event_type, c.method) for c in consumers} >= {
            ("service_order.closed", "consume_service_order_closed"),
            ("party.merged", "consume_party_merged"),
        }

    def test_a_closed_order_earns_once_through_the_relay(self, env, account, make_order):
        order = make_order(account.partner_id, 25000.0)
        _close(env, order)
        _relay(env)
        earned = _lines(env, account, transaction_type="accrual")
        assert len(earned) == 1
        assert (earned.points, earned.state, earned.service_order_id) == (250, "posted", order)
        assert earned.system_generated and earned.dofa_tier_required == "tier_0"
        assert account.points_balance == 250
        # A re-published event, and a direct redelivery, earn nothing more.
        replay = _close(env, order)
        _relay(env)
        env["fix.loyalty.account"].sudo().consume_service_order_closed(_event(env, replay))
        assert len(_lines(env, account, transaction_type="accrual")) == 1
        assert account.points_balance == 250

    def test_the_active_scheme_earn_rules_apply(self, env, make_user, account, make_order):
        scheme = env["fix.loyalty.scheme"].create(
            {
                "name": "P2 Double",
                "code": "P2DBL",
                "program_id": account.program_id.id,
                "estimated_annual_cost": 1000.0,
            }
        )
        env["fix.loyalty.earn.rule"].create(
            {
                "scheme_id": scheme.id,
                "name": "Everything doubles",
                "dimension": "all",
                "points_per_bdt": 0.02,
            }
        )
        scheme.with_user(make_user()).action_activate()
        order = make_order(account.partner_id, 10000.0)
        _close(env, order)
        _relay(env)
        line = _lines(env, account, transaction_type="accrual")
        assert line.points == 200 and "Everything doubles" in line.notes

    def test_system_accruals_skip_manual_dofa_but_not_the_velocity_check(
        self, env, account, make_order
    ):
        # 100,000 points each: as a manual credit this would need Tier 4.
        for _ in range(4):
            order = make_order(account.partner_id, 10_000_000.0)
            env["fix.loyalty.account"].sudo().consume_service_order_closed(
                {"event_id": "p2-%d" % order.id, "aggregate_id": order.id}
            )
        assert len(_lines(env, account, transaction_type="accrual", state="posted")) == 4
        assert account.state == "frozen" and "Velocity" in account.freeze_reason
        # A fifth order earns, but a frozen wallet takes no posting: held as draft.
        fifth = make_order(account.partner_id, 1000.0)
        env["fix.loyalty.account"].sudo().consume_service_order_closed(
            {"event_id": "p2-fifth", "aggregate_id": fifth.id}
        )
        held = _lines(env, account, service_order_id=fifth.id)
        assert held.state == "draft" and held.points == 10

    def test_a_manual_credit_of_any_label_is_still_metered(self, env, make_user, account):
        clerk = make_user()
        big = (
            env["fix.loyalty.ledger"]
            .with_user(clerk)
            .create({"account_id": account.id, "transaction_type": "accrual", "points": 1000000})
        )
        assert big.dofa_tier_required == "tier_4"
        with pytest.raises(ValidationError):
            big.action_post()
        with pytest.raises(ValidationError, match="negative"):
            _post(env, clerk, account, 5000, kind="redemption")
        with pytest.raises(ValidationError, match="merge"):
            _post(env, clerk, account, 100, kind="merge_transfer")

    def test_only_the_relay_may_call_a_consumer(self, env, make_user, account, make_order):
        clerk = make_user()
        order = make_order(account.partner_id, 25000.0)
        Account = env["fix.loyalty.account"].with_user(clerk)
        with pytest.raises(AccessError):
            Account.consume_service_order_closed({"event_id": "x", "aggregate_id": order.id})
        with pytest.raises(AccessError):
            Account.consume_party_merged(
                {"event_id": "x", "payload": {"victim_id": 1, "survivor_id": 2}}
            )
        assert not _lines(env, account)

    def test_an_open_order_earns_nothing(self, env, account, make_order):
        order = make_order(account.partner_id, 25000.0, state="ready")
        result = (
            env["fix.loyalty.account"]
            .sudo()
            .consume_service_order_closed({"event_id": "p2-open", "aggregate_id": order.id})
        )
        assert result["accrued"] == 0 and not _lines(env, account)


class TestReferralAward:
    @pytest.fixture
    def referral(self, env, program):
        program.write({"referral_referrer_points": 200, "referral_referee_points": 50})
        referrer = env["res.partner"].create({"name": "M10P2 Referrer"})
        referee = env["res.partner"].create({"name": "M10P2 Referee"})
        code = env["fix.loyalty.referral.code"].create(
            {
                "name": "P2-REF-1",
                "program_id": program.id,
                "referrer_partner_id": referrer.id,
                "referee_partner_id": referee.id,
            }
        )
        return code, _account(env, program, referrer), _account(env, program, referee)

    def test_the_referees_first_closed_order_converts_and_pays(self, env, referral, make_order):
        code, referrer_acct, referee_acct = referral
        _close(env, make_order(referee_acct.partner_id, 10000.0))
        _relay(env)
        assert code.state == "converted" and code.points_awarded == 250
        bonus = _lines(env, referrer_acct, transaction_type="referral_bonus")
        assert (bonus.points, bonus.state, bonus.system_generated) == (200, "posted", True)
        assert referrer_acct.points_balance == 200
        assert referee_acct.points_balance == 100 + 50  # order accrual + referee award

    def test_manual_conversion_needs_the_evidence(self, env, make_user, referral, make_order):
        code, referrer_acct, referee_acct = referral
        clerk = make_user()
        with pytest.raises(UserError, match="closed service order"):
            code.with_user(clerk).action_mark_converted()
        with pytest.raises(UserError):
            code.with_user(clerk).write({"state": "converted", "points_awarded": 999})
        make_order(referee_acct.partner_id, 1000.0)
        code.with_user(clerk).action_mark_converted()
        assert code.state == "converted" and referrer_acct.points_balance == 200
        with pytest.raises(UserError, match="pending"):
            code.with_user(clerk).action_mark_converted()

    def test_a_self_referral_never_pays(self, env, make_user, program, make_order):
        program.write({"referral_referrer_points": 200})
        member = env["res.partner"].create({"name": "M10P2 Self"})
        _account(env, program, member)
        code = env["fix.loyalty.referral.code"].create(
            {
                "name": "P2-SELF",
                "program_id": program.id,
                "referrer_partner_id": member.id,
                "referee_partner_id": member.id,
            }
        )
        make_order(member, 1000.0)
        with pytest.raises(UserError, match="refer themselves"):
            code.with_user(make_user()).action_mark_converted()

    def test_the_award_amount_is_a_director_setting(self, env, make_user, program):
        with pytest.raises(UserError, match="Tier 3"):
            program.with_user(make_user()).write({"referral_referrer_points": 100000})
        program.with_user(make_user()).write({"referral_referrer_points": 0, "name": "Renamed"})
        program.with_user(make_user(T3)).write({"referral_referrer_points": 200})
        assert program.referral_referrer_points == 200


# ==========================================================================
# 2. points_balance is derived, and reconciled (M10-2)
# ==========================================================================
class TestDerivedBalance:
    def test_the_balance_follows_the_posted_ledger_only(self, env, make_user, account):
        clerk = make_user()
        draft = (
            env["fix.loyalty.ledger"]
            .with_user(clerk)
            .create({"account_id": account.id, "transaction_type": "accrual", "points": 300})
        )
        assert account.points_balance == 0  # a draft moves nothing
        draft.action_post()
        assert account.points_balance == 300
        with pytest.raises(UserError):
            account.with_user(clerk).write({"points_balance": 4242424})
        reversal = env["fix.loyalty.ledger"].browse(
            draft.with_user(clerk).action_reverse(reason="Wrong member")["reversal_id"]
        )
        reversal.with_user(clerk).action_post()
        assert account.points_balance == 0

    def test_reconciliation_proves_and_flags_drift(self, env, make_user, account):
        clerk = make_user()
        _post(env, clerk, account, 400)
        clean = account.with_user(clerk).action_reconcile_balance()
        assert clean["drifted"] == 0 and account.balance_reconciled_at
        # Something writes around the ORM: a script, an import, old data.
        env.flush_all()
        env.cr.execute(
            "UPDATE fix_loyalty_account SET points_balance = 999 WHERE id = %s", (account.id,)
        )
        account.invalidate_recordset()
        result = account.with_user(clerk).action_reconcile_balance()
        assert result["drifted"] == 1
        assert result["detail"][0] == {
            "account": account.name,
            "stored": 999,
            "ledger": 400,
            "drift": 599,
        }
        assert account.balance_drift == 599
        env.cr.execute("SELECT points_balance FROM fix_loyalty_account WHERE id=%s", (account.id,))
        assert env.cr.fetchone()[0] == 400
        assert env["fix.event.outbox"].search_count(
            [("event_type", "=", "loyalty.balance_drift"), ("aggregate_id", "=", account.id)]
        )
        with pytest.raises(UserError):
            account.with_user(clerk).write({"balance_drift": 0})

    def test_the_reconciliation_cron_is_scheduled(self, env):
        cron = env.ref("cd_loyalty.ir_cron_loyalty_reconcile_balances")
        assert cron.active and "cron_reconcile_balances" in cron.code
        assert env["fix.loyalty.account"].cron_reconcile_balances() >= 0


# ==========================================================================
# 3. Tier trap (M10-6)
# ==========================================================================
class TestTierTrap:
    def test_one_point_no_longer_earns_platinum(self, env, make_user, program, account):
        env["fix.loyalty.tier"].create(
            {
                "program_id": program.id,
                "name": "Platinum",
                "code": "P2PLAT",
                "sequence": 4,
                "min_points_threshold": 100000,
            }
        )
        _post(env, make_user(), account, 1)
        assert account.tier_id.code == "P2SILVER"

    def test_either_real_floor_still_promotes(self, env, make_user, program, customer):
        clerk = make_user()
        by_points = _account(env, program, customer)
        _post(env, clerk, by_points, 400)
        _post(env, clerk, by_points, 400)
        _post(env, clerk, by_points, 300)
        assert by_points.tier_id.code == "P2GOLD"
        spender = _account(env, program, env["res.partner"].create({"name": "M10P2 Spender"}))
        _post(env, clerk, spender, 10, order_amount_bdt=60000.0)
        assert spender.tier_id.code == "P2GOLD"

    def test_posting_never_demotes(self, env, make_user, program, account):
        gold = program.tier_ids.filtered(lambda t: t.code == "P2GOLD")
        account.write({"tier_id": gold.id})
        _post(env, make_user(), account, 5)
        assert account.tier_id == gold


# ==========================================================================
# 4. Expiry (M10-7) and voucher expiry (M10-10)
# ==========================================================================
class TestExpiry:
    def test_one_frozen_account_no_longer_stops_the_run(self, env, make_user, program):
        clerk = make_user()
        healthy = _account(env, program, env["res.partner"].create({"name": "M10P2 Healthy"}))
        frozen = _account(env, program, env["res.partner"].create({"name": "M10P2 Frozen"}))
        lapsed = []
        for acct in (frozen, healthy):
            line = _post(env, clerk, acct, 300)
            line._guarded().write({"expiry_date": date.today() - timedelta(days=1)})
            lapsed.append(line)
        frozen._guarded().write({"state": "frozen"})
        assert env["fix.loyalty.ledger"].cron_expire_points() == 1
        assert healthy.points_balance == 0 and lapsed[1].points_expired
        # The frozen wallet is untouched and retried on the next run.
        assert frozen.points_balance == 300 and not lapsed[0].points_expired

    def test_lapsed_vouchers_expire_by_cron(self, env, customer):
        Voucher = env["fix.loyalty.voucher"]
        today = date.today()
        old = Voucher.create(
            {
                "partner_id": customer.id,
                "discount_type": "fixed_bdt",
                "discount_value": 100.0,
                "valid_from": today - timedelta(days=30),
                "valid_until": today - timedelta(days=1),
                "state": "active",
            }
        )
        live = Voucher.create(
            {
                "partner_id": customer.id,
                "discount_type": "fixed_bdt",
                "discount_value": 100.0,
                "valid_until": today + timedelta(days=30),
                "state": "active",
            }
        )
        assert Voucher.cron_expire_vouchers() >= 1
        assert (old.state, live.state) == ("expired", "active")
        cron = env.ref("cd_loyalty.ir_cron_loyalty_expire_vouchers")
        assert cron.active and cron.interval_type == "days"


# ==========================================================================
# 5. Fraud-freeze release through the M63 engine (M10-4)
# ==========================================================================
class TestFraudRelease:
    def _freeze(self, account):
        account._guarded().write({"state": "frozen", "freeze_reason": "Velocity check (test)"})

    def test_release_is_requested_and_approved_from_the_inbox(self, env, make_user, account):
        self._freeze(account)
        clerk, manager = make_user(), make_user(T2)
        with pytest.raises(UserError, match="inbox"):
            account.with_user(manager).action_unfreeze()
        with pytest.raises(UserError, match="frozen"):
            account.with_user(clerk).action_activate()
        approve_via_inbox(account, manager, clerk, justification="Repairs verified at branch.")
        assert account.state == "active" and account.unlock_supervisor_id == manager
        assert account.approval_state == "approved"

    def test_an_active_wallet_has_nothing_to_release(self, env, make_user, account):
        with pytest.raises(UserError, match="Nothing to approve"):
            account.with_user(make_user()).action_request_approval()

    def test_the_member_cannot_release_their_own_wallet(self, env, make_user, program):
        member_manager = make_user(T2)
        own = _account(env, program, member_manager.partner_id)
        self._freeze(own)
        clerk = make_user()
        own.with_user(clerk).action_request_approval(justification="Please release.")
        with pytest.raises(UserError, match="own wallet"):
            inbox_task(own, member_manager).with_user(member_manager).action_approve()
        assert own.state == "frozen"

    def test_a_rejected_release_keeps_the_freeze(self, env, make_user, account):
        self._freeze(account)
        clerk, manager = make_user(), make_user(T2)
        account.with_user(clerk).action_request_approval(justification="Looks fine.")
        inbox_task(account, manager).with_user(manager).action_reject(comment="Same-day bursts.")
        assert account.state == "frozen" and account.approval_state == "rejected"

    def test_a_new_freeze_needs_a_new_release(self, env, make_user, account):
        self._freeze(account)
        approve_via_inbox(account, make_user(T2), make_user(), justification="Cleared.")
        for _ in range(4):
            _post(env, make_user(), account, 50)
        assert account.state == "frozen" and account.approval_state == "none"


# ==========================================================================
# 6. IFRS 15 breakage (finance decision; mechanism only)
# ==========================================================================
class TestBreakage:
    def _row(self, env, program):
        pack = m10_api.points_liability(env)
        return next(r for r in pack["rows"] if r["program"] == program.name)

    def test_default_zero_is_todays_gross_liability(self, env, make_user, account):
        _post(env, make_user(), account, 400)
        row = self._row(env, account.program_id)
        assert row["gross_liability"] == row["liability"] == 200.0
        assert row["expected_breakage_pct"] == 0.0

    def test_a_breakage_rate_nets_the_liability(self, env, make_user, account):
        _post(env, make_user(), account, 400)
        with pytest.raises(UserError, match="Tier 3"):
            account.program_id.with_user(make_user()).write({"expected_breakage_pct": 20.0})
        account.program_id.with_user(make_user(T3)).write({"expected_breakage_pct": 20.0})
        row = self._row(env, account.program_id)
        assert (row["gross_liability"], row["liability"]) == (200.0, 160.0)
        with pytest.raises(ValidationError):
            account.program_id.write({"expected_breakage_pct": 120.0})


# ==========================================================================
# 7. party.merged moves loyalty to the survivor (M10-11)
# ==========================================================================
class TestPartyMerge:
    def _merge(self, env, victim, survivor):
        return publish(
            env,
            "party.merged",
            "res.partner",
            survivor.id,
            {"survivor_id": survivor.id, "victim_id": victim.id, "mandated_consumers": "all"},
        )

    def test_a_lone_victim_account_is_re_pointed(self, env, make_user, account):
        survivor = env["res.partner"].create({"name": "M10P2 Survivor"})
        _post(env, make_user(), account, 300)
        self._merge(env, account.partner_id, survivor)
        _relay(env)
        assert account.partner_id == survivor and account.points_balance == 300

    def test_two_accounts_merge_through_ledger_lines(self, env, make_user, program, account):
        clerk = make_user()
        survivor = env["res.partner"].create({"name": "M10P2 Survivor"})
        target = _account(env, program, survivor)
        _post(env, clerk, target, 100)
        old = _post(env, clerk, account, 300)
        old_expiry = date.today() + timedelta(days=40)
        old._guarded().write({"expiry_date": old_expiry})
        new = _post(env, clerk, account, 200)
        _post(env, clerk, account, -350, kind="redemption")  # leaves 150, all of `new`
        event_id = self._merge(env, account.partner_id, survivor)
        _relay(env)
        assert account.state == "closed" and account.points_balance == 0
        assert target.points_balance == 250
        debit = _lines(env, account, transaction_type="merge_transfer")
        credit = _lines(env, target, transaction_type="merge_transfer")
        assert (debit.points, debit.state) == (-150, "posted")
        assert (credit.points, credit.state, credit.expiry_date) == (150, "posted", new.expiry_date)
        assert "Party merge" in credit.notes
        # The victim's history is untouched.
        assert (old.points, old.state, new.points, new.state) == (300, "posted", 200, "posted")
        # The same event again changes nothing.
        env["fix.loyalty.account"].sudo().consume_party_merged(_event(env, event_id))
        assert len(_lines(env, target, transaction_type="merge_transfer")) == 1
        assert target.points_balance == 250

    def test_a_frozen_victims_points_are_not_moved(self, env, make_user, program, account):
        survivor = env["res.partner"].create({"name": "M10P2 Survivor"})
        target = _account(env, program, survivor)
        _post(env, make_user(), account, 300)
        account._guarded().write({"state": "frozen"})
        self._merge(env, account.partner_id, survivor)
        _relay(env)
        assert account.state == "frozen" and account.points_balance == 300
        assert target.points_balance == 0
        assert env["fix.event.outbox"].search_count(
            [
                ("event_type", "=", "loyalty.merge_transfer_blocked"),
                ("aggregate_id", "=", account.id),
            ]
        )


# ==========================================================================
# P03 surfaces: the new actions are whitelisted and have buttons
# ==========================================================================
def test_p03_offers_the_routed_release_and_reconcile():
    actions = m10_api.SURFACES["fix.loyalty.account"]["actions"]
    assert {
        "action_request_approval",
        "action_recall_approval",
        "action_reconcile_balance",
    } <= actions
    assert "action_unfreeze" not in actions  # the engine's apply method, never a button
