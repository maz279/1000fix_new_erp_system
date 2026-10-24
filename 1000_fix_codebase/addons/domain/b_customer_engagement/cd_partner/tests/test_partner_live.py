"""Behavioural tests for M40 partners/referrals and the P12 partner API (live ORM).

``odoo_env`` (fix_test, rolled back per test). The API runs with
``odoo.http.request`` replaced by a stand-in carrying the caller's ``env``, so
the P12 portal group's ACLs and record rules apply exactly as in production.
"""

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo import Command
from odoo.addons.cd_partner.controllers import partner_api
from odoo.addons.cd_partner.controllers.partner_api import PartnerApiController
from odoo.exceptions import UserError, ValidationError


@contextmanager
def _as(env, user):
    with patch.object(partner_api, "request", SimpleNamespace(env=env(user=user.id))):
        yield PartnerApiController()


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    group = env.ref("cd_partner.group_fix_partner_portal")
    users = env["res.users"].with_context(no_reset_password=True)
    rafi = users.create(
        {"name": "Rafi Referrals", "login": "rafi@p12.test", "group_ids": [Command.set([group.id])]}
    )
    nadia = users.create(
        {
            "name": "Nadia Reseller",
            "login": "nadia@p12.test",
            "group_ids": [Command.set([group.id])],
        }
    )
    newcomer = users.create(
        {"name": "Not Onboarded", "login": "new@p12.test", "group_ids": [Command.set([group.id])]}
    )
    staff = users.create({"name": "Partnerships Staff", "login": "staff@p12.test"})
    profiles = env["fix.partner"]
    rafi_profile = profiles.create(
        {"name": "Rafi Electronics", "partner_id": rafi.partner_id.id, "territory": "Mirpur"}
    )
    nadia_profile = profiles.create(
        {"name": "Nadia Mobiles", "partner_id": nadia.partner_id.id, "partner_type": "reseller"}
    )
    customer = env["res.partner"].create({"name": "Referred Customer One"})
    return SimpleNamespace(
        env=env,
        rafi=rafi,
        nadia=nadia,
        newcomer=newcomer,
        staff=staff,
        rafi_profile=rafi_profile,
        nadia_profile=nadia_profile,
        customer=customer,
    )


def _referral(world, profile, name, state="submitted", commission=0.0):
    return world.env["fix.referral"].create(
        {
            "partner_id": profile.id,
            "name": name,
            "referred_partner_id": world.customer.id,
            "state": state,
            "commission_amount": commission,
        }
    )


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (1.999, "2.00"),
        (-1234.5, "-1,234.50"),
        (500, "500.00"),
        (2500000, "25,00,000.00"),
        (None, "0.00"),
    ],
)
def test_amounts_are_south_asian_grouped(amount, expected):
    assert partner_api._fmt_bdt(amount) == expected


# --- models -------------------------------------------------------------------------


def test_partner_onboarding_and_referral_commission_lifecycle(world):
    env = world.env
    world.rafi_profile.action_onboard()
    referral = _referral(world, world.rafi_profile, "REF-LIFE-1")
    with pytest.raises(UserError, match="Convert before commissioning"), world.env.cr.savepoint():
        referral.action_earn_commission()
    referral.action_convert()
    with pytest.raises(UserError, match="commission base is required"), world.env.cr.savepoint():
        referral.action_earn_commission()  # no flat, invented amount
    referral.base_amount = 12000.0
    world.rafi_profile.commission_rate = 0.075
    referral.action_earn_commission()
    assert world.rafi_profile.state == "onboarded"
    # rate x base: 7.5% of 12,000
    assert (referral.state, referral.commission_amount) == ("commissioned", 900.0)
    [earned] = env["fix.event.outbox"].search(
        [("event_type", "=", "commission.earned"), ("aggregate_id", "=", referral.id)]
    )
    assert '"gross": 12000.0' in earned.payload and '"commission": 900.0' in earned.payload
    events = env["fix.event.outbox"].search(
        [
            ("event_type", "in", ("partner.onboarded", "referral.converted", "commission.earned")),
            ("aggregate_id", "in", (world.rafi_profile.id, referral.id)),
        ]
    )
    assert sorted(events.mapped("event_type")) == [
        "commission.earned",
        "partner.onboarded",
        "referral.converted",
    ]


def test_commission_needs_a_valid_rate_and_one_conversion(world):
    referral = _referral(world, world.rafi_profile, "REF-RATE-1")
    referral.action_convert(base_amount=4000.0)
    assert referral.base_amount == 4000.0
    with pytest.raises(UserError, match="submitted referral"), world.env.cr.savepoint():
        referral.action_convert()
    world.rafi_profile.commission_rate = 0.0
    with pytest.raises(UserError, match="no valid commission rate"), world.env.cr.savepoint():
        referral.action_earn_commission()
    world.rafi_profile.commission_rate = 0.05
    referral.action_earn_commission()
    assert referral.commission_amount == 200.0


# --- the P12 API --------------------------------------------------------------------


def test_profile_is_the_callers_own(world):
    with _as(world.env, world.rafi) as ctrl:
        own = ctrl.profile()
        foreign = ctrl.profile(partner_profile_id=world.nadia_profile.id)
        explicit_own = ctrl.profile(partner_profile_id=world.rafi_profile.id)
        junk = ctrl.profile(partner_profile_id="nadia")
    with _as(world.env, world.newcomer) as ctrl:
        nobody = ctrl.profile()
    assert own["partner"] == {
        "id": world.rafi_profile.id,
        "name": "Rafi Electronics",
        "partner_type": "referral",
        "territory": "Mirpur",
        "commission_rate": 0.05,
        "state": "prospective",
    }
    assert explicit_own["partner"]["id"] == world.rafi_profile.id
    for res in (foreign, junk, nobody):
        assert res["error"]["code"] == "no_partner_profile"


def test_internal_staff_may_open_any_profile(world):
    with _as(world.env, world.staff) as ctrl:
        res = ctrl.profile(partner_profile_id=world.nadia_profile.id)
        commissions = ctrl.commissions(partner_profile_id=world.nadia_profile.id)
    assert res["partner"]["name"] == "Nadia Mobiles"
    assert commissions["commissions"]["earned_total_bdt"] == "0.00"


def test_referral_tracking_shows_the_referred_party_to_the_portal_partner(world):
    """Regression: the referred customer's name was read under the portal
    partner rule, which hides other customers' partner rows - AccessError."""
    _referral(world, world.rafi_profile, "REF-TRACK-1")
    _referral(world, world.nadia_profile, "REF-NADIA-1")
    with _as(world.env, world.rafi) as ctrl:
        res = ctrl.referrals()
    assert [(r["name"], r["referred"], r["state"]) for r in res["referrals"]] == [
        ("REF-TRACK-1", "Referred Customer One", "submitted")
    ]


def test_referral_submission(world):
    with _as(world.env, world.rafi) as ctrl:
        missing = ctrl.referrals(referred_name="Walk-in friend")
        unknown = ctrl.referrals(referred_name="Ghost", referred_partner_id=999999999)
        junk = ctrl.referrals(referred_name="Ghost", referred_partner_id="abc")
        created = ctrl.referrals(referred_name="REF-NEW-1", referred_partner_id=world.customer.id)
    assert missing["error"]["code"] == "missing_referred"
    assert unknown["error"]["code"] == "no_referred_party"
    assert junk["error"]["code"] == "no_referred_party"
    referral = world.env["fix.referral"].browse(created["referral"]["id"])
    assert created["referral"]["state"] == "submitted"
    assert (referral.partner_id, referral.referred_partner_id) == (
        world.rafi_profile,
        world.customer,
    )


def test_a_refused_referral_leaves_no_row(world):
    referrals = type(world.env["fix.referral"])
    original_create = referrals.create

    def create_then_refuse(self, vals_list):
        original_create(self, vals_list)
        raise ValidationError("duplicate referral")

    with patch.object(referrals, "create", create_then_refuse), _as(world.env, world.rafi) as ctrl:
        res = ctrl.referrals(referred_name="REF-DUP", referred_partner_id=world.customer.id)
    assert res["error"] == {"code": "referral_rejected", "message": "duplicate referral"}
    assert not world.env["fix.referral"].search([("name", "=", "REF-DUP")])


def test_commission_statement(world):
    _referral(world, world.rafi_profile, "REF-C-1", state="commissioned", commission=500.0)
    _referral(world, world.rafi_profile, "REF-C-2", state="commissioned", commission=1250.5)
    _referral(world, world.rafi_profile, "REF-C-3")
    with _as(world.env, world.rafi) as ctrl:
        res = ctrl.commissions()["commissions"]
    assert [line["referral"] for line in res["lines"]] == ["REF-C-2", "REF-C-1"]
    assert res["lines"][0]["commission_bdt"] == "1,250.50"
    assert res["lines"][0]["referred"] == "Referred Customer One"
    assert res["earned_total_bdt"] == "1,750.50"


def test_no_profile_no_referrals_or_commissions(world):
    with _as(world.env, world.newcomer) as ctrl:
        referrals = ctrl.referrals()
        commissions = ctrl.commissions()
    assert referrals["error"]["code"] == "no_partner_profile"
    assert commissions["error"]["code"] == "no_partner_profile"
