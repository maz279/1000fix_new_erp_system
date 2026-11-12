"""M05 business rules the bidirectional audit (2026-11-13) found unbuilt.

BRU-RMS-02 unattended access, 05 coverage-window SLA clocks, 07 no
absorbed overage, 10 recurring incidents need a problem record, 11
offboarding evidence, 12 recording retention and logged access. Each is
tested both ways: the bypass is refused, the legitimate path works. Actors
are non-admin users holding only their M05 role.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from odoo import fields
from odoo.addons.cd_msp_contract.models.fix_msp_rules_bru import add_business_hours
from odoo.exceptions import UserError, ValidationError

from . import test_a02_p0_m05 as p0

m5 = p0.m5
call = p0.call
_as = p0._as


def _asset(m5, n):
    return m5.env["fix.monitored.asset"].create(
        {"msp_contract_id": m5.msp.id, "agent_id": "AGT-BRU-%s" % n, "operating_unit_id": m5.ou.id}
    )


def _alert(m5, asset=None, **vals):
    base = {"msp_contract_id": m5.msp.id, "asset_id": (asset or m5.asset).id, "message": "x"}
    base.update(vals)
    return _as(m5.env["fix.msp.alert"], m5.eng).create(base)


# --- BRU-RMS-02 -------------------------------------------------------------


def _session(m5, **vals):
    base = {
        "msp_contract_id": m5.msp.id,
        "asset_id": m5.asset.id,
        "technician_id": m5.emp.id,
        "operating_unit_id": m5.ou.id,
    }
    base.update(vals)
    return _as(m5.env["fix.remote.session"], m5.eng).create(base)


def test_unattended_access_needs_a_contract_that_grants_it(m5):
    with pytest.raises(ValidationError, match="unattended"):
        _session(m5, access_mode="unattended")
    m5.msp.write({"unattended_access": True})
    assert _session(m5, access_mode="unattended").access_mode == "unattended"
    assert _session(m5).access_mode == "attended"


# --- BRU-RMS-05 -------------------------------------------------------------


def test_business_hours_skip_the_bangladesh_weekend():
    # Thursday 12 Nov 2026 17:00 Dhaka = 11:00 UTC; 4 working hours later is
    # Sunday 15 Nov 12:00 Dhaka (1 h on Thursday, Fri/Sat closed, 3 h Sunday)
    end = add_business_hours(datetime(2026, 11, 12, 11, 0), 4)
    assert end == datetime(2026, 11, 15, 6, 0)
    # raised at 02:00 on Monday: the clock starts at 09:00 that day
    assert add_business_hours(datetime(2026, 11, 15, 20, 0), 1) == datetime(2026, 11, 16, 4, 0)


def test_the_sla_deadline_follows_the_coverage_window(m5):
    alert = _alert(m5, severity="major")
    alert.env.cr.execute(
        "UPDATE fix_msp_alert SET create_date = %s WHERE id = %s",
        (datetime(2026, 11, 12, 11, 0), alert.id),
    )
    alert.invalidate_recordset()
    m5.msp.write({"alert_resolve_hours_major": 4.0})
    assert m5.msp._msp_deadline(alert) == datetime(2026, 11, 12, 15, 0)
    m5.msp.write({"coverage_window": "business"})
    assert m5.msp._msp_deadline(alert) == datetime(2026, 11, 15, 6, 0)
    # judged on Saturday: inside business hours it is still pending, not breached
    saturday = datetime(2026, 11, 14, 6, 0)
    assert m5.msp._msp_period_sla(alert, as_of=saturday)["pending"] == 1


# --- BRU-RMS-07 -------------------------------------------------------------


def test_a_device_beyond_the_contracted_count_is_refused(m5):
    cr = m5.env.cr
    m5.msp.write({"device_count": 1})  # the fixture's one asset
    # the workspace saves in a savepoint, so a refused save leaves nothing
    with pytest.raises(ValidationError, match="covers 1 devices"), cr.savepoint():
        _asset(m5, "OVER")
    m5.msp.write({"device_count": 2})  # the uplift, billed per device
    _asset(m5, "UPLIFTED")
    with pytest.raises(ValidationError, match="cannot drop"), cr.savepoint():
        m5.msp.write({"device_count": 1})


def test_a_contract_with_no_count_bills_every_enrolled_device(m5):
    m5.msp.write({"device_count": 0, "per_device_monthly": 1000.0})
    _asset(m5, "B1")
    m5.msp.invalidate_recordset()
    assert m5.msp.monthly_value == 1000.0 * len(m5.msp.asset_ids)


# --- BRU-RMS-10 -------------------------------------------------------------


def test_the_third_incident_on_an_asset_needs_a_problem_record(m5):
    first = _alert(m5)
    _as(first, m5.eng).action_resolve(note="reseated the cable")
    _alert(m5)
    third = _alert(m5)
    assert third.recurring
    with pytest.raises(UserError, match="problem record"):
        _as(third, m5.eng).action_resolve(note="reseated the cable again")
    problem = p0._change(m5, kind="problem", name="Flapping uplink on the core switch")
    with pytest.raises(ValidationError, match="problem record"):
        third.write({"problem_id": p0._change(m5, name="a change").id})
    _as(third, m5.eng).write({"problem_id": problem.id})
    _as(third, m5.eng).action_resolve(note="linked to the uplink problem; cable replaced")
    assert third.state == "resolved"


def test_a_runbook_does_not_close_an_unlinked_recurring_incident(m5):
    _alert(m5)
    _alert(m5)
    third = _alert(m5)
    book = _as(m5.env["fix.msp.runbook"], m5.eng).create(
        {
            "name": "Bounce port",
            "script": "bounce",
            "auto_resolve_alert": True,
            "operating_unit_id": m5.ou.id,
        }
    )
    _as(book, m5.eng).action_execute(alert_id=third.id, evidence="port bounced, link back up")
    assert third.state == "new"  # logged, not resolved: it needs its problem record
    assert m5.env["fix.msp.runbook.run"].search_count([("runbook_id", "=", book.id)]) == 1


# --- BRU-RMS-11 -------------------------------------------------------------


def test_offboarding_completes_only_with_every_agent_removed_and_access_revoked(m5, call):
    msp = _as(m5.msp, m5.eng)
    with pytest.raises(UserError, match="during offboarding"):
        _as(m5.asset, m5.eng).action_record_agent_removal(evidence="uninstalled via RMM")
    msp.action_start_offboarding()
    assert msp.lifecycle == "offboarding"
    with pytest.raises(UserError, match="refused"):
        _session(m5)  # no new work on a contract being offboarded
    with pytest.raises(UserError, match="agent is still on"):
        msp.action_complete_offboarding()
    with pytest.raises(UserError, match="evidence"):
        _as(m5.asset, m5.eng).action_record_agent_removal(evidence="done")
    _as(m5.asset, m5.eng).action_record_agent_removal(
        evidence="agent uninstalled; RMM shows 0 check-ins since 10:05"
    )
    with pytest.raises(UserError, match="access"):
        msp.action_complete_offboarding()
    out = call(
        m5.env(user=m5.eng.id),
        "model_action",
        model="fix.msp.contract",
        ids=[m5.msp.id],
        method="action_record_access_revoked",
        kwargs={"evidence": "portal users archived; VPN keys revoked; vault entries deleted"},
    )
    assert out.get("success"), out
    msp.action_complete_offboarding()
    assert msp.lifecycle == "offboarded" and msp.offboarded_by_id == m5.eng


def test_lifecycle_cannot_be_typed_on_the_form(m5, call):
    out = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.contract",
        record_id=m5.msp.id,
        values={"lifecycle": "offboarded"},
    )
    assert out.get("error"), out
    assert m5.msp.lifecycle == "in_service"


def test_a_plain_user_cannot_offboard(m5):
    with pytest.raises(UserError, match="MSP Engineer"):
        _as(m5.msp, m5.plain).action_start_offboarding()


# --- BRU-RMS-12 -------------------------------------------------------------


def _ended_session(m5, days_ago):
    session = _session(m5)
    session._guarded().write(
        {
            "started": True,
            "ended_at": fields.Datetime.now() - timedelta(days=days_ago),
            "recording_url": "rec://session/%s" % session.id,
        }
    )
    return session


def test_opening_a_recording_is_logged(m5):
    session = _ended_session(m5, 1)
    out = _as(session, m5.eng).action_open_recording()
    assert out["secret"] == session.recording_url
    assert session.recording_access_count == 1
    assert "opened by" in session.message_ids[0].body
    with pytest.raises(UserError, match="MSP Engineer"):
        _as(session, m5.plain).action_open_recording()


def test_recordings_past_retention_are_purged(m5):
    m5.msp.write({"recording_retention_days": 30})
    old = _ended_session(m5, 40)
    recent = _ended_session(m5, 5)
    m5.env["fix.remote.session"].cron_purge_recordings()
    assert not old.recording_url and old.recording_purged_at
    assert recent.recording_url
    with pytest.raises(UserError, match="purged"):
        _as(old, m5.eng).action_open_recording()


def test_the_new_rules_are_scheduled(m5):
    cron = m5.env.ref("cd_msp_contract.ir_cron_msp_purge_recordings")
    assert cron.active


# --- BRU-RMS-03 -------------------------------------------------------------


def test_a_credential_is_never_written_in_a_ticket_or_note(m5, call):
    out = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.alert",
        record_id=False,
        values={
            "msp_contract_id": m5.msp.id,
            "asset_id": m5.asset.id,
            "source": "phone",
            "message": "Client cannot log in, admin password: Hunter2!",
        },
    )
    assert out.get("error") and "credential vault" in out["error"]
    alert = _alert(m5, message="Client reports the shared printer is not printing")
    with pytest.raises(ValidationError, match="credential vault"):
        _as(alert, m5.eng).action_resolve(note="reset it, new pwd=Winter2026")
    _as(alert, m5.eng).action_resolve(note="password reset done; see vault entry ACME-PRN")
    with pytest.raises(ValidationError, match="credential vault"):
        p0._change(m5, description="rotate the VPN, api key = sk-live-123")
