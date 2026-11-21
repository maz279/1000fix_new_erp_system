# The alerts the workspace text promised. Each event must reach a person.
from __future__ import annotations

import itertools
import json

import pytest
from odoo.addons.cd_asset_workorder_spine.models.fix_asset_alert import ROUTES
from odoo.exceptions import UserError

_SEQ = itertools.count(1)


def _user(env, *groups):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A07 Alert %s" % n,
                "login": "a07-alert-%s" % n,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _event(event_type, aggregate="res.partner", aggregate_id=0, event_id="e1"):
    return {
        "event_id": event_id,
        "event_type": event_type,
        "aggregate": aggregate,
        "aggregate_id": aggregate_id,
        "payload": {},
    }


def _routed():
    # A07 ERP audit (2026-11-20) M48-15/18: the M48 events routed to the owner of
    # the asset (fix_m48_routing.ROUTED_TEXT) are consumed here too
    from odoo.addons.cd_asset_workorder_spine.models.fix_m48_routing import ROUTED_TEXT

    return set(ROUTES) | set(ROUTED_TEXT)


# what makes a gated event a routed one (M47-17: _route reads the payload)
_ROUTING_PAYLOAD = {
    "site.outage": {"branch_stopped": True},
    "site.status_changed": {"to_status": "closed"},
}


def test_every_routed_event_has_a_consumer_and_a_real_role(odoo_env):
    from odoo.addons.cd_asset_workorder_spine.models.fix_m48_routing import OWNER_ROLE

    # A07 ERP finishing pass (R2b): inactive records too, so a consumer that is
    # registered but switched off is caught instead of silently not listed
    consumers = (
        odoo_env["fix.event.consumer"]
        .sudo()
        .with_context(active_test=False)
        .search([("method", "=", "consume_asset_alert")])
    )
    routed = _routed()
    # no routed event without a consumer, no consumer for an event nobody routes
    assert set(consumers.mapped("event_type")) == routed
    for event_type in sorted(routed):
        mine = consumers.filtered(lambda c, e=event_type: c.event_type == e)
        assert mine.filtered("active"), "%s has no ACTIVE consumer" % event_type
        assert set(mine.mapped("model")) == {"fix.asset.alert"}, event_type
    for _module, group, _text in ROUTES.values():
        assert odoo_env.ref(group, raise_if_not_found=False), group
    for group in OWNER_ROLE.values():
        assert odoo_env.ref(group, raise_if_not_found=False), group


def test_every_routed_event_reaches_an_alert_through_its_consumer(odoo_env):
    """Each routed event, handed to its active consumer record as the relay hands
    it, leaves one open alert row (the consumer is wired, not just listed)."""
    env = odoo_env
    Relay = env["fix.event.outbox"].sudo()
    consumers = env["fix.event.consumer"].sudo().search([("method", "=", "consume_asset_alert")])
    partner = env["res.partner"].create({"name": "A07 Routed Subject"})
    for n, event_type in enumerate(sorted(_routed()), start=1):
        sub = consumers.filtered(lambda c, e=event_type: c.event_type == e)[:1]
        row = Relay.create(
            {
                "event_type": event_type,
                "aggregate": "res.partner",
                "aggregate_id": partner.id,
                "payload": json.dumps(_ROUTING_PAYLOAD.get(event_type, {})),
                "event_id": "a07-routed-%s" % n,
            }
        )
        assert Relay._relay_deliver(sub, row) == "", event_type
        alerts = env["fix.asset.alert"].search(
            [("event_type", "=", event_type), ("res_id", "=", partner.id)]
        )
        assert alerts and set(alerts.mapped("state")) == {"open"}, event_type


def test_an_expiring_document_gives_each_role_holder_a_to_do(odoo_env):
    env = odoo_env
    officer = _user(env, "fleet.fleet_group_user")
    partner = env["res.partner"].create({"name": "A07 Subject"})
    assert env["fix.asset.alert"].consume_asset_alert(
        _event("vehicle.document_expiring", aggregate_id=partner.id)
    )
    alert = env["fix.asset.alert"].search(
        [("event_type", "=", "vehicle.document_expiring"), ("res_id", "=", partner.id)]
    )
    assert alert.module == "M46" and alert.state == "open" and not alert.no_holder
    assert officer in alert.activity_ids.mapped("user_id")
    assert "A07 Subject" in alert.name


def test_a_repeat_counts_on_the_open_alert_instead_of_raising_another(odoo_env):
    env = odoo_env
    partner = env["res.partner"].create({"name": "A07 Repeat"})
    for event_id in ("e1", "e2"):
        env["fix.asset.alert"].consume_asset_alert(
            _event("site.compliance_expiring", aggregate_id=partner.id, event_id=event_id)
        )
    alert = env["fix.asset.alert"].search(
        [("event_type", "=", "site.compliance_expiring"), ("res_id", "=", partner.id)]
    )
    assert len(alert) == 1 and alert.raise_count == 2


def test_an_alert_with_no_role_holder_says_so(odoo_env):
    env = odoo_env
    group = env.ref("cd_facility.group_branch_operations_lead").sudo()
    group.write({"user_ids": [(5, 0, 0)]})
    partner = env["res.partner"].create({"name": "A07 Nobody"})
    env["fix.asset.alert"].consume_asset_alert(
        _event("site.compliance_expired", aggregate_id=partner.id)
    )
    alert = env["fix.asset.alert"].search(
        [("event_type", "=", "site.compliance_expired"), ("res_id", "=", partner.id)]
    )
    assert alert.no_holder is True and not alert.activity_ids


def test_only_the_role_may_acknowledge_and_it_closes_the_to_dos(odoo_env):
    env = odoo_env
    officer = _user(env, "fleet.fleet_group_user")
    plain = _user(env)
    partner = env["res.partner"].create({"name": "A07 Ack"})
    env["fix.asset.alert"].consume_asset_alert(
        _event("driver.licence_expiring", aggregate_id=partner.id)
    )
    alert = env["fix.asset.alert"].search(
        [("event_type", "=", "driver.licence_expiring"), ("res_id", "=", partner.id)]
    )
    with pytest.raises(UserError, match="role"), env.cr.savepoint():
        alert.with_user(plain).action_acknowledge()
    alert.with_user(officer).action_acknowledge()
    assert alert.state == "acknowledged" and alert.acknowledged_by_id == officer
    assert not alert.activity_ids


def test_an_alert_cannot_be_typed(odoo_env):
    env = odoo_env
    plain = _user(env)
    partner = env["res.partner"].create({"name": "A07 Typed"})
    env["fix.asset.alert"].consume_asset_alert(
        _event("lease.critical_date_due", aggregate_id=partner.id)
    )
    alert = env["fix.asset.alert"].search(
        [("event_type", "=", "lease.critical_date_due"), ("res_id", "=", partner.id)]
    )
    with pytest.raises(Exception, match="(?i)access|allowed"), env.cr.savepoint():
        alert.with_user(plain).write({"state": "acknowledged"})
