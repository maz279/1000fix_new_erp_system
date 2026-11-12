"""The order's SLA deadline follows its clock (order rehearsal, 12 Nov 2026).

A resumed clock is a NEW instance with a later deadline (fix.sla.kpi.instance
resume). The order keeps its own copy, sla_resolution_deadline, which was
written once at intake and never again - and it is what the SLA compliance
report, the "SLA at risk" KPI, the technician app, the customer portal's ETA
and the performance scores read. After any hold (and any wait on the
customer's estimate decision, which pauses the clock too) they counted an
on-time order as late.

Also: an estimate had no name source and read "fix.estimate,15" in every
message (the rehearsal's segregation-of-duties refusal named it so).

``odoo_env``: superuser environment on fix_test, rolled back after every test.
"""

from datetime import timedelta
from types import SimpleNamespace

import pytest
from odoo import fields
from odoo.exceptions import UserError


@pytest.fixture
def base(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "SLADL", "legal_name": "SLA Deadline Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {
            "name": "SLA DL Branch",
            "code": "SLADB",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )
    brand = env["fix.brand"].create({"name": "SlaDlBrand", "code": "SLADBR"})
    model = env["fix.device.model"].create({"name": "SlaPhone", "brand_id": brand.id})
    customer = env["res.partner"].create({"name": "SLA DL Customer", "phone": "01711999777"})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": customer.id, "serial_number": "SN-SLADL-1"}
    )
    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "fault_description": "Restarts while charging",
        }
    )
    return SimpleNamespace(env=env, order=order)


def _clock(order):
    return order.env["fix.sla.kpi.instance"].for_record(order, kpi_code="resolution")


def _backdate_pause(env, order, hours):
    """The hold began ``hours`` ago: the guarded stamps are moved in SQL."""
    inst = _clock(order)
    when = fields.Datetime.now() - timedelta(hours=hours)
    env.flush_all()
    env.cr.execute("UPDATE fix_sla_kpi_instance SET paused_at = %s WHERE id = %s", (when, inst.id))
    env.cr.execute(
        "UPDATE fix_service_order SET sla_paused_at = %s WHERE id = %s", (when, order.id)
    )
    env.invalidate_all()
    return inst


def test_intake_writes_the_clocks_deadline_on_the_order(base):
    order = base.order
    order.action_intake()
    clock = _clock(order)
    assert clock and clock.state == "in_progress"
    assert order.sla_resolution_deadline == clock.target_at


def test_a_resumed_hold_moves_the_orders_deadline_with_its_clock(base):
    env, order = base.env, base.order
    order.action_intake()
    first_deadline = order.sla_resolution_deadline

    order.action_defer_order(reason="parts_backorder", notes="Panel on back-order")
    held = _backdate_pause(env, order, hours=2)
    assert held.state == "paused"

    order.action_resume_order()
    successor = _clock(order)
    assert successor.supersedes_id == held and successor.state == "in_progress"
    # the hold costs nothing: the new deadline is about two hours later
    assert successor.target_at - first_deadline >= timedelta(hours=1, minutes=59)
    assert order.sla_resolution_deadline == successor.target_at


def test_a_clock_resumed_from_the_clock_list_moves_the_order_too(base):
    """Live SLA Clocks offers Resume (supervisor) on the clock itself: the
    order follows whichever path resumed it."""
    env, order = base.env, base.order
    order.action_intake()
    first_deadline = order.sla_resolution_deadline
    clock = _clock(order)
    clock.pause("Supervisor check")
    _backdate_pause(env, order, hours=3)
    successor = _clock(order).resume()
    assert successor.target_at - first_deadline >= timedelta(hours=2, minutes=59)
    order.invalidate_recordset()
    assert order.sla_resolution_deadline == successor.target_at


def test_the_at_risk_count_no_longer_counts_a_resumed_order(base):
    """What the KPI asks: open orders past sla_resolution_deadline. With the
    stale intake deadline a resumed order whose clock still has time read as
    late."""
    env, order = base.env, base.order
    order.action_intake()
    order.action_defer_order(reason="customer_travel")
    _backdate_pause(env, order, hours=5)
    # the intake deadline has passed while the order was on hold
    env.flush_all()
    env.cr.execute(
        "UPDATE fix_sla_kpi_instance SET target_at = %s WHERE id = %s",
        (fields.Datetime.now() + timedelta(hours=1), _clock(order).id),
    )
    env.cr.execute(
        "UPDATE fix_service_order SET sla_resolution_deadline = %s WHERE id = %s",
        (fields.Datetime.now() - timedelta(minutes=1), order.id),
    )
    env.invalidate_all()
    order.action_resume_order()
    late = env["fix.service.order"].search_count(
        [("id", "=", order.id), ("sla_resolution_deadline", "<", fields.Datetime.now())]
    )
    assert late == 0
    assert order.sla_resolution_deadline > fields.Datetime.now()


def test_an_estimate_reads_as_its_order_and_revision(base):
    env, order = base.env, base.order
    est = env["fix.estimate"].create(
        {
            "order_id": order.id,
            "line_ids": [
                (
                    0,
                    0,
                    {"line_type": "part", "description": "Panel", "quantity": 1, "unit_price": 900},
                )
            ],
        }
    )
    assert est.display_name == "%s · Estimate v1" % order.name
    assert "fix.estimate," not in est.display_name


def test_the_preparers_refusal_names_the_estimate_readably(base):
    """The refusal the rehearsal met: it named the estimate "fix.estimate,15"."""
    env, order = base.env, base.order
    clerk = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Estimate Preparer",
                "login": "estimate.preparer@sla-dl.test",
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            env.ref("base.group_user").id,
                            env.ref("cd_service_order.group_so_supervisor").id,
                        ],
                    )
                ],
            }
        )
    )
    est = (
        env["fix.estimate"]
        .with_user(clerk)
        .create(
            {
                "order_id": order.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "line_type": "labour",
                            "description": "Bench",
                            "quantity": 1,
                            "unit_price": 500,
                        },
                    )
                ],
            }
        )
    )
    est.sudo().action_send()
    with pytest.raises(UserError) as info:
        est.with_user(clerk).action_approve()
    message = str(info.value)
    assert "fix.estimate," not in message
    assert "%s · Estimate v1" % order.name in message
