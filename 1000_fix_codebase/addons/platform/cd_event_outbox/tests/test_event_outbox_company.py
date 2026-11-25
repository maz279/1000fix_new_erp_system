# FIN-24 (A07 ERP audit 2026-11-20): an outbox event is stamped with the company
# of the record it is about, not the company the publishing user happens to be
# working in. Live ORM (`odoo_env`, rolled back after every test).
from libs.py.fix_events import publish


def _other_company(env):
    return env["res.company"].create({"name": "FIN24 OtherCo"})


def test_fin24_an_event_carries_the_company_of_its_record(odoo_env):
    env = odoo_env
    other = _other_company(env)
    assert env.company != other
    partner = env["res.partner"].create({"name": "FIN24 B partner", "company_id": other.id})
    event = env["fix.event.outbox"].emit("fin24.tested", "res.partner", partner.id, {"k": 1})
    assert event.company_id == other


def test_fin24_publish_stamps_the_records_company_too(odoo_env):
    env = odoo_env
    other = _other_company(env)
    partner = env["res.partner"].create({"name": "FIN24 B partner 2", "company_id": other.id})
    event_id = publish(env, "fin24.published", "res.partner", partner.id, {})
    row = env["fix.event.outbox"].search([("event_id", "=", event_id)])
    assert row.company_id == other


def test_fin24_a_company_record_is_its_own_company(odoo_env):
    env = odoo_env
    other = _other_company(env)
    event = env["fix.event.outbox"].emit("fin24.company", "res.company", other.id, {})
    assert event.company_id == other


def test_fin24_falls_back_to_the_current_company(odoo_env):
    env = odoo_env
    Outbox = env["fix.event.outbox"]
    shared = env["res.partner"].create({"name": "FIN24 shared partner", "company_id": False})
    country = env.ref("base.bd")
    cases = [
        ("res.partner", shared.id),  # a record with no company
        ("res.country", country.id),  # a model with no company field
        ("res.partner", 0),  # no record
        ("res.partner", 2_000_000_000),  # a record that does not exist (deleted)
        ("test.outbox.aggregate", 7),  # not an Odoo model at all
    ]
    for aggregate, aggregate_id in cases:
        event = Outbox.emit("fin24.fallback", aggregate, aggregate_id, {})
        assert event.company_id == env.company, (aggregate, aggregate_id)


def test_fin24_the_relay_hands_the_event_to_its_consumer_in_the_records_company(odoo_env):
    env = odoo_env
    other = _other_company(env)
    partner = env["res.partner"].create({"name": "FIN24 relay partner", "company_id": other.id})
    event = env["fix.event.outbox"].emit("fin24.relayed", "res.partner", partner.id, {})
    assert event._relay_event_dict()["company_id"] == other.id
