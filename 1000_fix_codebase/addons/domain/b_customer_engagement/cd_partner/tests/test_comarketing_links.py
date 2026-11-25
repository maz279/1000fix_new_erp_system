"""M40 co-marketing: the partner <-> campaign link and the MDF -> campaign key.

The M40-comarketing report was a declared gap because neither link existed:
fix.campaign carried no fix.partner key and an MDF accrual no campaign key.
These tests drive the two links as the roles that would use them: a channel
officer names the co-marketing partners of a campaign and ties an MDF claim
to one, a plain clerk does neither, and an MDF claim cannot point at a
campaign its partner does not co-fund or be re-pointed once it is submitted.

A04 ERP audit M40-F26 (21 Nov 2026): one MDF mechanism. The MDF is a claim
on the partner's MDF fund (fix.mdf.claim, campaign_id); a rebate of kind
'mdf' is refused with a pointer there.
"""

import base64
import types
from contextlib import contextmanager
from datetime import timedelta

import pytest
from odoo import Command, fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
OFFICER = "cd_partner.group_fix_channel_officer"
MANAGER = "cd_partner.group_fix_channel_manager"


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
    x = types.SimpleNamespace(env=env, today=fields.Date.context_today(env.user))
    x.clerk = _user(env, "cm_clerk")
    x.officer = _user(env, "cm_officer", OFFICER)
    x.manager = _user(env, "cm_manager", MANAGER)
    x.manager2 = _user(env, "cm_manager2", MANAGER)

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

    def fund(partner_rec):
        rec = (
            env["fix.mdf.fund"]
            .with_user(x.officer)
            .create(
                {
                    "name": "CM fund",
                    "partner_id": partner_rec.id,
                    "period": "2026-Q4",
                    "allocated": 100000.0,
                }
            )
        )
        rec.with_user(x.manager).action_open()
        return rec

    def claim(partner_rec, campaign=None, **kw):
        vals = {
            "fund_id": fund(partner_rec).id,
            "amount": 20000.0,
            "description": "CM co-promo stall",
            **kw,
        }
        if campaign is not None:
            vals["campaign_id"] = campaign.id
        return env["fix.mdf.claim"].with_user(x.officer).create(vals)

    def evidence(rec):
        att = (
            env["ir.attachment"]
            .with_user(x.officer)
            .create(
                {
                    "name": "proof.pdf",
                    "res_model": rec._name,
                    "res_id": rec.id,
                    "datas": base64.b64encode(b"%PDF-1.4 cm"),
                }
            )
        )
        rec.with_user(x.officer).write({"evidence_attachment_id": att.id})

    def rebate(partner_rec, campaign=None, kind="rebate"):
        vals = {
            "name": "CM rebate",
            "partner_id": partner_rec.id,
            "period": "2026-Q4",
            "period_from": x.today - timedelta(days=30),
            "period_to": x.today,
            "rate": 0.05,
            "kind": kind,
        }
        if campaign is not None:
            vals["campaign_id"] = campaign.id
        return env["fix.partner.rebate"].with_user(x.officer).create(vals)

    x.claim, x.evidence, x.rebate = claim, evidence, rebate
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


def test_an_mdf_claim_carries_its_campaign(cm):
    cm.campaign.write({"partner_ids": [Command.link(cm.p1.id)]})
    rec = cm.claim(cm.p1, cm.campaign)
    assert rec.campaign_id == cm.campaign
    field = cm.env["fix.mdf.claim"]._fields["campaign_id"]
    assert field.comodel_name == "fix.campaign" and not field.required


def test_an_mdf_is_no_longer_a_rebate(cm):
    """M40-F26: one MDF mechanism - the rebate of kind 'mdf' is refused with
    the pointer to the MDF fund / claim registers, and a volume rebate still
    names no campaign."""
    cm.campaign.write({"partner_ids": [Command.link(cm.p1.id)]})
    with _refused(cm.env, ValidationError, "MDF Claim"):
        cm.rebate(cm.p1, kind="mdf")
    with _refused(cm.env, ValidationError, "market development fund"):
        cm.rebate(cm.p1, cm.campaign)
    # an MDF claim without a campaign is still allowed (the key is optional)
    assert cm.claim(cm.p1).campaign_id.id is False


def test_an_mdf_claim_points_only_at_a_campaign_its_partner_co_funds(cm):
    cm.campaign.write({"partner_ids": [Command.link(cm.p1.id)]})
    with _refused(cm.env, ValidationError, "co-marketing partner"):
        cm.claim(cm.p2, cm.campaign)


def test_the_campaign_is_pinned_once_the_claim_is_submitted(cm):
    cm.campaign.write({"partner_ids": [Command.link(cm.p1.id)]})
    cm.other.write({"partner_ids": [Command.link(cm.p1.id)]})
    rec = cm.claim(cm.p1, cm.campaign)
    rec.with_user(cm.officer).write({"campaign_id": cm.other.id})  # draft: still editable
    cm.evidence(rec)
    rec.with_user(cm.officer).action_submit()
    assert rec.state == "submitted"
    with _refused(cm.env, UserError):
        rec.with_user(cm.officer).write({"campaign_id": cm.campaign.id})
    assert rec.campaign_id == cm.other
    assert "campaign_id" in rec._fix_form_locked_fields()


def test_a_partner_with_a_live_mdf_claim_stays_on_the_campaign(cm):
    cm.campaign.write({"partner_ids": [Command.link(cm.p1.id), Command.link(cm.p2.id)]})
    rec = cm.claim(cm.p1, cm.campaign)
    with _refused(cm.env, ValidationError, "MDF"):
        cm.campaign.with_user(cm.officer).write({"partner_ids": [Command.unlink(cm.p1.id)]})
    with _refused(cm.env, ValidationError, "MDF"):
        cm.p1.with_user(cm.officer).write(
            {"comarketing_campaign_ids": [Command.unlink(cm.campaign.id)]}
        )
    # a partner with no MDF on the campaign leaves freely
    cm.campaign.with_user(cm.officer).write({"partner_ids": [Command.unlink(cm.p2.id)]})
    # once the claim is refused the link may go
    cm.evidence(rec)
    rec.with_user(cm.officer).action_submit()
    rec.with_user(cm.manager2).action_refuse(reason="No proof of the stall")
    cm.campaign.with_user(cm.officer).write({"partner_ids": [Command.unlink(cm.p1.id)]})
    assert not cm.campaign.partner_ids
