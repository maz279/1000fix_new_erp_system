"""party.merged re-points open service orders and device owners (A03 audit M33-5, R8).

The merge is executed by a non-admin data steward through the real
fix.party.merge.action_execute(); the consumers are then driven both directly
(for idempotency and the reversed-merge case) and through the relay cron.
"""

from datetime import timedelta

import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

STEWARD = "cd_party_master.group_party_data_steward"


@pytest.fixture
def env(odoo_env):
    return odoo_env


def _branch(env):
    branch = env["fix.branch"].search([], limit=1)
    if branch:
        return branch
    unit = env["operating.unit"].search([], limit=1) or env["operating.unit"].create(
        {"name": "P2 Merge Unit", "code": "P2MU"}
    )
    entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
        {
            "legal_name": "1000FiX Group Ltd",
            "code": "P2GRP",
            "company_id": env.company.id,
            "operating_unit_id": unit.id,
        }
    )
    return env["fix.branch"].create(
        {
            "name": "P2 Merge Hub",
            "code": "P2-HUB",
            "entity_id": entity.id,
            "operating_unit_id": unit.id,
        }
    )


def _order(env, customer, device, branch):
    return env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "P2 merge probe",
        }
    )


def _merge_and_execute(env):
    victim = env["res.partner"].create({"name": "P2 SO Victim", "phone": "01755500001"})
    survivor = env["res.partner"].create({"name": "P2 SO Survivor", "phone": "01755500001"})
    brand = env["fix.brand"].create({"name": "P2 Merge Brand", "code": "P2MB"})
    model = env["fix.device.model"].create({"name": "P2 Merge Phone", "brand_id": brand.id})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": victim.id, "serial_number": "P2-MERGE-1"}
    )
    branch = _branch(env)
    open_order = _order(env, victim, device, branch)
    closed_order = _order(env, victim, device, branch)
    env.flush_all()
    # History, not an open document (test surgery: skips the state machine).
    env.cr.execute(
        "UPDATE fix_service_order SET state = 'closed' WHERE id = %s", (closed_order.id,)
    )
    closed_order.invalidate_recordset()
    steward = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "P2 SO Steward",
                "login": "p2.so.steward@a03.test",
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            env.ref("base.group_user").id,
                            env.ref("base.group_partner_manager").id,
                            env.ref(STEWARD).id,
                        ],
                    )
                ],
            }
        )
    )
    merge = env["fix.party.merge"].create({"survivor_id": survivor.id, "victim_id": victim.id})
    # A03 audit W4: the steward executes the merge from the M63 approval inbox.
    approve_via_inbox(merge, steward)
    event = env["fix.event.outbox"].search(
        [("event_type", "=", "party.merged"), ("aggregate_id", "=", survivor.id)],
        order="id desc",
        limit=1,
    )
    return {
        "victim": victim,
        "survivor": survivor,
        "device": device,
        "open": open_order,
        "closed": closed_order,
        "merge": merge,
        "steward": steward,
        "event": event,
    }


@pytest.fixture
def merged(env):
    return _merge_and_execute(env)


def test_open_orders_and_devices_follow_the_survivor_idempotently(env, merged):
    event = merged["event"]._relay_event_dict()
    assert env["fix.service.order"].consume_party_merged(event) == 1
    assert env["fix.device"].consume_party_merged(event) == 1
    assert merged["open"].customer_id == merged["survivor"]
    assert merged["closed"].customer_id == merged["victim"]  # history stays
    assert merged["device"].owner_id == merged["survivor"]
    assert env["fix.service.order"].consume_party_merged(event) == 0
    assert env["fix.device"].consume_party_merged(event) == 0


def test_a_reversed_merge_is_not_repointed(env, merged):
    event = merged["event"]._relay_event_dict()
    merged["merge"].with_user(merged["steward"]).action_reverse()
    assert env["fix.service.order"].consume_party_merged(event) == 0
    assert env["fix.device"].consume_party_merged(event) == 0
    assert merged["open"].customer_id == merged["victim"]


def test_the_relay_delivers_to_both_consumers(env):
    Consumer = env["fix.event.consumer"]
    mine = Consumer.search(
        [("event_type", "=", "party.merged"), ("module", "=", "cd_service_order")]
    )
    # A03 audit W1 added the running SLA clocks.
    assert set(mine.mapped("model")) == {"fix.service.order", "fix.device", "fix.sla.kpi.instance"}
    (Consumer.search([]) - mine).write({"active": False})
    mine.write({"active_from": env.cr.now() - timedelta(minutes=1)})
    data = _merge_and_execute(env)  # after the consumers start
    env["fix.event.outbox"].cron_relay()
    deliveries = env["fix.event.consumer.delivery"].search([("event_id", "=", data["event"].id)])
    assert len(deliveries) == 3 and set(deliveries.mapped("state")) == {"done"}
    assert (
        data["open"].customer_id == data["survivor"] and data["device"].owner_id == data["survivor"]
    )
