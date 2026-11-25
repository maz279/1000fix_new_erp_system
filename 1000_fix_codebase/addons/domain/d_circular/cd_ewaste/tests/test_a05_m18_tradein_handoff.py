"""A05 P2: M14 -> M18 hand-off. A graded grade-E trade-in unit harvested with
target 'recycle' (cd_tradein publishes tradein.harvested) enters the e-waste
stream as ONE collection per trade-in, re-read from the records, never from
the payload; the M18 gates (triage, wipe, dispatch) then apply as usual."""

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


def _harvested(m, tradein, target="recycle", component="board"):
    # trusted set-up: the harvest's own gates are cd_tradein's (its suite)
    return m.env["fix.tradein.harvest"].create(
        {"tradein_id": tradein.id, "component": component, "target": target, "state": "harvested"}
    )


def _event(line, **payload):
    return {
        "event_type": "tradein.harvested",
        "aggregate": "fix.tradein.harvest",
        "aggregate_id": line.id,
        "payload": {"tradein": line.tradein_id.name, "target": line.target, **payload},
    }


def _consumer(m):
    sub = m.env.ref("cd_ewaste.consumer_tradein_harvested_recycle")
    assert (sub.event_type, sub.model, sub.method) == (
        "tradein.harvested",
        "fix.ewaste.collection",
        "consume_tradein_harvested",
    )
    return getattr(m.env[sub.model].sudo(), sub.method)


def _tradein(m):
    return m.env["fix.tradein.request"].create(
        {"customer_id": m.customer.id, "device_id": m.device().id}
    )


def test_recycle_harvest_opens_one_collection_per_tradein(m):
    consume = _consumer(m)
    tradein = _tradein(m)
    line = _harvested(m, tradein)
    col = consume(_event(line))
    assert col and col.state == "collected"
    assert (col.source_model, col.source_res_id, col.source_ref) == (
        "fix.tradein.request",
        tradein.id,
        tradein.name,
    )
    assert col.device_id == tradein.device_id and col.material_type == "phone"
    assert col.company_id == tradein.company_id
    # a repeat, and a second recycle line of the same trade-in, are no-ops
    assert consume(_event(line)) == col
    assert consume(_event(_harvested(m, tradein, component="screen"))) == col
    Col = m.env["fix.ewaste.collection"]
    assert (
        Col.search_count([("source_model", "=", tradein._name), ("source_res_id", "=", tradein.id)])
        == 1
    )


def test_only_a_recycle_target_enters_m18_and_the_payload_is_not_trusted(m):
    consume = _consumer(m)
    tradein = _tradein(m)
    line = _harvested(m, tradein, target="spare_stock")
    # the payload claims 'recycle'; the record says spare stock
    assert not consume(_event(line, target="recycle"))
    pending = m.env["fix.tradein.harvest"].create(
        {"tradein_id": tradein.id, "component": "board", "target": "recycle"}
    )
    assert not consume(_event(pending))  # not harvested yet
    assert not consume({"aggregate": "fix.tradein.harvest", "aggregate_id": 0, "payload": {}})
    assert not m.env["fix.ewaste.collection"].search_count(
        [("source_model", "=", tradein._name), ("source_res_id", "=", tradein.id)]
    )


def test_consumer_is_superuser_only_and_the_m18_gates_still_apply(m):
    tradein = _tradein(m)
    line = _harvested(m, tradein)
    Col = m.env["fix.ewaste.collection"]
    with pytest.raises(UserError, match="event relay"):
        Col.with_user(m.clerk).consume_tradein_harvested(_event(line))
    col = _consumer(m)(_event(line))
    clerk_col = col.with_user(m.clerk)
    # the link is not editable, and the item starts at the beginning of M18
    assert refused(m.env, lambda: clerk_col.write({"source_res_id": 0}))
    assert m.p03_write(m.clerk, "fix.ewaste.collection", col.id, {"source_ref": "X"}).get("error")
    assert refused(m.env, lambda: clerk_col.write({"state": "recycled"}))
    assert refused(m.env, lambda: clerk_col.action_secure_destruction())
    m.triage(col, "recycle")
    assert col.state == "triaged" and col.wipe_required
