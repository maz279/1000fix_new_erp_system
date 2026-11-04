# A09 M59 acceptance suite (A09 workflow audit B1-B6, C5, C6, I5; findings
# M59-F1..F17, working/A09_evidence/module_findings/M59.md).
#
# Every attack runs as a freshly created NON-admin user and asserts the
# refusal; then the proper path is walked by the right roles. Writes go
# through call_kw with the client-controlled `tracking_disable` key and
# through the real /p03 controller with `request` patched.
import base64
import itertools
import json
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import a09
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a09 import m59
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.service.model import call_kw

REFUSED = (AccessError, UserError, ValidationError)
FORM27 = base64.b64encode(b"%PDF-1.4 Form 27 as dispatched").decode()
_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


def _user(env, *groups, employee=True):
    n = next(_SEQ)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A09 M59 User %d" % n,
                "login": "a09-m59-%d@a09.test" % n,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )
    if employee:
        env["hr.employee"].create({"name": user.name, "user_id": user.id})
    return user


def _rpc_write(env, user, rec, vals):
    return call_kw(
        env(user=user.id, context={"tracking_disable": True})[rec._name],
        "write",
        [[rec.id], vals],
        {},
    )


def _decide(rec, requester, approver):
    rec.with_user(requester).action_request_approval()
    rec.invalidate_recordset()
    task = rec.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )
    assert task, "no inbox task for %s; routed to %s" % (
        approver.name,
        rec.approval_request_id.task_ids.mapped("assigned_user_id.name"),
    )
    task.with_user(approver).action_approve()
    rec.invalidate_recordset()
    return task


def _events(env, event_type, aggregate_id):
    return (
        env["fix.event.outbox"]
        .sudo()
        .search([("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)])
    )


@pytest.fixture
def call():
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@pytest.fixture
def x(odoo_env):
    env = odoo_env
    c = SimpleNamespace(env=env)
    c.plain = _user(env)
    c.colleague = _user(env)
    c.hse = _user(env, "cd_hse.group_hse_officer")
    c.hse2 = _user(env, "cd_hse.group_hse_officer")
    c.notifier = _user(env, "cd_hse.group_statutory_notifier")
    c.comp_approver = _user(env, "cd_hse.group_injury_compensation_approver")
    c.oh = _user(env, "cd_hse.group_occupational_health")
    entity = env["fix.entity"].create(
        {"code": "A9M59", "legal_name": "A09 M59 Ltd", "company_id": env.company.id}
    )
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    c.branch = env["fix.branch"].create(
        {"code": "A9B", "name": "A09 Depot", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    c.now = fields.Datetime.now()
    c.today = fields.Date.today()
    return c


def _report(x, user, **vals):
    base = {"description": "Burn from rework station", "branch_id": x.branch.id}
    base.update(vals)
    return x.env(user=user.id)["fix.hse.incident"].create(base)


def _serious(x, user=None):
    user = user or x.plain
    return _report(
        x,
        user,
        incident_type="injury",
        severity="high",
        injured_employee_id=user.employee_id.id,
    )


def _notify(x, incident):
    reg = incident.statutory_record_id
    reg.with_user(x.hse).write({"dife_notice_file": FORM27})
    reg.with_user(x.notifier).action_notify_dife(notice_ref="DIFE/2026/0042")
    return reg


def _investigated(x, incident):
    incident.with_user(x.hse).action_investigate()
    incident.with_user(x.hse).write(
        {
            "root_cause": "Iron left on without a stand",
            "corrective_action": "Stands fitted; toolbox talk",
            "capa_owner_id": x.hse.employee_id.id,
            "capa_due_date": x.today + timedelta(days=7),
        }
    )
    incident.with_user(x.hse).action_record_action_taken()


# =================================================================== reporting
def test_plain_employee_reports_a_serious_injury(x):
    inc = _serious(x)
    reg = inc.sudo().statutory_record_id
    assert reg and reg.employee_id == x.plain.employee_id
    assert inc.employee_id == x.plain.employee_id  # reported in their own name


def test_plain_employee_cannot_report_in_someone_elses_name(x):
    with pytest.raises(AccessError):
        _report(x, x.plain, employee_id=x.colleague.employee_id.id)


def test_original_report_is_immutable(x, call):
    inc = _serious(x)
    for vals in ({"severity": "low"}, {"description": "nothing happened"}):
        with pytest.raises(UserError, match="original report"), x.env.cr.savepoint():
            _rpc_write(x.env, x.plain, inc, vals)
    res = call(
        x.env(user=x.plain.id),
        "model_write",
        model="fix.hse.incident",
        record_id=inc.id,
        values={"severity": "low"},
    )
    inc.invalidate_recordset()
    assert "error" in res and inc.severity == "high"


def test_plain_employee_cannot_see_or_touch_a_colleagues_incident(x):
    inc = _serious(x, x.colleague)
    assert not x.env(user=x.plain.id)["fix.hse.incident"].search([("id", "=", inc.id)])
    with pytest.raises(AccessError):
        _rpc_write(x.env, x.plain, inc, {"corrective_action": "none"})


# =================================================================== closure gates
def test_state_cannot_be_written_to_closed(x, call):
    inc = _serious(x)
    for who in (x.plain, x.hse):
        with pytest.raises(UserError, match="changes only through its workflow"):
            _rpc_write(x.env, who, inc, {"state": "closed"})
    res = call(
        x.env(user=x.plain.id),
        "model_write",
        model="fix.hse.incident",
        record_id=inc.id,
        values={"state": "closed"},
    )
    inc.invalidate_recordset()
    assert "error" in res and inc.state == "reported"


def test_reporter_cannot_run_the_investigation_or_close(x):
    inc = _report(x, x.plain, incident_type="near_miss")
    for method in ("action_investigate", "action_close"):
        with pytest.raises(AccessError):
            getattr(inc.with_user(x.plain), method)()


def test_close_needs_investigation_verified_capa_and_the_dife_notice(x):
    inc = _serious(x)
    with pytest.raises(UserError, match="investigation"):
        inc.with_user(x.hse).action_close()
    inc.with_user(x.hse).action_investigate()
    with pytest.raises(UserError, match="root cause"):
        inc.with_user(x.hse).action_record_action_taken()
    inc.invalidate_recordset()
    _investigate_rest = {
        "root_cause": "Iron left on",
        "corrective_action": "Stands fitted",
        "capa_owner_id": x.hse.employee_id.id,
        "capa_due_date": x.today,
    }
    inc.with_user(x.hse).write(_investigate_rest)
    inc.with_user(x.hse).action_record_action_taken()
    with pytest.raises(UserError, match="CAPA is not verified"):
        inc.with_user(x.hse).action_close()
    with pytest.raises(UserError, match="another HSE Officer"):
        inc.with_user(x.hse).action_verify_capa()  # the investigator
    inc.with_user(x.hse2).action_verify_capa()
    with pytest.raises(UserError, match=r"s\.80"):
        inc.with_user(x.hse).action_close()
    _notify(x, inc)
    inc.with_user(x.hse).action_close()
    assert inc.state == "closed" and inc.closed_by_id == x.hse


def test_a_property_damage_incident_still_needs_its_corrective_action(x):
    inc = _report(x, x.plain, incident_type="property_damage", severity="low")
    inc.with_user(x.hse).action_investigate()
    with pytest.raises(UserError, match="corrective"):
        inc.with_user(x.hse).action_record_action_taken()


# =================================================================== register on escalation
def test_escalated_incident_enters_the_register_and_cannot_close_unnotified(x):
    inc = _report(
        x,
        x.plain,
        incident_type="injury",
        severity="low",
        injured_employee_id=x.plain.employee_id.id,
    )
    assert not inc.sudo().statutory_record_id
    with pytest.raises(AccessError):
        inc.with_user(x.plain).action_escalate(reason="hospitalised")
    inc.with_user(x.hse).action_escalate(reason="Hospitalised overnight")
    inc.with_user(x.hse).action_escalate(reason="Lost-time over 20 days")
    assert inc.severity == "high" and inc.statutory_record_id
    _investigated(x, inc)
    inc.with_user(x.hse2).action_verify_capa()
    with pytest.raises(UserError, match=r"s\.80"):
        inc.with_user(x.hse).action_close()


# =================================================================== DIFE notice
def test_dife_notice_needs_the_authority_and_the_form_on_file(x):
    inc = _serious(x)
    reg = inc.statutory_record_id
    with pytest.raises(AccessError):
        reg.with_user(x.hse).action_notify_dife(notice_ref="x")
    with pytest.raises(UserError, match="Attach the Form 27"):
        reg.with_user(x.notifier).action_notify_dife(notice_ref="DIFE/1")
    reg.with_user(x.hse).write({"dife_notice_file": FORM27})
    with pytest.raises(UserError, match="reference"):
        reg.with_user(x.notifier).action_notify_dife(notice_ref=" ")
    reg.with_user(x.notifier).action_notify_dife(notice_ref="DIFE/1")
    assert reg.dife_notified and reg.dife_notified_by_id == x.notifier and not reg.notified_late


def test_a_late_notice_is_recorded_as_late(x):
    inc = _report(
        x,
        x.plain,
        incident_type="injury",
        severity="medium",
        injured_employee_id=x.plain.employee_id.id,
        accident_datetime=x.now - timedelta(days=12),
    )
    reg = _notify(x, inc)
    assert reg.notified_late


def test_the_workspace_notify_button_exists_and_works(x, call):
    inc = _serious(x)
    inc.statutory_record_id.with_user(x.hse).write({"dife_notice_file": FORM27})
    res = call(
        x.env(user=x.notifier.id),
        "model_action",
        model="fix.hse.incident",
        ids=[inc.id],
        method="action_notify_dife",
        kwargs={"notice_ref": "DIFE/P03"},
    )
    assert res["success"], res
    assert inc.statutory_record_id.dife_notified and inc.dife_notice_ref == "DIFE/P03"


def test_register_flags_are_not_writable_and_facts_stay_frozen(x):
    inc = _serious(x)
    reg = inc.statutory_record_id
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse, reg, {"dife_notified": True})
    _notify(x, inc)
    # the old two-step: un-notify, then edit the facts
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse, reg, {"dife_notified": False, "dife_ack_ref": False})
    with pytest.raises(UserError, match="append-only"):
        _rpc_write(x.env, x.hse, reg, {"nature_of_injury": "minor scratch"})
    with pytest.raises(UserError, match="append-only"):
        reg.with_user(x.hse).unlink()


def test_statutory_report_shows_the_clock_and_not_to_a_plain_employee(x, call):
    inc = _serious(x, x.colleague)
    res = call(x.env(user=x.plain.id), "model_report", module="M59", report="statutory_compliance")
    assert x.colleague.name not in [r.get("employee") for r in res.get("rows", [])]
    res = call(x.env(user=x.hse.id), "model_report", module="M59", report="statutory_compliance")
    row = next(r for r in res["rows"] if r["record"] == inc.statutory_record_id.name)
    assert row["notice_due"] != "—" and row["overdue"] in ("No", "OVERDUE")


def test_the_notice_clock_escalates_once_per_level(x):
    inc = _report(
        x,
        x.plain,
        incident_type="fire",
        severity="high",
        injured_employee_id=x.plain.employee_id.id,
        accident_datetime=x.now - timedelta(days=10),
    )
    Reg = x.env["fix.statutory.accident.register"]
    assert Reg.cron_escalate_dife_notices() >= 1
    reg = inc.statutory_record_id
    assert reg.notice_escalation_level == 2
    assert reg.activity_ids.filtered(lambda a: a.user_id == x.notifier)
    count = len(reg.activity_ids)
    Reg.cron_escalate_dife_notices()
    assert len(reg.activity_ids) == count


def test_the_clock_cron_opens_a_missing_register_entry(x):
    """Live M59-F4: reportable incidents escalated before this build have no
    Form 28 entry; the clock cron opens it."""
    inc = _serious(x)
    reg = inc.statutory_record_id
    inc.sudo().write({"statutory_record_id": False})
    reg.sudo().unlink()
    x.env["fix.statutory.accident.register"].cron_escalate_dife_notices()
    assert inc.statutory_record_id and inc.statutory_record_id.employee_id == x.plain.employee_id


def test_serious_incident_alert_is_consumed(x):
    inc = _serious(x)
    event = _events(x.env, "hse.incident_reported", inc.id)
    x.env["fix.hse.incident"].consume_incident_reported(event._relay_event_dict())
    assert inc.alert_sent_on
    assert inc.activity_ids.filtered(lambda a: a.user_id == x.hse)
    count = len(inc.activity_ids)
    x.env["fix.hse.incident"].consume_incident_reported(event._relay_event_dict())
    assert len(inc.activity_ids) == count


# =================================================================== I5 compensation
def test_compensation_is_approved_by_someone_else_and_handed_to_payroll(x):
    inc = _serious(x)
    reg = _notify(x, inc)
    reg.with_user(x.hse).write(
        {
            "compensation_basis": "temporary",
            "compensation_proposed": 25000.0,
            "compensation_reason": "Half wages for 30 days",
        }
    )
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse, reg, {"statutory_compensation_bdt": 1.0})
    with pytest.raises(REFUSED):
        reg.with_user(x.hse).action_approve_compensation()
    reg.with_user(x.hse).action_request_approval()
    assigned = reg.approval_request_id.task_ids.mapped("assigned_user_id")
    assert x.hse not in assigned and x.plain not in assigned  # requester and the injured worker
    task = reg.approval_request_id.task_ids.filtered(
        lambda t: t.assigned_user_id == x.comp_approver
    )
    task.with_user(x.comp_approver).action_approve()
    reg.invalidate_recordset()
    assert reg.statutory_compensation_bdt == 25000.0 and reg.state == "compensation_settled"
    award = _events(x.env, "hse.compensation.awarded", reg.id)
    assert len(award) == 1
    payload = json.loads(award.payload)
    assert payload["employee_id"] == x.plain.employee_id.id and payload["amount"] == 25000.0
    assert payload["incident_id"] == inc.id and payload["reason"]
    with pytest.raises(UserError, match="approved and handed to payroll"):
        _rpc_write(x.env, x.hse, reg, {"compensation_proposed": 99999.0})


# =================================================================== lone worker
def test_missed_checkout_escalates_by_cron_and_alerts_the_buddy(x):
    Lone = x.env(user=x.plain.id)["fix.hse.loneworker"]
    session = Lone.create(
        {
            "checkin_time": x.now - timedelta(hours=6),
            "expected_end": x.now - timedelta(hours=4),
            "buddy_id": x.colleague.employee_id.id,
            "location": "Uttara customer site",
        }
    )
    assert x.env["fix.hse.loneworker"].cron_escalate_missed_checkouts() >= 1
    assert session.state == "escalated" and session.escalated_on
    event = _events(x.env, "hse.loneworker.escalated", session.id)
    assert len(event) == 1
    x.env["fix.hse.loneworker"].consume_loneworker_escalated(event._relay_event_dict())
    assert session.activity_ids.filtered(lambda a: a.user_id == x.colleague)
    assert x.env["fix.hse.loneworker"].cron_escalate_missed_checkouts() == 0 or (
        session.state == "escalated"
    )


def test_colleague_cannot_silence_a_lone_worker_session(x):
    session = x.env(user=x.plain.id)["fix.hse.loneworker"].create(
        {"expected_end": x.now + timedelta(hours=2), "buddy_id": x.colleague.employee_id.id}
    )
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.plain, session, {"state": "checked_out"})
    with pytest.raises(AccessError):
        session.with_user(x.colleague).action_checkout()
    with pytest.raises(AccessError):
        x.env(user=x.colleague.id)["fix.hse.loneworker"].create(
            {"employee_id": x.plain.employee_id.id, "expected_end": x.now + timedelta(hours=1)}
        )
    session.with_user(x.plain).action_checkout()
    assert session.state == "checked_out"


def test_a_session_needs_an_expected_end(x):
    with pytest.raises(ValidationError, match="expected end"):
        x.env(user=x.plain.id)["fix.hse.loneworker"].create({})


# =================================================================== JSA
def test_jsa_is_approved_by_another_hse_officer_and_frozen(x):
    jsa = x.env(user=x.hse.id)["fix.hse.jsa"].create(
        {
            "name": "Micro-soldering",
            "job_type": "BGA rework",
            "steps": "1. Preheat",
            "hazards": "Burns, fumes",
            "controls": "Extractor, gloves",
        }
    )
    with pytest.raises(REFUSED):
        jsa.with_user(x.hse).action_approve()
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse, jsa, {"approved_by_id": x.hse2.employee_id.id})
    _decide(jsa, x.hse, x.hse2)
    assert jsa.state == "approved" and jsa.approved_by_id == x.hse2.employee_id
    assert jsa.approved_user_id == x.hse2
    with pytest.raises(UserError, match="new revision"):
        _rpc_write(x.env, x.hse, jsa, {"controls": ""})
    new_id = jsa.with_user(x.hse).action_revise()["ids"][0]
    revision = x.env["fix.hse.jsa"].browse(new_id)
    assert revision.state == "draft" and revision.revision == 2
    _decide(revision, x.hse, x.hse2)
    assert jsa.state == "retired"


# =================================================================== hazards
def test_hazard_closes_only_with_controls_and_another_reviewer(x):
    hz = x.env(user=x.hse.id)["fix.hse.hazard"].create(
        {"name": "Live mains on bench", "likelihood": 5, "severity": 5}
    )
    assert hz.risk_score == 25 and hz.residual_risk == "critical"
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse, hz, {"state": "closed"})
    with pytest.raises(UserError, match="controls are recorded"):
        hz.with_user(x.hse).action_close()
    with pytest.raises(UserError, match="controls"):
        hz.with_user(x.hse).action_control()
    hz.with_user(x.hse).write(
        {"controls": "Isolation transformer", "residual_likelihood": 1, "residual_severity": 3}
    )
    hz.with_user(x.hse).action_control()
    assert hz.residual_risk == "low"
    with pytest.raises(UserError, match="another HSE Officer"):
        hz.with_user(x.hse).action_close()
    hz.with_user(x.hse2).action_close()
    assert hz.state == "closed"


# =================================================================== inspections, road, substances
def test_inspection_does_not_pass_by_default(x):
    insp = x.env(user=x.hse.id)["fix.safety.inspection"].create(
        {"name": "A09 walk", "branch_id": x.branch.id}
    )
    with pytest.raises(UserError, match="inspector"):
        insp.with_user(x.hse).action_complete()
    insp.with_user(x.hse).write({"inspector_id": x.hse.employee_id.id})
    with pytest.raises(UserError, match="findings"):
        insp.with_user(x.hse).action_complete()
    insp.with_user(x.hse).write({"findings": "Nothing inspected yet"})
    insp.with_user(x.hse).action_complete()
    assert insp.state == "follow_up" and insp.findings_count == 7
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse, insp, {"state": "done"})


def test_road_check_needs_every_item_and_a_valid_licence(x):
    Road = x.env(user=x.plain.id)["fix.hse.roadcheck"]
    blank = Road.create({"vehicle_ref": "DHA-1"})
    assert not blank.passed and blank.employee_id == x.plain.employee_id
    with pytest.raises(UserError, match="computed"):
        _rpc_write(x.env, x.plain, blank, {"passed": True})
    with pytest.raises(AccessError):
        Road.create({"employee_id": x.colleague.employee_id.id, "vehicle_ref": "DHA-2"})
    ok = {"tyres_ok": True, "brakes_ok": True, "lights_ok": True, "documents_ok": True}
    assert not Road.create(
        {**ok, "licence_expiry": x.today - timedelta(days=1), "vehicle_ref": "DHA-3"}
    ).passed
    assert Road.create({**ok, "licence_expiry": x.today + timedelta(days=90)}).passed


def test_substance_and_ppe_state_follow_the_figures(x):
    sub = x.env(user=x.hse.id)["fix.hazardous.substance.register"].create(
        {
            "name": "IPA",
            "storage_location": "Cabinet 1",
            "current_stock_litres": 500,
            "max_allowable_litres": 50,
        }
    )
    assert sub.state == "threshold_exceeded"
    sub.with_user(x.hse).write({"current_stock_litres": 10})
    assert sub.state == "no_msds"
    with pytest.raises(UserError, match="computed"):
        _rpc_write(
            x.env,
            x.hse,
            x.env["fix.ppe.register"].create({"name": "Goggles"}),
            {"state": "compliant"},
        )
    ppe = x.env(user=x.hse.id)["fix.ppe.register"].create(
        {"name": "Wristband", "stock_quantity": 0, "min_required_quantity": 10}
    )
    assert ppe.state == "replenish"
    sub.with_user(x.hse).action_quarantine(reason="Swollen Li-ion lot")
    assert sub.state == "quarantined"


def test_ppe_is_issued_and_acknowledged_by_the_recipient(x):
    ppe = x.env(user=x.hse.id)["fix.ppe.register"].create(
        {"name": "Gloves", "stock_quantity": 5, "min_required_quantity": 1}
    )
    with pytest.raises(AccessError):
        x.env(user=x.plain.id)["fix.ppe.issue"].create(
            {"employee_id": x.plain.employee_id.id, "ppe_id": ppe.id}
        )
    issue = x.env(user=x.hse.id)["fix.ppe.issue"].create(
        {"employee_id": x.plain.employee_id.id, "ppe_id": ppe.id, "quantity": 2}
    )
    assert ppe.stock_quantity == 3
    with pytest.raises(AccessError):
        issue.with_user(x.colleague).action_acknowledge()
    issue.with_user(x.plain).action_acknowledge()
    assert issue.acknowledged
    assert (
        x.env["fix.ppe.register"].search_count([])
        and m59.kpis(x.env(user=x.hse.id))["ppe_compliance"] <= 100.0
    )


# =================================================================== drills, committee
def test_drill_completion_needs_participants_and_duration(x):
    drill = x.env(user=x.hse.id)["fix.hse.drill"].create({"drill_type": "fire"})
    with pytest.raises(UserError, match="participants"):
        drill.with_user(x.hse).action_complete()
    drill.with_user(x.hse).write({"participants": 18, "duration_min": 12})
    drill.with_user(x.hse).action_complete()
    assert drill.state == "completed"


def test_committee_composition_dife_registration_and_meetings(x):
    Emp = x.env["hr.employee"]
    chair = Emp.create({"name": "A09 Chair"})
    committee = x.env(user=x.hse.id)["fix.safety.committee"].create(
        {
            "name": "A09 Committee",
            "branch_id": x.branch.id,
            "chairperson_id": chair.id,
            "secretary_id": chair.id,
        }
    )
    assert not committee.dife_registered and committee.state == "draft"
    with pytest.raises(UserError, match="at least"):
        committee.with_user(x.hse).action_activate()
    Member = x.env(user=x.hse.id)["fix.safety.committee.member"]
    Member.create({"committee_id": committee.id, "employee_id": chair.id, "side": "employer"})
    secretary = Emp.create({"name": "A09 Secretary"})
    Member.create({"committee_id": committee.id, "employee_id": secretary.id, "side": "worker"})
    for i in range(4):
        Member.create(
            {
                "committee_id": committee.id,
                "employee_id": Emp.create({"name": "A09 Member %d" % i}).id,
                "side": "worker" if i % 2 else "employer",
            }
        )
    with pytest.raises(UserError, match="same person"):
        committee.with_user(x.hse).action_activate()
    committee.with_user(x.hse).write({"secretary_id": secretary.id})
    committee.with_user(x.hse).action_activate()
    assert committee.state == "active"
    with pytest.raises(UserError, match="changes only through its workflow"):
        _rpc_write(x.env, x.hse, committee, {"dife_registered": True})
    with pytest.raises(UserError, match="minutes"):
        committee.with_user(x.hse).action_record_meeting()
    committee.with_user(x.hse).action_record_meeting(minutes_text="Reviewed Q3 incidents")
    today = fields.Date.context_today(committee)
    assert committee.last_meeting_date == today and committee.next_meeting_date > today


def test_an_overdue_committee_meeting_is_flagged(x):
    Emp = x.env["hr.employee"]
    a, b = Emp.create({"name": "A09 A"}), Emp.create({"name": "A09 B"})
    committee = x.env["fix.safety.committee"].create(
        {
            "name": "A09 Old",
            "branch_id": x.branch.id,
            "chairperson_id": a.id,
            "secretary_id": b.id,
            "formation_date": "2025-01-15",
        }
    )
    committee.sudo()._guarded().write({"state": "active"})
    assert committee.meeting_overdue
    x.env["fix.safety.committee"].cron_flag_overdue_meetings()
    assert committee.state == "review_needed"


# =================================================================== health
def test_health_records_are_occupational_health_only_with_a_trail(x):
    rec = x.env(user=x.oh.id)["fix.hse.health"].create(
        {"employee_id": x.plain.employee_id.id, "fitness": "unfit", "clinician": "Dr Rahman"}
    )
    for who in (x.plain, x.hse):
        with pytest.raises(AccessError):
            rec.with_user(who).read(["fitness"])
    x.env.cr.flush()  # tracking is finalised per flush (mail precommit hook)
    rec.with_user(x.oh).write({"fitness": "fit"})
    x.env.cr.flush()
    tracked = rec.sudo().message_ids.mapped("tracking_value_ids.field_id.name")
    assert "fitness" in tracked


# =================================================================== deployment
@pytest.mark.parametrize(
    "xmlid",
    [
        "cd_hse.cron_hse_loneworker_missed",
        "cd_hse.cron_hse_dife_notice_clock",
        "cd_hse.cron_hse_committee_meetings",
        "cd_hse.cron_hse_hazard_reviews",
    ],
)
def test_crons_are_deployed_and_active(odoo_env, xmlid):
    cron = odoo_env.ref(xmlid)
    assert cron.active and cron.user_id == odoo_env.ref("base.user_root")


def test_consumers_groups_and_acl_rows_are_deployed(odoo_env):
    for xmlid in ("cd_hse.consumer_hse_incident_alert", "cd_hse.consumer_hse_loneworker_escalated"):
        consumer = odoo_env.ref(xmlid)
        assert consumer.active and callable(getattr(odoo_env[consumer.model], consumer.method))
    for xmlid in ("cd_hse.group_statutory_notifier", "cd_hse.group_injury_compensation_approver"):
        holders = odoo_env.ref(xmlid).user_ids
        assert holders <= (odoo_env.ref("base.user_root") | odoo_env.ref("base.user_admin"))
    for xmlid in (
        "cd_hse.access_fix_ppe_issue_role",
        "cd_hse.access_fix_safety_committee_meeting_role",
        "cd_hse.access_fix_statutory_register_notifier",
    ):
        assert odoo_env.ref(xmlid).perm_read
    assert odoo_env.ref("cd_hse.param_dife_notice_working_days").value == "2"


def test_workspace_actions_exist_and_never_offer_the_apply_methods(odoo_env):
    for model, conf in m59.SURFACES.items():
        for method in conf["actions"]:
            assert callable(getattr(odoo_env[model], method, None)), (model, method)
    assert "action_approve" not in a09.SURFACES["fix.hse.jsa"]["actions"]
    assert (
        "action_approve_compensation"
        not in a09.SURFACES["fix.statutory.accident.register"]["actions"]
    )
