"""A11 fix B1 — M63 KPIs and packs count only what is real.

Companion of addons/domain/i_governance/cd_workflow_engine/tests/
test_aut_bindings.py (the model side). These tests pin the portal-facing
numbers: the automation coverage tiles, the two register-based rates
(automation rate = coverage, STP share = straight-through), escalations MTD
with asserted basis, and the scheduled_jobs pack with its gate.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from odoo.addons.cd_p03_portal.controllers.a11 import m63
from odoo.exceptions import AccessError, UserError

DOA = "cd_workflow_engine.group_doa_administrator"


def _clear_register(env):
    env["fix.automation.register"].sudo().search([]).unlink()


def _load_catalogue(env):
    automations = env["fix.automation"].with_context(active_test=False)
    automations.search([]).unlink()
    automations.action_load_register()
    return automations.search([])


def _plain_user(env, login):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
            }
        )
    )


# --------------------------------------------------------------- the rates
def test_rates_are_none_without_registered_routine_work(odoo_env):
    _clear_register(odoo_env)
    kpis = m63.kpis(odoo_env)
    assert kpis["automation_rate"] is None, "no denominator must read None, never 0.0"
    assert kpis["stp_share"] is None, "STP must not fall back to instances again"
    pack = m63.automation_rate(odoo_env)
    assert "not measurable" in pack["title"]
    assert pack["totals"]["rate"] is None


def test_rates_follow_the_stated_formulas(odoo_env):
    """Hand-computed: 100/mo not automated + 300/mo automated at 50% STP.
    automation_rate = 300/400 = 75.0 (coverage); stp_share = 150/400 = 37.5
    (straight-through volume)."""
    _clear_register(odoo_env)
    aut = (
        odoo_env["fix.automation"]
        .with_context(active_test=False)
        .create(
            {
                "code": "AUT-920",
                "trigger": "Nightly",
                "action": "Reconcile settlements",
                "engine": "odoo_method",
                "engine_ref": "method:fix.service.order._flag_rework",
                "implementation": "full",
            }
        )
    )
    Register = odoo_env["fix.automation.register"].sudo()
    Register.create(
        {"name": "Key in walk-in intakes", "process_area": "Front Desk", "volume_per_month": 100}
    )
    Register.create(
        {
            "name": "Reconcile bKash settlements",
            "process_area": "Treasury",
            "volume_per_month": 300,
            "automated": True,
            "automation_id": aut.id,
            "stp_rate": 50.0,
        }
    )
    kpis = m63.kpis(odoo_env)
    assert kpis["automation_rate"] == 75.0
    assert kpis["stp_share"] == 37.5
    pack = m63.automation_rate(odoo_env)
    areas = {r["area"]: r for r in pack["rows"]}
    assert areas["Treasury"]["rate"] == 50.0
    assert areas["Front Desk"]["rate"] == 0.0
    assert pack["totals"]["rate"] == 37.5
    assert "37.5%" in pack["title"]


# ------------------------------------------------------- coverage tiles
def test_automation_tiles_count_coverage_not_rows(odoo_env):
    rows = _load_catalogue(odoo_env)
    kpis = m63.kpis(odoo_env)
    assert kpis["automations"] == len(rows.filtered(lambda r: r.coverage_state == "implemented"))
    assert kpis["automations_partial"] == len(
        rows.filtered(lambda r: r.coverage_state == "partial")
    )
    assert kpis["automations_planned"] == len(
        rows.filtered(lambda r: r.coverage_state == "planned")
    )
    assert kpis["automations_broken"] == 0
    assert kpis["automations"] + kpis["automations_partial"] + kpis["automations_planned"] == 60
    # a row claiming an implementation its reference cannot back is counted as
    # broken, and drops out of 'implemented'
    full = rows.filtered(lambda r: r.coverage_state == "implemented")[0]
    full._catalogue_write({"engine_ref": "method:fix.service.order.no_such_method"})
    assert m63.kpis(odoo_env)["automations"] == kpis["automations"] - 1
    assert m63.kpis(odoo_env)["automations_broken"] == 1


# ------------------------------------------------------ escalations MTD
def _escalated_history(env):
    request = env["fix.approval.request"].create(
        {
            "res_model": "fix.automation",
            "res_id": 1,
            "requested_by_id": env.user.id,
        }
    )
    return env["fix.approval.history"].create(
        {
            "request_id": request.id,
            "res_model": "fix.automation",
            "res_id": 1,
            "event": "escalated",
            "user_id": env.user.id,
            "at": datetime.now(),
        }
    )


def test_escalations_mtd_counts_the_approval_history(odoo_env):
    before = m63.kpis(odoo_env)["escalations_mtd"]
    _escalated_history(odoo_env)
    after = m63.kpis(odoo_env)["escalations_mtd"]
    if before is not None:
        assert after == before + 1
    else:
        assert after is None  # unreadable stays unreadable, never a smaller count
    # an escalation from a previous month does not count (history is
    # append-only through the ORM, so it is aged by SQL in the test only)
    old = _escalated_history(odoo_env)
    odoo_env.cr.execute(
        "UPDATE fix_approval_history SET at = %s WHERE id = %s",
        [datetime.now() - timedelta(days=40), old.id],
    )
    assert m63.kpis(odoo_env)["escalations_mtd"] == after


def test_escalations_mtd_is_none_when_history_is_unreadable(odoo_env, monkeypatch):
    History = odoo_env["fix.approval.history"]

    def _refuse(*args, **kwargs):
        raise AccessError("no history for you")

    monkeypatch.setattr(type(History), "search_count", _refuse)
    assert m63.kpis(odoo_env)["escalations_mtd"] is None


# --------------------------------------------------------- scheduled jobs
def test_scheduled_jobs_refuses_a_plain_internal_user(odoo_env):
    user = _plain_user(odoo_env, "b1_plain_jobs")
    with pytest.raises(UserError, match="reserved for DoA Administrators"):
        m63.scheduled_jobs(odoo_env(user=user))


def test_scheduled_jobs_lists_the_real_cron_estate_for_a_doa_admin(odoo_env):
    user = _plain_user(odoo_env, "b1_doa_jobs")
    user.group_ids += odoo_env.ref(DOA)
    pack = m63.scheduled_jobs(odoo_env(user=user))
    rows = pack["rows"]
    assert rows, "the estate has scheduled actions"
    names = {r["job"] for r in rows}
    assert "M63: remind and escalate overdue approvals" in names
    module_col = {r["job"]: r["module"] for r in rows}
    assert (
        module_col["M63: remind and escalate overdue approvals"]
        == "cd_workflow_engine.ir_cron_approval_escalate_overdue"
    )
    assert all(r["module"] != "—" for r in rows), "every cron names its owning xmlid"
    # sorted by next run (the display is a fixed-width local timestamp)
    next_runs = [r["next_run"] for r in rows if r["next_run"] != "—"]
    assert next_runs == sorted(next_runs)
    notes = " ".join(pack["notes"])
    assert "Odoo scheduled actions" in notes
    assert "Airflow DAGs are not used" in notes


# -------------------------------------------------------- rule change log
def test_rule_change_log_prints_the_callers_timezone(odoo_env):
    odoo_env["fix.business.rule"].create(
        {
            "code": "B1-TZ-001",
            "name": "Timezone witness",
            "rule_type": "validation",
            "expression": "always true",
        }
    )
    pack = m63.rule_change_log(odoo_env)
    assert pack["labels"]["changed_on"] == "Changed On (Asia/Dhaka)"
    assert "Asia/Dhaka" in " ".join(pack["notes"])
    row = next(r for r in pack["rows"] if r["code"] == "B1-TZ-001")
    # tz in the env is Asia/Dhaka: the printed time is UTC + 6
    rule = odoo_env["fix.business.rule"].search([("code", "=", "B1-TZ-001")])
    expected = (rule.last_changed_on + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
    assert row["changed_on"] == expected
