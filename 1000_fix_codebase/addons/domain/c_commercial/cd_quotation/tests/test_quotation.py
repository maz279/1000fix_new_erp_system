# cd_quotation tests — M36 (P06-M06-T05/T07).
#
# A04 C13 (2026-11-04): these used to read the module's source text
# (inspect.getsource + "in source"), which passes while the behaviour is
# broken. Each claim is now exercised as a non-admin user.
import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import assigned
from odoo.exceptions import UserError


def _user(env, login, groups=()):
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": login, "login": login, "group_ids": [(6, 0, ids)]})
    )


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    branch = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if not branch:
        entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
            {"legal_name": "M36 QT Entity", "code": "M36QE", "company_id": env.company.id}
        )
        branch = env["fix.branch"].create(
            {"name": "M36 QT", "code": "M36QT", "entity_id": entity.id, "operating_unit_id": ou.id}
        )
    brand = env["fix.brand"].create({"name": "M36QTBrand", "code": "M36Q"})
    model = env["fix.device.model"].create({"name": "M36QT", "brand_id": brand.id})
    partner = env["res.partner"].create({"name": "M36 QT Customer"})
    device = env["fix.device"].create({"device_model_id": model.id, "owner_id": partner.id})
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": partner.id,
            "branch_id": branch.id,
            "fault_description": "Cracked display",
        }
    )
    clerk = _user(env, "m36qt_clerk")
    t2 = _user(env, "m36qt_t2", ["cd_entity_config.group_dofa_tier_2"])
    t3 = _user(env, "m36qt_t3", ["cd_entity_config.group_dofa_tier_3"])

    def estimate(discount=0.0):
        return env["fix.estimate"].create(
            {
                "order_id": order.id,
                "operating_unit_id": ou.id,
                "discount": discount,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "line_type": "labour",
                            "description": "labour",
                            "quantity": 1,
                            "unit_price": 3000.0,
                        },
                    )
                ],
            }
        )

    def request(est, pct):
        return (
            env["fix.discount.approval"]
            .with_user(clerk)
            .create(
                {
                    "quotation_id": est.id,
                    "operating_unit_id": ou.id,
                    "discount_pct": pct,
                    "justification": "Loyal customer",
                }
            )
        )

    return type(
        "Ctx",
        (),
        {"env": env, "clerk": clerk, "t2": t2, "t3": t3, "estimate": estimate, "request": request},
    )


class TestUnifiedEstimate:
    def test_the_estimate_itself_carries_the_quotation_lifecycle(self, ctx):
        """T07 / AS-01: ONE estimate concept — the M01 estimate is quoted."""
        est = ctx.estimate()
        assert est.quotation_state == "internal"

    def test_quote_requires_approved_estimate(self, ctx):
        with pytest.raises(UserError, match="approved estimate"):
            ctx.estimate().with_user(ctx.clerk).action_quote()

    def test_pending_discount_blocks_quoting(self, ctx):
        est = ctx.estimate()
        ctx.request(est, 15.0)  # above the agent's 10%: pending
        est.action_send()
        est.action_approve()
        with pytest.raises(UserError, match="pending discount approval blocks quoting"):
            est.with_user(ctx.clerk).action_quote()

    def test_validity_window_positive(self, ctx):
        with pytest.raises(UserError, match="validity window must be positive"):
            ctx.env["fix.estimate"].create(
                {"order_id": ctx.estimate().order_id.id, "valid_days": 0}
            )


class TestDiscountGovernance:
    @pytest.mark.parametrize(("pct", "state"), [(10.0, "approved"), (12.0, "pending")])
    def test_authority_matrix(self, ctx, pct, state):
        """BRU-PRC-06, the single M11 ladder: the agent's own authority ends at 10%."""
        assert ctx.request(ctx.estimate(), pct).state == state

    def test_high_discount_needs_director(self, ctx):
        """Above 20% a sales manager / director (Tier 3) is asked, not Tier 2."""
        req = ctx.request(ctx.estimate(), 25.0)
        req.with_user(ctx.clerk).action_request_approval(justification="tender match")
        assert ctx.t3 in assigned(req) and ctx.t2 not in assigned(req)
