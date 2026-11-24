# ruff: noqa: F811  (the marketplace fixture is imported and used as a parameter)
"""A04 ERP audit, round 2 (21 Nov 2026) - M12 masking, award window, probation.

  M12-F7   before award a seller sees an open job as a short brief and the
           customer's initials: the order's customer and description are
           staff fields; the awarded seller alone sees the full job, and the
           customer's contact only while it is revealed
  M12-F15  the awarded seller accepts within the window, else the award
           lapses back to bidding (cron); the job starts only once accepted;
           a provisional seller holds at most the probation cap of open jobs

Run as a REAL portal seller in a fresh environment (no sudo prefetch), and
as marketplace operators / compliance.
"""

from datetime import timedelta
from types import SimpleNamespace

import pytest
from odoo import fields
from odoo.addons.cd_marketplace.controllers import seller_api
from odoo.addons.cd_marketplace.controllers.seller_api import SellerApiController
from odoo.addons.cd_marketplace.models.fix_marketplace_award import job_brief, masked_name
from odoo.exceptions import AccessError, UserError

from .test_a04_m12_controls import QUOTE, SELLER, mk  # noqa: F401

REFUSED = (UserError, AccessError)
SELLER_GROUP = "cd_marketplace.group_fix_marketplace_seller"


def _portal_seller(mk, name):
    """A portal seller account and its verified, CFO-approved profile."""
    env = mk.env
    partner = env["res.partner"].create({"name": name})
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": name,
                "login": "r2_" + name.lower().replace(" ", "_"),
                "partner_id": partner.id,
                "group_ids": [(6, 0, [env.ref(SELLER_GROUP).id])],
            }
        )
    )
    profile = mk.seller(name, partner=partner)
    return user, profile


def _fresh(env, user):
    """A new environment of `user` (empty cache: nothing prefetched as sudo)."""
    env.flush_all()
    env.invalidate_all()
    return env(user=user.id, su=False)


def _api(env, user, monkeypatch):
    fake = SimpleNamespace(
        env=_fresh(env, user),
        session={},
        httprequest=SimpleNamespace(remote_addr="127.0.0.1", headers={}),
    )
    monkeypatch.setattr(seller_api, "request", fake)
    return SellerApiController()


# ================================================================ M12-F7
def test_f7_a_seller_never_reads_the_customer_or_description_before_award(mk):
    mk.customer.sudo().write({"phone": "01711000222", "name": "Rahim Karim"})
    order = mk.order(description="Screen cracked, call me on 01711000222 or rahim@mail.test")
    user, _profile = _portal_seller(mk, "R2 Board Shop")
    as_seller = _fresh(mk.env, user)["fix.marketplace.order"].browse(order.id)
    with pytest.raises(AccessError):
        as_seller.read(["customer_id"])
    with pytest.raises(AccessError):
        as_seller.read(["description"])
    row = as_seller.read(
        [
            "seller_job_brief",
            "seller_customer_name",
            "seller_customer_contact",
            "seller_description",
        ]
    )[0]
    assert row["seller_customer_name"] == "R. K."
    assert row["seller_customer_contact"] == ""
    assert "01711000222" not in row["seller_job_brief"]
    assert "rahim@mail.test" not in row["seller_job_brief"]
    assert row["seller_description"] == row["seller_job_brief"]


def test_f7_the_board_api_serves_the_masked_projection(mk, monkeypatch):
    mk.customer.sudo().write({"name": "Rahim Karim"})
    long = "Battery swollen; " + "details " * 60 + "phone 01811-222333"
    order = mk.order(description=long)
    user, _profile = _portal_seller(mk, "R2 Api Shop")
    rows = {r["id"]: r for r in _api(mk.env, user, monkeypatch).orders()["orders"]}
    row = rows[order.id]
    assert row["customer"] == "R. K."
    assert len(row["description"]) <= 140 and "01811" not in row["description"]
    assert row["description"] != long


def test_f7_only_the_awarded_seller_sees_the_full_job(mk, monkeypatch):
    mk.customer.sudo().write({"name": "Rahim Karim", "phone": "01711000333"})
    winner_user, winner = _portal_seller(mk, "R2 Winner")
    loser_user, loser = _portal_seller(mk, "R2 Loser")
    order = mk.order(description="Fan noise, 3rd floor flat")
    mk.env[QUOTE].create(
        {"marketplace_order_id": order.id, "seller_id": loser.id, "quoted_price": 900}
    )
    q = mk.env[QUOTE].create(
        {"marketplace_order_id": order.id, "seller_id": winner.id, "quoted_price": 800}
    )
    q.with_user(mk.operator).action_select()
    win = _fresh(mk.env, winner_user)["fix.marketplace.order"].browse(order.id)
    assert win.seller_customer_name == "Rahim Karim"
    assert win.seller_description == "Fan noise, 3rd floor flat"
    assert "01711000333" in win.seller_customer_contact
    # the losing seller no longer reaches the job at all (record rule)
    lose = _fresh(mk.env, loser_user)["fix.marketplace.order"]
    assert not lose.search([("id", "=", order.id)])
    awards = _api(mk.env, winner_user, monkeypatch).awards()["awards"]
    assert awards[0]["customer"] == "Rahim Karim" and awards[0]["contact"]


def test_f7_brief_and_name_helpers():
    assert masked_name("rahim  karim") == "R. K." and masked_name("") == "Customer"
    brief = job_brief("Call +880 1711-000111, a@b.co " + "x" * 300, 60)
    assert len(brief) <= 60 and "1711" not in brief and "a@b.co" not in brief


# ================================================================ M12-F15 window
def test_f15_the_job_starts_only_once_the_seller_accepts(mk):
    user, seller = _portal_seller(mk, "R2 Accept Shop")
    order, _q = mk.awarded(seller)
    assert order.award_expires_at
    with pytest.raises(UserError, match="not accepted"), mk.env.cr.savepoint():
        order.with_user(mk.operator).action_start_job()
    # another seller, or a plain user, cannot accept for them
    other_user, _other = _portal_seller(mk, "R2 Other Shop")
    with pytest.raises(UserError, match="awarded seller"), mk.env.cr.savepoint():
        _fresh(mk.env, other_user)["fix.marketplace.order"].browse(order.id).action_accept_award()
    assert _fresh(mk.env, user)["fix.marketplace.order"].browse(order.id).action_accept_award()
    order.invalidate_recordset()
    assert order.award_accept_channel == "seller" and order.award_accepted_by_id == user
    order.with_user(mk.operator).action_start_job()
    assert order.state == "in_progress"


def test_f15_an_unaccepted_award_lapses_back_to_bidding(mk):
    first_user, first = _portal_seller(mk, "R2 Slow Shop")
    _u2, second = _portal_seller(mk, "R2 Next Shop")
    order = mk.order()
    q2 = mk.env[QUOTE].create(
        {"marketplace_order_id": order.id, "seller_id": second.id, "quoted_price": 950}
    )
    q1 = mk.env[QUOTE].create(
        {"marketplace_order_id": order.id, "seller_id": first.id, "quoted_price": 900}
    )
    q1.with_user(mk.operator).action_select()
    assert (order.state, q2.state) == ("selected", "not_selected")
    # not yet due: the cron leaves it
    assert mk.env["fix.marketplace.order"].cron_lapse_unaccepted_awards() == 0
    mk.env.flush_all()
    mk.env.cr.execute(
        "UPDATE fix_marketplace_order SET award_expires_at = %s WHERE id = %s",
        (fields.Datetime.now() - timedelta(minutes=1), order.id),
    )
    mk.env.invalidate_all()
    assert mk.env["fix.marketplace.order"].cron_lapse_unaccepted_awards() == 1
    order.invalidate_recordset()
    assert (order.state, order.selected_quote_id, order.revealed_seller_id) == (
        "quoted",
        q1.browse(),
        first.browse(),
    )
    assert (q1.state, q2.state, order.awarded_price, order.customer_contact_revealed) == (
        "lapsed",
        "submitted",
        0.0,
        False,
    )
    # the lapsed seller can no longer accept; the operator awards another quote
    lapsed = _fresh(mk.env, first_user)["fix.marketplace.order"].search([("id", "=", order.id)])
    assert not lapsed.filtered(lambda o: o.revealed_seller_id)
    q2.with_user(mk.operator).action_select()
    assert order.state == "selected" and order.revealed_seller_id == second


def test_f15_a_late_acceptance_lapses_instead(mk, monkeypatch):
    user, seller = _portal_seller(mk, "R2 Late Shop")
    order, _q = mk.awarded(seller)
    mk.env.flush_all()
    mk.env.cr.execute(
        "UPDATE fix_marketplace_order SET award_expires_at = %s WHERE id = %s",
        (fields.Datetime.now() - timedelta(hours=1), order.id),
    )
    mk.env.invalidate_all()
    out = _api(mk.env, user, monkeypatch).accept_award(order_id=order.id)
    assert out["error"]["code"] == "award_lapsed"
    order.invalidate_recordset()
    assert order.state == "open" and not order.award_accepted_at


def test_f15_the_window_is_a_parameter(mk):
    mk.env["ir.config_parameter"].sudo().set_param("cd_marketplace.award_acceptance_hours", "6")
    order, _q = mk.awarded()
    left = order.award_expires_at - fields.Datetime.now()
    assert timedelta(hours=5, minutes=55) < left <= timedelta(hours=6)


def test_f15_an_operator_may_record_the_sellers_acceptance(mk):
    order, _q = mk.awarded()
    with pytest.raises(REFUSED), mk.env.cr.savepoint():
        order.with_user(mk.plain).action_accept_award()
    order.with_user(mk.operator).action_accept_award()
    assert order.award_accept_channel == "operator"


# ================================================================ M12-F15 probation
def test_f15_a_provisional_seller_takes_no_job_beyond_the_cap(mk):
    mk.env["ir.config_parameter"].sudo().set_param("cd_marketplace.probation_job_cap", "2")
    seller = mk.seller("R2 Probation Shop")
    assert seller.standing == "provisional"
    mk.awarded(seller)
    mk.awarded(seller)
    seller.invalidate_recordset(["open_job_count"])
    assert seller.open_job_count == 2
    with pytest.raises(UserError, match="probation cap of 2"), mk.env.cr.savepoint():
        mk.awarded(seller)
    # compliance ends the probation: no cap any more
    with pytest.raises(REFUSED), mk.env.cr.savepoint():
        seller.with_user(mk.operator).action_confirm_standing()
    seller.with_user(mk.compliance).action_confirm_standing(reason="3 clean jobs")
    assert seller.standing == "full"
    order, _q = mk.awarded(seller)
    assert order.state == "selected"


def test_f15_standing_is_guarded(mk):
    seller = mk.seller("R2 Guard Shop")
    with pytest.raises(REFUSED), mk.env.cr.savepoint():
        seller.with_user(mk.operator).write({"standing": "full"})
    with pytest.raises(UserError, match="why"), mk.env.cr.savepoint():
        seller.with_user(mk.compliance).action_place_on_probation()
    unverified = mk.seller("R2 Unverified", ready=False)
    with pytest.raises(UserError, match="approved seller"), mk.env.cr.savepoint():
        unverified.with_user(mk.compliance).action_confirm_standing()


# ================================================================ wiring
class TestDeployment:
    def test_wiring(self, odoo_env):
        env = odoo_env
        cron = env.ref("cd_marketplace.ir_cron_marketplace_award_lapse")
        assert cron.active and "cron_lapse_unaccepted_awards" in cron.code
        Order = env["fix.marketplace.order"]
        assert Order._fields["customer_id"].groups == "base.group_user"
        assert Order._fields["description"].groups == "base.group_user"
        from odoo.addons.cd_p03_portal.controllers.a04 import m12

        assert "action_accept_award" in m12.SURFACES["fix.marketplace.order"]["actions"]
        assert {"action_confirm_standing", "action_place_on_probation"} <= m12.SURFACES[SELLER][
            "actions"
        ]
        assert SellerApiController.accept_award.original_routing["auth"] == "user"
