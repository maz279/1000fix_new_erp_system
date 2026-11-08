"""A07 operability, the M48 half of the spine: what a preventive request and a
dispatched action do once they reach the work-order spine.

Live ORM, rolled back. Events go through the relay's own delivery path, and the
people are non-admin users with the role they would really hold."""

from __future__ import annotations

import pytest
from odoo.addons.cd_asset_workorder_spine.tests.test_a07_p1_spine import (
    DEMAND,
    FM,
    REFUSED,
    WO,
    _deliver,
    _dispatch,
    _m48,
    _run_wo,
    c,  # noqa: F401 - the fixture
)

OPERATOR = "cd_stream_registry.group_iot_operator"


@pytest.fixture
def op(c):  # noqa: F811
    env = c.env
    groups = [env.ref("base.group_user").id, env.ref(OPERATOR).id]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "a07m48spine_operator",
                "login": "a07m48spine_operator",
                "group_ids": [(6, 0, groups)],
                "assigned_operating_unit_ids": [(6, 0, c.ou.ids)],
                "default_operating_unit_id": c.ou.id,
            }
        )
    )


def _demand(c, p):  # noqa: F811
    return c.env[DEMAND].search([("prediction_id", "=", p.id)], order="id desc")


def _waiting_prediction(c):  # noqa: F811
    """A prediction whose demand cannot route itself: its device has no site and
    its equipment no branch, so the demand waits for a person."""
    e, p = _m48(c)
    c.env["fix.iot.device"].search([("equipment_id", "=", e.id)]).write({"site_id": False})
    e.write({"branch_id": False})
    return p


def test_15_dismissing_the_demand_frees_the_request(c, op):  # noqa: F811
    env = c.env
    p = _waiting_prediction(c)
    p.with_user(op).action_create_preventive_wo()
    assert p.work_order_created is True
    _deliver(c, "predictive_maintenance.wo_created", p)
    first = _demand(c, p)
    assert len(first) == 1 and first.state == "pending"
    # while it is live, a second request is refused
    with pytest.raises(REFUSED), env.cr.savepoint():
        p.with_user(op).action_create_preventive_wo()
    first.with_user(c.fm).action_dismiss("the asset is being retired")
    assert first.state == "dismissed"
    assert p.work_order_created is False, "the flag followed the dismissal"
    assert any("retired" in str(b) for b in p.message_ids.mapped("body"))
    # the request can be made again, and it raises a new demand
    p.with_user(op).action_create_preventive_wo()
    assert p.work_order_created is True
    _deliver(c, "predictive_maintenance.wo_created", p)
    demands = _demand(c, p)
    assert len(demands) == 2
    assert demands[0].state == "pending" and demands[0].source_key != first.source_key
    # the redelivered event raises nothing more
    _deliver(c, "predictive_maintenance.wo_created", p)
    assert len(_demand(c, p)) == 2


def test_15_a_redelivered_event_after_dismissal_raises_nothing(c, op):  # noqa: F811
    p = _waiting_prediction(c)
    p.with_user(op).action_create_preventive_wo()
    _deliver(c, "predictive_maintenance.wo_created", p)
    first = _demand(c, p)
    first.with_user(c.fm).action_dismiss("not needed")
    _deliver(c, "predictive_maintenance.wo_created", p)
    assert _demand(c, p) == first


def test_15_the_flag_is_labelled_for_what_it_means(c):  # noqa: F811
    field = c.env["fix.predictive.maintenance"]._fields["work_order_created"]
    assert "Requested" in field.string


def test_completing_an_action_waits_for_its_order(c, op):  # noqa: F811
    _e, p = _m48(c)
    a = _dispatch(c, p)
    _deliver(c, "iot.action_dispatched", a)
    wo = c.env[WO].search([("iot_action_id", "=", a.id)])
    assert wo and wo.state in ("draft", "scheduled", "in_progress")
    a.write({"outcome_evidence_ref": "JC-9"})
    with pytest.raises(REFUSED, match=wo.name), c.env.cr.savepoint():
        a.with_user(op).action_done(outcome="confirmed", note="found")
    assert a.state == "dispatched" and p.outcome == "pending"
    _run_wo(c, wo, notes="Bearing replaced")
    assert wo.state == "completed"
    with pytest.raises(REFUSED, match=wo.name), c.env.cr.savepoint():
        a.with_user(op).action_done(outcome="confirmed", note="found")
    wo.with_user(c.fm2).action_verify()
    a.with_user(op).action_done(outcome="confirmed", note="found")
    assert a.state == "done" and p.outcome == "confirmed"


def test_an_action_cannot_finish_while_its_demand_has_no_order(c, op):  # noqa: F811
    """The journeys on live data finished an action, and recorded its finding as confirmed,
    with its demand still waiting for a site and no order ever raised."""
    e, p = _m48(c)
    c.env["fix.iot.device"].search([("equipment_id", "=", e.id)]).write({"site_id": False})
    e.write({"branch_id": False})
    a = _dispatch(c, p)
    _deliver(c, "iot.action_dispatched", a)
    demand = c.env["fix.maintenance.demand"].search([("iot_action_id", "=", a.id)])
    assert demand.state == "pending" and not demand.work_order_id
    a.write({"outcome_evidence_ref": "JC-9"})
    with pytest.raises(REFUSED, match="has no order yet"), c.env.cr.savepoint():
        a.with_user(op).action_done(outcome="confirmed", note="found")
    assert a.state == "dispatched" and p.outcome == "pending"


def test_an_action_with_no_routed_order_completes(c, op):  # noqa: F811
    _e, p = _m48(c)
    a = _dispatch(c, p)
    a.write({"outcome_evidence_ref": "JC-9"})
    a.with_user(op).action_done(outcome="not_confirmed", note="nothing found")
    assert a.state == "done" and p.outcome == "false_alarm"


def test_the_facility_manager_role_is_still_what_dismisses(c, op):  # noqa: F811
    assert c.env.ref(FM)
    p = _waiting_prediction(c)
    p.with_user(op).action_create_preventive_wo()
    _deliver(c, "predictive_maintenance.wo_created", p)
    with pytest.raises(REFUSED), c.env.cr.savepoint():
        _demand(c, p).with_user(op).action_dismiss("not mine to dismiss")
    assert p.work_order_created is True
