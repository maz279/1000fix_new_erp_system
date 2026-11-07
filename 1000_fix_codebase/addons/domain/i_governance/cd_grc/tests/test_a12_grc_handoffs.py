"""A12 D8 hand-off: M67 project risks escalate into the M60 register.

A12 finish (2026-11-07) F5: this suite called the consumer with a hand-made
payload ({"project": {"name": ...}}) that the publisher never sends, which is how
a hand-off that died on all 3 live deliveries passed its tests. Every test now
raises a real project risk and runs the real cron_relay.
"""

from __future__ import annotations

import json


def _risk(odoo_env, title, probability="high", impact="high", project_name="Tower DC upgrade"):
    project = odoo_env["fix.project"].create({"name": project_name})
    return odoo_env["fix.project.risk"].create(
        {
            "project_id": project.id,
            "title": title,
            "probability": probability,
            "impact": impact,
        }
    )


def _event(odoo_env, risk):
    return odoo_env["fix.event.outbox"].search(
        [("event_type", "=", "project.risk_escalated"), ("aggregate_id", "=", risk.id)], limit=1
    )


def _entries(odoo_env, title):
    return odoo_env["fix.risk.register"].search([("name", "like", title)])


def test_consumer_record_exists(odoo_env):
    consumer = odoo_env.ref("cd_grc.consumer_project_risk_escalated", raise_if_not_found=False)
    assert consumer, "fix.event.consumer record for project.risk_escalated is missing"
    assert consumer.model == "fix.risk.register"
    assert consumer.method == "consume_project_risk_escalated"


def test_escalated_risk_opens_a_register_entry(odoo_env):
    risk = _risk(odoo_env, "Single-point network failure")
    assert risk.escalated
    odoo_env["fix.event.outbox"].sudo().cron_relay(limit=10000)
    entry = _entries(odoo_env, "Single-point network failure")
    assert len(entry) == 1
    assert entry.name == "[M67] %s: Single-point network failure — Tower DC upgrade" % risk.name
    assert entry.category == "operational"
    assert entry.state == "open"
    # severity 9 is the top of the project scale, and of the register's.
    assert entry.likelihood == "5" and entry.impact == "5"
    assert entry.risk_score == 25
    assert _event(odoo_env, risk).event_id in (entry.mitigation or "")


def test_consumer_delivery_is_recorded_done_and_the_risk_says_so(odoo_env):
    risk = _risk(odoo_env, "Battery room flood")
    odoo_env["fix.event.outbox"].sudo().cron_relay(limit=10000)
    consumer = odoo_env.ref("cd_grc.consumer_project_risk_escalated")
    delivery = odoo_env["fix.event.consumer.delivery"].search(
        [("subscription_id", "=", consumer.id), ("event_id", "=", _event(odoo_env, risk).id)]
    )
    assert delivery.state == "done", delivery.last_error
    bodies = " ".join(risk.message_ids.mapped("body"))
    assert "Entered on the enterprise risk register" in bodies


def test_consumer_is_idempotent_on_redelivery(odoo_env):
    risk = _risk(odoo_env, "Battery fire risk")
    event = _event(odoo_env, risk)
    Register = odoo_env["fix.risk.register"]
    first = Register.consume_project_risk_escalated(event._relay_event_dict())
    again = Register.consume_project_risk_escalated(event._relay_event_dict())
    assert again.id == first.id
    assert len(_entries(odoo_env, "Battery fire risk")) == 1


def test_two_risks_with_the_same_title_stay_two_entries(odoo_env):
    project = odoo_env["fix.project"].create({"name": "Twin risks"})
    vals = {
        "project_id": project.id,
        "title": "Vendor slip",
        "probability": "high",
        "impact": "high",
    }
    odoo_env["fix.project.risk"].create([vals, dict(vals)])
    odoo_env["fix.event.outbox"].sudo().cron_relay(limit=10000)
    assert len(_entries(odoo_env, "Vendor slip")) == 2


def test_event_published_before_the_scores_were_added_reads_the_risk(odoo_env):
    """The 3 live events carry no probability or impact: they must land scored."""
    risk = _risk(odoo_env, "Key developer unavailable", probability="high", impact="medium")
    event = _event(odoo_env, risk) or _publish_legacy(odoo_env, risk)
    payload = json.loads(event.payload)
    payload.pop("probability", None)
    payload.pop("impact", None)
    event.payload = json.dumps(payload)
    entry = odoo_env["fix.risk.register"].consume_project_risk_escalated(event._relay_event_dict())
    assert (entry.likelihood, entry.impact) == ("5", "3")


def _publish_legacy(odoo_env, risk):
    risk.sudo()._guarded().write({"escalated": False})
    risk._publish_escalation("overdue")
    return _event(odoo_env, risk)


def _deliver(odoo_env, event, **changes):
    """The real event with its payload altered, through the relay's own delivery. The
    relay catches a consumer's crash and returns it as text: '' means it did not crash."""
    payload = json.loads(event.payload)
    payload.update(changes)
    event.payload = json.dumps(payload)
    consumer = odoo_env.ref("cd_grc.consumer_project_risk_escalated")
    error = odoo_env["fix.event.outbox"].sudo()._relay_deliver(consumer, event)
    assert error == "", error
    return _entries(odoo_env, payload["title"])


def test_payload_clamps_out_of_range_scores(odoo_env):
    # An out-of-range number clamps to the register's 1-5; a value that is no score at
    # all falls back to the project risk, whose medium is the register's 3.
    risk = _risk(odoo_env, "Odd payload", probability="medium", impact="medium")
    risk._publish_escalation("overdue")
    entry = _deliver(odoo_env, _event(odoo_env, risk), probability=9, impact="garbage")
    assert entry.likelihood == "5", "probability 9 clamps to the 1-5 scale"
    assert entry.impact == "3", "garbage falls back to the risk's own impact"


def test_payload_clamps_low_scores_up(odoo_env):
    risk = _risk(odoo_env, "Low odd payload")
    entry = _deliver(odoo_env, _event(odoo_env, risk), probability=0, impact=-4)
    assert (entry.likelihood, entry.impact) == ("1", "1")


def test_garbage_scores_with_the_risk_gone_fall_back_to_the_severity(odoo_env):
    risk = _risk(odoo_env, "Deleted risk payload", probability="low", impact="low")
    risk._publish_escalation("overdue")
    event = _event(odoo_env, risk)
    risk.sudo().unlink()
    entry = _deliver(odoo_env, event, probability="garbage", impact=None, severity=9)
    assert (entry.likelihood, entry.impact) == ("5", "5"), "severity 9 is the top of the scale"


def test_a_stated_score_survives_when_the_other_falls_back_to_the_severity(odoo_env):
    risk = _risk(odoo_env, "Half payload", probability="low", impact="low")
    risk._publish_escalation("overdue")
    event = _event(odoo_env, risk)
    risk.sudo().unlink()
    entry = _deliver(odoo_env, event, probability=9, impact="garbage", severity=1)
    assert (entry.likelihood, entry.impact) == ("5", "1")


def test_garbage_everywhere_lands_mid_scale_and_does_not_kill_the_consumer(odoo_env):
    risk = _risk(odoo_env, "All garbage payload", probability="low", impact="low")
    risk._publish_escalation("overdue")
    event = _event(odoo_env, risk)
    risk.sudo().unlink()
    entry = _deliver(odoo_env, event, probability="?", impact="?", severity="?")
    assert (entry.likelihood, entry.impact) == ("3", "3")
