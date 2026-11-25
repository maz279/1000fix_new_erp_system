"""A04 audit C1 (M12-2, M12-7): a portal seller cannot approve themselves.

With write on their own profile a P07 seller set kyc_status=verified,
cfo_approved, tier=platinum and lifted their own payout hold; they could also
mark their own quote selected and rule on their disputes. The seller API only
reads profiles and disputes and creates quotes, so that is all the portal
group may now do.
"""

import pytest
from odoo.exceptions import AccessError, UserError

REFUSED = (AccessError, UserError)


@pytest.fixture
def seller(odoo_env):
    env = odoo_env
    partner = env["res.partner"].create({"name": "C1 Seller Shop"})
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "C1 Seller",
                "login": "c1.seller@a04.test",
                "partner_id": partner.id,
                "group_ids": [(6, 0, [env.ref("cd_marketplace.group_fix_marketplace_seller").id])],
            }
        )
    )
    profile = env["fix.marketplace.seller"].create(
        {"name": "C1 Seller Shop", "partner_id": partner.id}
    )
    return env, user, profile


@pytest.mark.parametrize(
    "vals",
    [
        {"kyc_status": "verified"},
        {"cfo_approved": True},
        {"tier": "platinum"},
        {"payout_hold": False},
        {"rating": 5.0},
    ],
)
def test_a_seller_cannot_approve_or_promote_themselves(seller, vals):
    env, user, profile = seller
    before = {k: profile[k] for k in vals}
    with pytest.raises(REFUSED):
        profile.with_user(user).write(vals)
    assert {k: profile[k] for k in vals} == before


def test_a_seller_still_reads_their_own_profile(seller):
    env, user, profile = seller
    assert profile.with_user(user).read(["name"])[0]["name"] == "C1 Seller Shop"


def _open_order(env):
    return env["fix.marketplace.order"].create(
        {
            "name": "C1-JOB",
            "order_type": "refurb_resale",
            "customer_id": env["res.partner"].create({"name": "C1 Buyer"}).id,
            "description": "C1 probe job",
            "state": "open",
        }
    )


def test_a_seller_quotes_but_cannot_select_their_own_quote(seller):
    env, user, profile = seller
    profile.sudo().write({"kyc_status": "verified", "cfo_approved": True})
    order = _open_order(env)
    Quote = env["fix.seller.quote"].with_user(user)
    with pytest.raises(UserError, match="only the operator selects"):
        Quote.create(
            {
                "marketplace_order_id": order.id,
                "seller_id": profile.id,
                "quoted_price": 900.0,
                "state": "selected",
            }
        )
    quote = Quote.create(
        {"marketplace_order_id": order.id, "seller_id": profile.id, "quoted_price": 900.0}
    )
    assert quote.state == "submitted"
    assert order.state == "quoted", "the first quote still moves the job (system transition)"
    with pytest.raises(REFUSED):
        quote.write({"quoted_price": 9000.0})
