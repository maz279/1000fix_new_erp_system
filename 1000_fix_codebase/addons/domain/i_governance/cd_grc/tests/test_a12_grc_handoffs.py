"""A12 D8 hand-off: M67 project risks escalate into the M60 register."""

from __future__ import annotations


def _event(
    odoo_env, title, project_name="Tower DC upgrade", probability=3, impact=3, event_id="evt-1"
):
    return {
        "event_id": event_id,
        "event_type": "project.risk_escalated",
        "payload": {
            "title": title,
            "project": {"name": project_name},
            "probability": probability,
            "impact": impact,
            "severity": (probability or 0) * (impact or 0),
            "kind": "risk",
        },
        "company_id": odoo_env.company.id,
    }


def test_consumer_record_exists(odoo_env):
    consumer = odoo_env.ref("cd_grc.consumer_project_risk_escalated", raise_if_not_found=False)
    assert consumer, "fix.event.consumer record for project.risk_escalated is missing"
    assert consumer.model == "fix.risk.register"
    assert consumer.method == "consume_project_risk_escalated"


def test_escalated_risk_opens_a_register_entry(odoo_env):
    reg = odoo_env["fix.risk.register"]
    entry = reg.consume_project_risk_escalated(_event(odoo_env, "Single-point network failure"))
    assert entry.name == "[M67] Single-point network failure — Tower DC upgrade"
    assert entry.category == "operational"
    assert entry.state == "open"
    assert entry.likelihood == "3" and entry.impact == "3"
    assert entry.risk_score == 9
    assert "evt-1" in (entry.mitigation or "")


def test_consumer_is_idempotent_on_redelivery(odoo_env):
    reg = odoo_env["fix.risk.register"]
    first = reg.consume_project_risk_escalated(
        _event(odoo_env, "Battery fire risk", event_id="evt-2")
    )
    again = reg.consume_project_risk_escalated(
        _event(odoo_env, "Battery fire risk", event_id="evt-2")
    )
    assert again.id == first.id
    count = reg.search_count([("name", "like", "Battery fire risk")])
    assert count == 1, "redelivery must not duplicate the register entry"


def test_payload_clamps_out_of_range_scores(odoo_env):
    reg = odoo_env["fix.risk.register"]
    entry = reg.consume_project_risk_escalated(
        _event(odoo_env, "Odd payload", probability=9, impact=None, event_id="evt-3")
    )
    assert entry.likelihood == "5", "probability 9 clamps to the 1-5 scale"
    assert entry.impact == "3", "a missing impact falls back to the default"
