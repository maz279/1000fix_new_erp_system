# cd_rate_card tests — M11 data core (P06-M06).
#
# A04 C13 (2026-11-04): these were source-text checks (`"A tier-99 rate is a
# CONTRACT rate" in inspect.getsource(...)`, hasattr on the constraint). They
# now run the rule as a non-admin Pricing Officer, through the ORM.
import uuid

import pytest
from odoo.addons.cd_rate_card.tests.contract_helpers import contract
from odoo.exceptions import UserError

CODE = "A4C13-RC-%s" % uuid.uuid4().hex[:6]


@pytest.fixture
def officer(odoo_env):
    return (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A04 C13 pricing officer",
                "login": "a04c13.pricing.%s@a04.test" % uuid.uuid4().hex[:6],
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            odoo_env.ref("base.group_user").id,
                            odoo_env.ref("cd_rate_card.group_pricing_officer").id,
                        ],
                    )
                ],
            }
        )
    )


def _card(env, user, **vals):
    return (
        env["fix.rate.card"]
        .with_user(user)
        .create(dict({"product_code": CODE, "unit_price": 450.0}, **vals))
    )


class TestRateCard:
    def test_contract_lane_needs_a_contract_number(self, odoo_env, officer):
        """Tier-99 is the contract lane and demands a contract number."""
        with pytest.raises(UserError, match="CONTRACT rate"), odoo_env.cr.savepoint():
            _card(odoo_env, officer, min_tier=99)
        k = contract(odoo_env)
        assert _card(odoo_env, officer, min_tier=99, contract_no=k.code).name.endswith(
            "contract %s" % k.code
        )

    def test_unique_per_product_tier_contract(self, odoo_env, officer):
        _card(odoo_env, officer, min_tier=2)
        with pytest.raises(Exception, match="product_tier_unique"), odoo_env.cr.savepoint():
            _card(odoo_env, officer, min_tier=2, unit_price=500.0)

    def test_projects_to_engine_line(self, odoo_env, officer):
        line = _card(odoo_env, officer, unit_price=750.0).to_engine_line()
        assert (line.product_code, str(line.unit_price)) == (CODE, "750.0")

    def test_a_new_card_is_a_draft_until_released(self, odoo_env, officer):
        card = _card(odoo_env, officer)
        assert card.state == "draft"
        assert not odoo_env["fix.rate.card"]._resolve(CODE)
