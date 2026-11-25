# ruff: noqa: F811  (the imported m5 / call fixtures are used as parameters)
"""A02 pass-2 independent review (2026-11-21), M05 findings on efb02a54.

  B2   an MSP engineer resolving a paused alert got AccessError (the pause
       close was not a system write);
  B8   a crafted period (bounds tuple / list) made a month's report over any
       window, with no role check;
  D10  the MSP cover was all-or-nothing (parts made labour billed) and read
       the latest estimate in any state;
  SLA  a pause added wall-clock seconds to a business-hours deadline and the
       75 % escalation was wall-clock;
  P2   canonical period labels, the report walk from the SLA binding on the
       Dhaka day, a late renewal undoing the expiry's offboarding, and a
       downgrade reclassification needing a second engineer.

Each control runs as the NON-admin users of the m5 fixture (engineer, credit
approver, plain internal user); the superuser only stages data. ``odoo_env``
rolls back after each test.
"""

from datetime import datetime, timedelta
from unittest import mock

import pytest
import pytz
from odoo import fields
from odoo.addons.cd_msp_contract.models.msp_periods import BD_TZ, dhaka_month, dhaka_today
from odoo.addons.cd_msp_contract.tests.test_a02_p0_m05 import call  # noqa: F401
from odoo.addons.cd_msp_contract.tests.test_a02_p1p2_cd_msp_contract import (  # noqa: F401
    _as,
    m5,
)
from odoo.exceptions import AccessError, UserError, ValidationError

REASON = "Client signed amendment 11 on the 21st"


def _alert(m5, user=None, **vals):
    base = {
        "msp_contract_id": m5.msp.id,
        "asset_id": m5.asset.id,
        "severity": "major",
        "message": "disk failure predicted",
    }
    base.update(vals)
    return _as(m5.env["fix.msp.alert"], user or m5.eng).create(base)


def _last_month():
    return dhaka_month(dhaka_today().replace(day=1) - timedelta(days=1))


def _backdate(record, when):
    record.flush_recordset()
    record.env.cr.execute(
        "UPDATE %s SET create_date = %%s WHERE id = %%s" % record._table, [when, record.id]
    )
    record.invalidate_recordset()


def _utc(day, hour, minute=0):
    """Naive UTC of a Dhaka wall-clock time on ``day``."""
    local = BD_TZ.localize(datetime.combine(day, datetime.min.time()).replace(hour=hour))
    return (local + timedelta(minutes=minute)).astimezone(pytz.utc).replace(tzinfo=None)


# ===================================================================== B2


def test_b2_an_engineer_resolves_a_paused_alert(m5):
    alert = _alert(m5)
    _as(alert, m5.eng).action_pause(reason="client to power the server on")
    pause = alert.pause_ids
    assert pause and not pause.ended_at
    # the engineer holds no write on the pause (it is evidence)...
    with pytest.raises(AccessError):
        _as(pause, m5.eng).check_access("write")
    # ...yet resolving the alert closes it, as the system's write
    _as(alert, m5.eng).action_resolve(note="disk replaced and RAID rebuilt")
    assert alert.state == "resolved"
    assert pause.ended_at == alert.resolved_at and pause.ended_by_id == m5.eng
    assert not alert.paused


def test_b2_a_user_without_the_resolve_right_closes_no_pause(m5):
    alert = _alert(m5)
    _as(alert, m5.eng).action_pause(reason="client to power the server on")
    with pytest.raises(AccessError):
        _as(alert, m5.plain).action_resolve(note="closing it from the sidelines")
    assert not alert.pause_ids.ended_at and alert.state != "resolved"


# ===================================================================== B8


def test_b8_a_crafted_window_is_refused(m5):
    last = _last_month()
    window = (last[0] + timedelta(days=20), last[1], last[2])  # the last 10 days only
    for forged in (window, list(window), [str(window[0]), str(window[1]), window[2]]):
        with pytest.raises(UserError, match="YYYY-MM"):
            _as(m5.msp, m5.eng).action_monthly_report(forged)
        with pytest.raises(UserError, match="YYYY-MM"):
            _as(m5.msp, m5.eng).action_generate_monthly_report(period=forged)
    for typo in ("2026-1", "2026-13", "Oct 2026", 202610):
        with pytest.raises(UserError, match="YYYY-MM"):
            _as(m5.msp, m5.eng).action_monthly_report(typo)
    assert not m5.msp.report_ids
    # the month named canonically is the full Dhaka month
    report = _as(m5.msp, m5.eng).action_monthly_report(last[2])
    assert report.period_label == last[2]


def test_b8_the_workspace_kwargs_cannot_name_bounds(m5, call):
    last = _last_month()
    out = call(
        m5.env(user=m5.eng.id),
        "model_action",
        model="fix.msp.contract",
        ids=[m5.msp.id],
        method="action_generate_monthly_report",
        kwargs={"period": [str(last[1] - timedelta(hours=1)), str(last[1]), last[2]]},
    )
    assert not out.get("success") and "YYYY-MM" in out["error"]
    assert not m5.env["fix.msp.service.report"].search([("msp_contract_id", "=", m5.msp.id)])


def test_b8_a_report_is_made_by_an_m05_role_only(m5):
    with pytest.raises(UserError, match="MSP Engineer"):
        _as(m5.msp, m5.plain).action_generate_monthly_report()
    with pytest.raises(UserError, match="MSP Engineer"):
        _as(m5.msp, m5.plain).action_monthly_report(_last_month()[2])
    # the credit approver (the commercial role) may make it
    report = _as(m5.msp, m5.fin).action_monthly_report(_last_month()[2])
    assert report.msp_contract_id == m5.msp


# ==================================================================== D10


def _ticket(m5):
    alert = _alert(m5, message="server will not boot")
    _as(alert, m5.eng).action_to_ticket()
    return alert.order_id


def _estimate(m5, order, *lines, version=1):
    prices = {"part": 1200.0, "labour": 800.0, "diagnostic": 300.0, "transport": 200.0}
    return m5.env["fix.estimate"].create(
        {
            "order_id": order.id,
            "version": version,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "line_type": kind,
                        "description": "%s line" % kind,
                        "quantity": 1,
                        "unit_price": prices[kind],
                    },
                )
                for kind in lines
            ],
        }
    )


def test_d10_labour_is_never_billed_on_an_msp_overage_estimate(m5):
    order = _ticket(m5)
    mixed = _estimate(m5, order, "part", "labour")
    assert not order._fix_msp_covers()  # parts: an overage the client approves
    with pytest.raises(UserError, match="covers labour and remote support"):
        mixed.action_send()
    with pytest.raises(UserError, match="covers labour and remote support"):
        _estimate(m5, order, "transport", "diagnostic", version=2).action_send()
    # the overage estimate prices the parts / out-of-scope work only
    overage = _estimate(m5, order, "part", "transport", version=3)
    overage.action_send()
    assert overage.state == "sent" and overage.labour_total == 0.0
    assert order._fix_zero_charge_basis() == ""  # the client pays the parts


def test_d10_a_parts_entitlement_covers_the_whole_order(m5):
    order = _ticket(m5)
    _as(m5.msp, m5.fin).action_amend_terms(term="parts_included", value="1", reason=REASON)
    est = _estimate(m5, order, "part", "labour")
    est.action_send()  # nothing billed: the labour line is only the cost to serve
    assert order._fix_msp_covers()
    assert "managed asset under MSP" in order._fix_zero_charge_basis()


def test_d10_a_rejected_parts_version_does_not_bill_the_labour(m5):
    order = _ticket(m5)
    _estimate(m5, order, "labour").action_send()  # v1, labour: covered by the fee
    parts = _estimate(m5, order, "part", version=2)
    parts.action_send()
    assert not order._fix_msp_covers()
    parts.action_reject()  # the client declined the parts overage
    assert order._fix_msp_covers()
    assert "managed asset under MSP" in order._fix_zero_charge_basis()


def test_d10_a_newer_labour_draft_does_not_make_quoted_parts_free(m5):
    order = _ticket(m5)
    _estimate(m5, order, "part").action_send()  # the parts the client has
    _estimate(m5, order, "labour", version=2)  # a later draft, labour only
    assert not order._fix_msp_covers()
    assert order._fix_zero_charge_basis() == ""


# ===================================================== business-hours SLA


def _thursday(m5):
    """A finished Thursday 8-14 days back, inside the fixture's term."""
    day = dhaka_today() - timedelta(days=8)
    while day.weekday() != 3:
        day -= timedelta(days=1)
    return day


def _business_contract(m5, thursday):
    _as(m5.msp, m5.fin).action_amend_terms(
        reason=REASON,
        effective_date=str(thursday - timedelta(days=1)),
        coverage_window="business",
        alert_resolve_hours_major="4",
    )


def _business_alert(m5, thursday):
    alert = _alert(m5)
    _backdate(alert, _utc(thursday, 16))  # Thursday 16:00 Dhaka
    alert._msp_stamp_deadlines()
    sunday = thursday + timedelta(days=3)
    # 2 working hours on Thursday, 2 on Sunday morning
    assert alert.sla_deadline == _utc(sunday, 11)
    return alert, sunday


def test_sla_a_weekend_pause_extends_a_business_deadline_by_working_time(m5):
    thursday = _thursday(m5)
    _business_contract(m5, thursday)
    alert, sunday = _business_alert(m5, thursday)
    _as(alert, m5.eng).action_pause(reason="client to ship the failed disk")
    # waiting from Thursday 17:00 to Sunday 10:00: 65 h of wall clock but
    # only 2 working hours (Thursday 17-18, Sunday 09-10)
    alert.pause_ids.sudo()._guarded().write(
        {"started_at": _utc(thursday, 17), "ended_at": _utc(sunday, 10)}
    )
    monday = _utc(sunday + timedelta(days=1), 12)
    assert alert._msp_effective_deadline("resolve", monday) == _utc(sunday, 13)
    measure = alert.msp_contract_id._msp_period_sla(alert, as_of=_utc(sunday, 14))
    assert measure["breached"] == 1  # due Sunday 13:00, not on Wednesday


def test_sla_the_escalation_share_counts_working_time(m5):
    thursday = _thursday(m5)
    _business_contract(m5, thursday)
    alert, sunday = _business_alert(m5, thursday)
    Alert = m5.env["fix.msp.alert"]
    # Sunday 09:30: 2.5 of 4 working hours used (62.5 %); wall clock says 98 %
    with mock.patch.object(fields.Datetime, "now", return_value=_utc(sunday, 9, 30)):
        Alert.cron_threshold_escalations()
    assert not alert.escalated
    # Sunday 10:30: 3.5 of 4 working hours (87.5 %): escalated, not breached
    with mock.patch.object(fields.Datetime, "now", return_value=_utc(sunday, 10, 30)):
        Alert.cron_threshold_escalations()
    assert alert.escalated and not alert.breach_notified_at


# ===================================================================== P2


def test_p2_a_credit_period_is_spelt_one_way(m5):
    Credit = m5.env["fix.msp.sla.credit"]
    for label in ("2026-1", "2026-01 ", "Jan-2026"):
        with pytest.raises(ValidationError, match="YYYY-MM"):
            _as(Credit, m5.fin).create(
                {"msp_contract_id": m5.msp.id, "period_label": label, "manual_amount": 900.0}
            )
    ok = _as(Credit, m5.fin).create(
        {"msp_contract_id": m5.msp.id, "period_label": "2026-01", "manual_amount": 900.0}
    )
    assert ok.period_label == "2026-01"


def _onboarding(m5, target=None, kickoff=None):
    return _as(m5.env["fix.msp.onboarding"], m5.eng).create(
        {
            "msp_contract_id": m5.msp.id,
            "target_live_date": target,
            "kickoff_date": kickoff or fields.Date.today(),
        }
    )


def test_p2_months_between_the_binding_and_a_late_go_live_are_reported(m5):
    start = dhaka_today() - timedelta(days=100)
    m5.term.sudo()._guarded().write({"date_start": start})
    _onboarding(m5, target=start + timedelta(days=10), kickoff=start)
    live = datetime.combine(start + timedelta(days=70), datetime.min.time())
    m5.msp.sudo()._guarded().write({"service_live_at": live})
    labels = [m[2] for m in m5.msp._msp_report_months()]
    bound = dhaka_month(start + timedelta(days=10))[2]
    assert bound in labels and labels[0] == bound
    assert dhaka_month(live.date())[2] in labels


def test_p2_the_go_live_month_is_the_dhaka_day(m5):
    # live at 19:00 UTC on a month's last day = 01:00 Dhaka on the 1st
    month_end = (dhaka_today() - timedelta(days=90)).replace(day=1) + timedelta(days=32)
    month_end = month_end.replace(day=1) - timedelta(days=1)
    m5.term.sudo()._guarded().write({"date_start": month_end - timedelta(days=10)})
    _onboarding(m5)
    live = datetime.combine(month_end, datetime.min.time()).replace(hour=19)
    m5.msp.sudo()._guarded().write({"service_live_at": live})
    labels = [m[2] for m in m5.msp._msp_report_months()]
    assert month_end.strftime("%Y-%m") not in labels
    assert labels[0] == (month_end + timedelta(days=1)).strftime("%Y-%m")


def _renewal(m5):
    renewal = m5.contract(date_start=fields.Date.today(), renewed_from_id=m5.term.id)
    m5.term.sudo()._guarded().write({"state": "expired"})
    return renewal


def test_p2_a_late_renewal_undoes_the_expirys_offboarding(m5):
    Contract = m5.env["fix.msp.contract"]
    renewal = _renewal(m5)
    Contract.consume_contract_expired({"aggregate_id": m5.term.id})
    assert m5.msp.lifecycle == "offboarding" and m5.msp.offboarding_cause == "contract_end"
    out = Contract.consume_contract_renewed(
        {"aggregate_id": renewal.id, "payload": {"old_code": m5.term.code}}
    )
    assert out["repointed"] == 1 and out["restored"] == 1
    assert m5.msp.contract_id == renewal and m5.msp.lifecycle == "in_service"
    assert not m5.msp.offboarding_started_at
    _alert(m5)  # the renewed client is served again


def test_p2_a_renewal_leaves_a_progressed_or_chosen_offboarding(m5):
    Contract = m5.env["fix.msp.contract"]
    renewal = _renewal(m5)
    Contract.consume_contract_expired({"aggregate_id": m5.term.id})
    _as(m5.msp, m5.eng).action_record_access_revoked(evidence="portal users disabled, keys gone")
    out = Contract.consume_contract_renewed(
        {"aggregate_id": renewal.id, "payload": {"old_code": m5.term.code}}
    )
    assert out["restored"] == 0 and m5.msp.lifecycle == "offboarding"
    assert m5.msp.activity_ids.filtered(lambda a: "Renewed during" in (a.summary or ""))


def test_p2_a_person_started_offboarding_is_not_undone(m5):
    Contract = m5.env["fix.msp.contract"]
    _as(m5.msp, m5.eng).action_start_offboarding()
    assert m5.msp.offboarding_cause == "manual"
    renewal = _renewal(m5)
    out = Contract.consume_contract_renewed(
        {"aggregate_id": renewal.id, "payload": {"old_code": m5.term.code}}
    )
    assert out["restored"] == 0 and m5.msp.lifecycle == "offboarding"


def test_p2_a_downgrade_takes_a_second_engineer(m5):
    alert = _alert(m5)  # major: 4 h
    major_deadline = alert.sla_deadline
    _as(alert, m5.eng).action_reclassify(severity="minor", reason="a desktop, not the server")
    assert alert.severity == "major" and alert.sla_deadline == major_deadline
    assert alert.reclass_requested_by_id == m5.eng
    with pytest.raises(UserError, match="another MSP engineer"):
        _as(alert, m5.eng).action_reclassify(severity="minor", reason="a desktop, honestly")
    _as(alert, m5.eng2).action_reclassify(severity="minor", reason="confirmed: a desktop PC")
    assert alert.severity == "minor" and not alert.reclass_requested_by_id
    assert alert.sla_deadline == alert.create_date + timedelta(
        hours=m5.msp.alert_resolve_hours_minor or 24.0
    )
