"""A07 P1/P2 (2026-11-04), M45 calibration: profile and interval, as-found /
as-left readings against tolerance bands, the usage decision by a second
person, the insert-only record, the retrospective impact assessment with its
NCR, and the routed interval-change approval. Live ORM (``odoo_env``, rolled
back); attacks run as NON-ADMIN users holding the role they would really hold
(and without it where the role is the control).

Audit probes covered: 05 (fail -> out of service + impact + quality event),
09 (100-year validity), 10 (back-dated certificate), 11/12/43 (insert-only).
"""

import itertools
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
    inbox_task,
)
from odoo.exceptions import AccessError, UserError, ValidationError

TAG = "A7M45C"
ROLE_QM = "cd_equipment_register.group_quality_manager"
ROLE_CAL = "cd_equipment_register.group_calibration_technician"
PARAM_ROLE = "cd_equipment_register.calibration_requires_role"
PARAM_DECISION = "cd_equipment_register.usage_decision_required"
PARAM_MAX = "cd_equipment_register.max_calibration_interval_months"
REFUSED = (UserError, ValidationError, AccessError)
_SEQ = itertools.count(1)


def _user(env, tag, groups=()):
    n = next(_SEQ)
    ou = env["operating.unit"].search([], limit=1)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %s %d" % (TAG, tag, n),
                "login": "%s.%s.%d@a07.test" % (TAG.lower(), tag, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    env["hr.employee"].create({"name": "%s %s %d (emp)" % (TAG, tag, n), "user_id": user.id})
    return user


def refused(env, fn, match=None):
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED as exc:
        env.invalidate_all()
        if match and match not in str(exc):
            raise AssertionError("refused for another reason: %s" % exc) from exc
        return True
    return False


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, n=0)
    x.today = fields.Date.context_today(env["fix.equipment"])
    x.clerk = _user(env, "clerk")
    x.tech = _user(env, "tech", [ROLE_CAL])
    x.qm = _user(env, "qm", [ROLE_QM])
    x.qm2 = _user(env, "qm2", [ROLE_QM])
    ICP = env["ir.config_parameter"].sudo()
    for key in (PARAM_ROLE, PARAM_DECISION, PARAM_MAX):
        ICP.set_param(key, False)
    return x


def eq(c, **kw):
    c.n += 1
    vals = {"code": "%s-EQ-%02d" % (TAG, c.n), "name": "%s meter %d" % (TAG, c.n)}
    vals.update(kw)
    return c.env["fix.equipment"].create(vals)


def cal(c, e, user=None, on=None, due=None, result="pass", **kw):
    vals = {
        "equipment_id": e.id,
        "calibrated_on": on or c.today - timedelta(days=10),
        "standard_ref": "STD-%s" % TAG,
        "certificate_ref": "CERT-%s" % TAG,
        "performed_by": "%s Lab" % TAG,
        # a new profile accepts an accredited provider only (enforced since the
        # A07 operability build); the refusal has its own test
        "provider_accredited": True,
    }
    if result is not None:
        vals["result"] = result
    if due is not False:
        vals["next_due"] = due or c.today + timedelta(days=355)
    vals.update(kw)
    return c.env["fix.calibration"].with_user(user or c.tech).create(vals)


def profiled(c, months=12, points=(("DCV 10V", 9.99, 10.01), ("Ohm 100", 99.5, 100.5))):
    e = eq(c)
    profile = (
        c.env["fix.calibration.profile"]
        .with_user(c.qm)
        .create(
            {
                "equipment_id": e.id,
                "interval_months": months,
                "point_ids": [
                    (0, 0, {"name": n, "tolerance_low": lo, "tolerance_high": hi})
                    for n, lo, hi in points
                ],
            }
        )
    )
    return e, profile


def readings(profile, *values):
    """values: (as_found,) or (as_found, as_left) per point, in order."""
    out = []
    for point, v in zip(profile.point_ids, values, strict=True):
        line = {"point_id": point.id, "as_found": v[0]}
        if len(v) > 1:
            line.update({"adjusted": True, "as_left": v[1]})
        out.append((0, 0, line))
    return out


def holds(c, e):
    return c.env["fix.equipment.oos"].search([("equipment_id", "=", e.id), ("state", "=", "open")])


# ============================================================ interval (probes 09, 10)
def test_no_profile_caps_a_typed_validity(c):
    e = eq(c)
    # probe 09: a 100-year validity is refused; probe 10: 3 years back, due +1200 d
    assert refused(c.env, lambda: cal(c, e, due=c.today + timedelta(days=36500)), "beyond")
    back = c.today - timedelta(days=1095)
    assert refused(c.env, lambda: cal(c, e, on=back, due=back + timedelta(days=1200)), "beyond")
    # an ordinary one-year certificate and an already lapsed one are recorded
    cal(c, e)
    cal(c, e, on=c.today - timedelta(days=400), due=c.today - timedelta(days=5))
    # the ceiling is a business setting (B2): 0 disables it
    c.env["ir.config_parameter"].sudo().set_param(PARAM_MAX, "0")
    cal(c, eq(c), due=c.today + timedelta(days=36500))


def test_profile_interval_sets_and_caps_next_due(c):
    e, profile = profiled(c, months=6)
    on = c.today - timedelta(days=5)
    r = cal(c, e, on=on, due=False, reading_ids=readings(profile, (10.0,), (100.0,)))
    assert r.next_due == fields.Date.add(on, months=6) and r.profile_id == profile
    assert refused(
        c.env,
        lambda: cal(
            c,
            e,
            on=on,
            due=on + timedelta(days=365),
            reading_ids=readings(profile, (10.0,), (100.0,)),
        ),
        "profile interval",
    )


# ============================================================ readings (T-10)
def test_result_is_derived_from_the_readings(c):
    e, profile = profiled(c)
    ok = cal(c, e, due=False, result=None, reading_ids=readings(profile, (10.0,), (100.2,)))
    assert (ok.result, ok.as_found_out_of_tolerance) == ("pass", False)
    adj = cal(c, e, due=False, result=None, reading_ids=readings(profile, (10.0,), (100.4, 100.0)))
    assert (adj.result, adj.as_found_out_of_tolerance) == ("adjusted", False)
    # a typed result that disagrees with the readings is refused
    assert refused(
        c.env,
        lambda: cal(
            c, e, due=False, result="pass", reading_ids=readings(profile, (10.5,), (100.0,))
        ),
        "readings give the result",
    )
    # every point must be read; a typed band is replaced by the profile's
    assert refused(
        c.env,
        lambda: cal(c, e, due=False, reading_ids=readings(profile, (10.0,), (100.0,))[:1]),
        "every measurement point",
    )
    typed = readings(profile, (10.0,), (100.0,))
    typed[0][2].update({"tolerance_low": -1e9, "tolerance_high": 1e9})
    r = cal(c, e, due=False, result=None, reading_ids=typed)
    assert r.reading_ids[0].tolerance_low == profile.point_ids[0].tolerance_low
    # with a profile, readings are required
    assert refused(c.env, lambda: cal(c, e, due=False), "as-found reading")


def test_as_found_out_of_tolerance_raises_the_impact_even_when_adjusted(c):
    e, profile = profiled(c)
    cal(
        c,
        e,
        on=c.today - timedelta(days=100),
        due=False,
        reading_ids=readings(profile, (10.0,), (100.0,)),
    )
    use = c.env["fix.equipment.usage"].create(
        {"equipment_id": e.id, "job_ref": "%s-J1" % TAG, "used_on": c.today - timedelta(days=50)}
    )
    r = cal(
        c,
        e,
        on=c.today,
        due=False,
        result=None,
        reading_ids=readings(profile, (10.3, 10.0), (100.0,)),
    )
    assert (r.result, r.as_found_out_of_tolerance) == ("adjusted", True)
    assert r.impact_id and r.impact_id.usage_ids == use
    # adjusted back within tolerance: it certifies, so no out-of-service hold
    assert not holds(c, e) and e.calibration_state == "current"


def test_readings_are_insert_only(c):
    e, profile = profiled(c)
    r = cal(c, e, due=False, reading_ids=readings(profile, (10.0,), (100.0,)))
    line = r.reading_ids[0].with_user(c.tech)
    assert refused(c.env, lambda: line.write({"as_found": 12.0}))
    assert refused(c.env, lambda: line.unlink())
    Reading = c.env["fix.calibration.reading"].with_user(c.tech)
    assert refused(
        c.env,
        lambda: Reading.create({"calibration_id": r.id, "name": "x", "as_found": 1.0}),
        "recorded with their calibration",
    )


# ============================================================ insert-only record (probes 11, 12, 43)
def test_calibration_is_insert_only_and_never_deleted(c):
    r = cal(c, eq(c), result="fail")
    for vals in ({"result": "pass"}, {"next_due": c.today + timedelta(days=99)}, {"notes": "x"}):
        assert refused(c.env, lambda v=vals: r.with_user(c.qm).write(v)), vals
    assert refused(c.env, lambda: r.with_user(c.qm).unlink())
    # system-set fields cannot be typed at create
    for vals in ({"decision_state": "accepted"}, {"as_found_out_of_tolerance": True}):
        assert refused(c.env, lambda v=vals: cal(c, eq(c), **v), "cannot be set directly"), vals
    # the register row of a calibrated item is not deleted with its certificates
    with pytest.raises(Exception), c.env.cr.savepoint():  # noqa: B017 - FK restrict
        r.equipment_id.unlink()
        c.env.flush_all()
    c.env.invalidate_all()
    assert r.exists()


# ============================================================ fail -> OOS + impact + NCR (probe 05)
def test_a_fail_puts_the_instrument_out_of_service_and_raises_the_impact(c):
    e = eq(c)
    cal(c, e, on=c.today - timedelta(days=100), due=c.today + timedelta(days=265))
    Usage = c.env["fix.equipment.usage"]
    before = Usage.create(
        {"equipment_id": e.id, "job_ref": "%s-OLD" % TAG, "used_on": c.today - timedelta(days=120)}
    )
    suspect = Usage.create(
        {"equipment_id": e.id, "job_ref": "%s-SUS" % TAG, "used_on": c.today - timedelta(days=40)}
    )
    ncr0 = c.env["fix.ncr"].search_count([])
    fail = cal(c, e, on=c.today - timedelta(days=1), due=c.today + timedelta(days=1), result="fail")
    hold = holds(c, e)
    assert e.operational_status == "out_of_service"
    assert (hold.hold_type, hold.calibration_id, hold.started_on) == (
        "calibration",
        fail,
        fail.calibrated_on,
    )
    impact = fail.impact_id
    assert impact.usage_ids == suspect and before not in impact.usage_ids
    assert impact.period_from == c.today - timedelta(days=100)
    assert c.env["fix.ncr"].search_count([]) == ncr0 + 1 and impact.ncr_ref
    assert fail.decision_state == "na"
    events = (
        c.env["fix.event.outbox"]
        .sudo()
        .search(
            [
                (
                    "event_type",
                    "in",
                    [
                        "equipment.out_of_tolerance",
                        "equipment.impact_assessment_raised",
                        "equipment.out_of_service",
                    ],
                )
            ]
        )
    )
    got = {
        (ev.event_type, ev.aggregate_id)
        for ev in events
        if ev.aggregate_id in (fail.id, impact.id, hold.id)
    }
    assert got == {
        ("equipment.out_of_tolerance", fail.id),
        ("equipment.impact_assessment_raised", impact.id),
        ("equipment.out_of_service", hold.id),
    }


def test_impact_is_closed_by_another_quality_manager_with_a_disposition(c):
    e = eq(c)
    fail = cal(c, e, user=c.qm, result="fail")
    impact = fail.impact_id
    Impact = c.env["fix.calibration.impact"]
    assert refused(
        c.env,
        lambda: Impact.with_user(c.qm).create({"calibration_id": fail.id, "equipment_id": e.id}),
    )
    assert refused(c.env, lambda: impact.with_user(c.tech).action_close_impact(), "Quality Manager")
    assert refused(c.env, lambda: impact.with_user(c.qm2).action_close_impact(), "disposition")
    impact.with_user(c.qm2).write(
        {"disposition": "retested", "disposition_note": "3 boards re-tested OK"}
    )
    assert refused(c.env, lambda: impact.with_user(c.qm).action_close_impact(), "Segregation")
    impact.with_user(c.qm2).action_close_impact()
    assert (impact.state, impact.decided_by_id) == ("closed", c.qm2)
    assert refused(c.env, lambda: impact.with_user(c.qm2).write({"disposition": "valid"}))
    use = c.env["fix.equipment.usage"].create({"equipment_id": e.id, "job_ref": "%s-LATE" % TAG})
    assert refused(c.env, lambda: impact.with_user(c.qm2).write({"usage_ids": [(4, use.id)]}))


# ============================================================ usage decision (SOD-07)
def test_usage_decision_is_a_second_quality_manager(c):
    e = eq(c)
    r = cal(c, e, user=c.qm)
    assert r.decision_state == "pending"
    assert refused(
        c.env, lambda: r.with_user(c.tech).action_accept_calibration(), "Quality Manager"
    )
    assert refused(c.env, lambda: r.with_user(c.qm).action_accept_calibration(), "Segregation")
    assert refused(c.env, lambda: r.with_user(c.qm).write({"decision_state": "accepted"}))
    r.with_user(c.qm2).action_accept_calibration()
    assert (r.decision_state, r.decided_by_id) == ("accepted", c.qm2)
    assert refused(c.env, lambda: r.with_user(c.qm2).action_reject_calibration(), "already")


def test_a_rejected_calibration_certifies_nothing(c):
    e = eq(c)
    r = cal(c, e)
    assert e.calibration_state == "current"
    assert refused(
        c.env, lambda: r.with_user(c.qm).action_reject_calibration(), "Usage Decision Note"
    )
    r.with_user(c.qm).write({"decision_note": "provider not accredited for this range"})
    r.with_user(c.qm).action_reject_calibration()
    assert (e.calibration_state, e.operational_status) == ("rejected", "out_of_service")
    assert holds(c, e).hold_type == "calibration"
    with pytest.raises(UserError, match="rejected"):
        e.with_user(c.clerk).action_assert_usable()


def test_usage_decision_switch_withholds_fitness_until_accepted(c):
    c.env["ir.config_parameter"].sudo().set_param(PARAM_DECISION, "1")
    e = eq(c)
    r = cal(c, e)
    assert e.calibration_state == "pending"
    with pytest.raises(UserError, match="usage decision"):
        e.with_user(c.clerk).action_assert_usable()
    r.with_user(c.qm).action_accept_calibration()
    assert e.with_user(c.clerk).action_assert_usable() is True


def test_calibration_role_switch(c):
    """B1: off on deploy (plain users record calibrations today); on, only a
    Calibration Technician or the Quality Manager records one."""
    e = eq(c)
    cal(c, e, user=c.clerk)
    c.env["ir.config_parameter"].sudo().set_param(PARAM_ROLE, "1")
    assert refused(c.env, lambda: cal(c, e, user=c.clerk), "Calibration Technician")
    cal(c, e, user=c.tech)
    cal(c, e, user=c.qm)


def _decision_todos(r):
    return r.sudo().activity_ids.filtered(
        lambda a: (a.summary or "").startswith("Usage decision needed")
    )


def test_b9_each_pending_calibration_is_in_the_quality_managers_todo_list(c):
    """A07 decision B9 (8 Nov 2026): with the usage decision on, a passing
    calibration waits for a second Quality Manager. Each one is in their to-do
    list (never the recorder's), and the decision closes every to-do."""
    c.env["ir.config_parameter"].sudo().set_param(PARAM_DECISION, "1")
    e = eq(c)
    r = cal(c, e, user=c.qm)
    asked = _decision_todos(r).user_id
    assert c.qm2 in asked and c.qm not in asked and c.tech not in asked
    assert e.name in _decision_todos(r)[:1].note
    r.with_user(c.qm2).action_accept_calibration()
    assert not _decision_todos(r)
    # a failed calibration asks nobody: there is nothing to accept
    assert not _decision_todos(cal(c, eq(c), result="fail"))
    # a rejection closes them too
    r2 = cal(c, eq(c))
    assert _decision_todos(r2)
    r2.with_user(c.qm).write({"decision_note": "certificate not traceable"})
    r2.with_user(c.qm).action_reject_calibration()
    assert not _decision_todos(r2)


def test_b9_switch_off_asks_nobody_and_switching_on_asks_for_what_waits(c):
    e = eq(c)
    r = cal(c, e)
    assert not _decision_todos(r) and e.calibration_state == "current"
    c.env["ir.config_parameter"].sudo().set_param(PARAM_DECISION, "1")
    e.invalidate_recordset()
    assert e.calibration_state == "pending"
    assert c.env["fix.calibration"].action_ask_pending_decisions() >= 1
    assert {c.qm, c.qm2} <= set(_decision_todos(r).user_id)
    # asking again adds nobody twice
    before = len(_decision_todos(r))
    c.env["fix.calibration"].action_ask_pending_decisions()
    assert len(_decision_todos(r)) == before


def test_b9_both_switches_on_as_decided(c):
    """The live setting: only the roles record, and a second Quality Manager
    certifies. The technician records, a Quality Manager accepts."""
    ICP = c.env["ir.config_parameter"].sudo()
    ICP.set_param(PARAM_ROLE, "1")
    ICP.set_param(PARAM_DECISION, "1")
    e = eq(c)
    assert refused(c.env, lambda: cal(c, e, user=c.clerk), "Calibration Technician")
    r = cal(c, e, user=c.tech)
    assert e.calibration_state == "pending"
    with pytest.raises(UserError, match="usage decision"):
        e.with_user(c.clerk).action_assert_usable()
    assert c.qm in _decision_todos(r).user_id
    r.with_user(c.qm).action_accept_calibration()
    assert e.calibration_state == "current"
    assert e.with_user(c.clerk).action_assert_usable() is True


# ============================================================ profile + interval approval (BRU-EAM-13)
def test_profile_is_the_quality_managers_and_its_interval_changes_by_approval(c):
    e = eq(c)
    Profile = c.env["fix.calibration.profile"]
    assert refused(
        c.env,
        lambda: Profile.with_user(c.tech).create({"equipment_id": e.id, "interval_months": 12}),
    )
    profile = Profile.with_user(c.qm2).create({"equipment_id": e.id, "interval_months": 12})
    assert refused(c.env, lambda: profile.with_user(c.qm).write({"interval_months": 24}))
    assert refused(c.env, lambda: profile.with_user(c.tech).write({"required_traceability": "x"}))
    # the technician proposes; a Quality Manager other than the requester decides
    tech_profile = profile.with_user(c.tech)
    assert refused(c.env, lambda: tech_profile.action_request_approval(), "Propose")
    tech_profile.write({"proposed_interval_months": 18})
    assert refused(c.env, lambda: tech_profile.action_request_approval(), "stability history")
    tech_profile.write(
        {"interval_change_reason": "3 consecutive as-found passes, drift < 10% of band"}
    )
    tech_profile.action_request_approval()
    assert profile.approval_state == "pending"
    assert c.qm in assigned(profile) and c.tech not in assigned(profile)
    assert refused(c.env, lambda: tech_profile.write({"proposed_interval_months": 36}))
    assert refused(c.env, lambda: profile.with_user(c.qm).action_apply_interval_change(), "inbox")
    approve_via_inbox(profile, c.qm, requester=c.tech)
    assert (profile.interval_months, profile.approval_state) == (18, "approved")


def test_a_quality_manager_who_calibrated_the_instrument_does_not_approve_its_interval(c):
    e = eq(c)
    profile = (
        c.env["fix.calibration.profile"]
        .with_user(c.qm)
        .create({"equipment_id": e.id, "interval_months": 12})
    )
    cal(c, e, user=c.qm2)  # qm2 performed a calibration of it
    qm3 = _user(c.env, "qm3", [ROLE_QM])
    profile.with_user(c.tech).write(
        {"proposed_interval_months": 24, "interval_change_reason": "stable"}
    )
    profile.with_user(c.tech).action_request_approval()
    # the request never reaches whoever calibrated it, so it cannot stall in their inbox
    assert not inbox_task(profile, c.qm2)
    task = inbox_task(profile, qm3)
    assert task
    # one who calibrates it after the request was routed is refused at the decision
    cal(c, e, user=qm3)
    assert refused(c.env, lambda: task.with_user(qm3).action_approve(), "Segregation")
    assert profile.interval_months == 12
