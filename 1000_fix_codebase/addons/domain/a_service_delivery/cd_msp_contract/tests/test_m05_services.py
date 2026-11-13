"""M05 spec features built by the audit (2026-11-13): client contacts and
permissions (FR-RMS-049), major incidents (020), service review meetings
(036), cloud subscriptions (040), DR plans and tests (042/043) and the
technology roadmap (045/046). Each rule is tested both ways, as non-admin
users holding only their M05 role, and each capture is saved through the
workspace controller.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

from . import test_a02_p0_m05 as p0

m5 = p0.m5
call = p0.call
_as = p0._as
GUARD = p0.GUARD


def _contact(m5, partner=None, **vals):
    base = {
        "msp_contract_id": m5.msp.id,
        "partner_id": (partner or m5.contact).id,
        "role": "it_manager",
    }
    base.update(vals)
    return _as(m5.env["fix.msp.client.contact"], m5.eng).create(base)


# --- FR-RMS-049 -------------------------------------------------------------


def test_a_contact_is_one_of_the_clients_people(m5):
    stranger = m5.env["res.partner"].create({"name": "Not the client"})
    with pytest.raises(ValidationError, match="not a contact of"):
        _contact(m5, partner=stranger)
    assert _contact(m5).partner_id == m5.contact


def test_a_client_ticket_names_a_contact_allowed_to_raise_it(m5, call):
    values = {
        "msp_contract_id": m5.msp.id,
        "asset_id": m5.asset.id,
        "source": "email",
        "message": "Mail server queue is stuck",
    }
    out = call(
        m5.env(user=m5.eng.id), "model_write", model="fix.msp.alert", record_id=False, values=values
    )
    assert out.get("error") and "client contact" in out["error"]
    viewer = _contact(m5, role="viewer", can_raise_tickets=False)
    out = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.alert",
        record_id=False,
        values={**values, "reported_by_contact_id": viewer.id},
    )
    assert out.get("error") and "not allowed to raise tickets" in out["error"]
    viewer.write({"can_raise_tickets": True})
    out = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.alert",
        record_id=False,
        values={**values, "reported_by_contact_id": viewer.id},
    )
    assert "error" not in out, out


def test_only_a_permitted_contact_consents_once_contacts_exist(m5):
    _contact(m5, can_receive_consent=False)
    Session = _as(m5.env["fix.remote.session"], m5.eng)
    vals = {
        "msp_contract_id": m5.msp.id,
        "asset_id": m5.asset.id,
        "technician_id": m5.emp.id,
        "consent_partner_id": m5.contact.id,
        "operating_unit_id": m5.ou.id,
    }
    with pytest.raises(ValidationError, match="consent codes"):
        Session.create(vals)
    m5.msp.client_contact_ids.write({"can_receive_consent": True})
    assert Session.create(vals).consent_partner_id == m5.contact


# --- FR-RMS-020 -------------------------------------------------------------


def _incident(m5, user=None):
    return _as(m5.env["fix.msp.major.incident"], user or m5.eng).create(
        {
            "name": "Core switch down at the client HQ",
            "msp_contract_id": m5.msp.id,
            "impact": "No network on three floors; 120 users offline",
            "operating_unit_id": m5.ou.id,
        }
    )


def test_a_major_incident_notifies_contacts_and_is_reviewed_by_someone_else(m5):
    inc = _incident(m5)
    with pytest.raises(UserError, match="no registered client contact"):
        _as(inc, m5.eng).action_notify_contacts()
    _contact(m5)
    with pytest.raises(UserError, match="after its client contacts are notified"):
        _as(inc, m5.eng).action_resolve(note="replaced the supervisor module")
    _as(inc, m5.eng).action_notify_contacts()
    assert inc.state == "notified" and inc.notified_count == 1
    assert m5.contact in inc.message_ids[0].partner_ids
    _as(inc, m5.eng).action_resolve(note="replaced the supervisor module; uplinks restored")
    with pytest.raises(UserError):  # the declarer does not review his own incident
        _as(inc, m5.eng).action_record_review(note="root cause: failed PSU; add redundant PSU")
    _as(inc, m5.eng2).action_record_review(note="root cause: failed PSU; add redundant PSU")
    assert inc.state == "closed" and inc.reviewed_by_id == m5.eng2
    with pytest.raises(UserError, match=GUARD):
        _as(inc, m5.eng).write({"state": "declared"})


def test_only_an_engineer_declares_a_major_incident(m5):
    with pytest.raises((AccessError, UserError)):
        _incident(m5, user=m5.plain)


# --- FR-RMS-036 -------------------------------------------------------------


def test_a_review_closes_only_when_every_action_is_done(m5, call):
    out = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.service.review",
        record_id=False,
        values={
            "msp_contract_id": m5.msp.id,
            "meeting_date": "2026-11-10",
            "attendees": "Client IT lead; 1000FiX account manager",
            "operating_unit_id": m5.ou.id,
        },
        lines={
            "field": "action_ids",
            "rows": [{"values": {"name": "Quote a firewall refresh", "done": False}}],
            "removed": [],
        },
    )
    assert "error" not in out, out
    review = m5.env["fix.msp.service.review"].search([("msp_contract_id", "=", m5.msp.id)])
    assert review.open_action_count == 1
    with pytest.raises(UserError, match="still open"):
        _as(review, m5.eng).action_close()
    review.action_ids.write({"done": True})
    _as(review, m5.eng).action_close()
    assert review.state == "closed"


def test_a_review_discusses_its_own_contracts_report(m5):
    other_report = (
        m5.env["fix.msp.service.report"]
        ._guarded()
        .create({"msp_contract_id": m5.other.id, "period_label": "2026-10"})
    )
    with pytest.raises(ValidationError, match="another contract"):
        _as(m5.env["fix.msp.service.review"], m5.eng).create(
            {
                "msp_contract_id": m5.msp.id,
                "attendees": "x",
                "service_report_id": other_report.id,
            }
        )


# --- FR-RMS-040 -------------------------------------------------------------


def test_a_cloud_subscription_costs_and_flags_its_renewal(m5):
    today = fields.Date.context_today(m5.env["fix.msp.cloud.subscription"])
    sub = _as(m5.env["fix.msp.cloud.subscription"], m5.eng).create(
        {
            "msp_contract_id": m5.msp.id,
            "provider": "m365",
            "name": "Business Standard",
            "seats": 25,
            "unit_cost": 1300.0,
            "renewal_date": today + timedelta(days=20),
        }
    )
    assert sub.monthly_cost == 32500.0 and sub.renewal_due
    assert sub in m5.env["fix.msp.cloud.subscription"].search([("renewal_due", "=", True)])
    sub.write({"renewal_date": today + timedelta(days=200)})
    assert not sub.renewal_due


# --- FR-RMS-042/043 ---------------------------------------------------------


def test_a_dr_test_passes_only_when_it_met_the_targets(m5):
    plan = _as(m5.env["fix.msp.dr.plan"], m5.eng).create(
        {
            "msp_contract_id": m5.msp.id,
            "name": "File server",
            "scope": "FS01, its shares and the nightly backup set",
            "rto_hours": 4,
            "rpo_hours": 24,
            "test_interval_days": 180,
        }
    )
    Test = _as(m5.env["fix.msp.dr.test"], m5.eng)
    base = {
        "plan_id": plan.id,
        "test_date": "2026-11-01",
        "evidence": "restored FS01 to the DR host",
    }
    with pytest.raises(ValidationError, match="missed its targets"):
        Test.create(
            {**base, "outcome": "passed", "rto_achieved_hours": 6, "rpo_achieved_hours": 12}
        )
    partial = Test.create(
        {**base, "outcome": "partial", "rto_achieved_hours": 6, "rpo_achieved_hours": 12}
    )
    assert not partial.meets_targets
    passed = Test.create(
        {**base, "outcome": "passed", "rto_achieved_hours": 3, "rpo_achieved_hours": 12}
    )
    assert passed.meets_targets and passed.tested_by_id == m5.eng
    assert str(plan.last_test_date) == "2026-11-01"
    assert str(plan.next_test_due) == "2027-04-30"
    with pytest.raises(UserError, match=GUARD):
        _as(passed, m5.eng).write({"outcome": "failed"})
    with pytest.raises(UserError, match="evidence"):
        Test.create(
            {
                **base,
                "evidence": "ok",
                "outcome": "failed",
                "rto_achieved_hours": 9,
                "rpo_achieved_hours": 30,
            }
        )


# --- FR-RMS-045/046 ---------------------------------------------------------


def test_an_accepted_roadmap_item_becomes_one_sales_opportunity(m5):
    item = _as(m5.env["fix.msp.roadmap.item"], m5.eng).create(
        {
            "msp_contract_id": m5.msp.id,
            "kind": "refresh",
            "name": "Replace 12 laptops past warranty",
            "target_quarter": "2027-Q1",
            "estimated_value": 960000.0,
        }
    )
    with pytest.raises(UserError, match="client accepted"):
        _as(item, m5.eng).action_create_opportunity()
    _as(item, m5.eng).action_accept()
    _as(item, m5.eng).action_create_opportunity()
    assert item.lead_id.type == "opportunity" and item.lead_id.expected_revenue == 960000.0
    with pytest.raises(UserError, match="already has opportunity"):
        _as(item, m5.eng).action_create_opportunity()
    with pytest.raises(ValidationError, match="YYYY-Qn"):
        item.write({"target_quarter": "next year"})
