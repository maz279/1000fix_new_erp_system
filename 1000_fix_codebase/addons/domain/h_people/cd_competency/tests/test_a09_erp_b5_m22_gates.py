# A09 ERP audit fix program, builder B5 — M22 gate, override-log, Dhaka-day
# and automation tests for the R2/R9 findings M22-F2, F3, F4, F8, F11, F12,
# F13 and the catalogue skill-profile gate M22-F10 (BRU-CAT-06).
# ruff: noqa: F811  (pytest fixtures imported from the round-1 suite and used
# as test parameters — the estate's convention, see the live capture suite)
#
# Reuses the round-1 suite's fixtures (attacked as fresh NON-admin users);
# the superuser only builds the world. Mutation checks: each test refuses
# exactly the re-introduced defect it names.
import datetime
import uuid
from unittest import mock

import odoo.addons.cd_competency.models.fix_competency as fc
import odoo.addons.cd_competency.models.fix_training_session as fts
from odoo import fields
from odoo.addons.cd_competency.tests.test_a09_m22_controls import (  # noqa: F401 (fixtures)
    TRAINING,
    _employee,
    _events,
    _user,
    c,
    refused,
)
from odoo.exceptions import UserError

TAG = "B5-%s" % uuid.uuid4().hex[:6]
FIELD_SERVICE_USER = "cd_field_service.group_fix_field_service_user"
WAIVER_MSG = "waiver SET by SUPERUSER"
GRANT_MSG = "granted by SUPERUSER"


def _comp(c, code, device_type="laptop", tier=None, **extra):
    vals = {
        "code": "%s-%s" % (TAG, code),
        "name": "B5 %s" % code,
        "device_type": device_type,
        "pass_mark": 70,
    }
    if tier:
        vals["repair_tier"] = tier
    vals.update(extra)
    return c.env["fix.competency"].create(vals)


def _valid_cert(c, employee, comp, tier=None, **extra):
    today = fields.Date.context_today(c.env.user.with_context(tz="Asia/Dhaka"))
    vals = {
        "employee_id": employee.id,
        "competency_id": comp.id,
        "issued_on": today - datetime.timedelta(days=10),
        "expires_on": today + datetime.timedelta(days=700),
    }
    if tier:
        vals["repair_tier"] = tier
    vals.update(extra)
    return c.env["fix.certification"].sudo().create(vals)  # su create -> valid


def _messages(rec, needle=""):
    return (
        rec.env["mail.message"]
        .sudo()
        .search([("model", "=", rec._name), ("res_id", "=", rec.id), ("body", "ilike", needle)])
    )


def _activities(rec):
    return (
        rec.env["mail.activity"]
        .sudo()
        .search([("res_model", "=", rec._name), ("res_id", "=", rec.id)])
    )


# ================================================================== M22-F3
def test_an_untiered_certification_does_not_satisfy_a_tiered_job(c):
    """Probe D5: a tier-less 'certified for laptop' passed an L4 job."""
    tierless = _comp(c, "NOTIER")
    _valid_cert(c, c.e_col, tierless)
    ok, why = c.env["fix.certification"].dispatch_eligibility(
        c.e_col, device_type="laptop", repair_tier="l4"
    )
    assert ok is False, "an un-tiered certification satisfied a tiered requirement"
    assert "TIER" in why.upper() and "L4" in why.upper()


def test_a_certification_at_the_requested_tier_passes(c):
    l4 = _comp(c, "L4COMP", tier="l4")
    _valid_cert(c, c.e_col, l4, tier="l4")
    for tier in ("l2", "l4"):
        ok, why = c.env["fix.certification"].dispatch_eligibility(
            c.e_col, device_type="laptop", repair_tier=tier
        )
        assert ok, (tier, why)
    low = _comp(c, "L2COMP", tier="l2")
    _valid_cert(c, c.e_uncert, low, tier="l2")
    ok, why = c.env["fix.certification"].dispatch_eligibility(
        c.e_uncert, device_type="laptop", repair_tier="l3"
    )
    assert ok is False and "TIER L2" in why.upper()


def test_a_competency_tier_satisfies_a_tierless_cert(c):
    """The competency's declared tier feeds the cert that carries none."""
    comp = _comp(c, "COMPTIER", tier="l3")
    _valid_cert(c, c.e_col, comp)  # cert tier unset
    ok, why = c.env["fix.certification"].dispatch_eligibility(
        c.e_col, device_type="laptop", repair_tier="l3"
    )
    assert ok, why
    ok, _why = c.env["fix.certification"].dispatch_eligibility(
        c.e_col, device_type="laptop", repair_tier="l4"
    )
    assert ok is False


# ================================================================== M22-F2
def test_the_workshop_gate_switch_leaves_today_alone_and_can_close(c):
    """Both switch positions: off (today's deliberate open window) and on
    (probe D6/D7). A gated device type passes either way; an ungated one
    passes only while the switch is off."""
    Param = c.env["ir.config_parameter"].sudo()
    param = "cd_competency.workshop_gate_fail_closed"
    tablet = _comp(c, "TAB", device_type="tablet", tier="l2")
    _valid_cert(c, c.e_col, tablet, tier="l2")
    gated = {"device_type": "tablet", "fail_closed_param": param}
    ungated = {"device_type": "desktop", "fail_closed_param": param}
    # default (unset): today's open window — the ungated device type passes
    ok, why = c.env["fix.certification"].dispatch_eligibility(c.e_col, **gated)
    assert ok, why
    ok, why = c.env["fix.certification"].dispatch_eligibility(c.e_col, **ungated)
    assert ok, why
    # the COO flips the switch: the ungated device type now fails closed
    Param.set_param(param, "true")
    try:
        ok, why = c.env["fix.certification"].dispatch_eligibility(c.e_col, **ungated)
        assert ok is False and "fail-closed" in why
        ok, why = c.env["fix.certification"].dispatch_eligibility(c.e_col, **gated)
        assert ok, why
    finally:
        Param.set_param(param, False)
    ok, why = c.env["fix.certification"].dispatch_eligibility(c.e_col, **ungated)
    assert ok, why


def test_the_readiness_pack_lists_ungated_device_types_and_missing_tiers(c):
    from odoo.addons.cd_p03_portal.controllers.a09 import m22

    # the round-1 fixture gates smartphone + laptop with NO tier; this one is
    # gated and tiered
    _comp(c, "TIERED", device_type="desktop", tier="l2")
    pack = m22.gate_readiness(c.env)
    rows = {r["device_type"].split(" (")[0]: r for r in pack["rows"]}
    assert rows["desktop"]["state"] == "Gated" and rows["desktop"]["without_tier"] == 0
    assert rows["smartphone"]["state"] == "Gated, tier missing"
    assert rows["tablet"]["state"].startswith("UNGATED")
    assert "as at" in pack["title"]


# ================================================================== M22-F12
def test_a_refused_assignment_leaves_the_technician_unchanged(c):
    """Probe F9: the gate raised AFTER super().write(); a caller that caught
    the UserError kept the blocked technician."""
    wo = c.env["fix.work.order"].create({"order_id": c.so_laptop.id})
    try:
        with c.env.cr.savepoint():
            wo.with_user(c.disp).write({"technician_id": c.e_uncert.id})
            c.env.flush_all()
    except UserError:
        pass
    assert not wo.technician_id, "the blocked assignment was written"


def test_a_bare_superuser_flag_never_covers_a_reassignment(c):
    """A bare waiver flag covers the technician it was set for (here: none),
    never a reassignment — the pre-write gate refuses and the job is clean."""
    waivered = c.env["fix.work.order"].create({"order_id": c.so_laptop.id})
    waivered._guarded().write({"certification_waiver": True})
    err = refused(c.env, lambda: waivered.with_user(c.disp).write({"technician_id": c.e_uncert.id}))
    assert err and "M22 eligibility" in err
    assert not waivered.technician_id and waivered.certification_waiver


# ================================================================== M22-F11
def test_a_superuser_waiver_tick_is_logged_on_the_job(c):
    wo = c.env["fix.work.order"].create({"order_id": c.so_laptop.id})
    assert not _messages(wo, WAIVER_MSG)
    wo.sudo().write({"certification_waiver": True})
    logged = _messages(wo, WAIVER_MSG)
    assert logged and c.env.user.name in logged[0].body, "the override was silent"


def test_a_superuser_valid_certification_create_is_logged(c):
    comp = _comp(c, "LOGC")
    cert = (
        c.env["fix.certification"]
        .sudo()
        .create(
            {
                "employee_id": c.e_col.id,
                "competency_id": comp.id,
                "issued_on": fields.Date.today(),
                "expires_on": fields.Date.today() + datetime.timedelta(days=365),
            }
        )
    )
    assert cert.state == "valid"
    logged = _messages(cert, GRANT_MSG)
    assert logged and c.env.user.name in logged[0].body, "the su grant was silent"


def test_a_normal_draft_create_is_not_logged_as_an_override(c):
    comp = _comp(c, "QUIET")
    # a Training Manager's own create (NOT the superuser path): a draft, and
    # no "granted by SUPERUSER" message
    cert = (
        c.env["fix.certification"]
        .with_user(c.trn)
        .create(
            {
                "employee_id": c.e_col.id,
                "competency_id": comp.id,
                "issued_on": fields.Date.today(),
                "expires_on": fields.Date.today() + datetime.timedelta(days=365),
            }
        )
    )
    assert cert.state == "draft" and not _messages(cert, GRANT_MSG)


# ================================================================== M22-F8
def test_the_expiry_alert_reaches_both_the_employee_and_the_manager(c):
    today = fields.Date.context_today(c.env.user.with_context(tz="Asia/Dhaka"))
    holder_user = _user(c.env)
    holder = _employee(c.env, holder_user)
    manager_user = _user(c.env)
    holder.parent_id = _employee(c.env, manager_user)
    comp = _comp(c, "DUAL")
    _valid_cert(
        c,
        holder,
        comp,
        expires_on=today + datetime.timedelta(days=5),
        brand_critical=True,
    )
    c.env["fix.certification"]._cron_certification_expiry()
    acts = _activities(comp.env["fix.certification"].search([("employee_id", "=", holder.id)]))
    users = {a.user_id for a in acts}
    assert (
        holder_user in users and manager_user in users
    ), "the renewal alert must reach BOTH (manager-or-employee before)"
    assert any("brand-critical" in (a.summary or "") for a in acts)
    # idempotent: a second run does not duplicate the alerts
    c.env["fix.certification"]._cron_certification_expiry()
    assert len(
        _activities(comp.env["fix.certification"].search([("employee_id", "=", holder.id)]))
    ) == len(acts)


def test_brand_critical_exists_on_the_model(c):
    comp = _comp(c, "BCRIT")
    cert = _valid_cert(c, c.e_col, comp)
    assert "brand_critical" in c.env["fix.certification"]._fields
    cert.sudo().write({"brand_critical": True})
    assert cert.brand_critical


# ================================================================== M22-F13
def test_the_business_day_is_dhaka_not_the_server_clock(odoo_env):
    # 23rd 21:30 UTC == 24th 03:30 Dhaka; 23rd 02:30 UTC == 23rd 08:30 Dhaka
    assert fc.dhaka_today(odoo_env, now=datetime.datetime(2026, 11, 23, 21, 30)) == (
        datetime.date(2026, 11, 24)
    )
    assert fc.dhaka_today(odoo_env, now=datetime.datetime(2026, 11, 23, 2, 30)) == (
        datetime.date(2026, 11, 23)
    )


def test_status_cron_and_gate_follow_the_dhaka_day(c):
    """Around midnight UTC the server date and the Dhaka date disagree: the
    certification rules follow the Dhaka business day."""
    comp = _comp(c, "DHAKA")
    cert = _valid_cert(
        c, c.e_col, comp, expires_on=fields.Date.today() + datetime.timedelta(days=5)
    )
    later = fields.Date.today() + datetime.timedelta(days=20)
    with mock.patch.object(fc, "dhaka_today", return_value=later):
        assert cert.status == "expired", "the Dhaka day is past the expiry"
        c.env["fix.certification"]._cron_certification_expiry()
        assert cert.state == "lapsed"
        ok, _why = c.env["fix.certification"].dispatch_eligibility(c.e_col, device_type="laptop")
        assert ok is False, "the gate judged the certificate by the server date"


# ================================================================== M22-F4
def _relay(env):
    env.flush_all()
    env["fix.event.outbox"].sudo().cron_relay()
    env.flush_all()


def _slot(c, employee, day):
    shift = c.env["fix.shift.template"].create(
        {"name": "B5 shift %s" % TAG, "start_hour": 9, "end_hour": 18}
    )
    return c.env["fix.roster.slot"].create(
        {"employee_id": employee.id, "date": day, "shift_id": shift.id}
    )


def _session(c, start, **vals):
    base = {
        "course_id": c.course.id,
        "delivery_mode": "classroom",
        "trainer_id": c.e_assessor.id,
        "venue": "B5 room",
        "date_start": start,
        "date_end": start + datetime.timedelta(hours=6),
        "capacity": 5,
    }
    base.update(vals)
    return c.env["fix.training.session"].with_user(c.trn).create(base)


def test_the_dhaka_dates_of_a_session_spanning_midnight_utc():
    # 21:00 UTC on the 23rd is already the 24th in Dhaka
    assert fts._dhaka_dates(
        datetime.datetime(2026, 11, 23, 21, 0), datetime.datetime(2026, 11, 24, 3, 0)
    ) == [datetime.date(2026, 11, 24)]


def test_a_scheduled_session_flags_the_trainees_roster_slots(c):
    start = datetime.datetime.now() + datetime.timedelta(days=3)
    sess = _session(c, start.replace(microsecond=0))
    (
        c.env["fix.training.enrollment"]
        .with_user(c.trn)
        .create({"course_id": c.course.id, "session_id": sess.id, "employee_id": c.e_col.id})
    )
    day = fts._dhaka_dates(sess.date_start, sess.date_end)[0]
    marked = _slot(c, c.e_col, day)
    untouched = _slot(c, c.e_uncert, day)
    sess.with_user(c.trn).action_schedule()
    assert _events(c.env, "training.session.scheduled", sess.id)
    _relay(c.env)
    assert marked.on_leave, "the trainee's roster slot was not flagged (FR-LMS-022)"
    assert not untouched.on_leave
    # idempotent: a redelivery flags nothing new and raises nothing
    c.env["fix.training.session"].consume_training_session_scheduled(
        {"aggregate_id": sess.id, "payload": {"employee_ids": [c.e_col.id]}}
    )
    assert marked.on_leave and not untouched.on_leave
    # cancelling releases the marks (BRU-LMS-08 gives the availability back)
    sess.with_user(c.trn).action_cancel()
    c.env.invalidate_all()
    assert not marked.exists().on_leave and not untouched.exists().on_leave


# ================================================================== AUT-LMS-12/13 (deployment)
def test_the_automation_wiring_exists(odoo_env):
    cron12 = odoo_env.ref("cd_competency.ir_cron_training_effectiveness")
    assert cron12.active and cron12.model_id.model == "fix.training.session"
    assert "_cron_training_effectiveness_reminder" in cron12.code
    cron13 = odoo_env.ref("cd_competency.ir_cron_competency_coverage")
    assert cron13.active and cron13.model_id.model == "fix.certification"
    assert "_cron_competency_coverage" in cron13.code and cron13.interval_type == "months"
    sub = odoo_env.ref("cd_competency.consumer_training_session_scheduled")
    assert sub.active and sub.event_type == "training.session.scheduled"
    assert sub.model == "fix.training.session"
    assert callable(getattr(odoo_env[sub.model], sub.method))


def test_the_90_day_effectiveness_reminder_fires_once(c):
    end = datetime.datetime.now() - datetime.timedelta(days=100)
    sess = _session(c, end.replace(microsecond=0))
    enr = (
        c.env["fix.training.enrollment"]
        .with_user(c.trn)
        .create({"course_id": c.course.id, "session_id": sess.id, "employee_id": c.e_col.id})
    )
    sess.with_user(c.trn).action_schedule()
    enr.with_user(c.trn).action_mark_attended()
    sess.with_user(c.trn).action_mark_held()
    flagged = c.env["fix.training.session"]._cron_training_effectiveness_reminder()
    assert flagged and sess in flagged
    acts = _activities(sess)
    assert acts and any("90 days" in (a.note or "") for a in acts)
    c.env["fix.training.session"]._cron_training_effectiveness_reminder()
    assert len(_activities(sess)) == len(acts), "the reminder must fire once"


def test_the_monthly_coverage_cron_flags_single_points_of_failure(c):
    # coverage is computed per DISPATCH-GATING competency (FR-LMS-008): both
    # fixtures are gating, one holds a single valid certificate
    spof = _comp(c, "SPOF", tier="l2", required_for_dispatch=True)
    safe = _comp(c, "SAFE", device_type="smartphone", tier="l2", required_for_dispatch=True)
    _valid_cert(c, c.e_col, spof)
    _valid_cert(c, c.e_uncert, safe)
    _valid_cert(c, _employee(c.env), safe)
    flagged = c.env["fix.certification"]._cron_competency_coverage()
    assert spof in flagged and safe not in flagged
    acts = _activities(spof)
    assert acts and any("single point of failure" in (a.note or "") for a in acts)
    c.env["fix.certification"]._cron_competency_coverage()
    assert len(_activities(spof)) == len(acts)


# ================================================================== M22-F10
def _catalogue_item(c, user, item_type="service", **extra):
    n = uuid.uuid4().hex[:6]
    tmpl = c.env["product.template"].create(
        {"name": "%s item %s" % (TAG, n), "default_code": "%s-%s" % (TAG, n), "name_bn": "পরীক্ষা"}
    )
    cat = c.env["product.category"].search([("tree_type", "=", "commercial")], limit=1) or (
        c.env["product.category"].create({"name": "%s commercial" % TAG, "tree_type": "commercial"})
    )
    vals = {
        "product_tmpl_id": tmpl.id,
        "item_type": item_type,
        "category_id": cat.id,
        "vat_class": "standard_15",
        "revenue_recognition": "on_completion",
        "scope_of_work": "Replace the part and test.",
        "mode_duration_ids": [(0, 0, {"delivery_mode": "walk_in", "standard_minutes": 40})],
    }
    if item_type == "labour":
        vals.update({"repair_level": "l1", "standard_labour_time": 1.0})
    vals.update(extra)
    return c.env["fix.catalogue.item"].with_user(user).create(vals)


def test_a_service_operation_cannot_leave_draft_without_its_skill_profile(c):
    """M22-F10: the estate's repair operations are typed 'service' (76
    approved, 0 with a competency); the gate only fired for 'labour'."""
    officer = _user(c.env, "cd_catalogue.group_catalogue_officer")
    svc = _catalogue_item(c, officer)
    assert svc.item_type == "service"
    err = refused(c.env, lambda: svc.with_user(officer).action_submit())
    assert err and "skill profile" in err, "a service left Draft with no competency (BRU-CAT-06)"
    svc.with_user(officer).write({"required_competency_id": c.c_lap.id})
    svc.with_user(officer).action_submit()
    assert svc.state == "in_review"
    # a non-operation type never needed one
    part = _catalogue_item(
        c,
        officer,
        item_type="part",
        scope_of_work=False,
        mode_duration_ids=[],
    )
    part.with_user(officer).action_submit()
    assert part.state == "in_review"
