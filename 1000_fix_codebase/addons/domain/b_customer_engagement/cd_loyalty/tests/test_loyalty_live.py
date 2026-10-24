"""Behavioural tests for M10 loyalty: programme, tiers, ledger, vouchers,
campaign hooks and the M11/M20 redemption stub (live ORM, rolled back)."""

from contextlib import suppress
from datetime import date, timedelta

import pytest
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def program(env):
    program = env["fix.loyalty.program"].create(
        {"name": "LY Privilege", "code": "LYPRIV", "points_per_bdt": 0.01, "bdt_per_point": 0.5}
    )
    tiers = env["fix.loyalty.tier"]
    tiers.create({"program_id": program.id, "name": "Silver", "code": "SILVER", "sequence": 1})
    tiers.create(
        {
            "program_id": program.id,
            "name": "Gold",
            "code": "GOLD",
            "sequence": 2,
            "min_points_threshold": 1000,
            "min_spend_bdt": 50000.0,
            "points_multiplier": 1.5,
        }
    )
    return program


@pytest.fixture
def customer(env):
    return env["res.partner"].create({"name": "LY Member"})


def _account(env, program, partner, **vals):
    return env["fix.loyalty.account"].create(
        {"partner_id": partner.id, "program_id": program.id, **vals}
    )


def _post(env, account, points, **vals):
    line = env["fix.loyalty.ledger"].create(
        {
            "account_id": account.id,
            "transaction_type": vals.pop("kind", "accrual"),
            "points": points,
            **vals,
        }
    )
    line.action_post()
    return line


def _events(env, event_type, rec):
    return env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", rec.id)]
    )


# --- programme & tiers --------------------------------------------------------------


def test_programme_ratios_are_validated(env, program):
    with pytest.raises(ValidationError, match="cannot be negative"), env.cr.savepoint():
        program.points_per_bdt = -0.1
    with pytest.raises(ValidationError, match="strictly positive"), env.cr.savepoint():
        program.bdt_per_point = 0


def test_points_earned_follow_rate_and_tier_multiplier(env, program):
    gold = program.tier_ids.filtered(lambda t: t.code == "GOLD")
    assert program.calculate_points_earned(25000) == 250
    assert program.calculate_points_earned(25000, tier=gold) == 375
    assert program.calculate_points_earned(0) == 0
    program.active = False
    assert program.calculate_points_earned(25000) == 0


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("points_multiplier", 0.5, "at least 1.0x"),
        ("labour_discount_pct", 120.0, "Labour discount"),
        ("parts_discount_pct", -5.0, "Parts discount"),
    ],
)
def test_tier_benefits_are_bounded(env, program, field, value, message):
    with pytest.raises(ValidationError, match=message), env.cr.savepoint():
        program.tier_ids[0][field] = value


# --- accounts -----------------------------------------------------------------------


def test_new_account_starts_on_the_lowest_tier(env, program, customer):
    account = _account(env, program, customer)
    assert account.tier_id.code == "SILVER"
    assert program.account_count == 1
    assert '"tier": "SILVER"' in _events(env, "loyalty.account_created", account).payload
    bare = env["fix.loyalty.program"].create({"name": "LY Tierless", "code": "LYBARE"})
    tierless = _account(env, bare, customer)
    assert not tierless.tier_id
    assert '"tier": "NONE"' in _events(env, "loyalty.account_created", tierless).payload
    gold = program.tier_ids.filtered(lambda t: t.code == "GOLD")
    vip = _account(env, program, env["res.partner"].create({"name": "LY VIP"}), tier_id=gold.id)
    assert vip.tier_id == gold  # an explicit tier is kept


def test_membership_numbers_are_unique(env, program, customer):
    """Regression: with no ir.sequence every account was numbered "NEW"."""
    first = _account(env, program, customer)
    second = _account(env, program, env["res.partner"].create({"name": "LY Second"}))
    assert first.name != second.name
    assert first.name.startswith("LYL/")


def test_account_state_actions(env, program, customer):
    account = _account(env, program, customer)
    account.action_suspend()
    assert account.state == "suspended"
    account.action_activate()
    assert account.state == "active"
    account.action_close()
    assert account.state == "closed"


def test_tier_upgrades_on_points_or_spend(env, program, customer):
    by_points = _account(env, program, customer)
    _post(env, by_points, 1200)
    assert by_points.tier_id.code == "GOLD"
    assert by_points.tier_upgraded_date == date.today()
    upgrade = _events(env, "loyalty.tier_upgraded", by_points)
    assert '"old_tier": "Silver"' in upgrade.payload
    other = env["res.partner"].create({"name": "LY Big Spender"})
    by_spend = _account(env, program, other)
    _post(env, by_spend, 10, order_amount_bdt=60000.0)
    assert by_spend.tier_id.code == "GOLD"
    assert by_spend.lifetime_spend_bdt == 60000.0


def test_no_tier_change_without_a_qualifying_tier(env, customer):
    program = env["fix.loyalty.program"].create({"name": "LY Strict", "code": "LYSTRICT"})
    env["fix.loyalty.tier"].create(
        {
            "program_id": program.id,
            "name": "Elite",
            "code": "ELITE",
            "min_points_threshold": 5000,
            "min_spend_bdt": 1,
        }
    )
    account = _account(env, program, customer, tier_id=False)
    account.tier_id = False
    account.check_and_update_tier()  # neither threshold met
    assert not account.tier_id
    account.lifetime_points_earned = 5000
    account.check_and_update_tier()
    assert account.tier_id.code == "ELITE"
    assert '"old_tier": "None"' in _events(env, "loyalty.tier_upgraded", account).payload
    account.check_and_update_tier()  # already there: no second upgrade
    assert len(_events(env, "loyalty.tier_upgraded", account)) == 1


# --- ledger -------------------------------------------------------------------------


def test_accrual_sets_balance_lifetime_and_expiry(env, program, customer):
    account = _account(env, program, customer)
    line = _post(env, account, 300)
    assert (account.points_balance, account.lifetime_points_earned) == (300, 300)
    assert (line.state, line.balance_after) == ("posted", 300)
    assert line.expiry_date == date.today() + relativedelta(months=12)
    assert account.lifetime_spend_bdt == 0.0
    assert _events(env, "loyalty.points_accrued", line)
    fixed = _post(env, account, 5, expiry_date=date(2027, 1, 31))
    assert fixed.expiry_date == date(2027, 1, 31)
    program.expiry_months = 0
    forever = _post(env, account, 5)
    assert not forever.expiry_date


def test_redemption_and_zero_adjustment(env, program, customer):
    account = _account(env, program, customer)
    _post(env, account, 300)
    redeemed = _post(env, account, -120, kind="redemption")
    assert (account.points_balance, account.lifetime_points_redeemed) == (180, 120)
    assert '"service_order": false' in _events(env, "loyalty.points_redeemed", redeemed).payload
    noop = _post(env, account, 0, kind="adjustment")
    assert noop.balance_after == 180
    assert (account.lifetime_points_earned, account.lifetime_points_redeemed) == (300, 120)
    with pytest.raises(ValidationError, match="Insufficient points"), env.cr.savepoint():
        _post(env, account, -500, kind="redemption")


def test_posting_guards(env, program, customer):
    account = _account(env, program, customer)
    line = _post(env, account, 10)
    with pytest.raises(UserError, match="Only draft transactions"), env.cr.savepoint():
        line.action_post()
    account.action_suspend()
    with pytest.raises(UserError, match="is suspended"), env.cr.savepoint():
        _post(env, account, 10)


# --- campaign hooks -----------------------------------------------------------------


@pytest.fixture
def campaign(env):
    return env["fix.campaign"].create({"name": "LY Monsoon Care"})


def _hook(env, campaign, program, **vals):
    return env["fix.loyalty.campaign.hook"].create(
        {"name": "LY hook", "campaign_id": campaign.id, "program_id": program.id, **vals}
    )


def test_hooks_disburse_only_when_active(env, program, campaign, customer):
    hook = _hook(env, campaign, program, bonus_points=200)
    with pytest.raises(UserError, match="Only active"), env.cr.savepoint():
        hook.action_execute_campaign_rewards(customer)
    hook.action_activate()
    existing = _account(env, program, customer)
    newcomer = env["res.partner"].create({"name": "LY Newcomer"})
    assert hook.action_execute_campaign_rewards(customer | newcomer) == 2
    assert existing.points_balance == 200
    enrolled = env["fix.loyalty.account"].search([("partner_id", "=", newcomer.id)])
    assert enrolled.points_balance == 200
    assert enrolled.ledger_ids.transaction_type == "campaign_bonus"
    assert '"rewarded_count": 2' in _events(env, "loyalty.campaign_rewards_disbursed", hook).payload


def test_voucher_hooks_and_empty_bonus_hooks(env, program, campaign, customer):
    voucher_hook = _hook(
        env,
        campaign,
        program,
        reward_type="voucher",
        voucher_discount_type="percentage",
        voucher_discount_value=10.0,
        voucher_validity_days=7,
    )
    voucher_hook.action_activate()
    assert voucher_hook.action_execute_campaign_rewards(customer) == 1
    voucher = env["fix.loyalty.voucher"].search([("partner_id", "=", customer.id)])
    assert (voucher.discount_type, voucher.valid_until) == (
        "percentage",
        date.today() + timedelta(days=7),
    )
    zero = _hook(env, campaign, program, bonus_points=0)
    zero.action_activate()
    assert zero.action_execute_campaign_rewards(customer) == 0


# --- vouchers -----------------------------------------------------------------------


def _voucher(env, customer, **vals):
    vals.setdefault("discount_value", 200.0)
    vals.setdefault("valid_until", date.today() + timedelta(days=30))
    return env["fix.loyalty.voucher"].create({"partner_id": customer.id, **vals})


@pytest.mark.parametrize(
    ("vals", "message"),
    [
        ({"discount_value": 0.0}, "greater than zero"),
        ({"discount_type": "percentage", "discount_value": 150.0}, "cannot exceed 100%"),
        ({"valid_until": date.today() - timedelta(days=1)}, "inverted"),
    ],
)
def test_voucher_parameters_are_validated(env, customer, vals, message):
    with pytest.raises(ValidationError, match=message), env.cr.savepoint():
        _voucher(env, customer, **vals)


def test_voucher_lifecycle(env, customer):
    voucher = _voucher(env, customer)
    assert voucher.name.startswith("VCH-")
    order = env["fix.service.order"].browse()  # redemption needs only the order id
    with pytest.raises(UserError, match="cannot be redeemed"), env.cr.savepoint():
        voucher.action_redeem(order)
    voucher.action_activate()
    with pytest.raises(UserError, match="Only draft vouchers"), env.cr.savepoint():
        voucher.action_activate()
    voucher.action_redeem(order)
    assert voucher.state == "redeemed"
    assert voucher.redeemed_at
    assert _events(env, "loyalty.voucher_redeemed", voucher)
    with pytest.raises(UserError, match="already-redeemed"), env.cr.savepoint():
        voucher.action_cancel()
    spare = _voucher(env, customer)
    spare.action_cancel()
    assert spare.state == "cancelled"


def test_a_voucher_is_redeemable_only_inside_its_window(env, customer):
    """Regression: a redemption attempt BEFORE the window opened marked a
    future voucher 'expired' for good."""
    order = env["fix.service.order"].browse()
    future = _voucher(
        env,
        customer,
        valid_from=date.today() + timedelta(days=2),
        valid_until=date.today() + timedelta(days=9),
    )
    lapsed = _voucher(
        env,
        customer,
        valid_from=date.today() - timedelta(days=9),
        valid_until=date.today() - timedelta(days=2),
    )
    (future | lapsed).action_activate()
    with pytest.raises(UserError, match="outside its validity window"), env.cr.savepoint():
        future.action_redeem(order)
    with pytest.raises(UserError, match="outside its validity window"), env.cr.savepoint():
        lapsed.action_redeem(order)
    assert (future.state, lapsed.state) == ("active", "active")  # a refusal changes nothing
    # a caller that handles the refusal (no rollback) keeps the expiry of the lapsed one
    for voucher in (future, lapsed):
        with suppress(UserError):  # a refusal raised in Python: the transaction stays usable
            voucher.action_redeem(order)
    assert (future.state, lapsed.state) == ("active", "expired")


# --- the M11/M20 redemption stub ----------------------------------------------------


def test_redemption_eligibility(env, program, customer):
    stub = env["fix.loyalty.redemption.stub"]
    nobody = stub.check_redemption_eligibility(customer.id, None, 100)
    assert nobody["eligible"] is False and "no active loyalty account" in nobody["reason"]
    account = _account(env, program, customer)
    _post(env, account, 150)
    too_few = stub.check_redemption_eligibility(customer.id, None, 50)
    too_many = stub.check_redemption_eligibility(customer.id, None, 400)
    ok = stub.check_redemption_eligibility(customer.id, None, 120)
    assert "Minimum points required" in too_few["reason"]
    assert "Insufficient balance" in too_many["reason"]
    assert (ok["eligible"], ok["discount_bdt"], ok["tier"]) == (True, 60.0, "Silver")
    account.tier_id = False
    assert stub.check_redemption_eligibility(customer.id, None, 120)["tier"] == "Standard"


def _invoice(env, customer, amount=1000.0, **vals):
    invoice = env["fix.ar.invoice"].create(
        {
            "operating_unit_id": env["operating.unit"].search([], limit=1).id,
            "customer_id": customer.id,
            "source_model": "fix.service.order",
            "source_id": env["fix.ar.invoice"].search_count([]) + 900000,
            **vals,
        }
    )
    env["fix.ar.invoice.line"].create(
        {"invoice_id": invoice.id, "description": "Repair", "taxable_amount": amount}
    )
    return invoice


def test_eligibility_never_claims_a_redemption(env, program, customer):
    account = _account(env, program, customer)
    _post(env, account, 300)
    res = env["fix.loyalty.redemption.stub"].check_redemption_eligibility(customer.id, None, 120)
    assert "stub_active" not in res
    assert res["redemption_mode"] == "invoice_offset"
    assert account.points_balance == 300  # a check deducts nothing


def test_execute_redemption_posts_the_ledger_and_offsets_the_invoice(env, program, customer):
    stub_model = env["fix.loyalty.redemption.stub"]
    account = _account(env, program, customer)
    _post(env, account, 500)
    with pytest.raises(UserError, match="Minimum points"), env.cr.savepoint():
        stub_model.execute_redemption(customer.id, points_to_redeem=10)
    stub = stub_model.create({})
    invoice = _invoice(env, customer)
    res = stub_model.execute_redemption(customer.id, invoice_id=invoice.id, points_to_redeem=200)
    assert (res["status"], res["discount_bdt"], res["account_balance_after"]) == (
        "closed",
        100.0,
        300,
    )
    assert (invoice.loyalty_points_redeemed, invoice.loyalty_discount_amount) == (200, 100.0)
    assert invoice.total_payable == res["invoice_total_payable"] == 900.0
    assert stub.status == "closed"
    ledger = env["fix.loyalty.ledger"].browse(res["ledger_id"])
    assert (ledger.points, ledger.transaction_type, ledger.state) == (-200, "redemption", "posted")
    assert invoice.display_name in ledger.notes


def test_redemption_without_a_valid_invoice_deducts_nothing(env, program, customer):
    stub_model = env["fix.loyalty.redemption.stub"]
    account = _account(env, program, customer)
    _post(env, account, 500)
    stranger = env["res.partner"].create({"name": "LOY Stranger"})
    issued = _invoice(env, customer)
    issued.state = "issued"
    used = _invoice(env, customer, loyalty_points_redeemed=100, loyalty_discount_amount=50.0)
    cases = [
        (None, "no invoice was given"),
        (999999999, "does not exist"),
        (_invoice(env, stranger).id, "another customer"),
        (issued.id, "DRAFT invoice only"),
        (used.id, "already carries a loyalty redemption"),
        (_invoice(env, customer, amount=50.0).id, "exceeds invoice"),
    ]
    for invoice_id, message in cases:
        with pytest.raises(UserError, match=message), env.cr.savepoint():
            stub_model.execute_redemption(customer.id, invoice_id=invoice_id, points_to_redeem=200)
    assert account.points_balance == 500  # never deducted without the discount landing
    assert not env["fix.loyalty.ledger"].search(
        [("account_id", "=", account.id), ("transaction_type", "=", "redemption")]
    )
