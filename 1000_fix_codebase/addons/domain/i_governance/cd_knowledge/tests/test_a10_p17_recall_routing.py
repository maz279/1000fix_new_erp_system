# A10 remediation (2026-11-05), P1-7: recall routing (M61-4).
#
# The audit distributed a HIGH recall with no affected models and nothing
# sent, let any user close it or downgrade it to LOW with a plain write, and
# routed nothing to M09 or M01. Now: a recall distributes only over what it
# recalls (models or serials) to NAMED branches; each branch acknowledges its
# own line (its duty officer, or its own staff when the employee record
# carries the branch); severity and type LOCK at distribution; closure is the
# Quality Manager's, and only over branches that answered; and distribution
# itself hands the recall to M09 as an active warranty campaign and flags
# M01's open orders on the affected models — through the event relay, not a
# promise. Every control is exercised as non-admin users; the superuser is
# trusted only where the relay is.
import itertools
import json
from unittest import mock

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError
from psycopg2 import IntegrityError

PUBLISHER = "cd_knowledge.group_knowledge_publisher"
QM_GROUP = "cd_qms_process.group_qms_quality_manager"
GUARD = "changes only through its workflow"
MODEL_NAME = "A10P17 Z14"

_SEQ = itertools.count(1)


def _user(env, name, groups=()):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 P17 %s %d" % (name, n),
                "login": "a10p17.%s.%d@a10.test" % (name.replace(" ", "").lower(), n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )


def _emp(env, user, name):
    return env["hr.employee"].create({"name": "A10 P17 %s" % name, "user_id": user.id})


def _ou(env, label):
    n = next(_SEQ)
    return env["operating.unit"].create(
        {
            "name": "A10 P17 %s %d" % (label, n),
            "code": ("P17-%s-%d" % (label[:3].upper(), n))[:16],
            "company_id": env.company.id,
            "partner_id": env["res.partner"].create({"name": "A10 P17 %s %d" % (label, n)}).id,
        }
    )


def _bulletin(env, **kw):
    vals = {
        "brand": "Zeltrix",
        "bulletin_type": "recall",
        "severity": "high",
        "affected_models": MODEL_NAME,
        "serial_scope": "SN-9001..SN-9050",
    }
    vals.update(kw)
    return env["fix.knowledge.bulletin"].create(vals)


def _recipients(rec, env, ou_a, officer_emp, ou_b=None, officer_b_emp=None):
    Recipient = env["fix.knowledge.bulletin.recipient"]
    a = Recipient.create(
        {"bulletin_id": rec.id, "branch_id": ou_a.id, "employee_id": officer_emp.id}
    )
    b = False
    if ou_b:
        vals = {"bulletin_id": rec.id, "branch_id": ou_b.id}
        if officer_b_emp:
            vals["employee_id"] = officer_b_emp.id
        b = Recipient.create(vals)
    return a, b


@pytest.fixture
def m(odoo_env):
    env = odoo_env
    x = lambda: None  # noqa: E731  (tiny namespace)
    x.env = env
    x.clerk = _user(env, "clerk")
    x.publisher = _user(env, "publisher", [PUBLISHER])
    x.qm = _user(env, "qm", [QM_GROUP])
    x.officer = _user(env, "officer")
    x.officer_emp = _emp(env, x.officer, "Duty Officer A")
    x.bstaff = _user(env, "bstaff")
    x.ou_a = _ou(env, "Branch A")
    x.ou_b = _ou(env, "Branch B")
    return x


# ------------------------------------------------------- the distribution gate
def test_a_recall_distributes_only_over_what_it_recalls_to_named_branches(m):
    env = m.env
    rec = _bulletin(env, affected_models="", serial_scope="")
    with pytest.raises(UserError, match="Only a Knowledge Publisher"):
        rec.with_user(m.clerk).action_distribute()
    with pytest.raises(UserError, match=r"Link .* to what it recalls"):
        rec.with_user(m.publisher).action_distribute()
    rec.affected_models = MODEL_NAME
    rec.serial_scope = "SN-9001..SN-9050"
    with pytest.raises(UserError, match="Name the recipient branch"):
        rec.with_user(m.publisher).action_distribute()
    _recipients(rec, env, m.ou_a, m.officer_emp, ou_b=m.ou_b)
    rec.with_user(m.publisher).action_distribute()
    assert rec.state == "distributed"
    assert (rec.recipients_total, rec.recipients_acknowledged) == (2, 0)
    # the distribution is an event the estate can consume — with the scope it
    # carried, not a bare status word
    events = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", "bulletin.distributed"),
                ("aggregate_id", "=", rec.id),
            ]
        )
    )
    assert len(events) == 1
    payload = json.loads(events[0].payload)
    assert payload["bulletin_type"] == "recall"
    assert payload["severity"] == "high"
    assert payload["affected_models"] == MODEL_NAME
    assert payload["serial_scope"] == "SN-9001..SN-9050"
    assert [r["operating_unit"] for r in payload["recipients"]] == [
        m.ou_a.name,
        m.ou_b.name,
    ]


def test_the_classification_locks_at_distribution(m):
    env = m.env
    rec = _bulletin(env)
    # before distribution the classification is the publisher's to fix
    rec.with_user(m.publisher).write({"severity": "medium"})
    assert rec.severity == "medium"
    rec.with_user(m.publisher).write({"severity": "high"})
    _recipients(rec, env, m.ou_a, m.officer_emp)
    rec.with_user(m.publisher).action_distribute()
    # the field acted on 'high recall': rewriting it afterwards rewrites history
    with pytest.raises(UserError, match="locked while distributed"):
        rec.with_user(m.publisher).write({"severity": "low"})
    with pytest.raises(UserError, match="locked while distributed"):
        rec.with_user(m.publisher).write({"bulletin_type": "technical"})
    # superuser code (the relay, crons) is trusted
    rec.sudo().write({"summary": "Refreshed wording"})
    assert "Refreshed wording" in rec.summary
    # the state itself remains the actions' alone
    with pytest.raises(UserError, match=GUARD):
        rec.with_user(m.publisher).write({"state": "closed"})
    rec.with_user(m.officer).action_acknowledge()
    rec.with_user(m.qm).action_close("Field swapped all affected batteries")
    assert rec.state == "closed"
    with pytest.raises(UserError, match="locked while closed"):
        rec.with_user(m.publisher).write({"severity": "low"})


# ------------------------------------------------------- the acknowledgement
def test_acknowledgement_is_the_branchs_own_act(m):
    env = m.env
    rec = _bulletin(env)
    a, b = _recipients(rec, env, m.ou_a, m.officer_emp, ou_b=m.ou_b)
    # nobody acknowledges what was not distributed
    with pytest.raises(UserError, match="acknowledges a distributed bulletin"):
        rec.with_user(m.officer).action_acknowledge()
    rec.with_user(m.publisher).action_distribute()
    # a clerk with no employee record holds nothing
    with pytest.raises(UserError, match=r"Only .* acknowledges"):
        rec.with_user(m.clerk).action_acknowledge(recipient_id=a.id)
    # branch A's duty officer answers for branch A — and only for branch A
    with pytest.raises(UserError, match=r"Only .* acknowledges"):
        rec.with_user(m.officer).action_acknowledge(recipient_id=b.id)
    rec.with_user(m.officer).action_acknowledge(recipient_id=a.id)
    assert a.acknowledged_on == fields.Date.context_today(a)
    assert a.acknowledged_by_id == m.officer
    assert rec.recipients_acknowledged == 1
    # the stamp is never typed
    with pytest.raises(UserError, match=GUARD):
        b.with_user(m.clerk).write({"acknowledged_on": fields.Date.today()})
    # branch B: its own staff answer when the employee record carries the
    # branch (hr.employee.operating_unit_id); a branch nobody of B holds does not
    bstaff_emp = _emp(env, m.bstaff, "Branch B Staff")
    if "operating_unit_id" in env["hr.employee"]._fields:
        bstaff_emp.operating_unit_id = m.ou_b.id
        rec.with_user(m.bstaff).action_acknowledge(recipient_id=b.id)
        assert b.acknowledged_on and b.acknowledged_by_id == m.bstaff
    else:
        with pytest.raises(UserError, match=r"Only .* acknowledges"):
            rec.with_user(m.bstaff).action_acknowledge(recipient_id=b.id)
        b.employee_id = _emp(env, m.clerk, "Duty Officer B").id
        rec.with_user(m.clerk).action_acknowledge(recipient_id=b.id)
    assert rec.recipients_acknowledged == 2
    # re-acknowledging changes nothing
    rec.with_user(m.officer).action_acknowledge(recipient_id=a.id)
    assert rec.recipients_acknowledged == 2
    # one line per branch per bulletin — the second line for A is a typo
    with pytest.raises(IntegrityError), env.cr.savepoint(), mock.patch("odoo.sql_db._logger"):
        env["fix.knowledge.bulletin.recipient"].create(
            {"bulletin_id": rec.id, "branch_id": m.ou_a.id}
        )


# ------------------------------------------------------------- the closure
def test_the_quality_manager_closes_what_the_branches_acknowledged(m):
    env = m.env
    rec = _bulletin(env)
    officer_b = _emp(env, m.bstaff, "Duty Officer B")
    a, b = _recipients(rec, env, m.ou_a, m.officer_emp, ou_b=m.ou_b, officer_b_emp=officer_b)
    rec.with_user(m.publisher).action_distribute()
    # the publisher who distributed it cannot close it
    with pytest.raises(UserError, match="Only the Quality Manager"):
        rec.with_user(m.publisher).action_close("Done")
    # and the Quality Manager cannot close unanswered branches
    rec.with_user(m.officer).action_acknowledge(recipient_id=a.id)
    with pytest.raises(UserError, match="have not acknowledged"):
        rec.with_user(m.qm).action_close("Done")
    assert rec.state == "distributed"
    rec.with_user(m.bstaff).action_acknowledge(recipient_id=b.id)
    with pytest.raises(UserError, match="State the closure note"):
        rec.with_user(m.qm).action_close()
    rec.with_user(m.qm).action_close("Both branches swapped the affected batteries")
    assert rec.state == "closed"
    with pytest.raises(UserError, match=r"Distribute .* before closing"):
        rec.with_user(m.qm).action_close("again")
    # a non-recall bulletin stays the publisher's to close — with the note
    tech = _bulletin(env, bulletin_type="technical", affected_models="", serial_scope="")
    tech.with_user(m.publisher).action_distribute()
    tech.with_user(m.publisher).action_close("Torque table circulated")
    assert tech.state == "closed"
    tech2 = _bulletin(env, bulletin_type="technical", affected_models="", serial_scope="")
    tech2.with_user(m.publisher).action_distribute()
    with pytest.raises(UserError, match="Only a Knowledge Publisher"):
        tech2.with_user(m.qm).action_close("not mine")


# ------------------------------------------------------- the routing itself
def _order_device_chain(env):
    brand = env["fix.brand"].search([("name", "=", "Zeltrix")], limit=1) or env["fix.brand"].create(
        {"name": "Zeltrix", "code": "ZLX"}
    )
    device_model = env["fix.device.model"].search(
        [("name", "=", MODEL_NAME), ("brand_id", "=", brand.id)], limit=1
    ) or env["fix.device.model"].create({"name": MODEL_NAME, "brand_id": brand.id})
    return brand, device_model


def test_m09_opens_the_recall_campaign_from_the_relay(m):
    env = m.env
    brand, _device_model = _order_device_chain(env)
    rec = _bulletin(env)
    _recipients(rec, env, m.ou_a, m.officer_emp, ou_b=m.ou_b)
    rec.with_user(m.publisher).action_distribute()
    # the wiring is registered, not implied
    consumers = (
        env["fix.event.consumer"].sudo().search([("event_type", "=", "bulletin.distributed")])
    )
    assert {c.method for c in consumers} >= {"consume_bulletin_distributed"}
    handled = env["fix.event.outbox"].sudo().cron_relay()
    assert handled >= 1
    campaign = env["fix.warranty.recall"].sudo().search([("bulletin_id", "=", rec.id)])
    assert len(campaign) == 1
    assert campaign.state == "active"
    assert campaign.launched_on == fields.Date.context_today(campaign)
    assert campaign.brand_id == brand
    assert MODEL_NAME in campaign.product_ref and "SN-9001..SN-9050" in campaign.product_ref
    assert campaign.affected_units == 0  # the bulletin states scope, not a unit count
    # redelivery is the relay's reality — the campaign is not duplicated
    env["fix.event.outbox"].sudo().cron_relay()
    assert len(env["fix.warranty.recall"].sudo().search([("bulletin_id", "=", rec.id)])) == 1
    # the consumer is the relay's, not an RPC
    with pytest.raises(AccessError, match="run only from the event relay"):
        env["fix.warranty.recall"].with_user(m.clerk).consume_bulletin_distributed(
            {
                "event_type": "bulletin.distributed",
                "aggregate": "fix.knowledge.bulletin",
                "aggregate_id": rec.id,
                "payload": {"bulletin_type": "recall"},
                "company_id": env.company.id,
            }
        )


def test_m01_flags_open_orders_on_the_recalled_models(m):
    env = m.env
    _brand, device_model = _order_device_chain(env)
    n = next(_SEQ)
    entity = env["fix.entity"].create(
        {
            "legal_name": "A10 P17 Entity %d" % n,
            "code": ("P17E%d" % n)[:10],
            "company_id": env.company.id,
        }
    )
    branch = env["fix.branch"].create(
        {
            "name": "A10 P17 Branch %d" % n,
            "code": ("P17-BR%d" % n)[:10],
            "entity_id": entity.id,
            "operating_unit_id": _ou(env, "Desk").id,
        }
    )
    customer = env["res.partner"].create({"name": "A10 P17 Customer %d" % n})
    device = env["fix.device"].create(
        {
            "device_model_id": device_model.id,
            "owner_id": customer.id,
            "serial_number": "A10P17-SN-9001",
        }
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "Swollen battery",
        }
    )
    other_model = env["fix.device.model"].create(
        {"name": "A10P17 Other %d" % n, "brand_id": device_model.brand_id.id}
    )
    other_device = env["fix.device"].create(
        {
            "device_model_id": other_model.id,
            "owner_id": customer.id,
            "serial_number": "A10P17-OTHER-%d" % n,
        }
    )
    other_order = env["fix.service.order"].create(
        {
            "device_id": other_device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "Cracked screen",
        }
    )
    rec = _bulletin(env)
    _recipients(rec, env, m.ou_a, m.officer_emp)
    rec.with_user(m.publisher).action_distribute()
    env["fix.event.outbox"].sudo().cron_relay()
    marker = "[recall-bulletin-%d]" % rec.id
    flagged = order.message_ids.filtered(lambda msg, mk=marker: mk in (msg.body or ""))
    assert len(flagged) == 1
    body = flagged[0].body
    assert rec.name in body and "high" in body and "SN-9001..SN-9050" in body
    assert not other_order.message_ids.filtered(lambda msg, mk=marker: mk in (msg.body or ""))
    # the relay may redeliver: the desk heard us once
    env["fix.event.outbox"].sudo().cron_relay()
    assert len(order.message_ids.filtered(lambda msg, mk=marker: mk in (msg.body or ""))) == 1


def test_the_relay_delivered_the_routing_without_error(m):
    """Every delivery of a bulletin.distributed event settles 'done' — a
    recall the relay silently dropped is the audit's 'nothing sent' again."""
    env = m.env
    rec = _bulletin(env)
    _recipients(rec, env, m.ou_a, m.officer_emp)
    rec.with_user(m.publisher).action_distribute()
    env["fix.event.outbox"].sudo().cron_relay()
    event = (
        env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", "bulletin.distributed"),
                ("aggregate_id", "=", rec.id),
            ]
        )
    )
    deliveries = env["fix.event.consumer.delivery"].sudo().search([("event_id", "in", event.ids)])
    assert deliveries and all(d.state == "done" for d in deliveries)
