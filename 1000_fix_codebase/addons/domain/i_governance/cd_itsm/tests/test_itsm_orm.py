"""cd_itsm — live-ORM behaviour of M66 IT tickets."""

from __future__ import annotations

import json

import pytest
from odoo.exceptions import UserError


def _events(env, event_type, aggregate_id):
    domain = [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)]
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def test_ticket_lifecycle(odoo_env):
    requester = odoo_env["hr.employee"].create({"name": "Branch Officer Tania"})
    ticket = odoo_env["fix.itsm.ticket"].create(
        {
            "name": "client-supplied",  # always replaced by the sequence/fallback
            "title": "POS printer offline",
            "requester_id": requester.id,
            "category": "hardware",
            "priority": "high",
            "description": "Thermal printer not detected after update",
        }
    )
    assert ticket.name != "client-supplied"
    assert ticket.name.startswith("ITSM/")
    assert ticket.state == "new"
    assert _events(odoo_env, "itsm.ticket_created", ticket.id) == [
        {"title": "POS printer offline", "priority": "high"}
    ]
    ticket.action_resolve("Driver reinstalled")
    assert (ticket.state, ticket.resolution) == ("resolved", "Driver reinstalled")
    assert _events(odoo_env, "itsm.ticket_resolved", ticket.id) == [{"ticket": ticket.name}]
    with pytest.raises(UserError, match="already resolved"), odoo_env.cr.savepoint():
        ticket.action_resolve("again")
    ticket.state = "closed"
    with pytest.raises(UserError, match="already resolved"), odoo_env.cr.savepoint():
        ticket.action_resolve("again")
