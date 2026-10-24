# cd_consignment live-ORM tests — M03 custody chain (G3-05).
import json
from datetime import date, datetime

import pytest
from odoo.exceptions import UserError

T0 = datetime(2026, 3, 1, 9, 0, 0)


def _at(minutes):
    return datetime(2026, 3, 1, 9, minutes, 0)


def _events(env, event_type, consignment):
    rows = env["fix.event.outbox"].search(
        [
            ("event_type", "=", event_type),
            ("aggregate", "=", "fix.consignment"),
            ("aggregate_id", "=", consignment.id),
        ],
        order="id",
    )
    return [json.loads(row.payload) for row in rows]


@pytest.fixture
def consignment(odoo_env):
    ou = odoo_env["operating.unit"].search([("company_id", "=", odoo_env.company.id)], limit=1)
    return odoo_env["fix.consignment"].create(
        {"operating_unit_id": ou.id, "scheduled_date": T0, "consignment_type": "delivery"}
    )


def _scan(consignment, step, minute, **extra):
    return consignment.env["fix.custody.scan"].create(
        {"consignment_id": consignment.id, "step": step, "scanned_at": _at(minute), **extra}
    )


def test_consignments_are_numbered_from_the_sequence(odoo_env, consignment):
    """Regression: without the fix.consignment sequence every consignment of
    a day was named 'CSG/<today>'."""
    other = consignment.copy()
    prefix = f"CSG/{date.today().year}/"
    assert consignment.name.startswith(prefix)
    assert other.name.startswith(prefix)
    assert other.name != consignment.name


def test_explicit_name_is_kept(odoo_env, consignment):
    named = consignment.copy({"name": "CSG/MANUAL/1"})
    assert named.name == "CSG/MANUAL/1"


def test_no_scans_is_an_intact_empty_chain(consignment):
    assert consignment.state == "draft"
    assert (consignment.chain_broken, consignment.custody_summary) == (False, "no scans")


def test_ordered_chain_with_skips_is_intact(consignment):
    _scan(consignment, "picked_up", 0)
    _scan(consignment, "in_transit", 10)
    _scan(consignment, "delivered", 30)  # hub/out-for-delivery skipped: still monotonic
    assert consignment.chain_broken is False
    assert consignment.custody_summary == "Picked Up -> In Transit -> Delivered"


def test_a_backwards_scan_breaks_the_chain(consignment):
    _scan(consignment, "picked_up", 0)
    _scan(consignment, "hub_scan", 10)
    _scan(consignment, "in_transit", 20)  # went back from hub to transit
    assert consignment.chain_broken is True
    assert consignment.custody_summary == "Picked Up -> Hub Scan -> In Transit"


def test_chain_is_evaluated_in_scan_time_order(consignment):
    # created out of order, but scanned in canonical order: intact
    _scan(consignment, "picked_up", 0)
    _scan(consignment, "delivered", 30)
    _scan(consignment, "in_transit", 15)
    assert consignment.chain_broken is False
    assert consignment.custody_summary == "Picked Up -> In Transit -> Delivered"


def test_chain_must_start_at_pickup_unless_explained(consignment):
    """Regression: the rule never fired (the scan is always among its own
    consignment's custody_ids at constraint time)."""
    with (
        pytest.raises(UserError, match="does not start at pickup needs a named exception"),
        consignment.env.cr.savepoint(),
    ):
        _scan(consignment, "in_transit", 0)


def test_a_named_exception_explains_a_late_start(consignment):
    scan = _scan(consignment, "hub_scan", 0, exception_reason="Customer dropped at hub")
    assert scan.consignment_id.custody_summary == "Hub Scan"


def test_later_links_need_no_exception(consignment):
    _scan(consignment, "picked_up", 0)
    later = _scan(consignment, "out_for_delivery", 5)
    assert later.exception_reason is False


def test_backdating_a_scan_before_the_pickup_is_refused(consignment):
    _scan(consignment, "picked_up", 10)
    with pytest.raises(UserError, match="named exception"), consignment.env.cr.savepoint():
        _scan(consignment, "in_transit", 0)


def test_confirm(consignment):
    consignment.action_confirm()
    assert consignment.state == "confirmed"


def test_lost_consignment_raises_an_incident_event(consignment):
    consignment.action_report_lost()
    assert consignment.state == "lost"
    assert _events(consignment.env, "consignment.lost", consignment) == [
        {"consignment": consignment.name}
    ]


def test_delivery_requires_an_intact_chain(consignment):
    _scan(consignment, "picked_up", 0)
    _scan(consignment, "out_for_delivery", 10)
    _scan(consignment, "in_transit", 20)
    with pytest.raises(UserError, match="custody chain is broken"), consignment.env.cr.savepoint():
        consignment.action_deliver()


def test_delivery_requires_a_terminal_scan(consignment):
    with (
        pytest.raises(UserError, match="terminal 'delivered' custody scan missing"),
        consignment.env.cr.savepoint(),
    ):
        consignment.action_deliver()  # no scans at all
    _scan(consignment, "picked_up", 0)
    _scan(consignment, "out_for_delivery", 10)
    with (
        pytest.raises(UserError, match="terminal 'delivered' custody scan missing"),
        consignment.env.cr.savepoint(),
    ):
        consignment.action_deliver()
    assert consignment.state == "draft"


def test_delivery_on_an_intact_chain(consignment):
    _scan(consignment, "picked_up", 0)
    _scan(consignment, "hub_scan", 10)
    _scan(consignment, "delivered", 20)
    consignment.action_deliver()
    assert consignment.state == "delivered"
    (event,) = _events(consignment.env, "consignment.delivered", consignment)
    assert event["consignment"] == consignment.name
    assert datetime.strptime(event["delivered_at"], "%Y-%m-%d %H:%M:%S")


def test_return_publishes(consignment):
    consignment.action_return()
    assert consignment.state == "returned"
    (event,) = _events(consignment.env, "consignment.returned", consignment)
    assert event["consignment"] == consignment.name
    assert datetime.strptime(event["returned_at"], "%Y-%m-%d %H:%M:%S")
