"""A04 ERP audit, round 2 (21 Nov 2026), stream R2-2: the deferred M39 items.

  M39-F16 a price increase needs the customer's notice; it applies only after
          the notice period (a decrease needs none)
  M39-F17 usage_reported consumers (idempotent by source key) and the service
          gate on suspension / pause / cancellation, read by the M01 intake
  M39-F11 one contract is billed by exactly one engine (walker or M39)
Real users, the live ORM, rolled back (``odoo_env``)."""

import uuid
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError

TAG = uuid.uuid4().hex[:6].upper()
SUB_OFFICER = "cd_subscription.group_subscription_officer"
BILLING = "account.group_account_user"
CONTRACT_MANAGER = "cd_contract_core.group_contract_manager"


def _user(env, ou, login, *groups):
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %s" % (login, TAG),
                "login": "r2_%s_%s" % (login, TAG),
                "group_ids": [(6, 0, ids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def s(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)

    class S:
        pass

    x = S()
    x.env, x.ou = env, ou
    x.today = fields.Date.context_today(env["fix.subscription"])
    x.partner = env["res.partner"].create({"name": "R2 Customer %s" % TAG, "email": "r2@x.test"})
    x.officer = _user(env, ou, "officer", SUB_OFFICER)
    x.acct = _user(env, ou, "acct", BILLING)
    x.manager = _user(env, ou, "cmgr", CONTRACT_MANAGER)
    x.plain = _user(env, ou, "plain")
    env["ir.config_parameter"].sudo().set_param("cd_subscription.price_change_notice_days", "30")
    return x


def _sub(s, **kw):
    vals = {
        "name": "R2 sub %s" % uuid.uuid4().hex[:6],
        "customer_id": s.partner.id,
        "operating_unit_id": s.ou.id,
        "plan": "standard",
        "billing_cycle": "monthly",
        "recurring_amount": 3000.0,
        "start_date": s.today - timedelta(days=10),
        "next_invoice_date": s.today + timedelta(days=20),
        "state": "active",
    }
    vals.update(kw)
    return s.env["fix.subscription"].create(vals)


def _change(s, sub, amount, **kw):
    Pro = s.env["fix.subscription.proration"].with_user(s.officer)
    return Pro.create_for_plan_change(sub, amount, effective_date=s.today, **kw)


def _approve(s, pro):
    approve_via_inbox(pro, s.acct, requester=s.officer)
    return pro


# ------------------------------------------------------------ M39-F16
def test_f16_an_increase_waits_for_the_customers_notice(s):
    sub = _sub(s)
    pro = _approve(s, _change(s, sub, 4000.0))
    assert (pro.state, pro.applied_to_subscription, sub.recurring_amount) == (
        "approved",
        False,
        3000.0,
    )
    assert pro.is_price_increase and not pro.price_applies_from
    s.env["fix.subscription.proration"].cron_apply_due_prorations()
    assert sub.recurring_amount == 3000.0  # no notice, no new price
    with pytest.raises(UserError), s.env.cr.savepoint():
        pro.with_user(s.plain).action_send_price_notice("email")
    pro.with_user(s.officer).action_send_price_notice("email")
    assert pro.notice_sent_at and pro.notice_channel == "email"
    assert pro.effective_date == s.today + timedelta(days=30)  # moved to the end of the notice
    told = (
        s.env["mail.message"]
        .search([("model", "=", "fix.subscription"), ("res_id", "=", sub.id)])
        .filtered(lambda m: s.partner in m.partner_ids)
    )
    assert told and "BRU-SUB-07" in told[0].body
    with pytest.raises(UserError, match="was told"), s.env.cr.savepoint():
        pro.with_user(s.officer).action_send_price_notice("sms")
    s.env["fix.subscription.proration"].cron_apply_due_prorations()
    assert sub.recurring_amount == 3000.0  # the notice period has not run
    # 31 days later
    pro._guarded().write(
        {
            "notice_sent_at": fields.Datetime.now() - timedelta(days=31),
            "effective_date": s.today,
        }
    )
    s.env["fix.subscription.proration"].cron_apply_due_prorations()
    assert pro.applied_to_subscription and sub.recurring_amount == 4000.0


def test_f16_a_decrease_needs_no_notice(s):
    sub = _sub(s)
    pro = _approve(s, _change(s, sub, 2000.0))
    assert not pro.is_price_increase
    assert pro.applied_to_subscription and sub.recurring_amount == 2000.0
    with pytest.raises(UserError, match="does not raise"), s.env.cr.savepoint():
        pro.with_user(s.officer).action_send_price_notice("email")


def test_f16_a_customer_requested_increase_with_evidence_applies_at_once(s):
    sub = _sub(s)
    pro = _change(s, sub, 4500.0)
    with pytest.raises(UserError, match="signed contract amendment"), s.env.cr.savepoint():
        pro.with_user(s.officer).write(
            {"notice_exemption": "contract_amendment", "notice_exemption_ref": "x"}
        )
    pro.with_user(s.officer).write(
        {"notice_exemption": "customer_request", "notice_exemption_ref": "Customer email 21 Nov"}
    )
    _approve(s, pro)
    assert pro.applied_to_subscription and sub.recurring_amount == 4500.0
    with pytest.raises(UserError, match="notice terms are fixed"), s.env.cr.savepoint():
        pro.with_user(s.officer).write({"notice_exemption_ref": "changed"})


# ------------------------------------------------------------ M39-F17 usage
def test_f17_usage_is_ingested_once_per_source_key(s):
    sub = _sub(s)
    Intake = s.env["fix.subscription.usage.intake"]
    event = {
        "event_id": "evt-%s" % TAG,
        "payload": {
            "subscription_id": sub.id,
            "metric": "remote_hours",
            "quantity": 7.5,
            "period_start": str(s.today - timedelta(days=30)),
            "period_end": str(s.today),
            "source_key": "M05-%s" % TAG,
        },
    }
    out = Intake.consume_msp_usage_reported(event)
    usage = s.env["fix.subscription.usage"].browse(out["id"])
    assert (usage.source_module, usage.source_key, usage.quantity) == ("m05", "M05-%s" % TAG, 7.5)
    again = Intake.consume_msp_usage_reported(event)
    assert again == {"duplicate": True, "id": usage.id}
    # another source with the same key is another reading
    other = Intake.consume_rental_usage_reported(event)
    assert other["id"] != usage.id
    with pytest.raises(AccessError):
        Intake.with_user(s.officer).consume_msp_usage_reported(event)
    lost = dict(event, payload=dict(event["payload"], subscription_id=0, source_key="k2"))
    with pytest.raises(UserError, match="names no subscription"), s.env.cr.savepoint():
        Intake.consume_data_usage_reported(lost)


# ------------------------------------------------------------ M39-F17 service gate
def _order(s, customer):
    env = s.env
    entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1)
    if not entity:  # the test template has none for this company
        entity = env["fix.entity"].create(
            {"code": "R2E%s" % TAG[:4], "legal_name": "R2 Entity", "company_id": env.company.id}
        )
    branch = env["fix.branch"].create(
        {
            "name": "R2 desk %s" % TAG,
            "code": "R2%s" % uuid.uuid4().hex[:4].upper(),
            "entity_id": entity.id,
            "operating_unit_id": s.ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "R2 brand %s" % TAG, "code": "R2B%s" % TAG})
    model = env["fix.device.model"].create({"name": "R2 phone", "brand_id": brand.id})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "R2SN%s" % TAG}
    )
    return {
        "device_id": device.id,
        "customer_id": customer.id,
        "branch_id": branch.id,
        "fault_description": "No power",
    }


def test_f17_suspension_gates_m01_service_warn_by_default_refuse_by_param(s):
    sub = _sub(s)
    Sub = s.env["fix.subscription"]
    event = {"event_type": "subscription.service_order_locked", "aggregate_id": sub.id}
    # the payload is a claim: an active subscription is not gated
    assert "skipped" in Sub.consume_service_gate_event(event)
    sub._guarded().write({"state": "hold", "dunning_step": "escalate"})
    assert Sub.consume_service_gate_event(event)["gate"] == "closed"
    assert sub.service_gate == "closed"
    with pytest.raises(AccessError):
        Sub.with_user(s.officer).consume_service_gate_event(event)
    vals = _order(s, s.partner)
    order = s.env["fix.service.order"].create(vals)
    assert any("subscription is gated" in (m.body or "") for m in order.message_ids)
    s.env["ir.config_parameter"].sudo().set_param(
        "cd_subscription.suspended_service_policy", "refuse"
    )
    with pytest.raises(UserError, match="Service is gated"), s.env.cr.savepoint():
        s.env["fix.service.order"].create(dict(vals))
    sub._guarded().write({"state": "active", "dunning_step": "none"})
    Sub.consume_service_gate_event(
        {"event_type": "subscription.reinstated", "aggregate_id": sub.id}
    )
    assert sub.service_gate == "open"
    s.env["fix.service.order"].create(dict(vals))  # refused no more


def test_f17_a_pause_closes_the_gate_and_its_end_reopens_it(s):
    sub = _sub(s)
    Sub = s.env["fix.subscription"]
    sub._guarded().write({"state": "paused"})
    Sub.consume_service_gate_event({"event_type": "subscription.paused", "aggregate_id": sub.id})
    assert sub.service_gate == "closed"
    sub._guarded().write({"state": "active"})
    Sub.consume_service_gate_event({"event_type": "subscription.resumed", "aggregate_id": sub.id})
    assert sub.service_gate == "open"


# ------------------------------------------------------------ M39-F11
def _contract(s, family="amc", **kw):
    vals = {
        "name": "R2 contract %s" % uuid.uuid4().hex[:6],
        "customer_id": s.partner.id,
        "family": family,
        "operating_unit_id": s.ou.id,
        "date_start": s.today,
        "date_end": s.today + timedelta(days=364),
        "annual_value": 120000.0,
    }
    vals.update(kw)
    return s.env["fix.contract"].create(vals)


def test_f11_a_contract_the_walker_bills_takes_no_subscription(s):
    contract = _contract(s)
    assert contract.billing_engine == "walker"
    with pytest.raises(UserError, match="bill the customer twice"), s.env.cr.savepoint():
        _sub(s, contract_id=contract.id)
    with pytest.raises(UserError, match="bill the customer twice"), s.env.cr.savepoint():
        _sub(s).write({"contract_id": contract.id})
    with pytest.raises(UserError), s.env.cr.savepoint():
        contract.with_user(s.plain).write({"billing_engine": "subscription"})
    contract.with_user(s.manager).write({"billing_engine": "subscription"})
    sub = _sub(s, contract_id=contract.id)
    # vice versa: the walker never bills it, and cannot take it back while M39 does
    Period = s.env["fix.contract.billing.period"]
    assert Period._bill_contract(contract, contract.date_end) == 0
    with pytest.raises(UserError, match="billed by its M39 subscription"), s.env.cr.savepoint():
        Period.create(
            {
                "contract_id": contract.id,
                "period_start": s.today,
                "period_end": s.today + timedelta(days=30),
                "amount": 10000.0,
            }
        )
    with pytest.raises(UserError, match="live M39 subscription"), s.env.cr.savepoint():
        contract.with_user(s.manager).write({"billing_engine": "walker"})
    assert sub.contract_id == contract


def test_f11_a_managed_services_contract_is_billed_by_m39_per_d8(s):
    contract = _contract(s, family="managed")
    assert contract.billing_engine == "subscription"
    _sub(s, contract_id=contract.id)


def test_f11_a_contract_already_walker_billed_does_not_move_to_m39(s):
    contract = _contract(s)
    s.env["fix.contract.billing.period"].create(
        {
            "contract_id": contract.id,
            "period_start": s.today,
            "period_end": s.today + timedelta(days=30),
            "amount": 10000.0,
        }
    )
    with pytest.raises(UserError, match="move it to M39 at renewal"), s.env.cr.savepoint():
        contract.with_user(s.manager).write({"billing_engine": "subscription"})


def test_f11_activation_creates_a_subscription_only_for_an_m39_contract(s):
    Sub = s.env["fix.subscription"]
    walker = _contract(s, state="active")
    assert "skipped" in Sub.consume_contract_activated({"aggregate_id": walker.id})
    assert not Sub.search([("contract_id", "=", walker.id)])
    m39 = _contract(s, state="active", billing_engine="subscription")
    out = Sub.consume_contract_activated({"aggregate_id": m39.id})
    sub = Sub.browse(out["created"])
    assert (sub.contract_id, sub.recurring_amount, sub.billing_cycle) == (m39, 10000.0, "monthly")
    assert sub.contract_end_date == m39.date_end
    again = Sub.consume_contract_activated({"aggregate_id": m39.id})
    assert again == {"existing": sub.id}
    with pytest.raises(AccessError):
        Sub.with_user(s.officer).consume_contract_activated({"aggregate_id": m39.id})


# ------------------------------------------------------------ M37-F5 (with R2-3)
def test_m37_f5_a_subscription_from_a_plan_takes_its_cycle_and_m11_price(s):
    env = s.env
    params = env["ir.config_parameter"].sudo()
    params.set_param("cd_rate_card.margin_floor_pct", "0")
    params.set_param("cd_rate_card.max_channel_spread_pct", "")
    params.set_param("cd_rate_card.margin_target_pct", "")
    code = "R2SUB-%s" % uuid.uuid4().hex[:6].upper()
    tmpl = env["product.template"].create({"name": "Plan %s" % code, "default_code": code})
    item = env["fix.catalogue.item"].create(
        {"product_tmpl_id": tmpl.id, "item_type": "subscription", "vat_class": "standard_15"}
    )
    item._guarded().write({"state": "approved"})
    plan = env["fix.subscription.plan.def"].create(
        {"item_id": item.id, "billing_frequency": "quarterly", "commitment_months": 12}
    )
    vals = {
        "name": "R2 plan sub %s" % code,
        "customer_id": s.partner.id,
        "operating_unit_id": s.ou.id,
        "plan": "standard",
        "start_date": s.today,
        "next_invoice_date": s.today,
        "plan_def_id": plan.id,
    }
    Sub = env["fix.subscription"]
    with pytest.raises(UserError, match="no released M11 price"), env.cr.savepoint():
        Sub.create(dict(vals))
    card = env["fix.rate.card"].create(
        {"product_code": code, "unit_price": 2400.0, "line_type": "labour"}
    )
    card._guarded().write({"state": "released"})
    sub = Sub.create(dict(vals))
    assert (sub.billing_cycle, sub.recurring_amount, sub.plan_def_id) == ("quarterly", 2400.0, plan)
    # an explicit amount is the amount typed (the plan only sets what is missing)
    typed = Sub.create(dict(vals, name="typed %s" % code, recurring_amount=999.0))
    assert typed.recurring_amount == 999.0
    with pytest.raises(UserError, match="set when it is created"), env.cr.savepoint():
        sub.with_user(s.acct).write({"plan_def_id": False})


# ------------------------------------------------------------ wiring
class TestDeployment:
    def test_consumers_fields_and_surfaces_exist(self, odoo_env):
        env = odoo_env
        Consumer = env["fix.event.consumer"].sudo()
        for event_type, method in (
            ("msp.usage_reported", "consume_msp_usage_reported"),
            ("data.usage_reported", "consume_data_usage_reported"),
            ("rental.usage_reported", "consume_rental_usage_reported"),
            ("subscription.service_order_locked", "consume_service_gate_event"),
            ("subscription.paused", "consume_service_gate_event"),
            ("subscription.cancelled", "consume_service_gate_event"),
            ("subscription.cancel_applied", "consume_service_gate_event"),
            ("subscription.churned", "consume_service_gate_event"),
            ("subscription.reinstated", "consume_service_gate_event"),
            ("subscription.resumed", "consume_service_gate_event"),
            ("contract.activated", "consume_contract_activated"),
        ):
            assert Consumer.search_count(
                [("event_type", "=", event_type), ("method", "=", method)]
            ), event_type
        assert "billing_engine" in env["fix.contract"]._fields
        from odoo.addons.cd_p03_portal.controllers.a04 import m39

        assert "action_send_price_notice" in m39.SURFACES["fix.subscription.proration"]["actions"]
