"""A12 P2 — the SLA escalation cron is the shipped feature-flag kill switch.

fix.feature.flag key `itsm.sla_auto_escalate`, read with is_disabled
(presence-based opt-out): escalation — which M66-7 mandates — runs by
default; an operator can switch it off without a deployment. The m66
suite proves the default escalation; this file proves the switch.
"""

from odoo import fields


def _employee(env, name):
    return env["hr.employee"].create({"name": name})


def _late_ticket(env):
    ticket = env["fix.itsm.ticket"].create(
        {
            "title": "Kill-switch probe: label printer offline",
            "requester_id": _employee(env, "KS Requester Rafiq").id,
            "category": "hardware",
            "priority": "medium",
            "description": "Printer offline past its SLA target.",
        }
    )
    # Push create_date back on the DATABASE clock and rerun the compute the
    # ORM way (same approach as the m66-7 test: a raw column push on
    # sla_deadline is clobbered by the pending compute).
    env.cr.execute(
        "UPDATE fix_itsm_ticket SET create_date = now() - interval '12 hours' WHERE id = %s",
        [ticket.id],
    )
    env.invalidate_all()
    catalogue = env["fix.itsm.catalogue"].create(
        {"code": "SLA-KS-%d" % ticket.id, "name": "Kill-switch probe", "target_hours": 4.0}
    )
    env["fix.itsm.ticket"].browse(ticket.id).write({"catalogue_id": catalogue.id})
    env.flush_all()
    assert env["fix.itsm.ticket"].browse(ticket.id).sla_deadline < fields.Datetime.now()
    return env["fix.itsm.ticket"].browse(ticket.id)


def test_the_kill_switch_stops_escalation_until_switched_back(odoo_env):
    env = odoo_env
    ticket = _late_ticket(env)
    # The operator throws the kill switch (flag EXISTS, disabled).
    env["fix.feature.flag"].create(
        {"key": "itsm.sla_auto_escalate", "name": "SLA auto-escalation kill switch"}
    )
    env["fix.itsm.ticket"].cron_escalate_sla()
    ticket.invalidate_recordset()
    assert ticket.escalated is False, "a disabled kill switch must stop escalation"
    assert ticket.priority == "medium"

    # Switched back on: the same cron run escalates the same late ticket.
    env["fix.feature.flag"].search([("key", "=", "itsm.sla_auto_escalate")]).write(
        {"enabled": True}
    )
    env["fix.itsm.ticket"].cron_escalate_sla()
    ticket.invalidate_recordset()
    assert ticket.escalated is True
    assert ticket.priority == "high"


def test_with_no_flag_row_escalation_runs_by_default(odoo_env):
    """No row anywhere: is_disabled answers False, escalation proceeds.

    This is the fail-safe direction the audit demands — the M66-7 control
    cannot be switched off by ACCIDENT, only by an explicit disabled row."""
    env = odoo_env
    ticket = _late_ticket(env)
    assert not env["fix.feature.flag"].search([])
    env["fix.itsm.ticket"].cron_escalate_sla()
    ticket.invalidate_recordset()
    assert ticket.escalated is True
    assert ticket.priority == "high"
