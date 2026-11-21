"""M40 co-marketing: the partner <-> campaign link and the MDF -> campaign key.

The M40-comarketing report was a declared gap because neither link existed:
fix.campaign carried no fix.partner key and an MDF accrual
(fix.partner.rebate, kind 'mdf') no campaign key. These tests drive the two
links as the roles that would use them: a channel officer names the
co-marketing partners of a campaign and ties an MDF accrual to one, a plain
clerk does neither, and an MDF cannot point at a campaign its partner does
not co-fund or be re-pointed once it is accrued.
"""

import types
from contextlib import contextmanager
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.addons.cd_partner.tests.m40_fixtures import paid_invoice

TODAY = None
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
OFFICER = "cd_partner.group_fix_channel_officer"


def _user(env, login, *xmlids):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    Command.set([env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids])
                ],
            }
        )
    )


@pytest.fixture
def cm(odoo_env):
    env = odoo_env
    if "fix.campaign" not in env:
        pytest.skip("cd_campaign not installed")
    global TODAY
    TODAY = fields.Date.context_today(env.user)
    x = types.SimpleNamespace(env=env)
    x.clerk = _user(env, "cm_clerk")
    x.officer = _user(env, "cm_officer", OFFICER)

    def partner(name, onboarded=True):
        rec = env["fix.partner"].create(
            {
                "name": name,
                "partner_id": env["res.partner"].create({"name": name}).id,
                "partner_type": "alliance",
                "tin_number": "123456789012",
                "trade_license_no": "TL-CM",
            }
        )
        if onboarded:  # seed-style, as the trusted superuser
            rec.write({"state": "onboarded"})
        return rec

    x.partner = partner
    x.p1 = partner("CM Alliance One")
    x.p2 = partner("CM Alliance Two")
    x.campaign = env["fix.campaign"].create({"name": "CM Monsoon Co-Promo", "channel": "social"})
    x.other = env["fix.campaign"].create({"name": "CM Eid Push", "channel": "sms"})

    def mdf(partner_rec, campaign=None, kind="mdf", **kw):
        vals = {
            "name": "CM MDF",
            "partner_id": partner_rec.id,
            "period": "2026-Q4",
            # A04 ERP audit M40-F12: the basis is computed from paid invoices
            "period_from": TODAY - timedelta(days=30),
            "period_to": TODAY,
            "rate": 0.05,
            "kind": kind,
            **kw,
        }
        if campaign is not None:
            vals["campaign_id"] = campaign.id
        return env["fix.partner.rebate"].with_user(x.officer).create(vals)

    x.mdf = mdf
    return x


@contextmanager
def _refused(env, exc=REFUSED, match=None):
    """Expect ``exc``; the failed operation is rolled back (flushing savepoint)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


def test_the_campaign_names_its_co_marketing_partners(cm):
    camp = cm.campaign.with_user(cm.officer)
    camp.write({"partner_ids": [Command.link(cm.p1.id), Command.link(cm.p2.id)]})
    assert cm.campaign.partner_ids == cm.p1 | cm.p2
    # the same link read from the partner side
    assert cm.campaign in cm.p1.comarketing_campaign_ids
    field = cm.env["fix.campaign"]._fields["partner_ids"]
    assert field.type == "many2many" and field.comodel_name == "fix.partner"


def test_only_a_channel_officer_names_co_marketing_partners(cm):
    with _refused(cm.env, UserError, "Channel Officer"):
        cm.campaign.with_user(cm.clerk).write({"partner_ids": [Command.link(cm.p1.id)]})
    assert not cm.campaign.partner_ids
    # a clerk may still edit the campaign's own fields
    cm.campaign.with_user(cm.clerk).write({"name_bn": "মনসুন"})


def test_only_an_onboarded_partner_co_markets(cm):
    prospect = cm.partner("CM Prospect", onboarded=False)
    with _refused(cm.env, ValidationError, "onboarded"):
        cm.campaign.with_user(cm.officer).write({"partner_ids": [Command.link(prospect.id)]})


def test_the_partner_side_is_maintained_by_the_officer_too(cm):
    cm.p1.with_user(cm.officer).write({"comarketing_campaign_ids": [Command.link(cm.other.id)]})
    assert cm.p1 in cm.other.partner_ids
    with _refused(cm.env):
        cm.p2.with_user(cm.clerk).write({"comarketing_campaign_ids": [Command.link(cm.other.id)]})


def test_an_mdf_accrual_carries_its_campaign(cm):
    cm.campaign.write({"partner_ids": [Command.link(cm.p1.id)]})
    rec = cm.mdf(cm.p1, cm.campaign)
    assert rec.campaign_id == cm.campaign
    field = cm.env["fix.partner.rebate"]._fields["campaign_id"]
    assert field.comodel_name == "fix.campaign" and not field.required


def test_a_volume_rebate_carries_no_campaign(cm):
    cm.campaign.write({"partner_ids": [Command.link(cm.p1.id)]})
    with _refused(cm.env, ValidationError, "market development fund"):
        cm.mdf(cm.p1, cm.campaign, kind="rebate")
    # an MDF without a campaign is still allowed (the key is optional)
    assert cm.mdf(cm.p1).campaign_id.id is False


def test_an_mdf_points_only_at_a_campaign_its_partner_co_funds(cm):
    cm.campaign.write({"partner_ids": [Command.link(cm.p1.id)]})
    with _refused(cm.env, ValidationError, "co-marketing partner"):
        cm.mdf(cm.p2, cm.campaign)


def test_the_campaign_is_pinned_once_the_mdf_is_accrued(cm):
    cm.campaign.write({"partner_ids": [Command.link(cm.p1.id)]})
    cm.other.write({"partner_ids": [Command.link(cm.p1.id)]})
    rec = cm.mdf(cm.p1, cm.campaign)
    rec.with_user(cm.officer).write({"campaign_id": cm.other.id})  # draft: still editable
    paid_invoice(cm.env, cm.p1.partner_id, 100000.0, TODAY - timedelta(days=5))  # set-up
    rec.with_user(cm.officer).action_accrue()
    assert rec.state == "accrued"
    with _refused(cm.env, UserError):
        rec.with_user(cm.officer).write({"campaign_id": cm.campaign.id})
    assert rec.campaign_id == cm.other
    assert "campaign_id" in rec._fix_form_locked_fields()


def test_a_partner_with_live_mdf_stays_on_the_campaign(cm):
    cm.campaign.write({"partner_ids": [Command.link(cm.p1.id), Command.link(cm.p2.id)]})
    rec = cm.mdf(cm.p1, cm.campaign)
    with _refused(cm.env, ValidationError, "MDF"):
        cm.campaign.with_user(cm.officer).write({"partner_ids": [Command.unlink(cm.p1.id)]})
    with _refused(cm.env, ValidationError, "MDF"):
        cm.p1.with_user(cm.officer).write(
            {"comarketing_campaign_ids": [Command.unlink(cm.campaign.id)]}
        )
    # a partner with no MDF on the campaign leaves freely
    cm.campaign.with_user(cm.officer).write({"partner_ids": [Command.unlink(cm.p2.id)]})
    # once the MDF is cancelled the link may go
    rec.with_user(cm.officer).action_cancel()
    cm.campaign.with_user(cm.officer).write({"partner_ids": [Command.unlink(cm.p1.id)]})
    assert not cm.campaign.partner_ids
