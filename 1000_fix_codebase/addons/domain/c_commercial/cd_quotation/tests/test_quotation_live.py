# cd_quotation live-ORM tests — M36 quotation lifecycle + discount governance.
import json
import uuid
from types import SimpleNamespace

import pytest
from odoo.exceptions import UserError

# per-run tag: unique keys never collide with a concurrent run on fix_test
TAG = uuid.uuid4().hex[:6].upper()


def _events(env, event_type, aggregate, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", aggregate),
            ("aggregate_id", "=", aggregate_id),
        ],
        order="id",
    )
    return [json.loads(row.payload) for row in rows]


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    # fix.entity is UNIQUE per company: the branch lives on its own company
    # so concurrent runs never queue behind one uncommitted entity row
    company = env["res.company"].create({"name": f"QA Quote Co {TAG}"})
    entity = env["fix.entity"].create(
        {"code": f"E{TAG}", "legal_name": "Quote Test Ltd", "company_id": company.id}
    )
    branch = env["fix.branch"].create(
        {
            "code": f"B{TAG}",
            "name": "Quote Branch",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": f"QA Quote Brand {TAG}", "code": f"Q{TAG}"})
    model = env["fix.device.model"].create({"name": "Galaxy A55", "brand_id": brand.id})
    device = env["fix.device"].create({"device_model_id": model.id, "branch_id": branch.id})
    partner = env["res.partner"].create({"name": "Rahim Uddin"})
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": partner.id,
            "branch_id": branch.id,
            "fault_description": "Cracked display",
        }
    )
    clerk = env["res.users"].create(
        {
            "name": "Front Desk Agent",
            "login": f"qt-front-desk-{TAG}",
            "group_ids": [(6, 0, [env.ref("base.group_user").id])],
        }
    )
    return SimpleNamespace(env=env, ou=ou, order=order, clerk=clerk)


def _estimate(ctx, **vals):
    return ctx.env["fix.estimate"].create({"order_id": ctx.order.id, **vals})


def _approval(ctx, estimate, pct):
    return ctx.env["fix.discount.approval"].create(
        {
            "operating_unit_id": ctx.ou.id,
            "quotation_id": estimate.id,
            "discount_pct": pct,
            "justification": "Loyal corporate customer",
        }
    )


# --- quotation lifecycle -------------------------------------------------------


def test_new_estimate_is_an_internal_quotation(ctx):
    estimate = _estimate(ctx)
    assert (estimate.quotation_state, estimate.valid_days) == ("internal", 15)


def test_only_an_approved_estimate_is_quoted(ctx):
    with (
        pytest.raises(UserError, match="Only an approved estimate can be quoted"),
        ctx.env.cr.savepoint(),
    ):
        _estimate(ctx).action_quote()


def test_pending_discount_blocks_quoting(ctx):
    estimate = _estimate(ctx, state="approved")
    _approval(ctx, estimate, 8.0)  # above the 5% agent authority: pending
    with (
        pytest.raises(UserError, match="pending discount approval blocks quoting"),
        ctx.env.cr.savepoint(),
    ):
        estimate.action_quote()
    assert estimate.quotation_state == "internal"


def test_quote_sends_and_publishes(ctx):
    estimate = _estimate(ctx, state="approved", valid_days=7)
    _approval(ctx, estimate, 3.0)  # within agent authority: auto-approved
    estimate.action_quote()
    assert estimate.quotation_state == "quoted"
    assert estimate.sent_at
    assert _events(ctx.env, "quotation.sent", "fix.estimate", estimate.id) == [
        {"version": estimate.version, "grand_total": estimate.grand_total, "valid_days": 7}
    ]


@pytest.mark.parametrize("from_state", ["quoted", "negotiating"])
def test_accept_from_quoted_or_negotiating(ctx, from_state):
    estimate = _estimate(ctx, quotation_state=from_state)
    estimate.action_accept()
    assert estimate.quotation_state == "accepted"
    assert estimate.accepted_at
    assert _events(ctx.env, "quotation.accepted", "fix.estimate", estimate.id) == [
        {"version": estimate.version, "grand_total": estimate.grand_total}
    ]


@pytest.mark.parametrize("from_state", ["internal", "declined", "accepted"])
def test_accept_requires_a_live_quote(ctx, from_state):
    with (
        pytest.raises(UserError, match="Only a quoted quotation can be accepted"),
        ctx.env.cr.savepoint(),
    ):
        _estimate(ctx, quotation_state=from_state).action_accept()


def test_decline(ctx):
    estimate = _estimate(ctx, quotation_state="quoted")
    estimate.action_decline()
    assert estimate.quotation_state == "declined"


@pytest.mark.parametrize("days", [0, -3])
def test_validity_window_must_be_positive(ctx, days):
    with pytest.raises(UserError, match="validity window must be positive"), ctx.env.cr.savepoint():
        _estimate(ctx, valid_days=days)


# --- discount governance (05-04 section 7) -------------------------------------


@pytest.mark.parametrize(("pct", "state"), [(4.0, "approved"), (5.0, "approved"), (5.5, "pending")])
def test_agent_authority_auto_approves_up_to_five_percent(ctx, pct, state):
    assert _approval(ctx, _estimate(ctx), pct).state == state


def test_manager_band_discount_is_approved_and_published(ctx):
    approval = _approval(ctx, _estimate(ctx), 8.0)
    approval.with_user(ctx.clerk).action_approve()  # 8% <= the 10% manager cap
    assert approval.state == "approved"
    assert approval.approved_by == ctx.clerk
    assert _events(ctx.env, "discount.approved", "fix.discount.approval", approval.id) == [
        {"pct": 8.0}
    ]


def test_director_band_discount_needs_a_system_approver(ctx):
    approval = _approval(ctx, _estimate(ctx), 12.0)
    with (
        pytest.raises(UserError, match=r"above 10.0% require commercial-director approval"),
        ctx.env.cr.savepoint(),
    ):
        approval.with_user(ctx.clerk).action_approve()
    assert approval.state == "pending"
    approval.action_approve()  # the superuser holds base.group_system
    assert approval.state == "approved"
    assert approval.approved_by == ctx.env.user
