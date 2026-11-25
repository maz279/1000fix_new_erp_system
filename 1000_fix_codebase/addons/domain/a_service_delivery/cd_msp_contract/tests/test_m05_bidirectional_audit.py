"""M05 bidirectional audit (2026-11-13): the screens on 8069 against the
backend, and the backend against the business rules.

Each test pins a defect the audit found:
  BRU-RMS-08  a change needed a rollback plan only when high risk
  BRU-RMS-04  an asset with no agent report was never reported as a gap
  T-08        a runbook execution was logged on the first asset in scope,
              never as failed, and the log had no screen
  FR-RMS-039  the backup log report was a "not built yet" placeholder
  reports     the period the screen sends was ignored, a month with no SLA
              figure averaged as 0 %, and "remote resolution" divided
              resolved alerts by "ticketed or resolved"

Actors are non-admin users holding only their M05 role. ``odoo_env``
(addons/conftest.py) rolls back after every test.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers.a02 import m05 as ctl
from odoo.exceptions import AccessError, UserError, ValidationError

from . import test_a02_p0_m05 as p0

m5 = p0.m5
call = p0.call
_as = p0._as
_window = p0._window
GUARD = p0.GUARD


def _alert(m5, asset=None, **vals):
    base = {
        "msp_contract_id": m5.msp.id,
        "asset_id": (asset or m5.asset).id,
        "message": "disk pressure",
    }
    base.update(vals)
    return _as(m5.env["fix.msp.alert"], m5.eng).create(base)


def _book(m5, **vals):
    base = {
        "name": "Clear temp",
        "script": "1. clear temp",
        "scope_contract_id": m5.msp.id,
        "operating_unit_id": m5.ou.id,
    }
    base.update(vals)
    return _as(m5.env["fix.msp.runbook"], m5.eng).create(base)


# --- BRU-RMS-08: every change carries its rollback plan ---------------------


def test_a_medium_risk_change_needs_a_rollback_plan(m5):
    ch = p0._change(m5, risk="medium", requested_by=m5.emp.id, rollback_plan="")
    with pytest.raises(UserError, match="no rollback plan"):
        _as(ch, m5.eng).action_request_approval()
    _as(ch, m5.eng).write({"rollback_plan": "restore the saved firewall config"})
    _as(ch, m5.eng).action_request_approval()  # with its plan, it is sent


def test_a_problem_record_needs_no_rollback_plan(m5):
    problem = p0._change(m5, kind="problem", risk="low", rollback_plan="")
    problem._msp_check_rollback()  # analysis, not a change: no refusal


# --- T-08: runbook executions on the right asset, with their outcome --------


def test_an_execution_without_an_asset_is_refused_when_the_scope_has_several(m5):
    m5.env["fix.monitored.asset"].create(
        {"msp_contract_id": m5.msp.id, "agent_id": "AGT-AUD-2", "operating_unit_id": m5.ou.id}
    )
    book = _book(m5)
    with pytest.raises(UserError, match="Name the asset"):
        _as(book, m5.eng).action_execute(evidence="cleared 4 GB of temp files")
    assert not m5.env["fix.msp.runbook.run"].search_count([("runbook_id", "=", book.id)])


def test_an_alerts_execution_is_logged_on_the_alerts_asset(m5):
    second = m5.env["fix.monitored.asset"].create(
        {"msp_contract_id": m5.msp.id, "agent_id": "AGT-AUD-3", "operating_unit_id": m5.ou.id}
    )
    alert = _alert(m5, asset=second)
    book = _book(m5)
    _as(book, m5.eng).action_execute(alert_id=alert.id, evidence="cleared temp on the host")
    run = m5.env["fix.msp.runbook.run"].search([("runbook_id", "=", book.id)])
    assert run.asset_id == second and run.alert_id == alert


def test_an_alert_of_another_asset_or_an_asset_out_of_scope_is_refused(m5):
    alert = _alert(m5)
    second = m5.env["fix.monitored.asset"].create(
        {"msp_contract_id": m5.msp.id, "agent_id": "AGT-AUD-4", "operating_unit_id": m5.ou.id}
    )
    book = _book(m5)
    with pytest.raises(UserError, match="not on"):
        _as(book, m5.eng).action_execute(asset=second.id, alert_id=alert.id)
    with pytest.raises(UserError, match="scoped to"):
        _as(book, m5.eng).action_execute(asset=m5.other_asset.id)


def test_a_failed_execution_is_logged_and_never_resolves_the_alert(m5):
    alert = _alert(m5)
    book = _book(m5, auto_resolve_alert=True)
    with pytest.raises(UserError, match="what failed"):
        _as(book, m5.eng).action_execute(alert_id=alert.id, outcome="failed", evidence="no")
    _as(book, m5.eng).action_execute(
        alert_id=alert.id, outcome="failed", evidence="temp share locked by backup agent"
    )
    run = m5.env["fix.msp.runbook.run"].search([("runbook_id", "=", book.id)])
    assert (run.state, run.outcome) == ("failed", "failed")
    assert alert.state == "new"


def test_an_execution_is_logged_on_the_workspace_form_and_is_then_evidence(m5, call):
    alert = _alert(m5)
    book = _book(m5, auto_resolve_alert=True)
    out = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.runbook.run",
        record_id=False,
        values={
            "runbook_id": book.id,
            "asset_id": m5.asset.id,
            "alert_id": alert.id,
            "outcome": "success",
            "output_note": "freed 12 GB; disk at 61 %",
        },
    )
    assert "error" not in out, out
    run = m5.env["fix.msp.runbook.run"].search([("runbook_id", "=", book.id)])
    assert run.state == "success" and run.started_at and run.finished_at
    assert run.logged_by_id == m5.eng  # who is accountable for it (T-08)
    assert alert.state == "resolved" and "freed 12 GB" in alert.resolution_note
    with pytest.raises(UserError, match=GUARD):
        _as(run, m5.eng).write({"output_note": "rewritten later"})
    with pytest.raises(UserError, match=GUARD):
        _as(run, m5.eng).write({"outcome": "failed"})


def test_only_an_msp_engineer_logs_an_execution(m5):
    book = _book(m5)
    with pytest.raises((AccessError, UserError)):
        _as(m5.env["fix.msp.runbook.run"], m5.plain).create(
            {"runbook_id": book.id, "asset_id": m5.asset.id, "output_note": "did it"}
        )


# --- BRU-RMS-04: an unreported asset is a coverage gap ----------------------


def _age(asset, hours):
    asset.env.cr.execute(
        "UPDATE fix_monitored_asset SET last_seen = %s WHERE id = %s",
        (fields.Datetime.now() - timedelta(hours=hours), asset.id),
    )
    asset.invalidate_recordset()


def test_an_asset_silent_for_24_hours_raises_one_coverage_gap(m5):
    Asset = m5.env["fix.monitored.asset"]
    _age(m5.asset, 30)
    Asset.cron_coverage_gaps()
    gap = m5.env["fix.msp.alert"].search(
        [("asset_id", "=", m5.asset.id), ("coverage_gap", "=", True)]
    )
    assert len(gap) == 1 and gap.severity == "major" and "Coverage gap" in gap.message
    Asset.cron_coverage_gaps()  # still silent: no second alert
    assert (
        m5.env["fix.msp.alert"].search_count(
            [("asset_id", "=", m5.asset.id), ("coverage_gap", "=", True)]
        )
        == 1
    )
    with pytest.raises(UserError, match=GUARD):
        _as(gap, m5.eng).write({"coverage_gap": False})


def test_a_recently_seen_asset_is_no_gap_and_a_window_suppresses_it(m5):
    Asset = m5.env["fix.monitored.asset"]
    _age(m5.asset, 2)
    Asset.cron_coverage_gaps()
    assert not m5.env["fix.msp.alert"].search_count([("asset_id", "=", m5.asset.id)])
    _age(m5.asset, 30)
    win = _window(m5, m5.cm)
    _as(win, m5.cab).action_approve()
    Asset.cron_coverage_gaps()
    assert not m5.env["fix.msp.alert"].search_count([("asset_id", "=", m5.asset.id)])


def test_the_coverage_check_is_scheduled_hourly(m5):
    cron = m5.env.ref("cd_msp_contract.ir_cron_msp_coverage_gaps")
    assert cron.active and (cron.interval_number, cron.interval_type) == (1, "hours")


# --- FR-RMS-039: backup jobs ------------------------------------------------


def _job(m5, user=None, **vals):
    base = {"asset_id": m5.asset.id, "plan_ref": "Nightly file server", "outcome": "success"}
    base.update(vals)
    return _as(m5.env["fix.msp.backup.job"], user or m5.eng).create(base)


def test_a_failed_backup_raises_one_alert_per_plan(m5):
    ok = _job(m5, restore_tested=True)
    assert not ok.alert_id and ok.consecutive_failures == 0
    with pytest.raises(UserError, match="what failed"):
        _job(m5, outcome="failed")
    first = _job(m5, outcome="failed", note="VSS snapshot timed out at 02:10")
    assert first.alert_id.severity == "major" and "Backup failed" in first.alert_id.message
    second = _job(m5, outcome="partial", note="2 of 9 shares skipped, locked files")
    assert second.alert_id == first.alert_id  # one open alert per plan
    assert second.consecutive_failures == 2
    assert first.msp_contract_id == m5.msp


def test_a_backup_job_is_evidence(m5):
    job = _job(m5)
    with pytest.raises(UserError, match=GUARD):
        _as(job, m5.eng).write({"outcome": "failed"})
    with pytest.raises((AccessError, UserError)):
        _job(m5, user=m5.plain)
    with pytest.raises(ValidationError, match="future"):
        _job(m5, run_at=fields.Datetime.now() + timedelta(days=1))


def test_the_backup_log_report_reads_the_jobs(m5):
    _job(m5, outcome="failed", note="tape library offline overnight")
    rep = ctl.REPORTS["backup_log"](m5.env)
    assert rep["rows"] and rep["rows"][0]["outcome"] == "Failed"
    assert "not built" not in str(rep)


# --- reports and KPIs -------------------------------------------------------


def test_period_reports_honour_the_period(m5):
    _alert(
        m5, source="phone", message="printer down", reported_by_contact_id=_reporting_contact(m5).id
    )
    today = fields.Date.context_today(m5.env["fix.msp.alert"])
    last_year = (today - timedelta(days=400), today - timedelta(days=370))
    now = (today, today)
    for key in ("remote_resolution", "alert_conversion"):
        empty = ctl.REPORTS[key](m5.env, date_from=last_year[0], date_to=last_year[1])
        full = ctl.REPORTS[key](m5.env, date_from=now[0], date_to=now[1])
        assert empty != full, key
    rr = ctl.REPORTS["remote_resolution"](m5.env, date_from=last_year[0], date_to=last_year[1])
    assert rr["rows"][0]["value"] == 0


def test_remote_resolution_counts_resolutions_without_a_service_order(m5):
    remote = _alert(m5, message="fixed over RustDesk")
    _as(remote, m5.eng).action_resolve(note="driver reinstalled remotely")
    _alert(m5, message="still open")
    c = ctl._resolution_counts(m5.env, [("msp_contract_id", "=", m5.msp.id)])
    assert (c["raised"], c["resolved"], c["remote"], c["open"], c["rate"]) == (2, 1, 1, 1, 100.0)


def test_a_month_without_a_figure_is_not_averaged_as_zero(m5):
    Report = m5.env["fix.msp.service.report"]._guarded()
    Report.create({"msp_contract_id": m5.msp.id, "period_label": "2026-08", "sla_attainment": 0.8})
    Report.create({"msp_contract_id": m5.msp.id, "period_label": "2026-09"})
    rows = ctl.REPORTS["sla_by_client"](m5.env)["rows"]
    row = next(r for r in rows if r["contract"] == m5.msp.name)
    assert (row["avg_attainment_pct"], row["periods"], row["unmeasured"]) == (80.0, 1, 1)


def test_the_credit_register_filters_by_service_month(m5):
    Credit = m5.env["fix.msp.sla.credit"]._guarded()
    Credit.create({"msp_contract_id": m5.msp.id, "period_label": "2026-03", "reason": "t"})
    march = ctl.REPORTS["sla_credit_register"](m5.env, date_from="2026-03-01", date_to="2026-03-31")
    may = ctl.REPORTS["sla_credit_register"](m5.env, date_from="2026-05-01", date_to="2026-05-31")
    assert any(r.get("period") == "2026-03" for r in march["rows"])
    assert not any(r.get("period") == "2026-03" for r in may["rows"])


def test_open_msp_tickets_counts_a_phoned_in_ticket(m5):
    before = ctl.kpis(m5.env)["open_msp_tickets"]
    _alert(
        m5,
        source="phone",
        message="client phoned: VPN down",
        reported_by_contact_id=_reporting_contact(m5).id,
    )
    _alert(m5, message="monitoring alert, not a ticket")
    assert ctl.kpis(m5.env)["open_msp_tickets"] == before + 1


def test_every_report_answers_without_a_placeholder(m5):
    for key, report in ctl.REPORTS.items():
        out = report(m5.env, date_from="2026-01-01", date_to="2026-12-31")
        assert out["cols"] and all(c in out["labels"] for c in out["cols"]), key
        assert "not built" not in str(out), key


def _reporting_contact(m5):
    """The client's IT lead, registered and allowed to raise tickets (FR-RMS-049)."""
    return m5.env["fix.msp.client.contact"].create(
        {"msp_contract_id": m5.msp.id, "partner_id": m5.contact.id, "role": "it_manager"}
    )
