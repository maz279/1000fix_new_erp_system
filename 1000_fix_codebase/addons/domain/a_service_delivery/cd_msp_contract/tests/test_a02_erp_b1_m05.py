# ruff: noqa: F401, F811 (the m5 fixture is imported, and named as test parameters)
"""A02 ERP audit (2026-11-19), builder stream B1, M05 Remote Support & MSP.

Each finding both ways, as non-admin users holding only the M05 roles they
need (the superuser is trusted by the guards).

``odoo_env`` (addons/conftest.py): rolled back after every test.
"""

import json
from datetime import date, datetime, timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_msp_contract.tests.test_a02_p1p2_cd_msp_contract import (
    GUARD,
    _alert,
    _as,
    _change,
    m5,
)
from odoo.addons.cd_p03_portal.controllers.a02 import m05 as m05_ctrl
from odoo.exceptions import UserError, ValidationError

REASON = "client addendum 2026-11 signed by the CFO"


def _fresh_msp(m5, **vals):
    """A new MSP contract on a new M08 term, with no service history."""
    return m5.env["fix.msp.contract"].create(
        {
            "name": "B1 MSP %s" % vals.pop("tag", "x"),
            "contract_id": m5.contract().id,
            "operating_unit_id": m5.ou.id,
            "device_count": 2,
            "per_device_monthly": 1000.0,
            **vals,
        }
    )


def _report(m5, msp, label, attainment):
    return (
        m5.env["fix.msp.service.report"]
        ._guarded()
        .create({"msp_contract_id": msp.id, "period_label": label, "sla_attainment": attainment})
    )


# ===================================================== M05-F2 onboarding


def test_f2_an_onboarding_cannot_suspend_a_contract_in_service(m5):
    _alert(m5, datetime(2026, 10, 3, 9, 0))  # m5.msp has delivered service
    with pytest.raises(UserError, match="already in service"):
        _as(m5.env["fix.msp.onboarding"], m5.eng).create({"msp_contract_id": m5.msp.id})


def test_f2_a_genuine_onboarding_suspends_only_until_go_live(m5):
    msp = _fresh_msp(m5, tag="onb")
    # A02 ERP pass 2 (D9): the SLA binds 30 days after the term start at the
    # latest; the fixture's term started 30 days ago, so start it today for
    # an onboarding that is still inside its window
    msp.contract_id.sudo()._guarded().write({"date_start": fields.Date.today()})
    asset = m5.env["fix.monitored.asset"].create(
        {"msp_contract_id": msp.id, "agent_id": "AGT-B1-ONB-%d" % m5.n}
    )
    _as(m5.env["fix.msp.onboarding"], m5.eng).create({"msp_contract_id": msp.id})
    alert = m5.env["fix.msp.alert"].create(
        {"msp_contract_id": msp.id, "asset_id": asset.id, "message": "x"}
    )
    far = fields.Datetime.now() + timedelta(days=60)
    assert msp._msp_period_sla(alert, as_of=far)["breached"] == 0  # not yet binding


def test_f2_a_project_on_a_contract_with_history_suspends_nothing(m5):
    """An onboarding opened (before this fix) on a contract already in
    service: its alerts stay measured."""
    msp = _fresh_msp(m5, tag="legacy")
    asset = m5.env["fix.monitored.asset"].create(
        {"msp_contract_id": msp.id, "agent_id": "AGT-B1-LEG-%d" % m5.n}
    )
    project = _as(m5.env["fix.msp.onboarding"], m5.eng).create({"msp_contract_id": msp.id})
    alert = m5.env["fix.msp.alert"].create(
        {"msp_contract_id": msp.id, "asset_id": asset.id, "message": "x"}
    )
    m5.env.flush_all()
    m5.env.cr.execute(
        "UPDATE fix_msp_alert SET sla_deadline = NULL, response_deadline = NULL, create_date = %s WHERE id = %s",
        (project.create_date - timedelta(days=40), alert.id),
    )
    m5.env.invalidate_all()
    assert msp._msp_onboarding_window() is None
    assert msp._msp_period_sla(alert)["breached"] == 1


# ===================================================== M05-F3 guarded terms


def test_f3_terms_and_lifecycle_are_not_engineer_writable(m5):
    for vals in (
        {"sla_target_pct": 50.0},
        {"per_device_monthly": 1.0},
        {"alert_resolve_hours_major": 400.0},
        {"coverage_window": "business"},
        {"contract_id": m5.contract().id},
        {"lifecycle": "offboarded"},
        {"service_live_at": fields.Datetime.now()},
    ):
        with pytest.raises(UserError, match=GUARD):
            _as(m5.msp, m5.eng).write(vals)
    # the form locks them on a saved contract, offers them on a new one
    assert "sla_target_pct" in m5.msp._fix_form_locked_fields()
    assert "sla_target_pct" not in m5.env["fix.msp.contract"].browse()._fix_form_locked_fields()


def test_f3_commercial_terms_are_typed_once_by_the_commercial_role(m5):
    Contract = m5.env["fix.msp.contract"]
    with pytest.raises(UserError, match="credit approver|SLA Credit"):
        _as(Contract, m5.eng).create(
            {"name": "eng", "contract_id": m5.contract().id, "per_device_monthly": 10.0}
        )
    plain = _as(Contract, m5.eng).create({"name": "eng", "contract_id": m5.contract().id})
    assert plain.sla_target_pct == 90.0 and not plain.per_device_monthly
    with pytest.raises(UserError, match=GUARD):
        _as(Contract, m5.eng).create(
            {"name": "x", "contract_id": m5.contract().id, "lifecycle": "offboarded"}
        )
    priced = _as(Contract, m5.fin).create(
        {"name": "fin", "contract_id": m5.contract().id, "per_device_monthly": 10.0}
    )
    assert priced.per_device_monthly == 10.0


def test_f3_terms_change_through_the_amendment_only(m5):
    msp = m5.msp
    with pytest.raises(UserError, match="SLA Credit Approver|role"):
        _as(msp, m5.eng).action_amend_terms(term="sla_target_pct", value="50", reason=REASON)
    with pytest.raises(UserError, match="reason"):
        _as(msp, m5.fin).action_amend_terms(term="sla_target_pct", value="50", reason="x")
    with pytest.raises(UserError, match="percentage"):
        _as(msp, m5.fin).action_amend_terms(term="sla_target_pct", value="150", reason=REASON)
    with pytest.raises(UserError, match="cannot be amended"):
        _as(msp, m5.fin).action_amend_terms(term="lifecycle", value="offboarded", reason=REASON)
    _as(msp, m5.fin).action_amend_terms(term="sla_target_pct", value="97.5", reason=REASON)
    assert msp.sla_target_pct == 97.5 and msp.terms_amended_by_id == m5.fin
    assert "Terms amended" in msp.message_ids[:1].body


def test_f3_an_approved_credit_keeps_the_terms_it_was_drafted_on(m5):
    report = _report(m5, m5.msp, "2026-09", 0.80)
    credit = (
        m5.env["fix.msp.sla.credit"]
        ._guarded()
        .create(
            {
                "msp_contract_id": m5.msp.id,
                "service_report_id": report.id,
                "period_label": "2026-09",
            }
        )
    )
    # 4 devices x 2500 = 10,000; target 95 %, attainment 80 % -> 15 %
    assert (credit.target_pct, credit.credit_amount) == (95.0, 1500.0)
    _as(m5.msp, m5.fin).action_amend_terms(
        reason=REASON, sla_target_pct="80", per_device_monthly="10"
    )
    credit._compute_amounts()  # whenever it recomputes, it reads the pinned terms
    assert (credit.target_pct, credit.credit_amount, credit.value_basis) == (
        95.0,
        1500.0,
        "contract",
    )


# ===================================================== M05-F4 uplift / base


def test_f4_raising_the_devices_publishes_the_uplift(m5):
    _as(m5.msp, m5.fin).action_amend_terms(term="device_count", value="6", reason=REASON)
    # A02 ERP pass 2 (M05-S06): every fee change publishes one event type
    event = m5.env["fix.event.outbox"].search(
        [("event_type", "=", "msp.commercial_terms_amended"), ("aggregate_id", "=", m5.msp.id)]
    )
    assert len(event) == 1
    payload = json.loads(event.payload)
    assert (payload["new_device_count"] - payload["old_device_count"]) == 2
    assert payload["monthly_delta"] == 5000.0


def test_f4_no_enrolment_without_a_contracted_count(m5):
    msp = _fresh_msp(m5, tag="nocount", device_count=0)
    with pytest.raises(ValidationError, match="no contracted device count"):
        m5.env["fix.monitored.asset"].create(
            {"msp_contract_id": msp.id, "agent_id": "AGT-B1-NC-%d" % m5.n}
        )


def test_f4_a_credit_is_a_share_of_what_was_invoiced(m5):
    report = _report(m5, m5.msp, "2026-08", 0.80)
    Contract = type(m5.env["fix.msp.contract"])
    with mock.patch.object(Contract, "_msp_invoiced_value", return_value=4000.0):
        credit = (
            m5.env["fix.msp.sla.credit"]
            ._guarded()
            .create(
                {
                    "msp_contract_id": m5.msp.id,
                    "service_report_id": report.id,
                    "period_label": "2026-08",
                }
            )
        )
    assert credit.value_basis == "invoiced" and credit.credit_base_value == 4000.0
    assert credit.credit_amount == 600.0  # 15 % of the invoiced 4,000, not of 10,000
    with pytest.raises(ValidationError, match="exceeds"):
        _as(credit, m5.eng).write({"manual_amount": 5000.0})


# ===================================================== M05-F8 pending alerts


def test_f8_the_report_waits_until_every_alert_can_be_judged(m5):
    now = fields.Datetime.now()
    _alert(m5, now - timedelta(hours=2))  # minor, 24 h target: still pending
    period = (now - timedelta(days=3), now + timedelta(days=1), "2099-01")
    with pytest.raises(UserError, match="still open inside their resolution target"):
        m5.msp._msp_monthly_report(period)
    assert m5.msp._msp_period_pending(period) == 1
    m5.env.cr.execute(
        "UPDATE fix_msp_alert SET sla_deadline = NULL, response_deadline = NULL, create_date = %s WHERE msp_contract_id = %s",
        (now - timedelta(hours=30), m5.msp.id),
    )
    m5.env.invalidate_all()
    report = m5.msp._msp_monthly_report(period)
    assert (report.breached_count, report.pending_count) == (1, 0)


def test_f8_the_cron_defers_a_month_with_pending_alerts(m5):
    Contract = m5.env["fix.msp.contract"]
    period = Contract._msp_previous_month()
    _alert(m5, period[1] - timedelta(minutes=5))
    with mock.patch.object(type(Contract), "_msp_period_pending", return_value=1):
        Contract.cron_monthly_service_reports()
    assert not m5.msp.report_ids.filtered(lambda r: r.period_label == period[2])
    Contract.cron_monthly_service_reports()
    assert m5.msp.report_ids.filtered(lambda r: r.period_label == period[2])


# ===================================================== M05-F14 credit report


def test_f14_a_credit_rests_on_its_own_contracts_report(m5):
    other = _fresh_msp(m5, tag="other")
    foreign = _report(m5, other, "2026-07", 0.5)
    with pytest.raises(ValidationError, match="another contract"), m5.env.cr.savepoint():
        m5.env["fix.msp.sla.credit"]._guarded().create(
            {
                "msp_contract_id": m5.msp.id,
                "service_report_id": foreign.id,
                "period_label": "2026-07",
            }
        )
    own = _report(m5, m5.msp, "2026-07", 0.5)
    credit = (
        m5.env["fix.msp.sla.credit"]
        ._guarded()
        .create(
            {"msp_contract_id": m5.msp.id, "service_report_id": own.id, "period_label": "2026-07"}
        )
    )
    fresh = m5.env["fix.msp.sla.credit"].browse(credit.id)  # outside the creating transition
    with pytest.raises(UserError, match="cannot change"):
        _as(fresh, m5.eng).write({"msp_contract_id": other.id})


# ===================================================== M05-F15 Dhaka months


def test_f15_the_report_month_is_the_dhaka_calendar_month(m5):
    start, end, label = m5.env["fix.msp.contract"]._msp_previous_month(date(2026, 11, 5))
    assert label == "2026-10"
    assert start == datetime(2026, 9, 30, 18, 0)  # 1 Oct 00:00 in Dhaka
    assert end.replace(microsecond=0) == datetime(2026, 10, 31, 17, 59, 59)


# ===================================================== M05-F18 patch defer / fail


def _patch(m5, ident="KB-B1"):
    upd = m5.env["fix.msp.patch.update"].create(
        {
            "msp_contract_id": m5.msp.id,
            "asset_id": m5.asset.id,
            "identifier": "%s-%d" % (ident, m5.n),
            "title": "Cumulative update",
        }
    )
    upd._guarded().write({"state": "missing"})  # whatever a live auto-approve policy did
    return upd


def test_f18_defer_and_fail_need_role_reason_and_sane_days(m5):
    upd = _patch(m5)
    with pytest.raises(UserError, match="role"):
        _as(upd, m5.plain).action_defer(days=2, reason="vendor recall pending")
    with pytest.raises(UserError, match="reason"):
        _as(upd, m5.eng).action_defer(days=2)
    limit = upd._msp_max_defer_days()
    for days in (-5, 0, limit + 1):
        with pytest.raises(UserError, match="1 to %d days" % limit):
            _as(upd, m5.eng).action_defer(days=days, reason="vendor recall pending")
    _as(upd, m5.eng).action_defer(days=1, reason="vendor recall pending")
    assert upd.state == "deferred"
    assert upd.deferred_until == fields.Date.context_today(upd) + timedelta(days=1)
    other = _patch(m5, "KB-FAIL")
    with pytest.raises(UserError, match="only an approved patch"):
        _as(other, m5.eng).action_fail(note="installer exit 1603")
    _as(other, m5.eng).action_approve()
    with pytest.raises(UserError, match="reason"):
        _as(other, m5.eng).action_fail(note="")
    _as(other, m5.eng).action_fail(note="installer exit 1603 on 3 hosts")
    assert other.state == "failed"


# ===================================================== M05-F19 rollback


def test_f19_no_change_is_implemented_without_a_rollback_plan(m5):
    ch = _change(m5, risk="low", rollback_plan="")
    ch._guarded().write({"state": "approved", "cab_approver_id": m5.cab.id})
    with pytest.raises(UserError, match="rollback plan"):
        _as(ch, m5.eng).action_implement(note="done")


# ===================================================== M05-F21 KPI


def test_f21_credits_mtd_is_this_periods_approved_money(m5):
    env = m5.env(user=m5.fin.id)
    label = fields.Date.context_today(m5.msp).strftime("%Y-%m")
    before = m05_ctrl.kpis(env)["sla_credits_mtd"]
    this = (
        m5.env["fix.msp.sla.credit"]
        ._guarded()
        .create({"msp_contract_id": m5.msp.id, "period_label": label})
    )
    old = (
        m5.env["fix.msp.sla.credit"]
        ._guarded()
        .create({"msp_contract_id": m5.msp.id, "period_label": "2001-01"})
    )
    m5.env.flush_all()
    # A02 ERP pass 2 (M05-S12): the tile counts the credits APPROVED this Dhaka
    # month (approved_at), not the credits whose period label is this month
    now = fields.Datetime.now()
    for credit, state, amount, when in (
        (this, "approved", 700.0, now),
        (old, "applied", 300.0, datetime(2001, 2, 10, 6, 0)),
    ):
        m5.env.cr.execute(
            "UPDATE fix_msp_sla_credit SET state = %s, approved_amount = %s, approved_at = %s "
            "WHERE id = %s",
            (state, amount, when, credit.id),
        )
    m5.env.invalidate_all()
    assert m05_ctrl.kpis(env)["sla_credits_mtd"] == round(before + 700.0, 2)
