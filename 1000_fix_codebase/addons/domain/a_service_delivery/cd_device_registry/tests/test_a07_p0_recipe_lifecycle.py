"""A07 P0 recipe (M17): guarded lifecycle fields, real transitions and routed
approvals, attacked as NON-ADMIN users on the live ORM (``odoo_env``:
fix_test, rolled back). Each refusal is paired with the proper path working.

A07 audit 2026-11-03, findings M17-3 (merge), M17-4 (custody), M17-8 (device
state), M17-10 (condition), M17-11 (components), M17-12 (PM): every state was
writable by a plain user, the creator merged his own candidate, custody events
were rewritten or future-dated, grades were born confirmed and PM never
re-scheduled.
"""

import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

TAG = "A7RC"
TIER_2 = "cd_entity_config.group_dofa_tier_2"
REFUSED = (UserError, ValidationError, AccessError, IntegrityError)


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


def refused(env, fn):
    """True when fn is refused (run in a savepoint and flushed)."""
    try:
        with env.cr.savepoint():
            fn()
            env.flush_all()
    except REFUSED:
        return True
    return False


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    brand = env["fix.brand"].create({"name": f"{TAG} Brand", "code": TAG})
    x = types.SimpleNamespace(env=env, seq=iter(range(1, 999)))
    x.model = env["fix.device.model"].create({"name": f"{TAG} Phone", "brand_id": brand.id})
    x.model2 = env["fix.device.model"].create({"name": f"{TAG} Tablet", "brand_id": brand.id})
    x.clerk = _user(env, f"{TAG.lower()}_clerk")
    x.clerk2 = _user(env, f"{TAG.lower()}_clerk2")
    x.manager = _user(env, f"{TAG.lower()}_mgr", [TIER_2])
    x.manager2 = _user(env, f"{TAG.lower()}_mgr2", [TIER_2])
    x.owner = env["res.partner"].create({"name": f"{TAG} Owner"})
    x.other = env["res.partner"].create({"name": f"{TAG} Other"})
    x.today = fields.Date.context_today(env["fix.device"])
    return x


def dev(c, **kw):
    vals = {
        "device_model_id": c.model.id,
        "serial_number": "%s-SN-%03d" % (TAG, next(c.seq)),
        "owner_id": c.owner.id,
    }
    vals.update(kw)
    return c.env["fix.device"].create(vals)


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()

    def ep(name):
        f = getattr(g.P03GenericApiController, name)
        return getattr(f, "original_endpoint", f)

    req = types.SimpleNamespace(env=c.env(user=c.clerk.id))
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)
    g.request = req
    s.request = req
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: ep("model_write")(ctl, **kw),
            action=lambda **kw: ep("model_action")(ctl, **kw),
        )
    finally:
        g.request, s.request = old_g, old_s


# ============================================================ device state
def test_device_state_and_archive_are_not_writable(c, p03):
    d = dev(c).with_user(c.clerk)
    for vals in ({"state": "scrapped"}, {"state": "lost"}, {"state": "transferred"}):
        assert refused(c.env, lambda v=vals: d.write(v)), vals
    assert refused(c.env, lambda: d.write({"active": False}))
    assert refused(
        c.env,
        lambda: (
            c.env["fix.device"]
            .with_user(c.clerk)
            .create(
                {"device_model_id": c.model.id, "serial_number": f"{TAG}-BORN", "state": "lost"}
            )
        ),
    )
    out = p03.write(model="fix.device", record_id=d.id, values={"state": "scrapped"})
    assert "error" in out and d.state == "registered" and d.active
    # an unchanged echo (the form posts every field) is still accepted
    d.write({"state": "registered", "purchase_channel": "online"})
    assert d.purchase_channel == "online"


def test_lost_flag_stamps_who_and_when_and_another_user_clears(c, p03):
    d = dev(c)
    d.action_transfer_ownership(c.other.id)  # state 'transferred': restored on clear
    as_clerk = d.with_user(c.clerk)
    with pytest.raises(UserError, match="reported"), c.env.cr.savepoint():
        as_clerk.action_mark_lost("  ")
    out = p03.action(
        model="fix.device", ids=[d.id], method="action_mark_lost", kwargs={"reason": "FIR 12/26"}
    )
    assert out["success"], out
    assert (d.state, d.lost_flagged_by_id, d.lost_reason) == ("lost", c.clerk, "FIR 12/26")
    assert d.lost_flagged_at and d.lost_prior_state == "transferred"
    with pytest.raises(UserError, match="already"), c.env.cr.savepoint():
        as_clerk.action_mark_lost("again")
    # BRU-AST-09: a lost device is not handed on (E1 still holds)
    with pytest.raises(UserError, match="cannot change owner"), c.env.cr.savepoint():
        as_clerk.action_transfer_ownership(c.owner.id)
    # SoD: the flagger never clears his own flag
    with pytest.raises(UserError, match="Segregation"), c.env.cr.savepoint():
        as_clerk.action_clear_lost("found it")
    d.with_user(c.clerk2).action_clear_lost("recovered at Uttara branch")
    assert (d.state, d.lost_cleared_by_id) == ("transferred", c.clerk2)
    with pytest.raises(UserError, match="flagged lost"), c.env.cr.savepoint():
        d.with_user(c.clerk2).action_clear_lost("twice")


def test_scrap_is_routed_to_tier2_and_never_self_approved(c):
    d = dev(c)
    as_clerk = d.with_user(c.clerk)
    # the apply method cannot be pressed, not even by a Tier 2 holder
    for user in (c.clerk, c.manager):
        with pytest.raises(UserError, match="approver's inbox"), c.env.cr.savepoint():
            d.with_user(user).action_scrap()
    with pytest.raises(UserError, match="scrapped"), c.env.cr.savepoint():
        as_clerk.action_request_approval()
    # a Tier 2 requester is excluded from his own request
    d.with_user(c.manager).action_request_approval(justification="board burnt, BER")
    assert d.approval_state == "pending"
    assert not inbox_task(d, c.manager)
    assert inbox_task(d, c.manager2)
    task = approve_via_inbox(d, c.manager2, requester=c.manager)
    assert task.decision == "approved"
    assert (d.state, d.scrapped_by_id, d.approval_state) == ("scrapped", c.manager2, "approved")
    with (
        pytest.raises(UserError, match="cannot be scrapped|needs no approval"),
        c.env.cr.savepoint(),
    ):
        as_clerk.action_request_approval(justification="again")
    # a lost device is not scrapped
    lost = dev(c)
    lost.with_user(c.clerk).action_mark_lost("stolen")
    with pytest.raises(UserError, match="cannot be scrapped"), c.env.cr.savepoint():
        lost.with_user(c.clerk2).action_request_approval(justification="write it off")


def test_a_pending_scrap_is_voided_by_an_ownership_transfer(c):
    d = dev(c)
    d.with_user(c.clerk).action_request_approval(justification="customer abandoned it")
    assert d.approval_state == "pending"
    d.with_user(c.clerk).action_transfer_ownership(c.other.id)
    assert d.approval_state == "none" and d.approval_request_id.state == "voided"
    assert d.state == "transferred"


# ============================================================ identity merge
def _ident(c, primary, dup, user, **kw):
    vals = {
        "primary_device_id": primary.id,
        "duplicate_device_id": dup.id,
        "match_reason": "same IMEI on the label",
    }
    vals.update(kw)
    return c.env["fix.device.identity"].with_user(user).create(vals)


def test_identity_cannot_be_born_or_set_merged(c, p03):
    p, d = dev(c), dev(c)
    for state in ("merged", "rejected"):
        assert refused(c.env, lambda s=state: _ident(c, p, d, c.clerk, state=s))
    r = _ident(c, p, d, c.clerk)
    for vals in ({"state": "merged"}, {"state": "rejected"}, {"resolved_on": c.today}):
        assert refused(c.env, lambda v=vals: r.with_user(c.clerk2).write(v)), vals
    out = p03.write(
        model="fix.device.identity",
        values={
            "primary_device_id": p.id,
            "duplicate_device_id": d.id,
            "match_reason": "p03",
            "state": "merged",
        },
    )
    born = c.env["fix.device.identity"].browse(out.get("id") or 0)
    assert "error" in out or born.state == "candidate"
    out = p03.write(model="fix.device.identity", record_id=r.id, values={"state": "merged"})
    assert "error" in out and r.state == "candidate" and d.active


def test_merge_is_routed_and_the_creator_never_approves(c):
    p, d = dev(c), dev(c)
    r = _ident(c, p, d, c.manager)  # a Tier 2 holder raises the candidate
    for user in (c.manager, c.clerk):
        with pytest.raises(UserError, match="approver's inbox"), c.env.cr.savepoint():
            r.with_user(user).action_merge()
    r.with_user(c.clerk).action_request_approval(justification="same IMEI")
    # neither the creator nor the requester is routed the decision
    assert not inbox_task(r, c.manager)
    approve_via_inbox(r, c.manager2, requester=c.clerk)
    assert (r.state, r.resolved_by_id, r.approval_state) == ("merged", c.manager2, "approved")
    assert not d.active and p.active
    # a merged resolution is final: not re-decided, not re-pointed, not undone
    with pytest.raises(UserError, match="candidate"), c.env.cr.savepoint():
        r.with_user(c.clerk).action_reject()
    assert refused(c.env, lambda: r.with_user(c.clerk).write({"state": "candidate"}))
    assert refused(c.env, lambda: r.with_user(c.clerk).write({"primary_device_id": d.id}))
    assert refused(c.env, lambda: d.with_user(c.clerk).write({"active": True}))


def test_a_changed_pair_voids_the_pending_merge(c):
    p, d, e = dev(c), dev(c), dev(c)
    r = _ident(c, p, d, c.clerk)
    r.with_user(c.clerk).action_request_approval()
    r.with_user(c.clerk).write({"duplicate_device_id": e.id})
    assert r.approval_state == "none" and r.approval_request_id.state == "voided"


def test_merge_of_different_owners_or_models_needs_a_justification(c):
    p = dev(c)
    d = dev(c, owner_id=c.other.id, device_model_id=c.model2.id)
    r = _ident(c, p, d, c.clerk)
    with pytest.raises(UserError, match="different owners and models"), c.env.cr.savepoint():
        r.with_user(c.clerk).action_request_approval()
    with pytest.raises(UserError, match="itself"), c.env.cr.savepoint():
        _ident(c, p, p, c.clerk).with_user(c.clerk).action_request_approval(justification="x")
    approve_via_inbox(
        r,
        c.manager,
        requester=c.clerk,
        justification="owner bought it second-hand; intake keyed the wrong model",
    )
    assert r.state == "merged" and not d.active


def test_reject_only_from_candidate_and_withdraws_the_request(c):
    p, d = dev(c), dev(c)
    r = _ident(c, p, d, c.clerk)
    r.with_user(c.clerk).action_request_approval()
    r.with_user(c.clerk2).action_reject()
    assert (r.state, r.resolved_by_id) == ("rejected", c.clerk2)
    assert r.approval_request_id.state == "voided" and d.active
    with pytest.raises(UserError, match="candidate"), c.env.cr.savepoint():
        r.with_user(c.clerk2).action_reject()
    assert refused(c.env, lambda: r.with_user(c.clerk).write({"match_reason": "rewritten"}))


# ============================================================ custody chain
def test_custody_events_are_insert_only_and_never_future(c, p03):
    d = dev(c)
    Custody = c.env["fix.device.custody"].with_user(c.clerk)
    ev = Custody.create({"device_id": d.id, "event": "lost", "from_party_id": c.owner.id})
    as_clerk2 = ev.with_user(c.clerk2)
    for vals in (
        {"event": "found"},
        {"to_party_id": c.other.id},
        {"event_date": c.today - timedelta(days=90)},
    ):
        assert refused(c.env, lambda v=vals: as_clerk2.write(v)), vals
    assert refused(c.env, lambda: ev.with_user(c.clerk).unlink())
    out = p03.write(model="fix.device.custody", record_id=ev.id, values={"event": "found"})
    assert "error" in out and ev.event == "lost"
    as_clerk2.write({"event": "lost"})  # an unchanged echo is no edit
    with pytest.raises(ValidationError, match="future"), c.env.cr.savepoint():
        Custody.create({"device_id": d.id, "event": "found", "event_date": c.today + timedelta(1)})
    found = Custody.create({"device_id": d.id, "event": "found", "event_date": c.today})
    assert found.event_date == c.today


# ============================================================ condition grade
def test_condition_grade_confirmed_by_another_user_then_frozen(c, p03):
    d = dev(c)
    Cond = c.env["fix.device.condition"].with_user(c.clerk)
    assert refused(c.env, lambda: Cond.create({"device_id": d.id, "state": "confirmed"}))
    out = p03.write(
        model="fix.device.condition", values={"device_id": d.id, "grade": "a", "state": "confirmed"}
    )
    born = c.env["fix.device.condition"].browse(out.get("id") or 0)
    assert "error" in out or born.state == "draft"
    g = Cond.create({"device_id": d.id, "grade": "d", "battery_health_pct": 40})
    assert refused(c.env, lambda: g.write({"state": "confirmed"}))
    with pytest.raises(UserError, match="Segregation"), c.env.cr.savepoint():
        g.action_confirm()
    g.with_user(c.clerk2).action_confirm()
    assert (g.state, g.confirmed_by_id) == ("confirmed", c.clerk2) and g.confirmed_at
    for vals in ({"grade": "a"}, {"battery_health_pct": 100}, {"state": "draft"}):
        assert refused(c.env, lambda v=vals: g.with_user(c.clerk2).write(v)), vals
    out = p03.write(model="fix.device.condition", record_id=g.id, values={"grade": "a"})
    assert "error" in out and g.grade == "d"
    with pytest.raises(UserError, match="draft"), c.env.cr.savepoint():
        g.with_user(c.manager).action_confirm()


# ============================================================ components
def test_component_state_guarded_and_serial_installed_once(c, p03):
    d1, d2 = dev(c), dev(c)
    Comp = c.env["fix.device.component"].with_user(c.clerk)
    k = Comp.create({"device_id": d1.id, "part_name": "Battery", "serial_no": f"{TAG}-BAT-1"})
    assert refused(c.env, lambda: k.with_user(c.clerk2).write({"state": "removed"}))
    assert refused(
        c.env,
        lambda: Comp.create(
            {
                "device_id": d2.id,
                "part_name": "Battery",
                "serial_no": f"{TAG}-BAT-2",
                "state": "removed",
            }
        ),
    )
    # the same serial (any case / padding) is not installed in a second device
    with pytest.raises(ValidationError, match="already installed"), c.env.cr.savepoint():
        Comp.create(
            {"device_id": d2.id, "part_name": "Battery", "serial_no": f" {TAG.lower()}-bat-1 "}
        )
    k.action_remove()
    assert k.state == "removed" and k.removed_on == fields.Date.context_today(k)
    # a removed installation is history: not re-installed, not re-dated
    for vals in (
        {"state": "installed", "removed_on": False},
        {"installed_on": c.today + timedelta(days=10)},
    ):
        assert refused(c.env, lambda v=vals: k.with_user(c.clerk2).write(v)), vals
    out = p03.write(model="fix.device.component", record_id=k.id, values={"state": "installed"})
    assert "error" in out and k.state == "removed"
    moved = Comp.create({"device_id": d2.id, "part_name": "Battery", "serial_no": f"{TAG}-BAT-1"})
    assert moved.state == "installed"


# ============================================================ PM plans
def test_pm_done_rolls_next_due_on_and_state_is_guarded(c):
    d = dev(c)
    Pm = c.env["fix.device.pm"].with_user(c.clerk)
    pm = Pm.create(
        {"device_id": d.id, "next_due": c.today - timedelta(days=5), "interval_months": 3}
    )
    assert refused(c.env, lambda: pm.write({"state": "paused"}))
    assert refused(c.env, lambda: pm.write({"last_done": c.today}))
    due = pm.next_due
    pm.action_complete()
    assert pm.last_done == c.today
    assert pm.next_due == due + _months(3) and pm.next_due > c.today
    # far overdue: rolled by whole intervals until it lies after today
    late = Pm.create(
        {"device_id": d.id, "next_due": c.today - timedelta(days=400), "interval_months": 6}
    )
    late.action_complete()
    assert c.today < late.next_due <= c.today + _months(6)
    pm.action_pause()
    with pytest.raises(UserError, match="Resume"), c.env.cr.savepoint():
        pm.action_complete()
    pm.action_resume()
    assert pm.state == "active"


def _months(n):
    from dateutil.relativedelta import relativedelta

    return relativedelta(months=n)
