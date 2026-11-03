"""A07 P0 recipe (M46 Fleet & Vehicles): guarded workflow fields, real
transitions, evidence before completion and the routed accident-settlement
approval, attacked as NON-ADMIN users on the live ORM (``odoo_env``: rolled
back). Each refusal is paired with the proper path working.

A07 audit 2026-11-03 (working/A07_evidence/module_findings/M46.md):
- M46-5  document state typed, born valid with no end date;
- M46-6  any employee suspended or reinstated a driver by write, no reason;
- M46-7  the pre-use check passed by default and was rewritten afterwards;
- M46-8  the user who took a van off the road returned it, with no re-check;
- M46-9  no fuel exception rules, no review, amounts edited by anyone;
- M46-10 claim with no reference, the reporter closed it, no settlement;
- M46-13 PM done forged by write, with no odometer and a negative cost.
"""

import types
from datetime import timedelta

import pytest
from odoo.addons.cd_vehicle_ext.models.fix_vehicle_ops import (
    TANK_CAPACITY_PARAM,
    dhaka_today,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import Error as PgError

TAG = "A7FR"
TIER_2 = "cd_entity_config.group_dofa_tier_2"
REFUSED = (UserError, ValidationError, AccessError, PgError)


def refused(env, fn):
    """The refusal text, or None when fn() went through (rolled back to a
    savepoint either way)."""
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED as exc:
        return str(exc) or exc.__class__.__name__
    return None


def _user(env, login, groups=()):
    ou = env["operating.unit"].search([], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = dhaka_today(env["fix.vehicle.check"])
    x.clerk = _user(env, f"{TAG.lower()}_clerk")
    x.clerk2 = _user(env, f"{TAG.lower()}_clerk2")
    x.approver = _user(env, f"{TAG.lower()}_appr", [TIER_2])
    brand = env["fleet.vehicle.model.brand"].create({"name": f"{TAG} Brand"})
    model = env["fleet.vehicle.model"].create({"name": f"{TAG} Van", "brand_id": brand.id})
    x.van = env["fleet.vehicle"].create({"model_id": model.id, "license_plate": f"{TAG}-1"})
    x.van2 = env["fleet.vehicle"].create({"model_id": model.id, "license_plate": f"{TAG}-2"})
    emp = env["hr.employee"].create({"name": f"{TAG} Driver"})
    x.driver = env["fix.driver"].create(
        {
            "name": f"{TAG} Driver",
            "employee_id": emp.id,
            "license_no": f"DL-{TAG}",
            "license_expiry": x.today + timedelta(days=300),
        }
    )
    return x


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()

    def ep(name):
        f = getattr(g.P03GenericApiController, name)
        return getattr(f, "original_endpoint", f)

    old = getattr(g, "request", None)

    def call(name, user, **kw):
        g.request = types.SimpleNamespace(env=c.env(user=user.id))
        return ep(name)(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            write=lambda user, **kw: call("model_write", user, **kw),
            action=lambda user, **kw: call("model_action", user, **kw),
        )
    finally:
        g.request = old


def ok_check(c, vehicle, user=None, **kw):
    vals = {
        "vehicle_id": vehicle.id,
        "tyres_ok": True,
        "lights_ok": True,
        "fluids_ok": True,
        "brakes_ok": True,
    }
    vals.update(kw)
    return c.env["fix.vehicle.check"].with_user(user or c.clerk).create(vals)


def fill(c, odometer, litres=40.0, amount=4500.0, user=None, vehicle=None, **kw):
    vals = {
        "vehicle_id": (vehicle or c.van).id,
        "driver_id": c.driver.id,
        "odometer": odometer,
        "litres": litres,
        "amount": amount,
    }
    vals.update(kw)
    return c.env["fix.vehicle.fuel"].with_user(user or c.clerk).create(vals)


def offroad(c, user=None, vehicle=None):
    return (
        c.env["fix.vehicle.offroad"]
        .with_user(user or c.clerk)
        .create({"vehicle_id": (vehicle or c.van).id, "reason": "Brake failure"})
    )


def accident(c, user=None, **kw):
    vals = {"vehicle_id": c.van.id, "description": "Side collision", "damage_cost": 50000}
    vals.update(kw)
    return c.env["fix.vehicle.accident"].with_user(user or c.clerk).create(vals)


# ================================================== guarded fields (D1)
def _targets(c):
    """(record as clerk2, field, forged value) for every guarded field."""
    off = offroad(c)
    chk = ok_check(c, c.van)
    pm = c.env["fix.vehicle.pm"].with_user(c.clerk).create({"vehicle_id": c.van.id})
    fuel_rec = fill(c, 10000)
    acc = accident(c)
    doc = (
        c.env["fix.vehicle.document"]
        .with_user(c.clerk)
        .create({"vehicle_id": c.van.id, "doc_type": "fitness", "valid_to": c.today})
    )
    u = c.clerk2
    return [
        (c.driver.with_user(u), "state", "suspended"),
        (c.driver.with_user(u), "suspended_by_id", c.clerk.id),
        (doc.with_user(u), "state", "expired"),
        (off.with_user(u), "state", "returned"),
        (off.with_user(u), "ended_on", c.today),
        (off.with_user(u), "returned_by_id", u.id),
        (off.with_user(u), "return_check_id", chk.id),
        (pm.with_user(u), "state", "done"),
        (pm.with_user(u), "done_on", c.today),
        (fuel_rec.with_user(u), "review_state", "cleared"),
        (fuel_rec.with_user(u), "exception_flags", "duplicate"),
        (fuel_rec.with_user(u), "reviewed_by_id", u.id),
        (acc.with_user(u), "state", "closed"),
        (acc.with_user(u), "closed_by_id", u.id),
        (acc.with_user(u), "dofa_approved", True),
        (acc.with_user(u), "approval_state", "approved"),
    ]


def test_guarded_fields_refuse_direct_write(c):
    for rec, name, value in _targets(c):
        assert refused(c.env, lambda r=rec, n=name, v=value: r.write({n: v})), (
            "%s.%s was written directly" % (rec._name, name)
        )


def test_guarded_fields_refuse_p03_model_write(c, p03):
    for rec, name, value in _targets(c):
        before = rec.sudo()[name]
        res = p03.write(c.clerk2, model=rec._name, record_id=rec.id, values={name: value})
        rec.invalidate_recordset()
        assert "error" in res, "%s.%s accepted over /p03/model/write: %s" % (rec._name, name, res)
        assert rec.sudo()[name] == before


def test_create_cannot_set_a_non_default_state(c):
    emp = c.env["hr.employee"].create({"name": f"{TAG} Emp2"})
    U = c.clerk
    attempts = [
        lambda: (
            c.env["fix.driver"]
            .with_user(U)
            .create({"name": "x", "employee_id": emp.id, "license_no": "x", "state": "suspended"})
        ),
        lambda: (
            c.env["fix.vehicle.offroad"]
            .with_user(U)
            .create({"vehicle_id": c.van.id, "reason": "x", "state": "returned"})
        ),
        lambda: (
            c.env["fix.vehicle.pm"].with_user(U).create({"vehicle_id": c.van.id, "state": "done"})
        ),
        lambda: fill(c, 10000, review_state="cleared"),
        lambda: accident(c, state="closed"),
    ]
    for fn in attempts:
        assert refused(c.env, fn)


# ================================================== drivers (M46-6)
def test_suspension_and_reinstatement_need_reason_and_second_person(c):
    d = c.driver.with_user(c.clerk)
    assert "reason" in refused(c.env, lambda: d.action_suspend())
    assert "Reinstate a suspended driver" in refused(
        c.env, lambda: d.action_reinstate(reason="fine")
    )
    d.action_suspend(reason="Speeding complaint")
    assert c.driver.state == "suspended" and c.driver.suspended_by_id == c.clerk
    assert "Segregation of duties" in refused(c.env, lambda: d.action_reinstate(reason="ok"))
    d2 = c.driver.with_user(c.clerk2)
    assert "reason" in refused(c.env, lambda: d2.action_reinstate())
    d2.action_reinstate(reason="Coaching completed")
    assert c.driver.state == "active" and not c.driver.suspended_by_id
    bodies = " ".join(c.driver.message_ids.mapped("body"))
    assert "Speeding complaint" in bodies and "Coaching completed" in bodies


def test_reinstatement_refused_while_licence_expired(c):
    c.driver.with_user(c.clerk).action_suspend(reason="Licence lapsed")
    c.driver.license_expiry = c.today - timedelta(days=1)
    d2 = c.driver.with_user(c.clerk2)
    assert "licence" in refused(c.env, lambda: d2.action_reinstate(reason="back"))
    c.driver.license_expiry = False
    assert "licence" in refused(c.env, lambda: d2.action_reinstate(reason="back"))
    c.driver.license_expiry = c.today + timedelta(days=365)
    d2.action_reinstate(reason="Licence renewed")
    assert c.driver.state == "active"


# ================================================== documents (M46-5)
def test_new_document_without_end_date_is_not_valid(c, p03):
    Doc = c.env["fix.vehicle.document"].with_user(c.clerk)
    nodate = Doc.create({"vehicle_id": c.van.id, "doc_type": "insurance"})
    assert nodate.state == "expired" and not nodate.is_valid
    assert "end date" in refused(
        c.env,
        lambda: Doc.create({"vehicle_id": c.van.id, "doc_type": "tax", "state": "valid"}),
    )
    past = Doc.create(
        {"vehicle_id": c.van.id, "doc_type": "tax", "valid_to": c.today - timedelta(days=1)}
    )
    assert past.state == "expired"
    # the proper path: a dated document is valid, and the P03 form creates it
    good = Doc.create(
        {"vehicle_id": c.van.id, "doc_type": "tax", "valid_to": c.today + timedelta(days=90)}
    )
    assert good.state == "valid" and good.is_valid
    res = p03.write(
        c.clerk,
        model="fix.vehicle.document",
        values={
            "vehicle_id": c.van.id,
            "doc_type": "fitness",
            "valid_to": str(c.today + timedelta(days=30)),
            "state": "valid",
        },
    )
    assert "error" not in res, res
    # marking it expired is the one-way action
    good.with_user(c.clerk2).action_expire()
    assert good.state == "expired"
    assert refused(c.env, lambda: good.with_user(c.clerk2).action_expire())


# ================================================== pre-use check (M46-7)
def test_untouched_check_fails_and_answered_check_passes(c):
    empty = c.env["fix.vehicle.check"].with_user(c.clerk).create({"vehicle_id": c.van.id})
    assert not empty.passed
    assert not ok_check(c, c.van, brakes_ok=False).passed
    assert ok_check(c, c.van).passed


def test_saved_check_is_never_rewritten(c, p03):
    chk = ok_check(c, c.van, brakes_ok=False, defects="Brakes soft")
    for user in (c.clerk, c.clerk2):
        assert refused(c.env, lambda u=user: chk.with_user(u).write({"brakes_ok": True}))
        assert refused(c.env, lambda u=user: chk.with_user(u).write({"defects": False}))
    res = p03.write(
        c.clerk2, model="fix.vehicle.check", record_id=chk.id, values={"brakes_ok": True}
    )
    chk.invalidate_recordset()
    assert "error" in res and not chk.passed
    # the form may echo the unchanged values back
    chk.with_user(c.clerk).write({"brakes_ok": False, "defects": "Brakes soft"})
    # a new check is created through the form
    res = p03.write(
        c.clerk,
        model="fix.vehicle.check",
        values={
            "vehicle_id": c.van.id,
            "tyres_ok": True,
            "lights_ok": True,
            "fluids_ok": True,
            "brakes_ok": True,
        },
    )
    assert "error" not in res, res


# ================================================== off-road (M46-8)
def test_return_to_service_needs_recheck_and_second_person(c, p03):
    off = offroad(c)
    assert "Segregation of duties" in refused(c.env, lambda: off.with_user(c.clerk).action_return())
    off2 = off.with_user(c.clerk2)
    assert "pre-use check" in refused(c.env, lambda: off2.action_return())
    ok_check(c, c.van, brakes_ok=False)  # a failed re-check does not clear it
    assert "pre-use check" in refused(c.env, lambda: off2.action_return())
    ok_check(c, c.van, checked_on=c.today - timedelta(days=1))  # before the off-road start
    assert "pre-use check" in refused(c.env, lambda: off2.action_return())
    ok_check(c, c.van2)  # another vehicle's check
    assert "pre-use check" in refused(c.env, lambda: off2.action_return())
    # P03 action path, then the proper path
    res = p03.action(c.clerk, model="fix.vehicle.offroad", ids=[off.id], method="action_return")
    assert not res["success"]
    recheck = ok_check(c, c.van)  # the re-check may be the opener's own
    res = p03.action(c.clerk2, model="fix.vehicle.offroad", ids=[off.id], method="action_return")
    assert res["success"], res
    off.invalidate_recordset()
    assert off.state == "returned" and off.ended_on and off.return_check_id == recheck
    assert off.returned_by_id == c.clerk2
    assert refused(c.env, lambda: off2.action_return())
    # a returned record is history
    assert refused(c.env, lambda: off.with_user(c.clerk).write({"reason": "Nothing"}))


def test_check_recorded_before_the_offroad_record_does_not_clear_it(c):
    early = ok_check(c, c.van)
    off = offroad(c)
    c.env.flush_all()
    # the check was saved an hour before the vehicle went off the road
    c.env.cr.execute(
        "UPDATE fix_vehicle_check SET create_date = create_date - interval '1 hour' WHERE id = %s",
        (early.id,),
    )
    c.env.invalidate_all()
    assert "pre-use check" in refused(c.env, lambda: off.with_user(c.clerk2).action_return())


# ================================================== PM (M46-13)
def test_pm_done_needs_odometer_and_non_negative_cost(c):
    pm = c.env["fix.vehicle.pm"].with_user(c.clerk).create({"vehicle_id": c.van.id})
    assert "odometer" in refused(c.env, lambda: pm.action_done())
    assert refused(c.env, lambda: pm.write({"cost": -20000}))
    pm.write({"odometer": 12000, "cost": 0})  # a warranty service costs nothing
    pm.action_done()
    assert pm.state == "done" and pm.done_on
    assert "Complete an open PM" in refused(c.env, lambda: pm.action_done())
    assert refused(c.env, lambda: pm.with_user(c.clerk2).write({"cost": 99999}))
    assert refused(c.env, lambda: pm.write({"odometer": 1}))
    pm.write({"notes": "Oil and filter"})  # notes stay editable


# ================================================== fuel (M46-9)
def test_fill_needs_driver_and_amount_and_no_negative_amount(c):
    assert "driver" in refused(c.env, lambda: fill(c, 10000, driver_id=False))
    assert "amount" in refused(c.env, lambda: fill(c, 10000, amount=0))
    assert refused(c.env, lambda: fill(c, 10000, amount=-50000))
    f = fill(c, 10000)
    assert f.review_state == "none" and not f.exception_flags
    assert refused(c.env, lambda: f.write({"driver_id": False}))
    # superuser data loading is trusted, but a negative amount is refused outright
    assert refused(c.env, lambda: f.sudo().write({"amount": -1}))


@pytest.mark.parametrize("rule", ["odometer_back", "over_capacity", "duplicate", "offroad"])
def test_exception_rules_hold_the_fill(c, rule):
    fill(c, 12000)
    if rule == "odometer_back":
        f = fill(c, 9000, litres=35)
    elif rule == "over_capacity":
        f = fill(c, 12500, litres=5000, amount=600000)
    elif rule == "duplicate":
        f = fill(c, 12000, user=c.clerk2)
    else:
        offroad(c)
        f = fill(c, 12500, litres=30)
    assert f.review_state == "held", f.exception_flags
    assert f.exception_flags.split(",") == [rule]
    assert f.exception_summary


def test_tank_capacity_is_a_parameter(c):
    c.env["ir.config_parameter"].sudo().set_param(TANK_CAPACITY_PARAM, "50")
    assert fill(c, 10000, litres=60).exception_flags == "over_capacity"
    assert fill(c, 10600, litres=45).review_state == "none"


def test_held_fill_is_reviewed_by_someone_other_than_the_recorder(c, p03):
    fill(c, 12000)
    f = fill(c, 9000, litres=35)
    assert "Segregation of duties" in refused(
        c.env, lambda: f.action_clear_exception(note="looks fine")
    )
    res = p03.action(
        c.clerk,
        model="fix.vehicle.fuel",
        ids=[f.id],
        method="action_clear_exception",
        kwargs={"note": "self"},
    )
    assert not res["success"]
    assert "reason" in refused(c.env, lambda: f.with_user(c.clerk2).action_clear_exception())
    # the recorder's correction does not release the hold
    f.write({"odometer": 12400})
    assert f.review_state == "held" and not f.exception_flags
    res = p03.action(
        c.clerk2,
        model="fix.vehicle.fuel",
        ids=[f.id],
        method="action_clear_exception",
        kwargs={"note": "Receipt and trip log match"},
    )
    assert res["success"], res
    f.invalidate_recordset()
    assert f.review_state == "cleared" and f.reviewed_by_id == c.clerk2
    # reviewed figures are locked, for the recorder too
    for vals in ({"amount": 99999}, {"litres": 80}):
        assert refused(c.env, lambda v=vals: f.write(v))
    assert refused(c.env, lambda: f.with_user(c.clerk2).action_clear_exception(note="again"))


def test_only_the_recorder_corrects_an_unreviewed_fill(c, p03):
    f = fill(c, 12000)
    assert refused(c.env, lambda: f.with_user(c.clerk2).write({"amount": 99999}))
    res = p03.write(c.clerk2, model="fix.vehicle.fuel", record_id=f.id, values={"amount": 99999})
    f.invalidate_recordset()
    assert "error" in res and f.amount == 4500
    f.write({"amount": 4600})  # the recorder corrects their own fill
    assert f.amount == 4600 and f.review_state == "none"
    f.write({"litres": 400})  # ...and the correction is re-checked
    assert f.review_state == "held" and "over_capacity" in f.exception_flags


def test_rejected_fill_is_not_the_previous_reading(c):
    fill(c, 10000)
    bad = fill(c, 99000, litres=30)  # a typo odometer, not flagged on its own
    bad.write({"litres": 3000})  # ...made implausible, so it is held
    assert bad.review_state == "held"
    assert "reason" in refused(c.env, lambda: bad.with_user(c.clerk2).action_reject_fill())
    bad.with_user(c.clerk2).action_reject_fill(reason="Odometer typo, wrong litres")
    assert bad.review_state == "rejected"
    nxt = fill(c, 10500, litres=38)
    assert nxt.review_state == "none", nxt.exception_flags


# ================================================== accidents (M46-10)
def test_claim_needs_a_reference(c):
    a = accident(c)
    assert "claim reference" in refused(c.env, lambda: a.action_claim())
    a.action_claim(claim_ref="  INS-2026-001 ")
    assert a.state == "claimed" and a.claim_ref == "INS-2026-001"
    assert "File a claim" in refused(c.env, lambda: a.action_claim(claim_ref="X"))
    assert refused(c.env, lambda: a.write({"claim_ref": "INS-OTHER"}))
    # a reference already on the record is used
    b = accident(c, claim_ref="INS-2026-002")
    b.action_claim()
    assert b.claim_ref == "INS-2026-002"


def test_close_needs_settlement_and_a_closer_who_is_not_the_reporter(c, p03):
    a = accident(c, claim_ref="INS-1")
    a.action_claim()
    assert "settled amount" in refused(c.env, lambda: a.with_user(c.clerk2).action_close())
    assert "Segregation of duties" in refused(c.env, lambda: a.action_close(settlement="0"))
    res = p03.action(
        c.clerk,
        model="fix.vehicle.accident",
        ids=[a.id],
        method="action_close",
        kwargs={"settlement": "0"},
    )
    assert not res["success"]
    # a declined claim (nothing settled) closes without an approval
    res = p03.action(
        c.clerk2,
        model="fix.vehicle.accident",
        ids=[a.id],
        method="action_close",
        kwargs={"settlement": "0"},
    )
    assert res["success"], res
    a.invalidate_recordset()
    assert a.state == "closed" and a.closed_by_id == c.clerk2
    for vals in ({"damage_cost": 1}, {"settlement_amount": 5}, {"description": "x"}):
        assert refused(c.env, lambda v=vals: a.with_user(c.clerk).write(v))
    assert "Close a claimed accident" in refused(
        c.env, lambda: a.with_user(c.clerk2).action_close(settlement="0")
    )


def test_settlement_above_tier_0_is_routed_and_pinned(c):
    a = accident(c, claim_ref="INS-2")
    assert "filed claim" in refused(c.env, lambda: a.action_request_approval(justification="early"))
    a.action_claim()
    a.write({"settlement_amount": 40000})
    assert a.dofa_tier_required == "tier_2"
    a2 = a.with_user(c.clerk2)
    assert "DOFA" in refused(c.env, lambda: a2.action_close(settlement="40000"))
    # a direct press of the approve button is refused: it comes from the inbox
    assert refused(c.env, lambda: a.with_user(c.approver).action_dofa_approve())
    approve_via_inbox(
        a, c.approver, requester=c.clerk2, justification="Insurer offer per assessor report"
    )
    assert a.dofa_approved and a.dofa_approved_amount == 40000
    # changing the approved figure, either way, withdraws the approval
    a.write({"settlement_amount": 35000})
    assert not a.dofa_approved
    assert "DOFA" in refused(c.env, lambda: a2.action_close(settlement="35000"))
    approve_via_inbox(a, c.approver, requester=c.clerk2, justification="Revised offer")
    assert "DOFA" in refused(c.env, lambda: a2.action_close(settlement="45000"))
    a2.action_close(settlement="35000")
    assert a.state == "closed" and a.closed_by_id == c.clerk2


def test_settlement_is_never_routed_to_its_reporter(c):
    """The engine never routes a record to its creator, requester or the
    person who set the amount, even when they hold the tier."""
    reporter = _user(c.env, f"{TAG.lower()}_rep", [TIER_2])
    a = accident(c, user=reporter, claim_ref="INS-3")
    a.action_claim()
    a.write({"settlement_amount": 10000})
    a.with_user(c.clerk2).action_request_approval(justification="Assessor report attached")
    assigned = a.sudo().approval_request_id.task_ids.mapped("assigned_user_id")
    assert c.approver in assigned
    assert not ({reporter, c.clerk2} & set(assigned))
    with pytest.raises(AssertionError, match="received no inbox task"):
        approve_via_inbox(a, reporter)
    assert refused(c.env, lambda: a.action_dofa_approve())
    approve_via_inbox(a, c.approver)
    assert a.dofa_approved
    # ...and the reporter still cannot close it
    assert "Segregation of duties" in refused(c.env, lambda: a.action_close(settlement="10000"))
    a.with_user(c.clerk2).action_close(settlement="10000")
    assert a.state == "closed"
