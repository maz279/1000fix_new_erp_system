"""cd_partner tests - P10-M04 (CD-M40-01)."""

import inspect
import unittest

import pytest
from odoo.addons.cd_partner.models.fix_partner import FixReferral
from odoo.addons.cd_partner.tests.m40_fixtures import make_onboardable
from odoo.exceptions import UserError


# A04 audit C13 (2026-11-04): the fix.partner checks here were source-text
# and attribute-existence tests ("partner.onboarded" appears in the class,
# the class has a contract_id), which passed while a state write onboarded
# anyone. They are now behaviour tests as a non-admin user, below; the
# lifecycles are proved in test_a04_c2_c13_partner.py. The fix.referral
# checks (A08) are unchanged.
@pytest.fixture
def channel(odoo_env):
    env = odoo_env
    users = env["res.users"].with_context(no_reset_password=True)
    officer = users.create(
        {
            "name": "M40 Unit Officer",
            "login": "m40.unit.officer@a04.test",
            "group_ids": [(6, 0, [env.ref("cd_partner.group_fix_channel_officer").id])],
        }
    )
    manager = users.create(
        {
            "name": "M40 Unit Manager",
            "login": "m40.unit.manager@a04.test",
            "group_ids": [(6, 0, [env.ref("cd_partner.group_fix_channel_manager").id])],
        }
    )
    party = env["res.partner"].create({"name": "M40 Unit Party"})
    return env, officer, manager, party


def test_a_partner_is_a_role_on_an_m33_party(channel):
    env, officer, _manager, party = channel
    p = env["fix.partner"].with_user(officer).create({"name": "Unit", "partner_id": party.id})
    assert (p.partner_id, p.partner_type, p.state, p.commission_rate) == (
        party,
        "referral",
        "prospective",
        0.0,  # A04 ERP audit M40-F5: no rate until one is approved
    )


def test_onboarding_is_a_second_persons_decision_and_is_published(channel):
    env, officer, manager, party = channel
    p = (
        env["fix.partner"]
        .with_user(officer)
        .create({"name": "Unit", "partner_id": party.id, "territory": "Mirpur"})
    )
    make_onboardable(env, p)  # M40-F11 set-up: programme, agreement, checklist
    with pytest.raises(UserError, match="Channel Manager"):
        p.with_user(officer).action_onboard()
    p.with_user(manager).action_onboard()
    assert p.state == "onboarded"
    assert env["fix.event.outbox"].search_count(
        [("event_type", "=", "partner.onboarded"), ("aggregate_id", "=", p.id)]
    )


class TestReferral(unittest.TestCase):
    def test_commission_through_events(self):
        """M12<->M53 break: referral commissions publish events, never
        call the settlement engine directly."""
        src = inspect.getsource(FixReferral.action_earn_commission)
        self.assertIn("commission.earned", src)
        self.assertNotIn("fix.commission.ledger", src)

    def test_conversion_required(self):
        src = inspect.getsource(FixReferral.action_earn_commission)
        self.assertIn("Convert before", src)

    def test_conversion_event(self):
        self.assertIn("referral.converted", inspect.getsource(FixReferral))

    def test_referral_states(self):
        src = inspect.getsource(FixReferral)
        for s in ("submitted", "converted", "commissioned"):
            self.assertIn(s, src)

    def test_monetary_commission(self):
        import odoo.fields as f

        self.assertIsInstance(FixReferral.commission_amount, f.Monetary)


if __name__ == "__main__":
    unittest.main()
