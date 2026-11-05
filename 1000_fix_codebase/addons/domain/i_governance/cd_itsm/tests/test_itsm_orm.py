"""cd_itsm — live-ORM behaviour of M66 IT tickets.

A12 rewrite (2026-11-05): the ticket now has an assignment step, an
agent-group gate on every working action, a REQUIRED resolution and an SLA
clock; the sequence prefix is ITSM/ (lead-shipped sequence). Runs as the
superuser, so the role gates are exercised in test_a12_m66_controls.py.
"""

from __future__ import annotations

import json
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError


def _events(env, event_type, aggregate_id):
    domain = [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)]
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def _ticket(env, **extra):
    requester = env["hr.employee"].create({"name": "Branch Officer Tania"})
    vals = {
        "name": "client-supplied",  # always replaced by the sequence/fallback
        "title": "POS printer offline",
        "requester_id": requester.id,
        "category": "hardware",
        "priority": "high",
        "description": "Thermal printer not detected after update",
    }
    vals.update(extra)
    return env["fix.itsm.ticket"].create(vals)


def test_ticket_lifecycle_and_sequence(odoo_env):
    ticket = _ticket(odoo_env)
    assert ticket.name != "client-supplied"
    assert ticket.name.startswith("ITSM/")
    assert ticket.state == "new"
    assert _events(odoo_env, "itsm.ticket_created", ticket.id) == [
        {"title": "POS printer offline", "priority": "high"}
    ]
    # M66-8: a request the service desk never took on cannot be resolved.
    with pytest.raises(UserError, match="Assign the ticket"), odoo_env.cr.savepoint():
        ticket.action_resolve("Driver reinstalled")
    ticket.action_assign(assigned_to=odoo_env["hr.employee"].create({"name": "Agent Ali"}))
    assert ticket.state == "assigned"
    ticket.action_start()
    assert ticket.state == "in_progress"
    with pytest.raises(UserError, match="resolution is required"), odoo_env.cr.savepoint():
        ticket.action_resolve("   ")
    ticket.action_resolve("Driver reinstalled")
    assert (ticket.state, ticket.resolution) == ("resolved", "Driver reinstalled")
    assert ticket.resolved_on
    assert _events(odoo_env, "itsm.ticket_resolved", ticket.id) == [{"ticket": ticket.name}]
    with pytest.raises(UserError, match="already resolved"), odoo_env.cr.savepoint():
        ticket.action_resolve("again")
    ticket.action_close()
    assert ticket.state == "closed"


def test_ticket_sla_from_catalogue(odoo_env):
    # Catalogue target wins...
    catalogue = odoo_env["fix.itsm.catalogue"].create(
        {"code": "SLA-PROBE-1", "name": "Printer swap", "target_hours": 4.0}
    )
    ticket = _ticket(odoo_env, catalogue_id=catalogue.id)
    assert ticket.sla_target_hours == 4.0
    assert ticket.sla_deadline == ticket.create_date + timedelta(hours=4.0)
    # ...else the config default (cd_itsm.sla_default_target_hours = 8).
    plain = _ticket(odoo_env)
    assert plain.sla_target_hours == 8.0
    assert plain.sla_deadline == plain.create_date + timedelta(hours=8.0)


def _age_ticket_beyond_sla(odoo_env, ticket, hours_back=12, target_hours=4.0):
    """Make a ticket's SLA genuinely past: the deadline is the COMPUTED
    create_date + target hours, and a stored compute is only rerun through its
    dependencies — so push create_date back on the DATABASE clock (a Python
    fields.Datetime.now() is local naive time before the process settles on
    UTC on this dev box) and touch catalogue_id through the ORM."""
    odoo_env.cr.execute(
        "UPDATE fix_itsm_ticket SET create_date = now() - (%s || ' hours')::interval "
        "WHERE id = %s",
        (str(hours_back), ticket.id),
    )
    odoo_env.invalidate_all()
    catalogue = odoo_env["fix.itsm.catalogue"].create(
        {"code": "SLA-LATE-%d" % ticket.id, "name": "Late probe", "target_hours": target_hours}
    )
    odoo_env["fix.itsm.ticket"].browse(ticket.id).write(
        {"catalogue_id": catalogue.id}
    )  # superuser bookkeeping; reruns _compute_sla on the pushed create_date
    odoo_env.flush_all()
    deadline = odoo_env["fix.itsm.ticket"].browse(ticket.id).sla_deadline
    assert deadline and deadline < fields.Datetime.now(), deadline


def test_cron_escalate_sla(odoo_env):
    ticket = _ticket(odoo_env, priority="medium")
    _age_ticket_beyond_sla(odoo_env, ticket)
    odoo_env["fix.itsm.ticket"].cron_escalate_sla()
    ticket.invalidate_recordset()
    assert ticket.escalated is True
    assert ticket.priority == "high"  # one step up, never fabricated beyond urgent
    # Already escalated tickets are not touched again.
    odoo_env["fix.itsm.ticket"].cron_escalate_sla()
    ticket.invalidate_recordset()
    assert ticket.priority == "high"


def test_cron_escalate_sla_names_its_recipient(odoo_env):
    """M66-7: with cd_itsm.sla_escalation_manager unset, nobody is notified —
    the escalation still applies, but no recipient is invented."""
    odoo_env["ir.config_parameter"].sudo().set_param("cd_itsm.sla_escalation_manager", False)
    ticket = _ticket(odoo_env)
    _age_ticket_beyond_sla(odoo_env, ticket)
    odoo_env["fix.itsm.ticket"].cron_escalate_sla()
    ticket.invalidate_recordset()
    assert ticket.escalated is True
    activities = (
        odoo_env["mail.activity"]
        .sudo()
        .search([("res_model", "=", "fix.itsm.ticket"), ("res_id", "=", ticket.id)])
    )
    assert not activities
