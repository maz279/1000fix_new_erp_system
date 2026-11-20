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
from odoo.addons.cd_partner.tests.m40_fixtures import make_onboardable
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
        {
            "name": "Nadia Mobiles",
            "partner_id": nadia.partner_id.id,
            "partner_type": "reseller",
            # a reseller onboards on its statutory identifiers (FLAW-33.1)
            "tin_number": "123456789012",
            "trade_license_no": "TL-NADIA",
        }
    )
    # A04 ERP audit M40-F9/F11: only an onboarded partner refers; onboarding
    # needs programme, agreement and checklist (set-up here, as the system)
    for profile in (rafi_profile, nadia_profile):
        make_onboardable(env, profile)
        profile.action_onboard()
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


def _referral(world, profile, name, state="submitted", commission=0.0, referred=None):
    # A04 hand-off closure, ref_02: one OPEN referral per customer and one
    # commission per (partner, customer) — staging uses a distinct customer
    # per referral unless a test says otherwise.
    referred = referred or world.env["res.partner"].create({"name": "Referred %s" % name})
    return world.env["fix.referral"].create(
        {
            "partner_id": profile.id,
            "name": name,
            "referred_partner_id": referred.id,
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
        # A04 ERP audit M40-F5/F11: no rate until approved; onboarded in set-up
        "commission_rate": 0.0,
        "state": "onboarded",
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


# --- A04 hand-off closure: duplicate / self-referral gate (ref_02) ----------


def test_a_partner_cannot_refer_themselves(world):
    """AS-09, now enforced: the referring partner's own res.partner is not a
    valid referred customer."""
    with pytest.raises(UserError, match="cannot refer themselves"), world.env.cr.savepoint():
        world.env["fix.referral"].create(
            {
                "partner_id": world.rafi_profile.id,
                "name": "REF-SELF",
                "referred_partner_id": world.rafi.partner_id.id,
            }
        )


def test_one_open_referral_per_customer_first_in_wins(world):
    Referral = world.env["fix.referral"]
    Referral.create(
        {
            "partner_id": world.rafi_profile.id,
            "name": "REF-FIRST",
            "referred_partner_id": world.customer.id,
        }
    )
    # a second partner piling on the same customer
    with pytest.raises(UserError, match="already has an open referral"), world.env.cr.savepoint():
        Referral.create(
            {
                "partner_id": world.nadia_profile.id,
                "name": "REF-SECOND",
                "referred_partner_id": world.customer.id,
            }
        )
    # the same partner doubling their own submitted referral
    with pytest.raises(UserError, match="already has an open referral"), world.env.cr.savepoint():
        Referral.create(
            {
                "partner_id": world.rafi_profile.id,
                "name": "REF-SECOND-OWN",
                "referred_partner_id": world.customer.id,
            }
        )


def test_one_commission_per_partner_and_customer_ever(world):
    """A commissioned referral cannot be repeated on the same customer by the
    same partner — the second commission is double pay (M40 ref_02)."""
    Referral = world.env["fix.referral"]
    Referral.create(
        {
            "partner_id": world.rafi_profile.id,
            "name": "REF-PAID",
            "referred_partner_id": world.customer.id,
            "state": "commissioned",
            "commission_amount": 500.0,
        }
    )
    with pytest.raises(UserError, match="one commission per customer"), world.env.cr.savepoint():
        Referral.create(
            {
                "partner_id": world.rafi_profile.id,
                "name": "REF-AGAIN",
                "referred_partner_id": world.customer.id,
            }
        )
    # a different customer is fine
    other = world.env["res.partner"].create({"name": "Referred Customer Next"})
    assert Referral.create(
        {
            "partner_id": world.rafi_profile.id,
            "name": "REF-OK",
            "referred_partner_id": other.id,
        }
    )


def test_repointing_an_existing_referral_reruns_the_gate(world):
    """write() on the attribution pair hits the same duplicate/self gate."""
    Referral = world.env["fix.referral"]
    ref = Referral.create(
        {
            "partner_id": world.rafi_profile.id,
            "name": "REF-REPOINT",
            "referred_partner_id": world.customer.id,
        }
    )
    other = world.env["res.partner"].create({"name": "Referred Customer Two"})
    ref.write({"referred_partner_id": other.id})  # to a free customer: allowed
    with pytest.raises(UserError, match="cannot refer themselves"), world.env.cr.savepoint():
        ref.write({"referred_partner_id": world.rafi.partner_id.id})


CONSENTED = {"consent_given": True, "consent_method": "digital"}


def test_the_portal_submits_through_the_gate(world):
    """A04 ERP audit M40-F8: the P12 partner submits a consented LEAD. It no
    longer names (and so reserves) an existing customer: a party id is
    refused, and two partners naming the same person both reach the company,
    which links the customer and attributes at conversion."""
    with _as(world.env, world.rafi) as ctrl:
        squat = ctrl.referrals(referred_name="REF-P1", referred_partner_id=world.customer.id)
        first = ctrl.referrals(referred_name="Karim", referred_phone="01711000001", **CONSENTED)
    assert squat["error"]["code"] == "referred_party_not_accepted"
    assert "Referred Customer One" not in str(squat)
    assert first["lead"]["state"] == "submitted"
    with _as(world.env, world.nadia) as ctrl:
        second = ctrl.referrals(referred_name="Karim", referred_phone="01711000001", **CONSENTED)
    assert second["lead"]["state"] == "submitted"


def test_referral_tracking_shows_the_referred_party_to_the_portal_partner(world):
    """Regression: the referral listing read the referred party under the
    portal partner rule (AccessError). A04 ERP audit M40-F8: it now shows what
    the partner itself typed on its lead, never the party master's name."""
    _referral(world, world.rafi_profile, "REF-TRACK-1", referred=world.customer)
    _referral(world, world.nadia_profile, "REF-NADIA-1")
    with _as(world.env, world.rafi) as ctrl:
        ctrl.referrals(referred_name="Karim", referred_phone="01711000002", **CONSENTED)
        res = ctrl.referrals()
    assert [(r["name"], r["referred"], r["state"]) for r in res["referrals"]] == [
        ("REF-TRACK-1", "", "submitted")
    ]
    assert [(lead["referred"], lead["state"]) for lead in res["leads"]] == [("Karim", "submitted")]
    assert "Referred Customer One" not in str(res)


def test_referral_submission(world):
    with _as(world.env, world.rafi) as ctrl:
        no_phone = ctrl.referrals(referred_name="Walk-in friend", **CONSENTED)
        no_consent = ctrl.referrals(referred_name="Walk-in friend", referred_phone="0171")
        party = ctrl.referrals(referred_name="Ghost", referred_partner_id=999999999)
        created = ctrl.referrals(
            referred_name="Walk-in friend", referred_phone="01711000003", **CONSENTED
        )
    assert no_phone["error"]["code"] == "missing_phone"
    assert no_consent["error"]["code"] == "missing_consent"
    assert party["error"]["code"] == "referred_party_not_accepted"
    lead = world.env["fix.partner.lead"].search([("name", "=", created["lead"]["name"])])
    assert (lead.partner_id, lead.customer_name, lead.consent_method) == (
        world.rafi_profile,
        "Walk-in friend",
        "digital",
    )


def test_a_refused_referral_leaves_no_row(world):
    leads = type(world.env["fix.partner.lead"])
    original_create = leads.create

    def create_then_refuse(self, vals_list):
        original_create(self, vals_list)
        raise ValidationError("duplicate referral")

    with patch.object(leads, "create", create_then_refuse), _as(world.env, world.rafi) as ctrl:
        res = ctrl.referrals(referred_name="REF-DUP", referred_phone="0171", **CONSENTED)
    assert res["error"] == {"code": "referral_rejected", "message": "duplicate referral"}
    assert not world.env["fix.partner.lead"].search([("customer_name", "=", "REF-DUP")])


def test_commission_statement(world):
    # one commission per (partner, customer): each referral names a distinct
    # customer (ref_02); the newest line's customer is the tracked one
    _referral(world, world.rafi_profile, "REF-C-1", state="commissioned", commission=500.0)
    _referral(
        world,
        world.rafi_profile,
        "REF-C-2",
        state="commissioned",
        commission=1250.5,
        referred=world.customer,
    )
    _referral(world, world.rafi_profile, "REF-C-3")
    with _as(world.env, world.rafi) as ctrl:
        res = ctrl.commissions()["commissions"]
    assert [line["referral"] for line in res["lines"]] == ["REF-C-2", "REF-C-1"]
    assert res["lines"][0]["commission_bdt"] == "1,250.50"
    # A04 ERP audit M40-F8: the party master's name is never echoed
    assert "Referred Customer One" not in str(res)
    assert res["earned_total_bdt"] == "1,750.50"


def test_no_profile_no_referrals_or_commissions(world):
    with _as(world.env, world.newcomer) as ctrl:
        referrals = ctrl.referrals()
        commissions = ctrl.commissions()
    assert referrals["error"]["code"] == "no_partner_profile"
    assert commissions["error"]["code"] == "no_partner_profile"
