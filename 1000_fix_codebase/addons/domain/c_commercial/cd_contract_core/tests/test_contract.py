# cd_contract_core tests — M08 (P07-M01).
#
# A04 C13 (2026-11-04): this file asserted that identifiers appeared in the
# source text (`assertIn("def entitlement_active", SOURCE)`), which passed on
# a stub. Each check is now the behaviour it named, run on the live ORM as a
# Contract Officer (a non-admin role holder), rolled back per test.
import json
import uuid
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError

TAG = uuid.uuid4().hex[:6].upper()
OFFICER = "cd_contract_core.group_contract_officer"


@pytest.fixture
def ctx(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    officer = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "C13 officer",
                "login": "c13_officer_%s" % TAG,
                "group_ids": [(6, 0, [env.ref("base.group_user").id, env.ref(OFFICER).id])],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    brand = env["fix.brand"].create({"name": "C13 Brand %s" % TAG, "code": "C13%s" % TAG})
    model = env["fix.device.model"].create({"name": "C13 Model", "brand_id": brand.id})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "serial_number": "C13-%s" % TAG}
    )
    partner = env["res.partner"].create({"name": "C13 Customer %s" % TAG})
    today = fields.Date.context_today(env["fix.contract"])
    return env, ou, officer, device, partner, today


def _contract(ctx, family="amc", **kw):
    env, ou, officer, device, partner, today = ctx
    vals = {
        "name": "C13 %s" % family,
        "family": family,
        "customer_id": partner.id,
        "operating_unit_id": ou.id,
        "date_start": today - timedelta(days=5),
        "date_end": today + timedelta(days=360),
        "annual_value": 120000.0,
        "stamp_duty_cert_no": "SD-C13",
        "has_signed_contract_doc": True,
        "covered_device_ids": [(6, 0, device.ids)],
    }
    vals.update(kw)
    return env["fix.contract"].with_user(officer).create(vals)


def _live(ctx, **kw):
    k = _contract(ctx, **kw)
    k.sudo().action_activate()  # the trusted path stands in for approval + signature
    k.invalidate_recordset()
    return k


@pytest.mark.parametrize("family", ["amc", "ramc", "managed", "rental", "marketplace"])
def test_all_five_families_on_one_engine(ctx, family):
    k = _contract(ctx, family=family)
    assert k.family == family and k.state == "draft"


def test_drawdown_never_goes_negative_and_unlimited_always_draws(ctx):
    k = _live(ctx)
    Ent = ctx[0]["fix.contract.entitlement"].sudo()
    counted = Ent._guarded().create(
        {"contract_id": k.id, "entitlement_type": "incidents", "quantity_included": 1}
    )
    unlimited = Ent._guarded().create(
        {"contract_id": k.id, "entitlement_type": "visits", "quantity_included": 0}
    )
    assert counted.consume(1.0) and not counted.consume(1.0)
    assert counted.quantity_remaining == 0
    assert unlimited.quantity_remaining == -1 and unlimited.consume(5.0)
    rows = ctx[0]["fix.event.outbox"].search([("event_type", "=", "entitlement.consumed")])
    assert {json.loads(r.payload)["remaining"] for r in rows} >= {0.0, -1}


def test_entitlement_active_is_the_amc_gate(ctx):
    env, _ou, _officer, device, _partner, _today = ctx
    k = _contract(
        ctx, entitlement_ids=[(0, 0, {"entitlement_type": "incidents", "quantity_included": 2})]
    )
    Ent = env["fix.contract.entitlement"]
    assert not Ent.entitlement_active(device.id, "amc"), "a draft contract covers nothing"
    k.sudo().action_activate()
    assert Ent.entitlement_active(device.id, "amc")
    assert not Ent.entitlement_active(device.id, "rental"), "only the contract's family"


def test_signature_gate_pm_schedule_and_activation_event(ctx):
    k = _contract(ctx)
    with pytest.raises(UserError):
        k.action_activate()  # a draft contract is not activated by its officer
    k.sudo().action_activate()
    assert k.pm_visit_ids and k.sudo().oca_contract_id
    rows = ctx[0]["fix.event.outbox"].search(
        [("event_type", "=", "contract.activated"), ("aggregate_id", "=", k.id)]
    )
    assert rows


def test_renewal_escalates_and_announces_on_activation(ctx):
    k = _live(ctx, escalation_pct=10.0)
    renewal = k.action_renew()
    assert renewal.annual_value == 132000.0 and k.state == "active"
    renewal.write({"stamp_duty_cert_no": "SD-R-C13", "has_signed_contract_doc": True})
    renewal.sudo().action_activate()
    rows = ctx[0]["fix.event.outbox"].search(
        [("event_type", "=", "contract.renewed"), ("aggregate_id", "=", renewal.id)]
    )
    assert json.loads(rows.payload)["old_code"] == k.code


def test_margin_is_value_less_delivered_cost(ctx):
    k = _live(ctx)
    # A04 ERP audit M08-F13: the margin is on the whole term's value
    assert k.total_delivery_cost == 0.0 and k.contract_margin_bdt == k.term_value


def test_contract_sla_uses_the_m01_policy_model(ctx):
    env = ctx[0]
    policy = env["fix.sla.policy"].create(
        {
            "code": "C13-%s" % TAG,
            "name": "C13 SLA",
            "service_type": "onsite",
            "response_hours": 4,
            "resolution_hours": 24,
            "priority": "high",
        }
    )
    k = _contract(ctx, sla_policy_ids=[(6, 0, policy.ids)])
    result = k.reconcile_service_sla()
    assert result["reconciled"] and result["max_response_hours"] == 4


def test_price_revision_on_a_live_contract_is_an_amendment(ctx):
    k = _live(ctx)
    amendment = k.action_price_revision(150000.0, "uplift")
    k.invalidate_recordset()
    assert k.annual_value == 120000.0 and amendment.kind == "pricing"
    assert amendment.delta_value == 30000.0 and amendment.state == "draft"


def test_pm_visit_dispatch_opens_one_order_linked_to_the_contract(ctx):
    env = ctx[0]
    branch = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if not branch:
        company = env["res.company"].create({"name": "C13 Co %s" % TAG})
        entity = env["fix.entity"].create(
            {"code": "C13E%s" % TAG, "legal_name": "C13 Ltd", "company_id": company.id}
        )
        branch = env["fix.branch"].create(
            {
                "code": "C13B%s" % TAG,
                "name": "C13",
                "entity_id": entity.id,
                "operating_unit_id": ctx[1].id,
            }
        )
    ctx[3].branch_id = branch
    k = _live(ctx)
    visit = k.pm_visit_ids[:1]
    visit.action_create_service_order()
    order = visit.service_order_id
    visit.action_create_service_order()
    assert visit.service_order_id == order and order.contract_id == k
    assert order.order_category == "amc"
