"""A06 final pass B13: M15 stock.written_off -> M18. The scrapped quantity enters
the e-waste stream as ONE collection per write-off, re-read from the quarantine
record, never from the payload."""

import pytest
from odoo.addons.cd_ewaste.tests.m18_fixtures import M18, refused
from odoo.exceptions import UserError


@pytest.fixture
def m(odoo_env):
    x = M18(odoo_env)
    try:
        yield x
    finally:
        x.close()


def _consumer(m):
    sub = m.env.ref("cd_ewaste.consumer_stock_written_off")
    assert (sub.event_type, sub.model, sub.method) == (
        "stock.written_off",
        "fix.ewaste.collection",
        "consume_stock_written_off",
    )
    return getattr(m.env[sub.model].sudo(), sub.method)


def _scrap(m, state="scrapped", category="battery"):
    env = m.env
    part = env["fix.spare.part"].create(
        {
            "name": "A06F Pack",
            "part_number": "A6EW-%s" % m.customer.id,
            "part_category": category,
            "unit_cost": 100.0,
        }
    )
    location = env["fix.stock.location"].create(
        {"name": "A06F EW Store", "code": "A6EW-%s" % m.customer.id, "location_type": "central"}
    )
    env["fix.stock.onhand"]._apply(part, location, "owned", 5.0, 100.0)
    scrap = env["fix.stock.quarantine"].create(
        {"part_id": part.id, "location_id": location.id, "qty": 3.0}
    )
    if state == "scrapped":
        scrap._do_scrap()
    return scrap


def _event(scrap, **payload):
    return {
        "event_type": "stock.written_off",
        "aggregate": "fix.stock.quarantine",
        "aggregate_id": scrap.id,
        "payload": {"quarantine": scrap.name, **payload},
    }


def test_a_write_off_opens_one_collection(m):
    consume = _consumer(m)
    scrap = _scrap(m)
    col = consume(_event(scrap))
    assert col and col.state == "collected"
    assert (col.source_model, col.source_res_id, col.source_ref) == (
        "fix.stock.quarantine",
        scrap.id,
        scrap.name,
    )
    assert (col.material_type, col.item_count) == ("battery", 3)
    # a repeat delivery is a no-op
    assert consume(_event(scrap)) == col
    assert (
        m.env["fix.ewaste.collection"].search_count(
            [("source_model", "=", scrap._name), ("source_res_id", "=", scrap.id)]
        )
        == 1
    )


def test_a_payload_cannot_invent_a_write_off(m):
    consume = _consumer(m)
    not_scrapped = _scrap(m, state="quarantined")
    assert not consume(_event(not_scrapped))
    assert not consume({"aggregate": "fix.stock.quarantine", "aggregate_id": 99999999})


def test_only_the_relay_runs_it(m):
    scrap = _scrap(m)
    exc = refused(
        m.env,
        lambda: m.env["fix.ewaste.collection"]
        .with_user(m.clerk)
        .consume_stock_written_off(_event(scrap)),
    )
    assert isinstance(exc, UserError)
