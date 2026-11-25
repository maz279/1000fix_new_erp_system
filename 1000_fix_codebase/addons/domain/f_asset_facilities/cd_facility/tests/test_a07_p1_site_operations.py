"""A07 P1/P2 (M47): utilities anomaly hold and review, safety inspection
interval, incident -> HSE hand-off with the s.80 clock, PM recurrence, and
the P03 wiring of the new actions and surfaces.

Live ORM, rolled back. Attacks run as NON-ADMIN users with the role they
would really hold, and without it where the role is the control.
"""

from __future__ import annotations

import json
import types
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
FM = "cd_facility.group_facility_manager"
BOL = "cd_facility.group_branch_operations_lead"


def _user(env, login, company, ou, *groups):
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, ids)],
                "company_ids": [(6, 0, company.ids)],
                "company_id": company.id,
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.today = fields.Date.context_today(env["fix.site"])
    x.co = env["res.company"].create({"name": "A07P1 M47 Ops Co"})
    x.ou = env["operating.unit"].create(
        {
            "name": "A07P1 M47O OU",
            "code": "A7P1M47O",
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.clerk = _user(env, "a07p1_m47o_clerk", x.co, x.ou)
    x.clerk2 = _user(env, "a07p1_m47o_clerk2", x.co, x.ou)
    x.fm = _user(env, "a07p1_m47o_fm", x.co, x.ou, FM)
    x.bol = _user(env, "a07p1_m47o_bol", x.co, x.ou, BOL)
    # A07 ERP audit (2026-11-20) M47-18: a utility bill is recorded by a Facility Manager
    x.ufm = _user(env, "a07p1_m47o_ufm", x.co, x.ou, FM)
    x.cenv = env(user=x.clerk.id, context=dict(env.context, allowed_company_ids=x.co.ids))
    x.site = env["fix.site"].create(
        {"name": "A07P1O Branch", "company_id": x.co.id, "state": "active"}
    )
    return x


def _events(c, event_type, res_id):
    rows = c.env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", res_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


def _refused(fn, *args, match=None, **kw):
    with pytest.raises(REFUSED, match=match), fn.__self__.env.cr.savepoint():
        fn(*args, **kw)


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g

    ctl = g.P03GenericApiController()
    cls = g.P03GenericApiController
    mw = getattr(cls.model_write, "original_endpoint", cls.model_write)
    ma = getattr(cls.model_action, "original_endpoint", cls.model_action)
    old = getattr(g, "request", None)
    g.request = types.SimpleNamespace(env=c.cenv)
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: mw(ctl, **kw), action=lambda **kw: ma(ctl, **kw)
        )
    finally:
        g.request = old


# ------------------------------------------------------------------ utilities
def test_a_spike_is_held_and_only_a_reviewer_who_did_not_record_it_clears_it(c, p03):
    U = c.env["fix.site.utility"].with_user(c.ufm)
    U.create({"site_id": c.site.id, "period": "2026-08", "amount": 10000.0, "usage": 1000.0})
    U.create({"site_id": c.site.id, "period": "2026-09", "amount": 11000.0, "usage": 1100.0})
    normal = U.create(
        {"site_id": c.site.id, "period": "2026-10", "amount": 12000.0, "usage": 1200.0}
    )
    assert normal.review_state == "none" and not normal.flagged and normal.anomaly_evaluated
    spike = U.create(
        {"site_id": c.site.id, "period": "2026-11", "amount": 100000.0, "usage": 10000.0}
    )
    assert (spike.flagged, spike.review_state) == (True, "held")
    assert "average" in spike.anomaly_basis
    assert _events(c, "site.utility_anomaly", spike.id)[0]["amount"] == 100000.0
    # the recorder cannot clear it: not by write, not by P03, not by review
    _refused(spike.write, {"flagged": False}, match="cannot be set directly")
    _refused(spike.write, {"review_state": "released"}, match="cannot be set directly")
    res = p03.write(model="fix.site.utility", record_id=spike.id, values={"flagged": False})
    spike.invalidate_recordset()
    assert spike.flagged and spike.review_state == "held", res
    recorder_lead = c.env["res.users"].browse(spike.create_uid.id)
    recorder_lead.group_ids = [(4, c.env.ref(BOL).id)]
    _refused(spike.with_user(recorder_lead).action_release, notes="fine", match="Segregation")
    # nor a plain colleague, nor a reviewer without a basis
    _refused(spike.with_user(c.clerk2).action_release, notes="fine", match="Branch Operations")
    _refused(spike.with_user(c.bol).action_release, match="basis")
    # the figures under review are frozen
    _refused(spike.with_user(c.fm).write, {"amount": 12000.0}, match="reviewed on")
    spike.with_user(c.bol).action_confirm_anomaly(notes="Meter fault confirmed by DESCO")
    assert (spike.review_state, spike.flagged, spike.reviewed_by_id) == ("confirmed", True, c.bol)
    _refused(spike.with_user(c.bol).action_release, notes="x", match="not held")


def test_a_manual_hold_is_released_by_a_reviewer(c):
    u = (
        c.env["fix.site.utility"]
        .with_user(c.ufm)
        .create(
            {"site_id": c.site.id, "period": "2026-10", "utility_type": "water", "amount": 500.0}
        )
    )
    u.action_flag()
    assert u.review_state == "held"
    _refused(u.write, {"flagged": False}, match="cannot be set directly")
    u.with_user(c.bol).action_release(notes="Two-month bill, verified with WASA")
    assert (u.review_state, u.flagged) == ("released", False)


def test_the_anomaly_factor_is_a_business_parameter(c):
    c.env["ir.config_parameter"].sudo().set_param("cd_facility.utility_anomaly_factor", "1.2")
    U = c.env["fix.site.utility"].with_user(c.ufm)
    U.create({"site_id": c.site.id, "period": "2026-09", "amount": 1000.0})
    held = U.create({"site_id": c.site.id, "period": "2026-10", "amount": 1300.0})
    assert held.review_state == "held"


# --------------------------------------------------------------------- safety
def test_record_check_rolls_by_the_items_interval_and_records_the_inspector(c):
    item = (
        c.env["fix.site.safety"]
        .with_user(c.clerk)
        .create(
            {
                "site_id": c.site.id,
                "next_check": c.today - timedelta(days=45),
                "inspection_interval_months": 12,
            }
        )
    )
    assert item.state == "overdue"
    item.with_user(c.clerk2).action_check_pass()
    assert item.next_check == c.today + relativedelta(months=12) and item.state == "ok"
    assert (item.last_check, item.last_checked_by_id) == (c.today, c.clerk2)
    _refused(item.write, {"last_checked_by_id": c.clerk.id}, match="cannot be set directly")
    # with no interval the inspector still states the date (none invented)
    other = (
        c.env["fix.site.safety"]
        .with_user(c.clerk)
        .create({"site_id": c.site.id, "next_check": c.today - timedelta(days=1)})
    )
    _refused(other.action_check_pass, match="inspection interval")


# ------------------------------------------------------------------- incident
def test_an_injury_publishes_the_hse_hand_off_with_the_s80_clock(c):
    inc = (
        c.env["fix.site.incident"]
        .with_user(c.clerk)
        .create(
            {
                "site_id": c.site.id,
                "incident_type": "injury",
                "severity": "high",
                "description": "Technician burned by a soldering iron",
                "occurred_on": c.today,
            }
        )
    )
    assert inc.injuries_flag and inc.hse_notice_due_on == c.today + timedelta(days=2)
    ev = _events(c, "site.incident", inc.id)
    assert ev and ev[0]["injuries_flag"] is True
    assert ev[0]["hse_notice_due_on"] == str(c.today + timedelta(days=2))
    # the clock and the case link are not typed; the flag is not cleared by staff
    _refused(
        inc.with_user(c.clerk2).write, {"hse_notice_due_on": False}, match="cannot be set directly"
    )
    _refused(
        inc.with_user(c.clerk2).write, {"hse_case_ref": "FAKE"}, match="cannot be set directly"
    )
    _refused(
        inc.with_user(c.clerk2).write, {"injuries_flag": False}, match="Branch Operations Lead"
    )
    # a Facility Manager closes ordinary incidents, not injuries
    _refused(inc.with_user(c.fm).action_close, resolution="Fine", match="HSE")
    inc.with_user(c.bol).action_close(resolution="First aid given; iron stand replaced")
    assert inc.state == "closed"


def test_an_ordinary_incident_is_closed_by_a_facility_manager(c):
    inc = (
        c.env["fix.site.incident"]
        .with_user(c.clerk)
        .create({"site_id": c.site.id, "incident_type": "theft", "description": "Cable stolen"})
    )
    assert not inc.injuries_flag and not inc.hse_notice_due_on
    assert _events(c, "site.incident", inc.id)[0]["injuries_flag"] is False
    _refused(inc.with_user(c.clerk2).action_close, resolution="x", match="Facility Manager")
    inc.with_user(c.fm).action_close(resolution="Police GD 112; cage fitted")
    assert inc.closed_by_id == c.fm


def test_injury_close_can_require_the_hse_case(c):
    c.env["ir.config_parameter"].sudo().set_param(
        "cd_facility.injury_close_requires_hse_case", "True"
    )
    inc = (
        c.env["fix.site.incident"]
        .with_user(c.clerk)
        .create({"site_id": c.site.id, "incident_type": "injury", "description": "Fall"})
    )
    _refused(inc.with_user(c.bol).action_close, resolution="ok", match="HSE case")
    inc.sudo().write({"hse_case_ref": "HSE/2026/0007"})  # the M59 bridge links it
    inc.with_user(c.bol).action_close(resolution="HSE investigation complete")
    assert inc.state == "closed"


# ---------------------------------------------------------------- building PM
def test_a_recurring_pm_schedules_its_next_job(c):
    pm = (
        c.env["fix.site.pm"]
        .with_user(c.clerk)
        .create(
            {
                "site_id": c.site.id,
                "service_type": "generator",
                "interval_months": 3,
                "scheduled_on": c.today - timedelta(days=1),
                "cost": 4000.0,
            }
        )
    )
    pm.with_user(c.fm).action_done()
    nxt = pm.next_pm_id
    assert nxt and nxt.state == "open" and nxt.interval_months == 3
    assert nxt.scheduled_on == pm.scheduled_on + relativedelta(months=3)
    _refused(pm.write, {"next_pm_id": False}, match="cannot be set directly")
    one_off = c.env["fix.site.pm"].with_user(c.clerk).create({"site_id": c.site.id})
    one_off.with_user(c.fm).action_done()
    assert not one_off.next_pm_id


def test_business_default_intervals_apply_where_none_is_set(c):
    ICP = c.env["ir.config_parameter"].sudo()
    ICP.set_param("cd_facility.default_pm_interval_months", "3")
    ICP.set_param("cd_facility.default_inspection_interval_months", "3")
    # a PM with no interval of its own repeats by the business default
    pm = (
        c.env["fix.site.pm"]
        .with_user(c.clerk)
        .create({"site_id": c.site.id, "scheduled_on": c.today - timedelta(days=1)})
    )
    pm.with_user(c.fm).action_done()
    assert pm.next_pm_id.scheduled_on == pm.scheduled_on + relativedelta(months=3)
    assert not pm.next_pm_id.interval_months  # it keeps following the default
    # its own interval still wins
    own = (
        c.env["fix.site.pm"].with_user(c.clerk).create({"site_id": c.site.id, "interval_months": 6})
    )
    own.with_user(c.fm).action_done()
    assert own.next_pm_id.scheduled_on == own.scheduled_on + relativedelta(months=6)
    # a safety item with no interval rolls by the default
    item = (
        c.env["fix.site.safety"]
        .with_user(c.clerk)
        .create({"site_id": c.site.id, "next_check": c.today - timedelta(days=1)})
    )
    item.with_user(c.clerk2).action_check_pass()
    assert item.next_check == c.today + relativedelta(months=3)
    # a malformed default counts as none
    ICP.set_param("cd_facility.default_pm_interval_months", "three")
    once = c.env["fix.site.pm"].with_user(c.clerk).create({"site_id": c.site.id})
    once.with_user(c.fm).action_done()
    assert not once.next_pm_id


# ------------------------------------------------------------------- P03 wiring
def test_p03_offers_the_new_actions_and_surfaces(c):
    from odoo.addons.cd_p03_portal.controllers.a07 import SURFACES
    from odoo.addons.cd_p03_portal.controllers.a07.writable import WRITABLE

    assert {"action_open", "action_resume"} <= SURFACES["fix.site"]["actions"]
    assert "action_approve_permit" in SURFACES["fix.facility.work.order"]["actions"]
    assert {"action_decide_renew", "action_decide_renegotiate", "action_decide_exit"} <= (
        SURFACES["fix.site.lease"]["actions"]
    )
    assert {"action_release", "action_confirm_anomaly"} <= SURFACES["fix.site.utility"]["actions"]
    assert SURFACES["fix.site.risk.exception"]["actions"] == {
        "action_decide_continue",
        "action_decide_suspend",
    }
    assert SURFACES["fix.site.lease.schedule"]["actions"] == {"action_send_to_ap"}
    assert SURFACES["fix.site.lease.extract"]["actions"] == set()
    for model in ("fix.site.lease.schedule", "fix.site.lease.extract"):
        assert WRITABLE[model] == frozenset()
    assert WRITABLE["fix.site.risk.exception"] == frozenset({"decision_notes"})
    # the internal transitions are never buttons
    every = set().union(*(s["actions"] for s in SURFACES.values()))
    assert not {"_site_suspend", "action_approve_status_change", "_exception_raise"} & every


def test_p03_review_and_decision_buttons_run_with_the_callers_rights(c, p03):
    u = (
        c.env["fix.site.utility"]
        .with_user(c.ufm)
        .create({"site_id": c.site.id, "period": "2026-10", "amount": 900.0})
    )
    u.action_flag()
    # the clerk recorded it: the workspace button is refused too
    res = p03.action(
        model="fix.site.utility", ids=[u.id], method="action_release", kwargs={"notes": "ok"}
    )
    assert res.get("success") is False, res
    u.invalidate_recordset()
    assert u.review_state == "held"
