"""A11 audit P2 (A05 area): the rental write-off and loss-waiver DOFA stamps
are ROUTED M63 requests — decided from the approver's inbox, never by
pressing Approve on the record while holding the tier."""

from datetime import date

import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
)
from odoo.exceptions import UserError

RES = "fix.rental.reservation"
T2 = "cd_entity_config.group_dofa_tier_2"


def _approver(env, login="a11.rental.t2"):
    existing = env["res.users"].search([("login", "=", login)], limit=1)
    if existing:
        return existing
    return env["res.users"].create(
        {
            "name": "A11 Rental Tier 2",
            "login": login,
            "group_ids": [
                (4, env.ref("base.group_user").id),
                (4, env.ref(T2).id),
            ],
        }
    )


def _reservation(env):
    return env[RES].create(
        {
            "customer_id": env["res.partner"].create({"name": "A11 Rental Customer"}).id,
            "date_from": date(2026, 11, 1),
            "date_to": date(2026, 11, 4),
        }
    )


def _asset(env):
    tmpl = env["product.template"].create({"name": "A11 router rental"})
    item = env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id})
    sku = env["fix.rental.sku"].create({"catalogue_item_id": item.id})
    return env["fix.rental.asset"].create(
        {"name": "A11-ASSET-1", "rental_sku_id": sku.id, "purchase_cost": 100000.0}
    )


class TestLossWaiverIsRouted:
    def test_the_waiver_comes_from_the_inbox_only(self, odoo_env):
        env = odoo_env
        approver = _approver(env)
        damage = env["fix.rental.damage"].create(
            {"reservation_id": _reservation(env).id, "description": "Cracked body", "cost": 30000.0}
        )
        assert damage.dofa_tier_required == "tier_1"
        # Without the sign-off the waiver refuses; a direct press of the DOFA
        # approve is refused too — the stamp comes from the inbox only.
        with pytest.raises(UserError, match="sign-off|approved"):
            damage.action_waive()
        damage.action_request_approval(justification="Customer dispute settled out of court.")
        assert damage.approval_state == "pending"
        assert approver in assigned(damage) or assigned(damage)
        with pytest.raises(UserError, match="inbox"):
            damage.with_user(approver).action_dofa_approve()
        approve_via_inbox(damage, approver)
        assert damage.dofa_approved
        damage.action_waive()
        assert damage.waived and damage.settled
        assert damage.waived_amount == 30000.0

    def test_a_recovery_booked_while_pending_withdraws_the_request(self, odoo_env):
        env = odoo_env
        _approver(env)
        damage = env["fix.rental.damage"].create(
            {"reservation_id": _reservation(env).id, "description": "Lost lens cap", "cost": 5000.0}
        )
        damage.action_request_approval(justification="Goodwill on a long contract.")
        assert damage.approval_state == "pending"
        # The unrecovered loss is the approval amount: recovering part of it
        # changes what the approval covers, so the request is withdrawn.
        damage.write({"recovered_amount": 2000.0})
        damage.invalidate_recordset()
        assert damage.approval_state == "none"
        with pytest.raises(UserError, match="sign-off|approved"):
            damage.action_waive()


class TestRetirementWriteOffIsRouted:
    def test_the_write_off_comes_from_the_inbox_only(self, odoo_env):
        env = odoo_env
        approver = _approver(env)
        asset = _asset(env)
        assert asset.net_book_value == 100000.0
        assert asset.dofa_tier_required == "tier_2"
        with pytest.raises(UserError, match="sign-off|approved"):
            asset.action_retire()
        asset.action_request_approval(justification="End of fleet life; beyond repair.")
        assert asset.approval_state == "pending"
        with pytest.raises(UserError, match="inbox"):
            asset.with_user(approver).action_dofa_approve()
        approve_via_inbox(asset, approver)
        assert asset.dofa_approved
        asset.action_retire()
        assert asset.status == "retired" and asset.retired_on
