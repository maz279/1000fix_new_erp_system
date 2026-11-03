"""A04 audit C1 (M40-7): a portal partner cannot set its own commission.

A P12 partner wrote its own referral to commissioned on a BDT 5,000,000 base,
and M53's accrual posts the GL entry from those fields. A partner submits who
was referred; converting, the revenue base and the commission are the
company's.
"""

import pytest
from odoo.exceptions import AccessError, UserError

REFUSED = (AccessError, UserError)


@pytest.fixture
def partner(odoo_env):
    env = odoo_env
    contact = env["res.partner"].create({"name": "C1 Referral Partner"})
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "C1 Partner",
                "login": "c1.partner@a04.test",
                "partner_id": contact.id,
                "group_ids": [(6, 0, [env.ref("cd_partner.group_fix_partner_portal").id])],
            }
        )
    )
    profile = env["fix.partner"].create({"name": "C1 Referral Partner", "partner_id": contact.id})
    referred = env["res.partner"].create({"name": "C1 Referred Customer"})
    return env, user, profile, referred


@pytest.mark.parametrize(
    "extra",
    [{"state": "commissioned"}, {"base_amount": 5000000.0}, {"commission_amount": 250000.0}],
)
def test_a_partner_cannot_submit_its_own_commission_terms(partner, extra):
    env, user, profile, referred = partner
    vals = {"name": "C1 ref", "partner_id": profile.id, "referred_partner_id": referred.id}
    vals.update(extra)
    with pytest.raises(REFUSED):
        env["fix.referral"].with_user(user).create(vals)


def test_a_partner_submits_and_the_company_converts(partner):
    env, user, profile, referred = partner
    ref = (
        env["fix.referral"]
        .with_user(user)
        .create({"name": "C1 ref", "partner_id": profile.id, "referred_partner_id": referred.id})
    )
    assert ref.state == "submitted" and not ref.base_amount
    with pytest.raises(REFUSED):
        ref.with_user(user).write({"base_amount": 5000000.0})
    with pytest.raises(REFUSED):
        ref.with_user(user).action_convert(base_amount=5000000.0)
    with pytest.raises(REFUSED):
        ref.with_user(user).action_earn_commission()
    assert ref.state == "submitted"
