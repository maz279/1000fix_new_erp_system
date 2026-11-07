"""A07 P1/P2 (M47): lease rent schedule, IFRS 16 extract, critical dates and
the renewal decision; facility work order vendor, permit to work, branch
verification and the M52 cost hand-off.

Live ORM, rolled back. Attacks run as NON-ADMIN users with the role they
would really hold (Facility Manager, CFO = DOFA Tier 4), and without it.
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
TIER = "cd_entity_config.group_dofa_tier_%d"
WO = "fix.facility.work.order"


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
    x.co = env["res.company"].create({"name": "A07P1 M47 Lease Co"})
    x.ou = env["operating.unit"].create(
        {
            "name": "A07P1 M47L OU",
            "code": "A7P1M47L",
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.clerk = _user(env, "a07p1_m47l_clerk", x.co, x.ou)
    x.clerk2 = _user(env, "a07p1_m47l_clerk2", x.co, x.ou)
    x.fm = _user(env, "a07p1_m47l_fm", x.co, x.ou, FM)
    x.fm2 = _user(env, "a07p1_m47l_fm2", x.co, x.ou, FM)
    x.cfo = _user(env, "a07p1_m47l_cfo", x.co, x.ou, TIER % 4)
    x.site = env["fix.site"].create(
        {"name": "A07P1L Branch", "company_id": x.co.id, "state": "active"}
    )
    x.landlord = env["res.partner"].create({"name": "A07P1L Landlord"})
    x.vendor = env["res.partner"].create({"name": "A07P1L Generator Vendor"})
    return x


def _events(c, event_type, res_id):
    rows = c.env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", res_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


def _refused(fn, *args, match=None, **kw):
    with pytest.raises(REFUSED, match=match), fn.__self__.env.cr.savepoint():
        fn(*args, **kw)


def _lease(c, user=None, **kw):
    vals = {
        "site_id": c.site.id,
        "lessor_id": c.landlord.id,
        "start_date": c.today - timedelta(days=3 * 365),
        "end_date": c.today + timedelta(days=400),
        "monthly_rent": 100000.0,
        "escalation_pct": 10.0,
        "deposit": 600000.0,
    }
    vals.update(kw)
    return c.env["fix.site.lease"].with_user(user or c.fm).create(vals)


# ------------------------------------------------------------- rent schedule
def test_recording_a_lease_builds_the_escalated_schedule_and_the_extract(c):
    ls = _lease(c)
    # this month's row: escalated by the lease years completed on its due date
    due = ls.schedule_ids.filtered(lambda r: r.period == c.today.strftime("%Y-%m")).due_date
    years = relativedelta(due, ls.start_date).years
    assert ls.current_rent == round(100000.0 * 1.1**years, 2) != 100000.0
    first = ls.schedule_ids.sorted("due_date")[0]
    assert (first.period, first.rent_due) == (ls.start_date.strftime("%Y-%m"), 100000.0)
    months = relativedelta(ls.end_date, ls.start_date)
    assert len(ls.schedule_ids) == months.years * 12 + months.months + 1
    # lease.recorded and extract v1 for M19 / M49
    rec = _events(c, "lease.recorded", ls.id)
    assert rec and rec[0]["monthly_rent"] == 100000.0 and rec[0]["deposit"] == 600000.0
    assert ls.extract_ids.version == 1 and ls.extract_ids.reason == "recorded"
    ex = _events(c, "lease.extract_published", ls.id)
    assert ex[0]["extract"]["commencement"] == str(ls.start_date)
    assert "liability" not in json.dumps(ex[0]) and "rou" not in ex[0]["extract"]
    # the register and the cost pack report the scheduled rent, not the stale figure
    import odoo.addons.cd_p03_portal.controllers.a07.m47 as m47

    env = c.env(user=c.fm.id, context=dict(c.env.context, allowed_company_ids=c.co.ids))
    row = next(r for r in m47.lease_expiry(env)["rows"] if r["lease"] == ls.name)
    assert row["rent"] == ls.current_rent
    cost = next(r for r in m47.cost_per_site(env)["rows"] if r["site"] == c.site.name)
    assert cost["rent"] == ls.current_rent


def test_schedule_and_extract_rows_are_insert_only(c):
    ls = _lease(c)
    row = ls.schedule_ids[:1]
    ext = ls.extract_ids[:1]
    for user in (c.clerk, c.fm):
        _refused(row.with_user(user).write, {"rent_due": 1.0})
        _refused(row.with_user(user).unlink)
        _refused(ext.with_user(user).write, {"payload": "{}"})
        _refused(
            c.env["fix.site.lease.schedule"].with_user(user).create,
            {"lease_id": ls.id, "period": "2099-01", "due_date": "2099-01-01"},
        )
    # the M52 payment match (a superuser service) may record the payment
    row.sudo().write({"paid_amount": row.rent_due, "paid_on": c.today, "invoice_ref": "INV-1"})
    assert row.variance == 0.0


def test_modification_rebuilds_the_future_schedule_and_publishes_extract_v2(c):
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    ls = _lease(c, end_date=c.today + timedelta(days=200))
    paid = ls.schedule_ids.sorted("due_date")[0]
    paid.sudo().write({"paid_amount": paid.rent_due, "paid_on": c.today})
    ls.action_open_modification()
    ls.write(
        {
            "proposed_monthly_rent": 90000.0,
            "proposed_end_date": c.today + timedelta(days=900),
            "modification_reason": "Renewal",
        }
    )
    approve_via_inbox(ls, c.cfo, requester=c.fm, justification="Renewal")
    ls.action_apply_modification()
    assert paid.exists() and paid.rent_due == 100000.0  # the paid row is the record
    assert ls.schedule_ids.sorted("due_date")[-1].due_date <= ls.end_date
    this_month = c.today.strftime("%Y-%m")
    now_row = ls.schedule_ids.filtered(lambda r: r.period == this_month)
    years = relativedelta(now_row.due_date, ls.start_date).years
    assert now_row.rent_due == round(90000.0 * 1.1**years, 2)
    assert sorted(ls.extract_ids.mapped("version")) == [1, 2]
    assert _events(c, "lease.extract_published", ls.id)[-1]["reason"] == "modified"


# -------------------------------------------------------------- critical dates
def test_lease_recorded_after_its_end_is_expired_and_the_job_expires_active_ones(c, monkeypatch):
    old = _lease(c, start_date=c.today - timedelta(days=400), end_date=c.today - timedelta(days=3))
    assert old.state == "expired"
    live = _lease(c, end_date=c.today + timedelta(days=5))
    later = c.today + timedelta(days=6)
    monkeypatch.setattr(fields.Date, "context_today", staticmethod(lambda *a, **k: later))
    c.env["fix.site.lease"].sudo().cron_lease_critical_dates()
    assert live.state == "expired"
    assert _events(c, "lease.critical_date_due", live.id)[-1]["event_type"] == "expiry"


def test_renewal_decision_is_the_cfos_and_is_requested_daily_near_the_deadline(c, monkeypatch):
    ls = _lease(c, end_date=c.today + timedelta(days=100), notice_period_days=90)
    assert ls.renewal_notice_date == c.today + timedelta(days=10)
    L = c.env["fix.site.lease"].sudo()
    L.cron_lease_critical_dates()
    L.cron_lease_critical_dates()
    assert len(_events(c, "lease.renewal_decision_required", ls.id)) == 1
    tomorrow = c.today + timedelta(days=1)
    monkeypatch.setattr(fields.Date, "context_today", staticmethod(lambda *a, **k: tomorrow))
    L.cron_lease_critical_dates()
    assert len(_events(c, "lease.renewal_decision_required", ls.id)) == 2
    # the decision fields are not typed
    _refused(ls.with_user(c.fm).write, {"renewal_decision": "renew"}, match="cannot be set")
    # not the Facility Manager, not without a basis, not the lease's recorder
    _refused(ls.with_user(c.fm).action_decide_renew, notes="keep", match="CFO")
    _refused(ls.with_user(c.cfo).action_decide_renew, match="basis")
    own = _lease(c, user=c.fm)
    own_cfo = c.env["res.users"].browse(own.create_uid.id)
    own_cfo.group_ids = [(4, c.env.ref(TIER % 4).id)]
    _refused(own.with_user(own_cfo).action_decide_exit, notes="x", match="Segregation")
    ls.with_user(c.cfo).action_decide_renew(notes="Branch profitable; renew at market rent")
    assert (ls.renewal_decision, ls.renewal_decision_by_id) == ("renew", c.cfo)
    L.cron_lease_critical_dates()
    assert len(_events(c, "lease.renewal_decision_required", ls.id)) == 2


# ---------------------------------------------------------------- work order
def _wo(c, user=None, **kw):
    vals = {
        "site_id": c.site.id,
        "company_id": c.co.id,
        "work_type": "repair",
        "description": "A07P1L generator overhaul",
    }
    vals.update(kw)
    order = c.env[WO].with_user(user or c.clerk).create(vals)
    # a person's request is triaged first (tested in test_a07_m47_operability.py)
    order.sudo().action_triage("normal")
    return order


def test_raising_publishes_and_a_vendor_job_names_its_vendor(c):
    w = _wo(c, assigned_type="vendor")
    assert _events(c, "facility.work_order_raised", w.id)[0]["source"] == "request"
    _refused(w.action_schedule, match="vendor")
    w.write({"vendor_id": c.vendor.id})
    w.action_schedule()
    assert w.state == "scheduled"


def test_high_risk_job_starts_only_under_an_approved_permit(c):
    w = _wo(c, high_risk=True)
    w.action_schedule()
    _refused(w.action_start, match="permit to work")
    # the permit is not typed, and the raiser and plain users do not approve it
    _refused(
        w.with_user(c.clerk2).write,
        {"permit_approved_by_id": c.clerk2.id},
        match="cannot be set directly",
    )
    _refused(w.with_user(c.clerk2).action_approve_permit, match="hazard")
    w.write({"hazard_type": "electrical", "permit_precautions": "LOTO on DB-2; insulated gloves"})
    _refused(w.with_user(c.clerk2).action_approve_permit, match="Facility Manager")
    raiser = c.env["res.users"].browse(w.create_uid.id)
    raiser.group_ids = [(4, c.env.ref(FM).id)]
    _refused(w.with_user(raiser).action_approve_permit, match="Segregation")
    w.with_user(c.fm).action_approve_permit()
    assert (w.permit_approved_by_id, w.permit_valid_to) == (c.fm, c.today)
    # changing the precautions withdraws it
    w.write({"permit_precautions": "gloves only"})
    assert not w.permit_approved_by_id
    _refused(w.action_start, match="permit to work")
    w.with_user(c.fm).action_approve_permit(valid_to=str(c.today + timedelta(days=2)))
    # only a Facility Manager takes the permit requirement off
    _refused(w.with_user(c.clerk2).write, {"high_risk": False}, match="Facility Manager")
    w.action_start()
    assert w.state == "in_progress"


def test_verification_is_a_facility_managers_and_sends_the_cost_to_m52(c):
    w = _wo(c, assigned_type="vendor", vendor_id=c.vendor.id)
    w.action_schedule()
    w.action_start()
    w.action_complete(notes="Alternator rewound, job sheet JS-77")
    _refused(w.with_user(c.clerk2).action_verify, match="Facility Manager")
    w.with_user(c.fm).action_verify(notes="Checked on site")
    closed = _events(c, "facility.work_order_closed", w.id)
    assert closed and closed[0]["cost"] == 0.0 and closed[0]["vendor_id"] == c.vendor.id
    assert closed[0]["verified_by"] == c.fm.name


def test_a_costed_vendor_job_needs_its_invoice_reference(c):
    from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox

    w = _wo(c, assigned_type="vendor", vendor_id=c.vendor.id, estimated_cost=8000.0)
    t2 = _user(c.env, "a07p1_m47l_t2", c.co, c.ou, TIER % 2)
    approve_via_inbox(w, t2, requester=c.clerk, justification="Generator down")
    w.action_schedule()
    w.action_start()
    w.write({"actual_cost": 7500.0})
    w.action_complete(notes="Done, JS-78")
    _refused(w.with_user(c.fm).action_verify, match="invoice reference")
    w.write({"invoice_ref": "VINV-2026-118"})
    w.with_user(c.fm).action_verify()
    closed = _events(c, "facility.work_order_closed", w.id)[0]
    assert (closed["cost"], closed["invoice_ref"]) == (7500.0, "VINV-2026-118")
