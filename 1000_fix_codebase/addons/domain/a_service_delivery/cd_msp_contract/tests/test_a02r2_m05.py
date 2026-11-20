# ruff: noqa: F811  (the imported m5 fixture is used as a parameter)
"""A02 ERP pass-2 audit (2026-11-20), stream S4: M05-S01..S19.

Each control is exercised through the ORM as the NON-admin users holding the
real M05 roles (the m5 fixture's engineer, CAB, change manager and credit
approvers); the superuser only stages data. ``odoo_env`` rolls back after
each test.
"""

import json
from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_msp_contract.models.msp_periods import dhaka_month, dhaka_today
from odoo.addons.cd_msp_contract.tests.test_a02_p1p2_cd_msp_contract import (  # noqa: F401
    FIN,
    _as,
    _events,
    m5,
)
from odoo.exceptions import AccessError, UserError, ValidationError

REASON = "Client signed amendment 7 on the 20th"


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


def _month_back(n):
    day = dhaka_today().replace(day=1)
    for _i in range(n):
        day = (day - timedelta(days=1)).replace(day=1)
    return dhaka_month(day)


def _backdate(record, when):
    """Move a record's creation time (the ORM never writes create_date)."""
    record.flush_recordset()
    record.env.cr.execute(
        "UPDATE %s SET create_date = %%s WHERE id = %%s" % record._table, [when, record.id]
    )
    record.invalidate_recordset()


def _stage_report(m5, label, attainment=None, **vals):
    """A report row staged by the superuser (the guard trusts it)."""
    data = {"msp_contract_id": m5.msp.id, "period_label": label, "alert_count": 1}
    if attainment is not None:
        data["sla_attainment"] = attainment
    data.update(vals)
    return m5.env["fix.msp.service.report"].create(data)


# ================================================================ M05-S01


def test_s01_a_hand_typed_credit_is_a_manual_credit_with_its_amount(m5):
    Credit = m5.env["fix.msp.sla.credit"]
    with pytest.raises(UserError, match="manual credit: give its amount"):
        _as(Credit, m5.eng).create({"msp_contract_id": m5.msp.id, "period_label": "2026-03"})
    with pytest.raises(UserError, match="manual credit: give its amount"):
        _as(Credit, m5.fin).create(
            {"msp_contract_id": m5.msp.id, "period_label": "2026-03", "manual_amount": 0.0}
        )
    ok = _as(Credit, m5.fin).create(
        {"msp_contract_id": m5.msp.id, "period_label": "2026-03", "manual_amount": 1000.0}
    )
    assert ok.is_manual and ok.credit_amount == 1000.0


def test_s01_a_draft_credit_without_report_gets_the_months_report(m5):
    # a manual draft took the month's slot before the month was measured
    manual = _as(m5.env["fix.msp.sla.credit"], m5.fin).create(
        {"msp_contract_id": m5.msp.id, "period_label": "2026-02", "manual_amount": 500.0}
    )
    report = _stage_report(m5, "2026-02", 0.5)
    _as(m5.msp, m5.eng).action_compute_sla_credits()
    assert manual.service_report_id == report
    assert manual.computed_amount > 0.0  # the computed figure now stands beside it


def test_s01_an_engineer_cannot_make_an_empty_report(m5):
    Report = m5.env["fix.msp.service.report"]
    with pytest.raises(UserError, match="not created by hand"):
        _as(Report, m5.eng).create({"msp_contract_id": m5.msp.id, "period_label": "2026-01"})
    # and the engineer's create right on reports is gone (ACL)
    acl = m5.env.ref("cd_msp_contract.access_fix_msp_service_report_eng")
    assert not acl.perm_create


def test_s01_a_report_with_no_attainment_is_recomputed_not_refused(m5):
    period = _last_month()
    empty = _stage_report(m5, period[2])  # no figure: blocks the credit
    report = _as(m5.msp, m5.eng).action_monthly_report(period)
    assert report == empty
    assert report.sla_attainment == 1.0 and not report.attainment_flagged
    # a report WITH its figure stays the month's report
    with pytest.raises(UserError, match="already exists"):
        _as(m5.msp, m5.eng).action_monthly_report(period)


# ================================================================ M05-S02


def test_s02_an_alerts_sla_inputs_are_fixed_and_its_deadline_stamped(m5):
    alert = _alert(m5, severity="minor")
    stamped = alert.sla_deadline
    assert stamped == alert.create_date + timedelta(hours=m5.msp.alert_resolve_hours_minor)
    for vals in ({"severity": "major"}, {"source": "phone"}, {"msp_contract_id": False}):
        with pytest.raises(UserError, match="cannot change once the alert is raised"):
            _as(alert, m5.eng).write(vals)
    # a later amendment of the target does not move a raised alert's deadline
    _as(m5.msp, m5.fin).action_amend_terms(
        term="alert_resolve_hours_minor", value="2", reason=REASON
    )
    alert.invalidate_recordset()
    assert alert.sla_deadline == stamped
    measured = m5.msp._msp_period_sla(alert, as_of=alert.create_date + timedelta(hours=3))
    assert measured["pending"] == 1  # still inside the 24 h it was raised with


def test_s02_reclassify_only_a_new_alert_with_its_reason(m5):
    alert = _alert(m5, severity="minor")
    with pytest.raises(UserError, match="reason"):
        _as(alert, m5.eng).action_reclassify(severity="major", reason="x")
    with pytest.raises(UserError, match="MSP Engineer"):
        _as(alert, m5.plain).action_reclassify(severity="major", reason=REASON)
    _as(alert, m5.eng).action_reclassify(severity="major", reason="Client server, not a PC")
    assert alert.severity == "major"
    assert alert.sla_deadline == alert.create_date + timedelta(
        hours=m5.msp.alert_resolve_hours_major
    )
    _as(alert, m5.eng).action_acknowledge()
    with pytest.raises(UserError, match="only a new alert"):
        _as(alert, m5.eng).action_reclassify(severity="minor", reason=REASON)


# ================================================================ M05-S07


def _offboard(m5):
    msp = m5.msp
    _as(msp, m5.eng).action_start_offboarding()
    _as(m5.asset, m5.eng).action_record_agent_removal(evidence="agent uninstalled, ticket 42")
    _as(msp, m5.eng).action_record_access_revoked(evidence="portal users disabled, keys rotated")
    _as(msp, m5.eng).action_record_data_returned(evidence="backups handed over on USB, signed")
    _as(msp, m5.eng).action_complete_offboarding()
    return msp


def test_s07_an_offboarded_contract_raises_nothing_and_is_announced(m5):
    msp = _offboard(m5)
    assert msp.lifecycle == "offboarded"
    with pytest.raises(UserError, match="offboarded"):
        _alert(m5)
    assert _events(m5.env, "msp.client_offboarded", msp.id)


def test_s07_no_coverage_gap_for_a_removed_agent_or_a_contract_leaving(m5):
    Asset = m5.env["fix.monitored.asset"]
    old = fields.Datetime.now() - timedelta(days=3)
    m5.asset.sudo().write({"last_seen": old})
    _as(m5.msp, m5.eng).action_start_offboarding()
    Asset.cron_coverage_gaps()
    assert not m5.env["fix.msp.alert"].search([("asset_id", "=", m5.asset.id)])


def test_s07_a_terminated_or_expired_contract_starts_the_offboarding(m5):
    Contract = m5.env["fix.msp.contract"]
    with pytest.raises(AccessError):
        _as(Contract, m5.eng).consume_contract_expired({"aggregate_id": m5.term.id})
    m5.term.sudo()._guarded().write({"state": "expired"})
    out = Contract.consume_contract_expired({"aggregate_id": m5.term.id})
    assert out["offboarding"] == 1 and m5.msp.lifecycle == "offboarding"
    again = Contract.consume_contract_expired({"aggregate_id": m5.term.id})
    assert again["offboarding"] == 0
    wired = m5.env["fix.event.consumer"].search(
        [
            ("model", "=", "fix.msp.contract"),
            ("event_type", "in", ("contract.expired", "contract.terminated")),
        ]
    )
    assert len(wired) == 2


def test_s07_no_report_for_a_month_after_the_offboarding(m5):
    msp = _offboard(m5)
    msp.sudo()._guarded().write({"offboarded_at": fields.Datetime.now() - timedelta(days=70)})
    with pytest.raises(UserError, match="not a service month"):
        _as(msp, m5.eng).action_monthly_report(_last_month())


# ================================================================ M05-S08


def _onboarding(m5, target=None):
    return _as(m5.env["fix.msp.onboarding"], m5.eng).create(
        {"msp_contract_id": m5.msp.id, "target_live_date": target}
    )


def test_s08_the_sla_binds_thirty_days_after_the_start_at_the_latest(m5):
    # the fixture's term started 30 days ago: an onboarding that never went
    # live no longer suspends the SLA
    m5.term.sudo()._guarded().write({"date_start": fields.Date.today() - timedelta(days=45)})
    _onboarding(m5)
    alert = _alert(m5)
    binds = m5.msp._msp_sla_binds_at()
    assert binds and binds <= fields.Datetime.now()
    late = alert.create_date + timedelta(hours=10)
    assert m5.msp._msp_period_sla(alert, as_of=late)["breached"] == 1


def test_s08_a_month_before_binding_is_not_yet_binding(m5):
    m5.term.sudo()._guarded().write({"date_start": fields.Date.today() - timedelta(days=2)})
    _onboarding(m5, target=fields.Date.today() + timedelta(days=20))
    report = _as(m5.msp, m5.eng).action_monthly_report(_last_month())
    assert report.sla_not_binding and "not yet binding" in report.summary_en
    report.flush_recordset()
    m5.env.cr.execute(
        "SELECT sla_attainment FROM fix_msp_service_report WHERE id = %s", [report.id]
    )
    assert m5.env.cr.fetchone()[0] is None  # never a free 100 %
    _as(m5.msp, m5.eng).action_compute_sla_credits()
    assert not report.attainment_flagged
    assert not m5.env["fix.msp.sla.credit"].search([("service_report_id", "=", report.id)])


def test_s08_an_onboarding_past_its_binding_date_is_escalated_once(m5):
    m5.term.sudo()._guarded().write({"date_start": fields.Date.today() - timedelta(days=40)})
    project = _onboarding(m5)
    Contract = m5.env["fix.msp.contract"]
    assert Contract.cron_onboarding_overdue() >= 1
    stamp = project.overdue_escalated_at
    assert stamp and _events(m5.env, "msp.onboarding_overdue", project.id)
    Contract.cron_onboarding_overdue()
    assert project.overdue_escalated_at == stamp
    assert len(_events(m5.env, "msp.onboarding_overdue", project.id)) == 1


# ================================================================ M05-S10


def _patch_missing(m5, severity="high"):
    return _as(m5.env["fix.msp.patch.update"], m5.eng).create(
        {
            "msp_contract_id": m5.msp.id,
            "asset_id": m5.asset.id,
            "identifier": "KB-S10-%s" % severity,
            "title": "Patch",
            "severity": severity,
        }
    )


def _contact(m5, approve=True):
    partner = m5.env["res.partner"].create(
        {"name": "Client IT head", "parent_id": m5.customer.id, "phone": "01711000222"}
    )
    return m5.env["fix.msp.client.contact"].create(
        {
            "msp_contract_id": m5.msp.id,
            "partner_id": partner.id,
            "role": "it_manager",
            "can_approve_changes": approve,
        }
    )


def test_s10_an_out_of_window_install_needs_the_clients_approval(m5):
    upd = _patch_missing(m5)
    with pytest.raises(UserError, match="Segregation of duties"):
        _as(upd, m5.eng).action_approve()  # he logged it
    _as(upd, m5.eng2).action_approve()
    with pytest.raises(UserError, match="client's approval"):
        _as(upd, m5.eng).action_install()
    viewer = _contact(m5, approve=False)
    with pytest.raises(UserError, match="may approve changes"):
        _as(upd, m5.eng).action_record_client_approval(
            contact_id=viewer.id, evidence="OTP 4711 verified"
        )
    approver = _contact(m5)
    _as(upd, m5.eng).action_record_client_approval(
        contact_id=approver.id, evidence="OTP ref fix.otp.log 4711"
    )
    _as(upd, m5.eng).action_install()
    assert upd.state == "installed" and upd.client_approval_contact_id == approver


def test_s10_what_a_patch_is_is_fixed_once_it_leaves_missing(m5):
    upd = _patch_missing(m5, severity="critical")
    with pytest.raises(UserError, match="role"):
        _as(upd, m5.eng).write({"severity": "low"})
    _as(upd, m5.cm).write({"severity": "high"})  # a change manager may
    _as(upd, m5.eng2).action_approve()
    with pytest.raises(UserError, match="cannot change"):
        _as(upd, m5.cm).write({"severity": "critical"})
    with pytest.raises(UserError, match="cannot change"):
        _as(upd, m5.eng).write({"category": "firmware"})


# ================================================================ M05-S11


def test_s11_alerts_reports_and_credits_follow_the_contracts_company(m5):
    other = m5.env["res.company"].create({"name": "A02R2 Other Co %d" % m5.n})
    alert = (
        m5.env["fix.msp.alert"]
        .with_company(other)
        .create(
            {
                "msp_contract_id": m5.msp.id,
                "asset_id": m5.asset.id,
                "message": "raised by a cron in another company",
            }
        )
    )
    assert alert.company_id == m5.msp.company_id
    assert alert.operating_unit_id == m5.msp.operating_unit_id
    with pytest.raises(ValidationError, match="contract's company"):
        m5.env["fix.msp.sla.credit"].create(
            {
                "msp_contract_id": m5.msp.id,
                "period_label": "2026-01",
                "manual_amount": 10.0,
                "company_id": other.id,
            }
        )
    report = _as(m5.msp, m5.eng).action_monthly_report(_last_month())
    assert report.company_id == m5.msp.company_id
    assert report.operating_unit_id == m5.msp.operating_unit_id


# ================================================================ M05-S12


def test_s12_credits_kpi_counts_credits_approved_this_month(m5):
    from odoo.addons.cd_p03_portal.controllers.a02.m05 import kpis

    before = kpis(m5.env)["sla_credits_mtd"]
    credit = _as(m5.env["fix.msp.sla.credit"], m5.fin).create(
        {"msp_contract_id": m5.msp.id, "period_label": _last_month()[2], "manual_amount": 700.0}
    )
    credit.sudo()._guarded().write(
        {"state": "approved", "approved_at": fields.Datetime.now(), "approved_amount": 700.0}
    )
    out = kpis(m5.env)
    assert round(out["sla_credits_mtd"] - before, 2) == 700.0
    assert out["sla_credits_last_month"] >= 700.0


# ================================================================ M05-S13


def test_s13_amendments_have_an_effective_date_and_a_history(m5):
    msp = m5.msp
    today = dhaka_today()
    with pytest.raises(UserError, match="future"):
        _as(msp, m5.fin).action_amend_terms(
            term="sla_target_pct",
            value="90",
            reason=REASON,
            effective_date=str(today + timedelta(days=3)),
        )
    _stage_report(m5, _last_month()[2], 1.0)
    with pytest.raises(UserError, match="already has its"):
        _as(msp, m5.fin).action_amend_terms(
            term="sla_target_pct",
            value="90",
            reason=REASON,
            effective_date=str(today.replace(day=1) - timedelta(days=3)),
        )
    _as(msp, m5.fin).action_amend_terms(term="sla_target_pct", value="90", reason=REASON)
    rows = msp.terms_amendment_ids.sorted("id")
    assert rows.mapped("kind") == ["baseline", "amendment"]
    assert rows[0].sla_target_pct == 95.0 and rows[1].sla_target_pct == 90.0
    # the month measured before the amendment keeps the target then in force
    assert msp._msp_terms_at(today - timedelta(days=20)).sla_target_pct == 95.0
    assert msp._msp_terms_at(today).sla_target_pct == 90.0
    assert msp._msp_period_terms(_last_month()[2]).sla_target_pct == 95.0
    with pytest.raises(UserError):
        _as(m5.env["fix.msp.terms.amendment"], m5.fin).create(
            {"msp_contract_id": msp.id, "company_id": msp.company_id.id, "effective_date": today}
        )


# ================================================================ M05-S14


def test_s14_the_cron_reports_every_unreported_month_since_the_start(m5):
    m5.term.sudo()._guarded().write({"date_start": _month_back(3)[0].date() + timedelta(days=1)})
    m5.env["fix.msp.contract"].cron_monthly_service_reports()
    labels = set(m5.msp.report_ids.mapped("period_label"))
    assert {_month_back(1)[2], _month_back(2)[2], _month_back(3)[2]} <= labels


def test_s14_the_button_takes_the_month(m5):
    label = _month_back(2)[2]
    action = _as(m5.msp, m5.eng).action_generate_monthly_report(period=label)
    report = m5.env["fix.msp.service.report"].browse(action["res_id"])
    assert report.period_label == label
    with pytest.raises(UserError, match="not finished"):
        _as(m5.msp, m5.eng).action_generate_monthly_report(period=dhaka_today().strftime("%Y-%m"))


def test_s14_an_unreportable_month_opens_an_activity_on_the_tenth(m5):
    last = _last_month()
    # an alert of last month whose clock is paused (waiting on the client):
    # still inside its target, so the month cannot be judged yet
    alert = _alert(m5)
    _backdate(alert, last[1] - timedelta(hours=1))
    alert._msp_stamp_deadlines()
    _as(alert, m5.eng).action_pause(reason="client to ship the failed disk")
    alert.pause_ids.sudo()._guarded().write({"started_at": last[1] - timedelta(minutes=30)})
    tenth = dhaka_today().replace(day=10)
    target = "odoo.addons.cd_msp_contract.models.fix_msp_lifecycle.dhaka_today"
    with mock.patch(target, return_value=tenth):
        m5.env["fix.msp.contract"].cron_monthly_service_reports()
        m5.env["fix.msp.contract"].cron_monthly_service_reports()
    acts = m5.env["mail.activity"].search(
        [("res_model", "=", "fix.msp.contract"), ("res_id", "=", m5.msp.id)]
    )
    assert len(acts.filtered(lambda a: last[2] in (a.summary or ""))) == 1


# ================================================================ M05-S15


def test_s15_the_client_report_prints_bilingually(m5):
    report = _as(m5.msp, m5.eng).action_monthly_report(_last_month())
    action = _as(report, m5.eng).action_print_service_report()
    assert action["print_url"].endswith("/%s" % report.id)
    values = (
        m5.env["report.cd_msp_contract.report_msp_service_report"]
        .with_user(m5.eng)
        ._get_report_values(report.ids)
    )
    payload = values["payloads"][report.id]
    titles = [b["title"] for b in payload["blocks"]]
    assert any("SLA Credit" in t for t in titles) and any("এস্টেট" in t for t in titles)
    assert payload["tables"][0]["title"].startswith("SLA Breaches")
    assert m5.env["fix.event.consumer"].search(
        [("event_type", "=", "msp.service_report_published"), ("model", "=", report._name)]
    )


def test_s15_the_report_is_sent_to_the_reporting_contacts(m5):
    if "fix.notif.delivery" not in m5.env:
        pytest.skip("M27 not installed")
    contact = _contact(m5)
    contact.partner_id.write({"email": "it.head@client.test"})
    report = _as(m5.msp, m5.eng).action_monthly_report(_last_month())
    out = m5.env["fix.msp.service.report"].consume_service_report_published(
        {"aggregate_id": report.id, "event_id": "evt-s15"}
    )
    assert out["queued"] == 1
    with pytest.raises(AccessError):
        _as(m5.env["fix.msp.service.report"], m5.eng).consume_service_report_published(
            {"aggregate_id": report.id}
        )


# ================================================================ M05-S16


def test_s16_a_ticket_escalates_to_a_field_order_with_its_context(m5):
    if "fix.field.order" not in m5.env:
        pytest.skip("M02 not installed")
    zone = m5.env["fix.zone"].create({"name": "A02R2 zone %d" % m5.n, "code": "Z%d" % m5.n})
    m5.branch.sudo().write({"zone_id": zone.id})
    alert = _alert(m5)
    with pytest.raises(UserError, match="only a ticketed alert"):
        _as(alert, m5.eng).action_escalate_to_field(note="needs a disk swap on site")
    _as(alert, m5.eng).action_to_ticket()
    with pytest.raises(UserError, match="why a visit"):
        _as(alert, m5.eng).action_escalate_to_field(note="")
    out = _as(alert, m5.eng).action_escalate_to_field(note="needs a disk swap on site")
    fo = m5.env["fix.field.order"].browse(out["field_order_ids"])
    assert fo.order_id == alert.order_id and "disk failure predicted" in fo.notes
    assert alert.field_order_ref
    assert _events(m5.env, "msp.ticket_escalated_to_field", alert.id)
    with pytest.raises(UserError, match="already went"):
        _as(alert, m5.eng).action_escalate_to_field(note="needs a disk swap on site")


# ================================================================ M05-S17


def _session_of(m5, minutes, ended=None):
    ended = ended or fields.Datetime.now()
    session = m5.env["fix.remote.session"].create(
        {"msp_contract_id": m5.msp.id, "asset_id": m5.asset.id, "technician_id": m5.tech.id}
    )
    session.sudo()._guarded().write(
        {
            "started": True,
            "started_at": ended - timedelta(minutes=minutes),
            "consent_captured": True,
            "consent_token_ref": "OTP-test",
        }
    )
    _as(session, m5.eng).action_end(recording_url="mesh://rec/%s" % session.id)
    session.sudo()._guarded().write({"ended_at": ended, "duration_minutes": float(minutes)})
    return session


def test_s17_session_time_is_metered_and_the_client_told_at_80_percent(m5):
    _as(m5.msp, m5.fin).action_amend_terms(
        remote_hours_monthly="10", overage_hourly_rate="1500", reason=REASON
    )
    session = _session_of(m5, 30)
    assert session.duration_minutes == 30.0
    _session_of(m5, 8 * 60)  # 8.5 h of 10 h
    m5.msp._msp_meter_hours(fields.Datetime.now())
    label = dhaka_today().strftime("%Y-%m")
    assert m5.msp.remote_notice_period == label
    assert _events(m5.env, "msp.remote_hours_threshold", m5.msp.id)
    _session_of(m5, 3 * 60)
    m5.msp._msp_meter_hours(fields.Datetime.now())
    assert m5.msp.remote_exceeded_period == label
    assert len(_events(m5.env, "msp.remote_hours_threshold", m5.msp.id)) == 1


def _entitle_from_last_month(m5, **terms):
    last = _last_month()
    m5.term.sudo()._guarded().write({"date_start": last[0].date() - timedelta(days=40)})
    first = (dhaka_today().replace(day=1) - timedelta(days=1)).replace(day=1)
    _as(m5.msp, m5.fin).action_amend_terms(reason=REASON, effective_date=str(first), **terms)
    return last


def test_s17_hours_above_the_entitlement_are_billed_or_flagged(m5):
    last = _entitle_from_last_month(m5, remote_hours_monthly="1", overage_hourly_rate="2000")
    _session_of(m5, 180, ended=last[1] - timedelta(days=2))
    report = _as(m5.msp, m5.eng).action_monthly_report(last)
    assert report.overage_hours == 2.0 and report.overage_amount == 4000.0
    events = _events(m5.env, "msp.remote_hours_overage", report.id)
    assert events and json.loads(events.payload)["amount"] == 4000.0


def test_s17_no_overage_rate_flags_the_hours(m5):
    last = _entitle_from_last_month(m5, remote_hours_monthly="1")
    _session_of(m5, 120, ended=last[1] - timedelta(days=2))
    report = _as(m5.msp, m5.eng).action_monthly_report(last)
    assert report.overage_flagged and report.overage_amount == 0.0
    assert not _events(m5.env, "msp.remote_hours_overage", report.id)


# ================================================================ M05-S18


def test_s18_waiting_on_the_client_pauses_the_clock(m5):
    alert = _alert(m5)  # major: 4 h
    with pytest.raises(UserError, match="client must do"):
        _as(alert, m5.eng).action_pause(reason="wait")
    _as(alert, m5.eng).action_pause(reason="client to power the server on")
    pause = alert.pause_ids
    pause.sudo()._guarded().write(
        {
            "started_at": alert.create_date + timedelta(hours=1),
            "ended_at": alert.create_date + timedelta(hours=4),
        }
    )
    at = alert.create_date + timedelta(hours=5)
    assert m5.msp._msp_period_sla(alert, as_of=at)["pending"] == 1  # 4 h + 3 h paused
    assert m5.msp._msp_period_sla(alert, as_of=at + timedelta(hours=3))["breached"] == 1


def test_s18_response_target_acked_at_and_mtta(m5):
    _as(m5.msp, m5.fin).action_amend_terms(response_hours_major="1", reason=REASON)
    alert = _alert(m5)
    assert alert.response_deadline == alert.create_date + timedelta(hours=1)
    _as(alert, m5.eng).action_acknowledge()
    assert alert.acked_at and alert.responded_at == alert.acked_at
    late = _alert(m5, message="no answer")
    measure = m5.msp._msp_period_sla(late, as_of=late.create_date + timedelta(hours=2))
    assert measure["breached"] == 1 and measure["response_breached"] == 1
    assert "mtta_minutes" in m5.msp._msp_period_sla(alert)


def test_s18_threshold_escalation_and_breach_notice(m5):
    alert = _alert(m5)
    _backdate(alert, fields.Datetime.now() - timedelta(hours=5))
    alert._msp_stamp_deadlines()
    assert m5.env["fix.msp.alert"].cron_threshold_escalations() >= 1
    assert alert.escalated and alert.breach_notified_at
    assert _events(m5.env, "msp.alert_sla_breached", alert.id)


def test_s18_mtta_mttr_reach_the_report_and_the_credit(m5):
    report = _as(m5.msp, m5.eng).action_monthly_report(_last_month())
    for name in ("mtta_minutes", "mttr_minutes", "response_breached_count"):
        assert name in report._fields
        assert name in m5.env["fix.msp.sla.credit"]._fields


# ================================================================ M05-S19


def test_s19_the_credential_guard_covers_evidence_notes_and_the_chatter(m5):
    _as(m5.msp, m5.eng).action_start_offboarding()
    with pytest.raises(ValidationError, match="credential"):
        _as(m5.msp, m5.eng).action_record_access_revoked(evidence="admin password: Hunter22!")
    upd = _patch_missing(m5)
    _as(upd, m5.eng2).action_approve()
    with pytest.raises(ValidationError, match="credential"):
        _as(upd, m5.eng).action_fail(note="failed, root pwd = toor123 still set")
    with pytest.raises(ValidationError, match="credential"):
        _as(m5.msp, m5.eng).message_post(body="<p>the VPN token: abc123def</p>")
    with pytest.raises(ValidationError, match="credential"):
        _as(_alert(m5), m5.eng).message_post(body="pin=4321")
    _as(m5.msp, m5.eng).message_post(body="Vault entry KV-77 holds the VPN credentials.")
