"""A07 P0 (E5, M47): the M47 figures tell the truth (live ORM, rolled back).

Every attack runs as a NON-ADMIN user created in the transaction
(base.group_user + an operating unit). The figures are read in a company of
their own, so the counts are exact and the company fence is exercised too.
"""

from __future__ import annotations

import importlib
import types
from datetime import timedelta

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
m47 = importlib.import_module("odoo.addons.cd_p03_portal.controllers.a07.m47")


FM = "cd_facility.group_facility_manager"


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
    x.co = env["res.company"].create({"name": "A07P0 M47 Co"})
    x.ou = env["operating.unit"].create(
        {
            "name": "A07P0 M47 OU",
            "code": "A7P0M47",
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    # A07 P1: licences are maintained by the Facility Manager role
    x.clerk = _user(env, "a07p0_m47_clerk", x.co, x.ou, FM)
    x.clerk2 = _user(env, "a07p0_m47_clerk2", x.co, x.ou, FM)
    # the clerks' env, restricted to their company like a browser session
    x.cenv = env(user=x.clerk.id, context=dict(env.context, allowed_company_ids=x.co.ids))
    x.landlord = env["res.partner"].create({"name": "A07P0 M47 Landlord"})
    return x


def _site(c, name, **kw):
    # operational unless stated (A07 P1: new sites are born Planned)
    vals = {"name": name, "company_id": c.co.id, "floor_area_sqm": 100.0, "state": "active"}
    vals.update(kw)
    return c.env["fix.site"].create(vals)


def _licence(c, site, user=None, **kw):
    vals = {
        "site_id": site.id,
        "licence_type": "trade",
        "number": "TL-A07P0",
        "evidence_file": "JVBERi0xLjQgc2Nhbg==",
    }
    vals.update(kw)
    model = c.env["fix.site.licence"]
    return (model.with_user(user) if user else model).create(vals)


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


# ------------------------------------------------------------------ licences
def test_licence_validity_follows_the_calendar(c, monkeypatch):
    site = _site(c, "A07P0 Validity Site")
    lic = _licence(c, site, c.clerk, valid_to=c.today)
    assert lic.is_valid is True
    later = c.today + timedelta(days=3)
    monkeypatch.setattr(fields.Date, "context_today", staticmethod(lambda *a, **k: later))
    lic.invalidate_recordset()
    assert lic.is_valid is False
    assert not c.env["fix.site.licence"].search([("id", "=", lic.id), ("is_valid", "=", True)])
    assert c.env["fix.site.licence"].search([("id", "=", lic.id), ("is_valid", "=", False)])


def test_licence_without_end_date_is_not_valid(c):
    site = _site(c, "A07P0 Undated Site")
    lic = _licence(c, site, c.clerk, licence_type="fire")
    assert lic.state == "valid"
    assert lic.is_valid is False
    assert lic in c.env["fix.site.licence"].search([("is_valid", "!=", True)])
    # recording the end date is the way to make it count
    lic.with_user(c.clerk2).write({"valid_to": c.today + timedelta(days=200)})
    assert lic.is_valid is True


def test_plain_user_cannot_revive_a_lapsed_licence(c, p03):
    site = _site(c, "A07P0 Revive Site")
    expired = _licence(c, site, c.clerk, state="expired", valid_to=c.today - timedelta(days=5))
    with pytest.raises(UserError, match="does not change"), c.env.cr.savepoint():
        expired.with_user(c.clerk2).write(
            {"state": "valid", "valid_to": c.today + timedelta(days=365)}
        )
    with pytest.raises(UserError, match="lapsed"), c.env.cr.savepoint():
        expired.with_user(c.clerk2).write({"state": "valid"})
    # still valid-state, but its date has passed: extending it is a revival too
    stale = _licence(c, site, licence_type="fire", valid_to=c.today - timedelta(days=3))
    with pytest.raises(UserError, match="does not change"), c.env.cr.savepoint():
        stale.with_user(c.clerk2).write({"valid_to": c.today + timedelta(days=365)})
    # via the P03 form
    res = p03.write(
        model="fix.site.licence",
        record_id=expired.id,
        values={"state": "valid", "valid_to": str(c.today + timedelta(days=365))},
    )
    expired.invalidate_recordset()
    assert expired.state == "expired" and expired.is_valid is False, res
    # the proper paths stay open: record the lapse, and the renewal as a new row
    stale.with_user(c.clerk2).write({"state": "expired"})
    assert stale.state == "expired"
    renewal = _licence(
        c,
        site,
        c.clerk2,
        licence_type="fire",
        number="FSCD-RENEW",
        valid_to=c.today + timedelta(days=365),
    )
    assert renewal.is_valid is True
    # a form save that posts the unchanged values is not a revival
    stale.with_user(c.clerk2).write({"state": "expired", "valid_to": stale.valid_to})
    # superuser code (seeds, data fixes) stays trusted
    expired.with_env(c.env).write({"state": "valid", "valid_to": c.today + timedelta(days=30)})
    assert expired.is_valid is True


def test_licence_gaps_kpi_and_reports(c):
    long = c.today + timedelta(days=365)
    past = c.today - timedelta(days=10)
    # 1: expired trade licence -> gap
    s1 = _site(c, "A07P0 Gap Expired Trade")
    _licence(c, s1, state="expired", valid_to=past)
    # 2: no licence at all -> gap (trade is required everywhere)
    s2 = _site(c, "A07P0 Gap No Licence")
    # 3: trade current, fire lapsed (state still valid) -> gap (fire held, none current)
    s3 = _site(c, "A07P0 Gap Fire Lapsed")
    _licence(c, s3, valid_to=long)
    _licence(c, s3, licence_type="fire", valid_to=past)
    # 4: expired trade superseded by a current renewal -> no gap
    s4 = _site(c, "A07P0 Renewed")
    _licence(c, s4, state="expired", valid_to=past)
    _licence(c, s4, valid_to=long)
    # 5: closed site with an expired licence -> no gap
    s5 = _site(c, "A07P0 Closed", state="closed")
    _licence(c, s5, state="expired", valid_to=past)
    # 6: undated trade licence -> gap (AC-21)
    s6 = _site(c, "A07P0 Gap Undated")
    _licence(c, s6)

    k = m47.kpis(c.cenv)
    assert k["licences_expired"] == 4, k

    pack = m47.licence_compliance(c.cenv)
    missing = [r for r in pack["rows"] if r["state"] == "Missing"]
    assert [r["site"] for r in missing] == [s2.name]
    by_site = {r["site"]: r for r in pack["rows"] if r["site"] == s6.name}
    assert by_site[s6.name]["valid"] is False
    assert "No expiry date" in by_site[s6.name]["basis"]

    gap_rows = [
        r for r in m47.critical_dates(c.cenv)["rows"] if r["kind"].startswith("Licence gap")
    ]
    assert sorted(r["site"] for r in gap_rows) == sorted([s1.name, s2.name, s3.name, s6.name])
    assert s4.name not in {r["site"] for r in gap_rows}
    assert s5.name not in {r["site"] for r in gap_rows}


# ------------------------------------------------------------------ safety
def test_safety_status_is_derived_from_next_check(c, p03):
    site = _site(c, "A07P0 Safety Site")
    Safety = c.env["fix.site.safety"].with_user(c.clerk)
    late = Safety.create(
        {
            "site_id": site.id,
            "equipment_type": "extinguisher",
            "next_check": c.today - timedelta(days=45),
            "state": "ok",
        }
    )
    soon = Safety.create(
        {"site_id": site.id, "equipment_type": "alarm", "next_check": c.today + timedelta(days=7)}
    )
    fine = Safety.create(
        {"site_id": site.id, "equipment_type": "cctv", "next_check": c.today + timedelta(days=90)}
    )
    assert (late.state, soon.state, fine.state) == ("overdue", "due", "ok")
    k = m47.kpis(c.cenv)
    assert k["safety_overdue"] == 1 and k["safety_due"] == 2, k
    overdue = c.env["fix.site.safety"].search(
        [("site_id", "=", site.id), ("state", "=", "overdue")]
    )
    assert overdue == late
    assert c.env["fix.site.safety"].search(
        [("site_id", "=", site.id), ("state", "!=", "overdue")]
    ) == (soon | fine)

    # forging: the status, the inspection record, a later next check
    with pytest.raises(UserError, match="derived"), c.env.cr.savepoint():
        late.with_user(c.clerk2).write({"state": "ok"})
    with pytest.raises(UserError, match="Record Check"), c.env.cr.savepoint():
        late.with_user(c.clerk2).write({"last_check": c.today})
    with pytest.raises(UserError, match="later"), c.env.cr.savepoint():
        late.with_user(c.clerk2).write({"next_check": c.today + timedelta(days=200)})
    res = p03.write(model="fix.site.safety", record_id=late.id, values={"state": "ok"})
    late.invalidate_recordset()
    assert late.state == "overdue", res
    # bringing a check forward, or saving the unchanged status, stays open
    fine.with_user(c.clerk2).write({"next_check": c.today + timedelta(days=60), "state": "ok"})
    assert fine.next_check == c.today + timedelta(days=60)


def test_record_check_requires_and_rolls_the_next_date(c, p03):
    site = _site(c, "A07P0 Check Site")
    item = (
        c.env["fix.site.safety"]
        .with_user(c.clerk)
        .create(
            {
                "site_id": site.id,
                "equipment_type": "extinguisher",
                "next_check": c.today - timedelta(days=45),
            }
        )
    )
    with pytest.raises(UserError, match="next check date"), c.env.cr.savepoint():
        item.with_user(c.clerk).action_check_pass()
    with pytest.raises(UserError, match="after today"), c.env.cr.savepoint():
        item.with_user(c.clerk).action_check_pass(next_check=str(c.today))
    with pytest.raises(UserError, match="not a date"), c.env.cr.savepoint():
        item.with_user(c.clerk).action_check_pass(next_check="next year")
    assert item.state == "overdue"
    # the P03 "Record Check" button sends the date as a kwarg
    nxt = c.today + timedelta(days=180)
    res = p03.action(
        model="fix.site.safety",
        ids=[item.id],
        method="action_check_pass",
        kwargs={"next_check": str(nxt)},
    )
    assert res.get("success"), res
    item.invalidate_recordset()
    assert item.next_check == nxt
    assert item.last_check == c.today
    assert item.state == "ok"
    assert m47.kpis(c.cenv)["safety_overdue"] == 0


# ------------------------------------------------------------------ leases
def test_lease_recorded_past_end_is_expired(c):
    """A07 P0 kept a lease past its end date in the expiry figures; A07 P1
    expires it: recorded after its end date it is born Expired, and the
    daily job expires an active one once the date passes."""
    site = _site(c, "A07P0 Lease Site")
    lease = (
        c.env["fix.site.lease"]
        .with_user(c.clerk)
        .create(
            {
                "site_id": site.id,
                "lessor_id": c.landlord.id,
                "start_date": c.today - timedelta(days=400),
                "end_date": c.today - timedelta(days=3),
                "monthly_rent": 100000.0,
            }
        )
    )
    assert lease.state == "expired"
    k = m47.kpis(c.cenv)
    assert k["leases_expiring_90d"] == 0 and k["leases_past_end"] == 0, k
    row = next(r for r in m47.lease_expiry(c.cenv)["rows"] if r["lease"] == lease.name)
    assert row["days_left"] == -3 and row["state"] == "Expired"


# ------------------------------------------------------------------ utilities
def _month(today, back):
    y, m = today.year, today.month - back
    while m <= 0:
        y, m = y - 1, m + 12
    return "%04d-%02d" % (y, m)


def test_utility_duplicate_and_free_text_period_refused(c):
    site = _site(c, "A07P0 Utility Site")
    U = c.env["fix.site.utility"].with_user(c.clerk)
    period = _month(c.today, 1)
    U.create({"site_id": site.id, "period": period, "utility_type": "gas", "amount": 7000})
    with pytest.raises(ValidationError, match="already has"), c.env.cr.savepoint():
        U.create({"site_id": site.id, "period": period, "utility_type": "gas", "amount": 7000})
        c.env.flush_all()
    with pytest.raises(ValidationError, match="YYYY-MM"), c.env.cr.savepoint():
        U.create({"site_id": site.id, "period": "last month", "utility_type": "gas", "amount": 1})
        c.env.flush_all()
    # another utility, or another month, is a different bill
    U.create({"site_id": site.id, "period": period, "utility_type": "water", "amount": 500})
    U.create({"site_id": site.id, "period": _month(c.today, 2), "utility_type": "gas", "amount": 1})


def test_utilities_cost_per_sqft_is_a_monthly_figure(c):
    # 100 sqm = 1,076.39 sqft; 10,763.90 a month = 10.00 per sqft per month
    site = _site(c, "A07P0 Sqft Site")
    U = c.env["fix.site.utility"].with_user(c.clerk)
    U.create(
        {
            "site_id": site.id,
            "period": _month(c.today, 2),
            "utility_type": "power",
            "amount": 10763.9,
        }
    )
    k1 = m47.kpis(c.cenv)
    U.create(
        {
            "site_id": site.id,
            "period": _month(c.today, 1),
            "utility_type": "power",
            "amount": 10763.9,
        }
    )
    k2 = m47.kpis(c.cenv)
    assert k1["utilities_cost_per_sqft"] == k2["utilities_cost_per_sqft"] == 10.0
    assert k2["utilities_cost_period"] == _month(c.today, 1)
    # the current month is still being billed and is not the reported period
    U.create(
        {"site_id": site.id, "period": _month(c.today, 0), "utility_type": "power", "amount": 99.0}
    )
    k3 = m47.kpis(c.cenv)
    assert k3["utilities_cost_period"] == _month(c.today, 1)
    assert k3["utilities_cost_per_sqft"] == 10.0


# ------------------------------------------------------------------ company fence
def test_kpis_and_reports_are_fenced_to_the_callers_companies(c):
    mine = _site(c, "A07P0 Fence Mine")
    other_co = c.env.ref("base.main_company")
    theirs = c.env["fix.site"].create({"name": "A07P0 Fence Theirs", "company_id": other_co.id})
    c.env["fix.site.licence"].create(
        {"site_id": theirs.id, "licence_type": "trade", "valid_to": c.today + timedelta(days=9)}
    )
    c.env["fix.site.safety"].create(
        {"site_id": theirs.id, "next_check": c.today - timedelta(days=9)}
    )
    for fn in m47.REPORTS.values():
        sites = {r.get("site") for r in fn(c.cenv)["rows"]}
        assert theirs.name not in sites, fn.__name__
    assert mine.name in {r["site"] for r in m47.branch_assets(c.cenv)["rows"]}
    k = m47.kpis(c.cenv)
    assert k["sites_active"] == 1 and k["safety_overdue"] == 0, k
