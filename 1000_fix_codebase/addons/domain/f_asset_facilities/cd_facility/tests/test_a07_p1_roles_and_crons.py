"""A07 P1 (M47): roles, ACLs, record rules and scheduled jobs.

Live ORM, rolled back. Attacks run as NON-ADMIN users created in the
transaction, with the M47 role they would really hold, and without it where
the role is the control. Each cron is asserted as an ir.cron RECORD that is
active and calls its method (a method with no record never runs: the A03
lesson), and each job is run twice to show it is idempotent.
"""

from __future__ import annotations

import json
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
FM = "cd_facility.group_facility_manager"
BOL = "cd_facility.group_branch_operations_lead"
OPSDIR = "cd_facility.group_operations_director"

CRONS = {
    "cd_facility.ir_cron_site_licence_expiry": ("fix.site.licence", "cron_licence_expiry"),
    "cd_facility.ir_cron_site_lease_critical_dates": (
        "fix.site.lease",
        "cron_lease_critical_dates",
    ),
    "cd_facility.ir_cron_site_safety_due": ("fix.site.safety", "cron_safety_due"),
    "cd_facility.ir_cron_site_pm_due": ("fix.site.pm", "cron_pm_due"),
    "cd_facility.ir_cron_site_utility_anomaly": ("fix.site.utility", "cron_utility_anomaly"),
}


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
    x.co = env["res.company"].create({"name": "A07P1 M47 Roles Co"})
    x.ou = env["operating.unit"].create(
        {
            "name": "A07P1 M47 OU1",
            "code": "A7P1M47A",
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.ou2 = env["operating.unit"].create(
        {
            "name": "A07P1 M47 OU2",
            "code": "A7P1M47B",
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.clerk = _user(env, "a07p1_m47r_clerk", x.co, x.ou)
    x.fm = _user(env, "a07p1_m47r_fm", x.co, x.ou, FM)
    x.bol = _user(env, "a07p1_m47r_bol", x.co, x.ou, BOL)
    x.site = env["fix.site"].create(
        {
            "name": "A07P1R Site",
            "company_id": x.co.id,
            "operating_unit_id": x.ou.id,
            "state": "active",
        }
    )
    x.site2 = env["fix.site"].create(
        {
            "name": "A07P1R Other-OU Site",
            "company_id": x.co.id,
            "operating_unit_id": x.ou2.id,
            "state": "active",
        }
    )
    x.landlord = env["res.partner"].create({"name": "A07P1R Landlord"})
    return x


def _lease(c, site=None, user=None, **kw):
    vals = {
        "site_id": (site or c.site).id,
        "lessor_id": c.landlord.id,
        "start_date": c.today - timedelta(days=30),
        "end_date": c.today + timedelta(days=700),
        "monthly_rent": 50000.0,
        "deposit": 300000.0,
    }
    vals.update(kw)
    model = c.env["fix.site.lease"]
    return (model.with_user(user) if user else model).create(vals)


def _count(c, event_type, res_id=None):
    dom = [("event_type", "=", event_type)]
    if res_id:
        dom.append(("aggregate_id", "=", res_id))
    return c.env["fix.event.outbox"].search_count(dom)


# ----------------------------------------------------------------- roles
def test_roles_exist_imply_upward_and_admin_keeps_access(c):
    fm, bol, od = (c.env.ref(x) for x in (FM, BOL, OPSDIR))
    assert fm.privilege_id == bol.privilege_id == od.privilege_id
    assert bol in od.implied_ids and fm in bol.implied_ids
    assert c.env.ref("base.group_user") in fm.implied_ids
    assert c.env.ref("base.user_admin") in fm.all_user_ids
    # the decision roles ship empty of real people (decision B1)
    assert not (bol.user_ids - c.env["res.users"].search([("login", "like", "a07p1_")]))


def test_plain_user_reads_and_raises_but_does_not_maintain_master_data(c):
    lease = _lease(c)
    licence = c.env["fix.site.licence"].create(
        {"site_id": c.site.id, "licence_type": "trade", "valid_to": c.today + timedelta(days=90)}
    )
    for rec, vals in (
        (c.site, {"floor_area_sqm": 1.0}),
        (lease, {"notes": "edited"}),
        (licence, {"number": "FORGED"}),
    ):
        with pytest.raises(AccessError), c.env.cr.savepoint():
            rec.with_user(c.clerk).write(vals)
        # the Facility Manager maintains it
        rec.with_user(c.fm).write(vals)
    with pytest.raises(AccessError), c.env.cr.savepoint():
        c.env["fix.site.condition"].with_user(c.clerk).create({"site_id": c.site.id})
    c.env["fix.site.condition"].with_user(c.fm).create({"site_id": c.site.id})
    # anyone raises a facility request (spec §13 R08/R09: C R)
    wo = (
        c.env["fix.facility.work.order"]
        .with_user(c.clerk)
        .create({"site_id": c.site.id, "company_id": c.co.id, "description": "Leaking roof"})
    )
    assert wo.state == "draft"


def test_unlink_is_for_the_branch_operations_lead(c):
    pm = c.env["fix.site.pm"].create({"site_id": c.site.id})
    for user in (c.clerk, c.fm):
        with pytest.raises(AccessError), c.env.cr.savepoint():
            pm.with_user(user).unlink()
    pm.with_user(c.bol).unlink()
    assert not pm.exists()


def test_satellite_records_follow_their_sites_operating_unit(c):
    """M47-14 / probe 47: an OU-1 user does not read the lease of an OU-2 site."""
    other = _lease(c, site=c.site2)
    mine = _lease(c)
    Lease = c.env["fix.site.lease"].with_user(c.fm)
    assert Lease.search_count([("id", "=", other.id)]) == 0
    assert Lease.search_count([("id", "=", mine.id)]) == 1
    with pytest.raises(AccessError), c.env.cr.savepoint():
        other.with_user(c.fm).read(["monthly_rent", "deposit"])
    for model in (
        "fix.site.licence",
        "fix.site.utility",
        "fix.site.pm",
        "fix.site.safety",
        "fix.site.incident",
        "fix.site.project",
        "fix.site.asset",
        "fix.site.lease.schedule",
        "fix.site.lease.extract",
        "fix.site.risk.exception",
    ):
        rules = c.env["ir.rule"].search([("model_id.model", "=", model)])
        assert len(rules) >= 2 and all("site_id" in r.domain_force for r in rules), model
    assert (
        c.env["fix.site.lease.schedule"].with_user(c.fm).search_count([("lease_id", "=", other.id)])
        == 0
    )


# ----------------------------------------------------------------- crons
@pytest.mark.parametrize("xmlid", sorted(CRONS))
def test_every_daily_job_is_a_live_cron_record(c, xmlid):
    model, method = CRONS[xmlid]
    cron = c.env.ref(xmlid)
    assert cron.active and cron.state == "code"
    assert cron.model_id.model == model
    assert cron.code.strip() == "model.%s()" % method
    assert (cron.interval_number, cron.interval_type) == (1, "days")
    assert callable(getattr(c.env[model], method))
    # the method runs as the cron does, twice (idempotent)
    assert getattr(c.env[model].sudo(), method)() is True
    assert getattr(c.env[model].sudo(), method)() is True


def test_licence_expiry_job_alerts_once_per_horizon_and_raises_the_exception(c, monkeypatch):
    soon = c.env["fix.site.licence"].create(
        {"site_id": c.site.id, "licence_type": "fire", "valid_to": c.today + timedelta(days=25)}
    )
    Lic = c.env["fix.site.licence"].sudo()
    Lic.cron_licence_expiry()
    Lic.cron_licence_expiry()
    assert _count(c, "site.compliance_expiring", soon.id) == 1
    assert soon.alert_horizon == 30
    # 20 days later the 7-day horizon fires once more
    later = c.today + timedelta(days=20)
    monkeypatch.setattr(fields.Date, "context_today", staticmethod(lambda *a, **k: later))
    Lic.cron_licence_expiry()
    Lic.cron_licence_expiry()
    assert _count(c, "site.compliance_expiring", soon.id) == 2
    # past expiry: marked expired, one expired event, one risk exception
    lapsed = c.today + timedelta(days=30)
    monkeypatch.setattr(fields.Date, "context_today", staticmethod(lambda *a, **k: lapsed))
    Lic.cron_licence_expiry()
    Lic.cron_licence_expiry()
    soon.invalidate_recordset()
    assert soon.state == "expired"
    assert _count(c, "site.compliance_expired", soon.id) == 1
    exc = c.env["fix.site.risk.exception"].search([("licence_id", "=", soon.id)])
    assert len(exc) == 1 and exc.state == "open"
    assert _count(c, "site.risk_exception_raised", exc.id) == 1
    assert exc.last_escalated_on == lapsed


def test_safety_job_reports_unfit_once_per_lapse(c):
    item = c.env["fix.site.safety"].create(
        {"site_id": c.site.id, "next_check": c.today - timedelta(days=3)}
    )
    S = c.env["fix.site.safety"].sudo()
    S.cron_safety_due()
    S.cron_safety_due()
    rows = c.env["fix.event.outbox"].search(
        [("event_type", "=", "site.safety_equipment_unfit"), ("aggregate_id", "=", item.id)]
    )
    assert len(rows) == 1
    assert json.loads(rows.payload)["due_date"] == str(item.next_check)


def test_pm_job_raises_one_work_order_for_a_due_pm(c):
    vendor = c.env["res.partner"].create({"name": "A07P1R Lift Co"})
    pm = c.env["fix.site.pm"].create(
        {"site_id": c.site.id, "service_type": "lift", "provider_id": vendor.id}
    )
    future = c.env["fix.site.pm"].create(
        {"site_id": c.site.id, "scheduled_on": c.today + timedelta(days=10)}
    )
    P = c.env["fix.site.pm"].sudo()
    P.cron_pm_due()
    P.cron_pm_due()
    wo = pm.work_order_id
    assert wo and wo.pm_id == pm and wo.state == "draft"
    assert (wo.assigned_type, wo.vendor_id) == ("vendor", vendor)
    assert c.env["fix.facility.work.order"].search_count([("pm_id", "=", pm.id)]) == 1
    assert not future.work_order_id
    # the link is the job's, not the user's
    with pytest.raises(UserError, match="cannot be set directly"), c.env.cr.savepoint():
        pm.with_user(c.fm).write({"work_order_id": False})


def test_utility_job_evaluates_unevaluated_bills_once(c):
    U = c.env["fix.site.utility"].sudo()
    base = U.create({"site_id": c.site.id, "period": "2026-01", "amount": 1000.0})
    spike = U.create({"site_id": c.site.id, "period": "2026-02", "amount": 5000.0})
    assert spike.review_state == "held"
    # a row imported with no evaluation is picked up by the job
    spike._guarded().write({"anomaly_evaluated": False, "review_state": "none", "flagged": False})
    U.cron_utility_anomaly()
    U.cron_utility_anomaly()
    assert spike.review_state == "held" and spike.anomaly_evaluated and base.anomaly_evaluated
    assert _count(c, "site.utility_anomaly", spike.id) == 2  # on record, then once by the job
