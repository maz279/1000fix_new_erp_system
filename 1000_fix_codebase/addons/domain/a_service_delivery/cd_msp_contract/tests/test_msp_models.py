"""Behavioural tests for M05 managed services (journey 6) on the live ORM
(``odoo_env``: fix_test, rolled back after every test)."""

import json
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo import fields
from odoo.exceptions import UserError


@contextmanager
def _refused(env, exc, match=None):
    """Expect ``exc``; the failed operation is rolled back (flushing savepoint)."""
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info
    env.invalidate_all()


@pytest.fixture
def msp(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "MSPENT", "legal_name": "MSP Entity", "company_id": env.company.id}
    )
    branch = env["fix.branch"].create(
        {"name": "MSP Hub", "code": "MSPB", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    client = env["res.partner"].create({"name": "MSP Client Ltd", "is_company": True})
    contract = env["fix.contract"].create(
        {
            "code": "MSP-CTR-1",
            "name": "Managed endpoints",
            "family": "managed",
            "state": "active",  # A02 audit M05-P2: MSP work needs a term in force
            "annual_value": 54000.0,
            "customer_id": client.id,
            "operating_unit_id": ou.id,
            "date_start": date(2026, 1, 1),
            "date_end": date(2026, 12, 31),
        }
    )
    msp_contract = env["fix.msp.contract"].create(
        {
            "name": "MSP Client endpoints",
            "contract_id": contract.id,
            "per_device_monthly": 450.0,
            # A02 ERP audit M05-F4: no enrolment without a contracted count
            "device_count": 2,
        }
    )
    brand = env["fix.brand"].create({"name": "MspBrand", "code": "MSPBR"})
    model = env["fix.device.model"].create({"name": "MspDesk", "brand_id": brand.id})
    device = env["fix.device"].create(
        {"device_model_id": model.id, "serial_number": "SN-MSP-1", "branch_id": branch.id}
    )
    asset = env["fix.monitored.asset"].create(
        {
            "msp_contract_id": msp_contract.id,
            "agent_id": "AGT-MSP-1",
            "hostname": "pc-01",
            "device_id": device.id,
        }
    )
    bare = env["fix.monitored.asset"].create(
        {"msp_contract_id": msp_contract.id, "agent_id": "AGT-MSP-2"}
    )
    tech = env["hr.employee"].create({"name": "MSP Tech"})
    return SimpleNamespace(
        env=env,
        branch=branch,
        client=client,
        msp=msp_contract,
        device=device,
        asset=asset,
        bare=bare,
        tech=tech,
    )


def _events(env, aggregate, rec_id):
    return env["fix.event.outbox"].search(
        [("aggregate", "=", aggregate), ("aggregate_id", "=", rec_id)], order="id asc"
    )


def _alert(msp, asset=None, state="new", created=None, resolved_in=None):
    alert = msp.env["fix.msp.alert"].create(
        {
            "msp_contract_id": msp.msp.id,
            "asset_id": (asset or msp.asset).id,
            "message": "disk full",
            "state": state,
        }
    )
    if created:
        msp.env.flush_all()
        msp.env.cr.execute(
            "UPDATE fix_msp_alert SET sla_deadline = NULL, response_deadline = NULL, create_date = %s WHERE id = %s",
            (created, alert.id),
        )
        if resolved_in is not None:
            msp.env.cr.execute(
                "UPDATE fix_msp_alert SET resolved_at = %s WHERE id = %s",
                (created + timedelta(hours=resolved_in), alert.id),
            )
        msp.env.invalidate_all()
    return alert


# --- telemetry -> alert -> ticket ------------------------------------------------------------


def test_first_unhealthy_transition_raises_one_alert(msp):
    env = msp.env
    asset_model = env["fix.monitored.asset"]
    with _refused(env, UserError, "Unknown RMM agent AGT-NOPE"):
        asset_model.ingest_telemetry("AGT-NOPE", "offline", fields.Datetime.now())
    seen = datetime(2026, 10, 22, 9, 0, 0)
    asset_model.ingest_telemetry("AGT-MSP-1", "healthy", seen)
    assert not env["fix.msp.alert"].search([("asset_id", "=", msp.asset.id)])
    asset_model.ingest_telemetry("AGT-MSP-1", "degraded", seen)
    asset_model.ingest_telemetry("AGT-MSP-1", "offline", seen)  # still unhealthy: no new alert
    alert = env["fix.msp.alert"].search([("asset_id", "=", msp.asset.id)])
    assert (alert.severity, alert.message, alert.state) == ("minor", "pc-01 became degraded", "new")
    assert (msp.asset.health, msp.asset.last_seen) == ("offline", seen)
    assert json.loads(_events(env, "fix.msp.alert", alert.id).payload) == {
        "agent": "AGT-MSP-1",
        "health": "degraded",
    }
    asset_model.ingest_telemetry("AGT-MSP-2", "offline", seen)
    major = env["fix.msp.alert"].search([("asset_id", "=", msp.bare.id)])
    assert (major.severity, major.message) == ("major", "AGT-MSP-2 became offline")


def test_alert_acknowledge_and_ticket(msp):
    env = msp.env
    alert = _alert(msp)
    alert.action_acknowledge()
    assert alert.state == "acked"
    with _refused(env, UserError, "Only NEW alerts acknowledge"):
        alert.action_acknowledge()
    alert.action_to_ticket()
    order = alert.order_id
    assert alert.state == "ticketed"
    assert (order.device_id, order.branch_id, order.customer_id) == (
        msp.device,
        msp.branch,
        msp.client,
    )
    assert (order.order_category, order.fault_description) == ("amc", "MSP alert: disk full")
    assert json.loads(_events(env, "fix.msp.alert", alert.id)[-1].payload) == {"order": order.name}
    with _refused(env, UserError, "already ticketed or resolved"):
        alert.action_to_ticket()


def test_ticket_needs_the_asset_linked_to_a_registered_device_with_a_branch(msp):
    """Regression: the ticket was created with no device and branch_id False,
    which the service order refuses - no alert could ever be ticketed."""
    env = msp.env
    alert = _alert(msp, asset=msp.bare)
    with _refused(env, UserError, "AGT-MSP-2 is not linked to a registered device"):
        alert.action_to_ticket()
    branchless = env["fix.device"].create(
        {"device_model_id": msp.device.device_model_id.id, "serial_number": "SN-MSP-2"}
    )
    msp.bare.write({"device_id": branchless.id, "hostname": "pc-02"})
    with _refused(env, UserError, "pc-02 is not linked"):
        alert.action_to_ticket()
    assert alert.state == "new" and not alert.order_id


# --- remote sessions ------------------------------------------------------------------------


def _grant_consent(session):
    """A02 audit M05-4: consent is the client's one-time code, not a tickbox."""
    sent = {}

    def _send(self, partner, code, ttl_seconds):
        sent["code"] = code
        return {"destination": "017*****000"}

    with patch.object(type(session), "_consent_send_code", _send):
        session.action_request_consent()
    session.action_verify_consent(code=sent["code"])


def test_remote_session_requires_consent(msp):
    env = msp.env
    session = env["fix.remote.session"].create(
        {"msp_contract_id": msp.msp.id, "asset_id": msp.asset.id, "technician_id": msp.tech.id}
    )
    with _refused(env, UserError, "PDPA: remote sessions require captured consent"):
        session.action_start()
    _grant_consent(session)
    session.action_start()
    session.action_end(recording_url="mesh://recordings/1")
    assert session.ended_at
    started, ended = _events(env, "fix.remote.session", session.id)
    assert (started.event_type, json.loads(started.payload)) == (
        "msp.remote_session_started",
        {"asset": "pc-01"},
    )
    assert ended.event_type == "msp.remote_session_ended"
    bare_session = env["fix.remote.session"].create(
        {
            "msp_contract_id": msp.msp.id,
            "asset_id": msp.bare.id,
            "technician_id": msp.tech.id,
        }
    )
    _grant_consent(bare_session)
    bare_session.action_start()
    assert json.loads(_events(env, "fix.remote.session", bare_session.id).payload) == {
        "asset": "AGT-MSP-2"
    }


# --- monthly reports ------------------------------------------------------------------------


def test_generate_button_reports_the_previous_calendar_month(msp):
    """Regression: the form button called action_monthly_report without its
    required ``period`` - every click raised a TypeError."""
    env = msp.env
    # A02 audit M05-P2: within SLA is measured against the resolution
    # target (minor: 24 h). Resolved in 2 h is within; open past it is a breach.
    _alert(msp, state="resolved", created=datetime(2026, 2, 3, 10, 0), resolved_in=2)
    # A02 ERP audit M05-F15: the month is the Dhaka calendar month (UTC+6)
    _alert(msp, state="new", created=datetime(2026, 2, 28, 23, 0))  # 1 Mar 05:00 Dhaka: out
    _alert(msp, state="resolved", created=datetime(2026, 3, 1, 0, 30))  # March: excluded
    # 1 Feb 05:59 in Dhaka: February, resolved with no resolution time (a breach)
    _alert(msp, state="resolved", created=datetime(2026, 1, 31, 23, 59))
    with patch(
        "odoo.addons.cd_msp_contract.models.msp_periods.dhaka_today",
        return_value=date(2026, 3, 15),
    ):
        action = msp.msp.action_generate_monthly_report()
    report = env["fix.msp.service.report"].browse(action["res_id"])
    assert action == {
        "type": "ir.actions.act_window",
        "res_model": "fix.msp.service.report",
        "res_id": report.id,
        "view_mode": "form",
    }
    # February: 2 alerts, 1 resolved within target -> 50.0 %, 2 covered devices
    assert (
        report.period_label,
        report.alert_count,
        report.resolved_count,
        report.sla_attainment,
    ) == (
        "2026-02",
        2,
        1,
        0.5,
    )
    assert report.summary_en == (
        "Monthly Managed Services Operations Report for 2026-02: 2 alerts processed, "
        "1 incidents resolved within SLA. SLA attainment achieved: 50.0% across 2 covered endpoints."
    )
    assert "এসএলএ অর্জনের হার 50.0%" in report.summary_bn
    event = _events(env, "fix.msp.service.report", report.id)
    assert json.loads(event.payload) == {"contract": "MSP Client endpoints", "period": "2026-02"}


def test_a_quiet_month_is_full_sla_attainment(msp):
    msp.msp.device_count = 25
    report = msp.msp._msp_monthly_report(
        (datetime(2025, 6, 1), datetime(2025, 6, 30, 23, 59, 59), "2025-06")
    )
    assert (report.alert_count, report.sla_attainment) == (0, 1.0)
    assert "100.0% across 25 covered endpoints" in report.summary_en


def test_bilingual_report_regeneration(msp):
    report = msp.env["fix.msp.service.report"].create(
        {
            "msp_contract_id": msp.msp.id,
            "period_label": "2026-09",
            "alert_count": 4,
            "resolved_count": 3,
            "sla_attainment": 0.75,
        }
    )
    empty = msp.env["fix.msp.service.report"].create(
        {"msp_contract_id": msp.msp.id, "period_label": "2026-08"}
    )
    (report | empty).action_generate_bilingual_report()
    assert report.summary_en == (
        "Monthly Managed Services Operations Report for 2026-09: 4 alerts processed, "
        "3 incidents resolved within SLA. SLA attainment achieved: 75.0% across 2 covered endpoints."
    )
    assert report.summary_bn.startswith("2026-09 মাসের")
    assert "SLA attainment achieved: 0.0%" in empty.summary_en
