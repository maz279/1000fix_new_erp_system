"""M05 sub-module 10 "Onboarding Projects" (capture audit pass 2, 2026-11-18).

The page's button opened the MSP contract. FR-RMS-047 (P1) and the client
onboarding lifecycle (spec 8.3) make the onboarding project the record it
captures: its eight-step checklist, coverage verified against the agreed
share, and the go-live from which SLA clocks are contractually binding.

Every rule is proved both ways (the bypass refused, the legitimate path
works), through the workspace controller where the screen uses it, as a
non-admin MSP engineer.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import UserError

from . import test_a02_p0_m05 as p0

m5 = p0.m5
call = p0.call
_as = p0._as


def _start(m5, call, user=None, contract=None, **values):
    vals = {"msp_contract_id": (contract or m5.msp).id, "kickoff_date": str(fields.Date.today())}
    vals.update(values)
    return call(
        m5.env(user=(user or m5.eng).id),
        "model_write",
        model="fix.msp.onboarding",
        record_id=False,
        values=vals,
    )


def _project(m5, call, **values):
    out = _start(m5, call, **values)
    assert "error" not in out, out
    return m5.env["fix.msp.onboarding"].search([("msp_contract_id", "=", m5.msp.id)])


def _mark(m5, call, step, evidence="checked on site with the client IT lead", user=None):
    return call(
        m5.env(user=(user or m5.eng).id),
        "model_action",
        model="fix.msp.onboarding.step",
        ids=[step.id],
        method="action_mark_done",
        kwargs={"evidence": evidence},
    )


def _step(project, code):
    return project.step_ids.filtered(lambda s: s.code == code)


def _ready_estate(m5, reporting=4):
    """Enrol up to the contract's four covered devices, ``reporting`` of them
    with a fresh check-in."""
    assets = m5.asset
    for i in range(3):
        assets |= m5.env["fix.monitored.asset"].create(
            {
                "msp_contract_id": m5.msp.id,
                "agent_id": "AGT-ONB-%s-%d" % (m5.msp.id, i),
                "operating_unit_id": m5.ou.id,
            }
        )
    now = fields.Datetime.now()
    for i, asset in enumerate(assets):
        seen = now if i < reporting else now - timedelta(days=3)
        asset.write({"last_seen": seen})
    return assets


def _prerequisites(m5):
    m5.env["fix.msp.client.contact"].create(
        {
            "msp_contract_id": m5.msp.id,
            "partner_id": m5.contact.id,
            "operating_unit_id": m5.ou.id,
        }
    )
    m5.env["fix.msp.runbook"].create(
        {"name": "Restart spooler", "script": "net stop spooler", "scope_contract_id": m5.msp.id}
    )
    m5.env["fix.msp.alert.rule"].create(
        {
            "name": "Disk below 5 GB",
            "metric": "disk_free_gb",
            "operator": "below",
            "threshold": 5.0,
            "severity": "major",
            "msp_contract_id": m5.msp.id,
        }
    )


def _complete_checklist(m5, call, project):
    for step in project.step_ids:
        out = _mark(m5, call, step)
        assert out.get("success"), (step.code, out)


# --- starting the project -------------------------------------------------------


def test_an_engineer_starts_the_onboarding_from_the_page_form(m5, call):
    out = _start(m5, call, user=m5.plain)
    assert out.get("error"), out  # not an MSP engineer
    project = _project(m5, call)
    assert project.state == "initiated"
    assert project.name == "Onboarding: %s" % m5.msp.name
    assert project.company_id == m5.msp.company_id
    assert project.operating_unit_id == m5.ou
    assert project.started_by_id == m5.eng
    assert project.step_ids.mapped("code") == [
        "discovery",
        "agents",
        "baseline",
        "contacts",
        "portal",
        "runbooks",
        "alerts",
        "sla",
    ]
    assert not any(project.step_ids.mapped("done"))


def test_one_onboarding_per_contract_and_never_on_a_departing_client(m5, call):
    _project(m5, call)
    again = _start(m5, call)
    assert again.get("error"), again
    _as(m5.other, m5.eng).action_start_offboarding()
    out = _start(m5, call, contract=m5.other)
    assert out.get("error") and "refused" in out["error"], out


def test_the_checklist_and_the_go_live_cannot_be_typed(m5, call):
    project = _project(m5, call)
    step = project.step_ids[0]
    out = call(
        m5.env(user=m5.eng.id),
        "model_write",
        model="fix.msp.onboarding.step",
        record_id=step.id,
        values={"done": True, "evidence": "typed in"},
    )
    assert out.get("error"), out
    with pytest.raises(UserError, match="cannot be set directly"):
        _as(step, m5.eng).write({"done": True})
    with pytest.raises(UserError, match="cannot be set directly"):
        _as(project, m5.eng).write({"state": "live"})
    with pytest.raises(UserError, match="not added"):
        _as(m5.env["fix.msp.onboarding.step"], m5.eng).create(
            {"onboarding_id": project.id, "code": "portal", "name": "Extra"}
        )


# --- the checklist ----------------------------------------------------------------


def test_a_step_needs_its_evidence_and_an_engineer(m5, call):
    project = _project(m5, call)
    discovery = _step(project, "discovery")
    out = _mark(m5, call, discovery, evidence="done")
    assert not out.get("success") and "evidence" in out["error"], out
    out = _mark(m5, call, discovery, user=m5.plain)
    assert not out.get("success"), out
    out = _mark(m5, call, discovery, evidence="network scan: 4 endpoints, 1 printer, 1 switch")
    assert out.get("success"), out
    assert discovery.done and discovery.done_by_id == m5.eng
    assert project.state == "onboarding"
    out = _mark(m5, call, discovery)
    assert not out.get("success") and "already done" in out["error"], out


@pytest.mark.parametrize(
    "code, refusal",
    [
        ("baseline", "has no reading yet"),
        ("contacts", "may raise tickets"),
        ("runbooks", "no active runbook"),
        ("alerts", "no active alert rule"),
    ],
)
def test_verified_steps_are_refused_until_the_estate_shows_them(m5, call, code, refusal):
    project = _project(m5, call)
    out = _mark(m5, call, _step(project, code))
    assert not out.get("success") and refusal in out["error"], out
    _ready_estate(m5)
    _prerequisites(m5)
    out = _mark(m5, call, _step(project, code))
    assert out.get("success"), out


def test_agent_deployment_needs_an_enrolled_asset(m5, call):
    m5.asset.unlink()
    project = _project(m5, call)
    out = _mark(m5, call, _step(project, "agents"))
    assert not out.get("success") and "no asset is enrolled" in out["error"], out


def test_a_global_runbook_and_rule_count_for_every_contract(m5, call):
    project = _project(m5, call)
    m5.env["fix.msp.runbook"].create({"name": "Clear temp", "script": "del /q %TEMP%"})
    m5.env["fix.msp.alert.rule"].create(
        {"name": "Any CPU", "metric": "cpu_utilization_pct", "operator": "above", "threshold": 95.0}
    )
    assert _mark(m5, call, _step(project, "runbooks")).get("success")
    assert _mark(m5, call, _step(project, "alerts")).get("success")


# --- going live -----------------------------------------------------------------


def _go_live(m5, call, project, user=None):
    return call(
        m5.env(user=(user or m5.eng).id),
        "model_action",
        model="fix.msp.onboarding",
        ids=[project.id],
        method="action_go_live",
        kwargs={},
    )


def test_go_live_needs_every_step_done(m5, call):
    _ready_estate(m5)
    _prerequisites(m5)
    project = _project(m5, call)
    for step in project.step_ids[:-1]:
        assert _mark(m5, call, step).get("success")
    out = _go_live(m5, call, project)
    assert not out.get("success") and "SLA configuration still to do" in out["error"], out
    assert not m5.msp.service_live_at


def test_go_live_needs_the_agreed_coverage(m5, call):
    _ready_estate(m5, reporting=3)  # 3 of 4 covered devices = 75 %
    _prerequisites(m5)
    project = _project(m5, call)
    _complete_checklist(m5, call, project)
    assert project.coverage_pct == 75.0
    out = _go_live(m5, call, project)
    assert not out.get("success") and "3 of 4 covered devices" in out["error"], out
    _as(project, m5.eng).write({"coverage_target_pct": 75.0})
    out = _go_live(m5, call, project)
    assert out.get("success"), out
    assert project.state == "live" and project.live_by_id == m5.eng
    assert project.live_coverage_pct == 75.0
    assert m5.msp.service_live_at == project.live_at


def test_a_live_service_closes_its_onboarding(m5, call):
    _ready_estate(m5)
    _prerequisites(m5)
    project = _project(m5, call)
    _complete_checklist(m5, call, project)
    assert _go_live(m5, call, project).get("success")
    assert not _go_live(m5, call, project).get("success")
    with pytest.raises(UserError, match="closed record"):
        _as(project, m5.eng).write({"coverage_target_pct": 50.0})
    with pytest.raises(UserError, match="evidence"):
        _as(project, m5.eng).sudo().unlink()


# --- SLA clocks bind from go-live (spec 8.3) --------------------------------------


def _breached_alert(m5, contract, asset, days_ago):
    alert = m5.env["fix.msp.alert"].create(
        {
            "msp_contract_id": contract.id,
            "asset_id": asset.id,
            "severity": "major",
            "message": "offline %d days ago" % days_ago,
        }
    )
    when = fields.Datetime.now() - timedelta(days=days_ago)
    m5.env.cr.execute("UPDATE fix_msp_alert SET create_date = %s WHERE id = %s", (when, alert.id))
    alert.invalidate_recordset(["create_date"])
    return alert


def test_sla_clocks_bind_only_from_the_go_live(m5, call):
    old = _breached_alert(m5, m5.msp, m5.asset, days_ago=5)
    new = _breached_alert(m5, m5.msp, m5.asset, days_ago=1)
    alerts = old | new
    # no onboarding project: the whole history binds, as before
    assert m5.msp._msp_period_sla(alerts)["breached"] == 2
    # being onboarded: nothing binds yet
    project = _project(m5, call)
    assert m5.msp._msp_period_sla(alerts)["breached"] == 0
    # live two days ago: only the alert raised since binds
    m5.msp.sudo().write({"service_live_at": fields.Datetime.now() - timedelta(days=2)})
    project._guarded().write({"state": "live"})
    sla = m5.msp._msp_period_sla(alerts)
    assert sla["breached"] == 1 and sla["attainment"] == 0.0


def test_a_contract_with_no_onboarding_is_not_affected(m5):
    alert = _breached_alert(m5, m5.other, m5.other_asset, days_ago=2)
    assert m5.other._msp_period_sla(alert)["breached"] == 1
